"""The blind module's fixed shapes: paths, screen registers, refusals.

Cut out of `blindplay.py` by `EB-180`. Every name here is the one that
file declared, at the value it declared, and `blindplay.py` re-exports
all of them -- so `blindplay.PLAY_GUARDRAIL` and
`blindplay.BlindPlayError` still resolve. It sits at the BOTTOM of the
seam stack: it imports nothing from this package.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any



# `EB-214` item 7 (`M55`, re-scoped by R224). The pile view's own header, as
# `KurageMemoryText.ChargeSource` renders it on screen. THE RATE IS SPELLED
# RATHER THAN IMPORTED, deliberately: this module may not reach `tier0` at all
# (`test_blindplay_cannot_reach_a_sheet_or_a_policy` is the structural
# no-leak pin), so the number is held in step from the OTHER side --
# `test_the_pile_views_charge_source_header_reaches_the_blind_page` reads
# `C.CHARGE_PER_EXHAUST` and fails the moment this sentence falls behind a
# retune, the same way `lint_constant_parity` holds the C# copy.
CHARGE_SOURCE_LINE = "Gain 1 Charge when a card of yours Exhausts"

# `EB-248`. What a memory's price is a multiple OF, spelled on the same terms
# as the line above and for the same reason: this module may not import
# `tier0`, so `test_a_discounted_memory_prints_the_cost_it_was_multiplied_by`
# reads `C.KURAGE_MEMORY_COST_PER_ENERGY` and fails if the two fall apart.
# The C# half interpolates it from `KurageMemoryLaw.CostPerEnergy`, which
# `lint_constant_parity` already pins to the same sim constant, so all three
# move on a retune or none do.
KURAGE_COST_PER_ENERGY = 3

# `EB-340`. RULE 1'S GROWTH NUMBER, and the two-line reason it is spelled here.
#
# THE GLOSSARY DROPPED IT. The Bomb card's own keyword tip reads "Grows by 4 at
# the start of your turn" (`ArmKeywordTips.ForBomb`, which interpolates
# `KleeOverhaul.BombGrowth`); the page's copy of that sentence said only "Grows
# at the start of your turn", on every screen, and the r7b act-1 seat filed the
# two sentences disagreeing on one screen -- "the number is the entire
# mechanic". It also read "Grows" as the PILE growing and measured otherwise
# (`Bomb 5` + `Bomb 8` -> 21, not 17), so the page says "each Bomb".
#
# LIVE FIRST, THIS SECOND. `keyword_notes` reads the number off the screen's
# own Bomb tip where the screen carries one; this is the fallback for a screen
# that prints the WORD with no tip on it -- an enemy's badge, a reward row -- and
# is held in step from the other side by
# `test_the_bomb_glossary_carries_the_growth_number`, which reads the C#
# constant, the same discipline `CHARGE_SOURCE_LINE` is under.
BOMB_GROWTH = 4

#: `EB-537`. The Shatter's bonus damage, `ReactionConstants.ShatterDamage` in
#: the mod and `C.SHATTER_DAMAGE` in the sim, mirrored here for `BOMB_GROWTH`'s
#: reason and held in step from the test side.
SHATTER_DAMAGE = 6

#: `EB-625`. What one Tamakushi Casket strike deals --
#: `KokomiOverhaulLaw.CasketStrike` in the mod and
#: `C.KOKOMI_OVERHAUL_CASKET_STRIKE` in the sim. Mirrored here for
#: `BOMB_GROWTH`'s reason (this module may not reach `tier0`) and held in step
#: from the test side against both, so a retune cannot leave the page's Casket
#: glossary quoting a retired number while the mod's hover tip moves.
CASKET_STRIKE = 2

#: `EB-535`. THE COMPANION SPARK, on the two numbers the Hexerei row prints.
#: `KleeCompanionSpark.Base` and `.MaxPerPlay` in the mod, which are the kit
#: declaration LAW:145 obliges Klee's kit to make, mirrored here for
#: `BOMB_GROWTH`'s reason: this module may not import `tier0` at all, so the
#: numbers are held in step from the test side and a retune goes red there.
COMPANION_SPARK = 1
COMPANION_SPARK_MAX = 3

#: `EB-560`. THE SPARK A KLEE COMBAT OPENS WITH, `KleeOverhaulLaw.OpeningSpark`
#: in the mod and `C.KLEE_OVERHAUL_OPENING_SPARK` in the sim, mirrored here for
#: `BOMB_GROWTH`'s reason and held in step from the test side. R242 pick 1 put
#: the opening bank into rule 4 and the Spark keyword tip says it -- but that
#: tip is raised by a card that PRINTS the word, so a seat holding no
#: Spark-priced card meets the meter row and nothing else: "Where Spark comes
#: from is not on the combat screen" (Klee r20 lane 2).
OPENING_SPARK = 1

# `EB-340`. How long an aura clings, as `ReactionConstants.AuraDurationTurns`
# sets it and the four `Applies <element>` tips interpolate it. Same discipline
# as the line above: pinned from the other side, never imported.
AURA_DURATION_TURNS = 2

# `EB-465`. The Block a Crystallize pays, as
# `ReactionConstants.CrystallizeBlock` sets it and the shipped
# `KLEEMOD-CRYSTALLIZE_PREVIEW` row interpolates it. Same discipline as the
# line above -- spelled here, never imported -- and held in step from the other
# side by `test_the_crystallize_block_is_the_mods_own_constant`.
CRYSTALLIZE_BLOCK = 4

# `EB-377`. THE THREE BASE-GAME DURATION DEBUFFS, AS PERCENTAGES.
#
# Spelled here for `CHARGE_SOURCE_LINE`'s reason and held in step from the
# other side by `test_the_base_keyword_glossary_quotes_the_engines_own_rates`,
# which reads `C.VULNERABLE_TAKEN_MULT`, `C.WEAK_DEALT_MULT` and
# `C.FRAIL_BLOCK_MULT`. They are STRUCTURAL rates rather than balance dials --
# the base game's own numbers -- but a sim that ever restates one must not be
# able to leave this page teaching the retired figure.
VULNERABLE_TAKEN_PCT = 50
WEAK_DEALT_PCT = 25
FRAIL_BLOCK_PCT = 25

# `EB-597`. A FOURTH, AND IT IS THE ONE THE SIM DOES NOT MODEL. Shrink is an
# enemy-applied debuff of the base game's (the Shrinker Beetle's), so there is
# no `C.` rate on this side to hold it in step with. The figure is the shipped
# `ShrinkPower`'s own `DamageDecrease` canonical var, MEASURED off the
# assembly -- 30, already a percentage -- and `Round22Tests` reads that var
# from the other side so this page cannot be left teaching a retired number.
SHRINK_DEALT_PCT = 30

REPO = Path(__file__).resolve().parents[1]
LOG_ROOT = Path(__file__).resolve().parent / "logs" / "blindplay"
RECORD_ROOT = REPO / "review" / "qa" / "blindplay"
PROMPT_PATH = Path(__file__).resolve().parent / "blindplay_prompt.md"


# ------------------------------------------- EB-456: the action budget ----
#
# THE DEFECT. Two of the three round-13 seats were told to stop at 120 actions
# and stopped at 155-160 (Klee) and 165 (Kokomi). The brief's rule was a
# sentence addressed to the player, and a player counting its own actions is a
# player doing arithmetic instead of reading the board. A lane above zero is
# disposable, so nothing was lost but comparability -- and comparability is
# the whole reason the cap exists.
#
# SO THE COUNT IS THE BRIDGE'S. `blindplay act` is one PROCESS PER CALL (the
# same fact that puts the deck memory on disk, `blindplay_faces._deck_store`),
# so the count lives in a file beside it; the coordinator writes the cap at
# embark and the seat cannot see either number unless it asks. `GITS_MAX_ACTIONS`
# overrides the recorded cap for an operator driving a lane by hand.
#
# PER LANE, for the deck store's reason: two seats play side by side and one
# lane's spent budget must not close the other's run. The tag is NORMALISED
# here -- `1`, `lane1` and `GITS_LANE=lane1` are one lane -- because the
# coordinator writes it from `--lane 1` and the seat reads it from the
# environment, and those two spellings have to meet.
MAX_ACTIONS_ENV = "GITS_MAX_ACTIONS"
BUDGET_REACHED = "budget reached"
_BUDGET_STORE_DIR = Path(__file__).resolve().parent / "logs"

# `instances.LANE_ENV`'s value, SPELLED rather than imported: `instances`
# reaches a game-directory resolver, and this module's whole job is to import
# nothing from this package. The test side holds the two in step, the way
# `CHARGE_SOURCE_LINE` is held against `tier0.constants`.
LANE_ENV = "GITS_LANE"


def lane_tag(lane: object = None) -> str:
    """`1` / `"1"` / `"lane1"` -> `"1"`; unset, empty or unreadable -> `"0"`.

    Read raw and scrubbed to a filename rather than resolved through
    `instances`. NORMALISED because the two doors spell it differently: the
    coordinator writes the cap from `--lane 1` and the seat reads its count
    from `GITS_LANE`, which is documented both as `1` and as `lane1`.
    """
    raw = os.environ.get(LANE_ENV, "") if lane is None else str(lane)
    raw = re.sub(r"[^A-Za-z0-9]", "", raw).lower()
    if raw.startswith("lane"):
        raw = raw[4:]
    return raw or "0"


def budget_path(lane: object = None) -> Path:
    return _BUDGET_STORE_DIR / f"_blindplay-budget-lane{lane_tag(lane)}.json"


def read_budget(lane: object = None) -> dict[str, int]:
    """`{"cap": n, "count": n}` for this lane. Zeroes where nothing is set."""
    try:
        blob = json.loads(budget_path(lane).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        blob = {}
    if not isinstance(blob, dict):
        blob = {}
    def _num(key: str) -> int:
        try:
            return max(0, int(blob.get(key) or 0))
        except (TypeError, ValueError):
            return 0
    return {"cap": _num("cap"), "count": _num("count")}


def _write_budget(row: dict[str, int], lane: object = None) -> None:
    try:
        _BUDGET_STORE_DIR.mkdir(parents=True, exist_ok=True)
        budget_path(lane).write_text(json.dumps(row), encoding="utf-8")
    except OSError:
        pass                       # a read-only tree simply keeps no count


def set_budget(cap: int, lane: object = None) -> dict[str, int]:
    """Record this lane's cap and ZERO its count. The coordinator's write.

    Zeroing is the point: a cap is set at embark, and an embark is a new run.
    A cap of 0 clears the budget entirely, which is the unlimited lane every
    round before this row ran on.
    """
    row = {"cap": max(0, int(cap or 0)), "count": 0}
    _write_budget(row, lane)
    return row


def budget_cap(lane: object = None) -> int:
    """The cap in force: `GITS_MAX_ACTIONS` first, then the lane's own."""
    env = os.environ.get(MAX_ACTIONS_ENV, "").strip()
    if env:
        try:
            return max(0, int(env))
        except ValueError:
            return 0
    return read_budget(lane)["cap"]


