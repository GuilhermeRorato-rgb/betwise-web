# Relatório de validação — 09/10/2026

## Ambiente e resultados

- Windows; Python 3.14.7.
- NumPy 2.5.3, SciPy 1.18.1, Pandas 3.0.6, Plotly 7.1.0, Streamlit 1.65.0, Pytest 9.1.1.
- Instalação em ambiente virtual isolado. Versões transitivas em `requirements-lock.txt`.
- Suíte completa: **39 testes aprovados**, última execução completa em **10,55 segundos**.
- Após os ajustes finais de layout e persistência de cenários, os **2 testes de interface foram executados novamente e aprovados**, em 7,53 segundos. O motor permaneceu inalterado.
- Inicialização real do servidor Streamlit em `127.0.0.1:8501` e inspeção no navegador.
- Conferência visual em larguras de 390 px e 1366 px; cartões reorganizados para telas menores.

AppTest verifica navegação pelas cinco áreas, probabilidades de 0%/100%, mensagens de erro, redefinição dos parâmetros, semente aleatória estável até solicitação de novos sorteios e presença das exportações. Os testes dos gráficos verificam sua serialização e correspondência entre dados do motor e séries exibidas. A inspeção visual não equivale a uma auditoria completa de acessibilidade ou testes em dispositivos físicos.

## Caso de referência

R$ 20 por aposta, cinco vezes por semana, três anos, odd 2, desvantagem hipotética de 5%, retorno anual alternativo de 8%, 10.000 simulações e semente 42. Todos são exemplos editáveis.

| Indicador | Resultado |
|---|---:|
| Número de apostas (ano de 365 dias) | 782 |
| Orçamento | R$ 15.640,00 |
| Probabilidade hipotética | 47,50% |
| ROI esperado | −5,00% |
| Resultado líquido esperado | −R$ 782,00 |
| Média simulada | −R$ 783,67 |
| Desvio-padrão teórico | R$ 558,59 |
| Desvio-padrão amostral | R$ 563,36 |
| Prejuízo binomial exato | 91,37% |
| Prejuízo simulado | 91,39% |
| Percentis simulados 5 e 95 | −R$ 1.720,00 / R$ 120,00 |
| Patrimônio esperado das apostas | R$ 14.858,00 |
| Investimento final hipotético | R$ 17.590,63 |
| Custo de oportunidade esperado | R$ 2.732,63 |

A diferença entre média simulada e teórica é aproximadamente R$ 1,67, menor que o erro-padrão empírico de R$ 5,63. Esse caso é uma verificação numérica, não uma previsão ou recomendação.

## Cobertura matemática

Casos p=0 e p=1; aposta justa; desvantagem de 5%; médias dentro de cinco erros-padrão em 100.000 sorteios; dispersão compatível; variância analítica; reprodução com seed; semente gerada recuperável; taxa zero, positiva, negativa e quase zero; comparação com soma direta de aportes; aporte único no fim do horizonte; rejeição de entradas inválidas e tipos inadequados; cenário grande sem números não finitos; empate com odd decimal; separação de patrimônio e lucro; fronteiras de probabilidades; overround; cenários e sensibilidade.

## Limites da verificação

Não houve publicação pública, auditoria de acessibilidade, teste de concorrência de múltiplos visitantes, nem validação contra o workbook ausente. O investimento é um cenário determinístico com taxa suposta, não um modelo de risco de ativos. O funcionamento na hospedagem escolhida deve ser conferido após publicar.
