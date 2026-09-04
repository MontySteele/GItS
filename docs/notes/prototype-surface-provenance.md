# prototype-surface.yaml - comment provenance

Long comment blocks that used to sit in `docs/prototype-surface.yaml`. They
moved here on 2026-09-01 so an agent reading the sheet loads rows,
not prose. Blocks are verbatim and in sheet order.

A heading names the row the block was attached to. `before <id>`
means a column-0 section note that sat above that row. `header` is
the file header. Blocks of three lines or fewer stayed in the sheet.

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

## before proto_pearl_barrage_turn

```
# =============================================================================
# KOKOMI SLICE 1 (R216) -- seven rows, three arms. Every one is a QUESTION put
# to the engine, not a card: they are deleted when the slice is accepted or
# rejected (the deletion rule above), and under R215 B no number measured on
# any of them is quotable anywhere.
#
# THE HYPOTHESIS THEY TEST, in R213 C/E3's words: subsidised Block dissolves
# the attack/defend decision. A card that hands you defence for free alongside
# the play you wanted to make anyway leaves no second line, because there was
# never a trade. Each pair below sets the shipped shape against a shape where
# the Block costs SOMETHING -- an outcome, or an energy.
#
# NAMES. Every display name here is provisional and mine (R179). They are
# deliberately ordinary card names rather than "(Priced)" or "(Variant)": the
# QA grader reads printed titles on a design-blind packet, and a title that
# names the experiment is a title that tells the grader what to answer. The
# alternatives considered, and why they lost, are in
# review/ruled/kokomi-slice-1-2026-08-27.md.
#
# `character:` ON A COMPANION ROW IS `klee`, AND THAT IS NOT A TYPO. It names
# the CODEGEN PROFILE and the off-pool list, and every shipped Companion of
# every nation is emitted through Klee's profile and pooled in
# KleeOffPoolCards -- that is where CompanionRoster.All is carried, and it is
# what gives a Companion its frame and its energy colour today. So a prototype
# Companion declared `klee` resolves through exactly the path its shipped twin
# resolves through, with no new machinery at all. `nation:` carries the pool
# identity the sim reads (the shipped sheets get it from their FILENAME, which
# this file does not have). The alternative -- a `character: companion` value
# with a nation field, taught to the loader and the generator -- is recorded
# in the packet and was rejected as machinery bought for one slice.
#
# OFF THE MUSTER POOL BY CONSTRUCTION, not by a filter: Muster and the reward
# slot both read `CompanionRoster.All`, which is generated from the three
# `*-companions.yaml` sheets and cannot see this file. The only door in is a
# grant by id against a dev build.
# =============================================================================
```

## before proto_pearl_barrage_turn

```
# ---------- ARM 1: Pearl Barrage's counting basis (R215 C) -------------------
# Shipped twin: `pearl_barrage` (docs/kokomi-cards.yaml). That card reads the
# cost of THE ONE CARD you chose to Exhaust. This one reads how many cards have
# been Exhausted THIS TURN -- the reading [USER] expected it to have. It still
# Exhausts one chosen card itself, and that card is in its own count, so the
# floor of the two shapes is the same number on a turn with one rotation in it.
# Base 5 and per 3 are the shipped numbers, UNMOVED: the counting basis is the
# question, and moving a number too would make the answer unattributable.
```

## before proto_shinobu_sanctifying_ring_either

