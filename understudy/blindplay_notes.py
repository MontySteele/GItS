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

from understudy.blindplay_shape import (AURA_DURATION_TURNS, BOMB_GROWTH,
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
PLAN_HYDRO_NOTE = ("- Every planned HIT is the jellyfish's, and it is a Hydro "
                   "hit: it leaves a Hydro aura, or reacts with the aura "
                   "already there. A Plan that blocks, draws or applies a "
                   "debuff leaves no aura.")

AURA_NOTE = ("*An aura is tagged `(aura)` rather than `(buff)` or "
             "`(debuff)`, because it is neither: it is the element left "
             "clinging to a body, and it is what an Elemental Reaction needs "
             "-- a hit of a different element consumes it and reacts.*")


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
    # so. In game the badge carries that fact ("Each grows at the start of
    # your turn"); the seat page has no badge, so the glossary says it.
    "Bomb": ("A charge on an enemy: each grows {growth} a turn, goes off "
             "only when Set off, all at once. Its hit takes the enemy's "
             "debuffs, not yours."),
    "Set off": ("Every Bomb on the target goes off first, one at a time, "
                "each a Pyro hit for its size."),
    "Spark": ("Some cards cost Sparks instead of Energy, with no cap. Gone "
              "after combat."),
    "Mine": ("A Bomb that also goes off when its enemy attacks you, before "
             "the hit lands. The enemy's debuffs move it, and the badge has "
             "the number."),
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
    "Plan": ("On the Bake-Kurage, paid now; next turn: front non-Minion, or "
             "ALL, Minions too. Enemy Vulnerable counts; your Weak and "
             "Strength do not."),
    "Mend": ("Mend N: heal N HP, never above the HP you entered the fight "
             "with."),
    # `EB-377` ADDED THESE TWO, and their absence was the same defect one row
    # over rather than a decision: both have had an `ArmKeywordTips` twin since
    # R244, and neither had a page row -- so the mod defined them on a hover
    # and the blind page defined them nowhere. `Hexerei` rides eighteen faces
    # and `Swirl` is printed as a VERB by ten Universals.
    "Hexerei": ("A Companion card from the witches' circle. It does nothing "
                "by itself; Klee is one too, and her own cards pay when you "
                "play one."),
    "Swirl": ("The enemy's aura is consumed and copied onto ALL enemies. No "
              "aura, no effect."),
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
    "Companion": ("A card titled with a character's name, a dash, then its "
                  "own. Card rewards after a fight offer a fourth, "
                  "Companion, choice."),
}

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
    "Vulnerable": (
        f"The wearer takes {VULNERABLE_TAKEN_PCT}% more damage from every "
        f"hit. One stack falls off at the end of each of its turns."),
    "Weak": (
        f"The wearer deals {WEAK_DEALT_PCT}% less damage. One stack falls "
        f"off at the end of each of its turns."),
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
# seen. `Swirl` and `Crystallize` are Anemo and Geo, which NO card in this
# build supplies (`_ELEMENT_KEYWORD` reads four elements), so they stay out
# under the same rule that keeps `Tide` and `Exert` out: a page defining them
# would be teaching a rule this board does not have.
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
    "Superconduct": ("Electro on a Cryo aura, or Cryo on an Electro aura. The "
                     "reacted enemy gains 2 Vulnerable."),
    "Electro-Charged": ("Hydro on an Electro aura, or Electro on a Hydro "
                        "aura. The reacted enemy loses 4 HP at the start of "
                        "its turn, 1 less each turn."),
    # `EB-366` SPLIT THE BOSS CLAUSE OFF THIS ROW. See `FROZEN_BOSS_CLAUSE`.
    "Frozen": ("Hydro on a Cryo aura, or Cryo on a Hydro aura. Its next "
               "action deals half damage, and the first Attack to hit it "
               "Shatters for 6 damage."),
}

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
# `ArmKeywordTips.ForBomb` builds it as "Grows by <n> at the start of your
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
    stops reading. It is computed over the WHOLE finished observation, so a
    word that reaches the page through a card's body, an enemy's badge, a
    power's text, a relic, a potion or a reward row is defined the same way.

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
    hay = "\n".join(_every_string(obs))
    growth = _BOMB_GROWTH_RE.search(hay)
    rows = [{"name": word,
             "text": ARM_KEYWORDS[word].format(
                 growth=int(growth.group(1)) if growth else BOMB_GROWTH)}
            for word, pattern in _ARM_KEYWORD_RE.items() if pattern.search(hay)]
    rows += [{"name": word, "text": GAME_KEYWORDS[word]}
             for word, pattern in _GAME_KEYWORD_RE.items()
             if pattern.search(hay)]
    if _elements_on_screen(obs):
        boss = str(obs.get("state_type") or "") == BOSS_ROOM
        rows += [{"name": word,
                  "text": text + (FROZEN_BOSS_CLAUSE
                                  if boss and word == "Frozen" else "")}
                 for word, text in REACTION_KEYWORDS.items()]
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
