# Nota de Atualização: Correção dos Testes Unitários de Configuração
Data: 18 de maio de 2026
Tipo: Refatoração da Suíte de Testes (Core)

## O que foi feito
- **Reescrita de `tests/unit/core/test_config.py`**:
  - Adaptamos todos os testes para refletir a nova arquitetura do módulo `config.py` e sua classe `Config`.
  - Implementamos testes isolados para as funções auxiliares `_merge`, `_validate_credentials` (tanto para o fluxo de sucesso quanto para o fluxo de erro).
  - Desenvolvemos testes focados no comportamento da instância `Config`, cobrindo os métodos `get()`, `require()` e `debug_browser()`.
  - Utilizamos a fixture `monkeypatch` do pytest para mockar a leitura de `settings.toml` e `.env`, garantindo que os testes unitários sejam completamente isolados de variáveis e arquivos reais no sistema local.
  - Ajustamos todas as linhas de comentários, docstrings e mocks para cumprir rigorosamente o limite de 100 colunas definido no `ruff.toml`.
- **Validação de Conformidade**:
  - Todos os 7 testes unitários criados passaram com sucesso (`100% PASSED`).
  - O Ruff validou o arquivo com **zero erros ou avisos**.

## Justificativa
Garantir a estabilidade e a corretude do novo módulo core de configuração sem poluir ou depender de arquivos do sistema do usuário, mantendo a suíte de testes unitários confiável, rápida e limpa.
