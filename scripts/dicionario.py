"""
Dicionario de dados do projeto de quedas da AACD.

Gera saidas/dicionario_dados.csv e DICIONARIO_DADOS.md a partir da base tratada,
cruzando a descricao curada de cada variavel com o tipo e a cobertura reais. Como
os numeros saem da propria base, o documento nao pode divergir dela.

Uso: python3 scripts/dicionario.py
"""

import os

import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(RAIZ, "saidas", "base_modelagem.csv")

# ─────────────────────────── de onde a coluna veio
ORIGEM_PLANILHA = "planilha, tipada"
ORIGEM_PADRONIZADA = "planilha, padronizada"
ORIGEM_AUSENCIA = "controle de ausência"
ORIGEM_DERIVADA = "derivada (cálculo)"
ORIGEM_CODIFICADA = "codificada p/ modelo"
ORIGEM_NORMATIVA = "comparação normativa"
ORIGEM_AUDITORIA = "auditoria do tratamento"

# Nome da coluna -> (grupo, origem, coluna original, o que e, cuidado ao usar)
# O campo "cuidado" e o que separa um dicionario util de uma lista de nomes.
VARIAVEIS = {
    # ───────────────────────────────────────────────── identificação
    "ID": ("Identificação", ORIGEM_PLANILHA, "ID",
           "Número sequencial do paciente dentro da aba. Já anonimizado.",
           "NÃO é único na base inteira: 60+ e 60− reiniciam em 1. "
           "Para chave única use ID + aba."),
    "aba": ("Identificação", ORIGEM_PLANILHA, "(aba da planilha)",
            "Faixa de idade de origem: '60+' (idosos, foco do estudo) ou "
            "'60−' (adultos 18–59, grupo de comparação).",
            "O foco do estudo é 60+. A aba 60− tem quase nenhum dado cognitivo."),

    # ───────────────────────────────────────────────── demografia
    "idade": ("Demografia", ORIGEM_PLANILHA, "Idade",
              "Idade em anos completos.",
              "7 pacientes da aba 60+ têm menos de 60 anos, 6 deles anotados com "
              "'?' (ex. '59?'). O '?' foi aproveitado como número e o caso foi "
              "para as pendências. O documento da AACD lembra que, nesta "
              "população, idade não é sinônimo de risco."),
    "sexo": ("Demografia", ORIGEM_PLANILHA, "Sexo",
             "Sexo registrado: 'M' ou 'F'.",
             "Estava vazio na 1ª linha de vários blocos e preenchido na 2ª — quem "
             "ler só as linhas ímpares perde o sexo de parte da amostra."),
    "dx_grupo": ("Demografia", ORIGEM_PADRONIZADA, "Clínica/Dx",
                 "Diagnóstico clínico padronizado: AMP (amputação), LEA (lesão "
                 "encefálica adquirida), LM (lesão medular), PC, DNM, Polio, "
                 "MFC, EM, AVC, Parkinson, Tumor.",
                 "'Parkison' e 'Parkinson' eram a mesma doença contada separada — "
                 "agora somadas. O documento é explícito: diagnóstico serve para "
                 "caracterizar e estratificar, NÃO para virar escore de risco."),

    # ───────────────────────────────────────────────── desfechos
    "n_quedas": ("Desfecho", ORIGEM_PLANILHA, "Nº quedas ao chão",
                 "Número de quedas ao chão nos últimos 12 meses. É a variável de "
                 "desfecho principal do estudo.",
                 "Ausente em 5 pacientes do 60+, que saem de qualquer análise de "
                 "desfecho. Vai até 20 quedas; os casos ≥16 estão nas pendências."),
    "caiu": ("Desfecho", ORIGEM_DERIVADA, "— (de n_quedas)",
             "True se o paciente caiu ao menos uma vez no ano (n_quedas ≥ 1). "
             "Desfecho binário principal.",
             "54,7% na aba 60+. Esse é o piso de comparação: um modelo que chute "
             "sempre 'caiu' acerta 54,7%."),
    "queda_recorrente": ("Desfecho", ORIGEM_DERIVADA, "— (de n_quedas)",
                         "True se caiu 2 vezes ou mais (n_quedas ≥ 2). O documento "
                         "da AACD destaca que quem cai repetidamente tem perfil de "
                         "risco diferente de quem teve um evento isolado.",
                         "Discrimina MELHOR que 'caiu': é com este desfecho que o "
                         "sentar/levantar aparece (p ≈ 0,02). 31,7% no 60+."),
    "queda_ultimo_mes": ("Desfecho", ORIGEM_PLANILHA, "Queda último mês",
                         "Houve queda no último mês — medida de ocorrência recente.",
                         "8 pacientes (IDs 22–29, consecutivos) foram gravados como "
                         "número em vez de sim/não. Interpretados e sinalizados em "
                         "queda_ultimo_mes_reinterpretado."),

    # ───────────────────────────────────────────────── saúde e rotina
    "polifarmacia": ("Saúde e rotina", ORIGEM_PLANILHA, "Polifarmácia?",
                     "Uso simultâneo e regular de 5 ou mais medicamentos.",
                     "Um dos dois únicos fatores que discriminam quem cai entre "
                     "quem anda (70% vs 46%, p ≈ 0,03). Em branco em 22 pacientes "
                     "do 60+. O documento alerta: a relação não é linear — o que "
                     "pesa são os fall-risk-increasing drugs, não a contagem."),
    "suporte_terapeutico": ("Saúde e rotina", ORIGEM_PADRONIZADA,
                            "Suporte social (terapêutico)",
                            "Quem acompanha o paciente na terapia, agrupado em: "
                            "independente, cônjuge, filho(a), pai/mãe, cuidador(a), "
                            "outro familiar, não familiar, institucional, mora só.",
                            "Não é escala psicométrica de suporte social. Ter "
                            "acompanhante não equivale a mais suporte nem a menos "
                            "risco. '.' foi tratado como nulo — o significado "
                            "ainda depende de confirmação da AACD."),
    "suporte_domiciliar": ("Saúde e rotina", ORIGEM_PADRONIZADA,
                           "Suporte social (domiciliar)",
                           "Quem convive no domicílio, nos mesmos grupos.",
                           "'mora só' e 'independente' são categorias DIFERENTES: "
                           "morar só é fator de risco descrito na literatura. "
                           "Colapsar as duas apagaria isso."),

    # ───────────────────────────────────────────────── mobilidade
    "nivel_marcha": ("Mobilidade", ORIGEM_PADRONIZADA, "Status funcional",
                     "Maior alcance de locomoção mencionado: terapêutica (só na "
                     "sessão), domiciliar (dentro de casa), comunitária (na rua), "
                     "ou cadeira de rodas.",
                     "Extraído de 128 textos livres distintos. 'Cadeira de rodas' "
                     "não é 'marcha curta' — é outro modo de locomoção, e fica "
                     "fora da escala ordinal."),
    "perfil_mobilidade": ("Mobilidade", ORIGEM_PADRONIZADA, "Status funcional",
                          "Como o paciente se locomove: 'anda', 'só cadeira de "
                          "rodas', ou 'misto (anda e usa cadeira)'.",
                          "A variável mais importante da base. Quem anda cai MAIS "
                          "que quem usa cadeira (61% vs 39%, p = 0,015) — é "
                          "exposição, não erro. Toda análise de queda precisa "
                          "estratificar por ela."),
    "aditamento_grupo": ("Mobilidade", ORIGEM_PADRONIZADA, "Aditamento 10m",
                         "Dispositivo usado no teste de 10 m, agrupado em: nenhum, "
                         "bastão, bengala, muleta, andador, cadeira de rodas.",
                         "25 rótulos originais viraram 6 grupos. O documento "
                         "avisa: o dispositivo NÃO causa queda — é marcador de "
                         "limitação funcional."),
    "supervisao": ("Mobilidade", ORIGEM_PADRONIZADA, "Status funcional",
                   "Precisa de supervisão de outra pessoa para se locomover.",
                   "Cobertura de apenas 7% no 60+: só foi extraído de quem "
                   "mencionou supervisão no texto livre. Ausência aqui significa "
                   "'não registrado', não 'não precisa'. Use com muita cautela."),

    # ───────────────────────────────────────────────── cognição
    "moca": ("Cognição", ORIGEM_PLANILHA, "Cognição (MOCA)",
             "Montreal Cognitive Assessment, 0 a 30 pontos. Rastreio cognitivo "
             "amplo: funções executivas, visuoespaciais, atenção, linguagem, "
             "memória e orientação.",
             "NÃO use o corte internacional de 26 pontos: ele marca 86,7% da "
             "amostra como alterada e não prioriza ninguém. Use moca_z. "
             "Cobertura de 45% no 60+, quase zero no 60−."),
    "dez_cs": ("Cognição", ORIGEM_PLANILHA, "Cognição (10-CS)",
               "10-Point Cognitive Screener, instrumento brasileiro de 0 a 10 "
               "pontos: orientação temporal, fluência verbal e evocação de "
               "3 palavras. Rápido e com pouca demanda motora.",
               "2 pacientes têm 11 e 12 pontos — ACIMA do máximo do instrumento. "
               "Impossível; está nas pendências."),

    # ───────────────────────────────────────────────── força
    "dinamometro": ("Força", ORIGEM_PLANILHA, "Dinamômetro",
                    "Força de preensão palmar em kgf. Marcador indireto de força "
                    "muscular global e estado funcional.",
                    "Melhor cobertura da bateria (97%). Nesta população está "
                    "PRESERVADA (~88% do normativo brasileiro), porque os braços "
                    "são mais usados que na população geral — muletas, andador, "
                    "propulsão de cadeira. Por isso não discrimina queda. "
                    "Dois pacientes com 0 kgf estão nas pendências."),
    "sentar_levantar": ("Força", ORIGEM_PLANILHA, "Sentar/levantar 30s",
                        "Repetições completas de sentar e levantar da cadeira em "
                        "30 s. Mede capacidade funcional de membros inferiores.",
                        "É o teste que MAIS discrimina queda recorrente entre quem "
                        "anda (4 vs 7 repetições, p ≈ 0,02). Só 3 de 44 pacientes "
                        "alcançam a referência do Senior Fitness Test. Aplicado "
                        "apenas em quem conseguia levantar — ver teste_forca_mmii."),
    "ponte": ("Força", ORIGEM_PLANILHA, "Ponte",
              "Ponte adaptada de 30 s, em segundos. Alternativa ao sentar/levantar "
              "para quem não realiza marcha funcional.",
              "Adaptação da própria instituição, SEM validação publicada e sem "
              "valores normativos. O documento é explícito: exige tratamento "
              "estatístico SEPARADO do sentar/levantar — não fundir num número."),

    # ───────────────────────────────────────────────── antropometria
    "panturrilha_d": ("Antropometria", ORIGEM_PLANILHA, "Panturrilha D",
                      "Circunferência da panturrilha direita, em cm. Marcador "
                      "indireto de massa muscular.",
                      "42% ausente, e boa parte é ausência ESTRUTURAL: sem perna "
                      "não há panturrilha. Imputar média aqui inventa uma perna. "
                      "Ver panturrilha_d_motivo_ausencia."),
    "panturrilha_e": ("Antropometria", ORIGEM_PLANILHA, "Panturrilha E",
                      "Circunferência da panturrilha esquerda, em cm.",
                      "Medir os dois lados permite calcular assimetria, que em "
                      "paciente neurológico é mais informativa que o valor "
                      "absoluto. O marcador 'AMP' só foi escrito na coluna "
                      "direita — inconsistência de registro."),
    "braco_d": ("Antropometria", ORIGEM_PLANILHA, "Braço D",
                "Circunferência do braço direito, em cm. É a medida SUBSTITUTA da "
                "panturrilha em amputação de membro inferior e atrofia por lesão "
                "medular.",
                "Parece ter 92% de lacuna, mas não é coluna inútil: os 13 "
                "pacientes medidos são exatamente os sem panturrilha (p < 0,001). "
                "A substituição foi incompleta — 57 pacientes ficaram sem nenhuma "
                "medida de massa muscular."),
    "braco_e": ("Antropometria", ORIGEM_PLANILHA, "Braço E",
                "Circunferência do braço esquerdo, em cm. Mesma função substituta.",
                "Mesma leitura de braco_d. Sofre influência de músculo e gordura, "
                "então não é medida direta de massa muscular."),

    # ───────────────────────────────────────────────── marcha e equilíbrio
    "tempo_10m": ("Marcha e equilíbrio", ORIGEM_PLANILHA, "10 metros",
                  "Tempo, em segundos, para percorrer 10 metros.",
                  "39 registros são de pacientes cadeirantes — não se sabe se o "
                  "trajeto foi andando ou na cadeira, e são testes diferentes. Um "
                  "paciente fez 10 m em 1,2 s (8,3 m/s, velocidade de velocista): "
                  "erro de digitação. Tudo nas pendências."),
    "cif_equilibrio": ("Marcha e equilíbrio", ORIGEM_PLANILHA, "CIF equilíbrio",
                       "Classificação de equilíbrio pela CIF, 0 a 4, segundo o "
                       "manual usado na instituição.",
                       "A CIF descreve funcionalidade, não gera tempo ou número "
                       "esperado — não existe valor normativo. A DIREÇÃO da escala "
                       "(0 = sem alteração ou o contrário) está nas pendências "
                       "para confirmar com a AACD."),
    "posicao_equilibrio": ("Marcha e equilíbrio", ORIGEM_PADRONIZADA,
                           "Posição equilíbrio",
                           "Posição em que o equilíbrio foi avaliado: 'sentado' ou "
                           "'ortostatismo' (em pé).",
                           "'Sentada' e 'Sentado' foram unificados (a planilha "
                           "usava o feminino na aba 60−). O 'NA' escrito à mão "
                           "virava uma terceira categoria falsa — agora é nulo."),

    # ───────────────────────────────────────────────── reação
    "reacao": ("Reação", ORIGEM_PLANILHA, "Reação (blazepod)",
               "Número de toques no BlazePod em 30 s, tarefa motora simples. Mede "
               "velocidade de resposta a estímulo externo.",
               "Medida EXPERIMENTAL: o protocolo de batida de mão não é validado "
               "para risco de queda e não tem ponto de corte. Os ERROS do teste "
               "deveriam ser analisados segundo o documento, mas não estão na "
               "planilha."),
    "reacao_dt": ("Reação", ORIGEM_PLANILHA, "Reação (blazepod) DT",
                  "Toques no BlazePod em 30 s COM tarefa cognitiva simultânea "
                  "(dupla tarefa).",
                  "Correlaciona forte com o MoCA (ρ = 0,72, p < 10⁻¹⁰) — e mais "
                  "que a versão simples (0,63), o que valida o desenho do teste. "
                  "Com 96% de cobertura contra 45% do MoCA, é candidato a rastreio "
                  "cognitivo rápido em triagem."),

    # ───────────────────────────────────────────────── derivadas
    "velocidade_marcha": ("Derivada", ORIGEM_DERIVADA, "— (10 ÷ tempo_10m)",
                          "Velocidade de marcha em m/s. A medida objetiva mais "
                          "recomendada pelas diretrizes mundiais para estratificar "
                          "risco de queda.",
                          "Calculada SÓ para quem anda: quem percorre 10 m "
                          "empurrando a cadeira não faz o mesmo teste. Mediana de "
                          "0,38 m/s — metade do corte de 0,8 m/s, que por isso "
                          "satura (77% abaixo) e não prioriza ninguém."),
    "custo_dupla_tarefa": ("Derivada", ORIGEM_DERIVADA,
                           "Custo dupla tarefa (estava 100% vazia)",
                           "Dual-Task Cost em %: (reacao − reacao_dt) ÷ reacao × "
                           "100. Quanto o desempenho motor caiu ao adicionar a "
                           "tarefa cognitiva.",
                           "A coluna existia na planilha e estava INTEIRAMENTE "
                           "vazia — nunca foi calculada. Agora sai em 96% dos "
                           "pacientes. Mediana de 30,6%. Não existe ponto de corte "
                           "universal: use como variável contínua."),
    "assimetria_panturrilha": ("Derivada", ORIGEM_DERIVADA,
                               "— (|panturrilha_d − panturrilha_e|)",
                               "Diferença absoluta entre as panturrilhas, em cm. "
                               "Ideia do documento: em paciente neurológico, a "
                               "diferença entre lados pode ser mais informativa "
                               "que o valor absoluto.",
                               "Exige as DUAS panturrilhas, então só sai em 38 "
                               "pacientes. Não detectou diferença (p = 0,35) — "
                               "inconclusivo por falta de poder, não ausência de "
                               "efeito."),
    "teste_forca_mmii": ("Derivada", ORIGEM_DERIVADA, "— (ponte / sentar_levantar)",
                         "Qual protocolo de força de membros inferiores foi "
                         "aplicado: 'ponte' ou 'sentar/levantar'.",
                         "Essa escolha é ela própria um MARCADOR DE GRAVIDADE: "
                         "aplicou-se ponte em quem não conseguia levantar da "
                         "cadeira. Guardar qual teste foi usado preserva "
                         "informação que a fusão apagaria."),
    "tem_forca_mmii": ("Derivada", ORIGEM_DERIVADA, "— (ponte OU sentar_levantar)",
                       "Se há alguma medida de força de membros inferiores.",
                       "Serve para medir COBERTURA (95%), não para entrar no "
                       "modelo: o documento pede tratamento separado dos dois "
                       "protocolos."),
    "tem_massa_muscular": ("Derivada", ORIGEM_DERIVADA,
                           "— (panturrilha OU braço)",
                           "Se há alguma medida antropométrica de massa muscular, "
                           "pela panturrilha ou pelo braço substituto.",
                           "Mostra a lacuna recuperável: 57 pacientes do 60+ não "
                           "têm nenhuma das duas."),

    # ───────────────────────────────────────────────── normativas
    "preensao_pct_norm": ("Normativa", ORIGEM_NORMATIVA, "— (de dinamometro)",
                          "Preensão como % do valor médio esperado para o sexo e a "
                          "faixa de idade, pelo normativo brasileiro de Rio Branco "
                          "(AC). 100% = exatamente a média da população brasileira.",
                          "Prefira esta à variável bruta: ela já ajusta sexo e "
                          "idade. Mediana de 88,4% — força de preensão preservada "
                          "nesta população."),
    "moca_z": ("Normativa", ORIGEM_NORMATIVA, "— (de moca)",
               "Z-score do MoCA contra o normativo brasileiro da faixa de idade. "
               "z = 0 é a média dos brasileiros saudáveis da mesma idade.",
               "Resolve a saturação do corte de 26 pontos: z mediano de +0,13 e "
               "apenas 6,7% abaixo de −2 dp. A cognição desta população NÃO está "
               "alterada. Ressalva: as normas brasileiras pedem ajuste também por "
               "ESCOLARIDADE, que não foi coletada — então o z usa só a idade."),
    "dez_cs_faixa": ("Normativa", ORIGEM_NORMATIVA, "— (de dez_cs)",
                     "Faixa de interpretação do 10-CS: 'desempenho normal' (≥8), "
                     "'possível comprometimento' (6–7), 'provável comprometimento' "
                     "(0–5).",
                     "Único instrumento cognitivo que distribui a amostra em "
                     "faixas de tamanho utilizável. A categoria 'fora do domínio' "
                     "marca os 2 pacientes com 11 e 12 pontos."),
    "sentar_levantar_pct_ref": ("Normativa", ORIGEM_NORMATIVA,
                                "— (de sentar_levantar)",
                                "Sentar/levantar como % da referência funcional do "
                                "Senior Fitness Test para o sexo e a idade.",
                                "Mediana muito abaixo de 100%: só 3 de 44 atingem "
                                "a referência. É o domínio comprometido desta "
                                "população. O documento avisa que não são cortes "
                                "para queda em pessoas com deficiência."),
    "sarcopenia_ewgsop2": ("Normativa", ORIGEM_NORMATIVA, "— (de dinamometro)",
                           "Preensão abaixo do corte de sarcopenia do EWGSOP2 "
                           "(2019): < 27 kg homens, < 16 kg mulheres.",
                           "São 27/16, NÃO 30/20 — estes últimos são do consenso "
                           "anterior e inflam a prevalência de 31,7% para 52,8%. "
                           "Serve para comparar com a literatura, não para "
                           "classificar paciente."),
    "panturrilha_abaixo_br": ("Normativa", ORIGEM_NORMATIVA, "— (de panturrilha_d)",
                              "Panturrilha abaixo do corte brasileiro de rastreio "
                              "de sarcopenia: < 31 cm homens, < 30 cm mulheres.",
                              "Só 9% abaixo do corte — massa muscular preservada "
                              "em quem tem perna mensurável. O documento alerta "
                              "que o corte não vale para lesão medular, amputação "
                              "ou atrofia neurológica."),

    # ───────────────────────────────────────────────── codificadas
    "sexo_fem": ("Codificada", ORIGEM_CODIFICADA, "— (de sexo)",
                 "Sexo em 0/1: 0 = masculino, 1 = feminino.",
                 "Convenção fixa: 1 é sempre a condição que o nome descreve."),
    "equilibrio_em_pe": ("Codificada", ORIGEM_CODIFICADA, "— (de posicao_equilibrio)",
                         "Posição da avaliação em 0/1: 0 = sentado, 1 = em pé.",
                         "Descreve a CONDIÇÃO do teste, não o desempenho: só quem "
                         "fica em pé foi avaliado em ortostatismo."),
    "polifarmacia_bin": ("Codificada", ORIGEM_CODIFICADA, "— (de polifarmacia)",
                         "Polifarmácia em 0/1, preservando o nulo.", ""),
    "supervisao_bin": ("Codificada", ORIGEM_CODIFICADA, "— (de supervisao)",
                       "Supervisão em 0/1, preservando o nulo.",
                       "Herda a cobertura de 7% da variável de origem."),
    "caiu_bin": ("Codificada", ORIGEM_CODIFICADA, "— (de caiu)",
                 "Desfecho principal em 0/1. É o 'y' dos modelos.", ""),
    "queda_recorrente_bin": ("Codificada", ORIGEM_CODIFICADA,
                             "— (de queda_recorrente)",
                             "Desfecho de recorrência em 0/1.",
                             "Use este quando quiser o desfecho que discrimina "
                             "melhor."),
    "queda_ultimo_mes_bin": ("Codificada", ORIGEM_CODIFICADA,
                             "— (de queda_ultimo_mes)",
                             "Queda no último mês em 0/1.", ""),
    "aditamento_ord": ("Codificada", ORIGEM_CODIFICADA, "— (de aditamento_grupo)",
                       "Dispositivo em escala ORDINAL de apoio crescente: "
                       "0 nenhum, 1 bastão, 2 bengala, 3 muleta, 4 andador, "
                       "5 cadeira de rodas.",
                       "A ordem tem sentido clínico (quanto apoio o dispositivo "
                       "dá), por isso ordinal e não one-hot."),
    "nivel_marcha_ord": ("Codificada", ORIGEM_CODIFICADA, "— (de nivel_marcha)",
                         "Alcance da marcha em escala ordinal: 0 terapêutica, "
                         "1 domiciliar, 2 comunitária.",
                         "Cadeira de rodas fica FORA desta escala de propósito — "
                         "é outro modo de locomoção, não marcha curta. Por isso a "
                         "cobertura é menor que a de nivel_marcha."),
    "usa_cadeira": ("Codificada", ORIGEM_CODIFICADA, "— (de perfil_mobilidade)",
                    "1 se usa cadeira de rodas, mesmo parcialmente.",
                    "Não é o complemento de 'anda': quem é misto tem 1 nas duas."),
    "anda": ("Codificada", ORIGEM_CODIFICADA, "— (de perfil_mobilidade)",
             "1 se realiza marcha, mesmo que também use cadeira.",
             "A variável de ESTRATIFICAÇÃO do estudo. Quem anda está exposto ao "
             "risco de cair andando; quem só usa cadeira, não."),
    "perfil": ("Codificada", ORIGEM_DERIVADA, "— (clusterização k-means)",
               "Grupo atribuído por clusterização não supervisionada sobre os "
               "testes.",
               "NÃO USE. Silhueta de 0,18 e χ² p = 1,0: os grupos não se separam e "
               "não diferem em queda. A população é um contínuo de gravidade. "
               "Mantido só para documentar a tentativa."),

    # ───────────────────────────────────────────────── auditoria
    "queda_ultimo_mes_reinterpretado": ("Auditoria", ORIGEM_AUDITORIA, "—",
                                        "True se o valor original era número e foi "
                                        "interpretado como sim/não.",
                                        "Torna a decisão auditável e reversível. "
                                        "São os IDs 22–29 — consecutivos, o que "
                                        "indica efeito de lote de um avaliador."),
    "polifarmacia_reinterpretado": ("Auditoria", ORIGEM_AUDITORIA, "—",
                                    "True se o valor de polifarmácia foi "
                                    "reinterpretado.",
                                    "Sempre False: polifarmácia veio sempre como "
                                    "sim/não ou vazio. Coluna mantida por simetria "
                                    "do tratamento."),
}

