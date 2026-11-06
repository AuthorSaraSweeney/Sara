"""Build the approved Reading Room Press front door and self-contained preview.
Runs only on the development branch in CI. Does not deploy GitHub Pages.
Requires beautifulsoup4 and Pillow. Original artwork remains in Git history.
"""
from pathlib import Path
import base64
import hashlib
import io
import json
import os
import re
import subprocess
from html import escape
from urllib.parse import urlsplit
from bs4 import BeautifulSoup
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
BRANCH = 'reading-room-press-expansion'
if os.environ.get('GITHUB_ACTIONS') == 'true' and os.environ.get('GITHUB_REF_NAME') != BRANCH:
    raise SystemExit('This builder is restricted to the development branch.')
BASELINE = 'e01e8ad6276698e3db795990d0344f9e80f06637'
original = subprocess.check_output(['git', 'show', BASELINE + ':index.html']).decode('utf-8')
old = BeautifulSoup(original, 'html.parser')
assets = ROOT / 'assets'
assets.mkdir(exist_ok=True)
manifest = {'original_commit': BASELINE, 'assets': {}, 'service_content_preserved': {}}

def artwork(selector, name, max_size):
    image = old.select_one(selector)
    if image is None:
        raise RuntimeError('Original artwork not found: ' + selector)
    src = image.get('src', '')
    if not src.startswith('data:image/'):
        raise RuntimeError('Expected embedded original artwork for ' + name)
    payload = base64.b64decode(src.split(',', 1)[1])
    with Image.open(io.BytesIO(payload)) as im:
        im = im.convert('RGB')
        im.thumbnail(max_size, Image.Resampling.LANCZOS)
        output = assets / (name + '.webp')
        im.save(output, 'WEBP', quality=90, method=6)
        manifest['assets'][name] = {'source_sha256': hashlib.sha256(payload).hexdigest(), 'width': im.width, 'height': im.height, 'bytes': output.stat().st_size}
    return 'assets/' + output.name

cover = artwork('#books img', 'year-that-wasnt-hers-cover', (900, 1350))
portrait = artwork('#author img', 'sara-portrait', (900, 1200))
book_description = old.select_one('#books .bdesc')
if book_description is None:
    raise RuntimeError('Cannot locate the original novel description.')
book_copy = escape(book_description.get_text(' ', strip=True))
# Only the original book description is reused. Stale preorder/date panels are not copied.

fonts = 'https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=IM+Fell+English:ital@0;1&family=Cinzel+Decorative:wght@400;700&family=Sorts+Mill+Goudy:ital@0;1&family=Lato:wght@400;700&display=swap'
mark = '<svg viewBox="0 0 36 40" fill="none" aria-hidden="true"><path d="M18 34V12m0 16C7 28 5 20 5 17c9 0 13 5 13 11Zm0-8c11 0 13-8 13-11-9 0-13 5-13 11ZM4 35c5-3 10-3 14 0 4-3 9-3 14 0v-5" stroke="currentColor" stroke-width="1.2"/><path d="M18 13c-6-4-5-9-2-12 5 3 7 8 2 12Z" stroke="currentColor" stroke-width="1.2"/></svg>'
sprig = '<svg viewBox="0 0 100 180" fill="none" aria-hidden="true"><g stroke="currentColor" stroke-width="1.2"><path d="M46 168C45 135 62 107 51 73C46 58 49 35 61 14"/><path d="M47 145C22 142 18 126 17 115C37 117 46 129 47 145ZM53 123C76 121 85 105 87 94C66 97 56 109 53 123ZM55 99C31 96 26 80 27 70C45 74 53 85 55 99ZM51 78C74 75 82 59 82 49C63 54 53 65 51 78ZM51 55C34 49 32 35 34 26C48 32 52 42 51 55ZM57 30C74 25 79 12 77 5C64 10 59 19 57 30Z"/></g></svg>'
nav_items = [('Books', 'index.html#featured-book'), ('Author Services', 'authors-desk.html'), ('Research', 'research-room.html'), ('Secondhand Books', 'secondhand-shelf.html'), ('About', 'index.html#about'), ('Contact', 'index.html#contact')]

def header(current=''):
    links = ''.join('<a href="' + href + '"' + (' aria-current="page"' if href == current else '') + '>' + text + '</a>' for text, href in nav_items)
    return '<header class="site-header"><div class="wrap masthead"><a class="brand" href="index.html">' + mark + '<span>Reading Room Press</span></a><nav class="site-nav" aria-label="Main navigation">' + links + '</nav></div></header>'

