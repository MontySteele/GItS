<#
  Build Klee and deploy it into the game's mods/ directory.

  IMPORTANT (spec C1, blocker found 2026-07-19): the game's ModManager walks
  mods/ RECURSIVELY and tries to parse every *.json it finds as a mod manifest.
  If build output (bin/, obj/) ends up under mods/, it picks up deps.json and
  project.assets.json, logs errors, and throws JsonException on every boot.

  So we never build in place. We stage a clean package (manifest + dll only)
  and copy exactly that.

  WHAT IT BUILDS, SINCE 2026-09-28: THE CURRENT KITS. [USER]'s ruling, in his
  words: "The current character builds are much more progressed than the old
  prototypes were, even though it's still a work in progress. Let's go ahead
  and make all 3 current builds the active release builds to avoid this
  confusion." klee-mod/Directory.Build.props turns the prototype surface and
  the four kit arms (Klee's overhaul, the companion overhaul, Kokomi's
  overhaul, Furina's Stage) on in every build that names no property, so this
  script names none and ships them, unmarked, in the local deploy and in the
  -Package handoff zip alike. The Teyvat frame stays off (on hold); only
  deploy_proto.ps1 -TeyvatFrame builds it, stamped +proto. A seat round wants
  the bridge too: tools/deploy_round.py runs this script and then
  deploy_bridge.ps1.

  NOTE: keep this file pure ASCII. Windows PowerShell 5.1 reads .ps1 as ANSI
  unless there's a BOM, so smart quotes / em-dashes / section signs get mangled
  and break the parser.
#>
[CmdletBinding()]
param(
    [ValidateSet('Debug', 'Release')]
    [string]$Configuration = 'Release',
    # Passed through to validate.ps1 S7: allow deploying when game_ref/
    # exists but is incomplete (falls back to committed-only with a loud
    # banner instead of failing validation).
    [switch]$AllowIncompleteGameRef,
    # Passed through to validate.ps1 S7 (2026-09-02): run the WHOLE repo
    # suite here, serially, instead of letting a green CI run on this exact
    # commit stand in for it. See klee-mod/build/ci_trust.ps1.
    [switch]$FullGate,
    # Also zip the validated stage into dist\klee-v<version>.zip for handoff.
    # The zip is the EXACT package that deploys locally (same validate gates),
    # including all card art and the pck -- recipients extract it into the
    # game's mods\ folder and additionally need BaseLib from the Workshop.
    # dist\ and *.zip are both gitignored; hand the zip off privately (it
    # carries Tier F art that must not be publicly distributed).
    [switch]$Package,
    # 2026-10-05. Stamp the package +next: a STAGING build of a `<kit>-next`
    # branch, the release deploy otherwise unchanged. Driven by
    # tools/deploy_round.py --staging, which checks the branch first.
    [ValidateSet('', 'next')][string]$Stamp = ''
)

$ErrorActionPreference = 'Stop'

# R70 manifest version policy (MAJOR.AUTO, shape amended by R214). Shared with validate.ps1 so the
# deploy-time stamp and the gate that checks it cannot compute it differently.
. (Join-Path $PSScriptRoot 'version.ps1')

$root       = Split-Path -Parent $PSScriptRoot
$repoRoot   = Split-Path -Parent $root
$csproj     = Join-Path $root 'KleeCode\KleeCode.csproj'
$packageDir = Join-Path $root 'Klee'   # NOT $package: collides with the -Package switch
$stage      = Join-Path $root 'dist\klee'
$localProps = Join-Path $root 'local.props'
$venvPython = Join-Path $repoRoot '.venv\Scripts\python.exe'

function Invoke-RepoPython {
    <#
      The repo's own interpreter, with PYTHONPATH pinned to the repo root, in
      deploy_proto.ps1's shape (tier0/tests/test_repo_python_convention).
      EAP is lowered around the call and restored in `finally`: in PS 5.1 a
      native command's stderr under EAP=Stop raises NativeCommandError even
      on exit code 0.
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
    throw "local.props not found. Copy local.props.example to local.props and set GameDir."
}

# Pull GameDir back out of local.props so the script and the build agree.
$gameDir = ([xml](Get-Content $localProps)).Project.PropertyGroup.GameDir
if ([string]::IsNullOrWhiteSpace($gameDir)) { throw "GameDir is empty in local.props." }
if (-not (Test-Path $gameDir)) { throw "GameDir does not exist: $gameDir" }

# The game holds an open handle on klee.dll while running, so deploying over a
# live session fails with an opaque "Access to the path is denied". Check first.
# With -Package the zip build itself is safe while the game runs, so only the
# local deploy step is skipped (loudly, below) instead of failing fast here.
$running = Get-Process -Name 'SlayTheSpire2' -ErrorAction SilentlyContinue
if ($running -and -not $Package) {
    $ids = $running.Id -join ', '
    throw "Slay the Spire 2 is running (PID $ids). Close the game before deploying; it holds a lock on klee.dll."
}

# EB-161. THE VERSION IS COMPUTED BEFORE THE BUILD, not after it, because the
# dll is stamped WITH it: MAJOR.AUTO into AssemblyVersion/FileVersion and the
# whole string into AssemblyInformationalVersion, so the one artifact a crash
# log names carries the build it came from. It used to read 1.0.0.0 on every
# build ever made. Get-PackageVersion depends on nothing the build produces --
# a manifest and a commit count -- so hoisting it is free, and computing it
# once is what makes the dll and manifest.json unable to disagree.
$version = Get-PackageVersion `
    -SourceManifest (Join-Path $packageDir 'manifest.json') -RepoRoot $repoRoot `
    -Stamp $Stamp
$asmStamp = Get-AssemblyStamp -Version $version

Write-Host "Building ($Configuration): the current kits (Klee overhaul, companion overhaul, Kokomi overhaul, Furina Stage)..." -ForegroundColor Cyan
& dotnet build $csproj -c $Configuration -v minimal --nologo @($asmStamp.BuildArgs)
if ($LASTEXITCODE -ne 0) { throw "Build failed." }

$dll = Join-Path $root "KleeCode\bin\$Configuration\klee.dll"
if (-not (Test-Path $dll)) { throw "Expected output not found: $dll" }

Write-Host "Staging package..." -ForegroundColor Cyan
if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
New-Item -ItemType Directory -Force -Path $stage | Out-Null
Copy-Item (Join-Path $packageDir 'manifest.json') -Destination $stage
Copy-Item $dll -Destination $stage

# R70: stamp MAJOR.AUTO into the STAGED manifest. MAJOR is the deliberate half
# and stays exactly as committed; AUTO is the commit count, generated here.
# The source manifest is never written to -- it is a ratified artifact.
# $version was computed above the build (EB-161) so the dll carries it too.
$stagedManifest = Join-Path $stage 'manifest.json'
$sm = Get-Content $stagedManifest -Raw | ConvertFrom-Json
$sm.version = $version.Version
# -Depth matters: the default of 2 flattens the dependencies array into type
# names and would ship a manifest whose BaseLib dependency reads as a string.
($sm | ConvertTo-Json -Depth 10) | Set-Content $stagedManifest -Encoding utf8
Write-Host "Stamped package version $($version.Version)" -ForegroundColor Cyan

if ($version.IsDirty) {
    # Loud, and deliberately not fatal: building from a dirty tree is a normal
    # part of iterating locally. What must never happen is that build reaching
    # a co-op partner, because the commit count no longer identifies its
    # contents -- two "+dirty" zips can share a name and differ.
    Write-Host ""
    Write-Host "*** DIRTY WORKING TREE ***" -ForegroundColor Red
    Write-Host ("  $($version.DirtyFiles.Count) uncommitted change(s) to TRACKED files; version stamped +dirty.") -ForegroundColor Red
    Write-Host "  DO NOT hand this build to a co-op partner. Commit first, then rebuild." -ForegroundColor Red
    foreach ($f in ($version.DirtyFiles | Select-Object -First 10)) {
        Write-Host "    $f" -ForegroundColor DarkYellow
    }
    if ($version.DirtyFiles.Count -gt 10) {
        Write-Host ("    ... and " + ($version.DirtyFiles.Count - 10) + " more") -ForegroundColor DarkYellow
    }
    Write-Host ""
}

# Untracked files are NOT dirt (2026-09-02; see Get-AutoVersion). They are
# still worth one line, because an untracked .cs under KleeCode/ is compiled
# by the csproj's default glob and so can change this build without moving the
# mark above.
if ($version.UntrackedFiles.Count -gt 0) {
    Write-Host ("note: $($version.UntrackedFiles.Count) untracked file(s) in the tree; they do not affect the version stamp.") -ForegroundColor DarkGray
}

# Card art ships as loose PNGs next to the dll -- no .pck needed, because
# BaseLib's CustomPortrait accepts a Texture2D object we build at runtime.
# Source of truth is the art pipeline's output dir, which is gitignored.
# RosterArt.CardPortrait looks up images/cards/<cardId>.png -- one FLAT dir keyed
# by card id, so every character's dir and the companions dir land in it.
#
# ONLY THE SHIPPED SET IS STAGED (2026-10-02). ImageGen keeps the paintings of
# cut cards and of the deleted old kits on purpose, and copying every png in
# the card dirs shipped 743 images where 433 can be drawn (~71 MB of dead
# art). tools/shipped_card_art.py is the one list: every literal
# RosterArt.CardPortrait key in the mod source, widened by every live
# prototype-surface id and art_of target. It reads EVERY dir under
# ImageGen\images\cards (klee, furina, kokomi, varka, companions today) off
# disk rather than a closed list here: Kokomi's art missed the stage for a
# day (2026-07-25) because a character was left off this script's list.
# Dry run, listing what is left behind:
#     .venv\Scripts\python.exe tools\shipped_card_art.py
# validate.ps1 S9 then holds the stage to exactly that set.
$artRoot = Join-Path $repoRoot 'ImageGen\images\cards'
$artDst = Join-Path $stage 'images\cards'
if (Test-Path $artRoot) {
    if (-not (Test-Path $venvPython)) {
        throw "repo venv python not found at $venvPython; cannot stage card art."
    }
    $artOut = Invoke-RepoPython 'tools\shipped_card_art.py' '--images-root' $artRoot '--stage' $artDst
    if ($LASTEXITCODE -ne 0) {
        $artOut | ForEach-Object { Write-Host $_ }
        throw "tools/shipped_card_art.py --stage failed (exit $LASTEXITCODE)."
    }
    $artOut | ForEach-Object { Write-Host $_ -ForegroundColor Cyan }
} else {
    Write-Host "WARNING: no card art at $artRoot (cards will render the blank portrait)" -ForegroundColor Yellow
}

# The pck carries the res://-bound art (select screen, top-panel icon, map
# marker, power/relic icons). It is built locally by tools\build_pck.ps1 --
# *.pck is gitignored (public repo, Tier F art) -- and the manifest declares
# has_pck, so validate.ps1's S2 rule fails the deploy if it is missing rather
# than shipping a manifest that lies to ModManager.
$pck = Join-Path $root 'assets\klee.pck'
$pckContract = "$pck.contract.txt"
if (Test-Path $pck) {
    Copy-Item $pck -Destination $stage
    Write-Host "Staged klee.pck ($((Get-Item $pck).Length) bytes)" -ForegroundColor Cyan
    if (Test-Path $pckContract) {
        Copy-Item $pckContract -Destination $stage
    } else {
        Write-Host "WARNING: no PCK contract at $pckContract; rebuild with tools\build_pck.ps1." -ForegroundColor Yellow
    }
} else {
    Write-Host "WARNING: no klee.pck at $pck; run tools\build_pck.ps1 first (validate will fail below)." -ForegroundColor Yellow
}

# Gate the deploy on the static checks. These run against the STAGED package,
# so they see exactly what the game will see -- including any stray *.json that
# would break ModManager's recursive scan.
Write-Host "Validating package..." -ForegroundColor Cyan
& (Join-Path $PSScriptRoot 'validate.ps1') `
    -StageDir $stage `
    -SourceDir (Join-Path $root 'KleeCode') `
    -GameDir $gameDir `
    -AllowIncompleteGameRef:$AllowIncompleteGameRef `
    -FullGate:$FullGate `
    -Stamp $Stamp

if ($Package) {
    # Read the version from the STAGED manifest so the zip name can never
    # disagree with what is inside it. Co-op is lockstep: peers on different
    # mod builds desync, so every handoff needs a distinct version stamp.
    $manifest = Get-Content (Join-Path $stage 'manifest.json') -Raw | ConvertFrom-Json
    if ([string]::IsNullOrWhiteSpace($manifest.version)) {
        throw "manifest.json has no version; refusing to build an unstamped handoff zip."
    }
    $zip = Join-Path $root ("dist\klee-v" + $manifest.version + ".zip")

    # R70: REFUSE to overwrite. Deploy used to Remove-Item this silently, and
    # with a version that had not moved in 134 commits that meant every zip
    # quietly replaced a different build wearing the same name.
    #
    # With AUTO in the name this can only fire on a same-commit rebuild --
    # which is exactly the case where two zips can share a name and differ
    # (uncommitted changes), so refusing is correct rather than inconvenient.
    # Commit, or delete the old zip on purpose.
    if (Test-Path $zip) {
        throw ("refusing to overwrite an existing handoff zip: $zip`n" +
               "  Same commit, same name, possibly different contents -- which is the " +
               "desync this version scheme exists to prevent.`n" +
               "  Commit your changes (AUTO advances), or delete that zip deliberately.")
    }

    Write-Host "Packaging $zip" -ForegroundColor Cyan
    # -Path on the stage DIRECTORY keeps klee\ as the archive root, so
    # extracting into mods\ lands as mods\klee\.
    Compress-Archive -Path $stage -DestinationPath $zip -CompressionLevel Optimal

    $mb = [math]::Round((Get-Item $zip).Length / 1MB, 1)
    Write-Host "Packaged $zip ($mb MB)" -ForegroundColor Green
    $dep = $manifest.dependencies | Where-Object { $_.id -eq 'BaseLib' }
    Write-Host "Handoff notes: extract into '<game>\mods\' (lands as mods\klee\)." -ForegroundColor Yellow
    Write-Host ("  Recipients also need BaseLib >= " + $dep.min_version + " (Steam Workshop) and game >= " + $manifest.min_game_version + ".") -ForegroundColor Yellow
    # R70: "bump the version before each handoff" is no longer a discipline
    # anyone has to remember -- AUTO advances with every commit. What the
    # recipient needs is the identity, and whether it is trustworthy.
    Write-Host ("  Co-op peers must all run THIS build: version " + $manifest.version + ".") -ForegroundColor Yellow
    Write-Host "  Versions compare: the higher AUTO (the patch component) is the newer build." -ForegroundColor Yellow
    if ($version.IsDirty) {
        Write-Host "  *** +dirty: built from uncommitted changes. NOT for handoff. ***" -ForegroundColor Red
    }
}

if ($running) {
    $ids = $running.Id -join ', '
    Write-Host "SKIPPED local deploy: Slay the Spire 2 is running (PID $ids) and holds a lock on klee.dll." -ForegroundColor Yellow
    Write-Host "The zip above is built from the validated stage; re-run without -Package after closing the game to deploy locally." -ForegroundColor Yellow
    return
}

$target = Join-Path $gameDir 'mods\klee'
Write-Host "Deploying to $target" -ForegroundColor Cyan
if (Test-Path $target) { Remove-Item $target -Recurse -Force }
New-Item -ItemType Directory -Force -Path $target | Out-Null
Copy-Item "$stage\*" -Destination $target -Recurse

Write-Host "Deployed:" -ForegroundColor Green
Get-ChildItem $target | ForEach-Object {
    $line = "  " + $_.Name + "  (" + $_.Length + " bytes)"
    Write-Host $line
}
