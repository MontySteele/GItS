# Kokomi r4b local-2026-09-02 census (turns 1-121, PARTIAL run)

## Top 5 findings

1. Block-now-vs-Plan-later ran HP from 64/80 to 7/80 by fight 6: the tester repeatedly ate hits on purpose to bank a Plan payoff, e.g. turn-058 "accepting the 8-damage 2x4 hit" and turn-099 "I'll take 12 damage ... and go to 4 HP, but next turn I only need 2 damage to finish it."
2. turn-024/025: "Doors of Light and Dark" printed NO options on first render. Tester guessed `choose "Light"`, got "nothing here is called 'Light'", and only on retry saw the real Light Door / Dark Door choice.
3. turn-067/turn-092: "The Clouds Like Waves Rippling" (2-cost power) was drafted at turn-067 and never played again; at turn-092 it sits in hand flagged "CANNOT BE PLAYED: you do not have enough energy."
4. turn-121 (last recorded turn): HP 7/80, Block 13, mid-fight vs. two Cultists (Calcified 41/41, Damp 26/51 with Ritual 5/Strength 5). Run unresolved -- session hit its context ceiling at turn 122 before the fight closed.
5. Plan-writing was a minority of turns (13 of 121): Kurage's Oath (proto)/+ x7, Battle Plan x6. Strike was the workhorse (25 plays); the potion Mazaleth's Gift sat unused in every fight's potion list.

## 1. Run shape

Six fights (HP as printed at fight start): Fight 1 (turn-004) Toadpole (1) HP 22/22, Toadpole (2) HP 24/24, no HP lost. Fight 2 (turn-028) Sludge Spinner HP 38/38, HP steady at 64/80. Fight 3 (turn-053) Seapunk HP 44/44, HP 57/80. Fight 4 (turn-070) Two-Tailed Rat (1) 17/17, (2) 21/21, (3) 19/19, HP 49/80. Fight 5 (turn-089) Punch Construct HP 55/55 + Artifact 1, HP 26/80. Fight 6 (turn-110) Calcified Cultist 41/41 + Damp Cultist 51/51 (both Empower intent), HP 7/80, still in progress at turn 121.

Map moves: turn-003 `go "Monster (path 3)"`; turn-023 `go "Unknown (path 2)"`; turns 027/052/069/088/109 all `go "Monster (path 1)"` (single path each time, per the tester's own reason). Event turns 024-026: "Doors of Light and Dark" -> Light Door taken (Upgrade 2 random cards, over Dark Door's Remove 1 card).

Rewards taken per fight (card drafted, quoted as printed): Fight 1 "Battle Plan" + potion "Dexterity Potion" + gold. Fight 2 "Song of Pearls (proto)" + gold. Fight 3 "The Clouds Like Waves Rippling" + gold. Fight 4 "Undertow (proto)" + potion "Explosive Ampoule" + gold. Fight 5 "Ambush" + gold ("more impactful long-term than 15 gold"). Turn-1 (pre-run) relic pick: "Phial Holster" over Hefty Tablet and Booming Conch. No rest/shop nodes appear anywhere in the 121 turns.

HP trajectory (quoted from prompt.md headers): "HP 64/80" (turn-004, turn-013, turn-028) -> "HP 57/80" (turn-053) -> "HP 49/80" (turn-070) -> "HP 26/80" (turn-089, turn-092) -> "HP 7/80" (turn-110, and still "HP 7/80" at turn-121, Block 13). The tester's own turn-121 projection would end that exchange at 3 HP, but the record stops before the enemy turn resolves.

Where the run stood at turn 121: mid-round-3 of fight 6 vs. the two Cultists, HP 7/80, Block 13, Energy 1/3, about to `play "Strike" on "Damp Cultist"`. No sealed record beyond this -- turn 122 refused on context size.

## 2. Plan usage

13 turns wrote a Plan onto the Bake-Kurage: Kurage's Oath (proto)/(proto)+ x7 (turns 5, 13, 33, 43, 70, 79, 95), Battle Plan x6 (turns 28, 35, 40, 57, 74, 112). Song of Pearls (proto), a passive power ("gain 3 Block" whenever a Plan is carried out), was played directly once (turn-092), not written as a Plan itself.

