"""Co-op embark: two lanes, one run, one seat on each side.

    python -m understudy.embark --coop --lanes 2,3 \\
        --characters KLEEMOD-KLEE,KLEEMOD-FURINA --ascension 0
    GITS_LANE=2 python -m understudy.blindplay observe      # seat A (host)
    GITS_LANE=3 python -m understudy.blindplay observe      # seat B (client)
    python -m understudy.embark --teardown --coop --lanes 2,3

THE TRANSPORT IS THE GAME'S OWN. `--fastmp` makes both sides of a co-op lobby
use ENet on localhost instead of Steam lobbies (the 0.111.0 decompile:
`NMultiplayerHostSubmenu` / `NJoinFriendScreen` choose Steam only when the
argument is absent). `--fastmp host_standard` opens the host's character
select directly and binds UDP 0.0.0.0:33771; `--fastmp join --clientId N`
connects to 127.0.0.1:33771 as player N. Two games on one Steam account work
(`understudy/instances.py`), and ENet sidesteps the one thing that would not:
both Steam peers would carry the same Steam id. THE PORT IS FIXED, so one
co-op pair per machine, and the host must be listening before the client's
join screen opens (it gives up after 10 s).

THE ORDER. Host launched and in its lobby; client launched and joined; both
lobbies show two players; each side picks its character; the host alone takes
the seed (only if one was asked for) and the ascension (the multiplayer lobby
defaults to the host's saved level, A5 on these lanes); both confirm, client
first; both bridges serve a run on `/api/v1/multiplayer`. Every wait is
bounded and a timeout is a refusal naming what was last read. Nothing is torn
down on a failure: `--teardown --coop` puts back whatever was launched.

WHAT IS WRITTEN. One sidecar per lane (`embark-<stamp>-laneN.json`, the shape
every lane reader already knows: `lanewatch`, `harness frame`, the worktree
guard, a single-lane `--teardown --lane N`), each with a `coop` block naming
its role and its partner; and one co-op sidecar (`coop-<stamp>.json`, not
matched by the lane readers' `embark-*.json` glob) with both lanes, both
characters, the seed and both ascension read-backs.

THE SEED IS READ OFF THE HOST'S SAVE. A co-op run saves to
`current_run_mp.save`, which the compendium's seed read does not open, and
only the host writes one. So the host lane's own user tree is read, for a
file written after this launch, and the one seed is recorded for both lanes.

RESUMING IS NOT SUPPORTED. `--fastmp load` looks the save up under the Steam
id while the save names its players 1 and 1000 (`NMainMenu`); every co-op
embark starts a fresh run.

A CO-OP RUN IS NOT A RUN OF RECORD, for the lane reason (both profiles are
disposable) and one more: nothing single-player is comparable to it.
"""
from __future__ import annotations

import json
import socket
import time
from pathlib import Path
from typing import Any, Callable

from understudy import blindplay_shape, bridge, instances, lanewatch, soak

#: The ENet port `--fastmp` hosts on (`ENetHost`, 0.111.0). Fixed in the game.
FASTMP_PORT = 33771
HOST_ARGS = ("--fastmp", "host_standard")
DEFAULT_CLIENT_ID = 1000

#: The waits, each bounded. The lobby waits start after the lane's own
#: menu-ready wait (`Session.setup`), so they cover navigation and the join,
#: not the boot.
HOST_LOBBY_TIMEOUT_S = 120.0
JOIN_TIMEOUT_S = 120.0
PICK_TIMEOUT_S = 30.0
RUN_TIMEOUT_S = 120.0
SEED_TIMEOUT_S = 30.0
POLL_S = 1.0

MP_SAVE = "current_run_mp.save"

#: Beside the per-lane `embark-*.json` sidecars (`embark.LOG_DIR`), under a
#: name their `embark-*.json` readers do not match.
LOG_DIR = Path(__file__).resolve().parent / "logs"

COOP_GUARDRAIL = (
    "co-op run on two disposable lane profiles over the game's --fastmp "
    "localhost transport: not a run of record, and nothing measured on it is "
    "comparable to a singleplayer run")


class EmbarkError(RuntimeError):
    """A co-op embark or teardown could not be done; the message says why."""


def client_args(client_id: int = DEFAULT_CLIENT_ID) -> tuple[str, ...]:
    return ("--fastmp", "join", "--clientId", str(int(client_id)))


# ---------------------------------------------------------------- parsing --

