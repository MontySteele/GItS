"""Resolved NAMES for a posted action -- policy_v1 revision #7, the P1 blocker.

WHY THIS MODULE IS THE BLOCKER AND NOT A NICETY

The Phase-0 log stored `card_index` and nothing else about what a play WAS.
`{"action": "play_card", "card_index": 2}` is a complete instruction to the
game and a useless row in a dataset: index 2 is a different card on every turn
of every run. That is why the Phase-0 divergence report was categorised BY
HAND, by a human reading the prose `why` field over 191 lines. A thousand-run
soak cannot be read that way, and [USER]'s ruling (R93) elevated this revision
above the other six for exactly that reason: **a log that cannot be analysed
automatically produces heat, not data.**

So every action this apparatus posts is accompanied by the identity of the
things it names, resolved at the state the action was decided against. The
resolution has to happen BEFORE the POST -- one frame later the hand has
changed and index 2 means something else.

WHAT IS RESOLVED, AND WHAT IS DELIBERATELY NOT

Resolved: the card (id, name, cost, type, upgraded), the enemy aimed at (id
and name), the menu/map/rest/event option (index, and its own label), the
potion in a slot. All from the wire's own fields -- nothing is inferred and
nothing is looked up in a sheet, because a name that disagrees with what the
GAME called it would make the log lie in the most expensive possible way.

Not resolved: anything requiring a second HTTP round trip. This runs on the
hot path of every decision in every soak run; it reads the state dict it was
handed and returns.

STABILITY CONTRACT: the key set below is a log schema. Analysis code keys on
it. Adding keys is free; renaming or repurposing one is a schema change and
belongs in `understudy/README.md`'s telemetry section with a note.
"""

from __future__ import annotations

from typing import Any

from understudy import adapter

# The wire's own field for "is this card upgraded". Recorded because two
# different spellings exist across screens (`is_upgraded` on card info,
# `upgraded` on some older paths) and a log that silently drops the flag on
# one screen makes upgraded and base copies indistinguishable in analysis.
_UPGRADE_KEYS = ("is_upgraded", "upgraded")


def _card_identity(entry: Any, prefix: str = "card") -> dict[str, Any]:
    if not isinstance(entry, dict):
        return {}
    out: dict[str, Any] = {
        f"{prefix}_id": entry.get("id"),
        f"{prefix}_name": entry.get("name"),
    }
    if entry.get("cost") is not None:
        out[f"{prefix}_cost"] = entry.get("cost")
    if entry.get("type") is not None:
        out[f"{prefix}_type"] = str(entry.get("type")).lower()
    if entry.get("rarity") is not None:
        out[f"{prefix}_rarity"] = str(entry.get("rarity")).lower()
    for k in _UPGRADE_KEYS:
        if k in entry:
            out[f"{prefix}_upgraded"] = bool(entry.get(k))
            break
    return {k: v for k, v in out.items() if v is not None}


def _at(seq: Any, index: Any) -> Any:
    if not isinstance(seq, list) or not isinstance(index, int):
        return None
    if 0 <= index < len(seq):
        return seq[index]
    return None


def _hand(state: dict[str, Any]) -> list:
    return list((state.get("player") or {}).get("hand") or [])


def _offers(state: dict[str, Any]) -> list:
    blob = state.get("card_reward") or {}
    if isinstance(blob, dict) and isinstance(blob.get("cards"), list):
        return blob["cards"]
    return list(state.get("cards") or [])


def _screen_cards(state: dict[str, Any], key: str) -> list:
    blob = state.get(key) or {}
    if isinstance(blob, dict) and isinstance(blob.get("cards"), list):
        return blob["cards"]
    return []


def _relics(state: dict[str, Any], key: str) -> list:
    """`state[key]["relics"]`, which is where the wire keeps a chest's."""
    blob = state.get(key) or {}
    if isinstance(blob, dict) and isinstance(blob.get("relics"), list):
        return blob["relics"]
    return []


def _options(state: dict[str, Any], key: str) -> list:
    blob = state.get(key) or {}
    if isinstance(blob, dict) and isinstance(blob.get("options"), list):
        return blob["options"]
    return list(state.get("options") or []) if isinstance(state.get("options"), list) else []


def _label(opt: Any) -> str | None:
    if isinstance(opt, str):
        return opt
    if not isinstance(opt, dict):
        return None
    # `EB-262` / `EB-263`: a shop item and an event option that hands over a
    # relic carry their printed name under a CATEGORY-PREFIXED key
    # (`card_name` / `relic_name` / `potion_name`,
    # `McpMod.StateBuilder.cs:1636`), and a chest's relic rows are plain
    # `name`. The plain spellings stay first so no existing row changes.
    for k in ("name", "title", "label", "card_name", "relic_name",
              "potion_name", "type", "kind", "room_type", "category"):
        v = opt.get(k)
        if v:
            return str(v)
    return None


