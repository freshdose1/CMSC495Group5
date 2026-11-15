"""Provider tests use a mock transport; never call OpenRouter."""
import json
import os
import unittest
from unittest.mock import patch

import httpx
from fastapi.testclient import TestClient

from backend.ai_adapter import analyze_with_ai, AnalysisUnavailable, MAX_RESPONSE_BYTES
from backend.api import app

TEXT = 'We may sell uploaded content to advertisers.'
RESULT = {'risk_level': 'High', 'summary': 'Review the sale of uploaded content.',
          'findings': [{'category': 'content_license', 'quote': TEXT,
                        'explanation': 'This permits commercial reuse of uploaded content.'}]}
REAL_CLIENT = httpx.Client


def envelope(result=RESULT, finish='stop'):
    return {'model': 'test-model', 'choices': [{'finish_reason': finish,
            'message': {'content': json.dumps(result)}}]}


class AdapterTests(unittest.TestCase):
    def setUp(self):
        env = patch.dict(os.environ, {'ANALYSIS_MODE': 'ai', 'OPENROUTER_API_KEY': 'secret-test-key', 'OPENROUTER_MODEL': 'test-model'})
        env.start()
        self.addCleanup(env.stop)
        self.requests = []

    def mock_provider(self, status=200, data=None, handler=None):
        def transport(request):
            self.requests.append(request)
            if handler:
                return handler(request)
            return httpx.Response(status, json=envelope() if data is None else data)
        def factory(**kwargs):
            self.assertLessEqual(kwargs['timeout'], 20)
            self.assertFalse(kwargs['follow_redirects'])
            return REAL_CLIENT(transport=httpx.MockTransport(transport), **kwargs)
        return patch('backend.ai_adapter.httpx.Client', side_effect=factory)

    def test_request_and_decoded_response(self):
        with self.mock_provider():
            self.assertEqual(analyze_with_ai(TEXT), RESULT)
        request = self.requests[0]
        body = json.loads(request.content)
        self.assertEqual(request.headers['Authorization'], 'Bearer secret-test-key')
        self.assertEqual(str(request.url), 'https://openrouter.ai/api/v1/chat/completions')
        self.assertEqual(body['response_format'], {'type': 'json_object'})
        self.assertTrue(body['provider']['require_parameters'])
        self.assertLessEqual(body['max_tokens'], 3500)
        self.assertEqual(json.loads(body['messages'][1]['content']), {'document_text': TEXT})
        self.assertIn('content_license', body['messages'][0]['content'])

    def test_missing_configuration_never_calls_provider(self):
        for key in ['OPENROUTER_API_KEY', 'OPENROUTER_MODEL']:
            with self.subTest(key=key), patch.dict(os.environ, {key: ''}), self.mock_provider(), self.assertRaises(AnalysisUnavailable):
                analyze_with_ai(TEXT)
        self.assertEqual(self.requests, [])

    def test_http_failures_are_sanitized_and_not_retried(self):
        for status in [301, 401, 402, 403, 404, 429, 500, 503]:
            with self.subTest(status=status), self.mock_provider(status, {'error': 'secret-test-key private document'}), self.assertRaises(AnalysisUnavailable) as caught:
                analyze_with_ai(TEXT)
            self.assertNotIn('secret', str(caught.exception))
        self.assertEqual(len(self.requests), 8)

    def test_network_and_timeout_fail_closed(self):
        for error in [httpx.ConnectError('private details'), httpx.ReadTimeout('secret')]:
            def handler(request):
                raise error
            with self.subTest(error=type(error)), self.mock_provider(handler=handler), self.assertRaises(AnalysisUnavailable) as caught:
                analyze_with_ai(TEXT)
            self.assertNotIn('private', str(caught.exception))
            self.assertNotIn('secret', str(caught.exception))

    def test_bad_envelopes_and_truncation(self):
        for data in [[], {}, {'error': {}}, {'error': 'failure'}, envelope(finish='length'),
                     {'choices': [{'finish_reason':'stop', 'message': {'refusal': 'no', 'content':'{}'}}]}]:
            with self.subTest(data=data), self.mock_provider(data=data), self.assertRaises(AnalysisUnavailable):
                analyze_with_ai(TEXT)

    def test_invalid_json_envelope(self):
        with self.mock_provider(handler=lambda r: httpx.Response(200, content=b'not json')), self.assertRaises(AnalysisUnavailable):
            analyze_with_ai(TEXT)

    def test_response_size_bound(self):
        with self.mock_provider(handler=lambda r: httpx.Response(200, content=b'x' * (MAX_RESPONSE_BYTES + 1))), self.assertRaises(AnalysisUnavailable):
            analyze_with_ai(TEXT)

    def test_malformed_content_is_invalid_output(self):
        data = {'choices': [{'finish_reason': 'stop', 'message': {'content': 'not JSON'}}]}
        with self.mock_provider(data=data):
            self.assertEqual(analyze_with_ai(TEXT), {})

    def test_http_route_through_real_adapter(self):
        client = TestClient(app)
        with self.mock_provider():
            response = client.post('/api/analyze', json={'text': TEXT})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['mode'], 'ai')
        self.assertEqual(response.json()['red_flags'], [RESULT['findings'][0]['explanation']])

    def test_route_rejects_invented_quote_and_wrong_category(self):
        client = TestClient(app)
        for changes in [{'quote': 'invented'}, {'category': 'content_rights'}]:
            result = {**RESULT, 'findings': [{**RESULT['findings'][0], **changes}]}
            with self.subTest(changes=changes), self.mock_provider(data=envelope(result)):
                response = client.post('/api/analyze', json={'text': TEXT})
            self.assertEqual(response.status_code, 502)
            self.assertEqual(response.json()['error']['code'], 'INVALID_AI_OUTPUT')
            self.assertNotIn('risk_level', response.json())

    def test_route_provider_failure_has_no_risk_result(self):
        client = TestClient(app)
        with self.mock_provider(429, {'error': 'secret'}):
            response = client.post('/api/analyze', json={'text': TEXT})
        self.assertEqual(response.status_code, 503)
        self.assertNotIn('risk_level', response.json())
        self.assertNotIn('secret', response.text)
