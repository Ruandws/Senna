"""
Testes adicionais para alcançar 100% de cobertura no Core (config e logger).

O QUÊ: valida casos excepcionais e representações do config e logger.
PARA QUÊ: atingir a meta estrita de 100% de cobertura do projeto.
COMO: testa caminhos de exceção e arquivos inexistentes usando patches e chamadas específicas.
"""

from __future__ import annotations

import logging
from unittest.mock import MagicMock, patch

from senna.core.config import Config, config
from senna.core.logger import _build_app_logger, app_logger


def test_config_repr() -> None:
    """Valida o __repr__ do Config."""
    representation = repr(config)
    assert "Config(keys=" in representation


@patch("senna.core.config._SETTINGS_FILE")
@patch("senna.core.config._ENV_FILE")
def test_config_files_not_exists(mock_env: MagicMock, mock_settings: MagicMock) -> None:
    """Valida o comportamento de inicialização do Config se os arquivos não existirem."""
    mock_settings.exists.return_value = False
    mock_env.exists.return_value = False

    # Instancia um Config temporário
    # Como as credenciais obrigatórias são validadas, precisamos mockar _validate_credentials
    with patch("senna.core.config._validate_credentials") as mock_val:
        cfg = Config()
        assert cfg is not None
        mock_val.assert_called_once()


def test_logger_json_formatter_exception() -> None:
    """Valida que o formatter JSON do app_logger formata exceções corretamente."""
    # Criamos um LogRecord com exc_info
    try:
        raise ValueError("Erro de teste para o formatador")
    except ValueError:
        import sys

        exc_info = sys.exc_info()

    # Obtemos o JSONFormatter
    formatter = None
    for handler in app_logger.handlers:
        if isinstance(handler, logging.FileHandler):
            formatter = handler.formatter
            break

    if formatter is not None:
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test_path",
            lineno=10,
            msg="Mensagem de erro",
            args=(),
            exc_info=exc_info,
        )
        formatted = formatter.format(record)
        assert "exception" in formatted
        assert "ValueError: Erro de teste para o formatador" in formatted


def test_build_app_logger_returns_existing() -> None:
    """Valida que _build_app_logger retorna o logger existente se já houver handlers."""
    logger = _build_app_logger()
    assert logger is app_logger
