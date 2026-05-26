"""Page Object da página de detalhes do usuário — Serviços TI."""

from __future__ import annotations

from datetime import date

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from senna.core.exceptions import ExecutionError
from senna.systems.servicos_ti.config import BASE_URL, NAV_TIMEOUT, PAGE_TIMEOUT
from senna.systems.servicos_ti.locators import user_details_locators as loc


class UserDetailsPage:
    """Encapsula interações com a tela de detalhes de um usuário específico."""

    def __init__(self, page: Page) -> None:
        self._page = page

    def navigate(self, login: str) -> None:
        """Navega diretamente para a página de detalhes do usuário via URL.

        Args:
            login: Login do usuário no sistema (ex: 'Maria.Neri').
        """
        user_details_url = f"{BASE_URL}/#/usuarios/{login}"
        try:
            self._page.goto(user_details_url, wait_until="networkidle", timeout=NAV_TIMEOUT)
        except PlaywrightTimeoutError as exc:
            raise ExecutionError(
                procedure_id="extend_access",
                message=f"Timeout ao navegar para detalhes do usuário '{login}': {exc}",
            ) from exc

    def set_expiration_date(self, expiration_date: date) -> None:
        """Preenche o campo de data de expiração com a nova data.

        Args:
            expiration_date: Nova data de expiração no formato date.
        """
        date_str = expiration_date.strftime("%d/%m/%Y")
        try:
            date_input = self._page.locator(loc.EXPIRATION_DATE_INPUT)
            date_input.wait_for(state="visible", timeout=PAGE_TIMEOUT)
            date_input.clear()
            date_input.fill(date_str)
        except PlaywrightTimeoutError as exc:
            raise ExecutionError(
                procedure_id="extend_access",
                message=f"Timeout ao preencher data de expiração: {exc}",
            ) from exc

    def click_update(self) -> None:
        """Clica no botão 'Atualizar dados' e aguarda a resposta."""
        try:
            self._page.locator(loc.UPDATE_BUTTON).click()
            self._page.wait_for_load_state("networkidle", timeout=NAV_TIMEOUT)
        except PlaywrightTimeoutError as exc:
            raise ExecutionError(
                procedure_id="extend_access",
                message=f"Timeout ao clicar em 'Atualizar dados': {exc}",
            ) from exc

    def verify_date_saved(self, expected_date: date) -> bool:
        """Recarrega a página e verifica se a data foi persistida.

        Estratégia em camadas (sem toast de confirmação):
        1. Reload da página
        2. Lê o valor do input de data
        3. Compara com a data esperada

        Args:
            expected_date: Data que deveria ter sido salva.

        Returns:
            True se a data persistida confere com a esperada.
        """
        expected_str = expected_date.strftime("%d/%m/%Y")
        try:
            self._page.reload(wait_until="networkidle", timeout=NAV_TIMEOUT)
            date_input = self._page.locator(loc.EXPIRATION_DATE_INPUT)
            date_input.wait_for(state="visible", timeout=PAGE_TIMEOUT)
            persisted_value = date_input.input_value()
            return persisted_value.strip() == expected_str
        except PlaywrightTimeoutError as exc:
            raise ExecutionError(
                procedure_id="extend_access",
                message=f"Timeout ao verificar data salva: {exc}",
            ) from exc
