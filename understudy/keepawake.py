"""EB-226: while the harness holds the game, Windows may not go to sleep.

WHY THIS EXISTS. Two overnight runs died to the power plan, not to a defect
in anything this repo owns. The System log records
`Kernel-Power 42 -- "entering sleep -- Sleep Reason: System Idle"` at
2026-08-29 07:05:40, with the resume at 11:21:48 on a mouse movement: a
4 h 16 m hole punched through the middle of a running funnel, the game
process suspended mid-fight, the bridge socket dead on the far side. It
happened again at 2026-08-30 00:56:17. The AC standby timeout was five
hours; [USER] has since set it to never.

THAT SETTING IS NOT THE FIX. A power plan is machine state: it survives no
reinstall, no new machine, no Windows update that resets a plan to its
default, and nothing in this tree can see that it was changed. A harness that
runs unattended for eight hours cannot rest on a control panel checkbox
somebody has to remember. The harness asks for what it needs, for exactly as
long as it needs it, and gives it back.

WHAT THE ASK IS. `SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)`
tells the power manager that this thread's work counts as activity: the idle
timer stops, the machine stays awake. `ES_CONTINUOUS` alone clears the
request. This is deliberately the WEAK form of the ask -- no
`ES_DISPLAY_REQUIRED` -- because the run does not need the monitor lit, only
the CPU running, and a harness that also kept the screen on overnight would
be a worse neighbour than the sleep it is preventing. A lid close or an
explicit "Sleep" from the Start menu still sleeps the machine; this blocks
the IDLE timer, which is the thing that actually bit.

THE FLAGS ARE PER-THREAD, WHICH IS THE WHOLE DESIGN OF THIS FILE. The state
lives on the calling thread and dies with it, and the request is released
when that thread exits. The thing this module has to keep awake -- a
`soak.Session` from `setup()` to `teardown()` -- is emphatically NOT a
single thread: `local_tester`'s two-lane round calls `setup()` on a lane
worker and may reach `teardown()` from another, `GameLane.step` binds and
unbinds threads under it, and any of those workers may finish and be
collected while the game is still up. Putting the `ctypes` call inline in
`Session.setup` would therefore hold a request on a thread that exits ten
minutes later, silently releasing it -- the exact failure this file exists to
prevent, with the added insult of looking correct in the diff.

So the request gets its OWN thread, whose only job is to stay alive. It sets
the flag, blocks on an event, and clears the flag on the way out. The thread
outlives every lane worker by construction because it has nothing else to do,
and `release()` is what ends it. Callers may be on any thread, and the
count is refcounted so a two-lane round's two sessions hold one request
between them and the first teardown does not release it out from under the
second.

NOT WINDOWS, OR NO `kernel32`: a one-line log and a no-op. This is a
Windows-only concern and a CI runner has no business pretending otherwise.

VERIFYING IT: `powercfg /requests` while a run is up prints the holder under
`SYSTEM:`, named by the executable that asked -- the python running the
harness. See `docs/current/operations/understudy-seats.md` beside the
funnel's lock text.
"""

from __future__ import annotations

import contextlib
import sys
import threading
from typing import Any, Callable

# The two `ES_` constants this file uses, spelled as Windows spells them.
# `ES_CONTINUOUS` means "this is the new standing state" rather than "count
# this instant as activity"; on its own it is the release.
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001

#: What `acquire` asks for, and what a test asserts it saw.
ES_HOLD = ES_CONTINUOUS | ES_SYSTEM_REQUIRED
#: What `release` asks for.
ES_FREE = ES_CONTINUOUS


def kernel32_setter() -> Callable[[int], Any] | None:
    """`SetThreadExecutionState`, or `None` where there is no such thing."""
    if sys.platform != "win32":
        return None
    try:
        import ctypes
        return ctypes.windll.kernel32.SetThreadExecutionState  # type: ignore
    except Exception:                                        # noqa: BLE001
        # A missing `windll` (any non-CPython-on-Windows runtime) and a
        # kernel32 without the symbol land in the same place on purpose:
        # neither is an error the harness should die of.
        return None


