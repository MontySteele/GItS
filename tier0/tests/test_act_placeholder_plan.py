"""The act-1 dressings' asset sets: one producer, one contract, one shape.

Three things can drift apart here and each is silent on its own:

  * the generator can write a file nobody packages;
  * the pck contract can claim a row nothing produces;
  * a committed `.tscn` under `klee-mod/pck-src/scenes` can be hand-edited
    away from what `tools/gen_act_placeholders.py` would write, so the next
    run of the generator quietly reverts someone's fix.

The failure mode for all three is a run that rolls Mondstadt and throws out of
`BackgroundAssets`'s constructor on its first combat -- a deploy question, and
the whole point of this file is that it is asked headlessly instead.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import gen_act_placeholders as gen              # noqa: E402
from tools.visual_qa import contract                        # noqa: E402

FIXTURE = ROOT / "tools" / "visual_qa" / "fixtures" / "sample.contract.txt"
BUILD_PCK = ROOT / "tools" / "build_pck.ps1"


def act_rows(resources: set[str]) -> set[str]:
    """The contract rows that belong to a dressing, by prefix.

    Prefix and not "everything the generator lists", because the question is
    whether the CONTRACT carries a row nothing produces as much as the other
    way round -- comparing a set against itself would answer neither.
    """
    prefixes = tuple(
        f"{p}{nation.id}" for nation in gen.NATIONS
        for p in ("scenes/backgrounds/", "scenes/rest_site/",
                  "teyvat/backgrounds/", "teyvat/rest_site/",
                  "images/packed/map/map_bgs/")
    )
    return {r for r in resources if r.startswith(prefixes)}


def test_the_plan_and_the_contract_fixture_name_the_same_files():
    parsed = contract.parse(FIXTURE.read_text(encoding="utf-8"))
    planned = {row.res[len("res://"):] for row in gen.plan()}
    assert planned == act_rows(parsed.resource_set)


def test_each_dressing_carries_the_whole_set():
    """Eighteen rows a nation, and the split is the engine's, not a taste."""
    for nation in gen.NATIONS:
        rows = [r.repo for r in gen.plan() if f"/{nation.id}/" in r.repo
                or f"/{nation.id}_" in r.repo]
        assert len(rows) == 18, (nation.id, rows)

        # `BackgroundAssets` groups by `_bg_NN` and draws one per group, then
        # once over the `_fg_` list -- so the GROUP COUNT is what keeps a
        # dressing's rng consumption equal to the zone it stands beside.
        layers = [r for r in rows if "/layers/" in r]
        assert len(layers) == gen.BG_GROUPS + 1
        assert sum(1 for r in layers if "_fg_" in r) == 1

        # The three map plates, at the engine's own non-negotiable path.
        maps = [r for r in rows if "map_bgs" in r]
        assert len(maps) == 3

        assert sum(1 for r in rows if r.endswith("_background.tscn")) == 1
        assert sum(1 for r in rows if r.endswith("_rest_site.tscn")) == 1


def test_every_committed_scene_matches_the_generator():
    problems = [p for p in gen.check(ROOT) if not p.startswith("missing placeholder texture")]
    assert problems == [], "\n".join(problems)


def test_the_committed_scenes_carry_no_script_and_the_right_nodes():
    sources = gen.scene_sources()
    for relative, text in sources.items():
        # A mod pck cannot carry a script resource, and the game's own
        # NCombatBackground.cs is not ours to reference (SD-SCRIPT).
        assert 'type="Script"' not in text, relative

    for nation in gen.NATIONS:
        root = sources[
            f"klee-mod/pck-src/scenes/backgrounds/{nation.id}/"
            f"{nation.id}_background.tscn"]
        # `NCombatBackground.AddLayer` throws on a missing slot; five plus the
        # foreground, matching KleeCode/Teyvat/NCombatBackgroundFactory.cs.
        for index in range(gen.BG_GROUPS):
            assert f'name="Layer_{index:02d}"' in root
        assert 'name="Foreground"' in root

        rest = sources[
            f"klee-mod/pck-src/scenes/rest_site/{nation.id}_rest_site.tscn"]
        # `NRestSiteRoom._Ready` fetches this one with GetNode, not
        # GetNodeOrNull, so its absence throws before the campfire is drawn.
        assert 'name="RestSiteLighting"' in rest
        assert "unique_name_in_owner = true" in rest


def test_build_pck_names_every_dressing_in_its_copy_loop():
    r"""A face the copy loop does not name gets no plates in the pack at all.

    The per-directory check below cannot see this: the directories are
    interpolated (`teyvat\backgrounds\$dressing`), so its leading segments are
    present whatever the loop iterates. This is the assertion that a new face
    costs a word in the script.
    """
    script = BUILD_PCK.read_text(encoding="utf-8")
    for nation in gen.NATIONS:
        assert f"'{nation.id}'" in script, nation.id


