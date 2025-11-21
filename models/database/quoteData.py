from typing import TYPE_CHECKING

import discord
from tortoise import fields

from models.database.baseModel import BaseModel

if TYPE_CHECKING:
    from models.database.userData import User


class QuoteMessage(BaseModel):
    """
    A class representing a message within a quote.

    Attributes:
        content (str): The content of the message.
        author (User): The author of the message.
    """
    id = fields.IntField(
        pk=True,
        description="The unique identifier for the quote"
    )
    content = fields.TextField(description="The content of the quote message")
    author: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField(
        "models.User",
        related_name="quote_messages",
        description="The author of the quote message",
    )
    quote: fields.ForeignKeyRelation["Quote"] = fields.ForeignKeyField(
        "models.Quote",
        related_name="messages",
        description="The quote this message belongs to",
    )
    date = fields.DatetimeField(
        description="The date and time when the quote message was created"
    )


class Quote(BaseModel):
    """
    A class representing a quote.

    A quote can be either a single message with an author or a conversation with multiple messages and authors.
    """
    id = fields.IntField(
        pk=True,
        description="The unique identifier for the quote"
    )
    reporter: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField(
        "models.User",
        related_name="quotes_reported",
        description="The user who has marked and sent the quote",
    )
    date_reported = fields.DatetimeField(
        description="The date and time when the quote was reported"
    )
    messages: fields.ReverseRelation["QuoteMessage"]
    comment = fields.TextField(
        null=True,
        description="An optional comment added by the reporter"
    )

    async def create_embed(
        self,
        search_term: str | None,
        user_name: str | None
    ) -> discord.Embed:
        """
        Create a Discord embed for the quote.

        :param search: The search term to highlight in the embed, if any.
        :param user_name: The user name to highlight in the embed, if any.
        :returns: The created embed.
        """
        await self.fetch_related("reporter", "messages", "messages__author")

        embed = discord.Embed(
            description=f"*{self.comment}*" if self.comment else None,
            timestamp=self.date_reported
        )
        embed.set_footer(
            text=
            f"von {self.reporter.mention} ({self.reporter.global_name})"
        )

        for msg in self.messages:
            content = msg.content[:1024] if msg.content else "[- kein Text -]"
            embed.add_field(
                name=f"~ {msg.author.mention}",
                value=f"“{content}”",
                inline=False
            )

        if search_term is not None or user_name is not None:
            embed.set_author(
                name=self._create_search_string(search_term,
                                                user_name)
            )

        return embed

    def _create_search_string(
        self,
        search_term: str | None,
        user_name: str | None
    ) -> str | None:
        search_parts: list[str] = []
        if search_term is not None:
            search_parts.append(search_term)
        if user_name is not None:
            search_parts.append(user_name)

        if len(search_parts) == 0:
            return None
        return "🔍 " + ", ".join(search_parts)
