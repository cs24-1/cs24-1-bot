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


class Mensa:
    OPENMENSA_API = "https://openmensa.org/api/v2/canteens/69/days/{date}/meals"
    NOODLE_NAMES = {"nudel", "spirelli", "spaghetti"}
    ALLERGENS = {
        "glutenhaltiges getreide",
        "krebstiere",
        "eier",
        "fisch",
        "erdnüsse",
        "soja",
        "milch/ milchzucker",
        "schalenfrüchte/ nüsse",
        "sellerie",
        "senf",
        "sesam",
        "sulfit/ schwefeldioxid",
        "lupine",
        "weichtiere",
        "insekten",
        "mandeln",
        "haselnüsse",
        "walnüsse",
        "cashewnüsse",
        "pekannüsse",
        "paranüsse",
        "pistazien",
        "macadamianüsse",
        "weizen",
        "roggen",
        "gerste",
        "hafer",
        "dinkel",
        "kamut",
        "konservierungsstoff",
        "antioxidationsmittel",
        "phosphat",
    }
    UNNECCESSARY_NOTES = {
        "vegetarisch",
        "geflügel",
        "schwein",
        "vegan",
    }


class AI:
    OPENAI_MODEL = "gpt-4o-mini"
    MAX_TRANSLATE_REQUESTS_PER_DAY = 5


class Constants:
    SECRETS = Secrects
    CHANNEL_IDS = ChannelIds
    SERVER_IDS = ServerIds
    REACTIONS = Reactions
    URLS = Mensa
    FILE_PATHS = FilePaths
    AI = AI
    MENSA = Mensa
    # --- ADDITIONAL CONSTANTS ---
    SYSTIMEZONE = datetime.now().astimezone().tzinfo
