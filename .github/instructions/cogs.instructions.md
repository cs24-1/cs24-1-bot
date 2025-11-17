---
applyTo: "**/cogs/**/*.py"
---

## Discord Cog Requirements

When creating or modifying Discord Cogs:

1. **Guild restriction** - All slash commands must include `guild_ids=[Constants.SERVER_IDS.CUR_SERVER]`
2. **German descriptions** - Command descriptions and user-facing messages in German
3. **Logging** - Use `self.logger` for all logging, include context in messages
4. **Error handling** - Catch exceptions and provide user-friendly German error messages
5. **Type hints** - All methods must have complete type hints including return types
6. **Docstrings** - Document what the Cog does and all non-trivial methods
7. **Async/await** - All Discord command handlers and DB operations must use async/await
8. **Resource cleanup** - Implement `cog_unload()` if the Cog uses background tasks
9. **Command options** - Use `@discord.option()` decorator for all command parameters
10. **Response patterns** - Use `await ctx.respond()` for slash command responses
11. **Cog initialization** - Accept `bot: discord.Bot` and `logger: logging.Logger` in `__init__`
12. **Event listeners** - Use `@commands.Cog.listener()` decorator for event handlers
13. **Bot check** - In message handlers, check `if message.author.bot: return` to avoid bot loops
