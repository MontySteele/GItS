# Open playtest items, all sprints

> ## SUPERSEDED AS THE CROSS-SPRINT REGISTER — see `docs/backlog-2026-07-29.md`
>
> This file stopped being the owed-item register on 2026-07-26. The live
> register is **`docs/backlog-2026-07-29.md`**, which carries the desk queue
> (§6 here), the ruling queue, the bug list and the art debt, and whose own
> retirement rule is "strike through with a commit reference, never delete."
>
> What is still worth reading here: **§1–§5**, the *table* agenda — the
> questions that need a human at the game, which the backlog deliberately
> does not restate at this length. §6 is kept for its reasoning, but its
> status column is maintained in the backlog now.
>
> Corrections that used to live in the §7 addendum have been **folded into
> the text they correct** (2026-07-29 doc de-drift pass) — every closed item
> below is struck through where it stands, so no reader has to reach an
> addendum to learn an item is closed.

**Compiled:** 2026-07-25, against deployed pck `20260725-175515+e263577`,
mod `klee-v0.2.0`, suite 808 passed / 0 skipped.

Everything below needs a human at the game. It is separated from the much
longer list of things that need a *ruling at a desk* (§6), because those two
queues have different costs and the desk queue keeps getting mixed into
playtest agendas where it silently expands them.

Sources swept: `docs/animation-sprint-{1,2}-log.md`,
`docs/kokomi-playtest-protocol.md`, `docs/archive/kokomi-v0.4-report.md`,
`docs/archive/ship-what-we-know-sprint-log.md`,
`docs/archive/shop-companion-channel-sprint-log.md`,
`docs/kokomi-art-pass-requirements.md`, `docs/archive/icon-gap-2026-07-24.md`,
`klee-mod/DECISIONS.md`.

---

## 1. Priority: things that are cheap to check and expensive to be wrong about

These are ordered by *cost of not knowing*, not by sprint.

| # | Check | Time | Why it outranks the rest |
|---|---|---|---|
| 1 | **Kokomi's Garment tip vs. the hit it describes** | one elite | The Garment's damage rider did not exist in C# until this build. Hover an attack while the Garment is up; the tip says *"deals +N"*. If N and the damage dealt disagree, that is a defect that invalidates every balance note about her. |
| 2 | **Corpse detonation** (`DECISIONS.md` §"Corpse detonation") | ~10 s | Bombed enemy + Pounding Surprise equipped, land the kill, watch for the Spark. Spark → sim and game agree, close it. No Spark → **every sim bomb number taken against a killable enemy overcounts**. Open since 2026-07-21 and cannot be settled from the repo. |
| 3 | **Kokomi boots and reaches a fight at all** | one run start | Her whole character shell is new as of today (§2). Nothing about it has been seen in-game. |

---

## 2. Kokomi — never played, and the build just changed under her twice

~~She has had **no table time at all**.~~ **CORRECTED 2026-08-06 (R107; S4 finding F17):** she has been played **exploratory** (2026-07-25/26, designated contaminating-exploratory by D5) and in the **08-01/02 three-seat holdout**. What has *not* run is the **protocol** playtest — `docs/kokomi-playtest-protocol.md`'s "Answers" section is still blank. Frame the next session as that, not as a first exposure. Two changes landed since the sim last
measured her, so the protocol's questions are live rather than confirmatory:

- **v0.4b starter rework (R56):** twelve-card Silent-shape starter, and the
  bank read flipped from divisor to multiplier
  (`KURAGE_PULSE_PER_CHARGE = 4`, duration 3 → 1).
  **Superseded by R73 (Neap Tide v2.1):** the multiplier is now **3** — ruled
  2, landed 3 when E1 graded P6 and the pre-committed weak-side fallback
  fired. `CONSTANTS_VERSION 4`, so every Kokomi number taken at ×4 is archive.
- **The character shell (today):** select portrait, locked portrait, char
  icon, map marker, selection splash, select backdrop, transition wipe and
  combat model are all hers for the first time — she was wearing Klee's.

### 2.1 The seven protocol questions

Full text and the specific failure modes: `docs/kokomi-playtest-protocol.md`.

