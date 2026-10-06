# Diagnóstico da base — Projeto de Extensão AACD

Primeira leitura da base com olhar de ciência de dados. Cobre o que a Atividade 1
pede (base organizada, tabela de problemas, primeiros números) e já antecipa o que
as Atividades 2 e 3 vão encontrar.

Tudo aqui é reproduzível com `python3 scripts/diagnostico.py`.

---

## 0. Antes de tudo: o repositório está público

O repositório `uvini07/aacd` está com visibilidade **pública** e contém
`base_quedas_AACD_anonimizada.xlsx`, com dados reais de saúde de 282 pacientes.

As regras do projeto dizem, literalmente: *"A base só circula entre a turma. Não
publiquem, não compartilhem"*. Mesmo anonimizada, a base é um dado pessoal
sensível sob a LGPD, e um conjunto de idade + diagnóstico + status funcional
permite reidentificação em uma população pequena.

**Ação sugerida, antes de qualquer análise:** tornar o repositório privado em
Settings → General → Danger Zone → Change visibility. Se a base já ficou exposta,
vale avisar a coordenação — o histórico do git guarda o arquivo mesmo depois de
apagado, e limpar isso exige reescrever o histórico.

---

## 1. Como a planilha está montada

| | 60+ | 60− |
|---|---|---|
| Pacientes | 166 | 116 |
| Colunas | 27 | 27 |
| Linhas por paciente | 2 | 2 |

O detalhe que trava qualquer leitura automática: **cada paciente ocupa duas linhas**,
com 3.839 células mescladas na aba 60+ e 2.769 na 60−. Quem abrir com
`pd.read_excel()` sem tratar isso vai ler 332 "pacientes" na aba 60+, metade deles
em branco.

A boa notícia: as duas linhas do bloco **nunca se contradizem** (verificado em todos
os 282 blocos). Onde a célula não foi mesclada, o valor caiu na segunda linha — basta
tomar o primeiro valor não-vazio do par. É o que `scripts/diagnostico.py` faz.

Os IDs são íntegros: 1–166 e 1–116, sem buraco e sem repetição.

---

## 2. Quantos caem

| | 60+ | 60− |
|---|---|---|
| Com desfecho registrado | 161/166 (97,0%) | 114/116 (98,3%) |
| Caiu ao menos 1× no ano | **88 (54,7%)** | 59 (51,8%) |
| Caiu 2× ou mais | 51 (31,7%) | 28 (24,6%) |

Metade da população caiu. Para modelagem isso é ótimo — classes equilibradas, sem
necessidade de reamostragem. O piso de comparação ("chutar sempre que caiu") acerta
54,7%, e é contra esse número que qualquer modelo tem de provar valor.

---

## 3. O achado que muda o desenho do estudo

Cruzando queda com forma de locomoção na aba 60+:

| Grupo | Caiu | Taxa |
|---|---|---|
| Anda | 60/99 | **61%** |
| Cadeirante | 19/49 | **39%** |

*p = 0,015 (Fisher)*

**Quem anda cai mais que quem usa cadeira de rodas.** Não é um erro da base: é
exposição. Para cair andando é preciso andar. O paciente mais comprometido, que se
locomove em cadeira, está protegido do desfecho justamente pela gravidade.

A consequência é direta e vale para o projeto inteiro: **misturar cadeirantes e
deambuladores na mesma análise cancela o efeito de todos os testes físicos.** Os
testes medem comprometimento; o desfecho exige exposição; e os dois andam em
direções opostas.

É por isso que, na base completa, praticamente nada separa quem caiu de quem não
caiu (todos Mann-Whitney, aba 60+):

