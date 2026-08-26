# understudy/ — the bot playtest apparatus

Opened 2026-08-04 by the Understudy sprint. Brief:
`docs/understudy-kickoff-brief.md`. P0 findings and the three ratified
rulings: `docs/archive/understudy-p0-findings.md`. Phase-0 measurement:
`docs/understudy-phase0-report.md`. The Phase-0 skim response, signed:
`docs/understudy-countersign-2026-08-04.md` (R93–R97 in `tier0/DECISIONS.md`).

This directory drives the **real game** through the vendored STS2MCP bridge
(`vendor/STS2_MCP/`). It is not a simulator and it must never become one.

| file | what it is |
|---|---|
| `bridge.py` | stdlib HTTP client for `localhost:15526`; the wire contract is `vendor/STS2_MCP/docs/raw-simplified.md` |
| `adapter.py` | wire JSON -> tier0 engine objects, with its fidelity losses enumerated in the module docstring |
| `deckwatch.py` | the deck reconstructed from combat piles; the wire hides it everywhere else |
| `policy_v0.py` | the counterfactual arm: delegates every decision to the live tier0/tier05 entry points, and returns *nothing* where it cannot delegate faithfully. **Frozen** — it is one arm of a published measurement, and editing it would retroactively move a quoted number |
| `policy_v1.py` | R93's seven approved revisions. The policy the soak flies |
| `committed.py` | R99/4b's archetype-committed DRAFT arm — a flagged variant, off by default. Membership comes off the design sheets, so the arm that builds a deck and the reader that grades it agree on what a Fanfare card is |
| `naming.py` | revision #7: resolved card / target / option NAMES per action |
| `rng.py` | the dedicated policy stream, and the refusal that keeps a game seed out of it |
| `harness.py` | `begin` / `state` / `act` — the Phase-0 measurement loop. Also `give-card` (EB-52's dev grant door) and `frame` (window capture, off by default); both are here and not in the soak on purpose |
| `soak.py` | **P1**: N unattended policy_v1 runs, telemetry, watchdog, reversibility. **P1.5**: chosen seeds, the encore column, the selector channel |
| `replay.py` | **S7**: drives tier0's combat model through a recorded action sequence and diffs the two instruments' numbers. It reads the SIM. **Track B**: `--use-selectors` reconstructs the Spotlight designation from `fight.selectors` instead of letting tier0's own heuristic stand in, and `--ledger` writes the per-turn Fanfare decomposition |
| `probe_block.py` | **Track B, probe B2**: a FIXED SCRIPT (no policy) that fixes the Spotlight answer, plays only cards whose wire text prints Block, and reads `player.block` at every decision point |
| `trace_replay.py` | **P1.5**: reconstruct a recorded fight and compare two recordings of one seed. It reads nothing but JSONL. Named apart from `replay.py` because the two are different instruments, not two halves of one |
| `hangwatch.py` | **EB-1**: the log-growth / message-pump watchdog. Tells a game that is alive and SPINNING from a wire that merely did not answer, so the spin stops being filed under a harness-side kind |
| `frames.py` | **OFF by default** (`GITS_UNDERSTUDY_CAPTURE=1`): one PNG of the game WINDOW, for [USER]'s art sittings. Material, never evidence — the guardrail rides on every manifest row |
| `report.py` | the morning report — defects, outliers, curves. No LLM |
| `analyze.py` | the Phase-0 divergence analysis |
| `logs/` | per-run decision JSONL; `phase0-<seed>.jsonl` (committed), `soak/` and `frames/` (gitignored) |

## The two rules this directory exists under

**Guardrail-7.** Every number a bot or an LLM produces here is a
**bot-limited floor**, in exactly the sense pilot-limited already means in
tier 0.5. No winrate, no HP curve and no damage figure from this directory is
a balance conclusion, and none of them are quotable as one. The apparatus
files defects and telemetry; it authors no design.

**No fun, ever.** A JSON-state agent cannot see the screen. Legibility,
readability, feel and fun remain [USER]-only instruments and nothing in this
directory may be read as evidence about them.

## Running the Phase-0 loop

Prerequisites: the bridge installed (`klee-mod\build\deploy_bridge.ps1`),
`steam_appid.txt` in the game root, Steam running, the game launched
directly from its exe.

```
python -m understudy.harness begin           # stamp the seed and speed
python -m understudy.harness state           # read the screen + policy_v0
python -m understudy.harness act '{"action":"end_turn"}' --why "..."
```

`act` recomputes the counterfactual at the current state *before* posting, so
a log line can never pair a choice with a policy answer from a screen that has
since moved.

### `give-card` — EB-52's dev grant door (attended loop only)

```
python -m understudy.harness give-card KLEEMOD-UNHEARD_CONFESSION --why "EB-52(a)"
python -m understudy.harness give-card "Unheard Confession" --pile hand --count 2
```

EB-52(a) owed one evidence shape — a Power played and the Fanfare floor rising
because of it — and its obstacle was **acquisition, not instrumentation**: the
floor has been on the wire since P1.5, and three live sessions could not get
one of the three rare Powers into a deck (six rare draws, P(0 hits) = 36%, an
ordinary miss). This verb removed that obstacle, and the shape was taken on
2026-08-13: `KLEEMOD_FANFARE_FLOOR` read 0 before `Unheard Confession` and 8
after it, one request either side of the play.

**Grant to `deck`, not to a combat pile.** A combat-pile grant lands in hand and
then throws on play (`must be added to a CombatState before playing it`),
wedging the fight — BACKLOG `EB-91`. The deck route is the one the evidence
above was taken through: grant, let the next combat build its piles, play the
card normally.

**Ids: use the exact printed Title, or `KLEEMOD-<SHEET_ID_UPPER>`.** The wiki
search this verb's own refusal recommends throws on every mod card
(`EB-92`), so it cannot be used to look one up; the grant response echoes the
real `card_id`, which is the cheapest way to learn a spelling.

It goes through the game's own acquisition path — `RunState.CreateCard` then
`CardPileCmd.Add`, the same two lines a card reward runs — and mints nothing.
It refuses multiplayer, refuses a combat pile out of combat, and does no fuzzy
matching (`/api/v1/wiki?query=` is the search surface). Full reasoning:
`vendor/STS2_MCP/gits/GitsGiveCard.cs`.

**A run that used it is not a run the generators produced.** Nothing measured
on it is comparable to any other run — not a winrate, not a floor reached, not
an HP curve. The endpoint stamps that sentence on every success, the verb
writes it onto the run log beside the grant, and `--why` is logged with it,
because a deck change nobody can account for later is worse than no smoke.

**It is deliberately not in `soak.py`.** The soak's claim is that its runs are
runs the game generated; a grant reachable from an unattended overnight loop is
a way for that claim to quietly become false while nobody is watching.
`tier0/tests/test_understudy_give_card.py` pins its absence there.

### `frame` — window capture (OFF by default)

```
GITS_UNDERSTUDY_CAPTURE=1 python -m understudy.harness frame --label salon-stage
```

One PNG of the **game window's** rectangle, written to the gitignored
`understudy/logs/frames/` with a manifest row naming the screen, act and floor
it was taken on. It exists so a sitting (`S4-G17`, `AS2-D5`, `AS2-B5`,
`AS2-E2`) can be given frames from moments the bot reaches cheaply and a person
would have to grind for — which is how EB-52's capture packet was assembled by
hand.

**Env-only and off by default**, the same shape and reasoning as
`GITS_ILSPY_TREE`: a leg whose output is material sitting on somebody's disk
must never be a default and must never be a path this repo chooses for you.
Frames are gitignored for the reason `art/g12_captures/` and
`art/eb52_captures/` are — a frame of the running game has Tier F art in it.

**The window's rectangle, never the whole desktop.** The rectangle comes from
the game process's own `MainWindowHandle`, and three states are named refusals:
no window, a zero-size rectangle, and a minimised window (Windows parks those
off-screen at a -32000 origin).

**Two routes, and on this build you have to name the one you want.** The
default asks the window for its own pixels (`PrintWindow`) and falls back to
reading the screen under its rectangle only if that comes back blank. On this
Godot/Vulkan window `PrintWindow` comes back neither blank nor complete — the
background and HUD chrome render, the **hand, the enemies and the prompt
caption do not** — so the blank test passes and every in-combat frame on the
default route is a partial. Set
**`GITS_UNDERSTUDY_CAPTURE_ROUTE=copyfromscreen`** (same family as
`GITS_UNDERSTUDY_CAPTURE`, env-only, an unknown value falls back to `auto`) to
pin the screen route, which does render all of it. Its honest limit is the old
one — it is the game's rectangle, not the game's pixels, so anything sitting ON
TOP of the game lands in the frame — which is why that route now raises the
game to the foreground for the grab and drops it back afterwards. Every
manifest row records the route that RAN (`copyfromscreen-forced` when pinned)
beside `route_requested`, and carries the guardrail either way.

**A frame is MATERIAL, not a finding.** Guardrail-7 and the no-fun rule are
not changed by the existence of a camera: nothing this directory derives from a
frame is a claim about look, legibility, readability or fun. That sentence is
`frames.GUARDRAIL` and it is written onto every row of the manifest — on every
row and not once in a header, because manifests get read in slices and
concatenated. Like `give-card`, the verb is on the ATTENDED harness only; the
soak takes no pictures.

## What policy_v0 will not answer

Three decision classes return no counterfactual and are excluded from the M2
denominator: events, boss-relic picks, and the Crystal Sphere minigame. The
reasons are in `policy_v0.NO_COUNTERFACTUAL`, and they are all the same
reason — the sim scores those by ids the wire does not carry, so any answer
would be a guess contributing noise to a number about judgment.

## policy_v1 — the seven revisions (R93)

| # | revision | where | what it changed |
|---|---|---|---|
| 1 | free expiring cards first | `_free_expiring` | a playable 0-cost Ethereal card is played before anything is scored |
| 2 | block-panic gate + kill line | `_gated_ladder` | the panic rung must show the Block on offer can dent the incoming, or that a kill removes more |
| 3 | map one ply deeper | `_map` | `leads_to` is on the wire; the reduction goes from depth 1 to depth 2, summed undiscounted as `route._plan` sums it |
| 4 | the potion arm | `_potion_arm` | `tier0.engine.potions.try_use_potions` is run against the reconstruction and the drink read back out of the diff |
| 5 | `next_fight` into the rest arm | `_rest` | the flag comes from the map lookahead in the memo instead of being hard-coded False |
| 6 | in-combat choice overlay | `_choice_overlay` | Center Stage vs Guest Cast on deck composition; other choose screens fall back to `score_offer` |
| 7 | resolved card NAMES | `naming.py` | every posted action carries the identity of what it names — **the P1 blocker** |

Two numbers live in `policy_v1` and nowhere else: `BLOCK_MATTERS_FRACTION` and
`COMPANION_SHARE_FOR_GUEST_CAST`. They are **bot-policy dials, not balance
constants**. They do not belong in `tier0/constants.py`, they are recorded per
run in the log so a log stays self-describing when they move, and no number
downstream of them is quotable as evidence about the game.

Draft, shop and the deck-management overlays were deliberately NOT revised:
Phase-0's divergences there were diagnosed as gaps in the SIM's scoring, and
R96 routed all three to their chartered streams. Re-deciding them inside
Understudy would be authoring design, which bots do not do.

## Running a soak (P1)

```
python -m understudy.soak --runs 20 --report
```

Setup and teardown are automatic and logged: `steam_appid.txt` created and
deleted, the bridge deployed and removed via
`klee-mod/build/deploy_bridge.ps1`, the speed setting captured and restored.
The reversibility ledger is written to
`understudy/logs/soak/reversibility-<stamp>.json` **before** each change lands
— a ledger written after the change is empty exactly when the process dies
mid-change, which is the one moment anybody needs it.

Steam must be running (the game is launched directly from its exe, which is
why the appid file is needed). Readiness is judged on the `options` key of a
menu state, **never** on `GET /`: the HTTP server answers about 20 seconds
before the main menu has buttons (R97/5a). `--no-setup` attaches to a game you
launched yourself and makes no game-dir changes at all.

Any resumable run found on the profile is abandoned rather than negotiated
with (R97/5b).

## Surviving EB-1 (the Punch Off soft-lock)

BACKLOG `EB-1` is root-caused, upstream, and not ours to fix: entering the
Punch Off room spins the main thread on an unbounded engine-error loop. The
process stays **alive**, the wire goes **dead**, `godot.log` grew to **2.4 GB
in ~30 minutes**, and the run save is poisoned — `continue` re-enters and hangs
again, so the only exit is `abandon_run` from the main menu.

The soak carries two legs against it, and neither fixes anything:

- **The hazard register** (`soak.HAZARD_EVENTS`). `PUNCH_OFF` is refused rather
  than driven: the run stops with a `hazard_event` defect and no verb is posted.
  The hazard is room ENTRY (`PunchOff` fires `PunchEachOther()` from
  `AfterEventStarted()`), so there is no safe option to pick — and the frozen
  frame carried no options at all. What the guard buys is the SECOND hang: the
  soak's own restart path answers a poisoned save with `abandon_run`, which is
  EB-1's recorded recovery. The wire id is read, not guessed
  (`ModelDb.GetEntry` slugifies `PunchOff` to `PUNCH_OFF`, which is also the
  prefix of the event's own loc keys); the display title is matched as a second
  reading. `--allow-hazard-events` lifts the guard for a deliberate
  reproduction.
- **The spin watchdog** (`hangwatch.py`), for the case where the game hangs
  before there is a screen to refuse. On a dead wire with a live process it
  samples `godot.log`'s growth rate and the Windows message pump; a sustained
  flood **or** a not-responding reading on every tick of the window files
  `unresponsive_spin` and terminates the process through the ledger. Either
  signal alone is enough — one machine cannot read the log, another cannot ask
  `tasklist` — but a single not-responding sample is not, because that is also
  what a long room load looks like.

**`unresponsive_spin` exists because `bridge_unreachable` is a HARNESS-side
kind.** Filing a spinning game under it makes the instrument blame its own wire
for a build defect it has just caught, and two of them would halt the night on
the wrong diagnosis. Neither new kind is harness-side: both are the soak
working.

The kill is a ledger step, not a shortcut around one. The speed row is marked
**NOT REVERTED** with the captured original in its note, because the wire is
dead and the live `PrefsSave.FastMode` really is left changed — it persists to
`prefs.save` (not `settings.save`, which never carries FastMode) only if
something flushes prefs, which a hard kill does not — and a ledger that
laundered that would cost somebody an evening. `--no-setup` kills nothing: it did not launch the game and may not
terminate it, so it reports instead.

## Chosen seeds (P1.5)

```
python -m understudy.soak --runs 1 --seed P15BRIDGE1 --max-fights 2
python -m understudy.trace_replay <stampA> <stampB>  # compare two recordings
```

R95 accepted read-back seeds for P1 and gated CHOSEN seeds at the first
cross-build comparison; R104 promoted that gate. `--seed` is repeatable (run
*i* takes seed *i*, cycling) and **off by default — without it this is R95's
read-back arm, unchanged**, and no seed is passed on the embark verb in either
arm.

The seed goes on through the forked bridge's own endpoint
(`POST /api/v1/gits/seed`), between the character pick and the embark confirm,
because `NCharacterSelectScreen.AfterInitialized()` clears the game's seed
override as that screen opens and the run is generated inside the confirm.
Upstream's `menu_select(seed=...)` arm is deliberately NOT used: it refuses
singleplayer on a guard the decompile contradicts, and rewriting an upstream
refusal means owning it. Full reasoning: `vendor/STS2_MCP/gits/GitsSeed.cs`
and `docs/archive/sprint-understudy-p15-log-2026-08-05.md`.

**The read-back is the verification.** A run whose seed reads back different
from the one chosen files `seed_not_honoured` — a harness-side defect, because
the game rolling its own seed is the game behaving normally and what failed is
our claim to have chosen one. Two of them halt the soak.

**The chosen seed is not a policy input.** It is stamped on the log and
compared against the read-back; `rng.py` still refuses a stream label of that
shape.

`--max-fights N` stops a run cleanly after N closed fights. It exists for
comparing two recordings of one seed, not for soaking, and it is off by
default.

## The R103 probes (Track B, 2026-08-05)

```
python -m understudy.probe_block --spotlight center --seed TRACKB2 --max-fights 1 --turns 8
python -m tools.probe_b2_table "understudy/logs/soak/probe-b2-*.jsonl"
python -m understudy.replay --logs "<glob>" --use-selectors --ledger <path>
```

Answers: `docs/probe-a-block-offset.md` (B2, the +2 block offset — YES, it
reproduces, and it is **Frail**, absent from the fight record the replay reads)
and `docs/probe-b-fanfare-residual.md` (B3, the Fanfare residual — localized to
the unrecorded Spotlight selector plus the turn-open sampling seam; **direction
flips from "tier0 pessimistic" to neutral**).

**`--use-selectors` is OFF by default and must stay that way**: the committed
`docs/s7-divergences.tsv` was produced from a pre-P1.5 corpus that carries no
selectors, and a default that consulted them would make that artefact
irreproducible on any log that does.

## The committed-draft arm (R99/4b)

```
python -m understudy.soak --runs 3 --commit fanfare --report
```

**Off by default, and `--commit` is the only difference from a baseline soak.**
With it, the card-reward arm takes the best-scoring offer of the declared
archetype when one is on offer, and falls through to the sim's own
`assigned_policy` under the declared plan — skip included — when none is. The
pilot, the map arm, the rest arm and the combat ladder are untouched, and the
shop is deliberately NOT committed (`policy_v1._committed_draft` says why).

It exists because B2 measures cards and every deck the baseline records is a
mixed deck, so no archetype claim could be graded against one. The arm makes
decks that are actually the declared archetype; the run stamps `intent` on
every fight record, and `tools/track_b_curves.py --intent <archetype>` cuts the
curves to them.

`tier0/tests/test_understudy_committed.py` pins the claim rather than asserting
it: every state shape the driver produces is replayed through `commit=None` and
compared against the un-flagged call, decision for decision, and again with the
flag set to prove the draft is the only category that moves. **A committed-arm
number is a bot-limited floor measured under a constraint no person plays
under** — one notch further from a design finding than a baseline soak number,
which is already not one.

---

# Telemetry schema

**SHARED SURFACE — LIVE as of 2026-08-04.** This stopped being a heads-up the
day Track B started reading it. Three consumers now depend on the key names
below, so **renaming or repurposing any of them is a cross-session change and
takes its note first** (house pattern: `docs/animation-sprint-2-log.md`; the
note for this landing is §"Cross-session note" in
`docs/sprint-track-b-curves-log-2026-08-04.md`). **Adding a key is still
free** — that is the whole reason the additions of 2026-08-04 needed no
renegotiation.

| consumer | what it does |
|---|---|
| `understudy/soak.py` | WRITES the bot feed (`feed: "bot"`, `source: "soak"`) |
| `klee-mod/KleeCode/Diagnostics/PlayTelemetry.cs` | WRITES the human feed (`feed: "human"`, `source: "mod"`) from normal play, co-op included |
| `tools/track_b_curves.py` | READS both and builds Track B's B1/B2 curves |

`tier0/tests/test_track_b_curves.py` compares the two writers' key sets
directly and names every permitted asymmetry, because nothing else in the repo
can see across the language boundary.

**Additions of 2026-08-04 (late), both writers, no renames:** `intent`
(R99/4a). The `outcome` value set gained `ended` and `won` became observable on
the human feed (R100/5) — a change of MEANING rather than of key, which is why
it is called out here as loudly as a rename would be: a reader who assumed
`interrupted` meant "probably won" was right yesterday and is wrong today.

**Addition of 2026-08-05 (P1.5):** `selectors`. The note for this landing is
§"Cross-session note" in
`docs/archive/sprint-understudy-p15-log-2026-08-05.md`. It arrived **BOT FEED
ONLY** — the soak records a selector answer because it POSTED it, while the mod
saw a card leave a pile rather than an offer being taken from a list — and so
stood as a declared asymmetry beside `potions_used` for a week.

**`selectors` became a BOTH-FEEDS key on 2026-08-12 (EB-14)**, no rename and
no change of meaning: the mod-side hook into the selection screens landed
(`klee-mod/KleeCode/Diagnostics/SelectionTelemetry.cs`), so **a selector cut is
no longer a bot-feed cut**. The row is the same five columns in the same order
— `[round, screen, index, chosen, [offered…]]` — and `understudy/replay.py` and
`understudy/trace_replay.py` read a mod-written row without knowing which feed
wrote it (checked, not asserted: `tier0/tests/test_eb14_selection_hook.py`).

Five things the human feed's column does **not** contain, declared here
because a reader of the column will look here and nowhere else. None is a key
asymmetry; all five are limits on what the column can hold:

- **Local seat only.** A co-op partner's answer arrives as indices through
  `PlayerChoiceSynchronizer` and opens no screen in this process, so a remote
  seat's rows are *absent*, not empty. Same fence as `corpse_detonations`:
  rows present are facts, no rows is not proof nobody chose anything.
- **In-fight only**, which is exactly the bot feed's scope (`soak.py` records a
  selector only while a fight record is open). A rest-site smith or a shop
  removal is outside the channel on both feeds.
- **No bundle rows.** `NChooseABundleSelectionScreen` offers *bundles*, and a
  bundle carries no first-party name; filling the bot feed's `bundle_select`
  row would mean inventing one.
- **An empty answer records nothing**, matching the bot feed, where a skipped
  screen produces no POST and therefore no row.
- **No combat-pile rows in any package up to and including `0.2-738`.** The
  grid patch read the offer off `_cards`, and
  `NCombatPileCardSelectScreen` assigns that field `Array.Empty<CardModel>()`
  once and never writes it again — so the offer read as empty, the row was
  dropped, and no warning fired (the field lookup *succeeded*). Every
  combat-pile selection is therefore **absent** from human-feed records taken
  on those packages: Liquid Memories, Droplet of Precognition, the Wish /
  Neow's Fury / Cosmic Indifference Ancients, and ten base cards (Headbutt,
  Dredge, Hologram, Charge, Cleanse, Graveblast, Seance, Secret Technique,
  Secret Weapon, Seeker Strike) plus Foregone Conclusion and Stratagem. No
  klee-mod card reaches this screen, so the hole is base-game content only.
  **Fixed and shipped in `0.2-820`** (per-type offer resolver reading
  `_pile` + `_filter`), and smoke-proven live on that package: two
  `ncombatpilecardselectscreen` rows with non-empty `offered`, matching the
  soak's rows on round, index, chosen name and offered list. The limit
  therefore names the packages it applies to and nothing later; records taken
  on `0.2-738` and earlier still carry the hole.

