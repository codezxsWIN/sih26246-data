"""Pure normalization and eligibility rules. No network calls or prediction claims."""
import hashlib,json,re
from datetime import date
from urllib.parse import urlsplit,urlunsplit,parse_qsl,urlencode
from .acquire import ROOT

JOB_FIELDS=['record_id','source_id','source_job_id','job_url','job_title','occupation','role_scope','company','location','geography_scope','description','skills_raw','posted_date','observed_at','closing_date','status','experience_min_years','experience_max_years','salary_min_lpa','salary_max_lpa','salary_disclosed','vacancy_count','usage_permission','date_quality','source_tier','eligible_for_verified_demand','quality_flags']
IMPORT_FIELDS=['source_id','source_job_id','job_url','job_title','company','location','description','skills_raw','posted_date','observed_at','closing_date','status','experience_min_years','experience_max_years','salary_min_lpa','salary_max_lpa','salary_disclosed','vacancy_count','usage_permission','date_quality','source_tier']

def extract_skills(text):
    dictionary=json.loads((ROOT/'config/data_analyst_skills.json').read_text())['skills']
    found=[]
    for skill,aliases in dictionary.items():
        matches=[m for alias in aliases for m in re.finditer(r'(?<!\w)'+re.escape(alias)+r'(?!\w)',text or '',re.I)]
        if matches:
            match=min(matches,key=lambda m:m.start())
            found.append({'skill_id':skill,'matched_text':match.group(),'start':match.start(),'end':match.end(),'extraction_method':'rule_based_alias_v1'})
    return found

def role_scope(title):
    if re.search(r'\bdata[\s_-]+analyst\b',title or '',re.I):return 'target'
    if re.search(r'\b(business analyst|bi analyst|business intelligence analyst|reporting analyst)\b',title or '',re.I):return 'adjacent_review'
    return 'out_of_scope'

def canonical_url(value):
    parts=urlsplit((value or '').strip())
    query=[(k,v) for k,v in parse_qsl(parts.query,keep_blank_values=True) if not k.lower().startswith('utm_') and k.lower() not in {'gclid','fbclid'}]
    return urlunsplit((parts.scheme.lower(),parts.netloc.lower(),parts.path,urlencode(sorted(query)),''))

def deduplicate(rows):
    seen={};kept=[];links=[]
    for row in rows:
        url=canonical_url(row.get('job_url',''))
        key=url or row['source_id']+':'+row['source_job_id']
        if key in seen:
            links.append({'canonical_source_id':seen[key]['source_id'],'canonical_source_job_id':seen[key]['source_job_id'],'duplicate_source_id':row['source_id'],'duplicate_source_job_id':row['source_job_id'],'identity_key':key})
        else:seen[key]=row;kept.append(row)
    return kept,links

def production_errors(row):
    errors=[]
    for field in ['source_id','source_job_id','job_title','location','description','posted_date','observed_at']:
        if not str(row.get(field,'')).strip():errors.append(field+'_missing')
    if str(row.get('source_tier','')) not in {'1','2'}:errors.append('prototype_source')
    if row.get('usage_permission')!='confirmed':errors.append('usage_permission_unconfirmed')
    if row.get('date_quality')!='verified':errors.append('dates_unverified')
    if role_scope(row.get('job_title',''))!='target':errors.append('not_target_role')
    if not re.search(r'\bPune\b',row.get('location',''),re.I):errors.append('not_pune_location')
    parsed={}
    for field in ['posted_date','observed_at','closing_date']:
        if row.get(field):
            try:parsed[field]=date.fromisoformat(row[field])
            except (ValueError,TypeError):errors.append(field+'_invalid')
    if parsed.get('posted_date') and parsed.get('observed_at') and parsed['posted_date']>parsed['observed_at']:errors.append('posting_after_observation')
    if parsed.get('observed_at') and parsed['observed_at']>date.today():errors.append('observation_in_future')
    return errors

def record_id(source,job_id,url):
    return hashlib.sha256((source+'|'+job_id+'|'+canonical_url(url)).encode()).hexdigest()[:24]

def readiness(verified,prototype,context):
    return {'prototype_ingestion_ready':prototype>0,'context_ready':context>0,'verified_demand_ready':verified>0,
        'available_data_analyst_supply_ready':False,'gap_ready':False,'skill_growth_ready':False,
        'forecast_ready':False,'forecast_confidence':None,
        'blocked_reasons':['Comparable Pune Data Analyst workforce supply not acquired','No validated repeated demand history/backtesting dataset','Prototype postings have inconsistent dates and cannot count as verified demand'],
        'verified_postings':verified,'prototype_postings':prototype,'context_observations':context}
