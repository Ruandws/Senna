# 🚀 Launcher TI

<div align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.14-blue?style=for-the-badge&logo=python">
  <img alt="Playwright" src="https://img.shields.io/badge/Playwright-1.58-green?style=for-the-badge&logo=playwright">
  <img alt="CustomTkinter" src="https://img.shields.io/badge/CustomTkinter-5.2.2-blueviolet?style=for-the-badge">
  <img alt="Ruff" src="https://img.shields.io/badge/Linter-Ruff-yellow?style=for-the-badge">
</div>

<br>

O **Launcher TI** é uma aplicação desktop desenvolvida em Python que centraliza automações web voltadas à gestão de usuários em sistemas hospitalares. Desenvolvido para facilitar a rotina dos técnicos de TI, ele permite executar procedimentos complexos e repetitivos de forma automatizada, segura e rastreável.

---

## ✨ Funcionalidades

- **Centralização de Sistemas:** Interface única para gerenciar acessos em diversos sistemas corporativos (Serviços TI, AGHUx, Integra, etc.).
- **Automação Headless:** Os fluxos rodam em segundo plano utilizando o **Playwright**, sem interromper o trabalho do técnico.
- **Execução em Lote (Batch):** Suporte à importação de planilhas `.xlsx` para processar múltiplos usuários de forma sequencial.
- **Auditoria Inteligente:** Registro detalhado e imutável de todas as execuções (sucesso ou falha) em formato JSON.
- **Arquitetura Resiliente:** Utiliza o padrão `Result[T, E]`, garantindo que nenhuma falha de automação chegue à interface gráfica (UI) ou trave o sistema.

---

## 🛠 Stack de Tecnologias

- **Linguagem:** Python 3.14
- **Automação Web:** Playwright 1.58
- **Interface Gráfica:** CustomTkinter 5.2.2
- **Manipulação de Dados:** Pandas 3.0.1
- **Qualidade de Código:** Ruff (Linter) & Pytest (Testes)

---

## 📂 Estrutura do Projeto

O projeto segue uma arquitetura modular baseada em subpacotes, isolando regras de negócio, interface e os sistemas-alvo:

```text
launcher-ti/
├── launcher/
│   ├── core/          # Contratos (ABCs), Orchestrator, Models, Config, Result
│   ├── interface/     # UI em CustomTkinter e formulários dinâmicos
│   ├── systems/       # Implementação dos sistemas (servicos_ti, aghux, etc.)
│   └── utils/         # Utilitários (BrowserFactory, DataLoader)
├── tests/             # Testes Unitários, de Integração e E2E
├── data/              # Planilhas de entrada (input) e relatórios (output)
├── agents/            # Prompts de IA versionados
└── docs/              # Documentações adicionais
```

---

## ⚙️ Como Executar

### Pré-requisitos
- **Python 3.14+**
- **Pip** (Gerenciador de pacotes)
- **Git**

### Passo a Passo

1. **Clone o repositório:**
   ```powershell
   git clone https://github.com/Ruandws/Senna.git
   cd Senna/launcher-ti
   ```

2. **Crie e ative um ambiente virtual:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Instale as dependências do projeto e navegadores:**
   ```powershell
   pip install -r requirements.md
   playwright install
   ```
   *(Nota: Se usar pyproject.toml / Poetry / uv no futuro, ajuste o comando acima)*

4. **Variáveis de Ambiente:**
   Copie o arquivo base `.env.example` para `.env` e preencha com as credenciais reais (as credenciais nunca devem ser enviadas ao repositório).

5. **Inicie a aplicação:**
   ```powershell
   python -m launcher.main
   ```

---

## 🧪 Testes e Qualidade de Código

Este projeto segue rigorosamente o ciclo **Codificar → Testar → Corrigir → Validar → Commitar**. Nenhuma alteração de código é aceita sem a validação do pipeline local.

Para validar o projeto antes de um commit, execute:
```powershell
# Verifica erros de formatação, tipagem e estilo
ruff check .

# Roda toda a suíte de testes unitários e de integração
pytest
```

---

## 📜 Fonte da Verdade

Toda a arquitetura, padrões de design (como Page Object e Result Pattern), restrições, glossário e **regras de commit** estão minuciosamente documentados no arquivo oficial do projeto:

👉 **[Consulte o SPEC.md](./SPEC.md)** antes de realizar qualquer modificação ou enviar PRs.
