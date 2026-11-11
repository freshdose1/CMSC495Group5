import os
import unittest
from unittest.mock import patch
from pydantic import ValidationError
from backend.contracts import AnalyzeRequest
from backend.service import analyze, AnalysisError


class ContractTests(unittest.TestCase):
    def test_reject_empty_whitespace_and_wrong_type(self):
        for value in ['', '  ', 7, None, ['terms']]:
            with self.subTest(value=value), self.assertRaises(ValidationError):
                AnalyzeRequest.model_validate({'text': value})

    def test_payload_cap_and_unicode(self):
        self.assertEqual(len(AnalyzeRequest(text='😀' * 30000).text), 30000)
        with self.assertRaises(ValidationError):
            AnalyzeRequest(text='x' * 30001)

    def test_truncation_metadata(self):
        self.assertTrue(AnalyzeRequest(text='terms', original_length=40000, truncated=True).truncated)
        for metadata in [{'original_length': 2}, {'original_length': 100}, {'truncated': True}]:
            with self.subTest(metadata=metadata), self.assertRaises(ValidationError):
                AnalyzeRequest(text='terms', **metadata)

    def test_unknown_fields_rejected(self):
        with self.assertRaises(ValidationError):
            AnalyzeRequest.model_validate({'text': 'terms', 'api_key': 'never-accepted'})


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {'ANALYSIS_MODE': 'mock', 'MOCK_SCENARIO': 'findings'})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.payload = AnalyzeRequest(text='We may share customer data with advertising partners.')

    def test_mock_is_labelled_and_quote_is_present(self):
        result = analyze(self.payload)
        self.assertEqual(result.mode, 'mock')
        self.assertIn('MOCK RESPONSE', result.summary)
        self.assertIn(result.findings[0].quote, self.payload.text)
        self.assertEqual(result.red_flags, [f.explanation for f in result.findings])

    def test_partial_is_disclosed(self):
        result = analyze(AnalyzeRequest(text='terms', original_length=40000, truncated=True))
        self.assertEqual(result.status, 'partial')
        self.assertTrue(result.coverage.truncated)
        self.assertTrue(any('30,000' in x for x in result.limitations))

    def test_no_findings_is_success(self):
        os.environ['MOCK_SCENARIO'] = 'none'
        result = analyze(self.payload)
        self.assertEqual(result.status, 'complete')
        self.assertEqual(result.findings, [])

    def test_failure_does_not_return_low_risk(self):
        os.environ['MOCK_SCENARIO'] = 'failure'
        with self.assertRaises(AnalysisError) as error:
            analyze(self.payload)
        self.assertEqual(error.exception.status, 503)

    def test_unimplemented_ai_fails_closed(self):
        os.environ['ANALYSIS_MODE'] = 'ai'
        with self.assertRaises(AnalysisError) as error:
            analyze(self.payload)
        self.assertEqual(error.exception.code, 'AI_UNAVAILABLE')

    def test_valid_ai_output_is_accepted(self):
        os.environ['ANALYSIS_MODE'] = 'ai'
        output = {'risk_level': 'High', 'summary': 'Review advertising data sharing.', 'findings': [{
            'category': 'third_party_sharing', 'quote': self.payload.text, 'explanation': 'Allows sharing with advertising partners.'}]}
        with patch('backend.ai_adapter.analyze_with_ai', return_value=output):
            result = analyze(self.payload)
        self.assertEqual(result.mode, 'ai')
        self.assertEqual(result.risk_level, 'High')

    def test_invalid_ai_output_and_invented_quote_rejected(self):
        os.environ['ANALYSIS_MODE'] = 'ai'
        outputs = ['markdown instead of JSON', {'risk_level': 'Safe'},
                   {'risk_level': 'High', 'summary': 'bad', 'findings': []},
                   {'risk_level': 'High', 'summary': 'bad', 'findings': [{
                       'category': 'third_party_sharing', 'quote': 'invented clause', 'explanation': 'bad'}]}]
        for output in outputs:
            with self.subTest(output=output), patch('backend.ai_adapter.analyze_with_ai', return_value=output), self.assertRaises(AnalysisError) as error:
                analyze(self.payload)
            self.assertEqual(error.exception.code, 'INVALID_AI_OUTPUT')

    def test_provider_exception_is_sanitized(self):
        os.environ['ANALYSIS_MODE'] = 'ai'
        with patch('backend.ai_adapter.analyze_with_ai', side_effect=RuntimeError('secret-provider-key')), self.assertRaises(AnalysisError) as error:
            analyze(self.payload)
        self.assertNotIn('secret', error.exception.message)

    def test_unknown_mode_fails(self):
        os.environ['ANALYSIS_MODE'] = 'typo'
        with self.assertRaises(AnalysisError):
            analyze(self.payload)


if __name__ == '__main__':
    unittest.main()
