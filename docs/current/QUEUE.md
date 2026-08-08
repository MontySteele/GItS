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
| `S4-G7` | One fenced Furina call remains: **three viable plans or one** (dead-archetype) — newest reading (n=3000, 2026-08-06 republication) has salon 11.20% vs spotlight 2.23% and fanfare 2.23%, non-overlapping intervals, fanfare still overlapping the `real_silent` floor | OPEN — fenced behind `S4-G5`/`B-G1` | user-queue §2; backlog §3 items 1–3; R107/F1 |
| `M1` | Furina's charter co-op Fanfare mechanic (partner damage + Encore swings feeding her meter, plus the self-damage audit): **BUILD or WAIVE** — the "Tier 2" deferral condition has lapsed. NOTE (2026-08-07): the chartered mechanism cites the `encore_gained` leg Track A deleted in both engines, so a BUILD is a re-specification, not an implementation | OPEN | user-queue §10; `git show aa09b97:docs/current/backlog/missed-requirements.md` §1.1 |
| `M2` | Second charter co-op mechanic — can co-op players pass a Spotlight to each other: **BUILD or WAIVE** | OPEN | user-queue §10; `git show aa09b97:docs/current/backlog/missed-requirements.md` §1.2 |
| `M5` | Furina's declared elite axis A6 has measured short (median 3.5 vs 4.2, an A6-v2 reading — no instrument discontinuity): **pick one of three routes** put to red-pen. NOTE (2026-08-07): the 3.5 measures a sheet since re-authored twice (Fanfare rework 2026-07-28; A15) — a fresh A6 read precedes route-picking | OPEN | user-queue §10; `git show aa09b97:docs/current/backlog/missed-requirements.md` §3.7 |
| `Q-C` (payoff-reach) | Author the payoff-reach / `RARITY_ODDS` sprint's **written predictions at kickoff** — direction + threshold per question, plus the Q-C target band (or its explicit deletion) — before any number is read. Q18 countersign is done; this is step (2) of its execution order | OPEN — design-side authoring | → review/active/payoff-reach-reregistration.md §4 |

## 2. Kokomi — band, playtest, pool, and art

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `S4-G6` | Declare Kokomi's HP stability band **from design intent, before her confirmatory playtest** (may not be revised against it) | OPEN — gates her protocol playtest; re-anchored to post-rework build | user-queue §2; `DEC-D5` clauses 2–4 |
| `S4-G13` | Kokomi measures below the Ironclad-anchored floor — **pick one of three levers** (Code may build any, may pull none); plus the `NT-G5` fork evaluation (weak-or-fine), whose only accepted input is `OT-1`. Re-confirmed worse on the 2026-08-06 republication (n=3000): priest 2.47 / commander 3.00 / assist 0.63% vs `real_ironclad` 8.53 — assist below even the `real_silent` floor, non-overlapping | OPEN | user-queue §2; `klee-mod/DECISIONS.md` E2/E2b (at tag `pre-simplification-2026-08-06`) |
| `S4-G14` / `OT-1` | Play the Kokomi protocol playtest deliberately against the written question list (exploratory runs cannot be graded); `OT-1` = draw and play Neap Tide, report weak or fine | OPEN — table time; blocked on `S4-G6` + N1 attribution pass | user-queue §2/§7; `docs/current/playtest/kokomi-playtest-protocol.md` |
| `M8` | Three Kokomi card-art rulings: crop-reuse budget (state a number or eyes-on per card); whether Watatsumi/shrine environment art counts as a card face (Furina rejected "a random hallway"); whether to hand-crop the banned `Character Details 1` for a Rare | OPEN | user-queue §10; `docs/current/art/kokomi-art-pass-requirements.md` §6 |
| `M9` | Two Kokomi v0.4 leftovers: ratify the meter-20 number on the 500-run confirm; keep or drop the commander Garment-uptime watch | OPEN | user-queue §10; `docs/archive/kokomi-v0.4-report.md` §6 |

