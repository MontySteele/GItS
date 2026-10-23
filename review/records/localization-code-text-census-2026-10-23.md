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

## Step 1, closed 2026-10-23

The mechanism is `CodeText` (`klee-mod/KleeCode/Localization/CodeText.cs`,
written up in `docs/current/operations/localization.md`, "Code-built text"):
a row is authored in C#, merged into the English table, and read through the
game's `LocString`, numbers as vars. 91 rows, all in `card_keywords`; the
English a player reads is unchanged, pinned by
`klee-mod/KleeTests/CodeTextTests.cs` against the English dumped off the old
assembly (`KleeTests/Fixtures/code_text_before_2026_10_23.json`).

- **Group 1, tip bodies: closed but for Yae's Annotations.** 38 rows in
  `PlayerTips.cs` (every arm tip a player reads, its variants, Yae's six),
  24 in `FurinaStageBadges.cs` (each guest's line and act, the join).
  Not keyed, on purpose: the seat's long forms in `ArmKeywordTips.cs`, the
  eight riders only a seat's chain raises, and every `BaseKeywordTips` body
  (a player reads the base game's own tip for those words). The Annotation
  tips (`YaeAnnotationText`) are step 2's, with the rest of
  `YaeAnnotations.cs`.
- **Group 3: closed.** A card face's hit element is a token
  (`[gold]{Hydro}[/gold] damage`, 212 of our card rows), filled with the
  element's own row (`KLEEMOD-ELEMENT_NAME.*`, 6 rows); a guest's tip half is
  a generated marker (`IPrintsGuestAct`, `IPrintsGuestLine`, 10 cards).
- **Group 6, the reaction guide and chart: closed.** 23 rows (a tip per
  element, a cell per reaction, the notes, the chart's labels and its button).
- **Found on the way:** three texts no lint had measured are now read, and
  over their rules: the full-shrine tip (161 of 135, and of the hover's 100),
  Neuvillette's guest sentence (136 of 135) and Escoffier's ("N more
  damage"). Carried as named exceptions; a rewording is each kit's text
  audit's. The Drained counter shows the seat's Drain sentence to a player
  (`DrainedCounter.cs:148`), left for group 4.

Left: groups 2, 4 and 5, the four leftovers of group 6, the story offer line,
and the Abyss strip title's key.

## Step 2, closed 2026-10-23

Varka and Furina, and the card-hover reaction riders. 88 rows, all in
`card_keywords`; the English a player reads is unchanged, pinned by
`CodeTextTests.Every_step_2_line_renders_the_same_from_its_rows` against 277
renderings dumped off main 2b5f235b1 (the `s2:` entries in the fixture), over
inputs that reach every branch (`klee-mod/KleeTests/CodeTextStep2Cases.cs`).

- **Group 2, Varka's and Furina's face tokens: closed.** `VarkaSwitch`,
  `VarkaSwirl` (with what a Swirl pays) and `VarkaWildfire`
  (`VarkaOath.cs`, 16 rows with the Oath gains); `StageBow`,
  `StageDrainLine`, `StageRepay`, `StageSpendShort`, `StageSpendHits` and
  `StageLost` (`FurinaStageBowPreview.cs`, 19 rows), a guest's name its own
  row (`PerformerWords.cs`, 11); `SwirlAura` and `HalfHp`, one row each. A
  line's leading line break or space is the row's, so a translation places
  it. The generated faces are unchanged: the token stays, and the C# that
  fills it reads a row.
- **Group 4, Varka's and Furina's captions: closed.** The Drained counter's
  hover (`DrainedCounter.cs`, 11 rows, the box a join row), the Fanfare
  gauge's (`FanfareCounter.cs`, 1), the stage cue's forecast
  (`FurinaStageCues.cs`, 4), and the Oath gains said over Varka's head
  (`GainClause`, `GainLine`: a row per source, and join rows for the list,
  the card and the relic).
- **The reaction riders: closed.** `KleeCardTooltips.cs`, 24 rows: the
  overridden element, the three amplified bodies and The Boot's clause (a
  join row), the Artifact sentences (each debuff a word row), "Only if you
  Spend:", the no-hit bodies (multipliers from `ReactionConstants`), the
  Swirl preview and Varka's clauses on it.
- **Not keyed, on purpose.** `FurinaStageLaw.LineWhy` and
  `FurinaStageFacePreview.LineNow` (`FurinaStageLaw.cs:274`,
  `FurinaStageBowPreview.cs:263-266` above): no player surface prints them
  since 2026-10-11, and the line's why goes only to the seat page.
  `VarkaOath.PayoutSentence` (`VarkaOath.cs:1321-1328`) is the Oath badge's
  model row, already in the English table. `SourceWord`, `PayoutWords` and
  `TwinGalesPaid` are the seat page's.
- **The Drained counter still shows the seat's Drain sentence**
  (`DrainedCounter.cs:148`, above): keyed as it reads
  (`KLEEMOD-ARM_STAGE_DRAINED.description_rule`), not swapped for the
  player's shorter Drain row, which would change what a player reads. The
  swap is the Furina text audit's.

Left: Yae's Tenko token, Kokomi's and Yae's captions, and groups 5 and 6
(step 3).

## Step 3, closed 2026-10-23

Kokomi, Yae, the Spiral Abyss and the leftovers, on step 1's mechanism.
The English a player reads is unchanged, pinned by
`klee-mod/KleeTests/CodeTextStep3Tests.cs` against the English the same calls
printed off the old assembly (main 2b5f235b1,
`KleeTests/Fixtures/code_text_before_step3_2026_10_23.json`, about 1,180
cases), plus the nine inline sentences copied from their literals.

- **Kokomi (38 rows, `Vfx/Prototype/KokomiPlanText.cs`).** The strip's
  captions and marks, the pager, the Plans view's captions, hint, prompts
  and flip refusals (`KokomiPlan.FlipRefusalShown`; the bridge keeps its
  lower-case reasons), Scry's auto-take bubble. "N attackers" and "N hits"
  are SmartFormat plurals. Not keyed, on purpose: `KurageBeat.Line` ("Bake-
  Kurage: Ambush, 12"), which only the blind page prints since the caption
  over the pet replaced the bubble (2026-10-21).
- **Yae (40 rows).** The Annotations' names (their tip titles), rules,
  Sakura readings and Red Ink's planting box (`YaeAnnotationText.Rows`), so
  `lint_hover_tips` measures `ForAnnotation` as keyed and its `UNKEYED_OK`
  entry is gone; the Masterpiece's two bodies (hover summary and face line,
  lists SmartFormat's); the Tenko token's clause and amounts
  (`YaeShrineFace.Rows`); the shrine row's previews, rules and mark letters
  (`YaeSakuraSlots.Rows`). The Edit prompts, Reborn faces and keyword
  fallback, which are English rows themselves, read the English.
- **Spiral Abyss (73 rows, `events`).** Every Blessing and Shadow name and
  text, whole sentences with the act's numbers and the element's name as
  vars (`AbyssText.Rows`), and the Blessing screen, strip hover, result line
  and the Shadows relic's list (`AbyssOverlayText.Rows`). The strip title's
  key is built from the enum (`AbyssText.NameKey`): seven keys moved
  (`BLOODINTHEWATER` became `RIPTIDE`, and `THELEYLINE`, `JADESHIELD`,
  `THECLOCK`, `ABYSSMAGESHIELD`, `ABYSSHERALD` took their enum names); no
  translation existed. The event page's 504 option rows stay composed
  English rows (now through `AbyssOverlayText.Option`).
- **Leftovers (6 rows).** The whole-bank X (`MeterCostBadge`), the four
  nation initials (`NationEmblem`), the cue's ALL (`FurinaStageCueNodes`).
  `TurnEndPreviewBridge.cs:435` has nothing to key: its source table
  (`TurnEndAttribution.Order`) is empty since 2026-10-11.
- **The story offer line is not player text.** `StoryOffer.Text` is read
  only by `StoryRewardsTests` as the oracle for the authored option rows,
  which are keyed; nothing shows it, so it stays as it is.
- **The Teyvat frame's rows are marked.** `LocReferenceTests` writes
  `klee-mod/localization/reference/teyvat_frame_rows.json` (1,804 rows a
  frame-off build does not merge), and `tools/lint_loc_translations.py`
  fails a translated row among them and counts 3,403 rows to translate.

Left: nothing. With step 2, every group of the census is keyed or named
above as seat text or not player text.
