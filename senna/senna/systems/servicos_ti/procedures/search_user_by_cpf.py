"""Procedure: pesquisar usuários por CPF — Serviços TI."""

from __future__ import annotations

import re

from playwright.sync_api import BrowserContext

from senna.core.base_procedure import BaseProcedure
from senna.core.exceptions import ExecutionError
from senna.core.models import UserSearchResult
from senna.core.result import Result
from senna.systems.servicos_ti.config import BASE_URL
from senna.systems.servicos_ti.pages.user_page import UserPage


class SearchUserByCpfProcedure(BaseProcedure):

    @property
    def procedure_id(self) -> str:
        return "search_user_by_cpf"

    def validate(self, payload: str) -> Result[None, str]:  # type: ignore[override]
        """Valida o CPF antes de qualquer I/O. Aceita com ou sem máscara."""
        cpf_digits = re.sub(r"\D", "", payload)
        if len(cpf_digits) != 11:
            return Result.fail("CPF inválido: informe 11 dígitos numéricos.")
        return Result.ok(None)

    def execute(  # type: ignore[override]
        self,
        payload: str,
        ctx: BrowserContext,
    ) -> Result[list[UserSearchResult], str]:
        """
        Pesquisa usuários pelo CPF e retorna os resultados encontrados.

        Returns:
            Result.ok([])                  — nenhum usuário encontrado.
            Result.ok([UserSearchResult])  — um ou mais usuários encontrados.
            Result.fail(mensagem)          — erro durante a execução.
        """
        cpf_digits = re.sub(r"\D", "", payload)

        try:
            page = ctx.new_page()
            page.goto(f"{BASE_URL}/#/usuarios", wait_until="networkidle")

            user_page = UserPage(page)
            results = user_page.search_by_cpf(cpf_digits)

            return Result.ok(results)

        except ExecutionError as exc:
            return Result.fail(str(exc))
        except Exception as exc:
            return Result.fail(f"Erro inesperado na pesquisa por CPF: {exc}")
        finally:
            page.close()