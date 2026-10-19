# CSC 325 Module 8: Django CI/CD

A small Django + Django REST Framework API with automated tests, a four-stage
GitHub Actions pipeline, and a Render deployment that verifies the public API.

## Run locally

Use Python 3.12. From this repository:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py test --verbosity 2
python manage.py runserver 0.0.0.0:8000
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1` instead.
No database or external credentials are needed for these read-only endpoints.
The development server is for local use; Render runs Gunicorn with
`gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --no-control-socket`.

```bash
curl http://127.0.0.1:8000/api/hello/
curl http://127.0.0.1:8000/api/health/
```

The baseline hello response is:

```json
{"message":"Hello from CSC 325!","course":"CSC 325","module":8}
```

The health response reports `status: "ok"` and the deployed revision, using
`RENDER_GIT_COMMIT`, then `APP_REVISION`, then `local`.

## How it works

- `config/` contains Django settings and the root URL configuration.
- `api/` contains public DRF views, routes, and automated API tests.
- `requirements.txt` pins the Python dependencies.
- `.github/workflows/csc325_ci_cd.yml` runs **Setup → Dependencies → Test → Deploy**.
  Each job uses `needs` to depend on the preceding job. Pushes to `main` run the
  complete pipeline; pull requests into `main` run CI with Deploy skipped.
- `render.yaml` describes the public Render web service. Automatic deployments
  are disabled so ordinary production updates go through the tested workflow.
- `scripts/deploy_render.py` requests deployment of the exact GitHub commit,
  waits for Render, and checks the public API and reported revision. A green
  build alone is not deployment verification.

See [the assignment guide](docs/ASSIGNMENT.md) for hosting setup, GitHub Secrets,
main protection, the final uncommitted camera change, a five-minute recording
checklist, submission links, and AI disclosure guidance. The prepared branch and
uncommitted patch live in this cloud workspace; they do not automatically appear
on your laptop.

## Deployment status

The checked-in configuration does not establish that a public service exists or
that a GitHub run passed. Those claims require an actual Render account/service,
GitHub configuration, a successful production workflow, and a matching live API
response. Record the verified URLs and commit SHA in the assignment guide.
The rubric requires a **public** repository and submission links that open
without login; verify them in a signed-out/private browser window.
