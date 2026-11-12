"""Apply the approved decorative sketch without changing any reader-facing copy."""
from pathlib import Path
import base64, hashlib, json, os, re
from PIL import Image
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT)
if os.environ.get('GITHUB_ACTIONS')=='true' and os.environ.get('GITHUB_REF_NAME') not in {'draft/next-novel-teaser','reading-room-press-expansion'}:
    raise SystemExit('Artwork installation is restricted to draft branches.')
source=ROOT/'assets/sunday-best-night-sketch-source.avif'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='0c9df487156dca5df913dbe2f4023ca33d849e1fcfb2c1c7b46978e63bbf82ca', 'Approved artwork checksum mismatch'
asset=ROOT/'assets/sunday-best-night-sketch.webp'
with Image.open(source) as im:
    assert im.size==(1200,675),im.size
    im.convert('RGB').save(asset,'WEBP',quality=95,method=6)
css=(ROOT/'night-sketch.css').read_text(encoding='utf-8')
protected=['authors-desk.html','research-room.html','secondhand-shelf.html','chapter-1.html','the-year-that-wasnt-hers.html','reading-room-services.css','reading-room-home.css','research-packages.css','CNAME']
snapshots={name:(ROOT/name).read_bytes() for name in protected}
unchanged=[]
for name in ['index.html','next-novel.html']:
    path=ROOT/name
    original=path.read_text(encoding='utf-8')
    if not re.search(r'<link\b[^>]*href=[\"\x27]night-sketch\.css[\"\x27]',original):
        updated=original.replace('</head>','<link rel="stylesheet" href="night-sketch.css"></head>',1)
    else: updated=original
    assert BeautifulSoup(original,'html.parser').body.decode_contents()==BeautifulSoup(updated,'html.parser').body.decode_contents()
    path.write_text(updated,encoding='utf-8')
    unchanged.append(name)
path=ROOT/'preview.html'
original=path.read_text(encoding='utf-8')
original_body=BeautifulSoup(original,'html.parser').body.decode_contents()
# Inline the optimized approved asset so third-party preview needs no CSS downloads.
data='data:image/webp;base64,'+base64.b64encode(asset.read_bytes()).decode('ascii')
preview_css=css.replace('assets/sunday-best-night-sketch.webp',data)
updated=re.sub(r'<style\b[^>]*id=[\"\x27]night-sketch-preview[\"\x27][^>]*>.*?</style>','',original,flags=re.S)
updated=updated.replace('</head>','<style id="night-sketch-preview">'+preview_css+'</style></head>',1)
assert BeautifulSoup(updated,'html.parser').body.decode_contents()==original_body
path.write_text(updated,encoding='utf-8')
unchanged.append('preview.html')
builder=ROOT/'tools/build_next_novel_teaser.py'
s=builder.read_text(encoding='utf-8')
marker='# Preserve the approved Night Truck sketch on future draft rebuilds.'
if marker not in s:
    s+='\n\n'+marker+'\nimport subprocess, sys\nartwork_installer = ROOT / "tools/install_night_sketch.py"\nif artwork_installer.exists():\n    subprocess.run([sys.executable, str(artwork_installer)], check=True)\n'
    builder.write_text(s,encoding='utf-8')
for name,data_before in snapshots.items():assert (ROOT/name).read_bytes()==data_before,name
report={'approved_artwork_source':'noir_food_truck_at_dusk.png','optimized_size':[1200,675],'webp_bytes':asset.stat().st_size,'unchanged_page_bodies':unchanged,'protected_files_unchanged':protected,'main_branch_changed':False}
(ROOT/'night-sketch-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
