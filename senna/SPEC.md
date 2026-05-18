# SPEC.MD — Especificação de Requisitos: Senna
> Fonte da verdade do projeto. Toda decisão de arquitetura, escopo e implementação deve ser validada contra este documento.

---

## 1. Visão Geral

O **Senna** é uma aplicação desktop em Python que centraliza automações web voltadas à gestão de usuários em sistemas hospitalares.

O técnico de TI, ao receber um chamado, abre o Senna, seleciona o sistema-alvo, escolhe o procedimento desejado, preenche o formulário e dispara a automação. O Senna executa o fluxo via Playwright em segundo plano e exibe o resultado na interface.

**Usuários:** Técnico de TI (executa procedimentos), Coordenador de TI (consulta logs de auditoria), Desenvolvedor (estende o Senna com novos sistemas e procedimentos).

---

## 2. Objetivos

| # | Objetivo | Critério de Sucesso |
|---|----------|---------------------|
| O1 | Automatizar procedimentos repetitivos | Execução de ponta a ponta sem intervenção manual |
| O2 | Centralizar 5 sistemas na mesma interface | Todos os sistemas operáveis a partir do Senna |
| O4 | Permitir processamento em lote via planilha | Importação de XLSX validado pelo Senna |
| O5 | Facilitar extensão para novos sistemas e procedimentos | Novo sistema = nova pasta com contratos já definidos |

---

## 3. Stack de Tecnologias

| Componente | Tecnologia | Versão |
|------------|-----------|--------|
| Linguagem | Python | 3.14 |
| Automação Web | Playwright | 1.58 |
| Interface Gráfica | CustomTkinter | 5.2.2 |
| Processamento de Dados | Pandas | 3.0.1 |
| Manipulação de Planilhas | openpyxl | >=3.1.5 |
| Variáveis de Ambiente | python-dotenv | >=1.0 |
| Linter | Ruff | latest |
| Versionamento | Git | — |
| Gerenciador de Projeto | pyproject.toml | PEP 517 |

---

## 4. Requisitos Funcionais

### RF-01 — Seleção de Sistema
- A UI deve exibir somente sistemas registrados em `AVAILABLE_SYSTEMS`.

### RF-02 — Seleção de Procedimento
- A UI deve exibir somente procedimentos disponíveis para o sistema selecionado.

### RF-03 — Formulário Dinâmico
- A UI deve exibir o formulário correspondente ao procedimento selecionado.
- Campos obrigatórios são validados antes do envio.
- Mensagens de erro são exibidas inline, próximas ao campo inválido.

### RF-04 — Execução Individual
Após o usuário preencher o formulário e clicar em "Executar", o Senna instancia o procedimento via `Orchestrator`, passa o payload e aguarda o `Result`, exibido na interface.

Procedimentos disponíveis (aplicam-se a todos os sistemas que os suportem; disponibilidade declarada em `AVAILABLE_SYSTEMS`):

| ID | Procedimento | Payload |
|----|-------------|---------|
| P1 | Adicionar usuário | nome, matrícula, e-mail, perfil |
| P2 | Remover usuário | matrícula ou login |
| P3 | Alterar data de expiração | matrícula, nova data |
| P4 | Conceder/revogar perfil de acesso | matrícula, perfil, ação (grant/revoke) |

### RF-05 — Execução em Lote
- O usuário importa um arquivo XLSX, validado em colunas obrigatórias pelo `DataLoader`.
- O Senna executa cada linha como execução individual sequencial.
- Um relatório consolidado é salvo em `data/output/`.

### RF-06 — Gerenciamento de Credenciais
- As credenciais dos sistemas são lidas de variáveis de ambiente (`.env`).
- Nunca são exibidas na interface ou gravadas em logs.
- O Senna alerta o técnico se uma credencial obrigatória estiver ausente ao inicializar.

### RF-08 — Sessão Isolada por Sistema
- Cada sistema abre e gerencia seu próprio `BrowserContext` isolado via `BrowserFactory`.
- A sessão é encerrada ao finalizar todos os procedimentos do sistema ou em caso de erro não recuperável.

---

## 5. Requisitos Não Funcionais

