/* Ana Paula Costa · Nutricionista — página Sobre
   Lê window.CONFIG (assets/js/config.js). Valor vazio = pendente: aparece como .pendente na prévia
   e some (ou cai na alternativa) quando CONFIG.previa = false. Nenhum dado de saúde vai para o dataLayer. */
(function () {
  "use strict";
  var C = window.CONFIG || {};
  var previa = C.previa !== false;
  var reduz = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var vazio = function (v) { return v === undefined || v === null || String(v).trim() === ""; };

  function pendente(txt) {
    var s = document.createElement("span");
    s.className = "pendente";
    s.textContent = txt;
    return s;
  }

  /* ---------- prévia ---------- */
  var faixa = $("#faixa-previa");
  if (faixa && !previa) faixa.hidden = true;

  /* ---------- CRN ---------- */
  $$("[data-crn]").forEach(function (el) {
    el.textContent = "";
    if (!vazio(C.crn)) el.textContent = "CRN-" + String(C.crn).replace(/^CRN-?\s*/i, "");
    else el.appendChild(pendente("CRN em confirmação"));
  });

  /* ---------- textos simples ---------- */
  $$("[data-cfg]").forEach(function (el) {
    var v = C[el.getAttribute("data-cfg")];
    el.textContent = "";
    if (!vazio(v)) el.textContent = v;
    else el.appendChild(pendente(el.getAttribute("data-pendente") || "em confirmação"));
  });

  /* frase inteira da Ana (some fora da prévia se não vier) */
  $$("[data-cfg-frase]").forEach(function (el) {
    var v = C[el.getAttribute("data-cfg-frase")];
    el.textContent = "";
    if (!vazio(v)) el.textContent = String(v).trim();
    else el.remove();   /* frase inteira pendente: não aparece nem na prévia (nada de bilhete interno no meio da copy) */
  });

  /* ---------- travas: frases que dependem de confirmação da Ana ---------- */
  $$("[data-trava]").forEach(function (el) {
    if (C[el.getAttribute("data-trava")] === true) el.hidden = false; else el.remove();
  });

  /* ---------- filhos: nomes só com autorização ---------- */
  var nomes = C.autorizaNomesFilhos === true;
  $$("[data-filhos]").forEach(function (el) {
    el.hidden = (el.getAttribute("data-filhos") === "sim") !== nomes;
  });

  /* ---------- fé ---------- */
  if (C.mostrarFraseFe === false) $$("[data-fe]").forEach(function (el) { el.remove(); });

  /* ---------- cursos e certificados ---------- */
  $$("[data-curso]").forEach(function (el) {
    var c = C[el.getAttribute("data-curso")] || {};
    var inst = $("[data-curso-inst]", el), cert = $("[data-curso-cert]", el);
    if (inst) { inst.textContent = ""; if (!vazio(c.instituicao)) inst.textContent = c.instituicao; else inst.appendChild(pendente("instituição em confirmação")); }
    if (cert && c.confirmado === true) { var sep = cert.previousElementSibling; if (sep && sep.classList.contains("sb-sep")) sep.remove(); cert.remove(); }
    if (!previa && (c.confirmado !== true)) el.remove(); /* só o que tiver comprovação vai ao ar */
  });
  $$("[data-certificado]").forEach(function (el) {
    var c = C[el.getAttribute("data-certificado")] || {};
    if (c.confirmado === true) el.remove();
    else if (!previa) { var li = el.closest("li"); if (li) li.remove(); }
  });
  $$("[data-congressos]").forEach(function (el) {
    var l = Array.isArray(C.congressos) ? C.congressos.filter(function (x) { return !vazio(x); }) : [];
    if (!l.length) { if (!previa) el.remove(); return; }
    var dd = $("dd", el); dd.textContent = l.join(" · ");
  });
  /* sem nenhum curso livre comprovado, o subtítulo some junto */
  var listaLivres = $("[data-cursos-lista]");
  if (listaLivres && !listaLivres.children.length) { listaLivres.remove(); var tl = $("[data-cursos-titulo]"); if (tl) tl.remove(); }

  /* ---------- teleconsulta: só com cadastro no e-Nutricionista ---------- */
  $$("[data-enutri]").forEach(function (el) {
    if (C.cadastroENutricionista === true) return;
    if (previa) { el.appendChild(document.createTextNode(" ")); el.appendChild(pendente("cadastro no e-Nutricionista em confirmação")); }
    else el.remove();
  });

  /* ---------- depoimento (autorização escrita) ---------- */
  var dep = C.depoimentoSobre;
  var secDep = $("[data-depoimento]");
  if (secDep && dep && !vazio(dep.texto)) {
    $("[data-dep-texto]", secDep).textContent = "“" + dep.texto + "”";
    $("[data-dep-autora]", secDep).textContent = [dep.autora, dep.fase].filter(function (x) { return !vazio(x); }).join(", ");
    secDep.hidden = false;
  }

  /* ---------- contato no rodapé ---------- */
  var w = $("[data-whatsapp]");
  if (w && !vazio(C.whatsapp)) {
    w.innerHTML = "";
    var a = document.createElement("a");
    a.href = "https://wa.me/" + String(C.whatsapp).replace(/\D/g, "");
    a.rel = "noopener";
    a.textContent = "WhatsApp " + (C.whatsappExibicao || C.whatsapp);
    w.appendChild(a);
  }
  var e = $("[data-email]");
  if (e && !vazio(C.email)) {
    e.innerHTML = "";
    var m = document.createElement("a");
    m.href = "mailto:" + C.email;
    m.textContent = C.email;
    e.appendChild(m);
  }

  /* ---------- dados estruturados: CRN só quando existir ---------- */
  if (!vazio(C.crn)) {
    try {
      var ld = $("#ld-sobre"), j = JSON.parse(ld.textContent);
      j["@graph"].forEach(function (n) {
        if (n["@type"] === "Person") n.identifier = { "@type": "PropertyValue", "propertyID": "CRN", "value": "CRN-" + String(C.crn).replace(/^CRN-?\s*/i, "") };
      });
      ld.textContent = JSON.stringify(j);
    } catch (err) { /* segue sem */ }
  }

  /* ---------- medição (sem dado de saúde) ---------- */
  $$("[data-agendar]").forEach(function (a) {
    a.addEventListener("click", function () {
      if (window.medir) window.medir("agendamento_clicado", { posicao: a.getAttribute("data-posicao") || "" });
      else window.dataLayer.push({ event: "agendamento_clicado", pagina: "sobre", posicao: a.getAttribute("data-posicao") || "" });
    });
  });

  /* ---------- menu ---------- */
  var topo = $(".sb-topo"), btn = $(".sb-menu-botao");
  if (btn) {
    var fechar = function () { topo.classList.remove("aberto"); btn.setAttribute("aria-expanded", "false"); };
    btn.addEventListener("click", function () {
      var abre = !topo.classList.contains("aberto");
      topo.classList.toggle("aberto", abre);
      btn.setAttribute("aria-expanded", String(abre));
    });
    document.addEventListener("keydown", function (ev) { if (ev.key === "Escape" && topo.classList.contains("aberto")) { fechar(); btn.focus(); } });
    $$(".sb-nav a").forEach(function (l) { l.addEventListener("click", fechar); });
  }
  var marcarTopo = function () { topo && topo.classList.toggle("rolou", window.scrollY > 8); };

  /* ---------- a Rota da linha do tempo ---------- */
  var rota = $("[data-rota]");
  var estado = { total: 0, marcos: [], ok: false };

  function montarRota() {
    if (!rota) return;
    var svg = $(".sb-rota-svg", rota), trilha = $(".sb-rota-trilha", rota), traco = $(".sb-rota-traco", rota), ponto = $(".sb-rota-ponto", rota);
    var caixa = rota.getBoundingClientRect();
    var lis = $$(".sb-marco", rota).filter(function (li) { return !li.hidden; });
    var pts = lis.map(function (li) {
      var r = $(".sb-marco-pino", li).getBoundingClientRect();
      return { x: r.left + r.width / 2 - caixa.left, y: r.top + r.height / 2 - caixa.top, li: li };
    });
    if (pts.length < 2) return;
    svg.setAttribute("viewBox", "0 0 " + caixa.width + " " + caixa.height);
    var horiz = Math.abs(pts[1].y - pts[0].y) < 4;
    var a = pts[0], b = pts[1], u = pts[pts.length - 1], d, i;
    if (horiz) {
      var y = a.y, w = b.x - a.x, fundo = Math.min(68, w * 0.36), meio = a.x + w * 0.56;
      d = "M" + a.x + " " + y +
        " L" + (a.x + w * 0.16) + " " + y +
        " C" + (a.x + w * 0.34) + " " + y + " " + (meio - w * 0.2) + " " + (y + fundo) + " " + meio + " " + (y + fundo) +
        " C" + (meio + w * 0.2) + " " + (y + fundo) + " " + (b.x - w * 0.2) + " " + y + " " + b.x + " " + y +
        " L" + u.x + " " + u.y;
    } else {
      var x = a.x, h = b.y - a.y, lado = 30, meioY = a.y + h * 0.58;
      d = "M" + x + " " + a.y +
        " L" + x + " " + (a.y + h * 0.2) +
        " C" + x + " " + (a.y + h * 0.38) + " " + (x + lado) + " " + (meioY - h * 0.2) + " " + (x + lado) + " " + meioY +
        " C" + (x + lado) + " " + (meioY + h * 0.2) + " " + x + " " + (b.y - h * 0.18) + " " + x + " " + b.y +
        " L" + u.x + " " + u.y;
    }
    trilha.setAttribute("d", d);
    traco.setAttribute("d", d);
    ponto.setAttribute("cx", u.x);
    ponto.setAttribute("cy", u.y);
    ponto.setAttribute("r", horiz ? 9 : 8);
    var total = traco.getTotalLength();
    traco.style.strokeDasharray = total + " " + total;
    /* comprimento em que o traço chega a cada marco */
    var amostras = 240, marcos = pts.map(function () { return 0; });
    var melhor = pts.map(function () { return Infinity; });
    for (i = 0; i <= amostras; i++) {
      var L = total * i / amostras, p = traco.getPointAtLength(L);
      pts.forEach(function (q, k) {
        var dd = (p.x - q.x) * (p.x - q.x) + (p.y - q.y) * (p.y - q.y);
        if (dd < melhor[k]) { melhor[k] = dd; marcos[k] = L; }
      });
    }
    marcos[marcos.length - 1] = total;
    estado = { total: total, marcos: marcos, lis: pts.map(function (p) { return p.li; }), ok: true, horiz: horiz };
    desenhar();
  }

  function desenhar() {
    if (!estado.ok) return;
    var r = rota.getBoundingClientRect(), vh = window.innerHeight || 800, prog;
    if (reduz) prog = 1;
    else if (estado.horiz) prog = (vh * 0.9 - r.top) / (vh * 0.55);
    else prog = (vh * 0.72 - r.top) / Math.max(r.height, 1);
    prog = Math.max(0, Math.min(1, prog));
    var feito = estado.total * prog;
    $(".sb-rota-traco", rota).style.strokeDashoffset = String(estado.total - feito);
    estado.lis.forEach(function (li, k) { li.classList.toggle("passou", feito >= estado.marcos[k] - 2); });
    rota.classList.toggle("chegou", prog >= 0.995);
  }

  /* ---------- entrada suave dos blocos ---------- */
  if (!reduz && "IntersectionObserver" in window) {
    var alvos = $$(".sb-cap-texto, .sb-citacao, .sb-cap-foto, .sb-cap3-fotos figure, .sb-cab, .sb-manifesto-cab, .sb-principios li, .sb-trabalho-foto, .sb-fase, .sb-funciona, .sb-formacao-cab, .sb-credenciais > div");
    var io = new IntersectionObserver(function (ents) {
      ents.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("visivel"); io.unobserve(en.target); } });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    alvos.forEach(function (el, k) {
      var r = el.getBoundingClientRect();
      if (r.top < (window.innerHeight || 800)) return; /* o que já está na tela fica como está */
      el.classList.add("sb-revela");
      if (el.matches(".sb-principios li, .sb-fase, .sb-credenciais > div, .sb-cap3-fotos figure")) el.style.transitionDelay = (k % 3) * 70 + "ms";
      io.observe(el);
    });
  }

  /* ---------- barra fixa do celular: aparece quando o botão do topo sai da tela, some perto da chamada final ---------- */
  var barra = $("#barra-celular"), ctaTopo = $("#cta-topo"), ctaFinal = $("#cta-final");
  function barraEstado() {
    if (!barra || !ctaTopo || !ctaFinal) return;
    var t = ctaTopo.getBoundingClientRect(), f = ctaFinal.getBoundingClientRect(), vh = window.innerHeight || 800;
    var on = t.bottom < 0 && f.top > vh * 0.9;
    if (on === barra.classList.contains("on")) return;
    barra.classList.toggle("on", on);
    barra.setAttribute("aria-hidden", on ? "false" : "true");
    barra.inert = !on;
    var a = $("a", barra); if (a) a.tabIndex = on ? 0 : -1;
  }

  var agendado = false;
  function aoRolar() {
    if (agendado) return;
    agendado = true;
    requestAnimationFrame(function () { agendado = false; marcarTopo(); desenhar(); barraEstado(); });
  }
  var tReflow;
  function aoRedimensionar() { clearTimeout(tReflow); tReflow = setTimeout(montarRota, 120); }

  window.addEventListener("scroll", aoRolar, { passive: true });
  window.addEventListener("resize", aoRedimensionar);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(montarRota);
  window.addEventListener("load", montarRota);
  montarRota();
  marcarTopo();
})();
