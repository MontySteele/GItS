"""EB-118 — the card CONNECTIVITY instrument.

WHAT THIS MEASURES, AND WHAT IT DOES NOT
----------------------------------------
Connectivity is "how much of the rest of the game does this card touch".
A card that deals 7 and stops touches nothing. A card that reads the
exhaust pile, asks you to pick a discard, and pays a meter three other
cards also spend is connected in four different directions. This tool
counts those directions, per card and per pool, from the SHEETS ONLY.

It is deterministic and it is a READ. No run count, no random seed, no
combat, no draft. Nothing here moves `RUNTEMPLATE_VERSION`,
`DRAFTER_VERSION`, `POLICY_VERSION` or `CONSTANTS_VERSION`, because
nothing here is a number any of those stamps govern -- the input is the
card sheets and the classifier below, both of which are versioned by
`VOCAB_VERSION` instead.

THERE IS NO GATE. This registration (the EB-118 packet) carries no
pass/fail threshold and no target share. Anything that reads like a bar
in the output ("share of cards with a shared hook") is a REPORTED
QUANTITY, not a floor, and no code here compares one to a constant.

THE COMPARISON CORPUS IS ALL EIGHT POOLS
-----------------------------------------
Five canon pools (Ironclad, Silent, Defect, Necrobinder, Regent) extracted
from the local game binary -- the same `tools/extract_base_game_pool.py`
route `tools/canon_role_tempo.py` uses, which reads `sts2.dll` through
`klee-mod/local.props` and decompiles it to a temporary tree -- and three
mod pools (Klee, Furina, Kokomi) read out of `docs/*-cards.yaml`.

**If the five canon pools are not all present, this tool prints an
explicitly incomplete, MOD-ONLY diagnostic report.** It does not print a
canon comparison and it does not derive a threshold from three pools. A
fresh clone has no `local.props` and no game, so the honest-stop path is
the DEFAULT path, not an error case. `canon_source()` is where that
question is asked, and it is the only place: a checkout is judged on the
binary it can reach, never on whether a gitignored `game_ref/` directory
happens to exist beside it.

ONE CLASSIFIER, TWO EVIDENCE ADAPTERS
--------------------------------------
The vocabulary below (`SHARED_STATES`, `PRIVATE_STATES`, the record
fields, the pool statistics) is frozen and shared by all eight pools.
What differs is where the evidence is read from:

  * the SHEET adapter walks a card row's effect TREE through
    `tools.effect_walk.iter_effects` -- branches included, which is the
    whole reason that module exists -- plus its card-level fields;
  * the CANON adapter walks a decompiled card's structural record
    (`extract.parse_card`) and its source, in the game's own command
    vocabulary, and TAGS THROUGH the powers a card applies by reading
    the power's own decompiled model (the recursion
    `canon_role_tempo.py` established).

Every vocabulary entry carries its canon detection status, and the
report prints it. Three values:

  `grounded`      -- there is a decompiled token this repo reads for that
                     entry. Every C# token named in this file is ENGINE
                     API SURFACE -- a command name, a model override, an
                     enum member -- and never a card name, a number or any
                     other game datum, so no game data enters the repo
                     here.
  `canon_absent`  -- the mechanic is a GItS invention with no base-game
                     analogue (elemental auras and reactions). Zero is
                     the true canon value, not a detection failure.
  `ungrounded`    -- the entry is real, but this repo holds no verified
                     decompiled token for it. It reports UNCLASSIFIED on
                     canon pools rather than a silent zero. NO SHARED
                     ENTRY IS UNGROUNDED TODAY: `junk_create`,
                     `junk_remove` and `enemy_intent` were the last three
                     and were grounded BEFORE the baseline, because packet
                     2.3(4) freezes the classifier once and complete
                     rather than repairing it mid-batch. The status value
                     and its UNCLASSIFIED path stay, because the next
                     vocabulary entry to arrive without a token must still
                     say so.

UNCLASSIFIED IS A FIRST-CLASS OUTPUT
-------------------------------------
An op, predicate, formula spelling, count token, power name or
card-level field the tables below do not know is recorded as
UNCLASSIFIED against the card and printed in the report. It is never
counted as zero and never guessed into the nearest entry. A pool with
UNCLASSIFIED rows has an incomplete classifier, and the report says so
in the place a reader is looking.

USAGE
-----
    python tools/card_connectivity_report.py
    python tools/card_connectivity_report.py --canon-tree <decompiled-dir>
    python tools/card_connectivity_report.py --json out.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools import effect_walk                       # noqa: E402

# v3 (EB-118 sec.4.4, the Explosives Workshop door) adds ONE `POWER_HOOKS`
# row, `bomb_damage_per_rotation`, and nothing else. No shared or private
# ENTRY is added, removed or re-hooked; no record field, pool statistic,
# canon detection token or grounding status moves. The full grammar argument
# -- why the new power joins `universal_verb_power` rather than a new
# verb-triggered class -- lives at that row, where a reader looking up the
# power will find it.
#
# WHY A BUMP AT ALL, AND WHY THE FREEZE IS HONOURED RATHER THAN BROKEN.
# Packet 2.3(4) freezes the classifier for the batch and names the ONE
# permitted repair: revise the vocabulary and re-run BOTH SIDES under a new
# `VOCAB_VERSION`, never repair only the post result. `POWER_HOOKS` is a
# detection table, so adding a row to it is a vocabulary revision even
# though the change is additive -- hence the bump, and hence the rule that
# a `v2` number may only be compared with a `v2` number.
#
# THE RE-RUN IS TRIVIALLY SATISFIED AND THAT IS A PROPERTY, NOT A SHORTCUT.
# `bomb_damage_per_rotation` does not exist in the pre-door sheets, so the
# added row cannot fire on the baseline corpus; every other table is
# untouched; and the only printed text that moves is the version line
# itself, because this decision is recorded in CODE COMMENTS rather than in
# the entry descriptions the report renders. The baseline therefore re-runs
# under `v3` numerically identical to its `v2` reading -- checked by
# re-running it, not assumed (`tier0/tests/test_eb118_connectivity.py`).
#
# v2 grounded the last three ungrounded shared entries (`junk_create`,
# `junk_remove`, `enemy_intent`) and listed the two hookless `CardKeyword`s.
# The vocabulary's ENTRIES are unchanged; what moved is how much of it the
# canon adapter can see. Bumped rather than reused because two reports that
# classify the same pool differently must not both say `v1` -- and no
# baseline has been taken under either, which is the whole point of doing
# this before the freeze (packet 2.3(4)). This is not an `RT/D/P/C` stamp.
#
# ===== v3 IS RATIFIED, AND ITS ONE KNOWN ARTIFACT IS DECLARED HERE =====
# R205 (2026-08-24). There is no v4 now. The artifact, measured at the
# Phase-1-only post-read: `random_enemies` sits in BOTH `RANDOM_TARGETS` and
# `MULTI_TARGETS`, so de-randomizing a placement row (door (a), R204) deletes
# an `enemy_count` shared read along with the randomness -- Klee `random
# placement` fell 20.8% -> 5.6% while shared-hook share fell 66.7% -> 65.3%,
# and two cards lost their only shared hook that way.
#
# THE ARTIFACT IS REAL AND IT IS CORRECTLY SIGNED. `random_enemies` and
# `all_enemies` genuinely DO depend on the enemy population -- how much they
# do is a fact about the board -- and a single aimed target genuinely does
# not. So the column is not lying about those rows. What the vocabulary is
# missing is a DIFFERENT concept, `target_selection`, not a defect in
# `enemy_count`: nothing here models how a target is chosen, only how many
# bodies an effect reaches.
#
# IF TARGET CHOICE IS EVER MODELLED it enters as a NEW vocabulary, roster-wide,
# with BOTH sides re-run under it -- never as a patch to this comparison. A
# reading is comparable only with readings taken under its own
# `VOCAB_VERSION`, and the published Phase-1 post-read stands as published
# (R101b) and is not re-run against a later vocabulary.
VOCAB_VERSION = "eb118-connectivity-v3"

# `recall_to_draw`'s exhaust-pile source (tier0.engine.effects).
RECALL_EXHAUST_SOURCE = "exhaust"

DOCS = REPO / "docs"
MOD_SHEETS = {
    "klee": DOCS / "klee-cards.yaml",
    "furina": DOCS / "furina-cards.yaml",
    "kokomi": DOCS / "kokomi-cards.yaml",
}
# Rarity-only lookups for cards a pool row CREATES but does not contain
# (tokens, statuses, curses). Never classified as pool members.
SIDE_SHEETS = REPO / "tier0" / "content" / "cards"
# The five canon pools, in `tools/canon_role_tempo.py`'s order. All five or
# no comparison -- see `canon_corpus`.
CANON_CHARACTERS = ("Ironclad", "Silent", "Defect", "Necrobinder", "Regent")

GROUNDED, CANON_ABSENT, UNGROUNDED = "grounded", "canon_absent", "ungrounded"

# --- the shared-state vocabulary, versioned WITH the tool --------------------
#
# Every entry is a public/universal state: something a card of any pool
# could in principle read or change, as opposed to a meter one character
# owns. `PRIVATE_STATES` below is the character-owned half, counted
# SEPARATELY rather than excluded.
SHARED_STATES: dict[str, tuple[str, str]] = {
    "hp_ledger": ("HP lost or paid (self-damage, heal, max HP)", GROUNDED),
    "discard_chosen": ("a discard the player picks", GROUNDED),
    "discard_random": ("a discard the game picks", GROUNDED),
    "exhaust_other_chosen": ("Exhaust another card, player's pick", GROUNDED),
    "exhaust_other_random": ("Exhaust another card, game's pick", GROUNDED),
    "self_exhaust": ("the card Exhausts itself", GROUNDED),
    "ethereal": ("the card is Ethereal", GROUNDED),
    "junk_create": ("junk/status/curse creation", GROUNDED),
    "junk_remove": ("junk/status/curse removal", GROUNDED),
    "hand_contents": ("hand contents or hand size", GROUNDED),
    "draw_pile": ("draw-pile contents or size", GROUNDED),
    "discard_pile": ("discard-pile contents or size", GROUNDED),
    "exhaust_pile": ("Exhaust-pile contents or size", GROUNDED),
    "block_held": ("Block held, by either side", GROUNDED),
    "enemy_count": ("how many enemies there are / how many died", GROUNDED),
    "enemy_intent": ("what the enemy intends this turn", GROUNDED),
    "aura_reaction": ("elemental aura / reaction state", CANON_ABSENT),
    "plays_this_turn": ("cards/Attacks/Skills/Companions played this "
                        "turn or combat", GROUNDED),
    "card_identity": ("card identity, type, cost or upgrade state",
                      GROUNDED),
    "card_timing": ("timing fields: X, Retain, Innate", GROUNDED),
    "universal_verb_power": ("a Power that modifies a universal verb -- "
                             "playing, drawing, discarding or Exhausting "
                             "ANY eligible card", GROUNDED),
}

# --- the character-private vocabulary ---------------------------------------
#
# The registration names eight mod-side meters (Bombs, Sparks, Encore,
# Fanfare, Salon, Spotlight, Charge, Conscript/Sly). Three entries below
# go beyond that list and each is deliberate, stated rather than smuggled:
#
#   `burst`  -- the engine keeps Kokomi's Burst meter (`burst_energy`,
#               `burst_max`) separate from her Charge bank, and collapsing
#               the two would report one writer:reader ratio for two
#               meters. The registration's "Charge" is these two rows.
#   `kurage` -- the Bake-Kurage is a Kokomi-owned persistent board entity
#               reached by its own ops and powers. It is character-owned
#               by every test the registration's own list applies; leaving
#               it out would file `summon_kurage` under nothing at all.
#   canon    -- `orbs`, `stars`, `osty` are the canon-side character-owned
#               states (Defect's orbs, Regent's Forge/Stars, Necrobinder's
#               summons). Without them every canon card would report zero
#               private hooks by construction and the private half of the
#               comparison would be a tautology.
PRIVATE_STATES: dict[str, tuple[str, str]] = {
    "bombs": ("Klee's Bombs", CANON_ABSENT),
    "sparks": ("Klee's Sparks", CANON_ABSENT),
    "encore": ("Furina's Encore", CANON_ABSENT),
    "fanfare": ("Furina's Fanfare", CANON_ABSENT),
    "salon": ("Furina's Salon members", CANON_ABSENT),
    "spotlight": ("Furina's Spotlight", CANON_ABSENT),
    "charge": ("Kokomi's Charge", CANON_ABSENT),
    "burst": ("Kokomi's Burst meter (the Charge family's spend door)",
              CANON_ABSENT),
    "conscript_sly": ("Conscript / Sly", CANON_ABSENT),
    "kurage": ("the Bake-Kurage summon", CANON_ABSENT),
    "orbs": ("canon: channelled Orbs", GROUNDED),
    "stars": ("canon: Forge / Stars", GROUNDED),
    "osty": ("canon: summoned bodies", GROUNDED),
}

# The choice categories the registration names. `target` is deliberately
# NOT one of them: picking whom to hit is not a non-target selection.
CHOICE_KINDS = ("discard", "exhaust", "pile", "mode", "x_alloc", "queue")


def _hook(scope: str, state: str, direction: str) -> tuple[str, str, str]:
    """One hook. `direction` is read | write | use.

    `use` is a read that also spends, consumes, moves or retrieves the
    state -- the verb `competing_uses` counts. It implies a read.
    """
    return (scope, state, direction)


# --- the sheet adapter: op -> hooks ------------------------------------------
#
# Every key of `tier0.engine.effects.OPS` appears here exactly once.
# `tier0/tests/test_eb118_connectivity.py` pins that both ways, so an op
# added to the engine without an entry here is a red test rather than a
# silent zero. An op with an EMPTY hook list is a classified op that
# touches no vocabulary state (`energy` is the worked example: energy is
# a per-turn allowance, not a state in this vocabulary).
OP_HOOKS: dict[str, list[tuple[str, str, str]]] = {
    # --- damage and defence ---
    "damage": [],                        # refined by target/riders below
    "chain_attack": [_hook("shared", "enemy_count", "read")],
    "block": [_hook("shared", "block_held", "write")],
    "block_next_turn": [_hook("shared", "block_held", "write")],
    # EB-83. The duration-scoped twin writes the SAME shared state as its
    # one-shot sibling, N turns running: the vocabulary asks what state an op
    # moves, not how many times it moves it, and a `turns`-scaled hook would
    # make a longer power look like a wider one.
    "block_at_turn_start": [_hook("shared", "block_held", "write")],
    # QUARANTINED (C.COMPANION_OVERHAUL). Gorou's "Block equal to half the
    # damage dealt": the same `block_held` WRITE its three neighbours make,
    # and nothing else. It reads a per-play damage total, and this vocabulary
    # has no state for that -- `damage` two lines above is `[]` for the same
    # reason, refined by target rather than counted as a state.
    "block_half_damage": [_hook("shared", "block_held", "write")],
    "strip_block": [_hook("shared", "block_held", "use")],
    "heal": [_hook("shared", "hp_ledger", "write")],
    "gain_max_hp": [_hook("shared", "hp_ledger", "write")],
    # --- card flow ---
    "draw": [_hook("shared", "draw_pile", "use"),
             _hook("shared", "hand_contents", "write")],
    "draw_while": [_hook("shared", "draw_pile", "use"),
                   _hook("shared", "hand_contents", "write"),
                   _hook("shared", "card_identity", "read")],
    "draw_to_hand_size": [_hook("shared", "hand_contents", "read"),
                          _hook("shared", "draw_pile", "use")],
    "discard": [_hook("shared", "hand_contents", "use"),
                _hook("shared", "discard_pile", "write")],
    "discard_for_sparks": [_hook("shared", "hand_contents", "use"),
                           _hook("shared", "discard_pile", "write"),
                           _hook("shared", "discard_chosen", "write"),
                           _hook("private", "sparks", "write")],
    "exhaust_from": [_hook("shared", "hand_contents", "use"),
                     _hook("shared", "exhaust_pile", "write")],
    "scry_discard": [_hook("shared", "draw_pile", "use"),
                     _hook("shared", "discard_pile", "write")],
    "recall_to_draw": [_hook("shared", "discard_pile", "use"),
                       _hook("shared", "draw_pile", "write")],
    "autoplay_from_exhaust": [_hook("shared", "exhaust_pile", "use"),
                              _hook("shared", "plays_this_turn", "write"),
                              _hook("shared", "card_identity", "read")],
    "autoplay_from_draw": [_hook("shared", "draw_pile", "use"),
                           _hook("shared", "plays_this_turn", "write")],
    "add_card": [],                      # refined by zone/pool/card below
    "generate_from_pool": [_hook("shared", "hand_contents", "write")],
    "extra_card_screen": [],             # a run-layer seam; no combat state
    "remember_card": [_hook("shared", "hand_contents", "read"),
                      _hook("shared", "card_identity", "read")],
    # --- card identity / timing ---
    "upgrade_in_hand": [_hook("shared", "hand_contents", "read"),
                        _hook("shared", "card_identity", "write")],
    "transform_in_hand": [_hook("shared", "hand_contents", "write"),
                          _hook("shared", "card_identity", "write")],
    "cost_mod": [_hook("shared", "card_identity", "write")],
    "grow_damage": [_hook("shared", "card_identity", "write")],
    "repeat_this": [_hook("shared", "card_identity", "read")],
    "buff_next_attack": [_hook("shared", "card_identity", "write")],
    "grant_sly_this_turn": [_hook("shared", "card_identity", "write"),
                            _hook("shared", "hand_contents", "read"),
                            _hook("private", "conscript_sly", "write")],
    # --- control flow ---
    # The branch node itself moves nothing; its `if:` is classified through
    # PREDICATE_HOOKS and its branches are walked by `iter_effects`.
    "conditional": [],
    # EB-118 sec.5.4. Same shape as `conditional`: the node itself moves
    # nothing and its mode bodies are walked by `iter_effects`. The
    # difference is WHO picks, and that is recorded through CHOICE_OPS
    # below rather than as a hook -- a mode is a play-time selection, not a
    # state.
    "choose_one": [],
    # --- energy ---
    "energy": [],
    "burst_energy": [_hook("private", "burst", "write")],
    # --- auras and reactions ---
    "apply_aura": [_hook("shared", "aura_reaction", "write")],
    "refresh_all_auras": [_hook("shared", "aura_reaction", "use")],
    "swirl": [_hook("shared", "aura_reaction", "use")],
    # --- powers ---
    "apply_power": [],                   # refined by POWER_HOOKS below
    # --- Klee ---
    "place_bomb": [_hook("private", "bombs", "write")],
    "detonate": [_hook("private", "bombs", "use")],
    "move_bombs": [_hook("private", "bombs", "use")],
    "modify_bombs": [_hook("private", "bombs", "use")],
    "chance_bomb_per_detonation": [_hook("private", "bombs", "write")],
    # --- Klee overhaul, slice one (QUARANTINED, C.KLEE_OVERHAUL) ---
    # The arm is C# first and tier0 refuses to resolve these eight, but the
    # connectivity vocabulary is about what state an op MOVES, which the
    # printed rule already settles (`klee-brief-2026-09-01.md` sec.3) and which
    # does not wait on an implementation. `set_off` also mints Sparks, so it
    # writes the bank as well as spending the pile -- that is rule 4, and it is
    # the whole reason the two loops connect.
    "set_off": [_hook("private", "bombs", "use"),
                _hook("private", "sparks", "write")],
    "plant_bomb": [_hook("private", "bombs", "write")],
    "grow_bombs": [_hook("private", "bombs", "use")],
    "merge_bombs": [_hook("private", "bombs", "use")],
    "remove_bomb_for_block": [_hook("private", "bombs", "use"),
                              _hook("shared", "block_held", "write")],
    "damage_set_off_total": [_hook("private", "bombs", "read")],
    "multiply_set_off": [_hook("private", "bombs", "read")],
    "draw_per_set_off": [_hook("private", "bombs", "read"),
                         _hook("shared", "draw_pile", "use"),
                         _hook("shared", "hand_contents", "write")],
    # R244's Alice's Introduction Magic. It moves no meter and no pile: it
    # READS the hand and WRITES what those cards ARE -- "all cards in your hand
    # count as Hexerei cards this turn" is a change of card identity, which is
    # a shared state this vocabulary already has a name for. Filing it under
    # `bombs` because a witch may later plant one would classify the payoff
    # rather than the op.
    "hexerei_mark_hand": [_hook("shared", "hand_contents", "read"),
                          _hook("shared", "card_identity", "write")],
    "gain_spark": [_hook("private", "sparks", "write")],
    # A competing use for the bank, mirroring spend_encore: the Sparks paid
    # here are Sparks the threshold cash-out no longer reaches (packet 4.5).
    "spend_spark": [_hook("private", "sparks", "use")],
    # --- Furina ---
    "gain_encore": [_hook("private", "encore", "write")],
    "spend_encore": [_hook("private", "encore", "use")],
    "gain_fanfare_floor": [_hook("private", "fanfare", "write")],
    "raise_fanfare_cap": [_hook("private", "fanfare", "write")],
    "crash_fanfare": [_hook("private", "fanfare", "use")],
    # QUARANTINED (R213 B, the Furina reframe's drain slice). The same
    # competing USE `crash_fanfare` above makes, and for the same
    # reason: the meter is spent, so a second drain in one turn finds
    # nothing. What follows it on the card reads the amount taken,
    # which is a per-play number and not a state in this vocabulary.
    "drain_fanfare": [_hook("private", "fanfare", "use")],
    "salon_bow": [_hook("private", "salon", "use")],
    # EB-118 5.5. Rotate is a pure REORDER: it consumes nothing, so it is a
    # write to the private board (which performer the FIFO end offers next)
    # and not a competing use of it.
    "salon_rotate": [_hook("private", "salon", "write")],
    # Perform-now runs the standard member action, upkeep included, so it
    # spends the stage AND the Encore that pays for it -- the same two
    # competing uses the turn-start tick makes, taken on demand.
    "salon_perform": [_hook("private", "salon", "use"),
                      _hook("private", "encore", "use")],
    "spotlight_designate": [_hook("private", "spotlight", "write")],
    "copy_spotlighted_in_hand": [_hook("private", "spotlight", "read"),
                                 _hook("shared", "hand_contents", "write"),
                                 _hook("shared", "card_identity", "read")],
    "generate_guest_star": [_hook("private", "salon", "write"),
                            _hook("shared", "hand_contents", "write")],
    "copy_companion_in_hand": [_hook("shared", "hand_contents", "use"),
                               _hook("shared", "card_identity", "read")],
    "replay_next_companion": [_hook("shared", "plays_this_turn", "write")],
    "copy_companions_played_this_combat": [
        _hook("shared", "plays_this_turn", "use"),
        _hook("shared", "hand_contents", "write")],
    # --- Kokomi ---
    "gain_charge": [_hook("private", "charge", "write")],
    # R213 E1, QUARANTINED. A competing USE of the bank, mirroring
    # spend_spark: Charge paid here is Charge her readers no longer read.
    # Nothing shipped prints it -- the op exists for the prototype surface --
    # but the table is total by construction and a missing row is a finding.
    "spend_charge": [_hook("private", "charge", "use")],
    "conscript": [_hook("private", "conscript_sly", "write"),
                  _hook("shared", "hand_contents", "use"),
                  _hook("shared", "card_identity", "write")],
    "summon_kurage": [_hook("private", "kurage", "write")],
    # Kurage memory v3, QUARANTINED. It USES the bank (the front's price is
    # spent) and it USES the jellyfish, which is what acts on the memory.
    # Nothing shipped prints it -- the op exists for the prototype surface --
    # but the table is total by construction and a missing row is a finding.
    "play_front_memory": [_hook("private", "charge", "use"),
                          _hook("private", "kurage", "use")],
    # --- Kokomi overhaul, DRAFT 6 (QUARANTINED, C.KOKOMI_OVERHAUL) ---
    # The arm is C# first and tier0 refuses to resolve these, but the
    # connectivity vocabulary is about what state an op MOVES, which the
    # printed rule already settles (`kokomi-brief-2026-09-01.md` draft 6 sec.2)
    # and which does not wait on an implementation -- the same argument the
    # Klee arm's eight make one block up.
    #
    # THE PLAN QUEUE IS FILED UNDER `kurage`, and that is a decision rather
    # than a shortcut. The vocabulary is FROZEN at v3 by
    # `test_v3_added_exactly_one_power_row_and_no_vocabulary_entry`, which
    # exists so a baseline re-run's relabel-only argument holds -- minting a
    # `plan_queue` entry would break that argument, and a measurement-law
    # change is not a build branch's to take. Filing it under the jellyfish is
    # the honest reading available and a better one than draft 2 had: rule 1
    # says the Bake-Kurage is WHERE A PLAN IS SENT, so the queue really is the
    # jellyfish's own state.
    "mend": [_hook("shared", "hp_ledger", "write")],
    # Sango Isshin's now-line. Damage, refined by target below like every other
    # damage row -- the Max-HP read moves nothing.
    "damage_quarter_max_hp": [],
    # A cost change, which is what `cost_mod` is filed under.
    "next_companion_discount": [_hook("shared", "card_identity", "write")],
    # Cleansing Wave takes a debuff off HER. The nearest grounded entry is the
    # HP ledger's sibling for statuses, which this vocabulary does not have --
    # so it is EMPTY and disclosed, on `plan`'s own argument below.
    "remove_debuff": [],
    # Change of Plans pulls one Plan forward: it USES the queue and nothing
    # else. What the Plan then does is the Plan's own row.
    "carry_out_front_plan": [_hook("private", "kurage", "use")],
    # Moon's Reflection reads the exhaust pile and writes the queue.
    "plan_from_exhaust": [_hook("shared", "exhaust_pile", "use"),
                          _hook("private", "kurage", "write")],
    # THE PLAN-ONLY CLAUSES. `plan_twice` is a modifier on the queue's own
    # resolution, so it writes the jellyfish; the per-Companion hit reads a
    # per-turn count this vocabulary has no entry for and is damage otherwise,
    # so it is `plays_this_turn` read and nothing else.
    "plan_twice": [_hook("private", "kurage", "write")],
    "damage_per_companion_last_turn": [
        _hook("shared", "plays_this_turn", "read")],
    # Crystal Collapse (R236) READS the same shared play stream the count above
    # reads -- "the last other Companion card you played this turn" -- and then
    # resolves a card, which is `plays_this_turn` WRITE the way every free play
    # in this table is. It does not touch the queue: the Plan it rides was
    # written by the ordinary Plan machinery.
    "play_copy_of_companion": [
        _hook("shared", "plays_this_turn", "read"),
        _hook("shared", "plays_this_turn", "write")],
    # Tide Wall (`EB-335`) READS the morning's own depth off the jellyfish --
    # the queue it is being drained from -- and pays Block, which this
    # vocabulary carries as a private write nowhere; Block is the player's own
    # pool and no other Block op declares a hook for it.
    "block_per_plan_this_morning": [_hook("private", "kurage", "read")],
}

# Ops whose value arrives at a card the player PICKS, through the pilot's
# own selection surface (`_worst_card` / `_best_card` /
# `_best_upgrade_target` in tier0/engine/effects.py). That surface is the
# engine's stand-in for a play-time choice, which is exactly what
# `chosen_actions` counts -- so membership here is read off the engine,
# not off taste. Value is the choice KIND.
CHOICE_OPS: dict[str, str] = {
    "discard_for_sparks": "discard",
    "scry_discard": "pile",
    "recall_to_draw": "queue",
    "remember_card": "pile",
    "grant_sly_this_turn": "pile",
    "choose_one": "mode",
    "spotlight_designate": "mode",
    "conscript": "mode",
    "extra_card_screen": "pile",
}

# Mod powers. Each entry says what the power READS and what it CHANGES;
# a power missing from this table is UNCLASSIFIED, never zero. Debuffs
# that only shrink the enemy's own output (weak, vulnerable, frail) carry
# no vocabulary hook and are listed with an empty tuple, the same way
# `energy` is.
POWER_HOOKS: dict[str, list[tuple[str, str, str]]] = {
    "weak": [], "vulnerable": [], "frail": [],
    "strength": [], "dexterity": [],
    "next_attack_up": [_hook("shared", "card_identity", "write")],
    # Klee
    "bomb_damage_up": [_hook("private", "bombs", "use")],
    # EB-118 sec.4.4 -- Explosives Workshop's install after the conversion,
    # and the one row `VOCAB_VERSION` v3 exists for.
    #
    # WHY v2 REPORTED IT UNCLASSIFIED, precisely. This table is keyed by
    # power NAME, so ANY new power is UNCLASSIFIED on arrival whatever its
    # grammar. That name gap is the mechanical reason the gate went red. It
    # is not the interesting question, and it is worth separating from the
    # one that is, because the two have different answers.
    #
    # THE GRAMMAR QUESTION. The power is TRIGGERED by a universal verb --
    # the first discard OR Exhaust of each turn, with no filter on the card
    # that leaves -- and it pays into a CHARACTER-PRIVATE meter. No previous
    # entry had that combination, so the choice was a new verb-TRIGGERED
    # shared entry against the existing `universal_verb_power`.
    #
    # IT IS `universal_verb_power`, DERIVED FROM THIS VOCABULARY'S OWN
    # CONVENTIONS RATHER THAN FROM THAT ENTRY'S ONE-LINE PROSE. Read
    # literally, "a Power that MODIFIES a universal verb" would exclude a
    # trigger -- but it would also exclude three of the four powers already
    # in the class, so it is the prose that is narrow, not the class. Three
    # independent facts in this file say so and they agree:
    #
    #   (1) MEMBERSHIP AS PRACTISED. `feel_no_pain` and `dark_embrace` are
    #       bodies inside `refpowers.after_card_exhausted` -- pure triggers
    #       on the Exhaust verb. `first_attack_draw` fires on the played-card
    #       path gated `attacks_played_this_turn == 1`: a trigger on the play
    #       verb WITH A ONCE-PER-TURN LATCH, which is this power's structural
    #       twin. Only `zero_cost_attacks_up` modifies a verb's arithmetic.
    #       The class as practised is "a rider a card installs on a universal
    #       verb", and that is what this power is.
    #   (2) THE CANON DETECTOR. `CANON_UNIVERSAL_VERB` -- the token set that
    #       decides this entry on all five canon pools -- is a pure TRIGGER
    #       vocabulary: AfterCardDiscarded, AfterCardExhausted,
    #       AfterCardPlayed, AfterCardDrawn, the hand-draw pair. The C# twin
    #       of this power (`ExplosivesWorkshopPower`) overrides
    #       `AfterCardDiscarded` and `AfterCardExhausted`, so a base-game
    #       power of exactly this shape is classified here ALREADY, under
    #       `v2`, with no vocabulary change at all.
    #   (3) ONE CLASSIFIER, TWO EVIDENCE ADAPTERS -- this tool's own premise.
    #       A sheet-only trigger class would make the two adapters disagree
    #       about the same mechanic, which is the one thing the premise
    #       forbids.
    #
    # THE REJECTED ALTERNATIVE, recorded because it was close. A separate
    # `universal_verb_trigger` entry is only honest if the three existing
    # triggers MOVE into it. Moving them renumbers the paired baseline's
    # shared writer:reader table, which the v3 acceptance check (relabel
    # only) forbids outright. Adding the class for this card ALONE -- inside
    # the batch that changed this card -- is precisely the failure the freeze
    # exists to prevent: two identical shapes in two classes, sorted by which
    # side of a batch they arrived on, with the newer one's label chosen by
    # the party that wants it to read as connected.
    #
    # THE HOOKS, each derived and none asserted:
    #   * `bombs use` -- the SAME hook `bomb_damage_up` carries directly
    #     above, because that is the stat this power increments (one
    #     bomb-damage number, so a Bomb armed before a trigger and one armed
    #     after agree). Carrying it verbatim is what makes this card's
    #     pre/post connectivity diff exactly the verb hooks it GAINED.
    #   * `discard_pile read` / `exhaust_pile read` -- it watches both event
    #     families. `feel_no_pain` and `dark_embrace` already encode "watches
    #     Exhausts" as `exhaust_pile read`; the discard half is the same
    #     encoding on the other pile.
    #   * `universal_verb_power write` -- the rider itself, and the ONLY
    #     source of this card's `external_reach`. That flag is derived
    #     through `UNIVERSAL_VERB_POWERS` below FROM these hooks; no line
    #     anywhere sets it for this power by hand. It comes out true for the
    #     reason the entry names -- a companion, a colorless card, an Ancient
    #     or a Status can be the card that leaves, because sec.4.4 puts no
    #     filter on the victim and names Klee's status-exhaust route as a
    #     trigger in terms.
    "bomb_damage_per_rotation": [_hook("private", "bombs", "use"),
                                 _hook("shared", "discard_pile", "read"),
                                 _hook("shared", "exhaust_pile", "read"),
                                 _hook("shared", "universal_verb_power",
                                       "write")],
    "detonation_splash": [_hook("private", "bombs", "read"),
                          _hook("shared", "enemy_count", "read")],
    "detonation_vuln": [_hook("private", "bombs", "read")],
    "bomb_and_spark_per_turn": [_hook("private", "bombs", "write"),
                                _hook("private", "sparks", "write")],
    "spark_per_turn": [_hook("private", "sparks", "write")],
    "sparks_n_splash": [_hook("private", "sparks", "read")],
    "spark_threshold_down": [_hook("private", "sparks", "read")],
    "zero_cost_attacks_up": [_hook("shared", "card_identity", "read"),
                             _hook("shared", "universal_verb_power",
                                   "write")],
    "reaction_bonus_spark_energy": [_hook("shared", "aura_reaction", "read"),
                                    _hook("private", "sparks", "write")],
    "amp_reaction_up": [_hook("shared", "aura_reaction", "read")],
    # Furina — Salon
    "salon_member": [_hook("private", "salon", "write")],
    "salon_cap_up": [_hook("private", "salon", "write")],
    "salon_damage_up": [_hook("private", "salon", "read")],
    "salon_bow_block": [_hook("private", "salon", "read"),
                        _hook("shared", "block_held", "write")],
    "salon_bow_encore": [_hook("private", "salon", "read"),
                         _hook("private", "encore", "write")],
    "salon_deploy_block": [_hook("private", "salon", "read"),
                           _hook("shared", "block_held", "write")],
    # Furina — Spotlight
    "spotlight_mult_bonus": [_hook("private", "spotlight", "read"),
                             _hook("shared", "card_identity", "write")],
    "spotlight_mult_bonus_turn": [_hook("private", "spotlight", "read"),
                                  _hook("shared", "card_identity", "write")],
    "spotlight_flat_damage": [_hook("private", "spotlight", "read"),
                              _hook("shared", "card_identity", "write")],
    "spotlight_flat_damage_turn": [_hook("private", "spotlight", "read"),
                                   _hook("shared", "card_identity", "write")],
    "spotlight_discount": [_hook("private", "spotlight", "read"),
                           _hook("shared", "card_identity", "write")],
    "spotlight_draw": [_hook("private", "spotlight", "read"),
                       _hook("shared", "draw_pile", "use"),
                       _hook("shared", "hand_contents", "write")],
    "spotlight_encore_first": [_hook("private", "spotlight", "read"),
                               _hook("private", "encore", "write")],
    "ovation_spend_boost": [_hook("private", "encore", "read"),
                            _hook("private", "spotlight", "write")],
    # Furina — Fanfare and the universal-verb riders
    "fanfare_delta_block": [_hook("private", "fanfare", "read"),
                            _hook("shared", "block_held", "write")],
    "fanfare_attack_per10": [_hook("private", "fanfare", "read"),
                             _hook("shared", "card_identity", "write")],
    "first_attack_draw": [_hook("shared", "plays_this_turn", "read"),
                          _hook("shared", "draw_pile", "use"),
                          _hook("shared", "universal_verb_power", "write")],
    "encore_spend_draw": [_hook("private", "encore", "read"),
                          _hook("shared", "draw_pile", "use")],
    "cross_examination": [_hook("shared", "aura_reaction", "read")],
    # Kokomi
    "kurage_ward": [_hook("private", "kurage", "read"),
                    _hook("shared", "block_held", "write")],
    "kurage_amp": [_hook("private", "kurage", "read")],
    "ceremonial_garment": [_hook("private", "charge", "read"),
                           _hook("shared", "block_held", "write")],
    "prevent_exhaust_ward": [_hook("shared", "hp_ledger", "write"),
                             _hook("shared", "draw_pile", "use"),
                             _hook("shared", "exhaust_pile", "write")],
    # base-game parity powers carried on our sheets
    "feel_no_pain": [_hook("shared", "exhaust_pile", "read"),
                     _hook("shared", "block_held", "write"),
                     _hook("shared", "universal_verb_power", "write")],
    "dark_embrace": [_hook("shared", "exhaust_pile", "read"),
                     _hook("shared", "draw_pile", "use"),
                     _hook("shared", "universal_verb_power", "write")],
    "metallicize": [_hook("shared", "block_held", "write")],
}

# Powers whose rider fires on a UNIVERSAL VERB -- playing, drawing,
# discarding or Exhausting ANY eligible card, ours or not. A card that
# applies one of these reaches outside its own pool by construction.
UNIVERSAL_VERB_POWERS = tuple(
    name for name, hooks in POWER_HOOKS.items()
    if any(h[1] == "universal_verb_power" for h in hooks))

# Named formula spellings. Unknown spelling -> UNCLASSIFIED.
FORMULA_HOOKS: dict[str, list[tuple[str, str, str]]] = {
    "1_per_1_fanfare": [_hook("private", "fanfare", "read")],
    "1_per_2_fanfare": [_hook("private", "fanfare", "read")],
    "1_per_4_fanfare": [_hook("private", "fanfare", "read")],
    "1_per_3_encore": [_hook("private", "encore", "read")],
    "1_per_2_charge": [_hook("private", "charge", "read")],
    "2_per_salon_member": [_hook("private", "salon", "read")],
    "2_plus_sparks": [_hook("private", "sparks", "read")],
    "2_per_detonation_this_combat": [_hook("private", "bombs", "read")],
    "2_per_companion_played_this_turn": [
        _hook("shared", "plays_this_turn", "read")],
    "per_aura": [_hook("shared", "aura_reaction", "read")],
}

# `_count` tokens (tier0/engine/effects.py) -- what a `{base, per, count}`
# formula or a string `amount`/`times` counts. Unknown token ->
# UNCLASSIFIED. `enemy_poison_total` is deliberately absent: enemy poison
# is a real engine token with NO entry in this vocabulary, so it reports
# UNCLASSIFIED, which is the honest answer and not a zero.
_IDENTITY_OF_THE_SELECTION = [_hook("shared", "exhaust_pile", "read"),
                               _hook("shared", "card_identity", "read")]

COUNT_HOOKS: dict[str, list[tuple[str, str, str]]] = {
    # EB-118 6.3: the selection the resolving card just made. Every one of
    # these reads a card that is now in the exhaust pile, and all but `size`
    # read a PRINTED identity field off it (cost, type, ownership, upgrade
    # state) -- which is the whole point of the grammar: the card you chose
    # tells this card what to do.
    "exhaust_selection_size": [_hook("shared", "exhaust_pile", "read")],
    "exhaust_selection_cost": _IDENTITY_OF_THE_SELECTION,
    "exhaust_selection_attacks": _IDENTITY_OF_THE_SELECTION,
    "exhaust_selection_skills": _IDENTITY_OF_THE_SELECTION,
    "exhaust_selection_powers": _IDENTITY_OF_THE_SELECTION,
    "exhaust_selection_upgraded": _IDENTITY_OF_THE_SELECTION,
    "exhaust_selection_companions": _IDENTITY_OF_THE_SELECTION,
    "exhaust_selection_personal": _IDENTITY_OF_THE_SELECTION,
    # EB-118 5.5's reward half: what the NEXT performer's act is worth right
    # now. Reads the private queue AND the Encore bank, because the value it
    # returns is the one the stage can currently pay for.
    "leftmost_salon_act": [_hook("private", "salon", "read"),
                           _hook("private", "encore", "read")],
    "exhaust_pile": [_hook("shared", "exhaust_pile", "read")],
    "exhausted_this_card": [_hook("shared", "exhaust_pile", "read")],
    "player_block": [_hook("shared", "block_held", "read")],
    "block_gained_this_card": [_hook("shared", "block_held", "read")],
    "hand_size": [_hook("shared", "hand_contents", "read")],
    "other_cards_in_hand": [_hook("shared", "hand_contents", "read")],
    "attacks_in_hand": [_hook("shared", "hand_contents", "read"),
                        _hook("shared", "card_identity", "read")],
    "skills_in_hand": [_hook("shared", "hand_contents", "read"),
                       _hook("shared", "card_identity", "read")],
    "strike_cards": [_hook("shared", "card_identity", "read")],
    "player_damage_events": [_hook("shared", "hp_ledger", "read")],
    "attacks_played_this_turn": [_hook("shared", "plays_this_turn", "read")],
    "cards_drawn_this_combat": [_hook("shared", "draw_pile", "read")],
    "discards_this_turn": [_hook("shared", "discard_pile", "read")],
    "discards_this_card": [_hook("shared", "discard_pile", "read")],
    "salon_members": [_hook("private", "salon", "read")],
}

# `if:` predicates. The `_at_least_N` families are matched by prefix, so a
# new threshold on a known meter is classified and a new METER is not.
PREDICATE_HOOKS: dict[str, list[tuple[str, str, str]]] = {
    "this_cost_zero": [_hook("shared", "card_identity", "read")],
    "has_spark": [_hook("private", "sparks", "read")],
    "target_has_nonpyro_aura": [_hook("shared", "aura_reaction", "read")],
    # Same shared surface, same direction: C2 (R189) widened WHICH auras
    # count, not what the predicate touches.
    "target_has_aura": [_hook("shared", "aura_reaction", "read")],
    "reaction_triggered_by_this": [_hook("shared", "aura_reaction", "read")],
    "reaction_triggered_this_turn": [_hook("shared", "aura_reaction", "read")],
    "killed_target": [_hook("shared", "enemy_count", "read")],
    "killed_target_fatal": [_hook("shared", "enemy_count", "read")],
    "enemy_intends_attack": [_hook("shared", "enemy_intent", "read")],
    "drew_skill_this_card": [_hook("shared", "draw_pile", "read"),
                             _hook("shared", "card_identity", "read")],
    "card_exhausted_this_turn": [_hook("shared", "exhaust_pile", "read")],
    "exhausted_this_card": [_hook("shared", "exhaust_pile", "read")],
    "hp_lost_this_turn": [_hook("shared", "hp_ledger", "read")],
    "has_salon_members": [_hook("private", "salon", "read")],
    # EB-118 6.3. The yes/no and closed-vocabulary forms of the selection
    # read; the two integer forms live in PREDICATE_PREFIXES above.
    "exhaust_selection_has_companion": _IDENTITY_OF_THE_SELECTION,
    "exhaust_selection_has_personal": _IDENTITY_OF_THE_SELECTION,
    "exhaust_selection_has_type_attack": _IDENTITY_OF_THE_SELECTION,
    "exhaust_selection_has_type_skill": _IDENTITY_OF_THE_SELECTION,
    "exhaust_selection_has_type_power": _IDENTITY_OF_THE_SELECTION,
    "spotlight_set": [_hook("private", "spotlight", "read")],
    "spotlight_moved_this_turn": [_hook("private", "spotlight", "read")],
    "spotlight_unmoved_this_combat": [_hook("private", "spotlight", "read")],
    "spotlighted_card_played_this_turn": [
        _hook("private", "spotlight", "read"),
        _hook("shared", "plays_this_turn", "read")],
}
PREDICATE_PREFIXES: dict[str, list[tuple[str, str, str]]] = {
    "encore_at_least_": [_hook("private", "encore", "read")],
    "fanfare_at_least_": [_hook("private", "fanfare", "read")],
    "charge_at_least_": [_hook("private", "charge", "read")],
    "exhaust_pile_at_least_": [_hook("shared", "exhaust_pile", "read")],
    # EB-118 6.3. The integer forms; the closed-vocabulary and yes/no forms
    # are named entries in PREDICATE_HOOKS, because the prefix path here
    # only accepts a digit argument.
    "exhaust_selection_cost_at_least_": [
        _hook("shared", "exhaust_pile", "read"),
        _hook("shared", "card_identity", "read")],
    "exhaust_selection_size_at_least_": [
        _hook("shared", "exhaust_pile", "read")],
}

# Prefixes whose argument is a NAME, not an integer. Kept separate from
# PREDICATE_PREFIXES above because that table's match requires a digit
# argument -- deliberately, so a typo'd `fanfare_at_least_ten` reports
# UNCLASSIFIED here rather than being waved through. These get the same
# strictness from a closed argument list instead: the engine validates the
# same vocabularies at load (`C.SALON_MEMBERS`, `effects.CARD_TYPES`), so a
# name outside them cannot reach a sheet, and one that appears here anyway
# is a drift signal worth an UNCLASSIFIED.
NAMED_ARG_PREFIXES: dict[str, tuple[frozenset, list]] = {
    # EB-118 5.5: WHICH performer is next -- a read of the private queue.
    "leftmost_salon_member_": (
        frozenset({"chevalmarin", "crabaletta", "usher"}),
        [_hook("private", "salon", "read")]),
}

# Card-level fields the sheets carry. A field not listed here is
# UNCLASSIFIED at the card level. The ones with hooks are printed rules;
# the rest are bookkeeping the connectivity question does not ask about.
CARD_FIELD_HOOKS: dict[str, list[tuple[str, str, str]]] = {
    "exhaust": [_hook("shared", "self_exhaust", "write")],
    "ethereal": [_hook("shared", "ethereal", "write")],
    "retain": [_hook("shared", "card_timing", "write")],
    "innate": [_hook("shared", "card_timing", "write")],
    "encore_cost": [_hook("private", "encore", "read")],
    "sly": [_hook("private", "conscript_sly", "write")],
}
CARD_FIELDS_NO_HOOK = frozenset({
    "id", "name", "cost", "type", "rarity", "solve", "tempo_band",
    "archetypes", "role", "effects", "register", "kit_card",
    "upgrade", "notes",
})
# `tags:` is the sheets' second printed-rule channel -- Ethereal is spelled
# as a tag, not as a card field (tier0/content/cards/tokens.yaml). Tags with
# no vocabulary hook are listed rather than ignored, so a NEW tag is
# UNCLASSIFIED instead of silently dropped.
TAG_HOOKS: dict[str, list[tuple[str, str, str]]] = {
    "ethereal": [_hook("shared", "ethereal", "write")],
}
TAGS_NO_HOOK = frozenset({"skill_tag", "burst", "focalors", "selector",
                          "strike", "defend"})
# `requires:` gates. Value-keyed, because the gate names the meter.
REQUIRES_HOOKS: dict[str, list[tuple[str, str, str]]] = {
    "burst_energy_full": [_hook("private", "burst", "read")],
}

# `random_enemies` is deliberately in BOTH sets -- it is random AND it is
# multi. The consequence for anyone reading the shared-hook column off a
# de-randomized row is DECLARED at `VOCAB_VERSION` above (R205); read it there
# before concluding this membership is a bug.
RANDOM_TARGETS = frozenset({"random_enemy", "random_enemies"})
MULTI_TARGETS = frozenset({"all_enemies", "random_enemies"})
# The junk rarities a created card can carry. `add_card`/`generate_*` ask
# the loader for the row, so junk creation is read off the created card's
# own rarity rather than from a name list.
JUNK_RARITIES = frozenset({"status", "curse"})


class Unclassified(list):
    """A card's UNCLASSIFIED notes. A list, so `or` reads naturally."""


