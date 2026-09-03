# TEXT CONVENTIONS

How a card, keyword tip, power badge or relic is written, derived from the
base game's own English strings and measured on them. The corpus is the
`localization/eng/*.json` tables inside `SlayTheSpire2.pck` (v0.111.0):
`cards.json` (624 descriptions), `powers.json` (295), `relics.json` (306),
`card_keywords.json` (7) and `static_hover_tips.json` (48). Strings are cited
by their loc id. Lengths are RENDERED characters: BBCode tags stripped, every
`{hole}` counted as one numeral, newlines as spaces. `tools/lint_text_conventions.py`
enforces the ceilings and spellings on the prototype arms and reports the
shipped surfaces (`--shipped`). **The shipped pass is ruled and applied
(`EB-345`):** the Furina sheet, the companion rows, the shared keyword tips,
the shipped powers and the shipped relics read clean against this page. Two
things stay where they were, by the same ruling: the shipped **Klee and Kokomi
card rows** are not rewritten — the overhauls being played replace them, so the
report skips them by id off those two sheets — and the shipped Klee kit keeps
**"detonates"** until the overhaul replaces it, two Bombs being two rules.

## Ceilings, measured

| surface | base median | base p90 | base longest static string | TARGET | CEILING (lint) |
|---|---|---|---|---|---|
| card description | 47 | 79 | 117 (`RIGHT_HAND_HAND`) | 80 | 120 |
| upgrade add-clause `{IfUpgraded:show:...}` | 6 | 17 | 18 | 18 | 20 |
| keyword / mechanic tip | 48 (`card_keywords`), 57 (`static_hover_tips`) | 87 / 109 | 134 (`CHANNELING`) | 90 | 135 |
| power badge (`description` and `smartDescription`) | 50 | 75 | 123 (`AGGRESSION_POWER`) | 75 | 125 |
| relic | 55 | 85 | 118 (`PAELS_TOOTH`, static part) | 85 | 120 |
| selection-screen prompt | 39 | 58 | 84 | 60 | 85 |

Card descriptions by rarity: Common median 33 (max 74), Uncommon 48 (max 118),
Rare 56 (max 115), Basic 28. Sentences per card: median 1, p95 2, max 4. The
one base card past 120 is `MAD_SCIENCE` (326), a runtime template that prints
one of many bodies, never all of them. A string over its CEILING fails the
lint unless it is in the lint's exception list with a reason; a string over
its TARGET is what a rewrite aims below.

## The rules, each with a base-game example

1. **One effect per sentence, imperative, present tense, a period after
   each.** `BASH`: "Deal 8 damage.\nApply 2 Vulnerable." `IRON_WAVE`: "Gain 5
   Block.\nDeal 5 damage." The base puts each sentence on its own line; the
   mod's codegen joins with spaces (a codegen change, not a text one).
2. **Verbs are the base's four: Deal, Gain, Apply, Draw.** "Deal 6 damage."
   "Gain 5 Block." "Apply 2 Weak." "Draw 2 cards." (`ACROBATICS`: "Draw 3
   cards." never "Draw 3.") Losing is "Lose 3 HP." (`OFFERING`); healing is
   "heal 6 HP" (`BURNING_BLOOD`).
3. **A single-target hit names no target.** "Deal 8 damage." The same enemy
   again is "the enemy" (`BULLY`: "for each Vulnerable on the enemy") or
   "it". Never "target enemy" (0 uses), never "the front enemy" on a card
   line, never "every enemy" (0 uses).
4. **Everyone is "ALL enemies", capitals and all** (47 uses, 0 lowercase):
   `THUNDERCLAP`: "Deal 4 damage and apply 1 Vulnerable to ALL enemies."
   `PIERCING_WAIL`: "ALL enemies lose 6 Strength this turn."
5. **Random is "a random enemy"**; repeats are "twice" or "N times":
   `SWORD_BOOMERANG`: "Deal 3 damage to a random enemy 3 times."
   `TWIN_STRIKE`: "Deal 5 damage twice." `EXTERMINATE`: "Deal 6 damage to ALL
   enemies 6 times."
6. **Keywords are Capitalised and `[gold]`.** Block (124/124 golded), Weak,
   Vulnerable, Strength, Dexterity, Exhaust, Hand, Discard Pile, Draw Pile,
   Exhaust Pile. Card types are plain words: "Whenever you play an Attack"
   (`RAGE_POWER`), "Skills cost 0" (`CORRUPTION`). Elements the mod names in
   text are golded like keywords.
7. **A conditional leads with "If", or trails as "... if ...".** `ESCAPE_PLAN`:
   "Draw 1 card.\nIf you draw a Skill, gain 3 Block." `FLATTEN`: "This card
   costs 0 if Osty has attacked this turn." The base has no either/or card;
   the mod's spelling is "If X, Y. Otherwise, Z."
8. **A bonus is "N additional damage"; a derived number is "equal to".**
   `ASHEN_STRIKE`: "Deals 3 additional damage for each card in your Exhaust
   Pile." `BODY_SLAM`: "Deal damage equal to your Block." (36 "additional" to
   2 "more damage".)
