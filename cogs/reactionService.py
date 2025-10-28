import logging

import discord
from discord.ext import commands
from thefuzz import fuzz  # type: ignore

from models.database.reactionData import ReactionLearning
from utils.constants import Constants


class ReactionService(commands.Cog):
    """
    A Discord Cog that learns from user reactions and suggests
    appropriate reactions for messages.
    """

    def __init__(self, bot: discord.Bot, logger: logging.Logger) -> None:
        self.logger = logger
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Runs when the bot is ready.
        """
        self.logger.info("ReactionService started successfully")

    @commands.Cog.listener("on_raw_reaction_add")
    async def learn_from_reaction(
        self,
        payload: discord.RawReactionActionEvent
    ):
        """
        Learns from user reactions by storing patterns in the database.

        :param payload: The reaction event payload
        """
        # Ignore reactions from bots
        if payload.member and payload.member.bot:
            return

        # Get the channel and message
        channel = self.bot.get_channel(payload.channel_id)
        if not isinstance(channel, discord.TextChannel):
            return

        try:
            message = await channel.fetch_message(payload.message_id)
        except discord.NotFound:
            return
        except discord.Forbidden:
            self.logger.warning(
                "Missing permissions to fetch message in channel %s",
                channel.id
            )
            return

        # Skip if message is too short
        if len(
            message.content
        ) < Constants.REACTION_LEARNING.MESSAGE_LENGTH_MIN:
            return

        # Get the reaction emoji (handle both custom and unicode emojis)
        if payload.emoji.is_custom_emoji():
            reaction_str = f"<:{payload.emoji.name}:{payload.emoji.id}>"
        else:
            reaction_str = str(payload.emoji)

        # Store or update the learning entry
        await self._store_reaction_pattern(
            message.content,
            reaction_str,
            payload.channel_id
        )

        self.logger.debug(
            "Learned reaction '%s' for message in channel %s",
            reaction_str,
            payload.channel_id
        )

    @commands.Cog.listener("on_message")
    async def suggest_reactions(self, message: discord.Message):
        """
        Suggests reactions for new messages based on learned patterns.

        :param message: The message to suggest reactions for
        """
        # Ignore messages from bots
        if message.author.bot:
            return

        # Skip if message is too short
        if len(
            message.content
        ) < Constants.REACTION_LEARNING.MESSAGE_LENGTH_MIN:
            return

        # Get learned reactions that might match this message
        suggestions = await self._find_matching_reactions(
            message.content,
            message.channel.id
        )

        # Add the suggested reactions
        for reaction in suggestions[:Constants.REACTION_LEARNING.
                                    MAX_SUGGESTIONS_PER_MESSAGE]:
            try:
                await message.add_reaction(reaction)
                self.logger.debug(
                    "Suggested reaction '%s' for message %s",
                    reaction,
                    message.id
                )
            except discord.Forbidden:
                self.logger.warning(
                    "Missing permissions to add reaction in channel %s",
                    message.channel.id
                )
                break
            except discord.HTTPException as e:
                self.logger.error(
                    "Failed to add reaction '%s': %s",
                    reaction,
                    e
                )
                continue

    async def _store_reaction_pattern(
        self,
        message_content: str,
        reaction: str,
        channel_id: int
    ):
        """
        Stores or updates a reaction pattern in the database.

        :param message_content: The message content
        :param reaction: The reaction emoji
        :param channel_id: The channel ID
        """
        # Normalize message content (lowercase, strip whitespace)
        normalized_content = message_content.lower().strip()

        # Try to find existing pattern
        existing = await ReactionLearning.filter(
            message_content=normalized_content,
            reaction=reaction,
            channel_id=channel_id
        ).first()

        if existing:
            await existing.increment_count()
        else:
            await ReactionLearning.create(
                message_content=normalized_content,
                reaction=reaction,
                channel_id=channel_id
            )

    async def _find_matching_reactions(
        self,
        message_content: str,
        channel_id: int
    ) -> list[str]:
        """
        Finds reactions that match the message content based on learned
        patterns.

        :param message_content: The message content to match
        :param channel_id: The channel ID
        :returns: List of suggested reaction emojis
        """
        normalized_content = message_content.lower().strip()

        # Get all learned reactions for this channel
        learned_patterns = await ReactionLearning.filter(
            channel_id=channel_id,
            count__gte=Constants.REACTION_LEARNING.MIN_COUNT_THRESHOLD
        ).all()

        # Calculate similarity scores
        matches = []
        for pattern in learned_patterns:
            similarity = fuzz.ratio(
                normalized_content,
                pattern.message_content
            ) / 100.0

            if similarity >= Constants.REACTION_LEARNING.SIMILARITY_THRESHOLD:
                matches.append((pattern.reaction, similarity, pattern.count))

        # Sort by similarity * count (to favor both similar and frequently
        # used reactions)
        matches.sort(key=lambda x: x[1] * x[2], reverse=True)

        # Return just the reaction emojis
        return [match[0] for match in matches]

    @commands.slash_command(
        name="reaction_stats",
        description="Zeige Statistiken über gelernte Reaktionen",
        guild_ids=[Constants.SERVER_IDS.CUR_SERVER]
    )
    async def reaction_stats(self, ctx: discord.ApplicationContext):
        """
        Shows statistics about learned reactions.
        """
        # Get total number of learned patterns
        total_patterns = await ReactionLearning.all().count()

        # Get patterns for this channel
        channel_patterns = await ReactionLearning.filter(
            channel_id=ctx.channel_id
        ).count()

        # Get most common reactions
        all_patterns = await ReactionLearning.all().order_by("-count").limit(5)

        embed = discord.Embed(
            title="📊 Reaktions-Lern-Statistiken",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="Gesamt gelernte Muster",
            value=str(total_patterns),
            inline=True
        )
        embed.add_field(
            name="Muster in diesem Kanal",
            value=str(channel_patterns),
            inline=True
        )

        if all_patterns:
            top_reactions = "\n".join(
                [
                    f"{pattern.reaction} - {pattern.count}x"
                    for pattern in all_patterns
                ]
            )
            embed.add_field(
                name="Top 5 Reaktionen",
                value=top_reactions,
                inline=False
            )

        await ctx.respond(embed=embed)


def setup(bot: discord.Bot):
    logger = logging.getLogger("bot")
    bot.add_cog(ReactionService(bot, logger))
