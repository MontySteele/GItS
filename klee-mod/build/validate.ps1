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
    [switch]$AllowIncompleteGameRef,
    # C6. Run every rule EXCEPT S7's suite invocation, for the inner loop.
    # Prints a loud banner and is never what deploy.ps1 uses -- a fast mode
    # that could be mistaken for a full pass would be the R70 failure class
    # wearing the opposite coat.
    [switch]$StaticOnly
)

$ErrorActionPreference = 'Stop'
$findings = New-Object System.Collections.Generic.List[string]
function Fail($rule, $detail) { $findings.Add("[$rule] $detail") | Out-Null }

# C6 timing. The cost of this gate was attributed to the wrong rule for its
# whole life -- see the note at S3 and the S7 header -- so it is now MEASURED
# and printed rather than believed.
$swTotal = [Diagnostics.Stopwatch]::StartNew()
$suiteSeconds = 0.0

# R70 manifest version policy (MAJOR-AUTO), shared with deploy.ps1 so the
# stamp and the gate that checks it cannot compute it differently. Also
# supplies Read-JsonFile (BOM-tolerant) and ConvertTo-ComparableVersion.
. (Join-Path $PSScriptRoot 'version.ps1')

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
                # v2 -> v3 is C4 (audit sec.3.2). A v2 contract is a HAND-WRITTEN
                # list appended after the export, asserting a set of resources
                # regardless of which copy blocks actually ran; v3 is derived
                # from the files that landed in the work directory. Reading a
                # v2 contract as current would be reading an assertion as a
                # measurement, so it is stale by definition.
                if ($contractLines -notcontains 'contract=roster-pck-v3') {
                    Fail 'S2' 'PCK contract is stale; expected roster-pck-v3 (C4: derived, not hand-written). Rebuild with tools\build_pck.ps1.'
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
                $doc = Read-JsonFile $j.FullName
                if ($doc.id) { $installed[$doc.id] = $doc }
            } catch { }
        }
    }

    # R70 (audit 3.5 + 3.6). Dependency min_version, min_game_version and the
    # staged manifest version are all COMPARED here, not merely asserted
    # present. The comparisons live in version.ps1's Test-VersionPolicy so
    # they are unit-testable, which is worth doing on its own merits.
    #
    # C6 CORRECTION (Serenitea Sweep): the reason originally given for that --
    # "validate.ps1 as a whole cannot be run quickly (S7's game_ref
    # verification takes minutes)" -- was never measured and is false.
    # `tools.build_ironclad_sheet --verify` runs in 0.17s. The gate costs ~85s
    # end to end and ~80s of that is the pytest suite S7 exists to run; every
    # other rule together is ~5s. There was no stall to bound or cache: the
    # cost is the suite, and the suite is the point. What was missing was
    # attribution, so the run now prints its own timing breakdown, and
    # -StaticOnly gives the inner loop a ~5s pass that says out loud what it
    # skipped. The unit-testable design stands; only its stated rationale was
    # wrong.
    $expected = Get-PackageVersion `
        -SourceManifest (Join-Path (Split-Path -Parent $PSScriptRoot) 'Klee\manifest.json') `
        -RepoRoot (Get-RepoRoot)
    foreach ($finding in (Test-VersionPolicy `
                -Manifest $m `
                -Installed $installed `
                -GameVersion (Get-InstalledGameVersion $GameDir) `
                -Expected $expected.Version)) {
        if ($finding -like 'WARN:*') {
            Write-Host "  [S3] $($finding.Substring(5).Trim())" -ForegroundColor Yellow
        } else {
            Fail 'S3' $finding
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
        # Scan only the STRING LITERALS on the line, never the surrounding C#.
        # BBCode can only ever appear inside a literal, and scanning the raw
        # line made a dictionary-initializer KEY look like a tag: the line
        #     [Cards.FurinaRiderTips.FanfareKey + ".title"] = "Fanfare scaling"
        # passes the loc-value filter above on its `.title"]`, and then `[Cards`
        # reads as an unknown BBCode tag. That false positive has blocked every
        # deploy since 0b33ffd. Narrowing to literals keeps the gate's reach --
        # a real '[Block]' inside any loc string is still caught -- while
        # dropping a class of finding that cannot be a render bug.
        foreach ($lit in [regex]::Matches($line, '"([^"\\]*(?:\\.[^"\\]*)*)"')) {
            foreach ($mm in [regex]::Matches($lit.Groups[1].Value,
                                             '\[/?([A-Za-z_][A-Za-z0-9_]*)')) {
                $tag = $mm.Groups[1].Value
                if ($knownTags -notcontains $tag.ToLower()) {
                    Fail 'S5' "$($f.Name):$n uses '[$tag]', which is not a known BBCode tag. If it is a variable write {$tag}; an unknown tag throws at render time."
                }
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

# Native stderr under Windows PowerShell 5.1 is a trap in BOTH directions, and
# the note that used to sit at S6 only covered one of them.
#
#   * Redirecting with 2>&1 while ErrorActionPreference is 'Stop' wraps every
#     stderr line in an ErrorRecord and throws NativeCommandError. That is why
#     the original code deliberately did not redirect.
#   * But NOT redirecting is not safe either: with EAP 'Stop', any native
#     stderr output raises NativeCommandError EVEN WHEN THE COMMAND EXITS 0.
#
# The second half is what broke this file on 2026-07-25. lint_constant_parity
# grew a reader that imports tier05.relics, which emits three house-rule
# UserWarnings on stderr at import; the lint PASSED, printed
# "constant parity: OK", and took the entire deploy down anyway. A gate that
# fails on a dependency's warning is not measuring what it claims to measure.
#
# Lowering EAP to 'Continue' for the duration of the call makes stderr behave
# like output rather than like an exception, so 2>&1 is then safe -- and we get
# to keep the diagnostics for the failure message instead of discarding them
# to $null. $LASTEXITCODE is a global automatic and survives the call, so
# callers check it exactly as before.
function Invoke-RepoPython {
    param([Parameter(Mandatory = $true, ValueFromRemainingArguments = $true)]
          [string[]]$Arguments)
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        & $venvPython @Arguments 2>&1
    } finally {
        $ErrorActionPreference = $prev
    }
}

$parityLint = Join-Path $repoRoot 'tools\lint_handwritten_parity.py'
if (-not (Test-Path $venvPython)) {
    Fail 'S6' "repo venv python not found at $venvPython; cannot run hand-written parity lint."
} elseif (-not (Test-Path $parityLint)) {
    Fail 'S6' "tools/lint_handwritten_parity.py is missing."
} else {
    $parityOut = Invoke-RepoPython $parityLint
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
    $codegenOut = Invoke-RepoPython $rosterCodegen --check
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
    $poolOut = Invoke-RepoPython $poolLint
    if ($LASTEXITCODE -ne 0) {
        Fail 'S6b' "pool membership lint failed:`n    $($poolOut -join "`n    ")"
    }
}

# ---------------------------------------------------------------------------
# S6d. Every roster character ships at least one Ancient-rarity pool card.
#
# Playtest 2026-07-23: the Darv ancient event rolls Dusty Tome ~50% of the
# time, and vanilla DustyTome.SetupForPlayer draws a random Ancient card from
# the character's pool -- an empty draw NREs inside the event's option
# generation and the run softlocks on entering the room. The ledger is
# KleeCode/RosterAncientCards.cs; the lint also proves each pool actually
# concats it and that no ledger card is off-pool filtered.
# ---------------------------------------------------------------------------
$ancientLint = Join-Path $repoRoot 'tools\lint_ancient_coverage.py'
if (-not (Test-Path $venvPython)) {
    Fail 'S6d' "repo venv python not found at $venvPython; cannot run ancient coverage lint."
} elseif (-not (Test-Path $ancientLint)) {
    Fail 'S6d' "tools/lint_ancient_coverage.py is missing."
} else {
    $ancientOut = Invoke-RepoPython $ancientLint
    if ($LASTEXITCODE -ne 0) {
        Fail 'S6d' "ancient coverage lint failed:`n    $($ancientOut -join "`n    ")"
    }
}

# ---------------------------------------------------------------------------
# S6e. Every mirrored balance constant matches tier0.
#
# Each balance number lives twice: once in tier0 where it was MEASURED, once
# in C# where it is PLAYED. The C# copies carry doc comments swearing they
# mirror the sim, and until 2026-07-25 that promise was kept by discipline
# alone. A sim-side retune nobody mirrors ships a mod playing to numbers no
# simulation endorsed, and it does so silently -- green build, green tests,
# and a tuning report describing a game nobody is playing.
#
# There is no C# test project to pin this at runtime, so the lint is the
# static form: every `public const int` must be classified MIRRORED (compared
# by value against tier0) or UNMIRRORED (with a written reason). Unclassified
# is a failure, not a skip.
# ---------------------------------------------------------------------------
$constLint = Join-Path $repoRoot 'tools\lint_constant_parity.py'
if (-not (Test-Path $venvPython)) {
    Fail 'S6e' "repo venv python not found at $venvPython; cannot run constant parity lint."
} elseif (-not (Test-Path $constLint)) {
    Fail 'S6e' "tools/lint_constant_parity.py is missing."
} else {
    $constOut = Invoke-RepoPython $constLint
    if ($LASTEXITCODE -ne 0) {
        Fail 'S6e' "constant parity lint failed:`n    $($constOut -join "`n    ")"
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
        $verifyOut = Invoke-RepoPython -m tools.build_ironclad_sheet --verify
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

    if ($StaticOnly) {
        Write-Host '===============================================================' -ForegroundColor Yellow
        Write-Host ' -StaticOnly: S7 DID NOT RUN THE SUITE.' -ForegroundColor Yellow
        Write-Host ' Every other rule ran. This is an inner-loop pass and says' -ForegroundColor Yellow
        Write-Host ' NOTHING about whether the repo tests are green.' -ForegroundColor Yellow
        Write-Host ' deploy.ps1 never passes this switch.' -ForegroundColor Yellow
        Write-Host '===============================================================' -ForegroundColor Yellow
        $referenceMode = $null
    }
    if ($null -ne $referenceMode) {
        $swSuite = [Diagnostics.Stopwatch]::StartNew()
        $oldReferenceMode = [Environment]::GetEnvironmentVariable(
            'GITS_REFERENCE_MODE', 'Process')
        $env:GITS_REFERENCE_MODE = $referenceMode

        # Invoke-RepoPython DOES redirect 2>&1 -- safely, because it drops
        # ErrorActionPreference to 'Continue' for the duration of the call.
        # (This comment used to say "No 2>&1", directly above a helper that
        # does exactly that: it was written for the bare call site the helper
        # replaced and was never updated. Audit sec.3.4.) -q keeps the output
        # to the summary line plus failures.
        try {
            $pytestOut = Invoke-RepoPython -m pytest $repoRoot -q
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
            $swSuite.Stop()
            $suiteSeconds = $swSuite.Elapsed.TotalSeconds
        }
    }
} elseif (-not $StaticOnly) {
    Fail 'S7' "repo venv python not found at $venvPython; cannot run the full suite."
}

# ---------------------------------------------------------------------------
# S9. Every roster character's card art actually reaches the package.
#
# deploy.ps1 stages art from a HARDCODED list of source directories into one
# flat images/cards. A character missing from that array fails nothing: the
# build is green, every other gate is green, the mod loads, and their cards
# simply render with no portrait. Kokomi shipped exactly that way on
# 2026-07-25 -- 58 painted faces sat in ImageGen and not one reached the game.
#
# Checked against the STAGE rather than the source list, so it verifies the
# outcome instead of restating the config.
#
# C2 (audit sec.3.3), two repairs:
#
#  * The guard was `Test-Path $stagedArt`, and deploy.ps1 only CREATES that
#    directory when it finds sources -- so the one case this rule exists for,
#    art missing entirely from the package, made the missing-art gate silent.
#    A gate whose precondition is the defect is not a gate. Now: if art exists
#    upstream and the stage has none, that is the finding.
#  * It probed ONE portrait per character and broke on the first hit, which
#    proves a directory was wired and nothing else. No gate anywhere asserted
#    per-card completeness -- art_coverage.py's test deliberately does not,
#    because it bills against the sheets rather than against the package. So
#    the break is gone and every painted portrait must reach the stage. The
#    failure names counts and examples, not just the first miss.
# ---------------------------------------------------------------------------
# ImageGen lives at the REPO root, not under klee-mod. Getting this wrong makes
# Test-Path false and silently skips the whole rule -- which it did on the first
# attempt, and the negative test caught it. $repoRoot is defined at S6.
$cardsRoot = Join-Path $repoRoot 'ImageGen\images\cards'
$stagedArt = Join-Path $StageDir 'images\cards'
if (Test-Path $cardsRoot) {
    $sourcePngs = @(Get-ChildItem $cardsRoot -Recurse -Filter *.png -ErrorAction SilentlyContinue)
    if ($sourcePngs.Count -gt 0 -and -not (Test-Path $stagedArt)) {
        # The inversion. deploy.ps1 creates images\cards only when it finds
        # sources, so "no staged art directory at all" used to skip this rule
        # entirely -- silence in exactly the case it was written for.
        Fail 'S9' ("ImageGen\images\cards holds $($sourcePngs.Count) portrait(s) " +
            "and the staged package has no images\cards directory at all. " +
            "Every card in the game will render with no art.")
    } elseif ($sourcePngs.Count -gt 0) {
        $staged = @{}
        foreach ($f in Get-ChildItem $stagedArt -Filter *.png -ErrorAction SilentlyContinue) {
            $staged[$f.Name] = $true
        }
        foreach ($charDir in Get-ChildItem $cardsRoot -Directory -ErrorAction SilentlyContinue) {
            $pngs = @(Get-ChildItem $charDir.FullName -Filter *.png -ErrorAction SilentlyContinue)
            if ($pngs.Count -eq 0) { continue }   # nothing painted yet is not a defect
            $missing = @($pngs | Where-Object { -not $staged.ContainsKey($_.Name) })
            if ($missing.Count -eq $pngs.Count) {
                Fail 'S9' ("ImageGen\images\cards\$($charDir.Name) holds $($pngs.Count) " +
                    "portrait(s) and NONE of them are in the staged package. That " +
                    "directory is missing from deploy.ps1's `$artSrcDirs -- their " +
                    "cards will render with no art and nothing else will complain.")
            } elseif ($missing.Count -gt 0) {
                # The half no gate covered: the directory IS wired, and some of
                # its portraits still did not land. A per-file copy filter, a
                # name collision in the flat stage, or a partial copy all look
                # like this, and all of them ship blank cards.
                $sample = ($missing | Select-Object -First 5 |
                    ForEach-Object { $_.Name }) -join ', '
                Fail 'S9' ("ImageGen\images\cards\$($charDir.Name): " +
                    "$($missing.Count) of $($pngs.Count) portrait(s) did not reach " +
                    "the staged package (e.g. $sample). Those cards render blank.")
            }
        }
    }
}