## 3. Klee — archetype bands and scorecard invariants

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `S4-G18` | Klee's three archetypes carry 28/22/14 cards each (spark drifted 21→22; recounted 2026-08-07) vs the constitution's 15–20 band — **amend the rule or fix the pools** (never done either) | OPEN | user-queue §2; `git show aa09b97:docs/current/backlog/missed-requirements.md` Tier 5 |
| `M4` | Klee pass-4 ask A5: enforce the scorecard's two invariants (≤4.0 A2 ceiling; A1+A6 elite pairing) as **suite failures or report flags** — the ask was always *which*, not *whether*; today neither exists | OPEN | user-queue §10; `docs/archive/klee-pass-4-plan.md` §3.4 |

## 4. The seven-axis scorecard

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `S4-G5` / `B-G1` | Per-axis disposition of the **Fanfare axis** (the other six axes are closed as reportable-only). Carries the re-registered Fanfare P1; governs `S4-G7` and the fanfare STOP via the R107/F1 fence | OPEN — narrowed, not discharged | user-queue §2; `docs/axis-validity-session-charter.md` §4/§7 |

## 5. Shop, pricing, and money

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `S4-G10` | Companion-shop close-out: grade `SHOP-P1…P3`; settle whether money is ever the constraint (~220 unspent gold); the 1.15× surcharge; Track A pool migration; R60 phase-2 fantasy-leak grading. **New agenda item (not an answer):** should slot 2 carry a rarity floor at all? (wants empirical Common offer/pick/skip data) | OPEN | user-queue §2; R60/R63; principles §4.7 |
| `M11` | Two shop close-out items tracked nowhere: **§7.6 R60 phase-2 fantasy-leak grading** (gates the deferred colorless-removal sprint) and §7.7 the Track D fallback taste check; plus the joined `R59` slot-2 rarity-floor design question | OPEN — rides the `S4-G10` sitting | user-queue §10; `git show aa09b97:docs/current/backlog/missed-requirements.md` Tier 5 |
| `EB-42q` | **Spine licence reconsider ($379).** The Skeleton2D spike came back PROMISING (`d69b7a0`); the remaining unknown is the live-combat seat (BACKLOG `EB-42`). Buy Spine, stay on Path C layered (the shipped fallback), or wait on the seating probe | OPEN — money call | `tools/skeleton2d_spike/README.md`; `git show d69b7a0` |
| `X10` | `gorou_heart_of_the_clan` looks too strong (the Metallicize treadmill): a **CANDIDATE, explicitly not ratified** — power adjustment, **priced at a sitting**; the exploit lines (81 hits) target the power, not the price (already Uncommon) | OPEN — money/pricing call | user-queue §4; docs/dockets/companion-pricing.md §1 and review/redteam/exploit-ledger.md X10 (both at tag `pre-simplification-2026-08-06`) |

