# Nota de Atualização: Refatoração do Padrão Result[T, E]
Data: 18 de maio de 2026
Tipo: Refatoração de Padrão Funcional (Core)

## O que foi feito
- **Reestruturação completa de `senna/core/result.py`**:
  - **Acesso Direto Simplificado**: Removemos os campos privados encapsulados (`_value` e `_error`) que eram acessados através de propriedades restritivas. A classe `Result` agora expõe diretamente os atributos públicos `value` e `error` (que assumem `None` caso não sejam preenchidos), facilitando integrações diretas.
  - **Métodos Estritos de Desempacotamento**: 
    - Implementamos `unwrap()`, que retorna `value` se `success=True` e levanta um `RuntimeError` contendo os detalhes do erro caso seja uma falha.
    - Implementamos `unwrap_error()`, que retorna `error` se `success=False` e levanta um `RuntimeError` detalhado caso seja um sucesso.
  - **Simplificação do Modelo**: O método utilitário de mapeamento monádico encadeado `.map()` foi inteiramente removido do escopo do `Result` para manter a classe focada e enxuta.
- **Validação de Conformidade**:
  - O código foi totalmente limpo e validado pelo formatador e linter Ruff com **100% de sucesso (zero erros)**.
  - O teste unitário correspondente (`test_result.py`) falhou na asserção de erros e no teste do método `.map()` removido. O ajuste dos testes para este padrão simplificado ocorrerá posteriormente em conformidade com as regras do projeto.

## Justificativa
Desacoplar o tipo Result de complexidades funcionais desnecessárias (como map) e prover acesso limpo e direto aos dados, enquanto mantém uma alternativa estrita e segura de desempacotamento via `unwrap` para evitar que exceções não tratadas cheguem e quebrem a interface visual do Senna (RNF-03).
