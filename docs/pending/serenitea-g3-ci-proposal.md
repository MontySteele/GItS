# G3 — CI proposal (RULED: ADOPTED 2026-07-27)

**Status: ADOPTED**, Serenitea Sweep II track B1. [USER] ruled all three jobs
in, (c) included — "cheap insurance", explicitly confirmed. The NOT-doing list
below was confirmed as written, Windows-runner refusal and all.

The workflow now lives at **`.github/workflows/repo.yml`**. This document is
retained as the argument behind it: the reasons a job exists, and the reasons
five other jobs do not. It is no longer a request for a ruling.

---

## Who this is for

Not a hypothetical contributor. **The consumer is the next Claude Code
session**, and CI here is a pre-session guarantee: every session inherits a
green world on the fresh clone it actually starts from.

That framing matters, because it rules most CI ideas out. This repo has one
deploy machine, one contractual editor build, and a gitignored art tree. Almost
nothing about the *product* can be verified off that machine. What CAN be
verified off it is whether the tree a session starts from is sound — and that is
exactly what has bitten. Track A of this sprint existed because the suite was
red on a bare clone and nobody knew.

---

## Three jobs. Nothing else.

### (a) `pytest` on ubuntu — per-PR and on `main` post-merge

The Track A fresh-clone gate, made permanent. A GitHub runner IS a fresh clone
with no art, no `game_ref/`, no `.venv` — the exact environment Track A had to
be reconstructed by hand to test, twice, and which caught two defects in this
sprint's own work.

Post-merge on `main` as well as per-PR, because merge races are not
hypothetical here: the numbering convention that hands out R/D numbers by hand
is itself evidence that two workstreams land near each other, and **this sprint
hit a live pre-commit collision** (see G4).

Runtime is ~80s locally; a cold runner will be slower and still cheap.

### (b) The python lint suite, invoked DIRECTLY — no PowerShell wrapper

Parity, codegen staleness, pool membership, art coverage, roster registry.
These five are the softlock-preventing signal, and today they exist **only on
the Windows deploy machine**, behind `validate.ps1`. Two of them prevent hard
softlocks.

The population that pushes most — sessions — will never run a Windows lint.
Invoking the linters directly rather than through `validate.ps1` is the whole
point: the wrapper is what makes them Windows-only, and it is not what makes
them correct.

*(This sprint already dual-wired art_lint and the roster registry into pytest
for exactly this reason, so (b) partly overlaps (a) by design — belt and
braces on the softlock class specifically.)*

### (c) Ledger integrity — duplicate R/D-number lint on `DECISIONS` files

The collision the hand-numbering convention currently handles by eye, caught at
merge instead of at next read.

**Measured now, so the proposal is honest about its own value:**
`tier0/DECISIONS.md` has 36 numbered rulings and **0 duplicates**;
`klee-mod/DECISIONS.md` has 1 and 0 duplicates. So this job would find nothing
today. It is proposed as a *cheap standing guard on a hand-maintained sequence*,
not as a fix for a live defect — and if [USER] would rather not pay for a job
that has never fired, dropping (c) costs nothing and the proposal stands on (a)
and (b).

---

## Explicitly NOT doing — recorded as policy, not as an oversight

| Not doing | Why |
|---|---|
| **Windows runner for `validate.ps1`** | Actions PowerShell is not the deploy machine's PS 5.1. Green there is *false confidence* — and PS 5.1's native-stderr trap, the exact thing that took the deploy down twice (audit §3.4), is a 5.1 behaviour. The deploy machine remains the only honest validator of itself. |
| **pck build in CI** | Impossible. MegaDot is a contractual editor build with one local copy. |
| **Release / deploy automation** | The deploy writes into a Steam install. Not CI's business. |
| **Coverage tracking** | This repo's tests are argued, not counted. A coverage number would become a target. |
| **Scheduled runs** | The sims are deterministic; nothing drifts without a commit. A nightly job would re-prove the same thing forever. |
| **MegaDot path externalization** | Folded in here per the sprint doc: `build_pck.ps1:23` defaults to one contributor's `Downloads\` folder. CI cannot help (see above), so this stays a local-config item and is **parked**, not adopted. |

---

## What [USER] ruled (2026-07-27)

1. **Adopt (a), (b) and (c).** (c) stays despite finding nothing today —
   ruled cheap insurance on a hand-maintained sequence.
2. **NOT-doing list confirmed as written**, including the Windows-runner
   refusal.
3. Executed: `serenitea-g3-ci.yml` → `.github/workflows/repo.yml`. Setting the
   jobs as **required checks on `main`** is a GitHub branch-protection setting,
   not a file in this repo — it is [USER]'s to click, and G4 depends on it.
   See `serenitea-g4-session-isolation.md`.
