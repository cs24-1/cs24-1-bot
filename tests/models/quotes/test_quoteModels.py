"""
Unit tests for models/quotes/quoteModels.py
"""

from unittest.mock import MagicMock

from discord import Message

from models.quotes.quoteModels import PartialMessage


class TestPartialMessage:
    """Tests for PartialMessage dataclass and its methods"""

    def test_from_discord_message_with_full_data(self):
        """Test conversion from discord.Message with all attributes."""
        # Create mock Discord message
        mock_message = MagicMock(spec=Message)
        mock_message.content = "Test message content"
        mock_message.jump_url = "https://discord.com/channels/123/456/789"
        mock_message.author = MagicMock()
        mock_message.author.display_name = "TestUser"

        # Convert to PartialMessage
        partial = PartialMessage.from_discord_message(mock_message)

        assert partial.content == "Test message content"
        assert partial.jump_url == "https://discord.com/channels/123/456/789"
        assert partial.author_name == "TestUser"

    def test_from_discord_message_with_empty_content(self):
        """Test conversion with empty content."""
        mock_message = MagicMock(spec=Message)
        mock_message.content = ""
        mock_message.jump_url = "https://discord.com/channels/123/456/789"
        mock_message.author = MagicMock()
        mock_message.author.display_name = "TestUser"

        partial = PartialMessage.from_discord_message(mock_message)

        assert partial.content == ""
        assert partial.jump_url == "https://discord.com/channels/123/456/789"
        assert partial.author_name == "TestUser"

    def test_from_discord_message_without_author(self):
        """Test conversion when message has no author."""
        mock_message = MagicMock(spec=Message)
        mock_message.content = "Test message"
        mock_message.jump_url = "https://discord.com/channels/123/456/789"
        mock_message.author = None

        partial = PartialMessage.from_discord_message(mock_message)

        assert partial.content == "Test message"
        assert partial.jump_url == "https://discord.com/channels/123/456/789"
        assert partial.author_name is None

    def test_from_discord_message_with_long_content(self):
        """Test conversion with very long message content."""
        long_content = "A" * 2000
        mock_message = MagicMock(spec=Message)
        mock_message.content = long_content
        mock_message.jump_url = "https://discord.com/channels/123/456/789"
        mock_message.author = MagicMock()
        mock_message.author.display_name = "TestUser"

        partial = PartialMessage.from_discord_message(mock_message)

        assert partial.content == long_content
        assert partial.content is not None
        assert len(partial.content) == 2000

    def test_from_discord_message_with_none_content(self):
        """Test conversion when message content is None."""
        mock_message = MagicMock(spec=Message)
        mock_message.content = None
        mock_message.jump_url = "https://discord.com/channels/123/456/789"
        mock_message.author = MagicMock()
        mock_message.author.display_name = "TestUser"

        partial = PartialMessage.from_discord_message(mock_message)

        assert partial.content is None
        assert partial.jump_url == "https://discord.com/channels/123/456/789"
        assert partial.author_name == "TestUser"

    def test_from_discord_message_with_special_characters(self):
        """Test conversion with special characters in content."""
        mock_message = MagicMock(spec=Message)
        mock_message.content = "Test 🎉 emoji and **markdown** text"
        mock_message.jump_url = "https://discord.com/channels/123/456/789"
        mock_message.author = MagicMock()
        mock_message.author.display_name = "User🎮"

        partial = PartialMessage.from_discord_message(mock_message)

        assert partial.content == "Test 🎉 emoji and **markdown** text"
        assert partial.author_name == "User🎮"
