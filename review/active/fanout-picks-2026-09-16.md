Status: OPEN (pick 4 only; R274 ruled picks 1-3 and 5-8 at their defaults on 2026-09-16; nothing here is measured)

# The 2026-09-16 fan-outs: what landed, and eight picks

Three fan-outs ran on 2026-09-16 after the epoch-reveal click: 32 PRs in the
day (#531-#562), 11 in the evening (#563-#573) and 19 in the afternoon after
(#574-#592), all merged by Claude as plumbing under R259. Main is green. This
page is the close-out: what is proven in the running game, what the second
deploy's live look proved (proofs-10, #594 and #595), and the picks only you
can make (QUEUE rows `fanout-picks-2026-09-16 4.1` to `4.8`).
Every claim names a file or a PR.

## 1. Proven in the running game

Build `0.2.3541+proto`, all arms ON, read by two lanes (proofs-9,
`review/records/teyvat-proofs-9-lane1-2026-09-16.md` and `-lane0-`):

- **The Punch-Off is fixed** (proofs-8a, item 1: 17 s at harness speed, 45 s
  at the game's own, zero "Element limit reached" lines). Every parked Teyvat
  event page is reached (items 2-5).
- **Every new wire field is live**: the enemy intent's breakdown folded an
  elite's Strength and a Tainted modifier (15 to 25), the intent names its
  side, the master deck reads on every screen, a 39-row removal grid came
  through whole, Pael's Wing's sacrifice reached the page, a resolution
  ledger listed an auto-played turn and a random Set off hit by hit.
- **The three grant ops** (relic, potion, gold) unlocked four rows proofs-8a
  could not reach: Pael's Eye's extra turn, Flex Potion's fold gone next
  turn, Neow's Arcane Scroll under Kokomi, The Future of Potions under all
  three arms.
- **On the faces**: the Spark sources line, Feint's fold, Ka-pow! with The
  Boot, the Plan line under Vulnerable (R246), the Stage rename, Rejoice's
  live preview, Stoke the Fuse's X, two Bombs in set-off order, a
  conditional companion preview, and Salon Solitaire draws its sigil (the
  8b placeholder was the base game's own `CARD.SNECKO-NOPE` id).
- **27 rows retired on those reads, 16 more on proofs-10**; the register
  stands at 62 open rows after 13 minted for what the reads found.

## 2. Built today and proven on the second deploy (proofs-10)

Read on both lanes against `0.2.3581+proto` with the Kokomi arm OFF on
purpose, the only condition under which the Kurage Memory has a surface: its
two rows (`EB-247`, `EB-248`) passed and are retired. Every item below read
PASS (`review/records/teyvat-proofs-10-lane1-2026-09-16.md` and `-lane0-`),
except the death SOUND, which an agent cannot hear (`EB-159` now asks you to
listen once). The installed build is now `0.2.3589+proto`, all arms ON.

- A modded death is waited for, and should be heard (#582, `EB-159`, an E
  default you can veto: the body's own clip length, Klee 1.0 s, Furina 1.2 s).
- An old save no longer logs two ValidationErrors per boot: 54 retired card
  ids carry hidden aliases and the codegen appends the next one on
  retirement (#585, `EB-790`, E default).
- Nimble on Barbara moves the Block and never the rider; the rider's payout
  never took the enchant, only the face lied (#583, nine generated cards).
- Piles and the master deck print the enchanted face with the hand's fields
  (#580, #588); the mode chooser's option cards fold the board (#590) and
  their titles print no raw markup (#588); the Spark sources line covers the
  whole fight, not the last turn (#590); the removal grid marks the picked
  row (#588); the page's Written line prints the sheet's literal on branch
  faces (#590); the Bomb clause is on the tip and the glossary (#590).
- The nine C# pins that failed under the Stage test property now declare
  their world, and the gate runs both configurations (#581).
- The harness frames the whole window: PrintWindow was clipping a 1.5x
  render, so every frame lost the hand and the enemies (#589, `EB-788`).
- 29 cards that wore a neighbour's art have their own (#591), and a
  semicolon no longer hides a face from the text ceiling (#584).

## 3. Found today and rowed, not fixed

Eight shipped power faces run over the 125-character ceiling now that
semicolons are measured, Fanfare's meter at 234 and Salon Member at 397
(`EB-801`, a text pass for Fable); Breakwater is offered Nimble and Nimble
pays it nothing (`EB-798`, E default: planned-only Block is not enchantable,
you veto); the four Furina power badges draw card portraits shrunk into badge
slots, an art bill (`EB-65`); the engine's own death wait is still skipped
for a spine-less body (`EB-797`); the bridge does not build in a bare
worktree without the game-dir flag (`EB-799`); the two Kaeya rows wear each
other's named art (`EB-803`); the second capture path may carry the same clip
and nothing refuses an incomplete frame (`EB-802`); the five arm properties
disagree on one test's shape (`EB-800`). Proofs-10 added five: a mode card's
title prints the sheet's number over a folded body (`EB-805`), the harness
camera can frame the other lane and labels every frame lane 0 (`EB-806`), an
arm-gated relic id warns at boot like the retired cards did (`EB-807`), a
create-mode Muster never stamps its recruit's discount (`EB-808`), and a free
queue entry prints no derivation (`EB-809`).

## 4. Picks

**R274 (2026-09-16):** picks 1, 2, 3, 5, 6, 7 and 8 were taken at their defaults. Pick 4 is deferred to a Fable design pass on 2026-09-17; [USER]'s lean is that Noelle's imprecise text is the defect and the groups still need settling. Of the mapping's carried items, the Wanderer collision on Knowledge Demon is accepted and Tanx waits for a reflavoring worth having.

Defaults are marked. A pick not taken stands at its default.

1. **May a Skill consume Vigor?** Kurage's Oath (a starter Skill) printed
   Deal 7 under Vigor 8 and dealt 7: face and hit agree, and the game's own
   rule keys Vigor on the attack door, not the card type. The old row asked
   that a Skill never fold Vigor, which would need a starter retype or a
   house rule against the game's. **(1) DEFAULT: the game's rule stands and
   `EB-441` closes;** (2) retype Kurage's Oath as an Attack; (3) make Skill
   damage unpowered (it then drops Strength too).
2. **Guest Cast and Kujou Sara's granted rider.** Delayed and conditional
   Companion legs now print the multiplied number (#567). Sara's "next
   Attack deals 4 additional" is not multiplied; multiplying it to 6 changes
   a shipped card's strength. **(1) DEFAULT: leave it;** (2) multiply every
   granted rider too, one commit.
3. **The inherited Silent relics and potions** (`EB-494`'s census,
   `review/active/inherited-potions-relics-census-2026-09-16.md`): Helical
   Dart and Snecko Skull mislead every kit (no Shiv, no Poison anywhere),
   Ring of the Snake never rolls. **(1) DEFAULT: drop Helical Dart and
   Snecko Skull from all three pools, leave the rest;** (2) drop nothing;
   (3) replace them with kit relics (a design pass).
4. **What the third companion set is** (`EB-444`, after EB-504/642/663
   moved the ground): Witches' Circle keys off "a Hexerei card", Noelle
   prints "Klee's own Companions", a plain Companion card says neither.
   **(1) DEFAULT: one printed name per set, decided in a short design pass
   with Fable, then the sweep and a lint;** (2) leave the three words.
5. **The twelve-arm table re-run** (`EB-195`, and `EB-74`'s staged lever):
   its gate, EB-199, retired on 2026-09-08, so nothing blocks the run except
   that it is a measurement window (R101b: strike, never rewrite). **(1,
   default) run it at the next re-baseline window, together with the
   Kokomi fold's;** (2) run it now on its own.
6. **Curl Up 14 on the sim's act-2 Louse** (found under D5/D6, #557): the
   yaml already says UNIMPLEMENTED; wiring it moves an encounter's
   difficulty. **(1) DEFAULT: wire it at the same re-baseline window as
   pick 5;** (2) leave it out.
7. **`EB-255`, starters excluded by membership** in `archetype_shares`:
   moves `dominant_archetype` on two rosters, so a `POLICY_VERSION` window.
   **(1) DEFAULT: fold it into the window of pick 5;** (2) leave the lint
   red as debt.
8. **`EXPERIMENTS.md` registrations naming deleted instruments** (KLEESPARK-S1
   and the FURINAREFRAME rows, after #535 and #561): the file is yours.
   **(1) DEFAULT: leave them as published, struck by the deletion's
   ledger line;** (2) strike them in the file with a one-line note.

Three things to look at, not picks. The 54 card faces on
`art/contact_sheet_coverage_2026-09-16.html` (one, `grand_gala`, took a
picnic chibi at rank 4 while ranks 6 and 7 are literally the Lavish Gala,
veto by a line). The 30 faces on
`art/contact_sheet_eb778_proxies_2026-09-16.html`: `proto_fs_final_bow` is a
tea party, `proto_fs_warm_reception` is desserts with no figure, six Stage
rows re-crop pictures Furina's shipped cards already hold, and
`proto_kk_tide_wall` is a third crop of the same Wish art. And your PR #476,
which needs a rebase because its six new row ids collided with rows minted
since; the six defects it names are fixed or rowed on main (`EB-774`,
`EB-775`, `EB-779`, `EB-780`, `EB-783`).
