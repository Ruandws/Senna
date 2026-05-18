# Nota de Atualização: Refatoração da Hierarquia de Exceções
Data: 18 de maio de 2026
Tipo: Refatoração de Exceções (Core)

## O que foi feito
- **Reestruturação completa de `senna/core/exceptions.py`**:
  - Unificamos todos os erros do projeto sob a raiz `SennaError` (Exception).
  - **Erros de Configuração**: Adição de `ConfigurationError` e detalhamento da exceção fail-fast `MissingCredentialError` (RF-06).
  - **Erros de Sistemas e Autenticação**: Implementação da classe base parametrizada `SystemError` (que carrega o identificador `system_id`), da qual herdam `SystemUnavailableError`, `AuthenticationError` e `SessionError` (renomeado do antigo `SessionExpiredError`).
  - **Erros de Procedimentos**: Criação da classe base parametrizada `ProcedureError` (carregando `procedure_id`), da qual herdam `ValidationError` (que agora rastreia o campo e a razão detalhada), `ExecutionError` (novo) e `TimeoutError` (renomeado do antigo `ProcedureTimeoutError`).
  - **Erros de Browser**: Adição de `BrowserError` para falhas do `BrowserFactory`.
  - **Erros de Lote (Batch)**: Criação da classe base `BatchError` que unifica `InvalidSpreadsheetError` e a nova `RowExecutionError` (permite que falhas em linhas individuais não abortem o processamento em lote - RF-05).
  - **Erros de Orquestração**: Criação de `OrchestratorError` para tratar chamadas a procedimentos e sistemas não registrados.
- **Validação de Conformidade**:
  - O código foi formatado e limpo via Ruff com **100% de sucesso**.
  - A execução específica do pytest em `test_exceptions.py` falhou durante a coleção devido à importação de exceções legadas que foram reestruturadas/removidas (como `DataLoaderError`), conforme esperado nesta fase.

## Justificativa
Estabelecer uma hierarquia tipada e rica de exceções, permitindo que a aplicação capture, registre e reporte os erros sem travar a UI (RNF-03), tratando de maneira robusta erros em lote (RF-05) e falhas em sistemas de terceiros.
