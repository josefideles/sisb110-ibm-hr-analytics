"""
Testes das funções estatísticas: cada resultado é conferido contra um
cálculo independente (fórmula manual ou outra função do SciPy/statsmodels).

Rodar com:  pytest -v
"""

import numpy as np
import pandas as pd
import pytest
from scipy import stats

from src import descritiva, inferencia, limpeza


@pytest.fixture(scope="module")
def df():
    return limpeza.aplicar_tipos(limpeza.limpar_dados(limpeza.carregar_dados_brutos()))


# --- Intervalos de confiança ------------------------------------------------
def test_ic_wilson_formula_manual():
    """Confere o IC de Wilson com a fórmula fechada."""
    x, n, z = 237, 1470, stats.norm.ppf(0.975)
    p = x / n
    centro = (p + z**2 / (2 * n)) / (1 + z**2 / n)
    meia = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / (1 + z**2 / n)
    ic = inferencia.ic_proporcao(x, n)
    assert ic["ic_inferior"] == pytest.approx(centro - meia, abs=1e-9)
    assert ic["ic_superior"] == pytest.approx(centro + meia, abs=1e-9)
    assert ic["ic_inferior"] < p < ic["ic_superior"]


def test_ic_diferenca_contem_estimativa():
    r = inferencia.ic_diferenca_proporcoes(127, 416, 110, 1054)
    assert r["ic_inferior"] < r["diferenca"] < r["ic_superior"]
    assert r["risco_relativo"] == pytest.approx((127 / 416) / (110 / 1054))


# --- Teste t ------------------------------------------------------------------
def test_teste_t_escolhe_welch_e_bate_com_scipy(df):
    a = df.loc[df["Status"] == "Saiu", "MonthlyIncome"]
    b = df.loc[df["Status"] == "Ficou", "MonthlyIncome"]
    r = inferencia.teste_t(a, b, "Saiu", "Ficou", "MonthlyIncome", "teste")
    assert r["teste"] == "t de Welch"  # Levene rejeita variâncias iguais
    ref = stats.ttest_ind(a, b, equal_var=False)
    assert r["estatistica"] == pytest.approx(ref.statistic)
    assert r["p_valor"] == pytest.approx(ref.pvalue)
    assert r["ic_inferior"] < r["diferenca_medias"] < r["ic_superior"]


def test_teste_t_usa_student_quando_variancias_iguais():
    rng = np.random.default_rng(0)
    a, b = rng.normal(0, 1, 200), rng.normal(0.5, 1, 200)
    r = inferencia.teste_t(a, b, "A", "B", "x", "teste")
    assert r["teste"] == "t de Student"
    assert r["p_valor"] == pytest.approx(stats.ttest_ind(a, b).pvalue)


# --- ANOVA --------------------------------------------------------------------
def test_anova_bate_com_scipy(df):
    r = inferencia.anova(df, "PercentSalaryHike", "JobInvolvement", "teste")
    grupos = [g["PercentSalaryHike"] for _, g in df.groupby("JobInvolvement")]
    ref = stats.f_oneway(*grupos)
    assert r["teste"] == "ANOVA (F de Fisher)"
    assert r["estatistica"] == pytest.approx(ref.statistic)
    assert r["p_valor"] == pytest.approx(ref.pvalue)
    assert 0 <= r["efeito"] <= 1


def test_anova_gera_tukey_quando_significativa():
    rng = np.random.default_rng(1)
    d = pd.DataFrame({"g": np.repeat([1, 2, 3], 100),
                      "v": np.concatenate([rng.normal(m, 1, 100) for m in (0, 0, 2)])})
    r = inferencia.anova(d, "v", "g", "teste")
    assert r["decisao"] == "Rejeita H0"
    assert r["tukey"] is not None


# --- Qui-Quadrado -------------------------------------------------------------
def test_qui_quadrado_bate_com_scipy(df):
    r = inferencia.qui_quadrado(df, "OverTime", "Attrition", "teste")
    ref = stats.chi2_contingency(pd.crosstab(df["OverTime"], df["Attrition"]))
    assert r["estatistica"] == pytest.approx(ref.statistic)
    assert r["p_valor"] == pytest.approx(ref.pvalue)
    assert r["pressupostos"]["todas_esperadas_maior_igual_5"]


def test_cramer_v_formula(df):
    r = inferencia.qui_quadrado(df, "Department", "Attrition", "teste")
    tab = pd.crosstab(df["Department"], df["Attrition"])
    chi2 = stats.chi2_contingency(tab).statistic
    assert r["efeito"] == pytest.approx(np.sqrt(chi2 / (tab.values.sum() * (min(tab.shape) - 1))))


# --- Correlação ---------------------------------------------------------------
def test_correlacao_bate_com_scipy(df):
    r = inferencia.teste_correlacao(df["MonthlyIncome"], df["PercentSalaryHike"], "x", "y", "teste", "spearman")
    assert r["estatistica"] == pytest.approx(stats.spearmanr(df["MonthlyIncome"], df["PercentSalaryHike"]).statistic)
    assert r["pearson_r"] == pytest.approx(df["MonthlyIncome"].corr(df["PercentSalaryHike"]))


# --- Holm e utilidades --------------------------------------------------------
def test_holm_nunca_diminui_p_valor():
    res = [{"p_valor": p} for p in (0.01, 0.04, 0.03, 0.20)]
    inferencia.ajustar_holm(res)
    for r in res:
        assert r["p_valor_holm"] >= r["p_valor"]
    assert res[0]["p_valor_holm"] == pytest.approx(0.04)  # menor p × 4


def test_decisao():
    assert inferencia.decisao(0.049) == "Rejeita H0"
    assert inferencia.decisao(0.05) == "Não rejeita H0"


# --- Descritiva ---------------------------------------------------------------
def test_medidas_numericas(df):
    tab = descritiva.medidas_numericas(df, ["Age"])
    assert tab.loc["Age", "media"] == pytest.approx(df["Age"].mean())
    assert tab.loc["Age", "IQR"] == pytest.approx(df["Age"].quantile(0.75) - df["Age"].quantile(0.25))


def test_frequencias_somam_100(df):
    tab = descritiva.frequencias(df, ["Department", "JobInvolvement_rot"])
    for _, g in tab.groupby("variavel"):
        assert g["freq_absoluta"].sum() == len(df)
        assert g["freq_relativa_pct"].sum() == pytest.approx(100, abs=0.05)


def test_taxa_por_grupo_reconstroi_total(df):
    t = descritiva.taxa_saida_por_grupo(df, "Departamento")
    assert t["n"].sum() == len(df)
    assert t["saidas"].sum() == 237
