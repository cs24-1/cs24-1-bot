from utils.constants import Constants

TORTOISE_ORM = { # type: ignore
    "connections": {
        "default": f"sqlite://{Constants.FILE_PATHS.DB_FILE}"
    },
    "apps": {
        "models": {
            "models": [
                "models.database.userData",
                "models.database.memeData",
                "models.database.aiData",
                "models.database.quoteData",
                "aerich.models",
            ],
            "default_connection":
            "default",
        },
    },
}
