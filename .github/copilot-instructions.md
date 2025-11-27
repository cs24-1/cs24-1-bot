# GitHub Copilot Instructions for cs24-1-bot

This repository contains a Discord bot for the CS24-1 seminar group. Follow these instructions when contributing code or suggesting changes.

## Documentation

For detailed information, refer to the following documentation files:

- **[Code Structure](../docs/CODE_STRUCTURE.md)** - Code organization, style conventions, naming patterns, and common code patterns
- **[Development Setup](../docs/DEVELOPMENT.md)** - Local setup, development tools, and getting started
- **[Database](../docs/DATABASE.md)** - Database models, migrations, and best practices
- **[Testing](../docs/TESTING.md)** - Running tests, coverage, linting, and CI
- **[Docker Images](../docs/DOCKER_IMAGES.md)** - Multi-layer Docker strategy
- **[Workflow Dependencies](../docs/WORKFLOW_DEPENDENCIES.md)** - GitHub Actions workflows

## Quick Reference

### Language and Communication

- All documentation, comments, and commit messages should be in **English**
- Exception: The README.md is in German as this is a German seminar group project
- User-facing messages and bot commands use German language
- Technical code elements (variable names, function names) follow English conventions
- **Discord commands**: User-facing parts (command `description`, option descriptions, response messages) in **German**, internal documentation (function docstrings, code comments) in **English**

### Project Overview

This is a Discord bot built with:
- **py-cord** (discord.py fork) for Discord integration
- **Tortoise ORM** with SQLite for database management
- **OpenAI API** for code translation features
- **PIL** and **EasyOCR** for meme processing

#### Key Features
1. **AI Service**: Code translation using OpenAI API with daily usage limits
2. **Meme Service**: Automatic meme collection and bot banner rotation
3. **Mensa Service**: Daily cafeteria menu updates
4. **Quote Service**: Zitatsammlung und -Verwaltung

### Code Style Essentials

- **Line length**: Maximum 80 characters
- **Indentation**: 4 spaces (no tabs)
- **Naming**: PascalCase for classes, snake_case for functions, UPPER_CASE for constants
- **Type hints**: Required for all function signatures
- **Docstrings**: Required for classes and non-trivial functions
- **Long type annotations**: Split into two lines if exceeding 80 characters:
  ```python
  very_long_variable_name: dict[str, list[tuple[int, str]]]
  very_long_variable_name = {"key": [(1, "value")]}
  ```

See [Code Structure](../docs/CODE_STRUCTURE.md) for complete style guidelines.

### Development Tools

- **YAPF**: Code formatting (80 char limit, PEP 8 based)
- **isort**: Import sorting
- **mypy**: Type checking
- **radon**: Code complexity analysis
- **pytest**: Testing framework

### Before Committing

1. ✅ Code follows YAPF formatting (80 char limit)
2. ✅ Type hints checked with mypy
3. ✅ Bot functionality tested in development environment
4. ✅ Database migrations verified if models changed
5. ✅ Code complexity checked with radon for significant changes
6. ✅ Tests pass (run with `pytest`)
7. ✅ No sensitive data (tokens, credentials) in code

### Security Considerations

- **Never commit** tokens, secrets, or credentials
- Store sensitive data in environment variables
- Validate user input in commands
- Implement rate limiting for API calls (e.g., AI service daily limits)
- Use Discord permissions appropriately (e.g., `@commands.has_permissions()`)

## Additional Notes

- Bot prefix: `$` (for text commands, though slash commands are preferred)
- Intents: Bot uses `discord.Intents.all()`
- Timezone: Uses system timezone (`Constants.SYSTIMEZONE`)
- Guild-specific: Commands restricted to specific guild via `Constants.SERVER_IDS.CUR_SERVER`
