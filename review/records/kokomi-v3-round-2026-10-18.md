# Kokomi v3 round, 2026-10-18

The round on Kokomi v3, card paper sec.6 (`review/active/kokomi-cards-2026-10-18.md`), ruled by the user:
"Makes sense! ... let's do both." It made two changes:
- Tideturn, Feint, Turning Tide and Shoal of Spears count Plans "not Stings or Wards";
- a new Uncommon, Unbroken Tide.

The seats were blind Sonnet seats at A0 on build 0.2.5880, drafting freely, and each answered two questions:
- did you play Stings at once instead of planning them?
- did you give up damage to prepare a particular future turn?

One more seat was given Unbroken Tide in its starting deck. Raw transcripts are not kept.

## Results

| Seat | Seed | End |
|---|---|---|
| 1 | TED63A9WLD6E | Floor 40, act 3 (Soul Nexus elite) |
| 2 | L3TP08JPKRSD | Floor 25, act 2 (The Obscura) |
| 3 | 37EYGXFL96DH | Floor 7, act 1 (Phrog Parasite elite) |
| 4 | T9EQN3RDANS5 | **Floor 48**, the final boss Aeonglass, at 57/512 |
| 5 | 0P39EB2FZASZ | **Floor 48**, the final boss Queen, at 288/400 |
| 6 | KTHGU34MLX8P | Floor 27, act 2 (Ovicopter) |
| 7, Unbroken Tide given | LFD3GZS4M1GN | Floor 48, the final boss Test Subject (second form) |

There were no wins. Three of the six free seats reached act 3, two of them the final boss, and seat 7 reached it too. The v2 round
had one win in five seats (`kokomi-v2-round-2026-10-18.md`).

Against the base five, normal fights, `tools/telemetry_report.py --character Kokomi --since 2026-10-18T12:30`:

| Act | Damage per turn, against base | HP lost, against base |
|---|---|---|
| 1 | 1.18 | 0.87 |
| 2 | 0.68 | 1.19 |
| 3 | 0.92 | 1.49 |

Act-2 damage fell from 0.91 in v2 to 0.68. These are 26 fights from four seats, so it is a watch, not yet a
finding.

## What played well

- **Stings are now played at once.** Every free seat played most of its Stings immediately: to finish an enemy
  left at 1 or 2 HP, to lay Hydro for an Electro reaction (seat 4's Sakura and Ring line decided about half its
  fights), to strip Vantom's Slippery, to stun a boss that turn, or into Hard To Kill's cap. Seat 5 never
  planned one. Seat 6 said why: "The count cards skip Stings, so a planned Sting never helped them." Planning a
  Sting is now a choice, for Breakwater or Battle Formation, which still count it (seat 4, The Insatiable).
- **Seats gave up damage to set up a turn, and it paid off:**
  - Seat 4 against the Tunneler, turn 3: took 11 and dealt no damage, planning Second Wave then Ambush. The
    doubled hit stripped its 32 Block and stunned it.
  - Seat 5 against the Slimed Berserker: planned Tide Wall instead of attacking. It landed as 59 Block, then a
    46-damage Coral Crash killed it.
  - Seat 1 against the Matriarch: planned Gambit and Undertide Lance, then dropped her from 96 to 45 the next turn.
- **Read the Tide carried a deep run without its Rares.** Seat 5's run rode Tide Wall, which reads the biggest
  attack a turn ahead, into Coral Crash. Coral Crash dealt 25.6 a play in act 3.
- Combos read clearly: Gambit, Second Wave, Feint+ and Tideturn+. Block-to-Stun on the Rock and Tunneler made good
  decisions.

## What did not

1. **Unbroken Tide was never offered** to the six free seats, out of about 320 Kokomi card offers. The card is in
   the installed build and in her pool (`KokomiOverhaulRoster.Slice()`). That is about a 2% chance for one Uncommon
   of 39, so it is most likely chance. Seat 7 was given one, and its own draft then offered and took a second copy, so the card is offered.
2. **Tidal Rebuke, Tidal Riposte and Shoal of Spears were not played**, and The Shape of Water wasn't either.
3. **Plans landing in Block.** Seat 6's Plans hit the Tunneler's Block for 21 of their damage. The warning is on
   the page but easy to skim.
4. **Grand Design is weak with Strikes and Defends in hand.** They have no Plan line (seats 1 and 6).
5. **Following Current looked broken.** It fires: 9 damage in one fight (`play-20261018-134806.jsonl`). But the
   seat page printed no line for it. **Fixed** in #1425: it now prints its own line.
6. **At Water's Edge read as once per enemy.** The rule is once a turn, on the first enemy hit. **Fixed** in the
   same PR, by rewording: "The first time each turn you deal Hydro damage, apply 1 Weak and 1 Vulnerable to the
   enemy hit."
7. Working as written, but surprised a seat:
   - Change of Plans isn't doubled by Nereid's Ascension, which doubles only at the start of your turn.
   - Treatise doesn't draw on Shoal Call, which is not a Plan card.
   - Vambrace's doubled Block shows already doubled.
8. **Turn 1 of fight 1 has no real decision** in four Strikes and Defends hands (seats 1, 2 and 5). The starter
   is unchanged by rule.

## What to change

- Watch act-2 damage in the next round. No number moves on one round.
- Unbroken Tide stays as written.
