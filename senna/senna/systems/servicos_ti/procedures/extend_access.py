"""Procedure: alterar data de expiração de acesso — Serviços TI."""

from __future__ import annotations

import re

from playwright.sync_api import BrowserContext

from senna.core.base_procedure import BaseProcedure
from senna.core.exceptions import ExecutionError
from senna.core.models import AccessPayload
from senna.core.result import Result
from senna.systems.servicos_ti.config import BASE_URL
from senna.systems.servicos_ti.pages.user_details_page import UserDetailsPage
from senna.systems.servicos_ti.pages.user_page import UserPage

_CPF_LENGTH: int = 11


def _is_cpf(registration: str) -> bool:
    """Retorna True se registration contém exatamente 11 dígitos (CPF)."""
    return len(re.sub(r"\D", "", registration)) == _CPF_LENGTH


def _resolve_login_from_cpf(
    cpf: str,
    ctx: BrowserContext,
) -> Result[str, str]:
    """Pesquisa por CPF via UserPage e retorna o login do primeiro resultado.

    Reutiliza o page object UserPage.search_by_cpf() para evitar
    duplicação com search_user_by_cpf.py, sem criar dependência
    entre procedures.
    """
    cpf_digits = re.sub(r"\D", "", cpf)
    page = ctx.new_page()
    try:
        page.goto(f"{BASE_URL}/#/usuarios", wait_until="networkidle")
        user_page = UserPage(page)
        results = user_page.search_by_cpf(cpf_digits)

        if not results:
            return Result.fail(f"Nenhum usuário encontrado para o CPF '{cpf}'.")

        if len(results) > 1:
            logins = ", ".join(r.login for r in results)
            return Result.fail(
                f"CPF '{cpf}' retornou {len(results)} usuários ({logins}). "
                "Informe o login diretamente para evitar ambiguidade."
            )

        return Result.ok(results[0].login)

    except ExecutionError as exc:
        return Result.fail(str(exc))
    except Exception as exc:
        return Result.fail(f"Erro ao resolver login a partir do CPF '{cpf}': {exc}")
    finally:
        page.close()


class ExtendAccessProcedure(BaseProcedure):
    """Procedimento P3 — Alterar data de expiração de acesso do usuário."""

    @property
    def procedure_id(self) -> str:
        return "extend_access"

    def validate(self, payload: AccessPayload) -> Result[None, str]:  # type: ignore[override]
        """Valida o payload antes de qualquer I/O.

        Regras:
        - registration não pode estar vazio
        - expiration_date deve ser uma data válida (tipagem garante via dataclass)
        """
        if not payload.registration or not payload.registration.strip():
            return Result.fail("Matrícula/login não pode estar vazio.")

        return Result.ok(None)

    def execute(  # type: ignore[override]
        self,
        payload: AccessPayload,
        ctx: BrowserContext,
    ) -> Result[str, str]:
        """Altera a data de expiração do acesso do usuário.

        Fluxo:
        1. Resolve login (direto ou via CPF → pesquisa)
        2. Navega para detalhes do usuário via URL
        3. Preenche nova data de expiração
        4. Clica em 'Atualizar dados'
        5. Reload + verifica se a data persistiu

        Returns:
            Result.ok(mensagem)  — data alterada e verificada.
            Result.fail(mensagem) — erro durante a execução.
        """
        # 1. Resolver login
        if _is_cpf(payload.registration):
            login_result = _resolve_login_from_cpf(payload.registration, ctx)
            if not login_result.success:
                return Result.fail(login_result.unwrap_error())
            login = login_result.unwrap()
        else:
            login = payload.registration.strip()

        # 2–5. Navegar, preencher, atualizar e verificar
        page = ctx.new_page()
        try:
            details_page = UserDetailsPage(page)
            details_page.navigate(login)
            details_page.set_expiration_date(payload.expiration_date)
            details_page.click_update()

            date_persisted = details_page.verify_date_saved(payload.expiration_date)
            if not date_persisted:
                return Result.fail(
                    f"Verificação falhou: data não persistiu após reload "
                    f"para o usuário '{login}'."
                )

            formatted_date = payload.expiration_date.strftime("%d/%m/%Y")
            return Result.ok(
                f"Data de expiração do usuário '{login}' alterada para {formatted_date}."
            )

        except ExecutionError as exc:
            return Result.fail(str(exc))
        except Exception as exc:
            return Result.fail(
                f"Erro inesperado ao alterar data de expiração do usuário '{login}': {exc}"
            )
        finally:
            page.close()
