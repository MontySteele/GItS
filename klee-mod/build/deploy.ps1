<#
  Build Klee and deploy it into the game's mods/ directory.

  IMPORTANT (spec C1, blocker found 2026-07-19): the game's ModManager walks
  mods/ RECURSIVELY and tries to parse every *.json it finds as a mod manifest.
  If build output (bin/, obj/) ends up under mods/, it picks up deps.json and
  project.assets.json, logs errors, and throws JsonException on every boot.

  So we never build in place. We stage a clean package (manifest + dll only)
  and copy exactly that.

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
    [switch]$Package
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
    -SourceManifest (Join-Path $packageDir 'manifest.json') -RepoRoot $repoRoot
$stamp = Get-AssemblyStamp -Version $version

Write-Host "Building ($Configuration)..." -ForegroundColor Cyan
& dotnet build $csproj -c $Configuration -v minimal --nologo @($stamp.BuildArgs)
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
# by sheet id. The pipeline keeps each character's cards and the companion cards
# in separate source dirs, so all of them are staged into that one flat
# destination. Ids are unique across the sheets (tools/lint_unique_names.py
# gates that), so nothing collides.
#
# EVERY ROSTER CHARACTER MUST BE LISTED HERE. A character missing from this
# array does not fail anything -- the build is green, validate is green, and
# the mod loads -- their cards simply render with no portrait. Kokomi shipped
# that way for one day (2026-07-25): 58 painted faces sat in ImageGen and none
# of them reached the game.
$artSrcDirs = @(
    (Join-Path (Split-Path -Parent $root) 'ImageGen\images\cards\klee'),
    (Join-Path (Split-Path -Parent $root) 'ImageGen\images\cards\furina'),
    (Join-Path (Split-Path -Parent $root) 'ImageGen\images\cards\kokomi'),
    (Join-Path (Split-Path -Parent $root) 'ImageGen\images\cards\companions')
)
$artDst = Join-Path $stage 'images\cards'
$foundAny = $false
foreach ($artSrc in $artSrcDirs) {
    if (Test-Path $artSrc) {
        New-Item -ItemType Directory -Force -Path $artDst | Out-Null
        Copy-Item (Join-Path $artSrc '*.png') -Destination $artDst
        $foundAny = $true
    } else {
        Write-Host "WARNING: no card art at $artSrc" -ForegroundColor Yellow
    }
}
if ($foundAny) {
    $artCount = (Get-ChildItem $artDst -Filter *.png).Count
    Write-Host "Staged $artCount card images" -ForegroundColor Cyan
} else {
    Write-Host "WARNING: no card art found (cards will fall back to BETA placeholder)" -ForegroundColor Yellow
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
    -FullGate:$FullGate

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
