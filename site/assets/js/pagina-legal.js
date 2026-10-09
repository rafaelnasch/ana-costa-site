/* Privacidade, Termos e 404 · comportamento da página
   - preenche marcadores a partir de window.CONFIG (assets/js/config.js); vazio = mantém o aviso .pendente
   - blocos condicionais: data-se="chave" (mostra se CONFIG.chave === true) e data-senao="chave" (mostra se não for true)
   - renumera os itens visíveis (1.1, 1.2...) e o sumário lateral
   - sumário lateral: acordeão no celular, item ativo e trilho da rota que acompanha a leitura
   - CTA de e-mail: mailto com assunto pronto; sem e-mail configurado, aviso de prévia e nada é enviado
   - sem medição de dado de saúde; esta página não dispara evento de conversão */
(function () {
  "use strict";
  var C = window.CONFIG || {};
  var doc = document.documentElement;
  doc.classList.add("js");
  var reduz = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var $$ = function (sel, raiz) { return Array.prototype.slice.call((raiz || document).querySelectorAll(sel)); };
  var vazio = function (v) { return v === undefined || v === null || String(v).trim() === ""; };

  /* faixa de prévia */
  var faixa = document.getElementById("faixa-previa");
  if (faixa && C.previa === false) faixa.hidden = true;

  /* ano do rodapé */
  $$("[data-ano]").forEach(function (el) { el.textContent = String(new Date().getFullYear()); });

  /* condicionais */
  /* "chave" = verdadeiro se CONFIG.chave === true; "chave=valor" = verdadeiro se String(CONFIG.chave) === valor */
  var vale = function (expr) {
    var p = expr.split("=");
    return p.length > 1 ? String(C[p[0]]) === p[1] : C[p[0]] === true;
  };
  $$("[data-se]").forEach(function (el) { el.hidden = !vale(el.getAttribute("data-se")); });
  $$("[data-senao]").forEach(function (el) { el.hidden = vale(el.getAttribute("data-senao")); });

  /* marcadores de texto: <span data-cfg="chave" data-modelo="{v}"> */
  $$("[data-cfg]").forEach(function (el) {
    var v = C[el.getAttribute("data-cfg")];
    if (vazio(v)) return;
    var modelo = el.getAttribute("data-modelo") || "{v}";
    el.textContent = modelo.replace("{v}", v);
    el.classList.remove("pendente");
  });

  /* CRN */
  if (!vazio(C.crn)) {
    $$("[data-crn]").forEach(function (el) { el.textContent = "CRN-" + C.crn; el.classList.remove("pendente"); });
  }

  /* contatos */
  $$("[data-contato]").forEach(function (el) {
    var tipo = el.getAttribute("data-contato");
    var a = document.createElement("a");
    if (tipo === "whatsapp" && !vazio(C.whatsapp)) {
      a.href = "https://wa.me/" + String(C.whatsapp).replace(/\D/g, "");
      a.rel = "noopener";
      a.textContent = (el.getAttribute("data-prefixo") || "") + (C.whatsappExibicao || C.whatsapp);
      el.replaceWith(a);
    } else if (tipo === "email" && !vazio(C.email)) {
      a.href = "mailto:" + C.email;
      a.textContent = C.email;
      el.replaceWith(a);
    }
  });

  /* aviso curto de prévia */
  var toast = document.getElementById("aviso-previa");
  var tt;
  function aviso(msg) {
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add("on");
    clearTimeout(tt);
    tt = setTimeout(function () { toast.classList.remove("on"); }, 3800);
  }

  /* CTA principal: e-mail com assunto pronto */
  $$("[data-mailto]").forEach(function (a) {
    var assunto = a.getAttribute("data-mailto") || "Meus dados pessoais";
    if (!vazio(C.email)) a.href = "mailto:" + C.email + "?subject=" + encodeURIComponent(assunto);
    a.addEventListener("click", function (e) {
      if (vazio(C.email)) {
        e.preventDefault();
        aviso("Prévia: o e-mail profissional da Ana ainda está em confirmação. Nada foi enviado.");
      }
    });
  });

  /* links que dependem de CONFIG (ex.: lista de espera) */
  $$("[data-link]").forEach(function (a) {
    var url = C[a.getAttribute("data-link")];
    if (!vazio(url)) { a.href = url; a.rel = "noopener"; return; }
    a.addEventListener("click", function (e) { e.preventDefault(); aviso("Prévia: este link ainda está em configuração."); });
  });

  /* preferências de cookies (o aviso de cookies entra junto com a ferramenta de análise) */
  $$("[data-cookies]").forEach(function (b) {
    b.addEventListener("click", function () {
      if (typeof window.abrirPreferenciasCookies === "function") { window.abrirPreferenciasCookies(); return; }
      aviso("Prévia: o aviso de cookies entra junto com a ferramenta de análise. Hoje o site não usa cookies de análise nem de anúncios.");
    });
  });

  /* renumeração dos itens visíveis e do sumário */
  $$("[data-doc]").forEach(function (secao) {
    var base = secao.getAttribute("data-doc");
    var n = 0;
    $$(".lg-item", secao).forEach(function (item) {
      if (item.hidden) return;
      n += 1;
      var num = base + "." + n;
      var span = item.querySelector(".lg-num");
      if (span) span.textContent = num;
      var link = document.querySelector('.lg-indice a[href="#' + item.id + '"] span:first-child');
      if (link) link.textContent = num;
    });
    $$(".lg-item[hidden]", secao).forEach(function (item) {
      var li = document.querySelector('.lg-indice a[href="#' + item.id + '"]');
      if (li && li.parentNode) li.parentNode.hidden = true;
    });
  });

  /* sumário: aberto no desktop, recolhido no celular */
  var indice = document.querySelector(".lg-indice");
  if (indice) {
    var mq = window.matchMedia("(min-width: 960px)");
    var ajusta = function () { indice.open = mq.matches; };
    ajusta();
    if (mq.addEventListener) mq.addEventListener("change", ajusta); else if (mq.addListener) mq.addListener(ajusta);
    $$("a", indice).forEach(function (a) {
      a.addEventListener("click", function () { if (!mq.matches) indice.open = false; });
    });

    /* item ativo + trilho: itens numerados e documentos sem itens (Cookies, Teleconsulta) na ordem do sumário */
    var todos = $$("ol a, .lg-indice-grupo-titulo", indice).filter(function (a) {
      if (a.classList.contains("lg-indice-grupo-titulo")) return !a.parentNode.querySelector("ol");
      return !a.parentNode.hidden;
    });
    var links = todos.filter(function (a) { return !a.classList.contains("lg-indice-grupo-titulo"); });
    var alvos = todos.map(function (a) { return document.getElementById(a.getAttribute("href").slice(1)); });
    var listas = $$("ol", indice);
    listas.forEach(function (ol) {
      var t = document.createElement("span");
      t.className = "lg-trilho";
      t.setAttribute("aria-hidden", "true");
      t.setAttribute("data-vazio", "");
      ol.appendChild(t);
    });
    var agendado = false;
    var atualiza = function () {
      agendado = false;
      var limite = window.innerHeight * 0.32;
      var ativo = -1;
      alvos.forEach(function (el, i) { if (el && el.getBoundingClientRect().top <= limite) ativo = i; });
      todos.forEach(function (a, i) {
        if (i === ativo) a.setAttribute("aria-current", "true"); else a.removeAttribute("aria-current");
      });
      listas.forEach(function (ol) {
        var trilho = ol.querySelector(".lg-trilho");
        var lidos = links.filter(function (a) { return ol.contains(a) && todos.indexOf(a) <= ativo; });
        if (!lidos.length) { trilho.style.height = "0px"; trilho.setAttribute("data-vazio", ""); return; }
        var ref = lidos[lidos.length - 1];
        trilho.style.height = Math.max(0, ref.offsetTop + ref.offsetHeight / 2 - 6) + "px";
        if (ref.getAttribute("aria-current") === "true") trilho.removeAttribute("data-vazio"); else trilho.setAttribute("data-vazio", "");
      });
    };
    var pede = function () { if (!agendado) { agendado = true; requestAnimationFrame(atualiza); } };
    window.addEventListener("scroll", pede, { passive: true });
    window.addEventListener("resize", pede);
    atualiza();
  }

  /* traço que se desenha quando entra na tela */
  var tracos = $$(".anima-traco");
  if (reduz || !("IntersectionObserver" in window)) {
    tracos.forEach(function (el) { el.classList.add("visto"); });
  } else {
    var io = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("visto"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.2 });
    tracos.forEach(function (el) { io.observe(el); });
  }
})();