9. **Timing words are the base's.** "this turn" (68), "Next turn," as an
   opener (7), "At the start of your turn," (29), "At the end of your turn,"
   (20), "this combat". A card's duration is "for 2 turns" (`DEBILITATE`);
   a power's is "Lasts for {Amount} turns." (`INTANGIBLE_POWER`) or
   "for {Amount} turns" (`WEAK_POWER`). Never "Lasts N more turns".
10. **A power is one trigger and one effect, present tense, and no second
    "whenever".** `AFTERIMAGE_POWER`: "Whenever you play a card, gain 1
    Block." `NOXIOUS_FUMES_POWER`: "At the start of your turn, apply 2 Poison
    to ALL enemies." A power on an enemy says "this enemy" (`SLOW_POWER`).
    Numbers in a power or relic are `[blue]`: "gain [blue]3[/blue]
    [gold]Block[/gold]", "[blue]{Amount}[/blue]".
11. **A relic is one sentence in the same shapes.** `BAG_OF_MARBLES`: "At the
    start of each combat, apply 1 Vulnerable to ALL enemies."
    `BLOOD_VIAL`: "At the start of each combat, heal 2 HP." A relic states its
    OWN rule and never a fact about the whole mod: the fourth-Companion reward
    slot is one, so it is stated once in `klee-mod/Klee/manifest.json` and no
    relic prints it (`EB-346`). Those 59 shared characters on four starting
    relics were what put three of them over this ceiling.
12. **A pet is named.** `FETCH`: "Osty deals 6 damage." `BONE_SHARDS`: "If Osty
    is alive, he deals 6 damage to ALL enemies." Never "the jellyfish", never
    "your pet".
13. **Exhaust, Retain, Ethereal, Innate are the keyword rail, never a
    sentence** ("Exhaust." appears in 0 of 624 descriptions). The codegen
    strips a printed "Exhaust." from a row that declares `exhaust: true`.
14. **Punctuation is the base's:** no dashes of any kind, no parentheses, no
    semicolons except between the halves of an either/or, a colon only after a
    mode label or a Plan line. A tip is one to three short sentences
    (`SLY.description` is 87 characters, one sentence).
15. **A card says what it does and nothing about why.** No "so that", no
    "which means", no restated rule on every carrier: the word carries the
    rule in its tip, the card prints the word.

## This mod's own words, spelled once

