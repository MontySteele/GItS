<#
  Manifest version policy (R70, 2026-07-26). Dot-sourced by deploy.ps1 and
  validate.ps1 so the two cannot compute the version differently -- which is
  the whole point of a gate that compares one against the other.

  THE VERSION IS TWO PARTS: MAJOR-AUTO.

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

  A dirty working tree appends "+dirty". A +dirty build is never handed to a
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
      copy, which already carries MAJOR-AUTO and would compound).
    #>
    param([string]$SourceManifest)
    if (-not (Test-Path $SourceManifest)) {
        throw "source manifest not found: $SourceManifest"
    }
    $major = (Read-JsonFile $SourceManifest).version
    if ([string]::IsNullOrWhiteSpace($major)) {
        throw "manifest.json has no version; MAJOR is a ratified artifact and must be set by hand."
    }
    if ($major -match '-') {
        throw "manifest.json version '$major' already contains an AUTO part. MAJOR is the deliberate half only (e.g. '0.2'); AUTO is generated at deploy time."
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
        IsDirty    = $isDirty
        DirtyFiles = $dirtyFiles
    }
}

function Get-PackageVersion {
    <#
      The full MAJOR-AUTO string, plus the parts that produced it.
    #>
    param([string]$SourceManifest, [string]$RepoRoot)
    $major = Get-ManifestMajor -SourceManifest $SourceManifest
    $auto = Get-AutoVersion -RepoRoot $RepoRoot
    return @{
        Version    = "$major-$($auto.Auto)"
        Major      = $major
        Auto       = $auto.Auto
        IsDirty    = $auto.IsDirty
        DirtyFiles = $auto.DirtyFiles
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
        Expected    the MAJOR-AUTO string this checkout computes
    #>
    param(
        [Parameter(Mandatory = $true)]$Manifest,
        [Parameter(Mandatory = $true)][hashtable]$Installed,
        [AllowNull()][string]$GameVersion,
        [Parameter(Mandatory = $true)][string]$Expected
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

    # R70. The staged version must be the MAJOR-AUTO this checkout computes.
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
