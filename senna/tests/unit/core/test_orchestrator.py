"""
Testes unitários para senna.core.orchestrator.Orchestrator

O QUÊ: valida o orquestrador que coordena sistema + procedimento + browser.
PARA QUÊ: garantir que o Orchestrator instancia, valida, executa e registra
          auditoria corretamente — inclusive em cenários de falha e erro.
COMO: usa MagicMock para sistema, procedimento, browser_factory e audit_logger.
      Todos os caminhos são testados sem I/O real — 100% em memória.
"""

from __future__ import annotations

import getpass
from unittest.mock import MagicMock, patch

import pytest

from senna.core.base_procedure import BaseProcedure
from senna.core.base_system import BaseSystem
from senna.core.exceptions import OrchestratorError
from senna.core.orchestrator import Orchestrator
from senna.core.result import Result

# =========================================================================
# Fixtures
# =========================================================================


@pytest.fixture
def mock_system() -> MagicMock:
    system = MagicMock(spec=BaseSystem)
    system.is_logged_in.return_value = True
    system.login.return_value = Result.ok(None)
    system.logout.return_value = Result.ok(None)
    return system


@pytest.fixture
def mock_procedure() -> MagicMock:
    procedure = MagicMock(spec=BaseProcedure)
    procedure.validate.return_value = Result.ok(None)
    procedure.execute.return_value = Result.ok("Sucesso")
    return procedure


@pytest.fixture
def orchestrator(mock_system: MagicMock, mock_procedure: MagicMock) -> Orchestrator:
    with patch.dict("senna.core.orchestrator.AVAILABLE_SYSTEMS", {"sys1": mock_system}, clear=True):
        with patch.dict(
            "senna.core.orchestrator.AVAILABLE_PROCEDURES",
            {"sys1": {"proc1": mock_procedure}},
            clear=True,
        ):
            yield Orchestrator()


# =========================================================================
# get_system
# =========================================================================


def test_get_system_success(orchestrator: Orchestrator, mock_system: MagicMock) -> None:
    assert orchestrator.get_system("sys1") == mock_system


def test_get_system_not_found(orchestrator: Orchestrator) -> None:
    with pytest.raises(OrchestratorError, match="Sistema 'sys2' não registrado"):
        orchestrator.get_system("sys2")


# =========================================================================
# get_procedure
# =========================================================================


def test_get_procedure_success(orchestrator: Orchestrator, mock_procedure: MagicMock) -> None:
    assert orchestrator.get_procedure("sys1", "proc1") == mock_procedure


def test_get_procedure_system_not_found(orchestrator: Orchestrator) -> None:
    with pytest.raises(OrchestratorError, match="Nenhum procedimento registrado para 'sys2'"):
        orchestrator.get_procedure("sys2", "proc1")


def test_get_procedure_not_found(orchestrator: Orchestrator) -> None:
    with pytest.raises(OrchestratorError, match="Procedimento 'proc2' não registrado para 'sys1'"):
        orchestrator.get_procedure("sys1", "proc2")


# =========================================================================
# list_systems / list_procedures
# =========================================================================


def test_list_systems(orchestrator: Orchestrator) -> None:
    assert orchestrator.list_systems() == ["sys1"]


def test_list_procedures(orchestrator: Orchestrator) -> None:
    assert orchestrator.list_procedures("sys1") == ["proc1"]
    assert orchestrator.list_procedures("sys2") == []


# =========================================================================
# run — caminho feliz
# =========================================================================


@patch("senna.core.orchestrator.browser_factory")
@patch("senna.core.orchestrator.audit_logger")
def test_run_success(
    mock_audit_logger: MagicMock,
    mock_browser_factory: MagicMock,
    orchestrator: Orchestrator,
    mock_system: MagicMock,
    mock_procedure: MagicMock,
) -> None:
    payload = MagicMock()
    mock_ctx = MagicMock()
    mock_browser_factory.open_context.return_value = mock_ctx

    result = orchestrator.run("sys1", "proc1", payload)

    assert result.success is True
    assert result.value == "Sucesso"

    mock_procedure.validate.assert_called_once_with(payload)
    mock_browser_factory.open_context.assert_called_once_with("sys1")
    mock_system.is_logged_in.assert_called_once_with(mock_ctx)
    # Não chama login porque is_logged_in retornou True
    mock_system.login.assert_not_called()
    mock_procedure.execute.assert_called_once_with(payload, mock_ctx)
    mock_system.logout.assert_called_once_with(mock_ctx)
    mock_browser_factory.close_context.assert_called_once_with("sys1")
    mock_audit_logger.log_execution.assert_called_once()


# =========================================================================
# run — login necessário
# =========================================================================


@patch("senna.core.orchestrator.browser_factory")
@patch("senna.core.orchestrator.audit_logger")
def test_run_needs_login(
    mock_audit_logger: MagicMock,
    mock_browser_factory: MagicMock,
    orchestrator: Orchestrator,
    mock_system: MagicMock,
    mock_procedure: MagicMock,
) -> None:
    payload = object()
    mock_system.is_logged_in.return_value = False

    result = orchestrator.run("sys1", "proc1", payload)

    assert result.success is True
    mock_system.login.assert_called_once()
    mock_procedure.execute.assert_called_once()
    mock_audit_logger.log_execution.assert_called_once()


