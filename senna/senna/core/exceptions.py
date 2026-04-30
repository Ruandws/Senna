# hierarquia de erros: LoginError, SelectorNotFoundError, SystemUnavailableError, ConnectivityError

from __future__ import annotations


class SennaError(Exception):
    """Base de todas as exceções do projeto."""


# --- Configuração e ambiente ---

class MissingCredentialError(SennaError):
    """Credencial obrigatória ausente no ambiente."""


class InvalidSettingsError(SennaError):
    """Configuração inválida ou ausente em settings.toml."""


# --- Sistema e autenticação ---

class SystemUnavailableError(SennaError):
    """Sistema-alvo fora do ar ou inacessível."""


class AuthenticationError(SennaError):
    """Falha no login com as credenciais fornecidas."""


class SessionExpiredError(SennaError):
    """Sessão expirada durante execução de procedimento."""


# --- Procedimentos ---

class ProcedureError(SennaError):
    """Erro genérico durante execução de procedimento."""


class ValidationError(SennaError):
    """Payload inválido — falhou na validação antes da execução."""


class ProcedureTimeoutError(ProcedureError):
    """Procedimento excedeu o tempo limite de 60 segundos."""


# --- Processamento em lote ---

class DataLoaderError(SennaError):
    """Erro ao carregar ou validar planilha de entrada."""


class InvalidSpreadsheetError(DataLoaderError):
    """Planilha com colunas obrigatórias ausentes ou formato inválido."""