import logging
from datetime import time

import discord
from discord import ApplicationContext
from discord.ext import commands, tasks

from models.database.userData import User
from utils.ai import ai
from utils.constants import Constants


class AIService(commands.Cog):
    """
    A Discord Cog for using the OpenAI API to translate code.
    """

    def __init__(self, bot: discord.Bot, logger: logging.Logger) -> None:
        self.logger = logger
        self.bot = bot
        self.ai = ai.AIUtils()

        self.reset_ai_usage.start()

    @tasks.loop(time=time(hour=0, minute=5, tzinfo=Constants.SYSTIMEZONE))
    async def reset_ai_usage(self):
        """
        Reset the usage of the AI service for all users.
        """
        users = await User.all()

        for user in users:
            await user.fetch_related("ai_metadata")
            await user.ai_metadata.reset_usage()

        self.logger.info("Reset AI usage for all users")

    @commands.slash_command(
        name="translate",
        description="Übersetze den gegebenen Code in die angegebene Sprache.",
        guild_ids=[Constants.SERVER_IDS.CUR_SERVER]
    )
    @discord.option(
        "language",
        type=discord.SlashCommandOptionType.string,
        required=True
    )
    @discord.option(
        "code",
        type=discord.SlashCommandOptionType.string,
        required=True
    )
    async def translate(
        self,
        ctx: ApplicationContext,
        language: str,
        code: str
    ):
        """
        Translates the given code into the specified language.
        """

        await ctx.defer()

        user, _ = await User.get_or_create(
                id=str(ctx.author.id), defaults={
                    "global_name": ctx.author.name, "display_name": ctx.author.display_name})

        if await user.remaining_ai_requests() <= 0:
            await ctx.respond(
                "AI ist nicht billig, du hast dein tägliches Limit erreicht. Versuche es morgen erneut.",
                ephemeral=True
            )
            return

        await user.increment_ai_usage()

        try:
            response = self.ai.code_translate(language, code)
        except Exception as e:
            self.logger.error(f"Error translating code: {e}")
            await ctx.respond(
                "Es gab einen Fehler beim Übersetzen des Codes.",
                ephemeral=True
            )
            return

        embed = await response.create_embed(
            ctx.author,
            await user.remaining_ai_requests()
        )

        await ctx.respond(embed=embed)


def setup(bot: discord.Bot):
    logger = logging.getLogger("bot")
    bot.add_cog(AIService(bot, logger))
