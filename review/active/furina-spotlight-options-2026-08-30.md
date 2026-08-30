# Furina — Spotlight: the options packet

> **Lifecycle: RULED. PAPER ONLY.** §5's pick is ANSWERED — **R228
> (2026-08-30) took option (1), one mode, priced** — and still **no code, no
> sheet row, no constant and no LAW line moves because of this file**. §3 is
> the numbered list of design directions as it was offered, in the register's
> numbering; §5 carries the ruling. The pick was [USER]'s (the R212 ladder: "a
> pick between genuinely different design directions" is still his): Claude
> drafted the list and did not choose.

**Date:** 2026-08-30. **Branch:** `furina-paper-2026-08-30`, stacked on
`gpt-review-2026-08-30`. **Authority:** R226 owed this packet
(`review/active/furina-reframe-2026-08-29.md` §3, the appended 2026-08-30
paragraph); R227 pick 4 started it in parallel with Klee's `KLEESPARK-W4`.
**Home of `M45`(4)**, the Spotlight selector amend/accept
(`docs/current/QUEUE.md:65`).

Every `file:line` below was read in this worktree today. Where the reframe
packet quotes a different line for the same fact, the constant has not moved —
the file has, since the reframe was verified at `77eea5f`. Both are noted.

---

## 1. What Spotlight is today

### 1.1 The two modes, and what picks between them

Spotlight is a **designation**. At any moment Furina's `player.spotlight` field
holds one of three things: her own character id (**CENTER STAGE**), the
sentinel string `SPOTLIGHT_GUEST_CAST = "__guest_cast__"`
(`tier0/constants.py:256`, **GUEST CAST**), or nothing at all.

- **Center Stage** lights Furina's own cards. Playing one mints
  `FANFARE_PER_SPOTLIGHT_CARD = 2` Fanfare (`tier0/constants.py:333`, fired at
  `tier0/engine/combat.py:477-479` behind `center_stage_active`). It grants
  **no** numeric bonus — `spotlight_mult` returns 1.0 for self-aim by
  construction (`tier0/engine/effects.py:669-692`).
- **Guest Cast** lights the whole Companion *category* — every Companion card,
  not a named one. Those cards' damage and Block are multiplied, and they mint
  **no** Fanfare.

LAW states the pair as law: "**Spotlight runs in exactly two modes**"
(`docs/current/LAW.md:185-191`), and "**Spotlight/empowerment boosts numbers
only, never turn-economy effects**" (`docs/current/LAW.md:74-75`) — a rule the
engine enforces structurally, since the multiplier is plumbed into damage
(`effects.py:1083`) and Block (`:1227`, `:1258`, `:1323`) and nowhere else.

**What picks between them is a two-line heuristic, not the player.**
`_op_spotlight_designate` (`tier0/engine/effects.py:1861-1892`) reads: if a
non-kit Companion is in hand, Guest Cast; otherwise Furina; otherwise Guest
Cast if a Companion exists anywhere in the deck. That is the selector's whole
brain. E4 recorded the consequence and this packet inherits it: **the heuristic
IS the collapse rule** — it does not lean toward one mode, it decides
outright, and the card the player plays only executes it.

### 1.2 `SPOTLIGHT_BASE_MULT = 1.5`, and where it is read

`tier0/constants.py:225` — **RATIFIED (R71, 2026-07-26)** off the W0 forced-arm
sweep of `{1.25, 1.5}`. (The reframe packet quotes `:151`; the value is
unchanged.) There is exactly one reader: `spotlight_mult`
(`tier0/engine/effects.py:684`), which returns 1.0 unless the card is
*outward*-Spotlighted, then returns `SPOTLIGHT_BASE_MULT` plus any percentage
bonus the player's powers carry:

```
base + bonus / 100.0      # effects.py:688-692
```

`_spotlight_scale` (`:694-696`) applies it, and it reaches damage and Block
only. A companion sibling, `SPOTLIGHT_CARDS_PER_TURN_CAP`
(`tier0/constants.py:292`), is schematized and **OFF** (`None`) — the per-turn
cap LAW names as live has never been switched on.

### 1.3 The selector card

`ethereal_spotlight` — "Ethereal Spotlight" — `tier0/content/cards/tokens.yaml:14-21`:
cost 0, Skill, **rarity `token`** so it can never be drafted, `exhaust: true`,
tags `[ethereal, selector]`, and a body of exactly one op:
`{op: spotlight_designate}`. It is **not** in `docs/furina-cards.yaml` and is
not one of her 84 rows.

