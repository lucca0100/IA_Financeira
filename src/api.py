"""API REST de triagem de mensagens."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from classificador import classificar_com_seguranca

app = FastAPI(
    title="API de Triagem com IA",
    description="Classifica mensagens de clientes do mercado financeiro usando LLM.",
    version="1.0.0",
)


class MensagemEntrada(BaseModel):
    assunto: str = Field(..., min_length=1, examples=["Interesse em crédito"])
    mensagem: str = Field(..., min_length=1, examples=["Olá, somos da Alfa Comércio LTDA e queremos crédito para capital de giro."])


@app.get("/")
def raiz():
    return {"status": "ok", "docs": "/docs"}


@app.post("/triagem")
def triagem(entrada: MensagemEntrada):
    try:
        return classificar_com_seguranca(entrada.assunto, entrada.mensagem)
    except Exception as e:
        # classificar_com_seguranca já tem fallback; isso aqui é a última barreira
        raise HTTPException(status_code=500, detail=f"Erro interno na triagem: {e}")