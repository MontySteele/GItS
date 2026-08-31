"""Tests for tools/art_ledger.py (charter label EB-148, tooling lane B).

FIXTURES, NOT THE REAL TREE. `ImageGen/` and `art/raw/` are gitignored Tier F,
so on CI and in every fresh worktree the real art tree is simply absent -- a
test that asserted against it would be green for the wrong reason on the only
machines that run it. Every test here builds a small synthetic checkout under
`tmp_path` and points `--root` at it, which is exactly why the tool takes a
required `--root` in the first place.

The three checks the lane charter names each get a test that proves the
finding fires AND a sibling assertion that the healthy case does not:

    test_missing_packed_path_is_a_finding
    test_stale_source_row_is_a_finding
    test_unintended_fallback_is_a_finding / test_declared_fallback_is_not_unintended
"""
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

import art_ledger  # noqa: E402

REPO = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Fixture construction
# ---------------------------------------------------------------------------

def _write(root: Path, rel: str, text: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def _png(root: Path, rel: str, body: bytes | None = None) -> Path:
    """A fixture PNG. Bytes default to something UNIQUE PER PATH, because the
    unintended-fallback check is a byte-identity check: a fixture that wrote
    one constant everywhere would report every surface as wearing every other
    surface's art."""
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(body if body is not None
                  else b"\x89PNG\r\n\x1a\n" + rel.encode("utf-8"))
    return p


BUILD_PCK_FIXTURE = r"""
$pckExclude = '*_cutout.png'

function Copy-FurinaFallback([string]$relative) {
    $target = Join-Path (Join-Path $work 'furina') $relative
    if (Test-Path $target) { return }
    $fallback = Join-Path (Join-Path $work 'klee') $relative
    Copy-Item $fallback -Destination $target
    Write-Host "Furina fallback: $relative <- Klee"
}

foreach ($relative in @(
        'ui\select_portrait.png',
        'ui\transition_wipe.png')) {
    Copy-FurinaFallback $relative
}

# A comment that quotes res://furina/ui/never_expected.png must NOT create an
# expectation -- only here-string bodies count.
[IO.File]::WriteAllText((Join-Path $work 'klee\ui\char_select_bg_klee.tscn'), @'
[gd_scene format=3]
[ext_resource type="Texture2D" path="res://klee/ui/select_bg.png" id="1"]
'@)
"""

ART_LINT_FIXTURE = '''\
"""Fixture stand-in for tools/art_lint.py -- registries only."""
GENERATOR_OWNED = {
    "ImageGen/images/ui/transition_wipe.png": "gen_wipe.py",
}
PENDING_UNDERSIZE = {"undersized_card"}
KNOWN_UNDERSIZED = set()
PENDING_BANNED_FAMILY = set()
PENDING_RED_PEN = {frozenset({"card_one", "card_two"})}
KNOWN_IDENTICAL = set()
APPROVED_FAMILY_EXCEPTIONS = {}
'''

ART_COVERAGE_FIXTURE = '''\
"""Fixture stand-in for tools/art_coverage.py -- KNOWN_STALE only."""
KNOWN_STALE = {"retired_card": "cut in the fixture's imaginary red-pen pass"}
'''

GEN_WIPE_FIXTURE = '''\
"""Generate the wipe (Tier O, procedural).

Writes ImageGen/images/ui/transition_wipe.png from pure geometry.
"""
'''


def make_root(tmp_path: Path) -> Path:
    """A minimal but complete synthetic checkout the ledger can read."""
    root = tmp_path / "checkout"
    root.mkdir()

    # --- canonical sheets -------------------------------------------------
    _write(root, "docs/klee-cards.yaml",
           "- id: card_one\n  rarity: common\n"
           "- id: card_two\n  rarity: rare\n")
    _write(root, "docs/furina-cards.yaml", "- id: furina_card\n  rarity: common\n")
    _write(root, "docs/kokomi-cards.yaml", "- id: kokomi_card\n  rarity: common\n")
    for nation in ("inazuma", "mondstadt", "fontaine"):
        _write(root, f"docs/{nation}-companions.yaml",
               f"- id: {nation}_companion\n  rarity: common\n")
    _write(root, "tier0/content/cards/tokens.yaml",
           "- id: a_token\n  rarity: token\n")

    # --- mod source -------------------------------------------------------
    _write(root, "klee-mod/KleeCode/Fixture.cs", """\
namespace Fixture;
internal static class F
{
    // A doc comment quoting "klee/ui/foo.png" must not create an expectation.
    public static string A => KleePck.Path("klee/ui/select_portrait.png");
    public static string B => KleePck.Path("klee/ui/select_bg.png");
    public static string C => KleePck.Path("klee/ui/transition_wipe.png");
    public static string D => KleePck.Path("furina/ui/select_portrait.png");
    public static string E => KleePck.Path("furina/ui/transition_wipe.png");
    public static string F2 => KleePck.Path("klee/powers/only_in_source.png");
    public static Texture2D? P => RosterArt.CardPortrait("csharp_only_card");
}
""")

    # --- build script + curated registries --------------------------------
    _write(root, "tools/build_pck.ps1", BUILD_PCK_FIXTURE)
    _write(root, "tools/art_lint.py", ART_LINT_FIXTURE)
    _write(root, "tools/art_coverage.py", ART_COVERAGE_FIXTURE)
    _write(root, "tools/gen_wipe.py", GEN_WIPE_FIXTURE)

    # --- provenance -------------------------------------------------------
    # card_one stays line 2 and select_portrait line 3 -- two tests cite those
    # line numbers. Everything BELOW them exists so the healthy fixture is
    # genuinely healthy under the EB-163 PROVENANCE-GAP check: a rendered file
    # with no recorded origin is a defect now, so a fixture that shipped ten of
    # them would have made the "healthy fixture is quiet" baseline a lie.
    # transition_wipe is deliberately ABSENT here -- it is generator-owned, and
    # a SOURCES row would shadow the generator's own Tier declaration, which
    # test_rights_tiers_come_from_declared_evidence_only reads.
    _write(root, "art/SOURCES.tsv",
           "filename\tsource_url\ttier\treplace_priority\n"
           "ImageGen/images/cards/klee/card_one.png\thttps://example/one\tF\thigh\n"
           "ImageGen/images/ui/select_portrait.png\thttps://example/portrait\tF\thigh\n"
           "ImageGen/images/cards/klee/card_two.png\thttps://example/two\tF\thigh\n"
           "ImageGen/images/cards/furina/furina_card.png\thttps://example/f\tF\thigh\n"
           "ImageGen/images/cards/furina/a_token.png\thttps://example/tok\tF\thigh\n"
           "ImageGen/images/cards/kokomi/kokomi_card.png\thttps://example/k\tF\thigh\n"
           "ImageGen/images/cards/companions/inazuma_companion.png\thttps://example/i\tF\thigh\n"
           "ImageGen/images/cards/companions/mondstadt_companion.png\thttps://example/m\tF\thigh\n"
           "ImageGen/images/cards/companions/fontaine_companion.png\thttps://example/fo\tF\thigh\n"
           "ImageGen/images/ui/select_bg.png\thttps://example/bg\tF\tlow\n"
           "ImageGen/images/powers/only_in_source.png\thttps://example/only\tF\tlow\n"
           "ImageGen/images/furina/ui/select_portrait.png\thttps://example/fp\tF\thigh\n")
    _write(root, "art/plan.tsv",
           "# fixture plan\n"
           "card_one\tImageGen/images/cards/klee/card_one.png\t500\t380\tcover\t"
           "c\tauto\t\tpng\tOne Source.png\t\tsplash\n")

    # --- rendered art -----------------------------------------------------
    for rel in ("ImageGen/images/cards/klee/card_one.png",
                "ImageGen/images/cards/klee/card_two.png",
                "ImageGen/images/cards/furina/furina_card.png",
                "ImageGen/images/cards/furina/a_token.png",
                "ImageGen/images/cards/kokomi/kokomi_card.png",
                "ImageGen/images/cards/companions/inazuma_companion.png",
                "ImageGen/images/cards/companions/mondstadt_companion.png",
                "ImageGen/images/cards/companions/fontaine_companion.png",
                "ImageGen/images/ui/select_portrait.png",
                "ImageGen/images/ui/select_bg.png",
                "ImageGen/images/ui/transition_wipe.png",
                "ImageGen/images/powers/only_in_source.png",
                "ImageGen/images/furina/ui/select_portrait.png"):
        _png(root, rel)

    # --- pck contract -----------------------------------------------------
    _write(root, "klee-mod/assets/klee.pck.contract.txt",
           "contract=roster-pck-v3\n"
           "sha256=FIXTURE\n"
           "resource=res://klee/ui/select_portrait.png\n"
           "resource=res://klee/ui/select_bg.png\n"
           "resource=res://klee/ui/transition_wipe.png\n"
           "resource=res://klee/ui/char_select_bg_klee.tscn\n"
           "resource=res://klee/powers/only_in_source.png\n"
           "resource=res://furina/ui/select_portrait.png\n"
           "resource=res://furina/ui/transition_wipe.png\n")
    return root


@pytest.fixture()
def root(tmp_path):
    return make_root(tmp_path)


def checks(ledger, name):
    return [f for f in ledger.findings if f.check == name]


# ---------------------------------------------------------------------------
# Baseline: a healthy fixture is quiet
# ---------------------------------------------------------------------------

def test_healthy_fixture_has_no_defect_findings(root):
    led = art_ledger.Ledger(root)
    defects = [f for f in led.findings if f.check in art_ledger.DEFECT_CHECKS]
    assert defects == [], [f"{f.check} {f.surface_id}: {f.detail}" for f in defects]


def test_every_expected_surface_is_billed(root):
    led = art_ledger.Ledger(root)
    ids = {r.surface_id for r in led.rows}
    # 7 sheet cards + 1 token + 1 C#-only card
    assert sum(1 for r in led.rows if r.kind == "card") == 9
    assert "card:shared:csharp_only_card" in ids
    # The scene is expected because build_pck.ps1's here-string authors it,
    # and select_bg.png because that scene references it -- neither is named
    # by any C# literal.
    assert "pck:klee/ui/char_select_bg_klee.tscn" in ids
    assert "pck:klee/ui/select_bg.png" in ids


def test_doc_comment_paths_are_not_expectations(root):
    led = art_ledger.Ledger(root)
    assert "pck:klee/ui/foo.png" not in {r.surface_id for r in led.rows}


def test_build_script_comment_is_not_an_expectation(root):
    """Only here-string BODIES are scanned; a comment that quotes a res:// path
    while explaining a defect is prose, not a demand."""
    led = art_ledger.Ledger(root)
    assert "pck:furina/ui/never_expected.png" not in {r.surface_id for r in led.rows}


# ---------------------------------------------------------------------------
# CHECK 1 -- a missing packed path
# ---------------------------------------------------------------------------

def test_missing_packed_path_is_a_finding(root):
    """The mod asks for a resource the build contract does not contain."""
    contract = root / "klee-mod/assets/klee.pck.contract.txt"
    contract.write_text(
        "\n".join(l for l in contract.read_text(encoding="utf-8").splitlines()
                  if "only_in_source" not in l) + "\n", encoding="utf-8")

    led = art_ledger.Ledger(root)
    found = checks(led, "MISSING-PACKED")
    assert [f.surface_id for f in found] == ["pck:klee/powers/only_in_source.png"]
    assert "klee-mod/KleeCode/Fixture.cs" in found[0].detail
    row = next(r for r in led.rows
               if r.surface_id == "pck:klee/powers/only_in_source.png")
    assert row.status == "defect"
    # The rendered PNG is still on disk: "the art exists but never reached the
    # pack" is precisely the case a rendered-only coverage number cannot see.
    assert row.rendered_present is True


def test_missing_packed_path_flags_diagnostics_probes_differently(root):
    _write(root, "klee-mod/KleeCode/Diagnostics/Probe.cs",
           'class P { string[] S = { "kokomi/model/combat.tscn" }; }')
    led = art_ledger.Ledger(root)
    found = [f for f in checks(led, "MISSING-PACKED")
             if f.surface_id == "pck:kokomi/model/combat.tscn"]
    assert found and "diagnostics probe list" in found[0].detail


# ---------------------------------------------------------------------------
# CHECK 2 -- a stale row
# ---------------------------------------------------------------------------

def test_stale_source_row_is_a_finding(root):
    """A SOURCES.tsv provenance row whose rendered output no longer exists."""
    (root / "ImageGen/images/ui/select_portrait.png").unlink()

    led = art_ledger.Ledger(root)
    found = checks(led, "STALE-ROW")
    assert [f.surface_id for f in found] == \
        ["sources:ImageGen/images/ui/select_portrait.png"]
    assert "art/SOURCES.tsv:3" in found[0].detail


def test_candidate_rows_are_not_stale_rows(root):
    """art/candidates/** is gitignored shortlist scratch; its absence is
    housekeeping, not a stale ledger row."""
    src = root / "art/SOURCES.tsv"
    src.write_text(src.read_text(encoding="utf-8")
                   + "art/candidates/card_one/r1.png\thttps://example/r1\tF\thigh\n",
                   encoding="utf-8")
    led = art_ledger.Ledger(root)
    assert checks(led, "STALE-ROW") == []


# ---------------------------------------------------------------------------
# CHECK -- provenance gaps (EB-163)
# ---------------------------------------------------------------------------

def test_a_rendered_file_with_no_recorded_origin_is_a_provenance_gap(root):
    """The check has to BITE, and be seen to. Drop card_one's SOURCES row and
    the file it points at keeps existing -- shipped bytes, no origin."""
    src = root / "art/SOURCES.tsv"
    kept = [ln for ln in src.read_text(encoding="utf-8").splitlines()
            if "cards/klee/card_one.png" not in ln]
    src.write_text("\n".join(kept) + "\n", encoding="utf-8")

    led = art_ledger.Ledger(root)
    found = checks(led, "PROVENANCE-GAP")
    assert [f.surface_id for f in found] == \
        ["file:ImageGen/images/cards/klee/card_one.png"]
    assert "PROVENANCE-GAP" in art_ledger.DEFECT_CHECKS


def test_a_surface_with_no_bytes_is_not_a_provenance_gap(root):
    """The distinction the check is built on. `csharp_only_card` has no
    SOURCES row AND no rendered file: that is an ART BILL (MISSING-RENDER),
    and calling it a provenance gap would let someone 'fix' missing art by
    writing it a provenance row."""
    led = art_ledger.Ledger(root)
    gaps = {f.surface_id for f in checks(led, "PROVENANCE-GAP")}
    missing = {f.surface_id for f in checks(led, "MISSING-RENDER")}
    assert "card:shared:csharp_only_card" in missing
    assert gaps == set()


def test_a_promoted_shortlist_resolves_through_its_candidate_row(root):
    """EB-163's first kind. A shortlist face is cleared at the CANDIDATE key,
    because that is the file art_fetch wrote; --apply-picks then copies it to
    the out-path. Reading only the out-path key reported 265 fully-recorded
    surfaces as having no provenance at all."""
    _png(root, "ImageGen/images/cards/klee/card_three.png")
    _write(root, "docs/klee-cards.yaml",
           (root / "docs/klee-cards.yaml").read_text(encoding="utf-8")
           + "- {id: card_three, name: Card Three}\n")
    plan = root / "art/plan.tsv"
    plan.write_text(plan.read_text(encoding="utf-8")
                    + "card_three\tImageGen/images/cards/klee/card_three.png\t500"
                      "\t380\tcover\tc\tshortlist\t1\tpng\tThree Source.png\t\tsplash\n",
                    encoding="utf-8")

    led = art_ledger.Ledger(root)
    assert "file:ImageGen/images/cards/klee/card_three.png" in \
        {f.surface_id for f in checks(led, "PROVENANCE-GAP")}

    src = root / "art/SOURCES.tsv"
    src.write_text(src.read_text(encoding="utf-8")
                   + "art/candidates/card_three/r1.png\thttps://example/three\tF\thigh\n",
                   encoding="utf-8")
    led = art_ledger.Ledger(root)
    assert checks(led, "PROVENANCE-GAP") == []
    row = {r.surface_id: r for r in led.rows}["card:klee:card_three"]
    assert row.rights_tier == "private-placeholder"
    assert "candidate row art/candidates/card_three/r1.png" in row.rights_evidence


def test_a_dead_rank_does_not_lend_its_clearance_to_the_effective_pick(root):
    """Two ranks are two different pictures. A candidate row for r2 must not
    silence the gap on a face whose EFFECTIVE pick is r1."""
    _png(root, "ImageGen/images/cards/klee/card_three.png")
    _write(root, "docs/klee-cards.yaml",
           (root / "docs/klee-cards.yaml").read_text(encoding="utf-8")
           + "- {id: card_three, name: Card Three}\n")
    plan = root / "art/plan.tsv"
    plan.write_text(plan.read_text(encoding="utf-8")
                    + "card_three\tImageGen/images/cards/klee/card_three.png\t500"
                      "\t380\tcover\tc\tshortlist\t1\tpng\tThree Source.png\t\tsplash\n",
                    encoding="utf-8")
    src = root / "art/SOURCES.tsv"
    src.write_text(src.read_text(encoding="utf-8")
                   + "art/candidates/card_three/r2.png\thttps://example/r2\tF\thigh\n",
                   encoding="utf-8")

    led = art_ledger.Ledger(root)
    assert "file:ImageGen/images/cards/klee/card_three.png" in \
        {f.surface_id for f in checks(led, "PROVENANCE-GAP")}


def test_stale_output_is_a_finding_and_a_known_reason_silences_it(root):
    _png(root, "ImageGen/images/cards/klee/orphan.png")
    _png(root, "ImageGen/images/cards/klee/retired_card.png")

    led = art_ledger.Ledger(root)
    stale = {f.surface_id for f in checks(led, "STALE-OUTPUT")}
    assert stale == {"file:ImageGen/images/cards/klee/orphan.png"}
    # KNOWN_STALE, read out of <root>/tools/art_coverage.py, is a NOTE.
    recorded = dict(led.stale_outputs)
    assert "cut in the fixture" in \
        recorded["ImageGen/images/cards/klee/retired_card.png"]


def test_build_excluded_working_file_is_not_stale(root):
    _png(root, "ImageGen/images/ui/klee_cutout.png")
    led = art_ledger.Ledger(root)
    assert checks(led, "STALE-OUTPUT") == []
    recorded = dict(led.stale_outputs)
    assert "$pckExclude" in recorded["ImageGen/images/ui/klee_cutout.png"]


# ---------------------------------------------------------------------------
# CHECK 3 -- an unintended fallback
# ---------------------------------------------------------------------------

def test_declared_fallback_is_reported_as_active_not_unintended(root):
    """Furina has no wipe of her own; build_pck.ps1 declares the fallback."""
    led = art_ledger.Ledger(root)
    active = checks(led, "ACTIVE-FALLBACK")
    assert [f.surface_id for f in active] == ["pck:furina/ui/transition_wipe.png"]
    assert checks(led, "UNINTENDED-FALLBACK") == []
    row = next(r for r in led.rows
               if r.surface_id == "pck:furina/ui/transition_wipe.png")
    assert row.fallback == "active:klee"
    assert row.status == "fallback"


def test_unintended_fallback_from_byte_identity(root):
    """Two characters ship the SAME pixels at a path nobody declared.

    This is the C4 defect class made visible: a green build in which one
    character silently wears another's face. String checks cannot see it --
    the two paths differ, the two files exist, every count is full.
    """
    same = (root / "ImageGen/images/ui/select_portrait.png").read_bytes()
    (root / "ImageGen/images/furina/ui/select_portrait.png").write_bytes(same)

    led = art_ledger.Ledger(root)
    found = checks(led, "UNINTENDED-FALLBACK")
    assert {f.surface_id for f in found} == {
        "pck:furina/ui/select_portrait.png", "pck:klee/ui/select_portrait.png"}
    assert all("identical" in f.detail for f in found)
    # A declared fallback does not excuse it: an ACTIVE fallback means the
    # character has no rendered file, and this one does.
    furina = next(f for f in found if f.surface_id.startswith("pck:furina"))
    assert "cannot be the cause" in furina.detail


def test_undeclared_fallback_in_a_build_log_is_a_finding(root, tmp_path):
    log = tmp_path / "build.log"
    log.write_text(
        "Stamped build id 20260826-000000+abc123\n"
        r"Furina fallback: ui\transition_wipe.png <- Klee" + "\n"
        r"Kokomi fallback: ui\char_icon.png <- Klee" + "\n",
        encoding="utf-8")

    led = art_ledger.Ledger(root, build_log=log)
    found = checks(led, "UNINTENDED-FALLBACK")
    # The Furina wipe is declared; the Kokomi icon is not (the fixture build
    # script has no Kokomi fallback block at all).
    assert [f.surface_id for f in found] == ["pck:kokomi/ui/char_icon.png"]
    assert "does not declare" in found[0].detail


def test_build_log_fallback_that_fired_despite_real_art_is_a_finding(root, tmp_path):
    """The `-Exclude` defect: the copy block skipped, so the fallback fired
    over art that exists. Both the log line and the file are individually
    innocent; only the join says anything."""
    _png(root, "ImageGen/images/furina/ui/transition_wipe.png")
    log = tmp_path / "build.log"
    log.write_text(r"Furina fallback: ui\transition_wipe.png <- Klee" + "\n",
                   encoding="utf-8")

    led = art_ledger.Ledger(root, build_log=log)
    found = checks(led, "UNINTENDED-FALLBACK")
    assert [f.surface_id for f in found] == ["pck:furina/ui/transition_wipe.png"]
    assert "even though" in found[0].detail


def test_fallback_source_character_is_read_correctly(root):
    """Anchored on `$fallback =`: an unanchored regex matches the TARGET
    Join-Path first and reports every character falling back to itself."""
    led = art_ledger.Ledger(root)
    assert led._fallbacks["furina"]["ui/transition_wipe.png"] == "klee"


# ---------------------------------------------------------------------------
# Rights: read, never assigned; the two coverages never merge
# ---------------------------------------------------------------------------

def test_rights_tiers_come_from_declared_evidence_only(root):
    led = art_ledger.Ledger(root)
    by_id = {r.surface_id: r for r in led.rows}

    # (1) SOURCES.tsv tier column
    card = by_id["card:klee:card_one"]
    assert card.rights_tier == "private-placeholder"
    assert "art/SOURCES.tsv:2" in card.rights_evidence and "tier=F" in card.rights_evidence

    # (2) generator docstring declaration
    wipe = by_id["pck:klee/ui/transition_wipe.png"]
    assert wipe.rights_tier == "public-safe"
    assert "gen_wipe.py" in wipe.rights_evidence

    # (3) nothing at all -> unclassified, and it says why. The case is carried
    # by the C#-only card, which has NO rendered file: unclassified rights and
    # an unrecorded ORIGIN are two different facts, and after EB-163 only the
    # second is a defect. A surface with no bytes cannot have an unrecorded
    # origin -- there is nothing to have come from anywhere.
    plain = by_id["card:shared:csharp_only_card"]
    assert plain.rights_tier == "unclassified"
    assert "no SOURCES.tsv row" in plain.rights_evidence


def test_private_and_public_coverage_are_reported_separately(root):
    led = art_ledger.Ledger(root)
    cov = led.rights_coverage()
    assert set(cov) <= set(art_ledger.RIGHTS_CATEGORIES)
    assert "private-placeholder" in cov and "public-safe" in cov
    # The two buckets share no surface: a summed "coverage" number would be
    # meaningless, so the tool never computes one.
    private = {r.surface_id for r in led.rows
               if r.rights_tier == "private-placeholder"}
    public = {r.surface_id for r in led.rows if r.rights_tier == "public-safe"}
    assert private and public and not (private & public)


def test_rights_inheritance_check_fires_on_a_derived_tier_o_claim(root):
    """A generator cannot declare Tier O for an output it derives from a
    Tier F input."""
    _write(root, "tools/gen_wipe.py", GEN_WIPE_FIXTURE.replace(
        "from pure geometry.",
        "by re-cropping select_portrait.png."))
    led = art_ledger.Ledger(root)
    found = checks(led, "RIGHTS-INHERITANCE")
    assert [f.surface_id for f in found] == \
        ["file:ImageGen/images/ui/transition_wipe.png"]


# ---------------------------------------------------------------------------
# Review state, computed paths, schema, CLI
# ---------------------------------------------------------------------------

def test_review_state_is_read_from_the_curated_registries(root):
    led = art_ledger.Ledger(root)
    by_id = {r.surface_id: r for r in led.rows}
    assert by_id["card:klee:card_one"].review_state == \
        "pending-red-pen:duplicate-source"
    assert by_id["card:furina:furina_card"].review_state == "none"


def test_computed_paths_attribute_files_and_are_named_as_unenumerable(root):
    _write(root, "klee-mod/KleeCode/Computed.cs",
           'class C { string P => KleePck.Path("klee/powers/aura_" + e + ".png"); }')
    _png(root, "ImageGen/images/powers/aura_pyro.png")
    _png(root, "ImageGen/images/powers/aura_hydro.png", b"\x89PNG\r\n\x1a\nOTHER")

    led = art_ledger.Ledger(root)
    ids = {r.surface_id for r in led.rows}
    assert "pck:klee/powers/aura_pyro.png" in ids
    assert "pck:klee/powers/aura_hydro.png" in ids
    # Attributed, so NOT stale...
    assert not [f for f in checks(led, "STALE-OUTPUT") if "aura_" in f.surface_id]
    # ...and the prefix is exposed so the report can say the set is unknown.
    assert "klee/powers/aura_" in led._pck_prefixes()


def test_json_ledger_is_machine_readable_and_carries_the_schema(root, tmp_path):
    import json
    out = tmp_path / "ledger.json"
    rc = art_ledger.main(["--root", str(root), "--json", str(out)])
    assert rc == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == art_ledger.SCHEMA_VERSION
    fields = set(data["rows"][0])
    assert {"surface_id", "kind", "owner", "expected_by", "source",
            "rendered_output", "rendered_present", "packed_path",
            "packed_present", "fallback", "rights_tier", "rights_evidence",
            "review_state", "status"} <= fields


def test_strict_exits_nonzero_on_a_defect(root, capsys):
    contract = root / "klee-mod/assets/klee.pck.contract.txt"
    contract.write_text(
        "\n".join(l for l in contract.read_text(encoding="utf-8").splitlines()
                  if "only_in_source" not in l) + "\n", encoding="utf-8")
    assert art_ledger.main(["--root", str(root), "--strict"]) == 1
    assert art_ledger.main(["--root", str(root)]) == 0


def test_root_is_required(root):
    """The art tree is gitignored, so the tool must never silently read its
    own checkout and report an empty bill as a clean one."""
    proc = subprocess.run(
        [sys.executable, str(REPO / "tools" / "art_ledger.py")],
        capture_output=True, text=True)
    assert proc.returncode != 0
    assert "--root" in proc.stderr


def test_report_renders_without_an_art_tree(tmp_path):
    """A worktree with no ImageGen/ at all must still produce a report --
    that is the normal state of every lane worktree and of CI."""
    root = make_root(tmp_path)
    import shutil
    shutil.rmtree(root / "ImageGen")
    import io
    buf = io.StringIO()
    art_ledger.report(art_ledger.Ledger(root), out=buf)
    text = buf.getvalue()
    assert "ART LEDGER" in text
    assert "RIGHTS COVERAGE" in text


# ---------------------------------------------------------------------------
# Rot guards against the real repo (skipped where the file is absent)
# ---------------------------------------------------------------------------

def test_pck_source_map_rules_are_still_in_the_build_script():
    """The res:// -> ImageGen map is derived from build_pck.ps1's copy blocks.
    If a block moves, the map silently starts pointing at nothing -- so each
    non-obvious rule pins the substring that proves it."""
    build = REPO / "tools" / "build_pck.ps1"
    if not build.is_file():
        pytest.skip("no build_pck.ps1 in this checkout")
    text = build.read_text(encoding="utf-8", errors="replace")
    for prefix, evidence in art_ledger.PCK_SOURCE_RULE_EVIDENCE.items():
        assert evidence in text, (
            f"PCK_SOURCE_RULES maps {prefix} through '{evidence}', which no "
            f"longer appears in tools/build_pck.ps1")


def test_card_universe_matches_art_coverage_on_this_repo():
    """art_ledger and art_coverage must bill the SAME card universe, or the
    reconciliation block in the report is decoration."""
    import art_coverage
    led = art_ledger.Ledger(REPO)
    expected, _covered, _missing = led.card_totals()

    ledger_ids = {r.surface_id.rsplit(":", 1)[1]
                  for r in led.rows if r.kind == "card"}
    coverage_ids = set()
    for path, _outdir, _label in art_coverage.SHEETS:
        coverage_ids |= {r["id"] for r in art_coverage.sheet_rows(path)}
    coverage_ids |= {r["id"] for r in art_coverage.token_rows(art_coverage.TOKENS)}
    coverage_ids |= set(art_coverage.mod_art_keys())

    assert ledger_ids == coverage_ids
    assert expected == len(coverage_ids)