```
# ---------- ARM 2: mutually exclusive Block (R216 C, option 1) ---------------
# Prune's shape: the card does the engine half OR the Block half, never both.
# Defence is paid for in OUTCOME. Same amounts, same cost, same element as the
# shipped twin -- only the conjunction moves.
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
# =============================================================================
# KLEE SLICE 1 (R213 E2) -- four rows, four arms. THE FOURTH ARM WAS HELD AND
# IS NOW ADMITTED: `proto_spark_mode_bombs` / "Bag of Tricks" was stopped by
# the independent seat's doctrine verdict, and holding it is the whole reason
# the seat was asked before anything was authored. Round 1's verdict is in
# review/qa/klee-slice-1-doctrine-review-codex-gpt-5.6-sol.md. The RE-ASK,
# taken after `EB-182` built per-mode playability, is in
# review/qa/bag-of-tricks-reask-doctrine-codex-gpt-5.6-sol.md: it RESOLVED D4
# and left ONE clause -- the top-level-cost rule -- in front of [USER]. R225
# amended that clause on 2026-08-30 (top level OR mode head) and the arm
# proceeds as `EB-224`. Its row is at the foot of this block. NOTHING about it
# was re-authored: the name, the id, the cost, the type, the rarity and both
# mode bodies are the packet's, unmoved, and the verdict changed no number.
#
# THE QUESTION. R213 E2 reopened "Sparks mean free Attack" as "likely upstream
# of Klee's Attack-spam identity". The engine says it more sharply than the
# playtest did: `combat.card_cost` zeroes ANY Attack at the threshold and
# `combat.play_card` debits the bank for it, both unconditionally, so the bank
# has one destination and it is chosen for the player. Against D2's six
# steerable verbs -- timing, targeting, placement, acquisition, conversion,
# forgoing -- the base rule feeds none.
#
# WHAT THESE ROWS DO NOT DO. The automatic rule is UNTOUCHED. Making it opt-in
# is a change to a character mechanic (klee-character-design.md section 3), it
# cannot be quarantined on a card surface, and the seat agreed it should not
# ride along with a card-level slice because it would destroy attribution. It
# also said plainly that the rule is the upstream problem and must eventually
# move; that is [USER]'s, and it is in the packet, not here.
#
# ONE PRICE ACROSS THE SLICE: every row charges THREE Sparks. An attribution
# call, not a balance one. Three is LIFTED, not picked -- it is the free
# Attack's own threshold, which is the thing under test, so each pair asks
# whether the bank is worth more as this card than as the rule. The three
# SHIPPED sinks (powder_charge, hold_the_line, smoke_and_sparks) charge 2, but
# 2 was authored against True Spark Knight's reduced threshold and would have
# confounded the question. The seat was asked about this directly and agreed:
# "Three is the right controlled price for this slice."
#
# EVERY NUMBER IS A SHIPPED NUMBER. 6 damage at cost 0 is
# `flame_on_the_wick`'s. `times: 2` is the sheet's standard multi-hit count
# (jumpy_dumpty, pocket_fireworks). Draw 3 is the twin's ceiling plus its
# floor. Block 5 is `clockwork_toy`'s. Burst 10 is `combustion_study`'s. THERE
# IS NO DERIVED NUMBER IN THIS SLICE AT ALL -- an earlier draft had one, and
# the seat's arithmetic correction removed the need for it.
#
# NO NEW OP, NO NEW PREDICATE, NO NEW PRICED VERB. `spend_spark` has been in
# both engines since EB-118 Phase 2 and has been printed by three shipped
# Uncommons since R211's W3 window; its playability gate (`combat.spark_cost`)
# and its no-partial-spend rule are shipped behaviour these rows only reuse.
# The proposal's arm 2 would have needed a `spark_at_least_` predicate; the
# seat's re-authoring of that arm removed the conditional and with it the
# predicate, so this branch adds NOTHING to either engine's vocabulary.
#
# NAMES are provisional and mine (R179), ordinary card names by construction:
# a blind grader reads printed titles, so no title here says spend, price,
# conversion or prototype.
#
# I DESIGNED THESE ROWS AND MAY NOT GRADE THEM (R213's first guard).
# =============================================================================
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
# =============================================================================
# KOKOMI -- THE KURAGE'S MEMORY v3 (a RULE arm, not a card row)
#
# DECLARED HERE AND CARRYING NO ROW, DELIBERATELY. Every row in this file is a
# CARD: `tools/gen_prototype_cards.py` requires an `id` starting `proto_`, a
# `character` in the codegen profiles, and an effects list it can emit as a
# C# class, and `tier0/content/loader.prototype_cards()` schema-checks it as a
# card. The Kurage's memory is ENGINE BEHAVIOUR -- two entry rules, a price, a
# turn-start fire, a pulse and a strip -- and it authors no card at all. A row
# for it would either be a card nobody designed or a new row KIND, taught to
# the loader, the generator, four lints and the surface tests. That is
# machinery bought for one arm, which is the same trade this file's header
# already refused for `character: companion`.
#
# So it is declared, not rowed, and the declaration is the audit trail:
#
#   arm:          the Kurage's memory, v3
#   character:    kokomi
#   spec:         review/ruled/kokomi-kurage-memory-2026-08-29.md sec.11
#                 (sec.11.1 is [USER]'s words and IS the spec)
#   sim:          tier0 behind C.KURAGE_MEMORY, default off
#   mod:          klee-mod/KleeCode/Powers/Prototype/KurageMemory.cs, compiled
#                 only under `dotnet build -p:PrototypeCards=true` -- the SAME
#                 switch that quarantines the card rows above, so a release
#                 build contains no type from it and every seam that calls it
#                 sits inside `#if PROTOTYPE_CARDS`
#   authored_by:  [claude, gpt] -- the field's closed set is
#                 {claude, gpt} (EB-190), so it records the MODEL FAMILIES and
#                 not the people: Claude implemented the rule and made it
#                 total, and [USER]'s advisor (GPT) wrote the rule statement
#                 [USER] forwarded as the design, which is text and therefore
#                 adds its family. [USER] SPECIFIED THE RULE and made four
#                 rulings on it; that is not a model family and has no cell in
#                 the field, so it is recorded here instead.
#                 THE FIELD ITSELF IS ON ROWS, and this arm has none -- it
#                 authors no card at all (see above) -- so `seat.py`'s refusal
#                 has nothing to key on for the RULE. What it does key on is
#                 the one row this chain does add,
#                 `proto_kurages_oath_memory`, which carries `[claude]`:
#                 [USER] ruled its numbers and its rule, Claude wrote it, and
#                 no seat contributed text, a number or a mode to it.
#   prints:       nothing. `play_front_memory` (provisional keyword "Stir",
#                 R179) has its op in the sim and its door in the mod so
#                 codegen can emit a card that prints it; no card does.
#   revert:       the flag. Delete Powers/Prototype/KurageMemory.cs and its
#                 `#if PROTOTYPE_CARDS` seams; the sim half is C.KURAGE_MEMORY.
#
# THE DELETION RULE AT THE TOP OF THIS FILE APPLIES TO THIS BLOCK TOO: when
# the arm is accepted or rejected, this block leaves with it.
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

