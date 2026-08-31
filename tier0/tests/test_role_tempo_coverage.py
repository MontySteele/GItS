"""The role x tempo taxonomy and its floors-only coverage gate.

Track A of the Axis-Validity session. Everything here runs on a fresh clone:
the floors are a COMMITTED percentages-only file, the tags are a COMMITTED
review file, and nothing in this module touches game_ref/ -- which is the
whole reason the floors were committed as percentages rather than recomputed
from the dll on demand.
"""

import subprocess
import sys
from pathlib import Path

import yaml

from tier0.content import loader

REPO = Path(loader.__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools import role_tempo as rt        # noqa: E402


def _run(script, *args):
    return subprocess.run(
        [sys.executable, str(REPO / "tools" / script), *args],
        capture_output=True, text=True)


# --- the gate ---------------------------------------------------------------

def test_the_coverage_gate_finds_exactly_the_pinned_debt():
    """A NEW finding is a coverage regression; a STALE pin is a cell that
    moved without anybody saying so. The gate fails on either, which is what
    makes a green suite mean something while the debt is real and unpaid."""
    res = _run("lint_role_tempo_coverage.py", "--gate")
    assert res.returncode == 0, res.stdout + res.stderr
    assert "gate ok" in res.stdout, res.stdout


def test_the_gate_says_out_loud_that_it_only_counts():
    """R90/1a. The null fired because a SIZE hypothesis was tested with a
    COUNTING tool, and the ruling's answer was to keep the tool and move the
    hypothesis. A run whose output does not say which of the two it is doing
    invites the same mistake a second time."""
    res = _run("lint_role_tempo_coverage.py", "--gate")
    assert "COUNTING TOOL" in res.stdout, res.stdout
    assert "Track B" in res.stdout, res.stdout


def test_the_debt_list_records_that_its_shrink_was_not_progress():
    """The list went 30 -> 19 with no gap fixed, because R90/1c changed the
    comparison population. A future reader diffing this file must not be able
    to read that as eleven wins."""
    text = (REPO / "docs" / "role-tempo-debt.tsv").read_text(encoding="utf-8")
    assert "30 -> 19" in text, text[:400]
    assert "NOT ONE GAP WAS FIXED" in text, text[:400]


def test_the_lint_can_never_name_a_card():
    """Charter A0.2(1): floors only. No card can EVER fail -- not for being
    unclassifiable, not for being hybrid, not for being strange. The unit of
    failure is (character, archetype, cell) and nothing smaller, so no card id
    from any sheet may appear anywhere in a full run's output."""
    res = _run("lint_role_tempo_coverage.py")
    ids = {row["id"] for path in rt.SHEETS.values()
           for row in rt.load_rows(path)}
    leaked = sorted(i for i in ids if i in res.stdout)
    assert not leaked, f"the floors-only lint named cards: {leaked}"


def test_the_review_and_tagthrough_artifacts_are_current():
    res = _run("suggest_role_tempo_tags.py", "--check")
    assert res.returncode == 0, res.stdout + res.stderr


# --- the floors -------------------------------------------------------------

def _floors() -> dict:
    return yaml.safe_load(
        (REPO / "docs" / "role-tempo-floors.yaml").read_text(encoding="utf-8"))


def _every_floor_cell(floors: dict):
    yield from floors["default"]["mandatory"].items()
    for block in floors["anchored"].values():
        yield from block["mandatory"].items()


def test_utility_support_and_sustain_are_never_linted():
    """`utility` is protected free space (A0.2(2)); `support` is graded by play
    only, because the sim is one-seat (D4); `sustain` joined them at R91/2d,
    where canon reads 0.0-2.3% under the structural definition and zero
    sustain was ruled a legal identity. None may acquire a floor by someone
    regenerating the file on a day canon happens to be non-zero everywhere."""
    floors = _floors()
    assert set(floors["never_linted"]) == {"utility", "support", "sustain"}
    assert set(rt.UNLINTED) | set(rt.NEVER_LINTED) == set(floors["never_linted"])
    for cell, _ in _every_floor_cell(floors):
        assert cell.split("|")[0] in ("frontload", "scaling", "block",
                                      "velocity"), cell


def test_every_floor_is_a_percentage_and_nothing_else_is_committed():
    """PERCENTAGES ONLY. game_ref/ is gitignored (.gitignore:28) and the
    committed deliverable is the shape, never the material."""
    for cell, value in _every_floor_cell(_floors()):
        assert isinstance(value, float), cell
        assert 0.0 < value <= 100.0, (cell, value)


def test_the_floors_come_from_packages_sized_like_our_archetypes():
    """R90/1c is a POPULATION fix and this is the number that says so. The old
    floors compared an 11-32 card archetype against an 88-card canon pool; a
    package that is itself 88 cards would have repaired nothing."""
    floors = _floors()
    sizes = [pkg["n"] for pkg in floors["packages"].values()]
    assert len(sizes) == 5, floors["packages"]
    assert max(sizes) <= 50, sizes


def test_no_anchored_floor_can_fail_the_package_it_came_from():
    """THE STANDING STOP-AND-SURFACE RULE, as an assertion: a floor that would
    fail the canon population it was derived from means the derivation is
    wrong, and the number is never the thing to adjust. An anchored floor is
    its package's own coverage, so it clears with equality and nothing else --
    which is the tightest form the rule can take."""
    from tools import canon_role_tempo as crt
    for who, block in _floors()["anchored"].items():
        pkg = block["package"]
        assert pkg in crt.PACKAGES, (who, pkg)
        for cell, floor in block["mandatory"].items():
            assert floor > 0.0, (who, cell)


def test_every_anchor_carries_a_reason():
    """ARCHETYPE_ANCHORS is a table of DESIGN CLAIMS -- "this GItS archetype is
    shaped like that canon package" -- and it moves floors. Same discipline as
    ENTITY_PAYOFFS: an entry without a reason is a claim nobody can argue
    with."""
    from tools import canon_role_tempo as crt
    for key, (pkg, why) in crt.ARCHETYPE_ANCHORS.items():
        assert pkg in crt.PACKAGES, key
        assert len(why) > 60, key
    for name, (character, markers, why) in crt.PACKAGES.items():
        assert markers, name
        assert len(why) > 60, name


# --- the Regent Stars anchor (EB-192 / R231) --------------------------------
#
# The anchor `klee/spark` and `kokomi/commander` are measured against used to
# be `regent_forge`, a regex union of Regent's Stars with the unrelated Forge
# card: ten of its nineteen members never touched a Star and no `ForgeStars`
# symbol exists in the assembly. R231 rebuilt it from Star-touching cards
# only. A curated member list is only as honest as its citation, so these
# lock it to the decompile-sourced census it claims to be -- a card the census
# does not carry cannot enter the package without failing here.

CENSUS = REPO / "docs" / "current" / "research" / "regent-stars-economy.md"
# Named in the census's reader section but not in any CARD pool: they are
# relics (census 1.3). The package is a subset of a canon card pool.
CENSUS_RELICS = {"GalacticDust", "MiniRegent"}


def _census_section(start: str, end: str) -> str:
    text = CENSUS.read_text(encoding="utf-8")
    i = text.index(start)
    return text[i:text.index(end, i)]


def _census_table_names(start: str, end: str) -> set:
    """The first column of every row whose first cell is a single card id."""
    import re
    out = set()
    for line in _census_section(start, end).splitlines():
        hit = re.match(r"^\|\s*`(\w+)`\s*\|", line)
        if hit:
            out.add(hit.group(1))
    return out


def test_the_star_generator_list_is_the_censuss_generator_table():
    from tools import canon_role_tempo as crt
    names = _census_table_names("## 2. Full generator census", "## 3. Spending")
    assert names, "the census generator table moved"
    assert set(crt.STAR_GENERATORS) == names, sorted(
        set(crt.STAR_GENERATORS) ^ names)


def test_the_star_spender_list_is_the_censuss_spender_table():
    from tools import canon_role_tempo as crt
    names = _census_table_names("### 3.5 Every spender",
                                "### 3.6 Cards that read Stars")
    assert names, "the census spender table moved"
    assert set(crt.STAR_SPENDERS) == names, sorted(
        set(crt.STAR_SPENDERS) ^ names)


def test_the_star_reader_list_is_the_censuss_reader_section():
    """The census names the two Powers by their power type, which is what the
    card applies; the card is the same name without the suffix."""
    import re
    section = _census_section("### 3.6 Cards that read Stars",
                              "## 4. Persistence")
    named = set()
    for line in section.splitlines():
        if line.startswith("- **"):
            named |= set(re.findall(r"\*\*`(\w+)`\*\*", line))
    assert named, "the census reader section moved"
    cards = {n[:-len("Power")] if n.endswith("Power") else n
             for n in named - CENSUS_RELICS}
    from tools import canon_role_tempo as crt
    assert set(crt.STAR_READERS) == cards, sorted(set(crt.STAR_READERS) ^ cards)


def test_the_package_is_exactly_the_three_census_lists():
    from tools import canon_role_tempo as crt
    assert crt.REGENT_STARS == crt.Curated(
        crt.STAR_GENERATORS + crt.STAR_SPENDERS + crt.STAR_READERS)
    character, selector, _why = crt.PACKAGES["regent_stars"]
    assert character == "Regent"
    assert selector is crt.REGENT_STARS


def test_a_curated_package_ignores_the_body_markers_entirely():
    """The failure EB-192 records was membership by REGEX. A Forge card whose
    body names every retired marker is still not a Stars card, and a Stars
    spender's body names none of them -- a Star price is a cost FIELD, which
    is why this package cannot be drawn structurally at all."""
    from tools import canon_role_tempo as crt
    pool = [{"name": "BeatIntoShape", "mentions": ["ForgeStars", "Stars"]},
            {"name": "FallingStar", "mentions": []}]
    members = crt.package_members(pool, crt.REGENT_STARS)
    assert [c["name"] for c in members] == ["FallingStar"]


def test_the_invented_forge_stars_marker_is_gone_for_good():
    """No `ForgeStars` type, method, field or loc key exists in the 0.111.0
    assembly (census 0). A marker naming one cannot come back."""
    from tools import canon_role_tempo as crt
    assert "regent_forge" not in crt.PACKAGES, sorted(crt.PACKAGES)
    marker_names = {name for _pattern, name in crt.MECHANIC_MARKERS}
    assert "ForgeStars" not in marker_names, marker_names
    for _character, selector, _why in crt.PACKAGES.values():
        if isinstance(selector, crt.Curated):
            continue
        assert "ForgeStars" not in selector, selector


# --- the vocabulary ---------------------------------------------------------

def test_the_vocabulary_is_the_charters_amended_one():
    """A0: `support` joins, `aoe` leaves for the modifier list."""
    assert "support" in rt.SOLVE
    assert "aoe" not in rt.SOLVE
    assert "aoe" in rt.MODIFIERS


def test_every_sheet_declares_its_archetypes_and_the_header_wrap_is_read():
    """R66 makes the sheet HEADER canonical for the archetype vocabulary, and
    two of the three headers wrap mid-parenthetical. A naive single-line read
    silently dropped `generic` from Kokomi's list -- i.e. deleted an identity
    from the floors without failing anything."""
    for name, path in rt.SHEETS.items():
        declared = rt.declared_archetypes(path)
        assert len(declared) >= 3, (name, declared)
        assert "generic" in declared, (name, declared)


def test_every_card_lands_in_at_least_one_band_on_both_scales():
    """A card with no band is invisible to every cell, which would let a pool
    pass by having cards the taxonomy cannot place."""
    for name, path in rt.SHEETS.items():
        rows = rt.load_rows(path)
        scans, _ = rt.classify_pool(rows, name)
        for row in rows:
            scan = scans[row["id"]]
            assert scan["fight"], (name, row["id"])
            assert scan["run"], (name, row["id"])


# --- the landed schema (R92/3b) ---------------------------------------------

def test_tempo_band_landed_on_every_row_of_every_sheet():
    """A-G1 closed and the tags landed. A partial landing is worse than none:
    the lint would then be reading a mix of derived and authored bands and no
    cell result would mean anything."""
    for name, path in rt.SHEETS.items():
        rows = rt.load_rows(path)
        assert rows, name
        for row in rows:
            band = row.get("tempo_band")
            assert isinstance(band, dict), (name, row["id"])
            assert set(band) == {"fight", "run"}, (name, row["id"])
            assert set(band["fight"]) <= set(rt.FIGHT_BANDS), row["id"]
            assert set(band["run"]) <= set(rt.RUN_BANDS), row["id"]
            assert band["fight"] and band["run"], (name, row["id"])


def test_the_sim_loader_reads_tempo_band():
    """READER ONE. `Card.from_dict` refuses unknown fields by design, so the
    field being DECLARED is what keeps 219 rows loadable. This test is half of
    what the cross-session note promised."""
    card = loader._card_index()["soloists_solicitation"]
    assert card.tempo_band == {"fight": ["early"], "run": ["early"]}


def test_tempo_band_survives_the_hand_rolled_deepcopy():
    """Card.__deepcopy__ copies exactly `_MUTABLE_FIELDS` and SHARES the rest.
    A new container field left off that list is aliased across every copy of
    the card -- silent, and exactly the class of bug the hand-rolled copy
    exists to be fast enough to justify."""
    import copy
    from tier0.engine import state
    assert "tempo_band" in state._MUTABLE_FIELDS
    card = loader._card_index()["soloists_solicitation"]
    clone = copy.deepcopy(card)
    assert clone.tempo_band == card.tempo_band
    assert clone.tempo_band is not card.tempo_band


def test_the_csharp_codegen_whitelists_tempo_band():
    """READER TWO, the other half of the note. `card_level_reason` BLOCKS any
    card carrying a field the emitter does not understand -- the gate that
    already caught `innate` and `retain` -- so an unlisted field would have
    blocked all 219 cards rather than one."""
    from tools import gen_klee_cards
    assert "tempo_band" in gen_klee_cards.CARD_FIELDS
    row = {"id": "x", "name": "X", "cost": 1, "type": "attack",
           "rarity": "common", "solve": ["frontload"],
           "tempo_band": {"fight": ["early"], "run": ["early"]},
           "archetypes": ["generic"], "role": "glue",
           "effects": [{"op": "damage", "amount": 6, "target": "enemy"}]}
    assert gen_klee_cards.card_level_reason(row) is None


# --- the A-G1 rulings, as rules (R91) ---------------------------------------

def test_every_meter_declares_bounded_or_unbounded_with_its_cap_from_constants():
    """R91/2b. The amendment's whole point is that a BOUNDED meter's readers
    may be frontload-after-a-tax rather than scaling, so the property has to
    be present and the cap has to be the real one. A cap retyped into this
    file would drift from the sim the first time the sim moved."""
    from tier0 import constants as C
    for token, (bounded, const, why) in rt.METERS.items():
        assert isinstance(bounded, bool), token
        assert len(why) > 40, token
        got_bounded, value, got_const = rt.meter_cap(token)
        assert got_bounded is bounded, token
        if const is None:
            assert value is None, token          # unbounded: no cap to read
        else:
            assert got_const == const
            assert value == getattr(C, const), token
    assert rt.METERS["salon_member"][1] == "SALON_MEMBER_SLOTS"
    assert C.SALON_MEMBER_SLOTS == 3


def test_meter_reading_damage_is_scaling_and_frontload_only_if_it_pays_at_zero():
    """R91/2c, COUNTERSIGNED AS WRITTEN, on the sheets' own cards — read
    through the PRINTED FLOOR (L4q / R129, 2026-08-07).

    `applause_line` deals a printed number and adds a Fanfare term, so it is
    both. `pearl_barrage` prints `5 + 1 per exhausted card`: the v0.3 base
    raise (3 -> 5, "the floor must be playable before the pile exists") gave
    it a floor AFTER this test's original sentence was written, so the old
    premise -- "deals nothing at an empty pile" -- had gone stale against the
    shipped sheet. R129 adopts `effect_walk.printed_floor`: `amount: 5` and
    `amount_formula: {base: 5, ...}` are the same promise to the player, so
    the kokomi pile-readers that print a base are both. What stays
    scaling-ONLY is a line with no printed floor at all: `the_final_verdict`.

    TWO ROWS MOVED AT R208 / W2b (2026-08-25), in opposite directions, and
    both moves are the rule working rather than an exception to it.
    `depths_judgment` LEAVES this list: its ratified body prints a flat 14 and
    buys Block over an exhaust bar, so it reads no meter on a damage line at
    all and the classifier lands it `block, frontload`. `dramatic_entrance`
    JOINS it, and it is the first row here to arrive by the GATE form rather
    than the formula form -- `damage 7`, then `damage 7 to all` behind
    `fanfare_at_least_12`. A gate on a damage line IS a meter read, so the
    rule makes it `scaling`, and the always-live 7 is the printed floor that
    makes it `frontload` as well.
    """
    both = {"furina": ["applause_line", "dramatic_entrance"],
            "kokomi": ["read_the_current", "pearl_barrage", "undertow"]}
    scaling_only = {"furina": ["the_final_verdict"]}
    for character, path in rt.SHEETS.items():
        rows = rt.load_rows(path)
        scans, _ = rt.classify_pool(rows, character)
        for card_id in both.get(character, ()):
            solve = scans[card_id]["solve"]
            assert "scaling" in solve and "frontload" in solve, (card_id, solve)
        for card_id in scaling_only.get(character, ()):
            solve = scans[card_id]["solve"]
            assert "scaling" in solve, (card_id, solve)
            assert "frontload" not in solve, (card_id, solve)


def test_the_sheets_and_the_classifier_cannot_drift():
    """The landed tags are machine-derived, so a hand edit on a sheet is a
    silent fork between what the sheet says and what the lint counts. --check
    is the gate; this is the suite carrying it."""
    res = _run("suggest_role_tempo_tags.py", "--check")
    assert res.returncode == 0, res.stdout + res.stderr
    assert "three sheets match the classifier" in res.stdout, res.stdout


def test_tag_through_entities_all_carry_their_provenance():
    """ENTITY_PAYOFFS is the hand-authored half of A0.1 and the artifact A-G1
    reviews. An entry without a reason is a design claim nobody can argue
    with, which is the one thing it must never be."""
    for token, (roles, bands, why) in rt.ENTITY_PAYOFFS.items():
        assert roles, token
        assert set(roles) <= set(rt.SOLVE), token
        assert set(bands) <= set(rt.FIGHT_BANDS), token
        assert len(why) > 60, token
    for power, (token, roles, why) in rt.TOKEN_PAYOFF_POWERS.items():
        assert set(roles) <= set(rt.SOLVE), power
        assert len(why) > 60, power
