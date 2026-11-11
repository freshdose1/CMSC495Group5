# Validation record

Updated November 11, 2026 (Pacific date). This supersedes the initial local-only checkpoint of November 10.

## Executed locally

- Python 3.12.14: **24 tests passed**, zero skipped, including HTTP integration and streamed-body middleware tests. Pytest also reported 18 passing subtests; these are not counted as additional tests.
- Backend **line coverage: 97%** (140 of 144 statements). Coverage is not a measure of model accuracy or release completeness.
- Node.js 24: **nine tests passed**, zero skipped, covering payload preparation, Unicode truncation, endpoint restrictions, response contracts, errors, timeout and history limits.
- `git diff --check` passed.
- Dependencies installed into an isolated local test directory: FastAPI 0.162.4, Starlette 1.10.0, Pydantic 2.14.3, Uvicorn 0.54.0, httpx 0.28.1, pytest 9.2.0 and pytest-cov 7.1.0. Dependency ranges remain in requirements files; CI may resolve different versions.
- One non-failing Starlette deprecation warning recommends migrating the test client from httpx to httpx2. This is follow-up maintenance, not a failed assertion.

Commands: `python -m pytest --cov=backend --cov-report=term-missing --cov-report=xml -q` with `REQUIRE_HTTP_TESTS=1`, then `node --test tests/extension.test.mjs`. Test providers are mocked and make no paid inference calls.

## Publication and deployed checks

- Source is published in [PR #3](https://github.com/freshdose1/CMSC495Group5/pull/3), branch `feat/unit5-alpha-foundation`. Main has not been merged or bypassed.
- The [first GitHub Actions run](https://github.com/freshdose1/CMSC495Group5/actions/runs/43088031874) could not start its job: GitHub reported the account locked due to a billing issue. The repository owner must resolve that issue and rerun checks. Local passing tests do not establish a passing GitHub CI run.
- Vercel's initial Other framework setting produced a Ready deployment with a 404 response. The setting was changed to **FastAPI**, repository root unchanged, and the user completed email verification/redeployment.
- [Preview health](https://cmsc495group5-git-feat-unit5-alpha-foundation-cmsc-495.vercel.app/api/health) returned `status: ok`, `analysis_mode: mock`.
- [Swagger UI](https://cmsc495group5-git-feat-unit5-alpha-foundation-cmsc-495.vercel.app/docs) loaded. A synthetic POST to `/api/analyze` returned **HTTP 200**, `mode: mock`, a conspicuous no-AI warning and an exact quotation of the submitted 53-character sample. No real agreement or provider credential was used.
- These deployed observations were made on source commit `4d36dbf`, Vercel deployment `DPtXkBRDYVUpQTVPYTJBifgPi2LW`, before the review hardening patch. The patch has separate local regression results above; verify its next preview after push.
- The Vercel email said **Ready**; the critical comments in the same Gmail thread came from **Amazon Q Developer**, not Vercel. See REVIEW_RESOLUTION.md.

## Still required for Unit 5

- A passing GitHub CI run and at least one teammate approval; billing and review requirements remain in place.
- Installed-extension testing across extraction, consent, results, failures and five-scan history. The optional isolated Edge component runner was retried but browser startup failed with OS access-denied errors before assertions ran. **Zero browser component assertions ran.** This is separate from the successful live API checks above.
- Real OpenRouter integration, model selection/availability, malformed output and timeout evaluation, annotated agreement evaluation and measured latency.
- Production deployment and a complete extension-to-backend end-to-end check after review/merge.

Current automated result: **33 tests passed** (24 Python + 9 JavaScript), zero skipped. Real AI, installed-extension behavior and GitHub CI remain unverified. Mock success is not functional AI.
