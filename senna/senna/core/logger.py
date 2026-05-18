"""
Sistema de logging do Senna.

Dois loggers distintos, com responsabilidades separadas:

  app_logger   — logs operacionais da aplicação (debug, info, erros internos).
                 Destinado ao desenvolvedor. Rotacionado diariamente.

  audit_logger — registro imutável de auditoria por execução (RF-06, §12).
                 Destinado ao Coordenador de TI. Nunca rotacionado automaticamente.
                 Formato JSON estrito: quem fez, o quê, quando, resultado.

Uso:
    from senna.core.logger import app_logger, audit_logger

    app_logger.info("Iniciando procedimento %s", procedure_id)
    audit_logger.log_execution(entry)
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import logging
import logging.handlers
from pathlib import Path
from typing import Any

from senna.core.config import config

# ---------------------------------------------------------------------------
# Caminhos
# ---------------------------------------------------------------------------

_ROOT: Path = Path(__file__).resolve().parents[2]
_LOG_DIR: Path = _ROOT / str(config.get("audit.log_dir", "logs/audit"))
_LOG_DIR.mkdir(parents=True, exist_ok=True)

_APP_LOG_FILE: Path = _ROOT / "logs" / "app.log"
_APP_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

_AUDIT_LOG_FILE: Path = _LOG_DIR / "audit.jsonl"

# ---------------------------------------------------------------------------
# Formatter JSON para o app_logger
# ---------------------------------------------------------------------------


class _JsonFormatter(logging.Formatter):
    """Formata cada registro de log como uma linha JSON."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


# ---------------------------------------------------------------------------
# app_logger — logs operacionais
# ---------------------------------------------------------------------------


def _build_app_logger() -> logging.Logger:
    logger = logging.getLogger("senna.app")
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger  # evita duplicar handlers em reimportações

    # Handler de arquivo — rotação diária, mantém 30 dias
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=_APP_LOG_FILE,
        when="midnight",
        backupCount=30,
        encoding="utf-8",
    )
    file_handler.setFormatter(_JsonFormatter())
    file_handler.setLevel(logging.DEBUG)

    # Handler de console — apenas WARNING+ para não poluir a UI
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
    )
    console_handler.setLevel(logging.WARNING)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False

    return logger


app_logger: logging.Logger = _build_app_logger()


# ---------------------------------------------------------------------------
# AuditEntry — contrato de dado para o audit_logger
# ---------------------------------------------------------------------------


class AuditEntry:
    """
    Representa uma entrada de auditoria imutável.

    Campos obrigatórios:
      system_id    — identificador do sistema (ex: "servicos_ti")
      procedure_id — identificador do procedimento (ex: "add_user")
      operator     — usuário do SO que disparou a execução
      success      — True se o procedimento concluiu sem erros
      payload_keys — chaves do payload (nunca valores — segurança RF-06)

    Campos opcionais:
      error        — mensagem de erro em caso de falha
      detail       — informação adicional de contexto (sem dados sensíveis)
    """

    def __init__(
        self,
        *,
        system_id: str,
        procedure_id: str,
        operator: str,
        success: bool,
        payload_keys: list[str],
        error: str | None = None,
        detail: str | None = None,
    ) -> None:
        self.system_id = system_id
        self.procedure_id = procedure_id
        self.operator = operator
        self.success = success
        self.payload_keys = payload_keys
        self.error = error
        self.detail = detail
        self.timestamp: str = datetime.now(tz=timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "system_id": self.system_id,
            "procedure_id": self.procedure_id,
            "operator": self.operator,
            "success": self.success,
            "payload_keys": self.payload_keys,
            "error": self.error,
            "detail": self.detail,
        }


# ---------------------------------------------------------------------------
# AuditLogger — registro imutável de auditoria
# ---------------------------------------------------------------------------


class AuditLogger:
    """
    Grava entradas de auditoria em formato JSONL (uma linha JSON por execução).

    O arquivo é append-only — nunca sobrescrito ou rotacionado automaticamente.
    Cada linha é um registro independente e autocontido (§12 Glossário).

    Uso:
        audit_logger.log_execution(
            AuditEntry(
                system_id="servicos_ti",
                procedure_id="add_user",
                operator="joao.silva",
                success=True,
                payload_keys=["name", "email", "profile"],
            )
        )
    """

    def __init__(self, log_file: Path) -> None:
        self._log_file = log_file

    def log_execution(self, entry: AuditEntry) -> None:
        """
        Persiste a entrada de auditoria.
        Falhas de I/O são registradas no app_logger mas não propagadas —
        um erro de log nunca deve interromper a execução principal.
        """
        try:
            with self._log_file.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")
        except OSError as exc:
            app_logger.error(
                "Falha ao gravar audit log para %s/%s: %s",
                entry.system_id,
                entry.procedure_id,
                exc,
            )


audit_logger: AuditLogger = AuditLogger(_AUDIT_LOG_FILE)
