"""Testes unitários para senna.systems.servicos_ti.pages.login_page.LoginPage

O QUÊ: valida a lógica e o comportamento de navegação, preenchimento e visibilidade
       do fluxo de login no sistema Serviços TI.
PARA QUÊ: garantir que falhas de rede, timeouts ou mudanças no estado de login sejam
          adequadamente capturadas e convertidas na exceção de negócio correspondente.
COMO: mocka o objeto Page e seus seletores internos, asseverando chamadas corretas e
      cenários de timeout.
"""

from __future__ import annotations

from unittest.mock import MagicMock

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
import pytest

from senna.core.exceptions import AuthenticationError
from senna.systems.servicos_ti.config import BASE_URL, NAV_TIMEOUT, PAGE_TIMEOUT
from senna.systems.servicos_ti.locators import login_locators as loc
from senna.systems.servicos_ti.pages.login_page import LoginPage


@pytest.fixture
def mock_page() -> MagicMock:
    """Retorna um mock da classe Page do Playwright."""
    return MagicMock(spec=Page)


def test_navigate_success(mock_page: MagicMock) -> None:
    """Deve navegar com sucesso e clicar no link de login."""
    mock_nav_link = MagicMock()
    mock_page.locator.return_value = mock_nav_link

    login_page = LoginPage(mock_page)
    login_page.navigate()

    mock_page.goto.assert_called_once_with(BASE_URL, wait_until="networkidle", timeout=NAV_TIMEOUT)
    mock_page.locator.assert_called_once_with(loc.NAV_ENTRAR_LINK)
    mock_nav_link.click.assert_called_once()
    mock_page.wait_for_load_state.assert_called_once_with("networkidle", timeout=NAV_TIMEOUT)


def test_navigate_timeout(mock_page: MagicMock) -> None:
    """Deve capturar timeout de navegação e levantar AuthenticationError."""
    mock_page.goto.side_effect = PlaywrightTimeoutError("Timeout simulado")

    login_page = LoginPage(mock_page)
    with pytest.raises(AuthenticationError) as exc_info:
        login_page.navigate()

    assert exc_info.value.system_id == "servicos_ti"
    assert "Timeout ao navegar para a página de login" in str(exc_info.value)


def test_login_success(mock_page: MagicMock) -> None:
    """Deve realizar login preenchendo credenciais e submetendo com sucesso."""
    mock_username_input = MagicMock()
    mock_password_input = MagicMock()
    mock_submit_button = MagicMock()

    mock_page.locator.side_effect = lambda selector: {
        loc.USERNAME_INPUT: mock_username_input,
        loc.PASSWORD_INPUT: mock_password_input,
        loc.SUBMIT_BUTTON: mock_submit_button,
    }.get(selector, MagicMock())

    login_page = LoginPage(mock_page)
    login_page.login()

    mock_username_input.fill.assert_called_once()
    mock_password_input.fill.assert_called_once()
    mock_submit_button.click.assert_called_once()
    mock_page.wait_for_load_state.assert_called_once_with("networkidle", timeout=NAV_TIMEOUT)


def test_login_timeout(mock_page: MagicMock) -> None:
    """Deve capturar timeout ao realizar login e levantar AuthenticationError."""
    mock_username_input = MagicMock()
    mock_username_input.fill.side_effect = PlaywrightTimeoutError("Timeout no input")
    mock_page.locator.return_value = mock_username_input

    login_page = LoginPage(mock_page)
    with pytest.raises(AuthenticationError) as exc_info:
        login_page.login()

    assert exc_info.value.system_id == "servicos_ti"
    assert "Timeout durante o login" in str(exc_info.value)


def test_is_login_page_visible_true(mock_page: MagicMock) -> None:
    """Deve retornar True se o botão de entrar estiver visível."""
    mock_nav_link = MagicMock()
    mock_nav_link.is_visible.return_value = True
    mock_page.locator.return_value = mock_nav_link

    login_page = LoginPage(mock_page)
    assert login_page.is_login_page_visible() is True
    mock_page.locator.assert_called_once_with(loc.NAV_ENTRAR_LINK)
    mock_nav_link.is_visible.assert_called_once_with(timeout=PAGE_TIMEOUT)


def test_is_login_page_visible_false_on_timeout(mock_page: MagicMock) -> None:
    """Deve retornar False se a checagem levantar um timeout."""
    mock_nav_link = MagicMock()
    mock_nav_link.is_visible.side_effect = PlaywrightTimeoutError("timeout")
    mock_page.locator.return_value = mock_nav_link

    login_page = LoginPage(mock_page)
    assert login_page.is_login_page_visible() is False
