from discord import Embed, Color
from discord.utils import utcnow

def build_quote_embed(messages, author_name=None):
    """Create a Discord Embed that presents one or more messages as quoted entries.

    Parameters
    ----------
    messages : Iterable[discord.Message]
        An iterable of message objects to include in the embed. Each message must
        provide at least the following attributes:
        - content: the text content of the message (str or falsy for empty)
        - author.display_name: display name of the message author (str)
        - jump_url: a URL linking to the original message (str)
    author_name : Optional[str], default None
        If provided, this string will be placed in the embed footer as
        "Eingereicht von {author_name}".

    Returns
    -------
    discord.Embed
        A discord.Embed containing one field per message. Each field's name is
        "~ {author_display_name}" and its value is the message content wrapped in
        quotation marks followed by a link labeled "Originalnachricht" to the
        original message. The embed uses Color.blurple() as its color and its
        timestamp is set to the current UTC time.

    Behavior and edge cases
    -----------------------
    - Message content is truncated to 1024 characters to respect Discord field
      length limits.
    - If a message has no content (falsy), the placeholder "[- kein Text -]" is
      used instead.
    - Fields are added with inline=False so they appear on separate lines.
    - If author_name is provided, the embed footer is set to "Eingereicht von {author_name}".
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