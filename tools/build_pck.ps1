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

# --- native stderr under Windows PowerShell 5.1 ----------------------------
# The trap validate.ps1 closed on 2026-07-25 was alive in this file until the
# Serenitea Sweep (audit sec.3.4). Both halves bite here, with
# $ErrorActionPreference set to 'Stop' at the top of this script:
#
#   * `2>&1` wraps every stderr line in an ErrorRecord and raises
#     NativeCommandError -- so ONE Godot deprecation warning on stderr killed
#     the pck build even though MegaDot exited 0.
#   * NOT redirecting is not safe either: with EAP 'Stop', native stderr
#     raises NativeCommandError EVEN WHEN THE COMMAND EXITS 0. That is the
#     half that took the whole deploy down from a Pillow UserWarning.
#
# Lowering EAP to 'Continue' for the duration of the call makes stderr behave
# like output rather than like an exception, so the redirect is then safe and
# the diagnostics survive into the failure message instead of going to $null.
# $LASTEXITCODE is a global automatic and survives the call, so every caller
# checks it exactly as before.
#
# Same shape as validate.ps1's Invoke-RepoPython, deliberately: one convention
# across both build scripts, enforced by
# tier0/tests/test_repo_python_convention.py so a new call site cannot quietly
# reintroduce either half.
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

function Invoke-RepoPython {
    param([Parameter(ValueFromRemainingArguments = $true)][object[]]$Arguments)
    Invoke-NativeCaptured $py @Arguments
}

# --- EB-154: sweep BOTH MegaDot logs, against an anchored pattern set -------
# The import log used to be swept with `Select-String 'ERROR'` -- case
# INSENSITIVE and UNANCHORED, so it matched a path containing "error" and
# missed every failure Godot reports without an `ERROR:` prefix
# (`Unrecognized dependency:`, `Failed loading resource`, `Cannot open file`).
# The export was checked by EXIT CODE ONLY, and Godot's headless exporter
# reports a missing referenced texture and exits 0: a dropped dependency
# shipped with the build green.
#
# The matching itself lives in `tools/godot_log_sweep.py` and not here,
# because PS 5.1 semantics cannot be executed from pytest
# (`test_repo_python_convention.py`) -- a sweep written in PowerShell could
# only ever be pinned as source text, and what has to be right is the
# matching. The log is written beside the scratch project so a failed build
# leaves the evidence on disk.
function Assert-GodotLogClean {
    param([Parameter(Mandatory = $true)][AllowEmptyCollection()][object[]]$Log,
          [Parameter(Mandatory = $true)][ValidateSet('import', 'export')][string]$Stage)
    $logPath = Join-Path $work "megadot-$Stage.log"
    [IO.File]::WriteAllText($logPath, ($Log | Out-String))
    $sweep = Invoke-RepoPython (Join-Path $repo 'tools\godot_log_sweep.py') $logPath --stage $Stage
    $sweep | Write-Host
    if ($LASTEXITCODE -ne 0) {
        throw "MegaDot $Stage reported failures (see $logPath)."
    }
}

if (-not (Test-Path $MegaDot)) { throw "MegaDot editor not found at $MegaDot (pass -MegaDot)." }
# The sweep above always runs, so the venv is a hard requirement of this
# script rather than of its WebP branch alone.
if (-not (Test-Path $py))      { throw "No venv python at $py; tools/godot_log_sweep.py cannot run and the import/export logs would go unread." }
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

# C4 (audit sec.3.2): every copy block below skipped SILENTLY on a missing
# source, and the contract at the bottom of this file was a hand-written list
# that asserted the result regardless. Missing salon art shipped with all
# gates green. Skips are now collected and reported as a block at the end --
# one place to look, rather than a warning buried in 200 lines of build
# output -- and the contract is DERIVED from what actually landed, so a
# skipped block is visible downstream instead of being papered over.
$skipped = @()
function Note-Skip([string]$what, [string]$path) {
    $script:skipped += "$what (no source at $path)"
    Write-Host "SKIPPED: $what -- no source at $path" -ForegroundColor Yellow
}

