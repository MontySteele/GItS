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
import time
from pathlib import Path
from typing import Any, Iterator



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
# constant.
BOMB_GROWTH = 2

#: `EB-537`. The Shatter's bonus damage, `ReactionConstants.ShatterDamage` in
#: the mod and `C.SHATTER_DAMAGE` in the sim, mirrored here for `BOMB_GROWTH`'s
#: reason and held in step from the test side.
SHATTER_DAMAGE = 6

#: `EB-625`, rewritten by the Casket pass (2026-09-28) and again by the Kokomi
#: re-founding (2026-10-12), which retired the count. The Block the Tamakushi
#: Casket gives for each Plan card or Companion she plays (2026-10-18) --
#: `KokomiOverhaulLaw.CasketBlock` in the mod and
#: `C.KOKOMI_OVERHAUL_CASKET_BLOCK` in the sim. Mirrored here for
#: `BOMB_GROWTH`'s reason (this module may not reach `tier0`) and held in step
#: from the test side against both, so a retune cannot leave the page's Casket
#: glossary quoting a retired number while the relic's face moves.
CASKET_BLOCK = 2

#: `EB-560`. THE SPARK A KLEE COMBAT OPENS WITH, `KleeOverhaulLaw.OpeningSpark`
#: in the mod and `C.KLEE_OVERHAUL_OPENING_SPARK` in the sim, mirrored here for
#: `BOMB_GROWTH`'s reason and held in step from the test side. R242 pick 1 put
#: the opening bank into rule 4 and the Spark keyword tip says it -- but that
#: tip is raised by a card that PRINTS the word, so a seat holding no
#: Spark-priced card meets the meter row and nothing else: "Where Spark comes
#: from is not on the combat screen" (Klee r20 lane 2).
OPENING_SPARK = 3

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

# The element port (2026-09-28). The flat damage a Swirl deals
# to every enemy, as `ReactionConstants.SwirlDamage` sets it and
# `ArmKeywordTips.ForSwirl` interpolates it. Same discipline: spelled here,
# held in step by `tier0/tests/test_element_port.py`.
SWIRL_DAMAGE = 2

# `EB-377`. THE THREE BASE-GAME DURATION DEBUFFS, AS PERCENTAGES.
#
# Spelled here for `BOMB_GROWTH`'s reason and held in step from the
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

# 2026-10-08. THE GAME'S OWN NUMBERS FIRST, THESE MIRRORS SECOND. Suite 5's
# act-1 page ran this module from `main` (growth 4, opening 1) against a game
# built from `klee-next` (2 and 3), and where no Bomb tip was on screen the
# page taught the stale numbers. The bridge now sends the build's
# `KleeOverhaulLaw.BombGrowth` and `.OpeningSpark` on every screen
# (`run.klee_law`, `vendor/STS2_MCP/gits/GitsKleeLaw.cs`); the observation
# carries them (never printed as such) and every page sentence that quotes
# either number reads them through these two functions.
KLEE_LAW_KEYS = ("bomb_growth", "opening_spark")


def live_klee_law(state: Any) -> dict[str, int]:
    """`{"bomb_growth": n, "opening_spark": n}` off the wire's `run` block,
    each key only where the bridge sent a number; `{}` on an older bridge
    or a build with no Klee mod."""
    run = state.get("run") if isinstance(state, dict) else None
    law = run.get("klee_law") if isinstance(run, dict) else None
    out: dict[str, int] = {}
    if isinstance(law, dict):
        for key in KLEE_LAW_KEYS:
            try:
                out[key] = int(law[key])
            except (KeyError, TypeError, ValueError):
                continue
    return out


def bomb_growth(obs: Any = None) -> int:
    """The Bomb growth this page quotes: the live build's, else the mirror."""
    law = obs.get("klee_law") if isinstance(obs, dict) else None
    return int((law or {}).get("bomb_growth", BOMB_GROWTH))


def opening_spark(obs: Any = None) -> int:
    """The opening Spark this page quotes: the live build's, else the mirror."""
    law = obs.get("klee_law") if isinstance(obs, dict) else None
    return int((law or {}).get("opening_spark", OPENING_SPARK))


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