def _blank_record(pool: str, card_id: str) -> dict:
    return {
        "pool": pool,
        "id": card_id,
        "name": card_id,
        "rarity": "",
        "archetypes": [],
        "shared_reads": set(),
        "shared_writes": set(),
        "private_reads": set(),
        "private_writes": set(),
        "uses": set(),                  # (scope, state) touched with `use`
        "chosen_actions": [],
        "external_reach": False,
        "automatic_value": False,
        "random_damage": False,
        "random_placement": False,
        "unclassified": Unclassified(),
    }


def _apply(record: dict, hooks) -> None:
    for scope, state, direction in hooks:
        table = SHARED_STATES if scope == "shared" else PRIVATE_STATES
        if state not in table:
            record["unclassified"].append(f"unknown {scope} state {state!r}")
            continue
        key = f"{scope}_{'writes' if direction == 'write' else 'reads'}"
        record[key].add(state)
        if direction == "use":
            record["uses"].add((scope, state))


def _note_choice(record: dict, kind: str) -> None:
    if kind not in CHOICE_KINDS:
        record["unclassified"].append(f"unknown choice kind {kind!r}")
        return
    if kind not in record["chosen_actions"]:
        record["chosen_actions"].append(kind)


# --- the sheet adapter ------------------------------------------------------

