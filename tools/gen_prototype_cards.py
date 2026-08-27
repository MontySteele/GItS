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
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import replace
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import tools.gen_klee_cards as gen                            # noqa: E402
from tier0.content.loader import PROTOTYPE_ID_PREFIX          # noqa: E402

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
)


def _profile_for(character_id: str) -> gen.CharacterProfile:
    """The owning character's profile, redirected at the prototype surface.

    `character_id`, `native_element`, `cadence`, `art_loader` and
    `emit_character_identity` are the OWNER's and are not overridden: they are
    what make the emitted card the character's card rather than a generic one.
    Only the four location fields move.
    """
    owner = gen.PROFILES[character_id]
    return replace(
        owner,
        sheet=SHEET,
        out_dir=OUT_DIR,
        manifest=MANIFEST,
        namespace=NAMESPACE,
        generator_script=SCRIPT,
    )


def _rows() -> list[dict]:
    if not SHEET.exists():
        return []
    return yaml.safe_load(SHEET.read_text(encoding="utf-8")) or []


def plan() -> gen.ProfilePlan:
    rows = _rows()
    generated: dict[str, str] = {}
    owners: dict[str, str] = {}
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

    for card in rows:
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
        reason = gen.blocked_reason(card, profile)
        if reason:
            # See the module docstring: a prototype that cannot be emitted
            # cannot be tried, so this is louder than a manifest row.
            raise SystemExit(
                f"gen_prototype_cards: {card_id} is NOT EXPRESSIBLE: {reason}. "
                "A prototype row must be emittable today -- rewrite it inside "
                "the existing grammar, or take the runtime work first.")
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
    lines: list[str] = []
    for character in sorted(gen.PROFILES):
        ids = sorted(cid for cid, owner in owners.items() if owner == character)
        classes = [gen.pascal(cid) for cid in ids]
        for cid in ids:
            classes.extend(mode_faces.get(cid, []))
        entries = "".join(
            f"{gen.NEWLINE}            ModelDb.Card<{cls}>(),"
            for cls in classes)
        lines.append(
            f'        ["{character}"] = new List<CardModel>'
            f"{gen.NEWLINE}        {{{entries}{gen.NEWLINE}        }},")
    body = gen.NEWLINE_JOIN.join(lines)
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
    private static readonly Dictionary<string, List<CardModel>> ByCharacter = new()
    {{
{body}
    }};

    /// <summary>Prototype rows owned by one character, or none.</summary>
    public static IReadOnlyList<CardModel> For(string characterId) =>
        ByCharacter.TryGetValue(characterId, out var cards)
            ? cards
            : new List<CardModel>();
}}
'''


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="fail if output would change")
    args = ap.parse_args(argv)

    built = plan()
    if args.check:
        return gen._check_plan(DIR_PROFILE, built)
    gen._write_plan(DIR_PROFILE, built)
    for line in built.summary:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
