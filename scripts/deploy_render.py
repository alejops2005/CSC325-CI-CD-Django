"""Deploy an exact tested commit to Render, then verify the public Django API."""
import json
import os
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


def request_json(url, token=None, data=None):
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    if data is not None:
        headers["Content-Type"] = "application/json"
    request = Request(url, data=json.dumps(data).encode() if data is not None else None, headers=headers)
    with urlopen(request, timeout=35) as response:
        return json.load(response)


def main():
    needed = ["RENDER_API_KEY", "RENDER_SERVICE_ID", "APP_BASE_URL", "DEPLOY_COMMIT"]
    missing = [name for name in needed if not os.getenv(name)]
    if missing:
        raise RuntimeError("Missing deployment configuration: " + ", ".join(missing))
    key = os.environ["RENDER_API_KEY"]
    service = os.environ["RENDER_SERVICE_ID"]
    origin = os.environ["APP_BASE_URL"].rstrip("/")
    commit = os.environ["DEPLOY_COMMIT"]
    if not origin.startswith("https://") or "/" in origin[len("https://"):]:
        raise RuntimeError("APP_BASE_URL must be the HTTPS origin, without /api/ or paths")
    if not service.startswith("srv-") or len(commit) != 40:
        raise RuntimeError("Invalid Render service ID or Git revision")
    endpoint = "https://api.render.com/v1/services/" + quote(service, safe="") + "/deploys"
    response = request_json(endpoint, key, {"commitId": commit, "clearCache": "do_not_clear"})
    deploy_id = response.get("id")
    if not deploy_id:
        raise RuntimeError("Render did not return a deployment ID")
    deadline = time.monotonic() + 1500
    while time.monotonic() < deadline:
        record = request_json(endpoint + "/" + quote(deploy_id, safe=""), key)
        state = record.get("status")
        print("Render deployment status:", state, flush=True)
        if state in {"build_failed", "pre_deploy_failed", "update_failed", "canceled", "deactivated"}:
            raise RuntimeError("Render deployment failed: " + str(state))
        if state == "live":
            actual = (record.get("commit") or {}).get("id")
            if actual != commit:
                raise RuntimeError("Live deployment commit does not match tested commit")
            break
        time.sleep(15)
    else:
        raise RuntimeError("Render deployment timed out")
    for attempt in range(18):
        try:
            health = request_json(origin + "/api/health/")
            hello = request_json(origin + "/api/hello/")
            if health.get("status") == "ok" and health.get("revision") == commit and hello.get("course") == "CSC 325":
                print("Verified deployed commit:", commit)
                print("Public API:", origin + "/api/hello/")
                return
        except (HTTPError, URLError, ValueError, TimeoutError):
            pass
        time.sleep(10)
    raise RuntimeError("Public API or deployed revision could not be verified")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, HTTPError, URLError, ValueError) as exc:
        print("Deployment failed:", str(exc) if not isinstance(exc, HTTPError) else "Render/API HTTP " + str(exc.code), file=sys.stderr)
        sys.exit(1)
