#!/usr/bin/env python3
"""Padroniza cabeçalho, rodapé, faixa de prévia e "pular para o conteúdo" em todas as páginas.

Idempotente: na primeira vez troca o cabeçalho/rodapé próprio de cada página pelo padrão;
nas seguintes, reescreve só o que está entre os marcadores <!-- site:... --> e <!-- /site:... -->.
Também garante <link> de assets/css/site.css (depois do CSS da página) e <script> de assets/js/site.js.

Uso: python3 _dev/padronizar_layout.py
"""
import re
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent / "site"

PAGINAS = {
    "index.html": "inicio",
    "atendimentos.html": "atendimentos",
    "comunidade.html": "comunidade",
    "semana-bem-nutrida.html": "semana",
    "sobre.html": "sobre",
    "ferro.html": "ferro",
    "privacidade.html": "privacidade",
    "termos.html": "termos",
    "404.html": None,
}

MENU = [
    ("inicio", "./", "Início"),
    ("atendimentos", "atendimentos.html", "Atendimentos"),
    ("comunidade", "comunidade.html", "Comunidade"),
    ("semana", "semana-bem-nutrida.html", "Semana Bem Nutrida"),
    ("sobre", "sobre.html", "Sobre a Ana"),
]

RODAPE_PAGINAS = [
    ("inicio", "./", "Início", ""),
    ("atendimentos", "atendimentos.html", "Atendimentos", ""),
    ("comunidade", "comunidade.html", "Comunidade Bem Nutrida", ""),
    ("semana", "semana-bem-nutrida.html", "Semana Bem Nutrida", ""),
    ("ferro", "ferro.html", "Aula Ferro Sem Sofrimento", ' data-site-requer="aulaFerroPronta"'),
    ("sobre", "sobre.html", "Sobre a Ana", ""),
]


def atual(chave, pagina):
    return ' aria-current="page"' if chave == pagina else ""


def topo(pagina):
    itens = "\n".join(
        f'        <li><a class="site-nav__link" href="{href}"{atual(k, pagina)}>{txt}</a></li>'
        for k, href, txt in MENU
    )
    return f"""<!-- site:topo -->
<a class="site-pular" href="#conteudo">Pular para o conteúdo</a>
<div class="site-previa" id="faixa-previa" role="note"><span>Prévia em aprovação</span></div>
<header class="site-topo">
  <div class="site-wrap site-topo__linha">
    <a class="site-topo__logo" href="./" aria-label="Ana Paula Costa · Nutricionista, página inicial">
      <img src="assets/marca/logo-horizontal-reduzida-cor.svg" width="186" height="28" alt="">
    </a>
    <button class="site-topo__menu" type="button" aria-expanded="false" aria-controls="menu-site">
      <svg class="i-abrir" aria-hidden="true" focusable="false"><use href="assets/marca/sprite.svg#ui-menu"/></svg>
      <svg class="i-fechar" aria-hidden="true" focusable="false"><use href="assets/marca/sprite.svg#ui-x"/></svg>
      <span>Menu</span>
    </button>
    <nav class="site-nav" id="menu-site" aria-label="Principal">
      <ul class="site-nav__lista">
{itens}
      </ul>
      <div class="site-nav__extra">
        <a class="site-nav__cta" href="atendimentos.html#agendar" data-agendar>Agendar minha avaliação<svg viewBox="0 0 57.28 18.68" aria-hidden="true" focusable="false"><use href="assets/marca/sprite.svg#rota-seta"/></svg></a>
        <p class="site-nav__redes"><a href="https://www.instagram.com/ana_costarodrigues/" rel="noopener" aria-label="Instagram @ana_costarodrigues"><svg aria-hidden="true" focusable="false"><use href="assets/marca/sprite.svg#ui-instagram"/></svg></a><a href="https://www.tiktok.com/@ana_costarodrigues" rel="noopener" aria-label="TikTok @ana_costarodrigues"><svg class="preenchido" aria-hidden="true" focusable="false"><use href="assets/marca/sprite.svg#ui-tiktok"/></svg></a><span>@ana_costarodrigues</span></p>
      </div>
    </nav>
  </div>
</header>
<!-- /site:topo -->"""


