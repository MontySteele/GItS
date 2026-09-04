"""Thin client for the vendored STS2MCP HTTP bridge.

Wire contract: `vendor/STS2_MCP/docs/raw-simplified.md`. Everything here is
stdlib -- the repo's CI installs pytest/pyyaml/pillow/numpy and nothing else,
and a harness that needs `requests` is a harness that does not run on a fresh
clone.

The bridge is turn-taking: GET to see `state_type`, POST the verb that
`state_type` advertises. Two things about that loop are worth stating because
both cost a session's time to learn the hard way:

1. The HTTP server comes up ~5s after launch, well BEFORE the main menu has
   buttons. `GET /` returning ok is not "the game is ready"; the main menu
   with a populated `options` list is.
2. `state_type: "overlay"`, and a `menu_screen` with no `options`, are the two
   shapes a soft-lock takes. Neither raises. A watchdog has to look for them.
"""

from __future__ import annotations

import json
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

from understudy import instances

BASE = "http://localhost:15526"
SINGLEPLAYER = f"{BASE}/api/v1/singleplayer"
COMPENDIUM = f"{BASE}/api/v1/compendium"
SPEED = f"{BASE}/api/v1/gits/speed"
SEED = f"{BASE}/api/v1/gits/seed"
GIVE_CARD = f"{BASE}/api/v1/gits/give_card"
DEBUG_STATE = f"{BASE}/api/v1/gits/debug_state"
METER_LEDGER = f"{BASE}/api/v1/gits/meter_ledger"


class BridgeError(RuntimeError):
    pass


class LaneCrossed(BridgeError):
    """This lane was answered with ANOTHER lane's run (`EB-210`).

    A BridgeError so every existing caller's `except` still catches it, and a
    subclass so the two callers that can say something better may.
    """


# ------------------------------------------------------ which game this is --
#
# TWO LANES, TWO BRIDGES, AND A THREAD-LOCAL RATHER THAN A `Bridge` OBJECT.
#
# The choice was between threading an object through every caller and keeping
# the free functions with a current-instance beside them. The free functions
# won on size and on blast radius: fourteen module-level functions and six
# module-level URL constants are called from `soak`, `staged_turn`,
# `scenario`, `harness`, `embark`, `blindplay` and `local_tester`, and three
# test modules assert on `bridge.SEED` / `bridge.GIVE_CARD` by identity. A
# `Bridge` object is a rewrite of all of that; a current-instance is this
# block plus one line in `_request`, and every existing caller and every
# existing test keeps working unchanged.
#
# IT IS THREAD-LOCAL AND NOT A PLAIN GLOBAL, because the two-lane round runs
# its lanes in THREADS in one process. A plain global would give the two lanes
# one port -- the exact bug this build exists to remove, moved from the mod
# side to ours. A thread that never sets one reads the process default, so
# nothing that is not lane-aware changes behaviour.
#
# The URL constants above stay spelled with lane 0's base. `_request` rebases
# every URL onto the CURRENT base at call time, so a constant is a path
# carrier and never a promise about which game answers it.
#
# AND BENEATH THE THREAD-LOCAL, ONE ENVIRONMENT VARIABLE: `GITS_LANE`.
# `blindplay observe` / `act` / `session` are the whole-run commands with no
# lane flag, and they cannot be given one the ordinary way -- that module is
# design-blind and may not import `instances` or `soak`
# (`test_understudy_blindplay` pins both ends of the line), so a `--lane` there
# would have to reach the lane registry through an import that is forbidden.
# It reaches it through THIS module instead, which every one of those commands
# already calls. The order is: an explicit `use()` on this thread FIRST (a
# two-lane round binds its workers and must never be second-guessed by whatever
# the operator exported), then the variable, then lane 0.
#
# `GITS_LANE=0`, and an unset variable, both resolve to NO instance rather
# than to lane 0's -- the same distinction `instances.cli_lane` makes, and for
# the same reason: lane 0 is the machine's own `%APPDATA%` and the default
# port, which is what an unbound thread already does.

_local = threading.local()


def env_instance():
    """The lane `GITS_LANE` names, or `None` for lane 0 / unset.

    WIRE-ONLY (`instances.wire_lane`): a client needs the port and the user
    tree and has no business resolving where the game is installed. `bridge`
    is imported by tests on machines with no `klee-mod/local.props` at all,
    and `instances.lane()` would `SystemExit` on them.
    """
    label = instances.env_label()
    return (None if label == instances.DEFAULT_LABEL
            else instances.wire_lane(label))


