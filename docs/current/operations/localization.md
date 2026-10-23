## Localization: our English and translations

**Our English goes to the English table, always** (route b, 2026-10-19).
Every row the mod authors (model `Localization` rows, the hand-written merges
in `KleeMod.InjectLocStrings`, `TeyvatLoc`, `StoryLoc`, `AbyssLoc`, the
run-stats label) is written into the game's English table, which the game
keeps as the per-key fallback of every other language's table. A player in
another language reads our English through that fallback, formatted with
English culture. The rows are re-applied each time the game builds a table set,
so an in-game language switch keeps them. The plumbing is
`klee-mod/KleeCode/Localization/EnglishLoc.cs`; a new merge goes through
`EnglishLoc.Table(name)`, never `LocManager.Instance.GetTable(name)`.

Rows copied from base-game text (a dressed Ancient's alias, a story Ancient's
"next" button) use `EnglishLoc.MergeDerived`, which copies each language from
its own table.

**A translation** is the game's flat table file in the pck,
`klee-mod/pck-src/klee/localization/<lang>/<table>.json`, key to string, with
the same keys as English. It wins per key; a missing key falls back to
English. Translate against the English reference,
`klee-mod/localization/reference/eng.json` (`{table: {key: English}}`).

```sh
# rewrite the English reference after an English change (the C# suite fails while it is stale)
cd klee-mod/KleeTests && GITS_WRITE_LOC_REFERENCE=1 dotnet test --filter LocReferenceTests
# after a translation pass: record the English each row was translated from
.venv/Scripts/python.exe tools/lint_loc_translations.py --stamp zhs
# the lint (ci lane): placeholders match English, no stale or unstamped row
.venv/Scripts/python.exe tools/lint_loc_translations.py
```

The hashes live outside the pck, `klee-mod/localization/hashes/<lang>/<table>.json`
(key to the first 16 hex digits of sha256 of the English), so the shipped file
stays flat.

**The Teyvat frame's rows are not translated while the frame is off.** The
reference's build turns the frame arm on, so it lists the nation events,
nation Ancients and acts too; the same test writes
`klee-mod/localization/reference/teyvat_frame_rows.json` (`{table: [key]}`,
the rows a frame-off build does not merge), and the lint fails a translated
row among them and counts the rows left to translate without them.

### Code-built text

English that C# builds (a tip body, a chart label, a guest's sentence) is a
`CodeRow`: table, key, English template, authored beside the code that shows
it and listed in `CodeText.Sources()`
(`klee-mod/KleeCode/Localization/CodeText.cs`). `CodeText.Inject` merges every
row into the English table through `EnglishLoc.Table`, so the English
reference picks it up, and a surface reads its row with
`CodeText.Format(row, vars)`, a `LocString` through the game's SmartFormat: a
translated row in the local table wins per key, and the vars fill its holes.
Headless (the C# suite) a row formats from its English through the same
SmartFormat extensions, so a test reads the text a player would.

- **Keys.** The surface's own key with a leaf for the box, in the table its
  title already lives in: `card_keywords`, `KLEEMOD-ARM_MEND.description`; a
  variant `KLEEMOD-ARM_SPARK.description_opening_bank`; a chart's parts
  `KLEEMOD-REACTION_CHART.cells.VAPORIZE`. An element's name is
  `KLEEMOD-ELEMENT_NAME.PYRO`. The Spiral Abyss's rows live in `events` beside
  its page (`KLEE_SPIRAL_ABYSS.blessings.LEYLINE.description`), a name keyed
  by its enum, never its display name (`KLEE_SPIRAL_ABYSS.strip.RIPTIDE.title`).
- **A row that is itself English reads the English.** Where code composes a
  row another merge writes into the English table (an event option, a
  badge's description, an Edit prompt), it reads `CodeText.English` (or the
  surface's `NameEnglish` / `RuleEnglish`), so the English table never holds a
  translated fragment.
- **A list is SmartFormat's** (`{Items:list:{}|, }`), so a translation sets
  its own separator.
- **Adding a row.** Add the template to the surface's rows (a tip body to
  `PlayerTips.Bodies`, or a `CodeRow` the surface lists), read it with
  `CodeText.Format`, rewrite the English reference, and pin the rendered
  English in a test.
- **The rule.** A row is a whole sentence or a whole box; code never glues
  English fragments, and where two sentences join, the join is its own row
  (`{Line} {Act}`). A number is a var read from the law constant
  (`{BombGrowth}`, `CodeText.Num` for a decimal), never baked in; a plural is
  SmartFormat's (`card{N:plural:|s}`). A word code fills in that is itself
  player text (an element) is a var whose value is its own row. SmartFormat
  reads a backslash as an escape, so a literal one is written twice.
- **Seat text is not keyed.** A sentence only a blind seat reads (the long
  forms in `ArmKeywordTips`, the riders only a seat's chain raises) stays an
  English literal. `tools/lint_hover_tips.py` fails a player chain that raises
  a tip with no keyed row.
- **A display rule never reads English.** A card face's hit element is a
  token (`[gold]{Hydro}[/gold] damage`), written into our card rows as they
  reach the English table (`EnglishLoc.ModelRowText`); a guest's tip half is a
  marker the generator stamps (`IPrintsGuestAct`, `IPrintsGuestLine`).
