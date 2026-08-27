<#
  Manifest version policy (R70, 2026-07-26; shape AMENDED by R214,
  2026-08-27). Dot-sourced by deploy.ps1 and validate.ps1 so the two cannot
  compute the version differently -- which is the whole point of a gate that
  compares one against the other.

  THE VERSION IS TWO PARTS: MAJOR.AUTO.

  R214 AMENDED THE SEPARATOR, and only the separator. The old shape was
  MAJOR-AUTO ("0.2-1159"), which is not a valid semantic version: the game's
  own parser walks the string and throws the moment it reaches a '-' while
  still in Minor (SemanticVersion.cs:102-107). Our parsed version was left
  null, so ModManager refuses any future mod declaring a min_version on us
  (ModManager.cs:810-812), and every player's log carried the warning. AUTO
  is now the PATCH component -- "0.2.1159" -- which parses, sorts
  monotonically, and keeps MAJOR two-part and deliberate.

  MAJOR ("0.2") lives in Klee\manifest.json and is bumped DELIBERATELY, by the
  user, as part of a release sprint's close-out. It is a ratified artifact like
  a sheet. No tool touches it.

  AUTO is generated at deploy time as the repo's commit count
  (git rev-list --count HEAD). Three properties earn it the job:

    stateless    nothing has to be stored, incremented, or remembered;
    monotonic    it only ever goes up;
    comparable   two co-op players can see not just THAT their versions
                 differ but WHO IS BEHIND -- the diagnostic that matters for
                 deterministic-lockstep desyncs, and the one a timestamp or a
                 random build id cannot give.

  A dirty working tree appends "+dirty" -- now as semver BUILD METADATA
  ("0.2.1159+dirty"), which parses and which the game's comparator ignores,
  rather than as part of a prerelease. A +dirty build is never handed to a
  co-op partner: the commit count no longer identifies its contents, so two
  zips can share a name and differ.

  WHY THIS EXISTS. manifest.json had one commit ever. Everything since --
  Kokomi's shell and three sprints -- shipped as "0.2.0", and deploy silently
  overwrote the previous zip of the same name. For lockstep co-op that is
  precisely the failure the version field exists to prevent.

  NOTE: keep this file pure ASCII. Windows PowerShell 5.1 reads .ps1 as ANSI
  unless there's a BOM, so smart quotes and em-dashes break the parser. That
  is also why the BOM-stripping regex below spells U+FEFF as an escape rather
  than embedding the character.
#>

# A BOM survives Get-Content -Raw in PS 5.1 and ConvertFrom-Json chokes on it.
# Match it whether it decoded to U+FEFF or was misread as ANSI ("\xEF\xBB\xBF").
$script:BomPattern = "^(\xEF\xBB\xBF|\uFEFF)"

function Get-RepoRoot {
    # build\ -> klee-mod\ -> repo root
    Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
}

function Read-JsonFile {
    param([string]$Path)
    $raw = (Get-Content $Path -Raw) -replace $script:BomPattern, ''
    return $raw | ConvertFrom-Json
}

function Get-ManifestMajor {
    <#
      The deliberate half, read from the SOURCE manifest (not the staged
      copy, which already carries MAJOR.AUTO and would compound).
    #>
    param([string]$SourceManifest)
    if (-not (Test-Path $SourceManifest)) {
        throw "source manifest not found: $SourceManifest"
    }
    $major = (Read-JsonFile $SourceManifest).version
    if ([string]::IsNullOrWhiteSpace($major)) {
        throw "manifest.json has no version; MAJOR is a ratified artifact and must be set by hand."
    }
    # R214: MAJOR is exactly two dotted integers. Before the amendment the
    # AUTO part was separated by '-', so a leaked AUTO was caught by looking
    # for a dash; now that AUTO is a third dotted component, a shape check is
    # the only thing that can still tell "0.2" from "0.2.1159" or "0.2-1159".
    if ($major -notmatch '^\d+\.\d+$') {
        throw "manifest.json version '$major' is not a bare MAJOR. MAJOR is the deliberate half only, exactly two dotted integers (e.g. '0.2'); AUTO is generated at deploy time and appended as the patch component."
    }
    return $major
}

