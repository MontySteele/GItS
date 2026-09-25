"""The standing notes a page prints, and the arm-keyword glossary.

Cut out of `blindplay.py` by `EB-180`: the sentences the page prints
beside a screen when the data feed cannot answer something, and the
register of arm keywords with one definition each. Re-exported from
`blindplay.py`, so `blindplay.ARM_KEYWORDS` and
`blindplay.HAND_REPEAT_NOTE` still resolve.

Prose, not shape: each note is a fact about what the WIRE carries,
held in step with the mod from the other side by a test that reads
the C#. Nothing here reads a state.
"""
from __future__ import annotations

import re
from typing import Any

from understudy.blindplay_faces import remember_elements
from understudy.blindplay_read import _fold
from understudy.blindplay_shape import (AURA_DURATION_TURNS, BOMB_GROWTH,
                                        CASKET_STRIKE,
                                        CRYSTALLIZE_BLOCK, OPENING_SPARK,
                                        SHATTER_DAMAGE,
                                        FRAIL_BLOCK_PCT, VULNERABLE_TAKEN_PCT,
                                        CRYSTALLIZE_BLOCK, SHATTER_DAMAGE,
                                        FRAIL_BLOCK_PCT,
                                        SHRINK_DEALT_PCT,
                                        VULNERABLE_TAKEN_PCT,
                                        WEAK_DEALT_PCT)




# `EB-179`. THREE LEGIBILITY GAPS RUN B6 REPORTED, AND WHAT THE WIRE ACTUALLY
# CARRIES FOR EACH. Read off the live bridge on 2026-08-29 and confirmed
# against the vendored builder, so these lines state a fact about the feed and
# not a guess:
#
#   POWERS -- a status row is `id`, `name`, `amount` (the game's own
#     `DisplayAmount`), `type`, `description` (the game's own resolved
#     `SmartDescription`) and `keywords`. There is NO duration or expiry
#     field. Where the game states a duration it is inside the printed text
#     (`Vulnerable 3`: "...for 3 turns"); where it does not, nothing else
#     says it either (`Thorns 3`: "When hit by an attack, deal 3 damage
#     back."), which is the Toadpole's Thorns that came and went unexplained.
#     So: print the `type` the page was dropping, and say the rest out loud.
#
#   METERS -- the resource snapshot reflects each registered resource's `Id`
#     and `Amount` and nothing else. There is no maximum and no spend rule on
#     the wire, so a meter cannot print one.
#
#   ENCHANTMENTS -- the card builder emits `id`, `name`, `type`, `cost`,
#     `star_cost`, `description`, `rarity`, `is_upgraded` and `keywords`. No
#     enchantment field exists, and run B6's live evidence says an enchant
#     reaches none of the fields that do. Filed as a bridge gap rather than
#     patched here. The note is printed only where it bites -- a hand holding
#     two cards that print one name, where the reader can SEE two faces and
#     the page cannot tell them apart.
#
# Each line says what is missing and whose it is to carry. None of them
# invents a number, and none names a register id -- the page is scrubbed.
POWER_NOTE = ("*A power's number is what the game's data feed reports for it. "
              "The feed carries no duration and no expiry, so unless a "
              "power's own text says when it ends, this page cannot say "
              "either.*")

# `EB-701`. NOTHING ON THE PAGE SAID WHEN "THE END OF YOUR TURN" IS.
#
# THE FIND (Kokomi r30 lane 1, debrief 5). No line says that end-of-turn
# effects -- a companion's end-of-turn hit, a Dusk Plan -- resolve BEFORE the
# enemies act; the seat learned it from a Gas Bomb dying without its Death
# Blow, which is a rule learned from a body that did not do the thing the page
# had just telegraphed.
#
# IT IS A SENTENCE ABOUT THE TURN AND NOT ABOUT ANY POWER, so it sits with
# `POWER_NOTE` at the foot of the board rather than under the row that raised
# it: two powers with the same trigger would otherwise print it twice, and the
# question is asked once per screen.
#
# THE CONSEQUENCE IS HALF THE POINT. "Before the enemies act" is only a fact
# about ordering until it is said what the ordering buys, which is that a body
# killed at the end of your turn never takes the intent printed above it.
TURN_ORDER_NOTE = (
    "*The end of your turn is a step of its own, and it comes BEFORE the "
    "enemies act: everything that fires at the end of your turn -- a power's "
    "end-of-turn trigger, a performer's act, a Dusk Plan -- resolves first, "
    "and only then do the bodies above take their intents. So an enemy killed "
    "by one of those never takes the intent this page printed for it.*")

METER_NOTE = ("the game's data feed carries this meter's amount only: no "
              "maximum, and no rule for how it is spent")
# `EB-181`. The same row where the meter DOES declare a ceiling. The second
# half of the sentence stands untouched -- a maximum is not a spending rule,
# and nothing on this wire says what fills or empties a meter.
METER_CAPPED_NOTE = ("the game's data feed carries this meter's amount and "
                     "its maximum, and no rule for how it is spent")

# `EB-407`. The third case: the glossary on this same screen already defines
# the word, so the meter line points at it rather than printing the rule twice.
# One definition per screen is `keyword_notes`' own rule, and the meters block
# was the one place two sources could both fire on one word.
METER_DEFINED_NOTE = "defined under *Words on this screen*"

# `EB-382`. WHERE A METER'S SPEND RULE EXISTS, THE ROW SAYS IT.
#
# The Furina round-two seat ended a turn holding four banked Encore and opened
# the next one with none, three times across three fights, and read it as a
# confiscation: "Encore evaporates at the start of my next turn". It does not.
# Encore is a damage buffer -- after Block it absorbs incoming damage before HP
# -- and every one of those boundaries had an enemy hit in it. Fight 1's
# arithmetic settles it: a `2x4` intent, HP 57 -> 53 and Encore 4 -> 0, which
# is eight damage split four and four. The one turn the seat kept its Encore is
# the turn its own record calls "Took 0 damage".
#
# THE RULE WAS WRITTEN AND REACHED NOBODY. `EncoreMeterPower` states it in the
# mod in one sentence -- but that badge was RETIRED as a display in the
# 2026-07-24 diet, its ambient home being the Salon stage ribbon, which is art
# and reaches no page. So `METER_NOTE` said, correctly, that the feed carries
# no spend rule, and a seat was asked to budget a resource the screen would not
# explain.
#
# WHAT THIS TABLE IS, AND IS NOT. It is not a glossary of meters: a row here is
# a spend rule the MOD declares and the FEED cannot carry, keyed by the name the
# page prints (`qa_packet.label` of the wire id). A meter with no row keeps
# `METER_NOTE` unchanged, still saying what is missing and whose it is to carry.
# The wording is held in step with the C# by
# `test_the_encore_meter_rule_is_the_mods_own_sentence`, the discipline
# `ARM_KEYWORDS` and `REACTION_KEYWORDS` are already under.
#
# ENCORE'S FANFARE CLAUSE IS DELIBERATELY ABSENT from the Encore row.
# `EncoreMeterPower`'s second sentence says losing Encore creates Fanfare, and
# the reframe's METER leg retires exactly that, so a page printing it would be
# teaching a rule this build does not have -- the reason `Tide` and `Exert` are
# out of `ARM_KEYWORDS`, one meter over.
#
# `EB-437` ADDED FANFARE'S OWN ROW, because the two readouts on one screen
# disagreed about whether a spend rule exists at all. `FanfareMeterPower`'s arm
# face ends "Cards read it and none spends it"; this block, with no row for the
# word, printed `METER_NOTE` -- "no maximum, and no rule for how it is spent".
# The r6 act-1 seat read both and filed the pair: "the two Fanfare readouts on
# the same screen say different things about whether a rule exists for spending
# it", inside a finding whose headline was "Fanfare does nothing I could
# observe". Both sentences were true of their own source and the pair was not:
# the mod states the rule, so the row prints it and the generic note stands
# down. Held in step with the C# by
# `test_the_fanfare_meter_rule_is_the_mods_own_sentence`, the same discipline
# the Encore row is under.
METER_RULES: dict[str, str] = {
    "Encore": ("a buffer and not a bank: after Block it absorbs incoming "
               "damage before HP. Cards spend it, and a Salon member spends "
               "1 each time it performs"),
    "Fanfare": "cards read it and none spends it",
}

# `EB-560`. WHERE THE FIRST SPARK COMES FROM, on the screen that has it.
#
# "Where Spark comes from is not on the combat screen. I opened fight 1 with 1
# and could not tell whether that was a starting bank, a relic, or something a
# card had done" (Klee r20 lane 2). The rule is R242 pick 1's and it IS printed
# -- inside the Spark keyword tip -- but that tip is raised by a card that
# PRINTS the word, so a seat whose opening hand holds no Spark-priced card
# meets the meter row and nothing else.
#
# ROUND ONE ONLY, which is what makes it the opening rule rather than a fact
# about the meter: a bank read on round 4 is the sum of everything since, and a
# page repeating "you started with 1" on it would be answering a question
# nobody is asking any more. `METER_RULES` is the wrong home for the same
# reason -- those rows are true on every screen the meter appears on.
#
# AND ONLY WHERE THE GLOSSARY IS NOT ALREADY SAYING IT (`EB-407`): the Spark
# tip carries the sentence in full, so a screen that raised it has the rule and
# a second copy on the meter row would be the two-sources defect this page has
# closed twice.
SPARK_OPENING_RULE = (f"you start each combat with {OPENING_SPARK}, and cards "
                      "that print a Spark price spend it")

# `EB-610`. WHERE THIS FIGHT'S SPARKS CAME FROM.
#
# THE FIND (Klee r23 lane 2, fight 5, turn 4): "a Spark appeared with no Bomb
# on the field" -- the bank went 2 to 3 across Kaeya and Rapid Fire on a bare
# board. The one sentence naming a Spark source anywhere on that screen is the
# relic's, "whenever a Bomb goes off", so the meter contradicted the only rule
# the reader had been given and nothing could settle it. The rule above says
# where the OPENING bank came from and `METER_RULES` says what the meter IS;
# neither can say what paid the bank in.
#
# `EB-796`: THE WINDOW WAS ONE TURN AND IS NOW THE FIGHT, and the line says so.
# It used to read "This turn:", stated out loud on the reasoning that the bank
# is cumulative and the sources were not. The live look of 2026-09-16 (proofs-9
# lane 0, defect 3) showed what that costs: turn one printed "This turn: +1
# your opening bank" beside `Spark 1`, and a later turn printed `Spark 3`
# beside "This turn: +2 an explosion" -- the sources summing to 2 against a
# bank of 3, with the +1 that is still sitting in that bank named nowhere. A
# Spark does not expire at end of turn (R270: a currency whose income stays),
# so the reader's question is about the BANK and the bank is a fight-long fact.
# `GitsSparkSourcesState` now sends every gain of the fight, and this line
# names that window rather than a narrower one.
#
# "SO FAR", AND "+", BECAUSE IT IS INCOME AND NOT A BALANCE. The gains here sum
# to the bank only on a fight that has spent nothing: a Spark PRICE is a row of
# the same ledger and is deliberately not on this field (the ledger's own
# header argues why a page may not carry it). So the sentence promises what
# paid in, which every term in it is, and never what is left.
SPARK_SOURCES_LINE = "So far this fight: {sources}."

# `EB-263`. THE ENCHANT PICKER MARKS NOTHING, and the r3 Opus seat found out
# the hard way: after `choose "Flame Dance"` "the whole list reprinted
# byte-identically; the only change anywhere on the screen was the footer
# going from `Confirm is not available.` to `Confirm is available.`". The
# reason was on the bridge and not here -- `BuildCardSelectState` read every
# grid card through `BuildCardInfo`, which had no selected flag, and the
# enchant screen's two preview containers were never looked up for
# `preview_cards` to hold. Both are closed on the bridge side of this row.
#
# THE NOTE STAYS, for the case that is left: a bridge that could not ask.
# `selection_known` is false when the grid's own selection could not be read
# at all, and "nothing is picked" and "I could not find out" are different
# things to tell a tester who is about to spend a turn confirming.
SELECTION_NOTE = ("*This screen's data feed did not answer which card is "
                  "picked, so nothing in the list above can be marked as the "
                  "one you chose. The `Confirm is` line below is the only "
                  "thing that moves when a pick lands.*")

# `EB-314`. THE CARD ON THE RIGHT OF A TRANSFORM SCREEN IS A SLOT MACHINE.
#
# What the r5 Opus seat saw: it picked `Strike (1)` and the page printed the
# result **Barricade**; the next two observations of the SAME screen printed
# **Dark Embrace** and then **Hemokinesis**. It confirmed on "Strike to
# Hemokinesis" and the deck came out with **Stomp**, one Defend short and
# four Strikes intact -- both halves of the line it was shown were wrong.
#
# Neither half was a re-roll. `NDeckTransformSelectScreen.OpenPreviewScreen`
# hands `NTransformPreview.Initialize` one `CardTransformation` per picked
# card; where the transformation carries no `Replacement` -- which is every
# random transform, and this screen's own doc comment says random is what it
# is FOR -- the preview starts `CycleThroughCards`, a loop that reassigns the
# right-hand holder to another card out of `CardFactory.GetDefaultTransform-
# ationOptions` EVERY 0.2 SECONDS until the screen closes. It is an animation
# on `Rng.Chaotic`, it is not the run's roll, and nothing it lands on is ever
# committed: `CompleteSelection` returns the SELECTED CARDS and the caller
# rolls the replacement afterwards. So three observations of one unchanged
# screen printed three frames of a reel as if each were the outcome.
#
# The page prints the left half -- `%Before`, which holds the cards actually
# picked -- and says in words that the right half has not been decided.
TRANSFORM_NOTE = ("*The card this becomes has NOT been chosen yet. This "
                  "screen rolls it at random when you confirm, and the card "
                  "it is showing on the right is an animation cycling "
                  "through the possibilities several times a second — it is "
                  "not the result, so it is not printed here. Confirming "
                  "means accepting an unknown card.*")
# The shape this has never been seen in: a transform preview whose cards do
# not pair off into a before half and an after half. Rather than guess which
# is which and risk naming a reel frame as the pick, the page names none.
TRANSFORM_UNREADABLE = ("*This transform screen is showing a preview whose "
                        "cards this page cannot sort into the ones you "
                        "picked and the ones it is cycling through, so it is "
                        "naming none of them. Say `skip` to go back to the "
                        "grid and pick again.*")
# `EB-314`'s other half. Every one of the five selection screens keeps its own
# `_selectedCards` set while its preview is open, and only the real UI's mouse
# block (`MouseFilter = Stop`, grid focus disabled) stops a further click
# reaching `OnCardClicked`. The bridge's `select_card` does not go through the
# mouse -- it emits `NCardGrid.HolderPressed` at the grid directly -- so a
# `choose` taken over an open preview silently changed WHICH card would be
# transformed while the preview went on showing the first one. That is exactly
# how the r5 seat confirmed "Strike" and lost a Defend.
PREVIEW_LOCKED = ("your pick is already made and this screen is showing it "
                  "back to you; naming another card here would change what "
                  "gets taken without changing what you are being shown. Say "
                  "`confirm` to take it, or `skip` to put it back and choose "
                  "again")

# `EB-329`, the card-removal half, and the refusal above is what made it
# legible in the end rather than the screen. The round-5 act-1 seat counted
# SIXTEEN rows on a removal screen over a fifteen-card deck: "the extra being
# a bare `Strike` after `Undertow (2)`, distinguishable only by the absence of
# a `(N)` index". It read that as a fifth Strike-family card -- as the Fishing
# Rod having ADDED an upgraded Strike rather than upgrading one in place --
# and only unpicked it two fights later off pile arithmetic.
#
# The rows were never wrong. `obs["selected"]` is the pending pick printed a
# SECOND time, under its own heading and numbered on its own, so the copy the
# grid already listed as `Strike (1)` reprints bare. Two lists in one format,
# one of them a subset of the other, and nothing on the page saying so.
#
# So the pick is MARKED on its own row (`PICKED`, the word `EB-294` already
# gave a chosen bundle) and the heading carries one sentence saying what the
# second printing is. Neither invents anything: the screen really is showing
# the pick back, which is what `PREVIEW_LOCKED` tells anyone who tries to
# name a second card.
# `EB-374`. THE SACRIFICE THAT NEVER REACHED THE PAGE, AND WHAT THIS PAGE CAN
# HONESTLY SAY ABOUT IT.
#
# THE FINDING. The r9 act-2 seat took Pael's Wing and met two card rewards
# afterwards; both printed `choose` and `skip` and nothing else, and the seat
# could not tell whether `skip` WAS the sacrifice the relic had promised or
# whether the sacrifice was somewhere it could not reach.
#
# WHAT THE FEED CARRIES, read off the vendored builder rather than guessed:
# a card reward is its list of cards plus ONE boolean, whether an alternative
# button exists on the screen at all. Not the button's words, not what it does,
# and `skip` presses that button whatever it has become. So the page cannot say
# that skip is the sacrifice, and it must not say that it is not.
#
# WHICH LEAVES THE HONEST LINE: name the relic the run is holding, say the
# control is not on this page's feed, and send the reader to the one place the
# words do exist -- the relic's own face, which this page prints. The register
# is folded relic names, one row per relic that is known to REPLACE this
# screen's alternative, because a page that printed the caveat on every reward
# screen of every run would be teaching a doubt that is not there. Carrying the
# control itself is a bridge change and belongs to `EB-310`'s family.
#
# THE POINTER WAS STALE, AND THAT IS THE ONLY THING THAT MOVED HERE
# (2026-09-07). It read "on your relic row in the next fight", which was true
# when the row was written and stopped being true at `EB-473`: the relic block
# now prints on every screen that is not a fight, and a card reward is one of
# them, so the words this line sends a reader hunting for are four lines below
# it on the same page. A caveat that sends the reader away from the answer is
# worse than the caveat alone, and this one did it on the screen where the
# decision is taken.
# FOLDED KEYS, and the fold is `_fold`'s: an apostrophe is punctuation there,
# so the relic the game prints as `Pael's Wing` is three words here. Written as
# the folded spelling rather than the printed one so the register cannot be a
# near-miss that silently matches nothing -- which is exactly what a hand-typed
# `paels wing` would have been.
REWARD_ALTERNATIVE_RELICS = {"pael s wing"}

CARD_REWARD_ALTERNATIVE_NOTE = (
    "*You are holding {relics}, which changes what the alternative to "
    "choosing a card does on this screen. The game's data feed carries the "
    "cards and whether an alternative button exists -- never what that button "
    "says or does -- so `skip` here presses whatever the button has become, "
    "and this page cannot tell you whether that is a plain skip or the "
    "relic's own option. Its own printed words are under *Your relics* on "
    "this page.*")

# `EB-333`. WHAT `skip` DID, SAID BY THE PAGE THAT TOOK IT. The verb answered
# `ok Skipping card reward`, no card was added, the run stayed where it was and
# no line joined those three facts up. Worded off the bridge's own handler --
# `ExecuteSkipCardReward` presses the screen's alternative button and hands the
# screen behind it back -- and it stops short of calling that button a plain
# skip, which is `EB-374`'s rule and `CARD_REWARD_ALTERNATIVE_NOTE`'s subject.
SKIPPED_CARD_REWARD = (
    "the card reward. No card is added to your deck. This does not leave the "
    "room: it presses the reward screen's alternative button and hands back "
    "the screen the reward came from, and `proceed` is the verb that leaves")

# `EB-393`, the decline half. A ROOM WITH NO WAY OUT BUT THROUGH.
#
# The same seat: "and no option to decline... I was forced to add *something*."
# `ExecuteProceed` walks rewards, rest, both merchants and the treasure room
# and never an event room (`EB-259`), and `_proceed_option` answers -1 where
# the screen prints no Proceed of its own -- so on such a screen the rows above
# are the whole of the grammar, and the page says so instead of leaving a
# reader hunting for the button.
EVENT_NO_DECLINE_NOTE = (
    "*This room prints no Proceed and this page has no verb that leaves one: "
    "the rows above are the whole of what this screen will take. If none of "
    "them is a decline, this room has none.*")

# `EB-349`. THE TURN SOMEBODY ELSE PLAYED, AND THE PAGE PRINTED NOTHING FOR IT.
#
# THE FIND (Kokomi r4d act 3). Whispering Earring -- "Vakuu plays your first
# turn for you" -- opened six fights, and five of them rendered as an empty
# hand with no card, no target and no result named: "Vakuu had spent my whole
# turn before I was shown anything." One of the six left 2 of 4 energy unspent
# and the seat could not tell that from a bug.
#
# THE LEDGER IS NOT ON THE WIRE. `BuildPlayerState` sends the piles, the hand
# and the board, and nothing anywhere sends a record of a card RESOLVING --
# there is no combat log on the feed, so the cards Vakuu played, what it aimed
# them at and what they did cannot be printed by this side at all. That half
# is the bridge's.
#
# WHAT THE PAGE HAS is the relic's own printed sentence, which is on every
# screen of the run (`EB-238`), and the round number. So it says the turn
# happened, names the relic that took it, and states the gap -- which is the
# difference between an empty hand that is a bug and an empty hand that is the
# price of a relic. Matched on the SENTENCE and not the relic's name: a second
# relic that does the same thing gets the same line.
AUTO_TURN_NOTE = (
    "*{relic} plays a turn of yours for you, and it has already played this "
    "one. What it played, what it aimed at and what each card did are not on "
    "this page's data feed -- there is no record of a card resolving on the "
    "wire at all -- so the board above is the state that turn LEFT and not a "
    "report of it. An empty hand or unspent energy here is that turn, not a "
    "fault.*")