# =========================================================================
# run — falhas antes do try/finally (sem audit log)
# =========================================================================


def test_run_system_not_found(orchestrator: Orchestrator) -> None:
    result = orchestrator.run("sys2", "proc1", object())
    assert result.success is False
    assert "Sistema 'sys2' não registrado" in str(result.error)


def test_run_validation_fails(orchestrator: Orchestrator, mock_procedure: MagicMock) -> None:
    mock_procedure.validate.return_value = Result.fail("Campo inválido")
    result = orchestrator.run("sys1", "proc1", object())
    assert result.success is False
    assert result.error == "Campo inválido"
    mock_procedure.execute.assert_not_called()


# =========================================================================
# run — falhas dentro do try/finally (com audit log)
# =========================================================================


@patch("senna.core.orchestrator.browser_factory")
@patch("senna.core.orchestrator.audit_logger")
def test_run_login_fails(
    mock_audit_logger: MagicMock,
    mock_browser_factory: MagicMock,
    orchestrator: Orchestrator,
    mock_system: MagicMock,
    mock_procedure: MagicMock,
) -> None:
    mock_system.is_logged_in.return_value = False
    mock_system.login.return_value = Result.fail("Credenciais inválidas")

    result = orchestrator.run("sys1", "proc1", object())

    assert result.success is False
    assert "Falha no login" in str(result.error)
    assert "Credenciais inválidas" in str(result.error)
    mock_procedure.execute.assert_not_called()
    mock_audit_logger.log_execution.assert_called_once()


@patch("senna.core.orchestrator.browser_factory")
@patch("senna.core.orchestrator.audit_logger")
def test_run_unexpected_error(
    mock_audit_logger: MagicMock,
    mock_browser_factory: MagicMock,
    orchestrator: Orchestrator,
    mock_procedure: MagicMock,
    mock_system: MagicMock,
) -> None:
    mock_procedure.execute.side_effect = RuntimeError("Erro bizarro")

    result = orchestrator.run("sys1", "proc1", object())

    assert result.success is False
    assert "Erro inesperado: Erro bizarro" in str(result.error)
    # Deve garantir que logout e close_context são chamados
    mock_system.logout.assert_called_once()
    mock_browser_factory.close_context.assert_called_once_with("sys1")
    mock_audit_logger.log_execution.assert_called_once()


@patch("senna.core.orchestrator.browser_factory")
@patch("senna.core.orchestrator.audit_logger")
def test_run_logout_error_does_not_fail_execution(
    mock_audit_logger: MagicMock,
    mock_browser_factory: MagicMock,
    orchestrator: Orchestrator,
    mock_system: MagicMock,
) -> None:
    # Mesmo se logout falhar, o resultado da procedure deve ser retornado
    mock_system.logout.side_effect = Exception("Falha ao sair")

    result = orchestrator.run("sys1", "proc1", object())

    assert result.success is True
    assert result.value == "Sucesso"
    mock_browser_factory.close_context.assert_called_once_with("sys1")
    mock_audit_logger.log_execution.assert_called_once()


# =========================================================================
# run — audit log — campos corretos
# =========================================================================


@patch("senna.core.orchestrator.browser_factory")
@patch("senna.core.orchestrator.audit_logger")
def test_run_audit_log_fields(
    mock_audit_logger: MagicMock,
    mock_browser_factory: MagicMock,
    orchestrator: Orchestrator,
) -> None:
    class FakePayload:
        def __init__(self) -> None:
            self.campo1 = "valor"
            self.campo2 = 123

    payload = FakePayload()
    orchestrator.run("sys1", "proc1", payload)

    mock_audit_logger.log_execution.assert_called_once()
    audit_entry = mock_audit_logger.log_execution.call_args[0][0]

    assert audit_entry.system_id == "sys1"
    assert audit_entry.procedure_id == "proc1"
    assert audit_entry.operator == getpass.getuser()
    assert audit_entry.success is True
    assert audit_entry.payload_keys == ["campo1", "campo2"]
    assert audit_entry.error is None


@patch("senna.core.orchestrator.browser_factory")
@patch("senna.core.orchestrator.audit_logger")
def test_run_audit_log_records_failure(
    mock_audit_logger: MagicMock,
    mock_browser_factory: MagicMock,
    orchestrator: Orchestrator,
    mock_procedure: MagicMock,
) -> None:
    """Audit log deve registrar success=False e error quando a execução falha."""
    mock_procedure.execute.side_effect = RuntimeError("Falha na automação")

    orchestrator.run("sys1", "proc1", object())

    audit_entry = mock_audit_logger.log_execution.call_args[0][0]
    assert audit_entry.success is False
    assert audit_entry.error is not None
    assert "Falha na automação" in str(audit_entry.error)
