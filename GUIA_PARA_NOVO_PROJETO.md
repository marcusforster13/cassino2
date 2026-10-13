# Briefing para um novo treinamento em VR no mesmo estilo

Este documento descreve como o projeto **"Cassino clandestino"** (treinamento VR de atendimento a denúncia de jogo de azar, PMERJ) foi construído, para servir de base a um novo cenário. É o terceiro da série, depois de "A Casa em Silêncio" (`Downloads\DV`) e "Operação Lei Seca" (`Downloads\leiseca`), e é o mais completo: use **este** como modelo.

**Como usar:** abra um novo chat com acesso à pasta `C:\Users\marcus.leite\Downloads\cassino`, preencha o tema na seção 1 e cole o texto. O restante é referência técnica para o assistente ler.

---

## 1. Texto para colar no novo chat

> Quero criar um treinamento em realidade virtual sobre **[TEMA: descreva a ocorrência em uma frase]** no Rio de Janeiro, **no mesmo estilo e com a mesma arquitetura** do projeto que está em `C:\Users\marcus.leite\Downloads\cassino`.
>
> Antes de começar, leia `GUIA_PARA_NOVO_PROJETO.md` nessa pasta e use os scripts de lá como modelo (copie e adapte, não reescreva do zero).
>
> O que eu quero:
> - Cenário 3D gerado no **Blender por script** (um `.py` que cria a cena inteira), em português e com a realidade brasileira.
> - Versão **three.js/WebXR** publicada no **Vercel** via GitHub, rodando no Meta Quest, com o sistema de versão que sempre carrega a mais nova.
> - Texturas e modelos de uso livre (CC0), iluminação pré-calculada (bake em qualidade alta), personagens animados com voz, boca e olhar.
> - Mecânica de treinamento baseada na **lei e no procedimento brasileiros**, com variações sorteadas, modo treino, avaliação e história, e relatório com nota e base legal.
> - Eu vou **remodelar peças no Blender**: você me manda o `.glb` de cada peça simples, eu devolvo melhorada (às vezes com uma imagem de referência ou um pacote PBR) e você integra.
> - Crie o projeto na pasta `C:\Users\marcus.leite\Downloads\[PASTA]`, com repositório `https://github.com/marcusforster13/[REPO]` e projeto Vercel próprios.
>
> Antes de modelar, faça as perguntas da seção 12 do guia e pesquise a base legal.
>
> Trabalhe como no projeto anterior: fale comigo em português simples, mostre imagens do que fez, teste antes de subir, suba para o GitHub/Vercel a cada etapa e me diga sempre se a mudança já está no site (com o número da versão) ou só no seu computador.

---

## 2. Estrutura de pastas

| Pasta | Conteúdo |
|---|---|
| `01_Cena_Render_Cycles/` | `cassino.py` (**gera a cena inteira**), `cassino.blend` (resultado, não editar à mão), `integrar_modelos.py`, `aplicar_texturas_cc0.py`, `modelos/` |
| `01_.../modelos/` | peças do autor (`*.glb`), `modelos.json`, `polyhaven/` (modelos CC0 baixados), `para_editar/` (peças exportadas para o autor refazer), scripts `exportar_*.py`, `baixar_polyhaven.py`, `gerar_tela_cameras.py` |
| `02_Cena_VR_Otimizada/` | `otimizar_para_vr.py`: junta os estáticos por coleção, gera a colisão (caixas orientadas) e a UV em caixa |
| `04_ThreeJS/` | `pipeline_threejs.py` (bake de lightmaps e exportação), `texturas_cc0/` (uma pasta por material PBR), `web/` (o site) |
| `05_Treinamento/` | `cenario_cs_01.json` (toda a mecânica) e `ROTEIRO_TREINAMENTO.md` (para instrutores) |
| `06_Audio/` | `brutos/` (sons e vozes), `LISTA_SONS.md` |
| `07_Personagens/` | `converter_personagens.py`; os avatares Rocketbox ficam em `leiseca\07_Personagens\rocketbox` |
| raiz | `atualizar_tudo.ps1`, `carimbar_versao.py`, `vercel.json`, `README.md`, `CREDITOS.md`, `imagens/` |

