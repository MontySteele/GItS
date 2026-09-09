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
# ---------- ARM 1: Pearl Barrage's counting basis (R215 C) -------------------
# Shipped twin: `pearl_barrage` (docs/kokomi-cards.yaml). That card reads the
# cost of THE ONE CARD you chose to Exhaust. This one reads how many cards have
# been Exhausted THIS TURN -- the reading [USER] expected it to have. It still
# Exhausts one chosen card itself, and that card is in its own count, so the
# floor of the two shapes is the same number on a turn with one rotation in it.
# Base 5 and per 3 are the shipped numbers, UNMOVED: the counting basis is the
# question, and moving a number too would make the answer unattributable.
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
# Candidate 1, renamed. sec.4.2: "Spend 1 / 8 damage", mirroring Regent's
# `GuidingStar` (1 star, 12 damage). Its twin on the printed sheet is
# `sparkly_treasure`, whose entire body is "gain 1 Spark" -- the purest
# generator in the pool becoming the cheapest sink in it.
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
# Shipped twin: `powder_charge` / "Powder Charge" (docs/klee-cards.yaml:248 --
# 1 Energy, Spend 2 Sparks, Uncommon Skill: detonate the target's Bombs for
# +4 each). Cost 1 -> 0; the Spark price, the detonation and the +4 are
# unmoved. Its shipped caveats ride along unchanged: dead on an unbombed
# target, and the bank is spent either way.
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

IT NOW HAS A SLOT (`EB-507`, 2026-09-06). Until this change the row was granted
from a scenario and offered by nothing -- the arm's own Rare drain, unreachable
in a run. `EB-507` took the three shipped Fanfare-floor Rares off the arm's
offer surface, and one of them, `the_sea_is_my_stage`, is NOTHING but the
floor rider: one `gain_fanfare_floor 15` op and no body. There is no copy to
make of a card with no body, so what it hands over is its Rare slot, and the
drain takes it. Rare for Rare, so the offer odds do not move; the row itself is
unchanged, and the shipped card still exists and is still dealt with the arm
off (R213 B).

THE SLOPE IS 2 PER DRAINED (the second-wave review of 2026-09-06; a D default).
At `per: 1` the Rare never out-damaged Universal Revelry's arm copy anywhere in
the meter's measured 0-to-15 range -- and it emptied the meter to do it, so the
card paid twice and bought nothing. `{base: 5, per: 2, count: fanfare_drained}`
is the printed slope; the face renders it through `{ExtraDamage:diff()}`, which
the emitter reads off `per:` (`fanfare_drained_calc_rider`).

ITS UPGRADE IS `{cost: -1}`, 2 Energy to 1, and it is DERIVED rather than
authored: the row carries no `upgrade:` key, so
`upgrades.prototype_default_delta` decides, and every number-moving clause of
that rule passes over it -- the damage op is formula-scaled and carries no
literal `amount`, which `_proto_hit` skips by name -- leaving the rule's cost
clause, "a card of cost 2 or more with no printed number costs 1 less". The
slope moving 1 to 2 does not change which clause fires.

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
the shipped card. The rows declare the shadow with ` (proto)`, the one suffix
`loader.display_name` strips in both engines, so the face the player
sees is the card's own name (`EB-419`: they spelled it ` (reframe)`
at first, which nothing stripped, and the arm's starter reached the
round-5 seat printing the tag).


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

THE BAR MOVED 6 -> 3 (the Furina reframe's round 6, sec.4, 2026-09-04 -- a D
default taken at its stated value and disclosed in that round's record, which
is where the three runs are read). It was built at the riders' 6 and three seat runs played Aria with the second
line never paying once: Aria is a STARTER, played at the top of a turn and
before the stage performs, so the meter it reads is not the one the offered
riders read later in the same turn -- 3 is the Fanfare the records show on an
Aria turn. So the row's condition is `fanfare_at_least_3` and it pays 5 at
Fanfare 2 and 10 at Fanfare 3. The 5 is untouched, the upgrade is untouched,
and the four OFFERED rider copies keep their own bars (6, 6, 8 and 10) --
those are read at a different point in the turn, and nothing in this move
says anything about them.

Numbers are Prototype numbers, D by the ladder, and nothing measured on them
is quotable.

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
there on the turn the pile is worth cashing. Fwoosh! with Retain and one less
damage; no new rule.

