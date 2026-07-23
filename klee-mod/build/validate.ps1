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
    [Parameter(Mandatory = $true)][string]$GameDir,
    # S7 escape hatch: a game_ref/ directory that EXISTS but is INCOMPLETE
    # fails validation by default (see S7 comment). Pass this switch to
    # acknowledge the stale local reference and test committed content only.
    [switch]$AllowIncompleteGameRef
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
        if (-not $pck) {
            Fail 'S2' 'manifest says has_pck but no .pck is in the package'
        } else {
            $pck = @($pck)[0]
            $contractPath = "$($pck.FullName).contract.txt"
            if (-not (Test-Path $contractPath)) {
                Fail 'S2' "PCK has no build contract at $contractPath; rebuild it with tools\build_pck.ps1."
            } else {
                $contractLines = Get-Content $contractPath
                if ($contractLines -notcontains 'contract=roster-pck-v2') {
                    Fail 'S2' 'PCK contract is stale; expected roster-pck-v2. Rebuild with tools\build_pck.ps1.'
                }
                $hashLine = @($contractLines | Where-Object { $_ -like 'sha256=*' })
                if ($hashLine.Count -ne 1) {
                    Fail 'S2' 'PCK contract must contain exactly one sha256 line.'
                } else {
                    $expectedHash = $hashLine[0].Substring('sha256='.Length)
                    $actualHash = (Get-FileHash $pck.FullName -Algorithm SHA256).Hash
                    if ($actualHash -ne $expectedHash) {
                        Fail 'S2' 'PCK does not match its build contract; rebuild rather than deploying a stale pack.'
                    }
                }
            }
        }
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
# S6a. Generated roster cards and blocker manifests must match their sheets.
#
# This is the character-aware entry point: it checks Klee's shipping output
# and every staged future-character tranche. A blocked card is valid; a stale
# or silently approximated generated card is not.
# ---------------------------------------------------------------------------
$rosterCodegen = Join-Path $repoRoot 'tools\gen_roster_cards.py'
if (-not (Test-Path $venvPython)) {
    Fail 'S6a' "repo venv python not found at $venvPython; cannot check roster codegen."
} elseif (-not (Test-Path $rosterCodegen)) {
    Fail 'S6a' "tools/gen_roster_cards.py is missing."
} else {
    $codegenOut = & $venvPython $rosterCodegen --check
    if ($LASTEXITCODE -ne 0) {
        Fail 'S6a' "roster codegen is stale:`n    $($codegenOut -join "`n    ")"
    }
}

# ---------------------------------------------------------------------------
# S6b. Every card class belongs to a card pool.
#
# Playtest 2026-07-21: companions, the kit Burst card and the Confiscated token
# were all deliberately kept out of KleeCardPool (correctly -- none of them are
# rollable), but a card in NO pool makes CardModel.Pool fall through to
# MockCardPool, which throws "You monster!" in a shipped build. Pool is read
# when a card NODE is built, so it crashed on DRAW, not on play: one softlocked
# combat and one dead-looking reward button. KleeExtraCardPool holds the
# never-rollable cards; this lint makes forgetting it impossible.
# ---------------------------------------------------------------------------
$poolLint = Join-Path $repoRoot 'tools\lint_pool_membership.py'
if (-not (Test-Path $venvPython)) {
    Fail 'S6b' "repo venv python not found at $venvPython; cannot run pool membership lint."
} elseif (-not (Test-Path $poolLint)) {
    Fail 'S6b' "tools/lint_pool_membership.py is missing."
} else {
    $poolOut = & $venvPython $poolLint
    if ($LASTEXITCODE -ne 0) {
        Fail 'S6b' "pool membership lint failed:`n    $($poolOut -join "`n    ")"
    }
}

# ---------------------------------------------------------------------------
# S6c. Every roster character closes the CharacterModel preload surface.
#
# CharacterModel.AssetPaths derives combat visuals, icon scene, energy counter
# and card trail from the character id. BaseLib redirects each only when the
# corresponding Custom*Path override is non-null. A missing override does not
# fail at model registration: the background preloader logs a missing scene,
# then the run crashes later with an incomplete AssetCache.
#
# Scene-converted paths (visuals/rest/merchant) must also be unique. BaseLib's
# conversion registry is keyed only by path; a later registration overwrites
# the earlier target type and can turn a rest-site scene into a merchant node.
# ---------------------------------------------------------------------------
$requiredCharacterPaths = @(
    'CustomVisualPath',
    'CustomIconPath',
    'CustomEnergyCounterPath',
    'CustomTrailPath',
    'CustomRestSiteAnimPath',
    'CustomMerchantAnimPath'
)
$characterSources = @()
foreach ($f in Get-ChildItem $SourceDir -Recurse -Filter *.cs) {
    $text = Get-Content $f.FullName -Raw
    if ($text -match ':\s*CustomCharacterModel\b') {
        $characterSources += [PSCustomObject]@{
            File = $f
            Text = $text
        }
    }
}

