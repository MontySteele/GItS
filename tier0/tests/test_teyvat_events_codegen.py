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
     refused too. A keyed line is never counted as an option;
  6. THE PLACEHOLDER RULE (EB-770): no dressed row hands the player a
     bracketed gloss where the base row spells a runtime value with a var.
     `[Specific card]` is not words a player reads -- the engine's rich-text
     parser deletes it -- and the exemption list for that is EMPTY. The vars
     the rows are read against live in the index's `key_vars`, so this arm
     needs neither the game nor a decompile;
  7. every `Loss:` line a face writes reaches the table. Thirty-nine lines
     against thirty-eight rows was the Liyue Tea Master's line being dropped
     for a base event that cannot kill; the generator now refuses it instead.
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


#: The only lowercase words an `is_allowed` note may contain: C# keywords the
#: fold leaves standing, the `it` it writes for a lambda's subject, the `m` of
#: a decimal literal, the `player` of a `foreach` it could not fold, and the
#: four words of the note for an event with no gate at all.
_NOTE_WORDS = {"if", "return", "foreach", "in", "is", "true", "false", "null",
               "it", "m", "player", "default", "no", "gate"}


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

        # EB-770. `is_allowed` is the event's own gate, folded to one boolean
        # expression by `--refresh-allowed`. It is the one value in the index
        # that is not a single token, so it is checked WORD BY WORD: every
        # word is either a base-game member name (a capitalised identifier) or
        # one of the handful of C# words the fold leaves behind. A base-game
        # sentence -- an event description, a comment out of a method body --
        # could not get through that, which is the rule this arm is here for.
        note = row["is_allowed"]
        assert isinstance(note, str), name
        assert isinstance(row["is_allowed_override"], bool), name
        assert re.fullmatch(r"[A-Za-z0-9_ ().,;:!&|<>=*+\-\"'\[\]{}/%]+",
                            note), f"{name}: {note}"
        for word in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", note):
            assert word in _NOTE_WORDS or word[0].isupper(), \
                f"{name}: {word!r} in is_allowed"


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


# ---------------------------------------------------------------------------
# The placeholder rule, and the `Loss:` line that never reached the table.
# ---------------------------------------------------------------------------


#: Dressed rows allowed to hand the player a bracket group the engine deletes.
#: IT IS EMPTY, AND IT IS MEANT TO STAY EMPTY -- a gloss is not prose the
#: player ever reads, it is prose the parser throws away. If a face genuinely
#: needs square brackets on screen, the fix is the game's own escape, not a row
#: on this list.
GLOSS_EXEMPTIONS: frozenset = frozenset()


def _real_plan():
    module = _load_generator()
    return module, module.build_plan()


def test_no_dressed_row_hands_the_player_a_bracket_gloss():
    """EB-770, pinned at the row.

    The Liyue Slippery Bridge's first option was written `[Specific card] is
    removed from your deck.` The engine's rich-text parser read `[...]` as a
    tag, found no tag called `Specific card`, deleted the group, and the
    option printed ` is removed from your deck.` with a hole where the card
    name belonged (proofs-4, 2026-09-15). Every dressed row is checked, not
    just that one, and the exemption list above is empty.
    """
    module, plan = _real_plan()
    offenders = []
    for item in plan.items:
        for key, text in item.rows():
            for gloss in module.unrendered_glosses(text):
                if (item.cls, key) in GLOSS_EXEMPTIONS:
                    continue
                offenders.append(f"{item.face.key} {key}: [{gloss}]")
    assert not offenders, "\n".join(offenders)
    assert not GLOSS_EXEMPTIONS, "the exemption list is meant to stay empty"


def test_the_card_the_bridge_takes_is_named_by_its_var_on_every_face():
    """The positive half of EB-770: the option that names a card carries the
    var that names it.

    Read off the index's `key_vars` rather than spelled here, so the pin
    follows the base game: if 0.111.x renames `RandomCard`, `--refresh-vars`
    moves the expectation and this arm moves with it.
    """
    module, plan = _real_plan()
    index = module.load_index()
    bridges = [i for i in plan.items if i.base_class == "SlipperyBridge"]
    assert len(bridges) == 6, "one Slippery Bridge dressing per face"

    for item in bridges:
        rows = dict(item.rows())
        # The OUTCOME page is not pinned: the base game's own
        # `pages.OVERCOME.description` carries no var, so there is nothing
        # there for a dressing to owe.
        suffix = "pages.INITIAL.options.OVERCOME.description"
        wanted = module.base_vars(index["SlipperyBridge"], suffix)
        assert wanted, f"the base row for {suffix} should carry a var"
        text = rows[f"{item.entry}.{suffix}"]
        for var in wanted:
            assert "{" + var + "}" in text, (
                f"{item.cls}.{suffix} does not name the card: {text!r}")


