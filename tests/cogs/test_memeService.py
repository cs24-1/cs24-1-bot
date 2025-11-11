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