## 6. Systems and data-model rulings

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `S4-G19` | Two mechanics do nearly the same thing (Sly unification) — **say whether they become one** | OPEN | user-queue §2; `docs/archive/tech-debt-audit-2026-07-26.md` §5 |
| `M7` | The enchantment **op**: R82 already settled the data-model half (per-instance `enchant_damage` / `enchant_effects` ship on Card, "open house design space" — the MODEL direction, narrowly). What remains open is whether to build the Enchant *op* those fields await: the event-conversion gallery carries a live `FLAG — [USER] decision needed` on Stone of All Time "blocked on the unmodeled Enchant op" (plus Blade of Ink, the original Silent demand site). BUILD the op / keep the fields dormant | OPEN — narrowed 2026-08-07 | user-queue §10; `docs/archive/enchantments-design-2026-07-27.md` (at tag); R82; `docs/current/dossiers/content/event-conversion-gallery.md` |
| `M12` | `ROUTE_REGRET_MARGIN` (and its twin, `draft_regret`'s `+ 1.0` at `draft.py:1692`) has **no recorded derivation** — the draft literal is pinned load-bearing (MEDIUM-11) but never derived, and EB-16w's wiring inherited the analogy explicitly uncalibrated. Setting it needs either a pre-registered measurement or a ruling; until then only the margin-free reads (`mean/p50/p90/max_regret`) are quotable, and `regretted`/`regret_rate` carry the caveat in-code | OPEN — measurement or ruling | EB-16w close-out 2026-08-07; `tier05/run_metrics.py` margin note |

## 7. Eyes-on reviews and taste

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `S4-G11` | **Read card names and lore text by eye before they ship** (R29d Furina pass; Kokomi's 20 authored-but-unaudited fill cards; kickoff ask 10) — ruled to have no substitute | OPEN | user-queue §2; `tier0/DECISIONS.md` entry 75 + R29d |
| `S4-G12` / `CC-G1` / `CC-G2` | Art contact-sheet eyes-on (three re-hunt candidates incl. `grand_gala`; confirm the `standing_room_only` crop by eye) + in-game screenshot review of the twelve Curtain Call cards and the A0 smoke run | OPEN — **materials ready** | user-queue §2; `docs/archive/g12-review-2026-08-05.md` |
| `S4-G16` / `G-A5(b)` | **One screenshot: a Power being played and the Fanfare floor going up because of it** — the last of four evidence shapes (eyes-on acceptance, not telemetry). Only the three RARE `gain_fanfare_floor` Powers move the floor (`unheard_confession`, `the_sea_is_my_stage`, `rapturous_applause`), so the capture must be staged on one of those three | OPEN | user-queue §2; `review/active/red-pen-2026-07-26.md` Part 3 |
| `S4-G17` | Three running-game looks (no full playtest): `AS2-D5` salon capture; `AS2-B5` motion pass + facing taste; `AS2-E2` icon picks (4 REHUNT) | OPEN — urgency reduced (hover-targets closed pt.4; B5 "not noticed") | user-queue §2/§7; `docs/animation-sprint-2-plan.md` (B5/D5/E2), §"Gates & rulings" |
| `S4-G20` | A bundle of small leftovers: sim-vs-C# salon RNG divergence (accept or fix — C# draws the shared combat stream, the sim rolls per iteration; same seed, different members); three taste passes (Kokomi 58 faces + 15 companions, L12 duplicate pairs, `kaboom == spark_knight_style`); two infra toggles (branch protection / `gh`; manifest MAJOR bump, dormant by design) | OPEN | user-queue §2; backlog §1 P3-cluster + §5 |
| N + O TOP-5 | Read the top five findings of the lore-fidelity and instrument-redteam ledgers (both worst-first); includes `N-1` and the PROVISIONAL reactions-corpus caveat | OPEN — read | user-queue §4; `docs/archive/lore-fidelity-audit-2026-08-05.md`, `docs/archive/instrument-redteam-2026-08-05.md` |
| S8 + S10 galleries | Taste calls on two proposal galleries: eight flagged potions/relics (S8), and enemies that could be reskinned rather than redesigned (S10 — RESKIN/REDESIGN is [USER]'s per north-star) | OPEN — taste | user-queue §4; `docs/current/dossiers/content/potion-relic-conversion-gallery.md`, `docs/current/dossiers/remap/reskin-gallery.md` |
| Art debt | Kokomi 58 faces + 15 companions awaiting picks; four missing Kokomi portraits; `curtain_cue` wordmark; `breathless` mood; A7 + six Curtain Call power sigils; `AS2-E2` icon re-hunt (4 of 7); `grand_gala` re-hunt; two `ART-L12` duplicate pairs (`blazing_delight==true_spark_knight`, `crowd_work==standing_ovation`) awaiting a re-pick ruling; the three placeholder-rendering cards `art_coverage` newly bills (`spotlight_center_stage`, `spotlight_guest_cast`, `confiscated` — EB-36's engineering half is done, the picks are not) | OPEN — mostly taste | user-queue §8; `docs/archive/backlog-2026-07-29.md` §5; `docs/current/art/kokomi-art-pass-requirements.md` §2a |

## 8. Fontaine Rares close-out

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `M10` | Four items the Fontaine Rares sprint left owned by [USER]: companion art picks (Navia/Clorinde/Neuvillette/Arlecchino); the v1.7 lore/naming eyes-on audit (non-delegable); the C2 grading countersign; and close-out ratification. Design note parked with them: Neuvillette graded WEAK/DEFERRED with the "different facet" question open | OPEN | user-queue §10; `git show aa09b97:docs/current/backlog/missed-requirements.md` §4.4 |

## 9. Design calls routed from the dockets & findings

Surfaced by engineering triage, but each needs a [USER] design / taste /
behavior / money call before any code moves.

| ID | Decision needed | Provenance |
|---|---|---|
| `EB-22` | Kokomi pool fill: draft ~15–17 rare-weighted cards and ratify (the pool-count *measurement* is done) | dockets; `docs/archive/brief-kokomi-pool-fill.md` |
| `EB-26` | Kokomi P4 prevention-on-curve (an uncommon lesser ward) — a new card = content design | eng-backlog |
| `EB-27p` | **Personal-pool companion design sweep** (Prune placement subsumed, [USER] 2026-08-08): the Prune event idea predates the decision to take on cards like the Wings and the Little Hexenzirkel in a future Klee rework, so how personal-pool cards enter a run is settled for the class at the design level first — no single placement ahead of it. Inputs the sweep inherits: the spec's anchor ("node 2") is dead since RUNTEMPLATE 6, so placement is genuinely open — **(a)** guaranteed fixed floor (`MAP_TREASURE_FLOOR` precedent; every Klee run gets a free Prune, every Klee tier-0.5 number moves), **(b)** act-1 event-pool entry (`events.roll_event`; RT bump per EB-30m precedent), **(c)** run-start Neow-shaped offer; Prune is today the only `personal_pool` card, so any event is Klee-only and character-gated like `add_ancient` unless the sweep gives each character a signature; and LAW's "Personal-pool companions are the character's kit" sits against the M7 spec's "drafted normally — rewards, shop, a possible randomized starter". Nothing built pending the sweep | eng-backlog §4; `git show pre-simplification-2026-08-06:docs/archive/tier05-draft-sim-spec.md` §3; `git show aa09b97:docs/current/backlog/missed-requirements.md` §3.5 |
| `EB-32` | The pilot block-panic rung — a scheduling decision ("would move every tier-0.5 number on one observation") | eng-backlog |
| `EB-33/34/35` | Pilot/drafter repricing exhibits (The Gallery Stirs 0.0 offer; Vulnerable-as-flat-debuff; `_reaction_value` has no defensive term) — inputs to a `_static_power` / reactions-promotion repricing session | eng-backlog |
| klee-rework `X1` | Companion cost-delta accumulator remedy — a Klee-rework NOTE; nothing built against the shared-state disposition | dockets/klee-rework §1 |
| klee-rework `X7` | Klee spark-economy violations (`skip_and_hop`, `sparkly_treasure`, `crackle`) — a sitting item on R109's disjunction | dockets/klee-rework |
| klee-rework `X8` | Bomb-damage carrier-card rarity check ("need to check these cards"), priced at a sitting (the *unimplemented cap* is `X8-cap` in BACKLOG) | dockets/klee-rework §3 |
| kokomi-workshop `X9` | Kokomi charge bank ("probably too strong, parse carefully") — the next kit workshop | dockets/kokomi-workshop |
| `shared_billing` | The only Common with a cost upgrade (1→0), which the delta-grammar convention forbids — needs a [USER] call (sheet and C# agree; the conflict is with the ruled convention) | triage-memo |
| Template heal/elite economy | Node composition and pathing-agency — a structural design question | tier05-perf §1.5.2(2) |

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
