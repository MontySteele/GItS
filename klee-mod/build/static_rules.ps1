<#
  THE VALIDATE RULES THAT NEED NOTHING BUT SOURCE TEXT.

  WHY THEY MOVED HERE (2026-09-02). The round-six deploy was REFUSED by S5:

      [S5] CompanionOverhaulHooks.cs:592 uses '[blue]', which is not a known
           BBCode tag.

  PR #291 had put the base game's own numeral colour on every power face, CI
  was green on it, it merged, and the FIRST thing that ever looked at those
  strings was a deploy attempt on a machine with the game installed. S5 is a
  regex over committed C# -- it needs no game, no dotnet, no pck, no art and
  no Steam -- and it was nevertheless reachable only through a 1000-line
  Windows PowerShell gate that only one machine can run. The wrapper is what
  made it unreachable; it is not what makes it correct (repo.yml's own words
  about this exact family of lints).

  So the source-only rules live in functions here, `validate.ps1` calls them
  and prints their findings under their own numbers exactly as before, and
  `validate_static.ps1` calls the same functions from the `lints` job in
  .github/workflows/repo.yml under `pwsh` on ubuntu. ONE implementation, two
  callers -- the arrangement `version.ps1`'s Test-VersionPolicy already has,
  and for the same reason: the tests and CI must exercise the shipped code
  path rather than a second copy that agrees with itself.

  WHICH RULES ARE HERE, AND WHY NOT THE OTHERS:

    S4  pool registration     reads *.cs                       -> here
    S5  loc template syntax   reads *.cs                       -> here
    S8  build scripts ASCII   reads *.ps1                      -> here

    S1/S2/S3/S9/S12  need the STAGED PACKAGE (and S3 the game install), which
                     only exists after a build. Not static.
    S6/S6a/S6b/S6d/S6e/S10/S11  are python lints, and every one of them is
                     ALREADY a step in repo.yml's `lints` job. Nothing to
                     move; running them twice would double the noise and
                     halve the trust.
    S6c  is half and half: the CharacterModel override sweep is source-only,
         but its second half compares against the staged pck contract. Left
         whole in validate.ps1 rather than forked into two homes -- see the
         PR's Not-done list.
    S7   is the pytest suite, which CI is already the definitive run of.
    S16  needs the game assemblies.

  PORTABILITY. Everything below is PS 5.1 and pwsh 7 on Linux alike:
  Get-ChildItem, Get-Content, [regex], [IO.File]. No Windows path separators
  in any comparison -- the ASCII sweep's exclude list is matched against a
  forward-slashed copy of the path, which is what broke first when this was
  tried against a Linux checkout.

  NOTE: keep this file pure ASCII (S8 sweeps every .ps1 in the repo, this one
  included; Windows PowerShell 5.1 reads .ps1 as ANSI unless there is a BOM).
#>

function Test-PoolRegistration {
    <#
      S4. BaseLib custom models must resolve their pool registration.

      CustomCardModel's ctor defaults autoAdd:true, which calls
      CustomContentDictionary.AddModel and THROWS unless the class carries a
      [Pool(typeof(...))] attribute. This is a startup crash, not a soft
      failure: it happens during model construction and takes the game to an
      error screen. Shipped 2026-07-20 on DuckAndCover.

      Heuristic by necessity -- proving it properly means reading IL for the
      base ctor's bool argument. It catches the shape we actually hit and is
      honest about being a lint, not a proof.
    #>
    param([Parameter(Mandatory = $true)][string]$SourceDir)
    $out = New-Object System.Collections.Generic.List[string]
    $customBases = 'CustomCardModel|CustomRelicModel|CustomPotionModel'
    foreach ($f in Get-ChildItem $SourceDir -Recurse -Filter *.cs) {
        $text = Get-Content $f.FullName -Raw
        if ($text -notmatch "class\s+\w+\s*:\s*($customBases)") { continue }

        $hasPoolAttr = $text -match '\[\s*Pool\s*\('
        $optsOut     = $text -match 'autoAdd\s*:\s*false'

        if (-not $hasPoolAttr -and -not $optsOut) {
            $out.Add("$($f.Name): derives from a BaseLib Custom*Model but has neither a [Pool(typeof(...))] attribute nor autoAdd: false. Its constructor will throw at startup.")
        }
    }
    return $out
}

# The BBCode tags the renderer knows. `blue` is the base game's own numeral
# colour and joined the list on 2026-09-02 (PR #301) after PR #291 printed it
# on every power face and this rule -- correctly -- refused the deploy.
$script:KnownBBCodeTags = @(
    'center', 'left', 'right', 'b', 'i', 'u', 's',
    'color', 'bgcolor', 'fgcolor', 'font', 'img', 'url',
    'gold', 'keyword', 'wave', 'shake', 'p', 'blue')

