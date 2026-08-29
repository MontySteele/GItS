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
    python -m understudy.embark --character klee --arm proto_spark_priced_draw
    python -m understudy.embark --teardown                     # put it all back

THE PROTOTYPE ARM DOOR (`EB-188`). The gate after a pair read ADVANCES an arm
is whole-fight blind play, automatically -- and it could not run for any arm,
because prototype rows are quarantined out of every pool by construction, so a
blind run cannot DRAW one. `--arm <proto id>` (repeatable) is the smallest
honest door: once the run is open, each named row is granted into the STARTING
DECK through the dev door, and the tester meets it the way it meets any other
card in the deck.

No C# was needed for it. `gits/GitsGiveCard.cs` with `pile: "deck"` already
reaches the MASTER DECK -- `player.RunState.CreateCard(canonical, player)`
then `CardPileCmd.Add(card, PileType.Deck)`, which is the pair a card reward
runs (`CardReward.OnSelected`), so every hook, history entry and relic trigger
a draft fires, this fires. The combat-scoped route (EB-91) is the other branch
of the same endpoint and is deliberately NOT what this uses: a combat-scoped
card is a generated card and does not outlive the fight.

THREE REFUSALS, each closing a way the run would otherwise be a lie about
itself:

  * A row that is not on `docs/prototype-surface.yaml`. The far side would
    answer `error: unknown card id`; refusing here names the id against the
    surface, which is the question the operator actually got wrong.
  * A RELEASE build. The prototype classes are `Compile Remove`d unless
    `PrototypeCards=true`, so the id does not exist in a shipped mod at all.
    The check is the deployed package's own version stamp: `deploy_proto.ps1`
    writes `+proto` into it and `deploy.ps1` never does.
  * A build version that cannot be READ. Not-read is refused rather than
    assumed to be a dev build -- a door that opens when it cannot see is not a
    door.

AND THE RUN SAYS SO. The grant, its guardrail and the build that carried it go
into the embark sidecar -- the run's own manifest, and the file `--teardown`
reads -- and `blindplay`'s sealed record names the arms in its identity block,
matched to the run by SEED so a stale sidecar cannot put its arms on somebody
else's run. A granted deck is not a deck the generators produced and nothing
measured on it is comparable to any other run; that sentence is
`bridge.GRANT_GUARDRAIL`, recorded beside the grant rather than left in a
comment.

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

from understudy import authorship, bridge, report, soak

LOG_DIR = Path(__file__).resolve().parent / "logs"

# EB-188. The build-metadata tag `klee-mod/build/deploy_proto.ps1` stamps onto
# the staged package version, and the one thing that separates a build holding
# the prototype classes from a build that never compiled them.
PROTO_TAG = "+proto"

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


# --------------------------------------------------------- prototype arms --

def wire_id(arm: str) -> str:
    """A prototype row id as `give_card` spells it: `KLEEMOD-PROTO_...`."""
    return f"KLEEMOD-{str(arm).strip().upper()}"


def check_arms(arms: list[str],
               version: tuple[str, str] | None = None) -> tuple[str, str]:
    """Refuse an arm that is not a row, or a build that cannot carry one.

    Returns `(build version, where it was read)` when the grant may proceed.
    `version` is injectable so the tests can put a release build, a dev build
    and an unreadable one in front of this without a game.
    """
    known = authorship.rows_authorship()
    unknown = [a for a in arms if a not in known]
    if unknown:
        raise EmbarkError(
            f"not prototype row(s) on {authorship.SURFACE.name}: "
            f"{', '.join(unknown)}. `--arm` names a row by its `id:`, and the "
            f"surface is the only place those ids exist -- a slice whose rows "
            f"have already left it cannot be granted (the deletion rule).")

    if version is None:
        # LAZY, and the direction matters. `blindplay` may never import this
        # module (it would drag `soak`, `policy_v1` and every tier0 sheet
        # loader into the design-blind side, and `test_understudy_blindplay`
        # pins both ends of that). The other direction is fine and is the
        # honest one: `build_version` reads the DEPLOYED package's own
        # manifest off disk, which is the same string the sealed record will
        # name, and duplicating that read here is how the two would disagree.
        from understudy import blindplay
        version = blindplay.build_version()
    build, source = version

    if not build:
        raise EmbarkError(
            f"the deployed build version could not be read ({source}), so "
            f"whether it carries the prototype surface is unknown. A grant is "
            f"refused on not-read rather than assumed: the row ids do not "
            f"exist in a release build at all.")
    if PROTO_TAG not in build:
        raise EmbarkError(
            f"the deployed build is {build!r} ({source}), which carries no "
            f"{PROTO_TAG!r}. Prototype classes are compiled out of a release "
            f"build entirely, so there is no id to grant -- stage a dev build "
            f"with klee-mod\\build\\deploy_proto.ps1 first.")
    return build, source


