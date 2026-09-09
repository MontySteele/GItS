Status: RECORD (was OPEN, no pick; the defaults it names were applied; moved 2026-09-08 under R267)

# Kokomi round 29: Slack Water's two halves split by body count as built; Breakwater's held-count was never separable above its base; one lane lost to a renderer storm in the Punch Off event

Written 2026-09-08, late morning. Two blind Opus seats, natural draft, on
`0.2.3041+proto` (main `90c0bfc2`), the first build with `EB-685` (pool pass
five: Breakwater counts the Plans the Bake-Kurage is holding, Slack Water's
Plan is a Dusk Plan, Night Watch retired, Scout Ahead's face says "this one
included, in any order"). Records:
`review/qa/kokomi-round-29-2026-09-08/opus-lane1-natural.md` (219 acts,
died at the Kin) and `opus-lane2-natural.md` (54 acts, the game died
entering the Punch Off event at floor 7). Prototype stage, Guardrail 7.

## 1. The hypothesis

"A seat holding Breakwater counts the Plans the pet holds at end of turn
against the Block paid and they agree at least once above 5; a seat with
Slack Water in the starter says when its Dusk Weak landed relative to the
swing and chooses between the halves by the number of bodies at least once."

Half met. Slack Water's halves were chosen by body count in both lanes, and
its Dusk Weak landed before the enemies acted the one time it was written.
Breakwater's count never rose above 5 in a separable case, because lane 1
never wrote two other Plans before it and lane 2 never saw the card.

## 2. The reads

**1. Breakwater.** Lane 1 wrote it three times. Fight 7 turn 3, alone on
the jellyfish, badge "Plan 1": paid 5, which is 5 plus 3 times zero others,
and the seat concluded correctly that it does not count itself. Fight 8
turn 3, written after Kurage's Oath: the expected 8 was inside 17 Block from
other sources and not isolable, and the seat says so instead of guessing.
Boss turn 3, alone again, consistent with 5. So the clause is in phase now
(a Plan written the same turn is held at Dusk) and was never paid above
base only because no separable turn held another Plan. The seat's verdict
stands as a design read: in its deck, holding no Block at all paid more
(Orichalcum's 6) than Breakwater's 5. What the screen owes: the badge
counts the Dusk entry among "Plans held" and the clause does not, and the
badge says "start of your next turn" for a Dusk entry (`EB-680`, already
open).

**2. Slack Water.** Lane 1 held it on nine turns and wrote it once, at four
bodies (fight 4 turn 1): the Dusk Weak landed on all four before the
attacks, the Casket answered each, and the answering 2 killed a body; "the
one turn where the card was unambiguously worth writing, and the body count
is the whole reason." Every single-body turn was face-up, for the 4 damage
and the Casket's 2, and at two bodies with one attacker also face-up. Lane
2 held it on four turns, played it face-up on all four, and priced the
Dusk half each time: at one body "ALL is one body minus 4 damage", and at
two bodies the face-up Weak had to land before Riptide's rider read the
debuff, which a Dusk resolve is too late for. The split is the one pass
five intended and both seats could state it.

**3. Defend.** Lane 1: the third energy's default, and under Orichalcum
worse than nothing; lane 2 (three fights): arithmetic. Unchanged.

**4. The safe-turn decision** (round 26's read) held: lane 1's best turns
were Ripple's doubled carry-out under Nereid's and a Plan ordering at the
elite; the write-or-play question carried every Plan card.

**5. The screen.** Lane 1 predicted damage to the point "six or seven times"
and names three misses: Sango Isshin's quarter-HP hit took Strength but not
Slow (`EB-693`); the Kin Priest lost 32 where the faces total 29,
unsourced; a 12 into 9 Block under Vulnerable 2 cost 3, which is the intent
already folding the player's Vulnerable, a reading the page could state.
Both lanes: whole blocks printed twice on some screens (`EB-694`).

## 3. What this says

Pass five did what it was built to do on the one face that reached both
seats, and the phase fix on Breakwater is correct in the one isolable case.
The card is still a 5-Block skill in a deck that writes one Plan a turn;
whether that is fine is a pool-density question the round-26 read already
holds, and no further rule or rate moves on one un-separable case. The
night's Kokomi line closes here: five rounds, three pool passes, the cap
retired, and the write-or-play question standing on every Plan card in
every record since round 25.

## 4. Where the screen and the outcome disagreed

- **The Punch Off event killed lane 2's game** at floor 7: a scene
  instantiate under the event's punch animation failed with a null renderer
  allocation, then logged 143 million particle errors, grew the process to
  3.2 GB and timed the bridge out; the health endpoint kept answering. The
  mod patches no instantiate; the event builds a visual-only combat room
  with Kokomi's static fallback visuals. `EB-692`, and `EB-691` for a lane
  watchdog on log growth so a seat is told the lane is dead instead of
  retrying for fifteen minutes.
- **Sango Isshin's big clause** ignores Slow and takes Strength. `EB-693`.
- **Blocks printed twice** on some screens. `EB-694`.
- **The badge and Breakwater disagree** on whether a Dusk entry is held, and
  on its timing. `EB-680`.
- Not ours: the intent folding the player's Vulnerable; 3 HP of the Kin
  Priest's turn-1 loss unsourced by the seat.

## 5. Rows and defaults

Minted: `EB-691`, `EB-692`, `EB-693`, `EB-694`.

Defaults applied (E): no pool pass six from this round; Breakwater stays as
built until a record shows it paid above base or a deck that never holds
two Plans is the norm. The next Kokomi lane is not scheduled until `EB-692`
is answered, since a natural act 1 reaches Punch Off often enough to cost a
lane. The cap stays retired (R266). [USER]'s act-1 run on the R261 Klee
build remains the next hands-on read owed, and Furina's five picks on PR
#443 are the open design line.
