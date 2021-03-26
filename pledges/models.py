from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Action(models.Model):
    """Action model.

    The corresponding table stores data for the available actions that can be pledged.
    """

    class Meta:
        """Meta class for the ``Action`` model.

        The ``unique_together`` attribute enforces a ``unique constraint``
        for combinations of ``action`` and ``version`` attributes on the database.
        Therefore we could not have two of the same ``action``s with the same ``version``.
        """

        unique_together = ["action", "version"]

    action = models.CharField(max_length=128)
    question_text = models.TextField()
    co2_formula = models.CharField(max_length=512, null=True)
    water_formula = models.CharField(max_length=512, null=True)
    waste_formula = models.CharField(max_length=512, null=True)
    version = models.CharField(max_length=128)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        """String representation of the model."""
        return self.action


class Pledge(models.Model):
    """Pledge model.

    The corresponding table stores pledges made by users.
    The pledge table links a user to an action.

    The users responses to the questions for the action are available
    through the action's ``content_object`` attribute.
    """

    class Meta:
        """Meta class for the ``Pledge`` model.

        The ``unique_together`` attribute enforces a ``unique constraint``
        for combinations of ``user`` and ``action`` objects on the database.
        Therefore a user cannot make a pledge towards an action while the user
        has an existing pledge towards that action.
        """

        unique_together = ["user", "action"]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.ForeignKey(Action, on_delete=models.CASCADE)

    def get_formula(self, formula):
        """Get the string representation of a formula as it is stored in the database.

        :param formula: The formula needed to calculate a specific metric.
        :ptype formula: str.

        :return: The required formula.
        :rtype: str.
        """
        return getattr(self.action, formula, None)

    def execute_formula(self, formula):
        """Calculate the result of the formula.

        This method recursively executes the formula and returns a float rounded to a maximum
        of three decimal places.

        :param formula: The formula split into a list.
        :ptype formula: list.

        :return: The result of executing the formula.
        :rtype: float.
        """
        if len(formula) == 1:
            return float(formula[0])
        else:
            if formula[1] == "*":
                return round(float(formula[0]) * self.execute_formula(formula[2:]), 3)
            elif formula[1] == "/":
                return round(float(formula[0]) / self.execute_formula(formula[2:]), 3)
            elif formula[1] == "+":
                return round(float(formula[0]) + self.execute_formula(formula[2:]), 3)
            elif formula[1] == "-":
                return round(float(formula[0]) - self.execute_formula(formula[2:]), 3)

    def calculate_savings(self, formula):
        """Execute the formula returned from the ``get_formula`` method.

        :param formula: The formula returned by the ``get_formula`` method.
        :ptype formula: str.

        :return: The result of executing the formula.
        :rtype: float.
        """
        formula = self.get_formula(formula)
        if formula:
            for question, answer in self.action.content_object.answers.items():
                if question in formula:
                    formula = formula.replace(question, str(answer))

            return self.execute_formula(formula.split())

    @property
    def co2_saving(self):
        """Calculate the amount of CO2 this pledge will save.

        :return: A float value of the amount of CO2 that will be saved.
        :rtype: float.
        """
        return self.calculate_savings("co2_formula")

    @property
    def water_saving(self):
        """Calculate the amount of water this pledge will save.

        :return: A float value of the amount of water that will be saved.
        :rtype: float.

        """
        return self.calculate_savings("water_formula")

    @property
    def waste_saving(self):
        """Calculate the amount of waste this pledge will save.

        :return: A float value of the amount of waste that will be saved.
        :rtype: float.
        """
        return self.calculate_savings("waste_formula")

    @property
    def version(self):
        """Return the version of the action that the user pledged towards.

        :return: The version of the action that the pledge is towards.
        :rtype: str.
        """
        return self.action.version


class FoodPledge(models.Model):
    """User data for a pledge that aims to replace meat based food with vegetarian based food.

    The corresponding table is specific to one action and should not be used for other actions even
    if they are very similar.

    When a user pledges to complete the associated action they will be asked a few questions.
    The user responses will be stored via this model. This data is accessible via the ``Pledge``
    object that will be created when the user pledges to complete the associated action.
    """

    CHOICES = [
        (2.5, "0"),
        (2.5, "1"),
        (2.5, "2"),
        (2.5, "3"),
        (2.5, "4"),
        (2.5, "5"),
        (3.0, "6"),
    ]

    question_id = models.CharField(max_length=128)
    pledge_id = models.ForeignKey(Pledge, on_delete=models.CASCADE)
    current_meals = models.IntegerField()
    vegetarian_meals = models.DecimalField(
        max_digits=3, decimal_places=2, choices=CHOICES
    )

    def __str__(self):
        """String representation of the model."""
        return f"Current meals: {self.current_meals}, vegetarian meals: {self.vegetarian_meals}"

    @property
    def answers(self):
        """Return the answers a user gave when they pledged."""
        return {
            "current_meals": self.current_meals,
            "vegetarian_meals": self.vegetarian_meals,
        }


class EnergyPledge(models.Model):
    """User data for a pledge that aims to reduce the amount CO2 expelled into the atmosphere by
    changing energy suppliers to one that is more environmentally friendly.

    The corresponding table is specific to one action and should not be used for other actions even
    if they are very similar.

    When a user pledges to complete the associated action they will be asked a few questions.
    The user responses will be stored via this model. This data is accessible via the ``Pledge``
    object that will be created when the user pledges to complete the associated action.
    """

    ENERGY_SUPPLIER_CHOICES = [
        (0.5, "bog_standard"),
        (0.0, "green_supplier"),
    ]

    HEATING_SOURCE_CHOICES = [(5.0, "gas or oil"), (3.0, "electricity")]

    question_id = models.CharField(max_length=128)
    pledge_id = models.ForeignKey(Pledge, on_delete=models.CASCADE)
    energy_supplier = models.DecimalField(
        max_digits=3, decimal_places=2, choices=ENERGY_SUPPLIER_CHOICES
    )
    number_of_people = models.IntegerField()
    heating_source = models.DecimalField(
        max_digits=3, decimal_places=2, choices=HEATING_SOURCE_CHOICES
    )

    def __str__(self):
        """String representation of the model."""
        return f"Energy supplier: {self.energy_supplier}"

    @property
    def answers(self):
        """Return the answers a user gave when they pledged."""
        return {
            "energy_supplier": self.energy_supplier,
            "number_of_people": self.number_of_people,
            "heating_source": self.heating_source,
        }
