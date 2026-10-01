"""Read-only validation of a model-input snapshot and preserved original data."""
import argparse,hashlib,json,re
from collections import Counter
from .acquire import ROOT
from .model_pack import read_csv
from .model_data import production_errors

def validate_jobs(jobs,features,eligible):
    ids=[r['record_id'] for r in jobs]
    if len(ids)!=len(set(ids)):raise ValueError('Duplicate job record IDs')
    feature_ids=[r['record_id'] for r in features]
    if len(feature_ids)!=len(set(feature_ids)) or set(ids)!=set(feature_ids):raise ValueError('Feature/job join mismatch')
    for row in jobs+features:
        if row['eligible_for_verified_demand']!=eligible:raise ValueError('Production/prototype eligibility mismatch')
    for row in features:
        if any(v not in {'0','1'} for k,v in row.items() if k not in {'record_id','eligible_for_verified_demand'}):raise ValueError('Skill features must be binary')

def validate(root,output,prototype):
    checked=0
    for folder in [output,prototype]:
        manifest=json.loads((folder/'output_hashes.json').read_text())
        for name,digest in manifest.items():
            if hashlib.sha256((folder/name).read_bytes()).hexdigest()!=digest:raise ValueError('Output checksum mismatch: '+name)
            checked+=1
    original=json.loads((output/'input_preservation.json').read_text())
    for name,digest in original['sha256_by_relative_path'].items():
        if hashlib.sha256((root/name).read_bytes()).hexdigest()!=digest:raise ValueError('Original file changed: '+name)
    production=read_csv(output/'production_jobs.csv');fallback=read_csv(prototype/'jobs.csv')
    validate_jobs(production,read_csv(output/'skill_features.csv'),'true')
    validate_jobs(fallback,read_csv(prototype/'skill_features.csv'),'false')
    for row in production:
        if production_errors(row):raise ValueError('Invalid production record')
    evidence=read_csv(prototype/'skill_evidence.csv');jobs={r['record_id']:r for r in fallback}
    seen=set()
    for row in evidence:
        key=(row['record_id'],row['skill_id'])
        if key in seen:raise ValueError('Duplicate skill evidence per job')
        seen.add(key)
        text=jobs[row['record_id']][row['evidence_field']]
        if text[int(row['start']):int(row['end'])]!=row['matched_text']:raise ValueError('Invalid skill evidence span')
    actual=Counter(r['skill_id'] for r in evidence)
    expected={r['skill_id']:int(r['posting_count']) for r in read_csv(prototype/'skill_posting_counts.csv')}
    if dict(actual)!=expected:raise ValueError('Skill counts do not reconcile')
    context=read_csv(output/'context_observations.csv')
    if any(r['supports_available_data_analyst_supply']!='false' for r in context):raise ValueError('Context misrepresented as available supply')
    readiness=json.loads((output/'readiness.json').read_text())
    if (readiness['verified_postings'],readiness['prototype_postings'],readiness['context_observations'])!=(len(production),len(fallback),len(context)):raise ValueError('Readiness counts mismatch')
    planner=read_csv(output/'planner_outputs.csv')
    for row in planner:
        if row['severity']!='not_assessed' or any(row[k] for k in ['demand','available_supply','gap','forecast_6_month','forecast_12_month','forecast_confidence','training_capacity_recommendation']):raise ValueError('Unsupported planner output')
    return {'passed':True,'output_files_hash_verified':checked,'original_files_hash_verified':len(original['sha256_by_relative_path']),'verified_postings':len(production),'prototype_postings':len(fallback),'context_observations':len(context),'skill_evidence_rows':len(evidence)}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--run-id',required=True);args=parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_-]+',args.run_id):raise ValueError('Unsafe run ID')
    print(json.dumps(validate(ROOT,ROOT/'data/model_input/runs'/args.run_id,ROOT/'data/model_input/local_prototype'/args.run_id),indent=2))

if __name__=='__main__':main()
