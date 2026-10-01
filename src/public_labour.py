"""Acquire public PLFS aggregates, not private microdata or live NCS postings.

Endpoint evidence: https://github.com/nso-india/mospi-esankhyiki
Uses Windows' native HTTPS transport without disabling certificate checks.
"""
import argparse,hashlib,json,math,re,subprocess,time
from collections import defaultdict
from datetime import datetime,timezone
from urllib.parse import urlencode
from .acquire import ROOT,write_json
from .extract_ncs import csv_write
from .model_pack import read_csv

ENDPOINTS={'getData','getIndicatorListByFrequency','getFilterByIndicatorId'}
DIMENSIONS=['geography','year','year_type','frequency','quarter','month','sector','gender','age_group','reference_status','education','religion','social_group']

def api_url(endpoint,params):
    if endpoint not in ENDPOINTS:raise ValueError('Unapproved PLFS endpoint')
    if 'limit' in params and not 1<=int(params['limit'])<=200:raise ValueError('PLFS page limit must be 1-200')
    return 'https://api.mospi.gov.in/api/plfs/'+endpoint+'?'+urlencode(params)

def native_json(url):
    if not re.fullmatch(r'https://api\.mospi\.gov\.in/api/plfs/[A-Za-z]+\?[A-Za-z0-9_.%=&+\-]*',url):raise ValueError('Unsafe API URL')
    command="$ErrorActionPreference='Stop'; [Console]::OutputEncoding=[System.Text.Encoding]::UTF8; (Invoke-WebRequest -UseBasicParsing -Uri '"+url+"' -MaximumRedirection 0 -TimeoutSec 25).Content"
    result=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',command],capture_output=True,timeout=35)
    if result.returncode:raise RuntimeError('Native HTTPS request failed; certificate validation retained')
    payload=json.loads(result.stdout.decode('utf-8-sig'))
    if payload.get('statusCode') is not True:raise ValueError('API did not confirm successful data retrieval')
    return payload

def normalize_plfs(rows,evidence,url):
    normalized=[]
    for row in rows:
        value=float(row['value'])
        if row.get('unit')!='%' or not math.isfinite(value) or not 0<=value<=100:raise ValueError('Invalid percentage')
        normalized.append({'source_id':'mospi_plfs_api','geography':row.get('state',''),'geography_level':'national' if row.get('state')=='All India' else 'state','year':row.get('year',''),'year_type':row.get('year_type') or '',
            'frequency':row.get('frequency',''),'quarter':row.get('quarter') or '', 'month':row.get('month') or '',
            'indicator':row.get('indicator',''),'value':value,'unit':'percent','sector':row.get('sector',''),'gender':row.get('gender',''),
            'age_group':row.get('AgeGroup',''),'reference_status':row.get('weekly_status') or '',
            'education':row.get('General_Education') or '', 'religion':row.get('religion') or '', 'social_group':row.get('socialGroup') or '',
            'role_scope':'all_roles','use':'workforce_baseline_only','available_analyst_supply':'false',
            'methodology_note':'2025 survey redesign: do not concatenate pre/post redesign as homogeneous series; empty dimensions mean publisher unspecified, not all',
            'evidence_file':evidence,'source_url':url})
    return normalized

def workforce_baselines(rows):
    groups=defaultdict(dict)
    for row in rows:
        measure=row['indicator'].split()[0]
        if measure in {'LFPR','WPR','UR'}:
            key=tuple(row[k] for k in DIMENSIONS)
            if measure in groups[key]:raise ValueError('Duplicate indicator within comparable dimensions')
            groups[key][measure]=row
    results=[]
    for key,values in groups.items():
        if not {'LFPR','UR'}<=values.keys():continue
        lfpr=values['LFPR']['value'];ur=values['UR']['value'];wpr=values.get('WPR',{}).get('value')
        unemployed=lfpr*ur/100
        results.append({**dict(zip(DIMENSIONS,key)),'lfpr_percent':lfpr,'ur_percent':ur,'wpr_percent':wpr,
            'unemployed_per_100_population':round(unemployed,4),'implied_employed_per_100_population':round(lfpr-unemployed,4),
            'wpr_rounding_residual':round(wpr-(lfpr-unemployed),4) if wpr is not None else '',
            'unit':'persons_per_100_population_in_matching_age_group','available_data_analysts_estimate':'',
            'role_scope':'all_roles','use':'baseline_not_skill_supply','formula':'LFPR * UR / 100',
            'limitations':'No population denominator, occupation/skill match, job-search availability or uncertainty interval; not an absolute workforce count',
            'evidence_files':'|'.join(sorted({r['evidence_file'] for r in values.values()}))})
    return results

