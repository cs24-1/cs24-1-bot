from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass, field

import discord
from discord import Member

from models.database.chainlyModel import ChainlyGame as ChainlyGameModel
from models.database.chainlyModel import (
    ChainlyParticipation,
)
from models.database.userData import User as DatabaseUser
from utils.constants import Constants

LOGGER = logging.getLogger(__name__)

active_games: dict[int, ChainlySession] = {}


@dataclass
class ChainlySession:
    topic: str
    participants: set[Member] = field(default_factory=set)
    words: list[str] = field(default_factory=list)


async def try_start_game(bot: discord.Bot, channel_id: int, topic: str) -> str:
    """Try to start a new game and schedule its timeout."""

    if _is_game_active(channel_id):
        game = active_games[channel_id]
        return (
            f"Es läuft gerade noch ein Spiel mit dem Thema: {game.topic}. "
            "Du kannst teilnehmen oder es abbrechen."
        )

    game = ChainlySession(topic=topic)
    active_games[channel_id] = game
    asyncio.create_task(_run_game_loop(bot, channel_id, game))
    asyncio.create_task(_end_game_after_timeout(bot, channel_id, game))

    return (
        f"Spiel mit dem Thema '{topic}' wurde gestartet! "
        f"(Läuft ab in {Constants.CHAINLY.GAME_TIMEOUT_SECS // 60}m)"
    )


async def _run_game_loop(
    bot: discord.Bot,
    channel_id: int,
    game: ChainlySession,
) -> None:
    """Process chainly messages for an active game in the background."""

    while _is_current_game(channel_id, game):
        try:
            message: discord.Message = await bot.wait_for(
                "message",
                check=lambda message: _is_game_message(message, channel_id),
            )
        except asyncio.CancelledError:
            return

        if not isinstance(message.author, Member):
            continue

        if not _is_current_game(channel_id, game):
            return

        if _is_game_end(message):
            # TODO: finish game
            game.participants.add(message.author)
            game.words.append(
                message.content.removesuffix(Constants.CHAINLY.GAME_END_SUFFIX)
            )
            await _end_game_orderly(bot, channel_id, game)
            return

        if _is_game_word(message):
            # TODO: modify game state
            game.participants.add(message.author)
            game.words.append(
                message.content.removesuffix(Constants.CHAINLY.GAME_WORD_SUFFIX)
            )


def _is_game_word(message: discord.Message) -> bool:
    return bool(re.match(Constants.CHAINLY.GAME_WORD_REGEX, message.content))


def _is_game_end(message: discord.Message) -> bool:
    return bool(re.match(Constants.CHAINLY.GAME_END_REGEX, message.content))


def _is_game_message(message: discord.Message, channel_id: int) -> bool:
    """Check whether a given message should be considered part of the game."""
    is_human = not message.author.bot
    posted_in_game_channel = message.channel.id == channel_id
    one_word_long = len(message.content.split(" ")) == 1

    return posted_in_game_channel and is_human and one_word_long


async def _end_game_orderly(
    bot: discord.Bot,
    channel_id: int,
    game: ChainlySession,
) -> None:
    """End an active game after terminating message."""

    current_game = active_games.get(channel_id)
    if current_game is None:
        return

    if current_game is not game:
        return

    channel = bot.get_channel(channel_id)
    if channel is not None:
        _ = await channel.send(
            f"Spiel beendet!\n- Thema: {current_game.topic}\n- "
            f"teilgenommen hat: {', '.join(p.mention for p in current_game.participants)}\n\n> "
            f"{' '.join(current_game.words)}"
        )

    await save_game(current_game)
    _ = active_games.pop(channel_id, None)


async def save_game(game: ChainlySession) -> ChainlyGameModel:
    """Persist a finished chainly session and its participants."""

    completed_game = await ChainlyGameModel.create(
        topic=game.topic,
        result=" ".join(game.words),
    )

    for participant in game.participants:
        user, _ = await DatabaseUser.get_or_create(
            id=participant.id,
            defaults={
                "global_name": participant.global_name or participant.name,
                "display_name": participant.display_name,
            },
        )
        await ChainlyParticipation.create(game_uuid=completed_game, user=user)

    return completed_game


async def _end_game_after_timeout(
    bot: discord.Bot,
    channel_id: int,
    game: ChainlySession,
) -> None:
    """End an active game after the configured timeout."""

    await asyncio.sleep(Constants.CHAINLY.GAME_TIMEOUT_SECS)

    current_game = active_games.get(channel_id)
    if current_game is None:
        return

    if current_game is not game:
        return

    channel = bot.get_channel(channel_id)
    if channel is not None:
        await channel.send(
            f"Das Spiel zum Thema '{current_game.topic}' ist abgelaufen."
        )

    active_games.pop(channel_id, None)
    LOGGER.info("Ended chainly game in channel %s due to timeout", channel_id)


def _is_current_game(channel_id: int, game: ChainlySession) -> bool:
    return active_games.get(channel_id) is game


def _is_game_active(channel_id: int) -> bool:
    return channel_id in active_games