# Klee's historical art layout predates the roster and stays at ImageGen/images
# /<surface>. Furina and later characters use ImageGen/images/<character>
# /<surface>. Both land in character namespaces inside the merged pack.
foreach ($d in 'ui', 'powers', 'relics', 'model') {
    $from = Join-Path $src $d
    if (-not (Test-Path $from)) { Note-Skip "klee\$d" $from; continue }
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
if (-not (Test-Path $layerSrc)) { Note-Skip 'klee\model\layers' $layerSrc } else {
    $to = Join-Path $work 'klee\model\layers'
    New-Item -ItemType Directory -Force -Path $to | Out-Null
    Copy-Item (Join-Path $layerSrc '*.png') -Destination $to
}

# Animation sprint 2 (Track B1): the same treatment for Furina, cut by
# tools/cut_combat_layers.py furina.
$furinaLayerSrc = Join-Path $src 'furina\model\layers\combat'
if (-not (Test-Path $furinaLayerSrc)) { Note-Skip 'furina\model\layers' $furinaLayerSrc } else {
    $to = Join-Path $work 'furina\model\layers'
    New-Item -ItemType Directory -Force -Path $to | Out-Null
    Copy-Item (Join-Path $furinaLayerSrc '*.png') -Destination $to
}

# Animation sprint 2 (Track D1): Salon member stage sprites, cut by
# tools/cut_salon_members.py. Silhouette-first mini-sprites for salon_stage.tscn.
$salonSrc = Join-Path $src 'furina\salon'
if (-not (Test-Path $salonSrc)) { Note-Skip 'furina\salon' $salonSrc } else {
    $to = Join-Path $work 'furina\salon'
    New-Item -ItemType Directory -Force -Path $to | Out-Null
    $files = Get-ChildItem $salonSrc -Filter *.png -ErrorAction SilentlyContinue
    if ($files) { Copy-Item $files.FullName -Destination $to }
}

# EB-53/N1 (the attribution pass): the Bake-Kurage entity for the end-of-turn
# docket, cut by tools/cut_kurage_summon.py. Its own namespace rather than
# kokomi\powers because it is a CREATURE on the field, not a status badge --
# the same distinction furina\salon draws, and the reason it takes the same
# shape of block.
$kurageSrc = Join-Path $src 'kokomi\summon'
if (-not (Test-Path $kurageSrc)) { Note-Skip 'kokomi\summon' $kurageSrc } else {
    $to = Join-Path $work 'kokomi\summon'
    New-Item -ItemType Directory -Force -Path $to | Out-Null
    $files = Get-ChildItem $kurageSrc -Filter *.png -ErrorAction SilentlyContinue
    if ($files) { Copy-Item $files.FullName -Destination $to }
}

# WORKING FILES MUST NOT SHIP. The still generators (gen_furina_stills.py,
# gen_kokomi_stills.py) cache their governing render next to the outputs, in
# model\, because that is where the source of truth for a character's framing
# belongs. Nothing in the game ever loads them -- the game loads the 240x280
# combat_model.png that gets CUT FROM them -- but a blanket *.png copy shipped
# them anyway. Kokomi's cached cutout is 8.6 MB against a whole pck of 8.3 MB,
# so this silently doubled the download for a file with no consumer. Excluded
# by suffix rather than by name so the next character's cutout is covered
# before anyone notices it exists.
#
# Filtered with Where-Object, NOT with -Exclude. Get-ChildItem -Filter *.png
# -Exclude <pattern> against a DIRECTORY path returns nothing at all: -Exclude
# matches the path item, which is the directory, so the directory is excluded
# and no files are enumerated. That silently copied zero images and dropped
# BOTH characters back onto the Klee fallbacks -- a green build that shipped
# the wrong art, caught only because the fallback lines are printed.
$pckExclude = '*_cutout.png'

foreach ($character in 'furina', 'kokomi') {
    $charSrc = Join-Path $src $character
    foreach ($d in 'ui', 'powers', 'relics', 'model') {
        $from = Join-Path $charSrc $d
        if (-not (Test-Path $from)) { Note-Skip "$character\$d" $from; continue }
        $to = Join-Path $work "$character\$d"
        New-Item -ItemType Directory -Force -Path $to | Out-Null
        $files = Get-ChildItem $from -Filter *.png -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -notlike $pckExclude }
        if ($files) { Copy-Item $files.FullName -Destination $to }
    }
}