# 2026-10-08. THE LANE'S STATE IS THE LANE'S, NOT THE CHECKOUT'S.
#
# THE FIND (suite 5). Every per-lane file below -- the action budget, the
# words a lane has been shown, the refusal mark, the ledger mark, the deck,
# arm, run and fight memories in `blindplay_faces`, and the embark sidecar's
# copy -- lived in `understudy/logs` of WHICHEVER CHECKOUT RAN THE COMMAND. The
# act-2 seats were moved to a second worktree to match the game's build, and
# every lane lost its cap (no budget file reads as no cap), its words store
# and its build identity. A control seat whose wrapper had no `cd` read one
# checkout's counter and then the other's, and saw it jump 20 -> 127.
#
# SO THE STATE LIVES BESIDE THE LANE'S GAME: `%LOCALAPPDATA%\gits-lanes\
# laneN\blindplay\`, under the folder `instances.LANE_ROOT` already gives the
# lane's disposable profile (spelled here, not imported, for `LANE_ENV`'s
# reason below). `GITS_LANE_STATE` names another root -- an operator's
# override. `_BUDGET_STORE_DIR` is the tests' older seam: set, it puts every
# lane's files in that ONE folder, as before.
#
# MIGRATION: a file missing in the new folder is read from the old one (this
# checkout's `understudy/logs`) on first read, so a lane that was embarked
# before this landed keeps its cap and its words.
LANE_STATE_ENV = "GITS_LANE_STATE"
_BUDGET_STORE_DIR: Path | None = None
_LEGACY_STATE_DIR = Path(__file__).resolve().parent / "logs"
_LANE_STATE_ROOT: Path | None = None


def lane_state_root() -> Path:
    """The folder that holds one sub-folder of state per lane."""
    if _LANE_STATE_ROOT is not None:
        return _LANE_STATE_ROOT
    env = os.environ.get(LANE_STATE_ENV, "").strip()
    if env:
        return Path(env)
    base = os.environ.get("LOCALAPPDATA") or str(
        Path.home() / "AppData" / "Local")
    return Path(base) / "gits-lanes"


def lane_state_dir(lane: object = None) -> Path:
    """Where this lane's blind-play state lives, whichever checkout runs."""
    if _BUDGET_STORE_DIR is not None:
        return _BUDGET_STORE_DIR
    return lane_state_root() / f"lane{lane_tag(lane)}" / "blindplay"


def migrated(path: Path, legacy_name: str | None = None) -> Path:
    """`path` if it exists; else the same file in this checkout's old
    `understudy/logs` if THAT exists (the first read after the move); else
    `path`. Writes always go to `path`, so the old file is read until the
    first write and never again."""
    if path.exists():
        return path
    old = _LEGACY_STATE_DIR / (legacy_name or path.name)
    return old if old != path and old.is_file() else path


def write_atomic(path: Path, text: str) -> bool:
    """Write `text` to `path` through a temp file and `os.replace`, so a
    reader -- or a kill mid-write -- never sees half a file. False on
    failure: a read-only tree simply keeps no state, as before."""
    tmp = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_text(text, encoding="utf-8")
        for attempt in range(5):
            try:
                os.replace(tmp, path)
                return True
            except PermissionError:
                # Windows refuses a replace while another process holds the
                # target open; that window is milliseconds.
                time.sleep(0.02 * (attempt + 1))
        os.replace(tmp, path)
        return True
    except OSError:
        try:
            tmp.unlink()
        except OSError:
            pass
        return False


def read_state_json(path: Path, legacy_name: str | None = None) -> Any:
    """The JSON in a lane state file (migrated), or None when unreadable."""
    try:
        return json.loads(migrated(path, legacy_name).read_text(
            encoding="utf-8"))
    except (OSError, ValueError):
        return None


def drop_state(path: Path, legacy_name: str | None = None) -> None:
    """Remove a lane state file, and its old-location copy, so a forget is
    not undone by the migration read."""
    for p in {path, _LEGACY_STATE_DIR / (legacy_name or path.name)}:
        try:
            p.unlink()
        except OSError:
            pass

# `instances.LANE_ENV`'s value, SPELLED rather than imported: `instances`
# reaches a game-directory resolver, and this module's whole job is to import
# nothing from this package. The test side holds the two in step, the way
# `BOMB_GROWTH` is held against the mod's constant.
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
    return lane_state_dir(lane) / f"_blindplay-budget-lane{lane_tag(lane)}.json"


def _budget_row(lane: object = None) -> dict[str, Any]:
    blob = read_state_json(budget_path(lane))
    return blob if isinstance(blob, dict) else {}