def budget_spent(lane: object = None) -> tuple[int, int]:
    """`(actions taken, cap)` for this lane. A cap of `0` is no budget."""
    return read_budget(lane)["count"], budget_cap(lane)


def count_action(lane: object = None) -> int:
    """Charge one accepted act to this lane and return the new count."""
    row = read_budget(lane)
    row["count"] += 1
    _write_budget(row, lane)
    return row["count"]


def forget_budget(lane: object = None) -> None:
    """Drop this lane's budget. The operator's reset, and the tests'."""
    try:
        budget_path(lane).unlink()
    except OSError:
        pass

# The disclaimer that rides on every observation, the transcript and the sealed
# record -- same reasoning as `qa_packet.PACKET_GUARDRAIL`: a caveat that lives
# outside the record is lost the moment two records are concatenated.
PLAY_GUARDRAIL = (
    "you are playing the real game through a tool that shows you only what "
    "the screen prints; nothing recorded here is a measurement, a comparison "
    "with any other run, or a judgement of whether the game is fun or good "
    "that anyone will treat as approval")

COMBAT_SCREENS = frozenset({"monster", "elite", "boss"})
SELECT_SCREENS = frozenset({"card_select", "hand_select"})

# `EB-245`. THE OVERLAYS A FIGHT WEARS, and they are not the end of one.
#
# The wire's `state_type` changes from `monster` to `card_select` the moment a
# *Choose one* mode, an Exhaust chooser or a bundle picker opens MID-COMBAT --
# the fight is still up behind it, the enemies are still standing, and the very
# next screen is the same board. `Session.run` read its fight boundary off
# `screen == "combat"` alone, so every such overlay looked like a fight ending
# and the seat was asked for a FIGHT RECORD in the middle of its turn.
# `KLEESPARK-W5` sealed FOUR fight records for THREE fights that way, and the
# phantom one reports a fight that ended while its enemy stood at 44/44.
#
# So an overlay is NEITHER a start nor an end: it INHERITS whatever the run was
# already in. A `card_select` at a rest site inherits "not in a fight" and is
# still not one, which is why this is the whole rule rather than a special case
# for combat overlays -- there is no field on the feed that says which it is.
FIGHT_OVERLAYS = frozenset({"card_select", "hand_select", "bundle_select"})

