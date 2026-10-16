# Yae dedupe, 2026-10-16: the near-copies to cut

Yae is a Prototype kit. [USER]: "Let's do a dedupe pass on Yae to identify
obvious cleanup targets, then do an art pass once that finishes." Earlier:
"we're printing a lot of same-y feeling "do a strike and X" + "do a block
and same X"".

**Evidence.** The 78-card sheet (`proto_ym_` rows of
`docs/prototype-surface.yaml`) and round 7's offers, five seats on the full
pool (`review/records/yae-round-7-2026-10-16.md`; `tools/telemetry_report.py
--offers --character "Yae Miko" --since 2026-10-16T02:30`). One round is
thin, so take rates only support a cut that the card text already argues for.

## 1. The rule behind the cuts

A Sakura kind gets one Common planter, on the card type that matches what
the kind does: the **Foxfire** Sakura hits ALL, so its planter is the AoE
attack; the **Kitsune** Sakura is the Block decoy, so its planter is a Block
card; the plain **Sakura** keeps a cheap attack and Twin Sakura. Any other
effect (duration, Deadline Extension, Levels, per-Edit scaling) lives on one
card at each rarity, not on an attack and a Block card side by side.

## 2. Cut targets (11)

| Card | Text today | Taken | Why it goes | What still does the job |
|---|---|---|---|---|
| **Kitsune Flick** (C Atk 1) | Deal 5. Plant a Kitsune Sakura. | 1/7 | Kitsune on an attack, against the rule | Shrine Maiden's Guard (3/6) |
| **Shrine Lantern** (C Skill 1) | Gain 6 Block. Plant a Foxfire Sakura. | 2/11 | Foxfire on a Block card, against the rule | Foxfire Sweep (3/5) |
| **Grafted Branch** (C Skill 1) | Plant a Sakura at Level 2, lasting 1 more turn. | 0/4 | Third plain planter | Twin Sakura (3/9), Thunder Petal, the starter |
| **Shrine Bell** (C Atk 1) | Deal 7. Each Sakura lasts 1 more turn. | 1/7 | Duration pair, the weakest row | Evergreen Charm (5/7) |
| **Shrine Offering** (C Skill 1) | Gain 6 Block. Each Sakura lasts 1 more turn. | 0/6 | Same pair, Block side | Evergreen Charm |
| **Deadline** (C Skill 1) | Gain 8 Block. Edit a hand card: Deadline Extension. | 1/7 | Block twin of Cliffhanger | Cliffhanger, Evergreen Charm |
| **Sacred Spark** (C Atk 1) | Deal 4. A Sakura strikes it. | 0/5 | Smaller Kitsune Pounce with no condition to play around | Kitsune Pounce, Narukami Judgment |
| **Kitsune Flash** (C Atk 1) | Deal 6; 3 more if Annotated. | 0/7 | A Strike with a footnote; no seat wanted it | Margin Note (5/8), Sly Strike |
| **Print Run** (U Skill 1) | Block 2, plus 3 per card Edited this combat. | 0/2 | Block twin of Bestseller | Bestseller, Serialization |
| **Rooted Shrine** (U Skill 1) | Gain 6 Block. Each Sakura gains a Level. | 1/2 | Block twin of Narukami Ray | Narukami Ray, Kitsune Veil |
| **Omikuji** (U Skill 1) | Choose: each Sakura gains a Level, or 2 Weak to ALL. | 0/3 | Both modes are other cards | Narukami Ray, Kitsune Guile |

That is 8 of 20 Commons and 3 of 38 Uncommons. Three of the 11 (Kitsune
Flick, Sacred Spark, Shrine Lantern) are among her 35 blank portraits; the
art pass running now skips them.

**Looked at and kept.**
- Sakura Canopy (Block per Sakura) and The Shrine's Sacred Shade (the same,
  each turn): a Skill and a Power, not an attack/Block mirror.
- Petal Storm and Thunderbolt Tithe (damage per Sakura, ALL or one): the
  AoE/single split is the base game's own (Cleave, Strike).
- Seven cards apply Weak; it is her archetype's fuel (Kitsune Pounce, Fox's
  Bargain, Saiguu's Lesson, Fox's Verdict all read it).
- **Flagged, not cut:** Mischievous Teasing (Rare, 0: 2 Weak to ALL, draw 2;
  0/2) reads as an Uncommon. It wants a Rare-sized rule, not a cut
  (Rares bend, never remove).

## 3. Refilling the pool

Cutting 11 leaves 67. Every kit's pool is 78, and 8 of the holes are
Commons. Round 7 says what the new cards should do: her damage is
0.78 of base in acts 1 and 2, she bleeds in act 1, and Sakura strike a random
enemy (two thirds of the Kin Priest fight's Sakura damage went to minions).
So the refill leans on early damage and aimed strikes, in new shapes, not a
third attack/Block pair.

## Picks

1. **The cuts.**
   - **(a) Default:** all 11 go.
   - (b) All except the ones you name.
2. **The refill.**
   - **(a) Default:** Claude designs 11 replacements (8 Common, 3
     Uncommon) to the brief in section 3, in a short follow-up paper;
     cuts and new cards are built together, so the pool never plays at 67,
     then her art pass covers the new cards.
   - (b) Cut now and play the 67-card pool in your run; refill after it.
