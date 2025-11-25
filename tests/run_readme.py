from lazily import cell, slot


@cell
def name(ctx: dict) -> str:
    return "World"


@slot
def greeting(ctx: dict) -> str:
    print("Calculating greeting...")
    return f"Hello, {name(ctx).value}!"

@cell
def response(ctx: dict) -> str:
    return "How are you?"

@slot
def greeting_and_response(ctx: dict) -> str:
    print("Calculating greeting_and_response...")
    return f"{greeting(ctx)} {response(ctx).value}"

ctx = {}

# First access: runs the function
print(greeting(ctx))
# Calculating greeting...
# 'Hello, World!'

# Second access: uses cache (no print)
print(greeting(ctx))
# 'Hello, World!'

# Dependencies also access cached values
print(greeting_and_response(ctx))
# Calculating greeting_and_response...
# 'Hello, World! How are you?'

# Dependencies also also cached
print(greeting_and_response(ctx))
# 'Hello, World! How are you?'

# Update cell: invalidates cache
name(ctx).value = "Lazily"
print("Updated name to Lazily.")

# Access again: re-runs the function
print(greeting_and_response(ctx))
# Calculating greeting...
# Calculating greeting_and_response...
# 'Hello, Lazily! How are you?'
print(greeting_and_response(ctx))
# 'Hello, Lazily! How are you?'
