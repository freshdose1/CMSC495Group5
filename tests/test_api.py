"""HTTP integration tests: run in CI/installed environment, never call paid AI."""
import importlib.util
import os
import unittest
from unittest.mock import patch

HAS_HTTP_DEPS = bool(importlib.util.find_spec('fastapi') and importlib.util.find_spec('httpx'))
if os.getenv('REQUIRE_HTTP_TESTS') == '1' and not HAS_HTTP_DEPS:
    raise RuntimeError('HTTP integration dependencies are required in CI; skipping is forbidden.')


@unittest.skipUnless(HAS_HTTP_DEPS, 'Install requirements-dev.txt for FastAPI HTTP integration tests.')
class ApiTests(unittest.TestCase):
    def setUp(self):
        from fastapi.testclient import TestClient
        from backend.api import app
        self.client = TestClient(app)
        self.env = patch.dict(os.environ, {'ANALYSIS_MODE': 'mock', 'MOCK_SCENARIO': 'findings'})
        self.env.start()
        self.addCleanup(self.env.stop)

    def test_root_and_health(self):
        self.assertEqual(self.client.get('/').status_code, 200)
        self.assertEqual(self.client.get('/api/health').json()['analysis_mode'], 'mock')

    def test_http_success_contract(self):
        r = self.client.post('/api/analyze', json={'text': 'We share data with partners.'})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['mode'], 'mock')
        self.assertEqual(r.headers['cache-control'], 'no-store')

    def test_validation_does_not_echo_input(self):
        for payload in [{'text': 'private-marker' * 3000}, {'text': 123}, {'text': '   '}]:
            r = self.client.post('/api/analyze', json=payload)
            self.assertEqual(r.status_code, 422)
            self.assertNotIn('private-marker', r.text)

    def test_invalid_json(self):
        r = self.client.post('/api/analyze', content='broken', headers={'Content-Type': 'application/json'})
        self.assertEqual(r.status_code, 422)

    def test_body_limit(self):
        r = self.client.post('/api/analyze', content=b'x' * 256001)
        self.assertEqual(r.status_code, 413)

    def test_failure_is_error_response(self):
        os.environ['MOCK_SCENARIO'] = 'failure'
        r = self.client.post('/api/analyze', json={'text': 'terms'})
        self.assertEqual(r.status_code, 503)
        self.assertNotIn('risk_level', r.json())

    def test_extension_cors_and_untrusted_site(self):
        origin = 'chrome-extension://' + 'a' * 32
        headers = {'Origin': origin, 'Access-Control-Request-Method': 'POST', 'Access-Control-Request-Headers': 'content-type'}
        r = self.client.options('/api/analyze', headers=headers)
        self.assertEqual(r.headers['access-control-allow-origin'], origin)
        r = self.client.options('/api/analyze', headers={**headers, 'Origin': 'https://untrusted.example'})
        self.assertNotIn('access-control-allow-origin', r.headers)


if __name__ == '__main__':
    unittest.main()
