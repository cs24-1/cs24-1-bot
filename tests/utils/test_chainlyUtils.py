"""Unit tests for chainly utility functions."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from utils import chainlyUtils


@pytest.fixture(autouse=True)
def clear_active_games() -> None:
    """Clear active game state before and after each test."""
    chainlyUtils.active_games.clear()
    yield
    chainlyUtils.active_games.clear()


class TestTryStartGame:
    """Test cases for starting chainly games."""

    @pytest.mark.asyncio
    async def test_starts_game_and_schedules_background_tasks(
        self,
        mock_bot: MagicMock
    ) -> None:
        """Test that a new game is created and background tasks are started."""
        with patch(
            "utils.chainlyUtils._run_game_loop",
            new_callable=AsyncMock
        ) as mock_run_loop, patch(
            "utils.chainlyUtils._end_game_after_timeout",
            new_callable=AsyncMock
        ) as mock_end_after_timeout:
            response = await chainlyUtils.try_start_game(mock_bot, 100, "Python")

        assert "wurde gestartet" in response
        assert 100 in chainlyUtils.active_games
        assert chainlyUtils.active_games[100].topic == "Python"
        assert mock_run_loop.call_count == 1
        assert mock_end_after_timeout.call_count == 1

    @pytest.mark.asyncio
    async def test_returns_message_when_game_is_already_active(
        self,
        mock_bot: MagicMock
    ) -> None:
        """Test that an existing game blocks creating another one."""
        chainlyUtils.active_games[100] = chainlyUtils.ChainlySession(topic="Alt")

        response = await chainlyUtils.try_start_game(mock_bot, 100, "Neu")

        assert "Es läuft gerade noch ein Spiel" in response
        assert "Alt" in response
        assert chainlyUtils.active_games[100].topic == "Alt"


class TestMessageValidation:
    """Test cases for chainly message recognition."""

    def test_is_game_message_accepts_human_single_word_in_channel(self) -> None:
        """Test acceptance for valid game messages."""
        message = MagicMock()
        message.author.bot = False
        message.channel.id = 55
        message.content = "hallo..."

        assert chainlyUtils._is_game_message(message, 55) is True

    @pytest.mark.parametrize(
        ("is_bot", "channel_id", "content"),
        [
            (True, 10, "hallo..."),
            (False, 11, "hallo..."),
            (False, 10, "zwei worte..."),
        ],
    )
    def test_is_game_message_rejects_invalid_messages(
        self,
        is_bot: bool,
        channel_id: int,
        content: str
    ) -> None:
        """Test rejection rules for invalid messages."""
        message = MagicMock()
        message.author.bot = is_bot
        message.channel.id = channel_id
        message.content = content

        assert chainlyUtils._is_game_message(message, 10) is False

    def test_is_game_word_and_end_regex(self) -> None:
        """Test message suffix matching for word and ending tokens."""
        word_message = MagicMock()
        word_message.content = "ende..."
        end_message = MagicMock()
        end_message.content = "stop."

        assert chainlyUtils._is_game_word(word_message) is True
        assert chainlyUtils._is_game_end(end_message) is True


class TestGameEnding:
    """Test cases for game shutdown and persistence flow."""

    @pytest.mark.asyncio
    async def test_end_game_orderly_sends_result_and_persists(
        self,
        mock_bot: MagicMock
    ) -> None:
        """Test orderly game completion sends result and stores data."""
        participant = MagicMock()
        participant.mention = "@Alice"
        game = chainlyUtils.ChainlySession(topic="Thema")
        game.participants.add(participant)
        game.words.extend(["Ein", "Satz"])
        chainlyUtils.active_games[77] = game

        channel = MagicMock()
        channel.send = AsyncMock()
        mock_bot.get_channel.return_value = channel

        with patch(
            "utils.chainlyUtils.save_game",
            new_callable=AsyncMock
        ) as mock_save_game:
            await chainlyUtils._end_game_orderly(mock_bot, 77, game)

        mock_save_game.assert_awaited_once_with(game)
        channel.send.assert_awaited_once()
        sent_text = channel.send.await_args.args[0]
        assert "Spiel beendet!" in sent_text
        assert "Thema" in sent_text
        assert "@Alice" in sent_text
        assert 77 not in chainlyUtils.active_games

    @pytest.mark.asyncio
    async def test_end_game_after_timeout_sends_timeout_message(
        self,
        mock_bot: MagicMock
    ) -> None:
        """Test timeout handling notifies channel and clears active game."""
        game = chainlyUtils.ChainlySession(topic="TimeoutThema")
        chainlyUtils.active_games[23] = game

        channel = MagicMock()
        channel.send = AsyncMock()
        mock_bot.get_channel.return_value = channel

        with patch("utils.chainlyUtils.asyncio.sleep", new_callable=AsyncMock):
            await chainlyUtils._end_game_after_timeout(mock_bot, 23, game)

        channel.send.assert_awaited_once()
        sent_text = channel.send.await_args.args[0]
        assert "abgelaufen" in sent_text
        assert "TimeoutThema" in sent_text
        assert 23 not in chainlyUtils.active_games


class TestSearchGame:
    """Test cases for finished-game search."""

    @pytest.mark.asyncio
    async def test_search_game_returns_not_found_message(self) -> None:
        """Test user feedback when no matching games are found."""
        with patch(
            "utils.chainlyUtils.ChainlyGameModel.all",
            new=AsyncMock(return_value=[]),
        ):
            response = await chainlyUtils.search_game("unbekannt")

        assert response == "Found no chainly games for topic 'unbekannt'"

    @pytest.mark.asyncio
    async def test_search_game_returns_best_matching_game_result(self) -> None:
        """Test result formatting for the closest matching finished game."""
        best_game = MagicMock()
        best_game.topic = "python"
        best_game.result = "ich mag python."
        best_game.fetch_related = AsyncMock()
        best_game.participants = [
            SimpleNamespace(user=SimpleNamespace(global_name="Alice"))
        ]

        other_game = MagicMock()
        other_game.topic = "hockey"
        other_game.result = "go team."
        other_game.fetch_related = AsyncMock()
        other_game.participants = []

        with patch(
            "utils.chainlyUtils.ChainlyGameModel.all",
            new=AsyncMock(return_value=[other_game, best_game]),
        ):
            response = await chainlyUtils.search_game("python")

        best_game.fetch_related.assert_awaited_once_with("participants__user")
        assert "- Thema: python" in response
        assert "Alice" in response
        assert "ich mag python." in response
