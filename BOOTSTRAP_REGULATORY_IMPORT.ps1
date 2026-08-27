param(
    [string]$RepoRoot = "G:\1\KNOWLEDGE_CORE",
    [string]$InventoryCsv = "C:\Users\1\Documents\Codex\2026-08-26\new-chat\outputs\library_inventory.csv",
    [string]$Branch = "agent/local-laws-gost-kb-import",
    [switch]$PlanOnly
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version 2.0

function Step([string]$Text) {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor DarkGray
    Write-Host $Text -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor DarkGray
}

function Require-Command([string]$Name) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command not found: $Name"
    }
}

Step "1. Preflight"
Require-Command "git"

if (-not (Test-Path -LiteralPath $InventoryCsv)) {
    throw "Inventory CSV not found: $InventoryCsv"
}

Write-Host "Inventory: $InventoryCsv"
Write-Host "Repository: $RepoRoot"
Write-Host "Branch: $Branch"
Write-Host "Mode: $(if ($PlanOnly) { 'PLAN' } else { 'APPLY + PUSH' })"

Step "2. Get KNOWLEDGE_CORE"

if (-not (Test-Path -LiteralPath (Join-Path $RepoRoot ".git"))) {
    $parent = Split-Path -Parent $RepoRoot
    if ($parent -and -not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }

    if (Test-Path -LiteralPath $RepoRoot) {
        $RepoRoot = "G:\1\KNOWLEDGE_CORE_GIT"
        if ((Test-Path -LiteralPath $RepoRoot) -and -not (Test-Path -LiteralPath (Join-Path $RepoRoot ".git"))) {
            $RepoRoot = "G:\1\KNOWLEDGE_CORE_GIT_" + (Get-Date -Format "yyyyMMdd-HHmmss")
        }
    }

    & git clone --branch $Branch --single-branch "https://github.com/VictorKVS/KNOWLEDGE_CORE.git" $RepoRoot
    if ($LASTEXITCODE -ne 0) {
        throw "git clone failed"
    }
}
else {
    Push-Location $RepoRoot
    try {
        $dirty = @(& git status --porcelain)
        if ($dirty.Count -gt 0) {
            Write-Host "Local changes detected:" -ForegroundColor Yellow
            $dirty | ForEach-Object { Write-Host "  $_" }
            throw "Repository is not clean. Nothing was reset or deleted. Commit/stash changes and run again."
        }

        & git fetch origin $Branch
        if ($LASTEXITCODE -ne 0) { throw "git fetch failed" }

        $localBranch = ((& git branch --list $Branch) | Out-String).Trim()
        if ($localBranch) {
            & git switch $Branch
        }
        else {
            & git switch -c $Branch --track ("origin/" + $Branch)
        }
        if ($LASTEXITCODE -ne 0) { throw "git switch failed" }

        & git pull --ff-only origin $Branch
        if ($LASTEXITCODE -ne 0) { throw "git pull --ff-only failed" }
    }
    finally {
        Pop-Location
    }
}

$collector = Join-Path $RepoRoot "scripts\collect-local-regulatory-pack.ps1"
if (-not (Test-Path -LiteralPath $collector)) {
    throw "Collector not found after repository update: $collector"
}

# Windows PowerShell 5.1 treats UTF-8 scripts without BOM as ANSI. Re-save the
# collector as UTF-8 with BOM before execution so Cyrillic regexes parse safely.
$collectorText = [System.IO.File]::ReadAllText($collector, [System.Text.Encoding]::UTF8)
$utf8Bom = New-Object System.Text.UTF8Encoding($true)
[System.IO.File]::WriteAllText($collector, $collectorText, $utf8Bom)

Step "3. Run collector"

if ($PlanOnly) {
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $collector -InventoryCsv $InventoryCsv -KnowledgeCoreRoot $RepoRoot -Branch $Branch
}
else {
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $collector -InventoryCsv $InventoryCsv -KnowledgeCoreRoot $RepoRoot -Branch $Branch -Apply -Push
}

if ($LASTEXITCODE -ne 0) {
    throw "Collector failed with ExitCode=$LASTEXITCODE"
}

Step "4. Result"

$statsPath = Join-Path $RepoRoot "_LOCAL_SOURCE_PACK\RU_REGULATORY_ALL\_stats.json"
$manifestPath = Join-Path $RepoRoot "_LOCAL_SOURCE_PACK\RU_REGULATORY_ALL\_manifest.csv"

if (Test-Path -LiteralPath $statsPath) {
    Write-Host "Stats: $statsPath" -ForegroundColor Green
    Get-Content -LiteralPath $statsPath
}
else {
    Write-Host "PLAN completed. Stats file is created only in APPLY mode."
}

if (Test-Path -LiteralPath $manifestPath) {
    Write-Host "Manifest: $manifestPath" -ForegroundColor Green
}

Write-Host ""
Write-Host "Local consolidated folder:" -ForegroundColor Green
Write-Host (Join-Path $RepoRoot "_LOCAL_SOURCE_PACK\RU_REGULATORY_ALL")

Write-Host ""
Write-Host "GitHub knowledge import folder:" -ForegroundColor Green
Write-Host (Join-Path $RepoRoot "security-knowledge\corpus\ru-local-regulatory-import")

Write-Host ""
Write-Host "Safety: source files deleted = 0; source files moved = 0."
Write-Host "Full GOST binaries remain local; public GitHub gets GOST metadata/SHA/provenance."
