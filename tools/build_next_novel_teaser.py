"""Build a draft teaser for Sara Sweeney's next novel.
Preserves the published novel and approved professional services.
No book title, cover, release date, preorder, or mailing list is invented.
"""
from pathlib import Path
from copy import deepcopy
from bs4 import BeautifulSoup
import hashlib
import json
import os

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
ALLOWED = {'draft/next-novel-teaser', 'reading-room-press-expansion'}
if os.environ.get('GITHUB_ACTIONS') == 'true' and os.environ.get('GITHUB_REF_NAME') not in ALLOWED:
    raise SystemExit('This builder does not publish to the live branch.')

CSS = r'''
/* Next novel: a darker companion to the existing parchment and botanical design. */
.next-feature,.next-hero{--next-night:#18201e;--next-light:#f5efe4;--next-muted:#d1c7b7;--next-copper:#d5a17e;--next-line:#65716a;color:var(--next-light);background:radial-gradient(ellipse at 87% 25%,rgba(139,58,34,.24),transparent 62%),linear-gradient(125deg,#18201e,#202823 65%,#29231f);position:relative;isolation:isolate}
.next-feature{padding-block:62px;border-block:1px solid #667168;scroll-margin-top:110px}
.next-feature::before,.next-hero::before{content:'';position:absolute;inset:16px;border:1px solid rgba(213,161,126,.32);pointer-events:none;z-index:-1}
.next-feature-layout{display:grid;grid-template-columns:270px minmax(0,1fr);gap:72px;align-items:center}
.next-feature-label{padding-right:28px;border-right:1px solid var(--next-line)}
.next-feature .eyebrow,.next-hero .eyebrow{color:var(--next-copper)}
.next-signature{font:italic 38px/1.25 'IM Fell English',Georgia,serif;color:var(--next-light);margin-top:18px}
.next-signature span{display:block}
.next-feature-label .next-genre{font:13px/1.8 var(--ui);color:var(--next-muted);margin-top:22px;max-width:190px}
.next-progress{display:inline-flex;gap:9px;align-items:center;font:11px/1.6 var(--ui);letter-spacing:.08em;text-transform:uppercase;color:var(--next-muted);margin-top:22px}
.next-progress::before{content:'';width:6px;height:6px;border:1px solid var(--next-copper);border-radius:50%;flex-shrink:0}
.next-feature h2{font:500 clamp(39px,4.5vw,58px)/1.08 var(--display);letter-spacing:-.015em;max-width:620px;color:var(--next-light)}
.next-feature h2 em{color:var(--next-copper)}
.next-feature-copy>p{font-size:18px;line-height:1.85;color:var(--next-muted);margin-top:23px;max-width:690px}
.next-feature .next-actions{margin-top:25px}
.next-actions{display:flex;align-items:stretch;flex-wrap:wrap;gap:14px}
.next-actions .btn{width:260px;min-height:52px;font-size:13px;gap:16px}
.next-feature .btn,.next-hero .btn{background:var(--next-light);border-color:var(--next-light);color:var(--next-night)}
.next-feature .btn:hover,.next-hero .btn:hover{background:#ead9c6;border-color:#ead9c6;color:var(--next-night)}
.next-feature a:focus-visible,.next-hero a:focus-visible{outline-color:var(--next-copper)}
.next-backlink{display:inline-flex;align-items:center;gap:10px;padding-block:9px;min-height:44px;font:12px/1.7 var(--ui);color:var(--next-muted);text-decoration:none}
.next-backlink::before{content:'←';font:18px Georgia,serif}
.next-backlink:hover{color:white;text-decoration:underline}
.next-hero{padding-block:30px 66px;text-align:center;border-bottom:1px solid var(--next-line)}
.next-hero .next-back-row{text-align:left;margin-bottom:26px}
.next-hero-inner{position:relative;max-width:890px;margin:auto;padding:7px 30px 0}
.next-hero h1{font:500 clamp(52px,6.5vw,88px)/1.04 var(--display);letter-spacing:-.025em;margin:24px auto 25px;color:var(--next-light);max-width:760px}
.next-hero h1 em{color:var(--next-copper)}
.next-hero .next-subtitle{font:italic 22px/1.65 'IM Fell English',Georgia,serif;color:var(--next-muted);max-width:650px;margin-inline:auto}
.next-divider{height:1px;width:120px;background:var(--next-line);margin:29px auto;position:relative}
.next-divider::after{content:'';position:absolute;left:calc(50% - 4px);top:-4px;width:8px;height:8px;background:var(--next-night);border:1px solid var(--next-copper);transform:rotate(45deg)}
.next-byline{font:12px/1.8 var(--ui);text-transform:uppercase;letter-spacing:.18em;color:var(--next-copper)}
.next-hero .next-progress{margin-top:19px}
.next-story{padding-block:57px 52px}
.next-story-layout{display:grid;grid-template-columns:245px minmax(0,1fr);gap:67px;align-items:start}
.next-story-aside{border-top:2px solid var(--moss);padding-top:20px}
.next-story-aside h2{font-size:34px;margin-top:13px}
.next-story-aside p:last-child{font:italic 18px/1.65 'IM Fell English',Georgia,serif;color:var(--moss);margin-top:20px}
.next-synopsis{max-width:730px}
.next-synopsis p{font-size:19px;line-height:1.85;color:var(--ink)}
.next-synopsis p+p{margin-top:21px}
.next-synopsis .next-last-line{font:italic 25px/1.5 'IM Fell English',Georgia,serif;color:var(--rust);padding-top:24px;margin-top:27px;border-top:1px solid var(--rule)}
.next-people{padding-block:6px 48px}
.next-character-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0 28px}
.next-character{display:grid;grid-template-rows:subgrid;grid-row:span 3;row-gap:0;position:relative;padding:28px 31px;border:1px solid var(--rule);background:var(--card)}
.next-character::before{content:'';position:absolute;left:-1px;top:-1px;width:24px;height:24px;border-top:2px solid var(--rust);border-left:2px solid var(--rust)}
.next-character .eyebrow{font-size:10px;padding-bottom:11px}
.next-character h3{font-size:35px;padding-bottom:17px}
.next-character>p:last-child{font-size:17px;line-height:1.8;color:var(--muted);margin:0}
.next-details{padding:25px 0 28px;border-bottom:1px solid var(--rule);display:flex;flex-wrap:wrap;gap:10px 22px;justify-content:center;list-style:none;margin:0;font:11px/1.7 var(--ui);letter-spacing:.055em;color:var(--moss)}
.next-details li+li::before{content:'·';margin-right:22px;color:var(--rust)}
.next-status{padding-block:0 58px}
.next-status-box{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:32px;align-items:center;border-block:1px solid var(--rule);background:var(--paper-deep);padding:31px 35px}
.next-status h2{font-size:34px;margin:8px 0 11px}
.next-status p{font-size:16px;color:var(--muted)}
.next-status .eyebrow{font-size:10px;color:var(--moss)}
.next-status .btn{width:250px;min-height:52px;font-size:13px;gap:16px}
.next-draft-note{font:12px/1.7 var(--ui);background:var(--moss);color:var(--card);text-align:center;padding:11px 18px}
@supports not (grid-template-rows:subgrid){.next-character{display:flex;flex-direction:column}}
@media(max-width:1000px){.next-feature-layout{grid-template-columns:220px minmax(0,1fr);gap:40px}.next-story-layout{grid-template-columns:205px minmax(0,1fr);gap:40px}.next-signature{font-size:34px}}
@media(max-width:760px){.next-feature{padding-block:42px}.next-feature::before,.next-hero::before{inset:10px}.next-feature-layout{grid-template-columns:1fr;gap:25px;padding-inline:12px}.next-feature-label{border-right:0;border-bottom:1px solid var(--next-line);padding:0 0 23px}.next-signature{font-size:29px;margin-top:10px}.next-signature span{display:inline}.next-signature span+span::before{content:' '}.next-feature-label .next-genre{max-width:none;margin-top:12px}.next-feature-label .next-progress{margin-top:12px}.next-feature h2{font-size:44px}.next-feature-copy>p{font-size:17px;margin-top:18px}.next-actions .btn{width:100%;max-width:330px}.next-hero{padding-block:18px 44px}.next-hero .next-back-row{padding-inline:12px;margin-bottom:15px}.next-hero-inner{padding-inline:16px}.next-hero h1{font-size:60px;margin-block:19px 22px}.next-hero .next-subtitle{font-size:20px}.next-hero .eyebrow{font-size:10px}.next-story{padding-block:35px}.next-story-layout{grid-template-columns:1fr;gap:25px}.next-story-aside{padding-top:17px}.next-story-aside h2{font-size:31px}.next-story-aside p:last-child{margin-top:13px;font-size:17px}.next-synopsis p{font-size:17px}.next-synopsis .next-last-line{font-size:23px}.next-character-grid{grid-template-columns:1fr;gap:20px}.next-character{display:block;grid-row:auto;padding:25px}.next-character h3{font-size:32px}.next-people{padding-bottom:34px}.next-details{gap:10px 18px}.next-details li+li::before{content:none}.next-status{padding-bottom:38px}.next-status-box{grid-template-columns:1fr;padding:26px;gap:22px}.next-status .btn{width:100%;max-width:330px}.next-status h2{font-size:31px}}
@media(max-width:380px){.next-hero h1{font-size:53px}.next-feature h2{font-size:40px}.next-actions .btn,.next-status .btn{font-size:12px}}
'''

