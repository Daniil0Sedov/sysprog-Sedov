from pathlib import Path
import hashlib,sys
if len(sys.argv)!=3:sys.exit('Использование: python verify_files.py <source_dir> <received_dir>')
src,dst=(Path(x) for x in sys.argv[1:])
if not src.is_dir() or not dst.is_dir():sys.exit('Обе папки должны существовать')
def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        while chunk:=f.read(1024*1024):h.update(chunk)
    return h.hexdigest()
errors=0
for p in sorted(src.rglob('*')):
    if not p.is_file():continue
    target=dst/p.relative_to(src)
    if not target.is_file():status='MISSING';errors+=1
    elif digest(p)!=digest(target):status='CHANGED';errors+=1
    else:status='OK'
    print(status, p.relative_to(src))
print('Errors:',errors)
sys.exit(1 if errors else 0)
