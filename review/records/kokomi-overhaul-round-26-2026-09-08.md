Status: RECORD (was OPEN, no pick; the defaults it names were applied; moved 2026-09-08 under R267)

# Kokomi round 26: on a safe turn the competition is a face-up attack or the same card's own timing, never draw or filter; the decision that lives there is which two Plans, in which order

Written 2026-09-08, small hours. Two blind Opus seats on `0.2.3031+proto`
(main `a4c58922`), the first build with `EB-668` (Battle Plan's rider is +4
damage on the next face-up Attack, mod and sim agreeing) and the round-25
print fixes. Records: `review/qa/kokomi-round-26-2026-09-08/opus-lane1-competition.md`
(lane 1, six cards granted: Battle Plan, Read the Field, Feint, Scout
Ahead, Breakwater, Night Watch) and `opus-lane2-natural.md` (lane 2,
natural). Prototype stage, Guardrail 7. Both seats spent 240 of 240 acts and
reached the act-1 boss. Both rounds were interrupted for about half an hour
by this machine's `python` alias (the Windows Store launcher) blocking on
launch; each seat first wrote a record reporting a stall, then found the
lane alive, switched interpreter, finished, and rewrote the record with the
second Write declared. Nothing in the game was touched by the pause.

## 1. The hypothesis

"On a SAFE turn (no lethal, no threshold, incoming covered or absent)
holding three or more Plan-capable cards, a seat names at least one such
turn where it chose immediate draw, filtering or an attack over writing
another Plan, and says what the immediate half bought; and at least one
such turn where it wrote everything and calls that free."

**Competition** (lane 1): floor 17, nine fights, the Kin Priest at 29 of
190 when the budget ended; 17 of 80 HP. **Natural** (lane 2): floor 17,
nine fights, Soul Fysh at 136 of 211 at the budget; 17 of 80. Neither lane
died, stalled on a screen, or hit a refusal streak.

## 2. The reads

