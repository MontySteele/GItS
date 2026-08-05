"""policy_v0 -- the tier-0.5 pilot, speaking the bridge protocol.

Understudy W3. This is the counterfactual arm of the Phase-0 measurement: at
every state the LLM decides, this module is asked what the sim's own policy
would have done, and the two answers go into the same log line.

Design commitment, stated once and honoured throughout: **policy_v0 contains
no heuristics of its own.** Every decision is delegated to the live tier0 /
tier05 entry points -- `tier0.pilot.policy.make_pilot`, `tier05.draft`,
`tier05.route`, `tier05.model.rest_action`, `tier05.shop`. If a decision class
cannot be delegated faithfully, it returns NO counterfactual rather than an
invented one, and says why. There are three of those and they are listed in
`NO_COUNTERFACTUAL` below.

That commitment is what makes M2 falsifiable. An agreement rate against a
re-typed policy measures the retyping; an agreement rate against the sim's own
policy measures the judgment gap the sprint exists to size.

Determinism: every entry point is asked to sort, never to roll. The RNG
handed in comes from `understudy.rng.policy_rng`, is stream-isolated from the
game seed by construction, and is expected to go unconsumed -- tier05's
policies deliberately consume no rng (`shop.py:27-28`). If a future revision
makes one of them roll, the stream is already there and already separate.

DECISION CLASSES AND THEIR CATEGORY LABEL (the divergence report's buckets):

  combat card play      -> "sequencing"   (which card, and whether to stop)
  combat targeting      -> "targeting"    (which enemy)
  card_reward           -> "draft"
  map                   -> "path"
  rest_site / shop /    -> "resource"     (when to spend HP, gold, a potion)
  potion use
  event / relic pick /  -> no counterfactual, excluded from the M2 denominator
  overlay selections
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from tier0.content import loader
from tier0.pilot import policy as pilot_policy
from tier05 import draft as t5draft
from tier05 import model as t5model
from tier05 import route as t5route

from understudy import adapter
from understudy.rng import policy_rng

# Furina's assigned plan, from the sim's single source of truth for
# plan->pilot (`tier05.runner.resolve_plan`, R68). Not a choice made here.
CHARACTER = "furina"
ARCHETYPE = "salon"
PILOT_ID = "salon"

NO_COUNTERFACTUAL = {
    "event": (
        "tier05.events.choose scores OPTIONS BY SIM EVENT ID against a curated "
        "table. The wire gives option prose from the live game, and matching "
        "prose to sim event ids is a guess wearing a policy's clothes. An "
        "invented answer here would inflate or deflate the agreement rate with "
        "noise that looks like judgment."),
    "relic_select": (
        "tier05.relics._neow_value is keyed on sim relic ids. Base-game boss "
        "relics have no sim row, so there is nothing to score."),
    "crystal_sphere": (
        "A minigame with no sim analogue at all."),
}

MECHANICAL = {
    "rewards", "card_select", "bundle_select", "hand_select",
    "treasure", "game_over", "menu", "unknown", "overlay",
}


@dataclass
class Counterfactual:
    """What policy_v0 would do, and how much of that is trustworthy."""
    category: str
    action: dict[str, Any] | None
    label: str
    rationale: str
    available: bool = True
    notes: dict[str, Any] = field(default_factory=dict)

    def as_log(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "available": self.available,
            "action": self.action,
            "label": self.label,
            "rationale": self.rationale,
            "notes": self.notes,
        }


def _unavailable(category: str, why: str) -> Counterfactual:
    return Counterfactual(category=category, action=None, label="(none)",
                          rationale=why, available=False)


# --------------------------------------------------------------- combat ----

def _combat(state: dict[str, Any]) -> Counterfactual:
    cs, notes = adapter.build_combat_state(state)
    pilot = pilot_policy.make_pilot(loader.pilot_weights(PILOT_ID))
    choice = pilot(cs)

    if choice is None:
        return Counterfactual(
            category="sequencing",
            action={"action": "end_turn"},
            label="end_turn",
            rationale=("no playable card scored above zero, which is the "
                       "pilot's end-of-turn condition"),
            notes=notes)

    # Identity, not equality: a hand can hold two copies of one card and the
    # pilot's tiebreak is explicitly earliest-hand-position, so matching by id
    # would silently re-target the second copy.
    index = next((i for i, c in enumerate(cs.player.hand) if c is choice), None)
    if index is None:
        return _unavailable(
            "sequencing",
            "the pilot returned a card that is not in the reconstructed hand; "
            "adapter bug, not a policy result")

    action: dict[str, Any] = {"action": "play_card", "card_index": index}
    # Only aim what needs aiming. The wire marks each hand card's target type;
    # sending a target with a Self card is an error the bridge rejects, and a
    # counterfactual that cannot be executed is not a counterfactual.
    hand_entry = (state.get("player") or {}).get("hand") or []
    # The field is `target_type`, not `target` -- reading the wrong key made
    # every card look self-targeting and every attack post without an aim.
    wire_target = (str(hand_entry[index].get("target_type", "")).lower()
                   if index < len(hand_entry) else "")
    target = (_pilot_target(state, cs)
              if wire_target not in ("", "self", "none") else None)
    if target:
        action["target"] = target
    return Counterfactual(
        category="sequencing",
        action=action,
        label=f"play {choice.name} [{index}]" + (f" -> {target}" if target else ""),
        rationale=_why_card(cs, choice),
        notes=notes)


def _pilot_target(state: dict[str, Any], cs) -> str | None:
    """tier0 aims at the lowest-HP living enemy (`effects._default_target`).

    Targeting is not IN the pilot in tier0 -- it is the engine's default -- so
    this is the engine's rule restated at the only place the wire can express
    it. The divergence report's "targeting" bucket is measured against this.
    """
    enemies = [e for e in adapter.enemy_blobs(state) if int(e.get("hp", 0)) > 0]
    if not enemies:
        return None
    if len(enemies) == 1:
        return adapter.enemy_id(enemies[0])
    lowest = min(enemies, key=lambda e: (int(e.get("hp", 0)), adapter.enemy_id(e)))
    return adapter.enemy_id(lowest)


def _why_card(cs, card) -> str:
    incoming = pilot_policy._incoming_damage(cs)
    dmg = pilot_policy._expected_damage(cs, card)
    blk = pilot_policy._block_value(cs, card, incoming)
    return (f"score picked it; expected damage {dmg:.1f}, block worth "
            f"{blk:.1f} against {incoming} incoming, cost {card.cost}")


# ---------------------------------------------------------------- draft ----

def _card_reward(state: dict[str, Any]) -> Counterfactual:
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
    pick = t5draft.assigned_policy(policy_rng("draft"), deck, offers, ARCHETYPE)
    from understudy import deckwatch
    notes = {"approximate_offers": approx, "deck_size": len(deck),
             "deck_from": deckwatch.provenance()}

    if pick is None:
        return Counterfactual(
            category="draft", action={"action": "skip_card_reward"},
            label="skip",
            rationale=("every offer scored below the skip threshold, or the "
                       "late-run lean gate refused all of them"),
            notes=notes)

    index = next((i for i, c in enumerate(offers) if c is pick), None)
    scores = {c.name: round(t5draft.score_offer(c, deck, ARCHETYPE), 2)
              for c in offers}
    return Counterfactual(
        category="draft",
        action={"action": "select_card_reward", "card_index": index},
        label=f"take {pick.name} [{index}]",
        rationale=f"score_offer under the {ARCHETYPE} plan: {scores}",
        notes=notes)


# ----------------------------------------------------------------- path ----

def _map(state: dict[str, Any]) -> Counterfactual:
    """The route want-table, applied to the offered nodes only.

    REDUCTION, declared: `tier05.route` plans by backward induction over the
    WHOLE act map and picks the first step of the best path. The wire exposes
    the next options and the boss, not the full successor DAG, so the lookahead
    cannot be reconstructed. What survives is `_make_value` -- the same want
    table, the same elite bar, the same rest-is-worth-what-it-heals rule --
    evaluated one step deep.

    This makes the path counterfactual systematically MORE myopic than the sim,
    and the divergence report must read a "path" disagreement with that in
    mind: it is a difference of horizon at least as much as of taste.
    """
    options = state.get("map", {}).get("next_options") or state.get("next_options") or []
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

    # The sim's own valuation function, called -- not restated. The reduction
    # is only in the SEARCH (one step instead of the whole DAG), so the per-
    # room value a disagreement is read against is still tier05's.
    value = t5route._make_value(want, st, elite_ok)
    scored = [(value(t5route.Room(i, st.floor, _room_kind(opt))), -i, i,
               _room_kind(opt))
              for i, opt in enumerate(options)]
    best = max(scored, key=lambda t: t[:2])

    return Counterfactual(
        category="path",
        action={"action": "choose_map_node", "index": best[2]},
        label=f"node {best[2]} ({best[3]})",
        rationale=("hunter want-table, one step deep (see the REDUCTION note): "
                   + ", ".join(f"{k}={v:.1f}" for v, _, _, k in scored)
                   + f"; elite bar {bar:.2f} vs hp_frac {st.hp_frac:.2f}"),
        notes={"reduced_from": "whole-map backward induction",
               "elite_ok": elite_ok,
               # A one-option map screen is a corridor, not a choice. Recorded
               # so the agreement rate can exclude forced moves instead of
               # being inflated by them.
               "n_options": len(options)})


_KIND_WORDS = {
    "elite": t5route.ELITE, "monster": t5route.NORMAL, "normal": t5route.NORMAL,
    "enemy": t5route.NORMAL, "combat": t5route.NORMAL,
    "shop": t5route.SHOP, "merchant": t5route.SHOP,
    "treasure": t5route.TREASURE, "chest": t5route.TREASURE,
    "rest": t5route.REST, "campfire": t5route.REST, "rest_site": t5route.REST,
    "event": t5route.UNKNOWN, "unknown": t5route.UNKNOWN, "question": t5route.UNKNOWN,
    "boss": t5route.ELITE,
}


def _room_kind(opt: Any) -> str:
    raw = opt if isinstance(opt, str) else str(
        (opt or {}).get("kind") or (opt or {}).get("type")
        or (opt or {}).get("room_type") or (opt or {}).get("name") or "")
    raw = raw.strip().lower()
    for word, kind in _KIND_WORDS.items():
        if word in raw:
            return kind
    return t5route.UNKNOWN


# ------------------------------------------------------------- resource ----

def _resolves_to_a_sim_row(card_id: str) -> bool:
    try:
        loader.peek_card(card_id)
        return True
    except (KeyError, ValueError):
        return False


def _rest(state: dict[str, Any]) -> Counterfactual:
    p = state.get("player") or {}
    # Same guard as the card_select screen: base-game cards and engine tokens
    # have no sheet row, and rest_action looks every id up. One base-game curse
    # in the deck ('DEBT') was enough to crash the counterfactual arm.
    deck_ids = [c.id for c in adapter.deck_cards(state)
                if _resolves_to_a_sim_row(c.id)]
    what, which = t5model.rest_action(
        deck_ids, int(p.get("hp", 0)), int(p.get("max_hp", 1)),
        archetype=ARCHETYPE, next_fight=False)
    blob = state.get("rest_site") or {}
    options = (blob.get("options") if isinstance(blob, dict) else None)         or state.get("options") or []
    index = _match_rest_option(options, what)
    return Counterfactual(
        category="resource",
        action=({"action": "choose_rest_option", "index": index}
                if index is not None else None),
        label=f"{what}" + (f" ({which})" if which else ""),
        rationale=("tier05.model.rest_action ladder on a deck of "
                   f"{len(deck_ids)} at {p.get('hp')}/{p.get('max_hp')} HP; "
                   "next_fight is passed False because the wire does not show "
                   "the node after this one; cards with no sim row are "
                   "excluded from the deck it scores"),
        available=index is not None,
        notes={"sim_choice": what, "sim_target": which})


_REST_WORDS = {"heal": ("rest", "sleep", "heal"), "upgrade": ("smith", "upgrade"),
               "remove": ("remove", "toke", "purge")}


def _match_rest_option(options: Any, what: str) -> int | None:
    words = _REST_WORDS.get(what, ())
    for i, opt in enumerate(options or []):
        name = (opt if isinstance(opt, str)
                else " ".join(str((opt or {}).get(k, "")) for k in ("id", "name"))).lower()
        if any(w in name for w in words):
            return i
    return None


def _shop(state: dict[str, Any]) -> Counterfactual:
    """One purchase decision, the way tier05.shop's buy loop asks for one.

    `visit_shop` runs a loop; a single wire state is a single iteration of it,
    so the counterfactual is that iteration: hand the shelf to the draft
    policy, buy if affordable, otherwise leave.
    """
    items = state.get("items") or state.get("shop", {}).get("items") or []
    p = state.get("player") or {}
    gold = int(p.get("gold", 0))
    deck = adapter.deck_cards(state)

    shelf, index_of = [], {}
    for i, it in enumerate(items):
        if not isinstance(it, dict):
            continue
        if str(it.get("type", "")).lower() not in ("card", ""):
            continue
        card, _ = adapter.resolve_card(it)
        index_of[id(card)] = i
        shelf.append((card, int(it.get("price", it.get("cost", 10**6)) or 10**6)))

    if not shelf:
        return Counterfactual(
            category="resource", action={"action": "proceed"}, label="leave shop",
            rationale="no card stock on the wire to hand to the draft policy")

    pick = t5draft.assigned_policy(policy_rng("shop"), deck,
                                   [c for c, _ in shelf], ARCHETYPE)
    if pick is None:
        return Counterfactual(
            category="resource", action={"action": "proceed"}, label="leave shop",
            rationale="the draft policy skipped every card on the shelf")
    price = next(pr for c, pr in shelf if c is pick)
    if price > gold:
        return Counterfactual(
            category="resource", action={"action": "proceed"}, label="leave shop",
            rationale=f"the policy wants {pick.name} at {price}g on {gold}g")
    return Counterfactual(
        category="resource",
        action={"action": "shop_purchase", "index": index_of[id(pick)]},
        label=f"buy {pick.name} ({price}g)",
        rationale=f"draft policy's pick off the shelf, affordable on {gold}g")


def _card_select(state: dict[str, Any]) -> Counterfactual:
    """Upgrade / remove overlays, answered by the sim's rest-site smith rule.

    `rest_action` is the only place tier05 expresses "which card do I upgrade"
    and "which card do I remove", so it is the entry point even though no rest
    site is involved. HP is passed at full deliberately: the ladder's first two
    rungs are heal decisions about a rest, and this screen is not one. What
    survives is exactly the smith/thin preference order.
    """
    blob = state.get("card_select") or {}
    screen = str(blob.get("screen_type") or "").lower()
    entries = [e for e in (blob.get("cards") or []) if isinstance(e, dict)]
    if not entries:
        return _unavailable("resource", "no cards on the wire to choose between")

    # Only the deck-management screens map onto a sim decision. A "choose"
    # overlay (Ethereal Spotlight's Center Stage / Guest Cast) is an in-combat
    # branch the sim expresses inside the CARD, not as a policy call.
    if screen not in ("upgrade", "remove"):
        return _unavailable(
            "resource",
            f"'{screen or 'unlabelled'}' overlay: tier05 has no policy for it; "
            f"only upgrade and remove screens map onto rest_action's ladder")

    ids, approx = [], []
    for e in entries:
        card, is_approx = adapter.resolve_card(e)
        # A card that only LOOKS like a sheet id (the KLEEMOD- token cards the
        # engine creates, e.g. KLEEMOD-CENTER_STAGE_OPTION) resolves as
        # approximate. Passing it on would make rest_action raise on a lookup,
        # which is a crash in the counterfactual arm rather than a finding.
        ids.append(None if is_approx else card.id)
        if is_approx:
            approx.append(card.name)

    sheet_ids = [i for i in ids if i]
    if not sheet_ids:
        return _unavailable(
            "resource", "no option resolves to a sim card row")

    p = state.get("player") or {}
    max_hp = int(p.get("max_hp", 1))
    what, target = t5model.rest_action(sheet_ids, max_hp, max_hp,
                                       archetype=ARCHETYPE, next_fight=False)
    if what != screen:
        return _unavailable(
            "resource",
            f"the sim's ladder wants to '{what}' but this screen is a "
            f"'{screen}' screen; delegating across them would be a guess")
    index = next((i for i, cid in enumerate(ids) if cid == target), None)
    if index is None:
        return _unavailable(
            "resource", f"the sim chose {target!r}, which is not on this screen")
    return Counterfactual(
        category="resource",
        action={"action": "select_card", "index": index},
        label=f"{what} {target} [{index}]",
        rationale=("tier05.model.rest_action's smith order (on-plan payoff "
                   "before enabler) over the offered cards, HP passed at full "
                   "so the heal rungs cannot fire"),
        notes={"approximate": approx, "screen_type": screen})


# -------------------------------------------------------------- dispatch ----

def counterfactual(state: dict[str, Any]) -> Counterfactual:
    st = str(state.get("state_type") or "unknown")
    if st in NO_COUNTERFACTUAL:
        return _unavailable(st, NO_COUNTERFACTUAL[st])
    try:
        if st in ("monster", "elite", "boss"):
            return _combat(state)
        if st == "card_reward":
            return _card_reward(state)
        if st == "map":
            return _map(state)
        if st == "rest_site":
            return _rest(state)
        if st in ("shop", "fake_merchant"):
            return _shop(state)
        if st == "card_select":
            return _card_select(state)
    except Exception as e:                      # noqa: BLE001
        # A crash in the counterfactual arm must never end the run: the run is
        # the expensive half. Record it as a finding and carry on.
        return _unavailable(st, f"policy_v0 raised {type(e).__name__}: {e}")
    return _unavailable(
        st, f"'{st}' is a mechanical screen with no sim decision behind it")
