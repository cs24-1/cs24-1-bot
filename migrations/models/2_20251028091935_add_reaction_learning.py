from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
 -- Create the table for reaction learning
CREATE TABLE IF NOT EXISTS
  "reaction_learning" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "message_content" TEXT NOT NULL
    /* The content of the message that received the reaction */,
    "reaction" VARCHAR(255) NOT NULL
    /* The reaction emoji that was added */,
    "count" INT NOT NULL DEFAULT 1
    /* The number of times this reaction was used for similar messages */,
    "channel_id" BIGINT NOT NULL
    /* The ID of the channel where the reaction was learned */,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    /* When this pattern was first learned */,
    "last_seen" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    /* When this pattern was last reinforced */,
    UNIQUE (message_content, reaction, channel_id)
  )
  /* A class representing learned associations between message patterns and reactions. */;
"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "reaction_learning";"""
