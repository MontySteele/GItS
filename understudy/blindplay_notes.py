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

from understudy.blindplay_shape import AURA_DURATION_TURNS, BOMB_GROWTH




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
    "Bomb": ("A charge on an enemy. Each Bomb grows by {growth} at the start "
             "of your turn. Never goes off by itself. Bombs on one enemy go "
             "off together when Set off."),
    "Set off": ("Every Bomb on the target goes off first, one at a time, "
                "each a Pyro hit for its size."),
    "Spark": ("Some cards cost Sparks instead of Energy, with no cap. Gone "
              "after combat."),
    "Mine": ("A Bomb that also goes off when its enemy attacks you, before "
             "the hit lands. Weak shrinks it like any Bomb; the badge shows "
             "the number."),
    "Plan": ("Play this on the Bake-Kurage: it carries out the Plan line at "
             "the start of your next turn. Cost is paid now. Plans hit the "
             "front enemy."),
    "Mend": ("Mend N: heal N HP, never above the HP you entered the fight "
             "with."),
    # The Furina reframe's three (slice two, R220 A). The same sentences
    # `ArmKeywordTips.ForDeploy` / `ForEvoke` / `ForDrain` print, with the two
    # numerals the C# interpolates from `FurinaReframeLaw` written out: this
    # page has no access to the mod's constants, and a seat reading it needs
    # the number rather than the name of the constant that holds it.
    "Deploy": ("A Salon member joins the stage and performs at once. Onto a "
               "full stage, the front member Evokes first."),
    "Evoke": ("The member performs and leaves. Its Fanfare bonus counts 3 "
              "times and it prints 5 Fanfare. The card's Encore price pays "
              "for it."),
    "Drain": ("Your Fanfare falls to nothing. What the card does next is "
              "priced off the amount it took."),
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
    "Deploy": re.compile(r"Deploys?"),
    "Evoke": re.compile(r"Evokes?"),
    "Drain": re.compile(r"Drains?"),
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
        "refreshes it."),
    "Melt": ("Pyro on a Cryo aura, or Cryo on a Pyro aura. The triggering hit "
             "deals 1.75x damage and consumes the aura."),
    "Vaporize": ("Pyro on a Hydro aura, or Hydro on a Pyro aura. The "
                 "triggering hit deals 1.5x damage and consumes the aura."),
    "Overloaded": ("Pyro on an Electro aura, or Electro on a Pyro aura. It "
                   "deals 6 splash damage to all enemies and applies 1 Weak "
                   "to the reacted enemy."),
    "Superconduct": ("Electro on a Cryo aura, or Cryo on an Electro aura. The "
                     "reacted enemy gains 2 Vulnerable."),
    "Electro-Charged": ("Hydro on an Electro aura, or Electro on a Hydro "
                        "aura. The reacted enemy gains a 4-damage decaying "
                        "damage-over-time effect."),
    "Frozen": ("Hydro on a Cryo aura, or Cryo on a Hydro aura. Its next "
               "action deals half damage; attacking it Shatters for 6 damage. "
               "Bosses cannot be Frozen: the pair is consumed and applies 2 "
               "Vulnerable instead."),
}

# The number the card's own Bomb tip prints, where a screen carries that tip.
# `ArmKeywordTips.ForBomb` builds it as "Grows by <n> at the start of your
# turn", so this is an exact read of the game's own sentence and never a guess
# at what a stray numeral near the word Bomb might have meant.
_BOMB_GROWTH_RE = re.compile(r"\bGrows by (\d+) at the start of your turn\b")


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

    THREE SOURCES, IN THIS ORDER (`EB-340`):

      the ARMS' words, matched on the text of the screen, unchanged since
        `EB-272` except that `Bomb` now carries its growth number;
      the REACTIONS, on any screen showing an aura or an element-bearing card,
        because a reaction is a rule about a board rather than a word printed
        on it and the seat that cannot see it cannot price a combination;
      the WIRE's own tips off a POWER row, which reach the page nowhere else.

    A word already defined by an earlier source is not defined twice, and the
    arms' own copies win: they are the sentences held in step with the C#.
    """
    hay = "\n".join(_every_string(obs))
    growth = _BOMB_GROWTH_RE.search(hay)
    rows = [{"name": word,
             "text": ARM_KEYWORDS[word].format(
                 growth=int(growth.group(1)) if growth else BOMB_GROWTH)}
            for word, pattern in _ARM_KEYWORD_RE.items() if pattern.search(hay)]
    if _elements_on_screen(obs):
        rows += [{"name": word, "text": text}
                 for word, text in REACTION_KEYWORDS.items()]
    seen = {row["name"] for row in rows}
    for row in _wire_keyword_rows(obs):
        if row["name"] in seen:
            continue
        seen.add(row["name"])
        rows.append(row)
    return rows
