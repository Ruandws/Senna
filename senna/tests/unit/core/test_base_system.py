"""
Testes unitários para senna.core.base_system.BaseSystem

O QUÊ: valida a classe base abstrata para sistemas.
PARA QUÊ: garantir que os contratos de login, logout e verificação de sessão sejam respeitados.
COMO: cria subclasses concretas dummy de BaseSystem e testa o comportamento de repr
      e a impossibilidade de instanciar a classe base abstrata diretamente.
"""

from __future__ import annotations

from unittest.mock import MagicMock

from playwright.sync_api import BrowserContext
import pytest

from senna.core.base_system import BaseSystem
from senna.core.result import Result


class DummySystem(BaseSystem):
    """Subclasse concreta para testar o comportamento de BaseSystem."""

    @property
    def system_id(self) -> str:
        return "dummy_system"

    def login(self, ctx: BrowserContext) -> Result[None, str]:
        return Result.ok(None)

    def logout(self, ctx: BrowserContext) -> Result[None, str]:
        return Result.ok(None)

    def is_logged_in(self, ctx: BrowserContext) -> bool:
        return True


def test_base_system_cannot_be_instantiated_directly() -> None:
    """BaseSystem é uma ABC e não deve permitir instanciação direta."""
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        BaseSystem()  # type: ignore[abstract]


def test_concrete_system_instantiation_and_methods() -> None:
    """Uma subclasse concreta de BaseSystem deve funcionar e expor os métodos/propriedades."""
    system = DummySystem()
    mock_ctx = MagicMock(spec=BrowserContext)

    assert system.system_id == "dummy_system"
    assert system.login(mock_ctx).success is True
    assert system.logout(mock_ctx).success is True
    assert system.is_logged_in(mock_ctx) is True


def test_base_system_repr() -> None:
    """repr() de uma instância de BaseSystem deve retornar o formato esperado."""
    system = DummySystem()
    assert repr(system) == "DummySystem(system_id='dummy_system')"