| Teste | Caiu (mediana) | Não caiu (mediana) | p |
|---|---|---|---|
| Idade | 68 | 67 | 0,76 |
| Dinamômetro | 25 | 26 | 0,63 |
| Ponte | 16 | 16,5 | 0,25 |
| Sentar/levantar 30 s | 7 | 7 | 0,37 |
| Reação BlazePod | 31 | 32 | 0,77 |
| Reação BlazePod DT | 20 | 19,5 | 0,78 |
| Tempo 10 m | 27 | 27 | 0,57 |
| MoCA | 22 | 19 | 0,39 |
| 10-CS | 9 | 8 | 0,35 |
| Velocidade de marcha | 0,38 | 0,50 | 0,42 |
| Custo de dupla tarefa | 36,1% | 28,1% | 0,22 |

Nenhum p abaixo de 0,05. Lido sem cuidado, o resultado é "os testes não servem" — e
essa conclusão estaria errada.

### O que aparece quando se estratifica

Restringindo aos 99 pacientes 60+ que andam, e trocando o desfecho para **queda
recorrente (2 ou mais)**:

| Variável | Recorrente | Não recorrente | p |
|---|---|---|---|
| **Sentar/levantar 30 s** | 4 rep | 7 rep | **0,023** |
| Ponte | 16 s | 18 s | 0,063 |
| Dinamômetro | 22 | 28 | 0,10 |

E para o desfecho "caiu ao menos uma vez", ainda entre os que andam:

| Variável | Taxa de queda | p |
|---|---|---|
| **Polifarmácia (sim vs não)** | 70% vs 46% | **0,028** |
| Usa dispositivo de marcha | 65% vs 41% | 0,098 |

Ou seja: **há sinal na base, mas ele só aparece no subgrupo certo, com o desfecho
certo.** Força de membros inferiores discrimina queda recorrente entre quem anda;
polifarmácia discrimina queda entre quem anda. São dois resultados defensáveis, e
os dois somem se a análise for feita na base inteira.

Ressalva honesta: sentar/levantar só tem 39 pacientes entre os que andam. O p de
0,023 é real, mas frágil — é uma pista para confirmar na próxima coleta, não um
achado fechado.

---

## 4. Os valores de referência dos artigos não discriminam aqui

As referências do repositório dão cortes prontos. Aplicados à aba 60+:

| Referência | Corte | Resultado |
|---|---|---|
| World Falls Guidelines 2022 (ref. 1) | Velocidade < 0,8 m/s | **75,5%** abaixo (80/106) |
| Força de preensão — EWGSOP2, 2019 | < 27 kg H / < 16 kg M | **31,7%** abaixo (51/161) |
| MoCA (ref. 5) | < 26 | **86,7%** abaixo (65/75) |
| 10-CS (ref. 6) | ≤ 5 provável déficit | 6 pacientes; 17 possível; 42 normais |

Velocidade mediana de marcha: **0,42 m/s** — metade do corte internacional. O corte
de 0,8 m/s foi construído em idosos da comunidade, não em pessoas com amputação,
sequela de AVC ou lesão medular. Aqui ele classifica três de cada quatro pacientes
como "de risco" e por isso não prioriza ninguém. O mesmo vale para o MoCA.

Isso não invalida as referências — é um resultado em si, e um dos mais úteis para a
AACD: **a população atendida está fora da faixa onde os cortes internacionais
funcionam, e o serviço precisa de um corte próprio.** Dá para propor um: usar os
tercis da própria distribuição (por exemplo, velocidade < 0,30 m/s como tercil
inferior) em vez de um número importado.

O 10-CS é a exceção: distribui os pacientes em três faixas com tamanhos razoáveis, e
é o instrumento cognitivo que vale manter.

---

## 5. Estado de preenchimento

Aba 60+, campos com mais lacunas:

