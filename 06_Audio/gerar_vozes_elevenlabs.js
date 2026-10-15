// Cassino clandestino - gera as vozes dos personagens no ElevenLabs, de uma vez (mesmo esquema do Busca e Apreensao).
//
// Como usar:
//   1. Ponha a sua chave da API do ElevenLabs no arquivo 06_Audio/chave_elevenlabs.txt (so a chave, uma linha).
//      Esse arquivo fica fora do GitHub (.gitignore). Se ele nao existir, o script usa o do Busca e Apreensao
//      (Desktop\buscaeapreensao\06_Audio\chave_elevenlabs.txt) ou a variavel de ambiente ELEVENLABS_API_KEY.
//   2. Para so ver as falas e quantos caracteres vao ser gastos, sem usar a chave:
//        node 06_Audio/gerar_vozes_elevenlabs.js --listar
//   3. Para gerar:
//        node 06_Audio/gerar_vozes_elevenlabs.js
//      Na primeira vez ele escolhe uma voz da sua conta para cada personagem e grava em 06_Audio/vozes_elevenlabs.json.
//      Para trocar a voz de alguem, troque o id ali e apague os .mp3 dessa pessoa em 06_Audio/brutos.
//      Rodar de novo so gera o que falta (nao gasta credito a toa).
//   4. Os audios vao para 06_Audio/brutos e 04_ThreeJS/web/audio, e o cenario passa a saber qual audio e de qual fala.
//      Depois e so avisar o Claude para publicar.
//
// As falas saem do proprio cenario (05_Treinamento/cenario_cs_01.json) e de algumas frases fixas do motor
// (04_ThreeJS/web/treinamento.js). O site acha o audio pelo TEXTO exato da fala.
const fs = require('fs'), path = require('path');
const AQUI = __dirname, RAIZ = path.join(AQUI, '..');
const BRUTOS = path.join(AQUI, 'brutos'), WEB_AUDIO = path.join(RAIZ, '04_ThreeJS', 'web', 'audio');
const CENARIOS = [path.join(RAIZ, '05_Treinamento', 'cenario_cs_01.json'), path.join(RAIZ, '04_ThreeJS', 'web', 'treinamento', 'cenario_cs_01.json')];
const API = 'https://api.elevenlabs.io/v1';
const MODELO = 'eleven_multilingual_v2';                 // fala portugues do Brasil com qualquer voz da conta

// perfil de cada voz: escolhe a voz da conta (genero, idade) e o jeito de falar
const PERFIL = {
  radio:       { nome: 'Sala de operações (rádio)', genero: 'male', idade: ['middle_aged', 'middle aged'], estilo: { stability: .7, similarity_boost: .8, style: .05 } },
  parceiro:    { nome: 'Policial parceiro', genero: 'male', idade: ['young', 'middle_aged', 'middle aged'], estilo: { stability: .6, similarity_boost: .8, style: .1 } },
  apoio:       { nome: 'Policial de apoio', genero: 'male', idade: ['middle_aged', 'middle aged', 'young'], estilo: { stability: .6, similarity_boost: .8, style: .1 } },
  atendente:   { nome: 'Funcionária do bar', genero: 'female', idade: ['young', 'middle_aged', 'middle aged'], estilo: { stability: .4, similarity_boost: .8, style: .35 } },
  responsavel: { nome: 'Responsável pelo local', genero: 'male', idade: ['middle_aged', 'middle aged', 'old'], estilo: { stability: .4, similarity_boost: .8, style: .4 } },
  seguranca:   { nome: 'Segurança', genero: 'male', idade: ['middle_aged', 'middle aged', 'young'], estilo: { stability: .45, similarity_boost: .8, style: .35 } },
  apostador:   { nome: 'Apostador', genero: 'male', idade: ['young', 'middle_aged', 'middle aged'], estilo: { stability: .35, similarity_boost: .8, style: .45 } },
  apostadora:  { nome: 'Apostadora', genero: 'female', idade: ['young', 'middle_aged', 'middle aged'], estilo: { stability: .35, similarity_boost: .8, style: .45 } },
  atirador:    { nome: 'Homem do sofá (sala reservada)', genero: 'male', idade: ['middle_aged', 'middle aged', 'young'], estilo: { stability: .45, similarity_boost: .8, style: .4 } },
};
// vozes femininas: o arquivo ganha o final _f (o site procura <arquivo>_f quando quem fala e mulher)
const FEMININA = new Set(['apostadora']);