def grant_arms(arms: list[str]) -> list[dict[str, Any]]:
    """Grant each arm into the STARTING DECK. One report per arm.

    `pile="deck"` is the run-scoped route (`RunState.CreateCard` +
    `CardPileCmd.Add`), which is the one that persists past the first fight --
    a starting deck is the whole point. A `status: "error"` answer is the
    bridge's ordinary dict shape rather than an exception, so it is read and
    raised HERE: a run that half-granted its arms and carried on would produce
    a record naming cards the deck does not hold.
    """
    granted: list[dict[str, Any]] = []
    for arm in arms:
        card_id = wire_id(arm)
        reply = bridge.give_card(card_id, count=1, upgraded=False,
                                 pile="deck")
        if str(reply.get("status") or "").lower() != "ok":
            raise EmbarkError(
                f"granting {card_id} failed: "
                f"{reply.get('message') or reply}")
        granted.append({"arm": arm, "card_id": card_id, "pile": "deck",
                        "count": 1, "upgraded": False,
                        "card_name": reply.get("card_name") or "",
                        "message": reply.get("message") or ""})
    return granted


# ------------------------------------------------------------- the embark --

def embark(character: str, *, hold: bool = False,
           chosen_seed: str | None = None,
           arms: list[str] | None = None) -> dict[str, Any]:
    """Launch (or attach), embark, read the seed back, and LEAVE IT RUNNING.

    Returns the sidecar dict. Raises rather than tearing down on failure: a
    half-open game the operator can look at is worth more than a clean
    directory and no diagnosis, and `--teardown` puts it back either way.
    """
    who = option_id(character)
    wanted = list(arms or [])
    # BEFORE the launch. An unknown row id or a release build is a fact about
    # the machine and the request, not about the run, and finding it out after
    # the game is up costs a launch and a teardown for nothing.
    build, build_source = check_arms(wanted) if wanted else ("", "")

    stamp = time.strftime("%Y%m%d-%H%M%S")
    soak.LOG_DIR.mkdir(parents=True, exist_ok=True)
    session = soak.Session(stamp, do_setup=not hold, intent="")
    sidecar = {
        "stamp": stamp,
        "ledger": str(session.ledger.path),
        "character_requested": who,
        "hold": hold,
        "arms_requested": wanted,
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

    # EB-188. AFTER the run exists, because `pile: "deck"` is a RunState
    # acquisition and there is no deck to add to before that -- it is the
    # endpoint's own first refusal. Written into the sidecar with the
    # guardrail beside it, because a caveat that lives only in a comment is a
    # caveat that is not in the record.
    if wanted:
        sidecar["arms_granted"] = grant_arms(wanted)
        sidecar["arms_build_version"] = build
        sidecar["arms_build_version_source"] = build_source
        sidecar["arms_guardrail"] = bridge.GRANT_GUARDRAIL

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
    ap.add_argument("--arm", action="append", default=[], metavar="PROTO_ID",
                    dest="arms",
                    help="EB-188: grant a prototype row from "
                         "docs/prototype-surface.yaml into the STARTING DECK "
                         "once the run is open, so a blind whole-fight run "
                         "can meet an arm the pools quarantine. Repeatable. "
                         "Refused unless the deployed build is stamped "
                         "`+proto`")
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
        blob = embark(args.character, hold=args.hold, chosen_seed=args.seed,
                      arms=args.arms)
    except EmbarkError as exc:
        print(f"embark error: {exc}", file=sys.stderr)
        return 2

    print(f"stamp:     {blob['stamp']}")
    print(f"character: {blob.get('character_actual') or '(unread)'}")
    print(f"run seed:  {blob.get('run_seed') or '(unread)'}   "
          f"(read back off the wire, R95)")
    print(f"screen:    {blob.get('screen')}  floor {blob.get('floor')}")
    granted = blob.get("arms_granted") or []
    if granted:
        print(f"arms granted: "
              f"{', '.join(g['card_id'] for g in granted)}  into the deck "
              f"on {blob.get('arms_build_version')}")
        print(f"  {bridge.GRANT_GUARDRAIL}")
    print(f"sidecar:   {sidecar_path(blob['stamp'])}")
    print()
    print("The game is UP and the run is OPEN. Nothing has been torn down.")
    print("  python -m understudy.blindplay observe")
    print("  python -m understudy.blindplay session --max-actions N")
    print("  python -m understudy.embark --teardown")
    return 0


if __name__ == "__main__":
    sys.exit(main())
