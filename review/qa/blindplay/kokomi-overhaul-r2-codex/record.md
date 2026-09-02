# Blind play session `kokomi-overhaul-r2-codex`

**R217 G — subjective feedback from an independent model playing the real game. Useful for iteration; not human validation, not balance evidence, not approval. It never enters an Understudy report, a win-rate table or a measurement register.**

## Identity

- **model_requested**: gpt-5.6-sol
- **model_observed**: gpt-5.6-sol
- **codex_version**: codex-cli 0.150.1
- **build_version**: 0.2.2007+proto.dirty
- **build_version_source**: the deployed `mods\klee\manifest.json` `version`
- **game_version**: v0.111.0
- **game_version_source**: the game's own `release_info.json` `version`
- **run_seed**: 0TY6NNVRM7L1
- **arms_granted**: (none)
- **arms_granted_source**: no `--arm` grant recorded against this run's seed
- **prompt_sha256**: 5dd16d9e02d6c11ae717749d2e1fd7926510f16d882d779a30557973112f7e0a
- **actions**: 100
- **termination**: max_actions

- **guardrail**: you are playing the real game through a tool that shows you only what the screen prints; nothing recorded here is a measurement, a comparison with any other run, or a judgement of whether the game is fun or good that anyone will treat as approval

- **wire snapshots**: 62 in `wire.json` beside this file — one row per play and per end turn, machine-written off the API and never shown to the tester (`EB-216`, R101b)

## Fight 1, in the tester's own words

1. I blocked enough to cover or nearly cover each attack, then spent remaining energy on immediate damage. On the enemy’s buff turn, I used all three Water’s Edges to push it to 4 HP and finished it next turn with Slack Water before its 14-damage attack.

2. I considered planning Kurage’s Oath or Slack Water on the Bake-Kurage. Against one enemy, that gave up immediate damage for weaker delayed damage or delayed Weak, so it never beat simply attacking.

3. Yes. A multi-enemy fight would have made Kurage’s Oath or planned Slack Water much more attractive. A non-attacking intent reduced Block to dead draws, while a stronger attack or a draw without enough Block would have forced a more defensive line.

4. Slack Water+ became automatic when drawn: it dealt the most damage, applied Weak, and triggered the casket’s 2-damage strike. Water’s Edge was the automatic remaining-energy attack. Coral Guard was useful only when damage was incoming; Kurage’s Oath was effectively dead in this single-target fight.

5. The plan stayed defensive at first, preserving HP while dealing damage. It shifted to full offense on round 3 when Nibbit intended to buff, after which the only goal was to secure the kill before its empowered attack.

6. The main confusion was that Hydro Aura is labeled a buff, so applying it did not trigger the relic despite Water’s Edge saying it “applies Hydro.” The duplicate-card numbering also changes as copies leave the hand, and the enchantment warning says the visible information cannot distinguish potentially different copies.

## Fight 2, in the tester's own words

1. I accepted 4 damage on round 1 to play three Water’s Edges, then used the enemy’s buff turn for Slack Water+, another Water’s Edge, and a planned Kurage’s Oath. The planned 5 damage helped put it into range for a three-attack kill on round 3.

2. I seriously considered blocking the first 4 damage. That would have saved a little HP but given up 6 immediate damage, likely extending the fight against an enemy that later gained 7 Strength. I also considered using Vulnerable Potion, but this fight did not seem dangerous enough to spend it.

3. Yes. A larger opening attack would have made Coral Guard automatic. If the buff turn had instead been an attack, I probably would have blocked rather than planning Kurage’s Oath. A draw without three attacks on the final turn would also have shifted me toward Sea-Salt Prayer for Weak and Block.

4. Slack Water+ was automatic because its damage, Weak, and casket trigger made it unusually efficient. Water’s Edge was the default damage filler. Coral Guard was dead during the buff turn, while Kurage’s Oath was useful only because spare energy could safely become delayed damage. Sea-Salt Prayer was dead once lethal was available.

