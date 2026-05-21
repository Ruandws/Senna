"""
Gerenciamento de configurações do Senna.

Estratégia de carregamento (ordem de precedência, menor → maior):
  1. settings.toml  — valores padrão versionados (não contém segredos)
  2. .env           — sobrescreve apenas variáveis sensíveis/ambiente-específicas

Variáveis obrigatórias ausentes levantam MissingCredentialError na importação,
impedindo que a aplicação inicialize em estado inválido (RF-06).
"""

from __future__ import annotations

from pathlib import Path
import tomllib

from dotenv import dotenv_values

from senna.core.exceptions import MissingCredentialError

# ---------------------------------------------------------------------------
# Caminhos base
# ---------------------------------------------------------------------------

_ROOT: Path = Path(__file__).resolve().parents[2]  # raiz do repositório
_SETTINGS_FILE: Path = _ROOT / "settings.toml"
_ENV_FILE: Path = _ROOT / ".env"

# ---------------------------------------------------------------------------
# Variáveis obrigatórias por sistema
# A ausência de qualquer uma delas na inicialização levanta MissingCredentialError.
# ---------------------------------------------------------------------------

_REQUIRED_CREDENTIALS: tuple[str, ...] = (
    "SERVICOS_TI_URL",
    "SERVICOS_TI_USER",
    "SERVICOS_TI_PASSWORD",
    "AGHUX_URL",
    "AGHUX_USER",
    "AGHUX_PASSWORD",
    "INTEGRA_URL",
    "INTEGRA_USER",
    "INTEGRA_PASSWORD",
)


# ---------------------------------------------------------------------------
# Carregamento
# ---------------------------------------------------------------------------


def _load_settings() -> dict[str, object]:
    """Lê settings.toml; retorna dict vazio se o arquivo não existir."""
    if not _SETTINGS_FILE.exists():
        return {}
    with _SETTINGS_FILE.open("rb") as f:
        return tomllib.load(f)


def _load_env() -> dict[str, str | None]:
    """Lê .env sem poluir os os.environ do processo."""
    if not _ENV_FILE.exists():
        return {}
    return dotenv_values(_ENV_FILE)


def _merge(settings: dict[str, object], env: dict[str, str | None]) -> dict[str, object]:
    """
    Mescla settings.toml (base) com .env (sobrescreve).
    Valores None do .env (variável declarada mas vazia) são ignorados.
    """
    merged: dict[str, object] = dict(settings)
    for key, value in env.items():
        if value is not None:
            merged[key] = value
    return merged


def _validate_credentials(config: dict[str, object]) -> None:
    """
    Verifica presença de todas as credenciais obrigatórias.
    Falha rápido na importação — nunca na metade de uma automação.
    """
    missing: list[str] = [key for key in _REQUIRED_CREDENTIALS if not config.get(key)]
    if missing:
        raise MissingCredentialError(
            f"Credenciais obrigatórias ausentes ou vazias: {', '.join(missing)}. "
            f"Verifique o arquivo .env na raiz do projeto."
        )


# ---------------------------------------------------------------------------
# Config — ponto de acesso único
# ---------------------------------------------------------------------------


class Config:
    """
    Ponto de acesso único às configurações do Senna.

    Uso:
        from senna.core.config import config

        url = config.get("SERVICOS_TI_URL")
        timeout = config.get("browser_timeout", 30)
    """

    def __init__(self) -> None:
        _settings = _load_settings()
        _env = _load_env()
        self._data: dict[str, object] = _merge(_settings, _env)
        _validate_credentials(self._data)

    def get(self, key: str, default: object = None) -> object:
        """Retorna o valor da chave ou o default fornecido."""
        return self._data.get(key, default)

    def require(self, key: str) -> object:
        """
        Retorna o valor da chave.
        Levanta MissingCredentialError se ausente — útil fora do conjunto
        de credenciais obrigatórias definido em _REQUIRED_CREDENTIALS.
        """
        value = self._data.get(key)
        if not value:
            raise MissingCredentialError(
                f"Configuração obrigatória ausente: '{key}'. Verifique settings.toml ou .env."
            )
        return value

    def debug_browser(self) -> bool:
        """Retorna True se DEBUG_BROWSER=true estiver definido (Restrição R2)."""
        return str(self._data.get("DEBUG_BROWSER", "false")).lower() == "true"

    def __repr__(self) -> str:
        keys = list(self._data.keys())
        return f"Config(keys={keys})"


# Instância única — importar sempre desta forma:
#   from senna.core.config import config
config: Config = Config()