def _classify_formula(record: dict, value, where: str) -> None:
    """A formula field -- the string family or the `{base, per, count}` dict."""
    if isinstance(value, str):
        hooks = FORMULA_HOOKS.get(value)
        if hooks is None:
            record["unclassified"].append(f"{where}: formula {value!r}")
            return
        _apply(record, hooks)
        record["automatic_value"] = True
        return
    if isinstance(value, dict):
        count = value.get("count")
        hooks = COUNT_HOOKS.get(count) if isinstance(count, str) else None
        if hooks is None:
            record["unclassified"].append(f"{where}: count token {count!r}")
            return
        _apply(record, hooks)
        record["automatic_value"] = True
        return
    record["unclassified"].append(f"{where}: formula of type "
                                  f"{type(value).__name__}")


def _classify_amount(record: dict, value, where: str) -> None:
    """A string `amount`/`times`: either `X` or a `_count` token."""
    # `X` and the `X_plus_N` family (tier0/engine/effects.py::_amount) are
    # the same fact: the number is whatever energy the player poured in.
    if value == "X" or (value.startswith("X_plus_")
                        and value[len("X_plus_"):].isdigit()):
        _apply(record, [_hook("shared", "card_timing", "read")])
        _note_choice(record, "x_alloc")
        return
    hooks = COUNT_HOOKS.get(value)
    if hooks is None:
        record["unclassified"].append(f"{where}: amount token {value!r}")
        return
    _apply(record, hooks)
    if value in EXTERNAL_REACH_READS:
        record["external_reach"] = True
    record["automatic_value"] = True


