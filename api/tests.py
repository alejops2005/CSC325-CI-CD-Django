"""Behavioral tests for the public Django REST Framework API."""
from django.test import SimpleTestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient


class PublicApiTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()

    def test_hello_returns_expected_json(self):
        response = self.client.get(reverse("hello"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(
            response.json(),
            {
                "message": "Hello from CSC 325!",
                "course": "CSC 325",
                "module": 8,
            },
        )

    def test_health_reports_ok(self):
        response = self.client.get(reverse("health"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    @override_settings(APP_REVISION="test-revision-123")
    def test_health_reports_configured_revision(self):
        response = self.client.get(reverse("health"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["revision"], "test-revision-123")

    def test_hello_rejects_post(self):
        response = self.client.post(reverse("hello"), {}, format="json")
        self.assertEqual(response.status_code, 405)

    def test_health_rejects_post(self):
        response = self.client.post(reverse("health"), {}, format="json")
        self.assertEqual(response.status_code, 405)

    def test_missing_route_returns_404(self):
        response = self.client.get("/api/does-not-exist/")
        self.assertEqual(response.status_code, 404)
