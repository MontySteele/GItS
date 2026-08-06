> **MOVED 2026-08-06 — Clear the Stage, Track R-B (charter R119, rail 1).**
> Old path: `docs/sprint-understudy-p15-log-2026-08-05.md` — new path: `docs/archive/sprint-understudy-p15-log-2026-08-05.md`.
> Verbatim move: everything below this banner is byte-identical to the
> pre-move file. Citers repointed in the move commit; see
> `review/stage-clear/rb-move-manifest.tsv`.

# Sprint log — Understudy P1.5, the bridge fork (2026-08-05)

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

Promoted at **R104**: three independent demands converge on one fork —
chosen seeds (R95's original gate), resource/meter visibility on the wire
(R100/6b's binding condition), and selector recording (R103(b)'s C2 probe and
family B's blind turn-1 Fanfare channel). One work item, three payoffs, and
the scope did not grow with the promotion.

**Everything below is plumbing and measurement. No design authority was
exercised and none was needed.** Guardrail-7 is untouched: nothing this pass
produced is a balance conclusion, and the two identical traces at the bottom
prove the *harness* is deterministic, not that anything about the game is
good.

---

## What shipped

| item | mechanism | where |
|---|---|---|
| 1 CHOSEN SEEDS | `POST /api/v1/gits/seed` on the forked bridge, fired between the character pick and the embark confirm; verified by read-back | `vendor/STS2_MCP/gits/GitsSeed.cs`, `understudy/bridge.py`, `understudy/soak.py` |
| 2 RESOURCE VISIBILITY | `player.resources` on the wire — a reflection read of BaseLib's own custom-resource registry | `vendor/STS2_MCP/gits/GitsResources.cs`, one line in `McpMod.StateBuilder.cs` |
| 3 SELECTOR RECORDING | `fight.selectors` — every selector answer with the offers it was chosen from | `understudy/soak.py` |
| (reader) | `understudy/trace_replay.py` — reconstruction and trace comparison | new file |

---

## Item 1 — the seed route, and the guard that was not describing the game

**Upstream already had a seed parameter and it already refused.**
`McpMod.Actions.ExecuteCharacterSelectMenuOption` applies a seed with
`charSelect.Lobby.SetSeed(seed)`, behind a `charSelect.Lobby == null` guard
whose message is *"Seeded embark is not supported for standard singleplayer
from this API"*. Phase-0 hit exactly that message and recorded the whole route
as unreachable; `understudy/soak.py::_embark` still carries the note.

**The decompile disagrees with the guard**, v0.107.1:

```
NCharacterSelectScreen.InitializeSingleplayer()
    _lobby = new StartRunLobby(GameMode.Standard,
                               new NetSingleplayerGameService(), this, 1);

StartRunLobby.SetSeed(string? seed)
    if ((uint)(NetService.Type - 1) > 1u) throw;   // Singleplayer=1, Host=2
```

Singleplayer has a lobby and `SetSeed` accepts singleplayer. So the guard is
defensive, not descriptive — but this pass **did not touch upstream's arm**,
because a fork that rewrites an upstream refusal owns that refusal forever.
It added its own endpoint instead, which fires *before* the confirm upstream
performs.

**Two routes were built; ONE fires in practice, and that is the measured
result rather than the designed one.** Both land on the same line in
`StartRunLobby.BeginRunForAllPlayersIfAllReady`:

```
string seed = NGame.Instance?.DebugSeedOverride != null
    ? NGame.Instance.DebugSeedOverride
    : (Seed == null ? SeedHelper.GetRandomSeed()
                    : SeedHelper.CanonicalizeSeed(Seed));
```

The endpoint prefers `lobby` (`charSelect.Lobby.SetSeed`) and falls back to
`debug_override` (`NGame.Instance.DebugSeedOverride`). **Across three live
runs the route that fired was `debug_override` every time** — the lobby was
not reachable from the endpoint's vantage at the moment the seed goes on,
which is the same fact Phase-0 recorded from the other side. The lobby arm is
kept rather than deleted: it costs four lines, it is the channel the game's
own Custom-run screen uses, and if a later pin makes it reachable the endpoint
will simply report `route: "lobby"` instead. **Nothing downstream reads the
route except the log**, so a change of route is not a change of behaviour.

**Three things the mechanism needs that are the game's constraints, not ours:**

1. **The moment.** `NCharacterSelectScreen.AfterInitialized()` sets
   `DebugSeedOverride = null` as the screen opens. A seed set earlier is wiped
   by the screen it was chosen for; the run is generated inside the confirm,
   so there is no later. The seed goes on *after* the character pick and
   *before* the confirm, and the test pins that ordering.
2. **Canonicalisation is asked for, never retyped.** `SeedHelper` upper-cases
   and maps `O`→`0`, `I`→`1`. The requested seed `P15BRIDGE1` becomes
   `P15BR1DGE1`, and the run reads back the canonical form. The harness takes
   the canonical string back from the endpoint's reply rather than
   reimplementing the mapping — one copy of somebody else's rule instead of
   two.
3. **The override is GLOBAL and STICKY.** Left set, every later run in the
   session is the same run, including one a person starts by hand. The
   reversibility ledger carries the release, the release runs
   unconditionally and first, and it is declared lazily so `--no-setup`
   (which makes no game-dir changes) still gets an undo on the ledger.

**The read-back is the verification, and it is a defect rather than a
warning.** A chosen-seed soak whose runs quietly rolled their own seeds is the
one failure a build-vs-build comparison cannot survive *and cannot detect
afterwards* — both builds would simply have been measured on different runs.
`seed_not_honoured` is filed harness-side (the game rolling its own seed is
the game behaving normally; what failed is our claim to have chosen one), so
two of them halt a soak.

**R95's read-back arm is unchanged and is still the default.** No seed is
passed on the embark verb in either arm; the existing test asserting that is
still green and now says why it is still worth asserting.

## Item 2 — the meters, and the sentence that was wrong

`understudy/soak.py` carried this: *"ENCORE IS NOT ON THE WIRE AND CANNOT
BE."* It was right about the wire and wrong about "cannot". `BuildPlayerState`
walks `creature.Powers`, so a meter with a badge is visible and a meter
without one is not; `EncoreMeterPower` was retired as a display in animation
sprint 2 (E1), and Encore left `Powers` with it. Every bot fight since has
recorded `encore: -1`.

**What the fork reads, and why it is generic.** BaseLib registers every custom
resource in one list (`CustomResourcePatches.RegisteredResources`), each entry
carrying an `Id` and a `Func<PlayerCombatState, CustomResource>`. The fork
walks it and emits `{ resource id -> amount }`. It knows nothing about Furina,
about klee, or about any particular mod — `KLEEMOD_ENCORE`,
`KLEEMOD_FANFARE`, `KLEEMOD_FANFARE_FLOOR`, `KLEEMOD_FANFARE_CAP_BONUS` and
`KLEEMOD_FURINA_BURST` arrive by construction, and so does anyone else's.
**Reflection rather than a reference is deliberate**: the registry is
`internal` and BaseLib is a Workshop mod that may be absent, so a compile-time
reference would make the bridge refuse to load without it. A missing BaseLib
means an empty map, which is the truth.

**-1 survives, and the distinction is load-bearing.** A MISSING `resources`
key means "this bridge predates P1.5" and still reads UNSEEN. A key that is
PRESENT with no Encore in it means a player who has no Encore, and reads 0.
Those are different facts and a reader is entitled to tell them apart.

**Fanfare now reads from the resource, not the badge.** The badge is *synced
from* the resource at known hook sites, so between two sync moments the badge
is the stale copy. The badge remains the fallback for an older bridge.

**The salon cap was cheaper than anybody thought.** The P1 note said the live
cap "is not on the wire at all". That was true of the CAP and false of its
only addend: the live cap is `SalonConstants.MemberSlots (3) +
SalonCapUpPower.Amount`, and `SalonCapUpPower` is an ordinary `PowerModel`
sitting in the status strip that the harness was already reading. Zero C#; the
column now follows Casting Call.

**Measured, in the acceptance run's first fight** (`meters_by_turn`, columns
`[round, fanfare, salon, salon_cap, encore]`):

```
[[1,0,0,3,0],[2,5,0,3,0],[3,13,0,3,0],[4,12,0,3,0],
 [5,22,1,3,0],[6,23,1,3,4],[7,24,2,3,2]]
```

Encore reads 0/0/0/0/0/4/2 where it read `-1` seven times before. **These are
telemetry readings, not a finding.** No claim about Furina's meters is made or
implied here; the point of the pass was to make the column readable, and R100/
6b's precondition is what is discharged, not the question behind it.

## Item 3 — the selector channel

Furina's Ethereal Spotlight opens a `card_select` on every one of her turns,
and the Center Stage / Guest Cast answer is that turn's whole Fanfare posture.
The fight record could not see it: `cards_played` records plays, and a
selector answer is not a play.

`selectors` is `[round, screen_type, index, chosen name, offered names]`.
**The offered list is in the row for the same reason `hand` travels with a
card play**: "Center Stage" means one thing against
`[Center Stage, Guest Cast]` and nothing at all against a list that did not
contain Guest Cast. A choice is not reconstructible from what was taken alone.

Recorded on the state it was made from (S7 family A, R101) — the screen a
selector closes into is not where the choice happened. `overlay` is excluded
from the recorded set on purpose: it is the shape a soft-lock takes, and a
screen nobody can answer has no choice to record.

**One defect found and fixed by the live run**: the same screen reached by two
verbs wrote `NCombatPileCardSelectScreen` on one row and the lowercased form
on the next, because `naming.describe` lowercases and the blob fallback did
not. Two spellings of one screen, in the channel whose entire job is to be
compared. Pinned by a test.

## The reader — `understudy/trace_replay.py`, and a name collision

> **ANSWERED 2026-08-06 (Class-P, R119 / P-B item C-2 — dated annotation; the
> frozen prose below is untouched).** The module the acceptance clause meant is
> **`understudy/trace_replay.py`**, confirmed from this section's own stated
> evidence (*"reconstruction only, no rules retyped"* describes the recording
> comparator, not the engine driver). The red-pen flag below asked for
> authority, not evidence; the Class-P charter supplies it. Queue row: 10.5,
> struck. Ledger: `docs/registry/p-ledger.md`.

**It did not exist, and then it did, and it was somebody else's.** The P1.5
spec's acceptance clause says "`understudy/replay.py` can consume the new
fields (extend it minimally if needed)". There was no such file at the commit
this branch started from (`7835bcd`). One was built here — and while it was
being built, **the merge train landed `understudy/replay.py` on `main` from
the S7 fidelity audit**, a different instrument wearing the same word:

| module | what it reads | what it does |
|---|---|---|
| `understudy/replay.py` (S7, landed) | soak logs **and tier0** | drives the sim through the recorded action sequence, diffs the two instruments' numbers |
| `understudy/trace_replay.py` (P1.5, here) | soak logs only | reports whether two RECORDINGS of one seed agree |

**The landed file keeps the name; this one moved.** That is the mechanical
resolution, not a judgement about which module the spec meant — and it is a
real question, because the clause's own words are *"reconstruction only, no
rules retyped"*, which describes `trace_replay` and not the module that drives
an engine. **Flagged for the red pen; deliberately not decided here.** Both
modules exist, neither was altered by the other, and the trial merge with
current `main` is otherwise clean.

**It simulates nothing and never will.** No damage formula, no meter law, no
draft score is retyped. It reads two JSONL logs the soak wrote and reports
whether the recorded traces agree. A reconstruction that computed what SHOULD
have happened would be a third engine, and the repo already has all the
engines it can keep honest.

The trace is `cards_played` + `selectors` + `meters_by_turn`.
`hp_trajectory` and the damage totals are deliberately **not** in it: they are
the OUTPUT a comparison exists to measure, and folding them into the identity
would make every interesting result an inequality of the thing being compared
with itself.

---

## Acceptance — pre-registered, and met

**Bar:** *a recorded selector trace on a CHOSEN seed replays deterministically
— run a short scripted/bot fight on a chosen seed twice with the same actions
and show the recorded selector choices + meter readings are identical.*

| | |
|---|---|
| requested seed | `P15BRIDGE1` |
| canonical seed, both runs | `P15BR1DGE1` (read back, `honoured: true`) |
| route that fired | `debug_override`, both runs |
| actions | **87**, both runs |
| fights recorded | 2, both runs (`--max-fights 2`) |
| defects | 0, both runs |
| selector answers | 7 + 7, all recorded with their offer lists |
| encore column | read (was `-1` on every bot fight before this pass) |
| stamps | `20260805-115449` (A), `20260805-115620` (B) |

```
$ python -m understudy.trace_replay 20260805-115449 20260805-115620
REPLAY COMPARE  A=20260805-115449  B=20260805-115620

run 001: IDENTICAL  seed=P15BR1DGE1 (chosen P15BR1DGE1)

VERDICT: identical traces
```

**`--max-fights` was added for this and is off by default.** Comparing two
recordings of one seed needs a run that ENDS at a stated point in both, and
"when the bot happened to die" is not one. It is a clean stop, not a defect:
the open fight has already closed before the bound is checked, so the records
the comparison reads are complete records.

**What two identical traces prove and do not prove.** They prove the harness
is deterministic and the recording faithful — which is only true because
`understudy/rng.py` keeps the game seed out of the policy stream, so the
policy is a pure function of the wire state. They are not evidence about
balance, difficulty, fun or legibility, and no number in this document is
quotable as one.

## Game-directory restoration

| | before | after |
|---|---|---|
| `mods/` | klee, quick_fingers, STS2AutoSlayMod | klee, quick_fingers, STS2AutoSlayMod |
| `steam_appid.txt` | absent | absent |
| game process | not running | not running |
| `settings.save` mtime | 2026-08-04 18:59:24 | 2026-08-04 18:59:24 (untouched — no FastMode leak) |
| resumable run on the profile | none | none |

All five reversibility-ledger entries read **REVERTED** on every run,
including the new seed-release entry.

---

## Cross-session note — the telemetry schema gains one bot-only key

Filed per D4/D5 and the house pattern (`docs/animation-sprint-2-log.md`,
`docs/sprint-track-b-curves-log-2026-08-04.md` §"Cross-session note"). The
telemetry schema has been a LIVE shared surface since 2026-08-04.

**The rule, unchanged:** *adding* a key is free; *renaming or repurposing* one
is a cross-session change that takes its note first.

**What changed under that rule in this pass — one ADDITION, no renames:**

| key | writer | reader |
|---|---|---|
| `selectors` | `understudy/soak.py` (bot feed only) | `understudy/trace_replay.py`; available to `tools/track_b_curves.py` |

`schema` stays `"1"`: additions do not bump it, and a test asserts that
together with the continued presence of every P1 key.

**`selectors` is a DECLARED ASYMMETRY, listed in
`tier0/tests/test_track_b_curves.py::BOT_ONLY` beside `potions_used`.** The
soak records a selector answer because it POSTED it — the choice passes
through the harness by construction. The mod has no equivalent vantage: a
person answering a `card_select` resolves it inside the game's own screen, and
`PlayTelemetry` sees a card leave a pile, not an offer being taken from a
list. **Consequence for any reader: a selector cut is a BOT-FEED cut**, and a
Track B curve built on it must be labelled accordingly. Closing the asymmetry
means hooking the selection screens on the mod side; that is a piece of work
and it is not this one. Surfaced, not smuggled.

**One change of MEANING, called out as loudly as a rename would be:**
`meters_by_turn`'s encore column and salon-cap column both stopped lying by
omission. A reader who treated `encore == -1` as "the bot cannot see Encore"
was right yesterday and is right only for pre-P1.5 logs today; a reader who
treated the cap column as the printed 3 was right yesterday and is wrong today
on any run that played Casting Call. **Neither key was renamed and neither
changed type.**

## The vendored fork, recorded as a fork

`tools/lint_vendor_pin.py` expresses a local fork exactly and no new
vendoring pattern was needed. Pin `55e0648` is unchanged; the snapshot is
byte-identical to upstream apart from:

| file | status | change |
|---|---|---|
| `McpMod.cs` | `gits-modified` | one route arm, `/api/v1/gits/seed` |
| `McpMod.StateBuilder.cs` | `gits-modified` | one line in `BuildPlayerState` |
| `gits/GitsSeed.cs` | GItS addition | item 1 |
| `gits/GitsResources.cs` | GItS addition | item 2 |

`PROVENANCE.md` §"What we changed" was rewritten from "one line, in one
upstream file" to the current three-lines-two-files, and the manifest was
regenerated with `--write`; **the manifest diff is exactly the two hashes and
the one status flip**, which is what reading the diff is for. Lint CLEAN over
17 carried / 3 ours. Build: 0 warnings, 0 errors, `net9.0`, against the same
game pin the vendoring recorded.

**The `BuildPlayerState` line is an edit rather than a Harmony patch for the
usual reason and one more:** a resources map attached out-of-band would not be
ATOMIC with the state read it belongs to, and a meter read a frame after the
hand it describes is a different measurement.

---

## Surfaced — things this pass did NOT decide

1. **`selectors` on the human feed.** Declared BOT_ONLY above. Needs a mod-side
   hook into the selection screens; costed at more than "minimal", so not
   taken. Until it lands, `PlayTelemetry` and the bot feed disagree about this
   key by design and the parity test says so.
2. **The `lobby` seed route never fired.** `debug_override` carried all three
   live runs. The lobby arm is retained and reports itself; nobody should read
   "two routes work" out of this pass.
3. **`understudy/replay.py` NAME COLLISION.** It did not exist at this
   branch's base; S7's landed on main mid-flight. Ours moved to
   `understudy/trace_replay.py`. Which module the acceptance clause meant is
   a red-pen question -- see the section above.
4. **The live salon cap is now correct; the salon MEMBER LIST still is not.**
   The wire carries the member count and this pass did not add the roster.
   Nothing needed it; recorded so the next reader does not assume it is there.
5. **`GitsResources` reads BaseLib internals by reflection.** A BaseLib update
   that renames `CustomResourcePatches.RegisteredResources` degrades this to
   an empty map — silently, by design, because a state read must never throw.
   The `GD.Print` on a failed probe is the only tell. If the encore column
   goes back to reading 0 across a whole soak, look here first.
