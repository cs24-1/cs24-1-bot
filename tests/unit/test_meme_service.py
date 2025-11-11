"""
Unit tests for cogs/memeService.py
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestMemeService:
    """Tests for MemeService Cog"""

    def test_meme_service_initialization(self, mock_bot, mock_logger):
        """Test that MemeService initializes correctly."""
        from cogs.memeService import MemeService

        service = MemeService(mock_bot, mock_logger)

        assert service.bot == mock_bot
        assert service.logger == mock_logger

    def test_meme_service_has_save_memes_listener(self, mock_bot, mock_logger):
        """Test that MemeService has the save_memes listener."""
        from cogs.memeService import MemeService

        service = MemeService(mock_bot, mock_logger)

        # Check that save_memes method exists
        assert hasattr(service, "save_memes")
        assert callable(service.save_memes)

    def test_meme_service_has_banner_task(self, mock_bot, mock_logger):
        """Test that MemeService has the set_random_meme_banner task."""
        from cogs.memeService import MemeService

        service = MemeService(mock_bot, mock_logger)

        # Check that task exists
        assert hasattr(service, "set_random_meme_banner")

    def test_meme_service_has_meme_command(self, mock_bot, mock_logger):
        """Test that MemeService has the meme command."""
        from cogs.memeService import MemeService

        service = MemeService(mock_bot, mock_logger)

        # Check that meme method exists
        assert hasattr(service, "meme")
        assert callable(service.meme)
