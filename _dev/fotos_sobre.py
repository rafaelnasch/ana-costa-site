#!/usr/bin/env python3
"""Fotos extras da página Sobre (complementa _dev/fotos.py sem mexer no fotos.json compartilhado).

Saída: site/assets/img/fotos/<id>-<largura>.{webp,avif} + site/assets/img/fotos-sobre.json
Idempotente. Regras: só a Ana no quadro (recorte tira as outras pessoas do box), sem filhos, sem IA.
Uso: python3 _dev/fotos_sobre.py
"""
import json
from pathlib import Path
from PIL import Image, features

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "site/assets/img/fotos"
JSON = RAIZ / "site/assets/img/fotos-sobre.json"
PESQ = Path("/Users/macbookprom5nasch/orca/workspaces/growaura-3/Ana-Costa-Nutri/"
            "workspace/clientes-growai/ana-costa/identidade-visual/_pesquisa")

# caixa = (x0, y0, x1, y1) em pixels da origem
FOTOS = [
    dict(id="crossfit", src="fotos/22-crossfit-kettlebell-acima-da-cabeca.jpg", caixa=(328, 28, 760, 604),
         larguras=[320, 432],
         alt="Ana Paula Costa no box de crossfit, de regata azul-marinho, erguendo um kettlebell acima da cabeça com os braços estendidos",
         uso="Sobre, capítulo 3 (atleta). Recorte fechado: só a Ana no quadro"),
]


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    tem_avif = features.check("avif")
    saida = {"_nota": "Gerado por _dev/fotos_sobre.py. Fotos reais da Ana; só ela no quadro.", "fotos": {}}
    for f in FOTOS:
        img = Image.open(PESQ / f["src"]).convert("RGB").crop(f["caixa"])
        w0, h0 = img.size
        fmts = ["webp"] + (["avif"] if tem_avif else [])
        for w in f["larguras"]:
            h = round(h0 * w / w0)
            r = img.resize((w, h), Image.LANCZOS)
            for fmt in fmts:
                dest = SAIDA / f"{f['id']}-{w}.{fmt}"
                tmp = dest.with_suffix(".tmp." + fmt)
                r.save(tmp, fmt.upper(), quality=82 if fmt == "webp" else 58)
                if dest.exists() and dest.read_bytes() == tmp.read_bytes():
                    tmp.unlink()
                else:
                    tmp.replace(dest)
        wmax = f["larguras"][-1]
        saida["fotos"][f["id"]] = dict(id=f["id"], alt=f["alt"], uso=f["uso"], origem=f["src"],
                                       width=wmax, height=round(h0 * wmax / w0), larguras=f["larguras"], formatos=fmts)
    novo = json.dumps(saida, ensure_ascii=False, indent=2) + "\n"
    if not JSON.exists() or JSON.read_text() != novo:
        JSON.write_text(novo)
    print(novo)


if __name__ == "__main__":
    main()
