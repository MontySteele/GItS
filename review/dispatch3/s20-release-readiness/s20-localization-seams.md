# S20 — localization seams (inventory)

> **This decides nothing.** It is a census of where player-visible text lives
> today, what reaches a translation table and what cannot, and which of the
> gaps are defects versus scope calls that are [USER]'s. Nothing here proposes
> that the mod support any language, and no ship, language, or accessibility
> promise is made or implied. Read date for every live artefact below:
> **2026-08-26**.
>
> Scope: the localization family only. Save/update/removal, player count,
> packaging/metadata, performance, controller/resolution/text and
> colour/reduced-motion are the other six S20 families — one-line pointers
> only where they touch text.

---

## 1. How the base game's localization works (mechanism, decompiled)

Sources are the local ILSpy decompile of the shipped game (paths below are the
scratch decompile tree; cite as `<Type>::<member>` + file:line).

| Fact | Evidence |
|---|---|
| 14 shipped languages: `eng zhs deu esp fra ita jpn kor pol ptb rus spa tha tur` | `LocManager` static ctor, `MegaCrit.Sts2.Core.Localization/LocManager.cs:614-648` |
| Base tables live at `res://localization/<lang>/<table>.json`; every `.json` in that dir becomes a table named after the file | `LocManager::LoadTablesFromPath`, `LocManager.cs:105,415,438-441,507-517` |
| **Fallback language is English, per key, per table.** Loading any non-`eng` language first loads the whole `eng` set and hands each table the English table as `_fallback` | `LocManager.cs:409-411`, `:448-449`; `LocTable::GetRawText` walks `_fallback`, `LocTable.cs:44-55` |
| A missing language directory falls back to `eng` wholesale, with a warning | `LocManager.cs:418-423` |
| A **missing key** in table + fallback **throws** `LocException`, it does not render blank | `LocTable.cs:38`, `:54` |
| A mod adds rows at `res://<manifest.id>/localization/<lang>/<file>`, merged into the base table **of the same filename** | `ModManager::GetModdedLocTables`, `MegaCrit.Sts2.Core.Modding/ModManager.cs:114`, `:989`; merge at `LocManager.cs:465-474` |
| **A mod cannot invent a new table.** The merge loop iterates the *base* game's files and only then asks mods for that filename | `LocManager.cs:438-441` vs `:465` |
| Player-side override dir for translators: `%AppData%/SlayTheSpire2/localization_override/<lang>/<table>.json`, plus a Weblate-nested layout `…/slaythespire2/<table>/<weblate-code>/<table>.json`; entries are SmartFormat-validated and bad ones skipped | `LocManager.cs:87-96`, `:424-436`, `:526-559`, `:572-592`. The dir exists and is **empty** on this machine (read 2026-08-26) |
| Values are SmartFormat templates (single braces) and BBCode (square brackets) | `LocManager::LoadLocFormatters`, `LocManager.cs:226-233`; house rules mirrored at `klee-mod/KleeCode/KleeMod.cs:88-101` |
| Formatting culture: a key present in the *current* table formats under that language's `CultureInfo`; a key served by the English fallback formats under English culture | `LocManager::SmartFormat`, `LocManager.cs:255-259`; `LocTable::IsLocalKey`, `LocTable.cs:71-74` |
| Language can be changed **at runtime** from the settings dropdown; it calls `SetLanguage` + `NGame.Relocalize()`, which rebuilds every table from disk | `NLanguageDropdown::OnDropdownItemSelected`, `MegaCrit.Sts2.Core.Nodes.Screens.Settings/NLanguageDropdown.cs:127-139`; `LocManager.cs:332-341` |
| The English-override path used for metrics upload is **not reached in a modded run** (metrics are skipped when modded) | `MetricUtilities.cs:97-115` |
| `res://localization/eng` cannot be enumerated off disk: `SlayTheSpire2.pck` is `GDPC` format 3 with an **encrypted directory** | repo-recorded verification, `tools/gen_energy_orb_layers.py:47-53` |

