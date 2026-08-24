# STATE

> **What currently ships** — roster, systems, versions, and active workstreams.
> Snapshot only. Open decisions live in [`docs/current/QUEUE.md`](QUEUE.md);
> engineering tasks in [`docs/current/BACKLOG.md`](BACKLOG.md); normative rules
> in [`docs/current/LAW.md`](LAW.md); how-to commands in
> [`docs/current/OPERATIONS.md`](OPERATIONS.md).

## Lifecycle

- **Tier 0 v0.1 — LOCKED.** Frozen v2 errata implemented — non-boss Frozen is
  **soft control** (−50% next action + Shatter on the first Attack hit); bosses
  take **Vulnerable 2** instead (§2.2; R44). The v0.1 scorecard baseline and
  median identity are regression-locked (`test_errata.V02_MEDIAN`).
- **Tier 0.5 M5 — SHIPPED.** The M5–M8 archive world was the v1 run template;
  the live run model is now the real StS2 map (see Versions below). Older
  run-layer numbers are archived, never compared across template versions
  unlabeled.
- **Kokomi meter-20 — RATIFIED (R139, 2026-08-10)** on the fresh
  `RT9/D14/P6/C8` read (`review/active/sitting-reads-2026-08-08.md` §3). **The
  current build is the comparison baseline from now on** — the dead v0.3 W1
  comparator is not rebuilt, and later Kokomi numbers are compared against this
  state, not against the archived world.
- **Artifact coexistence + Kokomi rotation law — RULED and LANDED 2026-08-23**
  (`CONSTANTS_VERSION` 11, [USER] pulled the staged branch into the open
  window): Auras and Bombs coexist with Artifact (only real debuffs consume
  it), and Kokomi never Exhausts — nor accrues Charge/Burst from — a Status
  or Curse. Pre-C11 Kokomi combat numbers are archive; a later
  `staged/eb74-lever2-b-alone` pull re-baselines on C11.
- **Roster slot 4 — Zhongli countersigned (R108), not yet scheduled.** The deep
  dive is unblocked; the pre-slot-4 gate is the roster registry (`tier0/roster.py`).

## Roster

Ship order is stable and meaningful (`tier0/roster.py`); reports print it.

| id | display | nation | element / cadence | default plan | archetypes |
|---|---|---|---|---|---|
| `klee` | Klee | Mondstadt | Pyro, catalyst-grade (all attacks apply) | demolition | demolition, spark, reaction |
| `furina` | Furina | Fontaine | Hydro, Skill-grade | salon | salon, spotlight, fanfare |
| `kokomi` | Sangonomiya Kokomi | Inazuma | Hydro, catalyst cadence | priest | priest, commander, assist |

Klee is the compatibility baseline character. Companion pools ship per nation:
`docs/mondstadt-companions.yaml`, `docs/fontaine-companions.yaml`,
`docs/inazuma-companions.yaml`.

**Reference anchors** (measurement anchors, NOT roster members — no art, no
pool, no C# class): `ref_ironclad`, `real_ironclad`, `ref_silent`, `real_silent`
(`tier0/roster.py:165-171`). The scoring anchor is `("ref_ironclad", "starter")`
under the `generic` pilot, normalized so every axis reads exactly `3.0`.
`real_*` variants depend on a local `game_ref/` tree that is gitignored and
absent on a fresh clone.

## Content inventory

Live sim inventory (`docs/current/atlas/tier0-pilot-roster.md` §2): **317 cards
in the loader index** (of which 3 are acquisition-only Ancient side-sheet rows,
leaving the 314 the atlas quotes), **5 character sheets** (3 roster + 2
reference), **6 encounters, 15 pilot weight sets**. The battery encounters are
frozen (`content/encounters/battery.yaml`, FROZEN 2026-07-19). Card sheets:
`docs/klee-cards.yaml`, `docs/furina-cards.yaml`, `docs/kokomi-cards.yaml` (all
three carry the `tempo_band:` field, **234 personal rows** total — 76 / 82 /
76). Kokomi's sheet moved 62 → **76 (5 basic / 31 common / 26 uncommon / 14
rare, 70 draftable)** on 2026-08-23: `EB-69`, the ruled 14-card pool fill
(R198). Her pool is now Klee's shape, and every pre-fill Kokomi draft number is
a pre-fill number. Balance numbers (HP, decks, bands) live in
`tier0/content/characters/*.yaml`, the ratified artifact — not in the registry.

