import pytest

from lazily import Cell, cell


class TestBe:
    """Test the base Be class functionality."""

    def test_cell_abstract_nature(self):
        """Test that Be cannot be instantiated directly without callable."""
        with pytest.raises(AttributeError):
            instance_cell = Cell()
            instance_cell({})

    def test_cell_with_manual_callable(self):
        """Test Be with manually assigned callable."""
        instance_cell = Cell()
        instance_cell .callable = lambda ctx: "test value"

        ctx = {}
        instance = instance_cell (ctx)

        assert instance == "test value"
        assert instance_cell  in ctx
        assert ctx[instance_cell ] == "test value"

    def test_cell_get_method(self):
        """Test the get method."""
        instance_cell = Cell()
        instance_cell.callable = lambda ctx: "test value"

        ctx = {}

        # Should return None when not in context
        assert instance_cell.get(ctx) is None

        # Should return value after calling
        instance_cell(ctx)
        assert instance_cell.get(ctx) == "test value"

    def test_cell_is_in_method(self):
        """Test the is_in method."""
        instance_cell = Cell()
        instance_cell.callable = lambda ctx: "test value"

        ctx = {}

        # Should not be in context initially
        assert not instance_cell.is_in(ctx)

        # Should be in context after calling
        instance_cell(ctx)
        assert instance_cell.is_in(ctx)


class TestBeClass:
    """Test the be class functionality."""

    def test_simple_be(self):
        """Test basic be functionality."""
        hello = cell(lambda ctx: "Hello")

        ctx = {}
        result_hello = hello(ctx)

        assert result_hello == "Hello"
        assert hello in ctx
        assert ctx[hello] == "Hello"

        @cell
        def world(ctx: dict) -> str:
            return "World"

        result_world = world(ctx)
        assert result_world == "World"
        assert world in ctx
        assert ctx[world] == "World"

    def test_cell_caching(self):
        """Test that be caches results."""
        call_count = 0

        @cell
        def counter(ctx: dict):
            nonlocal call_count
            call_count += 1
            return f"called {call_count} times"

        ctx = {}

        # First call
        result1 = counter(ctx)
        assert result1 == "called 1 times"
        assert call_count == 1

        # Second call should return cached value
        result2 = counter(ctx)
        assert result2 == "called 1 times"
        assert call_count == 1  # Should not increment

    def test_cell_dependency_chain(self):
        """Test be objects depending on other be objects."""

        first = cell(lambda ctx: "Hello")
        second = cell(lambda ctx: "World")
        combined = cell(lambda ctx: f"{first(ctx)} {second (ctx)}!")

        ctx = {}
        result = combined (ctx)

        assert result == "Hello World!"
        assert first in ctx
        assert second  in ctx
        assert combined  in ctx

    def test_multiple_contexts(self):
        """Test that different contexts are independent."""
        value = cell(lambda ctx: len(ctx))

        ctx1 = {}
        ctx2 = {"existing": "value"}

        result1 = value(ctx1)
        result2 = value(ctx2)

        assert result1 == 0
        assert result2 == 1

    def test_cell_with_complex_types(self):
        """Test be with complex return types."""
        dict_cell = cell(lambda ctx: {"key": "value", "number": 42})
        list_cell = cell(lambda ctx: [1, 2, 3])

        ctx = {}

        dict_result = dict_cell(ctx)
        list_result = list_cell(ctx)

        assert dict_result == {"key": "value", "number": 42}
        assert list_result == [1, 2, 3]


class TestIntegration:
    """Integration tests combining different be types."""

    def test_complex_dependency_graph(self):
        """Test a complex dependency graph."""
        @cell
        def config(ctx: dict) -> dict:
            return {"api_url": "https://api.example.com", "timeout": 30}

        class HttpClient(Cell[str]):
            def callable(self, ctx: dict) -> str:
                _config = config(ctx)
                return f"HttpClient({_config['api_url']}, timeout={_config['timeout']})"

        http_client = HttpClient()

        user_service_cell = cell(lambda ctx: f"UserService({http_client(ctx)})")
        auth_service_cell = cell(lambda ctx: f"AuthService({http_client(ctx)})")

        @cell
        def app(ctx: dict) -> str:
            return f"App(user={user_service_cell(ctx)}, auth={auth_service_cell(ctx)})"

        ctx = {}
        result = app(ctx)

        expected = "App(user=UserService(HttpClient(https://api.example.com, timeout=30)), auth=AuthService(HttpClient(https://api.example.com, timeout=30)))"
        assert result == expected

    def test_context_isolation(self):
        """Test that different contexts don't interfere with each other."""
        @cell
        def value_cell(ctx: dict) -> str:
            return ctx.get("input", "default")

        @cell
        def multiplier_cell(ctx: dict) -> int:
            base = value_cell(ctx)
            return len(base) * 2

        ctx1 = {"input": "hello"}
        ctx2 = {"input": "hi"}
        ctx3 = {}

        result1 = multiplier_cell(ctx1)  # len('hello') * 2 = 10
        result2 = multiplier_cell(ctx2)  # len('hi') * 2 = 4
        result3 = multiplier_cell(ctx3)  # len('default') * 2 = 14

        assert result1 == 10
        assert result2 == 4
        assert result3 == 14


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_context(self):
        """Test behavior with empty context."""
        simple_cell = cell(lambda ctx: "value")

        ctx = {}
        result = simple_cell(ctx)

        assert result == "value"
        assert len(ctx) == 1

    def test_context_mutation(self):
        """Test that be objects can read from context mutations."""
        reader_cell = cell(lambda ctx: ctx.get("dynamic_value", "not_found"))

        ctx = {}

        # First call - value not in context
        result1 = reader_cell(ctx)
        assert result1 == "not_found"

        # Add value to context
        ctx["dynamic_value"] = "found"

        # Create new be that reads the same key
        reader_cell2 = cell(lambda ctx: ctx.get("dynamic_value", "not_found"))
        result2 = reader_cell2(ctx)
        assert result2 == "found"

        # Original reader_cell should still return cached value
        result3 = reader_cell(ctx)
        assert result3 == "not_found"  # Cached result

    def test_none_values(self):
        """Test handling of None values."""
        none_cell = cell(lambda ctx: None)

        ctx = {}
        result = none_cell(ctx)

        assert result is None
        assert none_cell.is_in(ctx)
        assert none_cell.get(ctx) is None

    def test_exception_in_callable(self):
        """Test behavior when callable raises an exception."""
        error_cell = cell(lambda ctx: 1 / 0)  # Division by zero

        ctx = {}

        with pytest.raises(ZeroDivisionError):
            error_cell(ctx)

        # Should not be cached after exception
        assert not error_cell.is_in(ctx)
