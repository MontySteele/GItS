# Sprint log — Track B: the two feeds and the first curves (2026-08-04)

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

Session: the hand-back note of 2026-08-04 evening
(`docs/handback-note-2026-08-04.md`), executed in order. Worktree G4.
Item 1 (the clean N=3) is recorded as **R98** and in
`docs/sprint-understudy-p1-log-2026-08-04.md`; this log is **Item 2**.

Charter: `docs/axis-validity-session-charter.md` §4. Deliverables: **B1** the
demand curve, **B2** the output curves over it, both from **two feeds**, both
labelled with their feed, and every empty cell left empty.

Status: **B1 and B2 SHIP for Act 1 on the bot feed. Acts 2 and 3 are EMPTY and
stay empty until the human feed plays there.** The generated document is
`docs/track-b-curves.md`; it regenerates with
`python tools/track_b_curves.py --out docs/track-b-curves.md`.

---

## What landed

| item | where |
|---|---|
| The human feed (C#, on by default, no UI) | `klee-mod/KleeCode/Diagnostics/PlayTelemetry.cs` |
| Its registration, on the single hook chain | `klee-mod/KleeCode/KleeMod.cs` |
| Bot-feed telemetry additions (pool, meters, end-of-turn block, feed labels) | `understudy/soak.py` |
| B1 + B2 generator | `tools/track_b_curves.py` |
| The curves | `docs/track-b-curves.md` |
| Tests | `tier0/tests/test_track_b_curves.py` (15) |
| Schema, now a live shared surface | `understudy/README.md` |
| The hand-back note, verbatim | `docs/handback-note-2026-08-04.md` |

**Nothing in `tier0/`, `tier05/`, the drafter or any sheet moved.** No balance
value, no card, no floor, no axis disposition, no drafter price. The only
number this pass added to the C# side is a schema version string, and the
constant-parity lint confirms it: 71 mirrored, 16 declared unmirrored,
unchanged.

## The two feeds, and why the second one had to exist

Understudy debt #3 — the bots die in Act 1 — caps the **bot** feed and nothing
else. A demand curve for Acts 2 and 3 needs somebody to reach Acts 2 and 3, and
the only instrument that does that is [USER] at the table. So Track B is built
on two feeds writing **one schema**:

| | bot feed | human feed |
|---|---|---|
| written by | `understudy/soak.py` (policy_v1) | `klee-mod/KleeCode/Diagnostics/PlayTelemetry.cs` |
| tagged | `feed: "bot"`, `source: "soak"` | `feed: "human"`, `source: "mod"` |
| seats | 1 | as played — one record PER SEAT |
| density | dense and cheap | sparse, on the table's schedule |
| reach | Act 1 | wherever the run goes |
| attribution | enemy HP drop observed after an action | the damage hook itself, with dealer and card |

**Zero friction was a requirement, not a preference.** The hook is on by
default in normal play, has no UI, no toggle and no export step, and writes to
`user://gits_telemetry/` — `%APPDATA%/SlayTheSpire2/gits_telemetry/`. It is
*outside* the mod directory on purpose: `deploy.ps1` deletes and re-copies
`mods/klee`, so the KleeArt idiom (write beside the dll) would destroy the log
at exactly the moment it holds the newest data. A test pins the path.

**Three rules the hook obeys**, in the order that breaking them costs:

1. It never touches game state and never consumes game RNG. Co-op is
   deterministic lockstep; a desync caused by a *measurement* would be the
   worst defect this repo has shipped.
2. Every entry point is wrapped. An exception out of a combat hook lands in an
   async continuation and takes the run with it (finding 21's failure mode).
   And `Subscribe` is wrapped too, because it runs inside the roster's single
   hook delegate — a throw there would disable the aura, resource and garment
   hooks concatenated beside it.
3. The JSON is hand-written, not reflected. The key names **are** the shared
   schema; a serializer deriving them from field names would turn a C# rename
   into a silent cross-session break.

## Cross-session note — the telemetry schema is now a LIVE shared surface

Filed here per D4/D5 and the house pattern (`docs/animation-sprint-2-log.md`).
P1's note said this section was "a heads-up rather than a cross-session note,
because Track B has not started reading it". **Track B has now started reading
it**, so the heads-up is discharged into the real thing.

**Who reads and writes the surface, as of this commit:**

| surface | role |
|---|---|
| `understudy/soak.py` → `FightTelemetry.as_record` | writer (bot) |
| `klee-mod/KleeCode/Diagnostics/PlayTelemetry.cs` → `FightRecord.ToJson` | writer (human) |
| `tools/track_b_curves.py` | reader (B1/B2) |
| `understudy/report.py` | reader (the morning report) |

**The rule, restated where it now bites:** *adding* a key is free; *renaming or
repurposing* one is a cross-session change that takes its note first. Two
writers in two languages cannot see each other, so
`tier0/tests/test_track_b_curves.py::test_the_two_feeds_write_the_same_fight_record`
compares the key sets directly and names each permitted asymmetry
(`potions_used` is bot-only — no first-party potion hook exists for the mod
side; `character`, `ts` and `reactions_by_turn` are mod-only). A drift in either direction is a red
test, not a discovery six weeks later.

**What changed under that rule in this pass — all ADDITIONS:** `schema`,
`feed`, `source`, `seats`, `seat_index`, `character`, `enemy_pool_by_turn`,
`meters_by_turn`, `block_at_turn_end`, `reactions_by_turn`. Nothing was
renamed. Logs written before
today carry none of them, and the reader treats a missing `feed` as `bot`
rather than as unlabelled — which is what those logs are.

**Three measurements the additions buy, and why each was not already there:**

- `enemy_pool_by_turn` — *the honest output curve*. `damage_by_source` credits
  the play the reader happened to observe next, and demonstrably under-counts:
  in the first validation soak a fight with 44 HP of enemies attributed 33. The
  pool's own drop between two turn openings cannot under-count, because it does
  not care who did it.
- `block_at_turn_end` — block sampled at the turn OPENING is whatever survived
  the enemy's turn. That is a different quantity wearing the same word, and the
  wrong one to lay over a demand curve.
- `meters_by_turn` — the instrument the Salon pre-registration names. Read by
  power ID, not by title: a display name is loc data and moves with a wording
  pass. **Encore reads `-1` on the bot feed, which means UNSEEN and not empty**:
  `EncoreMeterPower` was retired as a display (animation sprint 2, E1) and the
  live value is a CustomResource the bridge does not serialise. The human feed
  reads 5, 10 and 8 on turns the bot feed cannot see at all, which is how the
  lie was caught.
- `reactions_by_turn` — the hand-back's *"reaction events MAY ride the schema if
  the field is cheap now"*, taken up because it was: `ReactionEffects.
  TotalResolved` already exists, so the field costs one read per turn.
  **Measurement only — no reaction constant is read, written or moved.** The
  counter is GLOBAL rather than per-player, so in co-op both seats' reactions
  appear in every seat's row; that is in the schema table, because a reader who
  did not know would divide by the wrong denominator.

## Guardrail 7, enforced rather than promised

Every table in `docs/track-b-curves.md` is headed with its feed, the two feeds
are never averaged, and `--` means *no fight of that shape has been recorded by
that feed*. Tests hold all three: one asserts the banner and the R14 reference
survive, one asserts no row mixes feeds, one asserts an act with no data
renders empty **and is named as empty** rather than quietly interpolated from
its neighbour. A bot-feed number is a **bot-limited floor** — what a heuristic
with declared reductions managed on read-back seeds, not what the fight demands
of a person.

## The pre-registrations, GRADED BEFORE ANYTHING WAS READ INTO THE RUN

Both carried in from R89/R95 via §7.8 of the Track A log. The grading rule was
fixed before the numbers existed: **grade only where the data supports it, and
name the instrument where it does not.**

Sample: **87 fight records, 77 monster and 10 elite, all Act 1, all bot feed**,
across four soaks (`20260804-221045`, `-222105`, `-224517`, `-225937`). 56 of
them carry meter samples — the counter landed mid-session, and a fight without
a sample is counted nowhere rather than as a zero.

### Pre-registration 1 — Fanfare shape, EARLY half (R90/1b, via §7.8)

> *In Act 1, Fanfare-archetype output in fight-turns 1–3 falls short of the
> demand curve where Salon does not.*

**GRADE: NOT GRADED — and the reason is the instrument, not the data volume.**

B2 as built measures **cards**, not **archetypes-as-decks**. policy_v1 drafts,
so every deck in this sample is a mixed deck: in fight-turn 1, 224 of the 299
recorded plays are `generic` — base-game, colorless and companion cards with
no Furina archetype at all — against 28 fanfare and 27 salon. A per-turn
archetype total from a mixed deck cannot separate *this archetype produces too
little* from *this deck drafted little of this archetype*, and the claim is
about the first. Grading it from these rows would be reading a draft
distribution as a design finding.

**What the data does say, descriptively and not as a grade** (bot feed, act 1,
attributed damage per play — attribution-limited, and the denominator is
`cards_played`):

| turn | salon | fanfare | demand (monster, required output/turn) |
|---|---|---|---|
| 1 | 86 over 27 plays = 3.2 | 96 over 28 plays = 3.4 | 10.6 |
| 2 | 97 over 39 plays = 2.5 | 66 over 28 plays = 2.4 | 10.6 |
| 3 | 87 over 24 plays = 3.6 | 56 over 24 plays = 2.3 | 10.6 |

The two archetypes are the same size per play in turns 1–2 and Fanfare is
lower in turn 3 — a difference far inside what an uncontrolled draft can
produce on its own. **The prediction's direction is not contradicted and not
supported. It is unmeasured.**

**Instrument named, per the standing rule that a null names its replacement:**
an **arm-controlled** feed. Three candidates, in cost order — (a) human-feed
sessions with the deck's intent DECLARED, which needs one line from [USER] per
run and nothing else (gate item); (b) a soak arm that starts from a fixed
archetype deck, which policy_v1 cannot do today and which is P1.5-shaped work
next to the chosen-seed arm R95 already gated; (c) tier-0.5's existing
archetype arms, which are a SIM instrument — and R90 already ruled that
pointing this question at the sim was aiming at the wrong instrument.

**LATE half: PENDING, as instructed.** *Underwhelming damage late* wants Act 3,
Act 3 wants the human feed, and the human feed has recorded nothing yet. The
instrument is named and built; the data is owed by play, not by code.

### Pre-registration 2 — Salon fill time (R91/2b, via §7.8)

> *The turn the Salon first reaches cap, and the fraction of fight-turns it
> sits full.*

**REPORTED. Bot feed, act 1, 56 fights carrying a meter sample:**

| measure | value |
|---|---|
| fights where the Salon reached cap (3) | **0 of 56** |
| median turn first at cap | **no such turn** |
| fraction of fight-turns at cap | **0.0%** |
| median peak members | **1 of 3** |

**What this is: a bot-limited floor, and an unusually literal one.** It is not
"the Salon fills slowly" — it is "**this policy never filled it**", median peak
one member. policy_v1 drafts what the offers give it and plays what it drafted;
a stage it never staffs is a fact about the pilot before it is a fact about the
Salon.

**It therefore does NOT discharge R91/2b's revisit condition, in either
direction.** That condition reads: *if bounded-meter readers plateau early on
Track B's output curves, the `scaling` tag for those readers is re-argued WITH
DATA*. A plateau needs a curve of a filling meter, and there is no fill here to
plateau. **No tag is revisited, nothing is proposed, and the number is reported
exactly as pre-registered** — which is what "report the number, do not revisit
the tags yourself" asks for.

The instrument that would discharge it is the same one Pre-registration 1
needs: a feed where a Salon deck is actually assembled and played. The human
feed does that by construction the first time [USER] plays one.

### One thing the grading exposed about the bot feed itself

Three quarters of this pilot's recorded plays are `generic`. That is not an
archetype finding either — but it does mean **the bot feed's value to Track B
is B1, not B2**. Demand is a property of the fight and the bot measures it
honestly by standing in front of it; output is a property of a deck, and this
bot's deck is nobody's deck. Recorded here so the next reader does not go
looking for archetype conclusions in the dense half of the data.

## What the four soaks cost in defects, and what they were

Twelve runs across four soaks. The validation soak (Item 1) and the final soak
were both clean N=3; the data soak filed three, none of which halted it (the
stop-and-surface rule needs TWO of the same shape).

| # | shape | what it was | state |
|---|---|---|---|
| 11 | `bridge_unreachable` misfiled | a crashing process still read alive | **FIXED** (R98) |
| 12 | `no_progress` (cycle) | selecting a bundle opens a PREVIEW; Neow's Scroll Boxes ended a run at 16 actions | **FIXED**, red test |
| 13 | `no_action` | the bridge answered with no `state_type` at all mid-transition; the driver filed rather than re-read | **FILED, not fixed** — routed to the harness backlog |
| 14 | `bridge_unreachable` (timeout) | the wire stopped answering while the process stayed alive through the full grace period — the FIRST time this kind was filed correctly rather than as a crash | **FILED, not fixed** — one observation, no reproduction |

13 and 14 are traversal-layer, the expected class, and neither was fixed here:
Item 2's job was the curves, and a harness the pass keeps re-opening is a
harness nobody can quote a clean run from. Both are in the debt list and the
gate package.

**Routing ACCEPTED 2026-08-04 (R99/3).** The gate package took the disposition
as offered: traversal-class per debt #1, filed with reproduction, deliberately
unfixed, **owned by the next traversal pass**. Registered in
`docs/backlog-2026-07-29.md` §1 under "Understudy harness — traversal layer",
which is where this repo's queues actually live. Nothing about them changed in
the pass that recorded the acceptance.

**The final soak re-validated the harness at HEAD**, not only at the commit
R98 was earned on: 3 runs, 10 fights, zero defects, ledger fully REVERTED. That
matters because the telemetry additions and the bundle fix landed after R98's
soak, and a validation that only ever held two commits ago is a validation
somebody will have to re-do.

## The human feed's one declared blind spot

**It cannot see a win.** The game exposes no first-party combat-END hook, so a
fight the player wins is closed by the NEXT fight's stale-flush and reads
`interrupted`. Two consequences, both handled rather than hidden:

- `hp_end` is the last reading taken **while the fight was live**. Without that
  the ledger charges the fight for the campfire in between, and the first
  run-verification proved it: a fight that took 6 damage was recorded as
  costing 59 HP.
- `died` is exact (the player's own death is observable); `won` is not
  distinguishable from `interrupted`, and the schema says so.

The named instrument for closing this is a Harmony postfix on
`CombatManager.EndCombatInternal` / `CheckWinCondition`. It is not written
here: the mod has never patched combat lifecycle, the method is reached through
an async continuation (finding 21's neighbourhood), and adding a patch there to
improve a LABEL is not a trade this pass should make unsupervised.

> **RETRACTED 2026-08-04 (late), R100/5 — and the retraction is about the game,
> not about the consequence.** The consequence was real and is now closed. The
> claim above it — *"the game exposes no first-party combat-END hook"* — was
> simply false, and the only reason it stood is that nobody decompiled the
> method before writing it down. `CombatManager.EndCombatInternal` calls
> `Hook.AfterCombatEnd(runState, combatState, room)` and then
> `Hook.AfterCombatVictory(...)`; both walk
> `runState.IterateHookListeners(combatState)`, the same iteration that had
> been delivering `BeforeCombatStart` to `PlayTelemetryHooks` all along. So the
> label cost two `AbstractModel` overrides, **no Harmony patch and no async
> continuation of our own**, which is a strictly better trade than the one this
> section declined to make. The instrument named here was more expensive than
> the one that existed; naming an instrument is not the same as checking
> whether it is needed.

## Reversibility ledger — game-directory changes this session

| # | change | undo | state |
|---|---|---|---|
| 1 | `steam_appid.txt` created at the game root (three soaks) | `Remove-Item steam_appid.txt` | **REVERTED** by each soak's teardown |
| 2 | `mods\STS2_MCP\` deployed from the vendor pin (three soaks) | `.\build\deploy_bridge.ps1 -Remove` | **REVERTED** |
| 3 | `SlayTheSpire2.exe` launched directly (three soaks) | terminated at teardown | **REVERTED** |
| 4 | `FastMode=Instant`, `TimeScale=3.0` via the speed endpoint | `POST {"enabled": false}` | **REVERTED** on soaks 2 and 3; **NOT REVERTED** on soak 1 (the bridge was gone — the game had died). Leak-checked and clean: soak 2 captured `fast_mode: "Fast"` at setup, so `Instant` never reached `settings.save` |
| 5 | `mods\klee` replaced: **0.2-247 → 0.2-289** | `git checkout 0691724 && cd klee-mod && .\build\deploy.ps1` | **STANDING BY DESIGN** — the human feed cannot record [USER]'s sessions from a build that does not contain it. In the gate package. |
| 6 | `user://gits_telemetry/` created (`%APPDATA%/SlayTheSpire2/`) | delete the directory | **STANDING BY DESIGN** — this is the human feed's log directory |

Entry 5 is the one that is not self-reverting, and it is deliberate: the point
of a zero-friction hook is that it is already there the next time [USER] plays.
It is a **content-identical build plus a read-only hook**, validated by
`validate.ps1` (OK, all rules) on a clean tree — but it is a build change to
the game [USER] plays, so it goes in front of them rather than in a footnote.

Worktree-local, gitignored, and NOT repo changes: `klee-mod/local.props` and
`game_ref/` copied from the main checkout; `ImageGen/images/` copied and
`.venv` / `art/raw` junctioned so `deploy.ps1`'s own gates (S6*, S7, S10) could
actually run rather than skip.
