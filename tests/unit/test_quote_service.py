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

    def test_quote_service_has_quote_command_group(self, mock_bot, mock_logger):
        """Test that QuoteService has the quote command group."""
        from cogs.quoteService import QuoteService

        service = QuoteService(mock_bot, mock_logger)

        # Check that quote command group exists
        assert hasattr(service, "quote")

    def test_quote_service_has_create_quote_command(
        self,
        mock_bot,
        mock_logger
    ):
        """Test that QuoteService has the create_quote command."""
        from cogs.quoteService import QuoteService

        service = QuoteService(mock_bot, mock_logger)

        # Check that create_quote method exists
        assert hasattr(service, "create_quote")
        assert callable(service.create_quote)

    def test_quote_service_has_search_quote_command(
        self,
        mock_bot,
        mock_logger
    ):
        """Test that QuoteService has the search_quote command."""
        from cogs.quoteService import QuoteService

        service = QuoteService(mock_bot, mock_logger)

        # Check that search_quote method exists
        assert hasattr(service, "search_quote")
        assert callable(service.search_quote)
