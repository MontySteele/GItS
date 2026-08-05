"""S7 — the sim-fidelity replay.

Drives tier0's combat model through the action sequences the soak actually
posted at the real game, and diffs every number both instruments recorded.

**This module measures. It concludes nothing.** Every row it writes is a raw
pair (sim said X, engine said Y) plus the context needed to read it; the
classification into families is a separate, later pass and deliberately does
not live here. Guardrail 7 applies unchanged: nothing produced here is a
balance finding.

What a soak log gives us, and why the replay is shaped the way it is
-------------------------------------------------------------------

A `decision` row carries `hand` (the exact hand, index-ordered), the resolved
`names.card_name`, and — for a targeted play — `names.target_hp`, the target's
HP **as read immediately before the action was posted**. A `fight` row carries
the per-turn curves: `hp_trajectory`, `block_at_turn_end`, `meters_by_turn`,
`enemy_pool_by_turn`, `incoming_by_turn`, `damage_by_source`.

So two independent replay levels are available, and both are run:

* **L1, per card.** Between two consecutive targeted plays at the same target
  in the same turn, the engine's own reading brackets exactly one card:
  `target_hp[n] - target_hp[n+1]`. The sim is asked the same question in
  isolation — a fresh state, the player's meters set from the turn's opening
  reading, one enemy at the bracketing HP, `effects.resolve_card`. The
  divergence is per card and needs no assumption about ordering.

* **L2, per turn.** The turn's opening reading (HP, block, fanfare, salon,
  encore) is loaded into a state, the recorded hand is dealt, the recorded
  cards are played in the recorded order through `combat.play_card`, and the
  turn's *closing* numbers are compared: block at turn end, the enemy pool
  drop, and the next turn's opening fanfare / salon members.

Declared confounders — read these before reading any row
--------------------------------------------------------

1. `combat.play_card` takes no target: single-target aim is always the
   lowest-HP living enemy. L1 sidesteps this by presenting one enemy. L2 does
   not, so an L2 row on a multi-enemy fight carries `n_enemies>1` in its
   context and a targeting difference is a live alternative explanation.
2. Relics, potions, pile order and exhaust contents are not carried by the
   wire and so are not reconstructed. A relic that adds damage is invisible
   to the sim side of every row.
3. Enemy block and enemy powers are not on the wire per enemy. `target_hp` is
   an HP reading; a card that was partly eaten by enemy block reads short.
4. Player Strength / Vulnerable accrued *within* a turn is not reconstructed
   at L1 (each card is resolved from the turn-opening reading), so a row for a
   card played late in a long turn understates the sim by the turn's own
   ramp. L2 does accrue it.
5. Base-game (non-mod) cards have no tier0 row at all. Those plays are
   skipped and counted, never approximated.
6. Five adapter defects were fixed during Phase 0 (enemies nested under
   `battle`, intent damage only in the label, hand field `target_type`,
   the "Cryo Aura" string, a Strength double-fold). Logs written before those
   fixes can carry corrupted READINGS. Rows whose engine side fails an
   internal consistency check are flagged `suspected_reading_corruption`
   rather than silently attributed to the sim.

Usage
-----

    python -m understudy.replay --logs "<glob>" --out docs/s7-divergences.tsv
"""

from __future__ import annotations

import argparse
import collections
import copy
import glob as globmod
import json
import os
import random
import sys
from typing import Any, Iterable

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat, effects, resources
from tier0.engine.state import CombatState, Enemy, Player

COMBAT_SCREENS = {"monster", "elite", "boss"}

# A divergence smaller than this is not reported: it is the reading noise of
# an HP sample taken one frame after an action.
TOLERANCE = 0.5


# --------------------------------------------------------------------------
# log reading
# --------------------------------------------------------------------------


def read_jsonl(path: str) -> list[dict]:
    out: list[dict] = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def fight_specs(path: str) -> list[dict]:
    """Split one soak run log into fights, each with its posted action stream.

    A `fight` record closes the combat decisions that preceded it, which is
    the order `soak.py` writes them in.
    """
    recs = read_jsonl(path)
    stem = os.path.basename(path)
    if stem.endswith(".jsonl"):
        stem = stem[: -len(".jsonl")]
    pending: list[dict] = []
    specs: list[dict] = []
    n = 0
    for rec in recs:
        kind = rec.get("record")
        if kind == "decision" and rec.get("state_type") in COMBAT_SCREENS:
            pending.append(rec)
        elif kind == "fight":
            n += 1
            specs.append(
                {
                    "fight_id": "%s#f%d" % (stem, n),
                    "log": path,
                    "fight": rec,
                    "turns": _turns(pending),
                }
            )
            pending = []
    return specs


