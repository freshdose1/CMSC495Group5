# Jean's Python integration — setup and review

## Why this replaces the standalone JavaScript module

The shared repository uses FastAPI/Python. Its documented integration boundary is
`backend/ai_adapter.py::analyze_with_ai(text)`. This implementation uses that boundary;
it does not add a Node server or change the extension/API contract.

| Standalone concept | Team contract |
| --- | --- |
| content_rights | content_license |
| data_sharing | third_party_sharing |
| retention_deletion | data_retention |
| liability_disputes | arbitration (only arbitration/dispute restrictions in scope) |
| evidence_quote | quote |
| Per-finding severity | Not part of the team contract |
| Unknown on failure | HTTP error with no risk result |

The prompt now requests the team's four categories directly. It is not a mechanical
conversion of every prior category. AI training and unilateral changes are not
separate categories in this version. Summary and evidence checks remain in the
application layer. The HTTP result deliberately has no additional model field,
because the interface is owned by the team. For router runs, inspect OpenRouter
Activity to identify the actual model and record it in evaluation notes.

## Local setup (Windows, from the cloned repository root)

Use Python 3.12 or newer and Node.js 22 or newer (for extension tests).

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
node --test tests/extension.test.mjs
```

The team's Python application does not automatically load `.env`. Your separate
JavaScript package's .env is not read by this application.

## Opt-in live synthetic test

```powershell
$env:OPENROUTER_MODEL = 'openrouter/free'
.\.venv\Scripts\python.exe scripts/smoke_ai.py --live
```

The script asks for the key with hidden input if it is not already in the environment.
Paste the key and press Enter; no characters appearing is expected. It sends a
synthetic example once. No automated tests call the real provider. Model availability
is not guaranteed. The free router can vary its choice between requests. Use a fixed
model for reproducibility after verifying its availability, JSON-mode support and cost.
No paid fallback is configured. The old google/gemma-2-9b-it value is removed from the
example configuration because Jean's live request reported it retired.

## Start the API for extension testing

In PowerShell, configure the key without putting its literal value in command history:

```powershell
$env:ANALYSIS_MODE = 'ai'
$env:OPENROUTER_MODEL = 'openrouter/free'
$secureKey = Read-Host 'OpenRouter API key' -AsSecureString
$env:OPENROUTER_API_KEY = [System.Net.NetworkCredential]::new('', $secureKey).Password
Remove-Variable secureKey
.\.venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000/docs and use POST /api/analyze with synthetic text first.
A health response only confirms the HTTP service is running. Then follow the extension
loading instructions in README_ALPHA.md; select http://127.0.0.1:8000 in its Settings.
Stop the server with Ctrl+C. Remove the shell key when finished:

```powershell
Remove-Item Env:OPENROUTER_API_KEY
```

Never commit keys or add them to the extension. Keep provider error details private;
the adapter intentionally exposes only sanitized errors through the API.

## Scope and limitations

- JSON mode is used with the schema in the prompt. Local Pydantic validation and exact
  substring checks enforce the output contract; JSON mode alone does not enforce it.
- One request per analysis, max 3000 output tokens, 18-second HTTP I/O phase timeout,
  no automatic retries, no redirects, and 256KB maximum decoded response body.
- An I/O timeout is not a total wall-clock deadline; slow streaming can extend elapsed
  time. The three/four-second latency target remains unverified.
- The team contract has only Low/Medium/High. It cannot express an Unknown success
  assessment. Irrelevant text is described as insufficient in the summary with zero
  findings and Low, per the existing contract. Discuss a distinct unassessable status
  with Matthew before release; do not present this as a safety judgment.
- Public paid inference still needs the access/rate-limit plan called out in the
  existing API contract. No deployment changes were made here.

## Validation of this repository adaptation

35 Python tests passed (plus 38 passing unittest subtests), and 9 Node extension tests
passed locally. There is one Starlette test-client deprecation warning with the
installed dependency versions; no test failed or skipped.
Provider tests mock HTTP, including success through the FastAPI route, authentication/
quota/provider failures, timeouts, invalid output, fabricated evidence, wrong categories,
truncation, redirects and bounded response size.

Jean previously ran two live examples with the separate JavaScript module: one High
content-rights result and one Low retention result. Those demonstrate the earlier
module's connection, not this Python adapter's live behavior.

Local live validation completed: the Python smoke test, HTTP API request,
and browser-extension scans succeeded using openrouter/free. Two browser
scans of the same 285-character synthetic agreement returned High risk
and findings for content licensing, third-party sharing, and data retention.

These results do not establish accuracy or consistent performance across
documents. Remaining work includes the full annotated synthetic suite,
five public agreements, latency and consistency evaluation, deployed
verification, and teammate review. Known issues include Low-risk results
for unrelated text and occasional unsupported inferences in explanations.

## Suggested pull request text

Title: Implement Jean's OpenRouter AI adapter

Replaces the AI placeholder with a configurable OpenRouter JSON-mode client using the
existing FastAPI contract. The prompt screens four agreed categories, treats agreement
content as untrusted, and requires supporting quotations. Application validation rejects
invalid findings; provider failures remain sanitized errors without risk results.

Adds mocked provider/API tests, a gated live smoke command, and Windows setup notes.
Moves httpx to runtime dependencies and removes the retired example model.

Validation: 35 Python tests and 9 extension tests passed locally. Live Python model,
browser and deployed integration checks remain pending. JSON mode does not enforce
schema server-side; local validation remains required.
