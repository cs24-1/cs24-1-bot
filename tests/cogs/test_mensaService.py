"""
Unit tests for cogs/mensaService.py
"""

from unittest.mock import MagicMock


class TestMensaService:
    """Tests for MensaService Cog"""

    def test_mensa_service_initialization(
        self,
        mock_bot: MagicMock,
        mock_logger: MagicMock
    ):
        """Test that MensaService initializes correctly."""
        from cogs.mensaService import MensaService

        service = MensaService(mock_bot, mock_logger)

        assert service.bot == mock_bot
        assert service.logger == mock_logger
