"""The Teyvat dressed-event id table, and the id rule it is read with.

Cut out of `understudy/force_event.py` by `EB-396`, WHOLE and unchanged, for
one reason: the blind page needs to know which base event a dressed page is,
and `force_event` imports `tier05.maps` and `policy_v0` -- neither of which
`blindplay` may have. This module imports the standard library and nothing
else, so both sides read ONE table (see the comment below on why a second one
maintained by hand is the failure mode this avoids).

`force_event` re-exports every name here, so `force_event.wire_id` and
`force_event.dressed_to_base` still resolve and every existing caller and pin
is untouched.
"""
from __future__ import annotations

import functools
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


# ------------------------------------------- EB-767: dressed -> base ------
#
# THE OP TAKES BASE IDS ONLY, AND THAT IS NOT A BUG IN THE OP.
#
# A Teyvat dressing does not replace an event in the act's pool. It cannot:
# `ActModel.GenerateRooms` concatenates `AllEvents` with
# `ModelDb.AllSharedEvents` and shuffles the whole thing ONCE on the run's
# `UpFront` rng, so a pool one element longer or shorter moves every later roll
# on that stream -- bosses, Ancients, encounter order. The substitution
# therefore happens DOWNSTREAM of the shuffle, in the `PullNextEvent` postfix
# (`klee-mod/KleeCode/Teyvat/Patches/PullNextEventPatch.cs`): the pending list
# holds the BASE event, and the dressed model is swapped in at the moment the
# map hands the player an event.
#
# So `force_next_event` -- which walks the pending list -- can only ever find a
# base id. Six proof ids were typed as their dressed names and all six failed
# against a run that was holding exactly the events they dress
# (`review/records/teyvat-proofs-3-2026-09-15.md`), and a `?` room forced by a
# name nothing matched can also resolve to a room that is not an event at all.
# This maps the name a reader has (the dressed one, the one on the page) to the
# name the op needs, and SAYS SO on every translation rather than doing it
# quietly -- a driver that silently retargeted an id would make the next
# failure unreadable.
#
# THE TABLE IS THE GENERATED FILE ITSELF, not a copy of it. `TeyvatEventsGenerated.cs`
# is written by `tools/gen_teyvat_events.py` from the curated faces and is
# checked for drift by that generator's own `--check`, so reading it here means
# there is exactly one substitution table in the repo. A second one maintained
# by hand would be a second thing to forget when a face lands.

_SUBSTITUTIONS_SOURCE = (REPO / "klee-mod" / "KleeCode" / "Teyvat"
                         / "TeyvatEventsGenerated.cs")

#: `[(TeyvatFrame.<Dressing>, typeof(<BaseClass>))] = () =>
#:  ModelDb.Event<Events.<Dressing>.<DressedClass>>(),` -- one generated row.
_SUBSTITUTION_ROW = re.compile(
    r"\[\(TeyvatFrame\.(\w+),\s*typeof\((\w+)\)\)\]\s*=\s*"
    r"\(\)\s*=>\s*ModelDb\.Event<Events\.\w+\.(\w+)>\(\)")

#: An underscore before each capital that follows a letter or digit. This is
#: `StringHelper.Slugify` for the one input shape it is handed here, a C# type
#: name, and it is what `ModelDb.GetEntry` does to produce an `Id.Entry`.
#: `tier0/tests/test_understudy_force_event.py` pins it against
#: `tools/gen_teyvat_events.py`'s own copy over every class name in the table,
#: so the two cannot drift into disagreeing about an id.
_CAMEL = re.compile(r"(?<=[A-Za-z0-9])([A-Z])")


def wire_id(class_name: str) -> str:
    """A C# event class name as the wire spells its `Id.Entry`."""
    text = _CAMEL.sub(r"_\1", class_name.strip())
    return re.sub(r"[^A-Z0-9_]", "", re.sub(r"\s+", "_", text.upper()))


@functools.lru_cache(maxsize=1)
def dressed_to_base() -> dict[str, tuple[str, str]]:
    """`{dressed wire id: (base wire id, dressing)}`, read off the generator's
    output. An empty dict when that file is missing, because a harness without
    the Teyvat sources should still force a base id.
    """
    try:
        text = _SUBSTITUTIONS_SOURCE.read_text(encoding="utf-8")
    except OSError:
        return {}
    _, _, block = text.partition("Substitutions =")
    table: dict[str, tuple[str, str]] = {}
    for dressing, base_cls, dressed_cls in _SUBSTITUTION_ROW.findall(block):
        table[wire_id(dressed_cls)] = (wire_id(base_cls), dressing)
    return table


def resolve_event_id(event_id: str) -> tuple[str, str | None]:
    """`(the id to force, the dressing it was translated out of or None)`.

    An id the table does not know is returned UNCHANGED and untranslated: this
    is a translation and never a validation, and the endpoint's own refusal --
    which prints the act's pending list back -- is a better answer for an
    unknown id than a guess made here without a run up.
    """
    target = (event_id or "").strip()
    row = dressed_to_base().get(target.upper())
    if row is None:
        return target, None
    return row[0], row[1]
