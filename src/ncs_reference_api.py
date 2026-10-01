"""Collect public NCS reference APIs when the user has enabled site access.

Not a partner API client. No login, candidate profiles, resume endpoints or keys.
The endpoint list is observed from the public NCS website on 2026-10-01.
"""
import argparse
import json
import time
from .acquire import ROOT,get,write_json,now

ENDPOINTS={
    'states':'https://api.ncs.gov.in/api/location/state',
    'functional_areas':'https://api.ncs.gov.in/employer-service/api/functional-areas-master/fetch-all-functional-area',
    'top_companies':'https://api.ncs.gov.in/employer-service/api/v1/hiring/top-companies?year=2026&limit=4'
}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--enabled-access',action='store_true',help='Confirm site access is enabled before collection')
    args=parser.parse_args()
    if not args.enabled_access:
        parser.error('Site access was denied in the acquisition session; enable access before running this connector.')
    results=[]
    for name,url in ENDPOINTS.items():
        response=get(url)
        value=response.json()
        if not isinstance(value,dict) or not isinstance(value.get('data'),list):
            raise ValueError('Expected JSON data list; endpoint format may have changed')
        write_json(ROOT/f'data/raw/ncs/{name}_api.json',value)
        results.append({'name':name,'url':url,'http_status':response.status_code,'retrieved_at':now(),'records':len(value['data'])})
        time.sleep(1)
    write_json(ROOT/'data/manifests/ncs_reference_api_run.json',results)
    print(json.dumps(results,indent=2))

if __name__=='__main__':main()
