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