def footer():
    links = ''.join('<a href="' + href + '">' + text + '</a>' for text, href in nav_items)
    return '<footer class="site-footer"><div class="wrap footer-inner"><div><a class="footer-title" href="index.html">Reading Room Press</a><p class="footer-caption">Independent stories. Thoughtful research. Books worth sharing.</p></div><p class="footer-contact"><a href="mailto:hello@readingroompress.com">hello@readingroompress.com</a></p></div><nav class="wrap footer-nav" aria-label="Footer navigation">' + links + '</nav></footer>'

home_main = '''
<main id="main">
<section class="home-hero" aria-labelledby="home-title">
<div class="home-border" aria-hidden="true"></div>
<div class="wrap home-hero-inner"><div class="home-sprig left">SPRIG</div><div class="home-sprig right">SPRIG</div>
<p class="eyebrow">An independent press &amp; literary services studio</p>
<h1 id="home-title" tabindex="-1">Reading Room <span>Press</span></h1>
<p class="home-tagline">Independent stories. Thoughtful research.<br>Books worth sharing.</p>
<div class="home-flourish" aria-hidden="true"><span></span><svg viewBox="0 0 40 20" fill="none"><path d="M2 10h36M20 3l7 7-7 7-7-7Z" stroke="currentColor"/></svg><span></span></div>
<p class="home-intro">An independent publishing imprint and literary services studio for writers and readers. Discover original fiction, find practical publishing support, get help with your research, or explore our growing collection of secondhand books.</p>
<div class="home-actions"><a class="btn" href="#featured-book">Explore Our Books</a><a class="btn secondary" href="#find-your-place">Find Help for Your Book</a></div>
</div></section>
<section class="section wrap home-destinations" id="find-your-place" aria-labelledby="destinations-title">
<div class="section-heading"><div><p class="eyebrow">For writers. For readers. For the curious.</p><h2 id="destinations-title">Find your place in the Reading Room</h2></div></div>
<div class="destination-grid">
<article class="destination-card"><div class="card-top"><p class="eyebrow">From the press</p><span class="number" aria-hidden="true">01</span></div><h3>Our Books</h3><p class="destination-description">Original fiction from Reading Room Press, including <em>The Year That Wasn’t Hers</em> by Sara Sweeney.</p><p class="destination-note">Stories with a life of their own.</p><div class="card-action"><a class="btn" href="#featured-book">Explore Our Books</a></div></article>
<article class="destination-card"><div class="card-top"><p class="eyebrow">Publishing support</p><span class="number" aria-hidden="true">02</span></div><h3>The Author’s Desk</h3><p class="destination-description">Practical help with book descriptions, publishing preparation, and the steps between a finished manuscript and publication.</p><p class="destination-note">Services from $99.</p><div class="card-action"><a class="btn" href="authors-desk.html">Explore Author Services</a></div></article>
<article class="destination-card"><div class="card-top"><p class="eyebrow">Professional research</p><span class="number" aria-hidden="true">03</span></div><h3>The Research Room</h3><p class="destination-description">Source discovery, scene-detail checks, and research support from <strong>Sara Mautino, MSLIS</strong>.</p><p class="destination-note">Research Assist starts at $50.</p><div class="card-action"><a class="btn" href="research-room.html">Explore Research Services</a></div></article>
<article class="destination-card"><div class="card-top"><p class="eyebrow">Curated secondhand books</p><span class="number" aria-hidden="true">04</span></div><h3>The Secondhand Shelf</h3><p class="destination-description">Mystery series, crime fiction, and true-crime nonfiction, carefully gathered for their next reader.</p><p class="destination-note">First listings coming soon.</p><div class="card-action"><a class="btn" href="secondhand-shelf.html">Visit the Secondhand Shelf</a></div></article>
</div></section>
<section class="home-book-band" id="featured-book" aria-labelledby="featured-book-title"><div class="wrap home-book-layout">
<div class="home-cover-frame"><a href="the-year-that-wasnt-hers.html" aria-label="Explore The Year That Wasn’t Hers"><img class="home-cover" src="COVER" alt="Cover of The Year That Wasn’t Hers by Sara Sweeney" width="600" height="900" loading="lazy"></a><p class="book-caption">From Reading Room Press</p></div>
<div class="home-book-copy"><p class="eyebrow">The featured novel</p><h2 id="featured-book-title">The Year That<br><em>Wasn’t Hers</em></h2><p class="home-byline">By Sara Sweeney</p><p class="home-book-description">BOOKCOPY</p><p class="home-publication">Published June 17, 2026 · Available now</p><div class="home-actions"><a class="btn" href="the-year-that-wasnt-hers.html">Explore the Book</a><a class="btn outline" href="chapter-1.html">Read the First Chapter</a></div></div>
</div></section>
<section class="section wrap home-about" id="about" aria-labelledby="about-title"><div class="home-about-layout">
<div class="home-portrait-frame"><img src="PORTRAIT" alt="Sara Mautino, who writes fiction as Sara Sweeney" width="600" height="800" loading="lazy"><p>Sara Mautino, MSLIS <span>Writing fiction as Sara Sweeney</span></p></div>
<div><p class="eyebrow">Meet the person behind the press</p><h2 id="about-title">A librarian’s eye.<br><em>An author’s understanding.</em></h2><p>Reading Room Press brings together the work of <strong>Sara Mautino, MSLIS</strong>, an academic librarian with nearly 20 years of research experience, and the fiction she publishes as <strong>Sara Sweeney</strong>.</p><p>Through her research and author services, Sara helps writers find reliable information and navigate the practical details of independent publishing. As an author herself, she understands the care, uncertainty, and expense involved in bringing a book into the world.</p><div class="home-about-note"><p class="eyebrow">A small press with room for more</p><p>Original fiction, practical support for fellow writers, and well-loved books finding new readers. Each has a place at Reading Room Press.</p><p class="fine">Author and research services are independent professional services, separate from publication under the imprint.</p></div></div>
</div></section>
<section class="home-contact" id="contact" aria-labelledby="contact-title"><div class="wrap home-contact-inner"><p class="eyebrow">You’re welcome here</p><h2 id="contact-title">What brings you to the Reading Room?</h2><p>A book you’d like to read, a detail you need to research, or a project you’re ready to share. Tell me what you have in mind.</p><a class="btn secondary" href="mailto:hello@readingroompress.com?subject=Reading%20Room%20Press%20Inquiry">Get in Touch</a><p class="home-email"><a href="mailto:hello@readingroompress.com">hello@readingroompress.com</a></p></div></section>
</main>
'''.replace('SPRIG', sprig).replace('COVER', cover).replace('PORTRAIT', portrait).replace('BOOKCOPY', book_copy)

