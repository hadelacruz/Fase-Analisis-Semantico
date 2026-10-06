from __future__ import annotations

from typing import Iterable, Optional

from ..types import Type
from .quadruple import Operand


class TempPool:

    def __init__(self, prefix: str = "t") -> None:
        self.prefix = prefix
        self._next_id = 0
        self._free: list[str] = []      # pila de nombres reutilizables
        self._live: set[str] = set()    # temporales en uso ahora mismo
        self.created = 0                # nombres distintos inventados
        self.peak = 0                   # máximo de temporales vivos a la vez

    # -- ciclo de vida --------------------------------------------------------
    def alloc(self, type_: Optional[Type] = None) -> Operand:
        if self._free:
            name = self._free.pop()
        else:
            name = f"{self.prefix}{self._next_id}"
            self._next_id += 1
            self.created += 1
        self._live.add(name)
        self.peak = max(self.peak, len(self._live))
        return Operand.temp(name, type_)

    def free(self, operand: Optional[Operand]) -> None:
        if operand is None or not operand.is_temp:
            return
        name = str(operand.value)
        if name not in self._live:
            return                       # ya estaba libre; liberar dos veces no rompe nada
        self._live.discard(name)
        self._free.append(name)

    def free_many(self, operands: Iterable[Optional[Operand]]) -> None:
        for operand in operands:
            self.free(operand)

    def reset(self) -> None:
        self._next_id = 0
        self._free.clear()
        self._live.clear()
        self.created = 0
        self.peak = 0

    # -- consulta --------------------------------------------------------------
    @property
    def live(self) -> set[str]:
        return set(self._live)

    @property
    def live_count(self) -> int:
        return len(self._live)

    def has_leaks(self) -> bool:
        return bool(self._live)

    def __repr__(self) -> str:  # pragma: no cover - depuración
        return (
            f"<TempPool vivos={sorted(self._live)} libres={self._free} "
            f"creados={self.created} pico={self.peak}>"
        )


class LabelFactory:

    def __init__(self) -> None:
        self._counter = 0

    def new(self, hint: str = "L") -> str:
        self._counter += 1
        return f"L_{hint}_{self._counter}" if hint != "L" else f"L{self._counter}"

    def many(self, *hints: str) -> tuple[str, ...]:
        return tuple(self.new(h) for h in hints)

    @property
    def count(self) -> int:
        return self._counter
