from tortoise import fields

from models.database.baseModel import BaseModel
from models.database.userData import User


class AIMetadata(BaseModel):
    """
    A class representing metadata for the AI service.
    """
    usage_today = fields.IntField(
        description="The number of requests used today",
        default=0
    )
    user: fields.OneToOneRelation["User"] = fields.OneToOneField(
        "models.User",
        related_name="ai_metadata"
    )

    async def increment_usage(self):
        """
        Increment the usage of the AI for the user service by one.
        """
        self.usage_today += 1
        await self.save()

    async def reset_usage(self):
        """
        Reset the usage of the AI service for the user.
        """
        self.usage_today = 0
        await self.save()

    def __str__(self):
        """
        Return a string representation of the AIMetadata instance.

        :returns: The key of the metadata.
        """
        return f"{self.user.global_name} ({self.user.id}) used {self.usage_today} requests today"