# ---------------------------------------------------------------------------
# S8. Build scripts are pure ASCII.
#
# Every .ps1 in this repo says so in its own header, and the rule was still
# broken -- Furina's Architect finale line carried an em-dash, and because
# Windows PowerShell 5.1 reads a BOM-less .ps1 as ANSI, the UTF-8 bytes were
# decoded as cp1252 and re-encoded as UTF-8 on the way into the pck. The line
# shipped reading "Now a<euro>" the people rejoice" on the WIN SCREEN, which
# is the last text a player sees after beating Act 3. Caught 2026-07-25 by
# reading the built json, not by any gate.
#
# The failure is silent by construction: the mangling happens at PARSE time,
# so nothing downstream can tell a mojibake string from an intended one. The
# only place to catch it is the bytes on disk, here.
#
# A line may opt out with the marker below when a non-ASCII byte is the
# POINT (validate.ps1's own literal-BOM regex is the one case today).
# ---------------------------------------------------------------------------
$asciiExempt = '# ascii-exempt:'
# C1 (audit sec.3.1): this walked $SourceDir (= KleeCode), which contains ZERO
# .ps1 files -- all three live in klee-mod\build\ and tools\. The loop found
# nothing and the rule passed, every run, since the day it was written. The
# mojibake class it exists for (build_pck.ps1's heredoc strings, which are the
# ONLY place this repo writes game-visible text from PowerShell) was never
# checked at all.
#
# Scanned from the repo root instead of from a list of directories, because a
# list is the same defect one level up: a .ps1 added somewhere new would be
# unchecked and nothing would say so. Excludes are for trees that are not ours
# -- .venv ships Activate.ps1, which is not this repo's to keep ASCII.
$asciiSkip = @('*\.venv\*', '*\dist\*', '*\obj\*', '*\bin\*',
               '*\pck-work\*', '*\node_modules\*')
