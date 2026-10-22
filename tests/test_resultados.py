"""
Testes de consistência dos resultados salvos (rodar depois do run_all.py).
Garantem que os números usados no relatório batem com um recálculo direto.
"""

import json

import pandas as pd
import pytest

from src import config, limpeza

ARQ = config.PASTA_TABELAS / "numeros_chave.json"
pytestmark = pytest.mark.skipif(not ARQ.exists(), reason="execute run_all.py antes")


@pytest.fixture(scope="module")
def num():
    return json.loads(ARQ.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def df():
    return limpeza.carregar_dados_limpos()


def test_taxa_geral(num, df):
    assert num["taxa_geral"] == pytest.approx(df["Attrition_bin"].mean() * 100)
    assert num["taxa_ic"][0] < num["taxa_geral"] < num["taxa_ic"][1]


def test_hora_extra(num, df):
    taxas = df.groupby("OverTime")["Attrition_bin"].mean() * 100
    assert num["taxa_he_sim"] == pytest.approx(taxas["Yes"])
    assert num["taxa_he_nao"] == pytest.approx(taxas["No"])
    assert num["he_diff_ic"][0] < num["he_diff"] < num["he_diff_ic"][1]


def test_renda(num, df):
    medias = df.groupby("Status", observed=True)["MonthlyIncome"].mean()
    assert num["renda_diff"] == pytest.approx(medias["Saiu"] - medias["Ficou"])


def test_tabela_resumo_coerente():
    """Toda decisão da tabela-resumo segue a regra p < 0,05 (com Holm quando houver)."""
    tab = pd.read_csv(config.PASTA_TABELAS / "resultados_inferencia.csv")
    p = tab["p_valor_holm"].fillna(tab["p_valor"])
    esperado = p.lt(config.ALFA).map({True: "Rejeita H0", False: "Não rejeita H0"})
    assert (tab["decisao"] == esperado).all()


def test_figuras_do_relatorio_existem():
    for i in range(1, 14):
        assert list(config.PASTA_FIGURAS.glob(f"fig{i:02d}_*.png")), f"figura {i} ausente"
