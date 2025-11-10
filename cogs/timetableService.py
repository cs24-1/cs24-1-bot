import asyncio
from datetime import datetime, time
import logging
import discord
from discord import ApplicationContext
from discord.ext import commands, tasks  # tasks for @tasks.loop decorator
import os
import pytz  # type: ignore
import requests

# from utils import timetableUtils
from utils import timetableUtils
from utils.constants import Constants


class Timetable(commands.Cog):
    """A Discord cog that provides commands to view the class timetable.
    
    This cog allows users to fetch and display class schedules for different time periods
    using slash commands. It integrates with the Campus Dual system to provide up-to-date
    timetable information.
    """

    def __init__(self, bot: discord.Bot, logger: logging.Logger) -> None:
        self.bot = bot
        self.logger = logger

    @discord.slash_command(
        name="timetable",
        description=
        "Sieh dir den Stundenplan für `today`, `tomorrow` oder die nächsten `n` Tage an",
        guild_ids=[Constants.SERVER_IDS.CUR_SERVER]
    )
    @discord.option(
        name="argument",
        description="`today`, `tomorrow`, Oder eine Zahl (1-30). Standard ist 7",
        required=False,
        default="7"
    )
    async def timetable(self, ctx: ApplicationContext, argument: str):
        """Fetch and display the class timetable.

        This command allows users to view the class schedule for different time periods.
        Users can request the schedule for today, tomorrow, or any number of upcoming days.

        Args:
            ctx: The Discord application context
            argument: The time period to fetch:
                     - "?" for help
                     - "today" for today's schedule
                     - "tomorrow" for tomorrow's schedule
                     - a number (1-30) for that many upcoming days
                     - defaults to 7 days if not specified
        """
        await ctx.defer()  # Defer response in case the request takes time

        try:
            # --- Argument logic ---
            if argument == "?":
                plan = (
                    "ℹ️ **Available Commands:**\n\n"
                    "`/timetable today`\n"
                    "→ Shows the timetable for **today**.\n\n"
                    "`/timetable tomorrow`\n"
                    "→ Shows the timetable for **tomorrow**.\n\n"
                    "`/timetable`\n"
                    "→ Shows the timetable for the **next 7 days**.\n\n"
                    "`/timetable <number>`\n"
                    "→ Shows the timetable for the next `<number>` days (max. 30)."
                )
            elif argument.lower() == "today":
                plan = timetableUtils.get_timetable(days=0)
            elif argument.lower() == "tomorrow":
                plan = timetableUtils.get_timetable(days=1)
            elif argument.isdigit():
                days = int(argument)
                if days <= 0 or days > 30:
                    await ctx.respond(
                        "❌ Please enter a number between 1 and 30."
                    )
                    return
                plan = timetableUtils.get_timetable(days=days)
            else:
                plan = f"❌ Invalid argument: {argument or ' - '}. Use 'today', 'tomorrow', or a number (1-30)."

            await self.send_long_message(ctx, plan)

        except requests.exceptions.SSLError:
            await ctx.respond(
                "❌ SSL Error: Certificate could not be validated."
            )
        except Exception as e:
            await ctx.respond(f"❌ Unexpected error: {e}")

    @tasks.loop(time=time(hour=6, minute=0, tzinfo=Constants.SYSTIMEZONE))
    async def daily_timetable_task(self):
        """Sends daily timetable message, skips weekends & holidays."""
        await self.bot.wait_until_ready()
        now = datetime.now(tz=Constants.SYSTIMEZONE)
        target_time = now.replace(hour=6, minute=0, second=0, microsecond=0)

        # --- After wake-up: perform the daily action ---
        today = datetime.now(tz=Constants.SYSTIMEZONE).date()
        channel: discord.TextChannel = self.bot.get_channel(
            Constants.CHANNEL_IDS.TIMETABLE_CHANNEL
        )  # type: ignore

        if not channel:
            self.logger.error("Channel not found - timetable post failed.")
            return

        if today.weekday() >= 5:
            self.logger.info("⏭ Weekend - skipping timetable post.")
            return

        if today in Constants.DATES.HOLIDAYS:
            self.logger.info("⏭ Holiday - skipping timetable post.")
            return

        self.logger.info(f"📨 Sending timetable for {today.isoformat()}...")
        timetable_text = timetableUtils.get_timetable(days=0)
        await self.send_long_message(channel, timetable_text)

    @daily_timetable_task.before_loop
    async def before_daily_timetable_task(self):
        """Ensure bot is ready before the loop starts."""
        await self.bot.wait_until_ready()
        self.logger.info("🕕 Daily timetable task initialized.")

    async def send_long_message(
        self,
        target: ApplicationContext | discord.abc.Messageable,
        text: str
    ) -> None:
        """Split messages into 2000-character chunks."""
        chunks = [text[i:i + 2000] for i in range(0, len(text), 2000)]
        for chunk in chunks:
            if isinstance(target, ApplicationContext):
                await target.respond(chunk)
            else:
                await target.send(chunk)

    @commands.Cog.listener()
    async def on_ready(self):
        print("TimetableService started successfully")


def setup(bot: discord.Bot):
    logger = logging.getLogger("bot")
    bot.add_cog(Timetable(bot, logger))
