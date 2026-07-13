"""Camada de IA: chama a API do Groq via REST e devolve a resposta como dict."""

import os
import json
import requests
from dotenv import load_dotenv

from prompt import montar_prompt

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    raise RuntimeError("GROQ_API_KEY não encontrada. Crie o arquivo .env na raiz do projeto.")

URL = "https://api.groq.com/openai/v1/chat/completions"
MODELO = "llama-3.3-70b-versatile"


def classificar_mensagem(assunto: str, mensagem: str) -> dict:
    """Envia a mensagem para o LLM e retorna o JSON de classificação como dict."""
    prompt = montar_prompt(assunto, mensagem)

    payload = {
        "model": MODELO,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
    }

    resposta = requests.post(
        URL,
        headers={"Authorization": f"Bearer {API_KEY}"},
        json=payload,
        timeout=30,
    )
    resposta.raise_for_status()

    texto = resposta.json()["choices"][0]["message"]["content"]
    return json.loads(texto)

def classificar_com_seguranca(assunto: str, mensagem: str, max_tentativas: int = 2) -> dict:
    """Classifica com retry e fallback. Nunca levanta exceção — sempre retorna um dict."""
    from validador import validar_saida

    ultima_falha = ""

    for tentativa in range(1, max_tentativas + 1):
        try:
            resultado = classificar_mensagem(assunto, mensagem)
            erros = validar_saida(resultado)
            if not erros:
                return resultado
            ultima_falha = f"saída inválida: {'; '.join(erros)}"
            print(f"  [tentativa {tentativa}] {ultima_falha}")
        except requests.exceptions.Timeout:
            ultima_falha = "timeout na chamada da API"
            print(f"  [tentativa {tentativa}] {ultima_falha}")
        except requests.exceptions.HTTPError as e:
            ultima_falha = f"erro HTTP da API: {e.response.status_code}"
            print(f"  [tentativa {tentativa}] {ultima_falha}")
        except (json.JSONDecodeError, KeyError) as e:
            ultima_falha = f"resposta da IA em formato inesperado: {e}"
            print(f"  [tentativa {tentativa}] {ultima_falha}")

    # Fallback: nunca deixamos o pipeline quebrar por causa de UMA mensagem
    return {
        "tipo_solicitacao": "pendencia_de_informacao",
        "empresa": None,
        "cnpj": None,
        "documentos_identificados": [],
        "data_mencionada": None,
        "urgencia": False,
        "area_sugerida": "N/A",
        "proxima_acao": "enviar para analise manual",
        "confianca": "baixo",
        "justificativa": f"Classificação automática falhou ({ultima_falha}). Requer análise manual.",
        "erro_processamento": True,
    }