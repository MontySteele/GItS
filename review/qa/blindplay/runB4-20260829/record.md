# Blind play session `runB4-20260829`

**R217 G — subjective feedback from an independent model playing the real game. Useful for iteration; not human validation, not balance evidence, not approval. It never enters an Understudy report, a win-rate table or a measurement register.**

## Identity

- **model_requested**: gpt-5.6-sol
- **model_observed**: gpt-5.6-sol
- **codex_version**: codex-cli 0.150.1
- **build_version**: (not read)
- **build_version_source**: the bridge's health payload carries no version
- **run_seed**: JM3TY7NL4G6T
- **prompt_sha256**: 508a4298178289d1ba8deca05a40fa793662eac2ff3b35efd2cbcecef62ef2eb
- **actions**: 30
- **termination**: observation_leak

- **guardrail**: you are playing the real game through a tool that shows you only what the screen prints; nothing recorded here is a measurement, a comparison with any other run, or a judgement of whether the game is fun or good that anyone will treat as approval

## Fight 1, in the tester's own words

1. I used Water’s Edge on the attacking Toadpole, then played Bake-Kurage and Coral Guard to combine delayed damage with defense. When Nereid’s Ascension appeared, I used its area damage to put both enemies at 4 HP, killed the non-Thorns attacker first, and later finished the survivor with the free Gorou attack.

2. I seriously considered attacking again instead of playing Coral Guard. That would have dealt 6 more damage, but it would also have given up 5 Block and cost another 2 HP to Thorns while 9 damage was incoming.

3. Yes. If the second Toadpole had attacked instead of buffing early, I would have valued defense more. A timely attack after Nereid’s Ascension—or a playable card in the unexpectedly empty round-four hand—would also have ended the fight much sooner.

4. Nereid’s Ascension was automatic because 12 damage to both enemies was far stronger than the alternatives. Coral Guard was automatic against the multi-hit intent, and Gorou was automatic as a free lethal hit. Water’s Edge became temporarily dead whenever I lacked energy, while Tactical Retreat was mostly speculative cycling and failed to find a usable zero-cost card when it mattered.

5. The initial plan was to control incoming damage while Bake-Kurage supplied efficient delayed damage. It changed when Nereid’s Ascension reduced both enemies to 4 HP: from there, the plan became removing one attacker immediately and finding any cheap hit for the other.

6. The duplicate enemy names made targeting ambiguous; I had to infer that the first matching Toadpole would be selected. Turn flow was also confusing: after ending round three, the screen still showed the same round with an empty hand and required another end-turn command, and round four then presented energy but no cards before jumping to round six.

## The run, in the tester's own words

1. The character seems to build Charge and convert it into stronger delayed or area damage. Bake-Kurage is the clearest engine: it gains Charge and then pulses for increasingly large damage, while Nereid’s Ascension gets a smaller Charge bonus and Hydro provides a separate reaction setup that I never fully explored.

2. The recurring tension was spending energy on defense versus building Charge and ending fights faster. Low health made Coral Guard important, but blocking slowed damage setup; Thorns also made ordinary attacks costly. A second, unintended tension was whether ending a turn would draw cards or simply expose me to another attack.

3. Bake-Kurage and Nereid’s Ascension defined the successful fight. Bake-Kurage offered efficient delayed scaling, and Nereid’s Ascension nearly cleared two enemies at once. Coral Guard repeatedly kept damage manageable. Ritual Purification looked like the natural Charge enabler, but playing it at 4 HP immediately ended the run, so I never saw its promised payoff.

4. Play became repetitive when empty-hand screens forced repeated end-turn commands despite having full energy. Tactical Retreat also became a routine desperation play whenever energy was gone, usually without changing the turn. The indistinguishable shop inventory added another stalled moment because every item was printed as “(unnamed)” but that name was rejected.

5. I would avoid Ritual Purification until its exhaust behavior is clearer. I drafted it for the strong 4 Charge gain and expected it to consume another card in hand, but using it ended the run without showing an intermediate choice or explanation. I would also avoid extra cycling like Tactical Retreat unless the deck had meaningful zero-cost draws, because it rarely produced a playable result.

## Leak audit

Every observation the tester was actually shown — `turn-*/prompt.md`, the exact bytes handed to `codex exec` — scanned against `qa_packet.FORBIDDEN` plus the pilot-vocabulary rules and this run's seed.

- **observations scanned**: 33
- **total hits**: 1

| rule | hits |
|---|---|
| `pilot-vocabulary-score` | 1 |

Offenders (first 40):

- `turn-001` — `pilot-vocabulary-score` matched `score` in: guide, no card list, no score, no recommendation, and no way to ask for one.
