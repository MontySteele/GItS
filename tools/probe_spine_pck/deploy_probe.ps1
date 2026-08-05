<#
  Track M spine probe, phase 2: put the throwaway probe mod in front of the
  game. RUN ONLY WHEN THE GAME WINDOW IS YOURS.

  This is the only step in the whole probe that writes anything into the game
  directory, and it writes exactly one new folder: <GameDir>\mods\spineprobe.
  Nothing existing is edited, moved, or overwritten. cleanup_probe.ps1 deletes
  that folder and re-checks the reversibility list.

  Reversibility baseline (Track C discipline) is captured BEFORE the copy, to
  <StateFile>, so cleanup can prove restoration rather than assert it:
    - the mods\ directory listing
    - user settings.save last-write time (both the default\1 profile and the
      steam\<id> profiles -- runs park under steam\...\profileN\saves, which is
      NOT where "default\1" would lead you to look)
    - the save directories, so "no run left behind" is checked where runs
      actually live
    - sha256 of every file in the install root

  steam_appid.txt: it does NOT ship with the game. The correct end state is
  ABSENT, and this script never creates one -- launch through Steam
  (steam://rungameid/2868840) instead. If one is present at baseline it is a
  leak from some other session; that is recorded here and removed by cleanup.

  NOTE: pure ASCII. Windows PowerShell 5.1 reads .ps1 as ANSI without a BOM.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$ProjectDir,
    [string]$GameDir,
    [string]$StateFile
)

$ErrorActionPreference = 'Stop'

$here = $PSScriptRoot
$repo = Split-Path -Parent (Split-Path -Parent $here)

if (-not $GameDir) {
    $localProps = Join-Path $repo 'klee-mod\local.props'
    if (-not (Test-Path $localProps)) { throw "No -GameDir and no klee-mod\local.props to read it from." }
    $GameDir = ([xml](Get-Content $localProps)).Project.PropertyGroup.GameDir
}
if (-not (Test-Path $GameDir)) { throw "GameDir does not exist: $GameDir" }
if (-not $StateFile) { $StateFile = Join-Path $ProjectDir 'gamedir_baseline.json' }

$running = Get-Process -Name 'SlayTheSpire2' -ErrorAction SilentlyContinue
if ($running) { throw "Slay the Spire 2 is running (PID $($running.Id -join ', ')). Close it first." }

$modsDir  = Join-Path $GameDir 'mods'
$probeDir = Join-Path $modsDir 'spineprobe'
if (Test-Path $probeDir) { throw "$probeDir already exists -- run cleanup_probe.ps1 before redeploying." }

Write-Host "== capturing reversibility baseline ==" -ForegroundColor Cyan
$userDir  = Join-Path $env:APPDATA 'SlayTheSpire2'
$settings = Join-Path $userDir 'default\1\settings.save'
$appId    = Join-Path $GameDir 'steam_appid.txt'

if (Test-Path $appId) {
    Write-Host "LEAK: steam_appid.txt is present at baseline. It does not ship with the game;" -ForegroundColor Yellow
    Write-Host "      some other session left it. cleanup_probe.ps1 will remove it." -ForegroundColor Yellow
}

# Runs park under steam\<id>\profileN\saves, not default\1. Check every saves
# directory that exists, or "no run left behind" checks the wrong folder.
$saveFiles = @(Get-ChildItem $userDir -Recurse -File -Filter '*.save' -ErrorAction SilentlyContinue |
    ForEach-Object {
        [ordered]@{
            path  = $_.FullName.Substring($userDir.Length + 1)
            mtime = $_.LastWriteTimeUtc.ToString('o')
            size  = $_.Length
        }
    } | Sort-Object { $_.path })

$baseline = [ordered]@{
    gameDir        = $GameDir
    userDir        = $userDir
    capturedUtc    = (Get-Date).ToUniversalTime().ToString('o')
    mods           = @(Get-ChildItem $modsDir -Directory | ForEach-Object { $_.Name } | Sort-Object)
    settingsExists = (Test-Path $settings)
    settingsMtime  = if (Test-Path $settings) { (Get-Item $settings).LastWriteTimeUtc.ToString('o') } else { $null }
    appIdExistsAtBaseline = (Test-Path $appId)
    saveFiles      = $saveFiles
    installRoot    = @(Get-ChildItem $GameDir -File | ForEach-Object {
                          [ordered]@{ name = $_.Name; sha256 = (Get-FileHash $_.FullName -Algorithm SHA256).Hash }
                      })
}
($baseline | ConvertTo-Json -Depth 6) | Set-Content $StateFile -Encoding utf8
Write-Host "Baseline written to $StateFile" -ForegroundColor Green

Write-Host "== staging probe mod ==" -ForegroundColor Cyan
$dll  = Join-Path $here 'SpineProbe\bin\Release\spineprobe.dll'
$pck  = Join-Path $ProjectDir 'probe_wide.pck'
$man  = Join-Path $here 'SpineProbe\manifest.json'
foreach ($p in $dll, $pck, $man) { if (-not (Test-Path $p)) { throw "Missing probe artefact: $p" } }

New-Item -ItemType Directory -Force -Path $probeDir | Out-Null
Copy-Item $man -Destination $probeDir
Copy-Item $dll -Destination $probeDir
Copy-Item $pck -Destination (Join-Path $probeDir 'spineprobe.pck')

Write-Host "Deployed to $probeDir :" -ForegroundColor Green
Get-ChildItem $probeDir | ForEach-Object { Write-Host "  $($_.Name)  $($_.Length) bytes" }
Write-Host ""
Write-Host "Now launch through STEAM, never by running the exe directly:" -ForegroundColor Yellow
Write-Host "  start steam://rungameid/2868840" -ForegroundColor Yellow
Write-Host "Running SlayTheSpire2.exe directly makes it write steam_appid.txt into the" -ForegroundColor Yellow
Write-Host "install root, which is a footprint the Steam launch does not leave." -ForegroundColor Yellow
Write-Host "Reach the main menu, quit, then read" -ForegroundColor Yellow
Write-Host "  $env:APPDATA\SlayTheSpire2\logs\godot.log" -ForegroundColor Yellow
Write-Host "for lines tagged [spineprobe]. Then run cleanup_probe.ps1." -ForegroundColor Yellow
