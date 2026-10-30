# CSC 325: Django REST API and CI/CD

This project demonstrates a complete continuous integration and continuous deployment workflow for a public Python API. Django provides the application framework and configuration, Django REST Framework handles JSON responses and API testing, GitHub Actions validates changes, and Render hosts the production service with Gunicorn.

- [GitHub repository](https://github.com/alejops2005/CSC325-CI-CD-Django)
- [Successful baseline production workflow](https://github.com/alejops2005/CSC325-CI-CD-Django/actions/runs/39888598055)
- [Live service](https://csc325-ci-cd-django.onrender.com)
- [Live hello API](https://csc325-ci-cd-django.onrender.com/api/hello/) and [live health API](https://csc325-ci-cd-django.onrender.com/api/health/)

## Historical production baseline and final demonstration

Before the final demonstration, the successfully deployed baseline was commit `9489c5f3c4a72fd12c23bc7c8e2050c167f5dc35`. That historical revision contains **six tests**, and its hello response does **not** include the demonstration field. The linked baseline workflow documents that earlier release, not necessarily the current production revision.

The final demonstration change, prepared on `feature/final-api-demo`, brings the suite to **seven tests**. It adds `"demonstration": "CI/CD works!"` to the hello response, updates the expected JSON, and adds `test_hello_includes_demonstration_field`. Before recording, keep the change uncommitted and unpushed. During recording, take it through the pull request and production pipeline. Determine its current release status from the latest successful main workflow, live health revision, and hello response; local test success alone does not update production.

## Public API

Both endpoints accept GET requests and return JSON without authentication.

| Endpoint | Historical baseline response |
| --- | --- |
| `/api/hello/` | `{"message":"Hello from CSC 325!","course":"CSC 325","module":8}` |
| `/api/health/` | `{"status":"ok","revision":"<deployed Git commit SHA>"}` |

The hello response introduced by the final demonstration change is:

```json
{
  "message": "Hello from CSC 325!",
  "course": "CSC 325",
  "module": 8,
  "demonstration": "CI/CD works!"
}
```

Locally, the health revision defaults to `local`. In production, Django reads `RENDER_GIT_COMMIT` so the revision identifies the deployed source. POST requests to these endpoints return 405; an unknown API route returns 404.

## Run locally with Windows PowerShell

Use Python 3.12 and the existing project virtual environment from the repository root. Calling its interpreter directly avoids activation and PATH dependencies.

```powershell
# Install dependencies only when setting up or refreshing the environment.
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# Run system checks and the complete suite.
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test --verbosity 2

# Start the local development server.
.\.venv\Scripts\python.exe manage.py runserver
```

The final demonstration revision should report seven passing tests. The historical baseline revision has six. Tests cover response content and status, configured health revision, rejected POST requests, a missing route, and the added demonstration field. These read-only API tests use `SimpleTestCase` and do not require a test database.

Open `http://127.0.0.1:8000/api/hello/` or `http://127.0.0.1:8000/api/health/`. A missing or broken `.venv` must be repaired with an installed Python 3.12 interpreter before these commands can run.

## GitHub Actions pipeline

The workflow in [`.github/workflows/csc325_ci_cd.yml`](.github/workflows/csc325_ci_cd.yml) executes **Setup → Dependencies → Test → Deploy** through job dependencies:

1. **Setup:** checks out source, selects Python 3.12, and verifies required project files.
2. **Dependencies:** installs pinned requirements and runs `pip check`.
3. **Test:** runs Django system checks and the complete automated test suite.
4. **Deploy:** requests a Render deployment of the exact tested commit and verifies the public API and deployed revision.

Pull requests targeting `main` run Setup, Dependencies, and Test before merging. Deploy is intentionally skipped for pull requests. Protect `main` with a required pull request and the three required checks; Deploy must not be a required PR check because it does not run there.

A merge into `main` generates a push-to-main workflow. Deploy runs only for a push to `main` after Test succeeds (`needs: test`). Render automatic deploys must remain off so production releases follow the tested GitHub Actions path.

## Production deployment and recording

The existing Render service is working at the live URL above. [`render.yaml`](render.yaml) describes the service, and [`scripts/deploy_render.py`](scripts/deploy_render.py) submits the tested SHA, waits for Render to report it live, and checks both public endpoints. The script verifies the health revision and hello course value; verify the new demonstration field explicitly during the final recording.

See [deployment documentation](docs/DEPLOYMENT.md) for hosting configuration, required checks, secret handling, the recording procedure, and submission evidence. The recording sequence is local tests → commit → push → pull request → required checks → merge → production deployment → live API verification. Keep credentials out of the recording and follow course requirements for AI assistance disclosure.
