# Shared-text census — current build

Arms ON: klee overhaul, companion overhaul, kokomi overhaul, furina-stage.
Teyvat frame OFF (its events skipped). Every row below is the text that
actually prints under this arm combination — where a class branches on
`#if KLEE_OVERHAUL` / `FurinaStage.Enabled` / `KokomiOverhaul.Enabled`, the
arm-ON branch is what's quoted. Lengths are RENDERED: BBCode tags
(`[gold]…[/gold]`, `[blue]…[/blue]`) stripped, `{DynamicVar}` holes rendered
with their live numbers, plain C# `$"{Element}"` string interpolation (not a
runtime loc hole — it bakes a literal word into each of four separate loc
rows at class-init) rendered per element. Read `docs/current/text-conventions.md`
ceilings: card 120 (target 80), tip 135 (target 90), power badge 125 (target
75), relic 120 (target 85), selection-screen prompt 85 (target 60).

## Counts

**58 rows read. 24 flagged. 34 clean.**

- Ancients (`RosterAncientCards`): 3 read, 1 flagged.
- Furina cards surviving into the Stage pool: 14 read, 3 flagged.
- Status/curse: 2 read (Confiscated's card face + its keyword tip), 0 flagged.
- Relics reachable in this build: 4 read, 3 flagged.
- Shared power badges / debuffs / reaction tips: 32 read, 16 flagged.
- Character select: 3 read, 1 flagged.

**Out of scope, checked and excluded rather than skipped silently:**
- No mod-added **potions** exist anywhere outside `Teyvat/` (grepped for a
  `PotionModel`/`CustomPotionModel` subclass; none found). `tier05/content/potions.yaml`
  only names base-game potions for the separate sim layer, not new ones.
- No **Shrink** debuff exists in the mod; the one hit is a base-game power
  referenced in a comment (`Powers/Prototype/KokomiPlan.cs:3287`), not
  mod-added.
- **Shatter** is not its own persistent badge; it's the bonus-hit clause
  inside Frozen's badge/tip (both read below), plus one small standalone
  companion-granted badge, **Shattering Pressure** (`ShatterBonusPower`,
  `Powers/CompanionPowers.cs:589-597`, "Your [gold]Shatters[/gold] deal
  [blue]{Amount}[/blue] additional damage.") — clean, listed below.
- Two starter relics (`EtherealSpotlightRelic`, `PearlOfWisdomRelic`) and two
  Ancient Touch-of-Orobas upgrades (`CurtainNeverFalls`, `PearlOfInsightRelic`)
  exist in code but are **unreachable under the current arms**: the live
  starting relics are `SalonSolitaire` and `TamakushiCasket`, and neither
  overrides `GetUpgradeReplacement()`, so Touch of Orobas cannot reach the
  other two either. Excluded rather than graded.
- Each kit's OWN keyword tips (Bomb, Set off, Mine, Plan, Spark, Casket —
  `klee-mod/KleeCode/Cards/Prototype/ArmKeywordTips.cs`) are that kit's own
  design surface, not shared text, so they're out of this pass. Worth
  flagging to the designer anyway: `BombKey`, `SetOffKey`, `MineKey`,
  `PlanKey` and several `ProtoBombPower`/`ProtoBakeKuragePower` faces are
  **already-registered exceptions in `tools/lint_text_conventions.py`**, each
  with its own ruled reason for sitting over ceiling — re-flagging them here
  would just repeat a decision already made.
- The "companion" arm (`CompanionOverhaul`) swaps the shipped Mondstadt and
  Inazuma companion pools for ~58 rewritten `proto_mc_`/`proto_mi_` rows.
  Companion cards are a large, separate shared surface the task's named
  categories don't cover; noting it here as a likely next census rather than
  auditing it in this pass.
- "Momentum Strike" (named in the brief as a card to check if offered/starter)
  does not exist anywhere in the repo except a stray mention in a seat-round
  log file — excluded rather than guessed at.

## Flagged rows, worst first

| id | kind | current text (rendered) | chars | flags | note |
|---|---|---|---|---|---|
| Burst Energy tip (`KleeCardTooltips.BurstBody`, `Cards/KleeCardTooltips.cs:161-183`) | shared mechanic tip (Klee, Kokomi, Furina all read it while their Burst is live; Klee's still is) | "Burst Energy: your character's meter, empty at the start of each combat. Playing a card with Elemental Skill grants 5 and every Elemental Reaction grants 5; some cards, powers and relics grant more. The moment the meter is FULL your character's Burst card is put into your hand, and casting it spends the WHOLE meter -- energy past full is lost at the cast, not at the gain." | 374 | F1, F6, F7 | 2.8x the tip ceiling (135), 3x the power-badge ceiling (125). A genuine rules essay: meter reset, two income rates, an overflow rule and a spend rule in one paragraph. Carries a semicolon and a dash mid-sentence, both against rule 14. Every kit-specific tip in `ArmKeywordTips.cs` went through a documented trim to fit its ceiling; this shared one never did. |
| Electro Aura, both faces (`Powers/AuraPower.cs:48-60`) | shared power badge (every enemy carrying an Electro aura) | smart (in combat): "Electro clings to this enemy for 2 more turns. A hit of a different element consumes the aura and triggers an Elemental Reaction; a Electro hit refreshes its duration." / static (out of combat): "Electro clings to this enemy. A hit of a different element consumes the aura and triggers an Elemental Reaction; a Electro hit refreshes its duration." | 167 / 150 | F1, F5, F7 | Worst of the four elements because "Electro" is the longest name. Over the power-badge ceiling (125) on BOTH faces — the smart face a player actually reads in every fight involving an Electro aura is 134% of ceiling. "**a** Electro hit" is also a grammar error (needs "an"); Pyro/Hydro/Cryo don't have this problem, so it's Electro-only. Semicolon violates rule 14. |
| Hydro Aura, both faces (`Powers/AuraPower.cs:48-60`) | shared power badge | smart: "Hydro clings to this enemy for 2 more turns. A hit of a different element consumes the aura and triggers an Elemental Reaction; a Hydro hit refreshes its duration." / static: "Hydro clings to this enemy. A hit of a different element consumes the aura and triggers an Elemental Reaction; a Hydro hit refreshes its duration." | 163 / 146 | F1, F7 | Same template, same overage, no grammar bug (H is a consonant sound). |
| Pyro Aura, both faces (`Powers/AuraPower.cs:48-60`) | shared power badge | smart: "Pyro clings to this enemy for 2 more turns. A hit of a different element consumes the aura and triggers an Elemental Reaction; a Pyro hit refreshes its duration." / static: "Pyro clings to this enemy. A hit of a different element consumes the aura and triggers an Elemental Reaction; a Pyro hit refreshes its duration." | 161 / 144 | F1, F7 | Same template, same overage. |
| Cryo Aura, both faces (`Powers/AuraPower.cs:48-60`) | shared power badge | smart: "Cryo clings to this enemy for 2 more turns. A hit of a different element consumes the aura and triggers an Elemental Reaction; a Cryo hit refreshes its duration." / static: "Cryo clings to this enemy. A hit of a different element consumes the aura and triggers an Elemental Reaction; a Cryo hit refreshes its duration." | 161 / 144 | F1, F7 | Same template, same overage. All four elements share one abstract class (`AuraPower`) — one fix in the template clears all eight rows at once. |
| Kokomi, character select (`Kokomi.cs:40-42`) | selection-screen prompt | "Divine Priestess of Watatsumi Island, and the strategist who wins by spending everything except lives." | 102 | F1, F5 | 17 chars over the selection-screen ceiling (85); Klee's line is 30 chars, Furina's is 53. "Wins by spending everything except lives" is also an odd turn of phrase to parse on a first read. |
| Salon Solitaire (`Relics/SalonSolitaire.cs:57-64`) | relic (Furina Stage starter) | "Start each combat with the Gentilhomme Usher in the front seat at 3 Fanfare." | 76 | F3, F4 | "Seat" is the internal/design word for this concept (it's how the mod's own engine code talks about Salon slots throughout `FurinaStageLedger.cs`, `FurinaStagePlacement.cs`, etc.) — but every OTHER player-facing Stage row uses "**performer**": `AllTheWorldsAStage.cs:60` "the back performer", `StageRaisePerTurnPower.cs:35` "the back performer", `FurinaStagePowers.cs:59` "on the back performer". This one relic prints the engine word instead of the established player-facing word, and it's also the only one of the four not wrapped in `[gold]…[/gold]` the way "back performer" is elsewhere. |
| Pounding Surprise (`Relics/PoundingSurprise.cs:76-80`) & Dodoco Tales (`Relics/UpgradedStarterRelics.cs:157-165`) | relic (Klee starter) and its Ancient upgrade | Both: "Whenever a Bomb goes off, gain 1 Spark." | 39 / 39 | F4, F5 | Byte-for-byte the same sentence. Dodoco Tales is what an act-2 Touch of Orobas turns Pounding Surprise INTO — under this arm its opening-Spark-bank half is deliberately gated off (code comment), so the "upgraded" relic's own printed text is indistinguishable from the relic it replaced. A player reading the two side by side (e.g. at a Touch of Orobas choice) has no textual signal anything changed. |
| Reaction preview: Frozen (`KleeMod.cs:320-322`, `card_keywords.json` key `KLEEMOD-FROZEN_PREVIEW`) | shared keyword tip | "Hydro meets Cryo: its next action deals half damage, and until it acts the first Attack to hit it Shatters for 6 damage." | 120 | F4 | Says "half damage" and "Shatters for 6 damage". The Frozen badge itself (`Powers/FrozenPower.cs:66-68`, clean, listed below) says "50% less damage" and "Shatters it for 6 unblockable damage" for the IDENTICAL rule — two different spellings of one number, on two surfaces a player reads back to back (hover the keyword, then hover the badge on the enemy). The badge's "unblockable" also doesn't appear in the preview at all. |
| Reaction preview: Frozen (Boss) (`KleeMod.cs:323-325`, `KLEEMOD-FROZEN_BOSS_PREVIEW`) | shared keyword tip | "Bosses cannot be Frozen. Hydro plus Cryo is consumed and applies 2 Vulnerable instead." | 86 | F4 | Every other reaction-preview row in this same glossary uses the pattern "X meets Y" (Pyro meets Hydro, Pyro meets Cryo, Pyro meets Electro, Electro meets Cryo, Hydro meets Electro, Hydro meets Cryo — the row directly above this one — Geo meets an aura, Anemo meets an aura). This is the one row that says "Hydro plus Cryo" instead, immediately under the row that got it right. |
| Reaction preview: Overload (`KleeMod.cs:290-292`, `KLEEMOD-OVERLOAD_PREVIEW`) | shared keyword tip | "Pyro meets Electro: 6 damage to ALL enemies and 1 Weak on the reacted enemy." | 76 | F4 | No verb before the numbers. Its siblings all state a verb: Vaporize/Melt "this hit **deals** …", Superconduct/Electro-Charged "the reacted enemy **gains** …", Frozen "its next action **deals** …". This row and Crystallize (below) are the two exceptions. |
| Reaction preview: Crystallize (`KleeMod.cs:329-345`, `KLEEMOD-CRYSTALLIZE_PREVIEW`) | shared keyword tip | "Geo meets an aura: 4 Block, and the aura is consumed -- nothing is left to react with." | 86 | F4, F7 | Same missing-verb pattern as Overload ("4 Block" with no verb). Also carries a double-hyphen dash mid-sentence, which house rule 14 bans outright ("no dashes of any kind"). |
| Applies Anemo (`KleeMod.cs:270-272`, `KLEEMOD-APPLIES_ANEMO`) | shared keyword tip | "Another aura: consumed, and an Elemental Reaction triggers. No aura: nothing happens. Anemo never stays on a body." | 114 | F4 | Leads with "Another aura", then "No aura". Its four siblings — Applies Pyro/Hydro/Electro/Cryo (clean, listed below) — all lead "No aura: … Another aura: …", the opposite order. |
| Applies Geo (`KleeMod.cs:273-275`, `KLEEMOD-APPLIES_GEO`) | shared keyword tip | "Another aura: consumed, and an Elemental Reaction triggers. No aura: nothing happens. Geo never stays on a body." | 110 | F4 | Same clause-order swap as Applies Anemo, same fix. |
| Reaction preview: Electro-Charged (`KleeMod.cs:307-319`, `KLEEMOD-ELECTRO_CHARGED_PREVIEW`) | shared keyword tip | "Hydro meets Electro: the reacted enemy gains 4 Poison, losing that much HP at the start of its turn, 1 less each turn." | 118 | F2 | Spells out Poison's own rule ("losing that much HP at the start of its turn, 1 less each turn") instead of golding the keyword and letting Poison's own tip carry it — every other reaction-preview row in this glossary just names the keyword it applies (Vulnerable, Weak, Block) and stops. |
| Stage Combat / `warmup_act` (`Cards/Furina/Generated/WarmupAct.cs:47-49`) | Furina Stage-pool card (common) | "Deal 3 damage. If an enemy intends to attack: gain 3 Block." | 59 | F7 | Colon after the conditional clause. House rule 7 spells a card conditional "If X, Y." (comma) — never "If X: Y." This is a systemic codegen pattern, not a one-off: `EagerToHelp.cs:40`, `AudienceParticipation.cs:44`, `DirectorsCut.cs:48` and `CurtainCue.cs:44` all print the same colon-conditional shape from the same codegen "conditional" effect op (those four just aren't reachable under this arm right now, since they read a retired word). |
| Crashing Waves (`Cards/Furina/Generated/CrashingWaves.cs:44`) | Furina Stage-pool card (uncommon) | "Deal 8 damage to ALL enemies. +5 damage if the enemy has an elemental aura." | 75 | F4, F5 | "+5 damage" instead of the house's "N additional damage" (rule 8) — its own siblings `FlameDance.cs:46` ("take {ExtraDamage} more") and `ClorindeImpaleTheNight.cs:61` / `AlbedoSolarIsotoma.cs:51` ("N additional damage") don't use a bare "+N". "The enemy" is also singular inside an ALL-enemies hit, which reads ambiguously about which body is meant. |
| Courtroom Drama (`Cards/Furina/Generated/CourtroomDrama.cs:44`) | Furina Stage-pool card (uncommon) | "Your first Elemental Reaction each turn applies 1 Vulnerable and 1 Weak to its target. The Vulnerable moves that hit." | 117 | F5, F6 | Under the card ceiling (120) but close, and the trailing clause "The Vulnerable moves that hit" is genuinely hard to parse — it means the Vulnerable amplifies the very hit that triggered the reaction, which the Superconduct preview (clean, above) says far more plainly: "gains 2 Vulnerable, which applies before this hit." |
| Princess of Watatsumi, arm face (`Cards/Kokomi/PrincessOfWatatsumi.cs:86-91`) | Ancient card (Kokomi) | "Whenever the Bake-Kurage carries out a Plan, gain 2 Block and draw 1 card." | 74 | F4 | Two effects under one trigger joined with "and" in a single sentence. Its own sibling in the Stage pool, The Witness Stand, prints the same Apply+Draw shape as two short sentences instead ("Apply 1 Vulnerable. Draw 1 card."). |

## Patterns

1. **Banned punctuation still leaks into shared tips.** House rule 14 bans
   semicolons (outside an either/or) and dashes of any kind. The Aura badge's
   two faces (all 4 elements, 8 rows) carry a semicolon; Crystallize's
   preview and the Burst tip carry a dash; the Burst tip carries both. Six of
   the sixteen shared-badge flags above are pure punctuation.
2. **The two biggest overages are both "explainer" tips nobody trimmed.**
   Burst Energy (374/135) and the four Element Auras (144-167/125) are the
   mod's two most-seen shared surfaces — a Burst-using card in hand, an aura
   on nearly every enemy — and both read like a first draft that was never
   run through the same compression pass every kit-specific keyword tip in
   `ArmKeywordTips.cs` visibly went through (documented trims down to "132 of
   135," "133 of 135" for Set off/Bomb/Mine/Plan).
3. **Two spellings of one rule, read back to back.** Frozen's badge ("50%
   less damage" / "unblockable damage") and its own reaction-preview tip
   ("half damage" / "damage") describe the identical rule differently, and a
   player meets both on the same hover chain.
4. **A relic "upgrade" that prints no upgrade.** Pounding Surprise and Dodoco
   Tales read identically under this arm — an Ancient reward with nothing
   textually different to show for it.
5. **The reaction-preview glossary has two small internal inconsistencies
   nobody would catch without reading all nine rows side by side:** Overload
   and Crystallize drop the verb their five siblings all use ("deals"/
   "gains"); Frozen (Boss) breaks the "X meets Y" pattern every other row
   (including the row directly above it) uses; Applies Anemo/Geo reverse the
   clause order their four elemental siblings use.
6. **"Seat" vs "performer."** Salon Solitaire is the one player-facing Stage
   string using the engine's internal word ("front seat") where every other
   Stage card and power uses the established player-facing word
   ("performer").

## Clean ids

**Ancients (2/3):** Jumpy Dumpty Mk.Omega, arm face (`Cards/JumpyDumptyMkOmega.cs`) —
"Deal 12 damage to a random enemy 3 times. Place a Bomb 12 on ALL enemies." ·
All the World's a Stage, Stage face (`Cards/Furina/AllTheWorldsAStage.cs`) —
"At the start of your turn, Raise 2 Fanfare on the back performer."

**Furina Stage-pool cards (11/14):** Commanding Gaze ("Gain 2 Block. Apply 1
Weak to ALL enemies."), Undercurrent ("Deal 2 damage to ALL enemies 3
times."), The Guest List ("Add 1 random Uncommon Companion card to your
hand. Gain 1 Energy."), Duet ("The next Companion card you play this turn is
played an extra time. Draw 1 card."), Quick Change ("The first Attack you
play each turn draws 1 card."), The Witness Stand ("Apply 1 Vulnerable. Draw
1 card."), Singer of Many Waters ("Heal 6 HP."), Command Performance ("Add 2
random Uncommon Companion cards to your hand."), Soloist's Solicitation
("Deal 6 damage."), Stage Presence ("Gain 6 Block."), Regal Bearing ("Gain 3
Block. Apply 1 Weak.") — all `Cards/Furina/Generated/*.cs`.

**Status (2/2):** Confiscated, card face ("Does nothing.",
`Cards/Confiscated.cs`) and its keyword tip ("A 1-cost Status card that does
nothing.", `KleeMod.cs`, `KLEEMOD-CONFISCATED`).

**Relics (1/4 reachable):** Tamakushi Casket ("Start each combat with the
Bake-Kurage. Each debuff you apply lands a real 2 Hydro hit on that enemy.",
101 chars, `Relics/TamakushiCasket.cs`) — under the relic ceiling (120); its
own history of getting misread ("real" was added at `EB-348` specifically to
head off the "is this a flat number" confusion) has already been fixed.

**Shared badges / keyword tips (16/32):** Element Aura titles, all four
("Pyro Aura" / "Hydro Aura" / "Electro Aura" / "Cryo Aura") · Frozen badge
("Its next action deals 50% less damage. Until it acts, an Attack Shatters
it for 6 unblockable damage and removes Frozen.", 120/125, `Powers/FrozenPower.cs`) ·
Shattering Pressure ("Your Shatters deal N additional damage.",
`Powers/CompanionPowers.cs`, companion-granted, shared badge) · reaction
previews Vaporize, Melt, Superconduct, Swirl · Applies Pyro, Applies Hydro,
Applies Electro, Applies Cryo · Elemental Skill tip ("Playing this card
grants 5 Burst Energy.") · `KLEEMOD-TURN_END_DOCKET` UI label ("END OF
TURN").

**Character select (2/3):** Klee — "The Spark Knight of Mondstadt." (30
chars, `Klee.cs`) · Furina — "The Regina of All Waters, Kindreds, Peoples
and Laws." (53 chars, `Furina.cs`) — both well under the selection-screen
ceiling (85).