def test_the_six_faces_are_two_per_act():
    """R273 layout 1, as a shape rather than as a list of names.

    Act 1's pair dresses two base zones and acts 2 and 3 dress one each, but
    the GENERATOR sees none of that -- the pin is only that the arm ships six
    faces, so this file fails loudly if one is dropped or a seventh is added
    without the C# side moving too.
    """
    assert len(gen.NATIONS) == 6
    assert len({n.id for n in gen.NATIONS}) == 6
    assert [n.entry for n in gen.NATIONS] == [n.id.upper() for n in gen.NATIONS]


def project_godot_text() -> str:
    """The `project.godot` heredoc `tools/build_pck.ps1` writes for the export.

    Sliced out rather than grepped for, because the setting below is only
    load-bearing INSIDE this heredoc: the same line sitting in a comment, or in
    the `export_presets.cfg` heredoc next door, changes nothing about the pack.
    """
    script = BUILD_PCK.read_text(encoding="utf-8")
    opening = "'project.godot'), @'"
    start = script.index(opening) + len(opening)
    return script[start:script.index("'@)", start)]


def test_the_export_ships_text_scenes_as_text():
    r"""The layer scenes must reach the pack as `.tscn`, not `.tscn.remap`.

    `editor/export/convert_text_resources_to_binary` is a PROJECT SETTING read
    by Godot's exporter, and it defaults to TRUE: every `.tscn` is then packed
    as a binary `.scn` plus a `<name>.tscn.remap` stub at the original path.

    `ResourceLoader` follows a remap transparently, so a scene reached BY NAME
    still loads -- the background root and the still portraits never noticed.
    `Rooms/BackgroundAssets`'s constructor does not use `ResourceLoader`: it
    `DirAccess.Open`s `res://scenes/backgrounds/<id>/layers` and takes each
    `GetNext()` filename VERBATIM. With remaps it therefore builds
    `.../<id>_bg_00_a.tscn.remap`, a path no loader recognizes;
    `NCombatBackground.AddLayer`'s `GetScene` throws inside
    `CombatManager.SetUpCombat` and combat never starts. That is the blocking
    defect of `git show ecfa839d:review/records/teyvat-proofs-3-2026-09-15.md`.

    The base game's own pack settles what correct looks like: 173 raw
    `scenes/backgrounds/*/layers/*.tscn` entries and zero `.tscn.remap` (its
    only remaps are `.gd.remap`, and this pack ships no scripts at all).
    """
    project = project_godot_text()
    assert "[editor]" in project
    assert "export/convert_text_resources_to_binary=false" in project

    # Not true by construction: the value is the whole point, and `true` here
    # reinstates the defect exactly.
    assert "export/convert_text_resources_to_binary=true" not in project


def test_no_contract_row_is_a_remap_stub():
    """The contract names what the pack must hold, and a stub is never it.

    The contract is derived from the work directory, so it has always listed
    `...liyue_bg_00_a.tscn` -- while the shipped pack held
    `...liyue_bg_00_a.tscn.remap`. Nothing compares the contract to the pack's
    actual entries, which is why that divergence was silent for a whole build.
    This is the half of it that CAN be asked headlessly.
    """
    parsed = contract.parse(FIXTURE.read_text(encoding="utf-8"))
    assert [r for r in parsed.resource_set if r.endswith(".remap")] == []

    planned = {row.res for row in gen.plan()}
    scenes = {r for r in planned if r.endswith(".tscn")}
    assert scenes, planned
    assert not any(r.endswith(".remap") for r in planned)


def test_build_pck_copies_every_directory_the_generator_writes():
    """A produced texture with no copy block never reaches the pack."""
    script = BUILD_PCK.read_text(encoding="utf-8")
    directories = {
        Path(row.repo).parent.as_posix()[len("ImageGen/images/"):]
        for row in gen.plan() if row.kind == "png"
    }
    for directory in sorted(directories):
        # The script writes Windows separators and interpolates the dressing
        # in its own loop, so the check is on the stable leading segments.
        head = directory.split("/")[0:2]
        assert "\\".join(head) in script, (directory, head)


# --------------------------------------------------------------------------
# One producer per out-path: art/plan.tsv vs the generator (2026-09-17)
# --------------------------------------------------------------------------

