# Companion Pool Value vs. the Base-Game Colorless Bar — A Balance Study

**Author:** balance-research pass (Claude Code)
**Date:** 2026-07-21
**Question under test:** The mod replaces StS2's base colorless card pool with the custom *Companion* pool. Colorless cards are conventionally costed **above** value-per-energy (acontextual premium splash). Companion cards were deliberately balanced **below** base-kit power (the enabler-not-carry principle, principles §4.3). Have we accidentally made the companion pool *trash* relative to the colorless value bar it now has to fill?

**Hypothesis to test (user's):**
`companion commons < base colorless commons < companion uncommons < base colorless uncommons < rares (both ≈ equal)`

---

## TL;DR verdict

**No, the companion pool is not trash — but only if you score it honestly for conditional value; the naive static reading *does* look like a failure, and that illusion is the trap.** Scored statically (no reaction payoff in deck — the "floor"), most companion appliers land at 4–5 value/energy, *below* the ~7 base-colorless-common bar, and the conditional cards (swirl/shatter/isotoma triggers) floor near **zero** — which superficially "confirms" the pool is weak. But every one of those appliers *ceilings* at 10–13 v/e (above the base colorless **uncommon** bar) the instant its element reacts, and the realistic expected value in a reaction-appetite deck sits right at or just under the equivalent colorless rarity band. The hypothesized ordering **holds at expected value and breaks only at the floor** — which is the correct, designed behavior for reaction fuel, not a bug. The single most important finding: **companion "rarity" tracks Genshin star-rank / kit-depth, not power tier**, so a rarity-label-to-rarity-label comparison against colorless is partly apples-to-oranges — several 4-star *uncommons* carry common-grade bodies by design. Only **one card (`sucrose_astable`)** is a genuine buff candidate; the rest are correctly-costed conditional fuel or, in two cases, outliers on the *strong* side.

---

## 1. Methodology & rubric

### 1.1 Baselines reused from the project (not invented)

The project already encodes a value-per-energy convention; this study reuses it rather than inventing a parallel one.

| Quantity | Project value | Source |
|---|---|---|
| Strike baseline | **6 dmg / energy** (5×Strike at 6) | `tier0-simulator-spec.md` §7; REF_IRONCLAD |
| Defend baseline | **5 block / energy** (4×Defend at 5) | `tier0-simulator-spec.md` §7 |
| Bash reference | 8 dmg + Vuln 2 @ 2 cost | spec §7 |
| Static value proxy | **`(sum damage + sum block) / cost`** | `tier05/draft.py::_static_power` — the project's own "deliberately dumb immediate-value proxy" |
| Weak | −25% damage dealt | `constants.WEAK_DEALT_MULT = 0.75` |
| Vulnerable | +50% damage taken | `constants.VULNERABLE_TAKEN_MULT = 1.50` |
| Vaporize (Pyro×Hydro) | that hit ×1.5 | `constants.VAPORIZE_MULT` |
| Melt (Pyro×Cryo) | that hit ×1.75 | `constants.MELT_MULT` |
| Overload (Pyro×Electro) | +6 dmg to ALL enemies | `constants.OVERLOAD_SPLASH = 6` |
| Superconduct (Electro×Cryo) | Vulnerable 2 | `constants.SUPERCONDUCT_VULN = 2` |
| Electro-Charged (Hydro×Electro) | DoT 4 × 2 turns (= 8) | `constants.ELECTROCHARGED_DOT = 4`, `_DOT_TURNS = 2` |
| Frozen (Hydro×Cryo) | soft control (−50% next action) + Shatter 6 on first attack | `constants.FROZEN_DAMAGE_MULT = 0.5`, `SHATTER_DAMAGE = 6` |
| Crystallize (Geo) | +4 player block | `constants.CRYSTALLIZE_BLOCK = 4` |
| Applier draft weight | **3.5** (score units, decaying with core progress) | `draft.py::REACTION_APPLIER_WEIGHT`; adaptive scorer adds `1.5 + 2.0×reaction-share` |

The critical anchor is `_static_power`: **the codebase itself scores a card as raw (damage + block) ÷ cost and credits element application through a *separate* weight**, exactly the floor/ceiling split this study needs. My rubric extends that same proxy to the other effect types.

### 1.2 Point conversions (per card, then ÷ cost for value/energy)

| Effect | Points | Justification |
|---|---|---|
| Damage (single target) | 1.0 / dmg | Strike anchor; `_static_power` sums dmg at face |
| Block | 1.0 / block | Defend anchor; `_static_power` sums block at face |
| AoE damage | 1.0 / dmg × (effective targets) | Face at 1 target for the floor; note swarm multiplier separately |
| Card draw | 2.0 / card | Tempo ≈ the body of an average 1-cost card (StS cantrip convention) |
| Burst energy (mod resource) | 0.5 / point | Only meaningful for characters with a Burst meter; `BURST_PER_REACTION = 5` implies ~1 reaction ≈ 5 burst; conditional, discounted |
| Weak (on enemy) | 2.0 / stack | −25% of ~one 6-dmg intent ≈ 1.5 mitigation, rounded to a small Defend |
| Vulnerable (on enemy) | 3.0 / stack | +50% of your next hit; stronger than Weak in an attacking deck |
| `next_attack_up N` | N (one hit) | Flat one-shot rider |
| `attack_up_this_turn N` | N × 2 | ≈ 2 attacks played the turn it lands |
| Strength / `celestial_gift +N` (permanent) | engine — see §1.4 | scales with attacks played after; not a one-shot |
| **Element application (floor)** | **0** | An off-element aura does nothing with no reaction payoff in deck |
| **Element application (ceiling)** | reaction credit below | The whole point of the card |

**Reaction ceiling credit** (added on top of the card's own body, per successful reaction):
- Enables Vaporize: +0.5 × the payoff hit it amplifies (≈ +5 against a ~10-dmg payoff)
- Enables Melt: +0.75 × payoff hit (≈ +7–8)
- Enables Overload: +6 (× living enemies — a swarm multiplier)
- Enables Superconduct: +6 (Vuln 2 × 3)
- Enables Electro-Charged: +8 (DoT 4×2)
- Enables Frozen/Shatter: +6–8 (soft control tempo + Shatter 6)
- Enables Crystallize: +4 block per triggering hit
- Swirl / spread: copies an existing aura to **all** enemies — a *multiplier* on applications, enormous in swarm, **zero with no pre-existing aura**

### 1.3 Floor / ceiling / expected — handled explicitly

Companion cards are hyper-contextual. A naive static score credits element application at 0 and therefore *systematically undervalues* the pool, which would falsely "confirm" the weakness hypothesis. Every conditional card below is therefore scored three ways:

- **Floor** = no reaction payoff in deck (application credited 0; swirl credited 0; `shatter_bonus`/`solar_isotoma` credited 0). This is the pessimal, "brick" world.
- **Ceiling** = the conditional fires on ~every relevant play (application → reaction every time, swirl on a live aura, etc.).
- **Expected** = the realistic middle for a **Standard companion-appetite** deck (Klee-class, principles §4.4) built to use the card: ≈ 50% of the ceiling reaction credit, which is roughly where a reaction deck's damage-share lands (`metrics.py` health band: reaction damage share 25–45%).

### 1.4 Powers (permanent engines) are rated as engines, not one-shots

Four companions are `power`-type permanent engines (`fischl_oz`, `albedo_solar_isotoma`, `durin_witchs_flame`, `nicole_celestial_gift`). Forcing a single value/energy on a repeating end-of-turn effect is dishonest, so these are rated by amortized per-fight value over a ~5-turn window and judged against "does it clear the rare bar," not by a v/e point.

---

## 2. Base-colorless reference band

> ⚠️ **BIGGEST SOURCING UNCERTAINTY — read first.** No base-game colorless card data exists in this repo. The band below is built from **Slay the Spire 1** colorless cards, which is the well-documented convention the mod's own design docs already reference. **StS2 is early-access; its colorless pool and exact numbers differ from StS1 and are still patch-volatile.** The bar the companion pool must actually clear is the *StS2* one, which I cannot verify from here. Treat every number in this section as an StS1-anchored estimate the user must re-check against current StS2 values. A second, subtler caveat: **most premium colorless cards are 0-cost utility (Blind, Dark Shackles, Discovery, Apotheosis, Mayhem)** whose "value per energy" is undefined/infinite — value-per-energy is a poor metric for half the colorless pool, so the band below is drawn only from the *costed, body-bearing* colorless cards where the metric is meaningful.**

**Colorless commons** (costed bodies, StS1): Swift Strike (7 dmg, treated as if 1-cost) ≈ 7; Good Instincts (6 block) ≈ 6; Flash of Steel (3 dmg + draw) ≈ 5; Dramatic Entrance (8 AoE, exhaust/innate) ≈ 8.
→ **Band ≈ 6–8 v/e, midpoint ~7.**

**Colorless uncommons** (StS1): Hand of Greed (20 dmg @ 2) = **10**; The Bomb (40 AoE @ 2, delayed 3 turns) ≈ 13–20 delayed AoE; plus deck-warping powers (Mayhem, Sadistic Nature, Panache) that are off-the-chart in the right deck and un-scoreable by v/e.
→ **Band ≈ 10–12 v/e for the costed attacks, midpoint ~10.**

**Colorless rares** (StS1): Ritual Dagger (15 dmg @ 1, exhaust, permanent on-kill scaling) = **15+ and self-scaling**; Apparition (Intangible — near-total single-turn mitigation, defensive premium). Payoff-grade.
→ **Payoff tier; not a v/e point but clearly the strongest band.**

The convention is visible in the numbers: colorless **commons sit at ~7 (above the 6-dmg Strike rate)** and **uncommons at ~10** — i.e., colorless is priced *above* base-kit rate, as folklore holds.

---

## 3. Companion scores

Value/energy shown as **Floor / Expected / Ceiling**. Powers (⚙) rated as engines in §3.4. "Reward pool" column notes whether the card is actually offered as a reward (guest-stars and, in reward terms, personal-pool cards are gated — `rewards.py::companion_pool` excludes `guest_star`; `personal_pool` is offered only to its own character).

### 3.1 Companion commons (4-star, common)

| Card | Cost | Body | Floor / Exp / Ceiling | Notes |
|---|---|---|---|---|
| dahlia_sacramental_shower | 1 | 4 dmg, hydro apply | **4 / 7 / 10** | Weakest applier body (4 dmg) |
| fischl_nightrider | 1 | 5 dmg, electro apply | **5 / 9 / 13** | Electro → Overload/EC/Superconduct all strong |
| kaeya_frostgnaw | 1 | 5 dmg, cryo apply | **5 / 9 / 13** | Melt/Frozen route |
| chevreuse_interdiction_fire | 1 | 5 dmg, pyro apply | **5 / 9 / 13** | Vaporize route; Fischl parity |
| freminet_pers_deploy | 1 | 5 dmg, cryo apply | **5 / 8 / 12** | His freeze-initiator |
| charlotte_freezing_point | 1 | 3 dmg + draw 1, cryo apply | **5 / 8 / 12** | Light dmg + cantrip + apply — 3 jobs at 1 cost |
| barbara_melody | 1 | 4 block + burst 4 | **4–6 / 4–6 / 4–6** | Flat buffer, no application. 4 v/e for non-Burst chars |
| bennett_passion | 1 | +4 next atk + burst 5 | **4–6.5 / — / —** | Flat buffer, no application |
| charlotte_enduring_frosthelm | 1 | 3 block + 3 block next turn | **6 / 6 / 6** | Honest flat sustain, no conditionality |
| lynette_box_trick | 1 | draw 2 | **4 / 4 / 4** | Pure velocity glue; deliberately plain |
| lynette_enigmatic_feint | 1 | swirl + 3 block | **3 / 6 / 9** | Swirl worth 0 with no live aura |
| chevreuse_vanguards_valor | 1 | +3 next atk, +3 more if reacted | **3 / 4.5 / 6** | Conditional on a reaction this turn |
| sucrose_gust | 1 | swirl + draw 1 | **2 / 5 / 8** | Double-thin at floor: swirl 0 + draw only |

**Common floor midpoint ≈ 4–5.** **Common expected midpoint ≈ 6–7.**

### 3.2 Companion uncommons (4-star, uncommon)

| Card | Cost | Body | Floor / Exp / Ceiling | Notes |
|---|---|---|---|---|
| charlotte_snappy_silhouette | 1 | Vuln 2 + draw 1 | **8 / 8 / 8** | Strong, *non*-conditional; no application |
| dahlia_favonian_favor | 1 | 5 block + hydro apply | **5 / 9 / 13** | Uncommon body at 1 cost |
| fischl_oz ⚙ | 1 | power: 3×(3 dmg + electro) | **9 / ~18 / 27+** | Engine — see §3.4; strong outlier |
| freminet_shattering_pressure ⚙ | 1 | power: Shatters +4 | **0 / 8 / 16** | Pure payoff; 0 without a freeze chain |
| freminet_pressurized_floe | 2 | 8 dmg + 4 block (no elem) | **6 / 7.5 / 9** | +Shatter 6 vs frozen target |
| bennett_fantastic_voyage | 2 | 4 block + atk_up_this_turn 3 | **5 / 5 / 5** | Flat buffer |
| barbara_shining_idol | 2 | 5 block + hydro apply + draw 1 | **3.5 / 5 / 6.5** | Costed at 2 — thin per-energy |
| chevreuse_bursting_grenades | 2 | 7 AoE, pyro apply | **3.5 / 6 / 10+** | 3.5 single / 10.5 at 3 targets; mass-Vaporize ceiling |
| lynette_astonishing_shift | 2 | swirl + 4 AoE (no elem) | **2 / 4 / 6+** | Low single-target floor; swarm/aura upside |
| sucrose_astable | 2 | swirl + burst 8 | **0–2 / 2 / 5** | **Weakest card in the pool — see §5** |
| prune_witch_hunt (Klee only) | 1 | swirl-all + spark 1 | **2 / 6 / 10** | Personal-pool; Klee patch card |

**Uncommon floor midpoint ≈ 4–5** (dragged down by the 0-floor conditional/engine cards). **Uncommon expected midpoint ≈ 6–8.**

### 3.3 Companion rares (5-star, one card each) — see §3.4 for engine ratings

| Card | Cost | Body | Rating |
|---|---|---|---|
| nicole_celestial_gift ⚙ | 2 | power: your attacks +2, +4 block/turn | Strong flat engine; no conditionality; clears rare bar |
| durin_witchs_flame ⚙ | 2 | power: reactions +30%, 4 dmg + pyro/turn | Reaction *payoff* rare; strong ceiling, real floor (4 dmg/turn) |
| albedo_solar_isotoma ⚙ | 1 | power: 3 turns, block on attacks vs aura'd enemy | **Floor 0**, ceiling 9–15 block; conditional defensive engine |

### 3.4 Power engines (amortized per-fight, ~5-turn window)

| Power | Floor (no reaction) | Ceiling (reaction deck) | Verdict |
|---|---|---|---|
| fischl_oz | 9 dmg + 3 electro apps over 3 turns | +3 reactions (~18–24) → ~27–33 total value @ 1 cost | **Strong outlier** — arguably hot for enabler-not-carry, but it is a fixed 3-turn engine (no self-scaling), so within Guardrail 3. Watchlist. |
| durin_witchs_flame | ~4 dmg/turn pyro (permanent) | +30% on every amplifying reaction, permanent | Correct rare payoff. Floor is real, not zero. |
| nicole_celestial_gift | +2/attack + 4 block/turn, permanent | same (no application component) | Correct rare buffer. Flat, safe. |
| albedo_solar_isotoma | **0** (needs aura'd enemies to hit) | 3 block/hit × 3 turns ≈ 9–15 block | Correctly a conditional support rare. Fine. |

---

## 4. Side-by-side comparison vs. the hypothesized ordering

Hypothesis: `companion commons < colorless commons < companion uncommons < colorless uncommons < rares (≈)`.

| Rarity band | Companion **floor** | Companion **expected** | Base colorless (StS1) |
|---|---|---|---|
| Common | ~4–5 | ~6–7 | ~7 |
| Uncommon | ~4–5 | ~6–8 | ~10 |
| Rare | engine (0–9 floor) | engine (strong) | payoff (Ritual Dagger 15+) |

**Testing the chain at the FLOOR (naive static score):**
- companion commons (4–5) < colorless commons (7) ✓
- colorless commons (7) < companion uncommons (4–5) ✗ **FAILS** — at floor, companion uncommons are dragged *below* colorless commons by the 0-floor conditional cards (`sucrose_astable`, `freminet_shattering_pressure`, swirl triggers).
- → At the floor the hypothesis breaks and the pool looks weak. **This is exactly the false-negative the method warned about.**

**Testing the chain at EXPECTED value (conditional-aware):**
- companion commons (6–7) ≈/just under colorless commons (7) ✓ (at the bar)
- colorless commons (7) < companion uncommons (6–8) ✓ (roughly holds; overlapping)
- companion uncommons (6–8) < colorless uncommons (10) ✓
- rares ≈ (both payoff-grade; companion rares are support-shaped engines, colorless rares are self-scaling payoffs — comparable in power, different in kind) ✓

**Verdict on the ordering: it holds at expected value and breaks only at the floor.** That is the *designed* signature of reaction fuel — low static value, high conditional value — not an accident. The appliers specifically **exceed the colorless uncommon bar at their ceiling (10–13 > 10)**, which is the strongest single piece of evidence that the pool is not trash: its enablers are *above* premium-splash rate the moment they do their job.

**Two structural caveats that qualify the whole comparison:**

1. **Companion rarity ≠ power tier.** Companion "common/uncommon" encodes Genshin **star-rank and kit-depth** (principles §4.2: "4-star cards may have multiple cards... Bennett's Skill as a common, Bennett's Burst as an uncommon"), *not* a power rung the way colorless rarity does. Several 4-star *uncommons* (`barbara_shining_idol`, `bennett_fantastic_voyage`) intentionally carry common-grade bodies. So "companion uncommon vs colorless uncommon" is partly a category error — the mod does not promise companion-uncommon = colorless-uncommon power. This *softens* the "uncommons underperform" finding: they underperform a bar they were never costed to hit.

2. **The reward-pool rarity odds still route around it.** `constants.RARITY_ODDS = {common .60, uncommon .35, rare .05}` and `rewards.py` roll companion rarity on the *same* table — so the practical value a player sees is dominated by the common band (appliers), whose expected value sits right at the colorless-common bar. The pool is healthiest exactly where it is drawn most.

---

## 5. Outliers & recommendations

### Genuinely undercosted — consider a buff (1 card)

- **`sucrose_astable`** (Sucrose — Astable Anemohypostasis; 2-cost uncommon: swirl + burst_energy 8). This is the pool's weakest card by a clear margin. It is **double-conditional**: swirl is worth 0 without a *pre-existing* aura, and burst_energy 8 is worth ~0 to any character without a Burst meter. Floor ≈ 0–2, ceiling only ~5 *at 2 cost*. Even the compact common `sucrose_gust` (swirl + draw 1 @ 1 cost) strictly dominates it for most decks because draw is unconditional and it costs half as much.
  - **Recommendation:** either drop it to 1 cost, or swap burst_energy for an unconditional body (e.g., draw 1 or block 4) so its floor isn't near-zero for non-Burst characters. **Verify in-context first:** for Klee/Furina (who *do* have Burst meters), burst_energy 8 is not dead — measure its actual pilot value before changing it. Flag, don't reflexively buff.

### Looks weak statically but is correctly-costed conditional fuel — leave alone

- **All 1-cost appliers** (`dahlia_sacramental_shower`, `fischl_nightrider`, `kaeya_frostgnaw`, `chevreuse_interdiction_fire`, `freminet_pers_deploy`, `charlotte_freezing_point`): floor 4–5 (below the colorless-common bar) but ceiling 10–13 (above the colorless-*uncommon* bar). This spread *is* the enabler-not-carry design. Do not raise their floors — doing so would make them carries.
- **`freminet_shattering_pressure`** (floor 0): a payoff power that is 0 without the freeze chain it pays off. Self-sufficient inside Freminet's own 3-card kit (Pers freezes → Backstroke shatters → this pays). Correctly-costed conditional payoff.
- **`albedo_solar_isotoma`** (floor 0): a rare support engine that is correctly worthless without auras to trigger on. Right by design.
- **Swirl triggers** (`lynette_enigmatic_feint`, `lynette_astonishing_shift`, `sucrose_gust`, `prune_witch_hunt`): low floors because Swirl needs a live aura; that is the honest cost of a multiplier card. `sucrose_gust`'s floor of 2 is thin but it is a *common* and always cantrips.

### Outliers on the STRONG side — watchlist, not buff

- **`fischl_oz`** (uncommon engine, floor 9 / ceiling 27+): the strongest per-energy card in the 4-star tier. It is a fixed 3-turn engine (no self-scaling, so still inside Guardrail 3), but it clears the colorless-uncommon bar even at floor and should be watched for over-performance in the sim, not buffed.
- **`charlotte_snappy_silhouette`** (uncommon, 8 v/e, unconditional): a strong honest uncommon — Vuln 2 + cantrip at 1 cost with no downside. Fine, but it is the ceiling of what a 4-star uncommon should be; do not let future cards drift above it.

### Fine as-is (flat glue, not conditional)

`barbara_melody`, `bennett_passion`, `charlotte_enduring_frosthelm`, `lynette_box_trick`, `bennett_fantastic_voyage`, `nicole_celestial_gift`, `durin_witchs_flame` — flat buffers/velocity/engines sitting at the enabler-not-carry grade by intent. `barbara_shining_idol` and `bennett_fantastic_voyage` are on the low side per-energy for uncommons, but that is the star-rank≠power-tier effect (§4 caveat 1), not a defect.

---

## 6. Caveats & what to verify

1. **StS1-vs-StS2 sourcing (the study's biggest hole).** The entire base-colorless reference band in §2 is anchored on **StS1** cards, because no colorless data exists in the repo and StS1 is the convention the design docs reference. **StS2 is early-access; its colorless pool composition and numbers differ and are patch-volatile.** The real bar the companion pool must clear is the *StS2* one. **Action for the user:** pull the current StS2 colorless card list (common/uncommon/rare, costs, effects) and re-derive the band; if StS2 colorless is *cheaper/weaker* than StS1 (plausible — MegaCrit rebalanced aggressively), the companion pool clears the bar even more comfortably and even `sucrose_astable` may be fine.

2. **Value-per-energy is a poor metric for both pools' cheap cards.** A large fraction of colorless cards (and several companions) are 0-cost or utility-shaped, where v/e is undefined or misleading. The bands in §2 and §3 are drawn only from body-bearing costed cards; the utility subset is compared qualitatively, not numerically. A firmer conclusion on the utility cards would need in-sim win-contribution data, not a rubric.

3. **Companion rarity is not a power tier** (§4 caveat 1). Any rarity-label-to-rarity-label comparison inherits this. The cleanest test is *expected value within the reward-odds-weighted mix*, which this study approximates but does not simulate.

4. **My reaction-ceiling credits are rubric estimates, not sim measurements.** They are derived from the constants (`VAPORIZE_MULT`, `OVERLOAD_SPLASH`, etc.) but assume a "reasonable" payoff-hit size and a ~50% expected fire-rate. The project has a live simulator (`tier05`, reaction damage-share metrics) that could replace these estimates with measured per-card win-contribution. If a firm buff decision on `sucrose_astable` is wanted, run it through the sim rather than trusting the rubric.

5. **Powers were amortized over a ~5-turn window.** Longer fights (TANK BOSS, GAUNTLET) make the permanent engines (`nicole`, `durin`, `fischl_oz`) worth proportionally more; shorter fights less. The rare-tier "roughly equal" verdict is fight-length-sensitive.

6. **Guest-star and personal-pool cards are gated.** The Neuvillette guest-stars (`fontaine-companions.yaml`) are personal-pool, this-combat-only, generator-gated (`rewards.py::companion_pool` excludes `guest_star`); `prune_witch_hunt` is Klee-only. They were scored for completeness but do not sit in the shared reward band the hypothesis is about.

---

## Appendix — Companion inventory scored

31 companion rows total: 16 in `mondstadt-companions.yaml` (12 shared 4-star + 3 five-star rare + 1 Klee personal), 15 in `fontaine-companions.yaml` (12 shared 4-star + 3 Neuvillette guest-star). All companion cards live only in these two files (confirmed: `role_c:` appears in no other sheet; `loader.py` derives `is_companion` from the `-companions.yaml` filename). No companion rows exist in `klee-cards.yaml` or `furina-cards.yaml` — those files only *reference* companions via `copy_companion` / `cost_mod: companion_cards` ops.
