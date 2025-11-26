import logging

import discord
from cachetools import TTLCache
from discord import ApplicationContext
from discord.ext import commands

from models.quotes.quoteModels import PartialMessage
from utils import quoteUtils
from utils.constants import Constants


class QuoteService(commands.Cog):
    """
    A Discord Cog for creating and managing quotes.
    """

    def __init__(self, bot: discord.Bot, logger: logging.Logger) -> None:
        self.logger = logger
        self.bot = bot

        self.quote_cache: TTLCache[int, list[discord.Message]]
        self.quote_cache = TTLCache(
            maxsize=99,
            ttl=10 * 60,  # 10 minutes TTL
        )

    @commands.Cog.listener("on_ready")
    async def on_ready(self):
        self.logger.info("QuoteService started successfully")

    # ----- Slash Commands -----

    quote = discord.SlashCommandGroup(
        name="quote",
        description="Verwalte Zitate."
    )

    @quote.command(
        name="by_messages",
        description=
        "Zitiert eine bis maximal fünf Nachrichten anhand ihrer URLs oder IDs.",
        guild_ids=[Constants.SERVER_IDS.CUR_SERVER],
    )
    async def create_quote(
        self,
        ctx: ApplicationContext,
        message_1: discord.Message,
        message_2: discord.Message | None,
        message_3: discord.Message | None,
        message_4: discord.Message | None,
        message_5: discord.Message | None,
        comment: str | None = None,
    ):
        """
        Quotes up to five messages specified by their URLs or IDs.
        """
        messages: list[discord.Message] = [message_1]
        for msg in [message_2, message_3, message_4, message_5]:
            if msg is not None:
                messages.append(msg)

        await self._store_and_send_quote(ctx, messages, comment)

    @quote.command(
        name="post",
        description="Postet alle gesammelten Nachrichten als Quote.",
        guild_ids=[Constants.SERVER_IDS.CUR_SERVER]
    )
    async def post_quote(
        self,
        ctx: ApplicationContext,
        comment: str | None = None
    ):
        """
        Posts all collected messages as a quote and clears the cache.
        """
        user_id = ctx.author.id
        quotes = self.quote_cache.get(user_id)

        if not quotes:
            await ctx.respond(
                "❌ Du hast keine gespeicherten Nachrichten.",
                ephemeral=True
            )
            return

        await self._store_and_send_quote(ctx, quotes, comment)

        self.quote_cache.pop(user_id)

    @quote.command(
        name="clear",
        description="Löscht alle gespeicherten Nachrichten.",
        guild_ids=[Constants.SERVER_IDS.CUR_SERVER]
    )
    async def clear_quotes(self, ctx: ApplicationContext):
        """
        Clears all stored messages for the user.
        """
        user_id = ctx.author.id
        self.quote_cache.pop(user_id, None)
        await ctx.respond(
            "✅ Alle gespeicherten Nachrichten wurden gelöscht.",
            ephemeral=True
        )

    @quote.command(
        name="search",
        description="Suche nach einem Zitat",
        guild_ids=[Constants.SERVER_IDS.CUR_SERVER]
    )
    @discord.option(
        "search_term",
        type=discord.SlashCommandOptionType.string,
        required=False
    )
    @discord.option(
        "search_user",
        type=discord.SlashCommandOptionType.string,
        required=False
    )
    async def search_quote(
        self,
        ctx: ApplicationContext,
        search_term: str | None = None,
        search_user: str | None = None,
    ):
        """
        Searches for a quote matching the search term and user and sends it in an embed.
        """
        if search_term is None and search_user is None:
            quote = await quoteUtils.get_random_quote()
        else:
            quotes = await quoteUtils.search_quotes(search_term, search_user, 1)

            if len(quotes) == 0:
                await ctx.respond(
                    f"Kein Zitat für die Suche `{search_term}` und den Namen `{search_user}` gefunden!"
                )
                return

            quote = quotes[0]

        embed = await quote.create_embed(search_term, search_user)

        await ctx.respond(embed=embed)

    @quote.command(
        name="external",
        description="Erstellt ein eigenes Zitat mit Inhalt und Person.",
        guild_ids=[Constants.SERVER_IDS.CUR_SERVER]
    )
    @discord.option(
        "inhalt",
        description="Der Inhalt des Zitats.",
        type=discord.SlashCommandOptionType.string,
        required=True
    )
    @discord.option(
        "person",
        description="Die Person, der das Zitat zugeschrieben wird.",
        type=discord.SlashCommandOptionType.string,
        required=True
    )
    async def custom_quote(
        self,
        ctx: ApplicationContext,
        content: str,
        person: str
    ):
        """
        Creates a custom quote without linking to a Discord message and posts
        it to the quote channel.

        This command allows users to specify the content and the person to
        whom the quote is attributed. The quote is posted as an embed in the
        designated quote channel. If the quote channel is not found, an error
        message is sent to the user.

        Parameters:
            ctx (ApplicationContext): The context of the command invocation.
            content (str): The content of the quote.
            person (str): The person to whom the quote is attributed.
        """
        self.logger.info(
            "Custom quote created by %s: '%s' - %s",
            ctx.author,
            content,
            person
        )

        # Send embed to quote channel
        quote_channel: discord.TextChannel | None = ctx.guild.get_channel(
            Constants.CHANNEL_IDS.QUOTE_CHANNEL
        )

        if not quote_channel:
            await ctx.respond("❌ Quote-Channel nicht gefunden.", ephemeral=True)
            return

        partial_message = PartialMessage(
            content=content,
            author_name=person,
            jump_url=None
        )

        embed = quoteUtils.build_quote_embed(
            [partial_message],
            ctx.author.display_name
        )
        await quote_channel.send(embed=embed)
        await ctx.respond(
            "✅ Zitat wurde im Quote-Channel gepostet!",
            ephemeral=True
        )

    # ----- Message Commands -----

    @discord.message_command(
        name="Nachricht zu Quote hinzufügen",
        guild_ids=[Constants.SERVER_IDS.CUR_SERVER]
    )
    async def add_message_to_quote(
        self,
        ctx: ApplicationContext,
        message: discord.Message
    ):
        """
        Adds a single message to your personal quoting context.
        """
        user_id = ctx.author.id

        quotes = self.quote_cache.setdefault(user_id, [])

        quotes.append(message)

        await ctx.respond(
            f"📌 Nachricht von **{message.author.display_name}** gespeichert!\n"
            f"({len(self.quote_cache[user_id])} gesammelt - verfällt in {self.quote_cache.ttl // 60} Minuten)\n\n"
            f"**Tipp:** nutze den Befehl `/quote post`, um deine gesammelten Nachrichten zu zitieren.",
            ephemeral=True
        )

    @discord.message_command(
        name="Nachricht direkt zitieren",
        guild_ids=[Constants.SERVER_IDS.CUR_SERVER]
    )
    async def quote_single_message(
        self,
        ctx: ApplicationContext,
        message: discord.Message
    ):
        """
        Immediately quotes a single selected message into the quotes channel.
        """
        await self._store_and_send_quote(ctx, [message], None)

        await ctx.respond(
            f"📌 Nachricht von **{message.author.display_name}** im Quotes-Channel zitiert!",
            ephemeral=True
        )

    # ---- Internal Methods -----

    async def _store_and_send_quote(
        self,
        ctx: ApplicationContext,
        messages: list[discord.Message],
        comment: str | None,
    ):
        await quoteUtils.store_quote_in_db(ctx, messages, comment)

        partial_messages = [
            PartialMessage.from_discord_message(msg) for msg in messages
        ]

        await quoteUtils.send_embed(ctx, partial_messages, comment)

        await ctx.respond(
            f"✅ {len(messages)} Quote{'s' if len(messages) > 1 else ''} gepostet!",
            ephemeral=True
        )


def setup(bot: commands.Bot):
    logger = logging.getLogger("bot")
    bot.add_cog(QuoteService(bot, logger))