$ps1Files = @(Get-ChildItem $repoRoot -Recurse -Filter *.ps1 -ErrorAction SilentlyContinue |
    Where-Object { $p = $_.FullName; -not ($asciiSkip | Where-Object { $p -like $_ }) })
if ($ps1Files.Count -eq 0) {
    Fail 'S8' ("found no .ps1 files under $repoRoot to check. This rule scanned " +
        "a directory with none in it for its entire life; an empty sweep is " +
        "the failure mode, not a pass.")
}
foreach ($script in $ps1Files) {
    $lineNo = 0
    foreach ($line in [IO.File]::ReadAllLines($script.FullName)) {
        $lineNo++
        if ($line -match $asciiExempt) { continue }
        $offenders = [char[]]$line | Where-Object { [int]$_ -gt 127 }
        if ($offenders.Count -gt 0) {
            $codes = ($offenders | ForEach-Object { 'U+{0:X4}' -f [int]$_ }) -join ', '
            Fail 'S8' ("$($script.Name):$lineNo has non-ASCII characters ($codes). " +
                "PowerShell 5.1 reads a BOM-less .ps1 as ANSI, so these are decoded as " +
                "cp1252 and ship as mojibake wherever the string lands. Use ASCII, or " +
                "mark the line '$asciiExempt <reason>' if the byte is deliberate.")
        }
    }
}