## before proto_pop_spark

```
# =============================================================================
# KLEE SPARKS -- SPARKS AS AN ALTERNATIVE COST (R213 E2). Seven rows.
#
# AN EIGHTH ROW WAS AUTHORED AND IS NOT HERE, and the reason is the generator
# rather than a doctrine hold. PICK 5's re-authored `true_spark_knight` --
# "Spark Knight's Oath", Rare Power, 2 Energy, "Your Attacks that do not
# already cost [Spark] cost 3 [Spark] instead of their Energy cost" -- applies
# a power named `spark_attack_cost`, and `tools/gen_prototype_cards.py`
# refuses it by name: "NOT EXPRESSIBLE: apply_power power 'spark_attack_cost'
# (no PowerModel in the registry). A prototype row must be emittable today --
# rewrite it inside the existing grammar, or take the runtime work first."
# That refusal is correct and is left standing rather than worked around: the
# C# `PowerModel` is owed work, and a row emitting a reference to a class that
# does not exist would be a prototype that cannot be staged, which is the one
# thing this surface promises its rows are not.
#
# THE SIM HALF OF THAT POWER IS BUILT AND TESTED ANYWAY, behind the same flag
# (`combat.spark_power_price`, `C.SPARK_ATTACK_POWER_PRICE`,
# tier0/tests/test_spark_alt_cost.py), because tier0 is the arm this branch is
# for and the power is applied there by name. The row's exact text and the C#
# it is waiting on are in the packet's sec.10, not commented out here -- the
# deletion rule at the top of this file forbids a commented-out row.
#
# THESE ROWS DO NOT STAND ALONE, and that is the difference between this
# slice and every other block on this surface. They are the CARD half of a
# RULE change that lives in code behind `C.SPARK_ALT_COST_ENABLED` -- the
# threshold rule ("At 3 Sparks, your Attacks cost 0. Playing one consumes 3")
# is retired under that flag, and with it retired these rows are the only
# thing the bank can be spent on. With the flag OFF the rule is the shipped
# rule and these rows are eight cards nothing reaches. The packet is
# review/ruled/klee-sparks-2026-08-29.md; sec.9 is the independent seat's
# doctrine read and sec.1 is [USER]'s ruling that closed the direction.
#
# THE PICKS THESE ROWS ARE, in the seat's words (sec.9):
#   PICK 1  "Options 1 and 5 together follow"  -- a Basic that MAKES and a
#           Basic that SPENDS, exactly Regent's starter shape.
#   PICK 3  "2, Tinder Toss; 3, Bang Bang!; 4, Dodoco Blast; 5, Firework
#           Finale; best: 2. Option 1 ruled out -- R69 / R29d."
#   PICK 4  "1, The tight set."  -- five conversions, pool stays 79.
#   PICK 5  "1, STRICT conversion" + "(a), already-priced Attacks are
#           unaffected".
#
# CANDIDATE 1 IS RENAMED, AND ONLY ITS NAME MOVED. sec.4.2 proposed `Sizzle`;
# `Sizzle` is a shipped Klee Common Attack (docs/klee-cards.yaml:158) and the
# seat ruled the candidate out by name under R69 / R29d. The card's rarity,
# price, cost and body are the packet's, unchanged. The replacement is
# `Fwoosh!` -- provisional and mine (R179), in the onomatopoeia family the
# sheet already speaks (Snap!, Crackle, Pop!, Da-da-da!), checked against
# docs/reserved-card-names.txt and every sheet name before use. The name is
# [USER]'s to settle; the lint is the floor, not the ruling.
#
# EVERY DISPLAY NAME HERE IS PROVISIONAL (R179), including the two Basics'
# and the Power's: a proto row may not reuse its twin's printed name, so
# `Pop!`, `Kaboom!` and `True Spark Knight` each get a working title rather
# than a design decision.
#
# THE PRICES ARE THE PACKET'S, and the packet says plainly what they are:
# "shape, not ruled values", set against sec.2.4's measured income of ~1 Spark
# per turn, so 1 Spark = one turn of income, 2 = a deck cycle, 3 = Regent's
# median sink. NO NUMBER BELOW IS A BALANCE CLAIM (R215 B).
#
# EVERY DAMAGE FIGURE IS THE PACKET'S sec.4.2 TABLE VERBATIM, except the two
# Basics, whose bodies are their shipped twins' unmoved (`kaboom` 7 damage,
# `pop` one Bomb at 5) so that the starter substitution is a PRICE change and
# nothing else.
#
# WHICH POOL ROW EACH ONE REPLACES (PICK 4, the tight set -- one for one, so
# the pool stays at 79 and the generator:sink ratio moves at the same time).
# The replacement is recorded HERE and executed nowhere: this surface cannot
# reach a pool, and re-authoring the shipped sheet is what ACCEPTANCE means
# under the deletion rule at the top of this file.
#   Fwoosh!          <- sparkly_treasure  (Common, 0E, gain 1)
#   Bang Bang!       <- spark_collection  (Common, 1E, gain 2)
#   Tinder Toss      <- pocket_fireworks  (Common, 1E attack, no rider)
#   Dodoco Blast     <- sugar_rush        (Uncommon, 1E, +1 energy + gain 1)
#   Firework Finale  <- cant_catch_me     (Uncommon, 1E, block/gain/draw)
#
# I DESIGNED THESE ROWS AND MAY NOT GRADE THEM (R213's first guard). The seat
# gated the PICKS; it wrote no text and picked no number here, so every row
# is `authored_by: [claude]` -- including the renamed candidate, whose name
# the seat ruled OUT and did not replace.
# =============================================================================
```

