# Validação da integração — 11/10/2026

Base do repositório: `9074a68f19224c9f0f871b156d83e8f8a4a16de7`. A branch `main` foi consultada novamente em 11/10/2026 e permanecia nessa revisão.

**41 testes aprovados em 28,91 segundos.** Ambiente isolado com Python 3.12.14 e as dependências exatas de `requirements.txt`: Streamlit 1.63.0, Google GenAI 2.23.0, NumPy 2.2.6, SciPy 1.15.3, Pandas 2.2.3 e Plotly 6.1.2. A hospedagem original recomenda Python 3.13; esta execução local utilizou 3.12.

## Verificações de escopo

- Todo o trecho do `app.py` anterior ao bloco do simulador foi preservado byte a byte, incluindo o chat e seus estilos.
- `cloud_backend.py`, biblioteca, índice, vetores, fontes, exemplo de secrets, `.gitignore` e `.streamlit/config.toml` permanecem idênticos ao original, verificados por SHA-256.
- Apenas `app.py`, o parágrafo do README sobre o simulador e `requirements.txt` foram modificados entre os arquivos existentes.
- O patch textual foi verificado com `git apply --check` contra a cópia original, sem erros.

## Verificações funcionais

- A tela inicial continua sendo o assistente, com o mesmo conteúdo renderizado após uma ida e volta pela aba Simulador.
- Todas as cinco áreas do novo simulador renderizam sem exceção.
- Parâmetros alterados sobrevivem à navegação pelo assistente.
- Redefinir parâmetros não remove mensagens nem avisos do agente.
- Uma entrada inválida exibe erro no simulador sem impedir a navegação para o assistente.
- Nenhuma pergunta foi enviada ao Gemini. Não houve consumo de quota de IA durante os testes.

## Verificações matemáticas

Os 37 casos do motor cobrem p=0/1, aposta justa, desvantagem de 5%, média e variância Monte Carlo, sementes, juros compostos e datas, entradas inválidas, extremos, empate com odd decimal, coerência entre gráficos e resultados, cenários e overround. O relatório da versão independente em `VALIDACAO.md` é histórico; os resultados acima são os da integração.