def test_the_bill_claims_every_dressings_five_real_surfaces():
    """Thirty rows, and they are the five surfaces a dressing actually shows.

    The other thirteen files a dressing owns are scenes and the four layers
    plus the foreground over `bg_00` -- nothing a picture can be picked for.
    """
    owned = gen.plan_owned()
    assert len(owned) == 30, sorted(owned)
    for nation in gen.NATIONS:
        i = nation.id
        assert {
            f"ImageGen/images/teyvat/backgrounds/{i}/{i}_bg_00.png",
            f"ImageGen/images/teyvat/rest_site/{i}_rest_site_bg.png",
            f"ImageGen/images/teyvat/map_bgs/{i}/map_top_{i}.png",
            f"ImageGen/images/teyvat/map_bgs/{i}/map_middle_{i}.png",
            f"ImageGen/images/teyvat/map_bgs/{i}/map_bottom_{i}.png",
        } <= owned, i


def test_the_generator_never_writes_what_the_bill_produces(tmp_path):
    """The reconciliation, measured rather than asserted about.

    Two producers for one path means whichever runs last wins -- the defect
    art_lint's L11 exists to stop, and the one that would have painted a
    nation-tinted gradient over a fetched landscape on the next `--check`
    repair run.
    """
    written = set(gen.write_all(tmp_path))
    owned = gen.plan_owned()
    assert not (written & owned), sorted(written & owned)
    for relative in sorted(owned):
        assert not (tmp_path / relative).exists(), relative


def test_a_layer_over_a_real_background_is_transparent(tmp_path):
    """bg_01..04 and the foreground must not hide the landscape on bg_00.

    `NCombatBackground` stacks Layer_00..Layer_04 and the foreground over one
    another, so the only correct plate over a real far layer is one that draws
    nothing at all.
    """
    from PIL import Image

    gen.write_all(tmp_path)
    owned = gen.plan_owned()
    for nation in gen.NATIONS:
        i = nation.id
        if f"ImageGen/images/teyvat/backgrounds/{i}/{i}_bg_00.png" not in owned:
            continue
        for name in [f"{i}_bg_{n:02d}" for n in range(1, gen.BG_GROUPS)] + [f"{i}_fg"]:
            path = tmp_path / f"ImageGen/images/teyvat/backgrounds/{i}/{name}.png"
            with Image.open(path) as img:
                assert img.size == gen.LAYER_PNG, (name, img.size)
                assert img.convert("RGBA").getchannel("A").getextrema() == (0, 0), name


def test_the_check_gate_does_not_demand_a_plate_it_stopped_producing(tmp_path):
    """`--check` on a fresh tree must report only the files it owns.

    Otherwise the staleness gate fails for a reason running the generator
    cannot fix, which is the same as having no gate.
    """
    gen.write_all(tmp_path)
    missing = [p for p in gen.check(tmp_path)
               if p.startswith("missing placeholder texture")]
    assert missing == [], "\n".join(missing)


def test_every_bill_row_has_a_ledger_row():
    """media/ACT.tsv records what art/plan.tsv produces (media.md sec.1)."""
    ledger = ROOT / "media" / "ACT.tsv"
    with ledger.open("r", encoding="utf-8", newline="") as handle:
        lines = [line.rstrip("\r\n") for line in handle if line.strip()]
    header = lines[0].split("\t")
    assert header == ["out", "raw", "dressing", "surface", "w", "h",
                      "title", "origin", "licence", "notes"], header
    rows = [dict(zip(header, line.split("\t"))) for line in lines[1:]]
    outs = [r["out"] for r in rows]
    assert len(outs) == len(set(outs)), "an out-path is recorded twice"
    assert set(outs) == gen.plan_owned()
    for row in rows:
        # The pre-public pass is `grep PLACEHOLDER-COPYRIGHTED media/*.tsv`,
        # and a row that forgets the column would pass it silently.
        assert row["licence"] == "PLACEHOLDER-COPYRIGHTED", row["out"]
        assert row["origin"].startswith(
            "https://genshin-impact.fandom.com/wiki/File:"), row["out"]
        assert row["surface"] in {"bg_00", "rest_site", "map_top",
                                  "map_middle", "map_bottom"}, row["surface"]


# --------------------------------------------------------------------------
# The combat feet line: a bg_00 plate is registered, not framed (2026-09-17)
# --------------------------------------------------------------------------

def test_ground_focus_lands_the_named_row_on_the_feet_line():
    """A synthetic source with a known ground row lands it on the feet line.

    The whole `ground` focus is this one sentence, so the pin is a picture
    whose ground row is unambiguous rather than a re-statement of the formula:
    black above source row 756 (0.70 of 1080), white below it, and the seam
    must come out of the crop on COMBAT_FEET_ROW.
    """
    from PIL import Image

    from tools.art_process import COMBAT_FEET_ROW, cover

    source = Image.new("RGB", (1920, 1080), (0, 0, 0))
    source.paste(Image.new("RGB", (1920, 1080 - 756), (255, 255, 255)), (0, 756))
    plate = cover(source, 1382, 648, "ground0.70@1.32").convert("L")
    column = [plate.getpixel((691, y)) for y in range(648)]
    seam = next(y for y, v in enumerate(column) if v > 128)
    assert abs(seam - COMBAT_FEET_ROW) <= 1, seam