def parse_lanes(value: str) -> list[str]:
    """`"2,3"` -> `["lane2", "lane3"]`: host first. Two distinct lanes above 0."""
    raw = [v.strip() for v in str(value or "").split(",") if v.strip()]
    if len(raw) != 2:
        raise EmbarkError(f"--lanes takes two lanes, host first (`--lanes "
                          f"2,3`); got {value!r}")
    try:
        labels = [instances.label_for(v) for v in raw]
    except ValueError as exc:
        raise EmbarkError(str(exc)) from None
    if labels[0] == labels[1]:
        raise EmbarkError(f"--lanes names {labels[0]} twice; a co-op run "
                          f"needs two games")
    if instances.DEFAULT_LABEL in labels:
        raise EmbarkError("lane 0 is the owner's own game and profile; a "
                          "co-op pair runs on two disposable lanes ("
                          + ", ".join(instances.seat_lane_labels()) + ")")
    return labels


def parse_characters(value: str) -> list[str]:
    """`"KLEEMOD-KLEE,furina"` -> two option ids, host's first. One name is
    both players'."""
    from understudy import embark
    raw = [v.strip() for v in str(value or "").split(",") if v.strip()]
    if len(raw) == 1:
        raw = raw * 2
    if len(raw) != 2:
        raise EmbarkError(f"--characters takes one or two characters, host "
                          f"first; got {value!r}")
    try:
        return [embark.option_id(v) for v in raw]
    except embark.EmbarkError as exc:
        raise EmbarkError(str(exc)) from None


