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
import time
import urllib.error
import urllib.request

BASE = "http://localhost:15526"
SINGLEPLAYER = f"{BASE}/api/v1/singleplayer"
COMPENDIUM = f"{BASE}/api/v1/compendium"
SPEED = f"{BASE}/api/v1/gits/speed"
SEED = f"{BASE}/api/v1/gits/seed"
GIVE_CARD = f"{BASE}/api/v1/gits/give_card"
DEBUG_STATE = f"{BASE}/api/v1/gits/debug_state"


class BridgeError(RuntimeError):
    pass


def _request(url: str, payload: dict | None = None, timeout: float = 20.0) -> dict:
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


def current_seed() -> str | None:
    """The seed the GAME generated for the active run.

    Recorded, never fed to a policy stream -- see understudy/rng.py.
    """
    try:
        c = compendium()
    except BridgeError:
        return None
    run = c.get("current_run") or {}
    return run.get("seed")


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

DEBUG_OPS = ("set_resource", "set_energy", "set_hp", "set_block", "set_power")


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
