"""Package repository and acquired data; exclude credentials and unrelated site code."""
import hashlib,json,zipfile
from .acquire import ROOT

def main():
    destination=ROOT.parent/'sih26246-data-pack.zip'
    logs=json.loads((ROOT/'data/manifests/download_log.json').read_text())
    raw={r['filename'] for r in logs if r['status']=='downloaded'}
    raw.update({'data/raw/ncs/evidence/dashboard_table.html','data/raw/ncs/evidence/dashboard_tables.js'})
    files=[]
    for path in ROOT.rglob('*'):
        if not path.is_file():continue
        relative=path.relative_to(ROOT);parts=relative.parts;name=relative.as_posix()
        if any(p in {'.git','.venv','__pycache__','work','dist'} for p in parts):continue
        if path.name.startswith('.env') or path.suffix in {'.pyc','.pem','.key'}:continue
        if name.startswith('data/raw/') and name not in raw:continue
        if name.startswith('data/private/'):continue
        files.append(path)
    with zipfile.ZipFile(destination,'w',compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:archive.write(path,'sih26246-data/'+path.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(destination) as archive:
        bad=archive.testzip()
        if bad:raise ValueError('Corrupt archive member: '+bad)
    checksum=hashlib.sha256(destination.read_bytes()).hexdigest()
    print(json.dumps({'archive':str(destination),'files':len(files),'bytes':destination.stat().st_size,'sha256':checksum},indent=2))

if __name__=='__main__':main()
