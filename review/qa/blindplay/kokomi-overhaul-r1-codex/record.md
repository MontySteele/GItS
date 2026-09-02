# Blind play session `kokomi-overhaul-r1-codex`

**R217 G — subjective feedback from an independent model playing the real game. Useful for iteration; not human validation, not balance evidence, not approval. It never enters an Understudy report, a win-rate table or a measurement register.**

## Identity

- **model_requested**: gpt-5.6-sol
- **model_observed**: gpt-5.6-sol
- **codex_version**: codex-cli 0.150.1
- **build_version**: 0.2.1921+proto.dirty
- **build_version_source**: the deployed `mods\klee\manifest.json` `version`
- **game_version**: v0.111.0
- **game_version_source**: the game's own `release_info.json` `version`
- **run_seed**: AU4C7763TAW5
- **arms_granted**: (none)
- **arms_granted_source**: no `--arm` grant recorded against this run's seed
- **prompt_sha256**: 5dd16d9e02d6c11ae717749d2e1fd7926510f16d882d779a30557973112f7e0a
- **actions**: 80
- **termination**: max_actions

- **guardrail**: you are playing the real game through a tool that shows you only what the screen prints; nothing recorded here is a measurement, a comparison with any other run, or a judgement of whether the game is fun or good that anyone will treat as approval

- **wire snapshots**: 64 in `wire.json` beside this file — one row per play and per end turn, machine-written off the API and never shown to the tester (`EB-216`, R101b)

## Fight 1, in the tester's own words

1. I attacked twice and blocked the first small hit, then used Kurage’s Oath into Rising Tide during the enemy’s buff turn for a 9-damage Surge. Once its Strength rose, I prioritized double Coral Guard on attack turns and dealt damage on buff turns, using Stolen Chapter at the end to find lethal before an 18-damage attack.

2. I seriously considered continuing with Oath plus Rising Tide for faster damage. That would have given up health to Exert, defensive energy, and the Casket’s healing on Surge turns, so it looked worse once the enemy began attacking for 11.

3. Yes. More buff turns would have encouraged full offense, while an earlier large attack would have made double Guard automatic sooner. If Stolen Chapter had not drawn another Water’s Edge on the final turn, I would have had to block and survive instead of killing.

4. Coral Guard became automatic against the strengthened attacks, especially in pairs. Water’s Edge was the automatic damage card. Kurage’s Oath and Rising Tide became mostly dead after the first combo because their combined benefit was too small relative to Exert, lost healing, and defensive needs.

5. My plan changed after the enemy’s first Empower raised its attack from 4 to 11. I moved from balanced offense to preserving health with double blocks, then switched back to maximum damage on buff turns and finally used card draw to secure lethal.

6. Exert was not defined on the screen; I inferred from losing 2 HP that it costs health. The timing and total usage of the Casket’s Mend were also difficult to track, and Stolen Chapter’s immediate draw plus planned future draw took one play to understand.

## Fight 2, in the tester's own words

1. I mostly paired Water’s Edge with enough Coral Guards to soften or cover each attack, then used buff turns for damage. Quiet Study supplied useful block and banked Tide without costing health; I finished with Water’s Edge before a 16-damage hit.

2. I seriously considered using Kurage’s Oath into Rising Tide for burst damage. It would have cost health through Exert, used defensive energy, and disabled the Casket’s mend on Surge turns, so I rarely thought the extra damage justified it.

3. Yes. More non-attacking intents would have pushed me toward all-out damage or Tide setup. Different draws could have forced Oath plus Rising Tide, especially if Water’s Edge or enough Guards were missing during a dangerous attack.

4. Water’s Edge was the automatic damage play, and Coral Guard was automatic against attacks. Quiet Study was useful when its block mattered or on safe setup turns. Oath became dead, while Rising Tide stayed mostly dead until enough Tide accumulated—but Water’s Edge still delivered lethal first.

5. The basic plan stayed defensive because Nibbit attacked often. Once it fell to 9 HP, I stopped gambling on card draw, fully blocked the next hit, then used its buff turn to reach 2 HP and finished safely.

6. Mend timing remained confusing: after the first turn HP fell from 63 to 61 despite no Surge, but later turns clearly healed. Exert still lacked an on-screen definition, and enemy Block made the first Water’s Edge appear to deal only 1 HP damage until I accounted for it.

## The run, in the tester's own words

1. The character builds Tide through skills, then cashes it out with Surge attacks for extra Hydro damage. The Bake-Kurage encourages alternating between setup turns that preserve its mend and selected burst turns that spend Tide, while Hydro auras appear intended to enable elemental reactions with Companion cards.

2. The repeated tension was damage versus survival: Surge disabled the turn’s healing, Tide setup consumed energy, and Kurage’s Oath also cost health through Exert. Most enemy attacks made ordinary attacks plus Coral Guards safer than committing to the Tide combo.

3. Water’s Edge and Coral Guard defined the run because they were the reliable one-energy damage and defense plays. Quiet Study was the most useful addition, combining block with safe Tide generation. Stolen Chapter often rescued awkward hands, while Rising Tide was the practical Surge outlet.

4. Play became repetitive when turns repeatedly reduced to Water’s Edge plus one or two Coral Guards. Enemy buff turns allowed offense, but attack turns were usually solved by counting how many Guards were needed and spending any remaining energy on Water’s Edge.

5. I would avoid drafting Breaker next time unless the deck had much stronger Tide generation or extra energy. Its two-energy cost made it difficult to defend and use in the same turn, and during the Shrinker Beetle fight, two one-cost attacks generally produced a better turn. I would also be cautious about adding more health-costing Tide setup, since the existing Oath copies were already frequently dead.
