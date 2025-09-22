"""
This module provides utility functions for fetching and processing the mensa plan.
Functions:
    get_mensa_plan(date: datetime) -> list[Meal]:
    get_next_mensa_day(current_date: datetime) -> datetime:
    get_last_mensa_day(current_date: datetime) -> datetime:
    check_if_mensa_is_open(current_date: datetime) -> bool:
    get_mensa_open_days() -> list[str]:
    mensa_day_autocomplete(ctx: discord.AutocompleteContext) -> list[str]:
"""

from datetime import datetime, timedelta
from typing import Iterator

import discord

import requests
import bs4
from bs4 import BeautifulSoup

from models.mensa.mensaModels import Meal, MealType, Price

from utils.cacheUtils import timed_cache
from utils.constants import Constants, MensaSelectors


@timed_cache(30)
def get_mensa_plan(date: datetime) -> Iterator[Meal]:
    """
    Fetches the mensa plan for a given date.

    Args:
        date (datetime): The date for which to fetch the mensa plan.

    Returns:
        iter: An iterator of Meal objects representing the meals available on the given date.
    """
    page = requests.get(
        f"{Constants.URLS.MENSAPLAN}{date.strftime('%Y-%m-%d')}"
    )
    soup = BeautifulSoup(page.content, "html.parser")

    for meal_element in soup.select(MensaSelectors.MEAL_CONTAINER):
        meal_type_element = meal_element.select_one(MensaSelectors.MEAL_TYPE)
        meal_price_element = meal_element.select_one(MensaSelectors.MEAL_PRICE)

        if not meal_type_element or not meal_price_element:
            continue

        # bs4 has a bug where it sometimes select the correct div, sometimes the parent div.
        # So the .text not always returns only the needed text, but sometimes more. To fix this,
        # we split the text by double spaces and take the first part.
        meal_type = MealType(meal_type_element.text.split("  ")[0].strip())
        meal_price = Price.get_from_string(meal_price_element.text.strip())

        if meal_type is not MealType.PASTA:
            meal = retrieve_standard_meal_data(
                meal_type,
                meal_element,
                meal_price
            )
            if meal:
                yield meal
            continue

        # TODO: Currently there is no pasta available, so i can only fix this once there is pasta again
        for pasta_element in meal_element.select(MensaSelectors.PASTA_SUBITEM):
            meal = extract_pasta_meal_data(meal_type, pasta_element, meal_price)
            if meal:
                yield meal


def extract_pasta_meal_data(
    meal_type: MealType,
    pasta_element: bs4.Tag,
    meal_price: Price
) -> None | Meal:
    meal_name_element = pasta_element.select_one(MensaSelectors.PASTA_NAME)

    if not meal_name_element:
        return None

    meal_name = meal_name_element.text
    meal_components = None  # TODO maybe there are components, but i can not find them
    meal_price = meal_price

    meal = Meal(meal_type, meal_name, meal_components, meal_price)
    return meal


def retrieve_standard_meal_data(
    meal_type: MealType,
    meal_element: bs4.Tag,
    meal_price: Price,
) -> Meal | None:
    meal_name_element = meal_element.select_one(MensaSelectors.MEAL_NAME)
    meal_components_element = meal_element.select_one(
        MensaSelectors.MEAL_COMPONENTS
    )

    if not meal_name_element:
        return None

    meal_name = meal_name_element.text

    meal_components = meal_components_element.text if meal_components_element else None

    return Meal(meal_type, meal_name, meal_components, meal_price)


def get_next_mensa_day(current_date: datetime) -> datetime:
    """
    Calculates the next open mensa day based on the current date.

    Args:
        current_date (datetime): The current date.

    Returns:
        datetime: The next open mensa day.
    """
    # Mensa is closed on weekends
    if current_date.weekday() == 4:
        return current_date + timedelta(days=3)
    elif current_date.weekday() == 5:
        return current_date + timedelta(days=2)
    else:
        return current_date + timedelta(days=1)


def get_last_mensa_day(current_date: datetime) -> datetime:
    """
    Calculates the last open mensa day based on the current date.

    Args:
        current_date (datetime): The current date.

    Returns:
        datetime: The last open mensa day.
    """
    # Mensa is closed on weekends
    if current_date.weekday() == 0:
        return current_date - timedelta(days=3)
    elif current_date.weekday() == 6:
        return current_date - timedelta(days=2)
    else:
        return current_date - timedelta(days=1)


def check_if_mensa_is_open(current_date: datetime) -> bool:
    """
    Checks if the mensa is open on the given date.

    Args:
        current_date (datetime): The date to check.

    Returns:
        bool: True if the mensa is open, False otherwise.
    """
    if current_date.weekday() >= 5:
        return False

    if current_date.date() < datetime.now().date():
        return False

    if current_date.date() > (datetime.now() + timedelta(days=7)).date():
        return False

    return True


def get_mensa_open_days() -> list[str]:
    """
    Returns a list of all open mensa days for the next week.

    Returns:
        list[str]: A list of all open mensa days for the next week.
    """
    current_date = datetime.now()
    open_days: list[str] = []

    for _ in range(7):
        if check_if_mensa_is_open(current_date):
            open_days.append(current_date.strftime('%d.%m.%Y'))
        current_date += timedelta(days=1)

    return open_days


def format_weekday_in_german(date: datetime) -> str:
    """
    Converts a given date's weekday to its German equivalent.

    Args:
        date (datetime): The date object from which to extract the weekday.

    Returns:
        str: The German name of the weekday corresponding to the given date.
    """
    weekday = date.strftime('%A')
    return {
        'Monday': 'Montag',
        'Tuesday': 'Dienstag',
        'Wednesday': 'Mittwoch',
        'Thursday': 'Donnerstag',
        'Friday': 'Freitag',
        'Saturday': 'Samstag',
        'Sunday': 'Sonntag',
    }.get(weekday,
          weekday)


async def mensa_day_autocomplete(ctx: discord.AutocompleteContext) -> list[str]:
    """
    Autocompletes the mensa days for the mensa command.

    Args:
        ctx (discord.AutocompleteContext): The context of the autocomplete.

    Returns:
        list[str]: A list of all open mensa days for the next week.
    """
    return [day for day in get_mensa_open_days() if day.startswith(ctx.value)]
