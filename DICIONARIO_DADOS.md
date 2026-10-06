# Dicionário de dados — Projeto de quedas AACD

Gerado por `python3 scripts/dicionario.py` a partir de `saidas/base_modelagem.csv`. Tipo, domínio e cobertura saem da própria base, então este documento não diverge dos dados.

**73 variáveis** · cobertura calculada sobre 166 pacientes (60+) e 116 (60−).

## Como ler a coluna *origem*

| Origem | Significa |
|---|---|
| planilha, tipada | veio da planilha; só foi convertida para o tipo certo |
| planilha, padronizada | veio da planilha; texto livre agrupado em dicionário versionado |
| derivada (cálculo) | calculada a partir de outras colunas |
| comparação normativa | compara o valor do paciente com referência externa brasileira |
| codificada p/ modelo | transformação numérica para entrar em modelo |
| controle de ausência | registra POR QUE outra coluna está vazia |
| auditoria do tratamento | marca decisões de tratamento, para serem reversíveis |

## Identificação

### `ID`

Número sequencial do paciente dentro da aba. Já anonimizado.

- **Origem:** planilha, tipada — de `ID`
- **Tipo:** `int64` · **Valores:** 1 a 166 (mediana 71)
- **Cobertura:** 100.0% em 60+ · 100.0% em 60−
- **Cuidado:** NÃO é único na base inteira: 60+ e 60− reiniciam em 1. Para chave única use ID + aba.

### `aba`

Faixa de idade de origem: '60+' (idosos, foco do estudo) ou '60−' (adultos 18–59, grupo de comparação).

- **Origem:** planilha, tipada — de `(aba da planilha)`
- **Tipo:** `str` · **Valores:** 60+ · 60-
- **Cobertura:** 100.0% em 60+ · 100.0% em 60−
- **Cuidado:** O foco do estudo é 60+. A aba 60− tem quase nenhum dado cognitivo.

## Demografia

### `idade`

Idade em anos completos.

- **Origem:** planilha, tipada — de `Idade`
- **Tipo:** `float64` · **Valores:** 18 a 91 (mediana 61)
- **Cobertura:** 100.0% em 60+ · 99.1% em 60−
- **Cuidado:** 7 pacientes da aba 60+ têm menos de 60 anos, 6 deles anotados com '?' (ex. '59?'). O '?' foi aproveitado como número e o caso foi para as pendências. O documento da AACD lembra que, nesta população, idade não é sinônimo de risco.

### `dx_grupo`

Diagnóstico clínico padronizado: AMP (amputação), LEA (lesão encefálica adquirida), LM (lesão medular), PC, DNM, Polio, MFC, EM, AVC, Parkinson, Tumor.

- **Origem:** planilha, padronizada — de `Clínica/Dx`
- **Tipo:** `str` · **Valores:** 11 categorias
- **Cobertura:** 100.0% em 60+ · 100.0% em 60−
- **Cuidado:** 'Parkison' e 'Parkinson' eram a mesma doença contada separada — agora somadas. O documento é explícito: diagnóstico serve para caracterizar e estratificar, NÃO para virar escore de risco.

### `sexo`

Sexo registrado: 'M' ou 'F'.

- **Origem:** planilha, tipada — de `Sexo`
- **Tipo:** `str` · **Valores:** F · M
- **Cobertura:** 100.0% em 60+ · 100.0% em 60−
- **Cuidado:** Estava vazio na 1ª linha de vários blocos e preenchido na 2ª — quem ler só as linhas ímpares perde o sexo de parte da amostra.

## Desfecho

### `n_quedas`

Número de quedas ao chão nos últimos 12 meses. É a variável de desfecho principal do estudo.

- **Origem:** planilha, tipada — de `Nº quedas ao chão`
- **Tipo:** `float64` · **Valores:** 0 a 20 (mediana 1)
- **Cobertura:** 97.0% em 60+ · 98.3% em 60−
- **Cuidado:** Ausente em 5 pacientes do 60+, que saem de qualquer análise de desfecho. Vai até 20 quedas; os casos ≥16 estão nas pendências.

### `queda_ultimo_mes`

Houve queda no último mês — medida de ocorrência recente.

- **Origem:** planilha, tipada — de `Queda último mês`
- **Tipo:** `object` · **Valores:** True / False
- **Cobertura:** 97.0% em 60+ · 98.3% em 60−
- **Cuidado:** 8 pacientes (IDs 22–29, consecutivos) foram gravados como número em vez de sim/não. Interpretados e sinalizados em queda_ultimo_mes_reinterpretado.

### `caiu`

True se o paciente caiu ao menos uma vez no ano (n_quedas ≥ 1). Desfecho binário principal.

- **Origem:** derivada (cálculo) — de `— (de n_quedas)`
- **Tipo:** `object` · **Valores:** True / False
- **Cobertura:** 97.0% em 60+ · 98.3% em 60−
- **Cuidado:** 54,7% na aba 60+. Esse é o piso de comparação: um modelo que chute sempre 'caiu' acerta 54,7%.

### `queda_recorrente`

True se caiu 2 vezes ou mais (n_quedas ≥ 2). O documento da AACD destaca que quem cai repetidamente tem perfil de risco diferente de quem teve um evento isolado.

