#!/usr/bin/env python3
"""QA visual da página Ferro Sem Sofrimento: prints (topo e full page), rolagem horizontal, posição do botão,
cadastro aberto e enviado. Uso: python3 _dev/qa_ferro.py [porta]"""
import sys, asyncio
from pathlib import Path
from playwright.async_api import async_playwright
PORTA = sys.argv[1] if len(sys.argv) > 1 else "8105"
URL = f"http://127.0.0.1:{PORTA}/ferro.html"
OUT = Path(__file__).resolve().parent / "qa/ferro"
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
                await pg.evaluate(f"window.scrollTo(0,{y})"); await pg.wait_for_timeout(100); y += h // 2
            await pg.wait_for_timeout(1500)
            if w in (390, 1440):
                await pg.screenshot(path=str(OUT / f"barra-{w}.png"))
            await pg.evaluate("window.scrollTo(0,0)"); await pg.wait_for_timeout(300)
            info = await pg.evaluate("""() => {
              const d=document.documentElement; const W=d.clientWidth; const largos=[];
              document.querySelectorAll('body *').forEach(e=>{ if(e.closest('dialog')) return; const r=e.getBoundingClientRect(); if(r.width&&(r.right>W+1||r.left<-1)) largos.push((e.className.baseVal??e.className)+' '+Math.round(r.left)+'..'+Math.round(r.right));});
              const btn=document.querySelector('#cta-topo .fer-botao').getBoundingClientRect();
              const pequenos=[...document.querySelectorAll('main p, main li, main summary')].filter(e=>parseFloat(getComputedStyle(e).fontSize)<15).length;
              return {scrollW:d.scrollWidth, W, largos:largos.slice(0,12), botaoTop:Math.round(btn.top), botaoBottom:Math.round(btn.bottom), pequenos};
            }""")
            print(w, info, ("ERROS: " + " | ".join(erros[:8])) if erros else "")
            if w in (390, 1440, 320):
                await pg.screenshot(path=str(OUT / f"full-{w}.png"), full_page=True)
            if w in (390, 1440):
                await pg.click("#cta-topo .fer-botao"); await pg.wait_for_timeout(600)
                await pg.screenshot(path=str(OUT / f"cadastro-{w}.png"))
                await pg.click("#f-enviar"); await pg.wait_for_timeout(300)
                await pg.screenshot(path=str(OUT / f"cadastro-erros-{w}.png"))
                await pg.fill("#f-nome", "Maria"); await pg.type("#f-whats", "21987654321")
                await pg.click("label.fer-check >> nth=0")
                v = await pg.input_value("#f-whats")
                await pg.click("#f-enviar"); await pg.wait_for_timeout(1500)
                await pg.screenshot(path=str(OUT / f"cadastro-ok-{w}.png"))
                dlv = await pg.evaluate("JSON.stringify(window.dataLayer)")
                print("  mascara:", v, "| dataLayer:", dlv)
            await pg.close()
        await b.close()
asyncio.run(main())