def collect(run_id):
    if not re.fullmatch(r'[A-Za-z0-9_-]+',run_id):raise ValueError('Unsafe run ID')
    raw=ROOT/'data/raw/public_labour'/run_id;output=ROOT/'data/processed/public_labour'/run_id
    if raw.exists() or output.exists():raise FileExistsError('Never overwrite earlier collection runs')
    before={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'data').rglob('*') if p.is_file()}
    raw.mkdir(parents=True);output.mkdir(parents=True);log=[];all_rows=[]
    def fetch(name,endpoint,params):
        url=api_url(endpoint,params);payload=native_json(url);path=raw/(name+'.json')
        write_json(path,payload)
        log.append({'source_id':'mospi_plfs_api','url':url,'retrieved_at':datetime.now(timezone.utc).isoformat(),'filename':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'status':'downloaded','records':len(payload.get('data',[]))})
        time.sleep(0.5)
        return payload,path.relative_to(ROOT).as_posix(),url
    for frequency in [1,2,3]:
        indicators,_,_=fetch('indicators_'+str(frequency),'getIndicatorListByFrequency',{'frequency_code':frequency})
        codes={r['indicator_code'] for r in indicators['data']}
        if not {1,2,3}<=codes:raise ValueError('Expected LFPR/WPR/UR indicators not available')
        metadata,_,_=fetch('filters_'+str(frequency),'getFilterByIndicatorId',{'indicator_code':1,'frequency_code':frequency})
        if frequency!=3:
            states=metadata['data']['state'];mh=next(r['state_code'] for r in states if r['description']=='Maharashtra')
        for indicator in [1,2,3]:
            for annual_type in ([1,2] if frequency==1 else [None]):
                params={'indicator_code':indicator,'frequency_code':frequency,'gender_code':3,'age_code':1,'sector_code':2,'limit':200,'page':1}
                if frequency!=3:params['state_code']=mh
                if frequency==1:params.update(year_type_code=annual_type,weekly_status_code=1,education_code=0,religion_code=1,social_category_code=1)
                name=f'data_f{frequency}_i{indicator}_y{annual_type or 0}'
                payload,evidence,url=fetch(name,'getData',params)
                meta=payload.get('meta_data',{})
                if int(meta.get('totalPages',1))>1:raise ValueError('Unexpected pagination: refuse incomplete collection')
                if int(meta.get('totalRecords',len(payload['data'])))!=len(payload['data']):raise ValueError('Record count mismatch')
                normalized=normalize_plfs(payload['data'],evidence,url)
                expected='All India' if frequency==3 else 'Maharashtra'
                if any(r['geography']!=expected for r in normalized):raise ValueError('Server ignored geography filter')
                all_rows.extend(normalized)
    csv_write(output/'plfs_workforce_rates.csv',all_rows,list(all_rows[0]))
    baselines=workforce_baselines(all_rows)
    csv_write(output/'workforce_baseline_estimates.csv',baselines,list(baselines[0]))
    history=[]
    for row in read_csv(ROOT/'data/processed/ncs/ncs_maharashtra_year_metrics.csv'):
        if row['metric'].lower()!='vacancies':continue
        year=row['financial_year'];partial=year.startswith('2026')
        history.append({**row,'geography_level':'state','role_scope':'all_roles','frequency':'financial_year','partial_period':str(partial).lower(),'eligible_for_pune_analyst_forecast':'false','use':'historical_demand_context_only','limitation':'Publisher vacancy aggregate; not Pune role-level monthly observations; confirm stock/flow definitions'})
    csv_write(output/'ncs_maharashtra_vacancy_history_context.csv',history,list(history[0]))
    for path,digest in before.items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=digest:raise ValueError('Existing data changed: '+path)
    result={'run_id':run_id,'retrieved_at':datetime.now(timezone.utc).isoformat(),'api_key_required_for_this_aggregate_access':False,'raw_json_downloads':len(log),'plfs_rate_observations':len(all_rows),'workforce_baseline_estimates':len(baselines),'ncs_annual_vacancy_context_observations':len(history),'live_ncs_postings_acquired':0,'pune_data_analyst_available_workforce_estimate':None,'pune_data_analyst_forecast_ready':False,'existing_files_preserved':len(before),'requests':log,'original_sha256':before}
    write_json(output/'acquisition_evidence.json',result)
    write_json(output/'output_hashes.json',{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in output.iterdir() if p.is_file()})
    print(json.dumps({k:v for k,v in result.items() if k not in {'requests','original_sha256'}},indent=2))

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--run-id',required=True);args=parser.parse_args();collect(args.run_id)

if __name__=='__main__':main()
