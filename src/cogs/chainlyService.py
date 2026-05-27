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
        description=(
            "Das Thema für das chainly Spiel "
            "(z.B. 'Beschwerdeschreiben', 'Lebenslauf', etc.)"
        ),
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
                ephemeral=False,
            )
        except Exception as e:
            self.logger.error(
                "Error starting chainly game: %s",
                e,
                exc_info=True,
            )
            _ = await ctx.respond(
                "Es gab einen Fehler beim Starten des Spiels.", ephemeral=True
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
            self.logger.error(
                "Error searching for chainly game: %s",
                e,
                exc_info=True,
            )
            _ = await ctx.respond(
                "Es gab einen Fehler bei der Suche nach dem Spiel.", ephemeral=True
            )

    @commands.slash_command(
        name="chainly_help",
        description="Erklärt die Regeln von Chainly",
        guild_ids=[Constants.SERVER_IDS.CUR_SERVER],
    )
    async def chainly_help_command(self, ctx: discord.ApplicationContext) -> None:
        """
        Slash command to explain the chainly game rules.
        """

        message = (
            "Chainly ist ein Wortketten‑Spiel. Starte mit `/chainly` und "
            "einem Thema.\n"
            "Anschließend schreibt jede*r der Reihe nach genau ein Wort "
            "als eigene Nachricht, wobei jede teilnehmende Nachricht "
            "entweder mit `...` (fortführend) oder mit `.` "
            "(abschließend) enden muss.\n"
            "Sobald eine Nachricht mit `.` gesendet wird, endet das Spiel "
            "und das Ergebnis wird ausgegeben. "
            f"Alternativ wird das Spiel nach "
            f"{Constants.CHAINLY.GAME_TIMEOUT_SECS // 60} Minuten "
            "abgebrochen und verworfen.\n"
            "Abgeschlossene Spiele kannst du mit `/chainly_search` "
            "finden."
        )

        try:
            _ = await ctx.respond(message, ephemeral=False)
        except Exception as exc:
            self.logger.error("Error sending chainly help: %s", exc, exc_info=True)
            _ = await ctx.respond(
                "Es gab einen Fehler beim Anzeigen der Hilfe.",
                ephemeral=True,
            )


def setup(bot: discord.Bot) -> None:
    logger = logging.getLogger("bot")
    bot.add_cog(ChainlyService(bot, logger))
