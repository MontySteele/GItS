Status: OPEN (PR = [USER]; two picks in §6)

# Klee round seven-b: four Opus seats, three acts, and a death two floors below Aeonglass

Two picks in §6, each with a marked default. Everything else is a default,
applied and disclosed in §5.

Written 2026-09-03. Four chained Opus seats played one run on lane 2 of the
build installed on 2026-09-02 (R243's numbers, the Fable card audit, the coven
and the stand-ins with #317's emitter fix). Seat one played act 1 to floor 7,
seat two killed the Ceremonial Beast and opened act 2, seat three killed The
Insatiable, seat four died on floor 46 to the second act-3 elite. The records
are `review/qa/klee-round-7b-2026-09-02/opus-act1.md`, `opus-act2.md`,
`opus-act2b.md` and `opus-act3.md`; every claim below names one of them. This
is the three-act read R244 asked for, short of the act-3 boss.

## 1. The run in one paragraph

Twenty-two fights across 46 floors, 577 actions, one refusal. Act 1 ran HP 62
to 23 by floor 7 with no rest site reachable; a rest and Planisphere brought
it back, and the Ceremonial Beast (252 HP) died to The Big One quadrupling a
60 stack the seat had refused to spend for four turns (`opus-act2.md`, fight
10). Act 2 was the kit's best act: Hard To Kill 9 made bomb count the stat
that mattered, and The Insatiable died on round 5 to a Bomb 130 badge, an 87
stack under the 2 Vulnerable that Barbara's Frozen-on-a-boss substitution
applied (`opus-act2b.md`, fight 16). Act 3 attacked the deck's pieces rather
than its numbers: Galvanic taxed every Power, Paper Cuts made damage
permanent, the Soul Nexus elite was won at 9 HP, and the Mecha Knight (300 HP,
intents 25, 8, Defend, 40) killed her at 27 HP two floors below Aeonglass with
Dig In in hand, unplayable for want of a Spark (`opus-act3.md`, fight 22).
Eight of the twelve act-3 floors offered one node, both elites included. The
stand-ins appeared this time: Thoma, Barbara, Charlotte, Shinobu, Kirara,
Ayaka, Nicole and Diona's Shaken, Not Purred were offered or drafted. No coven
Personal was seen by any of the four seats.

## 2. What the round found

**Bank or cash holds through three acts, and the seats refined it.** Every
seat named it first. The refinements are worth keeping: fire the weaker
detonator into the empty board and save the multiplier for the stack
(`opus-act3.md`, fight 17); never detonate for tempo you do not need, and act
3 charges for it (four forced detonations, each against a printed clock);
Chain Fuse is a multiplier that reads like a flat buff, so place every bomb
before it. Ka-pow! and The Big One were the happiest draws; Alice's Recipe
into an empty board the automatic mistake. The most satisfying thing any seat
found was Sizzle's chain, a Set off whose first bomb Overloads and whose own
conditional then collects on it, 60 damage from a 0-cost card
(`opus-act3.md`, fight 21). Flame Dance, which seats one and two skipped as
worded to switch itself off, is correct and the same pattern.

**The reaction layer works the moment a companion supplies an element.**
Charlotte's Cryo, Barbara's Hydro and Ayaka's Cryo produced Melt, Vaporize,
Frozen on a boss and Overload across three acts, and the arithmetic was exact
every time the seats checked it, roughly fifty outcomes over two records.
R244 pick 2 stands: companion-fed, and the companions arrive on this build.

**Bombs carry Klee's Strength and Weak, and no card says so.** Under Tender's
minus 5 Strength three bombs of printed 6, 4 and 4 badged `Bomb -1`, a
negative number on the screen (`opus-act2b.md`, finding 1). Weak on Klee
shrank a banked stack at the badge; Vulnerable on the target multiplied it
(87 to 130), and multiplied Ayaka's Cryo tick and every bomb but not Letter
Opener's relic damage (`opus-act3.md`, finding 4). Two seats rejected Strength
relics on the printed rule that Strength boosts Attacks, and the third called
a Strength relic "a bomb-size relic" once the badge taught him otherwise. The
Kokomi ruling R246 put the same question one kit over and answered it: a
placed effect carries the target's modifiers, never the placer's. Pick 1.

**Act 3 asks for block on a schedule, and the kit's block is priced in the
currency the other strategy earns.** Dig In and Powder Charge cost Spark;
Spark comes from Pounding Surprise, one per detonation; Grounded pays only for
not detonating and Sparks 'n' Splash argues for never detonating
(`opus-act2b.md`, finding 10). Seat four held Dig In unplayable on two turns of
the fight that killed him because he had spent the fight refusing to
detonate, which is exactly what his engine paid him to do. R244 held the
starter's shape as an F pick and set the draft's survival density as the next
read. That read is in: this run drafted Grounded twice, Dig In, Thoma,
Kirara, Shrug It Off, Barbara and Nicole, and still could not answer a
printed 40. Pick 2.

**The rules that decide a turn exist only as previews.** A single-hit
elemental card consumes the aura and leaves nothing, a Set off leaves its own
aura behind, and the one word carrying that is "instead" (`opus-act3.md`,
finding 1). The four Reactions are defined nowhere on the page; Galvanized was
announced by an enemy and defined nowhere; the Bomb glossary drops the growth
number. Rows in §3.

## 3. What the screens got wrong

Each is a row in `BACKLOG.md`, minted on this packet's branch.

- **A lethal Mine does not stop the hit** (`EB-336`). A Mine 4 killed a 4 HP
  Chomper on its 8x2 and the first 8 landed; the tip says "before the hit
  lands". Default applied: the rule matches the tip.
- **Blazing Barrier's buff line is a stale second print of the Block pool**
  (`EB-337`). "6 Block left" while 15 passed; Block 6 to 12 with the line
  beside it (`opus-act2.md` (c), `opus-act2b.md`).
- **A Reaction preview on a card with no hit reads as an upside and is a loss**
  (`EB-338`). Barbara's Vaporize ate the aura a Cryo tick would have Melted.
- **"Free to play this turn" leaves a Spark price standing** (`EB-339`).
- **The glossary stops at the kit's four words** (`EB-340`): the Reactions,
  the consumed-aura rule, enemy buff keywords, the growth number.
- **Event, shop and reward pages hide the choice** (`EB-341`): two options
  with one title, a potion sold as a relic, a claim on full slots that
  answered ok and vanished.
- **Three page lines short of the state** (`EB-342`): a compound intent
  printed as one Attack while four Burns arrived, one cost sentence for an
  upgrade and a discount, a Smith list that omits without saying why.
- Four open rows widened: `EB-318` (seat three saw one Mine per enemy where
  seats one and two saw a split), `EB-321` (the Melt preview multiplies the
  first bomb, not the card's number), `EB-323` (eleven unnamed purchases over
  four seats), `EB-325` (eight of twelve act-3 floors, both elites).

Seen and not rowed, because they are the base game's: Artifact ate two
relics' debuffs and never decremented on two enemies, which is either the
enemy's kit or a display and needs the decompile, not a row; Planisphere
keys on the ? node, not the room; Burn is blockable; Fruit Juice heals what
it adds; rounding is down; the full heal on entering an act is unannounced;
Very Hot Cocoa's energy lands on the one turn that is hand-limited; the
random-enemy clause four seats called the kit's worst line never bit in 22
fights, because Ayaka's Soumetsu answered every four-body room.

## 4. What the round did not test

The three Hexerei readers (`EB-326`) are not built; the coven Personals
(Prune, Sayu, Qiqi, Yaoyao) were not offered in four seats, so their rate is
still unread and the Hexerei window has no reader yet. Two of five companion
titles still print "(proto)" (`EB-322`, unbuilt). The Jumpy Dumpty split was
not isolated. Aeonglass was never seen.

## 5. Defaults applied (D and E), disclosed

- **E:** the Kokomi run R246 set goes on lane 1 next, on the fix build
  `0.2.2256+proto` installed today from main (#321's Burst gate, the idles,
  the trail log, the Mods image, the understudy split). Three chained Opus
  seats, 250 actions each, a stop at each act's boss.
- **E:** your Klee run comes on the round-8 build that carries the picks and
  the Hexerei readers, one sitting instead of two; veto by playing this build.
- **D:** `EB-336`'s rule reading, `EB-338`'s and `EB-339`'s text readings.
- **E:** seven rows minted here, `EB-336` to `EB-342`; four widened. No agent
  minted an id tonight.

## 6. Picks

1. **Whose modifiers a Bomb carries.** (1) *The target's only: the enemy's
   Vulnerable, Weak and Hard To Kill apply at set-off, Klee's own Strength and
   Weak leave the stack alone, and the badge names every modifier it folds
   in. One sentence in the Bomb tip. The same rule as R246 one kit over*
   [default]. (2) Keep the code's rule, Strength and Weak at placement, and
   print it: the seats' case is that a bomb deck hunting Strength relics is a
   real draft axis, and Weak devaluing a banked stack was act 3's sharpest
   pressure. The one-line new fact: `Bomb -1` on the screen, and two seats
   pricing relics off a printed rule the kit does not follow.
2. **Block on a schedule.** The new fact reopening R244's F pick: the survival
   set was drafted this time and the run died holding Dig In unplayable,
   because the kit's block is funded by detonating while its engine pays for
   holding. (1) *Grounded's held turn also grants 1 Spark ("gain 6 Block and 1
   Spark"), so a holding deck funds Dig In and Powder Charge and the two
   currencies meet; plus one new Uncommon Skill, Take Cover! (1): "Gain 4
   Block. Gain 2 Block for each of your Bombs." Upgrade 6 and 3. On the
   five-bomb board every seat built that is 14 Block for one energy, the hold
   archetype's burst block, scaling with what it already does* [default].
   (2) Hold the shape as R244 set it; round 8 reads the Hexerei readers first.
   (3) Pounding Surprise grants 1 Spark at the start of each turn as well, a
   starter-relic change that funds every archetype and repeats the rules gate.

Both numbers in (1) are prototype numbers, D by the ladder, and ride the
round-8 build with `EB-326`; the seats read them before you do.
