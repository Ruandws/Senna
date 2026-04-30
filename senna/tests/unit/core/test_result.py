"""
Testes unitários para senna.core.result.Result[T, E]

O QUÊ: valida o tipo que encapsula sucesso/falha em todo o projeto.
PARA QUÊ: garantir que nenhuma exceção inesperada vaze da camada de automação
          para a UI — o contrato central da arquitetura.
COMO: instancia Result via .ok() e .fail(), verifica flags e propriedades;
      não há I/O, rede ou arquivos — 100% em memória.
"""

from __future__ import annotations

import pytest
from dataclasses import FrozenInstanceError

from senna.core.result import Result


# =============================================================================
# Result.ok — caminho de sucesso
# =============================================================================


def test_ok_sets_success_true() -> None:
    """Result.ok deve marcar success=True."""
    result: Result[str, Exception] = Result.ok("usuario criado")
    assert result.success is True


def test_ok_value_is_accessible() -> None:
    """Result.ok deve permitir leitura de .value sem exceção."""
    result: Result[int, Exception] = Result.ok(42)
    assert result.value == 42


def test_ok_error_raises() -> None:
    """Acessar .error em um Result.ok deve levantar ValueError — não faz sentido."""
    result: Result[str, Exception] = Result.ok("ok")
    with pytest.raises(ValueError, match="sucesso"):
        _ = result.error


def test_ok_accepts_none_value() -> None:
    """Result.ok(None) é válido — representa sucesso sem valor de retorno."""
    result: Result[None, Exception] = Result.ok(None)
    assert result.success is True
    assert result.value is None


# =============================================================================
# Result.fail — caminho de falha
# =============================================================================


def test_fail_sets_success_false() -> None:
    """Result.fail deve marcar success=False."""
    result: Result[str, ValueError] = Result.fail(ValueError("algo deu errado"))
    assert result.success is False


def test_fail_error_is_accessible() -> None:
    """Result.fail deve permitir leitura de .error sem exceção."""
    erro = RuntimeError("timeout")
    result: Result[str, RuntimeError] = Result.fail(erro)
    assert result.error is erro


def test_fail_value_raises() -> None:
    """Acessar .value em um Result.fail deve levantar ValueError."""
    result: Result[str, Exception] = Result.fail(Exception("falha"))
    with pytest.raises(ValueError, match="falha"):
        _ = result.value


def test_fail_accepts_string_error() -> None:
    """O tipo E pode ser qualquer coisa — inclusive str."""
    result: Result[int, str] = Result.fail("credencial ausente")
    assert result.error == "credencial ausente"


# =============================================================================
# Result.map — transformação encadeada
# =============================================================================


def test_map_transforms_value_on_success() -> None:
    """map deve aplicar a função ao valor quando Result é sucesso."""
    result: Result[int, str] = Result.ok(5)
    mapped = result.map(lambda x: x * 2)
    assert mapped.success is True
    assert mapped.value == 10


def test_map_is_noop_on_failure() -> None:
    """map NÃO deve executar a função quando Result é falha — falha passa direto."""
    chamado = {"count": 0}

    def fn(x: int) -> int:
        chamado["count"] += 1
        return x * 2

    result: Result[int, str] = Result.fail("erro")
    mapped = result.map(fn)

    assert mapped.success is False
    assert chamado["count"] == 0  # fn nunca foi chamada


# =============================================================================
# Imutabilidade (frozen=True)
# =============================================================================


def test_result_is_immutable() -> None:
    """Result é frozen — atribuição direta deve levantar FrozenInstanceError."""
    result = Result.ok("valor")
    with pytest.raises(FrozenInstanceError):
        result.success = False  # type: ignore[misc]


# =============================================================================
# __repr__ legível
# =============================================================================


def test_repr_ok() -> None:
    """__repr__ de sucesso deve conter 'Result.ok'."""
    assert "Result.ok" in repr(Result.ok("teste"))


def test_repr_fail() -> None:
    """__repr__ de falha deve conter 'Result.fail'."""
    assert "Result.fail" in repr(Result.fail("ops"))
