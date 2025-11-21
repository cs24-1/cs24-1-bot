"""
Unit tests for utils/mensaUtils.py
"""
import re
from datetime import datetime, timedelta
from typing import Any

import pytest

from models.mensa.mensaModels import MealType
from utils.mensaUtils import (
    check_if_mensa_is_open,
    extract_normal_meals,
    get_last_mensa_day,
    get_mensa_open_days
)


class TestGetNextMensaDay:
    """Tests for get_next_mensa_day function"""

    @pytest.mark.parametrize(
        "input_date,expected_weekday,expected_days_diff",
        [
            (datetime(2024, 1, 1), 1, 1),  # Monday -> Tuesday
            (datetime(2024, 1, 2), 2, 1),  # Tuesday -> Wednesday
            (datetime(2024, 1, 3), 3, 1),  # Wednesday -> Thursday
            (datetime(2024, 1, 4), 4, 1),  # Thursday -> Friday
            (datetime(2024, 1, 5), 0, 3),  # Friday -> Monday (skip weekend)
            (datetime(2024, 1, 6), 0, 2),  # Saturday -> Monday
        ],
    )
    def test_get_next_mensa_day(
        self,
        input_date: datetime,
        expected_weekday: int,
        expected_days_diff: int
    ):
        """Test getting next mensa day from various days."""
        from utils.mensaUtils import get_next_mensa_day

        next_day = get_next_mensa_day(input_date)
        assert next_day.weekday() == expected_weekday
        assert (next_day - input_date).days == expected_days_diff


class TestGetLastMensaDay:
    """Tests for get_last_mensa_day function"""

    @pytest.mark.parametrize(
        "input_date,expected_weekday,expected_days_diff",
        [
            (datetime(2024, 1, 2), 0, 1),  # Tuesday -> Monday
            (datetime(2024, 1, 3), 1, 1),  # Wednesday -> Tuesday
            (datetime(2024, 1, 4), 2, 1),  # Thursday -> Wednesday
            (datetime(2024, 1, 5), 3, 1),  # Friday -> Thursday
            (datetime(2024, 1, 8), 4, 3),  # Monday -> Friday (skip weekend)
        ],
    )
    def test_get_last_mensa_day(
        self,
        input_date: datetime,
        expected_weekday: int,
        expected_days_diff: int
    ):
        """Test getting previous mensa day from various days."""
        last_day = get_last_mensa_day(input_date)
        assert last_day.weekday() == expected_weekday
        assert (input_date - last_day).days == expected_days_diff


class TestCheckIfMensaIsOpen:
    """Tests for check_if_mensa_is_open function"""

    def test_mensa_is_closed_on_weekend(self):
        """Test that mensa is closed on weekends."""
        # Test with a future Saturday
        future_saturday = datetime.now() + timedelta(days=30)
        # Adjust to Saturday
        days_until_saturday = (5 - future_saturday.weekday()) % 7
        saturday = future_saturday + timedelta(days=days_until_saturday)

        assert check_if_mensa_is_open(saturday) is False

        # Test with a future Sunday
        sunday = saturday + timedelta(days=1)
        assert check_if_mensa_is_open(sunday) is False

    def test_mensa_is_closed_for_past_dates(self):
        """Test that mensa is closed for past dates."""
        # Yesterday
        yesterday = datetime.now() - timedelta(days=1)
        assert check_if_mensa_is_open(yesterday) is False

    def test_mensa_is_closed_for_far_future(self):
        """Test that mensa is closed for dates more than 7 days ahead."""
        # 10 days in the future
        far_future = datetime.now() + timedelta(days=10)
        assert check_if_mensa_is_open(far_future) is False


class TestGetMensaOpenDays:
    """Tests for get_mensa_open_days function"""

    def test_get_mensa_open_days_returns_list(self):
        """Test that get_mensa_open_days returns a list."""
        open_days = get_mensa_open_days()
        assert isinstance(open_days, list)
        # Should return weekdays within next 7 days
        assert len(open_days) >= 1

    def test_get_mensa_open_days_format(self):
        """Test that get_mensa_open_days returns dates in correct format."""
        open_days = get_mensa_open_days()
        # Check date format DD.MM.YYYY
        date_pattern = re.compile(r'^\d{2}\.\d{2}\.\d{4}$')
        for day in open_days:
            assert date_pattern.match(
                day
            ), f"Date {day} doesn't match format DD.MM.YYYY"


class TestExtractNormalMeals:
    """Tests for extract_normal_meals function"""

    def test_extract_normal_meals_valid_data(self):
        """Test extracting normal meals from valid data."""
        meals_data: list[dict[str, Any]]
        meals_data = [
            {
                "category": "Veganes Gericht",
                "name": "Vegane Bowl",
                "notes": ["glutenfrei"],
                "prices": {
                    "students": 3.50
                }
            },
            {
                "category": "Fleischgericht",
                "name": "Schnitzel",
                "notes": ["Schwein"],
                "prices": {
                    "students": 4.50
                }
            }
        ]

        meals = list(extract_normal_meals(meals_data))
        assert len(meals) == 2
        assert meals[0].mealType == MealType.VEGAN
        assert meals[0].mealName == "Vegane Bowl"
        assert meals[1].mealType == MealType.MEAT
        assert meals[1].mealName == "Schnitzel"

    def test_extract_normal_meals_filters_invalid(self):
        """Test that invalid meals are filtered out."""
        meals_data: list[dict[str, Any]]
        meals_data = [
            {
                "category": "Veganes Gericht",
                "name": "Valid Meal",
                "notes": [],
                "prices": {
                    "students": 3.50
                }
            },
            {
                # Missing price
                "category": "Fleischgericht",
                "name": "No Price",
                "notes": []
            },
            {
                # Missing name
                "category": "Fischgericht",
                "notes": [],
                "prices": {
                    "students": 4.50
                }
            },
            {
                # Invalid category
                "category": "Invalid Category",
                "name": "Invalid",
                "notes": [],
                "prices": {
                    "students": 2.50
                }
            }
        ]

        meals = list(extract_normal_meals(meals_data))
        # Only the first meal should be valid
        assert len(meals) == 1
        assert meals[0].mealName == "Valid Meal"