home_css = '''
/* Homepage and shared navigation. Keep approved service cards unchanged. */
.footer-title{text-decoration:none}.footer-nav{display:flex;justify-content:center;flex-wrap:wrap;gap:10px 25px;padding-top:23px;margin-top:24px;border-top:1px solid var(--rule)}.footer-nav a{font:12px/1.8 var(--ui);color:var(--moss)}
.home-hero{position:relative;isolation:isolate;overflow:hidden;background:radial-gradient(ellipse at 10% 70%,rgba(61,92,62,.09),transparent 55%),radial-gradient(ellipse at 85% 15%,rgba(139,58,34,.06),transparent 50%),linear-gradient(180deg,var(--paper-deep),var(--paper));border-bottom:1px solid var(--rule)}.home-border{position:absolute;inset:19px;border:1px solid rgba(139,58,34,.18);pointer-events:none}.home-hero-inner{position:relative;text-align:center;padding:63px 100px 66px}.home-hero h1{font:400 clamp(44px,5.8vw,76px)/1.12 var(--ornamental);letter-spacing:.02em;color:var(--ink);margin:24px 0}.home-hero h1 span{display:block;color:var(--rust);font-size:.66em;letter-spacing:.28em;padding-left:.28em;margin-top:10px}.home-tagline{font:italic 26px/1.55 'IM Fell English',var(--body);color:var(--rust)}.home-intro{max-width:680px;margin:22px auto 0;font-size:17px;line-height:1.85;color:var(--muted)}.home-flourish{display:flex;justify-content:center;align-items:center;gap:15px;margin:23px auto}.home-flourish span{width:80px;height:1px;background:var(--rule)}.home-flourish svg{width:36px;height:18px;color:var(--rust)}.home-sprig{position:absolute;top:115px;width:110px;color:var(--moss);opacity:.52;z-index:-1}.home-sprig.left{left:0;transform:rotate(-12deg)}.home-sprig.right{right:0;transform:scaleX(-1) rotate(-12deg)}.home-actions{display:flex;flex-wrap:wrap;gap:14px;margin-top:28px}.home-hero .home-actions{justify-content:center}.home-actions .btn{width:250px;min-height:52px}.btn.outline{color:var(--rust);background:transparent}.btn.outline:hover{background:var(--rust);color:var(--card)}
.home-destinations{padding-top:55px}.home-destinations .section-heading{max-width:none}.destination-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:26px}.destination-card{display:grid;grid-template-rows:subgrid;grid-row:span 5;row-gap:0;position:relative;background:var(--card);border:1px solid var(--rule);padding:29px 32px}.destination-card::before,.destination-card::after{content:'';position:absolute;width:25px;height:25px;border-style:solid;border-color:var(--rust);pointer-events:none}.destination-card::before{top:-1px;left:-1px;border-width:2px 0 0 2px}.destination-card::after{bottom:-1px;right:-1px;border-width:0 2px 2px 0}.destination-card h3{font-size:37px;padding-bottom:17px}.destination-description{font-size:17px;line-height:1.8;padding-bottom:20px}.destination-note{font:13px/1.7 var(--ui);color:var(--moss);padding-bottom:22px;margin:0}.destination-card .card-action{align-self:end}.destination-card .btn{width:280px;min-height:51px;font-size:13px;gap:14px}
.home-book-band{background:var(--paper-deep);border-block:1px solid var(--rule);padding:64px 0}.home-book-layout{display:grid;grid-template-columns:310px 1fr;gap:76px;align-items:center}.home-cover-frame{position:relative;padding:24px 23px 0}.home-cover-frame::before{content:'';position:absolute;inset:8px 0 58px;border:1px solid var(--rule);pointer-events:none}.home-cover{display:block;width:100%;height:auto;box-shadow:9px 12px 25px rgba(41,25,12,.22);position:relative}.book-caption{text-align:center;font:10px/1.7 var(--ornamental);letter-spacing:.12em;color:var(--moss);padding-top:25px}.home-book-copy h2{font-size:clamp(40px,4.5vw,62px);margin:15px 0 13px}.home-book-copy h2 em{color:var(--rust)}.home-byline{font:12px/1.8 var(--ui);letter-spacing:.15em;text-transform:uppercase;color:var(--moss)}.home-book-description{font-size:18px;line-height:1.85;margin-top:25px;border-left:2px solid var(--rule);padding-left:24px}.home-publication{font:12px/1.7 var(--ui);color:var(--muted);margin-top:23px}.home-book-copy .home-actions .btn{width:235px;font-size:13px}
.home-about{padding-block:70px}.home-about-layout{display:grid;grid-template-columns:280px 1fr;gap:70px;align-items:start}.home-portrait-frame{padding:12px;border:1px solid var(--rule);background:var(--paper-deep);position:relative}.home-portrait-frame img{display:block;width:100%;height:auto;aspect-ratio:3/4;object-fit:cover;object-position:center 30%}.home-portrait-frame p{padding:17px 6px 5px;font:14px/1.8 var(--ui);color:var(--rust);text-align:center}.home-portrait-frame p span{display:block;font:italic 15px/1.7 var(--body);color:var(--moss)}.home-about h2{font-size:45px;margin:13px 0 24px}.home-about h2 em{color:var(--rust)}.home-about-layout>div>p:not(.eyebrow){font-size:17px;line-height:1.9;color:var(--muted)}.home-about-note{margin-top:27px;padding-top:24px;border-top:1px solid var(--rule)}.home-about-note p{font-size:16px}.home-about-note .eyebrow{font-size:11px}.home-about-note .fine{font-size:12px;margin-top:15px}
.home-contact{background:var(--paper-deep);border-top:1px solid var(--rule);padding:53px 0}.home-contact-inner{text-align:center;max-width:760px}.home-contact h2{font-size:43px;margin:15px 0 21px}.home-contact-inner>p:not(.eyebrow){font-size:17px;color:var(--muted)}.home-contact .btn{margin-top:25px;width:240px}.home-email a{font:13px/1.7 var(--ui)}#featured-book,#about,#contact,#find-your-place{scroll-margin-top:115px}
@supports not (grid-template-rows:subgrid){.destination-card{display:flex;flex-direction:column}.destination-card .card-action{margin-top:auto;align-self:stretch}}
@media(max-width:1050px){.home-book-layout{grid-template-columns:260px 1fr;gap:45px}.home-about-layout{grid-template-columns:250px 1fr;gap:45px}.home-hero-inner{padding-inline:85px}.destination-card h3{font-size:33px}}
@media(max-width:720px){.home-border{inset:10px}.home-hero-inner{padding:40px 16px 44px}.home-hero .eyebrow{font-size:9px;letter-spacing:.1em}.home-hero h1{font-size:clamp(35px,8vw,48px);margin:22px 0}.home-tagline{font-size:22px}.home-intro{font-size:16px}.home-sprig{width:65px;top:115px;opacity:.14}.home-actions{gap:12px;justify-content:center}.home-actions .btn{width:100%;max-width:340px}.home-destinations{padding-top:35px}.home-destinations .section-heading h2{font-size:35px}.destination-grid{grid-template-columns:1fr;gap:24px}.destination-card{display:flex;flex-direction:column;grid-row:auto;padding:26px}.destination-card h3{font-size:33px}.destination-card .btn{width:100%;max-width:none;font-size:13px}.destination-card .card-action{align-self:stretch;margin-top:auto}.home-book-band{padding-block:40px}.home-book-layout{grid-template-columns:1fr;gap:38px}.home-cover-frame{width:min(285px,100%);margin:auto}.home-book-copy h2{font-size:43px}.home-book-copy .home-actions .btn{width:100%;max-width:340px}.home-book-description{font-size:17px;padding-left:18px}.home-about{padding-block:45px}.home-about-layout{grid-template-columns:1fr;gap:34px}.home-portrait-frame{width:min(285px,100%);margin:auto}.home-about h2{font-size:38px}.home-contact{padding-block:40px}.home-contact h2{font-size:37px}.footer-nav{gap:10px 19px}.preview-controls{gap:6px}}
'''
(ROOT / 'reading-room-home.css').write_text(home_css, encoding='utf-8')
verification = old.find('meta', attrs={'name': 'facebook-domain-verification'})
verification_html = str(verification) if verification else ''
analytics = ''.join(str(x) for x in old.find_all('script') if 'G-QNXLFXXK0C' in str(x))
head = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Reading Room Press: original fiction, author services, research by Sara Mautino, MSLIS, and curated secondhand books."><title>Reading Room Press | Books, Research &amp; Author Services</title><link rel="canonical" href="https://readingroompress.com/"><link rel="icon" href="favicon.png"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="' + escape(fonts, quote=True) + '" rel="stylesheet"><link rel="stylesheet" href="reading-room-services.css"><link rel="stylesheet" href="reading-room-home.css">' + verification_html + analytics + '</head><body><a class="skip" href="#main">Skip to content</a>'
(ROOT / 'index.html').write_text(head + header() + home_main + footer() + '</body></html>', encoding='utf-8')

