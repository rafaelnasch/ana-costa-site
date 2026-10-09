#!/usr/bin/env python3
"""QA visual da página inicial: prints (topo e página inteira) + checagem de rolagem horizontal,
botão principal na primeira tela do celular e erros de rede/console.
Uso: python3 _dev/qa_home.py [porta]   (servidor: python3 -m http.server 8100 dentro de site/)"""
import sys, asyncio
from pathlib import Path
from playwright.async_api import async_playwright

PORTA = sys.argv[1] if len(sys.argv) > 1 else "8100"
URL = f"http://127.0.0.1:{PORTA}/index.html"
OUT = Path(__file__).resolve().parent / "qa/home"
OUT.mkdir(parents=True, exist_ok=True)
CHEIA = {390, 1440}


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for w, h in [(320, 640), (360, 740), (390, 844), (430, 932), (768, 1024), (1024, 768), (1440, 900)]:
            pg = await b.new_page(viewport={"width": w, "height": h}, device_scale_factor=2 if w < 800 else 1)
            erros = []
            pg.on("console", lambda m: erros.append(m.text) if m.type in ("error", "warning") else None)
            pg.on("pageerror", lambda e: erros.append("JS " + str(e)))
            pg.on("response", lambda r: erros.append(f"{r.status} {r.url}") if r.status >= 400 else None)
            await pg.goto(URL, wait_until="networkidle")
            await pg.add_style_tag(content="html{scroll-behavior:auto!important}")
            await pg.screenshot(path=str(OUT / f"topo-{w}.png"))
            altura = await pg.evaluate("document.documentElement.scrollHeight")
            y = 0
            while y < altura:
                await pg.evaluate(f"window.scrollTo(0,{y})"); await pg.wait_for_timeout(90); y += h // 2
            await pg.wait_for_timeout(1300)
            info = await pg.evaluate("""() => {
              const d=document.documentElement, W=d.clientWidth, largos=[];
              document.querySelectorAll('body *').forEach(e=>{const r=e.getBoundingClientRect();
                if(r.width && (r.right>W+1 || r.left<-1) && getComputedStyle(e).position!=='fixed') largos.push((e.className.baseVal??e.className)+' '+Math.round(r.left)+'..'+Math.round(r.right));});
              window.scrollTo(0,0);
              const btn=document.querySelector('#cta-hero .hm-botao').getBoundingClientRect();
              const pequenos=[]; document.querySelectorAll('main p, main li, main a, footer p, footer li').forEach(e=>{const f=parseFloat(getComputedStyle(e).fontSize); if(f<14 && e.offsetParent) pequenos.push(e.textContent.trim().slice(0,30)+':'+f)});
              return {scrollW:d.scrollWidth, W, largos:largos.slice(0,10), botaoBottom:Math.round(btn.bottom), pequenos:pequenos.slice(0,6)};
            }""")
            print(w, info, ("ERROS: " + " | ".join(erros[:8])) if erros else "")
            if w in CHEIA:
                await pg.wait_for_timeout(300)
                await pg.screenshot(path=str(OUT / f"cheia-{w}.png"), full_page=True)
            if w == 390:
                await pg.evaluate("window.scrollTo(0,2600)"); await pg.wait_for_timeout(600)
                await pg.screenshot(path=str(OUT / "barra-390.png"))
                await pg.evaluate("window.scrollTo(0,0)")
                await pg.click(".hm-menu-botao"); await pg.wait_for_timeout(200)
                await pg.screenshot(path=str(OUT / "menu-390.png"))
            await pg.close()
        await b.close()

asyncio.run(main())
