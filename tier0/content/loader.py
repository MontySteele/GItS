"""YAML content loading: cards, characters, encounters, pilots.

Card files may hold one card or a list. Everything is validated minimally —
this is design tooling; a loud KeyError beats a validation framework.
"""

from __future__ import annotations

import copy
import warnings
from functools import lru_cache
from pathlib import Path

import yaml

from tier0 import constants as C
from tier0.content import enchantments
from tier0.content import local_reference
from tier0.content import upgrades
from tier0.engine import state as state_mod
from tier0.engine.state import Card, Enemy, Player, sly_riders

CONTENT_DIR = Path(__file__).parent
# Design sheets in docs/ are the single source of truth for real card
# pools — the sim reads them directly so design and sim never drift.
DOCS_DIR = CONTENT_DIR.parents[1] / "docs"
DOCS_CARD_SHEETS = ("klee-cards.yaml", "furina-cards.yaml",
                    "kokomi-cards.yaml",
                    "mondstadt-companions.yaml", "fontaine-companions.yaml",
                    "inazuma-companions.yaml")

# The QUARANTINED prototype surface (R213 B, BACKLOG EB-147). DELIBERATELY
# NOT in DOCS_CARD_SHEETS and deliberately not named `*-cards.yaml`.
#
# Both halves of that sentence are load-bearing:
#
#   * Out of DOCS_CARD_SHEETS means out of `_card_index`, which is the ONE
#     index every pool, run template, reward roll, digest and balance report
#     reads. A prototype row is therefore absent from ordinary runs BY
#     CONSTRUCTION rather than by a filter somebody has to remember -- there
#     is no filter, because the rows never enter.
#   * Out of the `docs/*-cards.yaml` NAME keeps it out of
#     `tools/lint_sheet_stamp.py` (whose digest is the sheet half of the stamp
#     law) and `tools/card_distinctness_report.py`, both of which glob that
#     pattern. Each of those two ALSO names this file explicitly, so a future
#     rename cannot quietly re-admit the surface to a stamp.
#
# The rows are still SCHEMA-CHECKED: `prototype_cards()` runs them through
# `Card.from_dict` and the same three validators `_card_index` runs.
# "Not measured" is the quarantine; "not checked" was never on offer.
PROTOTYPE_SHEET = DOCS_DIR / "prototype-surface.yaml"

# Every prototype id starts here. A prototype is usually a variant of
# something that already ships, so its id -- and the C# class name derived
# from it -- would collide with the real card often enough that "we will
# notice" is not a plan, and a duplicated ModelId is a registry defect rather
# than a sheet typo. The prefix also makes the R213 deletion rule greppable:
# `git grep proto_ docs/` answers "did the last slice leave the surface?".
PROTOTYPE_ID_PREFIX = "proto_"

# The real base-game pool (tools/extract_base_game_pool.py ->
# tools/build_ironclad_sheet.py). game_ref/ is gitignored (.gitignore:28):
# decompiled material is REFERENCE ONLY, so this is a regenerable LOCAL
# artifact that is simply absent on a fresh clone.
#
# Absence is TOTAL and that is the design, not an accident: the cards live
# here AND so does the character yaml (char_*.yaml below). Committing a
# character whose starting_deck ids ship in a gitignored file would leave
# `build_player("real_ironclad")` a KeyError on every fresh clone -- a
# committed reference to a missing thing. Nothing in the repo names
# real_ironclad except inert guards (tier05.rewards.NO_COMPANION_CHARACTERS)
# and a skip-guarded test module.
GAME_REF_DIR = local_reference.game_ref_dir()
EXTERNAL_CARD_SHEETS = {"ironclad_pool.yaml": "real_ironclad",
                        "silent_pool.yaml": "real_silent"}
# The REQUIRED reviewed layers behind each merged pool. These must agree
# with tools/build_official_sheet.CHARACTERS; test_real_ironclad and
# test_real_silent pin that they do, because a layer listed in one place
# and not the other is a pool that loads at the wrong size.
EXTERNAL_CARD_LAYERS = {
    "ironclad_pool.yaml": (
        "ironclad_pool_pass4.yaml",
        "ironclad_pool_pass5.yaml",
        "ironclad_pool_pass6.yaml",
    ),
    "silent_pool.yaml": (
        "silent_pool_pass1.yaml",
        "silent_pool_pass2.yaml",
        "silent_pool_pass3.yaml",
        "silent_pool_pass4.yaml",
        "silent_pool_pass5.yaml",
        "silent_pool_pass6.yaml",
        "silent_pool_pass7.yaml",
    ),
}


class MissingReferenceLayer(RuntimeError):
    """A `real_*` arm was asked for and its `game_ref/` layer is not here.

    BACKLOG `EB-128` (4). Until this existed, a lost `game_ref/` announced
    itself in one of two structurally-invisible ways: an experiment naming a
    `real_*` arm discovered the loss by traceback halfway through a cell (an
    empty pool, then a failure downstream that names neither the tree nor the
    fix), and the test suite's only tell was a SILENT SKIP-COUNT JUMP. Both
    are the shape this repo keeps calling out -- a narrower run reporting
    itself in the same shape as a full one.

    The class is separate from `ValueError` so a caller that wants to say
    "this arm is unavailable, here is the table without it" can catch exactly
    this and nothing else.
    """


# The character -> merged sheet each `real_*` arm loads out of `game_ref/`.
# Derived from EXTERNAL_CARD_SHEETS rather than retyped: the two must not be
# able to disagree about which sheet backs which arm.
REFERENCE_LAYER_SHEETS = {char: sheet
                          for sheet, char in EXTERNAL_CARD_SHEETS.items()}


def require_reference_layer(character: str) -> None:
    """Fail LOUDLY and EARLY if this character's `game_ref/` layer is gone.

    A no-op for every character that does not read `game_ref/` -- the roster,
    both `ref_*` anchors, anything unknown -- so it is safe to call from the
    one door every tier-0.5 arm goes through (`tier05.runner.resolve_plan`,
    R68), which is where it is called from.

    **STANDING RULE, and it is the row's: DO NOT fabricate, stub or
    approximate a missing layer to make an anchor load.** A stubbed
    `real_ironclad` produces numbers that look like floors and are not, which
    is worse than the absence. This function's only job is to turn the absence
    into a sentence naming the restore point.
    """
    sheet = REFERENCE_LAYER_SHEETS.get(character)
    if sheet is None:
        return
    missing = [name for name in (sheet, *EXTERNAL_CARD_LAYERS.get(sheet, ()))
               if not (GAME_REF_DIR / name).exists()]
    if not missing:
        return
    where = ("the directory does not exist" if not GAME_REF_DIR.exists()
             else "the directory exists but is missing")
    raise MissingReferenceLayer(
        f"{character!r} needs the local `game_ref/` reference layer and "
        f"{where}: {', '.join(missing)} (looked in {GAME_REF_DIR}).\n"
        f"  `game_ref/` is gitignored decompile-derived material, so it is "
        f"absent on a fresh clone and in EVERY worktree by construction, and "
        f"git history cannot restore it.\n"
        f"  RESTORE POINT: the OneDrive vault, via "
        f"`python -m tools.backup_game_ref` (its docstring names the vault "
        f"path and the wipe guard); `tools/lint_game_ref_backup.py` says "
        f"whether that mirror is current. A rebuild from the game instead "
        f"runs tools/extract_base_game_pool.py then "
        f"tools/build_official_sheet.py -- and note that `--verify` is a "
        f"CONSISTENCY check, not a currency one, so a restore from a backup "
        f"older than the last field retirement can verify and still not "
        f"load.\n"
        f"  DO NOT stub, fabricate or approximate this layer to make the arm "
        f"run. A stubbed anchor produces numbers that look like floors and "
        f"are not (BACKLOG EB-128).")


