"""Compara a saída da IA com o gabarito e calcula métricas simples."""

import json
from pathlib import Path

ARQUIVO_SAIDA = Path("resultados/saida.json")
ARQUIVO_GABARITO = Path("dados/gabarito.json")


def main():
    with open(ARQUIVO_SAIDA, encoding="utf-8") as f:
        resultados = {r["id"]: r for r in json.load(f)}
    with open(ARQUIVO_GABARITO, encoding="utf-8") as f:
        gabarito = json.load(f)

    acertos_tipo = 0
    acertos_confianca = 0

    print(f"{'ID':<4}{'Esperado':<32}{'Obtido':<32}{'Tipo':<7}{'Confiança'}")
    print("-" * 85)

    for item in gabarito:
        r = resultados.get(item["id"])
        if r is None:
            print(f"{item['id']:<4}{'—':<32}{'SEM RESULTADO':<32}")
            continue

        tipo_ok = r["tipo_solicitacao"] == item["tipo_solicitacao"]
        conf_ok = r["confianca"] == item["confianca_esperada"]
        acertos_tipo += tipo_ok
        acertos_confianca += conf_ok

        if conf_ok:
            status_conf = "OK"
        else:
            status_conf = f"ERRO (esperado {item['confianca_esperada']}, veio {r['confianca']})"

        print(
            f"{item['id']:<4}"
            f"{item['tipo_solicitacao']:<32}"
            f"{r['tipo_solicitacao']:<32}"
            f"{'OK' if tipo_ok else 'ERRO':<7}"
            f"{status_conf}"
        )

    total = len(gabarito)
    print("-" * 85)
    print(f"Acurácia do tipo:      {acertos_tipo}/{total} ({100 * acertos_tipo / total:.0f}%)")
    print(f"Acurácia da confiança: {acertos_confianca}/{total} ({100 * acertos_confianca / total:.0f}%)")


if __name__ == "__main__":
    main()