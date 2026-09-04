Status: RULED R253 2026-09-04 (picks 1 and 2 at their defaults; the four rider copies passed the charter audit, `review/records/card-audit-2026-09-04.md`)

# Furina round two: the reframe on its own engine, and the two economies that read wrong

Two picks in §6, each with a marked default. Everything else is a default,
applied and disclosed in §5.

Written 2026-09-04. Opus seats played two runs on lane 1 of the round-2 build
(`0.2.2371+proto`: R251's retirement of the shipped Burst under the arm,
`EB-364` and `EB-366` to `EB-368` built, all arms on, Ascension 2). Run one
died on floor 6, in the fifth fight. Run two cleared act 1 at 1 of 92 and
died on act-2 floor 30, to the Infested Prism at 12 of 92 off a forced
single-node map. The records are
`review/qa/furina-reframe-round-2-2026-09-04/opus-act1.md`,
`opus-run2-act1.md` and `opus-run2-act2.md`; every claim below names one of
them. Both seats were Opus, so this is the round comparable with Klee's and
Kokomi's records, where round one's was Sonnet.

## 1. The runs in one paragraph

Run one (124 actions): Overflowing Hospitality into Ethereal Spotlight into
Freminet on turn one of fight one, the best turn of the run, then hands of
four Block cards and no attack from fight three on, and death at 3 of 78 to
a Calcified Cultist and a Seapunk (`opus-act1.md`, fight 5). Run two (about
290 actions, forty past the cap, declared): three rests, two one-HP finishes,
Vantom killed on the seat's turn at 1 of 92 with 171 gold and six relics
(`opus-run2-act1.md`, Identity). Act 2 (144 actions) cleared six fights
including the Entomancer, then died to the Infested Prism, whose intent
doubled from 3x3 to 6x3 on a turn the seat only applied Weak
(`opus-run2-act2.md`, the death). Both seats named the same best
decision, Shatter now or keep the Frozen, and the same dead turns, Block-only
hands.

## 2. What the round found

**The reframe's rules read true where they were printed, and the printing
is half done.** A Companion play performs the front member and a deploy
performs at once, and both seats saw the member's damage land
(`opus-act1.md` §(c) 4; `opus-run2-act1.md` §(c) 5). But the shipped Salon
buff still prints "each Salon Member spends 1 Encore for its act" in the
status bar beside the arm's tip "Members do NOT act on their own", both seats
tested it, and the tip is the one that is right (`opus-run2-act1.md` §(c) 2).
Neither seat ever learned which member it held; run one found Chevalmarin by
subtracting Neuvillette's 7 from a 9. `EB-383`.

**Encore is Furina's second Block, and nothing said so.** Four to zero,
three to zero, one to zero at turn start with a member on stage, no act
performed (`opus-act1.md` §(c) 2). The seat read it as the stage eating the
bank. The cause (`EB-382`, built) is the shipped rule the arm kept: damage
past Block is absorbed by Encore one for one, and the shipped kit printed a
Fanfare per point absorbed, which the arm's meter leg silenced, so the
absorption became invisible. Fight one reconciles exactly: an 8 intent, 4 HP
lost, 4 Encore gone. The page now prints the spend rule on the meter. Two
things follow. Round one's watch on Encore income is answered: the seats
were not starved by income but by an involuntary sink, and a bank held
across an enemy turn is Block first and applause second. And that sink
competes with the reframe's engine, which asks the player to hold Encore for
member acts and Spotlights. Pick 2.

**The shipped Burst is gone and its words are not.** Nine plays of cards
printing "Burst +5" and Barbara's "Gain 4 Burst Energy" left every tooltip
at "You hold 0 of 70 Burst Energy" (`opus-act1.md` §(c) 3;
`opus-run2-act1.md` §(c) 1). That is R251 working: the meter is refused
under the arm. The faces and the tooltip still describe it, which is
`EB-369`, widened; the seats read a prominent mechanic that is "simply not
connected", and that is the cost of building the retirement before the
words.

**The Fanfare economy under the arm is a tenth of the shipped one, and the
shipped riders know it.** The arm mints Fanfare by performance only, 2 per
trigger and 5 per Evoke (`FurinaReframe.cs`, `FanfarePerTrigger`,
`FanfarePerEvoke`). Across fourteen fights Fanfare ranged 0 to 8; the
shipped riders at 12 (Dramatic Entrance, Florid Cadenza) and 20 (Flood of
Emotion) never came within reach, Applause Line's 1 per 4 paid 0 or 1, and
Crescendo's 1 per 2 visibly moved (`opus-run2-act1.md` §(b)). The Fanfare
tip still lists the shipped generators (`EB-385`). The riders are a design
question, not a page one: the arm's drain rows (`proto_fr_`) are its
Fanfare payoff and were never offered in two rounds. Pick 1.

