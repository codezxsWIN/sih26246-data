"""Download public files with native certificate validation and provenance."""
import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests
import truststore
from bs4 import BeautifulSoup

truststore.inject_into_ssl()
ROOT = Path(__file__).resolve().parents[1]

def now():
    return datetime.now(timezone.utc).isoformat()

def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding='utf-8')

def get(url):
    response = requests.get(url, timeout=(15, 60), headers={
        'User-Agent': 'SIH26246-DataDiscovery/0.1 (research; public files only)'
    })
    response.raise_for_status()
    return response

def validate(body, kind):
    if kind == 'pdf' and not body.startswith(b'%PDF'):
        raise ValueError('Expected PDF; server returned another format')
    if kind in ('xlsx','zip') and not body.startswith(b'PK'):
        raise ValueError('Expected ZIP/XLSX; server returned another format')
    if kind == 'json':
        json.loads(body)
    if kind == 'csv' and (body.lstrip().startswith(b'<') or b'<!DOCTYPE html' in body[:1000]):
        raise ValueError('Expected CSV; server returned HTML')

def download(source):
    entry = {'source_id': source['id'], 'retrieved_at': now(), 'status': 'failed'}
    try:
        response = get(source['download_url'])
        validate(response.content, source['format'])
        target = ROOT/'data/raw'/source['filename']
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(response.content)
        entry.update(status='downloaded', http_status=response.status_code,
                     content_type=response.headers.get('Content-Type'),
                     bytes=len(response.content), sha256=hashlib.sha256(response.content).hexdigest(),
                     filename=str(target.relative_to(ROOT)).replace('\\','/'),
                     source_page=source['url'], download_host=urlparse(response.url).hostname)
    except (requests.RequestException, ValueError) as error:
        entry['error'] = str(error).split('?')[0][:400]
    return entry

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--only', nargs='*', help='Source IDs; default all configured downloads')
    args=parser.parse_args()
    sources=json.loads((ROOT/'config/downloads.json').read_text(encoding='utf-8'))
    results=[]
    for source in sources:
        if args.only and source['id'] not in args.only:
            continue
        entry=download(source); results.append(entry)
        print(source['id'],entry['status'],entry.get('bytes',entry.get('error')))
        time.sleep(1)
    path=ROOT/'data/manifests/download_log.json'
    existing=json.loads(path.read_text(encoding='utf-8')) if path.exists() else []
    write_json(path,existing+results)
    if any(r['status']=='failed' for r in results):
        raise SystemExit(1)

if __name__ == '__main__':
    main()
