# CSC 325 Module 8 demonstration guide

## What to explain

“Django handles application configuration and URL routing. Django REST Framework
turns the public views into JSON API responses. `/api/hello/` returns the course
message, and `/api/health/` reports service health and its deployed commit. The
tests make requests to the API and check its actual responses. A nonzero test
exit code fails GitHub Actions, preventing the Deploy job from running.”

“The four jobs are Setup, Dependencies, Test, and Deploy. Each job declares
`needs` on its predecessor. GitHub gives each job a separate runner, so jobs
explicitly prepare the files and runtime they need. Pull requests run the first
three jobs so I can check a change before merging. Only a push to `main` may
deploy. The deployment script asks Render to deploy that exact commit, waits
for completion, and verifies both the public API and its reported revision.”

Read the source and run the commands yourself before recording. Use wording you
understand rather than reciting this guide verbatim.

## Rubric evidence

The supplied assignment and Level 4 rubric require a public repository, a running backend, at
least two tests of real behavior, a ruleset protecting main, four clearly named
jobs triggered by pushes to main, and Deploy depending on Test. It also requires
a narrated recording of **at most five minutes**, covering the **six parts in
the order listed below**, opening stage logs, and showing the code change. The
linked passing workflow must result from the commit pushed during that video,
with all four jobs green. All four submitted links must open without login.

The six-part recording checklist and four submission items below follow the
assignment instructions. This project uses Python 3.12; the tutorial itself was
not provided, so compare its version requirement if the course mandates one.

| Requirement | Evidence to show or verify |
| --- | --- |
| Public repository and working backend | Open the repository and public API without GitHub/Render login. |
| At least two real behavior tests | Show API response assertions and a successful full-suite run. |
| Main ruleset | Show an active ruleset targeting `main`, requiring PRs and checks. |
| Four-stage workflow | Show `Setup → Dependencies → Test → Deploy`, the main push trigger, `needs`, and each job's actual logs. |
| Change pushed in the video | Show the final feature commit, push, PR, merge commit, and the resulting successful main workflow. |
| Real deployment of that change | Show the final public response field and health revision matching that main run's SHA. |
| Submission and recording | Use the six-part order below, keep the recording ≤5:00, and check anonymous access to each submitted URL. |

## External setup and authorization

These steps require your GitHub/Render account access and your decision to
publish or change repository settings. Do not paste secret values into chat or
commit them to Git. No hosting account, subscription, remote branch protection,
remote push, or successful public deployment is implied by local project files.

1. **Open a bootstrap pull request for the baseline.** Use the published baseline
   of `feature/module-8-ci-cd` to open a pull request into `main`:
   https://github.com/alejops2005/CSC325-CI-CD-Django/compare/main...feature/module-8-ci-cd?expand=1
   An uncommitted demonstration patch is not included in that branch's push.
   Check that Setup, Dependencies, and Test pass. Review the diff before
   publishing. Confirm the repository is **public** as required by the rubric;
   changing visibility requires an account-authorized repository settings change.
   An unauthenticated GitHub HTML check returned HTTP 200, a Public label, and
   repository-public metadata. Confirm visibility again in a private browser
   before submission. Remote ruleset enforcement has not been verified here.
2. **Merge the tested baseline.** Once its PR checks pass, merge the baseline into
   `main` using **Create a merge commit** and keep the feature branch. This puts
   `render.yaml` and the application on the branch Render will build. The first
   main workflow will fail Deploy while hosting secrets are still absent; that
   is an unresolved bootstrap prerequisite, not a successful assignment run.
3. **Create/configure a Render service.** Connect your GitHub repository to Render
   and review `render.yaml` in the Blueprint flow, or create an equivalent Python
   web service using the commands and environment settings in that file. Grant
   Render the repository access it needs. Review the selected plan, any billing
   terms, and your account's current free-tier availability before approving
   service creation. The service is named `csc325-ci-cd-django`; Render assigns
   the actual public hostname. Do not assume a hostname from the service name.
   Initial service provisioning may itself start a deploy: create the service
   only after the baseline's tests have passed and it is merged into main.
   Keep Render automatic deployment disabled. Subsequent releases use the
   workflow's exact commit deployment after its tests pass.
4. **Add GitHub Actions configuration.** In the repository's **Settings → Secrets
   and variables → Actions**, add the secrets and variable below. Obtain the
   service ID from Render service settings/dashboard; it has the form `srv-…`.
   Create a Render API key using your own authorized account. Treat that key as
   a credential with the account access granted by Render.
5. **Finish the bootstrap.** On the original baseline push-to-main workflow,
   choose **Re-run failed jobs** after Render and GitHub configuration are ready.
   If its artifacts have expired, choose **Re-run all jobs** instead. Confirm all
   four jobs are green and the public API reports that exact main commit.
   Resolve any setup failure before starting the final recording.

