Status: OPEN (PR = [USER]; one pick in §6)

# Kokomi round five: three runs, two deaths at the first boss, and a clear

One pick in §6, with a marked default. Everything else is a default, applied
and disclosed in §5.

Written 2026-09-04, overnight. Five Opus seats played three runs on lane 1 of
the round-8 build (`0.2.2301+proto`: R246's rows, the Bake-Kurage dealing Plan
damage, Tide Wall and Shell Guard, all arms on). Run one died at the act-1
boss, run two died at the act-1 boss, run three cleared the spire with no fight
lost, Queen dead at 99 of 115. The records are
`review/qa/kokomi-round-5-2026-09-03/opus-act1.md`, `opus-run2-act1.md`,
`opus-run3-act1.md`, `opus-run3-act2.md` and `opus-run3-act3.md`; every claim
below names one of them. This is round five's read, the one R246 said comes
before you play.

## 1. The runs in one paragraph

Run one (191 actions) killed the Waterfall Giant on round 6 and died to its
Steam Eruption on the corpse's turn, 27 against 26 HP, by one point
(`opus-act1.md`, finding 2). Run two (208 actions) met The Kin, whose
Followers stand in front of the Priest: every single-target Plan landed on a
Follower the boss's own text says not to kill, and the Priest died of nothing
but hand attacks until Kokomi did (`opus-run2-act1.md`, finding 1). Run three
(654 actions) cleared 23 fights out of 23, Vantom, The Insatiable and Queen,
never below 18 of 80 in act 1 and never in danger after it; the engine was
The Moon Overlooks the Waters, Sango Isshin twice, Battle Plan chained into
itself, the Casket re-arming Hydro under Electro, and Poison ticking before
the enemy acts (`opus-run3-act3.md`, the boss). The seats' repeated praise:
Hard To Kill, Sandpit and Chains of Binding are good fights, and every one
of them was won by reading a number the screen printed.

## 2. What the round found

**Single-target Plans aim at the front enemy, and two bosses put a decoy
there.** The Kin's Followers absorbed a Feint Plan for 10 while the Priest
moved only by hand attacks; the same lane did 46 in one morning against a
lone elite (`opus-run2-act1.md`, finding 1). Queen fights beside a Torch Head
Amalgam carrying "Minions abandon combat without their leader", and every
single-target Plan, Vanguard+ included, went to the minion for the whole fight
(`opus-run3-act3.md`, finding 4). The rule is R241's legibility choice, and
it reads the formation exactly wrong: the enemy the game marks as a decoy is
the one the Kurage hits. Pick 1.

**The Moon is what makes Sango reachable, not an excess.** R246 held The Moon
Overlooks the Waters as the card most likely over-tuned. Run three's seats
found the opposite: "Plans also happen when played" is what lets a Plan count
as carried out on the turn you hold Sango, so Sango's quarter-Max-HP mode
becomes a play instead of a draw (`opus-run3-act2.md`, finding 4), and Battle
Plan under it draws past Chains of Binding's three Bound cards
(`opus-run3-act3.md`, finding 2). Without it, run two's seat paid both Sango
copies at 8. The hold moves from "over-tuned" to "the payoff's key", and the
round-4d pick on the Plan cards' shape is the other half of the same answer.

**The Bake-Kurage's hit is its own kind, and the seats mapped its edges.**
It ignores Shrink and Weak on Kokomi and Skittish's first-hit Block, it is
stopped by enemy Block, and its per-Plan receipt is exact (`opus-act1.md`,
finding 1; `opus-run3-act1.md`, finding 2). Plan order matters, Vulnerable
first, and the queue prints in order only after the fact
(`opus-act1.md`, finding 5). All of it is R246's rule; the tip now says
"or ALL if it says so" since #345, which the run-three seat watched arrive
mid-run. What is still unprinted: that Plans queue, that Chain of Command
counts the turn before the one it was written on and so reads "Deal 0"
whenever you would want it (`opus-run3-act3.md`, finding 7), rows in §3.