It arrives by relic hook, at turn start, once per turn
(`tier0/engine/effects.py:4583-4623`), with a hand-full fallback that discards
one non-kit card to make room rather than silently skipping the grant. LAW
names it kit machinery that "**does not count toward A5**"
(`docs/current/LAW.md:212-213`).

### 1.4 The relic, and the upgrade that deletes the choice

The base starting relic is the `ethereal_spotlight` hook itself, declared at
`tier0/content/characters/furina.yaml:32`. Its whole job is delivering the
selector each turn.

Its **upgraded** form is `touch_of_orobas_furina`, "**The Curtain Never
Falls**" (`tier05/content/relics.yaml:264-302`; C#
`klee-mod/KleeCode/Relics/UpgradedStarterRelics.cs:376`), ruled by [USER] as
red-pen R2 on 2026-07-26. It is **the only row in that file with no number** —
a pure flag, `{hook: spotlight_both_modes}` (`relics.yaml:302`), read in one
place (`tier0/engine/relics.py:281-305`) and surfaced to the four Spotlight
readers by `both_spotlight_modes` (`tier0/engine/effects.py:614-623`). Its
drop weight is 13 (`tier05/relics.py:197`).

With it in play: both halves are permanently on, the targeting is unchanged
(no multiplier leaks onto Furina's own cards, her Companions still mint no
Fanfare), **every `spotlight_moved_this_turn` condition is permanently TRUE**
(`tier0/engine/effects.py:3082`), and — the relic's own comment says so —
**the selector card stops arriving**, because it has nothing left to choose
(`relics.yaml:291-292`, `effects.py:4590-4596`). E4's §2.4 finding, restated
from the source: **the upgrade deletes the mode choice outright.**

### 1.5 The 18 `spotlight` sheet rows

Counted live from `docs/furina-cards.yaml` (84 rows): **0 basic, 4 common, 10
uncommon, 4 rare** — matching the reframe's §2.4 census exactly. No spotlight
row is also tagged `salon`; one is also `fanfare` (`curtain_cue`) and one also
`generic` (`blocking_notes`).

| # | id | line | rarity | what it does with Spotlight |
|---|---|---|---|---|
| 1 | `an_invitation` | `:362` | common | no Spotlight read: generates one common Guest Star |
| 2 | `limelight` | `:365` | uncommon | spends 1 Encore for `spotlight_mult_bonus_turn` +25 this turn, +1 energy, +1 draw |
| 3 | `shared_billing` | `:376` | common | Hydro on a random enemy, `spotlight_mult_bonus_turn` +25, +1 energy |
| 4 | `blocking_notes` | `:383` | common | no Spotlight read: 5 Block, +2 per Companion played this turn |
| 5 | `stage_lights` | `:402` | common | `spotlight_flat_damage_turn` +2, Weak to all enemies, +1 draw |
| 6 | `curtain_cue` | `:408` | uncommon | pays 3 Encore + draw **if the Spotlight moved this turn**, else 1 Encore |
| 7 | `leading_role` | `:603` | uncommon | Power: `spotlight_discount` — the first Spotlighted card each turn costs 1 less (`combat.py:366-368`) |
| 8 | `supporting_cast` | `:609` | uncommon | Power: `spotlight_draw` — the first Spotlighted card each turn draws 1 (`combat.py:488-493`) |
| 9 | `guest_list` | `:612` | uncommon | no Spotlight read: one uncommon Guest Star, +1 energy |
| 10 | `directors_cut` | `:615` | uncommon | +1 energy and 2 draw **if the Spotlight moved this turn**, else 1 draw |
| 11 | `take_it_from_the_top` | `:623` | uncommon | 5 Block, plus 10 damage **if the Spotlight moved this turn** |
| 12 | `top_billing` | `:654` | uncommon | Power: `spotlight_mult_bonus` +25 for the rest of combat |
| 13 | `duet` | `:663` | uncommon | no Spotlight read: replays the next Companion this turn, +1 draw |
| 14 | `standing_ovation` | `:666` | uncommon | Power: `ovation_spend_boost` (every Encore spend adds +10 to the turn multiplier, `resources.py:380-384`) and `spotlight_encore_first` |
| 15 | `encore_performance` | `:844` | rare | copies a Spotlighted card in hand (`effects.py:2153-2173`) |
| 16 | `star_of_the_show` | `:913` | rare | Power: `spotlight_flat_damage` +5 on Spotlighted damage ops (`effects.py:1087-1089`) |
| 17 | `prima_donna` | `:928` | rare | Power: `spotlight_discount` +1 and `spotlight_draw` +1 together |
| 18 | `command_performance` | `:976` | rare | no Spotlight read: two uncommon Guest Stars |

