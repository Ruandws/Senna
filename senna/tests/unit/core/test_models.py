"""
Testes unitários para senna.core.models

O QUÊ: valida instanciação, herança e regras de negócio dos payloads.
PARA QUÊ: payloads errados chegando aos procedures causam automações
          corrompidas no sistema real; testar aqui é barato, testar lá é caro.
COMO: instancia cada dataclass com dados válidos e inválidos;
      verifica frozen=True (imutabilidade); testa __post_init__ de CpfCheck.
      Sem I/O — 100% em memória.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import date
from pathlib import Path

import pytest

from senna.core.models import (
    BaseAccessPayload,
    BaseUserPayload,
    IntegraCreateUserPayload,
    IntegraDeactivateUserPayload,
    IntegraGrantProfilePayload,
    ServicoesTiCpfCheckPayload,
    ServicoesTiCreateUserPayload,
    ServicoesTiExtendAccessPayload,
    ServicoesTiModelingPayload,
)

# Datas fixas para não depender de "hoje"
_DATA_HOJE = date(2025, 12, 31)


# =============================================================================
# Bases
# =============================================================================


def test_base_user_payload_instantiation() -> None:
    payload = BaseUserPayload(name="João Silva", cpf="12345678901")
    assert payload.name == "João Silva"
    assert payload.cpf == "12345678901"


def test_base_access_payload_instantiation() -> None:
    payload = BaseAccessPayload(username="jsilva")
    assert payload.username == "jsilva"


# =============================================================================
# ServicoesTi — CreateUser
# =============================================================================


def test_servicos_ti_create_user_payload_all_fields() -> None:
    """Payload completo deve instanciar sem erros e preservar todos os valores."""
    payload = ServicoesTiCreateUserPayload(
        name="Maria Souza",
        cpf="98765432100",
        user_type="interno",
        alternative_email="maria@hospital.gov.br",
        company="Hospital Geral",
        role="Enfermeira",
        manager="Carlos Lima",
        expiration_date=_DATA_HOJE,
    )
    assert payload.name == "Maria Souza"
    assert payload.cpf == "98765432100"
    assert payload.expiration_date == _DATA_HOJE


def test_servicos_ti_create_user_is_base_user() -> None:
    """Deve ser detectável como BaseUserPayload para polimorfismo."""
    payload = ServicoesTiCreateUserPayload(
        name="X", cpf="000", user_type="externo",
        alternative_email="x@x.com", company="C", role="R",
        manager="M", expiration_date=_DATA_HOJE,
    )
    assert isinstance(payload, BaseUserPayload)


def test_servicos_ti_create_user_is_immutable() -> None:
    """frozen=True — não deve aceitar modificação após criação."""
    payload = ServicoesTiCreateUserPayload(
        name="X", cpf="000", user_type="externo",
        alternative_email="x@x.com", company="C", role="R",
        manager="M", expiration_date=_DATA_HOJE,
    )
    with pytest.raises(FrozenInstanceError):
        payload.name = "Outro Nome"  # type: ignore[misc]


# =============================================================================
# ServicoesTi — Modeling
# =============================================================================


def test_servicos_ti_modeling_payload_includes_login_and_office() -> None:
    payload = ServicoesTiModelingPayload(
        name="Pedro Alves",
        cpf="11122233344",
        user_type="interno",
        office="Sede",
        login="palves",
        alternative_email="pedro@h.com",
        company="H",
        role="TI",
        manager="Chefe",
        expiration_date=_DATA_HOJE,
    )
    assert payload.login == "palves"
    assert payload.office == "Sede"


# =============================================================================
# ServicoesTi — ExtendAccess
# =============================================================================


def test_servicos_ti_extend_access_payload() -> None:
    payload = ServicoesTiExtendAccessPayload(
        username="jsilva",
        cpf="12345678901",
        new_expiration_date=_DATA_HOJE,
    )
    assert payload.username == "jsilva"
    assert payload.new_expiration_date == _DATA_HOJE


def test_servicos_ti_extend_access_is_base_access() -> None:
    payload = ServicoesTiExtendAccessPayload(
        username="jsilva", cpf="123", new_expiration_date=_DATA_HOJE,
    )
    assert isinstance(payload, BaseAccessPayload)


# =============================================================================
# ServicoesTi — CpfCheck (com __post_init__)
# =============================================================================


def test_cpf_check_with_cpf_only() -> None:
    """Consulta avulsa por CPF deve funcionar."""
    payload = ServicoesTiCpfCheckPayload(cpf="12345678901")
    assert payload.cpf == "12345678901"
    assert payload.spreadsheet_path is None


def test_cpf_check_with_spreadsheet_only() -> None:
    """Consulta em lote por planilha deve funcionar."""
    path = Path("data/input/lote.xlsx")
    payload = ServicoesTiCpfCheckPayload(spreadsheet_path=path)
    assert payload.spreadsheet_path == path
    assert payload.cpf is None


def test_cpf_check_raises_when_both_none() -> None:
    """Sem CPF e sem planilha deve levantar ValueError."""
    with pytest.raises(ValueError, match="cpf"):
        ServicoesTiCpfCheckPayload()


def test_cpf_check_raises_when_both_provided() -> None:
    """CPF e planilha juntos devem levantar ValueError."""
    with pytest.raises(ValueError, match="apenas"):
        ServicoesTiCpfCheckPayload(
            cpf="123",
            spreadsheet_path=Path("data/input/lote.xlsx"),
        )


# =============================================================================
# Integra
# =============================================================================


def test_integra_create_user_payload() -> None:
    """Payload mínimo — só username herdado."""
    payload = IntegraCreateUserPayload(username="mrocha")
    assert payload.username == "mrocha"
    assert isinstance(payload, BaseAccessPayload)


def test_integra_grant_profile_payload() -> None:
    payload = IntegraGrantProfilePayload(username="mrocha", profile="MEDICO")
    assert payload.profile == "MEDICO"
    assert isinstance(payload, BaseAccessPayload)


def test_integra_deactivate_user_payload() -> None:
    payload = IntegraDeactivateUserPayload(username="mrocha")
    assert payload.username == "mrocha"
    assert isinstance(payload, BaseAccessPayload)


def test_integra_payloads_are_immutable() -> None:
    """Todos os payloads Integra são frozen."""
    payload = IntegraGrantProfilePayload(username="x", profile="Y")
    with pytest.raises(FrozenInstanceError):
        payload.profile = "Z"  # type: ignore[misc]
