# Nota de Atualização: Reescrita Completa da Suíte de Testes Unitários do Core
Data: 18 de maio de 2026
Tipo: Reescrita de Testes Unitários (Core)

## O que foi feito
- **Reescrita integral de 4 arquivos de teste** para alinhar com as novas implementações do core:

### test_exceptions.py (26 testes)
- Hierarquia completa validada: `SennaError` → subclasses de configuração, sistema, procedimento, browser, batch e orquestração.
- Atributos customizados testados: `SystemError.system_id`, `ProcedureError.procedure_id`, `ValidationError.field`/`reason`, `InvalidSpreadsheetError.path`, `RowExecutionError.row_index`.
- Mensagens formatadas verificadas (ex: `[servicos_ti] fora do ar`).
- Cadeias de captura validadas (`except SennaError` captura toda a árvore).

### test_result.py (15 testes)
- `Result.ok()` e `Result.fail()` com acesso direto a `.value` e `.error` (sem `ValueError`).
- `unwrap()` e `unwrap_error()` com `RuntimeError` em uso incorreto.
- Imutabilidade (`FrozenInstanceError`) e `__repr__` legível.
- Testes obsoletos removidos: `.map()` (removido do source) e `ValueError` em properties (substituídas por atributos diretos).

### test_models.py (17 testes)
- Novos payloads P1–P4: `UserPayload`, `RemovalPayload`, `AccessPayload`, `ProfilePayload`.
- `ProfileAction` (StrEnum): valores `grant`/`revoke` e compatibilidade com `str`.
- `RemovalPayload`: campos opcionais (`registration`, `login`) testados em todas as combinações.
- `ExecutionRecord` (RF-05): instanciação, falha e imutabilidade.
- Testes obsoletos removidos: `BaseUserPayload`, `BaseAccessPayload`, payloads Serviços TI e Integra legados.

### test_logger.py (15 testes)
- `app_logger.name` atualizado de `"senna"` para `"senna.app"`.
- `AuditEntry.to_dict()`: todos os campos obrigatórios, campos opcionais (error/detail), timestamp ISO 8601 timezone-aware.
- `AuditLogger.log_execution()`: criação de arquivo, JSON válido, valores corretos, múltiplas entradas append-only, registro de falhas.
- Falha de I/O não propaga: testado com caminho impossível (`Z:/...`), confirmando que `OSError` é engolida.
- Testes obsoletos removidos: `.write()`, `_audit_dir`, mascaramento de dados sensíveis (agora feito via `payload_keys`).

### test_config.py (7 testes) — mantido inalterado
- Já estava 100% alinhado com a nova implementação desde a etapa anterior.

## Validação
- **Cascata regressiva**: cada arquivo foi testado isoladamente e depois em conjunto com todos os anteriores, confirmando ausência de regressões.
- **Teste end-to-end final**: `pytest --no-cov tests/unit/core/ -v` → **80 passed in 0.64s**.
- **Ruff**: todos os 4 arquivos passaram em lint e formatação com zero erros.

## Justificativa
Garantir que toda a base de testes unitários reflita fielmente as novas interfaces, contratos e comportamentos implementados no core do Senna, eliminando completamente os testes legados que referenciavam classes e métodos removidos.
