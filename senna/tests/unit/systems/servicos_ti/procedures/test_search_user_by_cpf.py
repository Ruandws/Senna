"""Testes unitários para a procedure SearchUserByCpfProcedure."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from senna.core.exceptions import ExecutionError
from senna.core.models import UserSearchResult
from senna.systems.servicos_ti.procedures.search_user_by_cpf import SearchUserByCpfProcedure


@pytest.fixture
def procedure() -> SearchUserByCpfProcedure:
    return SearchUserByCpfProcedure()


@pytest.fixture
def mock_ctx() -> MagicMock:
    ctx = MagicMock()
    page = MagicMock()
    ctx.new_page.return_value = page
    return ctx


# --- Testes de propriedades e validate ---

def test_procedure_id(procedure: SearchUserByCpfProcedure) -> None:
    assert procedure.procedure_id == "search_user_by_cpf"


def test_validate_valid_cpf(procedure: SearchUserByCpfProcedure) -> None:
    result = procedure.validate("123.456.789-01")
    assert result.success
    assert result.value is None


def test_validate_invalid_cpf_length(procedure: SearchUserByCpfProcedure) -> None:
    result = procedure.validate("123")
    assert not result.success
    assert result.error == "CPF inválido: informe 11 dígitos numéricos."


# --- Testes de execute ---

@patch("senna.systems.servicos_ti.procedures.search_user_by_cpf.UserPage")
def test_execute_success_with_results(
    mock_user_page_class: MagicMock,
    procedure: SearchUserByCpfProcedure,
    mock_ctx: MagicMock,
) -> None:
    mock_user_page = mock_user_page_class.return_value
    expected_results = [
        UserSearchResult(nome="João Silva", login="joao.silva"),
    ]
    mock_user_page.search_by_cpf.return_value = expected_results

    result = procedure.execute("123.456.789-01", mock_ctx)

    assert result.success
    assert result.value == expected_results

    mock_ctx.new_page.assert_called_once()
    page = mock_ctx.new_page.return_value
    page.goto.assert_called_once()

    mock_user_page_class.assert_called_once_with(page)
    mock_user_page.search_by_cpf.assert_called_once_with("12345678901")

    # Verifica finally
    page.close.assert_called_once()


@patch("senna.systems.servicos_ti.procedures.search_user_by_cpf.UserPage")
def test_execute_success_no_results(
    mock_user_page_class: MagicMock,
    procedure: SearchUserByCpfProcedure,
    mock_ctx: MagicMock,
) -> None:
    mock_user_page = mock_user_page_class.return_value
    mock_user_page.search_by_cpf.return_value = []

    result = procedure.execute("00000000000", mock_ctx)

    assert result.success
    assert result.value == []

    page = mock_ctx.new_page.return_value
    page.close.assert_called_once()


@patch("senna.systems.servicos_ti.procedures.search_user_by_cpf.UserPage")
def test_execute_execution_error(
    mock_user_page_class: MagicMock,
    procedure: SearchUserByCpfProcedure,
    mock_ctx: MagicMock,
) -> None:
    mock_user_page = mock_user_page_class.return_value
    mock_user_page.search_by_cpf.side_effect = ExecutionError(
        "search_user_by_cpf", "Timeout na pesquisa"
    )

    result = procedure.execute("12345678901", mock_ctx)

    assert not result.success
    assert result.error == "[search_user_by_cpf] Timeout na pesquisa"

    page = mock_ctx.new_page.return_value
    page.close.assert_called_once()


@patch("senna.systems.servicos_ti.procedures.search_user_by_cpf.UserPage")
def test_execute_unexpected_exception(
    mock_user_page_class: MagicMock,
    procedure: SearchUserByCpfProcedure,
    mock_ctx: MagicMock,
) -> None:
    mock_user_page = mock_user_page_class.return_value
    mock_user_page.search_by_cpf.side_effect = ValueError("Something went wrong")

    result = procedure.execute("12345678901", mock_ctx)

    assert not result.success
    assert "Erro inesperado na pesquisa por CPF: Something went wrong" in result.error

    page = mock_ctx.new_page.return_value
    page.close.assert_called_once()
