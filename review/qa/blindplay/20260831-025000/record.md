# Blind play session `20260831-025000`

**R217 G — subjective feedback from an independent model playing the real game. Useful for iteration; not human validation, not balance evidence, not approval. It never enters an Understudy report, a win-rate table or a measurement register.**

## Identity

- **model_requested**: gpt-5.6-sol
- **model_observed**: gpt-5.6-sol
- **codex_version**: codex-cli 0.150.1
- **build_version**: 0.2.1786+proto.dirty
- **build_version_source**: the deployed `mods\klee\manifest.json` `version`
- **game_version**: v0.111.0
- **game_version_source**: the game's own `release_info.json` `version`
- **run_seed**: 1L130R6XTSRQ
- **arms_granted**: KLEEMOD-PROTO_PEARL_BARRAGE_TURN
- **arms_granted_source**: the embark sidecar `embark-20260830-224850.json`, matched by run seed
- **prompt_sha256**: 5dd16d9e02d6c11ae717749d2e1fd7926510f16d882d779a30557973112f7e0a
- **actions**: 24
- **termination**: max_actions

- **guardrail**: you are playing the real game through a tool that shows you only what the screen prints; nothing recorded here is a measurement, a comparison with any other run, or a judgement of whether the game is fun or good that anyone will treat as approval

- **wire snapshots**: 15 in `wire.json` beside this file — one row per play and per end turn, machine-written off the API and never shown to the tester (`EB-216`, R101b)

## Fight 1, in the tester's own words

1. I opened with Water’s Edge, then used Coral Guard+ and a regular Coral Guard to cover the 12-damage attack. On round two, I led with the free, self-Exhausting Gorou so Pearl of Wisdom would grant Charge and Burst Energy, then used the newly strengthened Tidal Barrage for the finishing line.

2. I seriously considered using only Coral Guard+ on round one and trusting the jellyfish’s 5 Block to reach 13 total, preserving the last energy conceptually. Since energy did not appear to carry over and there was no offensive card left after Tactical Retreat, that line would mainly have given up certainty against the attack.

3. A defensive or non-attacking enemy intent would have pushed me toward maximum damage instead of blocking. A better draw from Tactical Retreat—especially a one-energy attack—would also have replaced the second regular Coral Guard.

4. Gorou became automatic because it cost nothing, dealt damage, Exhausted itself, triggered Pearl of Wisdom, and entered the jellyfish’s memory. Tidal Barrage then became nearly automatic because it benefited from that Exhaust and created another one. The regular Coral Guards were effectively dead once enough Block was already secured, though I spent one because the energy had no visible future use.

5. My initial plan was simply to deal some damage and block the full attack. It changed when Coral Guard+ made the jellyfish promise another 5 Block, which encouraged Tactical Retreat, and changed more sharply on round two when Gorou revealed the Exhaust–Charge–memory synergy and made Tidal Barrage the clear payoff.

6. The most confusing part was that the jellyfish’s displayed end-turn action changed according to cards played even though its headline text only described Hydro damage. Tactical Retreat’s random discard also made it unclear which newly drawn card disappeared, and Tidal Barrage’s printed damage changed from 5 to 8 after Gorou without an explicit explanation on the screen.

## Fight 2, in the tester's own words

1. I opened with Water’s Edge and enough Coral Guards to cover the first 12-damage attack. On round two I played Gorou first to trigger Pearl of Wisdom, followed with Tidal Barrage, exhausted To the Front!, then used Sayu before Water’s Edge so the jellyfish ended on its damage mode. I finished with Water’s Edge+ and a regular Water’s Edge.

2. I seriously considered exhausting Sayu instead of To the Front!, since that might have added Sayu to the jellyfish’s memory. That would have given up immediate and next-turn Block, while To the Front! had no direct value unless I spent an action using its random transformation.

3. A larger round-two attack would have made Sayu more important and might have changed the Exhaust choice or forced a more defensive order. A stronger offensive draw from Tactical Retreat on round one would have replaced the unnecessary extra Coral Guard.

4. Gorou became automatic because it was free damage, Exhausted itself, triggered Pearl, and queued a replay. Tidal Barrage was the automatic follow-up because it scaled from Exhausts and created another one. Water’s Edge+ was automatic for finishing damage. Extra Coral Guards became dead once enough Block was secured, and To the Front! was the easiest sacrifice because its payoff was random and indirect.

5. The plan began as straightforward attack-and-block play. It shifted when I learned that the most recently played meaningful card changed the jellyfish’s end-turn output, so card order mattered; on round two I deliberately played Sayu before Water’s Edge to end in damage mode. The Exhaust interaction then became the main offensive plan.

6. The jellyfish display was still the confusing part. Its headline promised damage scaling with Charge, but the detailed forecast repeatedly showed only 4 damage at 2 Charge, and defensive cards changed that forecast to Block without the headline explaining why. The premature fight-record prompt during Tidal Barrage’s unresolved Exhaust selection was also confusing.

## Fight 3, in the tester's own words

1. I played To the Front! immediately because the incoming attack was only 4, leaving room to develop the deck’s Muster, Exhaust, Charge, and memory synergies instead of spending the turn on three redundant block cards.

2. I seriously considered opening with Tidal Barrage and exhausting a Coral Guard for reliable damage and an immediate Pearl trigger. That would have given up the chance to turn a weak card into a discounted Companion and potentially create two useful memories.

3. A much stronger enemy attack would have made a Coral Guard automatic before experimenting with Muster. A hand containing Press the Advantage, Gorou, or a stronger direct attack would also have made me sequence those cards first or preserve To the Front! for later.

4. To the Front! was the only automatic card in this hand because it enabled the deck’s central engine at zero energy. One Coral Guard was useful against the 4 damage, but the extra copies were dead; Tidal Barrage was promising, though I never reached the point of choosing its Exhaust target.

5. The plan did not have time to change. I began by trying to establish the Muster engine, and the fight ended immediately after that first action.

6. The abrupt ending was confusing: the enemy began at 57 HP, To the Front! printed no damage, and I was not shown which card it transformed or any resulting Companion before receiving the fight-over prompt.

## The run, in the tester's own words

1. The character appears to revolve around Bake Kurage, using Exhausts to gain Charge and Burst Energy while storing played or transformed cards as memories for later replays. Hydro application and elemental Companions add Reaction damage, while sequencing the final card of a turn seems to determine whether the jellyfish attacks or grants Block.

2. The repeated tension was between spending cards for immediate damage or defense and sacrificing or transforming them to build the Exhaust–Charge–memory engine. Card order also mattered: ending on defense protected HP, while ending on Hydro preserved jellyfish damage.

3. Gorou, Tidal Barrage, and To the Front! defined the run. Gorou demonstrated the ideal free Exhaust payoff, Tidal Barrage converted expendable cards into scaling damage and Charge, and To the Front! turned redundant cards into discounted Exhausting Companions. Water’s Edge was the reliable finishing attack, and Press the Advantage looked like a stronger combined attack-and-Muster enabler but was never drawn.

4. Play started to feel repetitive when hands contained several Coral Guards: once enough Block was secured, the remaining copies were mostly transformation or Exhaust fodder. The repeated Water’s Edge sequence was straightforward, though the run ended before that became a major pattern.

5. Next time I would avoid drafting more plain defensive cards like Coral Guard unless enemy damage clearly demanded them. The deck already drew redundant copies, and cards that attack while Mustering, Exhaust themselves, apply a different aura, or provide defense alongside another effect fit the engine better. The run also ended during Tidal Barrage’s unresolved Exhaust selection, so I never saw how the second fight or the new draft fully developed.
