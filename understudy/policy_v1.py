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

REVISIONS #8-#11 (2026-08-13 onward, the Act-2 reach pass and its follow-up).
Four DEFECT fixes, not new preferences: each one restores an input this module
already declares it reads and was not reading. Named here because R93's
convention is that a revision has a number, a justification from observed
decisions, and a log.

  #8 the plan follows the character   `_plan_for`, `_card_reward`, `_rest`,
                                      `_score_offers`
  #9 elites/rests counted per act     `_map` (+ `Memo.elites_taken`)
  #10 a spent rest site is a decision `_rest`
  #11 a delegated select screen has   `_card_select_screen`,
      a HISTORY                       `_reindex_to_screen`

  #8, from the 20260813-002613 soak, three runs of KLEE: every draft
  rationale read `score_offer under the SALON plan`, and `Combustion Study`,
  `Explosives Workshop` and `Catalytic Converter` -- Klee cards -- all scored
  literally 0.0 while a generic `Dodge Roll` was taken three times. The cause
  is one line: `ARCHETYPE = policy_v0.ARCHETYPE` and policy_v0's is the
  string `"salon"`, written when the bot played Furina and correct only for
  her. A bot playing Klee that drafts for Furina's salon is not a policy, it
  is a bug, and it is the largest single thing between this bot and Act 2.
  **Consequence, stated because it is not free: every Klee soak recorded
  before this date drafted under the wrong plan, so its draft telemetry
  describes a deck nobody would build. Those numbers are archive.** The
  Furina arm is unchanged by construction -- `resolve_plan("furina", None)`
  returns `salon`, the string that was hardcoded.

  #9, from the same soak: all 48 path decisions across three runs print
  `elite bar 0.55`, including in run 3 AFTER two elites had been taken. The
  rising bar the arm's own source documents ("55% / 70% / 85%", tier05.route
  `hunter`) never engages, because `state.get("elites_taken", 0)` reads a key
  the wire does not carry and never has. The bot therefore takes every elite
  it is offered above half HP -- 5 of them in 3 runs, at a median 35 HP each
  out of 62 -- and meets the act boss at 41-44 HP. The count is the arm's own
  history of its own choices, kept in the Memo where the other carried state
  already lives.

  #10, same soak, 9 of the 11 "forced defaults": choosing Rest re-serves the
  rest screen with `options: []`, the arm re-decides, nothing matches, and
  `_last_resort` proceeds -- counted as "a decision nobody made" when in fact
  the rest was taken and the screen is SPENT (the HP jumps +18 right before
  each one). A counter whose entries are 82% bookkeeping cannot do the job
  that counter exists for.

  #11, from the 20260813-010707 soak, run 2 (EB-106): the run ends
  `no_progress` on an Act-2 `card_select` at floor 20 -- the Amalgamator
  event's "Choose 2 cards to Remove." -- with the SAME index posted twelve
  times ("Toggling card selection: Kaboom!") and `can_confirm` never turning
  true. The multi-select lesson was already learned twice and written into
  `_choice_overlay` and `_committed_screen`, both of which skip an index the
  Memo says was toggled this visit; the third path -- the one that delegates
  an upgrade/remove screen to policy_v0 -- recorded the toggle into the Memo
  and then never read it back. `Memo.selected_screens` was working, and the
  cycle is the `card_select` arm re-toggling, not the event re-serving: the
  visit was never left, so nothing was cleared. Fixed by WITHHOLDING the
  toggled cards from the offer policy_v0 is asked about, which is the only
  shape available -- that module is frozen.

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

from understudy import adapter, committed, naming, policy_v0
from understudy.rng import policy_rng

CHARACTER = policy_v0.CHARACTER
ARCHETYPE = policy_v0.ARCHETYPE
PILOT_ID = policy_v0.PILOT_ID


# --------------------- revision #8: the plan follows the character ----------

