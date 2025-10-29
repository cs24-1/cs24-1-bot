from typing import TYPE_CHECKING

from tortoise import fields

from models.database.baseModel import BaseModel

if TYPE_CHECKING:
    from models.database.userData import User


class ReactionLearning(BaseModel):
    """
    A class representing learned associations between message patterns
    and reactions.
    """
    id = fields.IntField(
        pk=True,
        description="The ID of the reaction learning entry"
    )
    message_content = fields.TextField(
        description="The content of the message that received the reaction"
    )
    reaction = fields.CharField(
        max_length=255,
        description="The reaction emoji that was added"
    )
    count = fields.IntField(
        default=1,
        description=
        "The number of times this reaction was used for similar messages"
    )
    channel_id = fields.BigIntField(
        description="The ID of the channel where the reaction was learned"
    )
    created_at = fields.DatetimeField(
        auto_now_add=True,
        description="When this pattern was first learned"
    )
    last_seen = fields.DatetimeField(
        auto_now=True,
        description="When this pattern was last reinforced"
    )

    class Meta:
        table = "reaction_learning"
        unique_together = (("message_content",
                            "reaction",
                            "channel_id"),
                           )

    async def increment_count(self):
        """
        Increment the count of times this reaction pattern was seen.
        """
        self.count += 1
        await self.save()

    def __str__(self):
        """
        Return a string representation of the ReactionLearning instance.

        :returns: A description of the learned pattern.
        """
        return (f"Reaction '{self.reaction}' for message pattern "
                f"(count: {self.count})")