- **Origem:** derivada (cálculo) — de `— (de n_quedas)`
- **Tipo:** `object` · **Valores:** True / False
- **Cobertura:** 97.0% em 60+ · 98.3% em 60−
- **Cuidado:** Discrimina MELHOR que 'caiu': é com este desfecho que o sentar/levantar aparece (p ≈ 0,02). 31,7% no 60+.

## Saúde e rotina

### `suporte_terapeutico`

Quem acompanha o paciente na terapia, agrupado em: independente, cônjuge, filho(a), pai/mãe, cuidador(a), outro familiar, não familiar, institucional, mora só.

- **Origem:** planilha, padronizada — de `Suporte social (terapêutico)`
- **Tipo:** `str` · **Valores:** 9 categorias
- **Cobertura:** 95.2% em 60+ · 99.1% em 60−
- **Cuidado:** Não é escala psicométrica de suporte social. Ter acompanhante não equivale a mais suporte nem a menos risco. '.' foi tratado como nulo — o significado ainda depende de confirmação da AACD.

### `suporte_domiciliar`

Quem convive no domicílio, nos mesmos grupos.

- **Origem:** planilha, padronizada — de `Suporte social (domiciliar)`
- **Tipo:** `str` · **Valores:** 10 categorias
- **Cobertura:** 92.2% em 60+ · 93.1% em 60−
- **Cuidado:** 'mora só' e 'independente' são categorias DIFERENTES: morar só é fator de risco descrito na literatura. Colapsar as duas apagaria isso.

### `polifarmacia`

Uso simultâneo e regular de 5 ou mais medicamentos.

- **Origem:** planilha, tipada — de `Polifarmácia?`
- **Tipo:** `object` · **Valores:** True / False
- **Cobertura:** 86.7% em 60+ · 90.5% em 60−
- **Cuidado:** Um dos dois únicos fatores que discriminam quem cai entre quem anda (70% vs 46%, p ≈ 0,03). Em branco em 22 pacientes do 60+. O documento alerta: a relação não é linear — o que pesa são os fall-risk-increasing drugs, não a contagem.

## Mobilidade

### `aditamento_grupo`

Dispositivo usado no teste de 10 m, agrupado em: nenhum, bastão, bengala, muleta, andador, cadeira de rodas.

- **Origem:** planilha, padronizada — de `Aditamento 10m`
- **Tipo:** `str` · **Valores:** andador · bastão · bengala · cadeira de rodas · muleta · nenhum
- **Cobertura:** 75.3% em 60+ · 90.5% em 60−
- **Cuidado:** 25 rótulos originais viraram 6 grupos. O documento avisa: o dispositivo NÃO causa queda — é marcador de limitação funcional.

### `nivel_marcha`

Maior alcance de locomoção mencionado: terapêutica (só na sessão), domiciliar (dentro de casa), comunitária (na rua), ou cadeira de rodas.

- **Origem:** planilha, padronizada — de `Status funcional`
- **Tipo:** `str` · **Valores:** cadeira de rodas · comunitária · domiciliar · marcha sem alcance especificado · outro · terapêutica
- **Cobertura:** 90.4% em 60+ · 98.3% em 60−
- **Cuidado:** Extraído de 128 textos livres distintos. 'Cadeira de rodas' não é 'marcha curta' — é outro modo de locomoção, e fica fora da escala ordinal.

### `perfil_mobilidade`

Como o paciente se locomove: 'anda', 'só cadeira de rodas', ou 'misto (anda e usa cadeira)'.

- **Origem:** planilha, padronizada — de `Status funcional`
- **Tipo:** `str` · **Valores:** anda · misto (anda e usa cadeira) · só cadeira de rodas
- **Cobertura:** 90.4% em 60+ · 97.4% em 60−
- **Cuidado:** A variável mais importante da base. Quem anda cai MAIS que quem usa cadeira (61% vs 39%, p = 0,015) — é exposição, não erro. Toda análise de queda precisa estratificar por ela.

### `supervisao`

Precisa de supervisão de outra pessoa para se locomover.

- **Origem:** planilha, padronizada — de `Status funcional`
- **Tipo:** `object` · **Valores:** True / False
- **Cobertura:** 7.2% em 60+ · 16.4% em 60−
- **Cuidado:** Cobertura de apenas 7% no 60+: só foi extraído de quem mencionou supervisão no texto livre. Ausência aqui significa 'não registrado', não 'não precisa'. Use com muita cautela.

## Cognição

### `moca`

Montreal Cognitive Assessment, 0 a 30 pontos. Rastreio cognitivo amplo: funções executivas, visuoespaciais, atenção, linguagem, memória e orientação.

- **Origem:** planilha, tipada — de `Cognição (MOCA)`
- **Tipo:** `float64` · **Valores:** 8 a 28 (mediana 20)
- **Cobertura:** 45.2% em 60+ · 0.9% em 60−
- **Cuidado:** NÃO use o corte internacional de 26 pontos: ele marca 86,7% da amostra como alterada e não prioriza ninguém. Use moca_z. Cobertura de 45% no 60+, quase zero no 60−.

### `dez_cs`

