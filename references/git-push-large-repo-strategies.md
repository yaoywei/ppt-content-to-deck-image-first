# Git Push Strategies for Large Existing Repos (40 MB+ total, 1-3 MB files)

**When to use this**: the agent needs to push a small change (1-5 new files, README update, etc.) to a GitHub repo that is **already large** (40 MB+ total working tree, with 1-3 MB files). The standard `git clone → git add → git commit → git push` flow timeouts on the clone step.

**Key insight**: the bottleneck is the **clone** (which downloads the full working tree), not the push (which only sends the diff). The agent already has the new content (in `/tmp/` or `~/projects/`); the question is how to land it in the remote without paying the 40 MB clone cost.

## Why the standard flow fails

```bash
# The standard 4-step flow:
git clone git@github.com:owner/repo.git        # ← times out on 40 MB+ repos
cd repo
cp /tmp/new-file.png examples/
git add . && git commit -m "..."
git push origin main
```

Empirically observed timeouts on a 40.6 MB public repo with 17 MB of PNG examples:
- `git clone` (full): **> 600s timeout** at foreground execution limit
- `git clone --depth 1 --filter=blob:none` (sparse checkout prep): **> 600s timeout**
- `git clone --depth 1 --filter=blob:limit=10m`: **> 600s timeout**
- `git fetch` (incremental, assuming a local repo exists): **> 60s timeout**

The 600s foreground limit is the killer. Background mode + `notify_on_complete` doesn't help either, because the agent needs the clone to complete to do the next step.

## The 4 push strategies, ranked by reliability

### Strategy 1: API-only push (RECOMMENDED for public repos, no PAT required for read)

This is the **GitHub Data API 4-step**: blobs → tree → commit → ref. Reads are public (no auth); writes need a PAT. The full flow lives in the `github-data-api-push` skill (mentioned in Pitfall 19).

**When to use**:
- Repo is public (read API has no auth)
- Agent has a `GITHUB_TOKEN` in `~/.hermes/.env` (write API needs auth)
- The new content is 1-10 small files (each < 5 MB)
- Total push size is < 30 MB

**Latency**: 30-60s for 5 files, scales linearly with file count. The bottleneck is the base64 POST body for each blob, not the round-trip count.

**Skip if**: no `GITHUB_TOKEN` is available, or the file is > 5 MB (route to Releases, see `github-release-large-assets-recipe.md`).

### Strategy 2: `git ls-remote` + targeted `git fetch` (PARTIAL clone, for already-cloned repos)

If the agent already has a local working copy of the repo (from a prior session, even if the working tree was lost), use the cheapest possible sync:

```bash
# Step 1: confirm the remote is alive and get the current SHA
git ls-remote origin main
# Output: eee612123340069b6fc385b8c2a6e28c99497c8b\trefs/heads/main

# Step 2: if no local repo, init a fresh one and point at the remote
git init -b main
git remote add origin git@github.com:owner/repo.git

# Step 3: fetch ONLY the commit metadata, no blobs
git fetch --depth 1 --filter=blob:none --no-tags origin main
# This succeeds in 5-30s even for large repos — it only fetches commit objects, not file contents

# Step 4: checkout files ONE AT A TIME from the remote tree
# (this is the part that pulls each file's blob, on demand)
git checkout FETCH_HEAD -- README.md
git checkout FETCH_HEAD -- examples/style-showcase-leadership.png
# ... etc

# Step 5: apply the agent's new content + commit + push
cp /tmp/new-readme.md README.md
cp /tmp/new-style.png examples/style-showcase-new.png
git add README.md examples/style-showcase-new.png
git commit -m "Add new style + README update"
git push origin main
```

**Empirically**: `git fetch --filter=blob:none` succeeded in < 30s on the 40 MB repo where full clone timed out at 600s. The blob-on-demand checkout is then per-file, ~5-15s per 1-2 MB PNG over SSH.

**Key**: the `--filter=blob:none` flag is the magic. GitHub's SSH endpoint can serve commit metadata fast, even on huge repos. The blob filter means "don't download the file contents, I'll ask for them explicitly".

### Strategy 3: Manual blob-by-blob (for repos where even partial clone fails)

If `git fetch --filter=blob:none` itself times out (rare, but possible on slow networks):

```bash
# Skip git entirely. Use the GitHub API to download specific files.

# Get a single file:
curl -sS -m 20 "https://api.github.com/repos/owner/repo/contents/path/to/file.png" \
  | python3 -c "import json,sys,base64; print(base64.b64decode(json.load(sys.stdin)['content']))" \
  > file.png
# This works for files up to ~1 MB. Larger files return a `download_url` field instead.

# Get the README:
curl -sS -m 20 "https://raw.githubusercontent.com/owner/repo/main/README.md" > README.md
# Note: raw.githubusercontent.com can be slow / SSL timeout. Use the API endpoint instead.
```