| ID | Requisito | Meta |
|----|----------|------|
| RNF-01 | Tempo máximo por procedimento | 60 segundos |
| RNF-02 | Feedback visual durante execução | Indicador de progresso em toda execução |
| RNF-03 | Tratamento de exceções | Capturadas e registradas sem travar a UI |
| RNF-04 | Isolamento de sistema | Sem alteração de código fora do subpacote do sistema |
| RNF-05 | Qualidade de código | Zero erros Ruff; cobertura de testes ≥ 80% |
| RNF-06 | Compatibilidade | Windows 10+ |
| RNF-07 | Segurança de credenciais | Apenas em `.env`, nunca em código ou logs |

---

## 6. Restrições

- **R1**: O Senna **não** substitui controles de acesso dos sistemas-alvo; apenas automatiza ações que o técnico já teria permissão de realizar manualmente.
- **R2**: O Playwright opera em modo **headless** por padrão; modo visível disponível via `DEBUG_BROWSER=true`.
- **R3**: O processamento em lote é **sequencial** na Fase 1; paralelismo é escopo futuro.
- **R4**: A interface **não** implementa autenticação própria na Fase 1 — controle de acesso ao Senna é responsabilidade do SO.
- **R5**: Arquivos em `data/output/` e `logs/` são **gitignored** e nunca versionados.

---

## 7. Arquitetura

### 7.1 Camadas

```
┌──────────────────────────────────────┐
│           Interface (CustomTkinter)   │  ← ui_main.py, forms.py
├──────────────────────────────────────┤
│              Orchestrator             │  ← orquestra sistema + procedimento
├──────────────────────────────────────┤
│  Core (Contratos, Config, Logger)    │  ← ABCs, Settings, Result[T,E]
├──────────────────────────────────────┤
│       Systems (S1…S5)                │  ← client, procedures, pages, locators
├──────────────────────────────────────┤
│           Utils                       │  ← BrowserFactory, DataLoader
└──────────────────────────────────────┘
```

### 7.2 Fluxo de Execução

```
Técnico seleciona sistema + procedimento
        │
        ▼
UI coleta e valida payload via forms.py
        │
        ▼
Orchestrator.get_procedure(sistema, proc)
        │
        ▼
procedure.validate(payload) ──falha──► exibe erro na UI
        │ sucesso
        ▼
BrowserFactory abre BrowserContext isolado
        │
        ▼
system.login(ctx)
        │
        ▼
procedure.execute(payload) → Result[T, E]
        │
        ▼
system.logout(ctx) ──► BrowserContext encerrado
        │
        ▼
audit_logger.write(entrada_json)
        │
        ▼
UI exibe resultado ao técnico
```

### 7.3 Padrão Result

Toda operação retorna `Result[T, E]` — nunca lança exceção para a camada de UI. A UI lê `result.success` para decidir o que exibir.

### 7.4 Padrão Page Object

Cada sistema possui `pages/` com classes que encapsulam ações de tela e `locators/` com seletores isolados. Procedimentos **nunca** contêm seletores diretamente.

---

## 8. Estrutura de Diretórios

