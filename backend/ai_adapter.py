"""JEAN'S IMPLEMENTATION BOUNDARY. See docs/AI_HANDOFF.md.

Replace this function's body with the OpenRouter call. Do not return mock
results from this adapter. Configure credentials only on the server.
"""


class AnalysisUnavailable(Exception):
    pass


def analyze_with_ai(text: str) -> dict:
    """Return {risk_level, summary, findings:[{category,quote,explanation}]}.

    Set a bounded provider timeout (suggested 20s), cap output tokens and
    retries, and raise AnalysisUnavailable for provider/network failures.
    Never log the input agreement, credentials, or raw provider errors.
    """
    raise AnalysisUnavailable('AI adapter has not been implemented.')