10-Point Cognitive Screener, instrumento brasileiro de 0 a 10 pontos: orientação temporal, fluência verbal e evocação de 3 palavras. Rápido e com pouca demanda motora.

- **Origem:** planilha, tipada — de `Cognição (10-CS)`
- **Tipo:** `float64` · **Valores:** 2 a 12 (mediana 8)
- **Cobertura:** 39.2% em 60+ · 0.9% em 60−
- **Cuidado:** 2 pacientes têm 11 e 12 pontos — ACIMA do máximo do instrumento. Impossível; está nas pendências.

## Força

### `sentar_levantar`

Repetições completas de sentar e levantar da cadeira em 30 s. Mede capacidade funcional de membros inferiores.

- **Origem:** planilha, tipada — de `Sentar/levantar 30s`
- **Tipo:** `float64` · **Valores:** 1 a 28 (mediana 8)
- **Cobertura:** 28.3% em 60+ · 56.0% em 60−
- **Cuidado:** É o teste que MAIS discrimina queda recorrente entre quem anda (4 vs 7 repetições, p ≈ 0,02). Só 3 de 44 pacientes alcançam a referência do Senior Fitness Test. Aplicado apenas em quem conseguia levantar — ver teste_forca_mmii.

### `ponte`

Ponte adaptada de 30 s, em segundos. Alternativa ao sentar/levantar para quem não realiza marcha funcional.

- **Origem:** planilha, tipada — de `Ponte`
- **Tipo:** `float64` · **Valores:** 4 a 34 (mediana 16.5)
- **Cobertura:** 67.5% em 60+ · 37.9% em 60−
- **Cuidado:** Adaptação da própria instituição, SEM validação publicada e sem valores normativos. O documento é explícito: exige tratamento estatístico SEPARADO do sentar/levantar — não fundir num número.

### `dinamometro`

Força de preensão palmar em kgf. Marcador indireto de força muscular global e estado funcional.

- **Origem:** planilha, tipada — de `Dinamômetro`
- **Tipo:** `float64` · **Valores:** 0 a 66 (mediana 27)
- **Cobertura:** 97.0% em 60+ · 100.0% em 60−
- **Cuidado:** Melhor cobertura da bateria (97%). Nesta população está PRESERVADA (~88% do normativo brasileiro), porque os braços são mais usados que na população geral — muletas, andador, propulsão de cadeira. Por isso não discrimina queda. Dois pacientes com 0 kgf estão nas pendências.

## Antropometria

### `panturrilha_d`

Circunferência da panturrilha direita, em cm. Marcador indireto de massa muscular.

- **Origem:** planilha, tipada — de `Panturrilha D`
- **Tipo:** `float64` · **Valores:** 22.5 a 48 (mediana 36)
- **Cobertura:** 57.8% em 60+ · 66.4% em 60−
- **Cuidado:** 42% ausente, e boa parte é ausência ESTRUTURAL: sem perna não há panturrilha. Imputar média aqui inventa uma perna. Ver panturrilha_d_motivo_ausencia.

### `panturrilha_e`

Circunferência da panturrilha esquerda, em cm.

- **Origem:** planilha, tipada — de `Panturrilha E`
- **Tipo:** `float64` · **Valores:** 23 a 53 (mediana 36)
- **Cobertura:** 55.4% em 60+ · 60.3% em 60−
- **Cuidado:** Medir os dois lados permite calcular assimetria, que em paciente neurológico é mais informativa que o valor absoluto. O marcador 'AMP' só foi escrito na coluna direita — inconsistência de registro.

### `braco_d`

Circunferência do braço direito, em cm. É a medida SUBSTITUTA da panturrilha em amputação de membro inferior e atrofia por lesão medular.

- **Origem:** planilha, tipada — de `Braço D`
- **Tipo:** `float64` · **Valores:** 13 a 39 (mediana 32)
- **Cobertura:** 7.8% em 60+ · 17.2% em 60−
- **Cuidado:** Parece ter 92% de lacuna, mas não é coluna inútil: os 13 pacientes medidos são exatamente os sem panturrilha (p < 0,001). A substituição foi incompleta — 57 pacientes ficaram sem nenhuma medida de massa muscular.

### `braco_e`

Circunferência do braço esquerdo, em cm. Mesma função substituta.

- **Origem:** planilha, tipada — de `Braço E`
- **Tipo:** `float64` · **Valores:** 23.5 a 39 (mediana 31)
- **Cobertura:** 6.0% em 60+ · 12.9% em 60−
- **Cuidado:** Mesma leitura de braco_d. Sofre influência de músculo e gordura, então não é medida direta de massa muscular.

## Marcha e equilíbrio

### `tempo_10m`

Tempo, em segundos, para percorrer 10 metros.

- **Origem:** planilha, tipada — de `10 metros`
- **Tipo:** `float64` · **Valores:** 1.2 a 201 (mediana 17)
- **Cobertura:** 78.9% em 60+ · 90.5% em 60−
- **Cuidado:** 39 registros são de pacientes cadeirantes — não se sabe se o trajeto foi andando ou na cadeira, e são testes diferentes. Um paciente fez 10 m em 1,2 s (8,3 m/s, velocidade de velocista): erro de digitação. Tudo nas pendências.

### `cif_equilibrio`

