# Sprint log — the Track B validation gate, seven items (2026-08-04 late / 08-05)

The signed package this pass executes, verbatim:
`docs/track-b-validation-gate-countersign-2026-08-04.md`. Rulings:
`tier0/DECISIONS.md` **R99** (items 1–4) and **R100** (items 5–7). Worktree G4.
Prior passes: `docs/sprint-understudy-p1-log-2026-08-04.md` (P1),
`docs/sprint-track-b-curves-log-2026-08-04.md` (Track B's first curves).

**Non-goals held, all of them.** No balance value, no card, no floor, no tag
revisit, no bridge fork, no drafter read. Nothing in `tier0/`, `tier05/`, the
drafter or any sheet moved; the constant-parity lint reads **71 mirrored, 16
declared unmirrored, unchanged**.

**Guardrail 7 applies to every number below and one notch harder than usual.**
The committed-arm figures are bot-limited floors measured under a constraint no
person plays under: a policy that drafts by declaration, on read-back seeds,
through a heuristic with its own declared reductions. They are not balance
evidence, they do not grade a character, and they are not comparable to any
other build's numbers.

---

## What landed

| item | where |
|---|---|
| The signed package, verbatim | `docs/track-b-validation-gate-countersign-2026-08-04.md` |
| R99, R100 | `tier0/DECISIONS.md` |
| Punch Off routing (item 2) | `docs/animation-sprint-2-log.md` § "ROUTED IN"; `docs/backlog-2026-07-29.md` §1 |
| The dated asterisk (item 2) | `docs/sprint-understudy-p1-log-2026-08-04.md` |
| Defects 13/14 routing accepted (item 3) | `docs/backlog-2026-07-29.md` §1; both sprint logs |
| Declared deck intent, human feed (item 4a) | `klee-mod/KleeCode/Diagnostics/PlayTelemetry.cs` |
| Declared-intent cut on B2 (item 4a) | `tools/track_b_curves.py --intent` |
| The archetype-committed draft arm (item 4b) | `understudy/committed.py`, `understudy/policy_v1.py`, `understudy/soak.py --commit` |
| Win visibility (item 5) | `PlayTelemetry.CombatEnded` + two `AbstractModel` overrides |
| Furina's meters on the human feed (item 6a) | already shipped; **verified**, not rebuilt |
| Tests | `tier0/tests/test_understudy_committed.py` (12), additions to `test_track_b_curves.py` |

---

## Item 5 — the combat-end seam was not the one the package named

The package authorised a Harmony patch on `EndCombatInternal` **or the correct
seam, verified by decompile rather than guessed**. Verified, and the guess would
have been wrong in the direction that costs less:

```
CombatManager.EndCombatInternal()
    IsInProgress = false
    foreach (player) await player.ReviveBeforeCombatEnd()
    await Hook.AfterCombatEnd(runState, combatState, room)      <-- here
    room.OnCombatEnded()
    ...
    await Hook.AfterCombatVictory(runState, combatState, room)  <-- and here
```

and in `MegaCrit.Sts2.Core.Hooks.Hook`:

```
public static async Task AfterCombatEnd(IRunState runState, ICombatState? combatState, CombatRoom room)
{
    foreach (AbstractModel model in runState.IterateHookListeners(combatState))
        await model.AfterCombatEnd(room);
}
```

`IterateHookListeners` is the same iteration that has been delivering
`BeforeCombatStart` to `PlayTelemetryHooks` since the Track B landing. So the
outcome label costs **two `AbstractModel` overrides and no Harmony patch** — no
new patch surface on the combat lifecycle of a deterministic-lockstep co-op
game, and no async continuation of our own in finding 21's neighbourhood.

**The record is corrected where the wrong claim lives.** "The game exposes no
first-party combat-END hook" was wrong about the game and right about the
consequence; the retraction is in
`docs/sprint-track-b-curves-log-2026-08-04.md` and in the schema table
(`understudy/README.md`), and a test now asserts that no `HarmonyPatch` appears
in the telemetry file — so a future pass that decides it needs one has to argue
for it rather than add it.

**Two behaviours worth naming:**

- **The loss path has no end hook and needs none.** `CheckWinCondition` sees a
  pending loss, calls `ProcessPendingLoss` and returns before
  `EndCombatInternal`. `died` was always exact from the player's own death.
- **`hp_end` is capped by the last in-fight reading.**
  `ReviveBeforeCombatEnd` runs immediately *before* our hook, so current HP can
  be higher than anything the fight ever saw. Crediting a fight for the revive
  that followed it is the same class of lie as charging it for the campfire —
  the bug the previous pass fixed in the other direction.

## Item 6a — already shipped, and the pass verified rather than rebuilt

`PlayTelemetry.OpenTurn` has recorded `[round, fanfare, salon_members,
salon_cap, encore]` per seat since the Track B landing, reading
`FurinaResources.Encore`/`Fanfare` and `SalonMemberPower.Count`/`SlotsFor`
directly off the CustomResources. That is the whole reason the human feed sees
a meter the bridge serialises as `-1`. Recorded as met by run-verification.
Building it a second time would have been the more expensive way of agreeing
with the package.

## Item 6b — not built, and not started

The bridge fork stays P1.5, gated where the package puts it.

---

## Item 4a — how [USER] declares an intent, in one line

**Write one word in `intent.txt` in the telemetry folder, before playing:**

```
%APPDATA%\SlayTheSpire2\gits_telemetry\intent.txt
```

The file may say `fanfare`, `salon`, or `spotlight`. Everything after the first
word on the first line is free comment space, so a note about why is free. An
absent, empty or unreadable file means **no declaration**, which is a reading
rather than a gap and is what most of the record will always be.

That is the entire mechanism. No UI, no toggle, no export, no menu — the same
bar the hook itself was built to. It is read **once per session** so a run's
records cannot disagree with each other about what the run was, and it is
**always a declaration, never an inference**: nothing reads a deck and guesses.

Then:

```
python tools/track_b_curves.py --intent fanfare
```

cuts every curve to fights whose run declared it — human sessions and committed
soak arms alike, because both feeds carry the same key.

## Item 4b — the committed draft arm

`python -m understudy.soak --runs 3 --commit fanfare`

Two rungs. If any offer is a card of the declared archetype **per the design
sheets**, take the best-scoring one — a priority over the ordering, imposed
ahead of the skip threshold and the late-run lean gate, because a commitment a
lean gate can overrule produces exactly the mixed deck the arm exists to avoid.
Otherwise the sim's own `assigned_policy` under the declared plan, skip
included.

Membership comes off `docs/*-cards.yaml`, which is the same source
`tools/track_b_curves.py` splits B2 by. That is deliberate: **the arm that
builds the deck and the reader that grades it must agree on what a Fanfare card
is**, or the grade measures the disagreement.

**Declared limits, both of them:**

- **The shop is not committed.** `policy_v0._shop` owns affordability and the
  shelf-index remapping that took a defect to get right; re-deciding a purchase
  around a commitment would put a second variable and a second index bug in the
  window.
- **The pilot is not committed.** A committed-Fanfare run drafts Fanfare cards
  and then plays them with the salon-weighted pilot, because changing the pilot
  too would make a divergence unreadable. One variable per window.

**The pin.** `tier0/tests/test_understudy_committed.py` replays every state
shape the driver produces through `commit=None` and compares it against the
un-flagged call decision for decision, then repeats with the flag set to prove
`card_reward` is the only category that moves. Without that, every baseline
soak taken after this landed would quietly be a number about a different
policy, and R98's validation would stop meaning what it says.

---

## Found on the way: the soak was writing its play into the human feed

Not in scope, fixed anyway, because the next six runs of this pass would have
been the first casualty.

`PlayTelemetry` labels a record `human` unless `GITS_TELEMETRY_FEED` says
otherwise, and **nothing set it**. The schema doc claimed the soak set it for
the child it launches; it did not — last night's runs came out labelled `bot`
only because the shell that ran them happened to export it. A soak launched
from a fresh shell files bot-driven play into the one feed whose entire value
is that a person produced it, and the Act 2/Act 3 rows that feed exists for are
exactly the rows nobody could sanity-check.

`Session._launch` now builds the child environment explicitly and passes the
declared intent down with it.

**That exposed the other half, which is a reader defect.** When the soak drives
the game, *both* writers record every fight — `soak.py` from the wire, the mod
from inside the process — and both are honestly `feed: bot`. A reader grouping
by feed alone therefore counts each soak fight twice, and reports a fight count
that is a fact about how many instruments were running. `tools/track_b_curves.py`
now names both writers whenever both are present and takes `--source soak` /
`--source mod`. **They are not copies of each other and must never be summed:**
`mod` carries the live Salon cap and a real Encore, `soak` carries the potions
and the policy's own view.

Every number in this log names its writer for that reason.

---

## The committed-arm soaks

*(Results and grades below were recorded before any interpretation was
written — D4.)*

<!--RESULTS-->

---

## Found on the way, second: the baseline curve cannot be regenerated

`docs/track-b-curves.md` says it regenerates with
`python tools/track_b_curves.py --out docs/track-b-curves.md`. It does not.

Its inputs are `understudy/logs/soak/`, which is **gitignored and
per-worktree**. The four soaks behind the published 87 records were run in a
worktree that this pass does not have, and the surviving logs in two older
worktrees hold 61 and 48 records — neither of which is 87. The document is a
photograph of a directory that no longer exists anywhere in one piece.

Nothing was regenerated on top of that, deliberately: overwriting a published
baseline with a corpus that is merely *nearby* is worse than leaving it
labelled. **`docs/track-b-curves.md` is unchanged by this pass.**

The forward fix is `--intent none`, which is why it exists: once a committed
arm writes into the same directory, "the baseline is whatever was in the folder
that day" stops being recoverable at all, and a flag that separates declared
from undeclared runs is the cheapest thing that keeps the next baseline a
baseline. The deeper problem — **a published document whose inputs die with a
worktree** — is a gate item below, not something this pass decides.

---

## Reversibility ledger — game-directory changes this session

<!--LEDGER-->
