# Player English that a translation file cannot reach, 2026-10-23

Census at main 21a1d00d6 (`tools/player_text_census.py` plus a read of the
code). A translation is a table file keyed like
`klee-mod/localization/reference/eng.json`
(`docs/current/operations/localization.md`), so a line reaches a translated
player only if it goes through a loc key. Counts are sentence templates (a
template with a number slot counts once). Seat, bridge and log text is left
out.

**3,089 census items; about 92% are keyed. About 270 templates are built in
code,** almost all of them tips and live riders. Skipping them would ship
English hover boxes and live clauses beside translated cards.

| Area | Keyed | Built in code |
|---|---:|---:|
| Cards (faces and names) | 574 | 126 keyed faces carry English tokens filled from code (about 14 templates) |
| Powers and statuses | 234 | 12 Abyss Shadow bodies, 2 Yae enchantment bodies |
| Relics | 48 | 14 Abyss Blessing bodies |
| Potions | 15 | 0 |
| Keywords and tips | 106 | about 107 tip bodies |
| Previews and annotations | 10 | about 45 |
| UI panels | 3 | about 75 |
| Story, events, barks, Ancients | 2,177 | 5 templates |
| Spiral Abyss | 38 | about 52 |
| Character select and profile | 75 | 0 |

## The groups, in the order to key them

1. **Keyword tip bodies (about 107).** The title is keyed, the body is a
   literal: `Cards/Prototype/ArmKeywordTips.cs` (57 `With(...)` sites),
   `PlayerTips.cs:30-108`, `BaseKeywordTips.cs:226`, `ReactionTips.cs:61`,
   `Vfx/ReactionChart.cs:84,136`. Fix: a `.description` row per tip with
   vars read from the law constants.
2. **English tokens inside keyed faces (126 faces).** `VarkaSwitch` (58,
   `VarkaOath.cs:1184-1200`), `VarkaSwirl` (17), `VarkaWildfire` (14),
   `StageRepay` and `StageDrainLine` (13 each), `StageBow` (12), `YaeTenko`
   (7), `SwirlAura` (5), `HalfHp` (4) and three Spend tokens. Fix: each token
   a key plus vars.
3. **Two display rules that read English text.**
   `Cards/OverriddenElementFace.cs:33-70` replaces "[gold]Hydro[/gold]
   damage" on the finished face (a translated face would keep the old
   element; fix: an element token, as `SwirlAuraFace` does).
   `PlayerTips.cs:131-168` tests a guest's English row for "Act:" (fix: a
   generated flag, as `ISetsOffFirstCard` did for the gameplay rule).
4. **Live captions:** Furina's HP and Fanfare displays (about 14,
   `DrainedCounter.cs:105-175`, `FanfareCounter.cs:108`,
   `FurinaStageCues.cs:163-170`, `FurinaStageBowPreview.cs:263-266`,
   `FurinaStageLaw.cs:274`); Kokomi's plan strip and bubbles (about 25,
   `KokomiPlan.cs:3871-4210`, `KokomiPlanStrip.cs:115-121,786-800`,
   `KokomiPlanView.cs:352,704`, `KurageBeat.cs:120`, `ScryTake.cs:105`); Yae's
   annotations and shrine display (about 35, `YaeAnnotations.cs:47-635`,
   `YaeSakuraDisplay.cs:80-94`); Varka's Swirl payout and Oath lines (about
   12, `VarkaOath.cs:784-800,1019-1026,1321-1328`); the card-hover reaction
   riders (about 12, `Cards/KleeCardTooltips.cs:80-773`).
5. **Spiral Abyss (about 52):** `Abyss/AbyssEntries.cs:218-300`,
   `AbyssRelics.cs:84-95`, `AbyssShadowPowers.cs:45-56`,
   `AbyssOverlayModel.cs`, `AbyssDisplay.cs:122`.
6. **The rest:** the story offer line (`Story/StoryTypes.cs:225-234` builds
   "Choose 1 of N random upgraded Rare Attacks" with a trailing "s"), the
   reaction guide and chart (about 25, `Elements/ReactionGuide.cs:36-139`;
   its names are already keyed in the `*_PREVIEW` rows), and four leftovers
   (`MeterCostBadge.cs:138`, `NationEmblem.cs:65`,
   `FurinaStageCueNodes.cs:269`, `TurnEndPreviewBridge.cs:435`).

## Also found

- English plurals built in code: `KokomiPlan.cs:3879,3914`,
  `StoryTypes.cs:232-234`; joined clauses with English word order in the
  Furina counters, `VarkaOath.cs:1019-1026` and the Abyss overlay. These need
  whole-sentence keys, not fragments.
- 71 keyed rows use `plural:|s` (21 cards, 50 powers). They are fine
  through the English fallback; a Russian or Polish row needs its own plural
  forms, and the translation lint checks placeholders only.
- Number formatting is clean (`InvariantCulture` everywhere).
- The gameplay rule that read English text is now a flag
  (`KleeCardTooltips.cs:523`, `ISetsOffFirstCard`), as ruled.