Classificação de equilíbrio pela CIF, 0 a 4, segundo o manual usado na instituição.

- **Origem:** planilha, tipada — de `CIF equilíbrio`
- **Tipo:** `float64` · **Valores:** 0.0 · 1.0 · 2.0 · 3.0 · 4.0
- **Cobertura:** 97.6% em 60+ · 97.4% em 60−
- **Cuidado:** A CIF descreve funcionalidade, não gera tempo ou número esperado — não existe valor normativo. A DIREÇÃO da escala (0 = sem alteração ou o contrário) está nas pendências para confirmar com a AACD.

### `posicao_equilibrio`

Posição em que o equilíbrio foi avaliado: 'sentado' ou 'ortostatismo' (em pé).

- **Origem:** planilha, padronizada — de `Posição equilíbrio`
- **Tipo:** `str` · **Valores:** ortostatismo · sentado
- **Cobertura:** 97.6% em 60+ · 98.3% em 60−
- **Cuidado:** 'Sentada' e 'Sentado' foram unificados (a planilha usava o feminino na aba 60−). O 'NA' escrito à mão virava uma terceira categoria falsa — agora é nulo.

## Reação

### `reacao`

Número de toques no BlazePod em 30 s, tarefa motora simples. Mede velocidade de resposta a estímulo externo.

- **Origem:** planilha, tipada — de `Reação (blazepod)`
- **Tipo:** `float64` · **Valores:** 4 a 55 (mediana 33)
- **Cobertura:** 98.2% em 60+ · 96.6% em 60−
- **Cuidado:** Medida EXPERIMENTAL: o protocolo de batida de mão não é validado para risco de queda e não tem ponto de corte. Os ERROS do teste deveriam ser analisados segundo o documento, mas não estão na planilha.

### `reacao_dt`

Toques no BlazePod em 30 s COM tarefa cognitiva simultânea (dupla tarefa).

- **Origem:** planilha, tipada — de `Reação (blazepod) DT`
- **Tipo:** `float64` · **Valores:** 4 a 51 (mediana 22)
- **Cobertura:** 95.8% em 60+ · 93.1% em 60−
- **Cuidado:** Correlaciona forte com o MoCA (ρ = 0,72, p < 10⁻¹⁰) — e mais que a versão simples (0,63), o que valida o desenho do teste. Com 96% de cobertura contra 45% do MoCA, é candidato a rastreio cognitivo rápido em triagem.

## Derivada

### `velocidade_marcha`

Velocidade de marcha em m/s. A medida objetiva mais recomendada pelas diretrizes mundiais para estratificar risco de queda.

- **Origem:** derivada (cálculo) — de `— (10 ÷ tempo_10m)`
- **Tipo:** `float64` · **Valores:** 0.071 a 2 (mediana 0.588)
- **Cobertura:** 62.7% em 60+ · 78.4% em 60−
- **Cuidado:** Calculada SÓ para quem anda: quem percorre 10 m empurrando a cadeira não faz o mesmo teste. Mediana de 0,38 m/s — metade do corte de 0,8 m/s, que por isso satura (77% abaixo) e não prioriza ninguém.

### `custo_dupla_tarefa`

Dual-Task Cost em %: (reacao − reacao_dt) ÷ reacao × 100. Quanto o desempenho motor caiu ao adicionar a tarefa cognitiva.

- **Origem:** derivada (cálculo) — de `Custo dupla tarefa (estava 100% vazia)`
- **Tipo:** `float64` · **Valores:** -16 a 81 (mediana 29.4)
- **Cobertura:** 95.8% em 60+ · 93.1% em 60−
- **Cuidado:** A coluna existia na planilha e estava INTEIRAMENTE vazia — nunca foi calculada. Agora sai em 96% dos pacientes. Mediana de 30,6%. Não existe ponto de corte universal: use como variável contínua.

### `teste_forca_mmii`

Qual protocolo de força de membros inferiores foi aplicado: 'ponte' ou 'sentar/levantar'.

- **Origem:** derivada (cálculo) — de `— (ponte / sentar_levantar)`
- **Tipo:** `str` · **Valores:** ponte · sentar/levantar
- **Cobertura:** 95.2% em 60+ · 94.0% em 60−
- **Cuidado:** Essa escolha é ela própria um MARCADOR DE GRAVIDADE: aplicou-se ponte em quem não conseguia levantar da cadeira. Guardar qual teste foi usado preserva informação que a fusão apagaria.

### `tem_forca_mmii`

Se há alguma medida de força de membros inferiores.

- **Origem:** derivada (cálculo) — de `— (ponte OU sentar_levantar)`
- **Tipo:** `bool` · **Valores:** True / False
- **Cobertura:** 100.0% em 60+ · 100.0% em 60−
- **Cuidado:** Serve para medir COBERTURA (95%), não para entrar no modelo: o documento pede tratamento separado dos dois protocolos.

### `assimetria_panturrilha`

Diferença absoluta entre as panturrilhas, em cm. Ideia do documento: em paciente neurológico, a diferença entre lados pode ser mais informativa que o valor absoluto.

