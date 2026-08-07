# QUEUE

> This file holds **only OPEN decisions that need [USER]
> judgment** — design, behavior, taste, or money calls. It is one of six
> governing files and owns no overlap: executable engineering work lives in
> **BACKLOG.md**, settled normative rules in **LAW.md**, shipped facts in
> **STATE.md**. Nothing here is decided; recording is not answering. Every row
> is migrated from the master queue (`docs/registry/user-queue.md`) and its
> upstream owners, with identifiers preserved exactly.

> **Owner of every row below: [USER].** Status is OPEN unless a row says
> otherwise. Where a row needs a supporting evidence packet, it points to
> `→ review/active/<packet>`.

---

## 1. Furina — strength, legibility, and unshipped mechanics

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `S4-G7` | Three fenced Furina calls: how strong her hidden Power bonus is and whether to print it; three viable plans or one (dead-archetype); what to do about her strongest plan running above its anchor (salon leak) | OPEN — fenced behind `S4-G5`/`B-G1` | user-queue §2; backlog §3 items 1–3; R107/F1 |
| `M1` | Furina's charter co-op Fanfare mechanic (partner damage + Encore swings feeding her meter, plus the self-damage audit): **BUILD or WAIVE** — the "Tier 2" deferral condition has lapsed | OPEN | user-queue §10; `git show aa09b97:docs/current/backlog/missed-requirements.md` §1.1 |
| `M2` | Second charter co-op mechanic — can co-op players pass a Spotlight to each other: **BUILD or WAIVE** | OPEN | user-queue §10; `git show aa09b97:docs/current/backlog/missed-requirements.md` §1.2 |
| `M3` | One Furina Encore card upgrading to Innate (measured green, never shipped): **SHIP or DROP** | OPEN | user-queue §10; `git show aa09b97:docs/current/backlog/missed-requirements.md` §1.5 |
| `M5` | Furina's declared elite axis A6 has measured short for two weeks (median 3.5 vs 4.2): **pick one of three routes** put to red-pen | OPEN | user-queue §10; `git show aa09b97:docs/current/backlog/missed-requirements.md` §3.7 |
| `Q-C` (payoff-reach) | Author the payoff-reach / `RARITY_ODDS` sprint's **written predictions at kickoff** — direction + threshold per question, plus the Q-C target band (or its explicit deletion) — before any number is read. Q18 countersign is done; this is step (2) of its execution order | OPEN — design-side authoring | → review/active/payoff-reach-reregistration.md §4 |

## 2. Kokomi — band, playtest, pool, and art

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `S4-G6` | Declare Kokomi's HP stability band **from design intent, before her confirmatory playtest** (may not be revised against it) | OPEN — gates her protocol playtest; re-anchored to post-rework build | user-queue §2; `DEC-D5` clauses 2–4 |
| `S4-G13` | Kokomi measures below the Ironclad-anchored floor — **pick one of three levers** (Code may build any, may pull none); plus the `NT-G5` fork evaluation (weak-or-fine), whose only accepted input is `OT-1` | OPEN | user-queue §2; `klee-mod/DECISIONS.md` E2/E2b |
| `S4-G14` / `OT-1` | Play the Kokomi protocol playtest deliberately against the written question list (exploratory runs cannot be graded); `OT-1` = draw and play Neap Tide, report weak or fine | OPEN — table time; blocked on `S4-G6` + N1 attribution pass | user-queue §2/§7; `docs/current/playtest/kokomi-playtest-protocol.md` |
| `M8` | Three Kokomi card-art rulings: crop-reuse budget (state a number or eyes-on per card); whether Watatsumi/shrine environment art counts as a card face (Furina rejected "a random hallway"); whether to hand-crop the banned `Character Details 1` for a Rare | OPEN | user-queue §10; `docs/current/art/kokomi-art-pass-requirements.md` §6 |
| `M9` | Three Kokomi v0.4 leftovers: ratify the meter-20 number on the 500-run confirm; rename `epiphany_of_the_deep` → "Song of Pearls"; keep or drop the commander Garment-uptime watch | OPEN | user-queue §10; `docs/archive/kokomi-v0.4-report.md` §6 |

## 3. Klee — archetype bands and scorecard invariants

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `S4-G18` | Klee's three archetypes carry 28/21/14 cards each vs the constitution's 15–20 band — **amend the rule or fix the pools** (never done either) | OPEN | user-queue §2; `git show aa09b97:docs/current/backlog/missed-requirements.md` Tier 5 |
| `M4` | Klee pass-4 ask A5: enforce the scorecard's two invariants (≤4.0 A2 ceiling; A1+A6 elite pairing) as **suite failures or report flags** — the ask was always *which*, not *whether*; today neither exists | OPEN | user-queue §10; `docs/archive/klee-pass-4-plan.md` §3.4 |

