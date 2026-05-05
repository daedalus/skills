# git-author-rewrite

Rewrite all commit authors in a git branch to a new name/email combination. Useful for correcting attribution across an entire branch history.

## When to use

Trigger on phrases like:
- "change author of all commits"
- "rewrite git author info"
- "mass update committer/author"
- "fix attribution across branch"
- "update all commits to use my new email"

## Workflow

### 1. Get current context
```bash
# Get repo URL and current branch
git remote get-url origin
rtk git branch --show-current
```

### 2. Clone to /tmp/ for safe rewriting
Never rewrite in-place. Always work on a clone:
```bash
git clone <repo-url> /tmp/<repo>-rewrite
cd /tmp/<repo>-rewrite
git checkout <branch>
```

### 3. Rewrite all commit authors
Use `git filter-branch` with `--env-filter` to update both author and committer:
```bash
cd /tmp/<repo>-rewrite
git filter-branch --env-filter '
GIT_AUTHOR_NAME="New Name"
GIT_AUTHOR_EMAIL="new@email.com"
GIT_COMMITTER_NAME="New Name"
GIT_COMMITTER_EMAIL="new@email.com"
' -- --all
```

Notes:
- `--all` rewrites all branches and tags
- The env-filter sets both author and committer to ensure consistency
- WARNING about git-filter-branch is normal; it's acceptable for this use case

### 4. Verify the rewrite
Check that authors were updated correctly:
```bash
rtk git log --format="%h %an <%ae> %s" | head -10
```

### 5. Clean up filter-branch artifacts
Remove backup refs and repack:
```bash
git for-each-ref --format='%(refname)' refs/original/ | xargs -n 1 git update-ref -d 2>/dev/null
git reflog expire --expire=now --all
git gc --prune=now
```

### 6. Apply to original repo (optional, not automatic)
If user wants to replace their local repo:
```bash
cd <original-repo>
git remote add rewritten /tmp/<repo>-rewrite
git fetch rewritten
git reset --hard rewritten/master
```

## Important constraints

- **Never push** unless explicitly asked
- **Always work on a clone** in `/tmp/` to avoid corrupting the working directory
- **Verify before applying** - once rewritten, commits have new hashes
- This rewrites history - all commit SHAs will change
- Team members will need to re-clone or reset if this is pushed to shared branches

## Example

User: "change the author of every commit in this branch to user name Dario clavijo email clavijodario@gmail.com"

Agent:
1. Gets repo URL and branch name
2. Clones to `/tmp/ImpactGuard-rewrite`
3. Runs filter-branch with the new author info
4. Verifies with `git log`
5. Cleans up backup refs
6. Informs user the rewritten repo is at `/tmp/ImpactGuard-rewrite` and explains how to apply it
