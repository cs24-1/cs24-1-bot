import logging
from dataclasses import dataclass
from typing import Any

from googletrans import LANGUAGES, Translator

LOGGER = logging.getLogger(__name__)


@dataclass
class TranslationResult:
    "translation result data class"

    original_text: str
    translated_text: str
    src_lang: str
    targ_lang: str


def get_supported_languages() -> list[tuple[str, str]]:
    """
    Return all supported languages as sorted code/name pairs.
    """
    return sorted(
        [(code,
          name) for code,
         name in LANGUAGES.items()],
        key=lambda item: item[0]
    )


def normalize_language(language: str) -> str:
    """
    normalizes language input to a standard format

    
    Accepts either code (de, en) or language name (german, english).
    Raises ValueError if unsupported.
    """

    cleaned = language.strip().lower()

    if cleaned in LANGUAGES:
        return cleaned

    for code, name in LANGUAGES.items():
        if name.lower() == cleaned:
            return code

    raise ValueError(f"Sprache nicht unterstützt: {language}")


async def _translate_async(
    text: str,
    target_code: str,
    source_code: str
) -> Any:
    """
    Async googletrans call extracted for wrapper/testing.
    """
    translator = Translator()
    return await translator.translate(text, dest=target_code, src=source_code)


async def translate_text(
    text: str,
    target_lang: str,
    source_lang: str | None = None
) -> TranslationResult:
    """
    Translate text using googletrans.
    """

    if not text.strip():
        raise ValueError("Der zu übersetzende Text darf nicht leer sein.")

    target_code = normalize_language(target_lang)

    if source_lang is None or source_lang.strip().lower() == "auto":
        source_code = "auto"
    else:
        source_code = normalize_language(source_lang)

    translated = await _translate_async(text, target_code, source_code)

    detected_src = getattr(translated, "src", None) or "unknown"

    LOGGER.info(
        "Translated message from %s to %s (%d chars)",
        detected_src,
        target_code,
        len(text)
    )

    return TranslationResult(
        original_text=text,
        translated_text=translated.text,
        src_lang=detected_src,
        targ_lang=target_code
    )
