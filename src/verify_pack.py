"""Verify local hashes and aggregate counts, without network access."""
import csv,hashlib,json
from .acquire import ROOT,write_json

def main():
    checked=0;missing=[];withheld=[]
    excluded=set(json.loads((ROOT/'data/manifests/distribution_policy.json').read_text())['excluded_raw_files'])
    for r in json.loads((ROOT/'data/manifests/download_log.json').read_text()):
        if r['status']!='downloaded':continue
        path=ROOT/r['filename']
        if not path.exists():
            (withheld if r['filename'] in excluded else missing).append(r['filename'])
            continue
        content=path.read_bytes()
        if hashlib.sha256(content).hexdigest()!=r['sha256'] or len(content)!=r['bytes']:raise ValueError('Hash/size mismatch: '+r['filename'])
        checked+=1
    counts={}
    expected={'ncs/ncs_state_year_metrics.csv':1788,'ncs/ncs_maharashtra_year_metrics.csv':48,'training/pmkvy_maharashtra_district_training_2021_22.csv':36,'training/dgt_iti_grading_2026_27.csv':14743,'training/dgt_maharashtra_iti_grading_2026_27.csv':1046,'training/dvet_maharashtra_institutes.csv':952,'training/dvet_trade_dictionary.csv':95,'training/dvet_pune_institutes.csv':61,'training/dvet_pune_institute_trade_links.csv':405,'training/naps_nats_state_engagement_2025.csv':37}
    for name,n in expected.items():
        with (ROOT/'data/processed'/name).open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
        if len(rows)!=n:raise ValueError('Unexpected count: '+name)
        counts[name]=len(rows)
        if 'pmkvy_maharashtra' in name and next(r for r in rows if r['district']=='Pune')['trained']!='4206':raise ValueError('Pune training mismatch')
    flags=json.loads((ROOT/'data/manifests/ncs_quality_flags.json').read_text())
    if flags:raise ValueError('NCS reconciliation flags require review')
    dgt=json.loads((ROOT/'data/manifests/dgt_grading_quality.json').read_text())
    if dgt['parameter_sum_mismatch_iti_codes'] or not dgt['row_serials_contiguous']:raise ValueError('DGT reconciliation issue')
    dvet=json.loads((ROOT/'data/manifests/dvet_quality.json').read_text())
    if dvet['errors'] or dvet['completed_institutes']!=dvet['pune_institutes']:raise ValueError('DVET institute collection incomplete')
    result={'raw_files_hash_verified':checked,'raw_files_missing':missing,'intentionally_withheld_raw_files':withheld,'csv_counts':counts,'ncs_numerical_flags':len(flags),'status':('distributed_pack_verified' if withheld else 'complete_local_pack_verified') if not missing else 'aggregate_repository_verified_raw_pack_not_installed'}
    write_json(ROOT/'data/manifests/validation.json',result);print(json.dumps(result,indent=2))

if __name__=='__main__':main()
