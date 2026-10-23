# Klee text audit, 2026-10-23

[USER], 2026-10-23, on the writing review and translation: "Agreed on all of
it!" The order is English first, kit by kit, in the Kokomi audit's format
(`kokomi-text-audit-2026-10-22.md`); the translation follows on the settled
English (`localization-2026-10-19.md`). Klee is first.

Read: every Klee card face, Ancient card, relic, power badge and keyword tip,
from `tools/player_text_census.py` and `tools/lint_text_conventions.py
--census`, against `docs/current/text-conventions.md`. Lengths are rendered
characters, as the lint counts them. Story events, Ancient dialogue and barks
are prose and wait for the story pass.

## 1. Length

Klee is in good shape: 85 cards, median 61, 20 over the 80 target, 8 over
100, none over the 120 ceiling. Her longest faces are long because of two
clauses repeated across carriers (sections 3 and 4), not because of
individual cards.

## 2. Fixes (no number or rule changes)

1. **Coven Errand prints the wrong upgraded number.** The upgrade adds 2 to
   the Bomb and the Companion bonus stays 4, so the upgraded card places 16
   but says 14. "Place a Bomb 10 [12] on an enemy, 14 if you played a
   Companion card this turn." becomes "Place a Bomb 10 [12]. If you played a
   Companion this turn, it is 4 larger."
2. **A single-target card names no target** (rule 3). "on an enemy" leaves
   Bombs Away!, Alice's Mine and Mine Toss, as Booby Trap and Pop! already
   read.
3. **One effect per sentence** (rule 1). Windblume Fireworks: "Set off ALL
   enemies, deal 10 [14] Pyro damage to them, and place a Bomb 8 [10] on
   each." becomes "Set off ALL enemies. Deal 10 [14] Pyro damage and place a
   Bomb 8 [10] on ALL enemies."
4. **No semicolons outside an either/or** (rule 14). Kitchen Alchemy: "ALL
   enemies lose 1 Strength. Exhaust every Status in your Hand; they lose 1
   more for each." becomes "Exhaust every Status in your Hand. ALL enemies
   lose 1 Strength, plus 1 for each Status Exhausted."
5. **"for each", never "per"; one spelling of spend-all.** Stoke the Fuse:
   "Spend all your remaining Sparks. Your largest Bomb on the enemy grows by
   5 [7] per Spark spent." becomes "Spend all your Sparks. Your largest Bomb
   on the enemy grows by 5 [7] for each Spark spent." (Fireworks Finale
   already says "Spend all your Sparks.")
6. **Grows "by"**, as on every other card. Chained Reactions: "your Bombs
   still waiting grow 3 [4]" becomes "grow by 3 [4]". The Bomb tip: "Grows 2
   at the start of your turn" becomes "Grows by 2 at the start of your turn".
7. **A bonus has its noun in the base's order** (rule 8). Sparkling Burst:
   "gain an additional 1 Energy" becomes "gain 1 additional Energy". Team
   Effort: "Deal 6 [9] Pyro damage, 6 additional damage if you played a
   Companion card this turn." becomes "Deal 6 [9] Pyro damage. If you played
   a Companion this turn, deal 6 additional damage." (the shape Sizzle
   uses).
8. **Two joined effects take "and"**. Flash Point: "gain 1 Spark, draw 1
   card." becomes "gain 1 Spark and draw 1 card." (fits only with section 3).
9. **Taste Test says what it counts.** "Deal Pyro damage equal to twice your
   Bombs on the enemy." becomes "Deal Pyro damage equal to twice the total
   size of your Bombs on the enemy." (the code reads the total).
10. **Simmer reads in order.** "Deal 6 [9] Pyro damage plus your largest
    Bomb's size, on any enemy, not setting it off." becomes "Deal 6 [9] Pyro
    damage plus the size of your largest Bomb. It does not go off." (119 to
    about 100, with section 4.)
11. **The Mine tip.** "A Bomb that also goes off when its enemy attacks you,
    and uses up the enemy's aura. Its plain Bombs stay. Any Set off spends it
    too." becomes "A Bomb that also goes off by itself when its enemy attacks
    you, using up the enemy's aura. The enemy's other Bombs stay." The last
    sentence goes because a Mine is a Bomb, and the Set off tip already says
    every Bomb goes off.

## 3. "If a Bomb triggered an Elemental Reaction this turn", on five carriers

The clause costs 50 characters and sits on Flash Point (118), Sizzle (117),
Perfect Timing (108), Aftershock (114) and Wait For It... The conventions
already admit the verb "react" ("a Bomb reacted this turn"), and the Bomb's
gold word keeps its tip.

- Flash Point, Sizzle, Perfect Timing: "If a Bomb reacted this turn, ..."
- Aftershock: "The first time each turn one of your Bombs reacts, place a Bomb
  that size on a random enemy."
- Wait For It...: "The next time a Bomb reacts this turn, draw 2 [3] cards
  and gain 1 Energy."

Each saves 20 to 25 characters. Sparkborne Magic already uses "react".

## 4. ", on any enemy," on seven carriers

Simmer, Favonius Escort, Half a Mountain, Hide Here!, Witch's Homework,
Treasure Map, Sparks 'n' Splash (and Albedo's Companion card) print "your
largest Bomb, on any enemy". The two cards that read only one enemy already
say so ("your largest Bomb on the enemy": Stoke the Fuse, Pocket Match). So
"your largest Bomb" alone can mean any enemy, and the clause can go.

## 5. "Companion card" against "Companion"

Klee prints "Companion card" on eight faces (Adventure Club, Alice's
Introduction Magic, Come Back and Play!, Coven Errand, Team Effort, Tag
Along, Little Hexenzirkel and its badge). Kokomi, Varka and the base game
say the type alone ("Whenever you play an Attack", "a random Common Inazuma
Companion").

## 6. "Bomb and Mine" against "Bomb"

The Mine tip says a Mine is a Bomb, yet Chain Fuse ("Each Bomb and Mine on
the enemy"), Alice's Recipe ("place a Bomb or Mine, your other Bombs and
Mines") and Alice's Masterpiece ("Bombs or Mines") name both, while Quick
Fuse, with the same effect as Chain Fuse in code, says "Each Bomb". A reader
can take the two-word cards to mean the one-word cards skip Mines.

## Picks

1. **Section 2's eleven fixes.** (a, default) build them all. (b) all but
   named ones.
2. **The reaction clause.** (a, default) "reacted" / "reacts" on the five
   carriers. (b) keep "triggered an Elemental Reaction".
3. **", on any enemy,".** (a, default) it goes from all eight; "your largest
   Bomb on the enemy" stays where only one enemy counts. (b) keep it.
4. **"Companion card".** (a, default) "Companion" on all eight. (b) keep.
5. **"Bomb and Mine".** (a, default) "Bomb" alone wherever the code already
   counts Mines as Bombs, checked card by card at build; a card whose code
   does not keeps both words. (b) keep both words everywhere.
