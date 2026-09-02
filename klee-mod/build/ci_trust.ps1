<#
  DOES A GREEN CI RUN ALREADY COVER THIS EXACT TREE?

  THE COST BEING PAID. validate.ps1's S7 runs the whole pytest suite, serially,
  before every deploy: measured 2026-09-02 on this box at 399.3s over 5911
  tests, out of a gate whose other twelve rules together are ~6s. CI had
  already run that same suite on that same commit minutes earlier -- in
  parallel, in 60s -- and the deploy machine ran it again because nothing
  connected the two. An eight-minute wait between "commit" and "play it" is
  paid on every dev build, and it buys a re-derivation of a fact already in
  hand.

  THE THREE THINGS THAT MUST ALL HOLD before a remote run may stand in for a
  local one. Each is a way the local tree could differ from what CI saw, and
  none of them is checkable from the other two:

    1. THE WORKING TREE IS CLEAN. An uncommitted change is by definition not
       in any commit CI has seen. (Untracked files are not dirt -- see
       version.ps1's Get-AutoVersion -- and they are not code CI ran either,
       which is why the trust line below names the untracked count too.)
    2. HEAD IS ON origin/main. Not merely "a commit CI has seen": a topic
       branch's head can be green and still not be the tree that ships. The
       test is ancestry against the local origin/main ref, and a STALE ref
       fails it -- which errs toward running the suite, the safe direction.
    3. GITHUB SAYS THAT SHA IS GREEN. Read live through the REST API. Not the
       branch's latest run, not "the last one I remember": the check runs of
       this exact commit.

  ANYTHING ELSE IS "NOT PROVEN", INCLUDING OFFLINE. No gh, no network, no
  answer, a pending run, a missing pytest job -- every one of them returns
  Trusted=$false with a reason, and validate.ps1 then runs the tests. A gate
  that waved a deploy through because it could not reach GitHub would be the
  R70 failure class wearing a network error's coat.

  WHY THE `pytest` CHECK RUN BY NAME. S7 is the pytest suite and nothing else,
  so the run that stands in for it has to be the run that WAS it. `lints` is
  required too, because the deploy gate's own S6* rules are that job's lints
  and a red `lints` means the tree is not fit to deploy either way.
  `patch-sentinel` is skipped by name: repo.yml marks it `continue-on-error`
  on purpose (an upstream balance patch is not a defect in the open pull
  request), so treating its red as a blocker would import a decision that
  workflow already made.

  Usage -- a dry run of the decision, deploying nothing:

    powershell -NoProfile -Command ". klee-mod\build\ci_trust.ps1; `
        Get-CiSuiteTrust -RepoRoot (Get-Location).Path | Format-List"

  NOTE: keep this file pure ASCII (validate.ps1 S8 sweeps every .ps1 in the
  repo; Windows PowerShell 5.1 reads .ps1 as ANSI unless there is a BOM).
#>

# The jobs in .github/workflows/repo.yml whose green is load-bearing here, and
# the one whose red is advisory BY THAT FILE'S OWN DECISION.
$script:RequiredChecks = @('pytest', 'lints')
$script:AdvisoryChecks = @('patch-sentinel')

function Get-GhExecutable {
    <#
      The GitHub CLI, wherever it is. It is installed on this machine but not
      on PATH (docs/current/operations, and the house note that has said so
      since 2026-07-27), so the full path is tried first and PATH second --
      and $null, not a throw, when neither answers. "I could not ask" is a
      legitimate outcome of this whole file; it is never an error.
    #>
    $known = Join-Path ${env:ProgramFiles} 'GitHub CLI\gh.exe'
    if (Test-Path $known) { return $known }
    $onPath = Get-Command 'gh' -ErrorAction SilentlyContinue
    if ($onPath) { return $onPath.Source }
    return $null
}

