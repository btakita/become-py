from typing import Protocol, TypeVar


__all__ = ["LazilyCallable", "ResolveCallable"]

C = TypeVar("C")
T = TypeVar("T")

class LazilyCallable(Protocol[C, T]):
    def __call__(self, ctx: C) -> T: ...

class ResolveCallable(Protocol[C]):
    def __call__(self, ctx: C) -> dict: ...
