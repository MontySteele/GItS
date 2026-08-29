# Blind play session `runB3-20260829`

**R217 G — subjective feedback from an independent model playing the real game. Useful for iteration; not human validation, not balance evidence, not approval. It never enters an Understudy report, a win-rate table or a measurement register.**

## Identity

- **model_requested**: gpt-5.6-sol
- **model_observed**: gpt-5.6-sol
- **codex_version**: codex-cli 0.150.1
- **build_version**: (not read)
- **build_version_source**: the bridge's health payload carries no version
- **run_seed**: JFK05UXUAYK9
- **prompt_sha256**: 508a4298178289d1ba8deca05a40fa793662eac2ff3b35efd2cbcecef62ef2eb
- **actions**: 50
- **termination**: run_over

- **guardrail**: you are playing the real game through a tool that shows you only what the screen prints; nothing recorded here is a measurement, a comparison with any other run, or a judgement of whether the game is fun or good that anyone will treat as approval

## Fight 1, in the tester's own words

1. I used the enemy’s buff turns as damage windows: Tactical Retreat found attacks, Bake-Kurage established Charge and an end-turn pulse, and repeated Water’s Edge attacks maintained Hydro. On the dangerous multi-hit turn, I attacked once and then spent everything else to reach 14 Block.

2. I considered playing more defensively earlier, including using Grass Ring on the buff turn, but that Block would have expired without stopping damage and would have given up useful deck cycling. On the multi-hit turn, I also considered skipping the 9-damage attack for defense, but I could already play every Block card afterward.

3. Yes. An attack intent on the Bake-Kurage turn would have made defense more important, while an elemental attack drawn into the existing Hydro aura might have made a reaction the best damage line. A stronger offensive draw could also have produced lethal before the multi-hit attack.

4. Water’s Edge became automatic on safe turns, and every available Block card became automatic against the 3x4 attack. Grass Ring was effectively dead against buff intents, while Tactical Retreat was valuable when it could refill the sparse hand.

5. The plan changed after the early empty-hand turns cost substantial health. I shifted from simply advancing combat to maximizing damage during the next buff window, then briefly switched to survival when the strengthened multi-hit attack appeared before returning to lethal damage.

6. The transition and timing were confusing. The fight began with empty hands, rounds appeared to jump from 1 to 3 and later to 5, and ending a turn sometimes left me on the same displayed round with an empty hand. It was also unclear whether the shown 3x4 intent already included Strength, though 14 Block ultimately prevented all damage.

## Fight 2, in the tester's own words

1. I used Liquid Bronze immediately because 17 HP made every future attack dangerous. I then paired Bake-Kurage with enough Block to cover each intent, using Water’s Edge only when the remaining cards could still prevent the shown damage.

2. I seriously considered spending more energy on attacks instead of defense. That would have accelerated the kill, but it would have surrendered health I could not safely spare, especially after entering the fight already badly injured.

3. Yes. A buff or non-attacking intent would have let me spend all three energy on damage and setup. Drawing Raiden against an enemy with Hydro would also have changed everything, since its large Electro hit looked capable of ending the fight immediately.

4. Coral Guard and Grass Ring became automatic whenever the enemy attacked because survival was the constraint. Bake-Kurage was also close to automatic because it produced damage while leaving energy for defense. Water’s Edge became dead whenever playing it would prevent full blocking, and Raiden never appeared.

5. The plan began as cautious attrition with Thorns and Block. Once Bake-Kurage+ appeared at 9 HP, I shifted toward ending the fight through repeated pulses while still overblocking every attack.

6. The timing remained confusing: setup rounds were skipped, resolving an end turn required a second end-turn command, and the fight ended while the enemy was still displayed at 16 HP. Bake-Kurage also showed a formula implying 10 damage at 2 Charge but dealt 7 while Weak was active, even though Weak’s text specifically said attacks deal less damage; it was unclear whether the pulse counted as an attack or whether another modifier was involved.

## The run, in the tester's own words

1. The character seemed built around applying Hydro, accumulating Charge through companion cards, and turning that Charge into recurring Bake-Kurage damage. Other elements can consume Hydro for reactions, while Burst Energy appears to support a payoff I never got to see.

2. The repeated tension was damage versus survival. Low health and frequent attack intents forced me to decide whether to spend energy on Water’s Edge or reserve it for Coral Guard, while Bake-Kurage was valuable because it advanced offense without consuming the whole turn.

3. Bake-Kurage and Coral Guard defined actual play: one supplied recurring damage and scaling, while the other kept me alive. Grass Ring was an excellent free defensive supplement. Raiden looked like the intended explosive Hydro-reaction finisher, but I never drew it, so it defined the deck more as an unrealized plan than an experienced card.

4. Play became repetitive when attack turns repeatedly reduced to playing every available Block card, ending the turn, then issuing another end-turn command after the pulse resolved. The repeated Water’s Edge sequence on safe turns also became automatic quickly.

5. I would avoid drafting another expensive payoff like Raiden unless the deck had better draw control or more energy. Its ceiling looked enormous, but it never reached my hand during the final fight, and at critically low health a three-cost attack could have crowded out necessary defense. I would favor efficient draw, reliable Block, or cards that build Charge while defending.

## Leak audit

Every observation the tester was actually shown — `turn-*/prompt.md`, the exact bytes handed to `codex exec` — scanned against `qa_packet.FORBIDDEN` plus the pilot-vocabulary rules and this run's seed.

- **observations scanned**: 54
- **total hits**: 1

| rule | hits |
|---|---|
| `pilot-vocabulary-score` | 1 |

Offenders (first 40):

- `turn-001` — `pilot-vocabulary-score` matched `score` in: guide, no card list, no score, no recommendation, and no way to ask for one.
