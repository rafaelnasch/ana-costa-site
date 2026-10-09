#!/usr/bin/env python3
"""Seleciona, recorta e exporta as fotos reais da Ana para o site.

Saída: site/assets/img/fotos/<id>-<largura>.{webp,avif} + site/assets/img/fotos.json
Idempotente: só regrava quando a receita (origem + recorte + qualidade) muda.

Regras (marca-final §9 e briefing do site):
  - só fotos reais da Ana, sem filhos nem outras pessoas (autorização pendente);
  - nada de mão na barriga em peça da marca;
  - modo 40+ usa foto sem gestação;
  - nenhuma imagem de IA de pessoa.

Uso: python3 _dev/fotos.py [--forcar] [--prova]   (--prova gera _dev/qa/fotos-prova.jpg)
"""
import argparse, hashlib, json, sys
from pathlib import Path
from PIL import Image, ImageOps, features

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "site/assets/img/fotos"
JSON = RAIZ / "site/assets/img/fotos.json"
CACHE = RAIZ / "_dev/.cache/fotos.json"
PESQ = Path(
    "/Users/macbookprom5nasch/orca/workspaces/growaura-3/Ana-Costa-Nutri/"
    "workspace/clientes-growai/ana-costa/identidade-visual/_pesquisa"
)
LARGURAS = [480, 800, 1200, 1600]
Q_WEBP, Q_AVIF = 82, 58

