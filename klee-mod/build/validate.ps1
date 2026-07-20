<#
  Static conformance checks for the Klee mod package.

  Scope: rules that are visible WITHOUT running the game -- source text, the
  manifest, and the staged package layout. Rules that need evaluated values
  (empty StartingRelics, pool rarity coverage, loc keys resolved through
  BaseLib's id prefixing) cannot be seen statically and live in
  KleeCode/Diagnostics/KleeSelfCheck.cs, which runs at boot.

  Every rule below is a bug that actually shipped. Run by deploy.ps1 before
  copying anything into the game directory.

  NOTE: keep this file pure ASCII. Windows PowerShell 5.1 reads .ps1 as ANSI
  unless there's a BOM, so smart quotes and em-dashes break the parser.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$StageDir,
    [Parameter(Mandatory = $true)][string]$SourceDir,
    [Parameter(Mandatory = $true)][string]$GameDir
)

$ErrorActionPreference = 'Stop'
$findings = New-Object System.Collections.Generic.List[string]
function Fail($rule, $detail) { $findings.Add("[$rule] $detail") | Out-Null }

# ---------------------------------------------------------------------------
# S1. No stray *.json in the staged package.
#
# ModManager walks mods/ RECURSIVELY and parses every *.json as a manifest. A
# stray deps.json or project.assets.json makes it throw JsonException on EVERY
# boot, for every mod, not just ours. This is why we stage instead of building
# in place.
# ---------------------------------------------------------------------------
$json = Get-ChildItem $StageDir -Recurse -Filter *.json -ErrorAction SilentlyContinue
foreach ($f in $json) {
    if ($f.Name -ne 'manifest.json') {
        Fail 'S1' "stray JSON in package: $($f.FullName). ModManager parses every *.json under mods/ as a manifest and will throw on boot."
    }
}

# ---------------------------------------------------------------------------
# S2. Manifest is well formed and agrees with what we actually shipped.
# ---------------------------------------------------------------------------
$manifestPath = Join-Path $StageDir 'manifest.json'
if (-not (Test-Path $manifestPath)) {
    Fail 'S2' "no manifest.json in $StageDir"
} else {
    $m = Get-Content $manifestPath -Raw | ConvertFrom-Json

    if ([string]::IsNullOrWhiteSpace($m.id)) { Fail 'S2' 'manifest has no id' }

    # has_dll lying in either direction is a silent no-op mod.
    $dll = Join-Path $StageDir "$($m.id).dll"
    if ($m.has_dll -and -not (Test-Path $dll)) {
        Fail 'S2' "manifest says has_dll but $($m.id).dll is not in the package"
    }
    if (-not $m.has_dll -and (Test-Path $dll)) {
        Fail 'S2' "package ships $($m.id).dll but manifest says has_dll: false; it will never be loaded"
    }
    if ($m.has_pck) {
        $pck = Get-ChildItem $StageDir -Filter *.pck -ErrorAction SilentlyContinue
        if (-not $pck) { Fail 'S2' 'manifest says has_pck but no .pck is in the package' }
    }

    # S3. Declared dependencies must actually be installed, or the game fails
    # the dependency gate and silently skips us.
    #
    # Manifests are NOT always named manifest.json: local mods use that name,
    # but Steam Workshop mods ship as <Name>.json (BaseLib.json, Downfall.json).
    # ModManager reads any *.json, which is the same permissiveness that makes
    # S1 necessary. Scan every *.json and match on the id field.
    $installed = @{}
    foreach ($root in @(
            (Join-Path $GameDir 'mods'),
            (Join-Path (Split-Path -Parent (Split-Path -Parent $GameDir)) 'workshop\content\2868840'))) {
        if (-not (Test-Path $root)) { continue }
        foreach ($j in Get-ChildItem $root -Recurse -Filter *.json -ErrorAction SilentlyContinue) {
            try {
                # These files are UTF-8 with BOM; PS 5.1 leaves the BOM in the
                # string and ConvertFrom-Json chokes on it.
                $raw = (Get-Content $j.FullName -Raw) -replace "^\xEF\xBB\xBF|^﻿", ''
                $id = ($raw | ConvertFrom-Json).id
                if ($id) { $installed[$id] = $j.FullName }
            } catch { }
        }
    }

    foreach ($dep in @($m.dependencies)) {
        if (-not $dep) { continue }
        if (-not $installed.ContainsKey($dep.id)) {
            Fail 'S3' "declared dependency '$($dep.id)' is not installed; the game will skip this mod entirely. Found: $($installed.Keys -join ', ')"
        }
    }
}

