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

## 3b. The layout revised on the first frame (2026-09-07, evening)

The first build of §3 was deployed (`0.2.2917+proto`) and a lane-1
scenario produced a frame (`understudy/logs/frames/frame-20260907-154029-
furina-strip-t4.png`). [USER] on it: the font and icon sizes need
controlling, Fanfare too large; Encore not visible anywhere; Encore,
Fanfare and the member count should leave the power row. GPT, on the same
frame: the problem is hierarchy and placement more than size, Fanfare
nearly as prominent as Energy while the members a decision is about are
tiny, low-contrast and overlapping the health area; the modifier read at
bottom left is separated from the effects it modifies. Both are taken,
and the widgets become **one Salon panel**, the shape the follow-up build
now targets (`EB-630`-`EB-638`):

- **One group beside Furina**, above and clear of her HP bar and status
  row, wide enough for three distinct chips, on a restrained dark backing,
  anchored to her combat area so hand expansion and targeting never cover
  it.
- **Each chip**: portrait, short name, and its current performance effect
  as the largest thing on it ("5" with the Hydro icon, "3 Block"),
  duplicates visibly separate. **Chip 0 says "FRONT"** in words; a gold
  border alone does not teach who performs.
- **A resource line on the panel**: "Encore N · Fanfare N · Member bonus
  +N". Encore has a name and a number before any pips; Fanfare's next
  threshold lives in its hover, not on the line; the Fanfare badge beside
  the energy orb goes, and Energy stays where it is.
- **Pips are secondary**: visible at zero, never permanently coloured as
  the Spotlight's price (a hover on the Spotlight shows what it would
  spend, if cheap; else the colouring simply goes). At Encore 0 the chip
  numbers fold the dry cut and the panel says "Reduced performance", so
  an empty meter does not read as a stopped stage.
- **A hierarchy table, not a scale table**: performance numbers first,
  names and the resource line second, explanations third, every element
  reading its tier.
- **Card-hover previews** are the next wave (`EB-637`): a Companion card
  highlights the front member; a Deploy on a full stage marks who leaves,
  shows the Evoke payoff with Chevalmarin's refund and where the newcomer
  enters; the Encore change is previewed with them. This is the biggest
  step past static layout and is built after the panel lands.
- Also from the frame and the review: the Spotlight refused after three
  deploys (`EB-631`): measured off the scenario's own log, Encore went 2,
  1, 0, 0, because R260's free arrival is Crabaletta's opening one only
  (`EB-553`, `EB-558`) and a Deploy's performance pays 1, so the refusal
  was correct and the packet's "three free arrivals" above was wrong; the
  Spotlight window tip's last clause says the same wrong thing and is
  corrected (`EB-638`). Member tips carrying clauses about effects the
  member lacks (`EB-632`), Chevalmarin's Evoke label without her refund
  (`EB-630`), the meters out of the power row (`EB-636`).

**The eyes-on is revised with it (§5):** not one frame but the short
combat sequence GPT proposed, a frame at each step: identify who acts,
predict the number, spend Encore, replace the front member.

## 4. What this does not touch

The kit's rules, numbers and pool. Round 17's hypothesis (the r16 packet)
runs unchanged once the strip is in.

## 5. Eyes-on

**A short combat sequence on the next `+proto` deploy**, a frame at each
step on a lane-1 scenario: a full stage; a Companion card hovered and
played (who performs, at what number); Encore spent to zero (the reduced
numbers and the "Reduced performance" note); a Deploy onto the full stage
(who leaves, the Evoke line with the refund, who enters). [USER] vetoes on
sight; a veto returns the layout to design, not to the silhouettes.

## 6. Defaults applied, disclosed

- **`EB-627`**, **`EB-628`**, **`EB-629`** as above, E defaults, built by
  Opus on `furina-ui-builds-2026-09-07`, not deployed until [USER]'s game
  is closed.
- No shipped-sheet number moves; no stamp moves; nothing measured.