def read_budget(lane: object = None) -> dict[str, int]:
    """`{"cap": n, "count": n}` for this lane. Zeroes where nothing is set."""
    blob = _budget_row(lane)
    def _num(key: str) -> int:
        try:
            return max(0, int(blob.get(key) or 0))
        except (TypeError, ValueError):
            return 0
    return {"cap": _num("cap"), "count": _num("count")}


def _write_budget(row: dict[str, Any], lane: object = None) -> None:
    # Atomic (2026-10-08): a kill mid-write used to leave half a file, which
    # reads as cap 0 -- an uncapped lane.
    write_atomic(budget_path(lane), json.dumps(row))


def set_budget(cap: int, lane: object = None,
               run: str = "") -> dict[str, int]:
    """Record this lane's cap and ZERO its count. The coordinator's write.

    Zeroing is the point: a cap is set at embark, and an embark is a new run.
    A cap of 0 clears the budget entirely, which is the unlimited lane every
    round before this row ran on. `run` is the embark's stamp: the count
    belongs to that run (`count_action`).
    """
    row: dict[str, Any] = {"cap": max(0, int(cap or 0)), "count": 0}
    if run:
        row["run"] = str(run)
    _write_budget(row, lane)
    # And the words the lane has been shown: a new run's first screen
    # defines its words again (`blindplay_brief`, 2026-10-01).
    forget_words_seen(lane)
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
    """Charge one accepted act to this lane and return the new count.

    2026-10-08. THE COUNT BELONGS TO THE RUN EMBARKED LAST. When the newest
    embark sidecar for this lane names a stamp newer than the one the budget
    was set for, the lane was re-embarked by a door that did not reset this
    store (an older checkout writing the old location), and the count held
    here is the previous run's: it restarts at 0, keeping the cap."""
    row = _budget_row(lane)
    cap = read_budget(lane)["cap"]
    newest = lane_embark_stamp(lane)
    held = str(row.get("run") or "")
    try:
        count = max(0, int(row.get("count") or 0))
    except (TypeError, ValueError):
        count = 0
    if newest and held and newest > held:
        count = 0
    if newest and newest > held:
        row["run"] = newest
    row["count"] = count + 1
    row["cap"] = cap
    row["refused"] = 0
    _write_budget(row, lane)
    return row["count"]


# THE REFUSAL STOP IS COUNTED BY THE BRIDGE (co-op paired round 2026-10-09,
# finding 8). The brief makes three refused commands in a row a stop, and the
# seat did the counting. A fight that ended partway through a batch turned the
# rest of the batch into "The fight is over: nothing was sent." lines, which do
# not start with REFUSED, so the seat never counted them and the run of
# refusals went past three. The lane now keeps the streak beside its action
# count: every refused `act` adds one, every sent `act` zeroes it, and a new
# embark (`set_budget`) starts it at 0.
MAX_REFUSALS = 3


def refusal_streak(lane: object = None) -> int:
    """Refused commands in a row on this lane's current run."""
    row = _budget_row(lane)
    held = str(row.get("run") or "")
    newest = lane_embark_stamp(lane)
    if newest and held and newest > held:
        return 0
    try:
        return max(0, int(row.get("refused") or 0))
    except (TypeError, ValueError):
        return 0


def count_refusal(lane: object = None) -> int:
    """Add one refused command to this lane's streak and return it."""
    row = _budget_row(lane)
    streak = refusal_streak(lane) + 1
    newest = lane_embark_stamp(lane)
    if newest and newest > str(row.get("run") or ""):
        row["run"] = newest
        row["count"] = 0
    row["refused"] = streak
    row["cap"] = read_budget(lane)["cap"]
    row.setdefault("count", 0)
    _write_budget(row, lane)
    return streak


def clear_refusal_streak(lane: object = None) -> None:
    """A sent command ends the streak (on a lane with no cap, where
    `count_action` is not called)."""
    row = _budget_row(lane)
    if row.get("refused"):
        row["refused"] = 0
        _write_budget(row, lane)


# 2026-10-01 (Varka lane 2, act 3). A REFUSAL MUST NOT COST THE TURN. A seat
# batched `play "Fischl - Nightrider"`, two more plays and `end turn`; every
# play was refused for want of an enemy name, and the `end turn` went through,
# so the whole turn was lost to a grammar slip. So a refused command in a
# fight leaves a mark, keyed on the board it was refused against, and an `end
# turn` typed on that same board is refused once with the refusal named. The
# mark is cleared by that refusal and by any command that is sent.
REFUSAL_MARK_TTL_S = 300.0


