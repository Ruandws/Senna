# lê settings.toml e variáveis de ambiente; instancia objetos para imports em outros arquivos, e expõe objeto Settings
from __future__ import annotations
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv
import os

_ROOT = Path(__file__).resolve().parents[2]
_ENV_PATH = _ROOT / ".env"
_SETTINGS_PATH = _ROOT / "settings.toml"

load_dotenv(_ENV_PATH)


def _load_toml(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("rb") as f:
        return tomllib.load(f)


@dataclass
class BrowserSettings:
    headless: bool = True
    timeout_ms: int = 60_000
    slow_mo_ms: int = 0


@dataclass
class LogSettings:
    level: str = "INFO"
    audit_dir: str = "logs/audit"


@dataclass
class DataSettings:
    input_dir: str = "data/input"
    output_dir: str = "data/output"
    temp_dir: str = "data/temp"


@dataclass
class Settings: # Instanciado, qualquer outro arquivo só importa e usa
    browser: BrowserSettings = field(default_factory=BrowserSettings)
    log: LogSettings = field(default_factory=LogSettings)
    data: DataSettings = field(default_factory=DataSettings)
    debug_browser: bool = False

    @classmethod
    def load(cls) -> "Settings":
        raw = _load_toml(_SETTINGS_PATH)

        browser = BrowserSettings(
            headless=not _is_true(os.getenv("DEBUG_BROWSER", "false")),
            timeout_ms=int(raw.get("browser", {}).get("timeout_ms", 60_000)),
            slow_mo_ms=int(raw.get("browser", {}).get("slow_mo_ms", 0)),
        )

        log = LogSettings(
            level=raw.get("log", {}).get("level", "INFO"),
            audit_dir=raw.get("log", {}).get("audit_dir", "logs/audit"),
        )

        data = DataSettings(
            input_dir=raw.get("data", {}).get("input_dir", "data/input"),
            output_dir=raw.get("data", {}).get("output_dir", "data/output"),
            temp_dir=raw.get("data", {}).get("temp_dir", "data/temp"),
        )

        return cls(
            browser=browser,
            log=log,
            data=data,
            debug_browser=_is_true(os.getenv("DEBUG_BROWSER", "false")),
        )

    def require_env(self, *keys: str) -> None:
        """Levanta EnvironmentError se qualquer chave estiver ausente no ambiente."""
        missing = [k for k in keys if not os.getenv(k)]
        if missing:
            raise EnvironmentError(
                f"Credenciais obrigatórias ausentes: {', '.join(missing)}"
            )


def _is_true(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes"}


settings: Settings = Settings.load()