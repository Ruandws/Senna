"""
Testes unitários para senna.core.exceptions

O QUÊ: valida a hierarquia de classes de erro do projeto.
PARA QUÊ: garantir que cada exceção pode ser capturada pelo tipo correto
          (ex: `except SennaError` captura qualquer erro do sistema).
          Sem isso, um `except` errado na UI pode deixar erros vazarem.
COMO: usa isinstance/issubclass para verificar herança; levanta as exceções
      reais para confirmar que são capturáveis pelos pais esperados.
"""

from __future__ import annotations

import pytest

from senna.core.exceptions import (
    AuthenticationError,
    DataLoaderError,
    InvalidSettingsError,
    InvalidSpreadsheetError,
    MissingCredentialError,
    ProcedureError,
    ProcedureTimeoutError,
    SennaError,
    SessionExpiredError,
    SystemUnavailableError,
    ValidationError,
)


# =============================================================================
# Raiz da hierarquia
# =============================================================================


def test_senna_error_is_exception() -> None:
    """SennaError deve ser subclasse de Exception — capturável genericamente."""
    assert issubclass(SennaError, Exception)


def test_senna_error_can_be_raised_and_caught() -> None:
    """Levantando SennaError, deve ser capturável como Exception."""
    with pytest.raises(Exception):
        raise SennaError("erro base")


# =============================================================================
# Configuração e ambiente
# =============================================================================


def test_missing_credential_error_is_senna_error() -> None:
    assert issubclass(MissingCredentialError, SennaError)


def test_invalid_settings_error_is_senna_error() -> None:
    assert issubclass(InvalidSettingsError, SennaError)


def test_missing_credential_carries_message() -> None:
    """A mensagem de erro deve ser preservada."""
    with pytest.raises(MissingCredentialError, match="SERVICOS_TI_PASSWORD"):
        raise MissingCredentialError("SERVICOS_TI_PASSWORD")


# =============================================================================
# Sistema e autenticação
# =============================================================================


def test_system_unavailable_error_is_senna_error() -> None:
    assert issubclass(SystemUnavailableError, SennaError)


def test_authentication_error_is_senna_error() -> None:
    assert issubclass(AuthenticationError, SennaError)


def test_session_expired_error_is_senna_error() -> None:
    assert issubclass(SessionExpiredError, SennaError)


def test_authentication_error_caught_as_senna_error() -> None:
    """Um except SennaError deve capturar AuthenticationError."""
    with pytest.raises(SennaError):
        raise AuthenticationError("credenciais inválidas")


# =============================================================================
# Procedimentos e sub-hierarquia
# =============================================================================


def test_procedure_error_is_senna_error() -> None:
    assert issubclass(ProcedureError, SennaError)


def test_validation_error_is_senna_error() -> None:
    assert issubclass(ValidationError, SennaError)


def test_procedure_timeout_error_is_procedure_error() -> None:
    """ProcedureTimeoutError é especialização de ProcedureError."""
    assert issubclass(ProcedureTimeoutError, ProcedureError)


def test_procedure_timeout_caught_as_senna_error() -> None:
    """Cadeia completa: ProcedureTimeoutError → ProcedureError → SennaError."""
    with pytest.raises(SennaError):
        raise ProcedureTimeoutError("excedeu 60s")


# =============================================================================
# Processamento em lote
# =============================================================================


def test_data_loader_error_is_senna_error() -> None:
    assert issubclass(DataLoaderError, SennaError)


def test_invalid_spreadsheet_error_is_data_loader_error() -> None:
    """InvalidSpreadsheetError é especialização de DataLoaderError."""
    assert issubclass(InvalidSpreadsheetError, DataLoaderError)


def test_invalid_spreadsheet_caught_as_senna_error() -> None:
    """Cadeia completa: InvalidSpreadsheetError → DataLoaderError → SennaError."""
    with pytest.raises(SennaError):
        raise InvalidSpreadsheetError("coluna 'cpf' ausente")
