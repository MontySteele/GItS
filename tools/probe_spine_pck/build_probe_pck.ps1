<#
  Track M spine probe, phase 1 (OFFLINE -- the game is never launched here).

  Runs the same two MegaDot steps tools/build_pck.ps1 runs, over the scratch
  project make_probe_project.py wrote, and exports it TWICE: once through the
  preset build_pck.ps1 uses verbatim ("strict"), once with an include_filter
  for the four spine extensions ("wide"). Then it reads both packs back with
  the S5 parser and prints what actually landed.

  The pair is what makes the failure modes distinguishable:

    strict has the spine files    -> packing is a non-issue; any in-game
                                     failure is type resolution or render
    strict drops, wide keeps      -> packing is an export-preset filter
                                     question, one line, no importer needed
    wide drops them too           -> the exporter itself will not carry a file
                                     it cannot classify, and the pack build is
                                     the blocker F1 predicted

  The control scene (plain Sprite2D) is in both packs: if IT goes missing, the
  export failed for reasons that have nothing to do with spine.

  Nothing here writes to the repo, to klee-mod\dist, or to the game directory.

  NOTE: pure ASCII. Windows PowerShell 5.1 reads .ps1 as ANSI without a BOM.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$ProjectDir,
    [string]$MegaDot = 'C:\Users\Monty\Downloads\megadot-4.5.1-m.14-windows-x86_64-llvm-editor-csharp\MegaDot_v4.5.1-stable_mono_win64_console.exe',
    [string]$Python
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path $MegaDot))     { throw "MegaDot editor not found at $MegaDot (pass -MegaDot)." }
if (-not (Test-Path $ProjectDir))  { throw "Probe project not found at $ProjectDir -- run make_probe_project.py first." }
if (-not $Python) {
    $repo = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
    $Python = Join-Path $repo '.venv\Scripts\python.exe'
}

# build_pck.ps1's stderr lesson (Serenitea Sweep audit sec.3.4): never 2>&1 a
# native exe under PS 5.1 with ErrorActionPreference=Stop -- one deprecation
# warning on stderr becomes a NativeCommandError and kills the run.
function Invoke-Captured {
    param([string]$Exe, [string[]]$Arguments)
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try { & $Exe @Arguments } finally { $ErrorActionPreference = $prev }
}

Write-Host "== import (MegaDot headless) ==" -ForegroundColor Cyan
$importLog = Invoke-Captured $MegaDot @('--headless', '--path', $ProjectDir, '--import')
$importLog | Write-Host
Write-Host "import exit=$LASTEXITCODE" -ForegroundColor Yellow
# NOT fatal here, unlike build_pck.ps1: an ERROR line on an unknown resource
# type is one of the results this probe exists to record.
($importLog | Select-String -Pattern 'ERROR|WARNING|spine|skel|atlas') | Write-Host

foreach ($preset in 'strict', 'wide') {
    $out = Join-Path $ProjectDir "probe_$preset.pck"
    Write-Host "== export-pack '$preset' ==" -ForegroundColor Cyan
    $log = Invoke-Captured $MegaDot @('--headless', '--path', $ProjectDir, '--export-pack', $preset, $out)
    $log | Write-Host
    Write-Host "export '$preset' exit=$LASTEXITCODE" -ForegroundColor Yellow
    if (Test-Path $out) {
        Write-Host "-- contents of probe_$preset.pck --" -ForegroundColor Green
        & $Python (Join-Path $PSScriptRoot 'pck_read.py') $out
    } else {
        Write-Host "probe_$preset.pck was NOT produced." -ForegroundColor Red
    }
}
