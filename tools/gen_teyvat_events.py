#!/usr/bin/env python3
"""Generate the Teyvat arm's DRESSED EVENTS from the curated event faces.

WHAT THIS IS
------------
Six curated face files under `docs/current/dossiers/content/event-faces/` hold,
per nation, a dressed title/scene/option set for each base event of the zone
that nation stands in. This turns those into:

  * one C# class per (base event, face) under
    `klee-mod/KleeCode/Teyvat/Events/<Face>/` -- a one-line subclass of the
    base event's hand-written MIRROR, with no body at all;
  * the loc rows for every key those classes ask for, as a `TeyvatLoc`
    partial;
  * the `(dressing, base event type) -> dressed model` rows the
    `PullNextEvent` postfix substitutes through.

The C# SHAPE decision, and the decompile facts it rests on, are written up in
`docs/current/operations/codegen.md` under "Codegen -- Teyvat dressed events".
The short version: every base event class is `sealed` and hardcodes its own loc
keys as string literals, so a dressed event CANNOT subclass its base; what it
CAN subclass is a hand-written abstract mirror of it, and then `Id.Entry`,
`OptionKey`, `Title` and `InitialDescription` all re-derive from the dressed
class NAME for free. That is why the generated file is one line of C#.

WHAT IS NOT GENERATED
---------------------
The mirrors. A base event with no mirror in `MIRRORS` below is reported and
skipped -- that report is the engineering queue for this surface. Mirroring an
event is hand work by design: it re-implements the base game's clauses and is
read against the decompile, which no generator can do on taste.

THE INDEX
---------
`tools/data/sts2_base_events.json` carries the structural facts both this
generator and the headless pins need: per base event the class name, the
`Id.Entry`, its option key names in order, its other page keys, whether an
option can kill, and the frozen harvest's option count. IDENTIFIERS ONLY --
no method bodies, no base-game prose -- so the repo's decompiled-material rule
(`.gitignore:28`, `csharp-build-spec.md` sec.0.3) is not bent, and `--check`
never needs a decompile.

Usage
-----
    python tools/gen_teyvat_events.py             # write the active faces
    python tools/gen_teyvat_events.py --check     # fail if output would change
    python tools/gen_teyvat_events.py --refresh   # rebuild the base-event index
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parent.parent

INDEX_PATH = REPO / "tools" / "data" / "sts2_base_events.json"
FACE_DIR = REPO / "docs" / "current" / "dossiers" / "content" / "event-faces"
HARVEST = REPO / "docs" / "sts2-events-harvest.txt"
EVENTS_ROOT = REPO / "klee-mod" / "KleeCode" / "Teyvat" / "Events"
GENERATED_CS = REPO / "klee-mod" / "KleeCode" / "Teyvat" / "TeyvatEventsGenerated.cs"

#: The decompiled namespace the index is refreshed from. Not in the repo; see
#: `tools/extract_base_game_pool.py` for the ilspycmd line that produces it.
DECOMP_DEFAULT = (
    Path.home() / "AppData" / "Local" / "Temp" / "claude" / "teyvat-decomp"
    / "MegaCrit.Sts2.Core.Models.Events"
)


# ---------------------------------------------------------------------------
# The face -> dressing map.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FaceSpec:
    """One curated face, and the dressing act it lands in.

    `act` is the dressing's `Id.Entry` -- the same constant
    `KleeMod.Teyvat.TeyvatFrame` holds, and the key the `PullNextEvent`
    substitution table is looked up by. `folder` is both the output directory
    and the C# namespace leaf.

    `active` is how acts 2 and 3 wait, and the reason CHANGED when R273's acts
    landed. It used to be that their sibling ACTS did not exist, so generating
    their events would have minted classes no run could reach and a
    substitution table keyed on an act id nothing answered to. The acts exist
    now -- `TeyvatFrame` publishes six dressings, two at each of the three
    indices -- so what is left is the CONTENT: a face's mirrors have to be
    written and read before its rows are emitted, exactly as act 1's six were.
    Turning one on is this flag and its mirrors, and nothing else.
    """

    key: str
    file: str
    act: str
    folder: str
    active: bool = True


FACES: Tuple[FaceSpec, ...] = (
    FaceSpec("overgrowth-mondstadt", "overgrowth-mondstadt-2026-09-14.md",
             "MONDSTADT", "Mondstadt"),
    FaceSpec("underdocks-liyue", "underdocks-liyue-2026-09-14.md",
             "LIYUE", "Liyue"),
    # Acts 2 and 3: the acts are published (R273) and the mirrors are written.
    FaceSpec("glory-sumeru", "glory-sumeru-2026-09-14.md",
             "SUMERU", "Sumeru"),
    FaceSpec("glory-fontaine", "glory-fontaine-2026-09-14.md",
             "FONTAINE", "Fontaine"),
    FaceSpec("hive-inazuma", "hive-inazuma-2026-09-14.md",
             "INAZUMA", "Inazuma"),
    FaceSpec("hive-natlan", "hive-natlan-2026-09-14.md",
             "NATLAN", "Natlan"),
)


@dataclass(frozen=True)
class TableOption:
    """ONE OPTION KEY WHOSE FACE LINES ARE A TABLE OF WHAT IT CAN BE.

    The Future of Potions builds its INITIAL options from the player's potion
    BELT -- up to three, every one of them under the SINGLE key
    `...options.POTION`, with the per-potion words supplied at runtime as
    `LocString` vars (`Rarity` on the title; `Potion`, `Rarity` and `Type` on
    the description). The face's five lines are therefore not five options:
    they are the five rarities that ONE option can wear, and pairing them one
    to one against option keys is impossible because there is only one key.

    So the table is carried into the one key, and nothing is authored to do it:

    `choices` -- the rendered values of `var`, in the face's table order. The
    title row becomes a SmartFormat `choose` over them whose arms are the
    face's own labels in that same order, plus the first label again as the
    default arm. `ChooseFormatter` is one of the extensions
    `LocManager.InitSmartFormat` registers, and the shipped German row for
    THIS VERY KEY already uses it, so this is the base game's own device and
    not a new one.

    `slots` -- literal-for-literal substitutions applied to the FIRST line's
    outcome to produce the description row, each swapping a rarity- or
    type-specific phrase for the var the engine fills at runtime. A literal
    the face does not contain is a REFUSAL rather than a silent no-op: the
    whole point is that the dressed key ends up carrying the same vars the
    base prints.

    Page text never goes through either. A page is looked up through
    `L10NLookup`, which adds only the event's own `DynamicVars`, so a page row
    carrying `{Potion}` would be a SmartFormat call on a var nobody supplies;
    page text comes off the RAW face line.
    """

    var: str
    choices: Tuple[str, ...]
    slots: Tuple[Tuple[str, str], ...] = ()


@dataclass(frozen=True)
class DishTable:
    """THE EIGHT-DISH TABLE ENDLESS CONVEYOR CARRIES INSIDE ONE OPTION LINE.

    The grab option's key IS THE ROLLED DISH -- `...pages.ALL.options.<id>`,
    eight of them -- and each dish also needs a `DISHES.<id>.title` row, which
    is what `CalculateVars` reads into the `CurrentDishTitle` var. None of
    that can be derived from an option line, because the face writes the belt
    as ONE line with the eight dishes listed inside it.

    `source` is the paired option key whose outcome carries the table, and
    `ids` the base event's dish ids IN THE FACE'S ORDER. The generator splits
    the line's `<Name> (<effect>)` pairs and hands each dish its own name and
    its own effect -- the dish's title row and its option's two rows -- so no
    dish name is authored here and none is written in the face twice. A parse
    that does not yield exactly `len(ids)` pairs is a refusal.
    """

    source: str
    ids: Tuple[str, ...]


@dataclass(frozen=True)
class MirrorSpec:
    """One hand-written mirror, and the loc-key shape it asks for.

    `cls` alone is enough for a two-option event whose keys the index's
    literal scrape already reads correctly -- the three the spike shipped are
    all of that kind, and their rows below carry nothing else. The other
    fields exist because the scrape is a REGEX OVER STRING LITERALS and three
    kinds of base event defeat it:

    `options` -- THE FACE-PAIRED OPTION KEYS, IN THE ORDER
    `GenerateInitialOptions` BUILDS THEM, which is the order the face's
    option lines are written in. The scrape cannot produce that list: it also
    picks up the `_LOCKED` twin an event substitutes when an option is
    unaffordable (Self-Help Book has three, Tea Master two), and it reports
    literals in SOURCE order rather than list order -- Wood Carvings
    constructs the locked Snake twin first and adds it second.

    `extra_options` -- the option keys a player can be shown that have NO
    face line of their own: those `_LOCKED` twins, and the options a LATER
    PAGE offers (Dense Vegetation's `FIGHT`). Each names the paired option
    key whose text it reuses, because an unaffordable option is the SAME
    option greyed out and a later page's option is the same branch continued
    -- neither is new prose, and prose is the face's to write, not this
    file's. Both rows are emitted for every one of them: an option key is a
    PREFIX the engine suffixes with `.title` and `.description` (EB-765),
    whichever page it sits on.

    `pages` -- the non-INITIAL page keys, for an event whose keys the scrape
    cannot read. An event that builds a page key by CONCATENATION leaves the
    index a truncated stub (`SLIPPERY_BRIDGE.pages.HOLD_ON_`) that nothing
    will ever look up; the mirror's real keys are enumerated here instead.

    `page_source` -- the option line a page's text comes from, when the page
    is not named after an option. Tea Master's `DONE` page is reached from
    Bone Tea AND Ember Tea, so there is no option of that name to derive
    from and the row says which line supplies it.

    A LATER-PAGE OPTION THAT HAS A FACE LINE OF ITS OWN goes in `options`,
    spelled as a FULL SUFFIX under the entry -- `pages.ALL.options.LINGER`,
    `pages.DECIPHER.options.GIVE_UP`. It pairs by position exactly like an
    INITIAL one and is emitted at its own path rather than under
    `pages.INITIAL.options.`; in the generated `EventShape` it lands in
    `ExtraOptionKeys`, which is the list of full-suffix option keys, because
    `OptionKeys` is the list the pins prefix with `pages.INITIAL.options.`.
    This is the third of the three shapes act 1 parks on: an event whose face
    lists a later page's option inline (Tablet of Truth's Give Up, Abyssal
    Baths' Linger and Exit Baths) needs the LINE, and the line is already
    written -- what was missing was somewhere for it to pair.

    `line_pages` -- A FACE LINE THAT IS NOT AN OPTION AT ALL. The curation
    follows the wiki, and the wiki sometimes writes a rule that applies to
    EVERY option as one more bullet beside them: Battleworn Dummy's
    `(all settings)` line is the three-turn limit and the no-reward failure,
    which is not a fourth setting and has no option key waiting for it. Such a
    line still has to pair with something or the count check refuses the whole
    event, so the spec names the PAGE keys it supplies instead -- one entry per
    consumed line, each a tuple of the page keys that line's outcome is written
    to, and the lines are taken in order AFTER the `options` list. A page named
    here is not also looked up through `page_source`: the line IS the page.

    `table_option` and `dish_table` are the two shapes no pairing can reach at
    all; see their own docstrings above.
    """

    cls: str
    options: Tuple[str, ...] = ()
    extra_options: Tuple[Tuple[str, str], ...] = ()
    pages: Tuple[str, ...] = ()
    page_source: Tuple[Tuple[str, str], ...] = ()
    line_pages: Tuple[Tuple[str, ...], ...] = ()
    table_option: Optional[TableOption] = None
    dish_table: Optional[DishTable] = None


#: Slippery Bridge's eight reachable Hold On pages, and the Hold On option
#: each of them offers. `GetHoldOnSuffix` answers the hold-on ordinal below
#: seven and `LOOP` at seven or above, so a run reaches pages 0 through 6 and
#: then LOOP for ever; the option on a page carries the NEXT ordinal, which is
#: what lets its title print the next HP price. The same eight are written out
#: literally in `SlipperyBridgeMirror` -- there, so the pin that compares a
#: mirror's literals to its shape can see them; here, so the rows exist.
_HOLD_ON_STEPS: Tuple[str, ...] = ("0", "1", "2", "3", "4", "5", "6", "LOOP")


def _hold_on_pages() -> Tuple[str, ...]:
    return tuple(f"pages.HOLD_ON_{s}.description" for s in _HOLD_ON_STEPS)


def _hold_on_options() -> Tuple[Tuple[str, str], ...]:
    pairs = [(_HOLD_ON_STEPS[i], _HOLD_ON_STEPS[i + 1])
             for i in range(len(_HOLD_ON_STEPS) - 1)]
    pairs.append(("LOOP", "LOOP"))
    return tuple((f"pages.HOLD_ON_{a}.options.HOLD_ON_{b}", "HOLD_ON_0")
                 for a, b in pairs)


#: Base event class -> the hand-written abstract mirror that re-implements it.
#: THE HAND-WORK LEDGER. Everything absent from here is reported by the
#: generator as needing a mirror; adding one is a C# file under
#: `Teyvat/Events/Mirrors/` plus a row here, and every face that names the
#: event generates on the next run with no further work.
MIRRORS: Dict[str, MirrorSpec] = {
    "RoomFullOfCheese": MirrorSpec("RoomFullOfCheeseMirror"),
    "TheLegendsWereTrue": MirrorSpec("TheLegendsWereTrueMirror"),
    "ThisOrThat": MirrorSpec("ThisOrThatMirror"),

    # --- act 1, batch 1 ---------------------------------------------------
    "SelfHelpBook": MirrorSpec(
        "SelfHelpBookMirror",
        options=("READ_THE_BACK", "READ_PASSAGE", "READ_ENTIRE_BOOK", "NO_OPTIONS"),
        extra_options=(
            ("pages.INITIAL.options.READ_THE_BACK_LOCKED", "READ_THE_BACK"),
            ("pages.INITIAL.options.READ_PASSAGE_LOCKED", "READ_PASSAGE"),
            ("pages.INITIAL.options.READ_ENTIRE_BOOK_LOCKED", "READ_ENTIRE_BOOK"),
        )),
    "SlipperyBridge": MirrorSpec(
        "SlipperyBridgeMirror",
        options=("OVERCOME", "HOLD_ON_0"),
        extra_options=_hold_on_options(),
        pages=("pages.OVERCOME.description",) + _hold_on_pages()),
    "AromaOfChaos": MirrorSpec("AromaOfChaosMirror"),
    "BrainLeech": MirrorSpec("BrainLeechMirror"),
    "ByrdonisNest": MirrorSpec("ByrdonisNestMirror"),

    # --- act 1, batch 2 ---------------------------------------------------
    "DenseVegetation": MirrorSpec(
        "DenseVegetationMirror",
        options=("TRUDGE_ON", "REST"),
        extra_options=(("pages.REST.options.FIGHT", "REST"),),
        pages=("pages.TRUDGE_ON.description", "pages.REST.description")),
    "JungleMazeAdventure": MirrorSpec("JungleMazeAdventureMirror"),
    "LuminousChoir": MirrorSpec(
        "LuminousChoirMirror",
        options=("REACH_INTO_THE_FLESH", "OFFER_TRIBUTE"),
        extra_options=(
            ("pages.INITIAL.options.OFFER_TRIBUTE_LOCKED", "OFFER_TRIBUTE"),
        )),
    "MorphicGrove": MirrorSpec("MorphicGroveMirror"),
    "SapphireSeed": MirrorSpec("SapphireSeedMirror"),

    # --- act 1, batch 3 ---------------------------------------------------
    "TeaMaster": MirrorSpec(
        "TeaMasterMirror",
        options=("BONE_TEA", "EMBER_TEA", "TEA_OF_DISCOURTESY"),
        extra_options=(
            ("pages.INITIAL.options.BONE_TEA_LOCKED", "BONE_TEA"),
            ("pages.INITIAL.options.EMBER_TEA_LOCKED", "EMBER_TEA"),
        ),
        page_source=(("pages.DONE.description", "BONE_TEA"),)),
    "UnrestSite": MirrorSpec("UnrestSiteMirror"),
    "Wellspring": MirrorSpec("WellspringMirror"),
    "WhisperingHollow": MirrorSpec("WhisperingHollowMirror"),
    "WoodCarvings": MirrorSpec(
        "WoodCarvingsMirror",
        options=("BIRD", "SNAKE", "TORUS"),
        extra_options=(("pages.INITIAL.options.SNAKE_LOCKED", "SNAKE"),)),

    # --- act 1, batch 4 ---------------------------------------------------
    "DoorsOfLightAndDark": MirrorSpec("DoorsOfLightAndDarkMirror"),
    "DrowningBeacon": MirrorSpec("DrowningBeaconMirror"),
    "PunchOff": MirrorSpec(
        "PunchOffMirror",
        options=("NAB", "I_CAN_TAKE_THEM"),
        extra_options=(("pages.I_CAN_TAKE_THEM.options.FIGHT", "I_CAN_TAKE_THEM"),),
        pages=("pages.NAB.description", "pages.I_CAN_TAKE_THEM.description")),
    "SpiralingWhirlpool": MirrorSpec("SpiralingWhirlpoolMirror"),
    "SunkenTreasury": MirrorSpec("SunkenTreasuryMirror"),

    # --- act 1, batch 5 ---------------------------------------------------
    "SunkenStatue": MirrorSpec("SunkenStatueMirror"),
    "TrashHeap": MirrorSpec("TrashHeapMirror"),
    "WaterloggedScriptorium": MirrorSpec(
        "WaterloggedScriptoriumMirror",
        options=("BLOODY_INK", "TENTACLE_QUILL", "PRICKLY_SPONGE"),
        extra_options=(
            ("pages.INITIAL.options.TENTACLE_QUILL_LOCKED", "TENTACLE_QUILL"),
            ("pages.INITIAL.options.PRICKLY_SPONGE_LOCKED", "PRICKLY_SPONGE"),
        )),

    # --- act 1, batch 6: the four the pairing parked ----------------------
    # Every one of these is a face whose lines were already written and had
    # nowhere to land. Nothing below authors a line; what is new is the three
    # places a line may now land -- a later-page option key in `options`, a
    # `table_option`, and a `dish_table`.
    "TabletOfTruth": MirrorSpec(
        "TabletOfTruthMirror",
        options=("SMASH", "DECIPHER_1", "pages.DECIPHER.options.GIVE_UP"),
        extra_options=tuple(
            (f"pages.DECIPHER_{i}.options.DECIPHER", "DECIPHER_1")
            for i in range(1, 5)),
        pages=("pages.SMASH.description", "pages.GIVE_UP.description")
              + tuple(f"pages.DECIPHER_{i}.description" for i in range(1, 6)),
        page_source=(("pages.GIVE_UP.description", "pages.DECIPHER.options.GIVE_UP"),)
                    + tuple((f"pages.DECIPHER_{i}.description", "DECIPHER_1")
                            for i in range(2, 6))),
    "AbyssalBaths": MirrorSpec(
        "AbyssalBathsMirror",
        options=("IMMERSE", "pages.ALL.options.LINGER",
                 "pages.ALL.options.EXIT_BATHS", "ABSTAIN"),
        pages=("pages.IMMERSE.description", "pages.ABSTAIN.description",
               "pages.EXIT_BATHS.description", "pages.DEATH_WARNING.description")
              + tuple(f"pages.LINGER{i}.description" for i in range(1, 10)),
        page_source=(("pages.EXIT_BATHS.description", "pages.ALL.options.EXIT_BATHS"),
                     ("pages.DEATH_WARNING.description", "pages.ALL.options.LINGER"))
                    + tuple((f"pages.LINGER{i}.description", "pages.ALL.options.LINGER")
                            for i in range(1, 10))),
    "EndlessConveyor": MirrorSpec(
        "EndlessConveyorMirror",
        # The grab option pairs with the one key it has that is NOT a rolled
        # dish -- the LOCKED twin the base substitutes when the purse is
        # short, which is the grab option greyed out and so takes the grab
        # line, exactly as a `_LOCKED` twin does anywhere else. The eight
        # dishes take their names and effects from the table inside that same
        # line, through `dish_table`.
        options=("pages.ALL.options.LOCKED", "OBSERVE_CHEF",
                 "pages.GRAB_SOMETHING_OFF_THE_BELT.options.LEAVE"),
        pages=("pages.GRAB_SOMETHING_OFF_THE_BELT.description",
               "pages.OBSERVE_CHEF.description", "pages.LEAVE.description"),
        page_source=(
            ("pages.GRAB_SOMETHING_OFF_THE_BELT.description", "pages.ALL.options.LOCKED"),
            ("pages.LEAVE.description", "pages.GRAB_SOMETHING_OFF_THE_BELT.options.LEAVE"),
        ),
        dish_table=DishTable(
            "pages.ALL.options.LOCKED",
            ("CAVIAR", "CLAM_ROLL", "SPICY_SNAPPY", "JELLY_LIVER", "FRIED_EEL",
             "SUSPICIOUS_CONDIMENT", "GOLDEN_FYSH", "SEAPUNK_SALAD"))),
    "TheFutureOfPotions": MirrorSpec(
        "TheFutureOfPotionsMirror",
        options=("POTION",),
        pages=("pages.DONE.description",),
        page_source=(("pages.DONE.description", "POTION"),),
        table_option=TableOption(
            var="Rarity",
            choices=("Common", "Uncommon", "Rare", "Event", "Token"),
            # The base's English description is
            # `Lose {Potion}. Obtain an Upgraded {Rarity} {Type}.` -- three
            # vars, and these three swaps are what put the same three into
            # the dressed row without touching a word around them.
            slots=(("a specified Common potion", "{Potion}"),
                   ("Upgraded Common", "Upgraded {Rarity}"),
                   ("[Attack/Skill]", "{Type}")))),

    # --- acts 2 and 3, batch 1 -------------------------------------------
    # Five two-option events. Three of them the index's scrape already reads
    # correctly; the two that carry a spec carry it for a shape the scrape
    # cannot reach.
    "Bugslayer": MirrorSpec("BugslayerMirror"),
    "InfestedAutomaton": MirrorSpec("InfestedAutomatonMirror"),
    "SpiritGrafter": MirrorSpec("SpiritGrafterMirror"),
    # `RelicOption<T>` keys an option by the RELIC's `Id.Entry`, not by a name
    # the event writes, so neither the base event's source nor the mirror's
    # contains these two literals and the scrape reports NO option keys at
    # all. They are declared instead.
    "HungryForMushrooms": MirrorSpec(
        "HungryForMushroomsMirror",
        options=("BIG_MUSHROOM", "FRAGRANT_MUSHROOM")),
    # Return the Key's outcome page is
    # `pages.DONE.options.RETURN_THE_KEY.description` -- a page named DONE
    # with the option's name inside it, which nothing derives -- and
    # `pages.KEEP_THE_KEY.options.FIGHT` is an option only the second page
    # offers and the face writes no line for.
    "TheLanternKey": MirrorSpec(
        "TheLanternKeyMirror",
        options=("RETURN_THE_KEY", "KEEP_THE_KEY"),
        extra_options=(("pages.KEEP_THE_KEY.options.FIGHT", "KEEP_THE_KEY"),),
        pages=("pages.DONE.options.RETURN_THE_KEY.description",
               "pages.KEEP_THE_KEY.description"),
        page_source=(("pages.DONE.options.RETURN_THE_KEY.description",
                      "RETURN_THE_KEY"),)),

    # --- acts 2 and 3, batch 2 -------------------------------------------
    "Reflections": MirrorSpec("ReflectionsMirror"),
    "FieldOfManSizedHoles": MirrorSpec("FieldOfManSizedHolesMirror"),
    "LostWisp": MirrorSpec("LostWispMirror"),
    "PotionCourier": MirrorSpec("PotionCourierMirror"),
    # Pick Fight opens a second page with one option, `CONTINUE_FIGHT`, which
    # the face writes no line for -- it is the same branch continued -- and
    # whose own outcome page is `pages.CONTINUE_FIGHT.description`. The
    # scrape puts the option key in with the pages, so both lists are
    # declared.
    "RoundTeaParty": MirrorSpec(
        "RoundTeaPartyMirror",
        options=("ENJOY_TEA", "PICK_FIGHT"),
        extra_options=(("pages.PICK_FIGHT.options.CONTINUE_FIGHT", "PICK_FIGHT"),),
        pages=("pages.ENJOY_TEA.description", "pages.PICK_FIGHT.description",
               "pages.CONTINUE_FIGHT.description"),
        page_source=(("pages.CONTINUE_FIGHT.description", "PICK_FIGHT"),)),

    # --- acts 2 and 3, batch 3 -------------------------------------------
    # Both options land on the SAME page, so `page_source` says which face
    # line supplies it -- the first, as Tea Master's `DONE` takes Bone Tea's.
    "CrystalSphere": MirrorSpec(
        "CrystalSphereMirror",
        options=("UNCOVER_FUTURE", "PAYMENT_PLAN"),
        pages=("pages.FINISH.description",),
        page_source=(("pages.FINISH.description", "UNCOVER_FUTURE"),)),
    "Symbiote": MirrorSpec(
        "SymbioteMirror",
        options=("APPROACH", "KILL_WITH_FIRE"),
        extra_options=(("pages.INITIAL.options.APPROACH_LOCKED", "APPROACH"),)),
    "GraveOfTheForgotten": MirrorSpec(
        "GraveOfTheForgottenMirror",
        options=("CONFRONT", "ACCEPT"),
        extra_options=(("pages.INITIAL.options.CONFRONT_LOCKED", "CONFRONT"),)),
    # ONE locked key serves TWO options -- `CreateLockedOption` returns
    # `...options.LOCKED` for both the second and the third, where Self-Help
    # Book and Tea Master name a twin per option. So the greyed-out row has to
    # take ONE face line, and it takes Emotional Awareness's: the cheaper of
    # the two, and so the one a player sees locked first. A text choice, the
    # same shape as Tea Master's shared `DONE` page.
    "ZenWeaver": MirrorSpec(
        "ZenWeaverMirror",
        options=("BREATHING_TECHNIQUES", "EMOTIONAL_AWARENESS", "ARACHNID_ACUPUNCTURE"),
        extra_options=(("pages.INITIAL.options.LOCKED", "EMOTIONAL_AWARENESS"),)),
    # Amalgamator is one of the few base events that calls `InitialOptionKey`
    # instead of writing its literals out, so the scrape reports no option
    # keys at all and the two are declared.
    "Amalgamator": MirrorSpec(
        "AmalgamatorMirror",
        options=("COMBINE_STRIKES", "COMBINE_DEFENDS")),

    # --- acts 2 and 3, batch 4 -------------------------------------------
    "StoneOfAllTime": MirrorSpec(
        "StoneOfAllTimeMirror",
        options=("LIFT", "PUSH"),
        extra_options=(
            ("pages.INITIAL.options.LIFT_LOCKED", "LIFT"),
            ("pages.INITIAL.options.PUSH_LOCKED", "PUSH"),
        )),
    # The face's FOURTH line, `(all settings)`, is the wiki's rule bullet --
    # the three-turn limit and the no-reward failure -- and it is not a fourth
    # setting. `line_pages` gives it the two pages that rule describes.
    "BattlewornDummy": MirrorSpec(
        "BattlewornDummyMirror",
        options=("SETTING_1", "SETTING_2", "SETTING_3"),
        pages=("pages.VICTORY.description", "pages.DEFEAT.description"),
        line_pages=(("pages.VICTORY.description", "pages.DEFEAT.description"),)),
    # The option key is `...options.` + the pool's `EnergyColorName` upper-cased,
    # so the scrape sees none of the five. Declared in the FACE's order, because
    # each key is its own colour and the pairing is by NAME rather than by the
    # order `CardPoolColorOrder` builds them in.
    "ColorfulPhilosophers": MirrorSpec(
        "ColorfulPhilosophersMirror",
        options=("IRONCLAD", "SILENT", "DEFECT", "NECROBINDER", "REGENT"),
        pages=("pages.DONE.description",),
        page_source=(("pages.DONE.description", "IRONCLAD"),)),
    "RanwidTheElder": MirrorSpec(
        "RanwidTheElderMirror",
        options=("POTION", "GOLD", "RELIC"),
        extra_options=(
            ("pages.INITIAL.options.POTION_LOCKED", "POTION"),
            ("pages.INITIAL.options.RELIC_LOCKED", "RELIC"),
        ),
        pages=("pages.POTION.description", "pages.GOLD.description",
               "pages.RELIC.description")),
    "RelicTrader": MirrorSpec(
        "RelicTraderMirror",
        options=("TOP", "MIDDLE", "BOTTOM"),
        pages=("pages.DONE.description",),
        page_source=(("pages.DONE.description", "TOP"),)),

    # --- acts 2 and 3, batch 5 -------------------------------------------
    "WarHistorianRepy": MirrorSpec(
        "WarHistorianRepyMirror",
        options=("UNLOCK_CAGE", "UNLOCK_CHEST"),
        pages=("pages.UNLOCK_CAGE.description", "pages.UNLOCK_CHEST.description",
               "pages.EXTRA_UNLOCK_CAGE.description",
               "pages.EXTRA_UNLOCK_CHEST.description"),
        page_source=(("pages.EXTRA_UNLOCK_CAGE.description", "UNLOCK_CAGE"),
                     ("pages.EXTRA_UNLOCK_CHEST.description", "UNLOCK_CHEST"))),
    # The three doll pages and the shared TAKE description all come off the
    # first line, which is the one that says what taking a doll gets you. The
    # doll options themselves need no rows: their key is the RELIC's title
    # text and their words are the relic's own -- see the mirror.
    "DollRoom": MirrorSpec(
        "DollRoomMirror",
        options=("RANDOM", "TAKE_SOME_TIME", "EXAMINE"),
        pages=("pages.TAKE_SOME_TIME.description", "pages.EXAMINE.description",
               "pages.DAUGHTER_OF_WIND.description", "pages.MR_STRUGGLES.description",
               "pages.FABLE.description", "pages.TAKE.options.TAKE.description"),
        page_source=(("pages.DAUGHTER_OF_WIND.description", "RANDOM"),
                     ("pages.MR_STRUGGLES.description", "RANDOM"),
                     ("pages.FABLE.description", "RANDOM"),
                     ("pages.TAKE.options.TAKE.description", "RANDOM"))),
    # All three purchases end on `CheckObtainWongoBadge`, which picks one of
    # three AFTER_BUY pages by the player's banked Wongo Points -- so none of
    # the three is an option's own page and all three take the Bargain Bin
    # line.
    "WelcomeToWongos": MirrorSpec(
        "WelcomeToWongosMirror",
        options=("BARGAIN_BIN", "FEATURED_ITEM", "MYSTERY_BOX", "LEAVE"),
        extra_options=(
            ("pages.INITIAL.options.BARGAIN_BIN_LOCKED", "BARGAIN_BIN"),
            ("pages.INITIAL.options.FEATURED_ITEM_LOCKED", "FEATURED_ITEM"),
            ("pages.INITIAL.options.MYSTERY_BOX_LOCKED", "MYSTERY_BOX"),
        ),
        pages=("pages.AFTER_BUY.description",
               "pages.AFTER_BUY_BADGE_COUNTER.description",
               "pages.AFTER_BUY_RECEIVE_BADGE.description",
               "pages.LEAVE.description"),
        page_source=(("pages.AFTER_BUY.description", "BARGAIN_BIN"),
                     ("pages.AFTER_BUY_BADGE_COUNTER.description", "BARGAIN_BIN"),
                     ("pages.AFTER_BUY_RECEIVE_BADGE.description", "BARGAIN_BIN"))),
}


#: PARKED: BASE EVENTS A FACE NAMES THAT ARE NOT DRESSED, AND WHY.
#:
#: A park is NOT a missing mirror. The generator already reports an event with
#: no mirror, and that report is the engineering queue; these three would sit
#: on it for ever with no work attached, because the work is not engineering.
#: Each is an event whose reachable options outnumber the lines the faces
#: write, in a way `extra_options` CANNOT paper over: `extra_options` exists
#: for an option that is the same branch continued -- a `_LOCKED` twin, a
#: later page's Fight -- and borrowing a line for an option with a DIFFERENT
#: outcome would print the wrong consequences on the button.
#:
#: Dressing any of these needs new curated prose, which is the face's work and
#: [USER]'s taste, not a generator change. Listed here so the report says PARKED
#: with a reason rather than NO MIRROR with none.
PARKED: Dict[str, str] = {
    "Trial":
        "the faces write the SIX verdict options (Merchant/Noble/Nondescript "
        "x Guilty/Innocent) and no line for the INITIAL Accept/Reject pair, "
        "the Reject page's Accept and Double Down, or the three story pages. "
        "There is nothing to borrow for Accept that would not print a "
        "verdict's consequences on the summons button, and Double Down opens "
        "the abandon-run popup -- the one option in this surface where wrong "
        "text is dangerous",
    "TinkerTime":
        "the faces write the three CARD TYPES (Attack/Skill/Power), which are "
        "`pages.CHOOSE_CARD_TYPE.options.*`, and no line for the INITIAL "
        "Choose Card Type option or for any of the NINE rider effects on "
        "`pages.CHOOSE_RIDER.options.*`. The riders are nine distinct "
        "mechanical effects picked two at a time; one borrowed line across all "
        "nine would print the wrong effect on eight of them",
    "ColossalFlower":
        "the faces write TWO lines -- take the prize, dig deeper -- for a "
        "three-level dig with six reachable option keys. The two per-level "
        "repeats are the same branch continued and would borrow cleanly, but "
        "the final page's Pollinous Core branch (the relic, for 7 unblockable) "
        "and its Extract Instead sibling are distinct outcomes with no line "
        "between them",
}


# ---------------------------------------------------------------------------
# Slugs and names.
# ---------------------------------------------------------------------------

_CAMEL = re.compile(r"([a-z0-9])([A-Z])")


def slugify(name: str) -> str:
    """`StringHelper.Slugify`, for the one input shape we hand it: a C# type
    name. CamelCase gets an underscore at each lower->upper boundary and the
    whole thing is upper-cased, which is exactly what `ModelDb.GetEntry` does
    to produce an `Id.Entry`."""
    return _CAMEL.sub(r"\1_\2", name.strip()).upper()


def normalise(text: str) -> str:
    """A heading or a class name reduced to comparable letters."""
    out = re.sub(r"[^a-z0-9]+", "", text.lower())
    return out


#: WIKI HEADINGS THE NORMALISER CANNOT REACH THE CLASS NAME FROM, keyed by the
#: normalised heading and read BOTH ways -- `match_base` uses it to find the
#: class, and `refresh_index` uses its inverse to find the harvest row whose
#: option count freezes that class.
#:
#: Two, and both are the wiki's title differing from the identifier by more
#: than punctuation and an article, which is the only difference `normalise`
#: was built to absorb:
#:
#:   * `Reflections snoitcelfeR` is the wiki's rendering of the event's own
#:     mirror-writing joke; the class is plain `Reflections`.
#:   * `The Merchant___` is class `FakeMerchant` -- the identifier says the
#:     twist the title hides, and no normalisation of one produces the other.
#:     It is the event the harvest marks `<<NO OPTIONS SECTION ON PAGE>>`, so
#:     the alias exists to make that SKIP reachable rather than to dress it.
#:
#: An alias is a stated fact, not a fuzzy match: a heading that is in neither
#: the normaliser's reach nor this table stays a refusal.
HEADING_ALIASES: Dict[str, str] = {
    "reflectionssnoitcelfer": "Reflections",
    "themerchant": "FakeMerchant",
}


def match_base(heading: str, index: Dict[str, dict]) -> Optional[str]:
    """Which base event class a face's `## - [ ] <name>` heading names.

    The headings are the wiki's English titles and the classes are the game's
    identifiers, and they disagree in exactly two ways: punctuation (`This or
    That?`, `The Future of Potions_`) and a leading article (`The Sunken
    Statue` is `SunkenStatue`). Normalising both sides and retrying without a
    leading "the" settles every act-1 heading; anything left over is a refusal,
    not a guess.
    """
    want = normalise(heading)
    by_norm = {normalise(cls): cls for cls in index}
    if want in by_norm:
        return by_norm[want]
    stripped = want[3:] if want.startswith("the") else want
    for norm, cls in by_norm.items():
        bare = norm[3:] if norm.startswith("the") else norm
        if bare == stripped:
            return cls
    alias = HEADING_ALIASES.get(want)
    if alias in index:
        return alias
    return None


def class_name_from_title(title: str) -> str:
    """The dressed C# class name for a face's `### <title>` line.

    A leading article is dropped and every non-alphanumeric character with it,
    which is the rule the spike's own `SpringvaleCheeseCellar` (from "The
    Springvale Cheese Cellar") already followed. The name is the WHOLE
    identity of a dressed event -- `Id.Entry`, every loc key, the portrait
    path and the ModelDb row all derive from it -- so it is checked for
    uniqueness across faces before anything is written.
    """
    text = title.strip()
    text = re.sub(r"^(the|a|an)\s+", "", text, flags=re.IGNORECASE)
    # Apostrophes are DELETED rather than treated as word breaks, so "The
    # Guild's Standing Commission" is `GuildsStandingCommission` and not
    # `GuildSStandingCommission` -- which would slug to `GUILD_S_STANDING_...`
    # and read as a typo in every loc key the event owns.
    text = re.sub(r"[’']", "", text)
    words = re.findall(r"[A-Za-z0-9]+", text)
    return "".join(w[:1].upper() + w[1:] for w in words)


# ---------------------------------------------------------------------------
# The base-event index (--refresh).
# ---------------------------------------------------------------------------

_CLASS_RE = re.compile(r"public\s+(sealed\s+)?class\s+(\w+)\s*:\s*(\w+)")
_KILL_RE = re.compile(r"\.(ThatDoesDamage|ThatDecreasesMaxHp|ThatWillKillPlayerIf)\(")


def harvest_option_counts() -> Dict[str, object]:
    """Option counts from the frozen harvest, keyed by normalised heading.

    The value is an int, or the string "none" for an event the harvest marks
    `<<NO OPTIONS SECTION ON PAGE>>` -- The Merchant___ is the one today. That
    marker is a SKIP and not a refusal: the wiki page has no options section,
    so there is nothing for a face to disagree with.
    """
    text = HARVEST.read_text(encoding="utf-8")
    out: Dict[str, object] = {}
    for block in re.split(r"^### ", text, flags=re.M)[1:]:
        head, _, body = block.partition("\n")
        name = re.sub(r"^\[[^\]]*\]\s*", "", head).strip()
        if "<<NO OPTIONS SECTION ON PAGE>>" in body:
            out[normalise(name)] = "none"
            continue
        out[normalise(name)] = len(re.findall(r"^\s*\[", body, flags=re.M))
    return out


def refresh_index(decomp: Path) -> int:
    """Rebuild `tools/data/sts2_base_events.json` from a local decompile.

    Reads ONLY identifiers: the class name, whether it is sealed, its base
    class, the loc-key literals it contains and whether any option is marked
    lethal. No method body and no base-game string ever leaves this function.
    """
    if not decomp.is_dir():
        print(f"gen_teyvat_events: no decompile at {decomp}", file=sys.stderr)
        print("  regenerate with: ilspycmd -p -o <dir> \"<GameDir>\\...\\sts2.dll\"",
              file=sys.stderr)
        return 2

    harvest = harvest_option_counts()
    index: Dict[str, dict] = {}
    for path in sorted(decomp.glob("*.cs")):
        src = path.read_text(encoding="utf-8", errors="replace")
        m = _CLASS_RE.search(src)
        if not m:
            continue
        cls, base = m.group(2), m.group(3)
        entry = slugify(cls)
        literals = re.findall(r'"(' + re.escape(entry) + r'[^"]*)"', src)

        options: List[str] = []
        pages: List[str] = []
        prefix = entry + ".pages.INITIAL.options."
        for lit in literals:
            if lit.startswith(prefix):
                # A truncated literal (`"...options."` built up by
                # concatenation, as Colorful Philosophers and Endless Conveyor
                # do) yields an EMPTY name. It is not an option key; it is a
                # sign the event builds its keys dynamically, which
                # `dynamic_keys` already records and which keeps the event off
                # the generatable list until a mirror is written for it.
                name = lit[len(prefix):]
                if name and name not in options:
                    options.append(name)
            else:
                suffix = lit[len(entry) + 1:]
                if suffix and suffix not in pages:
                    pages.append(suffix)

        norm = normalise(cls)
        count = harvest.get(norm)
        if count is None:
            for heading_norm, alias_cls in HEADING_ALIASES.items():
                if alias_cls == cls and heading_norm in harvest:
                    count = harvest[heading_norm]
                    break
        if count is None:
            # The harvest is keyed by the wiki's title, which may carry a
            # leading article the class name drops.
            for key, value in harvest.items():
                bare = key[3:] if key.startswith("the") else key
                if bare == (norm[3:] if norm.startswith("the") else norm):
                    count = value
                    break

        index[cls] = {
            "entry": entry,
            "sealed": bool(m.group(1)),
            "base": base,
            "option_keys": options,
            "page_keys": pages,
            "can_kill": bool(_KILL_RE.search(src)),
            "dynamic_keys": any("{" in lit for lit in literals),
            "harvest_options": count,
        }

    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "_comment": (
            "GENERATED by tools/gen_teyvat_events.py --refresh from a local "
            "0.111.0 decompile of MegaCrit.Sts2.Core.Models.Events. "
            "Identifiers only -- no base-game bodies or prose (.gitignore:28)."
        ),
        "game": "0.111.0",
        "events": index,
    }
    INDEX_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n",
                          encoding="utf-8")
    print(f"gen_teyvat_events: index refreshed, {len(index)} base events "
          f"-> {INDEX_PATH.relative_to(REPO)}")
    return 0


def load_index() -> Dict[str, dict]:
    if not INDEX_PATH.exists():
        raise SystemExit(
            f"gen_teyvat_events: missing {INDEX_PATH.relative_to(REPO)}; "
            f"run with --refresh on a machine that has the decompile")
    return json.loads(INDEX_PATH.read_text(encoding="utf-8"))["events"]


# ---------------------------------------------------------------------------
# The face parser.
# ---------------------------------------------------------------------------


@dataclass
class FaceEvent:
    base_heading: str
    title: str
    subtitle: str
    body: str
    options: List[Tuple[str, str]] = field(default_factory=list)
    loss: Optional[str] = None
    line: int = 0


_OPTION_RE = re.compile(r"^-\s+\*\*(.+?)\*\*\s+[—-]\s+(.*)$")


def parse_face(path: Path) -> List[FaceEvent]:
    """Read one curated face file.

    The format is fixed by the curation pass: `## - [ ] <base event>`, then
    `### <title> - <nation> / <faction> - [literal|loose -] REUSED|DRAFTED`,
    then the scene paragraphs, then `- **<label>** - <outcome>` lines, then
    prose notes ending in `Mechanics check:`. Anything after the first option
    line that is not itself an option line is a NOTE and is not emitted: the
    notes restate the harvest for a human reader and are not player-facing
    text.

    An optional `Loss: <text>` line anywhere in the section supplies the
    `.loss` row for an event whose base can kill; without one the engine falls
    back to `DEFAULT_EVENT_LOSS_MESSAGE`, which `NRunHistory` reaches through
    `LocString.GetIfExists`.
    """
    events: List[FaceEvent] = []
    current: Optional[FaceEvent] = None
    body_lines: List[str] = []
    seen_option = False

    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.rstrip()
        if line.startswith("## ") and not line.startswith("### "):
            if current is not None:
                current.body = _join(body_lines)
                events.append(current)
            heading = re.sub(r"^##\s*-\s*\[\s*[xX ]?\s*\]\s*", "", line).strip()
            current = FaceEvent(base_heading=heading, title="", subtitle="",
                                body="", line=lineno)
            body_lines, seen_option = [], False
            continue
        if current is None:
            continue
        if line.startswith("### "):
            head = line[4:].strip()
            parts = re.split(r"\s+[—]\s+", head)
            current.title = parts[0].strip()
            current.subtitle = head
            continue
        m = _OPTION_RE.match(line)
        if m:
            seen_option = True
            current.options.append((m.group(1).strip(), m.group(2).strip()))
            continue
        if line.lower().startswith("loss:"):
            current.loss = line.split(":", 1)[1].strip()
            continue
        if not seen_option and line and not line.startswith("---"):
            body_lines.append(line)

    if current is not None:
        current.body = _join(body_lines)
        events.append(current)
    return [e for e in events if e.title]


def _join(lines: Sequence[str]) -> str:
    return " ".join(l.strip() for l in lines if l.strip()).strip()


# ---------------------------------------------------------------------------
# Emission.
# ---------------------------------------------------------------------------

BANNER = (
    "// <auto-generated>\n"
    "//     GENERATED by tools/gen_teyvat_events.py from\n"
    "//     {source}\n"
    "//     Do not edit by hand: `python tools/gen_teyvat_events.py --check`\n"
    "//     fails on any drift, and the next run overwrites it.\n"
    "// </auto-generated>\n"
)


def cs_string(text: str) -> str:
    """One C# string literal, wrapped at a readable width as a `+` chain.

    Escaped rather than verbatim so a quote in the curated prose cannot end
    the literal, and wrapped because these are two-to-five-sentence scene
    paragraphs and a single 600-column line is unreviewable.
    """
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    if len(escaped) <= 66:
        return f'"{escaped}"'
    words, lines, cur = escaped.split(" "), [], ""
    for word in words:
        if cur and len(cur) + 1 + len(word) > 66:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}" if cur else word
    if cur:
        lines.append(cur)
    out = [f'"{lines[0]} "']
    for i, chunk in enumerate(lines[1:]):
        tail = "" if i == len(lines) - 2 else " "
        out.append(f'  + "{chunk}{tail}"')
    return "\n".join(out)


@dataclass
class Dressed:
    face: FaceSpec
    base_class: str
    mirror: str
    cls: str
    entry: str
    base_entry: str
    face_event: FaceEvent
    option_keys: List[str]
    page_keys: List[str]
    can_kill: bool
    extra_options: Tuple[Tuple[str, str], ...] = ()
    page_source: Tuple[Tuple[str, str], ...] = ()
    #: The paired rows for a `table_option`, already chosen and slotted, or
    #: None for an event that pairs one line to one key.
    table_pair: Optional[Tuple[str, str, str]] = None
    #: `(dish id, dressed name, dressed effect)` for a `dish_table`.
    dishes: Tuple[Tuple[str, str, str], ...] = ()
    #: `page key -> the text of the face line that is not an option`, already
    #: resolved from the mirror's `line_pages`. Those pages take their text
    #: from here and never from `page_source`.
    line_page_text: Dict[str, str] = field(default_factory=dict)

    def _paired(self) -> Tuple[Dict[str, Tuple[str, str]], Dict[str, Tuple[str, str]]]:
        """`(emitted, raw)` -- the face's lines matched to the keys they pair
        with, twice over.

        `emitted` is what the option rows are written from; `raw` is the face
        line untouched, and it is what PAGE text is written from. They differ
        only for a `table_option`, whose emitted rows carry SmartFormat vars
        that no page's `L10NLookup` would supply.
        """
        if self.table_pair is not None:
            key, title, description = self.table_pair
            label, outcome = self.face_event.options[0]
            return ({key: (title, description)},
                    {key: (strip_base_gloss(label, key), outcome)})
        paired = {
            key: (strip_base_gloss(label, key), outcome)
            for key, (label, outcome) in zip(self.option_keys, self.face_event.options)
        }
        return paired, paired

    def option_key_path(self, key: str) -> str:
        """Where an option key's rows are written.

        A bare name is an option on the INITIAL page and the engine builds its
        key through `EventModel.OptionKey`; a key spelled as a full suffix
        under the entry is a LATER PAGE's option that happens to have a face
        line of its own, and is written where it sits.
        """
        if key.startswith("pages."):
            return f"{self.entry}.{key}"
        return f"{self.entry}.pages.INITIAL.options.{key}"

    def shape_option_keys(self) -> List[str]:
        """The INITIAL option NAMES, which is what the pins prefix with
        `pages.INITIAL.options.`."""
        return [k for k in self.option_keys if not k.startswith("pages.")]

    def shape_extra_keys(self) -> List[str]:
        """Every option key that is a FULL SUFFIX under the entry: the paired
        later-page options, the `_LOCKED` twins and the later-page options
        with no line, and a `dish_table`'s eight rolled dishes."""
        return ([k for k in self.option_keys if k.startswith("pages.")]
                + [k for k, _ in self.extra_options]
                + [f"pages.ALL.options.{did}" for did, _, _ in self.dishes])

    def shape_page_keys(self) -> List[str]:
        """Every other key the mirror hands to the loc table whole -- the page
        descriptions, and a `dish_table`'s `DISHES.<id>.title` rows, which are
        single keys rather than prefixes."""
        return list(self.page_keys) + [
            f"DISHES.{did}.title" for did, _, _ in self.dishes]

    def rows(self) -> List[Tuple[str, str]]:
        """Every loc row this dressed event needs, in key order.

        An option key is a PREFIX and the engine suffixes it twice --
        `EventModel.GetOptionTitle` is `key + ".title"` and
        `GetOptionDescription` is `key + ".description"`, and `GetIfExists`
        answers NULL for an absent key, which `EventOption`'s constructor then
        dereferences through `CharacterModel.AddDetailsTo`. A flat row per
        option is the defect that took the spike's page down to `options: []`
        (EB-765), so both rows are always written.
        """
        out: List[Tuple[str, str]] = [
            (f"{self.entry}.title", self.face_event.title),
            (f"{self.entry}.pages.INITIAL.description", self.face_event.body),
        ]
        paired, raw = self._paired()
        for key in self.option_keys:
            base = self.option_key_path(key)
            out.append((base + ".title", paired[key][0]))
            out.append((base + ".description", paired[key][1]))
        # A `dish_table`'s eight dishes: each one an option key of its own,
        # plus the `DISHES.<id>.title` row `CalculateVars` reads. Both halves
        # come out of the one face line the belt is written on.
        for did, name, effect in self.dishes:
            out.append((f"{self.entry}.pages.ALL.options.{did}.title", name))
            out.append((f"{self.entry}.pages.ALL.options.{did}.description", effect))
            out.append((f"{self.entry}.DISHES.{did}.title", name))
        # An option a player can be SHOWN but that has no face line of its
        # own -- a `_LOCKED` twin, or an option a later page offers. Both
        # rows, for the same EB-765 reason as above: the key is a prefix
        # wherever it sits, and `GetIfExists` answering null for one half is
        # what took the spike's page down to `options: []`.
        sources = dict(self.page_source)
        for key, source in self.extra_options:
            label, outcome = paired.get(source, ("", ""))
            out.append((f"{self.entry}.{key}.title", label))
            out.append((f"{self.entry}.{key}.description", outcome))
        for page in self.page_keys:
            # A page a `line_pages` entry supplies takes that face line's text
            # directly: the line IS the page, so there is no option to derive
            # it from and `page_source` is not consulted for it.
            if page in self.line_page_text:
                out.append((f"{self.entry}.{page}", self.line_page_text[page]))
                continue
            out.append((f"{self.entry}.{page}", _page_text(raw, page, sources)))
        if self.can_kill and self.face_event.loss:
            out.append((f"{self.entry}.loss", self.face_event.loss))
        return out


def strip_base_gloss(label: str, option_key: str) -> str:
    """A face's option label with its base-game gloss removed.

    The curation writes a renamed option as `Taste the Racks (Gorge)` so a
    reader can check it against the harvest. The parenthetical is EDITORIAL,
    not player-facing, and it is stripped only when it names the base event's
    own option key -- `(Gorge)` slugs to `GORGE`, so it goes; a parenthetical
    that is part of the dressing (`Broach the Wild Cask (Let Go)` names the
    base option too, and goes for the same reason) is distinguished by the
    same test and nothing else is touched.
    """
    m = re.match(r"^(.*?)\s*\(([^()]*)\)\s*$", label)
    if m and slugify_words(m.group(2)) == option_key:
        return m.group(1).strip()
    return label.strip()


def slugify_words(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", text).upper().strip("_")


def build_table_option(key: str, table: TableOption,
                       lines: Sequence[Tuple[str, str]]) -> Tuple[Tuple[str, str, str],
                                                                  List[str]]:
    """The one option key a `TableOption` collapses its face lines into.

    Returns `((key, title, description), refusals)`. The title is a
    SmartFormat `choose` over `table.var` whose arms are the face's own labels
    in the face's order, with the first repeated as the default arm -- a
    `choose` with one more output than choice takes the last as the fallback,
    which is what keeps a rarity the table does not name from being a format
    error on the page. The description is the FIRST line's outcome with each
    declared slot swapped for its var.
    """
    refusals: List[str] = []
    labels = [strip_base_gloss(label, key) for label, _ in lines]
    if any("|" in l or "{" in l or "}" in l for l in labels):
        refusals.append("a table option's label carries a `|` or a brace, "
                        "which SmartFormat's `choose` would read as syntax")
    description = lines[0][1]
    for literal, replacement in table.slots:
        if literal not in description:
            refusals.append(
                f"the table option's first line does not contain {literal!r}, "
                f"so the {replacement} var has nowhere to go")
            continue
        description = description.replace(literal, replacement)
    title = "{%s:choose(%s):%s}" % (
        table.var, "|".join(table.choices), "|".join(labels + labels[:1]))
    return (key, title, description), refusals


_DISH_RE = re.compile(r"([A-Za-z][A-Za-z' -]*?)\s*\(([^()]*)\)")


def parse_dish_table(outcome: str, ids: Sequence[str]) -> Tuple[
        Tuple[Tuple[str, str, str], ...], List[str]]:
    """The `<Name> (<effect>)` pairs a belt line lists, matched to dish ids.

    The face writes the eight dishes inside the grab option's one outcome
    sentence, after a colon; each is a dressed NAME and a parenthesised
    effect. Positional against `ids`, because a nation is free to rename every
    dish and a name match would then quietly find nothing -- the ORDER is the
    contract, and a count that disagrees is a refusal rather than a short
    table with silent blanks.
    """
    segment = outcome.split(":", 1)[1] if ":" in outcome else outcome
    found = _DISH_RE.findall(segment)
    if len(found) != len(ids):
        return (), [f"the belt line lists {len(found)} dish(es) and the mirror "
                    f"names {len(ids)}"]
    return tuple((did, name.strip(), effect.strip())
                 for did, (name, effect) in zip(ids, found)), []


def _page_text(paired: Dict[str, Tuple[str, str]], page: str,
               sources: Optional[Dict[str, str]] = None) -> str:
    """The text for a non-INITIAL page key.

    A page key is `pages.<OPTION>.description` (the outcome screen the option
    leads to) or `pages.<OPTION>.selectionScreenPrompt` (the grid header).
    Both are derived from the face's own option line rather than authored
    here: the outcome sentence IS the page description, and the prompt
    restates the option's label. `<OPTION>` is the BASE event's key, and
    `paired` is that key already matched to this face's line by position --
    the same pairing the option rows are written from, so a page description
    and its option can never come from different lines.
    """
    tail = page[len("pages."):] if page.startswith("pages.") else page
    option, _, kind = tail.partition(".")
    # A page that is not named after an option -- Tea Master's `DONE`, which
    # Bone Tea and Ember Tea both land on -- says in the mirror's spec which
    # option line supplies it, because there is nothing to derive.
    option = (sources or {}).get(page, option)
    label, outcome = paired.get(option, ("", ""))
    if kind == "selectionScreenPrompt":
        return label or option.replace("_", " ").title()
    return outcome or label


def dressed_class_source(item: Dressed, face_file: str) -> str:
    return (
        BANNER.format(source=f"docs/current/dossiers/content/event-faces/{face_file}")
        + "\n"
        + "using KleeMod.Teyvat.Events.Mirrors;\n"
        + "\n"
        + f"namespace KleeMod.Teyvat.Events.{item.face.folder};\n"
        + "\n"
        + "/// <summary>\n"
        + f"/// {item.face_event.title} -- {item.base_class}, dressed for "
        + f"{item.face.folder}.\n"
        + "///\n"
        + f"/// {item.face_event.subtitle}\n"
        + "///\n"
        + "/// NOTHING MECHANICAL IS HERE AND THERE IS NOWHERE FOR IT TO BE. The\n"
        + f"/// base event's clauses are in <see cref=\"{item.mirror}\"/>, written\n"
        + "/// once and shared by every nation that dresses this event; this class\n"
        + "/// is a NAME. `ModelDb.GetEntry` slugifies it into\n"
        + f"/// `{item.entry}`, `EventModel.Title` and `InitialDescription`\n"
        + "/// derive from that, and `EventModel.OptionKey` slugifies\n"
        + "/// `GetType().Name` -- so every loc key the mirror asks for is already\n"
        + "/// this dressing's. The rows are in `TeyvatLoc.GeneratedEventRows`.\n"
        + "/// </summary>\n"
        + f"public sealed class {item.cls} : {item.mirror}\n"
        + "{\n"
        + "}\n"
    )


def generated_cs_source(items: Sequence[Dressed]) -> str:
    rows: List[str] = []
    for item in items:
        rows.append(f"            // {item.cls} ({item.face.folder} / {item.base_class})")
        for key, value in item.rows():
            rows.append(f'            ["{key}"] =')
            body = cs_string(value)
            rows.append("\n".join("                " + l.strip() if i else "                " + l
                                  for i, l in enumerate(body.splitlines())) + ",")
    portraits = "\n".join(
        f'            ["{item.entry}"] =\n'
        f'                "res://images/events/{item.base_entry.lower()}.png",'
        for item in items
    )
    subs = "\n".join(
        f"            [(TeyvatFrame.{_frame_const(item.face.act)}, typeof({item.base_class}))] =\n"
        f"                () => ModelDb.Event<Events.{item.face.folder}.{item.cls}>(),"
        for item in items
    )
    shapes = "\n".join(
        "            [typeof(Events.{face}.{cls})] = new EventShape(\n"
        "                \"{base_entry}\", \"{mirror}\",\n"
        "                {opts},\n"
        "                {pages},\n"
        "                {extra},\n"
        "                {kill}),".format(
            face=item.face.folder, cls=item.cls,
            base_entry=item.entry, mirror=item.mirror,
            opts=_cs_array(item.shape_option_keys()),
            pages=_cs_array(item.shape_page_keys()),
            extra=_cs_array(item.shape_extra_keys()),
            kill="true" if (item.can_kill and item.face_event.loss) else "false")
        for item in items
    )
    return (
        BANNER.format(source="docs/current/dossiers/content/event-faces/*.md")
        + "\n"
        + "using System;\n"
        + "using System.Collections.Generic;\n"
        + "using MegaCrit.Sts2.Core.Models;\n"
        + "using MegaCrit.Sts2.Core.Models.Events;\n"
        + "\n"
        + "namespace KleeMod.Teyvat;\n"
        + "\n"
        + _generated_loc_doc()
        + "internal static partial class TeyvatLoc\n"
        + "{\n"
        + "    internal static readonly IReadOnlyDictionary<string, string> GeneratedEventRows =\n"
        + "        new Dictionary<string, string>(StringComparer.Ordinal)\n"
        + "        {\n"
        + "\n".join(rows) + "\n"
        + "        };\n"
        + "}\n"
        + "\n"
        + _generated_table_doc()
        + "internal static class TeyvatGeneratedEvents\n"
        + "{\n"
        + "    /// <summary>What a dressed event's mirror asks the loc table for:\n"
        + "    /// the INITIAL option key names, in the base event's order; the\n"
        + "    /// other page keys; and `ExtraOptionKeys`, the option keys that\n"
        + "    /// are not on the INITIAL page or have no face line of their own\n"
        + "    /// -- a `_LOCKED` twin, or an option a later page offers. An\n"
        + "    /// extra key is a full suffix under the entry and is a PREFIX\n"
        + "    /// like any option key: `.title` and `.description` both. Read\n"
        + "    /// by the headless pins, which check the key set against the\n"
        + "    /// merged rows without constructing a model.</summary>\n"
        + "    internal sealed record EventShape(\n"
        + "        string BaseEntry,\n"
        + "        string Mirror,\n"
        + "        IReadOnlyList<string> OptionKeys,\n"
        + "        IReadOnlyList<string> PageKeys,\n"
        + "        IReadOnlyList<string> ExtraOptionKeys,\n"
        + "        bool HasLossRow);\n"
        + "\n"
        + "    /// <summary>Dressed event type -> its shape.</summary>\n"
        + "    internal static readonly IReadOnlyDictionary<Type, EventShape> Shapes =\n"
        + "        new Dictionary<Type, EventShape>\n"
        + "        {\n"
        + shapes + "\n"
        + "        };\n"
        + "\n"
        + "    /// <summary>(dressing act entry, base event type) -> the dressed\n"
        + "    /// model that stands in for it at pull time. Consumed by\n"
        + "    /// `Patches/PullNextEventPatch`; see that file for why the\n"
        + "    /// substitution happens downstream of the shuffle.</summary>\n"
        + "    internal static readonly IReadOnlyDictionary<(string Dressing, Type BaseEvent), Func<EventModel>> Substitutions =\n"
        + "        new Dictionary<(string, Type), Func<EventModel>>\n"
        + "        {\n"
        + subs + "\n"
        + "        };\n"
        + "\n"
        + _portrait_doc()
        + "    internal static readonly IReadOnlyDictionary<string, string> Portraits =\n"
        + "        new Dictionary<string, string>(StringComparer.Ordinal)\n"
        + "        {\n"
        + portraits + "\n"
        + "        };\n"
        + "}\n"
    )


def _portrait_doc() -> str:
    return (
        "    /// <summary>\n"
        "    /// A dressed event's `Id.Entry` -> the image the default event layout\n"
        "    /// draws for it until one of its own is supplied (EB-764).\n"
        "    ///\n"
        "    /// `EventModel.InitialPortraitPath` is `ImageHelper.GetImagePath(\n"
        "    /// \"events/\" + Id.Entry.ToLowerInvariant() + \".png\")` -- DERIVED from\n"
        "    /// the id, `private`, and not virtual -- so a dressed event asks the\n"
        "    /// pack for a path nothing produces and `NEventLayout.InitializeVisuals`\n"
        "    /// threw `AssetLoadException` before the page was drawn. The value is the\n"
        "    /// BASE event's own image, which is the same borrowing\n"
        "    /// `TeyvatFrame.AssetAlias` makes for a dressing's backgrounds, and it\n"
        "    /// retires the same way: `Patches/EventPortraitPatch` asks\n"
        "    /// `ResourceLoader.Exists` of the DRESSED path first, so a real portrait\n"
        "    /// dropped at `events/&lt;dressed entry&gt;.png` wins with no code change.\n"
        "    ///\n"
        "    /// GENERATED, so a dressed event cannot exist without a portrait row --\n"
        "    /// which is exactly the shape EB-764 was.\n"
        "    /// </summary>\n"
    )


def _cs_array(values: Sequence[str]) -> str:
    """A C# `string[]` literal, or `Array.Empty<string>()` when there is
    nothing in it -- `new[] { }` does not compile."""
    if not values:
        return "Array.Empty<string>()"
    return "new[] { " + ", ".join(f'"{v}"' for v in values) + " }"


def _frame_const(act: str) -> str:
    return act.capitalize()


def _generated_loc_doc() -> str:
    return (
        "/// <summary>\n"
        "/// THE DRESSED EVENTS' LOC ROWS, generated from the curated faces.\n"
        "///\n"
        "/// EVERY KEY IS THIS ARM'S OWN. A `LocTable.MergeWith` is GLOBAL and\n"
        "/// overwrites, so a row whose key drifted onto a base event's family\n"
        "/// would silently rewrite the shipped game's text -- and the `events`\n"
        "/// table has no dressed-key trick to fall back on the way the monster\n"
        "/// names do. Every key below is prefixed with a DRESSED `Id.Entry`,\n"
        "/// which no base event has, and a pin asserts it.\n"
        "///\n"
        "/// AN OPTION KEY IS A PREFIX, NOT A STRING (EB-765). `EventOption`'s\n"
        "/// constructor reads `GetOptionTitle(key)` and `GetOptionDescription(key)`\n"
        "/// -- `key + \".title\"` and `key + \".description\"` -- and `GetIfExists`\n"
        "/// answers NULL for an absent key, which `AddLocVars` then dereferences.\n"
        "/// The generator writes both rows for every option, always.\n"
        "/// </summary>\n"
    )


def _generated_table_doc() -> str:
    return (
        "/// <summary>\n"
        "/// THE GENERATED TABLES the arm's two readers consult: the shape a\n"
        "/// dressed event's mirror has, and the substitution the `PullNextEvent`\n"
        "/// postfix makes. Both are generated from the same face files and the\n"
        "/// same base-event index as the classes and the rows above, so the\n"
        "/// three cannot disagree about what a dressing contains.\n"
        "/// </summary>\n"
    )


# ---------------------------------------------------------------------------
# The plan.
# ---------------------------------------------------------------------------


@dataclass
class Plan:
    items: List[Dressed] = field(default_factory=list)
    refusals: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    no_mirror: List[str] = field(default_factory=list)
    parked: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


def build_plan() -> Plan:
    index = load_index()
    harvest = harvest_option_counts()
    plan = Plan()
    claimed: Dict[str, str] = {}

    for face in FACES:
        if not face.active:
            continue
        path = FACE_DIR / face.file
        if not path.exists():
            plan.refusals.append(f"{face.key}: no face file at {path.relative_to(REPO)}")
            continue
        for event in parse_face(path):
            base = match_base(event.base_heading, index)
            if base is None:
                plan.refusals.append(
                    f"{face.key}: '{event.base_heading}' (line {event.line}) names no "
                    f"base event in {INDEX_PATH.relative_to(REPO)}")
                continue

            info = index[base]
            want = info.get("harvest_options")
            if want is None:
                want = harvest.get(normalise(base))
            if want == "none":
                plan.skipped.append(
                    f"{face.key}: {base} -- the harvest marks it "
                    f"<<NO OPTIONS SECTION ON PAGE>>, nothing to dress")
                continue
            mismatch = (
                f"{face.key}: {base} -- the face gives {len(event.options)} option(s) "
                f"(line {event.line}) and the harvest freezes {want}"
                if isinstance(want, int) and want != len(event.options) else None)

            # A MISMATCH ON AN EVENT WITH NO MIRROR IS A NOTE, NOT A REFUSAL,
            # and the difference is what the count is FOR. The count check
            # exists to stop a face's option lines being paired with the wrong
            # base option keys; an event with no mirror is not generated at
            # all, so there is no pairing to get wrong and nothing to refuse.
            # Some harvest entries also count a multi-page event's later-page
            # options inline (Abyssal Baths lists Linger and Exit Baths beside
            # the two INITIAL options), so a mirror-less mismatch is as often
            # the harvest's shape as the face's -- and it is settled when the
            # mirror is written and the event becomes generatable, which is
            # exactly when the refusal below starts biting.
            if base in PARKED:
                plan.parked.append(f"{face.key}: {base} ({event.title}) -- {PARKED[base]}")
                continue

            spec = MIRRORS.get(base)
            if spec is None:
                note = f" [option count {len(event.options)} vs harvest {want}]" \
                    if mismatch else ""
                plan.no_mirror.append(f"{face.key}: {base} ({event.title}){note}")
                continue

            # AND A MISMATCH ON A MIRROR THAT DECLARES ITS OWN OPTION LIST IS
            # A NOTE TOO, for the same reason read from the other end. The
            # harvest's count is the wiki's, and the wiki writes a multi-page
            # event's later-page options as it pleases -- Abyssal Baths lists
            # Linger and Exit Baths beside the two INITIAL ones, Endless
            # Conveyor writes Leave as a note under the grab option rather
            # than as an option at all. A declared `options` list is read off
            # the DECOMPILE, which is the stronger truth, and the pairing
            # check below compares the face against THAT rather than against
            # the wiki. A mirror that does not declare one still pairs
            # position by position off the index's scrape, and there the
            # harvest count is the only guard there is.
            if mismatch:
                if not spec.options:
                    plan.refusals.append(mismatch)
                    continue
                plan.notes.append(mismatch + " (the mirror's declared list governs)")

            # The MIRROR'S spec wins over the index's literal scrape wherever
            # it speaks: the scrape reads every key literal in the base class,
            # which is a superset (the `_LOCKED` twins) in source order (not
            # list order) and sometimes a truncated stub (a key built by
            # concatenation). The spec is what the mirror actually asks for.
            option_keys = list(spec.options) or list(info["option_keys"])
            page_keys = list(spec.pages) or list(info["page_keys"])
            # A `table_option` is ONE key wearing a table of face lines, so
            # the count it has to agree with is the table's, not the key
            # list's.
            wanted_lines = (len(spec.table_option.choices)
                            if spec.table_option is not None else len(option_keys))
            # A `line_pages` entry consumes one more face line that is not an
            # option at all -- the wiki's rule-beside-the-options bullet -- so
            # it counts toward what the face must supply.
            wanted_lines += len(spec.line_pages)
            if wanted_lines != len(event.options):
                plan.refusals.append(
                    f"{face.key}: {base} -- the mirror's {wanted_lines} option "
                    f"key(s) {option_keys} cannot be paired with the face's "
                    f"{len(event.options)} option line(s)")
                continue

            # The consumed lines are taken in order AFTER the option lines,
            # and each one's OUTCOME is the text of every page it supplies.
            line_page_text: Dict[str, str] = {}
            for offset, pages_for_line in enumerate(spec.line_pages):
                _, outcome = event.options[len(event.options) - len(spec.line_pages) + offset]
                for page in pages_for_line:
                    line_page_text[page] = outcome

            table_pair = None
            if spec.table_option is not None:
                table_pair, bad = build_table_option(
                    option_keys[0], spec.table_option, event.options)
                plan.refusals.extend(f"{face.key}: {base} -- {b}" for b in bad)
                if bad:
                    continue

            dishes: Tuple[Tuple[str, str, str], ...] = ()
            if spec.dish_table is not None:
                source = spec.dish_table.source
                line = dict(zip(option_keys, event.options)).get(source)
                if line is None:
                    plan.refusals.append(
                        f"{face.key}: {base} -- the dish table names {source}, "
                        f"which is not one of the paired option keys")
                    continue
                dishes, bad = parse_dish_table(line[1], spec.dish_table.ids)
                plan.refusals.extend(f"{face.key}: {base} -- {b}" for b in bad)
                if bad:
                    continue

            cls = class_name_from_title(event.title)
            if cls in claimed:
                plan.refusals.append(
                    f"{face.key}: '{event.title}' slugs to {cls}, already claimed by "
                    f"{claimed[cls]} -- a dressed name IS the id and must be unique")
                continue
            claimed[cls] = f"{face.key}/{base}"

            plan.items.append(Dressed(
                face=face, base_class=base, mirror=spec.cls, cls=cls,
                entry=slugify(cls), base_entry=info["entry"], face_event=event,
                option_keys=option_keys,
                page_keys=page_keys,
                can_kill=bool(info["can_kill"]),
                extra_options=spec.extra_options,
                page_source=spec.page_source,
                line_page_text=line_page_text,
                table_pair=table_pair,
                dishes=dishes,
            ))

    return plan


def plan_files(plan: Plan) -> Dict[Path, str]:
    out: Dict[Path, str] = {}
    for item in plan.items:
        out[EVENTS_ROOT / item.face.folder / f"{item.cls}.cs"] = \
            dressed_class_source(item, item.face.file)
    out[GENERATED_CS] = generated_cs_source(plan.items)
    return out


def report(plan: Plan) -> None:
    by_face: Dict[str, int] = {}
    for item in plan.items:
        by_face[item.face.key] = by_face.get(item.face.key, 0) + 1
    for face in FACES:
        if face.active:
            print(f"  {face.key}: {by_face.get(face.key, 0)} dressed event(s)")
    for line in plan.skipped:
        print(f"  SKIP    {line}")
    for line in plan.no_mirror:
        print(f"  NO MIRROR {line}")
    for line in plan.parked:
        print(f"  PARKED  {line}")
    for line in plan.notes:
        print(f"  NOTE    {line}")
    for line in plan.refusals:
        print(f"  REFUSE  {line}", file=sys.stderr)


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="fail if regenerating would change anything")
    ap.add_argument("--refresh", action="store_true",
                    help="rebuild tools/data/sts2_base_events.json from a decompile")
    ap.add_argument("--decompile", type=Path, default=DECOMP_DEFAULT,
                    help="the decompiled MegaCrit.Sts2.Core.Models.Events directory")
    args = ap.parse_args(argv)

    if args.refresh:
        return refresh_index(args.decompile)

    plan = build_plan()
    files = plan_files(plan)

    if plan.refusals:
        report(plan)
        return 1

    if args.check:
        stale: List[str] = []
        for path, text in files.items():
            if not path.exists():
                stale.append(f"missing: {path.relative_to(REPO)}")
            elif path.read_text(encoding="utf-8") != text:
                stale.append(f"stale: {path.relative_to(REPO)}")
        for face in FACES:
            folder = EVENTS_ROOT / face.folder
            if not folder.is_dir():
                continue
            for existing in sorted(folder.glob("*.cs")):
                if existing not in files:
                    stale.append(f"extra: {existing.relative_to(REPO)}")
        if stale:
            print("gen_teyvat_events --check: generated output is out of date")
            for line in stale:
                print(f"  {line}")
            return 1
        print(f"gen_teyvat_events --check: {len(files)} file(s) up to date")
        report(plan)
        return 0

    for face in FACES:
        folder = EVENTS_ROOT / face.folder
        if folder.is_dir():
            for existing in sorted(folder.glob("*.cs")):
                if existing not in files:
                    existing.unlink()
    for path, text in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    print(f"gen_teyvat_events: wrote {len(files)} file(s)")
    report(plan)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