def _classify_effect(record: dict, fx: dict, junk_rarity) -> None:
    op = fx.get("op")
    if op == effect_walk.SLY_AUTOPLAY_OP:
        _apply(record, [_hook("private", "conscript_sly", "write"),
                        _hook("shared", "plays_this_turn", "write")])
        return
    hooks = OP_HOOKS.get(op)
    if hooks is None:
        record["unclassified"].append(f"unknown op {op!r}")
        return
    if op == "recall_to_draw" and fx.get("from") == RECALL_EXHAUST_SOURCE:
        # EB-118 6.4: `from: exhaust` moves the SOURCE PILE. Substituted at
        # the lookup rather than subtracted after `_apply`, because by then
        # the discard-pile hook is indistinguishable from one another effect
        # on the same card contributed. The returned card also gains Exhaust
        # for the rest of combat -- a write to the pile it just left.
        hooks = [_hook("shared", "exhaust_pile", "use"),
                 _hook("shared", "draw_pile", "write"),
                 _hook("shared", "self_exhaust", "write")]
    _apply(record, hooks)

    target = fx.get("target")
    if target in RANDOM_TARGETS:
        if op == "damage":
            record["random_damage"] = True
        else:
            record["random_placement"] = True
    if target in MULTI_TARGETS or fx.get("scope") == "all_enemies":
        _apply(record, [_hook("shared", "enemy_count", "read")])

    if op == "damage" and target == "self":
        _apply(record, [_hook("shared", "hp_ledger", "write")])
    if "bonus_vs_aura" in fx:
        _apply(record, [_hook("shared", "aura_reaction", "read")])
        record["automatic_value"] = True
    if "bonus_vs_bombed" in fx:
        _apply(record, [_hook("private", "bombs", "read")])
        record["automatic_value"] = True

    for key in ("amount_formula", "bonus_formula", "times_formula",
                "damage_formula"):
        if key in fx:
            _classify_formula(record, fx[key], f"{op}.{key}")
    for key in ("amount", "times"):
        if isinstance(fx.get(key), str):
            _classify_amount(record, fx[key], f"{op}.{key}")

    if op == "apply_power":
        power = fx.get("power")
        power_hooks = POWER_HOOKS.get(power)
        if power_hooks is None:
            record["unclassified"].append(f"unknown power {power!r}")
        else:
            _apply(record, power_hooks)
            if power_hooks:
                record["automatic_value"] = True
            if power in UNIVERSAL_VERB_POWERS:
                record["external_reach"] = True

    if op in ("discard", "exhaust_from"):
        chosen = fx.get("select", "random") == "chosen"
        kind = "discard" if op == "discard" else "exhaust"
        entry = (f"{'discard' if op == 'discard' else 'exhaust_other'}"
                 f"_{'chosen' if chosen else 'random'}")
        _apply(record, [_hook("shared", entry, "write")])
        if chosen:
            _note_choice(record, kind)
        else:
            record["random_placement"] = True
    if op == "discard_for_sparks":
        _note_choice(record, "discard")
    if op == "exhaust_from":
        filt = fx.get("filter")
        if filt == "status":
            _apply(record, [_hook("shared", "junk_remove", "write"),
                            _hook("shared", "card_identity", "read")])
            record["external_reach"] = True
        elif filt == "non_attack":
            _apply(record, [_hook("shared", "card_identity", "read")])
        elif filt is not None:
            record["unclassified"].append(f"exhaust_from.filter {filt!r}")
    if op == "add_card":
        zone = fx.get("zone") or fx.get("to", "discard")
        zone_state = {"hand": "hand_contents", "discard": "discard_pile",
                      "draw": "draw_pile"}.get(zone)
        if zone_state is None:
            record["unclassified"].append(f"add_card.zone {zone!r}")
        else:
            _apply(record, [_hook("shared", zone_state, "write")])
        if "pool" in fx:
            record["random_placement"] = True
            record["external_reach"] = True
        if fx.get("card") == "self":
            _apply(record, [_hook("shared", "card_identity", "read")])
        elif junk_rarity is not None:
            named = fx.get("card_id") or fx.get("card")
            if isinstance(named, str):
                rarity = junk_rarity(named)
                if rarity is None:
                    record["unclassified"].append(
                        f"add_card names an unknown card {named!r}")
                elif rarity in JUNK_RARITIES:
                    _apply(record, [_hook("shared", "junk_create", "write")])
                    record["external_reach"] = True
    if op == "generate_from_pool":
        record["random_placement"] = True
        record["external_reach"] = True
    if op in ("generate_guest_star", "conscript", "copy_companion_in_hand",
              "replay_next_companion",
              "copy_companions_played_this_combat"):
        record["external_reach"] = True
    if op == "generate_guest_star":
        record["random_placement"] = True
    if op == "conscript" and fx.get("mode", "transform") == "transform":
        record["random_placement"] = True
    if op == "cost_mod" and fx.get("scope") == "companion_cards":
        record["external_reach"] = True
    if op == "chance_bomb_per_detonation":
        record["random_placement"] = True

    choice = CHOICE_OPS.get(op)
    if choice:
        _note_choice(record, choice)
    if op == "upgrade_in_hand" and fx.get("scope", "chosen") == "chosen":
        _note_choice(record, "pile")

    if op == "conditional":
        cond = fx.get("if")
        _classify_predicate(record, cond)
        record["automatic_value"] = True