**Four families, and they do not migrate together.**

- **A — the five outward-multiplier rows** (2, 3, 5, 12, 16, and half of 14):
  dead text under Center Stage, because `spotlight_mult` short-circuits to 1.0
  on self-aim and `spotlight_flat_damage` is gated on
  `is_outward_spotlighted`. They need Guest Cast to mean anything.
- **B — the three designation-event rows** (6, 10, 11): they read
  `spotlight_moved_this_turn`, which the drafter prices at
  `STATIC_SPOTLIGHT_MOVED_SHARE = 0.167` — one turn in six
  (`tier05/draft.py:79`, read at `:176`) — and which the upgraded relic makes
  permanently true.
- **C — the four first-Spotlighted-card-window rows** (7, 8, 14, 17) **plus the
  copier** (15): mode-agnostic. They ask `is_spotlighted`, which is true of
  Furina's cards under Center Stage and of Companions under Guest Cast, so
  they work in either mode.
- **D — the five rows with no Spotlight read at all** (1, 4, 9, 13, 18): Guest
  Star generators and Companion riders, tagged `spotlight` because they feed
  the plan, not because they read it.

**How many are already covered by the reframe's §7 blast radius?** All 18, and
in one line: §7 says "**The 18 `spotlight` rows. Untouched.**" None of them is
among §7's eleven Fanfare-meter readers, none is among its 26 `salon` rows, and
exactly one (`curtain_cue`) sits inside its 30 `fanfare`-tagged rows. So the
reframe's migration cost and this packet's are **disjoint**: whatever is
decided here is additional work, not a re-cut of work already counted. On the
test side the reframe cites E4's census — 18 test files referencing spotlight,
6 pinning the plan name as a string literal; a re-count today reads 22 files
under `tier0/tests/` mentioning spotlight and 4 pinning `"spotlight"` as a
quoted literal, against a suite that has grown to 227 files. The order of
magnitude is what matters and it has not changed.

---

## 2. Why it is a hole under the reframe

The reframe gives Furina one board (the Salon), one scaling meter (Fanfare as
Focus), one aiming currency (Encore), and one hook that ties the Companion half
to the board half (a Companion play makes one member perform and rotate). Every
one of those sentences is about *making the stage act*. Spotlight sits beside
that architecture untouched, and under it Spotlight stops being a choice at
all: **the reframe's own ruled §4.1 retires `FANFARE_PER_SPOTLIGHT_CARD`,
which is Center Stage's entire mechanical payoff** — so one of the two modes
would ship with nothing in it, and a selector that "chooses" between a
multiplier and nothing is not a decision, it is a cutscene. Meanwhile the
multiplier itself is now a *second* scaling system pointed at the same action
the board already rewards: a Companion play triggers a member (scaled by
Fanfare) and is itself scaled by `SPOTLIGHT_BASE_MULT` (a different number,
from a different source, shown in a different place), which is exactly the
"cards competing for space" failure [USER]'s framing message asked the design
to avoid. Leaving it as it ships means shipping a collapsed selector, a dead
mode, two scaling numbers on one play, and a relic upgrade whose stated effect
is to delete the choice.

**No new design is proposed in this section.** The options are §3's.

---

## 3. The options

Five directions. They are genuinely different — not five prices for one idea —
and each is stated with what it costs to build and what it puts at risk.

Two constraints bind all five and are called out where they bite. **LAW's
Funnel Contract** names **Spotlight-is-a-designation-event** as a contracted
visual binding point, and a breach is stop-work on that track
(`docs/current/LAW.md:523-527`). **LAW's companion-synergy clause**
(`docs/current/LAW.md:93-97`) permits Furina to route damage through
*empowered* Companions, but the delete-test still has to gut the deck when her
own cards are removed.

### Option 1 — ONE MODE, PRICED. Guest Cast survives; the selector aims and costs Encore.

