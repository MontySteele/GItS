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
    if vs.dawn and element == vs.current:
        # R4 Dawn Wind's March: "Whenever you gain Oath of your current
        # element, gain 2 Block" -- per gain event, not per point.
        blk = vs.dawn_amt * vs.dawn
        state.player.block += blk
        vs.dawn_block += blk
        state.emit("block", amount=blk)
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


def set_current(state, vs, element, knight=True) -> None:
    if element not in ELEMENTS:
        return
    if knight and vs.standard and element == vs.current:
        # R4 Favonian Standard: "Whenever you play a Knight of your current
        # element" -- read as the element current BEFORE the Knight, i.e. a
        # Knight that keeps him where he is.
        blk = vs.std_amt * vs.standard
        state.player.block += blk
        vs.standard_block += blk
        state.emit("block", amount=blk)
    if element != vs.current:
        vs.switches += 1 if vs.current is not None else 0
        vs.current = element
        if vs.unbound:
            state.player.energy += vs.unbound
            vs.unbound_energy += vs.unbound
    if knight:
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
    if vs.no_apply:
        return          # R5 Baron Bunny's burst credits its Oath itself
    if not _once_per_play(state, vs, element, "apply"):
        return
    # 2026-09-29 second spec update: EVERY direct application counts,
    # including one that reacts instead of leaving an aura.
    gain_oath(state, vs, element, 1, "apply")


def on_swirl(state, vs, enemy, aura) -> None:
    from tier0.engine import powers, reactions        # late: cycle
    vs.swirls += 1
    vs.swirls_this_card += 1
    vs.swirled_ids.add(id(enemy))
    vs.swirl_log.append((state.turn, aura))
    if _once_per_play(state, vs, aura, "swirl"):
        gain_oath(state, vs, aura, 1, "swirl")
    if not vs.payout or vs.current is None:
        return
    cur = vs.current
    if cur == "pyro":
        if vs.pyro_all:
            # R5 contingency: "3 damage to every enemy that Swirl touched",
            # read as every living enemy now wearing the Swirled element
            # (the struck enemy, the spread copies, and any already on it).
            for e in [e for e in state.living_enemies if e.aura == aura]:
                reactions._splash(state, e, PAY_PYRO)
                vs.pay["pyro_dmg"] += PAY_PYRO
        elif enemy.alive:
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
        if vs.electro_draw:
            state.draw(1)                  # R4 E-Draw: draw 1 per Swirl
            vs.pay["electro_dmg"] += 1
            return
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
    if vs.bunny:
        _bunny_fire(state, vs)
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
        name = state.rng.choice(tuple(vs.roll_pool))
        c = make_card(vs.swap.get(name, name))
        c.free_this_turn = True
        if len(state.player.hand) < HAND_LIMIT:
            state.player.hand.append(c)
        else:
            state.player.discard_pile.append(c)
    elif kind in R4_OPS:
        R4_OPS[kind](state, vs, fx, card)
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


def _register_block_variants():
    for base, block, new in (
            ("barbara_shining_miracle_one", 0,
             "barbara_shining_miracle_one_b0"),
            ("barbara_shining_miracle_one", 5,
             "barbara_shining_miracle_one_b5"),
            ("amber_fiery_rain", 5, "amber_fiery_rain_b5"),
            ("lisa_lightning_rose", 5, "lisa_lightning_rose_b5"),
            ("kaeya_glacial_waltz", 5, "kaeya_glacial_waltz_b5")):
        CARD_BUILDERS[new] = _block_variant(base, block, new)


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
    # The Block test (fifth round): S5 Barbara one enemy, 0 Block; S6
    # Barbara one enemy 7 Block and the other three +5 Block; S7 all four
    # one-target with 5 Block.
    "S5": {"barbara_shining_miracle": "barbara_shining_miracle_one_b0"},
    "S6": {"barbara_shining_miracle": "barbara_shining_miracle_one",
           "amber_fiery_rain": "amber_fiery_rain_b5",
           "lisa_lightning_rose": "lisa_lightning_rose_b5",
           "kaeya_glacial_waltz": "kaeya_glacial_waltz_b5"},
    "S7": {"barbara_shining_miracle": "barbara_shining_miracle_one_b5",
           "amber_fiery_rain": "amber_fiery_rain_b5",
           "lisa_lightning_rose": "lisa_lightning_rose_b5",
           "kaeya_glacial_waltz": "kaeya_glacial_waltz_b5"},
}


