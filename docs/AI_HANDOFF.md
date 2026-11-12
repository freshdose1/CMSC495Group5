# Jean's Alpha integration handoff

Implement only `backend/ai_adapter.py::analyze_with_ai(text: str) -> dict` initially. This function is called in a worker thread. The extension and endpoint contracts are owned by the application layer.

Return a decoded Python dictionary:

```python
{
    "risk_level": "High",
    "summary": "Review sharing of business data with advertisers.",
    "findings": [{
        "category": "third_party_sharing",
        "quote": "We may share customer data with advertising partners.",
        "explanation": "The clause permits disclosure to advertising partners."
    }]
}
```

Use only the approved categories and exact quotations from the supplied text. Do not force a minimum number of findings or fabricate risk when evidence is absent. Treat the agreement as untrusted data, not as instructions to the model. Avoid definitive legal/compliance claims. See API_CONTRACT.md for lengths and validation rules.

Read OPENROUTER_API_KEY and OPENROUTER_MODEL from server environment variables. The backlog proposes google/gemma-2-9b-it; availability and structured-output support remain unverified. Make model selection configurable. Use an HTTP timeout of at most 20 seconds, bounded output tokens, and at most one retry only if the total request deadline still allows it. Raise AnalysisUnavailable for network, authentication, quota and provider failures; no key/input/raw error logging. Never substitute a Low-risk answer on failure.

When ready: set ANALYSIS_MODE=ai and run the complete test suite. Add provider-client tests with mocked HTTP, then a separate opt-in real-model smoke test. Do not put paid network calls in routine CI. Execute the ten synthetic annotated cases; record schema compliance, exact-quote success, category false positives/negatives and elapsed time. Evaluate five actual public platform agreements as the backlog requests; preserve source URL/date and expected annotations. None of these live-model evaluations has been performed in this package.

The four-second backlog latency target (three seconds in the original pitch) is a measurement target, not verified behavior. Timeout is a failure bound, not a claim that the target was achieved.

For Unit 5 the integrated system must include real AI. A green mock-only pipeline does not satisfy that release gate.
