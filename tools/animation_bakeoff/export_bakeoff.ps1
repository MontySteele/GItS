<#
  Lane A (dispatch3) animation bake-off: headless import, editor-side probe,
  and .pck export for each generated approach project.

  This script is SEPARATE from tools\build_pck.ps1 on purpose. Lane A does not
  own, run, or edit that script; it borrows two things from it and nothing
  else: the MegaDot editor path and the headless flag pair
  (`--headless --path <dir> --import`, then
  `--headless --path <dir> --export-pack <preset> <out>`), which are what make
  a pack the game could actually load (tools\build_pck.ps1:770-781).

  It never writes into the game installation, never deploys, and never touches
  klee-mod\assets. Everything lands under -OutDir.

  What it measures, per approach:
    * import exit code and any ERROR lines the editor printed;
    * a probe pass that loads the scene headless and prints node/animation/
      state counts (editor-side evidence; live capture is not available while
      the game is in use);
    * THREE exports -- warm, warm-again, and cold (import cache deleted) --
      hashed, which is the repeatability measurement;
    * a failure-mode pass with one referenced texture deleted: does the editor
      hard-fail, or does the scene silently fall back?

  NOTE: keep this file pure ASCII. Windows PowerShell 5.1 reads .ps1 as ANSI
  unless there is a BOM, so smart quotes and em-dashes break the parser
  (same rule as tools\build_pck.ps1, enforced by validate.ps1 S8).
#>
[CmdletBinding()]
param(
    [string]$MegaDot = 'C:\Users\Monty\Downloads\megadot-4.5.1-m.14-windows-x86_64-llvm-editor-csharp\MegaDot_v4.5.1-stable_mono_win64_console.exe',
    [Parameter(Mandatory = $true)][string]$ProjectsDir,
    [Parameter(Mandatory = $true)][string]$OutDir,
    [string[]]$Approach = @('layered', 'cutout', 'mesh', 'particles'),
    [switch]$SkipFailureMode
)

$ErrorActionPreference = 'Stop'

# Same EAP-lowering convention as tools\build_pck.ps1:56-71 and
# klee-mod\build\validate.ps1. Under PS 5.1 with EAP 'Stop', native stderr
# raises NativeCommandError EVEN AT EXIT 0, and `2>&1` without the swap turns
# every stderr line into an ErrorRecord. One Godot deprecation warning is
# enough to kill the run either way, so both halves are handled here rather
# than at each of the four call sites below.
function Invoke-NativeCaptured {
    param([Parameter(Mandatory = $true)][string]$Exe,
          [Parameter(ValueFromRemainingArguments = $true)][object[]]$Arguments)
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        & $Exe @Arguments 2>&1
    } finally {
        $ErrorActionPreference = $prev
    }
}

function Get-Sha256([string]$Path) {
    if (-not (Test-Path $Path)) { return $null }
    return (Get-FileHash $Path -Algorithm SHA256).Hash
}

function Get-ErrorLines($Log) {
    $hits = @($Log | Select-String -Pattern 'ERROR|SCRIPT ERROR|Failed to load')
    return @($hits | ForEach-Object { $_.ToString().Trim() })
}

# ConvertTo-Json renders an empty array as null and a one-element array as a
# scalar, which makes an empty error list indistinguishable from an unrun
# check. Errors are therefore recorded as a count plus a joined sample.
function New-ErrorRecordSummary($Log) {
    $lines = @(Get-ErrorLines $Log)
    $sample = ''
    if ($lines.Count -gt 0) { $sample = ($lines | Select-Object -First 3) -join ' ;; ' }
    return [ordered]@{ count = $lines.Count; sample = $sample }
}

function Get-Bytes([string]$Path) {
    if (-not (Test-Path $Path)) { return 0 }
    return (Get-Item $Path).Length
}

if (-not (Test-Path $MegaDot))     { throw "MegaDot editor not found at $MegaDot (pass -MegaDot)." }
if (-not (Test-Path $ProjectsDir)) { throw "Projects directory not found at $ProjectsDir (run tools\animation_bakeoff\build.py first)." }

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$results = @{}

