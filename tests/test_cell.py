from lazily import Cell, cell, slot


class TestCell:
    """Test the base cell class functionality."""

    def test_cell_with_subscriber(self) -> None:
        @slot
        def slot_events(ctx: dict) -> list[str]:
            return []

        @slot
        def hello(ctx: dict) -> Cell[str]:
            slot_events(ctx).append("hello")
            return Cell(ctx, "Hello")

        @cell
        def name(ctx: dict) -> str:
            slot_events(ctx).append("name")
            return "World"

        @slot
        def greeting(ctx: dict) -> str:
            slot_events(ctx).append("greeting")
            return f"{hello(ctx).value} {name(ctx).value}!"

        @cell
        def response(ctx: dict) -> str:
            return "How are you?"

        @slot
        def greeting_and_response(ctx: dict) -> str:
            slot_events(ctx).append("greeting_and_response")
            return f"{greeting(ctx)} {response(ctx).value}"

        ctx = {}
        assert ctx.get(greeting) is None
        assert slot_events(ctx) == []
        assert greeting(ctx) == "Hello World!"
        assert slot_events(ctx) == ["greeting", "hello", "name"]
        assert greeting_and_response(ctx) == "Hello World! How are you?"
        assert slot_events(ctx) == ["greeting", "hello", "name", "greeting_and_response"]
        name(ctx).value = "You"
        assert ctx.get(greeting) is None
        assert slot_events(ctx) == ["greeting", "hello", "name", "greeting_and_response"]
        assert greeting_and_response(ctx) == "Hello You! How are you?"
        assert slot_events(ctx) == [
            "greeting",
            "hello",
            "name",
            "greeting_and_response",
            "greeting_and_response",
            "greeting",
        ]
