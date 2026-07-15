# Triagem de Mensagens com IA — POC

Assistente de triagem automática para mensagens de clientes de uma empresa do mercado financeiro. Recebe textos livres, classifica o tipo de solicitação, extrai informações relevantes (empresa, CNPJ, documentos, datas, urgência) e sugere a próxima ação — tudo em JSON estruturado e validado.

Desenvolvido como parte do desafio técnico para a posição de Trainee de Tecnologia.

## Como funciona

```
mensagem → prompt com regras fixas → LLM (Groq / Llama 3.3 70B) → JSON → validação → retry/fallback → resultado
```

A decisão central da arquitetura é a **separação entre regra fixa e decisão da IA**:

- **Regra fixa (código):** as categorias permitidas, os campos obrigatórios, a validação da saída e o comportamento em caso de falha são definidos e garantidos por código determinístico e testável (`prompt.py` + `validador.py`).
- **Decisão da IA (LLM):** interpretar o texto livre e classificá-lo **dentro** das categorias permitidas, extrair entidades e atribuir confiança com justificativa.

Se a IA devolver algo fora das regras (categoria inventada, campo ausente, tipo errado), o sistema rejeita, tenta novamente e, persistindo o erro, encaminha a mensagem para **análise manual** — o pipeline nunca quebra por causa de uma mensagem.

## Estrutura do projeto

```
├── dados/
│   ├── exemplos_entrada.json   # 8 mensagens (5 do desafio + 3 casos de borda propositais)
│   └── gabarito.json           # classificação esperada, para medir acurácia
├── src/
│   ├── prompt.py               # prompt e categorias permitidas (fonte única de verdade)
│   ├── classificador.py        # chamada ao LLM via REST + retry + fallback
│   ├── validador.py            # validação da saída da IA contra as regras fixas
│   ├── main.py                 # pipeline em lote com logs de execução
│   ├── avaliador.py            # compara saída vs. gabarito e calcula acurácia
│   └── api.py                  # API REST (FastAPI) com documentação Swagger
├── testes/
│   ├── test_validador.py       # testes das regras de validação
│   └── test_prompt.py          # testes da montagem do prompt
├── resultados/
│   └── saida.json              # saída estruturada gerada pelo pipeline
├── requirements.txt
└── README.md
```

## Como rodar

Pré-requisitos: **Python 3.11+** e uma chave gratuita da API do Groq (https://console.groq.com/keys — não exige cartão).

```bash
# 1. Instalar dependências
cd triagem-ia
python -m venv venv
source venv/Scripts/activate        # Windows Git Bash (PowerShell: venv\Scripts\activate | Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt

# 2. Configurar a chave da API (criar arquivo .env na raiz)
echo "GROQ_API_KEY=sua_chave_aqui" > .env

# 3. Processar as mensagens de exemplo (gera resultados/saida.json)
python src/main.py

# 4. Medir a qualidade da classificação contra o gabarito
python src/avaliador.py

# 5. Rodar os testes automatizados
pytest testes/ -v

# 6. Subir a API REST
uvicorn api:app --app-dir src --reload
# Documentação interativa: http://127.0.0.1:8000/docs
```

## Como a IA foi usada

- **Modelo:** Llama 3.3 70B via API do Groq, chamado por REST puro (`requests`) no formato OpenAI-compatible — o que torna o código portável para outros provedores com mudanças mínimas.
- **Temperatura 0.1:** classificação pede consistência, não criatividade; a mesma mensagem deve gerar a mesma classificação.
- **Modo JSON** (`response_format: json_object`): força a saída a ser JSON sintaticamente válido. Ainda assim, todo retorno passa pelo validador — JSON válido não significa conteúdo dentro das regras.
- **Papel restrito:** a IA nunca inventa categorias. O prompt lista os valores permitidos e o validador rejeita qualquer coisa fora deles, disparando retry e, em último caso, fallback para análise manual.
- **Calibração com casos de borda (few-shot):** os testes revelaram que o modelo "chutava" classificações com confiança média em mensagens vagas. O prompt foi ajustado com uma regra mais dura e um exemplo concreto de mensagem vaga, corrigindo o comportamento.
- **Nota de transparência:** também usei IA generativa (Claude) como apoio no desenvolvimento do projeto, revisando cada decisão tomada e mantendo entendimento completo do código entregue.

## Tratamento de erros

- **Entrada:** arquivo inexistente ou JSON malformado geram mensagem clara e encerramento controlado.
- **Chamada à API:** timeout de 30s, tratamento específico de erros HTTP e de parsing (exceções específicas, sem `except` genérico).
- **Saída da IA:** validação de campos obrigatórios, categorias permitidas e tipos de dados; saída inválida dispara retry (até 2 tentativas).
- **Fallback:** se tudo falhar, a mensagem é marcada com `erro_processamento: true` e encaminhada para análise manual — o lote continua.
- **API REST:** entrada validada automaticamente via Pydantic (HTTP 422 com explicação para requisições malformadas).

## Qualidade e limitações encontradas

A qualidade é medida pelo `avaliador.py`, que compara a saída da IA com um gabarito rotulado manualmente (`dados/gabarito.json`):

- Acurácia do tipo de solicitação: **X/8 (XX%)** ← preencher com o resultado do avaliador
- Acurácia do nível de confiança: **X/8 (XX%)** ← preencher com o resultado do avaliador

Além dos 5 exemplos do enunciado, foram criados 3 casos de borda propositais para estressar a solução. Limitações identificadas e documentadas:

- **Mensagens híbridas** (caso 7: envio de documento + interesse em crédito na mesma mensagem): o modelo classifica o assunto principal corretamente, mas nem sempre reduz a confiança para "medio" como instruído no prompt.
- **Ambiguidade de negócio** (caso 6: boleto não recebido que vence hoje): a mensagem admite leitura como "segunda via" ou "dúvida sobre operação". O gabarito registra a decisão de negócio adotada (segunda via — o pedido central é receber o boleto novamente).
- **Mensagens vagas** (caso 8): após calibração do prompt, o sistema retorna corretamente confiança "baixo" e "solicitar informacoes complementares" em vez de adivinhar.

## O que eu melhoraria em uma versão real

- **Fila assíncrona** (mensagens → fila → workers) em vez de processamento síncrono, para escalar volume.
- **Gabarito maior e medição contínua:** centenas de casos reais rotulados, com alertas de degradação de acurácia (ex.: quando o provedor atualiza o modelo).
- **Feedback humano no loop:** triagens de confiança "baixo"/"medio" revisadas por pessoas, e as correções realimentando os exemplos do prompt (ou fine-tuning).
- **Regex como dupla checagem** para CNPJ e datas — padrões determinísticos são território de regra fixa, não de IA.
- **Persistência em banco de dados** e logs estruturados em vez de arquivos JSON.
- **Autenticação e rate limiting** na API.
- **Docker** para padronizar o ambiente de execução.
- **Análise de custo por mensagem**, testando modelos menores contra o gabarito — talvez um modelo mais barato entregue a mesma acurácia.