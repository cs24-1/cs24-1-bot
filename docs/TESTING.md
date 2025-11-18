# Testing

The project includes a comprehensive pytest-based test suite to ensure code quality and prevent regressions.

## Running Tests

### Basic Commands

Run all tests:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov
```

## Test Structure

Tests are organized to mirror the project structure:

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_main.py             # Main bot tests
├── cogs/                    # Cog tests
│   ├── test_aiService.py
│   ├── test_memeService.py
│   └── ...
├── models/                  # Model tests
│   └── mensa/
│       ├── test_mensaModels.py
│       └── ...
└── utils/                   # Utility tests
    ├── test_constants.py
    ├── test_mensaUtils.py
    └── ...
```

## Writing Tests

### Test Naming

- Test files: `test_*.py` or `*_test.py`
- Test functions: `test_*`
- Test classes: `Test*`

### Fixtures

Common fixtures are defined in `conftest.py`:

```python
import pytest

@pytest.fixture
def mock_bot():
    """Provide a mock Discord bot instance."""
    # Mock implementation
    return mock_bot_instance
```

## Coverage

### Generating Coverage Reports

Generate terminal coverage report:
```bash
pytest --cov --cov-report=term-missing
```

## Continuous Integration

Tests run automatically on GitHub Actions on:
- Pushes to `main` branch
- Pull requests

See `.github/workflows/test.yml` for the CI configuration.

### CI Workflow

The test workflow:
1. Uses pre-built CI Docker image (`ghcr.io/cs24-1/cs24-1-bot-ci:latest`)
2. Runs pytest with coverage
3. Generates JUnit XML report
4. Posts coverage report as PR comment (only for changed files)

See [WORKFLOW_DEPENDENCIES.md](WORKFLOW_DEPENDENCIES.md) for more details on CI workflows.

## Linting

### Used Tools

- **YAPF**: Code formatting
- **isort**: Import sorting
- **mypy**: Type checking

They are available in Visual Studio Code when using the Development Container.

## Best Practices

1. **Write tests first** (TDD approach) or alongside new features
2. **Keep tests isolated** - each test should be independent
3. **Use descriptive names** - test name should describe what is being tested
4. **Mock external dependencies** - don't rely on Discord API, databases, etc.
5. **Test edge cases** - empty inputs, None values, boundary conditions
6. **Keep tests fast** - use fixtures and mocks to avoid slow operations
7. **Document complex tests** - add docstrings explaining non-obvious test logic

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/) - For testing async code
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html) - For mocking
