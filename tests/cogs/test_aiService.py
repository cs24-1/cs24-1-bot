"""
Unit tests for cogs/aiService.py
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestAIService:
    """Tests for AIService Cog"""

    def test_ai_service_initialization(
        self,
        mock_bot: MagicMock,
        mock_logger: MagicMock
    ):
        """Test that AIService initializes correctly."""
        from cogs.aiService import AIService

        with patch("cogs.aiService.ai.AIUtils"):
            service = AIService(mock_bot, mock_logger)

            assert service.bot == mock_bot
            assert service.logger == mock_logger
            assert hasattr(service, "ai")

    @pytest.mark.asyncio
    async def test_reset_ai_usage_resets_all_users(
        self,
        mock_bot: MagicMock,
        mock_logger: MagicMock
    ):
        """Test that reset_ai_usage task resets usage for all users."""
        from cogs.aiService import AIService

        with patch("cogs.aiService.ai.AIUtils"), \
             patch("cogs.aiService.User") as mock_user_class:

            # Setup mock users
            mock_user1 = AsyncMock()
            mock_user1.fetch_related = AsyncMock()
            mock_user1.ai_metadata = AsyncMock()
            mock_user1.ai_metadata.reset_usage = AsyncMock()

            mock_user2 = AsyncMock()
            mock_user2.fetch_related = AsyncMock()
            mock_user2.ai_metadata = AsyncMock()
            mock_user2.ai_metadata.reset_usage = AsyncMock()

            mock_user_class.all = AsyncMock(
                return_value=[mock_user1,
                              mock_user2]
            )

            service = AIService(mock_bot, mock_logger)

            # Execute reset task
            await service.reset_ai_usage()

            # Verify all users were reset
            mock_user1.ai_metadata.reset_usage.assert_called_once()
            mock_user2.ai_metadata.reset_usage.assert_called_once()

            # Verify logging
            assert mock_logger.info.called
