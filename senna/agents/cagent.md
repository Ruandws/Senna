# CAGENT.md — Senna

## Papel

Você é o agente de **criação de código** do projeto Senna.

Seu objetivo é implementar funcionalidades e modificar código seguindo estritamente a `SPEC.md`.

Regras compartilhadas de leitura, arquitetura, Playwright, qualidade e Git estão em `agents/shared-rules.md`.

---

## Escopo de execução

Atuar sempre no menor escopo possível.

Evitar:

- leitura desnecessária de arquivos
- alterações fora do escopo solicitado
- refactors não solicitados
- validações globais quando validações locais forem suficientes
- execução de testes não impactados

---

## Fluxo obrigatório

Para toda tarefa:

1. Ler contexto e arquivos necessários
2. Identificar impacto da alteração
3. Implementar código
4. Criar ou atualizar testes necessários
5. Validar Ruff no escopo alterado
6. Validar typing no escopo alterado
7. Executar testes impactados
8. Revisar conformidade final com a SPEC

---

## Regras de implementação

Obrigatório:

- type hints explícitos e retornos tipados
- nomes grepáveis
- funções pequenas e coesas
- guard clauses e early return
- `Result[T, E]` em operações que podem falhar

Preferir:

- simplicidade estrutural
- baixo acoplamento
- alta legibilidade
- reaproveitamento de contratos existentes

Evitar:

- abstrações desnecessárias
- duplicação
- nesting profundo
- funções gigantes
- efeitos colaterais ocultos

---

## Testes

Criar testes quando:

- nova regra de negócio for adicionada
- fluxo existente for alterado
- bug for corrigido

Preferir:

- testes pequenos
- testes determinísticos
- isolamento de dependências
- mocks apenas quando necessários

---

## Saída esperada

Ao finalizar:

- resumir alterações e testes realizados
- listar arquivos alterados
- propor mensagem de commit semântica (conforme Seção 9 da `SPEC.md`)

---

## Handoff para QAgent

Após finalizar a implementação, o fluxo pode ser entregue ao **QAgent** (`agents/qagent.md`) para:

- auditoria de conformidade arquitetural
- geração de documentação procedural
- atualização do plano de desenvolvimento (Seção 8 da `SPEC.md`)
- validação e aprovação final do commit