function Test-LocTemplates {
    <#
      S5. Loc strings declared in source use the right template syntax.

      Two distinct syntaxes, both of which bit us:
        - SmartFormat uses SINGLE braces. "{{Damage}}" renders literally.
        - Square brackets are BBCode. "[Block]" collides with the [center]
          wrapper the card renderer adds and throws "Found end tag center,
          expected Block".
      The runtime check covers strings after they land in the table; this
      catches them at author time.
    #>
    param([Parameter(Mandatory = $true)][string]$SourceDir)
    $out = New-Object System.Collections.Generic.List[string]
    foreach ($f in Get-ChildItem $SourceDir -Recurse -Filter *.cs) {
        $n = 0
        foreach ($line in (Get-Content $f.FullName)) {
            $n++
            # Only look at lines that are plausibly loc values.
            if ($line -notmatch '"(title|description)"|\.description"\]|\.title"\]') {
                if ($line -notmatch '\("(title|description)",') { continue }
            }

            if ($line -match '\{\{') {
                $out.Add("$($f.Name):$n uses doubled braces; SmartFormat placeholders are single-braced and {{X}} renders literally.")
            }
            # Scan only the STRING LITERALS on the line, never the surrounding
            # C#. BBCode can only ever appear inside a literal, and scanning
            # the raw line made a dictionary-initializer KEY look like a tag:
            # the line
            #     [Cards.FurinaRiderTips.FanfareKey + ".title"] = "Fanfare scaling"
            # passes the loc-value filter above on its `.title"]`, and then
            # `[Cards` reads as an unknown BBCode tag. That false positive
            # blocked every deploy since 0b33ffd. Narrowing to literals keeps
            # the gate's reach -- a real '[Block]' inside any loc string is
            # still caught -- while dropping a class of finding that cannot be
            # a render bug.
            foreach ($lit in [regex]::Matches($line, '"([^"\\]*(?:\\.[^"\\]*)*)"')) {
                foreach ($mm in [regex]::Matches($lit.Groups[1].Value,
                                                 '\[/?([A-Za-z_][A-Za-z0-9_]*)')) {
                    $tag = $mm.Groups[1].Value
                    if ($script:KnownBBCodeTags -notcontains $tag.ToLower()) {
                        $out.Add("$($f.Name):$n uses '[$tag]', which is not a known BBCode tag. If it is a variable write {$tag}; an unknown tag throws at render time.")
                    }
                }
            }
        }
    }
    return $out
}

function Test-ScriptsAscii {
    <#
      S8. Build scripts are pure ASCII.

      Every .ps1 in this repo says so in its own header, and the rule was
      still broken -- Furina's Architect finale line carried an em-dash, and
      because Windows PowerShell 5.1 reads a BOM-less .ps1 as ANSI, the UTF-8
      bytes were decoded as cp1252 and re-encoded as UTF-8 on the way into the
      pck. The line shipped mangled on the WIN SCREEN, which is the last text
      a player sees after beating Act 3. Caught 2026-07-25 by reading the
      built json, not by any gate.

      The failure is silent by construction: the mangling happens at PARSE
      time, so nothing downstream can tell a mojibake string from an intended
      one. The only place to catch it is the bytes on disk, here.

      A line may opt out with the marker below when a non-ASCII byte is the
      POINT (validate.ps1's own literal-BOM regex is the one case today).

      C1 (audit sec.3.1): this walked $SourceDir (= KleeCode), which contains
      ZERO .ps1 files -- they all live in klee-mod/build/ and tools/. The loop
      found nothing and the rule passed, every run, since the day it was
      written. So it sweeps from the repo ROOT, and an empty sweep is a
      FINDING: a list of directories would be the same defect one level up.
    #>
    param([Parameter(Mandatory = $true)][string]$RepoRoot)
    $out = New-Object System.Collections.Generic.List[string]
    $asciiExempt = '# ascii-exempt:'
    # Trees that are not ours: .venv ships Activate.ps1, which is not this
    # repo's to keep ASCII. Matched against a FORWARD-SLASHED copy of the
    # path so the same list works on Linux, where the separator is '/' and the
    # old backslash patterns matched nothing at all.
    $asciiSkip = @('*/.venv/*', '*/dist/*', '*/obj/*', '*/bin/*',
                   '*/pck-work/*', '*/node_modules/*')
    $ps1Files = @(Get-ChildItem $RepoRoot -Recurse -Filter *.ps1 -ErrorAction SilentlyContinue |
        Where-Object {
            $p = $_.FullName.Replace('\', '/')
            -not ($asciiSkip | Where-Object { $p -like $_ })
        })
    if ($ps1Files.Count -eq 0) {
        $out.Add("found no .ps1 files under $RepoRoot to check. This rule scanned a directory with none in it for its entire life; an empty sweep is the failure mode, not a pass.")
        return $out
    }
    foreach ($script in $ps1Files) {
        $lineNo = 0
        foreach ($line in [IO.File]::ReadAllLines($script.FullName)) {
            $lineNo++
            if ($line -match $asciiExempt) { continue }
            $offenders = [char[]]$line | Where-Object { [int]$_ -gt 127 }
            if ($offenders.Count -gt 0) {
                $codes = ($offenders | ForEach-Object { 'U+{0:X4}' -f [int]$_ }) -join ', '
                $out.Add("$($script.Name):$lineNo has non-ASCII characters ($codes). PowerShell 5.1 reads a BOM-less .ps1 as ANSI, so these are decoded as cp1252 and ship as mojibake wherever the string lands. Use ASCII, or mark the line '$asciiExempt <reason>' if the byte is deliberate.")
            }
        }
    }
    return $out
}