# The reads only a NON-PERSONAL card can satisfy. A card asking whether the
# selection contained a Companion reaches outside the character's own pool
# in exactly the sense `external_reach` names -- the same call the op side
# already makes for `conscript`, `copy_companion_in_hand` and the rest.
EXTERNAL_REACH_READS = frozenset({
    "exhaust_selection_has_companion",
    "exhaust_selection_companions",
})


def _classify_predicate(record: dict, name) -> None:
    if not isinstance(name, str):
        record["unclassified"].append(f"conditional.if {name!r}")
        return
    hooks = PREDICATE_HOOKS.get(name)
    if hooks is None:
        for prefix, pref_hooks in PREDICATE_PREFIXES.items():
            if name.startswith(prefix) and name[len(prefix):].isdigit():
                hooks = pref_hooks
                break
    if hooks is None:
        for prefix, (allowed, pref_hooks) in NAMED_ARG_PREFIXES.items():
            if name.startswith(prefix) and name[len(prefix):] in allowed:
                hooks = pref_hooks
                break
    if hooks is None:
        record["unclassified"].append(f"unknown predicate {name!r}")
        return
    _apply(record, hooks)
    if name in EXTERNAL_REACH_READS:
        record["external_reach"] = True


def classify_row(row: dict, pool: str, junk_rarity=None) -> dict:
    """One SHEET row -> the connectivity record.

    `junk_rarity(card_id) -> rarity | None` resolves a card an `add_card`
    names, so junk creation is read off the created row's own rarity. Pass
    nothing and `add_card` rows report their zone but no junk verdict.
    """
    record = _blank_record(pool, str(row.get("id", "?")))
    record["name"] = row.get("name", record["id"])
    record["rarity"] = str(row.get("rarity", ""))
    record["archetypes"] = list(row.get("archetypes") or [])

    for field, value in row.items():
        if field in CARD_FIELDS_NO_HOOK:
            continue
        if field == "tags":
            for tag in value or ():
                hooks = TAG_HOOKS.get(tag)
                if hooks is not None:
                    _apply(record, hooks)
                elif tag not in TAGS_NO_HOOK:
                    record["unclassified"].append(f"unknown tag {tag!r}")
            continue
        if field == "requires":
            hooks = REQUIRES_HOOKS.get(value)
            if hooks is None:
                record["unclassified"].append(f"requires {value!r}")
            else:
                _apply(record, hooks)
            continue
        hooks = CARD_FIELD_HOOKS.get(field)
        if hooks is None:
            record["unclassified"].append(f"unknown card field {field!r}")
            continue
        if value:
            _apply(record, hooks)

    if isinstance(row.get("cost"), str):
        _classify_amount(record, row["cost"], "card.cost")

    for fx in effect_walk.iter_effects(row.get("effects")):
        _classify_effect(record, fx, junk_rarity)
    # A Sly rider resolves on a DISCARD, not on the play -- still this
    # card's printed rule, and still its connectivity.
    for fx in effect_walk.iter_effects(effect_walk.sly_riders(row)):
        _classify_effect(record, fx, junk_rarity)
    if effect_walk.sly_autoplays(row):
        _apply(record, [_hook("private", "conscript_sly", "write"),
                        _hook("shared", "plays_this_turn", "write")])
    return record