| Campo | Sem dado | Leitura |
|---|---|---|
| Custo dupla tarefa | 100% | Coluna derivada, nunca calculada — não é dado perdido |
| Braço D / E | 92% / 94% | **Medida substituta** da panturrilha em amputação e lesão medular — não descartar |
| Diagnóstico Funcional | 83% | Só preenchido quando havia hemiparesia |
| Sentar/levantar 30 s | 72% | **Não é lacuna — ver abaixo** |
| 10-CS | 61% | Aplicado em parte da amostra |
| MoCA | 55% | Aplicado em parte da amostra |
| Panturrilha E | 45% | Boa parte é ausência estrutural (amputação) |

### Três tipos de "vazio" que não podem ser tratados igual

**a) Ausência estrutural.** `NA` em panturrilha para quem tem amputação (56% dos AMP,
100% dos AMP bilaterais) não é dado perdido: a perna não existe. Imputar média aí é
inventar. O certo é marcar como "não aplicável" e criar uma variável separada
`membro_ausente`. Mesmo caso do tempo de 10 m para cadeirantes.

**b) Protocolos alternativos.** Ponte e sentar/levantar parecem ter 72% e 32% de
lacuna. Na verdade são **testes mutuamente exclusivos**:

| | Pacientes (60+) |
|---|---|
| Só sentar/levantar | 46 |
| Só ponte | 111 |
| Ambos | 1 |
| Nenhum | 8 |

Aplicou-se ponte em quem não conseguia levantar da cadeira, e sentar/levantar em quem
conseguia. Combinando os dois numa variável "força de MMII avaliada", a cobertura vai
de 28% para **158/166 (95%)**. É o maior ganho de dado disponível na base, e custa
uma linha de código — mas exige guardar qual teste foi aplicado, porque a escolha do
teste é, ela própria, um marcador de gravidade.

**c) Lacuna verdadeira.** Polifarmácia em branco em 22 pacientes, desfecho ausente em
5. Essas são perdas reais.

---

## 6. Inconsistências encontradas

`saidas/pendencias.csv` traz as 136 linhas com ID e campo. Resumo:

| Problema | Ocorrências | Gravidade |
|---|---|---|
| Cadeirante com tempo de 10 m registrado | 39 | alta |
| Polifarmácia em branco | 33 | média |
| 10 m = NA sem indicação de cadeira | 8 | média |
| "Queda último mês" como 0/2 em vez de sim/não | 8 | média |
| Suporte social = "." | 7 | média |
| Menor de 60 anos na aba 60+ | 7 | alta |
| Desfecho ausente | 7 | alta |
| Idade anotada com "?" (57?, 59?) | 6 | alta |
| Tempo de 10 m acima de 120 s | 5 | média |
| Dinamômetro = 0 | 5 | média |
| Valores com "?" (Polio?, Cadeira?) | 4 | média |
| "AMP" no lugar de NA em panturrilha | 2 | baixa |
| 16 e 20 quedas no ano | 2 | média |
| 10 m = 1,2 s (impossível) | 1 | alta |
| Idade = "k" | 1 | alta |

Três merecem destaque:

**Cadeirantes com tempo de 10 m (39 casos).** Nove na aba 60+, treze na 60−, e o
restante em variações de status. Um deles fez 10 m em 1,2 s — 8,3 m/s, velocidade de
velocista olímpico. Enquanto não se souber se o trajeto foi andando ou empurrando a
cadeira, a coluna de 10 m mistura dois testes diferentes e a velocidade de marcha
derivada dela não é confiável para esses pacientes.

**Padronização de texto.** `Parkison` (7) e `Parkinson` (5) são a mesma doença
contada separadamente — juntando, Parkinson vira o terceiro diagnóstico mais comum.
`Status funcional` tem **80 valores distintos para 150 preenchimentos**: texto livre
puro. O mesmo em aditamento (`Bengala de 4 apoios` / `Bengala 4 apoios`,
`Andador com rodas dianteras` / `Andador de rodas dianteiras`, `Cadeira` /
`Cadeira de rodas` / `Cadeira?`). Sem padronizar, nenhum agrupamento funciona.

