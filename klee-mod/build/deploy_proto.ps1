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

  WHAT IS DIFFERENT FROM deploy.ps1, and it is exactly four things:

    1. `-p:PrototypeCards=true` on the build, which compiles
       Cards/Prototype/** and defines PROTOTYPE_CARDS.
    2. The staged package version carries the +proto build metadata, so a dev
       build is identifiable on sight in the game's own version string.
    3. `tools/gen_prototype_cards.py --check` runs FIRST. The release gate's
       S6a runs the ROSTER codegen staleness check, which cannot see this
       surface -- so without this a dev deploy could ship prototype classes
       that no longer match the sheet, which is the one way this script could
       hand a staged turn a card nobody wrote.
    4. It installs the STS2_MCP bridge as its LAST step, so this machine's
       next launch is parallel-ready (2026-09-02). The reason it belongs here
       and nowhere near deploy.ps1: mods load at BOOT and this script is the
       one moment the game is guaranteed closed (it refuses to run otherwise),
       so it is the only moment the bridge can be put in front of a launch the
       OWNER makes from Steam. Without it, an agent's second instance can only
       ever reach a game the harness launched itself. A dev build is never
       handed to anyone -- that is stated three times below -- so the harness
       riding along with it reaches nobody a prototype class does not. It is a
       WARNING and not a failure if it does not take: the klee package is
       already deployed by then, and the bridge is a harness.

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
    [switch]$AllowIncompleteGameRef,
    # Passed through to validate.ps1 S7 (2026-09-02): run the WHOLE repo
    # suite here, serially, instead of letting a green CI run on this exact
    # commit stand in for it. Off by default because the default was costing
    # 399 s of every dev deploy to re-derive a fact GitHub already held; see
    # klee-mod/build/ci_trust.ps1 for the three conditions a skip needs.
    [switch]$FullGate,
    # THE KLEE OVERHAUL ARM (the ruled brief klee-brief-2026-09-01.md sec.3,
    # slice one klee-overhaul-slice-1-2026-09-01.md). Adds -p:KleeOverhaul=true
    # to the build below, which is the ONLY thing that turns the arm on:
    # without it a dev build compiles the arm's types and never reaches them,
    # and Klee's starter and pool are the Sparks arm's exactly as before. Sim
    # twin: C.KLEE_OVERHAUL, which ships False.
    #
    # A SWITCH HERE AND NOWHERE ELSE, the same arrangement the prototype
    # property has: the release scripts must not be able to name it, and this
    # is the one file the release path never calls.
    [switch]$KleeOverhaul,
    # THE MONDSTADT COMPANION OVERHAUL ARM (the approved workshop
    # companion-workshop-mondstadt-2026-09-01.md sec.3). Adds
    # -p:CompanionOverhaul=true to the build below, which is the ONLY thing
    # that turns the arm on: without it a dev build compiles the arm's types
    # and never reaches them, and the companion reward slot offers the
    # seventeen shipped Mondstadt rows exactly as before. Sim twin:
    # C.COMPANION_OVERHAUL, which ships False.
    #
    # INDEPENDENT OF -KleeOverhaul, and the two are meant to be passed
    # together: that arm replaces Klee's starter and pool, this one replaces
    # Mondstadt's companion pool, and the two sets do not intersect. A dev
    # build that carries both is the supported dev build.
    [switch]$CompanionOverhaul,
    # THE KOKOMI OVERHAUL ARM (the ruled brief kokomi-brief-2026-09-01.md
    # sec.4, slice one kokomi-overhaul-slice-1-2026-09-01.md). Adds
    # -p:KokomiOverhaul=true to the build below, which is the ONLY thing that
    # turns the arm on: without it a dev build compiles the arm's types and
    # never reaches them, and Kokomi's starter, starting relic and pool are the
    # shipped ones exactly as before. Sim twin: C.KOKOMI_OVERHAUL, which ships
    # False.
    #
    # INDEPENDENT OF THE OTHER TWO, and all three are meant to be passed
    # together: the Klee arm replaces Klee's starter and pool, the companion
    # arm replaces Mondstadt's companion pool, this one replaces Kokomi's
    # starter, relic and pool, and the three sets do not intersect. A dev build
    # that carries all three is the supported dev build.
    [switch]$KokomiOverhaul,
    # THE FURINA REFRAME ARM (the countersigned packet
    # review/ruled/furina-reframe-2026-08-29.md, R220 A; R228 option 1 for the
    # Spotlight; the slot-6 ruling for the aimed Evoke). Adds
    # -p:FurinaReframe=true to the build below, which is the ONLY thing that
    # turns the arm on: without it a dev build compiles the arm's types and
    # never reaches them, and Furina's Salon, her Fanfare meter and her
    # Spotlight selector behave exactly as they ship. Sim twin: the five module
    # flags in tier0/engine/furina_reframe.py, which all ship False.
    #
    # INDEPENDENT OF THE OTHER THREE, and all four may be passed together: the
    # Klee arm replaces Klee's starter and pool, the companion arm replaces two
    # nations' companion pools, the Kokomi arm replaces her starter, relic and
    # pool, and this one changes FURINA's engine. The four sets do not
    # intersect.
    [switch]$FurinaReframe
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

$arms = @()
if ($KleeOverhaul) { $arms += 'the Klee overhaul arm' }
if ($CompanionOverhaul) { $arms += 'the Mondstadt companion overhaul arm' }
if ($KokomiOverhaul) { $arms += 'the Kokomi overhaul arm' }
if ($FurinaReframe) { $arms += 'the Furina reframe arm' }
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

Write-Host "Building ($Configuration) WITH the prototype surface$armLabel..." -ForegroundColor Magenta
$buildArgs = @('-p:PrototypeCards=true')
if ($KleeOverhaul) { $buildArgs += '-p:KleeOverhaul=true' }
if ($CompanionOverhaul) { $buildArgs += '-p:CompanionOverhaul=true' }
if ($KokomiOverhaul) { $buildArgs += '-p:KokomiOverhaul=true' }
if ($FurinaReframe) { $buildArgs += '-p:FurinaReframe=true' }
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
Write-Host "*** PROTOTYPE BUILD ***" -ForegroundColor Magenta
Write-Host "  The quarantined prototype surface is COMPILED IN. Off-pool, so" -ForegroundColor Magenta
Write-Host "  ordinary play is unchanged and no reward roll can offer one." -ForegroundColor Magenta
Write-Host "  Reach a row only by id, through the understudy grant tooling." -ForegroundColor Magenta
Write-Host "  DO NOT hand this build to a co-op partner, and run" -ForegroundColor Magenta
Write-Host "  klee-mod\build\deploy.ps1 to put the release build back." -ForegroundColor Magenta
if ($KleeOverhaul) {
    Write-Host ""
    Write-Host "*** KLEE OVERHAUL ARM ON ***" -ForegroundColor Magenta
    Write-Host "  Klee's starter and her WHOLE reward pool are slice one's rows." -ForegroundColor Magenta
    Write-Host "  Her shipped 79 cards cannot be offered while this build is in." -ForegroundColor Magenta
    Write-Host "  Bombs never go off by themselves; only a Set off card pops one." -ForegroundColor Magenta
}
if ($CompanionOverhaul) {
    Write-Host ""
    Write-Host "*** MONDSTADT COMPANION OVERHAUL ARM ON ***" -ForegroundColor Magenta
    Write-Host "  The companion reward slot offers the workshop's rewritten" -ForegroundColor Magenta
    Write-Host "  Mondstadt Universals; the 17 shipped Mondstadt rows cannot" -ForegroundColor Magenta
    Write-Host "  be offered. Inazuma and Fontaine are untouched." -ForegroundColor Magenta
}
Write-Host ""

if ($KokomiOverhaul) {
    Write-Host ""
    Write-Host "*** KOKOMI OVERHAUL ARM ON ***" -ForegroundColor Magenta
    Write-Host "  Kokomi's starter, her starting relic and her WHOLE reward" -ForegroundColor Magenta
    Write-Host "  pool are slice one's rows. Her shipped 76 cards cannot be" -ForegroundColor Magenta
    Write-Host "  offered while this build is in, and the Pearl of Wisdom is" -ForegroundColor Magenta
    Write-Host "  replaced by Tamakushi Casket." -ForegroundColor Magenta
    Write-Host "  The Bake-Kurage is always out and holds Tide; nothing" -ForegroundColor Magenta
    Write-Host "  Exhausts for Charge and the Burst gate does not fill." -ForegroundColor Magenta
}

if ($FurinaReframe) {
    Write-Host ""
    Write-Host "*** FURINA REFRAME ARM ON ***" -ForegroundColor Magenta
    Write-Host "  Salon Members DO NOT auto-play: the turn-start upkeep is" -ForegroundColor Magenta
    Write-Host "  gone. A Companion play makes the front member perform and" -ForegroundColor Magenta
    Write-Host "  rotate; a deploy performs the member it deploys; a deploy" -ForegroundColor Magenta
    Write-Host "  onto a full stage EVOKES the front member." -ForegroundColor Magenta
    Write-Host "  Fanfare is minted ONLY by a member performing -- HP lost," -ForegroundColor Magenta
    Write-Host "  Encore spent, Encore absorbed and Center Stage all pay 0." -ForegroundColor Magenta
    Write-Host "  Center Stage retires; the selector aims Guest Cast for" -ForegroundColor Magenta
    Write-Host "  Encore. Her sheet is UNCHANGED -- this arm is engine only." -ForegroundColor Magenta
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
