# CMSC495Group5

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