def _block_variant(base: str, block: int, new: str):
    """A starter Knight with its Block set to `block` (added if absent)."""
    def build():
        c = make_card(base)
        c.id = f"varka_{new}"
        for fx in c.effects:
            if fx.get("op") == "varka" and fx.get("kind") == "knight":
                inner = [i for i in fx["inner"] if i.get("op") != "block"]
                if block:
                    inner.append({"op": "block", "amount": block})
                fx["inner"] = inner
        return c
    return build


def build_player(deck: list[str], payout: bool = True,
                 apply_oath: bool = True, hp: int | None = None,
                 per_card: bool = False, starter_set: str | None = None,
                 pay_electro: int = PAY_ELECTRO_ALL,
                 electro_draw: bool = False, r4: bool = False,
                 swap: dict | None = None, std_amt: int = 3,
                 dawn_amt: int = 2, pyro_all: bool = False):
    """A fresh rev-3 Varka for one fight, holding exactly `deck` (card
    names; use `starter(el)` + extras)."""
    from tier0.engine.state import Player
    swap_all = dict(STARTER_SETS.get(starter_set, {}), **(swap or {}))
    cards = [make_card(swap_all.get(n, n)) for n in deck]
    hp = V.HP if hp is None else hp
    player = Player(hp=hp, max_hp=max(hp, V.HP), draw_pile=cards,
                    element=V.ELEMENT, cadence="catalyst",
                    character_id=V.CHARACTER)
    vs = V.VarkaState(rev=3)
    vs.payout = payout
    vs.apply_oath = apply_oath
    vs.per_card = per_card
    vs.pay_electro = pay_electro
    vs.electro_draw = electro_draw
    vs.swap = dict(swap or {})
    vs.std_amt, vs.dawn_amt, vs.pyro_all = std_amt, dawn_amt, pyro_all
    if r4:
        vs.roll_pool = R4_KNIGHTS
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


# ==========================================================================
#  R4: the paper at HEAD (sec.3-6, batch two). Behind the same arm; built by
#  `build_player(..., r4=True)` with `starter4(element)` and `POOL4`.
#
#  READINGS TAKEN (listed in the report):
#    * Favonian Standard pays on a Knight whose element was ALREADY current
#      (see `set_current`); the first Knight of a fight never pays.
#    * Dawn Wind's March pays 2 Block per Oath GAIN EVENT of the current
#      element (a Sworn Brotherhood tick, Accord's +1, a Knight, a Swirl).
#    * Change of Guard: the pilot names the element (`vs.cog_choice`); it
#      must have Oath (else the card only gives 0 Block). It is not a Knight,
#      so Favonian Standard and Knightly Guard do not see it; Boreas Unbound
#      does (the current element changes).
#    * Jean: Dandelion Breeze is a Skill, not a Knight; it Swirls the aimed
#      enemy's fresh aura, else the first fresh aura on the board.
#    * Storm Surge's "5 more" is element-less damage to each enemy its own
#      hits Swirled.
#    * Oathsworn Strike and Azure Devour deal element-less damage.
#    * Northwind Avatar's elemental hit gains Oath like any card's (only
#      Ascension's own hit is excluded); its Oath is read after the Anemo hit.
#    * Eula's per-enemy Oath counts enemies wearing Cryo (fresh or spent)
#      after her hit.
#    * Unfurled Banner does nothing if Ascension is not in the discard pile.
# ==========================================================================

DAWN_BLOCK = 2
STANDARD_BLOCK = 3
R4_KNIGHTS = ("amber", "barbara", "lisa", "kaeya", "razor", "mika",
              "diluc", "eula", "barbara_whisper")


def _r4_jean(state, vs, fx, card):
    from tier0.engine import effects, reactions
    effects._op_block(state, {"op": "block", "amount": fx["block"]}, card)
    t = state.card_aim
    if t is None or not t.alive or not (t.aura and not t.aura_spent):
        t = next((e for e in state.living_enemies
                  if e.aura and not e.aura_spent), None)
    if t is not None:
        reactions.resolve_hit(state, t, V.ELEMENT, 0, "jean")


def _r4_knightly_guard(state, vs, fx, card):
    from tier0.engine import effects
    effects._op_block(state, {"op": "block", "amount": fx["block"]}, card)
    if vs.current and any(t == state.turn for t, _ in vs.knights_played):
        gain_oath(state, vs, vs.current, 1, "guard")


def _r4_oathsworn(state, vs, fx, card):
    from tier0.engine import effects
    effects._op_damage(state, {"op": "damage", "target": "enemy",
                               "amount": fx["base"] + current_oath(vs)}, card)