# `EB-349`, the second half. A PER-HIT MODIFIER AGAINST A MULTI-HIT ICON.
#
# THE FIND (Kokomi r4d act 2, elite 4). "With `Tainted 4` the screen printed
# `6x3` = 18. I had 7 Block and Tungsten Rod, so 18 - 7 - 3 = 8 expected. I
# took 15." And the round after, the same debuff against a ONE-hit icon
# printed 12 = 8 + 4, "which is correct -- Tainted *is* folded into a one-hit
# intent". So the game's own icon folds a per-hit modifier into one figure and
# not into the other, and nothing on the feed says which of the two you are
# looking at.
#
# THE PAGE DOES THE ARITHMETIC IT CAN AND CLAIMS NEITHER READING. Both numbers
# are on this screen already -- the icon's `AxB` and the stack on the player's
# own status line, whose printed rule says "additional damage from Attacks",
# which `EB-359` established is per hit. The note nets the modifier per hit and
# prints both totals, because a reader who is shown 18 and takes 30 has been
# given the wrong number and a reader shown a range has been given the
# decision.
PER_HIT_NOTE = (
    "*You are carrying {name} {n}, and its own line says that is additional "
    "damage from each Attack hit. A part whose icon reads `{label}` is {hits} "
    "hits: {low} in all if the game's figure already counts your {name}, "
    "{high} if it does not. This page's feed carries no breakdown of an icon "
    "number, so it cannot say which of the two this is -- both have been "
    "seen, on one-hit and multi-hit parts of the same fight.*")

# `EB-408`. THE SAME CARD, THE SAME BUFF, TWO PRINTED NUMBERS.
#
# THE FIND (Kokomi r10 run 2 (c) 3). "Weak on me *was* folded into printed
# numbers (Oath showed 2, Slack Water 3). Sara's `Fantastic Voyage 5` was
# **not** folded in the first time -- fight 3 round 2 printed `Strike -- Deal 6
# damage` while the buff was up, and it hit for 11 -- but **was** folded in
# later (fight 4 round 3 printed `Deal 11 damage`, same buff, same card)."
#
# WHERE THE NUMBER COMES FROM, and it is `INTENT_SOURCE_NOTE`'s answer one side
# of the board over: a card's printed body is the game's own resolved
# `SmartDescription`, carried on the wire as `description` and printed here
# unchanged (`blindplay_faces._card_face`). There is no base anywhere on the
# feed, no modifier list and no second field -- so this page cannot fold a buff
# in, cannot unfold one, and cannot tell which of the two a given row is. The
# render is a pure function of the state it is given, so TWO OBSERVES OF ONE
# STATE cannot disagree; the two numbers the seat read came from two states,
# and the difference is the game's.
#
# SO WHAT IS OWED IS THE PROVENANCE, printed where a reader is about to price a
# hit off a row that may or may not already count the buff. Matched on the
# BUFF'S OWN SENTENCE rather than on its name -- `_PLAYS_YOUR_TURN`'s
# discipline -- so a second power worded the same way gets the same line and a
# renamed one does not go silent. `PER_HIT_NOTE` is the twin for a modifier
# that is per HIT and meets a multi-hit icon; this one is about the flat term
# on the player's own Attacks and the faces in front of them.
ATTACK_BUFF_NOTE = (
    "*You are carrying {name} {n}, and its own line says that is additional "
    "damage on your Attacks. The damage printed on each Attack above is the "
    "one figure the game's data feed sends for that card, printed here "
    "unchanged: this page has no base, no modifier list and no second source "
    "for it, and does no arithmetic on it. So a row may already count your "
    "{n} or may not, and this page cannot say which -- both have been seen "
    "under one live buff.*")
# `EB-605`. TWO NUMBERS FOR ONE BOMB IN ONE SENTENCE.
#
# THE FIND (Klee r22 lane 1 re-run (c) 2, fight 6 turn 4). "`Bomb 6 ... Bomb
# sizes here: 4`. Two numbers for one bomb in one sentence. I believe the 6 is
# the Vaporize-adjusted forecast against a Hydro aura, but I inferred that from
# a Spark counter, not from any printed word."
#
# WHAT THE TWO NUMBERS ARE, read off `ProtoBombPower`: the badge's headline is
# `DisplayAmount`, which is `PredictedSetOffDamage()` -- what setting the pile
# off would deal into THIS body right now, through everything standing on it --
# and `{Charges}` is the list of charge SIZES before any of that. The badge's
# own `mods.Clause` names two of the modifiers it folds in (Vulnerable, and a
# cap that clamps) and the REACTION multiplier is not among them, which is
# exactly the gap the seat fell into: 4 into a Hydro aura is a 1.5x Vaporize
# and prints as 6 with nothing saying so.
#
# THE PAGE DOES NOT DO THE ARITHMETIC AND CLAIMS NO NUMBER. Both figures are
# the game's and the page prints them unchanged, `INTENT_SOURCE_NOTE`'s rule.
# What it adds is which is which, and it adds it ONLY where they disagree --
# the row's own acceptance is that a lone Bomb 6 prints 6 everywhere on its
# line, and a badge that agrees with itself raises no question to answer.
BOMB_FORECAST_NOTE = (
    "*The {n} on this badge is what setting these off would deal into this "
    "body NOW, through everything standing on it; the sizes in its own "
    "sentence are the charges themselves, {total} between them. The gap is "
    "this body's and not the pile's.*")

#: `EB-605`, the half the seat had to infer from a Spark counter. Where the
#: body is wearing an aura the pile's own element reacts with, the reaction is
#: named -- off `REACTION_ELEMENTS`, the same table the glossary on this screen
#: is built from, so the two cannot say different things about one pair.
BOMB_REACTION_CLAUSE = (" It is wearing a {aura} aura, and {element} into "
                        "{aura} is {reaction}.")

# `EB-349`, the third half. A ONE-USE DISCOUNT PRICED ONTO EVERY ROW.
#
# THE FIND (Kokomi r4d). Pounce reads "Deal 14 damage. The next Skill you play
# costs 0", and while it is up EVERY Skill in hand prints the cut price -- the
# game's own "if played now" preview, right one card at a time and read as a
# hand-wide sale. `cost_note` explains the cut per card ("the cut is this
# turn's board and not the card") and says nothing about it being spendable
# once.
#
# READ OFF THE POWER'S OWN SENTENCE, the word `next` included, so a discount
# that really is hand-wide never takes this line.
ONE_USE_DISCOUNT_NOTE = (
    "*{power} pays for ONE card: its own words are \"the next {kind} you "
    "play\". Every {kind} above is showing the reduced price because the game "
    "prices each row as if it were the next one played -- only the first one "
    "you actually play is charged it, and the rest go back to their printed "
    "cost.*")

# `EB-669`. THE SAME SHAPE ON A RIDER THAT IS NOT A PRICE.
#
# Battle Plan's carry-out leaves "The next Attack you play face-up this turn
# deals 4 additional damage", and every Attack in hand redraws with the +4
# folded in -- the game's own "if played now" preview, right one card at a time
# and read as a hand-wide buff. BOTH r26 seats counted it twice before catching
# it. Lane 2: "both attacks printed the rider though only the first can consume
# it ... same over-display shape as the Battle Plan rider" (of Mika's cost cut,
# which is `ONE_USE_DISCOUNT_NOTE` above). Lane 1 put the pair side by side:
# "Kyouka's +4 shows on every Attack in hand and really does apply to every one,
# where Battle Plan's +4 shows on every Attack and applies to one."
#
# SO IT IS MIKA'S FOOTNOTE, GENERALISED, and it is read off the power's own
# sentence exactly as that one is -- the words "the next X you play", the
# `next` included, so a rider that really is hand-wide never takes this line.
# The two notes are separate strings because the thing being over-shown is
# different: a price goes back UP on the rest of the hand and a rider simply is
# not on them.
ONE_USE_RIDER_NOTE = (
    "*{power} pays for ONE card: its own words are \"the next {kind} you "
    "play\". Every {kind} above is showing it folded in because the game "
    "previews each row as if it were the next one played -- only the first "
    "one you actually play gets it, and the rest do what their printed "
    "numbers say without it.*")

# `EB-607`. WHERE THE INTENT NUMBER COMES FROM, WHICH IS THE ROW'S FIRST ASK.
#
# THE FIND (Klee r23 lane 1 (c) 3). "Fossil Stalker showed 'the number on its
# icon is 12' both before and after it gained Strength 3, while Corpse Slug's
# icon *did* move (3x2 to 7x2 at Strength 4). One of those two is telling me
# something the other is not; I planned my block around the higher number to
# be safe."
#
# THE READ, and it is one line: there is ONE source and it is the same one for
# every enemy. `BuildEnemyState` fills a part's `label` from
# `intent.GetIntentLabel(targets, creature)` -- the game's own call for the
# figure it draws on that icon, asked per creature per part
# (`McpMod.StateBuilder.cs:1541-1566`) -- and this page prints that string
# unchanged. There is no base anywhere on the feed, no modifier list, no
# second field a different enemy could be read from, and no arithmetic on this
# side. So the page cannot be the origin of the difference the seat saw, and it
# cannot resolve it either: both figures are the game's.
#
# WHAT THE PAGE OWES IS THEREFORE THE PROVENANCE, printed where a reader is
# about to plan a block against a number that may or may not have moved.
#
# `EB-779`'s companion find (proofs-9 lane 1, defect 2). The closing clause was
# written when it was true and `EB-607`'s bridge half made it false: the feed
# now carries `breakdown.base_damage`, `folded_damage`, `repeats`, `total` and
# the game's own `modifiers` list, and `_breakdown_clauses` prints them an inch
# above this paragraph. So the page said *"the game folded **Strength** into
# that: it is 12 on the move and 15 after"* and then, at the foot of the same
# section, *"the feed carries no base, no modifier list and no breakdown"*.
#
# TWO ENDINGS, ONE OPENING. The provenance half is unchanged and true on every
# board -- the figure is the game's and this page does no arithmetic on it --
# and only the sentence about what the feed carries moves, chosen off whether
# THIS board's breakdown actually arrived. A bridge older than `EB-607` sends
# none and reads exactly as it did.
_INTENT_SOURCE_HEAD = (
    "*An intent's number is the one figure the game draws on that icon, taken "
    "off the data feed and printed here unchanged: this page has no second "
    "source for it and does no arithmetic on it. An enemy carrying Strength "
    "whose figure does not move is the game's own figure not moving -- ")

INTENT_SOURCE_NOTE = (
    _INTENT_SOURCE_HEAD
    + "the feed carries no base, no modifier list and no breakdown, so "
      "nothing here can say which parts are inside a given number.*")

#: The same note where `EB-607`'s breakdown DID arrive on this board: the
#: parts are named above each intent, so the page stops denying it carries
#: them (`EB-779`, proofs-9 lane 1 defect 2).
INTENT_SOURCE_NOTE_BREAKDOWN = (
    _INTENT_SOURCE_HEAD
    + "and where the feed carries the game's own base, the figure its hooks "
      "arrived at and the models it folded in, the clauses printed beside "
      "that intent above name all three, so what is inside the number is "
      "read off the game rather than guessed at here.*")

#: `EB-607`, the fold. An icon figure and the hover sentence under it are two
#: numbers from two wire fields, and the page printed them side by side with
#: nothing said about the pair. Where they cannot be the same number, the line
#: says which is which instead of leaving a reader to pick one.
INTENT_NUMBER_DISAGREES = ("the icon's figure and this sentence's number are "
                           "two different fields of the feed and they do not "
                           "agree here; the icon is the figure the game draws")

PICKED_MARK = "PICKED"
# `EB-393`. "(Clone)" ON A TITLE READ AS A SECOND COPY. The enchant confirm
# listed two picked rows, one tagged `(Clone)`, and the Klee r10 seat read them
# as two cards; the deck held one. Clone is the game's own mark.
CLONE_NOTE = ("*A title ending in (Clone) is the game's mark for a card that "
              "can be duplicated at a Rest Site. It is one card, not a copy; "
              "a row above and its (Clone) row are the same card.*")

PENDING_PICK_NOTE = ("*Already listed above. These rows are the pick this "
                     "screen is holding, printed a second time so you can "
                     "read its face -- each is one of the cards in the list "
                     "above and not another copy of it, so counting both "
                     "lists counts it twice.*")

# `EB-329`, the morning log's own note. THE TWO NUMBERS UNDER A PLAN ARE NOT
# THE SAME QUANTITY and three seats spent three acts finding that out the hard
# way: the figure on the Plan's line is what its FIRST clause produced -- two
# stacks of Vulnerable for `Exposed Flank, 2` -- while the board moved 3 that
# beat, because the Tamakushi Casket answers a debuff with a Hydro strike and
# the Vulnerable it had just applied multiplied it. `Feint+, 19` agreed with
# the board only because a damage clause's landed number IS the damage. The
# note says which is which, once, under the block that prints both.
CARRY_OUT_BOARD_NOTE = (
    "*Under each Plan is the HP each enemy lost while that Plan resolved -- "
    "the whole beat, so anything the Plan set off is inside the number. The "
    "figure on the Plan's own line is what its first clause produced, which "
    "is a different quantity whenever that clause is not damage.*")
# `EB-360`. A SHOP THE FEED SENT NOTHING FOR.
EMPTY_SHELVES_NOTE = (
    "*The feed returned no shelves for this shop, so nothing is listed. This "
    "page cannot tell a sold-out shop from a shop the feed did not send; if "
    "the game shows wares, observe again, and say `proceed` to leave.*")

LAST_MORNING_NOTE = (
    "*The fight is over. This is the last thing the Bake-Kurage carried out "
    "in it -- printed here because a Plan whose kill ends a fight never "
    "reaches a battle screen.*")

# `EB-604`. THE SAME SENTENCE ONE ARM OVER, for the same screen and the same
# defect: a deliberate Evoke onto a full stage that KILLS ends the fight, and
# the beat the seat spent a turn building is the one beat of the run with no
# receipt. Furina r16 lane 2 Evoked twice on purpose, at 10 and 7 Encore, and
# "the bridge printed nothing about either because both were lethal"; r14
# lane 1's Second Course was the same turn a round earlier.
# `EB-299`. THE NOTE WAS WRONG IN BOTH DIRECTIONS AND THE r2 OPUS SEAT CAUGHT
# BOTH. It said *"Two cards here print the same name"* over a hand holding
# THREE Coral Guards, over a hand with two separate duplicate PAIRS, and over
# three Water's Edge beside two Slimed -- "It says 'Two cards' regardless."
# And it implied the page cannot tell the copies apart when `EB-177` had
# already numbered them: what the page cannot do is say which copy carries an
# ENCHANTMENT, because no field on the feed reports one. The same seat found
# the other half unprompted -- "the numbered suffixes renumber inside a turn",
# so `(1)` names a different card the moment the first one is played -- and
# that is a fact about the handle, which belongs beside it.
HAND_REPEAT_NOTE = ("*More than one card in this hand prints the same name. "
                    "The copies are numbered in the order they are listed, "
                    "and that number is a place in this list rather than "
                    "anything the card carries: it is re-counted on every "
                    "screen, so `(1)` names a different copy once one of them "
                    "leaves your hand. An enchantment prints beside the "
                    "title where a card carries one, so where two copies show "
                    "none and differ only by one, this page cannot say which "
                    "is which.*")

# `EB-496`. THE WARNING WAS UNDER THE WRONG LIST, AND IT WAS ALSO WRONG.
#
# WHAT THE SEAT DID (Klee r17 lane 1, turn 2 of the four-Gardener elite). It
# killed `Phantasmal Gardener (1)` with Pocket Fireworks and aimed Kaeya at
# `Phantasmal Gardener (2)`. "The list had already renumbered the moment the
# first one died, so my Kaeya hit what had been Gardener (3) ... I only found
# out by reading max-HP values off the next screen." It cost a 14-damage Melt,
# and the seat's own diagnosis names the page: the re-count warning is printed
# under `Your hand`, where it is about CARDS, and there was nothing at all
# under `The other side`.
#
# THE NUMBER NOW HOLDS, so the note says so rather than repeating the hand's
# caveat one list down. `_FIGHT_MEMORY` is on disk since this row, so a body
# keeps its number for the fight across the separate processes a seat's
# `observe` and `act` each run in -- which is why the seats went on watching
# it re-count long after `EB-271` and `EB-427` closed it for the in-process
# driver.
#
# AND THE LETTER IS THE HANDLE FOR THE OTHER HALF of what the seat asked for:
# "there is no way to name an enemy that survives a kill inside the same
# turn". A number only appears where a name repeats; a letter is on every
# body, is minted once and is never reused, so it is the one word that names
# the same creature on every screen of the fight.
# `EB-671`. WHAT THE MARK ON ONE OF THOSE LINES MEANS. The mark itself is
# `blindplay_board.mark_front`, whose header carries the r26 reading and the
# rule; this is the sentence under the list, printed once per screen with the
# handle note it belongs beside. It says what the mark IS -- the body a
# single-target aim lands on -- and the one thing that moves it, because a
# reader who cannot predict the move cannot use the mark.
FRONT_ENEMY_NOTE = (
    "*FRONT marks the body an aim with one target lands on: the first living "
    "enemy that is not a Minion, or the first living enemy of any kind when "
    "every body is a Minion. It moves when that body dies, and it is not the "
    "order this list happens to print in.*")

# `EB-674`. THE SECOND HALF OF THE VERB, ON THE SCREEN AND NOT IN A REFUSAL.
#
# Kokomi r26 lane 1, fight 5 turn 3: `use potion "Touch of Insanity"` opened a
# card chooser, `choose "Strike"` toggled the selection "but left the chooser
# open, and my next two commands were both refused ... The refusal listed
# `confirm`, and `confirm` worked. The chooser's own screen prints
# `choose "<card title>"` and does not print that a `confirm` follows; I
# learned that only from the refusal."
#
# NOT BY OFFERING THE VERB, which is `EB-259`'s rule and still binds: the
# commands list is what the WIRE says will work this instant, and `confirm`
# before a pick is a button that is not there. What the page owes is the
# SHAPE of the screen -- that a pick here is two commands and the screen stays
# up between them -- and that is a sentence, printed whether or not the button
# is live yet.
# ROUND THREE (Furina, the Stage), sec.4: AND SOMETIMES THE SECOND COMMAND IS
# `choose` AGAIN.
#
# "The Spend mode chooser needs `choose` twice: the first returns ok and the
# chooser stays open, the next commands are refused; about eight occurrences a
# run, two refusals spent on it." The seats were doing exactly what this note
# told them -- `choose`, then `confirm` -- and on the mode chooser the
# `confirm` was refused, so each pick cost two refusals and was then taken by
# saying `choose` a second time.
#
# WHAT THE PAGE MAY CLAIM. The two live reports disagree about ONE screen: the
# potion chooser `EB-674` was filed from took `confirm`, and the mode chooser
# this round was filed from took a second `choose`. Both arrive at the page as
# `card_select`, and the harness cannot open either to settle which press the
# bridge's `ExecuteSelectCard` lands
# (`vendor/STS2_MCP/McpMod.Actions.cs`, the `NChooseACardSelectionScreen`
# branch), so the page does not pick between them -- it names both ways out,
# which is what stops a refusal being the only teacher. The bridge half is a
# live look and is NOT in this row.
#
# `EB-779`, AND THE LIVE LOOK SETTLED IT, SO THE PAGE STOPS NAMING BOTH.
#
# proofs-9 lane 1 sec.9 opened `Curtain Rise`'s mode chooser and sent ONE
# `choose`: it came back ok, the next state carried no `card_select` at all
# and the enemy had taken the mode's damage. No `confirm` was sent and none
# was needed. So on `NChooseACardSelectionScreen` -- the wire's
# `screen_type: "choose"`, which `BuildChooseCardState` hardwires
# `can_confirm: false` on -- a pick is ONE command and the screen closes on
# it, and the three clauses above ("it does not close the screen", "say
# `confirm` after `choose`", "this chooser stays open") are all FALSE there.
# They were printed on it anyway, because the note was one constant on every
# chooser, and a seat reading top to bottom still spent the two refusals the
# row was opened on.
#
# SO THE NOTE IS SPLIT BY THE SCREEN THE WIRE NAMES, not by a guess: the card
# GRID choosers (`select`, `simple_select`, `upgrade`, `transform`,
# `enchant`) and the bundle picker take `choose` then `confirm` and keep the
# sentence they had, minus its now-pointless fallback clause; the mode
# chooser gets a sentence that is true of it and never says `confirm`.
# `chooser_note` below is the one place that choice is made.
CHOOSER_CONFIRM_NOTE = (
    "*Choosing here arms a pick; it does not close the screen. Say `confirm` "
    "after `choose` to take it, and until you do this chooser stays open and "
    "every other command is refused.*")

#: The mode chooser (`screen_type: "choose"`), where one `choose` resolves.
#: It never says `confirm`, because there is no confirm button on this screen
#: and saying the word costs a refusal (`EB-779`).
#:
#: 2026-09-25 (opus-furina-l2b, Fight 1 T2): AND IT SAYS THE SCREEN BLOCKS.
#: The seat chained `play` and `end turn` behind a Curtain Rise whose chooser
#: had opened, and both were refused ("a card chooser is open and has to be
#: answered first") -- two refusals in a row, one short of the stop. The note
#: said how to answer and never that nothing else would be taken until then.
CHOOSER_ONE_CHOICE_NOTE = (
    "*A chooser is open, and until you answer it every other command, "
    "`end turn` included, is refused. One `choose` takes your answer here and "
    "closes this screen: there is no confirm button on this chooser and no "
    "second command to say. Read the options before you choose -- the one you "
    "name resolves immediately.*")

#: 2026-09-25 (opus-furina-l2b, (c) 2). The heading of a chooser whose every
#: row is a MODE of the card just played. The bridge hardwires "Choose a
#: card." on this screen, and a mode chooser is not choosing a card.
MODE_CHOOSER_PROMPT = ("The card you just played asks which way to resolve. "
                       "Choose one:")

#: The wire's `screen_type` for the one-press chooser. `BuildChooseCardState`
#: writes it for `NChooseACardSelectionScreen` and nothing else.
ONE_PRESS_CHOOSER_KIND = "choose"


def chooser_note(select_kind: str | None) -> str:
    """The chooser sentence that is TRUE of this screen (`EB-779`).

    One argument, the wire's own `screen_type`, because that is the only field
    that tells the two choosers apart before a pick is made: `can_confirm` is
    false on a grid with nothing picked yet AND on the mode chooser always, so
    a split on the button's state would print the wrong sentence on the screen
    the row was filed against.
    """
    if str(select_kind or "").strip().lower() == ONE_PRESS_CHOOSER_KIND:
        return CHOOSER_ONE_CHOICE_NOTE
    return CHOOSER_CONFIRM_NOTE

