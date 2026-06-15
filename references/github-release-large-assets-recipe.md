# GitHub Releases for Large Assets — Pushing > 5 MB files (PPTX, PDF, ZIP) to a skill repo

**When to use this**: the agent has generated a deliverable artifact (PPTX deck, PDF, ZIP) larger than 5 MB and needs to push it to a GitHub repo. The Blob API (`POST /git/blobs`) handles small files fine but **times out at ~6 MB+** in practice, even though GitHub's documented limit is 100 MB per blob.

**The empirical size threshold**: 1-2 MB files push in 5-10s; 5-6 MB sometimes time out; 24 MB always times out. The 5 MB cutoff is conservative.

## Why the Blob API times out on large files

The `github-data-api-push` skill pushes via 4 HTTP calls: blobs → tree → commit → ref. The `POST /git/blobs` endpoint takes base64-encoded content. For a 24 MB file:

1. base64 inflation: 24 MB → ~32 MB POST body
2. Single `urllib.request.urlopen` write, no streaming support on the API side
3. Default `urllib` timeout: 60s per write
4. Over slow networks, a 32 MB single write exceeds 60s → `TimeoutError: The write operation timed out`

The fix is to use the **Releases API** instead, which is designed for large binary uploads (up to 2 GB per asset) and supports proper streaming uploads.

## The 4-step pattern

### Step 1: Identify the size split

```bash
# Find files > 5 MB that need the Release path
find . -size +5M -type f -not -path "./.git/*" -not -path "./node_modules/*"
# Example output: ./kunpeng-yihang-v4-leadership-style.pptx (24 MB), ./kunpeng-yihang-v4-leadership-style.pdf (4 MB)
```

### Step 2: Push small files via Blob API (unchanged from `github-data-api-push`)

```python
import os, json, base64, urllib.request

# ... (load token from ~/.hermes/.env, see github-data-api-push for the safe pattern)

# 1. blobs → tree → commit → ref
# (use the github-data-api-push skill's reference implementation)
# ONLY push files that are < 5 MB through this path.
```

### Step 3: Create the Release

```python
import urllib.request, json

REPO = "owner/repo"
TOKEN = "..."  # from ~/.herherm/.env via the github-data-api-push safe pattern

release_payload = {
    "tag_name": "v1.0.0-deck-name",
    "name": "Deck Name - Style Description (15 pages)",
    "body": """# Deck Title

Brief description of what's in this release.

## Files
- `deck.pptx` (24 MB) - Editable PPT, 16:9
- `deck.pdf` (4 MB) - PDF preview, no edit
""",
    "draft": False,
    "prerelease": False
}

req = urllib.request.Request(
    f"https://api.github.com/repos/{REPO}/releases",
    data=json.dumps(release_payload).encode(),
    headers={"Authorization": f"token {TOKEN}",
             "Accept": "application/vnd.github.v3+json",
             "Content-Type": "application/json"},
    method="POST"
)
with urllib.request.urlopen(req, timeout=30) as resp:
    release = json.loads(resp.read())
# Response includes:
# release["upload_url"] = "https://uploads.github.com/repos/.../releases/{id}/assets{?name,label}"
# release["html_url"] = "https://github.com/{REPO}/releases/tag/v1.0.0-deck-name"
```

### Step 4: Upload each large file to the Release's upload_url

The key: **the upload URL takes the raw binary**, not base64, not multipart. The `Content-Type` is `application/octet-stream`.

```python
for filename in ["kunpeng-yihang-v4-leadership-style.pptx",
                 "kunpeng-yihang-v4-leadership-style.pdf"]:
    file_path = os.path.join(LOCAL_DIR, filename)
    with open(file_path, "rb") as f:
        binary = f.read()
    # Strip the {?name,label} template suffix and add ?name=<filename>
    upload_url = release["upload_url"].split("{")[0] + f"?name={filename}"
    req = urllib.request.Request(upload_url, data=binary, method="POST")
    req.add_header("Authorization", f"token {TOKEN}")
    req.add_header("Content-Type", "application/octet-stream")
    with urllib.request.urlopen(req, timeout=180) as resp:
        asset = json.loads(resp.read())
        # asset["browser_download_url"] is the direct download link
        print(f"  ✅ {asset['browser_download_url']}")
```

Note the **180s timeout** for the upload — large files over slow networks can legitimately take a minute or two to push. The Blob API's 60s default is what kills it.

## The hard gate (P29/P30 pattern)

Before any `POST /git/blobs` call, run:

```bash
du -h <file> | awk '{ if (substr($1, length($1)) == "M" && substr($1, 1, length($1)-1)+0 > 5) print "RELEASE: " $0; else if (substr($1, length($1)) == "G") print "RELEASE: " $0 }'
```

If the output contains "RELEASE: ...", the file is too big for the Blob API. Route to the Release path. Embed this as the first 2 lines of the push script, before any blob creation.

## What the user sees

After the push, send the user TWO links:

1. **The code commit**: `https://github.com/{REPO}/commit/{sha}` — for the workflow files (SKILL.md, scripts, examples, README)
2. **The release page**: `https://github.com/{REPO}/releases/tag/{tag}` — for the binary download (PPTX, PDF, ZIP)

The release page has direct download links the user can hand to clients without exposing the repo URL or the workflow. The user said "推荐给客户看的页面最好是仓库有了" — the release page is the public-facing delivery surface, the repo is the workflow surface.

## When NOT to use Releases

- The user is just iterating on the workflow (Pushing v0.1, v0.2, ...). Use the Blob API. Only create a Release when there's a stable deliverable.
- The artifact is text-only (Markdown, JSON, YAML). Use the Blob API.
- The artifact is a small (< 1 MB) image, even if it's the final product. Use the Blob API.

Use Releases **only** for "this is the final deliverable, clients download it from here" scenarios.

## Limits & pitfalls

| Limit | Value | Notes |
|---|---|---|
| Release asset size | 2 GB per asset | Way more than the Blob API's 100 MB |
| Number of assets per release | Unlimited | But UI gets crowded past 20 |
| Release upload timeout | 180s recommended (urllib default is too low) | The endpoint supports streaming |
| `Content-Type` | `application/octet-stream` | NOT multipart/form-data, NOT base64 |
| `Authorization` | `token {PAT}` (not `Bearer`) | GitHub-specific quirk |

## Related

- `github-data-api-push` skill — handles the small-file Blob API path
- `hermes-secrets` skill — safe way to read `GITHUB_TOKEN` from `~/.hermes/.env` without echoing
- `token-filter-workarounds` skill — the `***` filter that breaks heredocs with token prefixes
- Pitfall 32 in the parent skill (`ppt-content-to-deck-image-first`) — captures this pattern
