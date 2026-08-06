# Understudy Phase 0 — the measured run

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

Sprint: Understudy (bot playtest apparatus). Phase: 0, the pre-registered
measurement. Brief: `docs/understudy-kickoff-brief.md`. P0 findings and the
three ratified rulings: `docs/understudy-p0-findings.md`. Date: 2026-08-04.
Worktree G4. Status: **PROPOSED** — the grades are final, the policy_v1 list
below is a proposal and nothing on it has been implemented.

One solo Furina run was driven through the vendored bridge with every decision
made by Opus and every decision logged beside what tier 0.5's own policy would
have done at the same state. The run did **not** finish. It reached Act 1
floor 9 of 16, alive.

Instrument: `understudy/logs/phase0-SSRWEGLNRG.jsonl`, 191 lines, reproduced
by `python -m understudy.analyze understudy/logs/phase0-SSRWEGLNRG.jsonl`.

---

## Grades

Recorded before any interpretation, per D4. Each is the pre-registered
prediction from the brief, then what the log says.

### M1 — tokens/decision and decisions/run. MEASUREMENT, no prediction.

These two numbers are the reason the run exists: they set Phase 2's tier
boundaries.

| | |
|---|---|
| **Decisions, LLM-issued** | **167** over 9 floors (8 fights, 3 events, 5 map screens, 1 rest) |
| **Decisions, mechanical** | 23 more, walked by the harness's `auto` verb; not decisions |
| **Decisions per floor** | **18.6** LLM-issued |
| **Marginal chars per decision** | **1045** (784 state read + 261 reasoning written) |
| **ESTIMATED marginal tokens per decision** | **~261** at 4 chars/token |
| **Wall clock per decision** | median 1.3 s, mean 8.7 s |

**The estimate's denominator, stated because a number without one is not
quotable here.** 261 tokens/decision is the *marginal* cost: the rendered
screen the model read plus the reasoning it wrote. It excludes the
conversation context re-read on every turn, which a process cannot observe
about the model driving it and which is the larger half. The true figure is
higher by whatever the context window costs, and grows with run length. What
261 IS good for is the comparison Phase 2 needs — the marginal cost of *one
more decision* at a given tier.

Extrapolated to a full 16-floor act at 18.6 decisions/floor: **~300 LLM
decisions per act, ~900 per run**. At 261 marginal tokens each that is ~235k
marginal tokens per run before context.

Two facts that belong beside those numbers because they change what a tier
costs:

- **117 of the 167 decisions were later steps of a planned turn**, issued
  without a fresh state read. Only 50 decisions cost a full screen read.
  Deciding a turn as a unit rather than a card at a time is what made 167
  decisions affordable, and it is a real thing a player does — but it is a
  different epistemic act, and the log flags it (`planned_sequence`).
- Mean wall clock (8.7 s) is six times the median (1.3 s), which is the
  planned-sequence effect again: batched steps post back-to-back.

### M2 — policy_v0 agrees with Opus on >60% of decisions, disagreement concentrated in draft picks.

**FAILED on the rate. FAILED on the concentration. Not a port bug.**

| category | scored | agree | differ | agree% |
|---|---|---|---|---|
| sequencing (combat card play) | 121 | 64 | 57 | 53% |
| path (map node) | 8 | 5 | 3 | 62% |
| draft (card reward) | 5 | 3 | 2 | 60% |
| resource (rest, overlays) | 3 | 1 | 2 | 33% |
| **all scored** | **137** | **73** | **64** | **53%** |

Excluded from the denominator by construction, not post hoc: 3 events, 1
rewards screen and 26 resource screens where policy_v0 returns no
counterfactual and says why (`policy_v0.NO_COUNTERFACTUAL`). 2 of the 8 path
comparisons were single-exit corridors and are flagged `n_options: 1`.

**The independence caveat, which matters more than the headline.** The 121
sequencing rows are not 121 independent tests. Once I diverge on the first
play of a turn, every later comparison in that turn asks policy_v0 about a
board my own play created. The subset where both arms genuinely face the same
question is the turn-opening decisions:

| | comparisons | agree | differ | agree% |
|---|---|---|---|---|
| **turn-opening combat decisions** | 47 | 13 | 34 | **28%** |

So the honest reading of M2 is a range, not a point: **53% across all scored
decisions, 28% on the independent combat subset.** Both miss 60%.

**M2's instruction was to treat a far-lower rate as a buggy port before a dumb
policy. I did, and here is what that produced.** Five adapter defects were
found and fixed *during* the run, all before the fights that produced the bulk
of the log:

| # | defect | consequence if unfixed |
|---|---|---|
| 1 | enemies live under `battle.enemies`, not at top level | every fight scored with zero enemies |
| 2 | intent damage is in `label` ("7", "6 x 3"), no numeric field exists | every attack read as 0 incoming; block-panic rung dead |
| 3 | the hand's target field is `target_type`, not `target` | every attack posted without an aim |
| 4 | enemy aura is `"Cryo Aura"`, not `"cryo"` | reaction term identically zero |
| 5 | the wire's intent label already includes the attacker's Strength; tier0 folded it in again | a Jaxfruit telegraphing 10 read as 45 incoming |

After those five the port is, as far as I can establish, faithful: policy_v0
delegates to `make_pilot`, `assigned_policy`, `_make_value` and `rest_action`
rather than re-typing them, so there is no scoring code of its own left to be
wrong. The residual 28% is a policy difference, not a translation error — with
two declared exceptions, the map reduction and the missing potion arm, both
listed under "known reductions" below.

**The concentration prediction is wrong in an interesting direction.** The
brief expected disagreement to pool in draft picks. Draft is the category we
agreed on *most* (60%, 3 of 5), and only 5 draft decisions occurred in 9
floors. The disagreement pooled in **sequencing**, which is also where 88% of
all decisions were. A tier that samples only draft picks would sample the
category where the policy and the LLM already mostly agree.

### M3 — one full LLM-driven run completes in a single Code session without hitting usage limits.

**FAILED.**

The run reached Act 1 floor 9 of 16 — 56% of one act, roughly 19% of a
three-act run — and was stopped deliberately at a rest site with budget
reserved for this report, the suite and the game-dir teardown. Nothing
crashed; the game and the bridge were stable throughout. The binding
constraint was session budget, spent on 167 decisions plus the five adapter
defects above plus building the harness in the same session.

**The consequence the brief pre-registered, now in force: Phase 2's
sampled-decision tier drops to draft-picks-only by default.** M2 immediately
complicates that default — see the concentration finding above — so the
recommendation is recorded and its tension flagged, not resolved here.

---

## Divergence, by category

Counts from the table above; the reading is mine, from the `why` field I wrote
at each decision.

### sequencing — 57 differences of 121 (34 of 47 turn-openers)

Three named classes, in order of how many rows they explain.

**(a) The free card that expires.** Furina's starting relic adds an Ethereal
Spotlight to hand every turn; it costs 0 and is discarded unplayed. I opened
almost every turn with it. policy_v0 opened with `Stage Presence` whenever
incoming damage crossed the block-panic threshold, because
`BLOCK_PANIC_THRESHOLD` short-circuits scoring entirely and a 0-cost card has
no privileged status in the score. This is the single largest contributor to
the turn-opener gap. It is not a judgment difference: playing a free card that
will otherwise vanish costs nothing and cannot be wrong.

**(b) Block bought against damage that block cannot cover.** On floor 7 the
board offered 39 incoming with a Frail-reduced 4 block available and a 25 HP
enemy that exactly 25 damage in hand could kill. policy_v0 asked for the 4
block on every one of five consecutive comparisons. I killed the smaller body,
which deleted 15 of the 39 permanently. The pilot's block-panic rung compares
`incoming` against HP but never asks whether the block on offer can
meaningfully dent it, or whether a source of the incoming can be removed.

**(c) Effects the pilot prices as damage when they are defence.** Playing Cryo
into a Hydro aura Freezes the target and halves its next attack. tier0's
`_reaction_value` prices reactions as expected damage
(`PILOT_REACTION_TRIGGER_VALUE`); the defensive half of Frozen is invisible to
it. I used the reaction to survive a 24 for ~0; policy_v0 wanted 5 block.

### path — 3 differences of 8 (2 of the 8 were forced corridors)

All three are the same difference, and it is a **known reduction, not a
judgment gap**: the wire exposes each option's `leads_to`, but policy_v0's map
arm scores one step deep because `tier05.route` plans by backward induction
over the whole act DAG and the wire does not carry the DAG. Twice I took the
node whose successor was better; once (floor 7) I planned into an Elite two
floors out that the reduction could not see — which is what the *unreduced*
hunter would have done. Read as evidence about `route`, these are agreements.

### draft — 2 differences of 5

Both are diagnosable as scoring blind spots rather than taste:

- **Floor 4, Charlotte over Usher the Waves.** Two Salon members were already
  ticking. `score_offer` prices 2 Vulnerable as a generic debuff (`amount * 2`
  through `_static_power`), not as a multiplier on damage the deck is already
  producing every turn. It scored Usher 7.58 and Charlotte 1.83.
- **Floor 7, The Gallery Stirs over Deep Breath.** `score_offer` returned
  **exactly 0.0** for a Power reading "the first time you spend Encore each
  turn, draw 1 card. Fanfare Cap +5" — in a deck whose three members spend
  Encore every turn. A 0.0 on a card that is obviously not worth zero is the
  tell for a missing op price, not a judgment call.

