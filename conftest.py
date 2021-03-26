from decimal import Decimal

import pytest

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from pledges.models import Action, EnergyPledge, FoodPledge, Pledge


@pytest.fixture
def action():
    """Add a test action.
    """
    action = Action(
        action="test action",
        question_text="test question",
        co2_formula="0.8 * test_parameter * 0.5",
        water_formula="0.8 * test_parameter * 0.5",
        waste_formula="0.8 * test_parameter * 0.5",
        version="version 1.0",
        content_type=ContentType(id=1),
        object_id=1,
    )

    def _action(real_data):
        """Updates test action with realistic data if needed.
        """
        if real_data:
            action.co2_formula = "0.8 * vegetarian_meals * 0.5"
            action.water_formula = "0.4 * current_meals"
            action.waste_formula = "0.9 * current_meals * vegetarian_meals"
            action.content_type = ContentType(
                id=3, app_label="pledges | food pledge", model=FoodPledge
            )

        action.save()
        return action

    return _action


@pytest.fixture
def user():
    """Add a test user.
    """
    user = User(username="test_user", password="test password")
    user.save()

    return user


@pytest.fixture
def pledge(user, action):
    """Add a test pledge.
    """
    def _pledge(real_data):
        """Add a food pledge if needed.

        An energy pledge, or any other realistic pledge could be used as well
        as long as the pledge metrics calculations can be executed.
        """
        pledge = Pledge(action=action(real_data), user=user)
        pledge.save()
        if real_data:
            food_pledge = FoodPledge(
                question_id="food pledge",
                pledge_id=pledge,
                current_meals=Decimal("5"),
                vegetarian_meals=Decimal("3"),
            )
            food_pledge.save()
        return pledge

    return _pledge


@pytest.fixture
def food_pledge(pledge):
    """Add a test food pledge.
    """
    food_pledge = FoodPledge(
        question_id="food pledge",
        pledge_id=pledge(False),
        current_meals=Decimal("5"),
        vegetarian_meals=Decimal("3"),
    )
    food_pledge.save()

    return food_pledge


@pytest.fixture
def energy_pledge(pledge):
    """Add a test energy pledge.
    """
    energy_pledge = EnergyPledge(
        question_id="energy pledge",
        pledge_id=pledge(False),
        energy_supplier=Decimal("0.5"),
        number_of_people=2,
        heating_source=Decimal("3"),
    )
    energy_pledge.save()

    return energy_pledge