# `EB-681`. EVERY REACTION IN A BEAT, BY NAME, IN ORDER.
#
# THE FIND (Kokomi r27). Lane 2, fight 4: Slack Water put Hydro on a body,
# Shinobu's Thundergrust hit it with Electro, and the panel showed Poison 8
# where the Electro-Charged rule prints 4. The eight was TWO procs -- the
# Tamakushi Casket answered the Weak with a 2 Hydro ping, which landed on the
# fresh Electro aura and reacted again -- and the seat reconstructed the whole
# beat from a doubled number: "I only trusted my reading because it reproduced
# four times." Lane 1, (c) 2, is the same hole from the other side: "Gorou+'s
# Crystallize did not visibly fire", with nothing anywhere to settle it.
#
# NO NUMBER ON THE ROW. What a reaction delivered is on the board already and
# on the panel; what no surface carried is that it HAPPENED, how many times,
# and off what. The heading says the window, because a log with no window
# reads as the fight's.
REACTIONS_HEADING = "## What reacted this turn"
REACTION_ROW = "- **{reaction}** on **{target}**, off {source}."
REACTION_ROW_NO_SOURCE = "- **{reaction}** on **{target}**."
#: Printed where the log is present and empty, which is a fact about the turn
#: and not a hole in the feed -- and it is the sentence that closes lane 1's
#: reading, since "no line" and "no reaction" were the same page.
NO_REACTION_THIS_TURN = ("- Nothing reacted this turn. A reaction that "
                         "happened would be listed here by name.")

# `EB-710`. THE HALF OF THE BEAT NOBODY WAS SHOWN.
#
# THE FIND. This heading said "Nothing reacted this turn" through a run where
# Electro-Charged fired six times off Shinobu's Ring -- at the END of the turn
# -- and Klee r26 read the header EMPTY on two Melts and an Overloaded off a
# played Set off. The log was cleared on the wrong window: it opens at the end
# of the ENEMY turn, so every reaction from the player's own end-of-turn
# tenants and from the whole enemy side was written and dropped with no player
# page in between. `KleeMod.Powers.ReactionLog.MarkTurnStart` now carries them.
#
# THEY CARRY ONE TURN, AND THEY SAY SO. A carried row prints under THIS
# heading, because it is the only receipt on the page and the alternative is
# the silence that was the defect; and it carries its own window on the line,
# because the heading names THIS turn and a row from before it would otherwise
# make the heading the second false thing on the screen. The wording is the
# Stage log's ("since you ended your last turn"), so the two receipts on this
# page name one boundary with one phrase.
REACTION_CARRIED_CLAUSE = " *(since you ended your last turn)*"
#: Printed above the rows where EVERY row is a carried one -- the honest
#: reading of a turn on which nothing has reacted YET and something reacted
#: while the reader was not being shown a page.
REACTION_CARRIED_ONLY = ("- Nothing has reacted yet this turn. These landed "
                         "after you ended your last turn:")

# `EB-695`. WHAT A RELIC ANSWERED WITH, ON THE PATH THAT HAD NO RECEIPT.
#
# THE FIND (Kokomi r30 lane 2, debrief 1). The Tamakushi Casket answers a
# debuff with a 2-damage Hydro strike from the jellyfish. Inside a PLAN
# carry-out it is named -- "Inside the same beat: Tamakushi Casket 2 on Damp
# Cultist", the clause `EB-453`/`EB-518` built -- because `KokomiPlan.NoteRider`
# is standing there to catch it. Play the same debuff card FROM HAND and the
# same strike lands with nothing naming it, and the seat subtracted it from HP
# by hand on every such play.
#
# THE ROW IS THE RIDER CLAUSE'S OWN SHAPE -- source, number, body -- because a
# reader meeting the two on different screens of one run is adding the same
# kind of thing, and two spellings of one fact is the defect this page has
# closed twice elsewhere.
#
# NO EMPTY LINE, unlike the reaction log beside it, and that is a difference
# rather than an inconsistency: the reaction section prints "nothing reacted"
# because a seat read the SILENCE as "may or may not have fired" (`EB-681`
# lane 1), and no such question exists here -- a relic that answered nothing
# answered nothing, and a page saying so on every screen of every run that
# holds no such relic is noise.
RELIC_ANSWERS_HEADING = "## What your relics answered with"
RELIC_ANSWER_ROW = "- **{source}** {amount} on **{target}**."
RELIC_ANSWER_ROW_NO_TARGET = "- **{source}** {amount}."

# `EB-708`. A SIZE IS NOT A STATUS, AND THE PAGE HAD NO LEGEND FOR EITHER.
#
# THE FIND (Kokomi r31 lane 2, (c)). `Twig Slime (M)` and `Leaf Slime (S)` read
# as MINION MARKERS against a Plan rule written in terms of Minion -- "the seat
# guessed whether a single-target Plan could hit them". The letters are part of
# the name the GAME prints (the slime family is drawn at three sizes) and this
# page passes a printed name through verbatim, so a reader meeting a bracketed
# letter on a screen that also prints `[A]` handles and two Minion rules has
# three bracketed things and a legend for one of them.
#
# IT SAYS WHERE MINION DOES LIVE, because the negative alone leaves the reader
# where it found them. `MinionPower` is a POWER on the body and this page
# prints every power a body wears under its intents, so the answer to "is this
# one a Minion" is on the same screen one line down -- which is `mark_front`'s
# own rule too, read off exactly those rows.
ENEMY_SIZE_NOTE = (
    "*A letter in round brackets inside an enemy's name is its SIZE -- `(S)` "
    "small, `(M)` medium, `(L)` large. It is part of the name the game prints: "
    "not a status, and not the `[A]` handle this page aims cards by. It does "
    "not make the body a Minion. Minion is a printed status, so a body that is "
    "one carries a `Minion` line of its own under its intents, and a body "
    "without that line is not one whatever size it is.*")

ENEMY_HANDLE_NOTE = (
    "*Each enemy keeps its letter and its number for the whole fight: a body "
    "that dies does not renumber or re-letter the ones still standing, and a "
    "summon takes the next free letter. Either handle aims a card -- "
    "`on \"B\"` is the same body as the full name beside it.*")

# `EB-672`. AND THE LINE THAT SAYS A LETTER RETIRED. Kokomi r26 lane 1, fight
# 7: Fogmog summoned a replacement Eye with Teeth "as B, at 6/6, with the same
# intent, on the screen right after I killed B. I spent an act testing whether
# my own Flank had whiffed. Nothing distinguished a replaced body from a
# survived one." The letter is now minted fresh (`_reborn_keys`); this is the
# sentence that tells the reader WHY the letter it was aiming at is gone,
# printed under the new body rather than in a footnote, because the question
# is asked about that one line.
ENEMY_REPLACED_LINE = (
    "    - This is a NEW body. It took the place of [{was}], which is dead; "
    "it is not the same creature and it carries none of [{was}]'s damage.")

# `EB-294`. AN AURA IS NOT A BUFF, AND THE FEED SAYS BUFF. `AuraPower.Type` is
# `PowerType.Buff` so that Artifact does not eat an elemental application
# ([USER] 2026-08-23), which is a rule about Artifact and reads on a page as a
# statement about who is being helped: `Hydro Aura 2 (buff)` sat beside
# `Vulnerable 1 (debuff)` and the r2 Opus seat read "the aura I put on them to
# set up a Reaction" as something helping the enemy. The tag is `(aura)` on
# the line, and this says once per screen what that third tag means.
# `EB-378`. WHOSE ELEMENT THE CARRY-OUT IS, on the panel that carries it out.
#
# `KokomiPlan.ResolveAll` deals every damaging Plan clause as
# `ElementalHit.Deal(..., Element.Hydro, ...)` -- and the sim's twin the same
# (`kokomi_plan`, `element="hydro"`) -- whatever the card's own type. So a
# SKILL's Plan leaves a Hydro aura, and the round-9 act-1 seat watched one
# appear "from a card whose face says nothing about an element" (run 2, act 1,
# finding 2). The card faces now declare it, and this is the same fact said
# where the hit actually happens: the jellyfish's own panel, which is the one
# section a reader is looking at when the morning resolves.
#
# ONE SENTENCE AND NO NUMBERS. The aura's duration and the reaction rule are
# the `Applies Hydro` keyword's and the reaction glossary's, both already on
# any screen showing an element; what is missing here is only whose hit it is.
# `EB-442`. THE AIM RULE, SAID WHERE THERE IS ROOM TO SAY IT.
#
# The `Plan` keyword carries the rule in 135 rendered characters -- "next
# turn: front non-Minion, or ALL, Minions too" -- which is AT the tip ceiling
# (`ArmKeywordTips.ForPlan`'s header does the arithmetic) and is all the room
# the mod has. The r12 seat read that clause about fifteen times and never got
# the rule out of it, while "the Bake-Kurage panel and the Reaction preview
# read clearly". The panel has no ceiling, so the compression is unnecessary
# here and the tip's clause stays exactly as it is, as the pointer.
#
# THE CORNER THE TIP HAD TO DROP IS HERE. `KokomiPlan.FrontEnemy` takes the
# leftmost hittable body that is not a Minion and FALLS BACK to the leftmost
# Minion when the board is Minions alone -- "a Plan that lands on nothing is
# worse than one that lands on the decoy". The tip's own header names that as
# the one corner it left unsaid; there is room for it here.
#
# TWO SENTENCES AND NOTHING ELSE. The modifier clause -- enemy Vulnerable
# counts, her Weak and Strength do not -- is the keyword's and stays there.
# This note is about WHERE a Plan lands, and a panel that restated the whole
# keyword would be the wall the seat was already reading past.
PLAN_AIM_NOTE = ("- A Plan with one target hits the front enemy and never a "
                 "Minion -- unless every enemy is a Minion, when it takes the "
                 "front one anyway. A Plan whose card says ALL hits every "
                 "living enemy, Minions included.")

# `EB-411`. THE PLATING THAT ATE A WHOLE PLAN.
#
# THE FIND (Kokomi r10 run 2 (c) 4, fight 4). "Whether to plan *at all* into a
# `Plating 8` enemy. This one was real and also the least fair, because the
# reason the answer is no -- the carry-out lands at the start of my turn,
# before I can strip block -- is nowhere on the card." The keyword's own clause
# says WHEN ("at the start of your next turn, before you draw") and nothing
# about what the hit meets when it gets there.
#
# THE ORDER IS THE ENGINE'S, and it is written down: the turn-start broadcast
# is `BeforeSideTurnStart`, BLOCK CLEAR, `AfterBlockCleared`, ENERGY RESET,
# HAND DRAW, `AfterPlayerTurnStart` (`ProtoBakeKuragePower`'s header, read off
# the decompile and pinned by `TURN_START_BROADCAST_ORDER`), and the morning
# resolves at the last of those. The block clear in that list is YOURS. An
# enemy's Block falls at ITS turn start, so whatever it raised on its own turn
# is still standing when the morning arrives -- and the morning arrives before
# the player has played a card, so there is no move that strips it first.
#
# ONE SENTENCE, ON THE PANEL, in the order the engine resolves. The `Plan`
# keyword is at its 135-character ceiling and cannot carry this
# (`PLAN_AIM_NOTE`'s argument, whole); the panel has no ceiling, and it is the
# screen every Plan is written from.
PLAN_BLOCK_NOTE = ("- A Plan is carried out before you play anything, so it "
                   "lands in whatever Block the enemy is still standing in "
                   "from its own turn -- you cannot strip that Block first.")

PLAN_HYDRO_NOTE = ("- Every planned HIT is the jellyfish's, and it is a Hydro "
                   "hit: it leaves a Hydro aura, or reacts with the aura "
                   "already there. A Plan that only blocks or draws leaves no "
                   "aura.")

# `EB-433`. THE CLAUSE THAT WAS FALSE WITH THE STARTER RELIC ON.
#
# THE FIND (Kokomi r11 run 2 (c)). The panel printed "A Plan that blocks, draws
# or applies a debuff leaves no aura", and Slack Water's debuff Plan left Hydro
# Aura 1 on all three enemies. The clause was right about the PLAN and wrong
# about the board, and nothing on the page closed the gap.
#
# WHY IT HAPPENS, in the relic's own words: the Tamakushi Casket reads
# "Whenever you apply a debuff to an enemy, it deals 2 Hydro damage to that
# enemy", and that strike is a REAL hit through the same `ElementalHit` funnel
# every other non-attack hit in this mod uses -- its own header says so, and
# lists the aura and the reaction among what it therefore applies. So a debuff
# Plan lays Hydro through the relic rather than through the Plan, which is
# exactly the distinction a reader cannot make from a board.
#
# A CLAUSE AND NOT A ROW, appended to the sentence it is the exception to: the
# aura rule is one fact and printing a second bullet contradicting the first is
# how the panel becomes the wall `PLAN_AIM_NOTE` refuses to build.
#
# GATED ON THE RELIC BEING HELD, and matched on its SENTENCE rather than its
# name -- `_PLAYS_YOUR_TURN`'s discipline -- so a run that never had it reads
# the true short rule, and a second relic that answers a debuff with an
# elemental hit gets the same clause.
PLAN_CASKET_AURA_CLAUSE = (
    " A Plan that applies a DEBUFF leaves one anyway while you hold "
    "{relic}: its answering strike is itself a Hydro hit.")

# `EB-563` / `EB-330` / `EB-357`. THE COUNT WAS READ AS A CAPACITY. The buff
# prints `Plan 1`, the box says "the Plan", and three seats wrote one Plan at
# a time for fights on end (one for four fights) before trying two; nothing in
# `KokomiPlan.cs` caps the queue. Said on the panel, beside the two rules a
# Plan is already read against.
#
# `EB-648`. AND THEN "ITS BUFF" NAMED THE WRONG BUFF. The r23 cap seat read
# this sentence against the buff the jellyfish itself carries -- and
# `ProtoBakeKuragePower` is a PRESENCE marker, a 1 that never moves for the
# whole fight -- so the note that exists to say the number is not a limit was
# read as "the counter is stuck at 1". Two badges are on that board and only
# one of them counts: `PendingPlansPower`, whose title is `Plan` and whose
# stack type is a Counter. So the note names it by that title, and says in one
# clause what the other 1 is, because a reader who has already found the wrong
# badge needs it ruled out rather than left unmentioned.
PLAN_COUNT_NOTE = ("- The jellyfish holds any number of Plans and carries them "
                   "out in the order written; the number on the **Plan** "
                   "badge is how many are written, not a limit. The "
                   "Bake-Kurage's own 1 is only its presence.")

# `EB-653`. AND THE SENTENCE ABOVE IS FALSE UNDER THE CAP LANE.
#
# WHAT THE r24 SEAT MET. With `GITS_KOKOMI_PLAN_CAP=2` the jellyfish carried
# out two of four written Plans, four mornings running, while this panel
# printed "not a limit". The seat: "either the cap is real and the panel's
# sentence is false, or the panel is right and the carry-out is dropping
# Plans." The cap was real. A rule read against a false sentence is not a read
# of the rule, and three of the four occurrences were read as a WALL.
#
# READ OFF THE WIRE, NOT ASSERTED. The page cannot know a lane's environment,
# and it does not have to: `ProtoBakeKuragePower`'s own description carries
# `KokomiPlan.CapSentence` when a cap is declared, and the description reaches
# `you["powers"]` like every other power's text. So the panel prints the note
# THE BUILD SUPPORTS -- `PLAN_COUNT_NOTE` where the wire says nothing about a
# cap, this one where it does -- and no third place spells the rule.
#
# WHAT SURVIVES EITHER WAY: "the number on the **Plan** badge is how many are
# written" is true under both rules and is what `EB-563` / `EB-648` put here.
# What goes under a cap is "not a limit", which is the clause the cap makes
# false, and what arrives is the cap's own second half.
# `EB-650`, R266 (2026-09-07): "a turn" became "at the start of your turn",
# because a Dusk carry-out is not capped and the old wording claimed it was.
PLAN_COUNT_CAPPED_NOTE = ("- The jellyfish carries out at most {n} Plans at "
                          "the start of your turn; the rest wait in order. "
                          "The number on the **Plan** badge is how many are "
                          "written. The Bake-Kurage's own 1 is only its "
                          "presence.")

# `EB-647`. THE WRITTEN NUMBER IS THE NUMBER, AND NOTHING SAID SO.
#
# WHAT THREE r23 LANES MET. Under Shrink the hand reprinted `Kurage's Oath` as
# 2 and the jellyfish carried it out for 7. That is the ruled behaviour and not
# a defect: a Plan folds HER terms at WRITING time (`kokomi_plan.hers` -- her
# Strength and her enchantment) and nothing of the target's, because a Plan
# resolves next morning against whatever the board wears then. A debuff that
# lands on Kokomi after the Plan is written therefore does not follow it. No
# surface printed the rule, so each lane derived it from an arithmetic that
# looked broken.
#
# BESIDE `PLAN_COUNT_NOTE`, and the C# half is on the `Plan` badge
# (`KokomiPlan.PendingPlansPower`): the `Plan` keyword tip is at its
# 135-character ceiling and cannot carry a word more.
#
# `EB-688`. AND "AFTERWARDS" WAS THE HALF THAT WAS NOT THE RULE. Both r27 and
# r28 wrote a Plan while ALREADY debuffed and were paid in full -- Riptide 13
# under Weak, Kurage's Oath 7 under Shrink -- so a seat holding this sentence
# had to guess: "Either 'a hit you land' excludes the jellyfish's hit ... or
# Plans are simply immune. The rules text does not say which, and the
# difference matters" (r28 lane 1, (c) 2).
#
# IT IS THE FIRST, and the panel already says the fact it turns on one line
# up: `PLAN_HYDRO_NOTE`'s "Every planned HIT is the jellyfish's". A debuff
# that cuts YOUR damage is not on the body that throws a planned hit, whenever
# it landed -- and the mirror is `EB-659`'s finding, that a planned BLOCK is
# yours and Frail does cut it. Two clauses, one rule, both predictable from
# the sentence.
PLAN_WRITTEN_NUMBER_NOTE = ("- A Plan carries the numbers you wrote. Every "
                            "planned HIT is the jellyfish's, so Shrink or Weak "
                            "on you never cuts it, before or after you write "
                            "it; a planned BLOCK is yours, so Frail does cut "
                            "it.")

# `EB-752`. THE RELIC TERM NO DAMAGE FACE CAN FOLD.
#
# THE FIND (Klee r27, lanes 2 and cook, fight 2 each). "Ka-pow! printed Deal 4
# while The Boot made it 5", and on a Weak turn the printed numbers
# under-counted in the direction that makes a seat UNDER-play.
#
# WHY IT IS A CLAUSE AND NOT A FOLD, which is `EB-328`'s finding and the
# reason this row was re-scoped: The Boot is a `ModifyHpLostAfterOstyLate`
# hook. It runs AFTER the target's Block has been taken out of the hit, so it
# is not a damage modifier at all -- it is an HP-loss modifier, and a card in
# hand has no target, no Block and no honest way to carry its number. The
# game's own figure stays the game's, and the modifier is printed beside it.
#
# "ON AN UNBLOCKED HIT" IS SAID EVERY TIME, because it is the half a reader
# cannot see: a hit that lands into Block gains nothing, and a flat `+1` on
# the face would be wrong on every such hit.
UNBLOCKED_RAISE_CLAUSE = " (+{n} {relic} on an unblocked hit)"

# The same clause for a relic whose sentence does not spell its numbers: the
# page names it and says where its rule runs, and does no arithmetic it cannot
# source off the feed.
UNBLOCKED_RAISER_CLAUSE = (
    " ({relic} can raise this on an unblocked hit; its rule runs after Block "
    "and is not in the number above)")

# `EB-773`. THE PLAN WRITTEN AT A BODY THE QUEUE WILL ALREADY HAVE KILLED.
#
# THE FIND (Kokomi r32 lane 1, read again in PR #554). "The two carry-outs
# both landed on Leaf Slime (S) -- 8 killed it down to 3, the second 8 killed
# it with 5 wasted. They did not retarget." The retarget half was wrong -- the
# aim is re-read per entry and the body was still alive when the second
# arrived -- and the seat's own next sentence is the true complaint: "nothing
# on the Plan screen warns you". The waste is ordinary overkill, and the
# screen a player writes a Plan from said nothing about it.
#
# THE ARITHMETIC IS THE BOARD'S AND NOT A FORECAST. Every figure in it is
# already on this page: the written numbers, fixed by the note above; the
# body's HP; and the Block it is standing in, which `PLAN_BLOCK_NOTE` says
# survives to the morning. Nothing here predicts a roll, reads an intent or
# re-aims anything.
#
# "MAY", DELIBERATELY, and it is the honest word rather than a hedge: a Plan
# ahead of this one can be hurried out early by Change of Plans, a reaction or
# a relic can move the bar first, and a Dusk entry lands a turn sooner. The
# page names the reason and leaves the decision where it belongs.
#
# ON THE ENTRY'S OWN ROW, because the reader deciding whether to write another
# Plan is reading the queue, and the fact is about THIS entry rather than
# about the jellyfish.
PLAN_PAST_LETHAL_CLAUSE = (
    " — target may be dead by then: {target} has {hp} HP{block}, and the "
    "{queued} already queued ahead of this one covers it")

# The Block half of the clause above, printed only where the body has some: a
# bare "12 queued ahead covers 11 HP" is a false sentence about a body standing
# in 6 Block, and the subtraction is the one a seat would otherwise do by hand
# off `PLAN_BLOCK_NOTE`.
PLAN_PAST_LETHAL_BLOCK = " behind {block} Block"


AURA_NOTE = ("*An aura is tagged `(aura)` rather than `(buff)` or "
             "`(debuff)`, because it is neither: it is the element left "
             "clinging to a body, and it is what an Elemental Reaction needs "
             "-- a hit of a different element consumes it and reacts.*")