**`proto_ko_bombs_away` -- the placer that is not a Skill.**
Round 13's Smoggy reading: one Skill per turn against a kit whose placers are
Skills by rule. Fish-Flavored Bait and Bang Bang! are already Attacks that
place; this is the wide one. Against Mine Toss (1 energy, Skill, Mine 4 on
ALL): a hit now and half the charge, and no Mine. No new rule.

**`proto_ko_fireworks_show` -- Set off ALL, and the first Spark price an
upgrade moves.** `set_off` already had `target: all_enemies` (Flame Dance);
this is that spelling with the aura filter off and no hit of its own, which is
what puts it behind the `EB-261` gate -- its whole body is a damage-less Set
off, so it refuses a Bomb-less board rather than eating two Sparks for
nothing.

THE UPGRADE IS THE NEW PART. No delta on any sheet had ever moved a Spark
price, and this one cuts it to 1. It is `spark_price: -1`, it bumps the op's
own `amount` in tier0 (so `combat.spark_price`'s gate and `spend_sparks`'
payment move together by construction), and in C# it is a play-time
`IsUpgraded` read used by BOTH `PrintedSparkPrice` and the `SparkPower.Spend`
beside it -- one expression, so the badge, the gate and the payment cannot
drift. THE FACE PRINTS NOTHING FOR IT, and that is `text-conventions`' own
rule: a Spark price sits in the cost slot and the body does not restate it. So
the fifth channel an upgrade can show through is the Spark BADGE, and
`gen_prototype_cards`' upgrade-visibility gate learned to read it -- without
that it would have called a real, visible upgrade invisible.

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

## `proto_kk_well_laid` -- the face is the total, the rule is the tip (`EB-539`)

The row's face carried the rule as well as the number: "Deal
{CalculatedDamage:diff()} damage, already including {ExtraDamage:diff()} for
each Plan carried out this morning". On a BARE morning that renders "Deal 2
damage, already including 3 for each Plan carried out this morning", and the
r19 lane-2 seat read it as self-contradictory -- 2 cannot already include a 3
that nothing paid.

Nothing is wrong with the number. It is `EB-441`'s clause working exactly as
written, on the one board where the fold is zero: the face's total IS live and
the count IS folded into it. What the sentence needs is to disappear at count 0
and reappear above it, and a card has exactly ONE face -- `Localization` is
read once at registration, neither description getter on the shipped
`CardModel` is virtual, and BaseLib's only runtime swap is `{IfUpgraded:show:}`,
which asks about the card and not the board.

So the split is Undertow's, one count over (`EB-484`,
`KokomiRiderTips.ForDebuffRider`): the FACE prints the live total and nothing
else, and the RULE goes on the rider tip, which is the surface that can carry a
rule and a live count at once -- "2, plus 3 for each Plan the Bake-Kurage
carried out this morning; this morning: 0". Out of combat the rule stands
without the count, which is the `FurinaRiderTips` rule every tip in that file
keeps: a shop shelf has no morning, and "this morning: 0" printed there would be
the same false certainty the row was filed on. The tip is handed the same `base`
and `per` the rider emits the vars from, so it cannot quote a number the hit
does not use.

THE WORD MOVED WITH THE RULE. The arm-keyword attach is derived from the words
a face PRINTS, and this split took `Plan` off the face -- so the generator now
carries a rider's own printed words into that scan (`rider_printed`), and the
row keeps `ArmKeywordTips.ForPlan`. Without it the card would have gone on
saying `Plan` in its tip with nothing on screen defining it, which is the exact
silence that rule exists to make impossible.

## before proto_fr_curtain_rises

The Furina pool pass, one (`EB-493`); the packet is
`review/records/furina-pool-pass-2026-09-05.md` and all four rows are FOLLOWS on
the doctrine read (`review/records/card-audit-2026-09-04.md` sec.5.5).

WHAT THE ROUNDS SAID. Rounds 9 and 10 read the Salon as FURNITURE: one Deploy
in the whole deck, most Companion plays printing "No member on stage: performs
nobody", the kit's headline mechanic spent as text explaining why nothing
happened -- and the two turns it was live were the best of the run. The shipped
sheet offers three single-deploy Commons in twenty-three, all Skills of one
shape, and neither seat drafted one. Round 9 also found no legal way to make
her act: a member idle, no Companion card in hand, and nothing of Furina's own
that asks the stage for anything. The four rows answer one reading each.

**Curtain Rises** (replaces *House Call*) is the second Deploy SHAPE: a deploy
on an Attack, with the usher's Block as he arrives. Against *Cold Snap* (1
energy: 6 damage, channel Frost) it is the same line with a member for an orb.
A deploy on an Attack was new to the surface and needed nothing built -- the
damage aims, the deploy is the owner's, and one card carries both because they
target different things.

