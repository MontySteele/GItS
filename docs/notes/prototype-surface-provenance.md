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

## before proto_ko_kaboom

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
# / `-p:KleeOverhaul=true` the first five ARE Klee's ten-card starter and the
# rest ARE her whole offerable pool -- `loader._starter_ids` and
# `loader.pool_replacement` in the sim, `Klee.StartingDeck` and
# `KleeCardPool.FilterThroughEpochs` in the mod. With the flag off none of them
# can be reached by any path, which is the acceptance condition
# (`tier0/tests/test_klee_overhaul.py`).
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
# ONE DISPLAY NAME IS SUFFIXED. "Sparks 'n' Splash (proto)": the shipped card of
# that name is Klee's KIT Burst card, which is granted by the meter and is
# therefore still reachable in the same run as this Power. Every other name here
# is the packet's own, because the shipped card that shares it cannot be reached
# while the flag is on.
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
# TEN DISPLAY NAMES CARRY A "(proto)" SUFFIX. Those ten rewrite a SHIPPED row
# whose display name they keep, and `tools/lint_unique_names.py` holds one
# namespace across all six sheets -- so the suffix is what lets the rewritten
# Frostgnaw and the shipped one coexist while the arm is being graded. It is
# the same device `proto_ko_sparks_n_splash` already uses. The other eleven
# names are new and carry no suffix.
#
# THIRTEEN OF THE WORKSHOP'S THIRTY-FOUR UNIVERSALS ARE NOT HERE, each because
# its printed text wants an engine hook that exists in NEITHER engine. A card
# that cannot be printed as written is left OUT rather than replaced by a
# simpler card -- the same rule the Klee overhaul applied to Vermillion Pact --
# and the hook each one wants is named so the next slice can price it:
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

## The Kokomi overhaul, slice one — `proto_kk_` (2026-09-01)

Thirty-three rows: the ten-card starter (five ids) and all twenty-eight pool
rows of `review/active/kokomi-overhaul-slice-1-2026-09-01.md`, written against
the ruled brief `kokomi-brief-2026-09-01.md` (all eight picks ruled at their
defaults on 2026-09-01). Under `C.KOKOMI_OVERHAUL` /
`-p:KokomiOverhaul=true` these ARE her starter and her whole reward pool; with
the flag off they are unreachable, like every other row on this surface.