**Where the decisions were.** Shatter now or keep the Frozen, both sides
printed and the answer moving with HP (`opus-act1.md` §(a) 1); Hydro and
Cryo order inside a turn; Ethereal Spotlight's two Encore against two
member acts; Crescendo into Slippery to keep the permanent 2
(`opus-run2-act1.md` §(a) 4). Both seats put the reaction layer first
among what was legible: the preview on the card, the aura's duration, the
intent halving the instant a Frozen lands. The Salon presented no choice
in either run: Salon Début is random, no seat filled the stage to three, and
the Evoke payout the tip spends four lines on was never seen. The act-2
seat's verdict is the round's: the interesting decisions were supplied by
enemy mechanics (the 9-damage cap, Thorns, Personal Hive) and by the
reaction layer, not by Furina's three meters, and Ethereal Spotlight read
"CANNOT BE PLAYED: you have no Encore" on turn one of every fight by
construction (`opus-run2-act2.md` §(c), §(e)).

**A companion's buff overrides the printed element.** With Razor's
Lightning Fang up, High Tide and Chevreuse both applied Electro while their
faces kept printing Hydro and Pyro; without it the same sequence Vaporized
as printed. It cost the seat a planned Overloaded (`opus-run2-act2.md`,
finding 1). `EB-389`.

**The pool's shape lost run one.** Fight three's second turn was four Block
cards and one unplayable card; fights three to five dealt 0 to 4 damage a
turn on hands like it (`opus-act1.md` §(b)). Run two's automatic turns were
"one attack and two Block cards", most turns of five fights. Furina's sheet
is Balance-stage and this is the reframe's read, so the packet notes the
shape and moves nothing; her pool pass comes after the arm reads true.

## 3. What the screens got wrong

Each is a row in `BACKLOG.md` on this packet's branch, or cited to one on
main.

- **Encore's absorption rule printed nowhere** (`EB-382`, built: the meter says it).
- **Two Salon rulebooks on one screen, no member named** (`EB-383`).
- **Overflowing Hospitality lost its member** to a stale-stage guard that fired
  inside a paying deploy, and its 1 damage is the dry three-quarters of a
  performance at 0 Encore, printed nowhere (`EB-384`, built; `opus-act1.md` §(c) 4; `opus-run2-act1.md` §(c) 5).