def describe(state: dict[str, Any], action: dict[str, Any]) -> dict[str, Any]:
    """The names behind `action`, resolved at `state`. Never raises.

    Returned dict is flat and JSON-safe by construction: it only ever contains
    values copied straight out of the wire payload.
    """
    try:
        return _describe(state, action)
    except Exception as e:                                   # noqa: BLE001
        # A naming failure must never cost a run. It costs one row's
        # analysability, and it says so out loud so the row is filterable.
        return {"name_resolution_error": f"{type(e).__name__}: {e}"}


def _describe(state: dict[str, Any], action: dict[str, Any]) -> dict[str, Any]:
    verb = str(action.get("action") or "")
    out: dict[str, Any] = {"verb": verb}
    st = str(state.get("state_type") or "")

    if verb == "play_card":
        out.update(_card_identity(_at(_hand(state), action.get("card_index"))))
        tid = action.get("target")
        if tid:
            out["target_id"] = tid
            for e in adapter.enemy_blobs(state):
                if adapter.enemy_id(e) == tid:
                    out["target_name"] = e.get("name")
                    out["target_hp"] = e.get("hp")
                    break

    elif verb in ("use_potion", "discard_potion"):
        slot = action.get("slot")
        out["potion_slot"] = slot
        entry = _at((state.get("player") or {}).get("potions") or [], slot)
        if isinstance(entry, dict):
            out["potion_id"] = entry.get("id")
            out["potion_name"] = entry.get("name")
        if action.get("target"):
            out["target_id"] = action["target"]

    elif verb == "select_card_reward":
        out.update(_card_identity(_at(_offers(state), action.get("card_index"))))

    elif verb == "skip_card_reward":
        out["offered_names"] = [c.get("name") for c in _offers(state)
                                if isinstance(c, dict)]

    elif verb in ("select_card", "combat_select_card"):
        key = "card_select" if verb == "select_card" else "hand_select"
        cards = _screen_cards(state, key) or _hand(state)
        out.update(_card_identity(_at(cards, action.get("index",
                                                        action.get("card_index")))))
        blob = state.get(key) or {}
        if isinstance(blob, dict) and blob.get("screen_type"):
            out["screen_type"] = str(blob["screen_type"]).lower()

    elif verb == "choose_map_node":
        idx = action.get("index")
        opt = _at((state.get("map") or {}).get("next_options")
                  or state.get("next_options") or [], idx)
        out["option_index"] = idx
        out["node_kind"] = _label(opt)
        if isinstance(opt, dict):
            out["node_col"] = opt.get("col")
            out["node_row"] = opt.get("row")
            leads = opt.get("leads_to")
            if isinstance(leads, list):
                out["leads_to_kinds"] = [_label(c) for c in leads]

    elif verb == "choose_event_option":
        idx = action.get("index")
        out["option_index"] = idx
        ev = state.get("event") or {}
        out["event_name"] = ev.get("event_name")
        out["event_id"] = ev.get("event_id")
        for o in ev.get("options") or []:
            if isinstance(o, dict) and o.get("index") == idx:
                out["option_name"] = o.get("title")
                break

    elif verb == "choose_rest_option":
        idx = action.get("index")
        out["option_index"] = idx
        for o in _options(state, "rest_site"):
            if isinstance(o, dict) and o.get("index") == idx:
                out["option_name"] = o.get("name")
                break

    elif verb == "shop_purchase":
        idx = action.get("index")
        items = state.get("items") or (state.get("shop") or {}).get("items") or []
        item = _at(items, idx)
        out["option_index"] = idx
        if isinstance(item, dict):
            # `EB-262`: the shelf's name is under its category's key.
            out["item_name"] = _label(item)
            out["item_type"] = item.get("type") or item.get("category")
            out["item_price"] = item.get("price", item.get("cost"))

    elif verb in ("select_relic", "claim_treasure_relic"):
        idx = action.get("index")
        # `EB-263`: the chest writes `treasure.relics` and the relic-select
        # screen writes `relic_select.relics`; neither is a top-level key.
        relics = (_relics(state, "treasure") or _relics(state, "relic_select")
                  or state.get("relics") or state.get("options") or [])
        out["option_index"] = idx
        out["relic_name"] = _label(_at(relics, idx))

    elif verb == "claim_reward":
        idx = action.get("index")
        blob = state.get("rewards")
        items = blob.get("items") if isinstance(blob, dict) else (blob or [])
        out["option_index"] = idx
        out["reward_name"] = _label(_at(items, idx))

    elif verb == "menu_select":
        out["option_name"] = action.get("option")

    elif verb == "select_bundle":
        out["option_index"] = action.get("index")

    # Screen context on every row, so a divergence can be sliced by screen
    # without joining back to the state dump.
    out["state_type"] = st
    return {k: v for k, v in out.items() if v is not None}


def hand_names(state: dict[str, Any]) -> list[str]:
    """Every card in hand, by name, in index order. The denominator a
    sequencing divergence is read against."""
    return [str(c.get("name") or c.get("id") or "?")
            for c in _hand(state) if isinstance(c, dict)]
