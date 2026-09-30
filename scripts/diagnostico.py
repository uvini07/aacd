"""
Achatamento e diagnostico da base de quedas da AACD.

Le as duas abas (60+ e 60-), onde cada paciente ocupa DUAS linhas, e devolve
uma linha por paciente. Aplica apenas normalizacoes seguras (espacos, caixa,
marcacao de ausentes). Nao corrige valor nenhum por suposicao: tudo que e
duvidoso vai para a tabela de pendencias, para ser confirmado com a AACD.

Saidas em saidas/ (nao versionado):
    base_60mais.csv, base_60menos.csv, pendencias.csv

Uso: python3 scripts/diagnostico.py
"""

import csv
import os
import re
from collections import Counter, OrderedDict, defaultdict

import openpyxl

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLANILHA = os.path.join(RAIZ, "base_quedas_AACD_anonimizada.xlsx")
SAIDAS = os.path.join(RAIZ, "saidas")

# Marcadores de ausencia usados a mao durante a coleta.
AUSENTES = {"NA", "N/A", ".", "-", "?"}

COL_QUEDAS = "Nº quedas ao chão"
COL_DX = "Clínica/Dx"
COL_STATUS = "Status funcional"
COL_ADIT = "Aditamento 10m"
COL_10M = "10 metros"
COL_REACAO = "Reação (blazepod)"
COL_REACAO_DT = "Reação (blazepod) DT"


def normaliza_texto(valor):
    """Colapsa espacos e devolve None para vazio. Nao mexe no conteudo."""
    if valor is None:
        return None
    if isinstance(valor, str):
        texto = re.sub(r"\s+", " ", valor).strip()
        return texto or None
    return valor


def para_numero(valor):
    """Converte para float quando o valor e mesmo numerico; senao devolve None.

    Tolera virgula decimal e o apostrofo que o Excel deixa na frente do numero
    ('´2). Um '?' no fim marca duvida do avaliador: o numero e aproveitado, mas
    o caso tambem entra nas pendencias.
    """
    if valor is None:
        return None
    if isinstance(valor, (int, float)):
        return float(valor)
    texto = str(valor).strip().replace(",", ".").lstrip("´`'").rstrip("?")
    try:
        return float(texto)
    except ValueError:
        return None


def le_aba(nome_aba):
    """Devolve uma lista de dicionarios, um por paciente (bloco de 2 linhas)."""
    planilha = openpyxl.load_workbook(PLANILHA, data_only=True)
    aba = planilha[nome_aba]
    cabecalhos = [
        re.sub(r"\s+", " ", str(aba.cell(1, c).value)).strip()
        for c in range(1, aba.max_column + 1)
    ]

    pacientes = []
    for linha in range(2, aba.max_row + 1, 2):
        registro = OrderedDict()
        for coluna, cabecalho in enumerate(cabecalhos, start=1):
            primeira = normaliza_texto(aba.cell(linha, coluna).value)
            segunda = (
                normaliza_texto(aba.cell(linha + 1, coluna).value)
                if linha + 1 <= aba.max_row
                else None
            )
            # As duas linhas do bloco nunca divergem (verificado); a segunda so
            # carrega o valor quando a celula nao foi mesclada.
            registro[cabecalho] = primeira if primeira is not None else segunda
        registro["_linha_excel"] = linha
        pacientes.append(registro)
    return cabecalhos, pacientes


def usa_cadeira(paciente):
    """Identifica cadeirantes a partir do texto livre de status e aditamento."""
    texto = f"{paciente.get(COL_STATUS)} {paciente.get(COL_ADIT)}"
    return bool(re.search(r"cadeir|\bCR\b", texto, re.I))


