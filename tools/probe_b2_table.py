"""Probe B2's table: engine per-play Block increments against tier0's.

Reads the readings `understudy/probe_block.py` wrote (one row per decision,
each carrying `player.block` as read from the wire at that moment) and pairs
consecutive readings within a round so each pair brackets exactly one card --
the same bracketing S7's L1 uses on `target_hp`, applied to Block.

The sim side is asked the identical question through tier0's OWN entry point
(`effects.resolve_card` on a fresh state), under the SAME Spotlight
designation the probe's arm declared. No rule is retyped here.

    python -m tools.probe_b2_table understudy/logs/soak/probe-b2-*.jsonl
"""

from __future__ import annotations

import collections
import glob as globmod
import json
import random
import sys

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import effects
from tier0.engine.state import CombatState, Enemy

from understudy.replay import Names

ARM_SPOTLIGHT = {"center": None, "guest": C.SPOTLIGHT_GUEST_CAST}


def rows(path: str) -> list[dict]:
    out = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def _status_map(row: dict) -> dict:
    """The player's status strip as the wire spelled it, lowercased."""
    out = {}
    for entry in row.get("status") or []:
        if isinstance(entry, (list, tuple)) and len(entry) >= 2 and entry[1] is not None:
            out[str(entry[0]).strip().lower()] = int(entry[1])
    return out


# Probe (d) (R120 / 10.13): the meter-loaded reconstruction sets cap and
# floor EXPLICITLY so a loaded level cannot be silently clipped by
# `min(p.fanfare_cap, ...)`. Printed in the table header per the
# registration's method step 4.
METERS_FANFARE_CAP = 999
METERS_FANFARE_FLOOR = 0


def sim_block(names: Names, card_name: str, arm: str, character: str = "furina",
              status: dict | None = None, fanfare: int | None = None):
    card = names.card(card_name, played=True)
    if card is None:
        return None
    player = loader.build_player(character)
    player.hand = []
    player.draw_pile = []
    player.discard_pile = []
    player.block = 0
    player.energy = 99
    # The RECONSTRUCTED arm. tier0 already models Frail exactly
    # (`powers._modify_block` -> `FRAIL_BLOCK_MULT`); what the replay never
    # had was the reading, because `hp_trajectory` carries `(round, hp,
    # block)` and no status strip. Loading it is reconstruction, not a rule.
    for name, amount in (status or {}).items():
        if name in ("frail", "weak", "vulnerable", "strength", "dexterity"):
            player.powers[name] = amount
    # Probe (d)'s third column: the recorded Fanfare level written onto the
    # reconstructed player before `effects.resolve_card`. Reconstruction,
    # not a rule -- the existing `1_per_4_fanfare` arm of
    # `effects._bonus_formula` is what gets exercised, unmodified.
    if fanfare is not None:
        player.fanfare_cap = METERS_FANFARE_CAP
        player.fanfare_floor = METERS_FANFARE_FLOOR
        player.fanfare = int(fanfare)
    spot = ARM_SPOTLIGHT[arm]
    player.spotlight = spot if spot else player.character_id
    enemy = Enemy(hp=200, max_hp=200, name="probe", intents=[])
    state = CombatState(player=player, enemies=[enemy], rng=random.Random(0), turn=1)
    before = player.block
    try:
        effects.resolve_card(state, card)
    except Exception as exc:                                   # noqa: BLE001
        return "ERROR:%s" % type(exc).__name__
    return state.player.block - before


def _fanfare_of(row: dict):
    """The wire's recorded Fanfare level at a reading, or None."""
    res = row.get("resources")
    if isinstance(res, dict) and "KLEEMOD_FANFARE" in res:
        return int(res["KLEEMOD_FANFARE"])
    return None


