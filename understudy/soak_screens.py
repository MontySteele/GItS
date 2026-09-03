"""What one screen is: a hazard, a forced action, an escape, a last resort.

Cut out of `soak.py` by `EB-180`. Every function here is that file's, moved
whole and re-exported from it, so `soak._mechanical_action(state)` and
`soak._trim_state(state)` still resolve.

Pure reads of a state dict -- no wire, no game directory, no dial a test
swaps -- so this seam reads its registers straight off `soak_shape`.
"""
from __future__ import annotations

import json

from understudy.soak_shape import (DECISION_SCREENS, HAZARD_EVENT_TITLES,
                                   HAZARD_EVENTS)

def _hazard_event(state: dict) -> tuple[str, str] | None:
    """`(identity, why)` when this screen is a registered hazard, else `None`.

    Matched on the wire ID first because an id is the thing itself, and on the
    display title second because a title is loc data that a wording pass moves
    -- the same read-by-id-not-by-name rule `_meters` states, with the fallback
    kept rather than dropped: a screen this harness must not drive is worth
    catching twice.
    """
    if str(state.get("state_type")) != "event":
        return None
    ev = state.get("event") or {}
    if not isinstance(ev, dict):
        return None
    ident = str(ev.get("event_id") or "").strip().upper()
    if ident in HAZARD_EVENTS:
        return ident, HAZARD_EVENTS[ident]
    title = " ".join(str(ev.get("event_name") or "").split()).lower()
    by_title = HAZARD_EVENT_TITLES.get(title)
    if by_title is not None:
        return by_title, HAZARD_EVENTS.get(
            by_title, "on the hazard register by display title")
    return None


def _option_names(state: dict) -> list[str]:
    out = []
    for o in state.get("options") or []:
        if isinstance(o, str):
            out.append(o)
        elif isinstance(o, dict) and o.get("name"):
            if o.get("enabled") is False:
                continue
            out.append(str(o["name"]))
    return out


def _first_of(options: list[str], preferred: tuple[str, ...]) -> str | None:
    low = {o.lower(): o for o in options}
    for p in preferred:
        if p in low:
            return low[p]
    return None


def _game_over_won(state: dict) -> bool:
    blob = state.get("game_over") or {}
    if isinstance(blob, dict):
        for k in ("victory", "won", "is_victory"):
            if k in blob:
                return bool(blob[k])
    return "victor" in json.dumps(blob).lower()


def _mechanical_action(state: dict) -> dict | None:
    """The one forced action on a screen where the game asks nothing.

    Same set the Phase-0 harness's `auto` verb walked, plus the event screens
    policy_v1 still declines (R93 did not add an event arm -- `tier05.events`
    scores by sim event id and the wire carries prose, so an invented answer
    would be noise wearing a policy's clothes).
    """
    st = str(state.get("state_type"))
    if st == "event":
        ev = state.get("event") or {}
        if ev.get("in_dialogue"):
            return {"action": "advance_dialogue"}
        opts = [o for o in (ev.get("options") or []) if not o.get("is_locked")]
        if opts:
            # Deterministic and declared: the FIRST unlocked option, always.
            # Not a policy -- a coin that always lands the same way, so an
            # event's contribution to a soak is at least constant across runs.
            return {"action": "choose_event_option",
                    "index": opts[0].get("index", 0)}
        return {"action": "advance_dialogue"}
    if st == "rewards":
        blob = state.get("rewards")
        items = blob.get("items") if isinstance(blob, dict) else (blob or [])
        return ({"action": "claim_reward", "index": 0} if items
                else {"action": "proceed"})
    if st == "treasure":
        relics = state.get("relics") or state.get("options") or []
        return ({"action": "claim_treasure_relic", "index": 0} if relics
                else {"action": "proceed"})
    if st == "relic_select":
        relics = state.get("relics") or state.get("options") or []
        return ({"action": "select_relic", "index": 0} if relics
                else {"action": "skip_relic_selection"})
    if st == "bundle_select":
        # SELECTING A BUNDLE OPENS A PREVIEW; IT DOES NOT TAKE THE BUNDLE, and
        # the second `select_bundle` is refused in as many words ("A bundle
        # preview is already open - confirm or cancel it first"). Without the
        # confirm the walker re-picks index 0 forever, which is how Neow's
        # Scroll Boxes ended a run at sixteen actions. Same shape as the
        # Enchant screen (defect 6) and the removal grid (defect 4): a screen
        # whose select is a preview, not a choice.
        blob = state.get("bundle_select") or {}
        if blob.get("preview_showing"):
            return {"action": "confirm_bundle_selection"}
        return {"action": "select_bundle", "index": 0}
    if st == "hand_select":
        blob = state.get("hand_select") or {}
        if blob.get("can_confirm"):
            return {"action": "combat_confirm_selection"}
        cards = blob.get("cards") or (state.get("player") or {}).get("hand") or []
        return ({"action": "combat_select_card", "card_index": 0} if cards
                else {"action": "combat_confirm_selection"})
    if st == "crystal_sphere":
        return {"action": "crystal_sphere_proceed"}
    if st in DECISION_SCREENS:
        return None
    if st == "menu":
        opts = _option_names(state)
        pick = _first_of(opts, ("ignore", "ok", "confirm", "back"))
        return {"action": "menu_select", "option": pick} if pick else None
    return None


