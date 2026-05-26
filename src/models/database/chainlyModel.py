from typing import TYPE_CHECKING

from tortoise import fields

from models.database.baseModel import BaseModel

if TYPE_CHECKING:
    from models.database.userData import User


class ChainlyGame(BaseModel):
    """
    A class representing a completed chainly game.
    """

    uuid = fields.UUIDField(pk=True, description="The UUID of the game session")
    topic = fields.TextField(description="The topic of that game.")
    result = fields.TextField(description="The final result string of that game.")


class ChainlyParticipation(BaseModel):
    """
    A class representing a user's participation in a chainly game.
    """

    game: fields.ForeignKeyRelation["ChainlyGame"] = fields.ForeignKeyField(
        "models.ChainlyGame",
        related_name="participants",
        description="The game session the user participated in",
    )
    user: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField(
        "models.User",
        related_name="chainly_games",
        description="The participating user",
    )
