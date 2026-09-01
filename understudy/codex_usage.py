"""EB-227: what the Codex seat has left, read from Codex's own rollout.

WHY THIS EXISTS. The Codex seat spends a third party's metered quota on a
$20/month plan, and until now nothing in this tree could see the meter. The
standing rule -- three Codex calls per graded turn (R217, and `M64`'s split
where a PLAYABLE round buys roughly seven) -- is a BUDGET, written down in
`OPERATIONS.md` and obeyed by hand. Obeyed by hand is fine for a sitting
somebody is watching. It is not fine for an overnight run, where the
failure mode is that the seat burns the week's window at 02:00 and every
round after it comes back `codex_failed  exit 1` with no more explanation
than that -- a whole night of grading lost, and the cost only visible the
next morning.

WHERE THE NUMBER COMES FROM. Codex writes its rate-limit state into every
session rollout, on the `token_count` event it emits after each turn:

    {"timestamp":"2026-08-30T04:45:37.586Z", ..., "type":"event_msg",
     "payload":{"type":"token_count","info":{...},
       "rate_limits":{"limit_id":"codex",
         "primary":{"used_percent":3.0,"window_minutes":300,
                    "resets_at":1788079221},
         "secondary":{"used_percent":11.0,"window_minutes":10080,
                      "resets_at":1788645521},
         "plan_type":"plus", ...}}}

`primary` is the five-hour window, `secondary` the week. THE READ IS
AS-OF THE LAST CALL, not as of now: nothing here asks OpenAI anything, it
reads a file Codex already wrote. So the number is a lower bound that goes
stale the moment somebody uses `codex` outside this harness, and the stop
lines below are set with room for that. `$CODEX_HOME` is Codex's, and this
module only ever READS it.

A ROLLED-OVER WINDOW READS AS ZERO. If `resets_at` is in the past, that
window has rolled over since the line was written and the recorded
`used_percent` describes a window that no longer exists. Carrying it
forward would refuse calls on a budget that has already been refunded, so
a stale window is reported as 0% used and the summary says which.

    python -m understudy.codex_usage
    codex: 5h 3% (resets 04:40 EDT) . week 11% (resets Sep 05 17:58) . from
    rollout <path> @ <timestamp>

THE STOP LINES are `CODEX_PRIMARY_STOP_PERCENT` (85) and
`CODEX_WEEKLY_STOP_PERCENT` (50), overridable per-run with
`GITS_CODEX_PRIMARY_STOP` / `GITS_CODEX_WEEKLY_STOP`. They are deliberately
asymmetric. The five-hour window refills five hours later, so stopping at
85% costs an overnight run one pause; the WEEK does not refill until the
week does, and a week spent by Wednesday is a week with no independent seat
in it -- which is R213's first guard gone, not merely a slow night. Half
the week is the point at which an unattended run should stop deciding on
its own that the rest is worth spending.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

#: Refuse a `codex exec` at or above this much of the FIVE-HOUR window.
CODEX_PRIMARY_STOP_PERCENT = 85.0
#: Refuse a `codex exec` at or above this much of the WEEKLY window.
CODEX_WEEKLY_STOP_PERCENT = 50.0

PRIMARY_STOP_ENV = "GITS_CODEX_PRIMARY_STOP"
WEEKLY_STOP_ENV = "GITS_CODEX_WEEKLY_STOP"


def codex_home() -> Path:
    """`$CODEX_HOME`, or `~/.codex`. Read-only, always."""
    return Path(os.environ.get("CODEX_HOME") or (Path.home() / ".codex"))


def _stop(env: str, default: float) -> float:
    raw = os.environ.get(env)
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        # A typo in an env var must not silently disable the guard.
        return default


def primary_stop() -> float:
    return _stop(PRIMARY_STOP_ENV, CODEX_PRIMARY_STOP_PERCENT)


def weekly_stop() -> float:
    return _stop(WEEKLY_STOP_ENV, CODEX_WEEKLY_STOP_PERCENT)


def _tz_abbrev(when: datetime) -> str:
    """`EDT`, not `Eastern Daylight Time`.

    Windows' `%Z` gives the long name where POSIX gives the abbreviation,
    and a one-line status that spends twenty-two characters on a timezone
    is not a one-line status. Initials of a multi-word name, otherwise the
    name as given.
    """
    name = when.strftime("%Z")
    if not name:
        return "local"
    words = name.split()
    if len(words) > 1:
        return "".join(w[0] for w in words).upper()
    return name


# ------------------------------------------------------------- the read ----

@dataclass(frozen=True)
class Window:
    """One rate-limit window as the rollout recorded it."""

    name: str                       # "primary" / "secondary"
    used_percent: float             # 0.0 for a window that has rolled over
    reported_percent: float         # what the file actually said
    window_minutes: int
    resets_at: datetime | None      # aware, local time
    stale: bool                     # resets_at is in the past

    @property
    def label(self) -> str:
        """`5h`, `week`, `24h`, `3d` -- the window, said the short way."""
        m = self.window_minutes
        if m <= 0:
            return "?"
        if m == 10080:
            return "week"
        if m % 1440 == 0:
            days = m // 1440
            return "day" if days == 1 else f"{days}d"
        if m % 60 == 0:
            return f"{m // 60}h"
        return f"{m}m"

    def resets_text(self) -> str:
        if self.resets_at is None:
            return "resets ?"
        if self.stale:
            return "rolled over"
        # A window inside a day is a clock time; a longer one needs a date,
        # because "resets 17:58" on a weekly window says nothing useful.
        if self.window_minutes < 1440:
            return f"resets {self.resets_at:%H:%M} {_tz_abbrev(self.resets_at)}"
        return f"resets {self.resets_at:%b %d %H:%M}"

    def text(self) -> str:
        return (f"{self.label} {self.used_percent:g}% "
                f"({self.resets_text()})")


@dataclass(frozen=True)
class Usage:
    """The seat's own meter, as of the last `codex` call on this machine."""

    primary: Window
    secondary: Window
    rollout: Path
    observed_at: datetime | None
    plan: str = ""

    def summary(self) -> str:
        when = (f"{self.observed_at:%Y-%m-%dT%H:%M:%SZ}"
                if self.observed_at is not None else "?")
        line = (f"codex: {self.primary.text()} · {self.secondary.text()} "
                f"· from rollout {self.rollout} @ {when}")
        rolled = [w.label for w in (self.primary, self.secondary) if w.stale]
        if rolled:
            line += (f" [{' and '.join(rolled)} window rolled over since that "
                     f"line -- counted as 0% used]")
        return line

    def over(self) -> tuple[str, str] | None:
        """`(reason, detail)` when a stop line is reached, else `None`."""
        if self.primary.used_percent >= primary_stop():
            return ("codex_budget_primary",
                    f"{self.primary.label} window at "
                    f"{self.primary.used_percent:g}% of the "
                    f"{primary_stop():g}% stop line "
                    f"({self.primary.resets_text()})")
        if self.secondary.used_percent >= weekly_stop():
            return ("codex_budget_weekly",
                    f"{self.secondary.label} window at "
                    f"{self.secondary.used_percent:g}% of the "
                    f"{weekly_stop():g}% stop line "
                    f"({self.secondary.resets_text()})")
        return None

    def record(self) -> dict[str, Any]:
        """What a per-call ledger row carries, so cost per call is learnable."""
        out: dict[str, Any] = {
            "rollout": str(self.rollout),
            "observed_at": (f"{self.observed_at:%Y-%m-%dT%H:%M:%SZ}"
                            if self.observed_at is not None else ""),
            "primary_stop_percent": primary_stop(),
            "weekly_stop_percent": weekly_stop(),
        }
        for w in (self.primary, self.secondary):
            out[f"{w.name}_used_percent"] = w.used_percent
            out[f"{w.name}_reported_percent"] = w.reported_percent
            out[f"{w.name}_window_minutes"] = w.window_minutes
            out[f"{w.name}_stale"] = w.stale
            out[f"{w.name}_resets_at"] = (w.resets_at.isoformat()
                                          if w.resets_at else "")
        if self.plan:
            out["plan_type"] = self.plan
        return out


