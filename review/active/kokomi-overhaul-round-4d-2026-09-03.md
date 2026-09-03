Status: OPEN (PR = [USER]; one pick in §6)

# Kokomi round four-d: three Opus seats, the spire cleared, and what the Plan layer is only good through

One pick in §6, with a marked default. Everything else is a default, applied
and disclosed in §5.

Written 2026-09-03, overnight. Three chained Opus seats played one run on
lane 1 of the arms-on fix build (`0.2.2263+proto`: R243's numbers, the Fable
card audit, the coven, #321's Burst gate; R246's rows were built during the
run and are not on it). Seat one cleared act 1, seat two killed The
Insatiable, seat three killed Aeonglass and left the lane on the Architect's
screen. The records are `review/qa/kokomi-round-4d-2026-09-03/opus-act1.md`,
`opus-act2.md` and `opus-act3.md`; every claim below names one of them. This
is the three-act read R244 asked for and R246 re-ordered. An earlier seat on
this lane played the base kit for 99 actions on a build I deployed with every
arm off; its record is set aside under
`review/qa/kokomi-base-kit-misdeploy-2026-09-03/` and fed the harness fixes
in #334 and #337, not this packet.

## 1. The run in one paragraph

Forty-five rooms, 646 actions, three refusals, no fight lost. The Ceremonial
Beast (252 HP) died on round 6 for 22 HP; The Insatiable (321) on round 5 for
16; Aeonglass (512) on round 6 for 30, with its Vulnerable at 12 from Cryo
ticks alone. HP ran 58/87 at the act-2 door, 35/87 at act 3's, 80/121 at the
end after Mango. Nineteen relics and a 43-card deck at the stop; Whispering
Earring's extra energy, Candelabra and Snecko Skull carried as much as any
card. The three seats agree on which cards made the Plan layer work: Change
of Plans+, Moon's Reflection and Sango Isshin, and on which one card decided
every boss, Sango's quarter-Max-HP mode landing after a morning (`opus-act3.md`,
the boss; `opus-act2.md` §(a)).

## 2. What the round found

**The kit clears the spire, and the seats say the Plan layer is only good
through three cards.** Seat three, after 225 actions: "the mechanic's whole
decision space in three acts is 'do I have a Sango in hand this turn', and
the answer is a draw, not a choice" (`opus-act3.md`, the closing note). Nine
of his twelve Plans were Vanguard, "a 0-cost card whose text says to write it
there". Seat one wrote nine Plans and counted seven as cards "played onto it
because their text says to, not because I chose between planning them and
playing them" (`opus-act1.md`, the closing note). Seat two found the Kurage
"much better than act 1 made it look, but almost entirely because of three
cards the previous seat did not have" (`opus-act2.md`, the closing note). The
card every seat liked is Feint, which prints a now-line beside its Plan line
and makes writing a trade. Seven of the sixteen Plan cards print no now-line
at all: Kurage's Oath, Ambush, War Council, Battle Plan, Vanguard, Chain of
Command and Nereid's Ascension. Where the layer has a decision it is because
the card has two halves. Pick 1.

**Round four-c's death is answered, mostly by relics.** Round four-c died on
floor 24 with a Defend+ for a block ceiling. This run took 22, 16 and 30 from
the three bosses with block from Salt Line, Coral Bulwark and a relic pile
nineteen deep, and with an energy floor of four from Whispering Earring. Tide
Wall and Shell Guard (R246) were not on this build, so the kit's own defence
is still unread; the round-five seats read it (§5).

**The reaction engine is the deck's strongest thing, and its unprinted half
is the Casket.** Every seat rebuilt the same machine from arithmetic: the
Tamakushi Casket's strike is a full Hydro hit, once per debuff that lands, on
the enemy it landed on. It re-arms the Hydro aura the next Electro card
needs, which is what turned Poison 9 into 29 on the boss (`opus-act2.md`,
finding 6); it reacts, and Vaporized the Pyro aura the player's own Amber had
just set (`opus-act3.md`, finding 2); it takes the target's Vulnerable; Red
Mask's combat-start Weak fired it on all three enemies. Three seats logged it
as "the rule is not printed anywhere". It is printed in one sentence on the
relic, and that sentence names none of the four consequences (`EB-348`). The
Frozen line's boss exception, two Vulnerable per Cryo-on-Hydro, is the
design's best surprise two acts running; it stays.

**The seats' debuffs and the morning.** Shrink did not touch a Plan's damage
while it rewrote every Strike (`opus-act1.md`, finding 2), which is R246's
rule one build early: the Bake-Kurage deals it. Sango Isshin's quarter-HP
mode is her own hit, so her Weak cuts it and the enemy's Vulnerable raises it
while Lightning Fang's flat bonus does not (`opus-act2.md`, finding 4); the
op is right and the face could say "not an Attack". Kujou Sara's Crowfeather
Cover buffs the next Attack without rewriting its element, Lightning Fang
rewrites it; both print "applies Electro" and only one changes the card.
Consistent, unprinted, noted.

