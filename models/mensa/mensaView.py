from datetime import datetime

import discord.ui

from models.mensa.mensaModels import Meal
from utils import mensaUtils
from utils.mensaUtils import get_mensa_plan


class MensaView(discord.ui.View):

    def __init__(self, current_date: datetime):
        super().__init__()
        self.current_date = current_date

        # disable last_day button if yesterday the mensa was closed
        if mensaUtils.check_if_mensa_is_open(
            mensaUtils.get_last_mensa_day(self.current_date)
        ):
            self.last_day.disabled = False  # type: ignore
        else:
            self.last_day.disabled = True  # type: ignore

        # disable next_day button if tomorrow the mensa is closed
        if mensaUtils.check_if_mensa_is_open(
            mensaUtils.get_next_mensa_day(self.current_date)
        ):
            self.next_day.disabled = False  # type: ignore
        else:
            self.next_day.disabled = True  # type: ignore

    @discord.ui.button(emoji="⬅️")
    async def last_day(
        self,
        button: discord.ui.Button["MensaView"],
        interaction: discord.Interaction
    ):
        last_date = mensaUtils.get_last_mensa_day(self.current_date)
        self.current_date = last_date

        meals: list[Meal] = get_mensa_plan(self.current_date)

        await interaction.response.edit_message(
            content=mensaUtils.get_mensa_message_title(self.current_date),
            embeds=[meal.create_embed() for meal in meals],
            view=MensaView(self.current_date)
        )

    @discord.ui.button(emoji="➡️")
    async def next_day(
        self,
        button: discord.ui.Button["MensaView"],
        interaction: discord.Interaction
    ):
        next_date = mensaUtils.get_next_mensa_day(self.current_date)
        self.current_date = next_date

        meals: list[Meal] = get_mensa_plan(self.current_date)

        await interaction.response.edit_message(
            content=mensaUtils.get_mensa_message_title(self.current_date),
            embeds=[meal.create_embed() for meal in meals],
            view=MensaView(self.current_date)
        )
