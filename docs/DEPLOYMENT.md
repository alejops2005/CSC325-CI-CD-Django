# CSC 325 deployment setup

This repository requires an actual Render Web Service before Deploy can succeed.

1. Create a Render Python web service/Blueprint using `render.yaml`, attached to this PUBLIC repository and main branch. Confirm the current plan and billing, and turn OFF automatic deploys.
2. In Render, set `DJANGO_DEBUG=false`, create a strong `DJANGO_SECRET_KEY`, configure `DJANGO_ALLOWED_HOSTS` for the Render hostname, and set `APP_REVISION` to the deployed SHA if the service does not provide `RENDER_GIT_COMMIT`.
3. In GitHub Settings > Secrets and variables > Actions, create secrets `RENDER_API_KEY` and `RENDER_SERVICE_ID`; create variable `APP_BASE_URL` with the actual Render HTTPS origin (without `/api/`).
4. Confirm Render is able to deploy the requested SHA and that its runtime exposes the SHA as `RENDER_GIT_COMMIT`. Configure a Render start or environment mechanism if needed; do not report successful verification without seeing the SHA match.
5. Create a PR and check Setup, Dependencies, Test. After it passes, require these check names in the main branch ruleset. Merge into main. The main push runs all four stages. Fix red runs before recording.
6. Reserve a small endpoint+test change for the recorded feature-branch push and protected-main merge. The final submitted Actions URL must be the main run caused by that on-camera change.

The project cannot be considered deployed until the live public URL and successful GitHub run have both been verified. Never commit API tokens.
