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
                  "teyvat/backgrounds/", "teyvat/rest_site/")
    )
    return {r for r in resources if r.startswith(prefixes)}


def test_the_plan_and_the_contract_fixture_name_the_same_files():
    parsed = contract.parse(FIXTURE.read_text(encoding="utf-8"))
    planned = {row.res[len("res://"):] for row in gen.plan()}
    assert planned == act_rows(parsed.resource_set)


def test_each_dressing_carries_the_whole_set():
    """Fourteen rows a nation, and the split is the engine's, not a taste.

    It was eighteen until 2026-09-17, and the day took four rows off it in two
    unrelated fixes:

      * the three MAP plates left, because the face's map ground is the base
        zone's again (`KleeCode/Teyvat/Patches/ActMapBgPathPatch.cs`) and the
        map's dressing is an overlay whose pictures are optional -- so nothing
        in THIS list, every row of which is a file whose absence throws,
        corresponds to them;
      * the rest-site SCENE left, and only its plate remains. See
        `test_no_dressing_ships_a_rest_site_scene` below for why.
    """
    for nation in gen.NATIONS:
        rows = [r.repo for r in gen.plan() if f"/{nation.id}/" in r.repo
                or f"/{nation.id}_" in r.repo]
        assert len(rows) == 14, (nation.id, rows)

        # `BackgroundAssets` groups by `_bg_NN` and draws one per group, then
        # once over the `_fg_` list -- so the GROUP COUNT is what keeps a
        # dressing's rng consumption equal to the zone it stands beside.
        layers = [r for r in rows if "/layers/" in r]
        assert len(layers) == gen.BG_GROUPS + 1
        assert sum(1 for r in layers if "_fg_" in r) == 1

        # And NO map plate: overriding the game's map ground is the thing
        # this generator stopped doing.
        assert [r for r in rows if "map_bgs" in r] == []

        assert sum(1 for r in rows if r.endswith("_background.tscn")) == 1

        # The rest-site PLATE, and no rest-site scene.
        assert sum(1 for r in rows if r.endswith("_rest_site_bg.png")) == 1
        assert sum(1 for r in rows if r.endswith("_rest_site.tscn")) == 0


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


def test_no_dressing_ships_a_rest_site_scene():
    r"""The rest-site scene is the game's, and ours is deleted (2026-09-17).

    We shipped one per face until [USER] took a BASE character -- the Silent --
    into her first campfire on a dressed act and the game HARD-CRASHED:
    native, no managed trace, the log ending at
    `Preloading 'RestSite Room' Complete`. Reproduced twice; Klee never crashed
    there, which is why every deploy proof missed it.

    Our scene was a `RestSiteBG` `TextureRect` plus an EMPTY
    `%RestSiteLighting` `Control` -- all `NRestSiteRoom._Ready`'s
    `GetNode<Control>("%RestSiteLighting")` asks for. The base game keeps the
    WHOLE campfire inside that node (ground-lighting particles, seven wall
    lights, `SteppedFire`, sparks, the log highlights) and a base character's
    campfire figure is a Spine rig whose `_Ready` reaches into it.

    So a face wears the base zone's ENTIRE rest scene -- the alias in
    `KleeCode/Teyvat/Patches/TeyvatRestSitePatch.cs` is unconditional, unlike
    the combat background's and the map's -- and only the PLATE is ours,
    swapped into that scene's own `RestSiteBG` by a postfix on
    `ActModel.CreateRestSiteBackground`. This pin is that nothing puts the
    scenes back: not the generator, not the contract, not a stray file.
    """
    assert not any(r.repo.startswith("klee-mod/pck-src/scenes/rest_site/")
                   for r in gen.plan())
    assert not any(k.startswith("klee-mod/pck-src/scenes/rest_site/")
                   for k in gen.scene_sources())

    directory = ROOT / "klee-mod" / "pck-src" / "scenes" / "rest_site"
    assert not directory.exists() or not list(directory.glob("*.tscn")), directory

    parsed = contract.parse(FIXTURE.read_text(encoding="utf-8"))
    assert not [r for r in parsed.resource_set
                if r.startswith("scenes/rest_site/")]

    # The plate is untouched: it is what the postfix writes into the base
    # scene, one a face, still produced and still contracted.
    plates = {r.res for r in gen.plan() if r.res.endswith("_rest_site_bg.png")}
    assert len(plates) == len(gen.NATIONS)


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

def test_the_bill_claims_every_dressings_four_real_surfaces():
    """Twenty-four rows: the four pictures a dressing actually shows.

    Thirty until 2026-09-17. The three map plates a face used to draw as its
    map GROUND are gone, and two overlay pictures drawn OVER the game's own
    ground replace them -- so the bill shrank by six rather than by eighteen.
    The other files a dressing owns are scenes and the four layers plus the
    foreground over `bg_00`: nothing a picture can be picked for.
    """
    owned = gen.plan_owned()
    assert len(owned) == 24, sorted(owned)
    for nation in gen.NATIONS:
        i = nation.id
        assert {
            f"ImageGen/images/teyvat/backgrounds/{i}/{i}_bg_00.png",
            f"ImageGen/images/teyvat/rest_site/{i}_rest_site_bg.png",
            f"ImageGen/images/teyvat/map/{i}_wordmark.png",
            f"ImageGen/images/teyvat/map/{i}_vignette.png",
        } <= owned, i
        assert not any(f"map_bgs/{i}/" in o for o in owned), i


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
        assert row["surface"] in {"bg_00", "rest_site",
                                  "map_wordmark", "map_vignette"}, row["surface"]
