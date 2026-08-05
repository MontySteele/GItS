# S1 Parity Sweep — Triage Memo (Fable pass)

**Date:** 2026-08-05 · **Input:** 72 non-CLEAN verdicts / 111 raw findings from the 219-card sweep (`review/parity-sweep/findings-ledger.md`) · All paths relative to `/home/user/GItS`.

## Stats

| Metric | Value |
|---|---|
| Cards swept | 219 (klee / furina / kokomi + upgrades) |
| CLEAN | 147 |
| With findings | 72 cards, 111 raw findings |
| **Post-dedupe distinct issues** | **41 defects** + 5 not-a-defect rows + 1 partially-unverified caveat |

**Raw vs deduped, by family**

| Family | Raw | Deduped | Notes |
|---|---|---|---|
| text_ops_mismatch | 32 | 13 | 3 systemic clusters + 10 singletons |
| sim_vs_csharp_divergence | 22 | 14 | 4 systemic clusters + 10 singletons |
| upgrade_delta_drift | 11 | 1 | one codegen root; 7 raw rows were stale-annotation prose, reclassified |
| other | 46 | 13 | 9 systemic clusters + 4 singletons; bulk was comment drift |

**Raw vs deduped, by severity:** raw 9 high / 26 medium / 76 low → deduped **6 high / 16 medium / 19 low**. Re-grades: the vigil/guest-star/copy-rebuild mediums fold up into their HIGH systemic parents; three cadence-comment findings filed as text_ops_mismatch re-classed other/low (comment-only); two "clean baseline" upgrade rows moved to NOT-A-DEFECT.

---

## Systemic findings (ranked)

### SYS-1 [HIGH · upgrade_delta_drift] Codegen drops or inert-wires ratified upgrade deltas — sim upgrades, C# doesn't
Three cards ship upgrades that tier0 applies and the C# silently doesn't. Two shapes, one emitter:
- **blocking_notes** — `bonus_slope: +1` (`docs/furina-upgrades.yaml:83`): sim steepens the formula (`tier0/content/upgrades.py:505-516`), but the OnUpgrade emitter only has a branch for the old key name `bonus_per_detonation` (`tools/gen_klee_cards.py:4597-4599`), so `BlockingNotes.cs:71-74` is empty. Upgraded, 3 companions: sim 14 Block, C# 11.
- **the_final_verdict** — `floor_drop: -10` (`docs/furina-upgrades.yaml:155`): sim bumps crash 30→20 (`upgrades.py:410-418`); emitter has only fanfare_cap/fanfare_floor branches (`gen_klee_cards.py:4616-4623`); `TheFinalVerdict.cs:78-81` empty, crashes 30 upgraded.
- **tideline_watch** — `block_next_turn: +4` (`docs/kokomi-upgrades.yaml:75`): OnUpgrade bumps `DynamicVars["BlockNextTurn"]` (`TidelineWatch.cs:78`) but OnPlay and the description both hardcode literal 8 (`TidelineWatch.cs:44,73`) — the var has no reader. Sim banks 12; C# banks and displays 8.
- **Confirmed 4th instance outside sweep scope:** `klee-mod/KleeCode/Cards/Generated/SayuDarumaGift.cs:51,74,80` — same inert-var shape (companion sheet, not in the 219).

Regenerating reproduces all of these; they are generator defects, not stale checked-in files. Spot-checked: all hold.

