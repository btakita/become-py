# lazily

A Python library for lazy evaluation with context caching.

## Installation

```
pip install lazily
```

### Example usage

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
