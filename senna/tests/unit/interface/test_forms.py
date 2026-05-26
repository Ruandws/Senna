"""Testes unitários para senna.interface.forms.

O QUÊ: Valida o comportamento de definição de campos e formulários.
PARA QUÊ: Garantir validação e payloads válidos antes da execução.
COMO: Testes unitários puros cobrindo caminhos felizes e de erro.
"""

from __future__ import annotations

from datetime import date

import pytest

from senna.core.models import AccessPayload
from senna.interface.forms import (
    PROCEDURE_FORMS,
    FieldDef,
    build_payload,
    validate_form,
)


def test_field_def_instantiation() -> None:
    """FieldDef deve reter corretamente seus atributos."""
    field = FieldDef(
        name="email",
        label="E-mail",
        required=True,
        field_type="email",
        options=["a", "b"],
    )
    assert field.name == "email"
    assert field.label == "E-mail"
    assert field.required is True
    assert field.field_type == "email"
    assert field.options == ["a", "b"]


def test_procedure_forms_coverage() -> None:
    """PROCEDURE_FORMS deve cobrir os procedimentos search_user_by_cpf e extend_access."""
    assert "search_user_by_cpf" in PROCEDURE_FORMS
    assert "extend_access" in PROCEDURE_FORMS

    cpf_fields = PROCEDURE_FORMS["search_user_by_cpf"]
    assert len(cpf_fields) == 1
    assert cpf_fields[0].name == "cpf"
    assert cpf_fields[0].required is True
    assert cpf_fields[0].field_type == "text"

    extend_fields = PROCEDURE_FORMS["extend_access"]
    assert len(extend_fields) == 2
    assert extend_fields[0].name == "registration"
    assert extend_fields[0].required is True
    assert extend_fields[0].field_type == "text"
    assert extend_fields[1].name == "expiration_date"
    assert extend_fields[1].required is True
    assert extend_fields[1].field_type == "date"


def test_validate_form_unknown_procedure() -> None:
    """Procedimento desconhecido não deve gerar erros."""
    errors = validate_form("unknown_proc", {"any": "value"})
    assert errors == {}


def test_validate_form_missing_required() -> None:
    """Campos obrigatórios ausentes devem gerar erro de preenchimento."""
    # Para search_user_by_cpf (cpf é obrigatório)
    errors = validate_form("search_user_by_cpf", {})
    assert errors.get("cpf") == "Campo obrigatório."

    # Campo vazio (com espaços)
    errors = validate_form("search_user_by_cpf", {"cpf": "   "})
    assert errors.get("cpf") == "Campo obrigatório."

    # Para extend_access (ambos são obrigatórios)
    errors = validate_form("extend_access", {"registration": ""})
    assert errors.get("registration") == "Campo obrigatório."
    assert errors.get("expiration_date") == "Campo obrigatório."


def test_validate_form_date_formats() -> None:
    """Validação de datas deve aceitar formatos válidos e rejeitar inválidos."""
    # Data em formato brasileiro válido (DD/MM/YYYY)
    errors = validate_form(
        "extend_access",
        {"registration": "12345", "expiration_date": "31/12/2026"},
    )
    assert "expiration_date" not in errors

    # Data em formato ISO válido (YYYY-MM-DD)
    errors = validate_form(
        "extend_access",
        {"registration": "12345", "expiration_date": "2026-12-31"},
    )
    assert "expiration_date" not in errors

    # Data em formato inválido
    errors = validate_form(
        "extend_access",
        {"registration": "12345", "expiration_date": "31-12-2026"},
    )
    assert errors.get("expiration_date") == "Formato de data inválido. Use DD/MM/YYYY."

    errors = validate_form(
        "extend_access",
        {"registration": "12345", "expiration_date": "invalid-date"},
    )
    assert errors.get("expiration_date") == "Formato de data inválido. Use DD/MM/YYYY."


