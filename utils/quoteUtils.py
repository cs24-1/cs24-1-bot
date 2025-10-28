from discord import Embed, Color
from discord.utils import utcnow

def build_quote_embed(messages, author_name=None):
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