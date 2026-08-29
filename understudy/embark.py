"""EB-167/EB-168: the OPERATOR side of a blind-play session -- get a run open.

`blindplay session` deliberately attaches to a run already in progress. It
stops on a menu and says so rather than driving one, and the reason is
structural rather than fastidious: launching the game means `soak.Session`, and
importing `soak` from the design-blind module would drag `policy_v1` and every
tier0 sheet loader across the line that module exists to hold
(`tier0/tests/test_understudy_blindplay.py` pins it, and this file is pinned
there too -- `blindplay` may never import THIS one either).

So the launch lives out here, on the operator's side of the line, exactly as
`staged_turn stage --hold` puts a staged board in front of a person: this
module owns `soak.Session`'s launch / readiness / embark / speed path, writes
the reversibility ledger, and then STOPS -- game up, bridge up, run open,
nothing torn down. What comes next is a person running
`python -m understudy.blindplay session`.

    python -m understudy.embark --character kokomi
    python -m understudy.embark --character kokomi --hold      # attach, no launch
    python -m understudy.embark --teardown                     # put it all back

THE SEED IS READ BACK, NEVER ASSUMED (R95). The embark path passes no seed on
the read-back arm, the game rolls one, and `bridge.current_seed()` is asked
after the run exists. That string is what the sealed record carries, and it is
also the one string the leak audit greps every observation for -- a tester who
can see the seed is not blind.

REVERSIBILITY ACROSS TWO PROCESSES. `soak.Session` reverts what it recorded
using entries it holds in memory, which is right for a soak that owns its whole
lifetime and wrong for a hold that ends in a different process. So the ledger
path and the stamp go into a sidecar (`understudy/logs/embark-<stamp>.json`),
and `--teardown` rebuilds the session from the ledger ON DISK and walks
`Session.teardown` -- soak's own undo steps, not a second copy of them. Every
entry still marked APPLIED is re-bound; anything already REVERTED is left
alone.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

from understudy import bridge, report, soak

LOG_DIR = Path(__file__).resolve().parent / "logs"

# Which ledger row feeds which of `Session`'s undo steps. Matched on the
# recorded `change` text because that text is what the ledger persists -- the
# alternative is a second copy of the step order living here, drifting from
# soak's.
_LEDGER_SLOTS = (
    ("_seed_entry", "May set a chosen run seed"),
    ("_speed_entry", "Set FastMode=Instant"),
    ("_launch_entry", "Launched `"),
    ("_bridge_entry", "Deployed `mods"),
    ("_appid_entry", "Created `steam_appid.txt`"),
)


class EmbarkError(RuntimeError):
    """The game, the bridge or the ledger is not in a state this can work on."""


def option_id(name: str) -> str:
    """A roster id or a select-screen option id, folded onto the option id.

    `soak._embark` compares against the character-select screen's own option
    strings, so `--character kokomi` would match nothing and embark on whatever
    was highlighted -- which is EB-117, and it cost a run. Accepting the short
    name and expanding it here is the cheap half of that lesson.
    """
    raw = str(name or "").strip()
    if not raw:
        raise EmbarkError("no character given")
    if raw.upper().startswith("KLEEMOD-"):
        return raw.upper()
    return f"KLEEMOD-{raw.upper()}"


# ------------------------------------------------------------- the embark --

def embark(character: str, *, hold: bool = False,
           chosen_seed: str | None = None) -> dict[str, Any]:
    """Launch (or attach), embark, read the seed back, and LEAVE IT RUNNING.

    Returns the sidecar dict. Raises rather than tearing down on failure: a
    half-open game the operator can look at is worth more than a clean
    directory and no diagnosis, and `--teardown` puts it back either way.
    """
    who = option_id(character)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    soak.LOG_DIR.mkdir(parents=True, exist_ok=True)
    session = soak.Session(stamp, do_setup=not hold, intent="")
    sidecar = {
        "stamp": stamp,
        "ledger": str(session.ledger.path),
        "character_requested": who,
        "hold": hold,
        "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    _write_sidecar(stamp, sidecar)

    session.setup()
    driver = soak.RunDriver(session, 1, stamp, character=who,
                            chosen_seed=chosen_seed, max_fights=0)
    try:
        state = driver._to_main_menu()
        state = driver._embark(state)
        state = driver._verify_character(state)
    except soak.Defect as d:
        raise EmbarkError(f"{d.kind}: {d.detail}") from None
    seed = bridge.current_seed() or ""

    sidecar.update({
        "character_actual": driver.character_actual,
        # R95: read off the wire AFTER the run exists. Never the requested one.
        "run_seed": seed,
        "screen": str(state.get("state_type") or "unknown"),
        "floor": int(((state.get("run") or {}).get("floor")) or 0),
        "run_log": str(driver.log),
    })
    _write_sidecar(stamp, sidecar)
    return sidecar


# ------------------------------------------------------------- the sidecar --

def sidecar_path(stamp: str) -> Path:
    return LOG_DIR / f"embark-{stamp}.json"


def _write_sidecar(stamp: str, blob: dict[str, Any]) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    sidecar_path(stamp).write_text(json.dumps(blob, indent=1) + "\n",
                                   encoding="utf-8")


def _is_hold(path: Path) -> bool:
    try:
        return bool(json.loads(path.read_text(encoding="utf-8")).get("hold"))
    except (OSError, ValueError):                            # noqa: PERF203
        return False


def latest_stamp() -> str:
    """The most recent embark that actually CHANGED something, or an error.

    A `--hold` embark attaches to a game somebody else launched and records no
    ledger rows at all, so it has nothing to tear down -- and picking one as
    "the latest" would hide the launch that DOES need reverting behind it.
    They are skipped here and answered by name below.
    """
    found = [p for p in sorted(LOG_DIR.glob("embark-*.json"))
             if not _is_hold(p)]
    if not found:
        raise EmbarkError(
            f"no launching embark sidecar in {LOG_DIR}; there is nothing to "
            f"tear down (if the game was launched by hand, close it by hand "
            f"and run `klee-mod\\build\\deploy_bridge.ps1 -Remove`)")
    return found[-1].stem[len("embark-"):]


def teardown(stamp: str = "") -> str:
    """Walk the ledger ON DISK through `Session`'s own undo steps."""
    stamp = stamp or latest_stamp()
    blob = json.loads(sidecar_path(stamp).read_text(encoding="utf-8"))
    if blob.get("hold"):
        return (f"embark {stamp} was a --hold: it attached to a game somebody "
                f"else launched, changed nothing in the game directory, and "
                f"has nothing to revert.")
    ledger_path = Path(blob["ledger"])
    if not ledger_path.exists():
        raise EmbarkError(f"the ledger named by the sidecar is gone: "
                          f"{ledger_path}")
    entries = json.loads(ledger_path.read_text(encoding="utf-8"))
    session = soak.Session(stamp, do_setup=False, intent="")
    session.ledger.path = ledger_path
    session.ledger.entries = entries
    for attr, marker in _LEDGER_SLOTS:
        match = next((e for e in entries
                      if str(e.get("change", "")).startswith(marker)
                      and e.get("state") == "APPLIED"), None)
        setattr(session, attr, match)
    session.teardown()
    return session.ledger.table()


