import os
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()


class Secrects:
    DISCORD_TOKEN = str(os.getenv("DISCORD_TOKEN"))  # type: ignore
    OPENAI_TOKEN = str(os.getenv("OPENAI_TOKEN"))  # type: ignore


class ChannelIds:
    MENSA_CHANNEL = int(os.getenv("MENSA_CHANNEL"))  # type: ignore
    MEME_CHANNEL = int(os.getenv("MEME_CHANNEL"))  # type: ignore


class ServerIds:
    CUR_SERVER = int(os.getenv("CUR_SERVER"))  # type: ignore


class Reactions:
    CHECK = "✅"
    CROSS = "❌"


class FilePaths:
    RAW_MEME_FOLDER = "data/memes/raw"
    BANNERIZED_MEME_FOLDER = "data/memes/bannerized"
    OCR_DATA_FOLDER = "data/ocr"
    DB_FILE = "data/db.sqlite3"


class Urls:
    MENSAPLAN = "https://www.studentenwerk-leipzig.de/mensen-cafeterien/speiseplan/?location=140&date="


class MensaSelectors:
    # --- Common CSS selectors used for all meal types ---
    # All Selectors are relative to the MEAL_CONTAINER, including the MEAL_CONTAINER itself
    MEAL_CONTAINER = "main#page-content > div.grid-container > div > div > div:nth-of-type(3) > div"
    MEAL_TYPE = "div:nth-of-type(1) > div:nth-of-type(1)"
    MEAL_PRICE = "div:nth-of-type(3) > div:nth-of-type(1)"
    # Specific selectors for meal details which are not pasta
    MEAL_NAME = "h4"
    MEAL_COMPONENTS = "h4 + div"
    # Specific selector for pasta meal type
    PASTA_SUBITEM = ".meal-subitem"
    PASTA_NAME = "h5"


class AI:
    OPENAI_MODEL = "gpt-4o-mini"
    MAX_TRANSLATE_REQUESTS_PER_DAY = 5


class Constants:
    SECRETS = Secrects
    CHANNEL_IDS = ChannelIds
    SERVER_IDS = ServerIds
    REACTIONS = Reactions
    URLS = Urls
    FILE_PATHS = FilePaths
    AI = AI
    # --- ADDITIONAL CONSTANTS ---
    SYSTIMEZONE = datetime.now().astimezone().tzinfo
