from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "chainlygame" (
    "uuid" CHAR(36) NOT NULL  PRIMARY KEY /* The UUID of the game session */,
    "topic" TEXT NOT NULL  /* The topic of that game. */,
    "result" TEXT NOT NULL  /* The final result string of that game. */
) /* A class representing a completed chainly game. */;
        CREATE TABLE IF NOT EXISTS "chainlyparticipation" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "game_uuid_id" CHAR(36) NOT NULL REFERENCES "chainlygame" ("uuid") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
) /* A class representing a users participation in a chainly game. */;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "chainlygame";
        DROP TABLE IF EXISTS "chainlyparticipation";"""
