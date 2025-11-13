"""
Unit tests for utils/constants.py
"""

class TestConstants:
    """Tests for utils/constants.py"""

    def test_constants_class_exists(self):
        """Test that Constants class is properly defined."""
        from utils.constants import Constants

        assert Constants is not None

    def test_secrets_configuration(self):
        """Test that SECRETS class has required tokens."""
        from utils.constants import Constants

        assert hasattr(Constants.SECRETS, "DISCORD_TOKEN")
        assert hasattr(Constants.SECRETS, "OPENAI_TOKEN")
        assert Constants.SECRETS.DISCORD_TOKEN == "test_token"
        assert Constants.SECRETS.OPENAI_TOKEN == "test_token"

    def test_channel_ids_configuration(self):
        """Test that CHANNEL_IDS class has all required channels."""
        from utils.constants import Constants

        assert hasattr(Constants.CHANNEL_IDS, "MENSA_CHANNEL")
        assert hasattr(Constants.CHANNEL_IDS, "MEME_CHANNEL")
        assert hasattr(Constants.CHANNEL_IDS, "QUOTE_CHANNEL")
        assert Constants.CHANNEL_IDS.MENSA_CHANNEL == 123456
        assert Constants.CHANNEL_IDS.MEME_CHANNEL == 123456
        assert Constants.CHANNEL_IDS.QUOTE_CHANNEL == 123456

    def test_server_ids_configuration(self):
        """Test that SERVER_IDS class has current server ID."""
        from utils.constants import Constants

        assert hasattr(Constants.SERVER_IDS, "CUR_SERVER")
        assert Constants.SERVER_IDS.CUR_SERVER == 123456

    def test_reactions_constants(self):
        """Test that reaction emojis are properly defined."""
        from utils.constants import Constants

        assert Constants.REACTIONS.CHECK == "✅"
        assert Constants.REACTIONS.CROSS == "❌"

    def test_file_paths_structure(self):
        """Test that file path constants are properly defined."""
        from utils.constants import Constants

        assert hasattr(Constants.FILE_PATHS, "RAW_MEME_FOLDER")
        assert hasattr(Constants.FILE_PATHS, "BANNERIZED_MEME_FOLDER")
        assert hasattr(Constants.FILE_PATHS, "OCR_DATA_FOLDER")
        assert hasattr(Constants.FILE_PATHS, "DB_FILE")

        # Verify paths are strings
        assert isinstance(Constants.FILE_PATHS.RAW_MEME_FOLDER, str)
        assert isinstance(Constants.FILE_PATHS.DB_FILE, str)

    def test_mensa_configuration(self):
        """Test that Mensa constants are properly defined."""
        from utils.constants import Constants

        # Test API URL exists and is a string
        assert hasattr(Constants.MENSA, "OPENMENSA_API")
        assert isinstance(Constants.MENSA.OPENMENSA_API, str)
        assert "{date}" in Constants.MENSA.OPENMENSA_API

        # Test noodle names set
        assert hasattr(Constants.MENSA, "NOODLE_NAMES")
        assert isinstance(Constants.MENSA.NOODLE_NAMES, set)
        assert "nudel" in Constants.MENSA.NOODLE_NAMES
        assert "pasta" in Constants.MENSA.NOODLE_NAMES
        assert len(Constants.MENSA.NOODLE_NAMES) > 5

        # Test allergens set
        assert hasattr(Constants.MENSA, "ALLERGENS")
        assert isinstance(Constants.MENSA.ALLERGENS, set)
        assert len(Constants.MENSA.ALLERGENS) > 10

    def test_ai_configuration(self):
        """Test that AI constants are properly defined."""
        from utils.constants import Constants

        assert hasattr(Constants.AI, "OPENAI_MODEL")
        assert hasattr(Constants.AI, "MAX_TRANSLATE_REQUESTS_PER_DAY")

        # Verify values
        assert isinstance(Constants.AI.OPENAI_MODEL, str)
        assert isinstance(Constants.AI.MAX_TRANSLATE_REQUESTS_PER_DAY, int)
        assert Constants.AI.MAX_TRANSLATE_REQUESTS_PER_DAY > 0

    def test_quote_weights_configuration(self):
        """Test that quote search weights are properly configured."""
        from utils.constants import Constants

        assert hasattr(Constants.QUOTE_WEIGHTS, "TEXT_WEIGHT")
        assert hasattr(Constants.QUOTE_WEIGHTS, "USER_WEIGHT")

        # Verify they are floats
        assert isinstance(Constants.QUOTE_WEIGHTS.TEXT_WEIGHT, float)
        assert isinstance(Constants.QUOTE_WEIGHTS.USER_WEIGHT, float)

        # Verify weights sum to 1.0 (standard weighting)
        total = (
            Constants.QUOTE_WEIGHTS.TEXT_WEIGHT +
            Constants.QUOTE_WEIGHTS.USER_WEIGHT
        )
        assert abs(total - 1.0) < 0.01

    def test_system_timezone_exists(self):
        """Test that system timezone is set."""
        from utils.constants import Constants

        assert hasattr(Constants, "SYSTIMEZONE")
        assert Constants.SYSTIMEZONE is not None
