"""Interface principal da aplicação Senna."""

from __future__ import annotations

import customtkinter as ctk

from senna.core.orchestrator import orchestrator
from senna.interface.forms import PROCEDURE_FORMS, build_payload, validate_form


class SennaApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.title("Senna - Automação Hospitalar")
        self.geometry("600x600")

        self.system_id: str | None = None
        self.procedure_id: str | None = None
        self.input_widgets: dict[str, ctk.CTkEntry | ctk.CTkOptionMenu] = {}

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

    def _on_execute(self) -> None:
        if not self.system_id or not self.procedure_id:
            return

        self.execute_button.configure(state="disabled")
        self.result_label.configure(text="Executando...", text_color="orange")
        self.update()

        raw_values = {
            name: widget.get()
            for name, widget in self.input_widgets.items()
        }

        errors = validate_form(self.procedure_id, raw_values)
        if errors:
            self.result_label.configure(
                text="Erro de validação. Verifique os campos.", text_color="red"
            )
            self.execute_button.configure(state="normal")
            return

        try:
            payload = build_payload(self.procedure_id, raw_values)
            result = orchestrator.run(self.system_id, self.procedure_id, payload)
            
            if result.success:
                self.result_label.configure(text=str(result.value), text_color="green")
            else:
                self.result_label.configure(text=str(result.error), text_color="red")
        except Exception as exc:
            self.result_label.configure(text=f"Erro inesperado: {exc}", text_color="red")
        finally:
            self.execute_button.configure(state="normal")