| Q | Question | What a useful answer looks like |
|---|---|---|
| Q1 | Does the Charge bank read as a scaling identity or a ticking counter? | **Name a turn.** "Turn 5 of the first elite I started routing plays to feed it." |
| Q2 | How often does the Burst fire, and does the 3-turn window land? | **Count casts** per normal / elite / boss. Target was 35–50% of fights. Judge cadence and window *separately* — "fires often, does nothing" and "enormous, never fires" have opposite fixes. |
| Q3 | Can you tell the Garment is up? | See §1 item 1. This is the one most likely to have a real bug behind it. |
| Q4 | Does Bake-Kurage take over the deck? | **Sharper now than when written:** the pulse reads the bank at ×3 (R73; ×5+ with "Before Sun and Moon", which stacks) and lasts 1 turn. Watch for plays chosen to set up the pulse rather than to win the turn. |
| Q5 | Does Exhaust read as rotation, or as sacrifice? | R55 is a binding voice law. The question is whether the fiction survives the mechanic, not whether the words are right. |
| Q6 | Does the deck stay thin? | **Report deck size at the end of each act.** LAW 4 is machine-checked; the reward screen is where it can be defeated anyway. |
| Q7 | Do you draft enough Companions to build Commander? | Companions are in no rollable pool — the 4th reward slot hangs off Pearl of Wisdom and is their only door. |

### 2.2 Kokomi shell art — new today, unreviewed

Deployed and self-consistent, but no eyes on it in-game. Judge:

- **Select screen** — she should sit left of centre over the Watatsumi reef
  backdrop with the right third clear for the info panel.
- **Char icon / map marker** — both are head crops centred on her *head*, not
  on her bounding box (see §5 for why that distinction was load-bearing).
- **Combat model** — 240×280 static. She has **no layered combat rig**, so
  unlike Furina this is what the game actually draws in battle: no idle, no
  lunge, no death animation. Expected, but it will read as flat next to Furina.
- **Transition wipe** — a rising tide rather than Klee's radial blast.

### 2.3 Not shipped, and it will be visible

Her **58 card faces are provisional rank-1 picks that nobody has chosen**
(Track D taste pass, §6.1). The art on her cards is real art in the right
shape, but it is my guess, not your pick.

---

## 3. Furina / animation sprint 2 — four open tracks

Full detail: `docs/animation-sprint-2-log.md` §"Open [USER] items after this
pass".

