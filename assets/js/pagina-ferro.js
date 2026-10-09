/* Ferro Sem Sofrimento · comportamento da página
   - marcadores a partir de window.CONFIG (assets/js/config.js); vazio = mantém o aviso .pendente
   - cadastro em 2 passos num <dialog>: nome + WhatsApp + 2 consentimentos separados e desmarcados
   - envio para CONFIG.formEndpointFerro (ou formEndpoint); vazio = prévia, nenhum dado sai do navegador
   - medição genérica no dataLayer: "lead" só no envio, com isca=a01 (código neutro) e origem; nada de saúde
   - barra fixa do celular, faixa de prévia, prévia em vídeo opcional, traço que se desenha ao rolar */
(function () {
  "use strict";
  var C = window.CONFIG || {};
  var dl = (window.dataLayer = window.dataLayer || []);
  var medir = function (ev, extra) { if (window.medir) window.medir(ev, extra); else { var d = { event: ev, pagina: "ferro" }; for (var k in extra || {}) d[k] = extra[k]; dl.push(d); } };
  var reduz = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var vazio = function (v) { return v === undefined || v === null || String(v).trim() === ""; };

  /* faixa de prévia */
  var faixa = $("#faixa-previa");
  if (faixa && C.previa === false) faixa.hidden = true;

  /* marcadores de texto (ex.: data dos números) */
  $$("[data-cfg]").forEach(function (el) {
    var v = C[el.getAttribute("data-cfg")];
    if (vazio(v)) return;
    el.textContent = v; el.classList.remove("pendente");
  });

  /* CRN */
  if (!vazio(C.crn)) {
    $$("[data-crn]").forEach(function (el) { el.textContent = "CRN-" + C.crn; el.classList.remove("pendente"); });
  }

  /* contatos do rodapé */
  var numWhats = vazio(C.whatsapp) ? "" : String(C.whatsapp).replace(/\D/g, "");
  $$("[data-contato]").forEach(function (el) {
    var tipo = el.getAttribute("data-contato"), a;
    if (tipo === "whatsapp" && numWhats) {
      a = document.createElement("a");
      a.href = "https://wa.me/" + numWhats; a.rel = "noopener"; a.target = "_blank";
      a.textContent = el.getAttribute("data-rotulo") || "WhatsApp";
      a.addEventListener("click", function () { medir("contato_clicado", { canal: "whatsapp", posicao: "rodape" }); });
      el.replaceWith(a);
    } else if (tipo === "email" && !vazio(C.email)) {
      a = document.createElement("a");
      a.href = "mailto:" + C.email; a.textContent = C.email;
      el.replaceWith(a);
    }
  });

  /* toast */
  var toast = $("#aviso-previa"), tt;
  function aviso(msg) {
    if (!toast) return;
    toast.textContent = msg; toast.classList.add("on");
    clearTimeout(tt); tt = setTimeout(function () { toast.classList.remove("on"); }, 4200);
  }

  /* origem (bio, tiktok, instagram, direct) a partir de ?origem= ou utm_source */
  function origem() {
    var p = new URLSearchParams(location.search);
    var o = (p.get("origem") || p.get("utm_source") || "").toLowerCase();
    if (/tiktok/.test(o)) return "tiktok";
    if (/insta|ig/.test(o)) return "instagram";
    if (/bio|link/.test(o)) return "bio";
    if (!o) {
      var r = document.referrer || "";
      if (/tiktok\./.test(r)) return "tiktok";
      if (/instagram\./.test(r)) return "instagram";
    }
    return o ? o.replace(/[^a-z0-9_-]/g, "").slice(0, 20) || "direct" : "direct";
  }

  /* prévia em vídeo (opcional): sem som automático, com controles, legenda abaixo */
  var midia = $("#midia-topo");
  if (midia) {
    var aviso_g = $("#aviso-gravacao");
    if (!vazio(C.videoPreviaFerro)) {
      var arco = $(".fer-arco", midia), foto = $(".fer-foto-topo img", midia);
      var v = document.createElement("video");
      v.src = C.videoPreviaFerro; v.controls = true; v.playsInline = true; v.preload = "metadata";
      v.setAttribute("playsinline", ""); v.muted = true;
      if (foto) v.poster = foto.currentSrc || foto.src;
      v.setAttribute("aria-label", "Prévia da aula Ferro Sem Sofrimento, com legenda");
      arco.innerHTML = ""; arco.appendChild(v);
      var leg = $("#legenda-midia"); if (leg) leg.hidden = false;
      var card = $(".fer-cartao-aula", midia); if (card) card.hidden = true;
      if (aviso_g) aviso_g.hidden = true;
    } else if (aviso_g && (C.previa === false)) {
      aviso_g.hidden = true; // fora da prévia, a foto basta (sem botão de play)
    }
  }

  /* ---------------------------------------------------------------- cadastro */
  var dlg = $("#cadastro"), form = $("#form-ferro");
  var p1 = $("#passo-1"), p2 = $("#passo-2");
  var nome = $("#f-nome"), whats = $("#f-whats"), c1 = $("#f-c1"), c2 = $("#f-c2"), mel = $("#f-site");
  var enviar = $("#f-enviar"), eEnvio = $("#e-envio");
  var enviado = false, gatilho = null;
  var temDialog = dlg && typeof dlg.showModal === "function";

  function abrir(btn) {
    gatilho = btn;
    if (!temDialog) { dlg.setAttribute("open", ""); }
    else if (!dlg.open) dlg.showModal();
    document.documentElement.style.overflow = "hidden";
    setTimeout(function () { (enviado ? $("#passo-2-titulo") : nome).focus(); }, 60);
  }
  function fechar() {
    if (temDialog && dlg.open) dlg.close(); else dlg.removeAttribute("open");
  }
  if (dlg) {
    dlg.addEventListener("close", function () {
      document.documentElement.style.overflow = "";
      if (gatilho && document.contains(gatilho) && gatilho.offsetParent !== null) gatilho.focus();
    });
    dlg.addEventListener("click", function (e) { if (e.target === dlg) fechar(); }); // toque fora da caixa
    $$("[data-fechar]", dlg).forEach(function (b) { b.addEventListener("click", fechar); });
  }
  $$("[data-abrir-cadastro]").forEach(function (b) {
    b.addEventListener("click", function () {
      medir("cadastro_aberto", { formulario: "isca_a01", posicao: b.getAttribute("data-posicao") || "" });
      abrir(b);
    });
  });

  /* máscara (00) 00000-0000 */
  function mascara(d) {
    d = d.replace(/\D/g, "").slice(0, 11);
    if (d.length <= 2) return d.length ? "(" + d : "";
    var ddd = d.slice(0, 2), r = d.slice(2);
    if (r.length <= 4) return "(" + ddd + ") " + r;
    if (d.length <= 10) return "(" + ddd + ") " + r.slice(0, 4) + "-" + r.slice(4);
    return "(" + ddd + ") " + r.slice(0, 5) + "-" + r.slice(5);
  }
  if (whats) whats.addEventListener("input", function () {
    var fim = whats.selectionStart === whats.value.length;
    whats.value = mascara(whats.value);
    if (fim) whats.setSelectionRange(whats.value.length, whats.value.length);
  });

  function erro(campo, id, mostra) {
    var el = document.getElementById(id);
    if (el) el.hidden = !mostra;
    campo.setAttribute("aria-invalid", mostra ? "true" : "false");
  }
  function valida() {
    var ok = true, primeiro = null;
    var n = nome.value.trim();
    var d = whats.value.replace(/\D/g, "");
    var nOk = n.length >= 2, wOk = d.length >= 10 && d.length <= 11 && !/^(\d)\1+$/.test(d), cOk = c1.checked;
    erro(nome, "e-nome", !nOk); if (!nOk) { ok = false; primeiro = primeiro || nome; }
    erro(whats, "e-whats", !wOk); if (!wOk) { ok = false; primeiro = primeiro || whats; }
    erro(c1, "e-c1", !cOk); if (!cOk) { ok = false; primeiro = primeiro || c1; }
    if (primeiro) primeiro.focus();
    return ok;
  }
  [nome, whats].forEach(function (f) { f && f.addEventListener("blur", function () { if (f.getAttribute("aria-invalid") === "true") valida(); }); });
  c1 && c1.addEventListener("change", function () { if (c1.checked) erro(c1, "e-c1", false); });

  function linkWhats() {
    var msg = encodeURIComponent("Oi, Ana! Quero a aula e o Guia do Ferro Sem Sofrimento.");
    return numWhats ? "https://wa.me/" + numWhats + "?text=" + msg : "";
  }
  var botaoWhats = $("#botao-whats");
  if (botaoWhats) {
    var lw = linkWhats();
    if (lw) botaoWhats.href = lw;
    else if (C.previa === false) botaoWhats.hidden = true;   // publicado sem número: o botão some (nada de link para lugar nenhum)
    botaoWhats.addEventListener("click", function (e) {
      medir("contato_clicado", { canal: "whatsapp", posicao: "cadastro_enviado" });
      if (!lw) { e.preventDefault(); aviso("Prévia: o WhatsApp oficial da Ana ainda está em confirmação."); }
    });
  }
  $$("[data-proximo]").forEach(function (a) {
    a.addEventListener("click", function () {
      var alvo = a.getAttribute("data-proximo");
      medir(alvo === "semana" ? "checkout_clicado" : "agendamento_clicado", { posicao: "ferro_sucesso", produto: alvo === "semana" ? "semana_bem_nutrida" : "avaliacao" });
    });
  });

  function sucesso(previa) {
    enviado = true;
    p1.hidden = true; p2.hidden = false;
    var av = $("#aviso-envio-previa"); if (av) av.hidden = !previa;
    document.body.classList.add("cadastro-enviado");
    barraEstado();
    setTimeout(function () { $("#passo-2-titulo").focus(); }, 30);
  }

  if (form) form.addEventListener("submit", function (e) {
    e.preventDefault();
    eEnvio.hidden = true;
    if (mel && mel.value) { sucesso(false); return; } // robô: finge sucesso e não envia
    if (!valida()) return;
    var endpoint = !vazio(C.formEndpointFerro) ? C.formEndpointFerro : C.formEndpoint;
    var org = origem();
    if (vazio(endpoint)) {
      if (C.previa === false) {   // publicado sem endpoint: nunca fingir sucesso (a gestante esperaria uma aula que não chega)
        eEnvio.hidden = false;
        if (window.console) console.error("formEndpointFerro/formEndpoint vazios em produção: o cadastro da aula não foi enviado.");
        return;
      }
      medir("lead", { formulario: "isca_a01", origem: org, previa: true });   // prévia: nenhum dado sai do navegador
      sucesso(true);
      return;
    }
    var dados = {
      nome: nome.value.trim(),
      whatsapp: "+55" + whats.value.replace(/\D/g, ""),
      consentimento_material: c1.checked,
      consentimento_mensagens: c2.checked,
      consentimento_em: new Date().toISOString(),
      versao_politica: C.dataAtualizacao || "previa",
      tag: "isca-ferro",
      origem: org,
      pagina: "ferro"
    };
    enviar.disabled = true;
    fetch(endpoint, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(dados) })
      .then(function (r) { if (!r.ok) throw new Error(r.status); })
      .then(function () {
        medir("lead", { formulario: "isca_a01", origem: org });
        sucesso(false);
      })
      .catch(function () { eEnvio.hidden = false; })
      .then(function () { enviar.disabled = false; });
  });

  /* ---------------------------------------------------------------- barra fixa do celular */
  var barra = $("#barra-fixa"), ctaTopo = $("#cta-topo .fer-botao"), final = $("#pedido-final");
  var topoFora = false, finalVisivel = false;
  function barraEstado() {
    if (!barra) return;
    var on = topoFora && !finalVisivel && !enviado;
    barra.classList.toggle("on", on);
    barra.setAttribute("aria-hidden", on ? "false" : "true");
    var b = $("button", barra); if (b) b.tabIndex = on ? 0 : -1;
    document.body.style.setProperty("--barra-h", on ? "76px" : "0px");
  }
  if ("IntersectionObserver" in window && barra) {
    if (ctaTopo) new IntersectionObserver(function (es) {
      es.forEach(function (en) { topoFora = !en.isIntersecting && en.boundingClientRect.top < 0; });
      barraEstado();
    }).observe(ctaTopo);
    if (final) new IntersectionObserver(function (es) {
      es.forEach(function (en) { finalVisivel = en.isIntersecting; });
      barraEstado();
    }, { rootMargin: "0px 0px -15% 0px" }).observe(final);
  }

  /* ---------------------------------------------------------------- entradas e traço */
  $$(".fer-cartao, .fer-frases li").forEach(function (el) { el.classList.add("fer-sobe"); });
  var animaveis = $$(".anima-traco, .fer-sobe");
  if (reduz || !("IntersectionObserver" in window)) {
    animaveis.forEach(function (el) { el.classList.add("visto"); });
  } else {
    /* o traço começa recortado (clip-path), então observa o elemento pai, que tem área visível */
    var alvos = new Map();
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (en) {
        if (!en.isIntersecting) return;
        (alvos.get(en.target) || []).forEach(function (el) { el.classList.add("visto"); });
        io.unobserve(en.target);
      });
    }, { threshold: 0.2 });
    animaveis.forEach(function (el) {
      var obs = el.classList.contains("anima-traco") ? el.parentNode : el;
      if (!alvos.has(obs)) { alvos.set(obs, []); io.observe(obs); }
      alvos.get(obs).push(el);
    });
  }

  /* FAQ: evento genérico, sem conteúdo da pergunta */
  $$(".fer-faq details").forEach(function (d, i) {
    d.addEventListener("toggle", function () { if (d.open) medir("duvida_aberta", { indice: i + 1 }); });
  });
})();
