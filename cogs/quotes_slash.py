import os
from pathlib import Path
from dotenv import load_dotenv

from discord import slash_command, ApplicationContext, Color, Embed, NotFound, Forbidden, HTTPException
from discord.utils import utcnow
from discord.ext import commands

load_dotenv()

QUOTE_CHANNEL_ID = int(os.getenv("CHANNEL_ID"))


class quotes_slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def build_quote_embed(self, messages, author_name=None):
        embed = Embed(color=Color.blurple())
        for msg in messages:
            content = msg.content[:1024] if msg.content else "[- kein Text -]"
            embed.add_field(
                name=f"~ {msg.author.display_name}",
                value=f"“{content}”\n[Originalnachricht]({msg.jump_url})",
                inline=False
            )
        if author_name:
            embed.set_footer(text=f"Eingereicht von {author_name}")
        embed.timestamp = utcnow()
        return embed

    @slash_command(
        name="quote",
        description="Zitiert eine oder mehrere Nachrichten anhand ihrer IDs.",
    )
    async def quote(
        self,
        ctx: ApplicationContext,
        message_1: str,
        message_2: str = None,
        message_3: str = None,
        message_4: str = None,
        message_5: str = None,
        comment: str = None
    ):
        quote_channel = ctx.guild.get_channel(QUOTE_CHANNEL_ID)
        if not quote_channel:
            await ctx.respond("❌ Quote-Channel nicht gefunden.", ephemeral=True)
            return

        message_ids = [m for m in [message_1, message_2, message_3, message_4, message_5] if m]
        if not message_ids:
            await ctx.respond("⚠️ Gib mindestens eine Nachrichten-ID an.", ephemeral=True)
            return

        found_messages = []
        for mid in message_ids:
            for ch in ctx.guild.text_channels:
                try:
                    msg = await ch.fetch_message(int(mid))
                    found_messages.append(msg)
                    break
                except (NotFound, Forbidden, HTTPException):
                    continue

        if not found_messages:
            await ctx.respond("⚠️ Keine gültigen Nachrichten gefunden.", ephemeral=True)
            return

        embed = self.build_quote_embed(found_messages, ctx.author.display_name)

        if comment:
            await quote_channel.send(content=f"💬 {comment}", embed=embed)
        else:
            await quote_channel.send(embed=embed)

        await ctx.respond(f"✅ {len(found_messages)} Quote{'s' if len(found_messages) > 1 else ''} gepostet!", ephemeral=True)

    @commands.Cog.listener()
    async def on_ready(self):
        print("📦 Cog 'QuotesSlash' ready.")


def setup(bot):
    bot.add_cog(quotes_slash(bot))