- **The Fanfare tip's generators are the shipped ones** (`EB-385`).
- **Guest Cast prints no duration; the three Spotlight meters are undefined**
  (`EB-386`; both records' lesser confusions).
- **Chevreuse's previewed Overloaded resolved as the bare hit, twice**, the
  Electro aura left standing, where Vaporize on the same card resolved as
  previewed (`EB-387`; `opus-run2-act1.md` §(c) 3).
- **Guest Cast reaches the immediate leg and not the delayed one**, and not
  Sara's granted rider (`EB-388`).
- **Lightning Fang overrides the printed element with no change on the
  face** (`EB-389`).
- **The Burst tooltip under the arm** (`EB-369`, widened).
- **Sharp, Nimble, Swift and Bond of Life defined nowhere, Tainted defined
  in a circle** (`EB-377`'s base-keyword tips; `EB-359`).
- Already rowed: HP never printed before a fight and gold never as a total
  (`EB-350`); the Encore meter's own line saying the feed carries "no rule
  for how it is spent" (`EB-368`'s family, the page's honest gap).

Seen and not rowed: the Poison with no printed source in run two's act 1
is Electro-Charged shown as Poison, which act 2 confirmed (`EB-357`); a
boss turn where cards printing 53 removed 84 (`opus-run2-act1.md` §(c) 4),
which the records cannot attribute; the Prism's intent doubling and the
act-boundary heal from 1 to 73 (the base game's); Lynette's Swirl blank against
one enemy (the card's own text); Slimed and Tainted as dead draws.

## 4. What the round did not test

No seat saw the five `proto_fr_` rows, so the named deploy, the aimed Evoke
and the drain are unread after two rounds. No seat filled the stage, so the
full-stage Evoke was never paid. Act 2 reached its second Elite and no
boss; act 3 is unplayed after two rounds. The Encore economy under a printed absorption rule is
unread; round three reads it.

## 5. Defaults applied (D and E), disclosed

- **E:** your Furina act-1 run is due on this build, `0.2.2371+proto`, the
  first with the reframe alone; `EB-382` is a defect fix, not a rule, and
  does not move your turn.
- **E:** `EB-382` to `EB-386` are built (PR #363, merged into this branch);
  `EB-387` to `EB-389` are open; round three runs on this build.
- **E:** rows minted on this branch as listed; three seat records committed
  beside the packet.
- **D:** the Fanfare amounts (2 and 5) stand until pick 1 is ruled.
- **D:** Encore's absorption stands until pick 2 is ruled; the page prints it.

## 6. Picks

1. **The shipped Fanfare riders under the arm.** The arm's Fanfare is small
   by design and the shipped 12 and 20 thresholds were priced for the
   shipped economy. (1) *Under the arm, the shipped riders re-price to the
   arm's scale: 12 becomes 6 and 20 becomes 10, arm-only prototype copies of
   the affected rows, nothing on the shipped sheet moves, the seats read
   them on round three* [default]. (2) Leave the riders where they are and
   raise the arm's income instead (trigger 3, Evoke 8), which also feeds the
   drain rows the seats have not seen. (3) Leave both: the riders are the
   shipped kit's and go when the shipped meter goes, and round three reads
   the drain rows first.

2. **Encore's absorption under the arm.** The shipped rule spends Encore
   on damage past Block, one for one, before the player can spend it on
   the stage. (1) *Keep it, now that the meter prints it: it is Furina's
   survival law from the shipped kit, the reframe's sec.4.1 retired only
   the Fanfare it minted, and a player who wants applause on the stage
   blocks first* [default]. (2) Retire the absorption under the arm, so
   Encore is spent only by choice, and Furina's defence is her Block cards
   and Fanfare's drain rows; the seats read whether she survives it. (3)
   Halve it: two damage per Encore, arm-only, a prototype number.

The numbers in pick 1 (1) and (2) and pick 2 (3) are prototype numbers, D
by the ladder; each pick is which surface moves, which is the reframe's own
question.

## 7. Round three, read after the fixes

Two Opus seats played one more run on `0.2.2401+proto`, which carries #363's
fixes in the C# (`review/qa/furina-reframe-round-3-2026-09-04/opus-act1.md`,
`opus-act2.md`). One caveat first: the act-1 seat's page came from `main`,
without #363's page half, so its two page findings (the Encore meter's "no
rule for how it is spent", the Spotlight meters still listed) are the
unfixed page and not a read of the fix; the act-2 seat had the fixed page.
The picks in §6 were not applied; this run reads the fixes only.

Act 1 cleared at 45 of 85 (189 actions), The Kin dead, an 18-card deck on
Ethereal Spotlight, Silver Crucible and Tiny Mailbox. Act 2 (126 actions)
cleared four fights and died on floor 25 to an Infested Prism the map
offered as the only node, at 17 of 85 going in, the same floor and the same
Elite that killed round one's act 2.

What the fixes did: the Salon badge names the member and the deploy's
performance shows on a buff line the moment it happens (`opus-act1.md`
§(c) 4), which is `EB-383` and `EB-384` read true, and the seat's one
complaint is that the card face still does not say it (`EB-398`, on the
round-10 branch above this one). Encore fell by exactly 3 across two turn
boundaries and held across two others, which is the absorption rule at
work (`EB-382`); the seat could not see the rule because its page was the
old one.

What the round adds: the opening is solved and automatic by fight four,
buy Encore, Ethereal Spotlight, the biggest Companion, four times
identically (`opus-act1.md` §(b)); the Salon is the longest rules block on
the screen and paid about 25 damage and 30 Block in seven fights; Fanfare
peaked at 15 and the seat never acted on it, which is §6 pick 1's fact
again; Casting Call was never worth playing and Duet+ was the best card in
the deck (`opus-act2.md` §(d)); Freminet's Block half prints 6 and pays 9
under Guest Cast while his damage prints its boost (`EB-388`, widened);
Lightning Rose's Vulnerable never showed on a body across three castings
(`EB-399`, above this branch); Tainted's circular gloss cost the seat its
last Elite (`EB-359`); the Burst tooltip still reads 0 of 70 (`EB-369`).
The elemental layer was, for the third round running, the part every seat
called legible and the source of the best turns.

Nothing in round three moves §6. Pick 1 has three rounds of Fanfare
between 0 and 15 behind it; pick 2 now has the absorption printed on the
meter for the round-four seat to read.

