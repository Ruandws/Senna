"""Seletores da página de usuários — Serviços TI."""

from __future__ import annotations

# Navegação lateral
MENU_SEARCH_LINK: str = "role=link[name=' Pesquisa de usuário'] >> i"

# Pesquisa
SEARCH_INPUT: str = 'input[ng-model="parametro"]'
SEARCH_BUTTON: str = "role=button[name='Pesquisar']"

# Tabela de resultados
RESULT_ROWS: str = "tbody tr"
ROW_LINK: str = "td:nth-child(1) a"  # contém href="#/usuarios/LOGIN"
ROW_NOME: str = "td:nth-child(4)"