# Klee text pass, held for klee-next (2026-10-08)

The card-text and tooltip conventions pass of 2026-10-08 (conventions review,
"Hygiene Claude can just do") landed on `main` for every kit but Klee. Klee is
frozen at Balance on `main` and her rows move on `klee-next`, so her edits are
written out here, to be applied on `klee-next` after its suite reads. Wording
only: no number, cost, rarity or behaviour moves.

The "now" texts are `origin/klee-next` at the time of writing (ids are stable;
Careful Arrangement is titled Exquisite Compound there). Each edit is to the
row's `description:` in `docs/prototype-surface.yaml`, then a regen.

**When these land, empty the lint's `DEFERRED` table** in
`tools/lint_text_conventions.py` (four entries: Team Effort and Sparkling Burst
for `more-damage`, Treasure Map and Come Back and Play! for `pile-plain`). It
has rot semantics: an entry whose spelling no longer fires fails the gate, so
the gate itself says when each one is done.

## Rule 8: "N additional ...", never a noun-less "N more"

| row | now | change to |
|---|---|---|
| `proto_ko_team_effort` | "... Deal 6 [gold]Pyro[/gold] damage, 6 more if you played a [gold]Companion[/gold] card this turn." | "... Deal 6 [gold]Pyro[/gold] damage, 6 additional damage if you played a [gold]Companion[/gold] card this turn." |
| `proto_ko_sparkling_burst` | "Gain 1 [gold]Energy[/gold]. If a [gold]Bomb[/gold] went off this turn, gain 1 more." | "Gain 1 [gold]Energy[/gold]. If a [gold]Bomb[/gold] went off this turn, gain 1 additional [gold]Energy[/gold]." |

`proto_ko_kitchen_alchemy` ("lose 1 more for each") is the scaled shape and
stays; the lint's ` for each` lookahead passes it.

## Spend is Furina's word

`ARM_KEYWORDS` maps a golded `Spend` to Furina's tip, so Klee's two print it
plain. Use another verb rather than gold it:

| row | now | change to |
|---|---|---|
| `proto_ko_stoke_the_fuse` | "Spend all your remaining [gold]Sparks[/gold]. ..." | "Pay all your remaining [gold]Sparks[/gold]. ..." |
| `proto_ko_fireworks_finale` | "Spend all your [gold]Sparks[/gold]. ..." | "Pay all your [gold]Sparks[/gold]. ..." |

## "Set off" is the verb, never prose; the event is "goes off"

| row | now | change to |
|---|---|---|
| `proto_ko_vermillion_pact` (Sparkborne Magic) | "When a [gold]Set off[/gold] makes one of your [gold]Bombs[/gold] react, every other [gold]Bomb[/gold] it sets off reacts with the same aura." | "Whenever a [gold]Set off[/gold] makes one of your [gold]Bombs[/gold] react, the other [gold]Bombs[/gold] that go off react with the same aura." ("Whenever": it repeats.) |
| `proto_ko_pass_the_match` | "Choose another player. This turn, their next Attack [gold]Sets off[/gold] your [gold]Bombs[/gold] on each enemy it hits. Draw {Cards:diff()} card{Cards:plural:\|s}." | "Another player's next Attack this turn makes your [gold]Bombs[/gold] go off on each enemy it hits. Draw {Cards:diff()} card{Cards:plural:\|s}." (co-op target spelling: a chosen ally is "Another player") |
| `proto_ko_knights_of_favonius` | "Whenever another player plays an Attack, it [gold]Sets off[/gold] your [gold]Bombs[/gold] on each enemy it hits." | "Whenever another player plays an Attack, your [gold]Bombs[/gold] on each enemy it hits go off." |

The fourth prose face, Prune's Hexhunter Chime (`proto_mc_prune_hexhunter_chime`),
is a companion row and landed on `main` ("The next [gold]Bomb[/gold] that goes
off this turn ..."; the code reads any explosion, `CompanionCovenBombs.ElementFor`
from `ProtoBombPower.Explode`).

**Check before applying the two co-op rows:** if another player's Attack
counts as a Set off for the Set off readers (Grounded's "no Set off card",
Spark gain, Chained Reactions), the golded verb is carrying a rule and should
stay; "go off" would drop it. Read `KnightsOfFavoniusPower` and the Pass the
Match power for which counter they bump.

## Co-op targets: one spelling per meaning

| row | now | change to |
|---|---|---|
| `proto_ko_shrapnel` | "... While an enemy holds your [gold]Mine[/gold], other players' Attacks deal 50% more damage to it." | "... While an enemy holds your [gold]Mine[/gold], each other player's Attacks deal 50% more damage to it." |

## Rule 15: no restated rule

| row | now | change to |
|---|---|---|
| `proto_ko_careful_arrangement` (Exquisite Compound) | "Move all your [gold]Bombs[/gold] onto the enemy as one [gold]Bomb[/gold]. It grows by 5, and is a [gold]Mine[/gold] if any of them were." (97) | "Merge all your [gold]Bombs[/gold] onto the enemy. The [gold]Bomb[/gold] grows by 5, and is a [gold]Mine[/gold] if any were." (84) |

