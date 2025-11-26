"""
Unit tests for utils/quoteUtils.py
"""

from discord import Color, Embed
from models.quotes.quoteModels import PartialMessage


class TestBuildQuoteEmbed:
    """Tests for build_quote_embed function"""

    def test_build_quote_embed_single_message(self):
        """Test building an embed with a single message."""
        from utils.quoteUtils import build_quote_embed

        # Create mock message
        mock_message = PartialMessage(
            content="Test message content",
            jump_url="https://discord.com/channels/123/456/789",
            author_name="TestUser"
        )

        embed = build_quote_embed([mock_message])

        assert isinstance(embed, Embed)
        assert embed.color == Color.blurple()
        assert embed.title == "💬 Neues Zitat"
        # New format: 2 fields per message (content field + author field)
        assert len(embed.fields) == 2
        # First field has the content
        assert "Test message content" in embed.fields[0].value
        # Second field has the author name
        assert "TestUser" in embed.fields[1].name
        assert embed.fields[0].inline is False
        assert embed.fields[1].inline is False

    def test_build_quote_embed_multiple_messages(self):
        """Test building an embed with multiple messages."""
        from utils.quoteUtils import build_quote_embed

        # Create mock messages
        mock_message1 = PartialMessage(
            content="First message",
            jump_url="https://discord.com/channels/123/456/789",
            author_name="User1"
        )

        mock_message2 = PartialMessage(
            content="Second message",
            jump_url="https://discord.com/channels/123/456/790",
            author_name="User2"
        )

        embed = build_quote_embed([mock_message1, mock_message2])

        # New format: 2 fields per message = 4 fields total
        assert len(embed.fields) == 4
        # First message content in field 0, author in field 1
        assert "First message" in embed.fields[0].value
        assert "User1" in embed.fields[1].name
        # Second message content in field 2, author in field 3
        assert "Second message" in embed.fields[2].value
        assert "User2" in embed.fields[3].name

    def test_build_quote_embed_empty_message_content(self):
        """Test that empty messages get placeholder text."""
        from utils.quoteUtils import build_quote_embed

        mock_message = PartialMessage(
            content="",
            jump_url="https://discord.com/channels/123/456/789",
            author_name="TestUser"
        )

        embed = build_quote_embed([mock_message])

        # Content is in the first field
        assert "[- kein Text -]" in embed.fields[0].value

    def test_build_quote_embed_with_author_name(self):
        """Test that author name appears in footer."""
        from utils.quoteUtils import build_quote_embed

        mock_message = PartialMessage(
            content="Test",
            jump_url="https://discord.com/channels/123/456/789",
            author_name="TestUser"
        )

        embed = build_quote_embed([mock_message], author_name="Submitter")

        assert embed.footer is not None
        assert embed.footer.text == "Eingereicht von Submitter"

    def test_build_quote_embed_long_content_truncation(self):
        """Test that messages longer than field limit are truncated."""
        from utils.quoteUtils import build_quote_embed

        mock_message = PartialMessage(
            content="A" * 2000,  # Very long message
            jump_url="https://discord.com/channels/123/456/789",
            author_name="TestUser"
        )

        embed = build_quote_embed([mock_message])

        # Content is in the first field
        field_content = embed.fields[0].value
        # The field should be under 1024 characters total
        assert len(field_content) <= 1024
        # Content should be truncated with "..."
        assert "..." in field_content
