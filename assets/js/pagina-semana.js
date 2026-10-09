/* Semana Bem Nutrida · comportamento da página
   - preenche os marcadores a partir de window.CONFIG (assets/js/config.js); vazio = mantém o aviso .pendente
   - checkout e links: usam CONFIG; vazio = aviso de prévia, sem sair da página
   - medição genérica no dataLayer (checkout_clicado), sem dado de saúde, fase da vida ou condição
   - barra fixa do celular, faixa de prévia, traço que se desenha ao rolar */
(function () {
  "use strict";
  var C = window.CONFIG || {};
  var dl = (window.dataLayer = window.dataLayer || []);
  var medir = function (ev, extra) { if (window.medir) window.medir(ev, extra); else { var d = { event: ev, pagina: "semana" }; for (var k in extra || {}) d[k] = extra[k]; dl.push(d); } };
  var previa = C.previa !== false;
  var reduz = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var $$ = function (sel, raiz) { return Array.prototype.slice.call((raiz || document).querySelectorAll(sel)); };
  var vazio = function (v) { return v === undefined || v === null || String(v).trim() === ""; };

  /* faixa de prévia */
  var faixa = document.getElementById("faixa-previa");
  if (faixa && C.previa === false) faixa.hidden = true;

  /* marcadores de texto: <span data-cfg="chave" data-modelo="{v} minutos"> */
  $$("[data-cfg]").forEach(function (el) {
    var v = C[el.getAttribute("data-cfg")];
    if (vazio(v)) return; // fica o aviso pendente que já está no HTML
    if (String(v).toLowerCase() === "nenhum") { el.textContent = ""; return; }
    var modelo = el.getAttribute("data-modelo") || "{v}";
    el.textContent = modelo.replace("{v}", v);
    el.classList.remove("pendente");
  });

  /* frases inteiras que dependem de um dado: somem enquanto o dado estiver vazio (nada de bilhete interno na copy) */
  $$("[data-frase]").forEach(function (el) { el.hidden = vazio(C[el.getAttribute("data-frase")]); });

  /* CRN */
  if (!vazio(C.crn)) {
    $$("[data-crn]").forEach(function (el) {
      el.textContent = "CRN-" + C.crn;
      el.classList.remove("pendente");
    });
  }

  /* contatos */
  function trocaPorLink(el, href, texto, externo) {
    var a = document.createElement("a");
    a.href = href;
    a.textContent = texto;
    if (externo) a.rel = "noopener";
    el.replaceWith(a);
  }
  $$("[data-contato]").forEach(function (el) {
    var tipo = el.getAttribute("data-contato");
    if (tipo === "whatsapp" && !vazio(C.whatsapp)) {
      var num = String(C.whatsapp).replace(/\D/g, "");
      trocaPorLink(el, "https://wa.me/" + num, "WhatsApp " + (C.whatsappExibicao || ""), true);
    } else if (tipo === "email" && !vazio(C.email)) {
      trocaPorLink(el, "mailto:" + C.email, C.email, false);
    }
  });

  /* contatos para suporte e devolução (WhatsApp e/ou e-mail); vazio = um pendente curto só */
  $$("[data-contatos]").forEach(function (el) {
    var partes = [];
    if (!vazio(C.whatsapp)) partes.push({ href: "https://wa.me/" + String(C.whatsapp).replace(/\D/g, ""), txt: "WhatsApp " + (C.whatsappExibicao || "") });
    if (!vazio(C.email)) partes.push({ href: "mailto:" + C.email, txt: C.email });
    if (!partes.length) return;
    el.textContent = "pelo ";
    partes.forEach(function (pt, i) {
      if (i) el.appendChild(document.createTextNode(" ou "));
      var a = document.createElement("a"); a.href = pt.href; a.textContent = pt.txt.trim();
      if (/^https/.test(pt.href)) a.rel = "noopener";
      el.appendChild(a);
    });
  });

  /* aviso curto de prévia */
  var toast = document.getElementById("aviso-previa");
  var tt;
  function aviso(msg) {
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add("on");
    clearTimeout(tt);
    tt = setTimeout(function () { toast.classList.remove("on"); }, 3600);
  }

  /* checkout: só liga com o link E com a identificação de quem vende e o caminho da devolução (CDC art. 49, Decreto 7.962/2013) */
  var checkout = C.linkCheckoutSemana;
  var vendedorOk = !vazio(C.nomeVendedor) && !vazio(C.cpfCnpj) && !vazio(C.enderecoFiscal) && (!vazio(C.email) || !vazio(C.whatsapp));
  var podeVender = !vazio(checkout) && vendedorOk && C.semanaPronta === true;
  if (!podeVender && !previa) {
    /* publicado sem checkout pronto: nada de botão de compra morto. Vira "avise-me" e o preço some */
    $$("[data-checkout]").forEach(function (a) {
      a.removeAttribute("data-checkout");
      a.href = "comunidade.html#lista";
      var seta = a.querySelector("svg");
      a.textContent = "Quero ser avisada quando abrir ";
      if (seta) a.appendChild(seta);
      a.addEventListener("click", function () { medir("lista_espera_clicado", { produto: "semana_bem_nutrida", posicao: a.getAttribute("data-posicao") || "" }); });
    });
    $$("[data-preco-semana]").forEach(function (el) { el.innerHTML = "<b>Em breve</b>"; });
  }
  $$("[data-checkout]").forEach(function (a) {
    if (podeVender) a.href = checkout;
    a.addEventListener("click", function (e) {
      medir("checkout_clicado", { produto: "semana_bem_nutrida", valor: 47, moeda: "BRL", posicao: a.getAttribute("data-posicao") || "" });
      if (!podeVender) {
        e.preventDefault();
        aviso(vazio(checkout) ? "Prévia: o checkout da Semana Bem Nutrida ainda está em configuração. Nenhum dado foi enviado."
          : "Prévia: o checkout só liga com os dados de quem vende e o contato para devolução preenchidos.");
      }
    });
  });

  /* links secundários (grupo, lista de espera) */
  $$("[data-link]").forEach(function (a) {
    var url = C[a.getAttribute("data-link")];
    if (!vazio(url)) { a.href = url; a.rel = "noopener"; }
    a.addEventListener("click", function (e) {
      var ev = a.getAttribute("data-evento");
      if (ev) medir(ev, { posicao: "conteudo" });
      if (vazio(url)) {
        e.preventDefault();
        aviso("Prévia: este link ainda está em configuração.");
      }
    });
  });

  /* links internos com evento (grupo e lista de espera vão para a página da comunidade) */
  $$("[data-evento]:not([data-link])").forEach(function (a) {
    a.addEventListener("click", function () { medir(a.getAttribute("data-evento"), { posicao: "depois" }); });
  });

  /* barra fixa do celular: aparece quando o botão do topo sai da tela, some na chamada final */
  var barra = document.getElementById("barra-fixa");
  var ctaTopo = document.getElementById("cta-topo");
  var ctaFinal = document.getElementById("cta-final");
  if (barra && ctaTopo && ctaFinal) {
    var botaoBarra = barra.querySelector("a");
    var agendado = false;
    var atualiza = function () {
      agendado = false;
      var t = ctaTopo.getBoundingClientRect();
      var f = ctaFinal.getBoundingClientRect();
      var mostra = t.bottom < 0 && f.top > window.innerHeight * 0.9;
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

  /* traço e entradas: desenha quando entra na tela (ou aparece pronto, com menos movimento) */
  var alvos = $$(".anima, .anima-traco, .sbn-revela");
  if (reduz || !("IntersectionObserver" in window)) {
    alvos.forEach(function (el) { el.classList.add("visto"); });
  } else {
    var io = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("visto"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -12% 0px", threshold: 0.15 });
    alvos.forEach(function (el) { io.observe(el); });
  }
})();
