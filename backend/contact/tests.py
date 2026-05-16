import pytest
from contact.models import ContactMessage


@pytest.fixture
def message(db):
    return ContactMessage.objects.create(
        name="Jan Kowalski",
        email="jan@test.com",
        subject="Zapytanie",
        message="Treść wiadomości testowej.",
    )


@pytest.mark.django_db
class TestContactMessageAPI:
    url = "/api/contact/"

    def test_send_message_anonymous(self, api_client):
        data = {
            "name": "Anna Nowak",
            "email": "anna@test.com",
            "subject": "Wycena",
            "message": "Proszę o wycenę strony.",
        }
        response = api_client.post(self.url, data)
        assert response.status_code == 201
        assert ContactMessage.objects.filter(email="anna@test.com").exists()

    def test_send_message_missing_fields(self, api_client):
        response = api_client.post(self.url, {"name": "Anna"})
        assert response.status_code == 400

    def test_send_message_invalid_email(self, api_client):
        data = {
            "name": "Anna",
            "email": "nie-email",
            "subject": "Test",
            "message": "Treść.",
        }
        response = api_client.post(self.url, data)
        assert response.status_code == 400

    def test_list_messages_admin(self, admin_client, message):
        response = admin_client.get(self.url)
        assert response.status_code == 200
        assert len(response.data["results"]) == 1

    def test_list_messages_forbidden_for_user(self, user_client):
        response = user_client.get(self.url)
        assert response.status_code == 403

    def test_list_messages_forbidden_anonymous(self, api_client):
        response = api_client.get(self.url)
        assert response.status_code == 403

    def test_retrieve_message_admin(self, admin_client, message):
        response = admin_client.get(f"{self.url}{message.pk}/")
        assert response.status_code == 200
        assert response.data["email"] == "jan@test.com"

    def test_mark_read(self, admin_client, message):
        assert message.is_read is False
        response = admin_client.patch(f"{self.url}{message.pk}/mark-read/", {"is_read": True})
        assert response.status_code == 200
        message.refresh_from_db()
        assert message.is_read is True

    def test_mark_read_forbidden_for_user(self, user_client, message):
        response = user_client.patch(f"{self.url}{message.pk}/mark-read/", {"is_read": True})
        assert response.status_code == 403

    def test_delete_message_admin(self, admin_client, message):
        response = admin_client.delete(f"{self.url}{message.pk}/")
        assert response.status_code == 204
        assert not ContactMessage.objects.filter(pk=message.pk).exists()

    def test_delete_message_forbidden_for_user(self, user_client, message):
        response = user_client.delete(f"{self.url}{message.pk}/")
        assert response.status_code == 403
