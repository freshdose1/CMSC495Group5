# Alpha API contract — version 1.0

Scope: ToS scanner only. No Unit 3 documents, interfaces or hypothetical chatbot requirements were used.

`POST /api/analyze`, `Content-Type: application/json`.

```json
{"text":"We may share customer data with advertising partners.","original_length":53,"truncated":false}
```

`text` is required, normalized, non-empty and at most 30,000 Unicode code points. The actual example text above is 53 characters. `original_length` and `truncated` are optional for direct callers; omitted length means the submitted length. If length exceeds the submitted text, truncated must be true. Unknown fields and wrong types are rejected. Request bodies over 256,000 bytes are rejected before validation.

Success, HTTP 200:

```json
{
  "schema_version":"1.0",
  "request_id":"generated-uuid",
  "mode":"mock",
  "status":"complete",
  "risk_level":"Medium",
  "summary":"MOCK RESPONSE: sample results only. This agreement has not been evaluated by AI.",
  "red_flags":["Example finding for interface testing; no AI evaluation occurred."],
  "findings":[{"category":"third_party_sharing","quote":"We may share customer data with advertising partners.","explanation":"Example finding for interface testing; no AI evaluation occurred."}],
  "coverage":{"submitted_characters":53,"original_characters":53,"truncated":false},
  "limitations":["Clause screening supports human review; it does not determine legal compliance.","Mock mode: no model was called and no risk assessment was performed."]
}
```

The three backlog fields `risk_level`, `summary`, `red_flags` remain available. `findings` adds evidence and categorization; `coverage`, `mode`, and `status` disclose mock/incomplete work. The backend derives red_flags from explanations so they cannot contradict findings. Risk is Low, Medium or High; it is never called Safe. Categories: content_license, third_party_sharing, data_retention, arbitration (included in the team's revised backlog).

Every quote must be an exact substring of submitted text. At most eight findings, each with quote and explanation up to 1,200 characters. The AI adapter should normally return 2–4 findings when supported; zero is valid when none are identified. Elevated risk without evidence is rejected. `complete` means the submitted text was processed, not that every linked policy or every legal issue was reviewed. Truncated input produces `partial`.

Errors contain **no risk result**:

```json
{"error":{"code":"AI_UNAVAILABLE","message":"AI analysis is currently unavailable.","retryable":true}}
```

| HTTP | Code | Meaning |
|---|---|---|
| 413 | REQUEST_TOO_LARGE | Body byte limit exceeded |
| 422 | INVALID_REQUEST | Invalid JSON, text, types or coverage metadata |
| 502 | INVALID_AI_OUTPUT | Schema failure, invented quotation, unsupported risk result |
| 503 | AI_UNAVAILABLE | Adapter absent or provider failure |
| 503 | MOCK_FAILURE | Explicit test scenario |
| 503 | CONFIGURATION_ERROR | Invalid server mode/scenario |

`GET /` identifies the service. `GET /api/health` reports HTTP availability and configured mode; it does not certify AI readiness. `/docs` and `/openapi.json` expose FastAPI's generated interface documentation. Analysis responses use Cache-Control: no-store.

The default CORS rule accepts extension origins; set ALLOWED_ORIGINS to exact installed extension origins for deployment. CORS is not authentication or rate limiting. This Alpha has no login or distributed quota protection; add provider spending limits and an access/rate-limit strategy before opening paid inference to unrestricted traffic.
