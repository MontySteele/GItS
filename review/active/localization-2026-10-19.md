# Translating the mod: what it would take

[USER], 2026-10-19: "what's the plausibility of allowing for foreign language
support in the mod? Given that you're already writing the text, I assume it's
not a huge lift ... I just don't know how that goes in the mod side."

## The mechanics are there

- **The game ships 16 languages** (`LocManager.cs`, decompiled lines 79-97):
  English, Simplified and Traditional Chinese, German, two Spanish, French,
  Indonesian, Italian, Japanese, Korean, Polish, Brazilian Portuguese,
  Russian, Thai, Turkish. It picks the Steam language and falls back to
  English **per line**, so a half-translated mod still runs.
- **Fonts are handled:** the game swaps in Chinese, Japanese, Korean, Thai
  and Cyrillic fonts itself (`FontManager.cs` 11-19).
- **A mod ships translations as files** in its pck,
  `klee/localization/<language>/<table>.json`, merged over the game's tables
  (`ModManager.GetModdedLocTables`; BaseLib adds the English fallback). The
  mod already ships one such file: `klee-mod/pck-src/klee/localization/eng/card_keywords.json`.

## The lift is moving the text, then the volume

- **Almost all of our text lives in code today,** in the `Localization =>`
  lists BaseLib writes into the English table once at start-up. Those lists
  have no language, and whether they even survive a language switch is
  untested. Step one is to make codegen and the hand-written lists emit
  English JSON files instead; nothing changes for an English player.
- **Volume:** about 3,050 strings, 238,000 characters (`tools/player_text_census.py`).
  About 60% is event and story prose. The text you meet every fight (cards,
  powers, relics, keywords, companions) is about 800 strings, 65,000
  characters.
- **Card text has placeholders** (`{Damage:diff()}`, plurals, `IfUpgraded`).
  A broken one prints raw braces in game, so each language needs a lint that
  checks every placeholder survived, and Russian and Polish need more plural
  forms than English.
- **Names must match Genshin's official translation** in each language
  (characters, constellations, places). That glossary has to exist first.
- **Text keeps changing.** Prototype kits change wording weekly; a translation
  would go stale. Each row needs the hash of the English it translated, so a
  changed line is flagged.
- **Longer languages may overflow card faces;** the 120-character ceiling is
  an English number.

## Picks

1. **Whether to start.** (a, default) Do step one now, English moved to
   files, no translation yet: it is invisible to players, it settles the
   language-switch question, and every later language becomes data. (b) Not
   now.
2. **Scope of the first language, when it comes.** (a, default) Gameplay text
   only (the 800 strings), for kits at Balance plus the shared text, with
   story prose left English. (b) Everything.
3. **Which first.** (a, default) Simplified Chinese: the largest Genshin and
   Slay the Spire audience after English. (b) Name one.

**Ruled 2026-10-19,** [USER]: "agreed on (a) all around for the characters at
Balance. Once we've finalized the other two and we've finished working on
event text, we can do a deeper pass on the rest of the text." So: step one
now; the first language is Simplified Chinese, gameplay text of the Balance
kits (Klee, Varka, Furina) and the shared text; Kokomi and Yae join at their
Balance; story and event prose waits for the event-text work to finish.

**Pick 1 reopened and ruled (b), 2026-10-19.** Moving the English into files
turned out to be four large PRs: 119 lines are built from balance numbers in
code, one gameplay rule reads English card text, and about 60 tools and 148
test files read the text from code. [USER] asked whether (b) would need (a)
later; it does not, since a translation is a file either way. [USER]: "agreed
on (b)". So English stays in code and is sent to the game's English fallback
table (re-applied on a language switch), a generated English reference file
carries every key for translators, each translated line carries the hash of
its English, and the placeholder lint ships. The rule that reads English card
text becomes a flag.

Live check, 2026-10-19 (lane 1 booted in Simplified Chinese): the game's own
text is Chinese and ours shows in English, but plurals break: Countdown reads
"Draw 2 card." because the English is formatted with Chinese plural rules.
(b) fixes that, since fallback lines are formatted as English.

**The writing review and the first translation, ruled 2026-10-23.**
[USER]: "Agreed on all of it!" (1) English first, kit by kit, then
translation on the settled English. (2) Each kit gets the Kokomi audit
format (`kokomi-text-audit-2026-10-22.md`): Klee, Varka, Furina, Yae and the
shared text, then the story and event prose as its own pass. (3) Claude
translates Simplified Chinese with a glossary of Genshin's official Chinese
names and Slay the Spire 2's own Chinese card wording; a reader who knows
Chinese checks a sample before release. (4) Yae's English pass is now; her
translation waits for her Balance. First audit: `klee-text-audit-2026-10-23.md`.
