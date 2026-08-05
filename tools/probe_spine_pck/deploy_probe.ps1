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
    - user settings.save last-write time
    - presence/last-write of steam_appid.txt (it SHIPS with the game, so the
      rule is "no NEW one", not "none")
    - sha256 of every file in the install root

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
$settings = Join-Path $env:APPDATA 'SlayTheSpire2\default\1\settings.save'
$appId    = Join-Path $GameDir 'steam_appid.txt'
$baseline = [ordered]@{
    gameDir        = $GameDir
    capturedUtc    = (Get-Date).ToUniversalTime().ToString('o')
    mods           = @(Get-ChildItem $modsDir -Directory | ForEach-Object { $_.Name } | Sort-Object)
    settingsExists = (Test-Path $settings)
    settingsMtime  = if (Test-Path $settings) { (Get-Item $settings).LastWriteTimeUtc.ToString('o') } else { $null }
    appIdExists    = (Test-Path $appId)
    appIdMtime     = if (Test-Path $appId) { (Get-Item $appId).LastWriteTimeUtc.ToString('o') } else { $null }
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
Write-Host "Now: launch the game, reach the main menu, quit, then read" -ForegroundColor Yellow
Write-Host "  $env:APPDATA\SlayTheSpire2\logs\godot.log" -ForegroundColor Yellow
Write-Host "for lines tagged [spineprobe]. Then run cleanup_probe.ps1." -ForegroundColor Yellow