def newest_rollout(home: Path | None = None) -> Path | None:
    """The most recently written `sessions/YYYY/MM/DD/rollout-*.jsonl`.

    By mtime rather than by name: the filename's stamp is the session's
    START, and a long session's rate-limit lines are newer than a short
    session that began after it.
    """
    sessions = (home or codex_home()) / "sessions"
    if not sessions.is_dir():
        return None
    found = list(sessions.rglob("rollout-*.jsonl"))
    if not found:
        return None
    return max(found, key=lambda p: p.stat().st_mtime)


def _window(name: str, blob: Any, now: datetime) -> Window:
    d = blob if isinstance(blob, dict) else {}
    resets_raw = d.get("resets_at")
    resets: datetime | None = None
    if isinstance(resets_raw, (int, float)):
        try:
            resets = datetime.fromtimestamp(float(resets_raw),
                                            tz=timezone.utc).astimezone()
        except (OverflowError, OSError, ValueError):
            resets = None
    reported = float(d.get("used_percent") or 0.0)
    stale = resets is not None and resets <= now
    return Window(name=name,
                  used_percent=0.0 if stale else reported,
                  reported_percent=reported,
                  window_minutes=int(d.get("window_minutes") or 0),
                  resets_at=resets,
                  stale=stale)


def _lines(path: Path) -> Iterable[str]:
    with path.open(encoding="utf-8", errors="replace") as fh:
        return fh.readlines()


