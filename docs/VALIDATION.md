# Validation record

Recorded during initial local Alpha implementation, November 10, 2026 (Pacific date).

## Executed

- Python 3.12 runtime: 13 contract/service unit tests passed.
- Seven FastAPI HTTP integration tests were skipped because FastAPI/httpx could not be installed in this restricted session. They have not passed here.
- Node.js 24: nine JavaScript contract/transport/history tests passed, including the final response-validation hardening.
- Python source compilation and JavaScript parser checks passed.

## Not established

- A complete passing installed-dependency test run or coverage percentage.
- GitHub branch, commit, PR or CI execution. Clone failed because the terminal could not resolve github.com. Files are delivered as additions for a real clone, preserving the upstream README.
- An installed-extension browser run, deployed FastAPI route verification or actual OpenRouter inference.
- Model accuracy, five-platform agreement evaluation, latency target, teammate review or Unit 5 submission readiness.

Tests added to CI use mocked providers and never make paid inference requests. Do not describe mock success as functional AI.

An isolated headless Edge component-check launch was attempted, but the browser exited before tests started with access-denied/profile initialization errors. No browser assertions ran. tests/browser-check.cjs is supplied for an unrestricted local test environment; it requires Playwright (`npm install --no-save playwright`) and an installed Edge browser. Run `node tests/browser-check.cjs` after installation. This checks DOM extraction and popup behavior with simulated Chrome APIs; the installed-extension checklist remains separate.

Final executed counts: **22 passed** (13 Python + 9 JavaScript), **7 HTTP tests skipped**, **0 browser checks executed**. Full CI, coverage, deployed HTTP and actual AI remain pending.