BaseLib adds one more injection point: custom models implementing
`ILocalizationProvider` get their rows written **straight into the live
`LocTable._translations` dictionary** by a Harmony postfix on `ModelDb.Init`,
category-mapped to a table name (`CardModel`→`cards`, `PowerModel`→`powers`,
`CharacterModel`→`characters`, `RelicModel`→`relics`, `DynamicVar`→
`static_hover_tips`, …) — `BaseLib/Patches/Localization/ModelLocPatch.cs:14-99`,
interface at `BaseLib/Abstracts/ILocalizationProvider.cs:5-10`.
`ModelDb.Init()` runs exactly once, at startup, immediately after
`LocManager.Initialize()` — `MegaCrit.Sts2.Core.Helpers/OneTimeInitialization.cs:79-81`.

---

## 2. Where our strings live today

| Storage | What it holds | Rows | Reaches a translation table? | Evidence |
|---|---|---|---|---|
| **C# `Localization` overrides on models** (cards, powers, relics, characters) | Every card title/description, power tooltip, relic text, character text | 319 files declare `Localization =>`; 368 `("title", …)` and 294 `("description", …)` pairs across `klee-mod/KleeCode` | Rows are injected into the *active* table at boot; they are not a file, so no `<lang>` variant of them can exist | e.g. `klee-mod/KleeCode/Cards/Generated/BombsAway.cs:44-48`; mechanism `ModelLocPatch.cs:76-98`; house rule `docs/current/LAW.md:410-413` |
| **PCK loc files**, generated *inside the build script* | `klee/localization/eng/card_keywords.json` (28 rows), `klee/localization/eng/ancients.json` (9 rows, Architect finale dialogue, marked PLACEHOLDER copy) | 37 | Yes — these are the only rows on the base game's own localization path | `tools/build_pck.ps1:583`, `:585-620`, `:632-643`; live build output `klee-mod/dist/pck-work/klee/localization/eng/*.json` |
| **DLL runtime dictionary** `KleeMod.InjectLocStrings` | 5 rows into `cards` (Jumpy Dumpty title/description + three selection-screen prompts) and 48 into `card_keywords`, of which the 28 already in the PCK are skipped (`!HasEntry`) — so ~20 are DLL-only (rider-tip titles, Salon member titles, turn-end docket titles, Kokomi tips, `CONFISCATED`, `FROZEN_BOSS_PREVIEW`) | 53 | No file backs them; they exist only in the running process | `klee-mod/KleeCode/KleeMod.cs:77-276`, merge guard `:265-267`, patch `:293-299` |
| **Free text built in C# at display time** (hover-tip *bodies*) | Fanfare / aura / Salon / companion rider bodies, Salon member bodies, turn-end docket bodies, Kokomi pulse/Garment/Charge/Muster bodies, Salon and docket VFX bridges | 13 `new HoverTip(...)` sites across 5 files | **No.** `HoverTip(LocString title, string description)` takes raw text for the body; only the title is a key | `klee-mod/KleeCode/Cards/FurinaRiderTips.cs:23-29`, `:61-66`; also `KokomiRiderTips.cs`, `SalonMemberTips.cs`, `Vfx/SalonVisualsBridge.cs:147`, `Vfx/TurnEndPreviewBridge.cs:106` |
| **Scene-baked text** | `text = "END OF TURN"` on the docket header label; `"5+"` on the Salon stage overflow pip | 2 | No | `klee-mod/pck-src/shared/turn_end_docket.tscn:141`; `klee-mod/pck-src/furina/ui/salon_stage.tscn:701` |
| **Mod manifest** | `name`, `description`, `author` shown in the mod list | 3 | No — `ModManifest` has no localization field | `klee-mod/Klee/manifest.json:3-5`; `MegaCrit.Sts2.Core.Modding/ModManifest.cs:16-46` |

