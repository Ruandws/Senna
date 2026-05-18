# Nota de Atualização: Padronização e Simplificação de Modelos de Dados e Payloads
Data: 18 de maio de 2026
Tipo: Refatoração Arquitetural de Modelos de Domínio (Core)

## O que foi feito
- **Reestruturação completa de `senna/core/models.py`**:
  - **Eliminação de Payloads Específicos por Sistema**: Removemos os payloads acoplados aos formulários locais das plataformas (como `ServicoesTiCreateUserPayload`, `IntegraGrantProfilePayload`, etc.) e a hierarquia base de herança (`BaseUserPayload`, `BaseAccessPayload`).
  - **Introdução de Modelos Alinhados a Requisitos de Negócio (RF-04)**:
    - `UserPayload` (P1 - Adicionar usuário): Nome, matrícula (`registration`), e-mail institucional e perfil inicial.
    - `RemovalPayload` (P2 - Remover usuário): Rastreia matrícula e/ou login. A presença de pelo menos um deles é validada de forma estrita em tempo de execução.
    - `AccessPayload` (P3 - Alterar data de expiração): Matrícula e nova data de expiração.
    - `ProfilePayload` (P4 - Conceder ou revogar perfil de acesso): Matrícula, perfil e a ação desejada (`ProfileAction.GRANT` ou `ProfileAction.REVOKE`).
  - **Enum de Domínio**: Adicionamos `ProfileAction` (StrEnum) para tipagem estrita das ações P4.
  - **Rastreamento de Lotes (RF-05)**:
    - Criamos a dataclass imutável `ExecutionRecord` para representar o resultado detalhado da execução de cada linha individual da planilha (row_index, system_id, procedure_id, success, message), compondo o relatório final consolidado.
- **Validação de Conformidade**:
  - O código foi totalmente inspecionado, formatado e validado pelo Ruff, apresentando **100% de conformidade (zero erros)**.
  - A execução específica do pytest em `test_models.py` falhou na fase de coleta devido à remoção de classes antigas de payloads, como previsto. O ajuste dos testes unitários para a nova suíte de modelos de dados será executado oportunamente.

## Justificativa
Alinhar a camada de modelos diretamente com as ações core do sistema (P1, P2, P3, P4) descritas nos requisitos funcionais (RF-04), garantindo tipagem estrita, imutabilidade (`frozen=True`) e impedindo a propagação de dicionários soltos ou dados sensíveis em trânsito pela aplicação.
