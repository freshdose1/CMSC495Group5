export const MAX_TEXT = 30000;
export const DEFAULT_ENDPOINT = 'https://cmsc495group5.vercel.app';

export function validateEndpoint(value) {
  const url = new URL(value);
  const allowed = ['https://cmsc495group5.vercel.app', 'http://127.0.0.1:8000', 'http://localhost:8000'];
  if (!allowed.includes(url.origin) || url.username || url.password || url.search || url.hash || !['', '/'].includes(url.pathname)) {
    throw new Error('Choose the production address or localhost on port 8000.');
  }
  return url.origin;
}

export function prepareText(text) {
  const clean = text.replace(/\s+/g, ' ').trim();
  if (!clean) throw new Error('This page has no readable agreement text.');
  // Python counts Unicode code points; JS string.length counts UTF-16 units.
  const characters = Array.from(clean);
  return {text: characters.slice(0, MAX_TEXT).join(''), original_length: characters.length, truncated: characters.length > MAX_TEXT};
}

export function validateResponse(data) {
  if (!data || data.schema_version !== '1.0' || !['mock', 'ai'].includes(data.mode) ||
      !['complete', 'partial'].includes(data.status) || !['Low', 'Medium', 'High'].includes(data.risk_level) ||
      typeof data.summary !== 'string' || data.summary.length > 2000 || !Array.isArray(data.findings) || data.findings.length > 8 ||
      !Array.isArray(data.red_flags) || !Array.isArray(data.limitations) ||
      !data.limitations.every(x => typeof x === 'string') ||
      !data.coverage || !Number.isInteger(data.coverage.submitted_characters) ||
      data.coverage.submitted_characters < 1 || data.coverage.submitted_characters > MAX_TEXT ||
      !Number.isInteger(data.coverage.original_characters) ||
      data.coverage.original_characters < data.coverage.submitted_characters ||
      typeof data.coverage.truncated !== 'boolean' ||
      data.coverage.truncated !== (data.coverage.original_characters > data.coverage.submitted_characters) ||
      data.status !== (data.coverage.truncated ? 'partial' : 'complete') ||
      (!data.findings.length && data.risk_level !== 'Low')) {
    throw new Error('The backend returned an incompatible response.');
  }
  for (const f of data.findings) {
    if (!f || typeof f.quote !== 'string' || !f.quote || typeof f.explanation !== 'string' || !f.explanation ||
        !['content_license', 'third_party_sharing', 'data_retention', 'arbitration'].includes(f.category)) {
      throw new Error('The backend returned an invalid finding.');
    }
  }
  return data;
}

export async function requestAnalysis(endpoint, payload, fetchImpl = fetch, timeoutMs = 25000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetchImpl(`${validateEndpoint(endpoint)}/api/analyze`, {
      method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload),
      signal: controller.signal, credentials: 'omit', cache: 'no-store'
    });
    let data;
    try { data = await response.json(); } catch { throw new Error('The backend returned unreadable data.'); }
    if (!response.ok) throw new Error(data?.error?.message || `Analysis failed (HTTP ${response.status}).`);
    return validateResponse(data);
  } catch (error) {
    if (error.name === 'AbortError') throw new Error('Analysis timed out. Please try again.');
    throw error;
  } finally { clearTimeout(timer); }
}

export function addHistory(history, entry) {
  return [entry, ...history].slice(0, 5);
}