def _turns(decisions: Iterable[dict]) -> list[dict]:
    turns: "collections.OrderedDict[Any, dict]" = collections.OrderedDict()
    for dec in decisions:
        rnd = dec.get("round")
        turn = turns.setdefault(
            rnd,
            {"round": rnd, "hand_at_open": None, "hp_at_open": dec.get("hp"), "plays": []},
        )
        if turn["hand_at_open"] is None:
            turn["hand_at_open"] = list(dec.get("hand") or [])
        names = dec.get("names") or {}
        if names.get("verb") == "play_card":
            turn["plays"].append(
                {
                    "card": names.get("card_name"),
                    "card_id": names.get("card_id"),
                    "upgraded": bool(names.get("card_upgraded")),
                    "target_id": names.get("target_id"),
                    "target_name": names.get("target_name"),
                    "target_hp": names.get("target_hp"),
                    "status": dec.get("status"),
                    "i": dec.get("i"),
                }
            )
    return list(turns.values())


# --------------------------------------------------------------------------
# name resolution
# --------------------------------------------------------------------------


class Names:
    """Display name -> tier0 card. `tools/lint_unique_names.py` guarantees the
    mapping is a function; the `+` suffix is the upgrade, per `upgrades.SUFFIX`.
    """

    def __init__(self) -> None:
        self._by_name: dict[str, str] = {}
        for card_id, card in loader._card_index().items():
            self._by_name.setdefault(card.name, card_id)
        self.unresolved: "collections.Counter[str]" = collections.Counter()
        self.unresolved_played: "collections.Counter[str]" = collections.Counter()

    def card(self, display: str, played: bool = False):
        if not display:
            return None
        base, upgraded = display, False
        if base.endswith("+"):
            base, upgraded = base[:-1], True
        card_id = self._by_name.get(base)
        if card_id is None:
            self.unresolved[display] += 1
            if played:
                self.unresolved_played[display] += 1
            return None
        try:
            return loader.get_card(card_id + "+" if upgraded else card_id)
        except Exception:
            try:
                return loader.get_card(card_id)
            except Exception:
                self.unresolved[display] += 1
                return None


# --------------------------------------------------------------------------
# state construction
# --------------------------------------------------------------------------


def _meters_at(fight: dict, rnd: Any) -> dict:
    for row in fight.get("meters_by_turn") or []:
        if row and row[0] == rnd:
            return {
                "fanfare": row[1] if len(row) > 1 else 0,
                "salon_members": row[2] if len(row) > 2 else 0,
                "salon_cap": row[3] if len(row) > 3 else 0,
                "encore": row[4] if len(row) > 4 else -1,
            }
    return {}


def _traj_at(fight: dict, rnd: Any) -> dict:
    for row in fight.get("hp_trajectory") or []:
        if row and row[0] == rnd:
            return {"hp": row[1], "block": row[2] if len(row) > 2 else 0}
    return {}


def _pool_at(fight: dict, rnd: Any):
    for row in fight.get("enemy_pool_by_turn") or []:
        if row and row[0] == rnd:
            return row[1]
    return None


def _block_end(fight: dict, rnd: Any):
    for row in fight.get("block_at_turn_end") or []:
        if row and row[0] == rnd:
            return row[1]
    return None


def _apply_meters(player: Player, meters: dict) -> None:
    """Load a turn-opening meter reading onto a fresh Furina player.

    `salon` is the source of truth for membership and `powers["salon_member"]`
    mirrors it, so both are set. `encore == -1` means the bot feed could not
    see the meter (it is a CustomResource the bridge does not serialise); it
    is left at the sim's own value and every encore comparison on that fight
    is suppressed rather than compared against a sentinel.
    """
    if not meters:
        return
    player.fanfare = int(meters.get("fanfare") or 0)
    cap = meters.get("salon_cap")
    if cap:
        extra = int(cap) - C.SALON_MEMBER_SLOTS
        if extra > 0:
            player.powers["salon_cap_up"] = extra
    n = int(meters.get("salon_members") or 0)
    if n > 0:
        members = list(C.SALON_MEMBERS)
        player.salon = [members[i % len(members)] for i in range(n)]
        player.powers["salon_member"] = n
    enc = meters.get("encore")
    if enc is not None and enc >= 0:
        player.encore = int(enc)


