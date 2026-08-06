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

> **UPDATE 2026-08-05 (R104) — the gate is lifted and P1.5 is NEXT in the
> Understudy queue.** Not because this item changed, but because two more
> demands arrived at the same fork: the S7 C2 probe needs the Center Stage /
> Guest Cast selector choice recorded (R103(b)), and family B's blind turn-1
> fanfare channel needs the same thing. With chosen seeds that is three
> payoffs on one work item. Scope unchanged — still the fork as described
> here, with nothing riding along.

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
written — D4. Every table names its WRITER, because both wrote every fight.)*

### The runs

**Committed-Fanfare, `--commit fanfare`, log stamp `20260805-003056`:**

| run | seed | outcome | reached | fights | actions | wall |
|---|---|---|---|---|---|---|
| 1 | `DT8RR60V03` | died | act 1 | 5 | 229 | 176 s |
| 2 | `EYN7XPN36M` | died | act 1 | 4 | 153 | 117 s |
| 3 | `ND9RJAYPBQ` | died | act 1, the boss | 9 | 412 | 313 s |

**Three runs, 18 fights, 794 actions, ZERO defects filed.** Reversibility
REVERTED on all four ledger entries; `fast_mode` captured as `Fast` at setup.
All three seeds read-back (R95).

**Committed-Salon, `--commit salon`, log stamp `20260805-004135`:**

| run | seed | outcome | reached | fights | actions | wall |
|---|---|---|---|---|---|---|
| 1 | `WNYVF59QS5` | died | act 1 | 4 | 153 | 118 s |
| 2 | `SKUSPCCTKK` | died | act 1 | 6 | 219 | 168 s |
| 3 | `43MLG7MG9L` | **defect** | act 1, floor 7 | 2 | 85 | 66 s |

**Three runs, 12 fights, 457 actions, one defect.** Reversibility REVERTED on
all four entries. Seeds read-back.

**Harness defect 15 — `no_progress`, the map↔rest_site bounce.** Two distinct
fingerprints across twelve posted actions, cycling
`map|1|6|hp 59` ↔ `rest_site|1|7|hp 59` — a rest site entered at full HP that
the run left and re-entered without the floor advancing. **Traversal class**,
the same family as 1–14, so it is **filed and not fixed** under the routing
R99/3 established: it goes to the next traversal pass with 13 and 14.
`no_progress` is deliberately outside the stop-and-surface set — halting on it
would stop the instrument on exactly what it exists to find — so the soak
filed it and finished.

### The arm did what it was built to do

Share of recorded plays by archetype, **soak writer, like for like** (the
baseline figure is the two surviving baseline corpora, 109 fights):

| corpus | fights | salon | fanfare | spotlight | generic |
|---|---|---|---|---|---|
| baseline (undeclared) | 109 | 13.9% | **8.7%** | 6.0% | 71.4% |
| committed-Fanfare | 18 | 6.4% | **24.9%** | 3.8% | 64.9% |
| committed-Salon | 12 | **12.7%** | 12.7% | 7.0% | 67.7% |

Fanfare's share of plays is **2.9× the baseline's**. That is the precondition
Track B's null was blocked on: a deck that is meaningfully the declared
archetype rather than a mixed deck with a few of its cards in it.

**It is still 65% generic, and that number is structural.** A run that dies in
act 1 drafts a handful of cards on top of a starter deck it did not choose;
`--commit` moves what is drafted, not what was there at floor 0. A committed
arm makes the archetype the *largest declared* share of the deck; it does not
make the deck pure, and no flag can while debt #3 stands.

**And the Salon arm barely moved at all — 12.7% against a 13.9% baseline.**
That is not a failure of the flag. `policy_v0.ARCHETYPE` is already `"salon"`,
so the baseline draft has been scoring every offer under the salon plan since
Phase 0. Committing to salon is close to a no-op against a policy that was
already committed to salon, and the number says so. It matters for the grades
below, because one of them is a *comparison* with Salon.

### The tables the grades are read from

Both arms, **mod writer** (the more complete record of what was played: it sees
auto-played companion cards the bot never posts, and it carries a live meter).
`required output` is B1's own column for the same fights.