def _plan_for(state: dict[str, Any]) -> tuple[str, str]:
    """(character id, assigned plan) for the run on the wire.

    R68's rule is that `tier05.runner.resolve_plan` is the single source of
    truth for character -> plan, and this asks it rather than deciding. The
    character comes off the wire's own `player.character` (the DISPLAY name,
    which is what the game reports: `"Klee"`, `"Sangonomiya Kokomi"`), matched
    against `tier0.roster` -- the registry, not a table written here, because
    a second table is a second thing to forget to update when slot 4 lands.

    Falls back to policy_v0's pair when the wire says nothing recognisable
    (a menu state, a reference anchor, a character this repo does not ship).
    The fallback is Furina/salon, which is what every caller here used
    unconditionally until this revision, so an unrecognised run behaves
    exactly as it did before rather than in some third way.
    """
    who = str(((state.get("player") or {}).get("character") or "")).strip()
    if not who:
        return CHARACTER, ARCHETYPE
    from tier0 import roster
    from tier05 import runner as t5runner
    key = who.casefold()
    for ch in roster.ROSTER:
        if key in (ch.id.casefold(), ch.display.casefold()):
            try:
                plan, _pilot = t5runner.resolve_plan(ch.id, None)
            except ValueError:                               # pragma: no cover
                return ch.id, ARCHETYPE
            return ch.id, plan
    return CHARACTER, ARCHETYPE


def _plan(state: dict[str, Any], memo: "Memo | None" = None) -> str:
    """The assigned plan, resolved once per run and carried on the Memo.

    Cached because it is read on every draft, rest and shop screen and the
    answer cannot change inside a run; carried on the Memo rather than in a
    module global because a global would leak between runs of one soak.
    """
    if memo is None:
        return _plan_for(state)[1]
    if memo.plan is None:
        who, plan = _plan_for(state)
        # A menu/game-over state has no character, and resolving there would
        # freeze the fallback in for the whole run. Only a state that named
        # somebody gets to fix the answer.
        if not ((state.get("player") or {}).get("character")):
            return ARCHETYPE
        memo.character, memo.plan = who, plan
    return memo.plan

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
    # `card_select` screen key -> the set of indices already toggled on it.
    #
    # The grid protocol needs all of this, and each part was learned from a
    # bounced run. `select_card` TOGGLES, so a second visit must not re-issue
    # the same index. `preview_showing` is not a reliable "a selection landed"
    # signal -- the Enchant screen (`NDeckEnchantSelectScreen`) reports
    # `can_confirm: true` with `preview_showing: false`. And some screens want
    # SEVERAL cards ("Choose 2 Common Cards to Add to Your Deck",
    # `simple_select`, `can_confirm: false` until the quota is met), so the
    # arm has to pick a DIFFERENT card each visit rather than the same best one.
    selected_screens: dict = field(default_factory=dict)
    # (turn key, card id) pairs the GAME rejected this turn. The wire's
    # `can_play` is the primary filter; this is the backstop for the case where
    # the wire says yes and the play still comes back an error, which a boss
    # debuff produced on a live run ("Card 'Stage Presence' cannot be played").
    rejected: set = field(default_factory=set)
    # Revision #8. The run's character id and assigned plan, resolved once
    # from the first state that names somebody.
    character: str | None = None
    plan: str | None = None
    # Revision #9. Elites and rests this ACT, counted from the arm's own
    # chosen nodes, because the wire carries neither. `act_counted` is the act
    # the counts belong to; `tier05.route` declares both figures act-local, so
    # they reset when the act does.
    elites_taken: int = 0
    rests_taken: int = 0
    act_counted: int | None = None
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
    rejected_here = memo.rejected
    for i, c in enumerate(hand):
        if c.get("can_play") is False:
            continue
        if (key, str(c.get("id"))) in rejected_here:
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

def _gated_ladder(state: dict[str, Any], cs, notes: dict[str, Any],
                  vetoed: set | None = None) -> Decision:
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
    vetoed = vetoed or set()
    weights = loader.pilot_weights(PILOT_ID)
    # THE GAME'S OWN PLAYABILITY VERDICT COMES FIRST. tier0's `card_playable`
    # knows about energy and nothing else, so a card the GAME has blocked --
    # a boss debuff, an unplayable status, a condition the sim does not model
    # -- scored normally, was chosen, was rejected, and was chosen again. That
    # loop reached the cycle watchdog on an Act 1 boss at 379 actions.
    playable = [c for i, c in enumerate(cs.player.hand)
                if i not in vetoed and pilot_policy.card_playable(cs, c)]
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


