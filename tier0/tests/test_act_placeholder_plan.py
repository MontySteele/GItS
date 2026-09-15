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
