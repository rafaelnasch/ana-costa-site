#!/usr/bin/env python3
"""Sincroniza a marca final (sistema Rota ap.) para o site.

Idempotente: pode rodar quantas vezes quiser; só reescreve o que mudou.
Origem: workspace/clientes-growai/ana-costa/identidade-visual/marca-final/
Destino: site/assets/{marca,fonts,img} + site/manifest.webmanifest

Uso:  python3 _dev/sync_marca.py [--origem CAMINHO]
Requer: fontTools + brotli (pip install --user fonttools brotli)
"""
import argparse, hashlib, json, re, shutil, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SITE = RAIZ / "site"
ASSETS = SITE / "assets"
ORIGEM_PADRAO = Path(
    "/Users/macbookprom5nasch/orca/workspaces/growaura-3/Ana-Costa-Nutri/"
    "workspace/clientes-growai/ana-costa/identidade-visual/marca-final"
)

MAR, CARAMELO, ALGODAO = "#103A40", "#C99A68", "#F2F0EB"

mudancas = []


def escrever(dest: Path, dados: bytes):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.read_bytes() == dados:
        return
    dest.write_bytes(dados)
    mudancas.append(str(dest.relative_to(RAIZ)))


def copiar(src: Path, dest: Path):
    escrever(dest, src.read_bytes())


# ---------------------------------------------------------------- logos
LOGOS = [
    # topo do site e rodapé
    "logo-horizontal-reduzida-cor", "logo-horizontal-reduzida-sobre-escuro", "logo-horizontal-reduzida-sobre-salvia",
    "logo-horizontal-cor", "logo-horizontal-sobre-escuro", "logo-horizontal-sobre-salvia",
    "logo-vertical-cor", "logo-vertical-sobre-escuro", "logo-vertical-sobre-salvia",
    "simbolo-cor", "simbolo-sobre-escuro", "simbolo-sobre-salvia",
    "assinatura-compacta-cor", "assinatura-compacta-sobre-escuro",
    "submarca-comunidade-bem-nutrida-cor", "submarca-comunidade-bem-nutrida-sobre-escuro", "submarca-comunidade-bem-nutrida-sobre-salvia",
    "submarca-semana-bem-nutrida-cor", "submarca-semana-bem-nutrida-sobre-escuro", "submarca-semana-bem-nutrida-sobre-salvia",
]

ROTA = [
    "rota-divisor", "rota-divisor-sobre-escuro", "rota-divisor-curto", "rota-divisor-salvia", "rota-divisor-curto-salvia", "rota-seta", "rota-seta-sobre-escuro",
    "moldura-arco-mascara", "moldura-arco-contorno", "padrao-fundo-claro", "padrao-fundo-escuro",
    "padrao-modulo-claro", "padrao-modulo-escuro",
]

ICONES = ["comece-aqui", "consulta", "comunidade", "gestacao", "pos-parto", "40-mais", "receitas", "depoimentos"]


def svg_interior(txt: str):
    vb = re.search(r'viewBox="([^"]+)"', txt).group(1)
    corpo = re.sub(r"^.*?<svg[^>]*>", "", txt, flags=re.S)
    corpo = re.sub(r"</svg>\s*$", "", corpo.strip())
    corpo = re.sub(r"<title>.*?</title>", "", corpo, flags=re.S)
    return vb, corpo


def recolorir(corpo: str) -> str:
    """Traço (Mar Fundo) vira currentColor; ponto (Caramelo) segue a variável --ponto do modo."""
    corpo = corpo.replace(f'fill="{MAR}"', 'fill="currentColor"')
    corpo = corpo.replace(f'fill="{CARAMELO}"', f'class="ponto-svg" style="fill:var(--ponto,{CARAMELO})"')
    corpo = re.sub(r'\s*transform="translate\(0\.0 0\.0\) scale\(1\.0\)"', "", corpo)
    # 1 casa decimal basta na tela e reduz o sprite em cerca de um terço
    corpo = re.sub(r"(\d+\.\d)\d+", r"\1", corpo)
    return corpo


