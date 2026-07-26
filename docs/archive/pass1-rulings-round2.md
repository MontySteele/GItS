# Pass-1 Rulings — Round 2 Handoff

From chat-Claude. I pulled b727cd, read `klee-pass-1-report.md`, and **ran the ruling candidates empirically through your harness before ruling** (my working copy has local experiments; the canonical amended sheet ships with this note as `klee-cards.yaml` v0.2 — diff it against docs/, seven number shaves + three stack-cap fields). Excellent pass — the baseline-pilot pinning bug catch especially, and going past ruling #4 to implement the companion trio was the right call.

## Ruling 1 — A4: redefine as healing/recovery. Stop measuring chip.
I prototyped both candidate metrics from your CSVs: proportional-per-turn on pressure encounters (Klee starter 2.9 vs declared 1.5) and fights-until-dead = maxHP ÷ avg pressure-fight loss with deaths at 1.25×maxHP (Klee 3.8 — *inverted*, she outlasts starter Ironclad). Three formulations agree: **kill-speed leaks into every HP-delta metric because it is genuinely defensive**, and a fast character cannot read as fragile at fight level. So:
- **A4_raw = healing done per fight (+ maxHP gained).** That's what "sustain" names. Chip-avoidance already belongs to A3 ("damage prevented"), speed to A1. Current A4 triple-counts speed.
- **Anchor fix required:** REF_IRONCLAD gains a Burning-Blood hook (heal 6 after each won fight) — makes the reference faithful AND gives A4 a nonzero baseline. Floor scores at 0.5 for zero-healing configs.
- **Canonical probe:** add a `barbara_injection` Klee config (companions incl. Barbara cards at draft rates); it should visibly raise A4. This doubles as the companion-sustain-patching validation.
- Fragility's real signal is the pressure-winrate delta — keep printing it; the design doc now points there. Klee's declared A4 is revised to "~0.5 by construction."

## Ruling 2 — A6: baseline-anchor both terms.
Self-relative AoE was my spec error. New: `A6_aoe_raw = config swarm DPT ÷ baseline swarm DPT`, `A6_debuff_raw = debuff stacks applied/fight ÷ baseline` (weak+vuln), composite 0.7/0.3, both baseline-relative like every other axis. Expected: Klee configs move from 1.7 to ≥4 (her swarm DPT ~21 vs starter baseline), Silent stays low. Sanity anchors: Silent < Ironclad-package < Klee on the AoE term.

## Ruling 3 — A2: three-part fix, empirically sequenced.
1. **Early window 1–3 → 2–4** (I tested this in your axes.py, then reverted): demolition 5.1→4.5 while Silent only 5.2→5.0 and Ironclad-package lands 3.5 — kills the bomb-lag artifact, keeps Silent on top, sane ordering. Adopt; A2-only recalibration, battery stays frozen.
2. **Number shaves are near-inelastic for A2** — measured: −1 on all three scaling powers moved the exponent 0.40→0.27 but the score ~0.0. A further −1 wave moved A2 nothing while dropping A1 by 0.3 (wrong axis) — reverted. Don't tune A2 with flat numbers again.
3. **The structural lever is stack caps** (in sheet v0.2, needs engine support: `max_stacks` on apply_power): bomb_damage_up ≤4, zero_cost_attacks_up ≤4, bomb_and_spark_per_turn unique (≤1). Per-turn compounding powers are the exponent source; caps flatten the tail. Predicted: demolition exponent <0.15, A2 ≤4.0 under the new window. If it still exceeds 4.0, next knob is Playtime Forever's bomb size (5→4), NOT commons.
4. **Declaration revised** (design doc updated): A2 ≤4.0 solo with a hard identity constraint **A1 > A2 in every Klee config** — her curve never tops her frontload. Add that as a per-character assertion the scorecard flags.

## Ruling 4 — A3/spark: partial acceptance, one experiment.
The four rider shaves (v0.2) moved spark A3 only 4.4→4.1; the residual driver is structural — free attacks create energy surplus that buys block, which is real archetype texture, not a bug. Revised acceptance: **spark deck A3 ≤3.5, all other Klee configs ≤2.5.** To get there: skip_and_hop is the only 0-cost block rider — experiment with making its block conditional ("gain 2 Block only if an enemy intends to attack") and measure; if that lands ≤3.5, stop. "Reluctant defense" survives as: her block is cheap but small, conditional, and never scales.

## Ruling 5 — Burst Retain: YES, mod-wide.
Principles doc amended (v1.4, §2.4): **Burst cards have Retain.** Faithful (a charged burst doesn't evaporate at end of turn) and it resolves the discard-rhythm collision you identified. Implement Retain as a card property in the sim; acceptance: Sparks 'n' Splash cast rate in reaction decks goes from ~never to majority-of-fights-that-reach-full-meter.

## Pass-2 acceptance targets (supersedes review #8)
Under new metrics + sheet v0.2 + stack caps: A1 4.0–4.7 and strictly > A2; A2 ≤4.0; A3 ≤2.5 (spark ≤3.5); A4 ≈0.5 solo, rises under barbara_injection; A6 ≥3.5; TOO_STRONG flags should clear for demolition (A4-driven flags disappear with ruling 1; if a config still flags, that's real). Also please implement `pilot_regret` this pass — two rulings above leaned on "pilot suspect first" reasoning and I want the instrument, not the assumption. Tank_boss winrates for archetype decks should land in the 78–93% Ironclad-package band after all of the above; if they're still ~98%, arm the global common-attack −1 shave and run it past me first.
