"""
This module provides utility functions for fetching and processing the mensa plan using the OpenMensa API.
Functions:
    get_mensa_plan(date: datetime) -> Iterator[Meal]:
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

from models.mensa.mensaModels import Meal, MealType, Price

from utils.cacheUtils import timed_cache
from utils.constants import Constants


@timed_cache(30)
def get_mensa_plan(date: datetime) -> Iterator[Meal]:
    """
    Fetches the mensa plan for a given date using the OpenMensa API.

    Args:
        date (datetime): The date for which to fetch the mensa plan.

    Returns:
        iter: An iterator of Meal objects representing the meals available on the given date.
    """
    url = Constants.URLS.OPENMENSA_API.format(date=date.strftime('%Y-%m-%d'))
    response = requests.get(url)
    
    if response.status_code != 200:
        return
    
    meals_data = response.json()
    
    for meal_data in meals_data:
        # Extract meal information from API response
        category = meal_data.get('category', '')
        name = meal_data.get('name', '')
        notes = meal_data.get('notes', [])
        prices = meal_data.get('prices', {})
        
        # Get student price (fallback to employees, then others)
        price_value = prices.get('students') or prices.get('employees') or prices.get('others')
        
        if not name or not category or price_value is None:
            continue
        
        # Map API category to MealType enum
        try:
            meal_type = MealType(category)
        except ValueError:
            # Skip meals with unknown categories
            continue
        
        # Create Price object
        price = Price(price_value)
        
        # Join notes as components
        components = ', '.join(notes) if notes else None
        
        yield Meal(meal_type, name, components, price)



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
