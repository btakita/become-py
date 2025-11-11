# lazily

A Python library for lazy evaluation with context caching.

## Installation

```
pip install lazily
```

### Example usage

```python
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
