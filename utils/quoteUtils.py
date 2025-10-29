from discord import Embed, Color
import discord
from discord.utils import utcnow


def build_quote_embed(
    messages: list[discord.Message],
    author_name: str | None = None
) -> Embed:
    """
    Creates a Discord Embed that presents one or more messages as quoted entries.

    Some behavioural concepts:
    - Message content is truncated to 1024 characters to respect Discord field length limit.
    - If a message has no content (falsy), the placeholder "[- kein Text -]" is used instead.
    - Fields are added with inline=False so they appear on separate lines.
    - If author_name is provided, the embed footer is set to "Eingereicht von {author_name}".
    

    Args:
        messages (list[discord.Message]): The messages to include in the embed.
        author_name (str, optional): The name of the author submitting the quotes. Defaults to None.

    Returns:
        discord.Embed: The constructed embed.
    """
    embed = Embed(color=Color.blurple())
    for msg in messages:
        content = msg.content[:1024] if msg.content else "[- kein Text -]"
        embed.add_field(
            name=f"~ {msg.author.display_name}",
            value=f"“{content}”\n[Originalnachricht]({msg.jump_url})",
            inline=False
        )
    if author_name:
        embed.set_footer(text=f"Eingereicht von {author_name}")
    embed.timestamp = utcnow()
    return embed