**Second Course** (replaces *Dinner Service*) buys a member's second
performance for three Encore, which is three Block she would otherwise hold:
the hold-or-spend tension on a deploy. The price is the `encore_cost` GATE and
NOT the `spend_encore` op -- the packet's sentence is "Unplayable below 3
Encore", and `spend_encore` is the overdraw primitive, which would have made
the card playable at 0 Encore for 3 HP. That is *Breathless*' rule and it is
printed on *Breathless*. THE PRINTED PRICE IS 1 AND NOT THE 3 IT WAS BUILT AT (`EB-552`, round 13,
FOLLOWS on the doctrine read, record sec.5.8): the printed 3 plus the shipped
per-performance drain is five Encore against an opening of two, and across
three rounds the card was refused on all four draws it ever had. At 1 the full
value is 3. The upgrade's `-1` is unchanged, so the `+` card is free and the
codegen drops the "Spend N Encore" sentence rather than printing "Spend 0"
(text conventions, the Evoke row).

**Guest List** (replaces *Blocking Notes*) puts An Invitation's verb in the
pool at a price: an energy and no Exhaust, three Block short of a Stage
Presence. THE EXHAUST IS THE ONE GUARDRAIL THIS PASS MOVES, and it is the only
one of kickoff sec.9's four that is a balance rule rather than a structural
fact -- this-combat-only, equal-rarity and the companion-plus-Guest-Star pool
are all properties of the code, while "generators Exhaust" is a sheet field.
`gen_klee_cards.blocked_reason` still refuses a non-Exhaust generator on any
`docs/*-cards.yaml` row; the exemption is the `proto_` prefix and nothing else,
so a row promoted to a shipped sheet meets the bar again on the way in.

THE ONE THING BUILT FOR THE PASS is an ARGUMENT and not an op:
`salon_perform` learned `member:`, so *Second Course* can say "she performs
once more" about the member it just deployed rather than about whoever stands
at the front (a deploy appends, so the two are only the same on an empty
stage). It rides the shipped verb for the reason the aimed Evoke does --
`tools/lint_op_parity.py` compares the KEY SET of the sim's op registry against
the drafter's priced-op table, so an extra field leaves the priced set
identical while a `salon_perform_member` synonym would have bought a
`DRAFTER_VERSION` stamp for a verb both engines already have. A named member
who is not on stage takes the FRONT, which is the slot-6 ruling's fallback for
the aimed Evoke, and the fact is emitted (`salon_perform_target_absent`) rather
than left silent.

ROLLING TIDE IS WITHDRAWN (`EB-552`, round 13, a D default, and the loop's
first cut). It replaced *Undercurrent* and was the kit's own perform verb on a
card she could draft. Four seats over three rounds read it the same way at two
energy and at one -- "4 damage into one body; zero against Plating 8; actively
harmful against four Skittish bodies" -- so the price was never the reason and
the row left the arm rather than moving a third time. The shipped Undercurrent
is offered again at that seam, and the row left this sheet with its pins under
R213 B's deletion rule.

WHICH SHIPPED ROWS, and it is the packet's sec.5 D default: each replaced
row is a plain number card of the same type and cost as its replacement, so the
swap moves what the card does and nothing about where it sits. Common for
Common in every case, so the offer odds do not move. The choice moves on the
seats' word. The shipped sheet stands (R213 B) -- the seam is
`furina_reframe.POOL_SUBS` and `FurinaReframeRoster.SwapOfferedRiders`, and
with the arm off no surface can see a `proto_fr_` id.

NO ` (proto)` SUFFIX ON THESE FOUR, unlike the rider copies above. The riders
are COPIES of a shipped card and share its name, which is what the shadow
suffix is for (`EB-419`); these are new rows with names of their own, so there
is nothing to shadow.

## proto_ko_jumpy_dumpty, `innate: true` (R261, `EB-557`, 2026-09-05)

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

## proto_fr_florid_cadenza, the arm copy (2026-09-06)

THE `+` CARD MOVES THE BAR INSTEAD OF DELETING IT. The rider copy is the
shipped Florid Cadenza at the arm's meter -- draw 1, and 2 more at 6 Fanfare
instead of 12 -- and it inherited the shipped row's `{condition: unconditional}`
upgrade, which HOISTS the gated clause out. That made the `+` card a 0-cost
"draw 3" that asks nothing at all: the strongest card in the arm's pool, and
the one card in it with no relationship to the meter the whole reframe is
about. The 2026-09-06 GPT balance review read it that way and the main session
took the D default.

