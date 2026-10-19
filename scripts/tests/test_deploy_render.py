"""Offline tests of deployment gating and real-response verification."""

import io
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import MagicMock, call, patch
from urllib.error import HTTPError

from scripts import deploy_render as deployment


REVISION = "a" * 40
HELLO = {"message": "Hello from CSC 325!", "course": "CSC 325", "module": 8}
BASE_URL = "https://example.onrender.com"


class DeploymentTests(TestCase):
    @patch.object(deployment, "verify_public_api")
    @patch.object(deployment, "wait_for_deploy")
    @patch.object(deployment, "request_json", return_value={"id": "dep-example"})
    def test_deploy_pins_exact_tested_commit_and_verifies_after_live(self, request, wait, verify):
        deployment.deploy(
            api_key="fake-test-key", service_id="srv-example", base_url=BASE_URL,
            revision=REVISION, expected_hello=HELLO,
        )
        request.assert_called_once_with(
            "POST", "https://api.render.com/v1/services/srv-example/deploys",
            api_key="fake-test-key",
            payload={"commitId": REVISION, "clearCache": "do_not_clear"},
        )
        wait.assert_called_once_with("fake-test-key", "srv-example", "dep-example", REVISION)
        verify.assert_called_once_with(BASE_URL, REVISION, HELLO)

    @patch.object(deployment, "request_json")
    def test_invalid_revision_cannot_trigger_deployment(self, request):
        with self.assertRaisesRegex(deployment.DeploymentError, "full tested Git commit SHA"):
            deployment.deploy(
                api_key="fake-test-key", service_id="srv-example", base_url=BASE_URL,
                revision="main", expected_hello=HELLO,
            )
        request.assert_not_called()

    @patch.object(deployment, "request_json", return_value={})
    def test_missing_deploy_id_fails(self, request):
        with self.assertRaisesRegex(deployment.DeploymentError, "deployment identifier"):
            deployment.deploy(
                api_key="fake-test-key", service_id="srv-example", base_url=BASE_URL,
                revision=REVISION, expected_hello=HELLO,
            )

    @patch.object(deployment, "request_json")
    def test_render_live_status_requires_matching_commit(self, request):
        request.return_value = {"status": "live", "commit": {"id": "b" * 40}}
        with self.assertRaisesRegex(deployment.DeploymentError, "does not match the tested commit"):
            deployment.wait_for_deploy("fake-test-key", "srv-example", "dep-example", REVISION)

    @patch.object(deployment, "request_json")
    def test_render_live_status_with_no_commit_fails(self, request):
        request.return_value = {"status": "live", "commit": None}
        with self.assertRaisesRegex(deployment.DeploymentError, "does not match the tested commit"):
            deployment.wait_for_deploy("fake-test-key", "srv-example", "dep-example", REVISION)

    @patch.object(deployment.time, "sleep")
    @patch.object(deployment, "request_json")
    def test_waits_for_real_live_status(self, request, sleep):
        request.side_effect = [
            {"status": "build_in_progress"},
            {"status": "live", "commit": {"id": REVISION}},
        ]
        deployment.wait_for_deploy("fake-test-key", "srv-example", "dep-example", REVISION)
        self.assertEqual(request.call_count, 2)
        sleep.assert_called_once_with(10)

    @patch.object(deployment, "request_json")
    def test_render_failure_never_counts_as_success(self, request):
        for status in deployment.FAILED_DEPLOY_STATUSES:
            with self.subTest(status=status):
                request.return_value = {"status": status}
                with self.assertRaisesRegex(deployment.DeploymentError, "failed with status"):
                    deployment.wait_for_deploy("fake-test-key", "srv-example", "dep-example", REVISION)

    @patch.object(deployment.time, "monotonic", side_effect=[0, 2])
    @patch.object(deployment, "request_json")
    def test_deployment_timeout_fails(self, request, clock):
        with self.assertRaisesRegex(deployment.DeploymentError, "Timed out"):
            deployment.wait_for_deploy(
                "fake-test-key", "srv-example", "dep-example", REVISION, timeout=1,
            )
        request.assert_not_called()

    @patch.object(deployment, "request_json")
    def test_public_api_requires_revision_and_exact_tested_json(self, request):
        final_hello = {**HELLO, "demonstration": "CI/CD works!"}
        request.side_effect = [{"status": "ok", "revision": REVISION}, final_hello]
        deployment.verify_public_api(BASE_URL, REVISION, final_hello)
        self.assertEqual(request.call_args_list, [
            call("GET", BASE_URL + "/api/health/"),
            call("GET", BASE_URL + "/api/hello/"),
        ])

    @patch.object(deployment.time, "sleep")
    @patch.object(deployment.time, "monotonic", side_effect=[0, 0, 2])
    @patch.object(deployment, "request_json")
    def test_green_render_status_cannot_hide_wrong_public_revision(self, request, clock, sleep):
        request.return_value = {"status": "ok", "revision": "old-commit"}
        with self.assertRaisesRegex(deployment.DeploymentError, "not the tested revision"):
            deployment.verify_public_api(BASE_URL, REVISION, HELLO, timeout=1)

    @patch.object(deployment.time, "sleep")
    @patch.object(deployment.time, "monotonic", side_effect=[0, 0, 2])
    @patch.object(deployment, "request_json")
    def test_missing_final_demonstration_field_fails_verification(self, request, clock, sleep):
        request.side_effect = [{"status": "ok", "revision": REVISION}, HELLO]
        with self.assertRaisesRegex(deployment.DeploymentError, "differs from the tested API"):
            deployment.verify_public_api(
                BASE_URL, REVISION, {**HELLO, "demonstration": "CI/CD works!"}, timeout=1,
            )

    def test_public_url_requires_https_origin_without_credentials(self):
        for value in (
            "http://example.onrender.com", "https://user:secret@example.com",
            "https://example.com/path", "https://example.com?query=1",
            "https://example.com#fragment", "example.com",
        ):
            with self.subTest(value=value), self.assertRaises(deployment.DeploymentError):
                deployment.validate_base_url(value)
        self.assertEqual(deployment.validate_base_url(BASE_URL + "/"), BASE_URL)

    @patch.dict(os.environ, {}, clear=True)
    @patch.object(deployment, "request_json")
    def test_missing_settings_fail_before_network_access(self, request):
        with self.assertRaisesRegex(deployment.DeploymentError, "RENDER_API_KEY"):
            deployment.main()
        request.assert_not_called()

    def test_verified_deployment_summary_contains_public_urls_and_commit(self):
        with TemporaryDirectory() as directory:
            summary = Path(directory) / "summary.md"
            with patch.dict(os.environ, {"GITHUB_STEP_SUMMARY": str(summary)}):
                deployment.write_github_summary(BASE_URL, REVISION)
            content = summary.read_text(encoding="utf-8")
        self.assertIn(BASE_URL + "/api/hello/", content)
        self.assertIn(BASE_URL + "/api/health/", content)
        self.assertIn(REVISION, content)


