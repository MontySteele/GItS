# Blind play session `runB5-20260829`

**R217 G — subjective feedback from an independent model playing the real game. Useful for iteration; not human validation, not balance evidence, not approval. It never enters an Understudy report, a win-rate table or a measurement register.**

## Identity

- **model_requested**: gpt-5.6-sol
- **model_observed**: gpt-5.6-sol
- **codex_version**: codex-cli 0.150.1
- **build_version**: (not read)
- **build_version_source**: the bridge's health payload carries no version
- **run_seed**: D0N8P3MQAJ1H
- **prompt_sha256**: 508a4298178289d1ba8deca05a40fa793662eac2ff3b35efd2cbcecef62ef2eb
- **actions**: 37
- **termination**: run_over

- **guardrail**: you are playing the real game through a tool that shows you only what the screen prints; nothing recorded here is a measurement, a comparison with any other run, or a judgement of whether the game is fun or good that anyone will treat as approval

## Fight 1, in the tester's own words

1. I used Tactical Retreat immediately, then spent all three attacks to kill the small attacking slime and soften the other small slime. Afterward I leaned on Bake-Kurage to build Charge and deal large end-of-turn pulses, using Sayu and Coral Guard to reduce the biggest incoming hits.

2. I seriously considered blocking more heavily instead of attacking on the first turn, and later using two Coral Guards rather than Sayu. Those lines would have saved a little health immediately, but given up faster enemy removal or Sayu’s delayed Block.

3. Yes. If the large slime had not been attacking for 11, I would have favored damage and Charge even more aggressively. A different draw—especially an attack when it had 9 HP—would also have ended the fight sooner; the empty-hand turns forced me to absorb avoidable damage.

4. Bake-Kurage became nearly automatic because each copy increased Charge and produced a stronger pulse. Sayu was usually preferable to Coral Guard when I could afford a little current damage. Coral Guard was never completely dead, but extra copies became dead once energy ran out; Water’s Edge also became unnecessary when a pulse already guaranteed lethal.

5. The plan shifted after the first Bake-Kurage showed how strongly its damage scaled with banked Charge. I stopped treating the fight as ordinary attack-and-block sequencing and instead built around surviving until increasingly large jellyfish pulses ended it.

6. The transition after pressing end turn was confusing: the pulse resolved on a separate screen, then I had to end turn again for enemy actions. Round numbers also skipped, and one round began with energy but an empty hand, so it was unclear whether drawing had failed or another transition was pending.

## Fight 2, in the tester's own words

1. I had to end the first three turns with empty hands, taking 12, then 16, then 16 damage. When cards finally appeared at 14 HP, I chose Sayu for Block because two Water’s Edges could not kill either 10-damage attacker.

2. I considered playing both Water’s Edges into the 18-HP attacker, but leaving it at 6 HP would not reduce the lethal 20 incoming damage and would give up Sayu’s 4 Block.

3. Absolutely. Any defensive cards during the first three rounds, or enough damage to kill one attacker on the last round, would have changed the line. Non-attacking intents on the final turn could also have created time to stabilize.

4. Sayu became automatic on the final screen because it was the only defensive option. Both Water’s Edges were effectively dead because neither could remove an attacker, and there was no chance to use the newly drafted Press the Advantage or the Charge/Bake-Kurage plan.

5. There was barely a plan to change: repeated empty hands prevented meaningful decisions. Once cards finally appeared, the plan shifted from simply waiting for a playable turn to minimizing otherwise unavoidable lethal damage.

6. The empty hands were very confusing. The pile counts changed each round as though cards had been drawn and discarded, but the hand stayed empty for three full rounds; that made it look like a display or turn-resolution bug rather than an intended combat state. The fight also ended immediately after playing Sayu, before the remaining actions or enemy damage were shown.

## The run, in the tester's own words

1. The character seems to build Charge with Bake-Kurage, turning later jellyfish pulses into increasingly large end-of-turn damage while accumulating Burst Energy. Hydro sets up elemental reactions, and defensive cards buy time for that scaling engine.

2. The recurring tension was immediate survival versus investing energy in Charge and future value. Sayu’s delayed Block posed the same question in miniature: accept slightly more damage now for better protection next turn.

3. Bake-Kurage defined the successful fight because its scaling pulses became the main win condition. Sayu and Coral Guard kept that plan alive, while Water’s Edge supplied straightforward damage and Hydro. Press the Advantage looked promising but never appeared in a usable hand.

4. Play became repetitive around the two-stage end-turn sequence: ending once to trigger Bake-Kurage, then ending again on an empty-hand screen to resolve enemy actions. The second fight became especially repetitive because three consecutive rounds offered no cards at all.

5. I would avoid drafting a merely incremental defensive card like Hold the Narrows unless its Muster condition proved reliable. The deck already had several basic Block cards, and this run suggested it needed dependable card access, stronger immediate enemy removal, or more copies of the Charge engine—not another modest defensive variation.

## Leak audit

Every observation the tester was actually shown — `turn-*/prompt.md`, the exact bytes handed to `codex exec` — scanned against `qa_packet.FORBIDDEN` plus the pilot-vocabulary rules and this run's seed.

- **observations scanned**: 40
- **total hits**: 1

| rule | hits |
|---|---|
| `pilot-vocabulary-score` | 1 |

Offenders (first 40):

- `turn-001` — `pilot-vocabulary-score` matched `score` in: guide, no card list, no score, no recommendation, and no way to ask for one.
