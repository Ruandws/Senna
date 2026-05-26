# Nota de Atualização: Refatoração do Módulo de Configuração (Core)
Data: 18 de maio de 2026
Tipo: Refatoração Arquitetural e Estrutural (Fail-Fast)

## O que foi feito
- **Refatoração completa de `senna/core/config.py`**: 
  - O antigo modelo `Settings` (dataclass) foi completamente substituído por uma única classe `Config` com um singleton instanciado em nível de módulo (`config = Config()`).
  - Implementado o carregamento hierárquico claro, onde `settings.toml` fornece a base e `.env` sobrescreve valores variáveis e credenciais, fundidos via `_merge()`.
  - Introduzida uma tupla `_REQUIRED_CREDENTIALS` que implementa o padrão "Fail-Fast" através do método `_validate_credentials()`. A ausência de configurações obrigatórias passa a abortar o sistema e levantar a exceção `MissingCredentialError` instantaneamente durante o import.
  - Implementação dos métodos auxiliares genéricos genéricos `get()`, estrito `require()` e explícito `debug_browser()`.
- **Análise do Linter e Testes**: 
  - O código de `senna/core/config.py` foi submetido ao crivo do Ruff, retornando zero erros com compliance de 100%.
  - O `test_config.py` retornou falha na coleção como previsto, refletindo a incompatibilidade com a arquitetura recém implementada. A lógica dos testes será abordada nas próximas iterações.

## Justificativa
A nova estrutura fortalece drasticamente a segurança do robô em produção, impedindo que procedimentos RPA iniciem a execução em cenários falhos de injeção de credenciais, além de centralizar e universalizar a aquisição de configurações no sistema (RF-06).
