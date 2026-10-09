# TEXT CONVENTIONS

How a card, keyword tip, power badge or relic is written, derived from the
base game's own English strings and measured on them. The corpus is the
`localization/eng/*.json` tables inside `SlayTheSpire2.pck` (v0.111.0):
`cards.json` (624 descriptions), `powers.json` (295), `relics.json` (306),
`card_keywords.json` (7) and `static_hover_tips.json` (48). Strings are cited
by their loc id. Lengths are RENDERED characters: BBCode tags stripped, every
`{hole}` counted as one numeral, newlines as spaces. `tools/lint_text_conventions.py`
enforces the ceilings and spellings on every kit's faces (`proto_ko_`, `kk_`,
`vk_`, `fs_`, `mc_`, `mi_`, `mf_`), the keyword tips (arm, base and the
`KLEEMOD-*` reaction rows), the prototype power badges, the potions and the
Ancient cards; `--report` reads the top-level power badges and relics the gate
does not yet hold, and `--census` flags every string over its target.

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
   2 "more damage".) The same word for a bonus of anything: "gain 4
   additional [gold]Block[/gold]", "draw 2 additional cards", "gain 1
   additional [gold]Energy[/gold]". Never a noun-less "deal 6 more". A scaled
   number keeps its shape ("plus 3 for each [gold]Oath[/gold]", "3 more for
   each [gold]Plan[/gold] waiting"), "instead" stays for a replaced number,
   and a count that grows ("the Casket gains 1 more") is not a bonus. A
   number that can reach 1 prints its noun through the hole:
   `card{Cards:plural:|s}`, never a fixed "{N} cards".
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
    Varka's "Knight." line rides the same rail (see the table below).
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
| `[gold]Bomb[/gold]` / `[gold]Bombs[/gold]` | "Place a [gold]Bomb[/gold] 5." (the number is its size); "Each [gold]Bomb[/gold] on the enemy grows by 3." | a Bomb "goes off"; never pops, fires, explodes or detonates |
| `[gold]Set off[/gold]` | the verb, sentence-initial: "[gold]Set off[/gold]. Deal 4 damage."; "[gold]Set off[/gold] a random enemy's [gold]Bombs[/gold]." | never as prose; the event is "goes off" |
| `[gold]Mine[/gold]` | "Place a [gold]Mine[/gold] 4 on ALL enemies." | a Mine is a Bomb; "goes off when its enemy attacks you" |
| `[gold]Spark[/gold]` / `[gold]Sparks[/gold]` | the price sits in the cost slot; the body does not restate it; "gain 1 [gold]Spark[/gold]" | "Some cards cost Sparks instead of Energy." |
| `[gold]Plan[/gold]` | the line: "[gold]Plan[/gold]: Deal 9 [gold]Hydro[/gold] damage." A plan-only row leads with "Play on the [gold]Bake-Kurage[/gold]." (codegen) | the Bake-Kurage "carries out" a Plan; a Plan "hits the front enemy" unless it says ALL |
| `[gold]Mend[/gold] N` | "[gold]Mend[/gold] 10." | "heal N HP, but never above the HP you had at the start of this combat" |
| `[gold]Bake-Kurage[/gold]` | the pet's name, always; "Whenever the [gold]Bake-Kurage[/gold] carries out a [gold]Plan[/gold], draw 1 card." | never "the jellyfish" |
| `[gold]Swirl[/gold]` | a verb with the base's targets: "[gold]Swirl[/gold] the enemy." "[gold]Swirl[/gold] ALL enemies." "Deal 8 [gold]Anemo[/gold] damage to a random enemy and [gold]Swirl[/gold] it." A sweep of the auras present at play is "[gold]Swirl[/gold] every aura." (Wall of Gales, Bottled Gale): the code takes the aura-wearing enemies once and does not Swirl one that gains an aura during the sweep, so "ALL enemies" would promise more. Never "Swirl an enemy's aura", never a bare "Swirl.", never "the element Swirled": "that element" | "Whenever a [gold]Swirl[/gold] happens" |
| `[gold]Elemental Reaction[/gold]` | the shipped spelling of the noun, kept, with its own tip (`ArmKeywordTips.ForElementalReaction`): "If it causes an [gold]Elemental Reaction[/gold], ...". The VERB "react" is admitted and needs no gold: "a [gold]Bomb[/gold] reacted this turn", "makes one of your [gold]Bombs[/gold] react". A hit "causes" a reaction; "sets off" is the Bomb's verb and never the reaction's | "reaction" lowercase as a noun is never printed |
| Element application (all six) | The text names the element AND the card wears its gem. [USER], 2026-10-02, after a co-op run: "Unify the language across all cards - say if it does an element and also apply the symbol to the card". This reverses the 2026-09-01 rule, under which the gem replaced the sentence. A hit that applies its element: "Deal 6 [gold]Pyro[/gold] damage." (also "to ALL enemies", "to a random enemy", "N times", "Deal [gold]Geo[/gold] damage equal to your [gold]Block[/gold]."); only the element word is added before "damage", and a Kokomi Plan hit is Hydro: "[gold]Plan[/gold]: Deal 12 [gold]Hydro[/gold] damage." An aura with no hit: "Apply [gold]Hydro[/gold] to an enemy." / "Apply [gold]Hydro[/gold] to ALL enemies." A Swirl keeps its verb and adds no word (it is Anemo by definition); its card wears the Anemo gem. The gem is `KleeKeywords.Applies*` at `AutoKeywordPosition.None`, drawn by `Vfx/ElementBadge.cs`: one gem per card, the first aura element its face declares, else Anemo, else Geo. `tools/lint_element_text.py` holds every prototype face to the words. | |
| `[gold]Spend[/gold]` N | Furina. As a mode: "Deal 6 damage. [gold]Spend[/gold] 5: deal 12 and draw 2 cards instead."; as a fixed price, its own sentence first: "[gold]Spend[/gold] 4. Deal 11 [gold]Hydro[/gold] damage."; spend-all: "[gold]Spend[/gold] all your [gold]Fanfare[/gold]. Deal that much damage." The tip: "Pay that much Fanfare. Offered only if you have enough." | she "spends" Fanfare; a Spend mode she cannot afford is not offered |
| `[gold]Fanfare[/gold]` | Furina's one number, never a bar or a meter: "gain 3 additional [gold]Fanfare[/gold]", "[gold]Spend[/gold] all your [gold]Fanfare[/gold]". The tip: "Gain 1 for each HP you lose or Repay. Spend uses it. It resets to 0 after each combat." | the gauge beside her portrait |
| `[gold]Summon[/gold]` X | a Guest Star card's face: "[gold]Summon[/gold] Charlotte." The guest's own Line and Act are its tip and badge, Defect-orb style (`furina-guest-batch-2026-09-25.md`, frame item 1); in combat the face adds the Bow line. The Summon tip: "A guest joins at the back. On a full stage, the oldest guest acts once more and leaves first." | a guest "joins", "acts", "leaves" |
| `Guest Star` | the card's keyword (its tip: "Acts at the end of your turn. Summoning one already on stage makes it act and stay."); a face that names the class prints the words: "Whenever a Guest Star joins the stage" | |
| `[gold]Drain[/gold]` N | Furina (the Salon's Tab, 2026-10-05). A price in HP, never a meter. As a mode: "Deal 7 damage. [gold]Drain[/gold] 3: deal 12 instead."; as a fixed price, its own sentence first: "[gold]Drain[/gold] 5. Deal 20 damage." A Drain may go past the line (3/4 of her entry HP, 2026-10-09); a card that would take her to 0 HP is unplayable, and a Drain mode that would is not offered. The tip: "Lose N HP. Drained HP returns after combat, but HP drained past your line (3/4 of your HP at combat start) is lost unless you Repay it." | she "drains" HP; the counter beside the Fanfare gauge reads "Drained N"; the floor is "the line" |
| `[gold]Repay[/gold]` N | "[gold]Repay[/gold] 3." / "[gold]Repay[/gold] all your drained HP." The Repay floor (2026-10-09): "[gold]Repay[/gold] 3. Gain 1 [gold]Block[/gold] for any HP it could not [gold]Repay[/gold]." (Vigor the same; damage: "Deal 6 damage, plus 1 for any HP it could not [gold]Repay[/gold]."). The tip: "Regain that much drained HP. It never returns more than you drained." Never "heal", which is the base's word for HP from anywhere | she "repays" drained HP; HP returned by the end of combat is "the curtain call", not a Repay |
| `[gold]Companion[/gold]`, `[gold]Energy[/gold]` | golded (the mod has no energy icon var) | |
| `[gold]Knight[/gold]` / `[gold]Knights[/gold]` | Co-op notes pick 2 ([USER], 2026-10-02): every Knight (a Varka Companion card, `VarkaRules.IsKnight`: the 17 colon-titled rows, the four starter-only ones included) prints "**Knight.**" as its first line, the way a card prints Exhaust. The line is the keyword rail (`KleeKeywords.Knight` at `AutoKeywordPosition.Before`, declared by codegen from `personal_pool: varka`) and is never typed into a row. A card written against Knights golds the bare word, singular or plural: "If you played a [gold]Knight[/gold] this turn", "Add a random [gold]Knight[/gold] to your hand.", "for each [gold]Knight[/gold] you played this combat". Never "Knight card", and on a Varka card "Companion" never means a Knight. The printed line and the golded word hover one tip, key `KLEEMOD-ARM_VARKA_KNIGHT`: "One of Varka's Companions. Playing one makes its element your current element. Geo does not." A relic that names a Knight golds it the same way and attaches the same tip. | a Knight is "played"; Noelle is a Geo Knight and sets no element |
| `[gold]Oath[/gold]` | Varka's count, one per element. The element is golded and leads: "gain 1 [gold]Pyro[/gold] [gold]Oath[/gold]", "for each [gold]Cryo[/gold] [gold]Oath[/gold]". His current element's is "[gold]Oath[/gold] of your [gold]current element[/gold]" (one spelling; never "your current element's Oath", never "for each Oath, as your current element"). The tip: "1 Oath per element a card applies, plus 1 per element it Swirls. Kept all fight. Element cards read their own, others the current." | he "gains" Oath |
| `[gold]current element[/gold]` | two words, lowercase, one span: "Apply your [gold]current element[/gold] to an enemy.", "deal 3 for each [gold]Oath[/gold] of your [gold]current element[/gold], as that element" | it "becomes" or "changes"; a card "switches" it (the switch hover) |
| `[gold]Tamakushi Casket[/gold]` / `[gold]Casket[/gold]` | Kokomi's relic, by either name: "the [gold]Casket[/gold] gains 2", "Double the [gold]Casket[/gold]'s count." Its token is `[gold]Open the Casket[/gold]` | the Casket "counts"; Open the Casket "empties it" |
| `[gold]Dusk[/gold]` | in place of "Plan:" on its line: "[gold]Dusk[/gold] [gold]Plan[/gold]: Gain 12 [gold]Block[/gold]." The tip carries the timing (end of this turn, before enemies act) and is the only place it is stated | |
| a card a face makes (`Nip`, `Sea Glass`, `Pop!` and the rest) | golded on the face that makes it, as the base golds `OVERCLOCK`'s Burn: "Add 2 [gold]Nips[/gold] to your hand." The card itself is the definition; the page prints its face once it is added | |
| a pile | the base's capitals and gold: "[gold]Draw Pile[/gold]", "[gold]Discard Pile[/gold]", "[gold]Exhaust Pile[/gold]". Never lowercase "discard pile" on a face | |
| co-op targets | three meanings, one spelling each. A chosen ally: "Another player gains 6 [gold]Block[/gold]." / "Another player's next Attack this turn ..."; every ally: "each other player"; everyone, you included: "each player" | |
| a repeating effect | "For N turns, at the start of your turn X." / "For N turns, at the end of your turn X." No comma after the timing clause (the ten companion rows' spelling). A card's own duration on a stat is rule 9's "Gain 2 [gold]Dexterity[/gold] for 2 turns." Never "At the start of your next N turns" or "At the end of each of your next N turns" | |
| a delayed one-shot | "In 2 turns, deal 12 [gold]Hydro[/gold] damage to a random enemy." Never "After 2 turns" | |
| the first time each turn | "The first time each turn you X, Y." Never "Once per turn, when you X" | |
| a status a card makes (`Dazed`, `Confiscated`, any other) | Status cards go to the discard pile, as in the base game. [USER], 2026-10-03: "I agree that we should adopt the same convention". The face is the base's (`OVERCLOCK`, `TURBO`, `BOOST_AWAY`, `FIGHT_THROUGH`): "Add a [gold]Dazed[/gold] into your [gold]Discard Pile[/gold]." / "Add 2 [gold]Confiscated[/gold] into your [gold]Discard Pile[/gold]." Never "Shuffle ... into your draw pile"; the codegen refuses `zone: draw`. | |

## Exceptions the lint carries (each with its reason in the lint)

**The prototype gate:** `proto_mc_durin_principle_of_purity` (a two-mode Power must
print both modes on the reward screen; the base has no static modal card); the
ten prototype Bomb-badge faces that carry the rider sentence (`EB-573`, 126 to
164 rendered; since the text pass of 2026-09-25 every other Bomb face, and the
Bomb, Set off and Mine keyword tips, meet the ceiling); and the Kokomi Plan
rows the lint names. `TamakushiCasket` left the list with `EB-346`: its own
two rules were always under the ceiling and the shared slot sentence is gone.

**The report (`--report`):** both faces of the old Bomb badge, `BombPower`'s
static `description` and its `smartDescription`, which no card raises any more
(its `KLEEMOD-BOMB` keyword tip left with the text pass of 2026-10-08); the
class stays until its tests and the telemetry that reads its counters are
retired, and the report does not read "detonates" on it.

**Rows held for `klee-next`:** the lint's `DEFERRED` table names the Klee rows
the 2026-10-08 pass widened a spelling over (Team Effort, Sparkling Burst,
Treasure Map, Come Back and Play!), because Klee is frozen at Balance on `main`.
The edits are written out in `docs/notes/klee-text-pass-pending-2026-10-08.md`;
the table has rot semantics and empties when they land.
