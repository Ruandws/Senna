"""
Testes unitários para senna.core.logger

O QUÊ: valida que app_logger retorna um Logger configurado e que
       AuditLogger.write() grava uma entrada JSONL válida em disco.
PARA QUÊ: um audit_logger silencioso que não grava nada quebra a rastreabilidade
          exigida pelo SPEC (RF-07 / seção 18.1). Testar aqui confirma o contrato.
COMO: usa o fixture `tmp_path` do pytest para criar um diretório temporário
      real (mas descartado após o teste) — assim AuditLogger grava em disco
      sem poluir logs/audit/. Nenhuma rede, nenhum browser.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from senna.core.logger import AuditLogger, app_logger

# =============================================================================
# app_logger
# =============================================================================


def test_app_logger_is_logging_instance() -> None:
    """app_logger deve ser um logging.Logger padrão."""
    assert isinstance(app_logger, logging.Logger)


def test_app_logger_name_is_senna() -> None:
    """O logger da aplicação deve ter o nome 'senna' para hierarquia de loggers."""
    assert app_logger.name == "senna"


def test_app_logger_has_at_least_one_handler() -> None:
    """Logger deve ter pelo menos um handler configurado (StreamHandler)."""
    assert len(app_logger.handlers) >= 1


def test_app_logger_level_is_set() -> None:
    """Logger deve ter um nível definido (não NOTSET=0)."""
    # NOTSET=0 significa que herda do pai sem nível próprio
    assert app_logger.level != logging.NOTSET


# =============================================================================
# AuditLogger — instanciação
# =============================================================================


def test_audit_logger_instantiation(tmp_path: Path) -> None:
    """AuditLogger deve instanciar sem erros dado um diretório válido."""
    logger = AuditLogger(tmp_path)
    assert logger._audit_dir == tmp_path


# =============================================================================
# AuditLogger.write — estrutura do arquivo JSONL
# =============================================================================


def test_write_creates_jsonl_file(tmp_path: Path) -> None:
    """write() deve criar um arquivo .jsonl no diretório de auditoria."""
    logger = AuditLogger(tmp_path)
    logger.write(
        system="servicos_ti",
        procedure="add_user",
        payload_summary={"name": "Joao"},
        success=True,
    )
    arquivos_jsonl = list(tmp_path.glob("*.jsonl"))
    assert len(arquivos_jsonl) == 1


def test_write_masks_sensitive_data(tmp_path: Path) -> None:
    """O logger deve mascarar nativamente campos sensíveis como cpf ou password."""
    logger = AuditLogger(tmp_path)
    logger.write(
        system="servicos_ti",
        procedure="add_user",
        payload_summary={"cpf": "12345678901", "name": "Joao", "PASSWORD": "123"},
        success=True,
    )
    arquivo = next(tmp_path.glob("*.jsonl"))
    entry = json.loads(arquivo.read_text(encoding="utf-8").strip())
    
    assert entry["payload_summary"]["cpf"] == "***"
    assert entry["payload_summary"]["PASSWORD"] == "***"
    assert entry["payload_summary"]["name"] == "Joao"


def test_write_entry_is_valid_json(tmp_path: Path) -> None:
    """Cada linha do .jsonl deve ser um JSON válido e parseável."""
    logger = AuditLogger(tmp_path)
    logger.write(
        system="servicos_ti",
        procedure="add_user",
        payload_summary={"name": "Joao"},
        success=True,
    )
    arquivo = next(tmp_path.glob("*.jsonl"))
    linhas = arquivo.read_text(encoding="utf-8").strip().splitlines()
    assert len(linhas) == 1
    entry = json.loads(linhas[0])
    assert isinstance(entry, dict)


def test_write_entry_contains_required_fields(tmp_path: Path) -> None:
    """A entrada deve conter todos os campos obrigatórios definidos no SPEC."""
    logger = AuditLogger(tmp_path)
    logger.write(
        system="aghux",
        procedure="remove_user",
        payload_summary={"username": "jsilva"},
        success=False,
        detail="usuário não encontrado",
    )
    arquivo = next(tmp_path.glob("*.jsonl"))
    entry = json.loads(arquivo.read_text(encoding="utf-8").strip())

    assert "timestamp" in entry
    assert "system" in entry
    assert "procedure" in entry
    assert "payload_summary" in entry
    assert "success" in entry
    assert "detail" in entry


def test_write_entry_values_are_correct(tmp_path: Path) -> None:
    """Os valores gravados devem refletir exatamente o que foi passado."""
    logger = AuditLogger(tmp_path)
    logger.write(
        system="integra",
        procedure="grant_profile",
        payload_summary={"username": "mrocha", "profile": "MEDICO"},
        success=True,
        detail="perfil concedido com sucesso",
    )
    arquivo = next(tmp_path.glob("*.jsonl"))
    entry = json.loads(arquivo.read_text(encoding="utf-8").strip())

    assert entry["system"] == "integra"
    assert entry["procedure"] == "grant_profile"
    assert entry["payload_summary"]["profile"] == "MEDICO"
    assert entry["success"] is True
    assert entry["detail"] == "perfil concedido com sucesso"


def test_write_success_false_is_recorded(tmp_path: Path) -> None:
    """Falhas também devem ser gravadas — audit log cobre o caminho de erro."""
    logger = AuditLogger(tmp_path)
    logger.write(
        system="servicos_ti",
        procedure="add_user",
        payload_summary={"name": "Joao"},
        success=False,
        detail="timeout ao submeter formulário",
    )
    arquivo = next(tmp_path.glob("*.jsonl"))
    entry = json.loads(arquivo.read_text(encoding="utf-8").strip())
    assert entry["success"] is False


def test_write_multiple_entries_appends(tmp_path: Path) -> None:
    """Múltiplos write() no mesmo dia devem acrescentar linhas, não sobrescrever."""
    logger = AuditLogger(tmp_path)
    for i in range(3):
        logger.write(
            system="servicos_ti",
            procedure=f"procedimento_{i}",
            payload_summary={},
            success=True,
        )
    arquivo = next(tmp_path.glob("*.jsonl"))
    linhas = arquivo.read_text(encoding="utf-8").strip().splitlines()
    assert len(linhas) == 3


def test_write_timestamp_is_iso_format(tmp_path: Path) -> None:
    """timestamp deve estar em formato ISO 8601 (parseável pelo stdlib)."""
    from datetime import datetime

    logger = AuditLogger(tmp_path)
    logger.write(
        system="servicos_ti",
        procedure="add_user",
        payload_summary={},
        success=True,
    )
    arquivo = next(tmp_path.glob("*.jsonl"))
    entry = json.loads(arquivo.read_text(encoding="utf-8").strip())
    # datetime.fromisoformat() levanta ValueError se o formato estiver errado
    parsed = datetime.fromisoformat(entry["timestamp"])
    assert parsed.tzinfo is not None  # deve ser timezone-aware (UTC)


def test_write_detail_defaults_to_empty_string(tmp_path: Path) -> None:
    """Quando detail não é informado, deve ser gravado como string vazia."""
    logger = AuditLogger(tmp_path)
    logger.write(
        system="servicos_ti",
        procedure="add_user",
        payload_summary={},
        success=True,
        # detail omitido intencionalmente
    )
    arquivo = next(tmp_path.glob("*.jsonl"))
    entry = json.loads(arquivo.read_text(encoding="utf-8").strip())
    assert entry["detail"] == ""