## 4. The seven-axis scorecard

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `S4-G5` / `B-G1` | Per-axis disposition of the **Fanfare axis** (the other six axes are closed as reportable-only). Carries the re-registered Fanfare P1; governs `S4-G7` and the fanfare STOP via the R107/F1 fence | OPEN — narrowed, not discharged | user-queue §2; `docs/axis-validity-session-charter.md` §4/§7 |

## 5. The ratification batch

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `S4-G9` | One sitting turning ~14 proposed numbers/small design calls into ratified ones (fanfare-rework X values; conversion clauses; `lasting_impression`; negative-floor semantics; D6 bow space; `kurages_oath`=12 re-file; pulse 2-vs-3; Curtain Call's four follow-ons; `scattering_spray` 7→6; Spotlight ten-icons-vs-family; Klee dead-card reworks) — the reason much shipped content is still PROPOSED | OPEN | user-queue §2; backlog §3 item 9 |

## 6. Shop, pricing, and money

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `S4-G10` | Companion-shop close-out: grade `SHOP-P1…P3`; settle whether money is ever the constraint (~220 unspent gold); the 1.15× surcharge; Track A pool migration; R60 phase-2 fantasy-leak grading. **New agenda item (not an answer):** should slot 2 carry a rarity floor at all? (wants empirical Common offer/pick/skip data) | OPEN | user-queue §2; R60/R63; principles §4.7 |
| `M11` | Two shop close-out items tracked nowhere: **§7.6 R60 phase-2 fantasy-leak grading** (gates the deferred colorless-removal sprint) and §7.7 the Track D fallback taste check; plus the joined `R59` slot-2 rarity-floor design question | OPEN — rides the `S4-G10` sitting | user-queue §10; `git show aa09b97:docs/current/backlog/missed-requirements.md` Tier 5 |
| `X10` | `gorou_heart_of_the_clan` looks underpriced (the Metallicize treadmill): a **CANDIDATE, explicitly not ratified** — Uncommon promotion + power adjustment, **priced at a sitting** | OPEN — money/pricing call | user-queue §4; docs/dockets/companion-pricing.md §1; review/redteam/exploit-ledger.md X10 |

## 7. Systems and data-model rulings

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `S4-G19` | Two mechanics do nearly the same thing (Sly unification) — **say whether they become one** | OPEN | user-queue §2; `docs/archive/tech-debt-audit-2026-07-26.md` §5 |
| `M7` | Should the simulator **model enchantments at all** (a data-model call — state on a card vs the sim's creature-scoped modifiers)? Exactly one Silent card needs it | OPEN — MODEL / DON'T | user-queue §10; `docs/archive/enchantments-design-2026-07-27.md` |
| `EB-30q` | **Ancient carve-out from the no-passive-accrual laws.** `PrincessOfWatatsumi` grants 3 Charge/turn and `AllTheWorldsAStage` +5 Encore/turn — each breaks its character's ruled law identically (LAW: Charge "no passive accrual"; `furina-cards.yaml:41` "no per-turn Encore or Fanfare trickle exists, and none may be added"), both C# docstrings argue the Ancient is "the one door out of her central bargain", and LAW carries no exception. Either LAW gains an explicit Ancient carve-out (the engineering is then small and pre-sourced: `charge_per_turn` beside `spark_per_turn`, an `ancient`-rarity sheet row, a Dusty Tome `add_card` event; numbers pinned 3 / +1 on upgrade) or the two Ancients get redesigned | OPEN | fix-sweep-4; EB-30 |

## 8. Card text and decision-record corrections

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `M6` | Kaboom Beetle Swarm's printed text now describes something the card no longer does (post-R72 snapshot-at-cast): **APPROVE the reword or LEAVE** | OPEN | user-queue §10; `git show aa09b97:docs/current/playtest/open-playtest-items.md` §6.2 |

## 9. Eyes-on reviews and taste

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `S4-G11` | **Read card names and lore text by eye before they ship** (R29d Furina pass; Kokomi's 20 authored-but-unaudited fill cards; kickoff ask 10) — ruled to have no substitute | OPEN | user-queue §2; `tier0/DECISIONS.md` entry 75 + R29d |
| `S4-G12` / `CC-G1` / `CC-G2` | Art contact-sheet eyes-on (three re-hunt candidates incl. `grand_gala`; confirm the `standing_room_only` crop by eye) + in-game screenshot review of the twelve Curtain Call cards and the A0 smoke run | OPEN — **materials ready** | user-queue §2; `docs/archive/g12-review-2026-08-05.md` |
| `S4-G16` / `G-A5(b)` | **One screenshot: a Power being played and the Fanfare floor going up because of it** — the last of four evidence shapes (eyes-on acceptance, not telemetry) | OPEN | user-queue §2; `review/active/red-pen-2026-07-26.md` Part 3 |
| `S4-G17` | Four running-game looks (no full playtest): `AS2-D5` salon capture; `AS2-B5` motion pass + facing taste; `AS2-E2` icon picks (4 REHUNT); hover-targets | OPEN — urgency reduced (hover-targets closed pt.4; B5 "not noticed") | user-queue §2/§7; `docs/animation-sprint-2-plan.md` (B5/D5/E2), §"Gates & rulings" |
| `S4-G20` | A bundle of small leftovers: Standing Ovation boost expiry (text-vs-intent); sim-vs-C# salon RNG divergence (accept or fix); three taste passes (Kokomi 58 faces + 15 companions, L12 duplicate pairs, `kaboom == spark_knight_style`); two infra toggles (branch protection / `gh`; manifest MAJOR bump, dormant by design) | OPEN | user-queue §2; backlog §1 P3-cluster + §5 |
| N + O TOP-5 | Read the top five findings of the lore-fidelity and instrument-redteam ledgers (both worst-first); includes `N-1` and the PROVISIONAL reactions-corpus caveat | OPEN — read | user-queue §4; `docs/archive/lore-fidelity-audit-2026-08-05.md`, `docs/archive/instrument-redteam-2026-08-05.md` |
| S8 + S10 galleries | Taste calls on two proposal galleries: eight flagged potions/relics (S8), and enemies that could be reskinned rather than redesigned (S10 — RESKIN/REDESIGN is [USER]'s per north-star) | OPEN — taste | user-queue §4; `docs/current/dossiers/content/potion-relic-conversion-gallery.md`, `docs/current/dossiers/remap/reskin-gallery.md` |
| Art debt | Kokomi 58 faces + 15 companions awaiting picks; four missing Kokomi portraits; `curtain_cue` wordmark; `breathless` mood; A7 + six Curtain Call power sigils; `AS2-E2` icon re-hunt (4 of 7); `grand_gala` re-hunt; two `ART-L12` duplicate pairs (`blazing_delight==true_spark_knight`, `crowd_work==standing_ovation`) awaiting a re-pick ruling | OPEN — mostly taste | user-queue §8; `docs/archive/backlog-2026-07-29.md` §5; `docs/current/art/kokomi-art-pass-requirements.md` §2a |

## 10. Fontaine Rares close-out

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `M10` | Four items the Fontaine Rares sprint left owned by [USER]: companion art picks (Navia/Clorinde/Neuvillette/Arlecchino); the v1.7 lore/naming eyes-on audit (non-delegable); the C2 grading countersign; and close-out ratification. Design note parked with them: Neuvillette graded WEAK/DEFERRED with the "different facet" question open | OPEN | user-queue §10; `git show aa09b97:docs/current/backlog/missed-requirements.md` §4.4 |

## 11. Design calls routed from the dockets & findings

Surfaced by engineering triage, but each needs a [USER] design / taste /
behavior / money call before any code moves.

| ID | Decision needed | Provenance |
|---|---|---|
| `EB-22` | Kokomi pool fill: draft ~15–17 rare-weighted cards and ratify (the pool-count *measurement* is done) | dockets; `docs/archive/brief-kokomi-pool-fill.md` |
| `EB-24` | Dead riders (`the_final_verdict` 0/298, `blocking_notes` 31/2471; `audience_participation` drawn 974 / played 0 across 600 `fanfare_weighted` fights, its Encore grant unreachable in play): propose reworked conditions for red-pen | eng-backlog; fix-sweep-4 EB-20 census |
| `EB-26` | Kokomi P4 prevention-on-curve (an uncommon lesser ward) — a new card = content design | eng-backlog |
| `EB-32` | The pilot block-panic rung — a scheduling decision ("would move every tier-0.5 number on one observation") | eng-backlog |
| `EB-33/34/35` | Pilot/drafter repricing exhibits (The Gallery Stirs 0.0 offer; Vulnerable-as-flat-debuff; `_reaction_value` has no defensive term) — inputs to a `_static_power` / reactions-promotion repricing session | eng-backlog |
| klee-rework `X1` | Companion cost-delta accumulator remedy — a Klee-rework NOTE; nothing built against the shared-state disposition | dockets/klee-rework §1 |
| klee-rework `X7` | Klee spark-economy violations (`skip_and_hop`, `sparkly_treasure`, `crackle`) — a sitting item on R109's disjunction | dockets/klee-rework |
| klee-rework `X8` | Bomb-damage carrier-card rarity check ("need to check these cards"), priced at a sitting (the *unimplemented cap* is `X8-cap` in BACKLOG) | dockets/klee-rework §3 |
| kokomi-workshop `X9` | Kokomi charge bank ("probably too strong, parse carefully") — the next kit workshop | dockets/kokomi-workshop |
| `shared_billing` | The only Common with a cost upgrade (1→0), which the delta-grammar convention forbids — needs a [USER] call (sheet and C# agree; the conflict is with the ruled convention) | triage-memo |
| Template heal/elite economy | Node composition and pathing-agency — a structural design question | tier05-perf §1.5.2(2) |
| `EB-29q` | **`test_subject`: accept, promote, or reconsider.** With the inflated-HP premise refuted (sheet exact on HP, weaker than the real boss elsewhere) and both EB-29 engine defects fixed, it measures 12.2% anchor / 33.3% klee / 69.7% furina at full HP — the only encounter in three acts under the 35% out-of-scale bar. The (c) `real_ironclad` re-instrument ran 2026-08-07 (`tools/encounter_audit` method, 300 realistic runs, seed 11, RT7/D14/P3/C6): **21.5%** at full HP vs the anchor's 12.7% control — the real pool reads it easier but it is still the only out-of-scale encounter for either Ironclad, so "player side under-scaled" is directionally real yet does not clear the bar; the real pool also reads both act-2 bosses at 35–38% (ref 55–62%) and wins 10.4% of runs (ref 19.6%). Remaining directions: **(a)** accept — a hard 50/50-drawn act-3 boss is legitimate; **(b)** promote §10.9 ops (all make it *harder*) and answer on the player side. Unilateral tuning ruled out (run-model-rework-plan `:584-586`) | fix-sweep-4; EB-29 audit; perf-1.5.2(3) run 2026-08-07 |
| `Q19b` | **Widen the R121 shield to all four behavioural tag readers, or accept the three unshielded channels.** EB-46: the C5→C6 bump is exactly zero on the anchor arm (bit-identical runs) — all movement was the instrumentation tags, and the smith (`model.py:130`), the event grant (`events.py:441`) and the plan bonuses (`draft.py:1261,1271`) still read them, worth **+2.17 pp (z=+6.42)** on the shipped row; the true untagged-C6 baseline is 11.13%, reproducible. The published record stands as published (R101b) | fix-sweep-4; EB-46; Q19 |
| `EB-31q` | `_NEOW_HOOK_WEIGHT` values for the Orobas/Ancient hooks (`combat_start_spark`, `charge_per_exhaust`, `burst_per_exhaust`, `spotlight_both_modes`) — all three Touch of Orobas variants currently value 0 in `ancient_pick` and are effectively never acquired. A valuation judgment with no derivable source. The loud-zero guard shipped (EB-31h): these four sit in `_NEOW_WEIGHT_PENDING`, any other unweighted hook now raises; ruling here moves them into the weight table | fix-sweep-4; EB-30/31 |
| `EB-31p` | Pilot policy is blind to both-Spotlight-modes (`policy.py:488,499,512`): under The Curtain Never Falls `p.spotlight` stays `None`, so the pilot over-values drafted designate cards and scores `copy_spotlighted_in_hand` at 0 despite live targets. Fixing re-bases every Furina cell (`POLICY_VERSION 3` stamp surface): bump P, or accept | fix-sweep-4; EB-30/31 |
| `L4q` | `role_tempo`'s `pays_at_zero` reads only literal amounts: `pearl_barrage` / `depths_judgment` / `undertow` print floors 5/10/4 via `amount_formula.base` and are tagged `scaling`-only, missing `frontload` — but `test_role_tempo_coverage.py:259-269` **pins exactly this classification** and warns "19 cards of tagging inverted with it". Tag-semantics call: adopt `effect_walk.printed_floor` (re-tagging the three) or ratify the pin as the intended reading | fix-sweep-4; L4 verified live |

---

## Not carried here

Engineering follow-through lives in **BACKLOG.md**; the rules these decisions
settle in **LAW.md**. Closed and answered items leave HEAD — they are in git
history at tag `pre-simplification-2026-08-06`.

Provenance entries are frozen citations: identifiers (`user-queue §2`,
`eng-backlog`, `dockets/…`, the DECISIONS ledgers) and any path not in HEAD
(`docs/archive/…`, `docs/registry/…`, retired sprint plans) name their
source as it stood when the row migrated. Retrieve any of them with
`git show pre-simplification-2026-08-06:<path>`.

A citation written as a whole `git show <commit>:<path>` command is one whose
content differs from the tag copy, so the commit — not the tag — is the
retrieval point. On a shallow clone, fetch it first:
`git fetch --depth=1 origin <commit>`.
