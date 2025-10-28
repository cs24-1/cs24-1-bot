import os
import asyncio
from logging import Logger
from pathlib import Path
from datetime import datetime, timedelta

from dotenv import load_dotenv
from utils.constants import Constants

from discord import commands, message_command, user_command, ApplicationContext, Message, User, Color, Embed, Forbidden
from discord.utils import utcnow
from discord.ext import commands

load_dotenv()

QUOTE_CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

collected_quotes = {}
EXPIRATION_MINUTES = 10


class QuotesContext(commands.Cog):
    def __init__(self, bot: commands.Bot, logger: Logger):
        self.bot: commands.Bot = bot
        self.logger: Logger = logger

    # ---------------------------------------------------------
    # Einheitliches Embed
    # ---------------------------------------------------------
    def build_quote_embed(self, messages, author_name=None):
        embed = Embed(color=Color.blurple())

        for msg in messages:
            content = msg.content[:1024] if msg.content else "[- kein Text -]"
            embed.add_field(
                name=f"~ {msg.author.display_name}",
                value=f'“{content}”\n[Originalnachricht]({msg.jump_url})',
                inline=False
            )

        if author_name:
            embed.set_footer(text=f"Eingereicht von {author_name}")

        embed.timestamp = utcnow()
        return embed

    # ---------------------------------------------------------
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

        embed = self.build_quote_embed(data["messages"], ctx.author.display_name)

        # Kommentar steht jetzt **über** dem Embed
        if comment:
            await quote_channel.send(content=f"💬 {comment}", embed=embed)
        else:
            await quote_channel.send(embed=embed)

        await ctx.respond(f"✅ {len(data['messages'])} Quote{'s' if len(data['messages']) > 1 else ''} gepostet!", ephemeral=True)

    # ---------------------------------------------------------
    async def cleanup_expired_quotes(self):
        while True:
            now = utcnow()
            expired = [uid for uid, data in collected_quotes.items() if data["expires"] < now]
            for uid in expired:
                del collected_quotes[uid]
            await asyncio.sleep(60)

    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info("📦 Cog 'QuotesContext' ready.")
        self.bot.loop.create_task(self.cleanup_expired_quotes())


def setup(bot):
    bot.add_cog(QuotesContext(bot))