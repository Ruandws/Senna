# SPEC.MD — Especificação de Requisitos: Launcher TI
> Fonte da verdade do projeto. Toda decisão de arquitetura, escopo e implementação deve ser validada contra este documento.

---

## 1. Visão Geral

O **Launcher TI** é uma aplicação desktop desenvolvida em Python que centraliza automações web voltadas à gestão de usuários em sistemas hospitalares. 
O técnico de TI, ao receber um chamado, abre o Launcher, seleciona o sistema-alvo, escolhe o procedimento desejado, preenche os dados do formulário e dispara a automação. O Launcher executa o fluxo via Playwright em segundo plano e exibe o resultado na interface.

---

## 2. Objetivos

| # | Objetivo | Critério de Sucesso |
|---|----------|---------------------|
| O1 | Automatizar procedimentos repetitivos. | Execução de ponta a ponta sem intervenção manual |
| O2 | Centralizar 5 sistemas na mesma interface | Todos os sistemas operáveis a partir do Launcher |
| O4 | Permitir processamento em lote via planilha | Importação de XLSX validado pelo Launcher |
| O5 | Facilitar extensão para novos sistemas e procedimentos | Novo sistema = nova pasta com contratos já definidos |

---

## 3. Stakeholders

- **Técnico de TI**: usuário primário — executa procedimentos via interface.
- **Coordenador de TI**: consulta logs de auditoria e relatórios de execução.
- **Desenvolvedor**: estende o Launcher com novos sistemas e procedimentos.

---

## 4. Stack de Tecnologias

| Componente | Tecnologia | Versão |
|------------|-----------|--------|
| Linguagem | Python | 3.14 |
| Automação Web | Playwright | 1.58 |
| Interface Gráfica | CustomTkinter | 5.2.2 |
| Processamento de Dados | Pandas | 3.0.1 |
| Linter | Ruff | latest |
| Versionamento | Git | — |
| Gerenciador de Projeto | pyproject.toml | PEP 517 |

---

## 5. Sistemas Suportados (Fase 1)

Cada sistema é isolado em seu próprio subpacote dentro de `launcher/systems/`. Os nomes abaixo são placeholders até a definição oficial pela equipe:

| ID | Nome do Pacote | Descrição |
|----|---------------|-----------|
| S1 | `servicos_ti` | Portal de serviços de TI corporativo |
| S2 | `aghux` | Sistema de gestão hospitalar AGHUx |
| S3 | `integra` | Sistema de integração de dados |
| S4 | *(a definir)* | Quarto sistema — mesmo padrão estrutural |
| S5 | *(a definir)* | Quinto sistema — mesmo padrão estrutural |

---

## 6. Procedimentos por Sistema

Os procedimentos abaixo aplicam-se a todos os sistemas que os suportem. Cada procedimento é uma classe independente que herda `BaseProcedure`.

| ID | Procedimento | Payload Necessário |
|----|-------------|-------------------|
| P1 | Adicionar usuário | nome, matrícula, e-mail, perfil |
| P2 | Remover usuário | matrícula ou login |
| P3 | Alterar data de expiração | matrícula, nova data |
| P4 | Conceder/revogar perfil de acesso | matrícula, perfil, ação (grant/revoke) |

> Nem todo sistema suportará todos os procedimentos. A disponibilidade é declarada no `AVAILABLE_SYSTEMS` de `launcher/systems/__init__.py`.

---

## 7. Requisitos Funcionais

### RF-01 — Seleção de Sistema
- A UI deve exibir somente sistemas registrados em `AVAILABLE_SYSTEMS`.

### RF-02 — Seleção de Procedimento
- A UI deve exibir somente procedimentos disponíveis para o sistema selecionado.

### RF-03 — Formulário Dinâmico
- A UI deve exibir o formulário correspondente ao procedimento selecionado.
- Campos obrigatórios são validados antes do envio.
- Mensagens de erro são exibidas inline, próximas ao campo inválido.

### RF-04 — Execução Individual
- Após o usuário preencher o formulário e clicar em "Executar", o Launcher instancia o procedimento via `Orchestrator`, passa o payload e aguarda o `Result` o qual é exibido na interface.

### RF-05 — Execução em Lote
- O usuáro importa um arquivo XLSX, que é validado em colunas obrigatórias pelo `DataLoader`.
- O Launcher executa cada linha como uma execução individual sequencial.
- Um relatório consolidado é salvo em `data/output/`.

### RF-06 — Gerenciamento de Credenciais
- As credenciais dos sistemas são lidas de variáveis de ambiente (`.env`).
- Nunca são exibidas na interface ou gravadas em logs.
- O Launcher alerta o técnico se uma credencial obrigatória estiver ausente ao inicializar.

