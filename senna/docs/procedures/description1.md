# Nota de Atualização: Dependências e Correção do Ruff
Data: 18 de maio de 2026
Tipo: Configuração do pyproject.toml e correção geral do Ruff

## O que foi feito
- **Configuração do pyproject.toml**: O arquivo `pyproject.toml` foi atualizado incluindo metadados do projeto, dependências principais tipadas, dependências opcionais de desenvolvimento (`dev`), descoberta automatizada de pacotes e opções de execução do `pytest` com regras de cobertura mínima de 80%.
- **Resolução de pendências do Ruff**: Para cumprir o requisito de "Zero erros Ruff" estabelecido na especificação:
  - Corrigido o erro de `Undefined name Path` (F821) em `tests/unit/core/test_config.py` importando `Path` no escopo do módulo e formatando as assinaturas de funções de teste.
  - Divididos comentários e docstrings longas em vários arquivos (`senna/core/config.py`, `senna/core/exceptions.py`, `senna/core/logger.py` e `senna/core/models.py`) para respeitar o limite de 88 caracteres por linha.
- **Validação de Testes**: Todos os 81 testes unitários e de integração passaram perfeitamente com 100% de cobertura.

## Justificativa
Alinhar as dependências do projeto e as ferramentas de teste e linting à especificação do projeto, além de garantir que a base de código esteja totalmente em conformidade com as regras de estilo de código e livre de avisos do linter antes da consolidação do commit.
