<#
  Build klee.pck from ImageGen art with the MegaDot editor.

  The pack carries the art that MUST live at res:// paths as editor-imported
  resources (CompressedTexture2D): character-select surfaces, the top-panel
  icon, the map marker, power icons, and relic icons. Card portraits are NOT
  in here -- they ship as loose PNGs (see KleeArt.cs) and stay on that path.

  The editor must be the game's own Godot fork (MegaDot 4.5.1) so the pack
  format and .ctex import format match the runtime. The game loads the pack
  itself: manifest has_pck true makes ModManager call LoadResourcePack on
  mods/klee/klee.pck during mod read, before mod initializers run.

  Output goes to klee-mod\assets\klee.pck, which deploy.ps1 stages. *.pck is
  gitignored (public repo, Tier F art never ships in the repo), so every
  machine builds its own with this script.

  NOTE: keep this file pure ASCII. Windows PowerShell 5.1 reads .ps1 as ANSI
  unless there's a BOM, so smart quotes and em-dashes break the parser.
#>
[CmdletBinding()]
param(
    [string]$MegaDot = 'C:\Users\Monty\Downloads\megadot-4.5.1-m.14-windows-x86_64-llvm-editor-csharp\MegaDot_v4.5.1-stable_mono_win64_console.exe'
)

$ErrorActionPreference = 'Stop'

$repo = Split-Path -Parent $PSScriptRoot
$src  = Join-Path $repo 'ImageGen\images'
$work = Join-Path $repo 'klee-mod\dist\pck-work'
$out  = Join-Path $repo 'klee-mod\assets\klee.pck'
$py   = Join-Path $repo '.venv\Scripts\python.exe'

if (-not (Test-Path $MegaDot)) { throw "MegaDot editor not found at $MegaDot (pass -MegaDot)." }
if (-not (Test-Path $src))     { throw "Art source not found at $src." }

# Fresh scratch project every run: stale .godot import caches from a previous
# editor version are a class of bug we never want to debug.
if (Test-Path $work) { Remove-Item $work -Recurse -Force }
New-Item -ItemType Directory -Force -Path $work | Out-Null

# Minimal project: its only job is to import the textures and export a pack.
[IO.File]::WriteAllText((Join-Path $work 'project.godot'), @'
; Minimal project whose only job is to import Klee's art and export a .pck
; the game (MegaDot 4.5.1) can merge into res:// at runtime.
config_version=5

[application]

config/name="KleePck"
'@)

[IO.File]::WriteAllText((Join-Path $work 'export_presets.cfg'), @'
[preset.0]

name="pck"
platform="Windows Desktop"
runnable=true
advanced_options=false
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path="klee.pck"
patches=PackedStringArray()
encryption_include_filters=""
encryption_exclude_filters=""
seed=0
encrypt_pck=false
encrypt_directory=false
script_export_mode=2

[preset.0.options]

binary_format/embed_pck=false
'@)

# Namespaced under res://klee/ so nothing can collide with the game's own
# resource tree when the pack merges.
foreach ($d in 'ui', 'powers', 'relics', 'model') {
    $from = Join-Path $src $d
    if (-not (Test-Path $from)) { Write-Host "WARNING: no $from, skipping" -ForegroundColor Yellow; continue }
    $to = Join-Path $work "klee\$d"
    New-Item -ItemType Directory -Force -Path $to | Out-Null
    Copy-Item (Join-Path $from '*.png') -Destination $to
}

# Some fetched files are WebP with a .png extension (the wiki serves them that
# way); Godot's PNG importer hard-fails on them. Re-encode in place, in the
# scratch copy only -- ImageGen sources belong to the art pipeline.
$webp = @()
foreach ($f in Get-ChildItem (Join-Path $work 'klee') -Recurse -Filter *.png) {
    $bytes = [IO.File]::ReadAllBytes($f.FullName)
    if ($bytes.Length -ge 4 -and $bytes[0] -eq 0x52 -and $bytes[1] -eq 0x49 -and $bytes[2] -eq 0x46 -and $bytes[3] -eq 0x46) {
        $webp += $f.FullName
    }
}
if ($webp.Count -gt 0) {
    if (-not (Test-Path $py)) { throw "Found $($webp.Count) WebP-mislabeled png(s) but no venv python at $py to convert them." }
    Write-Host "Re-encoding $($webp.Count) WebP-mislabeled file(s) to PNG..." -ForegroundColor Cyan
    $list = ($webp | ForEach-Object { $_.Replace('\', '/') }) -join "','"
    & $py -c "from PIL import Image`nfor p in ['$list']:`n    Image.open(p).save(p, 'PNG')"
    if ($LASTEXITCODE -ne 0) { throw "Pillow re-encode failed." }
}

Write-Host "Importing assets (MegaDot headless)..." -ForegroundColor Cyan
$importLog = & $MegaDot --headless --path $work --import 2>&1
if ($LASTEXITCODE -ne 0) { $importLog | Write-Host; throw "MegaDot import failed ($LASTEXITCODE)." }
$importErrors = $importLog | Select-String 'ERROR'
if ($importErrors) { $importErrors | Write-Host; throw "MegaDot import reported errors." }

Write-Host "Exporting pack..." -ForegroundColor Cyan
$exportLog = & $MegaDot --headless --path $work --export-pack 'pck' (Join-Path $work 'klee.pck') 2>&1
if ($LASTEXITCODE -ne 0) { $exportLog | Write-Host; throw "MegaDot export failed ($LASTEXITCODE)." }

$pck = Join-Path $work 'klee.pck'
if (-not (Test-Path $pck) -or (Get-Item $pck).Length -lt 1024) { throw "Export produced no usable pck at $pck." }

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $out) | Out-Null
Copy-Item $pck -Destination $out -Force
$size = (Get-Item $out).Length
Write-Host "Built $out ($size bytes)" -ForegroundColor Green
