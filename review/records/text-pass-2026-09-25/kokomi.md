# Kokomi prototype arm — text census

**Surfaces read:** 45 card rows (44 `proto_kk_*` rows in `docs/prototype-surface.yaml`
— the `Slice()` + `MultiplayerSlice()` + the two starters — plus the Ancient
tail card `PrincessOfWatatsumi`'s arm branch); 6 Kokomi-scoped keyword tips in
`klee-mod/KleeCode/Cards/Prototype/ArmKeywordTips.cs` (`ForPlan`, `ForDusk`,
`ForPlanElement`, `ForPlanTwice`, `ForMend`, `ForCasket`); 13 power/pet badges
in `KokomiOverhaulPowers.cs`, `KokomiPlan.cs` and `ProtoBakeKuragePower.cs`;
1 relic (`TamakushiCasket.cs`); 1 selection-screen prompt (Moon's Reflection's
exhaust-pile picker, in `KokomiPlan.cs`). `BakeKurageMonster` (the pet's
name/title only, no body text) was checked and carries nothing to measure.
Card lengths are measured on the CODEGEN-RENDERED face (BBCode stripped, each
`{hole}` as one numeral), which for exhaust cards drops the printed
"Exhaust." lead-in and for `Breakwater` (the one Plan-only row, no now-line)
adds the codegen's "Play on the [gold]Bake-Kurage[/gold]. " prefix — both per
`tools/gen_klee_cards.py`'s `_dedupe_printed_exhaust` / `_plan_only_line`.

**Rows flagged: 20. Rows clean: 46.**

## Flagged rows, worst first

| id | kind | current text (rendered) | chars | flags | note |
|---|---|---|---|---|---|
| `ArmKeywordTips.ForPlan` (Plan keyword tip) | tip | "On the Bake-Kurage, paid now; any number wait, in order, and the badge is their count. Next turn: front non-Minion, or ALL, Minions too, into Block still standing. Your Strength folds as you write it; the enemy's Vulnerable counts next turn. A carry-out is not a hit: no when-hit power fires." | 292 | F1, F5, F6 | more than double the 135-char tip ceiling (4 sentences, two non-either/or semicolons); it is the tooltip a player reads on every single Kokomi card, and it reads as a rules essay covering six separate findings at once |
| `proto_kk_battle_plan` (Battle Plan) | card | "Draw 3 cards. Plan: Next turn, your Attacks deal 3 additional damage." | 69 | F8 | "your Attacks" (plural, unscoped) reads as every Attack for the rest of the turn — the shipped `AttackUpThisTurnPower` template this phrasing echoes — but the power it actually applies, `NextAttackDamagePower`, removes itself the moment the FIRST qualifying Attack resolves (`KokomiOverhaulPowers.cs:390-401`, `AfterCardPlayed`/`IsLastInSeries`); its own co-op twin Coordinated Strike, worded almost identically, genuinely does last the whole turn because it applies the shipped `AttackUpThisTurnPower` instead (`KokomiPlan.cs:196-203`) |
| `ProtoBakeKuragePower` (Bake-Kurage badge) | power | "Enemies cannot target it, all combat. Holds any number of Plans, each carried out next turn, or at this turn's end if Dusk." | 123 | F2, F5 | "all combat" is an odd, clipped idiom for "for the whole fight"; the Dusk-timing clause here restates the same fact `ForDusk`'s tip and the Plan badge below both also carry |
| `PendingPlansPower` (Plan badge) | power | "Carries out 3 Plans in order next turn; a Dusk Plan at this turn's end. Later debuffs do not change what you wrote." | 115 | F2, F5 | semicolon used outside an either/or (rule 14); restates the Dusk-timing fact a third time (see `ForDusk`, `ProtoBakeKuragePower` above) |
| `proto_kk_opening_gambit` (Opening Gambit) | card | "Deal 5 damage. Plan: Apply 1 Vulnerable to ALL enemies. Doubles the damage of the next Plan carried out with this one." | 118 | F1, F3, F5 | 3 sentences; the third is a subjectless fragment ("Doubles..." — doubles what?); "carried out with this one" is the exact undefined jargon phrase the house style calls out by name |
| `proto_kk_second_wave` (Second Wave) | card | "Gain 4 Block. Plan: The next Plan carried out with this one is carried out twice." | 81 | F3 | "carried out with this one" — undefined jargon about drain order, printed on the card with nothing on screen defining "this one" |
| `proto_kk_scout_ahead` (Scout Ahead) | card | "Draw 1 card. Plan: Draw 1 card for each later Plan carried out with this one." | 77 | F3 | same jargon phrase as Opening Gambit and Second Wave |
| `proto_kk_moons_reflection` (Moon's Reflection) | card | "Choose a card in your Exhaust Pile. Next turn, the Bake-Kurage carries out its Plan line, or plays it if it has none." | 117 | F3 | "Plan line" — "line" is never defined as a term for players; a reader has to guess it means "the printed Plan sentence on the card" |
| `KokomiPlan.ReflectionPromptText` (Moon's Reflection selection prompt) | selection prompt | "Choose a card. The Bake-Kurage carries out its Plan line, or the card if it has none." | 85 | F3 | same "Plan line" jargon, and sits exactly at the 85-char prompt ceiling |
| `proto_kk_read_the_field` (Read the Field) | card | "Look at the top 4 cards of your draw pile; put one into your hand and the rest on the bottom. Plan: Gain 10 Block." | 113 | F5 | semicolon used outside an either/or (rule 14) |
| `proto_kk_breakwater` (Breakwater) | card | "Play on the Bake-Kurage. Dusk Plan: Gain 5 Block, plus 3 for each Plan the Bake-Kurage is holding." (the lead sentence is codegen-added because this is the one Plan-only row) | 98 | F4, F5 | "Bake-Kurage" is printed twice on the same face, once in the auto-added lead sentence and once mid-sentence; reads as repetitive rather than as one rule |
| `proto_kk_feint` (Feint) | card | "Deal 5 damage. If a Plan was carried out this turn, deal 10 damage instead. Plan: Apply 1 Vulnerable." | 100 | F1, F5 | 3 sentences; the conditional ("if a Plan was carried out this turn") can be satisfied by any card's Plan, not just this one, and nothing on the face signals that |
| `proto_kk_slack_water` (Slack Water) | card | "Deal 4 damage. Apply 1 Weak. Plan: Apply 1 Weak to ALL enemies." | 63 | F1 | 3 sentences on a starter card (the first card new players see) |
| `proto_kk_vanguard` (Vanguard) | card | "Apply 1 Vulnerable. Draw 1 card. Plan: Gain 1 Energy." | 53 | F1 | 3 sentences |
| `proto_kk_cleansing_wave` (Cleansing Wave) | card | "Gain 5 Block. Remove one of your debuffs. Plan: Gain 10 Block." | 62 | F1 | 3 sentences |
| `proto_kk_feigned_retreat` (Feigned Retreat) | card | "Gain 6 Block. Plan: Deal 9 damage. If you lost no HP since you wrote this, deal 14 instead." (upgraded: "...Deal 12 damage. If you lost no HP since you wrote this, deal 18 instead.") | 91 | F1 | 3 sentences |
| `proto_kk_chain_of_command` (Chain of Command) | card | "Deal 3 damage for each Companion you played this turn. Plan: Deal 6 damage for each Companion you played last turn." | 115 | F5 | two clauses that differ only by "this turn" vs. "last turn" sit back to back and are easy to misread as the same count |
| `proto_kk_tide_wall` (Tide Wall) | card | "Gain 4 Block. Plan: Gain Block equal to the damage the enemy intends to deal." (upgraded: "...the enemy intends to deal, plus 3.") | 77 (85 upgraded) | F5 | the face reads as "the intent you see now," but the Plan resolves next turn, so the number it actually reads is a fresh intent rolled a turn later — the row's own dev comment concedes this was "re-aimed" for exactly that reason, and none of it is on the card |
| `proto_kk_well_laid` (Well Laid) | card | "Deal 4 damage, plus 4 for each debuff on the enemy." | 51 | F4 | drops the convention's "N additional damage for each X" template (rule 8) for "plus N for each" |
| `proto_kk_riptide` (Riptide) | card | "Deal 9 damage to ALL enemies, and 4 more to each enemy with a debuff. Plan: Gain 1 Energy and draw 1 card." | 106 | F4 | a third spelling of the same "bonus vs. a debuffed target" idea (see Well Laid, and Undertow's "deal X instead") — three siblings, three idioms |

## Patterns

1. **Three-sentence card faces exceed the census's own 2-sentence ceiling.**
   `proto_kk_slack_water`, `proto_kk_feint`, `proto_kk_vanguard`,
   `proto_kk_cleansing_wave`, `proto_kk_feigned_retreat` and
   `proto_kk_opening_gambit` all print 3 sentences — one of them (Slack Water)
   is a starter card, so it is the first thing a new Kokomi run shows.
2. **"Carried out with this one" is undefined jargon on three reward cards.**
   `proto_kk_opening_gambit`, `proto_kk_second_wave`, `proto_kk_scout_ahead`.
   This is the literal phrase the house style guide names as an example of
   design jargon that never gets defined for a player.
3. **"Plan line" is a second undefined term, printed on two surfaces.**
   `proto_kk_moons_reflection` and `KokomiPlan.ReflectionPromptText` both use
   it to mean "the printed Plan sentence on a card," which is never stated.
4. **Semicolons outside an either/or, banned by text-conventions rule 14,
   show up on the kit's highest-traffic surfaces.** `ArmKeywordTips.ForPlan`,
   `PendingPlansPower` and `proto_kk_read_the_field`.
5. **The Dusk-timing rule is stated three separate times.** `ForDusk`'s
   keyword tip, `ProtoBakeKuragePower`'s badge and `PendingPlansPower`'s badge
   each independently explain when a Dusk Plan resolves — a player meets the
   same sentence, worded three different ways, on three different screens.
6. **The Plan tip is the single worst offender on the whole arm.**
   `ArmKeywordTips.ForPlan` renders at 292 characters against a 135-character
   ceiling (more than double), carries four sentences against the rule-14
   guidance of one to three, and uses two semicolons that are not either/or
   pairs. It is also the tip every Kokomi card attaches, so it is the most
   frequently read string in the kit.

## Clean

`proto_kk_kurages_oath`, `proto_kk_ambush`, `proto_kk_exposed_flank`,
`proto_kk_treatise`, `proto_kk_song_of_pearls`, `proto_kk_war_council`,
`proto_kk_nereids_ascension`, `proto_kk_sea_salt_prayer`,
`proto_kk_deep_current`, `proto_kk_coral_bulwark`, `proto_kk_shell_guard`,
`proto_kk_the_clouds_like_waves`, `proto_kk_the_moon_a_ship`,
`proto_kk_sango_isshin`, `proto_kk_rally`, `proto_kk_the_generals_banner`,
`proto_kk_stolen_chapter`, `proto_kk_change_of_plans`, `proto_kk_undertow`,
`proto_kk_salt_line`, `proto_kk_tide_chart`, `proto_kk_ripple`,
`proto_kk_pincer`, `proto_kk_flank`, `proto_kk_second_thoughts`,
`proto_kk_joint_orders`, `proto_kk_coordinated_strike`,
`proto_kk_sangonomiyas_counsel`, `PrincessOfWatatsumi` (Ancient, arm branch),
`ArmKeywordTips.ForDusk`, `ArmKeywordTips.ForPlanElement`,
`ArmKeywordTips.ForPlanTwice`, `ArmKeywordTips.ForMend`,
`ArmKeywordTips.ForCasket`, `TreatisePower`, `SongOfPearlsPower`,
`PrincessOfWatatsumiPlanPower`, `CloudsLikeWavesPower`,
`GeneralsBannerPower`, `NextCompanionDiscountPower` (Rally's grant),
`NextAttackDamagePower` (its own badge text, as opposed to the card face
above), `FirstAttackTwicePower` (Pincer's grant), `FirstCardFreePower`
(Stolen Chapter's grant), `ShellGuardPower`, `NereidsAscensionPower`,
`TamakushiCasket` (relic), `BakeKurageMonster` (name/title only).