# `EB-461`. THE PAGE PROMISED A NUMBER AND THE ENEMY NEVER DEALT IT.
#
# WHAT THE SEATS SAW. "Every enemy turn where the intent listed an attack
# number AND a second intent, the attack did not land. I planned two turns of
# blocking around numbers that were never going to arrive" -- Kokomi r14 (c),
# four for four across the Living Fog, a Gremlin Merc and a Terror Eel, with
# Klee r14's Sludge Spinner the same shape.
#
# WHAT THE WIRE CARRIES, which decides which of the row's two options is
# buildable at all. `BuildEnemyState` reads `monster.NextMove` and walks
# `moveState.Intents`, sending one entry per intent with `type`, `label`,
# `title` and `description` and NOTHING ELSE -- no order of resolution, no
# condition, no likelihood, no marker of any kind separating a part that will
# fire from a part that will not. So "print only the move the enemy will take"
# is not something this side of the line can do: the feed does not know. The
# other half of the row's next action is what is left, and it is the honest
# one -- the page stops calling a multi-part telegraph's number damage that is
# coming.
#
# WHY EVERY PART STILL PRINTS. `EB-342` put them all there and its finding
# stands: the seat shown only the first row of a two-row telegraph opened the
# next round with four `Burn`s in hand. Dropping a part would be that defect
# again. What changes is the CLAIM the page makes about the number, not how
# many parts it shows.
#
# REOPENED 2026-09-04, AND THE FIRST WORDING WAS ITSELF A CLAIM. "Has
# repeatedly not landed" and "MAY perform" are a FREQUENCY reading of four
# turns, and the page has no standing to make one: both r15 seats read the
# label as a warning and stopped blocking against five telegraphs that then
# landed in full -- the same defect the row opened on, pointed the other way.
# So the note and the label say only what the feed supports: there are several
# parts, and the feed does not say which resolve. No history, no likelihood,
# no advice. The fact the page is missing is a RESOLVING-PART MARKER on the
# wire, and that is asked for in
# `docs/current/operations/understudy-seats.md` rather than guessed at here.
MULTI_INTENT_NOTE = (
    "*An enemy showing more than one intent is telegraphing every part of one "
    "move, and this page's data feed carries nothing that says which of those "
    "parts resolve, in what order, or on what condition. Every part the feed "
    "sends is printed above, exactly as it was sent; this page makes no claim "
    "about which of them the enemy will perform.*")

# `EB-474`. THE BLOCK ON THE BODY, AND THE PART THAT WILL ADD MORE.
#
# WHAT THE SEAT SAW. "Nibbit at 5 HP, I played a card printing *Deal 6
# damage*, and it lived at 4. Nothing on the combat page showed the Block that
# ate the other 5. That is the only outright unpredictable outcome of the run"
# (Furina r9 (c) 1) -- and its own reading of it was "Block from the Defend
# half of its previous multi-part telegraph".
#
# WHAT THE PAGE ALREADY DID, and it matters for what is left to build. The
# enemy line has printed `, Block N` beside HP since `EB-180`, off the wire's
# own `battle.enemies[].block`, which `BuildEnemyState` fills from
# `creature.Block`. That half of the row was standing; it is now PINNED rather
# than assumed, because nothing held it.
#
# WHAT WAS MISSING. The TELEGRAPH said nothing. `BuildEnemyState` sends a
# `Defend` part with an empty `label` and, on every capture in `review/qa`, no
# description at all, so the line read `Defensive (Defend)` -- a word with no
# consequence attached, one row above the number it was about to change. A
# reader who is shown Block only once it exists learns about it a turn late.
DEFEND_INTENT_CLAUSE = ("this part adds Block to the Block on its line above, "
                        "and the feed carries no number for how much")

#: What a number on a multi-part telegraph is called ON THE LINE ITSELF, so a
#: reader who plans off the enemy block without reaching the note under it
#: knows the number belongs to one part of a several-part move. It says what
#: the number IS and nothing about how often such a part has landed.
MULTI_INTENT_LABEL = ", one part of this move"

# `EB-323`. THE BUFF THAT NAMED NOBODY.
#
# WHAT THE SEAT SAW (Klee r7). `Empower (Buff)` -- a heading, a bracketed kind,
# no number and no target -- on a board of three bodies. A part that hits the
# player and a part that strengthens the enemy's own side read as the same
# line, and the seat could not tell whether to block for it.
#
# THE TARGET IS NOT ON THE WIRE, and that half is the bridge's:
# `BuildEnemyState` sends an intent part as `type`, `label`, `title` and
# `description` and nothing else (`McpMod.StateBuilder.cs:1541-1566`) --
# `IntentModel` has the target and the serializer never asks for it. So the
# page may not name the body.
#
# WHAT IT MAY SAY is the side, which is the wire's own `type`: a `Buff` part is
# the enemy's side gaining something, so it is not damage arriving at the
# reader. The clause states that and states the gap, in `DEFEND_INTENT_CLAUSE`'s
# shape one part-kind over -- a consequence attached to a word that had none.
BUFF_INTENT_CLAUSE = ("this part strengthens the enemy's own side rather than "
                      "hitting you, and the feed carries no target for an "
                      "intent part, so this page cannot say which body it "
                      "lands on")

# `EB-323`, the other half. WHERE THE PAGE IS, IN THE NUMBER THE RUN COUNTS IN.
#
# The map named a room by its room type and a path number, the bridge's own
# answer to `go` names a grid coordinate (`ok Traveling to Ancient at (3,0)`),
# and the only screen of the run that ever said `floor` was the run-over page.
# Three vocabularies for one position, and a seat planning a run against
# "eight floors of act 1" had none of them to count in.
#
# `run.floor` IS THE RUN'S OWN NUMBER, the same field the game-over page reads
# (`EB-333`), and a map option is one floor up -- which is not a guess: it is
# the same reading `_map_ahead` numbers its whole lookahead from. Absent from
# a feed that sends no floor, rather than a `0` this page cannot stand behind.
MAP_FLOOR_LINE = ("You are on floor {here}{act}; the rooms above are floor "
                  "{next}. This is the run's own floor number -- the one the "
                  "run-over page counts in, not a grid coordinate.")


# `EB-272`. THE ARMS' OWN WORDS, DEFINED ONCE PER SCREEN.
#
# THE GAP. Every keyword a SHIPPED face prints has somewhere a player can read
# it -- `Block` and `Exhaust` are the base game's, `Applies Pyro` and the eight
# reaction previews are `KleeKeywords`' -- and the words the two live prototype
# arms invented had nothing at all. Both Kokomi seats in round one worked out
# what a rule did by watching their own HP; the Casket's `Mend` read as BROKEN
# at full HP because the entry-HP bound is real and was printed nowhere; the r4
# Opus seat lost a deliberate free kill because a Mine's damage is shrunk by
# Weak and no line said so.
#
# WHERE THESE SENTENCES COME FROM, AND WHY THEY ARE COPIED RATHER THAN READ.
# They are `klee-mod/KleeCode/Cards/Prototype/ArmKeywordTips.cs`'s bodies, with
# the game's `[gold]` markup and the interpolated balance constants folded out
# -- the mod's own tooltip text, which is what a player hovering the card in
# the real game reads. They are copied HERE because the wire only ever defines
# a word on the card that DECLARES it: `Kaboom!` prints *Set off* in its own
# body while the tip rides on the rows that place a Bomb, an enemy's badge and
# a reward row print the word with no tip at all, and this page is read by
# somebody who met the word for the first time three lines up. A page-side
# table answers all of those; a per-card tip answers one.
# `test_the_arm_keyword_glossary_is_the_mods_own_tooltip_text` reads the C# and
# fails the moment a sentence here falls behind it -- the same way
# `CHARGE_SOURCE_LINE` is held in step from the other side.
#
# THE LIVE ARMS ONLY. Klee's overhaul (Bomb, Set off, Spark, Mine) and Kokomi's
# (Plan, Mend). `Tide`, `Surge` and `Exert` left with the rules they named when
# R240/R241 replaced the Tide with the Plan, and a page defining a dead word
# would be teaching a tester a rule this build does not have.
#
# `EB-340`: the `Bomb` row carries `{growth}`, filled by `keyword_notes` from
# the screen's own tip where the screen has one and from `BOMB_GROWTH`
# otherwise. It is the ONE row with a hole in it, and the hole is a number the
# card face already prints.
#: `EB-744`. THE REWARD SLOT, in the mod's own words -- and they are the mod's
#: own NEW words. "Card rewards after a fight offer a fourth, Companion,
#: choice" is `EB-620`'s 5 percent roll stated as a rule, on this page and on
#: the Mods screen (`klee-mod/Klee/manifest.json`) alike, so a seat pricing a
#: run around a fourth slot it will meet once in twenty fights was told
#: something false by the two surfaces whose job is the opposite. Quoted
#: verbatim from the manifest and pinned to it, `EB-329`'s rule unchanged.
COMPANION_SLOT_SENTENCE = (
    "About one card reward in twenty offers a fourth, Companion, choice.")

#: 2026-09-25. What a Companion IS, word for word the in-game tip
#: (`ArmKeywordTips.ForCompanion`).
COMPANION_DEFINITION = ("A card titled with a character's name, a dash, then "
                        "its own.")

#: `EB-744`. WHAT AN ACT IS, in one sentence, shared by the two seat rows.
#:
#: Rule 10: each performer performs a FLAT act at the end of her turn, from any
#: seat, and the act does not read the bar. Round two found that the reserve
#: performs and that nothing printed said so, and that "the three read as three
#: at the exit and one at the table, because every card speaks in seats and the
#: acts are not documented". The numerals are `FurinaStageLaw`'s, written out
#: for `ARM_KEYWORDS`' standing reason: this page has no access to the mod's
#: constants and a seat needs the number rather than the name of the constant.
def _summon_row(hay: str) -> str:
    """The Summon row. ONE variant since the trio can be cloned (2026-09-25;
    [USER]: "Let's allow for copies and then check the balance."): named and
    random summons meet a full stage the same way, as the tip says once."""
    return ARM_KEYWORDS["Summon"]


#: 2026-09-25 (opus-furina-l2b, (c) 3): the SEAT COUNT, in step with The
#: Stage badge (`StageSummaryPower`), which now opens "Up to 3 performers act
#: at the end of your turn" off `FurinaStageLaw.Seats`. The seat never dared a
#: third summon because nothing printed how many seats there are.
#: Draft 3 (2026-09-25): no act applies Hydro, so the act list is plain
#: damage.
STAGE_ACTS = ("Up to 3 performers act at the end of your turn, from any "
              "seat: Usher gives you 3 Block, Chevalmarin deals 2 to every "
              "enemy, Crabaletta deals 5 damage to a random enemy.")

ARM_KEYWORDS: dict[str, str] = {
    # TEXT PASS 2026-09-25, in step with `ArmKeywordTips.ForBomb` and
    # `ForSetOff`: the tips were rewritten short ("the existing text is often
    # very verbose and unintuitive", the owner) and these rows follow them
    # word for word, markup and interpolation folded out. The growth is
    # `{growth}`, filled from the screen's own tip (`_BOMB_GROWTH_RE`). The
    # long history of both rows is in git.
    "Bomb": ("Deals its size in Pyro damage when Set off. Grows {growth} at "
             "the start of your turn. If its enemy dies, it jumps to "
             "another."),
    "Set off": ("Every Bomb on the enemy goes off, oldest first. A random Set "
                "off picks an enemy with Bombs."),
    "Spark": ("Some cards cost Sparks instead of Energy, with no cap. Gone "
              "after combat."),
    # Text pass 2026-09-25, in step with `ArmKeywordTips.ForMine`.
    "Mine": "A Bomb that also goes off just before its enemy attacks.",
    # THE 2026-09-25 TEXT PASS rewrote the word to two short sentences, in
    # step with `ArmKeywordTips.ForPlan` word for word: the old row carried
    # six seats' edge cases (the aim and its Minion exception, Strength
    # folding, Vulnerable timing, "a carry-out is not a hit", standing Block,
    # the badge as a count) in 292 characters. The panel keeps the long form
    # of the ones a board needs -- `PLAN_AIM_NOTE`, `PLAN_BLOCK_NOTE`,
    # `PLAN_COUNT_NOTE`, `PLAN_WRITTEN_NUMBER_NOTE` -- because the panel has
    # no ceiling; the history of each clause is in git.
    "Plan": ("Play the card on the Bake-Kurage and this happens at the start "
             "of your next turn. Plans are carried out in the order you made "
             "them."),
    # `EB-643` (R265). THE POOL PASS'S ONE NEW WORD, and it is a rule about
    # WHEN and nothing else: everything else about a Dusk Plan is a Plan, and
    # the row above says all of it. What a reader cannot get from anywhere else
    # is that the Block arrives in time for the swing. Same sentence as
    # `ArmKeywordTips.ForDusk`.
    "Dusk": ("Dusk: the Bake-Kurage carries this Plan out at the end of this "
             "turn, before enemies act."),
    "Mend": ("Mend N: heal N HP, never above the HP you entered the fight "
             "with."),
    # `EB-625`. THE RELIC A FACE IS WRITTEN AGAINST. Shell Guard says
    # "whenever the Tamakushi Casket strikes" and nothing on the page said
    # what the Casket is or what makes it strike -- [USER]'s act-1 run read
    # the card and could not tell. The mod's twin is
    # `ArmKeywordTips.ForCasket`; this is the same sentence, from the relic's
    # own face, with the number off the shared constant.
    # `EB-348` WIDENED IT TO THE RULE THE PING ACTUALLY HAS. "Deals N Hydro
    # damage" reads as a number arriving, and the r4d seat priced it that way
    # in all three acts -- act 3 finding 2 is the sharpest: a Casket ping
    # Vaporized the player's OWN standing Pyro aura for 2 x 1.5 x 1.5, and Red
    # Mask's combat-start Weak fired the relic on all three enemies at once.
    # The ping goes out through the same `ElementalHit` funnel every other
    # non-attack hit in this mod does, so it reacts, it takes the target's
    # Vulnerable, and it leaves Hydro behind.
    "Tamakushi Casket": (
        f"Your relic. Each debuff you apply is a {CASKET_STRIKE} Hydro hit on "
        f"that enemy: it reacts, takes its Vulnerable, and re-arms Hydro."),
    # `EB-377` ADDED `Swirl`, printed as a VERB by ten Universals, beside
    # `Hexerei` -- which R276 pick 2 retired: the Spark and Klee's three
    # readers read any Companion play now, so the word and its row left the
    # page with the tip (`ArmKeywordTips`).
    "Swirl": ("The enemy's aura is consumed and copied onto ALL enemies. No "
              "aura, no effect."),
    # `EB-372`. THE WORD REACHED A SEAT THAT HAD NEVER DRAFTED IT. `Grounded`
    # is a Power card of Klee's, and Kaeya's Cold-Blooded Strike is written
    # against it by name ("Next turn, Grounded pays even if you played a
    # Set off card", `EB-749`), as is the Cold-Blooded buff it leaves behind. The r9 seat
    # met the word in both acts, held neither the Power nor a screen that
    # defined it, and read it as noise. Held in step with
    # `ArmKeywordTips.ForGrounded`.
    # `EB-516` moved the condition to the board and the tip moved with it;
    # `EB-749` (R271 sec.5.1) moved it again, onto the CARDS the player played.
    # Kaeya's clause above is stale as a result and is left standing by that
    # ruling's scope -- it rules Klee's face and not the companion row.
    "Grounded": ("A Power that pays at the start of your turn, but only if "
                 "you played no Set off card last turn. Its card prints what "
                 "it pays."),
    # `EB-446`. THE NAME ONE CARD IS WRITTEN AGAINST AND ANOTHER GRANTS.
    # `Fischl -- Nightrider` prints "If Oz is out, he deals 5 Electro damage"
    # and cannot put him out: the Power that does is a DIFFERENT companion
    # card the r7 run never held. The seat played Nightrider five times and
    # never learned what the word meant. Held in step with
    # `ArmKeywordTips.ForOz`.
    "Oz": ("Fischl's raven, out while you hold the Power Oz, at Your Side. "
           "He makes an Electro hit at the end of your turn while he is "
           "out."),
    # FURINA, THE STAGE (`EB-723`, R269). The reframe's three -- Deploy, Evoke
    # and Drain -- left this table with the eleven `proto_fr_` rows that
    # printed them: R213 B's deletion rule took the rows off the surface, and a
    # glossary row for a word no card prints is a rule nobody can meet. What
    # replaced them is the SEVEN the brief's sec.12 names, in the same words
    # `ArmKeywordTips.ForSpend` and its six neighbours print, with the numerals
    # the C# interpolates from `FurinaStageLaw` written out: this page has no
    # access to the mod's constants, and a seat reading it needs the number
    # rather than the name of the constant that holds it.
    #
    # EACH ROW CARRIES THE HALF A PLAYER CANNOT INFER, which is what the whole
    # table is for. `Spend` carries "fires in full even if the bar is short",
    # because a rider that pays one point for the full number is the entire
    # Expend deck (brief sec.4). `Fanfare` carries the damage ORDER, because
    # that is the reason a bar matters at all. `Bow` says what triggers one:
    # since 2026-09-25 (rule 7) every performer at 0 Fanfare bows, whatever
    # emptied it.
    # `EB-746`: the word names a MODE now, not a rider. The page adds the
    # sentence the 135-character tip has no room for, which is what the
    # choose-a-card screen shows a player and a blind seat has to be told: a
    # Spend the back performer cannot pay is not offered.
    # R276 picks 1 and 2: the BACK performer pays, in full or not at all. The
    # "it Bows" clause left with rule 7's 2026-09-25 change: the Bow row
    # covers every way of reaching 0.
    # THE TEXT PASS (2026-09-25, review/records/furina-text-pass-2026-09-25.md):
    # the glossary follows the tooltips word for word. The Spend row's old
    # page-only sentence ("not offered at all") is the tip's own clause now.
    "Spend": ("Pay Fanfare from your back performer. Offered only if it can "
              "pay in full."),
    # The follow-up: the empty-stage summon rides the Fanfare row, which
    # every Fanfare-giving face prints.
    "Fanfare": ("A performer's health. Hits take your Block, then the front "
                "performer's, then you. Gained on an empty stage, it summons "
                "a performer."),
    # `EB-744`, and rule 7 as changed 2026-09-25: a performer at 0 Fanfare
    # Bows whatever emptied it -- a Spend, a hit or a full-stage summon.
    # Draft 3 (2026-09-25): the Bow is the performer's act once more.
    # 2026-09-25 evening, [USER]: "I think it would be better to have the
    # performer bow immediately (during the opponent's turn) instead of at
    # the start of your turn." The waiting Bow is gone.
    # THE GUEST CAST (2026-09-25): a guest's act may pay, and its Bow does
    # not -- stated once, here, for every performer.
    "Bow": ("A performer that leaves the stage acts one last time on its "
            "way out, without paying."),
    # `EB-744`. AND NOTHING SAID WHAT AN ACT IS. The acts go on BOTH seat rows
    # because a seat may meet either word alone -- the page's one addendum to
    # the tip, `STAGE_ACTS`, which also carries the seat count (the
    # opus-furina-l2b seat's (c) 3).
    "front performer": ("Takes hits first. Regains 1 Fanfare at the start of "
                        "your turn. " + STAGE_ACTS),
    # `EB-744` and round four: the back is reached LAST, per attack.
    # Draft 3 (2026-09-25): rule 12, the fade.
    "back performer": ("Gains and Spends Fanfare. Hits reach it last. At the "
                       "end of your turn, it loses half its Fanfare above 5. "
                       + STAGE_ACTS),
    # R276 batch two: Arkhe Alignment's two halves, in
    # `ArmKeywordTips.ForOusia` / `ForPneuma`'s words.
    "Ousia": "This turn, your performers' acts deal double damage.",
    "Pneuma": ("This turn, your performers' acts give double Block, and your "
               "front performer gains 2 Fanfare."),
    # 2026-09-25. WHAT A SUMMON DOES, AND WHAT EACH PERFORMER DOES. A
    # first-time co-op player "found it very hard to understand what was
    # going on from the tooltips, such as what each summoned actor actually
    # did". `ArmKeywordTips.ForSummon`, `ForUsher`, `ForChevalmarin` and
    # `ForCrabaletta`'s words, with `FurinaStageLaw`'s numerals written out;
    # the performer rows are also each body's badge in game
    # (`StagePerformerBadge`). One Summon row since the trio can be cloned
    # (2026-09-25): named and random summons meet a full stage the same way.
    "Summon": ("A performer joins at the back with 1 Fanfare. On a full "
               "stage, the front one Bows and leaves, and the newcomer adds "
               "its Fanfare."),
    # Draft 3 (2026-09-25): no Bow clause (a Bow is the act once more) and
    # no Hydro (no act applies it).
    "Gentilhomme Usher": "End of your turn: gain 3 Block.",
    "Surintendante Chevalmarin": ("End of your turn: deal 2 damage to ALL "
                                  "enemies."),
    "Mademoiselle Crabaletta": ("End of your turn: deal 5 damage to a random "
                                "enemy."),
    # THE GUEST CAST (2026-09-25): `ArmKeywordTips.ForGuestStar` and the eight
    # guests' tips, word for word with the numerals written out. Each is also
    # the guest's badge on its body in game. The act lives here and on the
    # badge, not on the card's face ("<Name> joins the stage with N
    # Fanfare.").
    "Guest Star": ("A performer who joins the stage, one of each. A second "
                   "copy makes it Bow, then return with the new Fanfare "
                   "added."),
    "Neuvillette": ("End of your turn: pay 3 of his Fanfare to deal 8 Hydro "
                    "damage to ALL enemies."),
    "Clorinde": ("End of your turn: take 1 Fanfare from each other performer "
                 "to deal 8 Electro damage to a random enemy."),
    "Navia": ("End of your turn: deal Geo damage equal to her Fanfare to a "
              "random enemy."),
    "Chevreuse": "End of your turn: Spend 2 to gain 1 Energy next turn.",
    "Wriothesley": ("End of your turn: deal Cryo damage to a random enemy "
                    "equal to twice the Fanfare he lost to hits since his "
                    "last act."),
    "Sigewinne": ("End of your turn: give 3 of her Fanfare to the performer "
                  "behind her, or to your front performer if she is at the "
                  "back."),
    "Charlotte": "End of your turn: each other performer gains 1 Fanfare.",
    "Lynette": "End of your turn: Swirl a random enemy with an aura.",
    # 2026-09-06. THE WORD THE MOD PRINTS AND DEFINES NOWHERE. Five Furina
    # surfaces print it -- Shared Billing, Limelight and Stage Lights on their
    # faces, and the two Spotlight buffs on their power rows -- and every one
    # of them says what a Spotlighted card GAINS while saying nothing about
    # which card is one. It surfaced through `EB-507`'s arm copy of Shared
    # Billing, which is the first row on the prototype surface to print it and
    # so the first the gold-word census could see; the gap is the shipped
    # kit's and is older than the arm.
    #
    # READ, NOT INVENTED. `SpotlightSystem.IsSpotlighted` is the whole rule and
    # `SpotlightSystem.Designate` its only writer: Ethereal Spotlight lights
    # cards and nothing else does, the mode chosen decides which class, and the
    # lighting stands until the Spotlight moves (`FurinaRiderTips`'
    # SpotlightMove and SpotlightLasts rows say those two halves on the faces
    # that ask about them).
    #
    # THE GUEST CAST HALF ONLY, deliberately: it is the half every face that
    # prints the word is about ("Spotlighted Companion cards gain ..."), and it
    # is the half that is true with the reframe on as well as off -- the arm
    # retires Center Stage (R228 (1)), so a row naming that mode would teach a
    # rule half the runs cannot reach. There is no C# tip to hold this in step
    # with, which is `Companion`'s standing one row up and the same finding.
    "Spotlighted": ("Lit by Ethereal Spotlight, and nothing else lights a "
                    "card. Its Guest Cast mode lights your Companion cards, "
                    "and the lighting stands until the Spotlight moves."),
    # `EB-407`. THE WORD PRINTED BEFORE THE PLAYER HOLDS ANY. Encore is named
    # on the Neow screen and on opening-hand faces, and the only surface that
    # stated its rule was the METER LINE -- which needs the meter to be on the
    # board. The Furina round-4 seat made the run's first decision without the
    # word (run 1, (c) 5). The sentence was `ArmKeywordTips.ForEncore`'s until
    # R276's hygiene took that unattached tip out of the mod; it now stands
    # here alone, for the SHIPPED kit (the Stage arm hides the row). The
    # ORDER clause is the half nothing printed: the buffer
    # (`FurinaResources.AbsorbDamage`), a card's price
    # (`FurinaResourceHooks.BeforeCardPlayed`, before resolution) and a
    # member's 1 (`SalonPowers.PerformMember`, or 3/4 when it cannot pay) all
    # draw on ONE amount with no reservation and no priority, so a hit that
    # lands first leaves the member dry.
    "Encore": ("After Block it absorbs damage before HP. One pool, as each "
               "lands: a card pays to resolve, a member spends 1 to perform "
               "or acts at 3/4."),
    # `EB-329`. THE WORD THE GAME DEFINED NOWHERE until 2026-09-25: two cards
    # price themselves on it -- Chain of Command counts the Companion cards you
    # played last turn, The General's Banner triggers on one -- and the
    # round-5 act-1 seat met both across seventeen floors on which "no screen
    # defines" the term. SINCE 2026-09-25 IT HAS A TWIN: the afternoon Klee
    # seats met the same gap on the card, and `ArmKeywordTips.ForCompanion`
    # now carries this row's FIRST SENTENCE word for word
    # (`COMPANION_DEFINITION`; `tier0/tests/test_arm_keyword_tips.py` holds
    # the two in step). The row is written out of the two things the game
    # prints:
    #
    #   the TITLE. A companion row is "<Character> — <Card>"
    #     (`docs/<nation>-companions.yaml`, and `KokomiPlan.Label` splits a
    #     held card's name on that same dash), so the shape of the name IS
    #     the tell, and it is the only one a reader has mid-fight.
    #   the SLOT, in the mod's own sentence: `klee-mod/Klee/manifest.json`'s
    #     description, printed on the Mods screen, says it in eleven words and
    #     they are quoted verbatim. That is where a sighted player reads it
    #     and where `docs/current/text-conventions.md` rule 11 put it (R249
    #     pick 4) when the four starting relics stopped each printing it.
    #
    # `EB-430` ADDED THE THIRD AND FOURTH SENTENCES, and `EB-439` decided what
    # they say. The r5 run-2 seat priced two Companion rewards blind, skipped
    # them, and worked the trigger out three fights later: "a Companion card is
    # a free extra member perform stapled to whatever else it does". It then
    # inferred the aim -- "a Companion card's perform lands on the Companion
    # card's target" -- and the r6 seat watched a perform split across two
    # Toadpoles and prove that wrong. THE CODE IS THE ARBITER and it is not
    # ambiguous: `SalonPowers.PerformMember` picks with
    # `RunState.Rng.CombatTargets.NextItem(HittableEnemies)`, so the card's own
    # target reaches it nowhere; `CompanionPlayTrigger` performs `company[0]`
    # and then `RotateLeftmost`, and returns on `company.Count == 0` with a
    # whiff the ledger records.
    #
    # "ON FURINA'S STAGE" IS NOT DECORATION. The word rides Klee's Companions
    # too, whose own rider is Spark and lives on its own tip
    # (`ArmKeywordTips` / `KleeCompanionSpark`), so a row that stated the
    # perform flatly would be teaching a Klee a rule her board does not have.
    # The qualifier is what lets the two clauses ride the ONE row a reader
    # meets on a reward screen, which is where the seat needed them.
    # `EB-744`, second half: the fourth slot is a ROLL and the row read as a
    # promise. See `COMPANION_SLOT_SENTENCE`.
    "Companion": (COMPANION_DEFINITION + " " + COMPANION_SLOT_SENTENCE),
}

