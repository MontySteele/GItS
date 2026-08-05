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
    4. steam_appid.txt ABSENT. It does not ship with the game: the file appears
       only when the exe is run outside Steam. Any copy found here is removed,
       whether this session created it or inherited it from another one.
    5. every file in the install root still hashes to its baseline value
    6. no leftover run: save files compared against baseline, across EVERY
       saves directory -- runs park under steam\<id>\profileN\saves, not under
       default\1, so checking one profile checks the wrong folder

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

$userDir  = if ($baseline.userDir) { $baseline.userDir } else { Join-Path $env:APPDATA 'SlayTheSpire2' }
$settings = Join-Path $userDir 'default\1\settings.save'
$nowSettings = if (Test-Path $settings) { (Get-Item $settings).LastWriteTimeUtc.ToString('o') } else { $null }
if ($nowSettings -ne $baseline.settingsMtime) {
    $note += "settings.save mtime moved ($($baseline.settingsMtime) -> $nowSettings). Expected if the game was launched; it is user state, not install state."
} else {
    Write-Host "OK  settings.save mtime unchanged" -ForegroundColor Green
}

# steam_appid.txt: correct end state is ABSENT. The file is written by the exe
# when it is run outside Steam; it does not ship. Remove it whoever made it.
$appId = Join-Path $GameDir 'steam_appid.txt'
if (Test-Path $appId) {
    Remove-Item $appId -Force
    if ($baseline.appIdExistsAtBaseline) {
        $note += "steam_appid.txt was present at baseline (a leak from another session) and has been REMOVED. End state is absent, as it should be."
    } else {
        $note += "steam_appid.txt appeared during this session and has been REMOVED -- something launched the exe directly instead of through Steam."
    }
} else {
    Write-Host "OK  steam_appid.txt absent (correct end state; it does not ship with the game)" -ForegroundColor Green
}

# Runs park under steam\<id>\profileN\saves -- NOT under default\1, so a check
# that looks only at the default profile looks in the wrong place.
#
# But not every .save is a run. settings.save / prefs.save / progress.save /
# profile.save are persistent user state and the game rewrites settings.save
# on every quit; treating those as "a run was left behind" cries wolf on a
# clean session (measured: steam\<id>\settings.save went 2949 -> 3062 bytes on
# a boot that never started a run). Classify, then judge:
#   - anything under a saves\ directory that is NOT prefs/progress  -> a RUN
#   - settings/prefs/progress/profile                               -> state
$stateNames = 'settings.save', 'prefs.save', 'progress.save', 'profile.save'
function Test-IsRunFile([string]$relPath) {
    $leaf = Split-Path $relPath -Leaf
    $leaf = $leaf -replace '\.backup$', ''
    return ($relPath -match '[\\/]saves[\\/]') -and ($leaf -notin $stateNames)
}

$nowSaves = @(Get-ChildItem $userDir -Recurse -File -Include '*.save', '*.save.backup' -ErrorAction SilentlyContinue |
    ForEach-Object { "$($_.FullName.Substring($userDir.Length + 1))|$($_.Length)" } | Sort-Object)
$wasSaves = @($baseline.saveFiles | ForEach-Object { "$($_.path)|$($_.size)" } | Sort-Object)

$changed  = @($nowSaves | Where-Object { $_ -notin $wasSaves })
$runFiles = @($changed | Where-Object { Test-IsRunFile ($_ -split '\|')[0] })
$statey   = @($changed | Where-Object { -not (Test-IsRunFile ($_ -split '\|')[0]) })

if ($runFiles.Count -gt 0) {
    $fail += "RUN LEFT BEHIND -- new/changed run file(s): $($runFiles -join '; ')"
} else {
    Write-Host "OK  no run left behind (all profiles checked, incl. steam\<id>\profileN\saves)" -ForegroundColor Green
}
if ($statey.Count -gt 0) {
    $note += "user-state file(s) rewritten, which a launch does by itself: $($statey -join '; ')"
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
