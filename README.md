# Fatores associados à rotatividade de funcionários — IBM HR Analytics

> Atividade prática da disciplina **SISB110 — Ciência dos Dados e Inteligência Empresarial**
> Universidade Federal de Alagoas · Campus Arapiraca · Unidade Educacional Penedo · Bacharelado em Sistemas de Informação
> **Aluno:** José Gabriel Fideles Silva · **Docente:** Jário José · 2026

Análise **descritiva** e **inferencial** da base *IBM HR Analytics Employee Attrition & Performance*, com um **relatório executivo** que transforma os resultados estatísticos em recomendações de retenção de pessoas.

📄 **Relatório executivo:** [`reports/relatorio_executivo.pdf`](reports/relatorio_executivo.pdf)

---

## 1. Problema de negócio

A saída voluntária de funcionários gera custos de recrutamento, treinamento e perda de produtividade. Este estudo busca responder:

> **Objetivo geral:** identificar os fatores salariais, de envolvimento e de ambiente de trabalho associados à rotatividade de funcionários, para subsidiar ações de retenção priorizadas por evidência estatística.

| # | Pergunta de negócio | Procedimento inferencial |
|---|---|---|
| Q1 | Qual é a taxa de rotatividade e ela difere entre departamentos? | IC 95% (Wilson) + Qui-Quadrado |
| Q2 | Funcionários que saem ganham menos do que os que ficam? | Teste t (Welch) + IC 95% da diferença de médias |
| Q3 | Envolvimento, ambiente, satisfação e equilíbrio vida-trabalho estão associados à saída? | Qui-Quadrado ×4 + correção de Holm |
| Q4 | Fazer hora extra está associado a mais saídas? | Qui-Quadrado 2×2 + IC 95% da diferença de proporções |
| Q5 | O desempenho e o envolvimento se refletem no reajuste salarial? | Teste t + ANOVA + Teste de correlação |

## 2. Principais resultados

| Achado | Evidência (α = 0,05) |
|---|---|
| **Taxa de rotatividade: 16,1%** | IC 95%: 14,3% a 18,1% |
| **Hora extra triplica o risco de saída** (30,5% × 10,4%) | χ²(1) = 87,6, p < 0,001; RR = 2,9; IC da diferença: 15,4 a 25,0 p.p. |
| **Envolvimento baixo → 33,7% de saída** (contra 9,0% no muito alto) | χ²(3) = 28,5, p (Holm) < 0,001 |
| Ambiente, satisfação e vida-trabalho também associados | 3 testes χ², todos p (Holm) < 0,002 |
| **Cargo pesa mais que departamento** (Representante de Vendas: 39,8%) | V de Cramér: cargo 0,24 × departamento 0,09 |
| Quem sai ganha US$ 2.046 a menos por mês, **mas dentro do mesmo nível a renda é igual** | t de Welch = −7,48, p < 0,001 |
| **O reajuste depende só da nota de desempenho**, e a nota não diferencia quem sai | t (nota): p < 0,001; ANOVA (envolvimento): p = 0,36; correlação (renda): p = 0,20 |

**Recomendações:** (1) gestão ativa de horas extras; (2) programa de retenção para cargos de entrada; (3) alerta precoce via pesquisa de clima; (4) incluir o envolvimento na política de reconhecimento. Detalhes e evidências na Seção 5 do relatório.

> ⚠️ Os dados são **fictícios** (criados pela IBM para fins didáticos), e o estudo é **observacional**: os resultados indicam **associação, não causalidade**.

## 3. Dados

- **Fonte:** [Kaggle — IBM HR Analytics Employee Attrition & Performance](https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset/data)
- **Arquivo:** `data/raw/WA_Fn-UseC_-HR-Employee-Attrition.csv` (1.470 linhas × 35 colunas, nunca é alterado)
- **Dicionário de dados:** [`docs/dicionario_dados.md`](docs/dicionario_dados.md)

**Decisões de limpeza** (detalhadas no notebook 01):

| Verificação | Decisão |
|---|---|
| Valores ausentes / duplicatas | Nenhum encontrado, nenhuma ação |
| `EmployeeCount`, `StandardHours`, `Over18` | Removidas (valor constante) |
| `DailyRate`, `HourlyRate`, `MonthlyRate` | Fora da análise (inconsistentes com a renda: correlação ≈ 0) |
| Outliers (regra do IQR) | **Mantidos**: valores legítimos; tratados com testes robustos |
| Escalas 1–4 | Convertidas em categorias ordinais rotuladas |

