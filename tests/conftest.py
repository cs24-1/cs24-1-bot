"""
Shared pytest fixtures and configuration for cs24-1-bot tests.
"""

from unittest.mock import AsyncMock, MagicMock

import discord
import pytest


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """
    Set up test environment variables.
    This fixture is automatically used by all tests.
    """
    monkeypatch.setenv("DISCORD_TOKEN", "test_token")
    monkeypatch.setenv("CUR_SERVER", "123456")

    monkeypatch.setenv("MENSA_CHANNEL", "123456")
    monkeypatch.setenv("MEME_CHANNEL", "123456")
    monkeypatch.setenv("QUOTE_CHANNEL", "123456")
    monkeypatch.setenv("TIMETABLE_CHANNEL", "123456")

    monkeypatch.setenv("OPENAI_TOKEN", "test_token")
    monkeypatch.setenv("CAMPUS_USER", "test_user")
    monkeypatch.setenv("CAMPUS_HASH", "test_hash")


@pytest.fixture
def mock_bot():
    """
    Fixture that provides a mocked Discord Bot instance.
    """
    bot = MagicMock(spec=discord.Bot)
    bot.user = MagicMock()
    bot.user.id = 123456789
    bot.user.name = "TestBot"
    return bot


@pytest.fixture
def mock_logger():
    """
    Fixture that provides a mocked logger instance.
    """
    logger = MagicMock()
    return logger


@pytest.fixture
def mock_context():
    """
    Fixture that provides a mocked Discord ApplicationContext.
    """
    ctx = AsyncMock(spec=discord.ApplicationContext)
    ctx.respond = AsyncMock()
    ctx.send = AsyncMock()
    ctx.author = MagicMock()
    ctx.author.id = 987654321
    ctx.author.name = "TestUser"
    return ctx