# ---------------------------------------------------------------------------
# S10. The art lint runs.
#
# C3 (audit sec.3.7). `tools/art_lint.py` is the largest lint in the repo -- 12
# rules over the whole card-art plan -- and it was wired into no validate rule
# and no test. It ran when somebody typed its name, which meant it ran during
# art passes and never afterwards. The sprint log's L11 "verified by negative
# test" claim referred to a test that did not exist.
#
# Dual-wired, the same argument test_sheet_lints.py makes for its own family:
# pytest covers it for anyone on any platform (tier0/tests/test_art_lint_full_set.py),
# and this rule covers the deploy, because the deploy is the moment the art
# actually ships and pytest is not what gates it.
#
# Its inputs (art/plan.tsv, ImageGen/images) are gitignored Tier F, so on a
# machine without them the tool lints an empty plan and exits 0. That is the
# correct behaviour here and not a silent skip: this rule asks "is the art
# plan self-consistent", while "did the art ship" is S9's question, and S9
# now fails loudly on exactly that case.
# ---------------------------------------------------------------------------
$artLint = Join-Path $repoRoot 'tools\art_lint.py'
if (-not (Test-Path $venvPython)) {
    Fail 'S10' "repo venv python not found at $venvPython; cannot run the art lint."
} elseif (-not (Test-Path $artLint)) {
    Fail 'S10' "tools/art_lint.py is missing."
} else {
    $artOut = Invoke-RepoPython $artLint
    if ($LASTEXITCODE -ne 0) {
        Fail 'S10' "art lint failed:`n    $($artOut -join "`n    ")"
    }
}

# ---------------------------------------------------------------------------
# S11. Every roster site knows every registered character.
#
# F1 (audit sec.5). Adding character #4 touches roughly 26 scattered edit sites,
# 4 gated and 22 SILENT. Silent is the defect: the mod builds, the suite is
# green, every other lint passes, and the character is simply absent from
# whichever list was missed. It has happened twice already -- Kokomi's
# archetype registry named three tags that existed on zero cards (R66, and
# every adaptive number ever taken for her went through it), and her card art
# was never staged because deploy.ps1's array did not list her.
#
# tier0/roster.py declares the roster once; this sweeps every site for every
# registered character. It is the S6c pattern -- a closed list a lint holds
# shut -- extended from one rule to the whole roster surface, and it is the
# PRE-ZHONGLI GATE: slot 4 does not open until a character can be declared in
# one place and have every consumer either read it or fail loudly.
# ---------------------------------------------------------------------------
$rosterLint = Join-Path $repoRoot 'tools\lint_roster_registry.py'
if (-not (Test-Path $venvPython)) {
    Fail 'S11' "repo venv python not found at $venvPython; cannot run the roster registry lint."
} elseif (-not (Test-Path $rosterLint)) {
    Fail 'S11' "tools/lint_roster_registry.py is missing."
} else {
    $rosterOut = Invoke-RepoPython $rosterLint
    if ($LASTEXITCODE -ne 0) {
        Fail 'S11' "roster registry lint failed:`n    $($rosterOut -join "`n    ")"
    }
}

