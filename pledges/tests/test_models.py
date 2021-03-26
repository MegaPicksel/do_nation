from decimal import Decimal
from unittest.mock import patch

import pytest

from django.contrib.contenttypes.models import ContentType
from django.db.utils import IntegrityError

from pledges.models import Action, EnergyPledge, FoodPledge, Pledge


@pytest.mark.django_db
class TestAction:
    """Test for the ``Action`` model."""

    def test_action(self, action):
        """Test the ``Action`` model."""
        action = action(real_data=False)
        test_action = Action.objects.get(pk=1)

        assert isinstance(test_action, Action)
        assert test_action.action == action.action
        assert test_action.question_text == action.question_text
        assert test_action.co2_formula == action.co2_formula
        assert test_action.water_formula == action.water_formula
        assert test_action.waste_formula == action.waste_formula
        assert test_action.version == action.version

    def test_unique_constraint_action_and_version_combination(self, action):
        """Test that adding two actions with the same ``action`` and ``version``
        causes an ``IntegrityError`` to be raised.
        """
        action = action(real_data=False)
        second_action = Action(
            action="test action",
            question_text="test question",
            co2_formula="0.8 * test_parameter * 0.5",
            water_formula="0.8 * test_parameter * 0.5",
            waste_formula="0.8 * test_parameter * 0.5",
            version="version 1.0",
            content_type=ContentType(id=1),
            object_id=1,
        )
        with pytest.raises(
            IntegrityError,
            match=r"UNIQUE constraint failed: pledges_action.action, pledges_action.version",
        ):
            second_action.save()


@pytest.mark.django_db
class TestPledge:
    """Tests for the ``Pledge`` model."""

    def test_pledge(self, pledge):
        """Test the ``Pledge`` model."""
        pledge = pledge(True)
        test_pledge = Pledge.objects.get(pk=1)

        assert isinstance(test_pledge, Pledge)
        assert test_pledge.action == pledge.action
        assert test_pledge.user == pledge.user
        assert test_pledge.version == pledge.version

        assert test_pledge.action.content_object.question_id == "food pledge"
        assert test_pledge.action.content_object.pledge_id == pledge
        assert test_pledge.action.content_object.current_meals == 5
        assert test_pledge.action.content_object.vegetarian_meals == 3

    def test_get_formula(self, pledge):
        """Test the ``Pledge`` object's ``get_formula`` method."""
        pledge = pledge(True)
        co2_formula = pledge.get_formula("co2_formula")
        assert co2_formula == "0.8 * vegetarian_meals * 0.5"

        water_formula = pledge.get_formula("water_formula")
        assert water_formula == "0.4 * current_meals"

        waste_formula = pledge.get_formula("waste_formula")
        assert waste_formula == "0.9 * current_meals * vegetarian_meals"

    @pytest.mark.parametrize(
        "formula_list, expected_result",
        [
            (["0.8", "*", "6"], 4.8),
            (["0.8", "/", "6"], 0.133),
            (["0.8", "+", "6"], 6.8),
            (["0.8", "-", "6"], -5.2),
            (["0.4", "*", "0.5", "*", "0.2"], 0.04),
            (["0.2", "+", "5", "*", "2"], 10.2),
            (["0.8", "-", "2", "*", "0.3"], 0.2),
            (["6", "/", "3", "*", "2"], 1),
            (["0.2", "+", "6", "/", "2"], 3.2),
            (["10", "/", "5", "/", "0.1"], 0.2),
            (["0.2", "+", "0.5", "+", "2"], 2.7),
            (["0.8", "-", "0.1", "-", "0.3"], 1.0),
            (["0.2", "-", "0.5", "/", "2"], -0.05),
            (["0.8", "*", "6", "/", "2"], 2.4),
        ],
    )
    def test_execute_formula(self, pledge, formula_list, expected_result):
        """Test the ``Pledge`` object's ``calculate`` method."""
        pledge = pledge(True)
        result = pledge.execute_formula(formula_list)
        assert result == expected_result

    @pytest.mark.parametrize(
        "formula, expected_result",
        [
            ("0.8 * 6", 4.8),
            ("0.8 / 6", 0.133),
            ("0.8 + 6", 6.8),
            ("0.8 - 6", -5.2),
            ("0.4 * 0.5 * 0.2", 0.04),
            ("0.2 + 5 * 2", 10.2),
            ("0.8 - 2 * 0.3", 0.2),
            ("6 / 3 * 2", 1),
            ("0.2 + 6 / 2", 3.2),
            ("10 / 5 / 0.1", 0.2),
            ("0.2 + 0.5 + 2", 2.7),
            ("0.8 - 0.1 - 0.3", 1.0),
            ("0.2 - 0.5 / 2", -0.05),
            ("0.8 * 6 / 2", 2.4),
        ],
    )
    def test_calculate_savings(self, pledge, formula, expected_result):
        """Test the ``Pledge`` object's ``execute_formula`` method."""
        p = pledge(True)
        with patch.object(Pledge, "get_formula", return_value=formula):
            result = p.calculate_savings(formula)
            assert result == expected_result

    def test_co2_savings(self, pledge):
        """Test the ``Pledge`` object's ``co2_saving`` attribute."""
        pledge = pledge(True)
        test_pledge = Pledge.objects.get(pk=1)
        assert test_pledge.co2_saving == 1.2

    def test_water_savings(self, pledge):
        """Test the ``Pledge`` object's ``water_saving`` attribute."""
        pledge = pledge(True)
        test_pledge = Pledge.objects.get(pk=1)
        assert test_pledge.water_saving == 2.0

    def test_waste_savings(self, pledge):
        """Test the ``Pledge`` object's ``waste_saving`` attribute."""
        pledge = pledge(True)
        test_pledge = Pledge.objects.get(pk=1)
        assert test_pledge.waste_saving == 13.5

    def test_version(self, pledge):
        """Test the ``Pledge`` object's ``version`` attribute."""
        pledge = pledge(True)
        test_pledge = Pledge.objects.get(pk=1)
        assert test_pledge.version == "version 1.0"

    def test_unique_constraint_user_and_action_combination(self, pledge):
        """Test that adding two pledges with the same ``user`` and ``action``
        causes an ``IntegrityError`` to be raised.
        """
        pledge(True)
        with pytest.raises(
            IntegrityError,
            match=r"UNIQUE constraint failed: pledges_pledge.user_id, pledges_pledge.action_id",
        ):
            pledge(True)


