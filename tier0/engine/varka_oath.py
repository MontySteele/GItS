"""VARKA, THE OATH REWORK -- a PAPER-STAGE sim arm (exploration only).

Source of truth: `review/active/varka-paper-kit-2026-09-28.md` sec.11 (branch
`varka-oath-paper`, PR #767). Numbers are the paper's placeholders and are
NOT tuned here. Measured by `tools/varka_oath_report.py`; nothing here is a
balance claim and no calibration band reads it.

It rides the Varka paper arm's switch (`varka_paper.VARKA_PAPER`, off) as
REVISION 3: a Varka built by `build_player` here carries a `VarkaState` with
`rev=3`, and the paper arm's hooks hand a rev-3 Varka to the functions below.
With the switch off nothing here is reachable; with it on, revisions 1-2.2
are unchanged (every rev-3 branch is keyed on `vs.rev == 3`). The one op the
new cards speak, `varka_oath`, is registered by `enable()` only.

THE RULES AS MODELLED (sec.11.1-11.2):
  * OATH, one count per element (P/H/E/C), on the VarkaState, fresh per fight.
    +1 each time Varka APPLIES the element to an enemy and +1 each time he
    SWIRLS an aura of it. A count only rises, except through Rally to the
    Banner and Four Winds' Accord.
  * CURRENT ELEMENT = the element of the last Knight played (None before the
    first). Readers read only its Oath.
  * SWIRL PAYOUT of the current element only (2026-09-29 spec change, over
    the paper's first text): Pyro 3 (element-less, the flat 2's path) to the
    enemy Swirled; Hydro 3 Block; Cryo 1 Vulnerable on the enemy Swirled;
    Electro 2 (element-less) to ALL enemies, on every Swirl.
  * The starter Kaeya: Glacial Waltz applies 1 Vulnerable (was Weak), and
    Headwind is cut from the pool (23 cards: 9 / 9 / 5).
  * BOREAS'S FANG: the first Oath gained each combat adds Four Winds'
    Ascension to hand (to the discard pile if the hand holds 10).
  * FOUR WINDS' ASCENSION (Attack, 1, created, not Exhaust): 6 Anemo, then
    3 per current-element Oath as that element, both hits on one enemy. The
    Oath is read AFTER the Anemo hit (a Swirl it makes counts).

R3b (third spec update, 2026-09-29; `build_player(per_card=True)`, the
report's default): a card play gains 1 Oath per element it applies, however
many enemies or hits, and 1 per distinct element it Swirls; the Swirl
payouts still fire per Swirl. Ascension's elemental hit gains no Oath (it
still applies, refreshes or reacts). `per_card=False` is R3, the rule above.

VARIANTS (the paper's picks), per fight on the VarkaState:
  * `payout=False`  -- pick 1 option 2: no Swirl payout.
  * `apply_oath=False` -- pick 2 option 2: Oath from Swirls only.

READINGS TAKEN WHERE THE PAPER IS SILENT (each flagged in the report):
  * THE OATH EVENT (second spec update, 2026-09-29, over the paper text):
    +1 for each direct application of the element to a live enemy by
    Varka's cards (a Knight, Favonius Drill, Ascension's elemental hit),
    INCLUDING one that reacts instead of leaving an aura; each hit of a
    multi-hit card counts. +1 for each actual Swirl of an aura of it.
  * A Swirl's SPREAD copies and a Converging Winds landing (and any
    reaction it sets off) do NOT count: `varka_paper.intercept_hit` returns
    before this module is asked while a landing resolves, and a spread copy
    is placed by `apply_aura`, never through `resolve_hit`.
  * An element-changing Knight counts as a change for Boreas Unbound when
    Varka had no current element yet (none -> Pyro is a change).
  * Oath gained with no current element (Sworn Brotherhood before a Knight)
    still triggers the Fang; Ascension then deals its 6 Anemo only.
  * Oath of the Knights and Sworn Brotherhood fire at the post-draw turn
    start site (`combat` calls `turn_start`), Oath of the Knights reading the
    Oath AFTER Sworn Brotherhood's gain.
  * Wall of Gales Swirls each enemy wearing a fresh aura when it is played
    (a 0-damage Anemo hit each, so the flat 2 and the payout land per Swirl).
"""

from __future__ import annotations

from tier0.engine import varka_paper as V

ELEMENTS = V.WIND_ELEMENTS               # pyro, hydro, electro, cryo
HAND_LIMIT = 10