def rodape(pagina):
    paginas = "\n".join(
        f'          <li{extra}><a href="{href}"{atual(k, pagina)}>{txt}</a></li>'
        for k, href, txt, extra in RODAPE_PAGINAS
    )
    return f"""<!-- site:rodape -->
<footer class="site-rodape">
  <div class="site-wrap">
    <div class="site-rodape__grade">
      <div class="site-rodape__marca">
        <img src="assets/marca/logo-horizontal-reduzida-sobre-escuro.svg" width="220" height="33" alt="Ana Paula Costa · Nutricionista" loading="lazy" decoding="async">
        <p class="site-rodape__ident">Ana Paula Costa · Nutricionista · <span class="pendente" data-site-crn>CRN em confirmação</span></p>
        <p>Atendimento online, por vídeo</p>
      </div>
      <div class="site-rodape__col">
        <h2 class="site-rodape__titulo">Contato</h2>
        <ul>
          <li><svg aria-hidden="true" focusable="false"><use href="assets/marca/sprite.svg#ui-whatsapp"/></svg><span class="pendente" data-site-contato="whatsapp">WhatsApp em confirmação</span></li>
          <li><svg aria-hidden="true" focusable="false"><use href="assets/marca/sprite.svg#ui-mail"/></svg><span class="pendente" data-site-contato="email">e-mail em confirmação</span></li>
          <li><svg aria-hidden="true" focusable="false"><use href="assets/marca/sprite.svg#ui-instagram"/></svg><a href="https://www.instagram.com/ana_costarodrigues/" rel="noopener">Instagram @ana_costarodrigues</a></li>
          <li><svg class="preenchido" aria-hidden="true" focusable="false"><use href="assets/marca/sprite.svg#ui-tiktok"/></svg><a href="https://www.tiktok.com/@ana_costarodrigues" rel="noopener">TikTok @ana_costarodrigues</a></li>
        </ul>
      </div>
      <nav class="site-rodape__col" aria-label="Páginas do site">
        <h2 class="site-rodape__titulo">Páginas</h2>
        <ul>
{paginas}
        </ul>
      </nav>
      <nav class="site-rodape__col" aria-label="Informações legais">
        <h2 class="site-rodape__titulo">Informações</h2>
        <ul>
          <li><a href="privacidade.html"{atual("privacidade", pagina)}>Política de Privacidade</a></li>
          <li><a href="termos.html"{atual("termos", pagina)}>Termos de Uso</a></li>
          <li><button type="button" class="site-rodape__botao" data-site-cookies>Preferências de cookies</button></li>
        </ul>
      </nav>
    </div>
    <div class="site-rodape__avisos">
      <ul>
        <li class="site-rodape__educativo">O conteúdo deste site é educativo e não substitui consulta individual com nutricionista, acompanhamento médico ou o seu pré-natal. Cada mulher responde de um jeito, e os resultados podem variar.</li>
        <li class="site-rodape__so-ferro">Nunca pare ou troque o suplemento receitado por conta própria. Leve suas dúvidas ao pré-natal.</li>
        <li>Materiais digitais trazem cardápios-exemplo e receitas. Plano alimentar individual só em consulta.</li>
        <li>As fotos deste site são reais. Não usamos inteligência artificial para criar pessoas ou resultados.</li>
        <li>Atendimento online conforme as regras de telenutrição do Conselho Federal de Nutricionistas. <span class="pendente" data-site-oculta-se="cadastroENutricionista">cadastro no e-Nutricionista em confirmação</span></li>
        <li>Seus dados são tratados conforme a Lei Geral de Proteção de Dados. Saiba como na <a href="privacidade.html">Política de Privacidade</a>.</li>
      </ul>
      <p class="site-rodape__final">© <span data-site-ano>2026</span> Ana Paula Costa Rodrigues · <span class="pendente" data-site-cfg="nomeVendedor">nome ou razão social em confirmação</span> · CPF/CNPJ <span class="pendente" data-site-cfg="cpfCnpj">em confirmação</span> · <span class="pendente" data-site-cfg="enderecoFiscal">endereço em confirmação</span></p>
    </div>
  </div>
</footer>
<!-- /site:rodape -->"""


def troca_marcado(html, nome, novo):
    pad = re.compile(rf"<!-- site:{nome} -->.*?<!-- /site:{nome} -->", re.S)
    if pad.search(html):
        return pad.sub(lambda m: novo, html, count=1), True
    return html, False


def processa(arq: Path, pagina):
    html = arq.read_text(encoding="utf-8")
    original = html

    html, ok = troca_marcado(html, "topo", topo(pagina))
    if not ok:
        # remove pular, faixa de prévia e cabeçalho próprios da página
        html = re.sub(r'<a class="[a-z]+-pular" href="#conteudo">[^<]*</a>\s*', "", html, count=1)
        html = re.sub(r'<div class="at-previa"[^>]*>.*?</div>\s*</div>\s*', "", html, count=1, flags=re.S)
        html = re.sub(r'<div class="[a-z]+-previa" id="faixa-previa"[^>]*>.*?</div>\s*', "", html, count=1, flags=re.S)
        html = re.sub(r"<!-- *\d+\. *Cabeçalho[^>]*-->\s*", "", html)
        html, n = re.subn(r'<header class="[a-z]+-topo"[^>]*>.*?</header>', lambda m: topo(pagina), html, count=1, flags=re.S)
        if not n:
            raise SystemExit(f"{arq.name}: cabeçalho não encontrado")

    html, ok = troca_marcado(html, "rodape", rodape(pagina))
    if not ok:
        html = re.sub(r"<!-- *\d+\. *Rodapé[^>]*-->\s*", "", html)
        html, n = re.subn(r'<footer class="[a-z]+-rodape"[^>]*>.*?</footer>', lambda m: rodape(pagina), html, count=1, flags=re.S)
        if not n:
            raise SystemExit(f"{arq.name}: rodapé não encontrado")

    # site.css depois do CSS da página
    if 'href="assets/css/site.css"' not in html:
        html, n = re.subn(r'(<link rel="stylesheet" href="assets/css/pagina-[a-z]+\.css">)',
                          r'\1\n<link rel="stylesheet" href="assets/css/site.css">', html, count=1)
        if not n:
            raise SystemExit(f"{arq.name}: CSS da página não encontrado")
    # site.js antes do JS da página
    if 'src="assets/js/site.js"' not in html:
        html, n = re.subn(r'(<script src="assets/js/pagina-[a-z]+\.js" defer></script>)',
                          r'<script src="assets/js/site.js" defer></script>\n\1', html, count=1)
        if not n:
            raise SystemExit(f"{arq.name}: JS da página não encontrado")

    if html != original:
        arq.write_text(html, encoding="utf-8")
        print("atualizado:", arq.name)
    else:
        print("sem mudança:", arq.name)


for nome, pagina in PAGINAS.items():
    processa(SITE / nome, pagina)
