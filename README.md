# lazily

A Python library for lazy evaluation with context caching.

## Installation

```
pip install lazily
```

### Example usage

```python
from lazily import be


@be
def hello(ctx: dict) -> str:
    return "Hello"


@be
def world(ctx: dict) -> str:
    return "World"


greeting = be(lambda ctx: f"{hello(ctx)} {world(ctx)}!")

ctx = {}
greeting(ctx)  # Hello World!
```
