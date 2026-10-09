/* Ana Paula Costa · Nutricionista
   site.js · comportamento comum a todas as páginas (carrega antes do JS de cada página)
   - trava de publicação: com previa=false e dado obrigatório vazio, o site continua em prévia
   - faixa "Prévia em aprovação" (some com CONFIG.previa = false)
   - window.medir: um formato só de evento no dataLayer {event, pagina, posicao, formulario|produto, previa}
   - blocos que dependem de produto pronto (data-pronto): prévia mostra com selo "Em breve"; publicado e não pronto = oculto
   - números das redes (data-rede) a partir de CONFIG.redes
   - menu do celular: aria-expanded, Esc fecha e devolve o foco, toque fora (ou no fundo escurecido) fecha
   - sombra do cabeçalho ao rolar
   - rodapé: CRN, contatos e dados de quem vende a partir do CONFIG; vazio = aviso .pendente
   - "Preferências de cookies"
   Medição: só eventos genéricos, sem dado de saúde. */
(function () {
  "use strict";
  var C = window.CONFIG = window.CONFIG || {};
  var doc = document.documentElement;
  doc.classList.add("js");
  window.dataLayer = window.dataLayer || [];
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var vazio = function (v) { return v === undefined || v === null || String(v).trim() === ""; };

  /* ---------------------------------------------------------- trava de publicação
     Nada vai ao ar sem CRN, cadastro no e-Nutricionista, contatos, identificação de quem vende e endpoint do formulário.
     Se alguém trocar previa para false antes disso, o site segue em prévia (faixa visível) e avisa no console. */
  var OBRIGATORIOS = ["crn", "whatsapp", "email", "nomeVendedor", "cpfCnpj", "enderecoFiscal", "formEndpoint"];
  var bloqueada = false;
  if (C.previa === false) {
    var faltam = OBRIGATORIOS.filter(function (k) { return vazio(C[k]); });
    if (C.cadastroENutricionista !== true) faltam.push("cadastroENutricionista");
    if (faltam.length) {
      bloqueada = true;
      C.previa = true;
      if (window.console) console.error("Publicação bloqueada: dados obrigatórios pendentes no CONFIG → " + faltam.join(", "));
    }
  }
  var previa = C.previa !== false;
  if (!previa) doc.classList.add("publicado");

  /* ---------------------------------------------------------- medição genérica */
  var classe = (document.body && document.body.className.match(/\bpg-([a-z-]+)/)) || [];
  var PAGINA = { home: "home", atendimentos: "atendimentos", comunidade: "comunidade", semana: "semana", sobre: "sobre", ferro: "ferro", legal: "legal" }[classe[1]] || (classe[1] || "outra");
  window.medir = function (evento, extra) {
    var d = { event: evento, pagina: PAGINA, previa: previa };
    if (extra) for (var k in extra) if (Object.prototype.hasOwnProperty.call(extra, k)) d[k] = extra[k];
    window.dataLayer.push(d);
    return d;
  };

  /* faixa de prévia */
  var faixa = $("#faixa-previa");
  if (faixa && !previa) faixa.hidden = true;
  if (faixa && bloqueada) { var tf = $("span", faixa); if (tf) tf.textContent = "Publicação bloqueada: dados obrigatórios pendentes"; }

  /* ---------------------------------------------------------- blocos que dependem de produto pronto */
  $$("[data-pronto]").forEach(function (el) {
    var chave = el.getAttribute("data-pronto");
    if (C[chave] === true) return;
    if (!previa) { el.hidden = true; return; }
    if (el.hasAttribute("data-sem-selo")) return;
    var selo = document.createElement("span");
    selo.className = "pendente pendente--pilula selo-pronto";
    selo.textContent = "Em breve";
    selo.title = "Prévia: entra no ar quando o produto estiver pronto";
    var alvo = $("[data-pronto-selo]", el);
    if (alvo) alvo.appendChild(selo); else el.insertBefore(selo, el.firstChild);
  });

  /* ---------------------------------------------------------- números das redes (uma fonte só) */
  var R = C.redes || {};
  $$("[data-rede]").forEach(function (el) {
    var v = R[el.getAttribute("data-rede")];
    if (vazio(v)) return;
    el.textContent = (el.getAttribute("data-modelo") || "{v}").replace("{v}", v);
  });

  /* aviso curto */
  var toast, tt;
  function aviso(msg) {
    if (!toast) {
      toast = document.createElement("div");
      toast.className = "site-toast";
      toast.setAttribute("role", "status");
      toast.setAttribute("aria-live", "polite");
      document.body.appendChild(toast);
    }
    toast.textContent = msg;
    requestAnimationFrame(function () { toast.classList.add("on"); });
    clearTimeout(tt);
    tt = setTimeout(function () { toast.classList.remove("on"); }, 4200);
  }

  /* ---------------------------------------------------------- cabeçalho */
  var topo = $(".site-topo"), botao = $(".site-topo__menu"), menu = $("#menu-site");
  if (topo && botao && menu) {
    var fecha = function (devolveFoco) {
      if (!menu.classList.contains("aberto")) return;
      menu.classList.remove("aberto");
      botao.setAttribute("aria-expanded", "false");
      if (devolveFoco) botao.focus();
    };
    botao.addEventListener("click", function () {
      var abre = !menu.classList.contains("aberto");
      menu.classList.toggle("aberto", abre);
      botao.setAttribute("aria-expanded", String(abre));
      if (abre) { var p = $("a", menu); if (p) p.focus(); }
    });
    menu.addEventListener("click", function (e) {
      if (e.target === menu) { fecha(true); return; }        // toque no fundo escurecido
      if (e.target.closest("a")) fecha(false);
    });
    $$("[data-agendar]", menu).forEach(function (a) {
      a.addEventListener("click", function () { window.medir("agendamento_clicado", { posicao: "menu" }); });
    });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") fecha(true); });
    document.addEventListener("click", function (e) { if (!topo.contains(e.target)) fecha(false); });
    window.addEventListener("resize", function () { if (window.innerWidth >= 960) fecha(false); }, { passive: true });
  }
  if (topo) {
    var marca = function () { topo.classList.toggle("rolou", window.scrollY > 8); };
    window.addEventListener("scroll", marca, { passive: true });
    marca();
  }

  /* ---------------------------------------------------------- rodapé */
  var rodape = $(".site-rodape");
  if (!rodape) return;

  $$("[data-site-ano]", rodape).forEach(function (el) { el.textContent = String(new Date().getFullYear()); });

  if (!vazio(C.crn)) {
    var crn = String(C.crn).trim();
    crn = /^crn/i.test(crn) ? crn : "CRN-" + crn.replace(/^-+/, "");
    $$("[data-site-crn]", rodape).forEach(function (el) { el.textContent = crn; el.classList.remove("pendente"); });
  }

  $$("[data-site-cfg]", rodape).forEach(function (el) {
    var v = C[el.getAttribute("data-site-cfg")];
    if (vazio(v)) return;
    el.textContent = (el.getAttribute("data-modelo") || "{v}").replace("{v}", v);
    el.classList.remove("pendente");
  });

  $$("[data-site-contato]", rodape).forEach(function (el) {
    var tipo = el.getAttribute("data-site-contato"), a = document.createElement("a");
    if (tipo === "whatsapp" && !vazio(C.whatsapp)) {
      a.href = "https://wa.me/" + String(C.whatsapp).replace(/\D/g, "");
      a.rel = "noopener";
      a.textContent = "WhatsApp " + (C.whatsappExibicao || C.whatsapp);
    } else if (tipo === "email" && !vazio(C.email)) {
      a.href = "mailto:" + C.email;
      a.textContent = C.email;
    } else { return; }
    a.addEventListener("click", function () { window.medir("contato_clicado", { canal: tipo, posicao: "rodape" }); });
    el.replaceWith(a);
  });

  /* links que só existem quando o produto estiver pronto (na prévia aparecem, publicados e não prontos somem) */
  $$("[data-site-requer]", document).forEach(function (el) {
    if (C[el.getAttribute("data-site-requer")] !== true && !previa) el.hidden = true;
  });

  /* itens que somem quando a pendência for resolvida (ex.: cadastro no e-Nutricionista) */
  $$("[data-site-oculta-se]", rodape).forEach(function (el) {
    if (C[el.getAttribute("data-site-oculta-se")] === true) el.remove();
  });

  $$("[data-site-cookies]", rodape).forEach(function (b) {
    b.addEventListener("click", function () {
      if (typeof window.abrirPreferenciasCookies === "function") { window.abrirPreferenciasCookies(); return; }
      aviso("O aviso de cookies entra junto com a ferramenta de análise. Hoje o site não usa cookies de análise nem de anúncios.");
    });
  });
})();
