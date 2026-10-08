# Co-op notes, 2026-10-02: Klee to Balance, Varka's Knights and Electro, Neuvillette

Status: RULED 2026-10-02.

[USER]'s co-op run reached the final fight: "it went much better than the
seats did." Klee: "Klee seems pretty well good to me! I'm comfortable moving
her to balance." Varka "seemed very fun, and had a trivial time generating
massive amounts of block and card draw, but my friend never saw any of the
Electro payoffs for discarding cards."

## Already being built (ruled in [USER]'s notes, no pick)

- **Jumpy Dumpty loses Innate.** "I think that's why seats keep getting chip
  damage hit on round one."
- **Barbara: Wellspring Hymn gains Exhaust.**
- **Amber: Explosive Puppet** becomes "Enemy loses 3 Strength this turn. The
  next time an enemy attacks you, deal 8 Pyro damage to ALL enemies." This
  replaces "take 3 less damage".
- **Card rewards:** one card sometimes lands off screen. The cause is being
  traced.
- **Element wording on every card:** "say if it does an element and also
  apply the symbol to the card." This reverses your 2026-09-01 ruling, which
  had the gem replace the sentence (`docs/current/text-conventions.md` line
  117). There are 64 element cards. Of these, 31 never name their element.
  The wording becomes:
  - "Deal 6 [Pyro] damage." for a hit;
  - "Apply [Hydro] to an enemy" or "to ALL enemies" for an aura with no hit.

  The gem, which already exists (`Vfx/ElementBadge.cs`), is extended to the
  seven cards that only Swirl (Anemo) and to Geo cards. Geo's icon file
  exists; Geo got no gem before only because it leaves no aura.
- **An art pass for the 132 cards without art of their own:** 65 Varka, 40
  Kokomi, 12 Klee, 9 Furina, and the rest Ancients and companions
  (`tools/art_coverage.py`). The main session picks one picture per card, as
  in the Kokomi pass.

## 1. What "Balance" means for Klee now

`operations/stage-gate.md` says a Balance landing re-authors a kit's rows
onto its real sheet. The cleanup deleted those sheets, and every card now
lives on `docs/prototype-surface.yaml` (legacy cleanup, pick 5). So the step
has nowhere to go.

**Pick 1.**
- **(a, default) A status change.** Klee's rows stay where they are. STATE
  marks her Balance. From then on, a change to a Klee number is your PR, as
  CLAUDE.md already says for shipped-sheet numbers. Two things fall due:
  - the sim's calibration is re-measured on her (cleanup, pick 5);
  - the `LAW.md` lines the rulings audit lists for her landing are struck,
    in a PR that is yours because it amends LAW (`rulings-deprecation-audit`
    §3; for Klee that is the Burst-meter lines).

  `stage-gate.md` is rewritten to say this. Jumpy Dumpty's change lands
  first.
- **(b) The full measurement law** (`EXPERIMENTS.md`: pre-registration,
  blind grading, stamps) for every Klee change from now on.
- **(c) Wait** until Kokomi or Furina is also ready, and move them together.

**Ruled (a), 2026-10-02.** [USER]: "Agreed on Klee - let's push the new
build with the most recent changes, give it one last playtest as a sanity
check, and if nothing turns up, then we move to Balance and clean up anything
stale in LAW or the queue / backlog." Nothing is built for this pick yet:
Klee moves to Balance only after that sanity playtest comes back clean.

## 2. Varka's Knights

A Knight is a Varka Companion card: one of the 17 with a colon in its name,
like "Lisa: Infinite Circuit" (`VarkaRules.IsKnight`). Nothing on a Knight's
face says it is one, and the shared Companions in his fourth reward slot
(Amber — Explosive Puppet) are not Knights. Eight cards are written against
the word:
- Knightly Guard and Knightly Strike (Commons);
- Grand Master's Order, Knights' Roll Call, Unwavering Banner and Assembly
  at the Cathedral (Uncommons);
- Charge of the Knights and The Order Answers (Rares).

**Pick 2.**
- **(a, default) Both.**
  - Assembly at the Cathedral becomes "Whenever you apply an element, deal 2
    [3] damage to a random enemy." That is your suggestion. It fires more
    often than once per Knight, so the number drops from 3 [4].
  - The other seven keep their Knight text, and every Knight prints a first
    line, "**Knight.**", the way a card prints Exhaust. The tooltip becomes:
    "One of Varka's Companions. Playing one makes its element your current
    element." Those seven are a Knight deck (Charge of the Knights, The
    Order Answers, Roll Call), and rewriting them would remove it.
