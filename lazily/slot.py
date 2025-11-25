from typing import Generic, Optional, Protocol, TypeVar


__all__ = ["BaseSlot", "LazilyCallable", "Slot", "callable_stack", "cell", "slot"]

T = TypeVar("T")

class LazilyCallable(Protocol[T]):
    def __call__(self, ctx: dict) -> T: ...

class BaseSlot(Generic[T]):
    """
    Base class for a lazy slot Callable. Wraps a callable implementation field.
    Does not subscribe to Cells.
    """
    callable: LazilyCallable[T]

    def __call__(self, ctx: dict) -> T:
        if self in ctx:
            return ctx[self]
        else:
            ctx[self] = self.callable(ctx)
            return ctx[self]

    def __repr__(self) -> str:
        return f"<Slot {self.callable.__name__}>"

    def get(self, ctx: dict) -> Optional[T]:
        return ctx.get(self)

    def reset(self, ctx: dict) -> None:
        del ctx[self]

    def is_in(self, ctx: dict) -> bool:
        return self in ctx

class Slot(BaseSlot[T]):
    """
    Base class for a lazy slot Callable that subscribes to Cells.
    """

    callable: LazilyCallable[T]

    def __call__(self, ctx: dict) -> T:
        if self in ctx:
            return ctx[self]
        else:
            try:
                callable_stack.append(self)
                ctx[self] = self.callable(ctx)
            finally:
                callable_stack.pop()
            return ctx[self]

callable_stack: list[Slot] = []

class slot(Slot[T]):
    """
    A Slot that can be initialized with the callable as an argument.

    Usage:
    ```
    from lazily import slot

    @slot
    def hello(ctx: dict) -> str:
        return "Hello"

    @slot
    def world(ctx: dict) -> str:
        return "World"

    @slot
    def greeting(ctx: dict) -> str:
        print("Calculating...")
        return f"{hello(ctx)} {world(ctx)}!"

    ctx = {}
    greeting(ctx)
    # Calculating...
    # Hello World!
    greeting(ctx)
    # Calculating...
    ```
    """

    def __init__(self, callable: LazilyCallable[T]) -> None:
        self.callable = callable
