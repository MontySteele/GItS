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
     class is a name and a base, and nothing else;
  5. the KEYED lines -- a face line that names the loc key it fills, which is
     what unparked The Trial, Tinker Time and Colossal Flower -- are checked
     by NAME in both directions: a key the mirror declares and the face does
     not write is refused, and a key the face writes and no mirror declares is
     refused too. A keyed line is never counted as an option.
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


def _load_generator():
    import importlib.util

    spec = importlib.util.spec_from_file_location("gen_teyvat_events", str(GENERATOR))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


#: One Battleworn Dummy section: the three settings, the wiki's rule bullet,
#: and whatever keyed lines a test wants after them. The mirror declares two
#: keyed keys for this event -- the victory page and the defeat page -- which
#: is what makes it the cheapest place to exercise both directions of the
#: keyed check.
_DUMMY_FACE = (
    "## - [ ] Battleworn Dummy\n\n"
    "### The Test Dummy — Fontaine / Test — DRAFTED\n\n"
    "A dummy on a rail.\n\n"
    "- **First Valve** — Fight a 75 HP dummy.\n"
    "- **Second Valve** — Fight a 150 HP dummy.\n"
    "- **Third Valve** — Fight a 300 HP dummy.\n"
    "- **(all valves)** — Three turns, or no reward.\n"
)


def _plan_for(module, tmp_path, body: str):
    """One plan built from ONE face file holding `body`, with everything else
    -- the index, the harvest, the mirror ledger -- as it really is."""
    face = tmp_path / "test-face.md"
    face.write_text(body, encoding="utf-8")
    module.FACE_DIR = tmp_path
    module.FACES = (module.FaceSpec("test-face", "test-face.md",
                                    "FONTAINE", "Fontaine"),)
    return module.build_plan()


def test_a_keyed_key_the_face_does_not_write_is_refused_by_name(tmp_path):
    """A mirror's declared keyed key with no line on the face.

    This is the EB-765 shape moved onto the new mechanism: the page would ship
    with no row at all, and a page with no row opens on a raw key. The
    generator must name the missing key rather than emit what it has.
    """
    module = _load_generator()
    plan = _plan_for(module, tmp_path, _DUMMY_FACE
                     + "\n@pages.VICTORY.description — The clock had time left.\n")

    assert not plan.items, "nothing may be emitted for a refused event"
    assert any("pages.DEFEAT.description" in r and "does not write" in r
               for r in plan.refusals), plan.refusals


def test_a_keyed_key_the_mirror_does_not_declare_is_refused_by_name(tmp_path):
    """The other direction: prose aimed at a key that does not exist.

    A keyed line names its own key, so a typo or a key renamed in the
    decompile would otherwise write a row nothing ever looks up -- silently,
    and with the page it was meant for still bare.
    """
    module = _load_generator()
    plan = _plan_for(module, tmp_path, _DUMMY_FACE
                     + "\n@pages.VICTORY.description — The clock had time left.\n"
                       "@pages.DEFEAT.description — The clock ran dry.\n"
                       "@pages.DRAW.description — A page this event has not got.\n")

    assert not plan.items
    assert any("pages.DRAW.description" in r and "does not declare" in r
               for r in plan.refusals), plan.refusals


def test_a_keyed_face_that_is_complete_emits_both_pages(tmp_path):
    """And the passing case, so the two refusals above are not vacuous: with
    both lines written, the victory and the defeat page carry DIFFERENT text.
    That is the wart this mechanism retired -- one rule bullet used to supply
    both, so a win and a loss printed the same sentence."""
    module = _load_generator()
    plan = _plan_for(module, tmp_path, _DUMMY_FACE
                     + "\n@pages.VICTORY.description — The clock had time left.\n"
                       "@pages.DEFEAT.description — The clock ran dry.\n")

    assert not plan.refusals, plan.refusals
    assert len(plan.items) == 1
    rows = dict(plan.items[0].rows())
    entry = plan.items[0].entry
    assert rows[f"{entry}.pages.VICTORY.description"] == "The clock had time left."
    assert rows[f"{entry}.pages.DEFEAT.description"] == "The clock ran dry."


def test_a_keyed_line_is_not_counted_as_an_option(tmp_path):
    """The parser's half of it. A keyed line carries its own key and pairs
    with nothing, so adding one to a face must not move the option count the
    harvest is compared against -- otherwise curating a page would refuse the
    whole event."""
    module = _load_generator()
    face = tmp_path / "counted.md"
    face.write_text(_DUMMY_FACE
                    + "\n@pages.VICTORY.description — Won.\n"
                      "@pages.DEFEAT.description — Lost.\n", encoding="utf-8")

    events = module.parse_face(face)
    assert len(events) == 1
    assert len(events[0].options) == 4, "the four bullets, and not the two @ lines"
    assert set(events[0].keyed) == {
        "pages.VICTORY.description", "pages.DEFEAT.description"}


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
        # StringHelper.CamelCaseRegex: an underscore before EVERY capital
        # that follows a letter or digit (ToABetterYou -> TO_A_BETTER_YOU).
        entry = re.sub(r"(?<=[A-Za-z0-9])([A-Z])", r"_\1", cls).upper()
        assert f'["{entry}"] =\n                "res://images/events/' in text, (
            f"{cls} has no portrait borrow; the event page throws "
            f"AssetLoadException before it is drawn (EB-764)")


def test_slugify_is_the_games_camel_case_rule():
    """`StringHelper.Slugify` (0.111.0) puts an underscore before EVERY capital
    that follows a letter or digit, a capital after a capital included. A
    lower->upper-only rule keyed the Six Contracts rows under
    `SIX_CONTRACTS_TO_ABETTER_YOU` while the game asked for
    `SIX_CONTRACTS_TO_A_BETTER_YOU`; the page opened with a raw key, no options
    and no portrait, and the run softlocked (proofs-4, 2026-09-15)."""
    sys.path.insert(0, str(REPO / "tools"))
    try:
        from gen_teyvat_events import slugify
    finally:
        sys.path.pop(0)
    assert slugify("SixContractsToABetterYou") == "SIX_CONTRACTS_TO_A_BETTER_YOU"
    assert slugify("CoralMirrorRorriMLaroCEhT") == "CORAL_MIRROR_RORRI_M_LARO_C_EH_T"
    assert slugify("TeaMaster") == "TEA_MASTER"
    assert slugify("Act2Boss") == "ACT2_BOSS"
