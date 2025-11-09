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
    QUOTE_CHANNEL = int(os.getenv("QUOTE_CHANNEL"))  # type: ignore
    TIMETABLE_CHANNEL = int(os.getenv("TIMETABLE_CHANNEL"))  # type: ignore


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
    NOODLE_NAMES = {
        "nudel",
        "spirelli",
        "spaghetti",
        "pasta",
        "penne",
        "fusilli",
        "farfalle",
        "rigatoni",
        "tagliatelle",
        "tortellini",
        "ravioli",
    }
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


class DateConstants:
    HOLIDAYS = {
        datetime(2025, 1, 1).date(),    # Neujahr 
        datetime(2025, 4, 18).date(),   # Karfreitag
        datetime(2025, 4, 21).date(),   # Ostermontag
        datetime(2025, 5, 1).date(),    # Tag der Arbeit
        datetime(2025, 5, 29).date(),   # Christi Himm
        datetime(2025, 6, 9).date(),    # Pfingstmontag
        datetime(2025, 10, 3).date(),   # Tag der Deutschen Einheit
        datetime(2025, 12, 25).date(),  # 1. Weihnachtstag
        datetime(2025, 12, 26).date(),  # 2. Weihnachtstag
    }


class QuoteWeights:
    TEXT_WEIGHT = 0.7
    USER_WEIGHT = 0.3


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
    QUOTE_WEIGHTS = QuoteWeights
    DATES = DateConstants
    # --- ADDITIONAL CONSTANTS ---
    SYSTIMEZONE = datetime.now().astimezone().tzinfo
