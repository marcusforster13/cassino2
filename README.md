# Cassino clandestino — treinamento em realidade virtual

Treinamento para policiais militares: atendimento a uma denúncia de **jogo de azar nos fundos de um bar** no Rio de Janeiro. Roda no navegador e no Meta Quest (WebXR). Mesmo estilo e arquitetura dos projetos *A Casa em Silêncio* e *Operação Lei Seca*.

**Status:** rascunho para validação com instrutores. Os itens marcados `validar` no cenário dependem de norma interna da instituição.

**Conteúdo sensível:** simula uso da força (arma de fogo e granada de efeito moral), prisão e oferta de suborno.

## O que o aluno treina

1. Chegada: rádio, apoio para cobrir os fundos, entrada com o parceiro.
2. Bar aberto ao público × porta "PRIVATIVO": quando pode entrar (flagrante visível, consentimento registrado) e quando não pode (só a denúncia anônima).
3. Contenção: anúncio, comando verbal, reação a agressão armada, fuga pelos fundos.
4. Identificação: responsável, funcionária, apostadores; oferta de dinheiro.
5. Apreensão: máquinas, dinheiro, fichas, cadernos, celular, computador, gravador das câmeras; escritório trancado; sala reservada escondida atrás de uma estante falsa no depósito do bar, com parte do dinheiro.
6. Enquadramento, algemas e condução.

Modos: exploração (cena livre), história (3 ocorrências guiadas), treino (objetivos e dicas) e avaliação (sem dicas). No fim, relatório com nota, erros, falhas graves e base legal, com download em JSON.

## Controles

| | Computador | Meta Quest |
|---|---|---|
| Andar / olhar | W A S D · arrastar o mouse | analógico esquerdo anda · direito gira |
| Falar, abrir, apreender | clique | gatilho |
| Menu (rádio, checklist) | T | botão Y ou B |
| Sacar ou guardar a arma | Q (com ela na mão, o clique dispara) | botão A (gatilho direito dispara) |
| Granada de efeito moral | E | botão X |
| Lanterna | F | grip |

Variações podem ser forçadas pelo endereço, para o instrutor: `?v=indicios:nenhum,consentimento:nega` ou `?v=seguranca:armado_reage,fuga:tentam_sair,suborno:sim`.

## Pastas

| Pasta | Conteúdo |
|---|---|
| `01_Cena_Render_Cycles/` | `cassino.py` gera `cassino.blend` do zero (a fonte de tudo); `modelos/` (viatura, arma, granada) |
| `02_Cena_VR_Otimizada/` | `otimizar_para_vr.py`: versão para Unity/Unreal e colisão |
| `04_ThreeJS/` | `pipeline_threejs.py` (lightmaps e exportação), `texturas_cc0/`, `web/` (o site) |
| `05_Treinamento/` | `cenario_cs_01.json` (toda a mecânica) e `ROTEIRO_TREINAMENTO.md` |
| `06_Audio/` | sons e roteiro de vozes |
| `07_Personagens/` | conversor dos avatares Rocketbox |

`atualizar_tudo.ps1` refaz tudo em ordem (`recriar` refaz o `.blend`; `rapido` e `alta` mudam a qualidade da luz).

## Publicação

O Vercel publica a pasta `04_ThreeJS/web` a cada envio ao GitHub (`vercel.json`). No projeto do Vercel, desligue *Settings → Deployment Protection → Vercel Authentication*, senão o site pede login e não abre no Quest.

## Créditos e licenças

Ver `CREDITOS.md`. Sem logotipos de marcas e sem brasões oficiais; os equipamentos de jogo são desenho próprio e genérico.