# As 8 colunas de motivo de ausencia seguem o mesmo padrao.
_MOTIVO = {
    "sentar_levantar": "quem não conseguia levantar da cadeira fez a ponte",
    "ponte": "quem conseguia levantar fez o sentar/levantar",
    "dinamometro": "cobertura quase total; poucas ausências",
    "panturrilha_d": "'nao_aplicavel' marca o membro amputado",
    "panturrilha_e": "o marcador 'AMP' só foi escrito na coluna direita",
    "tempo_10m": "'nao_realizado' concentra-se em quem usa cadeira de rodas",
    "reacao": "cobertura quase total",
    "reacao_dt": "cobertura quase total",
}
for _campo, _nota in _MOTIVO.items():
    VARIAVEIS[f"{_campo}_motivo_ausencia"] = (
        "Controle de ausência", ORIGEM_AUSENCIA, f"— (de {_campo})",
        f"POR QUE {_campo} está vazio: 'nao_aplicavel' (não existe o que medir), "
        "'nao_realizado' ('NA' escrito à mão no teste), 'nao_informado' (célula "
        "em branco), 'duvidoso' ou 'nao_numerico'.",
        f"Distinguir isso é o que impede imputar valor onde não cabe. Aqui, {_nota}.",
    )

# One-hot de diagnostico.
for _dx in ["AMP", "LEA", "LM", "PC", "Parkinson", "DNM", "Polio", "MFC", "outro"]:
    VARIAVEIS[f"dx_{_dx}"] = (
        "Codificada", ORIGEM_CODIFICADA, "— (de dx_grupo)",
        f"1 se o diagnóstico é {_dx}. One-hot, sem ordem entre as categorias.",
        "Categorias com menos de 8 casos na base caem em dx_outro — com 161 "
        "pacientes, uma coluna de 2 casos é ruído. Codificar diagnóstico como "
        "1,2,3 faria o modelo achar que LM é 'o triplo de' AMP.",
    )


