from dataclasses import dataclass

from discord import Message


@dataclass
class PartialMessage:
    content: str | None
    jump_url: str | None
    author_name: str | None

    @classmethod
    def from_discord_message(cls, message: Message) -> "PartialMessage":
        """
        Create a PartialMessage from a discord.Message.

        Args:
            message: The discord.Message to convert.

        Returns:
            A PartialMessage with content, jump_url and author_name
            extracted from the message. Missing attributes become None.
        """

        return cls(
            content=message.content,
            jump_url=message.jump_url,
            author_name=message.author.display_name if message.author else None,
        )