// ---------------------------------------------------------------- falas
function falasDoCenario() {
  const c = JSON.parse(fs.readFileSync(CENARIOS[0], 'utf8')), D = c.dialogos, E = c.exploracao || {}, Q = c.equipe || {};
  const lista = [];
  const add = (quem, texto, quando) => { if (texto && typeof texto === 'string') lista.push({ quem, texto, quando }); };
  const todos = (quem, obj, quando) => Object.values(obj || {}).forEach(t => add(quem, t, quando));
  for (const [k, t] of Object.entries(c.radio || {})) add('radio', t, 'Rádio: ' + k);
  add('parceiro', Q.pm_parceiro, 'Conversa com o parceiro'); add('parceiro', D.resposta_parceiro, 'Parceiro acompanha a entrada');
  add('apoio', Q.pm_apoio, 'Conversa com o apoio');
  add('atendente', E.atendente, 'Modo livre'); add('atendente', D.resposta_abertura, 'Abordagem no balcão');
  todos('atendente', D.resposta_fundos, 'Pergunta sobre os fundos'); todos('atendente', D.resposta_consentimento, 'Pedido para entrar');
  add('atendente', D.resposta_funcionaria, 'Pergunta sobre o dono'); add('atendente', 'A chave fica com o dono. Eu não tenho.', 'Pedido da chave do escritório');
  add('responsavel', E.responsavel, 'Modo livre'); add('responsavel', D.responsavel && D.responsavel.resposta_quem, 'Identificação');
  add('responsavel', D.responsavel && D.responsavel.resposta_direitos, 'Direitos'); add('responsavel', D.suborno_oferta, 'Oferta de suborno');
  add('responsavel', D.resposta_chave, 'Abre o escritório'); add('responsavel', D.resposta_cofre, 'Abre o cofre'); add('responsavel', D.reclamacao_responsavel, 'Reclama ao anúncio');
  add('seguranca', E.seguranca, 'Modo livre'); add('seguranca', D.resposta_armado, 'Rendido');
  for (const quem of ['apostador', 'apostadora']) {                       // as respostas valem para os dois; cada um com a sua voz
    add(quem, E.apostador, 'Modo livre'); add(quem, D.resposta_apostador && D.resposta_apostador.reunir, 'Mandado para a parede');
    add(quem, D.resposta_apostador && D.resposta_apostador.qualificar, 'Qualificação');
  }
  add('apostador', 'Tá bom, tá bom… eu só ia embora.', 'Para com a ordem verbal');
  add('apostadora', D.resposta_apostador && D.resposta_apostador.devolver, 'Devolve as fichas');
  add('atirador', E.atirador, 'Modo livre');
  // falas que ja estavam no catalogo antigo continuam (mesmo arquivo), mesmo que nao apareçam acima
  const antigas = (c.vozes && c.vozes.falas) || [];
  return { lista, antigas };
}
function montarFalas() {
  const { lista, antigas } = falasDoCenario();
  const porTexto = new Map(antigas.map(f => [f.texto, f]));
  const cont = {}, usados = new Set(antigas.map(f => f.arquivo)), saida = [], visto = new Set();
  const novoNome = quem => { let n; do { cont[quem] = (cont[quem] || 0) + 1; n = `fala_${quem === 'apostadora' ? 'apostador' : quem}_${String(cont[quem]).padStart(2, '0')}`; } while (usados.has(n)); usados.add(n); return n; };
  for (const f of lista) {
    const chave = f.quem + '|' + f.texto; if (visto.has(chave)) continue; visto.add(chave);
    // o mesmo texto dito por homem e mulher usa o mesmo nome-base (a versao feminina e <base>_f)
    const irma = saida.find(s => s.texto === f.texto);
    const base = irma ? irma.base : (porTexto.get(f.texto)?.arquivo || novoNome(f.quem));
    saida.push({ ...f, base, arquivo: base + (FEMININA.has(f.quem) ? '_f' : ''), personagem: PERFIL[f.quem].nome });
  }
  return saida;
}