def refusal_mark_path(lane: object = None) -> Path:
    return lane_state_dir(lane) / f"_blindplay-refused-lane{lane_tag(lane)}.json"


def mark_refusal(board: str, command: str, why: str,
                 lane: object = None, now: float | None = None) -> None:
    row = {"board": board, "command": command, "why": why,
           "at": time.time() if now is None else now}
    write_atomic(refusal_mark_path(lane), json.dumps(row))


def clear_refusal(lane: object = None) -> None:
    drop_state(refusal_mark_path(lane))


# VARKA ROUND (2026-10-13, lanes 1 and 2). A BATCH THAT CROSSES A SCREEN
# CHANGE STOPS CLEANLY. A seat played Chain Lightning ("Discard 2 cards") into
# the last enemy with `choose`, `choose`, `confirm` already queued for the
# discard prompt; the fight ended, the three were refused against the reward
# screen, and the third tripped the sticky REFUSAL STOP. A command typed
# before the seat could see the screen it lands on is not a refusal, it is a
# stale order. So every SENT act leaves the room it was sent from, and an act
# that finds the lane in a different room before any `observe` is skipped:
# not sent, not counted toward the streak. `observe` (a look) clears the mark.
# A room is coarser than `state_type`: a fight's overlays (`FIGHT_OVERLAYS`)
# inherit the room they opened in, and a card offer is part of the reward
# screen, so a discard prompt or a reward's card pick is never a "change".
SCREEN_ROOMS = {"card_reward": "rewards"}


def room_of(screen: str) -> str:
    """The room a screen belongs to; `""` for an overlay, which inherits."""
    if screen in FIGHT_OVERLAYS:
        return ""
    if screen in COMBAT_SCREENS:
        return "fight"
    return SCREEN_ROOMS.get(screen, screen)


def sent_mark_path(lane: object = None) -> Path:
    return lane_state_dir(lane) / f"_blindplay-last-sent-lane{lane_tag(lane)}.json"


def mark_sent(command: str, room: str, lane: object = None,
              now: float | None = None) -> None:
    """Remember the last sent command and the room it was sent from. An
    overlay's `""` keeps the room the last mark held."""
    if not room:
        held = read_state_json(sent_mark_path(lane))
        room = str(held.get("room") or "") if isinstance(held, dict) else ""
    row = {"command": command, "room": room,
           "at": time.time() if now is None else now}
    write_atomic(sent_mark_path(lane), json.dumps(row))


def clear_sent(lane: object = None) -> None:
    drop_state(sent_mark_path(lane))


def last_sent_command(lane: object = None) -> str:
    """The last command this lane sent, or `""` (no freshness check: it
    only names the card in a sentence)."""
    row = read_state_json(sent_mark_path(lane))
    return str(row.get("command") or "") if isinstance(row, dict) else ""


def screen_changed_after(room: str, lane: object = None,
                         now: float | None = None) -> str | None:
    """The sent command after which the lane left its room, if no look has
    happened since (fresh within `REFUSAL_MARK_TTL_S`); else `None`."""
    row = read_state_json(sent_mark_path(lane))
    if not isinstance(row, dict) or not room:
        return None
    held = str(row.get("room") or "")
    if not held or held == room:
        return None
    now = time.time() if now is None else now
    try:
        if now - float(row.get("at") or 0) > REFUSAL_MARK_TTL_S:
            return None
    except (TypeError, ValueError):
        return None
    return str(row.get("command") or "the last command")


# KOKOMI ROUND 3 (2026-10-11, lane 5). `end turn` SENT TWICE. The seat typed
# `end turn` a second time without looking, and the turn it ended was the NEXT
# one, at 56 HP (F4, 56 to 35). `end turn` is asynchronous: the act that
# follows reads through `settle` (`EB-175`), which rides out the enemy turn
# and hands back the new turn's board -- so a second `end turn` (or a `play`
# written for the old hand) lands on a turn the seat has never seen. The room
# does not change, so `screen_changed_after` cannot see it. Any command after
# a sent `end turn`, with no look since, is now a skip: not sent, not counted.
TURN_ENDED_SKIP = ("Skipped: your `end turn` was sent and the next turn is a "
                   "board you have not seen, so this was not sent (a second "
                   "`end turn` would end the NEW turn). This is not counted "
                   "as a refusal. `observe` first, then give the command "
                   "again.")