## before proto_pop_spark

```
# ---------- PICK 1: the starter's Basic that MAKES ---------------------------
# Shipped twin: `pop` / "Pop!" (0, Skill, Basic, skill_tag -- one Bomb at 5).
# Cost, type, rarity, tag and the Bomb are unmoved; a Spark rider joins them,
# which is the packet's option 1 verbatim: "the natural home is `pop` (0
# energy, places a bomb), which becomes 'place a Bomb, gain 1 Spark'."
#
# WHY THE BUFFER GOES ON A CARD AND NOT ON THE RELIC (options 2 and 3): the
# relic's grant would be unsteerable income, and the seat cited D2's "the
# control must be reachable early and reliably -- starter kit, starting relic,
# base system, or the ordinary pool" for putting it on a card the player
# chooses to play. Pounding Surprise keeps its body unchanged and untouched.
```

## before proto_kaboom_sink

```
# ---------- PICK 1: the starter's Basic that SPENDS --------------------------
# Shipped twin: `kaboom` / "Kaboom!" (1, Attack, Basic -- 7 damage). The
# packet's option 5: "`kaboom` becomes 0 energy / Spend 1 Spark. This is
# `FallingStar`'s exact role." The damage figure does not move, so the whole
# delta is the CURRENCY: this Attack is bought with the bank instead of with
# the turn.
#
# ONE COPY, NOT FOUR, AND THE PACKET DOES NOT SAY WHICH. Klee's starter holds
# four `kaboom` and one `pop`; Regent's holds one generator and one sink out
# of ten. Substituting one copy of each is the reading that "matches their
# generation pattern" ([USER], sec.1(a)); substituting all four `kaboom` would
# make four of her ten opening cards unplayable on an empty bank. The seam at
# `loader._starter_ids` does one of each and says so; it goes back to [USER]
# in the packet's sec.10.
```

## before proto_spark_strike

```
# ---------- PICK 3 / PICK 4: the tight set of Spark-cost Attacks -------------
# All five are 0 Energy with a top-level `spend_spark`, which is the whole of
# "cost Sparks instead of Energy" in both engines: `combat.spark_cost` derives
# the price off the op, `card_playable` gates on it, and the payment is
# `effects.spend_sparks`, all-or-nothing. NOTHING WAS BUILT FOR THESE ROWS --
# the rail has shipped since EB-118 Phase 2 and has been printed by three
# Uncommon Skills since R211. The only new thing in the branch is the RULE
# these five now have to compete with the absence of.
#
# THE COST SITS AT TOP LEVEL OR AT A MODE HEAD (the rule authored at
# `powder_charge`, enforced by the seat in Klee slice 1, and AMENDED BY R225 on
# 2026-08-30 to admit a mode price): a spend at the card's top level is the
# CARD's price, a spend at the HEAD of a `choose_one` mode is that MODE's
# price, and a spend nested in a conditional or further down a mode body is
# invisible to the playability gate and is refused. No row here has a
# conditional.
```

## before proto_spark_strike