def current_base() -> str:
    """The base URL this thread's calls go to."""
    bound = getattr(_local, "base", None)
    if bound is not None:
        return bound
    inst = env_instance()
    return BASE if inst is None else inst.base


def current_label() -> str:
    """This thread's lane label, for record rows. `lane0` unless set."""
    bound = getattr(_local, "label", None)
    if bound is not None:
        return bound
    inst = env_instance()
    return instances.DEFAULT_LABEL if inst is None else inst.label


def current_instance():
    """The `instances.Instance` this thread is bound to, or `None`.

    Kept beside the base and the label because `EB-210`'s check needs the
    lane's `appdata`, not just its port: the crossing it exists to catch is
    about which USER TREE answered, and the port cannot say. That is also why
    the `GITS_LANE` fallback returns a whole instance rather than a port: a
    lane-1 blind session gets the crossing check and the per-lane `godot.log`
    cursor (`scenario._LogWindow`) out of the same one answer.
    """
    bound = getattr(_local, "instance", None)
    return bound if bound is not None else env_instance()


def use(instance) -> None:
    """Point THIS THREAD's calls at `instance` (an `instances.Instance`)."""
    _local.base = instance.base
    _local.label = instance.label
    _local.instance = instance


def use_default() -> None:
    """Undo `use` for this thread."""
    for attr in ("base", "label", "instance"):
        if hasattr(_local, attr):
            delattr(_local, attr)


def _rebase(url: str) -> str:
    base = current_base()
    if base == BASE or not url.startswith(BASE):
        return url
    return base + url[len(BASE):]


def _request(url: str, payload: dict | None = None, timeout: float = 20.0) -> dict:
    url = _rebase(url)
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            raise BridgeError(f"HTTP {e.code} from {url}: {body[:400]}") from e
    except urllib.error.URLError as e:
        raise BridgeError(f"bridge unreachable at {url}: {e}") from e
    except OSError as e:
        # A GAME THAT DIES MID-REQUEST DOES NOT RAISE URLError. It resets the
        # socket, and `ConnectionResetError` (an OSError, not a URLError)
        # escaped this function during a soak -- past the driver's watchdog,
        # which is written to catch BridgeError, and then past the teardown,
        # which left `steam_appid.txt` and `mods\STS2_MCP` in the game
        # directory. Every failure to reach the bridge is a BridgeError,
        # including the ones the stdlib does not spell that way.
        raise BridgeError(f"bridge connection failed at {url}: "
                          f"{type(e).__name__}: {e}") from e


def health() -> dict:
    return _request(BASE + "/")


def get_state() -> dict:
    return _request(SINGLEPLAYER)


def post(action: str, **params) -> dict:
    return _request(SINGLEPLAYER, {"action": action, **params})


def compendium() -> dict:
    return _request(COMPENDIUM)


def current_run() -> dict:
    """The compendium's `current_run` block, or `{}` if nothing answers.

    IT IS NOT AN IN-MEMORY READ, AND THAT IS THE WHOLE OF `EB-210`. The mod
    builds this block by opening `current_run.save` OFF DISK
    (`vendor/STS2_MCP/McpMod.Compendium.cs`, `BuildCurrentRunContext` ->
    `ResolveCurrentRunPath`), and it reports the file it opened as
    `save_path`. So a lane reads the seed of whatever run owns the file that
    resolution landed on -- which, before the fix in that file, was lane 0's
    for BOTH lanes.
    """
    try:
        c = compendium()
    except BridgeError:
        return {}
    run = c.get("current_run")
    return run if isinstance(run, dict) else {}