## 4. Estrutura do repositório

```
sisb110-ibm-hr-analytics/
├── README.md                 ← este arquivo
├── requirements.txt          ← bibliotecas com versões fixadas
├── run_all.py                ← executa TODO o projeto do zero
├── pytest.ini
├── data/
│   ├── raw/                  ← CSV original do Kaggle
│   └── processed/            ← base limpa (gerada pelo notebook 01)
├── notebooks/
│   ├── 01_contexto_e_limpeza.ipynb   ← Etapa I + qualidade e limpeza
│   ├── 02_analise_descritiva.ipynb   ← medidas, frequências, gráficos, correlação
│   └── 03_analise_inferencial.ipynb  ← ICs e testes de hipóteses
├── src/                      ← funções reutilizáveis (comentadas)
│   ├── config.py             ← caminhos, α, cores, rótulos, tipagem
│   ├── limpeza.py            ← carregamento, qualidade, limpeza
│   ├── descritiva.py         ← medidas, frequências, taxas, correlação
│   ├── inferencia.py         ← IC, t, ANOVA, qui-quadrado, correlação, Holm
│   ├── graficos.py           ← estilo e gráficos padronizados
│   └── relatorio.py          ← gera o relatório DOCX/PDF a partir do modelo
├── reports/
│   ├── figures/              ← fig01…fig13 (PNG)
│   ├── tables/               ← todas as tabelas em CSV + numeros_chave.json
│   ├── insights.md           ← insights consolidados
│   ├── relatorio_executivo.docx
│   └── relatorio_executivo.pdf
├── tests/                    ← testes automatizados (pytest)
└── docs/
    ├── dicionario_dados.md
    └── modelo_relatorio/     ← modelo do relatório (exportado do Google Docs)
```

## 5. Como executar

**Pré-requisitos:** Python 3.11+ (testado no 3.14) e, para gerar o PDF, o [LibreOffice](https://www.libreoffice.org/).

```bash
git clone https://github.com/SEU-USUARIO/sisb110-ibm-hr-analytics.git
cd sisb110-ibm-hr-analytics
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run_all.py                  # notebooks + relatório (≈ 1 min)
pytest -v                          # testes automatizados
```

- `python run_all.py --sem-pdf` executa só os notebooks (sem LibreOffice).
- Para explorar passo a passo: `jupyter notebook notebooks/` e rode os notebooks na ordem 01 → 02 → 03.

### Como o relatório é gerado
`src/relatorio.py` abre o modelo em `docs/modelo_relatorio/` (capa, folha de rosto e seções vindas do Google Docs), escreve o texto e insere tabelas e figuras. **Todos os números são lidos de `reports/tables/`**, nenhum é digitado à mão. Em seguida converte o arquivo para PDF com o LibreOffice e atualiza o sumário com as páginas reais.

## 6. Metodologia estatística (resumo)

- **α = 0,05** em todos os testes; ICs de **95%**.
- Para cada teste: H₀/H₁ → pressupostos → escolha justificada → estatística e p-valor → decisão → tamanho de efeito → interpretação de negócio.
- Pressupostos: Shapiro-Wilk e Q-Q (normalidade), Levene (variâncias → Welch quando diferentes), frequências esperadas ≥ 5 (qui-quadrado), Teorema Central do Limite para amostras grandes.
- Tamanhos de efeito: V de Cramér, d de Cohen, η², r (Cohen, 1988).
- Correção de Holm para múltiplos testes (Q3).

## 7. Testes e verificação

`pytest` roda **29 testes** em três arquivos:
- `test_limpeza.py`: formato da base, ausência de nulos e duplicatas, colunas removidas, nenhuma linha perdida, tipos ordinais;
- `test_inferencia.py`: cada função estatística conferida contra o SciPy ou contra a fórmula manual (Wilson, Cramér, Holm etc.);
- `test_resultados.py`: os números do relatório batem com um recálculo direto da base, e as decisões seguem a regra p < α.

---
*Paleta dos gráficos: azul `#2a78d6` (ficou) e laranja `#eb6834` (saiu), escolhidas para serem distinguíveis por pessoas com daltonismo.*
