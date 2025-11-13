# GitHub Copilot Instructions for cs24-1-bot

This repository contains a Discord bot for the CS24-1 seminar group. Follow these instructions when contributing code or suggesting changes.

## Language and Communication

- All documentation, comments, and commit messages should be in **English**
- Exception: The README.md is in German as this is a German seminar group project
- User-facing messages and bot commands use German language
- Technical code elements (variable names, function names) follow English conventions

## Project Overview

This is a Discord bot built with:
- **py-cord** (discord.py fork) for Discord integration
- **Tortoise ORM** with SQLite for database management
- **OpenAI API** for code translation features
- **PIL** and **EasyOCR** for meme processing

### Key Features
1. **AI Service**: Code translation using OpenAI API with daily usage limits
2. **Meme Service**: Automatic meme collection and bot banner rotation
3. **Mensa Service**: Daily cafeteria menu updates

## Code Style and Formatting

### Python Style Guidelines

Follow **PEP 8** conventions with these specific configurations:

#### YAPF Configuration (from `pyproject.toml`)
```
based_on_style = "pep8"
coalesce_brackets = false
column_limit = 80
dedent_closing_brackets = true
each_dict_entry_on_separate_line = true
space_between_ending_comma_and_closing_bracket = false
split_all_comma_separated_values = true
split_arguments_when_comma_terminated = true
split_before_named_assigns = true
```

#### Key Style Rules
- **Line length**: Maximum 80 characters
- **Indentation**: 4 spaces (no tabs)
- **Imports**: Group in order: standard library, third-party, local imports
- **Type hints**: Use type hints where beneficial (see mypy configuration)
- **Docstrings**: Use for classes and non-trivial functions (triple quotes)

### Naming Conventions

- **Classes**: PascalCase (e.g., `AIService`, `MemeService`, `User`)
- **Functions/Methods**: snake_case (e.g., `reset_ai_usage`, `save_meme_image`)
- **Constants**: UPPER_CASE with underscores (e.g., `MAX_TRANSLATE_REQUESTS_PER_DAY`)
- **Private methods**: Prefix with underscore (e.g., `_helper_method`)
- **Type checking imports**: Use `TYPE_CHECKING` guard for circular dependencies

### Code Organization

#### File Structure
```
.
├── cogs/              # Discord command modules (Cogs)
├── models/            # Data models
│   ├── ai/           # AI-related models
│   ├── database/     # Database models (Tortoise ORM)
│   └── mensa/        # Mensa-related models
├── utils/            # Utility functions
│   ├── ai/           # AI utilities
│   └── memeUtils/    # Meme processing utilities
├── migrations/       # Database migrations (aerich)
├── data/             # Runtime data (gitignored)
└── main.py          # Bot entry point
```

#### Module Organization
- Group related functionality into Cogs (Discord.py pattern)
- Place data models in `models/database/` inheriting from `BaseModel`
- Utility functions go in appropriate `utils/` subdirectories
- Constants centralized in `utils/constants.py`

## Discord Bot Patterns

### Cog Structure

All Discord commands should be implemented as Cogs:

```python
class ServiceName(commands.Cog):
    """
    Brief description of the Cog's purpose.
    """

    def __init__(self, bot: discord.Bot, logger: logging.Logger) -> None:
        self.logger = logger
        self.bot = bot
        # Initialize any resources
```

### Command Definitions

Use slash commands with guild restriction:

```python
@commands.slash_command(
    name="command_name",
    description="German description of what the command does",
    guild_ids=[Constants.SERVER_IDS.CUR_SERVER]
)
@discord.option(
    "parameter_name",
    type=discord.SlashCommandOptionType.string,
    required=True
)
async def command_name(self, ctx: ApplicationContext, parameter_name: str):
    # Implementation
```

### Event Listeners

```python
@commands.Cog.listener()
async def on_ready(self):
    """
    Runs when the bot is ready.
    """
    # Initialization logic
    self.logger.info("Service started successfully")

@commands.Cog.listener("on_message")
async def handler_name(self, message: discord.Message):
    """
    Handles incoming messages.
    """
    if message.author.bot:
        return
    # Handler logic
```

## Database (Tortoise ORM)

### Model Definition

All database models should inherit from `BaseModel`:

