# SHARED-RULES.md — Senna

> Regras comuns a todos os agentes. Importado por `cagent.md` e `qagent.md`.

---

## Fonte da verdade

A `SPEC.md` é a fonte da verdade do projeto.
Critérios técnicos de qualidade, code style e boundaries estão em `spec/quality-gates.md`.

---

## Regra de leitura

NUNCA leia a `SPEC.md` inteira automaticamente.

Leia APENAS:

- seções explicitamente informadas no prompt
- arquivos diretamente relacionados à tarefa
- `ruff.toml`
- `pyproject.toml` quando necessário

Se existir ambiguidade arquitetural ou a seção necessária não for informada:
PARE e solicite esclarecimento.

---

## Regras arquiteturais

### Procedures

Nunca:

- conter seletores
- acessar UI
- quebrar isolamento do sistema

### Pages

Responsáveis por:

- comportamento da tela
- interação Playwright

### Locators

Responsáveis apenas por:

- seletores

### Core

Nunca depende de `systems`.

---

## Regras Playwright

Preferir:

1. `get_by_role(...)`
2. `locator(...)`
3. waits explícitos

Proibido:

- XPath absoluto
- `time.sleep(...)`
- waits arbitrários
- lógica Playwright dentro de procedures

---

## Regras de qualidade

Seguir integralmente o `spec/quality-gates.md`.

Resumo operacional:

- type hints explícitos e retornos tipados
- `Result[T, E]` em operações que podem falhar
- zero erros Ruff no escopo alterado
- nomes grepáveis (proibido: `data`, `tmp`, `obj`, `handle`, `manager`)
- guard clauses e early return
- nenhuma exceção não tratada chegando à UI
- credenciais apenas em `.env`, nunca em código ou logs

---

## Validação obrigatória

Se qualquer validação falhar:

- interromper
- corrigir
- revalidar

Commit é proibido antes de tudo passar.

---

## Workflow Git

Seguir estritamente a Seção 9 da `SPEC.md`.

Resumo:

- Formato: `<tipo>: <descrição curta>` (`feat`, `fix`, `refactor`, `test`, `chore`, `docs`)
- Um commit = uma mudança lógica
- Commits vagos são proibidos
