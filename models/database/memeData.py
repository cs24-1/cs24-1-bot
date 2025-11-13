from enum import Enum
from typing import TYPE_CHECKING

import discord
from tortoise import Model, fields

from models.database.baseModel import BaseModel
from utils.constants import Constants

if TYPE_CHECKING:
    from models.database.userData import User


class MemeFormat(Enum):
    """Enum representing the format of the meme image."""
    PNG = "png"
    GIF = "gif"


class Meme(BaseModel):
    """
    A class representing a meme image.
    """
    uuid = fields.UUIDField(pk=True, description="The UUID of the meme image")
    format = fields.CharEnumField(
        MemeFormat,
        max_length=3,
        description="The format of the meme image"
    )
    message = fields.TextField(
        description="The message that the user attached to the meme image"
    )
    content = fields.TextField(
        description="The OCRed content of the meme image"
    )
    author: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField(
        "models.User",
        related_name="memes"
    )
    date = fields.DatetimeField(description="The date the meme was sent")

    async def create_embed(self,
                           search: str | None) -> tuple[discord.Embed,
                                                        discord.File]:
        """
        Create a Discord embed for the meme.

        :param search: The search term to highlight in the embed, if any.
        :returns: The created embed and the image file.
        """
        await self.fetch_related("author")
        image_file = discord.File(
            f"{Constants.FILE_PATHS.RAW_MEME_FOLDER}/{self.uuid}.{self.format.value}",
            filename=f"{self.uuid}.{self.format.value}"
        )

        embed = discord.Embed(
            description=f"*{self.message}*" if self.message != "" else None,
            timestamp=self.date
        )
        embed.set_image(url=f"attachment://{image_file.filename}")
        embed.set_footer(
            text=f"von @{self.author.display_name} ({self.author.global_name})"
        )

        if search is not None:
            embed.set_author(name=f"🔍 {search}")

        return embed, image_file

    def __str__(self):
        """
        Return a string representation of the Meme instance.

        :returns: The UUID of the meme.
        """
        return self.uuid
