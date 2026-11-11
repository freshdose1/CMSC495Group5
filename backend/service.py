"""Application orchestration and evidence validation, shared by API/tests."""
import os
from uuid import uuid4
from pydantic import ValidationError
from . import ai_adapter
from .contracts import AnalyzeRequest, AnalyzeResponse, Coverage, ProviderResult


class AnalysisError(Exception):
    def __init__(self, code: str, message: str, status: int, retryable: bool = False):
        super().__init__(message)
        self.code, self.message, self.status, self.retryable = code, message, status, retryable


def analyze(payload: AnalyzeRequest) -> AnalyzeResponse:
    mode = os.getenv('ANALYSIS_MODE', 'mock')
    if mode == 'mock':
        scenario = os.getenv('MOCK_SCENARIO', 'findings')
        if scenario == 'failure':
            raise AnalysisError('MOCK_FAILURE', 'Simulated analysis failure for testing.', 503, True)
        if scenario not in ('findings', 'none'):
            raise AnalysisError('CONFIGURATION_ERROR', 'Invalid mock scenario configuration.', 503)
        findings = [] if scenario == 'none' else [{
            'category': 'third_party_sharing', 'quote': payload.text[:120],
            'explanation': 'Example finding for interface testing; no AI evaluation occurred.'}]
        raw = {'risk_level': 'Low' if scenario == 'none' else 'Medium',
               'summary': 'MOCK RESPONSE: sample results only. This agreement has not been evaluated by AI.',
               'findings': findings}
    elif mode == 'ai':
        try:
            raw = ai_adapter.analyze_with_ai(payload.text)
        except ai_adapter.AnalysisUnavailable:
            raise AnalysisError('AI_UNAVAILABLE', 'AI analysis is currently unavailable.', 503, True) from None
        except Exception:
            raise AnalysisError('AI_UNAVAILABLE', 'The analysis provider failed.', 503, True) from None
    else:
        raise AnalysisError('CONFIGURATION_ERROR', 'Invalid analysis mode configuration.', 503)
    try:
        result = ProviderResult.model_validate(raw)
        if any(f.quote not in payload.text for f in result.findings):
            raise ValueError('Unsupported evidence.')
        if not result.findings and result.risk_level != 'Low':
            raise ValueError('Elevated risk must include evidence.')
    except (ValidationError, ValueError, TypeError):
        raise AnalysisError('INVALID_AI_OUTPUT', 'Analysis returned invalid or unsupported findings.', 502, True) from None
    limitations = ['Clause screening supports human review; it does not determine legal compliance.']
    if mode == 'mock':
        limitations.append('Mock mode: no model was called and no risk assessment was performed.')
    if payload.truncated:
        limitations.append('Only the first 30,000 characters of extracted content were submitted.')
    return AnalyzeResponse(
        request_id=str(uuid4()), mode=mode, status='partial' if payload.truncated else 'complete',
        risk_level=result.risk_level, summary=result.summary,
        red_flags=[f.explanation for f in result.findings], findings=result.findings,
        coverage=Coverage(submitted_characters=len(payload.text),
                          original_characters=payload.original_length or len(payload.text),
                          truncated=payload.truncated), limitations=limitations)
