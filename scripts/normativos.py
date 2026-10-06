"""
Valores normativos externos, com a fonte de cada um.

As tabelas vem do documento INTERPRETACAO DOS COMPONENTES INSERIDOS NA PLANILHA,
escrito pela equipe de fisioterapia da AACD, que cita a referencia de cada valor.

Regra de ouro que o documento repete em quase todo paragrafo: nesta populacao os
normativos servem como REFERENCIA EXTERNA, nunca como classificacao absoluta. A
populacao atendida tem deficiencia fisica; uma medida baixa pode refletir a
condicao neurologica, nao fragilidade relacionada ao envelhecimento.

Por isso cada funcao aqui devolve uma medida CONTINUA (z-score ou % do esperado)
em vez de um rotulo "normal/alterado". Comparar na escala continua preserva a
informacao; o corte binario a joga fora — e, como a analise mostrou, satura.
"""

import numpy as np

# ─────────────────────────────────────────────────────────── preensao palmar
# Media do desempenho maximo, em kgf, por sexo e faixa de idade.
# Fonte: Amaral et al., Rio Branco (AC), 1.609 adultos e idosos — referencia 9.
PREENSAO_NORMATIVA = {
    "M": [(18, 29, 44.7), (30, 39, 46.9), (40, 49, 42.7), (50, 59, 41.2),
          (60, 69, 36.2), (70, 79, 31.3), (80, 200, 25.7)],
    "F": [(18, 29, 28.6), (30, 39, 29.4), (40, 49, 28.3), (50, 59, 24.2),
          (60, 69, 23.0), (70, 79, 20.3), (80, 200, 17.1)],
}

# Pontos de corte de sarcopenia do EWGSOP2 (2019).
# ATENCAO: 27/16, nao 30/20 — estes ultimos sao do consenso anterior (EWGSOP1)
# e inflam a prevalencia em cerca de 20 pontos percentuais nesta amostra.
CORTE_SARCOPENIA_EWGSOP2 = {"M": 27.0, "F": 16.0}

# ─────────────────────────────────────────────────────────── MoCA
# Media e desvio padrao de brasileiros cognitivamente saudaveis, por idade.
# Fonte: dados normativos brasileiros citados na referencia 5.
# O documento e explicito: "Nao e adequado interpretar o MoCA brasileiro apenas
# pelo ponto de corte internacional de 26 pontos" — a escolaridade pesa muito.
MOCA_NORMATIVO = [(50, 59, 21.7, 4.0), (60, 69, 20.4, 4.5),
                  (70, 79, 19.4, 4.6), (80, 200, 17.7, 4.5)]

# ─────────────────────────────────────────────────────────── 10-CS
# Faixas de interpretacao, ja com o ajuste educacional previsto no instrumento.
# Fonte: Apolinario et al. — referencia 6. Maximo do instrumento: 10 pontos.
DEZ_CS_MAXIMO = 10
DEZ_CS_FAIXAS = [(0, 5, "provável comprometimento"),
                 (6, 7, "possível comprometimento"),
                 (8, 10, "desempenho normal")]

# ─────────────────────────────────────────── sentar e levantar em 30 segundos
# Limite inferior da faixa de referencia funcional, em repeticoes.
# Fonte: Senior Fitness Test, citado na referencia 7. Vale para idosos
# comunitarios relativamente ativos — o documento avisa que NAO sao pontos de
# corte para queda em pessoas com deficiencia.
SENTAR_LEVANTAR_REFERENCIA = {
    "M": [(60, 64, 17), (65, 69, 16), (70, 74, 15), (75, 79, 14), (80, 200, 13)],
    "F": [(60, 64, 15), (65, 69, 15), (70, 74, 14), (75, 79, 13), (80, 200, 12)],
}

# ─────────────────────────────────────────────────────── antropometria
# Rastreio de sarcopenia em idosos brasileiros da comunidade.
# Panturrilha: Oliveira & Fernandes, AUC ~0,83 — referencia 10.
# Braco: estudo de Maceio, AUC ~0,85 — referencia 11.
CORTE_PANTURRILHA_BR = {"M": 31.0, "F": 30.0}
CORTE_BRACO_BR = {"M": 28.0, "F": 27.0}

