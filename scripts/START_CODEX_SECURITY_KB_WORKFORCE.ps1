[CmdletBinding()]
param(
    [string]$RepoRoot = (Get-Location).Path,
    [string]$BlobRoot = "",
    [switch]$LaunchCodex
)

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path $RepoRoot).Path
if (-not (Test-Path (Join-Path $RepoRoot ".git"))) {
    throw "RepoRoot is not a Git checkout: $RepoRoot"
}

if ([string]::IsNullOrWhiteSpace($BlobRoot)) {
    $parent = Split-Path $RepoRoot -Parent
    $BlobRoot = Join-Path $parent "KNOWLEDGE_CORE_BLOBS"
}

New-Item -ItemType Directory -Force $BlobRoot | Out-Null
$env:KNOWLEDGE_CORE_BLOB_ROOT = $BlobRoot

if ($LaunchCodex -and -not (Get-Command codex -ErrorAction SilentlyContinue)) {
    throw "Codex CLI was not found in PATH. Run without -LaunchCodex to prepare worktrees only."
}

$lanes = @(
    "source_scout",
    "byte_acquirer",
    "legal_applicability",
    "taxonomy_classifier",
    "annotation_builder"
)

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$worktreeRoot = Join-Path (Split-Path $RepoRoot -Parent) "KNOWLEDGE_CORE_CODEX_WORKTREES"
New-Item -ItemType Directory -Force $worktreeRoot | Out-Null

Write-Host "Fetching origin/main..."
& git -C $RepoRoot fetch origin main
if ($LASTEXITCODE -ne 0) { throw "git fetch failed" }

$created = @()
foreach ($lane in $lanes) {
    $branch = "codex/lane-$lane-$stamp"
    $path = Join-Path $worktreeRoot "$lane-$stamp"

    Write-Host "Creating $lane -> $path"
    & git -C $RepoRoot worktree add -b $branch $path origin/main
    if ($LASTEXITCODE -ne 0) { throw "git worktree add failed for $lane" }

    $prompt = @"
Read AGENTS.md, security-knowledge/AGENTS.md, .ai/codex-local-workforce.yaml and .ai/task-queue/security-kb.yaml. Act as the '$lane' lane only. Claim the highest-priority READY task assigned to this lane. Work evidence-first and fail closed. Do not edit shared master inventories unless your role explicitly owns them. Finish with a compact evidence packet containing task_id, changed_paths, evidence_refs, facts_confirmed, facts_still_unknown, validators, and reconciliation_needed. Commit only focused in-scope changes to the current branch.
"@.Trim()

    $created += [pscustomobject]@{
        Lane = $lane
        Branch = $branch
        Worktree = $path
    }

    if ($LaunchCodex) {
        $escapedPath = $path.Replace("'", "''")
        $escapedPrompt = $prompt.Replace("'", "''")
        $command = "Set-Location '$escapedPath'; `$env:KNOWLEDGE_CORE_BLOB_ROOT='$($BlobRoot.Replace("'", "''"))'; codex '$escapedPrompt'"
        Start-Process powershell.exe -ArgumentList @("-NoExit", "-Command", $command) | Out-Null
    }
}

Write-Host ""
Write-Host "Stage-1 Security KB worktrees prepared:" -ForegroundColor Green
$created | Format-Table -AutoSize
Write-Host "Blob root: $BlobRoot"

if (-not $LaunchCodex) {
    Write-Host ""
    Write-Host "To launch Codex manually, cd into one worktree and run: codex"
    Write-Host "Or rerun this script with -LaunchCodex."
}

Write-Host ""
Write-Host "After accepted lane changes are integrated, run the reconciler once, then qa_guard."
