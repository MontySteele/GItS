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


# =========================================================================
# sec.4.3 -- the salon member sprite scale was written up and never applied
# =========================================================================

CUT_TOOL = (ROOT / "tools" / "cut_salon_members.py").read_text(encoding="utf-8")
SALON_STAGE = (PCK_SRC / "furina" / "ui" / "salon_stage.tscn").read_text(
    encoding="utf-8")
SALON_BRIDGE = (SOURCE / "Vfx" / "SalonVisualsBridge.cs").read_text(
    encoding="utf-8")

# Read from the TOOL, not from ImageGen/images/furina/salon/members.json --
# that file is gitignored Tier F output and absent on a fresh clone. Track A's
# lesson: an assertion anchored on an ungenerable artifact reports the machine.
TARGET_H = int(re.search(r"^TARGET_H\s*=\s*(\d+)", CUT_TOOL, re.M).group(1))


def _rect(node: str) -> tuple[float, float]:
    """(width, height) of a ColorRect declared in the stage scene."""
    block = SALON_STAGE[SALON_STAGE.index(f'name="{node}"'):]
    block = block[:block.index("\n[node") if "\n[node" in block else len(block)]
    vals = {k: float(v) for k, v in re.findall(
        r"offset_(left|top|right|bottom) = (-?[\d.]+)", block)}
    return vals["right"] - vals["left"], vals["bottom"] - vals["top"]


def _slot_positions() -> list[float]:
    return [float(x) for x, _ in re.findall(
        r'name="Slot\d" type="Node2D".*?position = Vector2\((-?[\d.]+), (-?[\d.]+)\)',
        SALON_STAGE, re.S)]


SCENE_SLOTS = 5


def test_the_stage_geometry_is_uniform_across_every_slot():
    """The numbers a scale fix will be written against, pinned first.

    D1 (salon UI sprint, 2026-07-28) took the slot count from three to five --
    A12 made the cap a per-player stat, and Casting Call upgraded reaches 5 --
    so the sweep is over every slot the scene ships, not over a hardcoded
    three. Uniformity is the actual invariant: a slot that renders a member
    differently from its neighbours would make identity a function of
    POSITION, which is precisely what the slot-index Funnel Contract forbids.
    """
    slots = range(1, SCENE_SLOTS + 1)
    ghosts = [_rect(f"Ghost{i}") for i in slots]
    pools = [_rect(f"Pool{i}") for i in slots]
    beams = [_rect(f"Beam{i}") for i in slots]
    chips = [_rect(f"Chip{i}") for i in slots]
    assert len(set(ghosts)) == 1, ghosts
    assert len(set(pools)) == 1, pools
    assert len(set(beams)) == 1, beams
    assert len(set(chips)) == 1, chips
    # The figures missed-requirements sec.4.3 quotes, so the write-up and the
    # scene cannot drift apart without one of them being wrong out loud.
    assert ghosts[0] == (34.0, 36.0), ghosts[0]
    assert len(_slot_positions()) == SCENE_SLOTS, _slot_positions()


def test_the_role_chip_and_the_tick_share_one_expression():
    """D1 §2 ruled that the chip reads "the same scaled path SalonPowers
    ticks with, so the chip can never disagree with the actual tick".

    That is only true while there is ONE expression. A bridge that recomputed
    the Focus term itself would agree today and drift the first time the
    scaling changes -- a fifth hand-maintained projection of arithmetic the
    sheet already has four of. So: the bridge must call TickValue, and it
    must not know how scaling is computed.
    """
    powers = (SOURCE / "Powers" / "SalonPowers.cs").read_text(encoding="utf-8")
    assert "public static int TickValue(" in powers
    upkeep = powers[powers.index("AfterPlayerTurnStart"):]
    upkeep = upkeep[:upkeep.index("TryModifyPowerAmountReceived")]
    assert "TickValue(" in upkeep, (
        "the upkeep loop no longer resolves through TickValue, so the chip "
        "is now reading an expression the tick does not use")
    assert "Scaled(" not in upkeep, (
        "the upkeep loop scales a number outside TickValue; whatever it is, "
        "the chip cannot see it")
    assert "SalonMemberPower.TickValue(" in SALON_BRIDGE
    for leak in ("FocusPerFanfare", "DryDamageMultiplier", "SalonDamageUp"):
        assert leak not in SALON_BRIDGE, (
            f"the bridge references {leak}: it is computing scaling rather "
            "than asking for the resolved tick")