def _fresh_player(character_id: str, hp: int, max_hp: int, block: int, meters: dict) -> Player:
    player = loader.build_player(character_id)
    player.max_hp = int(max_hp or player.max_hp)
    player.hp = int(hp if hp is not None else player.hp)
    player.block = int(block or 0)
    player.draw_pile = []
    player.discard_pile = []
    player.hand = []
    player.energy = C.ENERGY_PER_TURN if hasattr(C, "ENERGY_PER_TURN") else 3
    _apply_meters(player, meters)
    return player


def _enemy(name: str, hp: int) -> Enemy:
    hp = int(hp)
    return Enemy(hp=hp, max_hp=max(hp, 1), name=name or "enemy", intents=[])


def _pool_total(state: CombatState) -> int:
    return sum(e.hp + e.block for e in state.enemies if e.alive)


# --------------------------------------------------------------------------
# L1 — per-card isolated replay
# --------------------------------------------------------------------------


def l1_rows(spec: dict, names: Names, character_id: str, tally: dict) -> list[dict]:
    """One row per card the engine's own readings bracket.

    The bracket is `target_hp` at play n minus `target_hp` at play n+1, both
    at the same target in the same turn. A NEGATIVE bracket means the target's
    HP went UP between two plays — an enemy that split, hatched or was
    replaced under a reused id — and is flagged as reading corruption rather
    than compared.
    """
    fight = spec["fight"]
    rows: list[dict] = []
    for turn in spec["turns"]:
        rnd = turn["round"]
        meters = _meters_at(fight, rnd)
        traj = _traj_at(fight, rnd)
        targeted = [p for p in turn["plays"] if p.get("target_id") and p.get("target_hp") is not None]
        for cur, nxt in zip(targeted, targeted[1:]):
            if cur["target_id"] != nxt["target_id"]:
                continue
            engine = cur["target_hp"] - nxt["target_hp"]
            corrupt = engine < 0
            card = names.card(cur["card"], played=True)
            if card is None:
                tally["l1_skipped_unresolved"] += 1
                continue
            tally["l1_compared"] += 1
            player = _fresh_player(
                character_id, traj.get("hp"), fight.get("max_hp"), traj.get("block"), meters
            )
            enemy = _enemy(cur.get("target_name") or "enemy", cur["target_hp"])
            state = CombatState(player=player, enemies=[enemy], rng=random.Random(0), turn=int(rnd or 1))
            before = enemy.hp + enemy.block
            try:
                effects.resolve_card(state, card)
            except Exception as exc:  # a card the reconstruction cannot resolve
                rows.append(
                    _row(
                        spec,
                        rnd,
                        "l1.damage.%s" % cur["card"],
                        "ERROR:%s" % type(exc).__name__,
                        engine,
                        "isolated card resolve raised",
                        False,
                    )
                )
                continue
            sim = before - (enemy.hp + enemy.block)
            if corrupt or abs(sim - engine) > TOLERANCE:
                rows.append(
                    _row(
                        spec,
                        rnd,
                        "l1.damage",
                        sim,
                        engine,
                        "card=%s target=%s target_hp=%s->%s n_enemies=%d"
                        % (
                            cur["card"],
                            cur.get("target_name"),
                            cur["target_hp"],
                            nxt["target_hp"],
                            len(fight.get("enemies") or []),
                        ),
                        corrupt,
                    )
                )
    return rows


# --------------------------------------------------------------------------
# L2 — per-turn sequential replay
# --------------------------------------------------------------------------


