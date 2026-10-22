# Insights consolidados

Gerados durante a análise (notebooks 02 e 03). Cada insight indica a evidência que o sustenta.

## Descritivos (notebook 02)

1. **Taxa de rotatividade: 16,1%** (237 de 1.470): base desbalanceada, mas com casos suficientes para os testes.
2. **Renda é muito assimétrica** (assimetria 1,37; média US$ 6.503 × mediana US$ 4.919): a mediana representa o salário típico. → Tabela `descritiva_numericas.csv`
3. **Hora extra:** 30,5% de saída × 10,4% sem hora extra. No quartil de menor renda, 58% de quem faz hora extra saiu. → Fig. 8
4. **Cargo > departamento:** Representante de Vendas 39,8%, Técnico de Laboratório 23,9%; cargos de gestão < 7%. → Fig. 5
5. **Renda e senioridade se confundem:** o quartil de menor renda tem 29,3% de saída, mas *dentro do mesmo nível de cargo* quem sai e quem fica ganham quase o mesmo; 60% das saídas estão no nível 1. → Fig. 6, `renda_mediana_por_nivel_status.csv`
6. **O nível mais baixo de cada escala concentra o risco:** envolvimento baixo 33,7%, ambiente baixo 25,4%, vida-trabalho ruim 31,2%, satisfação com o trabalho baixa 22,8%. → Fig. 7
7. **As escalas de satisfação são independentes entre si** (|ρ| < 0,05): cada dimensão exige ação própria. → Fig. 10
8. **Início de carreira é o perfil de risco:** 18–25 anos (35,8%), até 2 anos de casa (29,8%), solteiros (25,5%), viagens frequentes (24,9%). → Fig. 11
9. **Avaliação de desempenho inflada e sem poder de diferenciação:** só notas 3 (85%) e 4 (15%), com saída igual nas duas (16,1% × 16,4%). → Fig. 4 e 9
10. **Reajuste = regra fixa pela nota:** nota 3 → 11–19%; nota 4 → 20–25%. → Fig. 9

## Inferenciais (notebook 03, α = 0,05)

| Pergunta | Conclusão | Evidência |
|---|---|---|
| Q1 | A taxa difere entre departamentos, mas o efeito é desprezível; por cargo o efeito é ≈ 3× maior | χ² = 10,8, p = 0,0045, V = 0,086 · cargo: χ² = 86,2, V = 0,242 |
| Q2 | Quem sai ganha menos (−US$ 2.046/mês), efeito pequeno a médio, mas explicado pela senioridade | t de Welch = −7,48, p < 0,001; IC [−2.583; −1.508]; robusto em log |
| Q3 | Os 4 fatores estão associados à saída; o maior efeito é o do envolvimento | χ² com Holm, todos p < 0,002; V de 0,105 a 0,139 |
| Q4 | Hora extra é a associação mais forte do estudo | χ² = 87,6, p < 0,001; RR = 2,93; IC da diferença [15,4; 25,0] p.p. |
| Q5 | Reajuste depende só da nota, não do envolvimento nem da renda | t: p < 0,001 · ANOVA: p = 0,36 · Spearman: p = 0,20 |

**Mensagem central:** a rotatividade está mais associada a **hora extra**, **início de carreira** e **baixo envolvimento**, enquanto a política de reajuste premia apenas a nota de desempenho, que não diferencia quem sai de quem fica.