# Screens that exist and are deliberately NOT driven. Each is TOOL-BLOCKED
# with its own reason rather than lumped in with the unknown ones, because
# "this module has no grammar for a minigame" and "the wire returned a screen
# nobody has ever seen" are different findings for whoever reads the log.
UNDRIVEN_SCREENS = {
    "crystal_sphere": "a minigame with a click-a-cell interface; the command "
                      "grammar has no shape for it",
    "overlay": "the wire's own catch-all for an overlay it does not model, "
               "which is one of the two shapes a soft-lock takes",
    "unknown": "the wire could not name this screen",
}

# ------------------------------- EB-396: the way OUT of an undriven screen --
#
# TOOL-BLOCKED USED TO MEAN STRANDED, AND THAT IS A DIFFERENT THING.
# A Klee r10 seat chose *Uncover Future*, landed on `crystal_sphere`, and sat
# there with the run alive at 53/77: the page said the screen was not being
# driven and offered no command at all, so there was nothing to type and the
# run ended there rather than on a board. The minigame is still not driven and
# is not going to be -- `UNDRIVEN_SCREENS` above is unchanged and says why --
# but LEAVING it is not playing it, and the soak has driven that exit all
# along (`soak_screens._escape`: `crystal_sphere_proceed`).
#
# So an undriven screen may declare an EXIT. Where it does, the page prints the
# one verb and `act` resolves it even though the screen is blocked; where it
# does not -- `overlay`, `unknown`, neither of which has an exit anyone knows
# -- nothing changes and the block is exactly what it was. The verb is `leave`
# rather than `proceed` because it is not a proceed button: a seat who typed
# `proceed` here would be telling the truth about intent and the wire would
# refuse it, which is the shape of `EB-259` one screen over.
#
# WHAT THE EXIT COSTS IS NOT HIDDEN. The gold is already spent by the time this
# screen is up -- the option pays before the minigame opens -- so leaving
# forfeits the divinations and nothing else, and the page says so rather than
# letting a seat believe it has undone the choice.
UNDRIVEN_EXITS: dict[str, dict[str, Any]] = {
    "crystal_sphere": {
        "command": "leave",
        "action": {"action": "crystal_sphere_proceed"},
        "how": "you can say `leave` to step away from it and carry on with "
               "the run; what the option already paid is spent either way",
    },
}

