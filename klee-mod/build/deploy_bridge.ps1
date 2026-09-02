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

  PLAYING ALONGSIDE AN AGENT (2026-09-02). The bridge is installed BEFORE the
  owner launches, with the game closed -- deploy_proto.ps1 now does it as its
  last step, so every dev deploy leaves the install parallel-ready. The owner's
  Steam-launched game then carries the bridge on the default port 15526
  (lane 0) and an agent's second instance takes 15527 (lane 1, its own APPDATA;
  understudy/instances.py). Once a game is up holding this dll, this script
  cannot rewrite it and does not need to: the lane reuses a current install
  (understudy/soak.py `bridge_status`).

  -BuildOnly lints the pin and compiles, and stops before the game directory is
  touched at all. That is the check a bridge EDIT wants (EB-142): a worktree
  that is not the art-bearing main checkout has no business installing
  anything, and the compiler is still the only thing that verifies a gits/
  handler against the game's real assemblies.

  NOTE: keep this file pure ASCII (validate.ps1 S8). Windows PowerShell 5.1
  reads .ps1 as ANSI unless there's a BOM.
#>
[CmdletBinding()]
param(
    [ValidateSet('Debug', 'Release')]
    [string]$Configuration = 'Release',
    # Uninstall: delete <GameDir>\mods\STS2_MCP and nothing else.
    [switch]$Remove,
    # Compile only: lint the pin, build the dll into the staging directory, and
    # STOP before anything is copied into the game. Added for EB-142, whose C#
    # half had to be shown to compile from a worktree that must not touch the
    # game directory at all. It is also the cheap check a bridge edit wants
    # before the game is closed: the install path below refuses to run while
    # SlayTheSpire2.exe is up, and this path does not care.
    [switch]$BuildOnly
)

if ($Remove -and $BuildOnly) {
    throw "-Remove and -BuildOnly are opposites; pass one."
}

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

function Test-FileHeld {
    <#
      Is this file locked by another process RIGHT NOW? Opened for read/write
      with FileShare.None: if anything else holds it the open throws, and if
      nothing does, it is closed again having changed nothing.

      THIS IS THE QUESTION THE REFUSAL BELOW ACTUALLY NEEDS TO ASK, and it
      replaces asking whether a game process exists at all. Those are
      different questions, and a live attempt (2026-09-02) proved it: the
      owner's Steam-launched game had no mods\STS2_MCP in the install, held
      nothing, and the by-process refusal blocked a second understudy lane
      that was in no danger -- so Steam's tolerance of a second instance went
      untested for a reason that was never Steam's. A game that HAS loaded
      this dll does hold it, and that case is still refused, by the lock,
      which is the thing that is true.
    #>
    param([string]$Path)
    if (-not (Test-Path $Path)) { return $false }
    try {
        $fs = [System.IO.File]::Open(
            $Path, [System.IO.FileMode]::Open,
            [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
        $fs.Close()
        $fs.Dispose()
        return $false
    } catch {
        return $true
    }
}

if (-not $BuildOnly) {
    $running = Get-Process -Name 'SlayTheSpire2' -ErrorAction SilentlyContinue
    $ids = if ($running) { $running.Id -join ', ' } else { 'none' }
    $held = @(Get-ChildItem -Path $target -Recurse -File -ErrorAction SilentlyContinue |
              Where-Object { Test-FileHeld $_.FullName })
    if ($held) {
        $names = ($held | ForEach-Object { $_.Name }) -join ', '
        throw "A running Slay the Spire 2 (PID $ids) is holding $names under $target, so this cannot rewrite it. Close that game -- and if it is another understudy lane's, tear the lane down (python -m understudy.embark --teardown --lane N) rather than killing it."
    }
    if ($running) {
        Write-Host "NOTE: Slay the Spire 2 is running (PID $ids), but nothing under $target is locked, so this is safe." -ForegroundColor Yellow
        Write-Host "      Mods load at BOOT: a game that is already up will NOT pick this up. The next launch does -- a second understudy lane, or a restart." -ForegroundColor Yellow
    }
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

if ($BuildOnly) {
    Write-Host "Built (not installed): $dll" -ForegroundColor Green
    Write-Host "The game directory was not touched." -ForegroundColor Cyan
    return
}

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