def deriva(paciente):
    """Acrescenta as variaveis calculadas. Nenhuma delas sobrescreve o original."""
    quedas = para_numero(paciente[COL_QUEDAS])
    paciente["caiu"] = None if quedas is None else int(quedas >= 1)
    paciente["queda_recorrente"] = None if quedas is None else int(quedas >= 2)

    paciente["grupo_mobilidade"] = (
        "cadeirante" if usa_cadeira(paciente)
        else ("anda" if paciente.get(COL_STATUS) else None)
    )

    # Velocidade de marcha so faz sentido para quem anda: quem percorre os 10 m
    # empurrando a cadeira nao esta fazendo o mesmo teste.
    tempo = para_numero(paciente[COL_10M])
    paciente["velocidade_marcha_m_s"] = (
        round(10.0 / tempo, 3)
        if tempo and tempo > 0 and paciente["grupo_mobilidade"] == "anda"
        else None
    )

    simples = para_numero(paciente[COL_REACAO])
    dupla = para_numero(paciente[COL_REACAO_DT])
    paciente["custo_dupla_tarefa_pct"] = (
        round((simples - dupla) / simples * 100, 1)
        if simples and dupla is not None and simples > 0
        else None
    )

    # Ponte e sentar/levantar sao protocolos alternativos (quase nunca coexistem).
    # Guardar qual foi aplicado preserva a informacao que a uniao apagaria.
    ponte = para_numero(paciente["Ponte"])
    sentar = para_numero(paciente["Sentar/levantar 30s"])
    paciente["teste_forca_mmii"] = (
        "sentar_levantar" if sentar is not None
        else ("ponte" if ponte is not None else None)
    )
    paciente["tem_forca_mmii"] = int(ponte is not None or sentar is not None)
    return paciente


def coleta_pendencias(nome_aba, pacientes):
    """Monta a lista de duvidas a confirmar com a equipe da AACD."""
    pendencias = []

    def registra(paciente, campo, valor, duvida, gravidade):
        pendencias.append(
            {
                "aba": nome_aba,
                "id": paciente["ID"],
                "campo": campo,
                "valor_registrado": valor,
                "duvida": duvida,
                "gravidade": gravidade,
            }
        )

    for p in pacientes:
        idade_txt = str(p["Idade"])
        idade = para_numero(p["Idade"])

        if "?" in idade_txt:
            registra(p, "Idade", idade_txt, "Idade anotada com '?' — confirmar", "alta")
        if nome_aba == "60+" and idade is not None and idade < 60:
            registra(p, "Idade", idade_txt,
                     "Menor de 60 anos na aba 60+ — inclui ou move para 60-?", "alta")
        if nome_aba == "60-" and idade is None:
            registra(p, "Idade", idade_txt, "Idade nao numerica", "alta")

        if para_numero(p[COL_QUEDAS]) is None:
            registra(p, COL_QUEDAS, str(p[COL_QUEDAS]),
                     "Desfecho ausente — paciente sai da analise", "alta")
        if "´" in str(p[COL_QUEDAS]):
            registra(p, COL_QUEDAS, str(p[COL_QUEDAS]),
                     "Numero com apostrofo do Excel — confirmar valor", "baixa")
        quedas = para_numero(p[COL_QUEDAS])
        if quedas is not None and quedas >= 16:
            registra(p, COL_QUEDAS, str(quedas),
                     "Numero muito alto de quedas — confirmar", "media")

        if isinstance(p["Queda último mês"], (int, float)):
            registra(p, "Queda último mês", str(p["Queda último mês"]),
                     "Codificado como numero em vez de sim/nao", "media")

        if p["Polifarmácia?"] is None:
            registra(p, "Polifarmácia?", "", "Em branco — nao perguntado ou nao anotado?", "media")

        for campo in ("Suporte social (terapêutico)", "Suporte social (domiciliar)"):
            if str(p[campo]) == ".":
                registra(p, campo, ".", "'.' significa sem dado ou sem acompanhante?", "media")

        if para_numero(p["Dinamômetro"]) == 0:
            registra(p, "Dinamômetro", "0", "Forca zero: real ou nao medido?", "media")

        tempo = para_numero(p[COL_10M])
        if tempo is not None and tempo < 5:
            registra(p, COL_10M, str(tempo),
                     "Tempo impossivel para 10 m — erro de digitacao?", "alta")
        if tempo is not None and tempo > 120:
            registra(p, COL_10M, str(tempo), "Tempo muito alto — confirmar", "media")
        if usa_cadeira(p) and tempo is not None:
            registra(p, COL_10M, str(tempo),
                     "Cadeirante com tempo de 10 m: percorreu andando ou na cadeira?", "alta")
        if str(p[COL_10M]) == "NA" and not usa_cadeira(p):
            registra(p, COL_10M, "NA",
                     "Teste nao feito sem indicacao de cadeira — por que?", "media")

        if str(p["Panturrilha D"]) == "AMP":
            registra(p, "Panturrilha D", "AMP",
                     "'AMP' usado no lugar de NA — padronizar", "baixa")

        for campo in (COL_DX, COL_ADIT, "Diagnóstico Funcional", COL_STATUS):
            if p[campo] and "?" in str(p[campo]):
                registra(p, campo, str(p[campo]), "Valor anotado com '?' — confirmar", "media")

    return pendencias