| arm | class | turn | fights | median incoming | median required output/turn | median pool drop | median block at turn end |
|---|---|---|---|---|---|---|---|
| Fanfare | monster | 1 | 14 | 7 | 10.6 | **12.0** | 6.0 |
| Fanfare | monster | 2 | 14 | 8 | 10.6 | **8.0** | 9.0 |
| Fanfare | monster | 3 | 14 | 6 | 10.6 | **7.5** | 5.5 |
| Salon | monster | 1 | 11 | 8 | 9.8 | **9.0** | 7.0 |
| Salon | monster | 2 | 11 | 8 | 9.8 | **6.0** | 9.0 |
| Salon | monster | 3 | 11 | 14 | 9.8 | **10.0** | 4.0 |

Attributed damage per PLAY of the declared archetype, soak writer,
attribution-limited in the direction the Track B log already declares
(a card's total is spread across the turns it was played in):

| arm | archetype | t1 | t2 | t3 |
|---|---|---|---|---|
| committed-Fanfare | fanfare | 5.2 (18 plays) | 4.8 (13) | 1.6 (8) |
| committed-Salon | salon | 0.0 (2) | 4.8 (6) | 12.0 (4) |
| *(baseline, published)* | fanfare | 3.4 | 2.4 | 2.3 |
| *(baseline, published)* | salon | 3.2 | 2.5 | 3.6 |

### GRADE (a) — Fanfare early-half, R90/1b

> *In Act 1, Fanfare-archetype output in fight-turns 1–3 falls short of the
> demand curve where Salon does not.*

**GRADE: PARTIALLY GRADED. The Fanfare half is measured and the prediction is
NOT SUPPORTED. The comparison to Salon is NOT GRADED, because the Salon arm is
not a contrast.**

> ~~**PROVISIONAL -- instrument under audit (R102, C2 escrow, 2026-08-05).** This
> grade is one of the four conclusions escrowed pending the S7 C2 probe (a
> candidate infidelity in tier0's Fanfare accounting,
> `docs/s7-classification.md` family C): **not citable as load-bearing, not
> shipped against, and not redesigned against** until the probe reports. If C2
> confirms, the grade re-opens formally and is re-graded against the corrected
> sim; if C2 is written off, this mark is struck and the grade stands exactly
> as written.~~
>
> **STRUCK 2026-08-06 (R113) -- escrow released, instrument vindicated.** The
> second branch of the sentence above is the one that fired: **C2 is written
> off** as a family-C infidelity (`docs/probe-b-fanfare-residual.md`: tier0's
> Fanfare generation and decay are both at parity; the residual is a
> reconstruction gap, a sampling seam, and one bounded +2-per-combat term in
> tier0's favour). **The grade stands exactly as written** and is no longer
> frozen. R113's clause C-d rides with it: the vindicating measurement is
> bot-limited (Guardrail 7), Furina-only, and taken with the salon empty
> throughout -- which is the same salon caveat this grade already carries in
> its own second half.

The first half is now gradeable and that is the change this pass bought: the
committed-Fanfare deck is 24.9% Fanfare by plays against a baseline 8.7%, so
the objection that killed the grade in the Track B pass — *this is a mixed deck
and the claim is about an archetype* — no longer applies to it.

Read against demand, **the Fanfare arm does not fall short in the early half in
the shape the prediction describes.** It is *above* required output on turn 1
(12.0 vs 10.6), below on turns 2 and 3 (8.0 and 7.5 vs 10.6). Per play, its
Fanfare cards hit for 5.2 / 4.8 / 1.6 against the baseline's published
3.4 / 2.4 / 2.3 — higher in exactly the turns the prediction says are weak.

**The second half cannot be graded, and the reason is the instrument again.**
"Where Salon does not" requires Salon to be a different condition, and it is
not: the baseline draft already runs the salon plan, so committed-Salon
reproduces baseline rather than contrasting with it. Its own curve falls short
on turns 1 and 2 (9.0 and 6.0 vs 9.8) and clears on turn 3 — i.e. **Salon falls
short in the early half too**, which is the opposite of the differential the
prediction asserts, measured on an arm that is not entitled to carry the
comparison.

**Instrument named, per the standing rule that a null names its replacement:**
a **no-plan arm**. The contrast this prediction needs is Fanfare against a
drafter with no archetype plan at all, and today there is no such arm —
`generic` is deliberately not declarable, and `policy_v0.ARCHETYPE` is frozen
at `"salon"` inside a module that may not be edited. That is a small, clean
piece of work and it is **not** taken here: adding an arm to fix a grade in the
same pass that reports the grade is how a measurement acquires the answer it
wanted.

### GRADE (b) — Salon fill time, R91/2b, re-measured

**REPORTED, and the confound was NOT removed.** Committed-Salon, 12 fights
carrying a meter sample, mod writer (the live cap, not the printed one):

| measure | committed-Salon | baseline (published) |
|---|---|---|
| fights where the Salon reached cap | **1 of 12** | 0 of 56 |
| median turn first at cap | **6** (the single fight that did) | no such turn |
| fraction of fight-turns at cap | **1.8%** (1 of 55) | 0.0% |
| median peak members | **0.5 of 3** | 1.0 of 3 |

**The number is 1.8%, and it does not discharge R91/2b's revisit condition in
either direction.** The condition asks for bounded-meter readers plateauing on
an output curve; one fight reaching cap on turn 6 is not a plateau, and a
median peak of half a member is not a filling meter.

**The reason it does not discharge is now sharper than "the bot doesn't build
salons".** The committed arm was supposed to remove that confound and it could
not, because *there was no salon-specific confound to remove*: the baseline was
already drafting the salon plan. What the two arms together say is that **a
Furina who drafts salon cards under this pilot still does not staff the stage**
— across 68 metered fights between them, the Salon reached cap once. That is a
sharper observation than the Track B pass could make, and it is still **a
bot-limited floor about a pilot**, not a finding about the Salon.

**No tag is revisited, nothing is proposed, and R91/2b stays open.** The
revisit is [USER]'s decision; this pass reports the number, as instructed.

---

## Run-verification — items 5 and 6a, from live play

Not asserted from source. A record written by the deployed build during the
committed-Fanfare soak, keys trimmed to the ones under test:

```json
{"record":"fight","schema":"1","feed":"bot","source":"mod","intent":"fanfare",
 "seats":1,"seat_index":0,"character":"Furina","act":1,"kind":"monster",
 "outcome":"won",
 "meters_by_turn":[[1,0,0,3,0],[2,5,0,3,5]]}
```

| item | what the record proves |
|---|---|
| **5 — win visibility** | `outcome: "won"`. Across 29 mod-written fights this session: **25 `won`, 4 `died`, zero `interrupted`.** Every one of those `won` rows would have read `interrupted` on 0.2-289. |
| **6a — Furina's meters** | `meters_by_turn` `[round, fanfare, salon_members, salon_cap, encore]`, with Fanfare 5 and **Encore 5** on turn 2 — the meter the bot feed records as `-1` because the wire does not serialise it. |
| **4a — declared intent** | `intent: "fanfare"`, stamped by the harness through `GITS_TELEMETRY_INTENT`; the human path is the same reader against `intent.txt`. |
| **the feed label** | `feed: "bot"` on a mod-written record, from the launcher's explicit child environment rather than from whoever's shell. |

**One limit found by verifying rather than by reading:** the mod writer
recorded 17 fights where the soak writer recorded 18. The missing one is the
last fight of a run that was still open when teardown killed the process —
there is no combat-end hook for a process that does not reach the end of the
combat. The soak's own writer closes it as `interrupted`, so nothing is lost
from Track B; it is recorded here because a reader comparing per-writer fight
counts will otherwise find an unexplained gap of one per killed run.

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

| # | change | undo | state |
|---|---|---|---|
| 1 | `steam_appid.txt` created at the game root (two soaks) | `Remove-Item steam_appid.txt` | **REVERTED** by each soak's teardown |
| 2 | `mods\STS2_MCP\` deployed from vendor pin `55e0648` (two soaks) | `.\build\deploy_bridge.ps1 -Remove` | **REVERTED** |
| 3 | `SlayTheSpire2.exe` launched directly (two soaks) | terminated at teardown | **REVERTED** |
| 4 | `FastMode=Instant`, `TimeScale=3.0` via the speed endpoint (two soaks) | `POST {"enabled": false}` | **REVERTED** on both; `fast_mode` captured as `Fast` at each setup, so `Instant` never reached `settings.save` |
| 5 | `mods\klee` replaced: **0.2-289 → 0.2-296** | `git checkout e07fb4c && cd klee-mod && .\build\deploy.ps1` | **STANDING BY DESIGN** — this is the build the gate package says to keep, plus this pass's outcome labels. In the gate items below. |
| 6 | `%APPDATA%\SlayTheSpire2\gits_telemetry\intent.txt` created | delete the file | **STANDING BY DESIGN** — it is the declaration mechanism, and it declares NOTHING as shipped (first line is a comment). Deleting it costs nothing but the instructions. |
| 7 | `%APPDATA%\SlayTheSpire2\gits_telemetry\play-*.jsonl` — 6 new files, 29 fight records, all `feed: bot` | delete them | **STANDING BY DESIGN** — soak-driven records, correctly labelled `bot`, in the human feed's directory (one writer, one folder). `--intent` and `--source` separate them from anything a person plays. |

Worktree-local, gitignored, NOT repo changes: `klee-mod/local.props` copied
from the main checkout; `game_ref/` copied; `ImageGen/images`, `.venv` and
`art/raw` junctioned so `deploy.ps1`'s own gates could run rather than skip.

## Suite

| mode | result |
|---|---|
| default (with `game_ref/`) | **1607 passed** |
| `GITS_REFERENCE_MODE=committed-only` | **1572 passed, 35 skipped** |

`validate.ps1`: **OK, all rules**, on the staged package. Constant parity: **71
mirrored, 16 declared unmirrored** — unchanged.

## The final build

**`0.2-296`**, zip at `klee-mod/dist/klee-v0.2-296.zip` (76.9 MB, `klee/` as
the archive root), built from the validated stage on a clean tree and deployed
to the game directory.

**This is the build to hand the table, not 0.2-289.** The gate package's item 1
says keep 0.2-289 and package it; items 5 and 6a landed in between, and a
record from 0.2-289 cannot say who won a fight — which is the demand curve's
whole job. The C# source of 0.2-296 is identical to the build every number
above was verified on (`0.2-293`); the dll differs only as any two Release
builds of the same source differ, and the version moved because four Python
commits moved the repo's commit count.

## Gate items — batched for one sitting

1. **Distribute `klee-v0.2-296.zip`, and tell the table about the telemetry
   BEFORE the session.** That courtesy condition is R99/1 and it is the only
   part of this pass that a machine cannot execute. What to say is short: the
   build writes a JSONL file of per-fight numbers to each player's own
   `%APPDATA%\SlayTheSpire2\gits_telemetry\`, it is read-only with respect to
   the game, nothing leaves their machine, and it exists so Acts 2 and 3 of the
   demand curve stop being empty.
2. **Optionally declare an intent** before a session by writing one word in
   `%APPDATA%\SlayTheSpire2\gits_telemetry\intent.txt`. The file is there with
   instructions in it and declares nothing until edited.
3. **R91/2b — the Salon revisit is still yours, and the number is now 1.8%.**
   Reported, not acted on. What changed is the reading, not the verdict: the
   committed arm could not remove the confound because there was no
   salon-specific confound — the baseline already drafted the salon plan. Two
   arms, 68 metered fights, the stage staffed once.
4. **The Fanfare early-half prediction is half-graded and the missing half
   needs one small arm.** A no-plan drafter is the contrast "where Salon does
   not" requires. It is a P1.5-shaped item next to the chosen-seed arm; not
   started here on purpose.
5. **`docs/track-b-curves.md` cannot be regenerated** — its inputs are
   gitignored per-worktree logs and the corpus behind the published 87 records
   no longer exists in one piece. Options, none taken: commit the fight records
   (small, and they stop being per-machine), write them to a stable path
   outside any worktree, or accept the document as a dated artifact and say so
   in it. This is a repo-shape decision.
6. **Three traversal defects (13, 14, 15) are queued and unfixed**, per the
   routing you accepted. The next traversal pass owns them.
7. **Punch Off stays SUSPECTED-OURS with seed `8B97LMCL2F` as its fixture**,
   and the animation stream's note carries one measured starting point: the
   router connects no signals at all.

## Stop-and-surface

1. **The soak was filing bot play into the human feed, and had been since the
   hook shipped.** The label depended on the operator's shell. Nothing was lost
   — last night's runs happened to be labelled correctly — but the failure mode
   is silent and lands in the one feed whose value is that a person produced
   it. Fixed. The general shape is worth keeping: *a default that is right only
   because of how somebody happened to invoke it is not a default.*
2. **Both writers record every soak fight, and a reader that groups by feed
   double-counts.** Named and cuttable now, but every fight count published
   from a mixed corpus before this is a count of RECORDS.
3. **The committed-Salon arm was not a new condition.** It cost three runs to
   discover that `policy_v0.ARCHETYPE` has been `"salon"` since Phase 0 — which
   is also why the baseline's own Salon share is the highest of the three
   archetypes. Any future arm that means to contrast with the baseline should
   check what the baseline's plan already is first.
4. **Debt #3 bounds what a committed arm can be.** A run that dies in act 1
   drafts a handful of cards onto a starter deck; the committed arm made
   Fanfare 24.9% of plays and could not make it the majority. No flag can while
   the bot dies on floor 14.
