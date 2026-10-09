#!/usr/bin/env python3
"""Gera site/privacidade.html, site/termos.html, site/404.html e site/legal.html.

Fonte do texto: _projeto/conteudo/legal.md (sem as notas internas).
Os marcadores {{...}} viram spans .pendente preenchidos por assets/js/pagina-legal.js a partir do CONFIG.
Idempotente: rode de novo depois de editar este arquivo.  python3 _dev/gerar_legal.py
"""
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent / "site"
URL = "https://rafaelnasch.github.io/ana-costa-site/"

# ---------------------------------------------------------------- marcadores
def P(chave, texto):
    return f'<span data-cfg="{chave}" class="pendente">{texto}</span>'

CRN = '<span data-crn class="pendente">CRN em confirmação</span>'
EMAIL = '<span data-contato="email" class="pendente">e‑mail em confirmação</span>'
WHATS = '<span data-contato="whatsapp" class="pendente">número em confirmação</span>'
CPF = P("cpfCnpj", "CPF/CNPJ em confirmação")
END = P("enderecoFiscal", "endereço em confirmação")
DATA = P("dataAtualizacao", "data definida na publicação")

def ico(nome, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<svg{c} aria-hidden="true" focusable="false"><use href="assets/marca/sprite.svg#{nome}"/></svg>'

SETA = '<svg class="lg-seta" viewBox="-1.06 2.66 57.28 18.68" aria-hidden="true" focusable="false"><use href="assets/marca/sprite.svg#rota-seta"/></svg>'

def traco(rotulo=False):
    return ('<svg class="lg-traco" viewBox="0 -3.6 600 32.14" width="600" height="32" aria-hidden="true" focusable="false">'
            '<path class="lg-traco-linha" d="M574.95 8.45C573.37 9.26 569.4 11.32 568.18 11.98C567.11 12.56 560.83 15.71 560.75 15.71C560.72 15.71 559.25 16.36 557.52 17.17C545.17 22.87 535.44 25.06 522.38 25.06C511.9 25.04 507.61 23.97 496.51 18.61C488.71 14.84 484.87 13.33 479.4 11.9C474.4 10.59 470.65 9.97 464.76 9.45C460.88 9.11 0.22 9.17 -0.13 9.52C-0.59 9.98 0.16 10.59 2.05 11.26L2.95 11.58L234.29 11.67C482.88 11.75 466.22 11.69 471.14 12.38C476.05 13.06 481.56 14.56 485.24 16.23C485.66 16.42 486.03 16.58 486.07 16.58C486.2 16.58 489.46 18.12 493.58 20.12C495.16 20.88 496.48 21.51 496.51 21.51C496.53 21.51 496.97 21.7 497.48 21.93C503.39 24.65 509.57 26.32 517.16 27.26C519.83 27.6 530.66 27.64 533.9 27.33C539.31 26.83 544.43 25.94 548.54 24.81C549.43 24.57 550.27 24.35 550.43 24.31C551.2 24.12 554.98 22.84 556.59 22.22C559.24 21.2 560.11 20.83 563.33 19.32C565.98 18.09 579.56 9.26 579.56 8.78C579.56 7.72 576.79 7.52 574.95 8.45Z"/>'
            '<circle class="lg-traco-ponto" cx="591.9" cy="4" r="6.6"/></svg>')

# ---------------------------------------------------------------- moldura comum
def head(titulo, descricao, caminho, extra_ld, preload_img="", base_dinamica=False):
    base = ""
    if base_dinamica:
        # 404 do GitHub Pages é servido em qualquer profundidade: fixa a base antes de qualquer recurso relativo
        base = ('<script>(function(){var p=location.pathname,b=p.indexOf("/ana-costa-site/")===0?"/ana-costa-site/":(location.protocol==="file:"?"":"/");'
                'if(b)document.write(\'<base href="\'+b+\'">\');})();</script>\n')
    return f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{base}<title>{titulo}</title>
<meta name="description" content="{descricao}">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#103A40">
<link rel="canonical" href="{URL}{caminho}">

<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="Ana Paula Costa · Nutricionista">
<meta property="og:title" content="{titulo}">
<meta property="og:description" content="{descricao}">
<meta property="og:url" content="{URL}{caminho}">
<meta property="og:image" content="{URL}assets/img/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Monograma ap. de Ana Paula Costa, nutricionista, com o traço da rota e o ponto caramelo">
<meta name="twitter:card" content="summary_large_image">

<link rel="icon" href="assets/marca/fav/favicon.svg" type="image/svg+xml">
<link rel="icon" href="assets/marca/fav/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="assets/marca/fav/apple-touch-icon.png">
<link rel="manifest" href="manifest.webmanifest">

<link rel="preload" href="assets/fonts/literata-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/atkinson-next-var.woff2" as="font" type="font/woff2" crossorigin>
{preload_img}<link rel="stylesheet" href="assets/css/tokens.css">
<link rel="stylesheet" href="assets/css/pagina-legal.css">

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@graph": [
    {{
      "@type": "Person",
      "@id": "{URL}#ana",
      "name": "Ana Paula Costa",
      "jobTitle": "Nutricionista",
      "description": "Nutricionista que atende mulheres online, na gestação, no pós-parto e depois dos 40.",
      "knowsAbout": ["Nutrição na gestação", "Nutrição no pós-parto e na amamentação", "Nutrição no climatério e na menopausa"],
      "sameAs": ["https://www.instagram.com/ana_costarodrigues/", "https://www.tiktok.com/@ana_costarodrigues"]
    }},
    {{
      "@type": "ProfessionalService",
      "@id": "{URL}#servico",
      "name": "Ana Paula Costa · Nutricionista",
      "description": "Atendimento nutricional online, por vídeo, para mulheres na gestação, no pós-parto e amamentação, e depois dos 40 e na menopausa.",
      "url": "{URL}",
      "founder": {{"@id": "{URL}#ana"}},
      "availableLanguage": "pt-BR",
      "image": "{URL}assets/img/og-image.png"
    }}{extra_ld}
  ]
}}
</script>
<script src="assets/js/config.js"></script>
<script>document.documentElement.classList.add("js");window.dataLayer = window.dataLayer || [];</script>
</head>
'''

TOPO = '''<a class="lg-pular" href="#conteudo">Pular para o conteúdo</a>
<div class="lg-previa" id="faixa-previa" role="note"><span>Prévia em aprovação</span></div>

<header class="lg-topo">
  <div class="lg-wrap">
    <a class="lg-logo" href="./" aria-label="Ana Paula Costa · Nutricionista, página inicial">
      <img src="assets/marca/logo-horizontal-reduzida-cor.svg" width="176" height="26" alt="Ana Paula Costa · Nutricionista">
    </a>
    <nav aria-label="Principal">
      <ul>
        <li><a href="atendimentos.html">Atendimentos</a></li>
        <li><a href="comunidade.html">Comunidade</a></li>
        <li><a href="sobre.html">Sobre a Ana</a></li>
      </ul>
    </nav>
  </div>