def _escape(state: dict) -> dict | None:
    """The verb that leaves a screen a forced action could not finish.

    Every one of these screens advertises a way out; the walker just never had
    a reason to use it until a full potion belt made `claim_reward` a no-op.
    """
    return {
        "rewards": {"action": "proceed"},
        "treasure": {"action": "proceed"},
        "relic_select": {"action": "skip_relic_selection"},
        "hand_select": {"action": "combat_confirm_selection"},
        "crystal_sphere": {"action": "crystal_sphere_proceed"},
    }.get(str(state.get("state_type")))


def _last_resort(state: dict) -> dict | None:
    """When policy_v1 declines and the screen is a real one, keep moving.

    Every use is counted and logged as `forced_default`, because a run that
    proceeds by shrugging is a run whose telemetry is worth less and the report
    has to be able to say so.
    """
    st = str(state.get("state_type"))
    if st == "card_select":
        # A SCREEN THAT CANNOT BE CANCELLED MUST BE ANSWERED. The in-combat
        # "Choose a card." overlay reports `can_cancel: false` and
        # `can_skip: false`, and the bridge rejects the cancel with "No skip
        # option available - a card must be chosen" -- so cancelling as a last
        # resort is a guaranteed loop, which is exactly what it produced.
        blob = state.get("card_select") or {}
        if blob.get("can_cancel") or blob.get("can_skip"):
            return {"action": "cancel_selection"}
        if blob.get("can_confirm"):
            return {"action": "confirm_selection"}
        return {"action": "select_card", "index": 0}
    if st == "rest_site":
        # EB-13, AND THE SAME LESSON AS `card_select` ABOVE: a screen that
        # refuses the exit must be answered, not exited. A rest site reports
        # `can_proceed: false` until its one option has been spent, and the
        # bridge says so in as many words ("No proceed button available or
        # enabled"). `proceed` used to be the unconditional answer here, so a
        # rest site whose options the policy could not match spent every
        # remaining action of the run posting a verb the screen had already
        # refused -- the `no_progress` defect filed against seed `43MLG7MG9L`.
        #
        # The answer is the screen's own: take the first ENABLED option, in
        # offered order. Deterministic and declared -- not a policy, the same
        # always-heads coin `_mechanical_action` spends on events, and counted
        # as a `forced_default` so the telemetry says the choice was not the
        # sim's.
        blob = state.get("rest_site") or {}
        options = ((blob.get("options") if isinstance(blob, dict) else None)
                   or state.get("options") or [])
        for i, opt in enumerate(options):
            if not isinstance(opt, dict) or opt.get("is_enabled") is not False:
                return {"action": "choose_rest_option", "index": i}
        return {"action": "proceed"}
    return {
        "card_reward": {"action": "skip_card_reward"},
        "shop": {"action": "proceed"},
        "fake_merchant": {"action": "proceed"},
        "monster": {"action": "end_turn"},
        "elite": {"action": "end_turn"},
        "boss": {"action": "end_turn"},
    }.get(st)


def _trim_state(state: dict) -> dict:
    """A state dump small enough to sit in a defect record and complete enough
    to diagnose from. The piles go; everything a screen turns on stays."""
    out = {k: v for k, v in state.items()
           if k not in ("player", "map", "compendium")}
    p = dict(state.get("player") or {})
    for pile in ("draw_pile", "discard_pile", "exhaust_pile", "deck"):
        if pile in p:
            p[pile] = f"<{len(p[pile])} cards>"
    out["player"] = p
    m = state.get("map") or {}
    if m:
        out["map"] = {k: m.get(k) for k in ("next_options", "boss")}
    return out