**Efeito de lote.** Os 8 pacientes com "queda último mês" numérico são os IDs 22–29,
consecutivos. Os 4 com suporte social "." são os IDs 4–7, também consecutivos. Isso
não é aleatório: é um avaliador, ou uma estação de coleta, usando convenção própria.
Vale perguntar à AACD quem preencheu cada faixa — e é o argumento mais forte para
padronizar o formulário na próxima edição.

---

## 7. Quanto a base aguenta de modelo

Casos completos na aba 60+ conforme se adicionam variáveis:

| Conjunto de variáveis | n completo | Quedas |
|---|---|---|
| Idade + dinamômetro | 159 (96%) | ~87 |
| + CIF equilíbrio + BlazePod (2) | 155 (93%) | ~85 |
| + tempo de 10 m | 126 (76%) | ~69 |
| + panturrilha | 75 (45%) | ~41 |
| + ponte | 40 (24%) | ~22 |
| + sentar/levantar | **0** | 0 |
| + MoCA | 0 | 0 |

O zero na linha de sentar/levantar é a consequência aritmética dos protocolos
alternativos: como quase ninguém tem ponte **e** sentar/levantar, exigir as duas
elimina a amostra inteira.

Pela regra de ~10 eventos por variável, com 85 quedas o teto honesto é de
**6 a 8 variáveis**. Um modelo com todas as 27 colunas não vai generalizar,
por mais que a acurácia de treino pareça boa.

Recomendação para a Atividade 3: um núcleo de 5 a 6 variáveis com 93% de cobertura
(idade, sexo, polifarmácia, dinamômetro, CIF equilíbrio, força de MMII combinada),
validação cruzada estratificada repetida em vez de split único — com 155 casos um
split de 30% tem 46 pacientes e o intervalo de confiança fica largo demais para
concluir qualquer coisa — e comparação obrigatória contra duas linhas de base: a
classe majoritária (54,7%) e uma regra de uma variável só.

---

## 8. Roteiro sugerido

**Atividade 1 — preparação.** Achatar os blocos de 2 linhas (feito, em
`scripts/diagnostico.py`); padronizar `Clínica/Dx`, `Status funcional`, aditamento e
suporte social em dicionários explícitos, versionados, nunca por regex solta;
separar ausência estrutural de lacuna real; derivar `custo_dupla_tarefa` (159/166
calculáveis), `velocidade_marcha` e `forca_mmii_combinada`; fechar a tabela de
pendências e levar à AACD.

**Atividade 2 — perfil e fatores.** Toda análise estratificada por mobilidade, sempre.
Descrever os dois grupos em separado. Testar os dois desfechos (caiu / caiu 2+) e
dizer qual respondeu. Comparar com os valores de referência das referências 1, 2, 5 e
6 — e reportar que os cortes saturam, que é resultado.

**Atividade 3 — modelo.** Núcleo enxuto, validação cruzada repetida, baseline
explícito. Métrica principal: **sensibilidade**, não acurácia. Num rastreio de
prevenção, deixar de sinalizar quem vai cair custa uma fratura; sinalizar a mais custa
uma consulta de fisioterapia. Reportar intervalo de confiança em tudo. Se o modelo
empatar com a regra simples, esse é o resultado — e deve ser dito.

**Atividade 4 — devolutiva.** O perfil de alerta precisa caber numa frase que um
fisioterapeuta use sem computador. Pelos dados atuais, algo como: *"idoso que anda,
usa dispositivo de marcha, toma 5 ou mais remédios e faz menos de 5 repetições no
sentar-e-levantar"*. Falta validar, mas é a direção que a base aponta.

**Recomendações de coleta.** Formulário com lista fechada nos campos categóricos;
distinguir "não aplicável" de "não realizado" com códigos diferentes; registrar qual
protocolo de força foi aplicado e por quê; registrar se o trajeto de 10 m foi andando
ou em cadeira; padronizar sim/não; e — o mais importante para a pergunta da AACD —
registrar **exposição**: quantas horas por dia o paciente fica em pé ou andando. Sem
isso, o paradoxo da seção 3 vai se repetir em toda coleta futura.

