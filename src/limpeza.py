"""
limpeza.py — Carregamento, diagnóstico de qualidade e limpeza dos dados.

Etapa II do roteiro (Limpeza e Qualidade):
  - valores ausentes
  - duplicatas
  - outliers (regra do IQR)
  - tipagem adequada das variáveis
"""

import pandas as pd

from src import config


# ---------------------------------------------------------------------------
# Carregamento
# ---------------------------------------------------------------------------
def carregar_dados_brutos(caminho=config.DADOS_BRUTOS) -> pd.DataFrame:
    """Lê o CSV original do Kaggle, sem nenhuma alteração."""
    return pd.read_csv(caminho)


# ---------------------------------------------------------------------------
# Diagnóstico de qualidade
# ---------------------------------------------------------------------------
def relatorio_qualidade(df: pd.DataFrame) -> pd.DataFrame:
    """
    Uma linha por coluna com: tipo lido pelo pandas, nº de ausentes,
    % de ausentes e nº de valores distintos.
    Serve para documentar a qualidade da base antes de qualquer mudança.
    """
    return pd.DataFrame({
        "tipo_pandas": df.dtypes.astype(str),
        "ausentes": df.isna().sum(),
        "pct_ausentes": (df.isna().mean() * 100).round(2),
        "valores_distintos": df.nunique(),
    })


def verificar_duplicatas(df: pd.DataFrame, coluna_id: str = "EmployeeNumber") -> dict:
    """Conta linhas inteiramente duplicadas e IDs repetidos."""
    return {
        "linhas_duplicadas": int(df.duplicated().sum()),
        "ids_duplicados": int(df[coluna_id].duplicated().sum()),
    }


def encontrar_colunas_constantes(df: pd.DataFrame) -> list:
    """Colunas com um único valor: não carregam informação para a análise."""
    return [c for c in df.columns if df[c].nunique() == 1]


def detectar_outliers_iqr(df: pd.DataFrame, colunas: list, k: float = 1.5) -> pd.DataFrame:
    """
    Regra do IQR (Tukey): é outlier o valor abaixo de Q1 - k·IQR
    ou acima de Q3 + k·IQR, com k = 1,5.
    Retorna, por variável, os limites e quantos valores ficam fora deles.
    """
    linhas = []
    for col in colunas:
        q1, q3 = df[col].quantile([0.25, 0.75])
        iqr = q3 - q1
        lim_inf, lim_sup = q1 - k * iqr, q3 + k * iqr
        fora = (df[col] < lim_inf) | (df[col] > lim_sup)
        linhas.append({
            "variavel": col,
            "Q1": q1, "Q3": q3, "IQR": iqr,
            "limite_inferior": lim_inf, "limite_superior": lim_sup,
            "n_outliers": int(fora.sum()),
            "pct_outliers": round(fora.mean() * 100, 2),
            "maximo_observado": df[col].max(),
        })
    return pd.DataFrame(linhas).set_index("variavel")


# ---------------------------------------------------------------------------
# Limpeza e enriquecimento
# ---------------------------------------------------------------------------
def limpar_dados(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica as decisões de limpeza documentadas no PLANEJAMENTO:

    1. Remove as colunas constantes (EmployeeCount, StandardHours, Over18).
    2. NÃO remove outliers: são valores legítimos (ex.: salários de diretores).
    3. Cria versões binárias (0/1) de Attrition e OverTime.
    4. Cria rótulos em português para as escalas ordinais.
    5. Cria faixas (idade, salário, tempo de casa) para leitura de negócio.

    Não há valores ausentes nem duplicatas (verificado antes), então nada
    precisa ser imputado ou excluído.
    """
    df = df.copy()

    # 1. Colunas sem variação
    df = df.drop(columns=config.COLUNAS_CONSTANTES)

    # 3. Binárias: facilitam calcular taxas (média de 0/1 = proporção)
    df["Attrition_bin"] = (df["Attrition"] == "Yes").astype(int)
    df["OverTime_bin"] = (df["OverTime"] == "Yes").astype(int)
    df["Status"] = df["Attrition"].map({"Yes": "Saiu", "No": "Ficou"})

    # 4. Rótulos das escalas ordinais (ex.: JobInvolvement 1 → "Baixo")
    for col, rotulos in config.ESCALAS_ORDINAIS.items():
        df[f"{col}_rot"] = df[col].map(rotulos)

    df["Departamento"] = df["Department"].map(config.TRADUCAO_DEPARTAMENTO)
    df["Cargo"] = df["JobRole"].map(config.TRADUCAO_CARGO)
    df["Viagens"] = df["BusinessTravel"].map(config.TRADUCAO_VIAGEM)
    df["HoraExtra"] = df["OverTime"].map({"Yes": "Sim", "No": "Não"})

    # 5. Faixas para leitura de negócio
    df["FaixaEtaria"] = pd.cut(df["Age"], bins=[17, 25, 35, 45, 60],
                               labels=["18–25", "26–35", "36–45", "46–60"])
    df["FaixaSalarial"] = pd.qcut(df["MonthlyIncome"], q=4,
                                  labels=["Q1 (mais baixa)", "Q2", "Q3", "Q4 (mais alta)"])
    df["FaixaTempoCasa"] = pd.cut(df["YearsAtCompany"], bins=[-1, 2, 5, 10, 40],
                                  labels=["0–2 anos", "3–5 anos", "6–10 anos", "11+ anos"])
    return df


def aplicar_tipos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converte as colunas de texto para 'category' e as faixas/rótulos para
    categorias ORDENADAS. Necessário porque o CSV não guarda essa informação.
    """
    df = df.copy()
    for col in config.TIPOS_VARIAVEIS["Qualitativa nominal"]:
        df[col] = df[col].astype("category")

    for col, rotulos in config.ESCALAS_ORDINAIS.items():
        ordem = [r for k, r in sorted(rotulos.items()) if r in set(df[f"{col}_rot"])]
        df[f"{col}_rot"] = pd.Categorical(df[f"{col}_rot"], categories=ordem, ordered=True)

    ordens = {
        "Status": ["Ficou", "Saiu"],
        "HoraExtra": ["Não", "Sim"],
        "Departamento": ["P&D", "Vendas", "RH"],
        "Viagens": ["Não viaja", "Viaja raramente", "Viaja frequentemente"],
        "BusinessTravel": ["Non-Travel", "Travel_Rarely", "Travel_Frequently"],
        "FaixaEtaria": ["18–25", "26–35", "36–45", "46–60"],
        "FaixaSalarial": ["Q1 (mais baixa)", "Q2", "Q3", "Q4 (mais alta)"],
        "FaixaTempoCasa": ["0–2 anos", "3–5 anos", "6–10 anos", "11+ anos"],
    }
    for col, ordem in ordens.items():
        df[col] = pd.Categorical(df[col], categories=ordem, ordered=True)
    return df


def salvar_dados_limpos(df: pd.DataFrame, caminho=config.DADOS_LIMPOS) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(caminho, index=False)


def carregar_dados_limpos(caminho=config.DADOS_LIMPOS) -> pd.DataFrame:
    """Lê a base limpa e reaplica os tipos (usado nos notebooks 02 e 03)."""
    return aplicar_tipos(pd.read_csv(caminho))
