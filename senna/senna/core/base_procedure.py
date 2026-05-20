"""Contrato base para procedimentos do Senna."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from playwright.sync_api import BrowserContext

from senna.core.result import Result


class BaseProcedure(ABC):
    @property
    @abstractmethod
    def procedure_id(self) -> str:
        """Identificador único do procedimento em snake_case.

        Deve corresponder à chave em AVAILABLE_PROCEDURES.
        """

    @abstractmethod
    def validate(self, payload: Any) -> Result[None, str]:
        """
        Valida o payload contra as regras de negócio.
        Sem I/O, sem browser. Erros são exibidos inline na UI (RF-03).
        Retorna Result.ok(None) ou Result.fail(mensagem).
        """

    @abstractmethod
    def execute(self, payload: Any, ctx: BrowserContext) -> Result[str, str]:
        """
        Executa o procedimento no sistema-alvo.
        Chamado pelo Orchestrator somente após validate bem-sucedido e sessão ativa.
        Deve capturar todas as exceções Playwright e convertê-las em Result.fail.
        Retorna Result.ok(mensagem) ou Result.fail(mensagem).
        """

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(procedure_id={self.procedure_id!r})"
