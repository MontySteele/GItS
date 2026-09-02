Status: OPEN (round three; both seats played; the read and the picks at the end)

# Klee overhaul, round three: two seats on starter draft 3

2026-09-02. Round two was your own run (R237); round three is the seats on
what it ruled: Kaboom! is the plain 6, Ka-pow! is the cash button at 1
energy, Dig In is the starter's Spark sink, Jumpy Dumpty costs 1, Quick
Fuse grows before it sets off, and EB-279/280/282/283/284 are built. The
build is 0.2.1966+proto.dirty from PR #261, soaked clean over three fights.

Two blind act-one runs, each seat seeing only the printed screens:

| Seat | Seed | Actions | Fights | Stopped by |
|---|---|---|---|---|
| Opus | LBR1QNKDMDK0 | 99 | 4, the Skulking Colony elite among them | its action budget, 49/62 HP, boss not reached |
| GPT (Codex) | RKE3U57FRK9H | 82 | 4 hallway fights | the harness's blindness gate, after a tool event in its transcript; its four fight records stand |

Records: `review/qa/blindplay/klee-overhaul-r3-opus/record.md` and
`review/qa/blindplay/klee-overhaul-r3-codex/record.md` (with its wire).
Seat numbers are floors, not fun claims (Guardrail 7).

## 1. What both seats found

1. **The loop is on the table now.** Both name "cash it now or let it
   grow" as the tension that came up again and again, which is the
   question round one failed. Opus: "Every charge is worth +2 for waiting
   a turn, and waiting costs a full enemy attack." GPT: "whether to
   detonate immediately for damage, Spark, and survival or let Bombs grow
   for a larger later payoff."
2. **Growing almost never wins.** Both cashed the moment a fuse was in
   hand. Waiting happened only when no fuse was drawn (GPT, fight 3) or
   the enemy telegraphed a buff instead of an attack (Opus). Cashing pays
   damage, Spark and, through Dig In, Block; growing pays 2 next turn.
3. **Spark bootstrapping.** Dig In, Powder Charge, Fwoosh! and Bang Bang!
   sat dead until the first Ka-pow! went off. GPT: "hands that cannot
   start their own engine." Opus: Bang Bang! "sat unplayable in my hand
   across two entire fights, which for a card that prints cost 0 is a
   trap." Half of that is the blind render printing Spark-priced cards as
   cost 0 (EB-286); the other half is the design: no Spark at the start of
   a combat.
4. **Duck and Cover is dead once Dig In exists, and Dig In is automatic
   once Spark exists.** Both seats, independently. Three copies of Duck and
   Cover in the starter read as two too many.
5. **Bombs merge into one number, so the target is free.** Opus: "the deck
   wants one target and doesn't much care which." Neither seat found the
   merge on a card; Opus learned it "by gambling a card on it" (EB-287).
6. **Both seats won every fight they opened,** the elite included, and
   both called the play repetitive from fight three on: place, cash, Dig
   In, block with the rest.

## 2. Defects from the round

- EB-285: a reward face printed the raw `{Damage:diff()}` template on
  Sayu's Fuuin Dash, the one random-target Attack. Both seats' worlds.
- EB-286: the blind hand line prints Spark-priced cards as cost 0.
- EB-287: the Bomb tooltip reads like a debug string and never says bombs
  merge.
- EB-288: under Weak, the upgraded Ka-pow! kept printing 7 while the base
  copy printed 5, so one of the two faces is not reading the debuff.
- EB-262 and EB-263 reopened: the shop loses a bought card's name and
  prints no energy cost; the chest, a spent rest site and the enchant
  picker print nothing to choose. Their fixtures passed; the live shapes
  do not.
- Base-game text, not ours: Hardened Shell's number is the turn's
  remaining allowance while its sentence says 20; Ravenous is worded in the
  singular and every survivor eats.

## 3. Applied for round four (D, disclosed, yours to veto)

Bombs grow by 3 a turn instead of 2. A number, taken at its default and
run by the seats: the read above says the growth is worth less than the
Spark a cash pays, and 3 is the smallest move that changes the arithmetic
without touching a rule. EB-286 and EB-288 are fixed in the same round so
the seats can read a Spark price and a debuffed face.

## 4. Picks

1. **Spark at the start of a combat.** (1) None; the first Ka-pow! turn is
   the engine's price by design, and round four's growth change is read
   first. **Default.** (2) Klee starts every combat with 1 Spark, so a
   Spark-priced card in the opening hand is live.
2. **A long fuse.** (1) No rule; growth alone is the reason to wait.
   **Default**, until round four says growth at 3 is still never taken.
   (2) A Bomb that has grown at least once pays 1 extra Spark when set
   off. A rule in the brief's list, so it would be a play by you.
3. **Duck and Cover.** (1) Three copies stay; the seats' "dead" is Dig In
   doing its job. **Default.** (2) Two copies, and a third Kaboom! in the
   tenth slot.

The rules stand, so no run of yours is owed by the gate; the seats drive
round four. If you want to play the growth change yourself, the build will
be the deployed one when round four lands.
