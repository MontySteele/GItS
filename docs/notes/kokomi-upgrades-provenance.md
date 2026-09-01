# kokomi-upgrades.yaml - comment provenance

Long comment blocks that used to sit in `docs/kokomi-upgrades.yaml`. They
moved here on 2026-09-01 so an agent reading the sheet loads rows,
not prose. Blocks are verbatim and in sheet order.

A heading names the row the block was attached to. `before <id>`
means a column-0 section note that sat above that row. `header` is
the file header. Blocks of three lines or fewer stayed in the sheet.

## header

```
# Lifecycle: LIVING — expected to change; read it to work on the project. Status index: docs/registry/identifiers.md §15.  (lint-ok)
# Kokomi + Inazuma upgrade deltas — v0.2 sheet pass (companion file to kokomi-cards.yaml / inazuma-companions.yaml)
# Grammar authority: upgrade-conventions.md; klee-upgrades.yaml precedents cited inline. ALL deltas PROPOSED.
# RESOURCE-CURVE LAW (Klee R1 precedent, applied to her engine): upgrades must NOT move the resource curve —
#   no gain_charge deltas, no conscript-count deltas, no cadence/aura riders. Charge lines and conscript counts
#   are printed identities; upgrades buy quality (damage/Block/draw/cost), never a faster engine.
# ceremonial_garment: NO UPGRADE (kit card, v1.9; sparks_n_splash precedent — Talent Training is v2 design space).
# KNOWN GAP, flagged not fudged: no sly-delta key exists in the applier, so Sly branches never move on upgrade
#   (drifting_lantern/tidal_lure upgrade their PLAYED faces only). Extending the dispatch is a design decision
#   about whether upgrades should sharpen the discard game — deferred to a ruling, not smuggled in here.
# `add_before: <op>` is the ONE position key `add:` takes. Without it `add:` appends, which is what every other
#   add-row on every sheet wants; with it the added effect is inserted in front of the first top-level effect
#   carrying that op. It exists because send_the_runner+ is ruled to resolve its new line in the MIDDLE of the
#   body — see that row. It is a POSITION, never a second effect: one `add`, one place.
```

## kurages_oath

```
                                         # 12: at a printed number already flagged as maybe-too-strong the
                                         # upgrade sold consistency (online turn 1, not drawn on turn 6)
                                         # instead of more of it. The 12 retired at R130 and that rationale
                                         # retires with it — at 5 there is nothing to be shy about, so the
                                         # upgrade sells the +2 the ruling prints. Name-matched delta key;
                                         # its applier sits beside weak/vulnerable in tier0/content/upgrades.py.
```

## tactical_retreat

```
                                         # together because the card is a TEACHER: a version that drew 2 and
                                         # discarded 1 would teach that discard is a cost you grow out of,
                                         # which is the opposite of the Sly lane's bargain. [USER] verbatim:
                                         # not a true cycling effect, and never to be tuned into a solo
                                         # engine piece.
```

## moon_signal

```
                                         # mechanical rather than a preference: `add` APPENDS unless `add_before`
                                         # is given, `recall_to_draw` inserts at draw-pile index 0, and
                                         # `state.draw` pops index 0 — so an appended draw would take back exactly
                                         # the card the recall just placed, turning a 0-cost Common into
                                         # "return the best card from your discard pile to your hand". On an empty
                                         # draw pile it degenerates further: the discard, the recall and the draw
                                         # all touch the same card and the upgrade becomes a no-op that has spent
                                         # itself. Retain sets a card FIELD and inserts nothing, so the printed
                                         # order is byte-identical between the faces and that failure cannot occur
                                         # by construction. It also leaves the hand economy negative, which is the
                                         # body's whole point. PRECEDENT, same argument: raise_the_sashimono
                                         # {retain: true} below, plus honor_guard, the_gunbai_turns and
                                         # open_the_stores. The Sly draw cannot move on upgrade (applier gap).
```

## surging_shoal

```
                                         # is unchanged; the base moved.
                                         # The old comment here read "4->6" (lint-ok: 4->6 quoted stale
                                         # annotation), which had been stale since the
                                         # v0.3 repricing to 7 -- two bases out of date, in the file whose
                                         # whole job is to say what a card becomes.
```

## pearl_barrage

```
                                         # {formula_per: +1} against the retired pile body; that delta has
                                         # no pile slope left to bump. ON A BOUNDED COUNT the base is the
                                         # honest half: the selection cost lives in {0, 1, 2} because
                                         # Kokomi's sheet has no card above cost 2, so steepening `per`
                                         # would make every chooser mistake more expensive over a
                                         # distribution 88% concentrated on two values. Bumping `per` is (lint-ok: measured distribution)
                                         # the ruling for counts that only grow; this count does not.
```

