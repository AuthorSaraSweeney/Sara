"""Check artwork decoding, all preview pages, navigation and approved copy."""
from pathlib import Path
import json, shutil, subprocess
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'night-sketch-review';out.mkdir(exist_ok=True)
server=subprocess.Popen(['python3','-m','http.server','8765','--bind','127.0.0.1'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
checks=[]
try:
 with sync_playwright() as p:
  exe=shutil.which('google-chrome') or shutil.which('chromium')
  browser=p.chromium.launch(headless=True,executable_path=exe) if exe else p.chromium.launch(headless=True)
  page=browser.new_page(viewport={'width':1440,'height':1000})
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto('http://127.0.0.1:8765/preview.html#upcoming',wait_until='networkidle')
  page.evaluate('document.fonts.ready')
  for width in [1440,1280,1024,900,768,720,390,320]:
   page.set_viewport_size({'width':width,'height':1000})
   for view in ['home','upcoming','authors','research','shelf']:
    page.locator('button[data-page="'+view+'"]').click()
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(width,view)
    assert page.locator('#'+view).is_visible()
    if view in ['home','upcoming']:
     selector='#home #next-novel' if view=='home' else '#upcoming .next-hero'
     dimension=page.locator(selector).evaluate('''async el=>{let bg=getComputedStyle(el).backgroundImage;let match=bg.match(/url\("?(data:[^")]+)"?\)/);if(!match)throw Error('Missing artwork');let im=new Image();im.src=match[1];await im.decode();return [im.naturalWidth,im.naturalHeight];}''')
     assert dimension==[1200,675],dimension
     if width in [1440,390]:
      page.locator('.preview-bar').evaluate("e=>e.style.visibility='hidden'")
      page.locator(selector).screenshot(path=str(out/(view+'-'+str(width)+'.png')))
      page.locator('.preview-bar').evaluate("e=>e.style.visibility=''")
    checks.append({'width':width,'view':view,'passed':True})
  text=page.locator('#upcoming').inner_text() if page.locator('#upcoming').is_visible() else page.locator('#upcoming').text_content()
  assert 'Alix’s twin nieces' in text
  assert 'For adult readers.' in text
  assert 'Georgia’s livelihood is on the line, too.' in text
  assert 'Mara learns that accepting his protection may be just as risky as refusing it.' in text
  assert 'Their friendship and the business they built remain central to the story.' not in text
  assert 'The reading experience' not in text
  page.set_viewport_size({'width':1440,'height':1000})
  page.locator('button[data-page="home"]').click()
  page.locator('#home #next-novel a').click()
  assert page.locator('#upcoming').is_visible()
  page.locator('#upcoming .next-backlink').click()
  assert '#home/next-novel' in page.url
  page.goto('http://127.0.0.1:8765/next-novel.html',wait_until='networkidle')
  assert 'sunday-best-night-sketch.webp' in page.locator('.next-hero').evaluate('e=>getComputedStyle(e).backgroundImage')
  await_result=page.evaluate("async()=>{let im=new Image();im.src='assets/sunday-best-night-sketch.webp';await im.decode();return im.naturalWidth}")
  assert await_result==1200
  assert not errors,errors
  browser.close()
 report={'passed':True,'responsive_views':checks,'image_decoded_in_preview_and_page':True,'approved_copy_preserved':True,'browser_errors':errors}
 (out/'checks.json').write_text(json.dumps(report,indent=2)+'\n')
 print('PASS: 40 responsive views, approved artwork decoded, copy and navigation preserved.')
finally:server.terminate()
