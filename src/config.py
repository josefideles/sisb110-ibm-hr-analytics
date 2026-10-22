"""
config.py — Configurações centrais do projeto.

Tudo o que é "constante" fica aqui: caminhos de pastas, nível de
significância, paleta de cores e os rótulos usados para traduzir os
códigos numéricos do dataset (ex.: 1 = "Baixo").

Assim, se algo precisar mudar (ex.: alfa = 0,01), muda-se em um só lugar.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Caminhos
# ---------------------------------------------------------------------------
# A raiz do projeto é a pasta acima de src/. Usar caminhos relativos à raiz
# garante que o projeto rode em qualquer máquina após o "git clone".
RAIZ = Path(__file__).resolve().parents[1]

DADOS_BRUTOS = RAIZ / "data" / "raw" / "WA_Fn-UseC_-HR-Employee-Attrition.csv"
DADOS_LIMPOS = RAIZ / "data" / "processed" / "hr_attrition_limpo.csv"

PASTA_FIGURAS = RAIZ / "reports" / "figures"
PASTA_TABELAS = RAIZ / "reports" / "tables"
PASTA_REPORTS = RAIZ / "reports"
MODELO_RELATORIO = RAIZ / "docs" / "modelo_relatorio" / "modelo_google_docs.docx"

URL_DATASET = "https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset/data"
NOME_REPOSITORIO = "sisb110-ibm-hr-analytics"
# ⚠️ Troque SEU-USUARIO pelo seu usuário do GitHub depois de publicar o repositório
URL_REPOSITORIO = f"https://github.com/SEU-USUARIO/{NOME_REPOSITORIO}"

# ---------------------------------------------------------------------------
# Parâmetros estatísticos
# ---------------------------------------------------------------------------
ALFA = 0.05          # nível de significância usado em todos os testes
CONFIANCA = 0.95     # nível de confiança dos intervalos (1 - alfa)
SEMENTE = 42         # semente aleatória (reprodutibilidade)

# ---------------------------------------------------------------------------
# Paleta de cores (validada para daltonismo — ver README)
# ---------------------------------------------------------------------------
COR_FICOU = "#2a78d6"     # azul  → funcionários que permaneceram
COR_SAIU = "#eb6834"      # laranja → funcionários que saíram
COR_NEUTRA = "#8a8984"    # cinza para marcas sem destaque
COR_TEXTO = "#0b0b0b"
COR_TEXTO_SEC = "#52514e"
COR_GRADE = "#e4e3df"
PALETA_ATTRITION = {"Ficou": COR_FICOU, "Saiu": COR_SAIU}

# Fonte padrão das legendas de figuras e tabelas
FONTE_DADOS = "Fonte: elaboração própria a partir de IBM HR Analytics (Kaggle)."

# ---------------------------------------------------------------------------
# Colunas e rótulos
# ---------------------------------------------------------------------------
# Colunas sem informação (valor único em todas as 1.470 linhas)
COLUNAS_CONSTANTES = ["EmployeeCount", "StandardHours", "Over18"]

# Colunas de "taxa" que não são consistentes com MonthlyIncome
# (mantidas na base, mas fora das análises principais)
COLUNAS_TAXA_INCONSISTENTES = ["DailyRate", "HourlyRate", "MonthlyRate"]

# Rótulos em português para as escalas ordinais (códigos do dicionário oficial)
ROTULOS_SATISFACAO = {1: "Baixo", 2: "Médio", 3: "Alto", 4: "Muito alto"}
ROTULOS_VIDA_TRABALHO = {1: "Ruim", 2: "Bom", 3: "Melhor", 4: "Excelente"}
ROTULOS_EDUCACAO = {1: "Abaixo da graduação", 2: "Graduação incompleta",
                    3: "Bacharelado", 4: "Mestrado", 5: "Doutorado"}
ROTULOS_DESEMPENHO = {1: "Baixo", 2: "Bom", 3: "Excelente", 4: "Excepcional"}

# Variável ordinal → dicionário de rótulos
ESCALAS_ORDINAIS = {
    "EnvironmentSatisfaction": ROTULOS_SATISFACAO,
    "JobInvolvement": ROTULOS_SATISFACAO,
    "JobSatisfaction": ROTULOS_SATISFACAO,
    "RelationshipSatisfaction": ROTULOS_SATISFACAO,
    "WorkLifeBalance": ROTULOS_VIDA_TRABALHO,
    "Education": ROTULOS_EDUCACAO,
    "PerformanceRating": ROTULOS_DESEMPENHO,
}

# Tradução das categorias nominais mais usadas nos gráficos
TRADUCAO_DEPARTAMENTO = {
    "Research & Development": "P&D",
    "Sales": "Vendas",
    "Human Resources": "RH",
}
TRADUCAO_CARGO = {
    "Sales Representative": "Representante de Vendas",
    "Laboratory Technician": "Técnico de Laboratório",
    "Human Resources": "Analista de RH",
    "Sales Executive": "Executivo de Vendas",
    "Research Scientist": "Cientista Pesquisador",
    "Manufacturing Director": "Diretor de Produção",
    "Healthcare Representative": "Representante de Saúde",
    "Manager": "Gerente",
    "Research Director": "Diretor de Pesquisa",
}
TRADUCAO_VIAGEM = {
    "Non-Travel": "Não viaja",
    "Travel_Rarely": "Viaja raramente",
    "Travel_Frequently": "Viaja frequentemente",
}

# Nomes em português das variáveis (para tabelas e gráficos)
NOMES_PT = {
    "Age": "Idade",
    "Attrition": "Rotatividade (saiu?)",
    "BusinessTravel": "Viagens a trabalho",
    "DailyRate": "Taxa diária",
    "Department": "Departamento",
    "DistanceFromHome": "Distância de casa (km)",
    "Education": "Escolaridade",
    "EducationField": "Área de formação",
    "EnvironmentSatisfaction": "Satisfação com o ambiente",
    "Gender": "Gênero",
    "HourlyRate": "Taxa horária",
    "JobInvolvement": "Envolvimento com o trabalho",
    "JobLevel": "Nível do cargo",
    "JobRole": "Cargo",
    "JobSatisfaction": "Satisfação com o trabalho",
    "MaritalStatus": "Estado civil",
    "MonthlyIncome": "Renda mensal (US$)",
    "MonthlyRate": "Taxa mensal",
    "NumCompaniesWorked": "Nº de empresas anteriores",
    "OverTime": "Hora extra",
    "PercentSalaryHike": "Reajuste salarial (%)",
    "PerformanceRating": "Avaliação de desempenho",
    "RelationshipSatisfaction": "Satisfação com relacionamentos",
    "StockOptionLevel": "Nível de ações (stock options)",
    "TotalWorkingYears": "Anos de experiência total",
    "TrainingTimesLastYear": "Treinamentos no último ano",
    "WorkLifeBalance": "Equilíbrio vida-trabalho",
    "YearsAtCompany": "Anos na empresa",
    "YearsInCurrentRole": "Anos no cargo atual",
    "YearsSinceLastPromotion": "Anos desde a última promoção",
    "YearsWithCurrManager": "Anos com o gestor atual",
    "Attrition_bin": "Saiu (1 = sim)",
    "OverTime_bin": "Faz hora extra (1 = sim)",
}

# ---------------------------------------------------------------------------
# Tipagem estatística das variáveis (Etapa II do roteiro)
# ---------------------------------------------------------------------------
TIPOS_VARIAVEIS = {
    "Quantitativa contínua": ["Age", "MonthlyIncome"],
    "Quantitativa discreta": [
        "DistanceFromHome", "NumCompaniesWorked", "PercentSalaryHike",
        "TotalWorkingYears", "TrainingTimesLastYear", "YearsAtCompany",
        "YearsInCurrentRole", "YearsSinceLastPromotion", "YearsWithCurrManager",
    ],
    "Qualitativa nominal": [
        "Attrition", "Department", "JobRole", "EducationField",
        "Gender", "MaritalStatus", "OverTime",
    ],
    "Qualitativa ordinal": [
        "BusinessTravel", "Education", "EnvironmentSatisfaction",
        "JobInvolvement", "JobLevel", "JobSatisfaction", "PerformanceRating",
        "RelationshipSatisfaction", "StockOptionLevel", "WorkLifeBalance",
    ],
}

VARS_NUMERICAS = TIPOS_VARIAVEIS["Quantitativa contínua"] + TIPOS_VARIAVEIS["Quantitativa discreta"]
VARS_CATEGORICAS = TIPOS_VARIAVEIS["Qualitativa nominal"] + TIPOS_VARIAVEIS["Qualitativa ordinal"]
