# tipo Result[T, E]: encapsula sucesso/falha sem lançar exceção na UI

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Generic, TypeVar

T = TypeVar("T")
E = TypeVar("E")


@dataclass(frozen=True)
class Result(Generic[T, E]):
    _value: T | None
    _error: E | None
    success: bool

    @classmethod
    def ok(cls, value: T) -> "Result[T, E]":
        return cls(_value=value, _error=None, success=True)

    @classmethod
    def fail(cls, error: E) -> "Result[T, E]":
        return cls(_value=None, _error=error, success=False)

    @property
    def value(self) -> T:
        if not self.success:
            raise ValueError("Result é falha — acesse 'error', não 'value'.")
        return self._value  # type: ignore[return-value]

    @property
    def error(self) -> E:
        if self.success:
            raise ValueError("Result é sucesso — acesse 'value', não 'error'.")
        return self._error  # type: ignore[return-value]

    def map(self, fn: Callable[[T], T]) -> "Result[T, E]":
        """Aplica fn ao valor se sucesso. Falha passa direto."""
        if self.success:
            return Result.ok(fn(self.value))
        return self

    def __repr__(self) -> str:
        if self.success:
            return f"Result.ok({self._value!r})"
        return f"Result.fail({self._error!r})"
