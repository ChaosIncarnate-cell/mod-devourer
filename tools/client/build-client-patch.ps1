# Builds (and with -Install, installs) the Devourer's client patch. Wrapper around build_client_patch.py.
#
#   .\tools\client\build-client-patch.ps1 -Client "C:\WoW" -Coa "D:\CoA\Data" -ClassIcon "D:\art\devourer.png" -Install
#
# -Coa takes several paths (comma separated); later ones win. On a new PC run the self-test first:
#   .\tools\client\build-client-patch.ps1 -SelfTest
param(
    [string]$Client,
    [string[]]$Coa = @(),
    [string]$ClassIcon,
    [string]$Name = "patch-Z.MPQ",
    [switch]$Install,
    [switch]$SelfTest
)
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path

function Invoke-Python {
    if (Get-Command py -ErrorAction SilentlyContinue) { & py -3 @args } else { & python @args }
}

Invoke-Python -c "import PIL" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing Pillow (needed for the class icon)..."
    Invoke-Python -m pip install --user pillow
    if ($LASTEXITCODE -ne 0) { throw "pip install pillow failed" }
}

if ($SelfTest) {
    Invoke-Python (Join-Path $here "selftest.py")
    exit $LASTEXITCODE
}
if (-not $Client) { throw "-Client <WoW folder> is required" }

$pyArgs = @((Join-Path $here "build_client_patch.py"), "--client", $Client, "--name", $Name)
foreach ($c in $Coa) { $pyArgs += @("--coa", $c) }
if ($ClassIcon) { $pyArgs += @("--class-icon", $ClassIcon) }
if ($Install) { $pyArgs += "--install" }

Invoke-Python @pyArgs
exit $LASTEXITCODE