def _r4_azure(state, vs, fx, card):
    from tier0.engine import effects
    n = current_oath(vs)
    if n:
        effects._op_damage(state, {"op": "damage", "target": "enemy",
                                   "amount": fx["per"] * n}, card)


def _r4_block_if_swirled(state, vs, fx, card):
    from tier0.engine import effects
    if vs.swirls_this_card:
        effects._op_block(state, {"op": "block", "amount": fx["amount"]},
                          card)


def _r4_eula_oath(state, vs, fx, card):
    n = sum(1 for e in state.living_enemies if e.aura == "cryo")
    if n:
        gain_oath(state, vs, "cryo", n, "eula")


def _r4_standard(state, vs, fx, card):
    vs.standard += 1


def _r4_dawn(state, vs, fx, card):
    vs.dawn += 1


def _r4_change_of_guard(state, vs, fx, card):
    from tier0.engine import effects
    el = vs.cog_choice or vs.current
    vs.cog_choice = None
    if el not in ELEMENTS or vs.oath.get(el, 0) <= 0:
        return
    effects._op_block(state, {"op": "block", "amount": vs.oath[el]}, card)
    set_current(state, vs, el, knight=False)
    vs.cog_rows.append((state.turn, el, vs.oath[el]))


def _r4_storm_surge(state, vs, fx, card):
    from tier0.engine import effects
    vs.swirled_ids = set()
    effects._op_damage(state, _dmg(fx["amount"], target="all_enemies"), card)
    for e in list(state.living_enemies):
        if id(e) in vs.swirled_ids:
            effects.deal_damage_to_enemy(state, e, fx["more"], element=None,
                                         source="attack")


def _r4_tailwind_guard(state, vs, fx, card):
    from tier0.engine import effects
    n = sum(1 for v in vs.oath.values() if v > 0)
    effects._op_block(state, {"op": "block", "amount": fx["per"] * n}, card)
    vs.tg_rows.append((state.turn, fx["per"] * n))


def _r4_unfurled(state, vs, fx, card):
    p = state.player
    asc = next((c for c in p.discard_pile
                if c.id == "varka_four_winds_ascension"), None)
    if asc is not None and len(p.hand) < HAND_LIMIT:
        p.discard_pile.remove(asc)
        asc.free_this_turn = True
        p.hand.append(asc)


def _r4_northwind(state, vs, fx, card):
    from tier0.engine import effects
    target = state.card_aim
    effects._op_damage(state, _dmg(fx["anemo"]), card)
    if vs.current and target is not None and target.alive:
        n = current_oath(vs)
        saved = card.element
        card.element = vs.current
        try:
            effects._op_damage(state, _dmg(fx["elem"] + fx["per"] * n), card)
        finally:
            card.element = saved


R4_OPS = {"jean": _r4_jean, "knightly_guard": _r4_knightly_guard,
          "oathsworn": _r4_oathsworn, "azure": _r4_azure,
          "block_if_swirled": _r4_block_if_swirled,
          "eula_oath": _r4_eula_oath, "standard": _r4_standard,
          "dawn": _r4_dawn, "change_of_guard": _r4_change_of_guard,
          "storm_surge": _r4_storm_surge,
          "tailwind_guard": _r4_tailwind_guard, "unfurled": _r4_unfurled,
          "northwind": _r4_northwind}


def _r4_starter_knight(cid, name, element):
    return lambda: _knight(
        cid, name, element,
        [{"op": "block", "amount": 8},
         {"op": "apply_aura", "element": element, "target": "enemy"}],
        rarity="basic")


def _attack_knight(builder):
    def build():
        c = builder()
        c.type = "attack"
        c.cost = 2
        return c
    return build