```
# Candidate 1, renamed. sec.4.2: "Spend 1 / 8 damage", mirroring Regent's
# `GuidingStar` (1 star, 12 damage). Its twin on the printed sheet is
# `sparkly_treasure`, whose entire body is "gain 1 Spark" -- the purest
# generator in the pool becoming the cheapest sink in it.
```

## before proto_spark_double_tap

```
# sec.4.2 candidate 3. Spend 2 / 5 damage to a random enemy, twice --
# mirroring `FallingStar`, Regent's own Basic sink, at his own price.
# `times: 2` is the sheet's standard multi-hit count (jumpy_dumpty,
# pocket_fireworks).
```

## before proto_spark_finisher

```
# sec.4.2 candidate 5. Spend 3, Exhaust / 18 damage single target, mirroring
# `Devastate` (4 stars, the big hit). Three Sparks is Regent's median sink and
# the retired threshold's own number, so this card is the direct question the
# slice asks: is a full bank worth more as this, or as the free Attack the
# rule used to hand out?
```

## before proto_true_spark_knight

```
# THE EIGHTH ROW, and it is the RULE the other seven are priced against
# (sec.5, PICK 5 wording (1) STRICT, sub-pick (a); the independent seat FOLLOWS
# on both). It replaces the shipped `true_spark_knight`'s body, which dies with
# the base rule -- a modifier to a threshold that does not exist. Same id shape,
# same rarity, same cost; only the rule moved.
#
# THE GENERATOR REFUSED THIS ROW ON THE SIM BRANCH BY NAME -- "apply_power power
# 'spark_attack_cost' (no PowerModel in the registry)" -- and the refusal was
# left standing rather than worked around, because a row emitting a reference to
# a class that does not exist is a prototype that cannot be staged. The class
# now exists (`klee-mod/KleeCode/Powers/Prototype/SparkAttackCostPower.cs`,
# compiled only under -p:PrototypeCards=true) and the row goes on.
#
# `amount: 1` is ONE STACK, not the price. The price is a constant of the rule
# (3, tier0 C.SPARK_ATTACK_POWER_PRICE); the registry template prints it as a
# literal for exactly that reason.
```

## before proto_powder_charge_spark

```
# =============================================================================
# KLEE SPARKS -- THE THREE HYBRID SPENDERS MIGRATE (R224 slate item 16;
# BACKLOG EB-218). Three rows, and no new design.
#
# WHAT THIS IS. The shipped Klee pool already holds three Spark spenders whose
# payoff is not a plain Attack -- `powder_charge`, `hold_the_line` and
# `smoke_and_sparks`, all ratified in W3 (R211), all three HYBRIDS: 1 Energy
# AND a top-level `spend_spark 2`. The packet's sec.14.2 preface records them
# and sec.14.3 option (5) -- TAKEN by R224 -- rules what they become in the
# priced-sink world: SPARK-ONLY. 0 Energy, the price paid wholly in Sparks,
# which is the economy the eight rows above are testing.
#
# NOTHING IS REPRICED. Each row keeps its shipped Spark number (2) and its
# shipped body byte for byte; the ONLY delta is that the 1 Energy is gone. A
# migration that also moved a number would confound the question sec.14.4
# asks, which is whether a bank with a NON-DAMAGE destination produces a hold.
#
# WHY THEY ARE PROTOTYPE ROWS AND NOT A SHEET EDIT. R224: "a dev-only
# substitution, not a shipped-pool edit". `loader._pool_substitutions`' Klee
# half under `C.SPARK_ALT_COST_ENABLED` (`C.SPARK_ALT_POOL_SUBS`) swaps each
# shipped row for its Spark-only twin at the SAME rarity -- three Uncommons in,
# three Uncommons out, so the offer odds do not move -- and with the flag OFF
# the pool is byte-identical to shipped. That is the one cost sec.14.3 records
# option (5) against itself, removed: no shipped face moves, and the act is as
# reversible as deleting three rows.
#
# ENERGY-GATING IS THE THING BEING REMOVED, and sec.14.3 says why: a hybrid
# cannot be reached by the bank alone, so a null read on a hybrid measures the
# Energy gate rather than the sink. Under this migration the bank alone
# reaches all three.
#
# NAMES ARE PROVISIONAL AND MINE (R179). A proto row may not reuse its twin's
# printed name, so each takes a working title in the sheet's own register.
# They are deliberately ordinary card names rather than "(Spark)" variants:
# the QA grader reads printed titles on a design-blind packet, and a title
# that names the experiment tells the grader what to answer. [USER] settles
# the names; `lint_unique_names` is the floor, not the ruling.
#
# I AUTHORED NOTHING BUT THE NAMES AND THE ENERGY DELETION, and both are
# R224's instruction, so every row is `authored_by: [claude]` and R213's first
# guard applies to it: I may not grade these rows.
# =============================================================================
```

