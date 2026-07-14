"""Testes da montagem do prompt (regras fixas de negócio)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from prompt import montar_prompt, TIPOS_SOLICITACAO, PROXIMAS_ACOES


def test_prompt_contem_a_mensagem_do_usuario():
    prompt = montar_prompt("Segunda via", "Preciso do boleto novamente.")
    assert "Segunda via" in prompt
    assert "Preciso do boleto novamente." in prompt


def test_prompt_contem_todas_as_categorias_permitidas():
    prompt = montar_prompt("Teste", "Mensagem qualquer")
    for tipo in TIPOS_SOLICITACAO:
        assert tipo in prompt
    for acao in PROXIMAS_ACOES:
        assert acao in prompt


def test_prompt_exige_saida_em_json():
    prompt = montar_prompt("Teste", "Mensagem qualquer")
    assert "JSON" in prompt