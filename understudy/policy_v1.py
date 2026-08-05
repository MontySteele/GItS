"""policy_v1 -- the seven ratified revisions, and the arm the soak actually flies.

R93 (2026-08-04) approved all seven revisions the Phase-0 report proposed, with
#7 elevated to a P1 blocker. This module implements them. It is the DRIVING
policy for `understudy/soak.py`; policy_v0 stays exactly as it was, because it
is the counterfactual arm of a measurement that has already been taken and
editing it would retroactively change a published number.

THE SEAM, RESTATED (it is the whole reason this sprint is allowed to exist)

Nothing in `tier0/`, `tier05/`, the drafter or any sheet is modified,
monkeypatched, or read for anything but its public behaviour. What policy_v1
adds on top of policy_v0 is ORDERING and GATING around the sim's own valuation
functions -- never a new way to price a card. Where a revision needed a number
of its own (two of them do), the number lives in this file, is named, and is
declared un-quotable: these are policy dials for a bot, not balance constants,
and no report may cite one as evidence about the game.

WHERE EACH REVISION LIVES

  #1 free expiring cards first     `_combat`, `_free_expiring`
  #2 block-panic gate + kill line  `_combat`, `_gated_ladder`
  #3 map one ply deeper            `_map`
  #4 potion arm                    `_combat`, `_potion_arm`
  #5 next_fight into rest          `_rest` (+ `Memo.next_node_kinds`)
  #6 in-combat choice overlay      `_choice_overlay`
  #7 resolved card NAMES           `understudy/naming.py`, attached by `decide`

DETERMINISM

Every arm sorts; none rolls. The RNG handed to the delegated tier05 policies
comes from `understudy.rng.policy_rng`, which is stream-isolated from the game
seed by construction and refuses a label shaped like one. Two soak runs on the
same wire state produce the same decision, which is what makes a divergence
between two runs a fact about the runs.

THE MEMO, AND WHY A POLICY HAS ONE

policy_v0 is a pure function of one wire state, because a counterfactual has to
be. policy_v1 drives, and two of its revisions need something the wire does not
carry at the moment it is needed: the potion arm fires once per combat ROUND
(the sim calls `try_use_potions` at turn start, not per card), and the rest arm
needs the kind of the node AFTER this one, which is on the map screen and gone
by the time the rest site loads. Both are carried in an explicit `Memo` the
driver owns, so the hidden state is named and inspectable rather than living in
module globals.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import potions as t0potions
from tier0.pilot import policy as pilot_policy
from tier05 import draft as t5draft
from tier05 import model as t5model
from tier05 import route as t5route

from understudy import adapter, naming, policy_v0

CHARACTER = policy_v0.CHARACTER
ARCHETYPE = policy_v0.ARCHETYPE
PILOT_ID = policy_v0.PILOT_ID

POLICY_VERSION = "policy_v1"

# --------------------------------------------------------------- dials ----
#
# THE TWO NUMBERS THIS MODULE OWNS. Both are bot-policy dials. Neither is a
# balance constant, neither belongs in `tier0/constants.py`, and no number
# produced downstream of them is quotable as evidence about the game (R93's
# scope clause, Guardrail-7).

# Revision #2. The block-panic rung fires on the ratio of incoming to HP alone,
# so it will buy 4 Block against 39 incoming -- the Phase-0 floor-7 board. This
# is the fraction of the UNCOVERED incoming that the best available Block must
# actually prevent for the panic to be worth obeying. At 0.5 the floor-7 board
# scores 4/39 = 0.10 and the panic is gated; a 12-Block card against 20
# incoming scores 0.60 and is obeyed.
BLOCK_MATTERS_FRACTION = 0.5

# Revision #6. Guest Cast makes Companion cards 50% stronger and stops them
# generating Fanfare; Center Stage makes Furina's own cards generate Fanfare.
# The choice is a deck-composition question, so it is answered on deck
# composition: below this share of Companions there is not enough Companion
# text in the deck for the multiplier to beat the generator.
COMPANION_SHARE_FOR_GUEST_CAST = 0.20


@dataclass
class Memo:
    """Named carry-over between decisions in ONE run. Owned by the driver.

    Everything here is state the wire does not carry at the moment a revision
    needs it. Nothing here is a policy preference -- a fresh Memo changes the
    potion arm's timing and the rest arm's lookahead, and nothing else.
    """
    # (floor, round) pairs the potion arm has already been offered. The sim
    # runs `try_use_potions` once per turn at turn start; without this the arm
    # would be re-offered before every single card play in the turn.
    potion_rounds: set = field(default_factory=set)
    # `leads_to` kinds of the map node most recently travelled to. Revision #5.
    next_node_kinds: list = field(default_factory=list)
    # `card_select` screens this run on which a selection has already been
    # posted. The grid protocol needs it: `select_card` TOGGLES, so the second
    # visit to a screen must confirm rather than re-toggle, and `preview_showing`
    # is not a reliable signal -- the Enchant screen
    # (`NDeckEnchantSelectScreen`) reports `can_confirm: true` with
    # `preview_showing: false` and bounced a run until the watchdog caught it.
    selected_screens: set = field(default_factory=set)
    # How many times revision #1 has already offered a given card this turn.
    # A free-card rule that re-offers a card whose play was rejected is the one
    # way revision #1 could spin, so the offer count is bounded by the number
    # of copies actually in hand. Keyed by (act, floor, round, card_id).
    offered: dict = field(default_factory=dict)

    def turn_key(self, state: dict[str, Any]) -> tuple:
        run = state.get("run") or {}
        b = state.get("battle") or {}
        return (run.get("act"), run.get("floor"), b.get("round"))


@dataclass
class Decision:
    """What policy_v1 does here, and which revision produced it."""
    category: str
    action: dict[str, Any] | None
    label: str
    rationale: str
    revision: str = "v0"
    available: bool = True
    notes: dict[str, Any] = field(default_factory=dict)

    def as_log(self) -> dict[str, Any]:
        return {
            "policy": POLICY_VERSION,
            "category": self.category,
            "revision": self.revision,
            "available": self.available,
            "action": self.action,
            "label": self.label,
            "rationale": self.rationale,
            "notes": self.notes,
        }


def _unavailable(category: str, why: str) -> Decision:
    return Decision(category=category, action=None, label="(none)",
                    rationale=why, available=False)


# ------------------------------------------------------- combat helpers ----

def _wire_target_type(state: dict[str, Any], index: int) -> str:
    hand = (state.get("player") or {}).get("hand") or []
    if 0 <= index < len(hand) and isinstance(hand[index], dict):
        return str(hand[index].get("target_type", "")).lower()
    return ""


def _needs_aim(target_type: str) -> bool:
    return target_type not in ("", "self", "none", "no_target", "all_enemies")


def _lowest_hp_enemy_id(state: dict[str, Any]) -> str | None:
    living = [e for e in adapter.enemy_blobs(state) if int(e.get("hp", 0)) > 0]
    if not living:
        return None
    return adapter.enemy_id(min(living,
                                key=lambda e: (int(e.get("hp", 0)),
                                               adapter.enemy_id(e))))


def _play(state: dict[str, Any], index: int,
          target_id: str | None = None) -> dict[str, Any]:
    action: dict[str, Any] = {"action": "play_card", "card_index": index}
    tt = _wire_target_type(state, index)
    if _needs_aim(tt):
        action["target"] = target_id or _lowest_hp_enemy_id(state)
        if action["target"] is None:
            action.pop("target")
    return action


def _is_ethereal(entry: dict[str, Any]) -> bool:
    """Does the WIRE say this card vanishes at end of turn?

    Read from the game's own hover tips, not from the sheet: Ethereal is a
    base-game keyword the game prints, and a sheet lookup would miss every
    base-game card that has it. `keywords` is a list of {name, description}.
    """
    for kw in entry.get("keywords") or []:
        if isinstance(kw, dict) and str(kw.get("name") or "").strip().lower() == "ethereal":
            return True
    return "ethereal" in str(entry.get("description") or "").lower()


# ------------------------------------------------ revision #1: free first ---

def _free_expiring(state: dict[str, Any], memo: Memo) -> Decision | None:
    """R93 #1. A playable 0-cost card that vanishes at end of turn is played
    before anything is scored.

    The ruling's words: "costs nothing, cannot lose value, and the card is gone
    at end of turn. There is no board state where declining is right." This was
    the single largest contributor to the 34-of-47 turn-opener gap: Furina's
    starter relic adds an Ethereal Spotlight every turn, and policy_v0 opened
    with a blocker whenever the panic rung fired because a 0-cost card has no
    privileged status inside the score.

    THE ONE GUARD. "Play it first" is a loop if the play does not remove the
    card from hand -- a rejected play, or a card that returns itself. The memo
    remembers what was already attempted this turn and stops offering it, so
    the failure mode is one wasted round trip rather than a spinning run.
    """
    hand = [c for c in (state.get("player") or {}).get("hand") or []
            if isinstance(c, dict)]
    key = memo.turn_key(state)
    copies: dict[str, int] = {}
    for c in hand:
        copies[str(c.get("id"))] = copies.get(str(c.get("id")), 0) + 1
    for i, c in enumerate(hand):
        if c.get("can_play") is False:
            continue
        cost = c.get("cost")
        if cost != 0 and str(cost) != "0":
            continue
        if not _is_ethereal(c):
            continue
        cid = str(c.get("id"))
        seen = memo.offered.get((key, cid), 0)
        if seen >= copies.get(cid, 1):
            continue
        memo.offered[(key, cid)] = seen + 1
        return Decision(
            category="sequencing",
            action=_play(state, i),
            label=f"play {c.get('name')} [{i}] (free, expiring)",
            rationale=("R93 #1: a playable 0-cost card that is Ethereal is "
                       "played before scoring -- it costs nothing and is gone "
                       "at end of turn"),
            revision="v1.1",
            notes={"card_name": c.get("name"), "card_id": c.get("id")})
    return None


# ---------------------------------------- revision #4: the potion arm ------

def _potion_arm(state: dict[str, Any], cs, memo: Memo) -> Decision | None:
    """R93 #4. `tier0.engine.potions.try_use_potions`, asked rather than run.

    The sim's potion policy MUTATES a CombatState: it drinks, and the effect
    lands. Over the wire we need the DECISION, not the effect, so the sim's
    policy is run against the reconstructed state and the drink is read back
    out of the diff -- which potion left `player.potions`, and (for a targeted
    potion) which enemy the sim aimed it at.

    Delegation, not reimplementation: the priority ladder (block > blood
    defensively; fire-for-a-kill > weak-on-a-big-hit > fear > strength
    offensively), the elite/boss gate on offensive drinks, and the
    "fairy is passive, never proactively drunk" rule are all the sim's.

    Fires once per combat round, which is where `try_use_potions` sits in the
    sim's own turn (after the draw, before the pilot loop).
    """
    key = memo.turn_key(state)
    if key in memo.potion_rounds:
        return None
    memo.potion_rounds.add(key)

    held = [p for p in (state.get("player") or {}).get("potions") or []
            if isinstance(p, dict)]
    if not held:
        return None

    # The sim names potions by sheet id; the wire names them by its own id and
    # a display name. Only ids the sim KNOWS can be handed to its policy --
    # an unknown id would be logged UNIMPLEMENTED and silently do nothing.
    slots: list[tuple[int, str]] = []
    unknown: list[str] = []
    for i, entry in enumerate(held):
        pid = _potion_sim_id(entry)
        if pid in t0potions.KNOWN:
            slots.append((i, pid))
        else:
            unknown.append(str(entry.get("name") or entry.get("id")))
    if not slots:
        return None

    before = [pid for _, pid in slots]
    cs.player.potions = list(before)
    drank: list[str] = []
    aimed: dict[str, str] = {}

    # The aim is read by watching which enemy object the sim handed to
    # apply_potion. Rather than patching the sim to tell us, the enemy list is
    # snapshotted by identity and the drink is replayed against the SAME
    # objects -- so the target is recovered by asking the sim's own
    # target-choosing helpers with the same state it just saw.
    try:
        t0potions.try_use_potions(cs)
    except Exception as e:                                   # noqa: BLE001
        return _unavailable("potion", f"try_use_potions raised {type(e).__name__}: {e}")

    after = list(cs.player.potions)
    remaining = list(after)
    for pid in before:
        if pid in remaining:
            remaining.remove(pid)
        else:
            drank.append(pid)
    if not drank:
        return None

    pid = drank[0]
    slot = next(i for i, p in slots if p == pid)
    action: dict[str, Any] = {"action": "use_potion", "slot": slot}
    if pid in t0potions._TARGETED:
        # Same helpers the sim used one line ago, on the same state.
        tgt = (t0potions._biggest_attacker(cs)[0]
               if pid in ("weak_potion", "fear_potion")
               else t0potions._lowest_hp_enemy(cs))
        if tgt is None:
            tgt = t0potions._lowest_hp_enemy(cs)
        if tgt is not None:
            wire = _match_enemy(state, tgt)
            if wire:
                action["target"] = wire
                aimed[pid] = wire
    return Decision(
        category="potion",
        action=action,
        label=f"drink {pid} [slot {slot}]"
              + (f" -> {aimed[pid]}" if pid in aimed else ""),
        rationale=("R93 #4: tier0.engine.potions.try_use_potions on the "
                   "reconstructed combat state; the drink is read back out of "
                   "the potion-list diff, so the ladder is the sim's"),
        revision="v1.4",
        notes={"potion_id": pid, "drank_all": drank,
               "unknown_to_sim": unknown, "node_kind": cs.player.node_kind})


# Wire potion id -> sim potion id. The bridge reports base-game ids; the sim's
# vocabulary is its own. Only the overlap is drivable, and the rest is recorded
# as `unknown_to_sim` rather than guessed at.
_POTION_ALIASES = {
    "block_potion": "block_potion", "blockpotion": "block_potion",
    "fire_potion": "fire_potion", "firepotion": "fire_potion",
    "blood_potion": "blood_potion", "bloodpotion": "blood_potion",
    "strength_potion": "strength_potion", "strengthpotion": "strength_potion",
    "swift_potion": "swift_potion", "swiftpotion": "swift_potion",
    "weak_potion": "weak_potion", "weakpotion": "weak_potion",
    "fear_potion": "fear_potion", "fearpotion": "fear_potion",
    "energy_potion": "energy_potion", "energypotion": "energy_potion",
    "fairy_in_a_bottle": "fairy_in_a_bottle",
    "fairyinabottle": "fairy_in_a_bottle",
}


def _potion_sim_id(entry: dict[str, Any]) -> str:
    raw = str(entry.get("id") or entry.get("name") or "").strip().lower()
    raw = raw.replace(" ", "_").replace("-", "_")
    if raw.startswith("kleemod_"):
        raw = raw[len("kleemod_"):]
    return _POTION_ALIASES.get(raw, _POTION_ALIASES.get(raw.replace("_", ""), raw))


def _match_enemy(state: dict[str, Any], enemy) -> str | None:
    """The wire entity_id for a tier0 Enemy the sim just chose.

    Matched on (name, hp), which is unique in every board this apparatus has
    seen; ties fall back to the first match, and a tie that mattered would be
    two identical enemies at identical HP, where either answer is the same
    answer.
    """
    for e in adapter.enemy_blobs(state):
        if str(e.get("name")) == enemy.name and int(e.get("hp", -1)) == enemy.hp:
            return adapter.enemy_id(e)
    for e in adapter.enemy_blobs(state):
        if str(e.get("name")) == enemy.name:
            return adapter.enemy_id(e)
    return None


# ------------------------- revision #2: the gated block-panic ladder --------

def _gated_ladder(state: dict[str, Any], cs, notes: dict[str, Any]) -> Decision:
    """R93 #2. The pilot's ladder, with the block-panic rung made to justify itself.

    tier0's rung is: if incoming >= BLOCK_PANIC_THRESHOLD x HP and block <
    incoming, play the biggest blocker, full stop. It never asks whether the
    Block on offer can DENT the incoming, or whether killing a body would
    remove more of it than the Block prevents. Phase-0 floor 7: 39 incoming, a
    Frail-reduced 4 Block available, a 25 HP enemy that exactly 25 damage in
    hand could kill. The rung asked for the 4 Block five times running.

    WHAT IS DELEGATED AND WHAT IS OURS. Every valuation is the sim's --
    `_incoming_damage`, `_expected_damage`, `_block_value`, `_raw_block`,
    `_score`, `_lethal_card`, and `potions._intent_damage` for "how much
    incoming does this body own". The ladder's SHAPE is the sim's too. What
    this function adds is one gate between two of its rungs. That is the whole
    revision, and it is why the pilot's own scorer is called rather than
    re-typed: a re-typed scorer would make every divergence unreadable.

    Also fixed here, incidentally: policy_v0's ladder could only aim where
    tier0 aims (lowest HP). The kill line aims at the body it is killing, which
    the wire allows and the sim's single-target model does not express.
    """
    weights = loader.pilot_weights(PILOT_ID)
    playable = [c for c in cs.player.hand
                if pilot_policy.card_playable(cs, c)]
    if not playable:
        return Decision(category="sequencing", action={"action": "end_turn"},
                        label="end_turn",
                        rationale="no playable card in hand",
                        revision="v1.2", notes=notes)

    incoming = pilot_policy._incoming_damage(cs)
    dmg = [pilot_policy._expected_damage(cs, c) for c in playable]
    blk = [pilot_policy._block_value(cs, c, incoming) for c in playable]

    # Rung 1, unchanged: a single-card lethal ends the fight.
    lethal = pilot_policy._lethal_card(cs, playable, dmg)
    if lethal is not None:
        return _from_card(state, cs, lethal, "v1.2",
                          "the sim's lethal rung: one card clears every "
                          "remaining enemy HP+block", notes)

    panic = (incoming >= C.BLOCK_PANIC_THRESHOLD * max(1, cs.player.hp)
             and cs.player.block < incoming)
    gate: dict[str, Any] = {"panic_condition": bool(panic),
                            "incoming": round(float(incoming), 1),
                            "block_held": cs.player.block}

    if panic:
        blockers = [c for c in playable if pilot_policy._raw_block(cs, c) > 0]
        uncovered = max(0.0, float(incoming) - cs.player.block)
        best_block = (max(blockers, key=lambda c: pilot_policy._raw_block(cs, c))
                      if blockers else None)
        prevented = (min(pilot_policy._raw_block(cs, best_block), uncovered)
                     if best_block is not None else 0.0)
        gate.update(uncovered=round(uncovered, 1),
                    prevented=round(float(prevented), 1))

        kill = _best_kill_line(cs, playable, dmg)
        if kill is not None:
            card, enemy, removed = kill
            gate.update(kill_target=enemy.name, kill_removes=int(removed))
            if removed > prevented:
                wire_target = _match_enemy(state, enemy)
                return _from_card(
                    state, cs, card, "v1.2-kill",
                    (f"R93 #2 kill-vs-block: killing {enemy.name} removes "
                     f"{int(removed)} incoming, the best Block prevents "
                     f"{prevented:.0f}"),
                    {**notes, "gate": gate}, target_id=wire_target)

        if best_block is not None and uncovered > 0 and \
                prevented >= BLOCK_MATTERS_FRACTION * uncovered:
            return _from_card(
                state, cs, best_block, "v1.2-panic",
                (f"R93 #2 gate HELD: the panic rung fires and the Block on "
                 f"offer prevents {prevented:.0f} of {uncovered:.0f} "
                 f"uncovered, at or above the {BLOCK_MATTERS_FRACTION:.2f} bar"),
                {**notes, "gate": gate})

        gate["outcome"] = "gated_to_scoring"

    # Rung 3, unchanged: the pilot's weighted score over everything playable.
    scored = [(pilot_policy._score(cs, c, weights, dmg[i], blk[i]), -i, c)
              for i, c in enumerate(playable)]
    best_score, _, best = max(scored, key=lambda t: t[:2])
    if best_score <= 0:
        return Decision(category="sequencing", action={"action": "end_turn"},
                        label="end_turn",
                        rationale=("no playable card scored above zero, which "
                                   "is the pilot's end-of-turn condition"),
                        revision="v1.2", notes={**notes, "gate": gate})
    return _from_card(state, cs, best, "v1.2",
                      f"the sim's scorer picked it at {best_score:.2f}",
                      {**notes, "gate": gate})


def _best_kill_line(cs, playable, dmg) -> tuple | None:
    """The single card that kills a body and the incoming that body owns.

    "How much incoming does this enemy own" is `potions._intent_damage`, the
    sim's own per-enemy telegraph reader -- the same function the sim's potion
    policy uses to decide whether a turn is survivable.

    APPROXIMATION, DECLARED: `_expected_damage` prices a card against tier0's
    default target, so using it against a chosen enemy overstates any card with
    a target-conditional rider. GItS starters carry none, and the alternative
    (rebuilding the state once per candidate target) costs a scoring pass per
    enemy per decision on the hot path of a soak.
    """
    best = None
    for enemy in cs.living_enemies:
        owed = t0potions._intent_damage(cs, enemy)
        if owed <= 0:
            continue
        need = enemy.hp + enemy.block
        for card, d in zip(playable, dmg):
            if d >= need:
                if best is None or owed > best[2]:
                    best = (card, enemy, owed)
                break
    return best


def _from_card(state: dict[str, Any], cs, card, revision: str,
               why: str, notes: dict[str, Any],
               target_id: str | None = None) -> Decision:
    index = next((i for i, c in enumerate(cs.player.hand) if c is card), None)
    if index is None:
        return _unavailable(
            "sequencing",
            "the ladder returned a card that is not in the reconstructed hand; "
            "adapter bug, not a policy result")
    action = _play(state, index, target_id)
    label = f"play {card.name} [{index}]"
    if action.get("target"):
        label += f" -> {action['target']}"
    return Decision(category="sequencing", action=action, label=label,
                    rationale=why, revision=revision,
                    notes={**notes, "card_name": card.name,
                           "card_id": card.id})


def _combat(state: dict[str, Any], memo: Memo) -> Decision:
    cs, notes = adapter.build_combat_state(state)
    pot = _potion_arm(state, cs, memo)
    if pot is not None:
        if pot.available:
            return pot
        # The sim's potion policy raised part-way through. Whatever it applied
        # to the reconstruction before it did must not leak into the scoring
        # pass, so the state is rebuilt from the wire rather than reused.
        cs, notes = adapter.build_combat_state(state)
    free = _free_expiring(state, memo)
    if free is not None:
        return free
    return _gated_ladder(state, cs, notes)


# ------------------------------ revision #3: the map, one ply deeper --------

def _map(state: dict[str, Any], memo: Memo) -> Decision:
    """R93 #3. `leads_to` is on the wire; use it.

    policy_v0 scored the offered nodes one step deep, against `tier05.route`'s
    backward induction over the whole act DAG. All three Phase-0 path
    differences were that horizon gap and nothing else. The bridge already
    ships a one-level lookahead per travelable node
    (`McpMod.StateBuilder`: `option["leads_to"] = children`), so the reduction
    can go from depth 1 to depth 2 for free.

    THE ARITHMETIC IS THE SIM'S. `tier05.route._plan` sums room values along a
    path UNDISCOUNTED (`value(room) + sv`) and re-plans from live run state at
    every floor with ONE value closure for the whole DAG. So the faithful
    truncation at depth 2 is `value(node) + max(value(child))`, with the same
    closure -- no discount factor invented here, because inventing one would
    make this a different policy rather than a shallower one.

    Still a reduction, and it says so: two plies, not the whole act. The Phase-0
    floor-7 case (an Elite two floors out) is still invisible.
    """
    options = ((state.get("map") or {}).get("next_options")
               or state.get("next_options") or [])
    if not options:
        return _unavailable("path", "no next_options on the wire")

    p = state.get("player") or {}
    run = state.get("run") or {}
    st = t5route.RouteState(
        hp=int(p.get("hp", 0)), max_hp=int(p.get("max_hp", 1)),
        gold=int(p.get("gold", 0)),
        deck_size=len(adapter.deck_cards(state)),
        floor=int(run.get("floor", 0)), act=int(run.get("act", 1)),
        elites_taken=int(state.get("elites_taken", 0)),
        rests_taken=int(state.get("rests_taken", 0)))

    want = {t5route.ELITE: 10.0, t5route.SHOP: 5.0, t5route.TREASURE: 5.0,
            t5route.UNKNOWN: 4.0, t5route.REST: 6.0, t5route.NORMAL: 2.0}
    bar = 0.55 + 0.15 * st.elites_taken
    elite_ok = st.hp_frac >= bar and st.elites_taken < 4
    value = t5route._make_value(want, st, elite_ok)

    scored = []
    for i, opt in enumerate(options):
        kind = policy_v0._room_kind(opt)
        here = value(t5route.Room(i, st.floor, kind))
        children = opt.get("leads_to") if isinstance(opt, dict) else None
        ahead = 0.0
        child_kinds: list[str] = []
        if isinstance(children, list) and children:
            child_kinds = [policy_v0._room_kind(c) for c in children]
            ahead = max(value(t5route.Room(i, st.floor + 1, k))
                        for k in child_kinds)
        # Ties break on offered index, the same convention `_plan` uses so a
        # seed replays identically.
        scored.append((here + ahead, -i, i, kind, child_kinds, here, ahead))

    best = max(scored, key=lambda t: t[:2])
    memo.next_node_kinds = list(best[4])
    detail = ", ".join(f"[{t[2]}]{t[3]}={t[5]:.1f}+{t[6]:.1f}" for t in scored)
    return Decision(
        category="path",
        action={"action": "choose_map_node", "index": best[2]},
        label=f"node {best[2]} ({best[3]})",
        rationale=("R93 #3: hunter want-table, two plies "
                   f"(node + best successor), undiscounted as tier05.route "
                   f"sums them: {detail}; elite bar {bar:.2f} vs hp_frac "
                   f"{st.hp_frac:.2f}"),
        revision="v1.3",
        notes={"reduced_from": "whole-map backward induction",
               "plies": 2, "elite_ok": elite_ok, "n_options": len(options),
               "leads_to": best[4]})


# ------------------------- revision #5: next_fight into the rest arm --------

def _rest(state: dict[str, Any], memo: Memo) -> Decision:
    """R93 #5. `rest_action` already takes the flag; stop passing False blindly.

    Phase-0's one rest decision diverged because `next_fight` was hard-coded
    False -- "we are passing False because we did not look, not because we
    know". The flag is DRAFTER v5(b)'s elite lookahead: with it set, the heal
    outranks the smith below REST_PREFIGHT_HEAL_THRESHOLD, which is the rung
    that stops a run walking into a guaranteed elite at half HP.

    Where the flag comes from: the `leads_to` the map screen showed for the
    node we travelled to (memo, revision #3's by-product). If this rest is the
    last floor before the act boss, that counts too.
    """
    p = state.get("player") or {}
    deck_ids = [c.id for c in adapter.deck_cards(state)
                if policy_v0._resolves_to_a_sim_row(c.id)]
    # The memo carries tier05.route's OWN room-kind constants (the map arm
    # reduced them with `policy_v0._room_kind`), not wire words -- and that
    # module maps a boss node onto ELITE, which is exactly the distinction
    # `next_fight` cares about: "the node after this rest is an Elite/Boss".
    kinds = list(memo.next_node_kinds)
    next_fight = t5route.ELITE in kinds
    what, which = t5model.rest_action(
        deck_ids, int(p.get("hp", 0)), int(p.get("max_hp", 1)),
        archetype=ARCHETYPE, next_fight=next_fight)
    blob = state.get("rest_site") or {}
    options = ((blob.get("options") if isinstance(blob, dict) else None)
               or state.get("options") or [])
    index = policy_v0._match_rest_option(options, what)
    return Decision(
        category="resource",
        action=({"action": "choose_rest_option", "index": index}
                if index is not None else {"action": "proceed"}),
        label=f"{what}" + (f" ({which})" if which else ""),
        rationale=("R93 #5: tier05.model.rest_action on a deck of "
                   f"{len(deck_ids)} at {p.get('hp')}/{p.get('max_hp')} HP, "
                   f"next_fight={next_fight} from the map lookahead "
                   f"{kinds or '(none seen)'}"),
        revision="v1.5",
        notes={"sim_choice": what, "sim_target": which,
               "next_fight": next_fight, "next_node_kinds": kinds,
               "option_matched": index is not None})


# ------------------- revision #6: the in-combat choice overlay arm ----------

def _is_companion(card) -> bool:
    return card.companion is not None or bool(card.nation)


def _shop(state: dict[str, Any]) -> Decision:
    """policy_v0's shop arm, over CARDS only.

    NOT a revision -- a defect fix, found by the fourth validation soak.
    policy_v0's shelf filter accepts an item whose `type` is `"card"` OR the
    empty string, and the shop's card-REMOVAL service comes across the wire
    with no type. So the policy bought a service, the remove screen it opened
    was declined, the driver cancelled it, and the run bounced
    shop -> card_select -> shop until the watchdog stopped it.

    Buying a service you cannot follow through on is not a judgment call the
    bot is entitled to make, so the untyped items are dropped rather than
    guessed at. They are counted in the notes: if a real card ever arrives
    untyped, that count is where it will show up.
    """
    items = state.get("items") or (state.get("shop") or {}).get("items") or []
    typed = [it for it in items if isinstance(it, dict)]
    untyped = [str(it.get("name")) for it in typed
               if not str(it.get("type") or "").strip()]

    # THE INDEX HAS TO COME BACK. `shop_purchase` takes an index into the
    # SHELF THE GAME IS SHOWING, and policy_v0 returns an index into whatever
    # list it was handed. Narrowing the list without remapping would buy a
    # different item than the one the policy chose -- silently, and more often
    # the more items were filtered. Caught by its own test rather than by a
    # soak, which is the only reason it is not a second night's defect.
    keep = [i for i, it in enumerate(typed)
            if str(it.get("type", "")).lower() == "card"]
    narrowed = dict(state)
    narrowed["items"] = [typed[i] for i in keep]
    narrowed.pop("shop", None)
    d = _from_v0(policy_v0._shop(narrowed))
    if d.action and d.action.get("action") == "shop_purchase":
        local = int(d.action.get("index", 0))
        if 0 <= local < len(keep):
            d.action = {**d.action, "index": keep[local]}
        else:
            return _unavailable(
                "resource",
                f"the shop arm returned index {local} against a shelf of "
                f"{len(keep)}; refusing to post an unmapped purchase")
    d.notes = {**d.notes, "untyped_items_skipped": untyped,
               "shelf_indices": keep}
    return d


_SCREEN_WORDS = (
    ("remove", ("remove", "purge", "destroy", "eliminate")),
    ("upgrade", ("upgrade", "smith")),
)


def _screen_kind(blob: dict[str, Any]) -> str:
    """upgrade / remove / "", read from the wire's own words.

    LEARNED FROM A LIVE STALL. The shop's card-removal service reports
    `screen_type: "select"` with `prompt: "Choose a card to Remove."` -- the
    type field says nothing and the prompt says everything. Keying only on
    `screen_type` sent that screen to the generic fallback, which scored the
    options with `score_offer` and would have removed the deck's BEST card.
    The prompt is read because it is the only place the game states intent.
    """
    st = str(blob.get("screen_type") or "").lower()
    for kind, _ in _SCREEN_WORDS:
        if st == kind:
            return kind
    text = str(blob.get("prompt") or "").lower()
    for kind, words in _SCREEN_WORDS:
        if any(w in text for w in words):
            return kind
    return ""


def _screen_key(state: dict[str, Any], blob: dict[str, Any]) -> tuple:
    run = state.get("run") or {}
    return (run.get("act"), run.get("floor"),
            str(blob.get("screen_type") or ""), str(blob.get("prompt") or ""))


def _card_select_screen(state: dict[str, Any], memo: Memo) -> Decision:
    """Dispatch for `card_select`, which is three screens wearing one name.

    THE GRID PROTOCOL, and it cost a soak run to learn. A grid screen TOGGLES
    on `select_card` and needs an explicit `confirm_selection`; a
    choose-a-card screen picks immediately and needs no confirm. The wire says
    which one you are on: `can_confirm` turns true once a selection is
    registered and `preview_showing` goes with it. Without this the driver
    re-toggled the same card twelve times and the watchdog -- correctly -- read
    it as a stall.
    """
    blob = state.get("card_select") or {}
    key = _screen_key(state, blob)
    already = key in memo.selected_screens
    if blob.get("can_confirm") and (blob.get("preview_showing") or already):
        memo.selected_screens.discard(key)
        return Decision(
            category="resource",
            action={"action": "confirm_selection"},
            label="confirm selection",
            rationale=("grid screen: a selection is registered and the wire "
                       "reports can_confirm, so the outstanding verb is the "
                       "confirm, not another toggle"),
            revision="v1.6",
            notes={"basis": "grid_confirm",
                   "registered_by": "preview_showing" if
                   blob.get("preview_showing") else "prior_selection",
                   "screen_type": blob.get("screen_type"),
                   "prompt": blob.get("prompt")})
    kind = _screen_kind(blob)
    if kind:
        # policy_v0's arm gates on `screen_type` being literally 'upgrade' or
        # 'remove'. Handing it the kind we read off the prompt is a
        # TRANSLATION, not a policy change: the decision it then makes is
        # still `rest_action`'s smith/thin order, unmodified.
        translated = dict(state)
        translated["card_select"] = {**blob, "screen_type": kind}
        d = _from_v0(policy_v0._card_select(translated))
        d.notes = {**d.notes, "screen_kind_from": "prompt"
                   if str(blob.get("screen_type") or "").lower() != kind
                   else "screen_type"}
        if d.available:
            return _remember_selection(d, memo, key)
        # THE SIM'S LADDER CAN REFUSE A SCREEN WE ARE ALREADY COMMITTED TO.
        # `rest_action` answers "what would I do at a rest site", and its
        # on-plan-upgrade rung outranks its thin rung -- so on a remove screen
        # it routinely wants to upgrade, policy_v0 declines rather than
        # delegate across, and the driver cancels. At a rest site cancelling
        # costs nothing. At a shop's removal service the gold is already
        # spent, and the fourth validation soak bounced there forever.
        #
        # So a committed screen gets a delegated answer rather than a shrug:
        # the card the DRAFT policy would least want to add is the card to
        # remove. That is `score_offer`, read in the direction the screen asks
        # -- still the sim's valuation, still no heuristic of ours.
        return _remember_selection(
            _committed_screen(state, blob, kind, d.rationale), memo, key)
    return _remember_selection(_choice_overlay(state), memo, key)


def _remember_selection(d: Decision, memo: Memo, key: tuple) -> Decision:
    """Record that a `select_card` has been posted for this screen.

    The grid protocol's second half: a toggle that is not followed by a
    confirm is a bounce, and `preview_showing` does not reliably say a
    selection landed.
    """
    if d.action and d.action.get("action") == "select_card":
        memo.selected_screens.add(key)
    return d


def _committed_screen(state: dict[str, Any], blob: dict[str, Any], kind: str,
                      why_v0_declined: str) -> Decision:
    entries = [e for e in (blob.get("cards") or []) if isinstance(e, dict)]
    deck = adapter.deck_cards(state)
    scored: list[tuple[float, int, Any]] = []
    for i, e in enumerate(entries):
        card, approx = adapter.resolve_card(e)
        if approx:
            continue
        try:
            scored.append((t5draft.score_offer(card, deck, ARCHETYPE), i, card))
        except Exception:                                    # noqa: BLE001
            continue
    if not scored:
        return _unavailable(
            "resource",
            f"the sim declined this '{kind}' screen ({why_v0_declined}) and no "
            f"option resolves to a sim card row to break the tie with")
    # remove -> the least wanted; upgrade -> the most wanted. Ties break on
    # offered index so a seed replays identically.
    pick = (min(scored, key=lambda t: (t[0], t[1])) if kind == "remove"
            else max(scored, key=lambda t: (t[0], -t[1])))
    return Decision(
        category="resource",
        action={"action": "select_card", "index": pick[1]},
        label=f"{kind} {pick[2].name} [{pick[1]}]",
        rationale=(f"the sim's rest ladder declined this screen "
                   f"({why_v0_declined}); the screen is already paid for, so "
                   f"tier05.draft.score_offer breaks it in the direction the "
                   f"screen asks -- {pick[2].name} at {pick[0]:.2f}"),
        revision="v1.6",
        notes={"basis": f"score_offer_{'inverse' if kind == 'remove' else 'direct'}",
               "screen_kind": kind,
               "scores": {c.name: round(s, 2) for s, _, c in scored}})


def _choice_overlay(state: dict[str, Any]) -> Decision:
    """R93 #6. Center Stage vs Guest Cast, keyed on deck composition.

    policy_v0 declined every `choose` overlay -- "tier05 has no policy for it"
    -- which was honest for a counterfactual and useless for a driver. These
    are recurring and consequential: Furina's starter relic puts an Ethereal
    Spotlight in hand EVERY TURN, so this screen is one of the most frequent
    decisions in a Furina run and it was invisible to the whole measurement.

    The rule, and why it is a deck question rather than a board question:
    Center Stage makes Furina's own cards generate 2 Fanfare and gives them no
    numeric boost; Guest Cast makes every Companion card 50% stronger and stops
    them generating Fanfare. Which is worth more depends on how much Companion
    text the deck holds, and on nothing about the current board -- so it is
    answered off the deck, deterministically.

    Deck-management overlays (upgrade / remove) still go to policy_v0's arm,
    which delegates them to `rest_action`'s smith order. Only the CHOOSE
    screens are new here.
    """
    blob = state.get("card_select") or {}
    screen = str(blob.get("screen_type") or "").lower()
    entries = [e for e in (blob.get("cards") or []) if isinstance(e, dict)]
    if not entries:
        return _unavailable("resource", "no cards on the wire to choose between")

    names = [str(e.get("name") or "") for e in entries]
    lowered = [n.strip().lower() for n in names]

    deck = adapter.deck_cards(state)
    companions = [c for c in deck if _is_companion(c)]
    share = (len(companions) / len(deck)) if deck else 0.0

    if "guest cast" in lowered or "center stage" in lowered:
        want_guest = ("guest cast" in lowered
                      and share >= COMPANION_SHARE_FOR_GUEST_CAST)
        wanted = "guest cast" if want_guest else "center stage"
        index = next((i for i, n in enumerate(lowered) if n == wanted), 0)
        return Decision(
            category="resource",
            action={"action": "select_card", "index": index},
            label=f"{names[index]} [{index}]",
            rationale=("R93 #6: Spotlight mode on deck composition -- "
                       f"{len(companions)} Companion cards of {len(deck)} "
                       f"({share:.0%}) against a "
                       f"{COMPANION_SHARE_FOR_GUEST_CAST:.0%} bar"),
            revision="v1.6",
            notes={"basis": "companion_density", "companion_share": round(share, 3),
                   "companions": len(companions), "deck_size": len(deck),
                   "screen_type": screen, "options": names})

    # A choose overlay we have no named rule for. Score the options with the
    # draft policy's own offer valuation against the live deck -- "which of
    # these do I most want" is the question `score_offer` answers -- and fall
    # back to the first option when nothing resolves to a sheet row.
    scores: dict[str, float] = {}
    resolved: list[tuple[int, Any]] = []
    for i, e in enumerate(entries):
        card, approx = adapter.resolve_card(e)
        if not approx:
            resolved.append((i, card))
    for i, card in resolved:
        try:
            scores[card.name] = round(t5draft.score_offer(card, deck, ARCHETYPE), 2)
        except Exception:                                    # noqa: BLE001
            pass
    if scores:
        pick_i, pick = max(
            ((i, c) for i, c in resolved if c.name in scores),
            key=lambda t: (scores[t[1].name], -t[0]))
        return Decision(
            category="resource",
            action={"action": "select_card", "index": pick_i},
            label=f"{pick.name} [{pick_i}]",
            rationale=f"R93 #6 fallback: tier05.draft.score_offer over the "
                      f"offered options under the {ARCHETYPE} plan: {scores}",
            revision="v1.6",
            notes={"basis": "score_offer", "scores": scores,
                   "screen_type": screen, "options": names})
    return Decision(
        category="resource",
        action={"action": "select_card", "index": 0},
        label=f"{names[0]} [0] (forced)",
        rationale=("R93 #6 last resort: no option resolves to a sim card row "
                   "and none is a named Spotlight mode, so the first option is "
                   "taken to keep the run moving. FLAGGED, not silent."),
        revision="v1.6",
        notes={"basis": "first_option_fallback", "screen_type": screen,
               "options": names, "forced_default": True})


# ------------------------------------------------------------- dispatch ----

def decide(state: dict[str, Any], memo: Memo | None = None) -> Decision:
    """policy_v1's answer at `state`, with revision #7's names attached.

    A crash in any arm returns an unavailable Decision rather than propagating:
    the run is the expensive half, and a policy that can end one by raising is
    a policy that cannot soak.
    """
    memo = memo if memo is not None else Memo()
    st = str(state.get("state_type") or "unknown")
    if st in policy_v0.NO_COUNTERFACTUAL:
        d = _unavailable(st, policy_v0.NO_COUNTERFACTUAL[st])
    else:
        try:
            if st in ("monster", "elite", "boss"):
                d = _combat(state, memo)
            elif st == "card_reward":
                d = _from_v0(policy_v0._card_reward(state))
            elif st == "map":
                d = _map(state, memo)
            elif st == "rest_site":
                d = _rest(state, memo)
            elif st in ("shop", "fake_merchant"):
                d = _shop(state)
            elif st == "card_select":
                d = _card_select_screen(state, memo)
            else:
                d = _unavailable(
                    st, f"'{st}' is a mechanical screen with no sim decision "
                        f"behind it")
        except Exception as e:                               # noqa: BLE001
            d = _unavailable(st, f"policy_v1 raised {type(e).__name__}: {e}")

    # Revision #7. Every action this policy emits carries the identity of what
    # it names, resolved at the state it was decided against. Attached HERE,
    # once, so no arm can forget.
    if d.action:
        d.notes = {**d.notes, "names": naming.describe(state, d.action)}
    return d


def _from_v0(cf: policy_v0.Counterfactual) -> Decision:
    """A policy_v0 arm, unchanged, wearing policy_v1's return type.

    Draft, shop and the deck-management overlays were not revised: the Phase-0
    divergences there were diagnosed as SIM scoring gaps (R96 routed all three)
    rather than as things Understudy should route around. Re-deciding them here
    would be authoring design, which bots do not do.
    """
    return Decision(category=cf.category, action=cf.action, label=cf.label,
                    rationale=cf.rationale, revision="v0",
                    available=cf.available, notes=dict(cf.notes))
