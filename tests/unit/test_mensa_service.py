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

    def test_mensa_service_has_get_mensa_plan_command(
        self,
        mock_bot,
        mock_logger
    ):
        """Test that MensaService has the get_mensa_plan command."""
        from cogs.mensaService import MensaService

        service = MensaService(mock_bot, mock_logger)

        # Check that get_mensa_plan method exists
        assert hasattr(service, "get_mensa_plan")
        assert callable(service.get_mensa_plan)

    def test_mensa_service_has_daily_message_task(self, mock_bot, mock_logger):
        """Test that MensaService has the send daily message task."""
        from cogs.mensaService import MensaService

        service = MensaService(mock_bot, mock_logger)

        # Check that task exists
        assert hasattr(service, "send_daily_mensa_message")
