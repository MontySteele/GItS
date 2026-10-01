"""`observe --brief` / `act --brief`: the page with its reference sections cut.

THE FIND (2026-09-30). Seats kept writing their own grep and awk wrappers
around `observe` to get the glossary off the screen, and one such filter
dropped every line containing "this part lands on you" -- the enemy attack
intents -- and the refusals with them. The seat played blind to the hits and
lost 41 HP. A trim the seat writes for itself is a trim nobody tested.

So the trim is the tool's, and it is a LIST OF WHAT MAY GO, never a filter on
what a line says:

- the `## Words on this screen` section (the glossary, the bulk of a page);
- the standing notes that print the same sentence every screen (the enemy
  handle note, the power-feed note, the end-of-turn order note, the play
  guardrail);
- a section whose only line is its own "nothing here" placeholder.

Everything else passes through untouched, in order. And then the safety net,
which is what "by construction" means here: every line the trim removed is
checked against `PROTECTED`, and if any of them is an intent, a damage line,
an HP / Block / Energy row, a refusal, an error, a blocked or waiting banner,
a heading the brief must keep, or a verb under *What you can say*, the brief
page is abandoned and the FULL page is returned. A brief page that would hide
one of those is not a brief page.
"""
from __future__ import annotations

import re

from understudy.blindplay_notes import (ENEMY_HANDLE_NOTE,
                                        NO_REACTION_THIS_TURN,
                                        NO_RESOLUTIONS_THIS_TURN, POWER_NOTE)
from understudy.blindplay_shape import PLAY_GUARDRAIL

#: Sections the brief page drops whole, heading and body.
DROPPED_SECTIONS = frozenset({"## Words on this screen"})

#: Lines the brief page drops wherever they appear: standing notes that print
#: the same sentence on every screen, and the empty-section placeholders.
DROPPED_LINES = frozenset({ENEMY_HANDLE_NOTE, POWER_NOTE, PLAY_GUARDRAIL,
                           NO_REACTION_THIS_TURN, NO_RESOLUTIONS_THIS_TURN})

#: `TURN_ORDER_NOTE` is formatted per board, so it is matched by its opening.
DROPPED_PREFIXES = ("*The end of your turn is a step of its own",)

#: Headings that are never dropped, even when their body is empty.
KEPT_HEADINGS = frozenset({"## What you can say", "## Your hand",
                           "## The other side", "## The other player"})

#: The line at the foot of a brief page, above the verbs.
BRIEF_NOTE = ("*Brief page: the word definitions and the standing notes are "
              "left out. `observe` without --brief prints them.*")

#: A removed line matching this means the trim went wrong; the full page is
#: returned instead. Intents and what lands on you, the player's own rows,
#: refusals and errors, banners, and the verbs.
PROTECTED = re.compile(
    r"lands on you|Intent:|intends to|"
    r"^- (HP|Block|Energy) |"
    r"REFUSED|refus|[Ee]rror|NO ANSWER|TOOL-BLOCKED|WAITING|budget|"
    r"^- `|^# ")


def _drop_line(line: str) -> bool:
    return line in DROPPED_LINES or line.startswith(DROPPED_PREFIXES)


def _trim(text: str) -> tuple[list[str], list[str]]:
    """(kept lines, removed lines)."""
    lines = text.splitlines()
    # Split into a preamble and sections, each section opening on a `## `.
    blocks: list[list[str]] = [[]]
    for line in lines:
        if line.startswith("## "):
            blocks.append([line])
        else:
            blocks[-1].append(line)
    kept: list[str] = []
    removed: list[str] = []
    for block in blocks:
        heading = block[0] if block and block[0].startswith("## ") else ""
        if heading in DROPPED_SECTIONS:
            removed += [ln for ln in block if ln.strip()]
            continue
        body = block[1:] if heading else block
        dropped = [ln for ln in body if _drop_line(ln)]
        rest = [ln for ln in body if not _drop_line(ln)]
        removed += dropped
        if (heading and heading not in KEPT_HEADINGS and dropped
                and not any(ln.strip() for ln in rest)):
            removed.append(heading)
            continue
        kept += ([heading] if heading else []) + rest
    return kept, removed


def _collapse_blanks(lines: list[str]) -> list[str]:
    out: list[str] = []
    for line in lines:
        if not line.strip() and (not out or not out[-1].strip()):
            continue
        out.append(line)
    while out and not out[-1].strip():
        out.pop()
    return out


def brief(text: str) -> str:
    """The brief page for a full page `observe` rendered, or the full page if
    the trim would have removed anything in `PROTECTED`."""
    kept, removed = _trim(text)
    if not removed:
        return text
    if any(PROTECTED.search(line) for line in removed):
        return text
    if "## What you can say" in kept:
        at = kept.index("## What you can say")
        kept = kept[:at] + [BRIEF_NOTE, ""] + kept[at:]
    else:
        kept += ["", BRIEF_NOTE]
    return "\n".join(_collapse_blanks(kept)) + "\n"
