from senna.core import (
    AVAILABLE_PROCEDURES,
    AVAILABLE_SYSTEMS,
    BaseProcedure,
    BaseSystem,
)


def test_core_init_exports() -> None:
    """Verifica se os exports de __init__.py estão corretos e acessíveis."""
    # Instâncias para validar os registries
    assert isinstance(AVAILABLE_SYSTEMS, dict)
    assert isinstance(AVAILABLE_PROCEDURES, dict)

    # Verifica se os tipos básicos estão acessíveis via core.__init__
    assert BaseSystem is not None
    assert BaseProcedure is not None


def test_registries_are_empty_initially() -> None:
    """Verifica se os registries iniciam vazios ou contêm as chaves esperadas."""
    # Como as implementações foram comentadas, os dicionários devem estar vazios
    assert len(AVAILABLE_SYSTEMS) == 0
    assert len(AVAILABLE_PROCEDURES) == 0
