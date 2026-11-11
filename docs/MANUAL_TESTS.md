# Alpha browser / deployment acceptance checklist

Status: pending in an installed extension and deployed FastAPI environment. Headless component checks, when run, do not establish installed-extension permissions or production readiness.

Record tester, browser/version, commit, endpoint, date and actual results. Use public or synthetic agreements only.

1. Open backend /api/health and /docs; verify expected mode. Confirm /api/analyze on the deployed origin, not just health.
2. Load extension; choose local backend; acknowledgement unchecked means Scan disabled.
3. Serve tests/fixtures/agreement.html on port 8080. Scan after acknowledgement. Expect prominent mock warning, quote from supplied text and a summary saved to History. Verify nav/footer/hidden text and form values are absent from submitted payload using local developer tools.
4. Open a chrome:// or edge:// page. Scan should show a readable restriction error; no risk result.
5. Set MOCK_SCENARIO=none and restart backend. Expect mock success with no findings, not an analysis failure or Safe claim.
6. Set MOCK_SCENARIO=failure. Expect error banner and enabled retry, no stale results presented as current analysis.
7. Stop backend. Expect connection/timeout error. Closing/reopening popup cancels active work and is documented.
8. Scan content exceeding 30,000 characters. Expect partial status and correct original/submitted lengths. Test emoji near boundary.
9. Complete six scans. Expect newest five history summaries; Clear History empties them. Full agreement text and finding quotes must not be stored.
10. Try invalid/arbitrary backend URL in Settings. It must be rejected. Verify server-origin CORS and manifest host permissions separately.
11. With Jean's real adapter and ANALYSIS_MODE=ai, repeat successful, empty, partial, provider timeout, invalid JSON and unsupported-quote cases. Confirm actual model invocation and no mock banner only when real AI is used.
12. Run ten annotated synthetic cases and five public platform agreements, recording source/version, expected findings, exact quotes, schema failures, category errors and elapsed time. Review negations to catch false positives.
13. Verify CI succeeds on the reviewed PR and deployment succeeds. Capture submission evidence only after successful runs.

Real-world agreements are not included as copied snapshots. The team must select public pages and annotate the relevant clauses before claiming accuracy results.
