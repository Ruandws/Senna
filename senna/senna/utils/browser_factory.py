"""
Gerenciamento do Playwright e BrowserContext isolado por sistema.

Estratégia:
  - Um único processo de browser (Chromium) é compartilhado por toda a sessão.
  - Cada sistema recebe seu próprio BrowserContext — cookies, sessões e storage
    completamente isolados entre sistemas (RF-08).
  - O browser é iniciado na primeira abertura de contexto e encerrado quando
    todos os contextos forem fechados (ou via close_all).

Uso:
    from senna.utils.browser_factory import browser_factory
    from playwright.sync_api import BrowserContext

    ctx: BrowserContext = browser_factory.open_context("servicos_ti")
    try:
        ...
    finally:
        browser_factory.close_context("servicos_ti")
"""

from __future__ import annotations

import logging

from playwright.sync_api import Browser, BrowserContext, Playwright, sync_playwright

from senna.core.config import config
from senna.core.exceptions import BrowserError

app_logger = logging.getLogger("senna.app")


class BrowserFactory:
    """
    Gerencia o ciclo de vida do browser e dos contextos isolados por sistema.

    - Um único browser Chromium é compartilhado por toda a aplicação.
    - Cada system_id mapeia para exatamente um BrowserContext ativo.
    - Contextos são criados sob demanda e encerrados explicitamente.

    Não instanciar diretamente — usar a instância singleton `browser_factory`.
    """

    def __init__(self) -> None:
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._contexts: dict[str, BrowserContext] = {}

    # ---------------------------------------------------------------------------
    # Browser — ciclo de vida interno
    # ---------------------------------------------------------------------------

    def _ensure_browser(self) -> Browser:
        """
        Inicia o Playwright e o browser se ainda não estiverem ativos.
        Chamado automaticamente na abertura do primeiro contexto.
        """
        if self._browser is not None and self._browser.is_connected():
            return self._browser

        try:
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(
                headless=not config.debug_browser(),
                args=["--no-sandbox"],  # necessário em alguns ambientes Windows
            )
            app_logger.info("Browser Chromium iniciado (headless=%s)", not config.debug_browser())
            return self._browser
        except Exception as exc:
            raise BrowserError(f"Falha ao iniciar o browser Chromium: {exc}") from exc

    # ---------------------------------------------------------------------------
    # Contextos — API pública
    # ---------------------------------------------------------------------------

    def open_context(self, system_id: str) -> BrowserContext:
        """
        Abre e retorna um BrowserContext isolado para o sistema informado.

        Se já existir um contexto ativo para o system_id, retorna o existente
        sem criar um novo — garantindo que cada sistema tenha exatamente uma
        sessão simultânea.

        Args:
            system_id: identificador do sistema (ex: "servicos_ti").

        Returns:
            BrowserContext isolado pronto para uso.

        Raises:
            BrowserError: se o browser não puder ser iniciado.
        """
        if system_id in self._contexts:
            app_logger.debug("Reutilizando contexto existente para '%s'", system_id)
            return self._contexts[system_id]

        browser = self._ensure_browser()

        try:
            timeout_ms = int(config.get("browser.timeout", 30_000))

            ctx = browser.new_context(
                locale="pt-BR",
                timezone_id="America/Sao_Paulo",
            )
            ctx.set_default_timeout(timeout_ms)
            ctx.set_default_navigation_timeout(
                int(config.get("browser.navigation_timeout", 60_000))
            )

            self._contexts[system_id] = ctx
            app_logger.info("BrowserContext aberto para sistema '%s'", system_id)
            return ctx

        except Exception as exc:
            raise BrowserError(f"Falha ao abrir BrowserContext para '{system_id}': {exc}") from exc

    def close_context(self, system_id: str) -> None:
        """
        Fecha e remove o BrowserContext do sistema informado.

        Chamado ao finalizar todos os procedimentos do sistema ou em caso
        de erro não recuperável (RF-08).

        Se não houver contexto ativo para o system_id, a chamada é ignorada.
        """
        ctx = self._contexts.pop(system_id, None)
        if ctx is None:
            app_logger.debug("close_context: nenhum contexto ativo para '%s'", system_id)
            return

        try:
            ctx.close()
            app_logger.info("BrowserContext encerrado para sistema '%s'", system_id)
        except Exception as exc:
            # Falha no fechamento é registrada mas não propagada —
            # não deve impedir o fluxo de auditoria e exibição de resultado.
            app_logger.error("Erro ao fechar BrowserContext de '%s': %s", system_id, exc)

        self._shutdown_if_idle()

    def close_all(self) -> None:
        """
        Fecha todos os contextos ativos e encerra o browser.

        Deve ser chamado no encerramento da aplicação (main.py teardown).
        """
        for system_id in list(self._contexts):
            self.close_context(system_id)

        self._shutdown_browser()

    def has_context(self, system_id: str) -> bool:
        """Retorna True se houver um BrowserContext ativo para o sistema."""
        return system_id in self._contexts

    # ---------------------------------------------------------------------------
    # Shutdown interno
    # ---------------------------------------------------------------------------

    def _shutdown_if_idle(self) -> None:
        """Encerra o browser quando não há mais contextos ativos."""
        if not self._contexts:
            self._shutdown_browser()

    def _shutdown_browser(self) -> None:
        """Encerra browser e Playwright, liberando recursos do processo."""
        if self._browser is not None:
            try:
                self._browser.close()
                app_logger.info("Browser Chromium encerrado.")
            except Exception as exc:
                app_logger.error("Erro ao encerrar browser: %s", exc)
            finally:
                self._browser = None

        if self._playwright is not None:
            try:
                self._playwright.stop()
            except Exception as exc:
                app_logger.error("Erro ao encerrar Playwright: %s", exc)
            finally:
                self._playwright = None

    # ---------------------------------------------------------------------------
    # Representação
    # ---------------------------------------------------------------------------

    def __repr__(self) -> str:
        active = list(self._contexts.keys())
        return f"BrowserFactory(active_contexts={active})"


# Instância singleton — importar sempre desta forma:
#   from senna.utils.browser_factory import browser_factory
browser_factory: BrowserFactory = BrowserFactory()
