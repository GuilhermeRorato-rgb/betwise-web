# Documentação técnica e metodológica

## Escopo e arquitetura

Modelo educacional de orçamento recorrente. O usuário dispõe de `s` em cada oportunidade. Não existe banca inicial, endividamento modelado, interrupção por falta de saldo ou probabilidade de ruína. As apostas são binárias e i.i.d.; os parâmetros não variam dentro de um cenário.

Fluxo: controles → `Parameters` (validação) → `theoretical` + `monte_carlo` → `simulate` (contrato JSON) → tabelas, gráficos e explicações. A interface possui cache limitado a quatro resultados; a lógica é independente do Streamlit. Cenários e sensibilidade usam a mesma função analítica. Não há transmissão dos parâmetros a um modelo externo, persistência de dados pessoais ou credenciais embutidas.

## Fórmulas de apostas

Para X ~ Bernoulli(p), L = s(oX − 1). Vitória rende lucro s(o−1); derrota rende −s. O pagamento bruto é soX; a devolução da aposta não é contada duas vezes.

- E[L] = s(po−1).
- Var(L) = s²o²p(1−p).
- ROI = po−1.
- S_N = soma dos lucros = s(oK−N), K ~ Binomial(N,p).
- E[S_N] = Ns(po−1); Var(S_N) = Ns²o²p(1−p).
- No método de desvantagem: p=(1−h)/o, ROI=−h.
- A chance de equilíbrio 1/o não informa a chance verdadeira.
- Overround = Σ 1/odd_i −1, somente para um mercado mutuamente exclusivo e exaustivo. Não identifica necessariamente a perda esperada efetiva do apostador.

Para prejuízo estrito: K < N/o; para lucro estrito: K > N/o. O empate é reportado separadamente. As fronteiras usam representação decimal da odd para evitar classificar uma igualdade monetária como lucro ou perda por arredondamento binário. Probabilidades teóricas usam CDF/SF/PMF da SciPy. Valores monetários internos usam precisão de ponto flutuante e só são formatados na apresentação; não são um livro contábil com arredondamento por evento.

## Datas e comparação financeira

Um ano corresponde a 365 dias, uma semana a 7 dias e um mês a 1/12 de ano. A frequência anual f é frequência × {365, 365/7, 12}. T é o horizonte em anos. N = piso(fT), com tolerância de 10⁻¹⁰ para artefatos numéricos na conversão. Uma frequência fracionária corresponde a oportunidades igualmente espaçadas, não a apostas fracionárias.

Os aportes ocorrem em t_i = i/f, i=1,…,N, no fim de cada intervalo. O primeiro aporte não ocorre em t=0. Pode existir uma fração final de horizonte sem novo aporte. N é mostrado explicitamente: por exemplo, cinco apostas semanais por três anos correspondem a 782 apostas nesta convenção, não a 780 semanas arredondadas.

No cenário de apostas, os pagamentos são preservados em uma conta sem rendimento: V_A = soK; E[V_A] = Nspo. O resultado líquido é V_A−Ns.

No cenário de investimento, os mesmos s são aplicados nas mesmas datas:

V_I(T) = Σ s(1+r)^(T−i/f).

Com q=(1+r)^(1/f), a expressão computacional é s(q^N−1)/(q−1) × (1+r)^(T−N/f). A implementação usa `log1p` e `expm1` para estabilidade, com limite contínuo para r≈0. A taxa efetiva por intervalo é q−1, nunca r/f como aproximação de juros simples. Retornos negativos maiores que −100% são permitidos.

Custo de oportunidade esperado = V_I(T) − E[V_A]. Pode ser negativo se as hipóteses favorecerem as apostas. Ele não é apresentado como necessariamente positivo, nem como recomendação. O investimento é determinístico sob a taxa hipotética; sua volatilidade não é modelada. Todos os valores são nominais, sem impostos, custos, inflação ou risco de crédito.

## Monte Carlo e memória

Cada trajetória representa apostas Bernoulli independentes. Até 240 intervalos de exibição são criados. Para cada intervalo com ΔN apostas, sorteia-se Binomial(ΔN,p) para cada trajetória. A distribuição é **exatamente equivalente** à soma das Bernoulli sob as hipóteses constantes; não se usa aproximação normal. Quando há no máximo 240 apostas, cada incremento é uma Bernoulli. Nos casos maiores, eventos individuais dentro dos intervalos não são armazenados nem exibidos.

