import random
from tortoise.transactions import in_transaction

from discord import ApplicationContext, Embed, Color
import discord
from discord.utils import utcnow
from thefuzz import fuzz  # type: ignore

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
    embed = Embed(
        title="💬 Neues Zitat",
        color=Color.blurple()
    )

    for msg in messages:
        content = msg.content if msg.content else "[- kein Text -]"
        # Description field has 4096 char limit, truncate if needed
        max_content_length = 4096 - 2  # 2 for quotes
        if len(content) > max_content_length:
            content = content[:max_content_length - 3] + "..."

        # Add content in description
        if embed.description:
            embed.description += f"\n\n\u201C{content}\u201D"
        else:
            embed.description = f"\u201C{content}\u201D"

        # Add author and link as field
        link_text = f"[Originalnachricht]({msg.jump_url})"
        embed.add_field(
            name=f"~ {msg.author.display_name}",
            value=link_text,
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
        id=int(ctx.author.id), defaults={
            "global_name": ctx.author.name, "display_name": ctx.author.display_name})

    date_reported = msg.created_at if (msg :=
                                       ctx.message) else utcnow()

    quote = await Quote.create(
        reporter=reporter,
        date_reported=date_reported,
        comment=comment
    )

    for message in messages:
        author, _ = await User.get_or_create(
            id=int(message.author.id), defaults={
                "global_name": message.author.name, "display_name": message.author.display_name})
        await QuoteMessage.create(
            content=message.content,
            author=author,
            date=message.created_at,
            quote=quote
        )


async def store_custom_quote_in_db(
    ctx: ApplicationContext,
    content: str,
    person: str,
):
    """
    Stores a custom quote (without Discord messages) in the database.

    Args:
        ctx (ApplicationContext): The context of the command.
        content (str): The text of the quote.
        person (str): The person the quote is attributed to.
    """
    reporter, _ = await User.get_or_create(
        id=int(ctx.author.id),
        defaults={"global_name": ctx.author.name, "display_name": ctx.author.display_name}
    )

    # Create the quote
    quote = await Quote.create(
        reporter=reporter,
        date_reported=utcnow(),
    )

    # Create or reuse a User record for the person being quoted.
    # We must not attempt to set the primary key `id` (an IntField).
    # Use `global_name` to find an existing entry or create a new one.

    custom_global_name = f"custom_person_{person}"
    author = await User.filter(global_name=custom_global_name).first()
    if author is None:
        # Use transaction to prevent race condition in ID assignment
        async with in_transaction() as connection:
            # Find the minimum negative id used so far, or start at -1
            min_id_user = await User.filter(
                id__lt=0
            ).order_by("id").using_db(connection).first()
            next_id = min_id_user.id - 1 if min_id_user else -1
            author = await User.create(
                id=next_id,
                global_name=custom_global_name,
                display_name=person,
                using_db=connection
            )

    await QuoteMessage.create(
        content=content,
        author=author,
        date=utcnow(),
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
        await quote_channel.send(content=f"💬 {comment}", embed=embed)
    else:
        await quote_channel.send(embed=embed)


async def build_custom_quote_embed(
    content: str,
    person: str,
    created_by: discord.abc.User
) -> discord.Embed:
    """
    Creates a Discord embed for a custom quote, visually consistent with message-based quotes.
    """
    embed = discord.Embed(
        title="💬 Neues Zitat",
        color=discord.Color.blurple()
    )

    # Truncate content to fit within description limit (4096 chars)
    # Account for the quotes around content
    max_content_length = 4096 - 2  # 2 for the quotes
    if len(content) > max_content_length:
        truncated_content = content[:max_content_length - 3] + "..."
    else:
        truncated_content = content

    # Add content in description with quotes
    embed.description = f"\u201C{truncated_content}\u201D"

    # Add the person being quoted as a field
    embed.add_field(
        name=f"~ {person}",
        value="\u200b",  # Zero-width space for empty value
        inline=False
    )

    # Footer shows who submitted it
    embed.set_footer(text=f"Eingereicht von {created_by.display_name}")
    embed.timestamp = utcnow()
    return embed


async def get_random_quote() -> Quote:
    """
    Returns a random quote from the database.

    Raises:
        ValueError: If no quotes are found in the database.

    Returns:
        Quote: A random quote from the database.
    """
    quotes = await Quote.all()

    if len(quotes) == 0:
        raise ValueError("No quotes found in the database.")

    random_quote: Quote = random.choice(quotes)

    return random_quote


async def search_quotes(
    search_term: str | None,
    user_name: str | None,
    num: int
) -> list[Quote]:
    """
    Searches for quotes containing the search term or the given user.

    If only one is given, it will not care about the other. If both are given, this is an AND.

    Args:
        search_term (str | None): The search term.
        user_name (str | None): The author / reporter to search.
        num (int): How many matching results should be returned.

    Returns:
        list[Quote]: The matching results.
    """
    quotes = await Quote.all().prefetch_related(
        "messages",
        "messages__author",
        "reporter"
    )

    ranked_quotes = [
        (
            rank_quote(
                quote,
                search_term,
                user_name,
            ),
            quote,
        ) for quote in quotes
    ]

    filtered_quotes = [
        (
            score,
            quote,
        ) for score, quote in ranked_quotes if score > 50
    ]

    if len(filtered_quotes) == 0:
        return []

    return random.choices([quote for _, quote in filtered_quotes], k=num)


def rank_quote(
    quote: Quote,
    search_term: str | None,
    user_name: str | None
) -> int:
    """
    Rank a quote and return a normalized 0-100 score.

    If both search_term and user_name are provided the result is a weighted
    average of the two sub-scores. If only one is provided that sub-score is
    returned. Handles missing fields and limits input length for performance.
    """
    concatenated_text = quote.comment if quote.comment else ""
    for msg in quote.messages:
        concatenated_text += "\n" + msg.content
    concatenated_text = concatenated_text.strip()[:2000]

    concatenated_users = quote.reporter.display_name
    for msg in quote.messages:
        concatenated_users += "," + msg.author.display_name
    concatenated_users = concatenated_users.strip()[:1000]

    text_score: int = 0
    user_score: int = 0

    if search_term:
        text_score = fuzz.token_set_ratio(search_term, concatenated_text)

    if user_name:
        user_score = fuzz.token_set_ratio(user_name, concatenated_users)

    if text_score == 0:
        return user_score

    if user_score == 0:
        return text_score

    # weighted average, stays in 0-100 range
    final = text_score * Constants.QUOTE_WEIGHTS.TEXT_WEIGHT + user_score * Constants.QUOTE_WEIGHTS.USER_WEIGHT
    return int(round(final))
