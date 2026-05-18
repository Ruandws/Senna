# configura logging estruturado uma vez; audit_logger separado em logs/audit/

from __future__ import annotations

from datetime import datetime, timezone
import json
import logging
import logging.handlers
from pathlib import Path

from senna.core.config import settings

_ROOT = Path(__file__).resolve().parents[2]
_AUDIT_DIR = _ROOT / settings.log.audit_dir
_AUDIT_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# App Logger
# =============================================================================


def _build_app_logger() -> logging.Logger:
    logger = logging.getLogger("senna")
    logger.setLevel(settings.log.level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(handler)

    return logger


app_logger: logging.Logger = _build_app_logger()


# =============================================================================
# Audit Logger
# =============================================================================


class AuditLogger:
    def __init__(self, audit_dir: Path) -> None:
        self._audit_dir = audit_dir

    def write(
        self,
        *,
        system: str,
        procedure: str,
        payload_summary: dict,
        success: bool,
        detail: str = "",
    ) -> None:
        safe_summary = {}
        for k, v in payload_summary.items():
            if k.lower() in {"cpf", "password", "senha", "secret", "token"}:
                safe_summary[k] = "***"
            else:
                safe_summary[k] = v

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system": system,
            "procedure": procedure,
            "payload_summary": safe_summary,
            "success": success,
            "detail": detail,
        }
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        log_file = self._audit_dir / f"{date_str}.jsonl"

        with log_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


audit_logger: AuditLogger = AuditLogger(_AUDIT_DIR)
