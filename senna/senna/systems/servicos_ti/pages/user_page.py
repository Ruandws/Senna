"""Page Object da página de usuários — Serviços TI."""

from __future__ import annotations

import re

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from senna.core.exceptions import ExecutionError
from senna.core.models import UserSearchResult
from senna.systems.servicos_ti.config import NAV_TIMEOUT, PAGE_TIMEOUT
from senna.systems.servicos_ti.locators import user_locators as loc

_TABLE_FIRST_ROW_TIMEOUT: int = 2_000


class UserPage:

    def __init__(self, page: Page) -> None:
        self._page = page

    def navigate(self) -> None:
        """Navega para a página de pesquisa de usuários."""
        try:
            self._page.locator(loc.MENU_SEARCH_LINK).click()
            self._page.wait_for_load_state("networkidle", timeout=NAV_TIMEOUT)
        except PlaywrightTimeoutError as exc:
            raise ExecutionError(
                procedure_id="search_user_by_cpf",
                message=f"Timeout ao navegar para Pesquisa de usuário: {exc}",
            ) from exc

    def search_by_cpf(self, cpf: str) -> list[UserSearchResult]:
        """
        Pesquisa usuários pelo CPF e retorna todos os resultados encontrados.

        Cenários tratados:
          - 0 resultados → lista vazia
          - 1 resultado  → lista com um item
          - N resultados → lista completa

        Raises:
            ExecutionError: timeout aguardando resposta do Angular ou
                            falha inesperada ao interagir com a página.
        """
        try:
            search_input = self._page.locator(loc.SEARCH_INPUT)
            search_input.wait_for(state="visible", timeout=PAGE_TIMEOUT)
            search_input.clear()
            search_input.fill(cpf)
            self._page.locator(loc.SEARCH_BUTTON).click()
            self._page.wait_for_load_state("networkidle", timeout=NAV_TIMEOUT)
        except PlaywrightTimeoutError as exc:
            raise ExecutionError(
                procedure_id="search_user_by_cpf",
                message=f"Timeout aguardando resposta da pesquisa por CPF '{cpf}': {exc}",
            ) from exc

        return self._extract_results()

    def _extract_results(self) -> list[UserSearchResult]:
        """Extrai nome e login de cada linha da tabela de resultados."""
        rows = self._page.locator(loc.RESULT_ROWS)

        try:
            rows.first.wait_for(state="attached", timeout=_TABLE_FIRST_ROW_TIMEOUT)
        except PlaywrightTimeoutError:
            return []

        results: list[UserSearchResult] = []

        for i in range(rows.count()):
            row = rows.nth(i)
            nome = row.locator(loc.ROW_NOME).inner_text().strip()
            href = row.locator(loc.ROW_LINK).get_attribute("href") or ""
            login = self._parse_login_from_href(href)

            if nome and login:
                results.append(UserSearchResult(nome=nome, login=login))

        return results

    @staticmethod
    def _parse_login_from_href(href: str) -> str:
        """Extrai o login do href no formato '#/usuarios/LOGIN'."""
        match = re.search(r"#/usuarios/(.+)$", href)
        return match.group(1) if match else ""