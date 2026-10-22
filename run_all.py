"""
run_all.py — Executa todo o projeto do zero, na ordem correta.

    1. notebooks/01_contexto_e_limpeza.ipynb   → data/processed/ + tabelas de qualidade
    2. notebooks/02_analise_descritiva.ipynb   → figuras e tabelas descritivas
    3. notebooks/03_analise_inferencial.ipynb  → testes, ICs e numeros_chave.json
    4. src/relatorio.py                        → reports/relatorio_executivo.docx e .pdf

Uso (com o ambiente virtual ativado):
    python run_all.py              # tudo
    python run_all.py --sem-pdf    # só os notebooks (não precisa de LibreOffice)
"""

import sys
import time
from pathlib import Path

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

RAIZ = Path(__file__).resolve().parent
NOTEBOOKS = [
    "01_contexto_e_limpeza.ipynb",
    "02_analise_descritiva.ipynb",
    "03_analise_inferencial.ipynb",
]


def executar_notebook(nome: str) -> None:
    """Executa o notebook e salva as saídas (gráficos, tabelas) dentro dele."""
    caminho = RAIZ / "notebooks" / nome
    nb = nbformat.read(caminho, as_version=4)
    executor = ExecutePreprocessor(timeout=600, kernel_name="python3")
    executor.preprocess(nb, {"metadata": {"path": str(caminho.parent)}})
    nbformat.write(nb, caminho)


def main() -> None:
    inicio = time.time()
    for nome in NOTEBOOKS:
        t0 = time.time()
        print(f"▶ Executando {nome} ...", flush=True)
        executar_notebook(nome)
        print(f"  ✔ concluído em {time.time() - t0:.0f}s")

    if "--sem-pdf" not in sys.argv:
        print("▶ Gerando o relatório executivo (DOCX + PDF) ...", flush=True)
        sys.path.insert(0, str(RAIZ))
        from src.relatorio import gerar_relatorio
        gerar_relatorio()

    print(f"Pipeline completo em {time.time() - inicio:.0f}s.")


if __name__ == "__main__":
    main()