</header>
'''

def rodape(aviso_extra=""):
    return f'''
<footer class="lg-rodape">
  <div class="lg-wrap">
    <div class="lg-rodape-topo">
      <div>
        <img src="assets/marca/logo-horizontal-reduzida-sobre-escuro.svg" width="220" height="33" alt="Ana Paula Costa · Nutricionista" loading="lazy" decoding="async">
        <p class="lg-id">Ana Paula Costa · Nutricionista · {CRN}</p>
        <p>Atendimento online · {EMAIL}</p>
      </div>
      <div>
        <h2>Contato</h2>
        <ul>
          <li>{ico("ui-whatsapp")}<span data-contato="whatsapp" data-prefixo="WhatsApp " class="pendente">WhatsApp em confirmação</span></li>
          <li>{ico("ui-instagram")}<a href="https://www.instagram.com/ana_costarodrigues/" rel="noopener">Instagram @ana_costarodrigues</a></li>
          <li>{ico("ui-tiktok")}<a href="https://www.tiktok.com/@ana_costarodrigues" rel="noopener">TikTok @ana_costarodrigues</a></li>
        </ul>
      </div>
      <nav aria-label="Rodapé">
        <h2>Páginas</h2>
        <ul>
          <li><a href="privacidade.html">Política de Privacidade</a></li>
          <li><a href="termos.html">Termos de Uso</a></li>
          <li><button type="button" class="lg-rodape-botao" data-cookies>Preferências de cookies</button></li>
        </ul>
      </nav>
    </div>
    <p class="lg-rodape-aviso">O conteúdo deste site é educativo e não substitui consulta individual com nutricionista, acompanhamento médico ou o seu pré-natal. Cada mulher responde de um jeito, e os resultados podem variar.{aviso_extra}</p>
    <p class="lg-rodape-final">© <span data-ano>2026</span> Ana Paula Costa Rodrigues · CPF/CNPJ {P("cpfCnpj", "em confirmação")} · {END}</p>
  </div>
</footer>

<div class="lg-toast" id="aviso-previa" role="status" aria-live="polite"></div>
<script src="assets/js/pagina-legal.js" defer></script>
</body>
</html>
'''

def botao(posicao, id_=""):
    i = f' id="{id_}"' if id_ else ""
    return (f'<a class="lg-botao" href="#"{i} data-mailto="Meus dados pessoais" data-posicao="{posicao}">'
            f'Falar sobre os meus dados {SETA}</a>')

AVATAR_FOTO = '<div class="lg-avatar"><picture><source type="image/avif" srcset="assets/img/fotos/retrato-perfil-480.avif 480w" sizes="84px"><source type="image/webp" srcset="assets/img/fotos/retrato-perfil-480.webp 480w" sizes="84px"><img src="assets/img/fotos/retrato-perfil-480.webp" width="965" height="965" alt="Ana Paula Costa, nutricionista" loading="lazy" decoding="async"></picture></div>'
# Termos usa o monograma: cada foto aparece em no máximo 2 páginas (retrato-perfil já está em Privacidade e na Semana)
AVATAR_SIMBOLO = '<div class="lg-avatar lg-avatar--simbolo"><svg viewBox="0 0 133.119 90.634" aria-hidden="true" focusable="false"><use href="assets/marca/sprite.svg#simbolo"/></svg></div>'

def fecho(foto=True):
    return f'''
  <section class="lg-fecho" aria-labelledby="fecho-titulo">
    <div class="lg-wrap">
      <div class="lg-fecho-caixa anima-traco">
        {traco()}
        {AVATAR_FOTO if foto else AVATAR_SIMBOLO}
        <h2 id="fecho-titulo">Ficou alguma dúvida?</h2>
        <p class="lg-lead">Pode perguntar. Prefiro responder uma pergunta a mais do que ver você marcar uma caixinha sem entender.</p>
        <div class="lg-acao">
          {botao("final")}
          <p class="lg-micro">Ana Paula Costa · Nutricionista · {CRN}</p>
        </div>
      </div>
    </div>
  </section>
