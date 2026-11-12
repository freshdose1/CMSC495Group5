# What was built, in plain language

This is the application's Alpha foundation. It supports mock analysis so Matt's application work can be developed while Jean implements AI. It is not yet a working AI release.

1. The user opens a public agreement and the extension popup. Nothing is sent until the user acknowledges the notice and clicks Scan.
2. extension/extract.js reads rendered page text and excludes common navigation, forms and hidden content. extension/core.mjs normalizes whitespace and limits the outgoing text to 30,000 Unicode characters. It records whether anything was cut off.
3. extension/popup.mjs sends that payload to POST /api/analyze. It disables duplicate scans, reports progress, applies a timeout and displays readable errors.
4. backend/api.py handles HTTP, body-size protection, input validation and CORS. backend/contracts.py defines exactly which inputs and outputs are valid.
5. backend/service.py chooses mock or AI mode. Mock mode produces conspicuously labelled demonstration data. AI mode calls Jean's function in backend/ai_adapter.py, which currently raises an unavailable error.
6. The service verifies each returned quote is present in the submitted text. It adds coverage and limitations and derives the older red_flags field from the finding explanations.
7. The popup displays those findings as expandable cards, shows partial/mock notices and stores only the last five summaries on the device. It uses plain text rendering so model content cannot become HTML.

## Important file map

| File | Purpose |
|---|---|
| app.py | Vercel/local FastAPI entry point |
| backend/contracts.py | Request, finding, response and coverage definitions |
| backend/service.py | Processing rules and response validation |
| backend/ai_adapter.py | Jean's provider integration boundary |
| extension/popup.html, popup.css, popup.mjs | User interface and interaction |
| extension/extract.js | Page-text extraction |
| extension/core.mjs | Shared input, transport, history and response logic |
| .github/workflows/alpha-ci.yml | Automated Python/JavaScript checks for GitHub |
| tests/ | Unit, transport, planned HTTP/browser checks and annotated fixtures |
| docs/AI_HANDOFF.md | What Jean must return and how to integrate |
| docs/VALIDATION.md | What was actually tested and what remains pending |

## Next practical steps

Add the files on a feature branch in the shared repo; install dependencies and run all tests; load the extension and verify it against the local backend; review the code with teammates; deploy and verify a Vercel preview; connect real AI; run the release checklist. The existing team's README.md is deliberately not included/replaced by this package.

The GitHub/Vercel connection already existed. This package does not contain evidence of a new GitHub push or deployment. The present Python/JavaScript test passes establish only their specific tested behavior.