Not player-facing, listed so the census is closed: the sim-side YAML sheets
(`docs/*-cards.yaml`) and every `Log.Info` string are repo-internal and never
rendered to a player (`tools/lint_prose_constants.py:29-32` makes the same
carve-out for `Diagnostics/`).

---

## 3. Key scheme

* Model rows: `<Id.Entry>.<title|description>` where `Id.Entry` is
  `UPPER_SNAKE_CASE` **with BaseLib's mod prefix** — `Kaboom` → `KLEEMOD-KABOOM`
  (`KleeMod.cs:96-103`; enforced at boot by self-check rule R4, which reads
  `Id.Entry` off the live model rather than trusting the class name,
  `klee-mod/KleeCode/Diagnostics/KleeSelfCheck.cs:500-507`).
* Card selection screens: `<Entry>.selectionScreenPrompt` in the `cards` table —
  base-game shape (`CardModel.cs:126-132` in the decompile); ours are keyed on
  the *verb*, e.g. `KLEEMOD-SLY_GRANT.selectionScreenPrompt`
  (`klee-mod/KleeCode/Powers/SlyGrant.cs:66`, `:83-88`).
* Custom keywords / hover-tip titles: `KLEEMOD-<NAME>.title` /`.description`
  in `card_keywords`, prefix allocated by BaseLib's enum generator
  (`tools/build_pck.ps1:578-582`).
* Ancient dialogue: `THE_ARCHITECT.talk.<CHAR_ENTRY>.<X>-<Y>[r].<ancient|char|next>`
  — the trailing `r` (repeating) is load-bearing (`tools/build_pck.ps1:645-659`,
  guard at `KleeSelfCheck.cs:356-393`).

Downfall uses the **same** scheme (`AUTOMATON-ALLOCATE.title`) —
`Downfall@32e6113:Automaton/localization/eng/cards.json:2-3`.

---

## 4. Which tables we reach

Observed live at boot on the deployed build (pck build id `20260826-204650+98fb3a0`),
`%AppData%/SlayTheSpire2/logs/godot.log:198-209`:

```
Loading locale path=res://localization/eng
Found loc table from mod: eng ancients.json …
Found loc table from mod: eng card_keywords.json …   (x2 — ours and BaseLib's)
Found loc table from mod: eng card_selection.json / credits.json / gameplay_ui.json /
  main_menu_ui.json / powers.json / settings_ui.json / static_hover_tips.json  (BaseLib's)
```

* **Ours, by file:** `ancients`, `card_keywords`.
* **Ours, by runtime injection:** `cards`, `card_keywords` (DLL);
  `cards`, `powers`, `characters`, `relics` (BaseLib model injection —
  category map at `ModelLocPatch.cs:14-72`; relics confirmed present in our
  tree: 4 files under `klee-mod/KleeCode/Relics` declare `Localization`).
* `monsters`, `events`, `encounters`, `potions`, `enchantments` are **not**
  reached — we ship no such custom models today (`grep -rl EnchantmentModel
  klee-mod/KleeCode` → no matches).
* Boot health today: `SELFCHECK passed (19 rule families across 3 characters
  and the assembly's powers)` — `godot.log:223`.

---

## 5. Case table

Status values: WORKS / DEFECT / UNKNOWN / NOT-SUPPORTED-BY-DESIGN. "Defect or
scope call" is kept deliberately separate from status.

