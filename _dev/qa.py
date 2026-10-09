#!/usr/bin/env python3
"""QA de todas as páginas do site (estático + navegador real).

Uso:  python3 _dev/qa.py [--larguras 320,390,768,1440] [--sem-prints]
Sobe um servidor local próprio em site/ (porta livre), roda Chromium (Playwright) em cada página e largura,
e grava prints em _dev/qa/final/ e o relatório em _dev/qa/final/relatorio.md (e .json).

Checagens
  estáticas: title, description, robots noindex/nofollow, canonical, Open Graph (imagem existe), JSON-LD válido,
             FAQPage onde há FAQ, cabeçalho e rodapé idênticos (sem contar o item ativo), item ativo correto,
             links internos e âncoras, imagens com alt/width/height/lazy, preload de fontes, favicon/manifest,
             marcadores {{...}} crus, emoji, travessões, consentimentos desmarcados, sitemap e robots.
  navegador: erros de JS/console/rede, rolagem horizontal (e quem estoura), um h1, corpo >= 17/18 px,
             texto < 14 px, botão principal visível na 1ª tela do celular, contraste AA aproximado,
             conteúdo que ficou invisível depois de rolar, nome acessível de links/botões/campos, LCP local.
"""
import argparse, asyncio, functools, http.server, json, re, socketserver, threading
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote

RAIZ = Path(__file__).resolve().parent.parent
SITE = RAIZ / "site"
OUT = RAIZ / "_dev" / "qa" / "final"
PAGINAS = ["index.html", "atendimentos.html", "comunidade.html", "semana-bem-nutrida.html", "sobre.html",
           "ferro.html", "privacidade.html", "termos.html", "404.html"]
ATIVO = {"index.html": "./", "atendimentos.html": "atendimentos.html", "comunidade.html": "comunidade.html",
         "semana-bem-nutrida.html": "semana-bem-nutrida.html", "sobre.html": "sobre.html"}
EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF⭐⬆↔-↪]")


# ---------------------------------------------------------------- estático
class Coletor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids, self.links, self.imgs, self.metas, self.linkrel, self.ldjson = set(), [], [], {}, [], []
        self._ld = None
        self.inputs = []
        self.preloads = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "a" and "href" in a:
            self.links.append(a["href"])
        if tag == "img":
            self.imgs.append(a)
        if tag == "meta":
            k = a.get("name") or a.get("property")
            if k:
                self.metas[k] = a.get("content", "")
        if tag == "link":
            self.linkrel.append(a)
        if tag == "script" and a.get("type") == "application/ld+json":
            self._ld = ""
        if tag == "input":
            self.inputs.append(a)

    def handle_data(self, data):
        if self._ld is not None:
            self._ld += data

    def handle_endtag(self, tag):
        if tag == "script" and self._ld is not None:
            self.ldjson.append(self._ld)
            self._ld = None


@functools.lru_cache(None)
def coleta(nome):
    c = Coletor()
    c.feed((SITE / nome).read_text(encoding="utf-8"))
    return c


def bloco(html, nome):
    m = re.search(rf"<!-- site:{nome} -->(.*?)<!-- /site:{nome} -->", html, re.S)
    return m.group(1) if m else None


def tipos_ld(obj):
    out = []
    if isinstance(obj, dict):
        t = obj.get("@type")
        out += t if isinstance(t, list) else ([t] if t else [])
        for v in obj.values():
            out += tipos_ld(v)
    elif isinstance(obj, list):
        for v in obj:
            out += tipos_ld(v)
    return out


def valor_config(chave):
    """Lê um valor simples de assets/js/config.js (string, true/false/null)."""
    cfg = (SITE / "assets/js/config.js").read_text(encoding="utf-8")
    m = re.search(rf'^\s*{re.escape(chave)}:\s*("([^"]*)"|true|false|null)', cfg, re.M)
    if not m: return None
    if m.group(1).startswith('"'): return m.group(2)
    return {"true": True, "false": False, "null": None}[m.group(1)]


