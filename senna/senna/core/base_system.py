"""Contrato base para sistemas do Senna."""

from __future__ import annotations

from abc import ABC, abstractmethod

from playwright.sync_api import BrowserContext

from senna.core.result import Result


class BaseSystem(ABC):
    @property
    @abstractmethod
    def system_id(self) -> str:
        """Identificador único do sistema em snake_case.

        Deve corresponder à chave em AVAILABLE_SYSTEMS.
        """

    @abstractmethod
    def login(self, ctx: BrowserContext) -> Result[None, str]:
        """Autentica a sessão. Retorna Result.ok(None) ou Result.fail(mensagem)."""

    @abstractmethod
    def logout(self, ctx: BrowserContext) -> Result[None, str]:
        """Encerra a sessão. Retorna Result.ok(None) ou Result.fail(mensagem)."""

    @abstractmethod
    def is_logged_in(self, ctx: BrowserContext) -> bool:
        """Retorna True se a sessão ainda estiver ativa."""

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(system_id={self.system_id!r})"
