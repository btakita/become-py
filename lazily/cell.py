from typing import Any, Generic, Protocol, TypeVar

from .slot import BaseSlot, slot_stack
from .types import LazilyCallable


__all__ = ["Cell", "cell"]

T = TypeVar("T")

class CellSubscriber[T](Protocol):
    def __call__[**P](self, ctx: dict, value: T) -> Any: ...

class Cell(Generic[T]):
    """
    A subscribable that can be used with Slots.
    """
    __slots__ = ("_subscribers", "_value", "ctx", "name")

    def __init__(self, ctx: dict, initial_value: T) -> None:
        self.ctx = ctx
        self._value = initial_value
        self._subscribers = set()

    def __call__(self) -> T:
        return self.value

    @property
    def value(self) -> T:
        if len(slot_stack) > 0:
            callable = slot_stack[-1]
            self.subscribe(lambda ctx, value : callable.reset(self.ctx))
        return self._value

    @value.setter
    def value(self, value: T) -> None:
        _value = self._value
        self._value = value
        if self._value != _value:
            self.touch()

    def subscribe(self, subscriber: CellSubscriber[T]) -> None:
        self._subscribers.add(subscriber)

    def touch(self) -> None:
        for subscriber in self._subscribers:
            subscriber(self.ctx, self._value)

none_callable = lambda ctx: None

class cell(BaseSlot[Cell[T]]):
    """
    
    
    ==Example==
    ```python
    from lazily import cell, slot
    
    
    @cell
    def name(ctx: dict) -> str:
        return "World"
    
    
    @slot
    def greeting(ctx: dict) -> str:
        print("Calculating...")
        return f"Hello, {name(ctx).value}!"
    
    
    ctx = {}
    
    # First access: runs the function
    greeting(ctx)
    # Calculating...
    # 'Hello, World!'
    
    # Second access: uses cache (no print)
    greeting(ctx)
    # 'Hello, World!'
    
    # Update cell: invalidates cache
    name(ctx).value = "Lazily"
    
    # Access again: re-runs the function
    greeting(ctx)
    # Calculating...
    # 'Hello, Lazily!'
    ```
    """
    def __init__(self, callable: LazilyCallable[T] = none_callable) -> None:
        self.callable = lambda ctx: Cell(ctx, callable(ctx))

