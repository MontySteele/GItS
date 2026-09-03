Status: OPEN (pick 1 in §6; the defaults in §5 are applied)

# Kokomi round nine: two runs on R250's rules, and the shelf the pool leaves empty

One pick in §6, with a marked default. Everything else is a default, applied
and disclosed in §5.

Written 2026-09-04. Opus seats played two runs on lane 1 of the round-9 build
(`0.2.2309+proto`, Ascension 2: R250's six now-lines and its skip-Minions
rule for a single-target Plan, `EB-362`'s Chain of Command fix, the fixes
from #344 to #347, all arms on). Run one cleared act 1 and was stopped one
move into act 2 by a page-leak guard, since fixed (`EB-370`, #357). Run two
cleared act 1 at 42 of 80 and act 2 at 24 of 80, and @@ACT3@@. The records
are `review/qa/kokomi-round-9-2026-09-04/opus-act1.md`, `opus-act2.md`
(the blocked seat), `opus-run2-act1.md`, `opus-run2-act2.md` and
`opus-run2-act3.md`; every claim below names one of them. This is the read
R250 asked for before you play, and it is the Kokomi half of the pool-size
question beside the Klee packet
(`review/active/klee-overhaul-round-9-2026-09-04.md`) and the control record
(`review/records/control-ironclad-2026-09-04.md`).

## 1. The runs in one paragraph

Run one (about 190 actions, seed `F3BMW33EX9H6`): ten fights, The Kin dead,
a deck built on Thoma, Shinobu, Kujou Sara and Bennett riders, and the seat's
best turns were element order inside a turn (`opus-act1.md` §(a)). Run two
(195 then 219 actions, seed `JZ3D0THZH141`): Silver Crucible at Neow, the
Bygone Effigy at 25 of 80, The Kin at 42; act 2 through the Entomancer and
the Knowledge Demon at 379 HP on a Moon, Nereid's Ascension and Sango Isshin
line that paid 62, 78 and a 49-damage double Vaporize on three boss turns
(`opus-run2-act2.md`, the boss). @@ACT3PARA@@ The seats' verdict across
both runs is the same sentence: the Plan decision is real on nearly every
turn, and the dead turns are all hands of basics.

## 2. What the round found

**R250's rules read true.** Feint's single-target Plan struck the Kin
Priest past two Followers, as the skip-Minions rule says
(`opus-run2-act1.md` §(c) 5). The now-lines did what they were for: Kurage's
Oath's 3-to-all was played once in ten fights and its Plan half three times
(`opus-act1.md` §(b)); the seat called the pair "one card and one trap",
which is the weaker now-line by design, and the card is no longer dead in a
hand. Vanguard's 0-cost now-mode was the better mode nearly always, which
is the one now-line that may be too strong; watched, not moved.

**The kit's decision is live, and the seats named four kinds.** Write it or
play it, with the enemy's intent deciding which (`opus-run2-act2.md` §(a));
which Plans and in what order, since they resolve top-down and Exposed
Flank above Kurage's Oath turns 10 into 15 (`opus-run2-act1.md` §(a));
element order within a turn, Pyro then Hydro chaining two Vaporizes for 49
(`opus-run2-act2.md` §(a)); and whether the Kurage carries anything out this
turn, because Sango Isshin reads off it. Hard To Kill and Personal Hive back
to back inverted the same axis twice and the seat called it the best
sequence of the act. That is the same praise the Klee and control seats
gave the base game's inverting enemies, and it is the kit meeting them.

**The pool's empty shelf is tempo, not defence.** The arm carries thirty
rows, thirty of them at a flat cost of 0 to 2, none that gains energy, two
that draw, and none that Retains (`docs/prototype-surface.yaml`, the
`proto_kk_` rows). The seats felt each absence: "energy-capped, never
card-capped", so Lynette's draw was a null play declined twice
(`opus-run2-act1.md` §(b)); "nothing retains", so holding Sango Isshin for
the turn the Plan lands is not a line that exists, and the combo needs the
enabler and the payoff drawn in order with no way to store either
(`opus-run2-act2.md` §(e)); and every dead turn was dilution, a hand of
Defends with no Plan card, in a deck that reached 32 with two forced boss
statuses (`opus-run2-act2.md` §(b)). Klee's shelf was defence; Kokomi's is
the way to hold or hurry a Plan. Pick 1.

**Reactions are a companion's, not hers.** In run two's act 1 every element
the seat could apply was Hydro, so seven reactions were glossed on every
screen and none fired in eight fights (`opus-run2-act1.md` §(c) 8). In act 2
Amber's Pyro made them the deck's best turns. That is the companion layer
working as the brief drew it, and it means a Kokomi deck with no off-element
companion reads a glossary it cannot use; the glossary's length is
`EB-359`'s family and the packet notes it.

**A Plan face is a live projection and nothing says so.** Feint printed
"Plan: Deal 15" in one fight and "Plan: Deal 10" in the next, the enemy's
Vulnerable folded in with no marker, and the seat carried a wrong belief
for three fights before deducing it (`opus-run2-act2.md` §(c) 1). Run one
read the inverse on the same card: the Plan half previewed Vulnerable and
the now half did not (`opus-act1.md` §(c) 3). R246 built the projection
(`EB-334`, read true here: 15 printed, 15 dealt); the marker is `EB-328`'s
pass; the row is at its length ceiling, so the packet cites it.

**The Moon's face says the wrong thing.** The sheet prints "Plans also
happen when played", the C# says "now", and the Bake-Kurage panel says "NOW
as you write them". Run one declined the card twice because it could not
parse the face; run two took it, read "played" as face-up, and burned a
Coral Bulwark+ and a Sango Isshin on one turn (`opus-act1.md` §(c) 10;
`opus-run2-act1.md` §(c) 1). `EB-376`, default applied: the sheet takes the
panel's sentence.

## 3. What the screens got wrong

Each is a row in `BACKLOG.md` on this packet's branch, or cited to one on
main.

- **The Moon's face** (`EB-376`, above).
- **The Plan tip's "never a Minion" reads flat and its modifier line skips
  Strength.** An ALL Plan hit a Minion (Exposed Flank+ on Eye With Teeth)
  while a single-target one skipped two; Kurage's Oath+ printed 4 under
  Vajra's Strength and its Plan 10, and the tip says only that Vulnerable
  counts and Weak does not (`opus-run2-act1.md` §(c) 4, 5). `EB-380`: the
  tip says a single-target Plan skips Minions, ALL means all, and Strength
  does not reach a Plan.
- **Vulnerable is defined on no screen** while Weak, Frail, Slow, Minion
  and every reaction are; Exposed Flank+ was bought on a genre assumption
  (`opus-run2-act1.md` §(c) 6). `EB-377`.
- **Sango Isshin and the Kurage's own hit apply Hydro with no tag** where
  Slack Water, Undertow and Feint print `[Hydro]` (`opus-run2-act1.md` §(c)
  2). `EB-378`.
- **Ayato's "Then deal 12 Hydro damage" never visibly landed** on the turn
  it was played, and the face's "Then" reads as immediate where the hit
  comes when the two turns end (`opus-run2-act2.md` §(c) 3). `EB-379`: the
  face says after, and the log says when.
- **Faces fold modifiers without saying so**, in both directions: the Plan
  line folds Vulnerable and the now line does not; Strength shows on
  Predator+ and Strike and not on Undertow; two totals came in one low
  (`opus-act1.md` §(c) 1 to 3; `opus-run2-act2.md` §(c) 2). `EB-328`'s
  pass, cited.
- **Already rowed, seen again:** Kujou Sara's rider printed under Bennett's
  name and debuffs on Kokomi tagged `(buff)` (`EB-360`); Electro-Charged
  shown on the body as Poison (`EB-357`); Steady sold before it is defined,
  Sown unglossed at the Sapphire Seed, Orobas's Circlet and the Chosen
  Cheese charged for unnamed (`EB-323`); a sale's price and the wallet
  never printed outside the shop (`EB-350`).

Seen and not rowed, because they are the base game's or by design: Strike
Dummy buffing Slack Water, which carries the Strike tag as the starter's
Strike (`ProtoKkSlackWater.cs`, `CanonicalTags`); Hard To Kill's cap sitting
invisibly on Predator+'s 21, the same cap Klee's badge prints and a card
face cannot; potion damage outside Vulnerable and Slow; Skittish not firing
on Thoma's rider; whether an enemy's Block persists; boss statuses that do
not say where they act; two events with no skip.

## 4. What the round did not test

No seat named Tide Wall, Chain of Command, Battle Plan, Change of Plans,
Treatise, Salt Line or The General's Banner, so `EB-362`'s Chain of Command
fix is built and unread live and the kit's own Block wall is still
undrafted after four rounds. Run one's act 2 was the leak, not a read.
@@ACT3TEST@@

## 5. Defaults applied (D and E), disclosed

- **E:** your Kokomi act-1 run is due on this build, `0.2.2309+proto`. R250's
  two rules have been read by two seats across three acts, and the pool work
  in pick 1 is card design inside the brief, not a rule change.
- **D:** `EB-376`, the Moon's sheet face takes the panel's sentence.
- **D:** `EB-380`, the Plan tip's two clauses.
- **D:** Vanguard's now-mode stays at 0; watched on round 10.
- **E:** rows `EB-376` to `EB-380` minted on this branch; four seat records and the blocked seat's record committed beside
  the packet.
- **E:** the round-9 rows for both kits build together on one branch after
  the pool picks, so the seats read one build.

## 6. Picks

1. **How the pool answers tempo.** (1) *Widen the arm by rows that let a
   Plan be held or hurried, every one keyed to the Kurage: a Retain payoff
   that wants the carry-out turn, an energy refund when the Kurage carries
   out, a draw that reads the memory, and a cheap Plan with a now-line
   worth playing. Four to five rows, designed on the round-10 branch, seats
   read them before you do; nothing existing moves* [default]. (2) Keep the
   pool at thirty and read the dilution as the identity: the kit is a flat
   cost curve by the brief, run two cleared two acts on it, and round 10
   re-runs on this pool. (3) The single-card answer: Sango Isshin gains
   Retain and nothing else changes, which gives the combo a place to wait
   and leaves the energy shelf empty.

The rows in (1) are Prototype card design, mine by the routing; the direction
is the pick because the two round-9 packets are the pool-size read you
asked for, and the two kits' empty shelves are different ones.
