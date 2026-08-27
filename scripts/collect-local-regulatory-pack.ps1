param(
    [string]$InventoryCsv = "",
    [string]$KnowledgeCoreRoot = "G:\1\KNOWLEDGE_CORE",
    [string]$Branch = "agent/local-laws-gost-kb-import",
    [switch]$Apply,
    [switch]$Push
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version 2.0

function Write-Step([string]$Text) {
    Write-Host "`n=== $Text ===" -ForegroundColor Cyan
}

function Resolve-InventoryPath {
    param([string]$ExplicitPath)

    if ($ExplicitPath) {
        if (-not (Test-Path -LiteralPath $ExplicitPath)) {
            throw "Inventory CSV not found: $ExplicitPath"
        }
        return (Resolve-Path -LiteralPath $ExplicitPath).Path
    }

    $candidates = @(
        "G:\1\OTUS\Библиотека\_inventory\library_inventory.csv",
        "G:\1\OTUS\reports\library_inventory\library_inventory.csv",
        "G:\1\OTUS\library_inventory.csv"
    )

    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate) {
            return (Resolve-Path -LiteralPath $candidate).Path
        }
    }

    $found = Get-ChildItem -LiteralPath "G:\1\OTUS" -Filter "library_inventory.csv" -File -Recurse -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($found) {
        return $found.FullName
    }

    throw "library_inventory.csv was not found. Pass -InventoryCsv explicitly."
}

function Get-DocumentKind {
    param(
        [string]$FileName,
        [string]$FullPath
    )

    $n = [string]$FileName
    $p = [string]$FullPath

    # Require a standard designation shape; avoids false positives such as 'Гостиная'.
    $gostPattern = '(?i)(?:^|[^А-ЯA-Z])(?:ГОСТ|GOST)\s*(?:Р|R)?\s*(?:(?:ИСО|ISO)(?:[\/_\- ](?:МЭК|IEC))?\s*)?(?:ТО\s*)?\d{4,6}(?:[.\-]\d+)*(?:-\d{2,4})?'
    if ($n -match $gostPattern) {
        return "GOST"
    }

    $lawPatterns = @(
        '(?i)\b\d{1,4}\s*[-–—]?\s*ФЗ\b',
        '(?i)Федеральн\w*\s+закон',
        '(?i)Постановлен\w*\s+Правительств',
        '(?i)\bПП\s*РФ\b',
        '(?i)Указ\s+Президент',
        '(?i)Распоряжен\w*\s+Правительств',
        '(?i)Приказ\s+(?:ФСТЭК|ФСБ|Роскомнадзор|РКН|Минздрав|Минтранс|Минпромторг|Минэкономразвития|Минэнерго|Минцифры|СФР|Росфинмониторинг)'
    )

    foreach ($pattern in $lawPatterns) {
        if ($n -match $pattern) {
            return "LAW"
        }
    }

    # Known core laws sometimes exist as numeric-only filenames (149.pdf, 152.pdf, 187.pdf, etc.).
    if ($p -match '(?i)\\OTUS\\Библиотека\\разобрать\\' -and
        $n -match '^(?:63|98|126|149|152|187|323)(?:[-_ ]?ФЗ)?(?:\.|\s|_|-)' ) {
        return "LAW"
    }

    return $null
}

function Get-IdentityCandidate {
    param(
        [string]$Kind,
        [string]$FileName
    )

    if ($Kind -eq "GOST") {
        $patterns = @(
            '(?i)(ГОСТ\s*Р\s*ИСО[\/_ ]?МЭК\s*ТО\s*\d{4,6}(?:[.\-]\d+)*(?:-\d{2,4})?)',
            '(?i)(ГОСТ\s*Р\s*ИСО[\/_ ]?МЭК\s*\d{4,6}(?:[.\-]\d+)*(?:-\d{2,4})?)',
            '(?i)(ГОСТ\s*Р\s*\d{4,6}(?:[.\-]\d+)*(?:-\d{2,4})?)',
            '(?i)(GOST[-_ ]?R[-_ ]?\d{4,6}(?:[.\-]\d+)*(?:[-_]\d{2,4})?)'
        )
        foreach ($pattern in $patterns) {
            $m = [regex]::Match($FileName, $pattern)
            if ($m.Success) {
                return ($m.Groups[1].Value -replace '_',' ' -replace '\s+',' ').Trim().ToUpperInvariant()
            }
        }
        return "GOST_IDENTITY_REVIEW_REQUIRED"
    }

    $fz = [regex]::Match($FileName, '(?i)(\d{1,4})\s*[-–—]?\s*ФЗ')
    if ($fz.Success) {
        return ($fz.Groups[1].Value + "-ФЗ")
    }

    $pp = [regex]::Match($FileName, '(?i)Постановлен\w*\s+Правительств\w*(?:\s+Российской\s+Федерации|\s+РФ)?.*?(?:N|№)?\s*(\d{1,5})')
    if ($pp.Success) {
        return ("ПП РФ №" + $pp.Groups[1].Value)
    }

    $order = [regex]::Match($FileName, '(?i)Приказ\s+([^№N\d]{2,40}).*?(?:N|№)?\s*(\d{1,5})')
    if ($order.Success) {
        return (("ПРИКАЗ " + $order.Groups[1].Value.Trim() + " №" + $order.Groups[2].Value) -replace '\s+',' ')
    }

    return "LAW_IDENTITY_REVIEW_REQUIRED"
}

