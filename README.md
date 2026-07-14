# Triagem de Mensagens com IA — POC

Assistente de triagem automática para mensagens de clientes de uma empresa do mercado financeiro. Recebe textos livres, classifica o tipo de solicitação, extrai informações relevantes (empresa, CNPJ, documentos, datas, urgência) e sugere a próxima ação — tudo em JSON estruturado e validado.

## Como funciona

```
mensagem → prompt com regras fixas → LLM (Groq / Llama 3.3 70B) → JSON → validação → retry/fallback → resultado
```

A solução separa **regras fixas** (categorias permitidas, validação, fallback — código) de **decisão da IA** (interpretar o texto e escolher dentro das categorias — LLM). Se a IA devolver algo fora das regras, o sistema tenta novamente e, persistindo o erro, encaminha para análise manual — o pipeline nunca quebra por causa de uma mensagem.

## Estrutura

```
├── dados/
│   ├── exemplos_entrada.json   # 8 mensagens (5 do desafio + 3 casos de borda)
│   └── gabarito.json           # classificação esperada, para medir acurácia
├── src/
│   ├── prompt.py               # prompt e categorias permitidas (fonte única de verdade)
│   ├── classificador.py        # chamada ao LLM + retry + fallback
│   ├── validador.py            # validação da saída da IA
│   ├── main.py                 # pipeline em lote
│   ├── avaliador.py            # compara saída vs. gabarito (acurácia)
│   └── api.py                  # API REST (FastAPI)
├── testes/                     # testes automatizados (pytest)
└── resultados/saida.json       # saída gerada
```

## Como rodar

Pré-requisitos: Python 3.11+ e uma chave gratuita da API do Groq (https://console.groq.com/keys).

```bash
# 1. Instalar dependências
python -m venv venv
source venv/Scripts/activate        # Windows Git Bash (ou venv\Scripts\activate no PowerShell)
pip install -r requirements.txt

# 2. Configurar a chave (criar arquivo .env na raiz)
echo "GROQ_API_KEY=sua_chave_aqui" > .env

# 3. Processar as mensagens de exemplo
python src/main.py

# 4. Medir a qualidade da classificação
python src/avaliador.py

# 5. Rodar os testes
pytest testes/ -v

# 6. Subir a API REST (documentação interativa em http://127.0.0.1:8000/docs)
uvicorn api:app --app-dir src --reload
```

## Como a IA foi usada

- **Modelo:** Llama 3.3 70B via API do Groq (REST, padrão OpenAI-compatible), temperatura 0.1 para maximizar consistência em tarefa de classificação.
- **Papel da IA:** interpretar o texto livre e classificá-lo **dentro de categorias fixas** definidas no código. A IA não inventa categorias: o prompt lista os valores permitidos e o validador rejeita qualquer coisa fora deles.
- **Modo JSON:** a API é chamada com `response_format: json_object`, forçando saída em JSON válido.
- **Calibração:** o prompt inclui regras para casos ambíguos e um exemplo de mensagem vaga (few-shot), após testes mostrarem que o modelo "chutava" classificações com confiança alta em mensagens sem conteúdo.
- Também usei IA generativa (Claude) como apoio no desenvolvimento, revisando cada decisão e mantendo o entendimento completo do código.

## Qualidade e limitações encontradas

Medida com `avaliador.py` contra um gabarito definido manualmente:

- Acurácia do tipo de solicitação: <<X/8 (XX%)>>
- Acurácia do nível de confiança: <<X/8 (XX%)>>

Limitações identificadas nos casos de borda:

- **Mensagens híbridas** (caso 7: envio de documento + interesse em crédito): o modelo classifica o assunto principal corretamente, mas nem sempre reduz a confiança para "medio" como instruído.
- **Ambiguidade de negócio** (caso 6): mensagens sobre boleto não recebido podem ser lidas como "segunda via" ou "dúvida sobre operação" — o gabarito registra a decisão de negócio adotada.

## O que eu melhoraria em uma versão real

- **Fila assíncrona** (ex: mensagens chegando por e-mail → fila → workers), em vez de processamento síncrono.
- **Gabarito maior e monitoramento contínuo:** medir acurácia sobre centenas de casos reais rotulados, com alertas de degradação.
- **Feedback humano no loop:** triagens de confiança "baixo"/"medio" revisadas por pessoas, e as correções alimentam novos exemplos no prompt (ou fine-tuning).
- **Extração de CNPJ por regex** como dupla checagem da IA (regra fixa é mais confiável para padrões determinísticos).
- **Logs estruturados e persistência** (banco de dados) em vez de arquivo JSON.
- **Autenticação na API** e rate limiting.
- **Docker** para padronizar o ambiente de execução.