"""
graficos.py — Funções de visualização com um estilo único.

Padrões adotados (para todas as figuras do relatório):
  - Azul = ficou, laranja = saiu (paleta testada para daltonismo)
  - Grade clara e discreta, sem bordas superior/direita
  - Rótulos de valor só onde ajudam a leitura (ex.: taxas nas barras)
  - Linha tracejada cinza com a taxa geral de saída como referência
  - Figuras salvas em PNG 200 dpi em reports/figures/
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyBboxPatch
from scipy import stats

from src import config


def aplicar_estilo() -> None:
    """Define o visual padrão do matplotlib para o projeto."""
    plt.rcParams.update({
        "figure.dpi": 110,
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": config.COR_TEXTO_SEC,
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.grid.axis": "y",
        "grid.color": config.COR_GRADE,
        "grid.linewidth": 0.8,
        "axes.axisbelow": True,
        "axes.titlesize": 11,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.labelsize": 9.5,
        "axes.labelcolor": config.COR_TEXTO_SEC,
        "xtick.color": config.COR_TEXTO_SEC,
        "ytick.color": config.COR_TEXTO_SEC,
        "xtick.labelsize": 8.5,
        "ytick.labelsize": 8.5,
        "legend.frameon": False,
        "legend.fontsize": 8.5,
        "font.family": "DejaVu Sans",
        "text.color": config.COR_TEXTO,
    })


def salvar(fig, nome: str) -> None:
    """Salva a figura em reports/figures/<nome>.png."""
    config.PASTA_FIGURAS.mkdir(parents=True, exist_ok=True)
    fig.savefig(config.PASTA_FIGURAS / f"{nome}.png")


def pct_br(valor: float, casas: int = 1) -> str:
    """Formata percentual no padrão brasileiro (vírgula decimal): 16.1 → '16,1%'."""
    return f"{valor:.{casas}f}%".replace(".", ",")


def _formatar_pct(ax, eixo: str = "y") -> None:
    fmt = mtick.PercentFormatter(decimals=0)
    (ax.yaxis if eixo == "y" else ax.xaxis).set_major_formatter(fmt)


# ---------------------------------------------------------------------------
# Univariados
# ---------------------------------------------------------------------------
def grade_histogramas(df: pd.DataFrame, colunas: list, ncols: int = 4):
    """Histograma de cada variável numérica com linhas de média e mediana."""
    nlin = int(np.ceil(len(colunas) / ncols))
    fig, axes = plt.subplots(nlin, ncols, figsize=(3.2 * ncols, 2.5 * nlin))
    for ax, col in zip(axes.flat, colunas):
        dados = df[col]
        discreta = dados.nunique() <= 20
        bins = np.arange(dados.min() - 0.5, dados.max() + 1.5) if discreta else 25
        ax.hist(dados, bins=bins, color=config.COR_FICOU, edgecolor="white", linewidth=0.6)
        ax.axvline(dados.mean(), color=config.COR_SAIU, lw=1.6, label="Média")
        ax.axvline(dados.median(), color=config.COR_TEXTO, lw=1.2, ls="--", label="Mediana")
        ax.set_title(config.NOMES_PT.get(col, col), fontsize=9.5)
        ax.set_ylabel("")
        ax.text(0.98, 0.95, f"assim. = {dados.skew():.2f}".replace(".", ","), transform=ax.transAxes,
                ha="right", va="top", fontsize=7.5, color=config.COR_TEXTO_SEC)
    for ax in list(axes.flat)[len(colunas):]:
        ax.axis("off")
    axes.flat[0].legend(loc="upper left", fontsize=7.5)
    fig.tight_layout()
    return fig


def grade_barras(df: pd.DataFrame, colunas: list, ncols: int = 4, rotulos: dict | None = None):
    """Gráfico de barras horizontais (frequência relativa) de cada categórica."""
    nlin = int(np.ceil(len(colunas) / ncols))
    fig, axes = plt.subplots(nlin, ncols, figsize=(3.6 * ncols, 2.4 * nlin))
    for ax, col in zip(axes.flat, colunas):
        contagem = df[col].value_counts(normalize=True, sort=False) * 100
        if not (isinstance(df[col].dtype, pd.CategoricalDtype) and df[col].cat.ordered):
            contagem = contagem.sort_values()
        else:
            contagem = contagem.iloc[::-1]
        ax.barh(contagem.index.astype(str), contagem.values, color=config.COR_FICOU, height=0.65)
        for i, v in enumerate(contagem.values):
            ax.text(v + 1, i, pct_br(v, 0), va="center", fontsize=7.5, color=config.COR_TEXTO_SEC)
        titulo = (rotulos or {}).get(col, config.NOMES_PT.get(col.replace("_rot", ""), col))
        ax.set_title(titulo, fontsize=9.5)
        ax.set_xlim(0, contagem.max() * 1.25)
        ax.grid(axis="x"); ax.grid(axis="y", visible=False)
        _formatar_pct(ax, "x")
        ax.tick_params(axis="y", labelsize=7.5)
    for ax in list(axes.flat)[len(colunas):]:
        ax.axis("off")
    fig.tight_layout()
    return fig


def grade_boxplots(df: pd.DataFrame, colunas: list, ncols: int = 4):
    """Boxplots individuais para visualizar os outliers pela regra do IQR."""
    nlin = int(np.ceil(len(colunas) / ncols))
    fig, axes = plt.subplots(nlin, ncols, figsize=(3.0 * ncols, 2.1 * nlin))
    for ax, col in zip(axes.flat, colunas):
        ax.boxplot(df[col], vert=False, widths=0.55, patch_artist=True,
                   boxprops=dict(facecolor="#cde2fb", edgecolor=config.COR_FICOU),
                   medianprops=dict(color=config.COR_TEXTO, lw=1.5),
                   whiskerprops=dict(color=config.COR_FICOU),
                   capprops=dict(color=config.COR_FICOU),
                   flierprops=dict(marker="o", markersize=3.5, markerfacecolor=config.COR_SAIU,
                                   markeredgecolor="white", markeredgewidth=0.4, alpha=0.8))
        ax.set_yticks([])
        ax.set_title(config.NOMES_PT.get(col, col), fontsize=9)
        ax.grid(axis="x"); ax.grid(axis="y", visible=False)
    for ax in list(axes.flat)[len(colunas):]:
        ax.axis("off")
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Taxas de saída por grupo (bivariada com a variável-alvo)
# ---------------------------------------------------------------------------
def barras_taxa(ax, tabela: pd.DataFrame, coluna: str, taxa_geral: float,
                titulo: str = "", horizontal: bool = False, destacar_maior: bool = True) -> None:
    """
    Barras com a taxa de saída (%) de cada grupo, barras de erro = IC 95% (Wilson)
    e linha tracejada com a taxa geral. O grupo de maior taxa recebe a cor laranja.
    """
    rotulos = tabela[coluna].astype(str).tolist()
    taxas = tabela["taxa_pct"].to_numpy()
    erro = np.vstack([taxas - tabela["ic_inf_pct"], tabela["ic_sup_pct"] - taxas])
    cores = [config.COR_FICOU] * len(taxas)
    if destacar_maior:
        cores[int(np.argmax(taxas))] = config.COR_SAIU
    pos = np.arange(len(taxas))
    if horizontal:
        ax.barh(pos, taxas, color=cores, height=0.62, xerr=erro,
                error_kw=dict(ecolor=config.COR_TEXTO_SEC, lw=1, capsize=3))
        ax.set_yticks(pos, rotulos)
        ax.axvline(taxa_geral, color=config.COR_NEUTRA, ls="--", lw=1)
        for i, (t, s) in enumerate(zip(taxas, tabela["ic_sup_pct"])):
            ax.text(s + 0.8, i, pct_br(t), va="center", fontsize=8, color=config.COR_TEXTO)
        ax.grid(axis="x"); ax.grid(axis="y", visible=False)
        _formatar_pct(ax, "x")
        ax.set_xlim(0, tabela["ic_sup_pct"].max() * 1.2)
    else:
        ax.bar(pos, taxas, color=cores, width=0.62, yerr=erro,
               error_kw=dict(ecolor=config.COR_TEXTO_SEC, lw=1, capsize=3))
        ax.set_xticks(pos, rotulos)
        ax.axhline(taxa_geral, color=config.COR_NEUTRA, ls="--", lw=1)
        for i, (t, s) in enumerate(zip(taxas, tabela["ic_sup_pct"])):
            ax.text(i, s + 0.8, pct_br(t), ha="center", fontsize=8, color=config.COR_TEXTO)
        _formatar_pct(ax, "y")
        ax.set_ylim(0, tabela["ic_sup_pct"].max() * 1.18)
        ax.set_ylabel("Taxa de saída")
    ax.set_title(titulo)


def nota_taxa_geral(fig, taxa_geral: float) -> None:
    fig.text(0.01, -0.02, f"Linha tracejada: taxa geral de saída ({pct_br(taxa_geral)}). "
             "Barras de erro: IC 95% (Wilson). Laranja: maior taxa.",
             fontsize=7.5, color=config.COR_TEXTO_SEC)


def boxplot_por_status(ax, df: pd.DataFrame, valor: str, titulo: str = "", mostrar_media: bool = True) -> None:
    """Boxplot de uma variável numérica para Ficou × Saiu, com a média marcada (◆)."""
    sns.boxplot(data=df, x="Status", y=valor, hue="Status", palette=config.PALETA_ATTRITION,
                width=0.5, fliersize=2.5, linewidth=1, ax=ax, legend=False,
                boxprops=dict(alpha=0.85), medianprops=dict(color="white", lw=1.8))
    if mostrar_media:
        medias = df.groupby("Status", observed=True)[valor].mean()
        for i, (k, m) in enumerate(medias.items()):
            ax.scatter(i, m, marker="D", s=36, color=config.COR_TEXTO, zorder=5,
                       edgecolor="white", linewidth=0.8)
            ax.text(i + 0.3, m, f"média\n{m:,.0f}".replace(",", "."), va="center",
                    fontsize=7.5, color=config.COR_TEXTO)
    ax.set_xlabel("")
    ax.set_ylabel(config.NOMES_PT.get(valor, valor))
    ax.set_title(titulo)


# ---------------------------------------------------------------------------
# Correlação
# ---------------------------------------------------------------------------
def mapa_correlacao(matriz: pd.DataFrame, titulo: str = ""):
    """Mapa de calor da matriz de correlação (escala divergente azul ↔ vermelho)."""
    cmap = LinearSegmentedColormap.from_list(
        "divergente", ["#104281", "#5598e7", "#f0efec", "#e66767", "#a32626"])
    rotulos = [config.NOMES_PT.get(c, c) for c in matriz.columns]
    mascara = np.triu(np.ones_like(matriz, dtype=bool), k=1)
    fig, ax = plt.subplots(figsize=(11, 9))
    sns.heatmap(matriz, mask=mascara, cmap=cmap, vmin=-1, vmax=1, center=0,
                annot=True, fmt=".2f", annot_kws={"size": 6.5},
                linewidths=0.6, linecolor="white", square=True,
                xticklabels=rotulos, yticklabels=rotulos,
                cbar_kws={"shrink": 0.6, "label": "Coeficiente de correlação"}, ax=ax)
    ax.grid(False)
    ax.tick_params(axis="both", labelsize=7.5)
    plt.setp(ax.get_xticklabels(), rotation=55, ha="right")
    ax.set_title(titulo)
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Pressupostos
# ---------------------------------------------------------------------------
def qq_plot(ax, dados, titulo: str, cor: str = config.COR_FICOU) -> None:
    """Gráfico Q-Q: se os pontos seguem a reta, os dados são aproximadamente normais."""
    (teo, obs), (inc, intercepto, _) = stats.probplot(np.asarray(dados, dtype=float), dist="norm")
    ax.scatter(teo, obs, s=7, color=cor, alpha=0.6, edgecolor="none")
    ax.plot(teo, inc * teo + intercepto, color=config.COR_TEXTO, lw=1.2)
    ax.set_xlabel("Quantis teóricos (normal)")
    ax.set_ylabel("Quantis observados")
    ax.set_title(titulo, fontsize=9.5)


# ---------------------------------------------------------------------------
# Intervalos de confiança
# ---------------------------------------------------------------------------
def grafico_ics(ax, tabela: pd.DataFrame, rotulo: str, estimativa: str, inf: str, sup: str,
                referencia: float | None = None, titulo: str = "", formato: str = "{:.1f}%") -> None:
    """Gráfico de intervalos (ponto = estimativa, linha = IC 95%)."""
    pos = np.arange(len(tabela))[::-1]
    ax.hlines(pos, tabela[inf], tabela[sup], color=config.COR_FICOU, lw=2.2)
    ax.scatter(tabela[estimativa], pos, color=config.COR_FICOU, s=40, zorder=3,
               edgecolor="white", linewidth=1)
    for p, e, s in zip(pos, tabela[estimativa], tabela[sup]):
        ax.text(s, p + 0.18, " " + formato.format(e).replace(".", ","), fontsize=8, color=config.COR_TEXTO)
    ax.set_yticks(pos, tabela[rotulo].astype(str))
    if referencia is not None:
        ax.axvline(referencia, color=config.COR_NEUTRA, ls="--", lw=1)
    ax.grid(axis="x"); ax.grid(axis="y", visible=False)
    ax.set_title(titulo)


# ---------------------------------------------------------------------------
# Fluxo metodológico (Figura da Metodologia)
# ---------------------------------------------------------------------------
def fluxo_pipeline():
    """Desenha o fluxo das etapas do projeto (dados brutos → relatório)."""
    etapas = [
        ("1. Dados brutos", "CSV Kaggle\n1.470 × 35"),
        ("2. Qualidade", "ausentes, duplicatas,\noutliers (IQR)"),
        ("3. Limpeza", "remove constantes,\ntipagem, faixas"),
        ("4. Descritiva", "medidas, frequências,\ngráficos, correlação"),
        ("5. Inferência", "IC, t, ANOVA,\nχ², correlação"),
        ("6. Relatório", "insights e\nrecomendações"),
    ]
    fig = plt.figure(figsize=(12, 1.8))
    ax = fig.add_axes([0, 0, 1, 1])  # eixo ocupa a figura inteira (sem margens)
    ax.set_xlim(0, len(etapas)); ax.set_ylim(0, 1); ax.axis("off")
    for i, (tit, desc) in enumerate(etapas):
        cor = config.COR_SAIU if i == 4 else config.COR_FICOU  # destaque: inferência
        ax.add_patch(FancyBboxPatch((i + 0.06, 0.1), 0.8, 0.8, boxstyle="round,pad=0,rounding_size=0.06",
                                    facecolor="white", edgecolor=cor, lw=1.6))
        ax.text(i + 0.46, 0.68, tit, ha="center", va="center", fontsize=9, weight="bold", color=cor)
        ax.text(i + 0.46, 0.36, desc, ha="center", va="center", fontsize=7.3, color=config.COR_TEXTO_SEC)
        if i < len(etapas) - 1:
            ax.annotate("", xy=(i + 1.05, 0.5), xytext=(i + 0.87, 0.5),
                        arrowprops=dict(arrowstyle="-|>", color=config.COR_TEXTO_SEC, lw=1.2))
    return fig
