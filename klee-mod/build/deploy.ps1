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
    # Also zip the validated stage into dist\klee-v<version>.zip for handoff.
    # The zip is the EXACT package that deploys locally (same validate gates),
    # including all card art and the pck -- recipients extract it into the
    # game's mods\ folder and additionally need BaseLib from the Workshop.
    # dist\ and *.zip are both gitignored; hand the zip off privately (it
    # carries Tier F art that must not be publicly distributed).
    [switch]$Package
)

$ErrorActionPreference = 'Stop'

$root       = Split-Path -Parent $PSScriptRoot
$csproj     = Join-Path $root 'KleeCode\KleeCode.csproj'
$package    = Join-Path $root 'Klee'
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

Write-Host "Building ($Configuration)..." -ForegroundColor Cyan
& dotnet build $csproj -c $Configuration -v minimal --nologo
if ($LASTEXITCODE -ne 0) { throw "Build failed." }

$dll = Join-Path $root "KleeCode\bin\$Configuration\klee.dll"
if (-not (Test-Path $dll)) { throw "Expected output not found: $dll" }

Write-Host "Staging package..." -ForegroundColor Cyan
if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
New-Item -ItemType Directory -Force -Path $stage | Out-Null
Copy-Item (Join-Path $package 'manifest.json') -Destination $stage
Copy-Item $dll -Destination $stage

# Card art ships as loose PNGs next to the dll -- no .pck needed, because
# BaseLib's CustomPortrait accepts a Texture2D object we build at runtime.
# Source of truth is the art pipeline's output dir, which is gitignored.
# RosterArt.CardPortrait looks up images/cards/<cardId>.png -- one FLAT dir keyed
# by sheet id. The pipeline keeps Klee cards and companion cards in separate
# source dirs, so both are staged into that one flat destination. Ids are unique
# across the two sheets, so nothing collides.
$artSrcDirs = @(
    (Join-Path (Split-Path -Parent $root) 'ImageGen\images\cards\klee'),
    (Join-Path (Split-Path -Parent $root) 'ImageGen\images\cards\furina'),
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
    -AllowIncompleteGameRef:$AllowIncompleteGameRef

if ($Package) {
    # Read the version from the STAGED manifest so the zip name can never
    # disagree with what is inside it. Co-op is lockstep: peers on different
    # mod builds desync, so every handoff needs a distinct version stamp.
    $manifest = Get-Content (Join-Path $stage 'manifest.json') -Raw | ConvertFrom-Json
    if ([string]::IsNullOrWhiteSpace($manifest.version)) {
        throw "manifest.json has no version; refusing to build an unstamped handoff zip."
    }
    $zip = Join-Path $root ("dist\klee-v" + $manifest.version + ".zip")
    if (Test-Path $zip) { Remove-Item $zip -Force }

    Write-Host "Packaging $zip" -ForegroundColor Cyan
    # -Path on the stage DIRECTORY keeps klee\ as the archive root, so
    # extracting into mods\ lands as mods\klee\.
    Compress-Archive -Path $stage -DestinationPath $zip -CompressionLevel Optimal

    $mb = [math]::Round((Get-Item $zip).Length / 1MB, 1)
    Write-Host "Packaged $zip ($mb MB)" -ForegroundColor Green
    $dep = $manifest.dependencies | Where-Object { $_.id -eq 'BaseLib' }
    Write-Host "Handoff notes: extract into '<game>\mods\' (lands as mods\klee\)." -ForegroundColor Yellow
    Write-Host ("  Recipients also need BaseLib >= " + $dep.min_version + " (Steam Workshop) and game >= " + $manifest.min_game_version + ".") -ForegroundColor Yellow
    Write-Host "  Co-op peers must all run THIS zip -- bump manifest version before each handoff." -ForegroundColor Yellow
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
