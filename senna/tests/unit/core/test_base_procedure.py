"""
Testes unitários para senna.core.base_procedure.BaseProcedure

O QUÊ: valida a classe base abstrata para procedimentos.
PARA QUÊ: garantir que os contratos de validação e execução sejam respeitados.
COMO: cria subclasses concretas dummy de BaseProcedure e testa o comportamento de repr
      e a impossibilidade de instanciar a classe base abstrata diretamente.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

from playwright.sync_api import BrowserContext
import pytest

from senna.core.base_procedure import BaseProcedure
from senna.core.result import Result


class DummyProcedure(BaseProcedure):
    """Subclasse concreta para testar o comportamento de BaseProcedure."""

    @property
    def procedure_id(self) -> str:
        return "dummy_procedure"

    def validate(self, payload: Any) -> Result[None, str]:
        return Result.ok(None)

    def execute(self, payload: Any, ctx: BrowserContext) -> Result[str, str]:
        return Result.ok("sucesso")


def test_base_procedure_cannot_be_instantiated_directly() -> None:
    """BaseProcedure é uma ABC e não deve permitir instanciação direta."""
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        BaseProcedure()  # type: ignore[abstract]


def test_concrete_procedure_instantiation_and_methods() -> None:
    """Uma subclasse concreta de BaseProcedure deve funcionar e expor os métodos/propriedades."""
    procedure = DummyProcedure()
    mock_ctx = MagicMock(spec=BrowserContext)

    assert procedure.procedure_id == "dummy_procedure"
    assert procedure.validate({}).success is True
    res = procedure.execute({}, mock_ctx)
    assert res.success is True
    assert res.unwrap() == "sucesso"


def test_base_procedure_repr() -> None:
    """repr() de uma instância de BaseProcedure deve retornar o formato esperado."""
    procedure = DummyProcedure()
    assert repr(procedure) == "DummyProcedure(procedure_id='dummy_procedure')"
