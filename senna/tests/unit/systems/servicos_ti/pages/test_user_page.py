"""Testes unitários para senna.systems.servicos_ti.pages.user_page.UserPage

O QUÊ: valida a lógica e o comportamento de busca por CPF, navegação lateral e
       extração semântica de resultados de tabelas no sistema Serviços TI.
PARA QUÊ: assegurar o correto desempacotamento de usuários retornados em tela e o
          tratamento resiliente de timeouts e falhas de rede.
COMO: mocka o objeto Page, seletores de linha da tabela Angular e assevera o parse de logins.
"""

from __future__ import annotations

from unittest.mock import MagicMock

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
import pytest

from senna.core.exceptions import ExecutionError
from senna.systems.servicos_ti.config import NAV_TIMEOUT, PAGE_TIMEOUT
from senna.systems.servicos_ti.locators import user_locators as loc
from senna.systems.servicos_ti.pages.user_page import UserPage


@pytest.fixture
def mock_page() -> MagicMock:
    """Fixture que retorna um mock completo de Page."""
    return MagicMock(spec=Page)


def test_navigate_success(mock_page: MagicMock) -> None:
    """Deve navegar com sucesso para a tela de usuários."""
    mock_link = MagicMock()
    mock_page.locator.return_value = mock_link

    user_page = UserPage(mock_page)
    user_page.navigate()

    mock_page.locator.assert_called_once_with(loc.MENU_SEARCH_LINK)
    mock_link.click.assert_called_once()
    mock_page.wait_for_load_state.assert_called_once_with("networkidle", timeout=NAV_TIMEOUT)


def test_navigate_timeout(mock_page: MagicMock) -> None:
    """Deve falhar e levantar ExecutionError em caso de timeout de navegação."""
    mock_link = MagicMock()
    mock_link.click.side_effect = PlaywrightTimeoutError("timeout")
    mock_page.locator.return_value = mock_link

    user_page = UserPage(mock_page)
    with pytest.raises(ExecutionError) as exc_info:
        user_page.navigate()

    assert exc_info.value.procedure_id == "search_user_by_cpf"
    assert "Timeout ao navegar para Pesquisa de usuário" in str(exc_info.value)


def test_search_by_cpf_success(mock_page: MagicMock) -> None:
    """Deve preencher o formulário de pesquisa e clicar em buscar com sucesso."""
    mock_input = MagicMock()
    mock_button = MagicMock()

    mock_page.locator.side_effect = lambda selector: {
        loc.SEARCH_INPUT: mock_input,
        loc.SEARCH_BUTTON: mock_button,
    }.get(selector, MagicMock())

    # Mock _extract_results to avoid deep mock of table in this specific test
    user_page = UserPage(mock_page)
    user_page._extract_results = MagicMock(return_value=[])  # type: ignore[method-assign]

    results = user_page.search_by_cpf("12345678901")

    assert results == []
    mock_page.locator.assert_any_call(loc.SEARCH_INPUT)
    mock_input.wait_for.assert_called_once_with(state="visible", timeout=PAGE_TIMEOUT)
    mock_input.clear.assert_called_once()
    mock_input.fill.assert_called_once_with("12345678901")
    mock_page.locator.assert_any_call(loc.SEARCH_BUTTON)
    mock_button.click.assert_called_once()
    mock_page.wait_for_load_state.assert_called_once_with("networkidle", timeout=NAV_TIMEOUT)


def test_search_by_cpf_timeout(mock_page: MagicMock) -> None:
    """Deve falhar e levantar ExecutionError em caso de timeout na busca."""
    mock_input = MagicMock()
    mock_input.wait_for.side_effect = PlaywrightTimeoutError("timeout")
    mock_page.locator.return_value = mock_input

    user_page = UserPage(mock_page)
    with pytest.raises(ExecutionError) as exc_info:
        user_page.search_by_cpf("12345678901")

    assert exc_info.value.procedure_id == "search_user_by_cpf"
    assert "Timeout aguardando resposta da pesquisa por CPF" in str(exc_info.value)


def test_extract_results_success(mock_page: MagicMock) -> None:
    """Deve extrair os resultados encontrados na tabela com sucesso."""
    mock_rows = MagicMock()
    mock_rows.count.return_value = 2

    mock_row_1 = MagicMock()
    mock_row_1.locator(loc.ROW_NOME).inner_text.return_value = "Maria Silva"
    mock_row_1.locator(loc.ROW_LINK).get_attribute.return_value = "#/usuarios/msilva"

    mock_row_2 = MagicMock()
    mock_row_2.locator(loc.ROW_NOME).inner_text.return_value = "João Sousa"
    mock_row_2.locator(loc.ROW_LINK).get_attribute.return_value = "#/usuarios/jsousa"

    mock_rows.nth.side_effect = [mock_row_1, mock_row_2]
    mock_page.locator.return_value = mock_rows

    user_page = UserPage(mock_page)
    results = user_page._extract_results()

    assert len(results) == 2
    assert results[0].nome == "Maria Silva"
    assert results[0].login == "msilva"
    assert results[1].nome == "João Sousa"
    assert results[1].login == "jsousa"
    mock_rows.first.wait_for.assert_called_once_with(state="attached", timeout=2000)


def test_extract_results_empty_on_timeout(mock_page: MagicMock) -> None:
    """Deve retornar lista vazia se a tabela de resultados sofrer timeout ao carregar."""
    mock_rows = MagicMock()
    mock_rows.first.wait_for.side_effect = PlaywrightTimeoutError("timeout")
    mock_page.locator.return_value = mock_rows

    user_page = UserPage(mock_page)
    results = user_page._extract_results()

    assert results == []


def test_parse_login_from_href() -> None:
    """Deve validar os padrões suportados pelo parser estático de login."""
    assert UserPage._parse_login_from_href("#/usuarios/roberto.almeida") == "roberto.almeida"
    assert UserPage._parse_login_from_href("#/usuarios/ana_maria") == "ana_maria"
    assert UserPage._parse_login_from_href("http://outro/usuarios/invalido") == ""
