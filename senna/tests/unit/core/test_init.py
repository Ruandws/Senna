"""
Testes unitários para senna.core.__init__

O QUÊ: valida os exports e registries do módulo core.
PARA QUÊ: garantir que AVAILABLE_SYSTEMS, AVAILABLE_PROCEDURES, BaseSystem,
          BaseProcedure e os type aliases estejam acessíveis e corretos.
COMO: importa os símbolos do core e verifica tipos, acessibilidade e estado
      inicial dos registries. Sem I/O — 100% em memória.
"""

from __future__ import annotations

from senna.core import (
    AVAILABLE_PROCEDURES,
    AVAILABLE_SYSTEMS,
    BaseProcedure,
    BaseSystem,
    ProcedureRegistry,
    SystemRegistry,
)

# =========================================================================
# Exports — acessibilidade dos símbolos públicos
# =========================================================================


def test_core_init_exports_base_classes() -> None:
    """BaseSystem e BaseProcedure devem ser acessíveis via senna.core."""
    assert BaseSystem is not None
    assert BaseProcedure is not None


def test_core_init_exports_registries() -> None:
    """AVAILABLE_SYSTEMS e AVAILABLE_PROCEDURES devem ser dicts acessíveis."""
    assert isinstance(AVAILABLE_SYSTEMS, dict)
    assert isinstance(AVAILABLE_PROCEDURES, dict)


# =========================================================================
# Type aliases — SystemRegistry e ProcedureRegistry
# =========================================================================


def test_system_registry_type_alias_is_dict() -> None:
    """SystemRegistry deve ser um alias para dict[str, BaseSystem]."""
    assert SystemRegistry is not None
    # Verifica que o type alias referencia dict
    assert getattr(SystemRegistry, "__origin__", None) is dict


def test_procedure_registry_type_alias_is_dict() -> None:
    """ProcedureRegistry deve ser um alias para dict[str, dict[str, BaseProcedure]]."""
    assert ProcedureRegistry is not None
    assert getattr(ProcedureRegistry, "__origin__", None) is dict


# =========================================================================
# Estado inicial — registries vazios na Fase 1
# =========================================================================


def test_registries_are_empty_initially() -> None:
    """Registries devem estar vazios enquanto nenhum sistema for implementado."""
    assert len(AVAILABLE_SYSTEMS) == 0
    assert len(AVAILABLE_PROCEDURES) == 0
