import logging

from discord import ApplicationContext
from discord.ext import commands, tasks
import discord

from models.database.userData import User
from utils.memeUtils import memeUtils
from utils.constants import Constants


class MemeService(commands.Cog):
    """
    A Discord Cog for getting memes and changing the bots banner.
    """

    def __init__(self, bot: discord.Bot, logger: logging.Logger) -> None:
        self.logger = logger
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Starts the set_random_meme_banner task when the bot is ready.
        """
        self.set_random_meme_banner.start()

        self.logger.info("MemeBannerService started successfully")

    @commands.Cog.listener("on_message")
    async def save_memes(self, message: discord.Message):
        """
        Listens for messages in the meme channel and saves them as memes.
        """
        if message.author.bot:
            return

        if message.channel.id != Constants.CHANNEL_IDS.MEME_CHANNEL:
            return

        for attachment in message.attachments:
            if attachment.content_type is None or not attachment.content_type.startswith(
                "image"
            ):
                continue

            user, _ = await User.get_or_create(
                id=str(message.author.id), defaults={
                    "global_name": message.author.name, "display_name": message.author.display_name})

            await memeUtils.save_meme_image(
                self.logger,
                attachment,
                user,
                message.content,
                message.created_at
            )

            self.logger.info(
                "Saved meme %s from %s",
                attachment.filename,
                message.author
            )

    @commands.slash_command(
        name="meme",
        description="Suche nach einem zufälligen Meme",
        guild_ids=[Constants.SERVER_IDS.CUR_SERVER]
    )
    @discord.option(
        "search",
        type=discord.SlashCommandOptionType.string,
        required=False
    )
    async def meme(self, ctx: ApplicationContext, search: str | None = None):
        """
        Searches for a meme matching the search term and sends it in an embed.
        """
        if search is None:
            _, meme = await memeUtils.get_random_meme(False)
        else:
            memes = await memeUtils.search_memes(search, 1)

            if len(memes) == 0:
                await ctx.respond(
                    f"Kein Meme für die Suche `{search}` gefunden!"
                )
                return

            _, meme = memes[0]

        embed, meme_file = await meme.create_embed(search)

        await ctx.respond(embed=embed, file=meme_file)

    @commands.slash_command(
        name="trick",
        description="Suche nach einem zufälligen Trick",
        guild_ids=[Constants.SERVER_IDS.CUR_SERVER]
    )
    async def trick(self, ctx: ApplicationContext):
        await self.meme(ctx, "Trick")

    @tasks.loop(minutes=5)
    async def set_random_meme_banner(self):
        assert self.bot.user is not None
        random_meme, _ = await memeUtils.get_random_meme(True)

        try:
            await self.bot.user.edit(banner=random_meme)
            self.logger.info("Successfully set random meme banner")
        except discord.HTTPException as ex:
            self.logger.error("Failed to set random meme banner %s", ex)


def setup(bot: discord.Bot):
    logger = logging.getLogger("bot")
    bot.add_cog(MemeService(bot, logger))