---

## 9. Sobre as referências

| Arquivo | Conteúdo | Serve para |
|---|---|---|
| `referncia_1.pdf` | World guidelines for falls prevention (Age and Ageing, 2022) | Algoritmo de risco baixo/intermediário/alto, 3 Perguntas-Chave, corte de 0,8 m/s |
| `referncia_2.pdf` | Força de preensão, valores de referência brasileiros (Rio Branco, AC) | Comparar dinamômetro com população brasileira |
| `Referncia_5.pdf` | MoCA, validação original (Nasreddine, 2005) | Corte < 26 |
| `referncia_6.pdf` | 10-CS, validação brasileira (Apolinario) | Faixas ≤5 / 6–7 / ≥8 |
| `referncia_9.pdf` | **Idêntico ao `referncia_2.pdf`** (mesmo md5) | — |

A referência 9 é uma duplicata da 2. Faltam as referências 3, 4, 7 e 8 — se existirem,
vale subir; provavelmente cobrem sentar/levantar 30 s, circunferência de panturrilha,
CIF e BlazePod, que hoje estão sem valor de referência para comparação.

As 3 Perguntas-Chave da referência 1 são, na íntegra: caiu no último ano; sente-se
inseguro ao ficar em pé ou andar; tem preocupação de cair. A base responde a primeira.
**As outras duas não foram coletadas** — e são baratas, duas perguntas. É a
recomendação de coleta com melhor relação custo-benefício do projeto.

---

## Como rodar

```bash
pip install -r requirements.txt
python3 scripts/diagnostico.py
```

Gera `saidas/base_60mais.csv`, `saidas/base_60menos.csv` e `saidas/pendencias.csv`.
A pasta `saidas/` está no `.gitignore` — contém dados por paciente e não deve ser
versionada.

---

## Notebook de análise

`analise_quedas_aacd.ipynb` percorre a base passo a passo, no Jupyter: abre a
planilha crua, mostra por que `read_excel` não funciona, achata os blocos, tipa as
colunas, padroniza os textos e chega aos indicadores. 46 células de código, 10
gráficos.

```bash
pip install -r requirements.txt
jupyter lab analise_quedas_aacd.ipynb
```

O notebook é versionado **sem saídas**: as tabelas intermediárias mostram linhas de
paciente, e o repositório precisa ficar privado antes de guardar isso. Rode
localmente para gerar os resultados.

### Indicadores produzidos

Três famílias, mais um índice composto:

| Família | Exemplos |
|---|---|
| Desfecho | taxa de queda no ano, taxa de queda recorrente, queda no último mês |
| Fatores | % polifarmácia, % com dispositivo, velocidade mediana, % preensão abaixo do corte |
| Qualidade do dado | % desfecho registrado, % força de MMII avaliada, completude média |

**Índice de Alerta de Queda (IAQ)** — 0 a 4 pontos, um por critério: anda, toma 5+
remédios, usa dispositivo de marcha, força de MMII abaixo da mediana do serviço.
Calibração observada na aba 60+:

| IAQ | Pacientes | Taxa de queda | Taxa recorrente |
|---|---|---|---|
| 0 | 9 | 33,3% | 11,1% |
| 1 | 28 | 42,9% | 17,9% |
| 2 | 51 | 45,1% | 23,5% |
| 3 | 52 | 65,4% | 40,4% |
| 4 | 21 | 76,2% | 57,1% |

A taxa sobe de forma monotônica — o índice ordena o risco. Em validação cruzada
(5 folds × 20 repetições) a AUC fica em torno de **0,6**: discriminação modesta.

**Conclusão honesta:** os dados de hoje permitem *ordenar* a fila de prevenção, não
*prever* queda individual. O IAQ serve para decidir quem a equipe chama primeiro
quando há 280 pacientes e agenda para 40.