### SYS-2 [HIGH · sim_vs_csharp] PreventExhaustWardPower (vigil_of_the_deep) diverges from sim on four axes
One power, four disagreements (merges 2 high + 2 medium raw findings):
1. Ward applies **before Block** in C# (`KuragePowers.cs:462-471`, additive modifier) vs **after Block** in tier0 (`tier0/engine/combat.py:658-661`) — different HP and Block on partially-blocked hits; the C# comment claims sim parity while implementing the opposite.
2. Fully-blocked hit still **burns the once-per-turn latch and exhausts a draw-pile card** in C# (`KuragePowers.cs:445-453` captures raw incoming; `:486-511` latches on it) vs no proc in sim (`effects.py:2058-2061` gates on unblocked residual). Player-visible: cards leave the pile on hits that dealt nothing.
3. C# fires on **any damage**, never testing `props.IsPoweredAttack()`; sim reaches the ward only from the enemy attack branch (`combat.py:634`); both descriptions say "attack damage".
4. Sheet `max_stacks: 6` enforced in sim (`powers.py:170-171`), **no cap in C#** — no `TryModifyPowerAmountReceived` anywhere in `KuragePowers.cs` (verified: 0 matches). Second copy → 12 vs 6.

### SYS-3 [HIGH · sim_vs_csharp] Guest Star `cost_override` lifetime: combat-permanent in sim, this-turn in C#
Root: `tier0/engine/effects.py:1205-1206` overwrites the token's base cost permanently (inline comment says "this turn", `upgrades.py:435` says "this combat" — the sim leg is internally inconsistent three ways), vs `GuestStarGenerator.cs:48-51` `SetThisTurn`. Any generated guest held past the turn: free forever in sim, printed cost in mod. **Instances:** guest_list (raw high), an_invitation, command_performance (raw mediums — re-graded up: same root, same player-visible energy cost, and Command Performance+ makes the held-over guest the normal case). C# matches its own printed text and base-game Discovery; tier0 looks like the drifting leg. Spot-checked: holds.

