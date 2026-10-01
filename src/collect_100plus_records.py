"""Acquire public bulk records using publisher downloads and anonymous APIs.

Sources: data.gov.in static downloads, AISHE reports, Skill India course API,
and the NQR public summary-download form linked by NSDC's standards page.
All output files are exclusive new files. NQR's session CSRF value stays in memory.
"""
import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from .acquire import ROOT, get, validate

RUN = '20261002-v1'
DOWNLOADS = {
    'ogd_jss_district_training': (
        'https://www.data.gov.in/resource/district-wise-enrolled-and-assessed-jan-shikshan-sansthan-jss-27-april-2022',
        'https://www.data.gov.in/files/ogdpv2dms/s3fs-public/JSS_EA_270422.csv', 'ogd_jss_20220427.csv', 'csv'),
    'aishe_2023_24': (
        'https://aishe.gov.in/document-category/aishe-final-reports/',
        'https://cdnbbsr.s3waas.gov.in/s392049debbe566ca5782a3045cf300a3c/uploads/2026/07/202607131602421770.pdf', 'aishe_2023_24.pdf', 'pdf'),
    'aishe_2022_23': (
        'https://aishe.gov.in/document-category/aishe-final-reports/',
        'https://cdnbbsr.s3waas.gov.in/s392049debbe566ca5782a3045cf300a3c/uploads/2026/07/20260708401535366.pdf', 'aishe_2022_23.pdf', 'pdf'),
}


def save(path, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(body)


def save_json(path, value):
    save(path, (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode('utf-8'))


def evidence(source, url, body, extra=None):
    row = {'source_id': source, 'url': url,
           'retrieved_at': datetime.now(timezone.utc).isoformat(),
           'bytes': len(body), 'sha256': hashlib.sha256(body).hexdigest()}
    row.update(extra or {})
    return row


def collect_static(output, source):
    page, url, filename, kind = DOWNLOADS[source]
    response = get(url)
    validate(response.content, kind)
    save(output / filename, response.content)
    save_json(output / (source + '_evidence.json'), evidence(
        source, url, response.content, {'source_page': page, 'access': 'public static download'}))
    print(source, filename, len(response.content), flush=True)


def collect_courses(output):
    url = 'https://courses.skillindiadigital.gov.in/api/courses/v1/courses/?page_size=100'
    rows = []
    logs = []
    visited = set()
    counts = set()
    while url:
        if url in visited or len(visited) >= 50:
            raise ValueError('Pagination loop or unexpected number of pages')
        parsed = urlparse(url)
        if parsed.scheme != 'https' or parsed.hostname != 'courses.skillindiadigital.gov.in' or parsed.path != '/api/courses/v1/courses/':
            raise ValueError('Unexpected course pagination URL')
        visited.add(url)
        response = get(url)
        payload = response.json()
        results = payload['results']
        if not isinstance(results, list):
            raise ValueError('Unexpected course result shape')
        rows.extend(results)
        counts.add(payload['pagination']['count'])
        filename = f'skillindia_courses_page_{len(visited):02}.json'
        save(output / filename, response.content)
        logs.append(evidence('skillindia_public_courses', url, response.content,
                             {'filename': filename, 'rows': len(results)}))
        print('skillindia', len(visited), len(rows), flush=True)
        url = payload['pagination']['next']
        if url:
            time.sleep(0.25)
    ids = [r['id'] for r in rows]
    stable = len(counts) == 1 and len(rows) == next(iter(counts)) and len(set(ids)) == len(ids)
    save_json(output / 'skillindia_courses_evidence.json', {
        'downloaded_rows': len(rows), 'unique_ids': len(set(ids)),
        'advertised_counts': sorted(counts), 'consistent_snapshot': stable, 'pages': logs})
    if not stable:
        print('WARNING: catalogue changed during pagination; completeness is not established', flush=True)


def collect_nqr(output):
    # This is the normal public download form, including its anonymous session CSRF.
    page = 'https://nqr.gov.in/qualifications-search'
    with requests.Session() as session:
        response = session.get(page, timeout=(15, 45))
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        form = soup.find('form', id='qualificationid-form')
        if form is None or form.get('action') != 'https://nqr.gov.in/downloadSummaryFile':
            raise ValueError('NQR public form changed')
        fields = {i['name']: i.get('value', '') for i in form.find_all('input', attrs={'name': True})}
        if set(fields) != {'_token', 'qualificationids'}:
            raise ValueError('NQR download fields changed')
        response = session.post(form['action'], data=fields, timeout=(15, 60))
        response.raise_for_status()
        validate(response.content, 'xlsx')
        save(output / 'nqr_public_qualification_summary.xlsx', response.content)
        save_json(output / 'nqr_qualifications_evidence.json', evidence(
            'nqr_public_qualifications', form['action'], response.content,
            {'source_page': page, 'access': 'anonymous public summary-download form',
             'csrf_persisted': False, 'content_type': response.headers.get('Content-Type')}))
        print('nqr_public_qualifications', len(response.content), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', default=RUN)
    parser.add_argument('--sources', nargs='+', default=list(DOWNLOADS) + ['skillindia', 'nqr'])
    args = parser.parse_args()
    if Path(args.run).name != args.run or args.run in ('.', '..'):
        raise ValueError('Run must be a single directory name')
    output = ROOT / 'data/raw/records_100plus' / args.run
    for source in args.sources:
        if source in DOWNLOADS:
            collect_static(output, source)
        elif source == 'skillindia':
            collect_courses(output)
        elif source == 'nqr':
            collect_nqr(output)
        else:
            raise ValueError('Unknown source: ' + source)


if __name__ == '__main__':
    main()
