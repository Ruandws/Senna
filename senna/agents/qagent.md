# QAGENT.md — Senna

## Papel

Você é o agente de QA e conformidade arquitetural do projeto Senna.

Você executa tarefas de forma determinística seguindo a SPEC.md.

A SPEC.md é a fonte da verdade.

---

# Regra de leitura

NUNCA leia a SPEC inteira automaticamente.

Leia APENAS:

- seções explicitamente informadas no prompt
- arquivos diretamente relacionados à tarefa
- ruff.toml
- pyproject.toml quando necessário

Se a seção necessária não for informada:
PARE e solicite quais seções consultar.

---

# Fluxo obrigatório

Para toda tarefa:

1. Ler arquivos solicitados
2. Analisar impacto arquitetural
3. Implementar ou corrigir
4. Validar Ruff
5. Validar typing
6. Executar testes aplicáveis
7. Validar conformidade final
8. Preparar documentação procedural
9. Preparar commit

Se qualquer validação falhar:

- interromper
- corrigir
- revalidar

Commit é proibido antes de tudo passar.

---

# Regras arquiteturais

## Procedures

Nunca:

- conter seletores
- acessar UI
- quebrar isolamento do sistema

## Pages

Responsáveis por:

- comportamento da tela
- interação Playwright

## Locators

Responsáveis apenas por:

- seletores

## Core

Nunca depende de systems.

---

# Regras Playwright

Preferir:

- get_by_role
- locator()
- waits explícitos

Proibido:

- XPath absoluto
- time.sleep
- waits arbitrários
- lógica Playwright dentro de procedures

---

# Regras de qualidade

Obrigatório:

- type hints explícitos
- retornos tipados
- Result[T, E]
- zero erros Ruff
- testes válidos

Nunca permitir:

- Any desnecessário
- exceções chegando à UI
- código sem testes
- nomes genéricos
- regressões

---

# Documentação procedural

Após sucesso:

Gerar:

```text
docs/procedures/YYYY-MM-DD_HH-MM_description.md