if ($characterSources.Count -eq 0) {
    Fail 'S6c' 'no CustomCharacterModel roster classes found.'
}

$conversionOwners = @{}
foreach ($source in $characterSources) {
    foreach ($property in $requiredCharacterPaths) {
        if ($source.Text -notmatch "override\s+string\?\s+$property\b") {
            Fail 'S6c' "$($source.File.Name): missing explicit $property override; CharacterModel will preload an id-derived scene."
        }
    }

    foreach ($property in @(
            'CustomVisualPath',
            'CustomRestSiteAnimPath',
            'CustomMerchantAnimPath')) {
        $pattern = $property + '\s*=>\s*KleePck\.Path\("(?<path>[^"]+)"\)'
        $match = [regex]::Match($source.Text, $pattern)
        if (-not $match.Success) {
            Fail 'S6c' "$($source.File.Name): $property must resolve through a character-specific KleePck.Path."
            continue
        }
        $path = $match.Groups['path'].Value
        if ($conversionOwners.ContainsKey($path)) {
            Fail 'S6c' "$($source.File.Name): $property reuses conversion path '$path' already owned by $($conversionOwners[$path]). BaseLib registrations are path-keyed."
        } else {
            $conversionOwners[$path] = "$($source.File.Name).$property"
        }
    }
}

$entryPath = Join-Path $SourceDir 'KleeMod.cs'
if (-not (Test-Path $entryPath)) {
    Fail 'S6c' "mod entry point missing at $entryPath."
} else {
    $entryText = Get-Content $entryPath -Raw
    $hookCalls = [regex]::Matches(
        $entryText, '(?m)^\s*ModHelper\.SubscribeForCombatStateHooks\(')
    if ($hookCalls.Count -ne 1) {
        Fail 'S6c' "expected one combined combat-hook subscription, found $($hookCalls.Count). ModHelper rejects duplicate ids."
    }
    foreach ($listener in @(
            'KleeElementalHooks.Subscribe',
            'FurinaResourceHooks.Subscribe')) {
        if (-not $entryText.Contains($listener)) {
            Fail 'S6c' "combined combat-hook subscription omits $listener."
        }
    }
}