## before proto_powder_charge_spark

```
# Shipped twin: `powder_charge` / "Powder Charge" (docs/klee-cards.yaml:248 --
# 1 Energy, Spend 2 Sparks, Uncommon Skill: detonate the target's Bombs for
# +4 each). Cost 1 -> 0; the Spark price, the detonation and the +4 are
# unmoved. Its shipped caveats ride along unchanged: dead on an unbombed
# target, and the bank is spent either way.
```

## before proto_hold_the_line_spark

```
# Shipped twin: `hold_the_line` / "Hold the Line" (docs/klee-cards.yaml:303 --
# 1 Energy, Spend 2 Sparks, Uncommon Skill: Block 5, and 6 more if the enemy
# intends to attack). Cost 1 -> 0; both Block halves and the conditional are
# unmoved. This is the row sec.14.2's candidate 3 (Behind the Barrel) turned
# out to be a duplicate of, which is the finding that produced option (5) --
# so migrating it is what makes minting that candidate unnecessary.
```

## before proto_smoke_and_sparks_spark

```
# Shipped twin: `smoke_and_sparks` / "Smoke and Sparks"
# (docs/klee-cards.yaml:320 -- 1 Energy, Spend 2 Sparks, Uncommon Skill: apply
# 3 Vulnerable). Cost 1 -> 0; the three stacks are unmoved. Note the shipped
# row's own exchange-rate comment prices the Sparks against `surprise_visit`
# (1 Energy, 2 Vulnerable) -- with the Energy gone that comparison is no
# longer the one the card makes, and re-reading it is acceptance work, not
# this row's.
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
# THE KLEE OVERHAUL, SLICE ONE (`review/active/klee-overhaul-slice-1-2026-09-01.md`,
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

THREE ILLUSTRATIONS ARE OWED. Each row wears the nearest Klee illustration
through `art_of:` -- Mine Toss for the Errand (a Bomb going wide), Chained
Reactions for the Circle (the power whose job it takes over one trigger away),
Alice's Recipe for the Introduction Magic (the same Alice) -- on the standing
terms: art is commissioned when a slice is ACCEPTED, and a prototype that
shipped new art would be paying for a card that may be deleted next week.
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
#                             plus incoming-damage reduction.
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
#   THE INCOMING-DAMAGE REDUCTION (Amber's "take 3 less") is
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
`review/active/kokomi-overhaul-slice-1-2026-09-01.md` **draft 6**, written
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

NEITHER ROW IS OWED ART. Both carry `art_of:` -- Tide Wall wears Coral
Bulwark's illustration and Shell Guard wears Salt Line's, the two nearest
defensive rows already fetched -- on the rule the stand-ins use one section up:
art is commissioned when a slice is ACCEPTED, and `tools/art_coverage.py` bills
the literals the codegen emits, so no new image is owed.

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
                        image: the codegen emits that id into
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
# illustration is REUSED rather than re-fetched: `art_of: prune_witch_hunt` is
# read at the codegen's one `CustomPortrait` line, because `art_lint` L11 is
# one producer per out-path and a second plan.tsv row for the same picture is
# exactly the collision that rule names.
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

ART: `art_of: proto_mi_gorou_juuga`, so the row borrows an illustration Gorou's
Universals already staged rather than minting an `art/plan.tsv` row for a
fourth picture of the same character.

THE DELETION RULE AT THE TOP OF THE SHEET BINDS THIS ROW: it leaves when the
arm is accepted or rejected.
```

## The companion stand-ins — the Hexerei family (2026-09-02)

