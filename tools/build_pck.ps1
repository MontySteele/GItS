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

# Klee's historical art layout predates the roster and stays at ImageGen/images
# /<surface>. Furina and later characters use ImageGen/images/<character>
# /<surface>. Both land in character namespaces inside the merged pack.
foreach ($d in 'ui', 'powers', 'relics', 'model') {
    $from = Join-Path $src $d
    if (-not (Test-Path $from)) { Write-Host "WARNING: no $from, skipping" -ForegroundColor Yellow; continue }
    $to = Join-Path $work "klee\$d"
    New-Item -ItemType Directory -Force -Path $to | Out-Null
    $files = Get-ChildItem $from -Filter *.png -ErrorAction SilentlyContinue
    if ($files) { Copy-Item $files.FullName -Destination $to }
}

# Animation sprint 1 (Track B): pre-scaled combat layer sprites for the
# animated combat scene. Full-res layer masters live in ImageGen/images/model
# /layers; only the combat-scale derivatives in layers/combat ship, matching
# how every other roster surface ships pre-sized art.
$layerSrc = Join-Path $src 'model\layers\combat'
if (Test-Path $layerSrc) {
    $to = Join-Path $work 'klee\model\layers'
    New-Item -ItemType Directory -Force -Path $to | Out-Null
    Copy-Item (Join-Path $layerSrc '*.png') -Destination $to
}

$furinaSrc = Join-Path $src 'furina'
foreach ($d in 'ui', 'powers', 'relics', 'model') {
    $from = Join-Path $furinaSrc $d
    if (-not (Test-Path $from)) { continue }
    $to = Join-Path $work "furina\$d"
    New-Item -ItemType Directory -Force -Path $to | Out-Null
    $files = Get-ChildItem $from -Filter *.png -ErrorAction SilentlyContinue
    if ($files) { Copy-Item $files.FullName -Destination $to }
}

# Furina can be tested before her art pass lands, but her resource PATHS must
# still be character-specific. Fill only missing Furina files from Klee; a real
# Furina file at the canonical path always wins.
function Copy-FurinaFallback([string]$relative) {
    $target = Join-Path (Join-Path $work 'furina') $relative
    if (Test-Path $target) { return }

    $fallback = Join-Path (Join-Path $work 'klee') $relative
    if (-not (Test-Path $fallback)) {
        throw "Neither Furina nor Klee provides required PCK asset: $relative"
    }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
    Copy-Item $fallback -Destination $target
    Write-Host "Furina fallback: $relative <- Klee" -ForegroundColor DarkYellow
}

