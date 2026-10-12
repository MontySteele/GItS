# Do Sonnet seats hold up at A5 and A8? The base five, 2026-10-12

**Why.** [USER]: "I'm honestly not sure how well the Sonnet agents handle the higher ascensions, so it's probably worth a sanity check that they don't faceplant and crash here in act 1 or something."

**What ran.** One whole-run Sonnet seat per base character, on build 0.2.5032. Base characters carry no mod content. The seat records are in the session scratchpad (`asc/lane*/`), which is gitignored.

## Result

| Character | Ascension | Seed | Died | Actions |
|---|---|---|---|---|
| Silent | A5 | — | Floor 17, act-1 boss The Kin, entered after two forced elites | 343 |
| Ironclad | A5 | HUYW4THQN7CB | Floor 48, act-3 boss Test Subject (left at 64 of 200) | 646 |
| Necrobinder | A8 | — | Floor 31, act-2 elite Entomancer | 459 |
| Regent | A8 | CGQGZ40GDNE0 | Floor 33, act-2 boss Knowledge Demon (left at 226 of 399) | 587 |
| Defect | A8 | SLHL4JPYWF1R | Floor 48, act-3 boss Aeonglass | 777 |

**The comparison** is the A0 whole-run baseline (`base-five-fullrun-2026-10-10.md`): 0 of 5, every run dead in act 2, on floors 24 to 33. Its earlier per-act run reached floor 46 to 48. So base-five depth at A0 already swings by a whole act from seat play alone.

## What it says

- **No faceplant.**
  - Four of five seats passed the act-1 boss. Two reached the act-3 boss, deeper than any run in the A0 whole-run baseline.
  - No seat stalled, crashed or ran out of actions; all five ended on the death screen.
- **The Silent's act-1 death is the worst result here, and it is a real loss.** It was forced through two elites before The Kin. One run can't say whether A5 is that much harder for the Silent or whether it was this seed.
- **Ascension shows up in how the seats died:** Ascender's Bane and Greed, unremovable curses that took a hand slot all run; the Knowledge Demon's forced curses (Sloth capped a hand at 3 cards); and Aeonglass's growing Wither cards in a deck with no card removal.
- **One seat per character is too few to compare A5 with A8.** This check answers whether seats can play high ascensions, and they can. Klee and Varka's A5 and A8 seats now run against this table.

## What the seats said (base game, not ours)

- **Decisions that were real:** Vantom's Slippery, the Tunneler's Burrowed Block, kill order against the Knight and Scroll groups, Stomp at 0 cost after Attacks, and exact lethals against the Exoskeletons' 9-per-hit cap.
- **Screen quirks:**
  - Necrobinder: Unleash's preview disagreed with the outcome; Osty's reset to 1 HP each turn is not printed; and a 0-cost Flatten did not trigger Danse Macabre.
  - Regent: Sovereign Blade's printed damage changed (24, 21, 51) with no message.
  - Defect: a bare `play "Strike"` resolved to Momentum Strike+ once the plain Strike was gone, and one chained command silently dropped plays.

  These are base-game or bridge items.
- **Bridge:** after a rest site, `proceed` once returned "No proceed button available" and worked after a short wait. Lane 4 once returned "NO ANSWER: the game is up but slow".

## Next

Klee (A5, A8) and Varka (A5, then A8) are running on 0.2.5052 now.
