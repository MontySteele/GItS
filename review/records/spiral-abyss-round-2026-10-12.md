# Spiral Abyss round, 2026-10-12

First seat round on the Spiral Abyss mode (#1150, #1152, #1155), build 0.2.5073,
ascension 0. Three Sonnet seats: one solo Klee (lane 1) and a co-op pair, Klee
hosting (lane 2) with Varka (lane 3), seed RH1JZ3EWSQUJ. The pair was stopped by
the coordinator at the end of act 2 on the owner's instruction (the run was on
course for about two hours per act). Raw records are seat transcripts, not kept.

## Results

| Seat | Result | Blessings (act 1 / 2 / 3) | Shadows on the enemies |
|---|---|---|---|
| Solo Klee, seed QSH6HQ2M64YK | Lost at the act-3 boss (Test Subject, phase 2), floor 48, 717 actions | Fateful Fortune / Moonlit Rest / The Ley Line | Riptide in act 1 (others not recorded by the seat) |
| Co-op Klee + Varka | Beat The Insatiable (act-2 boss) on round 13; stopped on the act-3 map, floor 31. Klee 20/82, Varka 17/99 | First Strike / Fateful Fortune / (not reached) | Fatui Skirmishers (act 1), Abyss Herald (act 2) |

Floor 48 solo is the same depth as a normal A0 Klee run (`kit-ascension-check-2026-10-12.md`).

## What played well

- **Passing a Shadow is a real choice.** The solo seat chose by the Shadow it
  would hand over, not only by the Blessing: Fateful Fortune in act 1 because
  "the two enemy-side Shadows I passed were the mild-looking ones", Moonlit Rest
  in act 2 because it "avoids The Clock".
- **The Ley Line feeds reactions.** With an Electro act, Klee's Pyro Tinder Toss
  Overloaded aura-wearing Cubex twice in one fight.
- **Fateful Fortune is shared in co-op as intended**: when the party took it,
  both players' Max HP rose by 12 (Varka 80 to 92).
- No crash in either run; the choice page appeared over Neow and the act-2
  Ancient on all three lanes.

## What did not

- **Riptide is the dangerous Shadow, as the owner predicted.** At the act-1
  boss the Kin Priest's Strength went from 1 to 8 by turn 7 on unblocked hits;
  the seat won at 24 HP. Watch it, no change yet.
- **The co-op vote is invisible.** Each seat thought a Blessing pick was a bug:
  "I chose Crystallize ... First Strike and the Fatui Skirmishers shadow showed
  up instead"; "I chose Resonance but got Fateful Fortune". Both were split
  votes resolved by the host's draw, working as built, but the page never says a
  vote happened or how it ended. Fixed in the batch below.
- **The co-op chest bid reads as a wrong item.** "Took: Tungsten Rod" gave
  Lasting Candy; "Took: Red Mask" gave Oddly Smooth Stone. That is the game's
  co-op relic split, not ours, but the page claims "Took". Fixed below.
- **First Strike may never fire.** Klee's seat saw no doubled Attack in 12
  fights; Varka's seat believed its first Strike doubled but saw a Fury hit for
  10 only. The check counts attacks already started this combat, and may count
  the current one. Being settled from the game source below.
- **"Crystallize" collides with the reaction.** The page's glossary explained
  the Crystallize *reaction* under the Crystallize *Blessing*. Renamed to Jade
  Shield below.
- **"What you played" lists the partner's cards** on both co-op pages.
- **Co-op seats are slow, mostly from waiting.** Each co-op seat spent about 75
  of 99 minutes inside `wait`, against 0 for the solo seat; 17 and 23 of those
  waits ran the full 100 s with nothing moving, often on both lanes at once on
  screens where neither was blocked (shop, chest, rest site, Battle round 1).
  `wait` now returns at once when nothing waits on the partner (#1157, merged).

## What to change

1. Merged: #1157, `wait` returns at once when the seat is not blocked.
2. In one batch PR: First Strike fix, the vote result on the page, the chest
   bid wording and result, the partner's plays filtered from "What you played",
   Crystallize renamed Jade Shield.
3. Next co-op Abyss round after that batch deploys, to read the vote and
   First Strike live. Grow both pools to about 16 each after it (plan line from
   the ARAM census).
