"""HTTP transport. Agreement content is never persisted by this application."""
import os
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool
from .contracts import AnalyzeRequest, AnalyzeResponse
from .service import AnalysisError, analyze


class BodyLimit:
    """Bound buffered body bytes even when Content-Length is omitted."""
    def __init__(self, app, limit=256_000):
        self.app, self.limit = app, limit

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            return await self.app(scope, receive, send)
        body = bytearray()
        while True:
            message = await receive()
            if message['type'] == 'http.disconnect':
                return
            chunk = message.get('body', b'')
            # Reject before copying an oversized chunk into our buffer.
            if len(body) + len(chunk) > self.limit:
                response = JSONResponse(status_code=413, content={'error': {
                    'code': 'REQUEST_TOO_LARGE', 'message': 'Request exceeds 256,000 bytes.', 'retryable': False}})
                # Finish the response promptly. The ASGI server manages unread
                # transport bytes; draining an unbounded upload here can stall.
                return await response(scope, receive, send)
            body.extend(chunk)
            if not message.get('more_body', False):
                break
        sent = False

        async def replay():
            nonlocal sent
            if not sent:
                sent = True
                return {'type': 'http.request', 'body': bytes(body), 'more_body': False}
            return await receive()
        await self.app(scope, replay, send)


app = FastAPI(title='ToS Scanner Alpha API', version='0.1.0')
app.add_middleware(BodyLimit)
origins = [s.strip() for s in os.getenv('ALLOWED_ORIGINS', '').split(',') if s.strip()]
# CORS wraps BodyLimit so allowed clients can read 413 errors. Preflight
# requests are answered without buffering an upload. CORS is not authentication.
app.add_middleware(CORSMiddleware, allow_origins=origins,
                   allow_origin_regex=None if origins else r'\Achrome-extension://[a-p]{32}\Z',
                   allow_credentials=False, allow_methods=['GET', 'POST'], allow_headers=['Content-Type'])


@app.middleware('http')
async def no_store(request: Request, call_next):
    response = await call_next(request)
    response.headers['Cache-Control'] = 'no-store'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response


@app.exception_handler(RequestValidationError)
async def invalid_request(request: Request, exc):
    # FastAPI's default error may echo the rejected agreement. Keep it out.
    return JSONResponse(status_code=422, content={'error': {
        'code': 'INVALID_REQUEST', 'message': 'Provide non-empty text up to 30,000 characters and valid truncation metadata.',
        'retryable': False}})


@app.exception_handler(AnalysisError)
async def analysis_error(request: Request, exc: AnalysisError):
    return JSONResponse(status_code=exc.status, content={'error': {
        'code': exc.code, 'message': exc.message, 'retryable': exc.retryable}})


@app.get('/')
def root():
    return {'service': 'ToS Scanner Alpha', 'docs': '/docs', 'health': '/api/health'}


@app.get('/api/health')
def health():
    mode = os.getenv('ANALYSIS_MODE', 'mock')
    return {'status': 'ok', 'analysis_mode': mode,
            'notice': 'Health confirms HTTP service availability; validate AI separately.'}


@app.post('/api/analyze', response_model=AnalyzeResponse)
async def analyze_endpoint(payload: AnalyzeRequest):
    return await run_in_threadpool(analyze, payload)