The `screen` column is spelled differently by the two writers **on purpose**.
The soak writes what the bridge called the screen (`card_select`,
`hand_select`, `bundle_select`), falling back to the raw screen class name
lowercased; the mod writes the concrete class name lowercased always
(`nchooseacardselectionscreen`, `nsimplecardselectscreen`, `nplayerhand`, …).
`card_select` is *three screens wearing one name* and the mod is the side that
can tell them apart, so re-spelling it as `card_select` would throw away the
only thing this vantage has that the wire's does not. The two vocabularies
overlap on the bot feed's fallback spelling rather than colliding, and no
consumer matches on the column — `replay.py` matches on the OFFERED list.

**The live smoke, complete across all three surfaces (2026-08-13).** Nothing in
this repo can execute the C# writer, so each surface had to be watched in a
real game. `NChooseACardSelectionScreen` on package `0.2-738`: three Furina
fights, 17 Ethereal Spotlight turns and 17 mod-written rows — one per turn,
never two — with both options in `offered`. `NPlayerHand.SelectCards` and
`NCombatPileCardSelectScreen` on package `0.2-820`: one Kokomi run, seed
`D95DXF1CFK`, act 1 floor 2, driven with `give_card` grants of Pearl Diver
(hand-exhaust select) and Hologram (`CardSelectCmd.FromCombatPile`) — **14
`nplayerhand` rows and 2 `ncombatpilecardselectscreen` rows**, every one of
them matched row for row by the soak's own column on round, index, chosen name
and offered list. The spelling split is visible in that pair: the mod writes
`nplayerhand`, the soak writes `hand_select`. The soak additionally writes
`index: -1` confirm rows that the mod correctly does not — an empty answer
records nothing.

