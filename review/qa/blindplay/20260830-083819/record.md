# Blind play session `20260830-083819`

**R217 G — subjective feedback from an independent model playing the real game. Useful for iteration; not human validation, not balance evidence, not approval. It never enters an Understudy report, a win-rate table or a measurement register.**

## Identity

- **model_requested**: gpt-5.6-sol
- **model_observed**: gpt-5.6-sol
- **codex_version**: codex-cli 0.150.1
- **build_version**: 0.2.1627+proto.dirty
- **build_version_source**: the deployed `mods\klee\manifest.json` `version`
- **game_version**: v0.111.0
- **game_version_source**: the game's own `release_info.json` `version`
- **run_seed**: KURAGEMEM002
- **arms_granted**: KLEEMOD-PROTO_KURAGES_OATH_MEMORY
- **arms_granted_source**: the embark sidecar `embark-20260830-043739.json`, matched by run seed
- **prompt_sha256**: 5dd16d9e02d6c11ae717749d2e1fd7926510f16d882d779a30557973112f7e0a
- **actions**: 60
- **termination**: max_actions

- **guardrail**: you are playing the real game through a tool that shows you only what the screen prints; nothing recorded here is a measurement, a comparison with any other run, or a judgement of whether the game is fun or good that anyone will treat as approval

- **wire snapshots**: 32 in `wire.json` beside this file — one row per play and per end turn, machine-written off the API and never shown to the tester (`EB-216`, R101b)

## Fight 1, in the tester's own words

1. I opened with Alchemical Curiosity for efficient block and more information, then focused every attack on the aggressive Toadpole. Defile, Gorou, and Water’s Edge killed it before its attack; with only the buffing enemy left, I used To the Front! to develop the memory engine.

2. I seriously considered playing Coral Guard and accepting some damage, or splitting damage toward the buffing Toadpole. Either line would have given up the clean kill on the attacker and likely prolonged the fight.

3. Yes. If both enemies had attacked, I would have prioritized more block; if neither attacked, I would have leaned into Muster earlier. A weaker attack draw would also have forced a defensive turn instead of the immediate kill.

4. Alchemical Curiosity became close to automatic because one energy bought both block and cards. Defile was automatic while available because Ethereal made holding it wasteful. Coral Guard became dead once the attacker was killed, while Tactical Retreat never became necessary because the draw was already strong.

5. The plan changed after Alchemical Curiosity drew Gorou and Water’s Edge. At that point, the hand contained exact lethal on the aggressive Toadpole, so I shifted from general defense and information gathering to removing all incoming damage.

6. The Bake-Kurage display was initially confusing: its end-of-turn preview changed from granting Block to dealing Hydro damage depending on the latest card played, while exhausted Gorou separately entered a next-turn memory. The relationship among the preview, memory queue, Charge, and the fight ending immediately after To the Front! was not fully clear.

## Fight 2, in the tester's own words

1. I used Alchemical Curiosity first for block and draw, then concentrated Defile, Gorou, and Water’s Edge on the attacking Toadpole to remove its 7 damage. Afterward I Mustered Coral Guard into a free Companion, built Charge, and finished the remaining Toadpole with two Water’s Edges plus the jellyfish’s end-of-turn damage.

2. I considered defending more conventionally with Coral Guard and saving Muster for later. That would have been safer to understand, but it would have given up a free Companion, extra Charge, and useful memory setup. I also considered splitting damage, but that would have left the first attacker alive.

3. Yes. More simultaneous incoming damage would have made Coral Guard or Sayu more important, while a draw without the exact first-turn attack sequence would have forced a slower defensive plan. If the final enemy had not shown a multi-hit attack, I might have played Kurage’s Oath instead of blocking Thorns before attacking.

4. Alchemical Curiosity was an automatic early play because its block and draw were both relevant. Defile was nearly automatic because holding an Ethereal attack wastes it. The two Water’s Edges became automatic once their combined damage plus the jellyfish represented lethal. Kurage’s Oath and Sayu were dead in the final hand because immediate lethal was better; Tactical Retreat also accomplished little when it drew and randomly discarded the only new card.

