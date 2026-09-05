Status: RULED R258 2026-09-04

# Furina round five: the reader in the starter, and the turn one that has no Encore

Written 2026-09-04, the afternoon after R254. Two blind Opus seats played the
reframe arm on `0.2.2476+proto`, the first build whose starter carries the
Aria of Recompense reader ("Gain 5 Encore. If you have at least 6 Fanfare,
gain 5 more.") and the named Salon Début (Deploy Mademoiselle Crabaletta),
with the six round-4 fixes live. Neither run reached the act-1 boss; both
spent the 120-action budget at floor 10 of 16. Records:
`review/qa/furina-reframe-round-5-2026-09-04/opus-act1.md` (run 1) and
`opus-run2-act1.md` (run 2). Prototype stage, Guardrail-7.

## 1. The runs in one paragraph

Run 1 (seed `Y89TQ208H8KY`, Ascension 2): five fights won including the
elite, 57 of 78 HP at the stop, two refusals never consecutive. Run 2 (seed
`WHK7LJSR1V5F`, Ascension 2): six fights won including the Byrdonis elite
at 67 of 78, stopped at 54 of 78 on the reward screen after fight six, no
refusals, no potions used all act. Fanfare sat at 3 when Aria was played
in both runs and the reader's second line never paid; run 2 upgraded Aria
at the floor-8 Smith and found the upgrade is Innate, which "changed every
opening turn in the act." Neither seat saw a Burst meter; both read its
gloss.

## 2. What the round found

**Encore is the kit, and its first turn is locked.** Both seats named the
same fact first. Ethereal Spotlight arrives in hand every turn from the
relic and costs 2 Encore; Standing Ovation's trickle pays only on a
Spotlighted card; Fanfare and Encore both open at 0; so the engine's key
is one Aria somewhere in the draw pile. "CANNOT BE PLAYED: you have no
Encore, and this costs 2" was the first line of the first hand of every
fight in run 1 and of fight one in run 2. Run 1: "Aria is never a choice;
it is a tax. If it is in hand it is the first card played, every time."
Run 2 found the fix by accident at the Smith: with Aria Innate, "the
Spotlight is up on turn 1" and the opening turn became the allocation the
kit is about. §5 is the pick.

**Once the engine is on, the decisions are the reframe's.** Run 1: "Encore
is one pool doing three jobs at once: armour under Block, the fee a member
pays to perform at full strength, and the price of the Spotlight," and
every turn with Aria in hand was "a real allocation problem, resolved five
cards deep with the numbers all visible." Run 2's best turns were reaction
ordering (Salon Début then Freminet is Frozen; the reverse is not, worth 9
points of incoming damage on the elite) and the same Encore split. The
Reaction preview line was named the clearest text in the kit by both.

**The reader was carried and not read.** Fanfare reached 3 to 5 in the
fights where Aria was played and the 6 bar was not crossed on an Aria
turn in either run. The bar is the rider copies' bar and stands (§4); what
the round says is that a 5-Encore Aria at Fanfare 3 is the card the seats
played, and the reader's half waits on a stage that has performed twice
before Aria is drawn.

**Duet doubled the card and not the perform.** Run 1 reconstructed it
exactly on the Sewer Clam: the doubled Freminet landed twice, Crabaletta
performed twice where three were due, and no line named Duet resolving
(`EB-420`). Run 1 called Duet "the card I never wanted," and the reason is
the half it did not do.

**Defects, twelve rows.** The starter reader printed its dev suffix on the
face, "Aria of Recompense (reframe)", in hand, in the deck list and on the
upgrade screen (`EB-419`). Guest Cast's tip says "no Fanfare" and Fanfare
rose 2 per performance under it in five fights across both runs (`EB-421`).
A status row "Spotlight Spend Boost: 30" sat unglossed all fight
(`EB-422`). Frozen's shatter text says it removes Frozen and Frozen stayed
(`EB-423`). The Salon log names no copy number in a two-of-a-kind fight
(`EB-424`); Salon Début reads as aimed and is not (`EB-425`); Poised
Riposte's face reads "already including Encore" and was skipped unparsed
(`EB-429`); nothing says a Companion's perform follows the card's target
or does nothing on an empty stage (`EB-430`). Electro-Charged still
renders as Poison (`EB-357`, open); the Burst gloss still prints under the
arm (`EB-369`, open). The round-4 fixes read true where they were met:
the second Ethereal Spotlight was refused with its reason in both runs,
and Encore's gloss was on the Neow screen.

**The pool-pass questions, for that packet and not this one.** No starter
card Evokes (the reframe packet's F16, unpicked), so a seat who could not
Evoke passed two Salon-member rewards blind; the elite's Skittish pack
still punishes many small hits and the pool offered one ALL card in
sixteen floors across both runs.

## 3. What the round did not test

The 6-Fanfare line on Aria; any rider copy; the boss. Both seats stopped
on the budget at floor 10, healthy. Nothing here is a strength reading.

## 4. Defaults applied (D and E), disclosed

- **The reader's bar STANDS at 6** (D): it is the copies' bar and it was
  not reached on an Aria turn; a bar that was never crossed is unread, not
  wrong. Re-ask when a record shows the line paying.
- **`EB-419` to `EB-425`, `EB-429`, `EB-430` minted**; seven of them are on
  an Opus fix branch beneath this packet. `EB-357` and `EB-369` are cited,
  not re-minted.
- **Aria's upgrade is Innate** on the arm copy, as the shipped card's own
  delta; run 2 found it and it is disclosed here rather than changed.

## 5. The pick

**Pick 1 (A): the Encore opening.** Two seats, two runs, every fight: the
relic hands the player a dead card until Aria is drawn, and the kit's one
recurring tension (hold Encore as armour, or spend it on the stage) cannot
happen on a turn with 0 Encore. The starter's shape and the relic's text
are rules, so [USER] plays the next build of whichever is picked.

1. **Furina starts each combat with 2 Encore (default).** The number is
   Ethereal Spotlight's own price, lifted off its face; the relic's line
   says it. Turn one has the Spotlight or the armour, never neither, and
   Aria stays a card the player chooses rather than a tax paid first. One
   constant in both engines, arm-only.
2. **The Aria copy is Innate at base**, the upgrade run 2 found, with the
   upgrade moving to the shipped +3 Encore. Fixes the same turn and makes
   the "tax paid first" read permanent, since the key is always in hand.
3. **STANDS.** The opening is a draw and Aria is the key; a seat that
   upgrades Aria first has the fix. Costs nothing, and both seats will say
   it again.

Default is 1 because it opens the decision without making Aria automatic;
2 is what the seat reached for and would take if 1 reads as too much
armour on turn one.

## 6. Ruled

R258, 2026-09-04: pick 1 at its default. Furina starts each combat with 2
Encore under the reframe arm; `EB-479` builds it. Read against rounds 5 to 9
(the dead first turn four times, then round 9's real choice "dry by
construction") and the GPT review's point that Encore's depth is its
destinations, which `EB-466` carries separately. [USER]'s words are in the
ruling commit.
