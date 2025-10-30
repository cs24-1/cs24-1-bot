from discord import ApplicationContext, Embed, Color
import discord
from discord.utils import utcnow

from models.database.quoteData import QuoteMessage, Quote
from models.database.userData import User
from utils.constants import Constants


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


async def store_quote_in_db(
    ctx: ApplicationContext,
    messages: list[discord.Message],
    comment: str | None
):
    """
    Stores a quote with its messages in the database.

    Args:
        ctx (ApplicationContext): The app context.
        messages (list[discord.Message]): The messages to quote.
        comment (str | None): An optional comment to add.
    """
    reporter, _ = await User.get_or_create(
        id=str(ctx.author.id), defaults={
            "global_name": ctx.author.name, "display_name": ctx.author.display_name})

    date_reported = msg.created_at if (msg :=
                                       ctx.message) else discord.utils.utcnow()

    quote = await Quote.create(
        reporter=reporter,
        date_reported=date_reported,
        comment=comment
    )

    for message in messages:
        author, _ = await User.get_or_create(
            id=str(message.author.id), defaults={
                "global_name": message.author.name, "display_name": message.author.display_name})
        await QuoteMessage.create(
            content=message.content,
            author=author,
            date=message.created_at,
            quote=quote
        )


async def send_embed(
    ctx: ApplicationContext,
    messages: list[discord.Message],
    comment: str | None
):
    """
    Send a quote embed to the quotes channel.

    Args:
        ctx (ApplicationContext): The context of the app.
        messages (list[discord.Message]): The messages to quote.
        comment (str | None): An optional comment to add.
    """
    quote_channel: discord.TextChannel | None = ctx.guild.get_channel(
        Constants.CHANNEL_IDS.QUOTE_CHANNEL
    )

    if not quote_channel:
        await ctx.respond("❌ Quote-Channel nicht gefunden.", ephemeral=True)
        return

    embed = build_quote_embed(messages, ctx.author.display_name)

    if comment:
        await ctx.send(content=f"💬 {comment}", embed=embed)
    else:
        await ctx.send(embed=embed)
