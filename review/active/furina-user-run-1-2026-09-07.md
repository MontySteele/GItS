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
now targets (`EB-630`-`EB-640`):

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

## 5b. The frames, taken 2026-09-07 on `0.2.2927+proto`

Lane-1 runs of `understudy/scenarios/furina-combat-sequence.yaml`, captured
by `understudy.harness frame` (Guardrail-7: material, not evidence):

- **Beat 1**, the full stage at Encore 0:
  `understudy/logs/frames/frame-20260907-163516-furina-seq-t05.png`. The
  panel above Furina; "Encore 0" with dim pips, "Fanfare 13", "Member bonus
  +1"; chip 0 "FRONT" with "Evoke 14 Hydro"; "Reduced performance". The
  chip numbers run together across the chips and the Evoke line sits on
  the reduced note (`EB-639`).
- **Beat 2**, the front member performing on a Companion card:
  `frame-20260907-163926-furina-seq2-t07.png`. In the fight; "Encore 1",
  "Fanfare 15"; the front Chevalmarin's Evoke line carries "+3 Encore";
  nothing beside the energy orb; no meter in the status row.
- **Beat 3**, the fourth Deploy evoking the front member:
  `frame-20260907-164358-furina-seq4-t09.png`. The Evoke was lethal, so
  the frame is the loot screen with the panel still drawn behind it
  (`EB-640`: the panel outlives the fight).

The first frame of the day, before the panel
(`frame-20260907-154029-furina-strip-t4.png`), is what [USER]'s and GPT's
notes in §3b were written on.

## 5c. Passes three and four (2026-09-07, evening)

- **Pass three** (`EB-639`/`640`/`641`, Opus, PR #426, `0.2.2958+proto`):
  `frame-20260907-173119-furina-p3-t05.png` (full stage) and
  `frame-20260907-173214-furina-p3-t10.png` (after the Companion play).
  GPT's read on them, relayed by [USER]: readable, but "several widgets
  assembled together" (the header floating above the chips, the replace
  text on its own strip, "Reduced performance" hanging under); "+1 at 10"
  beside Fanfare 13 ambiguous; FRONT names position, not the trigger; no
  frame showed the replacement. That verdict triggered the rule in §5: the
  next pass went to a Fable agent, not Opus.
- **Pass four** (`EB-644`, with `EB-637` hover previews and `EB-638` the
  tip clause folded in; PR #430, `0.2.2985+proto`): one backing and inset
  with a hairline per row gap; the width a function of the chip count
  only, every header and footer string pinned inside the slot row;
  "Encore 0 · Reduced" on the Encore line and the notice row gone; one
  footer, the front member's replacement, bright while a Deploy is hovered;
  PERFORMS / LEAVES / ENTERS on the chips from the game's own hovered-card
  tracker; the Fanfare hover names the next threshold ("Bonus +2 at 20").
  Frames on a lane-1 run of the same scenario, the fourth Debut now granted
  just before beat 3 (five grants over a drawn hand of six overflowed the
  hand cap and the game dropped one):
  `frame-20260907-184115-furina-p4b-t01.png` (beat 1: Crabaletta FRONT
  "5 damage", two Ushers "3 Block", "Encore 0 · Reduced", "Fanfare 13 ·
  Bonus +1", "Replace: 14 damage"),
  `frame-20260907-184140-furina-p4b-t03.png` (beat 2: "Encore 1" with one
  pip, the front Usher "4 Block", "Replace: 9 Block"),
  `frame-20260907-184206-furina-p4b-t05.png` (beat 3, after the fourth
  Deploy: Usher FRONT "3 Block", Crabaletta "6 damage", Chevalmarin "3
  damage", "Encore 0 · Reduced", "Fanfare 22 · Bonus +2"). The hover states
  are not in any frame; the runner has no hover step. Sent with a one-page
  brief for GPT's next read; the eyes-on in §5 stays open until [USER]
  says the panel reads.

## 5d. The hover baseline (2026-09-07, night, `0.2.3002+proto`)

The scenario runner gained a `hover` step (`EB-652`, PR #436: a debug op on
the mod's own route that calls the game's hovered-card tracker, the pair the
panel's patches listen to), and `understudy/scenarios/furina-hover-states.yaml`
was run on lane 1 with captures alongside. Frames:
`frame-20260907-210218-furina-hover-t01.png` (Chevreuse hovered: the front
Crabaletta chip reads PERFORMS in a lit frame),
`frame-20260907-210244-furina-hover-t03.png` (a Salon Début hovered on the
full stage: the front chip reads LEAVES and the footer "Replace: 14 damage"
brightens; measured, the footer text averages 172/167/159 against 118/130/152
at rest), `frame-20260907-210309-furina-hover-t05.png` (Ethereal Spotlight
hovered at Encore 0: no pips to tint, so the resting FRONT state; the tint
needs a board with Encore 2). ENTERS (a Deploy onto a stage with room) needs a
different board and is not framed. This is the baseline GPT asked for; the
direction pick (`review/active/furina-stage-direction-2026-09-07.md`) decides
what is built on it.

## 6. Defaults applied, disclosed

- **`EB-627`**, **`EB-628`**, **`EB-629`** as above, E defaults, built by
  Opus on `furina-ui-builds-2026-09-07`, not deployed until [USER]'s game
  is closed.
- No shipped-sheet number moves; no stamp moves; nothing measured.
