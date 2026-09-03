Status: OPEN (PR = [USER]; one pick in §6)

# Klee round eight: two runs, the spire cleared, and what the Splash does to the kit's one decision

One pick in §6, with a marked default. Everything else is a default, applied
and disclosed in §5.

Written 2026-09-04, overnight. Five Opus seats played two runs on lane 2 of the
round-8 build (`0.2.2301+proto`: R248's target-only Bomb and Grounded's Spark,
the Hexerei readers, the round-7b defaults, all arms on). Run one cleared act 1
and died on act-2 floor 7; run two cleared the spire, Aeonglass dead on round 5
at 36 of 69. The records are `review/qa/klee-round-8-2026-09-03/opus-act1.md`,
`opus-act2.md`, `opus-run2-act1.md`, `opus-run2-act2.md` and `opus-run2-act3.md`;
every claim below names one of them. This is the three-act read R248's rules
were owed before you play.

## 1. The runs in one paragraph

Run one (341 actions): the Waterfall Giant died on turn 6; act 2 opened with
Tender and Vital Spark, and at 2 of 62 HP the map offered one exit, an Elite,
with a rest site behind it. The deck's best line made 19 Block against 24
(`opus-act2.md`, the Decimillipede). Run two (582 actions, no fight lost): the
Ceremonial Beast on turn 6, the Knowledge Demon (379 HP) on turn 7, Aeonglass
(512 HP) on round 5 with two Splash turns of 127 and 232 damage
(`opus-run2-act3.md`, the boss). Sixteen relics, thirty-seven cards. The engine
was Sparks 'n' Splash, Chain Fuse and three Pop!s, Grounded paying 6 Block and
a Spark every turn, and Diona's double Cryo painting the Melt. The seat's own
verdict on the fights: Hard To Kill, Hardened Shell, Galvanic and Aeonglass's
Defend rounds each asked a different question of the deck, and the deck had
an answer to each.

## 2. What the round found

**Once the Splash lands, the kit's one decision is over.** Sparks 'n' Splash
pays the whole stack every turn and spends nothing, so banking is always
right and every Set off card "deletes my engine" (`opus-run2-act1.md`,
finding 2). Run two never detonated after the Power landed, and the seat
called Grounded "the best 37 gold in the run" because under the Splash its
condition is never false: 6 Block and a Spark every turn, unconditionally
(`opus-run2-act3.md`, finding 8). Ammo Scavenging, Chained Reactions,
Catalytic Converter and Run Away!'s conditional half go blank at the same
moment. R243 designed the echo so that holding pays; the seats say it pays so
well that nothing else does. Pick 1.

**A reaction multiplies one bomb of a Set off and the whole Splash.** Bomb 56
in three charges, Set off under a Hydro aura, dealt 70: Vaporize took one
charge of three. The Splash is a single hit, so the same reaction multiplied
133 into 232 (`opus-run2-act2.md`, finding 3; `opus-run2-act3.md`, finding 1).
The badge prints one number for both. And because the Splash repaints Pyro
every turn, one Cryo card only strips it; Diona's "Apply Cryo twice" is the
one card that strips and paints, and her no-damage preview from `EB-338` is
"the only text in the game that tells you an aura application with no damage
is a stripper". Barbara's Hydro was eaten by Klee's own Pyro the same way
(`opus-run2-act2.md`, finding 2): a Hydro companion is near-dead in this deck,
a Cryo one is the deck's best pick. `EB-321` widened; the companion reads carry
the note.

**Bombs jump off a dying host, and it is the rule behind EB-318.** Three
bombs on a dead Flail Knight reappeared split across two survivors, and a Magi
Knight came up carrying four (`opus-run2-act3.md`, finding 4). The rule is in
the power's header and on no card, badge or tip; two Mines on one enemy after
a double kill is the same rule seen in act 1. `EB-361`, default applied: the
tip says it.

**R248's rules read true.** The badge folds the enemy's Vulnerable in and says
so; Klee's own Shrink no longer touches a Set off; Grounded's Spark funds
Powder Charge and Dig In on a held turn (`opus-run2-act1.md` §(e);
`opus-run2-act3.md`, finding 8). The one seam the seats found: the Splash is
her hit and takes her Strength (89 with Strength 4 dealt 93), while a Set off
is the bomb's and ignores her debuffs. Both follow their text; the packet
notes it, the pick decides whether the Splash stays a hit worth caring about.

