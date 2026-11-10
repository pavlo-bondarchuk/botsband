from pathlib import Path
import json,threading,http.server,socketserver
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'reports'
REPORT.mkdir(exist_ok=True)
class Server(socketserver.TCPServer):
    allow_reuse_address=True
def serve():
    import os
    os.chdir(ROOT)
    with Server(('127.0.0.1',8765),http.server.SimpleHTTPRequestHandler) as httpd:
        httpd.serve_forever()
threading.Thread(target=serve,daemon=True).start()
results=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
    for device,width,height in [('desktop',1440,900),('mobile',390,844)]:
        context=browser.new_context(viewport={'width':width,'height':height},device_scale_factor=1,is_mobile=device=='mobile',has_touch=device=='mobile')
        for label,url in [('original','https://botsband.online/'),('static','http://127.0.0.1:8765/')]:
            page=context.new_page()
            errors=[]
            page.on('pageerror',lambda error:errors.append(str(error)))
            try:
                response=page.goto(url,wait_until='domcontentloaded',timeout=45000)
                page.wait_for_timeout(1800)
                page.screenshot(path=str(REPORT/f'{device}-{label}.png'),full_page=True,animations='disabled',timeout=30000)
                result={'device':device,'version':label,'status':response.status if response else None,'title':page.title(),'scroll_width':page.evaluate('document.documentElement.scrollWidth'),'viewport_width':width,'images':page.locator('img').count(),'broken_images':page.evaluate('Array.from(document.images).filter(i=>!i.complete || i.naturalWidth===0).map(i=>i.src)'),'js_errors':errors}
                if label=='static' and device=='mobile':
                    button=page.locator('.menu-toggle')
                    button.click()
                    result['mobile_menu_opens']=page.locator('.nav').evaluate('(e)=>getComputedStyle(e).display')!='none'
                if label=='static' and device=='desktop':
                    page.locator('.js-open-modal').first.click()
                    result['modal_opens']=page.locator('#consultation-modal').evaluate('(e)=>e.open')
                results.append(result)
            except Exception as exc:
                results.append({'device':device,'version':label,'error':str(exc)[:500]})
            page.close()
        context.close()
    browser.close()
(REPORT/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
print(json.dumps(results,ensure_ascii=False,indent=2))
