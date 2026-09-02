# Blind play session `klee-overhaul-r2-codex`

**R217 G — subjective feedback from an independent model playing the real game. Useful for iteration; not human validation, not balance evidence, not approval. It never enters an Understudy report, a win-rate table or a measurement register.**

## Identity

- **model_requested**: gpt-5.6-sol
- **model_observed**: gpt-5.6-sol
- **codex_version**: codex-cli 0.150.1
- **build_version**: 0.2.1911+proto.dirty
- **build_version_source**: the deployed `mods\klee\manifest.json` `version`
- **game_version**: v0.111.0
- **game_version_source**: the game's own `release_info.json` `version`
- **run_seed**: JHZ4W7H7M9KM
- **arms_granted**: (none)
- **arms_granted_source**: no `--arm` grant recorded against this run's seed
- **prompt_sha256**: 5dd16d9e02d6c11ae717749d2e1fd7926510f16d882d779a30557973112f7e0a
- **actions**: 80
- **termination**: max_actions

- **guardrail**: you are playing the real game through a tool that shows you only what the screen prints; nothing recorded here is a measurement, a comparison with any other run, or a judgement of whether the game is fun or good that anyone will treat as approval

- **wire snapshots**: 52 in `wire.json` beside this file — one row per play and per end turn, machine-written off the API and never shown to the tester (`EB-216`, R101b)

## Fight 1, in the tester's own words

1. I opened with Pop!, then Jumpy Dumpty, then Kaboom! to set off 13 Bomb damage alongside Kaboom’s 6. I accepted the first 8-damage hit because this line cut the enemy nearly in half, created a Mine, and generated Spark.

2. I seriously considered Jumpy Dumpty plus Duck and Cover, leaving the Bombs to grow for a later detonation. That would have prevented 5 damage, but given up immediate burst and risked needing another setup turn before drawing Kaboom again.

3. A larger first attack would have pushed me toward blocking; a non-attacking intent would have made the full Bomb line even more automatic. A draw without Kaboom would also have favored placing Bombs and defending while waiting for a way to set them off.

4. Pop! was automatic whenever Bomb setup was useful because it cost no energy. Kaboom became automatic once Bombs were stacked, and Ka-pow! was automatic as free damage with spare Spark. Duck and Cover was temporarily dead during the opening burst, but became important when the enemy survived at 2 HP. No card was permanently dead.

5. The initial plan was an aggressive Bomb detonation. On round two, Weak made the available attacks fall 2 HP short of lethal, so I changed to dealing maximum damage while reserving one energy for Block, then finished on round three.

6. The Bomb and Mine text was understandable once the Mine triggered. The confusing part was the duplicate-card enchantment warning: the screen said one copy might be enchanted but could not show which, leaving no informed way to choose between identical copies.

## Fight 2, in the tester's own words

1. I focused Corpse Slug (2), first with two Kabooms, then with Pop! plus Kaboom. Once it reached 4 HP, Ka-pow! killed it for free; the other slug ate it and became Stunned, giving me a safe setup turn. I then used Powder Charge and two Kabooms to finish the survivor before its 12-damage attack.

2. I seriously considered playing Jumpy Dumpty on round two and immediately detonating. If its random Bomb landed on the damaged slug, that line would have killed it and created Mines; if it landed on the other slug, I would have taken the full 14 incoming damage. I chose guaranteed damage and Block instead, giving up the higher-upside Bomb setup.

3. If only one slug had been attacking on round two, I would have been more willing to gamble on Jumpy Dumpty. A draw containing Ka-pow! one turn earlier would have killed the damaged slug sooner and prevented more damage; a draw without Kaboom would have forced slower Bomb growth and heavier defense.

4. Ka-pow! became automatic when it could kill the 4-HP slug and trigger the survivor’s Stun. Pop! and Powder Charge were automatic before an available Kaboom because they added free detonation damage. Duck and Cover was useful under incoming attacks but dead during the Stunned turn. Jumpy Dumpty was effectively dead because its random targeting was too risky against two enemies.