def test_the_slot_row_is_laid_out_by_the_bridge_not_by_the_scene():
    """D1 §5: a cap raise must appear as a new ghost slot on a row that still
    fits inside Furina's 240-wide bounds, so X and Y come from the LIVE cap.

    The authored positions in the scene are therefore inert -- which is worth
    a test, because the old contract pinned them to a 62px pitch and reading
    that pin as still-load-bearing is how someone "fixes" a spacing bug in
    the wrong file. The spacing rule now lives in the bridge, and the cap on
    it is still 62 so a three-member stage is pixel-identical to the one that
    shipped.
    """
    # Twice: the definition AND a call site. Asserting the name alone passes
    # on a bridge that defines the layout and never runs it, which is the
    # defect this pins -- the row would silently fall back to the scene's
    # authored three positions.
    assert SALON_BRIDGE.count("LayOutSlots") >= 2, (
        "LayOutSlots is defined but never called; the slot row is back to "
        "whatever the scene authored")
    assert re.search(r"SlotSpacingMax\s*=\s*62f", SALON_BRIDGE), (
        "the shipped three-slot pitch is no longer the maximum gap; a normal "
        "Furina's stage would move for a reason that only applies to a "
        "cap raise")
    half = float(re.search(r"SlotHalfSpan\s*=\s*(-?[\d.]+)f",
                           SALON_BRIDGE).group(1))
    half_slot = _rect("Ghost1")[0] / 2
    # 96 is the stage arc's half-width (StageArc offset_right).
    assert half + half_slot <= 96.0, (
        f"a slot centred at {half} with half-width {half_slot} overhangs the "
        "stage arc, and the arc is already at the creature bounds edge")


def test_shipped_sprite_height_is_exactly_twice_the_stage_slot():
    """`TARGET_H = 144` is not free-floating: it is 2x the beam, deliberately.

    The tool says so in prose -- "the stage slots are ~72 px tall in creature
    space; 2x that gives headroom for the deploy pop without resampling
    artefacts". That sentence is the ONLY statement of the intended runtime
    scale (0.5), so it is asserted here rather than trusted.
    """
    _, beam_h = _rect("Beam1")
    assert beam_h == 72.0, beam_h
    assert TARGET_H == 2 * beam_h, (
        f"TARGET_H={TARGET_H} is no longer 2x the {beam_h}px stage slot; the "
        "house rule is pre-scaled art with no runtime minification, so this "
        "ratio IS the intended Sprite2D scale and cannot move silently")


def test_the_member_art_is_scaled_to_its_slot():
    """missed-requirements sec.4.3, CLOSED by playtest 3 (2026-07-28).

    The gap this replaces asserted the opposite: that the bridge set no
    Scale, so 121x144 art rendered at 1:1 into a 34x36 ghost on a 62px pitch
    and every member overlapped its neighbour by about half. The old test
    said, in as many words, that on the day a Scale is set it must be
    replaced with the arithmetic check below. This is that test.

    What forced it: A12 made the pitch a function of a per-player stat, and
    at cap 4-5 (39.5px) the overlap went from ugly to illegible -- "the salon
    pictures stacked over each other and became unreadable". So the old house
    rule of pre-scaled art with no runtime minification is amended, because
    there is no single size art could be cut at to serve a variable pitch.

    The CAP is still the documented ratio -- beam / TARGET_H -- so the
    ordinary three-member stage lands on a clean 2x downscale. Only a raised
    cap goes below it.
    """
    _, beam_h = _rect("Beam1")
    expected = beam_h / TARGET_H
    assert re.search(rf"SpriteScaleMax\s*=\s*{expected}f", SALON_BRIDGE), (
        f"the sprite scale cap is no longer {expected} (beam {beam_h}px / "
        f"TARGET_H {TARGET_H}); a stage of three members is no longer an "
        "exact 2x downscale of the master")
    assert re.search(r"sprite\.Scale\s*=", SALON_BRIDGE), (
        "the bridge stopped scaling member art; at cap 5 the sprites are "
        "three times the slot pitch and stack into an unreadable pile")
    # The cap alone is not enough: 121px of art at 0.5 is 60px wide, which
    # does not fit a 39.5px pitch. The scale must also answer to the pitch.
    assert "spacing / width" in SALON_BRIDGE, (
        "SpriteScale ignores the slot pitch, so a raised cap stacks the "
        "members again -- which is the defect playtest 3 reported")
