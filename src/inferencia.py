"""
inferencia.py — Intervalos de confiança e testes de hipóteses.

Só usa os procedimentos citados no roteiro da atividade:
  - Intervalo de Confiança (proporção, diferença de proporções, diferença de médias)
  - Teste t de Student (duas médias)
  - ANOVA (três ou mais médias)
  - Teste Qui-Quadrado (associação entre categóricas)
  - Teste de Correlação (Pearson / Spearman)

Cada teste devolve um dicionário com o mesmo formato (pergunta, H0, H1,
pressupostos, estatística, p-valor, decisão, tamanho de efeito), para que
todos possam ser reunidos numa única tabela-resumo no final.
"""

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.oneway import anova_oneway
from statsmodels.stats.proportion import confint_proportions_2indep, proportion_confint
from statsmodels.stats.multicomp import pairwise_tukeyhsd

from src.config import ALFA, CONFIANCA


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def decisao(p_valor: float, alfa: float = ALFA) -> str:
    """Regra de decisão: p < alfa → rejeita H0. Nunca dizemos 'aceita H0'."""
    return "Rejeita H0" if p_valor < alfa else "Não rejeita H0"


def formatar_p(p: float) -> str:
    """p-valores muito pequenos são mostrados como '< 0,001'."""
    return "< 0,001" if p < 0.001 else f"{p:.4f}".replace(".", ",")


def classificar_cramer(v: float, gl_min: int) -> str:
    """
    Interpretação do V de Cramér (Cohen, 1988), que depende de
    gl_min = min(linhas, colunas) - 1.
    """
    limites = {1: (0.10, 0.30, 0.50), 2: (0.07, 0.21, 0.35), 3: (0.06, 0.17, 0.29)}
    p, m, g = limites.get(gl_min, limites[3])
    if v < p:
        return "desprezível"
    if v < m:
        return "pequeno"
    if v < g:
        return "médio"
    return "grande"


def classificar_d(d: float) -> str:
    """Interpretação do d de Cohen (|d|): 0,2 pequeno · 0,5 médio · 0,8 grande."""
    d = abs(d)
    if d < 0.2:
        return "desprezível"
    if d < 0.5:
        return "pequeno"
    if d < 0.8:
        return "médio"
    return "grande"


def classificar_eta2(eta2: float) -> str:
    """Interpretação do eta²: 0,01 pequeno · 0,06 médio · 0,14 grande."""
    if eta2 < 0.01:
        return "desprezível"
    if eta2 < 0.06:
        return "pequeno"
    if eta2 < 0.14:
        return "médio"
    return "grande"


def classificar_r(r: float) -> str:
    """Interpretação do coeficiente de correlação |r|."""
    r = abs(r)
    if r < 0.1:
        return "desprezível"
    if r < 0.3:
        return "fraca"
    if r < 0.5:
        return "moderada"
    return "forte"


# ---------------------------------------------------------------------------
# Intervalos de confiança
# ---------------------------------------------------------------------------
def ic_proporcao(sucessos: int, n: int, confianca: float = CONFIANCA) -> dict:
    """
    IC para uma proporção pelo método de Wilson.
    Wilson é preferível ao IC "clássico" (Wald) porque mantém a cobertura
    correta mesmo com proporções longe de 50% ou grupos pequenos (ex.: RH, n = 63).
    """
    inf, sup = proportion_confint(sucessos, n, alpha=1 - confianca, method="wilson")
    return {"proporcao": sucessos / n, "ic_inferior": inf, "ic_superior": sup,
            "n": n, "sucessos": sucessos, "metodo": "Wilson"}


def ic_diferenca_proporcoes(x1: int, n1: int, x2: int, n2: int,
                            confianca: float = CONFIANCA) -> dict:
    """
    IC para p1 - p2 (método de Newcombe, baseado em Wilson) e risco relativo p1/p2.
    Se o IC não contém zero, a diferença é significativa ao nível 1 - confiança.
    """
    inf, sup = confint_proportions_2indep(x1, n1, x2, n2, method="newcomb",
                                          compare="diff", alpha=1 - confianca)
    p1, p2 = x1 / n1, x2 / n2
    return {"p1": p1, "p2": p2, "diferenca": p1 - p2,
            "ic_inferior": inf, "ic_superior": sup,
            "risco_relativo": p1 / p2, "metodo": "Newcombe"}


