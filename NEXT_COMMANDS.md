# Next Commands

Set these placeholders before running:

```powershell
$LOCAL_PROJECT_ROOT = "<LOCAL_PROJECT_ROOT>"
$GIT_REPO_ROOT = "<GIT_REPO_ROOT>"
```

## Regenerate Public Summaries

```powershell
Set-Location $LOCAL_PROJECT_ROOT
.\.venv312\Scripts\python.exe .\confirmatory_package\scripts\05_make_public_summary_tables.py
```

## Regenerate Heterogeneity Summary

```powershell
Set-Location $LOCAL_PROJECT_ROOT
.\.venv312\Scripts\python.exe .\confirmatory_package\scripts\06_make_heterogeneity_summary.py
```

## Run Release Safety Check

```powershell
Set-Location $LOCAL_PROJECT_ROOT
.\.venv312\Scripts\python.exe .\scripts\check_release_safety.py
```

## Inspect Release Candidate

```powershell
Set-Location $LOCAL_PROJECT_ROOT
Get-Content .\github_release_candidate\RELEASE_CANDIDATE_MANIFEST.md -Raw
Get-Content .\github_release_candidate\RELEASE_SAFETY_REPORT.md -Raw
Get-ChildItem .\github_release_candidate -Recurse -File | Select-Object FullName,Length,LastWriteTime
```

## Copy Release Candidate Into Git Repository

Review the release candidate and safety report before running.

```powershell
$src = Join-Path $LOCAL_PROJECT_ROOT "github_release_candidate"
$dst = $GIT_REPO_ROOT
Copy-Item -Path (Join-Path $src "*") -Destination $dst -Recurse -Force
```

## Inspect Git State

```powershell
git -C $GIT_REPO_ROOT status
git -C $GIT_REPO_ROOT diff --stat
git -C $GIT_REPO_ROOT diff --name-only
```

## Stage and Commit Locally After Manual Review

```powershell
git -C $GIT_REPO_ROOT add .
git -C $GIT_REPO_ROOT status
git -C $GIT_REPO_ROOT commit -m "Add confirmatory analysis and fingerprint release package"
```

## Push Only After Manual Review

Do not push until you have inspected the manifest, safety report, staged files, and diff.

```powershell
git -C $GIT_REPO_ROOT push
```