## "If a Bomb reacted this turn"

The `reaction-lowercase` rule bans only the noun; the verb is admitted on the
conventions page since this pass. Sizzle (117), Flash Point (118) and Perfect
Timing share a 52-character clause:

| row | now | change to |
|---|---|---|
| `proto_ko_sizzle` | "If a [gold]Bomb[/gold] triggered an [gold]Elemental Reaction[/gold] this turn, deal ..." | "If a [gold]Bomb[/gold] reacted this turn, deal ..." |
| `proto_ko_flash_point` | same clause | same change |
| `proto_ko_perfect_timing` | same clause | same change |

Note (Klee review 2026-10-08, sec.5): the change drops the golded
`Elemental Reaction` from the three faces, and with it the new Elemental
Reaction tip (`ArmKeywordTips.ForElementalReaction`). The Bomb tip and the
reaction previews still ride them. If the hover matters more than 27
characters, keep the noun.

## Placement: one spelling

The base names no target on a single-target play (rule 3): "Place a
[gold]Bomb[/gold] N." The same enemy again is "it".

| row | now (klee-next) | change to |
|---|---|---|
| `proto_ko_mine_toss` | "Place a [gold]Mine[/gold] 9 on an enemy." | "Place a [gold]Mine[/gold] 9." |
| `proto_ko_coven_errand` | "Place a [gold]Bomb[/gold] 10 on an enemy, 14 if ..." | "Place a [gold]Bomb[/gold] 10, 14 if ..." |
| `proto_ko_bombs_away` | "Place a [gold]Bomb[/gold] 6 on an enemy. Gain ..." | "Place a [gold]Bomb[/gold] 6. Gain ..." |
| `proto_ko_fire_fire` (klee-next only) | "Place a [gold]Bomb[/gold] 7 on the enemy. [gold]Set off[/gold] the enemy." | "Place a [gold]Bomb[/gold] 7. [gold]Set off[/gold] the enemy." |
| `proto_ko_mine_all_mine` | "Deal 8 [gold]Pyro[/gold] damage. Place a [gold]Mine[/gold] 6 on that enemy." | "Deal 8 [gold]Pyro[/gold] damage. Place a [gold]Mine[/gold] 6 on it." |

## Piles are golded

| row | now | change to |
|---|---|---|
| `proto_ko_treasure_map` | "Put a [gold]Set off[/gold] card from your discard pile into your hand. ..." | "Put a [gold]Set off[/gold] card from your [gold]Discard Pile[/gold] into your hand. ..." |
| `proto_ko_come_back_and_play` | "Put a [gold]Companion[/gold] card from your discard pile into your hand." | "Put a [gold]Companion[/gold] card from your [gold]Discard Pile[/gold] into your hand." |

## Exhaust as a verb is golded; rule 14's semicolon

| row | now | change to |
|---|---|---|
| `proto_ko_kitchen_alchemy` | "ALL enemies lose 1 [gold]Strength[/gold]. Exhaust every status in your hand; they lose 1 more for each." | "ALL enemies lose 1 [gold]Strength[/gold]. [gold]Exhaust[/gold] every Status in your hand. They lose 1 more [gold]Strength[/gold] for each." |

"Status" is capitalised as a card type on five readers in the Klee review
(Finders Keepers, Klee Can Explain!, Damage Report, Kitchen Alchemy, Albedo's
Dust): "Whenever you draw a Status, ...". Albedo's row is a companion and was
golded on `main` without the capital; take the capital on all five together.

## Accuracy faces from seats

- **Big Badda Boom** (`proto_ko_big_badda_boom`), BACKLOG lines 81 and 87
  (suite 1 item 3): "then damage equal to what your [gold]Bombs[/gold]
  dealt" does not say the scope. The code (`ProtoBombPower.DealSetOffTotal`)
  hits for `SetOffEchoBaseThisPlay`: the Bombs THIS card set off, each
  explosion's Vulnerable taken back out, Block they removed counted. Proposed:
  "... then damage equal to what those [gold]Bombs[/gold] dealt." Check the
  Block half against suite 1 item 3 before applying; the comment and the seat
  disagree.
- **Treasure Map**, BACKLOG lines 79 and 89 (scaling round 2 item 2): the face
  is accurate (it grows the Bomb whether or not a card comes back); what is
  missing is a warning when the discard holds no Set off card. That is a live
  hover or a playability refusal, not a wording change; leave it to the
  BACKLOG line.

## Already on main, nothing to carry

The old shipped Bomb keyword (`KLEEMOD-BOMB`, `KleeKeywords.Bomb`, the
`includesBombRules` path and its coexistence test) left `main` in this pass;
`klee-next` takes it on merge. `BombPower.cs` stays (its tests, telemetry and
two relics' listener read it).
