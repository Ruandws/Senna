"""
Testes unitários para senna.utils.browser_factory.BrowserFactory

O QUÊ: valida o gerenciador de ciclo de vida do Playwright e contextos do browser.
PARA QUÊ: garantir que os contextos de navegação por sistema sejam abertos de forma
          isolada e que o browser seja fechado apropriadamente.
COMO: mocka o sync_playwright e seus objetos retornados (Browser, BrowserContext),
      verificando chamadas e controle de estados internos.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from playwright.sync_api import Browser, BrowserContext, Playwright
import pytest

from senna.core.exceptions import BrowserError
from senna.utils.browser_factory import BrowserFactory, browser_factory


@pytest.fixture(autouse=True)
def reset_browser_factory() -> None:
    """Garante que o estado interno do browser_factory seja limpo antes/depois de cada teste."""
    # Como browser_factory é um singleton importado, limpamos seus atributos
    browser_factory._playwright = None
    browser_factory._browser = None
    browser_factory._contexts = {}


def test_browser_factory_repr() -> None:
    """repr() de BrowserFactory deve listar os contextos ativos."""
    factory = BrowserFactory()
    assert repr(factory) == "BrowserFactory(active_contexts=[])"

    mock_context = MagicMock(spec=BrowserContext)
    factory._contexts["sistema_a"] = mock_context
    assert repr(factory) == "BrowserFactory(active_contexts=['sistema_a'])"


def test_has_context() -> None:
    """has_context deve retornar a presença do contexto mapeado pelo id do sistema."""
    factory = BrowserFactory()
    assert factory.has_context("sistema_a") is False

    mock_context = MagicMock(spec=BrowserContext)
    factory._contexts["sistema_a"] = mock_context
    assert factory.has_context("sistema_a") is True


@patch("senna.utils.browser_factory.sync_playwright")
@patch("senna.utils.browser_factory.config")
def test_open_context_new_browser(mock_config: MagicMock, mock_sync_playwright: MagicMock) -> None:
    """open_context deve instanciar o browser e o Playwright se não existirem."""
    mock_config.debug_browser.return_value = False
    mock_config.get.side_effect = lambda key, default=None: {
        "browser.timeout": 30000,
        "browser.navigation_timeout": 60000,
    }.get(key, default)

    mock_playwright_inst = MagicMock(spec=Playwright)
    mock_browser_inst = MagicMock(spec=Browser)
    mock_context_inst = MagicMock(spec=BrowserContext)

    mock_sync_playwright.return_value.start.return_value = mock_playwright_inst
    mock_playwright_inst.chromium.launch.return_value = mock_browser_inst
    mock_browser_inst.new_context.return_value = mock_context_inst
    mock_browser_inst.is_connected.return_value = True

    factory = BrowserFactory()
    ctx = factory.open_context("sistema_a")

    assert ctx is mock_context_inst
    assert factory.has_context("sistema_a") is True
    mock_sync_playwright.return_value.start.assert_called_once()
    mock_playwright_inst.chromium.launch.assert_called_once_with(
        headless=True,
        args=["--no-sandbox"],
    )
    mock_browser_inst.new_context.assert_called_once_with(
        locale="pt-BR",
        timezone_id="America/Sao_Paulo",
    )
    mock_context_inst.set_default_timeout.assert_called_once_with(30000)
    mock_context_inst.set_default_navigation_timeout.assert_called_once_with(60000)


@patch("senna.utils.browser_factory.sync_playwright")
def test_open_context_reutiliza_existente(mock_sync_playwright: MagicMock) -> None:
    """open_context deve reutilizar o contexto de um sistema se ele já estiver aberto."""
    factory = BrowserFactory()
    mock_context = MagicMock(spec=BrowserContext)
    factory._contexts["sistema_a"] = mock_context

    ctx = factory.open_context("sistema_a")
    assert ctx is mock_context
    mock_sync_playwright.assert_not_called()


@patch("senna.utils.browser_factory.sync_playwright")
def test_open_context_raises_browser_error_on_failure(mock_sync_playwright: MagicMock) -> None:
    """open_context deve levantar BrowserError se o Playwright ou browser falhar ao iniciar."""
    mock_sync_playwright.return_value.start.side_effect = Exception("Erro Playwright")

    factory = BrowserFactory()
    with pytest.raises(BrowserError, match="Falha ao iniciar o browser Chromium"):
        factory.open_context("sistema_a")


@patch("senna.utils.browser_factory.sync_playwright")
@patch("senna.utils.browser_factory.config")
def test_open_context_raises_browser_error_on_context_failure(
    mock_config: MagicMock, mock_sync_playwright: MagicMock
) -> None:
    """open_context deve levantar BrowserError se a criação do contexto falhar."""
    mock_config.debug_browser.return_value = False
    mock_playwright_inst = MagicMock(spec=Playwright)
    mock_browser_inst = MagicMock(spec=Browser)

    mock_sync_playwright.return_value.start.return_value = mock_playwright_inst
    mock_playwright_inst.chromium.launch.return_value = mock_browser_inst
    mock_browser_inst.new_context.side_effect = Exception("Erro de contexto")
    mock_browser_inst.is_connected.return_value = True

    factory = BrowserFactory()
    with pytest.raises(BrowserError, match="Falha ao abrir BrowserContext"):
        factory.open_context("sistema_a")


def test_close_context_non_existing() -> None:
    """close_context deve simplesmente ignorar se o contexto solicitado não existir."""
    factory = BrowserFactory()
    # Não deve levantar exceção
    factory.close_context("sistema_a")


def test_close_context_closes_and_shutdowns_browser_when_idle() -> None:
    """close_context deve fechar o contexto e fechar o browser se for o último ativo."""
    factory = BrowserFactory()
    mock_playwright = MagicMock(spec=Playwright)
    mock_browser = MagicMock(spec=Browser)
    mock_context = MagicMock(spec=BrowserContext)

    factory._playwright = mock_playwright
    factory._browser = mock_browser
    factory._contexts["sistema_a"] = mock_context

    factory.close_context("sistema_a")

    mock_context.close.assert_called_once()
    mock_browser.close.assert_called_once()
    mock_playwright.stop.assert_called_once()
    assert factory._browser is None
    assert factory._playwright is None
    assert "sistema_a" not in factory._contexts


def test_close_context_does_not_shutdown_browser_if_not_idle() -> None:
    """close_context não deve desligar o browser se ainda houverem outros contextos ativos."""
    factory = BrowserFactory()
    mock_playwright = MagicMock(spec=Playwright)
    mock_browser = MagicMock(spec=Browser)
    mock_context_a = MagicMock(spec=BrowserContext)
    mock_context_b = MagicMock(spec=BrowserContext)

    factory._playwright = mock_playwright
    factory._browser = mock_browser
    factory._contexts["sistema_a"] = mock_context_a
    factory._contexts["sistema_b"] = mock_context_b

    factory.close_context("sistema_a")

    mock_context_a.close.assert_called_once()
    mock_browser.close.assert_not_called()
    mock_playwright.stop.assert_not_called()
    assert factory._browser is mock_browser
    assert "sistema_a" not in factory._contexts
    assert "sistema_b" in factory._contexts


def test_close_context_absorbs_context_exceptions() -> None:
    """close_context deve capturar erros ao fechar o contexto, mas ainda assim limpar."""
    factory = BrowserFactory()
    mock_playwright = MagicMock(spec=Playwright)
    mock_browser = MagicMock(spec=Browser)
    mock_context = MagicMock(spec=BrowserContext)
    mock_context.close.side_effect = Exception("Erro ao fechar")

    factory._playwright = mock_playwright
    factory._browser = mock_browser
    factory._contexts["sistema_a"] = mock_context

    # Não deve subir exceção
    factory.close_context("sistema_a")

    mock_context.close.assert_called_once()
    mock_browser.close.assert_called_once()
    mock_playwright.stop.assert_called_once()
    assert "sistema_a" not in factory._contexts


def test_close_all() -> None:
    """close_all deve fechar todos os contextos e o browser."""
    factory = BrowserFactory()
    mock_playwright = MagicMock(spec=Playwright)
    mock_browser = MagicMock(spec=Browser)
    mock_context_a = MagicMock(spec=BrowserContext)
    mock_context_b = MagicMock(spec=BrowserContext)

    factory._playwright = mock_playwright
    factory._browser = mock_browser
    factory._contexts["sistema_a"] = mock_context_a
    factory._contexts["sistema_b"] = mock_context_b

    factory.close_all()

    mock_context_a.close.assert_called_once()
    mock_context_b.close.assert_called_once()
    mock_browser.close.assert_called_once()
    mock_playwright.stop.assert_called_once()
    assert not factory._contexts


def test_ensure_browser_returns_existing_if_connected() -> None:
    """_ensure_browser deve retornar o browser existente se ele já estiver conectado."""
    factory = BrowserFactory()
    mock_browser = MagicMock(spec=Browser)
    mock_browser.is_connected.return_value = True
    factory._browser = mock_browser

    assert factory._ensure_browser() is mock_browser


def test_shutdown_browser_handles_close_exception() -> None:
    """_shutdown_browser deve capturar erros ao fechar o browser e prosseguir."""
    factory = BrowserFactory()
    mock_browser = MagicMock(spec=Browser)
    mock_browser.close.side_effect = Exception("erro close")
    factory._browser = mock_browser

    factory._shutdown_browser()
    assert factory._browser is None


def test_shutdown_browser_handles_playwright_stop_exception() -> None:
    """_shutdown_browser deve capturar erros ao parar o Playwright e prosseguir."""
    factory = BrowserFactory()
    mock_playwright = MagicMock(spec=Playwright)
    mock_playwright.stop.side_effect = Exception("erro stop")
    factory._playwright = mock_playwright

    factory._shutdown_browser()
    assert factory._playwright is None