- **Origem:** derivada (cálculo) — de `— (|panturrilha_d − panturrilha_e|)`
- **Tipo:** `float64` · **Valores:** 0 a 12 (mediana 1)
- **Cobertura:** 22.9% em 60+ · 43.1% em 60−
- **Cuidado:** Exige as DUAS panturrilhas, então só sai em 38 pacientes. Não detectou diferença (p = 0,35) — inconclusivo por falta de poder, não ausência de efeito.

### `tem_massa_muscular`

Se há alguma medida antropométrica de massa muscular, pela panturrilha ou pelo braço substituto.

- **Origem:** derivada (cálculo) — de `— (panturrilha OU braço)`
- **Tipo:** `object` · **Valores:** True / False
- **Cobertura:** 100.0% em 60+ · 0.0% em 60−
- **Cuidado:** Mostra a lacuna recuperável: 57 pacientes do 60+ não têm nenhuma das duas.

## Normativa

### `preensao_pct_norm`

Preensão como % do valor médio esperado para o sexo e a faixa de idade, pelo normativo brasileiro de Rio Branco (AC). 100% = exatamente a média da população brasileira.

- **Origem:** comparação normativa — de `— (de dinamometro)`
- **Tipo:** `float64` · **Valores:** 0 a 162.9 (mediana 87.55)
- **Cobertura:** 97.0% em 60+ · 99.1% em 60−
- **Cuidado:** Prefira esta à variável bruta: ela já ajusta sexo e idade. Mediana de 88,4% — força de preensão preservada nesta população.

### `moca_z`

Z-score do MoCA contra o normativo brasileiro da faixa de idade. z = 0 é a média dos brasileiros saudáveis da mesma idade.

- **Origem:** comparação normativa — de `— (de moca)`
- **Tipo:** `float64` · **Valores:** -2.53 a 1.69 (mediana 0.02)
- **Cobertura:** 45.2% em 60+ · 0.9% em 60−
- **Cuidado:** Resolve a saturação do corte de 26 pontos: z mediano de +0,13 e apenas 6,7% abaixo de −2 dp. A cognição desta população NÃO está alterada. Ressalva: as normas brasileiras pedem ajuste também por ESCOLARIDADE, que não foi coletada — então o z usa só a idade.

### `dez_cs_faixa`

Faixa de interpretação do 10-CS: 'desempenho normal' (≥8), 'possível comprometimento' (6–7), 'provável comprometimento' (0–5).

- **Origem:** comparação normativa — de `— (de dez_cs)`
- **Tipo:** `str` · **Valores:** desempenho normal · fora do domínio do instrumento · possível comprometimento · provável comprometimento
- **Cobertura:** 39.2% em 60+ · 0.9% em 60−
- **Cuidado:** Único instrumento cognitivo que distribui a amostra em faixas de tamanho utilizável. A categoria 'fora do domínio' marca os 2 pacientes com 11 e 12 pontos.

### `sentar_levantar_pct_ref`

Sentar/levantar como % da referência funcional do Senior Fitness Test para o sexo e a idade.

- **Origem:** comparação normativa — de `— (de sentar_levantar)`
- **Tipo:** `float64` · **Valores:** 11.8 a 186.7 (mediana 48.55)
- **Cobertura:** 26.5% em 60+ · 0.0% em 60−
- **Cuidado:** Mediana muito abaixo de 100%: só 3 de 44 atingem a referência. É o domínio comprometido desta população. O documento avisa que não são cortes para queda em pessoas com deficiência.

### `sarcopenia_ewgsop2`

Preensão abaixo do corte de sarcopenia do EWGSOP2 (2019): < 27 kg homens, < 16 kg mulheres.

- **Origem:** comparação normativa — de `— (de dinamometro)`
- **Tipo:** `object` · **Valores:** True / False
- **Cobertura:** 97.0% em 60+ · 100.0% em 60−
- **Cuidado:** São 27/16, NÃO 30/20 — estes últimos são do consenso anterior e inflam a prevalência de 31,7% para 52,8%. Serve para comparar com a literatura, não para classificar paciente.

### `panturrilha_abaixo_br`

Panturrilha abaixo do corte brasileiro de rastreio de sarcopenia: < 31 cm homens, < 30 cm mulheres.

- **Origem:** comparação normativa — de `— (de panturrilha_d)`
- **Tipo:** `object` · **Valores:** True / False
- **Cobertura:** 57.8% em 60+ · 66.4% em 60−
- **Cuidado:** Só 9% abaixo do corte — massa muscular preservada em quem tem perna mensurável. O documento alerta que o corte não vale para lesão medular, amputação ou atrofia neurológica.

## Codificada

### `sexo_fem`

Sexo em 0/1: 0 = masculino, 1 = feminino.

- **Origem:** codificada p/ modelo — de `— (de sexo)`
- **Tipo:** `int64` · **Valores:** True / False
- **Cobertura:** 100.0% em 60+ · 100.0% em 60−
- **Cuidado:** Convenção fixa: 1 é sempre a condição que o nome descreve.

### `equilibrio_em_pe`

Posição da avaliação em 0/1: 0 = sentado, 1 = em pé.

- **Origem:** codificada p/ modelo — de `— (de posicao_equilibrio)`
- **Tipo:** `float64` · **Valores:** True / False
- **Cobertura:** 97.6% em 60+ · 98.3% em 60−
- **Cuidado:** Descreve a CONDIÇÃO do teste, não o desempenho: só quem fica em pé foi avaliado em ortostatismo.