PAY_PYRO = 3
PAY_HYDRO = 3
PAY_CRYO_VULN = 1
PAY_ELECTRO_ALL = 2
ASC_BASE = 6
ASC_PER_OATH = 3
STORMWARD_OATH = 4
STORMWARD_BONUS = 3


# --------------------------------------------------------------------------
#  State helpers
# --------------------------------------------------------------------------

def _vs(state):
    vs = V.vs_of(state)
    return vs if vs is not None and vs.rev == 3 else None


def current_oath(vs) -> int:
    return vs.oath.get(vs.current, 0) if vs.current else 0


def gain_oath(state, vs, element, n=1, source="apply") -> None:
    if element not in ELEMENTS or n <= 0:
        return
    vs.oath[element] = vs.oath.get(element, 0) + n
    vs.oath_log.append((state.turn, element, n, source))
    if not vs.fang_done:
        vs.fang_done = True
        _add_ascension(state, vs)


def _add_ascension(state, vs) -> None:
    card = make_card("four_winds_ascension")
    p = state.player
    if len(p.hand) >= HAND_LIMIT:
        p.discard_pile.append(card)
    else:
        p.hand.append(card)
    vs.asc_created_turn = state.turn


def set_current(state, vs, element) -> None:
    if element not in ELEMENTS:
        return
    if element != vs.current:
        vs.switches += 1 if vs.current is not None else 0
        vs.current = element
        if vs.unbound:
            state.player.energy += vs.unbound
            vs.unbound_energy += vs.unbound
    vs.knights_played.append((state.turn, element))


# --------------------------------------------------------------------------
#  Hooks (called from varka_paper's hooks for a rev-3 Varka)
# --------------------------------------------------------------------------

def _once_per_play(state, vs, element, source) -> bool:
    """R3b: True the first time this card play earns `source` Oath of
    `element`; False after. Always True under R3."""
    if not vs.per_card:
        return True
    key = (state.turn, state.cards_played_this_turn, id(vs.playing),
           source, element)
    if key in vs.credited:
        return False
    vs.credited.add(key)
    return True


def on_hit_pre(state, vs, enemy, element) -> None:
    """Before the shared rule resolves an element hit: an application?"""
    if not vs.apply_oath or element not in ELEMENTS or not enemy.alive:
        return
    if vs.per_card and vs.asc_elemental:
        return          # R3b: Ascension's elemental hit gains no Oath
    if not _once_per_play(state, vs, element, "apply"):
        return
    # 2026-09-29 second spec update: EVERY direct application counts,
    # including one that reacts instead of leaving an aura.
    gain_oath(state, vs, element, 1, "apply")


def on_swirl(state, vs, enemy, aura) -> None:
    from tier0.engine import powers, reactions        # late: cycle
    vs.swirls += 1
    vs.swirls_this_card += 1
    vs.swirl_log.append((state.turn, aura))
    if _once_per_play(state, vs, aura, "swirl"):
        gain_oath(state, vs, aura, 1, "swirl")
    if not vs.payout or vs.current is None:
        return
    cur = vs.current
    if cur == "pyro":
        if enemy.alive:
            reactions._splash(state, enemy, PAY_PYRO)
            vs.pay["pyro_dmg"] += PAY_PYRO
    elif cur == "hydro":
        state.player.block += PAY_HYDRO
        vs.pay["hydro_block"] += PAY_HYDRO
        state.emit("block", amount=PAY_HYDRO)
    elif cur == "cryo":
        if enemy.alive:
            powers.apply_power(state, enemy, "vulnerable", PAY_CRYO_VULN)
            vs.pay["cryo_vuln"] += PAY_CRYO_VULN
    elif cur == "electro":
        for e in list(state.living_enemies):
            reactions._splash(state, e, vs.pay_electro)
            vs.pay["electro_dmg"] += vs.pay_electro


def attack_bonus(state, vs, card) -> int:
    if (vs.stormward and card.element == V.ELEMENT
            and current_oath(vs) >= STORMWARD_OATH):
        return vs.stormward
    return 0


def turn_start(state) -> None:
    """Post-draw turn start: Sworn Brotherhood, then Oath of the Knights."""
    vs = _vs(state)
    if vs is None:
        return
    for _ in range(vs.sworn):
        for el in ELEMENTS:
            gain_oath(state, vs, el, 1, "sworn")
    if vs.okn:
        blk = current_oath(vs) * vs.okn
        if blk:
            state.player.block += blk
            state.emit("block", amount=blk)
        vs.okn_block += blk
        vs.okn_rows.append((state.turn, blk))
    vs.turn_oath.append((state.turn, vs.current, current_oath(vs),
                         dict(vs.oath)))


