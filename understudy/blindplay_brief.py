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
- a section whose only line is its own "nothing here" placeholder;
- the italic gloss lines, `*Word* — what it means`, that print under a card,
  a relic or an enemy (2026-10-01: three of four seats still cut them with
  their own `grep -v` after `--brief` shipped), and the standing reference
  notes on FRONT, auras, multi-part intents, intent figures and repeated
  names.

2026-10-01, THE WORD NOBODY DEFINED. An Infested Prism elite made every
Skill "Tainted 2" and a base-game seat on `--brief` never once saw what
Tainted does: the glossary was cut on every screen, including the first. So
a definition -- a glossary row or an italic gloss -- is now KEPT the first
time it prints on a lane, and dropped on every screen after it. The lane's
seen words live beside its action budget (`blindplay_shape.words_seen_path`)
and are cleared where the budget is set, at embark. `observe --define
"<Word>"` prints one definition again.

A gloss or note line that matches `PROTECTED` is KEPT where it stands rather
than dropped: the line-level trim never removes an intent, a refusal or a
verb, whatever it is wrapped in.

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

from understudy.blindplay_notes import (AURA_NOTE, ENEMY_HANDLE_NOTE,
                                        FRONT_ENEMY_NOTE, HAND_REPEAT_NOTE,
                                        MULTI_INTENT_NOTE,
                                        NO_REACTION_THIS_TURN,
                                        NO_RESOLUTIONS_THIS_TURN, POWER_NOTE,
                                        _INTENT_SOURCE_HEAD,
                                        glossary_definition)
from understudy.blindplay_enemies import brief_by_name
from understudy.blindplay_shape import PLAY_GUARDRAIL

#: The glossary section. Its rows are kept the first time each prints on a
#: lane and dropped after; with no lane memory it is dropped whole.
WORDS_HEADING = "## Words on this screen"
DROPPED_SECTIONS = frozenset({WORDS_HEADING})

#: Lines the brief page drops wherever they appear: standing notes that print
#: the same sentence on every screen, and the empty-section placeholders.
DROPPED_LINES = frozenset({ENEMY_HANDLE_NOTE, POWER_NOTE, PLAY_GUARDRAIL,
                           NO_REACTION_THIS_TURN, NO_RESOLUTIONS_THIS_TURN})

def _opening(note: str) -> str:
    """A standing note's first words, which is how a note formatted per board
    (or wrapped) is matched."""
    return note[:40]


#: `TURN_ORDER_NOTE` is formatted per board, so it is matched by its opening;
#: so are the standing reference notes seats cut by hand (2026-10-01).
DROPPED_PREFIXES = ("*The end of your turn is a step of its own",
                    *(_opening(n) for n in (
                        FRONT_ENEMY_NOTE, AURA_NOTE, MULTI_INTENT_NOTE,
                        HAND_REPEAT_NOTE, _INTENT_SOURCE_HEAD,
                        "*An intent's figure is the game's own")))

#: The italic gloss: `*Word* — what it means`, indented under the thing that
#: prints it or not. Only this shape; an italic NOTE (a whole sentence in
#: italics, which may be an instruction) is not a gloss and is kept.
GLOSS_LINE = re.compile(r"^\s*\*[^*\s][^*]*\* — ")

#: A definition and the word it defines: a glossary row (`- **Word** — ...`,
#: or a bare `- **Word**` where no rule applies) or an italic gloss.
_WORDS_ROW = re.compile(r"^- \*\*(?P<word>[^*]+)\*\*(?: — (?P<text>.*))?$")
_GLOSS_ROW = re.compile(r"^\s*\*(?P<word>[^*\s][^*]*)\* — (?P<text>.*)$")

#: Headings that are never dropped, even when their body is empty.
KEPT_HEADINGS = frozenset({"## What you can say", "## Your hand",
                           "## The other side", "## The other player"})

#: The line at the foot of a brief page, above the verbs.
BRIEF_NOTE = ("*Brief page: the standing notes, and any word definition "
              "this lane has already printed, are left out. `observe --define "
              "\"<Word>\"` prints one again; `observe` without --brief "
              "prints them all.*")

#: (2026-10-05: `error` as a word, so the Terror Eel's briefing is a gloss
#: the trim may cut, not a line it must keep.)
#: A removed line matching this means the trim went wrong; the full page is
#: returned instead. Intents and what lands on you, the player's own rows,
#: refusals and errors, banners, and the verbs.
PROTECTED = re.compile(
    r"lands on you|Intent:|intends to|Incoming this turn|Since last page|"
    r"^- (HP|Block|Energy) |"
    r"REFUSED|refus|\b[Ee]rror|NO ANSWER|TOOL-BLOCKED|WAITING|budget|"
    r"^- `|^# ")


