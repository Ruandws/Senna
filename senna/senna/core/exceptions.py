"""
Hierarquia de exceções do Senna.

Todas as exceções herdam de SennaError, permitindo captura ampla quando necessário:

    except SennaError as e:
        ...

Regra geral: exceções são levantadas na camada de sistemas/procedures e
capturadas pelo Orchestrator, que as converte em Result[T, E].
Nenhuma exceção deve chegar à UI sem ser tratada (RNF-03).
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------


class SennaError(Exception):
    """Exceção base do Senna. Todas as exceções do projeto herdam desta."""


# ---------------------------------------------------------------------------
# Configuração e ambiente
# ---------------------------------------------------------------------------


class MissingCredentialError(SennaError):
    """
    Levantada quando uma credencial obrigatória está ausente ou vazia no .env.
    Detectada na inicialização do Config, antes de qualquer automação (RF-06).
    """


class ConfigurationError(SennaError):
    """
    Levantada quando settings.toml ou .env contém um valor inválido
    (tipo errado, valor fora do intervalo esperado, etc.).
    """


# ---------------------------------------------------------------------------
# Sistemas e autenticação
# ---------------------------------------------------------------------------


class SystemError(SennaError):
    """Base para erros relacionados a um sistema-alvo específico."""

    def __init__(self, system_id: str, message: str) -> None:
        self.system_id = system_id
        super().__init__(f"[{system_id}] {message}")


class SystemUnavailableError(SystemError):
    """
    Levantada quando o sistema-alvo não está acessível (fora do ar, timeout
    de conexão, resposta inesperada na página inicial).
    Capturada pelo Orchestrator → Result de falha exibido na UI sem travar (RNF-03).
    """


class AuthenticationError(SystemError):
    """
    Levantada quando o login falha (credenciais inválidas, sessão expirada,
    MFA inesperado, etc.).
    """


class SessionError(SystemError):
    """
    Levantada quando a sessão é perdida durante a execução de um procedimento
    (logout inesperado, timeout de inatividade do sistema-alvo).
    """


# ---------------------------------------------------------------------------
# Procedimentos
# ---------------------------------------------------------------------------


class ProcedureError(SennaError):
    """Base para erros ocorridos durante a execução de um procedimento."""

    def __init__(self, procedure_id: str, message: str) -> None:
        self.procedure_id = procedure_id
        super().__init__(f"[{procedure_id}] {message}")


class ValidationError(ProcedureError):
    """
    Levantada por procedure.validate() quando o payload não satisfaz
    as regras de negócio (campo obrigatório vazio, formato inválido, etc.).
    Deve ser exibida inline na UI, próxima ao campo responsável (RF-03).
    """

    def __init__(self, procedure_id: str, field: str, reason: str) -> None:
        self.field = field
        self.reason = reason
        super().__init__(procedure_id, f"Campo '{field}': {reason}")


class ExecutionError(ProcedureError):
    """
    Levantada quando procedure.execute() falha após validação bem-sucedida
    (elemento não encontrado, ação bloqueada pelo sistema-alvo, etc.).
    """


class TimeoutError(ProcedureError):  # noqa: A001
    """
    Levantada quando um procedimento excede o limite de 60 segundos (RNF-01).
    Subclasse de ProcedureError para manter rastreabilidade do procedimento.
    """


# ---------------------------------------------------------------------------
# Browser
# ---------------------------------------------------------------------------


class BrowserError(SennaError):
    """
    Levantada pelo BrowserFactory quando não é possível abrir ou fechar
    um BrowserContext isolado (RF-08).
    """


# ---------------------------------------------------------------------------
# Processamento em lote
# ---------------------------------------------------------------------------


class BatchError(SennaError):
    """Base para erros no processamento de planilhas em lote (RF-05)."""


class InvalidSpreadsheetError(BatchError):
    """
    Levantada pelo DataLoader quando a planilha importada não contém
    as colunas obrigatórias ou está corrompida.
    """

    def __init__(self, path: str, reason: str) -> None:
        self.path = path
        super().__init__(f"Planilha inválida '{path}': {reason}")


class RowExecutionError(BatchError):
    """
    Levantada quando uma linha do lote falha na execução.
    Não interrompe o lote — é registrada no relatório de saída (RF-05).
    """

    def __init__(self, row_index: int, reason: str) -> None:
        self.row_index = row_index
        super().__init__(f"Linha {row_index}: {reason}")


# ---------------------------------------------------------------------------
# Orquestração
# ---------------------------------------------------------------------------


class OrchestratorError(SennaError):
    """
    Levantada pelo Orchestrator quando sistema ou procedimento solicitado
    não está registrado em AVAILABLE_SYSTEMS.
    """
