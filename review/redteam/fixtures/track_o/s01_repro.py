"""Track O slice 1 reproducers. Read-only: drives the instruments, changes none.

    python review/redteam/fixtures/track_o/s01_repro.py

Every block prints an OBSERVED line that is the defect. Nothing here launches
the game; the fixtures beside this file are ordinary soak JSONL.
"""

from __future__ import annotations

import json
import pathlib
import shutil
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from understudy import bridge, report, rng            # noqa: E402
from understudy import trace_replay as replay         # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent


def _logdir(pairs: list[tuple[str, str]]) -> pathlib.Path:
    tmp = pathlib.Path(tempfile.mkdtemp())
    for src, dst in pairs:
        shutil.copyfile(HERE / src, tmp / dst)
    report.LOG_DIR = tmp
    return tmp


def o_s01_1_unknown_seeds_compare_as_the_same_seed() -> None:
    print("\n[O-S01-1] two runs whose seed never read back")
    _logdir([("s01-nullseed-runA.jsonl", "soak-nA-run001.jsonl"),
             ("s01-nullseed-divergent-runB.jsonl", "soak-nB-run001.jsonl")])
    print("  seed_of A:", replay.seed_of("nA", 1))
    print("  findings :", [f.splitlines()[0] for f in
                           replay.compare_runs(("nA", 1), ("nB", 1))])
    print("  OBSERVED : the SEED guard never fires; two runs of unknown "
          "provenance are diffed field-by-field as if comparable.")


def o_s01_2_absent_run_logs_are_identical() -> None:
    print("\n[O-S01-2] an index naming runs whose logs were never written")
    tmp = _logdir([("s01-ghost-index.json", "soak-ghost-index.json"),
                   ("s01-ghost-index.json", "soak-ghost2-index.json")])
    replay.LOG_DIR = tmp
    print(replay.render_compare("ghost", "ghost2"))
    print("  OBSERVED : VERDICT identical traces over zero recorded fights.")


def o_s01_3_a_truncated_seed_line_is_dropped() -> None:
    print("\n[O-S01-3] a half-written seed_read_back line")
    _logdir([("s01-corrupt-seedline-runA.jsonl", "soak-cA-run001.jsonl")])
    raw = (HERE / "s01-corrupt-seedline-runA.jsonl").read_text(
        encoding="utf-8").splitlines()[0]
    print("  on disk  :", raw[:60], "...")
    print("  seed_of  :", replay.seed_of("cA", 1))
    print("  OBSERVED : the file names seed ABCDEFGHIJ; the reader reports "
          "None, with no warning, and O-S01-1 then applies.")


def o_s01_4_honoured_is_never_consulted() -> None:
    print("\n[O-S01-4] two runs that both failed to honour their seeds")
    tmp = pathlib.Path(tempfile.mkdtemp())
    report.LOG_DIR = replay.LOG_DIR = tmp
    fight = json.loads((HERE / "s01-nullseed-runA.jsonl").read_text(
        encoding="utf-8").splitlines()[1])
    for stamp, chosen in (("hA", "BBBBBBBBBB"), ("hB", "CCCCCCCCCC")):
        (tmp / f"soak-{stamp}-run001.jsonl").write_text("\n".join([
            json.dumps({"record": "seed_read_back", "seed": "AAAAAAAAAA",
                        "chosen": chosen, "honoured": False}),
            json.dumps(fight)]) + "\n", encoding="utf-8")
        (tmp / f"soak-{stamp}-index.json").write_text(
            json.dumps({"runs": [{"index": 1}]}), encoding="utf-8")
    print("  findings :", replay.compare_runs(("hA", 1), ("hB", 1)))
    print(" ", replay.render_compare("hA", "hB", 1).splitlines()[2])
    print("  OBSERVED : the printed line credits run A's chosen seed to a "
          "run that demonstrably did not get it, and never mentions B's.")


def o_s01_5_the_leak_guard_fails_open() -> None:
    print("\n[O-S01-5] policy_rng's game-seed guard")
    for label in ("SSRWEGLNRG", "ssrweglnrg", "p15bridge1", "1A2B3",
                  "SSRWEG-LNRG"):
        try:
            rng.policy_rng(label)
            print(f"  {label!r:>15} ACCEPTED")
        except rng.GameSeedLeak:
            print(f"  {label!r:>15} refused")
    print("  OBSERVED : the pre-canonical (lower-case) form of a seed, which "
          "is what --seed carries until the endpoint answers, is accepted.")


def o_s01_6_label_offsets_collide() -> None:
    print("\n[O-S01-6] two sub-policy labels, one stream")
    a, b = rng.policy_rng("boss"), rng.policy_rng("rest")
    print("  offsets  :", rng._label_offset("boss"), rng._label_offset("rest"))
    print("  same draw:", [a.random() for _ in range(3)]
          == [b.random() for _ in range(3)])
    print("  OBSERVED : 'boss' and 'rest' are byte-identical streams.")


def o_s01_7_a_stream_is_a_constant() -> None:
    print("\n[O-S01-7] policy_rng returns a fresh Random on every call")
    draws = [rng.policy_rng("draft").random() for _ in range(3)]
    print("  three successive first-draws:", len(set(draws)) == 1)
    print("  OBSERVED : each call replays the same sequence, so a label is a "
          "constant rather than a stream. Inert today -- "
          "tier05/draft.py assigned_policy never consumes its rng.")


def o_s01_8_an_empty_chosen_seed_silently_disarms_the_arm() -> None:
    print("\n[O-S01-8] --seed '' ")
    chosen, seed = "", "REALGAMESEED"
    print("  _embark guard `if pick is not None and self.chosen_seed`:",
          bool(chosen), "-> set_seed is never called")
    print("  logged   :", {"record": "seed_read_back", "seed": seed,
                           "chosen": chosen,
                           "honoured": (None if not chosen else seed == chosen),
                           "note": ("chosen; P1.5 arm" if chosen
                                    else "game-generated; R95 read-back arm")})
    print("  OBSERVED : the index records seeds=[''] while every run logs "
          "itself as the R95 read-back arm. No defect, no warning.")
    seen = {}
    real = bridge._request
    bridge._request = (lambda url, payload=None, timeout=20.0:
                       seen.update(payload=payload) or {"status": "ok"})
    bridge.set_seed(12345)
    bridge._request = real
    print("  aside    : set_seed does not type-check; wire payload was",
          json.dumps(seen["payload"]))


if __name__ == "__main__":
    for fn in (o_s01_1_unknown_seeds_compare_as_the_same_seed,
               o_s01_2_absent_run_logs_are_identical,
               o_s01_3_a_truncated_seed_line_is_dropped,
               o_s01_4_honoured_is_never_consulted,
               o_s01_5_the_leak_guard_fails_open,
               o_s01_6_label_offsets_collide,
               o_s01_7_a_stream_is_a_constant,
               o_s01_8_an_empty_chosen_seed_silently_disarms_the_arm):
        fn()