# ------------------- EB-396: and the warning BEFORE the choice is taken -----
#
# The exit above is the repair; this is the half that stops the seat needing
# it. The Crystal Sphere's options both end on the same minigame (the mirror's
# own note: "the same MINIGAME on both -- three divinations after paying, six
# after taking the curse"), so the warning is a fact about the EVENT and is
# printed on each of its options rather than guessed at from one option's
# words.
#
# KEYED ON THE BASE EVENT ID, THROUGH THE ONE SUBSTITUTION TABLE. A Teyvat
# dressing gives the same event a new id and new option titles, so matching on
# printed words would warn on the base event and silently stop warning on the
# six faces that dress it -- the failure mode `EB-767` already met from the
# other side. `understudy/teyvat_ids.resolve_event_id` is that table, and it
# imports the standard library and nothing else, which is why it is a module
# and not a copy.
UNDRIVEN_AFTER_EVENT: dict[str, str] = {
    "CRYSTAL_SPHERE": "both of this event's options open a minigame this tool "
                      "cannot play -- a grid of cells clicked one at a time. "
                      "You will be able to say `leave` on that screen and "
                      "carry on with the run, but what you spend here is "
                      "spent and the divinations are forfeit",
}

# How long the driver rides out a TRANSITION before calling it a screen.
# `unknown` -- and a state with no `state_type` key at all -- is what the wire
# answers for the moment between leaving one room and entering the next, which
# is not a screen and must not be reported as one. `soak._settle_transient`
# learned this on the same wire and these are its numbers.
SETTLE_TRIES = 60
SETTLE_DELAY_S = 0.5

