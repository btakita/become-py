from typing import Any, Protocol, TypeVar


__all__ = ["LazilyCallable"]

T = TypeVar("T")

class LazilyCallable(Protocol[T]):
    def __call__(self, ctx: dict) -> T: ...
