"""
Example smoke tests to verify basic imports and project structure.
"""

import os

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


def test_imports_main():
    """
    Test that main module can be imported.
    """
    import main

    assert main is not None


def test_imports_constants():
    """
    Test that constants module can be imported.
    """
    from utils import constants

    assert constants is not None
    assert hasattr(constants, "Constants")


def test_imports_models():
    """
    Test that database models can be imported.
    """
    from models.database import baseModel

    assert baseModel is not None
    assert hasattr(baseModel, "BaseModel")


def test_python_version():
    """
    Test that Python version is 3.10 or higher.
    """
    import sys

    assert sys.version_info >= (3, 10)
