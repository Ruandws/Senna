"""Registro central de sistemas e procedimentos disponíveis no Senna."""

from __future__ import annotations

from senna.core.base_procedure import BaseProcedure
from senna.core.base_system import BaseSystem
from senna.systems.servicos_ti.client import ServicoesTiSystem
from senna.systems.servicos_ti.procedures.search_user_by_cpf import SearchUserByCpfProcedure

SystemRegistry = dict[str, BaseSystem]
ProcedureRegistry = dict[str, dict[str, BaseProcedure]]

AVAILABLE_SYSTEMS: SystemRegistry = {
    "servicos_ti": ServicoesTiSystem(),
    # "aghux":    AghuxSystem(),     # Fase 5
    # "integra":  IntegraSystem(),   # Fase 5
}

AVAILABLE_PROCEDURES: ProcedureRegistry = {
    "servicos_ti": {
        "search_user_by_cpf": SearchUserByCpfProcedure(),
        # "add_user":      AddUserProcedure(),      # próximas procedures
        # "remove_user":   RemoveUserProcedure(),
        # "extend_access": ExtendAccessProcedure(),
        # "grant_profile": GrantProfileProcedure(),
    },
    # "aghux":   {...},  # Fase 5
    # "integra": {...},  # Fase 5
}