### RF-08 — Sessão Isolada por Sistema
- Cada sistema abre e gerencia seu próprio `BrowserContext` isolado via `BrowserFactory`.
- A sessão é encerrada ao finalizar todos os procedimentos do sistema ou em caso de erro não recuperável.

---

## 8. Requisitos Não Funcionais

| ID | Requisito | Meta |
|----|----------|------|
| RNF-01 | O sistema deve executar cada procedimento em até 60 segundos.
| RNF-02 | O sistema deve exibir feedback visual durante toda execução, com indicador de progresso
| RNF-03 | O sistema deve tratar qualquer exceção capturando-a e registrando-a sem travar a UI
| RNF-04 | O sistema não deve exigir alteração de código fora de seu subpacote
| RNF-05 | Qualidade de código | Zero erros Ruff na pipeline; cobertura de testes ≥ 80% |
| RNF-06 | O sistema deve funcionar em windows 10+
| RNF-07 | O sistema deve tratar credenciais apenas em `.env`, nunca em código ou logs |

---

## 9. Restrições

- **R1**: O Launcher **não** substitui controles de acesso dos sistemas-alvo; apenas automatiza ações que o técnico já teria permissão de realizar manualmente.


- **R2**: O Playwright opera em modo **headless** por padrão; modo com janela visível disponível via variável de ambiente `DEBUG_BROWSER=true`.


- **R3**: O processamento em lote é **sequencial** na Fase 1; paralelismo é escopo futuro.


- **R4**: A interface **não** implementa autenticação própria na Fase 1 — controle de acesso ao Launcher é responsabilidade do SO.


- **R5**: Arquivos em `data/output/` e `logs/` são **gitignored** e nunca versionados.

---

## 10. Arquitetura

### 10.1 Camadas

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

### 10.2 Fluxo de Execução

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

### 10.3 Padrão Result

Toda operação retorna `Result[T, E]` — nunca lança exceção para a camada de UI. A UI lê `result.success` para decidir o que exibir.

### 10.4 Padrão Page Object

Cada sistema possui `pages/` com classes que encapsulam ações de tela, e `locators/` com seletores isolados. Procedimentos **nunca** contêm seletores diretamente.

---

## 11. Estrutura de Diretórios (Referência)

```
launcher-ti/
├── launcher/
│   ├── core/          # ABCs, Orchestrator, Models, Config, Logger, Result
│   ├── interface/     # UI CustomTkinter + formulários dinâmicos
│   ├── systems/
│   │   ├── servicos_ti/
│   │   │   ├── procedures/   # add_user, remove_user, extend_access, grant_profile
│   │   │   ├── pages/        # login_page, user_page
│   │   │   └── locators/     # login_locators, user_locators
│   │   ├── aghux/            # mesma estrutura
│   │   └── integra/          # mesma estrutura
│   └── utils/         # BrowserFactory, DataLoader
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
└── logs/audit/        # JSON imutável de auditoria (gitignored)
```

---

## 12. Plano de Desenvolvimento — Passo a Passo

### Fase 0 — Fundação (Sprint 1)
**Objetivo**: infraestrutura funcionando, zero lógica de negócio.

- [ ] `0.1` Configurar `pyproject.toml`: dependências, entry point `launcher.main:main`, config pytest e Ruff.
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
- [ ] `3.2` Implementar `interface/ui_main.py`: tela inicial (seleção de sistema), tela de procedimento, formulário dinâmico, área de resultado.
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

## 13. Definição de Pronto (Definition of Done)

Uma funcionalidade está **pronta** quando:

1. Código implementado e passando em `ruff check .` sem erros.
2. Testes unitários escritos e verdes.
3. Testes de integração escritos e verdes (quando aplicável).
4. Log de auditoria gerado corretamente para o caminho feliz e para falhas.
5. `Result[T, E]` retornado corretamente — sem exceções não tratadas chegando à UI.
6. Código revisado e commitado com mensagem semântica (`feat:`, `fix:`, `test:`, `refactor:`).

---

## 14. Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|-------------|---------|-----------|
| Seletores dos sistemas mudam sem aviso | Alta | Alto | Seletores isolados em `locators/`; fácil de atualizar sem tocar em procedures |
| Sistema-alvo fora do ar durante execução | Média | Médio | `SystemUnavailableError` capturado; resultado de falha exibido sem travar a UI |
| Credenciais expiradas | Média | Alto | Verificação de `is_logged_in` antes de cada procedimento; alerta ao técnico |
| Planilha com dados inválidos | Alta | Baixo | `DataLoader` valida schema antes de iniciar o lote |
| Mudança de layout dos sistemas | Média | Alto | Page Object Pattern isola impacto; apenas `pages/` e `locators/` precisam ser atualizados |