5. The initial plan was pure damage while the attack was small. When the enemy showed a buff, I used the otherwise dead defensive energy to set up a Plan. After it gained 7 Strength, the plan became immediate lethal before its attack rather than trying to defend.

6. The Plan interaction was clear once used. The lingering oddity is that Hydro Aura is labeled a buff and does not trigger a relic that rewards debuffs, despite the character’s repeated “Applies Hydro” wording. Duplicate-card numbering also shifts as copies are played, which requires care.

## Fight 3, in the tester's own words

1. I killed the 4-damage Twig Slime immediately, then planned Kurage’s Oath to hit both remaining enemies. Next I used Slack Water+ to exactly kill the small Leaf Slime, followed by Sea-Salt Prayer and Water’s Edge on the medium slime; later Water’s Edges brought it into range for Slack Water+ to finish.

2. I considered blocking on round 1, which would have reduced damage by only one more than killing Twig Slime while leaving that enemy alive. I also considered blocking fully on round 2, but that would have surrendered 6 damage and prolonged the fight. Gambler’s Brew could have replaced the dead guards on round 3, but spending a potion merely to avoid two Status cards seemed wasteful.

3. Yes. Larger combined attacks would have made Coral Guard more important, while non-attacking enemies made area Plans and attacks dominant. A stronger offensive draw on round 3 might have ended the fight before the medium slime added Status cards; a worse draw after those Status cards could have made that choice costly.

4. Slack Water+ was automatic whenever it could secure a kill or combine damage, Weak, and the casket trigger. Kurage’s Oath became valuable with multiple enemies, unlike in prior single-target fights. Sucrose was completely automatic because it produced energy and replaced itself for zero cost. Guards were dead against Strategic intents, and Slimed was unnecessary once lethal was already in hand.

5. The plan began with target removal plus delayed area damage. Once only the medium slime remained, it shifted back to efficient single-target damage while accepting small amounts of HP loss. On round 3, the unusually defensive hand forced a slower setup turn rather than immediate lethal.

6. The enemy list and intents were readable. Duplicate numbering still shifts as copies leave the hand, and Hydro’s presentation remains slightly counterintuitive because it is an aura labeled as a buff rather than a debuff. The Strategic intent’s number was understandable only from its accompanying sentence.

## The run, in the tester's own words

1. The character appears to balance immediate Hydro attacks with delayed Plans carried out by the untouchable Bake-Kurage. Weak and Vulnerable are especially valuable because applying a true debuff triggers Tamakushi Casket for extra Hydro damage, while Plans convert spare energy on safe turns into damage or control next turn.

2. The repeated tension was immediate survival versus delayed efficiency. Plans were excellent during buff or Status intents, especially against several enemies, but aggressive turns demanded Block, Weak, or immediate kills. The elite sharpened this tension by flooding the deck with damaging Infection cards while its spawned enemies kept gaining Strength.

3. Slack Water+ defined most fights because it combined good damage, Weak, Hydro, and a casket trigger. Sea-Salt Prayer+ became the best defensive card by pairing 7 Block with Weak and extra relic damage. Kurage’s Oath was weak against one enemy but excellent against groups, Ambush supplied efficient delayed single-target damage, and Sucrose was an automatic free energy-and-draw play.

4. Play became repetitive when turns reduced to Slack Water first, Water’s Edge with remaining offensive energy, and enough Coral Guard or Sea-Salt Prayer to cover the intent. The elite broke that pattern initially, but its Infection-heavy draws later became repetitive in a harsher way: play whatever guards appeared, lose HP to unplayable cards, and wait for attacks.

5. I would avoid drafting additional ordinary Block-only cards or narrow Plan support without an immediate effect. The deck already had several Coral Guards, and dead defensive hands were costly during non-attacking turns; conversely, slow Plans became dangerous once Status cards crowded out reliable draws. I would prioritize draw, Status removal or discard, efficient Weak, and area damage instead. Gambler’s Brew looked like the intended answer to Infection, but its command was repeatedly refused, so I could not evaluate that escape route.
