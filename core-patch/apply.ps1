<#
.SYNOPSIS
    Applies the class-10 (Devourer) patches to azerothcore-wotlk and mod-playerbots.

.DESCRIPTION
    Dry-runs both patches first (git apply --check). Nothing is changed unless both would apply cleanly.
    Re-running on an already patched tree is detected and does nothing.

.EXAMPLE
    .\apply.ps1 -CorePath Z:\ChromaticawBots\azerothcore-wotlk
    .\apply.ps1 -CorePath Z:\src\ac -PlayerbotsPath Z:\src\ac\modules\mod-playerbots
#>
param(
    [Parameter(Mandatory = $true)][string]$CorePath,
    [string]$PlayerbotsPath = ""
)

$ErrorActionPreference = "Stop"
if (-not $PlayerbotsPath) { $PlayerbotsPath = Join-Path $CorePath "modules\mod-playerbots" }

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$targets = @(
    @{ Name = "azerothcore-wotlk"; Repo = $CorePath;       Patch = Join-Path $here "class-devourer.patch" },
    @{ Name = "mod-playerbots";    Repo = $PlayerbotsPath; Patch = Join-Path $here "playerbots-class-devourer.patch" }
)

# --ignore-whitespace: tolerate CRLF checkouts (core.autocrlf=true on Windows)
$gitArgs = @("apply", "--ignore-whitespace", "--whitespace=nowarn")

function Invoke-GitApply($repo, [string[]]$extra, $patch) {
    & git -C $repo @gitArgs @extra $patch 2>&1 | Out-Null
    return ($LASTEXITCODE -eq 0)
}

$todo = @()
foreach ($t in $targets) {
    if (-not (Test-Path (Join-Path $t.Repo ".git"))) { throw "$($t.Name): $($t.Repo) is not a git checkout" }
    if (Invoke-GitApply $t.Repo @("--check") $t.Patch) {
        $todo += $t
    }
    elseif (Invoke-GitApply $t.Repo @("--check", "-R") $t.Patch) {
        Write-Host "$($t.Name): already applied, skipping"
    }
    else {
        Write-Host "$($t.Name): patch does NOT apply cleanly. Details:" -ForegroundColor Red
        & git -C $t.Repo @gitArgs --check -v $t.Patch
        throw "Dry run failed for $($t.Name); nothing was changed."
    }
}

foreach ($t in $todo) {
    if (-not (Invoke-GitApply $t.Repo @() $t.Patch)) { throw "$($t.Name): git apply failed after a clean dry run" }
    Write-Host "$($t.Name): applied $([IO.Path]::GetFileName($t.Patch))" -ForegroundColor Green
}
Write-Host "Done. Rebuild the server (the core headers changed, expect a near-full rebuild)."