**What Spotlight becomes:** one mode. Center Stage retires with its own payoff
(`FANFARE_PER_SPOTLIGHT_CARD`, already retired by the reframe). The
designation event *survives* — but what it chooses changes from "which of two
modes" to "**which Companion, or which Companion class, the light is on**",
and playing the selector costs **Encore**, the reframe's own aiming currency.
The heuristic selector is replaced by a player decision with a price.
**The 18 rows:** family A's **5 kept unchanged** — the multiplier is still
there and still outward. Family B's **3 kept**, and they get *better*: with a
real, priced designation the `spotlight_moved_this_turn` window stops being a
heuristic artefact priced at one turn in six. Family C's **5 kept** —
`is_spotlighted` still answers, on a narrower target. Family D's **5 kept**.
Net: **18 kept, 0 retired**, with re-pricing owed on family B once the
designation rate is measured rather than assumed.
**Selector / relic / the 1.5:** the token stays and gains a cost;
`SPOTLIGHT_BASE_MULT = 1.5` stays as the outward term; the base relic keeps its
job; **"The Curtain Never Falls" must be re-authored**, since "both modes at
once" is meaningless with one mode — the natural replacement is "the selector
is free" or "the designation persists through a re-aim", which restores the
upgrade's shape (never having to choose) without deleting the choice for
everyone else.
**Co-op:** unchanged in kind, and slightly richer — an ally's Companions are
lit or not by a decision Furina's seat made and paid for.
**Build cost:** moderate. A new target type for the designation, a cost on the
token, the upgraded relic re-authored, the two-mode assertions in LAW and the
tests rewritten. No sheet row is retired.
**Biggest risk:** **a third claim on Encore.** Encore is already the deferred
Block *and* the Evoke price (`F7` = 1). Adding a designation price makes three
consumers of one unbounded buffer, and if it is under-priced it is free while
if it is over-priced the Evoke family starves. That is a real interaction with
slots 2 and 3 of the reframe's own slate and it is stated here rather than
discovered later.

### Option 2 — ACCEPT. Ship Spotlight exactly as it is.

**What Spotlight becomes:** unchanged. Two modes, a heuristic selector, `1.5`,
the token, the relic, the upgrade that deletes the choice.
**The 18 rows:** all 18 kept, 0 re-authored, 0 retired.
**Selector / relic / the 1.5:** all unchanged.
**Co-op:** unchanged — Spotlight is single-seat and does not touch the table.
**Build cost:** zero.
**Biggest risk:** it ratifies a mode that the reframe empties. With
`FANFARE_PER_SPOTLIGHT_CARD` retired, Center Stage does nothing at all, so
family A's five rows become the only Spotlight rows that pay and the selector's
"choice" is between a multiplier and a no-op. It also leaves the collapse
finding standing and unanswered on the record.

### Option 3 — FOLD SPOTLIGHT INTO FANFARE. One scaling number for the whole character.

**What Spotlight becomes:** a property of the meter. `SPOTLIGHT_BASE_MULT`
retires and Companion card numerics scale off **held Fanfare**, the way member
numerics already do through `SALON_FOCUS_PER`. One meter, one tier, one number
on screen, scaling both halves of her kit.
**The 18 rows:** family A's **5 re-author** — a percentage bonus on a retired
multiplier has to become a bonus on the Focus term instead. Families B and C's
**8 re-author or retire**, depending on whether any designation event survives
at all. Family D's **5 kept**. Net: **13 re-authored, 5 kept**.
**Selector / relic / the 1.5:** the 1.5 retires; the token retires or becomes a
Fanfare verb; both relics need re-authoring.
**Co-op:** unchanged.
**Build cost:** high, but concentrated — one term replaces another, and 13
bodies follow it.
**Biggest risk:** it directly loads the invariant the packet just drafted.
§3.1 amendment 4 (**countersigned as PROSPECTIVE by R224**) says the Focus term
scales *performance numerics only* — a member's damage and Block — and this
option points the same meter at card bodies. That is not a contradiction (the
amendment binds the term applied to member performances and says so), but it is
the second application of one number and it needs its own written bound before
it is safe. The secondary risk is compounding: Companion plays mint Fanfare
through the trigger, and Fanfare would then scale Companion plays.

### Option 4 — FOLD SPOTLIGHT INTO THE STAGE. The front member is the spotlit one.

