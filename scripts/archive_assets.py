from __future__ import annotations
import json,re,hashlib,mimetypes
from pathlib import Path
from urllib.parse import urljoin,urlparse,unquote
import requests
from bs4 import BeautifulSoup

BASE='https://botsband.online/'
ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/'index.html'
session=requests.Session()
session.headers.update({'User-Agent':'Mozilla/5.0 (compatible; BotsBandStaticArchiver/1.0)'})
mapping={}
failures=[]
inventory={'images':[],'stylesheets':[],'scripts':[],'fonts':[]}
allowed={'botsband.online','www.botsband.online'}
resource_exts={'.png','.jpg','.jpeg','.webp','.avif','.gif','.svg','.ico','.woff','.woff2','.ttf','.otf','.mp4','.webm','.css','.js'}

def get(url):
    response=session.get(url,timeout=35)
    response.raise_for_status()
    return response

def save(url,kind):
    absolute=urljoin(BASE,url.strip())
    parsed=urlparse(absolute)
    if parsed.hostname not in allowed or parsed.scheme not in ('https','http'):
        return None
    if absolute in mapping:
        return mapping[absolute]
    path=unquote(parsed.path)
    suffix=Path(path).suffix.lower()
    if suffix not in resource_exts:
        return None
    filename=Path(path).name
    safe=re.sub(r'[^a-zA-Z0-9_.-]','_',filename)
    if len(safe)>140:
        safe=safe[:110]+suffix
    local=ROOT/'assets'/kind/safe
    if local.exists() and absolute not in mapping:
        safe=hashlib.sha256(absolute.encode()).hexdigest()[:9]+'-'+safe
        local=ROOT/'assets'/kind/safe
    try:
        response=get(absolute)
        if len(response.content)>20_000_000:
            raise ValueError('Asset exceeds 20 MB')
        local.parent.mkdir(parents=True,exist_ok=True)
        local.write_bytes(response.content)
        rel=local.relative_to(ROOT).as_posix()
        mapping[absolute]=rel
        bucket='images' if kind=='img' else 'fonts' if kind=='fonts' else 'stylesheets' if kind=='css/original' else 'scripts'
        inventory[bucket].append({'url':absolute,'local':rel,'size':len(response.content)})
        return rel
    except Exception as exc:
        failures.append({'url':absolute,'error':str(exc)[:180]})
        return None

def main():
    original=get(BASE).text
    soup=BeautifulSoup(original,'html.parser')
    for node in soup.select('img,source'):
        for attr in ('src','data-src','data-lazy-src','data-original','data-srcset','srcset'):
            raw=node.get(attr)
            if not raw or raw.startswith('data:'):
                continue
            if attr.endswith('srcset'):
                items=[part.strip() for part in raw.split(',')]
                for item in items:
                    candidate=item.split()[0]
                    save(candidate,'img')
            else:
                save(raw,'img')
    for node in soup.select('link[href]'):
        href=node.get('href','')
        rel=' '.join(node.get('rel',[]))
        kind='css/original' if 'stylesheet' in rel else 'fonts' if Path(urlparse(href).path).suffix in ('.woff','.woff2','.ttf') else 'img' if 'icon' in rel else None
        if kind:
            save(href,kind)
    for node in soup.select('script[src]'):
        save(node.get('src',''),'js/original')
    css_urls=re.compile(r'url\\(\\s*[\\x22\\x27]?([^\\x22\\x27)]+)')
    for stylesheet in list((ROOT/'assets/css/original').glob('*.css')):
        content=stylesheet.read_text(errors='replace')
        for match in css_urls.finditer(content):
            url=match.group(1).strip()
            if url.startswith('data:'):
                continue
            absolute=urljoin(BASE, url) if url.startswith('/') else urljoin(next((k for k,v in mapping.items() if v==stylesheet.relative_to(ROOT).as_posix()),BASE),url)
            ext=Path(urlparse(absolute).path).suffix.lower()
            if ext in ('.woff','.woff2','.ttf','.otf'):
                save(absolute,'fonts')
            elif ext in resource_exts:
                save(absolute,'img')
    markup=HTML.read_text()
    for url,local in sorted(mapping.items(),key=lambda item:-len(item[0])):
        markup=markup.replace(url,local)
    HTML.write_text(markup)
    (ROOT/'assets/asset-manifest.json').write_text(json.dumps({'source':BASE,'inventory':inventory,'failures':failures},indent=2,ensure_ascii=False))
    print('ASSETS:',{key:len(value) for key,value in inventory.items()})
    print('FAILED:',len(failures))
    for failure in failures[:15]:
        print('FAILED URL:',failure['url'],failure['error'])
    print('LOCALIZED REFS:',len([x for x in mapping if x in original]))
    if not inventory['images']:
        raise SystemExit('No images downloaded; archive failed')

if __name__=='__main__':
    main()