# `EB-460`. THE QUALIFIER WAS NOT ENOUGH, AND THE ROW SAID SO ITSELF.
#
# `EB-430` put Furina's perform rule on the shared `Companion` row and hung it
# on the words "On Furina's stage", on the reasoning that a Klee reading a flat
# sentence would be taught a rule her board does not have. The r14 Kokomi seat
# read the qualified version and filed it anyway: "Nothing on any screen in
# this run had a stage or a member order ... That entry appears to be
# describing a different character's kit." A qualifier a reader has to
# recognise as not-about-them is still three sentences of somebody else's kit
# on every screen, which is `EB-444` one word over.
#
# SO THE STAGE HALF IS THE ARM'S, and the arm is asked rather than the board:
# the word's home screen is a card REWARD, where a Furina board shows no stage
# and the rule is exactly what the r5 run-2 seat needed. `obs["character"]` is
# the wire's own answer and it is on every screen.
COMPANION_STAGE_CLAUSE = (
    " On Furina's stage playing one performs the front member, then sends it "
    "to the back; an empty stage performs nobody. The member picks its own "
    "enemy at random, never the card's target.")

# `EB-744`. AND UNDER THE STAGE THAT SENTENCE IS FALSE, which is the row's
# first find: the round-two Preserve seat played Companion cards for a run
# believing they rotate the cast. They do not. The Stage retires the shipped
# Salon outright (brief sec.2's table, R269) -- a Companion card is the shared
# action pool and nothing else -- and the one touchpoint the brief names is
# Chevalmarin's Hydro, which the Fontaine bench reacts off. So the arm gets its
# own clause rather than the shipped one, and it says what a reader can use.
COMPANION_STAGE_ARM_CLAUSE = (
    " It does nothing to your stage: no performer acts, moves or leaves for "
    "one. Chevalmarin's Hydro is the touchpoint -- a Pyro or Cryo Companion "
    "played into it reacts.")

#: Whose stage it is. Matched the way `understudy/adapter.py` matches it -- on
#: the character's printed Title, case-folded -- because that is the field the
#: wire sends and a Title is not an id.
_STAGE_CHARACTER = "furina"


# `EB-744`. IS THE STAGE ARM LIVE ON THIS SCREEN?
#
# THE FIND (round two, sec.4): "the glossary still carries the old words". An
# Encore row on a page whose kit has no Encore, the Companion row's shipped
# Salon sentence -- which the Preserve seat played Companion cards for a run
# believing -- and "Bow: earned by Spend only" beside a Final Bow that grants
# one. Every one of them is a rule the ARM retires, so the arm has to be
# askable.
#
# THE COMBAT BLOCK IS THE ANSWER AND IT USED TO BE THE WHOLE ANSWER.
# `blindplay_board` builds `combat.stage` from the wire's own `furina_stage`
# map, which is the mod saying the rule is live for this seat -- the same fact
# `_stage_live` hides the retired meters on. It exists only in COMBAT: outside
# one there is no creature and the mod's snapshot is empty by construction.
#
# ROUND THREE MEASURED WHAT THAT GAP COSTS: "the Companion glossary alternates
# between two sentences on consecutive screens of one fight" (sec.4). A chooser
# overlay, a reward and a shop are all not-combat, so the same word changed its
# meaning between two screens a seat read a minute apart. A rule that moves is
# worse than a rule that is merely narrow.
#
# SO THE ARM IS A FACT ABOUT THE RUN AND IS HELD FOR IT. The arm cannot turn on
# or off inside a run -- it is a build switch -- so the first screen that can
# answer answers for all of them, latched by `blindplay_faces.stage_arm` under
# the deck store's own two guards (character, and never backwards a floor). The
# combat block stays the reading; the latch is only what carries it.
_STAGE_RETIRED_KEYWORDS = frozenset({"Encore"})

# 2026-09-25. AND THE ROWS ONLY THE ARM HAS. The three performers carry the
# shipped Salon members' names, and the shipped members' rules are not these
# (a shipped member deploys and performs on a Companion play). So their rows
# print on an arm page and on no other: a shipped seat reading "End of your
# turn: gain 3 Block" beside a Salon Usher would be two rules for one name,
# `EB-728`'s Fanfare finding one table over.
_STAGE_ONLY_KEYWORDS = frozenset({
    "Gentilhomme Usher", "Surintendante Chevalmarin",
    "Mademoiselle Crabaletta",
    # THE GUEST CAST (2026-09-25): a shipped Fontaine Companion shares a
    # guest's name, and off the arm its face means that Companion.
    "Guest Star", "Neuvillette", "Clorinde", "Navia", "Chevreuse",
    "Wriothesley", "Sigewinne", "Charlotte", "Lynette"})

# `EB-728`. AND THE ROW THE SHIPPED KIT STILL OWNS.
#
# `Fanfare` is a word BOTH kits print and they do not mean the same thing by
# it: under the Stage it is a performer's own bar, and on the shipped sheet it
# is Furina's meter, whose rule `METER_RULES["Fanfare"]` already states beside
# it. The table stated the Stage's bar unconditionally, so a flag-OFF seat read
# the arm's rule next to the shipped meter's -- two rules for one word on one
# screen. The row is keyed on the arm now, like `Encore`'s retirement above and
# `Companion`'s clause below, and a screen that cannot tell keeps the reading
# it has always had.
FANFARE_SHIPPED_ROW = (
    "Furina's own meter, spent by the cards that print a Fanfare rider. It is "
    "hers and not a performer's -- this run has no stage.")


def _stage_arm(obs: dict[str, object]) -> bool:
    """Is the Stage arm live for this RUN (`EB-744`, round three)?

    The screen's own block where it has one; otherwise what an earlier screen
    of this run latched. `False` where nothing has ever answered, which is the
    reading every page had before the latch existed.
    """
    combat = obs.get("combat")
    if isinstance(combat, dict) and combat.get("stage") is not None:
        return True
    held = obs.get("stage_arm")
    return held is True

# `EB-504`. TWO ROWS WHOSE RULE IS ABOUT A CHARACTER WHO IS NOT IN THE RUN.
#
# WHAT TWO SEATS READ. On a Kokomi shop screen: "*Hexerei -- A Companion card
# that prints the word, and Klee herself. Some are Klee's own, some are not.
# Cards of hers pay when you play one.* I could not extract a rule from that
# sentence, and it names a character who is not in this run" (Kokomi r17 lane
# 2). And on a Furina run, `Fischl -- Nightrider` printed BOTH this and the
# `Oz` row: "In a Furina run I have no Klee cards, no way to obtain that
# Power, and no idea what 'pay' means or what it would cost me ... half its
# rules text was noise" (Furina r11 lane 2).
#
# THE WORDS ARE PRINTED ON EVERY RUN AND THE RULES ARE NOT. `Hexerei` rides
# eighteen companion faces the whole roster can draft, and its rule is Klee's
# Spark rider; `Oz` is named by Fischl's face, which every character meets,
# and the Power that fields him is Klee's. So the tag reaches every run and
# the rule reaches one, which is `EB-460`'s finding one table over -- and its
# answer too: the ARM is asked, not the board, off the wire's own `character`.
#
# THE TAG STILL PRINTS, NAME ONLY. A word on the screen with no entry at all
# reads as a word the page failed to define; the name with no rule says what
# is true, which is that this run has no rule for it. A feed that does not say
# who is playing gets the rule, `absent is not zero`'s direction: silence
# about the character is not evidence it is somebody else's.
_ARM_KEYWORD_CHARACTER: dict[str, str] = {"Oz": "klee"}

# `EB-753`. AND THE OTHER KIND OF OFF-ARM WORD, WHICH IS NOT THAT ONE.
#
# THE FIND (Klee r27, lane 1 and cook, fight 2 reward). The Furina Stage's
# `Spend` row -- lead performer, Bow, an empty stage -- printed on a KLEE card
# reward screen, because R270 made Spark a currency and Klee's sinks print the
# word "Spend". A rule about three performers, on a screen with no performers
# and no way to get one.
#
# THE DIFFERENCE FROM `_ARM_KEYWORD_CHARACTER` IS THE WORD AND NOT THE RULE.
# `Hexerei` and `Oz` are printed BY faces every run can draft, so the word is
# genuinely on the screen and the reader is owed the sentence saying it is
# inert here (`EB-583`). These words are not: `Spend`, `Bow`, `Raise`,
# `Rotate`, `Mine`, `Plan`, `Mend` are ordinary English that another kit's
# prose says for its own reasons, and the match is a FALSE POSITIVE rather
# than an off-arm tag. A false positive owes no entry at all -- there is
# nothing to say "is inert here" about -- so the row does not print.
#
# THE UNIVERSAL WORDS KEEP NO OWNER and are untouched: `Companion` (every arm
# drafts them and `EB-460` already splits its one arm-conditional clause),
# `Swirl` (ten Universals print the verb), `Grounded` (Kaeya's Power, on a
# companion card), and the two above.
#
# A FEED THAT DOES NOT SAY WHO IS PLAYING GETS EVERY ROW, which is
# `_ARM_KEYWORD_CHARACTER`'s direction one table up and `absent is not zero`'s:
# silence about the character is not evidence it is somebody else's.
_ARM_KEYWORD_ARM: dict[str, str] = {
    "Bomb": "klee", "Set off": "klee", "Spark": "klee", "Mine": "klee",
    "Plan": "kokomi", "Dusk": "kokomi", "Mend": "kokomi",
    "Tamakushi Casket": "kokomi",
    "Spend": "furina", "Fanfare": "furina", "Bow": "furina",
    "front performer": "furina", "back performer": "furina",
    "Encore": "furina", "Spotlighted": "furina",
    "Ousia": "furina", "Pneuma": "furina",
    "Summon": "furina", "Gentilhomme Usher": "furina",
    "Surintendante Chevalmarin": "furina", "Mademoiselle Crabaletta": "furina",
    # THE GUEST CAST (2026-09-25).
    "Guest Star": "furina",
    "Neuvillette": "furina",
    "Clorinde": "furina",
    "Navia": "furina",
    "Chevreuse": "furina",
    "Wriothesley": "furina",
    "Sigewinne": "furina",
    "Charlotte": "furina",
    "Lynette": "furina",
}


def _arm_owns(word: str, who: str) -> bool:
    """May this run's character be shown this kit word's rule? (`EB-753`)"""
    owner = _ARM_KEYWORD_ARM.get(word)
    return not (owner and who and owner != who)


# ROUND FOUR. TWO WORDS THAT BELONG TO ONE CARD.
#
# `Ousia` and `Pneuma` are the two halves of Arkhe Alignment's choice, and the
# rows were matched on the word alone -- so they rode Ousia Surge and Pneuma
# Refrain too, whose names merely share it, and a seat read the Arkhe meaning
# as those cards' meaning. The rows now print only on a screen that shows
# Arkhe Alignment itself: the card, or its Power's badge (both print the
# name). The C# side is the same rule: the tips ride the Arkhe card's golded
# face and `ArkheAlignmentPower`'s own hover, and nothing else.
_ARM_KEYWORD_ANCHOR: dict[str, str] = {
    "Ousia": "Arkhe Alignment", "Pneuma": "Arkhe Alignment",
}


def _anchored(word: str, obs: dict[str, Any]) -> bool:
    """Is the card this word belongs to on the screen? True for every word
    that belongs to no one card. TITLES INCLUDED (`_every_string`, not
    `_body_strings`): the anchor is the card's own name."""
    anchor = _ARM_KEYWORD_ANCHOR.get(word)
    if not anchor:
        return True
    return any(anchor in text for text in _every_string(obs))

# `EB-583`. WHAT AN OFF-ARM WORD SAYS INSTEAD, and it is the correction to the
# paragraph above rather than a second rule.
#
# THE FIND (Furina r15 lane 1 (c) 7). `Hexerei` printed on Sucrose's face and
# on Razor's under the Furina arm, and the Words block answered with the name
# and nothing after it. `EB-504`'s reasoning was that "a word on the screen
# with no entry at all reads as a word the page failed to define"; a bare name
# in a block of definitions reads as exactly the same thing -- the seat called
# it "an empty definition" -- so the half that was missing is the sentence
# saying WHY there is no rule to give.
#
# IT NAMES NO CHARACTER AND STATES NO OFF-ARM RULE, which is `EB-504`'s
# finding kept whole: the sentence the seats could not use was the one that
# named somebody else's kit and priced somebody else's resource. What is left
# is the only fact a reader of THIS run needs -- the mark is inert here -- and
# it is one line. The ON-arm row is untouched and is still the sentence held
# in step with the C# tip.
_OFF_ARM_KEYWORD: dict[str, str] = {
    "Oz": ("A summoned raven another kit's Power fields. Nothing you can "
           "draft in this run puts him out, so the clause never fires."),
}

# One pattern per word, and they are CASE-SENSITIVE on purpose: the game
# capitalises a keyword wherever it prints one, and a case-blind `mine` or
# `plan` would define a word out of ordinary prose. The plural is the same
# word (`two Bombs`), and `Set Off` is accepted because a badge title-cases it.
# `Sets off` is the verb with another subject -- the co-op set's Pass the Match
# and Knights of Favonius ("their next Attack Sets off your Bombs"), the
# codegen's second `Set off` token -- and it is the same word.
_ARM_KEYWORD_RE = {
    "Bomb": re.compile(r"\bBombs?\b"),
    "Set off": re.compile(r"\bSets? (?:it )?[Oo]ffs?\b"),
    "Spark": re.compile(r"\bSparks?\b"),
    "Mine": re.compile(r"\bMines?\b"),
    "Plan": re.compile(r"\bPlans?\b"),
    # `EB-643`. NO PLURAL: the word names one moment. It fires on the two rows
    # that print it and on the strip line a queued Dusk entry draws.
    "Dusk": re.compile(r"\bDusk\b"),
    "Mend": re.compile(r"\bMends?\b"),
    # `EB-377`'s `Swirl` is printed as a verb, so it conjugates the way
    # `Mend` does. (Its sibling `Hexerei` was retired by R276 pick 2.)
    "Swirl": re.compile(r"\bSwirls?\b"),
    # `EB-372`. NO PLURAL: the word names one Power. It fires on Kaeya's face,
    # on the Cold-Blooded buff it leaves behind, and on the Power card itself
    # wherever one is printed -- which is every screen a reader can meet the
    # word on, whether or not the deck holds it.
    "Grounded": re.compile(r"\bGrounded\b"),
    # `EB-446`. NO PLURAL: there is one raven. It fires on Nightrider's face,
    # which names him and cannot grant him, and on the Power card that does --
    # every screen a reader can meet the word on, whether or not the run holds
    # the Power, which is the state the r7 seat was in for five plays.
    "Oz": re.compile(r"\bOz\b"),
    # FURINA, THE STAGE (`EB-723`). The reframe's four -- `Deploy`, `Evoke`,
    # `Drain` and `Encore` -- left this table with the rows that printed them.
    #
    # THE SEVEN, and each pattern says what the word is on a face. `Spend`,
    # `Raise` and `Rotate` are printed as VERBS and conjugate the way `Mend`
    # does. `Fanfare` and `Bow` take no plural: a bar is never printed as one
    # and a curtain call is one act. The two SEAT words are two words on
    # purpose -- what they carry is a rule about WHICH SEAT, and a pattern on
    # the bare word "lead" would fire on ordinary prose.
    #
    # AND THEY ARE WRITTEN WITH AN EDITOR rather than a shell heredoc, which
    # is how the reframe's three once acquired a literal 0x08 in place of a
    # word boundary and matched nothing at all.
    # THE TEXT PASS (2026-09-25) retired `Raise` and `Rotate`, renamed the
    # lead the FRONT performer, and prints `Bow` as a verb ("it Bows").
    "Spend": re.compile(r"\bSpends?\b"),
    "Fanfare": re.compile(r"\bFanfare\b"),
    "Bow": re.compile(r"\bBows?\b"),
    "front performer": re.compile(r"\bfront performer\b"),
    "back performer": re.compile(r"\bback performer\b"),
    # R276 batch two: Arkhe Alignment's two halves.
    "Ousia": re.compile(r"\bOusia\b"),
    "Pneuma": re.compile(r"\bPneuma\b"),
    # 2026-09-25. `Summon` in either case: Improvised Number prints it
    # mid-sentence ("summon a random performer"), and the mod attaches the
    # tip off the op, not the capital. A PERFORMER is matched on its name --
    # the short one a face prints ("Summon Usher") ends the full one the stage
    # lines print -- and on a RANDOM summon's face, which may field any of the
    # three and so carries all three tips in game.
    "Summon": re.compile(r"\b[Ss]ummon\b"),
    "Gentilhomme Usher": re.compile(
        r"\bUsher\b|\b[Ss]ummon (?:a|2|two) random performer"),
    "Surintendante Chevalmarin": re.compile(
        r"\bChevalmarin\b|\b[Ss]ummon (?:a|2|two) random performer"),
    "Mademoiselle Crabaletta": re.compile(
        r"\bCrabaletta\b|\b[Ss]ummon (?:a|2|two) random performer"),
    # THE GUEST CAST (2026-09-25). The keyword on a Guest Star's title or
    # face, and each guest by its name -- but never a shipped Companion's
    # dashed title ("Neuvillette — O Tears, I Shall Repay"), which is that
    # Companion and not the guest.
    "Guest Star": re.compile(r"\bGuest Star\b|\bjoins the stage with\b"),
    "Neuvillette": re.compile(r"\bNeuvillette\b(?!\s*[—–-])"),
    "Clorinde": re.compile(r"\bClorinde\b(?!\s*[—–-])"),
    "Navia": re.compile(r"\bNavia\b(?!\s*[—–-])"),
    "Chevreuse": re.compile(r"\bChevreuse\b(?!\s*[—–-])"),
    "Wriothesley": re.compile(r"\bWriothesley\b(?!\s*[—–-])"),
    "Sigewinne": re.compile(r"\bSigewinne\b(?!\s*[—–-])"),
    "Charlotte": re.compile(r"\bCharlotte\b(?!\s*[—–-])"),
    "Lynette": re.compile(r"\bLynette\b(?!\s*[—–-])"),

    # `EB-407`, and it OUTLIVED the reframe (`EB-723`): the meter is shipped
    # machinery, the word is printed on the Neow screen and on opening-hand
    # faces before the meter exists, and every Furina row the Stage does not
    # swap still carries it. NO PLURAL: a meter is never printed as one.
    "Encore": re.compile(r"\bEncore\b"),
    # NO PLURAL AND NO CONJUGATION: the word is an adjective on a card class
    # ("Spotlighted Companion cards"), and the VERB the kit prints is "moved
    # the Spotlight", which is `FurinaRiderTips.ForSpotlightMove`'s phrase and
    # not this row's.
    "Spotlighted": re.compile(r"\bSpotlighted\b"),
    # `EB-329` MATCHED THE PHRASE `Companion cards?` AND THE FACES HAVE SINCE
    # MOVED. That row's reasoning was that the two cards which PRICE themselves
    # on the word both spell it out; `Chain of Command` now reads "for each
    # [gold]Companion[/gold] you played this turn" and `The General's Banner`
    # the same way, so the phrase pattern fired on neither and the word was
    # undefined again on exactly the screens the row was filed for. `EB-377`
    # widens it to the bare word.
    #
    # THE ORIGINAL WORRY DOES NOT BITE HERE. It was that "Companion" alone
    # would fire on a companion's own face -- but no companion face prints the
    # term (their tell is the dashed title), and the haystack is the
    # OBSERVATION's printed values rather than this page's own prose, so the
    # section headings and standing notes cannot raise it either.
    "Companion": re.compile(r"\bCompanions?\b"),
}


