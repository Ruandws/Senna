"""
Testes unitários para senna.core.result.Result[T, E]

O QUÊ: valida o tipo que encapsula sucesso/falha em todo o projeto.
PARA QUÊ: garantir que nenhuma exceção inesperada vaze da camada de automação
          para a UI — o contrato central da arquitetura.
COMO: instancia Result via .ok() e .fail(), verifica flags, acesso direto
      a value/error, unwrap/unwrap_error e imutabilidade.
      Não há I/O, rede ou arquivos — 100% em memória.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from senna.core.result import Result

# =========================================================================
# Result.ok — caminho de sucesso
# =========================================================================


def test_ok_sets_success_true() -> None:
    """Result.ok deve marcar success=True."""
    result: Result[str, Exception] = Result.ok("usuario criado")
    assert result.success is True


def test_ok_value_is_accessible() -> None:
    """Result.ok deve permitir leitura direta de .value."""
    result: Result[int, Exception] = Result.ok(42)
    assert result.value == 42


def test_ok_error_is_none() -> None:
    """Em um Result.ok, .error deve ser None."""
    result: Result[str, str] = Result.ok("ok")
    assert result.error is None


def test_ok_accepts_none_value() -> None:
    """Result.ok(None) é válido — representa sucesso sem valor de retorno."""
    result: Result[None, Exception] = Result.ok(None)
    assert result.success is True
    assert result.value is None


# =========================================================================
# Result.fail — caminho de falha
# =========================================================================


def test_fail_sets_success_false() -> None:
    """Result.fail deve marcar success=False."""
    result: Result[str, str] = Result.fail("algo deu errado")
    assert result.success is False


def test_fail_error_is_accessible() -> None:
    """Result.fail deve permitir leitura direta de .error."""
    result: Result[str, str] = Result.fail("timeout")
    assert result.error == "timeout"


def test_fail_value_is_none() -> None:
    """Em um Result.fail, .value deve ser None."""
    result: Result[str, str] = Result.fail("erro")
    assert result.value is None


def test_fail_accepts_string_error() -> None:
    """O tipo E pode ser qualquer coisa — inclusive str."""
    result: Result[int, str] = Result.fail("credencial ausente")
    assert result.error == "credencial ausente"


# =========================================================================
# unwrap — acesso estrito ao valor
# =========================================================================


def test_unwrap_returns_value_on_success() -> None:
    """unwrap() deve retornar value quando success=True."""
    result: Result[int, str] = Result.ok(42)
    assert result.unwrap() == 42


def test_unwrap_raises_on_failure() -> None:
    """unwrap() deve levantar RuntimeError quando success=False."""
    result: Result[str, str] = Result.fail("erro fatal")
    with pytest.raises(RuntimeError, match="falha"):
        result.unwrap()


# =========================================================================
# unwrap_error — acesso estrito ao erro
# =========================================================================


def test_unwrap_error_returns_error_on_failure() -> None:
    """unwrap_error() deve retornar error quando success=False."""
    result: Result[str, str] = Result.fail("timeout")
    assert result.unwrap_error() == "timeout"


def test_unwrap_error_raises_on_success() -> None:
    """unwrap_error() deve levantar RuntimeError quando success=True."""
    result: Result[str, str] = Result.ok("ok")
    with pytest.raises(RuntimeError, match="sucesso"):
        result.unwrap_error()


# =========================================================================
# Imutabilidade (frozen=True)
# =========================================================================


def test_result_is_immutable() -> None:
    """Result é frozen — atribuição direta deve levantar FrozenInstanceError."""
    result = Result.ok("valor")
    with pytest.raises(FrozenInstanceError):
        result.success = False  # type: ignore[misc]


# =========================================================================
# __repr__ legível
# =========================================================================


def test_repr_ok() -> None:
    """__repr__ de sucesso deve conter 'Result.ok'."""
    assert "Result.ok" in repr(Result.ok("teste"))


def test_repr_fail() -> None:
    """__repr__ de falha deve conter 'Result.fail'."""
    assert "Result.fail" in repr(Result.fail("ops"))
