# Matriz de aderência

**Base verificada:** texto “PROMPT — DESENVOLVIMENTO DE SIMULADOR FINANCEIRO DE APOSTAS ESPORTIVAS” recebido nesta conversa. **Workbook:** não recebido. Assim, “atendido” significa implementado contra o texto, não aprovação de critérios acadêmicos não fornecidos.

| Seção do texto | Requisito | Entrega / evidência |
|---|---|---|
| 1 | Aplicação funcional educativa | `app.py`; motor independente; testes executáveis |
| 1, 15 | Leitura e critérios do workbook | Pendente: documento não recebido; sem critérios inventados |
| 2 | Python, Streamlit, NumPy, SciPy, Pandas, Plotly, Pytest | Dependências, módulos e suíte de testes |
| 2 | Navegador, gratuito, sem cadastro | Aplicação local sem autenticação; instruções para hospedagem pública gratuita |
| 3 | Português, reais, navegação e controles | Barra lateral, cinco áreas, formatação pt-BR, layouts responsivos |
| 4 | Todos os parâmetros e dois métodos | `Parameters`, controles laterais, validação e seed efetiva |
| 5 | Esperança, variância, ROI e chance implícita | `theoretical`, fórmulas na interface e documentação |
| 5 | Overround opcional | Calculadora em “Entenda”, sem confundi-lo com h |
| 6 | Monte Carlo, trajetórias e binomial | Incrementos binomiais exatos de Bernoulli, amostra de trajetórias, referência SciPy |
| 6 | Memória e reprodução | Agregação em até 240 intervalos, RNG local, seed e lock |
| 7 | Cinco gráficos obrigatórios | `charts.py`; testes de coerência com as séries do motor |
| 7 | Total, resultado, prejuízo e oportunidade | Quatro indicadores permanentes |
| 8 | Mesmos aportes e datas | Função de valor futuro, conta sem rendimento para pagamentos, testes de soma direta |
| 8 | Patrimônio versus lucro | Tabela dedicada, distribuição de patrimônio em CSV e percentis no gráfico |
| 9 | Três ou mais cenários editáveis | Editor dinâmico, redefinição, gráfico, tabela, CSV e ROI normalizado |
| 10 | Conceitos e oito vieses | Painel educativo contextualizado; referências adicionais identificadas |
| 11 | Função central JSON para assistente | `simulate`; nenhum modelo generativo fictício |
| 12 | Validação matemática e funcional | `tests/test_model.py` e `tests/test_ui.py` |
| 12 | Sem ruína em modelo sem banca | Nenhuma métrica de ruína é calculada; limitação explícita |
| 13 | Transparência e apoio | Nota permanente, metodologia detalhada e fontes oficiais |
| 14 | Código, dependências, README e documentação | Pasta completa e arquivo ZIP de entrega |
| 14 | Publicação gratuita | Passo a passo no README; publicação efetiva não realizada |
| 15–16 | Execução e verificações | Resultados registrados em `VALIDACAO.md` |

## Melhorias adicionais implementadas

Empate separado de lucro/prejuízo; erro-padrão de Monte Carlo; comparação com probabilidades binomiais exatas; exportações JSON/CSV; semente aleatória registrada; taxas alternativas negativas; overround opcional; limites de processamento; matriz de aderência e contrato de integração.

## Fora do escopo ou pendente

Não há banca inicial, ruína, estratégia de aposta, odds ao vivo, previsão esportiva, login, coleta de renda, IA generativa ou conexão com uma casa de apostas. Nenhum desses recursos é necessário ao modelo base pedido. A integração com um assistente existente e a aderência à bibliografia do curso dependem dos materiais não fornecidos.
