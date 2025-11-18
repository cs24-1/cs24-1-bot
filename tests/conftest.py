"""
Shared pytest fixtures and configuration for cs24-1-bot tests.
"""

import os
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import discord
import pytest


def pytest_configure(config: Any) -> None:
    """
    Configure pytest before any tests run.
    This sets up environment variables before any modules are imported.
    """
    os.environ["DISCORD_TOKEN"] = "test_token"
    os.environ["CUR_SERVER"] = "123456"

    os.environ["MENSA_CHANNEL"] = "123456"
    os.environ["MEME_CHANNEL"] = "123456"
    os.environ["QUOTE_CHANNEL"] = "123456"
    os.environ["TIMETABLE_CHANNEL"] = "123456"

    os.environ["OPENAI_TOKEN"] = "test_token"
    os.environ["CAMPUS_USER"] = "test_user"
    os.environ["CAMPUS_HASH"] = "test_hash"


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