def test_ground_focus_flags_a_source_that_cannot_reach():
    """A clamped ground row is the defect this focus exists to catch.

    Under plain `cover` a 16:9 source has 130 scaled pixels of slack, so a
    ground row near the bottom edge is simply unreachable without a zoom. The
    wrong answer is to clamp and say nothing -- that is `top` again, wearing a
    new spelling.
    """
    from PIL import Image

    from tools import art_process

    art_process.flags.clear()
    try:
        art_process.cover(Image.new("RGB", (1920, 1080)), 1382, 648, "ground0.98")
        assert any("clamped" in f for f in art_process.flags), art_process.flags
    finally:
        art_process.flags.clear()


def test_the_legacy_focus_spellings_are_untouched():
    """`top` / `center` / `x<f>` must not move because `ground` was added.

    `_ground` returns None for every one of them, and shipped Klee art depends
    on that: the thirty map and rest-site rows still run under `x0.42`.
    """
    from PIL import Image

    from tools.art_process import cover

    source = Image.new("RGB", (1920, 1080), (0, 0, 0))
    # 60 source rows of white: 43 rows once scaled to cover, so the band
    # survives `top` whole and falls entirely above `center`'s 64-row offset.
    source.paste(Image.new("RGB", (1920, 60), (255, 255, 255)), (0, 0))
    top = cover(source, 1382, 648, "top").convert("L")
    assert top.getpixel((691, 0)) > 128          # the white band is kept
    centre = cover(source, 1382, 648, "center").convert("L")
    assert centre.getpixel((691, 0)) < 128       # the middle is not


def test_the_zoom_runs_to_the_next_comma_not_to_the_end():
    """`ground0.70@1.32,x0.46` must parse, and legacy `center@1.5` must too.

    `cover` used to take everything after the `@` as the zoom, which was
    invisible for as long as every spelling put the zoom last. The first focus
    that did not -- the combined ground-and-anchor one the six bg_00 rows use
    -- sent `float("1.32,x0.46")` into a ValueError, and the run wrote a plate
    off a fallback path instead of failing loudly.
    """
    from PIL import Image

    from tools.art_process import COMBAT_FEET_ROW, cover

    source = Image.new("RGB", (1920, 1080), (0, 0, 0))
    source.paste(Image.new("RGB", (1920, 1080 - 756), (255, 255, 255)), (0, 756))
    plate = cover(source, 1382, 648, "ground0.70@1.32,x0.46").convert("L")
    column = [plate.getpixel((691, y)) for y in range(648)]
    assert abs(next(y for y, v in enumerate(column) if v > 128)
               - COMBAT_FEET_ROW) <= 1
    # And the anchor half really reached the crop: x0.46 shifts it left of
    # centre, which is what keeps the wordmark out now that `top` cannot.
    marked = Image.new("RGB", (1920, 1080), (0, 0, 0))
    marked.paste(Image.new("RGB", (400, 1080), (255, 255, 255)), (1520, 0))
    def brightness(focus):
        strip = cover(marked, 1382, 648, focus).convert("L").resize((1382, 1))
        return sum(strip.getpixel((x, 0)) for x in range(1382))

    white = [brightness("ground0.70@1.32"), brightness("ground0.70@1.32,x0.46")]
    assert white[1] < white[0], white

    # The legacy spelling, unchanged: the zoom is the whole tail when there is
    # no comma after it.
    assert cover(source, 1382, 648, "center@1.5").size == (1382, 648)
    assert cover(source, 1382, 648, "x0.3,y0.4@1.2").size == (1382, 648)


def test_every_bg_00_row_is_registered_to_the_feet_line():
    """The six combat plates answer to `ground`, and only they do.

    A rest-site or map plate has no creature standing on it, so it keeps the
    wordmark rule (`top`, `x0.42`) and must NOT acquire a feet line.
    """
    from tools.art_fetch import read_plan

    rows = [r for r in read_plan() if r["asset_id"].startswith("act_")]
    combat = [r for r in rows if r["asset_id"].startswith("act_bg_00_")]
    assert len(combat) == 6, [r["asset_id"] for r in combat]
    for row in combat:
        assert row["focus"].startswith("ground"), row["asset_id"]
        # The zoom is what buys the reach, and the x anchor is what keeps the
        # GENSHIN IMPACT wordmark out now that `top` no longer can.
        assert "@" in row["focus"] and ",x" in row["focus"], row["focus"]
    for row in rows:
        if row not in combat:
            assert not row["focus"].startswith("ground"), row["asset_id"]