# ─────────────────────────────────────────────────────── velocidade de marcha
# 0,8 m/s e o corte das World Falls Guidelines 2022 (referencia 1).
# A meta-analise de 2026 (referencia 12) encontrou risco relativo de apenas
# ~1,27 para <0,8 m/s e sugere que <1,0 m/s identifica mais gente em risco.
# Nenhum dos dois deve ser lido como "abaixo = vai cair".
VELOCIDADE_CORTE_OMS = 0.8
VELOCIDADE_CORTE_AMPLIADO = 1.0
VELOCIDADE_RR_ABAIXO_08 = 1.27


def _busca_faixa(tabela, idade):
    """Devolve a tupla cuja faixa de idade contem `idade`, ou None."""
    if idade is None or (isinstance(idade, float) and np.isnan(idade)):
        return None
    for linha in tabela:
        if linha[0] <= idade <= linha[1]:
            return linha
    return None


def preensao_esperada(sexo, idade):
    """Preensao media esperada (kgf) para o sexo e a idade, pelo normativo BR."""
    if sexo not in PREENSAO_NORMATIVA:
        return np.nan
    linha = _busca_faixa(PREENSAO_NORMATIVA[sexo], idade)
    return linha[2] if linha else np.nan


def preensao_percentual(valor, sexo, idade):
    """Preensao observada como % do esperado para sexo e idade.

    100% significa exatamente a media da populacao brasileira daquela faixa.
    Escala continua: preserva a gradacao que um corte binario apagaria.
    """
    esperado = preensao_esperada(sexo, idade)
    if valor is None or np.isnan(valor) or np.isnan(esperado) or esperado == 0:
        return np.nan
    return round(valor / esperado * 100, 1)


def moca_z(valor, idade):
    """Z-score do MoCA contra o normativo brasileiro da faixa de idade.

    z = 0 significa desempenho igual a media dos brasileiros saudaveis daquela
    idade; z = -1 significa um desvio padrao abaixo dela.
    """
    if valor is None or np.isnan(valor):
        return np.nan
    linha = _busca_faixa(MOCA_NORMATIVO, idade)
    if not linha:
        return np.nan
    _, _, media, desvio = linha
    return round((valor - media) / desvio, 2)


def dez_cs_faixa(valor):
    """Faixa de interpretacao do 10-CS, ou None fora do dominio do instrumento."""
    if valor is None or np.isnan(valor):
        return None
    if not (0 <= valor <= DEZ_CS_MAXIMO):
        return "fora do domínio do instrumento"
    for piso, teto, rotulo in DEZ_CS_FAIXAS:
        if piso <= valor <= teto:
            return rotulo
    return None


def sentar_levantar_referencia(sexo, idade):
    """Repeticoes minimas da faixa de referencia funcional (Senior Fitness Test)."""
    if sexo not in SENTAR_LEVANTAR_REFERENCIA:
        return np.nan
    linha = _busca_faixa(SENTAR_LEVANTAR_REFERENCIA[sexo], idade)
    return linha[2] if linha else np.nan


def sentar_levantar_percentual(valor, sexo, idade):
    """Sentar/levantar observado como % da referencia funcional para sexo e idade."""
    referencia = sentar_levantar_referencia(sexo, idade)
    if valor is None or np.isnan(valor) or np.isnan(referencia) or referencia == 0:
        return np.nan
    return round(valor / referencia * 100, 1)


def abaixo_do_corte(valor, sexo, cortes):
    """True/False/nan para 'valor abaixo do corte do sexo'. Usa com parcimonia.

    Serve para comparar com a literatura, nao para classificar paciente: nesta
    populacao os cortes saturam (ver secao de normativos do relatorio).
    """
    if valor is None or np.isnan(valor) or sexo not in cortes:
        return np.nan
    return bool(valor < cortes[sexo])
