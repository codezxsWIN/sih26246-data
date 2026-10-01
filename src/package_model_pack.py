"""Create a new private local archive without overwriting any earlier ZIP."""
import argparse,hashlib,json,zipfile
from .acquire import ROOT

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--filename',default='sih26246-model-input-pack-20261001-v1.zip')
    args=parser.parse_args()
    if '/' in args.filename or '\\' in args.filename or not args.filename.endswith('.zip'):raise ValueError('Use a ZIP filename, not a path')
    destination=ROOT.parent/args.filename
    previous={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.parent.glob('*.zip')}
    if destination.exists():raise FileExistsError('Existing archives are never overwritten')
    logs=json.loads((ROOT/'data/manifests/download_log.json').read_text())
    excluded=set(json.loads((ROOT/'data/manifests/distribution_policy.json').read_text())['excluded_raw_files'])
    raw={r['filename'] for r in logs if r['status']=='downloaded' and r['filename'] not in excluded}
    raw.update({'data/raw/ncs/evidence/dashboard_table.html','data/raw/ncs/evidence/dashboard_tables.js'})
    files=[]
    for path in ROOT.rglob('*'):
        if not path.is_file():continue
        relative=path.relative_to(ROOT);name=relative.as_posix()
        if any(p in {'.git','.venv','__pycache__','work','dist'} for p in relative.parts):continue
        if path.name.startswith('.env') or path.suffix in {'.pyc','.pem','.key'}:continue
        if name.startswith('data/private/') or name in excluded:continue
        if name.startswith('data/raw/') and name not in raw:continue
        files.append(path)
    with zipfile.ZipFile(destination,'x',compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:archive.write(path,'sih26246-data/'+path.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(destination) as archive:
        if archive.testzip():raise ValueError('Archive integrity failure')
        members=set(archive.namelist())
        if any('sih26246-data/'+name in members for name in excluded):raise ValueError('Distribution policy violation')
    for name,digest in previous.items():
        if hashlib.sha256((ROOT.parent/name).read_bytes()).hexdigest()!=digest:raise ValueError('Previous archive changed')
    print(json.dumps({'archive':str(destination),'files':len(files),'bytes':destination.stat().st_size,'sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),'previous_archives_unchanged':list(previous)},indent=2))

if __name__=='__main__':main()