page_paths = {'authors': 'authors-desk.html', 'research': 'research-room.html', 'shelf': 'secondhand-shelf.html'}
page_mains = {}
for key, filename in page_paths.items():
    doc = BeautifulSoup((ROOT / filename).read_text(encoding='utf-8'), 'html.parser')
    before = doc.main.decode_contents()
    doc.select_one('header.site-header').replace_with(BeautifulSoup(header(filename), 'html.parser'))
    doc.select_one('footer.site-footer').replace_with(BeautifulSoup(footer(), 'html.parser'))
    if not doc.select_one('link[href="reading-room-home.css"]'):
        link = doc.new_tag('link', rel='stylesheet', href='reading-room-home.css')
        doc.head.append(link)
    after = doc.main.decode_contents()
    assert before == after, 'Approved service content changed: ' + filename
    manifest['service_content_preserved'][filename] = True
    (ROOT / filename).write_text(str(doc), encoding='utf-8')
    page_mains[key] = after

# Standalone preview contains all four views, styles, and the actual existing artwork.
preview_css = '\n'.join((ROOT / p).read_text(encoding='utf-8') for p in ['reading-room-services.css', 'research-packages.css', 'reading-room-home.css'])
preview_head = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Reading Room Press | Complete Site Preview</title><link href="' + escape(fonts, quote=True) + '" rel="stylesheet"><style>' + preview_css + '</style></head><body><a class="skip" href="#preview-content">Skip to content</a>'
labels = {'home':'Homepage', 'authors':'Author Services', 'research':'Research', 'shelf':'Secondhand Books'}
controls = '<div class="preview-bar"><div class="wrap preview-inner"><p class="preview-label">Reading Room Press · Design preview<small>Draft only. The live website is unchanged.</small></p><nav class="preview-controls" aria-label="Choose a preview page">' + ''.join('<button type="button" class="preview-tab" data-page="' + k + '" aria-controls="' + k + '" aria-pressed="' + str(k == 'home').lower() + '">' + v + '</button>' for k,v in labels.items()) + '</nav></div></div>'
page_mains = {'home': BeautifulSoup(home_main, 'html.parser').main.decode_contents(), **page_mains}
sections = ''.join('<section class="preview-page" id="' + k + '" aria-labelledby="' + {'home':'home','authors':'authors','research':'research','shelf':'shelf'}[k] + '-title"' + ('' if k == 'home' else ' hidden') + '>' + text + '</section>' for k,text in page_mains.items())
preview = BeautifulSoup(preview_head + controls + header() + '<main id="preview-content">' + sections + '</main>' + footer() + '</body></html>', 'html.parser')
for img in preview.find_all('img'):
    src = img.get('src', '')
    if src.startswith('assets/'):
        img['src'] = 'data:image/webp;base64,' + base64.b64encode((ROOT / src).read_bytes()).decode()
