from lazily import cell, Cell, slot


class TestCell:
    """Test the base cell class functionality."""

    def test_cell_with_subscriber(self) -> None:
        @slot
        def hello(ctx: dict) -> Cell[str]:
            return Cell(ctx, "Hello")

        @cell
        def world(ctx: dict) -> str:
            return "World"

        @slot
        def greeting(ctx: dict) -> str:
            return f"{hello(ctx).value} {world(ctx).value}"

        ctx = {}
        assert ctx.get(greeting) is None
        assert greeting(ctx) == "Hello World"
        world(ctx).value = "You!"
        assert ctx.get(greeting) is None
        assert greeting(ctx) == "Hello You!"