def _vetoed(state: dict[str, Any], memo: Memo) -> set:
    """Hand indices no arm may choose: the game says no, or it already said no.

    Two sources, and the first is the one that should have been there all
    along. The wire marks every hand card `can_play` with an
    `unplayable_reason`, and the adapter does not carry it -- so tier0 decided
    playability on energy alone. The second is the memo: a play the bridge
    rejected this turn is not offered again, because re-offering it is a loop
    and a loop is a lost run.
    """
    key = memo.turn_key(state)
    out = set()
    for i, c in enumerate((state.get("player") or {}).get("hand") or []):
        if not isinstance(c, dict):
            continue
        if c.get("can_play") is False:
            out.add(i)
        elif (key, str(c.get("id"))) in memo.rejected:
            out.add(i)
    return out


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
    return _gated_ladder(state, cs, notes, _vetoed(state, memo))


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
    act = int(run.get("act", 1))
    # REVISION #9. `elites_taken`/`rests_taken` are act-local by tier05.route's
    # own declaration, so they reset with the act. Reading them off the wire --
    # which is what this arm did, and what the FROZEN policy_v0 still does --
    # yields a permanent 0, because no build of this bridge has ever sent
    # either key. The dial the arm computes from them (`bar`) therefore sat at
    # its floor value for every path decision ever taken.
    if memo.act_counted != act:
        memo.act_counted, memo.elites_taken, memo.rests_taken = act, 0, 0
    st = t5route.RouteState(
        hp=int(p.get("hp", 0)), max_hp=int(p.get("max_hp", 1)),
        gold=int(p.get("gold", 0)),
        deck_size=len(adapter.deck_cards(state)),
        floor=int(run.get("floor", 0)), act=act,
        elites_taken=memo.elites_taken,
        rests_taken=memo.rests_taken)

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
    # REVISION #9. Count what we CHOSE, at the moment we choose it. The count
    # is the arm's own history; nothing else on the wire can supply it. The
    # act boss reduces to ELITE in `policy_v0._room_kind` (the rest arm's
    # `next_fight` depends on that and says so), so the last node of an act
    # increments the elite count -- harmlessly, since the act ends there and
    # the counter resets.
    if best[3] == t5route.ELITE:
        memo.elites_taken += 1
    elif best[3] == t5route.REST:
        memo.rests_taken += 1
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
    archetype = _plan(state, memo)                       # revision #8
    what, which = t5model.rest_action(
        deck_ids, int(p.get("hp", 0)), int(p.get("max_hp", 1)),
        archetype=archetype, next_fight=next_fight)
    blob = state.get("rest_site") or {}
    options = ((blob.get("options") if isinstance(blob, dict) else None)
               or state.get("options") or [])

    # REVISION #10. A SPENT SCREEN IS NOT AN UNANSWERED DECISION. Choosing
    # Rest re-serves this screen with every option gone, and the arm used to
    # re-decide, fail to match, and decline -- so `_last_resort` proceeded and
    # the run recorded a `forced_default`. That counter's job is to name
    # screens the policy could not answer, and 9 of the 11 entries in the
    # 20260813-002613 soak were this: a rest that HAD been taken (the HP row
    # jumps +18 immediately before each one). Proceeding off an exhausted
    # screen is the only correct move and this arm now owns it.
    #
    # GATED ON `can_proceed`, and that gate is EB-13 itself: a rest site with
    # nothing enabled AND no exit is the bounce that row was filed for, where
    # posting `proceed` got "No proceed button available or enabled" for every
    # remaining action of the run. When the screen refuses its own exit this
    # falls through to the decline below, and `_last_resort` answers the
    # screen instead. A refused verb is not a fallback.
    enabled = [o for o in options
               if not (isinstance(o, dict) and o.get("is_enabled") is False)]
    can_proceed = bool(blob.get("can_proceed")) if isinstance(blob, dict) \
        else False
    if not enabled and can_proceed:
        return Decision(
            category="resource",
            action={"action": "proceed"},
            label="proceed (rest site spent)",
            rationale=("this rest site offers no enabled option -- it has "
                       "already been spent this visit, and proceeding is the "
                       "only move on the screen"),
            revision="v1.10",
            notes={"sim_choice": what, "sim_target": which,
                   "next_fight": next_fight, "next_node_kinds": kinds,
                   "option_matched": False, "screen_spent": True,
                   "archetype": archetype})
    index = policy_v0._match_rest_option(options, what)
    # EB-13. `_match_rest_option` matches on `id`/`name` and does not read
    # `is_enabled`, because the wire key did not exist when it was written and
    # `policy_v0.py` is FROZEN -- it is one arm of a published measurement.
    # Screening the match HERE is the same answer without moving a quoted
    # number: an option the screen has greyed out is not an option.
    if index is not None:
        opt = options[index] if index < len(options) else None
        if isinstance(opt, dict) and opt.get("is_enabled") is False:
            index = None
    if index is None:
        # THE SIM ASKED FOR SOMETHING THIS SCREEN DOES NOT SELL, and this arm
        # DECLINES rather than inventing. It used to emit `proceed`, which is
        # how the seed `43MLG7MG9L` run ended: `tier05.model.rest_action`
        # returned `remove` at an act-1 rest site offering only HEAL and SMITH,
        # the fallback posted `proceed`, and the screen answered
        # "No proceed button available or enabled" (`can_proceed: false`) --
        # forever, until the no-progress watchdog stopped the run. A refused
        # verb is not a fallback; it is a loop with a rationale attached.
        #
        # Declining routes it to `soak._last_resort`, which is the module's
        # existing seat for "the policy has no answer and the screen still has
        # to be answered" and which COUNTS every use as a `forced_default`. The
        # old shape spent the same action while reporting itself as a decision.
        declined = _unavailable(
            "rest_site",
            f"tier05.model.rest_action chose '{what}'"
            + (f" ({which})" if which else "")
            + f", which this rest site does not offer as an enabled option "
              f"(offered: {[str((o or {}).get('id')) for o in options if isinstance(o, dict)] or options})")
        # The diagnosis keys survive the decline. What the sim wanted and what
        # the lookahead said are the whole reason this row is readable at all;
        # dropping them because no action came out would throw away the record
        # that made EB-13 diagnosable.
        declined.notes = {"sim_choice": what, "sim_target": which,
                          "next_fight": next_fight, "next_node_kinds": kinds,
                          "option_matched": False}
        return declined
    return Decision(
        category="resource",
        action={"action": "choose_rest_option", "index": index},
        label=f"{what}" + (f" ({which})" if which else ""),
        rationale=("R93 #5: tier05.model.rest_action on a deck of "
                   f"{len(deck_ids)} at {p.get('hp')}/{p.get('max_hp')} HP "
                   f"under the {archetype} plan, "
                   f"next_fight={next_fight} from the map lookahead "
                   f"{kinds or '(none seen)'}"),
        revision="v1.5",
        notes={"sim_choice": what, "sim_target": which,
               "next_fight": next_fight, "next_node_kinds": kinds,
               "option_matched": True, "archetype": archetype})


