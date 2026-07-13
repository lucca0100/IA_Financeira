"""Prompt de classificação — regras fixas do negócio ficam aqui."""

# Regras fixas: categorias permitidas (a IA escolhe DENTRO delas)
TIPOS_SOLICITACAO = [
    "interesse_em_credito_pj",
    "atualizacao_cadastral",
    "envio_de_documentacao",
    "solicitacao_de_segunda_via",
    "duvida_sobre_operacao_financeira",
    "pendencia_de_informacao",
    "fora_do_escopo",
]

AREAS = ["Comercial", "Cadastro", "Operacoes", "Analise de Credito", "Atendimento", "N/A"]

PROXIMAS_ACOES = [
    "encaminhar para contato comercial",
    "encaminhar para operacoes",
    "encaminhar para cadastro",
    "solicitar informacoes complementares",
    "registrar pendencia",
    "enviar para analise manual",
    "marcar como fora do escopo",
]

NIVEIS_CONFIANCA = ["alto", "medio", "baixo"]


def montar_prompt(assunto: str, mensagem: str) -> str:
    return f"""Você é um assistente de triagem de mensagens de uma empresa do mercado financeiro.
Analise a mensagem abaixo e retorne APENAS um objeto JSON válido, sem markdown, sem texto extra.

MENSAGEM A ANALISAR:
Assunto: {assunto}
Mensagem: {mensagem}

FORMATO DE SAÍDA (obrigatório):
{{
  "tipo_solicitacao": "<um valor de: {", ".join(TIPOS_SOLICITACAO)}>",
  "empresa": "<nome da empresa citada ou null>",
  "cnpj": "<CNPJ no formato XX.XXX.XXX/XXXX-XX ou null>",
  "documentos_identificados": ["<documentos citados no texto>"],
  "data_mencionada": "<data citada ou null>",
  "urgencia": <true ou false>,
  "area_sugerida": "<um valor de: {", ".join(AREAS)}>",
  "proxima_acao": "<um valor de: {", ".join(PROXIMAS_ACOES)}>",
  "confianca": "<um valor de: {", ".join(NIVEIS_CONFIANCA)}>",
  "justificativa": "<1 ou 2 frases explicando a decisão>"
}}

REGRAS:
1. Use SOMENTE os valores listados para tipo_solicitacao, area_sugerida, proxima_acao e confianca.
2. Extraia dados APENAS se estiverem no texto. Nunca invente empresa, CNPJ ou data.
3. Se a mensagem tratar de mais de um assunto, classifique pelo assunto principal e use confianca "medio".
4. Se a mensagem for vaga ou não der para classificar com segurança, use confianca "baixo" e proxima_acao "solicitar informacoes complementares".
5. Se o assunto não tiver relação com serviços financeiros, use "fora_do_escopo" e area_sugerida "N/A".
6. urgencia é true apenas se houver indicação clara de prazo curto ou pedido urgente."""