def sheet_rows(path: Path) -> list[dict]:
    rows = yaml.safe_load(path.read_text(encoding="utf-8"))
    return [row for row in rows if isinstance(row, dict)]


def mod_corpus() -> dict[str, list[dict]]:
    """The three mod pools, classified. Sheets only -- no loader, no engine."""
    sheets = {name: sheet_rows(path) for name, path in MOD_SHEETS.items()}
    # A card an `add_card` names is often NOT a pool row -- Fish Blasting
    # creates a Status that lives on the token sheet. Junk creation is read
    # off the created row's own `rarity:`, so the side sheets are consulted
    # for RARITY only and never classified as pool members.
    rarity_by_id = {row["id"]: str(row.get("rarity", ""))
                    for rows in sheets.values() for row in rows
                    if "id" in row}
    for side in sorted(SIDE_SHEETS.glob("*.yaml")):
        for row in sheet_rows(side):
            if "id" in row:
                rarity_by_id.setdefault(row["id"], str(row.get("rarity", "")))

    def junk_rarity(card_id: str):
        return rarity_by_id.get(card_id)

    return {name: [classify_row(row, name, junk_rarity) for row in rows]
            for name, rows in sheets.items()}


# --- the canon adapter ------------------------------------------------------
#
# Every token below already appears in committed repo source
# (tools/extract_base_game_pool.py, tools/canon_role_tempo.py, the
# klee-mod C# tree). Nothing decompiled is added to the repo here.
CANON_SIGNALS: tuple[tuple[re.Pattern, tuple[str, str, str], bool], ...] = (
    # (pattern, hook, sets_automatic_value)
    (re.compile(r"CreatureCmd\.(?:Damage|Heal|GainMaxHp)\b"),
     _hook("shared", "hp_ledger", "write"), False),
    (re.compile(r"CreatureCmd\.GainBlock\b|new (?:Block|CalculatedBlock)Var"),
     _hook("shared", "block_held", "write"), False),
    (re.compile(r"CreatureCmd\.LoseBlock\b"),
     _hook("shared", "block_held", "use"), False),
    (re.compile(r"CardPileCmd\.Draw\b"),
     _hook("shared", "draw_pile", "use"), False),
    (re.compile(r"CardPileCmd\.Draw\b|CardPileCmd\.Add\w*\b"),
     _hook("shared", "hand_contents", "write"), False),
    (re.compile(r"CardCmd\.Discard\w*\b"),
     _hook("shared", "discard_pile", "write"), False),
    (re.compile(r"CardCmd\.Discard\w*\b"),
     _hook("shared", "hand_contents", "use"), False),
    (re.compile(r"CardCmd\.Exhaust\b|CardPileCmd\.\w*Exhaust\w*\b"),
     _hook("shared", "exhaust_pile", "write"), False),
    (re.compile(r"PileType\.Draw\b"),
     _hook("shared", "draw_pile", "read"), True),
    (re.compile(r"PileType\.Discard\b"),
     _hook("shared", "discard_pile", "read"), True),
    (re.compile(r"PileType\.Exhaust\b|\bExhaustPile\b"),
     _hook("shared", "exhaust_pile", "read"), True),
    (re.compile(r"PileType\.Hand\b"),
     _hook("shared", "hand_contents", "read"), True),
    (re.compile(r"CardPileCmd\.AutoPlayFromDrawPile\b"),
     _hook("shared", "draw_pile", "use"), False),
    (re.compile(r"CardCmd\.AutoPlay\b|CardPileCmd\.AutoPlayFromDrawPile\b"),
     _hook("shared", "plays_this_turn", "write"), False),
    (re.compile(r"CombatState\.\w*Count\b"),
     _hook("shared", "plays_this_turn", "read"), True),
    (re.compile(r"CardCmd\.(?:Upgrade|Transform|Enchant)\b|"
                r"ModifyEnergyCost\b"),
     _hook("shared", "card_identity", "write"), False),
    (re.compile(r"\bCardTag\.\w+|\bCardType\.\w+(?!\s*,\s*CardRarity)|"
                r"\bOfType<"),
     _hook("shared", "card_identity", "read"), True),
    (re.compile(r"CardKeyword\.(?:Retain|Innate)\b|HasEnergyCostX\b"),
     _hook("shared", "card_timing", "write"), False),
    (re.compile(r"ResolveEnergyXValue\b"),
     _hook("shared", "card_timing", "read"), False),
    (re.compile(r"TargetType\.AllEnemies\b|HittableEnemies\b|"
                r"WasTargetKilled\b"),
     _hook("shared", "enemy_count", "read"), False),
    (re.compile(r"OrbCmd\.Channel\b"),
     _hook("private", "orbs", "write"), False),
    (re.compile(r"OrbCmd\.(?:Evoke|AddSlots)\b"),
     _hook("private", "orbs", "use"), False),
    (re.compile(r"ForgeCmd\.Forge\b|PlayerCmd\.GainStars\b|\bStars\b"),
     _hook("private", "stars", "write"), False),
    (re.compile(r"OstyCmd\.Summon\b|\bFromOsty\b"),
     _hook("private", "osty", "write"), False),
)
# Play-time selection, in the game's own vocabulary. `CardSelectCmd.*` IS
# the selection screen; which screen decides the choice KIND.
CANON_CHOICES: tuple[tuple[re.Pattern, str], ...] = (
    (re.compile(r"CardSelectCmd\.FromHandForDiscard\b"), "discard"),
    (re.compile(r"CardSelectCmd\.FromHand\b"), "pile"),
    (re.compile(r"CardSelectCmd\.From(?:SimpleGrid|ChooseACardScreen)\b"),
     "pile"),
    (re.compile(r"CardSelectCmd\.(?:PushSelector|UseSelector)\b"), "pile"),
    (re.compile(r"ResolveEnergyXValue\b"), "x_alloc"),
)
CANON_DISCARD = re.compile(r"CardCmd\.Discard\w*\b")
CANON_DISCARD_SELECT = re.compile(r"CardSelectCmd\.FromHandForDiscard\b")
# `CardCmd.Exhaust` on another card. The card's OWN Exhaust is the printed
# keyword and is read off `keywords`, never off this call.
CANON_EXHAUST_OTHER = re.compile(r"CardCmd\.Exhaust\b|"
                                 r"CardPileCmd\.\w*Exhaust\w*\b")
CANON_HAND_SELECT = re.compile(r"CardSelectCmd\.From(?:Hand|SimpleGrid|"
                               r"ChooseACardScreen)\b")
