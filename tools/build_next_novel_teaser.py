"""Rebuild the draft teaser from the owner's approved copy.
Only the draft branch is allowed in CI. No deployment is performed.
The cinematic street artwork remains a separate design task.
"""
from pathlib import Path
from copy import deepcopy
from html import escape
from bs4 import BeautifulSoup
import json
import os

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
if os.environ.get('GITHUB_ACTIONS') == 'true' and os.environ.get('GITHUB_REF_NAME') not in {'draft/next-novel-teaser', 'reading-room-press-expansion'}:
    raise SystemExit('This builder cannot publish to the live branch.')

def parsed(text):
    return BeautifulSoup(text, 'html.parser')

TITLE = 'Sunday Best'
SERIES = 'City of Favors'
SERIES_HTML = 'The first book in <em>City of Favors</em>, a new dark mafia romance series.'
PARAGRAPHS = [
    'Mara Hayes fought hard for the life she built. Her food truck, Sunday Best, is her livelihood, her independence, and her second chance.',
    'Alix Delorenzi comes from a family accustomed to getting what it wants.',
    'One expensive request brings their worlds together. When danger follows, Mara learns that accepting his protection may be just as risky as refusing it.',
]
EXACT_LINE = 'Mara learns that accepting his protection may be just as risky as refusing it.'
STATUS = 'Coming Soon | In Development'
BODY = ''.join('<p>' + escape(text) + '</p>' for text in PARAGRAPHS)

# Keep the tested layout. Apply the approved Night Truck colors without new artwork.
css_path = ROOT / 'next-novel.css'
marker = '/* Approved Sunday Best identity and Night Truck palette. */'
css_base = css_path.read_text(encoding='utf-8').split(marker)[0].rstrip()
CSS = css_base + '\n\n' + marker + r'''
.next-feature,.next-hero{--next-night:#101b1d;--next-light:#f2e7d5;--next-muted:#cfc5b7;--next-copper:#b49a68;--next-line:#596a66;background:radial-gradient(ellipse at 88% 20%,rgba(112,43,56,.24),transparent 62%),linear-gradient(125deg,#101b1d,#152226 65%,#121a1e)}
.next-feature h2.next-book-title{font:500 clamp(45px,4.8vw,65px)/1.06 var(--display);margin:21px 0 19px;letter-spacing:-.025em}
.next-feature-label .next-series{font:16px/1.7 var(--body);color:var(--next-muted);margin:0}
.next-series em{color:var(--next-light)}
.next-feature-copy>p:first-child{margin-top:0}
.next-feature-copy>p{margin-top:20px;font-size:18px;line-height:1.85}
.next-feature .btn,.next-hero .btn{color:var(--next-light);background:#702b38;border-color:#b49a68}
.next-feature .btn:hover,.next-hero .btn:hover{background:#57212c;border-color:var(--next-light);color:var(--next-light)}
.next-feature .next-progress{font-size:10px;letter-spacing:.04em;text-transform:none}
.next-hero .next-subtitle{max-width:650px;font-size:21px}
.next-hero .next-subtitle em{color:var(--next-light)}
.next-story-approved{padding-block:48px 50px}
.next-story-approved .next-synopsis{margin:35px auto 0;text-align:center;max-width:780px;border-top:1px solid var(--rule);padding-top:26px}
.next-story-approved .next-synopsis p{font:italic 25px/1.6 'IM Fell English',var(--body);color:var(--rust)}
.next-status .btn{font-size:12px}
@media(max-width:760px){.next-feature h2.next-book-title{font-size:53px;margin-block:15px}.next-feature-label .next-series{max-width:500px}.next-feature-copy>p{font-size:17px}.next-story-approved{padding-block:32px 35px}.next-story-approved .next-synopsis{margin-top:25px;padding-top:24px}.next-story-approved .next-synopsis p{font-size:22px}.next-hero .next-subtitle{font-size:19px}}
'''