**Additions of 2026-08-07 (EB-18), HUMAN FEED ONLY, no renames:** `run_id`,
`run_instance`, `fight_index`, `encounter`, `detonations`,
`corpse_detonations`. The first four are per-fight identity — `run_id` is the
run's string seed, which is the same token the game's own run history writes as
`seed`, so `tier1/analyze.py` can join a fight row to a run row without either
side minting an id. **A seed is not a run**, though: replaying one is a
first-class arm (P1.5 / R104), and the first cut of this restarted
`fight_index` when the seed changed, so a seed played twice in one session read
as a single run with fights numbered 0,1,2,6,7,8. `run_instance`
(`<session stamp>#<ordinal>`) is minted once per `RunState` the mod sees —
`RunManager.State` is assigned once per run and nulled on cleanup, so object
identity is the game's own answer to "same run?" — and `(run_id,
run_instance)` is unique where the seed alone is not. Records written before it
carry no token and group by seed alone, which is ambiguous under a replayed
seed and reported as such. The last two are read off `BombPower`'s per-combat,
per-player counters; a **corpse detonation** is one that resolved on a body that
was already dead, which is probe (e) / Q11's question asked of every fight
instead of one scripted pair. All six are **declared asymmetries** (`MOD_ONLY` in
`tier0/tests/test_track_b_curves.py`, beside `reactions_by_turn`): the soak
drives the game from outside and has no wire route to the run object or to an
internal hook ORDER, so **a cut on any of them is a human-feed cut** until such
a route lands. `corpse_detonations > 0` is a fact; `== 0` is not proof of
absence (see `PlayTelemetry.FlushAll` for the one declared race).

**Addition of 2026-08-23 (EB-118), HUMAN FEED ONLY, no renames:**
`exhaust_selections`. One object per resolved Exhaust selection, in the
**sim's** column order — `card`, `victims`, then `size`, `cost`, `attacks`,
`skills`, `powers`, `companions`, `personal`, `upgraded`. The columns are
owned by `KleeCode/Powers/ExhaustSelection.cs` (`RowKeys`) and pinned against
`tier0.engine.effects.EXHAUST_SELECTION_ROW_KEYS` by
`tier0/tests/test_exhaust_context_parity.py`, so this is the one telemetry
column whose partner is the **tier0 kernel's event stream** rather than the
soak's record. `card` and `victims` carry model ENTRY names (`PEARL_DIVER`) —
the sim's sheet ids uppercased, so a reader case-folds rather than expecting a
literal match. An **empty selection still writes a row**: "nothing was there to
take" is a reading, not a gap, and a stream comparison needs the same row count
on both sides. A declared asymmetry (`MOD_ONLY`): the wire narrates a card
leaving a pile, not the identity of the selection that took it, so a bot-feed
twin is new wire surface.

**And two changes of MEANING in the same pass, called out as loudly as renames
would be.** Both live inside `meters_by_turn`; neither key was renamed and
neither changed type:

- the **encore** column now carries real values. It read `-1` (UNSEEN) on
  every bot fight before P1.5 because the bridge only serialised
  `creature.Powers` and Encore lost its badge in animation sprint 2. `-1`
  still means UNSEEN and is still what a pre-P1.5 log says.
- the **salon_cap** column now follows Casting Call. It used to record the
  printed base and ignore the raise.

**Two feeds, one schema, and the labels are load-bearing.** `feed` says who
produced the row and `source` says which instrument wrote it; Guardrail 7's
labelling requirement on every Track B curve is enforced from those two keys.
`seats` and `seat_index` carry co-op: the human feed writes ONE RECORD PER
SEAT per fight, so a two-seat fight is two rows that share an act, floor and
enemy list.

Logs live under `understudy/logs/soak/` (bot) and `user://gits_telemetry/`
— `%APPDATA%/SlayTheSpire2/gits_telemetry/` on Windows — (human). Neither is
committed: they are per-machine run output, not evidence anyone else can
reproduce. The human feed writes OUTSIDE the mod directory on purpose;
`deploy.ps1` deletes and re-copies `mods/klee`, which would destroy the log
at exactly the moment it holds the newest data.