### targeting — 0 differences

Every aimed card in the run went to the enemy tier0's `_default_target` would
have chosen. That is partly a small-sample artefact — most fights were
single-enemy — and partly genuine: lowest-HP-first is correct most of the
time. The one deliberate exception, putting Charlotte's Vulnerable on the 48 HP
Flyconid rather than the lower-HP Jaxfruit, was a *card choice* under this
harness's accounting and lands in the sequencing bucket, because the
comparison fires on the card and its target together.

### resource — 2 differences of 3 scored (26 unscored)

- **The rest site (floor 9).** 39/71 HP, an on-plan upgradable in the deck.
  `rest_action`'s ladder smiths, because the on-plan-upgrade rung sits above
  the 0.65 heal line. I rested for 21 HP. `next_fight` is the flag that would
  have changed the sim's answer and the wire cannot supply it — the bridge
  shows the next options but the harness does not thread them into the rest
  screen.
- **One row is an accounting artefact and is not a real disagreement**: log
  index 4, a `confirm_selection` on the upgrade overlay counted as a
  difference because policy_v0 answers the overlay with the card choice while
  I had already made that choice on the previous action. Noted rather than
  filtered, because filtering a row after seeing it is how a rate becomes a
  story.

The 26 unscored resource rows are potion use, in-combat choice overlays
(Center Stage / Guest Cast), and enchant screens. policy_v0 has no arm for any
of them.

---

## Known reductions in policy_v0, restated

These are declared in the code and repeated here so no reader mistakes one for
a finding:

1. **Map lookahead.** One step deep, against `tier05.route`'s whole-map
   backward induction. Explains all three path differences.
2. **No potion arm.** `tier0.engine.potions.try_use_potions` is a real entry
   point that was not wired. Every potion decision is unscored.
3. **No event arm, no boss-relic arm, no minigame arm.** The sim scores these
   by ids the wire does not carry. Returning nothing is deliberate.
4. **Deck staleness at a draft.** The bridge exposes no deck outside combat,
   so `understudy/deckwatch.py` reconstructs it from the last combat
   observation. At a card reward the deck scored is the deck that *fought*,
   one card stale.
5. **Base-game cards are text stubs.** Anything without a `KLEEMOD-` sheet row
   gets damage/block scraped from its rules text and nothing else, so the
   policy systematically undervalues them. Flagged per decision as
   `approximate`.

---

## policy_v1 — PROPOSED revisions. None implemented.

[USER] skims this list; it is the gate this pass stops at. Ordered by how much
of the measured divergence each would close. Every one is a change to
`understudy/policy_v0.py` or its adapter — **nothing here touches
`tier0/pilot/policy.py`, `tier05/`, the drafter or any sheet.** Where a
proposal implies the SIM is wrong, that is called out separately and does not
belong to this sprint.

| # | proposal | closes | why it is judgment and not noise |
|---|---|---|---|
| 1 | **Play free expiring cards first.** Before scoring, if a playable card costs 0 and is Ethereal (or otherwise expires), play it. | the largest share of the 34 turn-opener differences | Costs nothing, cannot lose value, and the card is gone at end of turn. There is no board state where declining is right. |
| 2 | **Ask whether the block on offer can matter.** Gate the block-panic rung on `available_block >= some fraction of incoming`, and prefer a lethal-on-one-body attack line when killing an enemy removes more incoming than the block prevents. | class (b), ~5-8 rows | The current rung fires on the ratio of incoming to HP alone; it will buy 4 block against 39 every time. |
| 3 | **Deepen the map arm by one ply using `leads_to`.** The wire already carries it. | all 3 path differences | Not a policy change at all — it moves policy_v0 closer to the tier05 policy it is a reduction of. Should be done before any path number is read. |
| 4 | **Wire the potion arm** to `tier0.engine.potions.try_use_potions`. | 26 unscored rows become scored | Same delegation principle as the rest of the module; the entry point exists. |
| 5 | **Thread `next_fight` into the rest arm** from the map's `leads_to`. | the rest-vs-smith difference | `rest_action` already takes the flag and changes answer on it; we are passing False because we did not look, not because we know. |
| 6 | **Give the in-combat choice overlay an arm** (Center Stage / Guest Cast) keyed on deck composition. | part of the 26 unscored | Recurring, consequential, and currently invisible to the measurement. |
| 7 | **Log the resolved card NAME with each action.** | nothing directly; everything about analysis | The log stores `card_index`, so a sequencing divergence cannot be categorised after the fact without the human's prose. This pass categorised by hand from `why`; a soak cannot. |

Three observations that look like findings about the **sim**, recorded for a
separate ruling and deliberately not acted on:

- `tier05.draft.score_offer` returns 0.0 for a Power whose text is
  "the first time you spend Encore each turn, draw 1 card". If that is a
  missing `_op_price` entry rather than a deliberate zero, the drafter has been
  blind to a class of cards. **This is a claim about the sim made from one
  observation and is not a finding until someone checks it in `tier05/`.**
- `score_offer` prices Vulnerable as a flat debuff, so it cannot see a
  multiplier applied to an engine already on the board.
- `tier0.pilot.policy._reaction_value` has no defensive term, so Frozen —
  which halves an incoming attack — is priced only as damage.

---

## Defects and stop-and-surface

1. **The bridge cannot start a seeded run through the singleplayer path.**
   `menu_select` with a `seed` requires `charSelect.Lobby != null`, which is
   null in standard singleplayer; the API returns "Seeded embark is not
   supported for standard singleplayer from this API". The Custom-run screen,
   which is where a seed would be entered, is **not modelled by the bridge at
   all** — selecting `custom` lands on a state reporting `menu_screen: "main"`
   with no options, and no verb (including `back`) is accepted. That is a
   soft-lock; recovery was to restart the game. **P1 needs one of: a Custom
   screen arm added to our fork, a multiplayer-lobby route, or acceptance of
   game-generated seeds read back after the fact.** This run took the third
   path: it started standard and recorded the seed the game generated
   (`SSRWEGLNRG`, from `GET /api/v1/compendium`). That is enough to identify a
   run and not enough to *choose* one, which a seeded soak needs.
2. **`GET /` returning ok is not "the game is ready".** The HTTP server comes
   up about 5 s after launch; the main menu has no buttons for another ~20 s,
   and a read in between returns `menu_screen: "main"` with the `options` key
   absent. A soak launcher that treats the health check as readiness will act
   into an empty menu. Watchdog on `options`, not on `/`.
3. **A run is left in progress on the local profile.** Act 1 floor 9, Furina,
   seed `SSRWEGLNRG`, 60/71 HP, at a rest site. It is left resumable
   deliberately — it is the instrument this report is about, and abandoning it
   would destroy the only way to continue this exact measurement. It will
   appear as `continue` / `abandon_run` on the main menu. Abandon it whenever
   it is in the way; nothing else depends on it.
4. **No crashes.** Neither the game nor the bridge crashed, hung, or produced
   an unhandled `overlay` state in 190 posted actions across 8 fights, 3
   events, a shop-free Act 1 and one elite. The one error returned mid-run
   ("Not in combat") was my own planned sequence overrunning a kill, which the
   harness caught and aborted cleanly.
5. **Adapter defects 1-5 above are recorded as measurement history, not as
   open defects.** All five are fixed. They are listed because they are what
   M2's "debug first, revise second" instruction actually cost, and because
   any future adapter against this wire will meet the same five.

## Guardrail-7 restatement

Nothing in this document is a balance finding. The run's HP curve, the
fights won, the cards drafted and the elite killed are all **bot-limited and
LLM-limited floors** in exactly the sense pilot-limited already means in tier
0.5, and none of them are quotable as evidence about Furina, the Salon, the
drafter or Act 1 difficulty. No fun or legibility claim is made or implied: a
JSON-state agent cannot see the screen.

## Appendix — reversibility log (game dir)

Format inherited from `docs/understudy-p0-findings.md` Appendix A. Initial
state was recorded before the first write: `mods/` contained exactly
`STS2AutoSlayMod`, `klee`, `quick_fingers`; `klee` was already deployed and
was left alone.

| # | Change | Undo | State |
|---|---|---|---|
| 1 | Created `mods\STS2_MCP\` with `STS2_MCP.dll` (239,104 bytes, built from `vendor/STS2_MCP` at pin `55e0648`) and `STS2_MCP.json` | `.\build\deploy_bridge.ps1 -Remove` | **REVERTED** — `mods\` lists exactly `klee`, `quick_fingers`, `STS2AutoSlayMod` |
| 2 | Created `steam_appid.txt` (`2868840`) at the game root for direct-exe launch | `Remove-Item steam_appid.txt` | **REVERTED** — absent |
| 3 | Set `PrefsSave.FastMode` to `Instant` and `Engine.TimeScale` to 3.0 via `POST /api/v1/gits/speed` | `POST {"enabled": false}` restores the captured originals | **REVERTED** — verified back at `Fast` / `1.0`, which is what it was |
| 4 | Launched the game three times (once restarted out of the unmodelled Custom screen); all processes terminated | n/a | Not running |

Not modified: `mods\klee\` (left as deployed, per instruction), the AutoSlay
settings, any Workshop content, any `.pck`. Under `%APPDATA%\SlayTheSpire2\`
the game wrote its own logs, `settings.save` and the in-progress run in item 3
of stop-and-surface; the P0 leftover run (seed `1A2B3C4D`) was abandoned
in-game at the start of this pass as instructed.
