from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
 -- Create the table for the AI metadata
CREATE TABLE IF NOT EXISTS
  "aimetadata" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "usage_today" INT NOT NULL DEFAULT 0
    /* The number of requests used today */
,
    "user_id" INT NOT NULL UNIQUE REFERENCES "user" ("id") ON DELETE CASCADE
  )
  /* A class representing metadata for the AI service. */;

-- Create default values for the AI metadata
INSERT INTO
  aimetadata (usage_today, user_id)
SELECT
  0,
  user.id
FROM
  user;
"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "aimetadata";"""