class PowerRequest:
    """A refcounted `ES_SYSTEM_REQUIRED` hold with its own owning thread."""

    def __init__(self, *, set_state: Callable[[int], Any] | None = None,
                 log: Callable[[str], None] | None = None,
                 probe: Callable[[], Callable[[int], Any] | None] | None = None):
        # `set_state` given explicitly is the test seam; `probe` is the
        # lookup, deferred so a process that never holds the game never
        # touches `ctypes` at all.
        self._explicit = set_state
        self._probe = probe or kernel32_setter
        self._log = log if log is not None else (lambda msg: print(msg))
        self._mutex = threading.Lock()
        self._count = 0
        self._thread: threading.Thread | None = None
        self._stop: threading.Event | None = None
        self._logged_absent = False

    # -- state ------------------------------------------------------------
    @property
    def held(self) -> bool:
        return self._thread is not None

    @property
    def holders(self) -> int:
        return self._count

    # -- the two doors ----------------------------------------------------
    def acquire(self, reason: str = "") -> bool:
        """Hold the request. Returns True only on the acquire that took it."""
        with self._mutex:
            self._count += 1
            if self._count > 1 or self._thread is not None:
                return False
            setter = (self._explicit if self._explicit is not None
                      else self._probe())
            if setter is None:
                if not self._logged_absent:
                    self._logged_absent = True
                    self._log("power request: not available on this platform "
                              "-- the harness will not stop an idle sleep")
                return False
            stop = threading.Event()
            started = threading.Event()
            thread = threading.Thread(
                target=self._own, args=(setter, started, stop),
                name="gits-power-request", daemon=True)
            self._thread = thread
            self._stop = stop
            thread.start()
            started.wait(timeout=5.0)
            tail = f" ({reason})" if reason else ""
            self._log(f"power request: held -- idle sleep is blocked while "
                      f"the harness holds the game{tail}")
            return True

    def release(self) -> bool:
        """Drop one holder. Returns True only on the release that let go."""
        with self._mutex:
            if self._count > 0:
                self._count -= 1
            if self._count > 0 or self._thread is None:
                return False
            thread, stop = self._thread, self._stop
            self._thread = self._stop = None
        if stop is not None:
            stop.set()
        if thread is not None:
            thread.join(timeout=5.0)
        self._log("power request: released -- the machine may idle again")
        return True

    @contextlib.contextmanager
    def holding(self, reason: str = ""):
        """`with power.holding(...)`: released on the way out, exception or not."""
        self.acquire(reason)
        try:
            yield self
        finally:
            self.release()

    # -- the owning thread ------------------------------------------------
    def _own(self, setter: Callable[[int], Any],
             started: threading.Event, stop: threading.Event) -> None:
        """Set the flag, stay alive, clear the flag. Nothing else, ever.

        Every line of this runs on ONE thread because the flag is that
        thread's; `started` exists so `acquire` does not return before the
        request is actually up, and the `finally` sets it even when the
        first call raises so an acquire can never hang on a broken kernel32.
        """
        try:
            try:
                setter(ES_HOLD)
            finally:
                started.set()
        except Exception as exc:                             # noqa: BLE001
            self._log(f"power request: refused by the OS ({exc}) -- the "
                      f"harness will not stop an idle sleep")
            return
        stop.wait()
        try:
            setter(ES_FREE)
        except Exception as exc:                             # noqa: BLE001
            self._log(f"power request: could not be released ({exc})")


#: THE process-wide request. One machine, one idle timer, one hold: two lanes
#: sharing one install share this too, and the refcount is what keeps lane
#: 0's teardown from waking the timer under lane 1.
REQUEST = PowerRequest()


def acquire(reason: str = "") -> bool:
    return REQUEST.acquire(reason)


def release() -> bool:
    return REQUEST.release()
