# GitHub Upload Plan

## Usually Safe to Push

- source scripts
- analysis scripts
- cleaned aggregate result tables
- redacted trial-level result tables, if non-sensitive
- Markdown reports
- analysis plans
- method definitions
- figures
- requirements file
- README updates
- `.gitignore`

## Usually Keep Local

- `.env`
- API keys
- credentials
- private tokens
- raw unredacted API logs
- payment or account information
- personal files
- temporary cache files
- raw provider payloads if sensitive
- model checkpoints unless intentionally released
- very large files that should use Git LFS or external storage

## Recommended Upload Scope for This Project

Push:

- `confirmatory_package/docs/`
- `confirmatory_package/scripts/`
- `confirmatory_package/outputs/tables/` after verifying no sensitive raw text is included
- `confirmatory_package/outputs/figures/`
- `fingerprint_package/docs/`
- `fingerprint_package/scripts/`
- `fingerprint_package/outputs/tables/` after verification
- `fingerprint_package/outputs/figures/`
- `LOCAL_PROJECT_INVENTORY.md`
- `GITHUB_UPLOAD_PLAN.md`
- `README.md`
- `requirements.txt`
- `.gitignore`

Do not push:

- `logs/`
- `.venv312/`
- `models/`
- raw API logs
- raw unredacted `results/*/raw_trials.csv` unless explicitly reviewed and redacted
- any file containing API keys or credentials

## Pre-Push Checks

Run these from the Git repository root before pushing:

```powershell
git status
git diff --stat
git diff -- .gitignore
git diff -- README.md
```

If using a cleaned GitHub repository at `<GIT_REPO_ROOT>`, copy only the reviewed package files and derived non-sensitive outputs into that repository before committing.
