<#
  Build the vendored STS2MCP bridge and install/remove it in the game's mods/
  directory. Understudy sprint W1; [USER] ruling 1 (2026-08-04).

  This is a SEPARATE producer from deploy.ps1 and it owns a SEPARATE out-path:

      deploy.ps1         ->  <GameDir>\mods\klee          (the shipping mod)
      deploy_bridge.ps1  ->  <GameDir>\mods\STS2_MCP      (the test harness)

  Two scripts writing one directory is the failure art_lint's L11 exists to
  name, so the split is deliberate and stated. Neither script touches the
  other's target, and this one refuses to run if the paths ever collide.

  The bridge is a HARNESS, not a shipped artifact. It is not in the handoff
  zip, it is not a dependency of klee, and it is not something a co-op partner
  should have installed. -Remove exists because the reversibility log demands
  a one-command undo, not as an afterthought.

  NOTE: keep this file pure ASCII (validate.ps1 S8). Windows PowerShell 5.1
  reads .ps1 as ANSI unless there's a BOM.
#>
[CmdletBinding()]
param(
    [ValidateSet('Debug', 'Release')]
    [string]$Configuration = 'Release',
    # Uninstall: delete <GameDir>\mods\STS2_MCP and nothing else.
    [switch]$Remove
)

$ErrorActionPreference = 'Stop'

$root       = Split-Path -Parent $PSScriptRoot      # klee-mod
$repoRoot   = Split-Path -Parent $root
$vendorDir  = Join-Path $repoRoot 'vendor\STS2_MCP'
$csproj     = Join-Path $vendorDir 'STS2_MCP.csproj'
$stage      = Join-Path $root 'dist\STS2_MCP'
$localProps = Join-Path $root 'local.props'

if (-not (Test-Path $localProps)) {
    throw "local.props not found. Copy local.props.example to local.props and set GameDir."
}
$gameDir = ([xml](Get-Content $localProps)).Project.PropertyGroup.GameDir
if ([string]::IsNullOrWhiteSpace($gameDir)) { throw "GameDir is empty in local.props." }
if (-not (Test-Path $gameDir)) { throw "GameDir does not exist: $gameDir" }

$target    = Join-Path $gameDir 'mods\STS2_MCP'
$kleeTarget = Join-Path $gameDir 'mods\klee'
if ($target -eq $kleeTarget) {
    throw "Refusing to run: this script's target collides with deploy.ps1's."
}

$running = Get-Process -Name 'SlayTheSpire2' -ErrorAction SilentlyContinue
if ($running) {
    $ids = $running.Id -join ', '
    throw "Slay the Spire 2 is running (PID $ids). Close it first; it holds a lock on the mod dll."
}

if ($Remove) {
    if (Test-Path $target) {
        Remove-Item $target -Recurse -Force
        Write-Host "Removed $target" -ForegroundColor Green
    } else {
        Write-Host "Nothing to remove: $target is already absent" -ForegroundColor Yellow
    }
    Write-Host "Reversibility: the game dir no longer carries the bridge." -ForegroundColor Cyan
    return
}

# The pin claim is checked before the pin is built, so a drifted snapshot
# cannot reach the game dir wearing the pinned commit's name.
Write-Host "Checking the vendor pin..." -ForegroundColor Cyan
$py = Join-Path $repoRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $py)) { $py = 'python' }
& $py (Join-Path $repoRoot 'tools\lint_vendor_pin.py')
if ($LASTEXITCODE -ne 0) { throw "vendor pin lint failed; refusing to deploy a drifted snapshot." }

Write-Host "Building the bridge ($Configuration)..." -ForegroundColor Cyan
if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
New-Item -ItemType Directory -Force -Path $stage | Out-Null
& dotnet build $csproj -c $Configuration -o $stage -p:STS2GameDir="$gameDir" -v minimal --nologo
if ($LASTEXITCODE -ne 0) { throw "Bridge build failed." }

$dll = Join-Path $stage 'STS2_MCP.dll'
if (-not (Test-Path $dll)) { throw "Expected output not found: $dll" }

# ModManager walks mods/ recursively and JSON-parses everything it finds, so
# the same S1 discipline deploy.ps1 uses applies: ship the dll and exactly one
# manifest, never the build output that produced them.
Write-Host "Staging package..." -ForegroundColor Cyan
$stray = Get-ChildItem $stage -Recurse -File |
    Where-Object { $_.Extension -in @('.json', '.pdb', '.deps') }
foreach ($f in $stray) { Remove-Item $f.FullName -Force }
Copy-Item (Join-Path $vendorDir 'mod_manifest.json') `
    -Destination (Join-Path $stage 'STS2_MCP.json')

$leftover = Get-ChildItem $stage -Recurse -File -Filter *.json |
    Where-Object { $_.Name -ne 'STS2_MCP.json' }
if ($leftover) {
    throw ("Stray json in the stage would break ModManager's recursive scan: " +
           ($leftover.Name -join ', '))
}

Write-Host "Installing to $target" -ForegroundColor Cyan
if (Test-Path $target) { Remove-Item $target -Recurse -Force }
New-Item -ItemType Directory -Force -Path $target | Out-Null
Copy-Item "$stage\*" -Destination $target -Recurse

Write-Host "Installed:" -ForegroundColor Green
Get-ChildItem $target | ForEach-Object {
    Write-Host ("  " + $_.Name + "  (" + $_.Length + " bytes)")
}
Write-Host ""
Write-Host "Health check once the game is up:  GET http://localhost:15526/" -ForegroundColor Cyan
Write-Host "Undo this install with:            .\build\deploy_bridge.ps1 -Remove" -ForegroundColor Cyan
