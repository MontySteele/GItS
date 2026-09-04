Status: RULED R252 2026-09-04

# Klee round nine: one run, dead on floor 22, and where the pool is thin

One pick in §6, with a marked default. Everything else is a default, applied
and disclosed in §5.

Written 2026-09-04. Two Opus seats played one run on lane 2 of the round-9
build (`0.2.2309+proto`, Ascension 1: R250's Splash paying the largest Bomb, `EB-358`'s
stacking answer, the fixes from #344 to #347, all arms on). The run cleared
act 1 at 12 of 69 HP and died on act-2 floor 22, in the third hallway fight,
before any Elite, shop, rest site or the boss. The records are
`review/qa/klee-round-9-2026-09-04/opus-act1.md` and `opus-act2.md`; every
claim below names one of them. The run is the read R250 asked for, and it is
also the first Klee run read beside the control run
(`review/records/control-ironclad-2026-09-04.md`), where the same seat family
on base Ironclad died on the act-1 boss.

## 1. The run in one paragraph

Act 1 (about 196 actions, one refusal): Silver Crucible at Neow, the Bygone
Effigy killed on turn 5 at 33 of 69, The Kin killed on turn 6 at 12 of 69
with a ninety-damage Big Badda Boom sequence two turns earlier
(`opus-act1.md`, fight 8). Twenty-two cards at the act boundary: eight base
cards, Ka-pow!, Jumpy Dumpty, four more placers, three detonators, Dig In,
two Kaeya cards and Alice's Recipe. Act 2 (61 actions): Pael's Wing at the
Ancient, a Thieving Hopper killed on its escape clock, three Exoskeletons
under Hard To Kill killed by exact arithmetic, then two Chompers at 30 of 69.
Two of the three act-2 fights ended with a full unblocked turn because the
hand held no Block card at all, and the last hand held one Defend against
sixteen (`opus-act2.md`, fight 3). The seat's verdict: the offence is
inventive and legible, the defence is two starter cards and a hope.

## 2. What the round found

**The kit's decision is intact, and it reads from the screen.** Bank or cash
was a real question on the first turn of the first fight (`opus-act1.md`
§(e)), and the seat named four kinds of decision in act 1: when to cash,
which body to point the detonator at, the order inside a turn, and Mines as
removal (`opus-act1.md` §(a)). Act 2 added the best turn of the run: Hard To
Kill's cap of 9 per hit made one enormous volley worthless and three medium
hits the answer, and the seat re-derived the deck on the spot for an exact
24 (`opus-act2.md`, fight 2). R248's target-only Bomb and the badge that
prints the post-cap number both read true; the seat called that badge "the
best piece of printing in the whole act".

**The pool's defence is where the run died, and the offer rate is why.**
The brief makes the weakness load-bearing: Klee cannot block on demand, her
defence is conditional on cook-or-cash, and "a Diona in the reward screen
reads as relief" (`review/active/klee-brief-2026-09-01.md` §6). That shape is
right and the seat felt it exactly as written. What the run shows is the
density: the arm carries four defensive rows in thirty-three (Dig In, Run
Away!, Grounded, Sorry, Jean...) and two defensive stand-ins (Diona, Noelle),
so a card reward shows one about a third of the time. Across ten reward
screens the seat was offered Sorry, Jean... twice and Bennett once, and never
saw Grounded, Run Away!, Diona or Noelle (`opus-act1.md` rewards;
`opus-act2.md` rewards). Round 8's clear ran on Grounded paying 6 Block every
turn; round 9 never met it. A kit whose survival answer is in the pool needs
the pool to show it. Pick 1.

**Bombs are not Attacks, and nothing says so.** Slow 50 on the Bygone Effigy
multiplied the seat's card attacks and left the Bombs flat (48 dealt where 46
was printed, `opus-act1.md`, fight 6). Flutter 5 on the Thieving Hopper
halved a Kaeya strike and left a 27-point Bomb whole (`opus-act2.md`, fight
1). Both read "from Attacks", and the Bomb's hit is not one: the C# folds in
the enemy's Vulnerable and a damage cap and nothing else
(`ProtoBombPower.cs`, `FoldedMods`). That is a coherent rule and a good one,
because Hard To Kill and Aeonglass's Block still bite while a Flutter does
not. But the tip says "its hit takes the enemy's debuffs, not yours", and Slow
is the enemy's debuff, so the seat found the truth by arithmetic twice and
said plainly that it guessed. `EB-373`, default applied: the tip and the face
say "not an Attack".

**Alice's Recipe lost every comparison.** Held in five hands across three
act-2 fights and declined every time: two energy for a payout two turns out,
in fights that ended inside four turns, and a literal blank under Hard To
Kill (`opus-act2.md` §(b), §(d)). Under R250 the Splash pays the largest
Bomb, so growing it twice is now the Rare pair the Splash wants; the card is
held at its number until a seat has read the two together.