```python
from models.database.baseModel import BaseModel
from tortoise import fields

class ModelName(BaseModel):
    id = fields.IntField(pk=True, description="Description")
    field_name = fields.CharField(
        max_length=255,
        description="Field description"
    )
```

### Database Operations

- Use `await Model.get_or_create()` for idempotent operations
- Always use `await` for database operations
- Fetch related fields explicitly: `await model.fetch_related("relation_name")`
- Prefer model methods for business logic over raw queries

### Migrations

When modifying database models:
1. Run `aerich migrate --name=descriptive_name` to create migration
2. Run `aerich upgrade` to apply migration

## Constants and Configuration

### Constants Pattern

All constants are centralized in `utils/constants.py`:

```python
class CategoryName:
    CONSTANT_NAME = value

class Constants:
    CATEGORY = CategoryName
```

Access as: `Constants.CATEGORY.CONSTANT_NAME`

### Environment Variables

- Define in `EXAMPLE.env` (template)
- Load in `.env` (gitignored)
- Access via `os.getenv()` in `utils/constants.py`
- Document all required environment variables

## Logging

### Logger Usage

```python
import logging

logger = logging.getLogger('bot')
logger.info("Informational message with %s", variable)
logger.error("Error occurred: %s", error)
logger.warning("Warning message")
```

- Use string formatting with `%s` placeholders (not f-strings in log messages)
- Log important state changes and errors
- Include context in error messages

## Type Checking

### MyPy Configuration
```
check_untyped_defs = true
line_length = 80
```

### Type Hints Best Practices
- Add type hints to function signatures
- Use `TYPE_CHECKING` guard for imports that cause circular dependencies
- Use `# type: ignore` sparingly and only when necessary
- Return types should be explicit for public methods

## Testing and Quality

### Development Requirements
- `radon`: Code complexity analysis

### Before Committing
1. Ensure code follows YAPF formatting (80 char limit)
2. Check type hints with mypy
3. Test bot functionality in development environment
4. Verify database migrations if models changed
5. Use radon to check code complexity if making significant changes

### VS Code Extensions (Auto-configured in Dev Container)
- `ms-python.python`: Python language support
- `ms-python.mypy-type-checker`: Type checking
- `eeyore.yapf`: Code formatting
- `ms-python.isort`: Import sorting
- `ChristianDein.python-radon`: Code complexity analysis
- `njpwerner.autodocstring`: Docstring generation
- `github.vscode-github-actions`: GitHub Actions support

## Dependencies

### Adding New Dependencies

1. Add to appropriate requirements file:
   - `requirements.txt`: Core dependencies
   - `requirements-torch.txt`: PyTorch and related packages
   - `requirements-dev.txt`: Development tools
2. Pin versions with `~=` for compatible updates
3. Update Dockerfile if needed for system dependencies

### Package Management
- Use `pip install -r requirements.txt` for installation
- Document system dependencies (e.g., for EasyOCR)

## Docker and Development Containers

This project uses Dev Containers for consistent development environment:
- Configuration in `.devcontainer/`
- Dockerfile for both development and production
- Automatic database initialization on container start
- VS Code extensions auto-configured: Python, mypy, yapf, isort, radon

### Production Deployment
- Multi-platform Docker images (linux/amd64, linux/arm64)
- Automatic deployment on push to `main` branch
- Deployed to GitHub Container Registry (ghcr.io)
- Timezone: Europe/Berlin

## Common Patterns

### Async/Await
- All Discord.py command handlers are `async`
- All Tortoise ORM operations use `await`
- Use `asyncio` for concurrent operations

### Error Handling
```python
try:
    # Operation
except SpecificException as ex:
    logger.error("Context: %s", ex)
    await ctx.send("User-friendly German error message")
```

### Resource Cleanup
- Use tasks with `.start()` for background jobs
- Clean up resources in Cog `__init__` if needed
- Handle bot shutdown gracefully

## Git Practices

### Commit Messages
- Use descriptive messages in English or German
- Reference issue numbers when applicable

### Ignored Files (`.gitignore`)
- Environment files (`.env`)
- Database files (`*.sqlite3`)
- Python cache (`__pycache__`, `*.pyc`)
- IDE files (`.idea/`, `.vscode/` except shared configs)
- Data directory (`data/`)
- Log files (`*.log`)

## Security Considerations

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
