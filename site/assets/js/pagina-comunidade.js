/* Comunidade Bem Nutrida · comportamento da página
   - estado A (só grupo gratuito) ou B (comunidade paga aberta) por CONFIG.estadoComunidade
   - marcadores a partir de window.CONFIG; vazio = mantém o aviso .pendente
   - formulário do grupo: máscara do WhatsApp, validação acessível, envio ao CONFIG.formEndpoint
     (vazio = prévia: mostra a tela de sucesso sem enviar dado nenhum)
   - medição genérica no dataLayer (lead, checkout_clicado), sem nome, telefone nem fase da vida
   - régua de fases, barra fixa do celular, faixa de prévia, traço que se desenha ao rolar */
(function () {
  "use strict";
  var C = window.CONFIG || {};
  var dl = (window.dataLayer = window.dataLayer || []);
  var medir = function (ev, extra) { if (window.medir) window.medir(ev, extra); else { var d = { event: ev, pagina: "comunidade" }; for (var k in extra || {}) d[k] = extra[k]; dl.push(d); } };
  var reduz = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var $ = function (sel, raiz) { return (raiz || document).querySelector(sel); };
  var $$ = function (sel, raiz) { return Array.prototype.slice.call((raiz || document).querySelectorAll(sel)); };
  var vazio = function (v) { return v === undefined || v === null || String(v).trim() === ""; };
  var estadoB = String(C.estadoComunidade || "A").toUpperCase() === "B" && !vazio(C.linkCheckoutComunidade);

  /* faixa de prévia */
  var faixa = document.getElementById("faixa-previa");
  if (faixa && C.previa === false) faixa.hidden = true;

  /* aviso curto */
  var toast = document.getElementById("aviso-previa"), tt;
  function aviso(msg) {
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add("on");
    clearTimeout(tt);
    tt = setTimeout(function () { toast.classList.remove("on"); }, 3800);
  }

  /* ---------------------------------------------------------------- estado A / B */
  if (estadoB) {
    document.body.classList.add("estado-b");
    $$("[data-estado-b]").forEach(function (el) { el.textContent = el.getAttribute("data-estado-b"); });
    $$("[data-so-estado-a]").forEach(function (el) { el.hidden = true; });
    $$("[data-so-estado-b]").forEach(function (el) { el.hidden = false; });
    // degrau 2 sobe para antes do degrau 1; o grupo vira a opção leve
    var d1 = document.getElementById("grupo"), d2 = document.getElementById("comunidade-paga");
    if (d1 && d2) d1.parentNode.insertBefore(d2, d1);
    $$("[data-cta-principal]").forEach(function (a) {
      a.href = C.linkCheckoutComunidade;
      a.setAttribute("data-checkout", "");
    });
    var desc = document.querySelector('meta[name="description"]');
    if (desc) desc.content = "Comunidade só de mulheres, com encontro ao vivo toda semana com uma nutricionista, para gestação, pós-parto, 40+ e menopausa. Também tem grupo gratuito.";
  }

  /* ---------------------------------------------------------------- marcadores */
  $$("[data-cfg]").forEach(function (el) {
    var v = C[el.getAttribute("data-cfg")];
    if (vazio(v)) return;
    el.textContent = v;
    el.classList.remove("pendente");
  });
  $$("[data-frase]").forEach(function (el) { el.hidden = vazio(C[el.getAttribute("data-frase")]); });
  if (!vazio(C.crn)) {
    $$("[data-crn]").forEach(function (el) { el.textContent = "CRN-" + C.crn; el.classList.remove("pendente"); });
  }
  if (C.encontroGravado === true) $$(".cbn-gravado").forEach(function (el) { el.hidden = false; });
  if (!vazio(C.numeroParticipantes)) {
    var p = $(".cbn-participantes");
    if (p) { $("[data-participantes]", p).textContent = C.numeroParticipantes + " mulheres já estão no grupo"; p.hidden = false; }
  }
  if (!vazio(C.linkTermosComunidade)) { var lt = document.getElementById("link-termos"); if (lt) lt.href = C.linkTermosComunidade; }

  /* fundadoras: só com vagas, preço e contador reais */
  var f = C.fundadora;
  if (f && f.vagas && f.preco && f.restantes !== undefined && f.restantes !== null) {
    var fb = document.getElementById("fundadora");
    $("[data-fundadora]", fb).textContent = "as primeiras " + f.vagas + " assinantes entram por " + f.preco + " por mês" + (f.condicao ? " " + f.condicao : "") + ". Restam " + f.restantes + " vagas.";
    fb.hidden = false;
  }

  /* depoimentos: só com autorização escrita */
  var dep = C.depoimentosComunidade;
  if (Array.isArray(dep) && dep.length) {
    var lista = document.getElementById("depo-lista");
    dep.forEach(function (d) {
      if (!d || vazio(d.texto)) return;
      var fig = document.createElement("figure");
      fig.className = "cbn-depo";
      var bq = document.createElement("blockquote");
      var pp = document.createElement("p");
      pp.textContent = "“" + d.texto + "”";
      bq.appendChild(pp);
      var cap = document.createElement("figcaption");
      cap.textContent = [d.autora, d.fase].filter(Boolean).join(", ");
      fig.appendChild(bq); fig.appendChild(cap);
      lista.appendChild(fig);
    });
    if (lista.children.length) document.getElementById("depoimentos").hidden = false;
  }

  /* contatos (rodapé = link; tela de sucesso = texto) */
  var whatsNum = vazio(C.whatsapp) ? "" : String(C.whatsapp).replace(/\D/g, "");
  $$("[data-contato]").forEach(function (el) {
    var tipo = el.getAttribute("data-contato"), a;
    if (tipo === "whatsapp" && whatsNum) {
      a = document.createElement("a");
      a.href = "https://wa.me/" + whatsNum; a.rel = "noopener";
      a.textContent = "WhatsApp " + (C.whatsappExibicao || "");
      el.replaceWith(a);
    } else if (tipo === "email" && !vazio(C.email)) {
      a = document.createElement("a");
      a.href = "mailto:" + C.email; a.textContent = C.email;
      el.replaceWith(a);
    }
  });
  if (whatsNum) $$('[data-contato-texto="whatsapp"]').forEach(function (el) { el.textContent = C.whatsappExibicao || whatsNum; el.classList.remove("pendente"); });

  /* ---------------------------------------------------------------- CTA principal e checkout */
  $$("[data-cta-principal]").forEach(function (a) {
    a.addEventListener("click", function (e) {
      if (estadoB) {
        medir("checkout_clicado", { produto: "comunidade_bem_nutrida", posicao: a.getAttribute("data-posicao") || "" });
        return;
      }
      medir("grupo_clicado", { posicao: a.getAttribute("data-posicao") || "" });
      e.preventDefault();
      modoLista(false);
      irParaFormulario(false);
    });
  });

  var form = document.getElementById("form-grupo");
  var cartao = document.getElementById("form-cartao");
  function irParaFormulario(destacarEspera) {
    if (!cartao) return;
    cartao.scrollIntoView({ behavior: reduz ? "auto" : "smooth", block: "start" });
    var alvo = document.getElementById("f-nome");
    if (destacarEspera) {
      var ce = document.getElementById("check-espera");
      if (ce && !ce.hidden) { ce.classList.remove("destaque"); void ce.offsetWidth; ce.classList.add("destaque"); }
    }
    if (alvo && !form.hidden) setTimeout(function () { alvo.focus({ preventScroll: true }); }, reduz ? 0 : 450);
  }
  /* modo lista de espera: quem quer só a comunidade paga não precisa entrar no grupo */
  var emModoLista = false;
  function modoLista(on) {
    emModoLista = !!on && !estadoB;
    var titulo = document.getElementById("titulo-form"), av = document.getElementById("aviso-modo-lista"), rot = document.getElementById("rotulo-envio");
    var esp = document.getElementById("f-espera");
    if (titulo) { if (!titulo.dataset.original) titulo.dataset.original = titulo.textContent; titulo.textContent = emModoLista ? titulo.getAttribute("data-titulo-lista") : titulo.dataset.original; }
    if (av) av.hidden = !emModoLista;
    if (rot) rot.textContent = emModoLista ? "Entrar na lista de espera" : "Liberar meu acesso ao grupo";
    if (esp && emModoLista) esp.checked = true;   // a pessoa pediu a lista ao tocar no botão
  }
  var trocar = document.getElementById("trocar-para-grupo");
  if (trocar) trocar.addEventListener("click", function () { modoLista(false); var n = document.getElementById("f-nome"); if (n) n.focus(); });
  var ctaEspera = document.getElementById("cta-lista-espera");
  if (ctaEspera) ctaEspera.addEventListener("click", function (e) {
    e.preventDefault();
    medir("lista_espera_clicado", { posicao: "degrau2" });
    modoLista(true);
    irParaFormulario(true);
  });
  // comunidade.html#lista (link da página inicial e da Semana) abre direto no modo lista
  if (location.hash === "#lista" && !estadoB) { modoLista(true); setTimeout(function () { irParaFormulario(true); }, 120); }

  /* ---------------------------------------------------------------- formulário do grupo */
  if (form) {
    var nome = document.getElementById("f-nome");
    var whats = document.getElementById("f-whats");
    var consent = document.getElementById("f-consent");
    var consentFase = document.getElementById("f-consent-fase");
    var checkFase = document.getElementById("check-fase");
    var espera = document.getElementById("f-espera");
    // fase escolhida = dado sensível: aparece a autorização destacada
    var atualizaFase = function () {
      var tem = !!form.querySelector('input[name="fase"]:checked');
      if (checkFase) checkFase.hidden = !tem;
      if (!tem && consentFase) { consentFase.checked = false; marca(consentFase, "e-consent-fase", true); }
    };
    $$('input[name="fase"]', form).forEach(function (r) {
      r.addEventListener("change", atualizaFase);
      // tocar de novo na fase marcada desmarca (a fase é opcional)
      r.addEventListener("click", function () { if (r.dataset.estava === "1") { r.checked = false; r.dataset.estava = ""; atualizaFase(); } else { $$('input[name="fase"]', form).forEach(function (o) { o.dataset.estava = ""; }); r.dataset.estava = "1"; } });
    });

    whats.addEventListener("input", function () {
      var d = whats.value.replace(/\D/g, "").slice(0, 11);
      var out = d;
      if (d.length > 2) out = "(" + d.slice(0, 2) + ") " + d.slice(2);
      if (d.length > 6) out = "(" + d.slice(0, 2) + ") " + d.slice(2, d.length === 11 ? 7 : 6) + "-" + d.slice(d.length === 11 ? 7 : 6);
      else if (d.length > 0 && d.length <= 2) out = "(" + d;
      whats.value = out;
    });

    function marca(campo, erroId, ok) {
      var err = document.getElementById(erroId);
      campo.setAttribute("aria-invalid", ok ? "false" : "true");
      if (err) err.hidden = ok;
      return ok;
    }
    nome.addEventListener("blur", function () { if (nome.value.trim()) marca(nome, "e-nome", true); });
    whats.addEventListener("blur", function () { var n = whats.value.replace(/\D/g, "").length; if (n >= 10) marca(whats, "e-whats", true); });
    consent.addEventListener("change", function () { if (consent.checked) marca(consent, "e-consent", true); });

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var digitos = whats.value.replace(/\D/g, "");
      var ok1 = marca(nome, "e-nome", nome.value.trim().length >= 2);
      var ok2 = marca(whats, "e-whats", digitos.length === 10 || digitos.length === 11);
      var ok3 = marca(consent, "e-consent", consent.checked);
      var faseMarcada = form.querySelector('input[name="fase"]:checked');
      var ok4 = marca(consentFase, "e-consent-fase", !faseMarcada || consentFase.checked);
      if (!(ok1 && ok2 && ok3 && ok4)) {
        var primeiro = !ok1 ? nome : !ok2 ? whats : !ok3 ? consent : consentFase;
        primeiro.focus();
        return;
      }
      var querEspera = !!(espera && espera.checked && !espera.closest("[hidden]"));
      var querGrupo = !emModoLista;
      var dados = {
        nome: nome.value.trim(),
        whatsapp: "+55" + digitos,
        fase: faseMarcada ? faseMarcada.value : "",
        consentimento_contato: true,
        consentimento_fase: !!faseMarcada && consentFase.checked,
        consentimento_avisos: !!form.querySelector('input[name="consentimento_avisos"]').checked,
        grupo_gratuito: querGrupo,
        lista_espera: querEspera,
        tags: (querGrupo ? ["comunidade-grupo-gratuito"] : []).concat(querEspera ? ["comunidade-lista-espera"] : []),
        origem: location.pathname + location.search,
        consentimento_em: new Date().toISOString(),
        versao_politica: C.dataAtualizacao || "previa"
      };
      var botao = form.querySelector('button[type="submit"]');
      botao.setAttribute("aria-busy", "true");

      var concluir = function (previa) {
        botao.removeAttribute("aria-busy");
        // medição genérica: nunca nome, telefone nem fase
        medir("lead", { formulario: querGrupo ? "grupo_gratuito" : "lista_espera", lista_espera: querEspera, previa: !!previa });
        mostraSucesso(dados.nome, querEspera, previa, querGrupo);
      };

      if (vazio(C.formEndpoint)) {
        if (C.previa === false) {   // publicado sem endpoint: nunca fingir sucesso
          botao.removeAttribute("aria-busy");
          if (window.console) console.error("formEndpoint vazio em produção: o cadastro do grupo não foi enviado.");
          var falhaEl = document.getElementById("form-falha");
          if (falhaEl) falhaEl.hidden = false;
          aviso("Não conseguimos enviar agora. Se preferir, chame a Ana no WhatsApp.");
          return;
        }
        setTimeout(function () { concluir(true); }, 350); return;
      }
      fetch(C.formEndpoint, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(dados) })
        .then(function (r) { if (!r.ok) throw new Error(r.status); concluir(false); })
        .catch(function () {
          botao.removeAttribute("aria-busy");
          aviso("Não conseguimos enviar agora. Confira a conexão e tente de novo em instantes.");
        });
    });
  }

  var barra = document.getElementById("barra-fixa");
  var enviado = false;
  function mostraSucesso(primeiroNome, querEspera, previa, querGrupo) {
    enviado = true;
    var s = document.getElementById("form-sucesso");
    var n = primeiroNome.split(/\s+/)[0];
    $("[data-nome]", s).textContent = n;
    var b = document.getElementById("botao-entrar-grupo");
    var soLista = querGrupo === false;
    var tituloS = document.getElementById("titulo-sucesso");
    if (soLista) {
      if (tituloS) tituloS.textContent = "Pronto, " + (n || "tudo certo") + ". Você está na lista de espera.";
      $$(".cbn-sucesso > p", s).forEach(function (pp) { if (pp.id !== "sucesso-espera" && pp.id !== "sucesso-previa") pp.hidden = true; });
      b.hidden = true;
    }
    if (!vazio(C.linkConviteGrupo)) {
      b.href = C.linkConviteGrupo;
      b.addEventListener("click", function () { medir("grupo_entrar_clicado", { posicao: "sucesso" }); });
    } else {
      b.setAttribute("aria-disabled", "true");
      b.addEventListener("click", function (e) { e.preventDefault(); aviso("Prévia: o link do grupo ainda está em configuração."); });
    }
    document.getElementById("sucesso-espera").hidden = !querEspera;
    if (!vazio(C.whatsapp) || C.previa !== false) { /* contato de reserva aparece */ } else { $$(".cbn-sucesso-micro", s).forEach(function (pp) { pp.hidden = true; }); }
    document.getElementById("sucesso-previa").hidden = !previa;
    form.hidden = true;
    s.hidden = false;
    s.focus();
    if (barra) { barra.classList.remove("on"); barra.setAttribute("aria-hidden", "true"); }
  }

  /* ---------------------------------------------------------------- régua de fases */
  var regua = document.getElementById("regua");
  if (regua) {
    var botoes = $$("button[data-fase-alvo]", regua);
    var trilho = $(".cbn-regua-linha", regua);
    botoes.forEach(function (bt, i) {
      bt.addEventListener("click", function () {
        regua.setAttribute("data-fase", bt.getAttribute("data-fase-alvo"));
        if (trilho) trilho.style.setProperty("--progresso", (i / (botoes.length - 1)) * 100 + "%");
        botoes.forEach(function (o) { o.setAttribute("aria-pressed", o === bt ? "true" : "false"); });
      });
    });
  }

  /* ---------------------------------------------------------------- barra fixa do celular */
  var ctaTopo = document.getElementById("cta-topo");
  var ctaFinal = document.getElementById("cta-final");
  if (barra && ctaTopo && ctaFinal) {
    var botaoBarra = barra.querySelector("a");
    var agendado = false;
    var atualiza = function () {
      agendado = false;
      var t = ctaTopo.getBoundingClientRect();
      var fi = ctaFinal.getBoundingClientRect();
      var c = cartao ? cartao.getBoundingClientRect() : null;
      var vh = window.innerHeight;
      var formNaTela = c && c.top < vh && c.bottom > 0;
      var mostra = !enviado && t.bottom < 0 && fi.top > vh * 0.9 && !(formNaTela && !estadoB);
      if (mostra !== barra.classList.contains("on")) {
        barra.classList.toggle("on", mostra);
        barra.setAttribute("aria-hidden", mostra ? "false" : "true");
        if (botaoBarra) botaoBarra.tabIndex = mostra ? 0 : -1;
      }
    };
    var pede = function () { if (!agendado) { agendado = true; requestAnimationFrame(atualiza); } };
    window.addEventListener("scroll", pede, { passive: true });
    window.addEventListener("resize", pede);
    atualiza();
  }

  /* ---------------------------------------------------------------- entradas e traço */
  var alvos = $$(".anima-traco, .cbn-revela, .cbn-regua");
  if (reduz || !("IntersectionObserver" in window)) {
    alvos.forEach(function (el) { el.classList.add("visto"); });
  } else {
    var io = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("visto"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -10% 0px", threshold: 0.12 });
    alvos.forEach(function (el) { io.observe(el); });
  }
})();
