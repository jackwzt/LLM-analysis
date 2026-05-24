param(
    [string]$ProjectRoot = $(Resolve-Path (Join-Path $PSScriptRoot "..")).Path
)

$ErrorActionPreference = "Stop"

function Get-Python312Path {
    $pyEntries = & py -0p 2>$null
    if (-not $pyEntries) {
        return $null
    }
    $match = $pyEntries | Select-String "3.12"
    if (-not $match) {
        return $null
    }
    return ($match.ToString() -replace "^\s*-V:3\.12\s+\*?\s*", "").Trim()
}

function Get-RscriptPath {
    $cmd = Get-Command Rscript -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }
    $candidate = Get-ChildItem "C:\Program Files\R" -Filter Rscript.exe -Recurse -ErrorAction SilentlyContinue |
        Sort-Object FullName -Descending |
        Select-Object -First 1
    if ($candidate) {
        return $candidate.FullName
    }
    return $null
}

$python312 = Get-Python312Path
if (-not $python312) {
    Write-Host "Python 3.12 not found. Installing with winget..."
    winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements --silent
    $python312 = Get-Python312Path
}

if (-not $python312) {
    throw "Python 3.12 installation failed or py launcher could not find it."
}

$venvPath = Join-Path $ProjectRoot ".venv312"
if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment at $venvPath"
    & $python312 -m venv $venvPath
}

$venvPython = Join-Path $venvPath "Scripts\python.exe"
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r (Join-Path $ProjectRoot "requirements.txt")

try {
    & $venvPython -m pip install --upgrade --force-reinstall torch --index-url https://download.pytorch.org/whl/cu128
}
catch {
    Write-Warning "CUDA-specific torch install failed. Falling back to the default torch wheel."
    & $venvPython -m pip install --upgrade --force-reinstall torch
}

foreach ($optionalPkg in @("bitsandbytes>=0.45", "autoawq>=0.2.9")) {
    & $venvPython -m pip install $optionalPkg
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Optional package install failed: $optionalPkg"
    }
}

$rscript = Get-RscriptPath
if (-not $rscript) {
    Write-Host "Rscript not found. Attempting winget install for R..."
    try {
        winget install -e --id RProject.R --accept-package-agreements --accept-source-agreements --silent
    }
    catch {
        Write-Warning "Automatic R install did not succeed. Install R manually, then rerun this script."
    }
    $rscript = Get-RscriptPath
}

if ($rscript) {
    & $rscript (Join-Path $ProjectRoot "scripts\install_r_packages.R")
}
else {
    Write-Warning "Rscript is still unavailable. Python setup finished, but R package installation was skipped."
}

Write-Host "Bootstrap complete."