## shell_of_sanctuary

```
                                         # DID NOT MOVE and that is not an accident: the ruled base face
                                         # prints Block 4 with upgrade +4, which is exactly the key and the
                                         # value this row already carried against the retired 11 (lint-ok:
                                         # 11 is the retired base, not this row's delta). The rewrite
                                         # therefore needs no upgrade-sheet edit at all.
```

## watch_of_the_shallows

```
                                         # along: the applier only carries the cap when cap == amount, and this
                                         # row's cap is the POOL's ward ceiling, not its magnitude. So the
                                         # upgrade buys magnitude and the ceiling stays where the Rare put it,
                                         # with the row's `never_reduces` mode keeping the bigger ward on top.
```

## ebb_tide

```
                                         # ENGINE, not more tempo: it is the conversion rate that scales, which
                                         # is the only thing this card was ever bought for. (Expressible only
                                         # because the branch is `chosen` -- the random branch has no C# path
                                         # at amount > 1; see the codegen guard.)
```

## before honor_guard

```
# ---- v0.5 PARTIAL-FILL UNCOMMONS (+8) ----
# SECTION HEADING IS NOW APPROXIMATE: honor_guard (R75 + G8's R79 collision) and moonlit_offering (G8) were
# both promoted to Rare in the Neap Tide pass and are left in place rather than moved, so their git history
# stays readable. Rarity lives on the CARD sheet and is authoritative there; these headings are organisational.
```

## honor_guard

```
                                         # The old delta added a draw, which is dead grammar now -- R79 gives
                                         # Discard/Sly the monopoly on draw, and this card is not in that lane.
                                         # A deeper discount is also out: cost_mod is energy, and energy is
                                         # the resource curve. Retain is the right sale for a 0-cost tempo
                                         # enabler -- it stops being a card you must draw ON the turn the
                                         # recruits are in hand, which is the whole failure mode it answers.
```

## moonlit_offering

```
                                         # This is the R79 template's own upgrade shape ("Gain 1 (2) energy,
                                         # draw 1 (2)"). The Exhaust is NOT removable by upgrade -- it is what
                                         # makes the card legal under R79 at all, and removing it would also
                                         # open the net-positive energy loop swift_currents was denied.
```

## undertow

```
                                         # slope stays +1, the bar-3 draw stays, and the Sly
                                         # energy stays 1. Upgrading the BASE rather than the slope on purpose:
                                         # the slope reads a pile that is uncapped and only grows (the same
                                         # shape R80 makes dangerous on Charge), so moving it is a
                                         # resource-curve move on an unbounded count. The base pays on turn 1.
```

## before_sun_and_moon

```
                                         # every other power on this sheet adds a TERM, and this one moves a
                                         # COEFFICIENT on a bank that is uncapped and never spent (R80), so
                                         # the same printed delta is not the same power. +1 here already
                                         # doubles the card. It is also legal under the resource-curve law by
                                         # the narrow reading -- Charge ACCRUAL does not move, only what a
                                         # point of it buys -- and that reading is worth stating, because a
                                         # coefficient on the engine's output is the closest this sheet comes
                                         # to selling a faster engine without technically being one.
```

## the_tide_remembers

```
                                         # ladder becomes 7 / 9 / 11. Was {damage: +3}, which has no matching
                                         # effect on the new body -- the retired one printed a flat wave and
                                         # a pile bar, and neither survives the rewrite. Base rather than
                                         # per, for pearl_barrage's reason: the selection cost is bounded.
```

## before the_gunbai_turns

```
# ---- EB-69 POOL FILL (+14) — R198, [USER] 2026-08-23 ----
# A COMPLETE upgrade row for every one of the fourteen: EB-69 may not ship without them, and nothing is held
# out. Same laws as everywhere above. (i) RESOURCE CURVE NEVER MOVES — no gain_charge delta, no muster-count
# delta, no threshold moves. (ii) COMMONS: one number, no cost reductions (ONE ruled [USER] exception below,
# marked as such). (iii) UNCOMMONS: a bump OR a keyword, and both uncommon cost slots are already spent
# (mass_mobilization, reinforcements), so NO new uncommon takes `cost: -1`. (iv) SLY BRANCHES NEVER MOVE —
# the applier has no sly-delta key (header gap note), so five of these fourteen can upgrade only their played
# face. (v) Every delta key below already exists in tier0/content/upgrades.py.
# Ten of the fourteen are a single existing delta key with a named live precedent.
```

