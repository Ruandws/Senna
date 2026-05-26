"""Definição de campos e validações de formulários dinâmicos do Senna."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
import re
from typing import Any, Literal

from senna.core.models import AccessPayload


@dataclass(frozen=True)
class FieldDef:
    """Definição de um campo do formulário dinâmico."""

    name: str
    label: str
    required: bool
    field_type: Literal["text", "date", "select", "email"]
    options: list[str] | None = None


PROCEDURE_FORMS: dict[str, list[FieldDef]] = {
    "search_user_by_cpf": [
        FieldDef(
            name="cpf",
            label="CPF",
            required=True,
            field_type="text",
        )
    ],
    "extend_access": [
        FieldDef(
            name="registration",
            label="Matrícula/Login",
            required=True,
            field_type="text",
        ),
        FieldDef(
            name="expiration_date",
            label="Data de Expiração",
            required=True,
            field_type="date",
        ),
    ],
}


def _parse_date(date_str: str) -> date | None:
    """Tenta converter uma string de data para datetime.date.

    Aceita formatos DD/MM/YYYY e YYYY-MM-DD.
    """
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None


def validate_form(procedure_id: str, raw_values: dict[str, str]) -> dict[str, str]:
    """Valida os campos de entrada de um formulário de procedimento.

    Valida obrigatoriedade e formatos básicos (data, e-mail, etc.).
    Retorna um dicionário mapeando o nome do campo à mensagem de erro correspondente.
    """
    errors: dict[str, str] = {}
    fields = PROCEDURE_FORMS.get(procedure_id)
    if fields is None:
        return errors

    for field in fields:
        value = raw_values.get(field.name, "")
        stripped_value = value.strip() if value else ""

        # 1. Valida obrigatoriedade
        if field.required and not stripped_value:
            errors[field.name] = "Campo obrigatório."
            continue

        if not stripped_value:
            continue

        # 2. Valida formatos com base no tipo
        if field.field_type == "date":
            if _parse_date(stripped_value) is None:
                errors[field.name] = "Formato de data inválido. Use DD/MM/YYYY."
        elif field.field_type == "email":
            email_regex = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
            if not re.match(email_regex, stripped_value):
                errors[field.name] = "E-mail inválido."
        elif field.field_type == "select":
            if field.options is not None and stripped_value not in field.options:
                errors[field.name] = "Opção inválida."

    return errors


def build_payload(procedure_id: str, raw_values: dict[str, str]) -> Any:
    """Constrói o payload tipado para o procedimento a partir dos valores brutos.

    Assume que os dados já foram validados previamente via validate_form.
    """
    if procedure_id == "search_user_by_cpf":
        return raw_values.get("cpf", "").strip()

    if procedure_id == "extend_access":
        registration = raw_values.get("registration", "").strip()
        date_str = raw_values.get("expiration_date", "").strip()
        parsed_date = _parse_date(date_str)
        if parsed_date is None:
            raise ValueError(f"Data de expiração inválida: '{date_str}'")
        return AccessPayload(
            registration=registration,
            expiration_date=parsed_date,
        )

    raise ValueError(f"Procedimento desconhecido: '{procedure_id}'")