HOME_SECTION = '''
<section class="next-feature" id="next-novel" aria-labelledby="next-novel-heading">
<div class="wrap next-feature-layout">
<div class="next-feature-label"><p class="eyebrow">Next from Sara Sweeney</p><h2 class="next-book-title" id="next-novel-heading">Sunday Best</h2><p class="next-series">''' + SERIES_HTML + '''</p><p class="next-progress">''' + STATUS + '''</p></div>
<div class="next-feature-copy">''' + BODY + '''<div class="next-actions"><a class="btn" href="next-novel.html">Discover the Story</a></div></div>
</div></section>
'''

TEASER_MAIN = '''
<main id="main">
<section class="next-hero" aria-labelledby="upcoming-title"><div class="wrap"><div class="next-back-row"><a class="next-backlink" href="index.html#next-novel">Back to the Reading Room</a></div><div class="next-hero-inner"><p class="eyebrow">Next from Sara Sweeney</p><h1 id="upcoming-title" tabindex="-1">Sunday Best</h1><p class="next-subtitle">''' + SERIES_HTML + '''</p><div class="next-divider" aria-hidden="true"></div><p class="next-progress">''' + STATUS + '''</p></div></div></section>
<section class="wrap next-story-approved" aria-labelledby="next-people-heading"><div class="section-heading"><div><p class="eyebrow">At the heart of the story</p><h2 id="next-people-heading">Mara &amp; Alix</h2></div></div><div class="next-character-grid">
<article class="next-character"><p class="eyebrow">01</p><h3>Mara Hayes</h3><p>''' + escape(PARAGRAPHS[0]) + '''</p></article>
<article class="next-character"><p class="eyebrow">02</p><h3>Alix Delorenzi</h3><p>''' + escape(PARAGRAPHS[1]) + '''</p></article>
</div><div class="next-synopsis"><p>''' + escape(PARAGRAPHS[2]) + '''</p></div></section>
<section class="wrap next-status" aria-labelledby="next-status-heading"><div class="next-status-box"><div><p class="eyebrow">Sunday Best · City of Favors</p><h2 id="next-status-heading">Coming Soon | In Development</h2><p>The cover and release date have not been announced.</p></div><a class="btn secondary" href="index.html#featured-book">Explore the Published Novel</a></div></section>
</main>
'''

# These files and these homepage regions must remain unchanged by this build.
protected_files = ['authors-desk.html','research-room.html','secondhand-shelf.html','the-year-that-wasnt-hers.html','chapter-1.html','reading-room-services.css','reading-room-home.css','research-packages.css','CNAME']
protected_bytes = {name:(ROOT / name).read_bytes() for name in protected_files}
home = parsed((ROOT / 'index.html').read_text(encoding='utf-8'))
protected_regions = {selector:str(home.select_one(selector)) for selector in ['#featured-book','#about','#find-your-place','header.site-header','footer.site-footer']}
for el in home.select('#next-novel'):
    el.decompose()
if not home.select_one('link[href="next-novel.css"]'):
    home.head.append(home.new_tag('link', rel='stylesheet', href='next-novel.css'))
home.select_one('#featured-book').insert_after(parsed(HOME_SECTION).section)
for selector,original in protected_regions.items():
    assert str(home.select_one(selector)) == original, selector
(ROOT / 'index.html').write_text(str(home), encoding='utf-8')
css_path.write_text(CSS, encoding='utf-8')

head = deepcopy(home.head)
for tag in head.find_all('script'):
    tag.decompose()
for tag in head.find_all('meta', attrs={'name': 'facebook-domain-verification'}):
    tag.decompose()
for tag in head.find_all('link', rel='canonical'):
    tag.decompose()
head.title.string = 'Sunday Best | City of Favors | Sara Sweeney'
head.find('meta', attrs={'name':'description'})['content'] = 'Sunday Best by Sara Sweeney. The first book in City of Favors, a new dark mafia romance series. Coming soon, in development.'
if not head.find('meta',attrs={'name':'robots'}):
    head.append(home.new_tag('meta',attrs={'name':'robots','content':'noindex,nofollow'}))