Sentences describing the next-morning payoff (quoted verbatim):
- turn-015: "Block the weakened 5-damage attack, then let the planned 7 damage bring the Toadpole to 2 HP next turn."
- turn-036: "Deal 4 damage with the last energy; the planned 10 plus Battle Plan next turn will finish the fight."
- turn-047: "No energy remains; 7 Block reduces the 14-damage attack to 7, and the planned 10 damage will kill the Sludge Spinner next turn."
- turn-073: "No energy remains; 10 Block reduces the 14 incoming damage to 4, and the planned 10 damage will hit all three rats next turn."
- turn-118: "No energy remains; 10 Block covers the 10 incoming damage. Next turn I need to set up plans and deal damage before the Ritual Strength buffs make their attacks stronger."

Block-now-vs-Plan-later tension (tester explicitly eating damage to bank a Plan or a kill-next-turn line):
- turn-058: "Battle Plan is queued for next turn, so I'll spend both energy on attacks now to drop the Seapunk to 20 HP and finish it next turn, accepting the 8-damage 2x4 hit."
- turn-095/096: "No Defend in hand, so I'll take the 10 damage." (twice in a row, banking on the Oath's planned 10 to close the gap)
- turn-099: "I'll take 12 damage (14 minus 2 Block) and go to 4 HP, but next turn I only need 2 damage to finish it."
- turn-100: "I'll take 10 damage (HP 6) but only need 8 damage next turn to finish it." This chain (turns 96-101) is exactly what drove HP from 49 down toward the 7/80 seen entering fight 6.

## 3. Legibility

- turn-024: "The screen offers no explicit options, but the title implies Light and Dark doors; I'll guess Light as the safer choice." The prompt.md for turn-024 has no options list at all under "Doors of Light and Dark" -- title only.
- turn-025 "What happened last time": "That did not work: nothing here is called 'Light'. What is on the screen: (nothing)" -- confirms the first render was genuinely blank; the real options (Light Door / Dark Door) only appeared on this retry screen.
- turn-092: "The Clouds Like Waves Rippling" prints "CANNOT BE PLAYED: you do not have enough energy" in-hand at 1 energy remaining -- the card drafted at turn-067 is still uncastable here and stays unplayed through turn 121.
- Every combat screen carries a standing caveat about card-copy numbering: "the copies are numbered in the order they are listed ... it is re-counted on every screen, so `(1)` names a different copy once one of them leaves your hand ... this page cannot say which is which" -- a structural legibility gap in the tool's own printout, not a tester error, present on every turn with duplicate card names (e.g. turn-004, turn-028, turn-070).
- No "(proto)" card ever produced a confused or contradicted read; "Slack Water (proto)", "Kurage's Oath (proto)", "Song of Pearls (proto)", "Undertow (proto)" were all used exactly per their printed text. No Companion-card reward screen appears in the turns sampled.

## 4. Cards

Play counts (by base name, copy-number suffixes merged): Strike 25 (most-played by far); Defend incl. Defend+ 20; Kurage's Oath (proto/proto+) 7 (all as Plans); Slack Water (proto) 6; Battle Plan 6 (all as Plans); Undertow (proto) 2; Song of Pearls (proto) 1; The Clouds Like Waves Rippling 0 -- drafted turn-067, held the rest of the run, never played (blocked by its 2-energy cost at least once, turn-092). Ambush drafted turn-107, not yet played by turn-121 (fight 6 still open). Potions used: Fortifier (turn-010), Dexterity Potion (turn-029), Explosive Ampoule (turn-091). Mazaleth's Gift is listed in every fight's potion pool and is never used in any of the 121 turns.

Drafted vs. skipped at rewards: drafted Battle Plan, Song of Pearls (proto), The Clouds Like Waves Rippling, Undertow (proto), Ambush (one per fight, always "Add a card to your deck" over gold/potion-only). No alternative draft options are printed in partial-notes.md itself; turn-001's relic pick is the only reward screen with named alternatives ("Hefty Tablet", "Booming Conch") skipped in favor of Phial Holster.