# ------------------- revision #6: the in-combat choice overlay arm ----------

COMMIT_REVISION = "v1.8-commit"


def _committed_draft(state: dict[str, Any], commit: str) -> Decision:
    """The archetype-committed draft arm (R99/4b). Reached ONLY when a soak
    declared an archetype; `commit=None` never enters this function.

    Two rungs, and the second one is baseline's:

      1. If any offer is a card of the declared archetype (per the design
         sheets, `understudy/committed.py`), take the best-scoring one. This is
         the whole delta: a PRIORITY over the ordering, imposed before the
         skip threshold and before the late-run lean gate, because a
         commitment that could be overruled by a lean gate would produce
         exactly the mixed deck the arm exists to avoid.
      2. Otherwise `assigned_policy` under the DECLARED plan, unchanged --
         including its right to skip. A committed arm that took junk rather
         than skip would be measuring junk.

    DECLARED LIMIT: the SHOP is not committed. `policy_v0._shop` owns
    affordability and shelf-index remapping, and re-deciding a purchase around
    a commitment would put a second variable (and a second index bug) in the
    window. Bot runs die in act 1 and shop rarely; card rewards are where a
    deck comes from. If a committed soak ever ends up deck-diluted by shop
    buys, that count is in the run log and this note is where to start.
    """
    blob = state.get("card_reward") or {}
    offers_raw = (blob.get("cards") if isinstance(blob, dict) else None) \
        or state.get("cards") or state.get("options") or []
    offers: list = []
    approx: list[str] = []
    for e in offers_raw:
        if not isinstance(e, dict):
            continue
        card, is_approx = adapter.resolve_card(e)
        offers.append(card)
        if is_approx:
            approx.append(card.name)
    if not offers:
        return _unavailable("draft", "no offers on the wire to score")

    deck = adapter.deck_cards(state)

    def score(card) -> float:
        return t5draft.score_offer(card, deck, commit)

    scores = {c.name: round(score(c), 2) for c in offers}
    notes = {"approximate_offers": approx, "deck_size": len(deck),
             "commit": commit,
             "committed_offers": [c.name for c in offers
                                  if committed.is_committed(c, commit)]}

    pick = committed.prefer(offers, commit, score)
    revision = COMMIT_REVISION
    if pick is None:
        # Nothing of the declared archetype on this screen. The sim decides,
        # under the declared plan rather than policy_v0's hardcoded one.
        pick = t5draft.assigned_policy(policy_rng("draft"), deck, offers, commit)
        revision = COMMIT_REVISION + "-fallback"

    if pick is None:
        return Decision(
            category="draft", action={"action": "skip_card_reward"},
            label="skip", revision=revision,
            rationale=(f"no {commit} card on offer, and every offer scored "
                       f"below the skip threshold under the {commit} plan"),
            notes=notes)

    index = next((i for i, c in enumerate(offers) if c is pick), None)
    return Decision(
        category="draft",
        action={"action": "select_card_reward", "card_index": index},
        label=f"take {pick.name} [{index}]",
        revision=revision,
        rationale=(f"committed to {commit}: score_offer under the {commit} "
                   f"plan: {scores}"),
        notes=notes)


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
    taken = memo.selected_screens.get(key, set())
    if blob.get("can_confirm") and (blob.get("preview_showing") or taken):
        memo.selected_screens.pop(key, None)
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
                   "selected_indices": sorted(taken),
                   "screen_type": blob.get("screen_type"),
                   "prompt": blob.get("prompt")})
    kind = _screen_kind(blob)
    if kind:
        # policy_v0's arm gates on `screen_type` being literally 'upgrade' or
        # 'remove'. Handing it the kind we read off the prompt is a
        # TRANSLATION, not a policy change: the decision it then makes is
        # still `rest_action`'s smith/thin order, unmodified.
        #
        # REVISION #11 (EB-106). The cards already toggled on this visit are
        # WITHHELD from that arm rather than filtered out of its answer.
        # policy_v0 is a pure function of one wire state and is frozen, so it
        # cannot know a screen has a history; asked the same screen twice it
        # returns the same index twice, `select_card` TOGGLES, and a screen
        # with a quota above one ("Choose 2 cards to Remove.", the Amalgamator
        # event) never reaches `can_confirm`. The offer is the only input that
        # moves, so the delegation stays a delegation: `rest_action` is asked
        # "which of the cards still on the table", and its smith/thin order
        # over that list is unmodified. Indices are mapped back to the
        # SCREEN's own numbering before the action is posted.
        entries = [e for e in (blob.get("cards") or []) if isinstance(e, dict)]
        offered = [i for i in range(len(entries)) if i not in taken]
        translated = dict(state)
        translated["card_select"] = {**blob, "screen_type": kind,
                                     "cards": [entries[i] for i in offered]}
        d = _reindex_to_screen(_from_v0(policy_v0._card_select(translated)),
                               offered)
        d.notes = {**d.notes, "screen_kind_from": "prompt"
                   if str(blob.get("screen_type") or "").lower() != kind
                   else "screen_type"}
        if taken:
            d.notes = {**d.notes, "already_toggled": sorted(taken)}
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
            _committed_screen(state, blob, kind, d.rationale, taken),
            memo, key)
    return _remember_selection(_choice_overlay(state, taken), memo, key)