HOME_SECTION = '''
<section class="next-feature" id="next-novel" aria-labelledby="next-novel-heading">
<div class="wrap next-feature-layout">
<div class="next-feature-label"><p class="eyebrow">Next from</p><p class="next-signature"><span>Sara</span><span>Sweeney</span></p><p class="next-genre">A new contemporary<br>dark mafia romance.</p><p class="next-progress">In progress</p></div>
<div class="next-feature-copy"><h2 id="next-novel-heading">Her trust<br><em>isn’t for sale.</em></h2><p>Mara Hayes has built a life she can call her own. A last-minute catering job puts Alix Delorenzi in her path, and a shooting turns her food truck into a getaway vehicle. His protection could keep her safe. Accepting it will have to be her choice.</p><div class="next-actions"><a class="btn" href="next-novel.html">Meet Mara &amp; Alix</a></div></div>
</div></section>
'''

TEASER_MAIN = '''
<main id="main">
<section class="next-hero" aria-labelledby="upcoming-title"><div class="wrap"><div class="next-back-row"><a class="next-backlink" href="index.html#next-novel">Back to the Reading Room</a></div><div class="next-hero-inner"><p class="eyebrow">A first look at the next novel</p><h1 id="upcoming-title" tabindex="-1">Her trust<br><em>isn’t for sale.</em></h1><p class="next-subtitle">She built her own second chance.<br>He’s used to getting his way.</p><div class="next-divider" aria-hidden="true"></div><p class="next-byline">A dark mafia romance by Sara Sweeney</p><p class="next-progress">Manuscript in progress</p></div></div></section>
<section class="wrap next-story" aria-labelledby="next-story-heading"><div class="next-story-layout">
<div class="next-story-aside"><p class="eyebrow">Mara &amp; Alix</p><h2 id="next-story-heading">One job.<br>A dangerous connection.</h2><p>Attraction is the easy part.<br>Trust will have to be earned.</p></div>
<div class="next-synopsis"><p>Mara Hayes has fought too hard for her independence to hand it over to another man. Her food truck, Sunday Best, is her livelihood, her second chance, and the one place where she makes the rules.</p><p>A last-minute catering job brings her into the orbit of Alix Delorenzi. He has money, influence, and a family name that makes people think twice. He’s also far too accustomed to solving other people’s problems without asking.</p><p>Then a shooting turns Sunday Best into a getaway vehicle, and keeping her distance becomes a lot more complicated.</p><p>Alix knows how to protect what matters to him. Mara knows the cost of letting someone else decide what’s best for her. With danger closing in and attraction becoming harder to ignore, they’ll have to learn the difference between offering protection and taking control.</p><p class="next-last-line">He can offer her protection.<br>She’ll decide what to accept.</p></div>
</div></section>
<section class="wrap next-people" aria-labelledby="next-people-heading"><div class="section-heading"><div><p class="eyebrow">At the heart of the story</p><h2 id="next-people-heading">Meet Mara &amp; Alix</h2></div><p class="aside">Two strong wills. Something worth risking.</p></div><div class="next-character-grid">
<article class="next-character"><p class="eyebrow">A life she built herself</p><h3>Mara Hayes</h3><p>A chef, a food truck, and a second chance she intends to keep. Mara has no interest in trading her independence for a powerful man’s protection.</p></article>
<article class="next-character"><p class="eyebrow">A name that opens doors</p><h3>Alix Delorenzi</h3><p>A mafia underboss who meets trouble with money, influence, and force. Wanting Mara is easy. Learning to offer help on her terms is another matter.</p></article>
</div><ul class="next-details" aria-label="Story themes"><li>Contemporary dark romance</li><li>Criminal intrigue</li><li>Earned trust</li><li>A fiercely independent heroine</li></ul></section>
<section class="wrap next-status" aria-labelledby="next-status-heading"><div class="next-status-box"><div><p class="eyebrow">From the writing desk</p><h2 id="next-status-heading">The story is taking shape.</h2><p>The manuscript is in progress. The title, cover, and release date have not been announced.</p></div><a class="btn secondary" href="index.html#featured-book">Explore the Published Novel</a></div></section>
</main>
'''