```
senna/
├── senna/
│   ├── core/                  # Core da aplicação
│   │   ├── base_procedure.py  # Contrato base para procedimentos
│   │   ├── base_system.py     # Contrato base para sistemas
│   │   ├── config.py          # Gerenciamento de configurações e .env
│   │   ├── exceptions.py      # Hierarquia de exceções customizadas
│   │   ├── logger.py          # Logger estruturado e auditoria
│   │   ├── models.py          # Modelos de dados e payloads (dataclasses)
│   │   ├── orchestrator.py    # Orquestrador de sistemas e procedimentos
│   │   └── result.py          # Padrão de retorno Result[T, E]
│   ├── interface/             # UI CustomTkinter
│   │   ├── forms.py           # Formulários dinâmicos
│   │   └── ui_main.py         # Tela inicial e seleção de rotinas
│   ├── systems/               # Portais suportados e lógica específica
│   │   ├── servicos_ti/       # S1 — Portal de serviços de TI corporativo
│   │   │   ├── procedures/    # add_user, remove_user, extend_access, grant_profile
│   │   │   ├── pages/         # login_page, user_page
│   │   │   └── locators/      # login_locators, user_locators
│   │   ├── aghux/             # S2 — Sistema de gestão hospitalar AGHUx (mesma estrutura)
│   │   ├── integra/           # S3 — Sistema de integração de dados (mesma estrutura)
│   │   ├── s4/                # S4 — a definir (mesma estrutura)
│   │   └── s5/                # S5 — a definir (mesma estrutura)
│   ├── utils/                 # Ferramentas auxiliares
│   │   ├── browser_factory.py # Gerenciamento do Playwright e BrowserContext
│   │   └── data_loader.py     # Leitura e validação de planilhas em lote
│   └── main.py                # Entry point da aplicação
├── tests/
│   ├── unit/          # sem rede, sem browser — lógica pura
│   ├── integration/   # Playwright contra staging
│   └── e2e/           # fluxo completo
├── data/
│   ├── input/         # planilhas fornecidas pelo técnico
│   ├── output/        # relatórios gerados (gitignored)
│   └── temp/          # intermediários (gitignored)
├── agents/            # prompts de IA versionados
├── docs/
│   ├── architecture/  # ADRs
│   └── procedures/    # guias de uso para o técnico
├── logs/audit/        # JSON imutável de auditoria (gitignored)
├── .env.example       # Template de variáveis de ambiente
├── .gitignore         # Arquivos ignorados pelo repositório
├── pyproject.toml     # Configuração do projeto e dependências
├── README.md          # Visão geral e instruções iniciais
├── requirements.md    # Justificativas das dependências
├── ruff.toml          # Configurações do linter Ruff
└── SPEC.md            # Especificação de requisitos (Fonte da verdade)
```

---

## 9. Plano de Desenvolvimento

### Fase 0 — Fundação (Sprint 1)
**Objetivo**: infraestrutura funcionando, zero lógica de negócio.

- [ ] `0.1` Configurar `pyproject.toml`: dependências, entry point `senna.main:main`, config pytest e Ruff.
- [ ] `0.2` Configurar `ruff.toml` com regras E, F, I, ANN básicas.
- [ ] `0.3` Implementar `core/config.py`: leitura de `.env` + `settings.toml` com valores padrão.
- [ ] `0.4` Implementar `core/logger.py`: logger estruturado (JSON) + `audit_logger` separado.
- [ ] `0.5` Implementar `core/result.py`: tipo `Result[T, E]` genérico.
- [ ] `0.6` Implementar `core/exceptions.py`: hierarquia de erros.
- [ ] `0.7` Implementar `core/models.py`: dataclasses `UserPayload`, `ProfilePayload`, `AccessPayload`.
- [ ] `0.8` Implementar `utils/browser_factory.py`: abre/fecha `BrowserContext` isolado por sistema.
- [ ] `0.9` Testes unitários para `result.py`, `models.py`, `exceptions.py`.

**Critério de saída**: `pytest tests/unit/` 100% verde; `ruff check .` zero erros.

---

### Fase 1 — Contratos e Orquestração (Sprint 2)
**Objetivo**: esqueleto de extensão funcionando.

- [ ] `1.1` Implementar `core/base_system.py`: ABC com `login`, `logout`, `is_logged_in`.
- [ ] `1.2` Implementar `core/base_procedure.py`: ABC com `execute`, `validate`.
- [ ] `1.3` Implementar `core/orchestrator.py`: `REGISTRY`, `get_procedure()`, `get_system()`.
- [ ] `1.4` Implementar `systems/__init__.py`: `AVAILABLE_SYSTEMS` mapeando chaves para classes.
- [ ] `1.5` Testes unitários para `orchestrator.py` com sistemas e procedimentos mockados.

**Critério de saída**: `Orchestrator` instancia corretamente qualquer procedimento registrado.

---

### Fase 2 — Sistema Piloto: Serviços TI (Sprint 3–4)
**Objetivo**: primeiro sistema completo, do login à execução de procedimento.

