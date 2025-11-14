"""
Unit tests for utils/quoteUtils.py
"""

from unittest.mock import MagicMock

from discord import Color, Embed


class TestBuildQuoteEmbed:
    """Tests for build_quote_embed function"""

    def test_build_quote_embed_single_message(self):
        """Test building an embed with a single message."""
        from utils.quoteUtils import build_quote_embed

        # Create mock message
        mock_message = MagicMock()
        mock_message.content = "Test message content"
        mock_message.author.display_name = "TestUser"
        mock_message.jump_url = "https://discord.com/channels/123/456/789"

        embed = build_quote_embed([mock_message])

        assert isinstance(embed, Embed)
        assert embed.color == Color.blurple()
        assert len(embed.fields) == 1
        assert "TestUser" in embed.fields[0].name
        assert "Test message content" in embed.fields[0].value
        assert embed.fields[0].inline is False

    def test_build_quote_embed_multiple_messages(self):
        """Test building an embed with multiple messages."""
        from utils.quoteUtils import build_quote_embed

        # Create mock messages
        mock_message1 = MagicMock()
        mock_message1.content = "First message"
        mock_message1.author.display_name = "User1"
        mock_message1.jump_url = "https://discord.com/channels/123/456/789"

        mock_message2 = MagicMock()
        mock_message2.content = "Second message"
        mock_message2.author.display_name = "User2"
        mock_message2.jump_url = "https://discord.com/channels/123/456/790"

        embed = build_quote_embed([mock_message1, mock_message2])

        assert len(embed.fields) == 2
        assert "User1" in embed.fields[0].name
        assert "User2" in embed.fields[1].name

    def test_build_quote_embed_empty_message_content(self):
        """Test that empty messages get placeholder text."""
        from utils.quoteUtils import build_quote_embed

        mock_message = MagicMock()
        mock_message.content = ""
        mock_message.author.display_name = "TestUser"
        mock_message.jump_url = "https://discord.com/channels/123/456/789"

        embed = build_quote_embed([mock_message])

        assert "[- kein Text -]" in embed.fields[0].value

    def test_build_quote_embed_with_author_name(self):
        """Test that author name appears in footer."""
        from utils.quoteUtils import build_quote_embed

        mock_message = MagicMock()
        mock_message.content = "Test"
        mock_message.author.display_name = "TestUser"
        mock_message.jump_url = "https://discord.com/channels/123/456/789"

        embed = build_quote_embed([mock_message], author_name="Submitter")

        assert embed.footer is not None
        assert embed.footer.text == "Eingereicht von Submitter"

    def test_build_quote_embed_long_content_truncation(self):
        """Test that messages longer than 1024 chars are truncated."""
        from utils.quoteUtils import build_quote_embed

        mock_message = MagicMock()
        mock_message.content = "A" * 2000  # Very long message
        mock_message.author.display_name = "TestUser"
        mock_message.jump_url = "https://discord.com/channels/123/456/789"

        embed = build_quote_embed([mock_message])

        # Field value should be truncated to 1024 + quote marks + jump URL
        field_content = embed.fields[0].value
        # Extract just the quoted part (before the jump URL line)
        quoted_part = field_content.split("\n[Originalnachricht]")[0]
        # Remove the quote marks
        quoted_text = quoted_part.strip('"')
        # Verify the message content is truncated to 1024 chars
        assert len(quoted_text) == 1024
