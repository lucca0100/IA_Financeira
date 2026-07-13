"""Pipeline de triagem: lê mensagens, classifica com IA e salva resultados em JSON."""

import json
import sys
import time
from pathlib import Path

from classificador import classificar_com_seguranca

ARQUIVO_ENTRADA = Path("dados/exemplos_entrada.json")
ARQUIVO_SAIDA = Path("resultados/saida.json")


def carregar_mensagens(caminho: Path) -> list[dict]:
    if not caminho.exists():
        print(f"ERRO: arquivo de entrada não encontrado: {caminho}")
        sys.exit(1)
    try:
        with open(caminho, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERRO: arquivo de entrada não é um JSON válido: {e}")
        sys.exit(1)


def main():
    mensagens = carregar_mensagens(ARQUIVO_ENTRADA)
    print(f"Iniciando triagem de {len(mensagens)} mensagens...\n")

    resultados = []
    inicio = time.time()

    for msg in mensagens:
        print(f"[{msg['id']}] Processando: {msg['assunto']}")
        classificacao = classificar_com_seguranca(msg["assunto"], msg["mensagem"])
        resultados.append({"id": msg["id"], **classificacao})
        print(f"     -> {classificacao['tipo_solicitacao']} (confianca: {classificacao['confianca']})")

    ARQUIVO_SAIDA.parent.mkdir(exist_ok=True)
    with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)

    duracao = time.time() - inicio
    com_erro = sum(1 for r in resultados if r.get("erro_processamento"))
    print(f"\nConcluído em {duracao:.1f}s")
    print(f"Processadas: {len(resultados)} | Falhas (análise manual): {com_erro}")
    print(f"Resultados salvos em: {ARQUIVO_SAIDA}")


if __name__ == "__main__":
    main()