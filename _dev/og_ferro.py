#!/usr/bin/env python3
"""Gera site/assets/img/og-ferro.jpg (1200x630) para a página ferro.html, com a foto da janela e o título.
Uso: python3 _dev/og_ferro.py   (usa os arquivos do próprio site, via file://)"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
SITE = Path(__file__).resolve().parent.parent / "site"
HTML = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:L;src:url('{SITE.as_uri()}/assets/fonts/literata-var.woff2')}}
@font-face{{font-family:A;src:url('{SITE.as_uri()}/assets/fonts/atkinson-next-var.woff2')}}
*{{margin:0;box-sizing:border-box}}
body{{width:1200px;height:630px;background:#D8ECE5;display:grid;grid-template-columns:1fr 430px;overflow:hidden;font-family:A}}
.t{{padding:64px 0 56px 72px;display:flex;flex-direction:column}}
.logo{{width:250px}}
.r{{margin-top:auto;font:650 19px/1.3 A;letter-spacing:.14em;text-transform:uppercase;color:#2F6E60;display:flex;gap:12px;align-items:center}}
.r:before{{content:"";width:9px;height:9px;border-radius:50%;background:#2F6E60}}
h1{{margin-top:18px;font:580 76px/1.02 L;font-variation-settings:'opsz' 72;color:#103A40;letter-spacing:-.015em}}
p{{margin-top:20px;font:480 30px/1.3 L;color:#103A40}} p em{{color:#2F6E60}}
.f{{position:relative;margin-top:64px;margin-right:56px;background:#63AF9C;border-radius:999px 999px 0 0;padding:14px 14px 0}}
.f img{{width:100%;height:100%;object-fit:cover;object-position:46% 26%;border-radius:999px 999px 0 0;display:block}}
</style></head><body><div class="t"><img class="logo" src="{SITE.as_uri()}/assets/marca/logo-horizontal-cor.svg">
<div class="r">Aula gratuita para gestantes</div><h1>Ferro Sem<br>Sofrimento</h1><p>E o que muda quando a <em>dose é a sua</em>.</p></div>
<div class="f"><img src="{SITE.as_uri()}/assets/img/fotos/gestacao-janela-800.webp"></div></body></html>"""

async def main():
    tmp = Path(__file__).resolve().parent / ".cache" / "og-ferro.html"
    tmp.write_text(HTML, encoding="utf-8")
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1200, "height": 630})
        await pg.goto(tmp.as_uri()); await pg.wait_for_timeout(600)
        await pg.screenshot(path=str(SITE / "assets/img/og-ferro.jpg"), type="jpeg", quality=86)
        await b.close()
    print("ok", SITE / "assets/img/og-ferro.jpg")
asyncio.run(main())