def main(argv: list[str]) -> int:
    # Probe (d) (R120 / 10.13): `--meters` adds the meter-loaded
    # reconstruction column and its layer-2 sub-fork (meter read BEFORE the
    # play vs AFTER the play's own Fanfare income lands). Without the flag
    # the output is byte-identical to B2's published table.
    meters = "--meters" in argv
    argv = [a for a in argv if a != "--meters"]
    paths: list[str] = []
    for pat in argv or ["understudy/logs/soak/probe-b2-*.jsonl"]:
        paths.extend(sorted(globmod.glob(pat)))
    names = Names()
    header = ("arm\tround\tcard\tengine\tsim_blind\tdiff_blind\tsim_status"
              "\tdiff_status\tfrail\tblock_before\tblock_after")
    if meters:
        print("== --meters reconstruction: fanfare_cap=%d fanfare_floor=%d "
              "(set explicitly; never left to build_player) =="
              % (METERS_FANFARE_CAP, METERS_FANFARE_FLOOR))
        header += ("\tfanfare_pre\tsim_m_pre\tdiff_m_pre"
                   "\tfanfare_post\tsim_m_post\tdiff_m_post")
    print(header)
    agg: "collections.Counter[tuple]" = collections.Counter()
    diff_blind: "collections.Counter[int]" = collections.Counter()
    diff_status: "collections.Counter[int]" = collections.Counter()
    diff_m_pre: "collections.Counter[int]" = collections.Counter()
    diff_m_post: "collections.Counter[int]" = collections.Counter()
    relics: set = set()
    enemies: set = set()
    estat: set = set()
    for path in paths:
        arm = "guest" if "-guest-" in path else "center"
        rs = rows(path)
        for cur, nxt in zip(rs, rs[1:]):
            if cur.get("about") != "before_play":
                continue
            if cur.get("round") != nxt.get("round"):
                continue
            if nxt.get("about") not in ("before_play", "before_end_turn"):
                continue
            card = cur.get("card")
            eng = nxt["block"] - cur["block"]
            status = _status_map(cur)
            sim = sim_block(names, card, arm)
            sim2 = sim_block(names, card, arm, status=status)
            for r in cur.get("relics") or []:
                relics.add(str(r))
            for e in cur.get("enemies") or []:
                enemies.add("%s blk=%s" % (e.get("name"), e.get("block")))
                for s in e.get("status") or []:
                    estat.add(str(tuple(s)))
            d1 = "" if not isinstance(sim, int) else sim - eng
            d2 = "" if not isinstance(sim2, int) else sim2 - eng
            line = ("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s"
                    % (arm, cur.get("round"), card, eng, sim, d1, sim2, d2,
                       status.get("frail", 0), cur["block"], nxt["block"]))
            if meters:
                # The layer-2 fork, run as two sub-columns rather than
                # chosen: the meter as read BEFORE the play (this reading)
                # and AFTER the play's own income landed (the next reading).
                f_pre = _fanfare_of(cur)
                f_post = _fanfare_of(nxt)
                m1 = (sim_block(names, card, arm, status=status,
                                fanfare=f_pre)
                      if f_pre is not None else "")
                m2 = (sim_block(names, card, arm, status=status,
                                fanfare=f_post)
                      if f_post is not None else "")
                dm1 = m1 - eng if isinstance(m1, int) else ""
                dm2 = m2 - eng if isinstance(m2, int) else ""
                if isinstance(m1, int):
                    diff_m_pre[m1 - eng] += 1
                if isinstance(m2, int):
                    diff_m_post[m2 - eng] += 1
                line += ("\t%s\t%s\t%s\t%s\t%s\t%s"
                         % ("" if f_pre is None else f_pre, m1, dm1,
                            "" if f_post is None else f_post, m2, dm2))
            print(line)
            if isinstance(sim, int):
                agg[(arm, card, eng, sim, sim2, status.get("frail", 0))] += 1
                diff_blind[sim - eng] += 1
            if isinstance(sim2, int):
                diff_status[sim2 - eng] += 1
    print()
    print("== aggregated (arm, card, frail) -> engine / sim blind / sim status ==")
    for k, n in sorted(agg.items()):
        f1 = "" if k[2] == k[3] else "  BLIND %+d" % (k[3] - k[2])
        f2 = "" if k[2] == k[4] else "  STATUS %+d" % (k[4] - k[2])
        print("  %-7s %-40s frail=%-2d eng=%-3d blind=%-3d status=%-3d n=%d%s%s"
              % (k[0], k[1][:40], k[5], k[2], k[3], k[4], n, f1, f2))
    print()
    print("== divergence distribution (sim - engine) ==")
    print("  selector-known, status-BLIND  :", dict(sorted(diff_blind.items())),
          " agree=%d/%d" % (diff_blind[0], sum(diff_blind.values())))
    print("  selector-known, status-LOADED :", dict(sorted(diff_status.items())),
          " agree=%d/%d" % (diff_status[0], sum(diff_status.values())))
    if meters:
        print("  status+meter (PRE-play)       :",
              dict(sorted(diff_m_pre.items())),
              " agree=%d/%d" % (diff_m_pre[0], sum(diff_m_pre.values())))
        print("  status+meter (POST-play)      :",
              dict(sorted(diff_m_post.items())),
              " agree=%d/%d" % (diff_m_post[0], sum(diff_m_post.values())))
    print()
    print("relics seen on the wire:", sorted(relics))
    print("enemies seen:", sorted(enemies))
    print("enemy statuses seen:", sorted(estat) or "(none)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
