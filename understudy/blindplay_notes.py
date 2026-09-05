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
                                        COMPANION_SPARK, COMPANION_SPARK_MAX,
                                        CRYSTALLIZE_BLOCK,
                                        FRAIL_BLOCK_PCT, VULNERABLE_TAKEN_PCT,
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
    "relic's own option. The relic's printed words are on your relic row in "
    "the next fight.*")

PICKED_MARK = "PICKED"
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

# `EB-329`, the fight-ended half. The round-5 act-1 seat banked two Plans for
# an exactly lethal morning and wrote: "the next screen was the reward screen
# -- the two Plans killed it at the top of turn 3 as computed". Computed, and
# never confirmed: a morning that ends the fight is the one morning no battle
# screen is ever drawn for. The mod now records its line on the way out
# (`KokomiPlan.ResolveEntry`'s finally) and the bridge sends the record on a
# screen with no combat behind it, so the receipt has somewhere to land.
LAST_MORNING_NOTE = (
    "*The fight is over. This is the last thing the Bake-Kurage carried out "
    "in it -- printed here because a Plan whose kill ends a fight never "
    "reaches a battle screen.*")

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
ENEMY_HANDLE_NOTE = (
    "*Each enemy keeps its letter and its number for the whole fight: a body "
    "that dies does not renumber or re-letter the ones still standing, and a "
    "summon takes the next free letter. Either handle aims a card -- "
    "`on \"B\"` is the same body as the full name beside it.*")

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

