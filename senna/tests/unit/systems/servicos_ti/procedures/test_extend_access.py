"""Testes unitários para senna.systems.servicos_ti.procedures.extend_access.ExtendAccessProcedure"""

from __future__ import annotations

import datetime
from unittest.mock import MagicMock, patch

import pytest

from senna.core.exceptions import ExecutionError
from senna.core.models import AccessPayload
from senna.systems.servicos_ti.procedures.extend_access import (
    ExtendAccessProcedure,
    _is_cpf,
    _resolve_login_from_cpf,
)


@pytest.fixture
def procedure() -> ExtendAccessProcedure:
    return ExtendAccessProcedure()


@pytest.fixture
def mock_ctx() -> MagicMock:
    ctx = MagicMock()
    page = MagicMock()
    ctx.new_page.return_value = page
    return ctx


# --- Testes de funções auxiliares ---

def test_is_cpf() -> None:
    assert _is_cpf("123.456.789-01") is True
    assert _is_cpf("12345678901") is True
    assert _is_cpf("123") is False
    assert _is_cpf("maria.neri") is False


@patch("senna.systems.servicos_ti.procedures.extend_access.UserPage")
def test_resolve_login_from_cpf_success(
    mock_user_page_class: MagicMock, mock_ctx: MagicMock
) -> None:
    mock_user_page = mock_user_page_class.return_value
    mock_result = MagicMock()
    mock_result.login = "maria.neri"
    mock_user_page.search_by_cpf.return_value = [mock_result]

    result = _resolve_login_from_cpf("123.456.789-01", mock_ctx)

    assert result.success is True
    assert result.value == "maria.neri"
    mock_user_page.search_by_cpf.assert_called_once_with("12345678901")
    page = mock_ctx.new_page.return_value
    page.close.assert_called_once()


@patch("senna.systems.servicos_ti.procedures.extend_access.UserPage")
def test_resolve_login_from_cpf_no_results(
    mock_user_page_class: MagicMock, mock_ctx: MagicMock
) -> None:
    mock_user_page = mock_user_page_class.return_value
    mock_user_page.search_by_cpf.return_value = []

    result = _resolve_login_from_cpf("12345678901", mock_ctx)

    assert result.success is False
    assert "Nenhum usuário encontrado" in result.error


@patch("senna.systems.servicos_ti.procedures.extend_access.UserPage")
def test_resolve_login_from_cpf_ambiguous(
    mock_user_page_class: MagicMock, mock_ctx: MagicMock
) -> None:
    mock_user_page = mock_user_page_class.return_value
    mock_result1 = MagicMock()
    mock_result1.login = "login1"
    mock_result2 = MagicMock()
    mock_result2.login = "login2"
    mock_user_page.search_by_cpf.return_value = [mock_result1, mock_result2]

    result = _resolve_login_from_cpf("12345678901", mock_ctx)

    assert result.success is False
    assert "retornou 2 usuários" in result.error


@patch("senna.systems.servicos_ti.procedures.extend_access.UserPage")
def test_resolve_login_from_cpf_error(mock_user_page_class: MagicMock, mock_ctx: MagicMock) -> None:
    mock_user_page = mock_user_page_class.return_value
    mock_user_page.search_by_cpf.side_effect = ExecutionError("search_user_by_cpf", "Timeout")

    result = _resolve_login_from_cpf("12345678901", mock_ctx)

    assert result.success is False
    assert "[search_user_by_cpf] Timeout" in result.error


@patch("senna.systems.servicos_ti.procedures.extend_access.UserPage")
def test_resolve_login_from_cpf_unexpected_exception(
    mock_user_page_class: MagicMock, mock_ctx: MagicMock
) -> None:
    mock_user_page = mock_user_page_class.return_value
    mock_user_page.search_by_cpf.side_effect = RuntimeError("Falha inesperada")

    result = _resolve_login_from_cpf("12345678901", mock_ctx)

    assert result.success is False
    assert "Erro ao resolver login a partir do CPF" in result.error
    assert "Falha inesperada" in result.error
    page = mock_ctx.new_page.return_value
    page.close.assert_called_once()


# --- Testes de propriedades e validate ---

def test_procedure_id(procedure: ExtendAccessProcedure) -> None:
    assert procedure.procedure_id == "extend_access"


def test_validate_success(procedure: ExtendAccessProcedure) -> None:
    payload = AccessPayload(registration="maria.neri", expiration_date=datetime.date(2026, 12, 31))
    result = procedure.validate(payload)
    assert result.success is True
    assert result.value is None


def test_validate_empty_registration(procedure: ExtendAccessProcedure) -> None:
    payload = AccessPayload(registration="   ", expiration_date=datetime.date(2026, 12, 31))
    result = procedure.validate(payload)
    assert result.success is False
    assert result.error == "Matrícula/login não pode estar vazio."


# --- Testes de execute ---