# recorte = (x0, y0, x1) em fração da imagem; a altura sai da proporção.
FOTOS = [
    dict(id="hero", src="drive/ensaio-profissional-gravida/IMG_9616.jpg", prop=(4, 5), recorte=(0.04, 0.20, 0.96),
         alt="Ana Paula Costa sorrindo, sentada num sofá claro com o notebook no colo, de camisa branca, numa sala iluminada com uma planta ao fundo",
         uso="Hero da home e chamadas finais (moldura em arco)", fase="todas"),
    dict(id="hero-mobile", src="drive/ensaio-profissional-gravida/IMG_9616.jpg", prop=(1, 1), recorte=(0.08, 0.255, 0.92),
         alt="Ana Paula Costa sorrindo, sentada num sofá claro com o notebook no colo, de camisa branca",
         uso="Hero no celular (vem depois do botão)", fase="todas"),
    dict(id="retrato-oculos", src="fotos/03-retrato-escritorio-notebook-oculos-sorrindo.jpg", prop=(4, 5), recorte=(0.0, 0.03, 1.0),
         alt="Ana Paula Costa de óculos, sorrindo com a mão no rosto, diante do notebook no escritório, com um mapa-múndi na parede",
         uso="Hero de Sobre, Atendimentos e Semana Bem Nutrida; retrato sem gestação", fase="todas, inclusive 40+"),
    dict(id="atendimento-online", src="fotos/04-selfie-trabalhando-notebook-sorrindo.jpg", prop=(4, 5), recorte=(0.38, 0.0, 1.0),
         alt="Ana Paula Costa de óculos, sorrindo para a câmera, em casa",
         uso="Como funciona o atendimento online", fase="todas, inclusive 40+"),
    dict(id="formatura", src="fotos/15-formatura-nutricao-diploma-pao-de-acucar.jpg", prop=(4, 5), recorte=(0.10, 0.0, 0.90),
         alt="Ana Paula Costa de beca, segurando o diploma de Nutrição, com o Pão de Açúcar ao fundo",
         uso="Sobre (a virada de rota) e bloco de credenciais", fase="todas"),
    dict(id="gestante-ar-livre", src="drive/ensaio-gestante-antonio/IMG_0188.jpg", prop=(4, 5), recorte=(0.20, 0.235, 0.80),
         alt="Ana Paula Costa grávida, de camisa branca aberta, encostada numa parede de pedra ao ar livre, sorrindo",
         uso="Gestação (cartão, comunidade, ferro)", fase="gestacao"),
    dict(id="gestacao-janela", src="drive/ensaio-profissional-gravida/IMG_9601.jpg", prop=(4, 5), recorte=(0.0, 0.14, 1.0),
         alt="Ana Paula Costa grávida, de camisa branca, segurando um copo de água perto da janela e olhando para fora",
         uso="Cartão Gestação e aula do ferro", fase="gestacao"),
    dict(id="gestacao-janela-sorriso", src="drive/ensaio-profissional-gravida/IMG_9606.jpg", prop=(4, 5), recorte=(0.0, 0.12, 1.0),
         alt="Ana Paula Costa grávida, de camisa branca, segurando um copo de água perto da janela e sorrindo para a câmera",
         uso="Gestação, alternativa", fase="gestacao"),
    dict(id="retrato-evento", src="drive/evento-nutricao/v2_fab6801d.jpg", prop=(4, 5), recorte=(0.0, 0.06, 1.0),
         alt="Retrato de Ana Paula Costa sorrindo, de blazer preto, com a mão no queixo, diante de um fundo escuro",
         uso="Modo 40+ e menopausa (sem gestação)", fase="40-mais"),
    dict(id="retrato-evento-bracos", src="drive/evento-nutricao/v2_a46a45b0.jpg", prop=(4, 5), recorte=(0.0, 0.06, 1.0),
         alt="Retrato de Ana Paula Costa sorrindo, de blazer preto e braços cruzados, diante de um fundo escuro",
         uso="Modo 40+, alternativa", fase="40-mais"),
    dict(id="retrato-close", src="drive/ensaio-profissional-gravida/IMG_9675.jpg", prop=(4, 5), recorte=(0.0, 0.12, 1.0),
         alt="Ana Paula Costa de camisa jeans, com as mãos unidas perto do rosto, sorrindo para a câmera",
         uso="Chamadas finais, Sobre, 40+ (close sem barriga)", fase="todas, inclusive 40+"),
    dict(id="poltrona-notebook", src="drive/ensaio-profissional-gravida/IMG_9611.jpg", prop=(4, 5), recorte=(0.0, 0.16, 1.0),
         alt="Ana Paula Costa sentada num sofá claro com o notebook, numa sala com planta e luz natural",
         uso="Como funciona, atendimento", fase="todas"),
    dict(id="tablet", src="drive/ensaio-profissional-gravida/IMG_9621.jpg", prop=(4, 5), recorte=(0.0, 0.17, 1.0),
         alt="Ana Paula Costa sorrindo enquanto olha um tablet, sentada num sofá claro ao lado de uma planta",
         uso="Plano no aplicativo, acompanhamento", fase="todas"),
    dict(id="livro", src="drive/ensaio-profissional-gravida/IMG_9579.jpg", prop=(4, 5), recorte=(0.0, 0.05, 1.0),
         alt="Ana Paula Costa de camiseta branca e calça jeans, segurando um livro aberto numa sala clara",
         uso="Conteúdos, Semana Bem Nutrida", fase="gestacao"),
    dict(id="retrato-perfil", src="fotos/00-foto-de-perfil-atual.jpg", prop=(1, 1), recorte=(0.0, 0.0, 1.0),
         alt="Retrato de estúdio de Ana Paula Costa, de blusa caramelo, sorrindo de leve diante de um fundo cinza claro",
         uso="Avatar de autora, assinatura de texto, depoimento da Ana", fase="todas, inclusive 40+"),
]


def receita(f):
    return hashlib.sha1(json.dumps([f["src"], f["prop"], f["recorte"], LARGURAS, Q_WEBP, Q_AVIF]).encode()).hexdigest()[:12]


