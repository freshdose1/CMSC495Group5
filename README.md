# CMSC495Group5

## Terms of Service Scanner

A browser extension that extracts text from the current public agreement page and displays clauses for human review. Supports Microsoft Edge and Google Chrome; Firefox is not supported.

**Current Alpha: mock mode.** Installation, page extraction, sample results and local history can be tested. Real AI integration is still pending; mock results do not evaluate the agreement or determine legal compliance.

## Download and install

You do not need Python, Node.js or an API key to use the extension with our hosted backend.

1. Open [this GitHub repository](https://github.com/freshdose1/CMSC495Group5) and select the **main** branch.
2. Click **Code > Download ZIP**, then extract the ZIP somewhere you will keep it.
3. In Edge, enter `edge://extensions` in the address bar. In Chrome, use `chrome://extensions`.
4. Enable **Developer mode**, click **Load unpacked**, and select the **extension** folder inside the extracted project. Select that folder, not the ZIP or the entire project.
5. Open **ToS Scanner Alpha** from the browser's Extensions menu. You can pin it for easier access.
6. Under **Settings**, enter `https://cmsc495group5.vercel.app` and click **Save connection**. Use that base address without `/docs` or `/api/health`.
7. Open a public Terms of Service page, open the extension, check the acknowledgment box, and click **Scan this page**. Keep the popup open while it runs.

Expect a clearly labeled **MOCK** result with an expandable sample finding. **History** keeps the last five scan summaries on your device; **Clear History** removes them. Full agreement text and finding quotes are not saved in history. The acknowledgment explains that extracted page text is sent to the backend and, in AI mode, to OpenRouter.

## Optional: use the included test page

The local HTML page shown in our demonstration is already included at `tests/fixtures/agreement.html`. You can use it instead of a public agreement page. **Only this optional test requires Python**; the backend can stay on Vercel.

1. Install Python if needed. Open PowerShell in the extracted project's main folder, which contains `README.md` and the `tests` folder.
2. Run this command. If `py` is not recognized, replace it with `python`:

   ```powershell
   py -m http.server 8080 --bind 127.0.0.1 --directory tests/fixtures
   ```

3. Leave PowerShell open and visit [http://127.0.0.1:8080/agreement.html](http://127.0.0.1:8080/agreement.html). Open that address rather than double-clicking the HTML file.
4. In the extension, keep the backend set to `https://cmsc495group5.vercel.app`, then acknowledge and scan. Expect mock results; this test does not demonstrate AI accuracy. Stop the page server with **Ctrl+C** when finished.

If the page cannot be reached, check that the PowerShell command is still running and that the address includes port **8080**. If a scan fails, check the saved backend address and [backend health](https://cmsc495group5.vercel.app/api/health). Browser settings pages and extension-store pages cannot be scanned. After downloading an update, replace your extracted files and click **Reload** for the extension on the extensions page.

## Developer documentation

- [Backend setup, tests and Vercel configuration](docs/DEVELOPMENT.md)
- [AI integration handoff](docs/AI_HANDOFF.md) and [API contract](docs/API_CONTRACT.md)
- [Implementation walkthrough](docs/WALKTHROUGH.md), [manual test checklist](docs/MANUAL_TESTS.md), [dated validation record](docs/VALIDATION.md) and [Alpha release plan](docs/ALPHA_PLAN.md)

Temporary change to demonstrate the branch, pull request, and review workflow.

## How to make a pull request

A pull request asks to merge your branch's changes into `main`.

1. Start from the latest `main`:

   ```powershell
   git switch main
   git pull origin main
   ```

2. Create your own branch. Replace `update-readme` with a short name for your change:

   ```powershell
   git switch -c update-readme
   ```

3. Edit your files, then commit them. Replace `README.md` with the files you changed:

   ```powershell
   git add README.md
   git commit -m "Describe your changes"
   ```

4. Push your branch:

   ```powershell
   git push -u origin update-readme
   ```

5. On GitHub, open this repository and select **Pull requests > New pull request**. Choose **base: main** and **compare: your branch**, add a title and description, then click **Create pull request**.

6. Ask another collaborator to review and approve, then merge the pull request. Write-access collaborators can explicitly override the review requirement through the pull request if needed.

Do not push directly to `main`. Your changes reach `main` only after the pull request is merged.
