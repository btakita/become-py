from typing import Callable, Generic, Optional, TypeVar


__all__ = ["Cell", "cell"]

T = TypeVar("T")


class Cell(Generic[T]):
    """
    Base class for a lazy be Callable. Wraps a callable implementation field.

    If the be is not in the ctx argument, it will be evaluated and stored in the ctx.
    """

    callable: Callable[[dict], T]

    def __call__(self, ctx: dict) -> T:
        if self in ctx:
            return ctx[self]
        else:
            ctx[self] = self.callable(ctx)
            return ctx[self]

    def get(self, ctx: dict) -> Optional[T]:
        return ctx.get(self)

    def is_in(self, ctx: dict) -> bool:
        return self in ctx


class cell(Cell[T]):
    """
    A Be that can be initialized with the callable as an argument.

    Usage:
    ```
    from lazily import cell

    @cell
    def hello(ctx: dict) -> str:
        return "Hello"

    @cell
    def world(ctx: dict) -> str:
        return "World"

    greeting = cell(lambda ctx: f"{hello(ctx)} {world(ctx)}!")

    ctx = {}
    greeting(ctx)  # Hello World!
    ```
    """

    def __init__(self, callable: Callable[[dict], T]) -> None:
        self.callable = callable
