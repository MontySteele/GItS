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
    python -m understudy.embark --character klee --arm proto_ko_kapow
    python -m understudy.embark --character klee --lane 1      # a SECOND game
    python -m understudy.embark --character IRONCLAD --lane 1  # base-game CONTROL
    python -m understudy.embark --teardown                     # put it all back
    python -m understudy.embark --teardown --lane 1            # lane 1's only
    python -m understudy.embark --lanes 1,2,3 --character klee --seeds A,B,C   # PARALLEL
    python -m understudy.embark --teardown --lanes 1,2,3
    python -m understudy.embark --coop --lanes 2,3         --characters KLEEMOD-KLEE,KLEEMOD-FURINA --ascension 0   # CO-OP
    python -m understudy.embark --teardown --coop --lanes 2,3

`--coop` is a different embark and lives in `understudy/embark_coop.py`: two
lanes over the game's own `--fastmp` localhost transport, host first, one run.

`--lane 1` opens the run in a second `SlayTheSpire2.exe` out of the same
install (port 15527, its own disposable user tree) so an agent's run can play
beside a game somebody else is playing. It prints the `GITS_LANE` export line,
which is how the three `blindplay` commands -- which take no flag -- find the
same game. The shared halves stay shared: the bridge under `mods\\STS2_MCP` is
reused when a game is up on it and refreshed when none is, and either way it is
recorded *shared, left in place* and NEVER removed by a teardown (`EB-310` --
the owner's own Steam launch reads that directory); `steam_appid.txt` found in
place is left in place; and one deployed `mods\\klee` serves every lane. A
teardown therefore touches its own process, port and profile and nothing else.
A lane-1 run is NOT a run of record.

THE PROTOTYPE ARM DOOR (`EB-188`). The gate after a pair read reads an arm PLAYABLE
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
  * A build that PREDATES THE CURRENT KITS. Until 2026-09-28 the prototype
    classes were `Compile Remove`d from a release build, so the id did not
    exist in one. Since then the release build compiles them too, so the
    check is the deployed package's own version stamp: `+proto`, or a commit
    count at or above `KITS_DEFAULT_SINCE`.
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
the read-back arm, the game rolls one, and `bridge.seed_read_back()` is asked
after the run exists. That string is what the sealed record carries, and it is
also the one string the leak audit greps every observation for -- a tester who
can see the seed is not blind. The read WAITS (`EB-435`): the abandon on the
way in deleted the profile's `current_run.save` and the new run writes its own
several seconds later, and a read taken inside that window is answered about
another user tree's file entirely.

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
import os
import sys
import time
from pathlib import Path
from typing import Any

from understudy import authorship, bridge, instances, report, soak

# `EB-456`: the LANE'S action budget, and this is the one direction the blind
# wall runs in. `blindplay` may never import this file; this file may read the
# blind module's bottom seam, which imports nothing from this package at all.
from understudy import blindplay_shape
# `EB-691`: the LANE'S watchdog cursor, armed here for the budget's reason --
# an embark is a new run, and a cursor left over from the lane's last game
# would have the first `observe` compare against a `godot.log` that no longer
# exists. `lanewatch` reads this module's sidecars as JSON and imports it only
# on the teardown path, so the blind wall still runs one way.
from understudy import lanewatch

LOG_DIR = Path(__file__).resolve().parent / "logs"

# EB-188. The build-metadata tag `klee-mod/build/deploy_proto.ps1` stamps onto
# the staged package version, and the one thing that separates a build holding
# the prototype classes from a build that never compiled them.
PROTO_TAG = "+proto"

# 2026-09-28. [USER]: "make all 3 current builds the active release builds".
# From this commit count on, the RELEASE build (`deploy.ps1`, no `+proto`)
# compiles the prototype classes too (`klee-mod/Directory.Build.props`), so an
# unmarked build at or above it carries the ids. Below it, only `+proto` did.
# The count is the ruling's commit on main; a build between an earlier merge
# and this one is the one case the number cannot tell apart, and there the far
# side's `unknown card id` still refuses the grant.
KITS_DEFAULT_SINCE = 3970


def carries_prototype_classes(build: str) -> bool:
    """True when the deployed build compiled the prototype surface."""
    if PROTO_TAG in build:
        return True
    head = build.split("+", 1)[0].split(".")
    return (len(head) == 3 and head[2].isdigit()
            and int(head[2]) >= KITS_DEFAULT_SINCE)

# Which ledger row feeds which of `Session`'s undo steps. Matched on the
# recorded `change` text because that text is what the ledger persists -- the
# alternative is a second copy of the step order living here, drifting from
# soak's.
#
# THERE IS NO BRIDGE SLOT, AND LEAVING IT OUT IS THE POINT (`EB-310`). Nothing
# in this harness removes `mods\\STS2_MCP`; the row `_deploy_bridge` writes is
# reverted the instant it is written, and a slot here would re-arm the removal
# for any ledger -- including one written before that rule existed -- that
# still carries a `Deployed mods` row marked APPLIED.
_LEDGER_SLOTS = (
    ("_seed_entry", "May set a chosen run seed"),
    ("_speed_entry", "Set FastMode=Instant"),
    ("_launch_entry", "Launched `"),
    ("_appid_entry", "Created `steam_appid.txt`"),
)


class EmbarkError(RuntimeError):
    """The game, the bridge or the ledger is not in a state this can work on."""


#: The base game's five playable classes, spelled the way the character-select
#: screen's own option id spells them (`cm.Id.Entry` in
#: `vendor/STS2_MCP/McpMod.StateBuilder.cs::AddCharacterSelectMenuState` --
#: uppercase, no prefix, unlike a custom model's id, which BaseLib prefixes
#: `KLEE -> KLEEMOD-KLEE`). Confirmed against this repo's own naming for the
#: same five: `game_ref/char_real_ironclad.yaml`'s `name: IRONCLAD (real
#: pool)`, `char_real_silent.yaml`'s `name: SILENT (real pool)`, and
#: `defect_char_facts.yaml`'s `id: real_defect` / `name: DEFECT (real pool)`
#: all use the bare uppercase class name, never a `THE_`-prefixed or
#: otherwise decorated spelling -- and `test_the_option_id_and_the_display_
#: name_fold_together` (tier0/tests/test_understudy_soak.py) already asserts
#: `canonical_character("IRONCLAD") == "ironclad"` on that same form.
BASE_CHARACTERS = ("IRONCLAD", "SILENT", "DEFECT", "NECROBINDER", "REGENT")


def option_id(name: str) -> str:
    """A roster id, a base-character id, or a select-screen option id --
    folded onto the option id `soak._embark` compares against.

    `soak._embark` compares against the character-select screen's own option
    strings, so `--character kokomi` would match nothing and embark on whatever
    was highlighted -- which is EB-117, and it cost a run. Accepting the short
    name and expanding it here is the cheap half of that lesson.

    A BASE CHARACTER IS NEVER PREFIXED. `KLEEMOD-` is BaseLib's prefix for
    THIS mod's own custom models; Ironclad, Silent, Defect, Necrobinder and
    Regent are the game's own classes and the select screen offers them
    unprefixed (`BASE_CHARACTERS` above). Prefixing one would ask the wire
    for `KLEEMOD-IRONCLAD`, which is not an option on any screen, and the
    control round this exists for could never embark at all.
    """
    raw = str(name or "").strip()
    if not raw:
        raise EmbarkError("no character given")
    up = raw.upper()
    if up.startswith("KLEEMOD-") or up in BASE_CHARACTERS:
        return up
    return f"KLEEMOD-{up}"


# --------------------------------------------------------- prototype arms --

def wire_id(arm: str) -> str:
    """A row id as `give_card` spells it: `KLEEMOD-<SHEET_ID>`.

    The same spelling for a prototype row and a shipped one -- the mod's ids
    are `KLEEMOD-` plus the sheet id, upper-cased (`understudy/adapter.py`).
    """
    return f"KLEEMOD-{str(arm).strip().upper()}"


def arm_kind(arm: str) -> str:
    """Which surface this id came off. Always `"prototype"` since legacy
    cleanup stage 6 deleted the shipped sheets; kept on the sidecar so a
    record's grant line keeps its shape."""
    return "prototype"


def check_arms(arms: list[str],
               version: tuple[str, str] | None = None) -> tuple[str, str]:
    """Refuse an arm that is not a row, or a build that cannot carry one.

    Returns `(build version, where it was read)` when the grant may proceed.
    `version` is injectable so the tests can put a release build, a dev build
    and an unreadable one in front of this without a game.

    ONE SURFACE, ONE DOOR. An id is legal if it is a row on the prototype
    surface; anything else is refused HERE rather than by the far side's
    `unknown card id`. The shipped sheets, and with them the shipped-row
    grants, left at legacy cleanup stage 6.
    """
    known = authorship.rows_authorship()
    unknown = [a for a in arms if a not in known]
    if unknown:
        raise EmbarkError(
            f"not a row on {authorship.SURFACE.name}: {', '.join(unknown)}. "
            f"`--arm` names a row by its `id:` on the prototype surface -- a "
            f"slice whose rows have already left the surface cannot be "
            f"granted (the deletion rule).")

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
            f"exist in a build that predates the current kits.")
    if not carries_prototype_classes(build):
        raise EmbarkError(
            f"the deployed build is {build!r} ({source}): no {PROTO_TAG!r} "
            f"and older than build {KITS_DEFAULT_SINCE}, when the current "
            f"kits became the release build. Its prototype classes were "
            f"compiled out, so there is no id to grant -- deploy the current "
            f"build with tools/deploy_round.py (klee-mod\\build\\deploy.ps1 "
            f"plus the bridge) first.")
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
                        "kind": arm_kind(arm),
                        "count": 1, "upgraded": False,
                        "card_name": reply.get("card_name") or "",
                        "message": reply.get("message") or ""})
    return granted


