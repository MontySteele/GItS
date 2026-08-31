# Blind play session `20260831-025720`

**R217 G — subjective feedback from an independent model playing the real game. Useful for iteration; not human validation, not balance evidence, not approval. It never enters an Understudy report, a win-rate table or a measurement register.**

## Identity

- **model_requested**: gpt-5.6-sol
- **model_observed**: gpt-5.6-sol
- **codex_version**: codex-cli 0.150.1
- **build_version**: 0.2.1786+proto.dirty
- **build_version_source**: the deployed `mods\klee\manifest.json` `version`
- **game_version**: v0.111.0
- **game_version_source**: the game's own `release_info.json` `version`
- **run_seed**: VC7KQVSAT3NB
- **arms_granted**: KLEEMOD-PROTO_SHINOBU_SANCTIFYING_RING_PRICED, KLEEMOD-PROTO_THOMA_CRIMSON_OOYOROI_PRICED, KLEEMOD-PROTO_ITTO_SUPERLATIVE_SUPERSTRENGTH_PRICED
- **arms_granted_source**: the embark sidecar `embark-20260830-225629.json`, matched by run seed
- **prompt_sha256**: 5dd16d9e02d6c11ae717749d2e1fd7926510f16d882d779a30557973112f7e0a
- **actions**: 24
- **termination**: max_actions

- **guardrail**: you are playing the real game through a tool that shows you only what the screen prints; nothing recorded here is a measurement, a comparison with any other run, or a judgement of whether the game is fun or good that anyone will treat as approval

- **wire snapshots**: 15 in `wire.json` beside this file — one row per play and per end turn, machine-written off the API and never shown to the tester (`EB-216`, R101b)

## Fight 1, in the tester's own words

1. I opened with To the Front! because it was free, preserved all three energy, and promised a discounted Exhausting companion that could activate Pearl of Wisdom and build Charge.

2. I seriously considered Water’s Edge plus Coral Guard, which would have applied Hydro, dealt some damage, and covered most of the incoming 7. That line would have given up the early Muster memories, Exhaust synergy, and whatever tempo the recruited companion provided.

3. Yes. If both enemies had intended heavy attacks, I would have prioritized immediate block, probably Itto - Superlative Guard. A draw without To the Front! would also have pushed me toward Water’s Edge and Coral Guard.

4. To the Front! looked automatic whenever drawn early because it cost nothing and connected directly to the relic and Charge engine. The two three-cost attacks looked situational rather than dead; Thoma was the least attractive on this screen because it offered less damage and block than Itto, though Pyro reactions could have changed that.

5. I did not see enough of the fight to revise the plan. My opening plan was to establish the Muster–Exhaust–Charge engine, then use the remaining energy according to the recruited card and enemy pressure.

6. The Bake-Kurage text was slightly confusing: the general buff said it attacks at the end of the turn, while its memory said it would do nothing because no card had been played yet. I inferred that playing cards or creating memories enables its action, but the exact trigger was not fully explicit.

## Fight 2, in the tester's own words

1. I opened by Mustering Coral Guard into a free Gorou, then used Gorou’s block-and-attack boost with Itto to nearly kill the attacking Toadpole. After finishing that enemy, I defended through the survivor’s multi-hit turn, used Tactical Retreat to find a free Exhaust attack, triggered Electro-Charged with Shinobu, and finally used Itto for the guaranteed kill.

2. I seriously considered using Water’s Edge after Gorou instead of Itto. It would have preserved energy and established Hydro, but it would have given up 8 immediate damage and the clean near-kill on the dangerous attacker. On the last turn I also considered letting Poison finish the enemy, but that risked unnecessary delay for no clear benefit.

3. Yes. Heavier opening attacks would have made immediate defense more important, while a passive first round could have favored slower Hydro and reaction setup. A different recruit from Muster, or an earlier draw of Shinobu against a Hydro target, would also have changed the order substantially.

4. Free Exhausting companions became automatic because they advanced Charge and Burst Energy while costing little or nothing. Itto was the reliable closer and emergency defensive attack. Coral Guard was useful against exact incoming damage but became dead when there was no attack, and Thoma was mostly dead because Itto offered much better immediate damage and block whenever reactions were not relevant.

5. The plan shifted during round two. Initially I wanted to build the Muster–Exhaust–Charge engine, but the expensive Coral Guard memory blocked every queued replay at only 1–2 Charge, so I stopped planning around memory value and focused on ordinary damage, exact defense, and the Electro-Charged damage over time.

6. The jellyfish display was the main source of confusion. Its buff said it deals 4 plus 3 per Charge, yet the turn preview sometimes showed only 4 damage and sometimes showed 5 Block instead. The memory also said nothing could fire because Coral Guard was unaffordable, while the preview still appeared to mimic recently played cards. “Kokomi Burst” also accumulated without any displayed spending rule.

## The run, in the tester's own words

1. The character seems built around turning ordinary cards into temporary companions, then Exhausting those companions to gain Charge and Burst Energy. Charge powers the persistent Bake-Kurage and pays for a queue of remembered cards, while elemental auras create a secondary reaction-based damage plan.

2. The recurring tension was immediate survival versus engine setup. Spending energy on block and reliable attacks kept HP safe, but Mustering and Exhausting companions promised stronger future turns; the memory queue also encouraged Charge generation while sometimes making that investment feel inaccessible.

3. To the Front! and the free Gorou companions defined the engine, while Itto - Superlative Guard was the dependable damage-and-defense card. Water’s Edge enabled Hydro setup, Shinobu converted it into useful damage over time, and Coral Guard repeatedly supplied straightforward survival. Pulsing Current looked like the best future addition because it combined improved damage, Hydro, and direct Charge gain.

4. Play became repetitive when the safe line was simply to match incoming damage with Coral Guards and use Itto whenever three energy were available. Several hands reduced to choosing between efficient block and a single large attack, especially while the memory queue remained stalled.

5. Next time I would avoid drafting more plain low-value block cards, especially additional Coral Guards. They kept the run safe, but duplicates crowded hands and the first transformed Coral Guard created a 3-Charge memory at the front of the queue, delaying the free companion memories behind it.