CANON_KEYWORD_HOOKS = {
    "Exhaust": _hook("shared", "self_exhaust", "write"),
    "Ethereal": _hook("shared", "ethereal", "write"),
    "Retain": _hook("shared", "card_timing", "write"),
    "Innate": _hook("shared", "card_timing", "write"),
    "Sly": _hook("private", "conscript_sly", "write"),
}
# The rest of `CardKeyword`, listed rather than ignored -- the same
# classified-but-hookless idiom `TAGS_NO_HOOK` and `CARD_FIELDS_NO_HOOK` use,
# so a keyword the enum grows later is UNCLASSIFIED instead of dropped.
# `Unplayable` is a printed rule that moves nothing BY BEING one: the card is
# never played, so it never reaches a state. `Eternal` refuses deck REMOVAL,
# a run-layer fact this combat vocabulary does not name. `None` is the enum's
# zero and says only that the card carries no keyword.
CANON_KEYWORDS_NO_HOOK = frozenset({"None", "Unplayable", "Eternal"})

# --- junk, in the game's two spellings ---------------------------------------
#
# The base game says "this is a Status or a Curse" in two places and this tool
# reads both, because they answer different questions. A card MODEL declares
# it in its own ctor (`CardRarity.Status` / `CardRarity.Curse`), which is what
# makes a CREATED card junk -- the same route the sheet adapter takes through
# `junk_rarity`, resolved here off the created model's own decompiled source
# instead of off a side sheet. A card that FILTERS for junk tests the TYPE
# instead (`c.Type == CardType.Status`), because the type is the field a pile
# predicate can see.
CANON_JUNK_MODEL = re.compile(r"CardRarity\.(?:Status|Curse)\b")
CANON_JUNK_FILTER = re.compile(r"CardType\.(?:Status|Curse)\b")
# The removal verbs, and the narrow reading of "removal" this tool takes:
# junk LEAVES the deck for good. Exhausting it and transforming it into
# something else both do that; discarding it does not (it comes back next
# shuffle) and neither does drawing it. A junk filter with no removal verb is
# a READER of junk, not a remover, which is the next entry down.
CANON_JUNK_REMOVE = re.compile(r"CardCmd\.(?:Exhaust|Transform)\b")
# `AfterCardGeneratedForCombat` is the game's own "a card just entered this
# combat from nowhere" callback. Gated on a junk filter, it is exactly a READ
# of junk creation -- the card's behaviour is conditioned on junk arriving.
CANON_JUNK_CREATED_HOOK = re.compile(r"\bAfterCardGeneratedForCombat\b")

# --- enemy intent ------------------------------------------------------------
#
# The intent layer is the monster's `NextMove` and the `IntentType`s hanging
# off it; a card that asks what the enemy is about to do reaches for one of
# those names (`klee-mod/KleeCode/Powers/CurtainCallPowers.cs` is this repo's
# own worked example of the read). The WRITE side is `CreatureCmd.Stun`, which
# replaces the move the enemy had telegraphed with a lost turn.
CANON_INTENT_READ = re.compile(r"\bIntentType\.\w+|\.Intents\b|\bNextMove\b")
CANON_INTENT_WRITE = re.compile(r"CreatureCmd\.Stun\b")
# A canon power whose rider fires on a universal verb, recognised off the
# POWER's own decompiled model rather than off a name table: the hook is
# a card-play/draw/discard/exhaust callback on a model that is not a
# debuff. These are the base game's own override names.
CANON_UNIVERSAL_VERB = re.compile(
    r"\b(?:AfterCardPlayed|BeforeCardPlayed|AfterCardDrawn|"
    r"AfterCardDiscarded|AfterCardExhausted|OnCardExhausted|"
    r"AfterHandDraw|BeforeHandDraw)\b")
CANON_POWER_APPLY = re.compile(r"PowerCmd\.Apply<(\w+Power)>")


class CanonReader:
    """Reads and memoises decompiled models by short type name.

    The same object `tools/canon_role_tempo.py::Reader` is, kept separate
    only because this tool must run when that one's outputs do not exist.
    """

    def __init__(self, root: Path):
        self.root = root
        self._cache: dict[str, str] = {}

    def source(self, short_name: str) -> str:
        if short_name not in self._cache:
            paths = sorted(self.root.rglob(f"{short_name}.cs"))
            self._cache[short_name] = (
                paths[0].read_text(encoding="utf-8") if paths else "")
        return self._cache[short_name]


def _classify_canon_junk(record: dict, card: dict, sources: list[str],
                         reader: CanonReader | None) -> None:
    """The junk axis: what a card puts into the deck and what it takes out.

    Creation is read off the CREATED card's own model, never off its name --
    the sheet adapter's rule, kept word for word on this side, because a name
    list would be both game data and a permanent maintenance debt. A model
    this reader cannot open is UNCLASSIFIED, not "not junk".

    Removal and the creation READ both need two tokens agreeing inside ONE
    source: a junk filter and, respectively, a removal verb or the
    card-generated callback. The conjunction is deliberately per-source and
    not over the concatenation -- a card that Exhausts something while a
    Power it applies happens to mention Statuses is not a junk remover, and
    joining the two texts first would say it was.
    """
    for created in card.get("creates") or ():
        model = reader.source(created) if reader else ""
        if not model:
            record["unclassified"].append(
                f"{created}: created card model unreadable, junk verdict "
                "UNCLASSIFIED (not 'not junk')")
            continue
        if CANON_JUNK_MODEL.search(model):
            _apply(record, [_hook("shared", "junk_create", "write")])
            record["external_reach"] = True
    for source in sources:
        if not CANON_JUNK_FILTER.search(source):
            continue
        if CANON_JUNK_REMOVE.search(source):
            _apply(record, [_hook("shared", "junk_remove", "write")])
            record["external_reach"] = True
        if CANON_JUNK_CREATED_HOOK.search(source):
            _apply(record, [_hook("shared", "junk_create", "read")])
            record["external_reach"] = True


def _classify_canon_intent(record: dict, sources: list[str]) -> None:
    """What the enemy intends: read it, or overwrite it with a lost turn."""
    for source in sources:
        if CANON_INTENT_READ.search(source):
            _apply(record, [_hook("shared", "enemy_intent", "read")])
        if CANON_INTENT_WRITE.search(source):
            _apply(record, [_hook("shared", "enemy_intent", "write")])


def classify_canon_card(card: dict, src: str, pool: str,
                        reader: CanonReader | None = None) -> dict:
    """One decompiled canon card -> the SAME record shape as a sheet row."""
    record = _blank_record(pool, card["name"])
    record["name"] = card["name"]
    record["rarity"] = str(card.get("rarity", "")).lower()
    record["archetypes"] = ["generic"]

    for pattern, hook, automatic in CANON_SIGNALS:
        if pattern.search(src):
            _apply(record, [hook])
            if automatic:
                record["automatic_value"] = True
    for keyword in card.get("keywords") or ():
        hook = CANON_KEYWORD_HOOKS.get(keyword)
        if hook is None:
            if keyword not in CANON_KEYWORDS_NO_HOOK:
                record["unclassified"].append(f"CardKeyword.{keyword}")
            continue
        _apply(record, [hook])
    if card.get("target") == "AllEnemies":
        _apply(record, [_hook("shared", "enemy_count", "read")])
    if card.get("calc_vars"):
        record["automatic_value"] = True
    if card.get("creates") or card.get("card_refs"):
        record["external_reach"] = True
    if card.get("mp_only"):
        record["external_reach"] = True

    for pattern, kind in CANON_CHOICES:
        if pattern.search(src):
            _note_choice(record, kind)

    # chosen vs random, on the canon side. The game asks the same question
    # the sheets' `select:` does, and it asks it with a SELECTION SCREEN:
    # a discard behind `CardSelectCmd.FromHandForDiscard` is the player's,
    # and one without any selector is the game's.
    if CANON_DISCARD.search(src):
        chosen = bool(CANON_DISCARD_SELECT.search(src))
        _apply(record, [_hook("shared", "discard_chosen" if chosen
                              else "discard_random", "write")])
        if not chosen:
            record["random_placement"] = True
    if CANON_EXHAUST_OTHER.search(src):
        chosen = bool(CANON_HAND_SELECT.search(src))
        _apply(record, [_hook("shared", "exhaust_other_chosen" if chosen
                              else "exhaust_other_random", "write")])
        if not chosen:
            record["random_placement"] = True

    # The power tag-through: a Power's own model says what verb it rides.
    power_sources: list[str] = []
    for power in sorted(set(CANON_POWER_APPLY.findall(src))):
        power_src = reader.source(power) if reader else ""
        if not power_src:
            record["unclassified"].append(
                f"{power}: model unreadable, rider unclassified")
            continue
        power_sources.append(power_src)
        if CANON_UNIVERSAL_VERB.search(power_src):
            _apply(record, [_hook("shared", "universal_verb_power", "write")])
            record["external_reach"] = True
        for pattern, hook, _automatic in CANON_SIGNALS:
            if pattern.search(power_src):
                _apply(record, [hook])
        record["automatic_value"] = True

    # The two detectors that need more than one token, over the card AND the
    # models of the powers it applies -- a Power is where half the base game's
    # junk-watching lives, so reading only the card would report a silent zero
    # for the card that applies it.
    _classify_canon_junk(record, card, [src] + power_sources, reader)
    _classify_canon_intent(record, [src] + power_sources)

    # The entries this repo holds no verified canon token for. Recorded per
    # card so the pool's UNCLASSIFIED count is honest rather than a zero.
    for state, (_why, status) in SHARED_STATES.items():
        if status == UNGROUNDED:
            record["unclassified"].append(
                f"{state}: no grounded canon token (UNCLASSIFIED, not 0)")
    return record


def canon_source() -> tuple[Path | None, str]:
    """`(sts2.dll, "")` when the canon half is reachable, `(None, why)` when
    it is not. THE capability question, asked in one place.

    What the canon half actually depends on is the BINARY -- read through
    `klee-mod/local.props` and decompiled to a temporary tree -- and never
    `game_ref/`. `game_ref/` holds the *sheet* artifacts other tools emit;
    this one extracts its five pools itself, so a checkout with local.props
    and no `game_ref/` (every DLL-backed worktree) is a checkout that CAN
    print the complete report. Anything asking "can this checkout support
    the canon comparison" -- `canon_corpus` below, and the suite that pins
    which report this checkout prints -- must ask through here, so the
    predicate and the behaviour cannot drift apart.
    """
    try:
        from tools import extract_base_game_pool as extract
    except Exception as exc:                       # pragma: no cover - import
        return None, f"tools.extract_base_game_pool unimportable: {exc}"
    try:
        return extract.game_dll(), ""
    except SystemExit as err:
        return None, f"no local game to read: {err.code}"


def canon_reachable() -> bool:
    """The boolean form of `canon_source`."""
    return canon_source()[0] is not None


