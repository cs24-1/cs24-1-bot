import logging

import discord
from discord.ext import commands

from utils.chainlyUtils import search_game, try_start_game
from utils.constants import Constants


class ChainlyService(commands.Cog):
    """
    Discord Cog for chainly game.
    """

    def __init__(self, bot: discord.Bot, logger: logging.Logger) -> None:
        self.bot = bot
        self.logger = logger

    @commands.Cog.listener("on_ready")
    async def on_ready(self) -> None:
        """
        Log when the cog has been loaded successfully.
        """
        self.logger.info("ChainlyService started successfully")

    @commands.slash_command(
        name="chainly",
        description="Startet das chainly Spiel",
        guild_ids=[Constants.SERVER_IDS.CUR_SERVER],
    )
    @discord.option(
        "topic",
        description="Das Thema für das chainly Spiel (z.B. 'Beschwerdeschreiben', 'Lebenslauf', etc.)",
        type=discord.SlashCommandOptionType.string,
        required=True,
    )
    async def chainly_start_command(
        self, ctx: discord.ApplicationContext, topic: str
    ) -> None:
        """
        Slash command to start chainly game.
        """


        try:
            _ = await ctx.respond(
                await try_start_game(self.bot, ctx.channel_id, topic),
                ephemeral=True,
            )
        except Exception as e:
            self.logger.error(f"Error starting chainly game: {e}")
            _ = await ctx.respond(
                "Es gab einen Fehler beim Starten des Spiels.",
                ephemeral=True
            )

    @commands.slash_command(
        name="chainly_search",
        description="Suche nach abgeschlossenen Spielen",
        guild_ids=[Constants.SERVER_IDS.CUR_SERVER],
    )
    @discord.option(
        "topic",
        description="Thema des Spiels.",
        type=discord.SlashCommandOptionType.string,
        required=True,
    )
    async def chainly_search_command(
        self, ctx: discord.ApplicationContext, topic: str
    ) -> None:
        """
        Slash command to search finished chainly games.
        """

        try:
            _ = await ctx.respond(
                await search_game(topic),
                ephemeral=False,
            )
        except Exception as e:
            self.logger.error(f"Error searching for chainly game: {e}")
            _ = await ctx.respond(
                "Es gab einen Fehler bei der Suche nach dem Spiel.",
                ephemeral=True
            )



def setup(bot: discord.Bot) -> None:
    logger = logging.getLogger("bot")
    bot.add_cog(ChainlyService(bot, logger))