# ------------------------------------------------------------- the embark --

def embark(character: str, *, hold: bool = False,
           chosen_seed: str | None = None,
           chosen_ascension: int | None = None,
           arms: list[str] | None = None,
           instance: Any = None,
           lane: object = None,
           max_actions: int = 0,
           install_bridge: bool = True) -> dict[str, Any]:
    """Launch (or attach), embark, read the seed back, and LEAVE IT RUNNING.

    Returns the sidecar dict. Raises rather than tearing down on failure: a
    half-open game the operator can look at is worth more than a clean
    directory and no diagnosis, and `--teardown` puts it back either way.

    `instance` is the lane (`None` for lane 0, which is every embark that ever
    ran before this flag existed). `install_bridge` is the hard OFF switch for
    WRITING the shared `mods\\STS2_MCP`: a caller that KNOWS another lane is
    driving it passes `False`, while `soak.lane_setup` leaves it on, because
    the session's own rule -- an install with a game up on it is left alone,
    one with nothing holding it is refreshed, and neither is ever removed
    (`EB-310`) -- can see the machine rather than guess at it.

    `max_actions` is `EB-456`: the coordinator's cap on how many acts this
    lane's seat may post. It is written to the lane's own budget -- and the
    count zeroed, because an embark is a new run -- BEFORE the launch, so a
    launch that fails half way still leaves the cap the operator asked for
    rather than the previous round's spent count. `0` clears the budget, which
    is every round before this row.

    `chosen_ascension` is posted beside the seed (character picked, confirm
    not fired) through `bridge.set_ascension`; `None` leaves the character's
    saved PreferredAscension, as every embark before the flag did. The run's
    read-back `ascension` must equal it or the embark fails
    `ascension_not_honoured`.
    """
    who = option_id(character)
    wanted = list(arms or [])
    # BEFORE the launch. An unknown row id or a release build is a fact about
    # the machine and the request, not about the run, and finding it out after
    # the game is up costs a launch and a teardown for nothing.
    build, build_source = check_arms(wanted) if wanted else ("", "")
    # A LANE HOLDS ONE GAME. A launch beside a game an earlier embark left up
    # cannot bind the lane's port, and the wire would read the old run (see
    # `live_launch_on_lane`). Refused before anything is written.
    if not hold:
        label = (instances.label_for(lane) if lane is not None
                 else instances.DEFAULT_LABEL)
        stale = live_launch_on_lane(label)
        if stale is not None:
            old, pid = stale
            flag = ("" if label == instances.DEFAULT_LABEL
                    else f" --lane {label[len('lane'):]}")
            raise EmbarkError(
                f"{label} still has a game up from embark {old} (pid {pid}); "
                f"it was never torn down, and a second game on this lane "
                f"cannot bind its port. Tear it down first: python -m "
                f"understudy.embark --teardown{flag} --stamp {old}")
    # `EB-691`. Zeroed BEFORE the launch, beside the budget and for the same
    # reason: a launch that fails half way leaves a watch armed on a lane with
    # no game rather than the last game's cursor.
    lanewatch.arm(lane)

    stamp = reserve_stamp(lane)
    # The budget is zeroed FOR THIS RUN (2026-10-08): the stamp rides in the
    # lane's budget row, so a count carried over from an earlier run on the
    # lane is recognised as one (`blindplay_shape.count_action`).
    budget = blindplay_shape.set_budget(max_actions, lane, run=stamp)
    soak.LOG_DIR.mkdir(parents=True, exist_ok=True)
    session = soak.Session(stamp, do_setup=not hold, intent="",
                           instance=instance, install_bridge=install_bridge)
    sidecar = {
        "stamp": stamp,
        "ledger": str(session.ledger.path),
        "character_requested": who,
        "hold": hold,
        "arms_requested": wanted,
        **({"ascension_requested": chosen_ascension}
           if chosen_ascension is not None else {}),
        # `EB-456`. The cap, in the run's own manifest: a round is only
        # comparable to another inside it, and a caveat that lives in the
        # coordinator's shell history is a caveat the reader does not have.
        "max_actions": budget["cap"],
        "max_actions_store": str(blindplay_shape.budget_path(lane)),
        # 2026-10-08: the install this lane launched, so the sealed record
        # finds the deployed build from any checkout (`build_version`).
        **({"game_dir": str(session.instance.game_dir)}
           if session.instance is not None
           and session.instance.game_dir is not None else {}),
        # WHICH GAME THIS RUN IS ON. A sidecar with no lane on it is a run
        # nobody can attribute once two of them can be open at once; the
        # label, the port and the user tree are all three facts a reader needs
        # to find the log that belongs to it.
        **(session.instance.as_row() if session.instance is not None
           else {"instance": bridge.current_label()}),
        # AND WHAT THAT MEANS, IN THE FILE. A lane above zero is a disposable
        # profile, and the sentence saying so travels with the run rather than
        # living in this comment -- the same arrangement `arms_guardrail`
        # below has, for the same reason.
        **({"lane_guardrail": instances.LANE_GUARDRAIL,
            "run_of_record": False}
           if session.instance is not None else {}),
        "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    _write_sidecar(stamp, sidecar)

    session.setup()
    driver = soak.RunDriver(session, 1, stamp, character=who,
                            chosen_seed=chosen_seed, max_fights=0,
                            chosen_ascension=chosen_ascension)
    try:
        state = driver._to_main_menu()
        state = driver._embark(state)
        state = driver._verify_character(state)
    except soak.Defect as d:
        raise EmbarkError(f"{d.kind}: {d.detail}") from None
    # EB-435: WAITED FOR. The abandon on the way in deleted the profile's
    # `current_run.save` and the new run writes its own several seconds later;
    # read inside that window, the mod's resolution leaves this lane's tree and
    # answers about another one. A crossing that survives the wait is a real
    # one and becomes an embark error rather than a bare traceback.
    try:
        seed = bridge.seed_read_back() or ""
    except bridge.LaneCrossed as crossed:
        raise EmbarkError(f"seed_read_back_crossed: {crossed}") from None

    sidecar.update({
        "character_actual": driver.character_actual,
        # R95: read off the wire AFTER the run exists. Never the requested one.
        "run_seed": seed,
        "screen": str(state.get("state_type") or "unknown"),
        "floor": int(((state.get("run") or {}).get("floor")) or 0),
        # The bridge's own run state, read back the same way `floor` is
        # (`McpMod.MultiplayerState.cs:243` / `McpMod.StateBuilder.cs:610`
        # both write `run.ascension = runState.AscensionLevel`). A CONTROL
        # round is only comparable to a mod round at the same ascension, so
        # this belongs beside `run_seed` in the run's own manifest rather
        # than left to be re-derived from a screenshot.
        "ascension": int(((state.get("run") or {}).get("ascension")) or 0),
        "run_log": str(driver.log),
    })
    if (chosen_ascension is not None
            and sidecar["ascension"] != chosen_ascension):
        # The lobby said yes and the run says otherwise. Written first, so the
        # record shows the mismatch; then the same refusal as the lobby check.
        _write_sidecar(stamp, sidecar)
        raise EmbarkError(f"ascension_not_honoured: asked for ascension "
                          f"{chosen_ascension}, the run reads back "
                          f"{sidecar['ascension']}")

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


def reserve_stamp(lane: object = None, *, clock=time.strftime,
                  sleep=time.sleep, attempts: int = 120) -> str:
    """A stamp no other embark holds, CLAIMED by creating its sidecar.

    THE STAMP NAMES THREE FILES -- this sidecar, the reversibility ledger
    (`soak/reversibility-<stamp>.json`) and the run log -- and it is a clock
    reading to the second. Two lanes embarked in the same second (the
    parallel `--lanes` embark does exactly that) took the SAME stamp: the
    second sidecar overwrote the first and both ledgers flushed into one
    file, so the first lane's launch row (its pid) was lost and its teardown
    had nothing to kill. The claim is an exclusive create, which only one
    process can win; the loser waits for the next second and tries again.
    """
    label = (instances.label_for(lane) if lane is not None
             else instances.DEFAULT_LABEL)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    for _ in range(max(1, attempts)):
        stamp = clock("%Y%m%d-%H%M%S")
        try:
            with sidecar_path(stamp).open("x", encoding="utf-8") as fh:
                fh.write(json.dumps({"stamp": stamp, "instance": label,
                                     "reserved": True}) + "\n")
            return stamp
        except FileExistsError:
            sleep(0.25)
    raise EmbarkError(f"could not claim an embark stamp in {LOG_DIR} after "
                      f"{attempts} tries")


def _write_sidecar(stamp: str, blob: dict[str, Any]) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    text = json.dumps(blob, indent=1) + "\n"
    sidecar_path(stamp).write_text(text, encoding="utf-8")
    # 2026-10-08: AND A COPY IN THE LANE'S STATE FOLDER, where `blindplay`
    # reads the run's seed, stamp and install from whichever checkout the
    # seat runs in (`blindplay_shape.lane_sidecars`). The checkout's copy
    # stays the teardown's ledger anchor; this one is read-only to the page.
    label = str(blob.get("instance") or "")
    if label:
        blindplay_shape.write_atomic(
            blindplay_shape.lane_state_dir(label) / sidecar_path(stamp).name,
            text)


def _sidecar(path: Path) -> dict[str, Any]:
    """One sidecar's dict, or `{}` when it cannot be read."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):                            # noqa: PERF203
        return {}


def _is_hold(path: Path) -> bool:
    return bool(_sidecar(path).get("hold"))


def sidecar_lane(blob: dict[str, Any]) -> str:
    """Which lane a sidecar's embark was on. A sidecar written before lanes
    existed carries no `instance` key at all, and it was lane 0."""
    return str(blob.get("instance") or instances.DEFAULT_LABEL)


def latest_stamp(label: str = "") -> str:
    """The most recent embark that actually CHANGED something, or an error.

    A `--hold` embark attaches to a game somebody else launched and records no
    ledger rows at all, so it has nothing to tear down -- and picking one as
    "the latest" would hide the launch that DOES need reverting behind it.
    They are skipped here and answered by name below.

    `label` NARROWS IT TO ONE LANE, which is what `--teardown --lane 1` needs:
    with two games open the newest sidecar is whichever was started last, and
    tearing that one down is a coin flip over somebody else's run.
    """
    found = [p for p in sorted(LOG_DIR.glob("embark-*.json"))
             if not _is_hold(p)
             and (not label or sidecar_lane(_sidecar(p)) == label)]
    if not found:
        where = f" on {label}" if label else ""
        raise EmbarkError(
            f"no launching embark sidecar{where} in {LOG_DIR}; there is "
            f"nothing to tear down (if the game was launched by hand, close "
            f"it by hand and run "
            f"`klee-mod\\build\\deploy_bridge.ps1 -Remove`)")
    return found[-1].stem[len("embark-"):]


def live_launch_on_lane(label: str) -> tuple[str, int] | None:
    """An earlier embark on `label` whose game is STILL UP, as (stamp, pid).

    THE FIND (Varka seat, lane 1, 2026-09-29). A run ended on `game_over`,
    and its embark (`20260929-145523`) was never reverted: the ledger's launch
    row still read APPLIED and pid 27116 was still alive. The next embark on
    lane 1 launched a SECOND game, which could not bind the lane's port, so
    the wire kept answering from the old one -- and the boot watch died on
    "menu never became ready ... last read: state_type=game_over". Worse,
    `--teardown --lane 1` then reverted the NEWEST sidecar (the failed
    launch), never the one holding the port, so the lane could not recover
    without a stamp named by hand.

    A launch row counts only while APPLIED and while its pid is a live game;
    an unreadable pid probe is not counted, so a broken `tasklist` cannot
    block every embark.
    """
    for path in sorted(LOG_DIR.glob("embark-*.json"), reverse=True):
        blob = _sidecar(path)
        if not blob or blob.get("hold") or sidecar_lane(blob) != label:
            continue
        try:
            rows = json.loads(Path(blob["ledger"]).read_text(encoding="utf-8"))
        except (KeyError, OSError, ValueError, TypeError):
            continue
        for row in rows if isinstance(rows, list) else []:
            if (str(row.get("change", "")).startswith("Launched `")
                    and row.get("state") == "APPLIED"
                    and row.get("pid") is not None):
                image = soak.pid_image(int(row["pid"]))
                if image and not image.startswith("<"):
                    return path.stem[len("embark-"):], int(row["pid"])
    return None


def teardown(stamp: str = "", lane: object = None) -> str:
    """Walk the ledger ON DISK through `Session`'s own undo steps.

    THE LANE COMES OFF THE SIDECAR, NOT OFF THE ENVIRONMENT. Every step of
    this teardown that touches the wire -- releasing the seed, restoring
    FastMode -- has to reach the game this embark opened, and the shell that
    runs the teardown is not the shell that ran the embark. So the thread is
    bound to the lane the sidecar RECORDS, explicitly and in both directions:
    a lane-0 teardown run in a shell with `GITS_LANE=1` exported still talks
    to lane 0.

    ANY teardown then touches its own process, port and profile and nothing
    else, because the shared halves were settled at setup: `steam_appid.txt`
    found in place was reverted then as "pre-existing, left in place", and the
    bridge row is reverted as "shared, left in place" on every branch there is.
    `mods\\STS2_MCP` is what the owner's own Steam launch reads, so this
    harness never removes it (`EB-310`) -- `deploy_bridge.ps1 -Remove` is the
    only remover, and it is run by hand.
    """
    label = instances.label_for(lane) if lane is not None else ""
    stamp = stamp or latest_stamp(label)
    blob = json.loads(sidecar_path(stamp).read_text(encoding="utf-8"))
    recorded = sidecar_lane(blob)
    if label and recorded != label:
        raise EmbarkError(
            f"embark {stamp} was on {recorded}, not {label}; refusing to tear "
            f"down another lane's game (drop --lane, or name the stamp you "
            f"mean)")
    bridge.use(instances.wire_lane(recorded))
    if blob.get("hold"):
        return (f"embark {stamp} was a --hold: it attached to a game somebody "
                f"else launched, changed nothing in the game directory, and "
                f"has nothing to revert.")
    ledger_path = Path(blob["ledger"])
    if not ledger_path.exists():
        raise EmbarkError(f"the ledger named by the sidecar is gone: "
                          f"{ledger_path}")
    entries = json.loads(ledger_path.read_text(encoding="utf-8"))
    # THE LANE GOES INTO THE SESSION, not just onto the thread. `bridge.use`
    # above settles where the WIRE talks; a Session with no instance still
    # resolves its own per-lane paths off the default, and `archive_log` then
    # copied lane 0's `godot.log` under a lane-1 stamp -- five of six archives
    # of proofs-8a (2026-09-16) were the other lane's game. `cli_lane` is
    # `None` for lane 0 exactly as the setup call above is, so the default
    # teardown is byte-for-byte what it was. Same family as EB-210 / EB-435.
    session = soak.Session(stamp, do_setup=False, intent="",
                           instance=instances.cli_lane(recorded))
    session.ledger.path = ledger_path
    session.ledger.entries = entries
    for attr, marker in _LEDGER_SLOTS:
        match = next((e for e in entries
                      if str(e.get("change", "")).startswith(marker)
                      and e.get("state") == "APPLIED"), None)
        setattr(session, attr, match)
    session.teardown()
    return session.ledger.table()


# ------------------------------------------------------- several lanes --
#
# `--lanes 1,2,3` WITHOUT `--coop`: one ordinary single-lane embark per lane,
# all started at once, each in its OWN PROCESS -- the same command a person
# would type per lane, with its output in its own log. A process per lane,
# not a thread per lane, because everything an embark binds (the wire's
# lane, the keep-awake hold, the launched game's parent) is per process, and
# because the command a lane ran is then the command anyone can re-run for
# that lane alone. What the lanes share -- the game directory -- is
# serialised by `instances.install_lock` inside each one, and their stamps
# by `reserve_stamp`; the boots overlap, which is the whole saving.

def parse_seat_lanes(value: str) -> list[str]:
    """`"1,2,3"` -> `["lane1", "lane2", "lane3"]`. Distinct, and never lane 0
    (the owner's own game and profile)."""
    raw = [v.strip() for v in str(value or "").split(",") if v.strip()]
    if not raw:
        raise EmbarkError("--lanes names no lane (`--lanes 1,2,3`)")
    try:
        labels = [instances.label_for(v) for v in raw]
    except ValueError as exc:
        raise EmbarkError(str(exc)) from None
    if len(set(labels)) != len(labels):
        raise EmbarkError(f"--lanes names a lane twice: {value!r}")
    if instances.DEFAULT_LABEL in labels:
        raise EmbarkError(
            "lane 0 is the owner's own game and profile; a parallel embark "
            "runs on the disposable lanes ("
            + ", ".join(instances.seat_lane_labels()) + ")")
    return labels


def _per_lane(value: str, labels: list[str], what: str) -> list[str | None]:
    """A comma list with one entry per lane, or one entry for every lane, or
    nothing (`None` for each)."""
    raw = [v.strip() for v in str(value or "").split(",")]
    raw = [v for v in raw if v]
    if not raw:
        return [None] * len(labels)
    if len(raw) == 1:
        return raw * len(labels)
    if len(raw) != len(labels):
        raise EmbarkError(f"--{what} gives {len(raw)} values for "
                          f"{len(labels)} lanes; give one, or one per lane in "
                          f"the --lanes order")
    return raw


def lane_commands(labels: list[str], *, characters: list[str | None],
                  seeds: list[str | None], ascension: int | None,
                  max_actions: int, arms: list[str]) -> list[list[str]]:
    """The single-lane embark command each lane runs."""
    out = []
    for label, who, seed in zip(labels, characters, seeds):
        cmd = [sys.executable, "-m", "understudy.embark",
               "--lane", label[len("lane"):],
               "--character", who or "kokomi"]
        if seed:
            cmd += ["--seed", seed]
        if ascension is not None:
            cmd += ["--ascension", str(ascension)]
        if max_actions:
            cmd += ["--max-actions", str(max_actions)]
        for arm in arms:
            cmd += ["--arm", arm]
        out.append(cmd)
    return out


def _sidecar_from_log(text: str) -> dict[str, Any]:
    """The sidecar a single-lane embark's output names, read, or `{}`."""
    for line in text.splitlines():
        if line.startswith("sidecar:"):
            return _sidecar(Path(line.split(":", 1)[1].strip()))
    return {}


def embark_lanes(labels: list[str], commands: list[list[str]], *,
                 popen=None, log_dir: Path | None = None) -> list[dict]:
    """Start every lane's embark at once, wait for all, report each.

    Returns one row per lane: label, port, exit code, log path, and -- off
    the lane's own sidecar -- the character, the read-back seed and the
    ascension. A lane that fails does not stop the others; its row says so
    and its log has the reason. Nothing is torn down here, on any branch.
    """
    import subprocess
    run = popen or subprocess.Popen
    where = Path(log_dir) if log_dir is not None else LOG_DIR
    where.mkdir(parents=True, exist_ok=True)
    started = time.strftime("%Y%m%d-%H%M%S")
    # UNBUFFERED, so a lane's log can be read while it boots rather than only
    # once its embark has exited; and with no `GITS_LANE` inherited, since
    # each lane is named by its own `--lane` and a stray export must not
    # reach a child's wire.
    env = {k: v for k, v in os.environ.items() if k != instances.LANE_ENV}
    env["PYTHONUNBUFFERED"] = "1"
    procs = []
    for label, cmd in zip(labels, commands):
        log = where / f"embark-{started}-{label}.log"
        fh = log.open("w", encoding="utf-8")
        proc = run(cmd, stdout=fh, stderr=subprocess.STDOUT, env=env,
                   cwd=str(Path(__file__).resolve().parent.parent))
        procs.append((label, proc, fh, log))
    rows = []
    for label, proc, fh, log in procs:
        code = proc.wait()
        fh.close()
        try:
            text = log.read_text(encoding="utf-8", errors="replace")
        except OSError:
            text = ""
        blob = _sidecar_from_log(text) if code == 0 else {}
        rows.append({
            "lane": label, "port": instances.port_for(label),
            "exit": code, "log": str(log),
            "character": blob.get("character_actual") or "",
            "run_seed": blob.get("run_seed") or "",
            "ascension": blob.get("ascension"),
            "stamp": blob.get("stamp") or "",
            "error": ("" if code == 0 else
                      next((ln for ln in reversed(text.splitlines())
                            if ln.strip()), "(no output)")),
        })
    return rows


def render_lane_rows(rows: list[dict]) -> str:
    out = []
    for r in rows:
        if r["exit"] == 0:
            out.append(f"{r['lane']}  port {r['port']}  UP  "
                       f"{r['character']}  seed {r['run_seed']}  "
                       f"ascension {r['ascension']}  stamp {r['stamp']}  "
                       f"log {r['log']}")
        else:
            out.append(f"{r['lane']}  port {r['port']}  FAILED (exit "
                       f"{r['exit']}): {r['error']}  log {r['log']}")
    return "\n".join(out)


# -------------------------------------------------------------------- CLI --

def main(argv: list[str] | None = None) -> int:
    report.console_safe()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--character", default="kokomi",
                    help="a roster id (kokomi), the select-screen option id "
                         "(KLEEMOD-KOKOMI), or a base-game class for a "
                         "CONTROL round (IRONCLAD, SILENT, DEFECT, "
                         "NECROBINDER, REGENT -- never KLEEMOD-prefixed)")
    ap.add_argument("--hold", action="store_true",
                    help="attach to a game somebody else launched: no bridge "
                         "deploy, no launch, no speed change, and nothing "
                         "recorded on the ledger for those")
    ap.add_argument("--arm", action="append", default=[], metavar="PROTO_ID",
                    dest="arms",
                    help="EB-188: grant a row into the STARTING DECK once the "
                         "run is open, so a blind whole-fight run can meet an "
                         "arm the pools quarantine. A row from "
                         "docs/prototype-surface.yaml. Repeatable, and "
                         "repeat an id to grant a second copy. A prototype id "
                         "is refused unless the deployed build carries the "
                         "current kits (`+proto`, or any build since the "
                         "2026-09-28 ruling)")
    ap.add_argument("--seed", default=None,
                    help="embark on a CHOSEN seed instead of one the game "
                         "rolls; the read-back still decides what is recorded")
    ap.add_argument("--ascension", type=int, default=None, metavar="N",
                    help="embark at ascension N instead of the character's "
                         "saved last-used level, so a CONTROL run can match a "
                         "mod run. Set on the select screen after the pick "
                         "(it also becomes that profile's saved level, as a "
                         "click would); refused above the character's max")
    ap.add_argument("--teardown", action="store_true",
                    help="revert an earlier embark: seed, speed, process, "
                         "steam_appid.txt, in that order. The shared bridge "
                         "under mods\\STS2_MCP is NOT removed -- the owner's "
                         "own Steam launch reads it; take it out by hand with "
                         "deploy_bridge.ps1 -Remove")
    ap.add_argument("--stamp", default="",
                    help="which embark to tear down; the newest by default")
    ap.add_argument("--max-actions", type=int, default=0, metavar="N",
                    help="EB-456: cap how many actions this lane's seat may "
                         "post. `blindplay act` counts every accepted act "
                         "against it and refuses past it with `budget "
                         "reached`, so the count is the bridge's rather than "
                         "the seat's own arithmetic -- two of three round-13 "
                         "seats overran a counted 120 by a third. 0 (the "
                         "default) is no budget, exactly as before")
    ap.add_argument("--lane", default=0, metavar="N",
                    help="which game instance to open the run in. 0 (the "
                         "default) is the machine's own %%APPDATA%% and port "
                         "15526 -- an embark exactly as it was. 1 launches a "
                         "SECOND game from the same install, on port 15527 "
                         "and its own disposable user tree "
                         "(%%LOCALAPPDATA%%\\gits-lanes\\lane1), so an agent's "
                         "run can play beside a game somebody else is "
                         "playing. A bridge with a game up on it is reused, "
                         "never rewritten, so this cannot pull the mods "
                         "directory out from under a running game -- and no "
                         "teardown removes it either. A lane-1 run is NOT a "
                         "run of record. With "
                         "--teardown it names WHICH lane's embark to revert")
    ap.add_argument("--coop", action="store_true",
                    help="CO-OP: open ONE run across two lanes, one player "
                         "each, over the game's --fastmp localhost transport "
                         "(understudy/embark_coop.py). Needs --lanes and "
                         "--characters; with --teardown it tears both lanes "
                         "down, the client first")
    ap.add_argument("--lanes", default="", metavar="N,N,...",
                    help="with --coop: the two lanes, host first (`2,3`). "
                         "WITHOUT --coop: embark every named lane AT ONCE, "
                         "one ordinary single-lane embark each, and report "
                         "each lane's port, character and read-back seed "
                         "(`--lanes 1,2,3`); with --teardown, tear each "
                         "named lane down")
    ap.add_argument("--characters", default="", metavar="A,B,...",
                    help="with --coop: each lane's character, host first; "
                         "one name is both players'. With a parallel "
                         "--lanes: one per lane, or one for all (else "
                         "--character)")
    ap.add_argument("--seeds", default="", metavar="S1,S2,...",
                    help="with a parallel --lanes: one chosen seed per lane, "
                         "in --lanes order")
    ap.add_argument("--client-id", type=int, default=1000, metavar="N",
                    help="with --coop: the client's --clientId (default "
                         "1000; the host is always 1)")
    ap.add_argument("--keep-bridge", action="store_true",
                    help="with --coop: write nothing to the shared "
                         "mods\\STS2_MCP and run the bridge already "
                         "installed (the host's launch otherwise refreshes it "
                         "from this checkout when no game holds it)")
    args = ap.parse_args(argv)

    if args.coop:
        if args.arms or args.hold:
            print("embark error: --coop takes no --arm and no --hold (a "
                  "grant refuses multiplayer, and a co-op pair is always "
                  "launched here)", file=sys.stderr)
            return 2
        from understudy import embark_coop
        return embark_coop.run_cli(args)

    if args.lanes:
        return _lanes_cli(args)
    if args.seeds or args.characters:
        print("embark error: --seeds and --characters go with --lanes (or "
              "--coop); a single lane takes --seed and --character",
              file=sys.stderr)
        return 2

    try:
        if args.teardown:
            # NO `lane_setup` HERE. Putting a game back must not depend on the
            # shared install still being in the state a LAUNCH needs; the
            # sidecar already knows which lane it was, and the ledger already
            # knows what it changed.
            print(teardown(args.stamp, lane=args.lane))
            return 0
        instance, install_bridge = soak.lane_setup(args.lane)
        blob = embark(args.character, hold=args.hold, chosen_seed=args.seed,
                      chosen_ascension=args.ascension,
                      arms=args.arms, instance=instance, lane=args.lane,
                      max_actions=args.max_actions,
                      install_bridge=install_bridge)
    except (EmbarkError, ValueError) as exc:
        print(f"embark error: {exc}", file=sys.stderr)
        return 2

    print(f"stamp:     {blob['stamp']}")
    print(f"character: {blob.get('character_actual') or '(unread)'}")
    print(f"run seed:  {blob.get('run_seed') or '(unread)'}   "
          f"(read back off the wire, R95)")
    print(f"screen:    {blob.get('screen')}  floor {blob.get('floor')}  "
          f"ascension {blob.get('ascension')}")
    granted = blob.get("arms_granted") or []
    if granted:
        print(f"arms granted: "
              f"{', '.join(g['card_id'] for g in granted)}  into the deck "
              f"on {blob.get('arms_build_version')}")
        print(f"  {bridge.GRANT_GUARDRAIL}")
    if blob.get("max_actions"):
        print(f"budget:    {blob['max_actions']} actions on this lane; "
              f"`blindplay act` refuses past it "
              f"({blindplay_shape.BUDGET_REACHED})")
    print(f"sidecar:   {sidecar_path(blob['stamp'])}")
    label = sidecar_lane(blob)
    lane_arg = ""
    if label != instances.DEFAULT_LABEL:
        lane_arg = f" --lane {label[len('lane'):]}"
        print(f"lane:      {label}  port {blob.get('port')}  "
              f"appdata {blob.get('appdata')}")
    print()
    print("The game is UP and the run is OPEN. Nothing has been torn down.")
    if lane_arg:
        # THE THREE BLIND COMMANDS TAKE NO FLAG, so the lane reaches them
        # through the environment (`bridge.env_instance`). Printed as an
        # export line rather than described, because the one way this goes
        # wrong is a tester reading lane 0's game and never knowing.
        print(f"  $env:{instances.LANE_ENV} = "
              f"'{label[len('lane'):]}'      # PowerShell, this shell only")
        print(f"  export {instances.LANE_ENV}={label[len('lane'):]}"
              f"          # bash")
    print("  python -m understudy.blindplay observe")
    print("  python -m understudy.blindplay session --max-actions N")
    print(f"  python -m understudy.embark --teardown{lane_arg}")
    if lane_arg:
        print()
        print(f"LANE {lane_arg.rsplit(' ', 1)[-1]} IS NOT A RUN OF RECORD: "
              f"its profile is disposable and nothing in it is read back.")
    return 0


def _lanes_cli(args: argparse.Namespace) -> int:
    """`--lanes 1,2,3` without `--coop`: a parallel embark, or a teardown of
    each named lane."""
    try:
        labels = parse_seat_lanes(args.lanes)
        if args.teardown:
            if args.stamp:
                raise EmbarkError("--stamp names one embark; tear several "
                                  "lanes down by lane alone")
            failed = 0
            for label in labels:
                try:
                    print(f"== {label}")
                    print(teardown("", lane=label))
                except (EmbarkError, OSError, ValueError) as exc:
                    failed += 1
                    print(f"embark error: {label}: {exc}", file=sys.stderr)
            return 2 if failed else 0
        if args.hold or args.seed:
            raise EmbarkError("a parallel --lanes embark takes no --hold, and "
                              "takes --seeds (one per lane) rather than --seed")
        characters = _per_lane(args.characters or args.character, labels,
                               "characters")
        seeds = _per_lane(args.seeds, labels, "seeds")
        for who in characters:
            option_id(who or "")
        if args.arms:
            check_arms(args.arms)
        commands = lane_commands(labels, characters=characters, seeds=seeds,
                                 ascension=args.ascension,
                                 max_actions=args.max_actions, arms=args.arms)
    except (EmbarkError, ValueError) as exc:
        print(f"embark error: {exc}", file=sys.stderr)
        return 2
    print(f"embarking {', '.join(labels)} at once (each lane's output goes to "
          f"its own log; the shared install is taken one lane at a time)")
    rows = embark_lanes(labels, commands)
    print(render_lane_rows(rows))
    up = [r for r in rows if r["exit"] == 0]
    print()
    print(f"{len(up)} of {len(rows)} lanes UP. Nothing has been torn down. "
          f"Each lane's seat sets GITS_LANE=<N>; tear down with "
          f"`python -m understudy.embark --teardown --lanes {args.lanes}` or "
          f"one lane at a time with `--teardown --lane N`.")
    return 0 if len(up) == len(rows) else 2


if __name__ == "__main__":
    sys.exit(main())
