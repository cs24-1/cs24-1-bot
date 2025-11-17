---
applyTo: "**/tests/**/*.py"
---

## Testing Requirements

When writing or modifying tests for this project:

1. **Use pytest** - All tests use the pytest framework
2. **Follow naming conventions** - Test files: `test_*.py`, Test functions: `test_*`
3. **Use fixtures** - Leverage pytest fixtures for setup/teardown (defined in `conftest.py`)
4. **Mock Discord objects** - Use `discord.ext.test` or manual mocks for Discord interactions
5. **Test database operations** - Use the test database fixture, ensure proper cleanup
6. **Async tests** - Use `@pytest.mark.asyncio` for async test functions
7. **Coverage targets** - Aim for >80% coverage on new code
8. **Assertions** - Use clear, specific assertions with helpful failure messages
9. **Test isolation** - Each test should be independent and not rely on test execution order
10. **German error messages** - When testing user-facing responses, verify German text
11. **Type hints** - Include type hints in test functions for clarity
12. **Docstrings** - Add docstrings to complex test functions explaining what they test
