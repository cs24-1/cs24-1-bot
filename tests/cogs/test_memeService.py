"""
Unit tests for cogs/memeService.py
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestMemeService:
    """Tests for MemeService Cog"""

    def test_meme_service_initialization(
        self,
        mock_bot: MagicMock,
        mock_logger: MagicMock
    ):
        """Test that MemeService initializes correctly."""
        from cogs.memeService import MemeService

        service = MemeService(mock_bot, mock_logger)

        assert service.bot == mock_bot
        assert service.logger == mock_logger

    @pytest.mark.asyncio
    async def test_save_memes_ignores_bot_messages(
        self,
        mock_bot: MagicMock,
        mock_logger: MagicMock
    ):
        """Test that save_memes ignores messages from bots."""
        from cogs.memeService import MemeService

        service = MemeService(mock_bot, mock_logger)

        # Create mock message from a bot
        mock_message = MagicMock()
        mock_message.author.bot = True

        # Execute listener
        await service.save_memes(mock_message)

        # Verify no processing occurred (logger not called)
        assert not mock_logger.info.called

    @pytest.mark.asyncio
    async def test_save_memes_ignores_non_meme_channel(
        self,
        mock_bot: MagicMock,
        mock_logger: MagicMock
    ):
        """Test that save_memes ignores messages from other channels."""
        from cogs.memeService import MemeService
        from utils.constants import Constants

        service = MemeService(mock_bot, mock_logger)

        # Create mock message from wrong channel
        mock_message = MagicMock()
        mock_message.author.bot = False
        mock_message.channel.id = Constants.CHANNEL_IDS.MEME_CHANNEL + 1

        # Execute listener
        await service.save_memes(mock_message)

        # Verify no processing occurred
        assert not mock_logger.info.called

    @pytest.mark.asyncio
    async def test_save_memes_processes_valid_image(
        self,
        mock_bot: MagicMock,
        mock_logger: MagicMock
    ):
        """Test that save_memes processes valid image attachments."""
        from cogs.memeService import MemeService
        from utils.constants import Constants

        with patch("cogs.memeService.User") as mock_user_class, \
             patch("cogs.memeService.memeUtils") as mock_meme_utils:

            service = MemeService(mock_bot, mock_logger)

            # Create mock user
            mock_user = AsyncMock()
            mock_user_class.get_or_create = AsyncMock(
                return_value=(mock_user,
                              False)
            )

            # Create mock message with image attachment
            mock_attachment = MagicMock()
            mock_attachment.content_type = "image/png"
            mock_attachment.filename = "test.png"

            mock_message = MagicMock()
            mock_message.author.bot = False
            mock_message.channel.id = Constants.CHANNEL_IDS.MEME_CHANNEL
            mock_message.attachments = [mock_attachment]
            mock_message.content = "Test meme"

            mock_meme_utils.save_meme_image = AsyncMock()

            # Execute listener
            await service.save_memes(mock_message)

            # Verify meme was saved
            mock_meme_utils.save_meme_image.assert_called_once()

            # Verify logging occurred
            assert mock_logger.info.called