```
FOUR MORE STAND-INS ON THE SEAM ABOVE, and every key on the row is that seam's
unchanged: `personal_pool: [klee]` (the LIST form, which `Card.from_dict`
normalises to the string), `replaces:` the Universal, `art_of:` the same id.
Nothing new was added to the contract for this slice.

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

## before proto_fr_salon_debut_named

```
# =========================================================================
# THE FURINA REFRAME, SLICE TWO -- the first cards the reframe's rules have
# (R220 A; the countersigned packet is review/ruled/furina-reframe-2026-08-29.md,
# its sec.6.2 row list, with sec.4.4 the Evoke, sec.4.6 the drain and sec.5 the
# starter delta). Slice one built the RULES -- the manual stage, the Companion
# trigger, the deploy that performs, the aimed Evoke and the meter that only
# performance mints -- in both engines and behind FURINA_REFRAME, and it left
# the surface with no row that speaks them. These five are that row list.
#
# THEY PRINT THREE WORDS THE SHIPPED KIT DOES NOT HAVE, and each carries its
# rule in a hover tip the codegen attaches off the printed word (`EB-272`):
# Deploy (a member joins AND performs), Evoke (it performs, leaves, counts its
# Fanfare bonus three times and prints five), Drain (the meter falls to nothing
# and the next clause is priced off what it took).
#
# FLAG-OFF AND UNRUN. Nothing here has been played, in the game or in a sim,
# and no number below is quotable (R215 B): the two mint figures and the Focus
# multiplier are slice one's prototype seeds, and the costs, the two Encore
# prices and the Rare's base are this slice's.
# =========================================================================
```

## proto_fr_salon_debut_named

Face: "Deploy Mademoiselle Crabaletta." The Deploy keyword tip carries the
perform clause: a deployed member performs at once; deployed onto a full stage,
the front member Evokes first. Reframe sec.5's starter delta: a NAMED member, so
which member is on the board is a decision and not a coin flip.

The shipped `salon_debut` it is a delta OF deploys `member: random`, which is
what makes the two a real A/B rather than a rename, and the row borrows that
card's illustration under R179 (`art_of`, cosmetic, lint-proved).

## proto_fr_curtain_call

Face: "Evoke the front Salon member." Prints its Encore price. The Evoke tip:
the member leaves the stage, its performance applies the Fanfare bonus three
times, and it mints 5 Fanfare. sec.6.2 row 2, `F16` (1)'s cheap Evoke.

The price is PRINTED as a sentence rather than left to the cost badge, which is
this sheet's shipped convention -- every priced Furina row on
`docs/furina-cards.yaml` opens "Spend N [gold]Encore[/gold]." -- and it is
shipped machinery on both engines: the playability gate and the spend run
before the op resolves, which is why `F7` (1) needed no port.

THE SENTENCE IS THE CODEGEN'S AND NOT THE ROW'S, which is what the designer's
`upgrade: {encore_cost: -1}` forced. The row used to write "Spend 2
[gold]Encore[/gold]." into its own `description:`, and a literal cannot move:
the delta emitted a real `UpgradeCostBy(-1)`, the gate and the badge charged
the moved number, and the face went on printing the old one -- so the emitter's
own visibility gate refused the row by name. `meter_price_clauses` is now the
ONE builder both face paths call, the base card prints "Spend 2 Encore" and the
`+` card "Spend 1 Encore", and a row's `description:` states what the card DOES
and never what it costs.

## proto_fr_exit_stage_left

Face: "Evoke Surintendante Chevalmarin." The aimed Evoke (`F5` (2)); her bow is
the alternative effect (the all-enemy aura and the Encore refund). If she is
not on stage the slice-1 fallback rule applies and the face must say what
happens then -- print exactly what the engine does. sec.6.2 row 3.

WHAT THE ENGINE DOES, printed: an aimed Evoke whose member is absent Evokes the
FRONT and reports it (`furina_reframe.EVOKE_TARGET_ABSENT`,
`FurinaReframeLedger.NoteEvokeTargetAbsent`) -- an aimed card that cannot find
its member is an unaimed Evoke, never a wasted one. So the face reads "or the
front member if she is not on stage" and the row's pin compares that sentence
with the rule rather than with a second copy of itself.

The aim is a `member:` ARGUMENT on the shipped `salon_bow` verb and not a new
op, which is the slot-6 ruling's own shape on both sides: registering a
`salon_evoke` would have grown the priced-op set, and that is a
`DRAFTER_VERSION` bump bought for a synonym.

ITS UPGRADE TAKES THE PRICE TO NOTHING, which is the one shape a printed price
had no wording for. "Spend 0 [gold]Encore[/gold]." is not a smaller price, it
is a line claiming a cost the card does not have -- and the rendered path's own
first clause already skips a row priced at 0. So the `+` card drops the whole
sentence, separator included, and the base card is unchanged.

## proto_fr_let_the_people_rejoice

Face: "Drain your Fanfare. Deal 5 damage to ALL enemies, plus 1 per Fanfare
drained." The Rare drain (sec.4.6, `F11` (1) as a proto twin: no `kit_card`, no
`requires` gate, a real cost). Playable at any Fanfare value; it reads the HELD
meter, never a threshold.

Neither gate travels with it, and each for its own reason: `kit_card` makes a
row inexpressible by name in the emitter ("hand-write it against the KitBurst
machinery"), and a `requires: burst_energy_full` would put back the threshold
the reframe took out. The shipped row keeps both and costs 0; this one costs 2.

## proto_fr_intermission

Face: "Drain your Fanfare. Gain Block equal to the Fanfare drained." `F12` (1):
the survival drain beside the damage one, so draining is a plan and not a single
card.

It is the first `amount_formula` on a BLOCK op in either engine, which is the
sentence four damage-side riders in `tools/gen_klee_cards.py` have carried for a
sprint ("a block-side reader needs `block_calc_rider`'s CalculationBase plumbing
and has no card yet"). The rail was already there; what this row added is a
predicate reading the other key.

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

- **Tide Chart** (Common, 0): draw per Plan the Kurage holds, the draw that
  reads the memory; blank with nothing written, which is the price.
- **Ripple** (Common, 0): a cheap Plan whose now-line is worth playing (2
  Block for 0) and whose Plan pays tempo (1 Energy and 4 Block).

TWO OF THE DRAFTED FOUR ARE WITHDRAWN on the R253 charter audit and are not
on the surface: Held Tide (Uncommon, Retain -- Sango Isshin's condition at
Common scale) on the owner's "not all agents always win" clause, because
Retain guarantees the payoff line; and Tidal Rhythm (Uncommon Power, an
Energy back once a turn when the Kurage carries out) as free repeatable
Energy. Both were ruled REQUIRES_MODIFICATION; the shelf ships as two.

Numbers are Prototype numbers, D by the ladder; the seats read them on
Kokomi round 10 before [USER] does.

## before proto_fr_florid_cadenza

The shipped Fanfare riders under the Furina arm, round 2 pick 1 taken at
its default (2026-09-04, disclosed and unanswered before the build; the
packet is `review/ruled/furina-reframe-round-2-2026-09-04.md`). The arm
mints Fanfare by performance only, 2 per trigger and 5 per Evoke, and in
three rounds Fanfare ranged 0 to 15 while the shipped riders asked 12, 15
and 20. These four rows are arm-only copies at the arm's scale (12 to 6, 15
to 8, 20 to 10), swapped in for the shipped ids at the same rarity by the
pool seam (`loader._pool_substitutions`, the Kurage's Oath shape), so
nothing on the shipped sheet moves and a run with the arm off is offered
the shipped card. The `(reframe)` suffix keeps the names unique for the
lint; the face the player sees is the card's own name.


## proto_mi_gorou_war_banner

`EB-403` (Kokomi round 10, run 1, (c) 1). The face printed "Gain 2 Dexterity
for 2 turns" on a screen whose Dexterity gloss says "It does not decay". Both
sentences are true and they read as a contradiction: what the row grants is
real `DexterityPower`, and the second effect it applies -- `mi_war_banner`,
`WarBannerPower` in `Powers/Prototype/CompanionOverhaulInazuma.cs` -- is a
clock that takes 2 Dexterity back when it runs out, at the end of the turn its
`Amount` reaches 1 (`CompanionOverhaulTurnEnd`, `AfterSideTurnEnd`).

The take-back clause is now on both faces, in that power's own words. The
number is the power's own constant, `CompanionOverhaulLaw.WarBannerDexterity`
= 2, and NOT the card's `PowerAmount`, which the upgrade moves to 3 -- so an
upgraded banner grants 3 and hands 2 back. That asymmetry is the shipped rule
as written and is disclosed here rather than changed; the base Dexterity gloss
stays the base rule and the exception is printed where the exception is made.

## before proto_fr_aria_of_recompense

The starter's reader, R254 (2026-09-04), Furina reframe round 4 pick 1. The
packet is `review/ruled/furina-reframe-round-4-2026-09-04.md`; its sec.6 is
the ruling, and it answers neither of the two options as written. [USER]:
"maybe a reader in the starter deck? I still want to leave it at just 2
'good' cards, but they can be stronger." So her starter keeps its two kit
cards -- Salon Début and Aria of Recompense -- and ONE of them reads Fanfare.

The reader goes on Aria, the card the seats had already weighed on three
axes. Under the arm it prints "Gain 5 Encore. If you have at least 6
Fanfare, gain 5 more." Both numbers are lifted and neither is new: the 5 is
Aria's own printed Encore and the 6 is the bar the four rider copies above
already carry. The loop it closes is the reframe's own -- a stage that
performs mints Fanfare, Fanfare pays Encore, Encore pays performances -- and
the 20% Encore decay is its brake.

Arm-only copy by the same seam as the riders, so the shipped sheet stands
(R213 B). The difference is which door: the riders are swapped in where a
run is OFFERED a card (`loader._pool_substitutions`,
`FurinaReframeRoster.SwapOfferedRiders`) and this one where a run is DEALT
one (`furina_reframe.STARTER_SUBS` read by `loader._starter_ids`;
`FurinaReframeRoster.StarterAria` called from `Furina.StartingDeck`). One
card for one card, so the printed ten is still ten, and with the arm off the
shipped Aria is dealt. The R130 veto on the SHIPPED starter's payoff
([USER], 2026-08-07) is untouched: it rules a Balance-stage sheet, and this
moves a prototype arm.

A STARTER CARD'S TEXT IS A RULE, so this one goes back to [USER]: he plays
the first build that carries it, per the norm on when [USER] plays. The
alternative reader is HELD rather than withdrawn -- Salon Début performing
its member again at 6 Fanfare is the packet's own re-ask if Aria's does not
read.

Numbers are Prototype numbers, D by the ladder, and nothing measured on them
is quotable.
