"""
descritiva.py — Estatística descritiva univariada e bivariada.

Etapa II do roteiro:
  - Numéricas: média, mediana, desvio padrão, IQR, assimetria, mínimo, máximo
  - Categóricas: frequência absoluta e relativa (%)
  - Correlação (Pearson e Spearman)
"""

import pandas as pd

from src import config
from src.inferencia import ic_proporcao


def medidas_numericas(df: pd.DataFrame, colunas: list) -> pd.DataFrame:
    """
    Tabela com as medidas pedidas no roteiro para cada variável numérica.
    Assimetria > 0: cauda longa à direita (poucos valores muito altos).
    """
    linhas = []
    for col in colunas:
        s = df[col]
        q1, q3 = s.quantile([0.25, 0.75])
        linhas.append({
            "variavel": col,
            "n": int(s.count()),
            "media": s.mean(),
            "mediana": s.median(),
            "desvio_padrao": s.std(),          # desvio padrão amostral (ddof=1)
            "Q1": q1,
            "Q3": q3,
            "IQR": q3 - q1,
            "assimetria": s.skew(),
            "minimo": s.min(),
            "maximo": s.max(),
        })
    return pd.DataFrame(linhas).set_index("variavel")


def frequencias(df: pd.DataFrame, colunas: list) -> pd.DataFrame:
    """Frequência absoluta e relativa (%) de cada categoria, em formato longo."""
    partes = []
    for col in colunas:
        absoluta = df[col].value_counts(sort=False)
        # mantém a ordem natural para escalas ordinais; senão, ordena por frequência
        if not isinstance(df[col].dtype, pd.CategoricalDtype) or not df[col].cat.ordered:
            if df[col].dtype.kind not in "iu":
                absoluta = absoluta.sort_values(ascending=False)
            else:
                absoluta = absoluta.sort_index()
        partes.append(pd.DataFrame({
            "variavel": col,
            "categoria": absoluta.index.astype(str),
            "freq_absoluta": absoluta.values,
            "freq_relativa_pct": (absoluta.values / absoluta.sum() * 100).round(2),
        }))
    return pd.concat(partes, ignore_index=True)


def taxa_saida_por_grupo(df: pd.DataFrame, grupo: str) -> pd.DataFrame:
    """
    Para cada categoria de `grupo`: nº de funcionários, nº de saídas,
    taxa de saída (%) e o IC 95% de Wilson dessa taxa.
    """
    linhas = []
    for nivel, sub in df.groupby(grupo, observed=True):
        n, saidas = len(sub), int(sub["Attrition_bin"].sum())
        ic = ic_proporcao(saidas, n)
        linhas.append({
            grupo: nivel, "n": n, "saidas": saidas,
            "taxa_pct": saidas / n * 100,
            "ic_inf_pct": ic["ic_inferior"] * 100,
            "ic_sup_pct": ic["ic_superior"] * 100,
        })
    return pd.DataFrame(linhas)


def comparar_grupos(df: pd.DataFrame, colunas: list, grupo: str = "Status") -> pd.DataFrame:
    """Média e mediana de cada variável numérica por grupo (ex.: Ficou × Saiu)."""
    tab = df.groupby(grupo, observed=True)[colunas].agg(["mean", "median"]).T
    tab.index.names = ["variavel", "medida"]
    return tab


def matriz_correlacao(df: pd.DataFrame, colunas: list, metodo: str = "spearman") -> pd.DataFrame:
    """Matriz de correlação (Pearson ou Spearman) entre as colunas informadas."""
    return df[colunas].corr(method=metodo)


def correlacoes_com_alvo(df: pd.DataFrame, colunas: list, alvo: str = "Attrition_bin") -> pd.DataFrame:
    """Correlação de cada variável com a saída (Pearson = ponto-bisserial e Spearman)."""
    return pd.DataFrame({
        "pearson": df[colunas].corrwith(df[alvo], method="pearson"),
        "spearman": df[colunas].corrwith(df[alvo], method="spearman"),
    }).sort_values("spearman")


def salvar_tabela(tabela: pd.DataFrame, nome: str, index: bool = True) -> None:
    """Salva a tabela em reports/tables/<nome>.csv (separador vírgula, UTF-8)."""
    config.PASTA_TABELAS.mkdir(parents=True, exist_ok=True)
    tabela.to_csv(config.PASTA_TABELAS / f"{nome}.csv", index=index, encoding="utf-8")