# ---------------------------------------------------------------------------
# S12. Every pck resource C# references is actually IN the pack.
#
# Kokomi playtest, 2026-07-26. Her starter relic renders the base-game
# placeholder icon and her Burst gauge has no cap icon, because
# kokomi/relics/pearl_of_wisdom.png and kokomi/powers/pearl.png do not exist.
# The game had been logging both misses once per session, all along, and no
# gate said a word.
#
# S6c is the rule that was supposed to be this. It is scoped twice over and
# neither scope is the interesting one:
#
#   * it inspects only classes matching ': CustomCharacterModel' -- so every
#     relic, power, VFX and gauge reference is invisible to it, and
#   * it matches only '\.(tscn|tres)' -- so no PNG has ever been checked by
#     anything, in any rule, since the pck existed.
#
# Both scopes were reasonable when S6c was written (it is a CHARACTER preload
# rule) and neither was ever widened when the pck grew relics, power icons and
# gauge skins. So the sweep is separate rather than a widening of S6c: that
# rule answers "does each character preload a real scene", this one answers
# "does every pck path in the mod resolve", and collapsing them would leave one
# rule with two jobs and the weaker error message for both.
#
# Namespaces are DERIVED from the contract rather than listed, so a new
# top-level directory in the pack is swept the day it appears.
#
# KNOWN LIMIT, stated rather than papered over: paths built by concatenation
# are not matched -- today that is exactly one, KleePowerIcons' per-element
# 'klee/powers/aura_<element>.png'. KleeSelfCheck R13 already asserts at boot
# that every power's icon path resolves in the merged pck, which covers that
# family and is the reason this rule does not try to evaluate C# expressions.
# ---------------------------------------------------------------------------