# Ícones de interface (Lucide, licença ISC; TikTok de Simple Icons, CC0). Traço, 24 x 24.
UI = {
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "x": '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
    "menu": '<path d="M4 7h16"/><path d="M4 12h16"/><path d="M4 17h16"/>',
    "plus": '<path d="M5 12h14"/><path d="M12 5v14"/>',
    "chevron-down": '<path d="m6 9 6 6 6-6"/>',
    "instagram": '<rect width="20" height="20" x="2" y="2" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><path d="M17.5 6.5h.01"/>',
    "mail": '<rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
    "whatsapp": '<path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/><path d="M9.2 8.8c.2-.5.6-.6.9-.6h.4c.2 0 .3.1.4.3l.6 1.4c.1.2 0 .4-.1.5l-.4.5c-.1.1-.1.3 0 .4.5.9 1.2 1.6 2.1 2.1.1.1.3.1.4 0l.5-.4c.1-.1.3-.2.5-.1l1.4.6c.2.1.3.2.3.4v.4c0 .3-.1.7-.6.9-.6.3-1.5.4-2.6-.1-1.6-.7-2.9-2-3.6-3.6-.5-1.1-.4-2-.1-2.6Z"/>',
    "video": '<path d="m16 13 5.22 3.48a.5.5 0 0 0 .78-.42V7.87a.5.5 0 0 0-.75-.43L16 10.5"/><rect x="2" y="6" width="14" height="12" rx="2"/>',
    "calendar": '<path d="M8 2v4"/><path d="M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/>',
    "smartphone": '<rect width="14" height="20" x="5" y="2" rx="2" ry="2"/><path d="M12 18h.01"/>',
    "file-text": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "cart": '<circle cx="8" cy="21" r="1"/><circle cx="19" cy="21" r="1"/><path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"/>',
    "panela": '<path d="M2 12h20"/><path d="M20 12v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-8"/><path d="m4 8 16-4"/><path d="m8.86 6.78-.45-1.81a2 2 0 0 1 1.45-2.43l1.94-.48a2 2 0 0 1 2.43 1.46l.45 1.8"/>',
    "cartao-credito": '<rect width="20" height="14" x="2" y="5" rx="2"/><path d="M2 10h20"/>',
    "nota-fiscal": '<path d="M4 2v20l2-1 2 1 2-1 2 1 2-1 2 1 2-1 2 1V2l-2 1-2-1-2 1-2-1-2 1-2-1-2 1Z"/><path d="M16 8h-6a2 2 0 1 0 0 4h4a2 2 0 1 1 0 4H8"/><path d="M12 17.5v-11"/>',
    "pix": '<path d="m12 3 4.5 4.5a2 2 0 0 0 1.4.6H19"/><path d="M12 3 7.5 7.5a2 2 0 0 1-1.4.6H5"/><path d="m12 21 4.5-4.5a2 2 0 0 1 1.4-.6H19"/><path d="m12 21-4.5-4.5a2 2 0 0 0-1.4-.6H5"/><path d="m5 8.1-2.3 2.5a2 2 0 0 0 0 2.8L5 15.9"/><path d="m19 8.1 2.3 2.5a2 2 0 0 1 0 2.8L19 15.9"/><path d="M8.5 12h7"/>',
    "lock": '<rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    "play": '<path d="M7 4.5v15a.8.8 0 0 0 1.2.7l12-7.5a.8.8 0 0 0 0-1.4l-12-7.5A.8.8 0 0 0 7 4.5Z"/>',
    "coracao": '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>',
    "info": '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>',
    "seta-direita": '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
    "aspas": '<path d="M7 15c-1.7 0-3-1.3-3-3s1.3-3 3-3 3 1.3 3 3c0 3-2 5-4 6"/><path d="M17 15c-1.7 0-3-1.3-3-3s1.3-3 3-3 3 1.3 3 3c0 3-2 5-4 6"/>',
}
TIKTOK = '<path fill="currentColor" stroke="none" d="M12.53.02C13.84 0 15.14.01 16.44 0c.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03a10.4 10.4 0 0 1-4.2-.97c-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75a7.6 7.6 0 0 1-1.35 3.94 7.5 7.5 0 0 1-5.91 3.21 7.4 7.4 0 0 1-4.08-1.03 7.5 7.5 0 0 1-3.65-5.71c-.02-.5-.03-1-.01-1.49a7.5 7.5 0 0 1 2.58-4.96 7.4 7.4 0 0 1 6.15-1.72c.02 1.48-.04 2.96-.04 4.44a3.4 3.4 0 0 0-3.02.37 3.4 3.4 0 0 0-1.36 1.75c-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87a3.3 3.3 0 0 0 2.77-1.61c.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07Z"/>'