**When to use**: only if `git fetch` also times out. This is the slowest path but the most reliable — you're downloading exactly the files you need, nothing else.

### Strategy 4: Ask the user to create the empty repo (for NEW repos)

If the remote doesn't exist yet (e.g. user says "push to a new repo called X"):

```bash
# Tell the user to:
# 1. Go to https://github.com/new
# 2. Create repo "X" (public, no README/license/.gitignore — those conflict with the agent's first push)
# 3. Reply "created"

# Then:
cd /tmp/agent-build
git remote add origin git@github.com:owner/X.git
git push -u origin main
# This push is fast — it's the first commit, no history to reconcile.
```

**When to use**: greenfield repos, no history to clone.

## Choosing the right strategy — decision tree

```
1. Does the remote exist already?
   ├─ NO → Strategy 4 (user creates empty repo, agent pushes first commit)
   └─ YES ↓

2. Does the agent have a local working copy of the repo?
   ├─ YES → `cd <local-repo> && git pull --rebase && <apply changes> && git push`
   │        (the pull may time out on large repos, fall through to strategy 2)
   └─ NO ↓

3. Is the new content < 5 MB total AND the agent has a GITHUB_TOKEN?
   ├─ YES → Strategy 1 (GitHub Data API 4-step)
   └─ NO ↓

4. Is the new content > 5 MB per file (e.g. PPTX, PDF)?
   ├─ YES → Releases API (see github-release-large-assets-recipe.md)
   └─ NO ↓

5. Default → Strategy 2 (`git fetch --filter=blob:none` + per-file checkout + push)
```

## Hard gate (P29/P30 pattern)

Before any `git clone` or `git fetch`, run a 1-line size check:

```bash
# Pre-condition: estimate the remote repo size
curl -sS -m 10 "https://api.github.com/repos/owner/repo" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('size', 'unknown'), 'KB')"
# If > 30,000 KB (30 MB): use Strategy 2 or 3, not full clone
# If < 30 MB: full clone is probably fine, but Strategy 2 is still faster
```

**Always** try Strategy 2 before falling back to a full `git clone`. The full clone is the slowest, most failure-prone path, and it's only faster than Strategy 2 in the rare case where the repo is small AND the network is fast.

## What NOT to do

| Anti-pattern | Why it fails |
|---|---|
| `git clone` and hope it works | Times out at 600s on 40 MB+ repos |
| `git clone --depth 1` alone | Still downloads the working tree, same timeout |
| `git clone --filter=blob:none` then `git checkout` all at once | The checkout step downloads all blobs, can be slow if the agent checks out 20+ files |
| `git push origin main` with no local clone | git refuses — there's no local branch to push |
| Tell the user "git pull is broken, I can't push" | It isn't broken, you're using the wrong strategy. Use Strategy 2. |
| `gh repo create` CLI | Requires `gh` CLI installed + auth; not available in most containers |

## Real session 2026-06-13

Agent needed to push 5 new files (4 PNGs + 1 README) to `yaoywei/ppt-content-to-deck-image-first` (40.6 MB total). Standard flow:

```bash
git clone git@github.com:yaoywei/ppt-content-to-deck-image-first.git /tmp/ppt-full
# Timed out at 600s (foreground limit)
```

Strategy 2 succeeded:

```bash
cd /tmp && git init -b main  # fresh local repo
git remote add origin git@github.com:yaoywei/ppt-content-to-deck-image-first.git
git fetch --depth 1 --filter=blob:none --no-tags --single-branch origin main
# 14s, returned FETCH_HEAD with commit eee61212
git checkout FETCH_HEAD -- examples/style-showcase-leadership.png  # per-file, ~5s each
# Applied the agent's new content
git add . && git commit -m "Add 4 new baoyu + de-anonymize README"
git push origin main
# Push succeeded in 8s — diff was small (~3 MB), well within SSH limits
```

**Total time**: 14s fetch + 5s/file × 1 checkout (didn't need to checkout the 11 existing showcases, only the 4 new ones + 1 modified README) + 8s push = **~30 seconds**, vs. the 600s timeout of the standard flow.

## Related

- `github-data-api-push` skill — Strategy 1 (4-step API push, ideal for repos with no SSH push access)
- `github-release-large-assets-recipe.md` — for files > 5 MB (Release assets, not Blob API)
- `hermes-secrets` — safe way to read `GITHUB_TOKEN` from `~/.hermes/.env` without echoing
- `hermes-terminal-pitfalls` — the 600s foreground timeout (Strategy 1 / 2 / 3 don't hit it)
- Pitfall 32 in the parent skill — covers the Release path for > 5 MB files
- Pitfall 34 in the parent skill — covers "verify before rebuild" (related: don't redo work that already shipped)