# -------------------------------------------------------------------- CLI --

def main(argv: list[str] | None = None) -> int:
    report.console_safe()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--character", default="kokomi",
                    help="a roster id (kokomi) or the select-screen option id "
                         "(KLEEMOD-KOKOMI)")
    ap.add_argument("--hold", action="store_true",
                    help="attach to a game somebody else launched: no bridge "
                         "deploy, no launch, no speed change, and nothing "
                         "recorded on the ledger for those")
    ap.add_argument("--seed", default=None,
                    help="embark on a CHOSEN seed instead of one the game "
                         "rolls; the read-back still decides what is recorded")
    ap.add_argument("--teardown", action="store_true",
                    help="revert an earlier embark: seed, speed, process, "
                         "bridge, steam_appid.txt, in that order")
    ap.add_argument("--stamp", default="",
                    help="which embark to tear down; the newest by default")
    args = ap.parse_args(argv)

    try:
        if args.teardown:
            print(teardown(args.stamp))
            return 0
        blob = embark(args.character, hold=args.hold, chosen_seed=args.seed)
    except EmbarkError as exc:
        print(f"embark error: {exc}", file=sys.stderr)
        return 2

    print(f"stamp:     {blob['stamp']}")
    print(f"character: {blob.get('character_actual') or '(unread)'}")
    print(f"run seed:  {blob.get('run_seed') or '(unread)'}   "
          f"(read back off the wire, R95)")
    print(f"screen:    {blob.get('screen')}  floor {blob.get('floor')}")
    print(f"sidecar:   {sidecar_path(blob['stamp'])}")
    print()
    print("The game is UP and the run is OPEN. Nothing has been torn down.")
    print("  python -m understudy.blindplay observe")
    print("  python -m understudy.blindplay session --max-actions N")
    print("  python -m understudy.embark --teardown")
    return 0


if __name__ == "__main__":
    sys.exit(main())
