import pytest

from django.test import Client


@pytest.mark.django_db
class TestViews:
    """Tests for the views."""
    client = Client()

    def test_home_view(self, pledge):
        """Test ``home_view``."""
        pledge(True)
        response = self.client.get("/")
        assert response.status_code == 200

        assert response.context["amount_of_pledges"] == 1
        assert response.context["total_co2_savings"] == 1.2
        assert response.context["total_water_savings"] == 2.0
        assert response.context["total_waste_savings"] == 13.5

    def test_search_view_existing_user(self, pledge):
        """Test ``search_view`` with an existing user."""
        pledge(True)
        response = self.client.get("/search/?user=test_user")
        assert response.status_code == 200

        assert response.context["pledges"][0]["username"] == "test_user"
        assert response.context["pledges"][0]["action"] == "test action"
        assert response.context["pledges"][0]["co2_saving"] == 1.2
        assert response.context["pledges"][0]["water_saving"] == 2.0
        assert response.context["pledges"][0]["waste_saving"] == 13.5

    def test_non_existent_user(self):
        """Test ``search_view`` with an non-existent user."""
        response = self.client.get("/search/?user=fake_user")
        assert response.status_code == 200

        assert not response.context["pledges"]