def escreve_csv(caminho, linhas, colunas):
    with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=colunas, extrasaction="ignore")
        escritor.writeheader()
        escritor.writerows(linhas)


def resume(nome_aba, pacientes):
    total = len(pacientes)
    com_desfecho = [p for p in pacientes if p["caiu"] is not None]
    caiu = sum(p["caiu"] for p in com_desfecho)
    recorrente = sum(p["queda_recorrente"] for p in com_desfecho)
    grupos = Counter(p["grupo_mobilidade"] for p in pacientes)

    print(f"\n--- aba {nome_aba}: {total} pacientes ---")
    print(f"  desfecho disponivel : {len(com_desfecho)} ({len(com_desfecho)/total*100:.1f}%)")
    print(f"  caiu ao menos 1x    : {caiu} ({caiu/len(com_desfecho)*100:.1f}%)")
    print(f"  caiu 2x ou mais     : {recorrente} ({recorrente/len(com_desfecho)*100:.1f}%)")
    print(f"  mobilidade          : {dict(grupos)}")
    print(f"  forca de MMII (ponte OU sentar/levantar): "
          f"{sum(p['tem_forca_mmii'] for p in pacientes)}/{total}")

    preenchimento = []
    for campo in pacientes[0]:
        if campo.startswith("_"):
            continue
        vazios = sum(
            1 for p in pacientes
            if p[campo] is None or str(p[campo]).strip() in AUSENTES
        )
        preenchimento.append((vazios / total * 100, campo))
    piores = sorted(preenchimento, reverse=True)[:8]
    print("  campos mais vazios  :")
    for pct, campo in piores:
        if pct > 0:
            print(f"      {campo:34} {pct:5.1f}% sem dado")


def main():
    os.makedirs(SAIDAS, exist_ok=True)
    todas_pendencias = []

    for nome_aba, arquivo in (("60+", "base_60mais.csv"), ("60-", "base_60menos.csv")):
        cabecalhos, pacientes = le_aba(nome_aba)
        pacientes = [deriva(p) for p in pacientes]
        todas_pendencias.extend(coleta_pendencias(nome_aba, pacientes))

        derivadas = [
            "caiu", "queda_recorrente", "grupo_mobilidade", "velocidade_marcha_m_s",
            "custo_dupla_tarefa_pct", "teste_forca_mmii", "tem_forca_mmii",
        ]
        escreve_csv(os.path.join(SAIDAS, arquivo), pacientes, cabecalhos + derivadas)
        resume(nome_aba, pacientes)

    escreve_csv(
        os.path.join(SAIDAS, "pendencias.csv"),
        todas_pendencias,
        ["aba", "id", "campo", "valor_registrado", "duvida", "gravidade"],
    )

    por_gravidade = Counter(p["gravidade"] for p in todas_pendencias)
    print(f"\n--- pendencias para a AACD: {len(todas_pendencias)} ---")
    for gravidade in ("alta", "media", "baixa"):
        print(f"  {gravidade:6}: {por_gravidade[gravidade]}")
    por_duvida = Counter(p["duvida"] for p in todas_pendencias)
    for duvida, quantas in por_duvida.most_common():
        print(f"      {quantas:3}x  {duvida}")
    print(f"\nArquivos gerados em {SAIDAS}/")


if __name__ == "__main__":
    main()