def l2_rows(spec: dict, names: Names, character_id: str, tally: dict) -> list[dict]:
    fight = spec["fight"]
    enemies_spec = fight.get("enemies") or []
    rows: list[dict] = []
    for turn in spec["turns"]:
        rnd = turn["round"]
        meters = _meters_at(fight, rnd)
        traj = _traj_at(fight, rnd)
        if not traj:
            continue
        pool_open = _pool_at(fight, rnd)
        pool_next = _pool_at(fight, (rnd or 0) + 1)
        player = _fresh_player(
            character_id, traj.get("hp"), fight.get("max_hp"), traj.get("block"), meters
        )
        hand = []
        skipped = 0
        for display in turn["hand_at_open"] or []:
            card = names.card(display)
            if card is None:
                skipped += 1
                continue
            hand.append(card)
        player.hand = hand
        player.energy = 99  # cost is not the question this level asks
        enemies = [
            _enemy(e.get("name"), e.get("max_hp") or 1) for e in enemies_spec
        ] or [_enemy("enemy", 100)]
        if len(enemies) == 1 and pool_open is not None:
            enemies[0].hp = max(int(pool_open), 1)
            enemies[0].max_hp = max(int(enemies_spec[0].get("max_hp") or pool_open), 1)
        state = CombatState(
            player=player, enemies=enemies, rng=random.Random(0), turn=int(rnd or 1)
        )
        before_pool = _pool_total(state)
        played = 0
        for play in turn["plays"]:
            card = _find_in_hand(state, play["card"])
            if card is None:
                card = names.card(play["card"], played=True)
                if card is None:
                    tally["l2_skipped_unresolved"] += 1
                    continue
                state.player.hand.append(card)
            try:
                combat.play_card(state, card)
                played += 1
            except Exception:
                tally["l2_play_errors"] += 1
                continue
        ctx = "cards=%d/%d hand_unresolved=%d n_enemies=%d" % (
            played,
            len(turn["plays"]),
            skipped,
            len(enemies),
        )
        # block at turn end
        eng_block = _block_end(fight, rnd)
        if eng_block is not None:
            tally["l2_block_compared"] += 1
        if eng_block is not None and abs(state.player.block - eng_block) > TOLERANCE:
            rows.append(_row(spec, rnd, "l2.block_at_turn_end", state.player.block, eng_block, ctx, False))
        # enemy pool drop across the turn
        if pool_open is not None and pool_next is not None:
            tally["l2_pool_compared"] += 1
            eng_drop = pool_open - pool_next
            sim_drop = before_pool - _pool_total(state)
            if abs(sim_drop - eng_drop) > TOLERANCE:
                rows.append(
                    _row(
                        spec,
                        rnd,
                        "l2.enemy_pool_drop",
                        sim_drop,
                        eng_drop,
                        ctx + " pool=%s->%s" % (pool_open, pool_next),
                        eng_drop < 0,
                    )
                )
        # meters at the NEXT turn opening
        nxt = _meters_at(fight, (rnd or 0) + 1)
        if nxt:
            tally["l2_fanfare_compared"] += 1
            tally["l2_salon_compared"] += 1
            if nxt["encore"] >= 0:
                tally["l2_encore_compared"] += 1
            if abs(state.player.fanfare - nxt["fanfare"]) > TOLERANCE:
                rows.append(
                    _row(spec, rnd, "l2.fanfare_after_turn", state.player.fanfare, nxt["fanfare"], ctx, False)
                )
            # The engine samples `meters_by_turn` at the turn OPENING, and
            # `combat._player_turn` decays Fanfare at the true top of the turn
            # before any turn-start generation. Both sides of that ordering
            # are reported: the raw end-of-turn value above, and the same
            # value after the sim's own decay here. Which one is the fair
            # comparison is a question for the classification pass, not for
            # this module to decide.
            decayed = copy.deepcopy(state)
            try:
                resources.decay_fanfare(decayed)
            except Exception:
                pass
            tally["l2_fanfare_decayed_compared"] += 1
            if abs(decayed.player.fanfare - nxt["fanfare"]) > TOLERANCE:
                rows.append(
                    _row(
                        spec,
                        rnd,
                        "l2.fanfare_next_open_post_decay",
                        decayed.player.fanfare,
                        nxt["fanfare"],
                        ctx,
                        False,
                    )
                )
            sim_members = len(state.player.salon)
            if sim_members != nxt["salon_members"]:
                rows.append(
                    _row(
                        spec,
                        rnd,
                        "l2.salon_members_after_turn",
                        sim_members,
                        nxt["salon_members"],
                        ctx,
                        False,
                    )
                )
            if nxt["encore"] >= 0 and abs(state.player.encore - nxt["encore"]) > TOLERANCE:
                rows.append(
                    _row(
                        spec,
                        rnd,
                        "l2.encore_after_turn",
                        state.player.encore,
                        nxt["encore"],
                        ctx,
                        _encore_unseen(fight),
                    )
                )
    return rows