foreach ($relative in @(
        'ui\select_portrait.png',
        'ui\select_portrait_locked.png',
        'ui\char_icon.png',
        'ui\map_marker.png',
        'ui\selection_splash.png',
        'ui\select_bg.png',
        'ui\transition_wipe.png',
        'model\combat_model.png')) {
    Copy-FurinaFallback $relative
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
New-Item -ItemType Directory -Force -Path (Join-Path $work 'furina\materials') | Out-Null

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

[IO.File]::WriteAllText((Join-Path $work 'furina\ui\char_select_bg_furina.tscn'), @'
[gd_scene load_steps=3 format=3]

[ext_resource type="Texture2D" path="res://furina/ui/selection_splash.png" id="1_art"]
[ext_resource type="Texture2D" path="res://furina/ui/select_bg.png" id="2_bg"]

[node name="FurinaBg" type="Control"]
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
self_modulate = Color(0.33, 0.55, 0.68, 1)

[node name="Splash" type="TextureRect" parent="."]
layout_mode = 0
offset_right = 1920.0
offset_bottom = 1080.0
texture = ExtResource("1_art")
expand_mode = 1
stretch_mode = 6
'@)

[IO.File]::WriteAllText((Join-Path $work 'klee\ui\character_icon.tscn'), @'
[gd_scene load_steps=2 format=3]

[ext_resource type="Texture2D" path="res://klee/ui/char_icon.png" id="1_tex"]

[node name="KleeIcon" type="TextureRect"]
offset_right = 88.0
offset_bottom = 88.0
texture = ExtResource("1_tex")
expand_mode = 1
stretch_mode = 5
mouse_filter = 2
'@)

[IO.File]::WriteAllText((Join-Path $work 'furina\ui\character_icon.tscn'), @'
[gd_scene load_steps=2 format=3]

[ext_resource type="Texture2D" path="res://furina/ui/char_icon.png" id="1_tex"]

[node name="FurinaIcon" type="TextureRect"]
offset_right = 88.0
offset_bottom = 88.0
texture = ExtResource("1_tex")
expand_mode = 1
stretch_mode = 5
mouse_filter = 2
'@)

[IO.File]::WriteAllText((Join-Path $work 'klee\model\combat_visuals.tscn'), @'
[gd_scene load_steps=2 format=3]

[ext_resource type="Texture2D" path="res://klee/model/combat_model.png" id="1_tex"]

[node name="KleeCombatSprite" type="Sprite2D"]
texture = ExtResource("1_tex")
'@)

[IO.File]::WriteAllText((Join-Path $work 'furina\model\combat_visuals.tscn'), @'
[gd_scene load_steps=2 format=3]

[ext_resource type="Texture2D" path="res://furina/model/combat_model.png" id="1_tex"]

[node name="FurinaCombatSprite" type="Sprite2D"]
texture = ExtResource("1_tex")
'@)

[IO.File]::WriteAllText((Join-Path $work 'klee\model\character_sprite.tscn'), @'
[gd_scene load_steps=2 format=3]

[ext_resource type="Texture2D" path="res://klee/model/combat_model.png" id="1_tex"]

[node name="KleeSprite" type="Sprite2D"]
texture = ExtResource("1_tex")
'@)

# Identical scene under a SECOND path: BaseLib's scene-conversion registry is
# keyed by path, so one scene cannot serve two conversion targets. Reusing
# character_sprite.tscn for both rest site and merchant made the merchant
# registration overwrite the rest-site one (BaseLib warns "Overwriting scene
# registration"), the campfire instantiated an NMerchantCharacter, and
# NRestSiteCharacter.Create's cast threw inside NRestSiteRoom._Ready -- the
# first-campfire softlock (godot.log 2026-07-20).
[IO.File]::WriteAllText((Join-Path $work 'klee\model\rest_character.tscn'), @'
[gd_scene load_steps=2 format=3]

[ext_resource type="Texture2D" path="res://klee/model/combat_model.png" id="1_tex"]

[node name="KleeSprite" type="Sprite2D"]
texture = ExtResource("1_tex")
'@)

# Furina receives two additional conversion paths. Reusing Klee's paths is
# harmless while both characters have the same conversion targets, but blocks
# future character-specific conversion behavior. Sharing Furina's own rest and
# merchant path would reproduce the original campfire softlock immediately.
[IO.File]::WriteAllText((Join-Path $work 'furina\model\rest_character.tscn'), @'
[gd_scene load_steps=2 format=3]

[ext_resource type="Texture2D" path="res://furina/model/combat_model.png" id="1_tex"]

[node name="FurinaRestSprite" type="Sprite2D"]
texture = ExtResource("1_tex")
'@)

[IO.File]::WriteAllText((Join-Path $work 'furina\model\merchant_character.tscn'), @'
[gd_scene load_steps=2 format=3]

[ext_resource type="Texture2D" path="res://furina/model/combat_model.png" id="1_tex"]

[node name="FurinaMerchantSprite" type="Sprite2D"]
texture = ExtResource("1_tex")
'@)

# Loc rows for the ElementalSkill custom keyword (KleeKeywords.cs). The game
# merges res://<modid>/localization/<lang>/<table>.json into the base table of
# the same name; the key prefix KLEEMOD-ELEMENTAL_SKILL comes from BaseLib's
# GenEnumValues (namespace prefix + CustomEnum name). The 5 is LAW: tier0
# constants.py BURST_PER_SKILL_TAG (mirrored, never re-derived).
$locDir = Join-Path $work 'klee\localization\eng'
New-Item -ItemType Directory -Force $locDir | Out-Null
[IO.File]::WriteAllText((Join-Path $locDir 'card_keywords.json'), @'
{
  "KLEEMOD-ELEMENTAL_SKILL.title": "Elemental Skill",
  "KLEEMOD-ELEMENTAL_SKILL.description": "Playing this card grants 5 Burst Energy.",
  "KLEEMOD-APPLIES_PYRO.title": "Applies Pyro",
  "KLEEMOD-APPLIES_PYRO.description": "If the target has no aura, this applies Pyro for 2 turns. A different aura is consumed to trigger a Reaction instead.",
  "KLEEMOD-APPLIES_HYDRO.title": "Applies Hydro",
  "KLEEMOD-APPLIES_HYDRO.description": "If the target has no aura, this applies Hydro for 2 turns. A different aura is consumed to trigger a Reaction instead.",
  "KLEEMOD-APPLIES_ELECTRO.title": "Applies Electro",
  "KLEEMOD-APPLIES_ELECTRO.description": "If the target has no aura, this applies Electro for 2 turns. A different aura is consumed to trigger a Reaction instead.",
  "KLEEMOD-APPLIES_CRYO.title": "Applies Cryo",
  "KLEEMOD-APPLIES_CRYO.description": "If the target has no aura, this applies Cryo for 2 turns. A different aura is consumed to trigger a Reaction instead.",
  "KLEEMOD-BOMB.title": "Bomb",
  "KLEEMOD-BOMB.description": "Detonates at the start of your turn or early when its enemy takes unblocked Attack damage. The first attack that enemy makes while Bombed each combat deals 25% less damage.",
  "KLEEMOD-VAPORIZE_PREVIEW.title": "Reaction preview: Vaporize",
  "KLEEMOD-VAPORIZE_PREVIEW.description": "This card supplies Pyro or Hydro while an enemy has the other aura. The triggering hit deals 1.5x damage and consumes the aura.",
  "KLEEMOD-MELT_PREVIEW.title": "Reaction preview: Melt",
  "KLEEMOD-MELT_PREVIEW.description": "This card supplies Pyro or Cryo while an enemy has the other aura. The triggering hit deals 1.75x damage and consumes the aura.",
  "KLEEMOD-OVERLOAD_PREVIEW.title": "Reaction preview: Overload",
  "KLEEMOD-OVERLOAD_PREVIEW.description": "This card supplies Pyro or Electro while an enemy has the other aura. It deals 6 splash damage to all enemies and applies 1 Weak to the reacted enemy.",
  "KLEEMOD-SUPERCONDUCT_PREVIEW.title": "Reaction preview: Superconduct",
  "KLEEMOD-SUPERCONDUCT_PREVIEW.description": "This card supplies Electro or Cryo while an enemy has the other aura. The reacted enemy gains 2 Vulnerable.",
  "KLEEMOD-ELECTRO_CHARGED_PREVIEW.title": "Reaction preview: Electro-Charged",
  "KLEEMOD-ELECTRO_CHARGED_PREVIEW.description": "This card supplies Hydro or Electro while an enemy has the other aura. The reacted enemy gains a 4-damage decaying damage-over-time effect.",
  "KLEEMOD-FROZEN_PREVIEW.title": "Reaction preview: Frozen",
  "KLEEMOD-FROZEN_PREVIEW.description": "This card supplies Hydro or Cryo while an enemy has the other aura. Its next action deals half damage; attacking it Shatters for 6 damage.",
  "KLEEMOD-SWIRL_PREVIEW.title": "Reaction preview: Swirl",
  "KLEEMOD-SWIRL_PREVIEW.description": "This card supplies Anemo to an existing aura. The aura is consumed and copied onto all enemies.",
  "KLEEMOD-CRYSTALLIZE_PREVIEW.title": "Reaction preview: Crystallize",
  "KLEEMOD-CRYSTALLIZE_PREVIEW.description": "This card supplies Geo to an existing aura. The aura is consumed and you gain 4 Block."
}
'@)

# Architect finale dialogue (2026-07-23 softlock). The base game's
# TheArchitect.WinRun() dereferences Dialogue unconditionally, and
# LoadDialogue picks ONLY from per-character entries (allowAnyCharacter-
# Dialogues: false) -- a roster character with no rows here softlocks the
# win-the-run screen. BaseLib merges "THE_ARCHITECT.talk.<CHAR>.<X>-<Y>"
# rows from this table into the game's dialogue set (AddAncientDialogues).
# Key law (from AncientDialogueSet's own doc): X-Y = dialogue-line, suffix
# .ancient/.char = speaker, "r" on X-Y = repeating, ".next" = button text
# for every line but the last. The "r" is LOAD-BEARING: GetValidDialogues
# exact-matches VisitIndex == character wins and only repeating rows
# survive the fallback, so a non-repeating-only set crashes on the SECOND
# win. No -attack rows: BaseLib's default EndAttackers=Both is the base
# game's own finale (character VFX barrage + Architect's counter).
# PLACEHOLDER dialogue text -- naming/writing pass, user red-pen.
[IO.File]::WriteAllText((Join-Path $locDir 'ancients.json'), @'
{
  "THE_ARCHITECT.talk.KLEEMOD-KLEE.0-0r.ancient": "You have climbed far, little spark. Show me what you carried up my Spire.",
  "THE_ARCHITECT.talk.KLEEMOD-KLEE.0-0r.next": "Respond",
  "THE_ARCHITECT.talk.KLEEMOD-KLEE.0-1r.char": "Klee brought the BIGGEST boom! Ready? Da-da-da!",
  "THE_ARCHITECT.talk.KLEEMOD-FURINA.0-0r.ancient": "The curtain falls at last, Regina of All Waters. Was it a performance, or was it real?",
  "THE_ARCHITECT.talk.KLEEMOD-FURINA.0-0r.next": "Respond",
  "THE_ARCHITECT.talk.KLEEMOD-FURINA.0-1r.char": "Both. It was always both. Now — the people rejoice, and their Regina takes her bow."
}
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

[IO.File]::WriteAllText((Join-Path $work 'furina\materials\furina_transition_mat.tres'), @'
[gd_resource type="ShaderMaterial" load_steps=3 format=3]

[ext_resource type="Texture2D" path="res://furina/ui/transition_wipe.png" id="1_wipe"]

[sub_resource type="Shader" id="Shader_furina"]
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
shader = SubResource("Shader_furina")
shader_parameter/threshold = 0.332
shader_parameter/transitionTex = ExtResource("1_wipe")
'@)

# Git-tracked scene sources (klee-mod\pck-src) overlay the work dir verbatim.
# Scenes with real animation data are unmaintainable as heredocs; they live in
# the repo as text and ship through the same import/export as everything else.
$pckSrc = Join-Path $repo 'klee-mod\pck-src'
if (Test-Path $pckSrc) {
    Copy-Item (Join-Path $pckSrc '*') -Destination $work -Recurse -Force -Exclude 'README.md'
    Write-Host "Overlaid pck-src scene sources." -ForegroundColor Cyan
}

# Build id stamp: boot telemetry logs this, so a stale pck announces itself in
# godot.log instead of silently rendering old art (animation sprint 1, A3).
try { $gitSha = (& git -C $repo rev-parse --short HEAD) } catch { $gitSha = $null }
if (-not $gitSha) { $gitSha = 'nogit' }
$buildId = '{0}+{1}' -f (Get-Date -Format 'yyyyMMdd-HHmmss'), $gitSha
[IO.File]::WriteAllText((Join-Path $work 'klee\build_id.tres'), @"
[gd_resource type="Resource" format=3]

[resource]
resource_name = "$buildId"
"@)
Write-Host "Stamped build id $buildId" -ForegroundColor Cyan

# Some fetched files are WebP with a .png extension (the wiki serves them that
# way); Godot's PNG importer hard-fails on them. Re-encode in place, in the
# scratch copy only -- ImageGen sources belong to the art pipeline.
$webp = @()
foreach ($f in Get-ChildItem $work -Recurse -Filter *.png) {
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
$hash = (Get-FileHash $out -Algorithm SHA256).Hash
$contract = "$out.contract.txt"
$contractLines = @(
    'contract=roster-pck-v2',
    "sha256=$hash",
    'resource=res://klee/model/combat_visuals.tscn',
    'resource=res://klee/model/combat.tscn',
    'resource=res://klee/model/layers/klee_combat_smoke.png',
    'resource=res://klee/model/layers/klee_combat_floaters.png',
    'resource=res://klee/model/layers/klee_combat_dumpty.png',
    'resource=res://klee/model/layers/klee_combat_body.png',
    'resource=res://klee/model/layers/klee_combat_dodoco.png',
    'resource=res://klee/build_id.tres',
    'resource=res://klee/ui/character_icon.tscn',
    'resource=res://klee/ui/char_select_bg_klee.tscn',
    'resource=res://klee/materials/klee_transition_mat.tres',
    'resource=res://klee/model/rest_character.tscn',
    'resource=res://klee/model/character_sprite.tscn',
    'resource=res://furina/model/combat_visuals.tscn',
    'resource=res://furina/ui/character_icon.tscn',
    'resource=res://furina/model/rest_character.tscn',
    'resource=res://furina/model/merchant_character.tscn',
    'resource=res://furina/ui/char_select_bg_furina.tscn',
    'resource=res://furina/materials/furina_transition_mat.tres'
)
[IO.File]::WriteAllLines($contract, $contractLines)
Write-Host "Built $out ($size bytes; contract roster-pck-v2)" -ForegroundColor Green
