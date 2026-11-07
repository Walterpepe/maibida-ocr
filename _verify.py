# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

URLS = [
    ("zh-home",    "http://127.0.0.1:8899/index.html"),
    ("en-home",    "http://127.0.0.1:8899/en/index.html"),
    ("en-product", "http://127.0.0.1:8899/en/product/10032.html"),
    ("en-company", "http://127.0.0.1:8899/en/company.html"),
    ("en-news",    "http://127.0.0.1:8899/en/newsInfo/10186.html"),
    ("en-pinfo",   "http://127.0.0.1:8899/en/productInfo/10200.html"),
    ("zh-product", "http://127.0.0.1:8899/product/10032.html"),
]

with sync_playwright() as p:
    b = p.chromium.launch()
    for name, url in URLS:
        pg = b.new_page(viewport={"width":1920,"height":1080})
        try:
            pg.goto(url, wait_until='load', timeout=25000)
            pg.wait_for_timeout(1500)
        except Exception as e:
            print(f"[{name}] goto error: {e}"); pg.close(); continue
        r = pg.evaluate("""async () => {
          const out = {};
          out.lang = document.documentElement.lang;
          out.hasBtn = !!document.querySelector('.lang-btn');
          out.btn = [...document.querySelectorAll('.lang-item')].map(a=>a.getAttribute('href'));
          const zhRe = /[\\u4e00-\\u9fff]{4,}/g;
          out.zh = (document.body.innerText.match(zhRe)||[]).length;
          out.hOver = document.documentElement.scrollWidth - document.documentElement.clientWidth;
          // 真坏图：fetch 资源并看 status
          let bad=0, tot=0;
          const imgs=[...document.querySelectorAll('img')];
          for (const im of imgs){
            const s=im.currentSrc||im.src; if(!s) continue; tot++;
            try{ const res=await fetch(s,{method:'HEAD'}); if(!res.ok) bad++; }
            catch(e){ bad++; }
          }
          out.imgTot=tot; out.imgBad=bad;
          return out;
        }""")
        print(f"{name}: lang={r['lang']} btn={r['hasBtn']} links={r['btn']} zhVisible={r['zh']} hOver={r['hOver']} imgBad={r['imgBad']}/{r['imgTot']}")
        pg.close()
    b.close()
print("DONE")