- **B5 — motion look pass.** Boot and fight as Furina. Idle should read poised
  rather than bouncy (hat tilt and the sword's glow pulse are the tells), the
  lunge should land *with* the damage numbers, hits should flash **blue not
  red**, death should bow and fade once.
  - **Now also carries the facing flip.** Ruled "passes for a first-pass
    attempt" on 2026-07-25, so this is a look, not a gate. Two accepted
    consequences to judge in play: the turn **persists** (she faces the last
    thing she hit, never returns to neutral), and non-damaging plays do not
    turn her at all. **The crab fight is the place to judge it** — Klee
    attacking left mirrors Dodoco to her other side, and whether that reads as
    "turned around" or as "the wrong Klee" is a taste call.
- **D5 — Salon stage layout/composition. Capture mandatory.** Explicitly
  re-opened because D4 failed. The acceptance question is *silhouette
  legibility at glance distance*. Two things to do deliberately:
  1. deploy **three of one member** — duplicate rendering has never been
     exercised;
  2. get a shot with **Encore > 0** so the ribbon number is in frame (its
     label moved onto the ribbon after playtest 1 found it occluded).
  Crabaletta's claw is the known weak silhouette.
- **E2 — Furina's icon register.** Now a **pick, not a hunt**. Seven icons are
  shortlisted on `art/contact_sheet_assets.html` (batch `assets`, native
  size); rank 1 is provisionally live for all seven. **Four of them — Friendly
  Visit, Study Buddy, Standing Ovation, Ovation Trickle — have no good source
  and are flagged for re-hunt, not presented as good.** Export, then
  `python tools/art_process.py --apply-picks art/picks.tsv`.
- **F2 — Klee spark motes.** Not started, [USER]-optional by origin.

---

## 4. Co-op — the surface with no simulator behind it

Tier 0.5 models one seat, so **every co-op defect is play-derived**; there is
no C# test project either. Anything found here is found by playing.

- Kokomi has never been played in co-op at all.
- Co-op is lockstep: peers on different mod builds desync. Everyone must run
  the same `klee-v0.2.0.zip`.
- **A funnel can now legitimately go quiet.** A Furina who takes Touch of
  Orobas never fires the Spotlight designation funnel again, so **the
  Spotlight beam stops appearing for that player for the rest of the run** —
  per-run and per-player, so one Furina may still be firing it while another
  has stopped. This is a design outcome, not a defect; recorded so it is
  diagnosable rather than investigated.

---

## 5. What changed in this build since your last session

So the playtest is read against the right baseline.

- **Kokomi's eight character-shell surfaces** — new (§2.2).
- **`build_pck` was shipping working files.** The still generators cache their
  governing render next to their outputs; a blanket `*.png` copy shipped them.
  Kokomi's cached cutout is 8.6 MB against a whole pck of 8.3 MB. Now excluded
  by suffix. **Net pck 8.3 → 9.1 MB** — eight real textures in, one working
  file (and Furina's) out.
- **`validate.ps1` was failing on a passing lint.** Under PS 5.1 with
  `ErrorActionPreference = 'Stop'`, *any* native stderr output raises
  `NativeCommandError` **even when the command exits 0**. `lint_constant_parity`
  grew a reader that imports `tier05.relics`, which emits three house-rule
  `UserWarning`s at import; the lint printed `constant parity: OK` and took the
  whole deploy down. All seven python call sites now go through one helper.
  This was latent on `main` from commit `e263577`, not introduced by the art
  work — but it meant **no deploy could succeed** until it was fixed.
- **The centring rule now has a test.** B4's "frame off the alpha bbox, never
  off the image frame" had two callers and no test; Furina's six approved
  surfaces are pinned byte-for-byte (`tier0/tests/test_char_stills.py`).

---

## 6. NOT playtest items — the desk queue

> **QUEUE POINTER, added 2026-08-06 by the housekeeping sweep (Track X).** The single source of truth for what is open and for whom is now **`docs/registry/user-queue.md`**. This section keeps its full text and stays the place the detail lives; the queue file is the index that says which items are still open, which were discharged and by which ruling. Where the two disagree about a *status*, the queue file is the later reconciliation. Identifier collisions (`G1`, `D5`, `C1`, `P1`, `S4`, `X<n>`) resolve at `docs/registry/identifiers.md`.


Listed so they stop being smuggled into playtest agendas. None of these needs
the game running.

### 6.1 Taste passes (need you, not the table)

1. **Kokomi's 58 card faces + 15 Inazuma companions.** Four contact sheets:
   `art/contact_sheet_kokomi-{identity,commander,priest,assist}.html`. Export
   picks, then `art_process.py --apply-picks`.
2. **Furina's seven power icons** (E2, §3) — same mechanism.
3. **Three L12 duplicate crops** that the new hash gate exposed as
   *pre-existing shipped* duplicates, allowlisted as known defects pending a
   re-pick: `blazing_delight == true_spark_knight`,
   `crowd_work == standing_ovation`, `catalytic_conversion == spark_collection`.
   ~~`blazing_delight` additionally has **no rank-1 plan row at all**.~~
   **CLOSED 2026-07-26 (`6f1b969`)** — the plan row exists and the L12
   allowlist entry is gone. The other two duplicate pairs remain open as
   written.

### 6.2 Rulings

- **Kokomi art §6** (`docs/kokomi-art-pass-requirements.md`): the crop-reuse
  budget; whether Watatsumi environment art counts as a card face given
  Furina's pass rejected an empty corridor as "a random hallway"; whether to
  hand-crop the banned `Character Details 1` for a rare.
- **Kokomi v0.4 §6:** meter-20 ratification on the 500-run confirm;
  `epiphany_of_the_deep` → "Song of Pearls"; whether to keep watching commander
  Garment uptime (still 50%, 58.7% in long fights).
- ~~**The single red-pen session** (ship-what-we-know §"What is NOT done"):
  every number in that sprint is PROPOSED — G-D's three cards, G-C2's Nicole
  delta, G-C3(b)'s two relic tune-ups. The sprint's own gate says this happens
  once, late, over the whole set.~~
  **CLOSED 2026-07-26** — the session happened; all seven numbers RATIFIED and
  APPLIED (`docs/red-pen-2026-07-26.md` Part 1). *(Item 1 of that list,
  G-A5(b)'s live capture, had already been captured on 2026-07-25.)*
- ~~**Furina's starter has no upgraded form.** Touch of Orobas still hands her a
  Circlet, and she is the character the playtest was played on. Every available
  tune-up breaks either the no-new-behaviour rule or her no-passive-accrual
  law. **Needs a ruling, not code.**~~
  **CLOSED 2026-07-26** — ruled (R2) and implemented (queue 3, `477b282`);
  `NO_UPGRADED_FORM` is now an empty dict by design.
- **Ten Spotlight powers, ten icons or one family mark?** Shipped as distinct
  on the sprint-1 reading that legibility failures came from indistinctness;
  the opposite case is real at badge size. Collapsing is a one-line change.
- **Shop companion channel §7:** close-out ratification; P1–P3 grading
  countersign; whether the shop's purse ever binds (runs end with ~220 unspent
  gold — this decides whether "pricing is the balance governor" can be true at
  all); the colorless 1.15× surcharge companions do not collect; Track A's pool
  migration.
- **Enchantments: a design pass, not a card.** Directed 2026-07-27; brief in
  `docs/silent-anchor-sprint-log-2026-07-27.md` §13. An enchantment is state
  on a CARD INSTANCE with its own amount, and every modifier tier0 has
  attaches to a creature — a data-model gap, not a missing op. The pass
  decides whether tier0 models them at all, and whether this is a parity
  feature or one our own characters want. Exactly ONE card in the Silent's
  remaining 27 needs it (Blade Of Ink), which is the argument against, and
  the anchor is honest without it either way.
- ~~**Kokomi kickoff §202:** Raiden Shogun's disposition.~~
  **CLOSED 2026-07-26 (R52)** — she ships as an Inazuma 5-star rare
  (`docs/inazuma-companions.yaml`); red-pen passes at `81ba9d5` / `e80f955`.
- **Kaboom Beetle Swarm's printed text, after R72** (2026-07-26). The bonus
  now snapshots bombed-state at cast, so an enemy whose bombs hit 1 detonated
  keeps paying the +3 on hits 2–3 — but the card still reads "*Bombed enemies
  take X more per hit*", which a player will read as live state. R72 item 4
  flags this rather than fixing it: the sheet is ratified, so the rewording
  needs your countersign. Nothing mechanical rides on it.

### 6.3 Known gaps, no action requested

- **Orobas is not modelled in the sim**, a recorded divergence. Cost: Klee's
  doubling is the most aggressive number in the ship-what-we-know sprint and
  the one with no sim evidence behind it.
  **NARROWED 2026-07-26** — Klee's variant *is* modelled now
  (`touch_of_orobas_klee`, real `combat_start_spark` hook, queue 2). Still
  unmodelled: Furina's R2 upgraded form and Kokomi's variant.
- **The Ancient card's 3 Charge/turn is unmeasurable** — it lives in a layer
  the run sim does not model. The single least-defended value in Kokomi's
  build. If the Darv event offers it, take it and say what happened.
- **~20 cards short of roster parity** for Kokomi (common 25/~32, uncommon
  20/25, rare 8/15).

---

## 7. Recap addendum (2026-07-26) — corrections to the compile above

Dated addendum from the 2026-07-26 recap audit. Full audit:
`docs/missed-requirements.md`.

**The "closed since compile" list that used to sit here has been FOLDED INTO
THE TEXT IT CORRECTS** (2026-07-29 doc de-drift pass). All five items —
§6.1's `blazing_delight` plan row, §6.2's red-pen session, §6.2's Furina
starter, §6.2's Raiden disposition, and §6.3's Orobas divergence — are now
struck through and dated where they stand, because a correction nobody
scrolls to is not a correction. Nothing was deleted; the closures moved.

What remains below is the half of the addendum that is *not* a correction to
§1–§6: findings the 2026-07-26 audit surfaced that this file never listed at
all. They are all carried forward in `docs/backlog-2026-07-29.md`.

**Newly surfaced, untracked above** (full list with evidence in
`docs/missed-requirements.md` — the top items):

- Three shipped cards render the BETA placeholder with no plan.tsv row:
  `spotlight_center_stage`, `spotlight_guest_cast`, `confiscated` (§4.1 there).
- The salon member sprite-scale fix from Playtest 2 was never applied — it
  blocks D5's capture from being judgeable (§4.3).
- The char-icon `_outline` asset was never produced; all three characters
  ship the fill icon in the outline slot (§4.2).
- The Fontaine Rares sprint's four [USER] close-out items (companion art
  picks, lore audit, C2 countersign, ratification) are on no tracker (§4.4).
- `kurages_oath` = 12 was [USER]-flagged "too strong" and is absent from this
  file and from the playtest protocol's standing-flags list (§3.3).
