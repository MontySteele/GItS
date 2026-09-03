Status: PARTIAL -- the session refused at turn 122 (prompt_exceeds_ctx: ~119k prompt + 12k answer against one 128k slot); no sealed record. Per-turn notes carried by `turn_notes`. Instrument row: EB-324.

## Turn by turn, in the tester's own words

One line per answered turn: the command the tester gave and the sentence it gave for it, verbatim, off `turn-*/reply.json`. The same R217 G label rides on it as on the fight records — it is one model's account, not a measurement.

| turn | command | the tester's sentence |
|---|---|---|
| `turn-001` | `choose "Phial Holster"` | Phial Holster gives immediate utility with an extra potion slot and two potions, which is broadly useful. Hefty Tablet is tempting but adds Injury, and Booming Conch only helps in elite fights. |
| `turn-002` | `proceed` | The relic choice is complete and the screen only offers Proceed. |
| `turn-003` | `go "Monster (path 3)"` | All immediate nodes are monsters, but path 3 leads to two options next, giving more flexibility than the single-node paths. |
| `turn-004` | `play "Slack Water (proto)" on "Toadpole (2)"` | Weaken the attacking Toadpole and deal some damage before setting up the Bake-Kurage plan and blocking. |
| `turn-005` | `play "Kurage's Oath (proto)" on "Bake-Kurage"` | Set the Bake-Kurage to deal 7 to all enemies next turn, then use remaining energy to block the weakened 5-damage attack. |
| `turn-006` | `play "Defend"` | Gain 5 Block to fully block the weakened Toadpole's 5 damage, then end turn. |
| `turn-007` | `end turn` | No energy remains, and our 5 Block should cover the weakened 5-damage attack. |
| `turn-008` | `play "Defend (1)"` | Build 5 Block first so Fortifier can triple it, then use the remaining energy to kill the unthorned Toadpole safely. |
| `turn-009` | `play "Strike (1)" on "Toadpole (2)"` | Kill the unthorned Toadpole 2 with two strikes, avoiding its buff and thorns, while keeping 5 Block for the 3x3 attack. |
| `turn-010` | `use potion "Fortifier"` | Triple the 5 Block to 15 before attacking, so the remaining Toadpole's 3x3 attack is fully blocked. |
| `turn-011` | `play "Strike" on "Toadpole (2)"` | Kill the unthorned Toadpole 2 with the last energy, leaving 15 Block to absorb the 3x3 attack and any thorns. |
| `turn-012` | `end turn` | No energy remains; 15 Block should fully cover the 3x3 attack. |
| `turn-013` | `play "Kurage's Oath (proto)" on "Bake-Kurage"` | Set up 7 damage next turn, then use Slack Water for 4 and Defend to survive the 7-damage attack, killing the Toadpole next turn. |
| `turn-014` | `play "Slack Water (proto)" on "Toadpole (1)"` | Deal 4 and apply Weak before blocking, so the planned 7 next turn is closer to killing it. |
| `turn-015` | `play "Defend (1)"` | Block the weakened 5-damage attack, then let the planned 7 damage bring the Toadpole to 2 HP next turn. |
| `turn-016` | `end turn` | No energy remains; 5 Block covers the weakened 5-damage attack, and the planned 7 will bring the Toadpole to 2 HP. |
| `turn-017` | `play "Strike (1)" on "Toadpole (1)"` | The Toadpole is at 2 HP, so a Strike finishes it before it can empower. |
| `turn-018` | `` |  |
| `turn-019` | `choose "Add a card to your deck"` | Adding a card is the most impactful long-term reward compared to gold or a potion. |
| `turn-020` | `choose "Battle Plan"` | Battle Plan fits the Bake-Kurage plan mechanic and gives energy plus card draw next turn, which is broadly stronger than the other options. |
| `turn-021` | `choose "Dexterity Potion"` | Take the potion for extra utility; gold is less immediately useful. |
| `turn-022` | `proceed` | The only remaining reward is gold, which is automatically collected; proceed to continue the run. |
| `turn-023` | `go "Unknown (path 2)"` | The unknown node may provide a useful event or reward, and it leads to fewer immediate monsters than the path that continues into more combat. |
| `turn-024` | `choose "Light"` | The screen offers no explicit options, but the title implies Light and Dark doors; I'll guess Light as the safer choice. |
| `turn-025` | `choose "Light Door"` | Upgrading 2 random cards is generally more valuable than removing 1 card, especially early in the run. |
| `turn-026` | `proceed` | The Light Door choice is complete and the screen only offers Proceed. |
| `turn-027` | `go "Monster (path 1)"` | Only one path is available, so I must take it. |
| `turn-028` | `play "Battle Plan" on "Bake-Kurage"` | Set up Battle Plan for next turn to gain energy and draw cards, then use remaining energy to block the 8-damage attack. |
| `turn-029` | `use potion "Dexterity Potion"` | Gain permanent Dexterity to reduce the incoming 8-damage attack, then use energy to block and attack. |
| `turn-030` | `play "Defend (1)"` | With Dexterity, Defend gives 7 Block; play two to fully block the 8-damage attack. |
| `turn-031` | `play "Defend (1)"` | Gain another 7 Block to fully cover the 8-damage attack, then end turn. |
| `turn-032` | `end turn` | 14 Block fully covers the 8-damage attack; no energy remains, so end turn to let Battle Plan trigger. |
| `turn-033` | `play "Kurage's Oath (proto)+" on "Bake-Kurage"` | Set up 10 damage next turn, then use Battle Plan for extra energy/draw, block the 6-damage attack, and deal some damage now. |
| `turn-034` | `play "Defend+"` | Block the 6-damage attack with upgraded Defend, then use remaining energy to deal damage while weak. |
| `turn-035` | `play "Battle Plan" on "Bake-Kurage"` | Add Battle Plan to the plan queue so next turn we get both 10 damage and extra energy/draw, then use remaining energy to deal damage now. |
| `turn-036` | `play "Strike (1)" on "Sludge Spinner"` | Deal 4 damage with the last energy; the planned 10 plus Battle Plan next turn will finish the fight. |
| `turn-037` | `end turn` | No energy remains; 10 Block covers the 6-damage attack, and the two planned cards will deal 10 and grant energy/draw next turn. |
| `turn-038` | `play "Defend+"` | Gain 10 Block to start covering the 11-damage attack, then add more block and deal damage with remaining energy. |
| `turn-039` | `play "Defend (1)"` | Add 7 more Block to reach 17, fully covering the 11-damage attack, then use remaining energy to deal damage. |
| `turn-040` | `play "Battle Plan" on "Bake-Kurage"` | Set up Battle Plan for next turn to gain energy and draw, then use remaining energy to deal damage. |
| `turn-041` | `play "Strike (1)" on "Sludge Spinner"` | Deal 6 damage with the last energy; 17 Block already covers the 11-damage attack. |
| `turn-042` | `end turn` | No energy remains; 17 Block covers the 11-damage attack, and Battle Plan will give extra energy/draw next turn. |
| `turn-043` | `play "Kurage's Oath (proto)+" on "Bake-Kurage"` | Set up 10 damage next turn, then block the 14-damage attack with two Defends, and deal 4 damage now to bring the enemy to 14 HP. |
| `turn-044` | `play "Strike (1)" on "Sludge Spinner"` | Reduce the enemy to 14 HP, then block with Defend and hit again; the planned 10 next turn will finish it. |
| `turn-045` | `play "Strike (1)" on "Sludge Spinner"` | Bring the Sludge Spinner to 10 HP so the planned 10 damage next turn kills it, then use the remaining energy to block. |
| `turn-046` | `play "Defend"` | Gain 7 Block to reduce the 14-damage attack; the planned 10 damage next turn will kill the Sludge Spinner. |
| `turn-047` | `end turn` | No energy remains; 7 Block reduces the 14-damage attack to 7, and the planned 10 damage will kill the Sludge Spinner next turn. |
| `turn-048` | `` |  |
| `turn-049` | `choose "Add a card to your deck"` | Adding a card is more impactful long-term than gold. |
| `turn-050` | `choose "Song of Pearls (proto)"` | It synergizes with the Bake-Kurage plan engine by giving Block whenever a Plan is carried out, which is broadly stronger than the one-off or situational options. |
| `turn-051` | `proceed` | The card reward is already taken; only gold remains, so proceed to continue. |
| `turn-052` | `go "Monster (path 1)"` | Both immediate nodes are monsters, so I'll take path 1 to continue toward the unknown and shop ahead. |
| `turn-053` | `play "Slack Water (proto)" on "Seapunk"` | Apply Weak and deal damage, then use the remaining energy to block the 11-damage attack. |
| `turn-054` | `play "Defend+"` | Gain 8 Block to fully cover the weakened 8-damage attack, then use remaining energy to deal 6 damage. |
| `turn-055` | `play "Strike (1)" on "Seapunk"` | We already have 8 Block covering the attack, so use the last energy to deal 6 damage and start setting up for next turn. |
| `turn-056` | `end turn` | No energy remains; 8 Block covers the 8-damage attack, and we can set up plans next turn. |
| `turn-057` | `play "Battle Plan" on "Bake-Kurage"` | Set up Battle Plan for extra energy and draw next turn, then use remaining energy to deal damage and block the 2x4 attack. |
| `turn-058` | `play "Strike (1)" on "Seapunk"` | Battle Plan is queued for next turn, so I'll spend both energy on attacks now to drop the Seapunk to 20 HP and finish it next turn, accepting the 8-damage 2x4 hit. |
| `turn-059` | `play "Strike" on "Seapunk"` | Bring the Seapunk to 20 HP so next turn's 4 energy (3 + Battle Plan's 1) can likely finish it with strikes, accepting the 8 damage from 2x4. |
| `turn-060` | `end turn` | No energy remains; end turn to take the 8 damage and let Battle Plan trigger next turn for extra energy and draw to finish the Seapunk. |
| `turn-061` | `play "Strike (1)" on "Seapunk"` | The Seapunk is at 20 HP and only intends to buff, so I'll spend all 4 energy on Strikes to kill it immediately. |
| `turn-062` | `play "Strike (1)" on "Seapunk"` | The Seapunk is at 14 HP and only intends to buff, so I'll spend all 3 energy on Strikes to kill it immediately. |
| `turn-063` | `play "Strike (1)" on "Seapunk"` | The Seapunk is at 8 HP; two more Strikes will kill it before it can buff. |
| `turn-064` | `play "Strike" on "Seapunk"` | The Seapunk is at 2 HP; one Strike kills it before it can buff. |
| `turn-065` | `` |  |
| `turn-066` | `choose "Add a card to your deck"` | Adding a card is more impactful long-term than gold. |
| `turn-067` | `choose "The Clouds Like Waves Rippling"` | It synergizes with my debuff application from Slack Water and Rally, giving passive Block whenever I apply Weak, which fits my playstyle. |
| `turn-068` | `proceed` | The card reward is already taken; only gold remains, so proceed to continue. |
| `turn-069` | `go "Monster (path 1)"` | Only one path is available, so I must take it. |
| `turn-070` | `play "Kurage's Oath (proto)+" on "Bake-Kurage"` | Set up 10 damage to all enemies next turn, then use remaining energy to block the 14 total incoming damage. |
| `turn-071` | `play "Defend (1)"` | Block 5 of the 14 incoming damage; I'll play another Defend next to reduce the hit further. |
| `turn-072` | `play "Defend"` | Gain 5 more Block for a total of 10, reducing the 14 incoming damage to 4; the planned 10 damage next turn will do the heavy lifting. |
| `turn-073` | `end turn` | No energy remains; 10 Block reduces the 14 incoming damage to 4, and the planned 10 damage will hit all three rats next turn. |
| `turn-074` | `play "Battle Plan" on "Bake-Kurage"` | Set up Battle Plan for next turn to gain energy and draw, then use remaining energy to deal damage and block the 22 incoming damage as best I can. |
| `turn-075` | `play "Strike" on "Two-Tailed Rat (1)"` | Kill the 7 HP rat to reduce incoming damage from 22 to 14, then block with Defend. |
| `turn-076` | `play "Defend"` | Gain 3 Block to reduce the 22 incoming damage to 19; no Strike in hand to finish the 1 HP rat, so block is the best use of last energy. |
| `turn-077` | `end turn` | No energy remains; 3 Block reduces the 22 incoming damage to 19, and Battle Plan will give extra energy/draw next turn. |
| `turn-078` | `play "Strike" on "Two-Tailed Rat (1)"` | Kill the 1 HP rat before it summons, then set up Oath and block the 6-damage attack. |
| `turn-079` | `play "Kurage's Oath (proto)+" on "Bake-Kurage"` | Set up 10 damage to all enemies next turn, then block the 6-damage attack with Defend+. |
| `turn-080` | `play "Defend+"` | Block the 6-damage attack with 8 Block, then set up Battle Plan for extra energy and draw next turn alongside the Oath. |
| `turn-081` | `play "Slack Water (proto)" on "Two-Tailed Rat (2)"` | Deal 4 damage and apply Weak now so the planned 10 damage next turn kills both rats, ending the fight. |
| `turn-082` | `end turn` | No energy remains; 8 Block covers the 6-damage attack, and the planned 10 damage will kill both rats next turn. |
| `turn-083` | `` |  |
| `turn-084` | `choose "Add a card to your deck"` | Adding a card is the most impactful long-term reward compared to gold or a potion. |
| `turn-085` | `choose "Undertow (proto)"` | It deals 7 damage normally and 10 if the enemy has a debuff, which synergizes perfectly with my Slack Water and Rally debuff application. 10 damage for 1 energy is excellent. |
| `turn-086` | `choose "Explosive Ampoule"` | The potion is more immediately useful in combat than gold. |
| `turn-087` | `proceed` | The only remaining reward is gold, which is automatically collected; proceed to continue the run. |
| `turn-088` | `go "Monster (path 1)"` | Only one path is available, so I must take it. |
| `turn-089` | `play "Undertow (proto)" on "Punch Construct"` | The enemy is going to Defend, so I have a free turn to deal damage. Undertow deals 7 damage, and I'll follow up with Strike and the Explosive Ampoule for a total of 23 damage. |
| `turn-090` | `play "Strike" on "Punch Construct"` | The enemy is going to Defend, so I can safely deal damage. Strike for 6, then I'll use the Explosive Ampoule for 10 more. |
| `turn-091` | `use potion "Explosive Ampoule" on "Punch Construct"` | The enemy is going to Defend, so I can safely use the free 10-damage potion to chip it down to 32 HP, then play Song of Pearls to set up Block for next turn. |
| `turn-092` | `play "Song of Pearls (proto)"` | The enemy is defending so I don't need Block now; play Song of Pearls to set up passive Block for future turns when Plans are carried out. |
| `turn-093` | `end turn` | No energy remains; the enemy is going to Defend so no Block needed this turn. Song of Pearls is set up for future turns. |
| `turn-094` | `play "Defend+"` | Block 8 of the 10 incoming damage (5x2), then set up Kurage's Oath for 10 damage next turn and use Strike to chip the enemy's 10 Block. |
| `turn-095` | `play "Kurage's Oath (proto)+" on "Bake-Kurage"` | No Defend in hand, so I'll take the 10 damage. Set up Oath for 10 damage next turn, then Battle Plan for extra energy, and Strike to chip the enemy's 10 Block. |
| `turn-096` | `play "Strike (1)" on "Punch Construct"` | No Defend in hand, so I'll take the 10 damage. Use both energy on Strikes to break the enemy's 10 Block and deal 2 HP damage, leaving it at 30 HP for the Oath next turn. |
| `turn-097` | `play "Strike" on "Punch Construct"` | Break the remaining 4 Block and deal 2 HP damage, bringing the enemy to 30 HP. The Oath next turn will deal 10 more, leaving it at 20 HP to finish. |
| `turn-098` | `end turn` | No energy remains; I'll take the 10 damage and the Oath will deal 10 next turn, bringing the enemy to 20 HP. |
| `turn-099` | `play "Strike (1)" on "Punch Construct"` | The enemy is at 20 HP and I have 3 energy. I'll play all 3 Strikes for 18 damage, bringing it to 2 HP. I'll take 12 damage (14 minus 2 Block) and go to 4 HP, but next turn I only need 2 damage to finish it. |
| `turn-100` | `play "Strike" on "Punch Construct"` | Bring the enemy to 8 HP, then play Defend for 2 more Block (4 total). I'll take 10 damage (HP 6) but only need 8 damage next turn to finish it. |
| `turn-101` | `play "Defend (1)"` | Gain 3 more Block for 5 total, reducing the 14-damage hit to 9. I'll be at 7 HP next turn and only need 8 damage to finish the enemy. |
| `turn-102` | `end turn` | No energy remains; 5 Block reduces the 14-damage hit to 9, leaving me at 7 HP. Next turn I only need 8 damage to finish the enemy. |
| `turn-103` | `play "Strike" on "Punch Construct"` | The enemy is at 8 HP and going to Defend. Strike for 6 brings it to 2 HP, then Slack Water for 4 kills it. |
| `turn-104` | `play "Slack Water (proto)" on "Punch Construct"` | The enemy is at 2 HP; Slack Water deals 4 damage and kills it. |
| `turn-105` | `` |  |
| `turn-106` | `choose "Add a card to your deck"` | Adding a card is more impactful long-term than 15 gold. |
| `turn-107` | `choose "Ambush"` | 12 damage as a plan is stronger than my current Oath+ (10), giving me a better finisher for future fights. |
| `turn-108` | `proceed` | The card reward is already taken; only gold remains, so proceed to continue. |
| `turn-109` | `go "Monster (path 1)"` | Only one path is available, so I must take it. |
| `turn-110` | `play "Slack Water (proto)" on "Damp Cultist"` | Both enemies are buffing, so I have a free turn. Deal 4 damage and apply Weak to the bigger Damp Cultist, then use remaining energy on Strike and Battle Plan. |
| `turn-111` | `play "Strike" on "Damp Cultist"` | Both enemies are buffing so I have a free turn. Deal 6 damage to the already-weakened Damp Cultist, then set up Battle Plan for extra energy and draw next turn. |
| `turn-112` | `play "Battle Plan" on "Bake-Kurage"` | Both enemies are buffing so no Block needed. Set up Battle Plan for extra energy and draw next turn, which I need badly at 7 HP. |
| `turn-113` | `end turn` | No energy remains; both enemies are buffing so no damage incoming. Battle Plan will give extra energy and draw next turn. |
| `turn-114` | `play "Defend (1)"` | I'm at 7 HP and facing 10 total damage. I need both Defends for 10 Block to survive, then use remaining 2 energy on Undertow (10 dmg due to Weak) and Strike (6 dmg) for 16 total damage. |
| `turn-115` | `play "Defend"` | I need 10 Block to survive the 10 damage (9+1). With 5 already, this Defend gives the second 5. Then I'll use 2 energy on Undertow (10 dmg due to Weak) and Strike (6 dmg) focused on the Damp Cultist. |
| `turn-116` | `play "Undertow (proto)" on "Damp Cultist"` | 10 Block covers the 10 incoming damage. Undertow deals 10 to the Damp Cultist (Weak), reducing it from 39 to 29. It has Ritual 5 so I need to focus damage on it. |
| `turn-117` | `play "Strike (1)" on "Damp Cultist"` | Focus damage on the Damp Cultist (Ritual 5) to bring it to 26 HP. 10 Block covers the 10 incoming damage. |
| `turn-118` | `end turn` | No energy remains; 10 Block covers the 10 incoming damage. Next turn I need to set up plans and deal damage before the Ritual Strength buffs make their attacks stronger. |
| `turn-119` | `play "Defend+"` | I'm at 7 HP facing 17 damage. I need maximum Block: Defend+ (8) + Defend (5) = 13 Block, taking only 4 damage. Then use last energy on Strike to chip the Damp Cultist. |
| `turn-120` | `play "Defend"` | I need 13 Block (8+5) to reduce the 17 damage to 4, leaving me at 3 HP. Then use last energy on Strike to deal 6 damage to the Damp Cultist, bringing it to 20 HP. |
| `turn-121` | `play "Strike" on "Damp Cultist"` | 13 Block reduces the 17 damage to 4, leaving me at 3 HP. Use last energy on Strike to deal 6 damage to the Damp Cultist, bringing it to 20 HP. |
