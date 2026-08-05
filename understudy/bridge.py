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
