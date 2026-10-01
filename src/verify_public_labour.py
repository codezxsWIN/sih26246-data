"""Verify additive public labour and employer snapshots without changing them."""
import hashlib,json
from .acquire import ROOT
from .model_pack import read_csv

def verify_hashes(root,manifest):
    for name,digest in manifest.items():
        if hashlib.sha256((root/name).read_bytes()).hexdigest()!=digest:raise ValueError('Checksum mismatch: '+name)
    return len(manifest)

def main():
    labour=ROOT/'data/processed/public_labour/public-labour-20261001-v2'
    employer=ROOT/'data/processed/live_employers/employer-snapshot-20261001-v1'
    evidence=json.loads((labour/'acquisition_evidence.json').read_text())
    original=verify_hashes(ROOT,evidence['original_sha256'])
    raw=verify_hashes(ROOT,{r['filename']:r['sha256'] for r in evidence['requests']})
    outputs=sum(verify_hashes(folder,json.loads((folder/'output_hashes.json').read_text())) for folder in [labour,employer])
    rates=read_csv(labour/'plfs_workforce_rates.csv');baselines=read_csv(labour/'workforce_baseline_estimates.csv');history=read_csv(labour/'ncs_maharashtra_vacancy_history_context.csv')
    if (len(rates),len(baselines),len(history))!=(evidence['plfs_rate_observations'],evidence['workforce_baseline_estimates'],evidence['ncs_annual_vacancy_context_observations']):raise ValueError('Count mismatch')
    if any(r['available_analyst_supply']!='false' for r in rates) or any(r['available_data_analysts_estimate'] for r in baselines):raise ValueError('Unsupported skill supply claim')
    if any(r['eligible_for_pune_analyst_forecast']!='false' for r in history):raise ValueError('Unsupported historical forecast input')
    jobs=read_csv(employer/'public_employer_posting_observations.csv')
    if any(r['source_is_ncs']!='false' or r['eligible_for_verified_market_demand']!='false' for r in jobs):raise ValueError('Employer evidence misrepresented')
    print(json.dumps({'passed':True,'original_files_preserved':original,'raw_api_files_verified':raw,'output_files_verified':outputs,'plfs_rate_observations':len(rates),'workforce_baselines':len(baselines),'ncs_annual_context_observations':len(history),'public_employer_postings':len(jobs),'forecast_ready':False},indent=2))

if __name__=='__main__':main()