5. The plan changed twice: Alchemical Curiosity revealed exact damage to kill the first attacker, shifting me from defense to focused lethal; then, once only the buffing enemy remained, I switched to experimenting with Muster and memory. On round two I abandoned engine development and used Coral Guard plus two attacks because the jellyfish supplied the last 4 damage.

6. The memory system was the confusing part. The jellyfish’s printed buff always described damage, but its preview sometimes said it would grant Block based on the last relevant card. It was also unclear at first that Muster required a separate selection and confirmation screen, and the game asked for a fight record before that interaction and the fight itself had actually finished.

## Fight 3, in the tester's own words

1. I played free Gorou first to deal damage and create Charge, established Kurage’s Oath, blocked with Coral Guard, and used Defile before it could vanish. On round two, the Spiral-enchanted Water’s Edge dealt 12 through Replay, and another Water’s Edge finished the Seapunk before its four-hit attack.

2. I considered skipping Kurage’s Oath to preserve energy or using Tactical Retreat for another draw. Skipping the power would have given up recurring Block from jellyfish pulses, while Retreat risked immediately discarding the card it drew and offered little control.

3. Yes. A non-attacking first-round intent would have let me skip Coral Guard and develop or attack more aggressively. A draw without Defile or with more free cards might have made Tactical Retreat worthwhile, while a stronger second-round attack without lethal would have pushed me toward Sayu plus Coral Guard.

4. Free Gorou and Defile were automatic: Gorou generated damage, Charge, and memory value, while Defile would be lost if held. Kurage’s Oath was attractive early because a replay was already queued. The Spiral Water’s Edge became automatic once it represented 12 damage for 1 energy. Tactical Retreat was effectively dead, and the defensive cards became dead once the second-round hand showed lethal.

5. The initial plan was balanced setup, defense, and damage because the enemy had 46 HP. The plan changed immediately on round two when the enchanted Water’s Edge and a second attack showed exact lethal, making further defense and engine development unnecessary.

6. Kurage’s Oath timing was unclear. The first turn’s pulse did not reduce the current 11-damage attack beyond Coral Guard’s 5 Block; instead, its 3 Block appeared to remain at the start of round two. The jellyfish preview, its printed damage rule, and what counts as a “pulse” still require careful inference.

## Fight 4, in the tester's own words

1. I opened with Alchemical Curiosity, used Sara to amplify free Gorou, then played Kurage’s Oath and Coral Guard to set up the memory engine while fully blocking the first attack. On round two I blocked again, used the weakened Defile, and chose To the Front! intending to turn the slow Before Sun and Moon power into an immediate discounted Companion while keeping one energy for Water’s Edge.

2. I seriously considered simply playing Water’s Edge after Defile. That guaranteed 4 immediate damage and preserved a straightforward line, but it gave up the chance for a free Companion, another Exhaust trigger, more Charge, and an additional memory. I also considered playing Before Sun and Moon directly, but the fight looked too short for its scaling to repay the energy quickly.

3. Yes. If the enemy had not attacked on either turn, I would have spent less energy on Coral Guard and prioritized Before Sun and Moon earlier. Without Weak on round two, Defile and Water’s Edge would have been much closer to ending the fight directly, making Muster less attractive.

4. Alchemical Curiosity was automatic for block plus draw, Sara into free Gorou was automatic efficient damage, and Defile remained automatic because Ethereal punished holding it. Tactical Retreat was dead because its random discard made the draw unreliable. Before Sun and Moon also became too slow in the immediate situation, which is why I selected it as the intended Muster target.

5. The first-turn plan was to build a stable engine while taking no damage. On round two, Weak reduced the direct-damage line, so I shifted toward using Muster to convert a slow setup card into immediate Companion and Charge value.

6. The fight-record prompt appeared immediately after playing To the Front!, before the required card-selection and confirmation screens, just as in the earlier fight. That makes the fight appear over even though the action has not resolved. The jellyfish preview also continued to alternate between copying a card’s effect and its printed pulse behavior in a way that was difficult to reconcile.

