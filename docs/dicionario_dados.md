# Dicionário de dados

Base: **IBM HR Analytics Employee Attrition & Performance** ([Kaggle](https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset/data)) · 1.470 linhas × 35 colunas.

Os códigos das escalas seguem a documentação oficial do dataset.

| Variável | Descrição | Tipo estatístico | Valores / codificação | Uso na análise |
|---|---|---|---|---|
| `Age` | Idade | Quantitativa contínua | 18 a 60 | Analisada |
| `Attrition` | Rotatividade (saiu?) | Qualitativa nominal | Yes = saiu · No = permaneceu | Analisada |
| `BusinessTravel` | Viagens a trabalho | Qualitativa ordinal | Non-Travel · Travel_Rarely · Travel_Frequently | Analisada |
| `DailyRate` | Taxa diária | — | 102 a 1499 | Fora da análise (inconsistente) |
| `Department` | Departamento | Qualitativa nominal | Human Resources a Sales | Analisada |
| `DistanceFromHome` | Distância de casa (km) | Quantitativa discreta | 1 a 29 | Analisada |
| `Education` | Escolaridade | Qualitativa ordinal | 1 = Abaixo da graduação · 2 = Graduação incompleta · 3 = Bacharelado · 4 = Mestrado · 5 = Doutorado | Analisada |
| `EducationField` | Área de formação | Qualitativa nominal | Human Resources a Technical Degree | Analisada |
| `EmployeeCount` | Contagem (sempre 1) | — | 1 a 1 | Removida (constante) |
| `EmployeeNumber` | Número do funcionário | — | 1 a 2068 | Identificador |
| `EnvironmentSatisfaction` | Satisfação com o ambiente | Qualitativa ordinal | 1 = Baixo · 2 = Médio · 3 = Alto · 4 = Muito alto | Analisada |
| `Gender` | Gênero | Qualitativa nominal | Female a Male | Analisada |
| `HourlyRate` | Taxa horária | — | 30 a 100 | Fora da análise (inconsistente) |
| `JobInvolvement` | Envolvimento com o trabalho | Qualitativa ordinal | 1 = Baixo · 2 = Médio · 3 = Alto · 4 = Muito alto | Analisada |
| `JobLevel` | Nível do cargo | Qualitativa ordinal | 1 (entrada) a 5 (executivo) | Analisada |
| `JobRole` | Cargo | Qualitativa nominal | Healthcare Representative a Sales Representative | Analisada |
| `JobSatisfaction` | Satisfação com o trabalho | Qualitativa ordinal | 1 = Baixo · 2 = Médio · 3 = Alto · 4 = Muito alto | Analisada |
| `MaritalStatus` | Estado civil | Qualitativa nominal | Divorced a Single | Analisada |
| `MonthlyIncome` | Renda mensal (US$) | Quantitativa contínua | 1009 a 19999 | Analisada |
| `MonthlyRate` | Taxa mensal | — | 2094 a 26999 | Fora da análise (inconsistente) |
| `NumCompaniesWorked` | Nº de empresas anteriores | Quantitativa discreta | 0 a 9 | Analisada |
| `Over18` | Maior de 18 (sempre Y) | — | Y a Y | Removida (constante) |
| `OverTime` | Hora extra | Qualitativa nominal | Yes / No | Analisada |
| `PercentSalaryHike` | Reajuste salarial (%) | Quantitativa discreta | 11 a 25 | Analisada |
| `PerformanceRating` | Avaliação de desempenho | Qualitativa ordinal | 1 = Baixo · 2 = Bom · 3 = Excelente · 4 = Excepcional (só 3 e 4 ocorrem) | Analisada |
| `RelationshipSatisfaction` | Satisfação com relacionamentos | Qualitativa ordinal | 1 = Baixo · 2 = Médio · 3 = Alto · 4 = Muito alto | Analisada |
| `StandardHours` | Horas padrão (sempre 80) | — | 80 a 80 | Removida (constante) |
| `StockOptionLevel` | Nível de ações (stock options) | Qualitativa ordinal | 0 (nenhuma) a 3 | Analisada |
| `TotalWorkingYears` | Anos de experiência total | Quantitativa discreta | 0 a 40 | Analisada |
| `TrainingTimesLastYear` | Treinamentos no último ano | Quantitativa discreta | 0 a 6 | Analisada |
| `WorkLifeBalance` | Equilíbrio vida-trabalho | Qualitativa ordinal | 1 = Ruim · 2 = Bom · 3 = Melhor · 4 = Excelente | Analisada |
| `YearsAtCompany` | Anos na empresa | Quantitativa discreta | 0 a 40 | Analisada |
| `YearsInCurrentRole` | Anos no cargo atual | Quantitativa discreta | 0 a 18 | Analisada |
| `YearsSinceLastPromotion` | Anos desde a última promoção | Quantitativa discreta | 0 a 15 | Analisada |
| `YearsWithCurrManager` | Anos com o gestor atual | Quantitativa discreta | 0 a 17 | Analisada |

## Variáveis derivadas (criadas em `src/limpeza.py`)

| Variável | Descrição |
|---|---|
| `Attrition_bin` | 1 = saiu, 0 = ficou (a média é a taxa de saída) |
| `OverTime_bin` | 1 = faz hora extra |
| `Status` | "Saiu" / "Ficou" |
| `*_rot` | Rótulo em português das escalas ordinais (ex.: `JobInvolvement_rot`) |
| `Departamento`, `Cargo`, `Viagens`, `HoraExtra` | Traduções para português |
| `FaixaEtaria` | 18–25 · 26–35 · 36–45 · 46–60 |
| `FaixaSalarial` | Quartis da renda mensal (Q1 = mais baixa) |
| `FaixaTempoCasa` | 0–2 · 3–5 · 6–10 · 11+ anos |
