# ToS Scanner — Unit 5 Alpha foundation

This package contains **new files to add to freshdose1/CMSC495Group5**. Preserve the existing README.md and any newer teammate changes. It was prepared locally because this session could not clone GitHub. No branch, commit, pull request or Vercel deployment has been created by this work.

Implemented: Manifest V3 extension; visible active-page extraction; explicit transmission acknowledgement; capped input; evidence-based results rendering; local history of five summaries; configurable production/local backend; FastAPI routes; strict contracts; mock scenarios; AI adapter boundary; automated tests and CI configuration.

**AI integration is intentionally unimplemented. This is not a submission-ready Alpha until the release gates below pass.** Mock results are clearly labelled. Unit 3 work is excluded completely.

## Run locally

Use Python 3.12 or newer and Node.js 22 or newer for JavaScript tests (Node is a development tool; the backend runs Python).

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
$env:ANALYSIS_MODE = 'mock'
$env:MOCK_SCENARIO = 'findings'
.\.venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8000
```

Linux/macOS equivalent: activate .venv, install requirements-dev.txt, and run `ANALYSIS_MODE=mock uvicorn app:app --host 127.0.0.1 --port 8000`.

Open http://127.0.0.1:8000/api/health and /docs. `.env.example` documents configuration; the app does not automatically load .env files.

## Load the extension

In Edge open edge://extensions (Chrome: chrome://extensions), enable Developer Mode, choose Load unpacked, and select `extension/`. Pin/open ToS Scanner Alpha. In Settings choose http://127.0.0.1:8000 and save. Open a **public** agreement page, acknowledge the transmission notice, then Scan. Browser internal/store pages are restricted; extraction failures are displayed. This package targets Chromium (Edge/Chrome); Firefox compatibility has not been implemented or tested.

For a controlled sample, run `python -m http.server 8080 --directory tests/fixtures` in another terminal and open http://127.0.0.1:8080/agreement.html. The main-page scan should exclude nav/footer/hidden content and form values. Mock mode returns an example finding from the submitted text; it does not classify the agreement.

History saves only hostname, time, mode, status, risk label and summary locally. It excludes full agreement text and quotation lists. Clear History removes stored entries. Results persist across popup reopenings in History; closing the popup cancels an active scan. All displayed server content uses textContent, never HTML injection.

## Test

```powershell
.\.venv\Scripts\python.exe -m pytest --cov=backend --cov-report=term-missing --cov-report=xml -q
node --test tests/extension.test.mjs
```

Without pytest, core tests can run with `python -m unittest discover -s tests -p 'test_*.py' -v`; FastAPI HTTP tests skip if dependencies are absent. A skipped test is not a passing integration check. See docs/VALIDATION.md for this session's actual results.

## Put the additions into GitHub

In a real clone of the shared repository:

```text
git switch main
git pull origin main
git switch -c feat/unit5-alpha-foundation
```

Copy this package's contents into that clone (including .github and .gitignore), preserving existing files and resolving any conflicts. Do not copy .venv, caches, secrets or this package's outer folder. Review `git status` and changes; commit the new files, push the feature branch and open a PR for teammate review. Append a link to README_ALPHA.md to the existing README rather than replacing the team's instructions.

## Vercel

The root app.py exports the FastAPI app and requirements.txt declares its dependencies. Use the repository root as the project root and the FastAPI framework preset. Existing project settings may need adjustment from the earlier README-only deployment. Set ANALYSIS_MODE=mock for a labelled preview; ALLOWED_ORIGINS can restrict calls to exact installed extension origins. Do not enable ai until Jean's adapter exists and server credentials are configured. No provider secrets belong in the extension or GitHub.

Validate `/`, `/api/health`, `/docs` and `/api/analyze` on a preview deployment before merge. The extension currently allows production plus local development addresses only. To test a Vercel preview, explicitly add that exact origin to manifest host_permissions and core.mjs's allowed endpoint list; reload the extension. Do not grant blanket access to all hosts.

The Vercel Git integration deploys; GitHub Actions runs tests. Confirm successful results in **both** systems before releasing. The existing Vercel integration may deploy independently of GitHub test results; protect main with the Alpha checks requirement through the team's normal repository controls.

## Unit 5 release gates

- [ ] All current MVP paths pass browser testing and deployed HTTP tests.
- [ ] Jean's real AI adapter is connected; malformed output and provider failures are handled.
- [ ] Quoted evidence is verified against source; truncated scans are disclosed.
- [ ] CI passes and the deployed application works.
- [ ] Teammates perform actual peer reviews and changes are recorded.
- [ ] Technical debt is documented honestly.
- [ ] Each member prepares their exactly 250-word refinement report from actual feedback.

See docs/ALPHA_PLAN.md for scope, ownership, evidence and Unit 8 preparation.
