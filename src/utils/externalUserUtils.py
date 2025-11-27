"""
Utilities for managing external (non-Discord) users in the database.

External users are created for quotes that don't originate from Discord
messages (e.g., custom quotes with arbitrary author names). They use
negative snowflake IDs to distinguish them from real Discord users.
"""

from snowflake import SnowflakeGenerator  # type: ignore

from models.database.userData import User

# Snowflake generator for external user IDs
# Using a fixed instance ID to ensure consistency across restarts
_external_user_generator = SnowflakeGenerator(instance=999)


async def get_or_create_external_user(author_name: str) -> User:
    """
    Get or create a User record for an external (non-Discord) author.

    External users are identified by negative IDs to distinguish them from
    real Discord users. The user is looked up by display_name, and if not
    found, a new user with a negative snowflake ID is created.

    Args:
        author_name: The name of the external author.

    Returns:
        User: The User object for the external author.
    """
    # First, try to find an existing external user by name
    existing_user = await User.filter(
        display_name=author_name,
        is_external=True
    ).first()

    if existing_user:
        return existing_user

    # Generate a negative snowflake ID
    external_id = -int(next(_external_user_generator))  # type: ignore

    # Create new external user
    user = await User.create(
        id=external_id,
        global_name=author_name,
        display_name=author_name,
        is_external=True
    )

    return user


def is_external_user(user: User) -> bool:
    """
    Check if a user is an external (non-Discord) user.

    Args:
        user: The user to check.

    Returns:
        bool: True if the user is external, False if it's a real Discord user.
    """
    return user.is_external
