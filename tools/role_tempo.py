"""The role x tempo taxonomy: vocabulary, classifiers, and the tag-through.

Track A of the Axis-Validity session (docs/axis-validity-session-charter.md
§3, docs/track-a-kickoff-brief.md). This module is the shared spine; the three
tools around it are thin:

  tools/canon_role_tempo.py         the five canon pools, out of the local DLL
  tools/suggest_role_tempo_tags.py  our three sheets -> the REVIEW column
  tools/lint_role_tempo_coverage.py the floors-only coverage gate

WHAT IS BEING MEASURED, and why it needed a new axis
----------------------------------------------------
`solve:` already existed on all three sheets and answers "what does this card
do". It cannot answer "WHEN is that worth anything", and the playtest finding
the charter grades is entirely a when-question: Fanfare is a flat adder in a
game that demands upfront numbers early and multiplicative scaling late. A
pool can be fully covered on `solve` and still have every one of an
archetype's answers land in the wrong half of the fight. `tempo_band:` is
that second coordinate.

THREE RULES THIS FILE IMPLEMENTS, all from the charter
-------------------------------------------------------
A0.1 TAG-THROUGH. A mechanic-carrier inherits the `solve` roles its token
cashes into. The corollary is the load-bearing half: a carrier that inherits
NO role at a band is a structural defect of the RESOURCE, and the rule makes
that visible without a special case for Fanfare.

  The payoff set of a METER (fanfare, encore, charge, spark, the exhaust pile)
  is DERIVED, never authored: it is the union of what its READERS deliver, at
  the band they deliver it. Carriers then inherit that set. Deriving it is
  what keeps the rule from being circular -- reading a meter is what DEFINES
  its cash-out; generating one is what INHERITS it -- and it is why the
  finding "fanfare pays nothing at fight-early" can come out of the data
  instead of being written into the table.

  The payoff set of an ENTITY (a Salon member, a bomb, the Bake-Kurage, a
  guest star, a conscript) is not derivable that way, because entities act on
  their own instead of being read by a card. Those come from ENTITY_PAYOFFS
  below -- a hand-authored, hand-auditable table, one line of provenance per
  entry, which is exactly the artifact the brief asks [USER] to review at
  A-G1.

A0.2 PROTECTIONS. `utility` is never linted and never split; the lint that
consumes this module is floors-only, so no card can ever fail. Nothing here
assigns blame to a card.

A0 AMENDMENTS. `support` joins the vocabulary (co-op roles; sim-invisible by
construction, so nothing in this track predicts a support cell). `aoe` leaves
it and becomes a MODIFIER recorded alongside the roles -- delivery shape, not
a job.

WHAT THIS FILE DELIBERATELY DOES NOT DO
----------------------------------------
No magnitude gate. A card that deals 3 at fight-early counts as frontload at
fight-early exactly as much as one that deals 12. Weighting cells by size
would be authoring balance numbers, which is a hard non-goal of this track --
and it would hide the alternative reading behind a threshold nobody ruled.
Coverage is a count question here; magnitude is Track B's curve.
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
DOCS = REPO / "docs"

# --- vocabulary -------------------------------------------------------------

# Charter A0: `support` added, `aoe` removed to the modifier list.
SOLVE = ("frontload", "scaling", "block", "sustain", "velocity", "support",
         "utility")
# A0.2(2): protected free space. Never linted, never split, never a floor.
UNLINTED = ("utility",)
FIGHT_BANDS = ("early", "mid", "late")
RUN_BANDS = ("early", "late")
MODIFIERS = ("aoe",)

# The three sheets, and the archetype vocabulary each one DECLARES in its own
# header. R66: the sheet header is canonical, so the floors are per-identity
# from these lists and from nowhere else.
SHEETS = {
    "klee": DOCS / "klee-cards.yaml",
    "furina": DOCS / "furina-cards.yaml",
    "kokomi": DOCS / "kokomi-cards.yaml",
}
COMPANION_SHEETS = {
    "fontaine": DOCS / "fontaine-companions.yaml",
    "inazuma": DOCS / "inazuma-companions.yaml",
    "mondstadt": DOCS / "mondstadt-companions.yaml",
}

# --- op -> role -------------------------------------------------------------
#
# The DIRECT half: what a card does on its own face, before any token is
# followed. Keyed on the sheet's effect ops rather than on card text, per the
# brief -- our sheets are structured data and reading their text would be
# strictly worse information.
DIRECT_ROLE = {
    "damage": "frontload",
    "repeat_this": "frontload",
    "grow_damage": "scaling",
    "block": "block",
    "block_next_turn": "block",
    "heal": "sustain",
    "draw": "velocity",
    "energy": "velocity",
    "scry_discard": "velocity",
    "discard": "velocity",
    "cost_mod": "velocity",
    "add_card": "velocity",
    "copy_companion_in_hand": "velocity",
    "copy_spotlighted_in_hand": "velocity",
    "copy_companions_played_this_combat": "velocity",
    "replay_next_companion": "velocity",
    # Application and deck-manipulation are the sheets' own `utility` voice
    # (Spooked!, commanding_gaze, Quick Fuse). Protected space by A0.2.
    "apply_aura": "utility",
    "refresh_all_auras": "utility",
    "exhaust_from": "utility",
    "detonate": "utility",
    "salon_bow": "utility",
}

# Powers that are NOT a token modifier. Everything whose name begins with a
# token prefix is handled by TOKEN_POWER_PREFIX instead, so this table stays
# small enough to audit.
POWER_ROLE = {
    "weak": ("utility",),
    "vulnerable": ("utility",),
    "cross_examination": ("utility",),
    "metallicize": ("block",),
    "feel_no_pain": ("block",),
    "dark_embrace": ("velocity",),
    "first_attack_draw": ("velocity",),
    "encore_spend_draw": ("velocity",),
    "prevent_exhaust_ward": ("sustain",),
    "amp_reaction_up": ("scaling",),
    "reaction_bonus_spark_energy": ("velocity",),
    "zero_cost_attacks_up": ("scaling",),
}

# --- tokens -----------------------------------------------------------------
#
# GENERATE: the carrier side. CONSUME/READ: the payoff side. A meter's payoff
# set is derived from the second list; a carrier inherits it through the
# first.
GENERATES = {
    "place_bomb": "bomb",
    "modify_bombs": "bomb",
    "move_bombs": "bomb",
    "chance_bomb_per_detonation": "bomb",
    "gain_spark": "spark",
    "discard_for_sparks": "spark",
    "generate_guest_star": "guest_star",
    "summon_kurage": "bake_kurage",
    "conscript": "conscript",
    "gain_charge": "charge",
    "gain_encore": "encore",
    "raise_fanfare_cap": "fanfare",
    "gain_fanfare_floor": "fanfare",
    "burst_energy": "burst",
    # Kokomi's exhaust verb is a Charge (and Burst) funnel on the relic, never
    # printed on a card -- so an exhaust op IS a charge carrier even though no
    # row says `gain_charge`. Recorded here because it is invisible on the
    # face and would otherwise read as a pure cost.
    "exhaust_from": "charge",
}
CONSUMES = {
    "detonate": "bomb",
    "salon_bow": "salon_member",
    "spend_encore": "encore",
    "crash_fanfare": "fanfare",
}

# Powers whose whole job is to make a token better. `scaling` is theirs by
# construction (a permanent multiplier on a resource's output), and the token
# is followed for the rest.
TOKEN_POWER_PREFIX = (
    ("salon_", "salon_member"),
    ("spotlight_", "spotlight"),
    ("ovation_", "spotlight"),
    ("fanfare_", "fanfare"),
    ("bomb_", "bomb"),
    ("detonation_", "bomb"),
    ("spark_", "spark"),
    ("sparks_", "spark"),
    ("kurage_", "bake_kurage"),
    ("ceremonial_garment", "charge"),
    ("bomb_and_spark_per_turn", "bomb"),
)

# THE DISTINCTION THE PREFIX RULE CANNOT MAKE, and the one a token's payoff
# set turns on: a Power that IMPROVES a resource (salon_damage_up: members
# tick harder) is a carrier and inherits; a Power that IS a payoff OF the
# resource (fanfare_delta_block: Fanfare moving is what pays the Block)
# defines the cash-out and must credit it. Left to the prefix rule, every
# Fanfare payoff would have been silently filed as a Fanfare carrier and the
# meter would have reported an empty cash-out for structural reasons that had
# nothing to do with the design.
#
# STOP-AND-SURFACE (A-G1): this table is the arguable part of the tag-through.
# Each entry is a claim about which side of that line a Power sits on.
TOKEN_PAYOFF_POWERS = {
    "fanfare_attack_per10": (
        "fanfare", ("scaling",),
        "furina-cards.yaml rapturous_applause: 'attacks +N damage per 10 "
        "Fanfare'. A per-attack term that grows with the meter -- the one "
        "genuinely multiplicative Fanfare read in the pool."),
    "fanfare_delta_block": (
        "fanfare", ("block",),
        "furina-cards.yaml unheard_confession: 'gain 1 Block whenever Fanfare "
        "CHANGES AMOUNT'. The meter moving is the payment."),
    "ceremonial_garment": (
        "charge", ("scaling",),
        "kokomi-cards.yaml ceremonial_garment: while the state holds, her "
        "attack cards read Charge (+1 damage per GARMENT_CHARGE_DIVISOR). "
        "The Burst is the window; Charge is what pays through it."),
}

# State a formula or a predicate can read. The keys are matched as substrings
# of the formula/predicate string, longest first, so `2_per_salon_member`
# resolves to salon_member and not to a shorter accidental hit.
STATE_READS = {
    "fanfare": "fanfare",
    "encore": "encore",
    "charge": "charge",
    "spark": "spark",
    "salon_member": "salon_member",
    "exhaust_pile": "exhaust_pile",
    "detonation": "bomb",
    "bombed": "bomb",
    "companion_played": "guest_star",
    "spotlight": "spotlight",
    "aura": "aura",
    "reaction": "aura",
    "this_cost_zero": "spark",
    "burst_energy": "burst",
    "per_aura": "aura",
}

# --- ENTITY payoffs (the hand-auditable half of A0.1) -----------------------
#
# An entity acts by itself, so no card "reads" it and the derivation used for
# meters cannot reach it. Each entry is (roles, band, provenance). The
# provenance line is the point: this is the table [USER] reviews at A-G1, and
# a claim about what a token cashes into is a DESIGN FACT, not a code fact.
#
# Bands here are the band at which the entity PAYS, which is not always the
# band at which its carrier is playable -- that difference is the whole
# subject of the track.
ENTITY_PAYOFFS = {
    "salon_member_usher": (
        ("block",), ("mid", "late"),
        "furina-cards.yaml gentilhomme_usher: 'THE SHIELD -- ticks 3 Block, "
        "bows for 9'. Ticks from the turn after the deploy, so it pays mid "
        "and late, never on the deploy turn."),
    "salon_member_chevalmarin": (
        ("utility", "sustain"), ("mid", "late"),
        "furina-cards.yaml surintendante_chevalmarin: 'THE APPLIER -- ticks 2 "
        "hydro, bows mass-application + Encore refund'. Application is the "
        "sheets' utility voice; the Encore refund is buffer, i.e. sustain."),
    "salon_member_crabaletta": (
        ("frontload",), ("mid", "late"),
        "furina-cards.yaml mademoiselle_crabaletta: 'THE HAMMER -- ticks 6 "
        "hydro, bows for 14'. Damage only."),
    "bomb": (
        ("frontload",), ("mid", "late"),
        "klee-cards.yaml: a bomb is delayed damage that resolves on a later "
        "turn or on a detonate. Damage only at the entity level -- "
        "bomb_damage_up and detonation_splash are POWERS and carry their own "
        "scaling through TOKEN_POWER_PREFIX."),
    "bake_kurage": (
        ("frontload", "block", "scaling"), ("mid", "late"),
        "kokomi-cards.yaml bake_kurage: 'pulses at each turn end for "
        "KURAGE_PULSE_BASE + Charge/KURAGE_PULSE_DIVISOR damage, hydro "
        "application, and KURAGE_PULSE_BLOCK Block'. The Charge term is what "
        "makes it scaling; kurages_oath adds the ward on top."),
    "spark": (
        ("frontload", "velocity"), ("mid", "late"),
        "klee-cards.yaml true_spark_knight: sparks buy a FREE ATTACK at a "
        "threshold -- damage the deck did not pay energy for, so both the "
        "frontload and the velocity read are literal."),
    "spotlight": (
        ("scaling",), ("mid", "late"),
        "furina-cards.yaml: the Spotlight is a selector; every payoff on it "
        "is a multiplier or a printed bonus on the selected card "
        "(spotlight_mult_bonus, spotlight_flat_damage). The DISCOUNT and DRAW "
        "powers are velocity and reach the pool through POWER_ROLE-adjacent "
        "prefixes, not through the entity."),
    "aura": (
        ("utility",), ("early", "mid", "late"),
        "elemental auras are application: they enable reactions rather than "
        "delivering a role themselves. The reaction damage is printed on the "
        "card that cashes it (bonus_vs_aura), so crediting the aura too would "
        "double-count."),
    "exhaust_pile": (
        ("scaling",), ("late",),
        "kokomi-cards.yaml pearl_barrage / depths_judgment / undertow: the "
        "pile is a monotonically growing counter read as `+N per exhausted "
        "card`. It is empty at fight-early by construction."),
}
# Entities whose payoff set is the pool they generate INTO, resolved from the
# companion sheets rather than authored here.
GENERATED_POOLS = {
    "guest_star": ("fontaine",),
    "conscript": ("inazuma",),
}


# --- sheet reading ----------------------------------------------------------

def load_rows(path: Path) -> list[dict]:
    """One design sheet's card rows."""
    docs = [d for d in yaml.safe_load_all(path.read_text(encoding="utf-8"))
            if d]
    if not docs:
        return []
    rows = docs[0]
    return [r for r in rows if isinstance(r, dict) and "id" in r]