Mantêm-se contagens de vitória por trajetória, 12 trajetórias de exemplo e estatísticas pontuais. Complexidade de memória O(M + 12J), em vez de O(MN); tempo aproximadamente O(MJ), acrescido do cálculo de quantis, com J≤240. As mesmas trajetórias originam média, percentis e distribuição final. Não há sorteios independentes entre o gráfico e a tabela.

O gráfico mostra seis das 12 trajetórias exportadas. A faixa P5–P95 é pontual; ela não garante cobertura de 90% de percursos inteiros. Quantis empíricos usam interpolação linear (`numpy.quantile`). O desvio-padrão é amostral (`ddof=1`). Erro-padrão da média = desvio-padrão amostral/√M. Mais sorteios reduzem erro Monte Carlo, não incerteza das hipóteses.

A semente efetivamente usada é retornada. Uma semente ausente gera uma semente aleatória de 32 bits. A mesma semente, parâmetros, versões de biblioteca e implementação reproduzem os resultados; não se promete igualdade entre versões do NumPy. O arquivo lock registra o ambiente validado.

## Interface e cenários

Cinco visualizações obrigatórias: evolução e faixa pontual; histograma final com média/mediana/equilíbrio/P5/P95; uma trajetória versus expectativa; patrimônios de apostas e investimento; sensibilidade. Adicionalmente, há gráfico de comparação de cenários.

Os cenários editáveis usam probabilidade diretamente informada, frequência semanal e horizonte anual, explicitados acima da tabela. Os resultados são analíticos/binomiais exatos. ROI oferece comparação normalizada quando os orçamentos diferem. A sensibilidade mantém as outras hipóteses constantes: ao variar odd com margem fixa, p é recalculada, mantendo ROI=−h; ao variar p, o método passa a probabilidade informada.

Linhas, nomes, tracejados e tabelas complementam as cores. A barra lateral pode ser recolhida em telas pequenas. As tabelas extensas permitem rolagem horizontal.

## Contrato do assistente

`simulate(parameters: dict, include_distribution: bool = False) -> dict` aceita as chaves de `Parameters`. Taxas em fração: 0.08 significa 8%. Os valores em reais não recebem símbolo dentro do JSON.

| Campo de saída | Conteúdo |
|---|---|
| schema_version, currency | Versão 1.0 e BRL |
| parameters, seed_used | Hipóteses recebidas e semente efetiva |
| theoretical | N, p, ROI, esperança, variância, probabilidades exatas, orçamento, patrimônios e custo de oportunidade |
| simulation | Média, mediana, desvio-padrão, P5/P95, probabilidades empíricas e erro-padrão |
| timeline | Número de apostas, anos, orçamento, média, faixas, percursos, investimento e valor esperado |
| explanations, assumptions | Explicações por regras e premissas explícitas |
| final_profit, final_betting_wealth | Vetores opcionais de tamanho M |

O assistente deve usar esses campos como fonte dos números, mencionar hipóteses e separar valores simulados de teóricos. Para “quanto posso perder?”, relatar percentis e possibilidade de resultados externos à faixa, sem apresentá-los como limites. O pior resultado possível neste modelo é −Ns e não inclui endividamento adicional. Para dobrar frequência, executar outro cenário; não inventar probabilidades. Uma pergunta sem odd ou p/h requer premissas explícitas.

Não há IA generativa ativa. Uma integração futura poderá envolver esta função como ferramenta e guardar credenciais em variáveis de ambiente. Nenhuma credencial é necessária ao funcionamento atual. Erros de validação são `ValueError`; não há endpoint HTTP nesta entrega.

## Limitações acadêmicas

O workbook e a base bibliográfica do curso não foram recebidos. As referências adicionais estão identificadas em `REFERENCIAS.md`, sem atribuí-las ao material da disciplina. Não se infere a vantagem real de uma casa de apostas a partir de uma odd isolada. Esportes reais podem ter dependência, alterações de chance, apostas canceladas, empates e comportamentos adaptativos; essas situações exigem outro modelo.