# ---------------------------------------------------------------------------
# Pressupostos
# ---------------------------------------------------------------------------
def checar_normalidade(*grupos, alfa: float = ALFA) -> list:
    """
    Shapiro-Wilk em cada grupo. H0: os dados vêm de uma distribuição normal.
    Observação: com n grande, o teste rejeita até desvios pequenos;
    por isso a decisão final também considera o Q-Q plot e o TCL.
    """
    saida = []
    for g in grupos:
        g = np.asarray(g, dtype=float)
        w, p = stats.shapiro(g)
        saida.append({"n": len(g), "W": w, "p_valor": p,
                      "normal": p >= alfa, "assimetria": stats.skew(g)})
    return saida


def checar_homogeneidade(*grupos, alfa: float = ALFA) -> dict:
    """Levene (centrado na mediana, robusto). H0: as variâncias são iguais."""
    est, p = stats.levene(*grupos, center="median")
    return {"estatistica": est, "p_valor": p, "variancias_iguais": p >= alfa}


# ---------------------------------------------------------------------------
# Teste t de Student (duas médias independentes)
# ---------------------------------------------------------------------------
def teste_t(grupo_a, grupo_b, nome_a: str, nome_b: str, variavel: str,
            pergunta: str, alternativa: str = "two-sided") -> dict:
    """
    Compara as médias de dois grupos independentes.

    Escolha do teste:
      - Levene não rejeita H0 → t de Student clássico (variâncias iguais)
      - Levene rejeita H0     → t de Welch (não supõe variâncias iguais)
    Normalidade: com n > 30 em cada grupo, o Teorema Central do Limite garante
    que a MÉDIA amostral é aproximadamente normal, mesmo que os dados não sejam.
    """
    a = np.asarray(grupo_a, dtype=float)
    b = np.asarray(grupo_b, dtype=float)

    normalidade = checar_normalidade(a, b)
    homog = checar_homogeneidade(a, b)
    var_iguais = homog["variancias_iguais"]

    res = stats.ttest_ind(a, b, equal_var=var_iguais, alternative=alternativa)
    ic = res.confidence_interval(confidence_level=CONFIANCA)  # IC de média_a - média_b

    # d de Cohen com desvio padrão combinado
    na, nb = len(a), len(b)
    dp_comb = np.sqrt(((na - 1) * a.var(ddof=1) + (nb - 1) * b.var(ddof=1)) / (na + nb - 2))
    d = (a.mean() - b.mean()) / dp_comb

    simbolo = {"two-sided": "≠", "less": "<", "greater": ">"}[alternativa]
    return {
        "pergunta": pergunta,
        "teste": "t de Student" if var_iguais else "t de Welch",
        "variaveis": f"{variavel} por grupo ({nome_a} × {nome_b})",
        "H0": f"μ({nome_a}) = μ({nome_b}): a média de {variavel} é igual nos dois grupos",
        "H1": f"μ({nome_a}) {simbolo} μ({nome_b})",
        "pressupostos": {
            "normalidade_shapiro": normalidade,
            "levene": homog,
            "tcl_aplicavel": min(na, nb) > 30,
        },
        "media_a": a.mean(), "media_b": b.mean(),
        "diferenca_medias": a.mean() - b.mean(),
        "ic_inferior": ic.low, "ic_superior": ic.high,
        "estatistica_nome": "t",
        "estatistica": res.statistic,
        "gl": res.df,
        "p_valor": res.pvalue,
        "decisao": decisao(res.pvalue),
        "efeito_nome": "d de Cohen",
        "efeito": d,
        "efeito_classe": classificar_d(d),
    }