| word | on a card | as an event or in prose |
|---|---|---|
| `[gold]Bomb[/gold]` / `[gold]Bombs[/gold]` | "Place a [gold]Bomb[/gold] 5." (the number is its size); "Each [gold]Bomb[/gold] on the enemy grows by 3." | a Bomb "goes off"; never pops, fires or explodes. **The SHIPPED Klee kit still says "detonates"** and keeps it until the overhaul replaces that kit (`EB-345`), which is why the shipped read does not carry the `goes-off` spelling and the prototype gate does |
| `[gold]Set off[/gold]` | the verb, sentence-initial: "[gold]Set off[/gold]. Deal 4 damage."; "[gold]Set off[/gold] a random enemy's [gold]Bombs[/gold]." | never as prose; the event is "goes off" |
| `[gold]Mine[/gold]` | "Place a [gold]Mine[/gold] 4 on ALL enemies." | a Mine is a Bomb; "goes off when its enemy attacks you" |
| `[gold]Spark[/gold]` / `[gold]Sparks[/gold]` | the price sits in the cost slot; the body does not restate it; "gain 1 [gold]Spark[/gold]" | "Some cards cost Sparks instead of Energy." |
| `[gold]Plan[/gold]` | the line: "[gold]Plan[/gold]: Deal 9 damage." A plan-only row leads with "Play on the [gold]Bake-Kurage[/gold]." (codegen) | the Bake-Kurage "carries out" a Plan; a Plan "hits the front enemy" unless it says ALL |
| `[gold]Mend[/gold] N` | "[gold]Mend[/gold] 10." | "heal N HP, never above the HP you entered the fight with" |
| `[gold]Bake-Kurage[/gold]` | the pet's name, always; "Whenever the [gold]Bake-Kurage[/gold] carries out a [gold]Plan[/gold], draw 1 card." | never "the jellyfish" |
| `[gold]Swirl[/gold]` | a verb with the base's targets: "[gold]Swirl[/gold] the enemy." "[gold]Swirl[/gold] ALL enemies." "Deal 8 damage to a random enemy and [gold]Swirl[/gold] it." | "Whenever a [gold]Swirl[/gold] happens" |
| `[gold]Elemental Reaction[/gold]` | the shipped spelling of the noun, kept: "If a [gold]Bomb[/gold] triggered an [gold]Elemental Reaction[/gold] this turn" | "reaction" lowercase is never printed |
| Hydro / Pyro / Electro / Cryo application | a GEM beside the type plaque and a hover tip, never a sentence ([USER] 2026-09-01; `KleeKeywords.Applies*` at `AutoKeywordPosition.None`). A card whose own action is the aura prints "Apply [gold]Hydro[/gold]." A card-less hit names its element: "deal 6 [gold]Cryo[/gold] damage to a random enemy." | |
| `[gold]Deploy[/gold]` | the verb, sentence-initial, naming the member: "[gold]Deploy[/gold] Mademoiselle Crabaletta." Never "Add 1 ... to your Salon", which is the SHIPPED deploy's face and a different rule | a member "joins the stage"; onto a full stage the front one "[gold]Evokes[/gold] first" |
| `[gold]Evoke[/gold]` | the verb: "[gold]Evoke[/gold] the front [gold]Salon[/gold] member." "[gold]Evoke[/gold] Surintendante Chevalmarin." The Encore price is its own sentence in front, built by the codegen and never written into a row: "Spend 2 [gold]Encore[/gold]." An upgrade that cuts it prints "Spend {IfUpgraded:show:1|2} [gold]Encore[/gold]."; one that takes it to 0 drops the sentence on the `+` card rather than printing "Spend 0" | the member "performs and leaves"; never "bows out", which is the shipped bow |
| `[gold]Drain[/gold]` | "[gold]Drain[/gold] your [gold]Fanfare[/gold]." followed by what it buys, one sentence each | the meter "falls to nothing"; what follows is "priced off the amount it took" |
| `[gold]Companion[/gold]`, `[gold]Energy[/gold]` | golded (the mod has no energy icon var) | |

## Exceptions the lint carries (each with its reason in the lint)

**The prototype gate:** `proto_mc_durin_binary_form` (a two-mode Power must
print both modes on the reward screen; the base has no static modal card); the
prototype Bomb badge's static `description` and its two Mine smart faces (a
live total, a live count, a Mine count and rule 6, which fires on the enemy's
turn when no card is in front of the player; the plain and Weak faces meet the
ceiling). `TamakushiCasket` left the list with `EB-346`: its own two rules
were always under the ceiling and the shared slot sentence is gone.

**The shipped report:** both faces of the shipped Bomb badge, `BombPower`'s
static `description` and its `smartDescription`, which carry all three of the
Bomb's rules between them (`EB-345`); the `KLEEMOD-BOMB` keyword tip
beside them is a primer and drops the last rule's once-per-combat scope to
stay under its own ceiling.