$pckBuilder = Join-Path $repoRoot 'tools\build_pck.ps1'
if (-not (Test-Path $pckBuilder)) {
    Fail 'S6c' "PCK builder missing at $pckBuilder."
} else {
    $pckText = Get-Content $pckBuilder -Raw
    $stagedContract = Get-ChildItem $StageDir -Filter *.pck.contract.txt -ErrorAction SilentlyContinue |
        Select-Object -First 1
    $contractText = if ($stagedContract) {
        Get-Content $stagedContract.FullName -Raw
    } else {
        ''
    }
    foreach ($source in $characterSources) {
        foreach ($match in [regex]::Matches(
                $source.Text,
                'KleePck\.Path\("(?<path>[^"]+\.(?:tscn|tres))"\)')) {
            $relative = $match.Groups['path'].Value
            $builderResource = $relative.Replace('/', '\')
            # Two authoring channels: heredoc text inside build_pck.ps1, or a
            # git-tracked source file under klee-mod\pck-src (animation sprint
            # 1 convention; the build overlays pck-src into the work dir).
            $pckSrcFile = Join-Path $repoRoot "klee-mod\pck-src\$builderResource"
            if (-not $pckText.Contains($builderResource) -and -not (Test-Path $pckSrcFile)) {
                Fail 'S6c' "$($source.File.Name): PCK resource '$builderResource' is neither authored by tools\build_pck.ps1 nor present in klee-mod\pck-src."
            }
            $contractResource = "resource=res://$relative"
            if (-not $contractText.Contains($contractResource)) {
                Fail 'S6c' "$($source.File.Name): staged PCK contract omits '$contractResource'. Rebuild the PCK."
            }
        }
    }
}

# ---------------------------------------------------------------------------
# S7. The portable repo test suite must be green before anything deploys.
#
# Lesson (2026-07-20): a compaction-narrowed "pytest tier0" habit reported
# "188 tests green" while the full suite was 236 with one failure -- a tier05
# rest-policy test stranded by the R37 ruling. Cross-tier coupling is exactly
# what full-suite discipline exists to catch, and it caught one on its first
# opportunity. This gate collects the WHOLE repo (tier0 + tier05 + tools
# tests), 1000-fight band checks included.
#
# game_ref/ is deliberately gitignored local/decompiled reference data. A
# complete copy receives its own --verify gate and participates in pytest.
#
# The fallback semantics were split on 2026-07-23 after a silent fallback
# masked a red auto-mode suite for a day (2026-07-22/23 cross-machine
# divergence). The decision table:
#
#   game_ref ABSENT entirely (fresh clone)
#       -> committed-only mode with a loud warning banner. Local-reference
#          modules skip exactly as on a fresh clone; every repository-owned
#          test still runs.
#   game_ref EXISTS but is INCOMPLETE (stale local reference)
#       -> FAIL by default, naming the missing pieces and the rebuild
#          commands. This is the dangerous case: the machine's real
#          (auto-mode) suite may be red while committed-only is green.
#          Pass -AllowIncompleteGameRef to fall back to committed-only
#          anyway, with the same loud banner.
#   game_ref COMPLETE
#       -> --verify gate, then the full suite in auto mode.
#
# Committed-only is NOT accepting a partial reference. The loader remains
# fail-closed in normal mode, and tools.build_ironclad_sheet --verify
# remains the only validity claim for real_ironclad.
# ---------------------------------------------------------------------------
function Write-GameRefBanner($reason) {
    Write-Host '===============================================================' -ForegroundColor Yellow
    Write-Host ' WARNING: S7 is running in committed-only mode.' -ForegroundColor Yellow
    Write-Host " $reason" -ForegroundColor Yellow
    Write-Host ' Local-reference modules (real_ironclad) are NOT being tested.' -ForegroundColor Yellow
    Write-Host ' A green result here says nothing about the auto-mode suite.' -ForegroundColor Yellow
    Write-Host '===============================================================' -ForegroundColor Yellow
}

if (Test-Path $venvPython) {
    $gameRef = Join-Path $repoRoot 'game_ref'
    $referenceFiles = @(
        'ironclad-cards.yaml',
        'ironclad_pool_pass4.yaml',
        'ironclad_pool_pass5.yaml',
        'ironclad_pool_pass6.yaml',
        'ironclad_pool.yaml',
        'ironclad-upgrades.yaml',
        'ironclad_char_facts.yaml',
        'char_real_ironclad.yaml'
    )
    $missingReferenceFiles = @()
    foreach ($name in $referenceFiles) {
        if (-not (Test-Path (Join-Path $gameRef $name))) {
            $missingReferenceFiles += $name
        }
    }
    $referenceComplete = ($missingReferenceFiles.Count -eq 0)

    # $null = do not run the suite at all (the incomplete-game_ref failure).
    $referenceMode = $null
    if ($referenceComplete) {
        Write-Host 'Verifying complete local game_ref...' -ForegroundColor Cyan
        $verifyOut = & $venvPython -m tools.build_ironclad_sheet --verify
        if ($LASTEXITCODE -ne 0) {
            Fail 'S7a' "complete local game_ref failed verification:`n    $($verifyOut -join "`n    ")"
        }
        $referenceMode = 'auto'
    } elseif (-not (Test-Path $gameRef)) {
        # Fresh clone: nothing local to be stale about.
        Write-GameRefBanner 'game_ref/ is absent (fresh clone).'
        $referenceMode = 'committed-only'
    } elseif ($AllowIncompleteGameRef) {
        Write-GameRefBanner "-AllowIncompleteGameRef: game_ref/ exists but is missing $($missingReferenceFiles -join ', ')."
        $referenceMode = 'committed-only'
    } else {
        # The stale-local-reference case that masked a red auto-mode suite
        # on 2026-07-22/23: a partial game_ref silently downgraded the gate
        # to committed-only and the full-suite check passed anyway.
        Fail 'S7' ("game_ref/ exists but is incomplete; missing: $($missingReferenceFiles -join ', ').`n" +
            "    The machine's real (auto-mode) suite cannot be trusted from a committed-only pass.`n" +
            "    Rebuild the local reference:`n" +
            "        python -m tools.extract_base_game_pool Ironclad --emit-sheet`n" +
            "        python -m tools.build_ironclad_sheet`n" +
            "    or re-run with -AllowIncompleteGameRef to test committed content only.")
    }

    if ($null -ne $referenceMode) {
        $oldReferenceMode = [Environment]::GetEnvironmentVariable(
            'GITS_REFERENCE_MODE', 'Process')
        $env:GITS_REFERENCE_MODE = $referenceMode

        # No 2>&1 (same PS 5.1 NativeCommandError reason as S6). -q keeps the
        # output to the summary line plus failures.
        try {
            $pytestOut = & $venvPython -m pytest $repoRoot -q
            if ($LASTEXITCODE -ne 0) {
                $tail = ($pytestOut | Select-Object -Last 25) -join "`n    "
                Fail 'S7' "portable repo suite not green (pytest exit $LASTEXITCODE):`n    $tail"
            }
        } finally {
            if ($null -eq $oldReferenceMode) {
                Remove-Item Env:GITS_REFERENCE_MODE -ErrorAction SilentlyContinue
            } else {
                $env:GITS_REFERENCE_MODE = $oldReferenceMode
            }
        }
    }
} else {
    Fail 'S7' "repo venv python not found at $venvPython; cannot run the full suite."
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
