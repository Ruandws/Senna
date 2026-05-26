"""Testes unitários para senna.interface.ui_main.

O QUÊ: Valida a lógica de execução da UI conectada ao Orchestrator.
PARA QUÊ: Garantir que o fluxo §6.2/§6.3 está correto sem precisar
           inicializar CustomTkinter ou browser real.
COMO: Mocks do orchestrator, validate_form e build_payload.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from senna.core.result import Result

# ---------------------------------------------------------------------------
# Fixtures — SennaApp mockado (sem Tk)
# ---------------------------------------------------------------------------


@pytest.fixture()
def app() -> MagicMock:
    """Cria um mock de SennaApp com os atributos mínimos para testar _on_execute."""
    mock_app = MagicMock()
    mock_app.system_id = "servicos_ti"
    mock_app.procedure_id = "search_user_by_cpf"

    # Widgets de input simulados
    cpf_widget = MagicMock()
    cpf_widget.get.return_value = "123.456.789-00"
    mock_app.input_widgets = {"cpf": cpf_widget}

    # Error labels simulados
    cpf_error_label = MagicMock()
    mock_app._error_labels = {"cpf": cpf_error_label}

    # Labels e botões simulados
    mock_app.result_label = MagicMock()
    mock_app.execute_button = MagicMock()
    mock_app.update = MagicMock()

    return mock_app


# ---------------------------------------------------------------------------
# Testes — _on_execute
# ---------------------------------------------------------------------------


class TestOnExecuteGuardClauses:
    """Testes para guard clauses de _on_execute."""

    def test_returns_early_when_system_id_is_none(self, app: MagicMock) -> None:
        """_on_execute deve retornar imediatamente se system_id for None."""
        from senna.interface.ui_main import SennaApp

        app.system_id = None
        SennaApp._on_execute(app)

        app.execute_button.configure.assert_not_called()

    def test_returns_early_when_procedure_id_is_none(self, app: MagicMock) -> None:
        """_on_execute deve retornar imediatamente se procedure_id for None."""
        from senna.interface.ui_main import SennaApp

        app.procedure_id = None
        SennaApp._on_execute(app)

        app.execute_button.configure.assert_not_called()


class TestOnExecuteValidation:
    """Testes para validação de formulário com erros inline (RF-03)."""

    @patch("senna.interface.ui_main.validate_form")
    def test_shows_inline_errors_on_validation_failure(
        self,
        mock_validate: MagicMock,
        app: MagicMock,
    ) -> None:
        """Erros de validação devem ser exibidos inline nos campos (RF-03)."""
        from senna.interface.ui_main import SennaApp

        mock_validate.return_value = {"cpf": "CPF inválido: informe 11 dígitos numéricos."}

        SennaApp._on_execute(app)

        # Deve limpar erros anteriores
        app._clear_field_errors.assert_called_once()

        # Deve exibir erros inline
        app._show_field_errors.assert_called_once_with(
            {"cpf": "CPF inválido: informe 11 dígitos numéricos."},
        )

        # Deve exibir mensagem geral de erro
        app.result_label.configure.assert_any_call(
            text="Erro de validação. Verifique os campos.",
            text_color="red",
        )

        # Botão deve ser reabilitado
        app.execute_button.configure.assert_any_call(state="normal")

    @patch("senna.interface.ui_main.validate_form")
    def test_clears_previous_errors_before_validation(
        self,
        mock_validate: MagicMock,
        app: MagicMock,
    ) -> None:
        """_on_execute deve limpar erros inline antes de revalidar."""
        from senna.interface.ui_main import SennaApp

        mock_validate.return_value = {}

        with patch("senna.interface.ui_main.build_payload", side_effect=ValueError("err")):
            SennaApp._on_execute(app)

        app._clear_field_errors.assert_called_once()


class TestOnExecutePayload:
    """Testes para construção de payload."""

    @patch("senna.interface.ui_main.validate_form", return_value={})
    @patch("senna.interface.ui_main.build_payload")
    def test_stops_on_payload_build_error(
        self,
        mock_build: MagicMock,
        mock_validate: MagicMock,
        app: MagicMock,
    ) -> None:
        """Se build_payload levantar ValueError, deve exibir erro e parar."""
        from senna.interface.ui_main import SennaApp

        mock_build.side_effect = ValueError("Data de expiração inválida: 'invalid'")

        SennaApp._on_execute(app)

        app.result_label.configure.assert_any_call(
            text="Erro ao construir payload: Data de expiração inválida: 'invalid'",
            text_color="red",
        )
        app.execute_button.configure.assert_any_call(state="normal")


class TestOnExecuteOrchestratorFlow:
    """Testes para o fluxo de execução via Orchestrator (§6.2, §6.3)."""

    @patch("senna.interface.ui_main.orchestrator")
    @patch("senna.interface.ui_main.validate_form", return_value={})
    @patch("senna.interface.ui_main.build_payload", return_value="123.456.789-00")
    def test_displays_success_result(
        self,
        mock_build: MagicMock,
        mock_validate: MagicMock,
        mock_orchestrator: MagicMock,
        app: MagicMock,
    ) -> None:
        """Resultado de sucesso deve ser exibido em verde (§6.3)."""
        from senna.interface.ui_main import SennaApp

        mock_orchestrator.run.return_value = Result.ok("Usuário encontrado: João Silva")

        SennaApp._on_execute(app)

        mock_orchestrator.run.assert_called_once_with(
            "servicos_ti",
            "search_user_by_cpf",
            "123.456.789-00",
        )
        app.result_label.configure.assert_any_call(
            text="Usuário encontrado: João Silva",
            text_color="green",
        )
        app.execute_button.configure.assert_any_call(state="normal")

    @patch("senna.interface.ui_main.orchestrator")
    @patch("senna.interface.ui_main.validate_form", return_value={})
    @patch("senna.interface.ui_main.build_payload", return_value="123.456.789-00")
    def test_displays_failure_result(
        self,
        mock_build: MagicMock,
        mock_validate: MagicMock,
        mock_orchestrator: MagicMock,
        app: MagicMock,
    ) -> None:
        """Resultado de falha deve ser exibido em vermelho (§6.3)."""
        from senna.interface.ui_main import SennaApp

        mock_orchestrator.run.return_value = Result.fail("CPF não encontrado no sistema.")

        SennaApp._on_execute(app)

        app.result_label.configure.assert_any_call(
            text="CPF não encontrado no sistema.",
            text_color="red",
        )

    @patch("senna.interface.ui_main.orchestrator")
    @patch("senna.interface.ui_main.validate_form", return_value={})
    @patch("senna.interface.ui_main.build_payload", return_value="123.456.789-00")
    def test_no_exception_wrapping_around_orchestrator(
        self,
        mock_build: MagicMock,
        mock_validate: MagicMock,
        mock_orchestrator: MagicMock,
        app: MagicMock,
    ) -> None:
        """Orchestrator.run() não é envolvido em try/except — Result garante (§6.3).

        Se o Orchestrator lançar exceção inesperada, ela deve propagar.
        """
        from senna.interface.ui_main import SennaApp

        mock_orchestrator.run.side_effect = RuntimeError("Bug inesperado no orchestrator")

        with pytest.raises(RuntimeError, match="Bug inesperado no orchestrator"):
            SennaApp._on_execute(app)


class TestClearFieldErrors:
    """Testes para _clear_field_errors."""

    def test_clears_all_error_labels_and_restores_styling(self) -> None:
        """Deve limpar texto, ocultar labels de erro e restaurar estilos originais dos widgets."""
        import customtkinter as ctk

        from senna.interface.ui_main import SennaApp

        mock_app = MagicMock()

        # Labels de erro
        label_a = MagicMock()
        label_b = MagicMock()
        mock_app._error_labels = {"field_a": label_a, "field_b": label_b}

        # Widgets de input
        widget_entry = MagicMock(spec=ctk.CTkEntry)
        widget_menu = MagicMock(spec=ctk.CTkOptionMenu)
        mock_app.input_widgets = {"field_a": widget_entry, "field_b": widget_menu}

        # Cores originais
        mock_app._original_colors = {
            "field_a": {"border_color": "gray"},
            "field_b": {"fg_color": "blue", "button_color": "darkblue"},
        }

        SennaApp._clear_field_errors(mock_app)

        # Labels devem ser limpas e esquecidas pelo layout
        label_a.configure.assert_called_once_with(text="")
        label_a.pack_forget.assert_called_once()
        label_b.configure.assert_called_once_with(text="")
        label_b.pack_forget.assert_called_once()

        # Widgets devem restaurar cores originais
        widget_entry.configure.assert_called_once_with(border_color="gray")
        widget_menu.configure.assert_called_once_with(fg_color="blue", button_color="darkblue")


class TestShowFieldErrors:
    """Testes para _show_field_errors."""

    def test_sets_error_text_packs_labels_highlights_widgets_and_focuses_first(self) -> None:
        """Deve exibir mensagens de erro, aplicar destaque visual e focar no primeiro inválido."""
        import customtkinter as ctk

        from senna.interface.ui_main import SennaApp

        mock_app = MagicMock()

        # Labels de erro e frames
        cpf_label = MagicMock()
        date_label = MagicMock()
        mock_app._error_labels = {"cpf": cpf_label, "date": date_label}

        cpf_frame = MagicMock()
        date_frame = MagicMock()
        mock_app._field_frames = {"cpf": cpf_frame, "date": date_frame}

        # Widgets de input
        widget_entry = MagicMock(spec=ctk.CTkEntry)
        widget_menu = MagicMock(spec=ctk.CTkOptionMenu)
        mock_app.input_widgets = {"cpf": widget_entry, "date": widget_menu}

        errors = {
            "cpf": "CPF inválido.",
            "date": "Data inválida.",
        }

        SennaApp._show_field_errors(mock_app, errors)

        # Verifica textos dos labels
        cpf_label.configure.assert_called_once_with(text="CPF inválido.")
        date_label.configure.assert_called_once_with(text="Data inválida.")

        # Verifica empacotamento após o frame correspondente
        cpf_label.pack.assert_called_once_with(fill="x", padx=15, after=cpf_frame)
        date_label.pack.assert_called_once_with(fill="x", padx=15, after=date_frame)

        # Verifica destaque em vermelho
        widget_entry.configure.assert_called_once_with(border_color="red")
        widget_menu.configure.assert_called_once_with(fg_color="red", button_color="red")

        # Verifica foco automático apenas no primeiro campo inválido
        widget_entry.focus_set.assert_called_once()
        widget_menu.focus_set.assert_not_called()

    def test_ignores_fields_without_error_label(self) -> None:
        """Campos sem label de erro registrada não devem causar exceção."""
        from senna.interface.ui_main import SennaApp

        mock_app = MagicMock()
        mock_app._error_labels = {}
        mock_app._field_frames = {}
        mock_app.input_widgets = {}

        # Não deve levantar exceção
        SennaApp._show_field_errors(mock_app, {"unknown_field": "Erro qualquer."})
