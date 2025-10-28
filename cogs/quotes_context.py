import os
import asyncio
from logging import Logger
from datetime import timedelta
from dotenv import load_dotenv

from utils.quoteUtils import build_quote_embed
from utils.constants import Constants

from discord import message_command, user_command, ApplicationContext, Message, User, Color, Embed, Forbidden
from discord.utils import utcnow
from discord.ext import commands

load_dotenv()

QUOTE_CHANNEL_ID = int(os.getenv("QUOTE_CHANNEL_ID"))
# This does not need a Database because quotes only need to be kept temporarily (in RAM)
# collected_quotes structure:
# { user_id (int): { "messages": [Message, ...], "expires": datetime } }
collected_quotes = {}
EXPIRATION_MINUTES = 10


class QuotesContext(commands.Cog):
    def __init__(self, bot: commands.Bot, logger: Logger):
        self.bot: commands.Bot = bot
        self.logger: Logger = logger

    @message_command(name="Quote Message", guild_ids=[Constants.SERVER_IDS.CUR_SERVER])
    async def quote_message_context(self, ctx: ApplicationContext, message: Message):
        """Fügt eine Nachricht zur persönlichen Quote-Liste hinzu (läuft automatisch ab)."""
        user_id = ctx.author.id
        now = utcnow()

        # Alte abgelaufene löschen
        expired = [uid for uid, data in collected_quotes.items() if data["expires"] < now]
        for uid in expired:
            del collected_quotes[uid]

        if user_id not in collected_quotes:
            collected_quotes[user_id] = {"messages": [], "expires": now + timedelta(minutes=EXPIRATION_MINUTES)}

        collected_quotes[user_id]["messages"].append(message)
        collected_quotes[user_id]["expires"] = now + timedelta(minutes=EXPIRATION_MINUTES)

        await ctx.respond(
            f"📌 Nachricht von **{message.author.display_name}** gespeichert!\n"
            f"({len(collected_quotes[user_id]['messages'])} gesammelt – verfällt in {EXPIRATION_MINUTES} Minuten)\n\n"
            f"**Tipp:** Rechtsklick auf **dich selbst → Apps → Send Saved Quotes**, um sie zu posten.",
            ephemeral=True
        )

    # ---------------------------------------------------------
    @user_command(name="Send Saved Quotes", guild_ids=[Constants.SERVER_IDS.CUR_SERVER])
    async def send_saved_quotes_context(self, ctx: ApplicationContext, user: User):
        """Sendet die gespeicherten Quotes des angegebenen Users."""
        if user.id != ctx.author.id:
            await ctx.respond("❌ Du kannst nur deine eigenen gespeicherten Zitate senden.", ephemeral=True)
            return

        quote_channel = ctx.guild.get_channel(QUOTE_CHANNEL_ID)
        if not quote_channel:
            await ctx.respond("❌ Quote-Channel nicht gefunden.", ephemeral=True)
            return

        data = collected_quotes.pop(user.id, None)
        if not data or not data["messages"]:
            await ctx.respond("⚠️ Du hast keine gespeicherten Zitate.", ephemeral=True)
            return

        await ctx.respond(
            "Möchtest du einen Kommentar **über deinem Embed** hinzufügen? "
            "Schreibe innerhalb von 60 Sekunden oder `skip`, um keinen zu setzen.",
            ephemeral=True
        )

        def check(m):
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=60)
            comment = None if msg.content.lower() == "skip" else msg.content
            try:
                await msg.delete(delay=1)  # automatisch löschen
            except Forbidden:
                pass
        except asyncio.TimeoutError:
            comment = None

        embed = build_quote_embed(data["messages"], ctx.author.display_name)

        # Kommentar steht jetzt **über** dem Embed
        if comment:
            await quote_channel.send(content=f"💬 {comment}", embed=embed)
        else:
            await quote_channel.send(embed=embed)

        await ctx.respond(f"✅ {len(data['messages'])} Quote{'s' if len(data['messages']) > 1 else ''} gepostet!", ephemeral=True)

    # ---------------------------------------------------------
    async def cleanup_expired_quotes(self):
        """
        Periodically remove expired entries from the module-level collected_quotes mapping.

        This coroutine runs forever as a background task. Every iteration it:
        - obtains the current UTC time via utcnow(),
        - finds all keys in collected_quotes whose data["expires"] is before the current time,
        - deletes those keys from collected_quotes,
        - then sleeps for 60 seconds before repeating.
        """
        while True:
            now = utcnow()
            expired = [uid for uid, data in list(collected_quotes.items()) if data["expires"] < now]
            for uid in expired:
                del collected_quotes[uid]
            await asyncio.sleep(60)

    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info("📦 Cog 'QuotesContext' ready.")
        self.bot.loop.create_task(self.cleanup_expired_quotes())


def setup(bot):
    bot.add_cog(QuotesContext(bot, bot.logger))