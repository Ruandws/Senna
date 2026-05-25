"""Page Object da página de login — Serviços TI."""

from __future__ import annotations

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from senna.core.exceptions import AuthenticationError
from senna.systems.servicos_ti.config import (
    BASE_URL,
    NAV_TIMEOUT,
    PAGE_TIMEOUT,
    PASSWORD,
    USERNAME,
)
from senna.systems.servicos_ti.locators import login_locators as loc


class LoginPage:

    def __init__(self, page: Page) -> None:
        self._page = page

    def navigate(self) -> None:
        """Navega até a página inicial e acessa o formulário de login."""
        try:
            self._page.goto(BASE_URL, wait_until="networkidle", timeout=NAV_TIMEOUT)
            self._page.locator(loc.NAV_ENTRAR_LINK).click()
            self._page.wait_for_load_state("networkidle", timeout=NAV_TIMEOUT)
        except PlaywrightTimeoutError as exc:
            raise AuthenticationError(
                system_id="servicos_ti",
                message=f"Timeout ao navegar para a página de login: {exc}",
            ) from exc

    def login(self) -> None:
        """Preenche as credenciais e submete o formulário de login."""
        try:
            self._page.locator(loc.USERNAME_INPUT).fill(USERNAME)
            self._page.locator(loc.PASSWORD_INPUT).fill(PASSWORD)
            self._page.locator(loc.SUBMIT_BUTTON).click()
            self._page.wait_for_load_state("networkidle", timeout=NAV_TIMEOUT)
        except PlaywrightTimeoutError as exc:
            raise AuthenticationError(
                system_id="servicos_ti",
                message=f"Timeout durante o login: {exc}",
            ) from exc

    def is_login_page_visible(self) -> bool:
        """Retorna True se o link 'Entrar' estiver visível na navegação — indica sessão inativa."""
        try:
            return self._page.locator(loc.NAV_ENTRAR_LINK).is_visible(timeout=PAGE_TIMEOUT)
        except PlaywrightTimeoutError:
            return False