# `EB-367`. THE BASE GAME'S OWN WORDS, WHEN ITS OWN TIP IS NOT WHAT THE WORD
# DOES. Separate from `ARM_KEYWORDS` on purpose: those rows are held in step
# with `ArmKeywordTips` in the C# and their pin asserts a one-to-one join, so a
# word this mod did not invent and hangs no tip on has no place in that table.
#
# THE SHAPE IS `EB-359`'s -- a keyword that names a STATUS gets the status's own
# rule printed, not the card-side reminder that mentions it. `Tainted`'s entry
# is that row's example: the game's tip says "Gain 2 Tainted when played" and
# never that Tainted is +2 damage taken, so two seats spent a card to find out.
#
# `Ringing` is the same gap one enemy over. Beast Cry stamps the affliction onto
# every card the player owns that carries no other affliction, and the rule is
# "playable only if you have not started a card play this turn" -- so the turn
# after Beast Cry is ONE card play. The Furina round-one seat met it twice at
# the act-1 boss, "a debuff I never saw named or explained anywhere before it
# first appeared", and had to infer it from the reminder printed on every card
# in hand. The two seams the reminder never mentions are what makes the choked
# turn playable at all, and they are the reason this entry is worth its lines.
#
# NO EARLIER WARNING IS AVAILABLE ON THIS WIRE, and that is a fact about the
# feed rather than a decision here: Beast Cry's intent is a bare `DebuffIntent`
# (`MegaCrit.Sts2.Core.Models.Monsters.CeremonialBeast`), whose hover tip names
# no power, so the first screen that carries the word is the one the affliction
# lands on. The entry prints there, which is the turn the seat has to choose.
#
# `EB-537` PUT `Shatter` HERE, and the table's own rule is why it belongs. The
# word is Frozen's second clause and NOT a reaction of its own, so it is in
# neither `REACTION_KEYWORDS` nor `ARM_KEYWORDS` -- and it had no row at all.
# The Klee r19 lane-2 seat was offered `Freminet -- Shattering Pressure`
# ("Your Shatters deal 4 additional damage") on a run that never printed a
# Shatter: "I could not have played it ... and the word is not in the glossary
# on that screen." A row here prints on the WORD, on every screen that carries
# it, which is exactly the rule a face naming an unreachable mechanic needs.
#
# THE SENTENCE IS `Frozen`'s OWN, not a second reading of the rule: the freeze
# ends with the hit, which is the half the Frozen row leaves to inference
# because it is written from the frozen enemy's side.
GAME_KEYWORDS: dict[str, str] = {
    "Ringing": ("An enemy debuff on YOU: you can play only 1 card this turn. "
                "The first play locks every other Ringing card in hand. Cards "
                "that already carry a different affliction are never stamped "
                "and stay playable; potions, relics and end-of-turn triggers "
                "are not card plays and are untouched."),
    "Shatter": (f"The first Attack to hit a Frozen enemy before it acts deals "
                f"{SHATTER_DAMAGE} additional damage and ends the freeze. "
                "Only a Frozen enemy can be Shattered."),
    # `EB-359`. THE GAME'S OWN TIP FOR THE WORD IS THE CARD-SIDE REMINDER
    # ("Gain 2 Tainted when played") and never what Tainted DOES; two seats
    # spent a card to read their own status line for it. The rule is that
    # status line's, verbatim from the wire (Kokomi r4d act 2, Klee r8 run 2).
    "Tainted": ("A debuff on YOU: take N additional damage from Attacks this "
                "turn, N being the stack, and per hit of a multi-hit intent. "
                "A card that says Gain 2 Tainted puts 2 on you when played; "
                "it wears off at the end of your turn."),
}

_GAME_KEYWORD_RE = {
    "Ringing": re.compile(r"\bRinging\b"),
    # `EB-537`: the verb conjugates on the faces that print it -- Freminet's
    # power says "Your Shatters", the Salon paragraph says "no Shatter", and
    # the Frozen row says "Shatters for 6".
    "Shatter": re.compile(r"\bShatter(?:s|ed|ing)?\b"),
    "Tainted": re.compile(r"\bTainted\b"),
}


# `EB-377`. THE BASE GAME'S WORDS A PRINTED FACE NAMES, WHEN NOTHING ON THE
# BOARD IS WEARING THEM YET.
#
# THE GAP, AND WHY IT LOOKED LIKE FOUR WORDS WERE FINE. `Weak`, `Frail`, `Slow`
# and `Minion` reached the r9 page correctly defined and `Vulnerable` did not,
# which reads as an oversight in a table and is not: those four arrived as
# POWERS on a body, and `_wire_keyword_rows` lifts the game's own tip off a
# status row. A word a CARD names has no such row until something is wearing
# it -- so the one screen where the definition decides a purchase is exactly
# the screen that has none. The r9 run-2 seat bought `Exposed Flank+` "on a
# genre assumption" (act 1, (c) 6) because the only surface that ever defines
# Vulnerable is an enemy already carrying it.
#
# LAST OF THE FOUR SOURCES, AND THAT ORDER IS THE POINT. These are the base
# game's rules, not this mod's, so the game's own sentence wins wherever the
# wire carries one: `keyword_notes` adds these only for a word no earlier
# source defined. A screen with a Weak-bearing enemy on it still reads the
# game's Weak; a screen holding only a card that APPLIES Weak reads this.
#
# WHERE THE NUMBERS COME FROM. The three duration debuffs quote
# `blindplay_shape`'s percentages, which are pinned to `tier0.constants` from
# the test side -- this module may not import `tier0` at all
# (`test_blindplay_cannot_reach_a_sheet_or_a_policy`). The two enchantments are
# `docs/current/dossiers/content/event-conversion-gallery.md`'s ruled
# conversion (`enchant_damage`, `enchant_block`, and Swift's first-play draw),
# which is the same rule `tier0.engine` runs.
#
# WHAT IS DELIBERATELY ABSENT. `Goopy` was reported undefined beside these and
# has no rule anywhere in this repo -- no constant, no op, no dossier line --
# so a sentence for it would be invented rather than read, which is the one
# thing this table may never do. It reaches the page the way `Slow` does, off
# the wire, the moment a body wears it. `Minion` is left to the wire for the
# same reason it was never missing: the word only ever appears on a body that
# is one.
BASE_KEYWORDS: dict[str, str] = {
    # `EB-481` IS `EB-469` ONE DEBUFF OVER, found the same way one round later:
    # the game's status line says "Receive 50% more damage from Attacks", this
    # row said "every hit", and `Kurage's Oath` -- printed `cost 1, skill` --
    # took the 1.5x (Kokomi r16 (c) 2). `VulnerablePower` is the TARGET's own
    # power and gates on `IsPoweredAttack()` exactly as `WeakPower` does, so
    # a card's hit is amplified whatever its `type:`.
    #
    # `EB-497` NARROWED IT to "every CARD hit", because "every hit" was one
    # case too wide: Explosive Ampoule dealt 10, not 15, into a Vulnerable
    # Sewer Clam (Klee r17 lane 1). `potions.fire_potion` goes through
    # `refpowers.unpowered_damage`, which never reaches `modify_damage_taken`,
    # and the shipped C# power's `IsPoweredAttack()` gate says the same thing
    # -- so a potion's damage is flat and this row says so.
    #
    # THE ENEMY'S OWN STATUS LINE now carries the same rule: `EB-481` reopened
    # for it and `KleeMod.InjectLocStrings` merges an arm row into the game's
    # `powers` table. Same sentence as `BaseKeywordTips.ForVulnerable`, pinned
    # to it.
    #
    # `EB-523` PUT THE ATTACK BACK IN, and it is `EB-497`'s own correction
    # meeting the side of the board that row did not read. "Every card hit" is
    # complete on an ENEMY, where everything that lands is a card or a potion,
    # and SILENT ON THE PLAYER, where the number that matters is a monster's
    # swing: the Kokomi r18 lane-2 seat wore `Vulnerable 99 -- Receive 50% more
    # damage from cards for 99 turns` in front of a 24-damage intent and could
    # not price it. It counts -- `IsPoweredAttack()` is a property of the HIT
    # and a monster's move carries it, and `combat` runs every enemy hit
    # through `powers.modify_damage_taken(state.player, ...)`.
    "Vulnerable": (
        f"An attack or card hit on it deals {VULNERABLE_TAKEN_PCT}% more, a "
        f"Skill's too. A potion's does not. One stack falls off at the end "
        f"of each of its turns."),
    # `EB-469`. THE GAME'S OWN STATUS LINE SAYS "Attacks deal 25% less damage
    # for 1 turn", and the Kokomi r15 seat read "Attacks" as the CARD TYPE --
    # "the status line told me skills were safe and the card told me they were
    # not" ((c) 2), after watching `Kurage's Oath`, printed `cost 1, skill`,
    # go from 3 to 2 while it wore Weak. The engine is not what is wrong:
    # `WeakPower.ModifyDamageMultiplicative` gates on `IsPoweredAttack()`, a
    # property of the HIT, and every damage clause the generator emits carries
    # `ValueProp.Move` whatever `type:` its sheet row declares. So the page
    # says which, in the mod's own words -- this row and
    # `BaseKeywordTips.ForWeak` are one sentence, pinned to each other.
    "Weak": (
        f"The wearer deals {WEAK_DEALT_PCT}% less damage with every hit it "
        f"lands, a Skill's damage too. One stack falls off at the end of "
        f"each of its turns."),
    "Frail": (
        f"The wearer gains {FRAIL_BLOCK_PCT}% less Block. One stack falls "
        f"off at the end of each of its turns."),
    # `EB-597`. THE SAME FINDING A FOURTH TIME, and this one the seat wrote up
    # as a contradiction rather than a doubt: "Shrink's own text says `your
    # Attacks deal 30% less damage`, but Kurage's Oath is printed `cost 1,
    # skill` and it still fell 3 to 2. Weak's glossary on the same screen goes
    # out of its way to say 'a Skill's damage too'; Shrink's does not, and
    # Shrink hits Skills anyway" (Kokomi r22 lane 1, fight 2).
    #
    # THE ENGINE IS RIGHT AND ONLY THE WORDS ARE WRONG.
    # `ShrinkPower.ModifyDamageMultiplicative` gates on `IsPoweredAttack()` and
    # nothing else -- the identical gate `WeakPower` uses, MEASURED off the
    # shipped assembly -- so "Attacks" in the game's sentence means attack
    # HITS, exactly as it does in Weak's. This row is Weak's sentence with its
    # own rate and its own duration clause, and `KleeMod.InjectLocStrings`
    # merges the same rule into the game's `SHRINK_POWER` rows.
    "Shrink": (
        f"The wearer deals {SHRINK_DEALT_PCT}% less damage with every hit it "
        f"lands, a Skill's damage too. It lasts while whoever applied it is "
        f"alive."),
    # The two undecaying stat powers. Named on four prototype faces and on the
    # Plan's own tip, which says Strength does NOT reach a Plan -- a sentence
    # that cannot be read by somebody who does not know what Strength is.
    "Strength": ("Adds its amount to every Attack hit the wearer lands. It "
                 "does not decay."),
    "Dexterity": ("Adds its amount to every Block the wearer gains. It does "
                  "not decay."),
    # The three enchantments (`EB-355` is the same gap at the enchant screen).
    # A card wears one for the rest of the run and the page prints it in the
    # card's own `enchantment` field (`EB-181`), which is a badge and not a
    # sentence.
    "Sharp": ("An enchantment on an Attack: it deals that much more damage, "
              "for the rest of the run."),
    "Nimble": ("An enchantment on a Skill: every Block it gives you is that "
               "much bigger, for the rest of the run."),
    "Swift": ("An enchantment on a Power: the first time you play it in a "
              "fight, draw that many cards."),
    # The one word here this mod invented and then defined nowhere a card can
    # be read: the Masque of the Red Death's debt. The rule is
    # `TurnEndAttribution`'s own docket sentence, which only ever renders at
    # the end of a turn the power has already taken the Block on.
    "Bond of Life": ("A debt on you: the first Block you gain each turn pays "
                     "it down instead of reaching your bar. Only Arlecchino "
                     "- Masque of the Red Death makes one."),
    # THE VERB, WHICH IS THE HALF THE GAME DOES NOT DEFINE. `Exhaust` on a card
    # that exhausts ITSELF is a declared keyword and the game hangs its own tip
    # on it; `Pearl Barrage` reads "Exhaust 1 card from your hand ... per card
    # Exhausted this turn", where the word is an instruction about OTHER cards,
    # declares nothing and hovers nothing.
    "Exhaust": ("The card leaves the fight the moment it is spent -- it is not "
                "discarded and cannot be drawn again this combat. It is back "
                "in the deck for the next fight."),
}

# Case-sensitive, `_ARM_KEYWORD_RE`'s rule and for its reason. Written out
# rather than derived from the table's keys, because two of the rows conjugate
# and the rest must NOT: a face says "2 Vulnerable", never "2 Vulnerables", and
# `Sharp`, `Swift` and `Strength` are ordinary English words whose plural would
# fire on prose.
_BASE_KEYWORD_RE = {
    "Vulnerable": re.compile(r"\bVulnerable\b"),
    "Weak": re.compile(r"\bWeak\b"),
    "Frail": re.compile(r"\bFrail\b"),
    # `EB-597`: the debuff the Shrinker Beetle applies. SINGULAR ONLY, the
    # rule the comment above states -- a status line reads "Shrink -1", never
    # "Shrinks", and the verb is ordinary English.
    "Shrink": re.compile(r"\bShrink\b"),
    "Strength": re.compile(r"\bStrength\b"),
    "Dexterity": re.compile(r"\bDexterity\b"),
    "Sharp": re.compile(r"\bSharp\b"),
    "Nimble": re.compile(r"\bNimble\b"),
    "Swift": re.compile(r"\bSwift\b"),
    "Bond of Life": re.compile(r"\bBond of Life\b"),
    "Exhaust": re.compile(r"\bExhaust(s|ed)?\b"),
}


# `EB-340`. THE FOUR-ELEMENT REACTIONS, DEFINED ON A SCREEN THAT HAS ONE.
#
# THE GAP. A Reaction reached the page only as a `*Reaction preview: Melt*` row
# under a card that HAPPENED to be in hand, HAPPENED to supply the right
# element and only while the aura was already on the board. Everywhere else the
# rule was unstated: the r7b act-3 seat watched `Shinobu`'s 5 Electro deal 13
# into a Pyro aura, could not price it, and got the formula two rounds later
# "unprompted on `Ka-pow!`" -- 5 x 1.5 + 6 splash, exact. "The rule existed the
# whole time; whether I was allowed to see it depended on my draw."
#
# WHERE THE SENTENCES COME FROM. `KleeMod.cs`'s `keywordFallback`, which is the
# one place the game's own preview text is composed (and is byte-identical to
# `pck-src/klee/localization/eng/card_keywords.json`, the shipped copy). Each
# body below keeps that text's load-bearing clause VERBATIM -- the multiplier,
# the splash, the Shatter -- and replaces only the "This card supplies X or Y"
# lead-in, which is a sentence about a card and there is no card here. Held in
# step from this side by `test_the_reaction_glossary_is_the_games_own_preview`,
# the discipline `ARM_KEYWORDS` is already under.
#
# `EB-329` ADDED THE RE-APPLICATION CLAUSE, and it is the one sentence in this
# table that is not about a reaction at all -- it is about why a reader cannot
# SEE one. Two Kokomi seats filed "the aura is not consumed when its own text
# says it is" as a defect; the r4c seat worked out what was really happening
# (round 4c, finding 15) and it is the two shipped rules composing. Sara's
# Electro reacts off a Hydro aura, the reaction applies a debuff, the
# Tamakushi Casket answers "whenever you apply a debuff to an enemy" with 2
# Hydro damage, and a Hydro hit refreshes a Hydro aura to its full duration.
# So the consumed state exists for less than one screen refresh, and the
# keyword's central sentence is unfalsifiable from the board. The relic is not
# NAMED here, because this row is printed for a Klee who holds no Casket; what
# is named is the shape, which any relic answering a debuff in the aura's own
# element has.
#
# SIX, NOT FOUR. `EB-340` names the four the seat met; the mod's `Reaction`
# enum pairs the game's four elements six ways, and the other two are reachable
# by the same deck -- Charlotte supplies Cryo, Shinobu Electro, Barbara Hydro,
# so Superconduct and Electro-Charged are one companion draft away. A glossary
# that defined four of six would hide the two a seat is least likely to have
# seen.
#
# `EB-465` MADE IT EIGHT. `Swirl` and `Crystallize` were kept out on the ground
# that "NO card in this build supplies Anemo or Geo" -- and that ground went
# when `EB-454` put both words in `_ELEMENT_KEYWORD`, because the faces were
# there all along (`Jean -- Gale Blade` is Anemo, `Chiori -- Fluttering Hasode`
# is Geo). The Furina r8 seat held an Anemo card over a live Swirl preview and
# was told in capitals that NO REACTION IS REACHABLE HERE. Both are in the
# mod's `Reaction` enum, both have a shipped preview row, and both are TRIGGER
# elements: they pair with nothing and react with ANY aura already standing
# (`ReactionTable.For`, the two lines above the pair switch). So they are
# reachable on a different test from the six -- `SPREAD_REACTIONS` below.
REACTION_KEYWORDS: dict[str, str] = {
    "Elemental Reaction": (
        "A hit of a different element than the aura an enemy is already "
        "wearing. The aura is CONSUMED to trigger the reaction, so the hit "
        "leaves no aura of its own behind: a card that hits once leaves the "
        "enemy bare, and only a later hit of the same card applies its "
        f"element. On a bare enemy the hit applies its own element for "
        f"{AURA_DURATION_TURNS} turns instead, and a hit matching the aura "
        "refreshes it. THAT LAST RULE CAN HIDE THE FIRST: where a reaction's "
        "own debuff sets off a relic that hits with the aura's own element, "
        "the aura is consumed and RE-APPLIED inside the same beat, so no "
        "screen ever shows it gone and the reaction looks as though it did "
        "not happen. The reaction did happen -- its effect is on the body. "
        # `EB-544`. WHERE AN ELEMENT COMES FROM, which no screen said and a
        # seat spent a potion finding out: "a Fire Potion used to set up
        # Vaporize left no Pyro aura at all, and nothing on any screen says
        # which sources apply an element and which do not" (Kokomi r19 lane 1).
        # The rule is one expression's -- `AuraCmd.ElementOfPlay`
        # answers off the CARD being played (and, under the companion arm, a
        # rider on the dealer), so a potion, which is played through no card at
        # all, answers `Element.None` and applies nothing. Named here rather
        # than on the six pair rows because it is true of all of them, and this
        # is the row a mono-element deck reads.
        # `EB-562`. AND THE CLAUSE NOW ADMITS THE EXCEPTION. It sent a reader
        # to the relic's own face, and the one relic that IS an exception did
        # not carry the answer there: the r20 seat called "does the Tamakushi
        # Casket's Hydro hit leave an aura" the single fact it most wanted and
        # never got, and the round-18 seat watched it re-lay Hydro inside a
        # beat. The strike is a real elemental hit in both engines
        # (`kokomi_plan.casket_strike`'s "THE HIT IS OTHERWISE REAL";
        # `TamakushiCasket.Strike` through `ElementalHit.Deal`), so it lays
        # Hydro or reacts with what is there. `EB-348` put the sentence on the
        # relic's face and on its keyword row; this is the glossary's half.
        #
        # NOT BY NAME HERE, for `EB-329`'s reason on this same row: it prints
        # for a Klee who holds no Casket, and what is general is the shape.
        "An element comes from a CARD that prints one and from nothing else: "
        "a potion, a relic or an enemy applies none unless its own face or its "
        "own glossary line says so -- and one relic's line does, because its "
        "strike is a real elemental hit and leaves the aura to prove it."),
    # `EB-345` (R249) retuned the six preview rows in `KleeMod.cs` -- each one
    # now leads with the pair that reacts instead of a 60-character preamble
    # about what the CARD supplies, and Electro-Charged says what the dot
    # actually does rather than naming its effect type. The clauses below
    # follow, verbatim, which is the whole point of the pin.
    "Melt": ("Pyro on a Cryo aura, or Cryo on a Pyro aura. This hit deals "
             "1.75x damage and consumes the aura."),
    "Vaporize": ("Pyro on a Hydro aura, or Hydro on a Pyro aura. This hit "
                 "deals 1.5x damage and consumes the aura."),
    "Overloaded": ("Pyro on an Electro aura, or Electro on a Pyro aura. "
                   "Deals 6 damage to ALL enemies and applies 1 Weak to the "
                   "reacted enemy."),
    # `EB-472`. THE ORDER, on the one row where the order changes a number the
    # reader is about to plan off. "Whether Superconduct's Vulnerable applies
    # before or after the damage of the card that caused it. From the numbers
    # it applies first, and Rosaria therefore amplifies herself by 50%. That is
    # a 4-point swing on a 1-cost card and it is nowhere on the screen" (Klee
    # r15 run 2 (c) 4). It applies FIRST: `ElementalHit.Deal` resolves the
    # reaction and only then reads `SimDamagePipeline.TargetMods`, which
    # `tier0/tests/test_reaction_phase_parity.py` pins -- and the clause is the
    # C#'s own, added to `KLEEMOD-SUPERCONDUCT_PREVIEW` in the same commit, so
    # the tooltip and this page cannot say different things about it.
    "Superconduct": ("Electro on a Cryo aura, or Cryo on an Electro aura. The "
                     "reacted enemy gains 2 Vulnerable, which applies before "
                     "this hit."),
    # `EB-357`: AND WHAT IT LOOKS LIKE ON THE PANEL. The dot is the game's own
    # Poison stack, so it prints as `Poison N`, the stacks add (3, 10, 13 on
    # one Eel), and it ticks before the enemy acts; the entry said none of
    # that and the r5 seat could not price a tick from it.
    # `EB-665` PUT THE DEBUFF'S NAME IN THE FIRST CLAUSE, in the C# and here
    # in one commit. The panel row and the preview named two different things
    # -- `Poison 4` on the body, "loses 4 HP" on the preview -- and the r24
    # lane-1 seat could not tell which number was which.
    # TEXT PASS 2026-09-25: the in-game preview stops at "gains 4 Poison",
    # because Poison's own tip rides beside it there. This page has no Poison
    # row to ride, so it keeps the tick clause the preview dropped.
    "Electro-Charged": ("Hydro on an Electro aura, or Electro on a Hydro "
                        "aura. The reacted enemy gains 4 Poison, losing that "
                        "much HP at the start of its turn, 1 less each turn. "
                        "On its panel that is the "
                        "Poison stack: stacks add, and it ticks before the "
                        "enemy acts."),
    # `EB-366` SPLIT THE BOSS CLAUSE OFF THIS ROW. See `FROZEN_BOSS_CLAUSE`.
    # `EB-517` PUT THE WINDOW ON IT, in the C# and here in one commit: the two
    # clauses read as independent riders and are one, because the freeze ticks
    # down at the end of the turn the halved action is taken on.
    "Frozen": ("Hydro on a Cryo aura, or Cryo on a Hydro aura. Its next "
               "action deals 50% less damage. Until it acts, the next Attack "
               "on it Shatters for 6 unblockable damage."),
    # `EB-465`'s two, and they are the mod's own preview sentences the way the
    # six above are. `Swirl` is `ARM_KEYWORDS`' row VERBATIM rather than a
    # second copy of it, because ten Universals print the word as a verb and
    # one screen must not carry two definitions of it.
    "Swirl": ARM_KEYWORDS["Swirl"],
    # `EB-613` (R263 sec.5 item 1). THE BLOCK IS NOT THE POINT OF THIS ROW;
    # THE AURA IS. A Geo hit is a COST to a reaction deck, and the seats
    # already sequence around it -- "Gorou must come after the Electro hit or
    # its Crystallize eats the aura the reaction needs" (Kokomi r5 run 3),
    # under the heading "element ordering is the deepest decision this deck
    # has, and it is entirely undocumented". The clause is the C#'s own, moved
    # in the same commit, so the tooltip and this page cannot say different
    # things about it.
    "Crystallize": ("Geo on any aura: "
                    f"gain {CRYSTALLIZE_BLOCK} Block. The aura is consumed."),
}