- **(b) Retire the word.** All eight trigger on elements instead, and Roll
  Call adds "a random card of your current element".
- **(c) Only tag the Knights;** Assembly is unchanged.

**Ruled (a), 2026-10-02.** [USER]: "Agreed on both fronts - let's do a pass
over the Varka card pool to standardize the language around the existence of
this tooltip". Built on branch `coop-rulings`:
- Assembly at the Cathedral reads "Whenever you apply an element, deal 2 [3]
  damage to a random enemy." Same cost, type and rarity.
- Every Knight (all 17, the four starter-only ones included) prints
  "Knight." as its first line. This is a real keyword (`KleeKeywords.Knight`)
  that the game prints and hovers. It is not typed into the 17 faces. The
  printed line and every golded [gold]Knight[/gold] on other cards hover the
  same tip: "One of Varka's Companions. Playing one makes its element your
  current element (except Geo)." The exception is Noelle: she is a Geo
  Knight, and Geo keeps no Oath, so playing her does not change his element.
- The language pass found one stray form. Knights' Roll Call+ said "a Knight
  you choose" without the gold, so it had no tip; it now golds the word. The
  Order Answers' power badge golded only "Knight" in "Knights"; it now golds
  the whole word. Every other card that names Knights already used
  [gold]Knight[/gold] or [gold]Knights[/gold], and no Varka card uses
  "Companion" to mean a Knight.
  His three relics that say "starting Knight" (Knight's Commission, Boreas's
  Fang, Wolf's Gravestone) now gold the word and carry the same tip.

## 3. Varka's Electro discard cards

The package is three cards:
- Short Circuit (Uncommon): "Discard 3 [2] cards. Gain 2 Energy. Apply
  Electro."
- Chain Lightning (Uncommon): costs 1 less per card discarded this turn,
  8 [11] to ALL.
- Violet Storm (Rare): "Discard your hand", 8 [11] per card.

There is no Common, so a run sees them late or never. The element-identities
paper put discard at Uncommon on purpose: "Below Rare, no card gains Energy
without discarding a card for it". The fix is access, not the rule.

**Pick 3.**
- **(a, default) A Common enabler.** Charged Lunge (Common, "Deal 6 [9]
  Electro damage. Draw 1 card.") becomes "Deal 6 [9] Electro damage. Draw 2
  cards, then discard 1." It makes no Energy, so the rule holds, and it
  turns on Chain Lightning and the discard count.
- **(b) Also move Chain Lightning to Common,** swapping one Common up, so
  the payoff is seen in act 1.
- **(c) Leave it** and watch the next Varka run.

**Reopened: folded into a Varka element rebalance.** [USER]: "I don't think
that Varka's electro deck has any problem drawing lots of cards; the issue is
the payoff. Unless he has a payoff ties to discards that I missed, this
change doesn't do anything by itself." He then reopened Varka's Electro
design as part of a wider rebalance. Charged Lunge and Static Field are
unchanged on this branch.

His Block and draw ("trivial", by your read) are a watch item, not a pick.
Hydro's Block is meant to be big (identities paper §4). If the next run
reads the same, the Common Block numbers go to a pass.

## 4. The Neuvillette rare

"Neuvillette — Heir to the Ancient Sea's Authority" is a Rare Power, cost
1 [0]. Its whole text is "Elemental auras you apply last 1 extra turn." It
is a 5-star Rare that does nothing by itself.

**Pick 4.**
- **(a, default) Add a Hydro aura each turn.** "At the start of your turn,
  apply Hydro to a random enemy. Elemental auras you apply last 1 extra
  turn." That gives a free reaction partner every turn, for any kit.
- **(b) Cost 0 [0, Innate].** Only cheaper.
- **(c) Leave it.**

**Ruled (a), 2026-10-02.** [USER]: "Agreed on Neuvillette's a)". Built on
branch `coop-rulings`: the card reads "At the start of your turn, apply
[gold]Hydro[/gold] to a random enemy. Elemental auras you apply last 1 extra
turn." Each copy applies Hydro once.

## Picks

1. Klee's Balance: (a) a status change, with calibration and LAW strikes
   owed; (b) full measurement law; (c) wait and move kits together.
2. Varka's Knights: (a) Assembly on elements plus a printed "Knight." line;
   (b) retire the word; (c) tag only.
3. Electro discard: (a) Charged Lunge draws 2, discards 1; (b) also move
   Chain Lightning to Common; (c) leave it.
4. Neuvillette's rare: (a) plus a Hydro aura each turn; (b) cost 0; (c)
   leave it.
