"""Save the tested API response so deployment can verify the same response."""

import argparse
import json
import os
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django
    from django.test import Client, override_settings

    django.setup()
    with override_settings(ALLOWED_HOSTS=["testserver"], SECURE_SSL_REDIRECT=False):
        response = Client().get("/api/hello/")
    if response.status_code != 200:
        raise SystemExit(f"Expected /api/hello/ HTTP 200, got {response.status_code}")
    payload = response.json()
    if not isinstance(payload, dict) or not payload:
        raise SystemExit("The tested API must return a nonempty JSON object")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Saved the tested /api/hello/ response to {args.output}")


if __name__ == "__main__":
    main()