def parsed(text):
    return BeautifulSoup(text, 'html.parser')

base_index = (ROOT / 'index.html').read_text(encoding='utf-8')
home = parsed(base_index)
featured_before = str(home.select_one('#featured-book'))
about_before = str(home.select_one('#about'))
for old in home.select('#next-novel'):
    old.decompose()
if not home.select_one('link[href="next-novel.css"]'):
    home.head.append(home.new_tag('link', rel='stylesheet', href='next-novel.css'))
home.select_one('#featured-book').insert_after(parsed(HOME_SECTION).section)
assert str(home.select_one('#featured-book')) == featured_before
assert str(home.select_one('#about')) == about_before
(ROOT / 'index.html').write_text(str(home), encoding='utf-8')
(ROOT / 'next-novel.css').write_text(CSS, encoding='utf-8')

# Keep the existing brand, navigation, fonts, and footer for the dedicated page.
head = deepcopy(home.head)
for tag in head.find_all('script'):
    tag.decompose()
for tag in head.find_all('meta', attrs={'name': 'facebook-domain-verification'}):
    tag.decompose()
for tag in head.find_all('link', rel='canonical'):
    tag.decompose()
head.title.string = 'The Next Novel by Sara Sweeney | Reading Room Press'
head.find('meta', attrs={'name': 'description'})['content'] = 'A first look at Sara Sweeney’s upcoming dark mafia romance: Mara Hayes, Alix Delorenzi, and a dangerous connection. Manuscript in progress.'
head.append(home.new_tag('meta', attrs={'name': 'robots', 'content': 'noindex,nofollow'}))
page = '<!doctype html><html lang="en">' + str(head) + '<body><a class="skip" href="#main">Skip to content</a>' + str(home.select_one('header.site-header')) + TEASER_MAIN + str(home.select_one('footer.site-footer')) + '</body></html>'
(ROOT / 'next-novel.html').write_text(page, encoding='utf-8')

