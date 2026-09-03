Status: RULED R249 2026-09-03

# The shipped sheets' text against text-conventions.md

What this is: the three shipped card sheets (`docs/klee-cards.yaml`,
`docs/kokomi-cards.yaml`, `docs/furina-cards.yaml`), the shipped companion
rows, the shipped powers and relics, and the keyword tips `KleeMod.cs`
registers, read against `docs/current/text-conventions.md`. Nothing here is
applied. The prototype arms took the same pass in this PR and are lint-gated
now; the shipped surfaces are a report until [USER] picks below.

The numbers, from `python tools/lint_text_conventions.py --shipped` on this
branch: 356 shipped strings (280 card faces, 54 powers, 15 tips, 5 relics,
2 mode faces). 20 are over their ceiling. 95 findings in all: 25 say "N more
damage" where the base says "N additional damage", 19 print Block or Weak
without the gold the base always gives them, 8 say a Bomb "detonates", 5
carry a parenthesis ("turn(s)"), 4 powers say "Lasts N more turns", 5 upgrade
clauses are longer than any the base prints, 3 faces run past four sentences,
2 tips say "all enemies" in lowercase, 1 says "the jellyfish", 1 says "draw 3"
without the noun.

A caution on the shipped Klee and Kokomi rows. Both kits are being replaced
by the prototype arms this PR rewrote (`STATE.md`, Active workstreams), so a
rewrite of their shipped faces is work the overhaul deletes. The Furina sheet,
the shipped companion rows, the shared keyword tips and the relics are the
part of this list that lasts.

## The worst 30, before and after

Lengths are rendered characters (tags stripped, each hole one numeral), the
ceiling in brackets. "After" moves no number, cost, target or effect; where
it cannot meet the ceiling the row says so.