def _encore_unseen(fight: dict) -> bool:
    """True when this fight's Encore column is the UNSEEN sentinel, not a zero.

    The bot feed cannot see Encore at all — it is a CustomResource the bridge
    does not serialise. The current writer records `-1` for that and this
    module skips those turns outright. Earlier soak builds wrote `0` instead,
    which is indistinguishable from a real empty meter turn by turn but is
    recognisable across a whole fight: a Furina fight in which Encore is 0 at
    *every* opening, while the same fight's mod-feed row shows the meter
    moving, is the sentinel wearing a zero. Rows from such a fight are
    flagged as reading corruption rather than charged to the sim.
    """
    col = [row[4] for row in (fight.get("meters_by_turn") or []) if len(row) > 4]
    return bool(col) and all(v == 0 for v in col)


def _find_in_hand(state: CombatState, display: str):
    for card in state.player.hand:
        if card.name == display:
            return card
    return None


# --------------------------------------------------------------------------
# cross-instrument reading check (NOT a sim divergence)
# --------------------------------------------------------------------------


def cross_feed_rows(soak_fights: list[tuple[str, dict]], mod_fights: list[dict], window: float = 10.0) -> list[dict]:
    """The same fight, read twice: `soak.py` off the wire and `PlayTelemetry.cs`
    inside the process. Neither side is the sim, so every row here is an
    instrument-vs-instrument reading disagreement by construction — it is
    emitted with `suspected_reading_corruption=1` so the classification pass
    can keep it out of the sim ledger.
    """
    rows: list[dict] = []
    if not mod_fights:
        return rows
    scalar = [
        "hp_start",
        "hp_end",
        "hp_lost",
        "max_hp",
        "turns",
        "damage_dealt",
        "damage_taken",
        "n_cards_played",
        "outcome",
        "act",
        "floor",
    ]
    for fid, s in soak_fights:
        m = min(mod_fights, key=lambda x: abs(x.get("ts", 0) - s.get("ts", 0)))
        if abs(m.get("ts", 0) - s.get("ts", 0)) > window:
            continue
        for key in scalar:
            if s.get(key) != m.get(key):
                rows.append(
                    _rowlite(fid, "", "xfeed.%s" % key, s.get(key), m.get(key), "soak vs mod feed", True)
                )
        smet = {r[0]: r[1:] for r in s.get("meters_by_turn") or []}
        mmet = {r[0]: r[1:] for r in m.get("meters_by_turn") or []}
        for rnd in sorted(set(smet) & set(mmet)):
            for i, label in enumerate(("fanfare", "salon_members", "salon_cap", "encore")):
                if i < len(smet[rnd]) and i < len(mmet[rnd]) and smet[rnd][i] != mmet[rnd][i]:
                    rows.append(
                        _rowlite(
                            fid,
                            rnd,
                            "xfeed.meters.%s" % label,
                            smet[rnd][i],
                            mmet[rnd][i],
                            "soak vs mod feed",
                            True,
                        )
                    )
        spool = {r[0]: r[1] for r in s.get("enemy_pool_by_turn") or []}
        mpool = {r[0]: r[1] for r in m.get("enemy_pool_by_turn") or []}
        for rnd in sorted(set(spool) & set(mpool)):
            if spool[rnd] != mpool[rnd]:
                rows.append(
                    _rowlite(fid, rnd, "xfeed.enemy_pool", spool[rnd], mpool[rnd], "soak vs mod feed", True)
                )
        straj = {r[0]: tuple(r[1:]) for r in s.get("hp_trajectory") or []}
        mtraj = {r[0]: tuple(r[1:]) for r in m.get("hp_trajectory") or []}
        for rnd in sorted(set(straj) & set(mtraj)):
            if straj[rnd] != mtraj[rnd]:
                rows.append(
                    _rowlite(
                        fid, rnd, "xfeed.hp_trajectory", straj[rnd], mtraj[rnd], "soak vs mod feed (hp,block)", True
                    )
                )
    return rows