**Automatic plays aim at the pet.** Uproar's "play a random Attack" wrote
Slack Water onto the Bake-Kurage as a Plan (`opus-act1.md`, finding 1) and
three act-2 plays were unreportable (`opus-act2.md`, finding 2). Plan cards
declare a pet-or-enemy target, and the game's automatic play picks either.
`EB-347`, default applied: the pet is a deliberate target only.

## 3. What the screens got wrong

Each is a row in `BACKLOG.md`, minted on this packet's branch. The page the
seats read changed under them: #337 landed during act 2, and seat two
recorded the reaction glossary and the potion-belt count arriving mid-run.

- **An auto-played turn prints nothing** (`EB-349`). Whispering Earring's
  Vakuu played six opening turns as an empty hand with no card, target or
  result named, and burnt a 32-damage Exhaust card twice; a multi-hit intent
  under Tainted printed 18 and cost 15; Pounce's one-use discount prints on
  every Skill.
- **The removal grid and the gold** (`EB-350`). The shop's Card Removal
  screen printed exactly 25 rows against decks of 29 and 38, omitting every
  card acquired since it was last opened; gold never prints on the map or
  reward pages, and the seats' reconstructions missed by 100, 47 and 202.
- **Unnamed grants** (`EB-323`, widened): Mango, Bag of Marbles, Byrdonis
  Egg, and Touch a Mirror downgrading two chosen rewards without naming them.
- **The turn boundary** (`EB-329`, widened): 118 damage across three enemies
  on one tick, two-thirds accountable; the Casket, reaction Poison, plan
  damage and the Banner's Weaks resolve together with the HP bar as the only
  evidence.

Seen and not rowed: Aeonglass pays nothing and the Architect follows, which
reads as the act's convention; Withering Presence counts down rather than up;
Crystallize and Swirl print only as previews (EB-340 shipped the six the
build's cards supply; the two Geo and Anemo reactions join when a card
supplies them); the Future of Potions' identical titles and the full belt,
both fixed in #337 and confirmed by seat three; a Max HP gain healing what it
adds, the base game's.

## 4. What the round did not test

R246's rows: the Bake-Kurage dealing Plan damage under Weak and Vulnerable
(`EB-334`), Tide Wall and Shell Guard (`EB-335`). The Kurage's beats
(`EB-316`, `EB-317`) are your eyes-on. The Moon Overlooks the Waters was
drafted by no seat, so its hold (R246 §5) is unread.

## 5. Defaults applied (D and E), disclosed

- **E:** the round-five seat run on the round-8 build (`0.2.2301+proto`,
  every ruled row through `EB-346`) is on lane 1 tonight, three chained Opus
  seats, 250 actions each, a stop at each act's boss; Klee's round-8 seats
  run beside it on lane 2. Your Kokomi run comes on that build after the
  read, as R246 set.
- **D:** `EB-347`, automatic plays never aim at the pet.
- **E:** four rows minted here, `EB-347` to `EB-350`; two widened.
- **E:** `EB-325`, two act-entry map screens read beside the harness's own
  reachable set and matched it exactly: the page prints the wire's list. A
  mid-act screen is still owed before the row closes.

## 6. Picks

1. **The Plan cards' shape.** Seven of sixteen Plan cards have no now-line,
   so writing them is not a decision, and the seats named the layer's only
   real choice as a Sango draw. (1) *Six of the seven gain a now-line that is
   the weaker half, so every one of them prints the trade Feint prints;
   Nereid's Ascension stays Plan-only as the rare engine card* [default]:
   Kurage's Oath (starter) "Deal 3 damage to ALL enemies. Plan: Deal 7
   damage to ALL enemies."; Ambush "Deal 5 damage. Plan: Deal 12 damage.";
   War Council "Apply 1 Weak to ALL enemies. Plan: Deal 5 damage and apply
   1 Weak to ALL enemies."; Battle Plan "Draw 1 card. Plan: Gain 1 Energy
   and draw 2 cards."; Vanguard "Exhaust. Apply 1 Vulnerable. Plan: Apply
   1 Vulnerable and 1 Weak."; Chain of Command "Deal 3 damage for each
   Companion card you played this turn. Plan: Deal 6 damage for each
   Companion card you played last turn." Upgrades stay on the Plan halves.
   (2) Keep the Plan-only cards and add a second payoff beside Sango: Rising
   Tide, Uncommon Attack, 1: "Deal 4 damage for each Plan the Bake-Kurage
   carried out this morning."; the layer's decision moves to the payoff
   draw, which is where the seats found it. (3) Hold until round five reads
   Tide Wall and Shell Guard, which are the first Plan cards designed to be
   written rather than played.

The numbers in (1) are prototype numbers, D by the ladder, and build on
round 6 after the round-five read; the seats read them before you do.