### `polifarmacia_bin`

Polifarmácia em 0/1, preservando o nulo.

- **Origem:** codificada p/ modelo — de `— (de polifarmacia)`
- **Tipo:** `float64` · **Valores:** True / False
- **Cobertura:** 86.7% em 60+ · 90.5% em 60−

### `supervisao_bin`

Supervisão em 0/1, preservando o nulo.

- **Origem:** codificada p/ modelo — de `— (de supervisao)`
- **Tipo:** `float64` · **Valores:** True / False
- **Cobertura:** 7.2% em 60+ · 16.4% em 60−
- **Cuidado:** Herda a cobertura de 7% da variável de origem.

### `caiu_bin`

Desfecho principal em 0/1. É o 'y' dos modelos.

- **Origem:** codificada p/ modelo — de `— (de caiu)`
- **Tipo:** `float64` · **Valores:** True / False
- **Cobertura:** 97.0% em 60+ · 98.3% em 60−

### `queda_recorrente_bin`

Desfecho de recorrência em 0/1.

- **Origem:** codificada p/ modelo — de `— (de queda_recorrente)`
- **Tipo:** `float64` · **Valores:** True / False
- **Cobertura:** 97.0% em 60+ · 98.3% em 60−
- **Cuidado:** Use este quando quiser o desfecho que discrimina melhor.

### `queda_ultimo_mes_bin`

Queda no último mês em 0/1.

- **Origem:** codificada p/ modelo — de `— (de queda_ultimo_mes)`
- **Tipo:** `float64` · **Valores:** True / False
- **Cobertura:** 97.0% em 60+ · 98.3% em 60−

### `aditamento_ord`

Dispositivo em escala ORDINAL de apoio crescente: 0 nenhum, 1 bastão, 2 bengala, 3 muleta, 4 andador, 5 cadeira de rodas.

- **Origem:** codificada p/ modelo — de `— (de aditamento_grupo)`
- **Tipo:** `float64` · **Valores:** 0.0 · 1.0 · 2.0 · 3.0 · 4.0 · 5.0
- **Cobertura:** 75.3% em 60+ · 90.5% em 60−
- **Cuidado:** A ordem tem sentido clínico (quanto apoio o dispositivo dá), por isso ordinal e não one-hot.

### `nivel_marcha_ord`

Alcance da marcha em escala ordinal: 0 terapêutica, 1 domiciliar, 2 comunitária.

- **Origem:** codificada p/ modelo — de `— (de nivel_marcha)`
- **Tipo:** `float64` · **Valores:** 0.0 · 1.0 · 2.0
- **Cobertura:** 55.4% em 60+ · 71.6% em 60−
- **Cuidado:** Cadeira de rodas fica FORA desta escala de propósito — é outro modo de locomoção, não marcha curta. Por isso a cobertura é menor que a de nivel_marcha.

### `usa_cadeira`

1 se usa cadeira de rodas, mesmo parcialmente.

- **Origem:** codificada p/ modelo — de `— (de perfil_mobilidade)`
- **Tipo:** `int64` · **Valores:** True / False
- **Cobertura:** 100.0% em 60+ · 100.0% em 60−
- **Cuidado:** Não é o complemento de 'anda': quem é misto tem 1 nas duas.

### `anda`

1 se realiza marcha, mesmo que também use cadeira.

- **Origem:** codificada p/ modelo — de `— (de perfil_mobilidade)`
- **Tipo:** `int64` · **Valores:** True / False
- **Cobertura:** 100.0% em 60+ · 100.0% em 60−
- **Cuidado:** A variável de ESTRATIFICAÇÃO do estudo. Quem anda está exposto ao risco de cair andando; quem só usa cadeira, não.

### `dx_AMP`

1 se o diagnóstico é AMP. One-hot, sem ordem entre as categorias.

- **Origem:** codificada p/ modelo — de `— (de dx_grupo)`
- **Tipo:** `int64` · **Valores:** True / False
- **Cobertura:** 100.0% em 60+ · 100.0% em 60−
- **Cuidado:** Categorias com menos de 8 casos na base caem em dx_outro — com 161 pacientes, uma coluna de 2 casos é ruído. Codificar diagnóstico como 1,2,3 faria o modelo achar que LM é 'o triplo de' AMP.

### `dx_LEA`

1 se o diagnóstico é LEA. One-hot, sem ordem entre as categorias.

- **Origem:** codificada p/ modelo — de `— (de dx_grupo)`
- **Tipo:** `int64` · **Valores:** True / False
- **Cobertura:** 100.0% em 60+ · 100.0% em 60−
- **Cuidado:** Categorias com menos de 8 casos na base caem em dx_outro — com 161 pacientes, uma coluna de 2 casos é ruído. Codificar diagnóstico como 1,2,3 faria o modelo achar que LM é 'o triplo de' AMP.

### `dx_LM`

1 se o diagnóstico é LM. One-hot, sem ordem entre as categorias.

