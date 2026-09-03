#!/usr/bin/env python3
"""DEV-ONLY codegen for the QUARANTINED prototype surface (R213 B, EB-147).

    python tools/gen_prototype_cards.py            # emit the dev-only C#
    python tools/gen_prototype_cards.py --check    # CI guard (staleness)

WHY THIS IS A SEPARATE ENTRY POINT AND NOT A FOURTH `--character`
-----------------------------------------------------------------
R213 B: *"built by a dev-only codegen profile"* -- the DEFAULT generator run
must not emit prototypes. `tools/gen_roster_cards.py` runs
`--character all`, and `all` means `PROFILES.values()`. Registering a
prototype profile there would put it in the default run by definition, and
"remember not to pass --all" is not a quarantine. So the prototype surface
gets its own script, its own out dir, its own manifest and its own namespace,
and `PROFILES` / `PLAN_BUILDERS` are untouched -- which also keeps
`tools/lint_roster_registry.py` (which reads `def _plan_<id>(` as the roster
of real characters) honest: there is no fourth character here.

THE EMITTER IS THE SAME EMITTER, AND THAT IS THE REQUIREMENT
------------------------------------------------------------
R213 B also says the rows are *"STILL checked for ... codegen
expressibility"*. A prototype run through a lenient second emitter would
answer a different question than the one we are asking -- it would prove a
prototype can be printed, not that it can SHIP. So this file owns no
templates: it calls `gen.blocked_reason` and `gen.emit` with the OWNING
character's profile, `dataclasses.replace`d to redirect sheet, out dir,
manifest and namespace. Element cadence, art loader and `CharacterId` come
from the owner untouched, because a Kokomi prototype that does not apply Hydro
off its Attacks is not a Kokomi prototype.

THE UPGRADE CHANNEL IS ON THE ROW (`EB-213`)
--------------------------------------------
Shipped upgrades live in `docs/<character>-upgrades.yaml`, keyed by shipped
card id. A `proto_` key in one of those files would give R213 B's deletion
rule a second file to remember, and a substituted prototype would carry its
upgrade in a place the row's own deletion does not reach. So a prototype row
carries `upgrade: {<key>: <delta>}` itself, and this script registers it into
the merged delta index (`gen.register_upgrade_deltas`) before emitting the
card. Everything after that is the SHIPPED path, unforked: `gen.upgrade_plan`
decides expressibility, the ordinary `*_upgrade` readers emit the vars, and
the card gets the same `OnUpgrade` a shipped card gets -- which is the whole
point, because the question a prototype answers is whether the card can SHIP.
A row with no `upgrade:` block is base-only, as every row on this surface was
before EB-213; a row whose declared delta the emitter cannot express is a
build failure for the reason in the next section.

A BLOCKED PROTOTYPE ROW IS A BUILD FAILURE, NOT A MANIFEST LINE
---------------------------------------------------------------
The character profiles list blocked cards in their manifests: a sheet is a
ratified design artifact that legitimately runs ahead of the runtime. This
surface is the opposite -- it exists to be tried at the real game THIS WEEK,
so a row the emitter cannot express is a row that cannot be tried, and
carrying it as a manifest entry would let a slice go to the funnel with a card
in it that does not exist. It stops the run, by name, with the emitter's own
reason. (Same shape as `_plan_klee`'s companion loop and `_plan_roster`'s
Guest Star loop, for the same reason.)

WHAT THE EMITTED C# IS NOT
--------------------------
It is not in any character's reward pool. `PrototypeRoster` is handed to the
three off-pool builders through `KleeMod.PrototypeCards`, which is `#if
PROTOTYPE_CARDS` and empty otherwise; off-pool means IN the pool for
`CardModel.Pool` legality (or the card throws "You monster!" the first time it
is drawn -- see `tools/lint_pool_membership.py`) and OUT of
`GetUnlockedCards`, which is the sole path into reward rolls and card
transforms. And the whole directory is `Compile Remove`d from
`KleeCode.csproj` unless `PrototypeCards=true`, so a release build does not
contain the classes at all: there is no id a shipped mod could be talked into
granting.

EVERY ROW'S UPGRADE MUST SHOW ON THE CARD (`EB-283` / `EB-277`)
---------------------------------------------------------------
The rows below the `plan()` walk are checked one further way, and this is the
only gate on this surface that is about what a card LOOKS LIKE rather than
about whether it can be emitted at all. See `upgrade_face_findings`.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import replace
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import tools.gen_klee_cards as gen                            # noqa: E402
from tier0.content.loader import PROTOTYPE_ID_PREFIX          # noqa: E402
from tier0.content.upgrades import prototype_default_delta    # noqa: E402
from understudy import authorship                             # noqa: E402

SHEET = REPO / "docs" / "prototype-surface.yaml"
OUT_DIR = REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype" / "Generated"
MANIFEST = OUT_DIR / "manifest.json"
NAMESPACE = "KleeMod.Cards.Prototype.Generated"
SCRIPT = "tools/gen_prototype_cards.py"

# The directory-and-manifest identity `_check_plan` / `_write_plan` read. Its
# `character_id` is "prototype" ONLY for log lines and the stale label; every
# per-card emit uses the owning character's profile (see `_profile_for`).
DIR_PROFILE = replace(
    gen.KLEE_PROFILE,
    character_id="prototype",
    sheet=SHEET,
    out_dir=OUT_DIR,
    manifest=MANIFEST,
    namespace=NAMESPACE,
    generator_script=SCRIPT,
    arm_keyword_tips=True,
)


def _profile_for(character_id: str) -> gen.CharacterProfile:
    """The owning character's profile, redirected at the prototype surface.

    `character_id`, `native_element`, `cadence`, `art_loader` and
    `emit_character_identity` are the OWNER's and are not overridden: they are
    what make the emitted card the character's card rather than a generic one.
    Only the four location fields move -- and `arm_keyword_tips`, which is a
    fact about the SURFACE rather than about the owner (`EB-272`): the three
    quarantined arms invented `Bomb`, `Set off`, `Spark`, `Mine`, `Tide`,
    `Surge`, `Exert`, `Mend`, `Plan`, `Garment` and the `Swirl` verb, and only
    a row on this sheet can mean the arm's rule by printing one. The same word
    on a shipped sheet means the shipped rule and keeps the shipped tip.
    """
    owner = gen.PROFILES[character_id]
    return replace(
        owner,
        sheet=SHEET,
        out_dir=OUT_DIR,
        manifest=MANIFEST,
        namespace=NAMESPACE,
        generator_script=SCRIPT,
        arm_keyword_tips=True,
    )


def _rows() -> list[dict]:
    if not SHEET.exists():
        return []
    return yaml.safe_load(SHEET.read_text(encoding="utf-8")) or []


def effective_upgrade(card: dict) -> dict | None:
    """This row's delta after the Prototype-stage rule, or None. MUTATES.

    `EB-213`, and it happens BEFORE `blocked_reason`: R20 blocks a card
    carrying an inline `upgrade:` key, because on a shipped sheet that key
    could silently diverge from the ratified upgrades file. Here the row IS the
    ratified home, so the block is lifted by taking the key off the card and
    putting it in the index the shipped path reads -- which is why this pops
    rather than reads.

    `EB-283`. A row with NO authored block takes the Prototype-stage rule, and
    it is imported from `tier0.content.upgrades` rather than written here so
    the two engines apply one implementation and not two spellings of one. An
    authored block always wins, which is how a Balance-stage ruling replaces
    the default without removing it.

    `EB-315`. `no_upgrade:` is the row's OPT-OUT and beats both: a row that
    states, in a sentence, why it cannot upgrade is base-only by declaration
    and the rule is not consulted. It is popped for `upgrade:`'s reason -- the
    emitter's field whitelist is deliberately total -- and read back off the
    committed sheet by the gate and by `tier0.content.loader`, which is what
    keeps the two engines and the register on one answer.
    """
    upgrade = card.pop("upgrade", None)
    no_upgrade = card.pop("no_upgrade", None)
    if upgrade is not None and (not isinstance(upgrade, dict) or not upgrade):
        raise SystemExit(
            f"gen_prototype_cards: {card['id']}: `upgrade:` must be a "
            "non-empty map of delta keys, as an upgrades sheet's entry is; "
            "drop the key for a base-only row.")
    if no_upgrade is not None:
        if upgrade is not None:
            raise SystemExit(
                f"gen_prototype_cards: {card['id']}: carries BOTH `upgrade:` "
                "and `no_upgrade:` -- a row either has a delta or states why "
                "it has none, never both.")
        if not isinstance(no_upgrade, str) or not no_upgrade.strip():
            raise SystemExit(
                f"gen_prototype_cards: {card['id']}: `no_upgrade:` must be "
                "the REASON this row cannot upgrade, as a non-empty string; "
                "a bare flag is the silent exemption this key exists to stop.")
        return None
    if upgrade is None:
        upgrade = prototype_default_delta(
            card["id"], card.get("cost"), card.get("effects", []),
            bool(card.get("exhaust")), card.get("plan") or []) or None
    return upgrade


# --- EB-283 / EB-277: the upgrade has to show on the card -------------------

#: The three shapes read off the EMITTED C#. Deliberately read off the emitted
#: source rather than off the row: the row says what was ASKED for, and the
#: whole defect class is an ask that the emitter turned into nothing visible.
_ON_UPGRADE = re.compile(
    r"protected override void OnUpgrade\(\)\s*\{(.*?)\n    \}", re.S)
_DESCRIPTION = re.compile(r'\("description", (".*?")\),\n', re.S)
_VAR_MOVED = re.compile(r'DynamicVars(?:\.(\w+)|\["(\w+)"\])\s*\.\s*Upgrade')
_VAR_PRINTED = re.compile(r"\{(\w+):diff\(\)\}")

#: A var that FEEDS a printed one. The base game's `Calculated*Var` is a
#: TRIPLE -- `CalculationBase` holds the number an upgrade moves and
#: `CalculatedDamage` / `CalculatedBlock` is what the face prints -- so a
#: literal name match would call every scaled companion row invisible. Mirrors
#: `gen_klee_cards.build_vars`' own branch; the two move together.
_VAR_FEEDS = {"CalculationBase": {"CalculatedDamage", "CalculatedBlock"}}

_DEBT_SPARK_ARM = (
    "outside the Prototype-stage rule by declaration: `EB-218`'s Spark-arm "
    "migration twins and the Spark surface predate `EB-283`, whose prefixes "
    "(`upgrades.PROTOTYPE_DEFAULT_PREFIXES`) are the five overhaul arms. "
    "Their upgrades are the SHIPPED rows' and are a Balance-stage ruling, not "
    "a default this generator may invent")

#: THE DEBT, CURATED AND CHECKED BOTH WAYS.
#:
#: `EB-277` was "an upgraded prototype card was identical to its base", and
#: `EB-283` answered it with a default rule -- but a rule with declared reach
#: leaves rows outside that reach, and nothing said which rows those were.
#: [USER] found two of them by playing ("'Change of Plans' has no upgrade?",
#: "Neither does Rally"), which is the sign that the register was a human's
#: memory. It is a file now.
#:
#: Two rules keep it from rotting, both enforced in `upgrade_face_findings`:
#: an id here that is not on the sheet is a finding (R213 B deletes rows
#: whole, and an exemption must go with its row), and an id here whose row now
#: passes is a finding too (a paid debt is deleted, never left standing).
#:
#: `EB-315` EMPTIED THE OVERHAUL-ARM HALF OF IT, two ways. The five Plan-only
#: rows and Stolen Chapter now upgrade for real -- the rule reads a row's
#: `plan:` line -- so their entries were DELETED rather than reworded. The two
#: that still cannot (`proto_mc_lisa_violet_arc`, `proto_mc_sucrose_gust`) say
#: so ON THE ROW with `no_upgrade:`, which travels with the row under R213 B's
#: deletion rule and is read by both engines; this dict is now the Spark
#: arm's alone, which is the one arm the Prototype-stage rule never claimed.
UPGRADE_DEBT: dict[str, str] = {
    # The Spark arm and its migration twins (`EB-218`, R224).
    "proto_hold_the_line_spark": _DEBT_SPARK_ARM,
    "proto_itto_superlative_superstrength_either": _DEBT_SPARK_ARM,
    "proto_itto_superlative_superstrength_priced": _DEBT_SPARK_ARM,
    "proto_kaboom_sink": _DEBT_SPARK_ARM,
    "proto_muster_subsidy_funnel": _DEBT_SPARK_ARM,
    "proto_pearl_barrage_turn": _DEBT_SPARK_ARM,
    "proto_pop_spark": _DEBT_SPARK_ARM,
    "proto_powder_charge_spark": _DEBT_SPARK_ARM,
    "proto_shinobu_sanctifying_ring_either": _DEBT_SPARK_ARM,
    "proto_shinobu_sanctifying_ring_priced": _DEBT_SPARK_ARM,
    "proto_smoke_and_sparks_spark": _DEBT_SPARK_ARM,
    "proto_spark_blast": _DEBT_SPARK_ARM,
    "proto_spark_burst_conversion": _DEBT_SPARK_ARM,
    "proto_spark_double_tap": _DEBT_SPARK_ARM,
    "proto_spark_finisher": _DEBT_SPARK_ARM,
    "proto_spark_mode_bombs": _DEBT_SPARK_ARM,
    "proto_spark_priced_draw": _DEBT_SPARK_ARM,
    "proto_spark_priced_strike": _DEBT_SPARK_ARM,
    "proto_spark_strike": _DEBT_SPARK_ARM,
    "proto_spark_sweep": _DEBT_SPARK_ARM,
    "proto_thoma_crimson_ooyoroi_either": _DEBT_SPARK_ARM,
    "proto_thoma_crimson_ooyoroi_priced": _DEBT_SPARK_ARM,
    "proto_true_spark_knight": _DEBT_SPARK_ARM,
}


def _upgrade_face_finding(delta: dict | None, source: str) -> str | None:
    """Why this emitted card's `+` face is the same as its base, or None.

    PURE, and it reads only the two strings the player is shown: the card's
    emitted `description` rows and its emitted `OnUpgrade` body. That is the
    point -- "the smith gave me back the card I put in" is a fact about the
    printed face, and every other reading of it (a delta exists, a delta was
    expressible, a var moved) was true of `EB-277`'s own two cards while they
    printed identical text.

    Four ways an upgrade shows, and any one is enough:

      * an `{IfUpgraded:show:...}` clause in the face -- an APPENDED effect,
        or a cost the face states in words;
      * `RemoveKeyword` / `AddKeyword` -- the keyword rail under the art;
      * `EnergyCost.Upgrade*` -- the cost pip in the corner;
      * a `DynamicVars` move whose var the face prints as `{Var:diff()}`,
        directly or through `_VAR_FEEDS`.
    """
    if not delta:
        return ("no upgrade at all -- the smith would hand back a copy of the "
                "card (`EB-277`)")
    match = _ON_UPGRADE.search(source)
    body = match.group(1) if match else ""
    face = " ".join(_DESCRIPTION.findall(source))

    if "{IfUpgraded:" in face:
        return None
    if ("RemoveKeyword(" in body or "AddKeyword(" in body
            or "EnergyCost.Upgrade" in body):
        return None
    moved: set[str] = set()
    for dotted, indexed in _VAR_MOVED.findall(body):
        name = dotted or indexed
        moved.add(name)
        moved |= _VAR_FEEDS.get(name, set())
    printed = set(_VAR_PRINTED.findall(face))
    if moved & printed:
        return None

    statements = [line for line in body.strip().splitlines()
                  if line.strip() and not line.strip().startswith("//")]
    if not statements:
        return (f"declares {sorted(delta)} and emits an OnUpgrade that does "
                "nothing")
    return (f"declares {sorted(delta)}; OnUpgrade moves "
            f"{sorted(moved) or 'no var'} and the face prints "
            f"{sorted(printed) or 'no upgradable number'} -- the `+` card is "
            "printed identically to its base")


def upgrade_face_findings(
        rows: list[dict], deltas: dict[str, dict],
        generated: dict[str, str]) -> list[str]:
    """Every row whose upgrade a player could not see, plus every stale debt.

    Returns rendered lines; empty is green. Split out of `plan()` so a test can
    run it against a synthetic row and watch it go red, which is the only way
    to know a gate is a gate (`understudy` red-first discipline).

    `EB-315`. TWO REGISTERS ARE CONSULTED, and the row's own beats the file's:
    `no_upgrade:` is written on the row, travels with it under R213 B's
    deletion rule, and is read by both engines -- so it is where a NEW
    exemption goes. `UPGRADE_DEBT` is what is left of the same idea kept in a
    dict, and it is now the Spark arm's alone (see its own note).
    """
    findings: list[str] = []
    ids = {row["id"] for row in rows}
    for row in rows:
        card_id = row["id"]
        source = generated.get(card_id)
        if source is None:
            continue
        why = _upgrade_face_finding(deltas.get(card_id), source)
        excused = UPGRADE_DEBT.get(card_id) or row.get("no_upgrade")
        if why and excused is None:
            findings.append(f"{card_id}: {why}")
        elif why is None and excused is not None:
            findings.append(
                f"{card_id}: this row is still excused, and it now prints its "
                "upgrade -- delete the exemption (the row's `no_upgrade:` key, "
                "or gen_prototype_cards.UPGRADE_DEBT)")
        # `EB-315`, the same anti-rot rule the debt dict keeps, for the key
        # that replaced it: an opt-out the RULE has since caught up with is an
        # opt-out that would quietly suppress a real campfire choice. A paid
        # debt is deleted, never left standing.
        if row.get("no_upgrade") and prototype_default_delta(
                card_id, row.get("cost"), row.get("effects", []),
                bool(row.get("exhaust")), row.get("plan") or []):
            findings.append(
                f"{card_id}: `no_upgrade:` still excuses this row, and the "
                "Prototype-stage rule now derives a delta for it -- delete "
                "the key so the row takes the upgrade the rule gives it")
    for card_id in sorted(UPGRADE_DEBT):
        if card_id not in ids:
            findings.append(
                f"{card_id}: UPGRADE_DEBT names a row that is not on the "
                "surface -- a deleted row takes its exemption with it "
                "(R213 B)")
    return findings


def plan() -> gen.ProfilePlan:
    rows = _rows()
    generated: dict[str, str] = {}
    owners: dict[str, str] = {}
    # EB-213: the row-carried upgrade deltas, recorded so "can this staged
    # card be smithed, and to what?" is answerable from the manifest rather
    # than by re-reading the sheet.
    upgrades: dict[str, dict] = {}
    # EB-315: the rows that OPTED OUT, with the reason, so "which staged rows
    # ship base-only, and why?" is one manifest read rather than a grep. The
    # shipped sheets answer the same question with `upgrades.no_upgrade_path`;
    # this is that ledger for a surface whose upgrades live on the row.
    no_upgrade: dict[str, str] = {}
    # EB-150's lesson, carried onto this surface: a choose-one card's MODE
    # FACES are pool members too. `CardModel.Pool` falls through to
    # MockCardPool and throws "You monster!" inside
    # `NChooseACardSelectionScreen._Ready()`, which soft-locks the turn -- and
    # a staged prototype turn is precisely a turn that draws and previews the
    # card. The character plans carry these in a separate `<Char>ModalOptions`
    # roster; here they go into `PrototypeRoster` itself, because a second
    # generated file for the same membership buys nothing on a surface whose
    # healthy state is empty.
    mode_faces: dict[str, list[str]] = {}

    for row in rows:
        # EB-190. `authored_by` is checked HERE and then STRIPPED: the field
        # records which model families wrote the row, which is a fact about
        # the row and not about the card, and `--check` staleness is the proof
        # that it cannot move generated output -- the emitter never sees it.
        # A row without it cannot be generated at all, because the seat's
        # refusal has nothing to read and the separation would be back to
        # being a procedure somebody remembers.
        bad = authorship.field_findings(row)
        if bad:
            raise SystemExit("gen_prototype_cards: " + "; ".join(bad))
        card = authorship.strip_field(row)
        card_id = card["id"]
        if not card_id.startswith(PROTOTYPE_ID_PREFIX):
            raise SystemExit(
                f"gen_prototype_cards: {card_id}: prototype ids must start "
                f"{PROTOTYPE_ID_PREFIX!r} (tier0 loader enforces the same "
                "rule; a bare id collides with a shipped class name).")
        character = card.get("character")
        if character not in gen.PROFILES:
            raise SystemExit(
                f"gen_prototype_cards: {card_id}: `character:` must name a "
                f"roster character {sorted(gen.PROFILES)}, got {character!r}.")
        profile = _profile_for(character)
        # EB-213, and it happens BEFORE `blocked_reason`: R20 blocks a card
        # carrying an inline `upgrade:` key, because on a shipped sheet that
        # key could silently diverge from the ratified upgrades file. Here the
        # row IS the ratified home, so the block is lifted by taking the key
        # off the card and putting it in the index the shipped path reads.
        # EB-315: `no_upgrade:` is read (and popped) by the same call, so the
        # reason is recorded here where the delta would have been.
        if row.get("no_upgrade"):
            no_upgrade[card_id] = row["no_upgrade"]
        upgrade = effective_upgrade(card)
        if upgrade is not None:
            gen.register_upgrade_deltas(card_id, upgrade)
            upgrades[card_id] = dict(upgrade)
        reason = gen.blocked_reason(card, profile)
        if reason:
            # See the module docstring: a prototype that cannot be emitted
            # cannot be tried, so this is louder than a manifest row.
            raise SystemExit(
                f"gen_prototype_cards: {card_id} is NOT EXPRESSIBLE: {reason}. "
                "A prototype row must be emittable today -- rewrite it inside "
                "the existing grammar, or take the runtime work first.")
        if upgrade is not None:
            _, upgrade_reason = gen.upgrade_plan(card)
            if upgrade_reason:
                # Same rule as the body above, for the same reason: a
                # declared upgrade the emitter drops is a campfire that does
                # nothing on a card staged to be tried at a campfire. On a
                # character sheet this is a `no_upgrade_path` manifest line;
                # here it stops the run.
                raise SystemExit(
                    f"gen_prototype_cards: {card_id}'s `upgrade:` is NOT "
                    f"EXPRESSIBLE: {upgrade_reason}. A staged upgrade must be "
                    "emittable today -- rewrite the delta inside the existing "
                    "grammar, drop the key to stage a base-only row, or take "
                    "the runtime work first.")
        generated[card_id] = gen.emit(card, profile)
        owners[card_id] = character
        mode_faces[card_id] = gen._modal_option_names([card], {card_id})

    # Emitted ALWAYS, empty surface included: `KleeMod.PrototypeCards` names
    # this class under `#if PROTOTYPE_CARDS`, so a dev build of an empty
    # surface must still compile. An empty surface is the healthy state.
    generated["prototype_roster"] = _roster_source(owners, mode_faces)

    manifest = {
        "_comment": (
            f"Generated by {SCRIPT} from docs/prototype-surface.yaml. "
            "QUARANTINED (R213 B): dev-only, granted by id, in no reward "
            "pool, no release build, no digest and no version stamp. Rows "
            "leave the surface when their slice is accepted or rejected."
        ),
        "quarantine": {
            "namespace": NAMESPACE,
            "compile_flag": "PrototypeCards=true (defines PROTOTYPE_CARDS)",
            "reachable_by": "understudy give_card / scenario `give:` step",
        },
        "generated": sorted(generated.keys() - {"prototype_roster"}),
        "owners": dict(sorted(owners.items())),
        # Named rather than merely emitted, so "did this row's mode faces
        # reach a pool?" is answerable from the manifest -- EB-150 shipped
        # because nothing wrote that question down anywhere.
        "mode_faces": {cid: names
                       for cid, names in sorted(mode_faces.items()) if names},
        # EB-213. Keyed on the row, not on a `docs/<character>-upgrades.yaml`
        # entry, so a row's deletion takes its upgrade with it (R213 B). A
        # declared delta the emitter cannot express stops the run rather than
        # landing here as a flag.
        "upgrades": dict(sorted(upgrades.items())),
        # EB-315. The rows that ship base-only ON PURPOSE, with the reason
        # each states. An id in neither block is a defect the surface's gate
        # (`tier0/tests/test_prototype_surface.py`) reports by name.
        "no_upgrade": dict(sorted(no_upgrade.items())),
    }

    count = len(owners)
    return gen.ProfilePlan(
        generated=generated,
        manifest_src=json.dumps(manifest, indent=2) + gen.NEWLINE,
        stale_label="Prototype ",
        up_to_date="gen_prototype_cards: prototype surface up to date",
        summary=[f"prototype: generated {count} card(s)"]
        + [f"  {card_id} -- {owner}" for card_id, owner in sorted(owners.items())],
    )


def _roster_source(owners: dict[str, str],
                   mode_faces: dict[str, list[str]] | None = None) -> str:
    """`PrototypeRoster.For(characterId)` -- membership, split by owner.

    Split by owner because `CardModel.Pool` supplies the card FRAME and the
    energy icon: a Kokomi prototype resolved through `KleeCardPool` would draw
    with Klee's frame, which is a lie about what is being tested. Each
    character's off-pool builder asks for its own rows.

    A choose-one row's MODE FACES ride here beside it, under the SAME owner,
    for two reasons that agree. The membership one is EB-150: a mode face in
    no pool takes `CardModel.Pool` through MockCardPool inside the choice
    screen's `_Ready()` and soft-locks the turn. The frame one is the same
    argument as the split itself -- the faces are drawn on the choose-a-card
    screen, so they must wear the frame of the card that opened it.
    """
    mode_faces = mode_faces or {}
    fields: list[str] = []
    builders: list[str] = []
    arms: list[str] = []
    for character in sorted(gen.PROFILES):
        ids = sorted(cid for cid, owner in owners.items() if owner == character)
        classes = [gen.pascal(cid) for cid in ids]
        for cid in ids:
            classes.extend(mode_faces.get(cid, []))
        entries = "".join(
            f"{gen.NEWLINE}            ModelDb.Card<{cls}>(),"
            for cls in classes)
        cs = gen.pascal(character)
        fields.append(f"    private static List<CardModel>? _{character};")
        builders.append(
            f"    private static List<CardModel> Build{cs}() =>"
            f"{gen.NEWLINE}        new()"
            f"{gen.NEWLINE}        {{{entries}{gen.NEWLINE}        }};")
        arms.append(
            f'            "{character}" => _{character} ??= Build{cs}(),')
    field_body = gen.NEWLINE_JOIN.join(fields)
    builder_body = (gen.NEWLINE + gen.NEWLINE).join(builders)
    arm_body = gen.NEWLINE_JOIN.join(arms)
    return f'''// <auto-generated>
//     Generated by {SCRIPT} from docs/prototype-surface.yaml.
//     DO NOT EDIT. Edits are lost on the next regen -- change the sheet instead.
//
//     QUARANTINED prototype surface (R213 B). These cards are compiled ONLY
//     under PrototypeCards=true and are handed to each character's OFF-POOL
//     list: in the pool so CardModel.Pool resolves (a poolless card throws
//     "You monster!" on draw), out of GetUnlockedCards so no reward roll and
//     no card transform can ever produce one. The only route in is a grant
//     by id through the understudy scenario tooling.
// </auto-generated>

#nullable enable

using System.Collections.Generic;
using MegaCrit.Sts2.Core.Models;

namespace {NAMESPACE};

public static class PrototypeRoster
{{
    // LAZY, AND PER CHARACTER (`EB-194`). This was one eager
    // `static readonly` dictionary that resolved EVERY character's rows in the
    // type initializer. `ModelDb.Card<T>()` throws KeyNotFoundException until
    // the models are built -- they are `autoAdd: false` and constructed at
    // pool-build time -- and a static constructor that throws POISONS ITS TYPE
    // for the life of the process. So one premature touch (a Harmony postfix on
    // `LocManager.Initialize` reaching in during boot) permanently disabled the
    // whole prototype surface for every character, and no run could start.
    // Building per character on first ask confines a premature touch to the
    // character that made it, and leaves the type recoverable.
{field_body}

{builder_body}

    /// <summary>Prototype rows owned by one character, or none.</summary>
    public static IReadOnlyList<CardModel> For(string characterId) =>
        characterId switch
        {{
{arm_body}
            _ => System.Array.Empty<CardModel>(),
        }};
}}
'''


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="fail if output would change")
    args = ap.parse_args(argv)

    built = plan()

    # EB-283 / EB-277. The last gate, and the only one about what a card LOOKS
    # like: a staged row whose `+` face is printed identically to its base is a
    # campfire choice that does nothing, and it has shipped twice. Raised, not
    # reported, on this file's own standing rule -- a prototype that cannot be
    # TRIED is a build failure, and a card whose upgrade nobody can see cannot
    # be graded on its upgrade.
    #
    # IN `main` AND NOT IN `plan`, because `UPGRADE_DEBT` is keyed to the
    # COMMITTED surface's ids and `plan()` is called by
    # `tier0/tests/test_prototype_surface.py` against a temporary one-row sheet
    # -- which is the emitter under test, not the surface. Both doors that read
    # the real sheet come through here: `--check` (the `prototype-codegen` CI
    # lint) and the write. `tier0/tests/test_prototype_upgrade_visible.py` runs
    # the finder against the committed sheet directly, which is the suite's
    # copy of this gate.
    # The manifest's `upgrades` block IS the effective delta per row (the
    # authored one, or the Prototype-stage default that stood in for it), so
    # the gate reads what was actually registered rather than re-deriving it.
    deltas = json.loads(built.manifest_src)["upgrades"]
    face_findings = upgrade_face_findings(_rows(), deltas, built.generated)
    if face_findings:
        raise SystemExit(
            "gen_prototype_cards: an upgrade that does not show on the "
            "card is an upgrade nobody can grade (`EB-283`):" + gen.NEWLINE
            + gen.NEWLINE.join("  " + f for f in face_findings) + gen.NEWLINE
            + "Give the row an `upgrade:` block that moves a printed "
              "number or keyword, or -- if the Prototype-stage rule "
              "genuinely cannot reach it -- add the id to "
              "`UPGRADE_DEBT` with the reason.")

    if args.check:
        return gen._check_plan(DIR_PROFILE, built)
    gen._write_plan(DIR_PROFILE, built)
    for line in built.summary:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