# `EB-428`. THE SIX ROWS FILLED 40% OF A SCREEN THAT COULD FIRE NONE OF THEM.
#
# FOUR SEATS, ONE SENTENCE. "The glossary is about 40% of the screen text and
# 0% of the gameplay until a Cryo card happens to show up in a reward" (Kokomi
# r11; Klee r10 and r11 and Kokomi r10 said the same). A deck that owns ONE
# element cannot react at all -- an element meeting its own aura refreshes it,
# which the umbrella row says -- so nine rows of table were being read past on
# every battle screen of four runs, and the words a reader did need were below
# them.
#
# THE PAIR IS THE GATE, and it is a fact this page already has: each of the six
# names its two elements in its own first clause, and the three sources a
# second element can come from are all on the screen -- the FACES this page
# prints (hand, the remembered deck, a reward, a shelf, the belt), the AURAS on
# the board, and any printed `Applies X` text. So a row prints when both of its
# elements are in reach and not otherwise.
#
# THE UMBRELLA ROW ALWAYS PRINTS, because it is not a reaction: it is the aura
# rule, and a mono-element deck needs it MORE than a mixed one -- "a hit
# matching the aura refreshes it" is the sentence that explains why its Hydro
# never does anything. When no pair is reachable it carries one extra clause
# saying so, which is the row's "otherwise one line".
#
# ANY TWO DISTINCT ELEMENTS ARE A REACTION -- the four pair six ways and all
# six are here -- so "no pair reachable" is exactly "fewer than two elements in
# reach", and the clause can say which one without a search.
REACTION_ELEMENTS: dict[str, frozenset[str]] = {
    "Melt": frozenset({"Pyro", "Cryo"}),
    "Vaporize": frozenset({"Pyro", "Hydro"}),
    "Overloaded": frozenset({"Pyro", "Electro"}),
    "Superconduct": frozenset({"Electro", "Cryo"}),
    "Electro-Charged": frozenset({"Hydro", "Electro"}),
    "Frozen": frozenset({"Hydro", "Cryo"}),
}

# `EB-465`. THE TWO THAT PAIR WITH NOTHING AND REACT WITH EVERYTHING.
#
# Anemo and Geo leave no aura of their own, so neither appears in the table
# above and neither can ever be half of a pair. `ReactionTable.For` checks them
# FIRST and against no partner at all -- "Trigger-only elements are checked
# first: they react with ANY aura" -- so their reachability test is a different
# one: the element in reach, and an aura standing on a body NOW.
#
# NOW, NOT REMEMBERED. The six are about what a DECK can draw, so they ride the
# fight's memory of every element seen; a trigger element is about what is on
# the board this instant, because a Swirl with nothing to spread does nothing
# and the keyword's own last clause says so.
#: `EB-675`. The umbrella row on a screen that can reach no reaction: what the
#: word means and nothing else. The eight sentences it replaces are the aura
#: rules, every one of them about a beat this board cannot produce.
REACTION_UNREACHABLE_ROW = (
    "A hit of a different element than the aura an enemy is already wearing.")

SPREAD_REACTIONS: dict[str, str] = {"Swirl": "Anemo", "Crystallize": "Geo"}

# `EB-537`. THE REACTION WORDS AS THEY ARE PRINTED, so a screen that NAMES one
# defines it whether or not the deck could reach it. Case-sensitive and
# word-bounded, `_ARM_KEYWORD_RE`'s discipline: the game capitalises a keyword
# wherever it prints one, and the haystack is the observation's printed values
# rather than this page's own prose. The umbrella is not here -- it is raised
# by the element census with its own no-reaction clause, and a second copy
# would print the paragraph twice on a screen that has both.
_REACTION_WORD_RE: dict[str, "re.Pattern[str]"] = {
    word: re.compile(rf"\b{re.escape(word)}\b")
    for word in REACTION_KEYWORDS if word != "Elemental Reaction"
}
#: The umbrella, printed. Asked only where the census above did not already
#: define it (2026-09-25 evening, `keyword_notes`).
_UMBRELLA_WORD_RE = re.compile(r"\bElemental Reactions?\b")

# `EB-547`. A SALON MEMBER IS AN ELEMENT SOURCE, and the census could not see
# one.
#
# THE FIND (Furina r13 lane 2). "NO REACTION IS REACHABLE HERE: Pyro is the only
# element this screen can supply" printed on a screen with `Salon Debut` -- a
# card whose whole body is "Deploy Mademoiselle Crabaletta" -- in the hand. The
# seat: "it was wrong in the most direct way available; the Hydro that broke the
# claim was a card in the hand printed underneath it", and it broke the claim
# two plays later.
#
# WHY THE THREE SOURCES MISSED IT. `EB-428`'s census reads a card's own
# `element` indicator, an aura on a body, and the printed phrase `Applies X`. A
# deploy card has none of the three: the element is the MEMBER's, and the member
# supplies it on arrival because a deploy performs.
#
# MATCHED ON THE MEMBER'S NAME, which is the one handle every surface carries --
# the deploy card's face names her and the member tip is titled with her. The
# Usher is absent on purpose and it is not an omission: he performs BLOCK and
# supplies no element at all, so a screen holding only his deploy really can
# reach nothing.
SALON_MEMBER_ELEMENTS: dict[str, str] = {
    "Crabaletta": "Hydro",
    "Chevalmarin": "Hydro",
}

#: The surname alone, word-bounded and case-sensitive, `_ARM_KEYWORD_RE`'s
#: discipline: the game capitalises a member's name wherever it prints one, and
#: the full stage name and the short one both end in it.
_SALON_MEMBER_RE = {
    name: re.compile(rf"\b{name}\b") for name in SALON_MEMBER_ELEMENTS
}

_ELEMENTS = ("Pyro", "Hydro", "Electro", "Cryo")
#: The trigger elements, in reach on the same three sources as the four above:
#: `EB-454` put both words in `_ELEMENT_KEYWORD`, so a face carries them.
_SPREAD_ELEMENTS = tuple(sorted(set(SPREAD_REACTIONS.values())))
#: The game's own phrase for a card that supplies an element, matched in any
#: printed body -- a potion's rule and a relic's read the same way a card's
#: keyword does, and the belt is one of the three sources the row names.
_APPLIES_RE = re.compile(
    r"\bApplies (Pyro|Hydro|Electro|Cryo|Anemo|Geo)\b")
#: `AuraPower.Localization` writes `("title", $"{Element} Aura")`, which is
#: the same handle `_is_aura` reads and the only one this side of the line has.
_AURA_NAME_RE = re.compile(r"^(Pyro|Hydro|Electro|Cryo) Aura$")

# `EB-366`. THE BOSS SUBSTITUTION, PRINTED IN A BOSS ROOM AND NOWHERE ELSE.
#
# WHAT THE SEAT SAW (Furina reframe round 1, the Elite fight, round 5): a Cryo
# hit onto a Hydro aura on Byrdonis, an ELITE, under a printed line reading
# "Bosses cannot be Frozen: Hydro plus Cryo is consumed and applies 2
# Vulnerable instead" -- and Byrdonis froze. The rule was right and the page
# was wrong: the substitution is `RoomType.Boss AND not a Minion`, so it has
# nothing to say about an elite, and stating it unconditionally told a seat
# that the freeze it was about to get could not happen.
#
# So the clause is appended by the ROOM, off the wire's own `state_type` --
# "monster", "elite" or "boss" (`McpMod.StateBuilder`, from the encounter's own
# `RoomType`) -- which is the same fact the mod's predicate reads. The minion
# half rides with it, because in a boss room it is the half that decides which
# body in front of you freezes.
FROZEN_BOSS_CLAUSE = (" Bosses can't be Frozen, so a boss gains 2 "
                      "Vulnerable instead. A Minion beside the boss still "
                      "Freezes.")

# The room the boss substitution applies in, off the wire's `state_type`.
BOSS_ROOM = "boss"

# The number the card's own Bomb tip prints, where a screen carries that tip.
# `ArmKeywordTips.ForBomb` builds it as "... when Set off. Grows <n> at the
# start of your turn" (text pass 2026-09-25), so this is an exact read of
# the game's own sentence and never a guess at what a stray numeral near the
# word Bomb might have meant.
# `EB-340` reads the rate off the SCREEN's own Bomb tip so the page quotes
# what this build prints rather than what tier0 believes. The pattern follows
# the tip's wording, capital G and all: a card face says "grows by N".
_BOMB_GROWTH_RE = re.compile(
    r"\bGrows (\d+) at the start of your turn\b")


def _every_string(blob: Any):
    """Every string anywhere in a finished observation, values only."""
    if isinstance(blob, str):
        yield blob
    elif isinstance(blob, dict):
        for value in blob.values():
            yield from _every_string(value)
    elif isinstance(blob, list):
        for value in blob:
            yield from _every_string(value)


# `EB-404`. THE KEYS THAT HOLD A NAME RATHER THAN A RULE.
#
# THE DEFECT. The page glossed `Deploy` -- "A member joins and performs at
# once" -- on a screen holding `Freminet - Pers, Deploy!`, whose printed body
# is "Deal 6 damage". The word was in the card's TITLE. The Furina round-4 seat
# played it six times waiting for a member to join, and read the card as broken
# (run 1, (c) 2).
#
# A TITLE IS NOT A RULE. A card is named by its flavour and ruled by its body:
# `Freminet - Pers, Deploy!` names a character's move and deploys nothing,
# `Spark Strike` may charge no Sparks, and a body that really carries the rule
# prints the word where the rule is. So the glossary's haystack is every
# printed string on the screen EXCEPT the ones that name a thing -- card and
# option titles, creature names, relic and potion names, map labels.
#
# `title` AND NOT `name`, AND THE DIFFERENCE IS THE RULE. In a finished
# observation `title` is the key that holds a CARD's or a potion's printed name
# -- `_card_face`, `blindplay_faces.py:137` -- and holds nothing else. A power
# row's `name` is the game's own BADGE, which is a printed rule in force and
# not flavour: `Bomb 6` on an enemy means there is a Bomb on the board, and
# `test_the_word_is_found_wherever_the_screen_prints_it` pins that it defines
# the word. So the badge stays in and the card title comes out.
#
# THE OTHER SOURCES ARE UNAFFECTED and that is the boundary. `_wire_keyword_rows`
# reads tips the game itself hung on a power, `_elements_on_screen` reads two
# computed fields, and the LEAK GUARD (`_every_string`, above) must keep
# sweeping titles -- a sprite tag in a card's NAME is exactly what it is for.
# Only the word-match haystack narrows.
_TITLE_KEYS = frozenset({"title"})


def _creature_names(obs: dict[str, Any]) -> list[str]:
    """Every body the page NAMES on this screen, yours and theirs."""
    combat = obs.get("combat") or {}
    rows = list((combat.get("enemies") or []))
    rows += list((combat.get("pets") or []))
    return [str(row.get("name") or "") for row in rows
            if isinstance(row, dict) and row.get("name")]


def _bomb_hay(word: str, hay: str, obs: dict[str, Any]) -> str:
    """The haystack ONE arm word is matched against (`EB-744`).

    THE FIND (round two, sec.4): "a Bomb row beside a Gas Bomb". `Gas Bomb` is
    a base-game ENEMY, and a creature's `name` is in the glossary's haystack on
    purpose -- `_TITLE_KEYS` keeps a power's badge in, because `Bomb 6` on a
    body means there is a Bomb on the board. A monster called one means nothing
    of the kind, and a Furina seat with no Bomb in the game read Klee's whole
    charge rule on every screen the Gas Bomb stood on.

    SO THE WORD IS KEYED OFF THE BOARD AND THE FACES, not off a body's name:
    the names this screen prints are struck out of the haystack before the
    match, which leaves a Bomb POWER's badge, a card that places one and an
    enemy rule that mentions one all still raising the row. Every other word is
    matched against the haystack unchanged -- this is one word's defect and not
    a new rule for the table.
    """
    if word != "Bomb":
        return hay
    for name in _creature_names(obs):
        hay = hay.replace(name, " ")
    return hay


def _body_strings(blob: Any):
    """Every printed string of an observation that is a RULE, not a title."""
    if isinstance(blob, str):
        yield blob
    elif isinstance(blob, dict):
        for key, value in blob.items():
            if key in _TITLE_KEYS:
                continue
            yield from _body_strings(value)
    elif isinstance(blob, list):
        for value in blob:
            yield from _body_strings(value)


def _elements_on_screen(obs: dict[str, Any]) -> bool:
    """Does this screen show an aura, or a card that bears an element?

    `EB-340`'s trigger, and it is deliberately the WIDER of the two halves: a
    reaction has to be readable while the combination is still being BUILT, so
    a Cryo card in hand against a bare board asks the question as much as a
    Pyro aura already on a body does. Read off the two fields the page itself
    computes -- `element` (`_element`, the card's own indicator keyword) and
    a power tagged `aura` (`_is_aura`) -- so a screen kind added tomorrow gets
    the rule for free, exactly as `keyword_notes` does.
    """
    def walk(blob: Any) -> bool:
        if isinstance(blob, dict):
            if str(blob.get("element") or "").strip():
                return True
            if str(blob.get("kind") or "").strip().lower() == "aura":
                return True
            return any(walk(v) for v in blob.values())
        if isinstance(blob, list):
            return any(walk(v) for v in blob)
        return False
    return walk(obs)


def _reachable_elements(obs: dict[str, Any]) -> set[str]:
    """The elements this screen can supply, from the three sources `EB-428`
    names: the FACES it prints, the AURAS on the board, and any printed
    `Applies X`.

    THE FACES ARE EVERY FACE, which is what makes the belt and the remembered
    deck free: `element` is computed by `_card_face` for anything the page
    prints as a card, so a hand, a reward row, a shop shelf and `EB-342`'s
    remembered deck all answer the same way. A potion or a relic that carries
    no `element` field still answers through its printed rule, because
    `Applies Pyro` is the game's own phrase and it is written out in the body.

    THE AURA IS READ OFF THE BADGE, `_is_aura`'s handle: an aura on any body,
    yours or theirs, is one half of a pair already standing on the board.
    """
    found: set[str] = set()
    # Draft 3 (2026-09-25): on the Stage arm no performer applies Hydro, so a
    # performer's NAME supplies no element there; the Hydro now comes from
    # cards, which answer through their own faces.
    members_supply = not _stage_arm(obs)
    # `EB-707`: THE DECK'S AND THE POWERS', off the observation's own carried
    # field. `blindplay_faces.deck_elements` reads the four piles and every
    # status row on the board -- the deck a card will be drawn from, and a
    # power whose rule names an element -- so this answer is about the RUN
    # rather than about the seven cards this turn happens to print. Nothing
    # here prints a pile; only the element set crosses.
    found.update(e for e in (obs.get("deck_elements") or [])
                 if e in _ELEMENTS or e in _SPREAD_ELEMENTS)

    def walk(blob: Any) -> None:
        if isinstance(blob, dict):
            element = str(blob.get("element") or "").strip()
            if element in _ELEMENTS or element in _SPREAD_ELEMENTS:
                found.add(element)
            aura = _AURA_NAME_RE.match(str(blob.get("name") or "").strip())
            if aura and str(blob.get("kind") or "").strip().lower() == "aura":
                found.add(aura.group(1))
            for value in blob.values():
                walk(value)
        elif isinstance(blob, list):
            for value in blob:
                walk(value)
        elif isinstance(blob, str):
            found.update(_APPLIES_RE.findall(blob))
            # `EB-547`: and a Salon member named anywhere on the screen -- on a
            # deploy card's face, on her own tip, or on the stage line -- is
            # the element she performs with, because a deploy performs the
            # member it fields at once.
            for name, pattern in _SALON_MEMBER_RE.items():
                if members_supply and pattern.search(blob):
                    found.add(SALON_MEMBER_ELEMENTS[name])

    walk(obs)
    # AND EVERY ELEMENT THIS FIGHT HAS ALREADY SHOWN. A screen is one turn and
    # a deck is a fight; see `_FIGHT_MEMORY`'s header for why the union is the
    # honest reading rather than the generous one.
    return remember_elements(found)


def _aura_on_board(obs: dict[str, Any]) -> bool:
    """Is an elemental aura standing on a body RIGHT NOW? (`EB-465`)

    The same badge `_is_aura` reads and `_reachable_elements` matches on, asked
    of the screen rather than of the fight: a trigger element needs an aura in
    front of it this instant, and one consumed two turns ago is not one.
    """
    def walk(blob: Any) -> bool:
        if isinstance(blob, dict):
            if (str(blob.get("kind") or "").strip().lower() == "aura"
                    and _AURA_NAME_RE.match(
                        str(blob.get("name") or "").strip())):
                return True
            return any(walk(v) for v in blob.values())
        if isinstance(blob, list):
            return any(walk(v) for v in blob)
        return False
    return walk(obs)