**Regra central:** a fonte é o **script** `cassino.py`. O `.blend` é refeito do zero a cada rodada (`recriar`); qualquer edição manual nele se perde. O que o autor modela entra como `.glb` em `modelos/`.

## 3. Pipeline (`atualizar_tudo.ps1 recriar alta`)

Roda o Blender sem interface, nesta ordem (uns 15 minutos em qualidade alta):

1. `cassino.py` cria a cena: coleções numeradas por cômodo, materiais, luzes, câmeras e pontos de referência.
2. `integrar_modelos.py` troca objetos da cena por peças do autor, conforme `modelos.json`.
3. `aplicar_texturas_cc0.py` aplica os PBR (tabela `material → pasta, tamanho do ladrilho, cor`; dicionário `METAL` para os metálicos).
4. `otimizar_para_vr.py` junta os objetos estáticos de cada coleção e gera `colisao.glb`.
5. `pipeline_threejs.py` assa um lightmap por coleção no Cycles e exporta `web/cena.glb` (Draco) + `cena.json`.
6. `converter_personagens.py` refaz só os personagens que mudaram (`SO=papel` converte um só).

Depois: `python carimbar_versao.py`, `git add -A`, commit, push e conferir `versao.json` no site publicado.

**Sempre bake em `alta`** (o autor prefere esperar). Avisar o tempo e dizer que ainda não está no site.

## 4. Coleções e iluminação

- Uma coleção por área (`01_Rua` … `11_Sala_Reservada`) recebe lightmap.
- **Ficam fora do lightmap** (`SEM_LIGHTMAP` no pipeline) e recebem luz uniforme no site: `08_Interativos`, `12_Cadeiras_Plastico`, `13_Garrafas` (cômodo claro) e `14_Garrafas_Escuro` (cômodos escuros, ×0,4).
- **Peça pequena ou fina sai manchada ou preta no lightmap** (ripas, garrafas, teclas, grades, folhas): colocar nas coleções sem lightmap.
- Objeto que abre (cofre, geladeira) não pode ter o interior no lightmap: a luz é calculada com a porta fechada e o interior fica preto.
- Metal puro fica preto no site à noite: usar metalicidade moderada (0,25 a 0,5).
- Materiais com prefixo `Modelo_` ou `Img_` mantêm a UV do autor; os demais recebem UV em caixa. Imagens `Modelo_` são reduzidas para JPG de até 1024 px (perdem a transparência).

## 5. Fluxo de peças com o autor

1. **Exportar:** `exportar_*.py` tira a peça de `cassino.blend` para `modelos/para_editar/nome.glb`, centrada, base em z = 0, na orientação da cena. Dizer o tamanho, para que lado fica a frente e quantas cópias existem.
2. **Receber:** o autor devolve o `.glb` (em `Downloads`). **Inspecionar antes de integrar**: peças, triângulos, caixa envolvente, materiais e imagens. Costuma vir:
   - sem materiais, com um pacote PBR à parte (ambientCG ou Poly Haven, **1K, JPG, normal GL**);
   - sem a imagem (o GLB sai só com a malha): usar a imagem de referência enviada na conversa, projetada na face certa;
   - em tamanho errado, fora da origem, com peças soltas ao lado ou com faces viradas.
3. **Integrar:** peças repetidas ou com lógica entram por função no `cassino.py` (malha carregada uma vez e instanciada); trocas simples entram por `modelos.json`.
4. **Conferir:** prévia rápida renderizada no Blender (enviar ao autor enquanto o bake roda) e, depois do bake, foto do site de teste. Só então subir.

Opções do `modelos.json`: `substitui` (nome, lista ou prefixo com `*`), `colecao`, `ignorar`, `pai`, `materiais` (`*maior` / `*`), `vazios`, `virar`, `deslocar`.

**Não reduzir triângulos das peças do autor** sem avisar. Modelos CC0 muito pesados (plantas com 90 mil polígonos) podem ser reduzidos, avisando.