## Files

| file | contents |
|---|---|
| `soak-<stamp>-index.json` | one object: the soak's parameters, per-run summaries, the reversibility ledger |
| `soak-<stamp>-run<NNN>.jsonl` | one run; one JSON object per line, `record` discriminates |
| `reversibility-<stamp>.json` | the game-dir change ledger |

## Record types (the `record` field)

### `run_begin`

`character`, `policy`, `dials` — the policy dials in force. Recorded per run so
a log is self-describing when the dials later move.

### `seed_chosen` — P1.5, only on a `--seed` run

`requested` (what the caller asked for), `seed` (the game's canonical form of
it), `route` (`lobby` or `debug_override`), `status`, `message`. Emitted at
the moment the seed goes on, which is after the character pick and before the
embark confirm.

### `seed_read_back`

`seed` — the seed the run actually has, read from `GET /api/v1/compendium`
after embarking. On R95's read-back arm that is the seed the game generated;
on P1.5's chosen arm it is the verification, and `chosen` / `honoured` record
the comparison. A mismatch raises `seed_not_honoured` rather than being logged
and walked past. **Never fed to a policy stream** on either arm; `rng.py`
refuses a label of that shape and the refusal is the enforcement.

### `bounded_stop` — P1.5, only on a `--max-fights` run

