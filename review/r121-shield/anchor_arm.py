"""Per-arm roster-anchor harness (R121 SHIELD re-measurement).

Byte-for-byte the wave-8 Track M harness quoted in
`docs/archive/v6-rebaseline-sweep-2026-08-06.md` §appendix, so the shielded
`ref_ironclad` reading is produced by the same body as the number it
replaces.

    python anchor_arm.py <repo_dir> <arm_index> <runs> <seed> <jobs> <out.json>
"""
import json
import sys


def main() -> int:
    repo, arm_index, runs, seed, jobs, out = sys.argv[1:7]
    sys.path.insert(0, repo)
    from tier05 import cells
    from tier05.exp_roster_anchors import ARMS

    character, archetype = ARMS[int(arm_index)]
    base = cells.CANONICAL.but(name="roster-anchors", runs=int(runs),
                               seed=int(seed), jobs=int(jobs))
    cell = base.but(character=character, archetype=archetype)
    a = cell.arm()
    results = a["results"]
    n = len(results)
    attained = [r for r in results if r.time_to_online is not None]
    row = {
        "character": character,
        "archetype": archetype,
        "stamp": cell.stamp(),
        "n": n,
        "win": a["win"],
        "act1": a["act1"],
        "acts": a["acts"],
        "deck": a["decksize"],
        "fights": a["fights"],
        "core_attain": len(attained) / n if n else 0.0,
        "tto": (sum(r.time_to_online for r in attained) / len(attained)
                if attained else None),
    }
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(row, fh, indent=2)
    print(json.dumps(row))
    return 0


if __name__ == "__main__":
    sys.exit(main())
