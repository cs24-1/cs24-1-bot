import discord
from discord.ext import commands
from pathlib import Path
from dotenv import load_dotenv
import os
import asyncio
from datetime import datetime, timedelta

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

GUILD_ID = int(os.getenv("GUILD_ID"))
QUOTE_CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

collected_quotes = {}
EXPIRATION_MINUTES = 10


class quotes_context(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ---------------------------------------------------------
    # Einheitliches Embed
    # ---------------------------------------------------------
    def build_quote_embed(self, messages, author_name=None):
        embed = discord.Embed(color=discord.Color.blurple())

        for msg in messages:
            content = msg.content[:1024] if msg.content else "[– kein Text –]"
            embed.add_field(
                name=f"~ {msg.author.display_name}",
                value=f'“{content}”\n[Originalnachricht]({msg.jump_url})',
                inline=False
            )

        if author_name:
            embed.set_footer(text=f"Eingereicht von {author_name}")

        embed.timestamp = discord.utils.utcnow()
        return embed

    # ---------------------------------------------------------
    @discord.message_command(name="Quote Message", guild_ids=[GUILD_ID])
    async def quote_message_context(self, ctx: discord.ApplicationContext, message: discord.Message):
        """Fügt eine Nachricht zur persönlichen Quote-Liste hinzu (läuft automatisch ab)."""
        user_id = ctx.author.id
        now = datetime.utcnow()

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
    @discord.user_command(name="Send Saved Quotes", guild_ids=[GUILD_ID])
    async def send_saved_quotes_context(self, ctx: discord.ApplicationContext, user: discord.User):
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
            except discord.Forbidden:
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
            now = datetime.utcnow()
            expired = [uid for uid, data in collected_quotes.items() if data["expires"] < now]
            for uid in expired:
                del collected_quotes[uid]
            await asyncio.sleep(60)

    @commands.Cog.listener()
    async def on_ready(self):
        print("📦 Cog 'QuotesContext' ready.")
        self.bot.loop.create_task(self.cleanup_expired_quotes())


def setup(bot):
    bot.add_cog(quotes_context(bot))