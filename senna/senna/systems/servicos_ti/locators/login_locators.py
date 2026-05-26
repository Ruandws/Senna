"""Seletores da página de login — Serviços TI.

Esta camada isola os seletores usados por `LoginPage`. Seguindo a especificação
`SPEC.md` (§7.4), os seletores são declarados como strings simples e reutilizados
nos objetos de página, permitindo que os testes unitários e a validação com
Playwright sejam consistentes.
"""

from __future__ import annotations

# Navegação inicial
# Clique no link "Entrar" da barra de navegação
NAV_ENTRAR_LINK: str = "role=link[name='Entrar']"

# Formulário de login
USERNAME_INPUT: str = "role=textbox >> nth=0"
PASSWORD_INPUT: str = "input[type=\"password\"]"
SUBMIT_BUTTON: str = "role=button[name='Entrar']"