def publicacao():
    """Com previa=false, nada vai ao ar sem os dados obrigatórios (CRN, e-Nutricionista, contatos, quem vende, endpoints)."""
    if valor_config("previa") is not False:
        return []
    faltam = [k for k in ("crn", "whatsapp", "email", "nomeVendedor", "cpfCnpj", "enderecoFiscal", "formEndpoint", "linkAgendamento")
              if not (valor_config(k) or "").strip()]
    if valor_config("cadastroENutricionista") is not True: faltam.append("cadastroENutricionista=true")
    if valor_config("semanaPronta") is True and not (valor_config("linkCheckoutSemana") or "").strip(): faltam.append("linkCheckoutSemana")
    return [f"PUBLICAÇÃO BLOQUEADA: previa=false com dado obrigatório vazio no CONFIG → {', '.join(faltam)}"] if faltam else []


def fotos_repetidas():
    """Nenhuma foto em mais de 2 páginas e nenhuma repetida dentro da mesma página (hero-mobile conta como hero)."""
    usos, P = {}, []
    for p in PAGINAS:
        html = (SITE / p).read_text(encoding="utf-8")
        corpo = html.split("<body", 1)[-1]
        imgs = re.findall(r'<img [^>]*src="assets/img/fotos/([a-z-]+?)-(?:mobile-)?\d+\.webp"', corpo)
        nomes = [n.replace("hero-mobile", "hero") for n in imgs]
        for n in set(nomes):
            if nomes.count(n) > 1: P.append(f"{p}: foto \"{n}\" repetida {nomes.count(n)}x na mesma página")
            usos.setdefault(n, set()).add(p)
    for n, ps in sorted(usos.items()):
        if len(ps) > 2: P.append(f"foto \"{n}\" em {len(ps)} páginas: {', '.join(sorted(ps))}")
    return P


