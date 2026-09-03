Status: OPEN (2 picks, both design directions)

# Kokomi round four-c: three Opus seats, a death on floor 24, and what act 2 asked that the kit could not answer

Two picks, both design directions. Everything else is a default, applied and
disclosed in §5.

Written 2026-09-03. Three chained Opus seats played one run on lane 1 of the
build installed on 2026-09-02 (R243's numbers, the Fable card audit, the
Bake-Kurage's beats, Gorou's Personal, the Burst meter still fed by
reactions). Seat one played act 1 to the boss's door, seat two beat the
Waterfall Giant and five act-2 rooms, seat three died two rooms later. The
records are `review/qa/kokomi-round-4c-2026-09-02/opus-act1.md`,
`opus-act2.md` and `opus-act2b.md`; every claim below names one of them.
This is not the three-act read R244 asked for. Act 3 was never reached, and
the reasons are in §4.

## 1. The run in one paragraph

Twelve fights across 24 floors, no rest site in the last six. Act 1 was
clean: 80 HP at the boss's door, Kujou Sara, Dahlia and Rosaria drafted, a
Chiori bought. The Waterfall Giant fell in nine rounds for 8 HP to spare
after a Death Blow of 33. Act 2 opened with a Tunneler behind 32 persistent
Block, then three Exoskeletons under Hard To Kill 9, then two Bowlbugs and a
Slumbering Beetle whose intent rose by a printed Strength 2 every round,
12 to 28. The deck's block ceiling never moved off Defend+ 16 plus one card
at base, and Kokomi died at 2 HP with three Plans banked. Thirty-one Plans
were written across the run; the seats priced every morning off the planned
number and the morning was wrong, one way or another, on six of them (§3).

## 2. What the round found

**Bank or spend now has a printed price, and the trade works.** Seat two's
best sentence: against the Giant's Steam Eruption rising 3 a round, delay
had a visible cost and front-loading was right; against the Tunneler's
standing Block the fight was long and compounding was right; the same
decision, opposite answers, both derivable from the screen (`opus-act2.md`
§(a)). Feint, which prints its face and its Plan side by side, flipped
between the two fights and was the card every seat was happiest to draw.
That is the kit doing what draft 6 said it would.

**Act 2 attacks the deck's shape, and the kit's own defence does not
scale.** Seat two wrote it before dying was on the table: every act-2 turn
he blocked, he blocked with a potion or a banked Coral Bulwark, never with a
block card (`opus-act2.md` §(f)). Seat three took the one defensive card
offered and still died on the treadmill, because the deck's block ceiling
is a Defend+ and a base card while the Beetle's intent grows 2 a round
(`opus-act2b.md`, fight 12). The Plan layer answers act 2's damage questions
well, Hard To Kill and standing Block included; it has no defensive line at
all, and the starter's Defends are the card every seat said it never wanted
to play. This is the acts-2/3 depth question STATE says the Plan cards'
own design must answer, and it is pick 2.

**Nobody knows who deals Plan damage.** Seat two's favourite discovery was
that Plans keep their full number while you are Weak, because the morning
comes after the Weak expires (`opus-act2.md` §(a)). Seat three found the
opposite against a Strategic enemy whose Weak lands at the end of your
turn: "Plan: Deal 12 damage" and "Plan: Deal 5 damage" paid 9 and 3 the
next morning, both exactly times 0.75, with no screen showing the reduced
number before it happened (`opus-act2b.md` finding 3). Meanwhile enemy
Vulnerable does not multiply Plan damage (`opus-act2.md` §(c)5) and Fantastic
Voyage does not add to it. So Kokomi's debuffs apply to the Kurage's hits
and the enemy's do not, which is the wrong way round if the Bake-Kurage is
the one hitting. Pick 1.

**The Moon Overlooks the Waters removes the layer's only drawback.** "Plans
also happen NOW as you write them" for 2 energy was the most fun the kit
had and, stacked with Change of Plans, made 20 damage from one 1-cost card
in a turn (`opus-act2.md` §(d)). It is where the kit is most likely
over-tuned. Held, not touched, until an act-3 read exists (§5).

**Plans have no cap and three seats guessed one.** The buff prints the count
written, "Plan 2", then "Plan 3", and each seat read it as the capacity
(`opus-act2b.md` finding 5). The code holds no cap. A tip line closes it
(`EB-330`).

## 3. What the screens got wrong

Each is a row in `BACKLOG.md`, minted on this packet's branch.

- **The card face composes modifiers wrong** (`EB-328`). With Weak and
  Fantastic Voyage both up, Slack Water printed 3 and dealt 6; the face
  applied the Weak and dropped the buff, in the direction that says do not
  attack. Undertow's conditional face printed unreduced beside a
  Weak-adjusted Strike (`opus-act2b.md` findings 2 and 14).
