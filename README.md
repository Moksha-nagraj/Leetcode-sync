# LeetCode → GitHub Auto-Sync

Automatically syncs your accepted LeetCode submissions into this repo on a schedule,
using a GitHub Action. No browser extension required.

## How it works

1. `sync_leetcode.py` calls LeetCode's GraphQL API (the same one the site itself uses)
   to fetch your recent **accepted** submissions.
2. For each new one, it writes the solution code into a folder named
   `difficulty/questionId-title-slug/`, along with a small README describing the problem.
3. `.github/workflows/sync.yml` runs this script once an hour (configurable) and
   commits/pushes any new solutions automatically.
4. `.synced_ids.json` keeps track of which submissions have already been synced so
   nothing gets duplicated.

## Setup

### 1. Create the repo
Push this folder to a new GitHub repo (public or private, your choice).

```bash
cd leetcode-sync
git init
git add -A
git commit -m "Initial setup"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

### 2. Get your LeetCode session cookies
You need two values from your browser, while logged into leetcode.com:

1. Open LeetCode in your browser and log in.
2. Open Developer Tools → **Application** tab (Chrome) or **Storage** tab (Firefox).
3. Under **Cookies** → `https://leetcode.com`, find:
   - `LEETCODE_SESSION`
   - `csrftoken`
4. Copy their values.

⚠️ Treat these like passwords — they let scripts act as your logged-in session.
They expire periodically (weeks to months), so you'll need to refresh them if the
Action starts failing with an auth error.

### 3. Add them as GitHub Secrets
In your new repo: **Settings → Secrets and variables → Actions → New repository secret**

Add:
- `LEETCODE_SESSION` = (the value you copied)
- `LEETCODE_CSRF` = (the value you copied)

### 4. Enable the workflow
Go to the **Actions** tab in your repo — GitHub should detect the workflow
automatically. You can also trigger it manually the first time via
**Actions → Sync LeetCode Submissions → Run workflow**.

### 5. Done
From now on, every hour (or whatever schedule you set in `sync.yml`), the Action
checks for new accepted submissions and commits them automatically.

## Customizing

- **Change frequency:** edit the `cron` line in `.github/workflows/sync.yml`.
  (e.g. `"*/30 * * * *"` for every 30 minutes)
- **Folder structure:** edit `slugify_folder()` in `sync_leetcode.py` if you'd
  rather organize by topic/pattern instead of difficulty.
- **Commit message:** edit the `git commit -m "..."` line in the workflow.

## Notes

- This uses an *unofficial* LeetCode API — it could break if LeetCode changes
  their schema, in which case the script will need small updates.
- If your session cookie expires, the script will fail with an authentication
  error in the Action logs — just grab a fresh cookie value and update the secret.
