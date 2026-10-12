# Integração do novo simulador ao BetWise Web

Base: `GuilhermeRorato-rgb/betwise-web`, branch `main`, commit `9074a68f19224c9f0f871b156d83e8f8a4a16de7` observado em 09/10/2026.

## Escopo da alteração

- `app.py`: apenas o bloco `elif pagina == "Simulador"` foi substituído por importação e chamada de `mostrar_simulador()`. Todo o conteúdo anterior permanece idêntico byte a byte.
- `interface_simulador.py` e `simulator/`: novo painel e motor independente, com cálculos, gráficos e conteúdo educativo.
- `requirements.txt`: versões originais de Streamlit, Google GenAI e NumPy preservadas. Adicionados SciPy 1.15.3, Pandas 2.2.3 e Plotly 6.1.2, compatíveis com a versão de Python 3.13 indicada pelo projeto.
- `README.md`: apenas o parágrafo que descrevia o simulador antigo foi atualizado.
- `tests/`, `pytest.ini`, `requirements-dev.txt` e `docs/simulador/`: testes e documentação da integração.

`cloud_backend.py`, `corpus.json`, `vectors.npz`, `index_meta.json`, fontes, secrets de exemplo e configuração Streamlit foram preservados integralmente. O teste de integridade usa hashes SHA-256 do original. As instruções, modelos, quotas, recuperação, geração e conteúdo visual do chat não foram alterados.

## Interface

O usuário abre a aba **Simulador** na mesma barra de navegação. O cabeçalho e o chat continuam sendo os do projeto. O painel usa os mesmos cálculos e gráficos da versão Monte Carlo aprovada. **Configurar cenário** expande os controles em três colunas, que se adaptam a telas menores. Não há segunda barra de navegação principal nem aplicativo separado.

As regras CSS novas só alcançam `.st-key-simulator_workspace`. Elas não alteram o chat nem sua navegação. Os parâmetros usam prefixo exclusivo `bw_sim_input_` e são preservados ao alternar de aba. Redefinir o simulador não apaga mensagens, avisos nem quotas do assistente.

O motor JSON continua disponível por `from simulator import simulate`. Esta substituição não injeta resultados no prompt do Gemini nem altera o backend do agente; essa conexão adicional seria uma alteração do agente e ficou fora do pedido de substituir apenas o simulador.

## Instalação e publicação

Mantenha o ponto de entrada `app.py`, os secrets existentes e a configuração atual da hospedagem. Atualize o código e instale as dependências:

```text
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Para os testes:

```text
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

O arquivo `betwise-web-atualizado.zip` contém a árvore completa, incluindo os dados originais preservados. O arquivo `somente-alteracoes-simulador.zip` contém apenas os arquivos novos/modificados. Não é necessário substituir a base vetorial ou reindexar. `substituir-simulador.patch` registra a diferença textual contra a base observada; se o repositório avançar, revise conflitos antes de aplicá-lo.

## Validação

Testes de navegação Assistente → Simulador → Assistente; reprodução da tela original do agente; persistência de parâmetros; preservação de mensagens e avisos ao redefinir; entradas inválidas sem impedir acesso ao chat; integridade dos arquivos originais; e testes matemáticos do motor Monte Carlo.

O teste da interface não envia perguntas nem consome chamadas do Gemini. A geração de respostas externas exige os secrets originais e não faz parte da verificação da troca do simulador.

As convenções de probabilidade, juros e datas estão em `TECNICA.md`. O relatório `VALIDACAO.md` descreve a versão independente anterior; os resultados desta integração são registrados em `VALIDACAO-INTEGRACAO.md`.
