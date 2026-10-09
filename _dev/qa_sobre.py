#!/usr/bin/env python3
"""QA visual da página Sobre: prints full page em 390 e 1440 + checagens de layout.
Uso: python3 _dev/qa_sobre.py [url_base]  (padrão http://127.0.0.1:8104/)"""
import sys, json
from pathlib import Path
from playwright.sync_api import sync_playwright
BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8104/"
OUT = Path(__file__).resolve().parent / "qa" / "sobre"
OUT.mkdir(exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch()
    for w, h in [(390, 844), (1440, 900), (320, 640), (375, 667)]:
        pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=1, reduced_motion="reduce" if w in (390, 1440) else "no-preference")
        erros = []
        pg.on("console", lambda m: erros.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: erros.append(str(e)))
        pg.goto(BASE + "sobre.html", wait_until="networkidle")
        info = pg.evaluate("""() => {
          const d = document.documentElement;
          const larg = [...document.querySelectorAll('body *')].filter(e => { const r = e.getBoundingClientRect(); return r.width && (r.right > d.clientWidth + 1 || r.left < -1); }).slice(0,8).map(e => e.className + ' ' + Math.round(e.getBoundingClientRect().right));
          const bt = document.querySelector('.sb-hero .sb-botao').getBoundingClientRect();
          return {scrollW: d.scrollWidth, clientW: d.clientWidth, fora: larg, botaoBase: Math.round(bt.bottom), vh: innerHeight};
        }""")
        print(w, json.dumps(info, ensure_ascii=False), erros[:5])
        if w in (390, 1440):
            # rola até o fim para disparar revelações e o traço
            pg.evaluate("""async () => { for (let y = 0; y < document.body.scrollHeight; y += 300) { scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); } scrollTo(0, 0); await new Promise(r => setTimeout(r, 300)); }""")
            pg.screenshot(path=str(OUT / f"sobre-{w}.png"), full_page=True)
        if w in (320, 375):
            pg.evaluate("document.querySelector('.sb-linha').scrollIntoView({block:'start'})")
            pg.wait_for_timeout(400)
            pg.evaluate("scrollBy(0, 250)"); pg.wait_for_timeout(400)
            pg.screenshot(path=str(OUT / f"sobre-{w}-rota.png"))
            pg.evaluate("scrollTo(0,0)"); pg.wait_for_timeout(200)
        if w == 375:
            pg.screenshot(path=str(OUT / "sobre-375-dobra.png"))
        pg.close()
    b.close()
