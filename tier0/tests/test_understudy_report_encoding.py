"""EB-93 -- the morning report must survive a cp1252 console.

The failure this pins is not a rendering bug. `render()` produced a correct
report from an intact UTF-8 log; the `print` of it raised
`UnicodeEncodeError: 'charmap' codec can't encode character '\\u266a'` and
`soak.main` exited **1** after three clean runs. An unattended night that
greps for a non-zero exit therefore reads a green soak as a failed one.

The character is committed content -- the two renamed Barbara titles carry a
`U+266A MUSIC NOTE` -- so this is not a one-seed accident: any soak that plays
one ends this way on a default Windows terminal.
"""

from __future__ import annotations

import io

from understudy import report

MUSIC_NOTE = "♪"


def _cp1252_stream() -> io.TextIOWrapper:
    return io.TextIOWrapper(io.BytesIO(), encoding="cp1252")


def test_a_shipped_title_cannot_be_written_to_an_undeclared_cp1252_console():
    """The defect, stated as the thing that must stay true for the fix to be
    load-bearing. If this ever stops raising, the console changed, not us."""
    stream = _cp1252_stream()
    try:
        stream.write(f"Barbara - Let the Show Begin{MUSIC_NOTE}")
        stream.flush()
    except UnicodeEncodeError:
        return
    raise AssertionError("cp1252 accepted U+266A -- the premise moved")


def test_console_safe_makes_the_same_write_succeed():
    stream = _cp1252_stream()
    report.console_safe(stream)
    stream.write(f"Barbara - Let the Show Begin{MUSIC_NOTE}")
    stream.flush()
    assert stream.errors == "backslashreplace"


def test_console_safe_never_raises_on_a_stream_it_cannot_reconfigure():
    """A captured or wrapped stdout is left exactly as it was. The fix may
    not itself become the reason a soak exits non-zero."""

    class Fixed:
        encoding = "cp1252"

        def reconfigure(self, **kw):
            raise ValueError("not reconfigurable")

    report.console_safe(Fixed())          # must not raise
    report.console_safe(object())         # no `reconfigure` at all
