<#
  THE DEV DEPLOY. Build Klee WITH the quarantined prototype surface compiled
  in, and stage it into the game's mods/ directory.

  WHY THIS IS A SECOND SCRIPT AND NOT A SWITCH ON deploy.ps1.

  tier0/tests/test_prototype_surface.py asserts that neither deploy.ps1 nor
  validate.ps1 contains the string "PrototypeCards" -- a bare substring check
  over the whole file, comments included. That assertion IS the quarantine's
  release-path leg (R213 B): the release scripts cannot set the flag, cannot
  be talked into setting it, and cannot describe setting it. A `-Prototype`
  switch on deploy.ps1 would have to name the property to pass it, so the
  ruling's own guard forbids the shape. One dev file that the release path
  never calls is the arrangement that leaves both halves true.

  WHAT IS DIFFERENT FROM deploy.ps1, and it is exactly three things:

    1. `-p:PrototypeCards=true` on the build, which compiles
       Cards/Prototype/** and defines PROTOTYPE_CARDS.
    2. The staged package version carries the +proto build metadata, so a dev
       build is identifiable on sight in the game's own version string.
    3. `tools/gen_prototype_cards.py --check` runs FIRST. The release gate's
       S6a runs the ROSTER codegen staleness check, which cannot see this
       surface -- so without this a dev deploy could ship prototype classes
       that no longer match the sheet, which is the one way this script could
       hand a staged turn a card nobody wrote.

  WHAT IS NOT DIFFERENT, deliberately: the gate. validate.ps1 runs whole --
  every S-rule and the full pytest suite, with no fast mode requested and
  nothing skipped. A prototype build that skipped gates would prove nothing
  about the cards it exists to try.

  A DEV PACKAGE CHANGES NOTHING FOR ORDINARY PLAY. Prototype rows are
  off-pool: in each character's off-pool list so CardModel.Pool resolves, out
  of GetUnlockedCards so no reward roll and no card transform can produce one.
  The only door in is a grant by id through the understudy tooling. So the
  difference between this package and the release one, for anybody just
  playing, is that some extra classes exist and are never reachable.

  RESTORING THE RELEASE BUILD. There is no --restore switch here and there
  should not be, because there is nothing to restore FROM: this script
  overwrites mods\klee, and so does deploy.ps1. The undo is simply

      klee-mod\build\deploy.ps1

  run from the art-bearing main checkout, which rebuilds without the property
  (the directory is then Compile Remove'd, so the classes are not in the dll
  at all) and overwrites mods\klee again. Confirm it took by reading the
  version in game: a release build has no +proto. Do this before any
  measured run, any handoff, and any co-op session.

  NO -Package SWITCH. deploy.ps1 has one; this must not. A handoff zip is a
  build somebody else runs, and a dev build carrying uncompiled-elsewhere
  prototype classes is not a thing to hand anyone -- co-op is lockstep and a
  peer on a release build has no such classes.

  NOTE: keep this file pure ASCII (validate.ps1 S8 sweeps every .ps1 in the
  repo). Windows PowerShell 5.1 reads .ps1 as ANSI unless there is a BOM.
#>
[CmdletBinding()]
param(
    [ValidateSet('Debug', 'Release')]
    [string]$Configuration = 'Release',
    # Passed through to validate.ps1 S7, same meaning as on deploy.ps1: an
    # acknowledgement of a stale local game_ref, not a fix.
    [switch]$AllowIncompleteGameRef
)

$ErrorActionPreference = 'Stop'

# The version policy is SHARED with deploy.ps1 and validate.ps1 so the
# deploy-time stamp and the gate that checks it cannot compute it
# differently. This script's only addition is the -Prototype switch.
. (Join-Path $PSScriptRoot 'version.ps1')

$root       = Split-Path -Parent $PSScriptRoot
$repoRoot   = Split-Path -Parent $root
$csproj     = Join-Path $root 'KleeCode\KleeCode.csproj'
$packageDir = Join-Path $root 'Klee'
$stage      = Join-Path $root 'dist\klee'
$localProps = Join-Path $root 'local.props'
$venvPython = Join-Path $repoRoot '.venv\Scripts\python.exe'

function Invoke-RepoPython {
    <#
      The repo's own interpreter, with PYTHONPATH pinned to the repo root so
      `-m tools.x` resolves regardless of the working directory. Copied in
      shape from validate.ps1 because tier0/tests/test_repo_python_convention
      requires any script that shells out to define one of these rather than
      calling an interpreter bare. EAP is lowered around the call and
      restored in `finally`: in PS 5.1 a native command's stderr under
      EAP=Stop raises NativeCommandError even on exit code 0.
    #>
    param([Parameter(Mandatory = $true, ValueFromRemainingArguments = $true)]
          [string[]]$Arguments)
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    $prevPyPath = $env:PYTHONPATH
    $env:PYTHONPATH = if ($prevPyPath) { "$repoRoot;$prevPyPath" } else { $repoRoot }
    try {
        & $venvPython @Arguments 2>&1
    } finally {
        $ErrorActionPreference = $prev
        $env:PYTHONPATH = $prevPyPath
    }
}

if (-not (Test-Path $localProps)) {
    throw "local.props not found. Copy local.props.example to local.props and set GameDir. (A worktree has none: this script runs from the art-bearing main checkout only.)"
}

$gameDir = ([xml](Get-Content $localProps)).Project.PropertyGroup.GameDir
if ([string]::IsNullOrWhiteSpace($gameDir)) { throw "GameDir is empty in local.props." }
if (-not (Test-Path $gameDir)) { throw "GameDir does not exist: $gameDir" }

$running = Get-Process -Name 'SlayTheSpire2' -ErrorAction SilentlyContinue
if ($running) {
    $ids = $running.Id -join ', '
    throw "Slay the Spire 2 is running (PID $ids). Close the game before deploying; it holds a lock on klee.dll."
}

# The prototype codegen staleness gate. FIRST, before anything is built:
# emitting a dev package from a sheet that no longer matches the committed
# C# is the one failure this script could produce that the shared gate below
# cannot see.
Write-Host "Checking the prototype surface is in sync..." -ForegroundColor Cyan
if (-not (Test-Path $venvPython)) {
    throw "repo venv python not found at $venvPython; cannot check the prototype codegen."
}
$protoGen = Join-Path $repoRoot 'tools\gen_prototype_cards.py'
$genOut = Invoke-RepoPython $protoGen --check
if ($LASTEXITCODE -ne 0) {
    $genOut | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
    throw "the prototype surface and its generated C# disagree. Run: .venv\Scripts\python tools\gen_prototype_cards.py"
}
$genOut | ForEach-Object { Write-Host "  $_" }

Write-Host "Building ($Configuration) WITH the prototype surface..." -ForegroundColor Magenta
& dotnet build $csproj -c $Configuration -v minimal --nologo -p:PrototypeCards=true
if ($LASTEXITCODE -ne 0) { throw "Build failed." }

$dll = Join-Path $root "KleeCode\bin\$Configuration\klee.dll"
if (-not (Test-Path $dll)) { throw "Expected output not found: $dll" }

Write-Host "Staging package..." -ForegroundColor Cyan
if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
New-Item -ItemType Directory -Force -Path $stage | Out-Null
Copy-Item (Join-Path $packageDir 'manifest.json') -Destination $stage
Copy-Item $dll -Destination $stage

# MAJOR.AUTO+proto (or +proto.dirty). The source manifest is never written to.
$version = Get-PackageVersion `
    -SourceManifest (Join-Path $packageDir 'manifest.json') `
    -RepoRoot $repoRoot `
    -Prototype
$stagedManifest = Join-Path $stage 'manifest.json'
$sm = Get-Content $stagedManifest -Raw | ConvertFrom-Json
$sm.version = $version.Version
($sm | ConvertTo-Json -Depth 10) | Set-Content $stagedManifest -Encoding utf8
Write-Host "Stamped package version $($version.Version)" -ForegroundColor Magenta

Write-Host ""
Write-Host "*** PROTOTYPE BUILD ***" -ForegroundColor Magenta
Write-Host "  The quarantined prototype surface is COMPILED IN. Off-pool, so" -ForegroundColor Magenta
Write-Host "  ordinary play is unchanged and no reward roll can offer one." -ForegroundColor Magenta
Write-Host "  Reach a row only by id, through the understudy grant tooling." -ForegroundColor Magenta
Write-Host "  DO NOT hand this build to a co-op partner, and run" -ForegroundColor Magenta
Write-Host "  klee-mod\build\deploy.ps1 to put the release build back." -ForegroundColor Magenta
Write-Host ""

if ($version.IsDirty) {
    Write-Host "*** DIRTY WORKING TREE ***" -ForegroundColor Red
    Write-Host ("  $($version.DirtyFiles.Count) uncommitted change(s); version stamped +proto.dirty.") -ForegroundColor Red
    foreach ($f in ($version.DirtyFiles | Select-Object -First 10)) {
        Write-Host "    $f" -ForegroundColor DarkYellow
    }
    if ($version.DirtyFiles.Count -gt 10) {
        Write-Host ("    ... and " + ($version.DirtyFiles.Count - 10) + " more") -ForegroundColor DarkYellow
    }
    Write-Host ""
}

# Card art, the same flat destination deploy.ps1 stages into and the same
# four source dirs. A prototype row has no art of its own by design -- art is
# commissioned when a slice is ACCEPTED and its rows move to a real sheet --
# so a prototype card renders with no portrait, which is correct and is not
# a warning.
$artSrcDirs = @(
    (Join-Path (Split-Path -Parent $root) 'ImageGen\images\cards\klee'),
    (Join-Path (Split-Path -Parent $root) 'ImageGen\images\cards\furina'),
    (Join-Path (Split-Path -Parent $root) 'ImageGen\images\cards\kokomi'),
    (Join-Path (Split-Path -Parent $root) 'ImageGen\images\cards\companions')
)
$artDst = Join-Path $stage 'images\cards'
foreach ($artSrc in $artSrcDirs) {
    if (Test-Path $artSrc) {
        New-Item -ItemType Directory -Force -Path $artDst | Out-Null
        Copy-Item (Join-Path $artSrc '*.png') -Destination $artDst
    } else {
        Write-Host "WARNING: no card art at $artSrc" -ForegroundColor Yellow
    }
}
if (Test-Path $artDst) {
    $n = (Get-ChildItem $artDst -Filter '*.png').Count
    Write-Host "Staged $n card images" -ForegroundColor Cyan
}

# The pck, exactly as deploy.ps1 stages it. Missing is a warning here and a
# validate finding below (S2/S12), which is the same split deploy.ps1 uses.
$pck = Join-Path $root 'assets\klee.pck'
$pckContract = Join-Path $root 'assets\klee.pck.contract.txt'
if (Test-Path $pck) {
    Copy-Item $pck -Destination $stage
    if (Test-Path $pckContract) {
        Copy-Item $pckContract -Destination $stage
    } else {
        Write-Host "WARNING: no PCK contract at $pckContract; rebuild with tools\build_pck.ps1." -ForegroundColor Yellow
    }
} else {
    Write-Host "WARNING: no klee.pck at $pck; run tools\build_pck.ps1 first (validate will fail below)." -ForegroundColor Yellow
}

# THE SAME GATE, WHOLE. -PrototypeBuild changes exactly one rule: S3 accepts
# the +proto mark instead of refusing it by name. Nothing else is relaxed,
# and the fast inner-loop mode is never requested.
Write-Host "Validating package (full gate)..." -ForegroundColor Cyan
& (Join-Path $PSScriptRoot 'validate.ps1') `
    -StageDir $stage `
    -SourceDir (Join-Path $root 'KleeCode') `
    -GameDir $gameDir `
    -AllowIncompleteGameRef:$AllowIncompleteGameRef `
    -PrototypeBuild

$target = Join-Path $gameDir 'mods\klee'
Write-Host "Deploying to $target" -ForegroundColor Magenta
if (Test-Path $target) { Remove-Item $target -Recurse -Force }
New-Item -ItemType Directory -Force -Path $target | Out-Null
Copy-Item "$stage\*" -Destination $target -Recurse

Write-Host "Deployed (PROTOTYPE):" -ForegroundColor Green
Get-ChildItem $target | ForEach-Object {
    $line = "  " + $_.Name + "  (" + $_.Length + " bytes)"
    Write-Host $line
}
Write-Host ""
Write-Host ("Installed version " + $version.Version + ". To go back to the release build:") -ForegroundColor Yellow
Write-Host "  klee-mod\build\deploy.ps1" -ForegroundColor Yellow
