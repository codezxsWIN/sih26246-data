"""One-shot public employer snapshot; not an NCS workaround or market estimate.

Documented read-only APIs: https://github.com/lever/postings-api
and https://docs.greenhouse.io/job-board.html
"""
import argparse,hashlib,json,re,time
from datetime import datetime,timezone
from .acquire import ROOT,get,write_json
from .extract_ncs import csv_write
from .model_data import role_scope,extract_skills

def posting_metadata(row,observed):
    posted=datetime.fromtimestamp(row['createdAt']/1000,timezone.utc).date().isoformat() if row.get('createdAt') else ''
    if posted and posted>observed[:10]:raise ValueError('Posting created in future')
    return {'source_id':'lever_parallelwireless','source_job_id':row['id'],'company':'Parallel Wireless','job_title':row['text'],'location':row['categories']['location'],
        'job_url':row.get('hostedUrl',''),'posted_date':posted,'date_semantics':'API createdAt; not independently verified first publication',
        'observed_date':observed[:10],'observed_at':observed,'status':'present_in_public_employer_feed','vacancy_count':'',
        'source_tier':'2','eligible_for_verified_market_demand':'false','source_is_ncs':'false',
        'usage_permission':'public_GET_documented; employer_reuse_terms_not_reviewed','coverage':'one_employer; nonrepresentative_sample'}

def collect(run_id):
    if not re.fullmatch(r'[A-Za-z0-9_-]+',run_id):raise ValueError('Unsafe run ID')
    output=ROOT/'data/processed/live_employers'/run_id
    if output.exists():raise FileExistsError('Existing snapshots never overwritten')
    observations=[];requests=[];skills=[];observed=datetime.now(timezone.utc).isoformat()
    for board in ['capco','modulrfinance']:
        url=f'https://boards-api.greenhouse.io/v1/boards/{board}/jobs'
        response=get(url);payload=response.json();rows=payload['jobs']
        if payload.get('meta',{}).get('total',len(rows))!=len(rows):raise ValueError('Incomplete employer board')
        requests.append({'source':board,'url':url,'http_status':response.status_code,'jobs_scanned':len(rows),'response_sha256':hashlib.sha256(response.content).hexdigest(),'matched_pune_data_analyst_titles':sum(role_scope(r['title'])=='target' and bool(re.search(r'\bPune\b',r['location']['name'],re.I)) for r in rows)})
        time.sleep(0.5)
    url='https://api.lever.co/v0/postings/parallelwireless?mode=json'
    response=get(url);rows=response.json()
    if not isinstance(rows,list):raise ValueError('Unexpected Lever payload')
    for row in rows:
        if role_scope(row.get('text',''))!='target' or not re.search(r'\bPune\b',row.get('categories',{}).get('location',''),re.I):continue
        record=posting_metadata(row,observed);observations.append(record)
        # Full descriptions, forms and any applicant/contact data are not persisted.
        text=' '.join([row.get('descriptionPlain',''),row.get('descriptionBodyPlain',''),*[(r.get('content','')) for r in row.get('lists',[])]])
        for match in extract_skills(text):skills.append({'source_id':record['source_id'],'source_job_id':record['source_job_id'],'skill_id':match['skill_id'],'matched_text':match['matched_text'],'evidence_scope':'rule-based match in employer feed description; full text not retained','source_url':record['job_url'],'observed_at':observed})
    requests.append({'source':'parallelwireless','url':url,'http_status':response.status_code,'jobs_scanned':len(rows),'response_sha256':hashlib.sha256(response.content).hexdigest(),'matched_pune_data_analyst_titles':len(observations)})
    output.mkdir(parents=True)
    fields=['source_id','source_job_id','company','job_title','location','job_url','posted_date','date_semantics','observed_date','observed_at','status','vacancy_count','source_tier','eligible_for_verified_market_demand','source_is_ncs','usage_permission','coverage']
    csv_write(output/'public_employer_posting_observations.csv',observations,fields)
    csv_write(output/'skill_mentions.csv',skills,['source_id','source_job_id','skill_id','matched_text','evidence_scope','source_url','observed_at'])
    result={'observed_at':observed,'public_employer_postings':len(observations),'ncs_live_postings':0,'forecast_ready':False,'full_descriptions_or_personal_data_saved':False,'requests':requests,'limitations':['Presence is not hiring confirmation or vacancy count','No historical snapshots yet; not suitable for backtesting','Employer reuse rights require review','Creation timestamp is not guaranteed first publication date']}
    write_json(output/'acquisition_evidence.json',result)
    write_json(output/'output_hashes.json',{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in output.iterdir() if p.is_file()})
    print(json.dumps(result,indent=2))

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--run-id',required=True);args=parser.parse_args();collect(args.run_id)

if __name__=='__main__':main()
