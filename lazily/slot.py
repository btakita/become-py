from typing import Any, Generic, Optional, Protocol, TypeVar

from .types import LazilyCallable


__all__ = ["BaseSlot", "Slot", "slot", "slot_stack"]


T = TypeVar("T")

class SlotSubscriber[T](Protocol):
    def __call__[**P](self, slot: "Slot", ctx: dict) -> Any: ...

class BaseSlot(Generic[T]):
    """
    Base class for a lazy slot Callable. Wraps a callable implementation field.
    Does not subscribe to Cells.
    """

    __slots__ = "callable"

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
        ctx.pop(self, None)

    def is_in(self, ctx: dict) -> bool:
        return self in ctx


class Slot(BaseSlot[T]):
    """
    Base class for a lazy slot Callable that subscribes to Cells.
    """

    __slots__ = "_subscribers", "callable"

    callable: LazilyCallable[T]

    def __init__(self) -> None:
        self._subscribers = set()
    def __call__(self, ctx: dict) -> T:
        if len(slot_stack) > 0:
            parent_slot = slot_stack[-1]
            self.subscribe(lambda self, ctx : parent_slot.reset(ctx))

        if self in ctx:
            return ctx[self]
        else:
            try:
                slot_stack.append(self)
                ctx[self] = self.callable(ctx)
                self.touch(ctx)
            finally:
                slot_stack.pop()
            return ctx[self]

    def reset(self, ctx: dict) -> None:
        super().reset(ctx)
        self.touch(ctx)
        self._subscribers.clear()

    def subscribe(self, subscriber: SlotSubscriber[T]) -> None:
        self._subscribers.add(subscriber)

    def touch(self, ctx: dict) -> None:
        for subscriber in self._subscribers:
            subscriber(self, ctx)

slot_stack: list[Slot] = []


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
        print("Calculating greeting...")
        return f"{hello(ctx)} {world(ctx)}!"

    @slot
    def response(ctx: dict) -> str:
        return "How are you?"

    @slot
    def greeting_and_response(ctx: dict) -> str:
        print("Calculating greeting_and_response...")
        return f"{greeting(ctx)} {response(ctx)}"

    ctx = {}

    greeting(ctx)
    # Calculating greeting...
    # Hello World!

    greeting_and_response(ctx)
    # Calculating greeting and response...
    # Hello World! How are you?

    greeting(ctx)
    # Hello World!

    greeting_and_response(ctx)
    # Hello World! How are you?
    ```
    """

    def __init__(self, callable: LazilyCallable[T]) -> None:
        super().__init__()
        self.callable = callable
