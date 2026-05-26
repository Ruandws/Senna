"""Configurações específicas do sistema Serviços TI."""

from __future__ import annotations

from senna.core.config import config

# ---------------------------------------------------------------------------
# Credenciais e URLs
# ---------------------------------------------------------------------------

BASE_URL: str = str(config.require("SERVICOS_TI_URL"))
USERNAME: str = str(config.require("SERVICOS_TI_USER"))
PASSWORD: str = str(config.require("SERVICOS_TI_PASSWORD"))

# ---------------------------------------------------------------------------
# Timeouts (ms)
# ---------------------------------------------------------------------------

PAGE_TIMEOUT: int = int(config.get("browser.timeout", 30_000))
NAV_TIMEOUT: int = int(config.get("browser.navigation_timeout", 60_000))

# ---------------------------------------------------------------------------
# Rotas
# ---------------------------------------------------------------------------

ROUTE_USUARIOS: str = f"{BASE_URL}/#/usuarios"