def estatico():
    probs = {p: [] for p in PAGINAS}
    geral = []
    topos, rodapes = {}, {}
    for p in PAGINAS:
        html = (SITE / p).read_text(encoding="utf-8")
        c = coleta(p)
        P = probs[p]
        if not re.search(r"<title>[^<]{10,}</title>", html): P.append("sem <title> útil")
        if len(c.metas.get("description", "")) < 50: P.append("meta description ausente/curta")
        if "noindex" not in c.metas.get("robots", "") or "nofollow" not in c.metas.get("robots", ""):
            P.append("robots sem noindex,nofollow (prévia)")
        if not any(l.get("rel") == "canonical" for l in c.linkrel): P.append("sem canonical")
        for og in ("og:title", "og:description", "og:image", "og:url", "og:type"):
            if not c.metas.get(og): P.append(f"sem {og}")
        img = c.metas.get("og:image", "")
        if img:
            caminho = urlparse(img).path.replace("/ana-costa-site/", "", 1).lstrip("/")
            if not (SITE / caminho).exists(): P.append(f"og:image não existe: {img}")
        if not any("icon" in (l.get("rel") or "") for l in c.linkrel): P.append("sem favicon")
        if not any(l.get("rel") == "manifest" for l in c.linkrel): P.append("sem manifest")
        fontes = [l for l in c.linkrel if l.get("rel") == "preload" and l.get("as") == "font"]
        if len(fontes) < 2 or any("crossorigin" not in l for l in fontes): P.append("preload de fontes incompleto")
        tipos = []
        for bloco_ld in c.ldjson:
            try:
                tipos += tipos_ld(json.loads(bloco_ld))
            except Exception as e:
                P.append(f"JSON-LD inválido: {e}")
        if p != "404.html":
            if "Person" not in tipos: P.append("JSON-LD sem Person")
            if not ({"MedicalBusiness", "ProfessionalService"} & set(tipos)): P.append("JSON-LD sem MedicalBusiness/ProfessionalService")
        if re.search(r'class="[^"]*faq', html, re.I) and "FAQPage" not in tipos: P.append("tem FAQ mas JSON-LD sem FAQPage")
        if re.search(r'"(identifier|hasCredential)"[^}]*CRN[^}]*\d{3,}', html): P.append("JSON-LD parece afirmar número de CRN")
        # cabeçalho e rodapé
        t, r = bloco(html, "topo"), bloco(html, "rodape")
        if t is None: P.append("sem cabeçalho padrão (<!-- site:topo -->)")
        else: topos[p] = re.sub(r' aria-current="page"', "", t)
        if r is None: P.append("sem rodapé padrão (<!-- site:rodape -->)")
        else: rodapes[p] = re.sub(r' aria-current="page"', "", r)
        if t is not None:
            ativos = re.findall(r'href="([^"]+)" aria-current="page"', t)
            esperado = [ATIVO[p]] if p in ATIVO else []
            if ativos != esperado: P.append(f"item ativo do menu errado: {ativos} (esperado {esperado})")
        # links internos
        for href in c.links:
            if re.match(r"^(https?:|mailto:|tel:|javascript:)", href) or href == "#": continue
            alvo, _, ancora = href.partition("#")
            alvo = unquote(alvo.split("?", 1)[0]) or p
            if alvo in ("./", ""): alvo = "index.html"
            arq = SITE / alvo
            if not arq.exists():
                P.append(f"link quebrado: {href}"); continue
            if ancora and arq.suffix == ".html" and ancora not in coleta(arq.name).ids:
                P.append(f"âncora inexistente: {href}")
        # imagens
        for i, im in enumerate(c.imgs):
            src = im.get("src", "")
            if "alt" not in im: P.append(f"img sem alt: {src}")
            if not (im.get("width") and im.get("height")): P.append(f"img sem width/height: {src}")
            if src and not src.startswith(("http", "data:")) and not (SITE / src).exists(): P.append(f"img inexistente: {src}")
        # texto: marcadores crus, emoji, travessões
        corpo = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S)
        corpo = re.sub(r"<!--.*?-->", " ", corpo, flags=re.S)
        texto = re.sub(r"<[^>]+>", " ", corpo)
        if "{{" in texto: P.append("marcador {{...}} cru no texto: " + ", ".join(sorted(set(re.findall(r"\{\{[^}]*\}\}", texto)))[:5]))
        em = EMOJI.findall(texto)
        if em: P.append("emoji no texto: " + "".join(sorted(set(em))))
        n_trav = texto.count("—")
        if n_trav > 2: P.append(f"{n_trav} travessões (—) no texto")
        # consentimentos
        for inp in c.inputs:
            if inp.get("type") == "checkbox" and "checked" in inp: P.append(f"checkbox marcado por padrão: {inp.get('name')}")
    # cabeçalho/rodapé idênticos
    for nome, d in (("cabeçalho", topos), ("rodapé", rodapes)):
        variantes = {}
        for p, v in d.items(): variantes.setdefault(re.sub(r"\s+", " ", v).strip(), []).append(p)
        if len(variantes) > 1: geral.append(f"{nome} difere entre páginas: " + " | ".join(", ".join(v) for v in variantes.values()))
    # sitemap e robots
    sm = SITE / "sitemap.xml"
    if not sm.exists(): geral.append("sitemap.xml ausente")
    else:
        urls = re.findall(r"<loc>([^<]+)</loc>", sm.read_text())
        for u in urls:
            caminho = urlparse(u).path.replace("/ana-costa-site/", "", 1) or "index.html"
            if not (SITE / caminho).exists(): geral.append(f"sitemap aponta para arquivo inexistente: {u}")
    rb = SITE / "robots.txt"
    if not rb.exists(): geral.append("robots.txt ausente")
    elif not re.search(r"^Disallow:\s*/\s*$", rb.read_text(), re.M): geral.append("robots.txt sem Disallow: / (prévia)")
    if not (SITE / "manifest.webmanifest").exists(): geral.append("manifest.webmanifest ausente")
    return probs, geral