@pytest.mark.django_db
class TestFoodPledge:
    """Tests for the ``FoodPledge`` model."""

    def test_food_pledge(self, action, user, pledge, food_pledge):
        """Test the ``FoodPledge`` model."""
        test_food_pledge = FoodPledge.objects.get(pk=1)

        assert isinstance(test_food_pledge, FoodPledge)
        assert food_pledge.question_id == test_food_pledge.question_id
        assert food_pledge.pledge_id == test_food_pledge.pledge_id
        assert food_pledge.current_meals == test_food_pledge.current_meals
        assert food_pledge.vegetarian_meals == test_food_pledge.vegetarian_meals

        assert food_pledge.answers == {
            "current_meals": Decimal("5"),
            "vegetarian_meals": Decimal("3"),
        }


@pytest.mark.django_db
class TestEnergyPledge:
    """Tests for the ``EnergyPledge`` model."""

    def test_energy_pledge(self, action, user, pledge, energy_pledge):
        """Test the ``EnergyPledge`` model."""
        test_energy_pledge = EnergyPledge.objects.get(pk=1)

        assert isinstance(test_energy_pledge, EnergyPledge)
        assert energy_pledge.question_id == test_energy_pledge.question_id
        assert energy_pledge.pledge_id == test_energy_pledge.pledge_id
        assert energy_pledge.energy_supplier == test_energy_pledge.energy_supplier
        assert energy_pledge.number_of_people == test_energy_pledge.number_of_people
        assert energy_pledge.heating_source == test_energy_pledge.heating_source

        assert energy_pledge.answers == {
            "energy_supplier": Decimal("0.5"),
            "number_of_people": 2,
            "heating_source": Decimal("3"),
        }
