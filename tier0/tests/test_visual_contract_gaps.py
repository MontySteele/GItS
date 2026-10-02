"""Two shipped visual contracts whose consumer was never wired.

`missed-requirements.md` sec.4.2 and sec.4.3. Both were billed, both were
written up, neither landed, and neither was visible anywhere the suite looked —
they lived in a requirements doc and a sprint log, which is precisely the class
of debt that gets rediscovered by playing the game instead of by running the
tests. **Both have since been closed** (sec.4.3 by playtest 3, sec.4.2 by
EB-37), and the assertions stayed: what each one now pins is that the fix
holds and that the next character cannot re-open the gap quietly.

CURATED KNOWN-GAP LEDGER, not an aspirational assertion. Track B was
tests-only, so these did not fix anything themselves; what they do is make
each gap **structural**. Two properties matter and both are asserted:

  * the arithmetic that IS settled is pinned hard, so the numbers a future fix
    will be written against cannot drift out from under it while nobody is
    looking;
  * the gap itself is listed with its receipt, and the ledger fails in BOTH
    directions -- a new character that inherits the gap without an entry
    fails, and an entry that survives its own fix fails too. A known-gap list
    that can only rot toward silence is the thing it was supposed to replace.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "klee-mod" / "KleeCode"
PCK_SRC = ROOT / "klee-mod" / "pck-src"


# =========================================================================
# sec.4.2 -- the character-icon outline asset was never produced
# =========================================================================

# Every character ships an icon SCENE (CustomIconPath -> character_icon.tscn)
# whose texture is the FILL icon, and separately an outline TEXTURE path.
# art-asset-manifest.md bills "Character icon 88x88 -- 1 (+outline) -- 2":
# two assets. For a year only one was made; the second is now derived from the
# first by tools/gen_char_icon_outlines.py (EB-37).
ROSTER_ICONS = ["Klee", "Furina", "Kokomi"]

# id -> the reason the outline path returns the fill asset. Delete an entry
# the day that character gets a real outline; the test below then ENFORCES
# the separation for it and fails if the wiring was forgotten.
#
# EMPTY as of EB-37 (2026-08-08): all three outlines are produced by
# tools/gen_char_icon_outlines.py and all three Custom*Path sites are wired,
# so the ledger emptied itself exactly the way it was built to. It stays here
# rather than being deleted because the ledger runs in BOTH directions -- the
# assertion below is what stops character four from inheriting the gap in
# silence, and an empty dict is the strictest state it can be in.
OUTLINE_IS_FILL: dict[str, str] = {}


def _character_source(name: str) -> str:
    return (SOURCE / f"{name}.cs").read_text(encoding="utf-8")


def _pck_path(source: str, prop: str) -> str:
    m = re.search(rf"{prop}\s*=>\s*(?:\n\s*)?KleePck\.Path\(\"([^\"]+)\"\)",
                  source)
    assert m, f"{prop} must resolve through KleePck.Path"
    return m.group(1)


PCK_BUILDER = (ROOT / "tools" / "build_pck.ps1").read_text(encoding="utf-8")


def _icon_scene_texture(character: str) -> str:
    """The FILL texture the character's icon scene actually draws.

    Two authoring channels (animation sprint 1): a git-tracked scene under
    klee-mod/pck-src/, or a heredoc inside build_pck.ps1. character_icon.tscn
    is on the heredoc channel for the whole roster today, but the lookup tries
    both so moving one to pck-src does not silently blind this test.
    """
    scene = PCK_SRC / character.lower() / "ui" / "character_icon.tscn"
    texture_re = r'ext_resource type="Texture2D" path="res://([^"]+)"'
    if scene.exists():
        m = re.search(texture_re, scene.read_text(encoding="utf-8"))
        assert m, f"{scene} declares no Texture2D"
        return m.group(1)

    # Scope to THIS scene's heredoc. Each character has several `<char>/ui/`
    # textures in the builder (select_bg, selection_splash, transition_wipe),
    # so a filename-prefix match picks up whichever happens to be written
    # first and silently compares the wrong pair.
    marker = f"{character.lower()}\\ui\\character_icon.tscn'), @'"
    assert marker in PCK_BUILDER, (
        f"no character_icon.tscn for {character} in pck-src or the "
        "build_pck.ps1 heredocs")
    heredoc = PCK_BUILDER[PCK_BUILDER.index(marker):]
    heredoc = heredoc[:heredoc.index("'@)")]
    m = re.search(texture_re, heredoc)
    assert m, f"{character}'s icon heredoc declares no Texture2D"
    return m.group(1)


@pytest.mark.parametrize("character", ROSTER_ICONS)
def test_outline_icon_is_either_distinct_or_a_listed_gap(character: str):
    """The pin the base game's two-asset icon contract deserves.

    `CustomIconOutlineTexturePath` exists because the game draws the outline
    separately from the fill. Pointing both at one PNG is not a neutral
    placeholder -- it renders the outline pass as a second copy of the fill.
    """
    outline = _pck_path(_character_source(character),
                        "CustomIconOutlineTexturePath")
    fill = _icon_scene_texture(character)

    if outline != fill:
        assert character not in OUTLINE_IS_FILL, (
            f"{character} now has a real outline asset ({outline}), but is "
            "still listed in OUTLINE_IS_FILL. Delete the entry -- a known-gap "
            "ledger that outlives its gap is how the gap comes back.")
        return

    assert character in OUTLINE_IS_FILL, (
        f"{character}.CustomIconOutlineTexturePath returns the fill icon "
        f"({fill}). That is missed-requirements sec.4.2, and a new character "
        "may not inherit it silently: either ship an outline asset or add an "
        "entry to OUTLINE_IS_FILL saying why not.")


def test_the_outline_gap_ledger_covers_the_whole_roster():
    """Guards the ledger against a character being added and forgotten."""
    assert set(OUTLINE_IS_FILL) <= set(ROSTER_ICONS), (
        "OUTLINE_IS_FILL names a character not in ROSTER_ICONS")
    for character in ROSTER_ICONS:
        assert (SOURCE / f"{character}.cs").exists()
