# Nota de Atualização: Refatoração do Sistema de Logging e Auditoria
Data: 18 de maio de 2026
Tipo: Refatoração Arquitetural de Log e Auditoria (Core)

## O que foi feito
- **Reestruturação completa de `senna/core/logger.py`**:
  - **Dois Loggers Especializados**:
    - `app_logger`: Focado no desenvolvedor e operações internas. Implementamos `TimedRotatingFileHandler` com rotação diária (mantendo 30 dias de histórico). Exibição configurada no console apenas para alertas e erros críticos (`WARNING+`), e gravação em arquivo no formato JSON estruturado (`_JsonFormatter`). O logger agora tem o nome `senna.app`.
    - `audit_logger`: Focado no Coordenador de TI para auditoria (RF-06). Registro imutável, append-only, em arquivo JSONL (`audit.jsonl`). Asseguramos que erros de I/O na gravação de logs de auditoria não travem o fluxo principal da aplicação (captura interna de `OSError`).
  - **Introdução de `AuditEntry`**:
    - Criamos a classe `AuditEntry` para padronizar e estruturar os dados de auditoria (timestamp UTC, operator, system_id, procedure_id, success, payload_keys, error, detail).
    - **Segurança de Dados**: O logger agora recebe apenas chaves de payload (`payload_keys`), nunca os valores sensíveis (como CPFs, senhas, etc.), cumprindo perfeitamente a segurança estipulada em §12 e RF-06.
- **Validação de Conformidade**:
  - O arquivo `logger.py` passou no linter Ruff com **100% de sucesso (zero erros)**.
  - A execução de testes unitários (`test_logger.py`) falhou na maioria dos casos devido à incompatibilidade com o design anterior (o teste legado tenta instanciar `AuditLogger` com diretório e chamar o método `write()` removido). A adaptação dos testes da suíte do logger ocorrerá posteriormente conforme a ordem do projeto.

## Justificativa
Garantir total isolamento e independência entre logs de depuração operacional (que rotacionam e limpam logs velhos) e logs de auditoria jurídica de execução (que devem ser imutáveis e append-only). O padrão `AuditEntry` garante segurança de compliance eliminando chances de vazamento de credenciais ou dados sensíveis em disco.
