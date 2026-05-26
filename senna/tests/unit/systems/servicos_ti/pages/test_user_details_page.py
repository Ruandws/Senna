"""Testes unitários para senna.systems.servicos_ti.pages.user_details_page.UserDetailsPage"""

from __future__ import annotations

import datetime
from unittest.mock import MagicMock

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
import pytest

from senna.core.exceptions import ExecutionError
from senna.systems.servicos_ti.config import BASE_URL, NAV_TIMEOUT, PAGE_TIMEOUT
from senna.systems.servicos_ti.locators import user_details_locators as loc
from senna.systems.servicos_ti.pages.user_details_page import UserDetailsPage


@pytest.fixture
def mock_page() -> MagicMock:
    return MagicMock(spec=Page)


def test_navigate_success(mock_page: MagicMock) -> None:
    page = UserDetailsPage(mock_page)
    page.navigate("maria.neri")

    mock_page.goto.assert_called_once_with(
        f"{BASE_URL}/#/usuarios/maria.neri",
        wait_until="networkidle",
        timeout=NAV_TIMEOUT,
    )


def test_navigate_timeout(mock_page: MagicMock) -> None:
    mock_page.goto.side_effect = PlaywrightTimeoutError("timeout")
    page = UserDetailsPage(mock_page)

    with pytest.raises(ExecutionError) as exc_info:
        page.navigate("maria.neri")

    assert exc_info.value.procedure_id == "extend_access"
    assert "Timeout ao navegar para detalhes do usuário 'maria.neri'" in str(exc_info.value)


def test_set_expiration_date_success(mock_page: MagicMock) -> None:
    mock_input = MagicMock()
    mock_page.locator.return_value = mock_input

    page = UserDetailsPage(mock_page)
    dt = datetime.date(2026, 12, 31)
    page.set_expiration_date(dt)

    mock_page.locator.assert_called_once_with(loc.EXPIRATION_DATE_INPUT)
    mock_input.wait_for.assert_called_once_with(state="visible", timeout=PAGE_TIMEOUT)
    mock_input.clear.assert_called_once()
    mock_input.fill.assert_called_once_with("31/12/2026")


def test_set_expiration_date_timeout(mock_page: MagicMock) -> None:
    mock_input = MagicMock()
    mock_input.wait_for.side_effect = PlaywrightTimeoutError("timeout")
    mock_page.locator.return_value = mock_input

    page = UserDetailsPage(mock_page)
    dt = datetime.date(2026, 12, 31)

    with pytest.raises(ExecutionError) as exc_info:
        page.set_expiration_date(dt)

    assert "Timeout ao preencher data de expiração" in str(exc_info.value)


def test_click_update_success(mock_page: MagicMock) -> None:
    mock_button = MagicMock()
    mock_page.locator.return_value = mock_button

    page = UserDetailsPage(mock_page)
    page.click_update()

    mock_page.locator.assert_called_once_with(loc.UPDATE_BUTTON)
    mock_button.click.assert_called_once()
    mock_page.wait_for_load_state.assert_called_once_with("networkidle", timeout=NAV_TIMEOUT)


def test_click_update_timeout(mock_page: MagicMock) -> None:
    mock_page.wait_for_load_state.side_effect = PlaywrightTimeoutError("timeout")
    page = UserDetailsPage(mock_page)

    with pytest.raises(ExecutionError) as exc_info:
        page.click_update()

    assert "Timeout ao clicar em 'Atualizar dados'" in str(exc_info.value)


def test_verify_date_saved_success(mock_page: MagicMock) -> None:
    mock_input = MagicMock()
    mock_input.input_value.return_value = "31/12/2026 "
    mock_page.locator.return_value = mock_input

    page = UserDetailsPage(mock_page)
    dt = datetime.date(2026, 12, 31)

    result = page.verify_date_saved(dt)

    assert result is True
    mock_page.reload.assert_called_once_with(wait_until="networkidle", timeout=NAV_TIMEOUT)
    mock_page.locator.assert_called_once_with(loc.EXPIRATION_DATE_INPUT)
    mock_input.wait_for.assert_called_once_with(state="visible", timeout=PAGE_TIMEOUT)


def test_verify_date_saved_failure(mock_page: MagicMock) -> None:
    mock_input = MagicMock()
    mock_input.input_value.return_value = "01/01/2025"
    mock_page.locator.return_value = mock_input

    page = UserDetailsPage(mock_page)
    dt = datetime.date(2026, 12, 31)

    result = page.verify_date_saved(dt)

    assert result is False


def test_verify_date_saved_timeout(mock_page: MagicMock) -> None:
    mock_page.reload.side_effect = PlaywrightTimeoutError("timeout")
    page = UserDetailsPage(mock_page)
    dt = datetime.date(2026, 12, 31)

    with pytest.raises(ExecutionError) as exc_info:
        page.verify_date_saved(dt)

    assert "Timeout ao verificar data salva" in str(exc_info.value)
