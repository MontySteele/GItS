# Klee Tier 0 Pass 1 — Scorecard Report

**Date:** 2026-07-19. **Input:** `klee-cards.yaml` (75 cards), `mondstadt-companions.yaml` (16), sim per `tier0-simulator-spec.md` with review rulings 1–8 applied. All 80 tests green; frozen battery untouched (A7 recalibrated per ruling #3 only).

**DSL coverage: 75/75 cards run — nothing stubbed.** All §6 ops implemented including the companion-copy trio, so Reaction rows are readable this pass (review item 7's caveat doesn't apply). One engine addition beyond §6: the review's pilot bomb-sequencing rule (attacks before placements) and early-detonation valuation.

## Scorecards (500 fights/encounter, seed 42, baseline = REF_IRONCLAD starter/generic = 3.0)

| Axis | Declared | starter | demolition | spark | reaction | dream_team |
|---|---|---|---|---|---|---|
| A1 Frontload | **4.5** | 4.2 ✓ | 4.3 ✓ | 3.6 | 4.0 ✓ | 4.1 |
| A2 Scaling | 3.0→4.0 drafted | 3.0 ✓ | **5.0 ✗** | **5.0 ✗** | 3.2 ✓ | 3.9 |
| A3 Block | **2.0** | 2.3 ✓ | 1.5 ✓ | **4.4 ✗** | 1.5 ✓ | 1.6 |
| A4 Sustain | **1.5** | **4.6 ✗** | 5.4 ✗ | 5.8 ✗ | 4.3 ✗ | 4.6 |
| A5 Velocity | 3.5 | 3.0 | 3.1 | 3.1 | 3.0 | 3.0 |
| A6 Utility | **4.0** | **1.7 ✗** | 1.7 ✗ | 1.7 ✗ | 2.5 ✗ | 2.2 |
| A7 Setup tax | 3.5 | 3.6 ✓ | 1.6 | 2.0 | 2.3 | 2.4 |

Balance heuristic: starter and reaction pass; demolition and spark flag TOO_STRONG (A2/A4 driven — see findings).

## Findings, ranked

1. **A4 metric bias (biggest miss, mostly not a card problem).** A4 = absolute avg HP delta. A fast-clearing 62-HP character takes less chip *and* caps her max loss at −62 vs Ironclad's −80, so declared-weakness 1.5 reads as 4.3–5.8. A proportional variant (Δ/maxHP) still reads ≈3.5 — her fragility genuinely expresses as **winrate cliffs under sustained pressure** (gauntlet 91–99% vs punisher 100%), not as chip. Needs a chat-side ruling: redefine A4 (candidates: Δ/maxHP; or fold loss-rate), or accept that the weakness lives in pressure winrates and read A4 accordingly.
2. **A6 under-reads AoE identity (metric artifact #2).** A6's AoE term is swarm-TTK *relative to your own* single-target TTK; Klee melts single targets too (punisher in 5 turns), so her ratio (1.25) lands below slow-but-even Ironclad (1.46). The declared 4.0 is unreachable under this definition for any all-around-fast character. Candidate fix: measure swarm TTK against the *baseline's* swarm TTK instead of self-relative.
3. **A2 solo = 5.0, declared 3.0 (real card finding).** Explosives Workshop, Spark Knight Style, Blazing Delight and friends make her *solo* scaling top-tier (demolition curve exponent +0.40, the highest measured yet — Silent's engine reads lower). "Real ceiling is draft-gated" does not hold: her personal powers carry it. If the declared identity stands, the scaling powers' numbers (bomb_damage_up 3, zero_cost_attacks_up 3) are the knob.
4. **Spark's A3 = 4.4 vs declared 2.0.** Four cheap/0-cost block+spark cards (Skip and Hop, Warm Glow, Patched Dress, Can't Catch Me) make block-per-energy excellent. If "reluctant defense" is the identity, these want costs/numbers shaved or fewer block riders.
5. **Overall power level is high but the shape is right.** Winrates ~100% vs the battery except tank_boss (starter dies like everyone; archetype decks 91–98% — vs Ironclad package's 78–93%). A1 did NOT overshoot 5 (review #8's global-shave trigger not hit).
6. **A7 sanity partially inverted vs review guess (informative, not a bug).** Demolition is her *slowest* to own-peak (raw 3.25) — bombs pay a turn late and the powers ramp; reaction is her fastest (2.34). Coherent under "when does YOUR plan come online."
7. **Burst timing observation.** The 60 meter fills reliably in reaction decks (~turn 6–8) but Sparks 'n' Splash almost never gets cast: it cycles through hand before the meter fills and StS discard sends it away for a full cycle. Genshin's "unplayable until full" fights StS's hand rhythm — recommend Burst cards get **Retain** (chat-side design ruling; trivially simulable once ruled).

## Watchlist (§7.3) — all clean

- **Melt stack** (Vermillion +25% & Durin +30% → ×2.71 melt): zero AMP_STACK flags across 900 fights; reaction damage share 12–13%. Cap holds with margin; locked by `test_amp_cap_holds_on_melt_stack`.
- **Barrage engine**: turn-8+ DPT on tank_boss is flat (≈17–23, no ramp); no SUPERLINEAR, no INFINITE. Bounded as predicted.
- **Loop density** (Playtime + Blazing Delight + Chained Reactions): max 6 cards/turn over 50 swarm fights; no flags.

## Dream team (§7.4) — structure holds

Prune+Durin+Nicole+Albedo forced: dpt 20.0, tank_boss 74% — strong, and clearly **not dominant** vs focused demolition (dpt 25.0, tank_boss 98%). No Rare nerf needed; enabler-not-carry survives contact with the sim.

## Deferred / honest gaps

- `pilot_regret` sampling (spec §6) still not implemented — the bomb-ordering fix's before/after regret comparison (review #6) couldn't be run; the fix is asserted by construction + clean detonation tests instead.
- Reaction damage share undercounts by design (amp delta + splash only; Superconduct/EC route through Vulnerable/DoT) — decision #19.
- Aura starvation in reaction_weighted: 0–2% of fights (target <15% ✓).

## Asks for chat-Claude

Rulings on findings 1, 2 (metric definitions), 3, 4 (design intent vs sheet numbers), and 7 (Retain on Burst cards).