def test_validate_form_invalid_cpf() -> None:
    """Validação deve retornar erro para CPF com menos (ou mais) de 11 dígitos numéricos."""
    errors = validate_form("search_user_by_cpf", {"cpf": "123.456.789"})
    assert errors.get("cpf") == "CPF inválido: informe 11 dígitos numéricos."

    errors = validate_form("search_user_by_cpf", {"cpf": "123"})
    assert errors.get("cpf") == "CPF inválido: informe 11 dígitos numéricos."


def test_validate_form_valid_payload() -> None:
    """Validação deve retornar dicionário vazio para um payload completamente válido."""
    # Para search_user_by_cpf
    errors = validate_form("search_user_by_cpf", {"cpf": "123.456.789-00"})
    assert errors == {}

    # Para extend_access
    errors = validate_form(
        "extend_access",
        {"registration": "12345", "expiration_date": "31/12/2026"},
    )
    assert errors == {}


def test_validate_form_optional_and_formats_dynamic(monkeypatch: pytest.MonkeyPatch) -> None:
    """Valida tipos email, select e campos opcionais dinamicamente."""
    # Registra um procedimento de teste dinamicamente em PROCEDURE_FORMS
    test_fields = [
        FieldDef(name="opt_text", label="Optional Text", required=False, field_type="text"),
        FieldDef(name="email_field", label="Email", required=True, field_type="email"),
        FieldDef(
            name="select_field",
            label="Select",
            required=True,
            field_type="select",
            options=["Option1", "Option2"],
        ),
        FieldDef(
            name="select_no_opts",
            label="Select sin opts",
            required=True,
            field_type="select",
            options=None,
        ),
    ]
    monkeypatch.setitem(PROCEDURE_FORMS, "test_proc", test_fields)

    # 1. Campos vazios opcionais não devem gerar erros nem validar formato
    errors = validate_form(
        "test_proc",
        {
            "opt_text": "",
            "email_field": "test@test.com",
            "select_field": "Option1",
            "select_no_opts": "Qualquer",
        },
    )
    assert errors == {}

    # 2. Email inválido
    errors = validate_form(
        "test_proc",
        {
            "email_field": "invalid_email",
            "select_field": "Option1",
            "select_no_opts": "Qualquer",
        },
    )
    assert errors.get("email_field") == "E-mail inválido."

    # 3. Select com opção inválida
    errors = validate_form(
        "test_proc",
        {
            "email_field": "test@test.com",
            "select_field": "InvalidOption",
            "select_no_opts": "Qualquer",
        },
    )
    assert errors.get("select_field") == "Opção inválida."


def test_build_payload_search_user_by_cpf() -> None:
    """build_payload deve extrair e limpar o CPF para o procedimento correspondente."""
    payload = build_payload("search_user_by_cpf", {"cpf": " 123.456.789-00 "})
    assert payload == "123.456.789-00"


def test_build_payload_extend_access() -> None:
    """build_payload deve retornar AccessPayload correto com data convertida."""
    # Usando DD/MM/YYYY
    payload = build_payload(
        "extend_access",
        {"registration": " 12345 ", "expiration_date": " 31/12/2026 "},
    )
    assert isinstance(payload, AccessPayload)
    assert payload.registration == "12345"
    assert payload.expiration_date == date(2026, 12, 31)

    # Usando YYYY-MM-DD
    payload = build_payload(
        "extend_access",
        {"registration": "12345", "expiration_date": "2026-12-31"},
    )
    assert payload.expiration_date == date(2026, 12, 31)


def test_build_payload_extend_access_invalid_date() -> None:
    """build_payload deve levantar ValueError se a data for inválida."""
    with pytest.raises(ValueError) as exc_info:
        build_payload(
            "extend_access",
            {"registration": "12345", "expiration_date": "invalid"},
        )
    assert "Data de expiração inválida: 'invalid'" in str(exc_info.value)


def test_build_payload_unknown_procedure() -> None:
    """build_payload deve levantar ValueError explícito para procedimento desconhecido."""
    with pytest.raises(ValueError) as exc_info:
        build_payload("unknown_proc", {"any": "value"})
    assert "Procedimento desconhecido: 'unknown_proc'" in str(exc_info.value)