# EB-40 / R231: the five Hydro orb layers for furina\ui\energy_counter.tscn.
# Its own block because the loop above is deliberately NON-recursive (one
# Get-ChildItem per surface directory), so a subdirectory under ui\ ships only
# if something asks for it -- and these five are one indivisible set that
# gen_energy_orb_layers.py --apply places in a directory of its own. If they
# are absent the scene still exports, with five ExtResource misses that
# Assert-GodotLogClean turns into a failed build rather than a silent
# textureless orb.
$orbSrc = Join-Path $src 'furina\ui\energy_orb'
if (-not (Test-Path $orbSrc)) { Note-Skip 'furina\ui\energy_orb' $orbSrc } else {
    $to = Join-Path $work 'furina\ui\energy_orb'
    New-Item -ItemType Directory -Force -Path $to | Out-Null
    $files = Get-ChildItem $orbSrc -Filter *.png -ErrorAction SilentlyContinue
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
        'ui\char_icon_outline.png',
        'ui\map_marker.png',
        'ui\selection_splash.png',
        'ui\select_bg.png',
        'ui\transition_wipe.png',
        'model\combat_model.png')) {
    Copy-FurinaFallback $relative
}

# Kokomi, same arrangement and the same NON-NEGOTIABLE reason. Her Custom*Path
# overrides return KleePck.Path(...), which is null when a file is absent --
# and a null override does NOT fall back to something safe. CharacterModel's
# AssetPaths then hands the game an id-derived path that does not exist, the
# background preloads fail, AssetCache is left incomplete, and the run crashes
# during map generation. That exact sequence is the Furina defect recorded in
# KleeSelfCheck R9. So "ship her on placeholders" cannot mean "ship her with no
# files"; it means ship her with Klee's files at HER paths.
function Copy-KokomiFallback([string]$relative) {
    $target = Join-Path (Join-Path $work 'kokomi') $relative
    if (Test-Path $target) { return }

    $fallback = Join-Path (Join-Path $work 'klee') $relative
    if (-not (Test-Path $fallback)) {
        throw "Neither Kokomi nor Klee provides required PCK asset: $relative"
    }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
    Copy-Item $fallback -Destination $target
    Write-Host "Kokomi fallback: $relative <- Klee" -ForegroundColor DarkYellow
}