def _refuse_foreign_save(run: dict) -> None:
    """`EB-210`. Refuse a `current_run` block that came from another lane.

    THE CHECK IS ON THE FILE, BECAUSE THE FILE IS WHAT CROSSED. Lane 1 runs
    with its own `APPDATA`, which is what Godot resolves `user://` through --
    but `Environment.GetFolderPath(SpecialFolder.ApplicationData)`, which the
    mod's save-root enumeration used, reads the SHELL folder and ignores that
    variable entirely (verified: `APPDATA=<anywhere else> powershell -c
    [Environment]::GetFolderPath('ApplicationData')` still answers the real
    roaming path). So lane 1 asked for its own seed, its own game embarked on
    it -- `godot.log`: "Embarking on a singleplayer KLEEMOD-KLEE run ... Seed:
    NMQLUYZDLV" in lane 1's own tree -- and the read-back opened lane 0's
    `current_run.save` and answered `R7W86HG7WHUD`. The round then filed
    `seed_not_honoured` against a game that had honoured the seed exactly.

    The mod-side fix is in `McpMod.Compendium.cs`. This is the harness-side
    lock, and it is worth keeping after that fix for the reason every
    read-back exists: a seed that is silently somebody else's cannot be
    detected afterwards, from the numbers, by anyone.

    LANE 0 AND EVERY UNBOUND THREAD ARE UNCHANGED. A lane with no `appdata`
    (which is lane 0 by construction, `instances.LANES`) has no tree of its
    own to be outside of, so there is nothing here to check and nothing here
    fires.
    """
    inst = current_instance()
    home = getattr(inst, "appdata", None)
    if home is None:
        return
    where = str(run.get("save_path") or "")
    if not where:
        # The block says it has no file yet (`limitation`), which is a state
        # this endpoint legitimately reports right after an embark. Not a
        # crossing, and not this function's business.
        return
    try:
        inside = Path(where).resolve().is_relative_to(Path(home).resolve())
    except (OSError, ValueError):
        inside = False
    if not inside:
        raise LaneCrossed(
            f"lane {current_label()} was answered with a run from another "
            f"lane's user tree: current_run.save resolved to {where!r}, which "
            f"is not under this lane's APPDATA ({home}). EB-210 -- the seed "
            f"read-back is a FILE read and the file crossed; nothing about "
            f"this lane's own run is wrong.")


def current_seed() -> str | None:
    """The seed the GAME generated for the active run.

    Recorded, never fed to a policy stream -- see understudy/rng.py. Raises
    `LaneCrossed` rather than answering with another lane's seed (`EB-210`).

    ONE READ, TAKEN NOW. A caller that has just embarked wants
    `seed_read_back` below instead: there is a window in which this answers
    about the wrong file, and `EB-435` is what it cost.
    """
    run = current_run()
    _refuse_foreign_save(run)
    return run.get("seed")


#: How long `seed_read_back` waits for the game to write its OWN
#: `current_run.save`. Generous rather than tight: the window measured on
#: 2026-09-04 was the several seconds of asset preloading that follow an
#: embark, and waiting too long costs a slow refusal while waiting too little
#: costs a run recorded against somebody else's seed.
SEED_READ_BACK_WAIT_S = 30.0


def seed_read_back(wait: float = SEED_READ_BACK_WAIT_S,
                   poll: float = 0.5) -> str | None:
    """The seed of THIS lane's run, waited for rather than snatched (`EB-435`).

    THE READ-BACK RACES THE GAME'S OWN SAVE, AND ON A LONE LANE IT LOST. The
    compendium's `current_run` block is built by opening `current_run.save`
    OFF DISK, and the harness's own route to the main menu abandons the
    profile's leftover run on the way -- `NMainMenu.AbandonRun` ->
    `RunSaveManager.DeleteCurrentRun`, which DELETES that file. The new run
    does not write its first one until several seconds later, after the
    `Common` and character asset preloads. Asked inside that window the mod
    finds no file in this process's tree, walks on to the next save root it
    knows -- the machine's own `%APPDATA%` -- and answers with a run from
    months ago. `_refuse_foreign_save` caught it, correctly, and two lone-lane
    Klee soaks died at `seed_read_back_crossed` (2026-09-04) with nothing
    whatever wrong with them.

    So the window is waited out here rather than read as a verdict: poll until
    the block resolves to a file inside THIS lane's tree AND names a seed, and
    only then answer. What is refused at the deadline is what was actually
    seen -- the crossing, if one was still standing, and otherwise the plain
    (unrefused) fact that this lane has no seed to read.

    `wait=0` is a single read and exactly `current_seed`'s behaviour, which is
    what every caller not reading back a just-started run should keep.
    """
    deadline = time.time() + max(0.0, float(wait))
    crossed: LaneCrossed | None = None
    while True:
        run = current_run()
        try:
            _refuse_foreign_save(run)
        except LaneCrossed as exc:
            crossed = exc
        else:
            seed = run.get("seed")
            if seed:
                return seed
            # In-tree and seedless is not a crossing: forget any earlier one
            # rather than raising it over a state that has since resolved.
            crossed = None
        if time.time() >= deadline:
            if crossed is not None:
                raise crossed
            return run.get("seed")
        time.sleep(max(0.0, float(poll)))