- [ ] `2.1` Implementar `systems/servicos_ti/config.py`: URL base, seletores, timeouts.
- [ ] `2.2` Implementar `systems/servicos_ti/locators/login_locators.py` e `user_locators.py`.
- [ ] `2.3` Implementar `systems/servicos_ti/pages/login_page.py` e `user_page.py`.
- [ ] `2.4` Implementar `systems/servicos_ti/client.py`: `login`, `logout`, `is_logged_in`.
- [ ] `2.5` Implementar procedimento `add_user.py` com `validate` + `execute`.
- [ ] `2.6` Implementar procedimento `remove_user.py`.
- [ ] `2.7` Implementar procedimento `extend_access.py`.
- [ ] `2.8` Implementar procedimento `grant_profile.py`.
- [ ] `2.9` Testes unitários de procedures com Page mockado.
- [ ] `2.10` Testes de integração contra ambiente staging do sistema.

**Critério de saída**: os 4 procedimentos executam com sucesso em staging; logs de auditoria gerados corretamente.

---

### Fase 3 — Interface Gráfica (Sprint 5)
**Objetivo**: UI funcional conectada ao Orchestrator.

- [ ] `3.1` Implementar `interface/forms.py`: definição declarativa de campos por procedimento.
- [ ] `3.2` Implementar `interface/ui_main.py`: tela inicial, seleção de sistema, formulário dinâmico, área de resultado.
- [ ] `3.3` Conectar UI → `Orchestrator` → `Result` → exibição.
- [ ] `3.4` Indicador de progresso durante execução (thread separada para não travar a UI).
- [ ] `3.5` Exibição inline de erros de validação de formulário.
- [ ] `3.6` Testes unitários de lógica de formulários (validação de campos).

**Critério de saída**: técnico consegue executar `add_user` no sistema piloto pela UI sem erros visuais.

---

### Fase 4 — Processamento em Lote (Sprint 6)
**Objetivo**: importar planilha e executar N registros sequencialmente.

- [ ] `4.1` Implementar `utils/data_loader.py`: leitura de CSV/XLSX, validação de colunas obrigatórias.
- [ ] `4.2` Integrar DataLoader à UI: botão "Importar Planilha", tabela de preview.
- [ ] `4.3` Executar linhas sequencialmente, atualizando progresso linha a linha.
- [ ] `4.4` Gerar relatório de execução em `data/output/` (CSV com status por linha).
- [ ] `4.5` Testes unitários de `data_loader.py` com arquivos de `tests/testdata/`.

**Critério de saída**: planilha com 10 registros processada, relatório gerado, falhas individuais não interrompem o lote.

---

### Fase 5 — Sistemas Adicionais (Sprint 7–9)
**Objetivo**: replicar padrão do sistema piloto para os demais 4 sistemas.

- [ ] `5.1` Implementar `systems/aghux/` completo (client, config, locators, pages, procedures).
- [ ] `5.2` Implementar `systems/integra/` completo.
- [ ] `5.3` Implementar sistemas S4 e S5 completos.
- [ ] `5.4` Registrar todos os sistemas em `AVAILABLE_SYSTEMS`.
- [ ] `5.5` Testes de integração para cada sistema.

**Critério de saída**: todos os 5 sistemas operáveis pela UI; testes de integração verdes.

---

### Fase 6 — Testes E2E e Qualidade (Sprint 10)
**Objetivo**: cobertura completa, zero regressões.

- [ ] `6.1` Implementar cenários E2E em `tests/e2e/scenarios/` para os fluxos críticos.
- [ ] `6.2` Cobertura de testes ≥ 80% medida via `pytest --cov`.
- [ ] `6.3` Pipeline CI local: `ruff check . && pytest` como hook de pre-commit.
- [ ] `6.4` Revisão e atualização da documentação em `docs/`.

**Critério de saída**: cobertura ≥ 80%; zero erros Ruff; todos os testes E2E verdes.

---

## 10. Definição de Pronto

Uma funcionalidade está **pronta** quando:

1. Código implementado e passando em `ruff check .` sem erros.
2. Testes unitários escritos e verdes.
3. Testes de integração escritos e verdes (quando aplicável).
4. Log de auditoria gerado corretamente para o caminho feliz e para falhas.
5. `Result[T, E]` retornado corretamente — sem exceções não tratadas chegando à UI.
6. Código commitado com mensagem semântica (`feat:`, `fix:`, `test:`, `refactor:`).