foreach ($key in $Approach) {
    $proj = Join-Path $ProjectsDir $key
    if (-not (Test-Path (Join-Path $proj 'project.godot'))) {
        throw "No generated project at $proj."
    }
    Write-Host "=== $key" -ForegroundColor Cyan
    $row = [ordered]@{ approach = $key }

    # --- 1. warm import -----------------------------------------------------
    $importLog = Invoke-NativeCaptured $MegaDot --headless --path $proj --import
    $row.import_exit = $LASTEXITCODE
    $row.import_errors = New-ErrorRecordSummary $importLog
    $importLog | Out-File -FilePath (Join-Path $OutDir "$key-import.log") -Encoding utf8

    # --- 2. editor-side probe ----------------------------------------------
    $probeLog = Invoke-NativeCaptured $MegaDot --headless --path $proj --script 'res://probe.gd'
    $row.probe_exit = $LASTEXITCODE
    $probeLog | Out-File -FilePath (Join-Path $OutDir "$key-probe.log") -Encoding utf8
    $row.probe_lines = (@($probeLog | Select-String -Pattern 'PROBE\|' | ForEach-Object { $_.ToString().Trim() })) -join "`n"
    $row.probe_errors = New-ErrorRecordSummary $probeLog

    # --- 3. three exports ---------------------------------------------------
    $packs = [ordered]@{}
    foreach ($run in @('warm1', 'warm2')) {
        $dest = Join-Path $OutDir "$key-$run.pck"
        if (Test-Path $dest) { Remove-Item $dest -Force }
        $exportLog = Invoke-NativeCaptured $MegaDot --headless --path $proj --export-pack 'pck' $dest
        $exitCode = $LASTEXITCODE
        $exportLog | Out-File -FilePath (Join-Path $OutDir "$key-$run-export.log") -Encoding utf8
        $bytes = Get-Bytes $dest
        $sha = Get-Sha256 $dest
        $errs = New-ErrorRecordSummary $exportLog
        $packs[$run] = [ordered]@{ exit = $exitCode; bytes = $bytes; sha256 = $sha; errors = $errs }
    }

    # Cold run: delete the .godot import cache, re-import, re-export. This is
    # the run that answers "is the pack reproducible on a fresh machine?",
    # which is a different question from "is it reproducible in this
    # directory?" -- and the one that matters for a public release.
    $cache = Join-Path $proj '.godot'
    if (Test-Path $cache) { Remove-Item $cache -Recurse -Force }
    $coldImportLog = Invoke-NativeCaptured $MegaDot --headless --path $proj --import
    $row.cold_import_exit = $LASTEXITCODE
    $coldImportLog | Out-File -FilePath (Join-Path $OutDir "$key-cold-import.log") -Encoding utf8
    $dest = Join-Path $OutDir "$key-cold.pck"
    if (Test-Path $dest) { Remove-Item $dest -Force }
    $exportLog = Invoke-NativeCaptured $MegaDot --headless --path $proj --export-pack 'pck' $dest
    $exitCode = $LASTEXITCODE
    $exportLog | Out-File -FilePath (Join-Path $OutDir "$key-cold-export.log") -Encoding utf8
    $bytes = Get-Bytes $dest
    $sha = Get-Sha256 $dest
    $errs = New-ErrorRecordSummary $exportLog
    $packs['cold'] = [ordered]@{ exit = $exitCode; bytes = $bytes; sha256 = $sha; errors = $errs }
    $row.packs = $packs

    # --- 4. failure modes ---------------------------------------------------
    # Delete ONE texture the scene references and ask whether anything notices.
    # Two variants, because they answer DIFFERENT questions:
    #
    #   warm_cache  the .png is gone but .godot/imported and the .import
    #               sidecar survive -- an artist's working tree after a delete
    #   cold_clone  the .png, its .import sidecar, and the whole .godot cache
    #               are gone -- a fresh clone, CI, or another machine
    #
    # Whether either is a hard fail or a silent fallback decides whether a
    # missing art file can ship green, which is the class of defect
    # build_pck.ps1's DERIVED contract exists to stop
    # (tools\build_pck.ps1:789-808).
    if (-not $SkipFailureMode) {
        $manifest = Get-Content (Join-Path $proj 'bakeoff-manifest.json') -Raw | ConvertFrom-Json
        $victimRes = @($manifest.textures_referenced)[0]
        $victim = Join-Path $proj ($victimRes -replace '^res://', '' -replace '/', '\')
        $backup = Join-Path $OutDir ("$key-victim.png.bak")
        $importSidecar = "$victim.import"
        $sidecarBackup = Join-Path $OutDir ("$key-victim.png.import.bak")
        $modes = [ordered]@{}

        foreach ($mode in @('warm_cache', 'cold_clone')) {
            Copy-Item $victim $backup -Force
            Copy-Item $importSidecar $sidecarBackup -Force
            Remove-Item $victim -Force
            if ($mode -eq 'cold_clone') {
                Remove-Item $importSidecar -Force
                if (Test-Path $cache) { Remove-Item $cache -Recurse -Force }
            }
            $failImport = Invoke-NativeCaptured $MegaDot --headless --path $proj --import
            $failImportExit = $LASTEXITCODE
            $failProbe = Invoke-NativeCaptured $MegaDot --headless --path $proj --script 'res://probe.gd'
            $failProbeExit = $LASTEXITCODE
            $failExportDest = Join-Path $OutDir "$key-$mode.pck"
            if (Test-Path $failExportDest) { Remove-Item $failExportDest -Force }
            $failExport = Invoke-NativeCaptured $MegaDot --headless --path $proj --export-pack 'pck' $failExportDest
            $failExportExit = $LASTEXITCODE
            ($failImport + $failProbe + $failExport) |
                Out-File -FilePath (Join-Path $OutDir "$key-$mode.log") -Encoding utf8
            $probeOk = @($failProbe | Select-String -Pattern 'PROBE\|ok=1').Count -gt 0
            $probeMissing = (@($failProbe | Select-String -Pattern 'PROBE\|missing_dependency=' |
                ForEach-Object { $_.ToString().Trim() })) -join ' ;; '
            $modes[$mode] = [ordered]@{
                import_exit        = $failImportExit
                import_errors      = New-ErrorRecordSummary $failImport
                probe_exit         = $failProbeExit
                probe_errors       = New-ErrorRecordSummary $failProbe
                probe_reported_ok  = $probeOk
                probe_missing      = $probeMissing
                export_exit        = $failExportExit
                export_errors      = New-ErrorRecordSummary $failExport
                export_bytes       = Get-Bytes $failExportDest
            }
            Copy-Item $backup $victim -Force
            Copy-Item $sidecarBackup $importSidecar -Force
            Invoke-NativeCaptured $MegaDot --headless --path $proj --import | Out-Null
        }
        Remove-Item $backup, $sidecarBackup -Force
        $row.failure_mode = [ordered]@{ deleted = $victimRes; modes = $modes }
    }

    $results[$key] = $row
}

$outFile = Join-Path $OutDir 'export-results.json'
$results | ConvertTo-Json -Depth 12 | Out-File -FilePath $outFile -Encoding utf8
Write-Host "Wrote $outFile" -ForegroundColor Green
