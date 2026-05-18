"""
Testes unitários para senna.core.config.Config

O QUÊ: valida a fusão de configurações, validação fail-fast de credenciais
       e o funcionamento de get(), require() e debug_browser().
PARA QUÊ: garantir que qualquer falha na injeção de ambiente ou regras de precedência
           seja identificada imediatamente.
COMO: usa pytest com monkeypatch para simular o carregamento de arquivos e ambiente
       sem depender de estados reais de arquivos no sistema.
"""

from __future__ import annotations

import pytest

from senna.core.config import (
    _REQUIRED_CREDENTIALS,
    Config,
    _merge,
    _validate_credentials,
)
from senna.core.exceptions import MissingCredentialError

# =============================================================================
# Testes das funções auxiliares
# =============================================================================


def test_merge() -> None:
    """_merge deve mesclar settings e env, ignorando None do env."""
    settings = {"timeout": 30000, "log_dir": "logs/audit"}
    env = {"timeout": "60000", "log_dir": None, "NEW_VAR": "value"}

    merged = _merge(settings, env)

    assert merged["timeout"] == "60000"
    assert merged["log_dir"] == "logs/audit"
    assert merged["NEW_VAR"] == "value"


def test_validate_credentials_missing() -> None:
    """_validate_credentials deve levantar erro se faltar credencial obrigatória."""
    config_data = {"SERVICOS_TI_URL": "http://example.com"}

    with pytest.raises(MissingCredentialError, match="SERVICOS_TI_USER"):
        _validate_credentials(config_data)


def test_validate_credentials_success() -> None:
    """_validate_credentials deve passar quando todas credenciais estiverem preenchidas."""
    config_data = {k: "dummy_value" for k in _REQUIRED_CREDENTIALS}

    # Não deve levantar exceção
    _validate_credentials(config_data)


# =============================================================================
# Testes da classe Config
# =============================================================================


def test_config_init_and_get(monkeypatch: pytest.MonkeyPatch) -> None:
    """Config deve carregar, mesclar e disponibilizar valores via get()."""
    monkeypatch.setattr(
        "senna.core.config._load_settings",
        lambda: {"browser": {"timeout": 30000}},
    )
    monkeypatch.setattr(
        "senna.core.config._load_env", lambda: {k: "val" for k in _REQUIRED_CREDENTIALS}
    )

    cfg = Config()

    assert cfg.get("SERVICOS_TI_URL") == "val"
    assert cfg.get("browser") == {"timeout": 30000}
    assert cfg.get("NON_EXISTENT", "default_val") == "default_val"


def test_config_require_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """require() deve retornar o valor caso ele exista."""
    monkeypatch.setattr("senna.core.config._load_settings", lambda: {})
    monkeypatch.setattr(
        "senna.core.config._load_env", lambda: {k: "val" for k in _REQUIRED_CREDENTIALS}
    )

    cfg = Config()

    assert cfg.require("SERVICOS_TI_URL") == "val"


def test_config_require_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """require() deve levantar erro se o valor não existir ou estiver vazio."""
    monkeypatch.setattr("senna.core.config._load_settings", lambda: {})
    monkeypatch.setattr(
        "senna.core.config._load_env", lambda: {k: "val" for k in _REQUIRED_CREDENTIALS}
    )

    cfg = Config()

    with pytest.raises(MissingCredentialError, match="Configuração obrigatória ausente"):
        cfg.require("NON_EXISTENT")


def test_config_debug_browser(monkeypatch: pytest.MonkeyPatch) -> None:
    """debug_browser() deve verificar corretamente se a variável DEBUG_BROWSER é verdadeira."""
    monkeypatch.setattr("senna.core.config._load_settings", lambda: {})

    # Caso 1: DEBUG_BROWSER = true
    monkeypatch.setattr(
        "senna.core.config._load_env",
        lambda: {**{k: "val" for k in _REQUIRED_CREDENTIALS}, "DEBUG_BROWSER": "true"},
    )
    cfg_true = Config()
    assert cfg_true.debug_browser() is True

    # Caso 2: DEBUG_BROWSER = false
    monkeypatch.setattr(
        "senna.core.config._load_env",
        lambda: {**{k: "val" for k in _REQUIRED_CREDENTIALS}, "DEBUG_BROWSER": "false"},
    )
    cfg_false = Config()
    assert cfg_false.debug_browser() is False