def definition(line: str) -> tuple[str, str] | None:
    """`(word, meaning)` for a glossary row or an italic gloss, else `None`."""
    hit = _WORDS_ROW.match(line) or _GLOSS_ROW.match(line)
    if not hit:
        return None
    return hit.group("word").strip(), (hit.group("text") or "").strip()


def definition_key(word: str, text: str) -> str:
    """What "already printed" is keyed on: the word and its meaning with the
    figures blanked. A gloss whose number moves (`*Charge scaling*`: "you
    hold 8 Charge") is one definition; a row whose WORDS change (the
    reactions entry, which prints in full once a second element is
    reachable) is a new one and prints once more."""
    return word.casefold() + "|" + re.sub(r"\d+", "#", text.casefold())


def _drop_line(line: str, fresh=None) -> bool:
    """Whether the brief page drops this line. `fresh(line)` answers for a
    definition the lane has not printed yet; without it every gloss goes."""
    if line in DROPPED_LINES:
        return True
    if PROTECTED.search(line):
        return False
    if line.startswith(DROPPED_PREFIXES):
        return True
    if GLOSS_LINE.match(line):
        return not (fresh and fresh(line))
    return False


def _trim(text: str, seen: set[str] | None = None
          ) -> tuple[list[str], list[str]]:
    """(kept lines, removed lines). With `seen`, a definition whose key is
    not in it is kept -- once per page -- and its key is added to it."""
    before = frozenset(seen) if seen is not None else None
    taken: set[str] = set()

    def fresh(line: str) -> bool:
        if before is None:
            return False
        found = definition(line)
        if not found:
            return False
        key = definition_key(*found)
        if key in before or key in taken:
            return False
        taken.add(key)
        return True

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
        body = block[1:] if heading else block
        if heading in DROPPED_SECTIONS:
            rows = [ln for ln in body
                    if ln.strip() and not PROTECTED.search(ln) and fresh(ln)]
            removed += [ln for ln in body if ln.strip() and ln not in rows]
            if rows:
                kept += [heading, ""] + rows + [""]
            else:
                removed.append(heading)
            continue
        verdict = [(ln, _drop_line(ln, fresh)) for ln in body]
        dropped = [ln for ln, gone in verdict if gone]
        rest = [ln for ln, gone in verdict if not gone]
        removed += dropped
        if (heading and heading not in KEPT_HEADINGS and dropped
                and not any(ln.strip() for ln in rest)):
            removed.append(heading)
            continue
        kept += ([heading] if heading else []) + rest
    if seen is not None:
        seen |= taken
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


def brief(text: str, seen: set[str] | None = None) -> str:
    """The brief page for a full page `observe` rendered, or the full page if
    the trim would have removed anything in `PROTECTED`.

    `seen` is the lane's set of definitions already printed (updated in
    place): those are cut, the rest are kept. `None` cuts every definition.
    A page returned whole printed every definition, so those count as seen
    too."""
    kept, removed = _trim(text, seen)
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


#: The marker on a `--define` row taken from the glossary, not this screen.
OFF_SCREEN_MARK = " (not on this screen)"

#: What `observe --define` prints when no glossary table has the word.
NOT_DEFINED = ("No definition of \"{word}\" on this screen. Words defined "
               "here: {words}.")


def define(text: str, word: str) -> str:
    """Every definition of `word` a full page prints -- its glossary row and
    its italic glosses, once each -- else the glossary's own row, marked as
    not on this screen, else the one line saying there is none."""
    want = word.strip().strip('"*').strip().casefold()
    rows: list[str] = []
    words: list[str] = []
    for line in text.splitlines():
        found = definition(line)
        if not found:
            continue
        if found[0] not in words:
            words.append(found[0])
        if found[0].casefold() == want:
            row = (f"- **{found[0]}** — {found[1]}" if found[1]
                   else f"- **{found[0]}**")
            if row not in rows:
                rows.append(row)
    if rows:
        return "\n".join(rows) + "\n"
    # 2026-10-02: a word this screen does not define is looked up in the
    # glossary's own tables, and marked as off-screen.
    found = glossary_definition(want)
    if found:
        return f"- **{found[0]}** — {found[1]}{OFF_SCREEN_MARK}\n"
    # 2026-10-05: an enemy's base-game briefing, by its base name, after
    # round 1 has stopped printing it.
    found = brief_by_name(want)
    if found:
        return f"- **{found[0]}** — {found[1]}{OFF_SCREEN_MARK}\n"
    return NOT_DEFINED.format(word=word.strip(),
                              words=", ".join(words) or "none") + "\n"