def _reindex_to_screen(d: Decision, offered: list[int]) -> Decision:
    """Map a `select_card` index over a WITHHELD offer back to the screen's.

    Revision #11's second half. The arm above hands policy_v0 a shortened card
    list, so the index that comes back counts positions in that list; the wire
    counts positions on the screen. The label carries the index too and is
    rewritten with it, because a log line that names a card and an index which
    disagree is worse than one that names neither.
    """
    if not d.available or not d.action:
        return d
    if d.action.get("action") != "select_card":
        return d
    off = int(d.action.get("index", -1))
    if not (0 <= off < len(offered)):
        return _unavailable(
            d.category,
            f"the sim chose offer {off}, which is not one of the "
            f"{len(offered)} options still untoggled on this screen")
    real = offered[off]
    d.action = {**d.action, "index": real}
    if d.label.endswith(f"[{off}]"):
        d.label = d.label[: -len(f"[{off}]")] + f"[{real}]"
    if real != off:
        d.notes = {**d.notes, "offer_index": off, "screen_index": real}
    return d


def _remember_selection(d: Decision, memo: Memo, key: tuple) -> Decision:
    """Record WHICH index a `select_card` was posted for on this screen.

    The grid protocol's second half. A toggle that is not followed by a
    confirm is a bounce; `preview_showing` does not reliably say a
    selection landed; and a multi-select screen needs a DIFFERENT index
    each visit, so the index is what gets remembered rather than the mere
    fact of having selected.
    """
    if d.action and d.action.get("action") == "select_card":
        memo.selected_screens.setdefault(key, set()).add(
            int(d.action.get("index", -1)))
    return d