## the_gunbai_turns

```
                                         # DRAWN on the turn the hand is right, so Retain is the failure mode
                                         # it answers. The Sly-grant count (3) and the discard count (3) are
                                         # printed identities and do not move; cost_mod-style deepening is not
                                         # available and would be energy anyway.
```

## gyorin_formation

```
                                         # 1-per-2-Charge read both stay. slack_water's note — "the half you
                                         # can rely on is the half that grows". The alternative
                                         # ({block_next_turn: +4}, the tideline_watch precedent) is NOT taken:
                                         # given this card's WATCH line the smaller of the two is the safer
                                         # sale, and the pre-emptive half is the half being watched.
```

## council_at_bourou

```
                                         # (resource-curve law) and the chosen discard stays 1. Reads against
                                         # the D5 body: [USER] took the draw down 2 -> 1 (lint-ok: 2->1 is the
                                         # D5 BASE-BODY history, not this row's delta) and dropped the
                                         # Exhaust, so the upgrade sells the point the base gave up.
```

## open_the_stores

```
                                         # player pays, not a reward the upgrade sells — the ebb_tide
                                         # "sells more engine" argument holds only where the engine half is
                                         # the exhaust, and here the discard is the tempo half. Charge stays 4
                                         # (resource-curve law) and the Sly exhaust stays 1 (applier gap).
```

## raise_the_sashimono

```
                                         # 1 at cost 0), so a second draw is a second card off one free order
                                         # rather than a sharpening — and the rationale line that claimed the
                                         # draw made it self-replacing "on upgrade" was simply wrong about the
                                         # base, and is corrected here rather than inherited. Retain is the
                                         # honest sale for an on-ramp: it stops being a card you must draw ON
                                         # the turn the Rare is in hand. The Sly-grant count stays 1.
```

## send_the_runner

```
                                         # [USER]-RULED (D2a): draw 1 / exhaust 1 chosen -> draw 2 / discard 1
                                         # chosen / exhaust 1 chosen. `add_before` is what makes the loaded
                                         # order the RULED order: a bare `add` appends, which loaded the card as
                                         # draw / exhaust / discard — the player was asked what to Exhaust
                                         # before being asked what to throw, and each question changes the
                                         # answer to the other. Naming the op (not an index) means a later edit
                                         # to the base body either still has an `exhaust_from` to sit in front
                                         # of or fails loudly. FLAGGED HONESTLY: this is TWO moves on a
                                         # COMMON where this file's own commons idiom is one number, and the
                                         # section heading above says so. The one live two-key common-shaped
                                         # row is tactical_retreat {draw: +1, discard: +1} — and that card is a
                                         # BASIC, not a common. RECORDED AS A [USER] EXCEPTION, NOT A
                                         # PRECEDENT: a later two-key common row cites its own ruling or does
                                         # not land. It is also the only place the assist lane gets its
                                         # chosen-discard cycler back, which is why the second key is the one
                                         # it is.
```

## tighten_the_cords

```
                                         # {power_amount: +1}: the body is now a threshold, and LAW's threshold
                                         # rule (R58) requires the ALWAYS-LIVE half to move so the bar cannot
                                         # drift down. Here that half is the Block; the exhaust-pile bar stays
                                         # where it is printed. Every other threshold row on this sheet obeys the
                                         # same rule — read_the_current {damage: +3} ("the ALWAYS-LIVE half"),
                                         # the_tide_remembers {damage: +3} ("the base wave"), gyorin_formation
                                         # {block: +3} ("the IMMEDIATE half"). The card is still bought for the
                                         # trajectory; the upgrade now sells the turn it is played on, and the
                                         # trajectory stays something the deck has to earn.
```

## raiden_musou_no_hitotachi

```
                                         # that was left over when the base went 18->40 (lint-ok: 18->40 is
                                         # that base move, not an upgrade delta) earlier the same day
                                         # (the buff ruling named the BASE only, so the delta was carried
                                         # forward unchanged and FLAGGED rather than inferred -- this is that
                                         # flag being answered). +10 restores the proportion: +4 was ~22% of
                                         # the old body and ~10% of the new one; +10 is 25%, in line with the
                                         # rest of this sheet. It also prices the Exhaust honestly, because
                                         # the upgrade is worth its damage exactly ONCE per combat where every
                                         # other companion upgrade here compounds on redraw.
```