### SYS-4 [HIGH · sim_vs_csharp] Copy-by-model-id rebuild drops instance state (vs sim's deepcopy)
Root pattern: `CombatState.CreateCard(ModelDb.GetById<CardModel>(id))` rebuilds a pristine card; tier0 deep-copies the live hand instance. **Instances:** shoulder_to_shoulder (raw high — C# copy loses the conscript −1 cost and `ExhaustOnNextPlay` (`KokomiConscript.cs:150-165` is instance-scoped, `ShoulderToShoulder.cs:81-87` rebuilds), so it never feeds the Charge funnel; sim carries cost/exhaust/conscripted, `effects.py:1713-1722, 2020-2027`); encore_performance (raw medium — copied upgraded card comes out unupgraded, `EncorePerformance.cs:71-72`). Dormant at `BorrowedBrilliance.cs:68`. Spot-checked: holds.

### SYS-5 [HIGH · sim_vs_csharp] encore_performance copy pool includes the kit Burst
`effects.py:1231-1232` filters `not c.kit_card`; `EncorePerformance.cs:64-65` filters only `IsSpotlighted` — no `KitGrant.NotKitCard` (`KitBurst.cs:141` exists for exactly this). Retained full-meter Burst is selectable/duplicatable at cost 0 when upgraded. Emitter never emits the filter (`gen_klee_cards.py:3379-3400`), while the discard emitter does. Spot-checked: holds.

### SYS-6 [HIGH · text_ops_mismatch] salon_debut prints "Gain 2 Encore" but grants 4 on a replacement deploy
`SalonDebut.cs:51` literal `{IfUpgraded:show:Gain 2 Encore|}`, empty CanonicalVars (`:54-58`), OnPlay `2 * (salonReplacements > 0 ? 2 : 1)` (`:73`); sim doubles identically (`effects.py:1012-1013`). Every sibling salon-deploy renders the doubled number via `{Encore:diff()}` + `ReplacementDelta` (GrandGala, SurintendanteChevalmarin, OverflowingHospitality). Root: the `add: {op: gain_encore}` upgrade-delta path emits an IsUpgraded literal instead of the CalculatedVar path. Starter card; routine case. Spot-checked: holds.

### SYS-7 [MEDIUM · text_ops_mismatch] Fanfare rider hover tip says "damage" on pure-Block cards
`FurinaRiderTips.cs:87-93` hardcodes the noun "damage" ("+1 damage per 4 Fanfare… already counted in the number above") with no `grantsBlock` flag — the Salon rider body has the noun switch (`:103-105`). **Instances filed:** aria_of_recompense, held_breath, suffering_for_art, thunderous_ovation; **hearts_swelling** confirmed same helper (5 cards affected; verified all five call `ForCard`). Numbers correct; noun wrong on every face-inspect.

### SYS-8 [MEDIUM · other] "Flagged in manifest" is false — the no-upgrade safety net is empty
Both `Furina/Generated/manifest.json` and `Kokomi/Generated/manifest.json` have `"no_upgrade_path": {}` (verified), yet blocking_notes and the_final_verdict claim "Flagged in manifest." `tools/lint_upgrade_coverage.py:134-140` reads exactly that dict, so SYS-1 shipped green. Companion defect to SYS-1: the reason its instances were invisible.

### SYS-9 [MEDIUM/LOW · text_ops_mismatch] Codegen grammar/pluralization/styling template gaps — 11 findings, 10 cards
One family: template branches in `tools/gen_klee_cards.py` bypassing the house plural/keyword conventions.
- **gleeful_barrage (MEDIUM — behavior-misleading):** times_formula branch hardcodes singular "a random enemy" (`gen:3953-3957` bypasses the plural rule at `:3993`) while both engines re-roll the target per hit — reads single-target, plays as spread.
- apply_power draw templates singular "card" on upgradeable counts (→ "draws 2 card"): supporting_cast, quick_change, crowd_work (`gen:4163`, `:539-576`; also power tooltips `CurtainCallPowers.cs:374,389`, `SpotlightSystem.cs:508-519`).
- "They cost 0 this turn." on amount-1 generators: an_invitation, guest_list (`gen:4204-4211`).
- "Look at the top 1 cards": curtain_up (`gen:4294-4296`). — "card(s)" literals: tactical_retreat, epiphany_of_the_deep. — "Exhaust 1 cards" (dynamic plural pinned): ebb_tide (`gen:4299-4306`). — un-golded Encore in `_ENCORE_BAR` predicate: swelling_overture (`gen:378` vs `:368,371`).

### SYS-10 [LOW · other] Kokomi cards carry Furina's cadence doc-comment — 14 findings, 18 files
`gen_klee_cards.py:4833-4843`: only `KLEE_PROFILE` gets the catalyst sentence; the else-branch hardcodes Furina's skill-cadence line for every other roster, contradicting `docs/kokomi-cards.yaml:51` (CATALYST, R52) and the Kokomi manifest. Verified: 18 Kokomi generated files carry the string. Comment-only; runtime correct. Instances: waters_edge, surging_shoal, pulsing_current, signal_arrow, scattering_spray, tideturn, all_streams_flow, exposing_current, read_the_current, driftglass, undertow, the_tide_remembers, nereids_ascension, depths_judgment (four were mis-filed as text_ops_mismatch; re-classed other/low).

### SYS-11 [LOW · other] Ratified changes not swept through prose — 19 findings, 4 sub-roots
a. **v0.2/v0.3 repricing stale before/after annotations in `docs/kokomi-upgrades.yaml`** (6): waterspout `:35` "7->10" (base is 10), pulsing_current `:45` "6->9" (base 7), pearl_barrage `:52` "3 + 2/…" (base 5), quiet_harbor `:116` "6->9" (base 5), nereids_ascension `:136` "10->14" (base 12), depths_judgment `:140` "8 + 3 per 2" (base 10, per applied per card). All verified against card rows/C#. The file self-documents this class (surging_shoal note `:47-50`).
b. **uncap-all ruling 2026-07-24 stale cap comments** (5): grand_salon, top_billing, standing_ovation, rapturous_applause ("cap … unchanged" in upgrades sheet) + playtime_forever (klee `DECISIONS.md:794` cap claims contradicted by `test_pass2.py`).
c. **Fanfare-rework / v0.4 stale prose** (4): ebb_and_flow ×2 (encore_gained deleted; "rings the bell BOTH ways"), the_sea_is_my_stage (deleted rarity grant), ceremonial_garment ("Meter 10 / two bake plays fill it" vs burst_max 20).
d. **Kokomi misc** (4): bake_kurage ×2 (KURAGE_DURATION "3"; retired divisor grammar — already copied into `tools/role_tempo.py:383-387`), nereids_ascension worked example ("20-to-all" at base 12 → 22), pearl_current bogus "mercy_of_the_deep-parity" rationale.

### SYS-12 [LOW · other] Stale doc comments in code — 9 findings
Hand-written Klee `.cs` sheet-number comments: kaboom ("damage 6" vs 7), sizzle ("7; +5" vs 8/+6), flame_dance ("7" vs 9). Plus: catalytic_conversion (live "NO UPGRADE PATH" comment post-R37), sparks_n_splash (pool-membership claim), gleeful_barrage (SparksAsResolved pre-R39 comment), no_holding_back (`effects.py:502` names it for a removed branch), command_performance (equal-rarity docstrings in both engines), ceremonial_garment ("Nereid's Ascension enters it too" — false).

### SYS-13 [LOW · other] One stale comment, filed three times: `FurinaResources.cs:191-192` "RaiseFanfareCap (retired grammar, no sheet user)"
~16 Furina cards are live users post-Track-B; the same file un-retires it at `:84`. Raw findings on grand_salon, pit_orchestra, reginas_mercy → one defect. Verified.

### SYS-14 [LOW · other] Salon replacement multiplier as bare literal 2
`SalonDebut.cs:73` and `OverflowingHospitality.cs:74` hardcode `? 2 : 1` instead of `SalonConstants.ReplacementNumericMultiplier` (`SalonPowers.cs:34` == `tier0/constants.py:298`). No divergence today; escapes the constant-parity gate. (Same literal-vs-named failure mode as SYS-1's tideline literal — see lint L5.)

---

## Remaining singletons

### text_ops_mismatch
| Card | Claim | Cites | Sev |
|---|---|---|---|
| chain_fuse (klee) | Text reads turn-long "Bombs placed this turn deal 3 more" but both engines snapshot-mutate existing bombs before placing; the card's own bomb is never buffed (4 stays 4, not 7) | `Generated/ChainFuse.cs:47,67-75` vs `docs/klee-cards.yaml:33`, `effects.py:916-921`; behavior ratified `klee-mod/DECISIONS.md:1158-1160`, wording is not | med |
| kaboom_beetle_swarm (klee) | "Bombed enemies take +N per hit" reads live but both legs snapshot at cast (8/8/8 not 8/5/5). **Already tracked** — dedupe against `docs/open-playtest-items.md:235-240` (R72 item 4) | `KaboomBeetleSwarm.cs:56,93-111` vs `effects.py:579-597`, `test_klee.py:556-558` | med |
| sparkly_explosion (klee) | Places Bombs, names them, ships `includesBombRules: false` — the tooltip scan only walks top-level effects, missing the conditional's then-branch (verified `gen:4723-4726`) | `SparklyExplosion.cs:43,50,85` vs `docs/klee-cards.yaml:196` | med |
| true_spark_knight (klee) | Spark power tooltip hardcodes "3" in both clauses while threshold and spend are live at 2 after this card (`SparkPower.cs:61-62` static vs `:52-55` correct math); minor sibling: card face omits the "(minimum 1)" clause | vs `docs/klee-cards.yaml:202`, `combat.py:24-27` | med |
| crashing_waves (furina) | +5 aura rider added inline at resolve, never rendered in the number/preview and no aura hover tip (siblings TorrentialTurn and FlameDance both render it); plus singular "the enemy" wording on a per-target AoE rider; plus (masked, low) spotlight-multiplier folds rider inside where sim excludes it | `CrashingWaves.cs:49,64,44` vs `effects.py:530-532,598-599`, `TorrentialTurn.cs:41,56` | med |
| overflowing_hospitality (furina) | On a full Salon the Hydro application runs twice (both legs agree) but face prints a static singular clause — only replacement-scaled effect with no dynamic-var display | `OverflowingHospitality.cs:51,74-86` vs `effects.py:874-879` | med |
| reinforcements (kokomi) | Muster keyword tooltip promises "transform N cards in your hand" but this card's conscript is create-mode (net +1, transforms nothing) — pool's only create-mode conscript | `KokomiRiderTips.cs:67-70`, `Reinforcements.cs:41,48` vs `effects.py:2027-2029` | med |
| suffering_for_art (furina) | Sheet directs "no zero is printed" but the bound `{CalculatedBlock:diff()}` renders "Gain 0 Block." below 4 Fanfare (shared with the base-0 rider cards) | `docs/furina-cards.yaml:198-202` vs `SufferingForArt.cs:48,55-57` | low |
| let_the_people_rejoice (furina) | Only Hydro-applying Furina card that never chains the element hover tips (hand-written; all generated siblings do) | `LetThePeopleRejoice.cs:46-48` vs `HighTide.cs:46-47` | low |
| all_streams_flow (kokomi) | Charge-rate (1 per 2) displayed nowhere — `rider_tip_args` handles only fanfare/salon/companion formulas (verified `gen:1667-1674`); Garment tip's "Not included in the number above" then reads as excluding the card's own unlabeled rider (sibling: nereids_ascension) | `AllStreamsFlow.cs:46-54` vs `KokomiRiderTips.cs:103-109` | low |

### sim_vs_csharp_divergence
| Card | Claim | Cites | Sev |
|---|---|---|---|
| ebb_and_flow (furina) | Encore cost is a hard unmodifiable gate in sim (`combat.py:117,207-208`) but discountable in C#: EncoreResource is the mod's only custom-resource cost with **no CanAfford override** (verified `FurinaResources.cs:111-128` vs the FurinaBurstResource override at `:245-251`); SpotlightDiscountPower can zero it, skipping the Fanfare mint. Also exposes dress_rehearsal | see also `BurstResource.cs:107-121` | med |
| leading_role (furina) | Discount window: global counter ticked pre-resolution in sim (`combat.py:169,224` — verified) means the card burns its own window; C# per-instance counter starting at 0 (`SpotlightSystem.cs:481-490`) leaves it live same turn | | med |
| supporting_cast (furina) | spotlight_draw resolves inline pre-card-effects in sim (`combat.py:236-252`) vs deferred to AfterCardPlayed in C# (`SpotlightSystem.cs:363-368`, `FurinaResources.cs:791-794`) — opposite pile-interaction order for first-play draw cards | | med |
| blocking_notes (furina) | Replayed (Duet'd) Companion counts once in sim (`combat.py:268-275`, outside replay loop) vs twice in C# (`CurtainCallPowers.cs:203-209`, deliberately per play index) — 7 vs 9 Block worked case | | med |
| rapturous_applause (furina) | fanfare_attack_per10 is a per-card snapshot in sim (`effects.py:2250-2267`) vs live per-hit read in C# (`FurinaResources.cs:1155-1162`); Breathless worked case 9 vs 10 | | med |
| driftglass (kokomi) | Sly damage collects the Garment charge bonus in C# (`Driftglass.cs:90-94` + `KuragePowers.cs:313-320`) but not in sim (sly resolved inline at discard site, reads the discarding card's bonus, `effects.py:1354-1356,2251,541`) — only damaging Sly on the sheet | | med |
| standing_ovation (furina) | Spend boost expires at player turn end (sim) vs next turn start (C#); no reachable consumer found — render-only during enemy turn | `powers.py:23,139-144` vs `SpotlightSystem.cs:300-307` | low |
| surging_shoal (kokomi) | Garment per-attack Block pre-damage in sim vs AfterCardPlayed in C#; unobservable without thorns/mid-play readers | `effects.py:2258-2266` vs `KuragePowers.cs:350-361` | low |
| sizzle (klee) | Overkill edge: C# IsAlive guard suppresses the rider; sim re-picks the target (documented engine-wide caveat, `effects.py:245-247`); Sizzle-only guard | `Sizzle.cs:79` | low |
| vermillion_pact (klee) | 4x amp-cap detector measures final post-pipeline damage in sim (`effects.py:375`) vs the amp multiplier alone in C# (`ReactionTable.cs:118-120`) — diagnostics only | | low |

### other
| Card | Claim | Cites | Sev |
|---|---|---|---|
| shared_billing (furina) | Only common on any sheet with a cost upgrade (1→0); the delta-grammar authority forbids it ("commons never upgrade cost" — verified `docs/upgrade-conventions.md:8,28`); sheet and C# agree with each other, conflict is with the ruled convention — needs a [USER] call | `docs/furina-upgrades.yaml:81`, `SharedBilling.cs:62,87` | med |
| duet (furina) | Granted power displays as "Study Buddy" with Klee's icon in a Furina run — only cross-character-titled power; the class of defect was closed in Sprint 2 Track E but this one wasn't swept | `CompanionPowers.cs:149`, `KleePowerIcons.cs:56` | low |
| controlled_demolition (klee) | Sheet comment still carries the telemetry figure the red-pen record retracted (4.7% "unchanged" vs measured 7.0%) | `docs/klee-cards.yaml:123-124` vs `docs/red-pen-2026-07-26.md:227-231` | low |
| pearl_barrage (kokomi) | role-tempo classifier's `pays_at_zero` never reads `amount_formula.base` (verified `tools/role_tempo.py:583-586`), so the base-5 card is documented/tagged "deals nothing at empty pile" — one of three flat-scan gaps (see lint L4) | `test_role_tempo_coverage.py:263-265` vs `effects.py:216-218` | low |

---

## Lint candidates (catch-to-lint: every root with ≥3 instances)

- **L1 — Upgrade-delta completeness (SYS-1 + SYS-8, 3–4 instances).** For every card with a delta in `docs/*-upgrades.yaml`: (a) the generator's upgrade plan must emit ≥1 OnUpgrade line, (b) every DynamicVar bumped in OnUpgrade must be referenced by OnPlay or the description, and (c) any shortfall must land in manifest `no_upgrade_path` — which `tools/lint_upgrade_coverage.py` should cross-check against the upgrades yaml instead of trusting the (currently empty) dict. Lives in `tools/gen_roster_cards.py --check` + `tools/lint_upgrade_coverage.py`.
- **L2 — Cadence comment from profile (SYS-10, 18 files).** Emit the cadence doc-comment from the profile's manifest cadence string instead of the two-branch hardcode at `gen_klee_cards.py:4833-4843`; check = assert emitted comment matches `manifest.json` profile cadence. Pin in `tier0/tests/test_roster_codegen.py`.
- **L3 — Rider-tip noun matches the op (SYS-7, 5 cards).** `FanfareBody` must take (or derive) the Block/damage noun from the op the `bonus_formula` rides, like `SalonBody` already does; test pinning tip text for a block-op fanfare-rider card. Lives in test_roster_codegen.
- **L4 — Flat effect-list scans (3 instances: sparkly_explosion `gen:4723-4726` no conditional recursion; pearl_barrage `role_tempo.py:583-586` ignores `amount_formula.base`; `rider_tip_args` `gen:1667-1674` unaware of charge formulas).** Shared `iter_effects()` that recurses then/else and normalizes amount/amount_formula; a tools/ lint asserting no scanner iterates `card["effects"]` raw.
- **L5 — Literal-vs-named sheet numerics (≥5 sites: tideline/sayu literal 8/4, salon_debut + overflowing literal 2, salon_debut literal Encore 2).** gen --check rule: emitted OnPlay/description numerics must come through DynamicVars or named constants (`SalonConstants.ReplacementNumericMultiplier`), never bare literals, when a var/constant exists for them.
- **L6 — Grammar/plural pass (SYS-9, 11 instances).** gen --check text lint over emitted descriptions/power tooltips: reject `card(s)`, `top 1 cards`, `1 cards`, hardcoded singular nouns adjacent to upgrade-movable vars lacking `{…:plural:|s}`, plural pronouns on amount-1 clauses, and un-golded resource keywords (extends the existing pin at `test_roster_codegen.py:943-944`).
- **L7 — Comment-arithmetic lint on upgrades sheets (SYS-11a, 6+ instances).** tools/ lint parsing `# a->b` annotations in `docs/*-upgrades.yaml` and recomputing from the card row's base + delta; `lint-ok:` markers exempt history notes. Same lint can flag "cap N unchanged"-style claims where the referenced op has no `max_stacks` (SYS-11b, 5 instances).
- **L8 — Copy/generate emitter contract (SYS-3/4/5, 3+ sites).** gen --check: every emitted copy/generate path must state provenance (instance clone vs model rebuild) and carry `KitGrant.NotKitCard` where the sim filters kit cards; plus a cross-engine parity test pinning copy cost/upgrade/exhaust state and cost-override lifetime.

## NOT-A-DEFECT (governing cite)

1. **crowd_work** draw deferral (C# AfterCardPlayed vs sim inline) — **ruled** R86, `tier0/DECISIONS.md:2778-2781`.
2. **borrowed_brilliance** `temp: true` ignored by both engines — **ratified** "accepted and IGNORED (sim is LAW)", `klee-mod/DECISIONS.md:1345-1348`; the dead sheet field remains a sheet-hygiene item only.
3. **no_holding_back** second row — agent's own parity-evidence record, states agreement.
4. **shared_billing** sim row — self-declared verified-clean baseline.
5. **shoulder_to_shoulder** upgrade row — self-declared checked-and-clean ("IGNORE FOR SCORING").
Sweep-level: agents correctly did not flag catalyst-header pyro application, burst/kit upgrade exclusions (`docs/furina-upgrades.yaml:3-4`), or manifest-blocked hand-written cards — no residual false positives of those classes found.

## UNVERIFIED (kept, not dropped)

- **ebb_and_flow reachability half:** the missing `CanAfford` override on EncoreResource is **verified fact**; but the claim that SpotlightDiscountPower's hook actually pipes through custom-resource costs rests on three in-repo doc comments (`BurstResource.cs:107-121` etc.) because **BaseLib is not vendored** — the exploit path cannot be confirmed from this repo. Finding stays ranked medium with this caveat.
- **leading_role** "verified by running the sim" — the agent's execution claim was not re-run (non-goal: nothing executed); the static evidence independently supports the finding.

**Spot-checks performed (all HELD):** all 9 raw highs (salon_debut, blocking_notes, guest_list, encore_performance, the_final_verdict, shoulder_to_shoulder, tideline_watch, vigil_of_the_deep ×2) re-read at cited lines; plus cluster roots — cadence template branch + 18-file count, FanfareBody noun + 5 call sites, both empty `no_upgrade_path` manifests + the lint that reads them, GuestStarGenerator/upgrades.py lifetime comments, EncoreResource CanAfford absence, `includes_bomb_rules` flat scan, kokomi-upgrades stale annotations vs card rows, `upgrade-conventions.md` commons rule, `FurinaResources.cs:191` comment, KuragePowers cap absence, `rider_tip_args` charge gap, leading_role counters, and the SayuDarumaGift fourth instance. No spot-check failed; nothing was moved to UNVERIFIED for evidence failure.

## How to read this (couch sitting)

The sweep's 111 findings boil down to 41 real issues, and only six need decisions with numbers attached: three upgrades the C# silently drops (SYS-1), the vigil ward's four-way divergence (SYS-2), the guest-star cost lifetime where tier0 itself is probably the wrong leg (SYS-3), the copy-rebuild state loss (SYS-4/5), and salon_debut's face lying by half (SYS-6). Everything below that line is either misleading text from a handful of codegen templates (fixable at the generator, lint-able forever) or stale prose left behind by rulings you already made. Nothing here was fixed, reworded, or executed — every item waits on you, and the lint-candidates section is the shortlist of checks that would keep each class from coming back.