'''

def item(id_, num, titulo, corpo, attrs=""):
    return f'''
          <section class="lg-item" id="{id_}" aria-labelledby="{id_}-t"{attrs}>
            <h3 id="{id_}-t"><span class="lg-num">{num}</span><span>{titulo}</span></h3>
{corpo}
          </section>'''

def indice_grupo(href, titulo, itens):
    lis = "\n".join(f'                <li><a href="#{i}"><span>{n}</span><span>{t}</span></a></li>' for i, n, t in itens)
    return f'''            <div class="lg-indice-grupo">
              <a class="lg-indice-grupo-titulo" href="#{href}">{titulo}</a>
              <ol>
{lis}
              </ol>
            </div>'''

def indice(grupos, outro):
    return f'''        <details class="lg-indice" open>
          <summary><span class="lg-indice-cabeca">Nesta página {ico("ui-chevron-down")}</span></summary>
          <nav class="lg-indice-corpo" aria-label="Sumário desta página">
{grupos}
            <div class="lg-indice-outro">{outro}</div>
          </nav>
        </details>'''

# ================================================================ PRIVACIDADE
priv_itens = [
    ("quem-e-a-responsavel", "1.1", "Quem é a responsável pelos seus dados"),
    ("quais-dados", "1.2", "Quais dados eu peço e quando"),
    ("para-que-uso", "1.3", "Para que eu uso cada dado"),
    ("compartilhamento", "1.4", "Com quem os dados são compartilhados"),
    ("automacao", "1.5", "Atendimento com apoio de automação"),
    ("por-quanto-tempo", "1.5", "Por quanto tempo eu guardo seus dados"),
    ("como-protejo", "1.6", "Como eu protejo seus dados"),
    ("seus-direitos", "1.7", "Seus direitos"),
    ("menores", "1.8", "Menores de idade"),
    ("mudancas-politica", "1.9", "Mudanças nesta política"),
]

def linha(para, dados, base, se=""):
    a = f' data-se="{se}" hidden' if se else ""
    return (f'                <tr{a}><th scope="row">{para}</th>'
            f'<td data-rotulo="Quais dados">{dados}</td><td data-rotulo="Com base em quê">{base}</td></tr>')

tabela = "\n".join([
    linha("Responder você, enviar o material que você pediu e liberar o link do grupo", "Nome, WhatsApp, e-mail", "Seu consentimento (art. 7º, I)"),
    linha("Saber a sua fase para mandar o material e as mensagens certas", "Fase (gestação, pós-parto, 40+, menopausa)", "Seu consentimento específico e destacado, porque a fase pode revelar dado de saúde (art. 11, I)"),
    linha("Enviar a leitura do Diagnóstico da Fase e conversar sobre o atendimento", "Respostas do questionário, nome, WhatsApp", "Seu consentimento específico e destacado para dado sensível (art. 11, I)", se="diagnosticoFase"),
    linha("Agendar, confirmar e lembrar a sua consulta", "Nome, WhatsApp, e-mail, data e horário", "Procedimentos para o serviço que você pediu (art. 7º, V)"),
    linha("Fazer a consulta, montar o plano e acompanhar você", "Dados de saúde do prontuário", "Tutela da saúde em atendimento feito por profissional de saúde (art. 11, II, “f”) e cumprimento do dever legal de manter prontuário (art. 11, II, “a”)"),
    linha("Cobrar, emitir nota fiscal e recibo para reembolso", "Nome, CPF, e-mail, dados da compra", "Obrigação legal e fiscal (art. 7º, II) e execução do contrato (art. 7º, V)"),
    linha("Liberar o acesso ao produto digital e à comunidade", "Nome, e-mail, WhatsApp", "Execução do contrato (art. 7º, V)"),
    linha("Mandar conteúdos, receitas e novidades", "Nome, WhatsApp, e-mail", "Seu consentimento opcional, separado do primeiro (art. 7º, I)"),
    linha("Entender quais páginas e posts são mais visitados", "Dados de navegação, sem dado de saúde", "Seu consentimento para cookies de análise e anúncios (art. 7º, I)"),
])

priv_corpo = "".join([
    item("quem-e-a-responsavel", "1.1", "Quem é a responsável pelos seus dados", f'''            <p>Sou eu. Na Lei Geral de Proteção de Dados (LGPD), o nome técnico disso é “controladora”.</p>
            <ul class="lg-lista-ficha">
              <li><strong>Ana Paula Costa Rodrigues</strong>, nutricionista, {CRN}</li>
              <li>CPF/CNPJ: {P("cpfCnpj", "em confirmação")}</li>
              <li>Endereço para correspondência: {END}</li>
              <li>E-mail para assuntos de dados pessoais: {EMAIL}</li>
            </ul>
            <p>Os pedidos sobre seus dados eu mesma respondo. Ficou com dúvida? Escreva para {EMAIL}.</p>'''),
    item("quais-dados", "1.2", "Quais dados eu peço e quando", f'''            <p class="lg-subtitulo">Quando você se inscreve em um material gratuito, entra no grupo ou pede para agendar:</p>
            <p>nome, WhatsApp, e-mail e a fase em que você está (por exemplo: gestação, pós-parto, 40+ ou menopausa). No agendamento, também o melhor período para a consulta.<br>Parece pouco, mas contar que está grávida ou na menopausa já diz algo sobre a sua saúde. Por isso a fase recebe o mesmo cuidado que eu dou a qualquer dado de saúde.</p>
            <div data-se="diagnosticoFase" hidden>
              <p class="lg-subtitulo">Quando você responde ao Diagnóstico da Fase (o questionário curto do site):</p>
              <p>além do nome e do WhatsApp, as respostas que você escolhe dar sobre a sua fase, o que mais te incomoda na alimentação, o que já tentou e quanto tempo tem para cozinhar. Algumas respostas podem dizer algo sobre a sua saúde. Por isso eu só uso o que você respondeu com a sua autorização, e só para duas coisas: mandar a leitura da sua fase e conversar com você sobre o atendimento.</p>
            </div>
            <p class="lg-subtitulo">Quando você compra um produto digital ou assina a comunidade:</p>
            <p>nome, e-mail, WhatsApp, CPF (quando exigido para a nota fiscal ou para o pagamento) e os dados da compra. O número do cartão você digita direto na plataforma de pagamento. Eu não vejo e não guardo.</p>
            <p class="lg-subtitulo">Quando você faz consulta comigo:</p>
            <p>aí sim entram informações de saúde: histórico, rotina, exames, medicações, suplementos e o que for necessário para montar o seu plano. Elas ficam no seu prontuário, protegidas pelo sigilo profissional, e são usadas só para o seu cuidado.</p>
            <p class="lg-subtitulo">Quando você navega pelo site:</p>
            <p>dados técnicos, como tipo de aparelho, navegador, páginas visitadas e de onde você chegou (um post do Instagram, por exemplo). Explico melhor em <a href="#cookies">Cookies</a>, lá embaixo.</p>
            <p class="lg-destaque"><strong>O que eu não peço no site:</strong> exames, peso, diagnóstico ou lista de remédios. Isso é conversa de consulta.</p>'''),
    item("para-que-uso", "1.3", "Para que eu uso cada dado", f'''            <p>A lei pede que eu diga, para cada uso, em que regra ele se apoia. Está tudo aqui:</p>
            <div class="lg-tabela-wrap">
              <table class="lg-tabela">
                <caption class="lg-vh">Para que cada dado é usado e em que regra da LGPD o uso se apoia</caption>
                <thead><tr><th scope="col">Para quê</th><th scope="col">Quais dados</th><th scope="col">Com base em quê (LGPD)</th></tr></thead>
                <tbody>
{tabela}
                </tbody>
              </table>
            </div>
            <p>Se um dia eu precisar usar algum dado para outra coisa, aviso você antes. E, quando a lei pedir, peço a sua autorização de novo.</p>'''),
    item("compartilhamento", "1.4", "Com quem os dados são compartilhados", f'''            <p>Não vendo, não alugo e não troco seus dados. Mas também não anoto tudo num caderninho: o site e o atendimento funcionam com algumas ferramentas, que guardam ou processam dados em meu nome.</p>
            <ul class="lg-lista">
              <li><strong>Plataforma de cadastro, formulários, agendamento e mensagens:</strong> HighLevel. É onde ficam seu cadastro, seus agendamentos e as conversas de atendimento.<span data-se="estadoComunidade=B" hidden> Se você assinar a comunidade paga, o acesso também fica no app de comunidade da HighLevel.</span></li>
              <li><strong>WhatsApp:</strong> para conversar com você, enviar confirmações e lembretes. Também recebe os exames que você escolher me enviar antes da consulta: depois de copiados para o seu prontuário, eu apago os arquivos da conversa.</li>
              <li><strong>Pagamentos:</strong> {P("plataformaPagamento", "plataforma em confirmação")}, que processa Pix e cartão.</li>
              <li><strong>Consulta por vídeo:</strong> {P("plataformaVideo", "plataforma em confirmação")}.</li>
              <li><strong>Aplicativo onde você recebe o plano:</strong> {P("appPlano", "aplicativo em confirmação")}.</li>
              <li><strong>Hospedagem do site e análise de visitas:</strong> {P("hospedagemSite", "hospedagem em confirmação")} e {P("ferramentaAnalise", "ferramenta de análise em confirmação")}.</li>
              <li><strong>Anúncios (Meta, dona do Instagram e do Facebook, e Google), quando eu anunciar:</strong> recebem só sinais genéricos, como “alguém se inscreveu” ou “alguém agendou”, e só se você aceitar os cookies de anúncios. <strong>Eu configuro o site para não enviar às plataformas de anúncio nenhuma informação de saúde, fase ou resposta do questionário.</strong></li>
              <li><strong>Profissionais que me ajudam na operação</strong> (atendimento, tecnologia, contabilidade): acessam só o necessário para a tarefa deles e têm dever de sigilo.</li>
              <li><strong>Autoridades:</strong> só quando a lei ou uma ordem judicial exigir.</li>
            </ul>
            <p>Algumas dessas empresas podem guardar dados fora do Brasil, por exemplo nos Estados Unidos. Nesses casos, a transferência segue as hipóteses previstas na LGPD (art. 33) e as cláusulas de proteção de dados dos contratos desses fornecedores.</p>
            <p>Dado de saúde nunca é repassado para alguém tirar vantagem comercial dele, como manda a LGPD (art. 11, § 4º).</p>'''),
    item("automacao", "1.5", "Atendimento com apoio de automação", '''            <p>Algumas mensagens do WhatsApp, como confirmações, lembretes e respostas a perguntas frequentes, podem ser enviadas de forma automática, com textos que eu aprovei antes. Nenhuma decisão sobre a sua saúde ou o seu plano é tomada por automação: quem avalia e orienta sou eu. Se quiser falar comigo diretamente, é só pedir na conversa.</p>''',
         attrs=' data-se="automacaoWhatsApp" hidden'),
    item("por-quanto-tempo", "1.5", "Por quanto tempo eu guardo seus dados", '''            <ul class="lg-lista">
              <li><strong>Cadastro de inscrição e do grupo<span data-se="diagnosticoFase" hidden> e respostas do questionário</span>:</strong> enquanto você mantiver o interesse, e no máximo por 24 meses depois do último contato. Depois disso, apago ou deixo anônimos, sem nada que identifique você. Se você retirar a autorização antes, apago antes.</li>
              <li><strong>Prontuário e dados da consulta:</strong> pelo prazo exigido pelas normas da nutrição e pela legislação de saúde.</li>
              <li><strong>Exames enviados pelo WhatsApp:</strong> só até eu copiá-los para o prontuário, antes ou logo depois da consulta. Depois disso, apago da conversa.</li>
              <li><strong>Dados de compra e nota fiscal:</strong> pelo prazo exigido pela legislação fiscal (em geral, 5 anos).</li>
              <li><strong>Dados de navegação:</strong> pelo prazo configurado em cada ferramenta, que não passa de 14 meses.</li>
            </ul>'''),
    item("como-protejo", "1.6", "Como eu protejo seus dados", '''            <p>Uso plataformas com acesso por senha e verificação em duas etapas, limito quem pode ver cada informação e mantenho o prontuário separado dos cadastros de inscrição e de conteúdo. Eu estaria mentindo se dissesse que algum sistema é cem por cento à prova de falhas. Se acontecer um incidente que possa te trazer risco ou dano relevante, eu aviso você e a Autoridade Nacional de Proteção de Dados (ANPD), como a lei manda.</p>'''),
    item("seus-direitos", "1.7", "Seus direitos", f'''            <p>Você pode, a qualquer momento e sem custo, me pedir para:</p>
            <ul class="lg-lista">
              <li>confirmar se eu tenho dados seus e ver quais são;</li>
              <li>corrigir dados errados ou desatualizados;</li>
              <li>apagar, bloquear ou deixar anônimos dados desnecessários ou tratados em desacordo com a lei;</li>
              <li>levar seus dados para outro profissional ou serviço (portabilidade);</li>
              <li>saber com quem eu compartilho seus dados;</li>
              <li>saber o que acontece se você não der o consentimento;</li>
              <li>cancelar um consentimento que você deu (isso não invalida o que foi feito antes);</li>
              <li>se opor a um uso que você não acha correto;</li>
              <li>pedir revisão de qualquer decisão tomada só por automação.</li>
            </ul>
            <p>Alguns dados não podem ser apagados na hora porque a lei me obriga a guardá-los, como o prontuário e as notas fiscais. Nesses casos, eu explico o motivo e o prazo.</p>
            <p class="lg-destaque"><strong>Como pedir:</strong> escreva para {EMAIL} com o assunto “Meus dados pessoais”. Para proteger você, posso pedir uma confirmação de que é você mesma. Respondo em até 15 dias.</p>
            <p>Se achar que eu não resolvi, você também pode reclamar na Autoridade Nacional de Proteção de Dados (ANPD), pelo site <a href="https://www.gov.br/anpd" rel="noopener">gov.br/anpd</a>.</p>'''),
    item("menores", "1.8", "Menores de idade", '''            <p>Este site e os meus atendimentos são para mulheres adultas. Eu não atendo crianças e não coleto, de propósito, dados de menores de 18 anos. Quando o assunto é a alimentação do seu bebê ou do seu filho, quem conversa comigo é você, e eu registro só o necessário para orientar você.</p>'''),
    item("mudancas-politica", "1.9", "Mudanças nesta política", '''            <p>Se eu mudar algo importante, a data no topo da página muda junto. E, se a mudança mexer no que você já autorizou, eu aviso antes pelo WhatsApp ou e-mail.</p>'''),
])

cookies = f'''
        <section class="lg-doc" id="cookies" data-doc="c" aria-labelledby="cookies-titulo">
          <header class="lg-doc-cabeca">
            <p class="rotulo">Cookies</p>
            <h2 id="cookies-titulo">Cookies, em poucas palavras</h2>
          </header>
          <div class="lg-item lg-item-solto">
            <p>Não são os de comer, infelizmente. Cookies são pequenos arquivos que o site guarda no seu navegador. Uso três tipos:</p>
            <ul class="lg-lista">
              <li><strong>Essenciais:</strong> fazem o site e os formulários funcionarem. Ficam sempre ligados.</li>
              <li><strong>De análise:</strong> mostram quais páginas são mais visitadas, sem identificar você pelo nome.</li>
              <li><strong>De anúncios (Meta e Google):</strong> ajudam a mostrar meus conteúdos para mulheres que podem se interessar. Recebem só sinais genéricos; o site é configurado para não enviar dado de saúde.</li>
            </ul>
            <p>Os de análise e de anúncios só ligam se você aceitar no aviso de cookies. Você pode mudar sua escolha a qualquer momento pelo link “Preferências de cookies”, no rodapé, ou apagar os cookies nas configurações do seu navegador.</p>
          </div>
        </section>'''

priv_indice = indice(
    indice_grupo("privacidade", "Política de Privacidade", priv_itens) + "\n" +
    '''            <div class="lg-indice-grupo">
              <a class="lg-indice-grupo-titulo" href="#cookies">Cookies</a>
            </div>''',
    '<p>Na outra página</p><a href="termos.html">Termos de Uso</a> · <a href="termos.html#teleconsulta">Consentimento para atendimento online</a>')

def faq(pares):
    import json
    q = [{"@type": "Question", "name": n, "acceptedAnswer": {"@type": "Answer", "text": t}} for n, t in pares]
    return json.dumps(q, ensure_ascii=False, indent=8)[:-1] + "      ]"

def faq_ld(pares, nome, caminho):
    return (f''',
    {{
      "@type": "WebPage",
      "@id": "{URL}{caminho}#pagina",
      "name": "{nome}",
      "inLanguage": "pt-BR",
      "isPartOf": {{"@type": "WebSite", "name": "Ana Paula Costa · Nutricionista", "url": "{URL}"}},
      "about": {{"@id": "{URL}#servico"}}
    }},
    {{
      "@type": "FAQPage",
      "@id": "{URL}{caminho}#faq",
      "mainEntity": {faq(pares)}
    }}''')

priv_faq = faq_ld([
    ("Quem é a responsável pelos meus dados?", "A própria Ana Paula Costa Rodrigues, nutricionista. Na Lei Geral de Proteção de Dados (LGPD), o nome técnico disso é controladora. Os pedidos sobre seus dados ela mesma responde."),
    ("O site pede exames ou dados de saúde?", "Não. O site não pede exames, peso, diagnóstico ou lista de remédios. Isso é conversa de consulta. Mesmo assim, a fase em que você está (gestação, pós-parto, 40+ ou menopausa) recebe o mesmo cuidado que qualquer dado de saúde."),
    ("Meus dados são vendidos ou usados em anúncio?", "Não. A Ana não vende, não aluga e não troca seus dados, e configura o site para não enviar às plataformas de anúncio nenhuma informação de saúde, fase ou resposta de questionário."),
    ("Por quanto tempo os dados ficam guardados?", "Cadastros de inscrição e grupo: enquanto você mantiver o interesse e no máximo 24 meses depois do último contato. Prontuário: pelo prazo exigido pelas normas da nutrição e pela legislação de saúde. Dados de compra e nota fiscal: pelo prazo da legislação fiscal, em geral 5 anos. Navegação: no máximo 14 meses."),
    ("Posso pedir para ver, corrigir ou apagar meus dados?", "Pode, a qualquer momento e sem custo, escrevendo com o assunto Meus dados pessoais. A resposta vem em até 15 dias. Prontuário e notas fiscais têm prazo legal de guarda, e nesses casos o motivo e o prazo são explicados."),
], "Política de Privacidade", "privacidade.html")

privacidade = head(
    "Política de Privacidade · Ana Paula Costa · Nutricionista",
    "Como a nutricionista Ana Paula Costa cuida dos seus dados no site, no WhatsApp, na comunidade e nas consultas online, em linguagem simples: o que é pedido, para quê, com quem é compartilhado e seus direitos pela LGPD.",
    "privacidade.html", priv_faq) + f'''<body class="pg-legal" data-fase="pos-parto">
{TOPO}
<main id="conteudo">
  <section class="lg-hero" aria-labelledby="titulo">
    <div class="lg-wrap">
      <div class="lg-hero-grade">
        <div class="lg-hero-texto">
          <p class="rotulo">Privacidade e termos</p>
          <h1 id="titulo">Seus dados, explicados <em>sem letra miúda</em></h1>
          <p class="lg-lead">O que você me conta pelo site, pelo WhatsApp e na consulta, e o que eu faço com isso. Escrevi do jeito que eu explicaria na consulta. Onde a lei pede um termo técnico, eu explico ali do lado.</p>
          <div class="lg-acao">
            {botao("topo", "cta-topo")}
            <p class="lg-micro">Respondo em até 15 dias. Atualizado em {DATA}.</p>
          </div>
        </div>
        <aside class="lg-resumo" aria-labelledby="resumo-titulo">
          <h2 class="lg-resumo-titulo" id="resumo-titulo">Em quatro linhas</h2>
          <ul>
            <li><span class="lg-ico">{ico("ui-file-text")}</span><span>Peço só o que preciso para falar com você e cuidar de você.</span></li>
            <li><span class="lg-ico">{ico("ui-video")}</span><span>Exames, peso, remédios e histórico de saúde ficam na consulta, não em formulário do site.</span></li>
            <li><span class="lg-ico">{ico("ui-lock")}</span><span>Eu não vendo seus dados e não uso informação de saúde em anúncio.</span></li>
            <li><span class="lg-ico">{ico("ui-check")}</span><span>Você pode pedir para ver, corrigir ou apagar seus dados quando quiser.</span></li>
          </ul>
        </aside>
      </div>
      <div class="lg-atalhos anima-traco">
        {traco()}
        <nav aria-label="Documentos">
          <span class="lg-atalhos-titulo">Sumário</span>
          <a href="#privacidade" aria-current="page">Política de Privacidade</a>
          <a href="termos.html#termos">Termos de Uso</a>
          <a href="termos.html#teleconsulta">Consentimento para atendimento online</a>
          <a href="#cookies">Cookies</a>
        </nav>
      </div>
    </div>
  </section>

  <div class="lg-leitura">
    <div class="lg-wrap lg-leitura-grade">
      <div class="lg-coluna-indice">
{priv_indice}
      </div>
      <article class="lg-texto">
        <section class="lg-doc" id="privacidade" data-doc="1" aria-labelledby="privacidade-titulo">
          <header class="lg-doc-cabeca">
            <p class="rotulo">Política de Privacidade</p>
            <h2 id="privacidade-titulo">Como eu cuido dos seus dados</h2>
            <p class="lg-lead">Vale para este site, para as páginas de inscrição, para o WhatsApp de atendimento, para a comunidade e para as consultas online.</p>
          </header>{priv_corpo}
        </section>
{cookies}
      </article>
    </div>
  </div>
{fecho()}
</main>
{rodape()}'''

# ================================================================ TERMOS
termos_itens = [
    ("quem-oferece", "2.1", "Quem oferece"),
    ("conteudo-educativo", "2.2", "O conteúdo do site é educativo"),
    ("produtos-digitais", "2.3", "Produtos digitais (como a Semana Bem Nutrida)"),
    ("termos-comunidade", "2.4", "Comunidade Bem Nutrida"),
    ("atendimentos", "2.5", "Atendimentos (Avaliação da Fase e Acompanhamento da Fase 90 dias)"),
    ("direitos-conteudo", "2.6", "Direitos sobre o conteúdo"),
    ("depoimentos", "2.7", "Depoimentos"),
    ("links-externos", "2.8", "Links e plataformas de outras empresas"),
    ("disponibilidade", "2.9", "Disponibilidade e responsabilidade"),
    ("mudancas-termos", "2.10", "Mudanças e lei aplicável"),
]

termos_corpo = "".join([
    item("quem-oferece", "2.1", "Quem oferece", f'''            <p>Este site ({P("dominio", "endereço do site em definição")}) é de Ana Paula Costa Rodrigues, nutricionista, {CRN}, CPF/CNPJ {P("cpfCnpj", "em confirmação")}.</p>'''),
    item("conteudo-educativo", "2.2", "O conteúdo do site é educativo", '''            <p>Os textos, vídeos, aulas, receitas, cardápios-exemplo e guias que eu publico servem para você entender melhor a alimentação de cada fase. Eles <strong>não são prescrição individual</strong> e não substituem consulta com nutricionista, acompanhamento médico ou o seu pré-natal.</p>
            <ul class="lg-lista">
              <li>Nunca pare, troque ou ajuste remédio ou suplemento receitado sem falar com quem receitou.</li>
              <li>Se você tem alguma condição de saúde, alergia, restrição ou está grávida ou amamentando, confira qualquer mudança com o seu médico ou com a sua nutricionista.</li>
              <li>Cada fase pede outro prato, e cada corpo responde de um jeito. O que funciona para uma mulher pode não funcionar igual para outra.</li>
              <li>Em emergência, procure um pronto-socorro ou ligue 192 (SAMU).</li>
            </ul>'''),
    item("produtos-digitais", "2.3", "Produtos digitais (como a Semana Bem Nutrida)", f'''            <ul class="lg-lista">
              <li><strong>O que você recebe:</strong> o material descrito na página do produto (por exemplo, planejador, cardápios-exemplo, receitas, listas de compras e aula gravada). É material educativo de organização da alimentação, não um plano individual.</li>
              <li><strong>Acesso:</strong> liberado no e-mail ou WhatsApp informado na compra, logo depois da confirmação do pagamento. Pix costuma liberar em minutos; cartão, depois da aprovação.</li>
              <li><strong>Uso pessoal:</strong> o acesso é seu. Não é permitido revender, repassar, publicar ou dividir o material com outras pessoas.</li>
              <li><strong>Garantia de 7 dias:</strong> comprou e não gostou? Peça a devolução em até 7 dias da compra pelo {EMAIL} ou pelo WhatsApp {WHATS}. Devolvo o valor pago, e você não precisa explicar o motivo. Essa garantia é de satisfação com o produto e segue o direito de arrependimento do Código de Defesa do Consumidor (art. 49). Ela não promete resultado.</li>
            </ul>'''),
    item("termos-comunidade", "2.4", "Comunidade Bem Nutrida", f'''            <ul class="lg-lista">
              <li><strong>Grupo gratuito:</strong> para entrar, basta se inscrever pelo site. Posso encerrar ou reorganizar o grupo, avisando antes.</li>
              <li data-se="estadoComunidade=B" hidden><strong>Comunidade paga:</strong> R$ 49,90 por mês, ou plano anual em 12x de R$ 39,90 (total de R$ 478,80 no ano). O plano mensal não tem fidelidade: você cancela quando quiser e o acesso vale até o fim do mês já pago. Plano anual: {P("regraCancelamentoAnual", "regra de cancelamento em confirmação")}.</li>
              <li data-senao="estadoComunidade=B"><strong>Comunidade paga:</strong> ainda não abriu. Quem entra na lista de espera da comunidade recebe o aviso da abertura, com valores e regras, antes de qualquer cobrança. Entrar na lista não gera pagamento nem compromisso.</li>
              <li data-se="estadoComunidade=B" hidden><strong>Primeiros 7 dias:</strong> se você assinar e desistir em até 7 dias, devolvo o valor pago, como garante o direito de arrependimento do Código de Defesa do Consumidor (art. 49).</li>
              <li><strong>Regras de convivência:</strong> respeito sempre; aqui não existe alimento vilão, e ninguém julga o corpo, o prato ou as escolhas de outra mulher; nada de vender produto, fazer propaganda ou mandar link de terceiros; o que outra participante conta lá dentro fica lá dentro. Quem desrespeitar essas regras pode ser removida.</li>
              <li><strong>A comunidade não é consulta:</strong> lá eu respondo dúvidas gerais e compartilho conteúdo. Orientação sobre o seu caso, com a sua história e os seus exames, é no atendimento.</li>
              <li><strong>Cuidado com o que você compartilha:</strong> o que você posta no grupo é visto pelas outras participantes. Evite mandar exames, laudos ou detalhes de saúde por lá. Se quiser falar do seu caso, me chame no particular ou marque um atendimento.</li>
            </ul>'''),
    item("atendimentos", "2.5", "Atendimentos (Avaliação da Fase e Acompanhamento da Fase 90 dias)", f'''            <ul class="lg-lista">
              <li><strong>Como funcionam:</strong> online, por vídeo. As regras de atendimento online estão no <a href="#teleconsulta">termo de consentimento</a> logo abaixo.</li>
              <li><strong>Valores e pagamento:</strong> os valores e as formas de pagamento são informados no agendamento. Pix ou cartão em até 10x. Você recebe nota fiscal, que pode usar para pedir reembolso ao seu plano de saúde, conforme as regras do seu plano.</li>
              <li><strong>Remarcação e cancelamento:</strong> {P("politicaRemarcacao", "regra de remarcação em confirmação")}. Se você contratou pela internet, essas regras não tiram o seu direito de desistir em até 7 dias da contratação, previsto no Código de Defesa do Consumidor (art. 49).</li>
              <li><strong>Garantia do Plano que Cabe:</strong> se, em até 7 dias depois de receber o plano, ele não couber na sua rotina, eu reescrevo sem custo. Plano bonito que não cabe na sua semana não serve para nada. Por isso a garantia é do serviço (ajustar o plano à sua vida real). Ela não promete resultado no corpo nem em exame.</li>
            </ul>'''),
    item("direitos-conteudo", "2.6", "Direitos sobre o conteúdo", '''            <p>Textos, vídeos, aulas, receitas, fotos, logotipo e materiais deste site são meus ou usados com autorização, e são protegidos por direito autoral. Compartilhar o link das páginas e dos posts pode, e eu agradeço. Copiar, reproduzir ou vender o conteúdo sem autorização por escrito, não.</p>
            <p>Algumas ilustrações de alimentos e objetos podem ser feitas com apoio de ferramentas de inteligência artificial e, quando forem, isso é indicado. Eu não uso inteligência artificial para criar pessoas, pacientes, corpos ou resultados.</p>'''),
    item("depoimentos", "2.7", "Depoimentos", '''            <p>Os depoimentos publicados aqui falam da experiência de cada mulher com o atendimento ou com o material, usam as palavras dela e só aparecem com autorização por escrito. Quando eu precisar encurtar um depoimento, aviso que ele foi resumido. Neste site e nos meus materiais, eu não publico fotos de corpo, comparações de antes e depois, números de peso nem resultados de exame, nem meus nem de pacientes.</p>'''),
    item("links-externos", "2.8", "Links e plataformas de outras empresas", '''            <p>O site leva você para o WhatsApp, Instagram, TikTok, plataforma de pagamento e app de comunidade. Essas empresas têm regras próprias de uso e privacidade, que valem quando você estiver nelas.</p>'''),
    item("disponibilidade", "2.9", "Disponibilidade e responsabilidade", '''            <p>Faço o possível para o site funcionar sem interrupção e com informação atualizada, mas ele pode sair do ar por manutenção ou falha técnica. O conteúdo educativo não substitui o acompanhamento individual: decisões sobre a sua saúde, alimentação, remédios e suplementos devem ser tomadas com o profissional que acompanha você. Nada nestes termos tira direitos que o Código de Defesa do Consumidor garante a você.</p>'''),
    item("mudancas-termos", "2.10", "Mudanças e lei aplicável", '''            <p>Posso atualizar estes termos; a data de atualização fica no topo da página. Valem as leis brasileiras. Se um dia houver uma disputa, ela pode ser levada à Justiça da cidade onde você mora (o “foro do seu domicílio”), como prevê o Código de Defesa do Consumidor.</p>'''),
])

teleconsulta = f'''
        <section class="lg-doc" id="teleconsulta" data-doc="3" aria-labelledby="teleconsulta-titulo">
          <header class="lg-doc-cabeca">
            <p class="rotulo">Atendimento online</p>
            <h2 id="teleconsulta-titulo">Termo de Consentimento para Atendimento Nutricional Online</h2>
            <p class="lg-lead">O Conselho Federal de Nutricionistas pede que você conheça e aceite estas condições antes da primeira consulta por vídeo. Leia com calma; se algo não ficar claro, me pergunte antes.</p>
          </header>
          <p class="lg-termo-intro">Eu, paciente, declaro que fui informada e concordo com o seguinte:</p>
          <ol class="lg-termo">
            <li><p><strong>Quem me atende:</strong> a consulta é feita por Ana Paula Costa Rodrigues, nutricionista, {CRN}, por vídeo, pela plataforma {P("plataformaVideo", "a confirmar")}.</p></li>
            <li><p><strong>O que o atendimento online pode e não pode:</strong> a consulta por vídeo permite avaliar a minha rotina, os meus hábitos, a minha história e os exames que eu enviar, e montar um plano individual. Ela não permite exame físico nem algumas medidas que dependem de atendimento presencial. Se a nutricionista entender que eu preciso de avaliação presencial ou de outro profissional, ela vai me orientar a procurar.</p></li>
            <li><p><strong>Não substitui outros cuidados:</strong> o atendimento nutricional não substitui o acompanhamento médico nem o pré-natal. Não vou parar nem trocar remédio ou suplemento receitado sem falar com quem receitou.</p></li>
            <li><p><strong>Emergências:</strong> a consulta e o WhatsApp de suporte não são canais de emergência. Em caso de urgência, procuro um pronto-socorro ou ligo 192 (SAMU).</p></li>
            <li><p><strong>Informações verdadeiras:</strong> a qualidade do plano depende das informações que eu passo. Vou contar a verdade sobre a minha saúde, medicações, suplementos e rotina, e avisar se algo mudar.</p></li>
            <li><p><strong>Ambiente e conexão:</strong> vou participar de um lugar reservado, com internet estável. Se a conexão cair, a consulta continua por outro meio combinado ou é remarcada.</p></li>
            <li><p><strong>Gravação:</strong> a consulta não é gravada por nenhuma das partes, a não ser que as duas concordem antes, por escrito.</p></li>
            <li><p><strong>Sigilo e dados:</strong> as informações da consulta ficam no prontuário, protegidas pelo sigilo profissional e tratadas como dado sensível, conforme a LGPD e a <a href="privacidade.html">Política de Privacidade</a> deste site.</p></li>
            <li><p><strong>Plano e suporte:</strong> recebo o plano pelo {P("appPlano", "aplicativo a confirmar")} e o suporte pelo WhatsApp, nos prazos combinados no agendamento.</p></li>
            <li><p><strong>Liberdade:</strong> posso recusar o atendimento online a qualquer momento. Como a nutricionista atende só online, ela me orienta a procurar atendimento presencial com outro profissional, se eu preferir. Também posso desistir antes da consulta, conforme as regras de remarcação e cancelamento e o meu direito de arrependimento.</p></li>
          </ol>
          <p class="lg-aceite">{ico("ui-calendar")}<span><strong>Registro do aceite:</strong> data, horário e identificação do aceite ficam guardados junto ao meu cadastro.</span></p>
        </section>'''

termos_indice = indice(
    indice_grupo("quem-oferece", "Termos de Uso", termos_itens) + "\n" +
    '''            <div class="lg-indice-grupo">
              <a class="lg-indice-grupo-titulo" href="#teleconsulta">Consentimento para atendimento online</a>
            </div>''',
    '<p>Na outra página</p><a href="privacidade.html">Política de Privacidade</a> · <a href="privacidade.html#cookies">Cookies</a>')

termos_faq = faq_ld([
    ("O conteúdo do site substitui consulta?", "Não. Textos, vídeos, aulas, receitas, cardápios-exemplo e guias são educativos, não são prescrição individual e não substituem consulta com nutricionista, acompanhamento médico ou o pré-natal. Em emergência, procure um pronto-socorro ou ligue 192 (SAMU)."),
    ("Posso devolver um produto digital?", "Pode. Em até 7 dias da compra você pede a devolução e recebe o valor pago, sem precisar explicar o motivo. A garantia é de satisfação com o produto, segue o direito de arrependimento do Código de Defesa do Consumidor (art. 49) e não promete resultado."),
    ("Como funciona a Garantia do Plano que Cabe?", "Se, em até 7 dias depois de receber o plano, ele não couber na sua rotina, a Ana reescreve sem custo. É uma garantia do serviço, de ajustar o plano à sua vida real, e não promete resultado no corpo nem em exame."),
    ("Como é a consulta online?", "Por vídeo. Ela permite avaliar rotina, hábitos, história e exames enviados e montar um plano individual, mas não permite exame físico. A consulta não é gravada sem que as duas partes concordem antes, por escrito, e não é canal de emergência."),
    ("A consulta dá nota fiscal para reembolso?", "Sim. Você recebe nota fiscal, que pode usar para pedir reembolso ao seu plano de saúde, conforme as regras do seu plano. O pagamento é por Pix ou cartão em até 10x."),
], "Termos de Uso", "termos.html")

termos = head(
    "Termos de Uso · Ana Paula Costa · Nutricionista",
    "O combinado entre você e a nutricionista Ana Paula Costa: conteúdo educativo, produtos digitais com garantia de 7 dias, Comunidade Bem Nutrida, atendimentos online e o termo de consentimento da consulta por vídeo.",
    "termos.html", termos_faq) + f'''<body class="pg-legal" data-fase="pos-parto">
{TOPO}
<main id="conteudo">
  <section class="lg-hero" aria-labelledby="titulo">
    <div class="lg-wrap">
      <div class="lg-hero-grade">
        <div class="lg-hero-texto" id="termos">
          <p class="rotulo">Termos de Uso</p>
          <h1 id="titulo">O combinado <em>entre nós</em></h1>
          <p class="lg-lead">As regras para usar este site, os materiais gratuitos, os produtos digitais e a comunidade. Ao navegar, se inscrever ou comprar, você concorda com elas.</p>
          <div class="lg-acao">
            {botao("topo", "cta-topo")}
            <p class="lg-micro">Respondo em até 15 dias. Atualizado em {DATA}.</p>
          </div>
        </div>
        <aside class="lg-resumo lg-resumo-docs" aria-labelledby="docs-titulo">
          <h2 class="lg-resumo-titulo" id="docs-titulo">Sumário</h2>
          <ul>
            <li><span class="lg-ico">{ico("ui-lock")}</span><a href="privacidade.html">Política de Privacidade</a>{ico("ui-chevron-down", "lg-chev")}</li>
            <li><span class="lg-ico">{ico("ui-file-text")}</span><a href="#quem-oferece">Termos de Uso</a>{ico("ui-chevron-down", "lg-chev")}</li>
            <li><span class="lg-ico">{ico("ui-video")}</span><a href="#teleconsulta">Consentimento para atendimento online</a>{ico("ui-chevron-down", "lg-chev")}</li>
            <li><span class="lg-ico">{ico("ui-info")}</span><a href="privacidade.html#cookies">Cookies</a>{ico("ui-chevron-down", "lg-chev")}</li>
          </ul>
        </aside>
      </div>
    </div>
  </section>

  <div class="lg-leitura lg-leitura-termos">
    <div class="lg-wrap lg-leitura-grade">
      <div class="lg-coluna-indice">
{termos_indice}
      </div>
      <article class="lg-texto">
        <section class="lg-doc" data-doc="2" aria-label="Termos de Uso do site">
          <span id="termos-inicio"></span>{termos_corpo}
        </section>
{teleconsulta}
      </article>
    </div>
  </div>
{fecho(False)}
</main>
{rodape()}'''

# ================================================================ 404
img404 = '''<link rel="preload" as="image" type="image/avif" imagesrcset="assets/img/fotos/crossfit-320.avif 320w, assets/img/fotos/crossfit-432.avif 432w" imagesizes="(min-width: 880px) 430px, 80vw">
'''
pagina404 = head(
    "Página não encontrada · Ana Paula Costa · Nutricionista",
    "Esta página não existe ou mudou de lugar. Volte para o início e encontre os atendimentos, a comunidade e os conteúdos da nutricionista Ana Paula Costa.",
    "404.html", "", preload_img=img404, base_dinamica=True) + f'''<body class="pg-legal" data-fase="pos-parto">
{TOPO}
<main id="conteudo">
  <section class="lg-perdida" aria-labelledby="titulo">
    <div class="lg-wrap lg-perdida-grade">
      <div>
        <p class="rotulo">Página não encontrada</p>
        <h1 id="titulo">Vilão, só no cinema. <em>Página perdida, aqui.</em></h1>
        <p class="lg-lead">O endereço que você abriu não existe ou mudou de lugar. Acontece: toda rota tem um desvio de vez em quando. O caminho de volta é curto.</p>
        <div class="lg-acao">
          <a class="lg-botao" href="./" id="cta-topo">Voltar para o início {SETA}</a>
        </div>
        <div class="lg-perdida-rota anima-traco">
          {traco()}
          <nav class="lg-perdida-links" aria-label="Páginas do site">
            <p>Ou siga direto para</p>
            <a href="atendimentos.html">Atendimentos</a>
            <a href="comunidade.html">Comunidade Bem Nutrida</a>
            <a href="semana-bem-nutrida.html">Semana Bem Nutrida</a>
            <a href="sobre.html">Sobre a Ana</a>
          </nav>
        </div>
      </div>
      <figure class="lg-perdida-foto">
        <div class="arco lg-arco">
          <picture>
            <source type="image/avif" srcset="assets/img/fotos/crossfit-320.avif 320w, assets/img/fotos/crossfit-432.avif 432w" sizes="(min-width: 880px) 430px, 80vw">
            <source type="image/webp" srcset="assets/img/fotos/crossfit-320.webp 320w, assets/img/fotos/crossfit-432.webp 432w" sizes="(min-width: 880px) 430px, 80vw">
            <img src="assets/img/fotos/crossfit-432.webp" width="432" height="576" alt="Ana Paula Costa no box de crossfit, de regata azul-marinho, erguendo um kettlebell acima da cabeça com os braços estendidos" fetchpriority="high" decoding="async">
          </picture>
        </div>
        <p class="lg-404" aria-hidden="true"><b>4<i>0</i>4</b><span>Fora da rota</span></p>
      </figure>
    </div>
  </section>
