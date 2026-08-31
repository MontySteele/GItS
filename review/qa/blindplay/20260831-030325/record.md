# Blind play session `20260831-030325`

**R217 G — subjective feedback from an independent model playing the real game. Useful for iteration; not human validation, not balance evidence, not approval. It never enters an Understudy report, a win-rate table or a measurement register.**

## Identity

- **model_requested**: gpt-5.6-sol
- **model_observed**: gpt-5.6-sol
- **codex_version**: codex-cli 0.150.1
- **build_version**: 0.2.1786+proto.dirty
- **build_version_source**: the deployed `mods\klee\manifest.json` `version`
- **game_version**: v0.111.0
- **game_version_source**: the game's own `release_info.json` `version`
- **run_seed**: 8G5ZXUVR3HAW
- **arms_granted**: KLEEMOD-PROTO_SHINOBU_SANCTIFYING_RING_EITHER, KLEEMOD-PROTO_ITTO_SUPERLATIVE_SUPERSTRENGTH_EITHER
- **arms_granted_source**: the embark sidecar `embark-20260830-230248.json`, matched by run seed
- **prompt_sha256**: 5dd16d9e02d6c11ae717749d2e1fd7926510f16d882d779a30557973112f7e0a
- **actions**: 24
- **termination**: max_actions

- **guardrail**: you are playing the real game through a tool that shows you only what the screen prints; nothing recorded here is a measurement, a comparison with any other run, or a judgement of whether the game is fun or good that anyone will treat as approval

- **wire snapshots**: 16 in `wire.json` beside this file — one row per play and per end turn, machine-written off the API and never shown to the tester (`EB-216`, R101b)

## Fight 1, in the tester's own words

1. I opened with the free, Exhausting Gorou attack on the small attacking slime to gain Charge and Burst Energy, then used both Water’s Edges to weaken a status-inflicting slime while blocking the incoming hit. On round two I killed the weakened Leaf Slime, stacked enough Block for the remaining 11 damage, and used To the Front! because one Coral Guard had become redundant.

2. I seriously considered immediately killing the small Twig Slime with Water’s Edge after Gorou. That would have removed its 4-damage intent at once, but given up the chance to let the queued Gorou finish it next turn while my paid attacks pressured another enemy.

3. A heavier first-round attack would have made immediate lethal and Block more important. A more offensive second-round draw would also have shifted me toward killing the medium slime rather than overblocking and Mustering a spare defensive card.

4. Gorou was automatic because it was free, dealt damage, Exhausted, and activated Pearl of Wisdom. Water’s Edge became automatic against enemies already near lethal. Tactical Retreat was effectively dead once I had spent my energy because its random discard could disrupt the hand without guaranteeing anything useful; the second Coral Guard also became surplus after enough defense was already secured.

5. My initial plan was to let the jellyfish’s Charge-scaled damage help clean up the two weakened enemies. I changed course after seeing that the jellyfish’s projected end-of-turn action followed the last card played—Coral Guard made it grant Block—so I stopped relying on its printed damage and instead used explicit lethal, full defense, and then Mustered the redundant card.

6. The main confusion was the jellyfish display: its buff text said it deals damage and applies Hydro, but after defensive cards its memory forecast said it would grant Block instead. It was also unclear why Shinobu’s printed 4 Block led to a projected 5 Block, and the fight ended immediately after To the Front! before showing what it transformed or how the remaining enemy was defeated.

## Fight 2, in the tester's own words

1. I used free Gorou to build Charge, weakened two small slimes while blocking their attack, then killed them through queued and direct damage. Against the last slime I Mustered a redundant Coral Guard into discounted Itto, dealt 14 damage while gaining Block, accepted 1 damage to preserve the jellyfish’s attack, and finished with Oni Rush.

2. I considered skipping Muster and simply playing both Coral Guards. That was safer and clearer, but it would have given up the discounted Itto, another Exhaust trigger, and a much faster kill. I also considered blocking the final 1 damage, but preferred keeping 4 jellyfish damage.

3. More incoming damage would have made the extra Coral Guard automatic and Muster less attractive. Without the Itto transformation or the round-three Oni Rush draw, I would have needed a slower defensive line while waiting for Water’s Edge or enough Charge to replay memory cards.

4. Free Exhausting Companions became automatic because they advanced Pearl of Wisdom and memory while providing immediate value. Water’s Edge was automatic for cleaning up weakened enemies, and Oni Rush was automatic lethal. Tactical Retreat was dead when its random discard risk outweighed its draw, while surplus Coral Guards became good Muster fuel once defense was covered.

5. The plan changed twice. First, I stopped assuming the jellyfish always dealt its printed damage after its forecast changed to Block based on the last card played. Second, after Muster produced Itto, I shifted from stalling behind Block to racing the remaining slime with large Companion attacks.

6. The jellyfish was difficult to read: its printed buff promised Charge-scaled damage, but the forecast sometimes copied Block and sometimes showed only 4 damage despite having Charge. The memory ordering and costs were clearer once displayed, though it was surprising that the first queued Coral Guard prevented the later Itto replay from firing. The temporary fight-over record prompt before the required Muster selection was also confusing.

## The run, in the tester's own words

1. The character appears to turn Exhaust into a resource engine: Exhausted cards generate Charge and Burst Energy, create memories that can replay later, and feed a persistent jellyfish. Muster converts ordinary cards into discounted, Exhausting Companions, so the deck wants expendable cards and strong Companion payoffs.

2. The recurring tension was between immediate defense and preserving offense. The jellyfish’s end-of-turn action seemed to follow the last card played, so ending on Coral Guard could replace damage with Block. Charge also created a tension between building a valuable memory queue and having enough Charge to pay for its first entry so later entries could fire.

3. Gorou defined the opening because its free Exhaust triggered every important engine piece. Water’s Edge supplied dependable cleanup damage, Coral Guard handled most defense and became Muster fuel when redundant, and To the Front! producing discounted Itto created the strongest turn. Communion of Tides looked well suited to the deck, although the run ended before I could use it.

4. Play became repetitive when turns reduced to playing Water’s Edge one or two times, then deciding whether Coral Guard was necessary. Against the Shrinker Beetle, the 30% attack penalty made those repeated attacks feel especially incremental.

5. I would avoid drafting more plain defensive cards like Coral Guard unless the deck needed Muster fodder, because duplicate copies frequently became redundant and could suppress the jellyfish’s damage when played last. I would also avoid Tactical Retreat: random discard made it unreliable whenever the hand contained a specific attack or defensive card I needed.
