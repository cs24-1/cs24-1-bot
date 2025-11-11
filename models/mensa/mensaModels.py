from dataclasses import dataclass
from enum import Enum

import discord


class MealType(Enum):
    VEGAN = "Veganes Gericht"
    VEGETARIAN = "Vegetarisches Gericht"
    MEAT = "Fleischgericht"
    FISH = "Fischgericht"
    PASTA = "Pastateller"


@dataclass
class Price:
    value: float

    def __str__(self):
        return f"{f'{self.value:.2f}'.replace('.',',')} €"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Price):
            return self.value == other.value
        return False

    def __lt__(self, other: object) -> bool:
        if isinstance(other, Price):
            return self.value < other.value
        return NotImplemented

    def __gt__(self, other: object) -> bool:
        if isinstance(other, Price):
            return self.value > other.value
        return NotImplemented

    @staticmethod
    def get_from_string(price: str):
        return Price(float(price.split("\xa0")[0].replace(",", ".")))


@dataclass
class Meal:
    mealType: MealType
    mealName: str
    mealComponents: set[str]
    mealPrice: Price
    mealAllergens: set[str]

    def create_embed(self) -> discord.Embed:
        joined_meal_components = ", ".join(sorted(self.mealComponents))

        joined_allergens = ", ".join(sorted(self.mealAllergens))

        footer = f"{self.mealPrice}"
        if joined_allergens:
            footer += f" • {joined_allergens}"

        embed = discord.Embed(title=self.mealName, color=0x00ff00)

        embed.set_author(name=self.mealType.value)

        embed.add_field(
            name="Zutaten",
            value=joined_meal_components or "Keine Angaben",
            inline=False,
        )
        embed.add_field(
            name="Preis",
            value=str(self.mealPrice),
            inline=True,
        )
        embed.add_field(
            name="Allergene",
            value=joined_allergens or "Keine Angaben",
            inline=True,
        )

        return embed
