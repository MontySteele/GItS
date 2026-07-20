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

# Text resources authored here, not in ImageGen: the character-select bg scene
# (a Control the game instantiates into its AnimatedBg container -- structure
# mirrors the base game's char_select_bg_ironclad.tscn, minus spine/particles),
# the model sprite scene (BaseLib auto-converts a Sprite2D root into the full
# NRestSiteCharacter/NMerchantCharacter node trees), and the select-transition
# ShaderMaterial (same 10-line threshold-wipe shader as the base game's
# ironclad_transition_mat.tres, pointed at our procedural wipe texture).
# No scripts anywhere in these scenes: script resources can't ship in a mod
# pck, and none are needed.
New-Item -ItemType Directory -Force -Path (Join-Path $work 'klee\materials') | Out-Null

[IO.File]::WriteAllText((Join-Path $work 'klee\ui\char_select_bg_klee.tscn'), @'
[gd_scene load_steps=3 format=3]

[ext_resource type="Texture2D" path="res://klee/ui/selection_splash.png" id="1_art"]
[ext_resource type="Texture2D" path="res://klee/ui/select_bg.png" id="2_bg"]

[node name="KleeBg" type="Control"]
layout_mode = 3
anchors_preset = 8
anchor_left = 0.5
anchor_top = 0.5
anchor_right = 0.5
anchor_bottom = 0.5
offset_left = -960.0
offset_top = -540.0
offset_right = 960.0
offset_bottom = 540.0
grow_horizontal = 2
grow_vertical = 2
pivot_offset = Vector2(960, 540)

[node name="Backdrop" type="TextureRect" parent="."]
layout_mode = 0
offset_right = 1920.0
offset_bottom = 1080.0
texture = ExtResource("2_bg")
expand_mode = 1
stretch_mode = 6
self_modulate = Color(0.52, 0.42, 0.42, 1)

[node name="Splash" type="TextureRect" parent="."]
layout_mode = 0
offset_right = 1920.0
offset_bottom = 1080.0
texture = ExtResource("1_art")
expand_mode = 1
stretch_mode = 6
'@)

[IO.File]::WriteAllText((Join-Path $work 'klee\model\character_sprite.tscn'), @'
[gd_scene load_steps=2 format=3]

[ext_resource type="Texture2D" path="res://klee/model/combat_model.png" id="1_tex"]

[node name="KleeSprite" type="Sprite2D"]
texture = ExtResource("1_tex")
'@)

[IO.File]::WriteAllText((Join-Path $work 'klee\materials\klee_transition_mat.tres'), @'
[gd_resource type="ShaderMaterial" load_steps=3 format=3]

[ext_resource type="Texture2D" path="res://klee/ui/transition_wipe.png" id="1_wipe"]

[sub_resource type="Shader" id="Shader_klee"]
code = "shader_type canvas_item;

uniform sampler2D transitionTex;
uniform float threshold : hint_range(0,1);

void fragment() {
    float falloff = 1.0 - texture(transitionTex, UV).r;

    // helps with falloff artifacts issues towards the transition extremes
    float remap  = mix(-0.1, 1.1, threshold);
    falloff = step(falloff, remap);
    COLOR.a = falloff;
}
"

[resource]
resource_local_to_scene = true
shader = SubResource("Shader_klee")
shader_parameter/threshold = 0.332
shader_parameter/transitionTex = ExtResource("1_wipe")
'@)

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
