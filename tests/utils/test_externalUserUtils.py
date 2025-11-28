"""Tests for external user utilities."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from utils.externalUserUtils import is_external_user


class TestIsExternalUser:
    """Test cases for is_external_user function."""

    def test_returns_true_for_external_user(self):
        """Test that users with is_external=True are identified as external."""
        mock_user = MagicMock()
        mock_user.is_external = True

        assert is_external_user(mock_user) is True

    def test_returns_false_for_internal_user(self):
        """Test that users with is_external=False are not external."""
        mock_user = MagicMock()
        mock_user.is_external = False

        assert is_external_user(mock_user) is False


class TestGetOrCreateExternalUser:
    """Test cases for get_or_create_external_user function."""

    @pytest.mark.asyncio
    @patch("utils.externalUserUtils.User")
    @patch("utils.externalUserUtils._external_user_generator")
    async def test_creates_new_user_when_not_found(
        self,
        mock_generator: MagicMock,
        mock_user_model: MagicMock
    ):
        """Test that a new external user is created when not found."""
        from utils.externalUserUtils import get_or_create_external_user

        # Mock filter to return None (user not found)
        mock_filter = AsyncMock()
        mock_filter.first = AsyncMock(return_value=None)
        mock_user_model.filter.return_value = mock_filter

        # Mock snowflake generator
        mock_generator.__next__.return_value = 123456789

        # Mock User.create
        mock_created_user = MagicMock()
        mock_created_user.id = -123456789
        mock_created_user.display_name = "Test Person"
        mock_created_user.global_name = "Test Person"
        mock_user_model.create = AsyncMock(return_value=mock_created_user)

        # Call function
        result = await get_or_create_external_user("Test Person")

        # Verify filter was called with correct parameters
        mock_user_model.filter.assert_called_once()

        # Verify create was called with negative ID
        mock_user_model.create.assert_called_once()
        create_kwargs = mock_user_model.create.call_args[1]
        assert create_kwargs["id"] < 0
        assert create_kwargs["display_name"] == "Test Person"
        assert create_kwargs["global_name"] == "Test Person"
        assert create_kwargs["is_external"] is True

        assert result == mock_created_user

    @pytest.mark.asyncio
    @patch("utils.externalUserUtils.User")
    async def test_returns_existing_user_when_found(
        self,
        mock_user_model: MagicMock
    ):
        """Test that existing user is returned when found."""
        from utils.externalUserUtils import get_or_create_external_user

        # Mock existing user
        existing_user = MagicMock()
        existing_user.id = -987654321
        existing_user.display_name = "Existing Person"

        # Mock filter to return existing user
        mock_filter = AsyncMock()
        mock_filter.first = AsyncMock(return_value=existing_user)
        mock_user_model.filter.return_value = mock_filter

        # Call function
        result = await get_or_create_external_user("Existing Person")

        # Verify create was NOT called
        mock_user_model.create.assert_not_called()

        # Verify existing user was returned
        assert result == existing_user