# ---------------------------------------------------------------------------
# ANOVA (três ou mais médias)
# ---------------------------------------------------------------------------
def anova(df: pd.DataFrame, valor: str, grupo: str, pergunta: str) -> dict:
    """
    ANOVA de um fator: compara as médias de `valor` entre os níveis de `grupo`.

    Escolha do teste:
      - Levene não rejeita H0 → ANOVA clássica (F de Fisher)
      - Levene rejeita H0     → ANOVA de Welch (não supõe variâncias iguais)
    Se H0 for rejeitada, o teste post-hoc de Tukey HSD mostra QUAIS pares diferem.
    """
    niveis = [n for n in df[grupo].dropna().unique()]
    try:
        niveis = sorted(niveis)
    except TypeError:
        pass
    grupos = [df.loc[df[grupo] == n, valor].to_numpy(dtype=float) for n in niveis]

    # Normalidade avaliada nos resíduos (valor - média do grupo)
    residuos = np.concatenate([g - g.mean() for g in grupos])
    normalidade = checar_normalidade(residuos)[0]
    homog = checar_homogeneidade(*grupos)
    var_iguais = homog["variancias_iguais"]

    if var_iguais:
        f, p = stats.f_oneway(*grupos)
        nome, gl = "ANOVA (F de Fisher)", (len(grupos) - 1, len(residuos) - len(grupos))
    else:
        r = anova_oneway(grupos, use_var="unequal")
        f, p = r.statistic, r.pvalue
        nome, gl = "ANOVA de Welch", (r.df_num, r.df_denom)

    # eta² = SQ entre grupos / SQ total → proporção da variação explicada pelo grupo
    todos = np.concatenate(grupos)
    sq_entre = sum(len(g) * (g.mean() - todos.mean()) ** 2 for g in grupos)
    sq_total = ((todos - todos.mean()) ** 2).sum()
    eta2 = sq_entre / sq_total

    tukey = None
    if p < ALFA:
        t = pairwise_tukeyhsd(df[valor].astype(float), df[grupo].astype(str), alpha=ALFA)
        tukey = pd.DataFrame(t.summary().data[1:], columns=t.summary().data[0])

    return {
        "pergunta": pergunta,
        "teste": nome,
        "variaveis": f"{valor} por {grupo} ({len(grupos)} grupos)",
        "H0": f"As médias de {valor} são iguais em todos os níveis de {grupo}",
        "H1": f"Pelo menos um nível de {grupo} tem média de {valor} diferente",
        "pressupostos": {
            "normalidade_residuos_shapiro": normalidade,
            "levene": homog,
            "n_por_grupo": {str(n): len(g) for n, g in zip(niveis, grupos)},
            "tcl_aplicavel": min(len(g) for g in grupos) > 30,
        },
        "medias_por_grupo": {str(n): g.mean() for n, g in zip(niveis, grupos)},
        "estatistica_nome": "F",
        "estatistica": f,
        "gl": gl,
        "p_valor": p,
        "decisao": decisao(p),
        "efeito_nome": "η² (eta quadrado)",
        "efeito": eta2,
        "efeito_classe": classificar_eta2(eta2),
        "tukey": tukey,
    }


# ---------------------------------------------------------------------------
# Qui-Quadrado de independência
# ---------------------------------------------------------------------------
def qui_quadrado(df: pd.DataFrame, var_x: str, var_y: str, pergunta: str) -> dict:
    """
    Testa se duas variáveis categóricas são independentes.

    Pressuposto: frequência ESPERADA ≥ 5 em todas as células (Cochran).
    Em tabelas 2×2 o scipy aplica a correção de continuidade de Yates,
    que deixa o teste um pouco mais conservador.
    """
    tabela = pd.crosstab(df[var_x], df[var_y])
    chi2, p, gl, esperado = stats.chi2_contingency(tabela)
    n = tabela.to_numpy().sum()
    gl_min = min(tabela.shape) - 1
    v = np.sqrt(chi2 / (n * gl_min))  # V de Cramér

    return {
        "pergunta": pergunta,
        "teste": "Qui-Quadrado de independência" + (" (correção de Yates)" if tabela.shape == (2, 2) else ""),
        "variaveis": f"{var_x} × {var_y}",
        "H0": f"{var_x} e {var_y} são independentes (a taxa de saída é a mesma em todos os níveis)",
        "H1": f"{var_x} e {var_y} estão associadas",
        "pressupostos": {
            "menor_freq_esperada": float(esperado.min()),
            "todas_esperadas_maior_igual_5": bool((esperado >= 5).all()),
        },
        "tabela_observada": tabela,
        "tabela_esperada": pd.DataFrame(esperado, index=tabela.index, columns=tabela.columns),
        "estatistica_nome": "χ²",
        "estatistica": chi2,
        "gl": gl,
        "p_valor": p,
        "decisao": decisao(p),
        "efeito_nome": "V de Cramér",
        "efeito": v,
        "efeito_classe": classificar_cramer(v, gl_min),
    }