def _is_end_turn(command: str) -> bool:
    return " ".join(str(command).lower().split()).startswith("end turn")


def turn_ended_since_look(command: str, lane: object = None,
                          now: float | None = None) -> bool:
    """Was the lane's last sent command an `end turn`, with no look since
    (fresh within `REFUSAL_MARK_TTL_S`), and is `command` something that acts
    on a turn? A co-op `wait` is exempt: it is what follows an `end turn`
    there, and it prints the page it waited for."""
    if " ".join(str(command).lower().split()).startswith("wait"):
        return False
    row = read_state_json(sent_mark_path(lane))
    if not isinstance(row, dict) or not _is_end_turn(row.get("command", "")):
        return False
    now = time.time() if now is None else now
    try:
        return now - float(row.get("at") or 0) <= REFUSAL_MARK_TTL_S
    except (TypeError, ValueError):
        return False


# CO-OP SPIRAL ABYSS (2026-10-14, lanes 4/5). THE SEAT'S LAST LOOK. The
# client seat chained `play` commands; the host's Bombs killed the last enemy
# in between, the rest were refused against a fight that had ended (or a
# target that had died), and three of those tripped the sticky stop. The look
# each `observe` (and each page `wait` prints) leaves here is what a refused
# command is checked against: a refusal whose room or target changed since
# that look is a skip, not a refusal (`blindplay.changed_under`).
def look_path(lane: object = None) -> Path:
    return lane_state_dir(lane) / f"_blindplay-last-look-lane{lane_tag(lane)}.json"


def remember_look(room: str, living: list[str], lane: object = None,
                  now: float | None = None, screen: str = "") -> None:
    """Remember the room the seat last looked at, the enemies alive on it
    (printed names and letters, folded), and the screen kind the page was
    rendered on (`state_type`), so a chooser that opened since is seen.

    Yae review r6, item 7 (lane 2, Aeonglass). A look at a fight OVERLAY
    (`room_of` gives `""`) keeps the room the last look held, as
    `mark_sent` does. The seat looked at a turn-start chooser (Stratagem)
    with the boss at 51; its `choose` let the turn start finish, a
    full-shrine plant killed the boss, and the chained `play` was refused
    as a counted refusal, because a look with no room could not see that
    the fight had ended since (`blindplay.changed_under`). The page was not
    behind: the kill came after the pick."""
    if not room:
        held = read_state_json(look_path(lane))
        room = str(held.get("room") or "") if isinstance(held, dict) else ""
    row = {"room": room, "living": list(living), "screen": screen,
           "at": time.time() if now is None else now}
    write_atomic(look_path(lane), json.dumps(row))


def read_look(lane: object = None, now: float | None = None) -> dict | None:
    """The seat's last look, if it is fresh (`REFUSAL_MARK_TTL_S`)."""
    row = read_state_json(look_path(lane))
    if not isinstance(row, dict):
        return None
    now = time.time() if now is None else now
    try:
        if now - float(row.get("at") or 0) > REFUSAL_MARK_TTL_S:
            return None
    except (TypeError, ValueError):
        return None
    return row


def clear_look(lane: object = None) -> None:
    drop_state(look_path(lane))


# KOKOMI ROUND 2 (2026-10-13, lane 5). A DELIBERATE `skip` IS THE SKIP. The
# Furina wave's hold (#1202) holds `proceed` once past a card offer on a
# reward screen, and a card reward the seat opened and skipped is still a row
# on that screen, so the seat had to say `proceed` twice after already saying
# `skip`. Each sent `skip` on a card reward leaves a count here; the hold drops
# that many card rows, and any sent `proceed` clears the count.
def card_skip_path(lane: object = None) -> Path:
    return lane_state_dir(lane) / f"_blindplay-card-skips-lane{lane_tag(lane)}.json"


def card_skips(lane: object = None, now: float | None = None) -> int:
    """How many card rewards were skipped on the reward screen still up
    (fresh within `REFUSAL_MARK_TTL_S` of the last skip)."""
    row = read_state_json(card_skip_path(lane))
    if not isinstance(row, dict):
        return 0
    now = time.time() if now is None else now
    try:
        if now - float(row.get("at") or 0) > REFUSAL_MARK_TTL_S:
            return 0
        return max(0, int(row.get("count") or 0))
    except (TypeError, ValueError):
        return 0