---

## 15. Glossário

| Termo | Definição |
|-------|----------|
| **Procedimento** | Unidade atômica de automação (ex: `add_user`) implementada como classe que herda `BaseProcedure` |
| **Sistema** | Um dos 5 portais web gerenciados pelo Launcher, representado por um subpacote em `launcher/systems/` |
| **Payload** | Conjunto de dados necessários para executar um procedimento (dataclass tipada) |
| **BrowserContext** | Sessão isolada do Playwright — equivalente a um perfil de navegador separado por sistema |
| **Result[T, E]** | Tipo que encapsula sucesso ou falha sem lançar exceção — garante que a UI nunca quebre por erro de automação |
| **Page Object** | Classe que encapsula as ações de uma tela específica do sistema, separando lógica de navegação dos seletores |
| **Lote** | Execução sequencial de múltiplos registros importados de uma planilha CSV/XLSX |
| **Audit Log** | Registro JSON imutável gerado a cada execução, contendo quem fez, o quê, quando e qual foi o resultado |

## 16. Workflow Git

### 16.1 Fluxo Obrigatório de Desenvolvimento

Todo desenvolvimento deve seguir **estritamente** esta ordem:

1 — Codificação  
2 — Testes unitários  
3 — Testes de integração  
4 — Linter (Ruff)  
5 — Commit (apenas se tudo passar)

Fluxo formal:

Codificar  
↓  
Rodar testes unitários  
↓  
Rodar testes de integração  
↓  
Rodar Ruff  
↓  
Se TODOS passarem → Commit  
Se qualquer etapa falhar → Corrigir → Repetir ciclo  

---

### 16.2 Regra de Commit

Um commit só é permitido quando:

- Todos os testes unitários passam
- Todos os testes de integração passam
- Ruff não retorna erros
- O código executa corretamente

Se qualquer verificação falhar:

O commit **é proibido**.

---

### 16.3 Convenção de Commits

Todos os commits devem seguir um prefixo padronizado.

Formato obrigatório:

<tipo>: <descrição curta>

Opcional:

<tipo>: <descrição curta>

<descrição longa>

---

### Tipos Permitidos

feat      → nova automação ou funcionalidade  
fix       → correção de erro  
refactor  → reorganização interna sem mudança funcional  
test      → novos testes ou melhoria de testes  
chore     → ajustes técnicos  
docs      → documentação  

---

### Exemplos Válidos

feat: add_user procedure for servicos_ti

fix: handle timeout during login

refactor: extract BrowserFactory from client

test: add unit tests for Result class

chore: update pytest configuration

docs: update workflow documentation

---

### Exemplos Proibidos

fix stuff  
update  
changes  
test  
misc  

Commits vagos são proibidos.

---

### 16.4 Frequência de Commits

Commits devem ser:

- Pequenos
- Frequentes
- Coerentes

Regra recomendada:

Um commit deve representar **uma única mudança lógica**.

Evitar:

- Commits gigantes
- Commits com múltiplos objetivos
- Commits contendo código quebrado

---

### 16.5 Hook de Verificação (Recomendado)

Recomenda-se configurar pre-commit hook executando:

ruff check .
pytest

Se qualquer comando falhar:

O commit deve ser bloqueado automaticamente.

## 17. Code Style e Loop Codar-Testar-Corrigir Headless

O código deve ser previsível, tipado, grepável e validado antes de qualquer commit.

Este projeto adota o ciclo obrigatório:

Codificar → Testar → Corrigir → Validar → Commitar

Nenhum commit é permitido antes da validação completa.

---

### 17.1 Tipagem Forte Obrigatória

Todo código Python deve usar type hints explícitos.

Tipagem é obrigatória para:

- Parâmetros de função
- Valores de retorno
- Atributos de classe
- Dataclasses
- Estruturas de dados

Funções sem tipagem são proibidas.

Exemplo obrigatório:

def add_user(payload: UserPayload) -> Result[User, Error]:

Exemplo proibido:

def add_user(payload):
    
Toda função deve declarar tipo de retorno, inclusive quando retornar None.

### 17.2 Payloads Tipados

Payloads devem ser modelados como dataclasses tipadas.

Dicionários soltos são proibidos para dados críticos de execução.

Exemplo:

@dataclass
class UserPayload:
    name: str
    email: str
    profile: str

### 17.3 Estilo Grepável