@patch("senna.systems.servicos_ti.procedures.extend_access._resolve_login_from_cpf")
@patch("senna.systems.servicos_ti.procedures.extend_access.UserDetailsPage")
def test_execute_with_login_success(
    mock_details_page_class: MagicMock,
    mock_resolve: MagicMock,
    procedure: ExtendAccessProcedure,
    mock_ctx: MagicMock,
) -> None:
    mock_details_page = mock_details_page_class.return_value
    mock_details_page.verify_date_saved.return_value = True

    payload = AccessPayload(registration="maria.neri", expiration_date=datetime.date(2026, 12, 31))
    result = procedure.execute(payload, mock_ctx)

    assert result.success is True
    assert "alterada para 31/12/2026" in result.value

    # Validate no CPF resolution was called
    mock_resolve.assert_not_called()

    # Validate page interaction
    mock_details_page.navigate.assert_called_once_with("maria.neri")
    mock_details_page.set_expiration_date.assert_called_once_with(payload.expiration_date)
    mock_details_page.click_update.assert_called_once()
    mock_details_page.verify_date_saved.assert_called_once_with(payload.expiration_date)

    page = mock_ctx.new_page.return_value
    page.close.assert_called_once()


@patch("senna.systems.servicos_ti.procedures.extend_access._resolve_login_from_cpf")
@patch("senna.systems.servicos_ti.procedures.extend_access.UserDetailsPage")
def test_execute_with_cpf_success(
    mock_details_page_class: MagicMock,
    mock_resolve: MagicMock,
    procedure: ExtendAccessProcedure,
    mock_ctx: MagicMock,
) -> None:
    # Setup mock to return a fake successful result with unwrap
    resolve_result = MagicMock()
    resolve_result.success = True
    resolve_result.unwrap.return_value = "maria.neri"
    mock_resolve.return_value = resolve_result

    mock_details_page = mock_details_page_class.return_value
    mock_details_page.verify_date_saved.return_value = True

    payload = AccessPayload(
        registration="123.456.789-01", expiration_date=datetime.date(2026, 12, 31)
    )
    result = procedure.execute(payload, mock_ctx)

    assert result.success is True

    # Validate CPF resolution was called
    mock_resolve.assert_called_once_with("123.456.789-01", mock_ctx)
    mock_details_page.navigate.assert_called_once_with("maria.neri")


@patch("senna.systems.servicos_ti.procedures.extend_access._resolve_login_from_cpf")
def test_execute_with_cpf_resolution_failure(
    mock_resolve: MagicMock,
    procedure: ExtendAccessProcedure,
    mock_ctx: MagicMock,
) -> None:
    resolve_result = MagicMock()
    resolve_result.success = False
    resolve_result.unwrap_error.return_value = "Nenhum usuário encontrado"
    mock_resolve.return_value = resolve_result

    payload = AccessPayload(registration="12345678901", expiration_date=datetime.date(2026, 12, 31))
    result = procedure.execute(payload, mock_ctx)

    assert result.success is False
    assert result.error == "Nenhum usuário encontrado"

    # Context should not have opened a second page for details
    # Only the first page in _resolve_login_from_cpf is created
    # (which is mocked out anyway, so 0 calls here)
    mock_ctx.new_page.assert_not_called()


@patch("senna.systems.servicos_ti.procedures.extend_access.UserDetailsPage")
def test_execute_verification_failure(
    mock_details_page_class: MagicMock,
    procedure: ExtendAccessProcedure,
    mock_ctx: MagicMock,
) -> None:
    mock_details_page = mock_details_page_class.return_value
    mock_details_page.verify_date_saved.return_value = False

    payload = AccessPayload(registration="maria.neri", expiration_date=datetime.date(2026, 12, 31))
    result = procedure.execute(payload, mock_ctx)

    assert result.success is False
    assert (
        "Verificação falhou: data não persistiu após reload para o usuário 'maria.neri'."
        in result.error
    )


@patch("senna.systems.servicos_ti.procedures.extend_access.UserDetailsPage")
def test_execute_execution_error(
    mock_details_page_class: MagicMock,
    procedure: ExtendAccessProcedure,
    mock_ctx: MagicMock,
) -> None:
    mock_details_page = mock_details_page_class.return_value
    mock_details_page.navigate.side_effect = ExecutionError("extend_access", "Timeout na navegação")

    payload = AccessPayload(registration="maria.neri", expiration_date=datetime.date(2026, 12, 31))
    result = procedure.execute(payload, mock_ctx)

    assert result.success is False
    assert result.error == "[extend_access] Timeout na navegação"


@patch("senna.systems.servicos_ti.procedures.extend_access.UserDetailsPage")
def test_execute_unexpected_exception(
    mock_details_page_class: MagicMock,
    procedure: ExtendAccessProcedure,
    mock_ctx: MagicMock,
) -> None:
    mock_details_page = mock_details_page_class.return_value
    mock_details_page.navigate.side_effect = ValueError("Algo quebrou")

    payload = AccessPayload(registration="maria.neri", expiration_date=datetime.date(2026, 12, 31))
    result = procedure.execute(payload, mock_ctx)

    assert result.success is False
    assert "Erro inesperado ao alterar data de expiração" in result.error
