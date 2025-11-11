"""
Unit tests for cogs/aiService.py
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestAIService:
    """Tests for AIService Cog"""

    def test_ai_service_initialization(self, mock_bot, mock_logger):
        """Test that AIService initializes correctly."""
        from cogs.aiService import AIService

        with patch("cogs.aiService.ai.AIUtils"):
            service = AIService(mock_bot, mock_logger)

            assert service.bot == mock_bot
            assert service.logger == mock_logger
            assert hasattr(service, "ai")

    def test_ai_service_has_translate_command(self, mock_bot, mock_logger):
        """Test that AIService has the translate command."""
        from cogs.aiService import AIService

        with patch("cogs.aiService.ai.AIUtils"):
            service = AIService(mock_bot, mock_logger)

            # Check that translate method exists
            assert hasattr(service, "translate")
            assert callable(service.translate)

    def test_ai_service_has_reset_usage_task(self, mock_bot, mock_logger):
        """Test that AIService has the reset usage task."""
        from cogs.aiService import AIService

        with patch("cogs.aiService.ai.AIUtils"):
            service = AIService(mock_bot, mock_logger)

            # Check that reset_ai_usage method exists
            assert hasattr(service, "reset_ai_usage")
