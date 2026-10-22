"""
Testes da etapa de limpeza: garantem que as decisões documentadas
foram de fato aplicadas e que nenhum dado foi perdido no caminho.

Rodar com:  pytest -v
"""

import pandas as pd
import pytest

from src import config, limpeza


@pytest.fixture(scope="module")
def bruto():
    return limpeza.carregar_dados_brutos()


@pytest.fixture(scope="module")
def limpo(bruto):
    return limpeza.aplicar_tipos(limpeza.limpar_dados(bruto))


def test_base_bruta_tem_formato_esperado(bruto):
    assert bruto.shape == (1470, 35)


def test_requisitos_do_roteiro(bruto):
    assert len(bruto) >= 500
    assert len(config.VARS_NUMERICAS) >= 5
    assert len(config.VARS_CATEGORICAS) >= 3


def test_sem_ausentes_e_sem_duplicatas(bruto):
    assert limpeza.relatorio_qualidade(bruto)["ausentes"].sum() == 0
    assert limpeza.verificar_duplicatas(bruto) == {"linhas_duplicadas": 0, "ids_duplicados": 0}


def test_colunas_constantes_identificadas_e_removidas(bruto, limpo):
    assert set(limpeza.encontrar_colunas_constantes(bruto)) == set(config.COLUNAS_CONSTANTES)
    assert not set(config.COLUNAS_CONSTANTES) & set(limpo.columns)


def test_nenhuma_linha_perdida(bruto, limpo):
    """Outliers são mantidos: a base limpa tem exatamente as mesmas linhas."""
    assert len(limpo) == len(bruto)
    assert limpo["EmployeeNumber"].tolist() == bruto["EmployeeNumber"].tolist()


def test_binarias_coerentes(limpo):
    assert limpo["Attrition_bin"].sum() == 237
    assert ((limpo["Attrition"] == "Yes") == (limpo["Attrition_bin"] == 1)).all()
    assert ((limpo["OverTime"] == "Yes") == (limpo["OverTime_bin"] == 1)).all()


def test_rotulos_ordinais_sem_valores_perdidos(limpo):
    for col in config.ESCALAS_ORDINAIS:
        assert limpo[f"{col}_rot"].isna().sum() == 0, col
        assert limpo[f"{col}_rot"].cat.ordered


def test_faixas_cobrem_todos(limpo):
    for col in ["FaixaEtaria", "FaixaSalarial", "FaixaTempoCasa", "Departamento", "Cargo", "Viagens"]:
        assert limpo[col].isna().sum() == 0, col


def test_outliers_iqr_renda(bruto):
    out = limpeza.detectar_outliers_iqr(bruto, ["MonthlyIncome"])
    q1, q3 = bruto["MonthlyIncome"].quantile([0.25, 0.75])
    limite = q3 + 1.5 * (q3 - q1)
    assert out.loc["MonthlyIncome", "n_outliers"] == (bruto["MonthlyIncome"] > limite).sum()


def test_ida_e_volta_pelo_csv(limpo, tmp_path):
    """Salvar e reler a base limpa preserva valores e tipos ordenados."""
    caminho = tmp_path / "limpo.csv"
    limpeza.salvar_dados_limpos(limpo, caminho)
    relido = limpeza.carregar_dados_limpos(caminho)
    assert relido.shape == limpo.shape
    assert relido["JobInvolvement_rot"].cat.categories.tolist() == ["Baixo", "Médio", "Alto", "Muito alto"]
    pd.testing.assert_series_equal(relido["MonthlyIncome"], limpo["MonthlyIncome"])