```
NOTHING DROPS. The Klee overhaul left Vermillion Pact off its own surface
because its rule wanted shared reaction code. Every row of this slice prints
inside the grammar the emitter already speaks once the arm's ten verbs exist,
so all twenty-eight are here and the packet's own rarity split -- 12 Common,
12 Uncommon, 4 Rare -- is the pool's.

EVERY ROW CARRIES ITS OWN `description:` (EB-215). The face is the packet's
printed text with this repo's rendering conventions applied: "Deal 6." becomes
"Deal 6 damage.", the six keywords are golded, and Exhaust is the keyword
rail's -- the same treatment the Klee slice's "Set off. Deal 6." got. No
number moves and no clause is added or dropped.

ELEVEN DISPLAY NAMES CARRY A "(proto)" SUFFIX, and they are:
  Water's Edge, Coral Guard, Kurage's Oath, Stolen Chapter, Song of Pearls,
  Nereid's Ascension, Sango Isshin, Undertow, Salt Line, Cleansing Tide
  -- ten names already owned by a SHIPPED Kokomi row, and
  High Tide -- owned by a shipped FURINA row (`furina-cards.yaml:high_tide`).
`tools/lint_unique_names.py` holds one namespace across all six sheets plus
the relics, so the suffix is what lets the rewritten card and the shipped one
coexist while the arm is being graded. It is the same device
`proto_ko_sparks_n_splash` and the ten `proto_mc_` rewrites already use. The
packet's sec.8 names seven of the ten Kokomi collisions; the other three
(Song of Pearls, Undertow, Cleansing Tide) and the Furina one were found by
running the lint over the six sheets and this surface together, and the same
rule was applied to them. The remaining twenty-two names are new.

THE TEN VERBS, and what each row's clause resolves to:
  gain_tide                 Tide +N. `per: enemies_hit` is Deep Current's
                            "per enemy hit", read off a snapshot taken at the
                            TOP of the body -- an enemy the card's own AoE
                            killed was still hit.
  surge                     rule 3: the whole Tide as one Hydro hit, then 0.
  block_half_surge          Undertow's second clause, read off the play's own
                            Surge total because the jellyfish is empty by the
                            time it asks.
  exert                     rule 5, and it is DAMAGE rather than an HP loss:
                            dropping `Unblockable` is what lets Block eat it.
                            Refused on an Attack by the emitter, which is
                            rule 5's second half enforced where a card is
                            built.
  mend                      heal, capped at her entry HP -- one function, so
                            the cap cannot be forgotten at a call site.
  plan                      rule 8, ONE clause from a table of seven, spelled
                            `then:` so the repo's one effect walk sees it.
  draw_companion_from_draw  Rally's search, through the game's own
                            pile-selection screen filtered to Companions.
  next_companion_free       Vanguard's grant. It ZEROES rather than discounts,
                            because the card prints "costs 0".
  draw_per_tide             Reading the Tide. A read, not a spend.
  play_top_of_draw          War Council's clause, and legal ONLY inside a
                            `plan` body -- a top-level spelling would be a
                            different, unpriced card.

THE READINGS TAKEN, each because the printed text does not settle it:
  Deep Current    "per enemy hit" is every living enemy when the card was
                  played, snapshotted before its own AoE resolves.
  Undertow        "half the damage dealt" is half the TIDE that went out,
                  rounded down -- not the number that landed after the shared
                  pipeline's amplifier and the target's Vulnerable, neither of
                  which is a fact about her Tide.
  Ambush / Feint  a Plan's damage is HYDRO, through the same funnel the Surge
                  and Sango Isshin's overflow use. The cards name no element;
                  Hydro is the only choice that leaves Feint's two halves
                  behaving alike, the printed one applying an element and the
                  delayed one not.
  The Art of War  "Plans ALSO happen now" is read as now AND next turn. As
                  "instead" it would delete rule 8 rather than break it, and
                  the brief's gloss is "Rule 8's delay is gone".
  Song of Pearls  vs The Clouds Like Waves: both make a flat statement about
                  the pulse's size and neither prints an order, so the larger
                  applicable number wins. Under 4 the Clouds card would be a
                  lie; under 3 Song of Pearls would be one. The budget is
                  Song's alone, because only Song mentions it.
  The pulse       spends its per-combat budget in HP THAT LANDED. Script A's
                  turn-1 pulse "would Mend 2, but she is at 80, so nothing",
                  and after three effective pulses "the pulse paid 6 of its
                  8". A consequence, reported rather than hidden: the damage
                  Sango Isshin makes out of the excess costs no budget either.
  The Garment     "each Attack that HITS" is per Attack CARD PLAY that landed
                  on something, not per hit -- sec.6.1's "three Attacks each
                  put 2 back" and script B's "Water's Edge twice (12, Mend 4)".
                  Blocked damage still counts as a hit.
  The Plan hook   resolves at `AfterPlayerTurnStart`, NOT before the draw as
                  the packet's sec.5 asks. There is no broadcast between the
                  game's energy reset and its hand draw, so "before draw"
                  means before the block clear and the energy reset too, and
                  Read the Field's Block and Battle Plan's Energy would both
                  be wiped. The brief's own script C requires the later hook:
                  its turn 2 opens on five energy, which is three plus the
                  Plan's two. Recorded in full on the method.

WHAT THE STARTER COSTS, stated: her opening deck goes from TWELVE cards to
TEN, which is the packet's own sec.3 count -- the twelve-card shape was ruled
for a deck that mills itself, and nothing in this arm exhausts. And the
starting-companion roll finds no slot to take, because it matches on the
shipped `SayuDarumaGift` type and none of the ten is that type: under this arm
she opens with no companions, and the Commander loop draws its army from the
reward slot, which is what the packet says it does.

THE RELIC. Tamanooya's Casket replaces the Pearl of Wisdom, because the
Pearl's printed body IS the exhaust funnel the brief retires. It carries the
pulse and both its numbers, keeps the companion reward slot (that hook is not
a Charge rule, and the Commander loop's whole army comes through it), and has
no upgraded form -- a curated absence in
`tier0/tests/test_starter_relic_upgrades.py` with its reason and the gate that
clears it.
```
