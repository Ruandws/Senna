"""Registro central de sistemas e procedimentos disponíveis no Senna."""

from __future__ import annotations

from senna.core.base_procedure import BaseProcedure
from senna.core.base_system import BaseSystem

SystemRegistry = dict[str, BaseSystem]
ProcedureRegistry = dict[str, dict[str, BaseProcedure]]

# Preenchido à medida que os sistemas forem implementados.
# Para registrar um novo sistema: adicione a entrada abaixo e importe a classe correspondente.

AVAILABLE_SYSTEMS: SystemRegistry = {
    # "servicos_ti": ServicoesTiSystem(),   # Fase 2
    # "aghux":       AghuxSystem(),         # Fase 5
    # "integra":     IntegraSystem(),       # Fase 5
}

AVAILABLE_PROCEDURES: ProcedureRegistry = {
    # "servicos_ti": {                      # Fase 2
    #     "add_user":      AddUserProcedure(),
    #     "remove_user":   RemoveUserProcedure(),
    #     "extend_access": ExtendAccessProcedure(),
    #     "grant_profile": GrantProfileProcedure(),
    # },
}
