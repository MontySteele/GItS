# Klee and Varka: cleanup batch, 2026-10-14

GPT reviewed both kits for cards that are undertuned or do too much. Claude
checked each claim against `docs/prototype-surface.yaml` and the seat
records. Both kits are at Balance. So each change below is staged on a fresh
`<kit>-next`, graded by a suite, and promoted in one PR
(`operations/stage-gate.md`).

## Ruled 2026-10-14

[USER]: "On the Short Circuit change and similar cards - I think that I don't
want to print that much text on the cards themselves, but it might go into the
harness layer. Otherwise agreed on these."

**Klee (staged on `klee-next`).** Each prediction is graded by the next suite:

| Card | Today | Change | Evidence | Prediction |
|---|---|---|---|---|
| Lizard-Tail Gunpowder (C, 1) | "Place a Bomb 8. Draw 1 card for each of your Bombs that went off this turn." | "Place a Bomb 8. Draw 1 card." Upgrade unchanged (+3 size). | Taken 0 of 10 offers (`klee-fullrun-pass-round-2026-10-11.md`) | Taken in at least 2 of 10 offers |
| Taste Test (U, 2) | "...damage equal to twice your Bombs on the enemy. They do not go off. Add 2 Confiscated into your Discard Pile." | Exhaust replaces the two Confiscated. | 0 of 13 | Taken at least once in 13 |
| Exquisite Compound (U, 1) | "Move all your Bombs onto the enemy. Each grows by 4 [6]." | Each grows by **7 [10]**. | 0 of 15. Against one enemy it was a weaker Chain Fuse (9) | Taken in at least 2 of 15 offers |

These changes should not move the kit as a whole. Klee's suite runs should
still reach act 3 at base-five rates, with damage a turn within 15%.

The cost of the Taste Test change: Confiscated was fuel for Klee Can
Explain!. Taste Test was never taken, so that synergy was never seen.

**Flash Point is unchanged.** Nothing shows it is under or over, and its
Spark is Klee's currency.

**Varka (`varka-next`).**
- **Short Circuit, Kaeya and Barbara** keep their text. The silent switch of
  his current element goes into the seat page, not the cards, as you ruled.
  That is a harness change with no rule change, built now.
- **Tempest Charge** has Rising Gale's exact text ("Deal X Anemo damage. If it
  Swirls, draw 1 card."), at 1 Energy for 8 against 0 for 4. Its slot gets a
  new job: pick 1 below.

**Next review:** Glacial Edict against Deep Freeze. Both are 1-Energy
Uncommons that apply Cryo, Weak and Vulnerable. It runs once this batch has
suite data.

## Pick

1. **Tempest Charge's new job** (Uncommon Attack, 1 Energy):
   - **(a, default) Two blades:** "Deal 5 [7] Anemo damage twice." Each hit
     can Swirl, so one card can pay his Oath twice. His pool has no plain
     double hit of its own (Diluc's is a Companion), and it is the dual
     claymores.
   - (b) **Tempo:** "Deal 12 [16] Anemo damage. Costs 1 less for each Swirl
     this turn." A finisher after a Swirl chain.
   - (c) **Oath:** "Deal 9 [12] Anemo damage. Gain 1 Oath of your current
     element." Direct scaling. It may be too strong at Uncommon; the suite
     would tell.