def test_every_var_a_dressed_row_uses_is_one_the_base_event_declares():
    """A var the base event does not declare is not substituted; it reaches
    the player as literal braces. `DynamicVars` belongs to the EventModel, so
    the comparison is against every var the base event uses ANYWHERE, plus the
    run-history formatter's `{character}` and `{event}`."""
    module, plan = _real_plan()
    index = module.load_index()
    offenders = []
    for item in plan.items:
        allowed = module.event_vars(index[item.base_class])
        for key, text in item.rows():
            for used in module._VAR_RE.findall(text):
                if used not in allowed:
                    offenders.append(f"{item.face.key} {key}: {{{used}}}")
    assert not offenders, "\n".join(offenders)


def test_the_index_key_vars_map_is_identifiers_only():
    """`key_vars` comes out of the game's own loc file, so it is held to the
    same rule as the rest of the index: key suffixes and var names, never a
    base-game sentence."""
    events = json.loads(INDEX.read_text(encoding="utf-8"))["events"]
    assert any(row.get("key_vars") for row in events.values()), \
        "no event carries a var map; run --refresh-vars"
    for name, row in events.items():
        for suffix, names in row.get("key_vars", {}).items():
            assert re.fullmatch(r"[A-Za-z0-9_.]+", suffix), f"{name}: {suffix}"
            assert names, f"{name}: {suffix} has an empty var list"
            for var in names:
                assert re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", var), \
                    f"{name}: {suffix}: {var}"


def test_a_loss_line_on_a_base_that_cannot_kill_is_refused(tmp_path):
    """The 39th `Loss:` line.

    Six faces carried 39 `Loss:` lines and the generated table held 38 death
    rows. The missing one was the Liyue Tea Master's: `Dressed.rows` writes
    the `.loss` row only when the base event `can_kill`, and Tea Master has no
    lethal option, so the face's line was silently dropped. Silently is the
    defect -- prose nobody will ever read, with nothing saying so.
    """
    module = _load_generator()
    assert module.load_index()["TeaMaster"]["can_kill"] is False, \
        "the premise: Tea Master has no lethal option"

    plan = _plan_for(module, tmp_path,
                     "## - [ ] Tea Master\n\n"
                     "### The Test Tea House — Fontaine / Test — DRAFTED\n\n"
                     "A kettle.\n\n"
                     "- **First Cup** — Pay 50 Gold. Something.\n"
                     "- **Second Cup** — Pay 150 Gold. Something else.\n"
                     "- **Third Cup** — A free cup.\n\n"
                     "Loss: {character} died at the [gold]{event}[/gold].\n")

    assert not plan.items, "nothing may be emitted for a refused event"
    assert any("`Loss:` line" in r and "can kill" in r for r in plan.refusals), \
        plan.refusals


def test_every_face_loss_line_reaches_the_generated_table():
    """The count that caught it, kept as a gate: a `Loss:` line in a face and
    a `.loss` row in the table are now one to one."""
    module, plan = _real_plan()
    lines = sum(
        1 for face in module.FACES if face.active
        for line in (module.FACE_DIR / face.file).read_text(
            encoding="utf-8").splitlines()
        if line.startswith("Loss:"))
    rows = sum(1 for item in plan.items
               for key, _ in item.rows() if key.endswith(".loss"))
    assert lines == rows, f"{lines} face Loss: line(s), {rows} row(s) emitted"
    assert GENERATED_CS.read_text(encoding="utf-8").count('.loss"] =') == rows


# ----------------------------------- EB-770: the IsAllowed fold -----------
#
# `--refresh-allowed` needs a decompile and CI has none, so the FOLD is pinned
# here against source it is handed directly. These are the shapes 0.111.0
# actually writes, one arm each, plus the fallback for the two events that
# iterate their players.


