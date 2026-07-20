# Upgrade Conventions — Mined Grammar & Our Rules

**Source:** programmatic mining of all 910 card files in the Downfall StS2 codebase (which demonstrably carries base-game values — the most frequent damage pair in the corpus is 6→+3, i.e. Strike itself; Defend's 5→+3 tops block). Samples: 283 damage upgrades, 157 block, 243 power-stack, 92 cost, 62 keyword.

## The mined grammar
1. **Numbers scale by % of base, delivered as small flat deltas.** Damage: small bases (≤6) get ~+50% (flat +2–3); mid (7–11) ~+30% (+2–3); big (12+) ~+28% (+4–5). Block identical shape, slightly more generous at small bases (+57%, flat +3 dominant). Deltas are essentially always 2, 3, or 4 — never percentages, never large jumps.
2. **Power stacks: +1 at base 1–3, +2 at base 4–6.** (n=243, overwhelming.)
3. **Cost reduction is a rarity privilege.** 92 cost upgrades: 52 rare, 32 uncommon, 2 common. Always −1 (one −2 outlier on a 9-cost). Rule: commons never upgrade cost; it's the rare-tier "your payoff gets cheaper" move.
4. **Keyword upgrades are the quality class:** Add Innate (19), Add Retain (15), Remove Ethereal (13), Remove Exhaust (11). Condition-removal and downside-removal live here — mid/rare territory.
5. **Basics upgrade generously and sometimes functionally** (Strike/Defend +50%; the "third basic" gets dual bumps à la Bash, or gains a whole mode à la Hexaghost's Float).
6. **One upgrade axis per card** is the overwhelming norm; dual bumps are reserved for signature basics and rare flavor moments.

## Our derived rules (applied in klee-upgrades.yaml)
- Basics: Strike/Defend-exact (+3); Jumpy Dumpty gets the Bash-style dual bump (signature basic privilege).
- Commons: exactly one number bump per grammar row 1/2. Zero common cost reductions.
- Uncommons: number bump OR one keyword/condition change; two cost −1 slots (bombs_away, elemental_ecstasy) + one 1→0 (endless_fireworks, StS engine-power precedent).
- Rares: cost −1 or condition-soften or payoff-scale bump — their base numbers are already payoff-sized, so quality > quantity.
- Condition-class upgrades used where they ARE the card's story: hot_hands loses its self-damage, sugar_rush loses Exhaust, patched_dress's bonus goes unconditional.
- Companions: modest single bumps only — **upgraded companions must remain enabler-grade** (guardrail 3 applies to upgraded forms; deltas chosen so no upgraded companion crosses uncommon-power). Barbara's Exhaust never removes (healing policy).
- Amp-watchlist discipline: vermillion_pact upgrades 25→30 (not 35) and durin's flat ping upgrades rather than his %, keeping the amp-cap detector's margins.
- **Bursts do not upgrade in v1.** They're kit, not deck contents (v1.9), so rest-smithing can't reach them; "Talent Training" (a rest-site or event option that levels the Burst) is logged as v2 design space — pleasingly, that's literally Genshin's talent system waiting to happen.

## Directive for Tier 0.5 M7 (this is the payoff of the whole pass)
Rest nodes gain the third option: heal / remove / **upgrade** (policy chooses; upgrade valued for on-plan cards). Then re-run the assigned-vs-adaptive comparison and the hybrid discriminator **with upgrades live** — explanation 3 predicted the archetype gap exists because payoffs scale and the sim truncated scaling; this is its direct test. Predictions to check: assigned's winrate gap to adaptive narrows materially; demolition (payoff-heaviest) gains most; if the gap survives upgrades at matched deck size, explanation 2 (scorer weights) inherits the blame and gets the tuning pass.