def _committed_screen(state: dict[str, Any], blob: dict[str, Any], kind: str,
                      why_v0_declined: str,
                      taken: set | None = None) -> Decision:
    taken = taken or set()
    entries = [e for e in (blob.get("cards") or []) if isinstance(e, dict)]
    deck = adapter.deck_cards(state)
    scored: list[tuple[float, int, Any]] = []
    for i, e in enumerate(entries):
        if i in taken:
            continue
        card, approx = adapter.resolve_card(e)
        if approx:
            continue
        try:
            scored.append((t5draft.score_offer(card, deck, _plan(state)), i, card))
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


def _choice_overlay(state: dict[str, Any],
                    taken: set | None = None) -> Decision:
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
    taken = taken or set()
    blob = state.get("card_select") or {}
    screen = str(blob.get("screen_type") or "").lower()
    entries = [e for e in (blob.get("cards") or []) if isinstance(e, dict)]
    if not entries:
        return _unavailable("resource", "no cards on the wire to choose between")
    if taken and len(taken) >= len(entries):
        return _unavailable(
            "resource",
            f"every one of the {len(entries)} options on this screen has "
            f"already been toggled and the wire still will not let it confirm")

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
        # A MULTI-SELECT SCREEN NEEDS A DIFFERENT CARD EACH VISIT. "Choose 2
        # Common Cards to Add to Your Deck" keeps `can_confirm` false until the
        # quota is met, so an arm that re-picks its single best option toggles
        # the same card on and off forever -- which is exactly what the sixth
        # validation soak did until the cycle watchdog stopped it.
        if i in taken:
            continue
        card, approx = adapter.resolve_card(e)
        if not approx:
            resolved.append((i, card))
    for i, card in resolved:
        try:
            scores[card.name] = round(
                t5draft.score_offer(card, deck, _plan(state)), 2)
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
                      f"offered options under the {_plan(state)} plan: "
                      f"{scores}",
            revision="v1.6",
            notes={"basis": "score_offer", "scores": scores,
                   "screen_type": screen, "options": names})
    first = next((i for i in range(len(entries)) if i not in taken), 0)
    return Decision(
        category="resource",
        action={"action": "select_card", "index": first},
        label=f"{names[first]} [{first}] (forced)",
        rationale=("R93 #6 last resort: no option resolves to a sim card row "
                   "and none is a named Spotlight mode, so the first "
                   "untoggled option is taken to keep the run moving. "
                   "FLAGGED, not silent."),
        revision="v1.6",
        notes={"basis": "first_option_fallback", "screen_type": screen,
               "options": names, "forced_default": True})