- **The morning log is not the board** (`EB-329`). It prints the Plan's own
  number and never the Casket's follow-ups, six mornings running; it prints
  nothing when the Plan's kill ends the fight; an on-play firing under The
  Moon is filed under the start-of-turn heading; and the reaction line never
  names a consumed aura because the Casket's Hydro re-applies it inside one
  refresh (`opus-act2.md` §(c)4, `opus-act2b.md` findings 4 and 15). This
  supersedes the page half of `EB-317`, which round four called met.
- **An off-sheet card applies Hydro with nothing printed** (`EB-331`).
  Breakthrough, an Ironclad card from an event, put Hydro Aura 2 on three
  enemies, and the next Electro hit reacted with nothing on the screen to
  predict it (`opus-act2b.md` finding 6). R244 ruled the base Strike applies
  nothing because it prints nothing; the same reading covers every card
  outside the character's sheet, and I have applied it as the default.
- **The boss printed a billion HP** (`EB-332`). The Giant's phase flip
  rendered as `HP 999999997/999999999` for a whole turn, with the seat unable
  to tell won from lost (`opus-act2.md`, fight 9).
- **Three pages hide their outcome** (`EB-333`). The run-over page is one
  line and a floor number; "This or That?" granted Red Mask and Clumsy and
  printed "Proceed"; Dusty Tome granted Princess of Watatsumi+ without its
  face; and `skip` on a card reward neither finalises nor says the reward
  waits until you proceed (`opus-act2b.md` findings 8, 10, 11).

Seen and not rowed, because they are the base game's: block faces print
the Unmovable-doubled value on every card in hand, which is the game's own
"if played now" preview being right one card at a time; enemy powers are
printed in the player's second person; Slumber counts a slept turn as a
turn; Colorful Philosophers cannot be declined; and a 57 HP heal on
entering act 2 that no screen announced.

## 4. Fixes in flight, and what the round did not test

- **The Burst meter** climbed to 25 of 20 on seat two and sat at 5 of 20
  for seven rounds on seat three. The reaction grant is gated off under
  the arm on main since PR #321 (`EB-327`); the meter row vanishes from the
  page with it. Not on the installed build.
- **The Bake-Kurage's beats** (`EB-316`, `EB-317`) are Godot visuals the
  blind page cannot see. Their acceptance is your eyes-on; the log half is
  `EB-329` now.
- **Act 3 and The Insatiable** were never reached, and not for lack of
  budget: act 2 is 16 floors, and the deck died at floor 24. A second run is
  the default (§5), on the fix build.
- **Gorou's "this turn" wording and the Hardened Shell number** could not be
  re-checked; no shop offered Gorou and no capped enemy appeared after act
  2's first rooms.

## 5. Defaults applied (D and E), disclosed

- **E:** a second Kokomi run on the fix build, three chained Opus seats,
  each with 250 actions and a stop at its act's boss, as soon as the Klee
  lane frees and the build is redeployed. Your own run follows it, as R244
  set.
- **E:** The Moon Overlooks the Waters is held at its numbers until that
  run's act 3 is read.
- **D:** `EB-331`'s reading of R244, cards outside the character's sheet
  apply no element. You veto by striking the row.
- **E:** the six rows above are minted here; no id was minted by any agent
  tonight, so the numbers follow `EB-327`.

## 6. Picks

**1. Who deals Plan damage.** Today Kokomi's Weak reduces a Plan at the
morning, enemy Vulnerable does not raise it, Fantastic Voyage does not add
to it, and no line shows the reduced number.

  1. **The Bake-Kurage deals it (default).** The enemy's debuffs apply,
     Kokomi's own Weak and her attack buffs do not, and the Plan line
     prints the number it will deal against the enemy's current state. One
     sentence on the Plan tip. This keeps seat two's discovery true
     everywhere: being debuffed is a reason to bank.
  2. **Snapshot at writing.** The number you paid for is the number you
     get, whatever lands on either side before the morning. Simplest to
     print; it makes a Plan immune to the enemy's play, which is stronger
     than it looks against Strategic intents.
  3. **Status quo, printed.** Resolution-time against everything, and the
     Plan line reprints under Weak the way attack faces do. Cheapest;
     leaves the Vulnerable asymmetry as it is.

**2. Does the kit's own defence scale in act 2, or is that the Companion
layer's job?**

  1. **The kit's (default).** I design two defensive Plan payoffs for
     round five, in the Hexerei readers' build shape: one whose Block
     scales with the Plans carried out that morning, one on the Casket's
     side of the kit. Sheet rows, seats first, your play after.
  2. **The Companions'.** Leave the starter and the Plan cards as they are,
     and read act 3 of the second run before deciding; Dahlia and Coral
     Bulwark are the defence, drafted.
  3. **Numbers only.** Raise Defend's replacement, Song of Pearls and Coral
     Bulwark, no new shape. The seats say act 2 attacks the shape, not the
     size, so I do not recommend it.
