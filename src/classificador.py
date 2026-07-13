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