| # | Case | Reproduction | Status | Evidence | Automation candidate | Defect or scope call |
|---|---|---|---|---|---|---|
| L1 | Our PCK loc files merge into the base tables under `eng` | Boot the game with the mod; read `godot.log` for `Found loc table from mod: eng …` | **WORKS** | `godot.log:198-200`; mechanism `ModManager.cs:114` | **yes** — a log-scrape assert in the existing boot-telemetry family (`KleeSceneTelemetry` is the precedent, `KleeMod.cs:44-49`) | — |
| L2 | Card / character / power loc keys exist at boot in the active language | Boot; self-check runs at `ModelDb.Init` postfix | **WORKS** (today, `eng`) | `KleeSelfCheck.cs:490-524`, `:578-600`; `godot.log:223` | already automated (R4/R5/R8) | — |
| L3 | Custom-keyword / hover-tip **title** rows are not covered by any check | Ship a new keyword with no row → the UI renders the literal key. Has happened twice in live builds: `card_keywords.KLEEMOD-COMPANION_RIDER.title` (0.2-589) and `card_keywords.KLEEMOD-MUSTER.title` (0.2-634) | **DEFECT (class; no instance found tonight)** | `KleeMod.cs:206-215`, `:253-260`; self-check walks only `cards`/`characters`/`powers` (`KleeSelfCheck.cs:500-524`) | **yes** — extend `CheckLocEntry` over every `KLEEMOD-` key referenced by a `new LocString("card_keywords", …)` site; the keys are already `const` fields | **Defect** (missing coverage for a repeat failure mode) |
| L4 | Switching language in-game loses every runtime-injected row | Settings → language → pick any non-English entry. **Not reproducible tonight — needs the game, and [USER] is playtesting.** Predicted: custom card/power/relic/character text throws `LocException`; ~20 DLL-only keyword titles render as raw keys; the 37 PCK rows survive via the English fallback | **DEFECT (predicted, UNVERIFIED at runtime)** | `SetLanguage` rebuilds `_tables` (`LocManager.cs:332-341`); injections run once — `LocManager.Initialize` postfix (`KleeMod.cs:293-299`) and `ModelDb.Init` postfix (`ModelLocPatch.cs:76`, `OneTimeInitialization.cs:79-81`); neither mod subscribes to locale change (`grep SubscribeToLocaleChange` → 0 hits in `klee-mod/KleeCode` and in the BaseLib decompile); missing key throws (`LocTable.cs:38,54`) | **yes** — a headless test could assert "every model row survives a simulated `SetLanguage`", but the cheap version is a manual capture: switch language, screenshot a card | **Defect** if any non-English language is ever in scope; harmless if English-only is ruled. The *rule* is [USER]'s (see §7-Q1); the *crash-on-switch* is a defect either way, because the dropdown is reachable by any player who installs the mod |
| L5 | Hover-tip **bodies** cannot be translated at all | Inspect any rider tip: the body is a C# string passed to `HoverTip(LocString, string)` | **NOT-SUPPORTED-BY-DESIGN** (ours, and the base type's) | `FurinaRiderTips.cs:23-29`, `:61-66` | no (nothing to gate until a mechanism exists) | **Scope call** — the bodies interpolate live constants on purpose (`KleeMod.cs:132-141`), so making them table rows trades that guarantee away |
| L6 | 302+ card/power/relic strings live in C#, not in a JSON table | `grep -rl "Localization =>" klee-mod/KleeCode` → 319 files | **NOT-SUPPORTED-BY-DESIGN**, and it is current LAW | `docs/current/LAW.md:410-413`; contrast Downfall §6 | no | **Scope call** — LAW says "declare loc via the `ILocalizationProvider.Localization` override, never a hand-rolled dict"; a translatable build needs per-language JSON, which is the opposite storage. Not a contradiction to resolve tonight |
| L7 | PCK keyword rows hand-type balance numbers and **win** over the interpolated DLL copy | Read both copies of any reaction row | **WORKS today — no drift** (checked 2026-08-26: `PerSkillTag=5`, `AuraDurationTurns=2`, `OverloadSplash=6`, `OverloadWeak=1`, `SuperconductVuln=2`, `ElectroChargedDot=4`, `ShatterDamage=6`, `CrystallizeBlock=4` all match the JSON) | JSON `tools/build_pck.ps1:585-620`; consts `klee-mod/KleeCode/Elements/ReactionTable.cs:30-51`, `Powers/BurstResource.cs:22`; precedence `KleeMod.cs:265-267` | **yes** — `tools/lint_prose_constants.py` already does exactly this check but its scope is `klee-mod/KleeCode/**/*.cs` only (`:29-32`), so the `.ps1` heredoc is ungated. Widening the scope to the generated loc JSON is a one-source-set change | **Defect** (gate gap, latent) |
| L8 | Scene-baked `"END OF TURN"` header has no loc key | Read the scene; the label is never reassigned (only per-slot labels are, `Vfx/TurnEndPreviewBridge.cs:307`, `:319`) | **DEFECT (untranslatable string), cosmetic today** | `klee-mod/pck-src/shared/turn_end_docket.tscn:141` | **yes** — a lint over `pck-src/**/*.tscn` for non-empty `text = "…"` with letters | **Defect** if translation is in scope; otherwise an inventory row |
| L9 | Architect finale dialogue is PLACEHOLDER English | Read the generated `ancients.json` | **WORKS mechanically / copy is placeholder** | `tools/build_pck.ps1:641-643` ("PLACEHOLDER dialogue text — naming/writing pass, user red-pen"); softlock guard `KleeSelfCheck.cs:356-393` | already automated (R12 presence + repeating-row check) | **Scope call** — writing the real copy is [USER]'s |
| L10 | Mod name/description in the mod list are English-only | Read the manifest and the manifest type | **NOT-SUPPORTED-BY-DESIGN** (base game has no loc field for it) | `klee-mod/Klee/manifest.json:3-5`; `ModManifest.cs:16-46` | no | Neither — an upstream constraint |
| L11 | Player-side translator overrides would also cover our rows | Drop `%AppData%/SlayTheSpire2/localization_override/deu/cards.json` with our keys | **UNKNOWN — not reproducible tonight.** Mechanically the override merges into the *base* table before mod injection order matters, but our model rows are written after load, so the override may be overwritten for our keys | `LocManager.cs:450-474` (overrides merge inside the load loop) vs `ModelLocPatch.cs:90-97` (writes after `LocManager.Initialize` completes) | yes, once a language is in scope | **Defect-or-not is undecidable until L4/Q1 is settled** |
| L12 | Number/date formatting culture for our strings under a non-English UI | Same as L4 | **UNKNOWN** | injected rows are "local" keys so they format under the *current* culture (`LocManager.cs:255-259`, `LocTable.cs:71-74`); the repo already avoids interpolating floats for exactly this reason (`KleeMod.cs:137-141`: a comma locale would print "1,5x") | no | — |
| L13 | Font coverage for CJK / Thai / Cyrillic in our own scenes | Needs the game with a non-Latin language | **UNKNOWN** — our scenes set only `theme_override_font_sizes` / colours and inherit the base theme (`turn_end_docket.tscn:130-141`); whether the inherited font carries those glyphs was not established | as above | no | — |

