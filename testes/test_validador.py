"""Testes das regras fixas de validação da saída da IA."""

import sys
from pathlib import Path

# Permite importar os módulos de src/
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from validador import validar_saida


def saida_valida() -> dict:
    """Retorna um exemplo de saída correta da IA (base para os testes)."""
    return {
        "tipo_solicitacao": "interesse_em_credito_pj",
        "empresa": "Alfa Comércio LTDA",
        "cnpj": "12.345.678/0001-99",
        "documentos_identificados": [],
        "data_mencionada": None,
        "urgencia": False,
        "area_sugerida": "Comercial",
        "proxima_acao": "encaminhar para contato comercial",
        "confianca": "alto",
        "justificativa": "Mensagem clara de interesse em crédito.",
    }


def test_saida_valida_passa_sem_erros():
    assert validar_saida(saida_valida()) == []


def test_campo_obrigatorio_ausente_gera_erro():
    saida = saida_valida()
    del saida["tipo_solicitacao"]
    erros = validar_saida(saida)
    assert len(erros) == 1
    assert "tipo_solicitacao" in erros[0]


def test_categoria_inventada_pela_ia_gera_erro():
    saida = saida_valida()
    saida["tipo_solicitacao"] = "pedido_de_credito"  # variação inventada
    erros = validar_saida(saida)
    assert any("tipo_solicitacao" in e for e in erros)


def test_confianca_fora_da_escala_gera_erro():
    saida = saida_valida()
    saida["confianca"] = "altissimo"
    erros = validar_saida(saida)
    assert any("confianca" in e for e in erros)


def test_urgencia_como_texto_gera_erro():
    saida = saida_valida()
    saida["urgencia"] = "sim"  # deveria ser booleano
    erros = validar_saida(saida)
    assert any("urgencia" in e for e in erros)


def test_documentos_como_texto_gera_erro():
    saida = saida_valida()
    saida["documentos_identificados"] = "contrato social"  # deveria ser lista
    erros = validar_saida(saida)
    assert any("documentos_identificados" in e for e in erros)


def test_multiplos_erros_sao_todos_reportados():
    saida = saida_valida()
    saida["confianca"] = "altissimo"
    saida["area_sugerida"] = "Jurídico"  # não existe na lista
    erros = validar_saida(saida)
    assert len(erros) == 2