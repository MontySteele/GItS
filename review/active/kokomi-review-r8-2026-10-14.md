# Kokomi review, round 8, 2026-10-14

Seven blind Sonnet seats, whole runs at A0, on build 0.2.5523 (round-6 build,
round-7 display fixes, the controller Plans view). The seat records are in the
session scratchpad (`seats/archive/kokomi-r8-*`, packet
`kokomi-r8-packet.md`). Take rates come from `tools/offer_report.py
--character kokomi --since 2026-10-14T19:50` (80 card rewards, 14 shop offers).

## Result: 0 wins in 7

| Seed | End |
|---|---|
| 66J0EFD2AB6B | Died to Aeonglass (act-3 boss) on 30 of 512 HP, floor 48 |
| G56P1KBDXWYY | Died to Test Subject (act-3 boss), floor 48 |
| ZDG6F14WFXQH, ZS0LT5UFM6PL | Died to the act-2 boss (Knowledge Demon, The Insatiable), floor 33 |
| 523XLPDEQDT8, F2HZXY77RDNZ | Died in act 2 (Slumbering Beetle, The Obscura), floors 27 and 30 |
| CB6R7B8JETLU | Died to the act-1 boss (Lagavulin Matriarch) one hit short, floor 17 |

Round 6 won 1 of 8 and round 7 won 0 of 3. She still dies in act 2 most often.

## What wins

The same as round 6. Choosing between Kurage's Oath as a Plan or as Block now
was "a real decision every turn" (two seats). Stacked Plans won the best
turns: Opening Gambit then an area Plan dealt 36 to 57 to every enemy; Resolve+
then three planned hits dealt 32 to each Nibbit; Riptide plus three planned
Stings set up Suffocating Deep to end all three Decimillipede segments.
Riptide Ruin was taken 3 of 3 times, Kurage Vanguard 4 of 6, Bubble Ward 3
of 5.

## What loses: Block in long fights

Five of the seven deaths were the same: a long fight, HP worn down, and a final
hand with no Block card.
- **Final turns:** 29 incoming at 10 HP with no Block card (Aeonglass); 50
  incoming at 9 HP (Test Subject); 42 at 13 with 0 Block (Knowledge Demon); 20
  at 13 with no Block card (Beetle); 23 against 9 Block (Matriarch, with
  Dexterity −4 turning Defend into 1 Block).
- **Her Block cards are small.** Undercurrent Snare gives 5, Tidal Screen 7,
  Evening Watch 4 per attacker; under Frail these became 4 to 6. Shell of
  Sanctuary (6 Block, draw 1) is strictly worse than Kelp Wall at the same
  cost. Evening Watch was taken 1 of 6 times; Shell of Sanctuary 1 of 7.
- **A Plan's Block cannot save the turn it is written.** It lands at the start
  of the next turn. That is the design, so the fix is Block cards that pay
  **now** on Plan-heavy turns, not a rule change.

## Changes Claude builds (no pick)

**Cards.** Kokomi is at Prototype, so these are Claude's.
1. **Shell of Sanctuary** (Common, 1): "Gain 7 [10] Block. Gain 2 more for each
   Plan waiting." It pays most on the turn you plan the most, which is the turn
   she has least Block. It is no longer a worse Kelp Wall.
2. **Evening Watch** (Uncommon, 1): "Gain **6** [8] Block for each enemy
   intending to attack. Draw 1 card." It was 4 [6] per attacker, which is less
   than a Defend against one enemy.
3. **Undercurrent Snare** (Uncommon, 1): "Gain **8** [11] Block. Apply 2 Weak."
   Plan unchanged. It was 5 Block at Uncommon.
4. **Surging Shoal** (Uncommon, 2): "Deal 10 [13] Hydro damage to ALL enemies.
   Gain 10 [13] Block." No Plan. It was a two-cost Tidal Surge; now it is the
   one card that attacks and defends in the same turn.
5. **Feint** (Common, 1): its now-line becomes flat, "Deal 8 [10] Hydro
   damage." The Plan is unchanged. The now-line paid only when Plans were
   already waiting, which is when you play Feint as a Plan anyway. Taken 1 of 7.

Left alone: the starter, Mend's cap (ruled in round 6), Kurage Vanguard (4 of
6 taken; one seat's "never again"), Read the Field, Resolve of Watatsumi.
Watched for next round: Tidecleanse 0 of 7, Sangonomiya's Orders 0 of 6,
Endless Shoal 0 of 6.

**Text and display.**
6. **The Moon's "(6 will land)"** must show what Mend will actually heal on
   every screen. One seat saw "6 will land" and healed 0.
7. **Sucrose** shows "(no aura: no Swirl)" when the target has no element, the
   way Tenko shows "(no Sakura)". Two plays were wasted.
8. **One wording for when Plans happen:** "Plans carry out after your draw."
   The line "before you play anything" goes.
9. **Masterstroke's preview** printed 42 and dealt 63. Check whether the
   target's Vulnerable is in the preview, as round 6 item 9 required.
10. **At Water's Edge** vanished from the buff list mid-fight against Hunter
    Killer. Find out why and print it.

**Seat harness only.**
11. **Card-limit curses** (Sloth) show the count and which cards counted,
    including a Companion played by a Plan.
12. **A Power with no measurable output** no longer prints "Nothing this page
    can count landed off it."

## Next

Build 1 to 12 on one branch, then a Kokomi round of five seats. If her act-2
deaths do not move, the next review looks at her Rare Block and at the act-2
bosses' clocks (the Insatiable's Sandpit, the Knowledge Demon's heal).