function Get-SafeFileName {
    param([string]$Name)
    $safe = $Name
    foreach ($ch in [IO.Path]::GetInvalidFileNameChars()) {
        $safe = $safe.Replace([string]$ch, '_')
    }
    $safe = $safe -replace '\s+', ' '
    return $safe.Trim()
}

function Get-RelativePathSafe {
    param([string]$Base, [string]$Path)
    try {
        $baseUri = New-Object System.Uri(($Base.TrimEnd('\') + '\'))
        $pathUri = New-Object System.Uri($Path)
        return [Uri]::UnescapeDataString($baseUri.MakeRelativeUri($pathUri).ToString()).Replace('/', '\')
    }
    catch {
        return $Path
    }
}

Write-Step "Resolve inputs"
$InventoryCsv = Resolve-InventoryPath -ExplicitPath $InventoryCsv
Write-Host "Inventory: $InventoryCsv"
Write-Host "Knowledge repo: $KnowledgeCoreRoot"
Write-Host "Mode: $(if ($Apply) { 'APPLY' } else { 'PLAN' })"
Write-Host "Push: $Push"

if (-not (Test-Path -LiteralPath $KnowledgeCoreRoot)) {
    if (-not $Apply) {
        throw "KnowledgeCoreRoot does not exist in PLAN mode: $KnowledgeCoreRoot"
    }
    Write-Step "Clone KNOWLEDGE_CORE"
    & git clone --branch $Branch --single-branch "https://github.com/VictorKVS/KNOWLEDGE_CORE.git" $KnowledgeCoreRoot
    if ($LASTEXITCODE -ne 0) { throw "git clone failed" }
}

if (-not (Test-Path -LiteralPath (Join-Path $KnowledgeCoreRoot ".git"))) {
    throw "Not a git clone: $KnowledgeCoreRoot"
}

if ($Push) {
    Write-Step "Git preflight"
    Push-Location $KnowledgeCoreRoot
    try {
        $dirty = (& git status --porcelain)
        if ($dirty) {
            throw "Working tree is not clean. Commit/stash your changes before -Push."
        }
        & git fetch origin $Branch
        if ($LASTEXITCODE -ne 0) { throw "git fetch failed" }

        $localBranch = (& git branch --list $Branch).Trim()
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

Write-Step "Load inventory"
$rows = Import-Csv -LiteralPath $InventoryCsv -Delimiter ';'
$allowedExt = @('.pdf','.odt','.doc','.docx','.rtf','.txt','.html','.htm','.xml')
$candidates = New-Object System.Collections.Generic.List[object]

foreach ($row in $rows) {
    $ext = ([string]$row.extension).ToLowerInvariant()
    if ($allowedExt -notcontains $ext) { continue }

    $kind = Get-DocumentKind -FileName ([string]$row.filename) -FullPath ([string]$row.full_path)
    if (-not $kind) { continue }

    if (-not (Test-Path -LiteralPath ([string]$row.full_path))) {
        $candidates.Add([pscustomobject]@{
            storage = [string]$row.storage
            full_path = [string]$row.full_path
            filename = [string]$row.filename
            extension = $ext
            size_bytes = [int64]$row.size_bytes
            doc_kind = $kind
            identity_candidate = Get-IdentityCandidate -Kind $kind -FileName ([string]$row.filename)
            source_exists = $false
            sha256 = $null
        })
        continue
    }

    $sha = (Get-FileHash -LiteralPath ([string]$row.full_path) -Algorithm SHA256).Hash.ToLowerInvariant()
    $candidates.Add([pscustomobject]@{
        storage = [string]$row.storage
        full_path = [string]$row.full_path
        filename = [string]$row.filename
        extension = $ext
        size_bytes = [int64](Get-Item -LiteralPath ([string]$row.full_path)).Length
        doc_kind = $kind
        identity_candidate = Get-IdentityCandidate -Kind $kind -FileName ([string]$row.filename)
        source_exists = $true
        sha256 = $sha
    })
}

$localPackRoot = Join-Path $KnowledgeCoreRoot "_LOCAL_SOURCE_PACK\RU_REGULATORY_ALL"
$trackedRoot = Join-Path $KnowledgeCoreRoot "security-knowledge\corpus\ru-local-regulatory-import"
$trackedLaws = Join-Path $trackedRoot "laws"
$trackedManifests = Join-Path $trackedRoot "manifests"

$manifest = New-Object System.Collections.Generic.List[object]
$seenSha = @{}
$plannedNames = @{}
$localCopied = 0
$exactDupes = 0
$missing = 0
$githubLawFiles = 0
$githubTooLarge = 0

Write-Step "Build pack plan"
foreach ($item in ($candidates | Sort-Object doc_kind, identity_candidate, full_path)) {
    if (-not $item.source_exists) {
        $missing++
        $manifest.Add([pscustomobject]@{
            doc_kind = $item.doc_kind
            identity_candidate = $item.identity_candidate
            sha256 = ""
            size_bytes = $item.size_bytes
            source_path = $item.full_path
            original_filename = $item.filename
            local_pack_file = ""
            duplicate_of = ""
            github_policy = if ($item.doc_kind -eq 'GOST') { 'METADATA_ONLY_PUBLIC_REPO' } else { 'PUBLIC_NPA_BINARY_CANDIDATE' }
            github_target = ""
            status = 'SOURCE_MISSING'
        })
        continue
    }

    if ($seenSha.ContainsKey($item.sha256)) {
        $exactDupes++
        $manifest.Add([pscustomobject]@{
            doc_kind = $item.doc_kind
            identity_candidate = $item.identity_candidate
            sha256 = $item.sha256
            size_bytes = $item.size_bytes
            source_path = $item.full_path
            original_filename = $item.filename
            local_pack_file = ""
            duplicate_of = $seenSha[$item.sha256]
            github_policy = if ($item.doc_kind -eq 'GOST') { 'METADATA_ONLY_PUBLIC_REPO' } else { 'PUBLIC_NPA_BINARY_CANDIDATE' }
            github_target = ""
            status = 'EXACT_DUPLICATE_SHA256'
        })
        continue
    }

    $prefix = if ($item.doc_kind -eq 'GOST') { 'GOST__' } else { 'LAW__' }
    $destName = Get-SafeFileName ($prefix + $item.filename)
    $baseName = [IO.Path]::GetFileNameWithoutExtension($destName)
    $ext = [IO.Path]::GetExtension($destName)

    if ($plannedNames.ContainsKey($destName.ToLowerInvariant())) {
        $destName = $baseName + '__' + $item.sha256.Substring(0,8) + $ext
    }
    $plannedNames[$destName.ToLowerInvariant()] = $true
    $seenSha[$item.sha256] = $destName

    $localDest = Join-Path $localPackRoot $destName
    $githubTarget = ""
    $status = if ($Apply) { 'LOCAL_COPY_PENDING' } else { 'PLAN_COPY' }

    if ($item.doc_kind -eq 'LAW') {
        if ($item.size_bytes -gt 95000000) {
            $githubTooLarge++
            $githubTarget = ""
        }
        else {
            $githubTarget = "security-knowledge/corpus/ru-local-regulatory-import/laws/$destName"
        }
    }

    if ($Apply) {
        New-Item -ItemType Directory -Path $localPackRoot -Force | Out-Null
        Copy-Item -LiteralPath $item.full_path -Destination $localDest -Force
        $copiedSha = (Get-FileHash -LiteralPath $localDest -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($copiedSha -ne $item.sha256) {
            throw "SHA-256 mismatch after copy: $($item.full_path)"
        }
        $localCopied++
        $status = 'LOCAL_COPIED_SHA256_VERIFIED'

        if ($item.doc_kind -eq 'LAW' -and $githubTarget) {
            New-Item -ItemType Directory -Path $trackedLaws -Force | Out-Null
            $lawDest = Join-Path $trackedLaws $destName
            Copy-Item -LiteralPath $item.full_path -Destination $lawDest -Force
            $lawSha = (Get-FileHash -LiteralPath $lawDest -Algorithm SHA256).Hash.ToLowerInvariant()
            if ($lawSha -ne $item.sha256) {
                throw "SHA-256 mismatch in tracked law copy: $($item.full_path)"
            }
            $githubLawFiles++
        }
    }

    $manifest.Add([pscustomobject]@{
        doc_kind = $item.doc_kind
        identity_candidate = $item.identity_candidate
        sha256 = $item.sha256
        size_bytes = $item.size_bytes
        source_path = $item.full_path
        original_filename = $item.filename
        local_pack_file = $destName
        duplicate_of = ""
        github_policy = if ($item.doc_kind -eq 'GOST') { 'METADATA_ONLY_PUBLIC_REPO' } elseif ($githubTarget) { 'PUBLIC_NPA_BINARY_CANDIDATE' } else { 'GITHUB_BINARY_TOO_LARGE' }
        github_target = $githubTarget
        status = $status
    })
}

$stats = [ordered]@{
    generated_at = (Get-Date).ToString('o')
    mode = if ($Apply) { 'APPLY' } else { 'PLAN' }
    inventory_csv = $InventoryCsv
    candidates_total = $candidates.Count
    candidates_gost = @($candidates | Where-Object { $_.doc_kind -eq 'GOST' }).Count
    candidates_law = @($candidates | Where-Object { $_.doc_kind -eq 'LAW' }).Count
    unique_sha256_files = $seenSha.Count
    exact_duplicate_files = $exactDupes
    source_missing = $missing
    local_copied = $localCopied
    github_law_files_prepared = $githubLawFiles
    github_binary_too_large = $githubTooLarge
    gost_binary_publication = 'BLOCKED_BY_POLICY_METADATA_ONLY'
    source_files_deleted = 0
    source_files_moved = 0
}

if ($Apply) {
    Write-Step "Write manifests"
    New-Item -ItemType Directory -Path $localPackRoot -Force | Out-Null
    New-Item -ItemType Directory -Path $trackedManifests -Force | Out-Null

    $localCsv = Join-Path $localPackRoot '_manifest.csv'
    $localJsonl = Join-Path $localPackRoot '_manifest.jsonl'
    $statsJson = Join-Path $localPackRoot '_stats.json'

    $manifest | Export-Csv -LiteralPath $localCsv -Delimiter ';' -NoTypeInformation -Encoding UTF8
    $manifest | ForEach-Object { $_ | ConvertTo-Json -Compress } | Set-Content -LiteralPath $localJsonl -Encoding UTF8
    $stats | ConvertTo-Json | Set-Content -LiteralPath $statsJson -Encoding UTF8

    $manifest | Export-Csv -LiteralPath (Join-Path $trackedManifests 'local-regulatory-manifest.csv') -Delimiter ';' -NoTypeInformation -Encoding UTF8
    $manifest | ForEach-Object { $_ | ConvertTo-Json -Compress } | Set-Content -LiteralPath (Join-Path $trackedManifests 'local-regulatory-manifest.jsonl') -Encoding UTF8
    $stats | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $trackedManifests 'local-regulatory-stats.json') -Encoding UTF8

    $readme = @"
# Local regulatory source import

Generated by `scripts/collect-local-regulatory-pack.ps1`.

- Full local source pack is kept under `_LOCAL_SOURCE_PACK/RU_REGULATORY_ALL` and is ignored by Git.
- Public-law source binaries may be copied under `laws/` with SHA-256 recorded in the manifest.
- Full GOST/standard binaries are intentionally NOT published to this public repository. Their local bytes remain in the source pack; only metadata, identity candidates and SHA-256 enter GitHub.
- No source file is deleted or moved.
- Filename-derived identity is a candidate until content/authority verification.
- Currentness and legal applicability are separate gates.
"@
    Set-Content -LiteralPath (Join-Path $trackedRoot 'README.md') -Value $readme -Encoding UTF8
}

Write-Step "Result"
$stats | ConvertTo-Json

if ($Apply) {
    Write-Host "Local pack: $localPackRoot"
    Write-Host "Tracked import: $trackedRoot"
}

if ($Push) {
    if (-not $Apply) {
        throw "-Push requires -Apply"
    }

    Write-Step "Commit and push public-safe import"
    Push-Location $KnowledgeCoreRoot
    try {
        & git add -- "security-knowledge/corpus/ru-local-regulatory-import"
        if ($LASTEXITCODE -ne 0) { throw "git add failed" }

        $staged = (& git diff --cached --name-only)
        if (-not $staged) {
            Write-Host "No tracked changes to commit."
        }
        else {
            & git commit -m "Import local regulatory source pack"
            if ($LASTEXITCODE -ne 0) { throw "git commit failed" }
            & git push origin $Branch
            if ($LASTEXITCODE -ne 0) { throw "git push failed" }
        }
    }
    finally {
        Pop-Location
    }
}
