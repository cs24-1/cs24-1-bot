from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass, field

import discord
from discord import Member
from thefuzz import fuzz

from models.database.chainlyModel import ChainlyGame as ChainlyGameModel
from models.database.chainlyModel import ChainlyParticipation
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
        return f"Es läuft gerade noch ein Spiel mit dem Thema: {game.topic}."

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
                timeout=5.0,  # allow exiting during inactivity
            )
        except asyncio.TimeoutError:
            continue
        except asyncio.CancelledError:
            return

        if not isinstance(message.author, Member):
            continue

        if not _is_current_game(channel_id, game):
            return

        if _is_game_end_line(message):
            game.participants.add(message.author)
            game.words.append(
                message.content.removesuffix(Constants.CHAINLY.GAME_END_SUFFIX)
            )
            await _end_game_orderly(bot, channel_id, game)
            return

        if _is_game_line(message):
            game.participants.add(message.author)
            game.words.append(
                message.content.removesuffix(Constants.CHAINLY.GAME_WORD_SUFFIX)
            )


def _is_game_line(message: discord.Message) -> bool:
    return bool(re.match(Constants.CHAINLY.GAME_WORD_REGEX, message.content))


def _is_game_end_line(message: discord.Message) -> bool:
    return bool(re.match(Constants.CHAINLY.GAME_END_REGEX, message.content))


def _is_game_message(message: discord.Message, channel_id: int) -> bool:
    """Check whether a given message should be considered part of the game."""
    is_human = not message.author.bot
    posted_in_game_channel = message.channel.id == channel_id
    one_word_long = len(message.content.strip().split()) == 1
    is_valid_game_line = _is_game_line(message) or _is_game_end_line(message)

    return (
        posted_in_game_channel
        and is_human
        and one_word_long
        and is_valid_game_line
    )


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

    try:
        channel = bot.get_channel(channel_id)
        if channel is not None:
            game_result = _format_game_result(
                topic=current_game.topic,
                result=" ".join(current_game.words),
                participants=[p.mention for p in current_game.participants],
            )
            _ = await channel.send(f"Spiel beendet!\n{game_result}")

        await save_game(current_game)
    finally:
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
        await ChainlyParticipation.create(game=completed_game, user=user)

    return completed_game


async def search_game(topic: str) -> str:
    """Search for a finished game and return game-result or error message."""

    games: list[tuple[int, ChainlyGameModel]] = [
        (fuzz.token_set_ratio(topic, game.topic), game)
        for game in await ChainlyGameModel.all()
    ]

    filtered_games: list[tuple[int, ChainlyGameModel]]
    filtered_games = [(ratio, game) for ratio, game in games if ratio > 50]

    if len(filtered_games) == 0:
        return f"Kein abgeschlossenes Spiel mit dem Thema '{topic}' gefunden"

    # extract game object of max ratio
    result_game = max(filtered_games, key=lambda g: g[0])[1]
    await result_game.fetch_related("participants__user")
    participants: list[DatabaseUser] = [
        participation.user for participation in result_game.participants
    ]

    return _format_game_result(
        result_game.topic,
        result_game.result,
        participants=[user.global_name for user in participants],
    )


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

    try:
        channel = bot.get_channel(channel_id)
        if channel is not None:
            await channel.send(
                f"Das Spiel zum Thema '{current_game.topic}' ist abgelaufen."
            )
    finally:
        active_games.pop(channel_id, None)
        LOGGER.info("Ended chainly game in channel %s due to timeout", channel_id)


def _format_game_result(topic: str, result: str, participants: list[str]) -> str:
    return f"""- Thema: {topic}
- Teilnehmende: {', '.join(participants)}

> {result}"""


def _is_current_game(channel_id: int, game: ChainlySession) -> bool:
    return active_games.get(channel_id) is game


def _is_game_active(channel_id: int) -> bool:
    return channel_id in active_games