# --------------------------------------------------------------------------
#  The op: {op: varka_oath, kind: ...}
# --------------------------------------------------------------------------

def _dmg(amount, target="enemy", times=1):
    return {"op": "damage", "amount": amount, "target": target,
            "applies_element": True, "times": times}


def _dealt_since(state, mark) -> int:
    return sum(r.get("amount", 0) for r in state.log[mark:]
               if r.get("event") == "damage")


def op_oath(state, fx, card) -> None:
    from tier0.engine import effects, reactions       # late: cycle
    vs = _vs(state)
    kind = fx["kind"]
    if kind == "ascension":
        mark = len(state.log)
        target = state.card_aim
        oath_before = current_oath(vs)
        effects._op_damage(state, _dmg(ASC_BASE), card)
        n = current_oath(vs)
        elem_amt = 0
        if vs.current and n and target is not None and target.alive:
            saved = card.element
            card.element = vs.current
            vs.asc_elemental = True
            try:
                effects._op_damage(state, _dmg(ASC_PER_OATH * n), card)
            finally:
                card.element = saved
                vs.asc_elemental = False
            elem_amt = ASC_PER_OATH * n
        vs.asc.append({"turn": state.turn, "element": vs.current,
                       "oath": n, "oath_before": oath_before,
                       "printed": ASC_BASE + elem_amt,
                       "dealt": _dealt_since(state, mark)})
    elif kind == "drill":
        effects._op_block(state, {"op": "block", "amount": fx["block"]}, card)
        t = state.card_aim
        if vs.current and t is not None and t.alive:
            reactions.resolve_hit(state, t, vs.current, 0, "apply_aura_op")
    elif kind == "wind_wall":
        amt = fx["amount"] + (fx["bonus"] if vs.current else 0)
        effects._op_block(state, {"op": "block", "amount": amt}, card)
    elif kind == "tailwind":
        state.draw(fx["amount"] + (1 if vs.current else 0))
    elif kind == "eye":
        amt = fx["per"] * current_oath(vs)
        effects._op_block(state, {"op": "block", "amount": amt}, card)
        vs.eye_rows.append((state.turn, amt, vs.current))
    elif kind == "stormward":
        vs.stormward += STORMWARD_BONUS
    elif kind == "unbound":
        vs.unbound += 1
    elif kind == "okn":
        vs.okn += 1
    elif kind == "sworn":
        vs.sworn += 1
    elif kind == "wall_of_gales":
        effects._op_block(state, {"op": "block", "amount": fx["block"]}, card)
        for e in [e for e in state.living_enemies
                  if e.aura and not e.aura_spent]:
            if e.alive and e.aura and not e.aura_spent:
                reactions.resolve_hit(state, e, V.ELEMENT, 0, "wall_of_gales")
    elif kind == "headwind":
        from tier0.engine import powers
        targets = (list(state.living_enemies) if vs.current == "cryo"
                   else [state.card_aim] if state.card_aim is not None
                   and state.card_aim.alive else [])
        for e in targets:
            powers.apply_power(state, e, "weak", fx["amount"])
    elif kind == "rally":
        if vs.current:
            total = sum(vs.oath.values())
            vs.oath = {el: 0 for el in ELEMENTS}
            vs.oath[vs.current] = total
    elif kind == "accord":
        total = sum(vs.oath.values())
        each = total // 4
        vs.oath = {el: each for el in ELEMENTS}
        for el in ELEMENTS:
            gain_oath(state, vs, el, 1, "accord")
    elif kind == "roll_call":
        name = state.rng.choice(("amber", "barbara", "lisa", "kaeya"))
        c = make_card(name)
        c.free_this_turn = True
        if len(state.player.hand) < HAND_LIMIT:
            state.player.hand.append(c)
        else:
            state.player.discard_pile.append(c)
    else:
        raise ValueError(f"unknown varka_oath kind {kind!r}")


# --------------------------------------------------------------------------
#  Cards (sim-side defs; never in the loader's index)
# --------------------------------------------------------------------------

def _o(kind, **kw):
    return {"op": "varka_oath", "kind": kind, **kw}


def _card(cid, name, cost, ctype, rarity, effects_, exhaust=False,
          element=V.ELEMENT):
    from tier0.engine.state import Card
    return Card(id=f"varka_{cid}", name=name, cost=cost, type=ctype,
                rarity=rarity, element=element, effects=effects_,
                exhaust=exhaust, character=V.CHARACTER)


