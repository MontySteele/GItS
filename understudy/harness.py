"""The Phase-0 measurement harness: one LLM-driven run, fully logged.

Understudy W4. Two verbs, and the discipline lives in the order they run in:

    python -m understudy.harness state
        Render the current screen compactly and, beside it, what policy_v0
        would do here. Reading this is one decision's INPUT.

    python -m understudy.harness act '<json action>' --why "one line"
        Recompute the counterfactual at the CURRENT state, write the log line
        (mine + policy_v0's, at the same state, before anything moves), then
        POST the action and render what came back.

    python -m understudy.harness frame --label salon-stage
        OFF unless GITS_UNDERSTUDY_CAPTURE=1. One frame of the game window,
        written to the gitignored understudy/logs/frames/ with a manifest row
        naming the screen it was taken on. MATERIAL for [USER]'s art sittings
        and nothing else: Guardrail-7 and the no-fun rule are not changed by
        the existence of a camera, and no claim about look, legibility or fun
        may be derived from a frame by anything in this directory.

    python -m understudy.harness give-card UNHEARD_CONFESSION --why "EB-52(a)"
        EB-52's dev door: put a CHOSEN card in the deck through the game's own
        acquisition path. A SMOKE verb. The run it is used on stops being a run
        the generators produced, so nothing measured on it is comparable to
        anything -- the grant, its reason and that sentence all go on the run
        log. It lives here and NOT in the soak deliberately: the soak's claim
        is that its runs are generated runs, and this is the attended loop.

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

from understudy import adapter, bridge, deckwatch, frames, policy_v0

LOG_DIR = Path(__file__).resolve().parent / "logs"
STATE_FILE = LOG_DIR / "_harness_state.json"


# ------------------------------------------------------------ rendering ----

def _card_line(i: int, c: dict[str, Any]) -> str:
    bits = [f"[{i}] {c.get('name')}", f"cost {c.get('cost')}"]
    if c.get("type"):
        bits.append(str(c["type"]).lower())
    tt = str(c.get("target_type") or c.get("target") or "").lower()
    if tt and tt not in ("none", "self", "no_target"):
        bits.append(f"tgt:{tt}")
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
    intent = e.get("intents") or e.get("intent") or {}
    if isinstance(intent, list):
        intent = intent[0] if intent else {}
    if isinstance(intent, dict):
        itxt = (intent.get("title") or intent.get("type")
                or intent.get("description") or intent.get("kind") or "?")
        if intent.get("label"):
            itxt = f"{itxt} {intent['label']}"
        dmg = intent.get("damage", intent.get("amount"))
        times = intent.get("times", intent.get("hits"))
        if dmg is not None:
            itxt = f"{itxt} {dmg}" + (f"x{times}" if times and int(times) > 1 else "")
    else:
        itxt = str(intent)
    return (f"  {e.get('entity_id') or e.get('id')} {e.get('name')} "
            f"{e.get('hp')}/{e.get('max_hp')} blk {e.get('block', 0)} "
            f"| intent: {itxt} | status: {_status_line(e.get('status'))}")


def render(state: dict[str, Any]) -> str:
    # Every render is also a chance to see the deck; combat states are the
    # only place the wire shows it. Cheap, idempotent, and it means the draft
    # counterfactual is never scored against nothing.
    deckwatch.record(state)
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
        b = state.get("battle") or {}
        lines[0] += f"  round {b.get('round')} ({b.get('turn')})"
        lines.append("Enemies:")
        lines += [_enemy_line(e) for e in adapter.enemy_blobs(state)]
        lines.append("Hand:")
        lines += ["  " + _card_line(i, c)
                  for i, c in enumerate(p.get("hand") or [])]
        piles = {k: len(p.get(k) or []) for k in ("draw_pile", "discard_pile", "exhaust_pile")}
        lines.append(f"Piles: {piles}")
    elif st == "card_reward":
        blob = state.get("card_reward") or {}
        cards = (blob.get("cards") if isinstance(blob, dict) else None) \
            or state.get("cards") or []
        lines.append("Offers:")
        for i, c in enumerate(cards):
            lines.append("  " + _card_line(c.get("index", i), c))
            for kw in c.get("keywords") or []:
                lines.append(f"        - {kw.get('name')}: "
                             + " ".join(str(kw.get("description") or "").split())[:220])
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
    elif st == "rest_site":
        blob = state.get("rest_site") or {}
        for o in (blob.get("options") if isinstance(blob, dict) else None) or []:
            lines.append(f"  [{o.get('index')}] {o.get('name')} - "
                         + " ".join(str(o.get("description") or "").split())
                         + ("" if o.get("is_enabled", True) else " DISABLED"))
    elif st in ("card_select", "bundle_select"):
        blob = state.get(st) or {}
        lines.append(f"{blob.get('screen_type', st)}: {blob.get('prompt', '')}")
        lines += ["  " + _card_line(c.get("index", i), c)
                  for i, c in enumerate(blob.get("cards") or [])]
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
        parsed = json.loads(args.action)
    except json.JSONDecodeError as e:
        print(f"bad action json: {e}", file=sys.stderr)
        return 2
    plan = parsed if isinstance(parsed, list) else [parsed]
    if not all(isinstance(a, dict) and "action" in a for a in plan):
        print("each action needs an 'action' key", file=sys.stderr)
        return 2

    # A PLANNED SEQUENCE is a real thing a player does -- you decide a turn,
    # not a card -- but it is a different epistemic act from deciding with the
    # intermediate state in front of you, so it is recorded as one. Each step
    # still gets its own counterfactual, computed at the state that step
    # actually faces.
    planned = len(plan) > 1
    for step, mine in enumerate(plan):
        if step > 0:
            state = bridge.get_state()
            cf = policy_v0.counterfactual(state)
            before = render(state)
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
            "state_chars": len(before) if step == 0 else 0,
            "why_chars": len(args.why or "") if step == 0 else 0,
            "mine": mine,
            "why": args.why or "",
            "planned_sequence": planned,
            "plan_step": step,
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
        if result.get("status") == "error":
            print(f"# step {step} ERROR, plan aborted: {result.get('error')}")
            break
        if step < len(plan) - 1:
            time.sleep(args.settle)

    time.sleep(args.settle)
    after = bridge.get_state()
    cf2 = policy_v0.counterfactual(after)
    print(f"# {len(plan)} action(s) posted; last -> {result.get('status')}: "
          f"{result.get('message', '')}")
    if result.get("status") == "error" or result.get("error"):
        print(f"# ERROR: {result.get('error') or result.get('message')}")
    print()
    print(render(after))
    print()
    print(f"POLICY_V0 [{cf2.category}] "
          + (cf2.label if cf2.available else "NO COUNTERFACTUAL"))
    print(f"  {cf2.rationale}")
    return 0


# --------------------------------------------------- mechanical screens ----
#
# Screens where the game asks a question with exactly one answer: dialogue to
# click through, a reward pile to collect, a single-relic chest. These are not
# decisions and they must not enter the M2 denominator -- but at ~1 tool call
# each they would have consumed the session before Act 2, which would have
# failed M3 for a reason that is about the harness rather than about the task.
#
# `auto` walks them and stops the instant a real decision appears. Every step
# is still logged, as `auto: true`, so the run's action history stays complete
# and the count of mechanical steps is itself reportable.

DECISION_SCREENS = {"monster", "elite", "boss", "card_reward", "map",
                    "rest_site", "shop", "fake_merchant", "relic_select",
                    "card_select", "bundle_select", "hand_select",
                    "crystal_sphere", "game_over"}


def _auto_step(state: dict[str, Any]) -> dict[str, Any] | None:
    """The single forced action on a mechanical screen, or None to stop."""
    st = str(state.get("state_type"))
    if st in DECISION_SCREENS:
        return None
    if st == "event":
        ev = state.get("event") or {}
        if ev.get("in_dialogue"):
            return {"action": "advance_dialogue"}
        opts = [o for o in (ev.get("options") or []) if not o.get("is_locked")]
        # A one-option event (or a bare "Proceed") is a click, not a choice.
        if len(opts) == 1:
            return {"action": "choose_event_option", "index": opts[0].get("index", 0)}
        return None
    if st == "rewards":
        blob = state.get("rewards")
        items = blob.get("items") if isinstance(blob, dict) else (blob or [])
        if items:
            return {"action": "claim_reward", "index": 0}
        return {"action": "proceed"}
    if st == "treasure":
        relics = state.get("relics") or state.get("options") or []
        if len(relics) == 1:
            return {"action": "claim_treasure_relic", "index": 0}
        if not relics:
            return {"action": "proceed"}
        return None
    return None


def cmd_auto(args) -> int:
    sess = _session()
    seed = sess.get("seed") or "unseeded"
    steps = 0
    state = bridge.get_state()
    while steps < args.max_steps:
        action = _auto_step(state)
        if action is None:
            break
        idx = int(sess.get("decision_index", 0))
        now = time.time()
        result = bridge.post(**action)
        append(seed, {
            "i": idx, "ts": now, "wall_ms": 0,
            "state_type": state.get("state_type"),
            "act": (state.get("run") or {}).get("act"),
            "floor": (state.get("run") or {}).get("floor"),
            "hp": (state.get("player") or {}).get("hp"),
            "state_chars": 0, "why_chars": 0,
            "mine": action, "why": "mechanical screen, forced action",
            "auto": True,
            "policy_v0": {"category": "mechanical", "available": False,
                          "action": None, "label": "(none)",
                          "rationale": "not a decision", "notes": {}},
            "agree": None, "category": "mechanical",
            "result": result,
        })
        sess["decision_index"] = idx + 1
        _save_session(sess)
        steps += 1
        time.sleep(args.settle)
        state = bridge.get_state()

    cf = policy_v0.counterfactual(state)
    print(f"# auto walked {steps} mechanical step(s)")
    print()
    print(render(state))
    print()
    print(f"POLICY_V0 [{cf.category}] "
          + (cf.label if cf.available else "NO COUNTERFACTUAL"))
    print(f"  {cf.rationale}")
    if cf.notes:
        print(f"  notes: {json.dumps(cf.notes)}")
    return 0


def cmd_give_card(args) -> int:
    """EB-52's acquisition door, and it is a SMOKE verb, not a measurement one.

    It is here rather than in `soak.py` on purpose. The soak's whole claim is
    that its runs are runs the game generated; a grant verb inside it would be
    a way to quietly break that claim on an unattended night. The Phase-0
    harness is the attended loop -- a person types every verb into it, one at a
    time -- so this is where a deliberate, logged, one-off intervention
    belongs.

    THE GRANT IS WRITTEN TO THE RUN LOG BEFORE ANYTHING ELSE IS READ, and it
    carries the guardrail sentence with it. A log that recorded the effect of a
    grant without recording the grant is a log that shows a card appearing in a
    deck from nowhere, which is exactly the shape of the thing nobody would
    catch six months later.
    """
    sess = _session()
    seed = sess.get("seed") or "unseeded"
    report = bridge.give_card(args.card_id, count=args.count,
                              upgraded=args.upgraded, pile=args.pile)
    append(seed, {
        "i": -1, "ts": time.time(), "event": "dev_card_grant",
        "request": {"card_id": args.card_id, "count": args.count,
                    "upgraded": args.upgraded, "pile": args.pile},
        "why": args.why,
        "guardrail": bridge.GRANT_GUARDRAIL,
        "result": report,
    })
    print(f"give_card -> {json.dumps(report, indent=1)}")
    print()
    print(f"GUARDRAIL: {bridge.GRANT_GUARDRAIL}")
    if str(report.get("status")) != "ok":
        return 1
    print()
    print("# confirm by reading the deck; the grant is queued, not instant")
    return 0


def cmd_frame(args) -> int:
    """Grab one frame of the game window as MATERIAL for an art sitting.

    OFF unless `GITS_UNDERSTUDY_CAPTURE=1`, and the refusal comes BEFORE the
    bridge is touched: a disabled leg should cost nothing and reach nothing.

    THE FRAME IS NOT A FINDING. Guardrail-7 and the no-fun rule are unchanged
    by the existence of a camera: a JSON-state agent still cannot see the
    screen, and nothing this apparatus derives from a frame is a claim about
    look, legibility, readability or fun. The frame is for a person to look at.
    `frames.GUARDRAIL` says exactly that and rides on every manifest row.

    The state read is for the CONTEXT LABEL only -- which screen, which act and
    floor the frame was taken on. A pile of unlabelled takes is a pile nobody
    can use, and the alternative (guessing afterwards from the picture) is the
    thing a bot must not do.
    """
    if not frames.enabled():
        print(frames.DISABLED_NOTE)
        return 2
    context: dict[str, Any] = {}
    try:
        state = bridge.get_state()
        run = state.get("run") or {}
        context = {"state_type": state.get("state_type"),
                   "menu_screen": state.get("menu_screen"),
                   "act": run.get("act"), "floor": run.get("floor"),
                   "seed": _session().get("seed")}
    except bridge.BridgeError as e:
        # A frame with no context is still a frame; the missing label is
        # recorded as missing rather than left to be inferred later.
        context = {"bridge": f"unreachable: {e}"}
    report = frames.capture(args.label, note=args.note, context=context)
    print(json.dumps({k: v for k, v in report.items() if k != "row"}, indent=1))
    if report["status"] != "ok":
        return 1
    seed = _session().get("seed") or "unseeded"
    append(seed, {"i": -1, "ts": time.time(), "event": "frame_captured",
                  "path": report["path"], "label": args.label,
                  "note": args.note, "context": context,
                  "guardrail": frames.GUARDRAIL})
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

    u = sub.add_parser("auto")
    u.add_argument("--max-steps", type=int, default=25)
    u.add_argument("--settle", type=float, default=1.2)
    u.set_defaults(func=cmd_auto)

    f = sub.add_parser("frame")
    f.add_argument("--label", default="frame",
                   help="what this take is of, e.g. salon-stage. Slugged into "
                        "the filename")
    f.add_argument("--note", default="",
                   help="one line onto the manifest row. NOT a judgment -- a "
                        "frame is material for a person to look at, and "
                        "nothing this apparatus says about one is evidence")
    f.set_defaults(func=cmd_frame)

    g = sub.add_parser("give-card")
    g.add_argument("card_id", help="wire id (UNHEARD_CONFESSION) or the exact "
                                   "printed title; no fuzzy match")
    g.add_argument("--count", type=int, default=1)
    g.add_argument("--upgraded", action="store_true")
    g.add_argument("--pile", default="deck",
                   choices=list(bridge.GRANT_PILES),
                   help="deck (default) is the between-rooms deck; the other "
                        "three are combat piles and need a combat in progress")
    g.add_argument("--why", default="",
                   help="one line, logged beside the grant. A grant with no "
                        "stated reason is a deck change nobody can account "
                        "for later")
    g.set_defaults(func=cmd_give_card)

    a = sub.add_parser("act")
    a.add_argument("action", help="JSON action body, e.g. '{\"action\":\"end_turn\"}'")
    a.add_argument("--why", default="", help="one line of reasoning, logged")
    a.add_argument("--settle", type=float, default=1.2)
    a.set_defaults(func=cmd_act)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