def canon_corpus(tree: Path | None = None) -> tuple[dict, list[str]]:
    """({character: [records]}, problems). All five pools, or nothing.

    Never raises on a missing game: a fresh clone has no `game_ref/` and
    the honest-stop path is this function returning `({}, [why])`.
    """
    problems: list[str] = []
    try:
        from tools import extract_base_game_pool as extract
    except Exception as exc:                       # pragma: no cover - import
        return {}, [f"tools.extract_base_game_pool unimportable: {exc}"]

    from contextlib import nullcontext
    if tree is not None:
        if not tree.exists():
            return {}, [f"--canon-tree {tree} does not exist"]
        context = nullcontext(tree)
    else:
        dll, why = canon_source()
        if dll is None:
            return {}, [why]
        context = extract.decompiled_project(dll)

    pools: dict[str, list[dict]] = {}
    try:
        with context as root:
            reader = CanonReader(Path(root))
            for character in CANON_CHARACTERS:
                try:
                    names, sources = extract.read_pool(Path(root), character)
                except SystemExit as err:
                    problems.append(f"{character}: {err.code}")
                    continue
                tokens = set(sources) - set(names)
                rows = []
                for name in names:
                    card = extract.parse_card(sources[name], name, tokens)
                    if card is None:
                        problems.append(
                            f"{character}/{name}: no CardModel ctor found")
                        continue
                    rows.append(classify_canon_card(
                        card, sources[name], character.lower(), reader))
                pools[character.lower()] = rows
    except SystemExit as err:                      # pragma: no cover - tooling
        return {}, problems + [f"decompile failed: {err.code}"]
    missing = [c for c in CANON_CHARACTERS if c.lower() not in pools]
    if missing:
        problems.append("missing canon pools: " + ", ".join(missing))
        return {}, problems
    return pools, problems


# --- pool statistics --------------------------------------------------------

def _pct(part: int, whole: int) -> float:
    return round(100.0 * part / whole, 1) if whole else 0.0


def pool_stats(records: list[dict]) -> dict:
    """Everything the registration asks a pool to report. No thresholds."""
    n = len(records)
    non_basic = [r for r in records if r["rarity"] != "basic"]
    m = len(non_basic)

    # competing_uses is corpus-relative by construction: a state is
    # CONTESTED when two or more distinct cards in the pool spend, consume,
    # move or retrieve it, i.e. when holding it means choosing between
    # downstream uses. Cards touching a contested state carry the flag.
    sinks: dict[tuple[str, str], set[str]] = defaultdict(set)
    for record in records:
        for key in record["uses"]:
            sinks[key].add(record["id"])
    contested = {key for key, who in sinks.items() if len(who) >= 2}
    for record in records:
        touched = ({("shared", s) for s in record["shared_reads"]}
                   | {("shared", s) for s in record["shared_writes"]}
                   | {("private", s) for s in record["private_reads"]}
                   | {("private", s) for s in record["private_writes"]})
        record["competing_uses"] = bool(touched & contested)
        record["automatic_only"] = bool(record["automatic_value"]
                                        and not record["chosen_actions"])
        record["hook_count"] = len(touched)

    writers: dict[str, Counter] = {"shared": Counter(), "private": Counter()}
    readers: dict[str, Counter] = {"shared": Counter(), "private": Counter()}
    for record in records:
        for scope in ("shared", "private"):
            for state in record[f"{scope}_writes"]:
                writers[scope][state] += 1
            for state in record[f"{scope}_reads"]:
                readers[scope][state] += 1

    # Cross-archetype edges: two non-generic plans joined by a state both
    # of them touch. The edge is the STATE's, not any one card's.
    by_state: dict[tuple[str, str], set[str]] = defaultdict(set)
    for record in records:
        plans = [a for a in record["archetypes"] if a != "generic"]
        for scope in ("shared", "private"):
            for state in record[f"{scope}_reads"] | record[f"{scope}_writes"]:
                by_state[(scope, state)].update(plans)
    edges: dict[str, list[str]] = defaultdict(list)
    for (scope, state), plans in by_state.items():
        ordered = sorted(plans)
        for i, left in enumerate(ordered):
            for right in ordered[i + 1:]:
                edges[f"{left}|{right}"].append(f"{scope}:{state}")
    two_plans = [r["id"] for r in records
                 if len({a for a in r["archetypes"] if a != "generic"}) >= 2]

    def share(pred) -> float:
        return _pct(sum(1 for r in non_basic if pred(r)), m)

    hook_hist = Counter(r["hook_count"] for r in records)
    return {
        "n": n,
        "n_non_basic": m,
        "shared_hook_share": share(lambda r: bool(r["shared_reads"]
                                                  or r["shared_writes"])),
        "choice_share": share(lambda r: bool(r["chosen_actions"])),
        "competing_uses_share": share(lambda r: r["competing_uses"]),
        "automatic_only_share": share(lambda r: r["automatic_only"]),
        "external_reach_share": share(lambda r: r["external_reach"]),
        "random_damage_share": share(lambda r: r["random_damage"]),
        "random_placement_share": share(lambda r: r["random_placement"]),
        "shared_ratio": {
            state: {"writers": writers["shared"][state],
                    "readers": readers["shared"][state]}
            for state in sorted(set(writers["shared"]) | set(readers["shared"]))
        },
        "private_ratio": {
            state: {"writers": writers["private"][state],
                    "readers": readers["private"][state]}
            for state in sorted(set(writers["private"])
                                | set(readers["private"]))
        },
        "cross_archetype_edges": {k: sorted(set(v))
                                  for k, v in sorted(edges.items())},
        "cards_in_two_plans": sorted(two_plans),
        "hook_count_distribution": {str(k): hook_hist[k]
                                    for k in sorted(hook_hist)},
        "choice_kinds": dict(Counter(
            kind for r in records for kind in r["chosen_actions"])),
        "unclassified": sorted({f"{r['id']}: {note}" for r in records
                                for note in r["unclassified"]}),
    }


def build_report(canon_tree: Path | None = None) -> dict:
    mod = mod_corpus()
    canon, problems = canon_corpus(canon_tree)
    pools = {name: pool_stats(records) for name, records in mod.items()}
    for name, records in canon.items():
        pools[name] = pool_stats(records)
    return {
        "vocab_version": VOCAB_VERSION,
        "complete": bool(canon),
        "canon_problems": problems,
        "mod_pools": sorted(mod),
        "canon_pools": sorted(canon),
        "pools": pools,
    }


# --- rendering --------------------------------------------------------------

INCOMPLETE_BANNER = (
    "=========================================================\n"
    "  INCOMPLETE REPORT -- MOD POOLS ONLY, NO CANON BASELINE\n"
    "=========================================================\n"
    "The comparison corpus is all EIGHT pools under one frozen\n"
    "classifier. The five canon pools (Ironclad, Silent, Defect,\n"
    "Necrobinder, Regent) are NOT readable here, so what follows is a\n"
    "DIAGNOSTIC of the three mod pools and nothing else. No canon\n"
    "comparison is printed and no threshold is derived from three\n"
    "pools -- the registration forbids both, and a bar drawn from the\n"
    "mod pools alone would be the mod pools grading themselves.\n"
    "Numbers below are readable AGAINST EACH OTHER only.")


def _render_pool(name: str, stats: dict) -> list[str]:
    out = [f"--- {name} ({stats['n']} cards, "
           f"{stats['n_non_basic']} non-basic) ---",
           "  shares over NON-BASIC cards:",
           f"    at least one shared hook      {stats['shared_hook_share']:>6.1f}%",
           f"    a non-target play-time choice {stats['choice_share']:>6.1f}%",
           f"    touches a contested state     {stats['competing_uses_share']:>6.1f}%",
           f"    extra value is automatic only {stats['automatic_only_share']:>6.1f}%",
           f"    external reach                {stats['external_reach_share']:>6.1f}%",
           f"    random damage                 {stats['random_damage_share']:>6.1f}%",
           f"    random placement              {stats['random_placement_share']:>6.1f}%",
           "  writer:reader by SHARED state (cards, not instances):"]
    for state, io in stats["shared_ratio"].items():
        out.append(f"    {state:<24} {io['writers']:>3} W : {io['readers']:>3} R")
    out.append("  writer:reader by PRIVATE state:")
    for state, io in stats["private_ratio"].items():
        out.append(f"    {state:<24} {io['writers']:>3} W : {io['readers']:>3} R")
    if not stats["private_ratio"]:
        out.append("    (none)")
    out.append("  distinct hooks per card: " + ", ".join(
        f"{k}:{v}" for k, v in stats["hook_count_distribution"].items()))
    out.append("  play-time choice kinds: " + (", ".join(
        f"{k}:{v}" for k, v in sorted(stats["choice_kinds"].items()))
        or "(none)"))
    edges = stats["cross_archetype_edges"]
    out.append(f"  cross-archetype edges: {len(edges)}")
    for pair, states in edges.items():
        out.append(f"    {pair:<24} via {', '.join(states)}")
    out.append(f"  cards in two non-generic plans: "
               f"{len(stats['cards_in_two_plans'])}"
               + (" -- " + ", ".join(stats["cards_in_two_plans"])
                  if stats["cards_in_two_plans"] else ""))
    if stats["unclassified"]:
        out.append(f"  UNCLASSIFIED ({len(stats['unclassified'])}) -- "
                   "counted as unknown, never as zero:")
        out.extend(f"    {note}" for note in stats["unclassified"])
    else:
        out.append("  UNCLASSIFIED: none")
    out.append("")
    return out


def render(report: dict) -> str:
    lines = [f"CARD CONNECTIVITY REPORT  (vocabulary {report['vocab_version']})",
             "EB-118. Deterministic, sheets-only, no gate and no threshold.",
             ""]
    if not report["complete"]:
        lines.append(INCOMPLETE_BANNER)
        lines.append("")
        lines.append("why the canon half is missing:")
        for problem in report["canon_problems"] or ["(no reason recorded)"]:
            lines.append(f"  - {problem}")
        lines.append("")
    else:
        lines += ["All eight pools read. Canon pools: "
                  + ", ".join(report["canon_pools"]), ""]
    for name in report["mod_pools"] + report["canon_pools"]:
        lines += _render_pool(name, report["pools"][name])
    lines += ["vocabulary (entry -- canon detection status):"]
    for state, (why, status) in SHARED_STATES.items():
        lines.append(f"  shared  {state:<22} {status:<13} {why}")
    for state, (why, status) in PRIVATE_STATES.items():
        lines.append(f"  private {state:<22} {status:<13} {why}")
    lines.append("")
    return "\n".join(lines)


def _jsonable(report: dict) -> dict:
    return json.loads(json.dumps(report, default=sorted))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--canon-tree", type=Path, default=None,
                    help="an already-decompiled project tree to read the "
                         "five canon pools from")
    ap.add_argument("--json", type=Path, default=None,
                    help="also write the whole report as JSON")
    args = ap.parse_args(argv)
    report = build_report(args.canon_tree)
    print(render(report))
    if args.json:
        args.json.write_text(json.dumps(_jsonable(report), indent=1),
                             encoding="utf-8")
        print(f"wrote {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
