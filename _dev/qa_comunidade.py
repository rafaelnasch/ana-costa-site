#!/usr/bin/env python3
"""QA visual da página Comunidade Bem Nutrida: prints (topo e página inteira), rolagem horizontal, erros e checagens.
Uso: python3 _dev/qa_comunidade.py [porta]"""
import sys, asyncio, json
from pathlib import Path
from playwright.async_api import async_playwright
PORTA = sys.argv[1] if len(sys.argv) > 1 else "8102"
URL = f"http://127.0.0.1:{PORTA}/comunidade.html"
OUT = Path(__file__).resolve().parent / "qa/comunidade"
OUT.mkdir(parents=True, exist_ok=True)
TAMANHOS = [(320, 640), (390, 844), (430, 932), (768, 1024), (1440, 900)]

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for w, h in TAMANHOS:
            pg = await b.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
            erros = []
            pg.on("console", lambda m: erros.append(m.text) if m.type in ("error", "warning") else None)
            pg.on("requestfailed", lambda r: erros.append("FALHOU " + r.url))
            pg.on("response", lambda r: erros.append(f"{r.status} {r.url}") if r.status >= 400 else None)
            await pg.goto(URL, wait_until="networkidle")
            await pg.wait_for_timeout(400)
            await pg.screenshot(path=str(OUT / f"topo-{w}.png"))
            altura = await pg.evaluate("document.documentElement.scrollHeight")
            y = 0
            while y < altura:
                await pg.evaluate(f"window.scrollTo(0,{y})"); await pg.wait_for_timeout(90); y += h // 2
            await pg.wait_for_timeout(1400)
            await pg.evaluate("document.documentElement.style.scrollBehavior='auto';window.scrollTo(0,0)"); await pg.wait_for_timeout(300)
            info = await pg.evaluate("""() => {
              const d=document.documentElement; const W=d.clientWidth; const largos=[];
              document.querySelectorAll('body *').forEach(el=>{const r=el.getBoundingClientRect(); if(r.width&&(r.right>W+1||r.left<-1)&&getComputedStyle(el).position!=='fixed'){largos.push(el.tagName+'.'+(el.className&&el.className.baseVal===undefined?el.className:'')+' '+Math.round(r.left)+'..'+Math.round(r.right))}});
              const bt=document.querySelector('#cta-topo .cbn-botao').getBoundingClientRect();
              const chaves=document.body.innerText.match(/\\{\\{[^}]+\\}\\}/g);
              const fonte=getComputedStyle(document.querySelector('.cbn-oque .cbn-corpo p')).fontSize;
              return {scrollW:d.scrollWidth, W, largos:largos.slice(0,12), botaoBottom:Math.round(bt.bottom), chaves, fonte};
            }""")
            print(w, json.dumps(info, ensure_ascii=False), "ERROS:", erros[:6])
            await pg.screenshot(path=str(OUT / f"pagina-{w}.png"), full_page=True)
            await pg.close()
        await b.close()
asyncio.run(main())
