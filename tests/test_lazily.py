import pytest

from lazily import Be, be


class TestBe:
    """Test the base Be class functionality."""

    def test_be_abstract_nature(self):
        """Test that Be cannot be instantiated directly without callable."""
        with pytest.raises(AttributeError):
            be_instance = Be()
            be_instance({})

    def test_be_with_manual_callable(self):
        """Test Be with manually assigned callable."""
        be_instance = Be()
        be_instance.callable = lambda ctx: "test value"

        ctx = {}
        result = be_instance(ctx)

        assert result == "test value"
        assert be_instance in ctx
        assert ctx[be_instance] == "test value"

    def test_be_get_method(self):
        """Test the get method."""
        be_instance = Be()
        be_instance.callable = lambda ctx: "test value"

        ctx = {}

        # Should return None when not in context
        assert be_instance.get(ctx) is None

        # Should return value after calling
        be_instance(ctx)
        assert be_instance.get(ctx) == "test value"

    def test_be_is_in_method(self):
        """Test the is_in method."""
        be_instance = Be()
        be_instance.callable = lambda ctx: "test value"

        ctx = {}

        # Should not be in context initially
        assert not be_instance.is_in(ctx)

        # Should be in context after calling
        be_instance(ctx)
        assert be_instance.is_in(ctx)


class TestBeClass:
    """Test the be class functionality."""

    def test_simple_be(self):
        """Test basic be functionality."""
        hello = be(lambda ctx: "Hello")

        ctx = {}
        result_hello = hello(ctx)

        assert result_hello == "Hello"
        assert hello in ctx
        assert ctx[hello] == "Hello"

        @be
        def world(ctx: dict) -> str:
            return "World"

        result_world = world(ctx)
        assert result_world == "World"
        assert world in ctx
        assert ctx[world] == "World"

    def test_be_caching(self):
        """Test that be caches results."""
        call_count = 0

        @be
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

    def test_be_dependency_chain(self):
        """Test be objects depending on other be objects."""

        first = be(lambda ctx: "Hello")
        second = be(lambda ctx: "World")
        combined = be(lambda ctx: f"{first(ctx)} {second (ctx)}!")

        ctx = {}
        result = combined (ctx)

        assert result == "Hello World!"
        assert first in ctx
        assert second  in ctx
        assert combined  in ctx

    def test_multiple_contexts(self):
        """Test that different contexts are independent."""
        value = be(lambda ctx: len(ctx))

        ctx1 = {}
        ctx2 = {"existing": "value"}

        result1 = value(ctx1)
        result2 = value(ctx2)

        assert result1 == 0
        assert result2 == 1

    def test_be_with_complex_types(self):
        """Test be with complex return types."""
        be_dict = be(lambda ctx: {"key": "value", "number": 42})
        be_list = be(lambda ctx: [1, 2, 3])

        ctx = {}

        dict_result = be_dict(ctx)
        list_result = be_list(ctx)

        assert dict_result == {"key": "value", "number": 42}
        assert list_result == [1, 2, 3]


class TestIntegration:
    """Integration tests combining different be types."""

    def test_complex_dependency_graph(self):
        """Test a complex dependency graph."""
        @be
        def config(ctx: dict) -> dict:
            return {"api_url": "https://api.example.com", "timeout": 30}

        class HttpClient(Be[str]):
            def callable(self, ctx: dict) -> str:
                _config = config(ctx)
                return f"HttpClient({_config['api_url']}, timeout={_config['timeout']})"

        http_client = HttpClient()

        be_user_service = be(lambda ctx: f"UserService({http_client(ctx)})")
        be_auth_service = be(lambda ctx: f"AuthService({http_client(ctx)})")

        @be
        def app(ctx: dict) -> str:
            return f"App(user={be_user_service(ctx)}, auth={be_auth_service(ctx)})"

        ctx = {}
        result = app(ctx)

        expected = "App(user=UserService(HttpClient(https://api.example.com, timeout=30)), auth=AuthService(HttpClient(https://api.example.com, timeout=30)))"
        assert result == expected

    def test_context_isolation(self):
        """Test that different contexts don't interfere with each other."""
        @be
        def be_value(ctx: dict) -> str:
            return ctx.get("input", "default")

        @be
        def be_multiplier(ctx: dict) -> int:
            base = be_value(ctx)
            return len(base) * 2

        ctx1 = {"input": "hello"}
        ctx2 = {"input": "hi"}
        ctx3 = {}

        result1 = be_multiplier(ctx1)  # len('hello') * 2 = 10
        result2 = be_multiplier(ctx2)  # len('hi') * 2 = 4
        result3 = be_multiplier(ctx3)  # len('default') * 2 = 14

        assert result1 == 10
        assert result2 == 4
        assert result3 == 14


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_context(self):
        """Test behavior with empty context."""
        be_simple = be(lambda ctx: "value")

        ctx = {}
        result = be_simple(ctx)

        assert result == "value"
        assert len(ctx) == 1

    def test_context_mutation(self):
        """Test that be objects can read from context mutations."""
        be_reader = be(lambda ctx: ctx.get("dynamic_value", "not_found"))

        ctx = {}

        # First call - value not in context
        result1 = be_reader(ctx)
        assert result1 == "not_found"

        # Add value to context
        ctx["dynamic_value"] = "found"

        # Create new be that reads the same key
        be_reader2 = be(lambda ctx: ctx.get("dynamic_value", "not_found"))
        result2 = be_reader2(ctx)
        assert result2 == "found"

        # Original be_reader should still return cached value
        result3 = be_reader(ctx)
        assert result3 == "not_found"  # Cached result

    def test_none_values(self):
        """Test handling of None values."""
        be_none = be(lambda ctx: None)

        ctx = {}
        result = be_none(ctx)

        assert result is None
        assert be_none.is_in(ctx)
        assert be_none.get(ctx) is None

    def test_exception_in_callable(self):
        """Test behavior when callable raises an exception."""
        be_error = be(lambda ctx: 1 / 0)  # Division by zero

        ctx = {}

        with pytest.raises(ZeroDivisionError):
            be_error(ctx)

        # Should not be cached after exception
        assert not be_error.is_in(ctx)