def mark_card_skip(lane: object = None, now: float | None = None) -> None:
    now = time.time() if now is None else now
    row = {"count": card_skips(lane, now) + 1, "at": now}
    write_atomic(card_skip_path(lane), json.dumps(row))


def clear_card_skips(lane: object = None) -> None:
    drop_state(card_skip_path(lane))


# KOKOMI ROUND 2 (2026-10-13, lane 4). The hand the last `observe` printed,
# numbered as printed, so a chained `play "Sting (4)"` names the copy the seat
# read (`blindplay_grammar.resolve_shown_card`). Overwritten by each
# `observe`; a hand with no repeated name clears it.
def shown_hand_path(lane: object = None) -> Path:
    return lane_state_dir(lane) / f"_blindplay-shown-hand-lane{lane_tag(lane)}.json"


def remember_shown_hand(row: dict | None, lane: object = None) -> None:
    if row is None:
        drop_state(shown_hand_path(lane))
    else:
        write_atomic(shown_hand_path(lane), json.dumps(row))


def read_shown_hand(lane: object = None) -> dict | None:
    row = read_state_json(shown_hand_path(lane))
    return row if isinstance(row, dict) else None


def pending_refusal(board: str, lane: object = None,
                    now: float | None = None) -> dict | None:
    """The refusal left on THIS board, if it is fresh; else `None`."""
    row = read_state_json(refusal_mark_path(lane))
    if not isinstance(row, dict) or row.get("board") != board:
        return None
    now = time.time() if now is None else now
    try:
        if now - float(row.get("at") or 0) > REFUSAL_MARK_TTL_S:
            return None
    except (TypeError, ValueError):
        return None
    return row


# 2026-10-04. THE RUN SEED, which no screen's feed carries (`run` sends act,
# floor and ascension only), so no page printed it and a seat could not fill
# its record's identity block. `embark` reads the seed back off the wire once
# and writes it into the lane's sidecar (`understudy/logs/embark-<stamp>.json`,
# `instance` naming the lane); the newest sidecar for this lane that holds a
# seed is the run up on it. Read as a file, by name, for the reason `LANE_ENV`
# is spelled above: this module imports nothing that reaches a lane resolver.
#
# 2026-10-08: `embark` also writes a copy of each sidecar into the LANE's
# state folder (`lane_state_dir`), and that copy is read first, so a seat
# running from another checkout than the embark still finds its run. The
# checkout's own `understudy/logs` is the fallback for an older embark.
_SIDECAR_DIR = Path(__file__).resolve().parent / "logs"


