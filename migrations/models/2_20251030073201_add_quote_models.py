from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "quote" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL /* The unique identifier for the quote */,
    "date_reported" TIMESTAMP NOT NULL  /* The date and time when the quote was reported */,
    "comment" TEXT   /* An optional comment added by the reporter */,
    "reporter_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE /* The user who has marked and sent the quote */
) /* A class representing a quote. */;
        CREATE TABLE IF NOT EXISTS "quotemessage" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL /* The unique identifier for the quote */,
    "content" TEXT NOT NULL  /* The content of the quote message */,
    "date" TIMESTAMP NOT NULL  /* The date and time when the quote message was created */,
    "author_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE /* The author of the quote message */,
    "quote_id" INT NOT NULL REFERENCES "quote" ("id") ON DELETE CASCADE /* The quote this message belongs to */
) /* A class representing a message within a quote. */;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "quote";
        DROP TABLE IF EXISTS "quotemessage";"""
