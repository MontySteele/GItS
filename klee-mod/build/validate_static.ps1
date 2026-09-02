<#
  THE DEPLOY GATE'S SOURCE-ONLY RULES, ON ANY MACHINE.

  Runs S4, S5 and S8 -- the validate.ps1 rules that read committed text and
  nothing else -- with no staged package, no game install, no dotnet, no pck
  and no .venv. That is what lets the `lints` job in .github/workflows/repo.yml
  run them on ubuntu under `pwsh`, which is the point: on 2026-09-02 a PR put
  the base game's `[blue]` numeral colour on every power face, CI was green,
  it merged, and the deploy was refused by S5 -- a regex over C# that any
  runner could have executed in two seconds, reachable only through a
  Windows-only 1100-line gate.

  ONE IMPLEMENTATION. Both this and validate.ps1 call the functions in
  static_rules.ps1; neither owns a copy of a rule. A finding printed here is
  the same string, under the same S-number, that would have refused the
  deploy.

  WHAT THIS IS NOT. It is not "validate.ps1 on Linux". Every rule that needs
  the staged package (S1, S2, S3, S9, S12), the game (S3, S16) or the built
  pck (S6c's contract half) stays where it is and still runs at deploy time,
  and S7 is the pytest suite CI already runs as its own job. static_rules.ps1's
  header has the full table and the reasons.

    pwsh klee-mod/build/validate_static.ps1          # from the repo root
    powershell -File klee-mod\build\validate_static.ps1

  Exit 0 clean, 1 with findings. Findings print one per line, prefixed with
  the S-number, so a CI log line can be pasted straight into a commit message.

  NOTE: keep this file pure ASCII (S8 sweeps every .ps1 in the repo, this one
  included).
#>
[CmdletBinding()]
param(
    # Defaults derived from this script's own location, so CI needs no paths
    # and a worktree needs no configuration.
    [string]$SourceDir,
    [string]$RepoRoot
)

$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot 'static_rules.ps1')

if (-not $RepoRoot) {
    # build/ -> klee-mod/ -> repo root
    $RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
}
if (-not $SourceDir) {
    $SourceDir = Join-Path (Join-Path $RepoRoot 'klee-mod') 'KleeCode'
}

if (-not (Test-Path $SourceDir)) {
    Write-Host "validate_static: no source directory at $SourceDir" -ForegroundColor Red
    exit 1
}

$findings = New-Object System.Collections.Generic.List[string]
$sw = [Diagnostics.Stopwatch]::StartNew()

foreach ($f in (Test-PoolRegistration -SourceDir $SourceDir)) { $findings.Add("[S4] $f") | Out-Null }
foreach ($f in (Test-LocTemplates -SourceDir $SourceDir))     { $findings.Add("[S5] $f") | Out-Null }
foreach ($f in (Test-ScriptsAscii -RepoRoot $RepoRoot))       { $findings.Add("[S8] $f") | Out-Null }

$sw.Stop()
Write-Host ("validate_static: S4 + S5 + S8 over $SourceDir in {0:N1}s" -f $sw.Elapsed.TotalSeconds)

if ($findings.Count -eq 0) {
    Write-Host 'validate_static: OK' -ForegroundColor Green
    exit 0
}

Write-Host "validate_static: $($findings.Count) finding(s)" -ForegroundColor Red
foreach ($f in $findings) { Write-Host "  $f" -ForegroundColor Red }
Write-Host ''
Write-Host 'These are deploy-gate rules (klee-mod/build/validate.ps1). A red here'
Write-Host 'is a deploy that will be refused on the machine that owns the game.'
exit 1
