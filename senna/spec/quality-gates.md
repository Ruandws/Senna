
# Critérios técnicos obrigatórios
## 1. Requisitos Não Funcionais

| ID | Requisito | Meta |
|----|----------|------|
| RNF-01 | Tempo máximo por procedimento | 60 segundos |
| RNF-02 | Feedback visual durante execução | Indicador de progresso em toda execução |
| RNF-03 | Tratamento de exceções | Capturadas e registradas sem travar a UI |
| RNF-04 | Isolamento de sistema | Sem alteração de código fora do subpacote do sistema |
| RNF-05 | Qualidade de código | Zero erros Ruff; cobertura de testes ≥ 100% |
| RNF-06 | Compatibilidade | Windows 10+ |
| RNF-07 | Segurança de credenciais | Apenas em `.env`, nunca em código ou logs |

---

## 2.  Definição de Pronto

Uma funcionalidade está **pronta** quando:

1. Código implementado e passando em `ruff check .` sem erros.
2. Testes unitários escritos e verdes.
3. Testes de integração escritos e verdes (quando aplicável).
4. Log de auditoria gerado corretamente para o caminho feliz e para falhas.
5. `Result[T, E]` retornado corretamente — sem exceções não tratadas chegando à UI.
6. Código commitado com mensagem semântica (`feat:`, `fix:`, `test:`, `refactor:`).

---

## 3. Code Style

### 3.1 Tipagem Forte

Todo código Python deve usar type hints explícitos em parâmetros, retornos, atributos de classe e dataclasses. Retorno `None` também deve ser declarado.

```python
# Obrigatório
def add_user(payload: UserPayload) -> Result[User, Error]: ...

# Proibido
def add_user(payload): ...
```

Payloads devem ser modelados como dataclasses tipadas. Dicionários soltos são proibidos para dados críticos de execução.

```python
@dataclass
class UserPayload:
    name: str
    email: str
    profile: str
```

### 3.2 Nomenclatura Grepável

Nomes devem ser significativos, únicos e fáceis de localizar por busca.

| Padrão | Exemplos ✅ | Exemplos 🚫 |
|--------|-----------|------------|
| Variáveis | `user_payload`, `login_response` | `data`, `obj`, `tmp`, `value` |
| Classes | `UserPage`, `AddUserProcedure`, `BrowserFactory` | `Manager`, `Handler`, `Processor` |
| Funções | `create_user`, `validate_payload`, `open_browser_context` | `do_it`, `handle`, `process` |

### 3.3 Simplicidade Estrutural

Prefira guard clauses, early return e funções pequenas e coesas. Evite funções gigantes, condições complexas e aninhamento profundo.

---

# Boundaries

### ✅ Sempre
- Registrar auditoria por execução, inclusive em falhas.
- Tratar erros sem deixar exceções não tratadas chegarem à UI.
- Preservar isolamento por sistema e por `BrowserContext`.
- Corrigir falhas antes de prosseguir para a próxima tarefa.

### ⚠️ Perguntar antes
- Alterar arquitetura base.
- Adicionar novo sistema fora do padrão previsto.
- Mudar o contrato de `Result[T, E]`.
- Mudar o formato do audit log.
- Alterar estratégia de execução em lote.
- Introduzir paralelismo.
- Alterar o fluxo de login ou logout.
- Criar exceção para um comportamento não previsto.
- Mudar o padrão de naming do projeto.
- Relaxar regra de tipagem ou lint.

### 🚫 Nunca
- Expor credenciais em logs, UI ou código.
- Gravar segredo em arquivo versionado.
- Usar dicionários soltos onde houver contrato tipado.
- Criar nomes genéricos (`data`, `tmp`, `obj`, `handle`, `manager`).
- Deixar exceção não tratada chegar à interface.
- Alterar comportamento sem atualizar os testes correspondentes.