function Get-AutoVersion {
    <#
      Commit count, plus "+dirty" when the working tree has uncommitted
      changes. Returns Auto / IsDirty / DirtyFiles.
    #>
    param([string]$RepoRoot)

    Push-Location $RepoRoot
    try {
        # Do NOT redirect native stderr here. PS 5.1 wraps each stderr line in
        # a NativeCommandError under $ErrorActionPreference='Stop' and would
        # kill the build over a git warning -- the same trap still live in
        # build_pck.ps1 (audit 3.4).
        $count = & git rev-list --count HEAD
        if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($count)) {
            throw "git rev-list --count HEAD failed in $RepoRoot. The AUTO version cannot be computed outside a git checkout."
        }
        $count = "$count".Trim()

        $status = @(& git status --porcelain)
        if ($LASTEXITCODE -ne 0) {
            throw "git status --porcelain failed in $RepoRoot."
        }
        $dirtyFiles = @($status | Where-Object { $_ -and "$_".Trim() })
    } finally {
        Pop-Location
    }

    $isDirty = $dirtyFiles.Count -gt 0
    $auto = if ($isDirty) { "$count+dirty" } else { $count }
    return @{
        Auto       = $auto
        Count      = $count
        IsDirty    = $isDirty
        DirtyFiles = $dirtyFiles
    }
}

function Get-PackageVersion {
    <#
      The full MAJOR.AUTO string, plus the parts that produced it.

      -Prototype STAMPS A DEV BUILD, on the SAME semver build-metadata
      channel R214 already uses for +dirty. The game's parser ignores
      everything after the '+', so a marked package is still a parseable
      version and still refuses no dependent mod. What the mark buys is that
      a dev package is IDENTIFIABLE ON SIGHT in the version string the game
      shows -- which matters precisely because deploy_proto.ps1 writes to the
      same mods\klee directory the release path writes to, so without it
      "which build is installed right now" is a question with no answer
      anywhere on screen.

        plain           0.2.1209
        dirty           0.2.1209+dirty          (R214, byte-unchanged)
        prototype       0.2.1209+proto
        both            0.2.1209+proto.dirty

      proto before dirty because the token that says WHAT WAS BUILT is more
      load-bearing than the one that says the tree moved. Composed from
      Count/IsDirty rather than from Auto so the non-prototype string stays
      exactly what it was before this switch existed.

      THIS EXTENDS R214'S USE OF BUILD METADATA AND IS FLAGGED FOR THE NEXT
      RULING: R214 ruled MAJOR.AUTO with +dirty, and +proto is a second token
      on that channel serving a build shape R214 did not contemplate.
    #>
    param([string]$SourceManifest, [string]$RepoRoot, [switch]$Prototype)
    $major = Get-ManifestMajor -SourceManifest $SourceManifest
    $auto = Get-AutoVersion -RepoRoot $RepoRoot
    if ($Prototype) {
        $meta = @('proto')
        if ($auto.IsDirty) { $meta += 'dirty' }
        $autoText = "$($auto.Count)+$($meta -join '.')"
    } else {
        $autoText = $auto.Auto
    }
    return @{
        Version     = "$major.$autoText"
        Major       = $major
        Auto        = $autoText
        IsPrototype = [bool]$Prototype
        IsDirty     = $auto.IsDirty
        DirtyFiles  = $auto.DirtyFiles
    }
}

