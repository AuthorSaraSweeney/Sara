"""Browser checks for draft pages. No live site changes or form submissions."""
import json
import shutil
import subprocess
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]
output = root / 'preview-test-output'
output.mkdir(exist_ok=True)
server = subprocess.Popen(['python3','-m','http.server','8765','--bind','127.0.0.1'], cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
results=[]
try:
    with sync_playwright() as p:
        executable = shutil.which('google-chrome') or shutil.which('chromium') or shutil.which('chromium-browser')
        browser=p.chromium.launch(headless=True, executable_path=executable) if executable else p.chromium.launch(headless=True)
        page=browser.new_page(viewport={'width':1440,'height':1000}, device_scale_factor=1)
        errors=[]
        page.on('pageerror',lambda error: errors.append(str(error)))
        page.goto('http://127.0.0.1:8765/preview.html',wait_until='networkidle')
        page.evaluate('document.fonts.ready')
        for width in [1440,1024,900,768,720,390,360,320]:
            page.set_viewport_size({'width':width,'height':900})
            for view in ['home','authors','research','shelf']:
                page.locator('button[data-page="'+view+'"]').click()
                page.evaluate('document.fonts.ready')
                page.wait_for_timeout(70)
                dims=page.evaluate('({width:innerWidth,scroll:document.documentElement.scrollWidth,visible:[...document.querySelectorAll(".preview-page")].filter(e=>!e.hidden).map(e=>e.id)})')
                assert dims['visible']==[view], (width,view,dims)
                assert dims['scroll']<=width+1, ('Horizontal overflow',width,view,dims)
                buttons = page.locator('#'+view+' .destination-card .card-action .btn' if view=='home' else '#'+view+' .service-grid .card-action .btn' if view=='authors' else '#'+view+' .research-pricing .card-action .btn' if view=='research' else '#'+view+' .btn')
                boxes=buttons.evaluate_all('(els)=>els.map(e=>{let b=e.getBoundingClientRect();return {x:b.x,y:b.y,w:b.width,h:b.height}})')
                if view in ('home','authors') and width>720:
                    for i in range(0,len(boxes)-1,2):
                        a,b=boxes[i:i+2]
                        assert abs(a['y']-b['y'])<1.1, ('Uneven buttons',width,view,boxes)
                        assert abs(a['h']-b['h'])<1.1 and abs(a['w']-b['w'])<1.1, ('Unequal buttons',width,view,boxes)
                if view=='research' and width>900:
                    assert max(x['y'] for x in boxes)-min(x['y'] for x in boxes)<1.1, ('Research alignment',width,boxes)
                results.append({'width':width,'view':view,'overflow':dims['scroll']-width,'buttons':boxes})
                if width in [1440,390] and view=='home':
                    page.screenshot(path=str(output/('home-'+str(width)+'.png')),full_page=True)
        page.set_viewport_size({'width':1440,'height':1000})
        page.locator('button[data-page="home"]').click()
        assert page.locator('#home img').evaluate_all('(els)=>els.every(e=>e.complete&&e.naturalWidth>0)'), 'Missing original artwork'
        for destination in ['authors','research','shelf']:
            page.locator('#home .destination-card a[data-page="'+destination+'"]').click()
            assert page.locator('#'+destination).is_visible()
            page.locator('.site-header .brand').click()
            assert page.locator('#home').is_visible()
        page.locator('button[data-page="research"]').click()
        page.locator('.site-header a[data-anchor="about"]').click()
        assert page.locator('#home').is_visible() and page.locator('#about').is_visible()
        assert '#home/about' in page.url
        page.locator('button[data-page="shelf"]').click()
        page.locator('.site-header a[data-anchor="contact"]').click()
        assert '#home/contact' in page.url
        page.goto('http://127.0.0.1:8765/index.html',wait_until='domcontentloaded')
        page.locator('.site-header a[href="research-room.html"]').click()
        assert page.locator('#research-title').is_visible()
        page.locator('.site-header .brand').click()
        assert page.locator('#home-title').is_visible()
        assert not errors, errors
        browser.close()
    (output/'checks.json').write_text(json.dumps({'passed':True,'cases':results,'script_errors':errors},indent=2))
    print('PASS: 32 responsive views, aligned cards, images, preview routing, and standalone navigation.')
finally:
    server.terminate()