Nomes devem ser significativos, únicos e fáceis de localizar por busca.

Use nomes descritivos para classes, funções, variáveis e módulos.

Exemplos recomendados:

user_payload
login_response
audit_log_entry
browser_context

Exemplos proibidos:

data
obj
tmp
value
result1

Classes devem seguir o padrão DomínioFunção.

Exemplos:

UserPage
LoginPage
AddUserProcedure
BrowserFactory

Evite nomes genéricos como:

Manager
Handler
Processor

Funções devem representar ação clara.

Exemplos:

create_user
validate_payload
open_browser_context

Evite nomes vagos como:

do_it
handle
process

### 17.4 Simplicidade Estrutural

Código deve ser explícito e fácil de revisar.

Evite:

Funções gigantes
Condições complexas
Aninhamento profundo

Prefira:

Guard clauses
Early return
Funções pequenas e coesas

### 17.5 Execução Headless Obrigatória

Todos os testes devem rodar via CLI, sem interface gráfica.

Nenhum teste pode depender de interação manual.

Comando padrão de validação:

ruff check . && pytest

Se este comando falhar, a tarefa não está concluída.

### 17.6 Ciclo Obrigatório de Trabalho

Toda alteração deve seguir esta ordem:

Codificar
Rodar testes unitários
Rodar testes de integração
Rodar Ruff
Corrigir falhas
Repetir até tudo passar
Commitar apenas depois da validação completa

É proibido declarar sucesso sem executar a suíte de testes.

### 17.7 Regra de Conclusão

Uma tarefa só pode ser considerada concluída quando:

Todos os testes unitários passaram
Todos os testes de integração passaram
Ruff não retornou erros
O comportamento foi validado via CLI
Nenhuma exceção não tratada permaneceu

### 17.8 Convenção de Commits

Commits devem seguir a convenção:

<tipo>: <descrição curta>

Tipos permitidos:

feat → nova automação ou funcionalidade
fix → correção de erro
refactor → reorganização interna sem mudança funcional
test → novos testes ou melhoria de testes
chore → ajustes técnicos
docs → documentação

Exemplos válidos:

feat: add_user procedure for servicos_ti
fix: handle timeout during login
refactor: extract BrowserFactory from client
test: add unit tests for Result class
chore: update pytest configuration
docs: update workflow documentation

Exemplos proibidos:

fix stuff
update
changes
test
misc

Commits vagos são proibidos.

### 17.9 Regra de Commit

Um commit só é permitido quando:

Todos os testes unitários passam
Todos os testes de integração passam
Ruff não retorna erros
O código executa corretamente via CLI

Se qualquer verificação falhar, o commit é proibido.

### 17.10 Hook de Verificação

O repositório deve usar pre-commit hook para bloquear commits inválidos.

O hook deve executar:

ruff check .
pytest

Se qualquer comando falhar, o commit deve ser bloqueado.

## 18. Riscos Operacionais

Os riscos do projeto devem ser tratados por regra de comportamento.

Eles são divididos em três grupos:

- Sempre fazer
- Perguntar antes
- NUNCA FAZER

---

### 18.1 Sempre fazer

- Sempre executar a suíte completa de testes antes de declarar sucesso.
- Sempre rodar `ruff check .` antes de commitar.
- Sempre rodar `pytest` antes de commitar.
- Sempre validar mudanças via CLI, sem interface gráfica.
- Sempre usar type hints explícitos.
- Sempre tipar retorno de funções.
- Sempre registrar auditoria por execução, inclusive em falhas.
- Sempre tratar erros sem deixar exceções não tratadas chegarem à UI.
- Sempre manter nomes significativos, únicos e grepáveis.
- Sempre manter payloads como dataclasses tipadas.
- Sempre preservar isolamento por sistema e por `BrowserContext`.
- Sempre corrigir falhas antes de prosseguir.

---

### 18.2 Perguntar antes

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

---

### 18.3 NUNCA FAZER

- Nunca commitar código sem passar em testes.
- Nunca commitar código com erro de Ruff.
- Nunca declarar tarefa concluída sem rodar testes.
- Nunca depender de GUI para validar comportamento.
- Nunca usar dicionários soltos onde houver contrato tipado.
- Nunca expor credenciais em logs, UI ou código.
- Nunca gravar segredo em arquivo versionado.
- Nunca criar nomes genéricos como `data`, `tmp`, `obj`, `handle` ou `manager`.
- Nunca deixar exceção não tratada chegar à interface.
- Nunca alterar comportamento sem atualizar testes.
- Nunca introduzir dependência manual para validação automática.
- Nunca permitir commit com código quebrado.
