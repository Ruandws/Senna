"""
Testes unitários para senna.core.logger

O QUÊ: valida que app_logger retorna um Logger configurado e que
       AuditLogger.log_execution() grava uma entrada JSONL válida em disco.
PARA QUÊ: um audit_logger silencioso que não grava nada quebra a
          rastreabilidade exigida pelo SPEC (RF-06 / §12).
COMO: usa o fixture `tmp_path` do pytest para criar um arquivo temporário
      real (mas descartado após o teste) — assim AuditLogger grava em disco
      sem poluir logs/audit/. Nenhuma rede, nenhum browser.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from senna.core.logger import AuditEntry, AuditLogger, app_logger

# =========================================================================
# app_logger
# =========================================================================


def test_app_logger_is_logging_instance() -> None:
    """app_logger deve ser um logging.Logger padrão."""
    assert isinstance(app_logger, logging.Logger)


def test_app_logger_name_is_senna_app() -> None:
    """O logger da aplicação deve ter o nome 'senna.app'."""
    assert app_logger.name == "senna.app"


def test_app_logger_has_at_least_one_handler() -> None:
    """Logger deve ter pelo menos um handler configurado."""
    assert len(app_logger.handlers) >= 1


def test_app_logger_level_is_set() -> None:
    """Logger deve ter um nível definido (não NOTSET=0)."""
    assert app_logger.level != logging.NOTSET


# =========================================================================
# AuditEntry — contrato de dados
# =========================================================================


def test_audit_entry_to_dict_contains_all_fields() -> None:
    """to_dict() deve retornar dicionário com todos os campos obrigatórios."""
    entry = AuditEntry(
        system_id="servicos_ti",
        procedure_id="add_user",
        operator="joao.silva",
        success=True,
        payload_keys=["name", "email"],
    )
    d = entry.to_dict()

    assert "timestamp" in d
    assert d["system_id"] == "servicos_ti"
    assert d["procedure_id"] == "add_user"
    assert d["operator"] == "joao.silva"
    assert d["success"] is True
    assert d["payload_keys"] == ["name", "email"]
    assert d["error"] is None
    assert d["detail"] is None


def test_audit_entry_with_error() -> None:
    """to_dict() deve incluir error e detail quando preenchidos."""
    entry = AuditEntry(
        system_id="aghux",
        procedure_id="remove_user",
        operator="admin",
        success=False,
        payload_keys=["username"],
        error="Usuário não encontrado",
        detail="Tentativa 2 de 3",
    )
    d = entry.to_dict()

    assert d["success"] is False
    assert d["error"] == "Usuário não encontrado"
    assert d["detail"] == "Tentativa 2 de 3"


def test_audit_entry_timestamp_is_iso_format() -> None:
    """timestamp deve estar em formato ISO 8601 timezone-aware."""
    from datetime import datetime

    entry = AuditEntry(
        system_id="s",
        procedure_id="p",
        operator="op",
        success=True,
        payload_keys=[],
    )
    parsed = datetime.fromisoformat(entry.timestamp)
    assert parsed.tzinfo is not None


# =========================================================================
# AuditLogger — instanciação
# =========================================================================


def test_audit_logger_instantiation(tmp_path: Path) -> None:
    """AuditLogger deve instanciar sem erros dado um arquivo válido."""
    log_file = tmp_path / "audit.jsonl"
    logger = AuditLogger(log_file)
    assert logger._log_file == log_file


# =========================================================================
# AuditLogger.log_execution — gravação em arquivo JSONL
# =========================================================================


def _make_entry(**overrides: object) -> AuditEntry:
    """Helper para criar AuditEntry com defaults sensatos."""
    defaults = {
        "system_id": "servicos_ti",
        "procedure_id": "add_user",
        "operator": "joao.silva",
        "success": True,
        "payload_keys": ["name", "email"],
    }
    defaults.update(overrides)
    return AuditEntry(**defaults)  # type: ignore[arg-type]


def test_log_execution_creates_jsonl_file(tmp_path: Path) -> None:
    """log_execution() deve criar o arquivo JSONL."""
    log_file = tmp_path / "audit.jsonl"
    logger = AuditLogger(log_file)
    logger.log_execution(_make_entry())
    assert log_file.exists()


def test_log_execution_entry_is_valid_json(tmp_path: Path) -> None:
    """Cada linha do .jsonl deve ser um JSON válido e parseável."""
    log_file = tmp_path / "audit.jsonl"
    logger = AuditLogger(log_file)
    logger.log_execution(_make_entry())

    linhas = log_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(linhas) == 1
    entry = json.loads(linhas[0])
    assert isinstance(entry, dict)


def test_log_execution_entry_contains_required_fields(
    tmp_path: Path,
) -> None:
    """A entrada deve conter todos os campos definidos em AuditEntry."""
    log_file = tmp_path / "audit.jsonl"
    logger = AuditLogger(log_file)
    logger.log_execution(
        _make_entry(success=False, error="timeout", detail="detalhe"),
    )

    entry = json.loads(
        log_file.read_text(encoding="utf-8").strip(),
    )
    for key in (
        "timestamp",
        "system_id",
        "procedure_id",
        "operator",
        "success",
        "payload_keys",
        "error",
        "detail",
    ):
        assert key in entry, f"Campo '{key}' ausente no registro"


def test_log_execution_values_are_correct(tmp_path: Path) -> None:
    """Os valores gravados devem refletir exatamente o que foi passado."""
    log_file = tmp_path / "audit.jsonl"
    logger = AuditLogger(log_file)
    logger.log_execution(
        _make_entry(
            system_id="integra",
            procedure_id="grant_profile",
            success=True,
            detail="perfil concedido",
        ),
    )

    entry = json.loads(log_file.read_text(encoding="utf-8").strip())
    assert entry["system_id"] == "integra"
    assert entry["procedure_id"] == "grant_profile"
    assert entry["success"] is True
    assert entry["detail"] == "perfil concedido"


def test_log_execution_multiple_entries_appends(tmp_path: Path) -> None:
    """Múltiplas chamadas devem acrescentar linhas, não sobrescrever."""
    log_file = tmp_path / "audit.jsonl"
    logger = AuditLogger(log_file)
    for i in range(3):
        logger.log_execution(
            _make_entry(procedure_id=f"proc_{i}"),
        )

    linhas = log_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(linhas) == 3


def test_log_execution_failure_is_recorded(tmp_path: Path) -> None:
    """Falhas devem ser gravadas — audit log cobre o caminho de erro."""
    log_file = tmp_path / "audit.jsonl"
    logger = AuditLogger(log_file)
    logger.log_execution(
        _make_entry(success=False, error="timeout ao submeter"),
    )

    entry = json.loads(log_file.read_text(encoding="utf-8").strip())
    assert entry["success"] is False
    assert entry["error"] == "timeout ao submeter"


# =========================================================================
# AuditLogger — falha de I/O não propaga
# =========================================================================


def test_log_execution_io_error_does_not_propagate() -> None:
    """Falha de I/O deve ser engolida e registrada, nunca propagada."""
    # Aponta para um caminho inexistente e impossível de criar
    log_file = Path("Z:/caminho/impossivel/audit.jsonl")
    logger = AuditLogger(log_file)

    # Não deve levantar exceção — o erro é engolido internamente
    logger.log_execution(_make_entry())