**What Spotlight becomes:** a **slot**, not a card class. The light sits on the
front Salon member. A Companion play triggers that member (as the reframe
already rules) and the multiplier applies to *that performance*. Evoking moves
the light with the queue. `salon_rotate` becomes the aiming verb for Spotlight
as well as for the trigger and the Evoke — one verb, one order, one lesson.
**The 18 rows:** family A's **5 re-author** onto the member's performance
rather than the Companion card. Family B's **3 kept in shape**, re-based from
"the Spotlight moved" to "the queue rotated", which is a *more* frequent and
far more legible event than one turn in six. Family C's **5 retire or
re-author** — the first-Spotlighted-*card* window has no meaning when the light
is on a board slot. Family D's **5 kept**. Net: **8 re-authored, 5 retired or
re-authored, 5 kept**.
**Selector / relic / the 1.5:** the 1.5 survives as the front-slot multiplier;
the token survives only if the designation stays a player choice (aiming the
light at a slot other than the front), otherwise it retires; the relic and its
upgrade re-author.
**Co-op:** **this is the option co-op changes most.** An ally's Companion plays
already rotate Furina's queue without asking (§3's stated cost); under this
option they also move the light. That makes the reframe's slate slot 7 —
already an OBSERVATION slot with no instrument — considerably more load-bearing.
**Build cost:** moderate-to-high, and it lands on the same code the reframe is
already rewriting, which is an argument for doing it in the same slice rather
than after.
**Biggest risk:** it removes the Companion *card* empowerment that LAW's
companion-synergy clause names (`LAW.md:93-95`) and replaces it with board
empowerment, so Furina's Companion half loses its numeric coupling to her.
Second risk: on a one-member stage the light never moves (the §2.7b constraint
the reframe already carries), so every "the light moved" payoff is worth zero
on the board a starter deck actually has.

### Option 5 — RETIRE Spotlight entirely.

**What Spotlight becomes:** nothing. The designation, both modes, the
multiplier, the selector token and the relic flag all go. Companions are
ordinary cards that trigger the stage.
**The 18 rows:** family A's **5 rows retire or are re-authored** (their bodies
are pure Spotlight terms); family B's **3 rows re-author** (their condition
ceases to exist); family C's **5 rows re-author** onto a different trigger
("the first Companion played each turn" is the obvious one, and it is not a
Spotlight read); family D's **5 rows are untouched** and simply lose the tag.
Net: **5 retired or re-authored, 8 re-authored, 5 kept**.
**Selector / relic / the 1.5:** the token retires; `SPOTLIGHT_BASE_MULT`
retires; the starting relic needs a new job entirely, and "The Curtain Never
Falls" has nothing to flag.
**Co-op:** simpler — one less single-seat system.
**Build cost:** the largest of the five. Thirteen sheet rows, a starting relic,
an upgraded relic, a token, four engine readers, the C# `SpotlightSystem`, and
every test that pins the modes.
**Biggest risk:** it breaches the Funnel Contract's Spotlight binding point
outright (`LAW.md:525-527`) and it removes Furina's only *numeric* companion
coupling, which is the mechanism LAW's companion-synergy clause was written
for. It also spends a starting relic and its ruled upgrade — a [USER] design
(R2) — to buy simplicity.

### Where `M45`(4) lands

`M45`(4) asks for the Spotlight selector to be **amended or accepted**
(`docs/current/QUEUE.md:65`). **Option 2 is "accept" in so many words.**
**Option 1 is the narrowest "amend"** — it keeps the selector and changes what
it chooses and what it costs. **Options 3 and 4 amend it by making it something
else** (a Fanfare verb; a slot-aimer), and **option 5 answers `M45`(4) by
deleting its subject.** Whichever is picked, `M45`(4) closes on the answer;
`M45`'s other six items are untouched by this packet.

---

## 4. Claude's recommendation

**Option 1 — one mode, and the selector aims and costs Encore.**

Center Stage's only mechanical payoff is retired by the reframe's own ruled
§4.1, so "accept" would ratify a branch that is already empty and the two-mode
law would describe a system with one mode in it. Option 1 is the smallest
change that converts the collapsed heuristic into a real decision, because a
designation that costs Encore is priced under D3 and steerable under D2, which
is precisely what the collapse finding says is missing. It is also the only
option of the five that keeps the Funnel Contract's Spotlight binding point,
the starting relic's job, and LAW's companion-synergy clause all intact at
once.

