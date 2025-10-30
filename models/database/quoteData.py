from typing import TYPE_CHECKING

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
