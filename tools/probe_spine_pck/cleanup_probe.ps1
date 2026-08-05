<#
  Track M spine probe: undo. Removes <GameDir>\mods\spineprobe and the local
  scratch project, then checks the reversibility list against the baseline
  deploy_probe.ps1 captured -- and SAYS what it found rather than assuming.

  Checked, in the Track C form:
    1. mods\ directory listing is back to the baseline set
    2. no spineprobe folder remains
    3. user settings.save mtime unchanged (the game rewrites it on quit; a
       change is REPORTED, not treated as failure -- launching the game is
       what the probe asked for)
    4. steam_appid.txt is exactly as it was (it ships with the game; the rule
       is that the probe leaves no NEW one and does not touch the existing)
    5. every file in the install root still hashes to its baseline value
    6. no leftover run: the probe never starts one, so this is a listing check

  NOTE: pure ASCII. Windows PowerShell 5.1 reads .ps1 as ANSI without a BOM.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$ProjectDir,
    [string]$StateFile,
    [switch]$KeepScratch
)

$ErrorActionPreference = 'Stop'

if (-not $StateFile) { $StateFile = Join-Path $ProjectDir 'gamedir_baseline.json' }
if (-not (Test-Path $StateFile)) { throw "No baseline at $StateFile -- deploy_probe.ps1 writes it." }
$baseline = Get-Content $StateFile -Raw | ConvertFrom-Json

$running = Get-Process -Name 'SlayTheSpire2' -ErrorAction SilentlyContinue
if ($running) { throw "Slay the Spire 2 is running (PID $($running.Id -join ', ')). Close it first." }

$GameDir  = $baseline.gameDir
$modsDir  = Join-Path $GameDir 'mods'
$probeDir = Join-Path $modsDir 'spineprobe'

if (Test-Path $probeDir) {
    Remove-Item $probeDir -Recurse -Force
    Write-Host "Removed $probeDir" -ForegroundColor Green
} else {
    Write-Host "No $probeDir to remove." -ForegroundColor DarkGray
}

$fail = @()
$note = @()

$nowMods = @(Get-ChildItem $modsDir -Directory | ForEach-Object { $_.Name } | Sort-Object)
$wasMods = @($baseline.mods)
if (($nowMods -join '|') -ne ($wasMods -join '|')) {
    $fail += "mods list differs: was [$($wasMods -join ', ')], now [$($nowMods -join ', ')]"
} else {
    Write-Host "OK  mods list unchanged: $($nowMods -join ', ')" -ForegroundColor Green
}

$settings = Join-Path $env:APPDATA 'SlayTheSpire2\default\1\settings.save'
$nowSettings = if (Test-Path $settings) { (Get-Item $settings).LastWriteTimeUtc.ToString('o') } else { $null }
if ($nowSettings -ne $baseline.settingsMtime) {
    $note += "settings.save mtime moved ($($baseline.settingsMtime) -> $nowSettings). Expected if the game was launched; it is user state, not install state."
} else {
    Write-Host "OK  settings.save mtime unchanged" -ForegroundColor Green
}

$appId = Join-Path $GameDir 'steam_appid.txt'
$nowAppIdExists = Test-Path $appId
$nowAppIdMtime  = if ($nowAppIdExists) { (Get-Item $appId).LastWriteTimeUtc.ToString('o') } else { $null }
if ($nowAppIdExists -ne $baseline.appIdExists -or $nowAppIdMtime -ne $baseline.appIdMtime) {
    $fail += "steam_appid.txt changed (exists $($baseline.appIdExists)->$nowAppIdExists, mtime $($baseline.appIdMtime)->$nowAppIdMtime)"
} else {
    Write-Host "OK  steam_appid.txt untouched (shipped with the game, still as found)" -ForegroundColor Green
}

foreach ($f in $baseline.installRoot) {
    $p = Join-Path $GameDir $f.name
    if (-not (Test-Path $p)) { $fail += "install file missing: $($f.name)"; continue }
    $h = (Get-FileHash $p -Algorithm SHA256).Hash
    if ($h -ne $f.sha256) { $fail += "install file modified: $($f.name)" }
}
if (-not ($fail | Where-Object { $_ -like 'install file*' })) {
    Write-Host "OK  install root files all hash to baseline ($($baseline.installRoot.Count) files)" -ForegroundColor Green
}

if (-not $KeepScratch) {
    if (Test-Path $ProjectDir) {
        Remove-Item $ProjectDir -Recurse -Force
        Write-Host "Removed scratch project $ProjectDir (rig copy included)" -ForegroundColor Green
    }
    $bin = Join-Path $PSScriptRoot 'SpineProbe\bin'
    $obj = Join-Path $PSScriptRoot 'SpineProbe\obj'
    foreach ($d in $bin, $obj) { if (Test-Path $d) { Remove-Item $d -Recurse -Force } }
    Write-Host "Removed probe build output" -ForegroundColor Green
}

Write-Host ""
foreach ($n in $note) { Write-Host "NOTE: $n" -ForegroundColor Yellow }
if ($fail.Count -gt 0) {
    foreach ($f in $fail) { Write-Host "FAIL: $f" -ForegroundColor Red }
    throw "Reversibility check failed ($($fail.Count) item(s))."
}
Write-Host "Reversibility check passed." -ForegroundColor Green