def set_speed(enabled: bool, time_scale: float | None = None) -> dict:
    payload: dict = {"enabled": bool(enabled)}
    if time_scale is not None:
        payload["time_scale"] = time_scale
    return _request(SPEED, payload)


def get_speed() -> dict:
    return _request(SPEED)


# --------------------------------------------------------- chosen seeds ----
#
# P1.5 item 1. `set_seed` must be called while the CHARACTER SELECT screen is
# up and before the embark `confirm`, for a reason that is the game's and not
# ours: `NCharacterSelectScreen.AfterInitialized()` sets
# `NGame.DebugSeedOverride = null` when the screen opens, so a seed chosen
# earlier is wiped by the screen it was chosen for. The endpoint reports which
# of its two routes fired (`lobby` or `debug_override`); callers that care
# should read `route` rather than assume.
#
# THE CHOSEN SEED IS NOT A POLICY INPUT. It is stamped on the log and compared
# against the read-back, and that is all. `understudy/rng.py` still refuses a
# stream label of this shape, and this function does not change that.


def set_seed(seed: str) -> dict:
    """Choose the seed of the NEXT run. Returns the endpoint's report."""
    return _request(SEED, {"seed": seed})


def clear_seed() -> dict:
    """Release both seed channels, so the next run rolls its own again.

    The `debug_override` route is GLOBAL and STICKY; leaving it set would make
    every subsequent run in the session the same run. Teardown calls this
    whether or not a seed was ever chosen.
    """
    return _request(SEED, {"seed": None})


def get_seed() -> dict:
    return _request(SEED)


# ------------------------------------------------------ dev card grants ----
#
# EB-52. `POST /api/v1/gits/give_card` puts a CHOSEN card in the deck (or in a
# combat pile) through the game's own acquisition path -- `RunState.CreateCard`
# + `CardPileCmd.Add`, the pair a card reward runs, for `pile="deck"`; and
# `CombatState.CreateCard` + `AddGeneratedCardToCombat`, the pair every
# in-combat generator runs, for the three combat piles (EB-91: the scope is
# part of the path, and the response's `route`/`scope` fields say which one
# ran). A combat-scoped grant is a GENERATED card -- it is not in the deck and
# does not outlive the fight; `pile="deck"` is the grant that persists. It exists
# because EB-52(a)'s obstacle is acquisition, not instrumentation: the Fanfare
# floor is already on the wire, and what could not be arranged in three live
# sessions was getting one of three RARE Powers into a deck.
#
# THIS IS NOT A MEASUREMENT DOOR, AND THE STAMP IS THE ENFORCEMENT. A run that
# used it is not a run the generators produced, so no number off it is
# comparable to any other run's. The endpoint says so in a `guardrail` field on
# every success; `GRANT_GUARDRAIL` below is the harness-side copy, and callers
# that log a grant are expected to log it beside them. Guardrail-7 is unchanged
# either way -- a bot still cannot see the screen.

GRANT_GUARDRAIL = (
    "dev card grant: this run's deck is not one the generators produced, so "
    "nothing measured on it is comparable to any other run")

GRANT_PILES = ("deck", "hand", "draw", "discard")


def give_card(card_id: str, count: int = 1, upgraded: bool = False,
              pile: str = "deck") -> dict:
    """Grant `count` copies of `card_id`. Returns the endpoint's report.

    `card_id` is the wire id (`UNHEARD_CONFESSION`), or the exact printed
    title; there is no fuzzy match here or on the far side, because
    `/api/v1/wiki?query=` is already the search surface and a near-miss grant
    is a card nobody asked for sitting in a deck for the rest of a run.

    The grant is QUEUED on the game's side and confirmed by the next
    `get_state()`, the same way a card play is. A `status: "error"` answer
    comes back as an ordinary dict, not an exception -- that is this module's
    convention for the bridge's two error shapes.
    """
    if pile not in GRANT_PILES:
        raise ValueError(f"pile must be one of {GRANT_PILES}, not {pile!r}")
    return _request(GIVE_CARD, {"card_id": card_id, "count": int(count),
                                "upgraded": bool(upgraded), "pile": pile})


