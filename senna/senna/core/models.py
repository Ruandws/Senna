"""
Modelos de dados e payloads do Senna.

Todos os payloads são dataclasses tipadas e imutáveis (frozen=True).
Dicionários soltos são proibidos para dados críticos de execução (§14.1, Boundaries §15).

Cada payload corresponde a um ou mais procedimentos definidos em RF-04:

  UserPayload    → P1 (Adicionar usuário)
  RemovalPayload → P2 (Remover usuário)
  AccessPayload  → P3 (Alterar data de expiração)
  ProfilePayload → P4 (Conceder/revogar perfil de acesso)

Uso:
    from senna.core.models import UserPayload, ProfilePayload

    payload = UserPayload(
        name="João Silva",
        registration="12345",
        email="joao.silva@hospital.gov.br",
        profile="assistente",
    )
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum

# ---------------------------------------------------------------------------
# Enums de domínio
# ---------------------------------------------------------------------------


class ProfileAction(StrEnum):
    """Ação sobre um perfil de acesso (P4)."""

    GRANT = "grant"
    REVOKE = "revoke"


# ---------------------------------------------------------------------------
# Payloads
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class UserPayload:
    """
    Payload para P1 — Adicionar usuário.

    Campos:
      name         — nome completo do usuário
      registration — matrícula funcional (identificador único no sistema)
      email        — e-mail institucional
      profile      — perfil de acesso inicial a ser atribuído
    """

    name: str
    registration: str
    email: str
    profile: str


@dataclass(frozen=True)
class RemovalPayload:
    """
    Payload para P2 — Remover usuário.

    Exige ao menos um identificador: matrícula ou login.
    A validação de presença mínima é feita em procedure.validate().

    Campos:
      registration — matrícula funcional (opcional se login fornecido)
      login        — login do sistema-alvo (opcional se registration fornecida)
    """

    registration: str | None = None
    login: str | None = None


@dataclass(frozen=True)
class AccessPayload:
    """
    Payload para P3 — Alterar data de expiração.

    Campos:
      registration    — matrícula funcional do usuário
      expiration_date — nova data de expiração do acesso
    """

    registration: str
    expiration_date: date


@dataclass(frozen=True)
class ProfilePayload:
    """
    Payload para P4 — Conceder ou revogar perfil de acesso.

    Campos:
      registration — matrícula funcional do usuário
      profile      — perfil a ser concedido ou revogado
      action       — ProfileAction.GRANT ou ProfileAction.REVOKE
    """

    registration: str
    profile: str
    action: ProfileAction


# ---------------------------------------------------------------------------
# ExecutionRecord — resultado por linha no processamento em lote (RF-05)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ExecutionRecord:
    """
    Representa o resultado de uma execução individual dentro de um lote.
    Compõe o relatório salvo em data/output/ ao final do processamento.

    Campos:
      row_index    — índice da linha na planilha (base 0)
      system_id    — sistema-alvo da execução
      procedure_id — procedimento executado
      success      — True se concluiu sem erros
      message      — mensagem de sucesso ou descrição do erro
    """

    row_index: int
    system_id: str
    procedure_id: str
    success: bool
    message: str
