# Unit 5 Alpha plan and implementation record

## Source of scope

ToS scanner pitch, revised backlog and CMSC495FALL2026 channel messages; Waylon's current scanner diagram; Unit 5/8 assignment instructions and rubrics. **All Unit 3 artifacts and requirements are excluded.** The initial eight-week AI-generated backlog is superseded where its enterprise dashboard, model training and recursive crawler were rejected. This package prioritizes the revised scanner workflow.

## Immediate release

Unit 5 (November 17, 2026): working integrated Alpha, actual AI, passing CI/CD, meaningful commits/review, formal review of a teammate's module, technical debt analysis and exactly 250 words per individual refinement report. Grade areas: functionality 40, integration 40, CI/testing 35, peer review 35, debt 30 (180 total).

Working ownership for this chat: Matt takes extension, extraction, popup/results/history, backend transport/contracts, tests and documentation; Jean owns provider invocation, prompts and risk analysis; Waylon owns architecture and the existing GitHub/Vercel setup. This reflects Matt's instruction to take unassigned implementation work, not evidence that teammates have approved all new code.

## Implemented locally

- Extension requests activeTab/scripting/storage plus only the production/local backend hosts.
- Page text is read after a user action and acknowledgement; rendered text is collected without altering the page. Navigation, footers, headers, forms and hidden nodes are excluded.
- Input is whitespace-normalized and capped at 30,000 Unicode code points before network transmission. Coverage metadata discloses truncation. Backend refuses oversized text rather than silently truncating it again.
- Popup handles consent, loading, disabled duplicate scans, transport/timeout errors, mock marking, findings with exact quotations, partial results and local history of five summaries.
- Backend preserves the backlog's three response fields and adds evidence, mode and coverage. It checks the schema and exact quotation substrings before returning results.
- FastAPI adapter accepts bounded bodies, sanitizes validation/provider errors, uses no-store responses and configurable extension CORS.
- Mock scenarios cover findings, none and failure. Setting ai calls the isolated, currently unimplemented adapter and returns a clear error until Jean implements it.
- No database, enterprise dashboard, recursive crawler, model training, account system or Unit 3 interfaces were added.

## Integration steps

1. Add this package's new files on feat/unit5-alpha-foundation in an actual clone; keep existing README and teammate changes.
2. Install requirements-dev.txt; run complete Python/JS suite; resolve any HTTP test failures before review.
3. Load unpacked extension in a real browser and run docs/MANUAL_TESTS.md.
4. Preview-deploy FastAPI on Vercel and check real HTTP routes and CORS; use narrow preview host permissions if needed.
5. Jean implements backend/ai_adapter.py against docs/AI_HANDOFF.md; configure server-side credentials/model and provider spending controls.
6. Run opt-in live-model evaluation and the complete extension-to-provider workflow. Compare actual timings with the three-/four-second proposed targets.
7. Obtain actual peer reviews, record changes and debt, complete the 250-word refinement report and identify the Alpha release commit.

## Documented design decisions

- Vanilla JS/HTML avoids a frontend build toolchain for a small extension.
- A normal FastAPI root entrypoint is used for Vercel; no static website or obsolete routing rewrites are required. Deployment remains unverified.
- UI text uses DOM textContent to prevent model/page content becoming executable markup.
- Browser history persists summaries only, with a clear control for local deletion.
- CORS restricts browser origins but is not authentication. Paid inference must have spending controls and a chosen access/rate-limit strategy before unrestricted public use.
- Mock mode is explicit. Unit 5 readiness requires real AI and cannot be inferred from a mock test pass.

## Technical debt / limitations

| Item | Impact | Next action |
|---|---|---|
| AI adapter absent | No actual clause screening; Unit 5 release blocked | Jean implements and validates provider integration |
| No distributed rate limiting/authentication | Public paid inference could incur unwanted usage | Choose access/quota strategy and enforce provider spending controls before live exposure |
| Popup-scoped requests | Closing popup cancels scan | Accept/document for Alpha; background service worker later if needed |
| First 30k extracted characters | Later clauses may be missed | Display partial status; evaluate coverage; consider sectioning after Alpha |
| Generic DOM extraction | Some layouts, PDFs, iframes or shadow DOM may be incomplete | Real-platform manual tests; document limitations |
| Dependency version ranges | Builds may change with compatible updates | Pin tested versions after full environment validation |
| Static backend host allowlist | Preview URLs need explicit local configuration | Keep narrow for Alpha; documented preview procedure |
| Framework/browser/deployed checks pending | Local unit tests alone cannot establish system readiness | Complete validation checklist and record evidence |

## Unit 8 preparation

Final portfolio due December 8, 2026: final integrated repository, comprehensive docs, CI/deployment screenshots, review and coverage evidence, performance/reliability metrics, team contribution records; team 10–15 minute stakeholder video with live AI demo; individual 1,300-word PDF (delivery 400, evaluation 450, development roadmap 450). Maintain real evidence from now on. No final video, position paper, fabricated reviews, model-accuracy claims or invented performance results are supplied in this Alpha package.

## References used for implementation

- https://vercel.com/docs/frameworks/backend/fastapi
- https://developer.chrome.com/docs/extensions/reference/api/scripting
- https://developer.chrome.com/docs/extensions/develop/concepts/activeTab

These are implementation references; they do not supply validation results for this project.
