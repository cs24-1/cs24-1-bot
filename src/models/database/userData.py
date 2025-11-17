from typing import TYPE_CHECKING

from tortoise import Model, fields

from models.database.baseModel import BaseModel
from utils.constants import Constants

if TYPE_CHECKING:
    from models.database.aiData import AIMetadata


class User(BaseModel):
    id = fields.IntField(pk=True, description="The ID of the user on Discord")
    global_name = fields.CharField(
        max_length=255,
        description="The name of the user on Discord"
    )
    display_name = fields.CharField(
        max_length=255,
        description="The display name of the user on the Server"
    )  # Maybe outdated because it is not updated onevery message
    ai_metadata: fields.OneToOneRelation["AIMetadata"]

    async def remaining_ai_requests(self):
        """
        Return the number of remaining requests for the AI service.
        """
        await self.fetch_related("ai_metadata")
        return Constants.AI.MAX_TRANSLATE_REQUESTS_PER_DAY - self.ai_metadata.usage_today

    async def increment_ai_usage(self):
        """
        Increment the usage of the AI service by one.
        """
        await self.ai_metadata.increment_usage()

    def __str__(self):
        return self.display_name
