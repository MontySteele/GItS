# Furina text audit, 2026-10-23

The writing review, kit three (ruled 2026-10-23, `localization-2026-10-19.md`;
format: `kokomi-text-audit-2026-10-22.md`). Read on `furina-next` (after
the upgrade census), so the fixes land there and reach `main` with her next
promotion.

Read: every Furina card face, Ancient card, relic, potion, power badge and
keyword tip, from `tools/player_text_census.py` and
`tools/lint_text_conventions.py --census`, against
`docs/current/text-conventions.md`. Her live counters (Drained, Fanfare,
the Bow cues) are code-built captions and go with the translation keying
(`review/records/localization-code-text-census-2026-10-23.md`). Story
events and dialogue wait for the story pass.

## 1. Length

80 cards, median 58, 13 over the 80 target, 2 over 100 (Verdict of the
Oratrice 113, Arkhe in Balance 102), none over 120. The shortest kit.

## 2. Fixes (no number or rule changes)

1. **Let the People Rejoice says what it counts.** "Deal 2 [3] damage to
   ALL enemies per point." becomes "Deal 2 [3] damage to ALL enemies for each
   Fanfare spent." ("point" is printed nowhere else; Klee's Fireworks Finale
   says "for each Spark spent".)
2. **A targeted card names no target** (rule 3). Verdict of the Oratrice:
   "Choose an enemy. If its HP is no higher than your Fanfare, it dies.
   Otherwise, ..." becomes "If the enemy's HP is no higher than your Fanfare,
   it dies. Otherwise, deal damage equal to your Fanfare." (113 to about 96).
   Plot Twist keeps "Choose an enemy that intends to attack", which is a
   restriction, not a target.
3. **Two joined effects take "and".** Guest Star: Lyney: "Act: Drain 2, deal
   5 Pyro damage to ALL enemies." becomes "Act: Drain 2 and deal 5 Pyro
   damage to ALL enemies."
4. **Chevreuse prints her rule,** as Navia and Neuvillette do. Her face is
   only "Summon Chevreuse." (upgraded: "Also applies Weak."), so a reader
   learns what she does from the hover. It becomes "Summon Chevreuse.
   Whenever you Spend, apply 1 Vulnerable [and 1 Weak] to a random enemy."
5. **The base's timing word** (rule 9). Trial by Water, face and badge:
   "Until end of turn, whenever that enemy takes damage" becomes "This turn,
   whenever that enemy takes damage".
6. **A bonus has its noun** (rule 8). Full House: "it deals that much more."
   becomes "it deals that much additional damage."
7. **Fontaine Teardrop in the Repay tip's words.** "An unreturned Repay gains
   2 Block for each HP instead of 1." becomes "Any HP a Repay cannot return
   gives 2 Block instead of 1."
8. **The "oldest guest" tip counts seats.** "the one a fourth summon would
   remove" is wrong with Ensemble Cast or the Epiclese Season Pass (four or
   five seats); it becomes "the one the next summon on a full stage would
   remove."
9. **No semicolons in a tip** (rule 14). Flip: "Turn this card to its other
   face; it starts each combat on Ousia." becomes two sentences. Repay:
   "Regain that much drained HP; a Repay counts the HP it returns." becomes
   "Regain that much drained HP. A Repay counts only the HP it returns."
10. **One verb for paying Fanfare.** The tip says "Spend uses it"; the
    Fanfare badge says "Spend pays it". Both say "uses".
11. **No contraction on a face.** Casting Call: "If you can't, draw 2
    cards." becomes "If you cannot, draw 2 cards."

## 3. ", all you can", on five carriers

"Spend up to N, all you can" sits on Bravura, Soloist's Solicitation, Hold
the Stage, Tidal Flourish and Full House. The Spend tip already says it:
"Spend up to X pays X, or all you have if that is less." (rule 15: the word
carries the rule, the card prints the word). Without it: "Spend up to 18.
Deal 7 [9] Hydro damage for every 3 spent." and so on, 13 characters each.

## Picks

1. **Section 2's eleven fixes.** (a, default) build them all. (b) all but
   named ones.
2. **", all you can".** (a, default) it goes from the five; the tip carries
   it. (b) keep it, since "up to" alone might read as a choice of amount.

## Ruling, 2026-10-23

[USER]: "Agreed on all Varka, Furina, Yae and Shared fixes - these makes
sense to me!"

1. **Pick 1 (a): built.** All eleven fixes as written. Chevreuse's face is
   "Summon Chevreuse. Whenever you Spend, apply 1 Vulnerable [and 1 Weak] to
   a random enemy." (`FurinaStageLaw.ChevreuseLineVulnerable`, and
   `ChevreuseLineWeakUpgraded` on the upgrade); Verdict targets an enemy
   (`TargetType.AnyEnemy`), so "the enemy" stands. Trial by Water's badge
   and the seat glossary's Flip, Repay and oldest-guest rows follow.
2. **Pick 2 (a): built.** ", all you can" is gone from Bravura, Soloist's
   Solicitation, Hold the Stage, Tidal Flourish and Full House, faces and
   the Full House badge.