def recortar(f):
    im = ImageOps.exif_transpose(Image.open(PESQ / f["src"])).convert("RGB")
    W, H = im.size
    x0, y0, x1 = f["recorte"]
    pw, ph = f["prop"]
    larg = (x1 - x0) * W
    alt = larg * ph / pw
    top = y0 * H
    if top + alt > H:  # encaixa sem sair da imagem
        alt = H - top
        larg = alt * pw / ph
    box = (round(x0 * W), round(top), round(x0 * W + larg), round(top + alt))
    return im.crop(box)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--forcar", action="store_true")
    ap.add_argument("--prova", action="store_true")
    a = ap.parse_args()
    avif = features.check("avif")
    SAIDA.mkdir(parents=True, exist_ok=True)
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    saida, provas, feitos = {}, [], 0
    for f in FOTOS:
        crop = recortar(f)
        cw, ch = crop.size
        larguras = [w for w in LARGURAS if w <= cw] or [cw]
        if cw > larguras[-1] and cw < LARGURAS[-1]:
            larguras.append(cw)  # aproveita a resolução máxima da fonte
        r = receita(f)
        if a.forcar or cache.get(f["id"]) != r or not all((SAIDA / f"{f['id']}-{w}.webp").exists() for w in larguras):
            for w in larguras:
                h = round(w * ch / cw)
                im = crop.resize((w, h), Image.LANCZOS)
                im.save(SAIDA / f"{f['id']}-{w}.webp", "WEBP", quality=Q_WEBP, method=6)
                if avif:
                    im.save(SAIDA / f"{f['id']}-{w}.avif", "AVIF", quality=Q_AVIF, speed=4)
            cache[f["id"]] = r
            feitos += 1
        maior = larguras[-1]
        altura = round(maior * ch / cw)
        srcset_webp = ", ".join(f"assets/img/fotos/{f['id']}-{w}.webp {w}w" for w in larguras)
        srcset_avif = ", ".join(f"assets/img/fotos/{f['id']}-{w}.avif {w}w" for w in larguras) if avif else ""
        padrao = min(larguras, key=lambda w: abs(w - 800))
        saida[f["id"]] = {
            "id": f["id"],
            "alt": f["alt"],
            "uso": f["uso"],
            "fase": f["fase"],
            "origem": f["src"],
            "proporcao": f"{f['prop'][0]}/{f['prop'][1]}",
            "width": maior,
            "height": altura,
            "larguras": larguras,
            "formatos": ["avif", "webp"] if avif else ["webp"],
            "src": f"assets/img/fotos/{f['id']}-{padrao}.webp",
            "srcset_webp": srcset_webp,
            "srcset_avif": srcset_avif,
            "html": (
                "<picture>"
                + (f'<source type="image/avif" srcset="{srcset_avif}" sizes="(min-width: 960px) 40vw, 92vw">' if avif else "")
                + f'<source type="image/webp" srcset="{srcset_webp}" sizes="(min-width: 960px) 40vw, 92vw">'
                + f'<img src="assets/img/fotos/{f["id"]}-{padrao}.webp" width="{maior}" height="{altura}" alt="{f["alt"]}" loading="lazy" decoding="async">'
                + "</picture>"
            ),
        }
        if a.prova:
            t = crop.copy()
            t.thumbnail((300, 380))
            provas.append((f["id"], t))
    JSON.write_text(json.dumps({"_nota": "Gerado por _dev/fotos.py. Fotos reais da Ana, uso sujeito à autorização dela. Sem filhos nem outras pessoas.", "fotos": saida}, ensure_ascii=False, indent=2) + "\n")
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(cache, indent=2))
    print(f"{len(FOTOS)} fotos no catálogo; {feitos} reprocessada(s). AVIF: {'sim' if avif else 'não'}.")
    if a.prova:
        from PIL import ImageDraw
        cols = 5
        rows = (len(provas) + cols - 1) // cols
        s = Image.new("RGB", (cols * 310, rows * 410), "white")
        d = ImageDraw.Draw(s)
        for i, (n, t) in enumerate(provas):
            x, y = (i % cols) * 310, (i // cols) * 410
            s.paste(t, (x + 5, y + 5))
            d.text((x + 5, y + 390), n, fill="black")
        (RAIZ / "_dev/qa").mkdir(parents=True, exist_ok=True)
        s.save(RAIZ / "_dev/qa/fotos-prova.jpg", quality=85)
        print("Prova: _dev/qa/fotos-prova.jpg")


if __name__ == "__main__":
    sys.exit(main())
