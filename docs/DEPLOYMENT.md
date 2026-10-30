# Deployment

## Historical production baseline

The Render service is already configured and working at [https://csc325-ci-cd-django.onrender.com](https://csc325-ci-cd-django.onrender.com).

The [successful baseline production workflow](https://github.com/alejops2005/CSC325-CI-CD-Django/actions/runs/39888598055) completed for commit `9489c5f3c4a72fd12c23bc7c8e2050c167f5dc35`, the merge of PR #3. Baseline preparation and the initial production deployment are complete.

Before the final demonstration, that baseline revision contained six automated tests and no demonstration field. The demonstration change, prepared on `feature/final-api-demo`, adds `"demonstration": "CI/CD works!"` and brings the suite to seven tests. The baseline workflow remains historical evidence after the final change is released. Determine the current deployment from the latest successful main workflow, live health revision, and hello response.

## Deployment process

[The GitHub Actions workflow](../.github/workflows/csc325_ci_cd.yml) runs Setup → Dependencies → Test → Deploy. Setup selects Python 3.12 and checks project files. Dependencies installs requirements and checks consistency. Test executes Django checks and the complete suite.

Pull requests targeting `main` run the first three jobs; Deploy is skipped. After a tested pull request is merged, the push to `main` starts a new workflow. Deploy depends on Test and runs only for a push to `refs/heads/main`. A failed prerequisite prevents deployment.

The Deploy job uses the `production` GitHub environment and serializes releases through the `csc325-production` concurrency group. It runs `scripts/deploy_render.py` with the workflow's exact Git SHA. The script requests that commit through the Render API, waits for the deployment to become live, verifies Render's deployed commit, and checks `/api/health/` and `/api/hello/`. The health revision must equal the tested SHA. The script checks the hello course value; the final demonstration field needs explicit live verification.

## Render configuration

Keep the existing web service connected to this repository and branch `main`. The configuration in [`render.yaml`](../render.yaml) describes:

| Setting | Value |
| --- | --- |
| Runtime | Python; configured version `3.12.8` |
| Build command | `pip install -r requirements.txt && python manage.py check` |
| Start command | `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT` |
| Health check | `/api/health/` |
| Automatic deploys | Off; GitHub Actions controls releases |

For a service configured manually in Render, changes to `render.yaml` do not automatically update dashboard settings. Keep the dashboard consistent with the intended configuration.

## Branch protection and required checks

Use the [main branch ruleset](https://github.com/alejops2005/CSC325-CI-CD-Django/rules/25436132) to enforce:

- Active enforcement for `main`, with pull requests required before merging.
- Required status checks named **Setup**, **Dependencies**, and **Test**.
- Branches up to date before merging, with force pushes and branch deletion blocked.

Confirm these settings in GitHub before recording; local workflow YAML does not prove that server-side rules are enabled. The required-check list must actually contain all three checks. Do not require Deploy on pull requests, where it is skipped. For a solo assignment, use the approval requirement permitted by the course without bypassing required checks.

## Secrets and environment variables

Configure deployment credentials through GitHub Settings → Secrets and variables → Actions, at a scope available to the `production` job:

| Type | Name | Purpose |
| --- | --- | --- |
| GitHub secret | `RENDER_API_KEY` | Authorizes Render API deployment requests |
| GitHub secret | `RENDER_SERVICE_ID` | Identifies the existing Render service |
| GitHub variable | `APP_BASE_URL` | `https://csc325-ci-cd-django.onrender.com`, without an API path |

In Render, maintain `DJANGO_DEBUG=false`, a securely generated `DJANGO_SECRET_KEY`, and the configured `PYTHON_VERSION`. Render supplies `RENDER_EXTERNAL_HOSTNAME` and `RENDER_GIT_COMMIT`; Django uses them for the allowed production host and deployed revision. `RENDER_GIT_COMMIT` takes precedence over the optional `APP_REVISION` fallback.

Keep credential values in the relevant secret stores. Never commit them, paste them into documentation or PRs, print them in logs, or show them in the recording. Only variable names and public URLs belong in demonstration evidence.

## Final recording procedure

Before recording, keep all four prepared files (`README.md`, `docs/DEPLOYMENT.md`, `api/views.py`, and `api/tests.py`) local and uncommitted. The steps below describe the transition from preparation to a deployed demonstration revision. After completing them, use the resulting workflow and live responses as release evidence. Allow time for hosted builds and edit out waiting while retaining the required evidence. The final narrated video must fit the five-minute assignment limit.

1. Introduce the project and show the [public repository](https://github.com/alejops2005/CSC325-CI-CD-Django). Show the pre-demonstration live baseline and explain that its six-test implementation lacks the new field. This is the historical starting point for the recording, followed by the final deployed result.
2. Show `feature/final-api-demo`, the local Git diff, the new hello field, the updated expected response, and `test_hello_includes_demonstration_field`.
3. Run the local checks with the existing Windows virtual environment:

   ```powershell
   git diff --check
   .\.venv\Scripts\python.exe manage.py check
   .\.venv\Scripts\python.exe manage.py test --verbosity 2
   git status --short --branch
   ```

   Show seven passing tests. If the environment cannot execute Python, repair it and obtain passing results before continuing.
4. During recording, stage the four prepared files, commit them, and push `feature/final-api-demo`. Create a pull request targeting `main`.
5. Show the PR's required Setup, Dependencies, and Test checks passing, with Deploy skipped. Merge only after the required checks and branch rules are satisfied.
6. Open the resulting push-to-main Actions run. Explain the four jobs and `needs: test`, then show successful Setup, Dependencies, Test, and Deploy logs for the merged revision.
7. Open the [live hello endpoint](https://csc325-ci-cd-django.onrender.com/api/hello/) and verify `"demonstration": "CI/CD works!"`. Open the [live health endpoint](https://csc325-ci-cd-django.onrender.com/api/health/) and confirm `status` is `ok` and `revision` matches the main workflow's deployed SHA.

A passing local suite or PR does not establish a production release. Use the successful main workflow and live API response as evidence that the demonstration change reached production.

## Final assignment submission checklist

- [ ] Narrated video, at most five minutes, submitted as the required file or an accessible unlisted link.
- [ ] Public repository: [CSC325-CI-CD-Django](https://github.com/alejops2005/CSC325-CI-CD-Django).
- [ ] Exact successful push-to-main Actions run for the recorded demonstration change; the linked baseline run is historical evidence, not a substitute for the final run.
- [ ] Public [hello API](https://csc325-ci-cd-django.onrender.com/api/hello/) displaying the demonstration field.
- [ ] Health revision matches the final deployed workflow SHA.
- [ ] Recording shows the code/test change, seven local tests, commit and push, PR checks, merge, four successful production stages, and live verification.
- [ ] Submission links work in a logged-out/private browser window.
- [ ] Any required disclosure of AI assistance follows course policy; no credentials appear in evidence.
