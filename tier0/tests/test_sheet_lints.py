"""Cross-sheet lint gates (tools/lint_strict_domination.py).

This module holds the lints that sweep every docs card sheet at once.

G1 (Serenitea Sweep, 2026-07-26) moved the comment/number lint here from
`test_furina_sheet`, where it gated ONE sheet of six. Audit sec.3.8: run
against the other five it reported 35 findings -- "real drift the gate's
scope hid". On inspection it is 34 comments legitimately citing numbers
that are not the row's (sibling cards, superseded values, measurement
brackets, worked arithmetic, engine constants, and two SHEET LINE NUMBERS)
plus exactly ONE real drift. Furina's sheet is clean precisely because it
already carries the `(lint-ok: reason)` markers the convention provides;
the other five had never been through the pass.
"""

import subprocess
import sys
from pathlib import Path

from tier0.content import loader

REPO = Path(loader.__file__).resolve().parents[2]


sys.path.insert(0, str(REPO / "tools"))
import lint_strict_domination as dom     # noqa: E402
import lint_handwritten_parity as hwp    # noqa: E402


def _sheet_paths():
    return [loader.DOCS_DIR / s for s in loader.DOCS_CARD_SHEETS]


def test_no_strict_domination_on_docs_sheets():
    sheets = [str(p) for p in _sheet_paths()]
    res = subprocess.run(
        [sys.executable, str(REPO / "tools" / "lint_strict_domination.py"),
         *sheets],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
    # The gate must be running the CROSS-SHEET pass, not only the within-sheet
    # one. Before 2026-07-29 the whole comparison was per-file, so a dominating
    # pair split across two sheets was structurally invisible -- and the one
    # that existed (Clorinde/Raiden) was caught by a human reading the set.
    assert "CROSS-SHEET" in res.stdout, res.stdout
    assert "NOT RUN" not in res.stdout, res.stdout


# --- the reporting defect: CLEAN with no denominator ----------------------

def test_the_summary_states_its_scope_not_just_a_verdict():
    """`CLEAN: <sheet names>` claimed the sheets were clean when it meant
    "the rows I compared had no findings" -- and it dropped basics, rows with
    no `effects`, non-draftable rows and formula amounts before comparing.
    A verdict without a denominator is the confident half of a partial check.
    """
    res = subprocess.run(
        [sys.executable, str(REPO / "tools" / "lint_strict_domination.py")],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
    assert "scope (rows this sweep has NO opinion about" in res.stdout
    assert "compared card(s) in" in res.stdout
    # Every sheet must own a scope line with a real denominator.
    for p in _sheet_paths():
        line = [ln for ln in res.stdout.splitlines() if p.name in ln
                and "compared" in ln]
        assert line, f"{p.name} has no scope line: {res.stdout}"
        assert "/0 " not in line[0], line[0]


def test_a_run_that_compares_nothing_refuses_to_print_clean(tmp_path):
    """The dead-gate direction. A sheet of nothing but basics used to produce
    the identical `CLEAN` line as a full sweep."""
    empty = tmp_path / "basics-only.yaml"
    empty.write_text(
        '- {id: probe_strike, name: "Probe Strike", cost: 1, type: attack,\n'
        '   rarity: basic, effects: [{op: damage, amount: 6, target: enemy}]}\n',
        encoding="utf-8")
    res = subprocess.run(
        [sys.executable, str(REPO / "tools" / "lint_strict_domination.py"),
         str(empty)], capture_output=True, text=True)
    assert res.returncode == 1, res.stdout
    assert "VACUOUS" in res.stdout
    assert "CLEAN" not in res.stdout


def test_within_only_says_the_cross_pass_did_not_run():
    """A narrower run is fine; a narrower run that reads like a full one is
    not. `--within-only` must name what it left unchecked."""
    res = subprocess.run(
        [sys.executable, str(REPO / "tools" / "lint_strict_domination.py"),
         "--within-only"], capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
    assert "NOT RUN (--within-only)" in res.stdout
    assert "WITHIN-SHEET ONLY" in res.stdout


# --- the cross-sheet sweep, both directions -------------------------------

def test_the_cross_sheet_sweep_catches_the_clorinde_raiden_shape(tmp_path):
    """THE RED DEMONSTRATION, rebuilt from the case that needed a human.

    docs/archive/fontaine-rares-banner-sprint-log.md item 2: a Clorinde (Fontaine) /
    Raiden (Inazuma) dominating pair "was flagged BY HAND because no lint could
    see it". Two companion sheets, one shared reward pool, and a per-file lint.
    The pair was resolved by buffing Raiden, so the live sheets no longer carry
    it -- which is exactly why the demonstration is synthetic: the fix must be
    provable without re-introducing the defect into shipped content.
    """
    a = tmp_path / "alpha-companions.yaml"
    b = tmp_path / "beta-companions.yaml"
    a.write_text(
        '- {id: probe_big, name: "Probe Big", rarity: uncommon, cost: 2,\n'
        '   type: attack, effects: [{op: damage, amount: 20, target: enemy}]}\n',
        encoding="utf-8")
    b.write_text(
        '- {id: probe_small, name: "Probe Small", rarity: common, cost: 2,\n'
        '   type: attack, effects: [{op: damage, amount: 18, target: enemy}]}\n',
        encoding="utf-8")

    lint = str(REPO / "tools" / "lint_strict_domination.py")
    # WITHIN-SHEET: each file holds one card, so the old scope sees nothing.
    within = subprocess.run([sys.executable, lint, "--within-only",
                             str(a), str(b)], capture_output=True, text=True)
    assert within.returncode == 0, within.stdout
    assert "probe_big" not in within.stdout, (
        "the within-sheet sweep cannot see a cross-sheet pair; if it does, "
        "this test is no longer demonstrating the gap")

    # CROSS-SHEET: the same two files, one finding.
    across = subprocess.run([sys.executable, lint, str(a), str(b)],
                            capture_output=True, text=True)
    assert across.returncode == 1, across.stdout
    assert "CROSS-SHEET" in across.stdout
    assert "probe_big" in across.stdout and "probe_small" in across.stdout


def test_two_personal_sheets_are_not_compared_across(tmp_path):
    """The comparability rule the cross pass adds, in the negative.

    Klee's cards and Kokomi's never appear in one run (`rewards.character_pool`
    requires `c.character == character_id`), so a domination between them is
    not a draft decision. Flagging it would be noise, and noise is how a gate
    gets switched off.
    """
    a = tmp_path / "alpha-cards.yaml"
    b = tmp_path / "beta-cards.yaml"
    a.write_text(
        '- {id: probe_big, name: "Probe Big", rarity: uncommon, cost: 2,\n'
        '   type: attack, effects: [{op: damage, amount: 20, target: enemy}]}\n',
        encoding="utf-8")
    b.write_text(
        '- {id: probe_small, name: "Probe Small", rarity: common, cost: 2,\n'
        '   type: attack, effects: [{op: damage, amount: 18, target: enemy}]}\n',
        encoding="utf-8")
    res = subprocess.run(
        [sys.executable, str(REPO / "tools" / "lint_strict_domination.py"),
         str(a), str(b)], capture_output=True, text=True)
    assert res.returncode == 0, res.stdout
    assert "probe_big" not in res.stdout
    # ...and the pair-count says so, rather than leaving it to be inferred.
    assert "0 co-draftable sheet pair(s)" in res.stdout


def test_co_draftable_matches_the_pool_assembly():
    assert dom.co_draftable("fontaine-companions.yaml",
                            "inazuma-companions.yaml")
    assert dom.co_draftable("klee-cards.yaml", "mondstadt-companions.yaml")
    assert dom.co_draftable("mondstadt-companions.yaml", "klee-cards.yaml")
    assert not dom.co_draftable("klee-cards.yaml", "kokomi-cards.yaml")


def test_the_cross_sheet_allowlist_is_not_stale():
    """CROSS_KNOWN is DEBT, exactly like test_distinctness_gate.KNOWN_FAILING.

    The cross pass surfaced seven pre-existing pairs the day it was switched
    on. Editing a printed card needs red-pen, so they print as notes and CI
    stays green -- but an entry that outlives its pair becomes cover for the
    next real cross-sheet domination on those ids. When one is errata'd, this
    fails and the entry has to come out.
    """
    live = set()
    for note in _cross_notes():
        live.add(note)
    stale = sorted(sorted(pair) for pair in dom.CROSS_KNOWN
                   if not any(all(i in msg for i in pair) for msg in live))
    assert not stale, (
        "these CROSS_KNOWN pairs no longer dominate -- the errata landed, so "
        f"DELETE them from the set: {stale}")


def test_the_cross_sheet_allowlist_is_not_a_blanket():
    """Each entry names two real card ids, so the set cannot be widened by a
    wildcard or by an id that no longer exists."""
    ids = {c["id"] for p in _sheet_paths() for c in dom.sheet_cards(p)[0]}
    for pair in dom.CROSS_KNOWN:
        assert len(pair) == 2, pair
        missing = sorted(i for i in pair if i not in ids)
        assert not missing, (
            f"CROSS_KNOWN names {missing}, which is not a comparable card on "
            "any sheet -- the entry is guarding nothing")


def _cross_notes():
    """Every cross-sheet domination message, with the allowlist LIFTED."""
    saved = dom.CROSS_KNOWN
    try:
        dom.CROSS_KNOWN = set()
        findings, notes, _ = dom.lint_cross_sheet(_sheet_paths())
    finally:
        dom.CROSS_KNOWN = saved
    return findings + notes


def test_sheet_comments_match_numbers_on_every_sheet():
    """G1: fanned from one sheet to all six.

    Per-line `(lint-ok: <reason>)` markers rather than a blanket suppression:
    a sheet-wide exemption would switch off the drift class this lint exists
    for, and the reasons are what let a reviewer tell "cites a sibling card"
    from "cites a number this row no longer has".
    """
    sheets = [str(loader.DOCS_DIR / s) for s in loader.DOCS_CARD_SHEETS]
    assert len(sheets) >= 6, sheets
    res = subprocess.run(
        [sys.executable, str(REPO / "tools" / "lint_sheet_comments.py"),
         *sheets],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr


def test_the_comment_lint_still_catches_real_drift(tmp_path):
    """The negative half. A gate fanned out and never seen failing is a gate
    whose new scope nobody has tested."""
    sheet = tmp_path / "drift.yaml"
    sheet.write_text(
        '- {id: probe, name: "Probe", cost: 1, type: attack, rarity: common,\n'
        '   effects: [{op: damage, amount: 10, target: enemy}]}\n'
        '   # The ceiling: 8 damage, single target.\n',
        encoding="utf-8")
    res = subprocess.run(
        [sys.executable, str(REPO / "tools" / "lint_sheet_comments.py"),
         str(sheet)],
        capture_output=True, text=True)
    assert res.returncode == 1, res.stdout
    assert "comment cites 8" in res.stdout


# --- L4 / L7 (S1 parity sweep) --------------------------------------------

def test_no_scanner_reads_effects_as_a_flat_list():
    """L4. Three tools had each written the same `for eff in card["effects"]`
    loop and each was silently answering about the TOP LEVEL only:
    sparkly_explosion's branch-nested Bombs, pearl_barrage's
    `amount_formula.base`, and rider_tip_args' missing charge formula.

    Wired into pytest rather than into the CI lints job on purpose: this is
    not a softlock class, it is a "the tool is answering a narrower question
    than it appears to" class, and the moment to learn that is while writing
    the loop -- which is a pytest run.
    """
    res = subprocess.run(
        [sys.executable, str(REPO / "tools" / "lint_effect_branch_scans.py")],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
    # The dead-gate direction: a run that walked no sheets and found no scan
    # sites prints the same CLEAN line as a full one.
    assert "card row(s) read" in res.stdout
    assert " 0 card row(s) read" not in res.stdout
    assert "registered flat scan site(s)" in res.stdout


def test_the_branch_scan_lint_sees_a_new_flat_loop():
    """The red half, on the SOURCE side. Written against a synthetic module
    dropped into the scanned directory rather than by breaking a real one:
    the gate has to fail for a loop it has never seen, which is the only case
    that matters."""
    sys.path.insert(0, str(REPO / "tools"))
    import lint_effect_branch_scans as l4

    probe = REPO / "tools" / "_probe_flat_scan_delete_me.py"
    probe.write_text(
        "def count_damage(card):\n"
        "    return sum(1 for e in card['effects'] if e['op'] == 'damage')\n",
        encoding="utf-8")
    try:
        findings, _ = l4.source_findings()
    finally:
        probe.unlink()
    assert any("_probe_flat_scan_delete_me.py::count_damage" in f
               and "FLAT EFFECT SCAN" in f for f in findings), findings
    # ...and green again once it is gone.
    assert l4.source_findings()[0] == []


def test_the_branch_scan_lint_sees_a_newly_hidden_keyword_op(tmp_path):
    """The red half, on the DATA side -- synthetic, like the source half.

    It used to assert against the live `sparkly_explosion` row, which was the
    L4 incident's own card. L4a fixed that card's readers (both Bomb scans
    walk the tree now, so the Bomb ops left RULES_BEARING_OPS) and the
    assertion went with it -- which is the lesson: a red-half test anchored to
    one shipped row stops testing the gate the moment that row is fixed. A
    synthetic sheet keeps the gate under test with no live case at all, which
    is the state the pool is now in."""
    sys.path.insert(0, str(REPO / "tools"))
    import lint_effect_branch_scans as l4

    sheet = tmp_path / "probe-cards.yaml"
    sheet.write_text(
        '- {id: probe, name: "Probe", cost: 1, type: attack, rarity: common,\n'
        '   effects: [{op: damage, amount: 10, target: enemy},\n'
        '             {op: conditional, if: killed_target,\n'
        '              then: [{op: apply_aura, element: pyro,\n'
        '                      target: enemy}]}]}\n',
        encoding="utf-8")
    saved_docs, saved_sheets = l4.DOCS, l4.SHEETS
    try:
        l4.DOCS, l4.SHEETS = tmp_path, (sheet.name,)
        findings, census = l4.data_findings()
    finally:
        l4.DOCS, l4.SHEETS = saved_docs, saved_sheets
    assert census["rules_bearing"] == 1, census
    assert any("probe" in f and "BRANCH-HIDDEN RULES" in f
               for f in findings), findings


def test_upgrade_comment_arithmetic_still_adds_up():
    """L7 (SYS-11a/b). `# 6->9` on an upgrade row is arithmetic, which is the
    worst thing a stale comment can be: a reader checks it, the numbers add
    up, and what they actually verified is that the OLD base and the OLD
    result still differ by the delta. surging_shoal's had been wrong through
    two repricings.
    """
    res = subprocess.run(
        [sys.executable,
         str(REPO / "tools" / "lint_upgrade_comment_arithmetic.py")],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
    # Denominator, not just a verdict -- most rows carry no `a -> b` at all,
    # and a run that recomputed nothing must not read like a full sweep.
    assert "pair(s) recomputed" in res.stdout
    assert "(0 pair(s) recomputed)" not in res.stdout
    for sheet in ("klee-upgrades.yaml", "furina-upgrades.yaml",
                  "kokomi-upgrades.yaml", "ref-ironclad-upgrades.yaml"):
        assert f"scope {sheet}:" in res.stdout, res.stdout


def test_the_upgrade_arithmetic_lint_catches_both_drift_shapes(tmp_path):
    """The red half, and it must be red for BOTH checks separately.

    A delta that moved (arithmetic disagrees) and a base that moved (the
    arithmetic still adds up and describes a card that no longer exists) are
    different bugs. SYS-11a was entirely the second kind, so a lint with only
    the first check would have reported those six rows clean.
    """
    lint = str(REPO / "tools" / "lint_upgrade_comment_arithmetic.py")
    sheet = tmp_path / "probe-upgrades.yaml"

    # Against the REAL `strike` row (base 6): the point of the base check is
    # that it reads the card, so a synthetic card the lint cannot index would
    # test the wrong half.
    def run(text):
        sheet.write_text(text, encoding="utf-8")
        return subprocess.run([sys.executable, lint, str(sheet)],
                              capture_output=True, text=True, cwd=str(REPO))

    # Shape 1: the delta moved, the comment did not.
    bad_delta = run("strike: {damage: +2}   # 6->9\n")
    assert bad_delta.returncode == 1, bad_delta.stdout
    assert "a change of +3" in bad_delta.stdout, bad_delta.stdout

    # Shape 2 (SYS-11a): the arithmetic adds up, the BASE is gone.
    stale_base = run("strike: {damage: +3}   # 4->7\n")
    assert stale_base.returncode == 1, stale_base.stdout
    assert "is not a number the card prints" in stale_base.stdout

    # And the honest row passes.
    ok = run("strike: {damage: +3}   # 6->9\n")
    assert ok.returncode == 0, ok.stdout + ok.stderr


def test_a_lint_ok_marker_excuses_its_pair_and_nothing_else(tmp_path):
    """The marker is NARROWED on purpose. A repricing is usually narrated on
    the row it moved ("was 7->9"), so the live arithmetic and its history
    share a line -- and a whole-line exemption there would switch off the
    check for the number that is still supposed to be true."""
    lint = str(REPO / "tools" / "lint_upgrade_comment_arithmetic.py")
    sheet = tmp_path / "probe-upgrades.yaml"

    def run(text):
        sheet.write_text(text, encoding="utf-8")
        return subprocess.run([sys.executable, lint, str(sheet)],
                              capture_output=True, text=True, cwd=str(REPO))

    # The history is excused; the live pair on the same line is not.
    good = run("strike: {damage: +3}   # 6->9 (was 4->7; lint-ok: 4->7)\n")
    assert good.returncode == 0, good.stdout + good.stderr

    bad = run("strike: {damage: +3}   # 6->8 (was 4->7; lint-ok: 4->7)\n")
    assert bad.returncode == 1, bad.stdout
    assert "a change of +2" in bad.stdout

    # A marker that outlived its claim is itself a finding.
    stale = run("strike: {damage: +3}   # 6->9 (lint-ok: 4->7)\n")
    assert stale.returncode == 1, stale.stdout
    assert "excuses a pair that is not on this line" in stale.stdout


def test_kokomi_decksize_grammar():
    """Kokomi kickoff §1 law 4 (user-authored, machine-checkable → gate):
    Commons in HER pool net card delta <= 0. Scope is her personal sheet
    only — deliberately not the companion pools, not mod-wide."""
    res = subprocess.run(
        [sys.executable, str(REPO / "tools" / "lint_kokomi_decksize.py"),
         str(loader.DOCS_DIR / "kokomi-cards.yaml")],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr


def test_furina_register_grammar():
    """Curtain Call sweep (R85): every Furina card carries a register in
    {salon, archon, private}; Fanfare touches are archon, salon_member
    deploys are salon, pure-Encore cards are private, and EXACTLY two rares
    carry the focalors flavor tag. Scope is her personal sheet only; the
    third-instance rule generalizes this when a second character adopts
    registers."""
    res = subprocess.run(
        [sys.executable, str(REPO / "tools" / "lint_furina_registers.py")],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
    assert "0 register violations" in res.stdout


def test_handwritten_cards_match_their_sheets():
    """Addendum A8: the hand-written cards, against the sheets they came from.

    This lint existed and gated DEPLOY only (validate.ps1 S6), so `pytest` had
    nothing to say about it. R74 deleted `ceremonial_garment`'s entry splash
    from the sheet; the hand-written C# kept dealing it for the length of the
    sprint, across a full green suite and a constant-parity run, because the
    only check that could see it was on the far side of a deploy the sprint
    never performed.

    A gate that runs on deploy and nowhere else does not gate development. It
    reports at the last possible moment, after the measurements it invalidates
    have already been taken.
    """
    res = subprocess.run(
        [sys.executable, str(REPO / "tools" / "lint_handwritten_parity.py")],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
    # EB-3: the gate must be running the Ancient witness too. A lint that
    # silently stopped covering a category still exits 0.
    assert "sheetless Ancients witnessed" in res.stdout, res.stdout


def _row(sheet_name: str, card_id: str) -> dict:
    import yaml
    rows = yaml.safe_load(
        (loader.DOCS_DIR / sheet_name).read_text(encoding="utf-8"))
    return next(r for r in rows if r["id"] == card_id)


def test_furina_kit_burst_numbers_come_from_her_sheet():
    """EB-3. `let_the_people_rejoice` was the last named deferral in the
    hand-written parity gate: its ops (gain_encore, and a Fanfare damage
    rider) had no parity rule, so four numbers in
    Cards/Furina/LetThePeopleRejoice.cs -- 8, 1, 4 and 6 -- existed in C# with
    nothing comparing them to docs/furina-cards.yaml.

    Asserted here at the RULE level rather than only through the lint's exit
    code, because the failure mode that matters is a rule that stops firing:
    a walk that quietly produced no Encore expectation would still leave the
    lint green, since the C# side would then match an empty expectation.
    """
    assert "let_the_people_rejoice" not in hwp.ROSTER_DEFERRED

    row = _row("furina-cards.yaml", "let_the_people_rejoice")
    exp = hwp.Expected()
    hwp.walk_effects(row["effects"], exp, row)
    assert sorted(exp.vars) == [1, 8]        # base damage + the rider's step
    assert exp.encore == [6]                 # gain_encore, not a DynamicVar
    assert exp.fanfare_riders == [(1, 4)]    # 1_per_4_fanfare

    path = (REPO / "klee-mod" / "KleeCode" / "Cards" / "Furina"
            / "LetThePeopleRejoice.cs")
    got = hwp.extract_cs(path.read_text(encoding="utf-8"))
    assert hwp.furina_number_findings(exp, got, path.name) == []
    # And it bites: the Encore literal is a bare int argument, which is the
    # reason it needed a category of its own.
    drifted = hwp.extract_cs(
        path.read_text(encoding="utf-8").replace(
            "GainEncore(Owner.Creature, 6)", "GainEncore(Owner.Creature, 7)"))
    assert hwp.furina_number_findings(exp, drifted, path.name)


def test_every_ancient_card_carries_a_pinned_witness():
    """EB-3, the other half. Ancient-rarity cards have no sheet row and never
    will -- the sim models neither events nor relics -- so `+5 Encore per
    turn` on AllTheWorldsAStage lived in exactly one place in the repo and any
    edit to it was self-consistent by definition.

    ANCIENT_WITNESS pins each one's numbers by value. The pin does not claim
    the number is right (nothing can, for an Ancient); it claims the number is
    what it was when someone last looked, so a change has to be made twice.

    Checked in both directions, like every table in that file: an unpinned
    Ancient and a pin whose card is gone are both findings.
    """
    assert hwp.ancient_witness() == []
    assert "AllTheWorldsAStage" in hwp.ANCIENT_WITNESS
    for name, pin in hwp.ANCIENT_WITNESS.items():
        assert pin.get("why"), f"{name}: a witness without a reason is a shrug"
        assert all(k in pin for k in hwp.WITNESSED_CATEGORIES), name


def test_every_draftable_card_can_be_upgraded():
    """G-C1. A card with no upgrade is a dead campfire choice.

    Two layers, because the 2026-07-25 playtest's actual defect was in the
    second: a card can have a perfectly good sheet delta that the GENERATOR
    cannot express, in which case the sim upgrades it and the live game does
    not. A lint that only checked the sheet would have reported all-clear on
    exactly the card that was reported broken.

    Wired here rather than left as a tool so that a missing upgrade is red,
    not a playtest note.
    """
    res = subprocess.run(
        [sys.executable, str(REPO / "tools" / "lint_upgrade_coverage.py")],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr


def test_card_names_are_unique():
    """Display names: unique internally, and clear of docs/reserved-card-names.txt.

    The reserved list exists because this class of bug is STRUCTURALLY
    INVISIBLE to the repo -- we ship alongside base-game and third-party
    cards whose name lists we cannot read, and the engine resolves a clash
    unpredictably. It was a human who noticed our "Grand Finale" was also
    the Silent's. No instrument here could have. The list is the record of
    those catches; append to it, and don't prune without a reason on file.
    """
    sheets = [str(loader.DOCS_DIR / s) for s in loader.DOCS_CARD_SHEETS]
    res = subprocess.run(
        [sys.executable, str(REPO / "tools" / "lint_unique_names.py"),
         *sheets],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
    # R69: relics are in the namespace too, and the lint must be SEEING them
    # -- a gate that scans zero relic files reports the same clean line as one
    # that scans them all (the §3.1/§3.7 dead-gate class).
    assert "relic names unique" in res.stdout
    assert " 0 relic " not in res.stdout


def test_a_card_relic_name_collision_fails_the_lint(tmp_path):
    """R69's negative test.

    Until R69 this exact collision existed and the lint was green: the Klee
    Rare Power card `explosive_frags` and Klee's Orobas relic upgrade both
    displayed "Explosive Frags", with unrelated effects, both reachable in
    one run. The lint read card sheets only, so relics were outside its
    scope while being squarely inside its purpose.

    Built as a synthetic sheet against the REAL relic sources, so it fails
    if the relic reader stops finding relics -- which is the way a gate like
    this dies.
    """
    lint = str(REPO / "tools" / "lint_unique_names.py")
    sheet = tmp_path / "collide.yaml"
    # "Dodoco Tales" is a real, live relic name. Minting a card with it is
    # precisely the mistake the extended lint exists to refuse.
    sheet.write_text(
        'cards:\n'
        '- {id: fake_collider, name: "Dodoco Tales", cost: 1, type: skill,\n'
        '   rarity: common}\n', encoding="utf-8")

    res = subprocess.run([sys.executable, lint, str(sheet)],
                         capture_output=True, text=True)
    assert res.returncode == 1, (
        "a card taking a live relic's display name must fail the lint\n"
        + res.stdout + res.stderr)
    assert "Dodoco Tales" in res.stdout
    assert ("CROSS-KIND NAME COLLISION" in res.stdout
            or "RESERVED NAME" in res.stdout), res.stdout


def test_the_reserved_list_does_not_fail_the_names_it_protects(tmp_path):
    """The other half of R69's reserved-both-sides rule.

    "Explosive Frags" and "Dodoco Tales" are BOTH reserved, so a naive
    reserved check would fail the card and the relic that legitimately hold
    them -- and the usual fix for that (drop the entries) is exactly what
    lets the collision re-form from the other side. The kind annotation is
    what makes reserving both sides survivable, so it needs its own pin.
    """
    lint = str(REPO / "tools" / "lint_unique_names.py")
    sheet = tmp_path / "owner.yaml"
    sheet.write_text(
        'cards:\n'
        '- {id: explosive_frags, name: "Explosive Frags", cost: 1,\n'
        '   type: power, rarity: rare}\n', encoding="utf-8")

    res = subprocess.run([sys.executable, lint, str(sheet)],
                         capture_output=True, text=True)
    assert res.returncode == 0, (
        "the card that OWNS a card-owned reserved name must pass\n"
        + res.stdout + res.stderr)


def test_the_unique_name_lint_declares_its_encoding(tmp_path):
    """Tooling-hardening sprint item 6.

    `load_cards` was `yaml.safe_load(open(path))` -- no encoding, no context
    manager. This lint's whole job is comparing display NAMES for uniqueness,
    and a name decoded through cp1252 is still perfectly unique, so the defect
    would have landed as a green run rather than as a failure. `Salon Debut`'s
    accented `e` is the live case.

    Pinned in BOTH directions the way the encoding gate argues for: the
    structural half (no undeclared read in the file) because the behavioural
    half only shows the bug on a cp1252 machine, and the behavioural half
    (a non-ASCII name survives the read) because the structural one cannot
    prove the value came back right.
    """
    from tools import lint_text_encoding
    assert "tools/lint_unique_names.py" not in lint_text_encoding.scan(), (
        "lint_unique_names must declare encoding= on its sheet read")

    sys.path.insert(0, str(REPO / "tools"))
    import lint_unique_names
    name = "Salon Début Probe"      # the live accented case, escaped
    sheet = tmp_path / "accented.yaml"
    sheet.write_text(
        "cards:\n"
        f'- {{id: probe_accent, name: "{name}", cost: 1,\n'
        "   type: skill, rarity: common}\n", encoding="utf-8")
    cards = lint_unique_names.load_cards(str(sheet))
    assert [c["name"] for c in cards] == [name]


def test_mirrored_constants_match_the_sim():
    """C# balance constants vs tier0, the source of truth.

    Every balance number lives twice -- once in tier0 where it was MEASURED,
    once in C# where it is PLAYED -- and the C# copies were kept in step by
    discipline alone until 2026-07-25. That failure mode is silent in the
    worst way: a sim-side retune nobody mirrors leaves the build green, the
    tests green, and the tuning report describing a game nobody is playing.

    It is wired into PYTEST as well as into validate.ps1 (S6e) on purpose.
    The retune happens HERE, in Python, and the person doing it runs the
    suite; making them wait for a deploy to learn they left the mod behind
    is one round trip too late. There is no C# test project to pin this at
    runtime, so this static comparison is the whole gate.
    """
    res = subprocess.run(
        [sys.executable, str(REPO / "tools" / "lint_constant_parity.py")],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr


def test_companion_roster_can_fill_both_shop_slots():
    """§4.7 shop channel: instance TWO of the empty-draw class.

    Wired here rather than left as a tool for the same reason as the upgrade
    lint above: the failure it prevents is a black-screen softlock on shop
    entry (finding 24's shape), and the roster corner that causes it moves
    every time someone edits a companion sheet. A thin nation is survivable --
    both implementations carry a fallback ladder -- but every rung the ladder
    takes is a slot that silently stopped honouring §4.7, which is invisible
    at the table and visible here.
    """
    res = subprocess.run(
        [sys.executable,
         str(REPO / "tools" / "lint_companion_shop_coverage.py")],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr


def test_register_stays_out_of_the_engine():
    """R85's register column is naming and art, never mechanics.

    Cell 1 of the Curtain Call sweep PROVED this empirically -- renames plus
    register assignments landed together and the run was byte-identical, so
    nothing read the new field. That is a measurement, and a measurement only
    speaks for the code that existed when it ran. This converts it into a
    standing guarantee.

    The failure it prevents is the nastiest kind of coupling: with a
    register-aware engine, moving a card from the salon voice to the archon
    one -- an ART decision, taken on art grounds, by whoever is picking
    illustrations -- would silently move win rate, and the next sim run would
    blame whatever else changed that day. Balance and lore have to be able to
    move independently.
    """
    res = subprocess.run(
        [sys.executable,
         str(REPO / "tools" / "lint_register_isolation.py")],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr


def test_every_engine_op_has_a_drafter_price():
    """Op parity (sim-hygiene sprint, 2026-07-29): tools/lint_op_parity.py.

    Wired into PYTEST as well as into CI for the same reason the constant
    parity lint is: the moment an op is registered is the moment the author
    knows what it is worth, and that moment is a pytest run, not a push. An
    op with no price is worth nothing to the drafter SILENTLY -- the defect
    class DRAFTER_VERSION 6, 7, 8 and 9 each rediscovered by measuring one
    character and wondering why its plan drafted badly.
    """
    res = subprocess.run(
        [sys.executable, str(REPO / "tools" / "lint_op_parity.py")],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr


def test_the_op_parity_lint_still_catches_a_newly_registered_op():
    """The red half. A lint nobody has seen fail is a lint nobody can trust.

    Registers a fictional op in the engine registry, in-process, and asserts
    the lint reports it as a FINDING rather than skipping it. The registry is
    restored in the `finally` -- this test must not leak a fake verb into the
    rest of the session.
    """
    import importlib

    from tier0.engine import effects as _effects
    lint = importlib.import_module("tools.lint_op_parity")

    assert lint.findings() == [], "the lint must be green before it is red"
    _effects.OPS["chorus_of_the_unpriced"] = lambda state, fx, card: None
    try:
        bad = lint.findings()
    finally:
        del _effects.OPS["chorus_of_the_unpriced"]
    assert any("chorus_of_the_unpriced" in line and "UNPRICED OP" in line
               for line in bad), bad
    assert lint.findings() == [], "and green again once the op is gone"
