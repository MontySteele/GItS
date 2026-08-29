# Blind play session `runB-20260829`

**R217 G — subjective feedback from an independent model playing the real game. Useful for iteration; not human validation, not balance evidence, not approval. It never enters an Understudy report, a win-rate table or a measurement register.**

## Identity

- **model_requested**: gpt-5.6-sol
- **model_observed**: gpt-5.6-sol
- **codex_version**: codex-cli 0.150.1
- **build_version**: (not read)
- **build_version_source**: the bridge's health payload carries no version
- **run_seed**: 2QXZH3UD1JKM
- **prompt_sha256**: 508a4298178289d1ba8deca05a40fa793662eac2ff3b35efd2cbcecef62ef2eb
- **actions**: 8
- **termination**: refusal_limit

- **guardrail**: you are playing the real game through a tool that shows you only what the screen prints; nothing recorded here is a measurement, a comparison with any other run, or a judgement of whether the game is fun or good that anyone will treat as approval

## The run, in the tester's own words

1. The character seems to combine straightforward attacks and block with elemental auras such as Hydro, setting up reactions by applying a different aura later. Tactical Retreat appears to cycle the hand, though its random discard makes its value uncertain.

2. The recurring tension was survival versus making offensive progress. Low health and multi-hit attacks made blocking urgent, while spending energy defensively left the enemy untouched and able to grow stronger.

3. Coral Guard and Coral Guard+ defined the only meaningful turn because together they could cover the incoming 12 damage. Water’s Edge and Water’s Edge+ showed the likely Hydro plan, but I never got a chance to use them.

4. Play became repetitive immediately when several turns presented an empty hand despite full energy and cards moving between the draw and discard piles. I could only end turn repeatedly while taking damage, so no real decisions existed during that stretch.

5. I did not see enough draft choices to identify a card I would avoid next time. I would be cautious about Tactical Retreat because drawing one and then randomly discarding one may provide no net card advantage and can discard something important. The card-selection interface was also confusing: it said “Coral Guard+” was ambiguous, instructed me to add “(upgraded),” then rejected that exact form even though only one Coral Guard+ appeared on screen.

## Leak audit

Every observation the tester was actually shown — `turn-*/prompt.md`, the exact bytes handed to `codex exec` — scanned against `qa_packet.FORBIDDEN` plus the pilot-vocabulary rules and this run's seed.

- **observations scanned**: 12
- **total hits**: 1

| rule | hits |
|---|---|
| `pilot-vocabulary-score` | 1 |

Offenders (first 40):

- `turn-001` — `pilot-vocabulary-score` matched `score` in: guide, no card list, no score, no recommendation, and no way to ask for one.
