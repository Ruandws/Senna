"""Entry point da aplicação Senna.

Instancia a interface principal e inicia o loop de eventos.
Nenhuma lógica de negócio deve residir neste módulo (§7 SPEC).
"""

from senna.interface.ui_main import SennaApp


def main() -> None:
    """Cria a janela principal e executa o mainloop."""
    app = SennaApp()
    app.mainloop()


if __name__ == "__main__":
    main()
