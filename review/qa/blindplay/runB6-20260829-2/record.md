# Blind play session `runB6-20260829-2`

**R217 G — subjective feedback from an independent model playing the real game. Useful for iteration; not human validation, not balance evidence, not approval. It never enters an Understudy report, a win-rate table or a measurement register.**

## Identity

- **model_requested**: gpt-5.6-sol
- **model_observed**: gpt-5.6-sol
- **codex_version**: codex-cli 0.150.1
- **build_version**: 0.2.1269
- **build_version_source**: the deployed `mods\klee\manifest.json` `version`
- **game_version**: v0.111.0
- **game_version_source**: the game's own `release_info.json` `version`
- **run_seed**: ZZRK9QHXEFCS
- **prompt_sha256**: 508a4298178289d1ba8deca05a40fa793662eac2ff3b35efd2cbcecef62ef2eb
- **actions**: 85
- **termination**: refusal_limit

- **guardrail**: you are playing the real game through a tool that shows you only what the screen prints; nothing recorded here is a measurement, a comparison with any other run, or a judgement of whether the game is fun or good that anyone will treat as approval

## Fight 1, in the tester's own words

1. I built Charge with Bake-Kurage, used Water’s Edge to focus the weakened slug, and relied on the end-turn pulse for efficient damage. Once only one slug remained at low HP, I finished it with Water’s Edge before its 7x2 attack.

2. I seriously considered spending more energy on Coral Guard and splitting damage between the slugs. That would have reduced immediate health loss, but given up kill pressure and made the random Bake-Kurage pulse less decisive.

3. A more defensive enemy intent would have pushed me further toward attacks and Charge generation; heavier attacks would have made Coral Guard more important. A different draw containing enough direct damage to secure a kill would also have replaced the pulse-dependent line.

4. Bake-Kurage became nearly automatic because each use increased both current and future pulse damage. Water’s Edge was the automatic finisher. Coral Guard was mostly dead when enemies were debuffing, and Tactical Retreat did little when its random discard erased the value of its draw.

5. My plan shifted from balancing defense and setup to racing one slug down. I briefly thought two Water’s Edge attacks would kill the 7-HP slug, then corrected the arithmetic after it survived at 1 HP and had to let the random pulse resolve the turn.

6. The two enemies had identical printed names, so targeting did not clearly communicate which slug would be selected. The transition into another empty “Battle — round 0” screen after the kill also looked like a new fight rather than a victory transition.

## Fight 2, in the tester's own words

1. I used Bake-Kurage for Thorns-safe damage, focused the more immediate attacker, and used free or efficient Block to preserve my low HP. After killing the first Toadpole, I defended through the second one’s multi-hit turn, established Metallicize, then let a 13-damage pulse finish it.

2. I considered attacking more aggressively through Thorns instead of playing two Coral Guards. That would have shortened the fight, but it would have traded away scarce HP for only 6 damage per attack, so full defense looked safer.

3. Yes. Buff or non-attacking intents made Bake-Kurage and attacks preferable, while 3x3 attacks made Block much stronger. Drawing Tactical Retreat alongside Shinobu also mattered: the cycle found 4 free Block, saving health that I otherwise would have lost.

4. Bake-Kurage became automatic because its pulse avoided Thorns and scaled with Charge. Shinobu and the zero-cost Gorou attack were also automatic. Coral Guard was valuable against multi-hit attacks but dead once existing Block covered the intent; Water’s Edge became unattractive whenever Thorns was active.

5. I began by racing down the first attacker despite Thorns, then changed to preservation once HP reached 23. The turning point was the round where two Coral Guards fully covered 3x3; after that, Metallicize stabilized defense and I waited for Bake-Kurage to end the fight safely.

6. The Toadpole’s Thorns appeared on some rounds and disappeared on others without an explanation of whether it had expired, transformed, or belonged to a particular state. The recurring empty “Battle — round 0” victory screen was again confusing, and Gorou’s free attack granting Charge and Burst was not explained in its displayed rules text.

## The run, in the tester's own words

1. The character seems to bank Charge through Hydro-themed attacks, Bake-Kurage, and Companions, then convert it into increasingly large end-turn jellyfish pulses. Burst Energy accumulated alongside that plan, although I never saw how to spend it. The supporting package uses Block, Metallicize, and eventually Kurage’s Oath to survive while Charge scales.

2. The recurring tension was spending limited energy on immediate Block versus advancing Charge and damage. Low HP made that especially sharp: defensive turns preserved the run but delayed the 70-HP stun threshold against the Terror Eel, while aggressive turns risked being punished by large intents or Thorns.

3. Bake-Kurage defined the run because it provided scaling, non-attack damage and, after Kurage’s Oath, defense. Pulsing Current was the cleanest attack because it also generated Charge. Gorou — Forward Unto Victory provided important long-fight stability, while Shinobu’s free Block repeatedly rescued otherwise awkward turns.

4. Play became repetitive when hands reduced to Water’s Edge versus Coral Guard: calculate the displayed attack, block as much as needed, and spend anything left on the same basic attack. Bake-Kurage turns were more distinctive, but waiting to redraw it during the Elite fight made the basic attack-and-block loop prominent.

5. I would avoid Distraction and probably A Moment Alone next time because random or discard-based hand manipulation was hard to value against reliable cards, especially with only three energy. I would also avoid adding more ordinary one-turn Block unless the deck lacked defense; Metallicize, free Shinobu, and Kurage’s Oath offered better efficiency. The final screen was also mechanically confusing: the game said identically titled Water’s Edge copies required an upgraded/not-upgraded suffix, then said the Sharp-enchanted copy was not upgraded, leaving no visible way to select the 8-damage version before the run ended.

## Leak audit

Every observation the tester was actually shown — `turn-*/prompt.md`, the exact bytes handed to `codex exec` — scanned against `qa_packet.FORBIDDEN` plus the pilot-vocabulary rules and this run's seed.

- **observations scanned**: 91
- **total hits**: 1

| rule | hits |
|---|---|
| `pilot-vocabulary-score` | 1 |

Offenders (first 40):

- `turn-001` — `pilot-vocabulary-score` matched `score` in: guide, no card list, no score, no recommendation, and no way to ask for one.