# `EB-381`. How many times `settle_board` will re-ask a board that is still
# moving. SHORTER THAN `SETTLE_TRIES` on purpose: `settle` is waiting for a
# screen the game is definitely about to hand over, and this is waiting for an
# action queue to drain -- a board still changing after six reads is a board
# with an animation ticking on it, and thirty seconds of polling per
# observation would buy a blind seat nothing but a timeout.
BOARD_SETTLE_TRIES = 6

# EB-1. A REGISTER, NOT A HEURISTIC, and a deliberate SECOND COPY of
# `soak.HAZARD_EVENTS`. Importing soak here would pull `policy_v1` and through
# it every tier0 sheet loader into the design-blind module, which is the one
# import this file may not have. `test_understudy_blindplay` asserts this map
# covers every id soak registers, so the two cannot drift apart silently: the
# day soak adds a hazard, the test here goes red.
HAZARD_EVENTS = {
    "PUNCH_OFF": "entering this room spins the game's main thread on an "
                 "unbounded error loop. It is refused, not played.",
}
HAZARD_EVENT_TITLES = {"punch off": "PUNCH_OFF"}


class BlindPlayError(RuntimeError):
    """A command, a screen or a seat this module refuses to work with."""


class SeatBudgetExhausted(BlindPlayError):
    """The SEAT's own budget ran out -- somebody else's rate limit, not ours.

    Kept apart from every other seat failure because the two mean opposite
    things to whoever reads the record. `seat_refused` says the transcript
    guard bit or the model would not answer, and that is a finding. A usage
    limit says the session was cut off mid-run by an account quota, which is
    not a finding about anything: the honest record is how far it got, under
    its own termination reason, with the partial records kept.
    """


# The markers a usage limit reads as on the seat's stderr. Deliberately three
# spellings and the HTTP status: the wording is a third party's and moves, and
# a session that misfiles a quota stop as a refusal is a session that reads as
# a finding about the game.
_RATE_LIMIT_MARKERS = ("rate limit", "rate_limit", "usage limit",
                       "usage_limit", "429", "quota", "too many requests")


def _is_rate_limited(stderr_text: str) -> bool:
    low = str(stderr_text or "").casefold()
    return any(m in low for m in _RATE_LIMIT_MARKERS)
