# Furina whole-run-seat round, 2026-10-10

This is the round [USER] ruled on #1036 (pick 2): "Definitely agree with testing whole-seat runs since we seem to have gotten token counts under control."
- It used the same four seeds and the Ironclad control, with one Sonnet seat per lane for the whole run.
- Build: 0.2.4765+next (`klee-next`). It carries the Spend build (#1016), Regina at the line and Navia at Uncommon (#1043), and High Stakes at 4 [3] (#1037).
- Embark `20261010-123915`.
- The fact packet, seat records and scripts are in the session scratchpad (`furina-fullrun-r1/`), which is gitignored.
- A Fable reviewer reviewed the round. The main session accepted the review with two corrections, given at the end.

## Result

| Seed | This round (whole-run seats) | Spend r3 (per-act) | Block round (whole-run) |
|---|---|---|---|
| JF391WG2NN0X | floor 27, Entomancer elite (entered at 28/85) | floor 33 | won |
| WDETA8RRGH98 | **won** | floor 33 | floor 33 |
| 0J427L1YQV15 | **won** | floor 42, Soul Nexus | won |
| TYXJLVY31QN7 | floor 48, the Queen | floor 33, Knowledge Demon | floor 17 |
| Ironclad control | floor 48, the Queen | floor 24 | floor 48 |

**Furina won 2 of 4.**
- None of her runs died to an act-2 boss. She won all three act-2 boss fights she reached, at 53.5 damage a turn against base's 58.4. Round 3 managed 28.6.
- Her normal fights ran 1.10× base damage a turn and 1.31× base Block.
- She lost 0.77× base HP after the curtain call.
- Base-five Sonnet seats at A0 won 0 of 5 (#927).

## Seat format: per-act seats play worse

| Seats | Furina wins | Control death floors | Control act-2 damage a turn |
|---|---|---|---|
| Whole-run (five rounds) | 6 of 18 | 48, 44, 48, 48, 48 | 33 to 41 |
| Per-act (Spend r1–r3) | 0 of 12 | 17, 48, 24 | 22 to 34 |

- Two-sided Fisher p = 0.057 on Furina's wins. The control moved the same way, and Varka went the same way too: 3 of 5 with whole-run seats against 1 and 2 of 5 with per-act.
- The build change between r3 and this round was barely played. Navia was seen once in a shop, Regina was passed once, and High Stakes was played in 4 fights. So the swing is format, plus noise.
- **The mechanism is HP carried between fights, not play inside them.** She entered act 2 at a median 92% of max HP, against 69% in r3; act 3 at 99% against 72%. Per fight, she is close to r3. A per-act seat starts each act without the plan the last seat was playing to.
- **Cost:** 1.53M tokens for the round (192k–369k a seat). That is 27.1 actions a fight, against r3's 26.8, so the price per fight is the same. Whole-run seats cost more only because they live longer. The largest seat stayed well inside the context window.
- **The three per-act Spend rounds are not a verdict on the Spend build.**

## Defects and legibility, checked in source

1. **Real.** The Drain chooser leaves out a card's enchantment. Its faces read 16 and 11 where Sharp and Instinct made the hits 18 and 22. The option cards are built without the parent's enchantments (`ModalChoice.cs:123-191`). Claude fixes this.
2. **Real, cause not found.** Neuvillette's first act read "no damage" against a plan of 21. Telemetry credits him only 18 over two acts. The forecast and the act read the same counter (`FurinaStage.cs:794-796`, `FurinaStageDirector.cs:699-708`). This needs a live repro before any C# change.
3. **Base-game rule or seat misread (no change):**
   - Quick Flourish+ shows 16 on the board and 14 on its face. The board number is the preview with her modifiers folded in, and the page says so.
   - Vigor is folded into every Attack's preview. That is the game's preview rule, and it is already footnoted.
   - "Fanfare lost to the end-of-turn discard": Fanfare never decays. The seat lost the cards in its hand, not the Fanfare.
   - Lane 1 died with 35 Fanfare it could not spend. It had passed five spenders at rewards.
4. **Page fixes:**
   - The game sometimes lists one power twice ("Weak 1", "Crab Rage"). The page will print it once, with a note.
   - The Strength tip will say it lasts "for the rest of this fight".

## Design

- **"Spend up to N" spends everything when the bank is below the cap.** It did that in 16 of 54 Spends. Prima Donna was in play in four of those fights, and in none of them would a chooser have changed the play. The card face already prints what it will spend. **No change.** It goes on the watch list for [USER]'s run.
- **No card numbers move.** The paper's overshoot line ("lower the caps by a third if clearly stronger than the Block round") does not fire: 2 of 4 against 2 of 4.
- `past_lost` rose to 11% of HP lost (from r3's 3.4%). Lane 3 accounts for most of it: it ran The Masquerade on purpose and won both bosses with it. Watch line only.

## What changes (Claude ships)

1. The Drain chooser's faces carry the card's enchantments, with a pin test.
2. A 0-damage stage act says why: "no damage (you lost no HP since your last turn)". Neuvillette gets a live repro.
3. A duplicated power row prints once.
4. The Strength tip reads "for the rest of this fight".
5. Telemetry adds Fanfare at the start of each turn, so Prima Donna and banking claims can be checked.
6. Check the "???" relic names after the fake merchant (lane 4).

**The main session's corrections to the review:**
- The review's default was whole-run seats for Furina only. The Ironclad control and Varka moved the same way, so the format effect is not Furina's. The default is now whole-run seats for every kit.
- The chooser and cap questions are dropped as picks. The round gave no evidence for either, so they are watch items for [USER]'s run.

## For [USER]

1. **Seat format.** **Default: whole-run seats for every seat round from now on.** Per-act is kept only for a run that would outgrow the context window. The alternative is per-act seats with the format effect treated as fixed noise.
2. **Next Furina round.** **Default:** the same five seeds, whole-run seats, this build unchanged, after your run, to take n to 8 before any number moves.
   - Pass: 4 of 8 pooled; act-2 bosses won with 55% or less of max HP lost after the return; the control at floor 48.
   - Fail: 0 or 1 of 4, with act-2 boss deaths entered at 80% HP or more. Then Standing Room Only to Uncommon and Wriothesley 5 [8] come back as picks.