**Act 2 and act 3 tax the kit's shape, and that is the good part.** Tender
charges a Strength and a Dexterity per card, Vital Spark makes every Skill
Tainted, Sloth caps the hand at three, Hard To Kill caps every hit at 9,
Hardened Shell caps the turn at 20, and Aeonglass's Defend rounds turned 127
and 241 into 5 and 0 (`opus-act2.md`, finding 2; `opus-run2-act3.md`, finding
5). Each one asks whether the deck can change shape for a fight, and run two
did. The seats' complaint is only that the price of Tainted is printed nowhere
before it is paid (`EB-359`).

## 3. What the screens got wrong

Each is a row in `BACKLOG.md`, on this packet's branch or already on main.

- **The shipped Kaboom! and Duck and Cover in the arm's starter** (`EB-351`,
  built, PR #344). Neow's Large Capsule read the raw pool. Run one carried
  both for seventeen floors.
- **The Blazing Barrier badge's raw `{Left}` and its rider paying once per
  attack** (`EB-353`, built, PR #347). Rapid Fire's short hits (`EB-354`)
  were the seat double-counting Strength under Tender; retired.
- **A second Sparks 'n' Splash badges 2 and pays once** (`EB-358`).
- **Tainted's glossary entry never says what Tainted does** (`EB-359`).
- **The Bomb jump is unprinted** (`EB-361`).
- Widened: `EB-318` (the jump), `EB-321` (one bomb of a Set off, the whole
  Splash), `EB-328` (Dexterity, Strength and Vambrace fold into faces with no
  marker, and Vambrace prints its once-only 12 on every Defend), `EB-333` (a
  won run ends on the Architect and `game_over` with no screen saying won),
  `EB-350` (no HP on the map page; 149 and 744 gold unannounced; every
  card-changing grid capped at 25 rows, Spoils Map outside it three times).

Seen and not rowed, because they are the base game's: Touch a Mirror, the
Relic Trader and Whetstone change cards and relics without naming them
(`EB-323`'s family, already widened); Festive Popper's 1 against a Frog Knight
was its 9 into Block; Plating grants one less than it prints; the full heal at
the act boundary; Snecko Skull inert because Klee's pool applies no Poison;
Rosaria's Vulnerable clause needs the aura her Cryo is there to replace, a
companion-sheet note.

## 4. What the round did not test

No seat named Coven Errand, Witches' Circle or Alice's Introduction Magic
(`EB-326`), so the Hexerei window is still unread; run two took no Large
Capsule, so `EB-351`'s fix is unread live; the fixes in #344 to #347 and the
morning receipt are not on the installed build.

## 5. Defaults applied (D and E), disclosed

- **E:** your Klee run comes on the next deploy, which carries #344 to #347
  and the round-8 build; the rules gate is R248's, and the seats have read
  it. Kokomi's round-five read is a separate packet.
- **D:** `EB-361`, the Bomb tip carries the jump.
- **E:** rows minted on this branch as listed; four seat records and one
  death record committed beside the packet.

## 6. Picks

1. **What the Splash pays.** (1) *The largest Bomb on the enemy, not the sum:
   "At the end of your turn, deal Pyro damage to a random enemy equal to its
   largest Bomb." The stack keeps growing under it, a reaction still
   multiplies the one hit, and a Set off is again the way to cash the whole
   pile, so hold-or-cash stays a decision after the Power lands. On run two's
   boss board, 21/21/14, the Splash pays 21 a turn where it paid 56, and a
   Set off pays 56 plus the reaction* [default]. (2) Keep the sum as R243
   designed it: the Splash is the Rare payoff, the detonators are the game
   before it lands, and Grounded's unconditional turn under it is the hold
   archetype's reward. (3) The sum, but the Splash spends the stack, a Set
   off on a schedule; Grounded then never pays under it, which couples the
   two cards the seats liked most.

The number in (1) is a prototype number, D by the ladder, and builds on
round 9 with `EB-358`'s stacking answer; the seats read it before you do.