Erros que já aconteceram (não repetir):
- material "Material.00X" do autor religado ao "Material" branco da cena: nunca religar materiais com imagem nem os de nome genérico;
- nomes mudam na importação (`Cylinder` vira `Cylinder.006`): decidir por tamanho ou posição, não pelo nome;
- faces soltas no GLB: unir vértices antes de separar ilhas;
- disco no mesmo plano do fundo (pisca) ou com a face para baixo (fica preto);
- foto recortada com fundo transparente ou branco: preencher o fundo, senão vira mancha preta ou canto branco;
- casca sem paredes internas (geladeira, cofre): criar um forro por dentro;
- comentário colado no meio de uma linha de código ao editar por substituição.

## 6. Site three.js (`04_ThreeJS/web/`)

- **three.js r160** por import map, `GLTFLoader` + `DRACOLoader`, `VRButton`, **three-mesh-bvh** para colisão.
- `index.html`: carrega a cena, aplica os lightmaps, regras por nome de material (vidros translúcidos, telas acesas, recorte por alfa) e os controles.
- `treinamento.js`: motor (painéis, personagens, portas com colisão dinâmica, itens, arma, granada, sangue, emboscada, cofre, relatório). Expõe `window.__trein._t` para testes.
- `audio.js`: sons de evento carregam primeiro; ambiente e posicionais começam conforme cada arquivo chega.
- **Versão:** `carimbar_versao.py` grava `VERSAO` no `index.html` e um `versao.json` com a marca de cada arquivo. A página consulta `versao.json` sem cache, recarrega sozinha e pede cada arquivo com `?h=marca` (só baixa de novo o que mudou). `vercel.json` com `no-store` para `/`, `index.html` e `versao.json`.
- **Controles no Quest:** analógico esquerdo anda, direito gira; gatilho direito interage e atira; A/X saca a arma e pega a granada; clique no analógico direito recarrega; Y/B abre o menu. O modelo do controle some enquanto a mão segura a arma ou a granada.
- **Arma:** o cano coincide com o raio do controle (`preparar_equipamentos.py` alinha pelo aro da boca do cano). Luz no cano, sangue no impacto, 15 tiros e recarga.
- **Granada:** fica na mão esquerda; segurar o gatilho, fazer o movimento e soltar. A velocidade vem das últimas posições da mão.

## 7. Personagens

**Onde estão os arquivos**