## The run, in the tester's own words

1. The character seems to turn played cards into a second, delayed layer of value through Bake-Kurage. Exhausting Companions builds Charge and queues memories; Muster converts ordinary cards into discounted Companions; Hydro and reactions add tactical sequencing; and powers can make the jellyfish’s pulses provide scaling damage or Block.

2. The recurring tension was immediate survival versus building the Charge-and-memory engine. Spending energy on block or direct attacks was reliable, while Muster and powers promised more later but could queue an expensive memory that stopped every card behind it. There was also constant tension over which card should be played last because the jellyfish preview appeared to copy that card’s effect.

3. Alchemical Curiosity defined the opening turns by combining efficient Block with draw. Defile was the most reliable burst damage, and free Gorou Companions connected attacks, Exhaust, Charge, and memory. Water’s Edge was the dependable finisher, especially the Spiral copy with Replay. Kurage’s Oath supplied persistent defensive value, though its timing was difficult to read.

4. Play became repetitive when turns reduced to Alchemical Curiosity or Coral Guard for defense, then Defile or Water’s Edge for damage, followed by checking whether the jellyfish would finish the enemy. Tactical Retreat repeatedly looked available but rarely looked worth the random discard. The reward and post-fight collection sequence also repeated several separate confirmations.

5. I would avoid Tactical Retreat because drawing one and randomly discarding one offered little dependable improvement and sometimes merely emptied the hand. I would also be cautious with Before Sun and Moon: it was slow when drawn, and transforming it created a 3-Charge memory at the front of the queue that blocked free memories behind it. I would avoid adding many more plain block cards as well, because the deck already had several Coral Guards and stronger block-plus-value options.

## Turn by turn, in the tester's own words

One line per answered turn: the command the tester gave and the sentence it gave for it, verbatim, off `turn-*/reply.json`. The same R217 G label rides on it as on the fight records — it is one model's account, not a measurement.

