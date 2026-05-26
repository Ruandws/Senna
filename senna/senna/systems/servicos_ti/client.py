"""Client do sistema Serviços TI — gerencia autenticação e sessão."""

from __future__ import annotations

import logging

from playwright.sync_api import BrowserContext

from senna.core.base_system import BaseSystem
from senna.core.exceptions import AuthenticationError
from senna.core.result import Result
from senna.systems.servicos_ti.pages.login_page import LoginPage

app_logger = logging.getLogger("senna.app")


class ServicoesTiSystem(BaseSystem):

    @property
    def system_id(self) -> str:
        return "servicos_ti"

    def login(self, ctx: BrowserContext) -> Result[None, str]:
        """Navega até o sistema e autentica a sessão."""
        try:
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            login_page = LoginPage(page)
            login_page.navigate()
            login_page.login()

            if login_page.is_login_page_visible():
                return Result.fail(
                    "Login falhou: o link 'Entrar' ainda está visível após a tentativa. "
                    "Verifique as credenciais em .env."
                )

            app_logger.info("Login bem-sucedido no sistema '%s'.", self.system_id)
            return Result.ok(None)

        except AuthenticationError as exc:
            return Result.fail(str(exc))
        except Exception as exc:
            return Result.fail(f"Erro inesperado durante o login: {exc}")

    def logout(self, ctx: BrowserContext) -> Result[None, str]:
        """Encerra a sessão — fecha todas as páginas do contexto."""
        try:
            for page in ctx.pages:
                page.close()
            app_logger.info("Logout concluído no sistema '%s'.", self.system_id)
            return Result.ok(None)
        except Exception as exc:
            return Result.fail(f"Erro ao encerrar sessão: {exc}")

    def is_logged_in(self, ctx: BrowserContext) -> bool:
        """
        Retorna True se a sessão estiver ativa.
        Critério: link 'Entrar' ausente na navegação.
        """
        try:
            if not ctx.pages:
                return False
            page = ctx.pages[0]
            login_page = LoginPage(page)
            return not login_page.is_login_page_visible()
        except Exception:
            return False