def usage_from_lines(lines: Iterable[str], *, rollout: Path,
                     now: datetime | None = None) -> Usage | None:
    """The LAST `rate_limits` block in these lines, or `None` if there is none.

    A rollout carries one such block per turn and the newest is the truth;
    `rate_limits` is also legitimately `null` on some `token_count` events,
    which is a line to skip rather than a file to give up on.
    """
    now = now or datetime.now(timezone.utc).astimezone()
    latest: dict[str, Any] | None = None
    stamp: datetime | None = None
    for raw in lines:
        raw = raw.strip()
        if not raw or '"rate_limits"' not in raw:
            continue
        try:
            row = json.loads(raw)
        except ValueError:
            continue
        payload = row.get("payload") or {}
        # BOTH HOMES ACCEPTED. On the rollouts this was built against
        # (codex 0.56, 2026-08-30) `rate_limits` is a sibling of `info` on
        # the `token_count` payload; older writeups put it inside `info`.
        # Reading both costs one `or` and outlives one refactor upstream.
        limits = payload.get("rate_limits")
        if not isinstance(limits, dict):
            limits = (payload.get("info") or {}).get("rate_limits")
        if not isinstance(limits, dict):
            continue
        latest = limits
        ts = str(row.get("timestamp") or "")
        try:
            stamp = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            stamp = None
    if latest is None:
        return None
    return Usage(primary=_window("primary", latest.get("primary"), now),
                 secondary=_window("secondary", latest.get("secondary"), now),
                 rollout=rollout,
                 observed_at=stamp,
                 plan=str(latest.get("plan_type") or ""))


def probe(*, home: Path | None = None,
          now: datetime | None = None) -> Usage | None:
    """The seat's meter, or `None` when there is nothing on disk to read.

    NEVER raises for a missing or unreadable file: a machine that has not
    run `codex` yet, or a pruned `$CODEX_HOME`, is not a reason to refuse a
    round. The caller logs and proceeds.
    """
    path = newest_rollout(home)
    if path is None:
        return None
    try:
        lines = _lines(path)
    except OSError:
        return None
    return usage_from_lines(lines, rollout=path, now=now)


def main(argv: list[str] | None = None) -> int:
    usage = probe()
    if usage is None:
        where = newest_rollout()
        detail = (f"no rollout under {codex_home() / 'sessions'}"
                  if where is None
                  else f"no rate-limit line in {where}")
        print(f"codex: {detail} -- no rate-limit read available")
        return 1
    print(usage.summary())
    over = usage.over()
    if over:
        print(f"OVER THE STOP LINE  {over[0]}: {over[1]}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":                                # pragma: no cover
    raise SystemExit(main())
