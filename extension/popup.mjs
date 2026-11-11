import {DEFAULT_ENDPOINT, prepareText, validateEndpoint, requestAnalysis, addHistory} from './core.mjs';
const $ = id => document.getElementById(id);
let busy = false;
function textElement(tag, text, className) {
  const el = document.createElement(tag); el.textContent = text;
  if (className) el.className = className;
  return el;
}
function renderResults(data) {
  const box = $('results'); box.replaceChildren(); box.hidden = false;
  if (data.mode === 'mock') box.append(textElement('p', 'MOCK RESULTS — interface demonstration only; no AI analysis occurred.', 'mock'));
  box.append(textElement('p', `${data.risk_level} risk${data.mode === 'mock' ? ' (sample)' : ''}`, `badge risk-${data.risk_level}`));
  box.append(textElement('p', data.summary));
  box.append(textElement('p', `${data.status === 'partial' ? 'Partial analysis' : 'Submitted text processed'} · ${data.coverage.submitted_characters.toLocaleString()} characters`, 'coverage'));
  if (!data.findings.length) box.append(textElement('p', 'No flagged clauses returned. This does not establish that the agreement is safe.'));
  for (const f of data.findings) {
    const item = document.createElement('details');
    item.append(textElement('summary', f.category.replaceAll('_', ' ')), textElement('blockquote', f.quote), textElement('p', f.explanation));
    box.append(item);
  }
  for (const limitation of data.limitations) box.append(textElement('p', limitation, 'coverage'));
}
async function renderHistory() {
  const {history = []} = await chrome.storage.local.get('history');
  $('history').replaceChildren();
  if (!history.length) $('history').append(textElement('p', 'No scans saved yet.'));
  for (const h of history) {
    const card = textElement('article', '', 'history-item');
    card.append(textElement('strong', h.site), textElement('small', `${new Date(h.at).toLocaleString()} · ${h.mode === 'mock' ? 'MOCK · ' : ''}${h.risk_level} risk · ${h.status}`), textElement('p', h.summary));
    $('history').append(card);
  }
}
function setTab(name) {
  for (const tab of ['scan', 'history', 'settings']) {
    $(`${tab}Panel`).hidden = name !== tab;
    $(`${tab}Tab`).setAttribute('aria-pressed', String(name === tab));
  }
  if (name === 'history') renderHistory().catch(showError);
}
function showError(error) { $('error').textContent = error.message || 'An unexpected error occurred.'; $('error').hidden = false; }
$('consent').addEventListener('change', () => { $('scan').disabled = busy || !$('consent').checked; });
for (const tab of ['scan', 'history', 'settings']) $(`${tab}Tab`).addEventListener('click', () => setTab(tab));
$('scan').addEventListener('click', async () => {
  if (busy || !$('consent').checked) return;
  busy = true; $('scan').disabled = true; $('error').hidden = true; $('results').hidden = true;
  $('progress').textContent = 'Extracting page text…';
  try {
    const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
    if (!tab?.id || !/^https?:\/\//.test(tab.url || '')) throw new Error('Open a public HTTP or HTTPS agreement page first. Browser settings and store pages cannot be scanned.');
    const injection = await chrome.scripting.executeScript({target: {tabId: tab.id}, files: ['extract.js']});
    const payload = prepareText(injection[0]?.result || '');
    const {endpoint = DEFAULT_ENDPOINT} = await chrome.storage.local.get('endpoint');
    $('progress').textContent = 'Waiting for analysis…';
    const data = await requestAnalysis(endpoint, payload);
    // Verify evidence again at the UI boundary before displaying it.
    if (data.findings.some(f => !payload.text.includes(f.quote))) throw new Error('The backend returned a quotation missing from the submitted text.');
    renderResults(data);
    $('progress').textContent = data.mode === 'mock' ? 'Mock demonstration complete.' : 'Analysis returned.';
    const {history = []} = await chrome.storage.local.get('history');
    const entry = {site: new URL(tab.url).hostname, at: new Date().toISOString(), mode: data.mode,
      status: data.status, risk_level: data.risk_level, summary: data.summary};
    try { await chrome.storage.local.set({history: addHistory(history, entry)}); }
    catch { $('progress').textContent += ' History could not be saved.'; }
  } catch (error) { $('progress').textContent = ''; showError(error); }
  finally { busy = false; $('scan').disabled = !$('consent').checked; }
});
$('clearHistory').addEventListener('click', async () => {
  try { await chrome.storage.local.remove('history'); await renderHistory(); } catch (e) { showError(e); }
});
$('saveSettings').addEventListener('click', async () => {
  try { const endpoint = validateEndpoint($('endpoint').value.trim()); await chrome.storage.local.set({endpoint}); $('settingsStatus').textContent = 'Connection saved.'; }
  catch (e) { $('settingsStatus').textContent = e.message; }
});
chrome.storage.local.get('endpoint').then(({endpoint = DEFAULT_ENDPOINT}) => { $('endpoint').value = endpoint; }).catch(showError);
