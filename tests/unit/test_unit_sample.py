"""
Sample unit tests demonstrating test patterns for the bot.
"""

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """
    Set up test environment variables.
    """
    monkeypatch.setenv("DISCORD_TOKEN", "test_token")
    monkeypatch.setenv("OPENAI_TOKEN", "test_token")
    monkeypatch.setenv("MENSA_CHANNEL", "123456")
    monkeypatch.setenv("MEME_CHANNEL", "123456")
    monkeypatch.setenv("QUOTE_CHANNEL", "123456")
    monkeypatch.setenv("CUR_SERVER", "123456")


def test_get_extensions():
    """
    Test that get_extensions function finds cog files.
    """
    from main import get_extensions

    extensions = list(get_extensions())
    assert len(extensions) > 0
    assert all(ext.startswith("cogs.") for ext in extensions)
    assert all(ext.endswith("Service") for ext in extensions)


def test_constants_structure():
    """
    Test that Constants class has expected attributes.
    """
    from utils.constants import Constants

    # Test that expected constant classes exist
    assert hasattr(Constants, "SECRETS")
    assert hasattr(Constants, "CHANNEL_IDS")
    assert hasattr(Constants, "SERVER_IDS")
    assert hasattr(Constants, "REACTIONS")
    assert hasattr(Constants, "FILE_PATHS")
    assert hasattr(Constants, "MENSA")


def test_file_paths_structure():
    """
    Test that file path constants are properly defined.
    """
    from utils.constants import Constants

    assert hasattr(Constants.FILE_PATHS, "RAW_MEME_FOLDER")
    assert hasattr(Constants.FILE_PATHS, "BANNERIZED_MEME_FOLDER")
    assert hasattr(Constants.FILE_PATHS, "OCR_DATA_FOLDER")
    assert hasattr(Constants.FILE_PATHS, "DB_FILE")


def test_reactions_constants():
    """
    Test that reaction constants are defined.
    """
    from utils.constants import Constants

    assert Constants.REACTIONS.CHECK == "✅"
    assert Constants.REACTIONS.CROSS == "❌"
