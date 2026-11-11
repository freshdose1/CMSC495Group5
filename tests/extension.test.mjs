import test from 'node:test';
import assert from 'node:assert/strict';
import {prepareText, validateEndpoint, validateResponse, requestAnalysis, addHistory} from '../extension/core.mjs';

const response = () => ({schema_version:'1.0', request_id:'test', mode:'mock', status:'complete', risk_level:'Medium',
  summary:'MOCK RESPONSE', red_flags:['Sample'], findings:[{category:'third_party_sharing', quote:'terms', explanation:'Sample'}],
  coverage:{submitted_characters:5, original_characters:5, truncated:false}, limitations:['Mock results']});

test('text extraction payload normalizes whitespace and refuses empty input', () => {
  assert.deepEqual(prepareText('  hello\n world  '), {text:'hello world', original_length:11, truncated:false});
  assert.throws(() => prepareText(' \n '));
});
test('truncation reports Unicode characters consistently with backend', () => {
  const p = prepareText('😀'.repeat(30001));
  assert.equal(Array.from(p.text).length, 30000); assert.equal(p.original_length, 30001); assert.equal(p.truncated, true);
});
test('endpoint selection prevents arbitrary-host transmission', () => {
  assert.equal(validateEndpoint('http://127.0.0.1:8000/'), 'http://127.0.0.1:8000');
  for (const endpoint of ['https://evil.example', 'https://cmsc495group5.vercel.app.evil.example', 'http://localhost:8000/path', 'https://u:p@cmsc495group5.vercel.app']) {
    assert.throws(() => validateEndpoint(endpoint));
  }
});
test('incompatible server responses cannot render as success', () => {
  assert.equal(validateResponse(response()).mode, 'mock');
  for (const value of [null, {}, {...response(), risk_level:'Safe'}, {...response(), findings:[{}]}, {...response(), mode:'unknown'}]) {
    assert.throws(() => validateResponse(value));
  }
});
test('successful fetch submits only agreed JSON and omits credentials', async () => {
  const data = await requestAnalysis('http://localhost:8000', prepareText('terms'), async (url, options) => {
    assert.equal(url, 'http://localhost:8000/api/analyze'); assert.equal(options.credentials, 'omit');
    assert.equal(JSON.parse(options.body).text, 'terms');
    return {ok:true, json:async () => response()};
  });
  assert.equal(data.mode, 'mock');
});
test('API failure is not converted to a low-risk result', async () => {
  await assert.rejects(requestAnalysis('http://localhost:8000', {}, async () => ({ok:false, status:503, json:async () => ({error:{message:'AI unavailable'}})})), /AI unavailable/);
});
test('invalid JSON produces a readable error', async () => {
  await assert.rejects(requestAnalysis('http://localhost:8000', {}, async () => ({ok:true, json:async () => {throw new Error('JSON');}})), /unreadable/);
});
test('network errors propagate and timeout aborts the request', async () => {
  await assert.rejects(requestAnalysis('http://localhost:8000', {}, async () => {throw new Error('offline');}), /offline/);
  await assert.rejects(requestAnalysis('http://localhost:8000', {}, (url, options) => new Promise((resolve, reject) => {
    options.signal.addEventListener('abort', () => reject(Object.assign(new Error(), {name:'AbortError'})));
  }), 5), /timed out/);
});
test('history is newest-first and capped at five', () => {
  const old = [1,2,3,4,5]; assert.deepEqual(addHistory(old, 0), [0,1,2,3,4]); assert.deepEqual(old, [1,2,3,4,5]);
});