**What would change it.** Two readings, both already scheduled. If the
reframe's slate **slot 2 or slot 3** shows Encore is fully subscribed as the
Evoke price — graders naming the buffer as the reason they decline an Evoke —
then a third consumer would starve the family [USER]'s brief calls central, and
**option 3** becomes the better answer because it prices nothing. If the
whole-fight gate (§6.4) shows Companion density is already the dominant lever
on the board, so that Companion plays need no second multiplier at all, then
**option 4** is better because it puts the scaling where the decisions are. A
third, blunter reading: if the migration read finds family A's five rows do not
survive re-basing in any option, the cost gap between 1 and 5 narrows and
retirement stops looking expensive.

---

## 5. The pick

**RULED (R228, 2026-08-30): option (1).** One mode, priced — Center Stage
retires, Guest Cast and `SPOTLIGHT_BASE_MULT = 1.5` stay, and the selector aims
a Companion and costs Encore. §4's own biggest risk is tested rather than
assumed away: **the third claim on Encore is measured by the slate slot below,
staged as a MATCHED PAIR against slot 2 (the Evoke price), and the designation
price RETURNS with evidence if Encore proves over-subscribed.** `M68` closes
and `M45`(4) is answered with it. **Nothing migrates before the reframe's own
whole-fight read.**

**ONE numbered pick list for [USER]. Item (1) is Claude's recommendation.**

**`Spotlight`. What happens to Spotlight under the reframe?**

1. **One mode, priced** — retire Center Stage, keep Guest Cast and the 1.5,
   keep the selector card but make it aim at a Companion target and cost
   Encore; re-author "The Curtain Never Falls". *(Claude's recommendation.)*
2. **Accept** — ship Spotlight exactly as it is, two modes and all, and record
   that the collapse finding stands unanswered.
3. **Fold into Fanfare** — retire the 1.5 and let held Fanfare scale Companion
   card numerics the way it scales member numerics.
4. **Fold into the stage** — the light sits on the front Salon member;
   `salon_rotate` aims it.
5. **Retire Spotlight entirely** — modes, multiplier, selector and relic flag
   all go; the 18 rows re-home onto Companion triggers or lose the tag.

**What Claude does after each answer.** In every case the migration is a
row-by-row read committed before any edit, and no sheet row moves before the
reframe's architecture has a verdict (§7 of the reframe: sheet edits are a
`CONSTANTS_VERSION` event and they happen *after*).

- **(1)** Re-price family B's three rows against a measured designation rate
  rather than `STATIC_SPOTLIGHT_MOVED_SHARE = 0.167`; re-author the upgraded
  relic; and **add one slate slot** to the reframe's §6.3 — *is the Encore
  price on the designation a real cost beside the Evoke price?* — staged as a
  matched pair against slot 2, because the two compete for the same buffer.
- **(2)** Nothing migrates. Claude records the acceptance against `M45`(4) and
  the collapse finding is closed as ruled-and-accepted rather than open.
- **(3)** Draft the second bound on the Focus term first (§3.1 amendment 4
  binds member performances; a card-body application needs its own sentence and
  its own countersign), then re-author family A's five rows onto the Focus
  term. **One slate slot added:** *does one meter scaling both halves read as
  one system or as one number doing too much?*
- **(4)** Re-base family B onto queue rotation, re-author family A onto the
  front member's performance, and triage family C row by row. **Two slate slots
  added:** one on whether the light reads as being on the board, and one
  **upgrading slot 7 from OBSERVATION to a real prediction**, because under
  this option an ally's Companion plays move the light and the co-op cost stops
  being a footnote.
- **(5)** A retirement packet: the thirteen rows, the token, both relics, the
  four engine readers and the C# system, plus the Funnel Contract breach
  flagged in the PR per `LAW.md:527`. No slate slot is added — there is nothing
  left to predict about.

---

## 6. What this packet does NOT do

- **No implementation.** No C#, no `tier0`, no test, no constant.
- **No sheet edits.** `docs/furina-cards.yaml` is read-only here; not one of the
  18 rows is touched, re-tagged or re-priced.
- **Nothing here implements the ruling.** §3's five options are directions and
  §4 is a recommendation; §5's pick is answered by R228 at option (1), and that
  answer closes `M68` and `M45`(4) and nothing else. **No LAW text is drafted
  and no sheet row moves** — the migration §5's `(1)` bullet describes is the
  next unit of work, and it waits on the reframe's own whole-fight read.
- **No re-opening of the reframe.** The reframe's countersigned §3 and §3.1 and
  R224's F-pick answers are untouched by this packet; the only line it adds
  there is the dated pointer under the R226 paragraph.
