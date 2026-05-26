# Guia de Prompts — CAgent + QAgent

## Estrutura do Fluxo

```
Prompt CAgent → Implementação → Prompt QAgent → Auditoria → Commit
```

O CAgent cria. O QAgent audita. O commit só acontece depois que ambos passam.

---

## 1. Prompt para o CAgent (Criação de Código)

### Estrutura obrigatória

```
@cagent.md

## Tarefa
<O que fazer — uma frase direta>

## Seções da SPEC
<Listar seções numéricas que o agente deve consultar>

## Arquivos de referência
<Arquivos existentes que servem de modelo ou contexto>

## Restrições
<Qualquer limitação específica desta tarefa>
```

### Por que essa estrutura funciona

| Elemento | Motivo |
|---|---|
| `@cagent.md` | Carrega as regras do agente de criação |
| Seções da SPEC | Evita que o agente leia a SPEC inteira (regra de leitura) |
| Arquivos de referência | Dá contexto sem o agente precisar explorar o projeto |
| Restrições | Delimita escopo (princípio do menor escopo) |

### Exemplo real — Tarefa 2.6

```
@cagent.md

## Tarefa
Implementar o procedimento `extend_access.py` para o sistema Serviços TI.

## Seções da SPEC
- Seção 4 (RF-04 — Execução Individual): payload P3 "Alterar data de expiração"
- Seção 6.2 (Fluxo de Execução)
- Seção 6.3 (Padrão Result)
- Seção 7 (Estrutura de Diretórios): localização em systems/servicos_ti/procedures/

## Arquivos de referência
- `senna/systems/servicos_ti/procedures/search_user_by_cpf.py` — procedimento existente como modelo
- `senna/core/base_procedure.py` — contrato ABC
- `senna/systems/servicos_ti/pages/user_page.py` — page object disponível
- `senna/systems/servicos_ti/locators/user_locators.py` — seletores disponíveis

## Restrições
- Não alterar arquivos fora de `systems/servicos_ti/`
- Usar seletores já existentes em `user_locators.py`; se faltar algum, adicionar lá
- Payload: matrícula (str) + nova_data (date)
```

---

## 2. Prompt para o QAgent (Auditoria)

### Estrutura obrigatória

```
@qagent.md

## Tarefa
Auditar a implementação de <descrição> realizada pelo CAgent.

## Escopo
<Arquivos que devem ser auditados>

## Seções da SPEC para validação
<Seções contra as quais o código deve ser validado>

## Contexto do CAgent
<Resumo do que o CAgent fez — pode ser colado da saída dele>
```

### Por que essa estrutura funciona

| Elemento | Motivo |
|---|---|
| `@qagent.md` | Carrega as regras do agente de QA |
| Escopo explícito | QAgent sabe exatamente o que auditar |
| Seções da SPEC | Validação direcionada, não global |
| Contexto do CAgent | Conecta o handoff — QAgent sabe o que foi feito |

### Exemplo real — Auditoria da tarefa 2.6

```
@qagent.md

## Tarefa
Auditar a implementação do procedimento `extend_access.py` para Serviços TI.

## Escopo
- `senna/systems/servicos_ti/procedures/extend_access.py`
- `senna/systems/servicos_ti/locators/user_locators.py` (se alterado)
- `tests/unit/systems/servicos_ti/test_extend_access.py`

## Seções da SPEC para validação
- Seção 4 (RF-04): payload P3
- Seção 6.3: padrão Result
- Seção 6.4: Page Object Pattern
- Seção 9: regras de commit

## Contexto do CAgent
O CAgent implementou `extend_access.py` com validate + execute,
criou testes unitários com Page mockado, e Ruff/typing passaram.
Commit proposto: `feat: extend_access procedure for servicos_ti`
```

---

## 3. Prompt Combinado (CAgent + QAgent numa sessão)

Para tarefas menores, você pode pedir ambos no mesmo prompt:

```
@cagent.md @qagent.md

## Tarefa
Implementar e auditar <descrição>.

## Seções da SPEC
<seções>

## Arquivos de referência
<arquivos>

## Fluxo esperado
1. CAgent: implementar + testes + Ruff
2. QAgent: auditar conformidade + gerar documentação procedural + atualizar Seção 8
3. Sugerir commit final
```

### Exemplo real — Tarefa 2.6 completa

```
@cagent.md @qagent.md

## Tarefa
Implementar e auditar o procedimento `extend_access.py` para Serviços TI (tarefa 2.6 da SPEC).

## Seções da SPEC
- Seção 4 (RF-04): payload P3
- Seção 6.2, 6.3, 6.4: fluxo, Result, Page Object
- Seção 7: estrutura de diretórios
- Seção 8: plano de desenvolvimento (atualizar ao final)
- Seção 9: regras de commit

## Arquivos de referência
- `senna/systems/servicos_ti/procedures/search_user_by_cpf.py` — modelo
- `senna/core/base_procedure.py` — contrato
- `senna/systems/servicos_ti/pages/user_page.py`
- `senna/systems/servicos_ti/locators/user_locators.py`

## Fluxo esperado
1. CAgent: implementar extend_access.py + testes unitários + Ruff + typing
2. QAgent: auditar conformidade arquitetural + gerar docs/procedures/ + marcar 2.6 na Seção 8
3. Sugerir commit final
```

---

## 4. Dicas Práticas

### ✅ Fazer

- **Citar seções por número** — "Seção 6.3" é melhor que "padrão Result"
- **Apontar arquivos de modelo** — o agente replica padrões existentes
- **Delimitar escopo** — "não alterar fora de X" evita efeitos colaterais
- **Colar saída do CAgent** no prompt do QAgent — conecta o handoff

### 🚫 Evitar

- **Prompts vagos** — "implemente o próximo item" sem citar qual
- **Omitir seções** — força o agente a ler a SPEC inteira (viola regra de leitura)
- **Pedir CAgent e QAgent sem ordem** — o fluxo é CAgent primeiro, QAgent depois
- **Esquecer o `@`** — sem a menção ao arquivo, o agente não carrega as regras