---

## Correções após o documento da equipe de fisioterapia

O documento *Interpretação dos componentes inseridos na planilha*, enviado depois
do primeiro diagnóstico, corrigiu três conclusões:

| O que este relatório dizia antes | O que é de fato |
|---|---|
| Circunferência do braço: descartar | É a **medida substituta** da panturrilha em amputação e lesão medular. Confirmado nos dados: os 13 pacientes com braço medido são exatamente os sem panturrilha (p < 0,001). |
| Corte de sarcopenia 30/20 | Esses são do EWGSOP**1**. O EWGSOP2 (2019) usa **27/16**, e a prevalência cai de 52,8% para 31,7%. |
| Unir ponte e sentar/levantar numa variável | O documento pede **tratamento estatístico separado**. A união serve para medir cobertura, não para entrar no modelo como um número só. |

E trouxe as tabelas normativas brasileiras que faltavam, agora em
`scripts/normativos.py` com a fonte de cada valor.

---

## Notebook 02 — engenharia de variáveis

`02_engenharia_variaveis.ipynb` faz a codificação (binária, ordinal, one-hot),
aplica os normativos brasileiros e responde qual teste vale o trabalho.

### O ganho maior: normativo em vez de corte importado

| Abordagem | Resultado |
|---|---|
| MoCA < 26 (corte internacional) | 86,7% "alterados" — satura, não prioriza ninguém |
| MoCA em z-score do normativo BR por idade | **z mediano +0,13**; só 6,7% abaixo de −2 dp |

A cognição desta população **não está alterada** — o corte importado é que era
inadequado, exatamente como o documento alertava.

### O retrato revisado

O comprometimento é **localizado em membros inferiores**, não global:

| Domínio | % da referência | Leitura |
|---|---|---|
| Força de preensão | ~88% do normativo BR | preservada |
| Panturrilha | 90% acima do corte BR | preservada |
| MoCA (ajustado por idade) | na média normativa | preservada |
| **Sentar/levantar 30 s** | **3 de 44 atingem a referência** | **comprometido** |

Faz sentido clínico: a deficiência é de membros inferiores, e os braços são *mais*
usados que na população geral (muletas, andador, propulsão de cadeira). Medidas
globais de força e cognição não discriminam quem cai porque não é ali que está o
problema — e isso responde à pergunta da AACD sobre quais testes diferenciam.

### A troca que economiza tempo

**BlazePod em dupla tarefa × MoCA: ρ = 0,72** (p < 10⁻¹⁰, n = 72), com 96% de
cobertura contra 45%, e 30 segundos contra 10 minutos. A versão em dupla tarefa
correlaciona mais com cognição que a simples (0,72 vs 0,63), o que valida o desenho
do teste. Para triagem em evento de massa, é a substituição mais rentável que os
dados apontam.

### O que não funcionou

Clusterização: silhueta 0,18 e χ² p = 1,0. Não existem perfis separáveis — a
população é um contínuo de gravidade. Vale reportar como resultado negativo em vez
de forçar grupos inexistentes.

E a bateria **não é redundante**: 5 de 7 componentes do PCA para 80% da variância,
com CP1 em apenas 23%. Não há testes repetidos para cortar; o que se corta é o de
cobertura baixa.

### Recomendações de coleta, por retorno

| Recomendação | Custo | Retorno |
|---|---|---|
| **Escolaridade** | uma pergunta | destrava a interpretação do MoCA e do 10-CS no Brasil |
| **As outras 2 Perguntas-Chave** | duas perguntas | completa o 3KQ; a base só tem a primeira |
| **Exposição** (horas/dia em pé) | uma pergunta | resolve o paradoxo da seção 3 |
| **Braço nos 70 sem panturrilha** | já está no protocolo | recupera 57 pacientes sem medida de massa muscular |