---

## 6. Downfall comparison (`lamali292/Downfall@32e6113`, reference-reading only)

| Dimension | Downfall | Us |
|---|---|---|
| Storage | Per-language JSON committed in the source tree, one dir per character mod: `Automaton/localization/{deu,eng,fra,ita,jpn,kor,ptb,rus,spa,zhs,zht}/` (`Downfall@32e6113:Automaton/localization/eng/cards.json:1`) | One generated `eng` dir written by a PowerShell heredoc (`tools/build_pck.ps1:583-643`); everything else is C# |
| Volume | 902 loc JSON files across 11 character dirs; Automaton's `eng` set is 12 tables (`cards` 222 rows, `powers` 81, `relics` 34, `encode` 94, `characters` 14, `potions` 6, `static_hover_tips` 6, `ancients` 4, `events` 2, `card_selection` 2, `enchantments` 2, `combat_messages` 1) | 2 tables, 37 rows on the file path; 53 rows injected from the DLL; 300+ strings in C# |
| Partial translations | Normal and relied upon: `Automaton/localization/deu/cards.json` carries **71** title rows against `eng`'s 222 — descriptions fall through to English per key | n/a |
| C# loc injection | Used **once** in the whole repo, and only where the string is *derived* from another model's title (`Downfall@32e6113:CollectorCode/Cards/Token/Collectible.cs:30-34`) | The default for all 300+ rows |
| Build | `localization/**` is an explicitly packed/symlinked asset folder (`Downfall@32e6113:build/mod.build.props:10`, `:54`); README calls repacking after a localization change a first-class step (`README.md:147`, `:161`) | The loc JSON is *generated text inside the build script*, not an asset directory; there is no `localization/` source folder to edit or diff |
| Curiosity worth one line | Downfall ships a `zht` dir, but `zht` is **not** in `LocManager.Languages` (14 codes, `LocManager.cs:614-648`), though `CultureInfoFromThreeLetterCode` does map it (`:198`). That directory is unreachable at load unless the base list changes | — |

