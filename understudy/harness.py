"""The Phase-0 measurement harness: one LLM-driven run, fully logged.

Understudy W4. Two verbs, and the discipline lives in the order they run in:

    python -m understudy.harness state
        Render the current screen compactly and, beside it, what policy_v0
        would do here. Reading this is one decision's INPUT.

    python -m understudy.harness act '<json action>' --why "one line"
        Recompute the counterfactual at the CURRENT state, write the log line
        (mine + policy_v0's, at the same state, before anything moves), then
        POST the action and render what came back.

The counterfactual is computed inside `act`, not carried over from the last
`state` call, so a log line can never pair my choice with a policy answer from
a screen that has since changed.

WHY THE STATE RENDER IS COMPACT, AND WHY THAT IS A MEASUREMENT DECISION
Raw wire state for a single character-select screen is ~9k characters. A run
is several hundred decisions. Reading raw JSON would exhaust the session long
before the run ended -- which is M3's failure mode, caused by the harness
rather than by the task. So the renderer is deliberately lossy in one
direction only: it drops presentation and keeps every field a decision could
turn on. `--raw` dumps the full payload to a scratch file when a screen looks
wrong, which is the escape hatch and is itself logged.

TOKEN ACCOUNTING (M1), AND ITS HONEST LIMIT
A process cannot observe the token counts of the model driving it. What IS
observable from inside, and what this harness records per decision:

  * `state_chars`  -- the rendered screen the model actually read
  * `why_chars`    -- the model's own stated reasoning for the choice
  * `wall_ms`      -- time between the previous log line and this one, which
                      is model thinking plus tool round-trip

M1 is therefore reported as MARGINAL characters per decision, converted at the
conventional ~4 chars/token and labelled an estimate. It excludes the
conversation context the model re-reads each turn, which is the larger and
unobservable half. The report says so where it prints the number; a
tokens/decision figure that quietly omitted its denominator would be exactly
the kind of number this house refuses to let anyone quote.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

from understudy import bridge, policy_v0

LOG_DIR = Path(__file__).resolve().parent / "logs"
STATE_FILE = LOG_DIR / "_harness_state.json"


# ------------------------------------------------------------ rendering ----

def _card_line(i: int, c: dict[str, Any]) -> str:
    bits = [f"[{i}] {c.get('name')}", f"cost {c.get('cost')}"]
    if c.get("type"):
        bits.append(str(c["type"]).lower())
    if c.get("target") and str(c["target"]).lower() not in ("none", "self"):
        bits.append(f"tgt:{c['target']}")
    if c.get("can_play") is False:
        bits.append("UNPLAYABLE")
    if c.get("upgraded"):
        bits.append("+")
    line = " | ".join(bits)
    desc = " ".join(str(c.get("description") or "").split())
    if desc:
        line += f"\n      {desc}"
    return line


def _status_line(blob: Any) -> str:
    out = []
    for s in blob or []:
        if isinstance(s, dict):
            amt = s.get("amount", s.get("stacks"))
            out.append(f"{s.get('name')}{'' if amt is None else f' {amt}'}")
    return ", ".join(out) or "-"


def _enemy_line(e: dict[str, Any]) -> str:
    intent = e.get("intent") or {}
    if isinstance(intent, dict):
        itxt = intent.get("description") or intent.get("type") or intent.get("kind") or "?"
        dmg = intent.get("damage", intent.get("amount"))
        times = intent.get("times", intent.get("hits"))
        if dmg is not None:
            itxt = f"{itxt} {dmg}" + (f"x{times}" if times and int(times) > 1 else "")
    else:
        itxt = str(intent)
    return (f"  {e.get('id')} {e.get('name')} "
            f"{e.get('hp')}/{e.get('max_hp')} blk {e.get('block', 0)} "
            f"| intent: {itxt} | status: {_status_line(e.get('status'))}")


def render(state: dict[str, Any]) -> str:
    st = str(state.get("state_type"))
    run = state.get("run") or {}
    p = state.get("player") or {}
    lines = [f"=== {st.upper()} | act {run.get('act')} floor {run.get('floor')} ==="]
    if p:
        lines.append(
            f"Furina {p.get('hp')}/{p.get('max_hp')} HP, blk {p.get('block', 0)}, "
            f"{p.get('gold')}g, energy {p.get('energy', '-')} "
            f"| status: {_status_line(p.get('status'))}")
        pots = [f"[{i}] {x.get('name')}" for i, x in enumerate(p.get("potions") or [])
                if isinstance(x, dict)]
        if pots:
            lines.append("Potions: " + ", ".join(pots))

    if st in ("monster", "elite", "boss"):
        lines.append("Enemies:")
        lines += [_enemy_line(e) for e in (state.get("enemies") or [])]
        lines.append("Hand:")
        lines += ["  " + _card_line(i, c)
                  for i, c in enumerate(p.get("hand") or [])]
        piles = {k: len(p.get(k) or []) for k in ("draw_pile", "discard_pile", "exhaust_pile")}
        lines.append(f"Piles: {piles}")
    elif st == "card_reward":
        lines.append("Offers:")
        lines += ["  " + _card_line(i, c)
                  for i, c in enumerate(state.get("cards") or state.get("options") or [])]
    elif st == "map":
        m = state.get("map") or {}
        opts = m.get("next_options") or state.get("next_options") or []
        lines.append("Next options:")
        for i, o in enumerate(opts):
            lines.append(f"  [{i}] {o if isinstance(o, str) else json.dumps(o)}")
        if m.get("boss"):
            lines.append(f"Boss: {m['boss']}")
    elif st == "event":
        ev = state.get("event") or {}
        lines.append(f"Event: {ev.get('event_name')} ({ev.get('event_id')})"
                     + (" [ancient]" if ev.get("is_ancient") else ""))
        if ev.get("body"):
            lines.append("  " + " ".join(str(ev["body"]).split()))
        for o in ev.get("options") or []:
            flag = " LOCKED" if o.get("is_locked") else ""
            lines.append(f"  [{o.get('index')}] {o.get('title')}{flag}: "
                         + " ".join(str(o.get("description") or "").split()))
    elif st in ("shop", "fake_merchant"):
        items = state.get("items") or (state.get("shop") or {}).get("items") or []
        lines.append("Stock:")
        for i, it in enumerate(items):
            lines.append(f"  [{i}] {it.get('name')} ({it.get('type')}) "
                         f"{it.get('price', it.get('cost'))}g"
                         + (f" - {' '.join(str(it.get('description') or '').split())}"
                            if it.get("description") else ""))
    else:
        for key in ("options", "cards", "relics", "message", "menu_screen",
                    "rewards", "selection"):
            if key in state and state[key] not in (None, [], {}):
                lines.append(f"{key}: {json.dumps(state[key])[:900]}")
    if "options" in state and st in ("rest_site", "rewards", "treasure",
                                     "relic_select", "card_select",
                                     "bundle_select", "hand_select"):
        pass  # already printed above
    return "\n".join(lines)


# ----------------------------------------------------------------- log ----

def _session() -> dict[str, Any]:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {}


def _save_session(s: dict[str, Any]) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(s, indent=1), encoding="utf-8")


def log_path(seed: str) -> Path:
    return LOG_DIR / f"phase0-{seed}.jsonl"


def append(seed: str, record: dict[str, Any]) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with log_path(seed).open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def _agree(mine: dict[str, Any], theirs: dict[str, Any] | None) -> bool | None:
    if theirs is None:
        return None
    if mine.get("action") != theirs.get("action"):
        return False
    for key in ("card_index", "index", "target", "slot"):
        if mine.get(key) != theirs.get(key):
            return False
    return True


# -------------------------------------------------------------- verbs ----

def cmd_state(args) -> int:
    state = bridge.get_state()
    text = render(state)
    cf = policy_v0.counterfactual(state)
    print(text)
    print()
    print(f"POLICY_V0 [{cf.category}] "
          + (cf.label if cf.available else "NO COUNTERFACTUAL"))
    print(f"  {cf.rationale}")
    if cf.notes:
        print(f"  notes: {json.dumps(cf.notes)}")
    if args.raw:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        p = LOG_DIR / "_raw_state.json"
        p.write_text(json.dumps(state, indent=1), encoding="utf-8")
        print(f"  [raw dumped to {p}]")
    sess = _session()
    sess["last_state_chars"] = len(text)
    sess["last_read_ts"] = time.time()
    _save_session(sess)
    return 0


def cmd_act(args) -> int:
    sess = _session()
    seed = sess.get("seed") or "unseeded"

    state = bridge.get_state()
    before = render(state)
    cf = policy_v0.counterfactual(state)

    try:
        mine = json.loads(args.action)
    except json.JSONDecodeError as e:
        print(f"bad action json: {e}", file=sys.stderr)
        return 2
    if "action" not in mine:
        print("action json needs an 'action' key", file=sys.stderr)
        return 2

    now = time.time()
    idx = int(sess.get("decision_index", 0))
    record = {
        "i": idx,
        "ts": now,
        "wall_ms": int((now - sess.get("last_act_ts", now)) * 1000),
        "state_type": state.get("state_type"),
        "act": (state.get("run") or {}).get("act"),
        "floor": (state.get("run") or {}).get("floor"),
        "hp": (state.get("player") or {}).get("hp"),
        "state_chars": len(before),
        "why_chars": len(args.why or ""),
        "mine": mine,
        "why": args.why or "",
        "policy_v0": cf.as_log(),
        "agree": _agree(mine, cf.action if cf.available else None),
        "category": cf.category,
    }

    result = bridge.post(**mine)
    record["result"] = result
    append(seed, record)

    sess["decision_index"] = idx + 1
    sess["last_act_ts"] = now
    _save_session(sess)

    time.sleep(args.settle)
    after = bridge.get_state()
    cf2 = policy_v0.counterfactual(after)
    print(f"# decision {idx} -> {result.get('status')}: {result.get('message', '')}")
    if result.get("status") == "error" or result.get("error"):
        print(f"# ERROR: {result.get('error') or result.get('message')}")
    print()
    print(render(after))
    print()
    print(f"POLICY_V0 [{cf2.category}] "
          + (cf2.label if cf2.available else "NO COUNTERFACTUAL"))
    print(f"  {cf2.rationale}")
    return 0


def cmd_begin(args) -> int:
    """Stamp the session: the game seed, the speed setting, the start time."""
    seed = args.seed or bridge.current_seed() or "unseeded"
    speed = bridge.get_speed()
    sess = {
        "seed": seed,
        "decision_index": 0,
        "started_ts": time.time(),
        "speed_at_start": speed,
    }
    _save_session(sess)
    append(seed, {"i": -1, "ts": time.time(), "event": "session_begin",
                  "seed": seed, "speed": speed})
    print(f"session begun: seed={seed}  log={log_path(seed)}")
    print(f"speed: {json.dumps(speed)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("begin")
    b.add_argument("--seed", default=None)
    b.set_defaults(func=cmd_begin)

    s = sub.add_parser("state")
    s.add_argument("--raw", action="store_true")
    s.set_defaults(func=cmd_state)

    a = sub.add_parser("act")
    a.add_argument("action", help="JSON action body, e.g. '{\"action\":\"end_turn\"}'")
    a.add_argument("--why", default="", help="one line of reasoning, logged")
    a.add_argument("--settle", type=float, default=1.2)
    a.set_defaults(func=cmd_act)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
