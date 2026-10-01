"""Extract official NCS dashboard tables from a saved public page and bundle.

Offline only. Parses JSON-compatible literals; never executes downloaded JavaScript.
The snapshot is dated by the publisher and is not a live vacancy feed.
"""
import argparse
import csv
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
from .acquire import ROOT,write_json

def object_literal(text, marker):
    start=text.index(marker)+len(marker)
    if text[start]!='{':raise ValueError('Expected literal object')
    level=0; quoted=False; escaped=False
    for pos in range(start,len(text)):
        ch=text[pos]
        if quoted:
            if escaped:escaped=False
            elif ch=='\\':escaped=True
            elif ch=='"':quoted=False
        elif ch=='"':quoted=True
        elif ch=='{':level+=1
        elif ch=='}':
            level-=1
            if level==0:
                value=text[start:pos+1]
                value=re.sub(r'([,{])\s*(rows|state|values|total|grandTotal|label|Vacancies):',r'\1"\2":',value)
                return json.loads(value)
    raise ValueError('Unterminated literal')

def csv_write(path,rows,fields):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields)
        writer.writeheader();writer.writerows(rows)

def extract(html,bundle):
    soup=BeautifulSoup(html,'html.parser')
    label=soup.select_one('button.tab-btn.active')
    if label is None:raise ValueError('No active dashboard metric')
    active=label.get_text(' ',strip=True)
    columns=json.loads(re.search(r'this\.allColumns=(\[[^\]]+\])',bundle).group(1))
    data=object_literal(bundle,'this.allTabData=')
    table=soup.find('table')
    if table is None:raise ValueError('No dashboard table')
    headers=[x.get_text(' ',strip=True) for x in table.select('thead th')]
    if headers[1:-1]!=columns[:len(headers)-2]:raise ValueError('HTML and bundle year labels disagree')
    rows_by_state={r['state']:r for r in data[active]['rows']}
    for tr in table.select('tbody tr'):
        cells=[td.get_text(' ',strip=True) for td in tr.find_all('td')]
        if not cells:continue
        state=cells[0]
        if state==data[active]['grandTotal']['label']:
            source=data[active]['grandTotal']
            observed=[int(x.replace(',','')) for x in cells[1:]]
            if observed!=source['values'][:len(headers)-2]+[source['total']]:
                raise ValueError('HTML and bundle national totals disagree')
            continue
        if state not in rows_by_state:raise ValueError('HTML state not present in bundle: '+state)
        source=rows_by_state[state]
        observed=[int(x.replace(',','')) for x in cells[1:]]
        expected=source['values'][:len(headers)-2]+[source['total']]
        if observed!=expected:raise ValueError('HTML and bundle values disagree: '+state)
    date_match=re.search(r'Last Updated on\s+([^<]+)',html)
    publisher_date=date_match.group(1).strip() if date_match else 'unknown'
    records=[];totals=[];quality=[]
    for metric,table_data in data.items():
        if len(table_data['grandTotal']['values'])!=len(columns):raise ValueError('National year count mismatch')
        if sum(table_data['grandTotal']['values'])!=table_data['grandTotal']['total']:
            quality.append({'metric':metric,'issue':'national_year_values_do_not_sum_to_reported_total'})
        for row in table_data['rows']:
            if len(row['values'])!=len(columns):raise ValueError('Year count mismatch')
            totals.append({'metric':metric,'state':row['state'],'reported_total':row['total']})
            if sum(row['values'])!=row['total']:
                quality.append({'metric':metric,'state':row['state'],'issue':'year_values_do_not_sum_to_reported_total','sum_years':sum(row['values']),'reported_total':row['total']})
            for year,count in zip(columns,row['values']):
                records.append({'metric':metric,'state':row['state'],'financial_year':year,'value':count,
                    'publisher_updated_at':publisher_date,'source_url':'https://ncs.gov.in/NCSReportDashboard',
                    'access_method':'offline extraction of previously downloaded public dashboard bundle',
                    'quality_flag':'publisher_snapshot;2026_2027_partial;metric_definitions_require_confirmation'})
        for year,value in zip(columns,table_data['grandTotal']['values']):
            expected=sum(row['values'][columns.index(year)] for row in table_data['rows'])
            if expected!=value:quality.append({'metric':metric,'financial_year':year,'issue':'state_sum_differs_from_national_total','state_sum':expected,'national_total':value})
    return records,totals,quality

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--html',type=Path,required=True)
    parser.add_argument('--bundle',type=Path,required=True)
    args=parser.parse_args()
    records,totals,quality=extract(args.html.read_text(encoding='utf-8'),args.bundle.read_text(encoding='utf-8'))
    csv_write(ROOT/'data/processed/ncs/ncs_state_year_metrics.csv',records,list(records[0]))
    csv_write(ROOT/'data/processed/ncs/ncs_maharashtra_year_metrics.csv',[r for r in records if r['state']=='Maharashtra'],list(records[0]))
    csv_write(ROOT/'data/processed/ncs/ncs_reported_totals.csv',totals,list(totals[0]))
    write_json(ROOT/'data/manifests/ncs_quality_flags.json',quality)
    print('NCS records',len(records),'Maharashtra',sum(r['state']=='Maharashtra' for r in records),'quality flags',len(quality))

if __name__=='__main__':main()
