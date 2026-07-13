"""Validação da saída da IA — garante que o JSON respeita as regras fixas."""

from prompt import TIPOS_SOLICITACAO, AREAS, PROXIMAS_ACOES, NIVEIS_CONFIANCA

CAMPOS_OBRIGATORIOS = [
    "tipo_solicitacao",
    "empresa",
    "cnpj",
    "documentos_identificados",
    "data_mencionada",
    "urgencia",
    "area_sugerida",
    "proxima_acao",
    "confianca",
    "justificativa",
]


def validar_saida(resultado: dict) -> list[str]:
    """Retorna uma lista de erros encontrados. Lista vazia = saída válida."""
    erros = []

    for campo in CAMPOS_OBRIGATORIOS:
        if campo not in resultado:
            erros.append(f"campo obrigatório ausente: {campo}")

    # Se faltam campos, nem adianta validar os valores
    if erros:
        return erros

    if resultado["tipo_solicitacao"] not in TIPOS_SOLICITACAO:
        erros.append(f"tipo_solicitacao inválido: {resultado['tipo_solicitacao']}")

    if resultado["area_sugerida"] not in AREAS:
        erros.append(f"area_sugerida inválida: {resultado['area_sugerida']}")

    if resultado["proxima_acao"] not in PROXIMAS_ACOES:
        erros.append(f"proxima_acao inválida: {resultado['proxima_acao']}")

    if resultado["confianca"] not in NIVEIS_CONFIANCA:
        erros.append(f"confianca inválida: {resultado['confianca']}")

    if not isinstance(resultado["documentos_identificados"], list):
        erros.append("documentos_identificados deve ser uma lista")

    if not isinstance(resultado["urgencia"], bool):
        erros.append("urgencia deve ser true ou false")

    return erros