So the delta is `{condition: fanfare_at_least_3}`: the gate STAYS and its
threshold falls 6 -> 3. The upgraded card still draws 1, still asks the arm's
question, and asks it at a bar an opening turn can reach -- the same 3 R254's
starter reader was moved to, and for the same measured reason (the meter an
early turn actually holds).

THE GRAMMAR IS NEW AND IT IS THE SMALLER OF THE TWO SPELLINGS. `condition:`
used to accept only `unconditional`. It now also accepts a meter bar naming the
upgraded threshold: tier0 rewrites the top-level conditional's `if:`
(`content/upgrades.py`), and the codegen emits ONE comparison whose threshold is
`(IsUpgraded ? 3 : 6)` with the face printing both numbers through a single
`{IfUpgraded:show:3|6}` token (`gen_klee_cards.moved_bar_predicate_cs`). Both
bars are authored on the row; nothing computes a threshold. Both engines refuse
a bar that reads a different meter from the printed one.

AND THE COPY EXHAUSTS (the second-wave review of 2026-09-06; a D default). A
0-cost non-Exhaust draw-3 whose bar does not deplete is a
hold-the-rest-of-the-deck loop -- three copies, a hand cap of 10, the overflow
to discard -- and it is that at bar 6 exactly as much as at bar 3, so the bar
move above was never the whole answer. `exhaust: true` makes each copy a
one-shot and the moved bar stays as it is.

The sheet's sentence keeps the word and the emitted face drops it
(`_dedupe_printed_exhaust`, `EB-293`): `exhaust: true` puts
`CardKeyword.Exhaust` on the card and the game's keyword rail prints the
banner, so a face that also wrote it would print it twice.

Nothing else on the row moves -- same cost, same rarity, same body -- and
`docs/furina-cards.yaml` and `docs/furina-upgrades.yaml` do not move at all:
the shipped Florid Cadenza, its shipped `{condition: unconditional}` and the
absence of Exhaust on it are Balance-stage content (R213 B).

## proto_fr_shared_billing

Face: the shipped Shared Billing's, unchanged -- "Apply Hydro to a random
enemy. Spotlighted Companion cards gain 25% this turn. Gain 1 Energy." Same
cost, same rarity, same three effects, same art (`art_of`, R179).

