"""EB-89: the prose half of constant parity, red and green.

`lint_constant_parity` compares constants to constants. The number a player
is SHOWN is prose, and prose is outside every gate this repo owns -- which is
how `EB-86` found `SalonMemberPower.Localization` printing the salon numbers
as string literals while `SalonMemberTips` interpolated the same constants
for the same copy. `tools/lint_prose_constants.py` is the gate for that
hazard class, and this file is its red half.

The tests below are built on a SYNTHETIC mod (a temp directory of two .cs
files) rather than on the shipped source, for the reason every lint test in
this repo is: a lint whose red half is "the codebase today" goes green the
moment someone fixes the finding and then proves nothing forever. The last
test is the green half -- the shipped mod, which must stay clean.
"""
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

from tools import lint_constant_parity as cp        # noqa: E402
from tools import lint_prose_constants as lint      # noqa: E402


CONSTANTS_CS = """
namespace Fake.Elements;

public static class ReactionConstants
{
    public const int ShatterDamage = 6;
    public const int AuraDurationTurns = 2;
}

public static class SalonConstants
{
    public const int CrabalettaTick = 6;
}
"""


def _mod(tmp_path: Path, *sources: str) -> Path:
    """A synthetic KleeCode tree: the constants file plus caller-supplied
    prose files."""
    root = tmp_path / "KleeCode"
    (root / "Powers").mkdir(parents=True)
    (root / "Powers" / "Constants.cs").write_text(CONSTANTS_CS,
                                                  encoding="utf-8")
    for i, text in enumerate(sources):
        (root / "Powers" / f"Prose{i}.cs").write_text(text, encoding="utf-8")
    return root


@pytest.fixture
def fake_mod(tmp_path, monkeypatch):
    """Point BOTH lints at the synthetic tree.

    `lint_prose_constants` reads its constants through
    `lint_constant_parity.collect()` on purpose -- the two agree by
    construction on what a named constant is -- so redirecting one root
    without the other would silently test the shipped constants against
    synthetic prose.
    """
    def _point(*sources: str) -> Path:
        root = _mod(tmp_path, *sources)
        monkeypatch.setattr(lint, "CS_ROOT", root)
        monkeypatch.setattr(cp, "CS_ROOT", root)
        monkeypatch.setattr(lint, "REPO", tmp_path)
        monkeypatch.setattr(lint, "ALLOWED", {})
        return root
    return _point


# --- RED: the hazard the row was filed for --------------------------------

def test_a_hand_typed_numeral_matching_a_constant_is_a_finding(fake_mod):
    """EB-89's acceptance, executable."""
    fake_mod('''
public sealed class FrozenPower
{
    public List<(string, string)>? Localization => new()
    {
        ("description",
            "Its next action deals half damage; attacking it Shatters for 6 damage."),
    };
}
''')
    findings = lint.prose_findings()
    assert [f.const for f in findings] == ["ReactionConstants.ShatterDamage"]
    assert findings[0].numeral == "6"
    assert "shatter" in findings[0].shared


def test_interpolating_the_constant_clears_the_finding(fake_mod):
    """The green half of the same site: the fix the lint asks for is the fix
    that satisfies it."""
    fake_mod('''
public sealed class FrozenPower
{
    public List<(string, string)>? Localization => new()
    {
        ("description",
            $"Its next action deals half damage; attacking it Shatters for "
          + $"{ReactionConstants.ShatterDamage} damage."),
    };
}
''')
    assert lint.prose_findings() == []


def test_two_shared_words_carry_a_common_word_match(fake_mod):
    """`AuraDurationTurns` against "applies Pyro for 2 turns": `turns` alone
    is too common to carry a match, and `aura` + `turns` together are not."""
    fake_mod('''
public sealed class AuraTip
{
    public List<(string, string)>? Localization => new()
    {
        ("description",
            "If the target has no aura, this applies Pyro for 2 turns."),
    };
}
''')
    assert [f.const for f in lint.prose_findings()] == [
        "ReactionConstants.AuraDurationTurns"]


# --- the noise controls, each one pinned ----------------------------------

def test_a_word_the_prose_uses_constantly_cannot_carry_a_lone_match(fake_mod):
    """The tuning that made this lint usable. `CrabalettaTick` is 6 and so is
    `ShatterDamage`; "deal 6 damage" joins the first through nothing and the
    second only through `damage`, which every card face in the corpus uses.
    Value equality alone produced ~74 hits on the shipped mod, of which a
    handful were real."""
    fake_mod('''
public sealed class Face
{
    public List<(string, string)>? Localization => new()
    {
        ("a", "Deal 6 damage to ALL enemies."),
        ("b", "Deal damage equal to your Block."),
        ("c", "Gain Block and deal damage twice."),
    };
}
''')
    assert lint.prose_findings() == []


def test_a_placeholder_numeral_is_not_hand_typed(fake_mod):
    """`{0}` is a format hole and `{Slots}` is a DynamicVar token; neither is
    a numeral a repricing could strand, and both would otherwise match."""
    fake_mod('''
public sealed class Tokens
{
    public List<(string, string)>? Localization => new()
    {
        ("a", "Shatters for {0} damage, up to {Slots} aura turns."),
    };
}
''')
    assert lint.prose_findings() == []


def test_a_comment_quoting_an_old_number_is_not_displayed(fake_mod):
    """Prose ABOUT code is not prose shown to anyone. A doc comment that
    still says 6 is a stale comment, not a lying tooltip."""
    fake_mod('''
public sealed class Documented
{
    /// <summary>Shatters for 6 damage (see ReactionConstants).</summary>
    // Shatters for 6 damage.
    public int Amount => ReactionConstants.ShatterDamage;
}
''')
    assert lint.prose_findings() == []


def test_a_key_or_a_path_is_not_prose(fake_mod):
    fake_mod('''
public sealed class Keys
{
    public const string K = "KLEEMOD-SHATTER_6.description";
    public Texture2D T => Load("res://klee/art/shatter 6 damage.png");
}
''')
    assert lint.prose_findings() == []


def test_a_stale_allowlist_entry_is_itself_a_finding(fake_mod, monkeypatch):
    """The allowlist cannot outlive what it excuses: an entry whose site is
    gone is reported, so the curated reasons stay true."""
    root = fake_mod('''
public sealed class Clean
{
    public List<(string, string)>? Localization => new()
    {
        ("a", "Nothing here quotes a constant at all."),
    };
}
''')
    assert root.exists()
    monkeypatch.setattr(lint, "ALLOWED", {
        ("Powers/Gone.cs", "ReactionConstants.ShatterDamage", "6"):
            "a site that no longer exists",
    })
    assert lint.main([]) == 1


def test_the_lint_refuses_to_pass_on_an_empty_tree(fake_mod, monkeypatch,
                                                   tmp_path):
    """A gate that passes because it read nothing is not a gate -- the same
    guard `lint_constant_parity` carries."""
    fake_mod("")
    monkeypatch.setattr(lint, "CS_ROOT", tmp_path / "nothing-here")
    assert lint.main([]) == 1


# --- GREEN: the shipped mod ------------------------------------------------

def test_the_shipped_mod_is_clean():
    """Run as a subprocess so this is the same invocation CI and
    `run_lints.py --lane ci` make, exit code included."""
    res = subprocess.run(
        [sys.executable, str(REPO / "tools" / "lint_prose_constants.py")],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
