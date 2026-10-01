"""Extract official ITI grading and state apprenticeship tables; audit school aggregates."""
import csv,hashlib,json,re
from decimal import Decimal
from pathlib import Path
from bs4 import BeautifulSoup
from pypdf import PdfReader
from .acquire import ROOT,write_json,now,get
from .extract_ncs import csv_write

def grade_row(line,page):
    tokens=line.split()
    if len(tokens)<11 or not tokens[0].isdigit():return None
    code_original=' '.join(tokens[1:-9]);code=code_original.replace(' ','')
    if not re.fullmatch(r'[A-Z]{1,3}\d{7,8}',code):return None
    values=tokens[-9:]
    if any(not re.fullmatch(r'\d+(?:\.\d+)?|NG',v) for v in values):raise ValueError('Unexpected grade token')
    result={'serial_number':int(tokens[0]),'iti_code':code,'publisher_code_text':code_original,'academic_year':'2026-27','pdf_page':page}
    result.update({f'parameter_{i}':v for i,v in enumerate(values[:8],1)})
    result['final_grade']=values[8]
    result['state_code_from_iti_id']=re.match(r'^[A-Z]+(\d{2})',code).group(1)
    result['source_url']='https://www.dgt.gov.in/en/node/4464'
    return result

def dgt():
    reader=PdfReader(ROOT/'data/raw/training/dgt_iti_grading_2026_27.pdf');rows=[];rejected=[]
    for i,page in enumerate(reader.pages):
        for line in (page.extract_text() or '').splitlines():
            row=grade_row(line,i+1)
            if row:rows.append(row)
            elif re.match(r'^\d+\s+[A-Z]{1,3}\s*\d{7,8}\b',line):rejected.append({'page':i+1,'line':line})
    if rejected:raise ValueError('Unparsed ITI rows: '+str(rejected[:3]))
    serials=[r['serial_number'] for r in rows]
    if not rows or serials!=list(range(1,max(serials)+1)):raise ValueError('ITI row numbering not contiguous')
    if len({r['iti_code'] for r in rows})!=len(rows):raise ValueError('Repeated ITI code')
    numeric=[r for r in rows if 'NG' not in [r[f'parameter_{i}'] for i in range(1,9)]+[r['final_grade']]]
    mismatch=[r['iti_code'] for r in numeric if sum(Decimal(r[f'parameter_{i}']) for i in range(1,9))!=Decimal(r['final_grade'])]
    mh=[r for r in rows if r['state_code_from_iti_id']=='27']
    csv_write(ROOT/'data/processed/training/dgt_iti_grading_2026_27.csv',rows,list(rows[0]))
    csv_write(ROOT/'data/processed/training/dgt_maharashtra_iti_grading_2026_27.csv',mh,list(rows[0]))
    result={'national_rows':len(rows),'maharashtra_code_27_rows':len(mh),'NG_final_grade_rows':sum(r['final_grade']=='NG' for r in rows),'parameter_sum_mismatch_iti_codes':mismatch,'row_serials_contiguous':True,'duplicate_iti_codes':0,'scope':'AY 2026-27 publisher grading scores, not capacity or placements','geography_method':'Maharashtra subset uses state code 27 embedded in NCVT/MIS-style ITI IDs; names/districts absent in current grade file'}
    write_json(ROOT/'data/manifests/dgt_grading_quality.json',result);print('DGT',result,flush=True)

def apprenticeship(html_path):
    html=html_path.read_text(encoding='utf-8');soup=BeautifulSoup(html,'html.parser')
    table=next(t for t in soup.select('table') if t.get('class')==['MsoTableGrid'] and 'Apprentices Engaged under NAPS' in t.get_text())
    rows=[]
    for tr in table.select('tr')[1:]:
        cells=[c.get_text(' ',strip=True) for c in tr.find_all('td',recursive=False)]
        if len(cells)!=4:raise ValueError('Unexpected apprenticeship table width')
        rows.append({'state_ut':cells[1],'naps_engaged':int(cells[2].replace(',','')),'nats_engaged':int(cells[3].replace(',','')),'calendar_year':'2025','published_at':'2026-03-23','source_url':'https://www.pib.gov.in/PressReleasePage.aspx?PRID=2243987&lang=1'})
    if len({r['state_ut'] for r in rows})!=len(rows):raise ValueError('Repeated state apprenticeship row')
    totals=[r for r in rows if r['state_ut']=='Total']
    if len(totals)!=1:raise ValueError('Expected one national apprenticeship total')
    states=[r for r in rows if r['state_ut']!='Total']
    for key in ['naps_engaged','nats_engaged']:
        if sum(r[key] for r in states)!=totals[0][key]:raise ValueError('Apprenticeship state/national totals disagree')
    write_json(ROOT/'data/manifests/apprenticeship_quality.json',{'state_ut_rows':len(states),'national_total_rows':1,'national_totals':{k:totals[0][k] for k in ['naps_engaged','nats_engaged']},'state_sums_reconcile':True,'period':'Calendar 2025'})
    csv_write(ROOT/'data/processed/training/naps_nats_state_engagement_2025.csv',rows,list(rows[0]))
    print('Apprenticeship rows',len(rows),'Maharashtra',[r for r in rows if r['state_ut']=='Maharashtra'],flush=True)

def schools():
    result={}
    for part in [1,2]:
        path=ROOT/f'data/raw/supply/udise_pune_2025_26_enrolment_{part}.csv'
        with path.open(encoding='utf-8-sig',newline='') as f:
            reader=csv.DictReader(f);columns=reader.fieldnames;rows=list(reader)
        key=columns[0];ids=[r[key] for r in rows]
        result[str(part)]={'rows':len(rows),'columns':columns,'first_column':key,'distinct_first_column_values':len(set(ids)),'duplicate_first_column_rows':len(ids)-len(set(ids)),'period':'2025-26 per mirror catalogue; encoded columns require acquired schema','source_tier':2,'source':'OpenCity public mirror of UDISE+; primary release not independently downloaded','use':'Future education pipeline only, not available skilled-worker stock'}
    write_json(ROOT/'data/manifests/udise_quality.json',result);print('UDISE',[(k,v['rows'],len(v['columns'])) for k,v in result.items()],flush=True)

def main():
    dgt()
    target=ROOT/'data/raw/training/pib_naps_nats_2026_03_23.html'
    if not target.exists():
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(get('https://www.pib.gov.in/PressReleasePage.aspx?PRID=2243987&lang=1').content)
    logfile=ROOT/'data/manifests/download_log.json';logs=json.loads(logfile.read_text())
    if not any(r.get('source_id')=='pib_naps_nats' for r in logs):
        logs.append({'source_id':'pib_naps_nats','retrieved_at':now(),'status':'downloaded','filename':target.relative_to(ROOT).as_posix(),'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'source_page':'https://www.pib.gov.in/PressReleasePage.aspx?PRID=2243987&lang=1'})
        write_json(logfile,logs)
    apprenticeship(target);schools()

if __name__=='__main__':main()