def give_card_info() -> dict:
    """The route's own description, including whether a run is in progress."""
    return _request(GIVE_CARD)


# ---------------------------------------------------- the meter ledger ----
#
# `EB-216` / R225's clause. `GET /api/v1/gits/meter_ledger` -> the per-play
# ledger the mod keeps: for every card played, bank before, price paid, gains
# BY SOURCE (the engine event that made each one -- the starter relic's
# detonation refund, a kit response, a card rider) and bank after.
#
# IT IS ITS OWN ROUTE AND NOT PART OF THE STATE, deliberately: the state
# payload is what `blindplay` builds the TESTER'S page out of, and the ledger
# names engine events in a developer's vocabulary. A grading surface (R101b)
# is easiest to keep clean by never putting the material on the same payload.


def meter_ledger() -> dict:
    """The ledger's rows, oldest first.

    `available: False` with an empty list means "this build has no klee mod to
    ask", which is a different fact from "nothing has moved a meter yet" --
    and the caller is entitled to tell them apart, so neither is flattened
    into an empty answer here.
    """
    return _request(METER_LEDGER)


# ------------------------------------------------------ board setup -------
#
# EB-142. `POST /api/v1/gits/debug_state` sets one combat number through the
# game's own mutator for it: `CreatureCmd.SetCurrentHp`, `PlayerCmd.SetEnergy`,
# a registered CustomResource's own `Amount` setter, or the creature's own
# block-internal pair. Singleplayer and in-combat only, and it refuses
# multiplayer for the identical reason `give_card` does.
#
# EB-146 ADDS `set_power`, THE FIFTH OP, AND IT IS THE ONE THAT REACHES SPARKS.
# Sparks are a `PowerModel` and not a registered CustomResource, so
# `set_resource` cannot move them and both Klee scenarios had to climb the bank
# by playing Sparkly Treasure. `set_power` resolves a power out of
# `ModelDb.AllPowers` by the id the WIRE prints on a status row (`SPARK_POWER`)
# or by its printed Title, and applies / stacks / clears it through
# `PowerCmd.Apply` / `ModifyAmount` / `Remove` -- the three commands every card
# in the game uses, with `applier: null` so nothing lands in the
# ModifyPowerAmountGiven chain (`SparkPower.Spend`'s own reasoning). It refuses
# an unknown power id, an ambiguous TITLE, a creature that cannot receive
# powers, a negative amount on a power that does not allow negatives, and a
# power the creature carries more than one instance of.
#
# THE NUMBER IT WRITES IS THE STACK COUNT; THE WIRE PRINTS `DisplayAmount`.
# Those are equal for most powers and deliberately unequal for at least one:
# `BombPower.Amount` is the bomb COUNT and its badge shows total pending
# damage. A scenario asserting `expect: {power: ...}` is reading the badge.
#
# IT IS THE SAME KIND OF DOOR AS `give_card` AND IS DISQUALIFYING IN THE SAME
# WAY. A combat whose board was set by hand is not a board the game's own play
# produced, so nothing measured on it is comparable to any other run. The
# endpoint stamps its OWN `guardrail` field on every success (the wording is
# about the board, not the deck); the harness-side sentence a scenario log
# carries on every row is `GRANT_GUARDRAIL` above, unchanged and shared with
# the grant door, because one caveat a reader reads beats two near-identical
# ones a reader learns to skip. Guardrail-7 is unchanged either way: a bot
# cannot see the screen.
#
# WHY `why` IS A REQUIRED ARGUMENT HERE AND NOT AN OPTIONAL ONE. The endpoint
# refuses a write without it (HTTP 400), which is the same rule
# `harness give-card --why` follows, made structural. A board change nobody can
# account for six months later is worse than no scenario.
#
# THREE OPS ANSWER `queued`. `set_hp`, `set_energy` and `set_power` go through
# async commands that run visuals, so the endpoint queues them and the response
# says `queued: true`; the value is confirmed by the next `get_state()`.
# `set_block` and `set_resource` are synchronous and report the real
# before/after pair. Callers that assert on a queued write must settle first --
# see `understudy/scenario.py`, which does. A `set_power` asking for the amount
# already standing writes nothing and answers `queued: false`.

