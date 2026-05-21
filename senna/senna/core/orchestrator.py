"""Orquestrador de sistemas e procedimentos do Senna."""

from __future__ import annotations

import getpass
import logging

from senna.core import AVAILABLE_PROCEDURES, AVAILABLE_SYSTEMS
from senna.core.base_procedure import BaseProcedure
from senna.core.base_system import BaseSystem
from senna.core.exceptions import OrchestratorError
from senna.core.logger import AuditEntry, audit_logger
from senna.core.result import Result
from senna.utils.browser_factory import browser_factory

app_logger = logging.getLogger("senna.app")


class Orchestrator:
    def get_system(self, system_id: str) -> BaseSystem:
        system = AVAILABLE_SYSTEMS.get(system_id)
        if system is None:
            raise OrchestratorError(
                f"Sistema '{system_id}' não registrado. Disponíveis: {list(AVAILABLE_SYSTEMS)}"
            )
        return system

    def get_procedure(self, system_id: str, procedure_id: str) -> BaseProcedure:
        system_procedures = AVAILABLE_PROCEDURES.get(system_id)
        if system_procedures is None:
            raise OrchestratorError(f"Nenhum procedimento registrado para '{system_id}'.")
        procedure = system_procedures.get(procedure_id)
        if procedure is None:
            raise OrchestratorError(
                f"Procedimento '{procedure_id}' não registrado para '{system_id}'. "
                f"Disponíveis: {list(system_procedures)}"
            )
        return procedure

    def run(self, system_id: str, procedure_id: str, payload: object) -> Result[str, str]:
        operator = getpass.getuser()
        app_logger.info(
            "Iniciando: sistema=%s procedimento=%s operador=%s",
            system_id,
            procedure_id,
            operator,
        )

        try:
            system = self.get_system(system_id)
            procedure = self.get_procedure(system_id, procedure_id)
        except OrchestratorError as exc:
            return Result.fail(str(exc))

        validation = procedure.validate(payload)
        if not validation.success:
            return Result.fail(validation.error)  # type: ignore[arg-type]

        result: Result[str, str] = Result.fail("Execução não iniciada.")
        ctx = None

        try:
            ctx = browser_factory.open_context(system_id)

            if not system.is_logged_in(ctx):
                login_result = system.login(ctx)
                if not login_result.success:
                    return Result.fail(f"Falha no login em '{system_id}': {login_result.error}")

            result = procedure.execute(payload, ctx)

        except Exception as exc:
            app_logger.error("Erro inesperado em %s/%s: %s", system_id, procedure_id, exc)
            result = Result.fail(f"Erro inesperado: {exc}")

        finally:
            if ctx is not None:
                try:
                    system.logout(ctx)
                except Exception as exc:
                    app_logger.error("Erro no logout de '%s': %s", system_id, exc)
                browser_factory.close_context(system_id)

            payload_keys = list(vars(payload).keys()) if hasattr(payload, "__dict__") else []
            audit_logger.log_execution(
                AuditEntry(
                    system_id=system_id,
                    procedure_id=procedure_id,
                    operator=operator,
                    success=result.success,
                    payload_keys=payload_keys,
                    error=result.error if not result.success else None,
                )
            )

        return result

    def list_systems(self) -> list[str]:
        """Retorna os IDs de todos os sistemas registrados (RF-01)."""
        return list(AVAILABLE_SYSTEMS.keys())

    def list_procedures(self, system_id: str) -> list[str]:
        """Retorna os IDs dos procedimentos disponíveis para o sistema (RF-02)."""
        return list(AVAILABLE_PROCEDURES.get(system_id, {}).keys())


orchestrator: Orchestrator = Orchestrator()