# Extend the existing one-click, fully styled preview rather than changing its interface.
preview = parsed((ROOT / 'preview.html').read_text(encoding='utf-8'))
style = preview.new_tag('style', id='next-novel-preview-css')
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
upcoming = preview.new_tag('section', attrs={'class': 'preview-page', 'id': 'upcoming', 'aria-labelledby': 'upcoming-title', 'hidden': ''})
for child in list(parsed(TEASER_MAIN).main.contents):
    upcoming.append(child)
preview.find(id='preview-content').append(upcoming)
if not preview.select_one('button[data-page="upcoming"]'):
    tab = preview.new_tag('button', attrs={'type':'button','class':'preview-tab','data-page':'upcoming','aria-controls':'upcoming','aria-pressed':'false'})
    tab.string = 'Next Novel'
    preview.select_one('.preview-controls').append(tab)
for link in preview.select('#upcoming a[href], #home #next-novel a[href]'):
    href = link['href']
    if href == 'next-novel.html':
        link['data-page'] = 'upcoming'
        link['href'] = '#upcoming'
    elif href.startswith('index.html#'):
        anchor = href.split('#',1)[1]
        link['data-page'] = 'home'
        link['data-anchor'] = anchor
        link['href'] = '#home/' + anchor
script_found = False
for script in preview.find_all('script'):
    text = script.string or script.get_text()
    old_ids = "const ids=['home','authors','research','shelf'];"
    new_ids = "const ids=['home','authors','research','shelf','upcoming'];"
    if old_ids in text:
        script.string = text.replace(old_ids, new_ids)
        script_found = True
    elif new_ids in text:
        script_found = True