def descreve_dominio(serie):
    """Resume os valores que a coluna assume, de forma legivel."""
    validos = serie.dropna()
    if validos.empty:
        return "(vazia)"
    if pd.api.types.is_bool_dtype(validos) or set(validos.unique()) <= {True, False}:
        return "True / False"
    if validos.nunique() <= 8:
        return " · ".join(sorted(str(v) for v in validos.unique()))[:120]
    if pd.api.types.is_numeric_dtype(validos):
        return (f"{validos.min():g} a {validos.max():g} "
                f"(mediana {validos.median():g})")
    return f"{validos.nunique()} categorias"


def monta_dicionario():
    base = pd.read_csv(BASE)
    mais = base[base["aba"] == "60+"]
    menos = base[base["aba"] == "60-"]

    faltando = [c for c in base.columns if c not in VARIAVEIS]
    if faltando:
        raise AssertionError(f"colunas sem descrição no dicionário: {faltando}")

    linhas = []
    for coluna in base.columns:
        grupo, origem, original, oque, cuidado = VARIAVEIS[coluna]
        linhas.append({
            "variável": coluna,
            "grupo": grupo,
            "origem": origem,
            "coluna na planilha": original,
            "tipo": str(base[coluna].dtype),
            "domínio / valores": descreve_dominio(base[coluna]),
            "cobertura 60+ (%)": round(mais[coluna].notna().mean() * 100, 1),
            "cobertura 60− (%)": round(menos[coluna].notna().mean() * 100, 1),
            "o que é": oque,
            "cuidado ao usar": cuidado,
        })
    return pd.DataFrame(linhas)