# ---------------------------------------------------------------------------
# Teste de correlação
# ---------------------------------------------------------------------------
def teste_correlacao(x, y, nome_x: str, nome_y: str, pergunta: str,
                     metodo: str = "pearson") -> dict:
    """
    Testa se a correlação populacional é zero.
      - Pearson: relação LINEAR entre variáveis quantitativas
      - Spearman: relação MONOTÔNICA (usa postos); robusta a outliers e assimetria
    Os dois são calculados; `metodo` define qual é o principal.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    pear = stats.pearsonr(x, y)
    spear = stats.spearmanr(x, y)
    ic = pear.confidence_interval(confidence_level=CONFIANCA)
    principal = pear if metodo == "pearson" else spear
    r = principal.statistic

    return {
        "pergunta": pergunta,
        "teste": f"Correlação de {'Pearson' if metodo == 'pearson' else 'Spearman'}",
        "variaveis": f"{nome_x} × {nome_y}",
        "H0": f"ρ = 0: não há correlação entre {nome_x} e {nome_y}",
        "H1": "ρ ≠ 0: há correlação",
        "pressupostos": {
            "n": len(x),
            "assimetria_x": stats.skew(x), "assimetria_y": stats.skew(y),
        },
        "pearson_r": pear.statistic, "pearson_p": pear.pvalue,
        "pearson_ic": (ic.low, ic.high),
        "spearman_rho": spear.statistic, "spearman_p": spear.pvalue,
        "estatistica_nome": "r" if metodo == "pearson" else "ρ",
        "estatistica": r,
        "gl": len(x) - 2,
        "p_valor": principal.pvalue,
        "decisao": decisao(principal.pvalue),
        "efeito_nome": "r² (variância compartilhada)",
        "efeito": r ** 2,
        "efeito_classe": classificar_r(r),
    }


# ---------------------------------------------------------------------------
# Múltiplos testes e resumo
# ---------------------------------------------------------------------------
def ajustar_holm(resultados: list) -> list:
    """
    Correção de Holm-Bonferroni: ao fazer vários testes ao mesmo tempo,
    a chance de algum "falso positivo" aumenta. Holm ajusta os p-valores
    para manter o erro global em 5%.
    """
    pvals = [r["p_valor"] for r in resultados]
    rejeita, p_ajust, _, _ = multipletests(pvals, alpha=ALFA, method="holm")
    for r, pa, rj in zip(resultados, p_ajust, rejeita):
        r["p_valor_holm"] = pa
        r["decisao_holm"] = "Rejeita H0" if rj else "Não rejeita H0"
    return resultados


def resumo_markdown(r: dict) -> str:
    """Texto em Markdown com o resultado de um teste (usado nos notebooks)."""
    gl = r["gl"]
    gl_txt = f"({gl[0]:.0f}; {gl[1]:.1f})" if isinstance(gl, tuple) else f"{float(gl):.1f}".replace(".0", "")
    linhas = [
        f"**{r['teste']}** — {r['variaveis']}",
        "",
        f"- H₀: {r['H0']}",
        f"- H₁: {r['H1']}",
        f"- Estatística: {r['estatistica_nome']} = {r['estatistica']:.3f} · gl = {gl_txt}",
        f"- p-valor = {formatar_p(r['p_valor'])}"
        + (f" · p-valor ajustado (Holm) = {formatar_p(r['p_valor_holm'])}" if "p_valor_holm" in r else ""),
        f"- **Decisão (α = {ALFA:.2f}".replace(".", ",") + f"): {r.get('decisao_holm', r['decisao'])}**",
        f"- Tamanho de efeito: {r['efeito_nome']} = {r['efeito']:.3f} ({r['efeito_classe']})",
    ]
    if "ic_inferior" in r:
        linhas.append(f"- IC 95% da diferença de médias: [{r['ic_inferior']:.2f}; {r['ic_superior']:.2f}]")
    return "\n".join(linhas)


def tabela_resumo(resultados: list) -> pd.DataFrame:
    """Uma linha por teste — vira a Tabela-resumo do relatório."""
    linhas = []
    for r in resultados:
        gl = r["gl"]
        if isinstance(gl, tuple):
            gl = f"({gl[0]:.0f}; {gl[1]:.1f})"
        else:
            gl = f"{gl:.1f}" if isinstance(gl, float) and not float(gl).is_integer() else f"{gl:.0f}"
        linhas.append({
            "pergunta": r["pergunta"],
            "teste": r["teste"],
            "variaveis": r["variaveis"],
            "H0": r["H0"],
            "estatistica": f"{r['estatistica_nome']} = {r['estatistica']:.3f}",
            "gl": gl,
            "p_valor": r["p_valor"],
            "p_valor_holm": r.get("p_valor_holm", np.nan),
            "decisao": r.get("decisao_holm", r["decisao"]),
            "efeito": f"{r['efeito_nome']} = {r['efeito']:.3f} ({r['efeito_classe']})",
        })
    return pd.DataFrame(linhas)
