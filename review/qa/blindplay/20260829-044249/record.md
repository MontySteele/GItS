# Blind play session `20260829-044249`

**R217 G — subjective feedback from an independent model playing the real game. Useful for iteration; not human validation, not balance evidence, not approval. It never enters an Understudy report, a win-rate table or a measurement register.**

## Identity

- **model_requested**: gpt-5.6-sol
- **model_observed**: gpt-5.6-sol
- **codex_version**: codex-cli 0.150.1
- **build_version**: (not read)
- **build_version_source**: the bridge's health payload carries no version
- **run_seed**: YL42LN39V34T
- **prompt_sha256**: 508a4298178289d1ba8deca05a40fa793662eac2ff3b35efd2cbcecef62ef2eb
- **actions**: 30
- **termination**: max_actions

- **guardrail**: you are playing the real game through a tool that shows you only what the screen prints; nothing recorded here is a measurement, a comparison with any other run, or a judgement of whether the game is fun or good that anyone will treat as approval

## Fight 1, in the tester's own words

1. I took a damage-and-defense line: Sango Isshin for efficient damage, then Coral Guard to limit incoming hits. When Tactical Retreat found a third Water’s Edge, I switched to exact lethal and used all three copies.

2. I seriously considered spending more energy on Water’s Edge instead of blocking. That would have accelerated damage slightly but given up 5 Block each time, without reaching lethal on those turns.

3. Yes. A non-attacking intent would have made full offense preferable. A stronger defensive draw could have reduced the heavy health loss, while failing to draw the third Water’s Edge on round 7 would have forced blocking and another turn.

4. The free Shinobu — Grass Ring of Sanctification was automatic whenever drawn against an attack. Sango Isshin was the best routine damage play, and Coral Guard was usually automatic with the remaining energy. Tactical Retreat became valuable when the hand lacked lethal; no card was permanently dead, though Water’s Edge was temporarily unattractive when blocking prevented more damage than it dealt.

5. The initial plan was to trade efficiently and preserve health. After Nibbit’s Strength grew and its attack reached 16, the plan changed to finding immediate lethal; Tactical Retreat enabled that pivot.

6. The turn flow was confusing. Ending a turn first emptied the hand, then required another end-turn command to resolve the enemy action, and some rounds appeared to advance or disappear while the hand was empty. The card and intent text itself was clear.

## The run, in the tester's own words

1. The character seems built around repeatedly applying Hydro, then using a different element to trigger reactions. There are also secondary systems around Charge, Sly, Companions, and Exhaust, but this short run never developed enough support to make those plans clear.

2. The recurring tension was damage versus survival. Sango Isshin and Water’s Edge pushed toward racing the enemy, while low health and steadily increasing enemy Strength made Coral Guard and free Block difficult to pass up.

3. Sango Isshin defined the early damage plan, Coral Guard defined the defensive decisions, and Tactical Retreat enabled the decisive draw into three Water’s Edges for exact lethal. Shinobu — Grass Ring of Sanctification was an automatic free Block play. Kaeya — Frostgnaw was drafted to unlock reactions, but the run ended before it was used.

4. Play became repetitive when several turns required ending once to empty the hand and again to resolve the enemy action. The repeated Hydro attacks also became mechanically samey because no reaction card appeared during the fight.

5. Next time I would avoid speculative cards tied to unsupported mechanics, especially Charge or Sly cards whose payoff condition is not yet established. I would also hesitate to draft a narrow power like Kurage’s Oath without already having Bake-Kurage pulses. I would prioritize immediate defense, efficient draw, and a reliable off-element attack earlier.

## Leak audit

Every observation the tester was actually shown — `turn-*/prompt.md`, the exact bytes handed to `codex exec` — scanned against `qa_packet.FORBIDDEN` plus the pilot-vocabulary rules and this run's seed.

- **observations scanned**: 33
- **total hits**: 1

| rule | hits |
|---|---|
| `pilot-vocabulary-score` | 1 |

Offenders (first 40):

- `turn-001` — `pilot-vocabulary-score` matched `score` in: guide, no card list, no score, no recommendation, and no way to ask for one.