PLAN_HYDRO_NOTE = ("- Every planned HIT is the jellyfish's, and it is a Hydro "
                   "hit: it leaves a Hydro aura, or reacts with the aura "
                   "already there. A Plan that blocks, draws or applies a "
                   "debuff leaves no aura.")

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
ARM_KEYWORDS: dict[str, str] = {
    # "EACH" IS `EB-340`'s, and it stays: the act-1 seat found growth is
    # +{growth} PER BOMB (Bomb 5 + Bomb 8 -> 21, not 17) and no wording said
    # so. In game the badge carries that fact ("Bombs here: N, growing each
    # turn"); the seat page has no badge, so the glossary says it per Bomb.
    # `EB-373` REWROTE THE SECOND SENTENCE: the C# folds exactly two things
    # off the target -- its Vulnerable, and whichever power sets the lowest
    # damage cap -- so "the enemy's debuffs" was a rule the r9 seat priced
    # two fights off and lost both reads (a Slow 50 enemy took 48 from a pile
    # printing 46; a Flutter 5 enemy took a 27 Bomb whole). Both debuffs say
    # "from Attacks", and a Bomb's hit is not an Attack.
    # `EB-361` ADDED THE LAST SENTENCE, in step with `ArmKeywordTips.ForBomb`:
    # a Bomb whose enemy dies moves to a survivor at its size, and three
    # round-10 seats met that rule for the first time as a stack they could
    # not account for. The page says it in the tip's own words, "Kills move
    # it on", because the glossary is pinned to the C# text word for word.
    # `EB-536` ADDED THE MINE. "Goes off only when Set off" sat directly
    # above the Mine row, which says a Mine also goes off before its enemy's
    # hit, so two rows of one glossary contradicted each other and the Klee r19
    # lane-2 seat said so. Same sentence as `ArmKeywordTips.ForBomb`.
    "Bomb": ("A charge on an enemy: each grows {growth} a turn, goes off "
             "only when Set off, or as a Mine. Not an Attack: only Vulnerable "
             "and a cap move it. Kills move it on."),
    # `EB-432`: the order INSIDE the pile, which nothing printed. `SetOff`
    # walks the charges in placement order and the first one through the
    # funnel meets the aura, because every reaction consumes it -- the r11
    # run-2 seat got that rule only by arithmetic ("Bombs go off in placement
    # order, and the first one is the one that eats the Melt"). "Oldest first"
    # is "one at a time" plus the order, in the same room.
    # `EB-443`: the two facts the Bomb tip's "not an Attack" left to
    # inference. The explosion passes `ignoreBlock: false`, so Block absorbs
    # it, and it lands as `Unpowered` with no dealer, so nothing keyed on
    # being hit by an Attack fires -- the r12 run-2 seat read a full-value hit
    # into Skittish 6 as "Set off ignores enemy Block" when what happened is
    # that Skittish never fired. "For its size" paid for them: the live number
    # is the badge's, which is the split `EB-343` already made.
    # `EB-490` NAMED THE CLASS INSTEAD OF THE TRIGGER. "No Attack trigger
    # fires" and "Block stops them" point opposite ways to a reader who does
    # not already know Skittish is an ON-HIT power: the r16 Klee seat planned
    # two turns around a tax it was not paying and learned the rule by autopsy
    # from a 26-HP Gardener dying to 30 points of Bomb. "No when-hit power
    # fires" is the same claim in the same room, said about the thing on the
    # enemy's status bar. Same sentence as `ArmKeywordTips.ForSetOff`.
    # `EB-516`: the AIM clause, held in step with `ArmKeywordTips.ForSetOff`.
    # A random Set off draws from the enemies already carrying one of hers,
    # and the two rows that do it (Tinder Toss, Rapid Fire) print "a random
    # enemy" and cannot say where it lands -- so the rule lives on the word,
    # the one surface both rows carry.
    "Set off": ("The target's Bombs go off first, oldest first, each a Pyro "
                "hit. Block stops them, no when-hit power fires, the first "
                "takes the aura. A random one picks a Bombed enemy first."),
    "Spark": ("Some cards cost Sparks instead of Energy, with no cap. Gone "
              "after combat."),
    # `EB-373`: a Mine IS a Bomb, so the same fold moves it and the same
    # sentence has to say so. The badge is still where the live number is.
    # `EB-436`: the old sentence said WHEN and nothing about the attack, and
    # the r12 act-1 seat read mitigation into it -- three Mines armed against
    # an elite, five went off, "every hit landed in full, 36 to 18 HP". The
    # only thing a Mine does to the hit is stop it happening, by killing the
    # attacker (`EB-336`). "Read the badge:" paid for the clause.
    "Mine": ("A Bomb that also goes off before its enemy's hit, which lands "
             "in full unless the Mine kills. Only their Vulnerable and a cap "
             "move it."),
    # `EB-329`. "OR ALL IF IT SAYS SO" IS THE HALF THE OLD SENTENCE GOT
    # WRONG, and it was reprinted on every battle screen of every run: a
    # starter, Kurage's Oath, deals its Plan to ALL enemies, and the round-5
    # act-1 seat watched one Plan take two Toadpoles and then four Phantasmal
    # Gardeners while this line said "the front enemy" and nothing else. The
    # card face was right the whole time; the word now defers to it.
    # `R250` (round-5 sec.6 pick 1) ADDED "NEVER A MINION": The Kin's
    # Followers and Queen's Torch Head Amalgam put a decoy on the leftmost
    # slot on purpose, and every single-target Plan landed on it.
    # `EB-380` FIXED THAT CLAUSE AND ADDED STRENGTH TO THE OTHER ONE. "Never a
    # Minion" is true of a SINGLE-TARGET Plan only -- an ALL Plan walks every
    # living body, decoys included, and the round-9 act-1 seat watched an
    # `Exposed Flank+` Plan land on `Eye With Teeth` while this line said it
    # could not. And the modifier clause named Vulnerable and Weak and stopped,
    # which reads as a complete list: the same seat priced `Kurage's Oath+`
    # face 4 under Vajra at Plan 10 expecting her Strength to ride it. It does
    # not -- the carry-out goes through `ElementalHit` UNPOWERED -- so the
    # clause names all three and says whose each one is.
    # `EB-538` ADDED THE CLASS A CARRY-OUT BELONGS TO, and it is the Set off
    # row's own sentence one kit over. Skittish gave no Block to a body hit by
    # Oath's and Ambush's carry-outs and 6 Block to a plain Strike on the same
    # enemy in the same fight (Kokomi r19 lane 2): a carry-out goes out through
    # `ElementalHit.Deal` as an unpowered hit with no dealer, so nothing keyed
    # on being hit can answer it. Same sentence as `ArmKeywordTips.ForPlan`.
    "Plan": ("On the Bake-Kurage, paid now; next turn: front non-Minion, or "
             "ALL, Minions too. Enemy Vulnerable counts; your Weak and "
             "Strength do not. A carry-out is not a hit: no when-hit power "
             "fires."),
    "Mend": ("Mend N: heal N HP, never above the HP you entered the fight "
             "with."),
    # `EB-377` ADDED THESE TWO, and their absence was the same defect one row
    # over rather than a decision: both have had an `ArmKeywordTips` twin since
    # R244, and neither had a page row -- so the mod defined them on a hover
    # and the blind page defined them nowhere. `Hexerei` rides eighteen faces
    # and `Swirl` is printed as a VERB by ten Universals.
    # `EB-392`: "from the witches' circle" was doing silent work -- the r12
    # run-2 seat "could not tell from any card face whether MY Companion
    # qualified" and then met a third word on the same screen. Every Hexerei
    # Companion prints the tag now, so the first sentence is a test a player
    # can run; the second names the overlap with "Klee's own", which is the
    # Spark rider's phrase.
    # `EB-535` PUT THE PAYMENT IN THE SENTENCE. "Cards of hers pay when you
    # play one" -- "pay what, to whom, and when? I played Razor four times and
    # never saw anything I could attribute to Hexerei" (Klee r19 lane 2). The
    # rule was on a different screen all along, the Companion Spark rider, and
    # the seat found it late and still could not tell whether Razor was one of
    # Klee's own. The reader clause gave up its room to the payment; the family
    # test and the ownership split stay, because those are what answer the
    # Razor question. Same sentence as `ArmKeywordTips.ForHexerei`, with the
    # two numerals the C# lifts from `KleeCompanionSpark` written out -- this
    # page has no access to the mod's constants and
    # `test_the_hexerei_line_names_the_payment_the_kit_declares` holds them in
    # step from this side.
    "Hexerei": ("A Companion card that prints the word, and Klee herself. "
                "Some are Klee's own, some are not. Playing one of hers makes "
                f"{COMPANION_SPARK} Spark, up to {COMPANION_SPARK_MAX}."),
    "Swirl": ("The enemy's aura is consumed and copied onto ALL enemies. No "
              "aura, no effect."),
    # `EB-372`. THE WORD REACHED A SEAT THAT HAD NEVER DRAFTED IT. `Grounded`
    # is a Power card of Klee's, and Kaeya's Cold-Blooded Strike is written
    # against it by name ("This turn, Grounded counts nothing as having gone
    # off"), as is the Cold-Blooded buff that card leaves behind. The r9 seat
    # met the word in both acts, held neither the Power nor a screen that
    # defined it, and read it as noise. Held in step with
    # `ArmKeywordTips.ForGrounded`.
    # `EB-516` moved the condition to the board and the tip moved with it.
    "Grounded": ("A Power that pays at the start of your turn, but only if "
                 "you have a Bomb on the field. Its card prints what "
                 "it pays."),
    # `EB-446`. THE NAME ONE CARD IS WRITTEN AGAINST AND ANOTHER GRANTS.
    # `Fischl -- Nightrider` prints "If Oz is out, he deals 5 Electro damage"
    # and cannot put him out: the Power that does is a DIFFERENT companion
    # card the r7 run never held. The seat played Nightrider five times and
    # never learned what the word meant. Held in step with
    # `ArmKeywordTips.ForOz`.
    "Oz": ("Fischl's raven, out while you hold the Power Oz, at Your Side. "
           "He hits at the end of your turn while he is out."),
    # The Furina reframe's three (slice two, R220 A). The same sentences
    # `ArmKeywordTips.ForDeploy` / `ForEvoke` / `ForDrain` print, with the two
    # numerals the C# interpolates from `FurinaReframeLaw` written out: this
    # page has no access to the mod's constants, and a seat reading it needs
    # the number rather than the name of the constant that holds it.
    # `EB-368` REWROTE THIS ROW, in step with `ArmKeywordTips.ForDeploy` and
    # for the reason the row gives: the act-2 seat played no Salon card in
    # three fights, because "joins the stage and performs at once" prices a
    # deploy as a one-shot and never says what makes a member act again. Three
    # rules in two sentences, the Bomb's shape, because the tip ceiling binds
    # on the C# side and the two copies must not fork.
    "Deploy": ("A member joins and performs at once; a full stage Evokes the "
               "front member first. Afterwards only a Companion play performs "
               "a member."),
    "Evoke": ("The member performs and leaves. Its Fanfare bonus counts 3 "
              "times and it prints 5 Fanfare. The card's Encore price pays "
              "for it."),
    "Drain": ("Your Fanfare falls to nothing. What the card does next is "
              "priced off the amount it took."),
    # `EB-407`. THE WORD PRINTED BEFORE THE PLAYER HOLDS ANY. Encore is named
    # on the Neow screen and on opening-hand faces, and the only surface that
    # stated its rule was the METER LINE -- which needs the meter to be on the
    # board. The Furina round-4 seat made the run's first decision without the
    # word (run 1, (c) 5). The sentence is `ArmKeywordTips.ForEncore`'s, and
    # the ORDER clause is the half nothing printed: the buffer
    # (`FurinaResources.AbsorbDamage`), a card's price
    # (`FurinaResourceHooks.BeforeCardPlayed`, before resolution) and a
    # member's 1 (`SalonPowers.PerformMember`, or 3/4 when it cannot pay) all
    # draw on ONE amount with no reservation and no priority, so a hit that
    # lands first leaves the member dry.
    "Encore": ("After Block it absorbs damage before HP. One pool, as each "
               "lands: a card pays to resolve, a member spends 1 to perform "
               "or acts at 3/4."),
    # `EB-329`. THE ONE WORD IN THIS TABLE THE GAME DEFINES NOWHERE, and that
    # is the finding rather than an oversight here: two cards price themselves
    # on it -- Chain of Command counts the Companion cards you played last
    # turn, The General's Banner triggers on one -- and the round-5 act-1 seat
    # met both, one on a reward and one on a shelf at 76 gold, across
    # seventeen floors on which "no screen defines" the term. So this row has
    # no `ArmKeywordTips` twin to be held in step with, and it is written
    # instead out of the two things the game does print:
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
    "Companion": ("A card titled with a character's name, a dash, then its "
                  "own. Card rewards after a fight offer a fourth, "
                  "Companion, choice."),
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

#: Whose stage it is. Matched the way `understudy/adapter.py` matches it -- on
#: the character's printed Title, case-folded -- because that is the field the
#: wire sends and a Title is not an id.
_STAGE_CHARACTER = "furina"

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
_ARM_KEYWORD_CHARACTER: dict[str, str] = {"Hexerei": "klee", "Oz": "klee"}

# One pattern per word, and they are CASE-SENSITIVE on purpose: the game
# capitalises a keyword wherever it prints one, and a case-blind `mine` or
# `plan` would define a word out of ordinary prose. The plural is the same
# word (`two Bombs`), and `Set Off` is accepted because a badge title-cases it.
_ARM_KEYWORD_RE = {
    "Bomb": re.compile(r"\bBombs?\b"),
    "Set off": re.compile(r"\bSet [Oo]ffs?\b"),
    "Spark": re.compile(r"\bSparks?\b"),
    "Mine": re.compile(r"\bMines?\b"),
    "Plan": re.compile(r"\bPlans?\b"),
    "Mend": re.compile(r"\bMends?\b"),
    # `EB-377`'s two. `Hexerei` takes no plural -- the word is a family name
    # and every face that prints it prints "a Hexerei card" -- and `Swirl` is
    # printed as a verb, so it conjugates the way `Mend` does.
    "Hexerei": re.compile(r"\bHexerei\b"),
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
    # THE THREE FURINA WORDS CARRIED A LITERAL BACKSPACE, not a word
    # boundary: `\b` inside these three patterns was the CHARACTER 0x08 and
    # not the escape, so `Deploy`, `Evoke` and `Drain` could never match any
    # screen and the reframe's glossary rows were unreachable. Nothing shipped
    # noticed because slice two is flag-off, and no pin exercised the three.
    # Hygiene, fixed in passing with `EB-329`; the pattern is now the same
    # shape as every row above it.
    "Deploy": re.compile(r"\bDeploys?\b"),
    "Evoke": re.compile(r"\bEvokes?\b"),
    "Drain": re.compile(r"\bDrains?\b"),
    # `EB-407`. NO PLURAL: the meter is never printed as one. And the pattern
    # is written with an editor rather than a shell heredoc, which is how the
    # three rows above once acquired a literal 0x08 in place of a word
    # boundary and matched nothing at all.
    "Encore": re.compile(r"\bEncore\b"),
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
GAME_KEYWORDS: dict[str, str] = {
    "Ringing": ("An enemy debuff on YOU: you can play only 1 card this turn. "
                "The first play locks every other Ringing card in hand. Cards "
                "that already carry a different affliction are never stamped "
                "and stay playable; potions, relics and end-of-turn triggers "
                "are not card plays and are untouched."),
}

_GAME_KEYWORD_RE = {
    "Ringing": re.compile(r"\bRinging\b"),
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
        "not happen. The reaction did happen -- its effect is on the body."),
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
                   "6 damage to ALL enemies and 1 Weak on the reacted "
                   "enemy."),
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
    "Electro-Charged": ("Hydro on an Electro aura, or Electro on a Hydro "
                        "aura. The reacted enemy loses 4 HP at the start of "
                        "its turn, 1 less each turn."),
    # `EB-366` SPLIT THE BOSS CLAUSE OFF THIS ROW. See `FROZEN_BOSS_CLAUSE`.
    # `EB-517` PUT THE WINDOW ON IT, in the C# and here in one commit: the two
    # clauses read as independent riders and are one, because the freeze ticks
    # down at the end of the turn the halved action is taken on.
    "Frozen": ("Hydro on a Cryo aura, or Cryo on a Hydro aura. Its next "
               "action deals half damage, and until it acts the first Attack "
               "to hit it Shatters for 6 damage."),
    # `EB-465`'s two, and they are the mod's own preview sentences the way the
    # six above are. `Swirl` is `ARM_KEYWORDS`' row VERBATIM rather than a
    # second copy of it, because ten Universals print the word as a verb and
    # one screen must not carry two definitions of it.
    "Swirl": ARM_KEYWORDS["Swirl"],
    "Crystallize": ("Geo on any aura. The aura is consumed and you gain "
                    f"{CRYSTALLIZE_BLOCK} Block."),
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
SPREAD_REACTIONS: dict[str, str] = {"Swirl": "Anemo", "Crystallize": "Geo"}

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
FROZEN_BOSS_CLAUSE = (" Bosses cannot be Frozen: Hydro plus Cryo is consumed "
                      "and applies 2 Vulnerable instead. A Minion beside the "
                      "boss still Freezes.")

# The room the boss substitution applies in, off the wire's `state_type`.
BOSS_ROOM = "boss"

# The number the card's own Bomb tip prints, where a screen carries that tip.
# `ArmKeywordTips.ForBomb` builds it as "A charge on an enemy: grows <n> a
# turn", so this is an exact read of the game's own sentence and never a guess
# at what a stray numeral near the word Bomb might have meant.
# `EB-340` reads the rate off the SCREEN's own Bomb tip so the page quotes
# what this build prints rather than what tier0 believes. `EB-343` (R248)
# rewrote that tip to fit its ceiling, so the pattern follows it: anchored
# on the tip's own opening, because a bare "grows N a turn" is a phrase a
# card face could reach one day and a wrong match here is silent.
_BOMB_GROWTH_RE = re.compile(
    r"charge on an enemy: grows (\d+) a turn\b")


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
    tail = (" Each of the six is defined again on the first screen that "
            "reaches a second element.")
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
    # `EB-504`: and two rows are the ARM's outright. A word whose rule belongs
    # to a character this run is not playing prints its name and no rule.
    who = _fold(obs.get("character"))
    rows = [{"name": word,
             "text": "" if (who and _ARM_KEYWORD_CHARACTER.get(word, who)
                            != who) else
             ARM_KEYWORDS[word].format(
                 growth=int(growth.group(1)) if growth else BOMB_GROWTH)
             + (COMPANION_STAGE_CLAUSE
                if stage and word == "Companion" else "")}
            for word, pattern in _ARM_KEYWORD_RE.items() if pattern.search(hay)]
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
        rows.append({"name": "Elemental Reaction",
                     "text": REACTION_KEYWORDS["Elemental Reaction"]
                     + ("" if live else _no_reaction_clause(reach, aura))})
        # A word an arm row already defined is not defined twice: `Swirl` is
        # printed as a verb by ten Universals and carries an `ARM_KEYWORDS` row
        # of its own, which is this row's sentence.
        named = {row["name"] for row in rows}
        rows += [{"name": word,
                  "text": REACTION_KEYWORDS[word]
                  + (FROZEN_BOSS_CLAUSE if boss and word == "Frozen" else "")}
                 for word in live if word not in named]
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
