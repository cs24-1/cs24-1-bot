"""
Unit tests for utils/translateUtils.py
"""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest


class TestNormalizeLanguage:
    """Tests for normalize_language function."""

    def test_normalize_language_accepts_language_code(self) -> None:
        """Return same value when input is a valid language code."""
        from utils.translateUtils import normalize_language

        assert normalize_language("de") == "de"

    def test_normalize_language_accepts_language_name(self) -> None:
        """Map language names to their language codes."""
        from utils.translateUtils import normalize_language

        assert normalize_language("german") == "de"

    def test_normalize_language_strips_and_lowercases(self) -> None:
        """Normalize whitespace and letter case before mapping."""
        from utils.translateUtils import normalize_language

        assert normalize_language("  ENGLISH  ") == "en"

    def test_normalize_language_raises_for_unsupported_language(self) -> None:
        """Raise ValueError for unsupported languages."""
        from utils.translateUtils import normalize_language

        with pytest.raises(ValueError, match="Sprache nicht unterstützt"):
            normalize_language("klingon")


class TestTranslateAsync:
    """Tests for _translate_async helper."""

    @pytest.mark.asyncio
    async def test_translate_async_awaits_underlying_translator(
        self,
        monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Call Translator.translate with the expected parameters."""
        from utils import translateUtils

        fake_response = SimpleNamespace(src="en", text="Hallo")
        translate_mock = AsyncMock(return_value=fake_response)

        class FakeTranslator:
            """Minimal async translator test double."""

            async def translate(
                self,
                text: str,
                dest: str,
                src: str
            ) -> SimpleNamespace:
                return await translate_mock(text=text, dest=dest, src=src)

        monkeypatch.setattr(translateUtils, "Translator", FakeTranslator)

        response = await translateUtils._translate_async("Hello", "de", "auto")

        assert response.text == "Hallo"
        translate_mock.assert_awaited_once_with(
            text="Hello",
            dest="de",
            src="auto"
        )


class TestTranslateText:
    """Tests for translate_text wrapper."""

    @pytest.mark.asyncio
    async def test_translate_text_rejects_empty_text(self) -> None:
        """Raise ValueError if text contains only whitespace."""
        from utils.translateUtils import translate_text

        with pytest.raises(ValueError, match="Der zu übersetzende Text"):
            await translate_text("   ", "de")

    @pytest.mark.asyncio
    async def test_translate_text_uses_auto_source_by_default(
        self,
        monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Use source language auto when source_lang is omitted."""
        from utils import translateUtils

        fake_response = SimpleNamespace(src="en", text="Hallo Welt")
        translate_async_mock = AsyncMock(return_value=fake_response)

        monkeypatch.setattr(
            translateUtils,
            "_translate_async",
            translate_async_mock
        )

        result = await translateUtils.translate_text("Hello world", "de")

        translate_async_mock.assert_awaited_once_with(
            "Hello world",
            "de",
            "auto"
        )
        assert result.original_text == "Hello world"
        assert result.translated_text == "Hallo Welt"
        assert result.src_lang == "en"
        assert result.target_lang == "de"

    @pytest.mark.asyncio
    async def test_translate_text_uses_explicit_source_language(
        self,
        monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Use normalized source language when source_lang is provided."""
        from utils import translateUtils

        fake_response = SimpleNamespace(src="de", text="Hello")
        translate_async_mock = AsyncMock(return_value=fake_response)

        monkeypatch.setattr(
            translateUtils,
            "_translate_async",
            translate_async_mock
        )

        result = await translateUtils.translate_text(
            "Hallo",
            "english",
            "german"
        )

        translate_async_mock.assert_awaited_once_with("Hallo", "en", "de")
        assert result.src_lang == "de"
        assert result.target_lang == "en"

    @pytest.mark.asyncio
    async def test_translate_text_falls_back_to_unknown_source(
        self,
        monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Use unknown when translator response has no src field."""
        from utils import translateUtils

        fake_response = SimpleNamespace(text="Bonjour")
        translate_async_mock = AsyncMock(return_value=fake_response)

        monkeypatch.setattr(
            translateUtils,
            "_translate_async",
            translate_async_mock
        )

        result = await translateUtils.translate_text("Hello", "french")

        assert result.src_lang == "unknown"
        assert result.target_lang == "fr"