- **Origem:** codificada p/ modelo — de `— (de dx_grupo)`
- **Tipo:** `int64` · **Valores:** True / False
- **Cobertura:** 100.0% em 60+ · 100.0% em 60−
- **Cuidado:** Categorias com menos de 8 casos na base caem em dx_outro — com 161 pacientes, uma coluna de 2 casos é ruído. Codificar diagnóstico como 1,2,3 faria o modelo achar que LM é 'o triplo de' AMP.

### `dx_PC`

1 se o diagnóstico é PC. One-hot, sem ordem entre as categorias.

- **Origem:** codificada p/ modelo — de `— (de dx_grupo)`
- **Tipo:** `int64` · **Valores:** True / False
- **Cobertura:** 100.0% em 60+ · 100.0% em 60−
- **Cuidado:** Categorias com menos de 8 casos na base caem em dx_outro — com 161 pacientes, uma coluna de 2 casos é ruído. Codificar diagnóstico como 1,2,3 faria o modelo achar que LM é 'o triplo de' AMP.

### `dx_Parkinson`

1 se o diagnóstico é Parkinson. One-hot, sem ordem entre as categorias.

- **Origem:** codificada p/ modelo — de `— (de dx_grupo)`
- **Tipo:** `int64` · **Valores:** True / False
- **Cobertura:** 100.0% em 60+ · 100.0% em 60−
- **Cuidado:** Categorias com menos de 8 casos na base caem em dx_outro — com 161 pacientes, uma coluna de 2 casos é ruído. Codificar diagnóstico como 1,2,3 faria o modelo achar que LM é 'o triplo de' AMP.

### `dx_DNM`

1 se o diagnóstico é DNM. One-hot, sem ordem entre as categorias.

- **Origem:** codificada p/ modelo — de `— (de dx_grupo)`
- **Tipo:** `int64` · **Valores:** True / False
- **Cobertura:** 100.0% em 60+ · 100.0% em 60−
- **Cuidado:** Categorias com menos de 8 casos na base caem em dx_outro — com 161 pacientes, uma coluna de 2 casos é ruído. Codificar diagnóstico como 1,2,3 faria o modelo achar que LM é 'o triplo de' AMP.

### `dx_Polio`

1 se o diagnóstico é Polio. One-hot, sem ordem entre as categorias.

- **Origem:** codificada p/ modelo — de `— (de dx_grupo)`
- **Tipo:** `int64` · **Valores:** True / False
- **Cobertura:** 100.0% em 60+ · 100.0% em 60−
- **Cuidado:** Categorias com menos de 8 casos na base caem em dx_outro — com 161 pacientes, uma coluna de 2 casos é ruído. Codificar diagnóstico como 1,2,3 faria o modelo achar que LM é 'o triplo de' AMP.

### `dx_MFC`

1 se o diagnóstico é MFC. One-hot, sem ordem entre as categorias.

- **Origem:** codificada p/ modelo — de `— (de dx_grupo)`
- **Tipo:** `int64` · **Valores:** True / False
- **Cobertura:** 100.0% em 60+ · 100.0% em 60−
- **Cuidado:** Categorias com menos de 8 casos na base caem em dx_outro — com 161 pacientes, uma coluna de 2 casos é ruído. Codificar diagnóstico como 1,2,3 faria o modelo achar que LM é 'o triplo de' AMP.

### `dx_outro`

1 se o diagnóstico é outro. One-hot, sem ordem entre as categorias.

- **Origem:** codificada p/ modelo — de `— (de dx_grupo)`
- **Tipo:** `int64` · **Valores:** True / False
- **Cobertura:** 100.0% em 60+ · 100.0% em 60−
- **Cuidado:** Categorias com menos de 8 casos na base caem em dx_outro — com 161 pacientes, uma coluna de 2 casos é ruído. Codificar diagnóstico como 1,2,3 faria o modelo achar que LM é 'o triplo de' AMP.

### `perfil`

Grupo atribuído por clusterização não supervisionada sobre os testes.

- **Origem:** derivada (cálculo) — de `— (clusterização k-means)`
- **Tipo:** `float64` · **Valores:** True / False
- **Cobertura:** 100.0% em 60+ · 0.0% em 60−
- **Cuidado:** NÃO USE. Silhueta de 0,18 e χ² p = 1,0: os grupos não se separam e não diferem em queda. A população é um contínuo de gravidade. Mantido só para documentar a tentativa.

## Controle de ausência

### `sentar_levantar_motivo_ausencia`

POR QUE sentar_levantar está vazio: 'nao_aplicavel' (não existe o que medir), 'nao_realizado' ('NA' escrito à mão no teste), 'nao_informado' (célula em branco), 'duvidoso' ou 'nao_numerico'.

- **Origem:** controle de ausência — de `— (de sentar_levantar)`
- **Tipo:** `str` · **Valores:** nao_informado · nao_realizado
- **Cobertura:** 71.7% em 60+ · 44.0% em 60−
- **Cuidado:** Distinguir isso é o que impede imputar valor onde não cabe. Aqui, quem não conseguia levantar da cadeira fez a ponte.

### `ponte_motivo_ausencia`

POR QUE ponte está vazio: 'nao_aplicavel' (não existe o que medir), 'nao_realizado' ('NA' escrito à mão no teste), 'nao_informado' (célula em branco), 'duvidoso' ou 'nao_numerico'.

