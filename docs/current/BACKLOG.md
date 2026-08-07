# BACKLOG

> **Only OPEN executable engineering work** — confirmed defects, mechanical /
> parity fixes, measurement instruments, refactors, and test-writing that need
> **no [USER] design call to start**. One of six governing files, no overlap:
> [USER] design / taste / behavior / money calls live in **QUEUE.md**, settled
> rules in **LAW.md**, shipped facts in **STATE.md**, commands in
> **OPERATIONS.md**. Identifiers are preserved from their source registers;
> closed items are in git history (tag `pre-simplification-2026-08-06`).

> **Resolving a provenance identifier.** `eng-backlog`, `dockets/…`,
> `user-queue` and the retired sprint docs read at
> `git show pre-simplification-2026-08-06:<path>`. The two recap registers —
> `missed-requirements` and `open-playtest-items` — left HEAD after their
> rows migrated here; read them at
> `git show aa09b97:docs/current/backlog/missed-requirements.md` and
> `git show aa09b97:docs/current/playtest/open-playtest-items.md`
> (`git fetch --depth=1 origin aa09b97` first on a shallow clone).

---

## tier0 — engine, pilot, constants

| ID | Item | Provenance |
|---|---|---|
| `EB-17p` | Force-first-copy **paired** winrate — the register's actual phrase: two decks on the same seeds, one with a copy forced in, one without. Deck construction is barred from the tier0 kernel, so this is a tier05 experiment under EXPERIMENTS pre-registration. The fight-side half ships (`metrics.card_flow_profile`, `--card-flow`) and explicitly declines to call its within-arm split the pairing | fix-sweep-2; EB-17 residual |

## tier0.5 — draft / run layer / measurement