# The two hand-approximated reference characters own the cards/ sheets.
# Same sheet-name convention as DOCS_CARD_SHEETS: ownership is a property
# of the pool a card ships in, not a field repeated on every row.
#
# This tagging is what makes the rewards.character_pool ownership filter
# work. Before it, these rows had character=None and the filter only
# dropped cards belonging to SOMEONE ELSE -- so cards belonging to NOBODY
# were offered to everybody, and ~12% of Klee's reward screens were
# Ironclad/Silent stand-ins. tokens.yaml stays untagged on purpose:
# generated tokens are genuinely shared and are excluded from draft pools
# by rarity, not by ownership.
REF_CARD_SHEETS = {"ironclad_starter.yaml": "ref_ironclad",
                   "ironclad_package.yaml": "ref_ironclad",
                   "silent.yaml": "ref_silent"}


def _load_yaml_dir(sub: str, owners: dict[str, str] | None = None
                   ) -> list[dict]:
    docs = []
    for path in sorted((CONTENT_DIR / sub).glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        rows = data if isinstance(data, list) else [data]
        owner = (owners or {}).get(path.name)
        if owner:
            for d in rows:
                # DRAFTABLE RARITIES ONLY. Basics/tokens/statuses stay
                # deliberately ownerless: rewards.character_pool already
                # excludes them by rarity, so tagging buys nothing there --
                # while `character` is ALSO Furina's Spotlight key
                # (combat.py:92, effects.py:127/459/578). Engine test states
                # use strike/defend as filler, and tagging those would make
                # them valid Spotlight targets, changing a shared path for a
                # draft-layer fix. test_fontaine.test_character_field_
                # derivation locks that invariant.
                if d.get("rarity") in C.RARITY_ODDS:
                    d.setdefault("character", owner)
        docs.extend(rows)
    return docs


def _is_reaction_fuel(card: Card) -> bool:
    """Does this companion feed or amplify the reaction system?

    DERIVED, not written per-row in the sheet, and that is the design decision
    rather than an implementation shortcut. Companions carried NO archetype tag
    at all, while tier05's adaptive scorer handed them a bonus scaled by
    reaction's share -- a share they could never raise, because untagged cards
    are invisible to `archetype_shares`. Reaction could not bootstrap through
    its own enablers.

    Deriving from effects keeps the tag from drifting away from what the card
    does. The rule is: a companion is reaction fuel iff it applies an element,
    places an aura, swirls (swirl IS a reaction), amplifies reactions, keys
    off existing auras (`consumes_aura` -- Albedo's Crystallize engine reads
    them, a reaction payoff), or summons something that applies an element
    (`summon_element` -- Oz).

    The last two fields exist because of this function (M7 ruling R4): both
    cards read as reaction cards to a human, but the only evidence was a
    prose `note`, and inferring intent from prose is exactly the drift this
    avoids. The sheet now says it structurally, so the tag can be honest.
    (The engine's oz_summon tick hardcodes electro; test_m6 pins the sheet
    field to that literal so the two cannot drift apart silently.)
    """
    for fx in card.effects:
        if fx.get("applies_element"):
            return True
        if fx.get("op") in ("apply_aura", "swirl"):
            return True
        if fx.get("consumes_aura") or fx.get("summon_element"):
            return True
        if (fx.get("op") == "apply_power"
                and fx.get("power") in C.AMP_PAYOFF_POWERS):
            return True
    return False


def _external_cards() -> list[dict]:
    """Rows from the gitignored game_ref/ reference sheets, if present.

    Deliberately NOT the docs/ path's post-processing: no nation inference
    (a base-game pool has no Teyvat nation), and `character` is FORCED
    rather than `setdefault`-ed. That force is load-bearing, not cosmetic:
    rewards.character_pool drops cards tagged with another character
    (rewards.py:48), so without it every Klee reward screen could offer a
    Bash -- and every Ironclad screen a Jumpy Dumpty.
    """
    raw: list[dict] = []
    for sheet, char in EXTERNAL_CARD_SHEETS.items():
        path = GAME_REF_DIR / sheet
        if not path.exists():
            continue          # fresh clone: the reference simply is not here
        docs = yaml.safe_load(path.read_text(encoding="utf-8")) or []
        for d in docs:
            d["character"] = char
        pool_ids = {d["id"] for d in docs}
        for layer_name in EXTERNAL_CARD_LAYERS.get(sheet, ()):
            layer_path = GAME_REF_DIR / layer_name
            if not layer_path.exists():
                raise ValueError(
                    f"{sheet}: missing required local layer {layer_name}; "
                    "rebuild/restore game_ref before loading real_ironclad")
            layer = yaml.safe_load(layer_path.read_text(encoding="utf-8")) or []
            layer_ids = {d["id"] for d in layer}
            stale = sorted(layer_ids - pool_ids)
            if stale:
                raise ValueError(
                    f"{sheet}: stale merged pool is missing {layer_name} "
                    f"cards {stale}; run build_ironclad_sheet.py")
        # A partial external upgrade population biases both combat (Armaments,
        # Aggression) and run decisions (smithing versus removal). Treat the
        # external reference as one atomic artifact: either every row resolves
        # through the shared `<id>+` path, or real_ironclad does not load.
        missing_upgrades = sorted(
            d["id"] for d in docs if not upgrades.has_upgrade(d["id"])
        )
        if missing_upgrades:
            raise ValueError(
                f"{sheet}: incomplete external upgrade coverage for "
                f"{missing_upgrades}; rebuild game_ref with "
                "extract_base_game_pool.py --emit-sheet before loading "
                "real_ironclad")
        raw.extend(docs)
    return raw


@lru_cache(maxsize=1)
def _card_index() -> dict[str, Card]:
    raw = _load_yaml_dir("cards", REF_CARD_SHEETS)
    for sheet in DOCS_CARD_SHEETS:
        path = DOCS_DIR / sheet
        if path.exists():
            docs = yaml.safe_load(path.read_text(encoding="utf-8"))
            # R20 (2026-07-20): *-upgrades.yaml sheets are the ONE upgrade
            # convention. Inline `upgrade:` fields are IGNORED by Tier 0,
            # and silently ignoring them risks an inline-only upgrade that
            # never applies -- so the tolerance is loud, not silent.
            # UserWarning on purpose: DeprecationWarning is filtered out
            # of non-__main__ code by default, which would be silence.
            inline = [d["id"] for d in docs if "upgrade" in d]
            if inline:
                warnings.warn(
                    f"{sheet}: DEPRECATED inline `upgrade:` fields on "
                    f"{inline} (R20, 2026-07-20). Upgrades live in the "
                    "*-upgrades.yaml sheets; these fields are IGNORED "
                    "and must be reverted to the upgrade sheet.")
            # Nation comes from the sheet name ("mondstadt-companions.yaml"),
            # not a per-card field: it is a property of the pool a card ships
            # in, and repeating it on every row is just drift waiting to
            # happen. This is what makes the v1.8 banner roll per-nation
            # without touching the sheets when Liyue lands.
            if sheet.endswith("-companions.yaml"):
                nation = sheet.split("-", 1)[0]
                for d in docs:
                    d.setdefault("nation", nation)
                    # character derives from the id prefix ("fischl_oz" ->
                    # fischl): same drift argument as nation-from-filename.
                    # Explicit field wins (Guest Star rows name their cameo
                    # because their ids are prefixed "guest_").
                    d.setdefault("character", d["id"].split("_", 1)[0])
            elif sheet.endswith("-cards.yaml"):
                # Personal sheets: every row belongs to the character in the
                # filename. This is what makes self-Spotlight legible.
                char = sheet[:-len("-cards.yaml")]
                for d in docs:
                    d.setdefault("character", char)
            raw.extend(docs)
    raw.extend(_external_cards())
    cards = [Card.from_dict(d) for d in raw]
    for c in cards:
        if c.role_c and "companion" not in c.tags:   # sheet marks via role_c
            c.tags.append("companion")
        if c.is_companion and _is_reaction_fuel(c):
            if "reaction" not in c.archetypes:
                c.archetypes.append("reaction")
    index = {c.id: c for c in cards}
    if len(index) != len(cards):
        seen: set[str] = set()
        dupes = {c.id for c in cards if c.id in seen or seen.add(c.id)}
        raise ValueError(f"duplicate card ids: {sorted(dupes)}")
    for c in cards:
        _validate_card_shape(c)
    return index


def _validate_card_shape(c: Card) -> None:
    """The three post-construction checks every loaded card passes.

    Factored out when the prototype surface landed (EB-147): a quarantined
    row is checked by exactly the code the shipped rows are checked by, or
    "still checked for schema validity" (R213 B) is a claim about a second
    implementation that will drift.
    """
    _validate_effect_vocabulary(c.id, c.effects)
    # EB-71 (R174): a Sly rider is printed effects too, and was the one
    # effect list nothing validated -- a typo in it loaded clean and
    # raised the first time a card effect discarded the row. The
    # base-game auto-play marker is not an op and is filtered out by
    # `sly_riders` before the check, so an extracted keyword row still
    # loads (see state.Card.sly).
    _validate_effect_vocabulary(c.id, sly_riders(c))
    _validate_recall_shape(c)


def prototype_cards(sheet: Path | None = None) -> list[Card]:
    """The quarantined prototype rows (R213 B), schema-checked and NOT pooled.

    This is the ONLY reader of `PROTOTYPE_SHEET` in tier0, and nothing in the
    engine, the pilot, the run templates or tier05 calls it. `get_card`,
    `all_cards`, `character_pool` and every reward roll go through
    `_card_index`, which this function does not touch and does not populate:
    that is the quarantine, and it is structural rather than a filter.

    What it DOES do is prove the row is legal:

      * `Card.from_dict` is total on both sides (unknown field -> ValueError,
        retired field -> a named ValueError), so the sheet schema is enforced;
      * `_validate_card_shape` runs the same effect-vocabulary and recall-shape
        checks the shipped index runs;
      * ids must carry `PROTOTYPE_ID_PREFIX` and must not collide with a
        shipped card id, because a duplicate id is a duplicate ModelId in the
        mod and an ambiguous `give_card` on the wire;
      * `character:` is REQUIRED and must name a real roster character. One
        surface carries every character's prototypes (R213 B: "rows carry
        which character they belong to"), and the codegen picks the owner's
        element cadence and art loader off this field -- a row without it has
        no cadence, which is a wrong card rather than a missing one.

    `sheet` is for the tests: they point it at a temporary fixture so the
    SHIPPED surface can stay empty, which is the R213 deletion rule's steady
    state. Production callers pass nothing.
    """
    path = sheet or PROTOTYPE_SHEET
    if not path.exists():
        return []
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    shipped = _card_index()
    known_characters = {"klee", "furina", "kokomi"}
    seen: set[str] = set()
    cards: list[Card] = []
    for d in raw:
        card_id = d.get("id")
        if not isinstance(card_id, str) or not card_id.startswith(
                PROTOTYPE_ID_PREFIX):
            raise ValueError(
                f"{path.name}: prototype id {card_id!r} must start "
                f"{PROTOTYPE_ID_PREFIX!r} -- see PROTOTYPE_ID_PREFIX")
        if card_id in shipped:
            raise ValueError(
                f"{path.name}: prototype id {card_id!r} collides with a "
                "shipped card; two cards cannot share one ModelId")
        if card_id in seen:
            raise ValueError(f"{path.name}: duplicate prototype id {card_id!r}")
        seen.add(card_id)
        character = d.get("character")
        if character not in known_characters:
            raise ValueError(
                f"{path.name}: prototype {card_id!r} must declare "
                f"`character:` as one of {sorted(known_characters)}, "
                f"got {character!r}")
        # EB-190: `authored_by:` is PROVENANCE, not card schema -- which model
        # families wrote the row. `Card.from_dict` is total on unknown fields
        # by design, so the field is removed here rather than added to `Card`:
        # a card object carrying an author list would put the fact inside the
        # engine, where nothing may ever read it. `understudy/authorship.py`
        # is the one reader, and `tools/gen_prototype_cards.py` refuses a row
        # that omits it.
        card = Card.from_dict({k: v for k, v in d.items()
                               if k != "authored_by"})
        _validate_card_shape(card)
        cards.append(card)
    return cards


@lru_cache(maxsize=1)
def _prototype_index() -> dict[str, Card]:
    """`{id: Card}` for the surface, memoized like `_card_index` is.

    A SECOND index, deliberately, and never merged into the first: merging is
    exactly what would put a prototype into `all_cards`, `character_pool` and
    every reward roll. `_card_prototype` consults this one only behind
    `C.SPARK_ALT_COST_ENABLED` and only for a `proto_`-prefixed id.
    """
    return {c.id: c for c in prototype_cards()}


def _validate_recall_shape(card: Card) -> None:
    """EB-118 §6.4 constraints 1 and 2, AT LOAD.

    A card that retrieves from the exhaust pile must be Uncommon or Rare and
    must itself Exhaust. Both are card-SHAPE law, so they are enforced where
    the loader already enforces shape rather than left to sheet-author
    discipline: the runtime pool filters (constraints 3-6) cannot see rarity
    or the printed keyword, and a Common permanent retriever is exactly the
    version of this capability the packet refuses.
    `tools/lint_recall_exhaust.py` is the same law swept over the sheets,
    including rows no run happens to load.
    """
    from tier0.engine import effects as _effects        # late: cycle

    if not _effects.retrieves_from_exhaust(card):
        return
    if card.rarity not in ("uncommon", "rare"):
        raise ValueError(
            f"card {card.id!r}: retrieval from the exhaust pile is "
            f"Uncommon-or-Rare only (EB-118 §6.4 constraint 1); this row is "
            f"{card.rarity!r}")
    if not card.exhaust:
        raise ValueError(
            f"card {card.id!r}: a card that retrieves from the exhaust pile "
            f"must itself Exhaust (EB-118 §6.4 constraint 2); this row has "
            f"no `exhaust: true`")


def _validate_effect_vocabulary(card_id: str, effects: list[dict]) -> None:
    """Every `op:` is in OPS and every `if:` is a real predicate. AT LOAD.

    Audit sec.5 ("content-boundary validation is inverted"): the loader validated
    FIELDS and never NAMES, so a misspelled op or predicate loaded clean and
    raised the first time the card resolved. For a rare that is in front of a
    player, not in a test -- and on the co-op seat there is no sim backstop at
    all.

    Both raises already existed in `effects._resolve_effects` and
    `effects._predicate`; this moves them from play time to load time. Content
    that was valid stays valid and nothing about resolution changes -- the only
    behaviour that moves is *when* a typo is reported, which is the whole point.

    Recurses through `then`/`else` branches and through `choose_one`'s
    `modes:` bodies: both nest, and an unreachable-today branch is exactly
    where a typo survives longest.

    EB-135: `count:` is checked here too, and it is the one grammar this
    function existed for that it did not cover. `op:` went through
    `effects.OPS` and `if:` through `is_known_predicate`, and then it stopped
    — while `_calc_amount` resolved `formula["count"]` through
    `_runtime_count`, which raises `unknown runtime count` the first time the
    card RESOLVES. That is verbatim the failure the paragraph above says this
    check was written to end. The same door is reached by a string-valued
    `amount:` and by a string-valued `times:` (both go through `_amount`,
    whose last arm IS the count vocabulary), and by a dict `times_formula:`
    (the same `_calc_amount`), so all four are checked against the same
    registry rather than one of them.

    One AMOUNT is checked here as well, for the same when-is-it-reported
    reason: a non-positive `gain_encore` (EB-119). It is not a vocabulary
    error, but it is a cross-engine one, and the recursion above is already
    the only walk that reaches every nested body on every sheet.
    """
    from tier0.engine import effects as _effects        # late: cycle

    for fx in effects:
        op = fx.get("op")
        if op not in _effects.OPS:
            raise ValueError(
                f"card {card_id!r}: unknown op {op!r} "
                f"(not in effects.OPS)")
        if op == "conditional":
            name = fx.get("if")
            if not _effects.is_known_predicate(name):
                raise ValueError(
                    f"card {card_id!r}: unknown predicate {name!r}")
        _validate_count_vocabulary(card_id, fx)
        if op == "gain_encore" and isinstance(fx.get("amount"), int) \
                and fx["amount"] <= 0:
            # EB-119. A negative GAIN is not a spend, and it is the exact
            # shape a spend gets smuggled in as. It is also silently INERT in
            # the mod -- FurinaResources.GainEncore opens `if (amount <= 0)
            # return;` -- so a row written this way moves the sim's meter and
            # does nothing in game. The overdraw primitive is `spend_encore`;
            # the no-overdraw price is the `encore_cost` field. Refused here
            # because a non-positive amount has no honest reading at all.
            raise ValueError(
                f"card {card_id!r}: gain_encore amount must be positive, got "
                f"{fx['amount']} -- a negative gain is not a spend; use "
                f"spend_encore (the overdraw primitive) or the encore_cost "
                f"field")
        if op == _effects.BLOCK_AT_TURN_START:
            # EB-83. The DURATION is a literal positive int and the engine
            # raises on anything else; checked HERE for this function's whole
            # stated reason -- at load, once, rather than the first time a card
            # already in front of a player resolves. Same door as the
            # gain_encore amount above: not a vocabulary error, but a
            # printed-text error only the resolver could otherwise see.
            try:
                _effects.block_at_turn_start_turns(fx)
            except ValueError as exc:
                raise ValueError(f"card {card_id!r}: {exc}") from exc
        if op == "choose_one":
            _validate_modal_shape(card_id, fx)
            for mode in fx[_effects.MODES_KEY]:
                _validate_effect_vocabulary(card_id, mode["effects"])
        for branch in ("then", "else"):
            if fx.get(branch):
                _validate_effect_vocabulary(card_id, fx[branch])


def _validate_count_vocabulary(card_id: str, fx: dict) -> None:
    """Every runtime-count token on ONE effect, checked AT LOAD (EB-135).

    Four spellings reach `effects._runtime_count`, and a typo in any of them
    raised only at RESOLVE before this existed:

      `amount_formula: {count: <token>}`   -> `_calc_amount`
      `times_formula:  {count: <token>}`   -> `_calc_amount`, same door
      `amount: "<token>"`                  -> `_amount`'s last arm
      `times:  "<token>"`                  -> `_amount`, same arm

    Split out of `_validate_effect_vocabulary` rather than inlined because it
    is per-EFFECT and op-agnostic: any op may carry a formula, and a check
    that lived inside one op's branch is exactly the shape of the defect
    `EB-132` fixed one file over.

    Deliberately NOT checked here: `bonus_formula`. It is a different grammar
    (`N_per_<thing>` / `N_per_M_<resource>`), not a count token, with its own
    raise in `_bonus_formula`; folding it in would mean a second hand-written
    vocabulary mirroring a second chain, and this row's whole argument is
    that a mirrored vocabulary is only safe when something pins it to its
    chain. It is recorded as the next honest step, not silently skipped.
    """
    from tier0.engine import effects as _effects        # late: cycle

    op = fx.get("op")
    for key in ("amount_formula", "times_formula"):
        formula = fx.get(key)
        if not isinstance(formula, dict):
            continue
        if key == "amount_formula" and op in _effects.POWER_FORMULA_OPS:
            # The OTHER grammar wearing this key: `{target_power: <name>}`,
            # resolved by `_power_amount_formula`. The power name is
            # deliberately open (any power a card reads), so what is checked
            # is that the key is there at all -- which is exactly what that
            # function raises on.
            if "target_power" not in formula:
                raise ValueError(
                    f"card {card_id!r}: apply_power amount_formula "
                    f"{formula!r} names no `target_power` -- "
                    f"effects._power_amount_formula would raise the first "
                    f"time it resolved")
            continue
        token = formula.get("count")
        if not _effects.is_known_count(token):
            raise ValueError(
                f"card {card_id!r}: unknown runtime count {token!r} in "
                f"{key} (op {op!r}) -- not resolvable by "
                f"effects._runtime_count, so this card would raise the first "
                f"time it resolved")
    for key in ("amount", "times"):
        val = fx.get(key)
        if not isinstance(val, str):
            continue
        if key == "amount" and val == "all" and op in _effects.AMOUNT_ALL_OPS:
            continue                    # the op reads it itself; see the set
        if not _effects.is_known_amount(val):
            raise ValueError(
                f"card {card_id!r}: unknown runtime count {val!r} in "
                f"{key} (op {op!r}) -- not resolvable by "
                f"effects._amount, so this card would raise the first time "
                f"it resolved")


def _validate_modal_shape(card_id: str, fx: dict) -> None:
    """The `choose_one` shape, checked AT LOAD (EB-118 sec.5.4).

    A modal is the one op whose payload is a list of DICTS rather than a list
    of effects, so it is also the one op a typo can hide in without tripping
    the op check above: `{effect: [...]}` for `{effects: [...]}` would load
    clean and resolve as an empty mode. Hence an exact key set at both
    levels, the same discipline `Card.from_dict` applies to a card row.

    Two modes is a floor, not a style rule. One mode is not a choice -- it is
    a conditional with the predicate left out -- and a card that offers the
    player a single option is a sheet defect, not a design.
    """
    from tier0.engine import effects as _effects        # late: cycle

    unknown = set(fx) - _effects.MODAL_FIELDS
    if unknown:
        raise ValueError(
            f"card {card_id!r}: unknown modal fields {sorted(unknown)}")
    modes = fx.get(_effects.MODES_KEY)
    if not isinstance(modes, list):
        raise ValueError(
            f"card {card_id!r}: choose_one needs a `modes:` list")
    if len(modes) < _effects.MIN_MODES:
        raise ValueError(
            f"card {card_id!r}: choose_one needs at least "
            f"{_effects.MIN_MODES} modes, got {len(modes)}")
    for i, mode in enumerate(modes):
        if not isinstance(mode, dict):
            raise ValueError(
                f"card {card_id!r}: mode {i} is not a mapping")
        unknown = set(mode) - _effects.MODE_FIELDS
        if unknown:
            raise ValueError(
                f"card {card_id!r}: mode {i} has unknown mode keys "
                f"{sorted(unknown)}")
        if not isinstance(mode.get("label"), str) or not mode["label"]:
            raise ValueError(
                f"card {card_id!r}: mode {i} needs a non-empty `label:` "
                f"-- the label IS that mode's printed card text")
        if not isinstance(mode.get("effects"), list) or not mode["effects"]:
            raise ValueError(
                f"card {card_id!r}: mode {i} needs a non-empty `effects:` "
                f"list")


def guest_star_generation_pool(rarity: str) -> list[Card]:
    """Guest Star generation pool (kickoff §9, guardrails c+d): shared
    companions plus the purpose-built Guest Star set, at EXACTLY the
    generator's rarity. 5-star shared Rares are unreachable from sub-Rare
    generators because their rarity is 'rare' (the equal-rarity clause is the
    banner's bodyguard).

    personal_pool rows are excluded by an EXPLICIT predicate, honored HERE so
    no pool source can forget it (the same reason the character generation
    pool re-checks `generatable`). The docstring used to claim they were
    absent "by construction", and that was false for a row that is a
    companion AND personal: prune_witch_hunt is a shared-companion uncommon
    with PersonalPool "klee", so The Guest List and Command Performance could
    mint a Klee kit card on Furina. LAW.md:98-110 makes personal-pool
    companions the character's kit, distinct from generated Guest Star
    cameos; rewards, the shop and the mod's own IsOfferable all filter, and
    this was the sole consumer that skipped it (EB-99)."""
    pool = [c for c in _card_index().values()
            if (c.is_companion or c.guest_star)
            and c.rarity == rarity and not c.kit_card
            and c.personal_pool is None]
    if not pool:
        raise ValueError(f"empty guest-star pool at rarity {rarity!r}")
    return sorted(pool, key=lambda c: c.id)


def companion_pool(nation: str) -> list[Card]:
    """The conscript op's generation pool (Kokomi kickoff §2.3): every
    ordinary shared Companion of the nation, ALL draftable rarities — the
    5-star Rare jackpot (Itto) is deliberately in the deck of outcomes;
    conscription pays card identity for a random recruit, and the rare
    hit is the verb's advertised dream. Guest Stars are excluded (they are
    a Furina personal-pool mechanism, kickoff §2.3 differentiation) and so
    are kit cards, as everywhere.

    personal_pool rows are excluded by the same explicit predicate the Guest
    Star pool carries, for the same reason (EB-99). Unreachable today only
    because conscript rows default to Inazuma and the personal-pool companion
    that exists is Klee's; the filter is stated rather than inherited from
    that accident."""
    pool = [c for c in _card_index().values()
            if c.is_companion and c.nation == nation
            and not c.guest_star and not c.kit_card
            and c.personal_pool is None
            and c.rarity in C.RARITY_ODDS]
    if not pool:
        raise ValueError(f"empty companion pool for nation {nation!r}")
    return sorted(pool, key=lambda c: c.id)


def cards_in_pool(pool: str) -> list[Card]:
    """Named draft pools for add_card (e.g. Secret Stash's
    'demolition_commons')."""
    archetype, _, rarity = pool.rpartition("_")
    rarity = rarity.rstrip("s")                      # commons -> common
    cards = [c for c in _card_index().values()
             if rarity == c.rarity and archetype in c.archetypes
             and not c.kit_card]              # kit is never draftable (v1.9)
    if not cards:
        raise ValueError(f"empty card pool {pool!r}")
    return cards


@lru_cache(maxsize=None)
def _card_prototype(card_id: str) -> Card:
    """The shared, never-handed-out template for a card id, upgrades applied.

    Building the upgraded form used to run on EVERY `get_card("x+")` call;
    it is a pure function of the id, so it is memoized here and only the
    cheap per-caller copy remains. Cleared with the card index (`reload`).
    """
    plain, ench, amount = enchantments.split(card_id)
    if plain.endswith(upgrades.SUFFIX):
        base_id = plain[:-len(upgrades.SUFFIX)]
        index = _card_index()
        # EB-213: the upgraded form of a SUBSTITUTED prototype resolves the
        # way its plain form does -- the shipped index first, the substitution
        # table only on a miss. The surface now carries its own `upgrade:`
        # deltas (`upgrades._prototype_deltas`), so `has_upgrade` is true of
        # such a row and the campfire will ask for `<proto id>+`; before this
        # it asked and got a KeyError, which is why the row was base-only.
        base = copy.deepcopy(index[base_id] if base_id in index
                             else _substituted_card_index()[base_id])
        card = upgrades.apply_upgrade(base)
    elif (C.SPARK_ALT_COST_ENABLED
            and plain.startswith(PROTOTYPE_ID_PREFIX)):
        # THE ONE DOOR THE SPARK ARM OPENS INTO THE QUARANTINE, and it is
        # exactly as wide as it has to be. `_starter_ids` substitutes two
        # PROTO ids into Klee's starting deck (PICK 1, options 1+5), and a
        # starting deck is a list of id STRINGS that both `build_player` and
        # `build_player_from_ids` resolve through here -- so without this
        # branch the substitution is a KeyError rather than a card.
        #
        # THREE GUARDS, ALL NECESSARY, none of them a filter somebody has to
        # remember: the flag must be ON (with it off this branch does not
        # exist and every shipped path is byte-identical), the id must carry
        # `proto_`, and the row must be on the surface. `_card_index` is
        # still not populated with prototypes, so pools, rewards, drafts and
        # digests remain structurally unable to see them -- the quarantine
        # that matters is membership, and membership does not move here.
        card = _prototype_index()[plain]
    else:
        index = _card_index()
        # The substituted-prototype table is consulted ONLY on a miss, and
        # only on the plain (un-upgraded) branch: a prototype has no upgrade
        # row, so `<proto id>+` correctly falls through to `apply_upgrade`'s
        # "no applicable upgrade". See `_substituted_card_index` for why the
        # table exists and why it does not weaken the R213 quarantine.
        card = (index[plain] if plain in index
                else _substituted_card_index()[plain])
    if ench is None:
        return card
    # R82 reopened: the enchantment is the OUTER decoration, applied to the
    # already-upgraded form, so the two are independent and either order of
    # acquisition lands on the same card. `card` may be the shared index
    # prototype here, hence the copy.
    card = copy.deepcopy(card)
    enchantments.apply(card, ench, amount)
    card.id = card_id
    card.name = f"{card.name} ({enchantments.CATALOG[ench].label})"
    return card


def get_card(card_id: str) -> Card:
    """`<id>+` returns the upgraded form (M7) -- deck lists stay strings.

    Always a FRESH copy: combat mutates card instances (Rampage's
    grow_damage, Armaments' in-place upgrade), so callers must never share
    one. Read-only callers that only score a deck should use `peek_card`.
    """
    return copy.deepcopy(_card_prototype(card_id))


def peek_card(card_id: str) -> Card:
    """The SHARED prototype for a card id -- do not mutate the result.

    The run layer re-derives `[get_card(cid) for cid in deck_ids]` several
    times per reward screen purely to score the deck (draft policy, core
    completion, rest/shop plans, regret). Those paths only read fields, and
    the copies they forced were ~70% of all card copying in a run. This is
    the read-only door; anything that plays, upgrades or otherwise mutates a
    card must go through `get_card`.
    """
    return _card_prototype(card_id)


@lru_cache(maxsize=1)
def _character_index() -> dict[str, dict]:
    index = {d["id"]: d for d in _load_yaml_dir("characters")}
    # Reference characters live beside their (gitignored) card sheet -- see
    # GAME_REF_DIR. glob() on a missing directory yields nothing, so no
    # exists() guard is needed; the `char_` prefix keeps this from ever
    # picking up ironclad.json's siblings.
    for path in sorted(GAME_REF_DIR.glob("char_*.yaml")):
        d = yaml.safe_load(path.read_text(encoding="utf-8"))
        index[d["id"]] = d
    return index


def _kit_cards(spec: dict) -> list[Card]:
    """v1.9: the character's kit Bursts, attached to the Player rather than
    shuffled into any deck. The character yaml names them (`kit:`) and the
    card sheet marks them (`kit_card: true`); requiring both to agree is the
    cross-check -- a card in a kit list that the sheet does not mark would
    silently dodge the pool exclusion, so it is a loud error instead."""
    kit = []
    for cid in spec.get("kit", []):
        card = get_card(cid)
        if not card.kit_card:
            raise ValueError(
                f"{spec['id']}: kit lists {cid!r} but the sheet does not "
                f"mark it kit_card")
        kit.append(card)
    return kit


def _starting_relic_effects(spec: dict) -> list[dict]:
    """The character's OWN starting relic, as engine/relics.py hook dicts.

    `relic_hooks` (a list of bare strings) cannot carry an amount, which is
    fine for Burning Blood's `heal_after_won_fight` but not for a relic with
    a number on it. Ring of the Snake -- ask A1, ruled 2026-07-27: wire it --
    is `combat_start_draw: 2`, verified from the character model
    (`ModifyHandDraw` returns `count + 2` and then `if (TurnNumber > 1)
    return count`, i.e. the FIRST TURN ONLY, which is exactly what tier0's
    `combat_start_draw` already means).

    This is the one place a character's intrinsic relic effects enter, so
    the battery (build_player) and the run layer (build_player_from_ids)
    cannot disagree about whether she has her relic. It does mean the
    battery is no longer categorically relic-free -- but only for a
    character whose yaml declares the field, and no roster character does:
    a relic on the roster is a DRAFTED relic and stays the run layer's job.
    Deep-copied because the engine may rewrite conditional effects in place.
    """
    return copy.deepcopy(list(spec.get("starting_relic_effects", [])))


def _starter_ids(spec: dict) -> list[str]:
    """The printed starting deck, with the quarantined starter substitutions
    the two live prototype arms make. Each arm is flagged, each applies only
    to its own character, and with both flags off this returns
    `list(spec["starting_deck"])` and nothing else -- the acceptance condition
    on both flags.

    THE SEAM IS HERE, IN CODE, AND NO PRINTED SHEET MOVES. Both readers of a
    printed starter go through this function -- `build_player` (the tier 0
    battery) and `starting_deck` (the tier 0.5 run) -- so the battery and the
    run cannot disagree about what a character opens with. That is the same
    argument `_starting_relic_effects` above makes for her relic. There is ONE
    such function, not one per arm: two arms that each rewrote the starter
    behind their own entry point is exactly the disagreement this seam exists
    to prevent.

    KOKOMI -- the Kurage base kit (`C.KURAGE_MEMORY` + `C.KURAGE_ALWAYS_ON`),
    ONE substitution. [USER], 2026-08-29: "I think that we will want to make
    Bake-Kurage part of the base kit (always on) rather than a separate card.
    So yes, we could add one Muster card to the base deck to teach the
    pattern." Bake-Kurage leaves -- a card that summons what is always on the
    field is a card that does nothing -- and one Muster card takes the slot,
    so that RULE 1 (the card sacrificed to a Muster enters the memory at three
    times its cost) is printed in fight 1 instead of drafted. The deck size is
    unchanged at twelve.

    KLEE -- Sparks as an alternative cost (`C.SPARK_ALT_COST_ENABLED`), TWO
    substitutions. PICK 1 of the Sparks packet, options 1 and 5 together (the
    seat: "Options 1 and 5 together follow"). Regent's ten-card starter ships
    exactly one Spark generator (`Venerate`) and exactly one Spark sink
    (`FallingStar`, 0 energy / 2 stars), and [USER] asked to "match their
    generation pattern". Klee's ten ship neither. So:

      * `pop` -> `proto_pop_spark`    -- the Basic that MAKES. Same Bomb, plus
                                         one Spark. Divine Right's job (a
                                         non-dead turn one) done by a card the
                                         player chooses to play, which is
                                         D2's answer and the seat's reason for
                                         preferring option 1 to option 2.
      * `kaboom` -> `proto_kaboom_sink` -- the Basic that SPENDS. Same 7
                                         damage, 0 energy, Spend 1 Spark.
                                         `FallingStar`'s exact role.

    ONE COPY OF EACH, AND THE PACKET DOES NOT SAY WHICH. Klee's starter holds
    FOUR `kaboom`; the packet says only "`kaboom` becomes 0 energy / Spend 1
    Spark". Substituting one copy is what makes her opening ten match
    Regent's shape (one source, one sink); substituting all four would make
    four of ten opening cards unplayable on an empty bank, which is a
    different card game and not the one the packet priced. One copy is taken,
    it is the smaller change, and it goes back to [USER] as a real pick. The
    deck size is unchanged at ten, which is what keeps this a substitution
    rather than a starter rework.
    """
    ids = list(spec["starting_deck"])
    character = spec.get("id")

    if (character == "kokomi"
            and C.KURAGE_MEMORY and C.KURAGE_ALWAYS_ON):
        drop, add = C.KURAGE_MEMORY_STARTER_DROP, C.KURAGE_MEMORY_STARTER_ADD
        if drop not in ids:
            # Loud rather than silent: if the printed starter ever stops
            # carrying Bake-Kurage, this swap has become a no-op that nobody
            # would notice until a smoke ran and the Muster was missing.
            raise ValueError(
                f"kurage base kit: {drop!r} is not in the printed starter, so "
                f"the {add!r} substitution has nothing to replace")
        ids[ids.index(drop)] = add

    if character == "klee" and C.SPARK_ALT_COST_ENABLED:
        for drop, add in C.SPARK_ALT_STARTER_SUBS:
            if drop not in ids:
                raise ValueError(
                    f"klee: Spark starter substitution cannot replace missing "
                    f"card {drop!r}")
            ids[ids.index(drop)] = add      # ONE copy: `.index` is the first
    return ids


def _pool_substitutions(spec: dict) -> dict[str, str]:
    """{shipped id: prototype id} for the character's OFFERABLE pool, under
    the same quarantine flag `_starter_ids` above reads.

    THE SEAM IS HERE, in code, and the sheets do not move -- the same argument
    `_starter_ids` makes for the printed starter, made once more for the other
    half of what a run can be handed. `rewards.character_pool` is the single
    source of truth for "which ids can be offered to this character" (fight
    rewards, the shop, every event card screen and the tier 0.5 drafter all
    read it), so it is the one caller, and gating it there gates them all.

    WHAT THE SWAP IS, and why ([USER], 2026-08-29): "Why does the power print 5
    instead of 3, exactly?" Under `C.KURAGE_MEMORY` Kurage's Oath's ward is
    paid on a MEMORY PLAY (`effects.kurage_fire`) and the amount is read off
    the stacks the card applied. The staged row prints [USER]'s ruled 3; the
    SHIPPED `kurages_oath` prints 5 (7 upgraded) under a face that says "per
    Bake-Kurage play", and it is frozen. So with the flag on and no
    substitution, a flagged run that DRAFTED the shipped Oath paid 5 per
    memory play under text that cannot bind -- which is D4, a defect, not a
    balance question. The offer side is what this branch owns: under the flag
    the shipped id leaves the pool and the prototype takes its slot at the
    SAME rarity, so the only Oath a flagged run can be offered is the 3.

    THE SECOND ARM, KLEE, under `C.SPARK_ALT_COST_ENABLED`
    (`C.SPARK_ALT_POOL_SUBS`). `KLEESPARK-R1` sec.11.6 item 5 records the
    absence of this branch as a limitation of the round -- with no pool seam
    the drafter could never be OFFERED a priced Spark row, so the sim's P5/P6
    read a deck assembled by id from PICK 4's own map instead of a drafted
    one. The map here IS that map, one for one, at matching rarities. It is
    the same shape as Kokomi's above and it is gated the same way; the only
    difference is that Kokomi's swap fixes text that cannot bind and this one
    makes an arm REACHABLE, which is what a two-arm flag is for.

    With EITHER flag off this returns `{}` for that character, and with both
    off `{}` and nothing else, which is the acceptance condition on the flags:
    no substitution, no second index, and `_card_prototype` never leaves
    `_card_index`.
    """
    character = spec.get("id")
    if character == "kokomi" and C.KURAGE_MEMORY:
        return {C.KURAGE_MEMORY_POOL_DROP: C.KURAGE_MEMORY_POOL_ADD}
    if character == "klee" and C.SPARK_ALT_COST_ENABLED:
        return dict(C.SPARK_ALT_POOL_SUBS)
    return {}


def pool_substitutions(character_id: str) -> dict[str, str]:
    """`_pool_substitutions` by character id -- the tier 0.5 door, the way
    `starting_deck` is the door onto `_starter_ids`."""
    spec = _character_index().get(character_id)
    return _pool_substitutions(spec) if spec else {}


@lru_cache(maxsize=1)
def _substituted_card_index() -> dict[str, Card]:
    """Prototype rows that a LIVE substitution has put within a run's reach.

    THE R213 QUARANTINE IS UNCHANGED AND THIS IS WHY. `_card_index` still
    carries no prototype row, so `all_cards`, the roster digest, the balance
    reports, `card_distinctness_report`, the codegen and every version stamp
    still cannot see one -- that is the structural quarantine and it is not
    weakened here. This is a SECOND table, read by `_card_prototype` alone,
    holding ONLY the rows some `_pool_substitutions` names. It is empty on
    every flag-off tree, which is every shipped tree.

    It exists because a substitution that could not be resolved by id would be
    a hack: every offer surface picks a card out of the pool and then re-reads
    it through `loader.get_card(pick.id)`, and the run layer stores decks as
    id strings and re-derives them on every reward screen. An offered card
    whose id does not resolve is a run that dies on the next screen.

    THERE IS AN UPGRADED FORM SINCE `EB-213`, and it is keyed on the row.
    `docs/prototype-surface.yaml` rows may carry their own `upgrade:` block,
    merged into the delta index by `upgrades._prototype_deltas`, so
    `has_upgrade` answers for a substituted row and `_card_prototype`'s `+`
    branch resolves its base through this table. Before that the surface had
    no upgrade channel at all: `has_upgrade` was False, the campfire skipped
    every substituted row, and the substituted Kurage's Oath's ruled upgraded
    value existed only as prose on the row. A row that declares no `upgrade:`
    is still base-only, and is still skipped honestly.
    """
    targets = {proto
               for spec in _character_index().values()
               for proto in _pool_substitutions(spec).values()}
    if not targets:
        return {}
    index = {c.id: c for c in prototype_cards() if c.id in targets}
    missing = sorted(targets - set(index))
    if missing:
        # The R213 deletion rule takes rows OFF this surface when a slice is
        # accepted or rejected. A substitution left pointing at a deleted row
        # must say so here, not as a KeyError on someone's reward screen.
        raise ValueError(
            f"pool substitution names {missing}, which is not on "
            f"{PROTOTYPE_SHEET.name}; a substituted row cannot have left the "
            "surface while the flag still points at it")
    return index


def build_player(character_id: str, deck: str = "starter") -> Player:
    """deck: 'starter' or the name of a package list in the character yaml
    (e.g. 'archetype_package') appended to the starter deck."""
    spec = _character_index()[character_id]
    card_ids = _starter_ids(spec)
    hooks = list(spec.get("relic_hooks", []))
    if deck != "starter":
        card_ids += spec["packages"][deck]
        # R8: probe-only relic hooks (harness instrumentation, e.g. the
        # sustain_probe's exempt heal trickle). Never on 'starter', never
        # in Tier 0.5 runs (build_player_from_ids does not read this).
        hooks += spec.get("package_relic_hooks", {}).get(deck, [])
    return Player(hp=spec["hp"], max_hp=spec["hp"],
                  draw_pile=[get_card(cid) for cid in card_ids],
                  element=spec.get("element", "none"),
                  cadence=spec.get("cadence", "skill"),
                  burst_max=spec.get("burst_max", 0),
                  relic_hooks=hooks,
                  relic_effects=_starting_relic_effects(spec),
                  kit_cards=_kit_cards(spec),
                  character_id=spec["id"],
                  fanfare_cap=(state_mod.fanfare_cap_base_term(spec["hp"])
                               if spec.get("fanfare") else 0))


def build_player_from_ids(character_id: str, card_ids: list[str],
                          relic_effects: list[dict] | None = None,
                          potions: list[str] | None = None,
                          potion_slots: int = C.POTION_SLOTS,
                          node_kind: str = "") -> Player:
    """Tier 0.5: build a player around an arbitrary (drafted) deck list.

    ``relic_effects`` is the combat-side relic engine's seam (engine/relics.py):
    a list of dicts keyed by ``hook``. It defaults to None -> [], and the run
    layer (tier05/model) computes the effective per-fight list and passes it
    in. DRAFTED relics remain run-layer-only, so for every character whose
    yaml declares no ``starting_relic_effects`` the battery path is still
    byte-identical and every relic code path is still a dead branch there.
    A character who declares one (real_silent, ask A1) carries it on BOTH
    paths -- see _starting_relic_effects.

    ``potions`` is the combat-side potion engine's seam (engine/potions.py): a
    list of held potion-id strings, likewise defaulting to None -> [] so the
    battery stays byte-identical and every potion code path is a dead branch.
    ``potion_slots`` (Potion Belt raises it) and ``node_kind`` (elite/boss
    context for the offensive use-policy) are inert on the battery."""
    spec = _character_index()[character_id]
    return Player(hp=spec["hp"], max_hp=spec["hp"],
                  draw_pile=[get_card(cid) for cid in card_ids],
                  element=spec.get("element", "none"),
                  cadence=spec.get("cadence", "skill"),
                  burst_max=spec.get("burst_max", 0),
                  relic_hooks=list(spec.get("relic_hooks", [])),
                  # The character's own starting relic FIRST, then whatever
                  # the run drafted. Two relics with the same hook both
                  # apply (Ring of the Snake + Bag of Preparation is +4 on
                  # turn 1), which is the game's behaviour and the reason
                  # this concatenates rather than merges.
                  relic_effects=(_starting_relic_effects(spec)
                                 + list(relic_effects or [])),
                  potions=list(potions or []),
                  potion_slots=potion_slots,
                  node_kind=node_kind,
                  kit_cards=_kit_cards(spec),
                  character_id=spec["id"],
                  fanfare_cap=(state_mod.fanfare_cap_base_term(spec["hp"])
                               if spec.get("fanfare") else 0))


def starting_deck(character_id: str, rng=None) -> list[str]:
    """Return the printed starter, optionally resolving its run-start rolls.

    Tier 0's frozen starter scorecards call this without an RNG and retain the
    canonical basic deck. Tier 0.5 passes a dedicated per-run stream so Klee's
    Mondstadt Companion pair is deterministic without perturbing encounters,
    rewards, or any previously calibrated run randomness.
    """
    spec = _character_index()[character_id]
    deck = _starter_ids(spec)         # the ONE seam; see `_starter_ids`
    if rng is None:
        return deck
    for slot in spec.get("randomized_starter", {}).values():
        replaced = slot["replace"]
        if replaced not in deck:
            raise ValueError(
                f"{character_id}: randomized starter cannot replace "
                f"missing card {replaced!r}")
        choices = list(slot["choices"])
        if not choices:
            raise ValueError(
                f"{character_id}: randomized starter has no choices")
        deck[deck.index(replaced)] = rng.choice(choices)
    return deck


def character_packages(character_id: str) -> dict[str, list[str]]:
    return {k: list(v) for k, v in
            _character_index()[character_id].get("packages", {}).items()}


@lru_cache(maxsize=1)
def _encounter_index() -> dict[str, dict]:
    return {d["id"]: d for d in _load_yaml_dir("encounters")}


def encounter_ids() -> list[str]:
    return sorted(_encounter_index())


def encounter_stages(encounter_id: str) -> list[str]:
    """A plain encounter is one stage; a 'sequence' encounter (GAUNTLET)
    lists stage encounter ids fought back-to-back with HP carryover."""
    spec = _encounter_index()[encounter_id]
    return list(spec.get("sequence", [encounter_id]))


def build_encounter(encounter_id: str) -> list[Enemy]:
    spec = _encounter_index()[encounter_id]
    if "sequence" in spec:
        raise ValueError(f"{encounter_id} is a sequence; use encounter_stages()")
    enemies = []
    for e in spec["enemies"]:
        for _ in range(e.get("count", 1)):
            enemies.append(Enemy(
                hp=e["hp"], max_hp=e["hp"], name=e["name"],
                intents=copy.deepcopy(e["intents"]),
                is_boss=e.get("is_boss", False),
                # NC-7 alpha (Q13 / R117): the MinionPower mirror, same
                # authored-passthrough shape as is_boss. No committed
                # encounter sets it today.
                is_minion=e.get("is_minion", False),
                sleep_turns=e.get("sleep_turns", 0)))
    return enemies


@lru_cache(maxsize=1)
def _pilot_index() -> dict[str, dict]:
    return {d["id"]: d for d in _load_yaml_dir("pilots")}


def reset_caches() -> None:
    """Drop every memoized view of the content tree.

    One door on purpose: `_card_prototype` is DERIVED from `_card_index`, so
    clearing the index alone would serve prototypes built from a content tree
    that no longer exists (the game_ref fresh-clone fixture does exactly
    that). Anything that changes what is on disk, or monkeypatches where the
    loader looks, must call this rather than picking caches by hand.
    """
    for cache in (_card_index, _card_prototype, _character_index,
                  _substituted_card_index, _encounter_index, _pilot_index):
        cache.cache_clear()
    # EB-213: the merged upgrade index is derived from `_substituted_card_index`
    # (a prototype row's `upgrade:` block registers only while a live door
    # resolves its id), so it is a memoized view of the content tree like the
    # six above and belongs behind the same one door.
    upgrades._upgrade_index.cache_clear()


def pilot_weights(pilot_id: str) -> dict:
    return _pilot_index()[pilot_id]["weights"]


def character_nation(character_id: str) -> str | None:
    """Home nation for reward weighting (§4.1). None for the refs, which
    never reach the companion slot anyway."""
    return _character_index().get(character_id, {}).get("nation")


def character_constraints(character_id: str) -> list[str]:
    """Declared identity comparisons like "A1_frontload>A2_scaling".

    REPORTED, NEVER ASSERTED since R204 (2026-08-24). They were the gate half
    of the retired per-axis deck-band system -- hard on starter and on the
    archetype-deck median, a warning on package decks (the round-3
    restructure). The comparison still runs on every deck of every run and
    prints conspicuously, through `axes.identity_flags`; nothing decides on
    it. The data stays here because it is per-character and the axis module
    holds no per-character data.
    """
    return list(_character_index()[character_id].get("constraints", []))


def archetype_decks(character_id: str) -> dict[str, str]:
    """deck -> pilot mapping for the median identity evaluation."""
    return dict(_character_index()[character_id].get("archetype_decks", {}))


# R204 (2026-08-24) RETIRED the live per-axis deck-band system as acceptance
# law, roster-wide, and `deck_bands()` / `stale_bands()` went with it -- the
# accessors, the three characters' data, the `BAND EXCEEDED` emission and
# B4's "a band is ratified law until a ruling moves it" docstring. No
# replacement bands are ratified. Seven-axis values are reportable
# diagnostics only. `winrate_bands()` below is UNAFFECTED: those are the
# ratified 1,000-fight bands, which the ruling leaves standing.


def winrate_bands(character_id: str) -> dict[str, dict[str, tuple]]:
    """Ratified per-encounter winrate bands: enc -> deck -> (lo, hi).
    hi may be None (floor only). Checked at >=WINRATE_BAND_MIN_FIGHTS."""
    raw = _character_index()[character_id].get("winrate_bands", {})
    return {enc: {deck: (band[0], band[1]) for deck, band in per_deck.items()}
            for enc, per_deck in raw.items()}