def lane_sidecars(lane: object = None) -> Iterator[dict[str, Any]]:
    """This lane's embark sidecars, newest stamp first, read lazily: the lane
    state folder's copies, then this checkout's `understudy/logs`. A stamp
    found in both is read once, from the lane folder. Lazy because a
    checkout's logs hold hundreds of sidecars and a caller wants the newest."""
    label = f"lane{lane_tag(lane)}"
    named: dict[str, Path] = {}
    for d in (lane_state_dir(lane), _SIDECAR_DIR):
        try:
            for path in d.glob("embark-*.json"):
                named.setdefault(path.name, path)
        except OSError:
            continue
    for name in sorted(named, reverse=True):
        try:
            blob = json.loads(named[name].read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(blob, dict):
            continue
        if str(blob.get("instance") or "lane0") != label:
            continue
        yield blob


def lane_embark_stamp(lane: object = None) -> str:
    """The stamp of the newest embark on this lane, or ""."""
    for blob in lane_sidecars(lane):
        stamp = str(blob.get("stamp") or "").strip()
        if stamp:
            return stamp
    return ""


def lane_run_seed(lane: object = None) -> str:
    """The seed `embark` read back for this lane's run, or "" when no
    sidecar for the lane names one."""
    for blob in lane_sidecars(lane):
        seed = str(blob.get("run_seed") or "").strip()
        if seed:
            return seed
    return ""


def lane_game_dir(lane: object = None) -> str:
    """The game install the newest embark on this lane launched, or ""."""
    for blob in lane_sidecars(lane):
        game = str(blob.get("game_dir") or "").strip()
        if game:
            return game
    return ""


# 2026-10-01. THE WORDS A LANE HAS ALREADY BEEN SHOWN. `observe --brief`
# keeps a definition the first time it prints on a lane and cuts it after
# (`blindplay_brief`), so the lane remembers which it has printed. Beside the
# budget, keyed the same way, and cleared where the budget is set: at embark.
def words_seen_path(lane: object = None) -> Path:
    return lane_state_dir(lane) / f"_blindplay-words-lane{lane_tag(lane)}.json"


def read_words_seen(lane: object = None) -> set[str]:
    blob = read_state_json(words_seen_path(lane))
    return {str(k) for k in blob} if isinstance(blob, list) else set()


def write_words_seen(words: set[str], lane: object = None) -> None:
    # A read-only tree simply repeats its words.
    write_atomic(words_seen_path(lane), json.dumps(sorted(words)))


def forget_words_seen(lane: object = None) -> None:
    drop_state(words_seen_path(lane))


# 2026-10-05. THE NEWEST LEDGER EVENT A LANE HAS BEEN SHOWN. The combat
# page's "Since last page" line prints only the events past it. The ledger's
# sequence rises across a game process and starts above the last process's
# (it is seeded off the clock), so a stale number here can only hide events
# from a game that is gone.
def events_seen_path(lane: object = None) -> Path:
    return lane_state_dir(lane) / f"_blindplay-events-lane{lane_tag(lane)}.json"


def read_events_seen(lane: object = None) -> int:
    blob = read_state_json(events_seen_path(lane))
    return blob if isinstance(blob, int) else 0


def write_events_seen(seq: int, lane: object = None) -> None:
    # A read-only tree repeats its events.
    write_atomic(events_seen_path(lane), json.dumps(int(seq)))


def forget_budget(lane: object = None) -> None:
    """Drop this lane's budget. The operator's reset, and the tests'."""
    drop_state(budget_path(lane))

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

# ------------- 2026-09-26: the Crystal Sphere's divinations, one verb each --
#
# THE STALL (the Furina supporting-pool seat round, lanes 1 and 2). After
# paying for *Uncover Future* the page printed `TOOL-BLOCKED: crystal_sphere`
# and one verb, `leave`; `leave` posted `crystal_sphere_proceed` and the game
# answered "Crystal Sphere proceed button is not enabled", five times in a
# row, because the minigame still owed its divinations (`can_proceed: False`,
# "3 Divinations remain"). The game lets nobody leave before they are spent.
#
# So while divinations remain the page offers `reveal`: it spends one on the
# FIRST hidden cell in the feed's own order (top row first) with the tool the
# game has selected -- selecting one first where none is, which is the whole
# of that `reveal`. The cell is chosen by position alone: nothing about what a
# cell hides crosses to the page, so the seat is choosing to spend, not
# choosing what to find. `leave` is offered once the game lets the run go on.
SPHERE_REVEAL = "reveal"
SPHERE_REVEAL_HOW = ("the sphere still owes its divinations ({left}), and "
                     "the game will not let the run go on until they are "
                     "spent. Say `reveal` to spend one on the next hidden "
                     "cell; `leave` is offered once they are gone")


# The two sphere reads live in `understudy/crystal_sphere.py` so the soak can
# drive the same divinations without importing a blindplay module.
from understudy.crystal_sphere import (  # noqa: E402,F401  (re-export)
    sphere_owes, sphere_reveal_action)

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
                      "On that screen you can say `reveal` to spend each "
                      "divination on the next hidden cell, and then `leave` "
                      "to carry on with the run; what you spend here is "
                      "spent, and the cells are not chosen for what they "
                      "hide",
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

# 2026-09-26 (control seats). How many times an event room drawn with no
# options is re-asked before it is drawn as it stands (`settle_event`).
EVENT_SETTLE_TRIES = 6

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
# THE HAZARDS THE MOD ITSELF DEFUSES UNDER INSTANT (2026-09-29). Since #733
# `PunchOffInstantGuardPatch.cs` skips `PunchOff.PunchEachOther` whenever
# `PrefsSave.FastMode` is `Instant`, which every embarked seat lane runs at --
# so on such a lane the room is an ordinary event, and refusing it only killed
# the run (a Sonnet seat, 2026-09-29). The refusal stays wherever the live
# FastMode is anything else or cannot be read (`blindplay_faces._hazard`).
INSTANT_GUARDED_HAZARDS = frozenset({"PUNCH_OFF"})


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
