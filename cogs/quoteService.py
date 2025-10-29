import logging

import discord
from discord.ext import commands

from utils.constants import Constants
from utils import quoteUtils


class QuoteService(commands.Cog):
    """
    A Discord Cog for creating and managing quotes.
    """

    def __init__(self, bot: discord.Bot, logger: logging.Logger) -> None:
        self.logger = logger
        self.bot = bot

    @discord.slash_command(
        name="quote",
        description=
        "Zitiert eine oder mehrere Nachrichten anhand ihrer URLs oder IDs.",
        guild_ids=[Constants.SERVER_IDS.CUR_SERVER],
    )
    @discord.option(
        "message_1",
        type=discord.Message,
        required=True,
    )
    @discord.option(
        "message_2",
        type=discord.Message,
        required=False,
    )
    @discord.option(
        "message_3",
        type=discord.Message,
        required=False,
    )
    @discord.option(
        "message_4",
        type=discord.Message,
        required=False,
    )
    @discord.option(
        "message_5",
        type=discord.Message,
        required=False,
    )
    @discord.option(
        "comment",
        type=str,
        required=False,
    )
    async def quote(
        self,
        ctx: discord.ApplicationContext,
        message_1: discord.Message,
        message_2: discord.Message | None,
        message_3: discord.Message | None,
        message_4: discord.Message | None,
        message_5: discord.Message | None,
        comment: str | None = None
    ):
        quote_channel: discord.TextChannel | None = ctx.guild.get_channel(
            Constants.CHANNEL_IDS.QUOTE_CHANNEL
        )

        if not quote_channel:
            await ctx.respond("❌ Quote-Channel nicht gefunden.", ephemeral=True)
            return

        messages: list[discord.Message] = [message_1]
        for msg in [message_2, message_3, message_4, message_5]:
            if msg is not None:
                messages.append(msg)

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
