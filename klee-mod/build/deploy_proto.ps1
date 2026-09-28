<#
  THE DEV DEPLOY. Build Klee as the release build does, PLUS an arm the
  release must not carry, stamp it +proto, and stage it into the game's mods/
  directory.

  WHAT CHANGED ON 2026-09-28. [USER]'s ruling, in his words: "The current
  character builds are much more progressed than the old prototypes were,
  even though it's still a work in progress. Let's go ahead and make all 3
  current builds the active release builds to avoid this confusion." So the
  DEFAULT build -- klee-mod\build\deploy.ps1, and any build naming no property --
  now compiles the prototype surface and turns on Klee's overhaul, the
  companion overhaul, Kokomi's overhaul and Furina's Stage
  (klee-mod/Directory.Build.props). Those four used to be this script's
  switches; they are gone from it, because the release already carries them.

  WHAT IS LEFT FOR THIS SCRIPT is the one arm the release must not carry:
  -TeyvatFrame, the run frame [USER] put on hold (docs/current/STATE.md). It
  REFUSES to run without it: a +proto package whose contents equal the
  release is the exact confusion the ruling removed. For the ordinary build,
  seats included, run klee-mod\build\deploy.ps1 (or
  tools/deploy_round.py, which adds the bridge).

  WHAT IS DIFFERENT FROM deploy.ps1, and it is exactly four things:

    1. `-p:TeyvatFrame=true` on the build.
    2. The staged package version carries the +proto build metadata, so a dev
       build is identifiable on sight in the game's own version string.
    3. `tools/gen_prototype_cards.py --check` runs FIRST, before anything is
       built. (validate.ps1's S6a runs it too since the ruling; this is the
       earlier, cheaper stop.)
    4. It installs the STS2_MCP bridge as its LAST step, so this machine's
       next launch is parallel-ready (2026-09-02). Mods load at BOOT and this
       script is a moment the game is guaranteed closed (it refuses to run
       otherwise). It is a WARNING and not a failure if it does not take: the
       klee package is already deployed by then, and the bridge is a harness.

  WHAT IS NOT DIFFERENT, deliberately: the gate. validate.ps1 runs whole --
  every S-rule, no rule relaxed and no static-only mode requested. A prototype
  build that skipped gates would prove nothing about the cards it exists to
  try.

  S7's ARM IS THE ONE THING THAT MOVED (2026-09-02), and it moved for both
  paths alike rather than as a dev-build concession. The suite still has to be
  green; what changed is WHERE that is established. When the tree is clean,
  HEAD is on origin/main and GitHub's check runs for that exact sha are green,
  S7 stands on that run and says which one; otherwise it runs the tests here,
  as the fast lane or -- with -FullGate -- the old whole-repo serial suite.
  The three conditions are in klee-mod/build/ci_trust.ps1 and every failure to
  establish one runs the tests.

  RESTORING THE RELEASE BUILD. There is no --restore switch here and there
  should not be, because there is nothing to restore FROM: this script
  overwrites mods\klee, and so does deploy.ps1. The undo is simply

      klee-mod\build\deploy.ps1

  run from the art-bearing main checkout, which rebuilds without the dev arm
  and overwrites mods\klee again. Confirm it took by reading the
  version in game: a release build has no +proto. Do this before any
  measured run, any handoff, and any co-op session.

  NO -Package SWITCH. deploy.ps1 has one; this must not. A handoff zip is a
  build somebody else runs, and co-op is lockstep: a peer on the release
  build has no dev arm.

  NOTE: keep this file pure ASCII (validate.ps1 S8 sweeps every .ps1 in the
  repo). Windows PowerShell 5.1 reads .ps1 as ANSI unless there is a BOM.