- **Origem:** controle de ausência — de `— (de ponte)`
- **Tipo:** `str` · **Valores:** nao_informado · nao_realizado
- **Cobertura:** 32.5% em 60+ · 62.1% em 60−
- **Cuidado:** Distinguir isso é o que impede imputar valor onde não cabe. Aqui, quem conseguia levantar fez o sentar/levantar.

### `dinamometro_motivo_ausencia`

POR QUE dinamometro está vazio: 'nao_aplicavel' (não existe o que medir), 'nao_realizado' ('NA' escrito à mão no teste), 'nao_informado' (célula em branco), 'duvidoso' ou 'nao_numerico'.

- **Origem:** controle de ausência — de `— (de dinamometro)`
- **Tipo:** `str` · **Valores:** nao_informado · nao_realizado
- **Cobertura:** 3.0% em 60+ · 0.0% em 60−
- **Cuidado:** Distinguir isso é o que impede imputar valor onde não cabe. Aqui, cobertura quase total; poucas ausências.

### `panturrilha_d_motivo_ausencia`

POR QUE panturrilha_d está vazio: 'nao_aplicavel' (não existe o que medir), 'nao_realizado' ('NA' escrito à mão no teste), 'nao_informado' (célula em branco), 'duvidoso' ou 'nao_numerico'.

- **Origem:** controle de ausência — de `— (de panturrilha_d)`
- **Tipo:** `str` · **Valores:** nao_aplicavel · nao_informado · nao_realizado
- **Cobertura:** 42.2% em 60+ · 33.6% em 60−
- **Cuidado:** Distinguir isso é o que impede imputar valor onde não cabe. Aqui, 'nao_aplicavel' marca o membro amputado.

### `panturrilha_e_motivo_ausencia`

POR QUE panturrilha_e está vazio: 'nao_aplicavel' (não existe o que medir), 'nao_realizado' ('NA' escrito à mão no teste), 'nao_informado' (célula em branco), 'duvidoso' ou 'nao_numerico'.

- **Origem:** controle de ausência — de `— (de panturrilha_e)`
- **Tipo:** `str` · **Valores:** nao_informado · nao_realizado
- **Cobertura:** 44.6% em 60+ · 39.7% em 60−
- **Cuidado:** Distinguir isso é o que impede imputar valor onde não cabe. Aqui, o marcador 'AMP' só foi escrito na coluna direita.

### `tempo_10m_motivo_ausencia`

POR QUE tempo_10m está vazio: 'nao_aplicavel' (não existe o que medir), 'nao_realizado' ('NA' escrito à mão no teste), 'nao_informado' (célula em branco), 'duvidoso' ou 'nao_numerico'.

- **Origem:** controle de ausência — de `— (de tempo_10m)`
- **Tipo:** `str` · **Valores:** nao_informado · nao_realizado
- **Cobertura:** 21.1% em 60+ · 9.5% em 60−
- **Cuidado:** Distinguir isso é o que impede imputar valor onde não cabe. Aqui, 'nao_realizado' concentra-se em quem usa cadeira de rodas.

### `reacao_motivo_ausencia`

POR QUE reacao está vazio: 'nao_aplicavel' (não existe o que medir), 'nao_realizado' ('NA' escrito à mão no teste), 'nao_informado' (célula em branco), 'duvidoso' ou 'nao_numerico'.

- **Origem:** controle de ausência — de `— (de reacao)`
- **Tipo:** `str` · **Valores:** nao_informado · nao_realizado
- **Cobertura:** 1.8% em 60+ · 3.4% em 60−
- **Cuidado:** Distinguir isso é o que impede imputar valor onde não cabe. Aqui, cobertura quase total.

### `reacao_dt_motivo_ausencia`

POR QUE reacao_dt está vazio: 'nao_aplicavel' (não existe o que medir), 'nao_realizado' ('NA' escrito à mão no teste), 'nao_informado' (célula em branco), 'duvidoso' ou 'nao_numerico'.

- **Origem:** controle de ausência — de `— (de reacao_dt)`
- **Tipo:** `str` · **Valores:** nao_informado · nao_realizado
- **Cobertura:** 4.2% em 60+ · 6.9% em 60−
- **Cuidado:** Distinguir isso é o que impede imputar valor onde não cabe. Aqui, cobertura quase total.

## Auditoria

### `queda_ultimo_mes_reinterpretado`

True se o valor original era número e foi interpretado como sim/não.

- **Origem:** auditoria do tratamento — de `—`
- **Tipo:** `bool` · **Valores:** True / False
- **Cobertura:** 100.0% em 60+ · 100.0% em 60−
- **Cuidado:** Torna a decisão auditável e reversível. São os IDs 22–29 — consecutivos, o que indica efeito de lote de um avaliador.

### `polifarmacia_reinterpretado`

True se o valor de polifarmácia foi reinterpretado.

- **Origem:** auditoria do tratamento — de `—`
- **Tipo:** `bool` · **Valores:** True / False
- **Cobertura:** 100.0% em 60+ · 100.0% em 60−
- **Cuidado:** Sempre False: polifarmácia veio sempre como sim/não ou vazio. Coluna mantida por simetria do tratamento.
