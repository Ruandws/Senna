"""
Testes unitários para senna.core.exceptions

O QUÊ: valida a hierarquia de classes de erro do projeto.
PARA QUÊ: garantir que cada exceção pode ser capturada pelo tipo correto
          (ex: `except SennaError` captura qualquer erro do sistema).
          Sem isso, um `except` errado na UI pode deixar erros vazarem.
COMO: usa isinstance/issubclass para verificar herança; levanta as exceções
      reais para confirmar que são capturáveis pelos pais esperados.
      Valida atributos customizados (system_id, field, row_index, etc.)
      e mensagens formatadas.
"""

from __future__ import annotations

import pytest

from senna.core.exceptions import (
    AuthenticationError,
    BatchError,
    BrowserError,
    ConfigurationError,
    ExecutionError,
    InvalidSpreadsheetError,
    MissingCredentialError,
    OrchestratorError,
    ProcedureError,
    RowExecutionError,
    SennaError,
    SessionError,
    SystemError,
    SystemUnavailableError,
    TimeoutError,
    ValidationError,
)

# =========================================================================
# Raiz da hierarquia
# =========================================================================


def test_senna_error_is_exception() -> None:
    """SennaError deve ser subclasse de Exception."""
    assert issubclass(SennaError, Exception)


def test_senna_error_can_be_raised_and_caught() -> None:
    """Levantando SennaError, deve ser capturável como Exception."""
    with pytest.raises(Exception):
        raise SennaError("erro base")


# =========================================================================
# Configuração e ambiente
# =========================================================================


def test_missing_credential_is_senna_error() -> None:
    assert issubclass(MissingCredentialError, SennaError)


def test_configuration_error_is_senna_error() -> None:
    assert issubclass(ConfigurationError, SennaError)


def test_missing_credential_carries_message() -> None:
    """A mensagem de erro deve ser preservada."""
    with pytest.raises(MissingCredentialError, match="SERVICOS_TI_PASSWORD"):
        raise MissingCredentialError("SERVICOS_TI_PASSWORD")


# =========================================================================
# Sistemas e autenticação — SystemError e filhas
# =========================================================================


def test_system_error_hierarchy() -> None:
    """SystemError → SennaError."""
    assert issubclass(SystemError, SennaError)


def test_system_error_stores_system_id() -> None:
    """SystemError deve armazenar system_id e formatar mensagem."""
    exc = SystemError("servicos_ti", "fora do ar")
    assert exc.system_id == "servicos_ti"
    assert "[servicos_ti]" in str(exc)
    assert "fora do ar" in str(exc)


def test_system_unavailable_is_system_error() -> None:
    assert issubclass(SystemUnavailableError, SystemError)


def test_authentication_error_is_system_error() -> None:
    assert issubclass(AuthenticationError, SystemError)


def test_session_error_is_system_error() -> None:
    assert issubclass(SessionError, SystemError)


def test_authentication_error_caught_as_senna_error() -> None:
    """Cadeia completa: AuthenticationError → SystemError → SennaError."""
    with pytest.raises(SennaError):
        raise AuthenticationError("servicos_ti", "credenciais inválidas")


# =========================================================================
# Procedimentos — ProcedureError e filhas
# =========================================================================


def test_procedure_error_hierarchy() -> None:
    """ProcedureError → SennaError."""
    assert issubclass(ProcedureError, SennaError)


def test_procedure_error_stores_procedure_id() -> None:
    """ProcedureError deve armazenar procedure_id e formatar mensagem."""
    exc = ProcedureError("add_user", "campo obrigatório vazio")
    assert exc.procedure_id == "add_user"
    assert "[add_user]" in str(exc)


def test_validation_error_is_procedure_error() -> None:
    assert issubclass(ValidationError, ProcedureError)


def test_validation_error_stores_field_and_reason() -> None:
    """ValidationError deve expor field e reason."""
    exc = ValidationError("add_user", "email", "formato inválido")
    assert exc.procedure_id == "add_user"
    assert exc.field == "email"
    assert exc.reason == "formato inválido"
    assert "email" in str(exc)


def test_execution_error_is_procedure_error() -> None:
    assert issubclass(ExecutionError, ProcedureError)


def test_timeout_error_is_procedure_error() -> None:
    assert issubclass(TimeoutError, ProcedureError)


def test_timeout_caught_as_senna_error() -> None:
    """Cadeia: TimeoutError → ProcedureError → SennaError."""
    with pytest.raises(SennaError):
        raise TimeoutError("add_user", "excedeu 60s")


# =========================================================================
# Browser
# =========================================================================


def test_browser_error_is_senna_error() -> None:
    assert issubclass(BrowserError, SennaError)


# =========================================================================
# Processamento em lote
# =========================================================================


def test_batch_error_is_senna_error() -> None:
    assert issubclass(BatchError, SennaError)


def test_invalid_spreadsheet_is_batch_error() -> None:
    assert issubclass(InvalidSpreadsheetError, BatchError)


def test_invalid_spreadsheet_stores_path() -> None:
    """InvalidSpreadsheetError deve expor path e formatar mensagem."""
    exc = InvalidSpreadsheetError("data/input/lote.xlsx", "coluna 'cpf' ausente")
    assert exc.path == "data/input/lote.xlsx"
    assert "lote.xlsx" in str(exc)
    assert "coluna 'cpf' ausente" in str(exc)


def test_row_execution_error_is_batch_error() -> None:
    assert issubclass(RowExecutionError, BatchError)


def test_row_execution_error_stores_row_index() -> None:
    """RowExecutionError deve expor row_index."""
    exc = RowExecutionError(42, "timeout")
    assert exc.row_index == 42
    assert "42" in str(exc)


def test_invalid_spreadsheet_caught_as_senna_error() -> None:
    """Cadeia: InvalidSpreadsheetError → BatchError → SennaError."""
    with pytest.raises(SennaError):
        raise InvalidSpreadsheetError("x.xlsx", "corrompida")


# =========================================================================
# Orquestração
# =========================================================================


def test_orchestrator_error_is_senna_error() -> None:
    assert issubclass(OrchestratorError, SennaError)