- **Avatares originais** (FBX + texturas, biblioteca **Rocketbox**, licença MIT): `C:\Users\marcus.leite\Downloads\leiseca\07_Personagens\rocketbox\`. **O chat novo precisa de acesso a essa pasta**, ou de uma cópia dela no projeto novo (`07_Personagens\rocketbox\`); o conversor procura primeiro no próprio projeto e depois em `leiseca`. Esses arquivos ficam fora do Git.
- **Já baixados:** `Police_Male_01`, `Police_Male_04`, `Male_Adult_01`, `_04`, `_10`, `_13`, `_14`, `_16`, `_20`, `Female_Adult_01`, `_08`, `Female_Child_01`, `Construction_Male_07`, `_08`, `Construction_Female_01`. Há miniaturas em `rocketbox\previas\`.
- **Animações já baixadas** (`rocketbox\Animacoes\`): parado (`m_`/`f_idle_neutral_01`), nervoso (`idle_nervous_01`), irritado (`m_idle_angry_01`), falando (`m_gestic_talk_neutral_01`, `f_gestic_talk_nervous_01`, `_sad_01`, `_femalestressed_01`), andando (`m_walk_fast_01`), correndo (`m_run_fast_01`), agachado (`crouch_idle`, `m_crouch_out`), respirando (`f_idle_breathe_01`).
- **Avatar ou animação nova:** baixar do repositório do Rocketbox (fonte já autorizada) e pôr na mesma pasta. Não há policial feminina baixada.
- **Conversor:** `07_Personagens\converter_personagens.py` (copiar para o projeto novo), mais `checar_personagens.py` e `LEIA-ME.md`.
- **Resultado:** `04_ThreeJS\web\personagens\<papel>.glb` e `manifest.json` (lista de animações de cada papel).

**No conversor**

- A tabela `PAPEIS` liga cada papel a um avatar e às suas animações: `"papel": ("Avatar", {"nome_no_site": "animacao_rocketbox"})`. `_civil("m" ou "f", extras)` dá o conjunto padrão: `parada`, `falando`, `nervoso`, `andando`, `correndo`, `rendido`, `algemado`, `algemado_andando`.
- **Pose por IK:** `"nome": "animacao_base+pose"`. Poses prontas: `maos_na_cabeca` (rendido), `maos_nas_costas` (algemado), `apontando` (arma com as duas mãos), `sentado_parado` (mãos nas coxas), `sentado_apontando`, `sentado_jogando` (mãos à frente, sobre mesa ou teclas), `sentado` e `sentado_entrega` (ao volante, do projeto Lei Seca), `soprando`, `bracos_para_cima`. Pose nova entra em `pose_bracos()`.
- Problemas já resolvidos (não refazer):
  - os FBX de animação trazem a pose do primeiro quadro como repouso; a animação é redirecionada osso a osso no espaço do mundo, comparando com a T-pose de um adulto;
  - crianças usam outro esqueleto (`Bip02`); o mesmo redirecionamento resolve;
  - a pelve é escalada pela altura do personagem;
  - caminhada e corrida ficam no lugar (o site move o personagem);
  - exportação glTF por faixas NLA, passo de 2 quadros, texturas em 1024 px.
- Converter um só: variável de ambiente `SO=papel`. Só refaz o que mudou; `-- --forcar` refaz todos.

**No site (`treinamento.js`)**

- `ELENCO`: `[chave, papel, nome, [x, y], [olha_x, olha_y], voz, altura]`, em coordenadas da planta do Blender. `criarNPCs(variacao)` decide quem aparece em cada variação.
- `animar(n, nome, segundos, transição)` troca a animação; `u.base` é a pose para a qual ele volta. Algemado força as animações `algemado*`.
- `rota(n, [[x, y], …], velocidade, animação, aoChegar)` move o personagem. **Personagens não colidem**: conferir a rota contra móveis e paredes.
- **Sentado:** `u.sentado`, `u.semVirar`, altura por `ALTURA_SENTADO(altura)`; ao levantar, vai para a posição de `EM_PE` (atrás da cadeira).
- **Fala:** `diz(n, texto, gesto)` toca a gravação, se houver, ou a voz do navegador, com legenda. O que vem depois da fala espera ela terminar.
- **Boca** pela análise do áudio, **piscar**, **olhar** para o jogador (pescoço e cabeça) e **área de clique** que acompanha a altura da cabeça. Ao girar um osso por código, partir da pose base quando a animação não mexe nele, senão o giro acumula.
- **Reações:** `reacoes()` roda após o anúncio da polícia (levantar as mãos, reclamar, esconder objeto, tentar sair). `renderNPC()` rende, `pessoas()` e `conferirPessoas()` controlam quem já foi reunido e qualificado.
- **Armados:** `u.arma`, `u.ameaca`, `u.atira`; `confronto()` e `tiroInimigo()` cuidam dos tiros; `emboscada()` é o atirador sentado que reage quando a passagem abre.
- Personagens não recebem lightmap: usam a luz uniforme (`ctx.iluminar`).

**Limites atuais**

- As mãos não seguram objetos de verdade (a arma do personagem é posicionada por código junto à mão).
- Não há animação de sentar, levantar ou pegar algo: troca-se de pose com uma transição curta.
- Roupas e rostos são os do Rocketbox; não há personalização.

## 8. Mecânica do treinamento (`05_Treinamento/cenario_*.json`)

- `fases[]` com `acoes` (pontos, `base` legal, `condicao`, `validar`), `erros` e `falhas_graves`.
- `variacoes` sorteadas; `condicao` no formato `variacao.x == 'y'`, com `&&` e `||`.
- `dialogos` (listas de opções com `id`, `fala`, `acao`, `erro`, `feedback`), `radio`, `historia` (capítulos com variação fixa) e `vozes.falas[]`.
- **Modos:** exploração (livre), treino (dicas do instrutor), avaliação e história. Relatório com nota 0–100, itens por fase e base legal.
- **Padrão de decisão em três caminhos**, usado na porta trancada e no cofre: pedir a quem pode abrir (certo), preservar/lacrar e informar a autoridade (certo quando não há quem abra), forçar (erro).
- **Uso da força:** a resposta proporcional pontua (ordem verbal); a resposta que funciona mas é excessiva entra como erro leve (arma apontada para quem não ameaça).
- Depois de editar o JSON, copiar para `04_ThreeJS/web/treinamento/`.
- **Todo ponto jurídico incerto leva `validar: true`** e entra no `ROTEIRO_TREINAMENTO.md`, para os instrutores confirmarem.

## 9. Áudio

- Sons em `06_Audio/brutos/`; o pipeline copia para `web/audio/`. Tiro e recarga gravados pelo autor; ambiente do Freesound (CC0).
- O som sintetizado só toca quando não existe arquivo para o evento.
- Vozes: um arquivo por fala, com o nome do catálogo. Sem gravação, voz sintética do navegador com legenda.

## 10. Regras e preferências do autor

- Português simples, sem jargão; mostrar imagens; testar antes de subir.
- **Dizer sempre** se a mudança já está no site (com a versão) ou só local, e quanto falta.
- Avisar quando terminar. Não parar para perguntar o que dá para decidir; perguntar só o que é escolha dele.
- Dizer com clareza o que **não** foi testado (o Quest quem testa é ele).
- Downloads autorizados: **Poly Haven**, **Rocketbox** e **Freesound**. Fonte nova (ex.: ambientCG) pede autorização; ele costuma baixar e mandar o zip.
- Sem logotipos de marcas e sem brasões oficiais. Texturas, modelos e sons só de licença livre; registrar em `CREDITOS.md`.
- Toda regra do treinamento com base legal; pontos incertos marcados para validação.
- Texto para o formulário de tarefas dele: em primeira pessoa, como se ele tivesse feito; versão simples ou técnica conforme pedir.

## 11. Armadilhas do ambiente (para o assistente)

- Não há Python no sistema: usar o do Blender (`C:\Program Files\Blender Foundation\Blender 5.2\5.2\python\bin\python.exe`). Não há `gh` nem Vercel CLI.
- Arquivos fora da pasta de trabalho da sessão: editar por **script de patch** gravado em arquivo (caminhos com `/`) e rodado com o Python do Blender. *Heredoc* no shell estraga barras invertidas.
- Parar o bake: só matar processos `blender.exe` com ` -b ` e `--python` na linha de comando. **Nunca fechar o Blender aberto pelo autor.**
- Servidor de testes: configuração `cassino-threejs` (porta 8003) em `DV\.claude\launch.json`; aceita `POST /__salvar?nome=` e grava em `cassino\.claude\capturas`.
- Fotos do site: um `WebGLRenderer` extra com câmera própria e `POST` ao servidor. O painel escondido pausa a animação: chamar `__trein.quadro()` por `setInterval`.
- No modo livre, entrar com a câmera no salão dispara reações: para fotografar poses, rodar o quadro com a câmera fora do cômodo.
- Falas usam a voz do navegador: nos testes, o que vem depois da fala (`diz(...).then`) demora alguns segundos.
- Prévia rápida: abrir `cassino.blend` logo depois de recriado (o bake só lê o arquivo) e renderizar no Cycles com uma câmera temporária.
- Conferir o push pela linha `main -> main` e a publicação pelo `versao.json` do site.

## 12. O que definir antes de modelar o novo treinamento

O novo chat deve perguntar e confirmar:

- **Papel do jogador** e em que condição chega (denúncia, mandado, flagrante, patrulha).
- **Local e horário**, e quais cômodos ou áreas existem.
- **Personagens** e o que cada um faz; quem é o responsável.
- **Objetos interativos e vestígios** a preservar ou apreender.
- **Variações** que mudam a conduta correta (consentimento, resistência, pessoa armada, fuga, suborno, vulneráveis).
- **Uso da força:** haverá arma, granada, confronto? Em que variação?
- **Base legal** a pesquisar e citar, e os **pontos a validar** com os instrutores.
- **Peças que o autor quer modelar** ele mesmo, e quais podem vir de modelos CC0 prontos.
