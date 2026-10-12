# Furina and Varka wave, 2026-10-12

**What ran.** Ten whole-run Sonnet seats at A0 on build 0.2.4994 (`main` at b390ff0d). The build includes:
- Varka's Block ruling (#1126): Rippling Guard became "Gain 7 [10] Block. Apply your current element to an enemy.", and Stormward Stance became 4 [6].
- Furina's Against the Tide change (#1127): it now reads "If you Drained this turn".

Four seats played Furina (lanes 1 and 2, twice each) and six played Varka (lanes 3 to 5, twice each). In the first Varka pass the embark flag forced the Amber (Pyro) Knight on all three lanes. In the second pass the Knight was rolled, giving Electro, Cryo and Cryo.

The seat records, telemetry scripts (`furina_wave.py`, `varka_wave.py`) and offer output are in the session scratchpad. The base five's numbers are lane telemetry since 2026-10-05: 623 normal fights.

## Result

| Kit | Seed | End |
|---|---|---|
| Furina | 8V8Z166ZWWND | Floor 14, act-1 elite, after a forced elite at 20/78 |
| Furina | YWELZX9C8RY7 | Floor 24, act-2 elite, after a forced elite at 19/78 |
| Furina | 4QC1655UUQVZ | Floor 48, act-3 boss (Test Subject, third phase) |
| Furina | 8BNZHM344QEG | Floor 48, act-3 boss (Test Subject, second phase) |
| Varka (Pyro) | QP3UQ4D96KKW | Floor 48, act-3 boss (Queen) |
| Varka (Pyro) | ARXGHAD62N48 | Floor 48, act-3 boss (Aeonglass, 373/512 left) |
| Varka (Pyro) | E2L9GRCDJ92B | Floor 33, act-2 boss (Kaiser Crab) |
| Varka (Electro) | 1YNW5K1BFDQZ | Floor 48, act-3 boss (Test Subject) |
| Varka (Cryo) | 7GR0LHERKUTL | **Won**, 42/94 HP |
| Varka (Cryo) | DCY36V6LYW8Y | Floor 48, act-3 boss (Aeonglass, 190/512 left) |

The base five's baseline on A0 was 0 wins of 5, all dying in act 3 (`review/records/base-five-baseline-2026-10-05.md`).

**Normal fights, median by act (1 / 2 / 3):**

| | Damage a turn | HP lost | HP lost, after drained HP returns |
|---|---|---|---|
| Base five | 19.0 / 30.2 / 38.6 | 9.8 / 15.5 / 10.3% | 7.6 / 13.5 / 10.0% |
| Furina | 18.7 / 32.8 / 63.8 | 14.1 / 30.1 / 17.6% | 9.0 / 9.6 / 9.4% |
| Varka | 20.0 / 27.0 / 44.1 | 5.0 / 9.2 / 13.3% | (same) |

Both kits sit within the base five's band, except Furina's act-3 damage, which is 1.65 times theirs.

## Varka

- **Pyro's Strength and Exhaust do not carry a deck.** The Pyro cards were offered 54 times and taken 7 times:
  - Stoke the Flames 1 of 16.
  - Ember Cleave 0 of 13.
  - Kindled Edge 0 of 4.
  - Blazing Charge 1 of 6.
  - Ashen Oath 2 of 5.
  - The 2026-10-12 round had taken 2 of 40.

  In the three forced Pyro starts, Pyro cards were 7 to 13% of plays. One of those runs played none of the Pyro pass cards and switched element 5 times a fight. Median peak Strength per fight was 0 to 1.5. The one 15-Strength fight was in the Cryo win, and that Strength did not come from Pyro cards.
- **Anemo is the plan, not the glue.** In every run, Anemo cards were 15 to 39% of plays and 15 to 48% of damage. Adding Swirl damage, Anemo plus Swirl made 22 to 66% of his damage. The main element's own cards were 10 to 20% of plays. "Half Anemo, half whatever element pieces you saw" is what every seat drafted, and it worked: 5 of 6 runs reached the act-3 boss.
- **Switching.** Element switches per fight ran from 1.1 to 5.0. The highest was lane 3's Cycle of Seasons deck, which stacked four copies (two upgraded) for 17 to 27 damage per switch and cleared 70 to 95 HP in a turn. Telemetry records no Oath counts, so it cannot yet show whether switch and mono decks bank Oath at once. The telemetry fields are being added.
- **Block.** The new Rippling Guard was taken 8 of 14 times, against 2 of 50 before. Every death came on a boss turn short of Block: 8 against 36, 15 against 28, 13 against 49, and one hand with no Block card. One deck had lost its Defends to Pandora's Box.
- **Stormward Stance at 4:** taken 3 of 10. A seat that drafted it said it was "never worth its energy".

## Furina

- **Where her damage comes from.** Spend cards made 25% of her damage in act 1, 35% in act 2 and 31% in act 3; Bravura+ and Rising Applause were the top two sources. Her other own cards made about half. Her Salon (Crabaletta, Chevalmarin) made about 10%, and guest acts 3 to 7%.
- **Fanfare left at a fight's end, wasted because Fanfare resets:**
  - About 6 to 10 in normal fights, against a peak of 15 to 27.
  - 10 to 24 against elites and bosses.
  - Two seats named it unprompted: "Fanfare piled up to 43 with no outlet", and "wasted 32 against Louse Progenitor".
- **The swing is there.** Within a fight she drops a median 14, 30 and 18% of her HP, but ends about 9% down once drained HP returns. The early deaths came after forced elites at about 20 HP. The deep runs died to act-3 bosses with Block-poor, all-burst decks; one had about three Block cards.
- **The diversity batch is still barely drafted:** 3 taken of 32 offers. Bravura was taken 2 of 2 and Packed House 1 of 11. Leading Lady, Tutti!, Full House, Headliner and Ensemble Cast were not taken. The guest-star line was never built: Lynette, as a guest and as a Companion, was taken 0 of 14.

## What to change

1. **Varka Pyro paper.** Strength and Exhaust have now failed two rounds, at 9 of 94 offers taken. [USER] said Pyro's core is "up for grabs" if they don't work out.
2. **Varka Oath read, after the telemetry lands:** Oath peaks in switch decks against mono decks, and how many Uncommons and Rares a big total took.
3. **Furina Spend paper:** what a Spend looks like, and how big the Drain floor is, aimed at the wasted third of her Fanfare and the act-3 burst-or-die shape. Then a distinct payoff for the guest-star line.
4. **Screen fixes (BACKLOG):**
   - Crashing Waves silently spends Fanfare under 4.
   - Hymn's Repay preview is wrong after a Drain.
   - Vulnerable is not shown in Spend damage.
   - A boss shows "Frozen 1".
   - Sayu's random Swirl gives no warning on an enemy with no aura.
   - Sharpshooter's second hit is lost when a Melt removes the Pyro first.
   - Cycle of Seasons' damage has no line of its own.
