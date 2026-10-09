#!/usr/bin/env python3
"""QA visual da página Semana Bem Nutrida: prints full page e topo do celular + checagem de rolagem horizontal.
Uso: python3 _dev/qa_semana.py [porta]"""
import sys, asyncio
from pathlib import Path
from playwright.async_api import async_playwright
PORTA = sys.argv[1] if len(sys.argv) > 1 else "8103"
URL = f"http://127.0.0.1:{PORTA}/semana-bem-nutrida.html"
OUT = Path(__file__).resolve().parent / "qa/semana"
OUT.mkdir(parents=True, exist_ok=True)

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for w, h in [(320, 640), (390, 844), (430, 932), (768, 1024), (1440, 900)]:
            pg = await b.new_page(viewport={"width": w, "height": h}, device_scale_factor=1 if w > 800 else 2)
            erros = []
            pg.on("console", lambda m: erros.append(m.text) if m.type in ("error", "warning") else None)
            pg.on("requestfailed", lambda r: erros.append("FALHOU " + r.url))
            pg.on("response", lambda r: erros.append(f"{r.status} {r.url}") if r.status >= 400 else None)
            await pg.goto(URL, wait_until="networkidle")
            await pg.screenshot(path=str(OUT / f"topo-{w}.png"))
            altura = await pg.evaluate("document.documentElement.scrollHeight")
            y = 0
            while y < altura:
                await pg.evaluate(f"window.scrollTo(0,{y})"); await pg.wait_for_timeout(120); y += h // 2
            await pg.wait_for_timeout(1500)
            await pg.evaluate("window.scrollTo(0,0)"); await pg.wait_for_timeout(300)
            info = await pg.evaluate("""() => {
              const d=document.documentElement; const W=d.clientWidth; const largos=[];
              document.querySelectorAll('body *').forEach(e=>{const r=e.getBoundingClientRect(); if(r.width&&(r.right>W+1||r.left<-1)) largos.push(e.className+' '+Math.round(r.left)+'..'+Math.round(r.right));});
              const btn=document.querySelector('#cta-topo .sbn-botao').getBoundingClientRect();
              return {scrollW:d.scrollWidth, W, largos:largos.slice(0,12), botaoBottom:Math.round(btn.bottom)};
            }""")
            print(w, info, ("ERROS: " + " | ".join(erros[:8])) if erros else "")
            if w == 390:
                await pg.evaluate("window.scrollTo(0,4200)"); await pg.wait_for_timeout(500)
                await pg.screenshot(path=str(OUT / "barra-390.png"))
                await pg.evaluate("window.scrollTo(0,0)"); await pg.wait_for_timeout(300)
            if w in (390, 1440, 320):
                await pg.screenshot(path=str(OUT / f"full-{w}.png"), full_page=True)
            await pg.close()
        await b.close()
asyncio.run(main())
