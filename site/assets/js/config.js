/* Ana Paula Costa · Nutricionista
   CONFIG central do site. Todos os marcadores {{...}} da copy vivem aqui.
   Valor vazio ("") = pendente: o site mostra um aviso elegante (classe .pendente), nunca as chaves cruas.
   Preencha os valores reais antes de publicar e troque previa para false. */
window.CONFIG = Object.assign({
  previa: true,                       // faixa "Prévia em aprovação" + robots noindex (o noindex fica no HTML)
                                      // previa=false só vale com crn, whatsapp, email, nomeVendedor, cpfCnpj, enderecoFiscal,
                                      // cadastroENutricionista=true e formEndpoint preenchidos; senão o site.js mantém a prévia
                                      // e o _dev/qa.py reprova a publicação.
  crn: "",                            // ex.: "4 nº 12345"  → exibe "CRN-4 nº 12345"; vazio = "CRN em confirmação" (sem afirmar a região)
  whatsapp: "",                       // só dígitos com DDI, ex.: "5521999999999"
  whatsappExibicao: "",               // ex.: "(21) 99999-9999"
  email: "",                          // ex.: "contato@dominio.com.br"
  instagram: "ana_costarodrigues",
  tiktok: "ana_costarodrigues",
  linkGrupo: "",                      // formulário curto do GHL para o grupo gratuito
  linkListaEsperaComunidade: "",      // formulário da lista de espera da comunidade paga
  linkCheckoutSemana: "",             // order form do GHL da Semana Bem Nutrida
  linkCheckoutComunidade: "",         // só quando a comunidade paga abrir
  linkAgendamento: "",                // calendário do GHL da Avaliação da Fase
  vagasMes: "",                       // número real de vagas de atendimento no mês
  precoSemana: "R$ 47",
  parcelamentoSemana: "",             // ex.: "em até 2x"; "nenhum" remove o trecho
  plataformaAcesso: "",               // ex.: "uma área de membros"
  prazoAcesso: "",                    // ex.: "12 meses"
  duracaoAula: "",                    // minutos, ex.: "12"
  qtdReceitas: "",                    // ex.: "20"
  formEndpoint: "",                   // endpoint do GHL; vazio = formulário em modo prévia, sem enviar dado (com previa=false, o envio falha de propósito)
  precoAvaliacao: "",                 // ex.: "R$ 280" → "Investimento: R$ 280 (ou em até 10x)"; vazio = "informado no agendamento"
  precoAcompanhamento: "",            // ex.: "R$ 690"
  /* ---- Números das redes: uma fonte só para todas as páginas (conferir na véspera da publicação) ---- */
  redes: {
    viewsTikTok: "2,6 milhões",       // visualizações somadas no TikTok
    viewsVideoFerro: "560 mil",       // vídeo do sulfato ferroso (contagem de 563 mil arredondada para baixo)
    seguidoresInstagram: "10 mil"     // seguidores no Instagram
  },
  /* ---- Atendimentos (atendimentos.html) ---- */
  horarioSuporte: "",                 // {{HORARIO_SUPORTE}}, ex.: "dias úteis, das 9h às 18h"
  politicaRemarcacao: "",             // {{POLITICA_REMARCACAO}}, frase completa
  agendaEsgotada: false,              // true = botão vira "Entrar na lista do próximo mês" e muda a tela de sucesso
  guiaDaFase: false,                  // true só quando o PDF do Guia da Fase existir
  garantiaNoAcompanhamento: null,     // true/false depois que a Ana confirmar; null = em confirmação
  atendeOutrasCidades: null,          // true depois que a Ana confirmar; null = pergunta travada
  depoimentos: [],                     // [{texto:"...", autora:"M. S.", fase:"pós-parto"}]; vazio = seção oculta
  /* ---- Sobre (sobre.html) ---- */
  anoInicioFaculdade: "",             // {{ANO_INICIO_FACULDADE}}: "2018" ou "2019"
  motivoVirada: "",                   // {{MOTIVO_DA_VIRADA}}: uma frase da Ana, em primeira pessoa
  instituicaoGraduacao: "",           // {{INSTITUICAO_GRADUACAO}}
  cursoCoaching: { instituicao: "", confirmado: false },   // programa de coaching em nutrição integrativa (2020), curso livre
  cursoImersao: { instituicao: "", confirmado: false },    // imersão em nutrição comportamental (2024)
  congressos: [],                     // {{LISTA_CONGRESSOS}}: ["Nome do congresso · 2025", ...] só os comprovados
  cadastroENutricionista: null,       // true depois de confirmar o cadastro ativo; libera a frase sobre teleconsulta
  autorizaNomesFilhos: null,          // true = usa "Tomás e Antônio" e os marcos de 2023 e 2026; senão "dois meninos"
  mostrarFraseFe: true,               // a Ana decide se "Minha fé é o que sustenta a minha rotina." fica
  depoimentoSobre: null,              // {texto:"...", autora:"M. S.", fase:"pós-parto"} com autorização escrita; null = seção oculta
  /* ---- Comunidade (comunidade.html) ---- */
  estadoComunidade: "A",              // "A" = só grupo gratuito (hoje) · "B" = comunidade paga aberta com checkout testado
  linkConviteGrupo: "",               // {{LINK_GRUPO}}: convite do grupo de WhatsApp, mostrado só depois do cadastro
  palavraGrupo: "BEM NUTRIDA",        // palavra que a pessoa manda no WhatsApp se o botão do grupo não abrir
  numeroParticipantes: "",            // {{NUMERO_PARTICIPANTES}}: só número real; vazio = a frase não aparece
  nomeAppComunidade: "",              // {{NOME_APP_COMUNIDADE}}, ex.: "GoKollab"
  diaHorarioEncontro: "",             // {{DIA_HORARIO_ENCONTRO}}, ex.: "Quartas, às 20h"
  encontroGravado: null,              // true = mostra "Perdeu? Fica gravado para você assistir depois."
  formasPagamentoComunidade: "",      // {{FORMAS_PAGAMENTO_COMUNIDADE}}, ex.: "Pix ou cartão" (Pix só depois do teste)
  regraAcessoAposCancelar: "",        // {{REGRA_ACESSO_APOS_CANCELAR}}, frase completa
  regraCancelamentoAnual: "",         // {{REGRA_CANCELAMENTO_ANUAL}}, frase completa
  linkTermosComunidade: "",           // {{LINK_TERMOS_COMUNIDADE}}; vazio = aponta para termos.html#termos-comunidade
  fundadora: null,                    // {vagas:100, preco:"R$ 39,90", condicao:"para sempre", restantes:37} só se real; null = bloco fora
  depoimentosComunidade: [],          // [{texto:"...", autora:"M. S.", fase:"pós-parto"}] com autorização escrita; vazio = bloco fora
  /* ---- Ferro Sem Sofrimento (ferro.html) ---- */
  formEndpointFerro: "",              // endpoint do GHL da isca (tag isca-ferro); vazio = usa formEndpoint; os dois vazios = prévia sem envio
  videoPreviaFerro: "",               // {{VIDEO_PREVIA_FERRO}}: URL do .mp4 de até 40 s com legenda queimada; vazio = só a foto, sem play
  /* ---- Privacidade e Termos (privacidade.html, termos.html) ---- */
  cpfCnpj: "",                        // {{CPF_OU_CNPJ}}; se houver CNPJ, preferir o CNPJ (não expor CPF)
  enderecoFiscal: "",                 // {{CIDADE_ENDERECO_FISCAL}}, ex.: "Rio de Janeiro (RJ)" ou o endereço fiscal da empresa
  dominio: "",                        // {{DOMINIO}}, ex.: "anapaulacosta.com.br"
  dataAtualizacao: "",                // {{DATA_ATUALIZACAO}}, ex.: "9 de outubro de 2026"
  plataformaPagamento: "",            // {{PLATAFORMA_PAGAMENTO}}
  plataformaVideo: "",                // {{PLATAFORMA_VIDEO}}, ex.: "Google Meet"
  appPlano: "",                       // {{APP_PLANO}}, app onde a paciente recebe o plano
  hospedagemSite: "",                 // {{HOSPEDAGEM_SITE}}
  ferramentaAnalise: "",              // {{FERRAMENTA_ANALISE}}
  diagnosticoFase: false,             // true só se o questionário Diagnóstico da Fase estiver no ar (mostra o parágrafo e a linha da tabela)
  automacaoWhatsApp: false,           // true só se a Ana usar respostas automáticas no WhatsApp (mostra o item "Atendimento com apoio de automação")
  /* ---- Página inicial (index.html) ---- */
  dataNumeros: "",                    // {{DATA_DOS_NUMEROS}}, ex.: "outubro de 2026" (conferir os números na véspera)
  nomeVendedor: "",                   // {{NOME_OU_RAZAO_SOCIAL}} no rodapé (identificação de quem vende)
  aulaFerroPronta: false,             // true quando a aula estiver gravada e ferro.html funcionando; false = prévia com selo, publicado = oculto
  semanaPronta: false,                // true quando o kit e o checkout entregarem o acesso de verdade; idem
  linkPostLevoOuDeixo: "",            // {{LINK_POST_LEVO_OU_DEIXO}}; vazio = perfil do Instagram
  linkPostPecoOuNaoPeco: "",          // {{LINK_POST_PECO_OU_NAO_PECO}}
  linkPostCasos: "",                  // {{LINK_POST_CASOS}}
  linkReceitaBolinhoBanana: "",       // {{LINK_RECEITA_BOLINHO_BANANA}}
  linkReceitaCuscuz: "",              // {{LINK_RECEITA_CUSCUZ}}
  linkReceitaPicole: "",              // {{LINK_RECEITA_PICOLE}}
  linkReceitaBoloProteico: ""         // {{LINK_RECEITA_BOLO_PROTEICO}}
}, window.CONFIG || {});