# ---------------------------------------------------------------- navegador
JS_INFO = r"""(larg) => {
  const d=document.documentElement, W=d.clientWidth, H=innerHeight, out={};
  out.scrollW=d.scrollWidth; out.W=W;
  const clipado = (e) => { for(let a=e.parentElement;a&&a!==document.body;a=a.parentElement){const o=getComputedStyle(a).overflowX; if(o!=='visible') return true;} return false; };
  const largos=[];
  document.querySelectorAll('body *').forEach(e=>{const r=e.getBoundingClientRect(); const cs=getComputedStyle(e);
    if(r.width && (r.right>W+1 || r.left<-1) && cs.position!=='fixed' && cs.visibility!=='hidden' && !clipado(e))
      largos.push((e.id?'#'+e.id:'')+'.'+String(e.className.baseVal??e.className).split(' ').slice(0,2).join('.')+' '+Math.round(r.left)+'..'+Math.round(r.right));});
  out.largos=largos.slice(0,8);
  out.h1=document.querySelectorAll('h1').length;
  out.corpo=parseFloat(getComputedStyle(document.body).fontSize);
  const vis = e => { const r=e.getBoundingClientRect(); const cs=getComputedStyle(e); return r.width>0&&r.height>0&&cs.visibility!=='hidden'&&cs.display!=='none'; };
  // tamanho típico do texto corrido: moda ponderada pelo número de caracteres (exclui rótulos, microcopy e selos)
  const ps=[...document.querySelectorAll('main p, main li')].filter(e=>vis(e) && !/rotulo|micro|selo|nota|legenda|tag|aviso/i.test(String(e.className)) && !e.closest('[aria-hidden="true"],form,nav'));
  const freq={}; ps.forEach(e=>{const f=parseFloat(getComputedStyle(e).fontSize); freq[f]=(freq[f]||0)+e.textContent.trim().length;});
  out.pModa = ps.length? +Object.entries(freq).sort((a,b)=>b[1]-a[1])[0][0] : null;
  const peq=[]; document.querySelectorAll('main p, main li, main a, main label, main span, footer p, footer li, footer a, header a').forEach(e=>{
    if(!vis(e) || !e.textContent.trim() || e.closest('.site-sr,[class*="-sr"],[aria-hidden="true"]')) return;
    const f=parseFloat(getComputedStyle(e).fontSize); if(f<14) peq.push((e.className&&typeof e.className==='string'?'.'+e.className.trim().split(/\s+/)[0]+' ':'')+e.textContent.trim().slice(0,28)+' ('+f+'px)');});
  out.pequenos=[...new Set(peq)].slice(0,6);
  // contraste
  const rgb=c=>{const m=c.match(/[\d.]+/g); if(!m) return null; const k=c.startsWith('color(srgb')?1:255; return m.slice(0,3).map(v=>+v/k);};
  const lum=c=>{const v3=rgb(c); if(!v3) return null; const [r,g,b]=v3.map(v=>{return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)}); return .2126*r+.7152*g+.0722*b;};
  const alfa=c=>{const m=c.match(/[\d.]+/g); if(c.startsWith('color(')){const a=c.split('/')[1]; return a?parseFloat(a):1;} return m&&m.length>3?+m[3]:1;};
  const fundo=e=>{for(let a=e;a;a=a.parentElement){const cs=getComputedStyle(a); if(cs.backgroundImage!=='none' && !cs.backgroundImage.startsWith('linear-gradient(transparent')) return null; if(alfa(cs.backgroundColor)>.9) return cs.backgroundColor;} return 'rgb(255,255,255)';};
  const nomeEl=e=>e.tagName.toLowerCase()+(e.className&&typeof e.className==='string'?'.'+e.className.trim().split(/\s+/).slice(0,2).join('.'):'');
  const ruins=[];
  document.querySelectorAll('body *').forEach(e=>{
    if(![...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim())) return;
    if(!vis(e) || e.closest('[aria-hidden="true"],.site-sr,[class*="-sr"],svg')) return;
    const cs=getComputedStyle(e); if(+cs.opacity<1 || alfa(cs.color)<.99) return;
    const bg=fundo(e); if(!bg) return;
    const l1=lum(cs.color), l2=lum(bg); if(l1==null||l2==null) return;
    const r=(Math.max(l1,l2)+.05)/(Math.min(l1,l2)+.05);
    const f=parseFloat(cs.fontSize), w=parseInt(cs.fontWeight);
    const grande = f>=24 || (f>=18.66 && w>=700);
    if(r < (grande?3:4.5)) ruins.push(nomeEl(e)+' "'+e.textContent.trim().slice(0,24)+'" '+r.toFixed(2)+':1 ('+f+'px)');
  });
  out.contraste=[...new Set(ruins)].slice(0,8);
  // nome acessível
  const semNome=[];
  document.querySelectorAll('a[href],button,input:not([type=hidden]),select,textarea').forEach(e=>{
    if(!vis(e) && !['checkbox','radio'].includes(e.type)) return;
    let n=(e.getAttribute('aria-label')||e.textContent||'').trim()||e.getAttribute('title')||'';
    if(e.matches('input,select,textarea')){ n = n || (e.labels&&e.labels.length?e.labels[0].textContent.trim():'') || e.getAttribute('aria-labelledby')||''; }
    if(!n && e.querySelector('img[alt]:not([alt=""])')) n='img';
    if(!n) semNome.push(e.outerHTML.slice(0,70));
  });
  out.semNome=semNome.slice(0,5);
  // conteúdo invisível depois de rolar
  const inv=[]; document.querySelectorAll('main h2, main h3, main p').forEach(e=>{
    const r=e.getBoundingClientRect(); if(!r.width||!e.textContent.trim()) return;
    let op=1; for(let a=e;a&&a!==document.body;a=a.parentElement){op*=+getComputedStyle(a).opacity;}
    if(op<.2 && !e.closest('[hidden],[aria-hidden="true"],dialog:not([open]),details:not([open])')) inv.push(e.textContent.trim().slice(0,30));});
  out.invisiveis=inv.slice(0,5);
  return out;
}"""