function Get-CheckRunVerdict {
    <#
      The check-run rollup for one commit, as a verdict object.

      Returns Green / Reason / Trusted-run description. Parsed from the REST
      payload rather than from `gh pr checks`, because the question is about a
      COMMIT and not about a pull request: a merge commit on main has no PR of
      its own and the deploy is made from main.
    #>
    param([Parameter(Mandatory = $true)][string]$Sha,
          [Parameter(Mandatory = $true)][string]$Repo,
          [int]$TimeoutSeconds = 25)

    $gh = Get-GhExecutable
    if (-not $gh) {
        return @{ Green = $false
                  Reason = 'the GitHub CLI is not installed (looked in Program Files and on PATH)' }
    }

    $json = $null
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $json = & $gh api "repos/$Repo/commits/$Sha/check-runs" --jq '.check_runs' 2>&1
        $code = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $prev
    }
    if ($code -ne 0 -or -not $json) {
        return @{ Green = $false
                  Reason = "gh api could not read the check runs for $Sha (offline, unauthenticated, or the commit is not pushed)" }
    }

    # TWO STEPS, NOT ONE. `@(<pipeline> | ConvertFrom-Json)` reads as "an
    # array of the runs" and is not: ConvertFrom-Json emits a JSON array as a
    # SINGLE object rather than enumerating it, so the `@()` wraps the whole
    # array as one element and every `Where-Object` below then matches that
    # one element and returns all three runs at once. Parse, then wrap.
    $parsed = $null
    try {
        $parsed = ("$json" -join '') | ConvertFrom-Json
    } catch {
        return @{ Green = $false; Reason = 'the check-run payload did not parse as JSON' }
    }
    $runs = @($parsed)
    if (-not $runs -or $runs.Count -eq 0) {
        return @{ Green = $false; Reason = "GitHub reports no check runs at all for $Sha" }
    }

    $trusted = $null
    foreach ($name in $script:RequiredChecks) {
        $run = $runs | Where-Object { $_.name -eq $name } | Select-Object -First 1
        if (-not $run) {
            return @{ Green = $false; Reason = "no '$name' check run on $Sha" }
        }
        if ("$($run.status)" -ne 'completed') {
            return @{ Green = $false
                      Reason = "the '$name' check run on $Sha is $($run.status), not completed" }
        }
        if ("$($run.conclusion)" -notin @('success', 'neutral', 'skipped')) {
            return @{ Green = $false
                      Reason = "the '$name' check run on $Sha concluded '$($run.conclusion)'" }
        }
        if ($name -eq 'pytest') { $trusted = $run }
    }

    # Anything else that actually failed, minus the job repo.yml itself marks
    # advisory. A new required job appearing in that workflow should block a
    # skip here without anyone having to remember to add it above.
    foreach ($run in $runs) {
        if ($script:AdvisoryChecks -contains "$($run.name)") { continue }
        if ("$($run.status)" -eq 'completed' -and
            "$($run.conclusion)" -in @('failure', 'timed_out', 'action_required')) {
            return @{ Green = $false
                      Reason = "the '$($run.name)' check run on $Sha concluded '$($run.conclusion)'" }
        }
    }

    return @{
        Green   = $true
        Reason  = ''
        RunName = "$($trusted.name)"
        RunId   = "$($trusted.id)"
        RunUrl  = "$($trusted.html_url)"
        RunEnd  = "$($trusted.completed_at)"
    }
}

function Get-CiSuiteTrust {
    <#
      The whole decision, as one object: Trusted, Reason, Sha, and (when
      trusted) the run being stood on.

      -Repo defaults to this project's own slug. It is a parameter so the
      function can be exercised against a repository that is NOT this one,
      which is what the pytest arms do.
    #>
    param([Parameter(Mandatory = $true)][string]$RepoRoot,
          [string]$Repo = 'MontySteele/GItS',
          [string]$Branch = 'origin/main')

    $result = @{ Trusted = $false; Reason = ''; Sha = ''; Untracked = 0 }

    Push-Location $RepoRoot
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $sha = "$(& git rev-parse HEAD 2>$null)".Trim()
        if ($LASTEXITCODE -ne 0 -or -not $sha) {
            $result.Reason = "git rev-parse HEAD failed in $RepoRoot"
            return $result
        }
        $result.Sha = $sha

        # (1) clean, on the tracked-files-only meaning of clean.
        $status = @(& git status --porcelain --untracked-files=no 2>$null)
        if ($LASTEXITCODE -ne 0) {
            $result.Reason = "git status failed in $RepoRoot"
            return $result
        }
        $dirty = @($status | Where-Object { $_ -and "$_".Trim() })
        $others = @(& git ls-files --others --exclude-standard 2>$null)
        $result.Untracked = @($others | Where-Object { $_ -and "$_".Trim() }).Count
        if ($dirty.Count -gt 0) {
            $result.Reason = "the working tree has $($dirty.Count) uncommitted change(s) to tracked files, which no CI run has ever seen"
            return $result
        }

        # (2) on origin/main.
        & git rev-parse --verify --quiet "$Branch" > $null 2>&1
        if ($LASTEXITCODE -ne 0) {
            $result.Reason = "there is no $Branch ref in this checkout to compare HEAD against"
            return $result
        }
        & git merge-base --is-ancestor HEAD "$Branch" > $null 2>&1
        if ($LASTEXITCODE -ne 0) {
            $result.Reason = "HEAD ($($sha.Substring(0, 8))) is not an ancestor of $Branch; either the branch is unmerged or this checkout's remote ref is stale (git fetch)"
            return $result
        }
    } finally {
        $ErrorActionPreference = $prev
        Pop-Location
    }

    # (3) GitHub's own verdict on this exact sha.
    $verdict = Get-CheckRunVerdict -Sha $result.Sha -Repo $Repo
    if (-not $verdict.Green) {
        $result.Reason = $verdict.Reason
        return $result
    }

    $result.Trusted = $true
    $result.Reason = ''
    $result.RunName = $verdict.RunName
    $result.RunId = $verdict.RunId
    $result.RunUrl = $verdict.RunUrl
    $result.RunEnd = $verdict.RunEnd
    return $result
}