# EB-165 ADDS `clear_hand`, THE SIXTH OP, AND IT IS THE ONLY ONE THAT MOVES A
# CARD RATHER THAN A NUMBER. The game deals its own opening hand, so a staged
# turn that grants five cards is staged with ten in hand -- reproducible on its
# pinned seed and not EXACT, which is what a design-blind packet needs it to
# be. `clear_hand` empties the hand BEFORE the grants go in, through
# `CardPileCmd.Add(card, PileType.Draw, CardPilePosition.Bottom)`: the pile
# move that sits UNDERNEATH `CardCmd.Discard` and `CardCmd.Exhaust`, so no
# on-discard or on-exhaust trigger fires and no combat-history row is written.
# `Hook.AfterCardChangedPiles` still fires, because every pile move in the game
# runs it and there is no route out of hand beneath it. It takes no `who` and
# no `amount`; `before` is the number of cards it moved.
DEBUG_OPS = ("set_resource", "set_energy", "set_hp", "set_block", "set_power",
             "clear_hand")


def debug_state(op: str, why: str, amount: int = 0, who: str = "player",
                resource: str = "", power: str = "") -> dict:
    """Set one combat number. Returns the endpoint's report.

    A `status: "error"` answer comes back as an ordinary dict, not an
    exception -- this module's standing convention for the bridge's two error
    shapes, and the debug door does not get to be the exception.
    """
    if op not in DEBUG_OPS:
        raise ValueError(f"op must be one of {DEBUG_OPS}, not {op!r}")
    if not str(why).strip():
        # Refused client-side because the answer is knowable client-side, the
        # same reason an unknown pile is refused in `give_card`. A round trip
        # to learn that the reason field was empty is a round trip that only
        # happens when a live game is up.
        raise ValueError("debug_state needs a --why: every board write is "
                         "logged with its reason")
    return _request(DEBUG_STATE, {"op": op, "amount": int(amount),
                                  "who": who, "resource": resource,
                                  "power": power, "why": str(why)})


def debug_state_info() -> dict:
    """The route's own description: ops, registered resources, living ids."""
    return _request(DEBUG_STATE)


def set_resource(name: str, amount: int, why: str) -> dict:
    return debug_state("set_resource", why, amount=amount, resource=name)


def set_energy(amount: int, why: str) -> dict:
    return debug_state("set_energy", why, amount=amount)


def set_hp(who: str, amount: int, why: str) -> dict:
    return debug_state("set_hp", why, amount=amount, who=who)


def set_block(who: str, amount: int, why: str) -> dict:
    return debug_state("set_block", why, amount=amount, who=who)


def set_power(who: str, name: str, amount: int, why: str) -> dict:
    """Set one power's STACK COUNT on one creature. `amount=0` removes it.

    `name` is the wire's own power id (`SPARK_POWER`, the string a status row
    carries) or the printed Title (`Spark`); the endpoint matches the id first
    and the title second, and refuses a title two powers share.

    THE COUNT IS ALL IT SETS. A power that carries a payload beside its stack
    count is not set by setting the count: `BombPower.Amount` is the bomb
    count and the per-bomb damages live in a list only `BombPower.Place`
    grows, so a `set_power BOMB_POWER 2` is two bombs that display nothing and
    detonate for nothing. Plain counters and durations only (Spark,
    Vulnerable, Weak, Strength); for anything else, play the card.
    """
    return debug_state("set_power", why, amount=amount, who=who, power=name)


def clear_hand(why: str) -> dict:
    """Empty the local player's hand to the BOTTOM of the draw pile (EB-165).

    Nothing is destroyed and nothing is discarded: the cards are moved through
    the game's own pile-move command, which fires no on-discard and no
    on-exhaust trigger. An already-empty hand answers `queued: false` rather
    than an error -- it is the state the caller asked for.
    """
    return debug_state("clear_hand", why)


def settle(prev_type: str | None = None, tries: int = 12, delay: float = 0.6) -> dict:
    """Poll until the screen stops being the one we just acted on.

    The action queue resolves over frames, so a GET issued immediately after a
    POST routinely reads the pre-action screen. Returns the last state read
    either way; callers decide whether an unchanged screen is a stall (it
    legitimately is not, mid-combat, where two plays in a row are normal).
    """
    state = get_state()
    for _ in range(tries):
        if prev_type is None or state.get("state_type") != prev_type:
            return state
        time.sleep(delay)
        state = get_state()
    return state
