"""Interface principal da aplicação Senna.

Conecta a UI ao Orchestrator conforme Seção 6.2 (Fluxo de Execução)
e Seção 6.3 (Padrão Result) da SPEC.
"""

from __future__ import annotations

import logging

import customtkinter as ctk

from senna.core.orchestrator import orchestrator
from senna.interface.forms import PROCEDURE_FORMS, build_payload, validate_form

app_logger = logging.getLogger("senna.app")


class SennaApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.title("Senna - Automação Hospitalar")
        self.geometry("600x600")

        self.system_id: str | None = None
        self.procedure_id: str | None = None
        self.input_widgets: dict[str, ctk.CTkEntry | ctk.CTkOptionMenu] = {}
        self._error_labels: dict[str, ctk.CTkLabel] = {}

        self._build_ui()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # 1. Seletor de Sistema
        self.system_frame = ctk.CTkFrame(self)
        self.system_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        self.system_label = ctk.CTkLabel(self.system_frame, text="Sistema:")
        self.system_label.pack(side="left", padx=10, pady=10)

        systems = orchestrator.list_systems()
        self.system_dropdown = ctk.CTkOptionMenu(
            self.system_frame,
            values=systems if systems else ["Nenhum sistema disponível"],
            command=self._on_system_change,
        )
        self.system_dropdown.pack(side="left", padx=10, pady=10, fill="x", expand=True)
        if not systems:
            self.system_dropdown.configure(state="disabled")

        # 2. Seletor de Procedimento
        self.procedure_frame = ctk.CTkFrame(self)
        self.procedure_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.procedure_label = ctk.CTkLabel(self.procedure_frame, text="Procedimento:")
        self.procedure_label.pack(side="left", padx=10, pady=10)

        self.procedure_dropdown = ctk.CTkOptionMenu(
            self.procedure_frame,
            values=["Selecione um sistema primeiro"],
            state="disabled",
            command=self._on_procedure_change,
        )
        self.procedure_dropdown.pack(side="left", padx=10, pady=10, fill="x", expand=True)

        # 3. Formulário Dinâmico
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")

        # 4. Execução e Resultado
        self.action_frame = ctk.CTkFrame(self)
        self.action_frame.grid(row=3, column=0, padx=20, pady=(10, 20), sticky="ew")

        self.execute_button = ctk.CTkButton(
            self.action_frame,
            text="Executar",
            state="disabled",
            command=self._on_execute,
        )
        self.execute_button.pack(pady=(10, 5))

        self.result_label = ctk.CTkLabel(self.action_frame, text="", font=("Arial", 12, "bold"))
        self.result_label.pack(pady=5)

    def _on_system_change(self, value: str) -> None:
        self.system_id = value
        self.procedure_id = None
        self._clear_form()
        self.result_label.configure(text="")

        procedures = orchestrator.list_procedures(value)
        if procedures:
            self.procedure_dropdown.configure(state="normal", values=procedures)
            self.procedure_dropdown.set(procedures[0])
            self._on_procedure_change(procedures[0])
        else:
            self.procedure_dropdown.configure(state="disabled", values=["Sem procedimentos"])
            self.procedure_dropdown.set("Sem procedimentos")
            self.execute_button.configure(state="disabled")

    def _on_procedure_change(self, value: str) -> None:
        if value in ("Sem procedimentos", "Selecione um sistema primeiro"):
            return

        self.procedure_id = value
        self._clear_form()
        self._render_form()
        self.execute_button.configure(state="normal")
        self.result_label.configure(text="")

    def _clear_form(self) -> None:
        for widget in self.form_frame.winfo_children():
            widget.destroy()
        self.input_widgets.clear()
        self._error_labels.clear()

    def _render_form(self) -> None:
        if not self.procedure_id:
            return

        fields = PROCEDURE_FORMS.get(self.procedure_id, [])
        if not fields:
            label = ctk.CTkLabel(self.form_frame, text="Nenhum formulário definido.")
            label.pack(pady=20)
            return

        for field in fields:
            frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
            frame.pack(fill="x", padx=10, pady=5)

            label_text = f"{field.label} *" if field.required else field.label
            label = ctk.CTkLabel(frame, text=label_text)
            label.pack(side="left")

            if field.field_type == "select" and field.options:
                widget = ctk.CTkOptionMenu(frame, values=field.options)
                widget.set(field.options[0])
            else:
                widget = ctk.CTkEntry(frame, width=200)

            widget.pack(side="right")
            self.input_widgets[field.name] = widget

            # Reserva label de erro inline abaixo de cada campo (RF-03)
            error_label = ctk.CTkLabel(
                self.form_frame,
                text="",
                text_color="red",
                font=("Arial", 10),
            )
            error_label.pack(fill="x", padx=15)
            self._error_labels[field.name] = error_label

    # ------------------------------------------------------------------
    # Erros inline (RF-03)
    # ------------------------------------------------------------------

    def _clear_field_errors(self) -> None:
        """Remove todas as mensagens de erro inline dos campos."""
        for error_label in self._error_labels.values():
            error_label.configure(text="")

    def _show_field_errors(self, errors: dict[str, str]) -> None:
        """Exibe mensagens de erro inline próximas ao campo inválido."""
        for field_name, message in errors.items():
            error_label = self._error_labels.get(field_name)
            if error_label is not None:
                error_label.configure(text=message)

    # ------------------------------------------------------------------
    # Execução — §6.2 Fluxo de Execução, §6.3 Padrão Result
    # ------------------------------------------------------------------

    def _on_execute(self) -> None:
        """Executa o procedimento selecionado via Orchestrator.

        Fluxo conforme §6.2:
          1. validate_form → erros inline → parar
          2. build_payload → monta dataclass tipada
          3. orchestrator.run() → abre BrowserContext, executa, fecha
          4. Exibe resultado conforme result.success (§6.3)

        O Orchestrator garante Result[T, E] — a UI nunca captura exceção
        de automação (§6.3).
        """
        if not self.system_id or not self.procedure_id:
            return

        self._clear_field_errors()
        self.execute_button.configure(state="disabled")
        self.result_label.configure(text="Executando...", text_color="orange")
        self.update()

        # 1. Coleta valores brutos do formulário
        raw_values = {
            name: widget.get()
            for name, widget in self.input_widgets.items()
        }

        # 2. Validação de formulário — erros inline (RF-03)
        errors = validate_form(self.procedure_id, raw_values)
        if errors:
            self._show_field_errors(errors)
            self.result_label.configure(
                text="Erro de validação. Verifique os campos.", text_color="red",
            )
            self.execute_button.configure(state="normal")
            return

        # 3. Construção do payload tipado
        try:
            payload = build_payload(self.procedure_id, raw_values)
        except ValueError as exc:
            app_logger.error("Falha ao construir payload: %s", exc)
            self.result_label.configure(
                text=f"Erro ao construir payload: {exc}", text_color="red",
            )
            self.execute_button.configure(state="normal")
            return

        # 4. Execução via Orchestrator (§6.2)
        #    O Orchestrator abre BrowserContext, faz login, executa o procedimento,
        #    faz logout e fecha o contexto no finally — nunca deixa contexto aberto.
        #    Retorna Result[T, E] — a UI lê result.success (§6.3).
        result = orchestrator.run(self.system_id, self.procedure_id, payload)

        # 5. Exibição do resultado (§6.3)
        if result.success:
            self.result_label.configure(text=str(result.value), text_color="green")
        else:
            self.result_label.configure(text=str(result.error), text_color="red")

        self.execute_button.configure(state="normal")
