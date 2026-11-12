"""Build the fuller Sunday Best story page and its draft preview.
The homepage teaser remains the owner's approved copy, unchanged.
Source for story details: the author's character and relationship notes.
The author renamed the city Glennon and approved City of Favors as the series.
No deployment, new artwork, release date, excerpt, or future pairing is added.
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
HOME_SECTION = '''
<section class="next-feature" id="next-novel" aria-labelledby="next-novel-heading">
<div class="wrap next-feature-layout">
<div class="next-feature-label"><p class="eyebrow">Next from Sara Sweeney</p><h2 class="next-book-title" id="next-novel-heading">Sunday Best</h2><p class="next-series">''' + SERIES_HTML + '''</p><p class="next-progress">''' + STATUS + '''</p></div>
<div class="next-feature-copy">''' + BODY + '''<div class="next-actions"><a class="btn" href="next-novel.html">Discover the Story</a></div></div>
</div></section>
'''

# Only the dedicated page receives these additional layout rules.
css_path = ROOT / 'next-novel.css'
marker = '/* Expanded Sunday Best story page. */'
css_base = css_path.read_text(encoding='utf-8').split(marker)[0].rstrip()
CSS = css_base + '\n\n' + marker + r'''
.next-full-story{padding-block:52px 48px}
.next-full-story .next-story-layout{grid-template-columns:245px minmax(0,1fr);gap:58px}
.next-full-story .next-story-aside h2{font-size:35px;line-height:1.15}
.next-full-story .next-synopsis p{font-size:18px;line-height:1.9}
.next-full-story .next-synopsis .next-last-line{font:italic 25px/1.6 'IM Fell English',var(--body);color:var(--rust)}
.next-full-people{padding-block:12px 48px}
.next-full-people .next-character h3{font-size:35px}
.next-full-people .next-character .eyebrow{min-height:30px}
.next-life{margin-top:28px;display:grid;grid-template-columns:.7fr 1.3fr;gap:34px;padding:29px 31px;border-block:1px solid var(--rule);background:var(--paper-deep)}
.next-life h3{font-size:30px;line-height:1.15;margin-top:8px}
.next-life>p{font-size:17px;line-height:1.85;color:var(--muted);margin:0}
.next-series-band{background:#101b1d;color:#f2e7d5;padding-block:49px;border-block:1px solid #596a66}
.next-series-layout{display:grid;grid-template-columns:.75fr 1.25fr;gap:58px;align-items:start}
.next-series-band .eyebrow{color:#b49a68}
.next-series-band h2{font:500 clamp(38px,4.5vw,55px)/1.1 var(--display);margin:15px 0 18px;color:#f2e7d5}
.next-series-band .next-series-sub{font:italic 20px/1.65 'IM Fell English',var(--body);color:#cfc5b7;max-width:300px}
.next-series-body{border-left:1px solid #596a66;padding-left:34px}
.next-series-body p{font-size:18px;line-height:1.85;color:#ddd3c5}
.next-series-body p+p{margin-top:20px}
.next-reader-section{padding-block:47px 45px}
.next-reader-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:28px}
.next-reader-item{display:grid;grid-template-rows:subgrid;grid-row:span 2;border-top:2px solid var(--moss);padding-top:20px;min-width:0}
.next-reader-item:nth-child(2){border-top-color:var(--rust)}
.next-reader-item h3{font-size:27px;line-height:1.2;padding-bottom:14px}
.next-reader-item p{font-size:16px;line-height:1.8;color:var(--muted);margin:0}
.next-reader-note{margin-top:28px;padding:18px 22px;border:1px solid var(--rule);background:var(--paper-deep);font:13px/1.8 var(--ui);color:var(--muted)}
.next-reader-note strong{color:var(--ink)}
.next-full-status{padding-bottom:58px}
@supports not (grid-template-rows:subgrid){.next-reader-item{display:flex;flex-direction:column}}
@media(max-width:1000px){.next-full-story .next-story-layout{grid-template-columns:215px minmax(0,1fr);gap:35px}.next-series-layout{gap:35px}.next-series-body{padding-left:28px}.next-reader-grid{gap:22px}}
@media(max-width:760px){.next-full-story{padding-block:35px}.next-full-story .next-story-layout{grid-template-columns:1fr;gap:25px}.next-full-story .next-story-aside h2{font-size:32px}.next-full-story .next-synopsis p{font-size:17px}.next-full-story .next-synopsis .next-last-line{font-size:23px}.next-full-people{padding-block:5px 35px}.next-life{grid-template-columns:1fr;gap:16px;padding:25px;margin-top:23px}.next-life>p{font-size:16px}.next-series-band{padding-block:35px}.next-series-layout{grid-template-columns:1fr;gap:25px}.next-series-body{border-left:0;border-top:1px solid #596a66;padding:23px 0 0}.next-series-band .next-series-sub{max-width:none}.next-series-body p{font-size:17px}.next-reader-section{padding-block:34px}.next-reader-grid{grid-template-columns:1fr;gap:25px}.next-reader-item{display:block;grid-row:auto}.next-reader-item h3{font-size:27px;padding-bottom:11px}.next-reader-note{padding:17px 19px}.next-full-status{padding-bottom:38px}}
'''

TEASER_MAIN = '''
<main id="main">
<section class="next-hero" aria-labelledby="upcoming-title"><div class="wrap"><div class="next-back-row"><a class="next-backlink" href="index.html#next-novel">Back to the Reading Room</a></div><div class="next-hero-inner"><p class="eyebrow">Next from Sara Sweeney</p><h1 id="upcoming-title" tabindex="-1">Sunday Best</h1><p class="next-subtitle">''' + SERIES_HTML + '''</p><div class="next-divider" aria-hidden="true"></div><p class="next-progress">''' + STATUS + '''</p></div></div></section>
<section class="wrap next-full-story" aria-labelledby="next-story-heading"><div class="next-story-layout">
<div class="next-story-aside"><p class="eyebrow">Inside Sunday Best</p><h2 id="next-story-heading">She already knows what it costs to start over.</h2><p>Desire comes easily.<br>Trust is another matter.</p></div>
<div class="next-synopsis">
<p>Mara Hayes spent ten years in a marriage where money, choices, and even her ambitions were subject to someone else’s approval. Two years after leaving, she has a place of her own and a food truck she runs with her best friend, Georgia. The hours are brutal and the margins are thin. But the life is one she chose.</p>
<p>Alix Delorenzi has built a successful development company and a reputation for getting things done. He also serves as underboss to his brother’s criminal organization. Money and influence have always given him options most people never have. He’s used to deciding which one to take.</p>
<p>At first, he notices the way Mara commands her kitchen. She notices how little he needs to say to make other people listen. Neither expects a single transaction to keep bringing them back into each other’s lives.</p>
<p>Then anonymous threats begin reaching Mara. Alix has money, security, and connections she doesn’t. What he lacks is the habit of asking before he uses them. For a woman who has already lived with control disguised as care, his help presents a problem of its own.</p>
<p>The attraction between them is immediate. Building a relationship Mara can choose freely, while Alix’s world closes around them, will demand more than either knows how to give.</p>
<p class="next-last-line">''' + escape(EXACT_LINE) + '''</p>
</div></div></section>
<section class="wrap next-full-people" aria-labelledby="next-people-heading"><div class="section-heading"><div><p class="eyebrow">Beyond the first impression</p><h2 id="next-people-heading">Meet Mara &amp; Alix</h2></div></div>
<div class="next-character-grid">
<article class="next-character"><p class="eyebrow">32 · Chef · Starting over</p><h3>Mara Hayes</h3><p>Sharp-tongued, observant, and warm with the people she lets close. Mara shows affection by feeding people and remembering what they like. She saves every receipt, hates financial surprises, and will work herself into the ground before admitting she needs help.</p></article>
<article class="next-character"><p class="eyebrow">35 · Developer · Underboss</p><h3>Alix Delorenzi</h3><p>Tailored suits, quiet authority, and violence kept under tight control. Alix’s niece and nephew know a patient, playful uncle. The people who do business with his family know someone very different. Both sides of him are real.</p></article>
</div>
<aside class="next-life" aria-labelledby="next-life-heading"><div><p class="eyebrow">The life worth protecting</p><h3 id="next-life-heading">Sunday Best belongs to two women.</h3></div><p>Georgia Price helped Mara turn the truck from a dream into a business. They are equal partners, with Mara running the kitchen and Georgia handling customers, schedules, and the work that keeps them moving. The danger that follows Mara reaches Georgia, too. Their friendship and the business they built remain central to the story.</p></aside>
</section>
<section class="next-series-band" aria-labelledby="next-series-heading"><div class="wrap next-series-layout">
<div><p class="eyebrow">A new interconnected series</p><h2 id="next-series-heading">City of Favors</h2><p class="next-series-sub">The families, the people they love, and the obligations between them.</p></div>
<div class="next-series-body"><p>In Glennon, the Delorenzis’ influence runs through downtown property, development, and hospitality. Along the working riverfront, the Kellehers have their own history and claim to power. As old industrial land becomes valuable again, the boundaries between them are harder to keep.</p><p><em>City of Favors</em> follows the romances woven through these families and their wider circle of friends, allies, and rivals. Some people inherit the obligations. Others become entangled with them through the people they love.</p><p><em>Sunday Best</em> begins with Mara and Alix. Future books will follow other couples into different corners of this connected world.</p></div>
</div></section>
<section class="wrap next-reader-section" aria-labelledby="next-reader-heading"><div class="section-heading"><div><p class="eyebrow">The reading experience</p><h2 id="next-reader-heading">Danger, desire, and difficult choices.</h2></div></div>
<div class="next-reader-grid">
<article class="next-reader-item"><h3>Attraction before trust</h3><p>The chemistry arrives before either of them is ready for it. Emotional trust develops through friction, vulnerability, and the choices they make when it would be easier to take control.</p></article>
<article class="next-reader-item"><h3>A heroine with a life to keep</h3><p>Mara has a home, a livelihood, and a friendship that matter before Alix enters the picture. Falling in love means finding room for him without surrendering those parts of herself.</p></article>
<article class="next-reader-item"><h3>Family ties with consequences</h3><p>Business, loyalty, and personal history reach into every relationship. The criminal intrigue puts pressure on a romance that remains at the center of the book.</p></article>
</div>
<p class="next-reader-note"><strong>For adult readers.</strong> The story includes explicit intimacy, violence, threats, and a history of financial and emotional abuse.</p>
</section>
<section class="wrap next-status next-full-status" aria-labelledby="next-status-heading"><div class="next-status-box"><div><p class="eyebrow">Sunday Best · City of Favors</p><h2 id="next-status-heading">Coming Soon | In Development</h2><p>The manuscript is in progress. The cover and release date have not been announced.</p></div><a class="btn secondary" href="index.html#featured-book">Explore the Published Novel</a></div></section>
</main>
'''

protected_files = ['authors-desk.html','research-room.html','secondhand-shelf.html','the-year-that-wasnt-hers.html','chapter-1.html','reading-room-services.css','reading-room-home.css','research-packages.css','CNAME']
protected_bytes = {name:(ROOT / name).read_bytes() for name in protected_files}
index_path = ROOT / 'index.html'
index_before = index_path.read_bytes()
home = parsed(index_before.decode('utf-8'))
existing_teaser = home.select_one('#next-novel')
if existing_teaser is None:
    # Preserve the approved teaser if the general homepage builder was rerun.
    if not home.select_one('link[href="next-novel.css"]'):
        home.head.append(home.new_tag('link', rel='stylesheet', href='next-novel.css'))
    home.select_one('#featured-book').insert_after(parsed(HOME_SECTION).section)
    index_path.write_text(str(home), encoding='utf-8')
else:
    for paragraph in PARAGRAPHS:
        assert paragraph in existing_teaser.get_text(' ',strip=True), 'Homepage copy has changed. Review before rebuilding.'
    # Do not even reserialize the approved homepage during this refinement.
    assert index_path.read_bytes() == index_before
css_path.write_text(CSS, encoding='utf-8')

head = deepcopy(home.head)
for tag in head.find_all('script'):
    tag.decompose()
for tag in head.find_all('meta', attrs={'name':'facebook-domain-verification'}):
    tag.decompose()
for tag in head.find_all('link', rel='canonical'):
    tag.decompose()
head.title.string = 'Sunday Best | City of Favors | Sara Sweeney'
head.find('meta',attrs={'name':'description'})['content'] = 'Discover Sunday Best by Sara Sweeney: meet Mara Hayes and Alix Delorenzi and explore City of Favors, a new dark mafia romance series.'
if not head.find('meta',attrs={'name':'robots'}):
    head.append(home.new_tag('meta',attrs={'name':'robots','content':'noindex,nofollow'}))
page = '<!doctype html><html lang="en">' + str(head) + '<body><a class="skip" href="#main">Skip to content</a>' + str(home.select_one('header.site-header')) + TEASER_MAIN + str(home.select_one('footer.site-footer')) + '</body></html>'
(ROOT / 'next-novel.html').write_text(page,encoding='utf-8')

preview = parsed((ROOT / 'preview.html').read_text(encoding='utf-8'))
protected_preview = {key:str(preview.find(id=key)) for key in ['home','authors','research','shelf']}
style = preview.new_tag('style',id='next-novel-preview-css')
style.string = CSS
old_style = preview.find(id='next-novel-preview-css')
if old_style:
    old_style.replace_with(style)
else:
    preview.head.append(style)
if not preview.select_one('#home #next-novel'):
    preview.select_one('#home #featured-book').insert_after(parsed(HOME_SECTION).section)
    for link in preview.select('#home #next-novel a[href]'):
        link['data-page']='upcoming'
        link['href']='#upcoming'
    protected_preview['home']=str(preview.find(id='home'))
for el in preview.select('#upcoming'):
    el.decompose()
upcoming = preview.new_tag('section',attrs={'class':'preview-page','id':'upcoming','aria-labelledby':'upcoming-title','hidden':''})
for child in list(parsed(TEASER_MAIN).main.contents):
    upcoming.append(child)
preview.find(id='preview-content').append(upcoming)
tab = preview.select_one('button[data-page="upcoming"]')
assert tab is not None, 'Sunday Best preview tab missing'
tab.string = TITLE
for link in preview.select('#upcoming a[href]'):
    href=link['href']
    if href.startswith('index.html#'):
        anchor=href.split('#',1)[1]
        link['data-page']='home'
        link['data-anchor']=anchor
        link['href']='#home/'+anchor
assert any("const ids=['home','authors','research','shelf','upcoming'];" in script.get_text() for script in preview.find_all('script')), 'Preview router missing'
for key,before in protected_preview.items():
    assert str(preview.find(id=key)) == before, ('Other preview page changed',key)
(ROOT / 'preview.html').write_text(str(preview),encoding='utf-8')

# The homepage stays short. The story page must provide genuinely new information.
for filename,selector in [('index.html','#next-novel'),('preview.html','#home #next-novel')]:
    text=parsed((ROOT / filename).read_text()).select_one(selector).get_text(' ',strip=True)
    for paragraph in PARAGRAPHS:
        assert paragraph in text,(filename,paragraph)
    assert text.count(EXACT_LINE)==1
for filename,selector in [('next-novel.html','main'),('preview.html','#upcoming')]:
    region=parsed((ROOT / filename).read_text()).select_one(selector)
    text=region.get_text(' ',strip=True)
    assert len(text.split()) > 550, ('Insufficient additional detail',filename)
    assert text.count(EXACT_LINE)==1
    for paragraph in PARAGRAPHS:
        assert paragraph not in text, ('Copied homepage paragraph',filename)
    for required in ['Georgia Price','equal partners','underboss','Kellehers','Glennon','City of Favors','dark mafia romance','explicit intimacy']:
        assert required in text,(filename,required)
    for forbidden in ['catering job','Her trust','isn’t for sale','Brightwater','set in Glennon','Daniel','abduction','staged fire','three-month transition']:
        assert forbidden not in text,(filename,forbidden)
for filename in ['index.html','next-novel.html','preview.html']:
    soup=parsed((ROOT / filename).read_text(encoding='utf-8'))
    ids=[el['id'] for el in soup.find_all(id=True)]
    assert len(ids)==len(set(ids)),('Duplicate IDs',filename)
    for link in soup.select('a[href]'):
        href=link['href']
        if ':' in href or href.startswith('#'):
            continue
        assert (ROOT / href.split('#')[0]).is_file(),(filename,href)
for name,data in protected_bytes.items():
    assert (ROOT / name).read_bytes()==data,('Protected file changed',name)
assert '\u2014' not in TEASER_MAIN
report={'built':True,'main_branch_changed':False,'book_title':TITLE,'series':SERIES,'homepage_bytes_unchanged':index_path.read_bytes()==index_before,'other_preview_views_unchanged':True,'exact_closing_line':EXACT_LINE,'detail_page_words':len(parsed(TEASER_MAIN).get_text(' ',strip=True).split()),'homepage_synopsis_not_duplicated':True,'protected_files_unchanged':protected_files,'artwork_changed':False,'palette':'Night Truck','new_page':'next-novel.html','preview_view':'upcoming'}
(ROOT / 'next-novel-build-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
