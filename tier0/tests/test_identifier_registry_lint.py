"""Pins for tools/lint_identifier_registry.py (housekeeping sweep, Track X).

The lint's whole value is that it checks ADDITIONS and grandfathers the corpus.
These tests pin that in BOTH directions -- the green cases matter as much as the
red ones, because a lint that flags the existing corpus would be reverted within
a week and the registry would rot.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
LINT_PATH = REPO_ROOT / "tools" / "lint_identifier_registry.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("lint_identifier_registry", LINT_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def lint():
    return _load_module()


def _fixture_repo(tmp_path: pathlib.Path) -> pathlib.Path:
    """A miniature repo: one registry, one doc, no snapshot yet."""
    (tmp_path / "docs" / "registry").mkdir(parents=True)
    (tmp_path / "docs" / "registry" / "identifiers.md").write_text(
        "# Identifier registry\n\n"
        "| Qualified form | Meaning |\n|---|---|\n"
        "| `S4-G1` | the S4 gate |\n"
        "| `CC-G1` | the Curtain Call gate |\n"
        "| `SS-G4` | worktree-per-session |\n"
        "| `NC-1` | a parity family |\n",
        encoding="utf-8",
    )
    (tmp_path / "docs" / "old-sprint-log.md").write_text(
        "Legacy prose. Gate G1 is open and NC-7 is filed and X9 rides along.\n",
        encoding="utf-8",
    )
    return tmp_path


def _point(lint, root: pathlib.Path) -> None:
    lint.REPO = root
    lint.REGISTRY = root / "docs" / "registry" / "identifiers.md"
    lint.BASELINE = root / "docs" / "registry" / "known-identifiers.tsv"
    lint.SCAN_ROOTS = ("docs",)
    lint.EXTRA_FILES = ()
    lint.LEDGERS = ()


# --------------------------------------------------------------------------
# Grandfathering: the corpus as it stands is never an error.
# --------------------------------------------------------------------------


def test_baselined_corpus_is_green_even_though_it_is_full_of_collisions(lint, tmp_path):
    root = _fixture_repo(tmp_path)
    _point(lint, root)
    # `NC-7` and `X9` are NOT in the registry, and the legacy doc uses a bare G1
    # that two namespaces mint. Snapshot it, and none of that is an error.
    tokens, files = lint.harvest()
    lint.write_baseline(tokens, files)
    assert lint.check() == 0


def test_deleting_an_identifier_is_not_an_error(lint, tmp_path):
    root = _fixture_repo(tmp_path)
    _point(lint, root)
    lint.write_baseline(*lint.harvest())
    (root / "docs" / "old-sprint-log.md").write_text("nothing here now\n", encoding="utf-8")
    assert lint.check() == 0


# --------------------------------------------------------------------------
# RULE 1 -- a new identifier must be written down in the registry.
# --------------------------------------------------------------------------


def test_rule1_new_unregistered_identifier_fails(lint, tmp_path, capsys):
    root = _fixture_repo(tmp_path)
    _point(lint, root)
    lint.write_baseline(*lint.harvest())
    (root / "docs" / "new-note.md").write_text(
        "Filed as NC-42, which nobody wrote down.\nidentifier-registry: allow-bare\n",
        encoding="utf-8",
    )
    assert lint.check() == 1
    out = capsys.readouterr().out
    assert "RULE 1" in out and "NC-42" in out


def test_rule1_new_identifier_passes_once_registered(lint, tmp_path):
    root = _fixture_repo(tmp_path)
    _point(lint, root)
    lint.write_baseline(*lint.harvest())
    (root / "docs" / "new-note.md").write_text(
        "Filed as NC-42.\nidentifier-registry: allow-bare\n", encoding="utf-8"
    )
    reg = root / "docs" / "registry" / "identifiers.md"
    reg.write_text(reg.read_text(encoding="utf-8") + "| `NC-42` | a new family |\n",
                   encoding="utf-8")
    assert lint.check() == 0


# --------------------------------------------------------------------------
# RULE 2 -- a NEW document may not mint a bare ambiguous G-token.
#           This is the synthetic-collision case.
# --------------------------------------------------------------------------


def test_rule2_new_document_with_bare_ambiguous_gate_fails(lint, tmp_path, capsys):
    root = _fixture_repo(tmp_path)
    _point(lint, root)
    lint.write_baseline(*lint.harvest())
    (root / "docs" / "brand-new-sprint.md").write_text(
        "## Track G\n- **G1.** Do the thing.\n", encoding="utf-8"
    )
    assert lint.check() == 1
    out = capsys.readouterr().out
    assert "RULE 2" in out and "G1" in out and "brand-new-sprint.md" in out


def test_rule2_qualified_form_passes(lint, tmp_path):
    root = _fixture_repo(tmp_path)
    _point(lint, root)
    lint.write_baseline(*lint.harvest())
    (root / "docs" / "brand-new-sprint.md").write_text(
        "## Track G\n- **`NS-G1`.** Do the thing.\n", encoding="utf-8"
    )
    reg = root / "docs" / "registry" / "identifiers.md"
    reg.write_text(reg.read_text(encoding="utf-8") + "| `NS-G1` | new sprint gate 1 |\n",
                   encoding="utf-8")
    assert lint.check() == 0


def test_rule2_escape_hatch_passes(lint, tmp_path):
    root = _fixture_repo(tmp_path)
    _point(lint, root)
    lint.write_baseline(*lint.harvest())
    (root / "docs" / "brand-new-sprint.md").write_text(
        "identifier-registry: allow-bare\n\n## Track G\n- **G1.** Deliberate.\n",
        encoding="utf-8",
    )
    assert lint.check() == 0


def test_rule2_only_fires_on_ambiguous_numbers(lint, tmp_path):
    """G4 is minted by exactly one namespace in the fixture registry, so a new
    document may use it bare. Under-flagging is the deliberate posture."""
    root = _fixture_repo(tmp_path)
    _point(lint, root)
    lint.write_baseline(*lint.harvest())
    (root / "docs" / "brand-new-sprint.md").write_text(
        "Worktree-per-session (G4).\n", encoding="utf-8"
    )
    assert lint.check() == 0


def test_ambiguous_number_derivation_reads_the_registry(lint, tmp_path):
    root = _fixture_repo(tmp_path)
    _point(lint, root)
    assert lint.ambiguous_gate_numbers() == {"1"}


# --------------------------------------------------------------------------
# RULE 3 -- a NEW document may not mint an open-item row outside the two homes
#           an open item has (docs diet, Track Z / Z-3).
# --------------------------------------------------------------------------


def _new_doc_with_open_rows(root: pathlib.Path, name: str, header: str = "") -> None:
    (root / "docs" / name).parent.mkdir(parents=True, exist_ok=True)
    (root / "docs" / name).write_text(
        f"# A brand new note\n\n{header}\n"
        "identifier-registry: allow-bare\n\n"
        "- **Ribbon legibility** -- AWAITING [USER], nobody has looked at it.\n"
        "- **The pulse has no visual** -- **OPEN**, needs a ruling.\n",
        encoding="utf-8",
    )


def test_rule3_new_document_minting_open_items_fails(lint, tmp_path, capsys):
    root = _fixture_repo(tmp_path)
    _point(lint, root)
    lint.write_baseline(*lint.harvest())
    _new_doc_with_open_rows(root, "brand-new-sprint.md")
    assert lint.check() == 1
    out = capsys.readouterr().out
    assert "RULE 3" in out and "brand-new-sprint.md" in out


def test_rule3_the_queue_itself_is_allowed(lint, tmp_path):
    root = _fixture_repo(tmp_path)
    _point(lint, root)
    lint.write_baseline(*lint.harvest())
    _new_doc_with_open_rows(root, "registry/user-queue.md")
    assert lint.check() == 0


def test_rule3_a_docket_is_allowed(lint, tmp_path):
    root = _fixture_repo(tmp_path)
    _point(lint, root)
    lint.write_baseline(*lint.harvest())
    _new_doc_with_open_rows(root, "dockets/new-thing.md")
    assert lint.check() == 0


def test_rule3_frozen_lifecycle_header_exempts(lint, tmp_path):
    """A REFERENCE record restates the history of an item; it does not mint work."""
    root = _fixture_repo(tmp_path)
    _point(lint, root)
    lint.write_baseline(*lint.harvest())
    _new_doc_with_open_rows(
        root, "brand-new-sprint.md", header="> **Lifecycle: REFERENCE** -- frozen record.\n"
    )
    assert lint.check() == 0


def test_rule3_escape_hatch_passes(lint, tmp_path):
    root = _fixture_repo(tmp_path)
    _point(lint, root)
    lint.write_baseline(*lint.harvest())
    _new_doc_with_open_rows(root, "brand-new-sprint.md", header="open-items: allow-elsewhere\n")
    assert lint.check() == 0


def test_rule3_prose_mentioning_an_open_question_is_not_a_row(lint, tmp_path):
    """Under-flagging is the deliberate posture: only a bullet or table row that
    carries an open marker is a minted row."""
    root = _fixture_repo(tmp_path)
    _point(lint, root)
    lint.write_baseline(*lint.harvest())
    (root / "docs" / "brand-new-sprint.md").write_text(
        "# Note\n\nidentifier-registry: allow-bare\n\n"
        "The axis question is still open, and the queue tracks it as AWAITING.\n",
        encoding="utf-8",
    )
    assert lint.check() == 0


def test_rule3_grandfathered_documents_never_fight_it(lint, tmp_path):
    """An existing register full of open rows stays green forever."""
    root = _fixture_repo(tmp_path)
    _point(lint, root)
    _new_doc_with_open_rows(root, "old-register.md")
    lint.write_baseline(*lint.harvest())
    assert lint.check() == 0


# --------------------------------------------------------------------------
# The real tree.
# --------------------------------------------------------------------------


def test_real_repo_is_green_and_snapshot_is_current(lint):
    """The committed snapshot must describe the committed tree, or the lint is
    dark. This is also the test that fails when someone mints a code and forgets
    the registry."""
    assert lint.BASELINE.exists(), "the grandfathering snapshot is not committed"
    assert lint.check() == 0