def gerar_sprite(origem: Path):
    simbolos = []
    for sid, corpo in UI.items():
        simbolos.append(f'<symbol id="ui-{sid}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">{corpo}</symbol>')
    simbolos.append(f'<symbol id="ui-tiktok" viewBox="0 0 24 24">{TIKTOK}</symbol>')
    fontes = {
        "rota-seta": origem / "forma-assinatura/rota-seta.svg",
        "rota-divisor": origem / "forma-assinatura/rota-divisor.svg",
        "rota-divisor-curto": origem / "forma-assinatura/rota-divisor-curto.svg",
        "simbolo": origem / "logo/svg/simbolo-cor.svg",
    }
    for nome in ICONES:
        fontes[f"icone-{nome}"] = origem / f"forma-assinatura/icones-destaques/icone-{nome}.svg"
    for sid, arq in fontes.items():
        vb, corpo = svg_interior(arq.read_text())
        simbolos.append(f'<symbol id="{sid}" viewBox="{vb}">{recolorir(corpo)}</symbol>')
    sprite = (
        '<svg xmlns="http://www.w3.org/2000/svg" aria-hidden="true">\n'
        "<!-- Gerado por _dev/sync_marca.py a partir da marca-final. Não editar à mão. -->\n"
        + "\n".join(simbolos)
        + "\n</svg>\n"
    )
    escrever(ASSETS / "marca/sprite.svg", sprite.encode())


# ---------------------------------------------------------------- tokens
def gerar_tokens(origem: Path):
    """Extrai de tokens.css só as variáveis (:root, modos por fase e ajustes de celular).

    As regras de fonte e de elementos ficam no site.css, com caminhos do site.
    """
    css = (origem / "tokens.css").read_text()
    blocos = []
    cab = css.splitlines()[0]
    for m in re.finditer(r"(@media[^{]+\{[^{}]*\{[^{}]*\}\s*\}|:root\{[^}]*\}|\[data-fase=\"[^\"]+\"\]\{[^}]*\})", css, re.S):
        bloco = m.group(1)
        if "--" not in bloco:
            continue
        blocos.append(bloco)
    texto = "\n".join(blocos)
    # aceita data-fase="40" como sinônimo de "40-mais"
    texto = texto.replace('[data-fase="40-mais"]', '[data-fase="40-mais"],[data-fase="40"]')
    saida = (
        f"{cab}\n/* Gerado por _dev/sync_marca.py a partir de marca-final/tokens.css. Não editar à mão. */\n"
        + texto + "\n"
    )
    escrever(ASSETS / "css/tokens.css", saida.encode())