def declared_archetypes(path: Path) -> list[str]:
    """The archetype vocabulary the sheet HEADER declares (R66).

    Read from the header rather than collected from the rows on purpose: a
    typo in one row's `archetypes` would otherwise mint an archetype, and the
    floors are per-identity from the DECLARED list.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"#\s*Archetypes?\s*(?:\([^)]*\))?\s*:\s*(.+)", line)
        if not m:
            continue
        # The header line WRAPS on two of the three sheets, and the wrap falls
        # inside a parenthetical every time. Unbalanced parens is therefore
        # the continuation test -- Kokomi's list lost `generic` to a naive
        # single-line read, which would have silently deleted an identity from
        # the floors.
        text = m.group(1)
        j = i
        while text.count("(") > text.count(")") and j + 1 < len(lines):
            j += 1
            text += " " + lines[j].lstrip("#").strip()
        names = []
        for chunk in text.split("|"):
            word = re.match(r"\s*([a-z_]+)", chunk)
            if word:
                names.append(word.group(1))
        if names:
            return names
    raise SystemExit(f"{path.name}: no `# Archetypes:` header line (R66)")


def _walk(effects, gated=False, gates=()):
    """Yield (effect, gated, gates) over a row's effect tree.

    `conditional` branches are GATED: their contents are not part of the
    card's unconditional body, which is what the fight-early test asks about.
    `gates` carries the tokens the enclosing conditionals READ, so the roles
    inside a branch can be credited to the resource that unlocked them --
    without that link, `if: fanfare_at_least_20 then: damage` would credit
    Fanfare with nothing at all.
    """
    for fx in effects or ():
        if not isinstance(fx, dict):
            continue
        if fx.get("op") == "conditional":
            yield fx, gated, gates
            token = _state_token(str(fx.get("if", "")))
            inner = tuple(gates) + ((token,) if token else ())
            for branch in ("then", "else"):
                yield from _walk(fx.get(branch), gated=True, gates=inner)
            continue
        yield fx, gated, gates


def _formula_strings(fx: dict) -> list[str]:
    out = []
    for key in ("bonus_formula", "times_formula", "amount_formula", "times",
                "if", "scope"):
        val = fx.get(key)
        if isinstance(val, str):
            out.append(val)
        elif isinstance(val, dict):
            out.extend(str(v) for v in val.values())
    for key in ("bonus_vs_aura", "bonus_vs_bombed"):
        if key in fx:
            out.append(key)
    return out


def _state_token(text: str) -> str | None:
    for needle in sorted(STATE_READS, key=len, reverse=True):
        if needle in text:
            return STATE_READS[needle]
    return None


def _power_token(power: str) -> str | None:
    for prefix, token in TOKEN_POWER_PREFIX:
        if power.startswith(prefix):
            return token
    return None


def scan_row(row: dict) -> dict:
    """Everything the classifiers need, read once off one card row."""
    effects = list(row.get("effects") or [])
    effects += list(row.get("sly") or [])
    direct: set[str] = set()
    # The roles this card DELIVERS itself, as distinct from `direct`, which
    # also carries the `scaling` a token-modifying Power gets by construction.
    # Only `delivered` may define a meter's cash-out set: letting the auto-tag
    # feed the derivation would have every meter report `scaling` purely
    # because some Power improves it, which is the claim the derivation exists
    # to TEST rather than to assume.
    delivered: set[str] = set()
    generates: set[str] = set()
    reads: set[str] = set()
    # PER-READ ATTRIBUTION. A token is credited only with the role of the
    # effect that actually reads it. Crescendo reads Fanfare on its damage
    # line AND grows permanently on a separate line; crediting Fanfare with
    # `scaling` because the two share a card would have been the derivation
    # inventing the very shape the charter says Fanfare lacks.
    read_roles: dict[str, set[str]] = {}
    card_level_reads: set[str] = set()
    aoe = False
    unconditional_body = False
    gated_effect = False

    for fx, gated, gates in _walk(effects):
        op = fx.get("op")
        if gated:
            gated_effect = True
        if op == "conditional":
            token = _state_token(str(fx.get("if", "")))
            if token:
                reads.add(token)
            continue

        target = fx.get("target")
        if str(target).startswith("all_") or target == "random_enemies":
            aoe = True

        role = DIRECT_ROLE.get(op)
        if op == "damage" and target == "self":
            role = None            # self-damage is a cost, never a job
        if role:
            direct.add(role)
            delivered.add(role)

        # This effect's own reads: its formulas, plus every gate it sits
        # behind. Both are "this resource is why the number happened".
        here = {t for text in _formula_strings(fx)
                if (t := _state_token(text))} | {g for g in gates if g}
        for token in here:
            reads.add(token)
            if role:
                read_roles.setdefault(token, set()).add(role)

        if op == "apply_power":
            power = str(fx.get("power", ""))
            if power in TOKEN_PAYOFF_POWERS:
                token, roles, _why = TOKEN_PAYOFF_POWERS[power]
                direct.update(roles)
                reads.add(token)
                read_roles.setdefault(token, set()).update(roles)
                continue
            token = _power_token(power)
            if token:
                direct.add("scaling")
                generates.add(token)
                reads.add(token)
            else:
                direct.update(POWER_ROLE.get(power, ("utility",)))
                delivered.update(POWER_ROLE.get(power, ("utility",)))
            if fx.get("member"):
                member = str(fx["member"])
                # A deploy carries BOTH: the typed member (what that member
                # does on stage) and the untyped stage counter (what
                # `2_per_salon_member` and `has_salon_members` read). They are
                # different payoffs of the same play and crediting only one
                # would understate the card either way.
                generates.update(
                    {f"salon_member_{m}" for m in
                     (("usher", "chevalmarin", "crabaletta")
                      if member == "random" else (member,))})
                generates.add("salon_member")

        if op in GENERATES:
            generates.add(GENERATES[op])
        if op in CONSUMES:
            # A CONSUME op has no number of its own -- `spend_encore 5` then
            # `block 10` is one bargain across two lines -- so it is credited
            # at the CARD level with everything the card delivers.
            reads.add(CONSUMES[op])
            card_level_reads.add(CONSUMES[op])

        # An UNCONDITIONAL BODY is a printed, ungated number that pays the
        # turn the card is played. `amount: 0` with a bonus_formula is the
        # sheets' explicit "this pays nothing on an empty meter" idiom
        # (suffering_for_art says so out loud), so it does not count.
        is_self_cost = op == "damage" and target == "self"
        if not gated and not is_self_cost \
                and isinstance(fx.get("amount"), (int, float)) \
                and fx["amount"] > 0:
            unconditional_body = True
        if not gated and op in ("conscript", "generate_guest_star",
                                "summon_kurage", "place_bomb", "detonate",
                                "salon_bow", "exhaust_from", "refresh_all_auras",
                                "apply_aura", "copy_companion_in_hand",
                                "copy_spotlighted_in_hand", "replay_next_companion",
                                "copy_companions_played_this_combat"):
            unconditional_body = True

    if str(row.get("requires", "")).startswith("burst"):
        reads.add("burst")
        card_level_reads.add("burst")
    for token in card_level_reads:
        read_roles.setdefault(token, set()).update(delivered)

    return {
        "direct": direct,
        "delivered": delivered,
        "generates": generates,
        "reads": reads,
        "read_roles": read_roles,
        "aoe": aoe,
        "unconditional_body": unconditional_body,
        "gated_effect": gated_effect,
    }


# --- tempo bands ------------------------------------------------------------

def _cost_number(cost) -> int:
    """`X` is priced as the top of the curve: it is never a turn-one play."""
    if isinstance(cost, (int, float)):
        return int(cost)
    return 3


def fight_bands(row: dict, scan: dict) -> list[str]:
    """When in a FIGHT this card is worth playing.

    early -- cost <= 1, not a Power, and it has an unconditional printed body.
    late  -- a Power (the payoff accrues), or cost >= 3 / X, or it reads
             accumulated state, or its effect is behind a gate.
    mid   -- everything else, plus cost 2, plus the bridge for a card that is
             genuinely both (a cheap body with a scaling rider is live at
             every band, and saying so is the point of multi-band).
    """
    cost = _cost_number(row.get("cost"))
    is_power = row.get("type") == "power"
    reads_state = bool(scan["reads"] & {
        "fanfare", "encore", "charge", "spark", "salon_member",
        "exhaust_pile", "bomb", "spotlight", "burst", "guest_star"})

    early = (not is_power) and cost <= 1 and scan["unconditional_body"]
    late = is_power or cost >= 3 or reads_state or scan["gated_effect"]
    bands = set()
    if early:
        bands.add("early")
    if late:
        bands.add("late")
    if cost == 2 or not bands or bands == {"early", "late"}:
        bands.add("mid")
    return [b for b in FIGHT_BANDS if b in bands]


def run_bands(row: dict, scan: dict) -> list[str]:
    """When in a RUN this card is available and functional.

    early -- you can draft it in act 1 and it works on its own.
    late  -- it needs the deck assembled first (a payoff, a rare, or a card
             that reads a resource it does not itself make).
    """
    rarity = str(row.get("rarity", "common"))
    role = str(row.get("role", "glue"))
    reads_only = scan["reads"] - scan["generates"]
    bands = set()
    if rarity in ("basic", "common") or (rarity == "uncommon"
                                         and role != "payoff"):
        bands.add("early")
    if rarity == "rare" or role == "payoff" or reads_only:
        bands.add("late")
    return [b for b in RUN_BANDS if b in bands] or ["early"]


# --- tag-through ------------------------------------------------------------

def derive_meter_payoffs(scans: dict[str, dict]) -> dict[str, dict[str, set]]:
    """{token: {fight_band: {roles}}} for the DERIVED (meter) tokens.

    A meter's cash-out set is the union of what its readers deliver, at the
    band those readers deliver it. Carriers inherit this; a carrier that
    inherits nothing at a band is the finding the corollary names.
    """
    payoffs: dict[str, dict[str, set]] = {}
    for info in scans.values():
        for token, roles in info["read_roles"].items():
            if token in ENTITY_PAYOFFS or token in GENERATED_POOLS:
                continue
            roles = roles - {"utility"}
            if not roles:
                continue
            slot = payoffs.setdefault(token, {b: set() for b in FIGHT_BANDS})
            for band in info["fight"]:
                slot[band] |= roles
    return payoffs


def entity_payoffs(companion_roles: dict[str, set]) -> dict[str, dict[str, set]]:
    """ENTITY_PAYOFFS plus the generated-companion pools, in the same shape."""
    out: dict[str, dict[str, set]] = {}
    for token, (roles, bands, _why) in ENTITY_PAYOFFS.items():
        out[token] = {b: (set(roles) if b in bands else set())
                      for b in FIGHT_BANDS}
    for token, pools in GENERATED_POOLS.items():
        roles = set()
        for pool in pools:
            roles |= companion_roles.get(pool, set())
        # A generated card is playable the turn it arrives, so it pays at
        # every band its own body would.
        out[token] = {b: set(roles) for b in FIGHT_BANDS}
    return out


def companion_pool_roles() -> dict[str, set]:
    """What each companion pool's cards actually deliver, by the same rules."""
    out: dict[str, set] = {}
    for pool, path in COMPANION_SHEETS.items():
        if not path.exists():
            continue
        roles: set[str] = set()
        for row in load_rows(path):
            roles |= scan_row(row)["direct"] - {"utility"}
        out[pool] = roles
    return out


