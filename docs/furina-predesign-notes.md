# Furina — Pre-Design Notes (+ Pass-3 Ratification Errata)

## Part 1 — ERRATA to pass-3 ratification (for Claude Code, before Tier 0.5 M5)

User review caught an ecosystem mismatch the sim cannot see (it validates internal consistency; base-game *pricing* lives outside it): base StS2's only reliable stun is an act-3 Ancient reward at 3 energy + Exhaust, and looping it is a known degenerate win condition. Our non-boss Frozen was a repeatable intent-skip at ~2 energy of common companion cards — an order of magnitude under the game's own stun pricing, and it means reaction's elite/act winrates were partly control-carried by supports ("supports freeze it while Klee does stuff" = enabler-not-carry violated on the control axis).

Ratification item 3 is therefore **partially superseded**:
- Boss ruling STANDS (Frozen→Vuln 2; the freeze-team control identity survives — it was never stun-based on bosses).
- Non-boss Frozen REDESIGNED (principles v1.5, §2.2): enemy's next action −50% damage; while Frozen, the first attack to hit it **Shatters** (bonus damage — start at 6, it's a knob — and removes Frozen). No skip at base. Full stun becomes payoff-tier design space with base-game-parity pricing and Freeze Resist diminishing returns.
- New detector: `control_uptime` (% of enemy actions negated by companion-sourced effects; SUPPORT_CARRY flag on winning fights above threshold — propose 40%, tune on first data).
- Companion errata (mondstadt-companions v0.3.1, shipped with this doc): barbara_melody and bennett_fantastic_voyage gain Exhaust, per the new healing-grade policy (Part 2 rationale). Expect the A4 barbara_injection probe to read lower; recalibrate its expectation, not the metric.
- **Directive:** re-run the reaction grid + floors under Frozen v2 before the v0.1 scorecard freezes. Predictions to check: boss 58% unchanged; elite/punisher winrates drop (that drop is the mispricing being removed, not a regression); floors (≥35 boss / ≥75 gauntlet) should hold via Shatter + Vuln routes — if gauntlet dips under 75, Shatter damage is the knob, not the stun.

## Part 2 — Furina design direction (pre-design; full doc after character kickoff)

**The healing red flag, adopted as a mod-wide law.** Any repeatable true healing hands stall/loop decks the payoff "top my HP forever." Base StS prices in-combat healing accordingly (rare, exhausting, or relic-scale trickles). Policy (principles v1.5): true in-combat healing is rare-tier or Exhausts; repeatable sustain routes through **capped buffer pools** — and Furina is where the pattern debuts.

**The Encore pool (working name).** Osty is the base-game precedent: a persistent, non-Block damage buffer that's mechanically legal in this ecosystem. Furina's version:
- Her "healing" effects grant **Encore** instead of HP: a pool that absorbs damage before HP, does not decay end-of-turn, and is **hard-capped** (~25% of max HP — the cap is the anti-stall guarantee: no unbounded banking, so stalling has no "never die" payoff).
- **Spending Encore is a cost line on her potent cards** ("Spend 4 Encore:") — sustain doubles as her mana battery, which is the interesting decision loop: every point held is safety, every point spent is tempo.
- **True HP damage is the overdraw consequence:** Salon Member summons drain HP directly when Encore is empty. Playing greedy is allowed and priced.
- **True healing exists at rare tier only** (her Pneuma/Singer identity), converting the base game's healing scarcity into her power fantasy rather than her floor.
- **Fanfare feeds on flux of both** — HP lost, Encore gained, Encore spent all tick the counter — so the drain→refill→spend cycle is the engine, and in co-op, partner HP flux counts (her Genshin identity, and the first ally-coupled mechanic on the road to Columbina).

**Anti-degeneracy audit to run at design time:** Encore cap enforcement under generation stacking; Encore-spend cards priced so spend-loops can't self-sustain (spends must exceed per-turn generation); interaction with Klee's Hot Hands-style self-damage cards in co-op Fanfare counting (probably exclude self-inflicted partner damage or Fanfare farms itself).

**Statline sketch (declare properly at kickoff):** weak frontload, strong A4-by-design at last (the healing metric finally gets a protagonist), strong utility/velocity via Salon application; archetypes: Salon (off-field Hydro engine — Klee's dream partner), Fanfare (flux-scaling buffs), Ousia/Pneuma stance duality (drain-mode/sustain-mode toggle; Downfall's Champ proves stances are buildable). Companion appetite: Standard, but with the mod's first ally-facing cards.
