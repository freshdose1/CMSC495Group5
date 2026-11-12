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
        for untrusted in ['https://untrusted.example', origin + '.evil.com',
                          'https://evil.example/' + origin, 'null',
                          'chrome-extension://' + 'a' * 31, 'chrome-extension://' + 'z' * 32]:
            with self.subTest(origin=untrusted):
                r = self.client.options('/api/analyze', headers={**headers, 'Origin': untrusted})
                self.assertEqual(r.status_code, 400)
                self.assertNotIn('access-control-allow-origin', r.headers)

    def test_oversized_error_is_readable_by_allowed_extension(self):
        origin = 'chrome-extension://' + 'a' * 32
        r = self.client.post('/api/analyze', content=b'x' * 256001, headers={'Origin': origin})
        self.assertEqual(r.status_code, 413)
        self.assertEqual(r.headers['access-control-allow-origin'], origin)
        self.assertEqual(r.headers['cache-control'], 'no-store')
        self.assertEqual(r.json()['error']['code'], 'REQUEST_TOO_LARGE')
        self.assertEqual(self.client.get('/api/health').status_code, 200)


@unittest.skipUnless(HAS_HTTP_DEPS, 'Install requirements-dev.txt for ASGI middleware tests.')
class StreamingBodyTests(unittest.IsolatedAsyncioTestCase):
    async def test_oversized_stream_returns_without_waiting_for_upload_tail(self):
        from backend.api import BodyLimit
        from unittest.mock import AsyncMock
        downstream = AsyncMock()
        receive = AsyncMock(side_effect=[
            {'type': 'http.request', 'body': b'abcd', 'more_body': True},
            {'type': 'http.request', 'body': b'ef', 'more_body': True},
            AssertionError('Do not wait for a possibly endless upload tail.'),
        ])
        send = AsyncMock()
        await BodyLimit(downstream, limit=5)({'type': 'http'}, receive, send)
        self.assertEqual(receive.await_count, 2)
        downstream.assert_not_awaited()
        self.assertEqual(send.call_args_list[0].args[0]['status'], 413)

    async def test_chunked_upload_is_replayed_without_data_loss(self):
        from backend.api import BodyLimit
        from unittest.mock import AsyncMock
        received = []

        async def downstream(scope, receive, send):
            received.append(await receive())

        receive = AsyncMock(side_effect=[
            {'type': 'http.request', 'body': b'ab', 'more_body': True},
            {'type': 'http.request', 'body': b'cde', 'more_body': False},
        ])
        await BodyLimit(downstream, limit=5)({'type': 'http'}, receive, AsyncMock())
        self.assertEqual(received, [{'type': 'http.request', 'body': b'abcde', 'more_body': False}])

    async def test_preflight_does_not_read_request_body(self):
        from backend.api import BodyLimit
        from starlette.middleware.cors import CORSMiddleware
        from unittest.mock import AsyncMock
        origin = 'chrome-extension://' + 'a' * 32
        downstream, receive, send = AsyncMock(), AsyncMock(), AsyncMock()
        middleware = CORSMiddleware(BodyLimit(downstream), allow_origins=[origin], allow_methods=['POST'])
        scope = {'type': 'http', 'method': 'OPTIONS', 'headers': [
            (b'origin', origin.encode()), (b'access-control-request-method', b'POST')]}
        await middleware(scope, receive, send)
        receive.assert_not_awaited()
        downstream.assert_not_awaited()
        self.assertEqual(send.call_args_list[0].args[0]['status'], 200)


if __name__ == '__main__':
    unittest.main()