def _knight(cid, name, element, inner, all_=False, rarity="common"):
    return V._knight(cid, name, element, inner, all_=all_, rarity=rarity)


CARD_BUILDERS = {
    # --- starter (sec.11.3) ---
    "amber_fiery_rain": lambda: _knight(
        "amber_fiery_rain", "Amber: Fiery Rain", "pyro", [_dmg(9)],
        rarity="basic"),
    "barbara_shining_miracle": lambda: _knight(
        "barbara_shining_miracle", "Barbara: Shining Miracle", "hydro",
        [{"op": "apply_aura", "element": "hydro", "target": "all_enemies"},
         {"op": "block", "amount": 7}], all_=True, rarity="basic"),
    "lisa_lightning_rose": lambda: _knight(
        "lisa_lightning_rose", "Lisa: Lightning Rose", "electro",
        [_dmg(6), {"op": "draw", "amount": 2}], rarity="basic"),
    "kaeya_glacial_waltz": lambda: _knight(
        "kaeya_glacial_waltz", "Kaeya: Glacial Waltz", "cryo",
        [_dmg(6), {"op": "apply_power", "power": "vulnerable", "amount": 1,
                   "target": "enemy"}], rarity="basic"),
    "windbound_execution": lambda: _card(
        "windbound_execution", "Windbound Execution", 1, "attack", "basic",
        [_dmg(4, target="all_enemies")]),
    "four_winds_ascension": lambda: _card(
        "four_winds_ascension", "Four Winds' Ascension", 1, "attack",
        "special", [_o("ascension")]),
    # --- starter-evenness variants (STARTER_SETS) ---
    "barbara_shining_miracle_one": lambda: _knight(
        "barbara_shining_miracle_one", "Barbara: Shining Miracle (one)",
        "hydro", [{"op": "apply_aura", "element": "hydro",
                   "target": "enemy"},
                  {"op": "block", "amount": 7}], rarity="basic"),
    "amber_fiery_rain_all": lambda: _knight(
        "amber_fiery_rain_all", "Amber: Fiery Rain (ALL)", "pyro",
        [_dmg(5, target="all_enemies")], all_=True, rarity="basic"),
    "lisa_lightning_rose_all": lambda: _knight(
        "lisa_lightning_rose_all", "Lisa: Lightning Rose (ALL)", "electro",
        [_dmg(3, target="all_enemies"), {"op": "draw", "amount": 2}],
        all_=True, rarity="basic"),
    "kaeya_glacial_waltz_all": lambda: _knight(
        "kaeya_glacial_waltz_all", "Kaeya: Glacial Waltz (ALL)", "cryo",
        [_dmg(3, target="all_enemies"),
         {"op": "apply_power", "power": "vulnerable", "amount": 1,
          "target": "all_enemies"}], all_=True, rarity="basic"),
    # --- sec.11.4 re-aimed ---
    "favonius_drill": lambda: _card(
        "favonius_drill", "Favonius Drill", 1, "skill", "common",
        [_o("drill", block=6)], element="none"),
    "wind_wall": lambda: _card(
        "wind_wall", "Wind Wall", 1, "skill", "common",
        [_o("wind_wall", amount=7, bonus=3)], element="none"),
    "tailwind_stride": lambda: _card(
        "tailwind_stride", "Tailwind Stride", 1, "skill", "uncommon",
        [_o("tailwind", amount=2)], element="none"),
    "favonius_cut": lambda: _card(
        "favonius_cut", "Favonius Cut", 2, "attack", "uncommon", [_dmg(14)]),
    "eye_of_the_storm": lambda: _card(
        "eye_of_the_storm", "Eye of the Storm", 1, "skill", "uncommon",
        [_o("eye", per=2)], element="none"),
    "stormward_stance": lambda: _card(
        "stormward_stance", "Stormward Stance", 1, "power", "uncommon",
        [_o("stormward")]),
    "boreas_unbound": lambda: _card(
        "boreas_unbound", "Boreas Unbound", 2, "power", "rare",
        [_o("unbound")]),
    "knights_roll_call": lambda: _card(
        "knights_roll_call", "Knights' Roll Call", 1, "skill", "uncommon",
        [_o("roll_call")], element="none"),
    # --- sec.11.5 expansion ---
    "oath_of_the_knights": lambda: _card(
        "oath_of_the_knights", "Oath of the Knights", 1, "power", "uncommon",
        [_o("okn")]),
    "wall_of_gales": lambda: _card(
        "wall_of_gales", "Wall of Gales", 2, "skill", "rare",
        [_o("wall_of_gales", block=16)]),
    # Headwind: CUT (2026-09-29 spec change). Its op stays for reference.
    "rally_to_the_banner": lambda: _card(
        "rally_to_the_banner", "Rally to the Banner", 1, "skill", "uncommon",
        [_o("rally")], exhaust=True, element="none"),
    "four_winds_accord": lambda: _card(
        "four_winds_accord", "Four Winds' Accord", 1, "skill", "rare",
        [_o("accord")], exhaust=True, element="none"),
    "sworn_brotherhood": lambda: _card(
        "sworn_brotherhood", "Sworn Brotherhood", 2, "power", "rare",
        [_o("sworn")]),
}
# Kept as written (sec.11.4), from the paper arm: squall, updraft (new here),
# gale_sweep, tempest_charge, the four pool Knights, grand_masters_order,
# converging_winds.
CARD_BUILDERS["updraft"] = lambda: _card(
    "updraft", "Updraft", 1, "attack", "common", [_dmg(8)])

