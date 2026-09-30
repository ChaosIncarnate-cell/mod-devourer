<#
.SYNOPSIS
    Reverts the class-10 (Devourer) patches from azerothcore-wotlk and mod-playerbots.

.DESCRIPTION
    Dry-runs both reversals first (git apply -R --check). Nothing is changed unless both would revert cleanly.
    A tree that is not patched is detected and skipped.
    Run the module's uninstall SQL first if class-10 characters exist (they would fail to load otherwise).

.EXAMPLE
    .\revert.ps1 -CorePath Z:\ChromaticawBots\azerothcore-wotlk
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

$gitArgs = @("apply", "--ignore-whitespace", "--whitespace=nowarn")

function Invoke-GitApply($repo, [string[]]$extra, $patch) {
    & git -C $repo @gitArgs @extra $patch 2>&1 | Out-Null
    return ($LASTEXITCODE -eq 0)
}

$todo = @()
foreach ($t in $targets) {
    if (-not (Test-Path (Join-Path $t.Repo ".git"))) { throw "$($t.Name): $($t.Repo) is not a git checkout" }
    if (Invoke-GitApply $t.Repo @("-R", "--check") $t.Patch) {
        $todo += $t
    }
    elseif (Invoke-GitApply $t.Repo @("--check") $t.Patch) {
        Write-Host "$($t.Name): not applied, skipping"
    }
    else {
        Write-Host "$($t.Name): patch does NOT revert cleanly. Details:" -ForegroundColor Red
        & git -C $t.Repo @gitArgs -R --check -v $t.Patch
        throw "Dry run failed for $($t.Name); nothing was changed."
    }
}

foreach ($t in $todo) {
    if (-not (Invoke-GitApply $t.Repo @("-R") $t.Patch)) { throw "$($t.Name): git apply -R failed after a clean dry run" }
    Write-Host "$($t.Name): reverted $([IO.Path]::GetFileName($t.Patch))" -ForegroundColor Green
}
Write-Host "Done. Rebuild the server."
