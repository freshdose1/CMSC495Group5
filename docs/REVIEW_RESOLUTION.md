# Automated review assessment

November 11, 2026. Amazon Q Developer review on PR #3 was checked against framework behavior and regression tests. Automated comments are review input, not proof of a defect; teammate review is still required.

## CORS origin matching

The claim that Starlette uses `re.search()` is incorrect for the tested dependency: it uses regex **fullmatch**. The original extension-only expression already rejected a suffix such as `.evil.com`. Explicit `\A` and `\Z` anchors were nevertheless added to make the policy clear. Tests accept a valid extension ID and reject suffix/prefix attacks, wrong ID length, invalid characters, null origin and an ordinary website.

Reference: [FastAPI middleware source reference, is_allowed_origin](https://fastapi.tiangolo.com/reference/middleware/#fastapi.middleware.cors.CORSMiddleware.is_allowed_origin).

## Middleware order

The last-added middleware runs first, but CORS outside the size limiter is intentional: an allowed extension needs CORS headers on the **413** response to read its explanation. CORS does not authenticate a caller, authorize paid inference or consume a POST body before delegating. Moving BodyLimit outside it would hide those error details from browser clients. Tests confirm oversized requests still return 413 with the permitted origin and no-store headers; a preflight is answered without reading a body or calling the endpoint.

Before real paid AI is exposed, the team must choose actual access and spending controls; CORS alone is not such a control.

## Unread request bytes after rejection

The generic claim that returning 413 without draining necessarily stalls Uvicorn is not supported by its [documented response-completion behavior](https://uvicorn.dev/server-behavior/#response-completion). Uvicorn stops buffering the remaining body after the response; subsequent receive calls return disconnect. An application-level loop waiting for an arbitrary upload tail could itself stall. The middleware therefore completes the error response promptly rather than adding an unbounded drain loop. Vercel's edge/server transport remains responsible for its own connection handling; no live keep-alive transport benchmark is claimed.

A real improvement was made here: check the accumulated size **before copying** a new chunk into the application's buffer. ASGI tests verify rejection of a multi-chunk oversized stream without waiting for the upload tail, and lossless replay of an upload exactly at the configured limit.

## Whitespace validation

No change: rejecting whitespace-only inputs is intentional. The bot itself withdrew this finding. Existing tests cover empty/whitespace/non-string inputs and Unicode length limits.

See VALIDATION.md for executed tests, deployment observations and remaining release gates. This automated review does not replace the Unit 5 teammate review or individual refinement report.
