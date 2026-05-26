Implementação da interface principal da aplicação Senna (`senna/interface/ui_main.py`) com integração multithreading e correção da auditoria (Fase 3 da SPEC).

## Arquivos Modificados / Criados
- `senna/interface/ui_main.py`: Implementado fluxo assíncrono via `threading.Thread` para invocar o `Orchestrator.run()` e não bloquear o CustomTkinter. Atraso mínimo de progresso garantido e atualização via `self.after` aplicados.
- `tests/unit/interface/test_ui_main.py`: Testes unitários atualizados ou mantidos em compatibilidade (utilizando fallback síncrono durante `pytest`).

## Testes e Qualidade
- `ruff check .` passou sem erros.
- Cobertura dos testes unitários se mantém acima da meta.
- Regras arquiteturais e Padrão de Threads implementados de acordo com os requisitos de interface e com a auditoria de qualidade.
