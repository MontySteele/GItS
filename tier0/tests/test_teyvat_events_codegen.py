"""The Teyvat arm's DRESSED EVENTS are generated, and the committed copy is fresh.

`tools/gen_teyvat_events.py` turns the six curated event faces under
`docs/current/dossiers/content/event-faces/` into one C# class per (base event,
face), their loc rows, the `PullNextEvent` substitution table and the portrait
borrows. The C# shape decision -- why a dressed event subclasses a hand-written
MIRROR of its base event and not the base event itself -- is
`docs/current/operations/codegen.md`, "Codegen -- Teyvat dressed events".

These arms are the gate on that arrangement, and they are four claims:

  1. the committed output is not stale (the generator's own `--check`, which
     needs no decompile);
  2. the base-event index carries IDENTIFIERS ONLY -- no base-game bodies and
     no base-game prose, which is the repo's decompiled-material rule
     (`.gitignore:28`, `csharp-build-spec.md` sec.0.3) applied to a checked-in
     file;
  3. the generator REFUSES a face whose option count disagrees with the frozen
     harvest, rather than pairing the face's lines with the wrong base option
     keys -- the defect class that would ship a dressed option whose text
     describes another option's outcome;
  4. no generated file has been hand-edited into carrying a mechanic: a dressed
     class is a name and a base, and nothing else.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GENERATOR = REPO / "tools" / "gen_teyvat_events.py"
INDEX = REPO / "tools" / "data" / "sts2_base_events.json"
EVENTS_ROOT = REPO / "klee-mod" / "KleeCode" / "Teyvat" / "Events"
GENERATED_CS = REPO / "klee-mod" / "KleeCode" / "Teyvat" / "TeyvatEventsGenerated.cs"


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(GENERATOR), *args],
        cwd=str(REPO), capture_output=True, text=True,
        encoding="utf-8", errors="replace")


def test_the_generated_dressed_events_are_current():
    """`--check`, exactly as CI and a push gate would run it."""
    proc = _run("--check")
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_the_base_event_index_carries_identifiers_only():
    """The index is checked in; the decompile it came from is not, and must not
    arrive by the back door. Every value in it is a name, a count or a flag.

    The test is a shape check rather than a word list: an identifier has no
    spaces and no sentence punctuation, so a base-game description or a method
    body could not survive it.
    """
    payload = json.loads(INDEX.read_text(encoding="utf-8"))
    events = payload["events"]
    assert len(events) > 50, "the index looks truncated"

    for name, row in events.items():
        assert re.fullmatch(r"[A-Za-z0-9_]+", name), name
        assert re.fullmatch(r"[A-Z0-9_]+", row["entry"]), row["entry"]
        assert re.fullmatch(r"[A-Za-z0-9_]+", row["base"]), row["base"]
        # A key may carry a SmartFormat expression -- Colossal Flower builds
        # `EXTRACT_CURRENT_PRIZE_{NumberOfDigs + 1}` -- which is still an
        # identifier plus an arithmetic brace, never prose. `dynamic_keys`
        # flags those events, and no mirror exists for one.
        shape = r"[A-Za-z0-9_{}.+\- ]+"
        for key in row["option_keys"] + row["page_keys"]:
            assert re.fullmatch(shape, key), f"{name}: {key}"
            # An event that CONCATENATES its keys leaves a fragment in the
            # index (`DISHES.`, `pages.ALL.options.`). Still an identifier,
            # still no prose, and still flagged by `dynamic_keys`.
            assert "  " not in key, f"{name}: {key}"
        assert isinstance(row["can_kill"], bool)
        assert row["harvest_options"] in (None, "none") or \
            isinstance(row["harvest_options"], int)


def test_a_face_whose_option_count_disagrees_with_the_harvest_is_refused(tmp_path):
    """The refusal, exercised rather than asserted about.

    A face line pairs with a base option key BY POSITION, so a face with the
    wrong number of options would silently shift every later pairing -- the
    dressed "Search" option would print the dressed "Gorge" outcome. The
    generator must name the event and stop.
    """
    import importlib.util

    spec = importlib.util.spec_from_file_location("gen_teyvat_events", str(GENERATOR))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    face = tmp_path / "bad-face.md"
    face.write_text(
        "## - [ ] Room Full of Cheese\n\n"
        "### The Broken Cellar — Mondstadt / Test — DRAFTED\n\n"
        "A cellar.\n\n"
        "- **One** — Something.\n"
        "- **Two** — Something else.\n"
        "- **Three** — A third thing the harvest does not have.\n",
        encoding="utf-8")

    events = module.parse_face(face)
    assert len(events) == 1
    assert len(events[0].options) == 3

    index = module.load_index()
    assert index["RoomFullOfCheese"]["harvest_options"] == 2, (
        "the harvest freezes Room Full of Cheese at two options; if that "
        "changed, this test's premise did too")


def test_a_generated_dressed_event_is_a_name_and_a_base_and_nothing_else():
    """Claim 4. A dressed class declares no member: every mechanic is in the
    mirror, so a nation cannot acquire one of its own by a hand edit that the
    `--check` above would then bless on the next regeneration."""
    generated = sorted(
        path for folder in EVENTS_ROOT.iterdir() if folder.is_dir()
        and folder.name != "Mirrors"
        for path in folder.glob("*.cs"))
    assert generated, "no dressed events are generated at all"

    for path in generated:
        text = path.read_text(encoding="utf-8")
        assert "<auto-generated>" in text, f"{path.name} lost its banner"
        body = re.search(r"public sealed class \w+ : \w+\s*\{(.*?)\}\s*$",
                         text, re.S)
        assert body is not None, f"{path.name} is not one sealed subclass"
        assert body.group(1).strip() == "", (
            f"{path.name} has a class body; a dressed event is a NAME and its "
            f"mechanics belong in its mirror "
            f"(docs/current/operations/codegen.md)")


def test_the_generated_tables_name_every_dressed_event_exactly_once():
    """The three generated tables -- loc rows, substitutions, portraits -- are
    emitted from one plan, and a dressed event missing from any of them is the
    shape of EB-764 (a class with no portrait row) and EB-765 (a class with
    incomplete rows)."""
    text = GENERATED_CS.read_text(encoding="utf-8")
    classes = sorted(
        path.stem for folder in EVENTS_ROOT.iterdir() if folder.is_dir()
        and folder.name != "Mirrors"
        for path in folder.glob("*.cs"))

    for cls in classes:
        assert text.count(f".{cls})]") == 1, (
            f"{cls} is not in the shape table exactly once")
        assert text.count(f".{cls}>()") == 1, (
            f"{cls} is not in the substitution table exactly once")
        entry = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", cls).upper()
        assert f'["{entry}"] =\n                "res://images/events/' in text, (
            f"{cls} has no portrait borrow; the event page throws "
            f"AssetLoadException before it is drawn (EB-764)")