# ---------------------------------------------------------------------------
# S4. BaseLib custom models must resolve their pool registration.
#
# CustomCardModel's ctor defaults autoAdd:true, which calls
# CustomContentDictionary.AddModel and THROWS unless the class carries a
# [Pool(typeof(...))] attribute. This is a startup crash, not a soft failure:
# it happens during model construction and takes the game to an error screen.
# Shipped 2026-07-20 on DuckAndCover.
#
# Heuristic by necessity -- proving it properly means reading IL for the base
# ctor's bool argument. It catches the shape we actually hit and is honest
# about being a lint, not a proof.
# ---------------------------------------------------------------------------
$customBases = 'CustomCardModel|CustomRelicModel|CustomPotionModel'
foreach ($f in Get-ChildItem $SourceDir -Recurse -Filter *.cs) {
    $text = Get-Content $f.FullName -Raw
    if ($text -notmatch "class\s+\w+\s*:\s*($customBases)") { continue }

    $hasPoolAttr = $text -match '\[\s*Pool\s*\('
    $optsOut     = $text -match 'autoAdd\s*:\s*false'

    if (-not $hasPoolAttr -and -not $optsOut) {
        Fail 'S4' "$($f.Name): derives from a BaseLib Custom*Model but has neither a [Pool(typeof(...))] attribute nor autoAdd: false. Its constructor will throw at startup."
    }
}

# ---------------------------------------------------------------------------
# S5. Loc strings declared in source use the right template syntax.
#
# Two distinct syntaxes, both of which bit us:
#   - SmartFormat uses SINGLE braces. "{{Damage}}" renders literally.
#   - Square brackets are BBCode. "[Block]" collides with the [center] wrapper
#     the card renderer adds and throws "Found end tag center, expected Block".
# The runtime check covers strings after they land in the table; this catches
# them at author time.
# ---------------------------------------------------------------------------
$knownTags = @('center','left','right','b','i','u','s','color','bgcolor','fgcolor',
               'font','img','url','gold','keyword','wave','shake','p')

foreach ($f in Get-ChildItem $SourceDir -Recurse -Filter *.cs) {
    $n = 0
    foreach ($line in (Get-Content $f.FullName)) {
        $n++
        # Only look at lines that are plausibly loc values.
        if ($line -notmatch '"(title|description)"|\.description"\]|\.title"\]') {
            if ($line -notmatch '\("(title|description)",') { continue }
        }

        if ($line -match '\{\{') {
            Fail 'S5' "$($f.Name):$n uses doubled braces; SmartFormat placeholders are single-braced and {{X}} renders literally."
        }
        foreach ($mm in [regex]::Matches($line, '\[/?([A-Za-z_][A-Za-z0-9_]*)')) {
            $tag = $mm.Groups[1].Value
            if ($knownTags -notcontains $tag.ToLower()) {
                Fail 'S5' "$($f.Name):$n uses '[$tag]', which is not a known BBCode tag. If it is a variable write {$tag}; an unknown tag throws at render time."
            }
        }
    }
}

# ---------------------------------------------------------------------------
# S6. Hand-written cards match the ratified sheets.
#
# Generated cards match by construction (R24); hand-written cards have no
# bridge, which is the drift class that shipped cant_catch_me at +3 against a
# ratified +2. tools/lint_handwritten_parity.py extracts each hand-written
# card's idioms (vars, cost, hit counts, upgrade calls) and compares against
# klee-cards.yaml + klee-upgrades.yaml. A missing interpreter is a FINDING,
# not a skip -- a gate that silently steps aside is not a gate.
# ---------------------------------------------------------------------------
$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$venvPython = Join-Path $repoRoot '.venv\Scripts\python.exe'
$parityLint = Join-Path $repoRoot 'tools\lint_handwritten_parity.py'
if (-not (Test-Path $venvPython)) {
    Fail 'S6' "repo venv python not found at $venvPython; cannot run hand-written parity lint."
} elseif (-not (Test-Path $parityLint)) {
    Fail 'S6' "tools/lint_handwritten_parity.py is missing."
} else {
    # No 2>&1: under ErrorActionPreference Stop, PS 5.1 turns redirected
    # native stderr into a terminating NativeCommandError. The lint reports
    # findings on stdout; a crash's traceback shows on the console and the
    # exit code still lands here.
    $parityOut = & $venvPython $parityLint
    if ($LASTEXITCODE -ne 0) {
        Fail 'S6' "hand-written parity lint failed:`n    $($parityOut -join "`n    ")"
    }
}

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
if ($findings.Count -eq 0) {
    Write-Host "validate: OK" -ForegroundColor Green
    exit 0
}

Write-Host "validate: $($findings.Count) finding(s)" -ForegroundColor Red
foreach ($f in $findings) { Write-Host "  $f" -ForegroundColor Red }
throw "Validation failed; refusing to deploy."
