"""
Unit tests for cogs/mensaService.py
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestMensaService:
    """Tests for MensaService Cog"""

    def test_mensa_service_initialization(self, mock_bot, mock_logger):
        """Test that MensaService initializes correctly."""
        from cogs.mensaService import MensaService

        service = MensaService(mock_bot, mock_logger)

        assert service.bot == mock_bot
        assert service.logger == mock_logger
