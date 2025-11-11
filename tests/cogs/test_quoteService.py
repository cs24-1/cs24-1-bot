"""
Unit tests for cogs/quoteService.py
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestQuoteService:
    """Tests for QuoteService Cog"""

    def test_quote_service_initialization(self, mock_bot, mock_logger):
        """Test that QuoteService initializes correctly."""
        from cogs.quoteService import QuoteService

        service = QuoteService(mock_bot, mock_logger)

        assert service.bot == mock_bot
        assert service.logger == mock_logger