`fights`, `max_fights`. A clean stop, not a defect: the open fight has already
closed before the bound is checked.

### `decision` — one posted action

| key | meaning |
|---|---|
| `i` | action ordinal within the run |
| `state_type`, `act`, `floor`, `round`, `hp` | where it happened |
| `action` | the exact body POSTed |
| `names` | **revision #7.** Resolved identities: `verb`, `card_id`, `card_name`, `card_cost`, `card_type`, `card_upgraded`, `target_id`, `target_name`, `target_hp`, `potion_slot` / `potion_id` / `potion_name`, `option_index` / `option_name`, `node_kind` / `leads_to_kinds`, `item_name`, `screen_type`. Only applicable keys are present. |
| `hand` | every card in hand by name, index-ordered — the denominator a sequencing decision is read against |
| `mechanical` | true when the screen asked nothing (dialogue, reward pile, single-relic chest) |
| `policy` | policy_v1's own record: `revision` (`v0`, `v1.1`…`v1.6`), `category`, `label`, `rationale`, `notes` |
| `status`, `message` | the bridge's answer |

This is the P1 blocker discharged: **no row in this log needs a human to read
prose to know what was played.** A sequencing divergence can be categorised
from `names.card_name` and `policy.revision` alone, which is precisely what
Phase 0 could not do.

