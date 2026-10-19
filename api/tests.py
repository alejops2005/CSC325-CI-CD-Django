from django.test import SimpleTestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient


class PublicApiTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()

    def test_hello_returns_public_json(self):
        response = self.client.get(reverse("hello"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(response.json()["message"], "Hello from CSC 325!")
        self.assertEqual(response.json()["course"], "CSC 325")
        self.assertEqual(response.json()["module"], 8)

    def test_hello_rejects_post(self):
        response = self.client.post(reverse("hello"), {}, format="json")
        self.assertEqual(response.status_code, 405)

    @override_settings(APP_REVISION="a" * 40)
    def test_health_reports_the_running_revision(self):
        response = self.client.get(reverse("health"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "revision": "a" * 40})

    def test_health_rejects_post(self):
        self.assertEqual(self.client.post(reverse("health"), {}).status_code, 405)

    def test_unknown_api_route_is_not_found(self):
        self.assertEqual(self.client.get("/api/missing/").status_code, 404)