# ------------------------------------------------------------- dispatch ----

def decide(state: dict[str, Any], memo: Memo | None = None,
           commit: str | None = None) -> Decision:
    """policy_v1's answer at `state`, with revision #7's names attached.

    A crash in any arm returns an unavailable Decision rather than propagating:
    the run is the expensive half, and a policy that can end one by raising is
    a policy that cannot soak.

    `commit` is R99/4b's archetype-committed draft arm, and it is OFF unless a
    soak declares it. **It is the only difference between this function and the
    one R98 validated**: with `commit=None` every branch below is the branch
    that was already there, which `tier0/tests/test_understudy_committed.py`
    pins by replaying recorded states through both settings. Baseline soak
    numbers therefore stay comparable to baseline soak numbers, which is the
    one property a flagged variant has to buy.
    """
    memo = memo if memo is not None else Memo()
    st = str(state.get("state_type") or "unknown")
    # A SCREEN'S SELECTION STATE IS PER-VISIT, NOT PER-FLOOR. Furina's starter
    # relic reopens the same "Choose a card." Spotlight screen every single
    # turn, with the same key -- so toggles remembered from last turn made the
    # arm believe every option was already taken and it declined a screen that
    # cannot be cancelled. Leaving `card_select` is what ends a visit.
    if st != "card_select" and memo.selected_screens:
        memo.selected_screens.clear()
    if st in policy_v0.NO_COUNTERFACTUAL:
        d = _unavailable(st, policy_v0.NO_COUNTERFACTUAL[st])
    else:
        try:
            if st in ("monster", "elite", "boss"):
                d = _combat(state, memo)
            elif st == "card_reward":
                d = (_committed_draft(state, commit) if commit
                     else _card_reward(state, memo))
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


def _card_reward(state: dict[str, Any], memo: Memo) -> Decision:
    """REVISION #8. policy_v0's draft arm, scored under the RUN's plan.

    Every line of the valuation is still the sim's: `t5draft.assigned_policy`
    picks and `t5draft.score_offer` prices, exactly as `policy_v0._card_reward`
    calls them, with `understudy.rng.policy_rng("draft")` as the stream. The
    single difference is the archetype argument, which was the module constant
    `"salon"` and is now the plan of the character actually being played.

    Why this is not just a call into policy_v0 with an extra argument: v0 is
    the counterfactual arm of a measurement already taken (R98) and does not
    get edited, not even to add a keyword with a default. So the arm is
    mirrored here, and the mirror is deliberately literal -- if v0's draft
    logic ever moves, this is a place that has to move with it.
    """
    archetype = _plan(state, memo)
    blob = state.get("card_reward") or {}
    offers_raw = (blob.get("cards") if isinstance(blob, dict) else None) \
        or state.get("cards") or state.get("options") or []
    offers: list = []
    approx: list[str] = []
    for e in offers_raw:
        if not isinstance(e, dict):
            continue
        card, is_approx = adapter.resolve_card(e)
        offers.append(card)
        if is_approx:
            approx.append(card.name)
    if not offers:
        return _unavailable("draft", "no offers on the wire to score")

    deck = adapter.deck_cards(state)
    pick = t5draft.assigned_policy(policy_rng("draft"), deck, offers, archetype)
    from understudy import deckwatch
    notes = {"approximate_offers": approx, "deck_size": len(deck),
             "deck_from": deckwatch.provenance(), "archetype": archetype,
             "character": memo.character}

    if pick is None:
        return Decision(
            category="draft", action={"action": "skip_card_reward"},
            label="skip",
            rationale=("every offer scored below the skip threshold, or the "
                       f"late-run lean gate refused all of them, under the "
                       f"{archetype} plan"),
            revision="v1.8-plan", notes=notes)

    index = next((i for i, c in enumerate(offers) if c is pick), None)
    scores = {c.name: round(t5draft.score_offer(c, deck, archetype), 2)
              for c in offers}
    return Decision(
        category="draft",
        action={"action": "select_card_reward", "card_index": index},
        label=f"take {pick.name} [{index}]",
        rationale=f"score_offer under the {archetype} plan: {scores}",
        revision="v1.8-plan", notes=notes)


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
