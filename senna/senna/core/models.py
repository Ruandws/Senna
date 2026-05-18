from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

# Até 30/4 - Haviam 2 bases. ServiçosTI : 4 payloads | Integra : 3 payloads
# =============================================================================
# PAYLOADS BASE — campos mínimos comuns entre sistemas
# =============================================================================


@dataclass(frozen=True)
class BaseUserPayload:
    name: str
    cpf: str


@dataclass(frozen=True)
class BaseAccessPayload:
    username: str


# =============================================================================
# SERVIÇOS TI
# =============================================================================


@dataclass(frozen=True)
class ServicoesTiCreateUserPayload(BaseUserPayload):
    """
    estende BaseUserPayload com campos do formulário do portal.
    Como: UI monta este payload; AddUserProcedure o passa ao ServicoesTiClient.

    Campos: Tipo, Nome*, CPF*, E-mail alternativo, Empresa, Cargo,
            Gerente, Data de expiração.
    (*) herdados de BaseUserPayload.
    """

    user_type: str
    alternative_email: str
    company: str
    role: str
    manager: str
    expiration_date: date


@dataclass(frozen=True)
class ServicoesTiModelingPayload(BaseUserPayload):
    """
    O quê: estende BaseUserPayload com escritório, login e campos
           corporativos. - Usado pela ModelingProcedure
    Campos: Tipo, Escritório, Nome*, Login, CPF*, E-mail alternativo,
            Empresa, Cargo, Gerente, Data de expiração.
    """

    user_type: str
    office: str
    login: str
    alternative_email: str
    company: str
    role: str
    manager: str
    expiration_date: date


@dataclass(frozen=True)
class ServicoesTiExtendAccessPayload(BaseAccessPayload):
    """
    O quê: estende BaseAccessPayload com CPF e nova data de expiração.
    Campos: CPF, Usuário*, Nova data.
    (*) herdado de BaseAccessPayload como `username`.
    """

    cpf: str
    new_expiration_date: date


@dataclass(frozen=True)
class ServicoesTiCpfCheckPayload:
    """
    O quê: payload para verificação avulsa de um CPF ou lote via planilha.
    Como: se `cpf` preenchido, consulta unitária. Se `spreadsheet_path`
          fornecido, DataLoader processa o lote. Exatamente um dos dois
          deve estar presente.
    Campos: CPF (avulso) | caminho da planilha (lote).
    """

    cpf: str | None = None
    spreadsheet_path: Path | None = None

    def __post_init__(self) -> None:
        if self.cpf is None and self.spreadsheet_path is None:
            raise ValueError("Informe 'cpf' para consulta avulsa ou 'spreadsheet_path' para lote.")
        if self.cpf is not None and self.spreadsheet_path is not None:
            raise ValueError("Informe apenas 'cpf' ou 'spreadsheet_path', não ambos.")


# =============================================================================
# INTEGRA
# =============================================================================


@dataclass(frozen=True)
class IntegraCreateUserPayload(BaseAccessPayload):
    """
    O quê: payload mínimo — herda `username` de BaseAccessPayload sem campos extras.
    Como: AddUserProcedure no Integra instancia este payload e cria o registro.
    (*) herdado de BaseAccessPayload como `username`.
    """


@dataclass(frozen=True)
class IntegraGrantProfilePayload(BaseAccessPayload):
    """
    O quê: estende BaseAccessPayload com o perfil desejado.
    Como: GrantProfileProcedure localiza o usuário e aplica o perfil informado.
    (*) herdado de BaseAccessPayload como `username`.
    """

    profile: str


@dataclass(frozen=True)
class IntegraDeactivateUserPayload(BaseAccessPayload):
    """
    O quê: payload mínimo — herda `username` de BaseAccessPayload sem campos extras.
    Como: DeactivateUserProcedure localiza e inativa o usuário pelo login.

    (*) herdado de BaseAccessPayload como `username`.
    """
