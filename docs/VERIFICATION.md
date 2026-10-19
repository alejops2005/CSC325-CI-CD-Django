# Verification and remaining work

Verified in the cloud workspace on 2026-10-19:

- Baseline full suite: **22 tests passed** (5 API tests and 17 deployment-helper
  tests). Helper tests mock hosting responses; they do not prove a Render deploy.
- The pinned wheelhouse installed in a fresh virtual environment without an
  index, and the full suite passed there, matching the CI dependency handoff.
- A temporary failing assertion made the full Django test command exit **1**.
  The temporary probe was removed; failures are not suppressed by the workflow.
- Django system checks, production deployment checks with warnings treated as
  failures, dependency consistency, and migration drift checks passed.
- `actionlint` 1.7.7 accepted the workflow. Its downloaded release archive was
  checked against the publisher's SHA-256 checksum.
- Gunicorn served both JSON API endpoints successfully over internal HTTP;
  health returned the configured local revision. This is local validation.
- A request without supplied GitHub credentials reached the repository page;
  HTTP 200, the Public label, and repository public metadata were observed.
- Reusable installation/startup instructions and required network destinations
  were saved to the cloud environment draft. Draft persistence does not mean
  publication, runtime network changes, or validation in a new task occurred.

Not verified or completed here:

- GitHub API calls returned Forbidden. Creating the bootstrap PR, inspecting or
  changing the main ruleset, inspecting Actions secrets, and validating hosted
  Actions runs were unavailable through that API. Native Git reads work.
- No Render credential bindings, service, or assigned live URL were available.
  Hosting creation, repository authorization, possible billing, and GitHub
  secret/variable entry require the user's account actions.
- No real deployment, green four-job hosted run, or live public API response has
  been verified. Do not submit the local checks as proof of those outcomes.
- The tutorial's exact Python version and course AI policy were not supplied.
  The project uses Python 3.12. Check the tutorial and disclose help as required.

Follow [ASSIGNMENT.md](ASSIGNMENT.md) to finish bootstrap, protect main, record
the final two-file change, and collect the four required submission items.