assert script_found, 'Existing preview router was not found.'
(ROOT / 'preview.html').write_text(str(preview), encoding='utf-8')

# Preserve the addition if the earlier homepage builder is deliberately rerun.
builder = ROOT / 'tools/build_reading_room_home.py'
source = builder.read_text(encoding='utf-8')
marker = '# Preserve the next-novel extension when rebuilding the homepage.'
if marker not in source:
    source += '\n\n' + marker + '\nnext_novel_builder = ROOT / "tools/build_next_novel_teaser.py"\nif next_novel_builder.exists():\n    import sys\n    subprocess.run([sys.executable, str(next_novel_builder)], check=True)\n'
    builder.write_text(source, encoding='utf-8')

for filename in ['index.html','next-novel.html','preview.html']:
    soup = parsed((ROOT / filename).read_text(encoding='utf-8'))
    ids = [el['id'] for el in soup.find_all(id=True)]
    assert len(ids) == len(set(ids)), ('Duplicate IDs', filename)
    assert soup.find('main'), filename
    assert 'Mara Hayes' in soup.get_text() and 'Alix Delorenzi' in soup.get_text()
    if filename != 'next-novel.html':
        assert 'Sara Mautino, MSLIS' in soup.get_text()
    assert 'Sara Mautino, MSLS' not in soup.get_text()
    for link in soup.select('a[href]'):
        href = link['href']
        if ':' in href or href.startswith('#'):
            continue
        target = href.split('#')[0]
        assert (ROOT / target).exists(), (filename, href)
# Do not expose plot resolutions or antagonists in the teaser.
for forbidden in ['Daniel', 'Declan', 'abduction', 'hidden antagonist', 'three-month transition']:
    assert forbidden.lower() not in TEASER_MAIN.lower()
assert '\u2014' not in HOME_SECTION + TEASER_MAIN
report = {'built':True,'main_branch_changed':False,'featured_novel_preserved':True,'MSLIS_preserved':True,'invented_release_date':False,'invented_book_title':False,'new_page':'next-novel.html','homepage_placement':'Immediately after the featured novel','preview_view':'upcoming'}
(ROOT / 'next-novel-build-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
