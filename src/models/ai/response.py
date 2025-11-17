from dataclasses import dataclass

import discord


@dataclass
class CodeTranslateResponse:
    detected_language: str
    translated_language: str
    translated_code: list[str]
    humorous_comment: str
    tokens_used: int

    async def create_embed(
        self,
        author: discord.User | discord.Member,
        remaining_usage: int
    ) -> discord.Embed:
        """
        Create a Discord embed for the translated code.

        :returns: The created embed.
        """

        embed = discord.Embed(
            description=
            f"```{'\n'.join(self.translated_code)}```\n\n-# {self.humorous_comment}"
        )
        embed.set_footer(
            text=
            f"von @{author.display_name} ({author.global_name}) ({self.tokens_used} Tokens verwendet)"
        )
        embed.set_author(name=get_usage(remaining_usage))
        embed.title = f"{self.detected_language} auf {self.translated_language}"

        return embed


def get_usage(remaining_usage: int) -> str:
    """
    Get the emoji and text for the remaining usage of the AI.

    :param remaining_usage: The remaining usage of the AI.
    :returns: The remaining usage message.
    """

    if remaining_usage > 2:
        return f"🟢 (noch {remaining_usage})"
    elif remaining_usage > 0:
        return f"🟡 (noch {remaining_usage})"
    return "🔴 (keine mehr)"