**The turn with no placer is the kit's dead turn.** With no Bomb on the
board, Perfect Timing, Big Badda Boom, Ka-pow! and Fwoosh! are vanilla
attacks with a paragraph of dead text, and Quick Fuse refuses itself
(`opus-act2.md`, fight 1 round 1; fight 3 round 1). The starter's one placer
is Jumpy Dumpty, so half of all first hands in a ten-card starter open
without one, and the seat's twenty-four-card deck with four placers opened
without one about one time in three. The starter is R242's and stands; the
finding is carried to the pool work in pick 1, where a cheap placer with a
defensive half is the natural row.

**Perfect Timing's replay never fired.** The clause needs a non-Pyro aura
standing when its own Set off lands, so it is a two-card line with a Kaeya
card played first, and the seat never held both (`opus-act2.md` §(c) 3). It
works as printed; it is rare in a deck with two aura sources. Noted, not
changed.

## 3. What the screens got wrong

Each is a row in `BACKLOG.md` on this packet's branch, or cited to one on
main.

- **The Bomb tip's "takes the enemy's debuffs"** against Slow and Flutter
  (`EB-373`, above).
- **Grounded is named and never defined.** Kaeya's Cold-Blooded Strike prints
  "This turn, Grounded counts nothing as having gone off" and its buff
  reprints it; a seat who never owned Grounded read it in two acts as noise
  on the screen it reads every turn (`opus-act1.md` §(c) 3; `opus-act2.md`
  §(c) 2). `EB-372`: the Grounded tip on every face that names it.
- **Pael's Wing never offered its sacrifice.** Two reward screens printed
  `choose` and `skip` only, and the seat could not tell whether skip was the
  sacrifice (`opus-act2.md`, Pael). The wire carries no sacrifice option.
  `EB-374`.
- **No way to drop a potion outside combat.** Tiny Mailbox's two potions at
  the pre-boss rest were refused at a full belt, and the page has no drop
  verb though the wire has one (`opus-act1.md`, Identity). `EB-371`.
- **The Infested Automaton never named the Power it gave.** One of the
  seat's twenty-four cards was unplannable for the whole act
  (`opus-act2.md`, the event). `EB-323`'s family, already on main; the packet
  cites it rather than widening a row at its length ceiling.
- **Jumpy Dumpty's rider read as two Mines on one bystander** after a Twig
  Slime died holding one (`opus-act1.md` §(c) 2). That is the Bomb jump,
  `EB-361`, default already applied on main.

Seen and not rowed: the Inklet spawn arrived unforecast (base game); Frail
capping Defend at 3 (base game); the seat's boss-turn-one Spark going 1 to 3
with no Bomb going off, which the seat could not source and this packet
cannot either from the records (`opus-act1.md` §(c) 4), watched for round 10;
the reaction glossary's length (`opus-act2.md` §(c) 6), which `EB-359`'s
family already carries.

## 4. What the round did not test

No seat saw Sparks 'n' Splash, so R250's largest-Bomb rule and `EB-358`'s
stacking answer are built and unread live. No seat saw Grounded, Run Away!
or a Hexerei card (`EB-326`, third round), so the hold archetype and the
Hexerei window are still unread. Act 2 ended before an Elite, a shop or a
rest site, and act 3 was never reached. One run, not two, because lane 1 was
held by Kokomi's round and then by a page-leak fix.

## 5. Defaults applied (D and E), disclosed

- **E:** your Klee act-1 run is due on this build, `0.2.2309+proto`. No rule
  has changed since R248, the seats have read it across three runs (round 8's
  two and this one), and the pool work in pick 1 is card design inside the
  brief, not a rule change, so it does not move your turn.
- **D:** `EB-373`, the Bomb tip and face say the hit is not an Attack.
- **D:** `EB-372`, the Grounded tip travels with any face naming it.
- **D:** Alice's Recipe stays at 2 energy until the Splash pair is read.
- **E:** rows `EB-371` to `EB-374` minted on this branch; two seat records
  committed beside the packet.
- **E:** the second round-9 run is not re-run; round 10 carries the pool
  rows from pick 1 and is the next seat read.

## 6. Picks

1. **How the pool answers the defence.** (1) *Widen the arm by defensive
   rows that keep the brief's shape, every one conditional on the Bomb
   state: a cheap placer with a Block half for the dead opening turn, a
   Retain Block that grows with the largest Bomb, a Cryo-side shield for the
   React loop, and one more Diona-shaped stand-in. Four to five rows, designed
   on the round-10 branch, seats read them before you do, and Grounded, Run
   Away! and Sorry, Jean... stay as they are* [default]. (2) Keep the pool at
   thirty-three and read the act-2 death as the identity working: the control
   Ironclad died on the act-1 boss, so a Klee dying on floor 22 is above the
   floor, and round 10 re-runs on this pool. (3) Move the answer into the
   starter instead: swap two Defends for Dig In and Run Away!, which is an
   R242 starter change and puts your play on the next build rather than this
   one.

The rows in (1) are Prototype card design, mine by the routing; the direction
is the pick because you asked for the pool-size read before any tuning, and
this is the first run that shows which shelf is empty.