STARTER_KNIGHTS = {"pyro": "amber_fiery_rain",
                   "hydro": "barbara_shining_miracle",
                   "electro": "lisa_lightning_rose",
                   "cryo": "kaeya_glacial_waltz"}
POOL_KNIGHTS = {"pyro": "amber", "hydro": "barbara", "electro": "lisa",
                "cryo": "kaeya"}

POOL = {
    "common": ["squall", "updraft", "gale_sweep", "amber", "barbara", "lisa",
               "kaeya", "favonius_drill", "wind_wall"],
    "uncommon": ["tempest_charge", "grand_masters_order", "knights_roll_call",
                 "tailwind_stride", "favonius_cut", "eye_of_the_storm",
                 "stormward_stance", "oath_of_the_knights",
                 "rally_to_the_banner"],
    "rare": ["converging_winds", "boreas_unbound", "wall_of_gales",
             "four_winds_accord", "sworn_brotherhood"],
}


def starter(element: str) -> list[str]:
    return (["strike"] * 4 + ["defend"] * 4
            + ["windbound_execution", STARTER_KNIGHTS[element]])


def make_card(name: str):
    if name in CARD_BUILDERS:
        return CARD_BUILDERS[name]()
    return V.make_card(name)


def knight_element(card):
    for fx in card.effects:
        if fx.get("op") == "varka" and fx.get("kind") == "knight":
            return fx["element"]
    return None


# Starter-evenness variants (fourth spec round, 2026-09-29). S1: Barbara:
# Shining Miracle paints ONE enemy. S2: the other three starter Knights hit
# ALL enemies (Amber 5, Lisa 3 + draw 2, Kaeya 3 + 1 Vulnerable to ALL).
STARTER_SETS = {
    "S1": {"barbara_shining_miracle": "barbara_shining_miracle_one"},
    "S2": {"amber_fiery_rain": "amber_fiery_rain_all",
           "lisa_lightning_rose": "lisa_lightning_rose_all",
           "kaeya_glacial_waltz": "kaeya_glacial_waltz_all"},
}


def build_player(deck: list[str], payout: bool = True,
                 apply_oath: bool = True, hp: int | None = None,
                 per_card: bool = False, starter_set: str | None = None,
                 pay_electro: int = PAY_ELECTRO_ALL):
    """A fresh rev-3 Varka for one fight, holding exactly `deck` (card
    names; use `starter(el)` + extras)."""
    from tier0.engine.state import Player
    swap = STARTER_SETS.get(starter_set, {})
    cards = [make_card(swap.get(n, n)) for n in deck]
    hp = V.HP if hp is None else hp
    player = Player(hp=hp, max_hp=max(hp, V.HP), draw_pile=cards,
                    element=V.ELEMENT, cadence="catalyst",
                    character_id=V.CHARACTER)
    vs = V.VarkaState(rev=3)
    vs.payout = payout
    vs.apply_oath = apply_oath
    vs.per_card = per_card
    vs.pay_electro = pay_electro
    player.varka = vs
    return player


def enable() -> None:
    from tier0.engine import effects
    V.enable()
    effects.OPS["varka_oath"] = op_oath


def disable() -> None:
    from tier0.engine import effects
    V.disable()
    effects.OPS.pop("varka_oath", None)