| GitHub Actions setting | Type | Purpose |
| --- | --- | --- |
| `RENDER_API_KEY` | Secret | Authorizes the real Render deployment API call. |
| `RENDER_SERVICE_ID` | Secret | Identifies the Render web service to deploy. |
| `APP_BASE_URL` | Variable | The service's real HTTPS origin, such as the URL shown in Render; no API path. |

Render's Blueprint generates `DJANGO_SECRET_KEY` in the hosting environment.
Production also sets `DJANGO_DEBUG=false`, allowed hosts, trusted HTTPS origins,
and HTTPS behavior as described in `render.yaml`. The API does not need a
database or user credentials. Never copy an actual secret into these files.
Keep GitHub Actions enabled and retain the workflow's read-only repository
token permissions; deployment credentials belong only in the Deploy job.

Free services may sleep or have current account limits. Allow time for startup
before the recording. Hosting restrictions, billing approval, repository access,
secret entry, and changes to repository protection all require your own account
actions. The exact GitHub/Render UI may change.

## Protect main with a GitHub ruleset

In **Settings → Rules → Rulesets**, create an active branch ruleset named
**Main**, targeting the branch `main`. The supplied rubric calls for a ruleset;
verify that your account supports its enforcement.

1. Require a pull request before merging. A solo assignment can use zero required
   reviewer approvals unless the actual course rubric requires another reviewer.
2. Require status checks: **Setup**, **Dependencies**, and **Test**, selecting the
   checks produced by this workflow. If the UI lists qualified names, select
   the matching job checks. Run the bootstrap PR once to populate the choices.
3. Require branches to be up to date before merging if available. This reruns
   checks when the target branch changes.
4. Block force pushes and branch deletion. Avoid bypass actors if the assignment
   requires demonstrating that the protection applies to your own account.
5. Do **not** require Deploy for PR merging: it intentionally skips on pull
   requests. It is verified on the push to `main` after merging.

Save and inspect the active rule and its `main` target. Test the protection by
observing the final PR's checks and merge requirements. An unsaved screenshot
or configuration guide does not prove protection is active. Ruleset enforcement
depends on repository visibility and your GitHub plan; check the displayed
availability instead of assuming the rule is enforced.

## Preserve the small final change for the camera

The prepared baseline is committed locally on `feature/module-8-ci-cd`. The final
API change and its corresponding test are intentionally left uncommitted and
unpushed: add `"demonstration": "CI/CD works!"` to `/api/hello/` and assert that
field in its test. Do not accidentally include those changes in the bootstrap
commit or initial push.

Here, “local” means this **cloud workspace**, not your personal laptop. To record
from your laptop, transfer the baseline branch and the uncommitted two-file patch
there, then check the branch and diff again. Pushing the baseline alone cannot
transfer the uncommitted patch. Keep a copy of the patch until the final commit
is safely on your feature branch.

The handoff includes `CSC325-final-camera.patch` outside the checkout. To move
the prepared change to a new laptop clone, download that patch, clone the repo,
check out `feature/module-8-ci-cd` from origin, and run `git apply` with the patch's
downloaded path. Apply it only once and inspect the diff. Do not commit or push
it until recording. You can also reproduce the two small edits from the diff.

Before recording, inspect the state:

```bash
git branch --show-current
git status --short
git diff -- api/views.py api/tests.py
python manage.py test --verbosity 2
```

The branch should be `feature/module-8-ci-cd`, and the final patch should be
limited to the API response and matching test. A normal `git push` publishes
commits, not these working-tree edits. Keep this patch while completing the
bootstrap above. If you need to switch branches or pull, first save it safely
with `git stash push -m "camera API change" -- api/views.py api/tests.py`; return
to the feature branch and use `git stash pop` before recording. Inspect the diff
after restoring it and resolve any conflict rather than overwriting work.

Once the baseline is merged, do not reuse its already-merged PR. Use the same
feature branch for a new PR containing the final camera commit. After a normal
merge-commit bootstrap, update the feature branch before recording:

```bash
git stash push -m "camera API change" -- api/views.py api/tests.py
git fetch origin
git merge --ff-only origin/main
git stash pop
git diff -- api/views.py api/tests.py
python manage.py test --verbosity 2
```

Run this only while on `feature/module-8-ci-cd` with the final patch still
uncommitted. If you already stashed it, omit the first command. If the fast
forward fails, stop and inspect the history; do not force it or drop the stash.
A squash/rebase bootstrap may need a different branch alignment because its
history differs. Never discard the working patch with `git reset --hard` or
`git clean`.

Show the prepared code change and matching test on camera, and run the local
suite. Keep the final change uncommitted until that recorded demonstration.
Commit only after reviewing the final diff:

```bash
python manage.py test --verbosity 2
git add api/views.py api/tests.py
git commit -m "Add CI/CD demonstration field to public API"
git push -u origin feature/module-8-ci-cd
```

Open the new PR into protected `main`, wait for required checks, and merge using
GitHub. The PR Deploy job will be skipped. The resulting **push to main** must
show all four jobs green. If tests fail, the workflow must stop before deploy;
do not bypass checks or mark a failure successful.