function ConvertTo-ComparableVersion {
    <#
      "v3.3.8" / "3.3.6" / "0.107.1" -> [version], for real >= comparisons.

      Returns $null when the string is not a dotted version, so callers can
      report "unparseable" rather than treating it as satisfied. Asserting
      presence and measuring nothing is the defect being fixed here (audit
      3.5); a comparison that quietly passes on garbage is the same defect
      wearing a comparison's clothes.
    #>
    param([string]$Text)
    if ([string]::IsNullOrWhiteSpace($Text)) { return $null }
    $t = "$Text".Trim()
    if ($t.StartsWith('v') -or $t.StartsWith('V')) { $t = $t.Substring(1) }
    # Keep only the leading dotted numerics: "0.107.1-rc2" -> "0.107.1".
    if ($t -notmatch '^\d+(\.\d+)*') { return $null }
    $t = $Matches[0]
    # [version] needs at least two parts; "3" alone is not a version.
    if ($t -notmatch '\.') { $t = "$t.0" }
    try { return [version]$t } catch { return $null }
}

function Test-VersionPolicy {
    <#
      The S3 version comparisons, as a function returning finding strings.

      validate.ps1 calls this and pipes the result into Fail, so this IS the
      gate rather than a description of it -- the tests exercise the shipped
      code path. It lives here rather than inline in validate.ps1 so it can be
      unit-tested, which is worth doing on its own merits.

      C6 CORRECTION, carried here 2026-07-27 (Sweep II). The reason originally
      given for extracting it -- "validate.ps1 cannot be run quickly: its S7
      game_ref verification takes minutes" -- was never measured and is false.
      That verification is 0.17s of an 84.0s gate (0.2%); the cost is the
      pytest suite S7 exists to run, ~78s, and every other rule together is
      ~5.5s. Sweep-I C6 deleted this claim from validate.ps1 and replaced it
      with the measured numbers, but the same sentence survived HERE, in the
      file the extraction produced -- a corrected claim and its uncorrected
      twin, one file apart. Found while running the gate during Sweep II and
      fixed under D4, which requires a quantitative claim used as rationale to
      carry a measurement or be marked UNMEASURED.

      Parameters are already-parsed objects so the caller owns all I/O:
        Manifest    the STAGED manifest (PSCustomObject)
        Installed   hashtable of dependency id -> parsed manifest object
        GameVersion the game's version string, or $null if unreadable
        Expected    the MAJOR.AUTO string this checkout computes

      AllowPrototypeMetadata is the DEV-BUILD gate and it is off by default,
      which is the whole point: the +proto token is legal in exactly one
      place, the package deploy_proto.ps1 stamped, and this switch is the
      only way to say so. The release path never passes it, so a +proto
      package reaching validate.ps1 without it is refused BY NAME rather than
      by the Expected-mismatch rule below -- a named refusal says what
      happened, and "0.2.1209+proto is not 0.2.1209" does not.
    #>
    param(
        [Parameter(Mandatory = $true)]$Manifest,
        [Parameter(Mandatory = $true)][hashtable]$Installed,
        [AllowNull()][string]$GameVersion,
        [Parameter(Mandatory = $true)][string]$Expected,
        [switch]$AllowPrototypeMetadata
    )
    $out = New-Object System.Collections.Generic.List[string]

    # R70 (audit 3.5): these pins used to assert PRESENCE and measure
    # nothing. min_version 3.3.6 was compared to exactly nothing, so a
    # too-old BaseLib passed the gate and failed at boot instead.
    foreach ($dep in @($Manifest.dependencies)) {
        if (-not $dep) { continue }
        if (-not $Installed.ContainsKey($dep.id)) {
            $out.Add("declared dependency '$($dep.id)' is not installed; the game will skip this mod entirely. Found: $($Installed.Keys -join ', ')")
            continue
        }
        if ([string]::IsNullOrWhiteSpace($dep.min_version)) { continue }
        $want = ConvertTo-ComparableVersion $dep.min_version
        $have = ConvertTo-ComparableVersion $Installed[$dep.id].version
        if (-not $want) {
            $out.Add("dependency '$($dep.id)' declares an unparseable min_version '$($dep.min_version)'.")
        } elseif (-not $have) {
            $out.Add("installed '$($dep.id)' reports an unparseable version '$($Installed[$dep.id].version)'; cannot verify min_version $($dep.min_version).")
        } elseif ($have -lt $want) {
            $out.Add("installed '$($dep.id)' is $($Installed[$dep.id].version) but the manifest requires >= $($dep.min_version). The game's dependency gate will skip this mod.")
        }
    }

    # min_game_version, against release_info.json.
    if (-not [string]::IsNullOrWhiteSpace($Manifest.min_game_version)) {
        $wantGame = ConvertTo-ComparableVersion $Manifest.min_game_version
        $haveGame = ConvertTo-ComparableVersion $GameVersion
        if (-not $wantGame) {
            $out.Add("manifest declares an unparseable min_game_version '$($Manifest.min_game_version)'.")
        } elseif (-not $haveGame) {
            # Deliberately NOT a finding: a build machine may legitimately
            # have no release_info.json. Reported by the caller instead, so
            # "not verified" never reads as "verified".
            $out.Add("WARN: game version unknown (no readable release_info.json); min_game_version $($Manifest.min_game_version) NOT verified.")
        } elseif ($haveGame -lt $wantGame) {
            $out.Add("installed game is $GameVersion but the manifest requires >= $($Manifest.min_game_version).")
        }
    }

    # R214. The staged version must be a valid semantic version. The game
    # parses it and keeps the parsed object; a version it cannot parse is
    # left null, and a null version refuses every dependent mod that declares
    # a min_version on us (ModManager.cs:810-812). This is the assertion the
    # old MAJOR-AUTO shape would have failed on every build.
    if ($Manifest.version -notmatch '^\d+\.\d+\.\d+(\+[0-9A-Za-z.-]+)?$') {
        $out.Add("staged manifest version '$($Manifest.version)' is not a valid semantic version (R214: MAJOR.AUTO, with +dirty as build metadata). The game's parser leaves an unparseable version null and then refuses any dependent mod declaring a min_version on us.")
    }

    # The +proto token is legal ONLY from the dev deploy path. R213 B's
    # quarantine is a claim about what a RELEASE package contains, and a
    # release package carrying a dev mark either was built by the dev script
    # (so the quarantine claim is false) or was hand-edited (so the stamp is
    # not evidence of anything). Both are the same finding.
    if (-not $AllowPrototypeMetadata -and $Manifest.version -match '\+proto') {
        $out.Add("staged manifest version '$($Manifest.version)' carries the +proto build metadata, which only klee-mod/build/deploy_proto.ps1 may stamp. The release path must not ship a package built with the quarantined prototype surface compiled in (R213 B).")
    }
    if ($AllowPrototypeMetadata -and $Manifest.version -notmatch '\+proto') {
        $out.Add("the prototype validate was asked for but the staged manifest version '$($Manifest.version)' carries no +proto mark, so nothing on the package says it is a dev build.")
    }

    # R70. The staged version must be the MAJOR.AUTO this checkout computes.
    # Without this the manifest silently fossilizes: it sat at 0.2.0 for 134
    # commits, through Kokomi's shell and three sprints, while deploy
    # overwrote each previous zip of that same name.
    if ($Manifest.version -ne $Expected) {
        $out.Add("staged manifest version is '$($Manifest.version)' but this checkout computes '$Expected'. Deploy stamps this; a mismatch means the package was not built from this tree.")
    }

    return $out
}

function Get-InstalledGameVersion {
    <#
      The game's real version, from release_info.json in the game directory.

      NOT from SlayTheSpire2.exe's VersionInfo, which reports a placeholder
      1.0.0.0 -- comparing min_game_version against that would fail every
      honest build while proving nothing.
    #>
    param([string]$GameDir)
    $info = Join-Path $GameDir 'release_info.json'
    if (-not (Test-Path $info)) { return $null }
    try { return (Read-JsonFile $info).version } catch { return $null }
}