## Mod card coverage (generated)

Codegen: `tools/gen_roster_cards.py` (`tools/gen_klee_cards.py` per-character).
Manifests are the live coverage ledgers.

Coverage numbers below are read from the live manifests, not prose — the
`docs/` recaps carried stale figures (75/76 and 77/78 for Furina), which is
exactly why STATE reads the artifact.

- **Klee** — the compatibility baseline profile; fully generated.
- **Furina** — **81 of 82** generated, 1 blocked (`let_the_people_rejoice`,
  intentionally hand-written kit machinery)
  (`klee-mod/KleeCode/Cards/Furina/Generated/manifest.json`).
- **Kokomi** — **70 of 76** generated, 6 blocked
  (`klee-mod/KleeCode/Cards/Kokomi/Generated/manifest.json`). One is
  `ceremonial_garment` (hand-written). The other **five arrived with `EB-69`**
  and each names an unimplemented C# runtime grammar rather than a defect:
  `the_gunbai_turns` and `raise_the_sashimono` (op `grant_sly_this_turn`),
  `what_the_tokoyo_took` (an `amount_formula` over `discards_this_turn` needs a
  CalculatedVar bound to that count), `gyorin_formation` (`bonus_formula`
  `1_per_2_charge` on `block` has no rider and would render as the bare base),
  and `what_the_tokoyo_returns` (a Sly `recall_to_draw` from **discard** —
  only the exhaust source is built). Two further cards generate but ship
  WITHOUT an upgrade under the no-partial-upgrades rule: `send_the_runner`
  ([USER]'s ruled two-key delta) and `wheel_the_ranks`. **The sim has all
  fourteen; the mod has nine of them and seven of their upgrades** — a declared
  asymmetry, tracked as `EB-122`.

## Version / world stamps

The run-cell stamp is **`RT/D/P/C`**, read live via `tier05/cells.py`. Numbers
are never comparable across a stamp boundary unless labeled.

| stamp | value | source | meaning |
|---|---|---|---|
| `C` `CONSTANTS_VERSION` | **11** | `tier0/constants.py` | The **Artifact-coexistence + Kokomi-rotation ruling** ([USER] rulings 1–3, 2026-08-23). Built PROPOSED on `artifact-muster-sweep` under the `S4-G13` staged-branch precedent, then **pulled by [USER] the same day**: the sequencing choice ruling 3 reserved was made as *join the open window*, so 11 is live and every branch shipping from here is C11. **(a) Artifact coexistence — C#-only.** `ArtifactPower` negates only an application whose `GetTypeForAmount(amount)` reads `PowerType.Debuff` (decompile-verified against `sts2.dll`; positive-amount counters fall through to `Type`), so `AuraPower` and `BombPower` move `Debuff` → **`Buff`** and coexist with Artifact — no Harmony patch needed. `FrozenPower` stays a real Debuff, and so do reaction-applied Vulnerable / Weak / Poison. Bomb's first-attack −25% rider now lands **through** Artifact, ruled acceptable under "Auras and Bombs". tier0 does not model Artifact, so this half moves **no sim number** and is recorded for the window's completeness. Eyes-on, `S4-G12`-style: aura/bomb badges on enemies now style as **Buffs** (amount-label colour included); `card_keywords.json` tooltips are unchanged pending that read. **(b) The Kokomi rotation law** — the half that is engine behaviour and moves numbers. A Status or a Curse is never one of her cards: `_op_conscript` never transforms one, `_op_exhaust_from` drops them from the **unfiltered** chosen-Exhaust pool under the `tamakushi_casket` hook (an explicit `filter:` is the opt-in, Dodge Roll's shape; a hookless player keeps the any-card pool), and `after_card_exhausted` pays **no Charge and no Burst particle** for one by any route — Ethereal, a played Dazed, the ward's random draw-pile pick. One predicate (`Card.is_junk`) at all three seams in each engine — C#-side `KokomiResources.IsJunk`/`OwnCard` at the Muster filter, the ten generated chosen-Exhaust selectors, and `AfterCardExhausted` — pinned by nine tests (`tier0/tests/test_kokomi_rotation_law.py`). **Every pre-C11 Kokomi combat number is archive:** junk was free curse removal that also paid the meter, so any number taken with a Status/Curse in hand or exhaust overstated her. The archive banner goes where the numbers are published and nothing is rewritten (R101b) — the 2026-08-13 twelve-arm table keeps its non-Kokomi rows as the standing baseline. **No card sheet was edited**, so R179/M15's clause is checked and not invoked; `D` and `P` do not move (`_static_power` never priced junk, no op added, no offer-time price moved), so the payoff-reach `D14` pin stands. `EB-69` collision: `staged/eb74-lever2-b-alone` is the second staged `C`-mover, lands second and **re-baselines on C11** (its branch note's 9 → 10 rebases to 11 → 12). C10 was the **tier0 engine half of the window-2 correctness batch** (`EB-104`, 2026-08-13), seven combat-kernel behavior fixes landed together and stamped once at the end of the window. `EB-95` player-side duration debuffs tick at the **enemy** side-turn end, and the first tick is skipped only when a **monster** applied the debuff (the authority's own predicate); enemy-owned Vulnerable/Weak/Frail keep ticking at their own turn end. `EB-96` a sleeping enemy is a side-turn **participant** — block clear, turn-start and turn-end hooks all run, while `advance_intent` and the Nemesis Intangible toggle stay suppressed; this moves a **frozen calibration-battery** number and two Act-1 bodies (3.545 → 3.653 mean turns, 79.70 → 79.50 mean end HP over 400 seeded fights). `EB-97` the Fanfare cap reads **live** max HP in both engines and recomputes on `gain_max_hp`, with a named C# cap constant so the parity lint can see the term. `EB-98` `masque_red_death` stops paying the flat-attack rider its 2026-07-25 redesign deleted. `EB-99` Guest Star generation applies the `personal_pool` filter in both engines. `EB-100` Encore Performance asks whether a card is **lit**, not who is designated, so it copies under the Orobas both-modes relic. `EB-101` Supporting Cast's first-play draw resolves **after** the triggering card, matching `SpotlightSystem`'s `BeforeCardPlayed`/`AfterCardPlayed` split. **No card sheet was edited**, so R179/M15's card-sheet clause is checked and not invoked — this bump rests on CONSTANTS 5's comparability criterion, with C6(a)/C7 as the direct precedent. Every pre-window combat number for every character is archive. C9's "further errata may join" clause was **spent** — it holds only until a number is published under the stamp, and the twelve-arm table of 2026-08-13 was published at `C9`. C9 was the slot-2 rarity floor restored ([USER] 2026-08-10, S4-G10 close-out): the shop's wildcard companion slot rolls Uncommon-or-better again in **both** engines, so Commons leave the paid channel and the 50-gold band is unreachable. Every §4.7 shop number taken under C6–C8 is archive. The `exp_shop_companion_channel` instrument repairs land inside the same window deliberately, so the corrected cell has one world to cite; further errata may join C9 until a number is quoted under it. **Erratum joined 2026-08-10 under that clause (no number had been published): the X7/X8 rarity promotions (R161, R162)** — `friendly_visit`, `chain_fuse`, `careful_arrangement` all Common → Uncommon, costs and numbers unchanged; Klee's pool now reads 29 Common / 28 Uncommon (was 32/25, total still 76) and `secret_stash`'s derived demolition-Common add-pool drops two entries. C8 was EB-30m/R127's `charge_per_turn` / `encore_per_turn` income powers (latent at the bump). |
| `RT` `RUNTEMPLATE_VERSION` | **12** | `tier0/constants.py` | The **run-layer half of the window-2 correctness batch** (`EB-104`, 2026-08-13), five fixes batched into one bump for the same reason v8 batched two — all `RUNTEMPLATE` content, one window, none quotable alone. `EB-102` `resolve_shop` finally receives the run's **Featured Banner**, so the shop can no longer sell a 5-star the banner excluded from every reward screen; it changes which card `rng.choice` lands on, so every §4.7 shop-channel figure taken under `C9` renumbers, and it lands **before** the `M14` shop rerun as that row required. `EB-103` potion capacity is derived from held relics **on read**, so a mid-run Potion Belt is visible to `resolve_event` and its grant is no longer dropped unlogged. `EB-110` the rest-site heal **floors** where it rounded, matching the authority's truncation through `SetCurrentHpInternal` — 2.39 HP/run of one-directional sim-generous bias removed from the HP ledger. `EB-111` Book of Five Rings counts **event** deck-adds through a single `note_add` door, not only shop buys and reward picks (88 uncounted adds across 64 book-holding runs in 300). `EB-112` event card-reward screens roll rarity through **`RARITY_ODDS`** like any other reward screen — 20.0% Rare per offer becomes 5.0% on three shipped options in acts 1 and 2 for every character; **`RARITY_ODDS` itself is unmoved**, only the site that failed to consult it. No drafter or pilot code moved, so `D` and `P` are untouched and the payoff-reach `D14` pin stands; `C` moved in the same window on its own ground (the engine half above), each field once, together, at the end. No v11 run-layer number carries across. **Re-baselined at the bump** — the twelve-arm standing table, `review/active/sitting-reads-2026-08-13.md`. v11 was the coordinated 2026-08-13 window (`EB-82` + `EB-85`), batched into one bump because both are `RUNTEMPLATE` content and neither was quotable alone — `M14` enumerates the window and asked for exactly one bump at the end of it. **(a) `EB-82`:** `grave_of_the_forgotten` joins the **act-3** event pool (2 own → 3 own), so act-3 event odds move for every character, and its Accept branch grants `forgotten_soul` — an **event** relic no reward, Neow or Ancient roll can reach — which arms `damage_per_exhaust` mid-run and puts damage into every later fight of that run. **(b) `EB-85`:** five places where tier0 modelled an enchantment differently from the class `sts2.dll` v0.107.1 ships, each re-verified against the binary first. Three move what an enchant event may **target** — Nimble gates on `GainsBlock` not `type == "skill"`, Swift has no type override at all (Self-Help Book's third reading was locked on Klee's printed starter for all of v10), and Nimble never rides `block_next_turn` — and two move what it **pays**: the Nimble rider is collected on every Block gain rather than once per card play, and Perfect Fit refuses the opening shuffle instead of acting as a free Innate. Enchantments stay post-draft only and no drafter or pilot code moved, so `D` and `P` are untouched and the payoff-reach `D14` pin stands; `C` did not move either, because the window's other two branches (`EB-70`, `EB-83`) wrote no code. No v10 enchant number and no v10 act-3 number carries across. v10 was R82 reopened ([USER] 2026-08-10, M7): the enchant events. |
| `D` `DRAFTER_VERSION` | **14** | `tier0/constants.py` | Generic-limb `core_complete` now requires an on-plan payoff. Held at 14 — the payoff-reach registration's pin (R121, six-step order; R125 widened the shield under the restores-not-redefines argument, no bump). |
| `P` `POLICY_VERSION` | **7** | `tier05/draft.py` | R176: the pilot values `copy_companion_in_hand` / `replay_next_companion` (EB-17p's 40,396 draws / 0 plays was pilot scoring, not an unreachable condition) — every Klee tier0.5 number moves; the payoff-reach `DRAFTER_VERSION=14` pin is untouched. v6 was EB-29t's Enrage/Intangible reads; v5 was EB-24p's `reaction_triggered_this_turn` read; v4 was R124's both-Spotlight-modes read. |

- **Run template string** `RUN_NODE_TEMPLATE = "NNNRETN$ERB"` is DEAD as of v6,
  kept only as the archived-world name and for tests that pin a node sequence.
- **Acts** (`RUN_ACTS`): `act1` (easy_fights 3), `act2` "the Hive" (2),
  `act3` "Glory" (2).
- **Map (StS2 DAG):** `MAP_FLOORS = 16`, `MAP_TREASURE_FLOOR = 8`,
  `MAP_REST_FLOOR = 14`, `MAP_BOSS_FLOOR = 15`, `MAP_MAX_EDGES = 3`,
  `MAP_MAX_FLOOR_WIDTH = 6`, `MAP_PATHS = 6`. Room odds
  `N 0.53 / ? 0.22 / R 0.12 / E 0.08 / $ 0.05`.
- **A6 instrument:** `A6_INSTRUMENT_VERSION = 2` (in `tier0/harness/axes.py`, not
  `constants.py`) — the scorecard's application-uptime term
  (`0.5*aoe + 0.3*debuff + 0.2*uptime`), anchored ADDITIVELY so `ref_ironclad`
  stays exactly 3.00. This is a **scorecard** instrument version, separate from
  the run-cell stamp above; v1 and v2 A6 numbers are discontinuous by design.
- **Pilot policy:** `POLICY_VERSION` lives in `tier05/draft.py` (current value
  in the stamp table above) and enters the cell stamp as `P`. Heuristic weights live in
  `content/pilots/archetypes.yaml` and `pilot/policy.py`; `STOKE_*` are
  deliberately NOT in `constants.py`.

## Mod build environment (pinned)

Per the retired klee-mod DECISIONS ledger (frozen at tag
`pre-simplification-2026-08-06`): Slay the Spire 2 **v0.107.1**, commit `59260271`
(2026-06-18), Steam buildid `23811903`, appid `2868840`, branch `public`.
MegaDot v4.5.1, BaseLib 3.3.7.0, .NET SDK 9.0.316, ilspycmd 8.2.0.7535. The PCK
contract version is `roster-pck-v3`.

## Systems

- **tier0 combat kernel** — op interpreter, powers, statuses, reactions,
  resources; comparability-first and emit-only toward the run layer. 7-axis
  scorecard, anchor `(ref_ironclad, starter) = 3.0`, frozen battery. Kokomi's
  rotation law lives at three seams off one predicate (`Card.is_junk`);
  Artifact itself is C#-only (unmodelled in sim).
  (`docs/current/atlas/tier0-engine.md`, `tier0-harness-tests.md`)
- **tier0.5 run sim + drafter** — run-level model, acts, runner, draft, and the
  real StS2 16-floor map/route policy. (`docs/current/atlas/tier05-sim-core.md`,
  `tier05-economy.md`, `tier05-metrics.md`)
- **understudy** — the bot playtest bridge driving the real game (Guardrail-7,
  no-fun rule). (`docs/current/atlas/understudy.md`)
- **klee-mod** — the C# character mod (`KleeCode/`) plus the PCK build/deploy
  pipeline, and since 2026-08-13 a headless C# test project (`KleeTests/`,
  `EB-105`). Co-op therefore has a **partial** automated backstop, not none and
  not a full one: per-seat ownership and attribution are testable; multiplayer
  transport and anything needing a live `CombatState` are still play-only
  (`klee-mod/KleeTests/README.md`).
  (`docs/current/atlas/klee-mod-cards.md`, `klee-mod-runtime.md`,
  `klee-mod-build-pck.md`)
- **vendor STS2_MCP bridge** — the vendored wire contract the understudy speaks.
  (`docs/current/atlas/vendor-sts2-mcp.md`)
- **art pipeline** — `ImageGen/` card/UI/model art staged into the roster mod
  and packed by `tools/build_pck.ps1`. (`docs/current/atlas/tools.md`)

## Active workstreams

Named here for status only. Open items are in
[`docs/current/QUEUE.md`](QUEUE.md); engineering tasks in
[`docs/current/BACKLOG.md`](BACKLOG.md).

- **EB-118 richness pass** — Phase-0 contract in HEAD
  (`review/active/eb118-richness-phase0-2026-08-23.md`); the connectivity
  instrument and the full Route-1 infrastructure set are merged **inert**
  ([USER] pulled the staged branches 2026-08-23): no card uses any new op,
  pilot policies sit behind `PILOT_POLICIES_ENABLED = False`, every new
  drafter price is PROPOSED, and no live version integer moved. **All three
  fences came down 2026-08-24.** The payoff-reach grade landed, releasing the
  Phase-1 sheet-edit gate and the Phase-2 `D14` lift, and the density row it
  minted (`QUEUE` `M37`) was **ruled the same day (R199)**: the canonical bands
  are a directional benchmark rather than a hard 1–3 requirement, the sheets do
  over-use `role: payoff`, and **Phase 3 is AUTHORIZED** to convert genuine
  setup / access / repair / bridge cards to glue or enabler and to drop
  unsupported `archetypes` tags — under four guardrails (no relabeling to
  improve a count; no rarity moves to force offer probability; no mechanical
  supply cut on `kokomi/commander` or `kokomi/assist`, whose problem is access
  not saturation; and a ruled priority order). The guardrails and the order live
  in the BACKLOG `EB-118` row.
- **Enemy remapping** — planned.
- **Art passes** — Furina and Kokomi surfaces (Kokomi's are newest).
- **Animation sprint 2.**
- **Axis-validity tracks** — Track A / Track E logs.
- **Kokomi playtest** — unrun.
- **Payoff-reach re-registration — RUN AND GRADED 2026-08-24.** R121's
  six-step order has run through step (4). §6.6's `P12` freeze was taken at
  the live `RT12/D14/P7/C11` (re-stamping §6's world string and `T1`'s
  registered stamp string from the superseded `RT10/D14/P7/C9`, **moving no
  version integer**), the registered cell ran value for value — n = 600/arm,
  seed 11, `hunter`, `assigned`, realistic, all acts, the nine arms and no
  others, 56 seconds against a 4-hour ceiling — and the grade went in blind.
  **Nine arms, nine `P5` MISSES on both axes, every one ABOVE its band window;
  Q-A SPLIT (reach beats its floor everywhere and clears 3×, but
  `kokomi/commander` reads 0.81 against a HIGH bar of 1.0) and Q-B SPLIT (the
  median offer more than doubles under both readings; the band-crossing clause
  is unsatisfiable because every actual offer already sits above the top
  band).** No tripwire fired, and `T3`'s classifier-integrity condition held
  with zero disagreements — so the misses are content, not instrument. The
  redesign trigger fired roster-wide and minted **`QUEUE` `M37`** under `M28`'s
  aggregation rule: one row, nine arms enumerated, and explicitly not a claim
  that one mechanism produced them — **and [USER] ruled it the same day (R199),
  so it has left HEAD and its authorization now lives in BACKLOG `EB-118`'s
  Phase-3 fence.** `P12` and `R190`'s remaining Assist fence are both
  discharged. **Steps (5) and (6) — the staged D15 (`EB-43`) landing
  and the `RA-G1`/`RA-G2`/`tto` quarantine lift — are UNBLOCKED and
  deliberately NOT taken**; they are the next window's work. Of the two
  defects the run surfaced, `EB-123` is **FIXED 2026-08-24** — after the
  grade, outside the discharged `P12` freeze: a remembered Status now rebuilds
  through `effects.token_card`, which asks the loader first and opens the
  synthesized-status door only inside the handler for the `KeyError` the
  loader raised, so a previously-crashing `real_silent` run completes and **no
  anchor or frozen-battery number moves** (`real_ironclad/generic` at the `C1`
  cell is byte-identical across the fix). The blocked half of `C1` is
  unblocked as an engine matter; **no completion run was taken and none is
  scheduled** — the published record stands as published (`R101b`) and whether
  a completed `C1` is wanted is [USER]'s call. `EB-124` is **FIXED the same
  day, for future runs only**: the reader's `base_id` now normalizes the
  run-applied enchantment mark as well as the upgrade suffix, through
  `enchantments.split` — the loader's own door past it — so an enchanted
  reward-pool card is compared instead of being printed under
  "entered from outside the reward pool". **The graded read does not move**;
  it was verified robust under both normalizations before the grade (all 122
  excluded ids carried an `@`, genuinely external on-plan payoffs numbered
  zero, `T3` fired under neither), and neither the results artifact nor the
  registration is edited.
- **`EB-69` Kokomi pool fill — CLOSED 2026-08-23 (R198).** Fourteen cards and
  fourteen upgrade rows in one batch, 62 → 76. `S4-G11`'s Kokomi pile is
  discharged; that row stays open on its other three piles. What the fill
  raised rather than settled: QUEUE `M36` (a distinctness-gate breach and
  three strict-domination pairs), BACKLOG `EB-121` (the art bill is 6 slots
  short) and `EB-122` (five cards blocked on unimplemented C# grammar).

## Watch register (dormant)

Blessed mechanisms with a named quantity and a named trigger — monitored, not
open decisions, and nothing is tuned on the strength of being watched. Each
returns to [USER] only when its trigger fires: `W1` X4 (block-side Guest Cast),
`W2` X6 (salon power level), `W3` X12 (co-op reaction potency — instrument
unblocked since `O-1` closed; a new reading runs under EXPERIMENTS law),
`W4` X5 (fanfare floor), `W5` `lynette_box_trick` (X7, R161 — deliberately left
alone at its current rarity; as a companion card it is close to "what if I
high-roll a colorless option". **Trigger:** playtest shows it overperforming).

**`W6` `gyorin_formation` — pre-emptive Block RATE.** [USER] was shown the card
as possibly an over-strong Block engine and deliberately deferred it
(2026-08-23, `EB-69`). The concern is explicitly not a single-turn spike: the
card is 6 Block now (+1 per 2 Charge) and 6 more at the start of the next turn
— 12 across two turns, not 12 on one — and the worry is **6 pre-emptive Block
every turn for as long as the card keeps coming around**, on a character whose
Charge bank fills every time she rotates a card off and is never spent (R80).
**Trigger:** her stability number moves materially in the post-fill baseline;
this is the first card to look at.

**`W7` `what_the_tokoyo_took` — upper-tail discard count and realized damage.**
[USER]'s reprice (cost 2 → 1, 3-per → 4-per) is a real power increase and was
ruled as one, not as a re-rate. Three discards is one card's worth inside this
pool and a chained turn reaching **6+** is reachable, which is 30 damage for 1
energy (33 upgraded). **The obligation is on the INSTRUMENT, not on the card:**
the post-fill baseline must report **p90/p99 per-turn discard count and the
realized damage distribution of this card**, never a worked example. A mean is
not the instrument here; the tail is the whole question.

**`W8` `send_the_runner` — burst-particle cadence.** [USER]'s D2a body trades
the printed Charge grant for a chosen Exhaust. Charge is a wash
(`CHARGE_PER_EXHAUST = 1` replaces the dropped grant exactly), but the card now
also pays `KOKOMI_BURST_PER_EXHAUST = 2` particles it never paid before — at
Common, at cost 0, repeatable. **Trigger:** Burst frequency across a run reads
above the ratified meter-20 cadence (R139) in the post-fill baseline.

(Migrated from the retired watch-items docket, frozen at tag
`pre-simplification-2026-08-06`; `W5` added 2026-08-10, `W6`–`W8` at `EB-69`
2026-08-23.)
