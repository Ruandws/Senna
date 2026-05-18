# Nota de Atualização da Spec
Data: 18 de maio de 2026
Tipo: Adição de arquivos raiz na estrutura de diretórios

## O que foi feito
- A Seção 8 (Estrutura de Diretórios) do `SPEC.md` foi expandida significativamente.
- Foram listados os principais arquivos da raiz do projeto (`.env.example`, `.gitignore`, `pyproject.toml`, `README.md`, `requirements.md`, `ruff.toml`, `SPEC.md`) com descrições breves de suas funções.
- Detalhamos os arquivos internos essenciais dos módulos `core`, `interface` e `utils`, além de mapearmos o `main.py` como entry point. Arquivos de inicialização (`__init__.py`) e diretórios de cache (`__pycache__`) foram deliberadamente omitidos para manter a árvore limpa.

## Justificativa
Garantir que a documentação ("Fonte da Verdade") reflita com precisão os arquivos de configuração, manifestos e de documentação que compõem a fundação do repositório, facilitando a navegação e entendimento para os desenvolvedores e ferramentas de IA que interagem com a base de código.
