import asyncio
from datetime import datetime, time
import logging
import discord
from discord import ApplicationContext, Bot, TextChannel, SlashCommandOptionType
from discord.ext import commands, tasks
from discord.abc import Messageable
from utils import timetableUtils
from utils.constants import Constants
from utils.holidayUtils import is_holiday

MAX_TIMETABLE_RANGE_DAYS = 30


class Timetable(commands.Cog):
    """A Discord cog that provides commands to view the class timetable.
    
    This cog allows users to fetch and display class schedules for different time periods
    using slash commands. It integrates with the Campus Dual system to provide up-to-date
    timetable information.
    """

    def __init__(self, bot: Bot, logger: logging.Logger) -> None:
        self.bot = bot
        self.logger = logger

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Warm cache and start background refresh when bot is ready.
        """
        if not self.refresh_timetable_cache.is_running():
            self.refresh_timetable_cache.start()

        if not self.send_daily_timetable.is_running():
            self.send_daily_timetable.start()

        self.logger.info("TimetableService started successfully")

    @commands.slash_command(
        name="timetable",
        description=
        "Sieh dir den Stundenplan für `today`, `tomorrow` oder die nächsten `n` Tage an",
        guild_ids=[Constants.SERVER_IDS.CUR_SERVER]
    )
    @discord.option(
        "argument",
        type=SlashCommandOptionType.string,
        description=
        f"`today`, `tomorrow`, Oder eine Zahl (1-{MAX_TIMETABLE_RANGE_DAYS}). Standard ist 7",
        required=False,
        default="7"
    )
    async def timetable(self, ctx: ApplicationContext, argument: str):
        """Fetch and display the class timetable.

        This command allows users to view the class schedule for different
        time periods. Users can request the schedule for today, tomorrow, or
        any number of upcoming days (max. 30).
        """
        await ctx.defer()  # Defer response in case the request takes time

        try:
            # --- Argument logic ---
            if argument == "?":
                response = (
                    "ℹ️ **Verfügbare Befehle:**\n\n"
                    "`/timetable today`\n"
                    "→ Zeigt den Stundenplan für **heute**.\n\n"
                    "`/timetable tomorrow`\n"
                    "→ Zeigt den Stundenplan für **morgen**.\n\n"
                    "`/timetable`\n"
                    "→ Zeigt den Stundenplan für die **nächsten 7 Tage**.\n\n"
                    "`/timetable <number>`\n"
                    "→ Zeigt den Stundenplan für die "
                    f"**nächsten `<number>` Tage** (max. {MAX_TIMETABLE_RANGE_DAYS})."
                )
            elif argument.lower() == "today":
                response = timetableUtils.get_timetable(days=0)
            elif argument.lower() == "tomorrow":
                response = timetableUtils.get_timetable(days=1)
            elif argument.isdigit():
                days = int(argument)
                if days <= 0 or days > MAX_TIMETABLE_RANGE_DAYS:
                    await ctx.respond(
                        f"❌ Bitte gib eine Zahl zwischen 1 und {MAX_TIMETABLE_RANGE_DAYS} ein."
                    )
                    return
                response = timetableUtils.get_timetable(days=days)
            else:
                response = f"❌ Ungültiger Parameter: {argument or ' - '}. Benutze 'today', 'tomorrow', oder eine Zahl (1-{MAX_TIMETABLE_RANGE_DAYS})."

            await self.send_long_message(ctx, response)

        except Exception as e:
            self.logger.error("Unhandled error in /timetable: %s", e)
            await ctx.respond(f"❌ Unbehandelter Fehler: {e}")

    @tasks.loop(time=time(hour=6, minute=0, tzinfo=Constants.SYSTIMEZONE))
    async def send_daily_timetable(self):
        """Sends daily timetable message, skips weekends & holidays."""
        await self.bot.wait_until_ready()

        today = datetime.now(tz=Constants.SYSTIMEZONE).date()
        channel: TextChannel = self.bot.get_channel(
            Constants.CHANNEL_IDS.TIMETABLE_CHANNEL
        )  # type: ignore

        if not channel:
            self.logger.error("Channel not found - timetable post failed.")
            return

        if today.weekday() >= 5:
            self.logger.info("⏭ Weekend - skipping timetable post.")
            return

        if is_holiday(today):
            self.logger.info("⏭ Holiday - skipping timetable post.")
            return

        self.logger.info("Sending timetable for %s...", today.isoformat())
        timetable_text = timetableUtils.get_timetable(days=0)
        await self.send_long_message(channel, timetable_text)

    @send_daily_timetable.before_loop
    async def before_daily_timetable_task(self):
        """Ensure bot is ready before the loop starts."""
        await self.bot.wait_until_ready()
        self.logger.info("Daily timetable task initialized.")

    @tasks.loop(minutes=60)
    async def refresh_timetable_cache(self):
        """Periodically refresh Campus Dual cache in background every 60 minutes."""
        await asyncio.to_thread(
            timetableUtils.warm_timetable_cache,
            True  # do force refresh
        )
        self.logger.info("Timetable cache refreshed successfully")

    async def send_long_message(
        self,
        target: ApplicationContext | Messageable,
        text: str
    ) -> None:
        """Split messages into 2000-character chunks."""
        chunks = [text[i:i + 2000] for i in range(0, len(text), 2000)]
        for i, chunk in enumerate(chunks):
            if isinstance(target, ApplicationContext):
                if i == 0:
                    await target.respond(chunk)
                else:
                    await target.followup.send(chunk)
            else:
                await target.send(chunk)


def setup(bot: Bot):
    logger = logging.getLogger("bot")
    bot.add_cog(Timetable(bot, logger))
