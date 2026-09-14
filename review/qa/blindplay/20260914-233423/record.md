# Blind play session `20260914-233423`

**R217 G — subjective feedback from an independent model playing the real game. Useful for iteration; not human validation, not balance evidence, not approval. It never enters an Understudy report, a win-rate table or a measurement register.**

## Identity

- **model_requested**: gpt-6-astra
- **model_observed**: gpt-6-astra
- **codex_version**: codex-cli 0.153.4
- **build_version**: (not read)
- **build_version_source**: no GameDir in local.props, so the deployed package cannot be found
- **game_version**: (not read)
- **game_version_source**: no GameDir in local.props, so the install root cannot be found
- **run_seed**: KLEECAL1B001
- **arms_granted**: (none)
- **arms_granted_source**: no `--arm` grant recorded against this run's seed
- **prompt_sha256**: 6ffcf91e6fa4fce2ecab254ec13718856a03506bc600214671dbd9b1395a4cdc
- **actions**: 107
- **termination**: seat_refused

- **guardrail**: you are playing the real game through a tool that shows you only what the screen prints; nothing recorded here is a measurement, a comparison with any other run, or a judgement of whether the game is fun or good that anyone will treat as approval

- **wire snapshots**: 54 in `wire.json` beside this file — one row per play and per end turn, machine-written off the API and never shown to the tester (`EB-216`, R101b)

## Fight 1, in the tester's own words

1. I planted Jumpy Dumpty and fully blocked the first turn. Next I blocked Thorns, detonated the Bomb, killed the first Toadpole with Strike, and used Fury on the survivor to recover Ka-pow!. Waiting let the transferred Mines grow into lethal damage while preserving all my health.

2. I considered using Strike instead of the second Defend on turn one: 6 damage at the cost of 2 HP. I also initially planned to kill the first Toadpole with Fury, but Strike was enough and saved Fury's larger hit for the survivor.

3. Yes. The survivor's buff turn let me wait safely for Mine growth. An attack would have made me reconsider blocking or detonating immediately. Without Fury alongside Ka-pow!, I could not have relied on recovering the detonator for next turn.

4. Planting Jumpy Dumpty early and using Ka-pow! at lethal became straightforward choices. Defend mattered against attacks and Thorns. On the final turn, everything except Ka-pow! was unnecessary. Sparks accumulated without any visible way to spend them.

5. I changed targets for Fury after seeing the first Toadpole at 5 HP. Then I shifted from replaying Ka-pow! immediately to retaining it, because another turn of growth would make the Mines lethal by themselves.

6. The distinction between Bombs that require detonation and Mines that trigger before attacks took attention, but the detailed status text helped. I was unsure whether Ka-pow!'s attack would still trigger Thorns after its detonation killed the target. Fury also left a Pyro aura despite its printed card text not mentioning Pyro, which I could not explain from that screen.

## Fight 2, in the tester's own words

1. I played Jumpy Dumpty and Ka-pow!, then used Neow's Fury to recover both and replay them. That delivered lethal damage on turn one, avoiding the attack and debuff. The Boot's extra attack damage made the arithmetic work.

2. I checked using Strike with Fury and the recovered Ka-pow!, but that left damage short of an immediate kill. Replaying Jumpy Dumpty added more damage for the same energy. I did not seriously consider waiting once I saw the lethal sequence.

3. A different intent alone would not change taking a damage-free kill. A different draw would: without Fury or Ka-pow!, I could not repeat the combo, and would need to reconsider immediate damage versus Bomb growth.

4. Jumpy Dumpty, Ka-pow!, and Fury were the whole turn. Both Strikes became unnecessary. Tinder Toss never reached my hand, so this fight did not test the new card.

5. The plan stayed the same from the opening hand. Each screen confirmed the expected damage and energy. After finding lethal, the remaining choices felt like executing a settled sequence, especially the separate recovery selections and confirmation.

6. The combined Bomb status was slightly awkward: its wording about dropping Mines could sound as though both charges had that effect. The individual card descriptions clarified it. The attack-plus-debuff intent left the debuff unspecified, but killing before it acted made that uncertainty irrelevant.

## Fight 3, in the tester's own words

1. I planted Jumpy Dumpty on the attacking Slug, used Ka-pow! to create Mines, then Tinder Toss to detonate both. Strike finished the attacker, stunning the survivor. Three Strikes killed that survivor next turn. This prevented all damage and debuffs.

2. On turn two I considered Fury and recovering damage cards. It also offered lethal, but required extra selections with no better outcome. Three Strikes used all my energy but finished directly. I did not seriously pursue a defensive opening after finding the first-turn kill.

3. Different intents would matter less with this opening because killing one Slug stunned the other. A draw without both detonators would change that calculation. Without enough damage on turn two, the survivor's increased Strength would make future defense more urgent.

4. Jumpy Dumpty into Ka-pow! felt familiar; Tinder Toss then had a clear job detonating the spawned Mines. Defend became dead once the survivor was stunned. Amber had no immediate trigger against a debuff intent, and Fury was unnecessary. The three Strikes became automatic once I counted lethal.

5. The opening plan held. On the second draw I switched from looking for another Bomb sequence to simply counting Strike damage. There was no reason to rebuild the combo.

6. Ravenous clearly described the stun, and the changed intent confirmed it. Nothing materially confused me this fight. The repeated rules took more reading than the final turn needed; playing three Strikes felt mechanical after the damage calculation.

## Fight 4, in the tester's own words

1. I worked around the 20-damage cap while blocking what I could. Two Strikes into Razor reached the first cap and refunded energy for Defend. Later I used Amber, Pop!, and Fury recovering Defend to combine damage with protection. Razor's Overloaded reduced the fourth-turn attack, and retained Ka-pow! finished on turn five. I lost 17 HP.

2. I seriously considered planting Jumpy Dumpty on turn one instead of taking immediate attack damage, or instead of the refunded Defend. Those choices gave up immediate damage or 5 HP of protection. On turn two I chose a second Defend over Strike. In hindsight, that Strike's 6 damage could have avoided the extra turn caused by leaving the Colony at 1 HP, although I did not work that through when choosing defense.

3. Yes. Repeated attacks made blocking and Weak important. A quieter turn would have favored planting Bombs. Drawing a detonator with Jumpy Dumpty would have changed the opening; drawing Fury immediately after the reshuffle limited its recovery options to cards I played that turn.

4. Defend became a frequent default, and Pop! was easy to play for later damage. Razor mattered for both his energy refund and Weak. Attacks became dead once the cap was spent. Jumpy Dumpty, usually my automatic opener, went unused throughout this fight. The Flex Potion offered no useful improvement to the lines I chose.

5. The cap immediately changed my usual Bomb opening. Fury then became a way to replay defense rather than repeat a damage combo. By turn four, the plan was simply to weaken the attack, block, and retain lethal for next turn. Waiting with the enemy at 1 HP felt mechanical and exposed the cost of my earlier defensive choice.

6. Amber's buff displayed the literal placeholder {Damage}. The screen also said no reaction was reachable, but her retaliation apparently dealt 14 rather than 8 against Electro, suggesting Overloaded; no reaction was listed next turn. That made the element rules harder to trust. The cap itself and Razor's later reaction were clearly displayed.