foreach ($relative in @(
        'ui\select_portrait.png',
        'ui\select_portrait_locked.png',
        'ui\char_icon.png',
        'ui\char_icon_outline.png',
        'ui\map_marker.png',
        'ui\selection_splash.png',
        'ui\select_bg.png',
        'ui\transition_wipe.png',
        'model\combat_model.png')) {
    Copy-KokomiFallback $relative
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
New-Item -ItemType Directory -Force -Path (Join-Path $work 'kokomi\materials') | Out-Null

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

# Kokomi's backdrop tint began as the only thing distinguishing her select
# screen from Klee's while she ran on Klee's fallback splash. Her own art
# landed 2026-07-25 (Watatsumi namecard backdrop, cut-out splash), and the
# tint is KEPT rather than retired: it is the same Watatsumi pearl-blue her
# CardPool, map marker and name colour use, and multiplying it over her
# namecard pushes the reef back so the figure separates from it. Furina's
# scene keeps its tint over her own namecard for the same reason.
[IO.File]::WriteAllText((Join-Path $work 'kokomi\ui\char_select_bg_kokomi.tscn'), @'
[gd_scene load_steps=3 format=3]

[ext_resource type="Texture2D" path="res://kokomi/ui/selection_splash.png" id="1_art"]
[ext_resource type="Texture2D" path="res://kokomi/ui/select_bg.png" id="2_bg"]

[node name="KokomiBg" type="Control"]
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
self_modulate = Color(0.44, 0.78, 0.84, 1)

[node name="Splash" type="TextureRect" parent="."]
layout_mode = 0
offset_right = 1920.0
offset_bottom = 1080.0
texture = ExtResource("1_art")
expand_mode = 1
stretch_mode = 6
'@)

# Character.Icon returns a Control that the game parents into its own slot --
# the box next to HP in the top-left player panel. These were authored at a
# fixed 88x88 anchored top-left, which only lands correctly if the slot happens
# to be exactly 88x88 with the same origin; playtest 2026-07-24 reported the
# icon sitting off its square. Full-rect anchors make the icon adopt whatever
# box it is given, and KEEP_ASPECT_CENTERED (stretch_mode 5) keeps the art
# square inside it. custom_minimum_size is the floor: if a slot ever hands us a
# zero-size parent, the icon stays 88x88 instead of collapsing to invisible.
[IO.File]::WriteAllText((Join-Path $work 'klee\ui\character_icon.tscn'), @'
[gd_scene load_steps=2 format=3]

[ext_resource type="Texture2D" path="res://klee/ui/char_icon.png" id="1_tex"]

[node name="KleeIcon" type="TextureRect"]
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
custom_minimum_size = Vector2(88, 88)
texture = ExtResource("1_tex")
expand_mode = 1
stretch_mode = 5
mouse_filter = 2
'@)

[IO.File]::WriteAllText((Join-Path $work 'furina\ui\character_icon.tscn'), @'
[gd_scene load_steps=2 format=3]

[ext_resource type="Texture2D" path="res://furina/ui/char_icon.png" id="1_tex"]

[node name="FurinaIcon" type="TextureRect"]
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
custom_minimum_size = Vector2(88, 88)
texture = ExtResource("1_tex")
expand_mode = 1
stretch_mode = 5
mouse_filter = 2
'@)

[IO.File]::WriteAllText((Join-Path $work 'kokomi\ui\character_icon.tscn'), @'
[gd_scene load_steps=2 format=3]

[ext_resource type="Texture2D" path="res://kokomi/ui/char_icon.png" id="1_tex"]

[node name="KokomiIcon" type="TextureRect"]
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
custom_minimum_size = Vector2(88, 88)
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

# Kokomi gets the same THREE distinct paths, and the distinctness is the
# load-bearing part -- BaseLib's conversion registry is keyed by path, so
# sharing one scene between rest site and merchant makes the second
# registration overwrite the first and NRestSiteCharacter.Create's cast throws
# inside NRestSiteRoom._Ready. That was the first-campfire softlock of
# 2026-07-20, and it is cheaper to write three near-identical scenes than to
# debug it a third time.
[IO.File]::WriteAllText((Join-Path $work 'kokomi\model\combat_visuals.tscn'), @'
[gd_scene load_steps=2 format=3]

[ext_resource type="Texture2D" path="res://kokomi/model/combat_model.png" id="1_tex"]

[node name="KokomiCombatSprite" type="Sprite2D"]
texture = ExtResource("1_tex")
'@)

[IO.File]::WriteAllText((Join-Path $work 'kokomi\model\rest_character.tscn'), @'
[gd_scene load_steps=2 format=3]

[ext_resource type="Texture2D" path="res://kokomi/model/combat_model.png" id="1_tex"]

[node name="KokomiRestSprite" type="Sprite2D"]
texture = ExtResource("1_tex")
'@)

[IO.File]::WriteAllText((Join-Path $work 'kokomi\model\merchant_character.tscn'), @'
[gd_scene load_steps=2 format=3]

[ext_resource type="Texture2D" path="res://kokomi/model/combat_model.png" id="1_tex"]

[node name="KokomiMerchantSprite" type="Sprite2D"]
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
  "KLEEMOD-OVERLOAD_PREVIEW.title": "Reaction preview: Overloaded",
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
  "THE_ARCHITECT.talk.KLEEMOD-FURINA.0-1r.char": "Both. It was always both. Now - the people rejoice, and their Regina takes her bow.",
  "THE_ARCHITECT.talk.KLEEMOD-KOKOMI.0-0r.ancient": "Priestess. You spent no blood on my stairs, only paper and patience. Tell me what that bought you.",
  "THE_ARCHITECT.talk.KLEEMOD-KOKOMI.0-0r.next": "Respond",
  "THE_ARCHITECT.talk.KLEEMOD-KOKOMI.0-1r.char": "Every plan I burned on the way up. Read them, and you will find the last one already written."
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

[IO.File]::WriteAllText((Join-Path $work 'kokomi\materials\kokomi_transition_mat.tres'), @'
[gd_resource type="ShaderMaterial" load_steps=3 format=3]

[ext_resource type="Texture2D" path="res://kokomi/ui/transition_wipe.png" id="1_wipe"]

[sub_resource type="Shader" id="Shader_kokomi"]
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
shader = SubResource("Shader_kokomi")
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
    $reencodeLog = Invoke-RepoPython -c "from PIL import Image`nfor p in ['$list']:`n    Image.open(p).save(p, 'PNG')"
    if ($LASTEXITCODE -ne 0) { $reencodeLog | Write-Host; throw "Pillow re-encode failed." }
}

Write-Host "Importing assets (MegaDot headless)..." -ForegroundColor Cyan
$importLog = Invoke-NativeCaptured $MegaDot --headless --path $work --import
if ($LASTEXITCODE -ne 0) { $importLog | Write-Host; throw "MegaDot import failed ($LASTEXITCODE)." }
Assert-GodotLogClean -Log $importLog -Stage 'import'

Write-Host "Exporting pack..." -ForegroundColor Cyan
$exportLog = Invoke-NativeCaptured $MegaDot --headless --path $work --export-pack 'pck' (Join-Path $work 'klee.pck')
if ($LASTEXITCODE -ne 0) { $exportLog | Write-Host; throw "MegaDot export failed ($LASTEXITCODE)." }
# The half that was never checked at all: the exporter reports a missing
# referenced texture and exits 0.
Assert-GodotLogClean -Log $exportLog -Stage 'export'

$pck = Join-Path $work 'klee.pck'
if (-not (Test-Path $pck) -or (Get-Item $pck).Length -lt 1024) { throw "Export produced no usable pck at $pck." }

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $out) | Out-Null
Copy-Item $pck -Destination $out -Force
$size = (Get-Item $out).Length
$hash = (Get-FileHash $out -Algorithm SHA256).Hash
$contract = "$out.contract.txt"

# C4 (audit sec.3.2): THE CONTRACT NOW MEASURES.
#
# It used to be the static list below -- written after the export, asserting a
# set of resources regardless of whether any of them had been copied. Every
# copy block above skips on a missing source, so the contract said
# "res://furina/salon/member_usher.png" whether or not that file existed.
# S2 verified the contract BELONGS to the pck (sha256) and S6c checked C#
# references against the contract TEXT, so the loop never once touched the
# actual pack contents: missing salon art shipped with all gates green.
#
# Derived from the work directory instead -- which is precisely what the
# exporter packed, since the preset is export_filter="all_resources". A
# resource missing from this list is now a resource that is missing from the
# pck, and S6c turns that into a failure for anything C# references.
#
# Excludes the project scaffolding and the exported pack itself: none of them
# are resources the game loads. `.godot` is the import cache.
#
# ROSTER-PCK-V3 is a real version bump, and validate.ps1 S2 requires it: a v2
# contract is a hand-written one, and reading it as current would be reading
# an assertion as a measurement. Rebuild with this script.
$contractSkip = @('*\.godot\*', '*\project.godot', '*\export_presets.cfg',
                  '*\klee.pck')
$packed = @(Get-ChildItem $work -Recurse -File |
    Where-Object {
        $p = $_.FullName
        -not ($contractSkip | Where-Object { $p -like $_ }) -and
        $_.Extension -ne '.import'
    } |
    ForEach-Object {
        'resource=res://' + $_.FullName.Substring($work.Length + 1).Replace('\', '/')
    } | Sort-Object)
if ($packed.Count -eq 0) { throw "Contract would be empty: nothing landed in $work." }
$contractLines = @('contract=roster-pck-v3', "sha256=$hash") + $packed
[IO.File]::WriteAllLines($contract, $contractLines)
Write-Host "Built $out ($size bytes; contract roster-pck-v3, $($packed.Count) resources)" -ForegroundColor Green
if ($skipped.Count -gt 0) {
    Write-Host ""
    Write-Host "$($skipped.Count) copy block(s) SKIPPED -- those resources are NOT in the pck:" -ForegroundColor Yellow
    foreach ($s in $skipped) { Write-Host "  $s" -ForegroundColor Yellow }
    Write-Host "validate.ps1 S6c will fail for any of these that C# references." -ForegroundColor Yellow
}

# The v2 contract this replaced was a hand-written list of ~45 resource lines,
# appended after the export and asserting that set regardless of what the copy
# blocks had actually done. It is deleted rather than kept: a record of what an
# assertion used to claim is not worth carrying, and `git show` has it.