def fastmp_port_free(port: int = FASTMP_PORT) -> bool:
    """Can a fastmp host bind its port? False while another pair holds it."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind(("0.0.0.0", port))
        return True
    except OSError:
        return False
    finally:
        sock.close()


# ------------------------------------------------------------- the reads --

class _Lanes:
    """The wire, pointed at one lane per call. `bridge` is thread-local, so
    each read binds the calling thread to the lane first."""

    def __init__(self, wire: Any, clock: Callable[[], float],
                 sleep: Callable[[float], None]):
        self.wire = wire
        self.clock = clock
        self.sleep = sleep
        self.error = getattr(wire, "BridgeError", bridge.BridgeError)

    def on(self, inst: Any) -> Any:
        self.wire.use(inst)
        return self.wire

    def state(self, inst: Any) -> dict[str, Any]:
        try:
            got = self.on(inst).get_state()
        except self.error as exc:
            return {"error": str(exc)}
        return got if isinstance(got, dict) else {}

    def wait(self, what: str, timeout: float,
             check: Callable[[], Any]) -> Any:
        """Poll `check` until it answers something truthy, or refuse."""
        deadline = self.clock() + timeout
        last = None
        while True:
            last = check()
            if last and not isinstance(last, _Miss):
                return last
            if self.clock() >= deadline:
                seen = last.read if isinstance(last, _Miss) else ""
                raise EmbarkError(f"{what} (waited {timeout:.0f}s)"
                                  + (f"; last read: {seen}" if seen else ""))
            self.sleep(POLL_S)


class _Miss:
    """A falsy poll answer that remembers what it saw, for the refusal."""

    def __init__(self, read: str):
        self.read = read

    def __bool__(self) -> bool:
        return False


def _brief(state: dict[str, Any]) -> str:
    if state.get("error"):
        return f"error: {str(state['error'])[:160]}"
    lobby = state.get("lobby") or {}
    opts = soak._option_names(state)
    return (f"state_type={state.get('state_type')} "
            f"menu_screen={state.get('menu_screen')} "
            f"lobby={lobby.get('type')}/{lobby.get('player_count')} "
            f"options={opts}")


def _lobby(state: dict[str, Any]) -> dict[str, Any]:
    lobby = state.get("lobby")
    if state.get("menu_screen") != "character_select" \
            or not isinstance(lobby, dict):
        return {}
    return lobby


def _local_character(lobby: dict[str, Any]) -> str:
    for p in lobby.get("players") or []:
        if isinstance(p, dict) and p.get("is_local") is True:
            return str(p.get("character_id") or p.get("character") or "")
    return ""


def _picked(lobby: dict[str, Any], who: str) -> bool:
    got = _local_character(lobby)
    return bool(got) and (got.upper() == who.upper()
                          or soak.character_matches(who, got))


# --------------------------------------------------------------- the seed --

def mp_save_seed(appdata: Path | None, since: float) -> str:
    """The seed in the newest `current_run_mp.save` under a lane's tree,
    written at or after `since`, or `""`."""
    if appdata is None:
        return ""
    root = Path(appdata).joinpath(*instances.SETTINGS_RELATIVE)
    best: tuple[float, Path] | None = None
    try:
        for path in root.glob(f"**/saves/{MP_SAVE}"):
            mtime = path.stat().st_mtime
            if mtime + 2 >= since and (best is None or mtime > best[0]):
                best = (mtime, path)
    except OSError:
        return ""
    if best is None:
        return ""
    try:
        blob = json.loads(best[1].read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ""
    rng = blob.get("rng") if isinstance(blob, dict) else None
    return str((rng or {}).get("seed") or "")


# -------------------------------------------------------------- sidecars --

def coop_path(stamp: str) -> Path:
    return LOG_DIR / f"coop-{stamp}.json"


def _write(path: Path, blob: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(blob, indent=1) + "\n", encoding="utf-8")


def _default_session(stamp: str, instance: Any,
                     extra_args: tuple[str, ...],
                     install_bridge: bool = True) -> Any:
    return soak.Session(stamp, do_setup=True, intent="", instance=instance,
                        install_bridge=install_bridge, extra_args=extra_args)


# ----------------------------------------------------------------- embark --

def embark(lanes: list[str], characters: list[str], *,
           ascension: int | None = None, seed: str | None = None,
           max_actions: int = 0, client_id: int = DEFAULT_CLIENT_ID,
           install_bridge: bool = True,
           wire: Any = bridge,
           session_factory: Callable[..., Any] = _default_session,
           lane_factory: Callable[[str], Any] = instances.lane,
           port_free: Callable[[], bool] = fastmp_port_free,
           clock: Callable[[], float] = time.monotonic,
           sleep: Callable[[float], None] = time.sleep) -> dict[str, Any]:
    """Launch both lanes, open one co-op run, and LEAVE IT RUNNING.

    Returns the co-op sidecar. Raises `EmbarkError` on any refusal or
    timeout, after writing what it knew, and tears nothing down.

    `install_bridge=False` is `--keep-bridge`: neither lane writes the shared
    `mods\\STS2_MCP`, and both run whatever bridge is installed. The host's
    launch otherwise refreshes it from THIS checkout's vendor tree when no game
    holds it, exactly as a singleplayer embark does -- which from a worktree
    carrying a bridge edit would be a deploy.
    """
    from understudy import embark as single
    host_label, client_label = lanes
    host_who, client_who = characters
    if not port_free():
        raise EmbarkError(
            f"UDP port {FASTMP_PORT} is taken: another --fastmp host is up on "
            f"this machine (the port is fixed in the game, so one co-op pair "
            f"per machine). Tear that pair down first.")
    host = lane_factory(host_label)
    client = lane_factory(client_label)
    io = _Lanes(wire, clock, sleep)
    for inst in (host, client):
        try:
            io.on(inst).health()
        except io.error:
            continue
        raise EmbarkError(f"{inst.label} already has a game answering on "
                          f"port {inst.port}; tear it down first")

    stamp = time.strftime("%Y%m%d-%H%M%S")
    roles = ((host, host_who, "host", client_label, HOST_ARGS),
             (client, client_who, "client", host_label,
              client_args(client_id)))
    blob: dict[str, Any] = {
        "stamp": stamp, "lanes": [host_label, client_label],
        "host": host_label, "client": client_label,
        "characters_requested": {host_label: host_who,
                                 client_label: client_who},
        **({"ascension_requested": ascension}
           if ascension is not None else {}),
        **({"seed_requested": seed} if seed else {}),
        "fastmp_port": FASTMP_PORT, "client_id": int(client_id),
        "lane_sidecars": {}, "state": "launching",
        "coop_guardrail": COOP_GUARDRAIL, "run_of_record": False,
        "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    path = coop_path(stamp)
    _write(path, blob)

    sessions: dict[str, Any] = {}
    lane_blobs: dict[str, dict[str, Any]] = {}
    launched_at = time.time()
    for inst, who, role, partner, args in roles:
        label = inst.label
        lanewatch.arm(label)
        lane_stamp = f"{stamp}-{label}"
        budget = blindplay_shape.set_budget(max_actions, label,
                                            run=lane_stamp)
        session = session_factory(lane_stamp, inst, args, install_bridge)
        sessions[label] = session
        lane_blob = {
            "stamp": lane_stamp, "ledger": str(session.ledger.path),
            "character_requested": who, "hold": False, "arms_requested": [],
            **({"ascension_requested": ascension}
               if ascension is not None else {}),
            "max_actions": budget["cap"],
            "max_actions_store": str(blindplay_shape.budget_path(label)),
            **({"game_dir": str(inst.game_dir)}
               if inst.game_dir is not None else {}),
            **inst.as_row(),
            "lane_guardrail": instances.LANE_GUARDRAIL,
            "run_of_record": False,
            "coop": {"role": role, "partner": partner, "stamp": stamp,
                     "sidecar": str(path), "launch_args": list(args)},
            "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        lane_blobs[label] = lane_blob
        blob["lane_sidecars"][label] = str(single.sidecar_path(lane_stamp))
        single._write_sidecar(lane_stamp, lane_blob)
        _write(path, blob)
        try:
            session.setup()
        except SystemExit as exc:
            raise EmbarkError(f"{label} ({role}) did not boot: {exc}") \
                from None
        if role == "host":
            io.wait(f"{host_label} never reached a host lobby (--fastmp "
                    f"host_standard opens the multiplayer character select; "
                    f"a main menu blocked by unrevealed epochs would stop it)",
                    HOST_LOBBY_TIMEOUT_S,
                    lambda: (_lobby(io.state(host)).get("type") == "host"
                             or _Miss(_brief(io.state(host)))))

    def both_in_lobby() -> Any:
        rows = {i.label: _lobby(io.state(i)) for i in (host, client)}
        if all(int(r.get("player_count") or 0) >= 2 for r in rows.values()):
            return True
        return _Miss(" | ".join(f"{k}: {_brief(io.state(i))}"
                                for k, i in ((host.label, host),
                                             (client.label, client))))

    io.wait(f"{client_label} never joined {host_label}'s lobby (the client "
            f"gives up 10 s after its join screen opens; a mod-list "
            f"mismatch is named in {client_label}'s godot.log)",
            JOIN_TIMEOUT_S, both_in_lobby)

    for inst, who, _role, _p, _a in roles:
        state = io.state(inst)
        offered = soak._option_names(state)
        if who.lower() not in [o.lower() for o in offered]:
            raise EmbarkError(f"character_not_offered: {inst.label}'s "
                              f"character select offers no {who!r}; the "
                              f"options are {offered}")
        io.on(inst).post("menu_select", option=who)
        io.wait(f"character_not_picked: {inst.label} never showed {who} as "
                f"its lobby character", PICK_TIMEOUT_S,
                lambda inst=inst, who=who: (
                    _picked(_lobby(io.state(inst)), who)
                    or _Miss(_brief(io.state(inst)))))

    if seed:
        sessions[host_label].note_seed_channel()
        report = io.on(host).set_seed(seed)
        blob["seed_report"] = {k: report.get(k) for k in
                               ("status", "route", "chosen", "message")}
    if ascension is not None:
        report = io.on(host).set_ascension(int(ascension))
        blob["ascension_report"] = {k: report.get(k) for k in
                                    ("status", "route", "lobby_ascension",
                                     "max", "message", "error")}
        if report.get("status") != "ok" \
                or report.get("lobby_ascension") != int(ascension):
            _write(path, blob)
            raise EmbarkError(
                f"ascension_not_honoured: asked the host lobby for "
                f"{ascension}, it answered {report.get('lobby_ascension')!r} "
                f"({report.get('error') or report.get('message')})")
        io.wait(f"ascension_not_synced: {client_label}'s lobby never showed "
                f"ascension {ascension}", PICK_TIMEOUT_S,
                lambda: (_lobby(io.state(client)).get("ascension")
                         == int(ascension)
                         or _Miss(_brief(io.state(client)))))

    # CLIENT FIRST, so the host's confirm is the one that starts the run with
    # every setting already on the lobby.
    for inst in (client, host):
        def confirm_offered(inst=inst) -> Any:
            opts = soak._option_names(io.state(inst))
            return soak._first_of(opts, ("confirm", "embark")) or _Miss(
                f"options={opts}")
        pick = io.wait(f"no_embark: {inst.label} never offered confirm",
                       PICK_TIMEOUT_S, confirm_offered)
        io.on(inst).post("menu_select", option=pick)

    def both_in_run() -> Any:
        reads = {i.label: io.state(i) for i in (host, client)}
        if all(r.get("game_mode") == "multiplayer"
               and ((r.get("player") or {}).get("character"))
               for r in reads.values()):
            return reads
        return _Miss(" | ".join(f"{k}: {_brief(r)}"
                                for k, r in reads.items()))

    reads = io.wait("coop_run_never_started: the multiplayer route never "
                    "served a run on both lanes", RUN_TIMEOUT_S, both_in_run)

    run_seed = seed or ""
    if not run_seed:
        run_seed = io.wait(
            f"seed_unread: no {MP_SAVE} written after the launch in "
            f"{host_label}'s tree", SEED_TIMEOUT_S,
            lambda: mp_save_seed(host.appdata, launched_at)
            or _Miss("no save yet")) if host.appdata is not None else ""

    mismatch = []
    blob.update({"state": "open", "run_seed": run_seed,
                 "character_actual": {}, "ascension": {}})
    for inst, who, _role, _p, _a in roles:
        read = reads[inst.label]
        actual = str((read.get("player") or {}).get("character") or "")
        asc = int(((read.get("run") or {}).get("ascension")) or 0)
        lane_blobs[inst.label].update({
            "character_actual": actual, "run_seed": run_seed,
            "screen": str(read.get("state_type") or "unknown"),
            "floor": int(((read.get("run") or {}).get("floor")) or 0),
            "ascension": asc,
        })
        single._write_sidecar(lane_blobs[inst.label]["stamp"],
                              lane_blobs[inst.label])
        blob["character_actual"][inst.label] = actual
        blob["ascension"][inst.label] = asc
        if not soak.character_matches(who, actual):
            mismatch.append(f"character_mismatch: {inst.label} asked for "
                            f"{who}, the run reads back {actual!r}")
        if ascension is not None and asc != int(ascension):
            mismatch.append(f"ascension_not_honoured: {inst.label} reads "
                            f"back ascension {asc}, not {ascension}")
    _write(path, blob)
    if mismatch:
        raise EmbarkError("; ".join(mismatch))
    return blob


# --------------------------------------------------------------- teardown --

def latest(lanes: list[str]) -> Path:
    """The newest co-op sidecar over exactly these two lanes."""
    want = sorted(lanes)
    found = []
    for path in sorted(LOG_DIR.glob("coop-*.json")):
        try:
            blob = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if sorted(blob.get("lanes") or []) == want:
            found.append(path)
    if not found:
        raise EmbarkError(f"no co-op embark over {', '.join(want)} in "
                          f"{LOG_DIR}; nothing to tear down")
    return found[-1]


def teardown(lanes: list[str],
             lane_teardown: Callable[..., str] | None = None) -> str:
    """Tear both lanes down, CLIENT FIRST, each through its own ledger.

    Every lane is attempted even when the first refuses, and the refusals are
    reported together: a pair half torn down is the state to avoid.
    """
    from understudy import embark as single
    down = lane_teardown or single.teardown
    path = latest(lanes)
    blob = json.loads(path.read_text(encoding="utf-8"))
    out, failed = [], []
    for label in (blob.get("client"), blob.get("host")):
        side = Path((blob.get("lane_sidecars") or {}).get(label) or "")
        if not label or not side.name or not side.is_file():
            out.append(f"{label}: no lane sidecar (never launched)")
            continue
        lane_stamp = side.stem[len("embark-"):]
        try:
            out.append(f"{label}:\n{down(lane_stamp, lane=label)}")
        except (single.EmbarkError, EmbarkError, OSError, ValueError) as exc:
            failed.append(f"{label}: {exc}")
    blob["state"] = "torn_down" if not failed else "teardown_failed"
    blob["torn_down"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    _write(path, blob)
    if failed:
        raise EmbarkError("co-op teardown incomplete: " + "; ".join(failed)
                          + "\n" + "\n".join(out))
    return "\n".join(out)


# -------------------------------------------------------------------- CLI --

def run_cli(args: Any) -> int:
    """`embark --coop ...`, from `embark.main`'s parsed arguments."""
    import sys
    try:
        lanes = parse_lanes(args.lanes)
        if args.teardown:
            print(teardown(lanes))
            return 0
        chars = parse_characters(args.characters)
        blob = embark(lanes, chars, ascension=args.ascension, seed=args.seed,
                      max_actions=args.max_actions,
                      client_id=args.client_id,
                      install_bridge=not args.keep_bridge)
    except EmbarkError as exc:
        print(f"embark error: {exc}", file=sys.stderr)
        return 2
    print(f"co-op:     {coop_path(blob['stamp'])}")
    print(f"run seed:  {blob.get('run_seed') or '(unread)'}")
    for label in blob["lanes"]:
        role = "host" if label == blob["host"] else "client"
        print(f"{label} ({role}): {blob['character_actual'].get(label)}  "
              f"ascension {blob['ascension'].get(label)}")
    print()
    print("The games are UP and the co-op run is OPEN. Nothing has been torn "
          "down.")
    for label in blob["lanes"]:
        n = label[len("lane"):]
        print(f"  seat on {label}: GITS_LANE={n} python -m "
              f"understudy.blindplay observe")
    print(f"  python -m understudy.embark --teardown --coop --lanes "
          f"{','.join(l[len('lane'):] for l in blob['lanes'])}")
    print()
    print(f"NOT A RUN OF RECORD: {COOP_GUARDRAIL}.")
    return 0
