import logging

from cachetools import TTLCache
import discord
from discord.ext import commands
from discord import ApplicationContext

from utils.constants import Constants
from utils import quoteUtils


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
        self.logger.info("MensaService started successfully")

    @discord.slash_command(
        name="quote",
        description=
        "Zitiert eine bis maximal fünf Nachrichten anhand ihrer URLs oder IDs.",
        guild_ids=[Constants.SERVER_IDS.CUR_SERVER],
    )
    async def quote(
        self,
        ctx: ApplicationContext,
        message_1: discord.Message,
        message_2: discord.Message | None,
        message_3: discord.Message | None,
        message_4: discord.Message | None,
        message_5: discord.Message | None,
        comment: str | None = None,
    ):
        messages: list[discord.Message] = [message_1]
        for msg in [message_2, message_3, message_4, message_5]:
            if msg is not None:
                messages.append(msg)

        await self._send_quote_embed(ctx, messages, comment)

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
            f"**Tipp:** nutze den Befehl `/quotes post`, um deine gesammelten Nachrichten zu zitieren.",
            ephemeral=True
        )

    quotes = discord.SlashCommandGroup(
        name="quotes",
        description="Verwalte deine gespeicherten Zitate."
    )

    @quotes.command(
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

        await self._send_quote_embed(ctx, quotes, comment)

        self.quote_cache.pop(user_id)

    @quotes.command(
        name="clear",
        description="Löscht alle gespeicherten Nachrichten.",
        guild_ids=[Constants.SERVER_IDS.CUR_SERVER]
    )
    async def clear_quotes(self, ctx: ApplicationContext):
        user_id = ctx.author.id
        self.quote_cache.pop(user_id, None)
        await ctx.respond(
            "✅ Alle gespeicherten Nachrichten wurden gelöscht.",
            ephemeral=True
        )

    async def _send_quote_embed(
        self,
        ctx: ApplicationContext,
        messages: list[discord.Message],
        comment: str | None,
    ):
        quote_channel: discord.TextChannel | None = ctx.guild.get_channel(
            Constants.CHANNEL_IDS.QUOTE_CHANNEL
        )

        if not quote_channel:
            await ctx.respond("❌ Quote-Channel nicht gefunden.", ephemeral=True)
            return

        embed = quoteUtils.build_quote_embed(messages, ctx.author.display_name)

        if comment:
            await quote_channel.send(content=f"💬 {comment}", embed=embed)
        else:
            await quote_channel.send(embed=embed)

        await ctx.respond(
            f"✅ {len(messages)} Quote{'s' if len(messages) > 1 else ''} gepostet!",
            ephemeral=True
        )


def setup(bot: commands.Bot):
    logger = logging.getLogger("bot")
    bot.add_cog(QuoteService(bot, logger))