ORDEM_GRUPOS = ["Identificação", "Demografia", "Desfecho", "Saúde e rotina",
                "Mobilidade", "Cognição", "Força", "Antropometria",
                "Marcha e equilíbrio", "Reação", "Derivada", "Normativa",
                "Codificada", "Controle de ausência", "Auditoria"]


def escreve_markdown(dicionario, caminho):
    partes = [
        "# Dicionário de dados — Projeto de quedas AACD",
        "",
        "Gerado por `python3 scripts/dicionario.py` a partir de "
        "`saidas/base_modelagem.csv`. Tipo, domínio e cobertura saem da própria "
        "base, então este documento não diverge dos dados.",
        "",
        f"**{len(dicionario)} variáveis** · cobertura calculada sobre 166 "
        "pacientes (60+) e 116 (60−).",
        "",
        "## Como ler a coluna *origem*",
        "",
        "| Origem | Significa |",
        "|---|---|",
        "| planilha, tipada | veio da planilha; só foi convertida para o tipo certo |",
        "| planilha, padronizada | veio da planilha; texto livre agrupado em dicionário versionado |",
        "| derivada (cálculo) | calculada a partir de outras colunas |",
        "| comparação normativa | compara o valor do paciente com referência externa brasileira |",
        "| codificada p/ modelo | transformação numérica para entrar em modelo |",
        "| controle de ausência | registra POR QUE outra coluna está vazia |",
        "| auditoria do tratamento | marca decisões de tratamento, para serem reversíveis |",
        "",
    ]
    for grupo in ORDEM_GRUPOS:
        bloco = dicionario[dicionario["grupo"] == grupo]
        if bloco.empty:
            continue
        partes += [f"## {grupo}", ""]
        for _, r in bloco.iterrows():
            partes += [
                f"### `{r['variável']}`",
                "",
                f"{r['o que é']}",
                "",
                f"- **Origem:** {r['origem']} — de `{r['coluna na planilha']}`",
                f"- **Tipo:** `{r['tipo']}` · **Valores:** {r['domínio / valores']}",
                f"- **Cobertura:** {r['cobertura 60+ (%)']}% em 60+ · "
                f"{r['cobertura 60− (%)']}% em 60−",
            ]
            if r["cuidado ao usar"]:
                partes += [f"- **Cuidado:** {r['cuidado ao usar']}"]
            partes += [""]
    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write("\n".join(partes))


def main():
    dicionario = monta_dicionario()
    saida_csv = os.path.join(RAIZ, "saidas", "dicionario_dados.csv")
    saida_md = os.path.join(RAIZ, "DICIONARIO_DADOS.md")
    os.makedirs(os.path.dirname(saida_csv), exist_ok=True)
    dicionario.to_csv(saida_csv, index=False)
    escreve_markdown(dicionario, saida_md)

    print(f"{len(dicionario)} variáveis documentadas\n")
    print(dicionario.groupby("grupo", sort=False).size()
          .reindex(ORDEM_GRUPOS).dropna().astype(int)
          .to_frame("variáveis").to_string())
    print(f"\n-> saidas/dicionario_dados.csv")
    print(f"-> DICIONARIO_DADOS.md")


if __name__ == "__main__":
    main()
