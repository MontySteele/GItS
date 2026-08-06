<#
  Track AN Skeleton2D spike, validation half (OFFLINE -- the game is never
  launched by anything in this directory).

  Runs the same two MegaDot steps tools/build_pck.ps1 runs over the scratch
  project gen_kokomi_rig.py wrote, then:

    1. reads the exported pack back with the S5 parser
       (tools/probe_spine_pck/pck_read.py, reused) and prints what landed --
       the load-bearing line is whether kokomi_spike/combat.tscn was CONVERTED
       to a binary .scn + .remap (the editor parsed the Skeleton2D scene) or
       stored as unconverted text (it could not, the spine probe's failure
       shape);
    2. runs spike_check.gd headlessly INSIDE the project -- load, instantiate,
       count bones/polygons, resolve the Polygon2D->Skeleton2D paths, play the
       idle clip half a second and print the chest bone's rotation;
    3. runs packcheck/pack_check.gd in a second, empty project that MOUNTS the
       exported .pck and loads the scene out of it -- the same remap
       resolution path the game's own mod mount uses.

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

if (-not (Test-Path $MegaDot))    { throw "MegaDot editor not found at $MegaDot (pass -MegaDot)." }
if (-not (Test-Path $ProjectDir)) { throw "Spike project not found at $ProjectDir -- run gen_kokomi_rig.py first." }
if (-not $Python) {
    $repo = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
    $Python = Join-Path $repo '.venv\Scripts\python.exe'
    if (-not (Test-Path $Python)) {
        # Worktrees do not carry the (gitignored) venv; fall back to the main
        # checkout's.
        $Python = 'C:\Users\Monty\Documents\GitHub\GItS\.venv\Scripts\python.exe'
    }
}
$PckRead = Join-Path (Split-Path -Parent $PSScriptRoot) 'probe_spine_pck\pck_read.py'

# build_pck.ps1's stderr lesson (Serenitea Sweep audit sec.3.4): never 2>&1 a
# native exe under PS 5.1 with ErrorActionPreference=Stop.
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
# Recorded, not fatal: this spike exists to observe, build_pck.ps1 is the gate.
($importLog | Select-String -Pattern 'ERROR|WARNING') | Write-Host

$out = Join-Path $ProjectDir 'spike_strict.pck'
Write-Host "== export-pack 'strict' ==" -ForegroundColor Cyan
$exportLog = Invoke-Captured $MegaDot @('--headless', '--path', $ProjectDir, '--export-pack', 'strict', $out)
$exportLog | Write-Host
Write-Host "export exit=$LASTEXITCODE" -ForegroundColor Yellow
($exportLog | Select-String -Pattern 'ERROR|WARNING') | Write-Host

if (Test-Path $out) {
    Write-Host "-- contents of spike_strict.pck --" -ForegroundColor Green
    & $Python $PckRead $out
} else {
    Write-Host "spike_strict.pck was NOT produced." -ForegroundColor Red
}

Write-Host "== spike_check.gd (in-project instantiate) ==" -ForegroundColor Cyan
Invoke-Captured $MegaDot @('--headless', '--path', $ProjectDir, '--script', 'res://spike_check.gd') | Write-Host
Write-Host "spike_check exit=$LASTEXITCODE" -ForegroundColor Yellow

Write-Host "== pack_check.gd (mount exported pck, load converted scene) ==" -ForegroundColor Cyan
Invoke-Captured $MegaDot @('--headless', '--path', (Join-Path $ProjectDir 'packcheck'), '--script', 'res://pack_check.gd') | Write-Host
Write-Host "pack_check exit=$LASTEXITCODE" -ForegroundColor Yellow
