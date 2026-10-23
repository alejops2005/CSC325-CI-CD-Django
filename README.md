# CSC 325 — Django REST API and GitHub Actions CI/CD

A small **Django + Django REST Framework** backend built for the CSC 325 Module 8 hands-on assignment. The repository provides a public API, automated tests, a four-stage GitHub Actions workflow, and configuration for a future Render deployment.

## Public API

| Method | Route | Example response |
| --- | --- | --- |
| GET | `/api/hello/` | `{"message":"Hello from CSC 325!","course":"CSC 325","module":8}` |
| GET | `/api/health/` | `{"status":"ok","revision":"local"}` during local development |

Other HTTP methods on these GET-only routes return HTTP 405. Unknown routes return HTTP 404. On Render, the health response's `revision` should match the Git commit being deployed.

## Run locally

Python 3.12 is configured in `.python-version`. From the repository root:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS / Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py check
python manage.py test --verbosity 2
python manage.py runserver
```

Visit `http://127.0.0.1:8000/api/hello/` and `http://127.0.0.1:8000/api/health/` locally. The six automated API tests cover normal responses, the configured revision, wrong HTTP methods, and missing routes.

## CI/CD workflow

The single file `.github/workflows/csc325_ci_cd.yml` runs on:
- Every **push to `main`**.
- Pull requests targeting `main` (so changes can be checked before merging).

It defines four jobs in order using `needs:`:
1. **Setup** — check out the repository and select Python 3.12.
2. **Dependencies** — install packages from `requirements.txt` and check consistency.
3. **Test** — run Django checks and the **full** automated test suite. A failing test fails this job and stops deployment.
4. **Deploy** — on a tested **push to `main` only**, request deployment of that exact commit to Render, then verify the public health and hello APIs.

Pull requests intentionally **skip Deploy**; only the main-branch production run should have all four jobs green.

## Production configuration

`render.yaml` documents the intended Python web service, and `scripts/deploy_render.py` handles a verified deployment. Rendering the YAML, merging code, or obtaining a green PR check **does not mean a live application has been deployed**.

Read [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for the complete **pre-deploy checklist**, Render settings, GitHub Secrets/variables, required ruleset checks, and final video/submission steps.

**Do not merge PR #3 while deferring deployment.** When ready, first enforce the PR's Setup/Dependencies/Test checks, then merge into main and bootstrap Render from the now-deployable main branch. The first production Deploy job may fail before hosting credentials exist; configure Render and rerun it to green. See the detailed checklist. Keep the final on-camera demonstration change uncommitted/unpushed until recording.

## Assignment evidence

Submit the public repository, a specific green four-stage push-to-main Actions run, the public API URL, and a narrated recording (at most five minutes). The recording must show the real code/test change, local tests, commit and push, successful stage logs, and the live deployed result.

Document any AI assistance according to your course's policy. The code repository, actual GitHub run, and deployed endpoint—not this README—are the evidence of completion.