CARD_BUILDERS.update({
    # starters (sec.5): "Gain 8 [11] Block. Apply its element to an enemy."
    "amber_fiery_rain_r4": _r4_starter_knight(
        "amber_fiery_rain_r4", "Amber: Fiery Rain", "pyro"),
    "barbara_melody_loop": _r4_starter_knight(
        "barbara_melody_loop", "Barbara: Melody Loop", "hydro"),
    "lisa_lightning_rose_r4": _r4_starter_knight(
        "lisa_lightning_rose_r4", "Lisa: Lightning Rose", "electro"),
    "kaeya_glacial_waltz_r4": _r4_starter_knight(
        "kaeya_glacial_waltz_r4", "Kaeya: Glacial Waltz", "cryo"),
    # Eye of the Storm, now Exhaust
    "eye_of_the_storm_x": lambda: _card(
        "eye_of_the_storm_x", "Eye of the Storm", 1, "skill", "uncommon",
        [_o("eye", per=2)], exhaust=True, element="none"),
    # batch two, Common
    "razor": lambda: _knight("razor", "Razor: Claw and Thunder", "electro",
                             [_dmg(7)]),
    "mika": lambda: _knight(
        "mika", "Mika: Starfrost Swirl", "cryo",
        [{"op": "apply_aura", "element": "cryo", "target": "enemy"},
         {"op": "block", "amount": 6}]),
    "jean": lambda: _card("jean", "Jean: Dandelion Breeze", 1, "skill",
                          "common", [_o("jean", block=7)], element="none"),
    "knightly_guard": lambda: _card(
        "knightly_guard", "Knightly Guard", 1, "skill", "common",
        [_o("knightly_guard", block=8)], element="none"),
    "oathsworn_strike": lambda: _card(
        "oathsworn_strike", "Oathsworn Strike", 1, "attack", "common",
        [_o("oathsworn", base=6)], element="none"),
    "crosswind": lambda: _card(
        "crosswind", "Crosswind", 1, "attack", "common",
        [V._v("count_begin"), _dmg(7), _o("block_if_swirled", amount=4)]),
    "rising_gale": lambda: _card(
        "rising_gale", "Rising Gale", 0, "attack", "common",
        [V._v("count_begin"), _dmg(4),
         V._v("draw_if_swirled", amount=1)]),
    # batch two, Uncommon
    "diluc": _attack_knight(lambda: _knight(
        "diluc", "Diluc: Searing Onslaught", "pyro", [_dmg(6, times=2)],
        rarity="uncommon")),
    "eula": lambda: _cost(_knight(
        "eula", "Eula: Icetide Vortex", "cryo",
        [_dmg(10), _o("eula_oath")], rarity="uncommon"), 2),
    "barbara_whisper": lambda: _knight(
        "barbara_whisper", "Barbara: Whisper of Water", "hydro",
        [{"op": "apply_aura", "element": "hydro", "target": "enemy"},
         {"op": "block", "amount": 4},
         {"op": "block_next_turn", "amount": 4}], rarity="uncommon"),
    "favonian_standard": lambda: _card(
        "favonian_standard", "Favonian Standard", 1, "power", "uncommon",
        [_o("standard")]),
    "change_of_guard": lambda: _card(
        "change_of_guard", "Change of Guard", 1, "skill", "uncommon",
        [_o("change_of_guard")], exhaust=True, element="none"),
    "storm_surge": lambda: _card(
        "storm_surge", "Storm Surge", 2, "attack", "uncommon",
        [_o("storm_surge", amount=5, more=5)]),
    "tailwind_guard": lambda: _card(
        "tailwind_guard", "Tailwind Guard", 1, "skill", "uncommon",
        [_o("tailwind_guard", per=3)], element="none"),
    "unfurled_banner": lambda: _card(
        "unfurled_banner", "Unfurled Banner", 1, "skill", "uncommon",
        [_o("unfurled")], exhaust=True, element="none"),
    # batch two, Rare
    "northwind_avatar": lambda: _card(
        "northwind_avatar", "Northwind Avatar", 3, "attack", "rare",
        [_o("northwind", anemo=12, elem=12, per=2)]),
    "dawn_winds_march": lambda: _card(
        "dawn_winds_march", "Dawn Wind's March", 2, "power", "rare",
        [_o("dawn")]),
    "azure_devour": lambda: _card(
        "azure_devour", "Azure Devour", 2, "attack", "rare",
        [_o("azure", per=4)], exhaust=True, element="none"),
})


def _cost(card, cost):
    card.cost = cost
    return card


STARTER_KNIGHTS4 = {"pyro": "amber_fiery_rain_r4",
                    "hydro": "barbara_melody_loop",
                    "electro": "lisa_lightning_rose_r4",
                    "cryo": "kaeya_glacial_waltz_r4"}
POOL_KNIGHTS4 = {"pyro": ("amber", "diluc"),
                 "hydro": ("barbara", "barbara_whisper"),
                 "electro": ("lisa", "razor"),
                 "cryo": ("kaeya", "mika", "eula")}
NEW4 = ("razor", "mika", "jean", "knightly_guard", "oathsworn_strike",
        "crosswind", "rising_gale", "diluc", "eula", "barbara_whisper",
        "favonian_standard", "change_of_guard", "storm_surge",
        "tailwind_guard", "unfurled_banner", "northwind_avatar",
        "dawn_winds_march", "azure_devour")