#>
[CmdletBinding()]
param(
    [ValidateSet('Debug', 'Release')]
    [string]$Configuration = 'Release',
    # Passed through to validate.ps1 S7, same meaning as on deploy.ps1: an
    # acknowledgement of a stale local game_ref, not a fix.
    [switch]$AllowIncompleteGameRef,
    # Passed through to validate.ps1 S7 (2026-09-02): run the WHOLE repo
    # suite here, serially, instead of letting a green CI run on this exact
    # commit stand in for it. Off by default because the default was costing
    # 399 s of every dev deploy to re-derive a fact GitHub already held; see
    # klee-mod/build/ci_trust.ps1 for the three conditions a skip needs.
    [switch]$FullGate,
    # THE TEYVAT RUN FRAME ARM (R272, the frame packet
    # review/active/teyvat-run-frame-2026-09-14.md sec.4; the spike merged as
    # PR #492). Adds -p:TeyvatFrame=true to the build below, which is the ONLY
    # thing that turns the arm on: without it a dev build compiles the arm's
    # types -- they are compiled in BOTH directions, unlike Cards/Prototype/**,
    # so a pin can say what the act list contains on each side -- and reaches
    # none of them, because every file under KleeCode/Teyvat/** reads
    # TeyvatFrame.Enabled first and ModelDb.Acts keeps its hardcoded four.
    # C# twin: TeyvatFrame.Enabled, which ships false. There is no sim twin:
    # tier0 has no run frame.
    #
    # IT IS THE ONE ARM THAT IS NOT A CHARACTER'S. It dresses the RUN -- act
    # names, monster names, still portraits, music -- and changes no starter,
    # no relic and no pool, so it composes with the four kit arms the default
    # build carries.
    #
    # OFF ON EVERY CALIBRATION DEPLOY (frame packet sec.5): a dressing's event
    # pool differing in LENGTH from the base zone's would move the UpFront rng
    # and with it the Klee calibration seed's whole map. The pools are equal by
    # construction and pinned equal by TeyvatFrameTests; the flag staying off
    # is the second belt.
    [switch]$TeyvatFrame
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

# ONE INSTALL MEANS ONE DEPLOYED BUILD, FOR EVERY LANE. The understudy funnel
# can run a second game out of this same directory (`--lane 1`,
# understudy/instances.py): a separate process, a separate port, a separate
# user tree -- but mods\klee is shared, so there is no such thing as deploying
# to one lane. This check is BY IMAGE NAME on purpose, and must stay that way:
# by pid it would miss the other lane's game, whose held lock on klee.dll is
# exactly the same lock. Every listed pid has to go before a deploy.
$running = Get-Process -Name 'SlayTheSpire2' -ErrorAction SilentlyContinue
if ($running) {
    $ids = $running.Id -join ', '
    throw "Slay the Spire 2 is running (PID $ids). Close EVERY game process before deploying; it holds a lock on klee.dll. One install means one deployed build for all lanes, so a second lane's game (understudy --lane 1) blocks this deploy exactly as the first one does -- tear its lane down (python -m understudy.embark --teardown --lane 1) rather than deploying around it."
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

# NO DEV ARM, NO DEV BUILD (2026-09-28). The four kit arms are the release
# default now, so without -TeyvatFrame this package would equal the release
# one while wearing +proto -- the confusion the ruling removed.
if (-not $TeyvatFrame) {
    throw "deploy_proto.ps1 builds only a build that differs from the release, and every kit arm is the release default since 2026-09-28. Pass -TeyvatFrame, or run klee-mod\build\deploy.ps1 (tools/deploy_round.py adds the bridge)."
}
$arms = @()
if ($TeyvatFrame) { $arms += 'the Teyvat run frame arm' }
$armLabel = if ($arms.Count) { ' AND ' + ($arms -join ' AND ') } else { '' }

# EB-161, on deploy.ps1's terms exactly: computed BEFORE the build because the
# dll is stamped with it. The +proto mark rides AssemblyInformationalVersion,
# which is the whole point of stamping the informational string verbatim -- a
# dev dll pulled out of a crash log says it is a dev dll.
$version = Get-PackageVersion `
    -SourceManifest (Join-Path $packageDir 'manifest.json') `
    -RepoRoot $repoRoot `
    -Prototype
$stamp = Get-AssemblyStamp -Version $version

Write-Host "Building ($Configuration): the release kits$armLabel..." -ForegroundColor Magenta
$buildArgs = @()
if ($TeyvatFrame) { $buildArgs += '-p:TeyvatFrame=true' }
$buildArgs += $stamp.BuildArgs
& dotnet build $csproj -c $Configuration -v minimal --nologo @buildArgs
if ($LASTEXITCODE -ne 0) { throw "Build failed." }

$dll = Join-Path $root "KleeCode\bin\$Configuration\klee.dll"
if (-not (Test-Path $dll)) { throw "Expected output not found: $dll" }

Write-Host "Staging package..." -ForegroundColor Cyan
if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
New-Item -ItemType Directory -Force -Path $stage | Out-Null
Copy-Item (Join-Path $packageDir 'manifest.json') -Destination $stage
Copy-Item $dll -Destination $stage

# MAJOR.AUTO+proto (or +proto.dirty). The source manifest is never written to.
# $version was computed above the build (EB-161) so the dll carries it too.
$stagedManifest = Join-Path $stage 'manifest.json'
$sm = Get-Content $stagedManifest -Raw | ConvertFrom-Json
$sm.version = $version.Version
($sm | ConvertTo-Json -Depth 10) | Set-Content $stagedManifest -Encoding utf8
Write-Host "Stamped package version $($version.Version)" -ForegroundColor Magenta

Write-Host ""
Write-Host "*** DEV BUILD (+proto) ***" -ForegroundColor Magenta
Write-Host "  The release kits plus a dev-only arm. DO NOT hand this build" -ForegroundColor Magenta
Write-Host "  to a co-op partner, and run klee-mod\build\deploy.ps1 to put" -ForegroundColor Magenta
Write-Host "  the release build back." -ForegroundColor Magenta

if ($TeyvatFrame) {
    Write-Host ""
    Write-Host "*** TEYVAT RUN FRAME ARM ON ***" -ForegroundColor Magenta
    Write-Host "  A SPIKE, and it dresses the RUN rather than a character:" -ForegroundColor Magenta
    Write-Host "  no starter, no relic and no pool moves, so this arm" -ForegroundColor Magenta
    Write-Host "  composes with every arm above it." -ForegroundColor Magenta
    Write-Host "  Acts one and two are MONDSTADT and LIYUE, standing at" -ForegroundColor Magenta
    Write-Host "  Overgrowth's and Underdocks' index and returning those" -ForegroundColor Magenta
    Write-Host "  zones' OWN encounters -- the mechanics cannot drift." -ForegroundColor Magenta
    Write-Host "  They wear the base zones' pictures: the asset alias is a" -ForegroundColor Magenta
    Write-Host "  disclosed spike shortcut, so the map screen reads the new" -ForegroundColor Magenta
    Write-Host "  names over Overgrowth's and Underdocks' backgrounds." -ForegroundColor Magenta
    Write-Host "  Nibbit reads as the Wooden Shield Hilichurl Guard in" -ForegroundColor Magenta
    Write-Host "  Mondstadt only, and draws a still portrait there if" -ForegroundColor Magenta
    Write-Host "  res://teyvat/ carries one; music is local placeholders." -ForegroundColor Magenta
    Write-Host "  NEVER PASS IT ON A CALIBRATION DEPLOY: an act's event pool" -ForegroundColor Magenta
    Write-Host "  length moves the UpFront rng and with it the Klee seed's" -ForegroundColor Magenta
    Write-Host "  whole map (frame packet sec.5)." -ForegroundColor Magenta
}

if ($version.IsDirty) {
    Write-Host "*** DIRTY WORKING TREE ***" -ForegroundColor Red
    Write-Host ("  $($version.DirtyFiles.Count) uncommitted change(s) to TRACKED files; version stamped +proto.dirty.") -ForegroundColor Red
    foreach ($f in ($version.DirtyFiles | Select-Object -First 10)) {
        Write-Host "    $f" -ForegroundColor DarkYellow
    }
    if ($version.DirtyFiles.Count -gt 10) {
        Write-Host ("    ... and " + ($version.DirtyFiles.Count - 10) + " more") -ForegroundColor DarkYellow
    }
    Write-Host ""
}

# Untracked files are NOT dirt (2026-09-02; see Get-AutoVersion). Until then
# this machine's seat logs and capture packets made EVERY dev package
# "+proto.dirty" from a clean main, which is exactly as informative as no mark
# at all. One grey line, because an untracked .cs under KleeCode/ is compiled
# by the csproj's default glob and so can move this build without moving the
# mark.
if ($version.UntrackedFiles.Count -gt 0) {
    Write-Host ("note: $($version.UntrackedFiles.Count) untracked file(s) in the tree; they do not affect the version stamp.") -ForegroundColor DarkGray
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
    -FullGate:$FullGate `
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

# THE FOURTH DIFFERENCE (2026-09-02). Install the harness bridge too, so the
# next launch out of this install is parallel-ready: mods load at BOOT, and
# this is the one moment the game is guaranteed closed, so it is the only
# moment the bridge can be put in front of a launch the OWNER makes from
# Steam. With it there, the owner's game answers on 15526 and an agent's
# second instance takes 15527 (understudy --lane 1); without it, an agent can
# only ever drive a game the harness launched itself.
#
# A WARNING RATHER THAN A FAILURE. The klee package is deployed by the line
# above and the deploy has already succeeded; the bridge is a harness, and a
# vendor-pin drift or a missing dotnet is a thing to be told about, not a
# reason to report the mod deploy as failed. Removed by hand with
# `.\build\deploy_bridge.ps1 -Remove` if it is ever in the way.
Write-Host ""
Write-Host "Installing the STS2_MCP bridge (parallel-ready launch)..." -ForegroundColor Cyan
try {
    & (Join-Path $PSScriptRoot 'deploy_bridge.ps1') -Configuration $Configuration
} catch {
    Write-Host ("WARNING: the bridge install did not take: " + $_.Exception.Message) -ForegroundColor Yellow
    Write-Host "  The klee package IS deployed. Install the harness by hand with:" -ForegroundColor Yellow
    Write-Host "  klee-mod\build\deploy_bridge.ps1" -ForegroundColor Yellow
}