5. The initial plan was straightforward focus fire. On round two I shifted toward cautious guaranteed damage because both enemies attacked while Frail weakened my Block. After the first slug died and the survivor became Stunned, the plan changed back to unrestricted Bomb setup and burst.

6. Ravenous was clear once it triggered, although “When an enemy dies” initially left a little ambiguity about which slug would eat the corpse. The repeated warning that identical cards might secretly differ by enchantment remained confusing because it offered no usable basis for choosing between them.

## Fight 3, in the tester's own words

1. I opened with Pop! and Jumpy Dumpty, then blocked instead of detonating immediately. The Bombs grew from 13 to 17, so the next Kaboom dealt 23 total damage, created a Mine, generated Spark, and enabled Run Away! for 7 free Block. Later, Powder Charge plus Pop! fed another large Kaboom, and Ka-pow! removed the enemy’s final Block before Kaboom finished it.

2. I seriously considered detonating the opening Bombs immediately with Kaboom instead of blocking. That would have dealt 19 damage and created the Mine a turn sooner, but it would have given up 5 Block and prevented the two Bombs from gaining 4 extra damage during the wait.

3. A non-attacking first intent would have made delaying the detonation even easier. A much larger attack, or a second-turn draw without Kaboom, might have made immediate detonation preferable. Drawing an attack on round three could also have ended the fight before the enemy gained Strength and Block.

4. Pop! and Powder Charge became automatic before Kaboom because they added free Bomb damage. Run Away! became automatic immediately after a detonation, and Ka-pow! was automatic when Spark was plentiful. Duck and Cover was useful against attacks but dead during the buff turn; Jumpy Dumpty was excellent in the opener but too slow late.

5. The plan began as delayed Bomb growth with defense. After the first detonation, it shifted to using the generated Spark and free cards for efficient follow-up. When the enemy survived at 2 HP and chose to buff, I stopped defending and waited for attacks to finish through its new Block.

6. The screen was mostly clear. The main uncertainty was whether each individual Bomb grows separately or the displayed total simply gains a fixed amount; the total changing from 13 to 17 clarified the result, but not the exact underlying rule.

## The run, in the tester's own words

1. The character builds Bombs on enemies, lets them grow when useful, then uses set-off attacks to combine delayed Bomb damage with direct damage. Detonations generate Spark, which pays for free Bomb placement or more set-off attacks, so the intended loop seems to be Bombs → detonation → Spark → more Bombs. Mines, Chained Reactions, and Run Away! add damage, rebuilding, and defense around that loop.

2. The recurring tension was whether to detonate immediately or block and let Bombs grow. Waiting improved damage but risked drawing no set-off card later; detonating early generated Spark and Mines sooner but sacrificed growth. Against multiple enemies, random Bomb placement also fought against the need to focus down the most dangerous target.

3. Pop!, Kaboom!, and Ka-pow! defined the basic engine. Powder Charge made Spark useful as free setup, while Run Away! turned successful detonations into efficient defense. Chained Reactions looked like the main scaling payoff because detonations automatically seeded new Bombs, although the run ended before I could explore it fully. Jumpy Dumpty was powerful against one enemy but unreliable against several.

4. Play became repetitive once most turns reduced to placing every free Bomb, detonating with Kaboom or Ka-pow!, then spending leftover energy on Duck and Cover. The three copies of Duck and Cover especially made defensive hands feel interchangeable, and repeated identical Kaboom choices added little decision-making.

5. Next time I would avoid Tinder Toss unless I had clearer control over its random targets, and I would be cautious about Jumpy Dumpty in a multi-enemy route for the same reason. I would also avoid adding too many Bomb setup cards without enough reliable detonation, draw, healing, or stronger defense; this run had a functional engine but steadily lost health and was vulnerable when scaling enemies demanded both focused damage and large Block.