def cards_played_rows(spec: dict) -> list[dict]:
    """`fight.cards_played` against the posted action stream in the same log.

    Same writer, same run: a card the driver posted and the bridge answered
    `ok` to, that never reached the fight record, is a hole in the record and
    not a statement about the sim.
    """
    fight = spec["fight"]
    recorded = collections.Counter(c for _, c in fight.get("cards_played") or [])
    posted = collections.Counter(
        p["card"] for turn in spec["turns"] for p in turn["plays"] if p.get("status") == "ok"
    )
    rows = []
    for name in sorted(set(recorded) | set(posted)):
        if recorded[name] != posted[name]:
            rows.append(
                _rowlite(
                    spec["fight_id"],
                    "",
                    "record.cards_played[%s]" % name,
                    recorded[name],
                    posted[name],
                    "fight.cards_played vs posted play_card actions (same log)",
                    True,
                )
            )
    return rows


# --------------------------------------------------------------------------
# rows / output
# --------------------------------------------------------------------------


def _row(spec, rnd, field, sim, engine, ctx, corrupt) -> dict:
    return _rowlite(spec["fight_id"], rnd, field, sim, engine, ctx, corrupt)


def _rowlite(fight_id, rnd, field, sim, engine, ctx, corrupt) -> dict:
    return {
        "fight_id": fight_id,
        "turn": "" if rnd is None else rnd,
        "field": field,
        "sim_value": sim,
        "engine_value": engine,
        "action_context": ctx,
        "suspected_reading_corruption": 1 if corrupt else 0,
    }


COLUMNS = [
    "fight_id",
    "turn",
    "field",
    "sim_value",
    "engine_value",
    "action_context",
    "suspected_reading_corruption",
]


def write_tsv(rows: list[dict], path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\t".join(COLUMNS) + "\n")
        for row in rows:
            fh.write(
                "\t".join(str(row.get(col, "")).replace("\t", " ").replace("\n", " ") for col in COLUMNS)
                + "\n"
            )


# --------------------------------------------------------------------------
# driver
# --------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="S7 sim-fidelity replay")
    ap.add_argument("--logs", action="append", default=[], help="glob of soak run JSONLs (repeatable)")
    ap.add_argument("--mod-logs", action="append", default=[], help="glob of human/mod-feed JSONLs")
    ap.add_argument("--character", default="furina")
    ap.add_argument("--out", default="docs/s7-divergences.tsv")
    ap.add_argument("--summary", default="", help="write a JSON summary here")
    args = ap.parse_args(argv)

    paths: list[str] = []
    for pattern in args.logs:
        paths.extend(sorted(globmod.glob(pattern, recursive=True)))
    paths = [p for p in dict.fromkeys(paths) if os.path.isfile(p)]

    specs: list[dict] = []
    for path in paths:
        specs.extend(fight_specs(path))

    names = Names()
    rows: list[dict] = []
    replayed = 0
    tally: "collections.Counter[str]" = collections.Counter()
    for spec in specs:
        if not spec["turns"]:
            continue
        replayed += 1
        tally["plays_posted"] += sum(len(t["plays"]) for t in spec["turns"])
        rows.extend(l1_rows(spec, names, args.character, tally))
        rows.extend(l2_rows(spec, names, args.character, tally))
        rows.extend(cards_played_rows(spec))

    mod: list[dict] = []
    for pattern in args.mod_logs:
        for path in sorted(globmod.glob(pattern, recursive=True)):
            mod.extend(r for r in read_jsonl(path) if r.get("record") == "fight")
    rows.extend(cross_feed_rows([(s["fight_id"], s["fight"]) for s in specs], mod))

    write_tsv(rows, args.out)

    by_field = collections.Counter(r["field"].split("[")[0] for r in rows)
    summary = {
        "logs": len(paths),
        "fights_found": len(specs),
        "fights_replayed": replayed,
        "rows": len(rows),
        "rows_flagged_reading": sum(r["suspected_reading_corruption"] for r in rows),
        "comparisons": dict(sorted(tally.items())),
        "unresolved_card_names_any": dict(names.unresolved.most_common()),
        "unresolved_card_names_played": dict(names.unresolved_played.most_common()),
        "by_field": dict(by_field.most_common()),
        "mod_fights": len(mod),
    }
    print(json.dumps(summary, indent=2))
    if args.summary:
        with open(args.summary, "w", encoding="utf-8") as fh:
            json.dump(summary, fh, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