class HttpRequestTests(TestCase):
    @patch.object(deployment, "build_opener")
    def test_api_authentication_and_json_request(self, opener_factory):
        response = MagicMock()
        response.headers = {"Content-Type": "application/json; charset=utf-8"}
        response.read.return_value = json.dumps({"id": "dep-example"})
        opener_factory.return_value.open.return_value.__enter__.return_value = response
        result = deployment.request_json(
            "POST", "https://api.render.com/v1/services/srv-example/deploys",
            api_key="fake-test-key", payload={"commitId": REVISION},
        )
        self.assertEqual(result, {"id": "dep-example"})
        request = opener_factory.return_value.open.call_args.args[0]
        self.assertEqual(request.get_header("Authorization"), "Bearer fake-test-key")
        self.assertEqual(json.loads(request.data), {"commitId": REVISION})
        self.assertIsInstance(opener_factory.call_args.args[0], deployment.NoRedirects)

    @patch.object(deployment, "build_opener")
    def test_http_error_does_not_expose_response_or_token(self, opener_factory):
        opener_factory.return_value.open.side_effect = HTTPError(
            "https://api.render.com/v1/services/srv-example/deploys", 401, "Unauthorized",
            {}, io.BytesIO(b"sensitive response should not be printed"),
        )
        with self.assertRaisesRegex(deployment.DeploymentError, "HTTP 401") as context:
            deployment.request_json("POST", deployment.RENDER_API, api_key="fake-test-key")
        self.assertNotIn("fake-test-key", str(context.exception))
        self.assertNotIn("sensitive", str(context.exception))

    @patch.object(deployment, "build_opener")
    def test_html_instead_of_public_json_fails(self, opener_factory):
        response = MagicMock()
        response.headers = {"Content-Type": "text/html"}
        opener_factory.return_value.open.return_value.__enter__.return_value = response
        with self.assertRaisesRegex(deployment.DeploymentError, "application/json"):
            deployment.request_json("GET", BASE_URL + "/api/hello/")