POOL4 = {
    "common": ["squall", "updraft", "gale_sweep", "wind_wall",
               "favonius_drill", "amber", "barbara", "lisa", "kaeya",
               "razor", "mika", "jean", "knightly_guard", "oathsworn_strike",
               "crosswind", "rising_gale"],
    "uncommon": ["tempest_charge", "favonius_cut", "grand_masters_order",
                 "knights_roll_call", "tailwind_stride", "eye_of_the_storm_x",
                 "stormward_stance", "oath_of_the_knights",
                 "rally_to_the_banner", "diluc", "eula", "barbara_whisper",
                 "favonian_standard", "change_of_guard", "storm_surge",
                 "tailwind_guard", "unfurled_banner"],
    "rare": ["converging_winds", "boreas_unbound", "wall_of_gales",
             "four_winds_accord", "sworn_brotherhood", "northwind_avatar",
             "dawn_winds_march", "azure_devour"],
}


def starter4(element: str) -> list[str]:
    return (["strike"] * 4 + ["defend"] * 4
            + ["windbound_execution", STARTER_KNIGHTS4[element]])



# ==========================================================================
#  R5: paper sec.10 Picks. Pick 2 (RULED): Lisa: Violet Arc and Amber: Baron
#  Bunny re-aimed. Picks 3 and 4 run as arms (`std_amt`, `dawn_amt`, the
#  `northwind_avatar_c` card). Readings:
#    * Lisa counts `state.attacks_played_this_turn` when she resolves; she is
#      a Skill, so she never counts herself.
#    * Baron Bunny's burst fires at the post-draw turn start (before Sworn
#      Brotherhood and Oath of the Knights), 6 Pyro to each living enemy
#      through the ordinary damage door (source "card", unpowered by
#      Strength), and gains exactly 1 Pyro Oath per Bunny played, as a card
#      application; it does not change the current element.
# ==========================================================================


def _r5_lisa(state, vs, fx, card):
    from tier0.engine import effects
    n = state.attacks_played_this_turn
    blk = fx.get("base", 0) + fx["per"] * n
    if blk:
        effects._op_block(state, {"op": "block", "amount": blk}, card)
    vs.lisa_rows.append((state.turn, n, blk))


def _r5_bunny(state, vs, fx, card):
    vs.bunny.append(fx["amount"])


def _bunny_fire(state, vs):
    from tier0.engine import effects
    pending, vs.bunny = vs.bunny, []
    for amount in pending:
        vs.no_apply = True
        try:
            for e in list(state.living_enemies):
                effects.deal_damage_to_enemy(state, e, amount, element="pyro",
                                             source="card", powered=False)
        finally:
            vs.no_apply = False
        gain_oath(state, vs, "pyro", 1, "bunny")
        vs.bunny_rows.append((state.turn, amount))


R4_OPS.update({"lisa_block": _r5_lisa, "bunny": _r5_bunny})

CARD_BUILDERS.update({
    "lisa_r5": lambda: _knight(
        "lisa_r5", "Lisa: Violet Arc", "electro",
        [{"op": "apply_aura", "element": "electro", "target": "enemy"},
         _o("lisa_block", per=3)]),
    "lisa_r5_4": lambda: _knight(
        "lisa_r5_4", "Lisa: Violet Arc (4)", "electro",
        [{"op": "apply_aura", "element": "electro", "target": "enemy"},
         _o("lisa_block", per=4)]),
    # R6, pick 5 (Lisa's floor): 3 [4] Block, plus 3 [4] per Attack.
    "lisa_r6": lambda: _knight(
        "lisa_r6", "Lisa: Violet Arc", "electro",
        [{"op": "apply_aura", "element": "electro", "target": "enemy"},
         _o("lisa_block", base=3, per=3)]),
    "lisa_r6_4": lambda: _knight(
        "lisa_r6_4", "Lisa: Violet Arc (4 + 3)", "electro",
        [{"op": "apply_aura", "element": "electro", "target": "enemy"},
         _o("lisa_block", base=4, per=3)]),
    "amber_r5": lambda: _knight(
        "amber_r5", "Amber: Baron Bunny", "pyro",
        [{"op": "block", "amount": 6}, _o("bunny", amount=6)]),
    "northwind_avatar_c": lambda: _card(
        "northwind_avatar_c", "Northwind Avatar", 2, "attack", "rare",
        [_o("northwind", anemo=10, elem=10, per=2)]),
})



_register_block_variants()