### `fight` — one fight, closed

| key | meaning |
|---|---|
| `schema` | schema version (`"1"`). Bumped only on a BREAKING change |
| `feed`, `source` | `bot`/`human`; `soak`/`mod`. Both mandatory — Track B labels every curve from them |
| `intent` | **R99/4a.** The DECLARED archetype for the run this fight belongs to, lowercase, `""` when nobody declared one. Human feed: the first word of `intent.txt` beside the logs (or `GITS_TELEMETRY_INTENT`), read ONCE per session so a run's records cannot disagree with each other. Bot feed: the `--commit` arm. **Always a declaration, never an inference** — nothing reads a deck and guesses. `tools/track_b_curves.py --intent X` cuts every curve by it |
| `seats`, `seat_index` | co-op seat count and this record's seat. The human feed writes one record per seat |
| `character` | *(human feed only)* the seat's character title |
| `act`, `floor`, `kind` | `monster` / `elite` / `boss` |
| `enemies` | `[{name, max_hp}]` as the fight opened |
| `hp_start`, `hp_end`, `hp_lost`, `max_hp` | the HP ledger |
| `turns` | highest round reached |
| `outcome` | `survived` / `died` / `won` / `ended` / `interrupted` / `superseded`. **The human feed CAN observe a win as of R100/5** — the previous entry here said the game exposes no first-party combat-end hook, and that was wrong about the game: `CombatManager.EndCombatInternal` calls `Hook.AfterCombatEnd` and `Hook.AfterCombatVictory`, both of which walk the same `IterateHookListeners` that already delivers `BeforeCombatStart`. `died` is exact and always was. The LOSS path never reaches `EndCombatInternal`, so there is no end hook on a death and none is needed. `interrupted` now means what it says: a fight closed by the next fight's stale-flush, i.e. fled, abandoned or crashed. `hp_end` is the last reading taken while the fight was live, capped by the reading at combat end so a revive cannot credit the fight for HP it never had |
| `hp_trajectory` | `[[round, hp, block], ...]`, sampled at each turn opening |
| `incoming_by_turn` | `[[round, telegraphed_damage, n_attacking_enemies], ...]`, read before block |
| `enemy_pool_by_turn` | `[[round, enemy hp+block total], ...]` at each turn opening. **The honest output curve**: the drop between two openings is everything that landed, whoever landed it — which `damage_by_source` cannot say |
| `meters_by_turn` | `[[round, fanfare, salon_members, salon_cap, encore], ...]`. **P1.5 opened both blind columns.** Encore comes off `player.resources` (`KLEEMOD_ENCORE`), the reflection read of BaseLib's registry the fork added; Fanfare prefers the resource over its badge, which is only ever a synced copy. The cap is the printed base plus `SalonCapUpPower` from the status strip — which had been on the wire all along. **`-1` still means UNSEEN, not empty**, and it is what a log written against a pre-P1.5 bridge (no `resources` key) still says; a `resources` map that simply has no Encore in it reads 0, because that is a player with no Encore rather than a blind spot |
| `reactions_by_turn` | `[[round, reactions resolved since this fight opened]]` — **human feed only**; the wire does not narrate reactions. `ReactionEffects.TotalResolved` is GLOBAL, so in co-op both seats' reactions appear in every seat's row. Measurement only: no reaction constant is read or written |
| `block_at_turn_end` | `[[round, block]]` as the player ENDED the turn — not the turn-opening block in `hp_trajectory`, which is whatever survived the enemy |
| `cards_played` | `[[round, card_name], ...]` |
| `selectors` | **P1.5; BOTH FEEDS since EB-14 (2026-08-12).** `[[round, screen_type, index, chosen_name, [offered names]], ...]` — every selector screen resolved inside this fight. The OFFERED LIST is in the row for the same reason `hand` travels with a card play: "Center Stage" means one thing against `[Center Stage, Guest Cast]` and nothing at all against a list that did not contain Guest Cast. `index: -1` is a selector resolved without naming an option (a confirm, a skip); on the HUMAN feed it additionally covers "the chosen card was not reference-equal to anything in the recorded offer", which the mod logs a warning for when it happens. `overlay` screens are excluded — that is the shape a soft-lock takes, and a screen nobody can answer has no choice to record. The human feed's five declared limits on this column (local seat, in-fight, no bundles, no row for an empty answer, no combat-pile rows on packages up to `0.2-738`) and the deliberate spelling split in `screen_type` are in §"Telemetry schema" above |
| `potions_used` | `[[round, potion_name], ...]` — **bot feed only**; no first-party potion hook exists for the mod side yet |
| `damage_by_source` | `{card_or_potion_name: total}` |
| `damage_dealt`, `damage_taken` | totals |

