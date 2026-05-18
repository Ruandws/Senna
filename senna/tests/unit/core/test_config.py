"""
Testes unitários para senna.core.config.Settings

O QUÊ: valida carregamento de configurações a partir de variáveis de ambiente
       e que require_env() levanta erro quando credencial está ausente.
PARA QUÊ: uma config errada silenciosa quebra o sistema inteiro em produção.
          Testar aqui é detectar isso antes de rodar o Playwright.
COMO: usa o fixture `monkeypatch` do pytest para injetar/remover variáveis
      de ambiente sem tocar no .env real. Settings.load() é chamado DENTRO
      do teste, nunca importado como singleton.
      Sem rede, sem arquivos reais.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from senna.core.config import Settings, _is_true

# =============================================================================
# _is_true — helper privado
# =============================================================================


@pytest.mark.parametrize(
    "value, expected",
    [
        ("true", True),
        ("True", True),
        ("TRUE", True),
        ("1", True),
        ("yes", True),
        ("YES", True),
        ("false", False),
        ("0", False),
        ("no", False),
        ("", False),
        ("  true  ", True),   # strip deve funcionar
    ],
)
def test_is_true(value: str, expected: bool) -> None:
    """_is_true deve normalizar variações de truthy corretamente."""
    assert _is_true(value) is expected


# =============================================================================
# Settings.load — valores padrão (sem settings.toml, sem env vars específicas)
# =============================================================================


def test_settings_load_returns_settings_instance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Settings.load() deve retornar um objeto Settings sem levantar exceção."""
    monkeypatch.delenv("DEBUG_BROWSER", raising=False)
    result = Settings.load()
    assert isinstance(result, Settings)


def test_settings_default_headless_is_true(monkeypatch: pytest.MonkeyPatch) -> None:
    """Sem DEBUG_BROWSER, o browser deve ser headless por padrão."""
    monkeypatch.delenv("DEBUG_BROWSER", raising=False)
    s = Settings.load()
    assert s.browser.headless is True
    assert s.debug_browser is False


def test_settings_debug_browser_true_via_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """DEBUG_BROWSER=true deve desativar headless e ativar debug_browser."""
    monkeypatch.setenv("DEBUG_BROWSER", "true")
    s = Settings.load()
    assert s.browser.headless is False
    assert s.debug_browser is True


def test_settings_debug_browser_accepts_1(monkeypatch: pytest.MonkeyPatch) -> None:
    """DEBUG_BROWSER=1 também deve ser reconhecido como verdadeiro."""
    monkeypatch.setenv("DEBUG_BROWSER", "1")
    s = Settings.load()
    assert s.debug_browser is True


def test_settings_default_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    """Sem settings.toml, timeout deve ser 60.000 ms (60 s conforme SPEC RNF-01)."""
    monkeypatch.delenv("DEBUG_BROWSER", raising=False)
    s = Settings.load()
    assert s.browser.timeout_ms == 60_000


def test_settings_default_log_level(monkeypatch: pytest.MonkeyPatch) -> None:
    """Nível de log padrão deve ser INFO."""
    monkeypatch.delenv("DEBUG_BROWSER", raising=False)
    s = Settings.load()
    assert s.log.level == "INFO"


def test_settings_default_data_dirs(monkeypatch: pytest.MonkeyPatch) -> None:
    """Diretórios de data devem ter os caminhos padrão definidos no SPEC."""
    monkeypatch.delenv("DEBUG_BROWSER", raising=False)
    s = Settings.load()
    assert s.data.input_dir == "data/input"
    assert s.data.output_dir == "data/output"
    assert s.data.temp_dir == "data/temp"


def test_settings_load_with_toml_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """settings.toml deve sobrescrever defaults."""
    toml_file = tmp_path / "settings.toml"
    toml_file.write_text(
        "[browser]\ntimeout_ms = 30000\n"
        "[log]\nlevel = 'DEBUG'\n",
        encoding="utf-8"
    )
    monkeypatch.setattr("senna.core.config._SETTINGS_PATH", toml_file)
    monkeypatch.delenv("DEBUG_BROWSER", raising=False)

    s = Settings.load()
    assert s.browser.timeout_ms == 30_000
    assert s.log.level == "DEBUG"



# =============================================================================
# require_env — verificação de credenciais obrigatórias
# =============================================================================


def test_require_env_passes_when_all_present(monkeypatch: pytest.MonkeyPatch) -> None:
    """Quando todas as chaves estão no ambiente, não deve levantar exceção."""
    monkeypatch.setenv("SISTEMA_USER", "admin")
    monkeypatch.setenv("SISTEMA_PASS", "secret")
    s = Settings.load()
    s.require_env("SISTEMA_USER", "SISTEMA_PASS")  # não deve levantar


def test_require_env_raises_when_key_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Credencial ausente deve levantar EnvironmentError com o nome da chave."""
    monkeypatch.delenv("CREDENCIAL_AUSENTE", raising=False)
    s = Settings.load()
    with pytest.raises(EnvironmentError, match="CREDENCIAL_AUSENTE"):
        s.require_env("CREDENCIAL_AUSENTE")


def test_require_env_lists_all_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Se múltiplas credenciais estiverem ausentes, todas devem aparecer no erro."""
    monkeypatch.delenv("KEY_A", raising=False)
    monkeypatch.delenv("KEY_B", raising=False)
    s = Settings.load()
    with pytest.raises(EnvironmentError) as exc_info:
        s.require_env("KEY_A", "KEY_B")
    message = str(exc_info.value)
    assert "KEY_A" in message
    assert "KEY_B" in message
