# Blind play session `klee-overhaul-r3-codex`

**R217 G — subjective feedback from an independent model playing the real game. Useful for iteration; not human validation, not balance evidence, not approval. It never enters an Understudy report, a win-rate table or a measurement register.**

## Identity

- **model_requested**: gpt-5.6-sol
- **model_observed**: gpt-5.6-sol
- **codex_version**: codex-cli 0.150.1
- **build_version**: 0.2.1966+proto.dirty
- **build_version_source**: the deployed `mods\klee\manifest.json` `version`
- **game_version**: v0.111.0
- **game_version_source**: the game's own `release_info.json` `version`
- **run_seed**: RKE3U57FRK9H
- **arms_granted**: (none)
- **arms_granted_source**: no `--arm` grant recorded against this run's seed
- **prompt_sha256**: 5dd16d9e02d6c11ae717749d2e1fd7926510f16d882d779a30557973112f7e0a
- **actions**: 82
- **termination**: seat_refused

- **guardrail**: you are playing the real game through a tool that shows you only what the screen prints; nothing recorded here is a measurement, a comparison with any other run, or a judgement of whether the game is fun or good that anyone will treat as approval

- **wire snapshots**: 53 in `wire.json` beside this file — one row per play and per end turn, machine-written off the API and never shown to the tester (`EB-216`, R101b)

## Fight 1, in the tester's own words

1. I opened with Jumpy Dumpty, detonated its Bomb with Ka-pow!, spent the resulting Spark on Dig In, and focused the attacking slug. On round two I killed that slug first to force the survivor to eat it and become Stunned, then loaded and detonated Bombs on the survivor.

2. I considered spreading damage or delaying the first Bomb so it could grow. That would have preserved more eventual Bomb damage, but given up immediate Sparks, full defense, and control of the dangerous enemy intents.

3. Yes. If both enemies had attacked on round one, I might have prioritized more Block; if the survivor had not been attacking on round two, killing the weakened slug immediately would have been less urgent. A draw without Ka-pow! would also have forced me to let the Bomb grow.

4. Jumpy Dumpty into Ka-pow! became the automatic setup-and-detonate line, and Dig In was automatic once Spark existed. Duck and Cover was effectively dead whenever Dig In covered the full attack or the enemy was Stunned.

5. The initial plan was to focus the attacking slug while building the Bomb engine. It shifted on round two when Ravenous let me deliberately kill one slug to cancel the survivor’s multi-hit turn through Stun.

6. The Spark display was initially a little confusing because Dig In printed cost 0 while its refusal explained that it actually cost 1 Spark. Otherwise the Bomb totals, Mine behavior, and numbered duplicate cards were clear.

## Fight 2, in the tester's own words

1. I used free Bombs before Ka-pow! whenever possible, turning each detonation into damage and Spark for Dig In. On the first turn that let me play my whole hand and fully block; later I used Jumpy Dumpty and Ka-pow! together, then finished with Powder Charge and Ka-pow!.

2. On round two I seriously considered Kaboom! instead of Duck and Cover. It would have left the enemy much closer to death, but I chose to give up that damage to save 5 HP; the Mine still reduced the enemy before its attack.

3. Yes. A non-attacking intent on round two would have made Kaboom! automatic, while a larger attack on round one might have forced more defensive compromises. Missing Ka-pow! alongside the Bomb cards would have delayed both their damage and Spark generation.

4. Free Bomb setup into Ka-pow! became automatic, and Dig In was automatic when Spark was available against meaningful damage. Extra Duck and Cover copies were dead when there was no attack, while plain Kaboom! was often squeezed out by the stronger Bomb-and-defense line.

5. The plan stayed mostly consistent: detonate quickly rather than waiting for Bomb growth, then convert Spark into defense. The only real adjustment was choosing Duck and Cover over extra damage on round two to preserve health.

6. Powder Charge unexpectedly reduced Spark from 2 to 1 when played, despite displaying cost 0 and describing Spark only as a general resource. That made its actual cost unclear; otherwise the screen was readable.

## Fight 3, in the tester's own words

1. I played both opening Bomb generators and blocked the first attack, letting the Bombs grow for one turn because no detonator was available. On round two I used both Ka-pow! copies, feeding the Sparks into Powder Charge and Dig In, then finished with Kaboom!.

2. I considered detonating only once on round two and saving the new Bomb for later growth. That would have improved its eventual damage and avoided attacking twice while Weak, but it would have left the enemy healthier and prolonged the fight.