JS_CTA = r"""() => {
  window.scrollTo(0,0);
  const vis = e => { const r=e.getBoundingClientRect(); const cs=getComputedStyle(e); return r.width>0&&r.height>0&&cs.visibility!=='hidden'&&cs.display!=='none'; };
  const cands=[...document.querySelectorAll('main a, main button')].filter(e=>vis(e) && /botao|btn|cta/i.test(String(e.className)) && !/link|texto|contorno|secund|claro|fase|chip|aba|regua/i.test(String(e.className)) && !e.closest('[role=tablist],.site-nav,form,dialog,details'));
  if(!cands.length) return {txt:null};
  const e=cands[0], r=e.getBoundingClientRect();
  return {txt:e.textContent.trim().replace(/\s+/g,' ').slice(0,40), bottom:Math.round(r.bottom), H:innerHeight};
}"""


class Silencioso(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass


async def navegador(larguras, prints):
    from playwright.async_api import async_playwright
    handler = functools.partial(Silencioso, directory=str(SITE))
    class Servidor(socketserver.ThreadingTCPServer):
        daemon_threads, allow_reuse_address, request_queue_size = True, True, 128
    httpd = Servidor(("127.0.0.1", 0), handler)
    porta = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    res = {}
    alturas = {320: 568, 360: 740, 390: 844, 430: 932, 768: 1024, 1024: 768, 1440: 900}
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        for p in PAGINAS:
            for w in larguras:
                h = alturas.get(w, 900)
                ctx = await b.new_context(viewport={"width": w, "height": h}, device_scale_factor=1)
                pg = await ctx.new_page()
                erros = []
                pg.on("console", lambda m: erros.append(m.type + ": " + m.text[:140]) if m.type in ("error", "warning") else None)
                pg.on("pageerror", lambda e: erros.append("JS " + str(e)[:160]))
                pg.on("response", lambda r: erros.append(f"HTTP {r.status} {r.url.split(str(porta))[-1]}") if r.status >= 400 and not r.url.endswith("/favicon.ico") else None)
                await pg.add_init_script("""window.__lcp=0;try{new PerformanceObserver(l=>{for(const e of l.getEntries())window.__lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true})}catch(e){}""")
                await pg.goto(f"http://127.0.0.1:{porta}/{p}", wait_until="networkidle")
                await pg.add_style_tag(content="html{scroll-behavior:auto!important}")
                cta = await pg.evaluate(JS_CTA)
                lcp = await pg.evaluate("window.__lcp")
                if prints:
                    await pg.screenshot(path=str(OUT / f"{p[:-5]}-{w}-topo.png"))
                altura = await pg.evaluate("document.documentElement.scrollHeight")
                y = 0
                while y < altura:
                    await pg.evaluate(f"window.scrollTo(0,{y})"); await pg.wait_for_timeout(70); y += h // 2
                await pg.wait_for_timeout(1400)
                info = await pg.evaluate(JS_INFO, w)
                info["cta"], info["lcp"], info["erros"] = cta, round(lcp or 0), sorted(set(erros))[:8]
                if prints and w in (390, 1440):
                    await pg.evaluate("window.scrollTo(0,0)"); await pg.wait_for_timeout(300)
                    await pg.screenshot(path=str(OUT / f"{p[:-5]}-{w}-inteira.png"), full_page=True)
                if w == 390:
                    # menu do celular abre, Esc fecha
                    await pg.evaluate("window.scrollTo(0,0)")
                    try:
                        await pg.click(".site-topo__menu", timeout=2000)
                        aberto = await pg.evaluate("document.querySelector('.site-topo__menu').getAttribute('aria-expanded')")
                        if prints: await pg.screenshot(path=str(OUT / f"{p[:-5]}-390-menu.png"))
                        await pg.keyboard.press("Escape")
                        fechado = await pg.evaluate("document.querySelector('.site-topo__menu').getAttribute('aria-expanded')")
                        await pg.click(".site-topo__menu", timeout=2000)
                        largura_aberto = await pg.evaluate("[document.documentElement.scrollWidth, document.documentElement.clientWidth, Math.round(document.querySelector('#menu-site').getBoundingClientRect().left)]")
                        await pg.keyboard.press("Escape")
                        info["menu"] = "ok" if (aberto, fechado) == ("true", "false") else f"falhou ({aberto},{fechado})"
                        if largura_aberto[0] > largura_aberto[1] or largura_aberto[2] < 0: info["menu"] = f"menu aberto estoura a tela {largura_aberto}"
                    except Exception as e:
                        info["menu"] = "erro: " + str(e)[:80]
                res.setdefault(p, {})[w] = info
                await ctx.close()
        await b.close()
    httpd.shutdown()
    return res


def avalia(p, w, i):
    """Transforma as medições em problemas."""
    P = []
    if i["scrollW"] > i["W"]: P.append(f"rolagem horizontal ({i['scrollW']} > {i['W']}): {', '.join(i['largos'][:4])}")
    if i["h1"] != 1: P.append(f"{i['h1']} h1 na página")
    minimo = 17 if w < 641 else 18
    if i["corpo"] < minimo: P.append(f"corpo {i['corpo']}px (< {minimo})")
    if i["pModa"] and i["pModa"] < minimo: P.append(f"parágrafo típico {i['pModa']}px (< {minimo})")
    if i["pequenos"]: P.append("texto < 14px: " + "; ".join(i["pequenos"]))
    if i["contraste"]: P.append("contraste abaixo de AA: " + "; ".join(i["contraste"]))
    if i["semNome"]: P.append("sem nome acessível: " + "; ".join(i["semNome"]))
    if i["invisiveis"]: P.append("conteúdo invisível após rolar: " + "; ".join(i["invisiveis"]))
    if i["erros"]: P.append("erros: " + " | ".join(i["erros"]))
    if w < 768 and p != "404.html":
        c = i["cta"]
        if not c.get("txt"): P.append("botão principal não encontrado no topo")
        elif c["bottom"] > c["H"]: P.append(f"botão principal \"{c['txt']}\" abaixo da 1ª tela ({c['bottom']} > {c['H']})")
    if i.get("menu") and i["menu"] != "ok": P.append("menu do celular: " + i["menu"])
    return P


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--larguras", default="320,390,768,1440")
    ap.add_argument("--sem-prints", action="store_true")
    a = ap.parse_args()
    larguras = [int(x) for x in a.larguras.split(",")]
    OUT.mkdir(parents=True, exist_ok=True)
    est, geral = estatico()
    geral = publicacao() + fotos_repetidas() + geral
    nav = asyncio.run(navegador(larguras, not a.sem_prints))
    linhas = ["# QA do site · Ana Paula Costa", "", f"Larguras: {', '.join(map(str, larguras))} px · páginas: {len(PAGINAS)}", ""]
    total = 0
    if geral:
        linhas += ["## Geral", ""] + [f"- {g}" for g in geral] + [""]
        total += len(geral)
    for p in PAGINAS:
        linhas.append(f"## {p}")
        probs = [f"[estático] {x}" for x in est[p]]
        for w in larguras:
            probs += [f"[{w}px] {x}" for x in avalia(p, w, nav[p][w])]
        lcps = ", ".join(f"{w}px {nav[p][w]['lcp']} ms" for w in larguras)
        ctas = nav[p][min(larguras)]["cta"]
        linhas.append(f"- LCP local: {lcps} · botão principal no celular: \"{ctas.get('txt')}\" (base {ctas.get('bottom')} de {ctas.get('H')} px)")
        linhas += [f"- PROBLEMA {x}" for x in probs] or ["- sem problemas"]
        linhas.append("")
        total += len(probs)
    linhas.insert(3, f"**Problemas encontrados: {total}**\n")
    rel = "\n".join(linhas)
    (OUT / "relatorio.md").write_text(rel, encoding="utf-8")
    (OUT / "relatorio.json").write_text(json.dumps({"estatico": est, "geral": geral, "navegador": nav}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(rel)


if __name__ == "__main__":
    main()
