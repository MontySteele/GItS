Status: OPEN (picks for [USER]; nothing here is measured)

# The 2026-09-16 fan-out: what landed, and eight picks

Two fan-outs ran on 2026-09-16 after the epoch-reveal click: 32 PRs in the
day (#531-#562) and 11 in the evening (#563-#573), all merged by Claude as
plumbing under R259. Main is green. This page is the evening's close-out:
what is proven in the running game, what is built and waiting for the next deploy (the proofs-9 row, `EB-782`), and the picks only you can make (QUEUE rows `fanout-picks-2026-09-16 4.1` to `4.8`). Every claim names a file or a PR.

## 1. Proven in the running game (build `0.2.3480+proto`, arm ON)

- **The Punch-Off is fixed.** The Liyue fight ran to its reward in 17 s at
  harness speed and 45 s at the game's own speed, with zero "Element limit
  reached" lines and a 15 KB log, against the 2.5 GB spin it was opened for
  (`review/records/teyvat-proofs-8a-2026-09-16.md`, item 1).
- **Every Teyvat event page that was parked is reached**: the Trial's Reject
  page and Double Down popup, Tinker Time to DONE, the Colossal Flower's
  third reach both ways, the training dummy's loss branch (same record,
  items 2-5). The dressed Slippery Bridge prints the card name, a dressed id
  forces its base event onto the dressed page, three Ancient rooms print
  their options, Neow's options print their rules text.
- **33 of 48 face and page rows read PASS on a lane** (`review/records/live-looks-8b-2026-09-16.md`):
  Set-off previews, the buff strip, Bomb headers, reaction naming, Amber's
  buff, Lisa's Vulnerable, Lightning Fang's override, Heizou under Shrink,
  Feint's Plan line, the Plan-screen lethal warning, and the whole Furina
  Stage batch (three bars in seat order, act lines, the glossary, Curtain
  Rise both ways and 5/9 under Weak, no Fanfare buff or Encore under the
  arm).
- **The register went from 162 open rows to 87**: 90 retired (nine moot with
  the reframe deletion, two moved to QUEUE, the rest done and seen), 33
  narrowed to the one thing still owed, 17 minted for what the rounds found
  (EB-774 to EB-790).

## 2. Built and waiting for the next deploy (proofs-9, `EB-782`)

Six new wire fields (#569: the enemy intent's breakdown and side, the master
deck on every screen, the whole removal grid, the reward's alternative
button and a `sacrifice` verb, a per-card resolution ledger with hits in
order); the Stage round-three fixes from your PR #476 (#566, #572: five of
six fixed, the sixth as a hover tip; the chooser's bridge press is a live
look); the Kokomi Plan tip rewrite and the quarter-hit's one damage kind
(#567); the harness's seed retry, per-act local-play sessions, the Crystal
Sphere exit, the matched-telegraph scorer and the seed ledger (#568); 54
card faces placed at shortlist rank 1 (#564, 54 uncovered -> 0).

## 3. Found tonight and not yet fixed (rows minted or in flight)

Every dressed Slippery Bridge hard-codes "Lose 3 HP" where the base charges
3 + hold-ons; a lane-1 teardown archives lane 0's log; the two Curtain Rise
mode cards are missing from the atlas; the KurageMemory card throws "Local
player not found in combat" at every combat start (which is why its two
rows have no surface to read); `hp_settled` is false on every map screen;
the bridge has no relic, potion or gold grant op, which kept five rows out
of reach; nine C# pins fail under the Stage test property and the gate never
runs it (`EB-781`); the Salon Solitaire relic draws the placeholder
(`EB-776`). Fixes for most of these were in flight when this page was
written and their rows carry the PR that lands them.

## 4. Picks

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

Two things to look at, not picks: the 54 new card faces on
`art/contact_sheet_coverage_2026-09-16.html` (one, `grand_gala`, took a
picnic chibi at rank 4 while ranks 6 and 7 are literally the Lavish Gala,
veto by a line), and your PR #476, which needs a rebase because its six new
row ids collided with rows minted since; the six defects it names are fixed
or rowed on main (`EB-774`, `EB-775`, `EB-779`, `EB-780`, `EB-783`).
