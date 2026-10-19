"""Deploy the tested Git commit to Render, then verify its real public API.

Uses Python's standard library and default TLS certificate verification.
Secrets are read only from environment variables and are never logged.
"""

import json
import os
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


RENDER_API = "https://api.render.com/v1"
FAILED_DEPLOY_STATUSES = {
    "build_failed", "pre_deploy_failed", "update_failed", "canceled", "deactivated",
}


class DeploymentError(RuntimeError):
    """A deploy or a public verification step failed."""


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        # In particular, never forward the Render authorization header elsewhere.
        return None


def request_json(method, url, *, api_key=None, payload=None):
    headers = {"Accept": "application/json", "User-Agent": "CSC325-CI-CD/1.0"}
    data = None
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = Request(url, data=data, headers=headers, method=method)
    try:
        with build_opener(NoRedirects()).open(request, timeout=30) as response:
            content_type = response.headers.get("Content-Type", "").split(";", 1)[0]
            if content_type != "application/json":
                raise DeploymentError("The server did not return application/json")
            result = json.load(response)
    except HTTPError as error:
        # Do not print response bodies, headers, or request objects with credentials.
        raise DeploymentError(f"{method} {urlsplit(url).hostname} returned HTTP {error.code}") from None
    except (URLError, TimeoutError, OSError):
        raise DeploymentError(f"Could not reach {urlsplit(url).hostname} over HTTPS") from None
    except (ValueError, UnicodeError):
        raise DeploymentError("The server returned invalid JSON") from None
    if not isinstance(result, dict):
        raise DeploymentError("Expected a JSON object")
    return result


def validate_base_url(value):
    parsed = urlsplit(value)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or not re.fullmatch(r"[A-Za-z0-9.-]+", parsed.hostname)
        or any(character.isspace() for character in value)
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path not in ("", "/")
        or parsed.query
        or parsed.fragment
    ):
        raise DeploymentError("APP_BASE_URL must be the public HTTPS origin, without a path or credentials")
    return value.rstrip("/")


def write_github_summary(base_url, revision):
    """Publish links only after both Render and the public responses are verified."""
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    with Path(summary_path).open("a", encoding="utf-8") as summary:
        summary.write(
            "### Verified public deployment\n\n"
            f"- Public API: [{base_url}/api/hello/]({base_url}/api/hello/)\n"
            f"- Health and revision: [{base_url}/api/health/]({base_url}/api/health/)\n"
            f"- Tested and deployed commit: `{revision}`\n\n"
            "The public JSON response exactly matches the API response captured by Test.\n"
        )


def wait_for_deploy(api_key, service_id, deploy_id, revision, *, timeout=1200, interval=10):
    url = f"{RENDER_API}/services/{quote(service_id, safe='')}/deploys/{quote(deploy_id, safe='')}"
    deadline = time.monotonic() + timeout
    previous_status = None
    while time.monotonic() < deadline:
        deployment = request_json("GET", url, api_key=api_key)
        status = deployment.get("status")
        if status != previous_status:
            print(f"Render deployment status: {status}", flush=True)
            previous_status = status
        if status in FAILED_DEPLOY_STATUSES:
            raise DeploymentError(f"Render deployment failed with status: {status}")
        if status == "live":
            if (deployment.get("commit") or {}).get("id") != revision:
                raise DeploymentError("Render's live deployment does not match the tested commit")
            return
        time.sleep(interval)
    raise DeploymentError("Timed out waiting for Render to report the tested deployment live")


def verify_public_api(base_url, revision, expected_hello, *, timeout=180, interval=10):
    deadline = time.monotonic() + timeout
    last_error = "No public response received"
    while time.monotonic() < deadline:
        try:
            health = request_json("GET", f"{base_url}/api/health/")
            if health.get("status") != "ok" or health.get("revision") != revision:
                raise DeploymentError("Public health response is not the tested revision")
            hello = request_json("GET", f"{base_url}/api/hello/")
            if hello != expected_hello:
                raise DeploymentError("Public /api/hello/ response differs from the tested API response")
            print(f"Verified public API: {base_url}/api/hello/", flush=True)
            print(f"Verified live commit: {revision}", flush=True)
            return
        except DeploymentError as error:
            last_error = str(error)
        time.sleep(interval)
    raise DeploymentError(f"Public API verification failed: {last_error}")


def deploy(*, api_key, service_id, base_url, revision, expected_hello):
    base_url = validate_base_url(base_url)
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise DeploymentError("EXPECTED_REVISION must be the full tested Git commit SHA")
    if not service_id.startswith("srv-"):
        raise DeploymentError("RENDER_SERVICE_ID must be the srv- identifier from Render")
    deployment = request_json(
        "POST",
        f"{RENDER_API}/services/{quote(service_id, safe='')}/deploys",
        api_key=api_key,
        payload={"commitId": revision, "clearCache": "do_not_clear"},
    )
    deploy_id = deployment.get("id")
    if not isinstance(deploy_id, str) or not deploy_id:
        raise DeploymentError("Render did not return a deployment identifier")
    print(f"Requested deployment of tested commit {revision}", flush=True)
    wait_for_deploy(api_key, service_id, deploy_id, revision)
    verify_public_api(base_url, revision, expected_hello)
    write_github_summary(base_url, revision)


def main():
    required = ("RENDER_API_KEY", "RENDER_SERVICE_ID", "APP_BASE_URL", "EXPECTED_REVISION", "EXPECTED_HELLO_PATH")
    missing = [name for name in required if not os.environ.get(name, "").strip()]
    if missing:
        raise DeploymentError("Configure the missing GitHub secrets/variables: " + ", ".join(missing))
    try:
        expected_hello = json.loads(Path(os.environ["EXPECTED_HELLO_PATH"]).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raise DeploymentError("Could not read the tested API response artifact") from None
    if not isinstance(expected_hello, dict) or not expected_hello:
        raise DeploymentError("The tested API response artifact must be a nonempty JSON object")
    deploy(
        api_key=os.environ["RENDER_API_KEY"],
        service_id=os.environ["RENDER_SERVICE_ID"],
        base_url=os.environ["APP_BASE_URL"],
        revision=os.environ["EXPECTED_REVISION"],
        expected_hello=expected_hello,
    )


if __name__ == "__main__":
    try:
        main()
    except DeploymentError as error:
        print(f"Deployment failed: {error}", file=sys.stderr)
        sys.exit(1)