---

## 11. Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|-------------|---------|-----------|
| Seletores dos sistemas mudam sem aviso | Alta | Alto | Seletores isolados em `locators/`; fácil atualizar sem tocar em procedures |
| Sistema-alvo fora do ar durante execução | Média | Médio | `SystemUnavailableError` capturado; resultado de falha exibido sem travar a UI |
| Credenciais expiradas | Média | Alto | Verificação de `is_logged_in` antes de cada procedimento; alerta ao técnico |
| Planilha com dados inválidos | Alta | Baixo | `DataLoader` valida schema antes de iniciar o lote |
| Mudança de layout dos sistemas | Média | Alto | Page Object Pattern isola impacto; apenas `pages/` e `locators/` precisam ser atualizados |

---

## 12. Glossário

| Termo | Definição |
|-------|----------|
| **Procedimento** | Unidade atômica de automação (ex: `add_user`) implementada como classe que herda `BaseProcedure` |
| **Sistema** | Um dos 5 portais web gerenciados pelo Senna, representado por um subpacote em `senna/systems/` |
| **Payload** | Conjunto de dados necessários para executar um procedimento (dataclass tipada) |
| **BrowserContext** | Sessão isolada do Playwright — equivalente a um perfil de navegador separado por sistema |
| **Result[T, E]** | Tipo que encapsula sucesso ou falha sem lançar exceção — garante que a UI nunca quebre por erro de automação |
| **Page Object** | Classe que encapsula as ações de uma tela específica do sistema, separando lógica de navegação dos seletores |
| **Lote** | Execução sequencial de múltiplos registros importados de uma planilha CSV/XLSX |
| **Audit Log** | Registro JSON imutável gerado a cada execução, contendo quem fez, o quê, quando e qual foi o resultado |

---

## 13. Workflow Git

### 13.1 Fluxo Obrigatório

Todo desenvolvimento deve seguir **estritamente** esta ordem:

```
Codificar → Testes unitários → Testes de integração → Ruff → Commit
```

Se qualquer etapa falhar: corrigir e repetir o ciclo. Commit é proibido antes de tudo passar.

### 13.2 Regra de Commit

Um commit só é permitido quando todos os testes unitários e de integração passam e Ruff não retorna erros.

### 13.3 Convenção de Commits

Formato obrigatório: `<tipo>: <descrição curta>`

| Tipo | Uso |
|------|-----|
| `feat` | nova automação ou funcionalidade |
| `fix` | correção de erro |
| `refactor` | reorganização interna sem mudança funcional |
| `test` | novos testes ou melhoria de testes |
| `chore` | ajustes técnicos |
| `docs` | documentação |

Exemplos válidos:
```
feat: add_user procedure for servicos_ti
fix: handle timeout during login
refactor: extract BrowserFactory from client
```

Commits vagos (`fix stuff`, `update`, `changes`) são proibidos.

### 13.4 Frequência

Um commit deve representar **uma única mudança lógica**. Pequenos, frequentes e coerentes.

### 13.5 Hook de Verificação

Configurar pre-commit hook executando `ruff check . && pytest`. Commit bloqueado automaticamente em caso de falha.

---

## 14. Code Style

### 14.1 Tipagem Forte

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

### 14.2 Nomenclatura Grepável

Nomes devem ser significativos, únicos e fáceis de localizar por busca.

| Padrão | Exemplos ✅ | Exemplos 🚫 |
|--------|-----------|------------|
| Variáveis | `user_payload`, `login_response` | `data`, `obj`, `tmp`, `value` |
| Classes | `UserPage`, `AddUserProcedure`, `BrowserFactory` | `Manager`, `Handler`, `Processor` |
| Funções | `create_user`, `validate_payload`, `open_browser_context` | `do_it`, `handle`, `process` |

### 14.3 Simplicidade Estrutural

Prefira guard clauses, early return e funções pequenas e coesas. Evite funções gigantes, condições complexas e aninhamento profundo.

---

## 15. Boundaries

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