"""
Unit tests for models/mensa/mensaModels.py
"""

import pytest

from models.mensa.mensaModels import MealType, Price


class TestPrice:
    """Tests for the Price dataclass"""

    def test_price_str_formatting(self):
        """Test that price is formatted correctly as German currency."""
        price = Price(5.50)
        assert str(price) == "5,50 €"

    def test_price_str_formatting_whole_number(self):
        """Test price formatting for whole numbers."""
        price = Price(10.0)
        assert str(price) == "10,00 €"

    def test_price_equality(self):
        """Test price equality comparison."""
        price1 = Price(5.50)
        price2 = Price(5.50)
        price3 = Price(6.00)

        assert price1 == price2
        assert price1 != price3

    def test_price_less_than(self):
        """Test price less than comparison."""
        price1 = Price(5.50)
        price2 = Price(6.00)

        assert price1 < price2
        assert not price2 < price1

    def test_price_greater_than(self):
        """Test price greater than comparison."""
        price1 = Price(6.00)
        price2 = Price(5.50)

        assert price1 > price2
        assert not price2 > price1

    def test_price_from_string_comma_separator(self):
        """Test parsing price from string with comma as decimal separator."""
        price = Price.get_from_string("5,50\xa0€")
        assert price.value == 5.50

    def test_price_from_string_different_values(self):
        """Test parsing various price strings."""
        price1 = Price.get_from_string("10,00\xa0€")
        assert price1.value == 10.0

        price2 = Price.get_from_string("3,75\xa0€")
        assert price2.value == 3.75


class TestMealType:
    """Tests for the MealType enum"""

    def test_meal_type_enum_values(self):
        """Test that all meal types have correct German names."""
        assert MealType.VEGAN.value == "Veganes Gericht"
        assert MealType.VEGETARIAN.value == "Vegetarisches Gericht"
        assert MealType.MEAT.value == "Fleischgericht"
        assert MealType.FISH.value == "Fischgericht"
        assert MealType.PASTA.value == "Pastateller"

    def test_meal_type_enum_count(self):
        """Test that we have all expected meal types."""
        assert len(MealType) == 5