Nothing above is copied; the comparison is structural.

---

## 7. What is [USER]'s (numbered pick lists, no recommendation)

**Q1 — language scope for a public build.** Pick one:
1. English only, and the language dropdown's behaviour with the mod installed is
   documented as unsupported.
2. English only, but the mod must not *break* when a player switches language
   (fixes L4 without shipping any translation).
3. English plus community translations via the base game's own
   `res://klee/localization/<lang>/` path (requires the strings to live in files
   — see Q2).
4. Not decided tonight; L4/L8/L11 stay inventory rows.

**Q2 — storage of card/power/relic strings** (only live if Q1 = 3). PROPOSED
technical options, all of which need a LAW read because `LAW.md:410-413`
currently mandates the C# override:
1. Keep C# as authoring source, **emit** `localization/eng/*.json` from the same
   codegen that writes the cards, and have models read the table.
2. Move authoring to JSON, keep `Localization` overrides only where the string is
   derived at runtime (Downfall's split).
3. Keep as-is and accept L4/L6.

**Q3 — hover-tip bodies (L5).** Pick one:
1. Stay free text and keep the live-constant guarantee.
2. Move to rows with SmartFormat holes for the numbers (translatable, and the
   numbers stay interpolated) — costs a row per body and a new failure mode
   (missing row → raw key).
3. Split: rows for bodies with no live number, free text for the rest.

**Q4 — the four automation candidates** (L3, L7, L8, and the L1 boot assert) are
engineering gates, not design; they are named here only so they can be routed to
BACKLOG by whoever owns the morning triage. This file mints no ids.

---

## 8. NON-FINDINGS and UNKNOWNs

* **NON-FINDING:** no repo doc records any localization stance. `LAW.md`,
  `QUEUE.md`, `BACKLOG.md`, `STATE.md`, `OPERATIONS.md` contain exactly one
  localization line between them (`LAW.md:411`, quoted above) and no
  language/translation policy at all.
* **NON-FINDING:** no translator-facing override files exist on this machine —
  `%AppData%/SlayTheSpire2/localization_override/` is empty (read 2026-08-26).
* **NON-FINDING:** no drift between the PCK's hand-typed numerals and the
  constants they quote, today (L7).
* **UNKNOWN:** the base game's full table-name list. The pack directory is
  encrypted (`tools/gen_energy_orb_layers.py:47-53`); the 10 names in
  `godot.log:198-209` and the 14 in BaseLib's category map are a lower bound,
  not the set.
* **UNKNOWN:** L4, L11, L12, L13 — all four need the game running under a
  non-English language, which tonight's rules forbid.
* **Search boundary:** decompiled game + BaseLib + this repo + the pinned
  Downfall clone. No other public StS2 mod was searched for localization
  patterns; another mod may have solved the runtime-injection/language-switch
  problem and would not appear here.

---

## What this does NOT establish

It does not establish that any non-English language works, partly works, or is
worth supporting; it does not measure anything; it does not test the
language-switch prediction (L4) against the running game; and it does not
resolve the tension between `LAW.md:410-413` and file-based translation — that
is a [USER] call, written above as a pick list, not a recommendation.
