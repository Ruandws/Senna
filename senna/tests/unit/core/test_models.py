"""
Testes unitários para senna.core.models

O QUÊ: valida instanciação, imutabilidade e regras dos payloads e enums.
PARA QUÊ: payloads errados chegando aos procedures causam automações
          corrompidas no sistema real; testar aqui é barato, testar lá é caro.
COMO: instancia cada dataclass com dados válidos; verifica frozen=True
      (imutabilidade); valida ProfileAction (StrEnum) e campos opcionais
      de RemovalPayload. Sem I/O — 100% em memória.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import date

import pytest

from senna.core.models import (
    AccessPayload,
    ExecutionRecord,
    ProfileAction,
    ProfilePayload,
    RemovalPayload,
    UserPayload,
)

_DATA_FIXA = date(2026, 12, 31)


# =========================================================================
# ProfileAction (StrEnum)
# =========================================================================


def test_profile_action_grant_value() -> None:
    """ProfileAction.GRANT deve ter valor 'grant'."""
    assert ProfileAction.GRANT == "grant"


def test_profile_action_revoke_value() -> None:
    """ProfileAction.REVOKE deve ter valor 'revoke'."""
    assert ProfileAction.REVOKE == "revoke"


def test_profile_action_is_str() -> None:
    """ProfileAction deve ser usável como string nativa."""
    assert isinstance(ProfileAction.GRANT, str)


# =========================================================================
# UserPayload (P1)
# =========================================================================


def test_user_payload_all_fields() -> None:
    """Payload completo deve instanciar e preservar todos os valores."""
    payload = UserPayload(
        name="Maria Souza",
        registration="12345",
        email="maria@hospital.gov.br",
        profile="enfermeira",
    )
    assert payload.name == "Maria Souza"
    assert payload.registration == "12345"
    assert payload.email == "maria@hospital.gov.br"
    assert payload.profile == "enfermeira"


def test_user_payload_is_immutable() -> None:
    """frozen=True — não deve aceitar modificação após criação."""
    payload = UserPayload(name="X", registration="0", email="x@x.com", profile="p")
    with pytest.raises(FrozenInstanceError):
        payload.name = "Outro"  # type: ignore[misc]


# =========================================================================
# RemovalPayload (P2) — campos opcionais
# =========================================================================


def test_removal_payload_with_registration_only() -> None:
    """RemovalPayload aceita apenas registration."""
    payload = RemovalPayload(registration="12345")
    assert payload.registration == "12345"
    assert payload.login is None


def test_removal_payload_with_login_only() -> None:
    """RemovalPayload aceita apenas login."""
    payload = RemovalPayload(login="jsilva")
    assert payload.login == "jsilva"
    assert payload.registration is None


def test_removal_payload_with_both() -> None:
    """RemovalPayload aceita ambos os campos preenchidos."""
    payload = RemovalPayload(registration="12345", login="jsilva")
    assert payload.registration == "12345"
    assert payload.login == "jsilva"


def test_removal_payload_is_immutable() -> None:
    payload = RemovalPayload(login="x")
    with pytest.raises(FrozenInstanceError):
        payload.login = "y"  # type: ignore[misc]


# =========================================================================
# AccessPayload (P3)
# =========================================================================


def test_access_payload_all_fields() -> None:
    payload = AccessPayload(registration="12345", expiration_date=_DATA_FIXA)
    assert payload.registration == "12345"
    assert payload.expiration_date == _DATA_FIXA


def test_access_payload_is_immutable() -> None:
    payload = AccessPayload(registration="12345", expiration_date=_DATA_FIXA)
    with pytest.raises(FrozenInstanceError):
        payload.registration = "99999"  # type: ignore[misc]


# =========================================================================
# ProfilePayload (P4)
# =========================================================================


def test_profile_payload_grant() -> None:
    payload = ProfilePayload(
        registration="12345",
        profile="MEDICO",
        action=ProfileAction.GRANT,
    )
    assert payload.registration == "12345"
    assert payload.profile == "MEDICO"
    assert payload.action == ProfileAction.GRANT


def test_profile_payload_revoke() -> None:
    payload = ProfilePayload(
        registration="12345",
        profile="MEDICO",
        action=ProfileAction.REVOKE,
    )
    assert payload.action == ProfileAction.REVOKE


def test_profile_payload_is_immutable() -> None:
    payload = ProfilePayload(registration="0", profile="X", action=ProfileAction.GRANT)
    with pytest.raises(FrozenInstanceError):
        payload.profile = "Y"  # type: ignore[misc]


# =========================================================================
# ExecutionRecord (RF-05)
# =========================================================================


def test_execution_record_all_fields() -> None:
    record = ExecutionRecord(
        row_index=0,
        system_id="servicos_ti",
        procedure_id="add_user",
        success=True,
        message="Usuário criado.",
    )
    assert record.row_index == 0
    assert record.system_id == "servicos_ti"
    assert record.procedure_id == "add_user"
    assert record.success is True
    assert record.message == "Usuário criado."


def test_execution_record_failure() -> None:
    record = ExecutionRecord(
        row_index=5,
        system_id="aghux",
        procedure_id="remove_user",
        success=False,
        message="Usuário não encontrado.",
    )
    assert record.success is False


def test_execution_record_is_immutable() -> None:
    record = ExecutionRecord(
        row_index=0,
        system_id="s",
        procedure_id="p",
        success=True,
        message="ok",
    )
    with pytest.raises(FrozenInstanceError):
        record.success = False  # type: ignore[misc]
