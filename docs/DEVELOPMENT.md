# Development setup

For extension installation and the optional sample page, start with the [project README](../README.md). This guide covers running and testing the backend yourself.

## Run the backend locally

Use Python 3.12 or newer. Run these PowerShell commands from the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
$env:ANALYSIS_MODE = 'mock'
$env:MOCK_SCENARIO = 'findings'
.\.venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8000
```

Leave the terminal open. Check [health](http://127.0.0.1:8000/api/health) and [API documentation](http://127.0.0.1:8000/docs). In the extension's Settings, save `http://127.0.0.1:8000` to use this backend. Port **8000** serves the backend; port **8080** in the README serves only the optional test page.

On Linux/macOS, create and activate `.venv`, install `requirements-dev.txt`, then run `ANALYSIS_MODE=mock uvicorn app:app --host 127.0.0.1 --port 8000`.

[.env.example](../.env.example) documents configuration. The app does not automatically load `.env` files. Mock scenarios are `findings`, `none` and `failure`; change `MOCK_SCENARIO` and restart the server to exercise them. Mock findings demonstrate the interface, not clause classification. Closing the popup cancels an active scan.

## Automated and browser checks

Node.js 22 or newer is needed only for JavaScript tests. The backend uses Python, and the extension has no build step.

```powershell
$env:REQUIRE_HTTP_TESTS = '1'
.\.venv\Scripts\python.exe -m pytest --cov=backend --cov-report=term-missing --cov-report=xml -q
node --test tests/extension.test.mjs
```

Without pytest, core tests can run with `python -m unittest discover -s tests -p 'test_*.py' -v`. HTTP tests may skip if dependencies are absent; a skipped test is not a passing integration check. Use [MANUAL_TESTS.md](MANUAL_TESTS.md) to verify the installed extension, including excluded navigation/form text, consent, failures, truncation and five-entry history. Record actual results in [VALIDATION.md](VALIDATION.md).

## Vercel and AI configuration

Use the repository root as the Vercel project root and **FastAPI** as the framework preset. Root `app.py` exports the app; `requirements.txt` declares runtime dependencies. Set `ANALYSIS_MODE=mock` for a labeled demonstration. `ALLOWED_ORIGINS` can restrict browser calls to exact installed-extension origins; CORS is not authentication.

Real AI requires the adapter in `backend/ai_adapter.py` to be implemented against [AI_HANDOFF.md](AI_HANDOFF.md), server-side provider credentials/model configuration, and provider spending/access controls. Keep secrets out of the extension and GitHub. Do not switch to `ai` before the adapter is ready.

Validate `/`, `/api/health`, `/docs` and `/api/analyze` on the deployment. Health confirms service availability, not successful AI analysis. The extension allows only the production backend and local development addresses. To test a Vercel preview, add its exact origin to both `extension/manifest.json` host permissions and the endpoint allowlist in `extension/core.mjs`, then reload the extension. Avoid blanket host access.

GitHub Actions runs tests; the Vercel Git integration deploys independently. Confirm both succeed before release and use the team's PR review requirements. Start new work from the latest `main`, following the [README contribution steps](../README.md#how-to-make-a-pull-request); the original Alpha foundation PR #3 has already been merged. Do not commit environments, caches or secrets.

## Alpha completion

The mock foundation includes page extraction, results/history, transport and validation. Unit 5 still requires real AI, complete browser/deployed testing, quote verification, passing CI/deployment, actual peer review, documented debt and each member's exactly 250-word refinement report. See [ALPHA_PLAN.md](ALPHA_PLAN.md) for the full scope, ownership and Unit 8 preparation. Dated validation notes describe specific checkpoints, not a guarantee that all release gates are complete.