Record the feature commit SHA (`git rev-parse HEAD`), then show that commit in
the final PR. When merging, use **Create a merge commit** and set its message to
the same clear demonstration message so the resulting main run is identifiable.
A PR merge creates a different main SHA: show the PR's recorded feature commit,
its main merge SHA, and the main workflow running for that merge. The deployed
health revision must match the main run's SHA. This connects the recorded push
to the protected-main production release.

The submitted successful run must be this run caused by the change pushed and
merged **during the video**, not the earlier bootstrap run or a PR run with
Deploy skipped. Both the push and the run it causes must appear on screen.
Open the logs for **each** of Setup, Dependencies, Test, and Deploy, including
the full test result and the deployment's public checks.

## Verify the actual public release

Take the actual service origin from Render and the deployed SHA from the
successful main workflow. With your own values in place of the placeholders:

```bash
curl --fail --show-error https://YOUR-RENDER-HOST/api/hello/
curl --fail --show-error https://YOUR-RENDER-HOST/api/health/
```

The hello response must contain `"demonstration":"CI/CD works!"` after the final
merge. The health response must report `status: "ok"` and a `revision` matching
the main workflow's commit SHA. A green workflow without a verified public
response does not satisfy this check. If the endpoint returns old content, a
wrong revision, or an error, keep troubleshooting and do not claim completion.

## Five-minute screen recording

Have the editor, terminal, PR, Actions, ruleset, and public API tabs ready.
Complete hosting bootstrap beforehand so the recording demonstrates the final
small change rather than account creation. **Waiting time may be cut**, but both
the push and the run it starts must appear on screen. Rehearse and edit only the
waiting so all six parts fit within **5:00**; content after five minutes is not
graded. Never substitute a previous green run or skip required evidence.

| Time | Show and explain |
| --- | --- |
| 0:00–0:20 — 1. Introduce | Say your name and show the public repository URL. |
| 0:20–1:15 — 2. Walk the workflow | Open `csc325_ci_cd.yml`; show the push-to-main trigger and explain each of Setup, Dependencies, Test, and Deploy. Explain in one sentence why Deploy cannot start before Test succeeds (`needs: test`, the Test job's ID). Briefly show the active main ruleset and PR checks. |
| 1:15–2:05 — 3. Show the change and test | Show the uncommitted new API field and matching test; run the full local suite and show its real result. Explain what the assertions check. |
| 2:05–3:05 — 4. Commit and push | Commit with a clear identifying message and push the feature branch on screen. Show its PR and successful required checks, then merge into protected main with the same identifying merge message. Cut waiting as needed; show the feature-to-merge SHA connection. |
| 3:05–4:15 — 5. Open the triggered run | Open the **main** Actions run caused by that recorded change. Show its commit and briefly open the logs for **all four** stages in order: Setup, Dependencies, Test, Deploy. The push and this resulting run must both be visible in the video. |
| 4:15–5:00 — 6. Prove success | Show all four stages **green**, then refresh the public app to show `demonstration: CI/CD works!`. Show the health revision matching this main run's SHA. Explain the result in your own words and include any required AI-use disclosure. |

Never reveal the Render API key, Django secret, GitHub tokens, or secret values
while recording. If a real operation is still running at the allotted time,
show its true state; the recording does not yet establish a completed passing
deployment. Cut only the waiting and include the completed evidence within the
five-minute final video before submitting.

## Submission URLs to collect

Submit these **four items** in Brightspace. The assignment permits an unlisted
YouTube URL or a video-file upload for the recording. Every submitted URL must
open without login.

| Required item | URL or file to collect after completion |
| --- | --- |
| Recording, narrated and no more than five minutes | Unlisted YouTube URL accessible without login, or the video file uploaded to Brightspace. |
| GitHub repository | `https://github.com/alejops2005/CSC325-CI-CD-Django` |
| Successful final push-to-main workflow | Copy the actual Actions URL for the recorded commit's merge, showing all four green jobs and accessible stage logs. |
| Public running app from Deploy | Copy the actual HTTPS `/api/hello/` URL verified by Deploy, showing the final change. |

The final merged PR and health-check URL are useful supplemental evidence,
not replacements for the four required items. Do not invent PR,
Actions, hosting, or recording URLs before those resources exist.
Open every submitted URL in a signed-out/private browser window.
Public repository visibility does not prove an external recording is shared
publicly. Check the recording provider's sharing settings and the actual link.

## AI use and evidence

No course AI policy was provided. Check the syllabus and assignment instructions
before submitting. Disclose assistance truthfully in the location and format
the course requires; do not claim that AI use is allowed or that this text
fulfills an unknown policy. A starting point, if permitted, is:

> I used OpenAI Codex to assist with Django/DRF scaffolding, CI/CD configuration,
> tests, and setup documentation. My own review, changes, test execution, and
> deployment verification were: [describe only work you personally completed].
> [Add any other disclosure the course requires.]

Keep the local test output, final commit SHA, PR checks, main workflow result,
and live responses as evidence. Claim only outcomes you actually observed.
