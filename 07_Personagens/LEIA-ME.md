# 07 · Personagens (Microsoft Rocketbox, licença MIT)

| Papel | Modelo | Animações |
|---|---|---|
| `pm_parceiro` | Police_Male_04 | parada, falando, andando, correndo |
| `pm_apoio` | Police_Male_01 | parada, falando, andando |
| `responsavel` | Male_Adult_14 | parada, falando, nervoso, irritado, andando, correndo, rendido, algemado, algemado_andando |
| `atendente` | Female_Adult_08 | as mesmas, sem irritado |
| `seguranca` | Male_Adult_01 | as do responsável, mais **apontando** (arma empunhada com as duas mãos) |
| `apostador_a`, `apostador_b`, `apostador_c` | Construction_Male_08, Construction_Male_07, Construction_Female_01 | parada, falando, nervoso, andando, correndo, rendido, algemado |

As poses **rendido** (mãos na cabeça), **algemado** (mãos nas costas) e **apontando** não existem na biblioteca: o conversor cria por IK sobre uma animação base.

**Pendência:** os apostadores usam avatares de operário (capacete e colete), os únicos civis extras já baixados. Para ficar mais fiel, baixar mais avatares civis (`Avatars/Adults` da biblioteca) e trocar em `PAPEIS` no conversor.

Os arquivos originais (FBX e texturas) ficam fora do Git. O conversor procura em `07_Personagens/rocketbox/` e, se não achar, usa a pasta do projeto Lei Seca (`../leiseca/07_Personagens/rocketbox`). Fonte: <https://github.com/microsoft/Microsoft-Rocketbox>.

Converter de novo, forçando todos:

    blender -b --factory-startup --python converter_personagens.py -- --forcar