map_pages = {'index.html':'home', **{v:k for k,v in page_paths.items()}}
for link in preview.find_all('a', href=True):
    href = link['href']
    parsed = urlsplit(href)
    if parsed.scheme in ('mailto','tel','https','http'):
        continue
    if href == '#preview-content':
        continue
    file = parsed.path or 'index.html'
    if file in map_pages:
        key = map_pages[file]
        anchor = parsed.fragment
        link['data-page'] = key
        if anchor:
            link['data-anchor'] = anchor
        link['href'] = '#' + key + ('/' + anchor if anchor else '')
    elif parsed.path in ('the-year-that-wasnt-hers.html','chapter-1.html'):
        link['href'] = 'https://readingroompress.com/' + parsed.path
        link['target'] = '_blank'
        link['rel'] = 'noopener'
script = preview.new_tag('script')
script.string = '''
(function(){
 const ids=['home','authors','research','shelf'];
 function show(page,anchor,move){
  if(!ids.includes(page))page='home';
  document.querySelectorAll('.preview-page').forEach(el=>{el.hidden=el.id!==page;});
  document.querySelectorAll('[data-page]').forEach(el=>{
   const selected=el.dataset.page===page&&!el.dataset.anchor;
   if(el.tagName==='BUTTON')el.setAttribute('aria-pressed',String(selected));
   else if(selected)el.setAttribute('aria-current','page');else el.removeAttribute('aria-current');
  });
  const title=document.getElementById((page==='shelf'?'shelf':page)+'-title');
  document.title=title.textContent+' | Reading Room Press preview';
  if(move){try{history.replaceState(null,'','#'+page+(anchor?'/'+anchor:''));}catch(e){}}
  const target=anchor&&document.getElementById(anchor);
  if(target&&!target.closest('[hidden]'))target.scrollIntoView({block:'start'});
  else if(move){window.scrollTo(0,0);title.focus({preventScroll:true});}
 }
 document.addEventListener('click',e=>{const el=e.target.closest('[data-page]');if(!el)return;e.preventDefault();show(el.dataset.page,el.dataset.anchor||'',true);});
 function route(){const parts=location.hash.slice(1).split('/');show(parts[0],parts[1]||'',false);}
 window.addEventListener('hashchange',route);route();
})();
'''
preview.body.append(script)
(ROOT / 'preview.html').write_text(str(preview), encoding='utf-8')

# Static checks cover internal links, unique IDs, credentials, pricing, and assets.
for filename in ['index.html', *page_paths.values(), 'preview.html']:
    soup = BeautifulSoup((ROOT / filename).read_text(encoding='utf-8'), 'html.parser')
    ids = [el['id'] for el in soup.find_all(id=True)]
    assert len(ids) == len(set(ids)), 'Duplicate IDs in ' + filename
    for el in soup.select('a[href],link[href],img[src]'):
        path = el.get('href', el.get('src', ''))
        url = urlsplit(path)
        if url.scheme or url.netloc:
            continue
        if url.path:
            assert (ROOT / url.path).is_file(), (filename, 'Missing file', path)
        if url.fragment and filename != 'preview.html':
            target = soup if not url.path else BeautifulSoup((ROOT / url.path).read_text(encoding='utf-8'), 'html.parser')
            assert target.find(id=url.fragment), (filename, 'Missing anchor', path)
assert 'Sara Mautino, MSLIS' in (ROOT / 'research-room.html').read_text()
assert 'Research Assist' in (ROOT / 'research-room.html').read_text()
assert 'true-crime nonfiction' in home_main
assert 'June 17, 2026' in home_main
(ROOT / 'home-build-report.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps(manifest, indent=2))