def _no_reaction_clause(reach: set[str], aura: bool = False) -> str:
    """`EB-428`'s "otherwise one line", and it says WHY rather than only that.

    A reader told "no reaction is reachable" and nothing else cannot act on
    it. The clause names the element it has, which turns the six missing rows
    into a shopping list: one card of any other element brings a reaction back,
    and the umbrella sentence above already says what an element meeting its
    own aura does instead.

    `EB-465` GAVE THE TRIGGER ELEMENTS THEIR OWN HALF. An Anemo card in hand is
    not a fifth element to pair off -- it is a reaction waiting on an aura, and
    a reader holding one needs to be told which of the two halves is missing.
    Where the hand reaches Anemo or Geo and no body wears an aura, the clause
    says so beside the pair half, because the two are different shopping lists.
    """
    tail = (" The rules above and the six reactions print in full on the "
            "first screen that reaches a second element.")
    pairs = sorted(reach & set(_ELEMENTS))
    spread = sorted(reach & set(_SPREAD_ELEMENTS))
    reasons: list[str] = []
    if len(pairs) == 1:
        only = pairs[0]
        reasons.append(f"{only} is the only element this screen can supply, "
                       f"and {only} meeting a {only} aura refreshes it rather "
                       f"than reacting")
    elif not pairs:
        reasons.append("this screen supplies no element at all")
    if spread and not aura:
        reasons.append(f"{' and '.join(spread)} reacts with any aura already "
                       f"standing, and no enemy is wearing one")
    return " NO REACTION IS REACHABLE HERE: " + "; ".join(reasons) + "." + tail


def _wire_keyword_rows(blob: Any) -> list[dict[str, str]]:
    """Every keyword tip the WIRE hung on a power, name and body.

    `EB-340`. THE ENEMY ANNOUNCED A WORD THE SCREEN WOULD NOT DEFINE. The r7b
    act-3 seat met `Galvanic 6 (buff) -- Powers are afflicted with Galvanized`
    on the one turn whose decision is "do I install my engine", and the
    glossary under it defined `Bomb`, `Set off` and `Spark` and not
    `Galvanized`. Two rounds later the SAME word arrived correctly defined --
    under a card, because a card's keywords are printed beneath its face and a
    power's were read off the wire and dropped.

    They are on the feed: `BuildPowersState` emits `keywords` per status row
    (`BuildHoverTips` of every tip that is not the power's own), which is the
    same shape a card face carries. So a word an enemy's buff line prints is
    read into the glossary the way a card's is -- the game's own tip text,
    never a sentence invented here, and nothing at all where the feed carries
    none.

    POWERS ONLY, and that is the whole scope: a CARD's keywords are already
    printed under the card that declares them (`_render_card`), and lifting
    those into the glossary as well would print every one of them twice.
    """
    out: list[dict[str, str]] = []
    if isinstance(blob, dict):
        for key, value in blob.items():
            if key == "powers" and isinstance(value, list):
                for power in value:
                    if not isinstance(power, dict):
                        continue
                    for k in power.get("keywords") or []:
                        if isinstance(k, dict) \
                                and str(k.get("name") or "").strip() \
                                and str(k.get("text") or "").strip():
                            out.append({"name": str(k["name"]).strip(),
                                        "text": str(k["text"]).strip()})
            else:
                out += _wire_keyword_rows(value)
    elif isinstance(blob, list):
        for value in blob:
            out += _wire_keyword_rows(value)
    return out


def keyword_notes(obs: dict[str, Any]) -> list[dict[str, str]]:
    """The words this screen prints, each with one definition.

    ONCE PER SCREEN and in the arms' own order, however many faces printed the
    word -- a definition repeated under every card in a hand is a page a reader
    stops reading. It is computed over the whole finished observation MINUS its
    titles (`EB-404`), so a word that reaches the page through a card's body,
    an enemy's badge, a power's text, a relic's or a potion's rule or a reward
    row is defined the same way, and a word that is only somebody's NAME
    defines nothing.

    FIVE SOURCES, IN THIS ORDER (`EB-340`, extended by `EB-367` and `EB-377`):

      the ARMS' words, matched on the text of the screen, unchanged since
        `EB-272` except that `Bomb` now carries its growth number;
      the BASE GAME's words whose own tip is not what the word DOES
        (`GAME_KEYWORDS`), matched the same way;
      the REACTIONS, on any screen showing an aura or an element-bearing card,
        because a reaction is a rule about a board rather than a word printed
        on it and the seat that cannot see it cannot price a combination;
      the WIRE's own tips off a POWER row, which reach the page nowhere else;
      the BASE GAME's status and enchantment words (`BASE_KEYWORDS`), LAST,
        because the four rows above carry the game's own sentences and this
        one carries a restatement -- so it fills a hole and never overwrites.

    A word already defined by an earlier source is not defined twice, and the
    arms' own copies win: they are the sentences held in step with the C#.

    `EB-366`: the reaction rows are room-aware in exactly one place. Frozen's
    boss substitution is a rule about a BOSS ROOM, so it prints in one and
    nowhere else -- an elite that is about to freeze must not be read a line
    saying it cannot.
    """
    # `EB-404`: BODIES AND PRINTED RULES, NEVER TITLES -- see `_body_strings`.
    # `EB-407`: AND THE METER NAMES, which are dict KEYS and so reach no value
    # walk, while the page prints every one of them as a row of its own. The
    # word this row was filed for is a meter's name, and a screen that prints
    # `Encore: 4` prints the word.
    meters = ((obs.get("combat") or {}).get("you") or {}).get("meters") or {}
    hay = "\n".join(list(_body_strings(obs)) + list(meters))
    growth = _BOMB_GROWTH_RE.search(hay)
    # `EB-460`: ONE OF THESE ROWS IS ARM-CONDITIONAL. The stage half of
    # `Companion` is Furina's rule, so it rides a Furina run and nothing else;
    # every other arm gets the definition and the reward slot, which are true
    # on all of them.
    stage = _fold(obs.get("character")) == _STAGE_CHARACTER
    # `EB-744`: and which of Furina's two kits is on the board, because the
    # shipped Salon sentence is false under the Stage and the Encore row is a
    # rule for a meter the arm never grants.
    arm = _stage_arm(obs)
    # `EB-504`: and two rows are the ARM's outright. A word whose rule belongs
    # to a character this run is not playing prints its name and no rule.
    who = _fold(obs.get("character"))
    rows = [{"name": word,
             # `EB-583`: an off-arm word takes `_OFF_ARM_KEYWORD`'s sentence
             # and never an empty string. A bare name in a block of
             # definitions is what the r15 seat read as "an empty definition".
             "text": _OFF_ARM_KEYWORD[word]
             if (who and _ARM_KEYWORD_CHARACTER.get(word, who) != who) else
             ARM_KEYWORDS[word].format(
                 growth=int(growth.group(1)) if growth else BOMB_GROWTH)
             + ((COMPANION_STAGE_ARM_CLAUSE if arm
                 else COMPANION_STAGE_CLAUSE)
                if stage and word == "Companion" else "")
             # `EB-728`: and `Fanfare` is the other word both kits print. The
             # arm's row is a performer's bar; off the arm it is Furina's own
             # meter, which `METER_RULES` states beside it -- and the shipped
             # seat was reading the arm's rule next to the shipped meter's.
             if not (word == "Fanfare" and not arm)
             else FANFARE_SHIPPED_ROW}
            for word, pattern in _ARM_KEYWORD_RE.items()
            # `EB-744`: a word the ARM retires is not defined on an arm page.
            # The Encore row is the one -- Encore has no job under the Stage
            # (brief sec.2, R269) and since `EB-745` nothing grants it -- and a
            # rule for a meter that cannot move is the noise round two filed.
            if not (arm and word in _STAGE_RETIRED_KEYWORDS)
            # 2026-09-25: and a word only the ARM defines prints on an arm
            # page alone -- the performers share the shipped members' names.
            and (arm or word not in _STAGE_ONLY_KEYWORDS)
            # `EB-753`: and a word another kit OWNS is not defined at all on
            # this run's screens. The match on a Klee reward screen was the
            # English word `Spend` in a Spark sink's own prose, not the Stage's
            # keyword, so there is no off-arm sentence to print either.
            and _arm_owns(word, who)
            # Round four: Ousia and Pneuma print only beside Arkhe Alignment.
            and _anchored(word, obs)
            and pattern.search(_bomb_hay(word, hay, obs))]
    # 2026-09-25: the Summon row is the variant this screen's faces owe.
    for row in rows:
        if row["name"] == "Summon" and _arm_owns("Summon", who):
            row["text"] = _summon_row(hay)
    rows += [{"name": word, "text": GAME_KEYWORDS[word]}
             for word, pattern in _GAME_KEYWORD_RE.items()
             if pattern.search(hay)]
    if _elements_on_screen(obs):
        # `EB-428`: the umbrella row always, the six only where the screen can
        # supply both of a pair. The umbrella is not a reaction -- it is the
        # aura rule, and a mono-element deck needs it most -- so when nothing
        # is reachable it carries the one line saying so instead.
        boss = str(obs.get("state_type") or "") == BOSS_ROOM
        reach = _reachable_elements(obs)
        live = [word for word in REACTION_KEYWORDS
                if word in REACTION_ELEMENTS
                and REACTION_ELEMENTS[word] <= reach]
        # `EB-465`: and the two that need an aura instead of a partner. The
        # sentence below can no longer contradict a preview on the same screen,
        # because the preview raises on exactly this board state.
        aura = _aura_on_board(obs)
        if aura:
            live += [word for word, element in SPREAD_REACTIONS.items()
                     if element in reach]
        # `EB-675`. AND WHERE NOTHING IS REACHABLE, THE ONE LINE ALONE.
        #
        # `EB-428` already stopped the six from printing at a mono-element
        # deck; what stayed was the UMBRELLA -- eight sentences of aura rules
        # -- printed above the clause saying none of it can happen here. "In
        # nine fights I never saw one, never had a way to cause one, and read
        # ~15 lines about them on every single screen" (Kokomi r26 lane 1,
        # (c) 10). Same complaint four seats made about the six, same answer:
        # the rules for a mechanic this board cannot reach sit above the words
        # a reader does need.
        #
        # THE ONE LINE IS STILL A DEFINITION, because the word is on the
        # screen and this page does not print a name with nothing after it
        # (`EB-583`); what it is not is the full rules, and the clause's tail
        # says where those come back.
        rows.append({"name": "Elemental Reaction",
                     "text": REACTION_KEYWORDS["Elemental Reaction"] if live
                     else (REACTION_UNREACHABLE_ROW
                           + _no_reaction_clause(reach, aura))})
        # A word an arm row already defined is not defined twice: `Swirl` is
        # printed as a verb by ten Universals and carries an `ARM_KEYWORDS` row
        # of its own, which is this row's sentence.
        named = {row["name"] for row in rows}
        rows += [{"name": word,
                  "text": REACTION_KEYWORDS[word]
                  + (FROZEN_BOSS_CLAUSE if boss and word == "Frozen" else "")}
                 for word in live if word not in named]
    # `EB-537`. A WORD A FACE ON THIS SCREEN PRINTS IS DEFINED, REACHABLE OR
    # NOT, and this is the rule the block above needs beside it rather than
    # inside it. `EB-428`'s census answers "can this DECK build the pair", and
    # that is the right question for a row the page raises on its own
    # initiative -- six reactions listed at a mono-element deck is the noise it
    # was filed on. It is the WRONG question for a word the screen is already
    # showing the reader: Freminet's power printed `Shatter` at a seat whose
    # run had no Cryo, and an offered card whose one mechanic is undefined
    # cannot be priced at all, which is the decision the reward screen is
    # asking for.
    #
    # OUTSIDE `_elements_on_screen`, deliberately: an offer screen may carry no
    # element at all and still print the word, which is exactly the r19 board.
    named = {row["name"] for row in rows}
    rows += [{"name": word, "text": REACTION_KEYWORDS[word]}
             for word, pattern in _REACTION_WORD_RE.items()
             if word not in named and pattern.search(hay)]
    # 2026-09-25 evening. AND THE UMBRELLA WORD TOO, where a face prints it.
    # `Courtroom Drama` ("Your first Elemental Reaction each turn ...") was
    # offered and held with the term never defined on any screen the seat
    # saw: the umbrella rides only the element census above, and a reward
    # screen or a hand whose cards bear no element never raises it. Where it
    # is printed and the census did not define it, it gets the one-line
    # definition -- `EB-675`'s row, which claims nothing about reach.
    if ("Elemental Reaction" not in {row["name"] for row in rows}
            and _UMBRELLA_WORD_RE.search(hay)):
        rows.append({"name": "Elemental Reaction",
                     "text": REACTION_UNREACHABLE_ROW})
    seen = {row["name"] for row in rows}
    for row in _wire_keyword_rows(obs):
        if row["name"] in seen:
            continue
        seen.add(row["name"])
        rows.append(row)
    # `EB-377`, last: a base word the screen NAMES and nothing above defined.
    for word, pattern in _BASE_KEYWORD_RE.items():
        if word not in seen and pattern.search(hay):
            seen.add(word)
            rows.append({"name": word, "text": BASE_KEYWORDS[word]})
    return rows


# ---------------------------------------------------------------------------
# `EB-607`. HOW THE GAME ARRIVED AT THE NUMBER ON THE ICON.
#
# THE FIND (Klee r23 lane 1 (c) 3). "Fossil Stalker read 12 before and after I
# gave it Strength 3, while Corpse Slug's number moved." The first half of this
# row printed the game's own `GetIntentLabel` unchanged and named the pair
# where an icon and its sentence disagree -- a DETECTOR, which fires after the
# fact. The arithmetic itself is the bridge's, and it is on the wire now:
# `Hook.ModifyDamage`'s base, its folded answer, the repeat count, and the
# models the game folded in -- which the game's own
# `AttackIntent.GetSingleDamage` computes and throws away.
#
# TWO LINES AND NOT ONE, because the two questions a reader has are different.
# The FOLD line says where the number came from, and it prints only where
# something was folded: an icon that is its own base is the ordinary case, and
# a line under every intent saying "nothing was folded" would be noise. The
# TOTAL line says what the whole move delivers if every hit lands, and prints
# only on a multi-hit, because that is the multiplication the r23 seat and the
# `PER_HIT_NOTE` reader are both doing by hand.
#
# NOTHING HERE IS RECOMPUTED. Every number on these lines is one the bridge
# read off the game; the page multiplies nothing and predicts nothing, which is
# the standing rule that keeps a printed line from disagreeing with the icon
# four words to its left.
INTENT_FOLD_CLAUSE = ("the game folded {modifiers} into that: it is {base} on "
                      "the move and {folded} after")
INTENT_FOLD_NOTHING = ("nothing on the board is folded into that number: it "
                       "is the {base} the move itself declares")
INTENT_TOTAL_CLAUSE = "{folded} x {repeats} is {total} if every hit lands"

#: `EB-323`. The wire's own answer to whose side a part is on, read off the
#: game's `IntentType`. Printed where the bridge sends it; the older
#: locally-derived `BUFF_INTENT_CLAUSE` is what a feed that sends nothing gets.
INTENT_TARGET_SIDE = ("this part lands on {side}, and the feed carries no "
                      "target for an intent part, so this page cannot say "
                      "which body")

# ---------------------------------------------------------------------------
# `EB-349` / `EB-611`. WHAT RESOLVED THIS TURN, AND WHAT EACH HIT DID.
#
# THE STANDING FACT this closes is further up this file, in `AUTO_TURN_NOTE`:
# "there is no record of a card resolving on the wire at all". Every screen the
# bridge sends is an after-state, so a relic that plays a turn for you left a
# board and no turn (Vakuu: six openings, five from an empty hand -- Kokomi r4d
# act 3, 1), and a multi-hit random `Set off` told a seat which bodies were hit
# and never the order (Klee r23 lane 2 (c) 3).
#
# THE EMPTY LIST IS THE FINDING ON AN AUTO-PLAYED TURN, which is why this
# section prints its empty state where the relic-answer section does not: a
# turn the game took for you files no rows of yours, and "nothing of yours has
# resolved" beside the auto-played row is the pair that tells a reader the
# empty hand in front of them is the price of a relic and not a fault.
#
# ONE LINE PER HIT AND NOT PER BODY, `EB-518`'s rule one card over: four
# entries reading `Rapid Fire 6` divide among a hallway more than one way, and
# the beat that does not add up is the one that struck the same body twice.
# Numbered, because the ORDER is the whole of `EB-611`.
RESOLUTIONS_HEADING = "## What you played this turn, and what it did"
RESOLUTION_ROW = "- **{card}**{clauses}"
RESOLUTION_HIT_ROW = "  {n}. **{target}** -- {amount}"
RESOLUTION_HIT_BLOCKED = " (and {blocked} onto Block)"
RESOLUTION_HIT_ALL_BLOCKED = "  {n}. **{target}** -- all {blocked} onto Block"
RESOLUTION_NO_HITS = "  Nothing this page can count landed off it."
#: 2026-09-25 (opus-furina-l2b, (c) 4). The same line on a board with a
#: stage, where "nothing countable" was false under every Raise: what a card
#: did to a performer's bar is filed on the stage log, and this says where.
RESOLUTION_NO_HITS_STAGE = ("  No hit on an enemy landed off it. What it did "
                            "to your stage is on the stage log above.")
#: 2026-09-25 evening: WHO A RANDOM SUMMON ROLLED, on the card's own row. The
#: section printed Take the Stage, Understudy and Double Casting with no
#: performer, and the seat had to find the arrival on the stage log.
RESOLUTION_SUMMONED = "  It summoned {names}."
#: A body that DIED inside the play. The game never hands a killing hit to the
#: damage hook the ledger reads, so a kill arrives with no number, and the
#: first wording printed it as "Nothing this page can count landed off it"
#: under the Strike that had just emptied its target (three seats,
#: 2026-09-24). The ledger's own entry sits in hit order.
RESOLUTION_HIT_KILLED = ("  {n}. **{target}** -- killed (the feed carries no "
                         "number for a killing hit)")
#: The same fact read off the board, where the ledger did not file it: the
#: body stood on the screen before this card and is gone from the one after.
#: No place in the hit order is claimed, because none is known.
RESOLUTION_KILLED = ("  Killed {targets}: standing on the screen before this "
                     "card, gone after it.")
NO_RESOLUTIONS_THIS_TURN = (
    "- Nothing has resolved on your turn yet. A card you played would be "
    "listed here with what each of its hits did.")
#: On a row the GAME played rather than the reader: the game's own
#: `CardPlay.IsAutoPlay`, not a guess about which relic holds the controller.
RESOLUTION_AUTO_CLAUSE = " *(the game played this one, not you)*"
#: `EB-710`'s clause, on this ledger. Same window, same words.
RESOLUTION_CARRIED_CLAUSE = " *(since you ended your last turn)*"
#: A card whose hits ran past what one row will hold. Said rather than
#: silently truncated, because a reader adding up forty lines that should be
#: forty-three has been handed the `EB-518` error in a new place.
RESOLUTION_OVERFLOW_CLAUSE = " *(more hits landed than this page will list)*"
#: Printed under the section when every row on it was played by the game --
#: the turn the reader never saw, with its contents on the page at last.
RESOLUTION_AUTO_TURN_NOTE = (
    "*The rows above are the turn the game took for you: what it played, what "
    "it aimed at, and what each hit did. An empty hand or unspent energy on "
    "the board below is that turn, not a fault.*")

# ---------------------------------------------------------------------------
# `EB-374`. THE REWARD SCREEN'S OTHER BUTTON, BY NAME.
#
# THE FIND (Klee r9, act 2). Pael's Wing adds a SACRIFICE option to a card
# reward, and two rewards in that run printed `choose` and `skip` and nothing
# else. `CARD_REWARD_ALTERNATIVE_NOTE` above is what the page could honestly
# say while the words were not on the feed. They are on it now
# (`BuildCardRewardState` sends `alternatives`), so the caveat comes off where
# the words arrive and the button is named instead.
#
# THE VERB IS `sacrifice` AND IT IS NOT A SYNONYM FOR `skip`. `skip` presses
# the screen's FIRST alternative, which is what it has always pressed and what
# every policy and soak caller sends; `sacrifice` presses the one whose words
# are not a plain skip. Where there is only a plain skip the verb refuses and
# says so, rather than pressing the skip under another name.
REWARD_ALTERNATIVES_HEADING = "## Instead of choosing a card"
REWARD_ALTERNATIVE_ROW = "- **{name}** -- say `{verb}`"
REWARD_ALTERNATIVE_UNNAMED = (
    "- There is another button on this screen and the game's data feed does "
    "not say what it is. `skip` presses it.")
NO_SACRIFICE_HERE = ("this screen offers no alternative but the plain skip, "
                     "and `skip` is the verb for that")
NO_ALTERNATIVE_AT_ALL = "this card reward offers no alternative to choosing"

# ---------------------------------------------------------------------------
# `EB-350`. THE GRID THAT PRINTED TWENTY-FIVE ROWS WHATEVER THE DECK WAS.
#
# THE FIND (Kokomi r4d act 2, 10; act 3, 4 and 5). The shop's Card Removal grid
# printed exactly 25 rows against a 38-card deck and again against a 29-card
# one, and a Klee seat routed into an Elite at 2/62 unseen because the screen
# it planned on was not the deck. The 25 was a VIEWPORT: `NCardGrid` is
# virtualised, and the bridge was walking the holders that happened to fit.
#
# THE BRIDGE SENDS THE WHOLE GRID NOW, so the rows are the grid. What is left
# is the other half of the row -- the Smith's "not on this list" model, kept on
# the removal screen: a card in the deck and not on the grid is a card the game
# will not remove, which is a rule about the deck and not a hole in the page.
#: The reason itself lives in `blindplay_board.NOT_REMOVABLE`, beside the
#: upgrade grid's three, because that is where the subtraction happens.
#: Printed where the bridge could not read the grid's own list and the page is
#: back on the viewport walk. It says which of the two a reader is looking at,
#: because "these are all the cards" and "these are the cards that fit" are
#: different claims and the second under the first's heading is the r4d defect.
GRID_INCOMPLETE_NOTE = (
    "*This page could not read the whole grid off this screen's data feed, so "
    "the list above is the rows the screen has drawn and not necessarily "
    "every card the grid holds.*")

# ---------------------------------------------------------------------------
# `EB-447`. THE DECK IS THE RUN'S OWN DECK NOW.
#
# Every deck list this page printed outside a fight was RECONSTRUCTED from the
# union of four combat piles, and the caveat beside it said so: "your deck as
# it stood in the last fight". The bridge sends `Player.Deck` -- the master
# list the game's own Deck screen draws -- on every screen, so where that key
# is present the caveat is simply wrong, and this prints instead.
DECK_IS_THE_RUNS_OWN = (
    "*This is the run's own deck list, off this screen's own data feed, and "
    "it is current as of this screen.*")
