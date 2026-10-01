"""Build an additive Data Analyst input pack. Never modify acquired data or old runs."""
import argparse,csv,hashlib,json,re
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
from .acquire import ROOT,write_json
from .extract_ncs import csv_write
from .model_data import JOB_FIELDS,IMPORT_FIELDS,extract_skills,role_scope,record_id,deduplicate,production_errors,readiness

def read_csv(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def create_run_directory(path):
    path.mkdir(parents=True,exist_ok=False)

def fallback_record(row,observed_at):
    source='kaggle_india_tech_2026';native=row.get('job_id','');url=row.get('job_url','')
    out={k:'' for k in JOB_FIELDS}
    out.update(record_id=record_id(source,native,url),source_id=source,source_job_id=native,job_url=url,
        job_title=row.get('job_title',''),occupation='Data Analyst' if role_scope(row.get('job_title',''))=='target' else '',
        role_scope=role_scope(row.get('job_title','')),company=row.get('company_name',''),location=row.get('location',''),
        geography_scope='Pune mentioned; may be multi-location',description=row.get('job_description',''),skills_raw=row.get('skills_required',''),
        observed_at=observed_at,status='unknown',salary_disclosed=row.get('salary_disclosed','').lower(),
        usage_permission='unverified_upstream_rights',date_quality='inconsistent',source_tier='3',eligible_for_verified_demand='false',
        quality_flags='prototype_only;publisher_dates_inconsistent;posting_date_unknown;vacancy_count_unknown;availability_unknown')
    for new,old in [('experience_min_years','experience_min_yrs'),('experience_max_years','experience_max_yrs')]:out[new]=row.get(old,'')
    if out['salary_disclosed']=='true':
        out['salary_min_lpa']=row.get('salary_min_lpa','');out['salary_max_lpa']=row.get('salary_max_lpa','')
    if row.get('job_description','').rstrip().endswith('...'):out['quality_flags']+=';description_truncated'
    return out

def context_rows(root):
    result=[]
    def add(source,geo,level,period,measure,value,unit,url,limitation):
        result.append({'source_id':source,'geography':geo,'geography_level':level,'period':period,'measure':measure,'value':value,'unit':unit,'role_scope':'all_roles','use':'context_only','supports_available_data_analyst_supply':'false','source_url':url,'limitation':limitation})
    for row in read_csv(root/'data/processed/ncs/ncs_maharashtra_year_metrics.csv'):
        add('ncs_dashboard',row['state'],'state',row['financial_year'],row['metric'],row['value'],'publisher_count',row['source_url'],'Metric definitions require confirmation; not Pune role-level observations; 2026-2027 partial')
    for row in read_csv(root/'data/processed/training/pmkvy_maharashtra_district_training_2021_22.csv'):
        add('pmkvy_district_training_2021_22',row['district'],'district',row['financial_year'],'trained',row['trained'],'people_trained',row['source_url'],'Historical training flow, not available skilled-worker stock')
    for row in read_csv(root/'data/processed/training/naps_nats_state_engagement_2025.csv'):
        if row['state_ut']=='Maharashtra':
            for key in ['naps_engaged','nats_engaged']:add('pib_naps_nats','Maharashtra','state',row['calendar_year'],key,row[key],'apprenticeship_engagements',row['source_url'],'Training engagements; no Data Analyst or Pune disaggregation')
    return result

def reviewed_sources(root):
    rows=json.loads((root/'config/approved_job_sources.json').read_text())['approved_sources']
    return {r['source_id'] for r in rows if all(r.get(k) for k in ['reviewer','reviewed_at','evidence_reference']) and r.get('permission_scope')=='job_data_analysis'}

def import_jobs(root,path):
    if path is None:return [],[]
    with path.open(encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        if set(reader.fieldnames or [])!=set(IMPORT_FIELDS):raise ValueError('Import columns must exactly match job_import_template.csv; no personal/contact fields allowed')
        rows=list(reader)
    approved=reviewed_sources(root);accepted=[];rejected=[]
    for i,row in enumerate(rows,2):
        errors=production_errors(row)
        if row.get('source_id') not in approved:errors.append('source_not_reviewed_and_approved')
        if errors:rejected.append({'csv_line':i,'reasons':'|'.join(sorted(set(errors)))});continue
        job={k:row.get(k,'') for k in JOB_FIELDS}
        job.update(record_id=record_id(row['source_id'],row['source_job_id'],row.get('job_url','')),occupation='Data Analyst',role_scope='target',geography_scope='Pune mentioned; review multi-location',eligible_for_verified_demand='true',quality_flags='status_and_market_coverage_require_separate_review')
        accepted.append(job)
    return accepted,rejected

def write_features(path,jobs):
    skill_ids=list(json.loads((ROOT/'config/data_analyst_skills.json').read_text())['skills'])
    features=[];evidence=[]
    for job in jobs:
        extracted=extract_skills(job['skills_raw']);found={r['skill_id'] for r in extracted}
        features.append({'record_id':job['record_id'],**{s:int(s in found) for s in skill_ids},'eligible_for_verified_demand':job['eligible_for_verified_demand']})
        evidence.extend({'record_id':job['record_id'],'evidence_field':'skills_raw',**r} for r in extracted)
    csv_write(path/'skill_features.csv',features,['record_id',*skill_ids,'eligible_for_verified_demand'])
    csv_write(path/'skill_evidence.csv',evidence,['record_id','evidence_field','skill_id','matched_text','start','end','extraction_method'])
    return Counter(r['skill_id'] for r in evidence)

def build(root,output,prototype_output,job_import=None):
    if output.exists() or prototype_output.exists():raise FileExistsError('Use new run directories; existing data must not be overwritten')
    before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/'data').rglob('*') if p.is_file()}
    accepted,rejected=import_jobs(root,job_import)
    source=root/'data/processed/demand/kaggle_pune_jobs.csv'
    rows=read_csv(source) if source.exists() else []
    logs=json.loads((root/'data/manifests/download_log.json').read_text())
    timestamp=next((r['retrieved_at'][:10] for r in reversed(logs) if r.get('source_id')=='kaggle_india_tech_2026' and r['status']=='downloaded'),'')
    selected=[fallback_record(r,timestamp) for r in rows if role_scope(r.get('job_title',''))=='target']
    prototype,duplicates=deduplicate(selected);production,prod_duplicates=deduplicate(accepted)
    context=context_rows(root)
    create_run_directory(output);create_run_directory(prototype_output)
    csv_write(output/'production_jobs.csv',production,JOB_FIELDS)
    csv_write(output/'job_import_template.csv',[],IMPORT_FIELDS)
    csv_write(output/'import_rejections.csv',rejected,['csv_line','reasons'])
    csv_write(output/'context_observations.csv',context,list(context[0]))
    for name in ['dvet_pune_institute_trade_links.csv','dgt_maharashtra_iti_grading_2026_27.csv']:
        records=read_csv(root/'data/processed/training'/name)
        csv_write(output/name,records,list(records[0]))
    csv_write(prototype_output/'jobs.csv',prototype,JOB_FIELDS)
    duplicate_fields=['canonical_source_id','canonical_source_job_id','duplicate_source_id','duplicate_source_job_id','identity_key']
    csv_write(prototype_output/'duplicate_links.csv',duplicates,duplicate_fields)
    csv_write(output/'production_duplicate_links.csv',prod_duplicates,duplicate_fields)
    skill_counts=write_features(prototype_output,prototype);write_features(output,production)
    csv_write(prototype_output/'skill_posting_counts.csv',[{'skill_id':k,'posting_count':v,'use':'prototype_demonstration_only','period':'unknown','not_current_demand':'true'} for k,v in sorted(skill_counts.items())],['skill_id','posting_count','use','period','not_current_demand'])
    csv_write(output/'available_supply_import_template.csv',[],['source_id','occupation','skill_id','geography','geography_level','period_start','period_end','available_people_estimate','lower_bound','upper_bound','unit','estimation_method','assumptions','evidence_reference','review_status'])
    csv_write(output/'demand_history_import_template.csv',[],['source_id','occupation','skill_id','geography','month','measure','value','unit','coverage_definition','collection_complete','review_status'])
    csv_write(output/'planner_outputs.csv',[{'occupation':'Data Analyst','geography':'Pune','demand':None,'available_supply':None,'gap':None,'forecast_6_month':None,'forecast_12_month':None,'severity':'not_assessed','forecast_confidence':None,'training_capacity_recommendation':None,'status':'missing_comparable_demand_supply_and_history'}],['occupation','geography','demand','available_supply','gap','forecast_6_month','forecast_12_month','severity','forecast_confidence','training_capacity_recommendation','status'])
    changed=[str(p.relative_to(root)) for p,digest in before.items() if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest]
    if changed:raise ValueError('Existing data changed: '+str(changed))
    result={**readiness(len(production),len(prototype),len(context)),'workflow':['Labour market data','Aggregation and normalisation','Demand + supply engine','Demand-supply gap','6-12 month forecast','Shortage/surplus severity','Planner dashboard','Training/capacity recommendations'],'prototype_target_rows_before_dedup':len(selected),'prototype_duplicates_retained_in_audit':len(duplicates),'prototype_skill_posting_counts':dict(skill_counts),'production_import_rejections':len(rejected),'existing_data_unchanged':True,'existing_data_files_checked':len(before),'schema_version':'1.0.0','built_at':datetime.now(timezone.utc).isoformat(),'prototype_data_location':str(prototype_output),'extraction':'Rule-based skill aliases, not an AI model; review required','missing_values':'Blank CSV cells/null JSON values mean unknown, never zero'}
    write_json(output/'readiness.json',result)
    write_json(output/'input_preservation.json',{'all_existing_data_unchanged':True,'checked_files':len(before),'sha256_by_relative_path':{p.relative_to(root).as_posix():d for p,d in before.items()}})
    result['prototype_data_location']=prototype_output.relative_to(root).as_posix() if prototype_output.is_relative_to(root) else prototype_output.name
    write_json(output/'readiness.json',result)
    write_json(prototype_output/'output_hashes.json',{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in prototype_output.iterdir() if p.is_file()})
    files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in output.iterdir() if p.is_file()}
    write_json(output/'output_hashes.json',files)
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id',default=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    parser.add_argument('--job-import',type=Path)
    args=parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_-]+',args.run_id):raise ValueError('Run ID must be a safe directory name')
    result=build(ROOT,ROOT/'data/model_input/runs'/args.run_id,ROOT/'data/model_input/local_prototype'/args.run_id,args.job_import)
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