**Attribution rule, stated because all three are approximations that
under-count rather than invent:**

- *damage by source* is the enemy `hp + block` drop observed on the state read
  immediately after an action, credited to the card that action named.
  Anything resolving in the same frame batch lands on the play that triggered
  it — usually right (a summon's hit belongs to the summon card), occasionally
  wrong (a bomb detonating on a later play).
- *damage taken* is the player HP drop across a round boundary, credited to
  the enemy turn as a whole. The wire does not narrate which enemy landed
  which hit.
- *incoming per turn* is the sum of telegraphed attack intents at the player's
  turn opening, before block. Intent ramps are structurally invisible to the
  wire, so this is this-turn-accurate and future-turn-blind — the same limit
  `adapter.py` already declares.

### `defect` — a filed crash, soft-lock, stall or NRE

`kind` is one of `process_died`, `overlay_softlock`, `no_progress`,
`action_ceiling`, `run_timeout`, `bridge_unreachable`, `no_action`,
`menu_loop`, `embark_loop`, `no_embark`, `no_embark_path`,
`unexpected_start_state`, `seed_not_honoured`, `state_type_missing`,
`unresponsive_spin`, `hazard_event`. Plus `seed`, `act`/`floor`, `state_dump` (piles
collapsed to counts) and `recent` — the last dozen state fingerprints, which is
what a stall looks like from inside.

An `unresponsive_spin` row carries two more keys: `hangwatch` (the probe's own
evidence — log path, the two byte counts, the derived rate, the threshold it
was compared against, and the per-tick responding samples) and `teardown` (what
the watchdog did about it). The rate is derivable from the two byte counts on
purpose: a number a reader cannot re-check is not a number this house ships.

The subset in `soak._HARNESS_SIDE` means **the instrument** failed rather than
the build. Two defects of the same harness-side shape halt the soak; that is
the stop-and-surface rule, and it exists so a broken harness does not fill a
night with the same row. `unresponsive_spin` and `hazard_event` are
deliberately NOT in it — both are the soak catching EB-1, which is the soak
working, and a second observation of a live-play hazard is not a broken
instrument.

### `forced_default`

A screen policy_v1 declined and the driver walked past to keep the run moving.
Not a defect — but every one is a decision nobody made, so they are counted and
surfaced in the report.

### `game_over` / `run_end`

`won`; then `outcome`, `actions`, `wall_s`, `fights`, `final_act`,
`final_floor`, `defects`, `forced_defaults`, `log`.

## Reading it

```
python -m understudy.report              # the most recent soak
python -m understudy.report <stamp>
```

Defects first, outliers second, curves third. The ordering is deliberate: a
page that opens with a winrate invites the reader to read a winrate, and there
is no winrate here that means anything.
