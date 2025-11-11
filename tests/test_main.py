"""
Tests for main.py utility functions.
"""

import os
from pathlib import Path

import pytest


def test_get_extensions_finds_cogs():
    """
    Test that get_extensions finds all cog files in the cogs directory.
    """
    from main import get_extensions

    extensions = list(get_extensions())

    # Should find at least the existing cogs
    assert len(extensions) > 0

    # All extensions should start with "cogs."
    assert all(ext.startswith("cogs.") for ext in extensions)

    # Should include the known services
    extension_names = [ext.split(".")[-1] for ext in extensions]
    assert "aiService" in extension_names
    assert "memeService" in extension_names
    assert "mensaService" in extension_names
    assert "quoteService" in extension_names


def test_get_extensions_format():
    """
    Test that get_extensions returns correctly formatted module paths.
    """
    from main import get_extensions

    extensions = list(get_extensions())

    for ext in extensions:
        # Should use dots, not slashes
        assert "/" not in ext

        # Should not have .py extension
        assert not ext.endswith(".py")

        # Should be importable format
        assert ext.count(".") >= 1


def test_python_version_requirement():
    """
    Test that Python version is 3.10 or higher as required by the bot.
    """
    import sys

    assert sys.version_info >= (3, 10), "Bot requires Python 3.10 or higher"
