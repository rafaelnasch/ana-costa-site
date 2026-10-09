/* Ana Paula Costa · Nutricionista
   Página Atendimentos: valores do CONFIG, travas de publicação, menu, régua de fases,
   traço que se desenha, barra fixa do celular, FAQ, formulário com máscara e medição genérica.
   Nenhum dado de saúde vai para o dataLayer. */
(function () {
  'use strict';
  var C = window.CONFIG || {};
  var doc = document, raiz = doc.documentElement;
  var reduzir = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $ = function (s, el) { return (el || doc).querySelector(s); };
  var $$ = function (s, el) { return Array.prototype.slice.call((el || doc).querySelectorAll(s)); };
  var vazio = function (v) { return v === undefined || v === null || String(v).trim() === ''; };

  /* ---------------------------------------------------------- medição genérica */
  window.dataLayer = window.dataLayer || [];
  function medir(evento, extra) {
    if (window.medir) return window.medir(evento, extra);   // formato único do site.js
    var d = { event: evento, pagina: 'atendimentos' };
    if (extra) for (var k in extra) d[k] = extra[k];
    window.dataLayer.push(d);
  }

  /* ---------------------------------------------------------- prévia */
  if (C.previa !== false) raiz.classList.add('previa');

  /* ---------------------------------------------------------- valores do CONFIG */
  var formatos = {
    crn: function (v) { v = String(v).trim(); return /^crn/i.test(v) ? v : 'CRN-' + v; },
    vagas: function (v) { return String(v).trim(); }
  };
  $$('.cfg[data-cfg]').forEach(function (el) {
    var chave = el.getAttribute('data-cfg');
    var v = C[chave];
    if (vazio(v)) {
      el.classList.add('pendente');
      el.setAttribute('title', 'Dado a confirmar antes da publicação');
      return;
    }
    var fmt = formatos[el.getAttribute('data-fmt') || chave];
    var texto = fmt ? fmt(v) : String(v);
    if (el.hasAttribute('data-minuscula')) texto = texto.replace(/\.$/, '');
    var link = el.getAttribute('data-link');
    if (link === 'whatsapp' && !vazio(C.whatsapp)) {
      el.innerHTML = '';
      var a = doc.createElement('a');
      a.href = 'https://wa.me/' + String(C.whatsapp).replace(/\D/g, '');
      a.rel = 'noopener'; a.target = '_blank'; a.textContent = texto;
      el.appendChild(a);
    } else if (link === 'email') {
      el.innerHTML = '';
      var m = doc.createElement('a');
      m.href = 'mailto:' + v; m.textContent = texto;
      el.appendChild(m);
    } else {
      el.textContent = texto;
    }
  });

  /* ---------------------------------------------------------- travas (itens que dependem da Ana) */
  $$('[data-trava]').forEach(function (el) {
    var v = C[el.getAttribute('data-trava')];
    if (v === true) return;                          // confirmado: publica
    if (v === false && el.getAttribute('data-trava') !== 'guiaDaFase') { el.remove(); return; }
    if (C.previa === false) { el.remove(); return; } // publicação: some
    el.classList.add('travado-previa');               // prévia: aparece sinalizado
    var tag = doc.createElement('span');
    tag.className = 'pendente pendente--pilula';
    tag.title = 'Item a confirmar antes da publicação';
    tag.textContent = 'em confirmação';
    if (el.tagName === 'DETAILS') {
      var sum = $('summary', el), span = doc.createElement('span');
      while (sum.firstChild) span.appendChild(sum.firstChild);
      span.appendChild(doc.createTextNode(' ')); span.appendChild(tag);
      sum.appendChild(span);
    } else {
      var dentro = el.querySelector(':scope > span:last-of-type') || el;
      dentro.appendChild(doc.createTextNode(' ')); dentro.appendChild(tag);
    }
  });

  /* ---------------------------------------------------------- investimento (CONFIG.precoAvaliacao / precoAcompanhamento) */
  $$('[data-preco]').forEach(function (el) {
    var v = C[el.getAttribute('data-preco')];
    var alvo = $('[data-preco-valor]', el);
    if (vazio(v)) { if (C.previa === false) el.remove(); else if (alvo) { alvo.classList.add('pendente'); alvo.title = 'Valor a confirmar antes da publicação'; } return; }
    alvo.textContent = String(v).trim();
    var parc = $('[data-preco-parcela]', el); if (parc) parc.hidden = false;
  });
  var faqPreco = $('[data-preco-faq]');
  if (faqPreco && !vazio(C.precoAvaliacao)) {
    faqPreco.textContent = 'A Avaliação da Fase custa ' + String(C.precoAvaliacao).trim() + ' (ou em até 10x no cartão)' +
      (!vazio(C.precoAcompanhamento) ? ' e o Acompanhamento da Fase, 90 dias, ' + String(C.precoAcompanhamento).trim() + '.' : '.');
    faqPreco.hidden = false;
  }

  /* ---------------------------------------------------------- agenda esgotada */
  if (C.agendaEsgotada === true) {
    $$('[data-cta-texto]').forEach(function (s) { s.textContent = 'Entrar na lista do próximo mês'; });
  }

  /* ---------------------------------------------------------- link do grupo */
  var grupo = $('[data-link-grupo]');
  if (grupo && !vazio(C.linkGrupo)) grupo.href = C.linkGrupo;

  /* ---------------------------------------------------------- aviso da aula do ferro (só para quem veio de lá) */
  var ferro = $('[data-ferro]');
  if (ferro) {
    var veioDoFerro = /ferro/i.test(doc.referrer) || /(\?|&)(origem|utm_content)=[^&]*ferro/i.test(location.search);
    if (veioDoFerro) ferro.classList.add('at-ferro--destaque');
    if (!veioDoFerro && C.previa === false) ferro.remove();
  }

  /* ---------------------------------------------------------- depoimentos */
  var depos = Array.isArray(C.depoimentos) ? C.depoimentos.filter(function (d) { return d && !vazio(d.texto); }) : [];
  var secDepo = $('[data-depoimentos]');
  if (secDepo && depos.length >= 2) {                // a partir de 2, a mesma regra da página inicial
    var lista = $('[data-depoimentos-lista]', secDepo);
    depos.slice(0, 3).forEach(function (d) {
      var f = doc.createElement('figure');
      f.className = 'at-depoimento';
      var bq = doc.createElement('blockquote'), p = doc.createElement('p');
      p.textContent = '“' + String(d.texto).replace(/^["“]|["”]$/g, '') + '”';
      bq.appendChild(p);
      var cap = doc.createElement('figcaption');
      cap.textContent = [d.autora, d.fase].filter(function (x) { return !vazio(x); }).join(' · ');
      f.appendChild(bq); f.appendChild(cap);
      lista.appendChild(f);
    });
    secDepo.hidden = false;
  } else if (secDepo) {
    secDepo.remove();
  }

  /* ---------------------------------------------------------- topo e menu */
  var topo = $('[data-topo]');
  var nav = $('.at-nav'), abrir = $('.at-nav__abrir');
  if (abrir) {
    abrir.addEventListener('click', function () {
      var aberto = nav.classList.toggle('aberto');
      abrir.setAttribute('aria-expanded', aberto ? 'true' : 'false');
    });
    doc.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('aberto')) { nav.classList.remove('aberto'); abrir.setAttribute('aria-expanded', 'false'); abrir.focus(); }
    });
    doc.addEventListener('click', function (e) {
      if (nav.classList.contains('aberto') && !nav.contains(e.target)) { nav.classList.remove('aberto'); abrir.setAttribute('aria-expanded', 'false'); }
    });
    $$('.at-nav__lista a').forEach(function (a) { a.addEventListener('click', function () { nav.classList.remove('aberto'); abrir.setAttribute('aria-expanded', 'false'); }); });
  }

  /* ---------------------------------------------------------- CTA: medição genérica */
  $$('[data-cta]').forEach(function (a) {
    a.addEventListener('click', function () { medir('agendamento_clicado', { posicao: a.getAttribute('data-local') || 'conteudo' }); });
  });

  /* ---------------------------------------------------------- observadores */
  var temIO = 'IntersectionObserver' in window;
  function aoVer(els, cb, opcoes) {
    if (!temIO || reduzir) { els.forEach(function (el) { cb(el); }); return; }
    var io = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (en) { if (en.isIntersecting) { cb(en.target); io.unobserve(en.target); } });
    }, opcoes || { rootMargin: '0px 0px -12% 0px', threshold: 0.15 });
    els.forEach(function (el) { io.observe(el); });
  }
  // o traço começa recortado (clip-path), então observamos o elemento pai
  $$('[data-rota]').forEach(function (rota) {
    aoVer([rota.parentNode], function () { rota.classList.add('desenhada'); }, { rootMargin: '0px 0px -18% 0px', threshold: 0 });
  });
  aoVer($$('.at-selo, .at-checklist, [data-passos]'), function (el) { el.classList.add('visivel'); }, { threshold: 0.3 });

  /* ---------------------------------------------------------- fases em abas: os cartões "Escolha a sua fase" mostram uma fase por vez */
  var paineis = $$('[data-painel-fase]');
  var cartoesFase = $$('.at-fase-cartao__link');
  var irParaRegua = null;
  function abrirFase(id, rolar) {
    var achou = false;
    paineis.forEach(function (sec) { var on = sec.id === id; sec.hidden = !on; if (on) achou = true; });
    if (!achou) return false;
    cartoesFase.forEach(function (a, i) {
      var on = a.getAttribute('href') === '#' + id;
      a.setAttribute('aria-expanded', on ? 'true' : 'false');
      a.parentNode.classList.toggle('ativo', on);
      if (on && irParaRegua) irParaRegua(i);
    });
    if (rolar) {
      var alvo = doc.getElementById(id);
      alvo.scrollIntoView({ behavior: reduzir ? 'auto' : 'smooth', block: 'start' });
      var t = $('h2', alvo); if (t) { t.setAttribute('tabindex', '-1'); t.focus({ preventScroll: true }); }
    }
    return true;
  }
  if (paineis.length) {
    cartoesFase.forEach(function (a) {
      a.setAttribute('aria-controls', a.getAttribute('href').slice(1));
      a.addEventListener('click', function (e) {
        e.preventDefault();
        var id = a.getAttribute('href').slice(1);
        abrirFase(id, true);
        if (history.replaceState) history.replaceState(null, '', '#' + id);
      });
    });
    var pedida = (location.hash || '').slice(1) || (new URLSearchParams(location.search).get('fase') || '');
    if (/^40/.test(pedida)) pedida = '40-mais';
    if (pedida === 'gestante') pedida = 'gestacao';
    var abriu = abrirFase(pedida, false);
    if (!abriu) abrirFase(/ferro/i.test(location.search + doc.referrer) ? 'gestacao' : 'gestacao', false);
    else if (location.hash) setTimeout(function () { abrirFase(pedida, true); }, 60);
  }

  /* ---------------------------------------------------------- régua de fases */
  var regua = $('[data-regua]');
  if (regua) {
    var rota = $('[data-regua-rota]', regua), ponto = $('[data-regua-ponto]', regua);
    var paradas = [166.7, 500, 833.3];
    var atual = -1;
    var caminho = function (x) {
      return 'M10 30 H' + (x - 84).toFixed(1) +
        ' C' + (x - 58).toFixed(1) + ' 30 ' + (x - 58).toFixed(1) + ' 50 ' + (x - 36).toFixed(1) + ' 50' +
        ' C' + (x - 14).toFixed(1) + ' 50 ' + (x - 16).toFixed(1) + ' 30 ' + x.toFixed(1) + ' 30';
    };
    var ir = function (i) {
      if (i === atual) return;
      atual = i;
      rota.setAttribute('d', caminho(paradas[i]));
      rota.style.d = 'path("' + caminho(paradas[i]) + '")';
      ponto.style.left = (paradas[i] / 10) + '%';
    };
    ir(0);
    irParaRegua = ir;
    cartoesFase.forEach(function (a, i) { if (a.getAttribute('aria-expanded') === 'true') ir(i); });
    $$('[data-regua-alvo]').forEach(function (cartao) {
      var i = parseInt(cartao.getAttribute('data-regua-alvo'), 10);
      cartao.addEventListener('mouseenter', function () { ir(i); });
      cartao.addEventListener('focusin', function () { ir(i); });
    });
  }

  /* ---------------------------------------------------------- fio do passo a passo (celular) */
  var passos = $('[data-passos]');
  if (passos && !reduzir) {
    var mq = window.matchMedia('(max-width: 959px)');
    var pedido = false;
    var atualizar = function () {
      pedido = false;
      if (!mq.matches) return;
      var r = passos.getBoundingClientRect(), vh = window.innerHeight;
      var p = (vh * 0.7 - r.top) / r.height;
      passos.style.setProperty('--progresso', Math.max(0, Math.min(1, p)).toFixed(3));
    };
    window.addEventListener('scroll', function () { if (!pedido) { pedido = true; requestAnimationFrame(atualizar); } }, { passive: true });
    window.addEventListener('resize', atualizar);
    atualizar();
  }

  /* ---------------------------------------------------------- topo com sombra + barra fixa */
  var heroCta = $('[data-cta-hero]'), barra = $('[data-barra]'), agendar = $('#agendar');
  var heroFora = false, formVisivel = false, enviado = false;
  var atualizaBarra = function () {
    if (!barra) return;
    var mostrar = heroFora && !formVisivel && !enviado;
    barra.classList.toggle('ativa', mostrar);
    barra.setAttribute('aria-hidden', mostrar ? 'false' : 'true');
    var a = $('a', barra); if (a) a.tabIndex = mostrar ? 0 : -1;
  };
  if (temIO) {
    if (heroCta) new IntersectionObserver(function (e) {
      heroFora = !e[0].isIntersecting && e[0].boundingClientRect.top < 0; atualizaBarra();
      if (topo) topo.classList.toggle('rolou', heroFora || window.scrollY > 8);
    }).observe(heroCta);
    if (agendar) new IntersectionObserver(function (e) { formVisivel = e[0].isIntersecting; atualizaBarra(); }, { threshold: 0.05 }).observe(agendar);
  }
  window.addEventListener('scroll', function () { if (topo) topo.classList.toggle('rolou', window.scrollY > 8); }, { passive: true });

  /* ---------------------------------------------------------- FAQ: uma aberta por vez (fallback para navegadores sem details[name]) */
  var faq = $('[data-faq]');
  if (faq) {
    var itens = $$('details', faq);
    itens.forEach(function (d) {
      d.addEventListener('toggle', function () {
        if (d.open) itens.forEach(function (o) { if (o !== d && o.open) o.open = false; });
      });
    });
  }

  /* ---------------------------------------------------------- formulário */
  var form = $('[data-form]');
  if (!form) return;
  var tel = $('[data-mascara-tel]', form);
  var mascara = function (v) {
    var d = v.replace(/\D/g, '');
    if (d.length > 11 && d.indexOf('55') === 0) d = d.slice(2);
    d = d.slice(0, 11);
    if (d.length <= 2) return d.length ? '(' + d : '';
    if (d.length <= 6) return '(' + d.slice(0, 2) + ') ' + d.slice(2);
    if (d.length <= 10) return '(' + d.slice(0, 2) + ') ' + d.slice(2, 6) + '-' + d.slice(6);
    return '(' + d.slice(0, 2) + ') ' + d.slice(2, 7) + '-' + d.slice(7);
  };
  if (tel) tel.addEventListener('input', function () {
    var fim = tel.selectionStart === tel.value.length;
    tel.value = mascara(tel.value);
    if (fim) tel.setSelectionRange(tel.value.length, tel.value.length);
  });

  var regras = {
    nome: function () { return form.nome.value.trim().length >= 2; },
    whatsapp: function () { var d = form.whatsapp.value.replace(/\D/g, ''); return d.length === 10 || d.length === 11; },
    email: function () { var v = form.email.value.trim(); return v === '' || /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v); },  // opcional
    fase: function () { return !!form.querySelector('input[name="fase"]:checked'); },
    periodo: function () { return !!form.querySelector('input[name="periodo"]:checked'); },
    consentimento_dados: function () { return form.consentimento_dados.checked; },
    // dado sensível: autorização destacada só é exigida quando a fase foi informada
    consentimento_fase: function () { var f = form.querySelector('input[name="fase"]:checked'); return !f || f.value === 'nao-informado' || form.consentimento_fase.checked; }
  };
  var erros = { nome: 'f-nome-erro', whatsapp: 'f-whats-erro', email: 'f-email-erro', fase: 'f-fase-erro', periodo: 'f-periodo-erro', consentimento_dados: 'f-aceite-erro', consentimento_fase: 'f-aceite-fase-erro' };
  var campos = { nome: form.nome, whatsapp: form.whatsapp, email: form.email, consentimento_dados: form.consentimento_dados, consentimento_fase: form.consentimento_fase };
  // a caixa da fase só aparece como obrigatória quando faz sentido
  var blocoFase = $('[data-consentimento-fase]', form);
  var atualizaFase = function () {
    var f = form.querySelector('input[name="fase"]:checked');
    var precisa = !!f && f.value !== 'nao-informado';
    if (blocoFase) blocoFase.classList.toggle('dispensado', !precisa);
    form.consentimento_fase.required = precisa;
    if (!precisa) { form.consentimento_fase.setAttribute('aria-invalid', 'false'); var e = doc.getElementById('f-aceite-fase-erro'); if (e) e.textContent = ''; }
  };
  $$('input[name="fase"]', form).forEach(function (r) { r.addEventListener('change', atualizaFase); });
  atualizaFase();
  var marcar = function (k, ok) {
    var p = doc.getElementById(erros[k]);
    if (p) p.textContent = ok ? '' : p.getAttribute('data-erro');
    var c = campos[k];
    if (c) c.setAttribute('aria-invalid', ok ? 'false' : 'true');
    var grupo = form.querySelector('input[name="' + k + '"]');
    if (grupo && grupo.type === 'radio') $$('input[name="' + k + '"]', form).forEach(function (r) { r.setAttribute('aria-invalid', ok ? 'false' : 'true'); });
    return ok;
  };
  // validar ao sair do campo sem mudar o layout no meio de um toque/clique (senão o clique "escorrega")
  var ponteiroAbaixo = false, pendentes = [];
  doc.addEventListener('pointerdown', function () { ponteiroAbaixo = true; }, true);
  doc.addEventListener('pointerup', function () {
    ponteiroAbaixo = false;
    setTimeout(function () { var f; while ((f = pendentes.shift())) f(); }, 0);
  }, true);
  var depois = function (fn) { if (ponteiroAbaixo) pendentes.push(fn); else fn(); };
  Object.keys(regras).forEach(function (k) {
    var alvo = campos[k];
    if (alvo && alvo.type !== 'checkbox' && k !== 'email') {
      alvo.addEventListener('blur', function () { if (alvo.value.trim()) depois(function () { marcar(k, regras[k]()); }); });
      alvo.addEventListener('input', function () { if (alvo.getAttribute('aria-invalid') === 'true' && regras[k]()) marcar(k, true); });
    }
    $$('input[name="' + k + '"]', form).forEach(function (i) { i.addEventListener('change', function () { marcar(k, regras[k]()); }); });
  });

  var cartao = $('[data-form-cartao]');
  var sucesso = $('[data-sucesso]', cartao);
  var falha = $('[data-falha]', form);
  var botao = $('[data-enviar]', form);

  var mostrarSucesso = function (nome, modoPrevia) {
    enviado = true; atualizaBarra();
    var primeiro = (nome || '').trim().split(/\s+/)[0];
    var alvoNome = $('[data-nome]', sucesso);
    if (primeiro && alvoNome) alvoNome.textContent = primeiro;
    else if (alvoNome) alvoNome.parentNode.textContent = 'Recebi seu pedido';
    if (C.agendaEsgotada === true) { $('[data-sucesso-normal]', sucesso).hidden = true; $('[data-sucesso-lista]', sucesso).hidden = false; }
    var cal = $('[data-calendario]', sucesso), linhaCal = $('[data-agenda-link]', sucesso);
    if (!vazio(C.linkAgendamento) && cal) {
      cal.href = C.linkAgendamento;
      cal.classList.remove('at-botao--contorno');      // com agenda configurada, ver horários vira a ação principal
      cal.classList.add('at-botao--cheio');
      cal.addEventListener('click', function () { medir('agendamento_clicado', { posicao: 'sucesso' }); });
    } else if (linhaCal) {
      if (C.previa === false) linhaCal.remove();
      else linhaCal.innerHTML = '<span class="cfg pendente" title="Dado a confirmar antes da publicação">Link da agenda em configuração</span>';
    }
    if (modoPrevia) $('[data-previa-nota]', sucesso).hidden = false;
    form.hidden = true;
    sucesso.hidden = false;
    sucesso.focus({ preventScroll: true });
    var topoCartao = cartao.getBoundingClientRect().top + window.scrollY - 100;
    window.scrollTo({ top: topoCartao, behavior: reduzir ? 'auto' : 'smooth' });
  };

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    falha.hidden = true;
    var primeiroErro = null;
    Object.keys(regras).forEach(function (k) {
      var ok = marcar(k, regras[k]());
      if (!ok && !primeiroErro) primeiroErro = campos[k] || form.querySelector('input[name="' + k + '"]');
    });
    if (primeiroErro) { primeiroErro.focus(); return; }
    if (form.site.value) { mostrarSucesso('', true); return; } // robô: finge sucesso, não envia

    var nome = form.nome.value.trim();
    var endpoint = C.formEndpoint;
    if (vazio(endpoint)) {
      if (C.previa === false) {                  // publicado sem endpoint: nunca fingir sucesso (o pedido se perderia)
        falha.hidden = false;
        if (window.console) console.error('formEndpoint vazio em produção: o pedido de agendamento não foi enviado.');
        return;
      }
      medir('lead', { formulario: 'avaliacao', previa: true });   // prévia: nenhum dado sai do navegador
      mostrarSucesso(nome, true);
      return;
    }
    var faseMarcada = form.querySelector('input[name="fase"]:checked').value;
    var dados = {
      nome: nome,
      telefone: '+55' + form.whatsapp.value.replace(/\D/g, ''),
      email: form.email.value.trim(),
      fase: (faseMarcada === 'nao-informado' || form.consentimento_fase.checked) ? faseMarcada : 'nao-informado',
      periodo: form.querySelector('input[name="periodo"]:checked').value,
      consentimento_dados: true,
      consentimento_fase: faseMarcada !== 'nao-informado' && form.consentimento_fase.checked,
      consentimento_conteudo: form.consentimento_conteudo.checked,
      consentimento_em: new Date().toISOString(),
      versao_politica: C.dataAtualizacao || 'previa',
      origem: 'site-atendimentos' + (/(\?|&)origem=ferro/i.test(location.search) ? '-ferro' : ''),
      lista_espera: C.agendaEsgotada === true
    };
    botao.disabled = true; botao.setAttribute('aria-disabled', 'true');
    fetch(endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(dados) })
      .then(function (r) { if (!r.ok) throw new Error('http ' + r.status); })
      .then(function () {
        medir('lead', { formulario: 'avaliacao' }); // evento genérico: sem nome, fase ou contato
        mostrarSucesso(nome, false);
      })
      .catch(function () { falha.hidden = false; })
      .then(function () { botao.disabled = false; botao.removeAttribute('aria-disabled'); });
  });
})();
