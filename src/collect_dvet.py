"""Collect public DVET institute/trade reference data, excluding people/contact fields."""
import argparse,hashlib,time
from bs4 import BeautifulSoup
from .acquire import ROOT,get,now,write_json
from .extract_ncs import csv_write

BASE='https://inventory.dvet.gov.in'
PAGE=BASE+'/Home/SearchInstituteAndTrade'

def options(html,selector):
    select=BeautifulSoup(html,'html.parser').select_one(selector)
    if select is None:raise ValueError('Required public select missing: '+selector)
    return [{'id':o['value'],'name':o.get_text(' ',strip=True)} for o in select.select('option[value]') if o['value']!='-1']

def reference(path):
    response=get(BASE+path);value=response.json()
    if not isinstance(value,list):raise ValueError('Expected public reference list')
    return [{'id':r['DataValueField'],'name':r['DataTextField']} for r in value if r['DataValueField']!=-1]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pune-trades',action='store_true',help='One public trade-reference request per Pune institute, spaced one second apart')
    args=parser.parse_args();stamp=now()
    response=get(PAGE)
    institutes=options(response.text,'#optionIti');trades=options(response.text,'#optionTrade')
    raw=ROOT/'data/raw/training/dvet_reference_snapshot.json'
    pune=reference('/Home/GetInstituteByLocation?regionId=6&districtId=521')
    talukas=reference('/Home/GetTalukaByDistrict?districtId=521')
    links=[];errors=[];completed=[]
    if args.pune_trades:
        for institute in pune:
            url='/Home/GetTradeByInstitute?instituteId='+str(institute['id'])
            try:
                found=reference(url);completed.append(institute['id'])
                links.extend({'institute_id':institute['id'],'institute_name':institute['name'],'trade_id':t['id'],'trade_name':t['name'],'district':'Pune','retrieved_at':stamp,'source_url':BASE+url} for t in found)
                print('Institute',institute['id'],'trades',len(found),flush=True)
            except Exception as e:errors.append({'institute_id':institute['id'],'error':str(e)[:200]})
            time.sleep(1)
    write_json(raw,{'retrieved_at':stamp,'source_page':PAGE,'maharashtra_institutes':institutes,'trade_dictionary':trades,'pune_institutes':pune,'pune_talukas':talukas,'pune_institute_trade_links':links,'completed_institute_ids':completed,'errors':errors,'vintage_warning':'Service retrieved currently; page banner says admission 2022 while site constants say 2026. Reference records lack explicit effective year; do not treat as current capacity.'})
    output=ROOT/'data/processed/training'
    csv_write(output/'dvet_maharashtra_institutes.csv',institutes,['id','name'])
    csv_write(output/'dvet_trade_dictionary.csv',trades,['id','name'])
    csv_write(output/'dvet_pune_institutes.csv',pune,['id','name'])
    csv_write(output/'dvet_pune_talukas.csv',talukas,['id','name'])
    if links:csv_write(output/'dvet_pune_institute_trade_links.csv',links,list(links[0]))
    summary={'retrieved_at':stamp,'maharashtra_institutes':len(institutes),'trade_dictionary':len(trades),'pune_institutes':len(pune),'pune_talukas':len(talukas),'pune_institute_trade_links':len(links),'completed_institutes':len(completed),'errors':errors,'vintage':'Reference-service snapshot; effective academic year unverified','capacity':'Search POST sample returned zero rows; no capacity observations inferred'}
    write_json(ROOT/'data/manifests/dvet_quality.json',summary)
    import json
    logfile=ROOT/'data/manifests/download_log.json';logs=json.loads(logfile.read_text())
    logs.append({'source_id':'dvet_reference_api','retrieved_at':stamp,'status':'downloaded','filename':raw.relative_to(ROOT).as_posix(),'bytes':raw.stat().st_size,'sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'source_page':PAGE,'notes':'Whitelisted organizational/trade fields only; no staff/candidate contact data'})
    write_json(logfile,logs);print(summary,flush=True)

if __name__=='__main__':main()
