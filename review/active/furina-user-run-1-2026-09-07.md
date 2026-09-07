Status: OPEN (one eyes-on, §5; three E defaults applied, §6)

# Furina, [USER]'s first act-1 run under the reframe: the UI is still not legible; the Encore idea is liked, the stage is not readable

Written 2026-09-07. [USER] played Furina's act 1 on `0.2.2888+proto` (main
`da0e5846`: the reframe of R220 and R260, the six audited rows of
`review/records/card-audit-2026-09-07.md`, the fixer-T faces of #413). The
run was short: the log has her embarking at Ascension 2 and dying to a
Corpse Slug, an early act-1 hallway enemy, within the first fights (the
capture taken at the end shows the Devastation screen at 0 of 89). [USER]'s notes are about the interface, not the kit,
and are quoted in the commit that carries this packet. Material: the frame
`understudy/logs/frames/frame-20260825-190421-s4g17-salon-stage.png`
(Guardrail-7: a frame is material for a person, and nothing a model reads
off it is a legibility claim; the claims below are [USER]'s).

## 1. The verdict

**"Furina still has basic UI legibility issues."** The Encore idea, "how
many ticks of the stage do you have available", is not bad; the energy orb
icon is liked. But it is too hard to tell who the stage members are or
what they will do, the Encore and Fanfare displays need rethinking along
with the Salon layout, and the Salon tooltip is still a wall of text. No
verdict on the kit's fun is given, and none is recorded: a kit whose board
cannot be read is not yet graded on play. **The stage holds at Prototype**;
the interface is rebuilt first.

## 2. What is on the screen today, and why it fails

The stage is three freestanding blue silhouettes at Furina's feet with a
small badge under each (a shield 3, a drop 2), an Encore ribbon under them
with one number, and an overhead bar reading "10/70". That is the D4
redesign of 2026-07-24, whose reason was that framed portraits had read as
"three identical blue smudges"; the silhouettes read the same way at combat
scale, and nothing on the stage says what a member will do next or which
one is the front. The overhead bar is the shipped Burst meter's shape, and
under the arm Fanfare has no cap, so "of 70" is a number that means
nothing. The Salon tooltip under the arm is one paragraph of about 700
characters carrying seven rules.

## 3. The defaults, applied (E)

**`EB-627` a member strip.** The silhouettes go. Under Furina, a strip of
up to three chips, left to right as the performance queue: the member's
face crop, its name, and its next act as a number and a word ("6 Hydro",
"3 Block", "Hydro to ALL"). The front member is marked, so "a Companion
card performs the front member" can be read off the strip before the card
is played. Duplicates are legal and render as duplicates (Funnel Contract
§1 stands).

**`EB-628` Encore as pips, Fanfare as a badge.** The Encore ribbon becomes
a row of pips on the strip, one per performance the stage can still pay
for this fight, with the Spotlight's price of two marked; that is the
"ticks available" reading [USER] liked, drawn as ticks. Fanfare leaves the
overhead bar and becomes a number beside the energy orb on the pattern the
Spark badge set (`EB-621`), with the next threshold beside it ("6, next +1
at 10") so the only thing Fanfare does under the arm is visible where it
is counted. The overhead bar is off under the arm.

**`EB-629` the Salon tip in three sentences.** The cap; what performs
(a Companion card performs the front member, a Deploy performs the member
it adds, and onto a full stage first Evokes the front one); the Fanfare
bonus. The clauses on Attacks, Shatter, when-hit powers and Minions move to
the Evoke tip and the member tips, where they are read at the moment they
matter.

## 4. What this does not touch

The kit's rules, numbers and pool. Round 17's hypothesis (the r16 packet)
runs unchanged once the strip is in.

## 5. Eyes-on

**A frame on the next `+proto` deploy**, taken in a fight with a full
stage and a lit Spotlight: does the strip say who and what, do the pips
read as ticks, does the Fanfare badge read beside the orb. [USER] vetoes
on sight; a veto returns the layout to design, not to the silhouettes.

## 6. Defaults applied, disclosed

- **`EB-627`**, **`EB-628`**, **`EB-629`** as above, E defaults, built by
  Opus on `furina-ui-builds-2026-09-07`, not deployed until [USER]'s game
  is closed.
- No shipped-sheet number moves; no stamp moves; nothing measured.
