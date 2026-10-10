# prototype-surface.yaml - comment provenance

Long comment blocks that used to sit in `docs/prototype-surface.yaml`. They
moved here on 2026-09-01 so an agent reading the sheet loads rows,
not prose. Blocks are verbatim and in sheet order.

A heading names the row the block was attached to. `before <id>`
means a column-0 section note that sat above that row. `header` is
the file header. Blocks of three lines or fewer stayed in the sheet.

## RETIRED — the Sparks alternative-cost arm's eleven rows (`EB-750`)

The blocks that used to sit here for `proto_pop_spark`, `proto_kaboom_sink`,
`proto_spark_strike` (Fwoosh!), `proto_spark_sweep` (Tinder Toss),
`proto_spark_double_tap` (Bang Bang!), `proto_spark_blast` (Dodoco Blast),
`proto_spark_finisher` (Firework Finale), `proto_true_spark_knight` (Spark
Knight's Oath), `proto_powder_charge_spark` (Set It Off),
`proto_hold_the_line_spark` (Dig In) and `proto_smoke_and_sparks_spark` (Powder
Smoke) went with those rows on 2026-09-16.

R270 ruled Spark a CURRENCY under `KLEE_OVERHAUL`, which superseded the whole
alternative-cost pool, so the surface's own deletion rule applied: the rows, the
two substitution maps (`SPARK_ALT_STARTER_SUBS`, `SPARK_ALT_POOL_SUBS`), the
derived `KLEE_SPARK_ALT_ROWS` and the C# starter seam left HEAD together.

Retrieval — the last tree that carried them:

```
git fetch --depth=1 origin 036c12d150d6dbd58f0776a0d07e3c028a321a61
git show 036c12d150d6dbd58f0776a0d07e3c028a321a61:docs/notes/prototype-surface-provenance.md
git show 036c12d150d6dbd58f0776a0d07e3c028a321a61:docs/prototype-surface.yaml
```

The arm's design reasoning is `review/ruled/klee-sparks-2026-08-29.md`; the
published `KLEESPARK` reads stand as published (R101b) and are not re-graded by
this deletion.

## RETIRED — the Furina reframe's sixteen rows and their blocks (`EB-726`)

The blocks that used to sit here for `proto_fr_salon_debut_named`,
`proto_fr_curtain_call`, `proto_fr_exit_stage_left`,
`proto_fr_let_the_people_rejoice`, `proto_fr_intermission`,
`proto_fr_florid_cadenza`, `proto_fr_dramatic_entrance`,
`proto_fr_universal_revelry`, `proto_fr_flood_of_emotion`,
`proto_fr_aria_of_recompense`, `proto_fr_curtain_rises`,
`proto_fr_second_course`, `proto_fr_guest_list`, `proto_fr_shared_billing`,
`proto_fr_rapturous_applause` and `proto_fr_unheard_confession` went on
2026-09-16.

R269 ruled the Stage, and its brief's §2 retires the reframe by name. The
sixteen rows left the surface with `EB-719` (2026-09-08) when batch one landed;
`EB-726` took the rest of the arm — the `FurinaReframe` compile switch and its
five flags, the sim's `tier0/engine/furina_reframe.py`, the C# roster, ledger
and opening seams, the Salon panel and its scale table, and every pin that
named one of them.

Retrieval — the last tree that carried the rows, with these blocks:

```
git fetch --depth=1 origin 525c5c58dd0d9aa958284a4b10cd34402ebcf8f5
git show 525c5c58dd0d9aa958284a4b10cd34402ebcf8f5^:docs/prototype-surface.yaml
git show 525c5c58dd0d9aa958284a4b10cd34402ebcf8f5^:docs/notes/prototype-surface-provenance.md
```

SIX FACES ARE FROZEN rather than gone: `docs/notes/retired-prototype-rows.yaml`
carries the six printed titles a sealed reframe round names that nothing in
HEAD resolves, so those records still replay through
`understudy/resource_order.SHEETS` (R101b). Its own header gives the split.

The arm's design reasoning is `review/ruled/furina-reframe-2026-08-29.md`
(R220 A); the published reads stand as published and are not re-graded by this
deletion.

## header

```
# PROTOTYPE SURFACE -- QUARANTINED. R213 B (1050f67), BACKLOG EB-147.
#
# WHAT THIS SHEET IS. One staging surface for cards that are being TRIED, for
# every character at once. A row here is not a card in the game: it is a
# question, put in front of the real engine so the funnel (R213 process) can
# ask whether the turn it produces has a second plausible line. Each row names
# the character it belongs to with `character:`; there is no per-character
# prototype sheet and there will not be one.
#
# THE DELETION RULE, WHICH IS THE POINT OF THE FILE.
#
#     Once a slice is ACCEPTED or REJECTED, its rows LEAVE this surface.
#
# Accepted rows are re-authored onto the owning character's real sheet, with
# their numbers ruled, their stamps bumped and their art commissioned, and the
# prototype rows are DELETED in the same commit. Rejected rows are deleted
# outright; the reasoning goes in the slice's packet under review/, never here
# as a commented-out row. This surface is NEVER a second permanent pool -- an
# empty file is the healthy steady state, and a row that has sat here across
# two slices is a defect in the process, not a backlog item.
#
# WHAT A ROW IS AND IS NOT.
#   IS      -- schema-valid (tier0/content/loader.py's own validators run on
#              it), codegen-expressible (tools/gen_prototype_cards.py must
#              emit it or the row is refused by name), runtime-legal (the
#              emitted class is pool-resolvable, so it does not throw
#              "You monster!" the moment it is drawn).
#   IS NOT  -- in any reward pool, in the release build, in the pck, in a
#              roster digest, in a balance report, in card_distinctness_report,
#              or in any version stamp. None of those tools can see this file.
#
# HOW A ROW IS REACHED. Only by id, through the grant tooling:
# `understudy/scenarios/*.yaml` step `give: {card: KLEEMOD-<ID>, ...}` against
# a DEV build (`dotnet build -p:PrototypeCards=true`). The default build does
# not compile these classes at all, so a shipped mod cannot reach them by any
# route, including a hand-typed id.
#
# ID CONVENTION (enforced, not a habit): every id starts `proto_`. That is what
# keeps a prototype's C# class name and its ModelId out of collision with a
# shipped card, and it is what makes "did this slice leave the surface?"
# answerable with a grep.
#
# `authored_by:` IS REQUIRED ON EVERY ROW, AND IT IS NOT A CREDIT LINE
# (EB-190). It is a list of MODEL FAMILIES from the closed set
# {claude, gpt}. The roles are fixed at two -- Claude authors, GPT grades and
# reviews (R217 C; OPERATIONS "Doctrine seat protocol") -- so this list is what
# `understudy/seat.py` reads in order to REFUSE a seat that would grade or
# review its own family's work. Anything a seat contributed BEYOND A CLAUSE
# NAME -- card text, a number, a mode -- adds its family to the row. A row with
# no field, or with a family outside the set, is refused by
# `tools/gen_prototype_cards.py`; the field is stripped before the emitter sees
# the row, so it cannot move one byte of generated C#.
#
# STAGING ONE: docs/current/OPERATIONS.md, "Prototype surface (EB-147)".
#
# There is deliberately no `[]` below for a staged row to trip over: an empty
# YAML document loads as null, and every reader of this file spells that
# `or []`. Append list rows directly under this header.
```

## before proto_shinobu_sanctifying_ring_either

```
# Shipped twin: `shinobu_sanctifying_ring` (3 damage to all + Electro, 4 Block,
# cost 2). The Electro rides the card-level interface, so the flag sits on the
# attack mode and the Block mode applies nothing.
#
# THE MODE LABELS NAME THE ELEMENT'S SCOPE, and that is a text fix taken from
# the round-1 pair read, which found "Choose one: ... | Gain 4 Block" printed
# beside an "Applies Electro" keyword badge with nothing saying WHICH mode the
# badge belongs to. The runtime answer is the damage mode only: the emitted
# body sends the attack half through `DamageCmd.Attack(...).FromCard(this)`,
# which is what applies an `IElementalCard`'s element, and sends the Block half
# through `CreatureCmd.GainBlock`, which applies nothing. The label prints
# that, and no number moves.
#
# THE LABEL SAYS "its element" RATHER THAN "Electro", and that is a lint
# constraint rather than a preference: `lint_prose_constants` reads a display
# string carrying an element name AND a bare numeral as a hand-typed reaction
# constant, and "Electro ... 4 Block" collides with `ElectroChargedDot`. The
# element is named by the card's own keyword badge, which is the thing the
# scope clause exists to explain, so the face says WHICH MODE and lets the
# badge say WHICH ELEMENT. Both `either` rows are worded the same way so the
# two arms differ only in the card under test.
```

## before proto_shinobu_sanctifying_ring_either

```
# Shipped twin: `shinobu_sanctifying_ring` (3 damage to all + Electro, 4 Block,
# cost 2). The Electro rides the card-level interface, so the flag sits on the
# attack mode and the Block mode applies nothing.
#
# THE MODE LABELS NAME THE ELEMENT'S SCOPE, and that is a text fix taken from
# the round-1 pair read, which found "Choose one: ... | Gain 4 Block" printed
# beside an "Applies Electro" keyword badge with nothing saying WHICH mode the
# badge belongs to. The runtime answer is the damage mode only: the emitted
# body sends the attack half through `DamageCmd.Attack(...).FromCard(this)`,
# which is what applies an `IElementalCard`'s element, and sends the Block half
# through `CreatureCmd.GainBlock`, which applies nothing. The label prints
# that, and no number moves.
#
# THE LABEL SAYS "its element" RATHER THAN "Electro", and that is a lint
# constraint rather than a preference: `lint_prose_constants` reads a display
# string carrying an element name AND a bare numeral as a hand-typed reaction
# constant, and "Electro ... 4 Block" collides with `ElectroChargedDot`. The
# element is named by the card's own keyword badge, which is the thing the
# scope clause exists to explain, so the face says WHICH MODE and lets the
# badge say WHICH ELEMENT. Both `either` rows are worded the same way so the
# two arms differ only in the card under test.
```

## before proto_itto_superlative_superstrength_either

```
# Shipped twin: `itto_superlative_superstrength` (14 damage, 6 Block, cost 2).
# No element on either mode: the shipped row applies none (`applies_element:
# false`), and adding one would make this a different card as well as a
# differently-priced one.
#
# NO SCOPE CLAUSE ON THIS ROW'S LABELS, unlike the two above, and the absence
# is the honest print rather than an omission: the emitted class declares no
# `IElementalCard` and carries no `Applies ...` keyword at all, so there is no
# badge beside the face for a scope clause to explain. Printing "applying no
# element" on both modes would be answering a question the card does not
# raise.
```

## before proto_shinobu_sanctifying_ring_priced

```
# ---------- ARM 3: the Block priced in the cost line (R216 C, option 4) ------
# The shipped effects EXACTLY, to the digit, and one more energy. Defence is
# paid for in TEMPO. This is the other cheapest answer to E3 and it points the
# opposite way from arm 2: you keep the whole card, and it competes for the
# turn instead of riding along in it.
```

## before proto_spark_priced_strike

```
# ---------- ARM 1: the Attack pays the bank instead of being paid by it ------
# Shipped twin: `flame_on_the_wick` (0, Attack, Uncommon -- 6 damage to a
# single enemy, bank untouched). Cost, type, rarity, target and the damage
# figure all match, so the pair differs in one idea: this card charges the bank
# and hits twice for having done so.
#
# WHY THE PRINTED COST IS ZERO, AND IT IS NOT A ROUNDING CHOICE. A paid Attack
# at a full bank is zeroed and DEBITED by the automatic rule, which would eat
# the three Sparks before this card's own `spend_spark` ran -- the card would
# pay for its cost line and then refuse its own payload. `play_card`'s debit
# branch is guarded by `card.cost != 0` (there since R39/R34, for their own
# reasons), so a printed-zero Attack takes no automatic debit and its top-level
# spend is the only thing that moves the meter. The rule is sidestepped, not
# altered.
#
# THE DECISION IT CREATES is the arm's whole content: with three Sparks and
# this card plus any PAID Attack in hand, playing the paid Attack first makes
# it free and empties the bank, which makes this card unplayable; playing this
# card first takes the bank itself and leaves the other Attack at full price.
# Two Attacks, one bank, and the player picks. That is D2's timing and
# forgoing, on the Attack half of the kit that W3's three Skill sinks left
# without a decision.
```

## before proto_spark_priced_strike

```
# ---------- ARM 1: the Attack pays the bank instead of being paid by it ------
# Shipped twin: `flame_on_the_wick` (0, Attack, Uncommon -- 6 damage to a
# single enemy, bank untouched). Cost, type, rarity, target and the damage
# figure all match, so the pair differs in one idea: this card charges the bank
# and hits twice for having done so.
#
# WHY THE PRINTED COST IS ZERO, AND IT IS NOT A ROUNDING CHOICE. A paid Attack
# at a full bank is zeroed and DEBITED by the automatic rule, which would eat
# the three Sparks before this card's own `spend_spark` ran -- the card would
# pay for its cost line and then refuse its own payload. `play_card`'s debit
# branch is guarded by `card.cost != 0` (there since R39/R34, for their own
# reasons), so a printed-zero Attack takes no automatic debit and its top-level
# spend is the only thing that moves the meter. The rule is sidestepped, not
# altered.
#
# THE DECISION IT CREATES is the arm's whole content: with three Sparks and
# this card plus any PAID Attack in hand, playing the paid Attack first makes
# it free and empties the bank, which makes this card unplayable; playing this
# card first takes the bank itself and leaves the other Attack at full price.
# Two Attacks, one bank, and the player picks. That is D2's timing and
# forgoing, on the Attack half of the kit that W3's three Skill sinks left
# without a decision.
```

## before proto_spark_priced_draw

```
# ---------- ARM 2: the bank buys velocity instead of an Attack ---------------
# Shipped twin: `eager_to_help` (1, Skill, Common -- draw 2 if you have any
# Spark, otherwise draw 1, and the bank is UNTOUCHED). It is the purest "watch
# it rise" card on the sheet: it looks at the bank, takes nothing, and pays
# more for the bank merely existing. This row buys the draw instead.
#
# RE-DERIVED FROM THE CLAUSE, CLAUDE-SIDE, 2026-08-29 (ROUND 3). Rounds 1 and 2
# ran this row on the seat's own re-authoring, and the same model family then
# graded and pair-read it, so both outcomes were PROVISIONAL (packet section
# 11). The repair is not a third grader: the seat's text is DISCARDED and the
# row is derived here from the CLAUSE it named and nothing else.
#
# THE CLAUSE, quoted and used as the only input: "THE COST MUST STAY AT TOP
# LEVEL. A `spend_spark` inside a conditional branch is invisible to the
# playability gate, and the payoff would then fire unpaid. That is a structural
# rule about this verb, not a preference about this card."
#
# THE ORIGINAL PROPOSAL (packet section 2, arm 2, mine): "Draw 1 card. If you
# have 3 or more Sparks: spend 3 Sparks and draw 2 cards." -- cost 1, Skill,
# effects `draw 1` then `conditional if spark_at_least_3 -> [spend_spark 3,
# draw 2]`.
#
# THE DERIVATION, IN THREE FORCED STEPS.
#   1. HOIST. The clause says the `spend_spark 3` may not sit inside the
#      conditional branch, so it moves to the top of the effect list. That is
#      the whole content of the clause and it is mechanical.
#   2. THE GUARD IS NOW DEAD, AND THIS IS ARITHMETIC RATHER THAN TASTE. With
#      the spend at top level, `combat.spark_cost` derives a PLAYABILITY GATE
#      from it (the shipped `powder_charge` behaviour this row reuses): the
#      card cannot be played at all below 3 Sparks. So `spark_at_least_3` is
#      true on every board where the card resolves, and a predicate that is
#      true whenever it is evaluated is not a branch. It is deleted because it
#      cannot change an outcome, not because a preference removed it.
#   3. THE TWO DRAWS COLLAPSE. `draw 1` at top level plus `draw 2` in a branch
#      that always runs is `draw 3`. Both figures are the ORIGINAL proposal's,
#      and both were already lifted off the twin (`eager_to_help` draws 2 with
#      a Spark and 1 without); nothing new is picked.
# The result is: `spend_spark 3` then `draw 3` -- cost 1, Skill, Uncommon.
#
# THIS LANDS ON THE SAME WORDING THE SEAT SUPPLIED, AND IT IS SAID PLAINLY.
# "Spend 3 Sparks. Draw 3 cards." is what the seat wrote as its volunteered
# remedy in round 1, and it is what the three steps above produce from the
# clause alone. That coincidence is expected: a categorical structural rule
# applied to a two-line card has one outcome. What makes this clean is that the
# RECORD now shows the derivation rather than an accepted remedy -- packet
# section 11's own words, "if a derivation lands on the same wording or the
# same number the seat gave, that is fine and it is still clean". The seat's
# text is discarded; this text is derived.
#
# WHAT THE ROW LOST, AND IT IS UNCHANGED FROM ROUND 1: the id kept the word
# `priced` and the slice has NO THRESHOLD ARM. Step 2 is the reason, and it is
# a real narrowing rather than a relabelling.
#
# The Klee generation limb ("no sub-Rare card is simultaneously a spark source
# and a draw enabler") does not reach this row: it is a spark SINK and a draw
# enabler, and the limb bans a SOURCE.
```

## before proto_spark_burst_conversion

```
# ---------- ARM 3: the bank leaves the Attack economy altogether -------------
# Shipped twin: `clockwork_toy` / "Imaginary Friend" (1, Skill, Common,
# skill_tag -- Block 5 and 3 Burst Energy, bank untouched). Cost, type, tag and
# the Block figure are unmoved; the Burst rider stops being free and starts
# being bought, and pays more for being bought.
#
# THE TWIN IS `clockwork_toy` AND THAT IS A REPOSITORY FACT, NOT A VERDICT. The
# proposal named `combustion_study`; it is actually Burst 10 + Draw 1
# (klee-cards.yaml line 160), and the Block 5 + Burst 3 skill_tag Common is
# this one (line 195). The seat pointed at the error, the repository settled
# it, and a corrected fact carries no authorship. And `skill_tag` pays
# BURST_PER_SKILL_TAG = 5 automatically (constants.py:69, combat.py:383), so
# the printed number is never the whole meter movement.
#
# THE PRINTED BURST NUMBER, RE-DERIVED CLAUDE-SIDE 2026-08-29 (ROUND 3). Rounds
# 1 and 2 ran this row at a figure the SEAT chose between two I put to it, and
# the same family then graded and pair-read it, so both outcomes were
# PROVISIONAL (packet section 11). The seat's pick is discarded. The number is
# re-derived here by the packet's own rule -- section 4, "The price, and the
# numbers": every number is LIFTED off a shipped face, or derived once from
# one, and a breakpoint is never invented.
#
#   THE SHAPE IS FIXED BEFORE THE NUMBER IS. This arm is its twin with exactly
#   one idea changed: the Burst rider stops being free and starts being bought.
#   Cost 1, type Skill, `skill_tag` and Block 5 are the twin's and do not move.
#   So the number being chosen is a printed `burst_energy` figure on a card of
#   the twin's own shape.
#
#   THE CANDIDATE SET IS THE SHEET'S, AND IT HAS THREE MEMBERS. Every shipped
#   Klee face that prints `burst_energy`: `combustion_study` 10 (cost 1, Skill,
#   Common, skill_tag), `clockwork_toy` 3 (cost 1, Skill, Common, skill_tag --
#   the twin), `study_of_explosions` 5 (cost 0, Skill, Common, skill_tag).
#
#   TWO OF THE THREE ARE ELIMINATED WITHOUT A JUDGEMENT CALL.
#     * 3 is the TWIN'S OWN figure. Printing it would leave the prototype half
#       identical to the shipped half but for a 3-Spark price -- a pair with no
#       second line, which is the one thing the funnel exists to refuse.
#     * 5 sits on a COST-0 card that pairs its Burst with damage, not Block.
#       Lifting a figure priced at 0 energy onto a 1-energy card is not a lift;
#       it is a figure moved to a different price, which the rule forbids as
#       surely as inventing one.
#   That leaves exactly ONE shipped figure printed at the twin's own cost,
#   type, rarity band and tag, and different from the twin's: `combustion_study`
#   at 10. The derivation is forced, and it uses one shipped face once.
#
# THIS LANDS ON THE SAME NUMBER THE SEAT PICKED, AND IT IS SAID PLAINLY. The
# seat chose 10 on an opportunity-cost argument ("7 additional Burst Energy ...
# a credible opportunity cost against `kaboom`"); that argument is NOT the
# derivation above and is not used here. The candidate set and the two
# eliminations are the derivation, and they arrive at 10 by themselves. Packet
# section 11's own words: what makes it clean is that the record shows the
# derivation, not that the output differs.
#
# WHY THIS ARM EXISTS AT ALL: Sparks and Burst have never interacted in either
# direction. Sparks buy Attacks; Burst fills from Skills and reactions and
# casts the kit Burst. This is the only shape in the slice where the bank buys
# something that is neither damage, defence, nor a Bomb -- it buys progress
# toward the one Klee payoff that is not an Attack. The Burst itself is
# untouched: nothing here grants, drafts or alters Sparks 'n' Splash.
```

## before proto_spark_mode_bombs

```
# ---------- ARM 4: two prices for one card (EB-224) --------------------------
# Shipped twin: `pop` / "Pop!" (0, Skill, basic -- one Bomb dealing 5). The
# CHEAP MODE IS THAT TWIN PRINTED ALONE, exactly, so the pair asks what the
# SECOND mode is worth and nothing else. The expensive mode is `bomb_voyage`'s
# body verbatim (3 Bombs dealing 5), which SHIPS AT 2 ENERGY; here the bank
# buys those two energy instead. Every number on the face is lifted off a
# shipped face and nothing is picked -- the packet's own rule, kept.
#
# WHAT THE BANK BUYS THAT IT HAS NEVER BOUGHT BEFORE: PLACEMENT. D2 lists
# placement as a steerable verb, Klee is the only character in the roster who
# has one, and Sparks have never touched it. It is also the only arm in the
# slice that changes the SHAPE of a turn rather than its size: three Bombs are
# delayed damage on a board the player must survive to collect.
#
# THE DESIGN INTENT, REWRITTEN UNDER R230 (2026-08-30) after KLEESPARK-BT2's
# rerun read the loop on the wire. This row is a BRIDGE. Its priced mode asks
# the player to hold a bank of 3 -- real liquidity, locked up and unavailable
# to anything else until it is released -- in order to buy TWO ADDITIONAL BOMBS
# for a NET COST OF ONE SPARK relative to the free mode once the Bombs
# detonate. (The arithmetic, on a bank of 3 with a detonator in hand: the free
# mode places one Bomb and the starter relic's +1-per-detonation takes the bank
# 3 -> 4; the priced mode places three and takes it 3 -> 0 -> 3. One Spark, for
# 10 more damage.) If an Attack is already in hand that liquidity comes back
# IMMEDIATELY and can be sequenced straight into another sink the same turn; if
# it is not, the bank stays locked until the Bombs go off on their own next
# turn. So the card poses two questions at once: CAN I AFFORD TO TIE UP THREE
# SPARKS RIGHT NOW, and DO I HOLD SOMETHING THAT UNTIES THEM THIS TURN.
#
# The mode is NOT net-free with a detonator in hand, and the refund does NOT
# make the two modes equivalent -- an earlier reading of BT1 said both and R230
# corrects it. R230 also PRE-REGISTERS the arm's whole-fight failure condition:
# if the priced mode proves effectively automatic wherever an affordable
# detonator exists, with no free-mode choices taken and no named reason to
# preserve the extra Spark, the bridge has collapsed into free damage and the
# arm RETURNS TO DESIGN. Packet: klee-sparks-2026-08-29 sec.24.9.11.
#
# WHY THIS ROW WAS HELD, AND WHAT UNHELD IT. The seat stopped it on two written
# clauses (packet sec.6.1). D4 -- "at the decision point the player can
# perceive and forecast the consequences that matter" -- because the
# choose-a-card screen had no per-mode playability, so an unpayable mode was
# offered anyway. `EB-182` built that in both engines and the RE-ASK graded D4
# RESOLVED by name: unaffordable modes are OMITTED (the 0.111.0 decompile gives
# the screen no per-option disabled state to grey), a fully priced-out card is
# REFUSED with a reason naming the price and the bank, and an offered priced
# mode DECLARES its price on its own face. The other clause was the top-level
# cost rule, and R225 amended it: a spend may sit at the card's TOP LEVEL or at
# the HEAD of a `choose_one` MODE, nothing nested or conditional. This row is
# the first in the repo to use the second half of that sentence.
#
# THE SIM NEEDED NOTHING. `choose_one` has shipped since EB-118 Phase 2;
# `effects.mode_price` / `offered_modes` / `mode_refusal` and
# `combat.modal_refusal` are `EB-182`'s, already carrying Furina's shipped
# `deep_breath`; the C# half is
# `ModalChoice.ModePrice` / `SelectAffordableMode` plus the generated
# `ModePrices` table, and `EB-220`'s `MeterCostBadge` paints the mode's Spark
# price by READING that table rather than a second literal. This row is the
# third consumer of machinery that was owed to a SHIPPED defect anyway.
#
# ONE THING WAS OWED, AND IT WAS A DEFECT RATHER THAN A FEATURE. The C#
# GENERATOR knew `spend_spark` as a mode PRICE (`MODE_PRICE_OPS` -> the
# `ModePrices` literal) but not as a mode-body RESOLVER: it was in neither
# `BRANCH_OPS` nor `_emit_branch_op`. So the row blocked -- and any caller
# reaching `emit()` past `blocked_reason` got a mode that declared a 3-Spark
# price, was offered only to a bank that could pay it, and then placed the
# Bombs WITHOUT DEBITING THAT BANK. `EB-224` added the resolver in its GUARDED
# form, matching `spend_charge`: `if (!await SparkPower.Spend(...)) return;`,
# because a mode body has no `IsPlayable` of its own and a screen filter is
# not the engine. Shipped generated output did not move one byte.
#
# THE PRICE IS THE SLICE'S ONE PRICE: THREE. Same attribution rule as the other
# three arms -- 3 is the retired free-Attack threshold, lifted, not picked --
# so this pair asks the same question the slice asks: is the bank worth more as
# this card than as the rule?
#
# NO `skill_tag`, AND THAT IS DELIBERATE. Both donor faces carry it (`pop` and
# `bomb_voyage` are both tagged, and BURST_PER_SKILL_TAG pays 5 automatically),
# but the arm as authored and as put to the seat prints no Burst line. Carrying
# the tag would add an unpriced meter movement to BOTH modes and confound a
# pair whose whole content is the second mode's price.
#
# NO POOL SUBSTITUTION, LIKE ITS THREE SIBLINGS. The slice-1 arms are reached
# by GRANT BY ID against a dev build (`understudy/scenarios/eb147-prototype-
# grant.yaml`), not through `C.SPARK_ALT_POOL_SUBS`, which is the SPARKS
# packet's own one-for-one conversion map and carries none of these four rows.
# The only shipped row this arm names is `pop`, and `pop` is a BASIC starter
# card already substituted through the other seam entirely
# (`C.SPARK_ALT_STARTER_SUBS`); a pool substitution across rarity tiers is
# refused by `rewards.character_pool` by construction. So there is nothing here
# to substitute one-for-one, and inventing a donor Uncommon would be a picked
# number in a slice that has none.
#
# I DESIGNED THIS ROW AND MAY NOT GRADE IT (R213's first guard). The seat GATED
# it twice and wrote no text, no number and no mode, so `authored_by: [claude]`.
```

## before proto_kurages_oath_memory

```
# KOKOMI KURAGE BASE KIT (sec.12 of
# review/ruled/kokomi-kurage-memory-2026-08-29.md) -- ONE row, one arm.
#
# THE QUESTION IT SETTLES IS ALREADY RULED, so this row is a STAGED FACE
# rather than an experiment: sec.12.4 pick 4 asked what happens to Kurage's
# Oath once the jellyfish is always on and its pulse therefore fires every
# turn, and [USER] answered on 2026-08-29, verbatim --
#
#     "Let's rewrite it to '3 block per memory played, upgrade to 5' as a
#      placeholder and see if it needs adjusting later."
#
# So the ward stops riding the pulse and starts riding a MEMORY PLAY. The
# trigger half of that is engine (`effects.kurage_fire`, behind
# `C.KURAGE_MEMORY`, one site covering both the automatic turn-start fire and
# the "Stir" keyword's manual one). The FACE half is this row.
#
# THE NUMBERS ARE [USER]'S AND ARE A PLACEHOLDER IN HIS OWN WORD. 3, and 5
# upgraded. No measurement is attached to either and none may be: nothing has
# been run on this shape, and under R213 B / R215 B no number measured on this
# surface would be quotable if it had. "See if it needs adjusting later" is
# the disposition, not a band.
#
# AUTHORSHIP. NUMBERS AND RULE: [USER]. IMPLEMENTATION AND WORDING: Claude.
# Nothing on this row was designed by the doctrine seat, and nothing here has
# been graded. `authored_by:` is a list of MODEL FAMILIES (EB-190, head of
# file) and [USER] is not one of them, so the field on the row below reads
# `[claude]` -- the family that wrote it -- and this paragraph is where his
# ownership of the numbers is recorded.
#
# THE SHIPPED ROW IS UNTOUCHED. `kurages_oath` in docs/kokomi-cards.yaml still
# prints ward 5 (7 upgraded) and still says "per Bake-Kurage play"; it is a
# shipped number under an R213 freeze and it is not this branch's to move, and
# leaving it alone is what makes accepting this arm a one-row re-authoring
# rather than an engine change.
#
# THE SHIPPED TWIN IS NOT OFFERABLE UNDER THE FLAG, and that is a fix, not a
# second staging rule. [USER] asked of the staged face: "Why does the power
# print 5 instead of 3, exactly?" The answer was that the ward's amount is read
# off whatever card applied it, so a flagged run that DRAFTED the shipped Oath
# paid 5 per memory play under a face that says per pulse -- text that cannot
# bind, which is D4. The sheets cannot move, so the OFFER side does: under
# `C.KURAGE_MEMORY` this row substitutes for `kurages_oath` in Kokomi's
# offerable pool at the same rarity (`loader._pool_substitutions`, read by
# `rewards.character_pool`, which is every offer surface's one source). Flag
# off, the shipped Oath is the only Oath and this row is unreachable as ever.
#
# THE UPGRADE IS ON THE ROW (`EB-213`). It used to be prose here and nothing
# else: the surface had no upgrade channel at all, so the substituted Oath
# could not be smithed at a campfire and [USER]'s upgraded 5 was a row note
# rather than a card. The channel is now the `upgrade:` key below, registered
# into the merged delta index by `tools/gen_prototype_cards.py` and read from
# there by the SHIPPED upgrade path -- same expressibility check, same
# `OnUpgrade`, same campfire. It lives on the row rather than in
# `docs/kokomi-upgrades.yaml` because a `proto_` key in a shipped sheet would
# give R213's deletion rule a second file to remember; when this row is
# re-authored onto her real sheet the delta travels with it, into the
# upgrades sheet, and both leave here together.
#
# THE DELTA IS THE SHIPPED OATH'S OWN, `kurage_ward: +2`. [USER] ruled the two
# ENDPOINTS -- "3 block per memory played, upgrade to 5" -- and +2 is the
# arithmetic between them, not a second pick; it is also, exactly, the delta
# `kurages_oath` already carries (5 -> 7, R130). Nothing new is invented here
# and no measurement is attached to either endpoint.
#
# NAME. "Kurage's Oath" is the shipped card's name and is [USER]'s; this row
# keeps it, because the row IS that card with one clause rewritten and a blind
# reader must see the card, not the experiment (R179).
#
# THE FACE, as it must read once the mod carries it:
#
#     Kurage's Oath -- 1 energy, Power, Common
#     Whenever the Bake-Kurage plays a card from its memory, gain 3 Block.
#     (Upgraded: 5.)
#
# THE ROW SAYS IT, through `description:` (`EB-215`). `gen_klee_cards`
# renders a Power's description PER POWER ID, not per row, so `kurage_ward`
# would print one string -- "Each Bake-Kurage pulse also grants {X} Block."
# -- shared with the SHIPPED Oath, and moving that string would move a
# shipped release face and make it false with the flag off, where the ward
# really does ride the pulse. The mod used to work around that by MERGING a
# replacement into the loc table at pool-build time, which left two channels
# describing one card and the generated file wrong until the override ran.
# R224 A takes `M57`(2) on those DUPLICATION grounds: the row's own text is
# the one channel, emitted by codegen into the same `Localization` list every
# shipped row uses, and the merge is deleted.
#
# The `{PowerAmount:diff()}` token is the SHIPPED renderer, not a prototype
# one: it prints the ruled 3 and, past a campfire, the ruled 5, off the same
# var `EB-213`'s upgrade delta moves.
# =============================================================================
```

## before proto_kurages_oath_memory

```
# KOKOMI KURAGE BASE KIT (sec.12 of
# review/ruled/kokomi-kurage-memory-2026-08-29.md) -- ONE row, one arm.
#
# THE QUESTION IT SETTLES IS ALREADY RULED, so this row is a STAGED FACE
# rather than an experiment: sec.12.4 pick 4 asked what happens to Kurage's
# Oath once the jellyfish is always on and its pulse therefore fires every
# turn, and [USER] answered on 2026-08-29, verbatim --
#
#     "Let's rewrite it to '3 block per memory played, upgrade to 5' as a
#      placeholder and see if it needs adjusting later."
#
# So the ward stops riding the pulse and starts riding a MEMORY PLAY. The
# trigger half of that is engine (`effects.kurage_fire`, behind
# `C.KURAGE_MEMORY`, one site covering both the automatic turn-start fire and
# the "Stir" keyword's manual one). The FACE half is this row.
#
# THE NUMBERS ARE [USER]'S AND ARE A PLACEHOLDER IN HIS OWN WORD. 3, and 5
# upgraded. No measurement is attached to either and none may be: nothing has
# been run on this shape, and under R213 B / R215 B no number measured on this
# surface would be quotable if it had. "See if it needs adjusting later" is
# the disposition, not a band.
#
# AUTHORSHIP. NUMBERS AND RULE: [USER]. IMPLEMENTATION AND WORDING: Claude.
# Nothing on this row was designed by the doctrine seat, and nothing here has
# been graded. `authored_by:` is a list of MODEL FAMILIES (EB-190, head of
# file) and [USER] is not one of them, so the field on the row below reads
# `[claude]` -- the family that wrote it -- and this paragraph is where his
# ownership of the numbers is recorded.
#
# THE SHIPPED ROW IS UNTOUCHED. `kurages_oath` in docs/kokomi-cards.yaml still
# prints ward 5 (7 upgraded) and still says "per Bake-Kurage play"; it is a
# shipped number under an R213 freeze and it is not this branch's to move, and
# leaving it alone is what makes accepting this arm a one-row re-authoring
# rather than an engine change.
#
# THE SHIPPED TWIN IS NOT OFFERABLE UNDER THE FLAG, and that is a fix, not a
# second staging rule. [USER] asked of the staged face: "Why does the power
# print 5 instead of 3, exactly?" The answer was that the ward's amount is read
# off whatever card applied it, so a flagged run that DRAFTED the shipped Oath
# paid 5 per memory play under a face that says per pulse -- text that cannot
# bind, which is D4. The sheets cannot move, so the OFFER side does: under
# `C.KURAGE_MEMORY` this row substitutes for `kurages_oath` in Kokomi's
# offerable pool at the same rarity (`loader._pool_substitutions`, read by
# `rewards.character_pool`, which is every offer surface's one source). Flag
# off, the shipped Oath is the only Oath and this row is unreachable as ever.
#
# THE UPGRADE IS ON THE ROW (`EB-213`). It used to be prose here and nothing
# else: the surface had no upgrade channel at all, so the substituted Oath
# could not be smithed at a campfire and [USER]'s upgraded 5 was a row note
# rather than a card. The channel is now the `upgrade:` key below, registered
# into the merged delta index by `tools/gen_prototype_cards.py` and read from
# there by the SHIPPED upgrade path -- same expressibility check, same
# `OnUpgrade`, same campfire. It lives on the row rather than in
# `docs/kokomi-upgrades.yaml` because a `proto_` key in a shipped sheet would
# give R213's deletion rule a second file to remember; when this row is
# re-authored onto her real sheet the delta travels with it, into the
# upgrades sheet, and both leave here together.
#
# THE DELTA IS THE SHIPPED OATH'S OWN, `kurage_ward: +2`. [USER] ruled the two
# ENDPOINTS -- "3 block per memory played, upgrade to 5" -- and +2 is the
# arithmetic between them, not a second pick; it is also, exactly, the delta
# `kurages_oath` already carries (5 -> 7, R130). Nothing new is invented here
# and no measurement is attached to either endpoint.
#
# NAME. "Kurage's Oath" is the shipped card's name and is [USER]'s; this row
# keeps it, because the row IS that card with one clause rewritten and a blind
# reader must see the card, not the experiment (R179).
#
# THE FACE, as it must read once the mod carries it:
#
#     Kurage's Oath -- 1 energy, Power, Common
#     Whenever the Bake-Kurage plays a card from its memory, gain 3 Block.
#     (Upgraded: 5.)
#
# THE ROW SAYS IT, through `description:` (`EB-215`). `gen_klee_cards`
# renders a Power's description PER POWER ID, not per row, so `kurage_ward`
# would print one string -- "Each Bake-Kurage pulse also grants {X} Block."
# -- shared with the SHIPPED Oath, and moving that string would move a
# shipped release face and make it false with the flag off, where the ward
# really does ride the pulse. The mod used to work around that by MERGING a
# replacement into the loc table at pool-build time, which left two channels
# describing one card and the generated file wrong until the override ran.
# R224 A takes `M57`(2) on those DUPLICATION grounds: the row's own text is
# the one channel, emitted by codegen into the same `Localization` list every
# shipped row uses, and the merge is deleted.
#
# The `{PowerAmount:diff()}` token is the SHIPPED renderer, not a prototype
# one: it prints the ruled 3 and, past a campfire, the ruled 5, off the same
# var `EB-213`'s upgrade delta moves.
# =============================================================================
```

## before proto_muster_subsidy_funnel

```
# =============================================================================
# EB-183 -- MUSTER'S CHARGE SUBSIDY, READ AS A FUNNEL PROPERTY. ONE row, one
# arm, and it is the FIFTH matched pair of a question the first four could not
# finish asking.
#
# R216 D deferred the subsidy into R213 E1 rather than settling it, in these
# words: *a Mustered Companion costs 1 less, Exhausts, and pays 1 Charge, so
# blocking with one also advances Kokomi's finisher*. That sentence has TWO
# readings, and Kokomi slice 2 could only put one of them on a card.
#
#   SLICE 2's reading -- the subsidy's SIGN. The order SPENDS Charge instead
#   of paying it (`proto_charge_muster_price`, "Watatsumi Levy"). That lives
#   in an EFFECT LIST, and it RETIRED with the rest of slice 2 under R227 /
#   M67 (1) -- every arm that priced Charge on a card retired as authored.
#
#   THIS reading -- the recruits of an order that PAID FOR THEM pay no Charge
#   when they Exhaust. It is not an effect list at all: it is a property of
#   the exhaust FUNNEL, so it wants a flag on the RECRUIT plus a check where
#   the wage is paid. Nothing in slice 2 could express it, which is why it was
#   minted as `EB-183` instead of being smuggled into a card row.
#
# THIS ROW IS NOT A RETIRED ARM, AND THE DISTINCTION IS THE ONE R227 DREW. It
# prints NO Charge price and reads the bank at no point; R226's Charge LAW
# ("no card prints a Charge price, no card reads the bank proportionally") is
# untouched by it. What it moves is an accrual the order already paid for.
#
# WHAT IT IS COHERENT WITH, AND WHERE THE TENSION IS -- disclosed, not buried.
# R226 signed the accrual rule as PROSPECTIVE law: 1 per Exhaust of one of her
# own cards, COMPANIONS INCLUDED, and it explicitly did NOT apply v3 §4(iii)'s
# Companion-exclusion clause -- "the funnel does not narrow". This row does
# not narrow the funnel either: it narrows ONE PROTOTYPE ORDER's own recruits,
# by the order's own printed text, and every other Exhaust on the board pays
# exactly what R226 says it pays. A blanket carve-out would have contradicted
# signed text; that is why the flag is stamped by the ORDER and not keyed on
# "is a Companion". [USER] countersigns the pair before it is staged, and this
# paragraph is the thing being countersigned.
#
# HOW IT IS BUILT (both engines, default OFF, no shipped number moved):
#   sim:  `subsidy: waived` on the conscript op stamps
#         `Card.muster_subsidised` (`effects._op_conscript`); the funnel reads
#         it (`refpowers.after_card_exhausted`) and pays 0 Charge. Burst is
#         untouched. Tests: tier0/tests/test_eb183_muster_subsidy_funnel.py.
#   mod:  `KokomiConscript.Run(..., subsidyWaived: true)` stamps
#         `Powers/Prototype/MusterSubsidy.cs`, a `Compile Remove`d file, and
#         the funnel seam in `KokomiResources.cs` sits inside
#         `#if PROTOTYPE_CARDS`. Tests: KleeTests/MusterSubsidyTests.cs.
#   "A PAID ORDER" IS DERIVED, NOT PICKED (R212): the order paid only if it
#         actually put the recruit BELOW its printed cost. A recruit that
#         prints 0 gets no discount (the delta floors) and therefore keeps its
#         wage. The error direction is one-way -- the doubt always pays the
#         SHIPPED wage.
#
# NAME. Provisional and mine (R179), and deliberately an ordinary Inazuma card
# name rather than one that names the experiment: the blind grader reads
# printed titles.
#
# Shipped twin: `mass_mobilization` / "Rally the Isles" (docs/kokomi-cards.yaml
# -- 2 Energy, Uncommon Skill, Muster 2 AND gain 1 Charge). Cost, type, rarity
# and the Muster COUNT are unmoved, exactly as slice 2's arm 4 held them; the
# only thing that moves is where the Charge line sits and which way it points.
#
# THE DELETION RULE AT THE TOP OF THIS FILE BINDS THIS ROW: it leaves when the
# arm is accepted or rejected.
# =============================================================================
```

## before proto_ko_kapow

```
# =============================================================================
# THE KLEE OVERHAUL, SLICE ONE (`review/ruled/klee-overhaul-slice-1-2026-09-01.md`,
# against the ruled brief `klee-brief-2026-09-01.md` sec.3 and sec.8).
#
# NO NUMBER BELOW IS A CLAIM. The slice packet says so in its sec.1: the numbers
# are placeholders so the cards can be played, and the Balance stage prices them
# later with the measurement law.
#
# THESE ROWS ARE REACHABLE, unlike every row above them. Under `C.KLEE_OVERHAUL`
# / `-p:KleeOverhaul=true` the first two ARE the two cards of her own that her
# ten-card starter carries, and the rest ARE her whole offerable pool --
# `loader._starter_ids` and `loader.pool_replacement` in the sim,
# `Klee.StartingDeck` and `KleeCardPool.FilterThroughEpochs` in the mod. With
# the flag off none of them can be reached by any path, which is the acceptance
# condition (`tier0/tests/test_klee_overhaul.py`).
#
# THE OTHER EIGHT STARTER SLOTS ARE NOT ROWS HERE, and that is DRAFT 4 (ruled
# R242 pick 3). [USER]: "the starting deck already does too much; base
# characters open with four Strikes, four Defends and two good cards of their
# own, and Klee had three, two and five." Strike x4 and Defend x4 are the BASE
# GAME's own cards -- `ModelDb.Card<StrikeIronclad>()` in the mod, the `strike`
# and `defend` rows tier0 has carried since `ironclad_starter.yaml` in the sim
# -- so there is nothing for this sheet to say about them. `proto_ko_kaboom`
# and `proto_ko_duck_and_cover` were the renamed twins they replace and are
# DELETED (R213 B); `proto_ko_pop` and `proto_ko_dig_in` left the starter for
# the POOL as Commons, because the canonical shape has no room for either.
#
# TWO NUMBERS MOVED WITH THE SHAPE, both applied defaults disclosed in the
# slice's sec.3. Ka-pow! is 0 energy for 4 -- "cashing costs a card and a
# moment, never energy" -- and its upgrade is Retain with the numbers
# unchanged. Jumpy Dumpty plants a Bomb 8 on the enemy you CHOOSE rather than a
# 6 at random, so the starter's one detonator can line up with it, and its
# upgrade is Bomb 11 / Mine 4 rather than the Prototype rule's default +2/+1.
#
# EVERY ROW CARRIES ITS OWN `description:`. That is the surface's own face
# channel (EB-215) and here it is load-bearing twice over: the printed text is
# the SLICE PACKET's, so what a seat plays is what the packet ruled; and the
# arm's eight ops have no renderer in `build_description`, because writing one
# would be inventing English for rules that may not survive the Prototype gate.
#
# VERMILLION PACT IS NOT HERE. The packet's sec.5 lets it drop -- "the one item
# on this list that touches shared reaction code; if it costs more than a day it
# drops out of slice one" -- and it does; the reasoning is in
# `KleeOverhaulPowers.VermillionPactNotBuilt`. A row for an unbuilt rule would
# be a face that lies.
#
# ONE ROW DECLARES A SHADOW. `proto_ko_sparks_n_splash` keeps the shipped name
# "Sparks 'n' Splash", and it is the one row on this sheet whose shipped twin
# is NOT hidden by the arm: that card is Klee's KIT Burst card, granted to hand
# by the meter rather than offered from the pool, so both are reachable in one
# run. The sheet declares the shadow with a " (proto)" suffix and the PLAYER
# never sees it (`EB-322`): the printed title is the bare name in both engines,
# and where the meter does put the kit card in the same hand the page numbers
# the two the way it numbers any repeated title (`EB-177`). Every other name
# here is the packet's own, because the shipped card that shares it cannot be
# reached while the flag is on.
```

## Klee's Hexerei readers — `proto_ko_` (R244, 2026-09-02)

```
THE RULED PACKET IS `review/ruled/klee-hexerei-readers-2026-09-02.md`, and it
is "slice two" of the Klee brief's sec.7.4: Hexerei is a one-word tag on
companion cards with no effect of its own, and the payoff was always meant to
live in three or four cards inside her OWN pool. Those cards did not exist.
Picks 1, 2 and 4 were taken at their defaults; pick 3 is [USER]'s own card,
replacing the drafted "Alice's Letters".

NO NUMBER HERE IS A CLAIM, on the slice packet's terms: they are a first
honest price against her live pool (Pop! is a 0-cost Bomb 5; Fish-Flavored Bait
is 1 for 4 damage and a Bomb 4; Chained Reactions is a Rare Power at 1 that
places a Bomb 3 whenever a Bomb goes off).

  proto_ko_coven_errand                Common, 1, Skill    upgrade Bomb 7
  proto_ko_witches_circle              Uncommon, 1, Power  upgrade Bomb 5
  proto_ko_alices_introduction_magic   Rare, 1, Skill      upgrade Retain

ONE PER RARITY, and the packet's sec.2 is what makes it three rather than four:
"Hex and Wick" is its sec.3 fourth and stays OUT at pick 1's default, "until
the round-8 read says the coven wants a cheaper fuse". A row for a card the
ruling left out would be scope the packet did not grant.

COVEN ERRAND'S WIDENING IS A FIELD ON THE OP (`wide_if:`) AND NOT A
CONDITIONAL, and the printed face is the whole argument. The card prints ONE
Bomb with one size, so there must be one op owning the one var that size
upgrades through: only a TOP-LEVEL effect owns a var
(`gen_klee_cards._authored_face_numbers`), so a `conditional` wrapping two
`plant_bomb`s would leave the branch's number a literal -- and the `+` card
would print 7 in one clause while placing 5 in the other, which is `EB-288`'s
defect class arriving through the grammar. The predicate is read through the
same registry a `conditional`'s `if:` is read through, and checked at load in
both engines, so the widening cannot invent a spelling the conditional grammar
does not have.

ITS FACE SAYS "place it on ALL enemies instead" WHERE THE PACKET SAID "place a
Bomb 5 on ALL enemies instead", and that is the same rule with the number
printed once. A face that printed the 5 twice would have had one of the two
swapped for the upgrade token and the other left behind as a literal, for the
reason above; "it" is the pronoun that keeps the sentence about one Bomb.

WITCHES' CIRCLE IS DEAD ALONE, AND THAT IS PICK 2 AT ITS DEFAULT. The brief's
own sketch accepted a dead-alone Power as the bridge card, drafted only by a
deck that already holds witches; the packet records the alternative it did not
take ("When you play this, gain 1 Spark", so it is never a blank draw). Klee is
herself Hexerei (brief sec.7.4), so "two witches make a circle" is her plus any
one Hexerei card. Its shape is Chained Reactions' one trigger over, which is
why it sits one rarity down.

ALICE'S INTRODUCTION MAGIC CARRIES TWO DERIVED READINGS, both APPLIED as D
defaults by the packet and both built as written:
  * THE WINDOW IS THIS TURN, over the cards in hand WHEN IT IS PLAYED. A card
    drawn later this turn is not counted, which is why the upgrade is Retain --
    holding it for the big hand is the play. The mark is therefore on card
    INSTANCES (a `HashSet<CardModel>` on the power; a list on the sim's
    CombatState), never on ids, so a second copy of a marked card is not
    marked.
  * IT COUNTS AS HEXEREI ITSELF, so it does not need a second witch to start a
    circle. That is the row's own `hexerei: true` and needs no rule: the row is
    a Klee POOL card carrying a companion sheet key, which the codegen turns
    into `IHexereiCard` exactly as it does for a Universal.

THE MARK HAS ONE READER IN EACH ENGINE, and R244 is what made that matter.
Until now the family had a single reader -- Nicole's Ladder, on
`C.COMPANION_OVERHAUL` -- so `card.hexerei` could be tested inline. Three of
the readers are now on `C.KLEE_OVERHAUL` instead, and one of them widens the
family, so "is this play a Hexerei card?" is answered once
(`companion_hexerei.is_hexerei` / `CompanionHexerei.IsHexerei`) and every
reader is gated on its own arm underneath. Nicole's power was MOVED onto that
reader in the same change; a payoff that still tested the interface itself
would have been the definition that disagreed.

THE PLAY HOOK LANDS ONCE, which is the packet's sec.4 in as many words ("a
Hexerei-play trigger, which the Nicole stand-in already needs, so it lands
once"). The sim has one sequential site (`combat._finish_play` ->
`companion_hexerei.note_card_played`, which counts and then pays both arms);
the mod hangs each PAYOUT on its own power's `AfterCardPlayed` and puts the
COUNT on the arm's one standing card-play listener, because Coven Errand's read
has to be answerable whether or not any power is on the board.

THREE ILLUSTRATIONS WERE OWED, AND `EB-778` PAID THEM (2026-09-16). Each row
wore the nearest Klee illustration through `art_of:` -- Mine Toss for the
Errand, Chained Reactions for the Circle, Alice's Recipe for the Introduction
Magic -- on the terms that art is commissioned when a slice is ACCEPTED. What
that reasoning missed is that a proxy asks for no art of its own, so the debt
could never be seen or worked off; `art_coverage.py`'s ART_OF PROXIES bill made
it visible and each row now carries its own rank-1 plan row (the Witch's
Homework event card, the Hexerei roundel, Alice herself). Nothing is
commissioned: all three are cleared wiki sources, the same tier every other
prototype placeholder uses.
```

## before proto_mc_diona_signature_mix

```
# THE MONDSTADT COMPANION OVERHAUL. Reachable rows, not staged ones: under
# `C.COMPANION_OVERHAUL` these ARE Mondstadt's Universal companion pool, and
# the seventeen shipped Mondstadt rows cannot be offered. Source: the approved
# workshop `companion-workshop-mondstadt-2026-09-01.md` sec.3 (a Paper
# artefact on the companion-workshop branch, not in this tree), whose printed
# text every face below carries.
#
# `hexerei: true` is ONE WORD WITH NO EFFECT (the workshop's sec.1, pick 2:
# "Hexerei is one word on a Universal. It does nothing by itself. Klee's own
# readers and any future Hexerei character's carry the payoff"). The mark is
# carried so a later reader can see which rows the family owns; nothing in
# either engine reads it today, and nothing here pays out on it. A field
# rather than a `tags:` entry because `tags` is already read by four unrelated
# predicates, and adding an inert word to a list four things filter is how an
# inert word stops being inert.
#
# WHAT A ROW HERE IS. Universals only. Every line the workshop's sec.3 marks
# as a STAND-IN is a Klee-only replacement card and is not a Universal; its
# sec.4 coven Personals are Klee's kit rather than companion offers; the Klee
# Hexerei readers are a separate slice. None of the three is on this sheet.
# Inazuma and Fontaine are untouched in every build.
#
# EVERY ROW CARRIES ITS OWN `description:` (EB-215). The face is the
# workshop's printed sentence, with this repo's rendering conventions applied:
# an Attack's element rides the AppliesX keyword chip rather than the text
# (the shipped companion sheet's convention), Block and the named keywords are
# golded, and Exhaust is the keyword rail's.
#
# TEN NAMES DECLARE A SHADOW WITH A "(proto)" SUFFIX. Those ten rewrite a
# SHIPPED row whose name they keep, and `tools/lint_unique_names.py` holds one
# namespace across all six sheets -- so the suffix is what lets the rewritten
# Frostgnaw and the shipped one coexist while the arm is being graded. It is
# the same device `proto_ko_sparks_n_splash` already uses, and it is a SHEET
# KEY AND NOT A TITLE: `EB-322` prints the bare name on the card face in both
# engines, so no player-facing title carries it. The other eleven names are
# new and carry no suffix.
#
# THIRTEEN OF THE WORKSHOP'S THIRTY-FOUR UNIVERSALS LANDED IN A SECOND WAVE,
# each because its printed text wanted an engine hook that existed in NEITHER
# engine when the first twenty-one were built. The hooks are built now, in both
# engines, and the rule that held the rows out is unchanged and still binds
# anything later: a card that cannot be printed as written is left OUT rather
# than replaced by a simpler card -- the same rule the Klee overhaul applied to
# Vermillion Pact. What each row wanted, and what it now spends:
#
#   Diona, Icy Paws           "when THIS Block absorbs damage": a per-instance
#                             Block-absorption trigger. Neither engine can name
#                             which Block a hit ate.
#   Noelle, Sweeping Time     damage equal to your Block: the C# amount-formula
#                             grammar has no `player_block` count (tier0 does).
#   Barbara, Melody Loop      a persistent power that re-applies to the CARD's
#                             chosen target each turn; a power holds no target.
#   Bennett, Passion Overload "your next Attack ... applies Pyro": an element
#                             override on a next-attack buff.
#   Dahlia, Sacramental Shower a trap that resolves BEFORE an enemy attack;
#                             there is no pre-enemy-attack counter hook.
#   Dahlia, Favonian Favor    "whenever a reaction happens this turn, gain 3
#                             Block": a per-reaction event, turn-scoped. The
#                             mod counts reactions but broadcasts none.
#   Durin, Binary Form        a modal Power choosing one of two damage-pipeline
#                             modifiers (reactions deal 50% more to enemies;
#                             Pyro Attacks that react deal 8 more).
#   Razor, Claw and Thunder   "the third Attack you played this turn": no
#                             Attacks-played-this-turn counter in the mod.
#   Razor, Lightning Fang     a timed rider that adds damage AND overrides the
#                             element your Attacks apply.
#   Varka, Sturm und Drang    a Swirl event that remembers the swirled element
#                             for the next Attack.
#   Amber, Explosive Puppet   the same pre-enemy-attack counter as the Shower,
#                             plus incoming-damage reduction (replaced by a
#                             this-turn Strength loss, 2026-10-02).
#   Eula, Glacial Illumination a placed counter that tallies Attacks for two
#                             turns and then pays 8 plus 5 per Attack counted.
#   Mika, Starfrost Swirl     "your next Attack costs 1 less": no next-Attack
#                             cost-discount power exists.
#
# THE `star` FIELD IS THE CHARACTER'S, NOT THE CARD'S, and the workshop gives
# Jean a five-star Uncommon (Gale Blade) beside her five-star Rare. Both
# engines gate the Featured Banner on `star == 5`, so under this arm Gale Blade
# is banner-eligible -- and Mondstadt now designs SIX five-star cards against
# BANNER_FEATURED_SLOTS = 3, so the banner binds on Mondstadt for the first
# time. That is the shipped law applied to a bigger roster, not a new rule, and
# it is written down here because it is the arm's most visible side effect.
```

## before proto_mc_diona_icy_paws

```
# THE SAME OVERHAUL'S SECOND WAVE -- THE THIRTEEN ROWS THAT NEEDED ENGINE
# HOOKS. Same source, same terms and the same deletion rule as the block
# above; what is different is that each of these thirteen was held out of the
# first pass because its printed text wanted a hook that existed in NEITHER
# engine. The hooks are built now, in both, and this block records WHICH HOOK
# EACH ROW SPENDS -- so a later slice can price the hook rather than
# rediscover it.
#
# THE HOOKS, and what was REUSED rather than built:
#
#   THE PRE-ENEMY-ATTACK TRAP (Dahlia's Sacramental Shower, Amber's Explosive
#   Puppet) is the hook Klee's Mine already answers an enemy attack with --
#   `PowerModel.BeforeDamageReceived` in the mod, and the same moment in the
#   sim (`combat._enemy_turn`, after the hit's number is settled and before
#   Block is spent). The traps sit on the PLAYER and read that broadcast from
#   the other side. The intent-based predicate that already exists
#   (`enemy_intends_attack`) was refused for the Mine's own reason: an intent
#   can be answered and then not happen, while a hit about to land cannot.
#   `effects.companion_overhaul_before_enemy_hit`.
#
#   THE INCOMING-DAMAGE REDUCTION (Amber's "take 3 less", REMOVED 2026-10-02:
#   see "The co-op run notes" at the end of this file) was
#   `ModifyDamageAdditive` returning a negative -- `PreventExhaustWardPower`'s
#   shape. It is PURE, because the engine asks it speculatively for the intent
#   preview; the consumption and the volley are one phase later, which is why
#   the C# splits Baron Bunny in two where the sim does not.
#
#   THE BLOCK-ABSORPTION TRIGGER (Diona's Icy Paws) is new. The engine has ONE
#   Block pool, so "this Block" is a MARK on the pool rather than a pile, and
#   a hit that spends Block spends the mark with it -- marked-Block-eaten-first,
#   which is the conservative reading of a question a single pool cannot
#   answer (R212's one-way rule). `effects.companion_overhaul_block_absorbed`.
#
#   THE NEXT-ATTACK ELEMENT OVERRIDE (Bennett's Passion Overload, Razor's
#   Lightning Fang, Varka's banked Swirl charge) is new, and it is the change
#   with the widest blast radius: the element a play applies used to be read
#   straight off the card at three sites, and is now read through ONE funnel
#   in each engine (`effects._element_for`, `AuraCmd.ElementOfPlay`). An
#   application site and a reaction site that disagreed about a card's element
#   would apply one aura and react with another. ORDER IS LAW -- blanket
#   first, one-shots after, LAST WINS -- and both engines assert it against
#   the other's source.
#
#   THE SWIRL EVENT THAT REMEMBERS ITS ELEMENT (Varka) and THE PER-REACTION
#   PAYOUT (Dahlia's Favonian Favor) ride ONE call from the single place each
#   engine resolves a reaction (`reactions._react`,
#   `ReactionEffects.Resolve`), where the CONSUMED element is still in hand.
#   A call to one owner, not a bus: two readers do not earn an interface
#   fanned over every power.
#
#   THE ATTACKS-PLAYED-THIS-TURN COUNTER (Razor's Claw and Thunder, and Eula's
#   tally) is `state.attacks_played_this_turn` in the sim and a new
#   round-rolling `CompanionOverhaulLedger` in the mod. NOT
#   `CurtainCallHooks.AttacksPlayed`, which counts the same thing and is
#   cleared only for Furina -- a Klee key would accumulate all fight, which is
#   the defect that map's own `Purge` comment already records once.
#   Both engines read the counter PLUS ONE, because both count an Attack after
#   it resolves and the card asking is itself the Attack.
#
#   THE NEXT-ATTACK COST DISCOUNT (Mika) is `combat.card_cost` beside the
#   Leading Role discount, and `TryModifyEnergyCostInCombat` in the mod --
#   `SpotlightDiscountPower`'s shape. Both are PURE: the stack is spent by the
#   Attack that takes it, never by being priced, so the playability gate may
#   ask as often as it likes.
#
#   THE BLOCK-READING DAMAGE FORMULA (Noelle's Sweeping Time) is
#   `amount_formula: {count: player_block}`, which tier0 has had since the
#   reference pool's Body Slam and which the C# amount grammar had no reader
#   for. `player_block_calc_rider` is that reader, on the same
#   CalculatedDamageVar path the four riders beside it use.
#
#   A POWER ON A CHOSEN BODY (Barbara's Melody Loop, Eula's Lightfall Sword).
#   A power holds no target, so the TARGET HOLDS THE POWER: both land on the
#   enemy the card named, which is the workshop's own gloss for Barbara ("a
#   persistent applier on a chosen body") and the literal reading of Eula's
#   "place a Lightfall Sword ON TARGET". A body that dies takes the loop or
#   the blade with it. The seam is `ENEMY_APPLY_POWERS`, which also makes the
#   two cards declare `TargetType.AnyEnemy`.
#
#   TWO DAMAGE-PIPELINE MODIFIERS BEHIND A MODAL POWER (Durin's Binary Form).
#   The modal surface itself is EB-118's and needed nothing: `choose_one` in
#   the sheet, `ModalChoice` in the mod. WHITE multiplies the REACTION'S OWN
#   damage -- a Vaporize that turns 10 into 20 has dealt 10 as a reaction, and
#   White makes that 15 -- and it reaches exactly two places in each engine,
#   the amplifier and the Overload splash. Electro-Charged applies a dot POWER
#   rather than damage and is left alone; Superconduct, Frozen, Crystallize and
#   Swirl deal no damage of their own. DARK adds its 8 in the ADDITIVE phase,
#   off a FORECAST of the reaction the standing aura is about to produce,
#   which is the same read `AuraPower.ModifyDamageMultiplicative` makes one
#   phase later.
#
# READ AMBIGUOUSLY, AND HOW.
#
#   1. "WHEN THIS BLOCK ABSORBS DAMAGE" -- one pool, so the marked Block is
#      taken as eaten FIRST. One-way: the paws bite on fewer hits than the
#      other reading would give, and no third reading exists.
#   2. "THE NEXT TIME AN ENEMY ATTACKS YOU" is one HIT, not one intent. A
#      multi-hit intent spends one trap on its first hit and finds none on the
#      second -- the Mine's own consumption rule, met again.
#   3. "TAKE 3 LESS" applies to the hit the trap answers and floors at zero.
#   4. TWO NEXT-ATTACK ELEMENT RIDERS AT ONCE: the damage halves STACK (three
#      separate sentences, three separate numbers) and only the ELEMENT is
#      exclusive, because an Attack applies one. Blanket first, one-shots
#      after, last wins.
#   5. AN OVERRIDE BEATS `applies_element: false`. "Your next Attack applies
#      Pyro" is a statement about the Attack, not a modifier to one it was
#      already making.
#   6. "IF THIS IS THE THIRD ATTACK YOU PLAYED THIS TURN" counts the card
#      asking. Both engines count an Attack after it resolves, so both read
#      the counter plus one.
#   7. "FOR 2 TURNS IT COUNTS YOUR ATTACKS; THEN IT DEALS ..." -- TICK, THEN
#      FIRE AT ZERO, the opposite order from the arm's volleys, because the
#      sentence says "then". Placed on your turn with 2 turns it counts this
#      turn's Attacks and next turn's and pays at the end of the second. The
#      blade's damage carries NO ELEMENT, because the card names none --
#      Solar Isotoma's call, made again.
#   8. "ENEMIES TAKE 50% MORE DAMAGE FROM REACTIONS" scales the REACTION'S
#      contribution, not the hit that triggered it. Stacks ADD (two Durins are
#      +100%, not +125%).
#   9. MIKA'S DISCOUNT DOES NOT DISCOUNT HER OWN CARD. She is the first
#      Attack in the repo to apply a next-Attack rider, which is why the mod
#      needed a latch: the amount standing BEFORE the play is what the play
#      spends, and anything the play itself added survives.
#  10. `role_c` ON A REWRITTEN ROW IS DERIVED FROM THE BODY, not inherited
#      from the shipped twin. Favonian Favor stops applying an element and
#      becomes `buffer`; the shipped row was `applier`.
#
# WHAT THIS BLOCK COST THE SHIPPED PATHS, exhaustively, and every one of them
# is byte-identical with the flag off (pinned, not intended, by
# `tier0/tests/test_companion_overhaul_hooks.py` and
# `KleeTests/Prototype/CompanionOverhaulHookTests.cs`):
#   `combat._enemy_turn`      two guarded calls
#   `combat.card_cost`        one guarded discount, beside Leading Role's
#   `effects._element_for`    one guarded override, read off a per-play snapshot
#   `effects.deal_damage_to_enemy`  one guarded additive term (Durin, Dark)
#   `reactions._react`        one guarded multiplier and one guarded call
#   `AuraPower` / `KleeElementalHooks`  the element read moved behind one funnel
#   `ReactionTable` / `ReactionEffects` two `#if PROTOTYPE_CARDS` blocks
```

## The Kokomi overhaul, slice one, draft 6 — `proto_kk_` (2026-09-02)

Thirty rows: the two cards of her own that the ten-card starter carries, the
twenty-six pool rows of
`review/ruled/kokomi-overhaul-slice-1-2026-09-01.md` **draft 6**, written
against the ruled brief `kokomi-brief-2026-09-01.md` draft 6 (direction ruled
R240, brief approved R241). Under `C.KOKOMI_OVERHAUL` /
`-p:KokomiOverhaul=true` these ARE her starter and her whole reward pool; with
the flag off they are unreachable, like every other row on this surface. The
last two arrived after round four-c and are `EB-335`'s, below.

**The other eight starter slots are the BASE GAME's Strike and Defend** (R242,
ruled in the same breath as Klee's draft-4 starter: "where a character's basics
are a renamed Strike or Defend with the same stat line, the base game's Strike
and Defend replace them"). `proto_kk_waters_edge` and `proto_kk_coral_guard`
printed exactly the base line -- 1 energy for 6 damage, 1 energy for 5 Block --
so they are DELETED rather than re-priced (R213 B), and the two names come off
the suffix list below with them. The mod uses `StrikeSilent` / `DefendSilent`,
whose frame and energy colour `KokomiCardPool` already borrows; the sim uses
the `strike` and `defend` rows of `content/cards/ironclad_starter.yaml`, at the
base numbers with the base +3 deltas. Her Attacks still apply Hydro, because
the catalyst cadence reads the CHARACTER and not the card -- which the mod only
learned to do here (`EB-307`, `Powers/Prototype/CatalystCadence.cs`).

```
DRAFT 6 REPLACED THE SLICE, IT DID NOT EDIT IT. Draft 2's thirty-three rows
were built on the Tide, played, and failed their gate
(review/ruled/kokomi-overhaul-round-1-2026-09-02.md). The ruled brief's sec.6
cuts Tide, Surge, Exert, the pulse, Orders, Tactics, Spent and the Garment by
name, so every row that printed one of them is GONE rather than rewritten --
which is the deletion rule applied to a slice that was rejected, one draft
before it reached the sheet.

THE `plan:` KEY IS THE SHEET'S ONE NEW FIELD. Draft 6's Plan is not a clause
inside a body: it is the second HALF of a printed face -- what the card does
if it is played on the Bake-Kurage instead of where it would normally go -- so
it is a TOP-LEVEL list of effects in the SAME op vocabulary `effects:` speaks.
Sixteen of the thirty rows carry one, and seven of those sixteen carry
`effects: []` beside it, which is not an omission: a Plan-only card does
nothing this turn, and every reader that indexes `effects` should see that
rather than a missing key.

WHY A LIST AND NOT AN OP. Draft 2 spelled it `{op: plan, then: [...]}` with
exactly one clause, and that was already straining: War Council prints two
clauses ("Deal 4 damage to every enemy AND apply 1 Weak to each") and Battle
Plan prints two ("Gain 2 Energy and draw 1"), which the one-clause rule could
not say. More decisively, the OP spelling could not move the card's declared
TargetType -- and under draft 6 a Plan card has to be AIMABLE AT THE PET,
which is a fact about the whole card and not about one effect in its body.

THE THREE TARGET SPELLINGS, decided by what the card does when it is NOT
planned: a Plan-only row takes `CustomTargetType.Pet`; a row whose now-line
aims at an enemy takes the arm's own `KokomiTargets.PetOrEnemy`; anything else
takes `CustomTargetType.PetOrSelf`. The base library ships the predicates and
every targeting patch for the first and third, so only the middle one is new.

`front_enemy` IS A PLAN-ONLY TARGET SPELLING and the codegen refuses it in an
`effects:` list by name. Rule 3 says a planned hit lands on the front enemy
(leftmost alive); a NOW-line lands where the player pointed, which is what
`enemy` already means everywhere on this surface.

FIVE NEW NOW-VERBS AND TWO PLAN-ONLY CLAUSES. `damage_quarter_max_hp` (Sango
Isshin's "a quarter of your Max HP", floored, computed in one place so the two
halves cannot round differently), `remove_debuff` (Cleansing Wave),
`next_companion_discount` (Rally; a DISCOUNT, where draft 2's Vanguard zeroed),
`carry_out_front_plan` (Change of Plans) and `plan_from_exhaust` (Moon's
Reflection). The two that are legal only inside a `plan:` list are
`plan_twice` (Nereid's Ascension) and `damage_per_companion_last_turn` (Chain
of Command).

EVERY ROW CARRIES ITS OWN `description:` (EB-215). The face is the packet's
printed text with this repo's rendering conventions applied -- Plan and Mend
golded, Exhaust on the keyword rail. No number moves and no clause is added or
dropped.

EIGHT NAMES DECLARE A SHADOW WITH A "(proto)" SUFFIX, and they are: Kurage's Oath,
Slack Water, Song of Pearls, Nereid's Ascension, Sango Isshin, Stolen Chapter,
Undertow and Salt Line -- eight names already owned by a SHIPPED Kokomi row.
(Water's Edge and Coral Guard were two more until R242 replaced them with the
base game's own basics and deleted their rows.) `tools/lint_unique_names.py` holds one namespace across
all six sheets plus the relics, so the suffix is what lets the rewritten card
and the shipped one coexist while the arm is being graded. It is a SHEET KEY
AND NOT A TITLE: `EB-322` prints the bare name on the card face in both
engines, so no player-facing title carries it. The other twenty
names are free, including the two Rares that took constellation names (The
Moon Overlooks the Waters, The Moon, A Ship O'er the Seas) and The Clouds Like
Waves Rippling, which is distinct from the shipped Kokomi row of a similar
shape only by its last word -- the lint reads exact names and both stand.

TWO ROWS ARRIVED AFTER THE SLICE: `proto_kk_tide_wall` and
`proto_kk_shell_guard` (`EB-335`), designed in
`review/ruled/kokomi-overhaul-round-4c-2026-09-02.md` sec.6 and ruled R246 pick
2 at its default. Round four-c is why: three chained Opus seats took the kit
through act 1 and five rooms of act 2 and died on a treadmill, because the
deck's block ceiling never moved off one `Defend+` and one base card while a
Slumbering Beetle's intent grew a printed 2 a round. "The Plan layer answers
act 2's damage questions well, Hard To Kill and standing Block included; it has
no defensive line at all" (that packet's sec.2). Both rows answer it off
machinery the deck already builds rather than off a bigger Defend: Tide Wall
scales on the MORNING's Plan count, which is the deck the seats actually built
(three Plans a turn), and Shell Guard scales on the Tamakushi Casket's strikes,
which the seats watched fire five and six times a turn. Numbers 4/3 and 5/3,
upgrading to 6/4 and 7/4, all four ruled in the packet and prototype numbers by
the ladder.

ONE NEW PLAN-ONLY CLAUSE CAME WITH THEM, `block_per_plan_this_morning`, and it
is a Block clause wearing a count exactly as `damage_per_companion_last_turn`
is a damage clause wearing one -- so it takes `plan_block`'s upgrade key rather
than a sixth key of its own. The count is the WHOLE morning's depth, taken once
when the queue is drained, so a Tide Wall written first, second or last in the
queue pays the same number; a count that grew as the drain went would make one
card's Block depend on the order the player happened to write in. Shell Guard
needed no new clause at all: it is an ordinary `apply_power` onto a window
(`kk_shell_guard` / `ShellGuardPower`) that the Casket's strike asks for, so
the card and The Clouds Like Waves Rippling stay separable -- the Clouds pay
per debuff APPLIED and this pays per Casket STRIKE.

"UNTIL YOUR NEXT TURN" INCLUDES THAT TURN'S MORNING, which is a reading and the
packet's own sentence is behind it: "the morning's Plans that apply Weak strike
it too, so the Block is there before the enemy swings". So the window is closed
one line AFTER the Plans are carried out rather than on the arm's turn-start
roll, in both engines (`kokomi_plan.close_shell_guard`,
`ProtoBakeKuragePower.AfterPlayerTurnStart`).

BOTH ROWS NOW OWN THEIR ART (`EB-778`, 2026-09-16). They carried `art_of:` --
Tide Wall wearing Coral Bulwark's illustration, Shell Guard wearing Salt
Line's -- on the rule the stand-ins used one section up, and that rule was
sound about COST and wrong about VISIBILITY: because `art_coverage.py` bills
the literals the codegen emits, a proxy's debt was unsayable rather than
absent. Shell Guard now takes the Tamakushi Casket TCG card its own text names,
and Tide Wall a lower crop of the full Wish art inside `kokomi_pool`.

WHO DEALS A PLAN'S DAMAGE CHANGED IN THE SAME BUILD (`EB-334`, R246 pick 1).
The slice's sec.5 gave a planned hit HER Strength and HER Weak; round four-c
watched a Strategic enemy's Weak shrink two banked Plans to x0.75 the next
morning while the enemy's own Vulnerable raised none, which is the wrong way
round if the Bake-Kurage is the one hitting. A planned hit is now UNPOWERED --
no Strength, no Weak, no attack buff of hers -- while the APPLIER stays her, so
the aura, the reaction and any debuff a reaction applies are all still hers and
the Casket still answers them. The card face follows: a Plan's damage var is
`KokomiPlan.PlanDamageVar`, which previews the one live term that is left (the
target's Vulnerable) against the front enemy, so the printed Plan line is the
number the morning will deal.

THE RELIC. Tamakushi Casket replaces BOTH Tamanooya's Casket (a misspelling
and a retired rule: the pulse) and the Pearl of Wisdom (whose printed body IS
the exhaust-for-Charge funnel the arm turns off). It carries one number, the
jellyfish's 2 Hydro strike per debuff she applies to an enemy; the jellyfish
is the DEALER, so a pet's absent Strength keeps the 2 a flat 2. It keeps the
companion reward slot (that hook is not a Charge rule, and the Commander
loop's whole army comes through it), and has no upgraded form -- a curated
absence in `tier0/tests/test_starter_relic_upgrades.py` with its reason and
the gate that clears it.
```

## The Inazuma companion overhaul — `proto_mi_` (2026-09-02)

Twenty-four Universals, on the SAME flag as the Mondstadt block above
(`C.COMPANION_OVERHAUL` / `-p:CompanionOverhaul=true`). Source: the approved
workshop `companion-workshop-inazuma-2026-09-01.md` sec.3, approved 2026-09-01
at its four default picks (its sec.9), with two edits already in that text —
Itto's Superlative Superstrength loses its Exhaust, and Mizuki's Mend stays at
10 because the keyword is bounded at entry HP. A Paper artefact on another
branch and not in this tree.

```
ONE FLAG, TWO NATIONS. There is no `INAZUMA_OVERHAUL` property. The arm already
means "the companion pool is the approved workshops' pool", and a second
property would let a build offer one nation's rewrites beside the other
nation's shipped rows -- a state no document describes and no seat would be
asked to grade. `C.COMPANION_OVERHAUL_NATIONS` is the one list the kept half of
the roster is filtered against, and Fontaine is deliberately not in it: its
workshop does not exist yet and both approved documents say so in their sec.6.

TWENTY-FOUR AND NOT TWENTY-FIVE. The document's sec.4 counts "25 Universals, 1
Personal" while its sec.3 enumerates 24 Universals plus Gorou's Kokomi-side
Personal (Crystal Collapse), and the rarity split it prints -- 9 Common, 12
Uncommon, 4 Rare -- only closes when the Personal is counted among the
Uncommons. The ENUMERATION is what is built, so the pool is 9 Common, 11
Uncommon and 4 Rare. A Personal is Kokomi's kit rather than a companion offer;
no stand-in is a Universal either; neither is on this sheet.

NOTHING WAS DROPPED. Every one of the twenty-four prints inside the grammar the
emitter speaks once the arm's fifteen powers exist, so the rule the Mondstadt
waves kept -- "a card that cannot be printed as written is left OUT rather than
replaced by a simpler card", the rule that left Vermillion Pact off the Klee
surface -- bit on nothing here.

FIFTEEN NAMES DECLARE A SHADOW WITH A "(proto)" SUFFIX, and they are the fifteen
rewrites of shipped Inazuma rows, whose printed names they keep.
`tools/lint_unique_names.py` holds one namespace across all six sheets plus
this surface, so the suffix is what lets the rewritten Thundergrust and the
shipped one coexist while the arm is graded. It is the same device the ten
`proto_mc_` rewrites and the eleven `proto_kk_` rows already use, and it is a
SHEET KEY AND NOT A TITLE: `EB-322` prints the bare name on the card face in
both engines, so no player-facing title carries it. Gorou's
Uncommon is NOT suffixed: the workshop renames it "Juuga: Forward Unto Victory"
where the shipped row is "Forward Unto Victory", so the two names differ
already. The other eight new characters' names are new.

EVERY ROW CARRIES ITS OWN `description:` (EB-215), the workshop's printed
sentence with this repo's rendering conventions applied: an Attack's element
rides the AppliesX keyword chip rather than the text, a POWER's volley names
its element in the sentence (the shipped `proto_mc_` convention), Block and the
named keywords are golded, and Exhaust is the keyword rail's. No number moves
and no clause is added or dropped.

WHAT THE HOOKS COST, and the headline is how little. Thirteen hooks were built
for the Mondstadt second wave and TWELVE of this pool's rows spend one without
a line of new plumbing:

  end-of-turn volley       Gorou's Juuga, Sayu's Daruma, Shinobu's ring,
                           Yae's Sakura, Ayaka's Soumetsu, Ayato's clock,
                           Chiori's Tamoto
  start-of-turn payout     Sayu's Naptime, Sara's Stormcall, Kirara's parcel
  Block-absorption mark    Thoma's Blazing Barrier (Diona's Icy Paws)
  next-Attack element      Sara's Crowfeather Cover, Ayato's Kyouka
                           (Bennett's Passion Overload, Razor's Lightning Fang)
  the reaction event       Heizou's Swirl count (Dahlia's Favonian Favor)
  a power on a chosen body Yoimiya's Aurous Blaze (Barbara's Melody Loop)
  AfterCardPlayed          Thoma's Crimson Ooyoroi

FOUR THINGS ARE NEW, and each is small:

  A PER-PLAY DAMAGE TOTAL. Gorou's Inuzaka All-Round Defense prints "Gain Block
  equal to half the damage dealt", and the printed 8 is not what landed once
  Strength, Weak, an amplifier and the target's Block have spoken. The total is
  `state.mi_damage_dealt_this_card` in the sim (written at the tail of
  `deal_damage_to_enemy`, zeroed at the head of `resolve_card`, saved across a
  free play with `block_gained_this_card`'s neighbours) and
  `CompanionOverhaulLedger.DamageDealtThisPlay` in the mod (totalled from
  `CompanionOverhaulPlayWatcher.AfterDamageReceived`). It counts HP damage from
  a CARD, which is the conservative reading of "the damage dealt" (R212's
  one-way rule -- the doubt pays LESS Block) and is also what keeps the two
  engines counting the same thing: the arm's power-sourced hits pass neither a
  dealer nor a card source, so neither engine counts them. The op is
  `block_half_damage`, Kokomi's `block_half_surge` asking about a different
  total.

  A HIT THAT IGNORES BLOCK. Chiori's Tamoto, "ignoring Block": one optional
  parameter on `deal_damage_to_enemy` and one on `ElementalHit.Deal`, both
  defaulted off, adding `ValueProp.Unblockable` beside the `Unpowered` a
  power-sourced hit already carries. The hit still reacts, still counts as a
  hit and is still capped by Intangible -- unblockable is not uncappable
  (R128).

  A SWIRL COUNT. Heizou's Heartstopper Strike, "4 more for each Swirl this
  turn": one integer written at the ONE site each engine resolves a reaction,
  beside Varka's latch and off the same event, so the two readers cannot
  disagree about what a Swirl was. `swirls_this_turn` in the amount grammar.

  A COMPANIONS-PLAYED COUNT. Raiden's Musou no Hitotachi, "5 more for each
  Companion card you played this combat": no new state at all, because both
  engines already keep the list -- `state.companions_played` and
  `CompanionPlays.PlayedThisCombat`, both unique by base id under the
  BFF-dedupe ruling of 2026-08-06. So the count is CARDS and not PLAYS, which
  is what "each Companion card" names.

MEND, MADE CHARACTER-AGNOSTIC, AND THE RULE NOT DUPLICATED. Mizuki's Anraku
Secret Spring Therapy is a UNIVERSAL that prints the Kokomi arm's keyword, so
Klee or Furina can draft it and "the one true heal in the pool" has to mean the
same thing in whoever's hands it lands. Exactly ONE LINE moved in the mod:
`KokomiRules.Mend` stops asking `KokomiOverhaul.LiveFor(creature)` and asks
`MendIsLive(creature)`, which is that OR "the companion arm is on and this
creature is a player's". The bound itself -- heal, never above the HP you
entered the fight with -- is still written once, in that same function, and no
second Mend was authored. What the widening costs is one more seat's ledger
entry: `KokomiRules.InstallAll` now captures EntryHp for every seat either arm
reaches, at the same combat-start moment it always did, because a lazily
captured ceiling taken at the first Mend would be the HP the fight had already
lowered. The sim had no Mend at all (the Kokomi arm is C# first and its ten
verbs raise), so `effects.mend` is that rule's first spelling there, and
`_op_mend` resolves under `C.COMPANION_OVERHAUL` while still raising the Kokomi
arm's own error when only that flag is on.

READ AMBIGUOUSLY, AND HOW. Every one of these is a place the printed text does
not settle the question, and the reading taken is the most literal one.

 1. "GAIN BLOCK EQUAL TO HALF THE DAMAGE DEALT" is half the damage that reached
    HP, rounded down -- not the swing. One-way: the doubt pays LESS Block.
 2. "GAIN 2 DEXTERITY FOR 2 TURNS" lasts THIS turn and the next, which is the
    reading Razor's Lightning Fang already gives the identical construction.
    The workshop's italic gloss says "applies this turn too, so THREE turns of
    Block"; the first half is true under this reading and the arithmetic in the
    second half is not. The PRINTED text is what is built (its sec.3 preamble:
    "Printed text only"), and the discrepancy is disclosed rather than settled
    by moving a number nobody ruled.
 3. "DEAL 8, ANEMO, TO A RANDOM ENEMY. SWIRL." is ONE op: the Anemo the Attack
    applies to the body it hit IS the Swirl. A separate `swirl` op would
    re-roll the random target and swirl a different body. Kazuha's "Swirl each"
    is the same reading over an AoE, where a second op would instead be a no-op
    on bodies the hit has already cleared.
 4. "EACH SAKURA YOU PLACE WHILE ONE IS OUT DEALS 3 MORE" is a statement about
    the SAKURA BEING PLACED, which is what its subject says: the first out
    deals 4 and every later one deals 7, whether one or two were already
    standing. So three Sakura are volleys of 4, 7 and 7. The workshop's italic
    gloss ("totems that level up together") suggests the other reading, where
    every placement raises every Sakura; the printed sentence does not say
    that, and the printed sentence is what is built.
 5. "UP TO 3" is read at the FIRE, not at the placement: a fourth Sakura can be
    placed and simply never pays. Conservative, and it needs no stack cap in
    either engine.
 6. "PLUS YOUR STRENGTH" (Yae) is PRINTED, NOT IMPLEMENTED. Every power-sourced
    hit in this arm already runs the dealer's modifiers, in both engines, so
    the clause describes what the volley was always going to do.
 7. "FOR 2 TURNS ... THEN DEAL 16" (Ayaka) fires, ticks, and fires the finale
    AT ZERO -- both on the same turn the clock runs out, because "then" is what
    happens after the two turns and the second turn's own 8 is one of them.
 8. "FOR EACH COMPANION CARD YOU PLAYED THIS COMBAT" (Raiden) counts CARDS, not
    plays: both engines' lists are unique by base id already.
 9. "WHENEVER IT TAKES DAMAGE FROM A CARD THAT IS NOT AN ATTACK" (Yoimiya) is a
    three-way test, not a two-way one. A Skill's damage line and an Attack's
    both arrive as powered card damage; a bomb, a volley or a Shatter arrives
    with no card at all. So the mark fires when a card is present AND its type
    is not Attack -- which also means the blast cannot re-trigger any mark, its
    own included.
10. "AT THE START OF YOUR NEXT TURN, DRAW 2 IF YOU PLAYED NO ATTACKS THIS TURN"
    (Sayu) answers "this turn" at the END of the turn the card was played: an
    Attack there deletes the promise, and anything still standing at the next
    turn's start has already earned its draw.
11. "IF YOU ARE ABOVE 70% HP" (Sayu's Daruma) is read when the Daruma ACTS, not
    when it was summoned. Present tense, and the whole point of the nation's
    shape is that the split follows the fight.
12. "LOSE 3 HP" (Shinobu) is plain HP loss -- `{op: damage, target: self}`, the
    shipped Hot Hands line, Unblockable and Unpowered -- and NOT Kokomi's Exert,
    which is damage Block can eat.
13. TWO MORE ELEMENT RIDERS AT ONCE. Five riders can now claim the element an
    Attack applies and the order is unchanged law: BLANKET first (Razor, then
    Ayato), ONE-SHOTS after (Bennett, then Sara), Varka's banked Swirl last of
    all, LAST WINS. The damage halves all stack; only the element is exclusive.
14. KIRARA CARRIES NO ELEMENT. She is Dendro, this engine has six elements and
    no Dendro aura, and her card names no element at all -- so the row declares
    none and `CompanionElement` is `Element.None`. Inventing one of the six
    would be a design decision wearing a schema default.

WHAT THIS BLOCK COST THE SHIPPED PATHS, exhaustively, and every one is
byte-identical with the flag off (pinned by
`tier0/tests/test_inazuma_companion_overhaul.py` and
`KleeTests/Prototype/InazumaCompanionOverhaulTests.cs`, not intended):
  `effects.deal_damage_to_enemy`   one guarded call at the tail, and one
                                   defaulted `ignore_block` parameter
  `combat._finish_play`            one guarded call beside after_card_played
  `combat._player_turn`            one new per-turn counter cleared
  `combat.new_combat`              the Mend ceiling captured
  `ElementalHit.Deal`              one defaulted `ignoreBlock` parameter
  `KokomiRules.Mend` / `InstallAll` the gate widened; the RULE unchanged

THE BANNER BINDS HARDER. `star` is the CHARACTER's rarity, not the card's, and
this pool designs ELEVEN five-star cards against `BANNER_FEATURED_SLOTS = 3` --
so on any given run the Featured Banner shows three of them and the rest are
unoffered, exactly as it now does for Mondstadt's six. Four of Inazuma's rows
are Rare and all four are five-star, so a run whose banner features no Rare
falls through to Uncommon, which is the ladder's shipped behaviour (R64). That
is the shipped law applied to a bigger roster, not a new rule, and it is
written down here because it is the arm's most visible side effect.

THE DELETION RULE AT THE TOP OF THE SHEET BINDS THIS BLOCK: these rows leave
when the arm is accepted or rejected.
```

## The companion stand-ins — the caretakers (2026-09-02)

(The seam below was emptied 2026-10-03 and deleted 2026-10-08, project review
2026-10-08 pick 3. Jean's rule lives on in `tier0/engine/lions_fang.py` and
`LionsFangPower.cs`. Git keeps the rest.)

```
THE SEAM, AND IT IS THE POINT OF THE SLICE. A stand-in is a whole Klee-only
card, with its own unique name, handed to Klee IN PLACE of one named Universal
(Klee brief pick 6; the approved Mondstadt workshop sec.1; R236 sec.3). It is
NOT a rewrite of the Universal and NOT a second pool: every other character is
handed the Universal and never sees the stand-in.

THREE KEYS ON THE ROW CARRY THE WHOLE CONTRACT, and the two later slices that
add stand-ins use the same three unchanged:

  personal_pool: klee   who may be handed it. A string, or a LIST of character
                        ids (a family stand-in writes `[klee]`). `Card.from_dict`
                        normalises a one-member list to the string, so all six
                        existing readers of the field are byte-identical; a
                        longer list is refused BY NAME rather than silently
                        matching nobody, and the day one is wanted those six
                        comparisons move to a membership predicate first.
  replaces: <id>        the `proto_mc_` Universal it stands in for. Prototype
                        surface only, and it must have a `personal_pool:` --
                        a row that replaces a Universal for everybody is a pool
                        replacement, which the arm already has.
  art_of: <id>          whose illustration it wears. NO plan.tsv row and NO new
                        image -- and, until `EB-778` built the ART_OF PROXIES
                        bill, no surface that said the debt existed either, so
                        write one only where the neighbour's picture is the
                        RIGHT picture: the codegen emits that id into
                        `RosterArt.CardPortrait`, deploy stages ONE flat
                        `images/cards` dir keyed by id (so the Universal's own
                        png is already the file that resolves), and
                        `tools/art_coverage.py` bills exactly the literals the
                        codegen emits -- so the art debt does not move.

IT IS IN NO POOL, and that is structural rather than filtered. The four ids are
absent from `C.MONDSTADT_OVERHAUL_POOL_IDS` and the four types are absent from
`CompanionOverhaulRoster.Universals()`, which are the ONE door each engine's
offer surfaces read. So no reward tier, no shop slot, no Featured Banner roster
and no event pool can contain one.

THE HAND-OFF IS ONE PLACE PER ENGINE, and it runs on the PICK rather than on
the candidate list, which is what makes "the offer odds do not move" a property
instead of a hope: the tiers, the rarity roll and the nation-weighted draw all
happen on the Universals, and the swap is the last thing before the card is
handed over.
  sim   `tier0.engine.companion_standins.hand_off`, called by
        `tier05.rewards.roll_rewards` and `tier05.shop.companion_offers`.
  mod   `KleeMod.Powers.CompanionStandIns.HandOff`, called by
        `CompanionSlot.Roll` and `MerchantCompanionSlots.AddSlot`.
The ONE asymmetry: `MerchantCardEntry` does its own draw, so the shop's mod
side maps the candidate LIST. The map is injective and no stand-in is in
`Eligible`, so the list keeps its length; it is applied BEFORE the `stocked`
filter, because `stocked` holds what the other slots actually shelved -- which
for Klee is the stand-in. tier05/shop.py excludes the same row from the other
direction (its `taken` keeps the Universal), and the two agree.

WHY THE FOUR ARE CARETAKERS. Each reads the Klee overhaul's explosion ledger,
which is what a stand-in is for: the Universal is a good card for anybody, and
the stand-in is the same card written for the character whose Bombs are on the
board.

  proto_mc_diona_shaken_not_purred   for Icy Paws. ONE-SHOT. "If a Bomb goes
    off this turn" carries no ordering word, so the condition is about the TURN:
    the card pays at once when one already has (read at `AfterCardPlayed` in the
    mod, `combat._finish_play` in the sim) and otherwise arms a watcher for the
    rest of the turn. A watcher alone would print a card that reads true and
    does nothing.
  proto_mc_noelle_i_got_your_back    for Breastplate. REPEATING, and Mines only.
    "Whenever" is forward-looking and pays per Mine.
  proto_mc_kaeya_cold_blooded_strike for Frostgnaw. A MARKER, spent at the turn
    roll. The card NAMES Grounded, so the blind is a READ by Grounded rather
    than a write to `ko_set_off_last_turn` -- which Jean's stand-in also reads,
    and would have been paid by a write it was never shown.
  proto_mc_jean_lions_fang           for Dandelion Breeze. Grounded's shape with
    a card on it. Its draw is a literal 1 in both engines and deliberately not a
    named constant: it would be the slice's only law number, and naming a `1`
    tagged "draw" makes `lint_prose_constants` read every "Draw 1 card" in the
    mod -- Elemental Ecstasy's included -- as an un-interpolated copy of it.

"THIS TURN" IS THE ROUND, the enemy's half included, and that is not a liberty.
Klee's Mines go off when an ENEMY attacks, so a window that closed at the end of
her own turn would leave "whenever a Mine goes off this turn" unable to fire at
all. Both watchers therefore close where the arm's explosion counters roll --
the start of her next turn (`combat._player_turn` under `klee_overhaul.roll_to`
in the sim, `AfterPlayerTurnStart` in the mod).

WHAT THE SLICE COST THE SHARED PATHS, exhaustively, and each is inert with the
arm off (pinned by `tier0/tests/test_companion_standins.py`):
  `klee_overhaul._explode`       one call, carrying the Mine flag the explosion
                                 bus does not (`ProtoBombPower.Explode` twin)
  `klee_overhaul.turn_start_late` / `GroundedPower`  one `or` on Grounded's test
  `combat._player_turn`          the turn roll, and the played-card retro-pay
  `effects.companion_overhaul_turn_start`  Jean's payout, last and commutative
  `loader._validate_card_shape`  the row's two-line schema rule
  `Card.from_dict`               the `personal_pool` list normalisation
  `CompanionSlot.Roll` / `MerchantCompanionSlots.AddSlot`  the hand-off

THE DELETION RULE AT THE TOP OF THE SHEET BINDS THIS BLOCK: these rows leave
when the arm is accepted or rejected.
## before proto_mc_prune_hexhunter_chime

```
# KLEE'S COVEN PERSONALS (QUARANTINED, R213 B / R236). Four rows, and they are
# the whole of the approved Mondstadt workshop's sec.4 plus the Prune entry in
# its sec.3. Same arm and same flag pair as the two nation blocks above; what
# is different is the CHANNEL. A Personal is not a Universal: `personal_pool:
# klee` is filtered at every offer site in both engines (`rewards`, the shop's
# `eligible`, `CompanionPool.IsOfferable`), so these four are offered to Klee
# and to nobody else, they are on neither nation's pool list, and neither
# nation's count moves. R234 P5 allows three to five Personals; these four are
# the set.
#
# PRUNE SUPERSEDES HER OWN SHIPPED ROW, and it costs no second rule. The Chime
# is `prune_witch_hunt` re-authored, and under the arm the shipped row is gone
# because the replacement KEEPS only rows of a nation the arm does not replace
# -- Prune is Mondstadt. So the supersession is the nation filter that was
# already there, and with the flag off the shipped row is byte-identical. Her
# illustration was REUSED rather than re-fetched: `art_of: prune_witch_hunt`
# was read at the codegen's one `CustomPortrait` line. `EB-778` (2026-09-16)
# gave the row its own pick -- Prune's TCG card, a DIFFERENT picture from the
# Wish splash the shipped row holds -- so L11's one-producer-per-out-path rule
# is untouched: two plan rows, two out-paths, two pictures.
#
# THE NATIONS ARE THE CHARACTERS' OWN, and two of them are new here. Sayu is
# Inazuma; Qiqi and Yaoyao are LIYUE, which has no workshop, no shipped
# companion row and no card in either nation pool. Nothing breaks: `nation` is
# free text that two things read, the reward slot's same-nation weighting and
# the shop's HOME slot filter, so an off-region Personal is weighted lower in
# the slot and reachable in the shop's any-region slot rather than its home
# one. That is today's behaviour applied to a wider roster, not a new rule.
#
# ONE SHARED FILTER MOVED, and it closes a contradiction rather than adding a
# rule. Qiqi is a FIVE-STAR character, so `star: 5`; the Featured Banner is
# rolled from `five_star_roster`, which excludes Personals by name (a Personal
# is a character's kit, not a draw), and `_banner_filtered` then gated every
# five-star that was not ON a banner -- which made a five-star Personal
# unofferable everywhere instead of rarely. Both engines argued both halves and
# both reached the same split, so both now exempt a Personal from the gate
# (`rewards._banner_filtered`, `CompanionBanner.IsOffered`). NOTHING SHIPPED
# MOVES: `prune_witch_hunt` is the only personal-pool companion in the index
# and it is a four-star, so the clause is unreachable on a release build --
# pinned by `test_companion_coven.py` rather than assumed.
#
# WHAT EACH ROW SPENDS.
#
#   Prune, Hexhunter Chime    the ONE place the companion arm reaches into the
#                             KLEE arm's rules: rule 5's Pyro becomes the
#                             swirled element for ONE explosion. The latch is
#                             on the turn-scoped ledger and not on the power,
#                             and the card is why -- its printed order is
#                             "Deal 8 damage. Swirl. The next Bomb ...", so the
#                             Swirl it names resolves BEFORE the rider it arms
#                             and a latch on the power would always be empty.
#                             Varka's Sturm und Drang is the opposite case (a
#                             Power already standing when the Swirl happens),
#                             which is why the two latch differently.
#   Sayu, Silencer's Secret   no power and no new op at all: `swirl`, `block`
#                             and the `bomb_went_off_this_turn` predicate the
#                             Klee arm already reads in both engines.
#   Qiqi, Herald of Frost     a start-of-turn payout, the SignatureMixPower
#                             shape. "Twice" is two applications at ONE body:
#                             the printed words aim once and then say how many
#                             times, and the second application is what lets
#                             the card be its own reaction.
#   Yaoyao, Yuegui            an end-of-turn volley that places a Bomb, so it
#                             joins the ONE end-of-turn sequencer (it draws
#                             from the rng) and takes the Klee arm's own gate
#                             as well as this one. The clock ticks even where
#                             the Bomb cannot land, which is what keeps the
#                             power from becoming permanent on a board it could
#                             not reach.
#
# THE NAME SAYU'S ROW DOES NOT USE. The ruled paper called this card "Yoohoo
# Art: Fuuin Dash". That name is already spoken for: it belongs to her INAZUMA
# Universal, `proto_mi_sayu_fuuin_dash`, and display names are unique by LAW
# R69 (`tools/lint_display_names.py` over this sheet). So the Personal takes
# her PASSIVE's name -- "Yoohoo Art: Silencer's Secret" -- which is the same
# character's own words and leaves the Universal untouched.
#
# THREE NUMBERS AND NO MORE are in `tier0/constants.py` (`CVN_*`) with C#
# mirrors in `CompanionCovenLaw`: a number a POWER carries lands there, a
# number the CARD prints stays on the row. Prune DECLARES her upgrade
# (`{damage: +3}`, the Prototype-stage rule's own delta) rather than deriving
# one, because the derived default would also bump the Chime's marker stack --
# a number the face does not print, and a second stack would arm the rider
# twice.
#
# THE DELETION RULE AT THE TOP OF THE SHEET BINDS THIS BLOCK: these rows leave
# when the arm is accepted or rejected.
## `proto_mi_gorou_crystal_collapse` — Kokomi's Personal (R236, 2026-09-02)

```
GOROU — CRYSTAL COLLAPSE, and it is the Inazuma workshop's ONE Personal:
"Plan: play a copy of the last other Companion card you played this turn."
1 Energy, Skill, Uncommon, Geo, four-star, upgrade 1 -> 0.

WHY IT IS NOT ONE OF THE TWENTY-FOUR. A Personal is a character's kit rather
than a companion offer. It carries `personal_pool: kokomi`, so it enters the
arm's ROSTER (a row that never did could not be offered to its own character
either) through `C.INAZUMA_OVERHAUL_PERSONAL_IDS` /
`CompanionOverhaulRoster.InazumaPersonals`, and the offer layer's own
`personal_pool in (None, character_id)` filter -- Prune's door since the
shipped Mondstadt sheet -- keeps it out of everybody else's slot. It is
deliberately absent from `C.INAZUMA_OVERHAUL_POOL_IDS`, whose every id is
asserted `personal_pool is None`.

WHY `character: kokomi` ON AN INAZUMA COMPANION ROW. The row prints a `plan:`
line, and `gen_klee_cards.card_level_reason` refuses one on any character but
Kokomi: the emitted body calls her queue and the row declares a pet-accepting
TargetType, so a Plan on anybody else's row would be a rule that character does
not have wearing a schema key. The other twenty-four Inazuma rows are
`character: klee` because they print nothing of hers.

THE ONE NEW CLAUSE: `play_copy_of_companion` / `KokomiPlan.Kind.
PlayCopyOfCompanion`. Two readings the printed text left open, both taken the
same way in both engines:

  * WHEN IS THE CARD CHOSEN? At WRITING time, not at carry-out. "This turn" is
    a fact about the turn the Plan was written on and the Plan resolves on the
    next one, so a read at the morning would find nothing on almost every
    board. The captured card rides the entry (`PlanEntry.card` /
    `Planned.Card`), which is the field `replay_exhausted` already uses.
  * WHAT IS "OTHER"? The card writing the Plan is excluded by IDENTITY, so a
    second copy of Crystal Collapse played earlier the same turn IS other. In
    the mod the exclusion is free (the recorder is an `AfterCardPlayed`
    listener and this runs in `OnPlay`); in the sim it is necessary
    (`combat._finish_play` records the play before the body resolves). Both
    engines assert it, so the two say so for the same reason.

A COPY, NOT THE CARD. Moon's Reflection takes its chosen card OUT of the
exhaust pile and plays that instance; this leaves the original where the first
play sent it and plays a clone (`ICombatState.CloneCard` / `copy.deepcopy`, the
same idiom Anger's self-clone uses), exhausted after so the deck is neither one
card shorter nor one longer. The aim is `KokomiPlan.FrontEnemy`, the reader
every planned hit already uses.

THE EMPTY CASE IS WRITTEN DOWN, not refused: a turn with no other Companion in
it queues a Plan that carries out as nothing. Refusing to queue would make the
pending-Plans badge and the strip lie about the queue's depth, and the face
says what it does with nothing. The strip says which card it holds --
"Crystal Collapse: Gorou — Juuga: Forward Unto Victory", or "Crystal Collapse:
nothing" -- through `KokomiPlan.Entry.Label`, the only Plan that overrides its
strip line.

NEREID'S ASCENSION DOUBLES IT like any other Plan, which is two copies; nothing
about this clause is special to `ResolveAll`'s drain loop.

ART: it carried `art_of: proto_mi_gorou_juuga` and borrowed an illustration
Gorou's Universals already staged. `EB-778` (2026-09-16) minted its own row
after all -- his full Wish art, the fourth picture of the character -- because
a borrowed one is invisible to the art bill and so can never be worked off.

THE DELETION RULE AT THE TOP OF THE SHEET BINDS THIS ROW: it leaves when the
arm is accepted or rejected.
```

## The companion stand-ins — the Hexerei family (2026-09-02)

```
FOUR MORE STAND-INS ON THE SEAM ABOVE, and every key on the row is that seam's
unchanged: `personal_pool: [klee]` (the LIST form, which `Card.from_dict`
normalises to the string), `replaces:` the Universal, and -- until `EB-778`
placed their own rank-1 art on 2026-09-16 -- `art_of:` the same id. Nothing new
was added to the contract for this slice.

WHAT MAKES THEM A FAMILY RATHER THAN CARETAKERS. The four caretakers read the
Klee overhaul's explosion ledger, which is what a caretaker is for. These four
read the REACTION, because Hexerei is the reaction family (the approved
Mondstadt workshop sec.1; R236 sec.3), and each replaces a HEXEREI Universal
and carries the mark itself. Same rarity, same cost, same nation as the row it
stands in for -- a face swap, never a tier move, so the offer odds do not move
for these four either.

  proto_mc_albedo_tectonic_tide       for Solar Isotoma        Rare, 1, Power
  proto_mc_fischl_sinful_hex          for Nightrider           Common, 1, Attack
  proto_mc_sucrose_mollis_favonius    for Wind Spirit Creation Uncommon, 0, Skill
  proto_mc_nicole_ladder_of_ascent    for Revelation           Rare, 2, Power

THE MARK IS MECHANICAL NOW, and this slice is what made it so. The workshop's
sec.1 pick 2 said "Hexerei is one word on a Universal. It does nothing by
itself. Klee's own readers and any future Hexerei character's carry the
payoff", and `hexerei: true` was carried inert on thirteen rows with a test
(`test_the_hexerei_mark_is_inert`) whose own docstring said the reader that
moved it would be the change that moved the test. Nicole's Ladder of Divine
Ascent is that reader. So:

  sim   `Card.hexerei`, read in `tier0.engine.companion_hexerei` and nowhere
        else. The old gate is now a LIST of allowed readers
        (`HEXEREI_READERS`), which keeps a second one a deliberate diff.
  mod   a MARKER INTERFACE, `IHexereiCard`, emitted by the codegen onto any row
        carrying the key. By type rather than by a bool or a list of ids, for
        `CompanionStandIns`' reason: the compiler owns the correspondence, so a
        row deleted from the surface takes its class with it and the arm stops
        building. The interface is declared in Powers/Prototype, which a
        release build removes, and every row carrying the mark is a `proto_`
        row compiled under the same switch -- so a shipped card cannot
        implement it.

FIVE READERS NOW RIDE THE ONE REACTION SITE, and none of them widened it. The
arm's rule is that "a reaction happened" has ONE definition per engine --
`reactions._react` in the sim, `ReactionEffects.Resolve` in the mod -- and the
two existing readers (Dahlia's Favonian Favor, Varka's Sturm und Drang) hang
off it. Three of these four join them there: Albedo's on ANY reaction,
Sucrose's on one that DEALS DAMAGE, Fischl's on an ELECTRO one.

  AN ELECTRO REACTION IS DERIVED, NOT PASSED. The site hands over the
  reaction's NAME and the CONSUMED AURA, and that pair names both elements:
  Overload, Superconduct and Electro-Charged are the three reactions Electro
  can be the TRIGGER of, and every other way Electro takes part is as the aura
  that was standing. Anemo and Geo never stick as an aura, so the derivation is
  total -- which is why no hook signature moved for this slice.

  FISCHL'S VOLLEY DEALS ELECTRO AND CAN THEREFORE REACT AGAIN. Two things could
  have gone wrong and neither does. THE LOG: the sim emits its own `reaction`
  event AFTER this call and `settle_amp_delta` rewrites the first one since the
  mark that carries a nonzero `amp_delta` -- but Electro is in no amplifier
  pair, so every reaction the volley can cause carries 0 and is skipped. THE
  DEPTH: each chained firing spends one standing aura and creates none, and a
  volley that instead APPLIES Electro to a bare enemy causes no reaction, so
  the chain is bounded by the enemies on the board.

SUCROSE'S ADDITIVE IS DELIVERED AT THE REACTION SITE, and that is the one
implementation call in the slice worth writing down. Her card and Durin's WHITE
form speak about one quantity -- the damage a reaction deals of its own -- so
they must reach the same reactions: the two amplifiers' contribution and the
Overload splash, which is `companion_overhaul_reaction_mult`'s own written
boundary. It is NOT folded into the amplifier arithmetic, because the mod's
amplifier is a MULTIPLIER (`AuraPower.ModifyDamageMultiplicative` returns a
factor, with no damage to add a constant to) and the mod's additive phase runs
BEFORE the amplifier, so the same 4 would be scaled there and unscaled in the
sim. THE ORDER, since the two stack: MULTIPLY FIRST, ADD AFTER -- White scales
the reaction's own contribution inside the pipeline, the flat 4 lands
afterwards, so White never scales the 4 and the 4 never enters an amplifier.
Both engines, same sentence. Once per reaction on the reacted enemy, including
Overload: "the reaction deals 4 additional damage" is one promise about one
reaction, not one per body the splash touched.

TWO WINDOWS CLOSE AT THE TURN END, NOT THE TURN START, which is where the
CARETAKERS' two close. Fischl's and Sucrose's are reaction promises, and only
the player makes reactions happen, so nothing is owed during the enemy's half;
the caretakers' watchers have to survive it because a Mine goes off when an
ENEMY attacks. So these two sit with Dahlia's and Bennett's in
`companion_overhaul_turn_end` / `AfterSideTurnEnd`, and both hold a row in the
co-tenancy ledger (`tier0/tests/test_reaction_phase_parity.py`).

NICOLE PAYS FOR HER OWN CARD, once. Her stand-in carries the mark like the
Universal it replaces, and the card-played site runs AFTER the body in both
engines -- the same contract Diona's stand-in already leans on -- so the power
the card just applied is standing when the site fires. That is a consequence of
the engines' contract rather than a special case, and it is identical in both.

TWO FACES ARE THE WORKSHOP'S SENTENCE WITH THIS REPO'S RENDERING APPLIED. The
reaction is spelled "[gold]Elemental Reaction[/gold]" (the shipped spelling,
which `tools/lint_text_conventions.py` enforces) and a bonus is "N additional
damage" rather than "N more damage" (the base game's own ratio, 36 to 2).
Fischl's ruled text also printed "Apply Electro", which the row does NOT: her
row is an Attack with `applies_element: true`, so the element rides the
AppliesX keyword chip -- the shipped companion sheet's convention, stated in
the Mondstadt block header -- and printing it too would put the face over the
120-character ceiling for a clause the chip already shows.

EVERY ROW'S UPGRADE IS DERIVED. `tier0.content.upgrades.prototype_default_delta`
finds a printed number on all four (a power stack on each, plus Fischl's
damage), so none of them states an `upgrade:` block; the Universal Sucrose
replaces carries a `no_upgrade:` reason and her stand-in does not need one,
because the delta it derives is the power stack and never the printed draw.

THE DELETION RULE AT THE TOP OF THE SHEET BINDS ALL FOUR: they leave when the
slice is accepted or rejected.
```

## before proto_ko_dodoco_cover

The defence shelf, R252 (2026-09-04), Klee round 9 pick 1 taken at its
default. The round-9 run died on act-2 floor 22 with no Block in hand; the
arm carried four defensive rows in thirty-three and offered none in ten
rewards (`review/ruled/klee-overhaul-round-9-2026-09-04.md` §2). The brief's
weakness stands (§6: she cannot block on demand), so every row here is keyed
to the Bomb state and none is a plain Block:

- **Dodoco Cover** (Common): a placer with a Block half, for the opening
  hand with no placer, which reduced every Set off card to a vanilla attack
  (round 9 act 2, fight 1 and fight 3). Cook's turn, paid a little safety.
- **Careful Now** (Uncommon, Retain): Block equal to the largest Bomb, capped.
  The bigger the bomb she is cooking, the more carefully she stands; the cap
  keeps it from making Grounded a stall. The `block_largest_bomb` op reads
  `klee_overhaul.largest_size`, the Splash's own reader since R250.
- **Barbara — Front Row Seat** (stand-in for Let the Show Begin♪): the
  fourth grown-up, Hydro applied twice so Klee's own Pyro does not eat it
  (round 8's Diona finding), Block per Bomb this turn. Same shape as Diona's
  Shaken, Not Purred on the other element.

Numbers are Prototype numbers, D by the ladder; the seats read them on
round 10 before [USER] does.

TWO OF THE FIVE ARE WITHDRAWN on the R253 charter audit and are on no
surface, in no roster and in no engine: Fire Safety (Common, 0 -- Run Away!'s
shape on the React loop) and Safety Lesson (Uncommon Power -- Spray's
Grounded, Block per Bomb going off). The shelf ships as three. The
`bomb_reacted_this_turn` condition STAYS, because Perfect Timing and Sizzle
read it too; the `ko_safety_lesson` power was Safety Lesson's alone and is
deleted with it.

## before proto_kk_tide_chart

The tempo shelf, Kokomi round 9 pick 1 taken at its default (2026-09-04,
disclosed to [USER] with the pick and unanswered before the build; the
packet is `review/ruled/kokomi-overhaul-round-9-2026-09-04.md`). The arm
had thirty rows at a flat cost, no energy gain, two draw cards and nothing
that Retains, and the seats' dead turns were all dilution with no way to
hold or hurry a Plan. Every row here is keyed to the Bake-Kurage:

- **Tide Chart** (Common, 0): REDESIGNED by R257 (`EB-478`). It was "draw 1
  card for each Plan the Bake-Kurage holds", read at PLAY time, and the r15
  seat drew zero on three plays out of four: a seat plays its cheap cards
  before it writes its Plans, so the count the row multiplied was the count it
  had just been dealt rather than the one it was about to bank. The row now
  reads "Next turn, after the Bake-Kurage carries out its Plans, draw 1 card
  for each" -- a promise written on the play and paid at the top of the next
  turn, after the carry-outs, for the Plans that were actually carried out.
  The same play reads forward instead of backward, the blank case survives
  (nothing carried out draws nothing), and the upgrade is one flat card on
  top, which is the only reading that leaves the upgraded row live on a
  morning with no Plans. Both engines carry the promise on one new op
  (`draw_after_plans`) and pay it one line after the drain.
- **Ripple** (Common, 0): a cheap Plan whose now-line is worth playing (2
  Block for 0) and whose Plan pays tempo (1 Energy and 4 Block). Uncommon
  since 2026-09-28: its face became "Draw 1 card" in the core pass, and a
  0-cost self-replacing card falls under LAW's cycling rule (Uncommon+).

TWO OF THE DRAFTED FOUR ARE WITHDRAWN on the R253 charter audit and are not
on the surface: Held Tide (Uncommon, Retain -- Sango Isshin's condition at
Common scale) on the owner's "not all agents always win" clause, because
Retain guarantees the payoff line; and Tidal Rhythm (Uncommon Power, an
Energy back once a turn when the Kurage carries out) as free repeatable
Energy. Both were ruled REQUIRES_MODIFICATION; the shelf ships as two.

Numbers are Prototype numbers, D by the ladder; the seats read them on
Kokomi round 10 before [USER] does.

## proto_mi_ayaka_soumetsu

`EB-698` (Kokomi round 30, lane 1, (c)). The card said "at the end of your
turn, deal 8 Cryo damage to ALL enemies. After 2 turns, deal 16 Cryo damage to
ALL enemies", and the buff said "8 ... then 16 when it ends, lasts 1 turn".
Three plays, and the seat never knew which number was about to land: "after 2
turns" reads as a third event happening AFTER the clock, and neither surface
said how many 8s there are.

What the code does -- `SoumetsuPower.FireVolley` and its twin
`effects.inazuma_overhaul_turn_end` -- is one 8 at the end of each of the N
turns and, on the LAST of them, the 16 beside it. So the last turn pays 24,
which `test_soumetsu_sweeps_twice_then_ends_on_the_big_one` has measured all
along. Both surfaces now say that sentence in that order; the badge carries
the live turns-remaining count on top, because `{Amount}` is one of the three
dumb variables `PowerModel.GetDumbHoverTip` binds on a static row. Neither
number moved, and this supersedes `EB-379`'s wording for this row only --
Kyouka keeps "after 2 turns", where the finale really is the only thing that
happens then.

## proto_mi_gorou_war_banner

`EB-403` (Kokomi round 10, run 1, (c) 1). The face printed "Gain 2 Dexterity
for 2 turns" on a screen whose Dexterity gloss says "It does not decay". Both
sentences are true and they read as a contradiction: what the row grants is
real `DexterityPower`, and the second effect it applies -- `mi_war_banner`,
`WarBannerPower` in `Powers/Prototype/CompanionOverhaulInazuma.cs` -- is a
clock that takes 2 Dexterity back when it runs out, at the end of the turn its
`Amount` reaches 1 (`CompanionOverhaulTurnEnd`, `AfterSideTurnEnd`).

The take-back clause is now on both faces, in that power's own words. The base
Dexterity gloss stays the base rule and the exception is printed where the
exception is made.

`EB-415` then CLOSED the asymmetry this note used to disclose. The take-back
was the power's own constant, `CompanionOverhaulLaw.WarBannerDexterity` = 2,
while the grant is the card's `PowerAmount`, which the upgrade moves to 3 -- so
an upgraded banner granted 3, handed 2 back, and left 1 permanent Dexterity
behind every play. That was never ruled; it is two numbers with different
authors, and it was recorded here as "the shipped rule as written" because the
`EB-403` build found it and did not own it.

The banner now BANKS what it granted and hands that back. In the mod that is a
`Granted` DynamicVar written from `AfterPowerAmountChanged` -- the hook that
fires on both `PowerCmd` paths, which matters because a second banner stacks
through `ModifyAmount` and never through `Apply`'s own tail; in the sim it is
`effects.war_banner_grant`, read off the card's own effects so the upgraded
face banks 3. Neither face's printed numbers moved: the card says "gain 2
Dexterity for 2 turns, then the banner takes it back", with no second number to
disagree with the first, and the badge prints the live `{Granted}` on its smart
row (a var on the static row would reach the screen as a placeholder --
`EB-353`).

## before proto_ko_countdown

The pool pass, Klee round 10 (2026-09-04). Three seats ended turns holding
Spark-priced detonators at 0 Spark with a fat Bomb sitting on the enemy and no
energy-priced detonator drawn. The arm's unconditional cash button is Ka-pow!
and Ka-pow! is the STARTER's -- one card in ten -- so a hand that has already
spent its Sparks has nothing that sets the pile off, and the Bomb the whole
turn was spent cooking grows for another round instead of paying.

Countdown is the pool's energy-priced plain detonator at Common, beside
Sizzle's reaction-keyed one: 1 energy, Set off, draw a card, no Spark price and
no condition on either clause. The draw is what keeps it off `EB-261`'s
playability gate -- `set_off_only` covers a row whose whole body is the Set off,
and a second clause that pays on any board is exactly the difference between a
card that eats a turn and a cantrip -- so it is playable, and pays, with nothing
on the enemy. Its one printed number is the draw, so that is what the smith
moves (`{Cards:diff()}`, the shape Stolen Chapter takes for the same reason).

A SPARK SINK WAS WRITTEN WITH IT AND IS WITHDRAWN: Explosive Spark, the row
that would have turned leftover energy back into Sparks. It is on no surface,
in no roster and in no engine, struck on the audit's C3 clause. The finding is
"she cannot cash a Bomb without Sparks", and a second way to make Sparks
answers a different sentence -- it makes the Spark-priced detonators easier to
fire rather than giving the hand one that never needed a Spark. One row, and it
is the one the finding names.

Numbers are Prototype numbers, D by the ladder; the seats read them on the next
round before [USER] does.

## before proto_ko_stoke_the_fuse

The pool pass, Klee rounds 11 and 12 (2026-09-04). The seats ended fights
holding four to nine Sparks they never spent. The bank fills from every
explosion (rule 4) and almost everything that empties it is a detonator, so a
turn that banks a Bomb banks Sparks with it and the meter climbs at the exact
moment the player has decided not to cash anything. Round 10 answered the
other end of that deadlock -- Countdown, the energy-priced detonator a hand at
0 Spark can always fire -- and left this end open in as many words: the Spark
surplus is "left for the next round to say again with Countdown in the pool".
It said it again.

A SINK WAS ALREADY WRITTEN ONCE AND WITHDRAWN, and the withdrawal is what
shapes this row. Explosive Spark (Uncommon Attack, 0 energy, X Sparks: 3
damage per Spark spent) was read on the C3 clause -- the card's value has to
turn on a choice the player makes, not on a number rising while you watch --
and its value followed the BANK. Spend nine, deal twenty-seven; the card is
worth what the meter happens to hold and the meter fills by itself. Stoke the
Fuse spends the same bank and its value follows the BOMB: the growth lands on
one charge, the charge is one the player chose to keep cooking rather than
cash, and on a board with no Bomb on it the row spends the whole bank and buys
nothing. That is the losing line C1 asks every card to keep, and it is printed
on the face rather than hidden in a rule -- "your largest Bomb", and if there
is no largest Bomb there is nothing to grow.

THE RATE IS QUICK FUSE'S. Three per Spark is lifted off the pool's existing
Spark-priced grow (Quick Fuse: one Spark, "each Bomb on the enemy grows by 3",
then a Set off), so a Spark buys the same growth here that it already buys
there and the sink is priced against a row the seats have played rather than
against nothing. What the two differ on is where the growth lands and what
follows it: Quick Fuse spreads three across an enemy's charges and cashes the
pile immediately, and this puts the whole bank on ONE charge and sets nothing
off. The upgrade moves the rate to 4, the sheet's per-unit grammar, and the
face reads it through the `Grow` var the two grow rows already use
(`{Grow:diff()}`) rather than an `IfUpgraded` swap -- a top-level effect owns
the var, and this is one.

THE FIRST X PRICE ON ANY SHEET, and it splits a Spark cost line in two for the
first time. `spend_spark: all` prints no literal, so what the GATE charges and
what the card PAYS stop being the same number: the gate charges ONE (an empty
bank cannot pay, any bank holding a Spark can) and the payment takes whatever
the bank holds. Both engines say it that way -- `effects.spend_spark_price`
and the emitted `PrintedSparkPrice => 1` -- and the consequence is reported
rather than hidden: the Spark cost badge and the QA packet's cost slot both
read that gate price, so they show "1 Spark" on a card whose face says "Spend
all your Sparks". The face carries the truth and the badge carries the bar to
play it.

WHAT "PER SPARK SPENT" READS, since nothing on the card can print it: the bank
as it stood when the card was played, before its own spend. That is R39's own
reading, `state.sparks_at_play` and `SparkPower.SparksAtPlay`, which are twins
of each other and which equal the amount spent only because the price is
all-in. The codegen refuses `grow_largest_bomb` on any row that does not open
with `spend_spark: all`, so the equality cannot be broken by a later row
quietly.

ONE RESPELLING, FOUND BY A LINT. The ruled face read "3 per Spark spent" with
the second Spark unmarked; `lint_keyword_meters` requires the keyword's gold
markup wherever a face prints the word, so it ships as "3 per [gold]Spark[/gold]
spent". Same words, same reading, one markup pair.

Numbers are Prototype numbers, D by the ladder; the seats read them on the next
round before [USER] does.

## the pool pass, rounds 13 to 16 (`EB-491`, 2026-09-05)

Ten rows, and the readings that asked for each are in
`review/records/klee-pool-pass-2026-09-05.md` §1. What follows is what the
BUILD had to decide, per row and per new rule, and it is here rather than on
the sheet for the reason the file's own header gives.

**`proto_ko_long_fuse` -- the detonator that stays.** As BUILT (rounds 15 and
16) it was the Retained detonator that got dearer the longer it waited: round
15 wanted a detonator that could be held at all, round 16 wanted the free
Retained Ka-pow! last turn to stop being automatic, and a rising hand cost
(`rising_cost: 1`, the base game's own `CardEnergyCost.AddUntilPlayed`,
refused by `blocked_reason` without `retain:`) answered both at once.

**THE ESCALATION CAME OFF on the comparison pass of 2026-09-06**
(`review/records/klee-pool-comparison-pass-2026-09-06.md` §1 and §3 item 1), on
three seat readings that all landed on the same clause: "never a decision ...
the Retain is a lie told by the card frame" (r17), passed "because Retain plus
an escalating cost is a card that punishes the exact hand-holding the rest of
the kit rewards" (r18 Spray), passed without comment (r22 b). The pass wanted a
card that stays in hand for hold-or-fire and Pocket Match already delivers that
at a Spark, so the smallest intervention was the existing card adjusted rather
than a display fix or a replacement: the row keeps `retain: true`, the frame
renders the keyword, and the face is now "[gold]Set off[/gold]. Deal 6
damage." -- **Pocket Match's Energy-priced twin**, and the Energy-priced exit
the r23 assembled deadlock lacked. Sizzle keeps the reaction line, Countdown
the draw, Ka-pow! stays the free one.

**THE AUDIT IS STILL OWED AT THE DOOR.** The adjusted row goes through
`understudy.seat review` on the Codex bridge before any tester sees it, and
that needs the local machine -- it was not run with this edit. The reading it
has to answer is the audit's own: Long Fuse FOLLOWED C2 because
"retaining it once raises its cost from 1 to 2 energy: keeping the detonator
carries a binding price" (`review/records/card-audit-2026-09-04.md`, §5.3 reply
1), and Held Tide was WITHDRAWN on C1 because "Retain waits out the dead
turns".

THE `rising_cost:` MACHINERY STAYS, UNUSED BY ANY ROW. No sheet row carries the
key now, but both engines keep the rule wired -- `Card.rising_cost` /
`rising_cost_risen` added by `combat.card_cost`, rolled by
`klee_overhaul.roll_rising_costs` at turn end, cleared in `_finish_play` and
zeroed by `run_fight`; `IRisingHandCostCard` read by
`KleeOverhaulRisingCost.RollHand` off the arm's one standing turn-end
listener, with the codegen's `retain:` refusal intact. It is covered by a synthetic row in the tests rather
than through this card.

**`proto_ko_all_of_my_treasures` -- a second pile the size of the first.**
Careful Arrangement merges; this copies. The pile it is measured against is
untouched and still growing, which is what makes it a cook decision (play it
on a 12, or wait for a 16) rather than a second merge. THE COPY IS A PLAIN
BOMB and carries no payload: a Mine's defence is not doubled by a card that
prints "Bomb", and Jumpy Dumpty's Mines are that charge's own promise rather
than its size. "Equal to" means equal WHEN PLACED -- from there it grows on its
own schedule, which is rule 9. The row carries no number at all, and
`blocked_reason` refuses one: the size is a read, and a figure on the row
would be a second reading of "your largest Bomb".

**`proto_ko_fish_blasting` -- the lore card, and a third `add_card` zone.**
The brief's §2 asks for "AoE with a cost card" and this is it. The cost is a
Confiscated, and the new decision was WHERE it goes: `add_card` had `hand` and
`discard`, and a Status laid on the discard pile is a card the player knows
the moment of. So the row uses `zone: draw` and both engines SHUFFLE it in --
`CardPilePosition.Random` in the mod, a random index in `effects._add_token`
-- because the whole cost of the Status is not knowing when it arrives. The
face says "Add a Confiscated to your draw pile", which is the codegen's own
`add_card` sentence with the third zone's name in it. It does NOT Set off:
plain pressure, which is what separates it from every detonator beside it.

**`proto_ko_pocket_match` -- the Spark-paid detonator that stays.**
Round 16's turn one is what it is for: Bang Bang! unplayable at 1 Spark with
no Set off in hand. The opening Spark pays this, and Retain means it is still
there on the turn the pile is worth cashing. It was Fwoosh! with Retain and
one less damage; no new rule. R271 sec.4 item 1 then CUT Fwoosh! on exactly
that reading -- Retain is what the seats drafted the pair for, and one point of
damage is not a decision -- so this row is the whole of that shape now.

**A NEW DESIGN, 2026-09-24** ([USER]'s co-op playtest: "Pocket Match is
redundant with Ka-pow!"). 0 Energy, no Spark price, Retain: "Set off only your
largest Bomb on the enemy. Deal 3 damage." (5 upgraded). ONE charge goes off
-- the largest, the oldest on a tie -- as a normal explosion (its Spark,
Explosive Frags and Second Surprise if it was a Mine, a jump for the rest on a
kill), and every other charge stays and keeps growing. It is still a `set_off`
op, with the field `charge: largest`, so every reader of a Set off card sees
it. C# `ProtoBombPower.SetOffLargestAimed` / `SetOffLargest`; sim
`klee_overhaul.set_off_largest`.

**`proto_ko_bombs_away` -- the placer that is not a Skill.**
Round 13's Smoggy reading: one Skill per turn against a kit whose placers are
Skills by rule. Fish-Flavored Bait and Bang Bang! are already Attacks that
place; this is the wide one. Against Mine Toss (1 energy, Skill, Mine 4 on
ALL): a hit now and half the charge, and no Mine. No new rule.

**`proto_ko_fireworks_show` -- CUT by R271 sec.4 item 2 (`EB-749`).** It was
Set off ALL with no hit of its own, at 2 Sparks with a `spark_price: -1`
upgrade. Round 22 read it as "a strictly worse Tinder Toss" and the
consolidation's comparison pass named the merge: Tinder Toss now carries the
line at 1 Spark with 3 damage behind it, and this row is off the surface. The
Spark-price delta it introduced is not orphaned -- three `proto_spark_*` rows
still spell `spark_price: -1`, and `gen_prototype_cards`' upgrade-visibility
gate still reads the Spark badge as an upgrade channel.

**`proto_ko_kindling` -- the React shelf's floor.**
Round 13 read Catalytic Converter as dead in a mono-Pyro deck by its own
printed admission. R244 pick 2 ruled Witches' Circle dead alone ON PURPOSE, so
"dead alone" is not by itself a defect -- but a shelf where every row is dead
alone is a shelf nobody drafts first. This row has a floor: 4 per Bomb on
every foreign aura when an applier went first, and 2 on the largest Bomb when
none did.

TWO READINGS DECIDED HERE. "Aura is not Pyro" is the enemy's CARRIED aura and
no aura does not count, which is `set_off`'s existing `non_pyro` filter (Flame
Dance) read the same way -- the two rows must not disagree about which enemies
are off-element. And an aura'd enemy holding NO Bomb is not a match, because
the face counts Bombs: a board of aura'd but Bomb-less enemies takes the
floor.

TWO PRINTED NUMBERS ON ONE FACE, which no other row on the surface carries, so
the upgrade needed two keys. `grow: +2` moves the per-Bomb amount through the
`Grow` var the three other grow rows already use; `grow_floor: +1` moves the
floor as a play-time `IsUpgraded` literal, with the face carrying the base
game's own `{IfUpgraded:show:3|2}` swap. A second var would render one number
twice, which is how two spellings of one number come to disagree.

**`proto_ko_flash_point` -- the tempo rider, and the arm's one card-borne
Spark.** Sizzle's and Perfect Timing's conditional grammar, paying a Spark and
a card where those pay damage. It is the FIRST slice card that mints a Spark,
and `Rule4_no_slice_card_mints_a_spark` was a real pin on that -- so the pin
now NAMES this one row rather than being deleted: the income is still keyed to
an explosion (it pays only when a Bomb triggered a reaction this turn), and a
SECOND row minting Sparks still fails the test.

**`proto_ko_vermillion_pact` -- the row slice one deferred, built.**
The slice packet's §5 named this as the one item that might drop out and set
out the two roads it could take: re-applying the consumed aura between the
explosion and the card's own hit, or threading a "do not consume" flag through
`ElementalHit.Deal`. THIS IS THE FIRST. The second is a shared-layer change
every character's reactions would have to be re-read against; this one is a
Klee power writing to a Klee enemy through the ordinary front door
(`AuraCmd.Apply` / `reactions.apply_aura`).

THE PRICE OF THAT ROAD IS STATED RATHER THAN HIDDEN, and the deferral's own
note predicted it: the aura really is back on the board, so a third hit in the
same play sees it and every on-apply hook fires again. On a multi-charge pile
that is the card compounding -- each reacting explosion hands the aura back,
so the next charge reacts too and the Attack behind them all still finds it
standing. That is what a 2-energy Rare printed as a rule-breaker buys, and it
is what its face says.

THE SCOPE IS THE FACE'S. "The Attack that Set it off": read off the card
source at the explosion, so a Mine answering an enemy intent (no card at all)
and a Skill's Set off (Quick Fuse, Countdown, Fireworks Show -- no hit behind
the explosion for the aura to feed) both decline. `reacted` gates the payout,
because an explosion into a Pyro aura refreshes rather than reacts and
consumes nothing; a corpse and a board that already holds an aura decline too,
the second being the one-aura invariant both engines keep. Dead alone, like
Witches' Circle beside it: a deck with no applier never puts a foreign aura
up.

REWORKED 2026-09-27 (Klee review; [USER]: "Most of Klee's set off cards are
pyro and do low damage, so that feels like it would combo poorly with hydro").
The face is now "When a Set off makes one of your Bombs react, every other Bomb
it sets off reacts with the same aura." The first aura a charge consumes is put
back before each later charge of the same take (`ProtoBombPower.SetOff` /
`klee_overhaul.set_off`), any card's Set off counts, and nothing carries past
the take: the Set off card's own hit no longer gets the aura back. The scope
paragraphs above describe the retired rule.

**`proto_ko_split_charge` -- the bridge.**
Careful Arrangement's opposite, and the arm's one row that carries charge from
Cook to Spray. The halves are `n // 2` and `n - n // 2`, so an odd Bomb loses
nothing; each rolls its OWN destination, which is `JumpCharges`' rule and
means both can land on one enemy -- on a single-enemy board they always do,
which is the printed losing line (two piles growing 4 apiece where one grew 4,
into Block, for a card and an energy). A MINE'S HALVES ARE PLAIN BOMBS: the
Mine is one fuse and splitting it does not make two, which is the price of the
bridge. A largest Bomb of 1 does nothing, because there is no split of 1 that
leaves two Bombs and halving it would silently delete a charge.

THE UPGRADE BUYS A CLAUSE THE BASE CARD DOES NOT HAVE, so there is no printed
figure for a var to keep honest: `split_grow: +2` is a play-time `IsUpgraded`
literal and the face states the clause in its own `{IfUpgraded:show:...}` hole
-- Tide Chart's shape (`EB-478`).

**FOUR RESPELLINGS, ALL FOUND BY LINTS AND NONE A DESIGN CHANGE.** Four names
collide with shipped Klee cards the arm replaces (All of My Treasures!, Fish
Blasting, Bombs Away!, Vermillion Pact), so each carries the `EB-322` shadow
suffix -- `loader.display_name` strips " (proto)" in both engines, so the
player still reads the bare name. Long Fuse's face drops the word "Retain",
which is the keyword rail's and never a sentence (`text-conventions` rule 13).
Fish Blasting says "Add ... to your draw pile" rather than "Shuffle ... into",
which is the codegen's own `add_card` sentence and keeps the four verbs.
Split Charge's upgrade clause reads "Halves grow by 2." because the
`{IfUpgraded:show:...}` ceiling is 20 rendered characters and "Each half grows
by 2." is 21.

Numbers are Prototype numbers, D by the ladder; the seats read them on the
next round before [USER] does.

## `proto_kk_undertow` -- one damage op with a rider (`EB-441`)

The row was a `conditional` whose two branch numbers were LITERALS in the face,
and the codegen's own note says why nothing could fold them: a branch amount
"owns no var to print a `:diff()` of". So the card carried no `DynamicVar` at
all, and the engine -- which is what turns Strike's printed 6 into the 4 it
prints under Weak -- had nothing to fold. The round-12 act-1 seat read both
faces on one screen, played Undertow into a Weak 1 turn and watched it deal 5:
"Strike's face is Weak-adjusted; Undertow's face is not. I chose the turn's
plays off a number that was 2 too high."

It is one `damage` op with `bonus_vs_debuff: 3` now, rendered through
`CalculatedDamageVar` by the same `calc_rider` machinery `bonus_vs_aura` has
used since the Legibility sprint. The engine folds that var exactly as it folds
Strike's `DamageVar`, and `Calculate(target)` at resolution is the same call, so
the face and the hit are one number by construction rather than by agreement --
and the multiplier reads the HOVERED enemy, so the face answers per body the
question the branch could only ask in the abstract.

THE ARITHMETIC DOES NOT MOVE. 7, or 7+3 on a debuffed enemy, is what "deal 7, or
10 instead" said, and the upgrade's +3 lands on the base exactly as the
`conditional_damage: 3` delta did. It is ONE hit either way, which is the part
worth naming: two would be two aura applications and two reaction rolls.
`KokomiOverhaulKit.HasDebuff` and `kokomi_plan.has_debuff` are the twins the
`target_has_debuff` predicate already used, so the rider asks the question the
branch asked.

`EB-624` PUT BOTH BRANCHES BACK ON THE FACE, and this time both are live.
[USER]'s act-1 run of 2026-09-07 read "Deal 10 damage, already including 3 if
the enemy has a debuff" as a sentence arguing with itself: 10 cannot already
include a 3 that the enemy it is aimed at has not earned. Nothing was wrong
with the number -- it is the paragraph above working exactly as written -- and
the base game simply never writes a conditional that way. `FLATTEN`'s shape is
two numbers and a reader who picks, so the face is "Deal {PlainDamage:diff()}
damage. If the enemy has a debuff, deal {DebuffDamage:diff()} instead."

The two printed halves are `FoldedDamageVar`s, one carrying the base and one
the base plus the bonus. That type is the mod's own subclass of the game's
`DamageVar` -- Strike's var, whose preview is the same
`Hook.ModifyDamage(..., ModifyDamageHookType.All)` call `CalculatedDamageVar`
makes -- with `SimDamagePipeline.TargetMods` added on top, which is exactly the
pair of folds `FrontFoldedDamageVar` already applies to the number the card
deals. A second `CalculatedDamageVar` was not available for the job: the game's
constructor hardcodes the token `CalculatedDamage` and `DynamicVar.Name` is
get-only, so two of them on one card would be one var, and a face needs two
tokens.

THE HIT IS UNTOUCHED. `DamageCmd.Attack` is still handed `CalculatedDamage`,
whose multiplier is still the debuff rider, so it is still ONE hit and the two
printed halves are display only. The upgrade's +3 moves all three bases, or the
face would part from the hit on the first forge and only on an upgraded copy.

AND `EB-484`'s HOVER TIP IS GONE rather than reworded. It carried the pair
because a card has exactly one face and cannot branch it -- true, and it never
had to branch. With both numbers printed and folded, a tip restating the
SHEET's 7 and 10 would be `EB-441`'s own defect arriving on the other surface:
two numbers on one screen computed to two conventions.

## Kokomi, the halves rewrite (R276 pick 1, 2026-09-23)

The rule, now in the brief: **the now-line answers this turn; the Plan line
buys something only a head start can buy. The two halves are never the same
effect at two sizes.** Twelve Plan cards and the starter's Kurage's Oath were
the now-line made bigger, so a safe turn had one right play (write
everything). They were rewritten to the rule: `proto_kk_kurages_oath`,
`proto_kk_feint`, `proto_kk_riptide`, `proto_kk_pincer`, `proto_kk_ambush`,
`proto_kk_exposed_flank`, `proto_kk_coral_bulwark`, `proto_kk_vanguard`,
`proto_kk_stolen_chapter`, `proto_kk_feigned_retreat`, `proto_kk_war_council`,
`proto_kk_battle_plan` and `proto_kk_the_moon_a_ship`. Two per-Plan payoffs
were re-aimed off Plan volume: `proto_kk_well_laid` pays per debuff on the
enemy and has no Plan line, and `proto_kk_tide_wall`'s Plan blocks the front
enemy's intent. The design is `review/ruled/kokomi-review-2026-09-23.md`.

Five new Plan clauses carry it, each Plan-only: `first_attack_twice` (Pincer),
`first_card_free` (Stolen Chapter), `attack_damage_this_turn` (Battle Plan,
the shipped Attack Up window), `damage_if_unhurt` (Feigned Retreat; the entry
records her HP when written and compares at carry-out) and
`block_front_intent` (Tide Wall; the intent is read at carry-out, every hit of
it, and `amount` is the upgrade's flat bonus). Feint's and Coral Bulwark's
Plan lines drop the design's "to the front enemy" and Tide Wall's says "the
enemy", because a card line never names the front enemy
(`tools/lint_text_conventions.py`); the Plan tip says which enemy a Plan hits.

## proto_ko_jumpy_dumpty, `innate: true` (R261, `EB-557`, 2026-09-05) -- undone 2026-10-02, restored 2026-10-03

The co-op run notes (end of this file) took Innate off; the w17 sanity round
(`review/records/klee-sanity-round-2026-10-03.md`) then lost the act-1 boss
on both seats, on seeds where all four earlier seats beat it, with turn-one
Dumpty plays down by about a third. [USER], 2026-10-03: "OK, let's put it
back on." The reasoning below stands again: an opening hand of five holds
1.78 Defends with Dumpty Innate against 2.0 without, about 1 Block, for a
Bomb that starts growing a turn earlier.

THE PLACER IS INNATE AND THE DETONATOR IS NOT. [USER] took none of the four
round-17 options as written: Pop! in the starter was declined ("I still would
rather avoid putting too many actually good cards in the starting deck"), a
relic-planted Bomb was reviewed by GPT and passed over
(`review/records/klee-turn-one-design-review-2026-09-05.md`), and Innate on
both basics was narrowed to one -- "Jumpy Dumpty gains Innate; Ka-pow! does
not". The starter keeps its ten cards and its two kit cards: turn one always
holds the placer, the detonator still has to be drawn, and the other draws
still have to carry the Block.

ARM-SCOPED BY CONSTRUCTION rather than by a flag read. The row exists only on
this surface, so with `KLEE_OVERHAUL` off nothing deals it and the shipped Klee
opening hand is untouched -- which is why the field is on the row rather than
inside a branch either engine has to remember to take.

A FIELD AND NOT AN UPGRADE DELTA, so both faces carry it: an upgrade is a
different card, and a player who smiths the placer must not lose the opening
the ruling gave it.

## the coven's Hexerei mark (`EB-642`, 2026-09-07) -- retired at R276

R276 pick 2 replaced the mark with "Companion": Klee's Spark, Coven Errand,
Witches' Circle, Alice's Introduction Magic and Nicole's Ladder read any
Companion card, so the `hexerei:` key left every row (and its reader left both
engines). See the R276 section at the end of this file.

## Kokomi pool pass two -- the queue as something you operate on (`EB-643`, R265, 2026-09-07)

THE FINDING. Round after round the seats wrote a Plan and then watched it
play itself: a morning is a thing that is READ, not decided. Everything the arm
had asked the player to choose happened before the Plan was queued -- which
card, and whether to plan it at all -- and nothing after. So the pass is eight
rows that reach INTO the queue, plus one new word and one lane rule.

Doctrine audit at the door: FOLLOWS on all nine arms, prompt and reply at
`review/qa/kokomi-pass-two-2026-09-07-prompt.txt` and
`review/qa/kokomi-pass-two-2026-09-07-reply.md`. Prototype numbers, D by the
ladder; nothing here is quotable (R215 B).

### `proto_kk_opening_gambit` -- the first rider

"The next Plan carried out with this one deals double damage" is the arm's
first clause about ANOTHER entry. The next Plan is the one carried out immediately after
this one in the same drain, so Gambit written before Riptide doubles Riptide and Riptide
before Gambit doubles nothing -- the card makes the ORDER of the queue a
decision, which is the pass's whole thesis in one line.

The upgrade moves the now-line (5 to 7) and not the Plan half, because the
Plan half prints no number the upgrade could move: the Vulnerable is the setup
and the doubling is the payoff, and neither is a size. Against Double Tap
(Uncommon, 1, repeat the next Attack) the audit reads Gambit as one damage
worse when the kill must happen this turn, which is the price of the delay.

### `proto_kk_opening_gambit` -- what the rider doubles (`EB-687`, r26 / r28)

The clause said "the next Plan carried out with this one deals double damage",
which reads as a promise about the next Plan whatever that Plan is. The rule
pays only on damage, so a Block or a draw Plan behind the rider is carried out
exactly as written. Seats held the card four times in r28 and twice in r26 with
only Block or draw Plans on the lane and learned the condition from the
`no Plan followed` line AFTER the energy was spent.

The verb leads now -- "Doubles the damage of the next Plan carried out with
this one" -- so the object is on the card before the play. That is the whole of
the fix: no number moves and the WINDOW above is untouched. The longer form,
naming the damageless case outright, measures 150 against the card ceiling's
120; this one measures 118, and `lint_text_conventions` is the gate.

### `proto_kk_second_wave` -- the second rider

"The next Plan carried out with this one is carried out twice." A FLAG and
not a count: an entry carried
out twice under Nereid's Ascension prints its rider twice, and "carried out
twice" said twice is still twice -- so the entry it reaches runs
`CarryOutTimes + 1`, which is 3 under the Ascension and not 4. Both engines
state that at `kokomi_plan.NEXT_PLAN_EXTRA_CARRY_OUT` and at
`KokomiPlan.Kind.NextPlanExtraCarryOut`, and both pin it.

### `proto_mi_heizou_heartstopper` -- one folding convention (`EB-696`, r30)

Kokomi r30 lane 2 (c): "Heizou's face kept printing Deal 6 under Shrink while
Strike printed 4 and Oath 2, and dealt 4." The row's first number was a LITERAL
in the description, so nothing on that screen could fold anything into it --
one hand, two conventions. The card already carries a `FrontFoldedDamageVar` at
`ValueProp.Move`; only the face was not reading it.

So the face takes Well Laid's shape (`EB-539`): the live TOTAL, which is the
base plus the per-Swirl term plus every modifier on the board, with the rate
written beside it as a rate rather than as a second number to add. The same
row's other half is the WINDOW -- the count is taken before the hit, so a
Heartstopper played into a bare board pays nothing for its own Swirl, which is
why the clause "never paid" in the seat's reading. "Counts 4 for each Swirl
made before it this turn" is that rule, on the card. 64 of the card ceiling's
120, two of four sentences.

### `proto_kk_feint` -- the Plan line it could always write (`EB-660`, r25)

The row carried a `plan:` clause from pool pass three and printed no Plan line
at all, so the round-25 seat wrote a Plan with Feint, found the 10 by testing,
and "did not know what it had written" (lane 1, fight 2). Every other
Plan-capable row on the sheet prints its line; the silence was the face's and
not the rule's. The sentence is printed live off the Plan's own `PlanDamage`
var, so a Smithed copy says 13 without a second string, and the face measures
96 of 120 at three of four sentences.

### THE WINDOW ON ALL THREE FACES, AND THE LINE WHEN IT CLOSES (`EB-645`, r23)

The rider lives in ONE DRAIN by construction, and none of the three faces said
so. The r23 defence lane wrote Second Wave with no Plan behind it in the same
morning, got nothing, and read "no enemy lost HP" off a Plan that had done its
whole job. So all three faces now name the window in `EB-623`'s own
vocabulary, which retired the printed word "morning" and replaced it with
Tide Wall's "carried out with it": "the next Plan carried out with this one"
on Opening Gambit and Second Wave, "each later Plan carried out with this
one" on Scout Ahead. And a drain that runs out with a rider in hand files one
more row on the
carry-out log the seats read: `<card>: no Plan followed`
(`KokomiPlan.NoFollowerLine`, `kokomi_plan._drain`'s `plan_no_follower`).

ONLY ON A DRAIN THAT RAN OUT, and not on one a kill cut short: that is
`NoteUnfinished`'s own reading, and "no Plan followed" about a morning nobody
is playing any more would be a fabricated receipt.

### `proto_kk_scout_ahead` -- the row whose value is its position

"Draw 1 card for each later Plan carried out with this one." First of a
three-entry morning it draws 2, last it draws 0, and the count is CARRY-OUTS rather than
entries -- `EB-501`'s reading pointed forwards, so under Nereid's Ascension
first of three is 4.

THE UPGRADE MOVES THE COST AND NOT THE RATE. The rate is the queue's fact and
not the card's: an upgrade that raised it to 2 per carry-out would scale with a
deck the offer screen cannot see, and the card would be a blank in a shallow
morning and the best draw in the pool in a deep one. `{cost: -1}` moves the
half the card owns.

### `proto_kk_second_thoughts` -- the newest Plan back

Change of Plans hurries the OLDEST entry; this takes back the NEWEST, so the
two tempo cards work opposite ends of one queue. The card that wrote the Plan
comes out of the DISCARD pile and its current cost is refunded -- and on the
paths where it is not there (an Exhaust row's own card, a Plan written off the
exhaust pile by Moon's Reflection) the Plan is still cancelled and nothing
comes back, because what the face promises is the card. It is a printed no-op
of the kind this arm already has several of, not a search of every pile for
something that looks similar.

No `plan:` line: a card that unwrites a Plan cannot also be one.

### `proto_kk_ebb_tide` -- RETIRED, round 23 (`EB-649`)

The row cashed the whole queue in for Energy and cards, per ENTRY. It drew
three times on the r23 cap lane and was played none of them: it is "only live
in the situation you spent the previous turn trying to create", which is a
card that asks the player to build the position it then throws away. So the
row left the sheet, `KOKOMI_OVERHAUL_POOL_IDS` and `KokomiOverhaulRoster`.

The RESOLVER stays on both sides with no row spelling it --
`kokomi_plan.cancel_all_plans_cash` and `KokomiPlan.CancelAllForCash`, each
with a note naming `EB-649` -- because the rule is the one a re-issue would
want and deleting a resolver to re-derive it later is how a reading is lost.
Its pins drive it directly, with no card in the path.

### `proto_kk_converging_tide` -- re-aiming what is already written (RETIRED, pool pass three, `EB-655`)

"Every queued Plan aims at this enemy instead of the front." Three readings,
and all three are stated in both engines:

* ONLY THE FRONT AIM MOVES. An ALL clause does not aim at the front and Flank's
  captured set was fixed when its Plan was written (`EB-492`), so there is
  nothing on either for "instead of the front" to be about.
* A PLAN WRITTEN AFTER THE REDIRECT AIMS AT THE FRONT as usual. The face names
  the queue as it stands; a rule that kept re-aiming later writes would be a
  Power the row does not print.
* A DEAD TARGET FALLS BACK TO THE FRONT, read at carry-out -- the arm's
  standing rule for a Plan pointed at a body it no longer finds.

The stamp is a `CombatId` in the mod and the `Enemy` object in the sim, which
is `Planned.Targets`' split verbatim and for its reason.

### `proto_kk_breakwater` and `proto_kk_night_watch` -- DUSK

The new word, and it is a rule about WHEN and nothing else: the Bake-Kurage
carries a Dusk Plan out at the END of the turn it was written on, before the
enemies act, instead of next morning. A ROW FLAG (`plan_dusk:`) and not a
clause, because Dusk is when the whole line lands -- a card cannot have one
dusk clause and one morning clause any more than it can be played on two
turns.

Everything else about a Dusk Plan is a Plan: written by playing the card on the
jellyfish, one entry in one queue, a carry-out for Treatise and Song of Pearls,
and poppable by Change of Plans whether or not it is dusk. Two things it is
NOT: it does not touch the morning's depth (`kk_plans_this_morning` /
`PlansThisMorning` -- Tide Wall, Well Laid and Tide Chart print "this morning",
and an evening is not one), and it is not counted against the two-Plan cap,
because a Dusk Plan has already waited for nothing.

The hook is `ProtoBakeKuragePower.BeforeSideTurnEnd` on the player side and, in
the sim, `combat._player_turn`'s turn-end block beside `klee_overhaul.turn_end`
-- after the hand's own end-of-turn triggers, before `_settle_phases`, before
any enemy acts. The last clause is the printed promise and the only one a card
can tell apart.

PRICING, RE-READ AT ROUND 23 (`EB-646`). The first pricing was Breakwater 4
now / 7 at dusk and Night Watch 3 now / 5 and a Weak, priced against Read the
Field and Coral Bulwark. The Dusk trial found the FACE-UP HALF OF BOTH ROWS
DEAD: the seat never played either now-line, because the Dusk line was worth
nearly twice it for the same Energy and landed on the same swing. A choice
where one branch is never taken is not a choice.

So the Dusk line is priced to the face and TIMING is what the card sells:
Breakwater 4 now / 5 at dusk (smith 5 / 6), Night Watch 3 now / 3 and 1 Weak
at dusk (smith 5 / 5 and 1 Weak). Night Watch's Weak is untouched because it
is the whole reason to wait -- it cuts the swing it was written for rather
than the one after it -- and Breakwater's dusk half keeps one Block over its
now half for the same reason and no more.

### The two-Plan cap -- a lane rule behind a runtime toggle

"At most N Plans a morning; the rest wait, in order." DEFAULT OFF, and 0 means
unlimited: with it unset both drains are what they were. At N the front N
entries are carried out and the rest stay queued IN ORDER -- not discarded, not
re-sorted, because the whole trial is about whether queue order becomes a
decision.

It is a TRIAL and not a shipped rule, so the toggle is a runtime one on both
sides and the two are the same rule and never the same literal:
`C.KOKOMI_PLAN_CAP` is a module constant a test monkeypatches, and
`KokomiPlan.PlanCap` reads `GITS_KOKOMI_PLAN_CAP` from the environment once at
first ask. The env-var shape is the existing per-lane pattern (`GITS_LANE`,
`GITS_TELEMETRY_FEED`, `GITS_TELEMETRY_INTENT`): a lane launches the game as a
child process, so an exported variable is what a lane already has, and not
having to rebuild per arm is what the toggle exists for. It is deliberately NOT
a `lint_constant_parity` row -- comparing the two defaults by value would pin 0
against 0 and say nothing about the rule they share.

## Kokomi pool pass three -- competing faces instead of a cap (`EB-655`, R266, 2026-09-07)

THE FINDING THE PASS ANSWERS. Every two-line row in the arm printed the same
trade: a small now-line, a bigger Plan. So "write it" was the right answer on
nearly every safe turn, the queue only ever got deeper, and the rule the r23
and r24 lanes ran into -- a cap on how many Plans a morning carries out -- was
an attempt to fix the shape from the outside. [USER] retired the cap as a rule
(R266, "Agreed, let's retire it"); the toggle stays dormant and no further cap
lane is owed. What replaces it is nine changes that make the NOW-LINE worth
something the written half cannot buy, so the choice lives on the face.

THE NINE CHANGES.

1. **Feint** -- "Deal 5 damage. If a Plan was carried out this turn, deal 10
   damage instead." Plan 10; upgrade 7 / 13 / Plan 13. Sango Isshin's shape at
   Common: the morning the jellyfish delivers is the morning Feint is worth
   playing face-up, and the now-line then pays exactly what writing would have.
   The two printed numbers upgrade by different amounts, which is why
   `conditional_then_damage` exists (`tools/gen_klee_cards.py`,
   `tier0/content/upgrades.py`).
2. **Read the Field** -- "Gain 5 Block. Look at the top 2 cards of your draw
   pile; put one on the bottom." Plan 10 Block; upgrade 7 / 12. The now-line
   buys INFORMATION, which the bigger written number does not answer. The op is
   new on both engines (`scry_bottom`): the mod shows the top two on the game's
   own selection grid and moves the pick with `CardPileCmd.Add(...,
   PileType.Draw, CardPilePosition.Bottom)`; the sim has no human and bottoms
   the highest-cost card of the two, stated at `effects._op_scry_bottom` as the
   stand-in for choice it is.
3. **Riptide** -- "Deal 9 damage to ALL enemies, and 4 more to each enemy with
   a debuff." Plan 13 to ALL; upgrade 12 / 6 more / Plan 17. Undertow's rider
   widened to `all_enemies`, which cannot FOLD (one printed number would have
   to stand for a board that takes several), so it prints its two numbers
   separately and the loop adds the rider per body -- `bonus_vs_aura`'s shape
   exactly. Against a board her own Weak and Vulnerable have touched the
   now-line beats the written 13, so the kit's debuff layer decides which half
   to play.
4. **Battle Plan** -- the `energy` clause comes OFF. It paid the write back its
   own cost, so writing was free and the now-line was a strictly smaller card.
   Now: "Draw 1 card. Plan: Draw 2 cards; the next Attack you play face-up this
   turn deals 4 additional damage." Upgrade draw 2 / Plan draw 3. The rider is
   narrow on purpose -- an ATTACK, one of them, and a card WRITTEN on the
   Bake-Kurage is not a face-up play and does not take it -- so the reward is
   spent on the board rather than on more writing.

   **`EB-668`: it is damage because a discount could not be made true in both
   engines.** Pool pass three shipped this clause as "the first Attack you play
   face-up this turn costs 1 less", read at the cost seam. The mod's seam is
   `TryModifyEnergyCostInCombat`, which is handed a card and no `CardPlay`: it
   cannot ask `KokomiPlan.PlayedOnPet`, so an Attack dragged onto the pet was
   charged the discounted price in the mod while the sim charged full
   (`combat.card_cost` asks the pure `plan_aimed_at_pet`). A rider applied at
   RESOLUTION is asked at the one moment both engines know the play's target:
   `NextAttackDamagePower.ModifyDamageAdditive` there, `flat_attack_bonus`
   here, spent by `AfterCardPlayed` / `spend_attack_bonus` and gated on the
   same pet question on both sides. Per HIT, one stack always, lapsing at the
   end of the turn. `C.KOKOMI_OVERHAUL_BATTLE_PLAN_BONUS` = 4 mirrors
   `NextAttackDamagePower.Bonus`; the retired `C.…_DISCOUNT` and
   `NextAttackDiscountPower` are gone, along with tier0's cost hook. Pins:
   write an Attack after the rider (no bonus, rider kept), play one face-up
   (+4 on each hit, rider spent), a non-Attack face-up play leaves it.
5. **Nereid's Ascension** -- "At the start of your turn, the Bake-Kurage
   carries out your first Plan twice." Every Plan twice paid for writing MORE,
   which is the shape this pass undoes, and it made a deep morning the Rare's
   only line. `carry_out_times` / `CarryOutTimes` are now read for the FIRST
   entry of each drain -- morning and dusk are two drains on one turn and each
   pays its own first entry, which is the drain-local reading "the next Plan"
   already takes. Consequences pinned: Scout Ahead's forward count is entries
   and no longer entries times two, a three-Plan morning under the Rare is four
   carry-outs, and Second Wave and the Ascension can no longer meet on one
   entry at all (Second Wave reaches the entry AFTER itself; no entry is both
   first and later).
6. **Breakwater and Night Watch are WRITTEN-ONLY.** `EB-646` priced the face-up
   half to the Dusk line and the seat still never played it, so the now-line
   comes off instead: no `effects`, `plan_dusk: true`, Breakwater "Dusk Plan:
   Gain 6 Block" (upgrade 8) and Night Watch "Dusk Plan: Gain 4 Block and apply
   1 Weak" (upgrade 6 Block). The existing plan-only shape does the rest --
   `KokomiTargets.PetOnly` and the face leading with "Play on the Bake-Kurage."
   (`gen_klee_cards._plan_only_line`), so a play that is not a write is refused
   with the reason printed.
7. **Converging Tide is RETIRED.** It re-aimed a queued Plan at a chosen enemy,
   which is a decision about a queue this pass deliberately makes shallower:
   with the cap gone and the Rare paying the FIRST Plan, "which body does the
   morning land on" stopped being a question worth a card. Off the sheet, off
   `KOKOMI_OVERHAUL_POOL_IDS` (41 -> 40) and off `KokomiOverhaulRoster`;
   `redirect_queued_plans` stays registered on both engines with nothing
   spelling it, the way `cancel_all_plans_cash` did at `EB-649`. **Second
   Thoughts is unchanged.**
8. **The cap sentence is corrected.** `KokomiPlan.CapSentenceFormat` and the
   page's count note now read "Carries out at most N at the start of your turn;
   the rest wait in order." Dusk carry-outs are NOT capped -- a Dusk Plan has
   waited for nothing -- so "a turn" claimed a limit the rule does not have.
   The toggle stays, default 0, dormant.
9. **The faces are regenerated** and every one of them is under the length
   lint; the Dusk keyword tip is unchanged.

THE AUDIT. Nine arms went to the doctrine door
(`review/qa/kokomi-pass-three-2026-09-07-prompt.txt` /
`-reply.md`): eight FOLLOWS and one REQUIRES_MODIFICATION -- Feint at base 6
matched Strike's printed 1-Energy 6 damage without a carry-out and exceeded it
by 4 with one. The base is 5, and the re-read at 5
(`-reread-prompt.txt` / `-reread-reply.md`) is FOLLOWS on C6: "1 damage worse
without a carry-out and 4 better on a carry-out turn". The record is
`review/records/kokomi-pass-three-audit-2026-09-07.md`. The reply's closing
paragraph is kept as filed and is not claimed away: the arms establish
competing Energy uses on SOME safe turns and not on every one, and Battle
Plan's grant does not exclude writing an Attack under the engine the
auditor was given -- which is exactly the mod-side gap item 4 closes at
`EB-668`.

## Kokomi pool pass four -- the round-26 dead faces (`EB-679`, 2026-09-08)

THE FINDING THE PASS ANSWERS. Round 26's lanes read four rows of the pool and
none of them was worth a slot, each for a different and nameable reason. The
pass rebuilds all four; nothing else on the sheet moves, and no rule of the arm
changes.

THE FOUR CHANGES.

1. **Night Watch** -- "Dusk Plan: Apply 1 Weak to ALL enemies." No Block;
   upgrade 2 Weak. Both seats called the old face (4 Block, a Weak and the
   casket's ping for one Energy) a card that asks nothing: it paid a little of
   everything and never made the player choose. As the multi-body Weak at Dusk
   it is **Slack Water's pair** -- Slack Water wins at one body, Night Watch at
   three -- and the Dusk timing is what the Weak is bought for, because it
   lands before the swing it was written against. The upgrade takes
   `plan_power_amount` (1 -> 2), the row's one printed number.
2. **Breakwater** -- "Dusk Plan: Gain 5 Block, plus 3 for each Plan carried out
   this turn." Upgrade base 7. r26 lane 1 called it Night Watch's worse twin,
   so it stops being a flat number and becomes **the wall behind the engine**:
   the deeper the morning it followed, the more of the turn it buys back.
   NO NEW OP -- the line is a flat `block` clause plus Tide Wall's
   `block_per_plan_this_morning`, and the count is exactly the one Tide Wall,
   Well Laid and Tide Chart read (`kk_plans_this_morning` /
   `KokomiOverhaulLedger.PlansThisMorning`). **"This turn" on a Dusk Plan IS
   the morning's depth**, and by construction rather than by a filter:
   `resolve_dusk` / `ResolveDusk` deliberately leave that count alone, so this
   Dusk entry is never one of the Plans it pays for. A dusk after an empty
   morning pays the base alone, which is the honest answer to "for each".
   `plan_block` binds to the FLAT clause first (`upgrades.PLAN_DELTA_OPS`), so
   the smith raises the wall and never the rate -- a rate that smithed would
   scale with a deck the offer screen cannot see.
3. **Scout Ahead** -- "Draw 1 card. Plan: Draw 1 card for each Plan carried out
   this turn", **itself included**. Face-up half and the cost upgrade
   unchanged. The old clause counted the carry-outs still to COME, which made
   the card's whole value its POSITION: 2 written first, 0 written last. r26
   lane 1 never wrote it, because a slot that pays 0 half the time competes
   with Plans that always pay. The count is now the whole drain, read ONCE
   before the first clause runs (`_drain` / `Drain`), so the answer does not
   move with the card -- alone it draws 1, with two others 3, wherever it sits.
   Still CARRY-OUTS and not entries (`EB-501`): Nereid's Ascension carries the
   first entry of a drain out twice, so a drain under the Rare counts one more,
   the same term `resolve_all` already writes for `kk_plans_this_morning`. A
   Scout Ahead hurried by Change of Plans is a drain of one and draws 1. The op
   is RENAMED with the count it now takes, `draw_per_plan_after` ->
   `draw_per_plan_this_turn` (`Kind.DrawPerPlanThisTurn`), because an op name
   that says "after" while the rule says "this turn" is the kind of drift that
   makes two engines agree by accident. The old name is spelled by nothing.
4. **Read the Field** -- "Look at the top 3 cards of your draw pile; put one
   into your hand and the rest on the bottom. Plan: Gain 10 Block." Upgrade
   look at 4 / Plan 12. r26 lane 1 never made a decision off the old
   look-and-bury -- burying the card you like least is a choice about the card
   you did not want -- and the 5 Block beside it was a dead slot next to a Dusk
   Plan. **Selection is what the seats valued**, so the pick comes to hand and
   everything it was seen beside goes to the bottom. A NEW OP on both engines,
   `scry_take`: the mod shows the top N on the game's own selection grid, adds
   the pick with `CardPileCmd.Add(..., PileType.Hand)` and bottoms the rest in
   the order they were seen; the sim has no human and takes the LOWEST-cost
   card of the N, stated at `effects._op_scry_take` as the stand-in for choice
   it is -- `_op_scry_bottom`'s convention read the other way round, because
   the card wanted now is the one that can be paid for now. Nothing leaves the
   deck, a short pile is read short and an empty pile is a printed no-op.
   `scry_bottom` stays registered on both engines with no row spelling it, the
   way `redirect_queued_plans` did at `EB-655`.

THE ONE NEW UPGRADE KEY. `scry` moves how many cards the look SHOWS, and it
exists because pool pass four made that number worth moving: "look at 2, bury
1" is no better for showing 3, and "look at 3, TAKE 1" is. It is its own key
rather than `draw`, for `tide_draw`'s reason -- the two are different promises
and one row could print both -- and it walks the whole scry family
(`scry_take`, `scry_bottom`, `scry_discard`) so a later look-and-bury row needs
no key of its own. The codegen renders it off a `"Scry"` DynamicVar declared
only when the upgrade moves it, the Sparks idiom every other number here keeps,
and the face prints `{Scry:diff()}` so the base card never claims 3 while the
upgraded one delivers 4.

THE SCREEN. `ScryTake` is a second prompt class beside `ScryBottom` rather than
a second member on it, on that file's own terms: a selection screen is keyed on
the VERB, and taking and burying ask the player different questions. One ruled
string, merged into the base game's `cards` table by `KleeMod.InjectLocStrings`
and outside the `PROTOTYPE_CARDS` switch, because `scry_take` is a sheet verb
any character may print rather than a prototype rule.

THE DRAFTER. `scry_take` prices at `STATIC_SCRY_VALUE`, the scry family's own:
the card taken to hand is a draw and every draw op in `tier05/draft.py` is
priced at `STATIC_DRAW_VALUE = 0.0`, so what is left to pay for is the
selection over the N seen. `draw_per_plan_this_turn` keeps its zero unchanged
-- `EB-679` moved WHICH carry-outs it counts, not the refusal to guess how deep
a morning a deck banks.

NOT MEASURED, NOT QUOTABLE. Prototype numbers, D by the ladder (R215 B): no
slate, no stamp and no re-baseline. What the pass owes is a round that draws
the four rows.

## Kokomi pool pass five -- the phase of the Dusk lines (`EB-685`, 2026-09-08)

THE FINDING THE PASS ANSWERS. Round 27 read pool pass four's own Dusk rows and
found two of them out of phase with the moment they land on. Breakwater's
clause counted the morning that had already been drained, which a Plan written
today can never be part of: both seats counted 0 and were paid 5 on four plays
out of four. Slack Water's Weak was still a MORNING Plan, so it arrived after
the swing it was written against -- the complaint every seat has made since
round 25. Both are timing defects rather than numbers, and the pass fixes them
by moving WHEN each clause looks, not how much it pays.

THE FOUR CHANGES.

1. **Breakwater** -- "Dusk Plan: Gain 5 Block, plus 3 for each Plan the
   Bake-Kurage is holding." Upgrade base 7, the shape unchanged. THE COUNT IS
   THE QUEUE AT DUSK -- the Plans written this turn and still waiting for the
   next morning -- so the wall rises on the turn the ENGINE IS WRITTEN rather
   than on the turn after a deep morning. That is the card the r26 reading
   asked for, one drain over: what it pays for is the queue standing behind
   it, which is the only thing a Dusk Plan can see that a morning Plan cannot.
   A NEW OP on both engines, `block_per_plan_held` /
   `KokomiPlan.Kind.BlockPerPlanHeld`, because the count really is a different
   fact from Tide Wall's: `kk_plans_this_morning` is the depth of a drain that
   has finished and `len(state.kk_plan_queue)` is what is still owed. Pass four
   spelled the clause with Tide Wall's op precisely to avoid minting one, and
   that economy is what produced the zero.
   **THE TWO EXCLUSIONS ARE BY CONSTRUCTION AND NOT BY A FILTER**, the
   discipline `resolve_all` already keeps: `resolve_dusk` / `ResolveDusk` take
   every dusk entry OFF the queue before the first clause runs, so this entry
   is never one of the Plans it pays for, and neither is a second Dusk Plan
   written the same turn -- a Dusk sibling is not "waiting for the next
   morning" either, which is the sentence the face says. A Plan hurried out by
   Change of Plans earlier in the turn has already left the queue and does not
   count, which is the trade the two tempo cards make with each other.
   THE COUNT IS READ LIVE, at the moment the entry resolves, rather than once
   at the drain the way `drain_plans` is. Order-independence was pass four's
   argument for Scout Ahead and it does not apply here: the face says "is
   holding", a present tense about a queue, and the only thing that can move
   the number mid-drain is a Dusk Plan that writes another Plan -- which the
   player watched happen. `plan_block` still binds to the FLAT clause first
   (`upgrades.PLAN_DELTA_OPS`), so the smith raises the wall and never the
   rate.
2. **Slack Water** -- "Deal 4 damage. Apply 1 Weak. Dusk Plan: Apply 1 Weak to
   ALL enemies." The face-up half is untouched; only the Plan's phase moves.
   At Dusk the multi-body Weak lands before the enemy acts, which is what the
   Weak is bought for -- a debuff that arrives the morning after is a debuff
   the player paid for and did not get to use.
   **IT IS THE SURFACE'S FIRST ROW WITH BOTH A NOW-LINE AND A DUSK PLAN, AND
   IT NEEDED NO EXTENSION.** `plan_dusk:` was already a fact about the row's
   PLAN LINE rather than about its whole face -- `loader._validate_plan_dusk`
   asks only that there BE a `plan:` list, and `gen_klee_cards` appends
   `dusk: true` to the one `KokomiPlan.Schedule` call it emits, which for a
   two-half row sits inside the `PlayedOnPet` branch it already wrote. The
   generated card picked up `ArmKeywordTips.ForDusk` and
   `KokomiTargets.PetOrEnemy` on its own. Nothing in either engine was widened;
   the row is the first one to exercise a seam both sides already had.
3. **Night Watch** -- RETIRED, and the row leaves the sheet, the pool tuple and
   `KokomiOverhaulRoster.Slice()` under R213 B's deletion rule. It lost every
   draft comparison in r27, and Slack Water's Dusk half is now its job: the
   multi-body Weak before the swing is exactly what pass four rebuilt Night
   Watch to be, and a pool does not need the same card twice when one of them
   also hits. It spelled NO op of its own -- its clause was the shared
   `apply_power` -- so nothing stays registered behind it the way
   `redirect_queued_plans`, `cancel_all_plans_cash` and `scry_bottom` do. The
   pool is 39.
4. **Scout Ahead** -- face wording only, no behaviour: "Plan: Draw 1 card for
   each Plan carried out this turn, this one included, in any order." Pass four
   made both of those true and printed neither, and a seat cannot read a count
   it has to infer. The two added clauses are the two questions the old face
   left open -- does it count itself, and does its position matter -- answered
   on the card at 99 characters against the 120 ceiling.

THE DRAFTER. `block_per_plan_held` prices exactly as
`block_per_plan_this_morning` does, its printed Block for ONE held Plan, and
the equality is the point: `EB-685` moved WHICH Plans the clause counts and not
the refusal to guess how many there will be. Plan density is still a deck fact
an offer screen cannot read.

NOT MEASURED, NOT QUOTABLE. Prototype numbers, D by the ladder (R215 B): no
slate, no stamp and no re-baseline. What the pass owes is a round that draws
Breakwater and Slack Water on the same lane.

## Passes six and seven withdrawn -- the starter basics stay the base game's (2026-09-08)

POOL PASS SIX (`EB-703`) AND POOL PASS SEVEN (`EB-711`) GAVE KOKOMI HER OWN
BASICS: `proto_kk_strike`, a Plan line printed on the Strike so no opening hand
could be Plan-less, and `proto_kk_defend`, 5 Block plus 2 while the Bake-Kurage
was holding a Plan, so the last unwritable card asked its question by ordering.
Both were swapped into her starter in both engines, and at the `EB-351` relic
seam.

BOTH ARE WITHDRAWN, on the day they landed, under [USER]'s rule: A CHARACTER'S
STARTER BASICS ARE NEVER CHANGED -- "they are supposed to suck". That is a
rule about the kit and not a reading of these two rows, so no measurement
settles it and no later pass reopens it by finding a better basic. Her starter
is four base Strikes and four base Defends again -- `StrikeSilent` /
`DefendSilent` in the mod, `strike` / `defend` in the sim -- which is R242's
text unamended. The findings the two passes answered are unanswered, and the
answer has to be a card the deck can DRAW rather than one it opens with.

WHAT WAS REMOVED: both sheet rows, `ProtoKkStrike` and `ProtoKkDefend`, the
starter and `StarterStrike` / `StarterDefend` swaps, `KokomiPoolPassSixTests`
and `KokomiPoolPassSevenTests`, the tier0 cases for the two rows, and the two
pieces that existed only for the Defend's face --
`KokomiPlan.PlanHeldBlockVar` and `gen_klee_cards.plan_held_block_rider`.

WHAT WAS KEPT, because it is general and printed by no row: the `basic_tag:`
sheet field with its loader and codegen validators, the `applies_element:
false` codegen path (`CharacterProfile.damage_applies_element` reading a
declared false, `declares_no_element`, and the mixed-declaration blocker), and
the `plan_held` predicate in both engines' registries with its
`_ENGINE_LIVE_PREDICATES` registration -- the `EB-144` pilot fix, which is
`EB-712`'s standing evidence.

## R267 (2026-09-08): Slack Water's Plan returns to the morning, Scout Ahead's clause returns to its position

Two moves are reversed; each puts a row back to its pre-pass shape.

SLACK WATER'S PLAN HALF IS A MORNING LINE AGAIN. Pool pass five (`EB-685`)
moved it to Dusk on the reading that the morning Weak arrived after the swing
it was written against. The Kokomi brief, line 75, names the next-morning Weak
as the kit's TURN-ONE DECISION -- one Weak on the front enemy now, or one on
every body tomorrow -- and a starter card is [USER]'s, not a default's. So the
move was a redesign taken as a D pick and it is reversed: the row is byte-equal
to its pre-pass-five form, and Breakwater is the surface's only Dusk row again.
The `plan_dusk` machinery stays exactly as pass five built it.

The pool's before-the-swing multi-body Weak is now A POOL QUESTION WITH NO ROW.
Night Watch stays retired -- pass five's retirement was on its own merits, it
lost every draft comparison in r27, and nothing here reopens it -- so if the
arm wants that line it will be a new card rather than a phase moved onto a
starter.

SCOUT AHEAD COUNTS THE PLANS THAT FOLLOW IT AGAIN. Pool pass four (`EB-679`)
replaced the positional clause with a whole-morning count because round 26's
lane never wrote the card: a row worth 2 written first and 0 written last
competed for its slot with Plans that always paid. THAT IS ONE SEAT AVOIDING
THE 0-PAYOUT SLOT, which is the ordering decision working, not a defect in it.
Round 28's praise for the recounted card -- "always written last" -- rested on
lane 2 believing position still mattered, so it is not evidence for the recount
either way. The clause returns in both engines: first of three draws 2, last
draws 0, alone draws 0, and the face says "later" so a seat can read the rule
off the card. The next Kokomi seat round reads it.

Two details. NEREID'S ASCENSION ADDS NOTHING to the count, and that follows
from `EB-655` rather than being chosen here: the Rare carries out the FIRST
entry of a drain and no other, and an entry is never the first when something
follows it, so every later entry is exactly one carry-out. A Scout Ahead
written first is itself carried out twice and pays its 2 each time; the test
pins both halves. And `draw_per_plan_this_turn`, pass four's whole-drain
spelling, is KEPT REGISTERED AND RESOLVED on both engines with no row spelling
it, the standing `scry_bottom` and `redirect_queued_plans` already have -- the
clause works if a sheet reaches for it, without a build.

## Scout Ahead counts later CARRY-OUTS, paid as they happen (`EB-718`, 2026-09-08)

The 2026-09-08 review queued Scout Ahead, then Second Wave, then Battle Plan,
and Scout Ahead drew 2. Second Wave carries the Plan behind it out TWICE, so
what followed was three carry-outs -- Second Wave's own, Battle Plan's two.

The face says "each later Plan CARRIED OUT with this one", and both engines
counted the ENTRIES still queued (`len(due) - index - 1`) -- the one number a
rider can move and an entry count cannot see. It contradicted the register too:
every reader counts carry-outs (`EB-501`), and every per-Plan clause counts a
doubled carry-out twice (`EB-709`). The R267 comments called the omission
deliberate, which made a wrong number a documented one; they are gone.

The clause draws nothing at its own carry-out now. It ARMS a counter for the
rest of THAT drain, and every carry-out that follows draws the armed rate; two
armed Scout Aheads draw 2 apiece. The counter is a local of the drain loop, so
a fight that ends mid-morning draws nothing more and a morning's arming never
reaches the evening. Last of three draws 0, first draws 2, first of {Scout,
Second Wave, Battle Plan} draws 3, Change of Plans is a drain of one and draws
0. NEREID'S ASCENSION IS THE CONSEQUENCE and not a second rule: the Rare
carries the first entry out twice, so a Scout Ahead written first arms twice
and draws 2 per later carry-out. Both suites pin it. Its own beat prints no
number -- no honest figure exists at the clause -- and the cards ride the later
beats by name through `KokomiPlan.NoteRider`.

## Furina, the Stage — batch one (`EB-723`, R269 2026-09-08)

The design is `review/active/furina-stage-brief-2026-09-08.md`, whose sec.12
prints the seventeen faces and whose sec.3 states the rules they play by. The
faces below are the brief's, word for word; nothing here is a design act, and
the names are provisional and cosmetic (sec.10 default 7, R179).

**What left first.** The reframe's eleven `proto_fr_` rows are gone, under
R213 B's deletion rule: the brief's sec.2 retires that arm by name, so its rows
left rather than sitting commented out. Four keyword tips went with them
(`Deploy`, `Evoke`, `Drain`), the `drain_fanfare` machinery stayed one more
commit with the arm's C#, and `furina_reframe.POOL_SUBS` and `STARTER_SUBS` are
empty maps rather than maps naming ids no sheet defines. `Encore` survived the
cut and is now a rider rather than an arm keyword: the meter is shipped
machinery, the word is printed on the Neow screen before a meter exists, and
every Furina row the Stage does not swap still carries it (`EB-407` stands).

**The three starters** swap in at `loader._starter_ids` for her three KIT
starters — `aria_of_recompense`, `salon_debut` and `an_invitation`. The seven
basics do not move and never will: three Soloist's Solicitation, three Stage
Presence and Regal Bearing are the base game's, and an arm does not touch a
basic. They are `basic` rarity, so `rewards.character_pool` cannot offer one
whatever any map says.

**The fourteen offerable rows** swap in at `loader._pool_substitutions`, one
for one at the same rarity, so the offer odds do not move. Which shipped row
each replaced is a D default disclosed on `furina_stage.POOL_SUBS`: the same
rarity always, the same type and cost where her sheet had one to spare, and
otherwise the nearest plain row of that rarity. The three named summons land on
the three shipped rows of the SAME NAME, which is the cleanest swap on the
sheet.

**Two titles collide with a shipped Furina card on purpose.** *Standing
Ovation* and *Let the People Rejoice* are cards this kit is a rewrite of, and
the arm swaps a shipped row out at the same door, so no run can hold both. The
reframe's own Rare took the same liberty for the same reason.

**`Salon Début` became `Take the Stage` (live look 8b, 2026-09-16).** The
paragraph above is the rule and this is the pair that broke it. The shipped
`Salon Début` and the Stage's were both live ids on `0.2.3480+proto` and both
printed the same title — `Salon Début (1)` / `Salon Début (2)` with one of
each in hand — held apart only by `EB-736`'s OFFER filter. An offer filter is
not a rule about a hand: a `give_card`, a Conscript or any later route puts a
shipped Salon row beside the Stage's and `EB-739`'s defect recurs with this
pair. So the Stage's row is renamed, which is exactly the repair `EB-739`
made to Standing Ovation, and an E default under R179: the brief's own card
table says "Names are provisional", the id (`proto_fs_salon_debut`) does not
move, and `lint_unique_names` is the proof it is cosmetic. **Not "Curtain
Up"**, the first name suggested: `Curtain Rise` is the card directly beneath
it in the same three-card starter kit, and two starters called Curtain Rise
and Curtain Up would be the legibility defect this rename exists to remove,
one word over. *Take the Stage* is the brief's own phrase for what the card
does — a performer joins the stage — and shares no word with a live title.

**Why the two-branch faces carry two `{IfUpgraded:show:…}` holes.** Every Spend
rider is printed as `conditional {if: stage_occupied, then: [stage_spend,
<big>], else: [<base>]}`, which is rule 8's two sentences as two branches. A
`conditional_damage` / `conditional_block` delta moves BOTH branches, and the
emitter only rewrites the literal it finds in the `then` arm — so a face
written with a bare base number would print 7 while the upgraded card dealt 10.
The base number carries its own hole, authored on the row. **This is a codegen
limitation worth a row of its own:** the emitter should hole every branch a
whole-card delta moves, and today it holes one.

**The three upgrades that are not numbers.** *Final Bow* drops its Exhaust
(so did *Understudy*, until it left the pool on 2026-09-28); *Salon Début*,
the named summons (three until *Gentilhomme Usher* left with it), *Rising Applause*,
*Ousia Surge*, *Pneuma Refrain*, *Bis!* and the Rare take a cost. Neither shows
in the body, which is why the blind-play Smith preview answers those rows with
"its upgrade changes nothing this face prints" rather than a rendered face —
the reason is a fact about the card, which is what `EB-551` asked of it.

**The seven keyword tips** are the brief's own list: `Spend`, `Fanfare`,
`Raise`, `Bow`, `lead performer`, `back performer`, `Rotate`. Each carries the
half of its rule a player cannot infer — rule 8's "fires in full even if the
bar is short" (the whole Expend deck), rule 6's damage order (the reason a bar
matters), rule 5's "with one performer that is the lead", and the difference
between a bow and a death, which is turn one's wager. Two are two words because
what they carry is a rule about WHICH SEAT. `Fanfare` collides by spelling with
the shipped meter and not by meaning; nothing on the blind-play page can tell
them apart today, and the round packet owes that finding.

## Furina, the Stage — batch two (R276 pick 3, 2026-09-23)

Fifteen rows designed by the main session on the rules R276's picks 1 and 2
set: the lead performer is the shield (it absorbs and regenerates), the back
performer is the bank (Raise fills it; Spend and the readers draw from it), and
a Spend needs its full price. The faces are the design's, word for word, save
two base-game spellings: *A Rapt Audience* prints "rounded up" between commas
rather than in parentheses, and it states its upgrade as an
`{IfUpgraded:show:...}` swap ("the" Fanfare it lost, for "half the").

**Which shipped row each replaces** is a D default on batch one's terms: the
same rarity always, the same type and cost where the sheet had one, and every
one of the fifteen is a row the arm's `EB-736` text filter already drops from
the game's offer. So the mod's appended rows and the sim's one-for-one
`furina_stage.POOL_SUBS` name the same fifteen, and no card a Stage run could
be offered today leaves the offer.

**New machinery, both engines**: the `stage_empty` predicate, the
`stage_count` count, three ops (`stage_step_forward`, `stage_perform_all`,
`stage_spend_back_all`), `stage_raise`'s `seat: lead | all`, the `stage_raise`
upgrade key, `conditional_then_damage` on a Spend mode (Quick Cue's 3/8 to
4/10), and five powers (`fs_full_house`, `fs_thunderous_applause`,
`fs_rapt_audience`, `fs_five_century_act`, `fs_arkhe_alignment`) whose rules
live in `FurinaStage` beside the rule each bends.

## Furina, the Stage — the Guest Cast (2026-09-25)

Eight Guest Star Skills, `proto_fs_guest_star_<name>`, as ruled in
`review/active/furina-guest-batch-2026-09-25.md` that evening and amended by
two rulings after it: no guest cap ("why not just let the Stage be filled
with guest stars if the player wants?"), and one of each guest ("only one
Neuvillette allowed - repeats trigger a Bow and then resummon them, carrying
over unused Fanfare"). The faces, rarities, costs and arrival Fanfare are the
build table's; each guest's act lives on its tip and its badge, not on the
face.

**Which shipped row each replaces** is a D default on batch two's terms: a
same-rarity shipped Skill the `EB-736` text filter already drops. Rares:
Neuvillette for `reginas_mercy`, Clorinde for `thunderous_ovation`, Navia for
`encore_performance`. Uncommons: Chevreuse for `audience_participation`,
Wriothesley for `deep_breath`, Sigewinne for `standing_room_only`, Charlotte
for `limelight`, Lynette for `take_it_from_the_top`.

**New machinery, both engines**: the `stage_guest` op and its upgrade key
(`stage_guest: +N`, what the guest arrives with), eight performers, their acts
(`FurinaStageLedger.ActFanfare` / `furina_stage.guest_fanfare` for the
payments and gifts, `FurinaStage.GuestAct` / `_guest_act` for the board), the
per-guest loss count Wriothesley reads, and the end-of-turn forecast.

## Furina, the Stage — Sold Out, the fourth seat (2026-09-26)

`proto_fs_sold_out`, family 7 of `review/ruled/furina-supporting-pool-2026-09-26.md`
(ruled that day, all four defaults; pick 2 (a) keeps both rule-bending Rares). A
Rare Power, cost 2 (1 upgraded): "Your stage has a fourth seat." Built ahead of
the other 28 because it bends rule 1, and every rule that meets a full stage had
to learn to count. The face is the paper's, word for word; a second copy is a
dead Power, and the face does not say so: the paper's face is kept as
written.

**What it means**, as the build spec read the brief's sec.3: the stage holds
four for the rest of the combat -- front, two middles, back. "Back performer"
is still the back-most and "front" the lead, so Raise, Spend and the damage
order need nothing. Both middles fade (rule 12 already fades everyone behind
the front). Rule 3's recast meets a full stage at four, not three, and
Wriothesley's front-join on a full four-stage Bows the back performer. **Full
House**'s face moves with it, from "If all three seats are filled" to "If every
seat is filled", so with Sold Out it needs four.

**How it is built**: one number, `FurinaStageLaw.SoldOutSeats` / `furina_stage.
SOLD_OUT_SEATS` (4, parity-mirrored), and one reader per engine:
`FurinaStageLedger.Capacity` (read live off her powers through
`FurinaStage.CapacityOf`; the forecast's clone carries a copy) and
`furina_stage.capacity`. Every `IsFull` and `len(seats) vs SEATS` reads it. The
power is `SoldOutPower` / `fs_sold_out`; The Stage badge's in-combat line reads
the live count.

**Which shipped row it replaces** is a D default on the Guest Cast's terms: a
same-rarity shipped Power the `EB-736` text filter already drops, and the only
one left at the same cost: `unheard_confession` (2 Power for 2 Power). The
other three Rare Powers the paper adds (Eternal Applause, One-Woman Show,
Regina of All Waters) have three dropped shipped Rare Powers left to replace:
`the_sea_is_my_stage`, `star_of_the_show` and `rapturous_applause`, all cost 1.

## Furina, the Stage — the supporting pool, 28 rows (2026-09-26)

The other 28 cards of `review/ruled/furina-supporting-pool-2026-09-26.md`
(ruled that day with all four defaults, swept before the build). The faces are
the paper's tables as swept, with the build's own wording where a lint or a
title forced it: **Showstopper** is *Bring the House Down* and **Undertow** is
*Groundswell* (title clashes with Furina's shipped `showstopper` and Kokomi's
arm Undertow); **Stage Whisper** reads "Move up to 3 ... It keeps at least 1",
so it never empties, and never Bows, the back (a 0-cost Bow would loop with
Thunderous Applause and A Five-Century Act); **Soliloquy** says "3 additional
damage", text-conventions rule 8. The two Guest Stars follow the Guest Cast's
frame: the face says what arrives, the act lives on the performer's tip and
badge.

**Which shipped row each replaces** is a D default on the earlier batches'
terms (the same rarity always, the type and cost where one was free), each a
row the `EB-736` text filter already drops. Commons: Plot Twist for
`shared_billing`, Stage Whisper for `ebb_and_flow`, Cheered On for
`dinner_service`, Spirited Aria for `macaron_break`, Bubble Aria for
`casting_call`. Uncommons: Revolving Stage for `grand_salon`, Oratrice's
Verdict for `curtain_cue`, Season Tickets for `top_billing`, Star Billing for
`supporting_cast`, Held Applause for `directors_cut`, Echoing Hall for
`pit_orchestra`, Intermission for `tempo_change`, Counterclaim for
`poised_riposte`, Da Capo for `florid_cadenza`, Groundswell for
`waters_embrace`, Tide of Applause for `leading_role`, Soliloquy for
`hearts_swelling`, Dual Nature for `curtain_up`. Rares: Lyney for
`rain_of_roses`, Escoffier for `the_final_verdict`, Eternal Applause for
`rapturous_applause`, Bring the House Down for `showstopper`, Grand Finale for
`flood_of_emotion`, Gala Premiere for `grand_gala`, Grand Deluge for
`high_tide`, Regina of All Waters for `the_sea_is_my_stage`, One-Woman Show for
`star_of_the_show`. `overflowing_hospitality` is the one dropped Uncommon left.

**Solo Verse replaces nothing.** Her sheet has only five Commons the filter
drops that no batch had replaced, and this batch has six. Replacing a Common
the arm still offers would take a card out of the pool and miss the paper's
49 + 29 = 78, so the arm APPENDS it: the mod's offer was always an append
(`FurinaStageRoster.SwapOfferedRows`), and the sim gains the one seam it
lacked, `furina_stage.POOL_ADDS`, read by `loader.pool_additions` beside
`pool_substitutions` and filed at its own rarity by
`tier05.rewards.character_pool`. Empty with the flag off.

**New machinery, both engines**: eight ops (`stage_reverse`,
`stage_whisper`, `stage_hold_fade`, `stage_intermission`,
`stage_spend_front_all`, `stage_grand_finale`, `stage_verdict`,
`stage_dual_nature`); `stage_summon`'s `fanfare:` (Gala Premiere's 3, and on a
full stage the recast's own arrival); `stage_raise` inside a branch
(Groundswell, Grand Deluge); the `stage_front_hit` predicate (Counterclaim) and
the `stage_bows` count (Da Capo); upgrade keys `stage_whisper` and
`stage_intermission`; two guests (Lyney, Escoffier) on the Guest Cast's
machinery; and nine powers, each a switch its rule asks about
(`FurinaStageSupporting.cs`, sim twin in `furina_stage.py`).

**The build's readings of the paper**, each a literal reading flagged in the
build PR rather than a design choice: Revolving Stage runs AFTER rule 4's
regen, so the regen goes to the old lead; the turn-start order is One-Woman
Show (on the stage the turn found), Revolving Stage, Season Tickets, Regina.
Oratrice's Verdict lasts until the end-of-turn sweep and reaches every random
pick an act or a Bow makes, Lynette's aura pool included. Echoing Hall is a
move (copies do not echo twice); Eternal Applause's copies do not stack
further; Revolving Stage moves the back forward once per copy. Grand Finale's
Bow is taken in place: a gift "to each other performer" or "behind her" skips
the giver, and Wriothesley's count resets. Dual Nature does not stack on an
Arkhe Alignment that chose the same half this turn (the larger multiple
stands). Star Billing draws on a Guest Star card's arrival only, a second
copy's recast included, not on A Five-Century Act's return. Soliloquy is read
per hit in the mod and once per play in the sim.

**The seat round's text fixes (2026-09-26, 0.2.3859+proto).** Bring the House
Down's "Spend" is no longer golded: the golded word hung the Spend tip ("Pay
Fanfare from your back performer") on the one card that spends the FRONT, and
the face names its seat itself; it is no "Spend N" mode (lane 1). The words
on the face are unchanged. Star Billing's face names Guest Star, so it now
carries that tip (`gen_klee_cards.stage_guest_tip_calls`; lanes 1 and 3).

**Stage Whisper, second rework (2026-09-26 seat round).** A second seat named
it NEVER AGAIN: "the back performer is nearly always at 1-2 Fanfare after
fading and Spends, so it moves nothing". The designer's new face: cost 1
(upgrade cost 0), "Your other performers give all but 1 of their Fanfare to
your front performer. Draw 1 card." It gathers the whole stage into the
shield. Each performer behind the front gives `Fanfare - 1`, so it never
empties anyone and no one Bows, which keeps the loop with Thunderous Applause
and A Five-Century Act closed; with one performer it only draws. The op keeps
its name and loses its `amount`, and the `stage_whisper` upgrade key is
retired. **The upgrade became draw 2 at cost 1 (2026-09-28):** upgraded at
cost 0 it was a 0-cost draw-1 Common, which LAW's cycling rule gates to
Uncommon+ (GPT review 2026-09-28).

**The Hydro rides the hit (2026-09-26 seat round, act 2 lane 2).** Quick
Cue's Spend mode hit a Pyro body, Vaporize was listed and the 8 landed at face
value: the row dealt a plain hit and then applied Hydro, so the reaction fired
on the application. Tidal Flourish's and Quick Cue's Spend modes, Bubble Aria
and Grand Deluge now put `applies_element: true` on the hit (Klee's
mechanism) and drop the `apply_aura`. Grand Deluge's one hit is its whole
damage, so it takes the card-level `IElementalCard`. Quick Cue and Tidal
Flourish also hit in their plain modes, which stay plain, so the mod carries
the element on the one `DamageCmd` (`HitElement.Carry`, read first by
`CatalystCadence.PrintedElement`); the sim has always answered per effect.
Bubble Aria's `element_hits: 1` carries it on the FIRST hit only, so a Pyro
body is Vaporized by hit one and hit two lands plain, the end state the old
"then apply Hydro" gave. The faces are unchanged.

## Furina, the Stage — the starter ruling (2026-09-28)

[USER]: "Typically we'd include 4 strikes, 4 defends and 2 actually useful
cards that teach the character's core mechanics - this seems like an
unnecessary power spike." Then: "I agree with keeping Curtain Raise and Rising
Applause." "We should really just replace Soloist's Solicitation and Stage
Presence with the basic strike and defend." And: "The characters' kits should
all use basic Strike and Defend."

The Stage starter is the base game's Strike x4 and Defend x4 (Silent's pair,
which `FurinaCardPool`'s borrowed frame matches, as Kokomi's arm does) plus
**Curtain Rise** and **Rising Applause** (`FurinaStageRoster.StartingDeck`,
sim `furina_stage.STARTER_IDS`). The base pair has no row on this sheet. Large
Capsule, Fasten's tip and transforms of the base pair route through
`ArmStarterBasics` / `ArmTransformPool` under the arm, as for Klee and Kokomi.

- **`proto_fs_salon_debut`** (Take the Stage): basic to **Common**, now
  offered. "Summon a random performer with 3 Fanfare. Draw 1 card.", cost 1,
  upgrade cost -1 as before. TENTATIVE: "'Become Common with a stronger
  effect' is fine as a tentative proposal, and then we can do an audit of the
  pool as part of the balance pass to see if we still want it." Audited in
  the balance pass's dedupe. The random summon arrives holding 3 through the
  same `fanfare:` argument Gala Premiere's named summons use (C#
  `FurinaStage.Summon`, sim `_op_stage_summon`), on a full stage as the
  recast's arrival.
- **`proto_fs_regal_bearing`** (Regal Bearing): new Common, cost 1, Gain 5
  Block, apply 1 Weak to the target; upgraded 6 Block, 2 Weak. [USER]: "5
  block, 1 weak" upgraded to "6 block, 2 weak". Wears the shipped portrait
  (`art_of: regal_bearing`). The shipped basic (Block 3, Weak 1) does not move.

Both `replaces:` a shipped STARTER basic, which is never offered, so a
same-rarity pool swap cannot express them: they are appended to the offer
(`furina_stage.PROMOTED_STARTERS`, read by `loader._pool_additions` and
`declared_starter_substitutions`). The pool goes from 78 to 80.

## Pool pass two: six Spark sinks on Regent's ladder (`EB-732`, R270, 2026-09-08)

R270 ruled the round-25 pick at option 1: Spark is a currency, its income
stays, and the pool gets things to buy with it, Regent's Stars the comparison
(`docs/current/research/regent-stars-economy.md`). The record is
`review/records/klee-pool-pass-two-2026-09-08.md`; the doctrine reply is
`review/qa/klee-pass-two-2026-09-08-reply.md` (six FOLLOWS; Blast Goggles, an
on-spend Block Power, withdrawn on C5 because a payoff spends nothing).

THE ROWS. Blast Shield (Uncommon, 0 Energy, 2 Sparks: 6 Block, returns to
hand; upgrade 8); Return to Sender (Uncommon, 1 Energy, 2 Sparks: 8 Block, and
this turn the damage that Block absorbs is placed on the attacker as a Bomb;
upgrade 11); Bottomless Bag (Common, 0 Energy, 2 Sparks: draw 2; upgrade 3);
Once More! (Uncommon, 0 Energy, 3 Sparks: the last Set off card you played
returns from the discard to your hand; upgrade 2 Sparks); Sparkling Burst
(Uncommon, 0 Energy, 3 Sparks: 1 Energy, 1 more if a Bomb went off this turn,
not Exhaust; upgrade 2 Sparks); Blazing Delight (Rare Power, 2 Energy, 5
Sparks: at the start of your turn gain 1 Energy and draw 1 card; upgrade 4
Sparks). Prices are Regent's tiers: 2 for the Commons and the repeatable
Uncommon, 3 for the median Uncommons, 5 for the Rare. No income figure moved.

THE SEAMS. Two new ops, `return_to_hand` and `return_last_set_off`, in
`klee_overhaul.OVERHAUL_OPS`, `effects.OPS`, the drafter's standing zero and
`gen_klee_cards`' op tables; `return_to_hand` is emitted as a class member
(the card's own result-pile override, `PileType.Hand`), not a statement, and
the codegen refuses it nested or repeated. Two new powers, `ko_return_to_sender`
/ `ReturnToSenderPower` and `ko_blazing_delight` / `BlazingDelightPower`.
Return to Sender rides the block-absorbed seam Diona's Icy Paws and Thoma's
Blazing Barrier already use (`effects.companion_overhaul_block_absorbed` gained
a Klee leg gated on `C.KLEE_OVERHAUL`; `CompanionOverhaulIncomingHit` the same
reader gated on `KleeOverhaul.Enabled`); the Bomb it places is an ordinary
plant and mints nothing. Once More! reads a per-combat `last Set off card`
noted where the `set_off` op RESOLVES (`effects._op_set_off`; the three C#
doors), which for every row on the surface is the card that was played. Blazing
Delight pays in the `AfterPlayerTurnStart` co-tenancy Grounded uses, after the
draw and the Energy reset. Bottomless Bag's face is spelled with Countdown's
`{Cards:diff()}` variable so the upgrade shows on the card (`EB-283`).

THE COUNT. The pool is 51: 22 Commons, 20 Uncommons, 9 Rares. THE NINTH RARE
is one past the brief's sec.7.4 count of eight and is recorded rather than
absorbed: a combat-long Energy engine is not an Uncommon, the brief's table
now says nine under R270, and `test_the_pool_keeps_the_packets_rarity_split`
pins 22 / 20 / 9 with the overrun in its docstring. Both engines pin every row
(`tier0/tests/test_klee_overhaul.py`; `KleeOverhaulPoolPassTwoTests`, 19
cases). Both new powers borrow an existing icon; art is owed at acceptance.

NOT MEASURED, NOT QUOTABLE. Prototype numbers, D by the ladder (R215 B). What
the pass owes is round 26: a natural lane that meets the rows at the draft and
an assembled lane built on them, read against round 25's figures.


## R271 stage one (`EB-749`, 2026-09-14)

The ruled consolidation's first build: two cuts, one redesign and three
repairs. `review/ruled/klee-pool-consolidation-2026-09-09.md` sec.4, sec.5 and
sec.8 are the spec and every number on a face below is its stated D default.

**`proto_ko_booby_trap` -- Powder Charge's shape, a Mine in its body.**
Powder Charge was Pop! with a price, and the SHAPE the seats praised was the
0-Energy placer bought from the bank. That shape stays and the body becomes the
pool's only single-target Mine: Common Skill, 0 Energy, 1 Spark, "Place a Mine
5", upgrade `bomb_size: +3` -- Powder Charge's own delta, unchanged. No new
rule and no second Mine implementation: a Mine is a Bomb that also goes off
when its own enemy attacks Klee, before the hit, and this row is Mine Toss's
`plant_bomb ... mine: true` with `target: enemy` instead of `all_enemies`. The
decision it asks is which enemy is about to swing.

**`proto_ko_tinder_toss` -- the merge, and the end of the random target.**
"Set off ALL enemies. Deal 3 damage to ALL enemies.", Common Attack, 0 Energy,
1 Spark, upgrade `damage: +2`. It takes the brief's shape and Fireworks Show's
slot. The ORDER is the two ops' order and is part of the rule: `set_off` on
every enemy resolves first, then the 3 lands on all of them. The price is a D
default at 1 Spark because the row replaces the pool's 1-Spark multi-target
card; Rapid Fire keeps the repeated-Set-off line, and the random-target
complaint round 11 raised through `EB-595` is gone.

**`proto_ko_grounded` -- the quiet-turn rule, third condition.**
"At the start of your turn, if you played no Set off card last turn, gain 4
Block and 1 Spark." The card has now had three conditions and the history is
the point: "none of your Bombs went off last turn" was a trap, because Mines
fire on the ENEMY's beat and the card paid once in five fights; `EB-516`'s "if
you have a Bomb on the field" was payable but paid a Cook deck for a board it
was holding anyway. R271 keys it to the player's own ACT. The two interactions
the ruling states are excepted BY CONSTRUCTION and not by a clause, because
"Set off card" is counted at the one site a card-facing Set off resolves
(`klee_overhaul.note_set_off_card`, `KleeOverhaulLedger.NoteSetOffCardPlayed`):
a Mine answering an attack passes no card there, and Sparks 'n' Splash is a
Power's end-of-turn hit that never reaches it. So a Cook deck's Mines no longer
switch Grounded off, and a turn on which only Splash fired is still paid.

KAEYA'S COLD-BLOODED STRIKE IS RE-WORDED, AS TEXT AND NOT AS A RULE. That
companion stand-in printed "This turn, Grounded counts a Bomb as on the field",
a condition Grounded no longer has; it now prints "Next turn, Grounded pays
even if you played a Set off card." Nothing in the effect moved -- the buff is
applied when the card resolves and spent at the next `AfterPlayerTurnStart`,
where it forces the payout whatever Grounded's condition says -- so the
sentence is the words catching up with the code for the second time (`EB-576`
did it for `EB-516`). It also stops saying "this turn" about a turn boundary
that has not arrived yet, which was true of the old wording too.

**`proto_ko_return_to_sender` -- the cap the face already claimed.**
The conversion of absorbed damage into a Bomb on the attacker is capped at the
Block the card granted -- 8, or 11 upgraded, and whatever a Block modifier made
of that grant -- as ONE allowance spent across every hit of the turn, never an
independent cap per hit. The mark already carried the allowance (it is clamped
to standing Block on the way in and shrunk by whatever each hit absorbed), so
the repair is the PLANT reading the mark: `min(blocked, mark)` in both engines.
An 8-mark eating a 20 plants 8 and is spent; two hits of 6 into the same
8-mark plant 6 and then 2. The face keeps "this Block" and is now true.

## R276 -- the Mines batch and slice two together, and Hexerei becomes Companion (2026-09-23)

`review/ruled/klee-review-2026-09-23.md`, all three picks at their defaults.
The designs are R271 sec.7's (`review/ruled/klee-pool-consolidation-2026-09-09.md`);
every number below is a starting value.

**Cut (pick 1):** `proto_ko_long_fuse`, `proto_ko_explosives_workshop`,
`proto_ko_sugar_rush`, `proto_ko_kindling`, `proto_ko_catalytic_converter`.
Rapid Fire stays. The rising hand cost Long Fuse once carried had no row left,
so `KleeOverhaulRisingCost` and its sim twin are deleted.

**`proto_ko_hair_trigger`** (R271's "Tripwire", renamed: a shipped card "Trip
Wire" exists). Common Skill, 1 Energy, "Your Bombs on this enemy become a
Mine.", upgrade cost 0. Every charge on the aimed enemy is flagged a Mine at its
own size (`ProtoBombPower.MineAllOn`, `klee_overhaul.mine_all_on`); nothing
moves, merges or goes off, so the pile keeps its order and riders.

**`proto_ko_explosive_frags`**. Uncommon Power, 1 Energy, "Whenever a Mine goes
off, apply 2 Vulnerable to that enemy.", upgrade 3. Read at the one site a
charge goes off, AFTER the Mine's own hit, for any Mine of hers whatever set it
off (`MineFragsPower`, `klee_overhaul.MINE_FRAGS`). The shipped Rare of the
same name is hidden by the arm's whole-pool swap.

**`proto_ko_where_did_i_put_it`**. Common Skill, 1 Energy, "Look at the top 4
cards of your draw pile. Put a Set off card from them into your hand and the
rest on the bottom.", upgrade 6. `scry_take` with `filter: set_off`; a Set off
card is any row whose body carries a `set_off` op (`ISetOffCard`,
`klee_overhaul.is_set_off_card`). With none among them, all go to the bottom.

**`proto_ko_big_bounce`**. Uncommon Attack, 1 Energy, "Set off. Deal 5 damage.
Explosion damage past the enemy's HP is dealt to a random other enemy.",
upgrade 8. `set_off` with `overflow: bounce`: the explosions' damage past the
kill is summed and dealt as ONE plain Pyro hit to a random other living enemy,
before the card's own hit. It does not Set off and does not bounce again; the
destination's Vulnerable is not applied (it was paid at the source).

**Hexerei becomes Companion (pick 2).** Coven Errand reads
`companion_played_this_turn`, Witches' Circle pays per Companion play, Alice's
Introduction Magic (`companion_mark_hand`) makes the hand count as Companion
cards -- and, with its `hexerei:` key gone, no longer counts itself. The Spark
rider (`ForCovenSpark`) rides every companion face on Klee's profile.
2026-09-23: under the arm a Companion play mints no Spark any more, so
`ForCovenSpark` returns its inherited tips unchanged there; the readers are
untouched.


## R276 -- the pool expansion to 78 (2026-09-23)

Thirty rows designed by the main session (2 Common, 18 Uncommon, 10 Rare),
built C# first and twinned in tier0, taking the pool from 48 to 78. The
readings below are the builder's where the spec left a choice; each is pinned
in `klee-mod/KleeTests/Prototype/KleeR276ExpansionTests.cs` and
`tier0/tests/test_klee_r276_expansion.py`.

**"Your largest Bomb"** (One More Charge, Treasure Map, Half a Mountain,
Patience, Klee!, Friendship Bracelet, Favonius Escort) is the arm's one
existing reading, `ProtoBombPower.LargestCharge`: the largest single charge of
hers on the living board, the first found on a tie (board order, then
placement order inside a pile -- so the older of two equal charges in one
pile). The spec's "ties: the older one" holds inside a pile; across two
enemies the tie goes to board order, because no charge carries a placement
stamp.

**`proto_ko_hiding_spot`** is the spec's Hide and Seek, renamed on the clash
with the shipped `hide_and_seek`. Block 6, then a Mine 3 on a random enemy.

**`proto_ko_playdate`**: `PlaydatePower`, Rally's construction under Klee's
reading of a Companion card (`CountsAsCompanion`). Two copies take 2 off the
same next card. Expires at the end of the turn.

**`proto_ko_jumpy_dumpty_mk_iii`** is the spec's Jumpy Dumpty Mk.II, renamed
on the clash with the shipped `jumpy_dumpty_mk2`. A `damage` op with the
`plant_on_hit` rider: each hit rolls a living enemy and plants on it; a hit
that kills sends its Bomb to a survivor (`PlaceOrJump`).

**`proto_ko_spinning_sparkler`**: the `grow_on_hit` rider. "Grows that Bomb"
grows the enemy's LARGEST charge of hers by the printed number, so the pile's
total rises by exactly 2 per hit.

**`proto_ko_mine_all_mine`**: `only_if: mined`, the enemies holding a Mine of
hers read once before the first hit.

**`proto_ko_team_effort`**: `set_off` with `wide_if:
companion_played_this_turn` -- every enemy's Bombs go off one enemy at a time,
then the 6 lands on the aimed enemy only (`SetOffAllThenHit`).

**`proto_ko_fish_fry`**: the shipped `bonus_vs_bombed` field, legal on a
`proto_ko_` all-enemies hit and read once before the first hit; the sim's
reader now counts `ko_charges` as well as shipped Bombs.

**`proto_ko_one_more_charge`**: `grow_largest` with the bar measured on the
grown Bomb. **`proto_ko_treasure_map`**: `fetch_from_discard` then
`grow_largest`; a lone candidate is taken without a screen (`ScryTake`'s
rule), none and the growth still happens.

**`proto_ko_sit_tight`**: 1 Spark, Retain, Block 5, then `apply_power
ko_sit_tight 4` (`SitTightPower`), which pays its 4 Block at
`BeforeSideTurnEnd` if rule 7's first counter (`SetOffThisTurn`: any Bomb or
Mine of hers went off, for any reason) is still 0, and is spent either way.
The sim pays it in `klee_overhaul.sit_tight_turn_end`, ahead of
`effects.player_turn_end_triggers`. The upgrade (7 and 5) is `block: +2,
power_amount: +1`. Before 2026-09-23 the 4 was a play-time `conditional` on
`no_bomb_went_off_this_turn`, which only rewarded playing it before a
detonator.

**`proto_ko_tag_along`** / **`proto_ko_adventure_club`**: `add_random_companion`
draws uniformly from the run's companion pool less other characters'
Personals, with the stand-in hand-off, and sets each to cost 0 this turn.

**`proto_ko_come_back_and_play`**: `fetch_from_discard` of a Companion card;
the upgrade appends a draw.

**`proto_ko_boom_badge`**: since the 2026-09-24 playtest ([USER]: "seems
weak") "The next time you Set off this turn, your Bombs deal double damage", 2
Sparks (1 upgraded). It was the game's replay surface, and the second play
found the Bombs already gone. Now each card-facing Set off entry point spends
the badge once (`BoomBadgePower.Spend`; sim `take_boom_badge`) and hands its
factor to every pile that clause reaches, multiplied with The Big One's armed
multiplier (x8 together). Two badges double the same next Set off twice (x4).
A Mine answering an attack is not a Set off and never spends it. Expires at
the end of the turn.

**`proto_ko_wait_for_it`** (Klee balance review, pick 4a, 2026-09-25: cost 0,
and the upgrade draws 3 instead of cutting the cost -- so the power's stack is
now the cards drawn and the Energy is 1 per payout): a one-shot on the
charge-aware explosion door; it
pays 2 cards and 1 Energy per copy on her first reacting explosion this turn
and is gone at the end of the turn.

**`proto_ko_duck_and_run`**: Block 7, then an aimed Set off.

**`proto_ko_party_poppers`**: "costs Sparks" is the cost badge
(`SparkCost.PriceOf > 0`), so the X-priced Fireworks Finale and Stoke the Fuse
count. Every play counts, a replayed one included.

**`proto_ko_look_out`**, **`proto_ko_second_surprise`**, **`proto_ko_aftershock`**:
the charge-aware door `KleeExpansion.AfterChargeExploded`, after the explosion
bus in `Explode`. Look Out! and Second Surprise answer a Mine however it went
off. Second Surprise's half is of the Mine's own size (not a multiplied hit),
and jumps if the enemy died. Aftershock's copy is of the charge's size, once
per turn per Klee on the ledger's latch, one Bomb per copy.

**`proto_ko_patience_klee`**: grows at `AfterSideTurnEnd`, strictly after
Sparks 'n' Splash's echo at `BeforeSideTurnEnd`, so the two never race.

**`proto_ko_secret_base`** and **`proto_ko_dodoco`**: both at
`AfterPlayerTurnStart` (after the draw and the growth) through one sequencer,
`KleeExpansion.RunTurnStartPlacements`, so Secret Base reads the board before
Dodoco's Mine lands. Dodoco's Mine joins any pile there as a Mine charge.

**`proto_ko_half_a_mountain`** / **`proto_ko_favonius_escort`**: repeatable
doubling; Sorry, Jean...'s removal with the Block times 2.

**`proto_ko_windblume_fireworks`**: Set off ALL, then 10 to ALL, then a Bomb 6
on ALL -- three existing ops in the printed order.

**`proto_ko_fireworks_finale`**: the all-in Spark price and `times:
sparks_spent`, one hit of 5 to ALL enemies per Spark spent.

**`proto_ko_spark_knight`**: rides `SparkPower.Gain` (the sim's
`gain_sparks`), one hit per Spark that LANDED, from any source. Since the
2026-09-24 playtest ([USER]: "seems underpowered") it costs 1 and each hit is 3
damage to ALL enemies (4 upgraded), where it was 2 to a random one. The hit has no
element (`ElementalHit.DealUnelemented`; the sim's `element=None`) since
2026-09-23, so it cannot spend an aura a companion laid down.

**`proto_ko_alices_detonator`**: two Power twins, `AlicesDetonatorPower` and
`AlicesDetonatorPlusPower`, installed by the card's upgrade; each adds one
Ka-pow! (upgraded on the Plus twin) per stack after the turn's draw.

## The co-op set (2026-09-25)

Design: `review/records/coop-set-2026-09-25.md` ([USER], "Co-op interaction,
pick 3a"). Nine rows, three per overhaul arm, each `multiplayer: true`: the
codegen emits the base game's `CardMultiplayerConstraint.MultiplayerOnly`
(Tank, Demonic Shield, Flanking, Sneaky), and `CardPoolModel.GetUnlockedCards`
and `CardFactory.FilterForPlayerCount` keep them out of every single-player
reward, shop and transform. Each arm offers them through its own
multiplayer tier (`KleeOverhaulRoster.MultiplayerSlice`,
`KokomiOverhaulRoster.MultiplayerSlice`, `FurinaStageRoster.MultiplayerRows`)
beside its pool and outside its count; the sim mirrors are
`C.*_MULTIPLAYER_IDS`, and `tools/lint_arm_pool_parity.py` holds sheet, mod
and mirror together. "Another player" is `target: ally`, the base game's
`TargetType.AnyAlly` (Lift, Believe In You); "each other player" is
`CoopSet.OtherPlayers`, Rally's and Huddle Up's own walk. The runtime is
`klee-mod/KleeCode/Powers/Prototype/CoopSet.cs`. Tier 0 seats one player, so
the sim loads the rows and never deals them (`tier0/engine/coop.py`).

**`proto_ko_pass_the_match`**: `PassTheMatchPower` goes ON the ally, placed by
Klee. The ally's next Attack (one stack each) is watched from
`BeforeCardPlayed` to `AfterCardPlayed`; every enemy it hits (the Attack as
`cardSource` of `AfterDamageReceived`, fully blocked hits included) has
Klee's Bombs set off after the play, through `ProtoBombPower.SetOff` with
Klee as applier and no card source, so it is not a "Set off card". Gone at
the end of the player turn. The face token for "Draw 1 card" is authored,
because an authored face's draw number is never auto-tokenised.

**`proto_ko_hide_here`**: Careful Now's read (`LargestBombBlock`) paid to the
aimed player, `ValueProp.Move` with the play attached (Klee's Dexterity folds
in, Lift's door).

**`proto_ko_knights_of_favonius`**: `KnightsOfFavoniusPower` on Klee; every play
of another player's Attack is watched the same way and sets off after it.

**`proto_fs_guest_of_honor`**: `GuestOfHonorPower` goes ON the ally. Its
`ModifyHpLostBeforeOsty` runs after the ally's Block and hands the rest to
`FurinaStage.AbsorbHit` for Furina's lead (rule 6: no Bow on a hit-emptied
lead, Rapt Audience fires); a hit a lethal Mine already answered
(`ProtoBombPower.Preempted`) takes nothing off the lead. Attacks only. Gone at
the next player turn start or when Furina dies.

**`proto_fs_share_the_spotlight`**: `FurinaStage.ShareTheSpotlight` empties
the back bar exactly, gives it to the aimed player as card Block, then Bows.

**`proto_fs_people_of_fontaine`**: `PeopleOfFontainePower`, a bare
`FurinaStage.Raise` on every play of another player's Attack.

**`proto_kk_joint_orders`**: target `KokomiTargets.PetOrAlly`. On the ally, the
now-line (Lift). On the Bake-Kurage, the Plan clause `AllyDraw`, whose player
is captured at writing (`CoopSet.PlanAlly`) as a CombatId on
`Planned.Targets`; a dead player draws nothing.

**`proto_kk_coordinated_strike`**: the Plan clause
`OthersAttackDamageThisTurn` puts Battle Plan's `AttackUpThisTurnPower` on
every other living player at carry-out.

**`proto_kk_sangonomiyas_counsel`**: `SangonomiyasCounselPower` on the Plan bus,
every Plan, `ValueProp.Unpowered` Block to each other player (SneakyPower's
shape).

### The second batch (2026-09-27)

Design: `review/ruled/coop-concepts-2026-09-27.md`, "Proposed cards" ([USER],
2026-09-27, picks 2a and 3a at their defaults). Four more `multiplayer: true`
rows on the first set's terms, two for Klee and two for Furina; Kokomi's pair
waits for her review (pick 4). The runtime is the same file, `CoopSet.cs`.

**`proto_fs_raise_a_toast`**: the new op `stage_toast` (`cap`, `target: ally`),
one call into `FurinaStage.RaiseAToast`: the front performer's Fanfare, read
and never spent, capped at the printed 6 (8 upgraded), applied to the aimed
player as `RaiseAToastPower`, a `TemporaryStrengthPower` subclass (the base
game's Coordinate), which removes itself and its Strength at the end of the
turn. An empty stage gives 0 and applies nothing; the card stays playable. The
`cap` upgrade key now binds either capped op (`gen_klee_cards.CAP_VAR`,
`upgrades.py`'s twin); the var is `ToastCap`.

**`proto_fs_the_crowd_roars`**: `TheCrowdRoarsPower` on Furina, on the base
game's `AfterCurrentHpChanged`: any negative delta on a player on her side who
is not her, whatever caused it and whatever its size, runs
`FurinaStage.RaiseLead` for the stack (1). `RaiseLead` asks the same
round-four door `Raise` does, so on an empty stage a random performer arrives
holding it, exactly as The People of Fontaine. Two copies give 2.

**`proto_ko_shrapnel`**: the arm's Mine placer (`plant_bomb`, `mine: true`, the
Booby Trap call), then `ShrapnelPower` on the same enemy, placed by Klee.
`ModifyDamageMultiplicative` is `FlankingPower`'s dealer check (a powered
attack, on this enemy, whose dealer is not the applier) plus a live
`ProtoBombPower.HoldsMineFrom(enemy, Klee)`, at x1.5. Single, instanced per
applier: one shred per Klee however many Shrapnels, where Flanking stacks
(accepted as designed, 2026-09-27). When one of her Mines goes off and she
holds none on that enemy after it, `ShrapnelPower.AfterMineWentOff` (called
from the Mine branch of `ProtoBombPower.Explode`) removes the badge. An ally's
Attack under Pass the Match or Knights of Favonius sets the Mine off at
`AfterCardPlayed`, after its hits, so that Attack is shredded. Debuff, like
Flanking, so Artifact refuses it.

**`proto_ko_sparks_for_everyone`**: `SparksForEveryonePower` on Klee, an
`IProtoExplosionListener` (Chained Reactions' bus), so every one of her Bombs
counts however it went off, a Mine answering an attack included. Once per turn
on the ledger's latch (`KleeOverhaulLedger.TakeSparksForEveryone`, Aftershock's
shape, rolled on the round), each other living player gains the stack (1) in
energy through `PlayerCmd.GainEnergy` (Believe In You). Only a Bomb that goes
off on the players' turn counts (designer ruling, 2026-09-27): a Mine answering
an attack on the enemies' turn gives nothing and does not use up the turn's
trigger, so the next explosion on the players' turn still pays
(`SparksForEveryonePower.Counts`, asked before the latch). With nobody else
alive the latch is not spent either. The upgrade is Innate; the cost stays 2.

## Kokomi core pass: eight cards (2026-09-27)

Design: `review/ruled/kokomi-core-pass-2026-09-27.md` (ruled at its defaults).
No rule changed and her starter is untouched.

**Faces.** Ambush, Cleansing Wave, Ripple, Feigned Retreat and Second Wave
swap a Block now-half for Vulnerable, a draw, draw-then-discard or 5 damage;
their Plan halves stand. Feigned Retreat prints the base game's "Draw 2 cards.
Discard 1 card." (a chosen discard). Second Wave's hit applies Hydro by the
arm's cadence, as Opening Gambit's does.

**`first_companion_free`** (Chain of Command's Plan): Stolen Chapter's
`first_card_free` narrowed to Companion cards. `FirstCompanionFreePower` /
`kokomi_plan.FIRST_COMPANION_FREE`: zero cost at the cost seam, spent by the
first Companion she pays for, gone at her turn's end. `KokomiPlan.Kind`
appends it last so no ordinal moves.

**`proto_kk_song_of_pearls`**: the queue is read at her turn start just
before the morning drain (`ProtoBakeKuragePower.AfterPlayerTurnStart`,
`combat._player_turn`); if it was empty, `SongOfPearlsPower.Strike` runs after
the drain and deals the stack to every hittable enemy as a planned hit is
dealt (Hydro, unpowered, her Strength folded by `Hers`). A morning that carried
a Plan out never fires it. A Dusk Plan was carried out the evening before, so
it leaves the next morning's queue empty. Plans held back by the lane cap
count as waiting.

**`proto_kk_treatise`**: `TreatisePower.AfterCardPlayed` draws the stack, once
a turn on the ledger latch, when she plays a card with a Plan line and
`KokomiPlan.PlayedOnPet` says no. The write test comes before the claim, so a
written card does not spend the turn's draw. An auto-play of a Plan card goes
to its now-line and counts. Sim: `kokomi_plan.note_face_up_plan_card` at the
end of `effects._resolve_card_bound`. Both powers left the plan bus.

## Furina, the Stage — balance pass one (2026-09-28)

[USER]'s Stage run on 2026-09-28 was "extremely easy" until an act-3 elite,
and the review found Fanfare GENERATION too high. The spend side is untouched:
"I actually think the spend is totally fine; it's the generation that's the
issue. Let's leave these alone for now." Bravura and every spender keep their
numbers. Design: `review/active/furina-stage-brief-2026-09-08.md`.

- **Dual Nature** (`proto_fs_dual_nature`): the upgrade is +1 draw (draw 2)
  instead of cost -1; it stays 1 cost. "I think a is good".
- **Guest Star: Lynette, Sigewinne, Wriothesley**: arrive with 5 Fanfare, not
  8; the upgrade stays +2 (7). "a) is good for now. This is much more
  effective block than a Necrobinder deck gives, but the per-card amount is
  fine; it's more the frequency that's higher."
- **Gala Dinner** gives each performer 2 (3 upgraded); **Season Tickets** 1 a
  turn (2 upgraded); **Thunderous Applause** 1 Fanfare a Bow (2 upgraded),
  its draw 1 a Bow unchanged. "agreed". The power's Amount is the Fanfare
  only (`FurinaStage.AfterBow` draws a fixed 1 a copy), so only the Fanfare
  moved. The face prints `{PowerAmount:diff()}` itself, and
  `gen_klee_cards._authored_face_with_tokens` now leaves a literal alone when
  the face already prints that var's token, so the draw's 1 is not taken for
  the amount.
- **Plot Twist** is an Attack: "Reverse the order of your performers. Deal 7
  damage." (10 upgraded), one enemy, no Block; cost 1, Common. "a)".
- **Two rows left the pool, 80 -> 78**: *Understudy* (`proto_fs_understudy`)
  and the summon-Usher card *Gentilhomme Usher*
  (`proto_fs_gentilhomme_usher`). "agreed on a)". Usher the PERFORMER stays.
  The shipped rows they replaced (`suffering_for_art`, `gentilhomme_usher`)
  stay out of the offer: the mod's `FurinaStageRoster.SwapOfferedRows` filter
  still names both, and the sim drops them through the new
  `furina_stage.POOL_DROPS` (read by `loader.pool_drops`, applied in
  `tier05.rewards.character_pool`). Both ids are in
  `docs/retired-card-ids.yaml`, so a save holding one still loads.

## Furina, the Stage — the Spend pass (2026-09-28)

After balance pass one (#740) two Sonnet seats both cleared both A0 bosses
comfortably. [USER]: "If Furina is still generating too much Fanfare and not
enough damage, we could solve her problem by upping both the spend and output
of her cards." Design: `review/active/furina-stage-brief-2026-09-08.md` §16.
Each row keeps its upgrade key; base / upgraded:

- **Quick Cue** (`proto_fs_quick_cue`): 3, or Spend 3: deal 11 and apply
  Hydro (was Spend 2: 8). Upgraded 4 / 12. The upgrade is
  `{conditional_damage: +1}`; the `conditional_then_damage: +1` that made it
  4 / 10 is gone, so both numbers move by one.
- **Spirited Aria** (`proto_fs_spirited_aria`): 8, or Spend 3: deal 11 and
  draw 2 cards (was Spend 2: 8 and draw 2). Upgraded 11 / 14, draw 2 both.
  The face now prints the Spend mode's own damage: "Deal 8 damage. Spend 3:
  deal 11 and draw 2 cards instead."
- **Tidal Flourish** (`proto_fs_tidal_flourish`): 5 to ALL, or Spend 3: 10
  to ALL and apply Hydro to ALL (was Spend 2: 9). Upgraded 8 / 13.
- **Interposition** (`proto_fs_interposition`): 5 Block, or Spend 3: 13
  (was Spend 2: 10). Upgraded 8 / 16.
- **Grand Entrance** (`proto_fs_grand_entrance`): 12, or Spend 7: 32 (was
  Spend 5: 24). Upgraded 16 / 36.

Not changed: Curtain Rise (the starter; [USER]'s pick), Bravura, Bring the
House Down, Let the People Rejoice, the performers' acts. The tier0 sim reads
these rows (`furina_stage.spend_mode_amount` takes the price off the mode's
head op), so it moved with them.

**The blind-seat page prints a Spend mode it cannot pay.** Both seats: "Spend
2 wasn't offered on some turns and offered on others; I only learned by
trying." The game offers the mode only when the back performer can pay in
full (`FurinaStage.CanSpend`; with Palais Ledger, the whole stage), and with
one mode left it plays it without opening the chooser
(`ModalChoice.TakenWithoutAsking`). `blindplay_board.spend_unavailable` now
marks each such mode under its hand card, e.g. "Spend 3: deal 11 and apply
Hydro instead — unavailable: your back performer has 2 Fanfare" (or "the stage
is empty"). The game's chooser is unchanged: the 0.111.0 choose-a-card screen
has no per-option disabled state (`ModalChoice.SelectAffordableMode`'s
comment). Pinned by `tier0/tests/test_furina_spend_pass_2026_09_28.py`.

## Furina, the Stage — Bravura gains a base (2026-09-29)

**Bravura** (`proto_fs_bravura`): "Spend all of your back performer's
Fanfare. Deal 5 damage, plus 3 per point." (plus 4 upgraded; the base stays
5). Was 3 damage per point with no base, 4 upgraded. The row is
`amount_formula: {base: 5, per: 3, count: stage_spent}`, upgrade
`{formula_per: +1}`; the face prints `{CalculationBase}` and `{ExtraDamage}`
like Da Capo and keeps the in-combat `{CalculatedDamage}` line. Why: the
Sonnet seats of 2026-09-28 (run FSR3RUN2Q7XB, acts 1 to 3) named it their
"never again" card: "Bravura -- deals 3 damage per Fanfare of a back
performer that is almost always 1". A main-session tuning fix under [USER]'s
direction "upping both the spend and output of her cards" (the Spend pass,
above, which had left Bravura unchanged). The tier0 sim reads this row, so it
moved with it. Design: `review/active/furina-stage-brief-2026-09-08.md` §16.

## Furina, the Stage — the audit pass (2026-09-29)

[USER]: "a dedupe / audit / balance pass on Furina, aimed at polishing the
existing core systems". Designed by the main session off a factual packet
(the sheet and twelve seat records: which cards the seats named, and damage
and Block per Energy); the reasons, card by card, are in
`review/active/furina-stage-brief-2026-09-08.md` §17.

**Cut, 78 -> 75:** `proto_fs_gala_dinner` (no seat record named it),
`proto_fs_rapt_audience` (the same) and `proto_fs_scene_change` (the third
rotation Common; [USER]'s "stage rotation spam"). Plumbing as for the
balance pass's two: the rows leave the sheet and `FurinaStageRoster`'s
append list; their shipped rows (`dress_rehearsal`, `crowd_work`,
`held_breath`) stay out of the offer through the `SwapOfferedRows` filter,
and the sim's `furina_stage.POOL_SUBS` loses the three pairs while
`POOL_DROPS` gains the three shipped ids. The ids are tombstoned in
`retired-card-ids.yaml` (hidden aliases), and the three painted portraits are
`art_coverage.KNOWN_STALE`. The engine verbs stay: `stage_scene_change`,
`seat: all` (Grand Deluge still raises all) and `RaptAudiencePower` (its
C# and sim pins still run).

**Numbers.** Ensemble Piece `per: 5`, upgrade `formula_per: +2` (5 per
performer, 7 upgraded; was 4 and 5). Improvised Number 8 (11; was 6 and 9).
Ousia Surge `base: 3`, upgrade `formula_base: +3`, face "Deal
{CalculationBase} damage, plus {ExtraDamage} for each Fanfare on your back
performer." (base 6 upgraded; was 0 plus the Fanfare, base 4 upgraded, and a
face with an `IfUpgraded` "plus 4"). Pneuma Refrain the same shape on Block:
"Gain {CalculationBase} Block, plus {CalculationExtra} for each Fanfare on
your front performer." Final Bow `per: 2`, "Gain Block equal to twice its
Fanfare."; the upgrade still removes Exhaust. Bring the House Down `per: 3`
(4 upgraded; was 2 and 3). Grand Deluge 12 to ALL (16; was 10 and 14). Each
formula face keeps its in-combat line. The tier0 sim reads these rows, so it
moved with them; the C# is regenerated.

**Frozen on a boss.** The Frozen preview (`KLEEMOD-FROZEN_PREVIEW`) and the
seat page's Frozen row end "In a boss fight, only minions can be Frozen; the
others become Vulnerable instead." The page's boss clause is that sentence now,
on the row in every room (it names the room, so it is true on each) rather
than appended in a boss room only.

## Furina, the Stage — the fade pass (2026-09-29)

[USER]: "I swear that I have never seen it tick down any of the summons
in-game before", then "make Fanfare deplete faster, but make that depletion
more impactful. Keep her Block cards generally weak but her Spend cards
strong", "What about a percentage fade, say 25%? Anything below 4 rounds to
losing 0." and "Yes, please proceed!" Designed by the main session; the
reasons and the sim evidence are in
`review/active/furina-stage-brief-2026-09-08.md` §18.

**Rule 12.** Every performer, the front one included, loses a quarter of its
Fanfare, rounded down, at the end of Furina's turn after the acts
(`FurinaStageLaw.FadeDivisor` = 4, `FadeLoss(f) = f / 4`;
`furina_stage.FADE_DIVISOR`, `fade_loss`). `FadeThreshold` and
`EternalFadeThreshold` (and their sim twins) are gone; the constant-parity
registry mirrors `FadeDivisor`. `FurinaStageLedger.Fade()` loops from seat 0.
`FurinaStage.FadeRules` is now `FurinaStage.Fades`, a switch Grand Theater
Program turns off; both the end-of-turn fade and the forecast read it. The
fade tip (`ArmKeywordTips.ForFade`), the Stage badge and the seat page's
glossary say "At the end of your turn, each performer loses a quarter of its
Fanfare, rounded down." No card face prints "fade" now, so the word left the
codegen keyword table; the tip stays as the sentence the glossary mirrors.

**Cut, 75 -> 72:** `proto_fs_held_applause`, `proto_fs_echoing_hall` and
`proto_fs_eternal_applause`. Plumbing as for the audit pass's three: the rows
leave the sheet and `FurinaStageRoster`'s append list; their shipped rows
(`directors_cut`, `pit_orchestra`, `rapturous_applause`) stay out of the offer
through the `SwapOfferedRows` filter, and the sim's `POOL_SUBS` loses the
three pairs while `POOL_DROPS` gains the three shipped ids. The ids are
tombstoned in `retired-card-ids.yaml` (hidden aliases regenerated), and the
three portraits are `art_coverage.KNOWN_STALE`. Unlike the audit pass, their
engine code is deleted: the `stage_hold_fade` op and `FurinaStage.HoldFade`,
the ledger's `FadeHeld`, `EchoingHallPower` and `EternalApplausePower` (and
their icons and codegen entries), the sim's `hold_fade`, `fade_threshold`,
`ECHOING_HALL`, `ETERNAL_APPLAUSE` and `stage_hold_fade`. Nothing else used
them.

**Numbers.** Curtain Rise's Spend mode 17 (upgrade `conditional_damage: +3,
conditional_then_damage: +1`, so 10 / 21; was 13, 16). Tidal Flourish 13 to
ALL (16; was 10, 13). Quick Cue 14 (upgrade `conditional_damage: +1,
conditional_then_damage: +1`, so 4 / 16; was 11, 12). Spirited Aria 14 and
draw 2 (17; was 11, 14). Grand Entrance 40 (upgrade `conditional_damage: +4,
conditional_then_damage: +1`, so 16 / 45; was 32, 36). Bravura `per: 4` (5
upgraded; was 3, 4). Bring the House Down `per: 4` (5 upgraded; was 3, 4).
Each plain mode keeps its number and its upgrade. The tier0 sim reads these
rows, so it moved with them; the C# is regenerated.

## Kokomi: Kurage's Oath now-line, and Plan lines on their own line (2026-09-28)

**Kurage's Oath** (`proto_kk_kurages_oath`, her starter). [USER]: "The
non-plan effect is quite bad (worse than a basic defend)" ... "Option 1 is
fine for now." The now-line goes 4 -> 6 Block and the upgrade moves both
halves, `{block: 2, plan_damage: 3}`: upgraded, 8 Block / Plan 10 to ALL. The
Plan stays "Deal 7 damage to ALL enemies." The tier0 sim reads this row, so
it moved with it.

**Plan lines.** [USER]: "The idea of Plan cards makes sense, but the card
text gets harder to read. Can we move all Plan lines to the next line down?"
The break is made once, on the emitted face: `gen_klee_cards._face_riders`
calls `plan_line_on_its_own_line`, which turns the space before a
sentence-opening `[gold]Plan[/gold]:` (or `[gold]Dusk[/gold]
[gold]Plan[/gold]:`) into a line break. Every face path passes through it,
so the sheet rows keep one-line prose and the text lints count them as
before. 27 faces moved; Change of Plans' "Cancel your last
[gold]Plan[/gold]: ..." is a sentence about a Plan and does not break. The
blind-seat bridge folds whitespace (`qa_packet._text`), so seats still read
one line per face. Pinned by `tier0/tests/test_plan_line_on_its_own_line.py`.

## Kokomi: the Casket pass (2026-09-28)

Designed in the main session and ruled by [USER] on 2026-09-28; recorded in
the brief (`review/active/kokomi-brief-2026-09-01.md`, sec. 4 and 10).

**The relic, Tamakushi Casket.** Forge-style over Vigor-style, because Vigor
"devolves into 'solve for lethal, press the I Win button'". The design: "an
artifact that grants / tracks an alternative energy that builds by 1 for every
Plan played, and adds one 0-cost Retain / Exhaust card that converts that
energy into Strength. We could build other archetypes in, including some that
read or modify the gauge." Counting: "when it's carried out". Rate: "1
strength per point seems fine; we can adjust down if we need to." "the casket
keeps counting." No card spends the gauge: "We don't need this to be the
equivalent to Regent's stars or Klee's sparks. This should feel like a
distinct effect."

- Face: "Start each combat with the Bake-Kurage and Open the Casket in hand.
  Each Plan it carries out adds 1 to the Casket." The ruled wording says "the
  Bake-Kurage" twice; "it" is the one change, because the ruled sentence is
  127 characters against the 120 relic ceiling (`lint_text_conventions`).
- The old debuff strike (2 Hydro per debuff she applied, `CasketStrike`) is
  REMOVED from both engines, with its constant and its V11 kit-verb row. The
  companion reward slot stays.
- The count is per combat and starts at 0. It lives on the arm's ledger
  (`KokomiOverhaulLedger.CasketCount`, sim `CombatState.kk_casket`) so a card's
  calculated var reads it with no relic lookup. The relic adds
  `KokomiOverhaulLaw.CasketPerPlan` once per CARRY-OUT from
  `KokomiPlan.ResolveEntry` (sim `kokomi_plan._note_plan_resolved`), so the
  morning, Dusk and Change of Plans all count, and a Plan carried out twice
  (Second Wave, Nereid's Ascension) adds twice. A Kokomi not holding the relic
  adds nothing on a carry-out; the cards that say "the Casket gains" add
  either way.
- SHOWN AS THE RELIC'S COUNTER, the base game's idiom (`Kunai`, `Pen Nib`):
  `ShowCounter` in combat, `DisplayAmount` the count. The bridge already sends
  a relic's counter (`McpMod.StateBuilder`: `counter = ShowCounter ?
  DisplayAmount : null`) and the blind page prints "Tamakushi Casket (N)", so
  the seats read it with no new wire field.

**Open the Casket.** Skill, 1, Retain, in no pool (it was 0, Retain,
Exhaust until 2026-10-01, the four-kit review's Kokomi pick 1): "Gain Strength
equal to the Casket's count, then empty it." A hand-written token
(`Cards/Prototype/OpenTheCasket.cs`, off-pool in `KokomiOffPoolCards`), not a
sheet row: the surface has no token rarity, and a `proto_kk_` row outside the
pool is a finding for `lint_arm_pool_parity`. Furina's Ethereal Spotlight is
the same shape. The relic deals it before the first hand draw
(`BeforeHandDraw` on turn one, `RadiantPearl`'s site). Sim twin:
`kokomi_plan.open_the_casket_card`, dealt on turn one by
`kokomi_plan.deal_open_the_casket` (after the opening draw, the sim's
combat-start site; it moves no card of the opening hand). No upgrade.

**Re-keyed payoffs.** Feint: "Deal 4 damage, plus 3 for each Plan carried out
this turn. Plan: Apply 1 Vulnerable." (base 6 upgraded, Plan Vulnerable 2).
Sango Isshin: "Deal 8 damage to ALL enemies, plus 6 for each Plan carried out
this turn." (10 plus 8 upgraded). The base of 8 came 2026-09-29: the Casket
pass had it at 0 plus 6 per Plan (8 per Plan upgraded), and a Sonnet seat
(Kokomi run KK2EL3M3NTS9, act 2) named it NEVER AGAIN -- "counts plans carried
out this turn, which resolve before I can play it" and "Deals 0 damage" most
turns. A code read found no bug: 0 is correct on turn 1 and after any turn
without Plans, which made a 2-cost Rare dead on those turns. Main-session
tuning fix; the upgrade moves base and per by 2 each. Both read the new per-turn count
(`KokomiOverhaulLedger.PlansCarriedOutThisTurn`, sim
`kk_plans_carried_out_this_turn`), written once per carry-out. Treatise and
Song of Pearls are unchanged.

**Numbers.** Second Wave Common -> Uncommon, now-damage 5 -> 7. Pincer 3x2 ->
4x2 (5x2 upgraded). Opening Gambit 5 -> 7. Deep Current 6 -> 7 to ALL, and an
upgrade of +2 (9). Riptide 11 to ALL, debuffed enemies take 3 more; upgraded
+3 and +1 (14 / 4), the existing upgrade shape with the rider's delta scaled
down with the rider; the Plan is "Gain 2 Energy and draw 1 card."

**Cut from the offer:** Tide Chart, Cleansing Wave, Ripple, Well Laid,
Sea-Salt Prayer, Salt Line (proto). Rows deleted, ids tombstoned in
`docs/retired-card-ids.yaml`, retired aliases generated. Their ops stay
registered (`draw_after_plans`, `remove_debuff`, the `debuffs_on_target`
count) with no row spelling them.

**Thirteen rows**, last in the sheet's order. On the Commons, [USER]: "Let's
avoid having too many attack / block spam cards ... they shouldn't just be 10
copies of 'do x damage, or plan y'". Numbers "agreed". AoE: "5 to 7 damage per
1 energy is roughly the going rate on AoE commons". Each wears the portrait of
the shipped Kokomi card whose id it borrows (`art_of:`). Kokomi art pass 2
(2026-09-29) gave ten of them their own art (Massed Volley, Signal Arrow,
Surging Shoal, Pearl Diver, Press the Advantage, Shell of Sanctuary, Depths' Judgment, Moon
Signal, Pearl Current, What the Tokoyo Took; `art/plan.tsv`); the other three
keep the proxy.

- Commons: Massed Volley (3x3; 4x3), Signal Arrow (7, Plan 3 to ALL twice; 10
  / 4 twice), Surging Shoal (2 energy, 14, Plan 22; 18 / 28), Pearl Diver
  (draw 1, Plan the Casket gains 2; draw 2), Press the Advantage (6, or 10 if
  a Plan is waiting; 8 / 13 -- "waiting" is the queue, the `plan_held`
  predicate), Shell of Sanctuary (draw 1, Dusk Plan 9 Block; 12), Driftglass
  (5 plus 1 per point in the Casket; base 7).
- Uncommons: What the Tokoyo Returns (1, Exhaust: the first Open the Casket in
  the Exhaust Pile goes to hand, none there nothing happens; cost 0), Depths'
  Judgment (2, damage = 3 x the Casket's count, with the in-combat preview; 4
  x), Tideturn (4 per Plan waiting; 5), Moon Signal (Power 1; cost 0), Pearl
  Current (2x4, Plan 2 to ALL x3; 3s).
- Rare: What the Tokoyo Took (2, Exhaust, double the Casket's count; cost 1).

**Moon Signal's timing.** "If 2 or more Plans are waiting" is read BEFORE the
morning's Plans are carried out, or it could never be true after a drain empties
the queue. `ProtoBakeKuragePower.AfterPlayerTurnStart` takes the queue depth
beside Song of Pearls' read and hands it to `MoonSignalPower.Signal` before
`KokomiPlan.ResolveAll`; the sim calls `kokomi_plan.moon_signal` at the same
point in `combat._player_turn`. The threshold is
`KokomiOverhaulLaw.MoonSignalThreshold`, mirrored by value.

**Hygiene.** The retired Garment tip (`KokomiRiderTips.ForGarmentAttack`) no
longer attaches to an arm row (`gen_klee_cards`, `proto_` ids skip it). Stale
pool counts (34, 39) read 46. The "Tamakushi Casket" keyword row now also
answers the short name "Casket", and "Open the Casket" has a tip of its own;
both are glossary rows on the blind page. The reaction glossary's clause
admitting "one relic's line" that applies an element went with the strike.

**Shell Guard, re-aimed (a main-session fix, 2026-09-28, not a [USER] ruling).** The Casket pass retired the strike Shell Guard's second clause paid on ("whenever the Tamakushi Casket strikes, gain 3 Block"), which left the clause dead. The card is now the Casket's defensive reader: "Gain 5 Block, plus 1 for each point in the Casket." Uncommon Skill, cost 1; upgraded base 8 (+1 per point unchanged); the in-combat Block preview Pneuma Refrain and the damage readers print. `ShellGuardPower` and its window (the dead `Pay` path and `Close`) are removed from both engines. It keeps its portrait.
In the C#, the Casket count rides the block rail's calculated var
(`gen_klee_cards.stage_count_block_rider` now also takes the Casket counts);
the sim reads `casket_count` through `effects._runtime_count`.

**Pool:** 46 offered (24 Common, 17 Uncommon, 5 Rare) plus the three co-op
cards.

## Kokomi: the cleanup pass (2026-09-29)

[USER], 2026-09-29: "a review and cleanup pass on Kokomi's current prototype
to handle the known problems". Designed in the main session; the design and
its evidence are in the brief (`review/active/kokomi-brief-2026-09-01.md`,
sec. 6, "The cleanup pass"). The evidence is the four Sonnet seat records of
2026-09-28: both runs died to an act-2 boss short of Block, and the hands
clogged with low-impact cantrips.

- `proto_kk_scout_ahead`, `proto_kk_song_of_pearls`: cut. Tombstoned in
  `docs/retired-card-ids.yaml` (retired aliases generated), kept as known-stale
  portraits in `tools/art_coverage.py`, out of `KokomiOverhaulRoster.Slice()`
  and `C.KOKOMI_OVERHAUL_POOL_IDS`. Scout Ahead: NEVER AGAIN in two records, one
  on the older build ("draw plan never mattered and cost a slot"). Song of Pearls fires by itself
  and "never seemed worth a slot". Their engine pieces (`SongOfPearlsPower` /
  `kokomi_plan.song_of_pearls`, `DrawPerPlanAfter` / `draw_per_plan_after`)
  stay registered with nothing spelling them, as Tide Chart's did.
- `proto_kk_shell_guard`: Uncommon to Common; numbers unchanged.
- `proto_kk_tide_wall`: the Plan clause `block_front_intent` takes `amount: 6`
  (it was 0; the upgrade's `plan_block: 3` makes 9). Both engines already add
  the amount to the intent read at carry-out. Face: "Gain 6 Block, plus the
  damage the enemy intends." "The front enemy" in the designed wording fails
  the text lint (a Plan line names no target; the tip carries the rule), so
  the face says "the enemy". A seat: "it gave 0 Block twice on Empower turns".
- `proto_kk_feint`: formula base 4 to 6, upgrade `formula_base` 2 to 3 (9).
- `proto_kk_press_the_advantage`: 6 / 10 to 7 / 11; the upgrade deltas are
  unchanged, so 9 / 14.
- `proto_kk_driftglass`: formula base 5 to 6; upgraded 8.

**Pool:** 44 offered (24 Common, 15 Uncommon, 5 Rare) plus the three co-op
cards.

## Varka: prototype batch one (2026-09-29)

[USER], 2026-09-29: "You're good to go on building the Varka prototype!" The
design is the paper kit's sec.10 (`review/active/varka-paper-kit-2026-09-28.md`,
with sec.5 and sec.9.1-9.6 for the rules it cites), built C# first; there is no
sim twin, and `tier0` registers his words and refuses to resolve them
(`effects.VARKA_OPS`, `VARKA_COUNTS`, `VARKA_PREDICATES`). Twenty rows here
(`proto_vk_`, owner `varka`): the starter's Four Winds' Ascension and the 19
pool cards of sec.10.3. Knights' Muster, the rest of the starter, is
hand-written (`Cards/Prototype/VarkaKnightsMuster.cs`) beside the base game's
Strike x4 and Defend x4 (Silent's pair, the frame his pool borrows).

What the rows needed that the grammar did not have, each one call into
`Powers/Prototype/Varka*.cs`:

- `tags: [absorb]` emits `IAbsorbCard` (Windbound Execution, Favonius Cut).
  The rule is the aura lifecycle's (`VarkaAbsorb.Decide`, asked by
  `AuraPower.ResolveLifecycle` and its forecast), so the card carries only
  the mark.
- `count: winds_held` on the damage and block rails (Ascension, Eye of the
  Storm), read off `VarkaWinds.HeldCount`.
- `if: holds_wind` (Wind Wall, Tailwind Stride) and `if: swirled_by_this`
  (Tempest Charge), the second a per-play diff of his Swirl count like
  `reaction_triggered_by_this`.
- `only_if: fresh_aura` on an all-enemies hit (Gale Sweep), `only_if:
  mined`'s shape: the fresh-aura bodies are taken when it is played, each takes
  its own hit, and a later body keeps its aura against an earlier Swirl's
  spread (sec.9.6).
- `knight_aura` (Favonius Drill) and `add_knight` (Knights' Roll Call; its
  upgrade `choose_knight` is a play-time `IsUpgraded` read, Alice's
  Detonator's shape).
- Four Knights do not fit the choose-a-card screen, which throws on more than
  three cards, so "choose a Knight" is a grid (`VarkaRules.ChooseKnight`,
  `CardSelectCmd.FromSimpleGrid`) over four option faces
  (`VarkaModalOptions`). Favonius Drill's sec.10.3 row is therefore not a
  `choose_one`.
- `tags: [dusty_tome]` emits BaseLib's `ITomeCard` (Ascension). He has no
  Ancient card, and Darv's Dusty Tome softlocks on an empty Ancient draw; the
  Tome hands him an upgraded Ascension until an Ancient is designed.
- `tags: [strike]` emits `CardTag.Strike` (Oathsworn Strike, 2026-09-29: a
  seat saw Strike Dummy pay on Strike and not on it). A non-basic Strike is
  tagged the way the base game tags Twin Strike; a basic still answers with
  `basic_tag:` alone.

Per row, where the face or the build differs from sec.10.3's words:

- `proto_vk_amber_baron_bunny`, `_barbara_show_begin`, `_lisa_violet_arc`,
  `_kaeya_frostgnaw`: titled as sec.10.3 prints them ("Amber: Baron Bunny"),
  colon and all. The dash form ("Lisa — Violet Arc") is the Mondstadt
  Universal of that name, a different card a Varka run can be offered, so the
  colon keeps the two apart. Companion rows (`star`, `nation`, `element`,
  `personal_pool: varka`), so their hit carries the Knight's element and
  Grand Master's Order can find them. Faces print `{CalculatedDamage}` /
  `{CalculatedBlock}`, the companion rail's var. Barbara keeps "Let the Show
  Begin" without the shipped row's note sign.
- `proto_vk_stormward_stance`, `proto_vk_boreas_unbound`: the face prints the
  literal 3 and 1; the upgrade is a cost cut, so no var moves.
- `proto_vk_converging_winds`: face "Your Swirls react where they land. An
  Elemental Reaction a spread sets off hits only that enemy." (the text lint
  spells the reaction that way).
- `proto_vk_grand_masters_order`: the upgrade is `retain: true` (sec.10.3's
  "[Retain.]").

**Pool:** 19 offered (10 Common, 7 Uncommon, 2 Rare), four of them Knights;
target 78 later.

**Starter costs, 2026-09-29.** `proto_vk_four_winds_ascension` cost 2 to 1
(damage and Exhaust unchanged), and the hand-written Knights' Muster cost 1
to 0 (upgrade still 4 to 6). [USER]: "I'm thinking we try 'Muster at 0 and
Ascension at 1' first." Evidence: both first blind seats died in act 1 (floor
8 elite; floor 7 Punch Construct), a 1-cost Muster leaving too little energy
for Block, and Ascension named "never again": "2 energy Exhaust for damage a
Strike-plus deals". Brief sec.10.2 carries the same line.

**Seat fixes, 2026-09-29.** Two blind seats' defects; the Fang ruling is the
main session's ("the Fang reads only an aura that was on the enemy BEFORE the
hit", after the paper's "a Knight never Absorbs its own paint").

- Absorb and Boreas's Fang no longer take an aura the same card's hit just
  applied (`AuraPower.PaintedBy`, `VarkaAbsorb.OwnPaint`): an element Attack
  on a bare enemy leaves its aura fresh and the Fang unused. On an aura that
  was already there, the Fang still takes the first non-Anemo Attack.
- The card's reaction preview asks the Absorb decision first: where the Fang
  (or an Absorb card) will take the aura it shows "Reaction preview: Absorb"
  instead of Melt/Vaporize, and a held Wind previews as the Swirl it becomes.
- An Absorb is a row on "What reacted this turn" ("Took the Pyro aura; you
  gained Pyro Wind.") and a line under its card on "What you played"; a held
  Wind's Swirl says "You already held Pyro Wind, so it Swirled instead of
  Absorbing." (`ReactionLog.NoteBeat` / `DetailNext`,
  `ResolutionLedger.NoteAbsorb`, wire keys `detail` and `absorbed`).
- The seat page counts Knights' Muster and Knights' Roll Call as supplying
  Pyro, Hydro, Electro and Cryo, so "NO REACTION IS REACHABLE HERE" no longer
  prints with one in hand.
- Words: the `aura` entry adds "A spent aura still reacts with Pyro, Hydro,
  Electro and Cryo."; the Varka aura line adds "Other elements still react
  with it."; Swirl's text now ends "The aura and its copies stay spent." (C#
  tip, preview row and the page, one commit; "No aura, no effect." left the
  tip to fit the 135 ceiling, since "On a fresh aura" already says it).
- Checked, not a defect: every reaction (Melt, Vaporize, Frozen, and the
  rest) is written to "What reacted this turn" by `ReactionEffects.Resolve`.
  The seats most likely saw only Swirl there because the Fang was Absorbing
  their element Attacks before they could react; a seat pin
  (`test_an_absorb_is_named_on_the_reaction_log`) prints a Melt row.

## Varka: the Oath rework (2026-09-29)

The paper (`review/active/varka-paper-kit-2026-09-28.md`, every pick ruled
2026-09-29) replaces batch one's Absorb and Winds with Oath: one count per
element, counted per card, read only for his current element (the last
Knight's). Forty-seven rows: Four Winds' Ascension (created by Boreas's Fang,
never in the deck), Windbound Execution and the four starter-only Knights
(one per run, rolled by the Fang), and the 41-card pool (16 / 17 / 8). The
ruled picks are on the rows: E-AoE (3 to ALL), Lisa 4 [5] Block plus 3 [4]
per Attack played this turn, Baron Bunny 6 [8] Block now and 6 [8] Pyro to
ALL next turn, Favonian Standard 4 [5], Dawn Wind's March 3, Northwind Avatar
cost 2 at 10 [14] and 10 [14] plus 2 per Oath. Built in both engines
(`Powers/Prototype/VarkaOath.cs`, `tier0/engine/varka_oath.py`).

The grammar gained one verb, `{op: varka, kind: ...}` (`gen_klee_cards.VARKA_KINDS`),
three runtime counts (`current_oath`, `oath_elements`,
`attacks_played_this_turn`) and two predicates (`has_current_element`,
`knight_played_this_turn`). Knights' Muster, `knight_aura`, `winds_held`,
`holds_wind` and the `absorb` tag are gone.

Readings taken where the paper is silent:

- A Knight is any Companion row in his personal pool; it sets his current
  element before its own effects resolve, so its application credits the new
  element. Jean — Wind Companion is a Skill, not a Knight (titled with a
  colon until the open-Oath round, 2026-10-01).
- Credit is per card play: the first application of an element and the first
  Swirl of an element each give 1, separately; a Swirl's spread and a
  Converging Winds spread reaction give nothing; an event outside a play
  (Baron Bunny's burst, a Power's hit) credits on its own, and the burst is one
  scope, so at most 1 Pyro Oath.
- Favonian Standard pays when the Knight's element was already current (the
  first Knight of a fight never pays); Boreas Unbound pays on any change,
  none to an element included, and Change of Guard counts.
- Dawn Wind's March pays once per gain event of the current element; Rally
  to the Banner is not a gain.
- The Swirl payout's damage is element-less and unpowered (the target's
  Vulnerable counts); Storm Surge's extra 5 and the Ascension and Northwind
  follow-up hits are the card's, so his Strength counts.
- Eula counts enemies wearing Cryo, fresh or spent, after her hit, as one gain.
- Stacked Baron Bunnies go off as one burst of the summed amount.
- Change of Guard asks on a grid only when he holds Oath in two or more
  elements; with one it takes that one.
- The starter Knight: the deck lists Amber: Precise Shot, and Boreas's Fang
  transforms it on a new run off the player's Transformations stream.
- Stormward Stance prints "additional damage", the base game's template.
- No new art: the new rows take no `art_of` (a proxy must be the same card
  under another id) and Change of Guard's faces wear the Mondstadt Universals'
  starter-Knight illustrations.

## Kokomi: the feed pass (2026-09-29)

[USER], 2026-09-29, after an act-1 death: "her cards are weirdly 'expensive'";
"I spent all of my energy staying alive or tossing debuffs on via plan"; "I
feel like some Plan cards need to go to 0 cost so there's some way to draft
lower-impact feed for the Plan mechanism. Let's not make too many 'do a thing
now AND get a plan going' cards - those should be higher rarity at least."
Designed in the main session; the quotes and the change table are in the brief
(`review/active/kokomi-brief-2026-09-01.md`, sec. 6, "The feed pass").

- Five new rows, last in the sheet's order and appended to
  `KokomiOverhaulRoster.Slice()` and `C.KOKOMI_OVERHAUL_POOL_IDS`:
  `proto_kk_bubble_ward` (Plan `block` 4, `plan_block: 2`), `proto_kk_nip`
  (Plan `damage` 5 at `front_enemy`, Ambush's aim, `plan_damage: 2`),
  `proto_kk_jellyfish_drift` (Plan `damage` 2 at `all_enemies`,
  `plan_damage: 1`), `proto_kk_current_read` (Plan `draw` 1 then `block` 0,
  `plan_block: 2`), `proto_kk_brine_sting` (Plan `apply_power weak` 1 at
  `front_enemy`, Coral Bulwark's old aim, `plan_power_amount: 1`). Each is a
  cost-0 Common Skill with `effects: []`, Breakwater's shape, so codegen
  emits `KokomiTargets.PetOnly` and leads the face with "Play on the
  Bake-Kurage."; none is a Dusk Plan.
- Current Read's upgrade ADDS "Gain 2 Block". No upgrade key adds a Plan
  clause, so the clause is written at 0 and the face prints it under
  `{IfUpgraded:show:...}`. The flat `block` joins `block_front_intent` in
  `PLAN_ZERO_AMOUNT_OPS` in both engines (`tools/gen_klee_cards.py`,
  `tier0/engine/kokomi_plan.py`), and a 0 flat Plan Block is carried out as
  nothing (`KokomiPlan` `Kind.Block`, `kokomi_plan._resolve_clause`): the
  Block path is powered, so without the guard Dexterity would have turned the
  unprinted 0 into Block.
- Common to Uncommon, nothing else moved: `proto_kk_ambush`,
  `proto_kk_read_the_field`, `proto_kk_stolen_chapter`, `proto_kk_riptide`,
  `proto_kk_pincer`, `proto_kk_feigned_retreat`, `proto_kk_signal_arrow`,
  `proto_kk_surging_shoal`.
- `proto_kk_coral_bulwark`: `block` 7 to 8, the `plan:` line removed, the
  upgrade is `block: 3` (11). Still Common.
- `proto_kk_exposed_flank`: cut. Tombstoned in `docs/retired-card-ids.yaml`
  (retired alias generated), kept as a known-stale portrait in
  `tools/art_coverage.py`. It spelled no engine piece of its own.
- Art: five `art/plan.tsv` rows (`kokomi_pool`, splash, shortlist rank 1) on
  official Kokomi art no other row claims: Birthday 2024 (Bubble Ward), the
  version 3.0 App Store wallpaper (Nip), Birthday 2026 (Jellyfish Drift),
  Birthday 2025 (Current Read) and Birthday 2022 (Brine Sting). The teaser
  wallpaper was Current Read's first pick; its wiki title carries double
  quotes, which a Windows raw filename cannot hold.

**The sim read (Prototype stage, not a measurement).** Priest pilot, 200
fights a cell, seeds 1000+, the arm on, the Casket held. The stock pilot never
plays Open the Casket, so a wrapper opened it the first time the Casket held
6, or from turn 6 if it held any; the "held" columns never open it and read the
count at the start of turns 3, 5 and 8. Package = the starter plus Feint,
Ambush, Coral Bulwark, Shell Guard, Pearl Diver, Press the Advantage,
Driftglass, Deep Current; feed4 adds Nip, Bubble Ward, Jellyfish Drift,
Current Read; feed8 adds two of each. The starter is unchanged, so its rows
match before and after exactly.

| deck | enc | win % before / after | HP lost | turns | Plans/turn | Casket at Open mean / p90 / max | held, turn 8 mean / p90 |
|---|---|---|---|---|---|---|---|
| package | tank_boss | 84 / 80 | 66.2 / 67.6 | 15.0 / 15.2 | 0.32 / 0.28 | 2.1/3/5 → 1.9/3/5 | 1.9/3 → 1.7/3 |
| package | punisher | 78 / 83 | 70.7 / 68.8 | 10.3 / 10.3 | 0 / 0 | never opened | 0 |
| package | attrition | 100 / 100 | 13.2 / 13.2 | 10.8 / 11.1 | 0.61 / 0.54 | 3.1/5/7 → 2.7/4/6 | 4.1/6 → 3.6/5 |
| package+feed4 | tank_boss | – / 100 | – / 41.3 | – / 11.0 | – / 1.04 | 5.6 / 7 / 9 | 7.5 / 9 |
| package+feed4 | punisher | – / 100 | – / 27.9 | – / 7.1 | – / 0.82 | 4.6 / 6 / 6 | 6.3 / 8 |
| package+feed4 | attrition | – / 100 | – / 11.5 | – / 9.0 | – / 1.20 | 5.9 / 7 / 9 | 8.7 / 11 |
| package+feed8 | tank_boss | – / 100 | – / 32.8 | – / 9.8 | – / 1.61 | 6.7 / 8 / 10 | 12.0 / 14 |
| package+feed8 | punisher | – / 100 | – / 21.1 | – / 6.4 | – / 1.41 | 6.7 / 8 / 9 | 11.3 / 13 |
| package+feed8 | attrition | – / 100 | – / 11.7 | – / 8.0 | – / 1.67 | 6.7 / 8 / 9 | 12.8 / 15 |

No turn-3 kill on tank_boss in any cell. The one runaway flag: a feed8 deck
that never opens the Casket holds 13 to 15 at the 90th percentile by turn 8.
The pilot writes no Plan at all against punisher with the package deck, before
or after, which is the pilot and not the pass.

**Pool:** 48 offered (20 Common, 23 Uncommon, 5 Rare) plus the three co-op
cards.

## Kokomi: expansion batch one (2026-09-29)

Paper `review/ruled/kokomi-expansion-2026-09-29.md`, every pick ruled at
the default ([USER]: "The defaults work here"). 22 rows, LAST in the sheet's
order (`C.KOKOMI_EXPANSION_BATCH_ONE_IDS`, `KokomiOverhaulRoster.Slice()`):
12 Uncommon and 10 Rare. The Clouds Like Waves Rippling is cut
(tombstoned in `docs/retired-card-ids.yaml`, a known-stale portrait in
`tools/art_coverage.py`); its power (`CloudsLikeWavesPower`,
`kk_clouds_like_waves`) and the one event it read ("she applied a debuff to an
enemy": `KokomiOverhaulKit.IsHerDebuffOnEnemy`, `kokomi_plan.note_debuff_applied`)
left both engines with it, since nothing else read them. The pool is 69
(20 / 35 / 14) plus the three co-op cards. No art: the rows have no
portrait yet.

**Engine pieces, both engines (twins named on each).**
- A Plan entry records the Energy paid for the card that wrote it
  (`PlanEntry.paid`, `KokomiPlan.Entry.Paid`, from
  `cardPlay.Resources.EnergySpent`; the generated `Schedule` call passes it).
  The runtime count `plan_energy_waiting` (`KokomiPlan.EnergyWaiting`) sums
  it over the queue.
- Four plan clauses: `energy_if_alone` (Lull), `damage_if_alone` (Undertide
  Lance; folds her Strength like any planned hit), `block_per_attacking_enemy`
  (Evening Watch), `double_block` (Brace for the Tide).
- One now-line op, `kokomi`, with six kinds (Varka's shape): Measured Breath,
  Salt in the Wound, Tidal Resonance, Suffocating Deep, All Streams Flow to
  the Sea, Shoal Call (`KokomiCards` in `Powers/Prototype/KokomiExpansion.cs`).
- Seven Powers: Grand Design, The Long Game, At Water's Edge, Ceremonial
  Garment (`ProtoCeremonialGarmentPower`; the shipped kit already has a
  `CeremonialGarmentPower`), Watatsumi's Grace, Tidal Riposte, Kurage Swarm.
  Two new mirrored constants: `KokomiOverhaulLaw.GrandDesignMinCost` (2) and
  `LongGameWaiting` (1).

**Readings where the paper is loose (the build's, for a ruling if any is
wrong).**
- *The Energy paid for the Plans waiting*: the sum of the costs actually paid
  (after reductions) for each Plan in the queue; an X cost counts what was
  paid. A card made free by Stolen Chapter adds 0.
- *Only Plan carried out this morning* (Lull, Undertide Lance): no OTHER entry
  in the same drain. The same entry carried out twice (Nereid's Ascension,
  Second Wave, All Streams) is still one Plan; Dusk Plans drain on their own
  and never count against a morning; a Plan hurried by Change of Plans is a
  drain of one, so it counts as alone.
- *Debuff* (Drowning Pressure, Ceremonial Garment): each DISTINCT debuff power
  on the target (Weak 2 is one). Elemental auras are NOT debuffs: both engines
  model an aura as a Buff (`AuraPower.Type`, `kokomi_plan.ENEMY_DEBUFFS`), so
  they do not count. Frozen does.
- *At Water's Edge*: any reaction on an enemy, whoever caused it (every
  player wearing the Power answers, off the one reaction site).
- *Tidal Riposte*: a hit of an enemy's attack that Block absorbed whole
  (Block took some, 0 HP lost), once per hit; 5 Hydro to the attacker,
  unpowered.
- *Watatsumi's Grace*: the base game's Sturdy Clamp shape. The Block clear is
  prevented, then everything above the cap is lost (so 10 kept of 40).
  Barricade, if also worn, keeps all.
- *All Streams Flow to the Sea*: cancelled Plans refund nothing and their
  cards stay where a written card already is (the discard pile, or the
  exhaust pile for an Exhaust row). "Your next Plan this turn" is the next
  card written on the Bake-Kurage this turn; its entry is carried out once
  plus once per Plan cancelled (0 cancelled is still taken). The gift dies at
  the turn's end. Change of Plans honours it too.
- *Shoal Call*: the Nips go to the hand, upgraded if Shoal Call is (the
  `upgraded_grant` key, the face's own swap).
- *Kurage Swarm*: counts when a Plan is WRITTEN whose paid cost was 0.
- *Grand Design*: "cost 2 or more" is the Energy paid for the Plan's card, per
  carry-out (a doubled Plan pays twice). It does not need the relic.
- *The Long Game*: the queue read before the morning drains it (Moon Signal's
  read).

**Faces changed from the paper's wording, by house text rules only.**
- Lull and Undertide Lance print "at the start of your turn" for "this
  morning" (`EB-623`: no printed surface says "morning").
- All Streams Flow to the Sea drops "their cards go to your discard pile"
  (the face was 140 of the 120 ceiling; the cards are already there) and
  reads "carried out once more for each Plan cancelled".
- At Water's Edge prints "[gold]Elemental Reaction[/gold]" and Ceremonial
  Garment "additional damage" (the text lint's spellings). Tidal Riposte's
  "fully blocked" is plain text (no tip defines a golded "Blocked").

**Upgrades the paper leaves open.** Five rows printed no bracketed upgrade (Grand Design has since been given cost 0, below).
The others take the Prototype-stage rule's default, as every unruled row does:
Tidal Resonance and
Coral Crash (each also draws 1). Brace for the Tide's default would have
removed Exhaust, which paper sec.4 guard 2 rules out ("the multiplier is
spent"), so it costs 0 instead -- flagged in the build PR for a ruling.

**The sim read (paper sec.5; Prototype stage, not a measurement).**
`python -m tools.kokomi_expansion_sim --seeds 400 --seed 7 --jobs 14`, on the
built rows, modelled on the Varka Oath report: a stylised act 1 (N N N N E R N
N E R B) and an act-2 boss, paired seeds, the stock `priest` play pilot with a
harness wrapper (Open the Casket at 6, Powers first, Dusk Plans written into
an attack, the new clauses valued as their nearest stock op). Drafters: the
four decks (sec.3 grouping plus the sec.1 parts, then the default drafter's
own score) and the default drafter as the baseline.
- Every pilot loses the stylised act at the first elite (act won 0.0 to
  0.2%; about 15 HP lost per fight), so the deck read is a full-deck gauntlet:
  the nine picks drafted as if every fight were won, then every act-1 elite,
  act-1 boss and act-2 boss at full HP. Fights won: Plan volume 58.1%, the
  default drafter 52.5, Tide Control 52.2, Dusk Guard 49.5, Big Plan 49.1
  (about ±1.9); none more than 10 points behind Plan volume. Every act-2 boss
  is lost by every pilot.
- Grand Design granted: Big Plan 45.6% against Plan volume 54.6% -- the Big
  Plan deck does not beat volume with the relic and the Rare in hand.
- Dusk Guard with Grace and Coral Crash granted: 0.1% of turns end with more
  than 30 Block, and 9.8% of its gauntlet fights pass turn 15 (others about
  1%), won 40.0%: long on too little damage, not on a wall.
- Flags: Undertide Lance dominant (the default drafter takes 83% of its
  offers, 1.57 plays per fight held); All Streams Flow to the Sea dead (0
  plays in 252 fights held -- the harness rule to play it never meets its
  condition, a pilot limit as much as a card one). Tidal Resonance sits at
  0.31 plays per fight, on the line.

**The main session's round (2026-09-29), on the sim above.** Brace for the
Tide+ at cost 0 keeping Exhaust is accepted as built. Undertide Lance goes to
6 [9] to ALL, Plan 12 [16] (it read dominant). Grand Design becomes "the
Casket gains 1 more for each Energy paid for it", cost 1 [0] (an authored
upgrade; it failed check 2). The harness now plays All Streams when 1+ Plan
waits and a Plan card costing 1+ is affordable after it, then writes that
card (the example rule's 2+ needs 4 Energy and never fired), and gives the
default drafter's zero-priced new rows (the seven Powers, Shoal Call) the
median default score of the other new cards. Re-run, same command:
- Gauntlet fights won: Plan volume 57.8%, Tide Control 51.5, the default
  drafter 50.1, Dusk Guard 48.4, Big Plan 47.7 -- Big Plan now 10.1 behind.
  The stylised act is still lost at the first elite (0 to 0.2%).
- Grand Design granted: Big Plan 47.1% against Plan volume 56.1%; the Casket
  at fight end 3.4 against 4.6. Check 2 still fails.
- Undertide Lance: still taken from 83% of the default drafter's offers,
  1.13 plays per fight held; no longer flagged. All Streams: 2 plays in 252
  fights held -- still dead. It needs a Plan waiting mid-turn (the queue
  drains each morning) and 3 Energy after that write, which a 3-Energy turn
  meets only after a 0-cost write.

**All Streams Flow to the Sea, the main session's last change (2026-09-29).**
Cost 1 [0], "Cancel all your Plans and regain their cost" -- the Energy
actually paid, Second Thoughts' refund -- "Your next Plan this turn is carried
out once more for each Plan cancelled." It was dead because a cancelled
Plan's Energy was lost (2 plays in 252 fights). The harness plays it with 2+
Plans waiting and a Plan card affordable after the refund, then writes the
most expensive such card. Re-run: 7 plays in 252 fights held (0.03 per fight,
still flagged dead); each play cancelled 2 Plans, regained 2 Energy and
carried its next Plan out 3.9 times on average (Bubble Ward, Feigned Retreat,
Undercurrent Snare, Feint, Slack Water, Jellyfish Drift). Big Plan's
gauntlet is unchanged at 47.7%. The limit is the stock pilot, which writes
its Plans one at a time and rarely holds a Plan card once two wait.


## Varka: co-op playtest 2026-09-30

[USER]'s co-op run, decided by the main session. Three changes, no other card
moved (Knights' Roll Call stays as is, no Exhaust).

1. **Tailwind Stride.** [USER]: "'Tailwind Stride' sounds like 'draw 3' at 1
   energy and the upgrade makes it free? Way too good!" Base is unchanged
   (cost 1, draw 2, draw 1 more with a current element). The upgrade no longer
   cuts the cost; it raises the conditional draw to 2 (draw 2, plus 2 more with
   a current element). Built with a new delta key `conditional_draw`, which
   moves the draws inside a conditional's arms and leaves the top-level draw
   alone (`draw` bumps all of them). Both engines: `tier0/content/upgrades.py`
   and `tools/gen_klee_cards.py` (the `DrawThen` var, diff-highlighted).
2. **Rising Gale** Common to Uncommon. [USER]: "'Rising Gale' is basically a
   cycling card with a clause - may need a bump to Uncommon". Pool is now
   15 / 18 / 8.
3. **Upgrades for the six cards that had none.** [USER]: "A few cards on Varka
   are missing upgrades"; in the run, upgraded copies did nothing. Oath of the
   Knights, Rally to the Banner, Change of Guard and Four Winds' Accord cost
   1 to 0; Unfurled Banner gains Retain; Azure Devour 4 to 5 damage per Oath
   (`formula_per: 1`).

## Varka: the open Oath (2026-09-30)

[USER] asked: "Is it reasonable to go the other direction and say 'Any card
that applies an element other than Anemo counts for Oath effects' - widening
the Companion pool", and on the main session's terms: "Yep, let's ship it and
see if anything breaks."

The rule: whenever he plays a card that applies Pyro, Hydro, Cryo or Electro,
that becomes his current element and he gains 1 Oath of it. The four terms:

1. **His own card plays only.** A Swirl's spread, a reaction's side effects,
   relics, potions, a Power ticking later (Baron Bunny's burst) and another
   player's cards in co-op do not switch it.
2. **The four Oath elements only.** Anemo and Geo give nothing and do not
   change the current element.
3. **Knight-named payoffs stay Knight-only.** Favonian Standard, Grand
   Master's Order, Knightly Guard ("if you played a Knight"), Knights' Roll
   Call and the starter Knight are unchanged; `VarkaRules.IsKnight` is.
4. **Favonius Drill counts, to watch.** It gains 1 Oath of the current
   element per play.

How it is built. The Oath part already stood: since the rework every card of
his that applies an Oath element gained 1 of it per play (sec.3's credit,
`VarkaOathLedger.TryCredit`, `varka_oath.credit`), Knight or not. What the open
Oath adds is the switch. A play of his card that is not a Knight opens an
open-Oath scope (`VarkaOathLedger.OpenScope(open: true, card)`, sim
`open_scope(open_oath=True)`); an application inside it of an Oath element
first makes that element current (`SetCurrent(knight: false)`, so Boreas
Unbound pays on a change and Favonian Standard never does), then credits, so
the gain is the current element's and Dawn Wind's March pays. The last element
applied wins; each element still credits its own 1 (sec.3's per-element
credit is unchanged). In the mod the hit must be dealt by him and, when it
names a card, by the card being played (`OpenOathSwitches`); Four Winds'
Ascension's no-credit hit switches nothing. Knights keep their switch at the
top of the play. The tips: "current element" now reads "The last Pyro, Hydro,
Cryo or Electro you applied" (the tip ceiling is 135; the Knight tip still
says playing one makes its element current), and the Knight tip drops
"others do not". The sim's
`varka_oath.OPEN_OATH` (on) runs the old rule for a paired comparison.

The paired sim (scratch harness, not committed; tier0 with `VARKA_OATH` on,
generic pilot, every tier0 encounter in turn, n = 400 fights per cell on
paired seeds 0 to 399). "pool" is the starter plus Favonius Drill, Oathsworn
Strike, Eye of the Storm and Knightly Guard; "comp" adds 4 random Companions
from the three nations' shipped sheets that apply an Oath element.

| deck | start | won old / new | Oath per fight old / new | switches per fight old / new | HP lost old / new |
|---|---|---|---|---|---|
| pool | Pyro | 99.8 / 99.8 | 5.64 / 5.64 | 0.98 / 0.98 | 22.5 / 22.5 |
| pool | Hydro | 99.2 / 99.2 | 5.81 / 5.81 | 0.98 / 0.98 | 21.3 / 21.3 |
| pool | Electro | 99.8 / 99.8 | 5.55 / 5.55 | 0.98 / 0.98 | 22.3 / 22.3 |
| pool | Cryo | 99.8 / 99.8 | 5.33 / 5.33 | 0.98 / 0.98 | 20.9 / 20.9 |
| comp | Pyro | 98.8 / 99.5 | 7.18 / 7.13 | 0.88 / 3.79 | 21.3 / 19.9 |
| comp | Hydro | 99.5 / 98.8 | 7.36 / 7.26 | 0.89 / 3.90 | 20.8 / 20.4 |
| comp | Electro | 99.8 / 100.0 | 6.90 / 6.90 | 0.87 / 3.38 | 19.9 / 19.1 |
| comp | Cryo | 100.0 / 99.8 | 6.93 / 6.94 | 0.88 / 3.72 | 19.9 / 19.8 |

On his own pool nothing moves: every non-Knight card of his that applies an
Oath element applies the current one. With Companions in the deck he switches
about four times as often and Oath per fight is unchanged (the credit already
stood); fights won move within noise and HP lost falls by 0.1 to 1.4. The
tier0 encounters are near 100% won, so this shows nothing breaks, not a
balance number.

### The open-Oath round's changes (2026-10-01)

The round (`review/records/varka-open-oath-round-2026-10-01.md`, "What to
change" 1 to 3, the main session's design):

1. **Change of Guard** is cost 0 with no Exhaust: "Choose an element you have
   Oath in. It becomes your current element. Draw 1 card." Upgraded it draws
   2 (this replaces the cost-0 upgrade from the co-op playtest). The Block
   equal to its Oath is gone. The draw is the row's own `draw` op, after the
   switch, so it draws with no Oath too. Lane 1 named the old card NEVER
   AGAIN in acts 1 and 2: "one card slot for 2 to 5 block and a switch I
   never needed".
2. **The rule text says the open rule.** The seat page's Oath block reads
   "Current element: none. Set by the last Pyro, Hydro, Cryo or Electro you
   applied." and "Your Swirls pay nothing until you apply Pyro, Hydro, Cryo
   or Electro." (was "Play a Knight to set it"). Jean's Varka card is
   "Jean — Wind Companion": the em dash the other Companions use, so the
   colon means Knight (Grand Master's Order+ fizzled on it in the round).
3. **The Swirl tip** reads "Anemo meets a fresh aura: deal 2 damage to ALL
   enemies and copy it, spent, onto the others. Enemies already wearing it
   are refreshed." on the keyword tip, the reaction preview and the seat
   page (two seats misread "old ones refresh").

## Power cost sweep, 2026-09-30

[USER]: "my friend and I both noticed that you have a convention of making
rare powers cost 2 energy with the upgrade putting them to 1. And having
uncommon powers cost 1 going to 0. It works! But can we do a sweep over the
current card pools and break them up a bit so it's less of a standard? Alter
the effects to rebalance at a different energy level, basically (either the
higher or the lower)". The main session chose eighteen changes; every other
Power keeps its cost and upgrade (Aftershock, Vermillion Pact, Knights of
Favonius, At Water's Edge, Arkhe Alignment, Sold Out, Converging Winds and
Dawn Wind's March stay 2 to 1, Full House 3 to 2, every companion row as is).

| Card | Was | Now |
|---|---|---|
| Sparks 'n' Splash | 2, upgrade cost 1 | 3, upgrade Innate |
| Dodoco | 2, Mine 4, upgrade cost 1 | 1, Mine 3, upgrade Mine 5 |
| Second Surprise | 1, upgrade cost 0 | 0, upgrade Innate |
| Nereid's Ascension | 2, upgrade cost 1 | 3, upgrade Innate |
| Moon Signal | 1, upgrade cost 0 | 0, upgrade Casket gains 2 |
| Grand Design | 1, upgrade cost 0 | 1, upgrade Innate |
| The Long Game | 1, upgrade cost 0 | 1, upgrade gain 1 Energy and draw 1 card |
| Kurage Swarm | 2, upgrade cost 1 | 1, upgrade Innate |
| A Five-Century Act | 2, returns at 1, upgrade cost 1 | 3, upgrade returns at 3 |
| Revolving Stage | 1, upgrade cost 0 | 0, upgrade Innate |
| Star Billing | 1, draw 2, upgrade cost 0 | 1, upgrade draw 3 |
| Regina of All Waters | 2, upgrade cost 1 | 1, upgrade Innate |
| One-Woman Show | 2, Energy 1 and draw 1, upgrade cost 1 | 3, Energy 1 and draw 2, upgrade cost 2 |
| The Crowd Roars | 2, Fanfare 1, upgrade cost 1 | 1, upgrade Fanfare 2 |
| Stormward Stance | 1, 3 damage, upgrade cost 0 | 1, upgrade 5 damage |
| Oath of the Knights | 1, upgrade cost 0 | 1, upgrade Innate |
| Boreas Unbound | 2, upgrade cost 1 | 3, upgrade Innate |
| Sworn Brotherhood | 2, Oath of every element, upgrade cost 1 | 1, Oath of your current element; upgrade every element |

How the two upgrades with no existing key were built: a new delta key
`upgraded_power: <power>`, a play-time `IsUpgraded` swap of the power the
card installs (codegen `gen_klee_cards.upgraded_power_effect`; sim
`tier0/content/upgrades.py` rewrites the effect's `power`). The Long Game+
installs `TheLongGamePlusPower` (`kk_the_long_game_plus`), paid by the same
`TheLongGamePower.Signal`; Sworn Brotherhood's base installs
`SwornBrotherhoodCurrentPower` (`vk_sworn_brotherhood_current`) and the
upgrade installs the old every-element power. A Five-Century Act's returnee
now arrives at the power's amount (`FurinaStage.ReturnFanfare`; sim
`furina_stage._after_bow`), and One-Woman Show draws 2 a copy.


## Orobas upgrades for Varka and Kokomi, 2026-09-30

[USER]'s co-op playtest: "Varka and Kokomi need Ancient relics for Orobas".
Touch of Orobas upgrades the starter through BaseLib's
`GetUpgradeReplacement()`, and neither Boreas's Fang nor the Tamakushi Casket
overrode it, so both became the no-effect Circlet. Main-session design, built
as given:

1. **Wolf's Gravestone** (Boreas's Fang upgraded): "The first time each combat
   you gain Oath, add an upgraded Four Winds' Ascension to your hand. It costs
   0 this turn." Same trigger as the Fang; the card comes upgraded and free
   this turn.
2. **Watatsumi Casket** (Tamakushi Casket upgraded): identical to the Tamakushi
   Casket in every way, except the Casket starts each combat with 3.

Both are Ancient rarity, members of their character's relic pool (so
`RelicModel.Pool` resolves at the grant) and never rolled. Each SUBCLASSES its
starter (`klee-mod/KleeCode/Relics/BoreasFang.cs`, `TamakushiCasket.cs`), so
the game's `GetRelic<T>` (an `is T` test) finds the upgrade wherever the
starter is looked up: the Oath rule's `BoreasFang.HeldBy`, the Casket's
carry-out add and its counter. The Casket cards (Shell Guard, Driftglass,
Depths' Judgment, What the Tokoyo Took, Open the Casket, Kurage Swarm, Grand
Design) read the count off `KokomiOverhaulLedger`, never the relic, so the
opening 3 (seeded at `BeforeCombatStart`) reaches every one. Icons are each
starter's own. Sim: tier0 already modelled the upgraded Fang
(`varka_oath.FANG_UPGRADED`) and now makes its Ascension free this turn; the
Casket's opening count has no sim twin, and neither upgrade has a tier05
Orobas row (curated in `tier0/tests/test_starter_relic_upgrades.py`) until the
kits reach Balance.

**Riptide's Plan draw (2026-09-30, ruled).** After the co-op playtest in which
a guest played Kokomi, [USER]: "Riptide - buff the Draw from 1 to 2, and
upgrades to 3; seems a bit weak at 2 energy". `proto_kk_riptide`'s Plan line
is now "Gain 2 Energy and draw 2 cards", and the upgrade raises the draw to 3
through the existing `plan_draw` key (the Plan line's first `draw` clause in
both engines; the codegen emits it as the `PlanCards` var). The now-line's
upgrade (14, 4 more on a debuffed enemy) and the Plan's 2 Energy do not move.

**Kokomi follow-ups, 2026-10-01.** Two follow-ups from PR #777's co-op fixes.
(1) A cancel is an undo (main session): a cancelled Plan's card returns to the
hand, even an Exhaust card; Exhaust applies when the card is played or its Plan
carried out, not when it is cancelled. Second Thoughts and All Streams Flow to
the Sea both give back through `KokomiPlan.GiveBack` / `kokomi_plan._give_back`
(discard, then exhaust, then draw pile); a Moon's Reflection Plan gives back
Moon's Reflection, never the card it found. All Streams now reads "Cancel all
your Plans and take their cards back. Your next Plan this turn is
carried out once more for each." It no longer refunds Energy (main session,
later 2026-10-01): with the cards returned, a refund made re-writing the
biggest Plan free (Masterstroke carried out 4 times at no net Energy). Loop
check: no loop, since both cancels Exhaust, so each copy returns cards once;
All Streams is stronger (a full undo plus its gift). The retired Ebb Tide op
still returns nothing. (2) A card Moon's Reflection replays at the morning (and
Crystal Collapse's copy) kept its Hydro a turn short; the morning drain now
opens `AuraPower.MorningWindow`, which spares every aura applied or refreshed
inside it. The sim ticks auras before the morning and needs nothing.

## Varka relics and potions, 2026-10-01

Built from `review/ruled/varka-expansion-2026-10-01.md` sec.4 at the
defaults of its picks, ruled 2026-10-01 ([USER]: "Agreed on all four. You're
good to proceed."). Seven relics (`klee-mod/KleeCode/Relics/VarkaArmRelics.cs`) and
three potions (`klee-mod/KleeCode/Potions/VarkaPotions.cs`), Klee's and
Furina's shape and build: each relic is a member of `VarkaRelicPool`, and the
pool's offer (`GetUnlockedRelics`, through `ArmRelicPools.Offer`) is Boreas's
Fang, the seven and Wolf's Gravestone, so the Silent borrow is no longer
offered (pick 1, default (a)). His `PotionPool` is `VarkaPotionPool` with the
arm live. **Pick 1(b)** (the borrow kept beside them) is one constant,
`VarkaArmRelics.KeepSilentBorrow`: true offers every relic member and appends
the Silent's potions to his pool. The Silent relics stay members (through
`InheritedSilentRelics.Curated()`), so the curation pins and self-check R21
read his pool as before.

| Tier | Relic | As built |
|---|---|---|
| Common | Knight's Commission | "At the start of each combat, gain 2 Oath in your starting Knight's element." His first turn, after the draw: 2 Oath of the starter Knight's element the run rolled, through `VarkaOath.Gain` (so the Fang answers it). It sets no element: the Fang does (re-aimed from "becomes your current element, with 1 Oath", main session, 2026-10-01). The Fang records that element when it rolls the Knight (`Relics/VarkaStarterKnight.cs`, a BaseLib `SavedSpireField` saved with the Fang and copied to Wolf's Gravestone), so it holds all run after the card is removed or transformed (main session, 2026-10-01). A run begun before the record existed falls back to the starter Knight in the deck. |
| Uncommon | Windblume Garland | 4 Block a copy on every current-element change, paid in `VarkaOath.SetCurrent`; the fight's first element (none to one) is a change, as Boreas Unbound counts it. |
| Uncommon | Dandelion Seeds | Late in his turn start (after Knight's Commission and his turn-start Powers): with a current element and no enemy wearing an aura (a spent aura counts as one), applies it to a random enemy. No Oath, no switch. |
| Rare | Banner of the West Wind | On a change, every point of the old element's Oath moves to the new one (`VarkaOathLedger.MoveOath`), before the Garland and Boreas Unbound pay. A move, not a gain. |
| Rare | Stormterror's Scale | `VarkaOath.OnSwirl`'s current-element payout runs 1 + copies times; the Swirl's Oath credit and the shared Swirl damage do not repeat. |
| Rare | Andrius's Howl | Each Four Winds' Ascension he plays is noted; at his next turn start, after the draw, each noted copy still in his draw or discard pile returns to hand, once per copy per turn. A copy already drawn stays; an exhausted one does not return. |
| Shop | Favonius Duty Roster | His first turn, after the draw: Knights' Roll Call's unchosen add (`VarkaRules.AddKnight`), a random pool Knight (never a starter-only one), costing 0 this turn. No new helper was written. |

| Tier | Potion | As built |
|---|---|---|
| Common | Bottled Resolve | Change of Guard's grid over all four elements; the pick becomes current, then 3 Oath of it. |
| Uncommon | Bottled Gale | Wall of Gales' sweep (`VarkaRules.SwirlFreshAuras`). The Swirls pay his current element but credit no Oath. |
| Rare | Elixir of the Four Winds | For the round drunk, `VarkaOathLedger.CurrentOath` (every card read of his current element's Oath) answers the total of all four; the badge shows it. |

**Relic and potion applications gain no Oath** (sec.4) and switch nothing:
Dandelion Seeds and Bottled Gale run inside the new `VarkaOath.NoCredit`
scope, which suppresses both the application credit and the Swirl credit.
Bottled Resolve sets his element and gains Oath, and Knight's Commission gains
Oath (it sets no element since its 2026-10-01 re-aim), because their faces say
so.

**Readings chosen where the draft left it open** (for the main session):
Bottled Gale's Swirls gain no Oath (read as "potion applications"); the
Scale stacks per copy, as Klee's relics do; the Elixir lasts the round (his
turn and the enemy turn after it); Andrius's Howl does not return a copy he
exhausted.

**Sim:** not mirrored. tier0 models no relic or potion of Klee's or Furina's
either; the three printed numbers are declared unmirrored in
`tools/lint_constant_parity.py` until Balance. **Art:** none fetched; each
relic reads `varka/relics/<slug>.png` and each potion `varka/potions/<slug>.png`
from the pack, with the base game's fallback icon and missing-potion picture
until an art pass adds them. Tests: `klee-mod/KleeTests/Prototype/VarkaRelicsPotionsTests.cs`.

## Kokomi payoff pass, 2026-10-01

The co-op player's complaint was "no payoff for playing lots of Plans" and
"short on block". On Second Thoughts the main session said it is "an undo
button, and an undo is a dead draw" and recommended cutting it in Kokomi's
next pass alongside a Plan-volume payoff that isn't damage; [USER]: "Sounds
good! Please proceed!" Built in both engines as given:

1. **Second Thoughts is cut** (`proto_kk_second_thoughts`, Common): out of the
   sheet, `C.KOKOMI_OVERHAUL_POOL_IDS` and `KokomiOverhaulRoster.Slice()`,
   tombstoned in `docs/retired-card-ids.yaml`, its painted portrait a
   known-stale entry in `tools/art_coverage.py`. Its cancel
   (`kokomi_plan.cancel_last_plan`, `KokomiPlan.CancelLast`) stays registered
   with no row spelling it, as Converging Tide's did; the give-back it shared
   with All Streams Flow to the Sea (`GiveBack` / `_give_back`) is All
   Streams' own door and is untouched.
2. **Kurage Canopy** (`proto_kk_kurage_canopy`, Power, 1, Uncommon):
   "Whenever the Bake-Kurage carries out a Plan, gain 2 Block." Upgraded 3
   (`power_amount: 1`), cost unchanged. `KurageCanopyPower` rides the plan
   bus (`IKokomiPlanListener`) beside her Ancient, which `ResolveEntry` rings
   once per carry-out, so a Plan carried out twice (Second Wave, Nereid's
   Ascension, All Streams' gift) pays twice. Powered Block (Dexterity counts),
   her Ancient's reading. Sim: `kokomi_plan.KURAGE_CANOPY` in
   `_note_plan_resolved`. Badge: her Ancient's (`princess_of_watatsumi.png`).
3. **Coral Tithe** (`proto_kk_coral_tithe`, Skill, 0, Uncommon): "Empty the
   Casket. Gain 1 Energy and draw 1 card for every 3 in it." Upgraded every 2
   (`kokomi_amount: -1`, a new `kokomi` kind `coral_tithe` whose `amount` is
   the divisor). Rounds down (7 pays 2, or 3 upgraded). The relic is found
   the way the Casket's own carry-out add finds it
   (`GetRelic<TamakushiCasket>`, which also finds the Orobas upgrade
   `WatatsumiCasket`; the sim's `_holds_casket`); without one the card does
   nothing and the count is not touched. The count itself is the ledger's,
   as every other Casket card reads it.

The pool is 70 (19 Common, 37 Uncommon, 14 Rare) plus the three co-op
cards. No art: neither new row has a portrait yet, so both render the
placeholder and `tools/art_coverage.py` bills them as missing, as expansion
batch one's 22 rows were. Pins: `tier0/tests/test_kokomi_payoff_pass.py`,
`KleeTests/Prototype/KokomiPayoffPassTests.cs`.

## Varka expansion, 2026-10-01

The paper `review/ruled/varka-expansion-2026-10-01.md`, all four picks at
the defaults; [USER]: "Agreed on all four. You're good to proceed." This
section is sec.3 (the cards); sec.4 (relics and potions) is "Varka relics and potions, 2026-10-01",
#787. Built in both engines as written, with the readings below where
a text left room. Pool 41 to 78 (20 Common, 35 Uncommon, 23 Rare), thirteen
pool Knights. Rows: the "VARKA, THE EXPANSION" block of
`docs/prototype-surface.yaml` (the five Knight-pass rows edited in place).
C#: `Powers/Prototype/VarkaOath.cs` (ledger counts, the play bracket, the
payout, twelve `VarkaCards` kinds), `VarkaPowers.cs` (fifteen Powers),
`VarkaRules.cs` (pool Knights, `AddRandomKnight`, `SpreadArrivesFresh`, the
optional element grid), `ReactionEffects.SwirlPays` (Downburst). Sim:
`tier0/engine/varka_oath.py`. Pins: `tier0/tests/test_varka_expansion.py`,
`KleeTests/Prototype/VarkaExpansionTests.cs`.

**Element of a plain hit.** The existing convention, kept: a fixed "Deal X
damage" Attack of his is Anemo (catalyst cadence: Knightly Strike, Shifting
Gale, Grand Master's Verdict, Downburst), and an Oath-formula Attack is
element-less (`applies_element: false`, as Oathsworn Strike and Azure
Devour: Four Banners, Charge of the Knights). A card that names its element
carries it (Blazing Charge Pyro, Thundering Verdict Electro, Tempest each of
the four), credits it like any hit of his and, under the open Oath, makes it
current. Cavalry Charge carries his current element, or is plain Anemo with
none.

**The new grammar.** Twelve `varka` kinds (`pathfinders_mark`,
`current_element_strike`, `blazing_charge`, `glacial_edict`,
`thundering_verdict`, `awakening`, `draw_per_enemy`, `cleanse`,
`apply_current_element_all`, `crosscurrent`, `double_current_oath`,
`tempest`); a kind names its target (`enemy` or `all_enemies`). Counts
`enemies_with_aura` (fresh or spent), `hydro_oath`,
`knights_played_this_combat`; predicates `target_has_pyro` (a snapshot at the
top of the play, fresh or spent) and `element_changed_this_turn` (none to an
element counts, as for Boreas Unbound). Upgrade key `varka_upgraded`. The
kinds' faces print their own `Vk*` numbers (Northwind Avatar's shape), so
Blazing Charge, Cavalry Charge, Thundering Verdict, Razor and Tempest preview
no Strength; Strength still lands (their hits are the card's own
`DamageCmd`).

**The Knight pass.**
- Diluc: "sets off a reaction" is any Elemental Reaction either hit sets off
  (`reaction_triggered_by_this`); 1 Energy once.
- Gleeful Songs: Block 5 [7]. Heart of the Abyss: the Vulnerable lands after
  the Cryo hit (its own hit is not amplified); the upgrade moves only the
  damage. Suppressive Barrage: Weak 2 [3], no Block.
- Razor: Awakening: one hit per enemy, 4 [6], plus 3 to each enemy wearing
  Electro (fresh or spent) before the first hit; stays a Skill.
- Amber: Sharpshooter (new, Common): an Attack, as the paper prints. "Already
  has Pyro" is read before her hit, so her own Pyro never turns it on; "deal
  it again" is a second hit of the same number, 8 [11] both.
- Barbara: Wellspring Hymn (new): in the printed order: the cleanse (Weak,
  Frail, Vulnerable; nothing else), the Block, the Hydro.
- Lisa: Pulsating Witch (new): "each enemy" is the living enemies after her
  Electro; Retain is the upgrade.
- Noelle: Steadfast Maid (new): a Geo Knight (`role_c: buffer`). She counts
  for every Knight-played read and Charge of the Knights; Geo keeps no Oath,
  so she sets no element, gains none, and Favonian Standard never pays on
  her. She is in the Roll Call / Order Answers / Duty Roster pool.

**Commons.** Pathfinder's Mark: one element for every target; with none it
rolls one of the four (`Rng.CombatTargets` / `state.rng`) and the open Oath
makes it current with 1 Oath (not under Unwavering Banner). West Wind Shield:
powered Block. Knightly Strike: "4 more" is a second hit (Counterclaim's
shape); tagged `strike`; the upgrade moves the 7.

**Uncommons.** Blazing Charge reads Pyro Oath before its hit. Tidal Bulwark
and Glacial Edict apply first and read their Oath after (their own point
counts); Glacial Edict's Weak and Vulnerable are each 1 + floor(Cryo / 4 [3]).
Static Field: any Electro application of his, a no-credit hit's too (and a
relic's), but not a Swirl's spread copy; once a turn; it draws on the spot.
Vow of the Blade draws with no current element too. Unwavering Banner stops
only the open Oath's switch: the application still credits its own element;
Knights, Change of Guard, Weathervane, Boreas's Fang and Bottled Resolve
still move it. Cycle of Seasons: element-less, unpowered, to ALL, after Boreas
Unbound. Eye Wall's 3 is a literal (the paper brackets only its 6 [8]),
unpowered, gone at the end of the turn. Pressure Front does nothing with no
current element. Crosscurrent: a Swirl on a spent aura pays nothing (Jean's
door); "pays twice" runs every payout of that Swirl twice and multiplies
with Stormterror's Scale; the upgrade adds "Draw 1 card". Assembly at the
Cathedral: once per Knight play, Grand Master's Order's replays included,
after the play resolves, to a random enemy, element-less and unpowered.

**Rares.** Wildfire Oath: while the current element is Pyro, the Pyro payout
is 3 + (stacks x Pyro Oath) to ALL enemies instead of 3 to one. Absolute
Zero: while current is Cryo, the Cryo payout is 1 Vulnerable and 1 Weak to
ALL. Neither widens a payout Twin Gales pays under another current element.
Unbroken Tide: Barricade's hook, read at the start-of-turn clear. Thundering
Verdict reads Electro Oath once, before its hits; one credit for the card.
Oath Unto Death: the extra point is inside the same gain, so Dawn Wind's
March pays once; Grand Master's Verdict's doubling is a gain and takes it.
Grand Master's Verdict: the Anemo hit, then a gain equal to the current
element's Oath; nothing to double with none. Wolfpack: after the Ascension
resolves, one copy per stack into the discard pile, upgraded if it was.
Oathbound Aegis: at his turn's end, unpowered, min(total Oath, cap); a second
copy adds its cap. Weathervane: first at the start of his turn (before Baron
Bunny, Sworn Brotherhood and Oath of the Knights); C# opens Change of Guard's
element grid, cancelable for "may", and asks nothing when he holds no Oath or
only the current element's; the sim pilot keeps the current element unless
another holds more. Tempest of the Four Winds: four hits in the printed
order, each crediting its element; reactions between them happen (Pyro then
Hydro vaporizes); Electro, last, wins the open Oath. Twin Gales: the current
element pays, then the Swirled one, once when they are the same, alone with
no current element. Downburst (pick 3a): the card is the marker; its Swirl's
spread copies arrive fresh; Converging Winds still replaces the spread. Eye
of Stormterror: the first three Swirls each turn draw 1 per stack. Charge of
the Knights: Knights played this combat, replays and Noelle included. The
Order Answers: last at the start of turn, a random pool Knight at its own
cost, one per stack.

**Shape, and what is unfinished.** Pathfinder's Mark+ ("ALL enemies") answers a live
TargetType, AllEnemies once upgraded (Coven Errand's shape, the codegen's
`VARKA_UPGRADE_WIDENS`), so it asks for no target. The element kinds
(Razor's Awakening, Blazing Charge, Thundering Verdict, Tempest) carry no
"Applies <element>" keyword tip, which the codegen derives only from
`damage` and `apply_aura` ops (BACKLOG). Weathervane's turn-start grid is
untried through the bridge and in co-op (BACKLOG).

**Art.** None of the 37 rows has a portrait: each renders the placeholder and
`tools/art_coverage.py` bills it as missing, as Kokomi's expansion rows were.
The fifteen Powers borrow the existing varka power badges
(`KleePowerIcons`: an element Power its element's Vision, a Swirl reader
Converging Winds', an element-change Power Boreas Unbound's, a Knight Power
Study Buddy's).

## Pool completion, 2026-10-01

The paper is `review/ruled/pool-completion-2026-10-01.md`, picks 1 to 5
ruled at the defaults ([USER]: "Overall this looks good, but one balance
note", the Body Slam note, sec.6). Built: sec.3 (three Ancients), sec.4
(Kokomi's one Common, seven Rares and two multiplayer cards), sec.5
(Furina's three Uncommons and three Rares; pick 3(a), her twelve old-kit
cards stay) and sec.6 (the Body Slam repricing). Sec.4 to sec.6 are built in
both engines; the Ancients are game-side only, as the first three were. One
text correction from the main session after a Furina audit: her faces use
"act" for what performers do, so Star Turn reads "it acts at once".

**Pools.** Kokomi is 78 (21 Common, 36 Uncommon, 21 Rare), the eight
appended LAST (`C.KOKOMI_POOL_COMPLETION_IDS`, `KokomiOverhaulRoster.Slice`),
plus five co-op cards (3 Uncommon, 2 Rare). Furina's Stage offer is 78 (23 /
35 / 20), the six appended (`furina_stage.POOL_ADDS`,
`FurinaStageRoster.SwapOfferedRows`). Each kit now holds two Ancients
(`RosterAncientCards`); the Dusty Tome draws one of them at random.

**Readings the paper left open, each the plainest one:**

- *Tidal Screen.* Gain 7 [10] Block; Plan: draw 2. The Plan line does not
  upgrade.
- *Spring Tide.* "All your Plans" is the whole queue, Dusk Plans included,
  in order. It is a drain (`KokomiPlan.ResolveAllNow`,
  `kokomi_plan.resolve_all_now`), so "the Plan after this one" riders reach
  the entry behind them, and every carry-out counts for the Casket, Kurage
  Canopy and the rest of the plan bus. Mid-turn, so Nereid's Ascension does
  NOT double its first entry (Change of Plans' reading for the whole queue),
  the morning's depth is untouched, and the Plan cap does not apply. The queue
  is emptied first, so a Plan written afterwards waits for the morning. An
  empty queue is a no-op.
- *Kurage School.* "0-cost" is the cost the card has in hand now
  (`GetResolved` / `combat.card_cost`), so a card some rule made free counts
  and an X card never does; "a Plan line" is a printed `plan:`. The hand is
  read once before the first copy, so copies are not copied; copies are exact
  (an upgraded Nip copies upgraded); a full hand stops the copying.
- *Shoal of Spears.* "Each Plan you wrote this turn" counts every write onto
  the Bake-Kurage this turn, Moon's Reflection's included; a Plan carried out
  or cancelled since still counts. New count `plans_written_this_turn`
  (`KokomiOverhaulLedger.PlansWrittenThisTurn`, cleared at the turn roll).
  4 [5] a Plan to ALL.
- *Patient Tide.* Copies add to the cap. The Energy left at her turn's end,
  up to the cap, is banked (after the Dusk drain) and added on top of the next
  turn's refill (C#: `BeforeSideTurnEnd`, then `AfterPlayerTurnStart`, which
  the game fires after the energy reset). Upgrade: keep 3.
- *Sea's Reproach.* A positive application of Weak or Vulnerable that she
  makes, once per enemy it lands on (Silent's Sadistic Nature); Suffocating
  Deep's doubling is an application and pays. The 3 damage is Hydro and
  unpowered, Tidal Riposte's hit. Upgrade: cost 1.
- *Tidal Rebuke.* Body Slam to ALL: damage equal to her Block, Rare, 2 [1],
  no Exhaust (sec.6).
- *Watatsumi Resistance.* "A Companion card" is the arm's existing
  definition (the one The General's Banner and Chain of Command read): one Nip
  per Companion play, per copy, no once-a-turn latch. Upgrade: cost 0.
- *Tactical Relay* (multiplayer). "Each player" is every living player in the
  fight, Kokomi included. New Plan clauses `each_player_energy` /
  `each_player_draw`; the draw is written at 0 and the upgrade adds it
  (`plan_draw`, Current Read's shape). Another seat draws through the base
  game's door for a draw on a player who is not acting.
- *Kurage's Mercy* (multiplayer). Each living player Mends 8 [12] through the
  one Mend rule (never above the HP each walked in with; entry HP is captured
  for every seat at combat start). Exhaust.
- *Coral Crash* is Common, 1 [0]: Body Slam exactly (sec.6). The
  Prototype-stage default had given it "draw 1" on upgrade; the row now says
  cost -1. *Noelle -- Sweeping Time* states `upgrade: {cost: -1}`: the
  Prototype-stage default already produced cost 2 [1], so the card does not
  change.
- *Aria for One.* "Three times" is the two hits and a third read once they
  have landed (a branch takes no `times:`); `conditional_damage: 2` moves all
  three hits to 7.
- *Interval Bell.* Spend 3 [2] moves the mode's price in both its gate and
  its payment, through a new upgrade key `stage_spend` (the first
  `stage_spend` anywhere on the card; codegen emits `(IsUpgraded ? 2 : 3)`).
  The Spend mode is "draw 1 card and gain 1 Energy instead" of the plain draw.
- *Casting Agent.* Three DIFFERENT cards from the Guest Cast's ten Guest Star
  cards (`FurinaStageRoster.GuestStarCards`, `furina_stage.GUEST_STAR_CARD_IDS`),
  drawn on the combat rng and shown on the choose-a-card screen; the chosen one
  costs 0 this turn and is upgraded when Casting Agent is. A full hand takes
  nothing. The sim's pilot takes the first offered.
- *The Last Act.* An empty seat is one of her seats (three, four under Sold
  Out) with no performer; the cost floors at 0. Keyed by id in both engines
  (`combat.card_cost`; `FurinaStageHooks.TryModifyEnergyCostInCombat`).
  Upgrade: 30 damage.
- *Critics' Darling.* "A Spend mode" is a chosen `stage_spend` mode, the only
  caller of `FurinaStage.Spend` / `furina_stage.spend`; Bravura and the other
  spend-all cards are not modes and do not pay. The damage is what the back
  performer actually paid, to ALL enemies, after the payment and its Bow,
  unpowered and element-less (sim source `card`, a Power's damage), once per
  copy. Upgrade: Innate.
- *Star Turn.* After the arrival and Star Billing's draw, however the guest
  arrived (a repeat copy's recast included), the guest's own seat acts once
  per copy through the one act every caller uses, so it pays as any act
  does. A guest no longer on stage does not act. Upgrade: cost 1.

**The three Ancients** (game-side only, `#if PROTOTYPE_CARDS`, witnessed by
`lint_handwritten_parity.ANCIENT_WITNESS` and set aside from the sim's
Ancient side-sheet by `ARM_ONLY_ANCIENTS`):

- *Alice's Masterpiece* (Klee, Power 3 [2]). Every charge that goes off,
  Mines included ("a Bomb that also goes off just before its enemy
  attacks"), whatever set it off. It stays at half its PRINTED size, rounded
  down, before The Big One's multiplier and Boom Badge; a 1 leaves nothing.
  The half keeps its kind (a Mine stays a Mine) and loses its payload (Jumpy
  Dumpty's Mines ride the first explosion only). It is a move, not a
  placement, so the Dodoco Charm is not paid again. It is placed after the
  explosion, so the take that set it off never sets it off again; on a dead
  enemy it jumps through the usual sweep.
- *Divine Strategy* (Kokomi, Power 2 [1]). The generated Plan branch of every
  row WITH a now-line asks `DivineStrategyPower.NowLine` after the Plan is
  written; a Plan-only row emits no ask, so it never spends the once. A row
  that aims at an enemy runs its now-line on the front enemy (a planned hit's
  own reader), one that aims at a player on the Plan's ally (Joint Orders),
  the rest untargeted. The once is claimed only once that aim is found.
- *Center of Attention* (Furina, Power 2 [1]). The turn's first chosen Spend
  takes nothing, even when the back performer could pay; while it is open the
  chooser offers a Spend mode on a short bar, provided someone is on stage.
  A free Spend pays Critics' Darling nothing.

**Art.** None of the 17 new cards (14 rows and 3 Ancients) has a portrait:
each renders the placeholder and `tools/art_coverage.py` bills the rows as
missing. The nine new Powers borrow existing badges (`KleePowerIcons`).

**Not run.** Paper sec.7's sim checks (each Kokomi deck within 10 points of
Plan volume with the new Rares; Furina's three decks within 10 points of the
default drafter; offer-take and play-rate bounds) were not run by this build
(BACKLOG). Pins: `tier0/tests/test_pool_completion.py`,
`KleeTests/Prototype/PoolCompletionTests.cs`.

## Varka element identities, 2026-10-01

The paper `review/ruled/varka-element-identities-2026-10-01.md`, picks 1 to
5 at the defaults; [USER]: "Overall looks reasonable, though Violet Storm
looks undertuned" (raised to 8 [11] and an Attack at the ruling). Five swaps
in place, the pool stays 78 (20 / 35 / 23): Charged Lunge for Updraft (C),
Short Circuit for Pressure Front (U), Chain Lightning for Unfurled Banner
(U), Violet Storm for Four Winds' Accord (R), Retaliating Tide for Unbroken
Tide (R); Thundering Verdict re-aimed to X, Wildfire Oath to one big hit.
Built in both engines. C#: `VarkaOath.cs` (`VarkaCards.ElectroStrike`,
`ElectroAll`, `VioletStorm`, the X Verdict, the ledger's first Attack and
the element he left), `VarkaPowers.cs` (`WildfireOathPower`,
`RetaliatingTidePower`, the four `OathLeftPower`s), `ArmKeywordTips`
(`ForElementSwitch`). Sim: `tier0/engine/varka_oath.py`,
`combat.card_cost`, `effects.deal_damage_to_enemy`. Codegen: three `varka`
kinds, the card field `cost_reduction_per_discard_this_turn`,
`VARKA_KIND_ELEMENTS`, `varka_switch_element`. Pins:
`tier0/tests/test_varka_element_identities.py`,
`KleeTests/Prototype/VarkaElementIdentitiesTests.cs`.

**Sec.2.** Dawn Patrol already carried Exhaust (the expansion printed it with
`exhaust: true`), so the rule needed no edit; a pin says so.

**Electro.**
- Charged Lunge: one Electro hit of the card's own (`electro_strike`), then
  the row's draw. Under the open Oath it makes Electro current.
- Short Circuit: the sheet's chosen `discard` (Concentrate's
  `FromHandForDiscard`, Survivor's sim path), then `energy 2`, then Electro
  on the chosen enemy. With fewer than 3 cards it discards what there is and
  still gains 2 (Concentrate's reading). Upgrade: the `Discards` var 3 to 2.
- Chain Lightning: the discount is a card-level rate,
  `cost_reduction_per_discard_this_turn: 1`, the shape Stomp's and
  Pinpoint's rates have in the sim. The C# card prices ITSELF in
  `TryModifyEnergyCostInCombat` off `KokomiResources.DiscardsThisTurn`
  (MementoMori's count from the combat history), so the end-of-turn flush
  (no `CardCmd.Discard`) counts nothing and no state outlives the turn; the
  sim reads `state.discards_this_turn`. Any discard of his counts, Sly and
  Violet Storm's included. Then 8 [11] Electro to ALL, one hit each.
- Thundering Verdict: `cost: X`, Whirlwind's `HasEnergyCostX`; the kind
  reads `ResolveEnergyXValue` (sim: `state.current_x`). Each of X times hits
  ALL for 6 [8] + 1 per Electro Oath; the Oath is read once, before the first
  hit (the old card's reading), so the card's own credit does not grow it
  mid-volley. X = 0 deals nothing. Upgrade moves only the 6.
- Violet Storm: Storm of Steel's discard, the whole hand in one
  `CardCmd.Discard` (sim: the `discard` op, `amount: hand_size`, so Sly and
  the turn's count see it), then one 8 [11] Electro hit per card discarded,
  each at a random living enemy (`Rng.CombatTargets` / `state.rng`). The
  card itself is not in hand while it resolves, so it does not count itself.
  `target: random_enemy` (TargetType AllEnemies, no aim).

**Retaliating Tide.** At the end of his turn, min(Block, Hydro Oath) to a
random enemy, element-less and unpowered (a Power's damage, Cycle of
Seasons' door, Block-able), once per stack. "Your Hydro Oath" is Hydro's by
name, whatever is current. After Oathbound Aegis, so the Aegis's Block counts:
the C# Aegis now pays at `BeforeSideTurnEndEarly` and the Tide at
`BeforeSideTurnEnd`; the sim pays them in that order in `turn_end`. Unbroken
Tide's kept Block left both engines with the card.

**Wildfire Oath.** The turn's first Attack card arms one bonus at the top of
its play (whatever is current then); that card's first powered hit on an
enemy takes his Pyro Oath per stack if Pyro is current as the hit lands, and
spends the arm either way. So a Pyro Knight Attack (which makes Pyro current
before its hit) is paid; Blazing Charge, whose own hit makes Pyro current, is
paid only if Pyro was already current. A Skill does not spend it; an unspent
arm goes with its play. C#: `ModifyDamageAdditive` gives it,
`BeforeDamageReceived` spends it (an AoE first Attack pays its first enemy
only, as the sim's per-enemy hits do). The Pyro Swirl payout is back to 3 on
the Swirled enemy.

**Sec.7, the switch warnings.**
1. The hover: every Varka row whose play makes an element current carries
   `ArmKeywordTips.ForElementSwitch` ("Switches your current element to
   Pyro."), printed only in a fight, while another element (or none) is
   current, and for a non-Knight only without Unwavering Banner. Which
   element is the codegen's `varka_switch_element`: a Knight's own; else the
   LAST Oath element the row applies, in effect order (Tempest ends on
   Electro). Rows that apply his current element (Favonius Drill, Cavalry
   Charge, Pathfinder's Mark) carry none. Universals and other characters'
   cards he drafts carry none (BACKLOG).
2. The panel: the element he left this turn shows beside his badge as its
   own icon, "Pyro Oath (left)", its number his Oath of it, applied loud (the
   game's apply flash), removed at the end of his turn or when it is current
   again (`OathBadge.SyncLeft`). A text line inside the badge was the first
   try and cannot work: a Power's description is registered once, so it
   cannot carry a per-turn sentence.

**The round's faces (record, "What to change" item 2).**
- Cavalry Charge is no longer tagged Anemo: a row whose hits are all
  `varka` kinds with their own element declares `Element.None` and is tagged
  with the kinds' elements (`VARKA_KIND_ELEMENTS`), so Cavalry Charge carries
  no element tag (its face says "current element"), and Blazing Charge,
  Razor, Thundering Verdict and Tempest now say "Applies Pyro / Electro / the
  four", which closes the BACKLOG line about them.
- The truth, read in the code: a Swirl's flat 2 is `ValueProp.Unblockable`
  (`ReactionEffects.SwirlPays`; the sim's `_splash` ignores Block too); the
  current element's payout damage (Pyro 3, Electro 3 to ALL) goes through
  `ElementalHit.DealUnelemented`, `ValueProp.Unpowered`, which Block stops.
  The Swirl tip and the seat glossary now say "deal 2 unblockable damage";
  to stay under the 135-character tip ceiling their last sentence is now
  "Enemies wearing it refresh." The payout is ordinary damage and stays
  unmarked, as base-game damage is (only the exception is printed; the
  current-element tip is at 132 of 135).

**Shape.** Retired ids: the five left rows got hidden aliases
(`docs/retired-card-ids.yaml`), filed under Klee's pool because
`tools/retired_ids.py` has no Varka owner (BACKLOG). No art: the five new rows
render the placeholder; Retaliating Tide's power and the left-element icons
borrow the varka element badges.

**The sim (paper sec.8), report only; no number moved on its account.**
`python -m tools.varka_expansion_sim --seeds 1000 --seed 7 --jobs 14`, the
built pool against main before this branch (each checkout's own harness;
this branch's lists drop Pressure Front from Gale and Four Winds' Accord from
Switch, put Retaliating Tide in Hydro's payoffs and the four new Electro
cards in Electro's). Default drafter act 1 won 21.3 to 23.5 (+2.2 ±1.0
paired). Forced decks, act-1 diff against the default (old, new): Pyro +3.9,
+2.7 ±2.7; Hydro -0.4, -3.6 ±3.1; Electro mono -21.6, -21.7 ±3.3; Cryo -8.7,
-10.5 ±2.9; Gale -8.9, -8.5 ±1.3; Switch -3.9, -4.5 ±1.4; Muster -1.3, -3.1
±1.3. In absolute act-1 terms every forced deck held or rose (Electro mono
7.2 to 9.5); the diffs moved mostly because the default rose. Electro is not
within 10. No new card is taken over 70% or played under 5%; Tempest Charge
crossed the take flag (68.3 to 70.9). Zero throws; one turn-cap stall.

The pilot, probed over 300 mono-Electro runs: Thundering Verdict is played
first at full Energy (X = 3 in 39 of 44 plays), so X is priced. Violet Storm is
played with 3.6 other cards in hand on average, but the harness's scorer
prices only the hits, not the cards it throws away. Short Circuit is played
last, at 0 Energy in 247 of 329 plays, with 1.7 cards to discard, so its 2
Energy mostly lands with nothing left to play, and Chain Lightning was never
played after a discard (0 of 167 plays discounted). **The pilot cannot
sequence discard into Energy or the discount**, so the sim does not read
Electro's middle; Short Circuit and Chain Lightning are unread here, as the
Kokomi sim marked Coral Tithe.


## Varka defence, 2026-10-01

The paper `review/ruled/varka-defence-2026-10-01.md`, both picks ruled
2026-10-01 ([USER]: "Everything else looks good!"; Tailwind Guard left as it
is). Three swaps in place, the pool stays 78 (20 / 35 / 23): Gale Mantle for
Squall (C), Gust Ward for Four Banners (U), Windborne Resolve for Favonian
Standard (U); Oathbound Aegis re-aimed; Tailwind Guard unchanged (3 [4] per
element, pinned). Built in both engines. C#: `VarkaOath.cs`
(`HalfTotalOath`, Windborne Resolve in `SetCurrent`, Favonian Standard's pay
gone), `VarkaPowers.cs` (`WindborneResolvePower`, `OathboundAegisPower`
re-aimed, `FavonianStandardPower` deleted), `Relics/BoreasFang.cs`
(`StartingElement`, `AfterPlayerTurnStart`), `VarkaRoster.cs`. Sim:
`tier0/engine/varka_oath.py` (`half_total_oath`, `WINDBORNE_RESOLVE`,
`turn_end`, the Fang in `turn_start`, `starting_element`). Codegen: the count
`half_total_oath`, the power `vk_windborne_resolve`. The three ids are in
`docs/retired-card-ids.yaml` (owner klee, as element identities' five). Art:
placeholders (no `art/plan.tsv` rows; Squall's row stays, as Updraft's did).
Pins: `tier0/tests/test_varka_defence.py`,
`KleeTests/Prototype/VarkaDefenceTests.cs`.

**Readings taken where the paper leaves room.**
- Gale Mantle: "half your total Oath" is the four counts summed, halved,
  rounded down (the paper's "Half rounds down"), read at play. The 5 [8] and
  the half are one powered Block (Dexterity and Frail apply, as Defend's);
  the face prints the base and, in a fight, the total.
- Gust Ward: the Block, then the draw; the upgrade moves only the Block.
- Windborne Resolve: pays on every change of his current element, the first
  of a fight included (None to X, as Boreas Unbound and Cycle of Seasons
  count it), so the Fang's turn-one element pays it if it is somehow already
  in play; unpowered Block, a Power's; copies add; paid after Cycle of
  Seasons.
- Oathbound Aegis: the power's amount counts copies (1 each, was the cap);
  each copy pays total // 2, unpowered, at the same moment as before (ahead
  of Retaliating Tide). The upgrade is cost 2 to 1 and nothing else.
- Favonian Standard's power and its pay on "a Knight already current" left
  both engines with the card; `SetCurrent` keeps its `knight` argument for its
  callers.
- **Boreas's Fang (sec.4).** The starter Knight's element is the one the Fang
  recorded when it rolled the Knight (`VarkaStarterKnight`, saved on the
  Fang), else the first starter-only Knight in the deck (Knight's
  Commission's fallback), else nothing. It fires at Knight's Commission's
  moment and through its door: his first turn, after the draw
  (`VarkaArmRelics.FirstTurnOf`), `VarkaOath.SetCurrent(knight: false)`. It
  gains no Oath, so the Ascension still waits for his first gain. It is a
  change, as Knight's Commission's is: Windblume Garland pays, and Shifting
  Gale reads "changed this turn" on turn one. Wolf's Gravestone, a Fang,
  does the same; its face says so. The relic's face gains one sentence. The
  sim records the element on the Player (`build_player`,
  `varka_starter_element`) and sets it in `turn_start` on turn 1, before
  Weathervane.
- **How the Oath panel shows it.** `SetCurrent` ends in `OathBadge.Sync`, so
  on turn one his status bar swaps from no badge (none is shown before a
  current element or any Oath) to that element's badge, "Pyro Oath" and so
  on, showing 0 (the current element's Oath), its tooltip "Your current
  element is Pyro." with the payout sentence and all four counts.
- Knight's Commission re-aimed to 2 Oath in the starting Knight's element now
  that the Fang sets the element (main session, 2026-10-01): it no longer sets
  an element; it keeps its StartingElement fallback for picking which.
- The sim tool (`tools/varka_expansion_sim.py`): Favonian Standard left FOCUS
  and Four Banners left SWITCH; Gale Mantle and Windborne Resolve joined
  SWITCH (the paper's "split and switch decks"); Gust Ward is in no list.

**The probe (sec.5).** The main session's Block probe
(`scratchpad/varka-block/block_probe.py`, the sim tool's run, gauntlet and an
act-3 deck of 27 offers at 80 HP), 500 seeds from 7, every pilot and start,
on main before this branch (6b2a2f3c) and on the built pool. Block divided by
incoming damage, base to new:

| deck | A1 elite | A2 boss | A3 normal | A3 elite | A3 boss |
|---|---|---|---|---|---|
| default | 0.66 to 0.68 | 0.63 to 0.64 | 0.68 to 0.74 | 0.55 to 0.60 | 0.72 to 0.80 |
| default, 3+ elements | 0.65 to 0.67 | 0.61 to 0.63 | 0.68 to 0.74 | 0.55 to 0.60 | 0.71 to 0.80 |
| switch | 0.61 to 0.67 | 0.61 to 0.66 | 0.69 to 0.84 | 0.53 to 0.66 | 0.69 to 0.92 |
| mono Hydro | 0.82 to 0.82 | 1.03 to 1.00 | 1.22 to 1.23 | 1.06 to 1.07 | 1.47 to 1.49 |
| mono Pyro | 0.64 to 0.63 | 0.72 to 0.69 | 0.92 to 0.87 | 0.73 to 0.71 | 1.07 to 1.03 |
| mono Cryo | 0.60 to 0.60 | 0.67 to 0.65 | 0.88 to 0.87 | 0.72 to 0.70 | 1.08 to 1.05 |
| mono Electro | 0.59 to 0.58 | 0.62 to 0.61 | 0.84 to 0.81 | 0.69 to 0.68 | 1.03 to 1.04 |
| gale | 0.65 to 0.66 | 0.60 to 0.60 | 0.63 to 0.65 | 0.50 to 0.53 | 0.62 to 0.66 |
| muster | 0.60 to 0.61 | 0.55 to 0.56 | 0.62 to 0.67 | 0.49 to 0.53 | 0.58 to 0.65 |

Against the paper's bars: the default drafter's act-3 elite Block rose 0.55 to
0.60, short of 0.72 (act-3 boss 0.80); Hydro mono stays under 1.5 (1.49 at the
act-3 boss); turn-cap stalls rose at the act-3 boss (default 12 to 21 of 4000,
switch 3 to 12, Hydro mono 9 to 17 of 1000) and are at most 10 elsewhere
(Hydro mono at act-3 normals, was 4 of 3000). The
default drafter's act-1 won 23.3% to 23.8% (n = 2000); the run never stalled.
Win rates moved within 2 points except switch at the act-3 elite (8 to 12%) and
boss (8 to 14%). The default drafter holds Gale Mantle in 10.6% of act-1 decks
and 61.8% of act-3 decks (0.86 plays per fight held), Windborne Resolve 6.4%
and 31.8% (1.08 plays per fight held, 10% of the default's act-3 Block, 22% of
the switch deck's), Oathbound Aegis 7.8% of act-3 decks (was 8.2%; its share of
the switch deck's act-3 Block 18% to 8%). **Gust Ward is never drafted**: the
stock scorer prices it 1.33 against about 2.2 for the cards beside it, so it
loses every offer; the sim does not read it. Report only; no number moved on
the sim's account.

## Furina rules pass, 2026-10-01

The paper is `review/ruled/furina-rules-pass-2026-10-01.md`, every pick
ruled. Built: sec.2 (rules 8, 5 and 4, Wriothesley), sec.3 (the old-kit
rows) and sec.4 (Quick Cue, the tips, the trims, the brief), in both
engines; Palais Ledger, Center of Attention and The Curtain Never Falls are
game-side only, as they were.

**The old-kit rows.** Exactly twelve shipped rows reached her offer through
`FurinaStageRoster.DropRetiredRows` (the audit's "about 15" counted three
already swapped): An Invitation, The Guest List, Command Performance, Singer
of Many Waters, Commanding Gaze, Undercurrent, Stage Combat (`warmup_act`),
Courtroom Drama, Crashing Waves, Duet, Quick Change and The Witness Stand.
All twelve are `proto_fs_` rows now and their shipped classes are named in
`SwapOfferedRows`, so nothing reaches the offer through the filter. Pool 78
(23 / 35 / 20), unchanged; Skills 34, Attacks 24 (was 37 / 21).

**Readings the paper left open, each the plainest one:**

- *Rule 5, "a card or potion you play".* Read by caller: `FurinaStage.Raise`
  and `RaiseLead` summon by default (every card, Bottled Applause) and every
  trigger passes `played: false` (Thunderous Applause, Tide of Applause,
  Season Tickets, All the World's a Stage, The People of Fontaine and the
  co-op `RaiseLead` power). `RaiseAll` never summons: "each performer"
  covers Curtain Water as well as Grand Deluge. Sim: only a `GAIN_CARD`
  source summons, never `SEAT_ALL`.
- *Pneuma.* A turn-start choice off Arkhe Alignment's Power, not a played
  card, so it keeps "regains" and summons nobody.
- *Rule 4.* `LEAD_REGEN` / `FurinaStageLaw.LeadRegen` are 0 in both engines
  (the constant and the turn-start door stay for The Curtain Never Falls).
  The Curtain's face drops "not 1": "Your front performer regains 2 Fanfare
  at the start of each turn."
- *Palais Ledger, "Your Spends cost 1 less Fanfare".* Per copy, floored at
  0, read by the gate and the payment alike (`FurinaStage.PriceOf`). Only a
  card's Spend N mode: a spend-all (Bravura, Bring the House Down, Let the
  People Rejoice) has no price to lower, and Chevreuse's act is the
  performer's. A price of 0 still needs someone on stage. Critics' Darling
  deals what was paid, after the discount.
- *Center of Attention.* The gate no longer asks it; its free Spend is
  claimed at payment as before and still needs someone on stage.
- *Wriothesley, "Always your front performer".* His own summon on a full
  stage now Bows the FRONT performer, as any summon does, and he arrives in
  front holding his Fanfare plus its remainder (`FurinaStage.RecastToFront`,
  sim `recast_to_front`; until now the back performer Bowed). A summon while
  he stands there Bows the performer behind him, and the seat moves that
  would move him still do nothing: both unchanged. The Summon tip keeps "the
  front one Bows first"; his face is the caveat.
- *The tips.* The damage order moved from the Fanfare tip to the front
  performer's ("Takes hits after your Block; what its Fanfare cannot hold
  reaches you."), so the paper's empty-stage line fits the 135-character tip
  ceiling. The Bow tip reads "A performer acts one last time, without
  paying, as it leaves the stage or, if a card says so, stays." (the text
  lint refuses parentheses). Spend: "...from your back performer first, then
  forward. Offered only if your performers hold enough." The seat page's
  refused-Spend line says what the performers hold between them.
- *Opening Number, "the first card you played this turn".* C# counts the
  cards she has finished playing this turn (`FurinaStageHooks.AfterCardPlayed`,
  auto-plays included; zeroed at her turn start) and asks for 0; the sim
  counts before the play resolves and asks for 1. The pilot treats the
  predicate as blind. It has no `replaces:`: An Invitation is Rising
  Applause's starter pairing, so the sim drops it (`POOL_DROPS`) and appends
  Opening Number (`POOL_ADDS`).
- *Endless Waltz.* Who has 5 or more is read once, before any act, so an act
  that moves a bar does not change who acts; a resting returnee sits it out,
  as with Tutti!. No Exhaust, no element.
- *Leading Lady.* Reads the front bar at play, as Pneuma Refrain does.
- *Singer of Many Waters.* "Your front performer gains 6 [9] Fanfare.
  Exhaust." A played card's gain, so on an empty stage it summons a performer
  holding it. Keeps its `archon` register and its art.
- *The eight ported as they are.* Body, cost, rarity, register and upgrade
  copied from `docs/furina-cards.yaml` and `docs/furina-upgrades.yaml`; the
  shipped sheet's design fields (`solve`, `tempo_band`, `archetypes`,
  `role`) are not prototype keys. Each wears its own art (`art_of:`). Stage
  Combat's id is `proto_fs_warmup_act` (the art-proxy rule wants the id to end
  in the art it wears), and its face prints its Block as a variable (the
  orphan-var lint). Duet still names a Companion card.
- *The trims.* Grand Deluge: "Deal 12 damage and apply Hydro to ALL enemies.
  On an Elemental Reaction, each performer gains 2 Fanfare." Bravura: "Spend
  your back performer's Fanfare." Guest of Honor: "Until your next turn, your
  front performer takes hits on another player after their Block." Pneuma
  Refrain: "per Fanfare" for "for each Fanfare". Stage Whisper: "Each other
  performer gives all but 1 Fanfare to your front performer." Bring the House
  Down: "If it empties, it Bows." after its first sentence.
- *Art.* Opening Number, Leading Lady and Endless Waltz render the
  placeholder (`BACKLOG.md`).

## Kokomi status batch, 2026-10-01

Paper `review/ruled/kokomi-status-batch-2026-10-01.md`, ruled: [USER]
"Agreed on the Plan text change"; "the 7 removals are good"; Kelp Wall,
Tidecleanse and Coral Sanctuary revised on his notes. Built in both engines,
except Coral Sanctuary: the main session withdrew it during the build and it
was cut ([USER]: "Coral Sanctuary feels messy ... since we only have 1 card
in the deck that makes them, it's not good otherwise"). Riptide Ruin took the
Rare slot in a follow-up the same day, so the pool is **78 (21 / 36 / 21)**.

**In (six rows, LAST in the sheet's order).** Kelp Wall (Skill 1, Common),
Tidecleanse (Skill 0, Common), Sea Glass Harvest (Skill 1, Uncommon), Turning
Tide (Skill 0, Uncommon), Flotsam Surge (Attack 1, Uncommon), Abyssal Salvage
(Power 1, Uncommon), plus the Sea Glass token (0, "Gain 1 [2] Energy.
Exhaust.", hand-written as `Cards/Prototype/SeaGlass.cs`, in no pool, off-pool
beside Open the Casket; sim `kokomi_plan.sea_glass_card`).

**Out (seven rows).** Rally, Pearl Diver (Common), Battle Plan, Feigned
Retreat, Moon Signal, Chain of Command (Uncommon), All Streams Flow to the
Sea (Rare): out of the sheet, `C.KOKOMI_OVERHAUL_POOL_IDS` and
`KokomiOverhaulRoster.Slice()`, tombstoned in `docs/retired-card-ids.yaml`.
Their engine pieces stay registered with no row spelling them (BACKLOG's
unused-engine-pieces line lists them). The pins that tested only a cut card
left with it.

**The face says "or" (paper sec.3).** One change in the generator, beside the
line break: `gen_klee_cards.plan_line_says_or` turns every broken Plan clause
into "Or [gold]plan[/gold]:" and a Dusk one into "Or [gold]dusk[/gold]
[gold]plan[/gold]:"; the sheet keeps "Plan:". Kurage's Oath now reads "Gain 6
Block. / Or plan: Deal 7 damage to ALL enemies." The lower-case words are
tokens of the Plan and Dusk keyword rows, so the tips still attach. The Plan
tip (`ArmKeywordTips.ForPlan`, the blind page's glossary row with it) is now
"Instead of the line above, play the card on the Bake-Kurage: this happens at
the start of your next turn. Plans go in the order made." (133 of 135).

**Readings the paper left open (the builder's plainest, flagged in the PR):**

1. *"Or plan:" on Plan-only rows.* The first build read "on every card"
   literally and printed "Play on the Bake-Kurage. / Or plan: ...". The
   main session's call, the same day: the "or" chooses between two printed
   effects, so it appears only when a now-line with an effect sits above
   the Plan line (`plan_line_says_or` tests `plan` and `effects`, the same
   test as `_plan_only_line` and the target type). A Plan-only face keeps
   "Play on the Bake-Kurage. / Plan: ..." ("Dusk Plan:" on Breakwater and
   Brace for the Tide); Shell of Sanctuary and Evening Watch, which have a
   now-line, print "Or dusk plan:".
2. *The tip's second sentence* was shortened ("Plans go in the order made.")
   so the paper's opening fits the 135-character ceiling.
3. *Tidecleanse's "up to N".* Every status and curse when she holds N or
   fewer; when she holds more, the mod asks which N (a hand screen,
   `CardSelectCmd.FromHand`); the sim takes them in hand order.
4. *Turning Tide's upgrade.* The paper prints none; the row takes the
   Prototype-stage default, the now-line draws 2.
5. *Turning Tide in the sim.* The mod asks (Gambler's Brew's screen, any
   number, none included); the sim discards every status and curse in hand
   and nothing else. An instrument surface, not tuned.
6. *Abyssal Salvage's upgrade.* "[and you gain 2 Block]" cannot be an `add:
   apply_power` delta (not expressible), so the upgraded card installs
   `AbyssalSalvagePlusPower` (`upgraded_power`, The Long Game's shape): each
   stack is 1 Casket and 2 Block per exhausted status or curse
   (`KOKOMI_ABYSSAL_SALVAGE_PLUS_BLOCK`, mirrored). "A status or curse" is one
   of hers, by any route (played Slimed, a Dazed's Ethereal exhaust at turn
   end, Tidecleanse); Block is powered.
7. *Sea Glass Harvest.* Upgraded, the Plan transforms into Sea Glass+, read
   off the writing card's `IsUpgraded` at carry-out (sim: the
   `upgraded_grant` flag on the clause). A curse the game will not transform
   (`IsTransformable` false) stays in hand.
8. *Kelp Wall.* The rate (3) does not upgrade; the flat Block does (7 to 10).
   The count is the hand when the clause runs.
9. *Flotsam Surge* shuffles the base game's Dazed (`status_dazed` in the sim)
   into the draw pile at random depths, and applies Hydro through the arm's
   cadence like every damaging card of hers.
10. *Drafter prices.* The four new Plan clauses are priced ZERO in
    `tier05.draft` (a hand fact an offer screen cannot read), the `kokomi`
    op's precedent; no `DRAFTER_VERSION` bump, as with every prototype op.

**Engine.** Four Plan kinds, appended last: `BlockPerStatusInHand`,
`ExhaustStatusesInHand`, `TransformStatusesInHand`, `DiscardAndDraw`
(`KokomiPlan.Kind`; sim `kokomi_plan`, the same names in snake case), bodies
in `Powers/Prototype/KokomiStatusBatch.cs`. Rule 2's after-the-draw
resolution is what lets them read the next hand. A status or curse is the
card's own type (`CardType.Status` / `Curse`); the sim asks type and rarity,
because an injected status is built at rarity "basic". Abyssal Salvage rides
`AfterCardExhausted` (sim: `refpowers.after_card_exhausted`). Pins:
`tier0/tests/test_kokomi_status_batch.py`,
`KleeTests/Prototype/KokomiStatusBatchTests.cs`.

**Sim read (census wrapper, 600 seeds, five pilots, stock priest pilot, not
tuned).** Pick % of offers (all drafters / default drafter), plays per fight
held:

| Card | Pick % | Default drafter | Plays per fight |
|---|---|---|---|
| Kelp Wall | 20.3 | 28.8 | 0.07 |
| Tidecleanse | 7.0 | 9.8 | 1.48 |
| Sea Glass Harvest | 25.9 | 36.4 | 1.16 |
| Turning Tide | 0.0 | 0.0 | never held |
| Flotsam Surge | 58.6 | 82.2 | 1.80 |
| Abyssal Salvage | 0.0 | 0.0 | never held |

The stock pilot cannot read the next-hand Plans: it writes a Plan only when
the now-line is empty or no enemy attacks, and it does not foresee the
statuses it will draw. So Kelp Wall's, Tidecleanse's, Sea Glass Harvest's and
Turning Tide's Plan halves are unread, and Turning Tide and Abyssal Salvage
(priced ZERO by the drafter) are never drafted. Flotsam Surge, the one card
the stock drafter can price, is taken from 82% of the default drafter's
offers, over the 70% line pool completion's sec.7 uses. The seats decide.

- *Art.* All six rows and Sea Glass render the placeholder; Abyssal Salvage
  wears the Princess of Watatsumi badge (`BACKLOG.md`).

**Riptide Ruin (follow-up, 2026-10-01).** Attack, 2, Rare: "Deal 9 [12]
damage to ALL enemies twice. Shuffle 3 Dazed into your draw pile." Appended
last (`C.KOKOMI_STATUS_BATCH_IDS`, `KokomiOverhaulRoster.Slice()`); Hydro
through the arm's cadence like every damaging card of hers. [USER]: "Riptide
Ruin sounds quite strong but possibly fine at Rare. My counterpoint example
would be Echoing Slash on Silent." The upgrade moves the per-hit damage only
(`upgrade: {damage: 3}`); the hit count and the Dazed count do not move.
Pins: `test_kokomi_status_batch.py`, `KokomiStatusBatchTests.cs`. Art:
placeholder. `tools/kokomi_expansion_sim.py` no longer names the cut rows
(All Streams' pilot rule and report line went with it).

## Klee status package, 2026-10-01

Paper `review/ruled/klee-status-package-2026-10-01.md`, ruled: [USER] "1) I
think a) is fine - we can keep tho the game's conventions 2) and 3) agreed on
your defaults". Built in both engines. The pool stays **78 (24 / 33 / 21)**,
from 24 / 36 / 18.

**In (eight rows, LAST in her pool's order, `C.KLEE_STATUS_PACKAGE_IDS`).**
Forbidden Fun (Attack 0, Common: 10 [14], a Dazed), It Wasn't Me! (Skill 0,
Common: 6 [9] Block, a Dazed), Lisa's Treats (Skill 0, Uncommon: 2 [3]
Energy, 2 Confiscated), Red Knight (Attack 2, Rare: 22 [28] to ALL, 2
Confiscated), Finders Keepers (Power 1, Uncommon: Confiscated played, a Bomb
5 [7] on a random enemy), Klee Can Explain! (Skill 1, Uncommon: 6 [8] Block,
every status in hand becomes Pop!), Damage Report (Power 1, Rare: a status
drawn, 5 [7] to ALL), Solitary Confinement (Power 1, Rare: Confiscated cost
0; upgrade adds Innate).

**Albedo's Klee stand-in.** "Albedo — Dust of Purification"
(`proto_mc_albedo_dust_of_purification`, Skill 1, Rare, Mondstadt, the same
slot: `personal_pool: [klee]`, `replaces: proto_mc_albedo_solar_isotoma`)
replaces "Albedo — Tectonic Tide": "Exhaust every status in your hand. Your
largest Bomb grows by 6 [8] for each." Tectonic Tide's id is tombstoned.

**Out (eight rows).** Pocket Fireworks, Dodoco Cover (Common), Careful Now,
Friendship Bracelet, Fish Fry, Flame Dance, Rapid Fire, Split Charge
(Uncommon): out of the sheet, `C.KLEE_OVERHAUL_POOL_IDS` and
`KleeOverhaulRoster.Slice()`, tombstoned in `docs/retired-card-ids.yaml`
(with Tectonic Tide). Their painted art, Tectonic Tide's too, is `KNOWN_STALE`
(`tools/art_coverage.py`). Engine pieces only they used stay registered with
no row spelling them (BACKLOG). The pins that tested only a cut card left
with it.

**Readings the paper left open (the builder's plainest):**

1. *What a status is.* A card of Status TYPE or Status RARITY
   (`KleeStatusPackage.IsStatus`, sim `klee_overhaul.is_status`).
   Confiscated is a Status-rarity Skill, so it counts; curses do not.
2. *The taxes.* Dazed is the base game's (`status_dazed`, Flotsam Surge's
   spelling), shuffled into the draw pile at a random depth; Confiscated is
   the existing token, added the way Fish Blasting adds it.
3. *Tips.* A card that shuffles in a Dazed now previews the base card
   (`KleeCardTooltips.ForCard(..., includesDazedCard: true)`, derived from
   the `add_card` op), so Kokomi's Flotsam Surge and Riptide Ruin gained it
   too; Confiscated's makers keep the Confiscated keyword tip. Klee Can
   Explain! previews Pop! (Compact's Fuel shape).
4. *Klee Can Explain!* transforms every status in hand that the game will
   transform (`IsTransformable`), Compact's body; the Pop!s arrive
   unupgraded.
5. *Dust of Purification.* The exhausts first, then one growth of 6 [8]
   times the count on her single largest Bomb; with no Bomb out the
   exhausts still happen. Art: a placeholder, since a stand-in may not wear
   a neighbour's art (`test_no_standin_wears_a_neighbours_art`); Tectonic
   Tide's painted file is `KNOWN_STALE`.
6. *Damage Report* is per card drawn (`AfterCardDrawn`; sim
   `refpowers.after_card_drawn`), Spark Knight's unelemented hit on every
   living enemy. Copies add.
7. *Finders Keepers* is Party Poppers' shape: a play of a Confiscated
   (replays count) places a plain Bomb of the stack's size on a random
   enemy.
8. *Solitary Confinement* is Playdate's cost seam for every Confiscated of
   hers for the rest of combat (sim `combat.card_cost`).
9. *Drafter prices.* The two new ops are priced ZERO in `tier05.draft`, the
   arm's other verbs' decision; no `DRAFTER_VERSION` bump.

**Engine.** Two ops, `transform_statuses_into` and
`exhaust_statuses_grow_largest`, and three Powers (`ko_finders_keepers`,
`ko_damage_report`, `ko_solitary_confinement`); C# in
`Powers/Prototype/KleeStatusPackage.cs`, sim in `klee_overhaul.py`'s
status-package block. Pins: `tier0/tests/test_klee_status_package.py`,
`KleeTests/Prototype/KleeStatusPackageTests.cs`.

- *Art.* The eight new rows render the placeholder; the three Powers borrow
  Party Poppers', Spark Knight's and Playdate's badges (`BACKLOG.md`).

## A Plan stays open (Kokomi), 2026-10-01

Paper `review/active/kokomi-delay-pays-2026-10-01.md`, ruled. [USER]:
"Interesting idea! Yes, I think this makes sense. We'd want to make sure that
the UX is reasonably snappy so players don't have to spend forever on their
turns, but it sounds doable." When the Bake-Kurage carries out a Plan written
from a two-line card, the player picks its Plan line (the default) or its
now-line at printed size. No card and no number changes.

**Readings taken.**

1. *Which Plans.* A two-line card's own line, Moon's Reflection's found card
   included (`KokomiPlan.Entry.TwoLine`: not Dusk, `Source` is an
   `INowLineCard`; sim `kokomi_plan.two_line`). Thirty rows on the 78.
2. *One screen a turn.* The chooser claims a once-a-turn latch
   (`kk_plan_line_chooser`). The morning asks first; a Change of Plans or
   Spring Tide later the same turn, after the screen was shown, carries out
   the Plan line. If the morning had no two-line Plan, the first such door
   that turn shows the screen.
3. *Copies.* The choice is per entry, so every carry-out of it (Nereid's
   Ascension, Second Wave, All Streams) takes it -- the paper's "the default
   is the line chosen for the first", with one screen.
4. *The now-line is the card's own, at printed size.* Generated two-line rows
   now put their now-line in `PlayNowLine`, which `OnPlay` calls face-up and
   `KokomiPlan.CarryOutNowLine` calls at carry-out on an auto-play
   `CardPlay` (no cost, no card moved, not a card played). Her Strength and
   Dexterity at carry-out apply, as on a face-up play; Opening Gambit's
   double does not reach it, and it writes no rider. Sim:
   `carry_out_now_line` resolves the card's `effects:` under a saved and
   restored per-card context.
5. *The aim.* Divine Strategy's: the front enemy, or Converging Tide's
   override while that body stands (the Plan retargeting rule); Joint
   Orders' captured ally, or nothing if that player is gone.
6. *Payoffs.* `ResolveEntry` rings the Casket, Sango Isshin, Feint, Grand
   Design, Kurage Canopy and the plan bus after either line.
7. *The screen.* The base game's simple card grid (`CardSelectCmd.FromSimpleGrid`,
   min 0, max N, manual confirm), the precedent Varka's Weathervane set for
   a turn-start chooser. It shows the Plans' own card instances, both lines on
   each face; a picked card is a flipped Plan, a second click unpicks it, and
   Confirm with nothing picked takes every Plan line. A card instance that
   wrote two Plans is shown once and both take its line. The grid has no
   live forecast panel: the highlight is the only thing a flip changes on
   screen.
8. *Text.* The Plan tip's middle now reads "next turn, you choose which line
   happens" (130 rendered characters); the Bake-Kurage's box adds "Then you
   choose each Plan's line." (100 of its 125). The
   beat over the pet names a now-line carry-out "<card> (now-line)".
9. *Sim pilot.* `kokomi_plan.line_policy`, an instrument surface: the
   now-line when it gains her Block and the enemies' intended damage this
   turn exceeds her Block, or when every damaging clause of the Plan line
   would land on nothing or on an Intangible body; else the Plan line.
10. *Bridge.* The waiting list prints both lines of a two-line Plan; the
    chooser page lists each due Plan, both lines and its current line, with
    the fight behind it (`McpMod.StateBuilder` now sends `battle` under a
    mid-fight card grid). Verbs `flip "<card>"` (or `flip <n>`) and
    `confirm`.

**Pins.** `tier0/tests/test_kokomi_open_plan.py`,
`KleeTests/Prototype/KokomiOpenPlanTests.cs`. Untested in game until a
deploy.

## Kokomi: the Casket repeats, and the flip, 2026-10-01

The four-kit review (PR #823), Kokomi pick 1, and the coordinator's pick 5,
ruled. [USER]: "On your new picks agree all around - I think that if it's
repeatable, it should probably cost energy, though, to make this a real
choice and not just button mashing when it comes up?" Paper
`review/active/kokomi-delay-pays-2026-10-01.md`, edited in place.

1. *Open the Casket.* Cost 1 (was 0), Retain, no Exhaust; text unchanged; no
   upgrade. Played, it goes to the discard pile and comes back with the deck,
   and each opening takes the count gathered since the last. The relic still
   deals one copy on turn one. Sim twin `kokomi_plan.open_the_casket_card`.
2. *What the Tokoyo Returns.* "Put Open the Casket into your hand from your
   draw pile or discard pile." The draw pile first, then the discard pile;
   the Exhaust Pile is no longer searched
   (`KokomiOverhaulKit.FetchOpenCasketPiles`; sim
   `kokomi_plan.fetch_open_casket`). Cost 1, Exhaust, upgrade cost -1, as
   before.
3. *Pick 5 (a): no chooser.* "Plans carry out on their Plan line; click a
   waiting Plan to flip it." `KokomiPlan.ChooseLines` no longer opens a
   screen or claims a latch: each due entry keeps its `Now` flag, cleared
   only on an entry that cannot offer the choice. Every door (morning, Change
   of Plans, Spring Tide) reads the flips; Dusk is untouched.
4. *The surface: the Plan strip.* The strip already drew one clickable
   picture per waiting Plan (its hover), so a left click on a two-line
   Plan's picture is the flip; a second click flips it back. A caption under
   each two-line Plan reads "Plan line" or "Now-line", and a flipped picture
   is tinted. The strip draws the first four Plans; a fifth or later is
   reached by the bridge verb. Chosen over a power-icon grid because it adds
   no screen and puts the click on the Plan itself.
5. *Sync.* The click is a game action (`FlipPlanGameAction`, wire twin
   `NetFlipPlanAction`), enqueued through `ActionQueueSynchronizer` as a card
   play is, so a co-op peer flips the same Plan. Play phase only, and
   `KokomiPlan.Flip` refuses again mid-drain and outside her play phase.
6. *Forecast.* The bridge's queue row carries `line`; a flipped Plan reports
   no front damage (its now-line is carried out instead).
7. *Text.* The Bake-Kurage's box: "Click a waiting Plan to flip it." The Plan
   tip: "it happens next turn. Click it to flip lines." (133 rendered, under
   the 135 ceiling).
8. *Sim pilot.* `kokomi_plan.line_policy` is the Plan line; the pilot sets
   its flips at the end of its turn (`pilot_flips`, before the Dusk drain).
   The old heuristic read the carry-out turn's intents, which a flip made a
   turn early cannot see, and went with the screen.
9. *Bridge.* `kokomi_flip_plan` (`vendor/STS2_MCP/gits/GitsKokomiFlip.cs`);
   the page's verb is `flip <n>` or `flip "<card>"`, offered while a waiting
   Plan has two lines. The chooser page and its `confirm` are gone; `confirm`
   stays for every other screen.

Items 2 and 7 to 10 of "A Plan stays open (Kokomi)" above describe the first
build's screen; this note supersedes them.

**Pins.** `tier0/tests/test_kokomi_casket_pass.py`,
`tier0/tests/test_kokomi_open_plan.py`,
`KleeTests/Prototype/KokomiCasketPassTests.cs`,
`KleeTests/Prototype/KokomiOpenPlanTests.cs`.

## Fontaine companions ported, 2026-10-01

Legacy cleanup pick 4 (`review/active/legacy-cleanup-2026-10-01.md`, ruled):
"The 19 Fontaine companion rows move to the prototype sheet as they are. A
Fontaine rework is its own paper." Built in legacy cleanup stage 4.

- The sixteen companions are `proto_mf_<shipped id>` rows owned by `klee`, as
  every companion row is (their frame is Klee's pool's, as the shipped rows'
  was). Bodies, cost, rarity, star, element and role are the shipped rows' from
  `docs/fontaine-companions.yaml`; each upgrade is the shipped row's from
  `docs/furina-upgrades.yaml`; `art_of:` borrows the shipped portrait. Names end
  " (proto)" (the declared-shadow rule) until stage 5 deletes the shipped rows.
- The three Neuvillette guest stars are `proto_mf_guest_neuvillette_*`, owned by
  `furina`, `guest_star: true`, `no_upgrade:` (a guest star is made for one
  fight; the shipped rows had no upgrade). No current card generates a guest
  star, so they are members only.
- Both engines' companion roster is now prototype rows only:
  `CompanionOverhaulRoster.FontaineUniversals` and
  `C.FONTAINE_OVERHAUL_POOL_IDS`, with `fontaine` in
  `C.COMPANION_OVERHAUL_NATIONS`.
- The shipped C# emitter's prototype-surface differences carry over unchanged
  (the arm keyword-tip wrapper and the front-folded damage var); nothing on a
  face or in a body moved.

## Klee defence in the status pile, 2026-10-01

The status package paper's sec.5, ruled: [USER] "Ok Klee - I'd say we go for
option 1 and add the defensive utility into her status pile, which gives some
incentive for players to engage with it. We can give a mix of weak,
high-block cards (already present) and perhaps an alchemy-flavored Strength
reduction?" Built in both engines. The pool stays **78 (24 / 33 / 21)**.

**In (three rows, appended to `C.KLEE_STATUS_PACKAGE_IDS`, LAST in her pool).**
Up in Smoke! (Skill 1, Common: 2 [3] Weak to ALL, a Dazed), Behind Jean's
Desk (Skill 1, Uncommon: 14 [18] Block, a Confiscated), Kitchen Alchemy
(Skill 1, Uncommon, Exhaust: ALL enemies lose 1 [2] Strength; exhaust every
status in hand, they lose 1 more for each).

Reworked 2026-10-02 after the forced-deck seat (0 plays in 7 hands: a status is rarely in hand): always playable, more with statuses.

**Out (three rows).** Fish-Flavored Bait (Common), Nova Burst
(`proto_ko_big_bounce`) and Spinning Sparkler (Uncommon): out of the sheet,
`C.KLEE_OVERHAUL_POOL_IDS` and `KleeOverhaulRoster.Slice()`; painted art
`KNOWN_STALE`; pins that tested only a cut card removed; engine pieces left
registered (BACKLOG).

**Readings:**

1. *No gate (2026-10-02).* The first build was unplayable with no status in
   hand (an `exhaust_a_status` op and an `IsPlayable` gate); the rework
   removed both. The card always plays.
2. *Which statuses.* All of them in hand (`KleeStatusPackage.ExhaustStatuses`,
   sim `klee_overhaul.exhaust_statuses`; Dust of Purification's exhaust,
   shared). A status is Status type or Status rarity; curses stay.
3. *The Strength loss* is permanent: Malaise's `PowerCmd.Apply<StrengthPower>`
   at minus N on every hittable enemy (op `lose_strength`, ALL enemies only;
   sim `effects._op_lose_strength`, negative `strength` on the enemy). Its
   `per_status: 1` field exhausts the statuses first and adds 1 per status,
   applied once as one total (`KleeStatusPackage.LossWithStatuses`). Upgrade
   key `strength_loss` moves the base only, the `StrengthLoss` var.
4. *Up in Smoke!'s face.* A name-matched power delta (`weak: +1`) on a row
   with its own `description:` now swaps the printed number for
   `{PowerAmount:diff()}` (`_authored_face_numbers`); before, only
   `power_amount` did. No other generated card changed.
5. *Drafter prices.* `lose_strength` is priced ZERO in
   `tier05.draft`, the arm's other verbs' decision; no `DRAFTER_VERSION` bump.

Pins: `tier0/tests/test_klee_status_package.py`,
`KleeTests/Prototype/KleeStatusPackageTests.cs`. Art: placeholders.

## Klee final pass, 2026-10-02

Paper `review/ruled/klee-final-pass-2026-10-02.md`, "Ruled". Klee lost all
nine seat runs since the status package, on Block at the act-2 boss turn,
with Sparks piling up unspent. Built in both engines. The pool stays **78
(24 / 33 / 21)**.

- **HP 62 to 70**, Silent's ([USER]: "Let's try 70 like Silent").
  `Klee.cs` `StartingHp`, `tier0/content/characters/klee.yaml`.
- **In: `proto_ko_cover_your_ears`**, Cover Your Ears! (Uncommon Skill, 0
  Energy and 2 Sparks, Exhaust): "ALL enemies lose 6 [8] Strength this
  turn." Piercing Wail's numbers, priced at the pool's two Sparks for an
  Energy's worth (Sparkling Burst, Boom Badge). It is the second Spark sink,
  and it fires on the boss turn. It takes Where Did I Put It?'s slot in
  `C.KLEE_OVERHAUL_POOL_IDS` and `KleeOverhaulRoster.Slice()`.
- **Blast Shield** (`proto_ko_blast_shield`) **Uncommon to Common**, so seats
  see the one repeatable Spark-to-Block card more often. Nothing else moves.
- **Out: `proto_ko_where_did_i_put_it`** (Common). The w14 act-2 seat named
  it NEVER AGAIN (it found a Set off card 1 time in 5), and Countdown,
  Treasure Map and Once More! already fetch Set off cards. The main
  session's call, not a ruled pick; it reverses with one row. Painted art
  `KNOWN_STALE`; its pins removed; its `scry_take` `filter: set_off` is left
  registered (BACKLOG).
- **Unchanged:** Kitchen Alchemy (the permanent, status-fed reducer, as
  ruled) and Playdate (Common; every post-fight reward offers a Companion).

**Readings:**

1. *The this-turn loss.* `lose_strength` takes `this_turn: true`. In C# the
   codegen applies the card's own `TemporaryStrengthPower` subclass,
   `ProtoKoCoverYourEarsPower` (`IsPositive` false, origin the card; the
   base game's `PiercingWailPower` shape, `Powers/Prototype/KleeFinalPass.cs`)
   at plus N to every hittable enemy. It gives the Strength back at the end
   of that enemy's turn. The sim applies `temp_strength_down`, the
   TemporaryStrength handling `refpowers` already runs for Mangle. It does
   not combine with `per_status`. The power borrows the Bomb's Vulnerable
   badge, as Shrapnel does.
2. *The upgrade* is `strength_loss: +2`, the key Kitchen Alchemy's first
   build used.
3. *The manifest.* Its description said "About one card reward in twenty
   offers a fourth, Companion, choice", which was stale. It now reads "After
   each fight, the card reward offers a fourth choice: a Companion card.",
   and the seat page's `COMPANION_SLOT_SENTENCE` quotes it, as pinned.

Pins: `tier0/tests/test_klee_final_pass.py`,
`KleeTests/Prototype/KleeFinalPassTests.cs`. Art: placeholder. Untested in
game until a deploy.

## The co-op run notes (2026-10-02)

[USER], after a co-op run with a friend:

- "Let's remove Innate from Klee's starting Jumpty Dumpty - I think that's
  why seats keep getting chip damage hit on round one". **`proto_ko_jumpy_dumpty`**
  drops `innate: true`, on both faces. Nothing else on the row moves. This
  undoes R261 (above). Pins: `tier0/tests/test_klee_overhaul.py`,
  `KleeTests/Prototype/KleeOverhaulRoundTwentyTests.cs`. Restored
  2026-10-03 (see the R261 entry).
- "Barbara: Wellspring Hymn needs Exhaust". **`proto_vk_barbara_wellspring_hymn`**
  gains `exhaust: true`. Its upgrade (Block +3) is unchanged.
- "can we make this a strength debuff instead of the weird wording on the
  hit?" **`proto_mc_amber_explosive_puppet`** now reads "Enemy loses 3
  Strength this turn. The next time an enemy attacks you, deal 8 Pyro damage
  to ALL enemies." It targets an enemy. The loss is Cover Your Ears!'s
  `lose_strength` with `this_turn: true`, on the chosen enemy: in C# the
  card's own `ProtoMcAmberExplosivePuppetPower` (a `TemporaryStrengthPower`,
  `Powers/Prototype/KleeFinalPass.cs`), in the sim `temp_strength_down`.
  The codegen's `lose_strength` now takes `target: enemy` (it is in
  `AIMING_OPS`). Baron Bunny keeps only its volley; its "take 3 less" and the
  constant `MC_BARON_BUNNY_REDUCTION` / `BaronBunnyReduction` are gone. The
  upgrade is unchanged: it never moved the reduction or the damage, it adds
  "Draw 1 card" (the Prototype default rule). The power borrows the Bomb's
  Vulnerable badge, as Cover Your Ears! does.

Untested in game until a deploy.

## The co-op notes rulings (2026-10-02)

The paper `review/ruled/coop-notes-2026-10-02.md` (PR #843), ruled
2026-10-02. Pick 1 (Klee to Balance) waits on a sanity playtest and builds
nothing yet. Pick 3 (Varka's Electro discard) was reopened and folded into a
Varka element rebalance, so Charged Lunge and Static Field do not move.

- Pick 2, "Agreed on both fronts - let's do a pass over the Varka card pool
  to standardize the language around the existence of this tooltip".
  - **`proto_vk_assembly_at_the_cathedral`** reads "Whenever you apply an
    element, deal 2 [3] damage to a random enemy." It was 3 [4] on a
    Knight's play. Cost, type and rarity are unchanged. It now pays at
    `VarkaOath.NoteApplication`, after the Oath credit; the sim twin is
    `varka_oath.note_hit`. Its own hit has no element, so it cannot pay
    itself.
  - **Every Knight prints "Knight." first.** `KleeKeywords.Knight`
    (`AutoKeywordPosition.Before`, the base game's before-description rail)
    is declared by codegen on every companion row with `personal_pool:
    varka`. That is the 17 colon-titled rows that `VarkaRules.IsKnight`
    answers yes for. Its key is `KLEEMOD-ARM_VARKA_KNIGHT`, the key
    `ArmKeywordTips.ForKnight` already titled. So the printed line and a
    golded [gold]Knight[/gold] hover one tip, and its sentence is one
    constant: "One of Varka's Companions. Playing one makes its element your
    current element (except Geo)." The exception is Noelle, a Geo Knight,
    who sets no element.
  - **The language pass:** Knights' Roll Call+ golds "a [gold]Knight[/gold]
    you choose", and The Order Answers' power golds the whole plural. No
    other face changed. Knight's Commission, Boreas's Fang and Wolf's
    Gravestone gold "starting [gold]Knight[/gold]" and attach the same tip
    (`ArmKeywordTips.ForKnight`).
- Pick 4, "Agreed on Neuvillette's a)". **`proto_mf_neuvillette_ancient_sea_authority`**
  reads "At the start of your turn, apply [gold]Hydro[/gold] to a random
  enemy. Elemental auras you apply last 1 extra turn." The power applies
  Hydro once per copy through `ElementalHit.ApplyOnly` in
  `AfterPlayerTurnStart`. The sim twin is `player_turn_start_triggers`. This
  reverses the row's old "applies no element of its own" note.

Pins: `KleeTests/Prototype/CoopNotesRulingsTests.cs`,
`tier0/tests/test_varka_expansion.py::test_assembly`,
`tier0/tests/test_fontaine.py`. Untested in game until a deploy.

## Status cards go to the discard pile (2026-10-03)

[USER], adopting the base game's convention: "I agree that we should adopt
the same convention". In the 0.111.0 decompile every base card that creates
a status (Turbo, Overclock, Gunk Up, Boost Away, Fight Through) adds it with
`CardPileCmd.AddGeneratedCardToCombat(card, PileType.Discard, owner)`; none
uses the draw pile. Nine rows of ours shuffled a status into the draw pile at
a random depth (the `zone: draw` of the pool pass, `EB-491`). Each now adds
it into the discard pile, and its face takes the base's wording (`OVERCLOCK`:
"Add a [gold]Burn[/gold] into your [gold]Discard Pile[/gold]."):

- Klee, Confiscated: Fish Blasting, Lisa's Treats, Red Knight, Behind Jean's
  Desk.
- Klee, Dazed: Forbidden Fun, It Wasn't Me!, Up in Smoke!.
- Kokomi, Dazed: Flotsam Surge (2), Riptide Ruin (3).

Numbers, costs and upgrades are unchanged. The `draw` zone is retired in both
engines: the codegen refuses it by name and `effects._add_token` no longer
inserts at a random index. Pins: `KleeTests/Prototype/StatusToDiscardTests.cs`
and the sim twins in `test_klee_status_package.py`,
`test_kokomi_status_batch.py` and `test_klee_overhaul_rules.py`. Untested in
game until a deploy.

## AoE trim, 2026-10-03

`review/ruled/aoe-trim-2026-10-03.md`, all picks ruled 2026-10-03. Klee,
Furina and Varka come down to the base five's AoE range (10 AoE cards or
fewer, 7 direct or fewer); Kokomi keeps her delayed AoE. Built in the sim
first, then in C# once the sim read well (the same branch). Varka's two
(sec.4) are another branch's.

The C# side: codegen learned `bonus_if` on `damage` and `plant_bomb`, the
`enemies_with_bomb` count (`ProtoBombPower.EnemiesHoldingChargeFrom`),
`set_off` `mines_only` (`ProtoBombPower.SetOffMinesAimed` / `SetOffMines`), a
literal `times` inside a mode, the per-mode upgrade keys (play-time
`IsUpgraded` reads; the face swaps with `{IfUpgraded:show:...}`), and one
legal mode mixture: an all-enemies mode beside an aimed one aims the card
(Binary Form). New powers in `Powers/Prototype/PrincipleOfPurity.cs`; White
is summed over every player in `CompanionOverhaulReactions.DamageMultiplier`,
which feeds the amplifier and the Overload and Swirl splashes; Dark adds in
`ElementalHit.Deal` (Bombs, Mines, volleys) and in `ModifyDamageAdditive`
(cards). `DamageReportPower` gains Block; `AurousBlazePower` takes the card's
banked 3 (`ISummonDamagePower`) and answers its marker's Skills. Pins:
`KleeTests/Prototype/AoeTrimTests.cs`.

Klee (sec.2), AoE moved into Block and single-target burst:

- `proto_ko_bombs_away`: a Skill. "Place a Bomb 4 on an enemy. Gain 4 Block,
  plus 2 for each enemy with a Bomb." The count is the runtime count
  `enemies_with_bomb` (living enemies holding a charge, Mines included), read
  after the card's own Bomb lands, so the floor is 6. Upgrade still moves the
  Bomb (+2).
- `proto_ko_mine_toss`: "Place a Mine 7 on an enemy." Was Mine 4 on ALL.
- `proto_ko_mine_all_mine`: "Deal 8 Pyro damage. Set off the Mines on that
  enemy." The hit first, then `set_off` with `mines_only: true`
  (`klee_overhaul.set_off_mines`): only the Mines on the aimed body go off,
  plain Bombs stay; it spends The Big One and Boom Badge as a Set off does.
- `proto_ko_team_effort`: "Set off. Deal 6 Pyro damage, 6 more if you played
  a Companion card this turn." The `bonus_if: {if, amount}` rider on one
  damage op, so the upgrade (+3) moves the 6 and not the rider.
- `proto_ko_coven_errand`: "Place a Bomb 5 on an enemy, 8 if you played a
  Companion card this turn." The same rider on `plant_bomb` (+3); upgraded
  7, or 10.
- `proto_ko_red_knight`: 34 Pyro to one enemy, was 22 to ALL; upgrade +6.
- `proto_ko_damage_report`: "Whenever you draw a status, gain 4 Block."
  Power-sourced Block, raw (NC-11); upgrade 6.

Furina (sec.3): `proto_fs_undercurrent` is 3 damage 3 times to one enemy
(was 2 to ALL 3 times; upgrade still +2 hits). `proto_fs_endless_waltz` is
18 to one enemy (was 14 to ALL; upgrade +4).

Durin split in two (sec.5), names from his character sheet:

- `proto_mc_durin_binary_form`: Uncommon Attack, 1. "Choose one, then draw 1
  card. White: 6 [8] Pyro to ALL. Dark: 4 [5] Pyro to an enemy 3 times."
  The upgrade is `mode_damage: [2, 1]`, one number per mode in mode order.
- `proto_mc_durin_principle_of_purity`: Rare Power, 2. "At the start of
  your turn, deal 4 [6] Pyro damage to a random enemy. Choose one for the
  combat. White: Enemies take 50% [75%] more damage from Elemental
  Reactions. Dark: Your Pyro damage deals 4 [6] more." Powers
  `mc_purity_strike` (the stack is the damage), `mc_purity_white` (the stack
  is the percentage) and `mc_purity_dark` (flat). White is the team form,
  as the text says: every player's reactions, not only the holder's; the sim
  seats one player, so it reads the holder's. Dark adds to every Pyro hit
  she deals, Bombs and Mines included, in the additive phase before the
  amplifier; a reaction's splash is not Pyro damage. The upgrade is
  `power_amount: +2` (the strike) and `mode_power_amount: [25, 2]`. The old
  `mc_binary_white` / `mc_binary_dark` powers no row applies any more.

Yoimiya (sec.6): `proto_mi_yoimiya_aurous_blaze` is "Deal 6 Pyro damage.
For 2 turns, whenever you play a Skill, deal 3 Pyro damage to that enemy."
The 3 is the card's (`summon_damage:`), the mark's stack is turns
remaining, and the card's own play does not answer its own mark. The sim
had no clock for the mark before this (it lasted the fight); it now ticks
where the mod's end-of-turn walk ticks it, after War Banner.

Pins: `tier0/tests/test_aoe_trim.py`, and the rows' existing pins updated
in place. Measured: the tier-0.5 drafted run sim, base vs trim on the same
seeds (the session's results file).

## Klee finish-line batch, 2026-10-03

[USER], after his Klee finish-line run: "Agreed all around!" to five
changes, designed by the main session. Ruling recorded in
`review/active/klee-brief-2026-09-01.md`. Pins:
`KleeTests/Prototype/KleeFinishBatchTests.cs` and
`tier0/tests/test_klee_finish_batch.py`, with the old pins updated in place.

- `confiscated` (the token; C# `Cards/Confiscated.cs`): `CardType.Status`,
  was a Skill at Status rarity. [USER]: "Confiscated should be a Status, not
  a Skill? Was this deliberate? Prevents Klee's cards from removing it."
  Still 1 Energy and does nothing: the base game's Slimed is a playable
  Status (no Unplayable keyword; `CardModel.CanPlay` reads only the keyword,
  the cost and the hooks). The sim's `combat.card_playable` refuses every
  `type: status` card, so Confiscated is exempted there by
  `klee_overhaul.is_confiscated`; `tokens.yaml` says `type: status`. Both
  engines' `IsStatus` already counted Status rarity, so the readers (Klee
  Can Explain!, Kitchen Alchemy, Dust of Purification, Damage Report) see it
  either way; the type change also stops it counting as a Skill for every
  Skill reader. Solitary Confinement keys on the class / id, unchanged.
- `proto_ko_finders_keepers`: "Whenever you draw a status, place a Bomb 4 on
  a random enemy." Upgrade 4 -> 6. Was "Whenever you play a Confiscated,
  place a Bomb 5 [7]." [USER]: "Finders Keepers seems too niche to be
  useful". Damage Report's trigger in both engines:
  `FindersKeepersPower.AfterCardDrawn` (any status, per card drawn) and the
  sim's `klee_overhaul.finders_keepers` read at `refpowers.after_card_drawn`;
  the play listener is gone from `note_card_played`.
- Dodoco Tales (`ExplosiveFrags`, the Touch of Orobas upgrade of Pounding
  Surprise): adds "Start each combat with 4 more Sparks." to its face, so an
  upgraded Klee opens at 5 (the kit's 1 plus 4). [USER]: "a bump from 1
  starting sparks to 3 or 5 ... would be a much stronger increase", the
  Regent's 3 -> 7 stars as the yardstick. C#: `ExplosiveFrags.OpeningSparks`
  = 4, paid by `GrantOpeningSparks` from `KleeOverhaulOpening.GrantSpark`
  right after the kit's Spark (one site, so the relic is not a second tenant
  of `AfterPlayerTurnStart`). Sim: `touch_of_orobas_klee`'s
  `combat_start_spark` is 4 (was 3) and no longer gated off under the kit;
  `lint_constant_parity` mirrors the two. The first-explosion 2 stays C#
  only, as before.
- `proto_ko_mine_all_mine`: "Deal 8 Pyro damage. Place a Mine 4 on that
  enemy." Upgrade damage +3, Mine +2 (8 [11], Mine 4 [6]). [USER]: "how
  often do you have mines you want to detonate early?" The mines-only Set
  off is gone, and with it the engine piece no other row used: `set_off`
  `mines_only` in the codegen, `ProtoBombPower.SetOffMinesAimed` /
  `SetOffMines`, and the sim's `klee_overhaul.set_off_mines` and its
  `effects._op_set_off` arm. It is no longer a Set off card (the carrier
  count is 10).
- `proto_mc_amber_explosive_puppet`: rarity common -> uncommon, nothing
  else. [USER]: "probably too good to be a Common now. Exhaust tag, or bump
  to Uncommon?"; the main session chose Uncommon to keep it repeatable. A
  companion card, so Klee's 78-card pool counts do not move.

Art: none (no new cards).

## Varka starter: Retain Ascension, 0-cost Windbound, 2026-10-03

`review/ruled/varka-rebalance-2026-10-03.md`, end of sec.5. [USER]: "I do
think that we should consider modifying Ascension to be 2 cost with Retain,
similar to Regent's Sovereign Blade", and on Windbound: "What about making it
single target but 0 energy? It nerfs his AoE output but we already found that
we print too many AoE cards." Then: "Sounds good! Please proceed."

- `proto_vk_four_winds_ascension`: cost 1 to 2, `retain: true`, damage 6 to
  10 (upgrade +3, so 10 [13]); per-Oath 3 [4] unchanged. The Fang creates it
  with `CombatState.CreateCard`, which builds the canonical keywords, so the
  created copy retains (C# `CanonicalKeywords` carries `CardKeyword.Retain`;
  the sim's `_add_ascension` reads the row, whose `retain` the end-of-turn
  flush keeps). Wolf's Gravestone's "costs 0 this turn" still lapses at turn
  end on a retained copy (`SetThisTurn`; the sim's turn sweep clears
  `free_this_turn`).
- `proto_vk_windbound_execution`: cost 1 to 0, `target: enemy` (was
  `all_enemies`), text "Deal 4 [6] Anemo damage." It Swirls by the normal
  element rules; the Swirl's own flat damage and spread are untouched.

Pins: `KleeTests/Prototype/VarkaRebalanceTests.cs` and
`tier0/tests/test_varka_rebalance.py`, "the starter ruling".

## Varka weak cards, 2026-10-03

`review/records/varka-starter-round-2026-10-03.md`: each of these three was a
seat's weakest card in the starter round, so each gets a small number tune.

- `proto_vk_crosswind` (Crosswind): damage 7 [10] to 8 [11]; the Block on a
  Swirl 4 [6] to 5 [7]. First built at 9 [12], it overshot in the drafted
  sim (taken from 19% to 69% of offers, at the 70% bar), so it came back to 8.
- `proto_vk_jean_dandelion_breeze` (Jean — Wind Companion): unchanged at
  7 [10] Block. It was tried at 8 [11] and reverted because it crossed the 70%
  take bar in the drafted sim (70.8% of offers). The drafter already took it
  from 65% of offers at 7, so the seats' complaint is its aura timing, not
  its size.
- `proto_vk_dawn_winds_march` (Dawn Wind's March): cost 2 to 1; the upgrade
  no longer cuts the cost, it raises the Block per Oath gain 3 to 4. The face
  prints the number as `{PowerAmount:diff()}` so the upgrade shows.

## Varka Electro Knights, 2026-10-03

The main session's Electro census found the three Electro Knights with the
least face value. The default drafter took them from 0.1% (Infinite Circuit),
2.3% (Awakening) and 1.0% (Pulsating Witch) of offers. The numbers are the
main session's.

- `proto_vk_lisa_violet_arc` (Lisa: Infinite Circuit): Block 4 [5] plus 3 [4]
  per Attack becomes 6 [7] plus 3 [4]. Only the base moved; the upgrade is
  still +1 base and +1 per Attack.
- `proto_vk_razor_claw_and_thunder` (Razor: Awakening): 4 [6] becomes 5 [7],
  and the extra on an enemy with Electro goes from 3 to 4. It was tried at
  6 [8] first. The drafter took it from 81.4% of offers there, over the 70%
  bar, so the main session trimmed the base to 5.
- `proto_vk_lisa_pulsating_witch` (Lisa: Pulsating Witch): cost 1 becomes 0.
  The text and the Retain upgrade are unchanged.

The sim used `tools.varka_expansion_sim --seeds 2400 --seed 7 --jobs 15
--no-gauntlet` with the discard-sequencing pilot, and was paired against the
same pilot on the old numbers. These are act-1 win rates.

| read | old | new | paired |
|---|---|---|---|
| default drafter, all four starts | 31.0 | 30.8 | -0.2 ±0.6 |
| mono_electro | 8.5 | 14.3 | +5.8 ±1.1 |
| elem_electro | 22.2 | 30.2 | +8.0 ±1.3 |
| starter spread (P / H / E / C) | 31.0 / 31.1 / 31.7 / 30.1 (1.6) | 30.9 / 30.6 / 31.6 / 30.1 (1.5) | |

| card | taken, old | taken, new | played in, old | played in, new |
|---|---|---|---|---|
| Lisa: Infinite Circuit | 0.1% | 0.1% | 68.8% | 76.3% |
| Razor: Awakening | 2.3% | 62.2% | 49.4% | 58.1% |
| Lisa: Pulsating Witch | 1.0% | 1.0% | 37.2% | 94.9% |

The 6 [8] trial read: mono_electro 15.6, elem_electro 31.6, default 31.7,
starter spread 2.4, and Awakening taken from 81.4% of offers and played in
68.2%. The default drafter's take of the two
Lisas did not move, because it prices them by its own scores (the Block
formula, and the `varka` draw it does not see). Their play rate is the reading
that changed. Every Knight still feeds the Muster, switch and `elem_` decks:
paired, muster +8.8, switch +6.8, and elem_pyro, elem_hydro and elem_cryo
+4.8 to +6.7.

## Mondstadt companions, 2026-10-03

`review/ruled/mondstadt-companions-2026-10-03.md`, both picks ruled at their
defaults ([USER]: "Agreed on the Mondstadt pool changes you proposed.").

- `proto_mc_mona_stellaris_phantasm` (Mona — Stellaris Phantasm): cost 2 → 1,
  Exhaust kept; "Apply Hydro and 3 [4] Vulnerable to ALL enemies." The
  Vulnerable lands on play. The next-turn promise (`mc_omen`,
  `StellarisOmenPower`, `C.MC_OMEN_VULNERABLE` / `OmenVulnerable`) had no
  other user and is deleted in both engines.
- `proto_mc_noelle_breastplate` (Noelle — Breastplate): Block 6 → 8, upgrade
  +3 (8 [11]); the 4 more below half HP stays.
- `proto_mc_sucrose_gust` (Sucrose — Wind Spirit Creation): cost 0 → 1;
  "Swirl ALL enemies. Draw 1 [2] card." Not Exhaust. Its Klee stand-in
  Mollis Favonius keeps cost 0, so the stand-in cost pin exempts that pair.
- `proto_mc_amber_fiery_rain` (Amber — Fiery Rain): 4 → 3 Pyro per hit to
  ALL, 3 times; upgrade +1 per hit (3 [4]).

## Klee-only companions, 2026-10-03

`review/ruled/mondstadt-companions-2026-10-03.md` sec.4 ([USER]: "Yeah,
agreed on all of these."; Kitchen Alchemy kept, "it's quite good!", Once More!
cut instead).

- To the shared Mondstadt roster (`C.MONDSTADT_OVERHAUL_POOL_IDS`, 35 to 39):
  `proto_mc_qiqi_herald_of_frost` (was a coven Personal),
  `proto_mc_fischl_sinful_hex`, `proto_mc_sucrose_mollis_favonius`,
  `proto_mc_nicole_ladder_of_ascent` (were stand-ins; `personal_pool:` and
  `replaces:` both dropped).
- Into Klee's draftable pool, last (`C.KLEE_OWN_COMPANION_IDS`):
  `proto_mc_jean_lions_fang`, `proto_mc_prune_hexhunter_chime`,
  `proto_mc_albedo_dust_of_purification`. Ids, text, numbers and rarity
  unchanged; still Companion cards.
- Cut: `proto_mc_barbara_front_row_seat`, `proto_mc_diona_shaken_not_purred`,
  `proto_mc_noelle_i_got_your_back`, `proto_mc_kaeya_cold_blooded_strike`,
  `proto_mc_sayu_silencers_secret`, `proto_mc_yaoyao_yuegui_throwing_mode`,
  `proto_ko_second_surprise`, `proto_ko_solitary_confinement`,
  `proto_ko_once_more`. Their powers and the engine pieces only they used are
  deleted in both engines. Klee stays 78, 24 / 33 / 21.
- The stand-in table (`C.COMPANION_STANDIN_IDS`, `CompanionStandIns.Pairs`)
  and the coven Personal list (`C.COVEN_PERSONAL_POOL_IDS`,
  `CompanionCovenRoster.Personals`) are empty; the seams stay.

## Varka Wildfire Oath and Short Circuit, 2026-10-03

[USER], after a Varka run in which Wildfire Oath "felt like a bit of a dud
... basically acts as a low form of vigor for 2 energy" and an Electro combo
"didn't pan out": "I think the Wildfire Oath and Electro Discard need a fix
(agreed on your suggestion for Wildfire Oath)". The numbers are the main
session's.

- `proto_vk_wildfire_oath` (R Power, cost 2, upgrade Innate): "Your first
  Attack each turn deals additional damage equal to half your Pyro Oath"
  becomes "Whenever you apply Pyro to an enemy, deal damage equal to your
  Pyro Oath to it." It is Absolute Zero's shape for Pyro: element-less,
  unpowered, once per stack, to the enemy the Pyro landed on.
  **Order:** it pays inside the application hook, after that application's
  own Oath credit. The Pyro Oath it reads already includes the point this
  application earned, when it earned one (once per play, by the Oath rules).
  Both engines do it this way: C# `VarkaOath.NoteApplication` calls
  `WildfireOathPower.OnPyroApplied` after `Gain`, and the sim's
  `varka_oath.note_hit` calls `_wildfire` after `credit`. Each later Pyro hit
  in the same play also pays, at the same Oath, because it credits nothing
  more. Its damage carries no element, so it cannot trigger itself. The old
  first-Attack pieces are deleted: C# `TakeFirstAttack`, `WildfireCard`,
  `WildfireStacks`, `WildfireBonus` and the power's damage hooks; sim
  `take_wildfire`, `wildfire_armed` and `first_attack_turn`.
  `NoteApplication` now takes the target enemy. The aura door
  (`KleeElementalHooks.BeforeDamageReceived`) puts no aura on an enemy that
  this payment, or Assembly's, has just killed.
- `proto_vk_short_circuit` (U Skill, cost 0, not Exhaust): "Discard 3 [2]
  cards. Gain 2 Energy. Apply Electro to an enemy." becomes "Discard 2
  cards. Draw 2 [3] cards. Gain 1 Energy. Apply Electro to an enemy." The
  upgrade is now draw +1. The sim showed why the old card failed: discarding
  3 of a five-card hand left nothing to spend the Energy on, so Chain
  Lightning almost never followed it.
- The sim pilot's discard sequencer (`_electro_pick`, an instrument surface)
  still plays Short Circuit as the discard enabler before Chain Lightning.
  It reads the discard, draw and Energy amounts off the card. A draw counts
  as the draw pile's median card by value; the pilot never reads the pile's
  order.

The sim ran `tools/varka_expansion_sim.py --seeds 2400 --seed 7 --jobs 15
--no-gauntlet` on origin/main (before) and on this branch (after). It is
paired, and the figures are act-1 win rates.

| read | before | after | paired |
|---|---|---|---|
| default drafter, all four starts | 30.8 | 30.8 | +0.0 |
| mono_pyro | 27.8 | 28.0 | +0.1 ±0.2 |
| elem_pyro | 37.7 | 37.8 | +0.1 ±0.1 |
| mono_electro | 14.3 | 18.5 | +4.3 ±0.9 |
| elem_electro | 30.2 | 34.5 | +4.3 ±0.9 |
| starter spread (P / H / E / C) | 30.9 / 30.6 / 31.6 / 30.1 (1.5) | unchanged (1.5) | |

| card | taken, before | taken, after | played in, before | played in, after |
|---|---|---|---|---|
| Wildfire Oath | 12.6% | 12.6% | 98.5% | 98.3% |
| Short Circuit | 0.0% | 0.0% | 95.4% (1.50 a fight) | 98.5% (1.73 a fight) |
| Chain Lightning | 17.6% | 17.6% | 68.9% | 70.0% |

The default drafter's take did not move for either card, because it prices
them by its own scores. No card is newly over the 70% take bar; the flagged
list is unchanged. A separate probe ran 400 seeds per deck, act-1 runs. It
counted Chain Lightning played after a discard card in the same turn: 2 of
203 before and 28 of 226 after (mono_electro), and 1 of 243 before and 35 of
273 after (elem_electro). Short Circuit was the turn's first or second play
107 of 513 times before and 613 of 713 after (mono), and 138 of 624 before
and 678 of 783 after (elem). Wildfire Oath is a Rare and is held in few
fights. Its triggers paid 2.0 damage each before (81 triggers, mono_pyro)
and 4.2 each after (71 triggers).

## Furina run notes: the fade at turn start, Tutti!, Gala Premiere, 2026-10-03

[USER]'s run notes: "Fanfare decay should be at the start of the next turn,
not the end." Rule 12's fade moved from the end of her turn (after the acts)
to the start of her next turn (`FurinaStage.TurnStartFade`, sim
`furina_stage.turn_start_fade`), same amount. Two rows changed:
`proto_fs_tutti` costs 1 (was 2) and its upgrade is Retain (was cost -1);
`proto_fs_gala_premiere` costs 1 (was 2), 0 upgraded, and keeps Exhaust.
Brief: `review/active/furina-stage-brief-2026-09-08.md` sec.20.

## Klee pre-Balance sweep, 2026-10-03

[USER]: "let's do one last rundown of her kit right now and just sanity check
that no cards seem obviously bad (low numbers / overly specific combo pieces)
or completely redundant with another card". The main session's rundown moved
six rows:

- `proto_ko_all_of_my_treasures`: cost 1 -> 2, keeps Exhaust. "Place a Bomb
  the size of your largest Bomb on ALL enemies." The size is read once before
  anything is placed; each living enemy gets a plain Bomb (never a Mine);
  nothing with no Bomb out (`ProtoBombPower.PlaceCopyOfLargestOnAll`, sim
  `klee_overhaul.place_copy_of_largest_on_all`). Upgrade: Retain (was
  Exhaust off).
- `proto_ko_coven_errand`: Bomb 5 / 8 -> 8 / 12 (upgraded 10 / 14).
- `proto_ko_alices_introduction_magic`: adds "Draw 2 cards." after the mark,
  so the drawn cards are not marked. Upgrade stays Retain.
- `proto_ko_damage_report`: "Whenever you draw a status, gain 4 Block and 1
  Spark." The Spark goes through `SparkPower.Gain` / `gain_sparks` (source
  `power:damage_report/status_drawn`), so Spark readers see it; flat 1 at both
  levels (`KleeOverhaulLaw.DamageReportSpark` = `C.KLEE_OVERHAUL_DAMAGE_REPORT_SPARK`).
  Upgrade moves the Block, 4 -> 6.
- `proto_ko_blast_shield`: Block 6 -> 4, upgrade +2 (-> 6). The kit prices a
  Spark at about half to two-thirds of an Energy (Sparkling Burst: 2 Sparks
  -> 1 Energy; Booby Trap's Mine 5 per Spark against Mine Toss's Mine 7 per
  Energy). Dig In at 8 is already generous, and Blast Shield turned the whole
  Spark bank into Block at that rate from one card. [USER]: "Spark-starved
  decks would skip blast shield - spark heavy decks treat it as 'I'm
  invincible this turn'."
- `proto_ko_dig_in`: stays Block 8; its upgrade (+3, 11) is now stated on the
  row rather than taken from the Prototype-stage default. Same card.

Countdown was on the list for draw 2 (3 upgraded); the row already read that
(since the playtest-one fixes), so it did not move.

## Klee "Set off the enemy." wording, 2026-10-03 (text only)

Three of four blind seats in the 2026-10-03 round read a targeted card's bare
"Set off." as setting off every enemy's Bombs; it sets off only the targeted
enemy's, and Tinder Toss already prints "Set off ALL enemies." Every aimed
row that printed the bare form now reads "[gold]Set off[/gold] the enemy.",
the rest of each face unchanged and no effect moved: `proto_ko_kapow` (the
starter; mechanics untouched), `proto_ko_big_badda_boom`,
`proto_ko_the_big_one`, `proto_ko_quick_fuse`, `proto_ko_bang_bang`,
`proto_ko_sizzle`, `proto_ko_perfect_timing`, `proto_ko_countdown`,
`proto_ko_team_effort`, `proto_ko_duck_and_run`.
`proto_ko_flash_point` keeps the bare form for now: the new wording puts
its face at 121 of the 120-character card ceiling, and the trim is a design
call, not a lint exception. `KleeCardTooltips.SetsOffFirst` keys on both
openings. A fourth seat read a
Mine as failing because a Set off had already spent it, so the Mine tip gains
"Any [gold]Set off[/gold] spends it too."

## Spent auras removed, 2026-10-03

[USER]: "Should we get rid of the concept of elements being 'spent' after a
swirl? It seems to generate confusion." then "agreed ... please proceed".
Every reaction now consumes its aura, Swirl and Crystallize included. A
Swirl's copies are ordinary fresh auras, so "fresh aura" means any aura. The
text changes, with no number moved:

- `proto_vk_gale_sweep`: "each enemy with a fresh aura" becomes "each enemy
  with an aura". The `only_if: fresh_aura` token keeps its name and now takes
  every aura.
- `proto_vk_jean_dandelion_breeze`, `proto_vk_crosscurrent`: "an enemy's
  fresh aura" becomes "an enemy's aura".
- `proto_vk_wall_of_gales` and the Bottled Gale potion: "Swirl every fresh
  aura" becomes "Swirl every aura". The `swirl_fresh_auras` kind keeps its
  name.
- `proto_vk_downburst`: "If it Swirls, the copies it spreads arrive fresh."
  is struck, because every copy now arrives fresh. The card is "Deal 12 [16]
  Anemo damage." until the main session gives it a new rider.

Sim, `tools/varka_expansion_sim.py --seeds 2400 --seed 7 --jobs 15
--no-gauntlet`, paired, act-1 win rates, before / after: default 30.8 /
29.2 (-1.6 ±0.6); starter spread 1.5 / 2.0 points; mono_electro 18.5 / 19.6,
mono_cryo 16.0 / 17.4, mono_hydro 29.7 / 31.5; elem_* within 1.3 points.
The 70% take flags and the dead-play list did not change.

## Downburst's new rider, 2026-10-04

- `proto_vk_downburst`: "Deal 12 [16] Anemo damage." becomes "Deal 12 [16]
  Anemo damage. If it Swirls, gain 2 Oath of the element Swirled." (main
  session, after spent auras were removed, #882). The 2 is on top of the
  Swirl's own per-card credit and is one gain through Varka's Oath door
  (`VarkaOath.Gain`, sim `varka_oath.gain`), so Oath Unto Death, Dawn Wind's
  March and Boreas's Fang see it. New `varka` kind `swirled_oath`
  (`VarkaCards.SwirledOath`). Upgrade unchanged: damage +4.

Sim, `tools/varka_expansion_sim.py --seeds 2400 --seed 7 --jobs 15
--no-gauntlet`, paired, before / after: Downburst taken 1.2 / 1.2% of
offers, played in 68.0 / 80.8% of fights held (0.83 / 1.00 plays a fight).
Act-1 win rates moved by at most 0.1 point. The 70% take flags did not
change.

## Furina re-founding, 2026-10-04

Every row of `review/ruled/furina-refounding-2026-10-03.md` sec.10 (and
sec.9's slice rows), built on the old ids. The rules are sec.1 as sec.8
amends them; the sim's reference is `tier0/engine/furina_v2.py`.

- Renamed on their old ids: `proto_fs_plot_twist` (Encore!),
  `proto_fs_interposition` (Places, Everyone!), `proto_fs_counterclaim`
  (Dress Rehearsal, now an Uncommon Power), `proto_fs_leading_lady`
  (Gentilhomme Usher, now a Common), `proto_fs_double_casting` (Premiere
  Season, now a Rare Power), `proto_fs_quick_cue` (Quick Flourish, name
  only). The two rarity moves leave the pool at 78, now 24 / 33 / 21; in the
  sim both rows are `POOL_ADDS` and their old shipped twins `POOL_DROPS`. The
  renamed rows keep their paintings, which still show the old cards.
- Rewritten to the sheet: the starter's Rising Applause, Take the Stage,
  Mademoiselle Crabaletta (its 4 damage carries Hydro under her Skill
  cadence, so the face names it), Encore!, Stage Whisper, Places, Everyone!,
  Step Forward, Warm Reception, Hold Your Places, Cheered On, Opening Number,
  Ousia Surge, Pneuma Refrain, Bravura, Bis!, Final Bow, Intermission, Dress
  Rehearsal, Revolving Stage, Thunderous Applause, Season Tickets,
  Groundswell, Tide of Applause, the ten Guest Stars, Let the People Rejoice,
  Bring the House Down, A Five-Century Act, Premiere Season, Gala Premiere,
  Grand Deluge, Endless Waltz, Critics' Darling, Singer of Many Waters, and
  the five co-op rows.
- Exhaust stays on Final Bow, Let the People Rejoice, Singer of Many Waters
  and Gala Premiere: sec.10 gives text and numbers, and keeps every row it
  does not list unchanged.
- Raise a Toast is a Spend 4 mode (the Spend is a choice on play, as on every
  Spend card); its 4 [6] Strength is read off `IsUpgraded` inside the mode.
- New sheet vocabulary: `stage_cue {times}`, `stage_perform_all {guests}`,
  `stage_spend_all` (spend all of her Fanfare), counts `fanfare_gained` and
  `fanfare_spent`, powers `fs_rehearsal` and `fs_premiere_season`. Retired:
  the seat-moving, per-performer spend and Intermission ops, the lead and back
  Fanfare counts, `stage_front_hit`, `fs_rapt_audience`, `fs_guest_of_honor`.

## Furina loop fix (2026-10-04)

Two infinite loops the v2 reviewers found, fixed as the main session designed
them; `tier0/harness/furina_loop_probe.py` catches both with the fixes taken
out (`--pre-fix`) and pins the rest of what it finds
(`tier0/tests/test_furina_loop_probe.py`).

- **`proto_fs_salon_debut`** (Take the Stage): the upgrade was cost 1 to 0
  ("Summon a random Salon member. Draw 1 card."). Two copies in a thinned
  deck drew each other forever, and every play onto a full stage Bowed a
  performer (+1 Fanfare): after 100 plays Energy was unchanged and Fanfare
  was up 98 (GPT). Now it stays at 1 Energy and draws 2 upgraded.
- **`proto_fs_interval_bell`**: the Spend mode's Energy comes next turn
  ("Spend 3: draw 1 card and gain 1 Energy next turn instead"; Spend 2
  upgraded). With Warm Reception (1: gain 3 Fanfare, draw 1), Interval Bell+
  (0: Spend 2, draw 1, gain 1 Energy) paid for its partner and netted +1
  Fanfare a pass (Fable). The new op `stage_energy_next` is Chevreuse's
  mechanism: `Player.stage_energy_next` in the sim, the game's
  `EnergyNextTurnPower` in C# (`FurinaStage.EnergyNextTurn`).

## Kokomi big-Plan pass, 2026-10-04

A friend's solo run called every Rare of hers weak; Masterstroke was "3 Cost
that does less damage THE TURN AFTER Regent's Uncommon 1 cost 4 star
(Devastate)". The reading: Open the Casket's Strength is added once per Plan
hit, so at 6 Strength a 0-cost Nip lands 11 and a 3-Energy Masterstroke 36.
[USER]: "Can we leave Casket alone and still make big plans work somehow?"

- **`proto_kk_masterstroke`**: "Strength affects this Plan 3 times."
- **`proto_kk_surging_shoal`**: "Strength affects this Plan twice." (the Plan
  line only; the now-line takes Strength once, as any Attack does).
- Undertide Lance is left alone: its Plan already doubles alone, Strength
  included.
- New clause field `strength_times` on a flat `damage` Plan clause (a literal
  int of 2 or more), read by `kokomi_plan.hers` and `KokomiPlan.Hers` when the
  Plan is written; `Planned.StrengthTimes` and `PlanDamageVar` carry it in C#.
  At 6 Strength: Masterstroke 48, Surging Shoal 34, Nip 11.

**The sim does not see it** (`tools/kokomi_expansion_sim.py`, n = 400 paired,
seed 7; exploration, not quotable). Gauntlet, share of fights won, Big Plan
against Plan volume: 44.4 against 54.4 before, 44.5 against 54.5 after. With
the pilot opening the Casket at 3 (`--open-at 3`, new): 46.5 against 57.0
before, 46.5 against 57.1 after. Its fights last about 7 turns with the
Casket near 1 to 2, so the pilot holds little Strength; the 10-point gap in
the sim is therefore not a Strength gap, and this pass does not close it. The
change is aimed at the long fights and large Caskets of a human run. No seat
round was run: [USER] may play it in co-op first.

## Furina: the Salon's Tab, 2026-10-05

The slice of `review/active/furina-research-proposal-2026-10-05.md` sec.16,
with sec.17's two edits (Curtain Rise's Drain mode deals 12 [16]; Universal
Revelry reads "You gain twice as much Fanfare."), replaces the v2 Stage in
place. [USER]: "the current one built overnight can be discarded." The pool is
exactly the starter and 24 rows; every other v2 row, the five co-op rows and
all Furina relics and potions but Opera Glasses, Grand Theater Program and
Bottled Applause are gone. The frozen v2 build is the tag
`furina-stage-frozen-2026-10-04`; the sim's reference is
`tier0/engine/furina_tide.py`, which the arm now runs on.

- New ids: `proto_fs_salons_tab`, `proto_fs_surging_waters`,
  `proto_fs_hymn_of_many_waters`, `proto_fs_salons_encore`,
  `proto_fs_soloists_solicitation`, `proto_fs_standing_ovation_all` (Standing
  Ovation; its old id is Rising Applause's) and `proto_fs_universal_revelry`.
  The last three wear their shipped pictures through `art_of`; the first four
  have no art yet and use the placeholder path.
- Kept ids, rewritten to the slice: Curtain Rise, Rising Applause,
  Mademoiselle Crabaletta, Surintendante Chevalmarin, Gentilhomme Usher
  (`proto_fs_leading_lady`), Pneuma Refrain, Singer of Many Waters, Tidal
  Flourish, Spirited Aria, Quick Flourish (`proto_fs_quick_cue`), Interval
  Bell (now a Common, as the slice lists it), Bravura, Endless Waltz (now an
  Uncommon Power), Thunderous Applause, Let the People Rejoice (no Exhaust:
  the slice prints none) and the four Guest Stars (Charlotte, Wriothesley,
  Lynette, Clorinde; "Summon X.", upgrade cost -1).
- Wording calls where the slice was open, each the plainest base-game shape:
  Salon's Tab's upgrade (Draw +1) lands in both modes; Gentilhomme Usher's Drain mode upgrades through the new
  `conditional_then_block` key (`conditional_then_damage`'s block twin).
- New sheet vocabulary: ops `stage_drain` (a mode's head or a card's fixed
  price), `stage_repay`, `stage_repay_all`; upgrade keys `stage_repay`,
  `conditional_then_block`, `mode_draw`; powers `fs_salons_encore`,
  `fs_endless_waltz`, `fs_thunderous_applause`, `fs_universal_revelry`.
  Retired with v2: `stage_summon`, `stage_raise`, `stage_cue`,
  `stage_perform_all`, the co-op ops and every v2 power.
- **Salon's Tab, the main session's ruling (2026-10-05):** cost 1, "Draw 2
  cards. Drain 4: also gain 2 Energy next turn." [Draw 3]. At cost 0 it
  made every upgraded Guest Star with two Tab+ an infinite (a re-summoned
  guest acts and stays); at cost 1 each cycle is paid out of this turn's
  Energy. The loop probe now finds no productive cycle.

## Kokomi Rare pass, 2026-10-04

The rest of the review of a friend's solo run ("why every single one of
planning girl's legendary cards is bad"). [USER]: "Can you do the rest of the
proposed changes as well?" The proposal was to rewrite the four Rares that
were a Common one size up, make the Nips she is handed Exhaust, and fix
Kurage Swarm's text. No rule changed and the Casket is untouched.

- **`proto_kk_shoal_of_spears`**: "Deal 4 [5] Hydro damage to ALL enemies
  once for each Plan you wrote this turn." It was one hit of 4 per Plan,
  Tideturn's rate made AoE ("likely to only do 8 - 12"). As separate hits her
  Strength and the enemy's Vulnerable count on each. Still nothing with no
  Plan written. `times: plans_written_this_turn` is new to the generator's
  `RUNTIME_TIMES`; the sim already read the token.
- **`proto_kk_tidal_rebuke`**: cost 2 [1] to 1 [0], and Retain. At 2 it was
  her own Common, Coral Crash, at double the price in a one-enemy fight ("A 2
  Cost legendary that has the same effect as a 1 cost common").
- **`proto_kk_the_moon_a_ship`**: cost 2 to 1. Its Block half was the
  Regent's Uncommon Bulwark (12 Block and Forge 10 for 2) without the Forge
  and with Exhaust. Mend is unchanged.
- **`proto_kk_suffocating_deep`**: applies 1 Weak and 1 Vulnerable to every
  enemy before it doubles, so the floor is Weak 2 and Vulnerable 2 ("might
  apply weak 2 and vuln 2").
- **The Nips she is handed Exhaust** when played, as a Shiv does: Shoal
  Call's, Watatsumi Resistance's, and Kurage School's copies ("you fill up
  your deck with 0 cost cards. If the clones were Exhaust it would be good").
  A drafted Nip is unchanged. `kokomi_plan._exhausting`,
  `KokomiCards.Exhausting`.
- **`proto_kk_kurage_swarm`**: text only, "the Casket gains 1 more". The
  friend read it as the carry-out's 1 ("Pointless bc every plan gives 1
  casket anyways"); it has always been 1 on writing as well.

Considered and not built: Tidal Rebuke as a Dusk Plan ("Dusk Plan: Deal
damage equal to your Block to ALL enemies"), which would read her Block after
the turn's other Dusk Plans land. It needs a new Plan clause in both engines.
Not touched: Ceremonial Garment, What the Tokoyo Took, The Long Game, Patient
Tide, Grand Design. No sim and no seat round were run.

## Varka combo pass, 2026-10-04

Paper `review/ruled/varka-combo-pass-2026-10-04.md`, RULED 2026-10-04, all
four picks at their defaults with Baron Bunny amended ([USER]: "Let's leave
the Baron Bunny's block alone for now, but nerf the attack from 'all
enemies' to 'one enemy at random.' ... I'm good with this proposal."). The
card designs are the main session's; this note records the build.

- **Five generic Block cards out (sec.2):** Gale Mantle (C), West Wind
  Shield (C), Knightly Guard (C), Tailwind Guard (U) and Oath of the Knights
  (U). Their rows, generated classes and pool entries are deleted, and so is
  `OathOfTheKnightsPower` with its turn-start Block (C# `VarkaOath.TurnStart`,
  sim `varka_oath.turn_start`). The counts they read (`half_total_oath`,
  `enemies_with_aura`, `oath_elements`) stay as grammar no row prints. Their
  paintings stay on disk as `KNOWN_STALE` in `tools/art_coverage.py`.
- **Amber: Baron Bunny:** the next-turn hit is "deal 6 [8] Pyro damage to a
  random enemy" (was ALL enemies); Block 6 [8] unchanged. Reading: two
  Bunnies stack into one power and one hit of 12 at one random living enemy,
  not two hits of 6 (`VarkaBaronBunnyPower.Fire`, `Rng.CombatTargets`).
- **Pyro burns (sec.3):** Stoke the Flames (C Skill 1: "Exhaust a card. Gain
  2 [3] Pyro Oath."), Ember Cleave (C Attack 1: "Deal 9 [12] Pyro damage.
  Exhaust a card.") and Pyre Oath (U Power 1: "Whenever you Exhaust a card,
  gain 1 Pyro Oath." [Innate]). "Exhaust a card" is True Grit+'s: the player
  chooses from the hand (`exhaust_from`, `select: chosen`), and any card can
  go, a Status or a Curse included; the chooser that excludes junk is
  Kokomi's rotation law and stays hers (the codegen picks the selector by
  owner). The Oath is a gain, not an application, so neither card switches
  his element. Pyre Oath pays one gain of its stack per card exhausted, any
  route (C# `PyreOathPower.AfterCardExhausted`; sim
  `varka_oath.on_card_exhausted` from `refpowers.after_card_exhausted`). In
  the sim a mid-play exhaust is swept after the play, so Stoke's own +2 lands
  before Pyre Oath's +1; in C# the hook fires at the exhaust. The total is
  the same.
- **Cryo shatters (sec.4):** Shatter (C Attack 1: "Deal 5 [7] Cryo damage,
  plus 2 [3] for each Weak and Vulnerable on the enemy.") counts stacks, read
  before the hit, and prints its total in combat as `{VkHit}` through a new
  display var, `VarkaShatterDamageVar`, against the aimed enemy (the front
  one in hand, the `FrontFoldedDamageVar` rule) with Cryo carried. Deep
  Freeze (U Skill 1, Retain: "Apply Cryo to an enemy. Double its Weak and
  Vulnerable.") doubles each by applying what the enemy holds, so Absolute
  Zero pays on it. **Its upgrade, cost 1 to 0, was the builder's proposal, confirmed by the main session 2026-10-04**
  and waits on the main session.
- **Unwavering Banner reworded:** "Only Knights can change your current
  element. Whenever another card would, gain 1 Oath of your current element
  instead." [Innate]. Readings: the "instead" Oath is paid once per card
  play however many switches the card would make (Tempest of the Four Winds
  would make three), and only when it would have been a change (another
  element is current; with none current nothing is gained). Change of Guard
  is a card and is held the same way: no grid, 1 Oath of the current element
  when another element could have been chosen. Weathervane is held too (the
  old "cards that name it" exception is gone from the text) and, being a
  Power rather than a card, gains nothing. The Fang's combat-start element
  is unaffected: it always lands before the Banner can be played.
- **Sec.1 fixes:** Charge of the Knights cost 2 to 1 and 5 [7] per Knight
  (was 5 [6]); Jean — Lion's Fang, Fair Protector (Klee's pool) upgrades
  cost 2 to 1 (was the Prototype default, 8 to 9 Block); Kaeya: Heart of the
  Abyss and Razor: Awakening are Attacks; Thundering Verdict reads "Deal 6
  [8] Electro damage, plus 1 for each Electro Oath, to ALL enemies X times."
  with its per-hit preview kept; Converging Winds reads "The elements your
  Swirls spread set off Elemental Reactions." with the same behaviour.
- **Four Winds' Ascension (pick 3):** the upgrade is cost 2 to 1, in place of
  +3 damage and +1 per Oath. The Dusty Tome still hands it upgraded.

The pool stays 78 (20 / 35 / 23): Commons lost Gale Mantle, West Wind
Shield and Knightly Guard and gained Stoke the Flames, Ember Cleave and
Shatter; Uncommons lost Tailwind Guard and Oath of the Knights and gained
Pyre Oath and Deep Freeze.

**Yardsticks, read off the game's own card data** (`game_ref/ironclad.json`,
`game_ref/silent.json`, `game_ref/ironclad-cards.yaml`): True Grit is an
Ironclad Common, cost 1, 7 [9] Block, exhausting a card from the hand
(random; the upgrade lets the player choose). Feel No Pain is an Ironclad
Uncommon Power, cost 1, 3 [4] Block whenever a card is exhausted. **Catalyst
is not in the StS2 Silent pool** (91 cards in `silent.json`, none by that
name and none that doubles Poison), so Deep Freeze's yardstick has no base
twin in this game. No number moved for them.

**Sim** (`tools/varka_expansion_sim.py --seeds 1500 --seed 7 --jobs 15
--no-gauntlet`, origin/main before, this branch after, paired seeds, act-1
win rate). The pyro and cryo `PAYOFFS` lists gained the new cards, so the
forced Pyro and Cryo decks draft them.

| deck | before | after | paired |
|---|---|---|---|
| default drafter, all four starts | 46.9 | 40.5 | -6.3 ±1.6 |
| elem_pyro | 53.7 | 38.9 | -14.8 ±3.2 |
| elem_hydro | 52.4 | 46.1 | -6.3 ±3.3 |
| elem_electro | 52.7 | 46.7 | -6.0 ±3.3 |
| elem_cryo | 42.8 | 42.8 | +0.0 ±3.1 |
| mono_pyro | 43.8 | 29.1 | -14.7 ±3.1 |
| mono_hydro | 47.5 | 41.6 | -5.9 ±3.5 |
| mono_electro | 36.7 | 29.8 | -6.9 ±3.2 |
| mono_cryo | 37.5 | 38.9 | +1.3 ±3.1 |
| switch | 47.4 | 45.4 | -2.0 ±1.6 |

Against the default drafter on the same start, after: elem_pyro -2.1,
elem_hydro +5.4, elem_electro +9.7, elem_cryo -0.7, all within 10; mono_pyro
-11.9 is outside. The starter spread widened from 3.2 to 6.5 points (P 41.0,
H 40.7, E 36.9, C 43.5). Block a fight, default drafter: 33.7 to 29.8.

**The bar "Pyro and Cryo up" is not met.** Cryo is flat; Pyro fell about 15
points. A diagnostic run (same seeds, the new pool, the Pyro decks not
forced to draft the three new Pyro cards) put elem_pyro at 46.5 and
mono_pyro at 34.1: about half of Pyro's fall is the cuts and Baron Bunny's
nerf, and half is the pilot drafting and playing the new Pyro cards badly.
The stock pilot prices an Exhaust at nothing outside Kokomi's Casket engine
(`policy`'s `exhaust_from` value is gated on her engine), so it plays Stoke
the Flames in 43% of the fights that hold it (0.46 plays a fight), the
lowest of the new cards, and its victim is the stock "lose the least" pick,
not a plan for Pyro Oath.

| card | taken (default) | played in | elite+boss won with / without |
|---|---|---|---|
| Stoke the Flames | 18.7% | 43.3% | 61.0 / 77.1 |
| Ember Cleave | 16.3% | 85.2% | 74.4 / 75.9 |
| Pyre Oath | 16.2% | 97.4% | 62.0 / 76.2 |
| Shatter | 17.8% | 77.6% | 71.9 / 76.2 |
| Deep Freeze | 0.0% | 52.9% | no default-drafter fights |
| Unwavering Banner | 19.0% (18.2 before) | 98.1% | 60.5 / 76.3 |

No new card is over the 70% take bar. None is dead by the sim's flag
(played in under 5% of fights held), but Stoke the Flames and Deep Freeze
are played in about half the fights that hold them, and the default drafter
never takes Deep Freeze (0 of 1,772 offers, as with Glacial Edict and Tidal
Bulwark). Charge of the Knights is played in 60.7%
of fights held (45.5% before) and taken 1.9% (0.0%).

## Varka seat-round fixes, 2026-10-05

From the combo pass's seat round (review/records/varka-combo-round-2026-10-05.md,
"What to change" 1 to 3). No number moves.

- **Stoke the Flames** (`proto_vk_stoke_the_flames`): "Exhaust a card. Gain 2
  [3] Pyro Oath. Pyro becomes your current element." Played off-element, the
  old card gave Pyro Oath nothing read; now it can start a Pyro deck. The gain
  lands first, then the switch, so the gain is not yet the current element's
  (Dawn Wind's March and Oath Unto Death do not see it). The switch is a
  non-Knight card's: it goes through `VarkaOath.CardMakesCurrent` (sim:
  `varka_oath.card_makes_current`), the open Oath's fork, so Unwavering Banner
  holds it and pays 1 Oath of the current element instead.
- **Icebreaker** (`proto_vk_shatter`), was "Shatter": the title was also the
  Frozen keyword's word, and a seat called it confusing. Text and id unchanged,
  so the art and coverage lists, keyed on the id, hold. The keyword keeps its
  name.
- **Tempest Charge** (`proto_vk_tempest_charge`): checked, not changed. The
  Swirl resolves inside the card's own attack (AuraPower's
  AfterDamageReceived, then ReactionEffects.Resolve, then VarkaOath.OnSwirl,
  which counts it on the dealer, the card's Owner.Creature) before the
  `swirled_by_this` re-read, so the draw fires. The seat page carries no draw
  event, only the hand after the play, which is why the seat could not see it.
  Pinned by `Tempest_charge_reads_its_swirl_after_the_hit_and_before_the_draw`.

## Kokomi kit review, 2026-10-05

The main session's whole-kit review of Kokomi: two cards to rate, one
upgrade that did nothing, five wording fixes, stale comments. No rule
changed.

- **`proto_kk_ceremonial_garment`**: cost 2 to 1, and 2 [3] per debuff (it
  was 1 [2]). A 2-cost Rare giving +1 per debuff (+2 a hit on a Weak and
  Vulnerable target) sat under an Uncommon Inflame. The face's shape is
  unchanged: "Your Attacks deal 2 [3] additional damage for each debuff on
  their target."
- **`proto_kk_deep_current`**: 7 [9] to ALL becomes 8 [11] to ALL, Cleave's
  numbers. Cleave is Slay the Spire 1's; `game_ref/ironclad.json` (Slay the
  Spire 2) has no Cleave, and its AoE Common is Breakthrough, 9 [13] to ALL
  for 1 HP.
- **Open the Casket** (the relic's hand-written token, `OpenTheCasket.cs`,
  sim `kokomi_plan.open_the_casket_card`): its upgrade changed nothing.
  Upgraded, it also draws 1 card after the Strength. Cost 1 and Retain stay.
  The hover tip describes the base card and is unchanged.
- **Wording, no rule change.** Breakwater, Opening Gambit and Second Wave
  gold the bare "Plan". Divine
  Strategy (card and `DivineStrategyPower`) used an undefined word, "its
  now-line happens too"; it reads "The first time each turn you play a card
  on the Bake-Kurage, the line above its Plan happens now too." Tidecleanse
  golds "Exhaust". Tidal Resonance's base face ended in a trailing space
  before its upgrade-only "Draw 1 card."; the codegen now puts that
  separator inside the upgrade clause (`_face_from_parts`), which also
  removes the same trailing space from six other cards' faces (Come Back
  and Play, Amber's Explosive Puppet, Dahlia's Sacramental Shower, Heizou's
  Heartstopper, Yae's Sesshou Sakura, Crosscurrent; whitespace only).
- **Comments.** `Kokomi.cs` no longer describes Charge and the Pearl of
  Wisdom funnel; `KokomiCardPool.cs` no longer promises stage 5 or the
  shipped Burst; the generated `upgraded_grant` comment says "the granted
  card arrives upgraded" (it named Ka-pow! on Kokomi's Sea Glass Harvest and
  Shoal Call; Alice's Detonator's copy changes with it).

Not built: Tide Wall's "plus the damage the front enemy intends". Its op,
`block_front_intent`, does read the front enemy
(`KokomiOverhaulKit.IntendedDamage(FrontEnemy(...))`), but
`docs/current/text-conventions.md` rules that a Plan line never names "the
front enemy" (the Plan tip says a Plan hits the front enemy), and
`lint_text_conventions` refuses it. The face is unchanged; the main session
dropped the item, since the convention already covers it.

Kept after a telemetry check (99 seat fights since 2026-10-01): The
General's Banner and Watatsumi Resistance (a Companion card was played in 59
fights), At Water's Edge (a reaction happened in 41 solo fights).

## Varka r6 round, 2026-10-05

Cycle of Seasons 4 [6] -> 7 [10], to a random enemy. Two seat rounds named it NEVER AGAIN ("4 damage per element change was the weakest card"). 7 is a Strike per element change and stays single-target per the AoE trim. Prediction: no NEVER AGAIN next round. Record: `review/records/varka-r6-round-2026-10-05.md`.

## Kokomi review round, 2026-10-05

Two changes after the seat round (`review/records/kokomi-review-round-2026-10-05.md`).

- Tide Wall's Plan now says "plus the damage the enemy intends next turn." Wording only, no op change: the seat read the intent on screen and took the Plan as this turn's, but it is carried out next turn.
- Sea Glass Harvest's now-line Block 6 [7] -> 8 [11]. Two seats named it NEVER AGAIN: 6 Block with nothing to transform. 8 [11] is Coral Bulwark's Common rate. The Plan is unchanged. Prediction: no NEVER AGAIN next round.

## Klee scaling pass, 2026-10-05

Staging branch `klee-next` only, under the freeze (`review/active/klee-balance-measurement-2026-10-05.md` sec.6). Paper: `review/active/klee-scaling-pass-2026-10-05.md` sec.4, ruled at its defaults.

- `proto_ko_secret_base`, v3 (replaces sec.4 A's "Your Bombs are placed 3 [4] bigger", whose placement bonus and card-face fold are removed, so faces print their own numbers again): "At the start of your turn, place a Bomb 4 [6] on a random enemy." 1-cost Uncommon Power; the upgrade raises 4 to 6. Copies add like Noxious Fumes (two copies place one Bomb 8, 12 upgraded). Placed after the start-of-turn growth, so it shows 4 when she acts, through the expansion's start-of-turn sequencer (after the echo, before Dodoco's Mine) and the ordinary placement path Pop! uses; a random living enemy, none means nothing.
- `proto_ko_boom_badge`: Retain, and "Does not stack." -- x2 whatever the stack (sec.4 C).
- `proto_ko_witchs_homework_next` (new, grant-only, `C.STAGING_GRANT_IDS`): "Place a Bomb 6. When it goes off, this card's Bomb is 2 [3] larger for the rest of the run." Exhaust (sec.4 B). Titled "Witch's Homework II" because titles are unique (`lint_prototype_titles`); the pool's Witch's Homework is unchanged.

## Klee tempo paper, 2026-10-07

Staging branch `klee-next`. Paper `review/active/klee-tempo-paper-2026-10-07.md` sec.3, ruled 2026-10-07. [USER]: "I personally found Blast Shield and Kitchen Alchemy quite useful in my runs, so I'm not sure I buy that they should go. Otherwise agreed." Klee is slow (act-3 turn-one damage 9 to the base five's 62) and her Block pays for it; each engine gets its missing damage. Five out, five in; the pool stays **78 (25 / 32 / 21)**. Built in both engines.

- **Out:** `proto_ko_it_wasnt_me` (C), `proto_ko_sorry_jean` (C), `proto_ko_grounded` (U Power), `proto_ko_sit_tight` (U), `proto_ko_patience_klee` (U, "Experiment in Progress"). Painted art `KNOWN_STALE`; card pins removed or moved onto Favonius Escort (the same `remove_bomb_for_block` verb). Their powers stay registered (BACKLOG).
- **In, after the status package in `C.KLEE_TEMPO_IDS` and `Slice()`:**
  - `proto_ko_simmer`, Simmer (Common Attack, 1): "Deal 4 [6] Pyro damage, plus half your largest Bomb's size. It does not go off. Add a Dazed into your Discard Pile." Cook's Common hit that leaves the Bomb cooking.
  - `proto_ko_taste_test`, Taste Test (Uncommon Attack, 2): "Deal Pyro damage equal to all your Bombs on the enemy. They do not go off. Add 2 [1] Confiscated into your Discard Pile." Set against Red Knight (2 Energy, 34, two Confiscated).
  - `proto_ko_tinkering`, Tinkering (Uncommon Skill, 0): "Gain 2 [3] Sparks. Add a Confiscated into your Discard Pile." The kit's second row allowed to mint Sparks without an explosion (rule-4 pins name it beside Flash Point).
  - `proto_ko_dodoco_tag`, Dodoco Tag (Uncommon Attack, 1): "Deal 7 [10] Pyro damage. Gain 5 [7] Block. Add a Dazed into your Discard Pile."
  - `proto_ko_explosive_spark`, Explosive Spark (Common Attack, 0, 1 Spark): "Deal 12 [16] Pyro damage." (12 [16] ruled mid-build over the paper's 7 [10].)

**Readings:**

1. *The read.* New op `damage_from_bombs` (`read: largest_half | target_total`, `amount` the flat part). C# `ProtoBombPower.DealFromBombs` / `BombReadDamage` (`Powers/Prototype/ProtoBombPowerTempo.cs`), sim `effects._op_damage_from_bombs`. `largest_half` is the largest single charge of hers on the living board (`LargestSizeFor`, Sparks 'n' Splash's read), halved and rounded down, the hit landing on the aimed enemy; `target_total` is every charge of hers on the aimed enemy, Mines included (`TotalPlacedBy`). Nothing goes off: no Spark, no Mine answer, no explosion counter.
2. *The hit is the card's.* One `DamageCmd.Attack` from the card (`DealCardDamage`), so Pyro, the reaction, Strength, Weak and Vulnerable land as on any other Attack of hers; a read of zero deals nothing. Simmer's flat 4 owns the `Damage` var (`bomb_read_damage_var_effect`; sim `damage` delta bumps it third, after `damage` and a Set off's own hit).
3. *Two upgrade keys newly printable on an authored face:* `spark` (Tinkering's "Gain {Sparks}") and `cards` on a named token (Taste Test's "Add {Stash} Confiscated"; the token loop reads the Stash var).
4. *Taste Test's face says "Pyro".* The paper's text is "Deal damage equal to all your Bombs on the enemy."; `lint_element_text` requires a hit that applies an element to name it (the 2026-10-02 co-op ruling), so the face reads "Deal [gold]Pyro[/gold] damage equal to ...".


## Klee design review, 2026-10-08

Staging branch `klee-next`. Paper `review/active/klee-design-review-2026-10-08.md`, ruled 2026-10-08, all five picks at the defaults. [USER]: "Nope, this all looks good. I'm now in agreement with all picks." The starter is not the root; rule 1 made waiting free and rule 4 left the Spark cards dead on turn one. No starter change. Built in both engines.

- **Rule 1 (sec.4.6):** Bomb growth 4 to **2** a turn. `C.KLEE_OVERHAUL_BOMB_GROWTH`, `KleeOverhaulLaw.BombGrowth`, `understudy/blindplay_shape.BOMB_GROWTH`; the Bomb tip interpolates the constant. Alice's Recipe still doubles it (4).
- **Rule 4 (sec.4.6):** opening Sparks 1 to **3**. `C.KLEE_OVERHAUL_OPENING_SPARK`, `KleeOverhaulLaw.OpeningSpark`, `blindplay_shape.OPENING_SPARK`; the Spark tip interpolates it. Pounding Surprise's text does not move; Explosive Frags' own 4 stacks on top (7).
- **Every drafted placer +2, base and upgraded (sec.4.2):** the upgrade deltas are unchanged, so the upgraded face moves by 2 as well. Mine Toss 7 to 9; Boom-Boom Strike's Bomb 4 to 6; Lizard-Tail Gunpowder 4 to 6; Booby Trap 5 to 7; Coven Errand 8 / 12 to 10 / 14; Little Hexenzirkel 3 to 5; Bombs Away! 4 to 6; Windtrace's Mine 3 to 5; Jumpy Dumpty Mk.III's per-hit Bomb 2 to 4; Mine, All Mine!'s Mine 4 to 6; Party Poppers 3 to 5; Klee's Secret Base 4 to 6; Windblume Fireworks' Bomb 6 to 8; Dodoco 3 to 5; Finders Keepers 4 to 6. Not moved: Jumpy Dumpty (starter, pick 4 (a)); the jumps and copies (Aftershock, All of My Treasures!); Return to Sender (its Bomb is the Block absorbed, no printed size); Pop! (off-pool) and the two new rows (their numbers are final); the co-op tier's Shrapnel and the staging-only Witch's Homework II, outside the 78.
- **Out (sec.4.4):** `proto_ko_playdate` (C), row deleted with a CUT note, art `KNOWN_STALE`, `PlaydatePower` stays registered. `proto_ko_pop` (C) leaves `Slice()` and `C.KLEE_OVERHAUL_POOL_IDS` but keeps its row and class: Klee Can Explain! transforms statuses into it. New register `C.KLEE_OFF_POOL_ROW_IDS` (a row created at play and offered nowhere), skipped by `lint_arm_pool_parity` and `card_distinctness_report` as a staging row is.
- **In (sec.4.5), after the tempo paper's in `C.KLEE_DESIGN_REVIEW_IDS` and `Slice()`:**
  - `proto_ko_fire_fire`, Fire! Fire! (Common Attack, 1, Pyro): "Place a Bomb 7 [10] on the enemy. Set off the enemy." Her normal attack: a Spark and Bomb-typed damage every turn without cooking.
  - `proto_ko_blasting_spree`, Blasting Spree (Common Skill, 1): "Place a Bomb 4 [6] on ALL enemies. Add a Dazed into your Discard Pile." Spray's fuel and the Spray half of the status bridge.
  - Both are existing ops (`plant_bomb`, `set_off`, `add_card`). Art `KNOWN_MISSING`. The pool stays **78 (25 / 32 / 21)**.

## Varka payoff fix, 2026-10-08

Paper: `review/active/varka-payoff-fix-2026-10-08.md` (project review
2026-10-08, pick 10). Seven rows; the record is
`review/records/varka-offers-round-2026-10-08.md`.

- Ember Cleave adds "Gain 1 Pyro Oath" after its Exhaust (`gain_pyro_oath`,
  amount 1), gained even with no card to Exhaust. Pyro becomes current from
  the hit, as before.
- Stoke the Flames costs 0, was 1.
- Pyre Oath adds "Exhaust a card" on play, after the Power lands, so that
  Exhaust pays 1 Oath. The paper prints "Exhaust up to 2 cards"; the chosen
  `exhaust_from` selector (`CardSelectCmd.FromHand` with
  `CardSelectorPrefs(prompt, n)`) takes an exact count and has no "up to",
  so by the paper's own reading it is built as exactly 1.
- Wildfire Oath and Absolute Zero cost 1, were 2.
- Deep Freeze adds 1 Vulnerable before the doubling (`apply_power
  vulnerable 1`), so a clean enemy ends on 2. It is an application, so
  Absolute Zero pays on it.
- Glacial Edict: every 3 [2] Cryo Oath, was 4 [3].

## Furina playtest trim, 2026-10-09

Record: `review/records/coop-human-playtest-2026-10-09.md`, picks 1 and 2.
[USER]: "Good on the defaults for now - we can start with these trims and
readjust after the card pool expands."

- Salon Solitaire (starting relic, not a sheet row): Repay 2 -> 1; its Orobas
  upgrade The Curtain Never Falls Repay 3 -> 2 (`FurinaStageLaw.SingerRepay`
  / `SingerRepayUpgraded`, `tier0/engine/furina_stage.py`,
  `tier0/engine/furina_tide.py`; the sim slice's research variants keep the
  2 they measured).
- Interval Bell (`proto_fs_interval_bell`): Common -> Uncommon.
- Gentilhomme Usher (`proto_fs_leading_lady`): 7 / 13 -> 6 / 11, upgraded
  9 / 17 -> 8 / 14 (`conditional_then_block` +2 -> +1; it adds on top of
  `conditional_block`).
- Tidal Flourish (`proto_fs_tidal_flourish`): Common -> Uncommon, and its
  plain mode applies Hydro: "Deal 5 Hydro damage to ALL enemies. Spend 6:
  deal 12 instead.", Surintendante Chevalmarin's wording.

## Furina: the pool to 75, 2026-10-09

Paper: `review/active/furina-pool-growth-2026-10-09.md` (on branch
`furina-pool-78-paper-2026-10-09`), ruled 2026-10-09 at all defaults after a
Fable design review ended with "no further critiques" ([USER]: "If they have
no further critiques, then I'm good to approve it."). Built on the 2026-10-09
playtest trims. Every row is the paper's sec.5 text as it stands after its
Review section (All In costs 0; Hymn of Renewal counts HP actually repaid,
which is on its power's hover and the Repay tip, not its face).

**The guest rule (sec.3)** is `FurinaStage` / `StageDirector` and the sim's
`furina_tide`: a Guest Star exhausts (`exhaust: true` on all eleven rows) and
hands itself to the summon; the seat holds the card and sends it from the
exhaust pile to the discard pile when its guest leaves (a fourth summon, or
Final Bow). A summon has no effect: the old "acts at once" path is gone, and
a duplicate copy moves its guest to the newest seat with no act. At the end of
her turn the guests act oldest first, then each Showstopper copy Spends 5 and
they act again, then Salon Solitaire Repays. A line that fires files a `line`
beat on the stage log and flashes the guest's badge (`StagePerformerBeat.Line`),
distinct from an act's lunge. A guest's upgrade (`guest_upgraded: true`) raises
its line or act per the paper's table; its face prints "Summon Charlotte+."
and the numbers are on its tip and badge (an upgraded guest wears its own
badge class). Charlotte stays Common.

**The 41 rows** (10 Common, 18 Uncommon, 13 Rare; the pool is 20 / 35 / 20,
with three slots held). The guest verbs the grammar cannot spell are one op,
`{op: furina, kind: ...}` (`act_oldest`, `act_all`, `final_bow`,
`tutor_guest`, `repay_next`; C# `FurinaCards`, sim `furina_stage.kind`).
Powers are `FurinaPool75Powers.cs`. New sheet machinery: `stage_drain` and
`stage_spend` fixed prices an upgrade moves (gate and payment read one
`IsUpgraded` swap), the count tokens `stage_drains`, `stage_half_drained`,
`stage_repays_turn` and `stage_repaid`, the predicates `stage_near_line` and
`stage_none_drained`, a `stage_repay` legal in a branch (Riptide Lunge), and
Star Turn's card-level `cost_reduction_per_fanfare: 6`. Encore! prints
"oldest guest", which has its own tip (`ArmKeywordTips.ForOldestGuest`).

**Readings where the paper is silent** (each is in the PR body too):
- An evicted guest leaves without acting ("no effect on summon"); only Final
  Bow's guest acts as it goes.
- A duplicate's card joins its guest's seat and returns with it; an upgraded
  duplicate upgrades the guest.
- Showstopper Spends only with a guest on stage and the price in the bank;
  each copy is one Spend and one round. It is automatic.
- Navia's discount is the first Spend of the turn (a Spend before she
  arrived uses it up); a spend-all keeps the discount; her act reads the
  Fanfare actually paid this turn.
- Escoffier's line answers every act, his own included.
- Neuvillette's bonus covers every Hydro hit she deals (cards, guests' acts,
  his own act). It is a passive line like Lyney's, so it has no cue.
- Casting Call and Final Bow let the player pick off a grid when there is
  more than one choice; the sim takes the first fresh Guest Star and the
  guest with the biggest act.
- Commanding Gaze's "[3 and 2]" is the Spend mode: 3 Vulnerable and 2 Weak.
- Undercurrent counts its own Drain; Balance the Books reads the drained HP
  before its own Repay, rounded down; Grand Absolution deals what it repaid.
- Turn start: Regina, Fountain of Lucine, Gentle Current, Pneuma Tides, then
  Prima Donna reads the Fanfare.
- Grand Entrance Repays after the summon, on every Guest Star played.
- "Within 5 HP of your Drain line" is HP minus the line at most 5.

**Art.** Eleven rows take paintings already on disk under the same id from
the v2 pool (`KNOWN_STALE` entries removed); thirty are `KNOWN_MISSING`. The
four new guests have no body scene (the Osty fallback) and no badge icon.

**The sim slice** (`furina_tide.CARDS`) mirrors all 75 for the probes, and
now carries the playtest trims (Usher 6 / 11, Tidal Flourish and Interval
Bell Uncommon) so its draft pool matches the sheet.

**Loop probe (sec.6).** As first built, the full sweep found 81 productive
cycles over 16 thin-deck card sets, ten with HP flat (the smallest: Overdraft
and Pneuma Refrain). The main session ruled that Overdraft ("Drain 4. Gain 1
Energy next turn." [Drain 3]) and Sold Out ("Spend 6. Draw 2 cards. Gain 1
Energy next turn." [Spend 4]) give their Energy next turn, Interval Bell's
2026-10-04 fix and its `stage_energy_next` op; the paper's rows are edited in
place. The sweep is then clean, and none of the four named combinations is a
productive loop.


## Furina: the Drain line rule, the Repay floor and the round's numbers, 2026-10-09

Record: `review/records/furina-pool75-round-2026-10-09.md`, "Picks (ruled
2026-10-09)", picks 1 to 3. [USER]: "Yes - let's test it with a seat".

**The Drain line rule (pick 1).** `FurinaStageLaw.LineOf` is 3/4 of her
entry HP rounded up, as the half line was (59 from 78; `LineNumerator` /
`LineDenominator`, sim `LINE_NUMERATOR` / `LINE_DENOMINATOR` / `LINE_SHARE`).
A Drain is never refused for the line; the one refusal left is a Drain to 0
HP (`DrainFloor` = 1, which replaces `FiveCenturyLine`). The ledger keeps
drained HP in two parts (`DrainedAbove`, `DrainedPast`; sim `drained_above`,
`drained_past`, with `drained` their sum). The curtain call returns only the
above-line part; A Five-Century Act ("HP you Drain past your line also
returns when combat ends.", same cost and rarity) returns both and no longer
moves the line. A Repay returns the past-line part first. Lyney's line is 10
lower and his act may Drain past it. "Within 5 HP of your Drain line" already
counted HP at or below the line (HP minus the line at most 5). The Drain tip,
the Drained counter, the card faces' in-combat line ("(Past your Drain line
of 59 HP)", "(Not enough HP)") and the seat page say the 3/4 rule and that
HP drained past the line is lost unless repaid.

**The Repay floor (pick 2).** "Repay N. Gain X for any HP it could not
Repay." -- `StageDirector.RepayFloor` (sim `repay_floor`): the Repay
resolves, then N minus the HP returned is paid. Block: Hymn of Many Waters
(`stage_repay` with `floor: block`), Gentle Current's next-turn Repay,
Fountain of Lucine each turn, Grand Entrance, Charlotte's and Sigewinne's
acts. Vigor (the base game's `VigorPower`; the sim's `next_attack_up`):
Pneuma Tides (Soothing Waters keeps none: see the loop probe). Damage: Surging Waters,
Hydro Lance and Cleansing Torrent now Repay first and deal `amount_formula
{base, per: 1, count: stage_repay_left}` (`FurinaStage.RepayLeftOrRoom`, the
ledger's `RepayLeftThisPlay`); their damage upgrades moved to `formula_base`.
Endless Waltz is cut: its row, card, power and sim twin are deleted (the
pool is 74, 19 / 35 / 20). Vigor joins the base keywords with a tip.

**The card numbers (pick 3).** Standing Ovation Common -> Uncommon; Bravura's
upgrade is `formula_base: +4` (10 plus 2 per point; was per-point +1);
Mademoiselle Crabaletta 20 [26]; Soloist's Solicitation 6 [9]; Commanding
Gaze's plain mode 2 Vulnerable; Freminet's act also gives 6 Block [9]
(`FreminetActBlock`); Guest Star: Neuvillette costs 1 and his act deals the
HP she lost since her last turn ended, Drained or taken
(`HpLostSinceLastTurn`, closed at the end of her turn after the acts).

**Readings where the ruling is silent:**
- "Gain X" pays 1 Block or 1 Vigor per HP not returned; the damage cards
  print "Deal 6 damage, plus 1 for any HP it could not Repay."
- Neuvillette's "this turn" is read as since her last turn ended, so the
  enemies' hits count ("from Drain or from enemies"), the window Grass Ring
  of Sanctification already uses; his face says "since your last turn".
- A Drain's split uses the line as it stands when it is paid (Lyney on stage
  or not). A heal from elsewhere clamps the past-line part first.
- A Five-Century Act no longer moves the line at all.
- Pool counts: Endless Waltz leaves an Uncommon and Standing Ovation joins
  them, so the Uncommon count is unchanged (35) and Commons drop to 19.

**Loop probe.** As first built, the full sweep found one productive cycle
the floor made: two Soothing Waters (0 cost, Repay 2, draw 1) with nothing
drained gained 2 Vigor a play without end. The main session ruled that
Soothing Waters keeps no leftover payout ("Repay 2. Draw 1 card." [Repay
3]): a 0-cost draw-1 card paying out on an empty Repay looped forever, and
the draw already carries it, as with Pneuma Refrain. The sweep then finds no
productive cycle, and none of the four named combinations is productive in
one turn. Over six whole turns `energy_cycle` (Overdraft, Soothing Waters,
Sold Out, Crescendo) still reaches the 60-play cap in one turn on Soothing
Waters' inert cycle, and Overdraft drains her from 78 to 4 HP since a Drain
may now go past the line; it grows nothing, and it is reported here, not
pinned.


## Furina: the Drain line is entry HP minus a quarter of Max HP, 2026-10-09

[USER]: "Yeah, let's build it that way. That also rewards max HP stacking,
which seems fair on a character designed for it, and punishes some event
choices which cost max HP that are usually auto-picks."

`FurinaStageLaw.LineOf(entryHp, maxHp)` is the HP she entered the combat
with minus her Max HP divided by `LineMaxHpDivisor` (4), rounded down, never
below 0: 50/80 gives 30 (20 HP of room), 80/80 gives 60, 85 Max HP gives 21
of room, 78/78 gives 59 as before. The ledger snapshots `EntryMaxHp` beside
`EntryHp` when the combat opens (`FurinaStageLedger.Open(entryHp,
entryMaxHp)`, and at the ledger's creation), so a Max HP change mid-fight
does not move the line; the wire sends `entry_max_hp`. Lyney still lowers it
by 10, never below 1. `LineNumerator` / `LineDenominator` are gone; the
parity lint pins `LineMaxHpDivisor` to sim `LINE_MAX_HP_DIVISOR`.

Sim: the default variant (`curtain_call`) and Furina's arm
(`furina_stage.reset_for_combat`) carry the marker `SHIPPED_LINE`, and
`furina_tide.half_line` computes `shipped_line(entry_hp, entry_max_hp)` for
it; `Ftd.entry_max_hp` is the snapshot. The research variants keep the float
shares they measured (`LINE_SHARE` is gone with the 3/4 line).

Player text: `LineWhy` is "the HP you started this fight with, minus 1/4 of
your Max HP" (Lyney: ", 10 lower with Lyney on stage"); the in-combat Drain
tip reads "Your Drain line is 30: the HP you started this fight with, minus
1/4 of your Max HP."; the Drain keyword tip and the seat page's Drain row
end "Your line is the HP you started this fight with, minus 1/4 of your Max
HP." The fraction is written "1/4", as "3/4" was, not the glyph.

## Furina: the block gap, 2026-10-09

`review/records/furina-drain-line-round-2026-10-09.md`, pick 2. A census
counted 7 Block cards in her 74 (9.5%) against 11 to 16 in 85 (13 to 19%) for
each base character, no Rare Block card and no Power with flat repeating
Block. [USER]: "Yeah, agreed - let's plug the block gap now." Four rows, built
as the main session wrote them; pool 78, 20 / 37 / 21.

- **Velvet Curtain** (1, Common): "Gain 7 Block. Gain 2 Fanfare." [10, 3]
  The Fanfare is a new `furina` kind, `gain_fanfare` (`FurinaCards.GainFanfare`
  into `FurinaStage.Gain`, the ledger's gain that Universal Revelry's gain
  also takes), so it counts as gained Fanfare; sim `furina_tide.gain`.
- **Private Box** (1, Uncommon): "Gain 5 Block, plus 3 for each guest on
  stage." [7, plus 4] A `block` `amount_formula` on the new count
  `stage_guests` (`FurinaStage.Of(...).Count`), with the live "(Gains N
  Block)" preview of the game's `CalculatedBlockVar` (card Block, so Dexterity
  and Frail apply).
- **The Masquerade** (1, Uncommon, Power): "Whenever you Drain, gain that much
  Block." [cost 0] `TheMasqueradePower`, read by `StageDirector.Drain` after
  the loop readers: the HP actually drained, past the line included, per
  copy, as a Power's unpowered Block (Freminet's line and Feel No Pain's
  shape). A guest act's Drain arrives already stopped at the line, so it pays
  less. Its icon is on `ICON_DEBT` until the art pass.
- **The Show Must Go On** (2, Rare): "Gain Block equal to your Fanfare."
  [cost 1] A `block` `amount_formula` on the new count `stage_fanfare`
  (`FurinaStage.FanfareOf`); it reads the bank and spends none of it.

No art: the four ids are on `tools/art_coverage.py`'s `KNOWN_MISSING`. Sim
twins: the sheet ops through `furina_stage` (`gain_fanfare`, the two counts,
`fs_the_masquerade` as `masquerade`), and the research slice's rows
`ftd_velvet_curtain`, `ftd_private_box`, `ftd_masquerade` and
`ftd_show_must_go_on`, which the tide pilot drafts and values.

## Furina: Spend up to X, and two guests Spend half the bank, 2026-10-10

`review/active/furina-spend-paper-2026-10-10.md`, picks 1 and 2, built at the
paper's defaults; [USER]'s ruling is pending (picks open on #1014). His
direction, quoted in the paper: "we could have Spend act as 'spend up to X'
with partial effects, and then make the X larger".

The rule (`FurinaStageLedger.SpendUpTo`, `StageDirector.SpendUpTo`,
`FurinaStage.SpendUpTo`; sim `furina_tide.spend_up_to`): it counts X, or all
she holds if that is less, and never fails. It is a Spend only when at least
1 counts (Thunderous Applause, Chevreuse, Crescendo answer it); it is not a
spend-all, so Bis! and Standing Room Only ignore it. Navia's line makes the
first 2 [3] points of the turn's first Spend free: they count and are not
taken, so with Navia on stage and 0 Fanfare an up-to Spend counts 2.
Center of Attention's free Spend counts the full X and takes nothing, and,
like its free Spend N, is no Spend. The new op is `stage_spend_up_to`; the
card reads what it counted as `stage_spent`, and "for every 4" as the count
`stage_spent_fours` (`FurinaStage.SpentFours`, sim
`furina_stage.spent_fours`), a Crashing Waves hit count (`times_formula`) and
a Spirited Aria draw.

The four cards lose their chooser (the Spend is made on play):

- Tidal Flourish: "Deal 5 [8] Hydro damage to ALL enemies. Spend up to 10:
  deal 1 more for each."
- Spirited Aria: "Deal 8 [11] damage. Spend up to 8: deal 1 more for each.
  Draw 1 for every 4 spent."
- Crashing Waves: "Deal 4 [5] Hydro damage twice. Spend up to 12: hit once
  more for every 4."
- Hold the Stage: "Gain 6 [8] Block. Spend up to 12: gain 1 more for each."

The three formula faces keep the house "(Deals N damage)" / "(Gains N Block)"
preview line, which previews what the Spend would count now.

The guests (lines unchanged): Navia's act is "Spend half your Fanfare
(rounded down). Deal that much Geo damage to a random enemy."; Freminet's is
"Gain 3 [6] Block. Spend half your Fanfare (rounded down): gain that much
more Block.", replacing 5 [8] Cryo and 6 [9] Block. Each takes half of what
is left when it acts, oldest first, and again after Showstopper; the
half-Spend is a Spend when at least 1 is spent, and takes Navia's discount
when it is the turn's first Spend. `FreminetActDamage` and its upgrade are
gone; `FreminetActBlock` is 3 [6]; `GuestSpendDivisor` (2) and
`SpendUpToEvery` (4) are new, each pinned by the parity lint. Freminet's
forecast cue is Block now (`StageCueKind.Block`), and the forecast walks the
bank in seat order. The research slice's four rows became the `upto_*`
kinds, valued by the tide pilot.

Pick 2 ruled 2026-10-10 ([USER]: "I don't like artificial limits, so I'd
prefer to just fiddle with the ratio (make him only spend a quarter or a
fifth or something like that...)"): Freminet's act Spends a quarter, not
half: "Gain 3 [6] Block. Spend a quarter of your Fanfare (rounded down): gain
that much more Block." Navia stays at half. `GuestSpendDivisor` split into
`NaviaSpendDivisor` (2) and `FreminetSpendDivisor` (4), each pinned by the
parity lint (sim `NAVIA_SPEND_DIVISOR`, `FREMINET_SPEND_DIVISOR`);
`StageDirector.SpendHalf` became `SpendShare(divisor)` (sim `spend_share`),
and the forecast divides by the acting guest's own divisor.

## Varka payoff round, 2026-10-10

Record: `review/records/varka-payoff-round-2026-10-10.md`, "What changes
(Claude ships)". Four rows' text; no number moved.

- Stoke the Flames (`proto_vk_stoke_the_flames`): "Exhaust a card. Pyro
  becomes your current element. Gain 2 [3] Pyro Oath." The code switched
  after the gain, so Dawn Wind's March and Oath Unto Death never saw it as
  the current element's; `gain_pyro_oath` now switches first (C#
  `VarkaCards.GainPyroOath`, sim `varka_oath._combo_kind`). Under Unwavering
  Banner the Banner's 1 Oath now lands before the 2 Pyro.
- Ember Cleave (`proto_vk_ember_cleave`): the same op order, through the same
  kind. Its hit already makes Pyro current (the open Oath), so the change
  shows only where the hit did not switch. Numbers held.
- Wolfpack (`proto_vk_wolfpack`): "Whenever you play Four Winds' Ascension,
  shuffle a copy of it into your Draw Pile. The copy Exhausts." The copy
  goes to a random depth of the draw pile (`CardPilePosition.Random`; sim: a
  random index) and carries Exhaust (`AddKeyword`, the Kokomi Nips' shape).
  A copy played fires Wolfpack again, so one real card and one copy
  circulate. Upgrade stays Innate.
- Unwavering Banner (`proto_vk_unwavering_banner`): "gain 1 Oath of it" said
  the would-be element; the code pays the current element
  (`VarkaOath.BannerHolds`), as the Power's own face already said. The card
  now says "of your current element".
