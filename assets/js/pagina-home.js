/* Ana Paula Costa · Nutricionista · página inicial
   - marcadores a partir de window.CONFIG (assets/js/config.js); vazio = mantém o aviso .pendente
   - blocos que dependem de produto pronto (data-pronto): tratados no site.js
   - régua de fases (abas acessíveis) com a rota que mergulha e pousa na fase escolhida
   - traço do método que se desenha ao rolar
   - medição genérica no dataLayer (agendamento_clicado), sem dado de saúde nem fase da vida
   - menu do celular, barra fixa do celular, faixa de prévia */
(function () {
  "use strict";
  var C = window.CONFIG || {};
  var dl = (window.dataLayer = window.dataLayer || []);
  var reduz = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var vazio = function (v) { return v === undefined || v === null || String(v).trim() === ""; };
  var previa = C.previa !== false;

  /* ---------------------------------------------------------- prévia */
  var faixa = $("#faixa-previa");
  if (faixa && !previa) faixa.hidden = true;

  /* ---------------------------------------------------------- marcadores */
  $$("[data-cfg]").forEach(function (el) {
    var v = C[el.getAttribute("data-cfg")];
    if (vazio(v)) return;
    el.textContent = (el.getAttribute("data-modelo") || "{v}").replace("{v}", v);
    el.classList.remove("pendente");
  });
  if (!vazio(C.crn)) {
    $$("[data-crn]").forEach(function (el) { el.textContent = "CRN-" + C.crn; el.classList.remove("pendente"); });
  }
  function trocaPorLink(el, href, texto, externo) {
    var a = document.createElement("a");
    a.href = href; a.textContent = texto;
    if (externo) a.rel = "noopener";
    el.replaceWith(a);
  }
  $$("[data-contato]").forEach(function (el) {
    var tipo = el.getAttribute("data-contato");
    if (tipo === "whatsapp" && !vazio(C.whatsapp)) {
      trocaPorLink(el, "https://wa.me/" + String(C.whatsapp).replace(/\D/g, ""), "WhatsApp " + (C.whatsappExibicao || ""), true);
    } else if (tipo === "email" && !vazio(C.email)) {
      trocaPorLink(el, "mailto:" + C.email, C.email, false);
    }
  });
  $$("[data-href-cfg]").forEach(function (a) {
    var v = C[a.getAttribute("data-href-cfg")];
    if (!vazio(v)) a.href = v;
  });
  $$("[data-oculta-se]").forEach(function (el) { if (C[el.getAttribute("data-oculta-se")] === true) el.remove(); });
  $$("[data-ano]").forEach(function (el) { el.textContent = new Date().getFullYear(); });

  /* ---------------------------------------------------------- depoimentos (a partir de 2 autorizados, a mesma regra de Atendimentos) */
  var depo = Array.isArray(C.depoimentos) ? C.depoimentos.filter(function (d) { return d && !vazio(d.texto); }) : [];
  var secDepo = $("[data-depoimentos]");
  if (secDepo && depo.length >= 2) {
    var lista = $("[data-depo-lista]", secDepo);
    depo.slice(0, 3).forEach(function (d) {
      var f = document.createElement("figure");
      f.className = "hm-depo";
      var q = document.createElement("blockquote");
      q.textContent = d.texto;
      var cap = document.createElement("figcaption");
      cap.textContent = [d.autora, d.fase].filter(function (x) { return !vazio(x); }).join(", ");
      f.appendChild(q); f.appendChild(cap); lista.appendChild(f);
    });
    secDepo.hidden = false;
  }

  /* ---------------------------------------------------------- medição genérica */
  $$("[data-agendar]").forEach(function (a) {
    a.addEventListener("click", function () {
      window.medir("agendamento_clicado", { posicao: a.getAttribute("data-posicao") || "" });
    });
  });

  $$("[data-lista-espera]").forEach(function (a) {
    a.addEventListener("click", function () { window.medir("lista_espera_clicado", { posicao: "caminhos" }); });
  });

  /* ---------------------------------------------------------- cabeçalho e menu */
  var topo = $("#topo");
  var botaoMenu = $(".hm-menu-botao");
  var menu = $("#menu");
  function fechaMenu() {
    if (!menu.classList.contains("aberto")) return;
    menu.classList.remove("aberto");
    botaoMenu.setAttribute("aria-expanded", "false");
    botaoMenu.setAttribute("aria-label", "Abrir menu");
  }
  if (botaoMenu && menu) {
    botaoMenu.addEventListener("click", function () {
      var abre = !menu.classList.contains("aberto");
      menu.classList.toggle("aberto", abre);
      botaoMenu.setAttribute("aria-expanded", String(abre));
      botaoMenu.setAttribute("aria-label", abre ? "Fechar menu" : "Abrir menu");
      if (abre) { var p = $("a", menu); if (p) p.focus(); }
    });
    menu.addEventListener("click", function (e) { if (e.target.closest("a")) fechaMenu(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && menu.classList.contains("aberto")) { fechaMenu(); botaoMenu.focus(); } });
    document.addEventListener("click", function (e) { if (!e.target.closest("#topo")) fechaMenu(); });
  }

  /* ---------------------------------------------------------- régua de fases */
  var regua = $("[data-regua]");
  if (regua) {
    var abas = $$("[role=tab]", regua);
    var paineis = $$("[role=tabpanel]", regua);
    var trilho = $(".hm-regua-trilho", regua);
    var svg = $(".hm-regua-svg", regua);
    var pFundo = $(".hm-regua-fundo", regua);
    var pRota = $(".hm-regua-rota", regua);
    var ponto = $(".hm-regua-ponto", regua);
    var atual = abas.filter(function (a) { return a.getAttribute("aria-selected") === "true"; })[0] || abas[0];
    // ?fase=gestacao|pos-parto|40-mais abre a régua na fase de quem chegou (bio, campanha)
    var pedida = (new URLSearchParams(location.search).get("fase") || "").toLowerCase().replace("40mais", "40-mais").replace("40", "40-mais").replace("40-mais-mais", "40-mais");
    abas.forEach(function (a) { if (a.getAttribute("data-fase-alvo") === pedida) atual = a; });
    abas.forEach(function (a) { var sel = a === atual; a.setAttribute("aria-selected", String(sel)); a.tabIndex = sel ? 0 : -1; });
    regua.setAttribute("data-ativa", atual.getAttribute("data-fase-alvo"));

    function desenhaRegua(animar) {
      if (!trilho || !trilho.offsetWidth) return;
      var w = trilho.offsetWidth, h = trilho.offsetHeight, y = 14;
      var tr = trilho.getBoundingClientRect();
      var ab = atual.getBoundingClientRect();
      var x = ab.left + ab.width / 2 - tr.left;
      svg.setAttribute("viewBox", "0 0 " + w + " " + h);
      pFundo.setAttribute("d", "M0 " + y + " H" + w);
      // corre reta, mergulha uma vez, sobe e pousa no ponto
      var m = Math.min(90, Math.max(56, x * 0.35));
      var d = "M0 " + y + " H" + (x - m) +
        " C" + (x - m * 0.62) + " " + y + " " + (x - m * 0.66) + " " + (y + 20) + " " + (x - m * 0.38) + " " + (y + 20) +
        " C" + (x - m * 0.14) + " " + (y + 20) + " " + (x - m * 0.12) + " " + y + " " + (x - 9) + " " + y;
      pRota.setAttribute("d", d);
      var len = pRota.getTotalLength();
      pRota.style.strokeDasharray = len;
      if (animar && !reduz) {
        pRota.style.transition = "none";
        pRota.style.strokeDashoffset = len;
        pRota.getBoundingClientRect();
        pRota.style.transition = "stroke-dashoffset var(--t-traco) var(--mare)";
      }
      pRota.style.strokeDashoffset = 0;
      ponto.style.transform = "translate(" + x + "px," + y + "px)";
    }

    function seleciona(aba, foco) {
      if (aba === atual && !foco) return;
      atual = aba;
      abas.forEach(function (a) {
        var sel = a === aba;
        a.setAttribute("aria-selected", String(sel));
        a.tabIndex = sel ? 0 : -1;
      });
      paineis.forEach(function (p) {
        var sel = p.id === aba.getAttribute("aria-controls");
        p.hidden = !sel;
        if (sel && !reduz) { p.classList.remove("entra"); p.getBoundingClientRect(); p.classList.add("entra"); }
      });
      regua.setAttribute("data-ativa", aba.getAttribute("data-fase-alvo"));
      if (foco) aba.focus();
      desenhaRegua(true);
    }

    paineis.forEach(function (p) { p.hidden = p.id !== atual.getAttribute("aria-controls"); });
    abas.forEach(function (a, i) {
      a.addEventListener("click", function () { seleciona(a); });
      a.addEventListener("keydown", function (e) {
        var n = null;
        if (e.key === "ArrowRight") n = abas[(i + 1) % abas.length];
        else if (e.key === "ArrowLeft") n = abas[(i - 1 + abas.length) % abas.length];
        else if (e.key === "Home") n = abas[0];
        else if (e.key === "End") n = abas[abas.length - 1];
        if (n) { e.preventDefault(); seleciona(n, true); }
      });
    });
    desenhaRegua(false);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { desenhaRegua(false); });
    var rt;
    window.addEventListener("resize", function () { clearTimeout(rt); rt = setTimeout(function () { desenhaRegua(false); }, 120); });
  }

  /* ---------------------------------------------------------- método: o traço se desenha ao rolar */
  var passos = $("[data-passos]");
  if (passos) {
    var pSvg = $(".hm-passos-svg", passos);
    var pTrilho = $(".hm-passos-trilho", passos);
    var pTraco = $(".hm-passos-rota", passos);
    var itens = $$(".hm-passo", passos);
    var marcas = $$(".hm-passo-marca", passos);
    var total = 0, frac = [];

    function geometria() {
      var r = passos.getBoundingClientRect();
      var w = passos.offsetWidth, h = passos.offsetHeight;
      pSvg.setAttribute("viewBox", "0 0 " + w + " " + h);
      var pts = marcas.map(function (m) {
        var b = m.getBoundingClientRect();
        return { x: b.left + b.width / 2 - r.left, y: b.top + b.height / 2 - r.top };
      });
      var horiz = Math.abs(pts[0].y - pts[pts.length - 1].y) < 4;
      var p0 = pts[0], pz = pts[pts.length - 1], d;
      // um único traço do 1 ao 4, reto e suave, com uma ondulação só no meio (como o traço da marca)
      if (horiz) {
        var y = p0.y, L = pz.x - p0.x, m0 = p0.x + L * 0.36, m1 = p0.x + L * 0.64, dip = 22;
        d = "M" + p0.x + " " + y + " L" + m0 + " " + y +
          " C" + (m0 + L * 0.07) + " " + y + " " + (m0 + L * 0.07) + " " + (y + dip) + " " + (p0.x + L * 0.5) + " " + (y + dip) +
          " C" + (m1 - L * 0.07) + " " + (y + dip) + " " + (m1 - L * 0.07) + " " + y + " " + m1 + " " + y +
          " L" + pz.x + " " + y;
      } else {
        var x = p0.x, T = pz.y - p0.y, n0 = p0.y + T * 0.36, n1 = p0.y + T * 0.64, dx = 18;
        d = "M" + x + " " + p0.y + " L" + x + " " + n0 +
          " C" + x + " " + (n0 + T * 0.07) + " " + (x + dx) + " " + (n0 + T * 0.07) + " " + (x + dx) + " " + (p0.y + T * 0.5) +
          " C" + (x + dx) + " " + (n1 - T * 0.07) + " " + x + " " + (n1 - T * 0.07) + " " + x + " " + n1 +
          " L" + x + " " + pz.y;
      }
      pTrilho.setAttribute("d", d);
      pTraco.setAttribute("d", d);
      total = pTraco.getTotalLength();
      pTraco.style.strokeDasharray = total;
      // fração do caminho em que cada marca é alcançada (ponto do traço mais perto do centro da marca)
      var melhor = pts.map(function () { return Infinity; });
      frac = pts.map(function () { return 0; });
      for (var k = 0; k <= 200; k++) {
        var q = pTraco.getPointAtLength(total * k / 200);
        pts.forEach(function (pt, i) {
          var dd = (q.x - pt.x) * (q.x - pt.x) + (q.y - pt.y) * (q.y - pt.y);
          if (dd < melhor[i]) { melhor[i] = dd; frac[i] = k / 200; }
        });
      }
      frac[frac.length - 1] = 1;
    }

    function progresso() {
      var r = passos.getBoundingClientRect();
      var vh = window.innerHeight || 800;
      var p = reduz ? 1 : (vh * 0.78 - r.top) / (r.height + vh * 0.15);
      p = Math.max(0, Math.min(1, p));
      pTraco.style.strokeDashoffset = total * (1 - p);
      itens.forEach(function (it, i) { it.classList.toggle("on", p >= frac[i] - 0.001 && p > 0); });
    }

    geometria(); progresso();
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { geometria(); progresso(); });
    var pt;
    window.addEventListener("resize", function () { clearTimeout(pt); pt = setTimeout(function () { geometria(); progresso(); }, 120); });
    if (!reduz) window.addEventListener("scroll", function () { window.requestAnimationFrame(progresso); }, { passive: true });
  }

  /* ---------------------------------------------------------- cabeçalho com sombra ao rolar e barra fixa do celular */
  var barra = $("#barra-celular");
  var ctaHero = $("#cta-hero"), ctaFinal = $("#cta-final");
  var heroFora = false, finalDentro = false;
  function atualizaBarra() {
    if (!barra) return;
    var on = heroFora && !finalDentro;
    barra.classList.toggle("on", on);
    barra.setAttribute("aria-hidden", String(!on));
    var a = $("a", barra); if (a) a.tabIndex = on ? 0 : -1;
  }
  if ("IntersectionObserver" in window) {
    if (ctaHero) new IntersectionObserver(function (es) { heroFora = !es[0].isIntersecting && es[0].boundingClientRect.top < 0; atualizaBarra(); }).observe(ctaHero);
    if (ctaFinal) new IntersectionObserver(function (es) { finalDentro = es[0].isIntersecting || es[0].boundingClientRect.top < 0; atualizaBarra(); }).observe(ctaFinal);

    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("visto"); io.unobserve(e.target); } });
    }, { rootMargin: "0px 0px -8% 0px" });
    if (!reduz) $$(".hm-cab, .hm-fase, .hm-oferta, .hm-citacoes, .hm-frases, .hm-aula").forEach(function (el) {
      if (el.getBoundingClientRect().top > window.innerHeight) { el.classList.add("hm-revela"); io.observe(el); }
    });
  }
  window.addEventListener("scroll", function () { if (topo) topo.classList.toggle("rolou", window.scrollY > 8); }, { passive: true });
})();