// ---------------------------------------------------------------- ElevenLabs
function chave() {
  if (process.env.ELEVENLABS_API_KEY) return process.env.ELEVENLABS_API_KEY.trim();
  for (const f of [path.join(AQUI, 'chave_elevenlabs.txt'), 'C:/Users/marcus.leite/Desktop/buscaeapreensao/06_Audio/chave_elevenlabs.txt'])
    if (fs.existsSync(f)) return fs.readFileSync(f, 'utf8').trim();
  console.error('Falta a chave: crie 06_Audio/chave_elevenlabs.txt com a sua chave da API do ElevenLabs.'); process.exit(1);
}
let KEY = null;
async function api(rota, opcoes = {}) {
  const r = await fetch(API + rota, { ...opcoes, headers: { 'xi-api-key': KEY, 'Content-Type': 'application/json', ...(opcoes.headers || {}) } });
  if (!r.ok) throw new Error(`${rota}: ${r.status} ${(await r.text()).slice(0, 300)}`);
  return r;
}
async function escolherVozes(quem) {
  const arq = path.join(AQUI, 'vozes_elevenlabs.json');
  const salvas = fs.existsSync(arq) ? JSON.parse(fs.readFileSync(arq, 'utf8')) : {};
  if (quem.every(k => salvas[k])) return salvas;
  const { voices } = await (await api('/voices')).json();
  const lab = v => v.labels || {};
  const br = v => /brazil|portug|pt-br|brasil/i.test(JSON.stringify(lab(v)) + ' ' + (v.name || '') + ' ' + (v.description || ''));
  const usadas = new Set(Object.values(salvas));
  for (const k of quem) {
    if (salvas[k]) continue; const p = PERFIL[k];
    const nota = v => (lab(v).gender === p.genero ? 10 : 0) + (p.idade.includes(lab(v).age) ? 4 - p.idade.indexOf(lab(v).age) : 0) + (br(v) ? 100 : 0) + (usadas.has(v.voice_id) ? -5 : 0);      // so voz brasileira; repete uma se faltar
    const melhor = [...voices].sort((a, b) => nota(b) - nota(a))[0];
    if (!melhor) throw new Error('Nenhuma voz encontrada na conta.');
    salvas[k] = melhor.voice_id; usadas.add(melhor.voice_id);
    console.log(`  ${k.padEnd(12)} -> ${melhor.name} (${[lab(melhor).gender, lab(melhor).age, lab(melhor).accent].filter(Boolean).join(', ')})`);
  }
  fs.writeFileSync(arq, JSON.stringify(salvas, null, 1));
  console.log('Vozes escolhidas e gravadas em 06_Audio/vozes_elevenlabs.json (pode trocar os ids ali).');
  return salvas;
}

(async () => {
  const falas = montarFalas();
  const faltam = falas.filter(f => !fs.existsSync(path.join(BRUTOS, f.arquivo + '.mp3')));
  const chars = faltam.reduce((a, f) => a + f.texto.length, 0);
  if (process.argv.includes('--listar')) {
    for (const f of falas) console.log(`${fs.existsSync(path.join(BRUTOS, f.arquivo + '.mp3')) ? 'ok ' : '   '} ${f.arquivo.padEnd(22)} ${f.quem.padEnd(12)} ${f.texto}`);
    console.log(`\n${falas.length} falas; faltam ${faltam.length}, que gastam ${chars} caracteres.`);
    return;
  }
  KEY = chave();
  fs.mkdirSync(BRUTOS, { recursive: true }); fs.mkdirSync(WEB_AUDIO, { recursive: true });
  console.log(`${falas.length} falas; faltam ${faltam.length} (${chars} caracteres).`);
  const vozes = await escolherVozes([...new Set(falas.map(f => f.quem))]);
  let feitas = 0;
  for (const f of falas) {
    const destino = path.join(BRUTOS, f.arquivo + '.mp3');
    if (!fs.existsSync(destino)) {
      const r = await api(`/text-to-speech/${vozes[f.quem]}?output_format=mp3_44100_128`, {
        method: 'POST', headers: { Accept: 'audio/mpeg' },
        body: JSON.stringify({ text: f.texto, model_id: MODELO, voice_settings: { ...PERFIL[f.quem].estilo, use_speaker_boost: true } }),
      });
      fs.writeFileSync(destino, Buffer.from(await r.arrayBuffer()));
      feitas++; console.log(`  ${f.arquivo}: ${f.texto.slice(0, 60)}`);
    }
    fs.copyFileSync(destino, path.join(WEB_AUDIO, f.arquivo + '.mp3'));
  }
  // lista de audios do site
  const man = path.join(WEB_AUDIO, 'manifest.json');
  const lista = new Set(fs.existsSync(man) ? JSON.parse(fs.readFileSync(man, 'utf8')) : []);
  for (const f of falas) lista.add(f.arquivo + '.mp3');
  fs.writeFileSync(man, JSON.stringify([...lista].sort()));
  // catalogo de falas do cenario (o site acha o audio pelo texto); uma entrada por nome-base
  for (const c of CENARIOS) {
    const cen = JSON.parse(fs.readFileSync(c, 'utf8')), vistos = new Set();
    cen.vozes = { _nota: (cen.vozes && cen.vozes._nota) || '', falas: falas.filter(f => !vistos.has(f.base) && vistos.add(f.base)).map(f => ({ arquivo: f.base, personagem: f.personagem, quando: f.quando || '', texto: f.texto })) };
    fs.writeFileSync(c, JSON.stringify(cen, null, 2) + '\n');
  }
  console.log(`Pronto: ${feitas} audios novos. Avise o Claude para publicar.`);
})().catch(e => { console.error('Erro:', e.message); process.exit(1); });