| # | string | before (length) | after (length) |
|---|---|---|---|
| 1 | `KurageSummonPower` badge [125] | "At the end of your turn, the jellyfish answers the last card you played this turn. After an Attack: it deals 6 damage and applies Hydro to a random enemy. After a Skill: it grants 6 Block. After a Power: it banks 6 Charge. If you played no card at all, it does nothing. It stays on the field for the whole fight." (354, 7 sentences) | "At the end of your turn the [gold]Bake-Kurage[/gold] answers your last card: Attack, [blue]6[/blue] [gold]Hydro[/gold] damage to a random enemy; Skill, [blue]6[/blue] [gold]Block[/gold]; Power, [blue]6[/blue] [gold]Charge[/gold]. Stays all combat." (123) |
| 2 | `BombPower.smartDescription` [125] | "Detonates at the start of your turn for {Damage} total damage ({Amount} Bombs). Detonates early if this enemy takes unblocked Attack damage. The first attack this enemy makes while Bombed each combat deals 25% less damage." (208) | "[blue]{Damage}[/blue] damage at the start of your turn, or early when this enemy takes unblocked Attack damage. Bombs here: [blue]{Amount}[/blue]. Its first attack while Bombed deals 25% less." (148; three rules plus a live count, an exception unless the 25% rule moves to the Bomb tip alone) |
| 3 | `BombPower.description` [125] | "Detonates at the start of your turn for its damage. Detonates early if this enemy takes unblocked Attack damage. The first attack this enemy makes while Bombed each combat deals 25% less damage." (194) | "Goes off at the start of your turn for its damage, or early when this enemy takes unblocked Attack damage. Its first attack while Bombed deals 25% less." (108) |
| 4 | `CurtainNeverFalls` relic [120] | "Center Stage and Guest Cast are both always active, and you always count as having moved the Spotlight this turn." + slot sentence (174) | "Center Stage and Guest Cast are always active. You always count as having moved the Spotlight." + slot sentence (152; over by the 59-character slot sentence, pick 4) |
| 5 | `KLEEMOD-BOMB` tip [135] | "Detonates at the start of your turn or early when its enemy takes unblocked Attack damage. The first attack that enemy makes while Bombed each combat deals 25% less damage." (172) | "Goes off at the start of your turn, or early when its enemy takes unblocked Attack damage. That enemy's first attack while Bombed deals 25% less." (135) |
| 6 | `what_the_tokoyo_returns` [120] | "Choose a card from your discard pile; put it on top of your draw pile. Gain 6 Block. Sly: Choose a card from your discard pile; put it on top of your draw pile." (160) | "Put a card from your [gold]Discard Pile[/gold] on top of your [gold]Draw Pile[/gold]. Gain 6 [gold]Block[/gold]. [gold]Sly[/gold]: Put a card from your Discard Pile on top of your Draw Pile." (138; `HEADBUTT`'s sentence twice, still over: the Sly body restates the whole card) |
| 7 | `KLEEMOD-OVERLOAD_PREVIEW` tip [135] | "This card supplies Pyro or Electro while an enemy has the other aura. It deals 6 splash damage to all enemies and applies 1 Weak to the reacted enemy." (150) | "Pyro meets Electro: [blue]6[/blue] damage to ALL enemies and [blue]1[/blue] [gold]Weak[/gold] on the reacted enemy." (84) |
| 8 | `ExplosiveFrags` relic [120] | "At the start of combat, gain 3 Spark. Whenever a Bomb detonates, gain 1 Spark." + slot sentence (139) | "Start each combat with [blue]3[/blue] [gold]Sparks[/gold]. Whenever a [gold]Bomb[/gold] goes off, gain [blue]1[/blue] [gold]Spark[/gold]." + slot sentence (138; pick 4) |
| 9 | `KLEEMOD-ELECTRO_CHARGED_PREVIEW` tip [135] | "This card supplies Hydro or Electro while an enemy has the other aura. The reacted enemy gains a 4-damage decaying damage-over-time effect." (139) | "Hydro meets Electro: the reacted enemy loses [blue]4[/blue] HP at the start of its turn, 1 less each turn." (85) |
| 10 | `standing_ovation` [120] | "Whenever you spend Encore, Spotlighted Companion numbers are 10% stronger this turn. The first Spotlighted card each turn grants 1 Encore." (138) | "[gold]Spotlighted[/gold] Companions are 10% stronger on turns you spend [gold]Encore[/gold]. The first Spotlighted card each turn grants 1 Encore." (119) |
| 11 | `vigil_of_the_deep`, `watch_of_the_shallows`, `PreventExhaustWardPower` [120/125] | "The first time you would take unblocked attack damage each turn, prevent up to 6 of it and Exhaust a random card from your draw pile." (133, three copies) | "The first unblocked Attack damage each turn is reduced by up to 6, and a random card in your [gold]Draw Pile[/gold] is [gold]Exhausted[/gold]." (116) |
| 12 | `FrozenPower` badge [125] | "This creature's next action deals 50% less damage. The first Attack that hits it Shatters for unblockable damage and removes Frozen." (132) | "Its next action deals 50% less damage. The first Attack to hit it Shatters for [blue]6[/blue] unblockable damage." (102, `ShatterDamage` interpolated) |
| 13 | `shell_of_sanctuary` [120] | "Draw 2 cards. Choose a card from your Exhaust pile; put it on top of your draw pile. It gains Exhaust. Gain 2 Charge. Gain 6 Block." (131, 5 sentences) | "Draw 2 cards. Put a card from your [gold]Exhaust Pile[/gold] on top of your [gold]Draw Pile[/gold] with [gold]Exhaust[/gold]. Gain 2 [gold]Charge[/gold] and 6 [gold]Block[/gold]." (109) |
| 14 | `limelight` [120] | "Spend 1 Encore; lose HP for any shortfall. Spotlighted Companion numbers are 25% stronger this turn. Gain 1 Energy. Draw 2 cards." (129) | "Spend 1 [gold]Encore[/gold], paying HP for any shortfall. [gold]Spotlighted[/gold] Companions are 25% stronger this turn. Gain 1 [gold]Energy[/gold]. Draw 2 cards." (121, one over; four effects on one card) |
| 15 | `grand_gala` [120] | "Add 2 Mademoiselle Crabaletta to your Salon. Add 1 Surintendante Chevalmarin. Add 1 Gentilhomme Usher. Gain 6 Encore. Burst +5." (127, 5 sentences) | "Add 2 Crabaletta, 1 Chevalmarin and 1 Usher to your [gold]Salon[/gold]. Gain 6 [gold]Encore[/gold]. Burst +5." (86; the member tips carry the full names) |
| 16 | `EtherealSpotlightRelic` [120] | "At the start of each turn, add an Ethereal Spotlight to your hand." + slot sentence (127) | "At the start of your turn, add an [gold]Ethereal[/gold] [gold]Spotlight[/gold] to your [gold]Hand[/gold]." + slot sentence (123; pick 4) |
| 17 | `KLEEMOD-VAPORIZE_PREVIEW`, `KLEEMOD-MELT_PREVIEW` tips [135] | "This card supplies Pyro or Hydro while an enemy has the other aura. The triggering hit deals 1.5x damage and consumes the aura." (127, twice) | "Pyro meets Hydro: this hit deals 1.5x damage and consumes the aura." (66); "Pyro meets Cryo: this hit deals 1.75x damage and consumes the aura." (67) |
| 18 | `PearlOfWisdomRelic` [120] | "Whenever a card is Exhausted, gain 1 Charge and 5 Burst Energy." + slot sentence (124) | unchanged but for `[blue]` numerals (124; pick 4) |
| 19 | `chevreuse_vanguards_valor` [120] | "Your next Attack deals 6 more damage. If an Elemental Reaction triggered this turn: your next Attack deals 3 more damage." (121) | "Your next Attack deals 6 additional damage, plus 3 if an [gold]Elemental Reaction[/gold] triggered this turn." (92) |
| 20 | `undertow` (Kokomi) [120] | "Deal 6 damage, already including the cards Exhausted. If 3 or more cards are Exhausted: draw 1 card. Sly: Gain 1 Energy." (120) | "Deal 6 damage. If 3 or more cards are [gold]Exhausted[/gold], draw 1 card. [gold]Sly[/gold]: Gain 1 [gold]Energy[/gold]." (83; the "already including" disclosure is `EB-164`'s, so it stays if `lint_face_scaling` still wants it, in the base's own form: `{InCombat: (Deals 6 damage)\|}`) |
| 21 | `KLEEMOD-APPLIES_PYRO` and the other three element tips [135] | "If the target has no aura, this applies Pyro for 2 turns. A different aura is consumed to trigger a Reaction instead." (117 to 120, four copies, also in `tools/build_pck.ps1`) | "No aura: applies [gold]Pyro[/gold] for [blue]2[/blue] turns. Another aura: consumed, and an [gold]Elemental Reaction[/gold] triggers." (99) |
| 22 | `universal_revelry` [120] | "Deal 6 damage to ALL enemies, already including Fanfare. If you have at least 15 Fanfare: deal 6 damage to ALL enemies." (119) | "Deal 6 damage to ALL enemies. If you have 15 or more [gold]Fanfare[/gold], repeat." (72, `ECHOING_SLASH`'s verb; same disclosure note as row 20) |
| 23 | `pit_orchestra` [120] | "Whenever a Salon Member takes its final bow, gain 6 Block. Whenever a Salon Member takes its final bow, gain 2 Encore." (118, one trigger written twice) | "Whenever a [gold]Salon Member[/gold] takes its final bow, gain 6 [gold]Block[/gold] and 2 [gold]Encore[/gold]." (82) |
| 24 | `blazing_delight`, `DetonationSplashPower` [120/125] | "When a Bomb detonates: deal 6 damage to ALL enemies, ignoring Block, and gain 3 Burst Energy. Up to 3 times per turn." (117) | "Whenever a [gold]Bomb[/gold] goes off, deal 6 damage to ALL enemies, ignoring [gold]Block[/gold], and gain 3 [gold]Burst Energy[/gold]. Up to 3 times per turn." (117; the rule fixes, not the length) |
| 25 | `durin_witchs_flame`, `WitchsFlamePower` [120/125] | "At the end of your turn, consume Pyro from each enemy. For each aura consumed, deal 6 damage and gain 3 Burst Energy." (117) | "At the end of your turn, consume each enemy's [gold]Pyro[/gold]: deal 6 damage to it and gain 3 [gold]Burst Energy[/gold] per aura." (106) |
| 26 | `audience_participation` [120] | "If an Elemental Reaction triggered this turn: gain Encore and draw 2 cards. Otherwise: gain Encore and draw 1 card." (115) | "Gain [gold]Encore[/gold]. Draw 1 card, or 2 if an [gold]Elemental Reaction[/gold] triggered this turn." (76) |
| 27 | `change_the_bill` [120] | "The leftmost member of your Salon moves to the back. The leftmost member of your Salon performs now. Gain 6 Block." (114) | "Move the front [gold]Salon[/gold] member to the back; the new front member performs now. Gain 6 [gold]Block[/gold]." (91) |
| 28 | `full_ensemble` [120] | "Add 1 Gentilhomme Usher to your Salon. Add 1 Surintendante Chevalmarin. Add 1 Mademoiselle Crabaletta. Burst +5." (112) | "Add 1 Usher, 1 Chevalmarin and 1 Crabaletta to your [gold]Salon[/gold]. Burst +5." (72) |
| 29 | `arlecchino_masque_red_death`, `MasqueRedDeathPower` [120/125] | "At the start of each turn, gain 6 Strength. Each turn your Bond of Life consumes the first 5 Block you gain." (108) | "At the start of your turn, gain 6 [gold]Strength[/gold]. Your [gold]Bond of Life[/gold] eats the first 5 [gold]Block[/gold] you gain each turn." (100) |
| 30 | `shoulder_to_shoulder` upgrade clause [20] | "{IfUpgraded:show:Add a copy of a random Companion card in your hand to your hand. The copy costs 0.\|}" (an 82-character upgrade clause; the base's longest is 18) | print the added effect as a base sentence with `{IfUpgraded:show:...}` on the one word that changes, `DUAL_WIELD`'s shape: "Add a copy of a random [gold]Companion[/gold] card in your Hand to your Hand{IfUpgraded:show:. It costs 0\|}." |

## The rule-only families (no length problem)

- **"N more damage" to "N additional damage"** (25): `bennett_passion`,
  `careful_arrangement`, `chain_fuse`, `clorinde_impale_the_night`,
  `explosives_workshop`, `freminet_shattering_pressure`, `gorou_war_banner`,
  `powder_charge`, `remote_detonator`, `sara_crowfeather_cover`,
  `spark_knight_style`, `sparkly_explosion`, `before_sun_and_moon`,
  `rapturous_applause`, and the powers `AttackUpThisTurnPower`,
  `NextAttackUpPower`, `ShatterBonusPower`, `BombDamageUpPower`,
  `ExplosivesWorkshopPower`, `NightVigilPower`, `FanfareAttackPer10Power`.
  A word swap each.
- **Bare Block and Weak** (19): `kurages_oath`, `mercy_of_the_deep`,
  `pearl_current`, `tighten_the_cords`, `fortissimo_guard`, `pit_orchestra`,
  `gorou_heart_of_the_clan`, `blazing_delight`, `MetallicizePower`,
  `SalonDeployBlockPower`, `SalonBowBlockPower`, `DetonationSplashPower`,
  `KurageSummonPower` and the rest of the list the lint prints. The codegen
  emits the bare word from `APPLY_POWERS` templates that say "gain {X}
  Block"; one template edit per row.
- **"Lasts N more turns"** (4): `OzSummonPower`, `SolarIsotomaPower`,
  `SparksNSplashPower` and one more; "Lasts for {Amount} turns."
- **Parentheses** (5): "turn(s)" and "Member(s)" become
  `{Amount:plural:turn|turns}`; `BombPower.smartDescription`'s "({Amount}
  Bombs)" becomes a sentence, as the prototype badge's did.
- **"all enemies" in lowercase** (2): `KLEEMOD-SWIRL_PREVIEW`,
  `KLEEMOD-CRYSTALLIZE_PREVIEW`.
- **"draw 3." without the noun** (1): `deep_breath`.

## The picks

1. **Which shipped surfaces take the pass.** (a) Everything in the list now.
   (b) DEFAULT: the Furina sheet, the shipped companion rows, the shared
   keyword tips (rows 5, 7, 9, 17, 21 and the lowercase pair) and the powers
   and relics now; the shipped Klee and Kokomi rows only if their overhauls
   are rejected, because the overhauls replace them. (c) Nothing until each
   kit reaches Balance.
2. **The shipped Bomb's verb.** (a) DEFAULT: leave "detonates" on the shipped
   Klee kit until the overhaul replaces it; the two Bombs are two rules and
   two words is honest. (b) Rewrite to "goes off" now so both arms say one
   word.
3. **The Bomb badge's 25% clause** (row 2). (a) DEFAULT: keep the three rules
   on the badge and carry it as a lint exception, as the prototype's Mine
   faces are. (b) Move the 25% rule to the `KLEEMOD-BOMB` tip alone and let
   the badge print the number and the two triggers.
4. **The shared Companion-slot sentence** on every starting relic ("Card
   rewards after a fight offer a fourth Companion choice.", 59 characters,
   `CompanionSlot.RewardSlotDescription`). (a) DEFAULT: shorten it once to
   "Combat rewards offer a fourth [gold]Companion[/gold] card." (48), which
   brings rows 8, 16 and 18 under the ceiling and row 4 to 141. (b) Keep it
   and carry the four relics as exceptions.

## The picks, ruled R249 (2026-09-03)

[USER], verbatim: "On the test conventions: 1) Default b is fine, 2) default
a) is fine, 3) default is fine, 4) Let's just remove this text; it's universal
to all of the modded characters, so I would consider it a fact about the mod,
not the relic."

1. RULED (b): the Furina sheet, the shipped companion rows, the shared keyword
   tips (rows 5, 7, 9, 17, 21 and the lowercase pair) and the shipped powers
   and relics take the pass now; the shipped Klee and Kokomi rows only if
   their overhauls are rejected. Build row `EB-345`.
2. RULED (a): "detonates" stays on the shipped Klee kit until the overhaul
   replaces it.
3. RULED (a): the three rules stay on the badge, carried as a lint exception.
4. RULED, neither option: the Companion-slot sentence leaves every starting
   relic. It is a fact about the mod, so it is stated once at mod level, in
   the mod's description on the Mods screen, the derived home ([USER]
   vetoes). Build row `EB-346`.
