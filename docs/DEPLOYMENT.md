# CSC 325 — pre-deployment checklist

This is a **preparation checklist**, not proof of a completed deployment. Production deployment and the narrated on-camera change are intentionally reserved for later.

## 1. Verify the code and workflow

- [ ] Open PR #3: https://github.com/alejops2005/CSC325-CI-CD-Django/pull/3
- [ ] Check **Setup, Dependencies, Test** completed successfully for the latest PR commit. The pull-request Deploy job is intentionally **skipped**.
- [ ] Review `api/views.py`, `api/tests.py`, `requirements.txt`, and `.github/workflows/csc325_ci_cd.yml`.
- [ ] Read a real **Test** job log to confirm all **six** API tests passed. Do not treat a green job alone as a deployment.
- [ ] Confirm the repository is public and `main` is the default branch.
- [ ] Keep a small new API behavior change and corresponding test for the final on-camera demonstration.

## 2. Strengthen the existing GitHub main ruleset (manual GitHub settings step)

Open https://github.com/alejops2005/CSC325-CI-CD-Django/rules/25436132

- Target: default branch (`main`).
- Enforcement: **Active**.
- Require a **pull request before merging** (zero required other-person approvals is reasonable for a solo project).
- Block **force pushes** and **deletion**.
- Require successful status checks: **Setup**, **Dependencies**, and **Test**. Select them from the latest passing PR workflow run. Keep **Deploy off the PR-required list**; it skips on PRs.
- Require branches to be up to date before merging (strict). Don't add a bypass unless the instructor explicitly requires one.
- Save, reopen the ruleset, and confirm the three named required status checks are stored.

A ruleset with an empty required-check list does not enforce test success even if its “require status checks” option is enabled.

## 3. Configure Render web hosting — do this only when ready to deploy

The written assignment requires a **running, publicly reachable app**, not an `echo "Deploying"` placeholder.

- Create **Render → New → Web Service**, source `alejops2005/CSC325-CI-CD-Django`, branch `main`, Python 3 runtime, root directory blank.
- Select an allowed plan (e.g. Free if available and acceptable). Review any billing implications.
- Build: `pip install -r requirements.txt && python manage.py check`
- Start: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`
- Use the health-check path `/api/health/`.
- Set **Auto-Deploy = Off**, so the tested GitHub Actions Deploy job controls production releases. For a manual Render web service, do **not** assume `render.yaml` changes your dashboard settings automatically.
- Render environment: `PYTHON_VERSION=3.12.8`, `DJANGO_DEBUG=false`, and a securely generated `DJANGO_SECRET_KEY`. Do not commit this secret. `RENDER_EXTERNAL_HOSTNAME` and `RENDER_GIT_COMMIT` are supplied by Render and read by Django.
- **Bootstrapping note:** The production backend and Gunicorn configuration currently live on PR #3. Before that PR is merged, `main` does not contain the final deployable app. Don't attempt to create a working Render service from today's `main` and expect it to build.
- At deployment time, the simplest sequence is **merge tested PR #3 → create Render Web Service from updated `main` → configure GitHub credentials → re-run the failed Deploy job**. A first main-branch Deploy attempt can fail because the Render service/secrets don't exist yet; this is expected bootstrap work, **not** submission evidence. The first Render provisioning itself may start an initial deploy; do this only when ready.
- Keep Render's **Auto-Deploy Off** so later releases originate from the tested GitHub Actions Deploy job rather than being independently triggered by every push.

## 4. Set GitHub Actions deployment credentials (manual GitHub settings step)

Under **Settings → Secrets and variables → Actions**:

| Type | Name | Value |
| --- | --- | --- |
| Repository secret | `RENDER_API_KEY` | Render API key from your account |
| Repository secret | `RENDER_SERVICE_ID` | Render service ID beginning `srv-` |
| Repository variable | `APP_BASE_URL` | Actual public Render HTTPS origin, no `/api/` path |

Never paste API keys into chat, screen recordings, PRs, or code.

## 5. Baseline merge and first production deployment — later

- [ ] After the three PR checks pass and the main ruleset is saved, **when you are ready to start deploying**, merge PR #3 into protected `main`. Do **not** do this during pre-deployment preparation.
- [ ] The push-to-main run begins automatically. Setup, Dependencies, and Test should pass. **Deploy may fail initially** because there is no Render service/secrets yet; do not mistake that bootstrap failure for a finished assignment.
- [ ] Create the Render Web Service from the now-updated `main` and enter the credentials/URL configuration listed above. Render's initial service creation may perform its own first deploy.
- [ ] In GitHub Actions, re-run the failed Deploy job or re-run all jobs, as appropriate. Verify **Setup → Dependencies → Test → Deploy** are all green.
- [ ] Inspect each job log, including the deployed commit and the verified public API URL.
- [ ] Open `https://YOUR-ACTUAL-RENDER-HOST/api/hello/` and `/api/health/` in a private window.
- [ ] Confirm `health.revision` equals the main workflow run's actual Git SHA.
- [ ] Do not claim the app is deployed merely because PR checks passed or Render settings were entered.

## 6. Reserve the required on-camera final change

After the baseline is successfully deployed, create a **new feature branch** from current `main`. Prepare a small API change, e.g. add `"demonstration": "CI/CD works!"` to `/api/hello/`, and add a test asserting that field.

**Do not commit or push this final change before the video.** During the recorded demonstration:
1. State your name and show the public repo URL.
2. Show `csc325_ci_cd.yml`, the push-to-main trigger, each of four jobs, and explain why `needs: test` prevents early Deploy.
3. Show the changed endpoint and test, and execute the full local suite.
4. Commit and push the change on camera to its feature branch; open a PR and merge into protected `main` once checks pass.
5. Show the resulting **main** Actions run, open logs for all four stages, and show their green results.
6. Open the public URL to show the newly deployed field and matching health revision.

The final video must be **at most five minutes**; edit out waiting, not the required evidence. Keep narration in your own voice and follow any course AI disclosure rules.

## 7. Four Brightspace submissions

- [ ] Video file or unlisted YouTube link accessible without an account.
- [ ] Public GitHub repository: https://github.com/alejops2005/CSC325-CI-CD-Django
- [ ] Exact successful push-to-main Actions run for the **on-camera** change.
- [ ] Actual public API URL showing that change.

Check access to each submitted link in a logged-out/private browser window.