| ID | Item | Provenance |
|---|---|---|
| `EB-16w` | Wire `route_regret` into the live run layer: `model.run_one` walks incrementally and `RunResult` records no route decisions, so nothing calls the sampler on a real run yet (`route.walk_decisions` exists for it); promote the sample-rate default to `tier0/constants.py` and calibrate `ROUTE_REGRET_MARGIN` (the 1.0 is a literal `draft_regret` analogy, not a measured threshold). Then §3.7.5's "relics underpriced" comparison can actually be re-run | fix-sweep-2; EB-16 residual |
| `EB-27` | Two tier0.5 spec features never built: `choose3` standalone slot mode (`model.py:246-250` raises `ValueError`) and the Prune signature event (`events.py` offers none) | eng-backlog §4; missed-requirements §3.5 |
| `EB-30m` | Model the three Ancient cards sim-side (unblocked by R127's carve-out): `jumpy_dumpty_mk_omega` (12×3 random hits + Bomb on every enemy), `princess_of_watatsumi` (`charge_per_turn` 3, +1 on upgrade), `all_the_worlds_a_stage` (`encore_per_turn` 5, +2 on upgrade). Constraints from the C# side: card rows live OUTSIDE the ratified sheets (the C# classes are hand-written; codegen must not see them — use a loader side-sheet like the ref decks), `ancient` rarity stays invisible to draft/reward/shop (`RARITY_ODDS` carries no row, mirroring the game's upstream filters), and the Darv/Dusty Tome act-2 event is the single door and grants the card UPGRADED. The `encore_per_turn` income's order vs the Salon upkeep in `player_turn_start_triggers` becomes `EB-2`'s parity target — pin it deliberately, income before upkeep, so the card's printed "at the start of your turn" funds that turn's ticks | R127; EB-30q |
| `EB-24p` | The pilot cannot see through an unlisted conditional: `policy._active_effects` skips the WHOLE conditional for predicates not on its allowlist — both branches, including an unconditional else — so `audience_participation` (R85 rework: reaction-read, else-branch 2 Encore + 1 draw) scores ~0 and measured drawn 974 / played 0. Add `reaction_triggered_this_turn` (`state.reactions_this_turn`, the Chevreuse window) to the readable set; POLICY-stamp surface, own window. Re-census after — only a still-dead card with a sighted pilot is a design question (worksheet: `review/active/eb24-dead-riders-worksheet.md`) | EB-24 decomposition 2026-08-07; EB-20 census |
| `EB-28` | The drafter's salon-deploy blindness — `tier05/draft.py:_static_power` has no `salon_member` term, so cross-plan the members are invisible | eng-backlog §4; missed-requirements §3.6 |
| `EB-29t` | Pilot counterplay for the promoted Test Subject mechanics (R128): the dossier's *basic* correct play — prefer attack-only turns under Enrage (every Skill feeds +2 permanent Strength), dump nothing into Intangible turns (P3 alternates a 1-damage-per-hit cap) — is played by NO pilot, so the C7 full-HP read is 0.0–3.9% for all four characters: the worst possible line, not the average player. Teach the play policy the two reads (`enemy.powers.enrage` skill tax; `intangible` turn discount on expected damage) — POLICY-stamp surface, own window, then re-run the boss instrument | R128; EB-29q closure 2026-08-07 |
| `EB-43` | **D15 (spotlight-limb payoff-presence) — STAGED, HELD.** Drafter behaviour change (`DRAFTER 15`) + re-baseline sweep; `Q18` countersigned, pinned DRAFTER 14. **Lands as step (5) of a fixed six-step order** — must not land before blind-first grading (4) or it invalidates the registration | eng-backlog §6; R121 |
| `SKIP-10.9` | Living skip-backlog of un-modelled mechanics to promote when a pass needs them. **Enemy:** Back Attack (Kaiser Crab), untargetable Burrow (Tunneler), Ethereal/Hex auras (Knight Gang), pick-your-poison curse choice (Knowledge Demon), damage caps (Hard to Kill / Plating / Hardened Shell), Artifact, Thorns, on-hit status injection, every-N-cards cadence intents, buff-all-enemies, block-an-ally, random-no-repeat AI, self-stun, Slimed self-exhaust, the minor-power list (Imbalanced / Ringing / Paper Cuts / Stock / Galvanic / Rampart), Soul Siphon stat-theft class (the Matriarch's player-half drain landed with EB-25), and the two Ancient relic hooks — Blessed Antler and Philosopher's Stone. **C#-side structures with no sim twin (EB-19):** the deferred-settle machinery (`SpotlightSystem` PendingDraws / `CurtainCallPowers` NoteEncoreSpent / `FurinaResources` PendingDeltaBlock — parity rests on every flush site being reached; a stranded draw is the failure mode) and per-dealer reaction windows (ruled co-op divergence, red-pen R1; solo is byte-identical). *Restored to the full §10.9 open list 2026-08-06 — the migration had dropped ~14 entries, making logged approximations read as unlogged fakes (EB-29c)* | run-model-rework-plan §10.9; EB-29 audit |

## klee-mod — C# implementation & parity

| ID | Item | Provenance |
|---|---|---|
| `EB-1` | **Punch Off crash** (reclassified GAME-SIDE/SPINE-SIDE) — the animation stream keeps the watch; not done while seed `8B97LMCL2F` crashes in Punch Off | eng-backlog §1 |
| `EB-2` | Salon upkeep vs All the World's a Stage income race — two powers in the same `AfterPlayerTurnStart` broadcast with no guaranteed order (`SalonPowers.cs:413` vs `FurinaResources.cs:1126`); nondeterministic tick rate. The EB-19 sweep found a third participant in the same broadcast — see `EB-19/races-b` | eng-backlog §1; `NC-9` seam; EB-19 |
| `EB-18` | The mod's per-fight telemetry (C2) was never built — JSON-lines per fight; `tier1/analyze.py` reads per-**run** granularity. Answers the corpse-detonation count for free | eng-backlog §3; missed-requirements §2.3 |
| `EB-19/M1` | Courtroom Drama's Vulnerable is applied from `AfterDamageReceived` (`CurtainCallPowers.cs:271` via `ReactionEffects.cs:145`), so a **card-triggered** first reaction does not amplify its own hit — the sim applies it before `modify_damage_taken` (`reactions.py:167-170` / `effects.py:367`) and the bomb path (`ElementalHit.cs:50-55`) already amplifies. Same shape as the 2026-07-21 Superconduct fix: mirror the ×1.5 in `AuraPower.ModifyDamageMultiplicative` behind a first-reaction guard, + a PHASE_LEDGER row | fix-sweep-4; EB-19 sweep |
| `EB-19/races-a` | Masque of the Red Death's Bond-of-Life pays in `BeforeSideTurnEnd` racing the Kurage pulse's Block grant (`FontainePowers.cs:191` vs `KuragePowers.cs:72→105`; sim pays strictly first, `effects.py:2588`) — a 5-Block swing per turn for Kokomi+Arlecchino. EB-2's broadcast co-tenancy class: nondeterministic, so fixed-seed parity passes while the bug lives. Fix idiom in-repo: stage into strictly earlier/later broadcasts (`CurtainCallPowers.cs:58-69`; `CompanionPowers.cs:316`) | fix-sweep-4; EB-19 sweep |
| `EB-19/races-b` | `SpotlightSystem.ResetTurn` clears the Standing Ovation spend-boost in the same `AfterPlayerTurnStart` whose Salon upkeep mints it (`SpotlightSystem.cs:300` via `FurinaResources.cs:911` vs `SalonPowers.cs:427`; sim clears at turn END, `powers.py:23,156`). Same class and fix idiom as `EB-19/races-a` | fix-sweep-4; EB-19 sweep |
| `EB-19/races-c` | The three end-of-turn elemental volleys (`KitBurst.cs:74`, `CompanionPowers.cs:272`, `KuragePowers.cs:72`) are unordered vs the sim's fixed Pyro→Electro→Hydro (`effects.py:2596-2658`) — reaction boards and the shared RNG stream diverge. Same class and fix idiom as `EB-19/races-a` | fix-sweep-4; EB-19 sweep |
| `EB-19/M5` | Navia's `cannon_fire_support` pays on her own play in C# (`AfterCardPlayed`, `FontainePowers.cs:60-69`) but not in the sim (power read pre-resolution, `combat.py`, intent stated in-line). Confirm the broadcast's listener-enumeration point, then snapshot presence at `BeforeCardPlayed` and settle after | fix-sweep-4; EB-19 sweep |
| `EB-19/M7` | `refpowers.py:29-36` and `AuraPower.cs:172-177` state **incompatible orders** for `AfterSideTurnStart` vs the hand draw and `AfterPlayerTurnStart` — the aura tick's position relative to Salon upkeep rides on it (wrong side re-opens the 2026-07-21 aura-expiry class). Settle against the decompiled `CombatManager` (the game_ref extractor can produce it), correct the losing doc, add the resolved order to `test_reaction_phase_parity`'s PHASE_LEDGER | fix-sweep-4; EB-19 sweep |
| `EB-19/M8` | `FurinaResourceHooks.BeforeCardPlayed` drains Burst before spending the Encore cost (`FurinaResources.cs:767,786`), the reverse of the sim (`combat.py` spend-then-drain), and its own comment at `:765-766` asserts the sim order it does not implement. Latent — no sheet card carries `encore_cost` on a Burst card. Reorder + fix the comment before a sheet edit makes it reachable | fix-sweep-4; EB-19 sweep |
| `NC-parity` | The C# side reads companion rarity from `Star`, not the sheet's `rarity` field — whether the cycling-rarity gate (X2 law) is enforceable in C# at all is open | dockets/companion-pricing §2 |
| `EB-14` | `selectors` is bot-feed only — a mod-side hook into the selection screens is the open item | eng-backlog §2 |

## tools — codegen, lint, scripts, refactors

| ID | Item | Provenance |
|---|---|---|
| `EB-41` | Refactors, only if budget remains (big, safe, boring): `run_one` 518-line split; codegen driver unification (F3); telemetry-module template dedupe; `exp_*` script archive move; `apply_upgrade` op-coverage guard | eng-backlog §7 |
| `L4a` | `sparkly_explosion` ships `includesBombRules: false` — its `place_bomb` sits in the kill-conditional's `then:` (`klee-cards.yaml:198`), invisible to `gen_klee_cards.py:4955`'s flat scan, and `lint_handwritten_parity.py:836` mirrors the same flat scan so the gate agrees with the defect. Fix the generator AND deepen the parity gate in the same commit (else the gate flips red), regen C# (Windows validation), then retire `lint_effect_branch_scans`' `TOP_LEVEL_ONLY[lint_handwritten_parity]` + `BRANCH_ONLY_KNOWN[sparkly_explosion]` entries | fix-sweep-4; L4 verified live |
| `L4b` | The `1_per_2_charge` rate is rendered nowhere on `all_streams_flow` / `nereids_ascension` / `read_the_current`: `gen_klee_cards.rider_tip_args` has no `chargePer` branch and no C# tip argument exists. Generator + KokomiRiderTips + regen (Windows validation) | fix-sweep-4; L4 verified live |

## tests — pins & filed-not-fixed

| ID | Item | Provenance |
|---|---|---|
| `EB-11` | Understudy Defect 13 — `no_action` on a state with no `state_type`; **FILED, NOT FIXED** (next traversal pass) | eng-backlog §2 |
| `EB-12` | Understudy Defect 14 — `bridge_unreachable` by timeout with the process alive; one observation, no reproduction; **FILED, NOT FIXED** | eng-backlog §2 |
| `EB-13` | Understudy Defect 15 — `no_progress`, the map↔rest_site bounce (seed `43MLG7MG9L`); **FILED, NOT FIXED** | eng-backlog §2 |
| `EB-15` | The seed's `lobby` route never fired in three live runs; the lobby arm is retained and reports itself — nobody should read "two routes work" out of it | eng-backlog §2 |

## art — production work (the *picks* are [USER]'s in QUEUE; these are not)

| ID | Item | Provenance |
|---|---|---|
| `EB-36` | Three shipped cards render the BETA placeholder and are invisible to the coverage tool (`spotlight_center_stage`, `spotlight_guest_cast`, `confiscated`) — zero `art/plan.tsv` rows; structural blind spot in `tools/art_coverage.py` | eng-backlog §6; missed-requirements §4.1 |
| `EB-37` | The character-icon `_outline` asset was never produced — `Klee.cs:146`,`Furina.cs:84`,`Kokomi.cs:134` all return the fill `char_icon.png`; no outline row in plan/SOURCES | eng-backlog §6; missed-requirements §4.2 |
| `EB-38` | Animation Track F3 + the sprint-1 polish deferral — rest/merchant gentle idles both characters; in-combat layer approved and frozen but no polish sprint opened | eng-backlog §6; missed-requirements §4.5 |
| `EB-39` | `no_holding_back` still uses the `Klee Multi Wish` source L6 flagged as trimming 76% of the image | eng-backlog §6; missed-requirements §4.6 |
| `EB-40` | Furina's energy counter: `Furina.cs:97` still points at `ironclad_energy_counter.tscn`; `energy_icon_74/22` have no plan rows | eng-backlog §6; furina-art-pass-requirements §8 |
| `EB-42` | Path B (Skeleton2D) animation spike — a normal Code sprint, ruled FREE-SPIKE (Kokomi pilot); Path C layered remains the shipped fallback. (The spike→Spine-licence $379 reconsider is a QUEUE money call) | eng-backlog §6; R118 |
