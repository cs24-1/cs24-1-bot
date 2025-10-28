import os
from logging import Logger
from dotenv import load_dotenv

from utils.quoteUtils import build_quote_embed
from utils.constants import Constants

from discord import ApplicationContext, slash_command, TextChannel, Message, Embed, Color, NotFound, Forbidden, HTTPException
from discord.utils import utcnow
from discord.ext import commands

load_dotenv()

QUOTE_CHANNEL_ID = int(os.getenv("QUOTE_CHANNEL_ID"))


class QuotesSlash(commands.Cog):
    def __init__(self, bot: commands.Bot, logger: Logger):
        self.bot: commands.Bot = bot
        self.logger: Logger = logger

    @slash_command(
        name="quote",
        description="Zitiert eine oder mehrere Nachrichten anhand ihrer URLs.",
        guild_ids=[Constants.SERVER_IDS.CUR_SERVER]
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
        
        input_messages: list[str] = [message_1, message_2, message_3, message_4, message_5]
        if not any(url and url.strip() for url in input_messages):
            return await ctx.respond("⚠️ Gib mindestens eine gültige Nachrichten-URL an.", ephemeral=True)
        
        found_messages: list[Message] = []

        for url in input_messages:
            if url is None:
                continue
            
            try:
                guild_id = url.split("/")[-3]
                channel_id = url.split("/")[-2]
                message_id = url.split("/")[-1]
            
                if int(guild_id) != Constants.SERVER_IDS.CUR_SERVER:
                    return await ctx.respond("❌ Kann nur Nachrichten aus diesem Server zitieren.")
                
                channel: TextChannel = await self.bot.fetch_channel(int(channel_id))
                message = await channel.fetch_message(int(message_id))
                found_messages.append(message)
            except (NotFound, Forbidden, HTTPException):
                pass
            
        if not found_messages:
            return await ctx.respond("⚠️ Keine gültigen Nachrichten gefunden.", ephemeral=True)
            

        embed = build_quote_embed(found_messages, ctx.author.display_name)

        if comment:
            await quote_channel.send(content=f"💬 {comment}", embed=embed)
        else:
            await quote_channel.send(embed=embed)

        await ctx.respond(f"✅ {len(found_messages)} Quote{'s' if len(found_messages) > 1 else ''} gepostet!", ephemeral=True)

    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info("📦 Cog 'QuotesSlash' ready.")


def setup(bot):
    bot.add_cog(QuotesSlash(bot, bot.logger))