page = '<!doctype html><html lang="en">' + str(head) + '<body><a class="skip" href="#main">Skip to content</a>' + str(home.select_one('header.site-header')) + TEASER_MAIN + str(home.select_one('footer.site-footer')) + '</body></html>'
(ROOT / 'next-novel.html').write_text(page,encoding='utf-8')

preview = parsed((ROOT / 'preview.html').read_text(encoding='utf-8'))
style = preview.new_tag('style',id='next-novel-preview-css')
style.string = CSS
old_style = preview.find(id='next-novel-preview-css')
if old_style:
    old_style.replace_with(style)
else:
    preview.head.append(style)
for el in preview.select('#home #next-novel'):
    el.decompose()
preview.select_one('#home #featured-book').insert_after(parsed(HOME_SECTION).section)
for el in preview.select('#upcoming'):
    el.decompose()
upcoming = preview.new_tag('section',attrs={'class':'preview-page','id':'upcoming','aria-labelledby':'upcoming-title','hidden':''})
for child in list(parsed(TEASER_MAIN).main.contents):
    upcoming.append(child)
preview.find(id='preview-content').append(upcoming)
tab = preview.select_one('button[data-page="upcoming"]')
if tab is None:
    tab = preview.new_tag('button',attrs={'type':'button','class':'preview-tab','data-page':'upcoming','aria-controls':'upcoming','aria-pressed':'false'})
    preview.select_one('.preview-controls').append(tab)
tab.string = 'Sunday Best'
for link in preview.select('#upcoming a[href], #home #next-novel a[href]'):
    href=link['href']
    if href=='next-novel.html':
        link['data-page']='upcoming'
        link['href']='#upcoming'
    elif href.startswith('index.html#'):
        anchor=href.split('#',1)[1]
        link['data-page']='home'
        link['data-anchor']=anchor
        link['href']='#home/'+anchor
script_found=False
for script in preview.find_all('script'):
    text=script.string or script.get_text()
    old_ids="const ids=['home','authors','research','shelf'];"
    new_ids="const ids=['home','authors','research','shelf','upcoming'];"
    if old_ids in text:
        script.string=text.replace(old_ids,new_ids)
        script_found=True
    elif new_ids in text:
        script_found=True
assert script_found,'Preview router missing'
(ROOT / 'preview.html').write_text(str(preview),encoding='utf-8')

# Check the exact approved paragraphs in every rendered location.
for filename,selector in [('index.html','#next-novel'),('next-novel.html','main'),('preview.html','#upcoming'),('preview.html','#home #next-novel')]:
    soup=parsed((ROOT / filename).read_text(encoding='utf-8'))
    region=soup.select_one(selector)
    assert region is not None,(filename,selector)
    text=region.get_text(' ',strip=True)
    for paragraph in PARAGRAPHS:
        assert paragraph in text,(filename,selector,paragraph)
    assert text.count(EXACT_LINE)==1,(filename,selector)
    assert TITLE in text and SERIES in text and 'dark mafia romance' in text
    for forbidden in ['catering job','Her trust','isn’t for sale','shooting','Brightwater','set in Glennon','complications neither']:
        assert forbidden not in text,(filename,selector,forbidden)
    ids=[el['id'] for el in soup.find_all(id=True)]
    assert len(ids)==len(set(ids)),('Duplicate IDs',filename)
    for link in soup.select('a[href]'):
        href=link['href']
        if ':' in href or href.startswith('#'):
            continue
        assert (ROOT / href.split('#')[0]).is_file(),(filename,href)
for name,data in protected_bytes.items():
    assert (ROOT / name).read_bytes()==data,('Protected file changed',name)
assert '\u2014' not in HOME_SECTION+TEASER_MAIN
report={'built':True,'main_branch_changed':False,'book_title':TITLE,'series':SERIES,'exact_closing_line':EXACT_LINE,'approved_copy_verified_in_four_locations':True,'protected_files_unchanged':protected_files,'artwork_changed':False,'palette':'Night Truck','new_page':'next-novel.html','preview_view':'upcoming'}
(ROOT / 'next-novel-build-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
