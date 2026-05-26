"""Seletores da página de usuários — Serviços TI."""

from __future__ import annotations

# Navegação lateral
MENU_SEARCH_LINK: str = "role=link[name='Pesquisa de usuário']"

# Pesquisa
SEARCH_INPUT: str = 'input[placeholder="Digite o login ou nome"]'
SEARCH_BUTTON: str = "role=button[name='Pesquisar']"

# Tabela de resultados
RESULT_ROWS: str = "table tbody tr"
ROW_LINK: str = "td:first-child a"
ROW_NOME: str = "td:nth-child(2)"