ONLY THE UPGRADE DIFFERS, and that is the whole row (the 2026-09-06 GPT
balance review; the main session's D default). The shipped delta is
`{cost: -1}`, which takes a Common that already REFUNDS its Energy down to 0 --
a card that costs nothing, gives a card's worth of Energy back, and is handed
out at every campfire.

IT BUYS BLOCK, NOT A CARD (the second-wave review of 2026-09-06; a D default).
The first pass bought a card, `{add: {op: draw, amount: 1}}`, and a card that
refunds its own Energy and then replaces itself is the same loop piece the
shipped `{cost: -1}` was taken off for -- free, repeatable, and net-positive on
both of the resources a loop needs. Block is neither energy nor draw, so the
delta is `{add: {op: block, amount: 3}}`: the `+` card buys survival and the
loop stays shut. Rendered by the emitter as an `IsUpgraded`-gated Block
appended after the printed body, with `GainsBlock => IsUpgraded` so the base
card claims none (`EB-122`), and an
`{IfUpgraded:show:Gain 3 [gold]Block[/gold].|}` clause on the face.

Common for Common at the same seam as the rider copies
(`furina_reframe.POOL_SUBS`, `FurinaReframeRoster.SwapOfferedRiders`). The
shipped row and its shipped delta stand (R213 B).

## proto_fr_rapturous_applause

Face: "Your Attacks deal 1 additional damage per 5 Fanfare." The shipped
Rare's body with its `gain_fanfare_floor 8` rider removed (`EB-507`), read at
the arm's own granularity.

WHY THE RIDER GOES. The reframe mints Fanfare by PERFORMING -- 2 per trigger, 5
per Evoke -- and `gain_fanfare_floor` mints it for being played. That is a
second source the arm neither has nor priced, and with the arm on it is the
offer surface contradicting the arm's one sentence about where the meter comes
from. Three shipped Rares print the rider; this is one of the two that have a
body underneath it.

WHY PER 5 AND NOT THE SHIPPED PER 10. The floor the copy no longer mints was
also this card's own opening payment -- it arrived with 8 Fanfare already on
the meter, which is most of the first 10 the shipped clause reads -- and a
per-10 clause on a meter that runs 0 to 15 pays on the top third of the range
or not at all. So the copy takes the THRESHOLD mapping every other arm copy in
`POOL_SUBS` takes: the shipped bars 12, 12, 15 and 20 became 6, 6, 8 and 10
because the shipped meter's 20-to-30 range maps to the arm's 0-to-15, and this
row's 10 becomes 5 for the same reason. The upgrade is the shipped
`{power_amount: +1}`, so the `+` card reads 2 per 5.

THE FIRST READ WAS 2 PER 10, AND THE AUDIT OF 2026-09-07 RULED IT
REQUIRES_MODIFICATION ON C8. That number pays for the lost floor out of the
PAYOUT rather than the threshold, which is the one move an arm copy of a
shipped rider may not make: it is the shipped card at 10 Fanfare, twice the
shipped card at 20, and nothing at all below 10. 1 per 5 is the same slope --
one point of damage for every ten points of shipped Fanfare, or every five of
the arm's -- and the granularity is the only thing that changed, which is what
puts the copy back on the mapping the other four rows already use.

Rare for Rare, art borrowed from the shipped row (`art_of`, R179), shipped
sheet unmoved (R213 B).

## proto_fr_unheard_confession

Face: "Whenever your Fanfare changes amount, gain 2 Block." The shipped Rare's
body with its `gain_fanfare_floor 8` rider removed, for `EB-507`'s reason
above.

TWO PER CHANGE, NOT THE SHIPPED ONE (the second-wave review of 2026-09-06; a D
default). The power pays per change EVENT and not per point moved, which is
what the first pass read as "no number to compensate" -- but it is also the
reason 1 is not a Rare's payout: a 2-cost Rare Power that pays 1 Block each
time the meter ticks is a dead card on a meter that ticks a few times a turn.
2 is the floor that makes the slot worth a Rare. Cost 2 and the shipped
`{cost: -1}` upgrade are unchanged. Rare for Rare, art borrowed (`art_of`,
R179), shipped sheet unmoved (R213 B).

## the coven's Hexerei mark (`EB-642`, 2026-09-07)

R265 pick 1 made the printed word the whole rule, and the one-word rule would
otherwise have cut the grant from Klee's OWN coven -- eight Personals that
paid a Spark and printed no family word -- which the pick did not name as a
cost.

The family is the coven plus the marked Universals: `hexerei: true` now sits on
`proto_mc_barbara_front_row_seat`, `proto_mc_diona_shaken_not_purred`,
`proto_mc_noelle_i_got_your_back`, `proto_mc_kaeya_cold_blooded_strike`,
`proto_mc_jean_lions_fang`, `proto_mc_sayu_silencers_secret`,
`proto_mc_qiqi_herald_of_frost` and `proto_mc_yaoyao_yuegui_throwing_mode`,
so every Companion face of Klee's prints the word and pays it.

The readers (Coven Errand, Witches' Circle, Venti's stand-in) therefore fire on
a wider set than R244 wrote them against; that widening is read at the audit
door in pool pass two, not assumed here.

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

### `proto_kk_second_wave` -- the second rider

"The next Plan carried out with this one is carried out twice." A FLAG and
not a count: an entry carried
out twice under Nereid's Ascension prints its rider twice, and "carried out
twice" said twice is still twice -- so the entry it reaches runs
`CarryOutTimes + 1`, which is 3 under the Ascension and not 4. Both engines
state that at `kokomi_plan.NEXT_PLAN_EXTRA_CARRY_OUT` and at
`KokomiPlan.Kind.NextPlanExtraCarryOut`, and both pin it.

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

**Why the two-branch faces carry two `{IfUpgraded:show:…}` holes.** Every Spend
rider is printed as `conditional {if: stage_occupied, then: [stage_spend,
<big>], else: [<base>]}`, which is rule 8's two sentences as two branches. A
`conditional_damage` / `conditional_block` delta moves BOTH branches, and the
emitter only rewrites the literal it finds in the `then` arm — so a face
written with a bare base number would print 7 while the upgraded card dealt 10.
The base number carries its own hole, authored on the row. **This is a codegen
limitation worth a row of its own:** the emitter should hole every branch a
whole-card delta moves, and today it holes one.

**The three upgrades that are not numbers.** *Understudy* and *Final Bow* drop
their Exhaust; *Salon Début*, the three named summons, *Rising Applause*,
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