**The reaction engine is the deck's damage, under the wrong name.**
Electro-Charged prints on the enemy as `Poison N`, stacks additively to 14
and 15 on bosses, and ticks before the enemy acts, which killed three
enemies in that gap in act 1 alone (`opus-run3-act1.md`, findings 4 and 5).
Element order is the deck's deepest decision and nothing documents it:
Gorou's Geo after the Electro hit, Kujou Sara's rider on the Strike rather
than on Thundergrust (`opus-run3-act2.md`, finding 7). Rows `EB-357`, and the
companion reads carry the note.

**Red Mask works, and two seats' finding was a display artefact.** The intent
number already carries the Weak, so an enemy under Red Mask "hit for its full
printed number" because the printed number had already fallen; the run-three
act-3 seat watched 40 fall to 30 as Weak landed (`opus-run3-act3.md`, finding
1). The operating rule every later HP reading closed on: the number on the
intent is the damage that lands.

## 3. What the screens got wrong

Each is a row in `BACKLOG.md`, on this packet's branch or already on main.

- **Chain of Command counts the wrong turn** (`EB-362`): written on a turn
  with three Companions played, it carried out for nothing.
- **The Future of Potions took a potion and offered nothing** (`EB-363`):
  the "Upgraded Uncommon Attack" it promised opened a selection with zero
  rows, twice; Kokomi's arm pool has no Uncommon Attack, so the base event
  has nothing to offer. The same shape as `EB-352`'s Fasten.
- **A potion reward on a full belt** (`EB-356`), **the enchant screen's dead
  skip** (`EB-355`), **Electro-Charged's name and the Plan queue** (`EB-357`),
  **Sara's buff under Bennett's name and an empty shop** (`EB-360`), all
  from these runs; `EB-328` widened (Undertow+ under Vigor; attack faces hide
  their modified damage where Plan faces show theirs); `EB-348` stands (the
  Casket pinged Inklets for 1 and everything else for 2, still unexplained).

Seen and not rowed, because they are the base game's: Steam Eruption's
posthumous clock, Reattach's revive that never comes, Plating printing one
more than it grants, Pen Nib's cross-combat counter, Burn being blockable,
Cleansing Wave+ choosing its own debuff, Rampart printed on the wrong
creature, the full heal at every act boundary; and Sango's "instead" mode
taking Strength but not a Gigantification triple, which is its op and which
the face could say.

## 4. What the round did not test

Tide Wall and Shell Guard were drafted by no seat in three runs; the kit's
own defence is still unread, and run three's block came from relics (Sai,
Potion Belt's potions) and from Poison killing first. The fixes in #344 to
#347 and the morning receipt were not on the installed build.

## 5. Defaults applied (D and E), disclosed

- **E:** The Moon Overlooks the Waters keeps its numbers; the hold in R246 §5
  closes on this read.
- **E:** your Kokomi run comes on the next deploy, which carries #344 to
  #347; round five's rules gate is met by this read.
- **E:** rows minted on this branch as listed; five records committed
  beside the packet.

## 6. Picks

1. **Where a single-target Plan lands.** (1) *The front enemy that is not a
   Minion. One clause on the Plan tip ("front enemy, or ALL if it says so;
   never a Minion"), no aiming step, and both formations this round lose
   their decoy: The Kin's Followers and Queen's Amalgam carry the Minion
   tag the game already prints* [default]. (2) The player aims a
   single-target Plan when writing it and the morning carries the target,
   a targeting step on the pet play in both engines. (3) Keep the front
   enemy as ruled; the two formations are the kit's known weakness and the
   answer is AoE Plans and hand attacks, which is how run three beat Queen.

The rule in (1) is a prototype rule, D by the ladder, and builds on round 6
with the round-4d pick; the seats read it before you do.
