# BetWise Web

Assistente educacional em português com respostas fundamentadas na biblioteca e calculadora de exposição financeira. Versão web derivada da V13 local. Não utiliza Ollama, Chroma ou caminhos do computador do autor.

## Publicação

No Streamlit Community Cloud, selecione este repositório, branch `main`, arquivo `app.py` e Python 3.13. Configure `GEMINI_API_KEY` exclusivamente em **Advanced settings → Secrets**. Campos adicionais estão em `secrets.example.toml`.

O repositório deve permanecer privado: `corpus.json` contém os trechos da biblioteca usados internamente para recuperação. Não há PDFs integrais nem chaves no pacote. O aplicativo pode ser compartilhado publicamente separadamente do código. A hospedagem deve ter acesso ao repositório privado.

## Arquitetura

- Gemini Embedding `gemini-embedding-001`, 768 dimensões: documentos com `RETRIEVAL_DOCUMENT` e perguntas com `RETRIEVAL_QUERY`.
- Matriz vetorial normalizada em `vectors.npz`, metadados em `index_meta.json`, biblioteca em `corpus.json`.
- Busca global/temática e reordenação preservadas da aplicação local; até quatro trechos por resposta.
- Gemini `gemini-3.1-flash-lite` para geração. Modelo configurável nos secrets.
- Histórico em sessão; não é gravado no repositório. Perguntas e trechos selecionados são enviados ao Google Gemini.

## Limites da demonstração

Padrões: 3 tentativas por minuto no aplicativo, 15 por dia e 5 por sessão/dia. A pergunta tem até 1.500 caracteres. Falhas também consomem tentativas para proteger a API. Os limites são conservadores e não representam a cota contratada com Google.

O controle global usa SQLite temporário na instância da hospedagem e é atômico entre sessões. A plataforma pode apagar esse armazenamento em reinicializações/reimplantações; os limites por sessão não identificam uma pessoa entre navegadores. Não são proteção robusta contra abuso nem teto financeiro garantido. Para divulgação ampla, usar autenticação, contador externo persistente e limites de orçamento no provedor.

## Execução local

Instale `requirements.txt`, configure `GEMINI_API_KEY` e execute `python -m streamlit run app.py`. Não é necessário reindexar ao iniciar. Ao mudar o modelo de embeddings, gere novamente toda a matriz; não misture vetores de Qwen3 e Gemini.

## Escopo

## Fontes regulatórias (consulta em 09/10/2026)

A biblioteca contém o texto da MP 1.394/2026 do Planalto e a notícia de 25/09/2026 do Ministério da Saúde. Os textos capturados e os registros de indexação estão em `sources/`, com URLs, natureza da fonte, data e localização. Total: 374 trechos, incluindo 43 novos trechos. O índice Gemini preserva os 331 vetores anteriores.

Textos regulatórios anteriores recebem indicação de referência histórica. O contexto entregue ao assistente distingue norma e notícia, projeto de lei criminal e MP, além dos diferentes prazos de transição. A consulta não monitora alterações legislativas automaticamente; respostas sobre vigência devem informar a data da base. Os arquivos preservam o conteúdo das fontes, inclusive eventuais divergências, sem corrigir silenciosamente seus números.

O simulador desta publicação mantém a calculadora da V13: volume apostado e probabilidade implícita. Não incorpora a ramificação separada com Monte Carlo. A finalidade é educacional, sem recomendação de apostas ou promessa de retorno.
