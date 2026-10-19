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
