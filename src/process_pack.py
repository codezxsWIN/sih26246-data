"""Create usable CSV extracts and flag observed source limitations."""
import csv
import io
import json
import re
import zipfile
from collections import Counter
from pathlib import Path

import openpyxl
from pypdf import PdfReader
from .acquire import ROOT,write_json
from .extract_ncs import csv_write

def extract_metadata():
    workbook=openpyxl.load_workbook(ROOT/'data/raw/ncs/ncs_metadata_2026_09.xlsx',read_only=True,data_only=True)
    def normalized(value):
        return '\n'.join(line.rstrip() for line in str(value or '').strip().splitlines())
    rows=[{'section':normalized(a),'field':normalized(b),'value':normalized(c)} for a,b,c in workbook.active.values if b or c]
    csv_write(ROOT/'data/processed/ncs/ncs_official_metadata.csv',rows,['section','field','value'])
    return len(rows)

def pmkvy():
    reader=PdfReader(ROOT/'data/raw/training/pmkvy_district_trained_2021_22.pdf')
    rows=[]
    for index,page in enumerate(reader.pages):
        for line in (page.extract_text() or '').splitlines():
            match=re.match(r'^Maharashtra\s+(.+?)\s+([\d,]+)\s*$',line.strip())
            if match:
                rows.append({'state':'Maharashtra','district':match[1].strip(),'financial_year':'2021-22',
                    'trained':int(match[2].replace(',','')),'page':index+1,
                    'source_url':'https://www.msde.gov.in/static/uploads/2024/05/Annexure-2.pdf'})
    if len(rows)!=36:raise ValueError(f'Expected 36 Maharashtra rows, got {len(rows)}; review extraction')
    csv_write(ROOT/'data/processed/training/pmkvy_maharashtra_district_training_2021_22.csv',rows,list(rows[0]))
    return len(rows)

def kaggle():
    with zipfile.ZipFile(ROOT/'data/raw/demand/kaggle_india_tech_2026.zip') as z:
        name='indian_tech_jobs_2026.csv'
        rows=list(csv.DictReader(io.StringIO(z.read(name).decode('utf-8-sig'))))
    pune=[row for row in rows if 'pune' in (row.get('location','')+' '+row.get('primary_city','')).lower()]
    for row in pune:
        row['source_tier']='3'
        row['date_quality_flag']='dataset_title_2026_but_scraped_at_2025_06_10;do_not_treat_as_current'
        row['description_truncated']=str(row['job_description'].rstrip().endswith('...'))
        row['salary_quality_flag']='undisclosed_zero_is_missing' if row['salary_disclosed'].lower()=='false' else ''
    csv_write(ROOT/'data/processed/demand/kaggle_pune_jobs.csv',pune,list(pune[0]))
    urls=[r['job_url'] for r in rows if r['job_url']]
    result={'rows':len(rows),'pune_location_mentions':len(pune),'distinct_nonempty_job_urls':len(set(urls)),
        'duplicate_nonempty_job_url_rows':len(urls)-len(set(urls)),
        'scraped_at_values':dict(Counter(r['scraped_at'] for r in rows)),
        'data_source_values':dict(Counter(r['data_source'] for r in rows)),
        'truncated_description_rows':sum(r['job_description'].rstrip().endswith('...') for r in rows),
        'columns':list(rows[0]),'suitability':'offline collector/parser development only; dates inconsistent; descriptions mostly truncated',
        'license':'Uploader lists CC BY-SA 4.0; original job-board rights are not independently established',
        'attribution':'Shreyash Gade (shree0910), Indian Tech Job Market 2026 | 23K+ Records, Kaggle',
        'source_url':'https://www.kaggle.com/datasets/shree0910/india-tech-job-market-2026-23k-records'}
    write_json(ROOT/'data/manifests/kaggle_quality.json',result)
    return result

def main():
    print('NCS metadata rows',extract_metadata(),flush=True)
    print('PMKVY Maharashtra rows',pmkvy(),flush=True)
    print('Kaggle audit',json.dumps(kaggle(),indent=2),flush=True)

if __name__=='__main__':main()
