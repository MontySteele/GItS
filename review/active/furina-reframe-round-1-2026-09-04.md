Status: OPEN (PR = [USER]; one pick in §6)

# Furina reframe round one: act 1 cleared at 8 HP, and the shipped Burst that won it

One pick in §6, with a marked default. Everything else is a default, applied
and disclosed in §5.

Written 2026-09-04. R250 pick 5 lifted the R220 B sequence, so the reframe's
first blind round ran the same day: the dev build `0.2.2309+proto` with all
four arms on, the three-fight soak green (`fights=3 defects=0`), one seat on
lane 2 at Ascension 2, seed `D9MY3R07XBD1`. The seat was Claude Sonnet, not
Opus, because Opus was out for the morning; the record says so in its first
line. It is `review/qa/furina-reframe-round-1-2026-09-04/opus-act1.md`, and
every claim below names a fight and round in it.

## 1. The run in one paragraph

About 150 actions, act 1 cleared, no fight lost. Wrigglers ×4 ground the seat
from 78 to 43 (fight 2), Byrdonis took it to 51, the Fuzzy Wurm Crawler did no
damage at all, and the Ceremonial Beast (252 HP) took it to 8 on round 10
under the second Ringing and then died on round 13 to Applause Line+, the one
card that was both legal under Ringing and lethal. One caveat on provenance:
an Opus seat had played the first few actions before the outage cut it off
and left no record, so this seat picked the run up at 62 of 78 and its Neow
paragraph describes a pick it may not have made. Nothing after the first fight
is affected.

## 2. What the round found

**The reframe's rules read true wherever the seat met them.** A deploy
performs at once: Salon Début's member hit the Cryo-wearing slime with Hydro
the turn it entered and froze it (fight 1, round 3). The Spotlight is one
mode, aimed: Ethereal Spotlight spent Encore and Guest Cast appeared with no
choice offered (fight 1, round 1). A deploy onto a full stage Evokes: Full
Ensemble on a 3-of-3 stage paid all three members' bows in one card, the
boss went 56 to 28, the seat gained 12 Block and Fanfare rose 26 (fight 5,
round 12). The seat called that last one the run's real decision and said it
was "betting on my own model of the system": the overflow Evoke is the slot-6
rule, and it is printed on no card. The meter ledger on the lane records only
the Spark meter, so Fanfare minting is not confirmed by an instrument, only
by the seat's numbers.

**The shipped Burst carried the boss, and it is not the reframe's.** The
seat's Burst meter read `78/70`, over its own cap, and Let the People
Rejoice arrived off that overflow: 14 to all for 0 and 6 Encore back, the
turn that took the boss from 28 to 14 (fight 5, round 12). Under R220 B the
Burst fold is the last of the three, so the shipped meter and card still run
beside the reframe's own meter. The reframe's Rare drain payoff and the five
`proto_fr_` rows were never offered, so round one read the reframe's loop
with the shipped kit's payoff bolted on. That is the new fact behind §6.

**Where the decisions were.** The seat named two kinds: sequencing under a
number it could read (Vulnerable before the two big hits to cross the
Beast's 150 stun line in one turn, fight 5 round 5; the one card under
Ringing, rounds 8 and 10) and the Full Ensemble gamble above. Fights 1, 3
and 4 were "attack with what is in hand, block with the rest" with one
attack card a turn, which the seat called automatic. The card it was
happiest to draw was Applause Line+, the Fanfare-scaled 0-cost attack, which
is the reframe's meter paying out on a card; the ones it never wanted were
Slimed and Infection.

## 3. What the screens got wrong

Each is a row in `BACKLOG.md` on this branch.

- **Ethereal Spotlight played at 0 Encore and did nothing** (`EB-364`): no
  refusal, no Guest Cast, no line; the seat found out two turns later.
- **The Burst meter prints over its cap and the shipped card rides the
  overflow** (`EB-365`), gated on §6.
- **The reaction preview said "Bosses cannot be Frozen" on an Elite that
  then froze** (`EB-366`).
- **Ringing is named nowhere before it lands, and Swirl's tip does not say
  the aura goes to every enemy** (`EB-367`).

Seen and not rowed, because they are the base game's: two enemies' Empower
intents meaning +2 a turn and +7 once under the same word; Energy printing
`5/3` off the Venerable Tea Set; Slimed and Infection as dead draws.

## 4. What the round did not test

The five `proto_fr_` rows (the named deploy, two Evokes, the drain pair)
were never offered, so the aimed Evoke and the drain are unread. Acts 2 and
3 are unplayed. The seat was Sonnet; a later Opus round is the comparable
one against Klee and Kokomi's records. The arm's Fanfare minting is read
off the seat's numbers, not a ledger.

## 5. Defaults applied (D and E), disclosed

- **E:** the round ran on the installed build with no change; no stamp
  moved, nothing measured.
- **E:** four rows minted as listed; the record committed beside the packet.
- **E:** your Furina act-1 run is due on this build: it is the first build
  of her rules (CLAUDE.md, when [USER] plays), and none of the four rows
  changes a rule. §6's pick does, so play before it lands if you want the
  round the seat saw, or after if you want the reframe alone.

## 6. Picks

1. **The shipped Burst under the Furina arm.** R220 B put the Burst fold
   last; the new fact is that the shipped Burst decided the boss fight in
   the reframe's first round, and will sit inside every Furina read until it
   goes. (1) *Retire the shipped Burst meter and Let the People Rejoice
   under the Furina arm now, arm-only, so round two reads the reframe on its
   own engine; the shared retirement branch (`EB-199`, `EB-200`) still owns
   the shipped engines and nothing there moves* [default]. (2) Keep R220 B's
   order: the shipped Burst stays beside the reframe until the shared
   retirement lands, and every Furina round is read with it in. (3) Keep the
   meter, cap it at 70 and let the card stand in for the drain payoff until
   the `proto_fr_` drain rows are read.

The retirement in (1) is a prototype-arm build, D by the ladder, and rides
round two with `EB-364` to `EB-367`; the seats read it before you do.
