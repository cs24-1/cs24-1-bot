"""
Unit tests for cogs/quoteService.py
"""

from unittest.mock import MagicMock


class TestQuoteService:
    """Tests for QuoteService Cog"""

    def test_quote_service_initialization(
        self,
        mock_bot: MagicMock,
        mock_logger: MagicMock
    ):
        """Test that QuoteService initializes correctly."""
        from cogs.quoteService import QuoteService

        service = QuoteService(mock_bot, mock_logger)

        assert service.bot == mock_bot
        assert service.logger == mock_logger
        assert hasattr(service, "quote_cache")

    def test_quote_cache_stores_messages(
        self,
        mock_bot: MagicMock,
        mock_logger: MagicMock
    ):
        """Test that quote_cache can store and retrieve messages."""
        from cogs.quoteService import QuoteService

        service = QuoteService(mock_bot, mock_logger)

        # Add messages to cache
        user_id = 12345
        mock_messages = [MagicMock(), MagicMock()]
        service.quote_cache[user_id] = mock_messages  # type: ignore

        # Verify retrieval
        assert user_id in service.quote_cache
        assert service.quote_cache[user_id] == mock_messages

    def test_quote_cache_can_be_cleared(
        self,
        mock_bot: MagicMock,
        mock_logger: MagicMock
    ):
        """Test that quote_cache entries can be removed."""
        from cogs.quoteService import QuoteService

        service = QuoteService(mock_bot, mock_logger)

        # Add and then remove
        user_id = 12345
        service.quote_cache[user_id] = [MagicMock()]
        service.quote_cache.pop(user_id, None)

        # Verify removal
        assert user_id not in service.quote_cache
