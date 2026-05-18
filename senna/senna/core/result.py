"""
Padrão Result[T, E] do Senna.

Toda operação que pode falhar retorna Result — nunca levanta exceção para a UI.
A UI lê result.success para decidir o que exibir (§7.3).

Uso — produzindo resultados:

    from senna.core.result import Result

    def add_user(payload: UserPayload) -> Result[str, str]:
        try:
            ...
            return Result.ok("Usuário criado com sucesso.")
        except ExecutionError as exc:
            return Result.fail(str(exc))

Uso — consumindo resultados:

    result = orchestrator.run(system_id, procedure_id, payload)

    if result.success:
        show_success(result.value)
    else:
        show_error(result.error)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")  # tipo do valor em caso de sucesso
E = TypeVar("E")  # tipo do erro em caso de falha


@dataclass(frozen=True)
class Result(Generic[T, E]):
    """
    Encapsula o resultado de uma operação que pode falhar.

    Exatamente um dos dois campos é preenchido:
      value — presente quando success=True
      error — presente quando success=False

    Use os construtores de classe Result.ok() e Result.fail()
    em vez de instanciar diretamente.
    """

    success: bool
    value: T | None
    error: E | None

    # ---------------------------------------------------------------------------
    # Construtores
    # ---------------------------------------------------------------------------

    @classmethod
    def ok(cls, value: T) -> Result[T, E]:
        """Constrói um resultado de sucesso."""
        return cls(success=True, value=value, error=None)

    @classmethod
    def fail(cls, error: E) -> Result[T, E]:
        """Constrói um resultado de falha."""
        return cls(success=False, value=None, error=error)

    # ---------------------------------------------------------------------------
    # Acesso seguro
    # ---------------------------------------------------------------------------

    def unwrap(self) -> T:
        """
        Retorna value se success=True.
        Levanta RuntimeError se chamado em resultado de falha.

        Use apenas em contextos onde o sucesso já foi verificado,
        como testes unitários ou após checagem explícita de result.success.
        """
        if not self.success:
            raise RuntimeError(f"Chamada a unwrap() em Result de falha. Erro: {self.error!r}")
        return self.value  # type: ignore[return-value]

    def unwrap_error(self) -> E:
        """
        Retorna error se success=False.
        Levanta RuntimeError se chamado em resultado de sucesso.
        """
        if self.success:
            raise RuntimeError(
                f"Chamada a unwrap_error() em Result de sucesso. Valor: {self.value!r}"
            )
        return self.error  # type: ignore[return-value]

    # ---------------------------------------------------------------------------
    # Representação
    # ---------------------------------------------------------------------------

    def __repr__(self) -> str:
        if self.success:
            return f"Result.ok({self.value!r})"
        return f"Result.fail({self.error!r})"