3. Yes. A non-attacking second turn could have justified waiting for Weak to expire and letting the Bombs grow again. Drawing a detonator on round one would probably have led me to cash in immediately for Sparks and use Dig In instead of two Duck and Covers.

4. Bomb setup before a Set off card remained automatic, and Dig In was automatic once Sparks existed. The third Duck and Cover was dead on the opening turn after 10 Block already covered 8 damage; Fwoosh! was also dead in practice because it arrived only after the enemy was already in direct-kill range.

5. The plan changed with the opening draw: instead of immediate detonation, I banked Bombs for a turn. On round two I switched back to rapid cycling, detonating twice despite Weak to create Sparks, defend, and leave a trivial finish.

6. The Bomb display showed Bomb 17 but said Set off would deal 12 total, which I inferred was the Weak-adjusted amount but had to reason through. The upgraded Ka-pow! still printed 7 damage while the unupgraded one printed 5 under Weak, making it unclear whether the upgrade had actually increased base damage or simply resisted the debuff. Powder Charge’s hidden 1-Spark cost was clearer this time only because the refusal explicitly stated it.

## Fight 4, in the tester's own words

1. I focused one slug immediately, then placed Pop!+ on it and used Jumpy Dumpty for another Bomb while blocking what I could. Once Ka-pow! arrived, I killed the weakened slug to trigger Ravenous Stuns, focused the bombed survivor, and repeatedly used kills to cancel dangerous enemy turns before finishing with Powder Charge, Pop!+, and Fwoosh!.

2. I considered spreading the opening attacks or placing Pop!+ on a full-health slug. That would have developed damage more evenly, but it would have delayed the first kill and the powerful Ravenous Stun chain while giving up more health.

3. Yes. If fewer enemies had attacked early, I could have invested more aggressively in Bomb setup. Drawing a usable detonation on round two—or starting with Spark—would have let Fwoosh! kill the first slug immediately and prevented much of the 19 HP lost across the first two rounds.

4. Killing a weakened slug before resolving the others became automatic because Ravenous Stunned every survivor. Bomb setup into Ka-pow! or Fwoosh! was also automatic. Block cards became dead whenever Ravenous produced Stun, while Powder Charge, Dig In, and Fwoosh! were dead in the opening cycle because their hidden Spark costs could not be paid.

5. The opening plan was to focus one attacker, but the lack of starting Spark stalled the engine and forced a defensive setup turn. Once the first Bomb was detonated, the plan shifted to exploiting Ravenous Stuns and spending the accumulated Sparks freely; the final turns were then straightforward lethal setups.

6. The largest confusion was that Powder Charge and Fwoosh! printed cost 0 but actually required 1 Spark, and their rules text did not state that price. It was also surprising that killing one slug caused both remaining slugs to become Stunned and gain Strength; Ravenous’s singular wording made me expect only one eater.

## The run, in the tester's own words

1. The character builds Bombs, detonates them for Pyro damage, and converts each Bomb that goes off into Spark. Spark then pays for cards that look energy-free, especially efficient defense and extra Bomb or detonation effects. The strongest turns chained setup, Set off, Spark generation, and defense in that order.

2. The recurring tension was whether to detonate immediately for damage, Spark, and survival or let Bombs grow for a larger later payoff. A second tension was Spark bootstrapping: several useful cards were completely unavailable until an energy-costing Ka-pow! detonated the first Bomb.

3. Pop!+ and Ka-pow! defined the basic engine, with Jumpy Dumpty adding Mines and strong multi-enemy value. Dig In turned successful detonations into efficient defense, while Run Away! became a good free follow-up. Powder Charge and Fwoosh! extended the engine once Spark existed, but Pocket Fireworks was drafted specifically to make weak opening hands less dependent on it.

4. Play became repetitive once most turns reduced to placing every affordable Bomb, detonating immediately, spending Spark on Dig In or Powder Charge, and using leftover energy on direct attacks or Block. Corpse Slug fights also repeated the tactic of killing one enemy to Stun every survivor through Ravenous.

5. Next time I would avoid taking too many Spark-costing cards early, especially a second Fwoosh! or similar effects, because they can create hands that cannot start their own engine. I would also avoid more ordinary Duck and Cover copies; Dig In and Run Away! made them inefficient or dead whenever the Bomb plan was functioning.
