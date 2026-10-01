"""Verify local hashes and aggregate counts, without network access."""
import csv,hashlib,json
from .acquire import ROOT,write_json

def main():
    checked=0;missing=[]
    for r in json.loads((ROOT/'data/manifests/download_log.json').read_text()):
        if r['status']!='downloaded':continue
        path=ROOT/r['filename']
        if not path.exists():missing.append(r['filename']);continue
        content=path.read_bytes()
        if hashlib.sha256(content).hexdigest()!=r['sha256'] or len(content)!=r['bytes']:raise ValueError('Hash/size mismatch: '+r['filename'])
        checked+=1
    counts={}
    for name,n in {'ncs/ncs_state_year_metrics.csv':1788,'ncs/ncs_maharashtra_year_metrics.csv':48,'training/pmkvy_maharashtra_district_training_2021_22.csv':36}.items():
        with (ROOT/'data/processed'/name).open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
        if len(rows)!=n:raise ValueError('Unexpected count: '+name)
        counts[name]=len(rows)
        if name.startswith('training/') and next(r for r in rows if r['district']=='Pune')['trained']!='4206':raise ValueError('Pune training mismatch')
    flags=json.loads((ROOT/'data/manifests/ncs_quality_flags.json').read_text())
    if flags:raise ValueError('NCS reconciliation flags require review')
    result={'raw_files_hash_verified':checked,'raw_files_missing':missing,'csv_counts':counts,'ncs_numerical_flags':len(flags),'status':'complete_local_pack_verified' if not missing else 'aggregate_repository_verified_raw_pack_not_installed'}
    write_json(ROOT/'data/manifests/validation.json',result);print(json.dumps(result,indent=2))

if __name__=='__main__':main()