# ---------------------------------------------------------------- fontes
def gerar_fontes(origem: Path):
    try:
        from fontTools.ttLib import TTFont
        from fontTools import subset
        from fontTools.varLib import instancer
        import brotli  # noqa: F401
    except ImportError as e:
        sys.exit(f"Falta dependência ({e}). Rode: python3 -m pip install --user fonttools brotli")

    # Latin básico + Latin-1 + pontuação tipográfica + seta + ordinal (nº)
    unicodes = list(range(0x20, 0x7F)) + list(range(0xA0, 0x100)) + [
        0x152, 0x153, 0x2013, 0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x2022, 0x2026, 0x20AC, 0x2192, 0x2122, 0x2009, 0x202F,
    ]
    alvos = [
        # arquivo origem, destino, limites de eixo
        ("fontes/Literata[opsz,wght].ttf", "literata-var.woff2", {"opsz": (24, 72), "wght": (400, 700)}),
        ("fontes/Literata-Italic[opsz,wght].ttf", "literata-italic-var.woff2", {"opsz": (24, 72), "wght": (400, 700)}),
        ("fontes/AtkinsonHyperlegibleNext[wght].ttf", "atkinson-next-var.woff2", {"wght": (400, 700)}),
        ("fontes/AtkinsonHyperlegibleNext-Italic[wght].ttf", "atkinson-next-italic-var.woff2", {"wght": (400, 700)}),
    ]
    for src, nome, eixos in alvos:
        arq = origem / src
        assinatura = hashlib.sha1(arq.read_bytes() + json.dumps(eixos).encode()).hexdigest()[:12]
        dest = ASSETS / "fonts" / nome
        marca = RAIZ / "_dev/.cache" / (nome + ".src")
        marca.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and marca.exists() and marca.read_text() == assinatura:
            continue
        f = TTFont(arq, lazy=False)
        opts = subset.Options()
        opts.flavor = "woff2"
        opts.layout_features = ["*"]
        opts.name_IDs = ["*"]
        opts.notdef_outline = True
        sub = subset.Subsetter(opts)
        sub.populate(unicodes=unicodes)
        sub.subset(f)
        f = instancer.instantiateVariableFont(f, dict(eixos), updateFontNames=False)
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_suffix(".tmp")
        f.flavor = "woff2"
        f.save(tmp)
        escrever(dest, tmp.read_bytes())
        tmp.unlink()
        marca.write_text(assinatura)
    for lic in ["OFL-Literata.txt", "OFL-AtkinsonHyperlegibleNext.txt"]:
        copiar(origem / "fontes" / lic, ASSETS / "fonts" / lic)


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--origem", default=str(ORIGEM_PADRAO))
    origem = Path(ap.parse_args().origem)
    if not origem.exists():
        sys.exit(f"Origem não encontrada: {origem}")

    for nome in LOGOS:
        copiar(origem / f"logo/svg/{nome}.svg", ASSETS / f"marca/{nome}.svg")
    for nome in ROTA:
        copiar(origem / f"forma-assinatura/{nome}.svg", ASSETS / f"marca/rota/{nome}.svg")
    for nome in ICONES:
        for suf in ("", "-sobre-escuro"):
            copiar(origem / f"forma-assinatura/icones-destaques/icone-{nome}{suf}.svg",
                   ASSETS / f"marca/icones/icone-{nome}{suf}.svg")

    # favicons e compartilhamento
    png = origem / "logo/png"
    copiar(origem / "logo/svg/favicon.svg", ASSETS / "marca/fav/favicon.svg")
    copiar(png / "favicon-16.png", ASSETS / "marca/fav/favicon-16.png")
    copiar(png / "favicon-32.png", ASSETS / "marca/fav/favicon-32.png")
    copiar(png / "favicon-180-apple-touch.png", ASSETS / "marca/fav/apple-touch-icon.png")
    copiar(png / "favicon-192.png", ASSETS / "marca/fav/icon-192.png")
    copiar(png / "favicon-512.png", ASSETS / "marca/fav/icon-512.png")
    copiar(png / "og-image-1200x630.png", ASSETS / "img/og-image.png")
    copiar(png / "avatar-instagram-512.png", ASSETS / "marca/avatar-512.png")

    manifest = {
        "name": "Ana Paula Costa · Nutricionista",
        "short_name": "Ana Paula Costa",
        "description": "Nutrição para cada fase da mulher: gestação, pós-parto e 40+.",
        "lang": "pt-BR",
        "start_url": "./",
        "scope": "./",
        "display": "browser",
        "background_color": ALGODAO,
        "theme_color": MAR,
        "icons": [
            {"src": "assets/marca/fav/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "assets/marca/fav/icon-512.png", "sizes": "512x512", "type": "image/png"},
            {"src": "assets/marca/fav/favicon.svg", "sizes": "any", "type": "image/svg+xml"},
        ],
    }
    escrever(SITE / "manifest.webmanifest", (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode())

    gerar_sprite(origem)
    gerar_tokens(origem)
    gerar_fontes(origem)

    if mudancas:
        print(f"{len(mudancas)} arquivo(s) atualizado(s):")
        for m in mudancas:
            print("  ", m)
    else:
        print("Marca já sincronizada. Nada mudou.")


if __name__ == "__main__":
    main()
