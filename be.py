from typing import Callable, Generic, Optional, TypeVar

__all__ = ["be", "be_singleton"]

T = TypeVar("T")

class BeBase(Generic[T]):
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

class be_singleton(BeBase[T]):
    instance: Optional[BeBase[T]] = None

    def __new__(cls, ctx: dict) -> T:
        if cls.instance is None:
            cls.instance = super().__new__(cls)

        return cls.instance(ctx)

class be(BeBase[T]):
    def __init__(self, callable: Callable[[dict], T]) -> None:
        self.callable = callable