</main>
{rodape()}'''

# ================================================================ legal.html (atalho das âncoras antigas)
legal = f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Privacidade e termos · Ana Paula Costa · Nutricionista</title>
<meta name="robots" content="noindex, nofollow">
<link rel="canonical" href="{URL}privacidade.html">
<script>
(function () {{
  var mapa = {{"privacidade": "privacidade.html#privacidade", "cookies": "privacidade.html#cookies",
    "termos": "termos.html", "termos-comunidade": "termos.html#termos-comunidade", "teleconsulta": "termos.html#teleconsulta"}};
  var h = location.hash.replace("#", "");
  location.replace(mapa[h] || (h && document.getElementById ? "privacidade.html" : "privacidade.html"));
}})();
</script>
<meta http-equiv="refresh" content="0; url=privacidade.html">
<style>body{{font:18px/1.6 system-ui,sans-serif;background:#F2F0EB;color:#2B2724;margin:0;padding:48px 16px}}a{{color:#2F6E60}}</style>
</head>
<body>
<p>Esta página mudou de endereço. <a href="privacidade.html">Política de Privacidade</a> · <a href="termos.html">Termos de Uso</a></p>
</body>
</html>
'''

for nome, html in [("privacidade.html", privacidade), ("termos.html", termos), ("404.html", pagina404), ("legal.html", legal)]:
    (RAIZ / nome).write_text(html, encoding="utf-8")
    print("ok", nome, len(html))
