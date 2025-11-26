from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "user" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL /* The ID of the user on Discord */,
    "global_name" VARCHAR(255) NOT NULL  /* The name of the user on Discord */,
    "display_name" VARCHAR(255) NOT NULL  /* The display name of the user on the Server */
);
CREATE TABLE IF NOT EXISTS "meme" (
    "uuid" CHAR(36) NOT NULL  PRIMARY KEY /* The UUID of the meme image */,
    "format" VARCHAR(3) NOT NULL  /* The format of the meme image */,
    "message" TEXT NOT NULL  /* The message that the user attached to the meme image */,
    "content" TEXT NOT NULL  /* The OCRed content of the meme image */,
    "date" TIMESTAMP NOT NULL  /* The date the meme was sent */,
    "author_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSON NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