def _generator():
    import importlib.util
    spec = importlib.util.spec_from_file_location("gen_teyvat_events",
                                                  str(GENERATOR))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_a_guard_clause_is_folded_into_what_the_gate_WANTS():
    """`if (X) return false;` says what refuses the event. The note has to say
    the opposite -- what lets it in -- or every reader does the flip by hand
    and the round after this one flips one wrong."""
    gen = _generator()
    src = """
    public override bool IsAllowed(IRunState runState)
    {
        if (runState.CurrentActIndex == 0)
        {
            return false;
        }
        return runState.Players.All((Player p) => p.Gold >= 100);
    }
    """
    note, override = gen.allowed_note(src)
    assert override is True
    assert note == "CurrentActIndex != 0 && Players.All(Gold >= 100)"


def test_an_any_guard_becomes_an_all_and_not_a_double_negative():
    """`Players.Any(p => !p.Potions.Any())` refuses the event, so the gate
    wants `Players.All(Potions.Any())`. Printing `!(Players.Any(!...))` would
    be true and unreadable, which is the same as unhelpful."""
    gen = _generator()
    src = """
    public override bool IsAllowed(IRunState runState)
    {
        if (runState.Players.Any((Player p) => !p.Potions.Any()))
        {
            return false;
        }
        return true;
    }
    """
    assert gen.allowed_note(src)[0] == "Players.All(Potions.Any())"


def test_a_conditional_return_is_folded_to_one_and():
    gen = _generator()
    src = """
    public override bool IsAllowed(IRunState runState)
    {
        if (runState.TotalFloor > 6)
        {
            return runState.Players.All((Player p) =>
                p.Deck.Cards.Any((CardModel c) => c.IsRemovable));
        }
        return false;
    }
    """
    assert gen.allowed_note(src)[0] == (
        "TotalFloor > 6 && Players.All(Deck.Cards.Any(IsRemovable))")


def test_a_one_expression_private_helper_is_inlined():
    """`GetValidRelics(it)` names nothing a caller can act on. The clause it
    hides -- the relics that are tradable -- is the whole fact."""
    gen = _generator()
    src = """
    public override bool IsAllowed(IRunState runState)
    {
        return runState.Players.All((Player p) => GetValidRelics(p).Count() >= 5);
    }

    private IEnumerable<RelicModel> GetValidRelics(Player player)
    {
        return player.Relics.Where((RelicModel r) => r.IsTradable);
    }
    """
    assert gen.allowed_note(src)[0] == (
        "Players.All(Relics.Where(IsTradable).Count() >= 5)")


def test_a_shape_the_fold_does_not_know_degrades_to_the_source_not_a_guess():
    """Two events walk their players in a `foreach`. A note that is longer is
    still readable; a note that guessed at a shape would be wrong quietly,
    which is the one outcome this table cannot afford."""
    gen = _generator()
    src = """
    public override bool IsAllowed(IRunState runState)
    {
        if (runState.Players.Count == 1)
        {
            return true;
        }
        foreach (Player player in runState.Players)
        {
            if (player.Creature.CurrentHp <= 5)
            {
                return false;
            }
        }
        return true;
    }
    """
    note, override = gen.allowed_note(src)
    assert override is True
    assert note.startswith("if (Players.Count == 1)")
    assert "foreach" in note


def test_an_event_with_no_override_is_marked_as_having_no_gate():
    gen = _generator()
    note, override = gen.allowed_note("public sealed class X : EventModel { }")
    assert override is False
    assert note == gen.ALWAYS_ALLOWED


def test_every_dressed_base_event_in_the_index_carries_a_gate_note():
    """The same claim `tier0/tests/test_understudy_force_event.py` makes from
    the harness side, made here against the generator's own substitution
    table: a dressing whose base event has no note would put the next proofs
    round back on a refusal with nothing in it."""
    events = json.loads(INDEX.read_text(encoding="utf-8"))["events"]
    by_entry = {row["entry"]: row for row in events.values()}
    source = GENERATED_CS.read_text(encoding="utf-8")
    bases = set(re.findall(r"typeof\((\w+)\)", source))
    assert bases, "no substitution rows in the generated file"
    for base in sorted(bases):
        row = events.get(base) or by_entry.get(base)
        assert row is not None, f"{base} is not in the index"
        assert row["is_allowed"], f"{base} has no is_allowed note"