**1. Safe turns with three or more Plan-capable cards.** Lane 1 counted
seven, lane 2 three (of 41 turns; "the rest of the time the hand was
Strikes and Defends"). What competed with writing another Plan:

| | turns | a non-Block competitor | which |
|---|---|---|---|
| lane 1 | 7 | 5 | Strike, Strike, Flank, Flank (damage needed now: a kill, a summoner's status cards), Kyouka (a four-turn buff) |
| lane 2 | 3 | 1 | Slack Water's own face-up half (Weak before three telegraphed hits) |

The draw and filter halves never competed. Battle Plan was written every
time it was held ("its written form is the run's best single energy");
Read the Field's face-up 5 Block "competes for the same dead slot as
Defend" and lane 1 "never once made a decision off what its filter showed
me". Block never won a slot on a safe turn in either lane. What stopped
more writes was mostly not competition but the board: Flank's attacker
clause with no attackers, a Weak against non-attacking intents, Dusk Block
against nothing incoming. Lane 1: "on a safe turn, roughly half the Plan
lines in a typical hand are dead letters."

Where the seats did find the safe turn rich, it was in **which two Plans
and in what order**: Opening Gambit then a damage Plan (24 to each of two
bodies; 42 to one body, twice, "reproducible to the point"), Second Wave
then Read the Field (a printed 10 Block became 20) or then Battle Plan
(the draw doubled, the rider +8). Both seats call these the best moments
of the run and both computed them off the faces before committing.

**2. Battle Plan.** Five rider turns in each lane. Planned around in eight
of the ten (written the turn before for Feint's double condition, or to
land on a safe turn); once "for the draw" with the rider then aimed at the
largest Attack; once knowingly wasted into a 6-HP summon. Lane 2's line:
"on Feint it is a combo, on Strike it is a patch." The rider stacked
honestly with Kyouka (Riptide 17, Flank 16) and doubled under Second Wave
(Feint 13 or 21, dealt 21). Both seats over-counted once because the +4
folds into every Attack in hand (`EB-669`).

**3. Read the Field.** Face-up half chosen only when nothing else was
worth an energy; the filter decided nothing (lane 1). Lane 2 drafted it
for Second Wave's doubling and wrote it. **4. Dusk.** Night Watch was
written on a hit and on quiet turns alike, and never presented a decision:
"a good card that asks nothing" (lane 2); Breakwater "is Night Watch minus
the Weak plus 2 Block, and the Weak is worth more than 2 Block every time"
(lane 1). Both seats: Dusk Plans make Defend a dead slot. **5. Feint** is
still the rhythm card, and lane 2 learned by losing a Feint that a Dusk
Plan resolves too late to power it. **6. Tide Wall** was drafted by
neither; Treatise's once-a-turn cap was counted twice and paid exactly 1.

## 3. What this says

The cap stays retired, and the round-25 worry narrows again: on a safe
turn nobody writes everything for want of a competitor, they write the
Plans the board has not disabled, and the interesting decision is the
pairing and the order. The immediate halves of the draw and filter cards
are priced so far under their Plan halves that the choice GPT asked us to
find is not there; that is a pool question, not a rule. The next Kokomi
work is a pass on the pool (§5), not another rule.

## 4. Where the screen and the outcome disagreed

- **Feint printed 5 with a Plan carried out and dealt 10** (lane 2, fight 7
  turn 3, after War Council's carry-out, which drew nothing); correct on
  four other turns, each after a Battle Plan that drew. `EB-670`.
- **Where a single-target Plan lands.** Ambush's Plan went to the Kin
  Priest, third in the list; the list re-ordered on the next screen. The
  rule held (the Followers are Minions, and the page says never a Minion),
  but nothing marks the front body. `EB-671`.
- **A replacement summon kept the dead body's letter and full HP** (Fogmog's
  Eye with Teeth, lane 1): the game reuses the slot id. `EB-672`.
- **The hand fell to three-quarters twice at the Kin and the status line
  showed nothing** (Orb of Weakness, lane 1 boss rounds 3 and 7), where
  fight 2 printed Shrink -1 by name. `EB-673`.
- **Flank's Plan dealt 1 to two of three attackers** (lane 1, fight 8): the
  Inklets enter with Slippery, which cuts a damage instance to 1 until the
  body takes unblocked damage, and only the first body had lost its stack.
  Printed on the bodies; not read. No row.
- **Nineteen prepared points became 2** (lane 2, boss round 4): Soul Fysh
  bought Intangible behind an unnamed Empower intent. The base game shows a
  human the same icon; a kit that commits a turn early feels it more. No
  row, but a design note carried into §5.
- Smaller: the kill screen printed 25 HP and the rest site 16 (Constrict
  after the fight, `EB-676`); a card chooser needs `confirm` and does not
  say so (`EB-674`); the reactions box prints its definitions and then says
  none is reachable (`EB-675`); Kyouka under Glam's Replay ran twice as
  long rather than twice as hard (`EB-677`); lane 2's fight-2 Night Watch
  turn has 2 HP of damage its own reading cannot place, unreproduced.
- **The tooling pause.** `python` on this machine resolves to the Store
  alias, which blocked for hours; the seat brief prints that bare word.
  `EB-678`.

## 5. Rows and defaults

Minted: `EB-669` to `EB-678`, as cited above.

Defaults applied (E): the cap stays retired (R266 stands); no further
"competition" lanes. The next Kokomi step is a pool pass four, Fable's
design, on the four faces this round found dead or automatic: Read the
Field's face-up half (the filter decided nothing), Breakwater (dominated
by Night Watch), Scout Ahead's Plan (never written in either lane), and
Night Watch's rate (4 Block, a Weak and the Casket's 2 for one energy at
Dusk, no face-up mode, "asks nothing"). Battle Plan is kept as built.
The design note from lane 2's boss: a Plan kit pays for anonymous buff
intents more than a face-up kit does; whether Kokomi should carry a card
that reads an enemy's next buff is a pass-four question, not a rule. After
the pass, a natural round 27 on its build. [USER]'s own act-1 run on the
R261 Klee build is still the next hands-on read owed.
