"""
Unit tests for models/mensa/mensaModels.py
"""

import pytest

from models.mensa.mensaModels import MealType, Price


class TestPrice:
    """Tests for the Price dataclass"""

    @pytest.mark.parametrize(
        "value,expected_str",
        [
            (5.50,
             "5,50 €"),
            (10.0,
             "10,00 €"),
            (3.75,
             "3,75 €"),
            (0.99,
             "0,99 €"),
        ],
    )
    def test_price_str_formatting(self, value, expected_str):
        """Test that price is formatted correctly as German currency."""
        price = Price(value)
        assert str(price) == expected_str

    @pytest.mark.parametrize(
        "value1,value2,expected_equal",
        [
            (5.50,
             5.50,
             True),
            (5.50,
             6.00,
             False),
            (10.0,
             10.0,
             True),
        ],
    )
    def test_price_equality(self, value1, value2, expected_equal):
        """Test price equality comparison."""
        price1 = Price(value1)
        price2 = Price(value2)
        assert (price1 == price2) == expected_equal

    @pytest.mark.parametrize(
        "value1,value2",
        [
            (5.50,
             6.00),
            (3.00,
             10.00),
            (0.99,
             1.00),
        ],
    )
    def test_price_less_than(self, value1, value2):
        """Test price less than comparison."""
        price1 = Price(value1)
        price2 = Price(value2)
        assert price1 < price2
        assert not price2 < price1

    @pytest.mark.parametrize(
        "value1,value2",
        [
            (6.00,
             5.50),
            (10.00,
             3.00),
            (1.00,
             0.99),
        ],
    )
    def test_price_greater_than(self, value1, value2):
        """Test price greater than comparison."""
        price1 = Price(value1)
        price2 = Price(value2)
        assert price1 > price2
        assert not price2 > price1

    @pytest.mark.parametrize(
        "price_str,expected_value",
        [
            ("5,50\xa0€",
             5.50),
            ("10,00\xa0€",
             10.0),
            ("3,75\xa0€",
             3.75),
        ],
    )
    def test_price_from_string(self, price_str, expected_value):
        """Test parsing price from string with comma as decimal separator."""
        price = Price.get_from_string(price_str)
        assert price.value == expected_value


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