| turn | command | the tester's sentence |
|---|---|---|
| `turn-001` | `choose "Kaleidoscope"` | Two card rewards offer immediate flexibility without adding a Curse, while the Rest-based Max HP gain is slower and competes with other rest-site actions. |
| `turn-002` | `choose "Card (1)"` | The two rewards appear identical at this stage, so I’ll inspect the first one. |
| `turn-003` | `choose "Card"` | The refusal confirms that the accepted reward name is the unnumbered title shown on screen. |
| `turn-004` | `choose "Defile"` | Defile is immediately useful, energy-efficient damage; Hotfix depends on Orbs we may not have, and Outbreak is expensive. |
| `turn-005` | `choose "Card"` | The remaining Kaleidoscope reward offers a second card choice, so I’ll inspect it before proceeding. |
| `turn-006` | `choose "Alchemical Curiosity"` | Block plus card draw for 1 energy is broadly useful and reliable, unlike the expensive or more random alternatives. |
| `turn-007` | `proceed` | The opening rewards are complete, so it is time to enter the run. |
| `turn-008` | `choose "Proceed"` | The direct proceed command errored, so I’ll select the printed Proceed option instead. |
| `turn-009` | `go "Monster (path 1)"` | Both routes currently show the same encounter type with no further distinguishing information, so I’ll take path 1. |
| `turn-010` | `play "Alchemical Curiosity"` | This covers most of the incoming 7 damage while drawing two cards, giving more information before committing attacks or Muster. |
| `turn-011` | `play "Defile" on "Toadpole (2)"` | The aggressive Toadpole can be killed this turn by combining Defile with the two smaller attacks, preventing its damage entirely. |
| `turn-012` | `play "Gorou — Inuzaka All-Round Defense" on "Toadpole (2)"` | This free attack advances the planned kill while preserving the final energy for Water's Edge. |
| `turn-013` | `play "Water's Edge" on "Toadpole (2)"` | This kills the attacking enemy now, eliminating all incoming damage this round. |
| `turn-014` | `play "To the Front!"` | With no incoming attack and no energy left, Muster can convert an otherwise unplayable card into a discounted Companion and build the memory engine. |
| `turn-015` | `` |  |
| `turn-016` | `choose "Coral Guard"` | Coral Guard has already become unnecessary this turn, while Tactical Retreat remains useful free hand cycling. |
| `turn-017` | `confirm` | Coral Guard is the intended transformation target, so I’ll confirm without also sacrificing Tactical Retreat. |
| `turn-018` | `play "Gorou — General's War Banner"` | The free Companion adds Block, strengthens the next attack, and should Exhaust to build Charge for the queued memories. |
| `turn-019` | `play "Tactical Retreat"` | With no incoming attack and no energy cost, cycling may find a free attack that can use the 3-damage buff before the turn ends. |
| `turn-020` | `end turn` | The hand is empty and the remaining enemy is not attacking, so there is nothing else to do this turn. |
| `turn-021` | `play "Coral Guard"` | Five Block will absorb the Thorns damage from the two Water’s Edge attacks, which should then deal lethal damage. |
| `turn-022` | `play "Water's Edge (1)" on "Toadpole"` | Two copies will reduce the enemy to 2 HP, and the jellyfish’s end-of-turn damage should finish it while the Block absorbs Thorns. |
| `turn-023` | `play "Water's Edge" on "Toadpole"` | This leaves the Toadpole at 2 HP, allowing the previewed 4 Hydro damage from the jellyfish to finish it before its attack. |
| `turn-024` | `end turn` | The jellyfish’s previewed 4 damage will kill the 2-HP Toadpole before its attack resolves. |
| `turn-025` | `` |  |
| `turn-026` | `choose "Gold"` | Gold is guaranteed value and can be collected before inspecting the card reward. |
| `turn-027` | `choose "Card"` | I’ll inspect the available card choices before deciding whether to add one. |
| `turn-028` | `choose "Kujou Sara — Crowfeather Cover"` | The free damage boost supports the deck’s attack turns without forcing a card sacrifice or adding another basic block effect. |
| `turn-029` | `proceed` | All rewards have been collected, so there is nothing else to select here. |
| `turn-030` | `go "Unknown (path 1)"` | This is the only available map node. |
| `turn-031` | `choose "Observe"` | A permanent enchantment should provide lasting value, while drinking would waste 8 points of the 26 healing at current HP. |
| `turn-032` | `choose "Water's Edge (1)"` | Water’s Edge benefits directly from the deck’s attack-damage boosts, so enhancing an attack should improve the main offensive line. |
| `turn-033` | `confirm` | Water’s Edge (1) is selected for the Spiral enchantment, so I’ll confirm it. |
| `turn-034` | `choose "Proceed"` | The event is complete, and selecting the printed option was the reliable way to advance on the earlier event screen. |
| `turn-035` | `go "Monster (path 1)"` | This is the only available route. |
| `turn-036` | `play "Gorou — Inuzaka All-Round Defense" on "Seapunk"` | The free attack deals damage, Exhausts to generate Charge, and queues a free memory replay for next turn. |
| `turn-037` | `play "Kurage's Oath"` | Playing the power now lets the queued Gorou replay generate Block next turn, while enough energy remains for both defense and Defile. |
| `turn-038` | `play "Coral Guard"` | Five Block reduces the incoming 11 damage while leaving exactly enough energy to use the Ethereal Defile. |
| `turn-039` | `play "Defile" on "Seapunk"` | Defile is strong immediate damage and would Exhaust unused, so it should be played before ending the turn. |
| `turn-040` | `end turn` | The jellyfish will deal 4 damage and Kurage’s Oath should add 3 Block, limiting the incoming hit; Tactical Retreat risks discarding whatever it draws without improving this turn. |
| `turn-041` | `play "Water's Edge (1)" on "Seapunk"` | The Spiral-enchanted copy replays for 12 total damage, setting up lethal with one more Water’s Edge while leaving energy unused. |
| `turn-042` | `play "Water's Edge (1)" on "Seapunk"` | Six damage immediately kills the 5-HP enemy and prevents its multi-hit attack. |
| `turn-043` | `` |  |
| `turn-044` | `choose "Gold"` | Gold is guaranteed value and can be collected before evaluating the potion and card reward. |
| `turn-045` | `choose "Potion"` | A free potion adds tactical flexibility, and it can be collected before inspecting the card reward. |
| `turn-046` | `choose "Card"` | I’ll inspect the card choices before deciding whether any improve the deck. |
| `turn-047` | `choose "Before Sun and Moon"` | This power directly strengthens every jellyfish pulse and scales with the Charge generated by exhausted Companions, reinforcing the deck’s existing engine. |
| `turn-048` | `proceed` | All available rewards have been collected. |
| `turn-049` | `go "Monster (path 1)"` | This is the only available route. |
| `turn-050` | `play "Alchemical Curiosity"` | It fully covers most of the incoming attack while drawing two cards to reveal the best use of the remaining energy. |
| `turn-051` | `play "Kujou Sara — Crowfeather Cover"` | The free buff turns Gorou’s upcoming attack from 6 into 10 damage without using either remaining energy. |
| `turn-052` | `play "Gorou — Inuzaka All-Round Defense" on "Sludge Spinner"` | This converts Sara’s buff into 10 free damage and Exhausts to start building Charge and memory. |
| `turn-053` | `play "Kurage's Oath"` | The queued free replay will make this power valuable next turn, and one energy will remain for Coral Guard to cover the incoming attack. |
| `turn-054` | `play "Coral Guard (1)"` | This raises Block to 10, fully covering the incoming 8 damage without spending the potion. |
| `turn-055` | `end turn` | The incoming attack is fully blocked, and Tactical Retreat could discard its own draw without adding reliable value. |
| `turn-056` | `play "Coral Guard"` | This raises Block to 8 against the incoming 11 while preserving two energy for Defile and Water’s Edge, the strongest immediate damage line. |
| `turn-057` | `play "Defile" on "Sludge Spinner"` | Defile is the strongest available attack and would Exhaust if left in hand, so it should be used now. |
| `turn-058` | `play "To the Front!"` | Muster can turn the slower power into a free Companion while preserving the last energy for Water’s Edge, potentially adding immediate value and more Charge. |
| `turn-059` | `` |  |
| `turn-060` | `choose "Before Sun and Moon"` | The power is too slow for the nearly finished fight, while Water’s Edge still provides immediate damage with the remaining energy. |
| `turn-061` | `confirm` | Before Sun and Moon is the intended transformation target, so I’ll keep Water’s Edge and confirm. |
| `turn-062` | `play "Water's Edge" on "Sludge Spinner"` | Water’s Edge applies Hydro so the free Sayu attack can Swirl that aura afterward, potentially triggering extra reaction damage. |
| `turn-063` | `play "Sayu — Yoohoo Art: Fuuin Dash" on "Sludge Spinner"` | The free attack consumes the Hydro aura for Swirl, adds damage, and Exhausts to increase Charge. |
| `turn-064` | `end turn` | The jellyfish will reduce the enemy to 5 HP, and the existing 8 Block limits the 11-damage attack to 3; that is not enough damage to justify spending Fortifier. |
| `turn-065` | `play "Water's Edge (1)" on "Sludge Spinner"` | It deals exactly the enemy’s remaining 6 HP, ending the fight before the incoming attack. |
| `turn-066` | `` |  |

## Leak audit

Every observation the tester was actually shown — `turn-*/prompt.md`, the exact bytes handed to `codex exec` — scanned against `qa_packet.FORBIDDEN` plus the pilot-vocabulary rules and this run's seed.

- **observations scanned**: 66
- **total hits**: 1

| rule | hits |
|---|---|
| `pilot-vocabulary-score` | 1 |

Offenders (first 40):

- `turn-001` — `pilot-vocabulary-score` matched `score` in: guide, no card list, no score, no recommendation, and no way to ask for one.