def classify_pool(rows: list[dict]) -> tuple[dict[str, dict], dict]:
    """Full classification for one character's rows, tag-through applied.

    Returns (per-card scans, the token payoff table) -- the second half is a
    deliverable in its own right: it is the hand-auditable tag-through table
    the brief asks for, and it is what A-G1 reviews.
    """
    scans = {}
    for row in rows:
        scan = scan_row(row)
        scan["fight"] = fight_bands(row, scan)
        scan["run"] = run_bands(row, scan)
        scans[row["id"]] = scan

    payoffs = derive_meter_payoffs(scans)
    payoffs.update(entity_payoffs(companion_pool_roles()))

    for scan in scans.values():
        inherited = {b: set() for b in FIGHT_BANDS}
        for token in scan["generates"]:
            table = payoffs.get(token)
            if not table:
                continue
            for band in FIGHT_BANDS:
                inherited[band] |= table[band]
        scan["inherited"] = inherited
        # The card's roles AT A BAND: its own direct roles at every band it is
        # playable, plus whatever its tokens cash into at that band.
        cells = {b: set() for b in FIGHT_BANDS}
        for band in scan["fight"]:
            cells[band] |= scan["direct"]
        for band in FIGHT_BANDS:
            cells[band] |= inherited[band]
        scan["cells"] = cells
        scan["solve"] = sorted(
            (scan["direct"] | set().union(*inherited.values())) or {"utility"})
    return scans, payoffs
