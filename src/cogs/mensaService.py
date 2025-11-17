import logging
from datetime import datetime, time

import discord
from discord import ApplicationContext
from discord.ext import commands, tasks

from models.mensa.mensaModels import Meal
from models.mensa.mensaView import MensaView
from utils import mensaUtils
from utils.constants import Constants


class MensaService(commands.Cog):
    """
    A Discord Cog for managing Mensa-related commands and tasks.
    """

    def __init__(self, bot: discord.Bot, logger: logging.Logger) -> None:
        self.bot = bot
        self.logger = logger

    @commands.Cog.listener("on_ready")
    async def on_ready(self):
        self.send_daily_mensa_message.start()

        self.logger.info("MensaService started successfully")

    @tasks.loop(time=time(hour=6, minute=0, tzinfo=Constants.SYSTIMEZONE))
    async def send_daily_mensa_message(self):
        guild: discord.Guild = self.bot.get_guild(
            Constants.SERVER_IDS.CUR_SERVER
        )  # type: ignore
        channel: discord.TextChannel = guild.get_channel(
            Constants.CHANNEL_IDS.MENSA_CHANNEL
        )  # type: ignore

        current_date: datetime = datetime.now()

        if not mensaUtils.check_if_mensa_is_open(current_date):
            return

        meals: list[Meal] = mensaUtils.get_mensa_plan(current_date)

        await channel.send(
            mensaUtils.get_mensa_message_title(current_date),
            embeds=[meal.create_embed() for meal in meals]
        )

        self.logger.info("Sent daily Mensa message")

    @commands.slash_command(
        name="mensa",
        description="Sieh dir die heutige Mensa-Auswahl an",
        guild_ids=[Constants.SERVER_IDS.CUR_SERVER]
    )
    @discord.option(
        name="date",
        description="Datum für den Mensaplan (Format: DD.MM.YYYY)",
        type=discord.SlashCommandOptionType.string,
        required=False,
        autocomplete=discord.utils.basic_autocomplete(
            mensaUtils.mensa_day_autocomplete
        )
    )
    async def get_mensa_plan(self, ctx: ApplicationContext, date: str | None):
        current_date = self._get_next_mensa_day(date)

        meals: list[Meal] = mensaUtils.get_mensa_plan(current_date)

        await ctx.respond(
            mensaUtils.get_mensa_message_title(current_date),
            embeds=[meal.create_embed() for meal in meals],
            view=MensaView(current_date)
        )

    def _get_next_mensa_day(self, date: str | None) -> datetime:
        if date is None:
            current_date = datetime.now()
        else:
            parsed_date = datetime.strptime(date, "%d.%m.%Y")
            current_date = max(parsed_date, datetime.now())

        if not mensaUtils.check_if_mensa_is_open(current_date):
            current_date = mensaUtils.get_next_mensa_day(current_date)

        return current_date


def setup(bot: discord.Bot):
    logger = logging.getLogger("bot")
    bot.add_cog(MensaService(bot, logger))