# Referenced on purpose, art deliberately not made yet. An entry here is a
# PROMISE that the miss is known and degrades safely, not a way to silence the
# rule. Checked in both directions below.
$pckDeferred = @{
    'kokomi/relics/pearl_of_wisdom.png' =
        'Kokomi art pass scoped her cards + the eight non-card surfaces; the ' +
        'relic icon was deliberately left for a manual crop with eyes on it ' +
        '(docs/kokomi-art-pass-requirements.md). Degrades via ?? base.PackedIconPath.'
    'kokomi/powers/pearl.png' =
        'Burst gauge cap icon, same pass, same scope decision. GaugeBridge ' +
        'routes it through KleePck.Path, so a miss renders no cap icon.'
}

$stagedContractS12 = Get-ChildItem $StageDir -Filter *.pck.contract.txt -ErrorAction SilentlyContinue |
    Select-Object -First 1
if (-not $stagedContractS12) {
    Fail 'S12' "no staged pck contract; cannot verify pck references. Rebuild with tools\build_pck.ps1."
} else {
    $packed = @{}
    $namespaces = @{}
    foreach ($line in Get-Content $stagedContractS12.FullName) {
        if ($line -like 'resource=res://*') {
            $rel = $line.Substring('resource=res://'.Length)
            $packed[$rel] = $true
            $head = $rel.Split('/')[0]
            if ($rel.Contains('/')) { $namespaces[$head] = $true }
        }
    }
    if ($namespaces.Count -eq 0) {
        Fail 'S12' "staged contract declares no namespaced resources; it is empty or malformed."
    } else {
        $nsAlt = ($namespaces.Keys | Sort-Object) -join '|'
        $refPattern = '"(?<path>(?:' + $nsAlt + ')/[^"]+\.(?:png|tscn|tres|ogg|wav))"'

        # Files whose resource strings are PROBES, not requests. Excluded with
        # the reason, because reading them as requests inverts what they say.
        #
        # KleeSceneTelemetry's ConventionScenes list exists to report which
        # convention scenes are absent -- it carries "kokomi/model/combat.tscn"
        # precisely BECAUSE that scene is expected missing, and it logs the
        # miss at boot. Feeding that list to a must-be-packed rule would turn
        # a deliberate absence report into a build failure.
        $s12ProbeFiles = @('KleeSceneTelemetry.cs')

        $refs = @{}
        foreach ($f in Get-ChildItem $SourceDir -Recurse -Filter *.cs) {
            if ($s12ProbeFiles -contains $f.Name) { continue }
            # Comment-only lines are dropped before matching: KleePck's own
            # doc comment spells the contract with a "klee/ui/foo.png" example,
            # and an example is not a reference. Dropping WHOLE comment lines
            # rather than everything after '//' is deliberate -- a real path
            # literal contains "res://", so a naive strip would eat the
            # references this rule exists to find.
            $lines = [IO.File]::ReadAllLines($f.FullName) | Where-Object {
                $t = $_.TrimStart()
                -not ($t.StartsWith('//') -or $t.StartsWith('*'))
            }
            $text = $lines -join "`n"
            foreach ($m in [regex]::Matches($text, $refPattern)) {
                $rel = $m.Groups['path'].Value
                if (-not $refs.ContainsKey($rel)) { $refs[$rel] = @() }
                if ($refs[$rel] -notcontains $f.Name) { $refs[$rel] += $f.Name }
            }
        }
        if ($refs.Count -eq 0) {
            Fail 'S12' ("found no pck resource references in $SourceDir. The mod " +
                "references dozens; an empty sweep is the failure mode, not a pass.")
        }
        foreach ($rel in ($refs.Keys | Sort-Object)) {
            if ($packed.ContainsKey($rel)) { continue }
            if ($pckDeferred.ContainsKey($rel)) { continue }
            $who = ($refs[$rel] | Sort-Object) -join ', '
            Fail 'S12' ("$who references res://$rel, which is NOT in the staged pck. " +
                "Either the art is missing (make it, or add it to `$pckDeferred with " +
                "the reason) or a copy block in tools\build_pck.ps1 did not run -- " +
                "that script now reports its skips at the end of a build.")
        }
        # Both directions. A deferred entry that has landed, or that nothing
        # references any more, is a stale exemption, and a stale exemption is
        # how the next missing asset gets waved through.
        foreach ($rel in ($pckDeferred.Keys | Sort-Object)) {
            if ($packed.ContainsKey($rel)) {
                Fail 'S12' ("res://$rel is in `$pckDeferred but IS now in the pck. " +
                    "The art landed; drop the exemption.")
            } elseif (-not $refs.ContainsKey($rel)) {
                Fail 'S12' ("res://$rel is in `$pckDeferred but no C# file references " +
                    "it any more. Drop the exemption.")
            }
        }
    }
}

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
$swTotal.Stop()
# C6: attribution, printed every run. The comment at S3 spent its life blaming
# the game_ref verification (0.17s) for a cost that is ~95% the pytest suite.
# A number nobody prints is a number somebody will guess.
$totalS = $swTotal.Elapsed.TotalSeconds
Write-Host ("timing: total {0:N1}s  (S7 suite {1:N1}s, all other rules {2:N1}s)" -f `
    $totalS, $suiteSeconds, ($totalS - $suiteSeconds)) -ForegroundColor DarkGray

if ($findings.Count -eq 0) {
    if ($StaticOnly) {
        Write-Host "validate: OK (STATIC ONLY -- the suite did not run)" -ForegroundColor Yellow
    } else {
        Write-Host "validate: OK" -ForegroundColor Green
    }
    exit 0
}

Write-Host "validate: $($findings.Count) finding(s)" -ForegroundColor Red
foreach ($f in $findings) { Write-Host "  $f" -ForegroundColor Red }
throw "Validation failed; refusing to deploy."
