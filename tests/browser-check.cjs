// Optional headless component checks. Uses an isolated browser, never your signed-in profile.
const {chromium} = require(process.env.PLAYWRIGHT_PATH || 'playwright');
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const server = http.createServer((req, res) => {
  const file = path.resolve(root, '.' + decodeURIComponent(req.url.split('?')[0]));
  if (!file.startsWith(root + path.sep) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {res.writeHead(404); res.end(); return;}
  const ext = path.extname(file);
  res.setHeader('Content-Type', ({'.mjs':'text/javascript', '.js':'text/javascript', '.css':'text/css', '.html':'text/html'})[ext] || 'text/plain');
  res.end(fs.readFileSync(file));
});
(async () => {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const base = `http://127.0.0.1:${server.address().port}`;
  let browser;
  try {
    browser = await chromium.launch({headless:true, channel:process.env.BROWSER_CHANNEL || 'msedge'});
    const page = await browser.newPage({viewport:{width:420, height:760}});
    await page.goto(base + '/tests/fixtures/agreement.html');
    const extracted = await page.evaluate(fs.readFileSync(path.join(root,'extension/extract.js'), 'utf8'));
    assert.ok(extracted.includes('advertising partners'));
    for (const excluded of ['Navigation text', 'Footer text', 'Hidden content', 'private form value']) assert.ok(!extracted.includes(excluded), excluded);
    console.log('PASS visible text extraction excludes navigation, hidden content and form values');
    await page.addInitScript(() => {
      window.saved = {}; window.calls = 0; window.scenario = 'success';
      window.chrome = {
        tabs:{query:async () => [{id:1,url:'https://example.org/terms'}]},
        scripting:{executeScript:async () => [{result:'We share data with partners.'}]},
        storage:{local:{get:async key => ({[key]:window.saved[key]}), set:async value => Object.assign(window.saved,value), remove:async key => {delete window.saved[key];}}}
      };
      window.fetch = async () => {
        window.calls++;
        if (window.scenario === 'failure') return {ok:false,status:503,json:async () => ({error:{message:'AI unavailable'}})};
        return {ok:true,json:async () => ({schema_version:'1.0', request_id:'test', mode:'mock', status:'complete', risk_level:'Medium',
          summary:'<img src=x onerror=alert(1)>', red_flags:['Sample'],
          findings:[{category:'third_party_sharing',quote:'We share data',explanation:'Sample'}],
          coverage:{submitted_characters:28,original_characters:28,truncated:false},limitations:['Mock demonstration']})};
      };
    });
    await page.goto(base + '/extension/popup.html');
    await page.locator('#endpoint').waitFor();
    assert.ok(await page.locator('#scan').isDisabled());
    assert.equal(await page.evaluate(() => window.calls),0);
    console.log('PASS transmission acknowledgement required before scan');
    await page.locator('#consent').check();
    await page.locator('#scan').click();
    await page.locator('#results').waitFor({state:'visible'});
    assert.match(await page.locator('#results').textContent(), /MOCK RESULTS/);
    assert.equal(await page.locator('#results img').count(),0);
    assert.match(await page.locator('#results').textContent(), /<img src=x/);
    console.log('PASS mock warning and safe rendering of server-controlled text');
    await page.locator('#historyTab').click();
    await page.locator('.history-item').waitFor();
    assert.equal(await page.locator('.history-item').count(),1);
    await page.locator('#clearHistory').click();
    await page.waitForFunction(() => !document.querySelector('.history-item'));
    console.log('PASS local history display and clearing');
    await page.locator('#scanTab').click();
    await page.evaluate(() => {window.scenario='failure';});
    await page.locator('#scan').click();
    await page.locator('#error').waitFor({state:'visible'});
    assert.match(await page.locator('#error').textContent(), /AI unavailable/);
    assert.ok(await page.locator('#results').isHidden());
    assert.ok(await page.locator('#scan').isEnabled());
    console.log('PASS failure hides prior findings and re-enables scanning');
    await browser.close(); browser = null;
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(error => {console.error(error); process.exitCode=1;});
