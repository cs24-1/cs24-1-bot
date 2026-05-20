import logging

import discord
from discord.ext import commands
from discord.utils import basic_autocomplete

from utils.constants import Constants
from utils.translateUtils import (
    TranslationResult,
    get_supported_languages,
    languages_autocomplete,
    translate_text,
)

"""
start: /chainly topic: some_topic 

input: search channel chat for single string messages ending with 3 dots e.g. ("Lieber...")
loop:
input: string, one word (enforce no space)
output: all the words as a string with spaces between
break loop if input terminates with dot (. ...) e.g. ("Herr. ...")
break outputs full sentence as message. 

"""

class MessageTranslateService(commands.Cog):
    """
    Discord Cog for translating custom text and selected messages.
    """

    def __init__(self, bot: discord.Bot, logger: logging.Logger) -> None:
        self.bot = bot
        self.logger = logger

    @commands.Cog.listener("on_ready")
    async def on_ready(self) -> None:
        """
        Log when the cog has been loaded successfully.
        """
        self.logger.info("MessageTranslateService started successfully")

    @commands.slash_command(
        name="chainly",
        description="Startet das chainly Spiel",
        guild_ids=[Constants.SERVER_IDS.CUR_SERVER],
    )
    @discord.option(
        "topic",
        description="Das Thema für das chainly Spiel (z.B. 'Beschwerdeschreiben', 'Lebenslauf', etc.).",
        type=discord.SlashCommandOptionType.string,
        required=True,
    )
    @discord.option(
        "target_language",
        description="Zielsprache (z.B. 'deutsch' oder 'de').",
        type=discord.SlashCommandOptionType.string,
        autocomplete=basic_autocomplete(languages_autocomplete()),
        required=True,
    )
    async def translate_command(
        self,
        ctx: discord.ApplicationContext,
        text: str,
        target_language: str
    ) -> None:
        """
        Slash command to translate custom text.
        """
        try:
            result = await translate_text(text, target_language)
        except ValueError as ex:
            await ctx.respond(f"❌ {ex}", ephemeral=True)
            return
        except Exception as ex:
            self.logger.error("Translate command failed: %s", ex)
            await ctx.respond(
                "❌ Übersetzung fehlgeschlagen. Versuche es später erneut.",
                ephemeral=True,
            )
            return

        await ctx.respond(
            embed=self._build_translation_embed(result),
            ephemeral=True
        )

    @discord.message_command(
        name="Übersetzen (de)",
        guild_ids=[Constants.SERVER_IDS.CUR_SERVER]
    )
    async def translate_message_command(
        self,
        ctx: discord.ApplicationContext,
        message: discord.Message
    ) -> None:
        """
        Message context menu command to translate the content of a message.
        """
        await ctx.defer(ephemeral=True)

        if not message.content.strip():
            await ctx.respond(
                "❌ Diese Nachricht enthält keinen Text.",
                ephemeral=True
            )
            return

        try:
            result = await translate_text(message.content, "de")
        except Exception as ex:
            self.logger.error("Message translation failed: %s", ex)
            await ctx.respond(
                "❌ Übersetzung fehlgeschlagen. Versuche es später erneut.",
                ephemeral=True,
            )
            return

        await ctx.respond(
            embed=self._build_translation_embed(result),
            ephemeral=True
        )

    def _build_translation_embed(
        self,
        result: TranslationResult
    ) -> discord.Embed:
        """
        Create a consistent translation response embed.
        """
        embed = discord.Embed(title="🌍 Übersetzung", color=discord.Color.blue())

        embed.add_field(
            name=f"Original ({result.src_lang})",
            value=result.original_text[:1024] or "-",
            inline=False,
        )
        embed.add_field(
            name=f"Übersetzt ({result.target_lang})",
            value=result.translated_text[:1024] or "-",
            inline=False,
        )
        return embed


def setup(bot: discord.Bot) -> None:
    logger = logging.getLogger("bot")
    bot.add_cog(MessageTranslateService(bot, logger))
