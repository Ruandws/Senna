# Nota de Atualização: Implementação do Contrato Base de Procedimentos
Data: 20 de maio de 2026
Tipo: Implementação de Contratos (Core) e Testes Unitários (100% de Cobertura)

## O que foi feito
- **Implementação do contrato base de procedimentos:**
  - Criada a classe abstrata `BaseProcedure` em `senna/core/base_procedure.py` que define os contratos para `procedure_id`, `validate` e `execute`.

- **Criação de novos arquivos de teste unitário:**
  - `tests/unit/core/test_base_procedure.py` (3 testes): Validação de erros de instanciação de classe abstrata, comportamento de subclasse concreta dummy e verificação do formato do método `__repr__`.

- **Ajustes de Qualidade:**
  - Docstring de `procedure_id` formatada em múltiplas linhas em `base_procedure.py` para cumprir a limitação de comprimento do Ruff (100 caracteres).
  - Remoção de comentários antigos/duplicados no topo do arquivo.

## Validação
- **Ruff**: `ruff check .` e `ruff format --check .` passaram com zero erros.
- **Testes Unitários em Cascata e Cobertura**:
  - Comando: `pytest`
  - Resultado: **104 testes passaram** em 2.56s.
  - Cobertura geral alcançada: **100.00%** (meta estrita de 100% de cobertura do projeto mantida).
  - Cobertura individual (`base_procedure.py`): 100%.

## Justificativa
Garantir o contrato unificado para todas as automações e procedimentos do Senna, validando a integridade das chamadas de execução e de validação prévia de payloads sem I/O direto, mantendo o nível máximo de confiabilidade por meio de testes unitários com cobertura total.
