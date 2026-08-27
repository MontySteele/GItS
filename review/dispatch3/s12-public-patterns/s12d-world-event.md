# S12d — World-event runtime in public StS2 sources

**Question.** Tell an actual event model — a player-facing "?" room with pages,
options and outcomes — apart from a project-local `Events` hook namespace.
Which public source, if any, implements the former?

**Decides nothing.** Research only, zero design authority (charter §3.1).
Read 2026-08-26.

---

## Overview

1. The short answer: **yes, one public source implements real "?" room events —
   but it is not Downfall.** It is the BaseLib library Downfall depends on.
2. Downfall's `*Code/Events/` folders are **the false positive the question
   warns about**. All 72 files across 11 submods are combat hook interfaces and
   dispatchers. Not one is a world event.
3. The base game calls that same concept `MegaCrit.Sts2.Core.Hooks`. "Events"
   is purely Downfall's own folder name.
4. Downfall defines **zero** new "?" events. Its entire world-event surface is
   five files: it adds *options* to one existing base-game event
   (`ColorfulPhilosophers`) and supplies their text through localization keyed
   on the **base** event's id.
5. That localization key shape is itself good evidence of the base model:
   `EVENT_ID.pages.PAGE.options.OPTION.title` / `.description`.
6. Downfall also carries one **Ancient** built out of the same parts
   (`EventOption`, pages, `SetEventState`, `EventRoom`) — proof that Ancients
   are event-shaped, but an Ancient is a *different map point type*, not a "?"
   room. That Ancient is also disabled at the pinned commit.
7. **BaseLib** (`Alchyr/BaseLib-StS2`, MIT) ships `CustomEventModel` plus the
   registration machinery that injects custom events into a specific act's
   event list or into the game's shared event pool. Verified by reading the
   code, not the filename.
8. A public tutorial documents the same pattern done by hand, without BaseLib,
   which corroborates the shape independently.

---

## Pattern table

| Pattern | Purpose | Pinned source | Base type it hangs off |
|---|---|---|---|
| **`Events/` as a combat-hook namespace** (the false positive) | Declare `IAfterX` / `IModifyY` interfaces and dispatch them over the combat state's hook listeners. Nothing to do with world events. | `Downfall@32e6113:DownfallCode/Events/MyHookUtils.cs:38-50`; doc comment at `DownfallCode/Events/DownfallHook.cs:11-17`; example interface `DownfallCode/Events/IAfterCardTransformed.cs:10-13` | `ICombatState.IterateHookListeners()`, `Hook.IterateCombatHookListeners()`, `IRunState.IterateHookListeners()` (`MegaCrit.Sts2.Core.Hooks`), listeners are `AbstractModel` subclasses |
| **Extend an existing base event's option list** | Add this mod's card pools as new pick-a-colour options inside the stock `Colorful Philosophers` event, without defining an event. | `Downfall@32e6113:DownfallCode/Patches/ColorfulPhilosophersPatch.cs:8-17` | Harmony postfix on `ColorfulPhilosophers.CardPoolColorOrder` getter (`MegaCrit.Sts2.Core.Models.Events`), returning `IEnumerable<CardPoolModel>` |
| **Event text supplied by localization overlay** | Ship only the option's title/description rows under the **base** event's id; no event object is created. Ten submods do this, one option each. | `Downfall@32e6113:Automaton/localization/eng/events.json:2-3` (and the nine sibling `*/localization/eng/events.json`) | loc category `events`; key grammar `EVENT.pages.PAGE.options.OPTION.title|.description` |
| **Event key grammar `pages → options`** | The base engine models an event as named pages, each with named options carrying title + description. | same as above; independently at `Downfall@32e6113:SneckoCode/Ancients/SneckoSpirit.cs:85` (`$"{Id.Entry}.pages.PAGE_{n}.description"`) | `EventModel` loc lookup via `L10NLookup` |
| **Ancient as an event-shaped multi-page choice tree** | Three sequential pages, two options each, each option grants a relic and advances the page; last page calls `Done()`. | `Downfall@32e6113:SneckoCode/Ancients/SneckoSpirit.cs:37-53` (initial options), `:55-59` (page builder), `:61-72` (option construction), `:74-92` (pick handler, `SetEventState` then `Done()`) | `BaseLib.Abstracts.CustomAncientModel` → `AncientEventModel` → `EventModel`; options are `EventOption` (`MegaCrit.Sts2.Core.Events`) |
| **`EventOption` construction signature** | An option is: owning model, async on-pick delegate, title, description, loc key, hover tips. A fluent `.WithRelic(...)` attaches the reward preview. | `Downfall@32e6113:SneckoCode/Ancients/SneckoSpirit.cs:69-71` | `new EventOption(EventModel, Func<Task>, LocString title, LocString desc, string textKey, IEnumerable<IHoverTip>)` |
| **Forcing entry into an event room** | Intercept map-coordinate entry and substitute an `EventRoom` wrapping a chosen model. | `Downfall@32e6113:SneckoCode/Patches/SneckoSpiritDialoguePatch.cs:55-77` | Harmony prefix on `RunManager.EnterMapCoord(MapCoord)`; `RunManager.EnterRoom(new EventRoom(model))`; `ModelDb.AncientEvent<T>()` |
| **Re-skinning the event room's presentation** | Replace the stock dialogue refresh so a custom transcript renders, then hand control back. | `Downfall@32e6113:SneckoCode/Patches/SneckoSpiritDialoguePatch.cs:17-45`, `:85-96` | `NEventRoom.RefreshEventState(EventModel)`, private `NEventRoom.SetOptions`, `NEventRoom.SetDescription`, `NEventRoom.GetDescriptionOrFallback()`, static `NEventRoom.Proceed()`; layout `NAncientEventLayout` (`…Core.Nodes.Events`) |
| **Looking an event up by id** | Events live in `ModelDb` under their own category and are fetched by `ModelId`. | `Downfall@32e6113:DownfallCode/Console/AncientVisitConsoleCmd.cs:29-32`; `DownfallCode/Patches/AncientSeaGlassConsolePatch.cs:59-61` | `ModelDb.GetByIdOrNull<EventModel>(new ModelId(ModelDb.GetCategory(typeof(EventModel)), ENTRY))`; `ModelDb.AllAncients` → `AncientEventModel` |
| **Events and Ancients are distinct map points** | Run telemetry counts "?" event choices as `RoomType.Event` **excluding** `MapPointType.Ancient`. | `Downfall@32e6113:DownfallCode/Data/DownfallMetrics.cs:82-84` | `MapPointHistoryEntry.MapPointType` vs `Rooms.First().RoomType` |
| **`CustomEventModel` — the real custom-event base** ✅ | Subclass it to define a genuinely new "?" event. Constructor auto-registers. Helpers build options and page descriptions with the right loc keys. | `Alchyr/BaseLib-StS2@2275793:Abstracts/CustomEventModel.cs` (release v3.4.5, 2026-08-14). Body read verbatim; line numbers UNCAPTURED (raw fetch is unnumbered) | `public abstract class CustomEventModel : EventModel, ICustomModel, ILocalizationProvider` |
| **Act routing via `Acts`** | `virtual ActModel[] Acts => []`. Empty array = a *shared* event that can spawn in any act; otherwise the named acts only. Its doc comment adds: for a custom act, set this rather than adding to the act model's own event list. | `Alchyr/BaseLib-StS2@2275793:Abstracts/CustomEventModel.cs` | `ActModel[]` |
| **Auto-registration into the pools** | Constructor calls `CustomContentDictionary.AddEvent(this)`, which sorts the event into `SharedCustomEvents` or `ActCustomEvents` by `Acts.Length`. | `Alchyr/BaseLib-StS2@2275793:Patches/Content/ContentPatches.cs` (quoted via fetch, not read line-numbered) | `CustomContentDictionary` (`BaseLib.Patches.Content`) |
| **Injection into the live event pools** | A Harmony **transpiler** on `ModelDb.AllSharedEvents` getter concatenates the shared list; a **postfix** applied per concrete act type to `ActModel.AllEvents` appends events whose `Acts` contain that act's id. | `Alchyr/BaseLib-StS2@2275793:Patches/Content/ContentPatches.cs` | `ModelDb.AllSharedEvents` (getter), `ActModel.AllEvents` (getter) |
| **Option loc keys derived from the handler's method name** | `Option(onChosen, pageKey)` builds the text key as `{Id.Entry}.pages.{pageKey}.options.{Slugify(methodName)}`, warns if the `.title`/`.description` rows are missing. `LockedOption(...)` makes a greyed-out option. | `Alchyr/BaseLib-StS2@2275793:Abstracts/CustomEventModel.cs` | `EventOption`, `LocString.Exists("events", key)`, `StringHelper.Slugify` |
| **Page description helper** | `PageDescription(pageKey)` → `L10NLookup($"{Id.Entry}.pages.{pageKey}.description")` — the same grammar Downfall's loc files use. | `Alchyr/BaseLib-StS2@2275793:Abstracts/CustomEventModel.cs` | `LocString` |
| **Custom art per event** | Two Harmony prefixes redirect `EventModel.InitialPortraitPath` and `EventModel.BackgroundScenePath` to the subclass's overrides; returning `null` falls through to stock. Plus `CustomVfxPath` (a `.tscn`). | `Alchyr/BaseLib-StS2@2275793:Abstracts/CustomEventModel.cs` | `EventModel.InitialPortraitPath` / `.BackgroundScenePath` getters |
| **Further overrides named by the library** | An in-file comment lists the other knobs: `LayoutType`, `CanonicalEncounter` (a *fight* event), `IsAllowed` (spawn condition), `IsShared` (all players must take the same option — **required for combat events**), `CanonicalVars`/`CalculateVars`. | `Alchyr/BaseLib-StS2@2275793:Abstracts/CustomEventModel.cs` | `EventModel` virtuals |
| **Hand-rolled custom act event, no library** (corroboration) | Subclass `EventModel` directly, override `GenerateInitialOptions()`, use `SetEventState` for another page vs `SetEventFinished` to end, then Harmony-postfix a concrete act's `AllEvents` getter (e.g. `Overgrowth.AllEvents`) appending `ModelDb.Event<T>()`; `ModelDb.AllSharedEvents` for act-agnostic. | `fresh-milkshake/Modding-Tutorial@dea5acc`, chapter 13 "Custom Act Events" (published at `fresh-milkshake.github.io/Modding-Tutorial/13-custom-act-events/`). **Documentation, not a shipped mod.** Targets game v0.103.3 | `EventModel`, `EventOption`, `ActModel.AllEvents` |

---

## Gotchas

1. **The folder name really is a trap.** Eleven submods each have a
   `*Code/Events/` directory; 72 files total; every one is a combat hook. The
   dispatcher iterates *combat* listeners and has a scope enum for
   run-level / combat / combat-while-ending
   (`Downfall@32e6113:DownfallCode/Events/MyHookUtils.cs:20-36`). If a sweep
   counted these as world-event evidence it would be wrong by 72 files.
2. **Ancients are not "?" rooms.** They share `EventOption`, the `pages` loc
   grammar, `SetEventState`, `EventRoom` and `NEventRoom` — but they are
   `MapPointType.Ancient`, and Downfall's own metrics explicitly subtract them
   when counting event choices
   (`Downfall@32e6113:DownfallCode/Data/DownfallMetrics.cs:82-84`). Treating
   "we can make an Ancient" as "we can make a ? event" would mis-scope the work.
3. **Downfall's only Ancient is switched off at the pinned commit.** The
   `ModPatcher` block registering all four Snecko Spirit patches is commented
   out, as is the run-start reset
   (`Downfall@32e6113:SneckoCode/SneckoMainFile.cs:28-34`, `:41`). The C#, the
   art and the dialogue lines all exist; the entry point does not. Do not cite
   it as a shipped feature.
4. **Non-ASCII inside ids.** The option loc keys embed a model id after a
   `∴` (U+2234 THEREFORE) separator —
   `CARD_POOL∴AUTOMATON-AUTOMATON_CARD_POOL`
   (`Downfall@32e6113:Automaton/localization/eng/events.json:2`). Any tooling
   of ours that assumes ASCII-safe keys will need to cope.
5. **Loc keys derived from method names are a rename hazard.** BaseLib's
   convenience `Option()` slugifies the delegate's method name into the key.
   Rename a handler and the key silently changes; BaseLib logs a warning when
   the row is missing but does **not** fail the build or the load.
6. **`IsShared` is a co-op constraint, not a nicety.** BaseLib's own comment
   says it forces all players onto the same option and is *required* for
   combat events.
7. **Two registration routes, only one correct per case.** BaseLib's `Acts`
   doc says that for a *custom* act you set `Acts` rather than adding to the
   act model's event list. Doing both, or the wrong one, is an available
   mistake.
8. **Version skew is unresolved.** Downfall pins BaseLib **3.4.5**
   (`Downfall@32e6113:build/mod.build.props:20`) and targets game **V107**
   (`Downfall@32e6113:Downfall.csproj:23`). Our repo pins BaseLib **3.3.7.0**
   (`docs/current/STATE.md:158-163`) via a Steam Workshop dll path
   (`klee-mod/local.props`), which is an auto-updating location, not a
   reproducible pin. The tutorial targets **v0.103.3**. Three different
   baselines.
9. *Pointer, S12g:* `Collector` and `Gremlins` have full code and localization
   trees but are absent from the default `Submods` list at
   `Downfall@32e6113:Downfall.csproj:18`.
10. *Pointer, S12a/S12b/S12c:* BaseLib's `Abstracts/` also carries
    `CustomMonsterModel`, `CustomEncounterModel` and `CustomActModel`
    (`Alchyr/BaseLib-StS2` at tag `v3.3.7`, directory listing — filenames
    only, bodies not read). Downfall uses `CustomMonsterModel` three times.
    Not my subsystem — handing over.

---

## Transfer questions

Questions against our own abstractions. Not proposals; nothing here recommends
building events.

1. **Pinning.** Downfall consumes BaseLib as a NuGet `PackageReference` at a
   fixed version. We consume it as a dll inside a Steam Workshop content
   folder that Steam updates underneath us. What would we have to decide to get
   a *reproducible* BaseLib before depending on any of this?
2. **Version proof.** `CustomEventModel.cs` exists by filename at BaseLib tag
   `v3.3.7` — the version STATE.md records — but I read its body only at
   v3.4.5. What would we have to check to know the 3.3.7 body has the same
   `Acts` routing and the same loc-key grammar?
3. **A new model category on the mod side.** Our C# uses `CustomCardModel`
   (299 classes), `CustomRelicModel` (6) and `CustomCharacterModel` (3) and
   nothing else content-shaped. Adopting `CustomEventModel` introduces a model
   kind our codegen, manifests and coverage ledgers have never carried. What
   would that do to `tools/gen_roster_cards.py`-shaped tooling and to the
   manifest coverage figures STATE.md quotes?
4. **Two event layers, one world.** `tier05/events.py` (827 lines) already
   interprets a full event grammar from `content/events.yaml` —
   `id / name / options / hidden / also_acts / variants` — with an explicit
   option-valuation policy, and the mod has no events at all. If events ever
   ship on the mod side, which layer is the source of truth, and does the
   constant-parity gate extend to event bodies?
5. **Are `Acts` and `also_acts` the same idea?** BaseLib routes by an
   `ActModel[]` (empty = shared). Our sim uses `also_acts` plus a `hidden`
   flag reachable only by escalation. BaseLib's comment also mentions a base
   rule that events already seen in a run are skipped until the act's pool is
   exhausted. What would we have to learn about that rule before our sim's
   "Unknown resolves to an event 55% of the time" is comparable to the game's?
6. **Co-op.** `IsShared` forces one option for all players and is required for
   combat events. Co-op has no sim backstop at all. How would an event's co-op
   path be tested here — is it play-only, like the rest of co-op?
7. **Localization discipline.** BaseLib derives option keys from handler
   method names and only warns when a row is missing. Our loc goes through
   `KleeMod.InjectLocStrings` with verb-keyed rows. What would a lint of ours
   have to assert so a renamed handler cannot ship an untranslated option?
8. **Patch stability.** Registration means Harmony-patching each concrete act
   type's `AllEvents` getter. What act types does v0.107.1 actually expose,
   and how stable is per-act-type patching across game updates? (This is
   S13's to answer from the decompile.)
9. **Save contract.** `SneckoSpirit.AfterCloned()`
   (`Downfall@32e6113:SneckoCode/Ancients/SneckoSpirit.cs:117-122`) clears
   per-run state, which suggests models are cloned per run. What happens to a
   half-finished multi-page event across a save/load, and across mod
   uninstall? (S12f / S20 territory — flagging, not answering.)

---

## NON-FINDINGS

- **No *released* public StS2 mod was found that defines a player-facing "?"
  room event.** Downfall — the largest released mod available to me, eleven
  submods, 5,209 tracked files — defines none. BaseLib supplies the mechanism
  but is a library, not content; I did not verify a BaseLib-shipped example
  event, and I could not enumerate consumer mods (below).
- **No act/map event-pool mutation in Downfall.** Every `RoomType` /
  `MapPointType` reference in the repo is a read (telemetry, card conditions,
  a console history append). Nothing adds or reorders map nodes. *(S12c's
  question, flagged here because I had to search the same ground.)*
- **No evidence either way on event save/serialization.** `AfterCloned()`
  hints at per-run cloning; I verified no save contract. Absence stays absence.
- **BaseLib's wiki page for `CustomEventModel` exists** (`docs/models/
  custom-event.html` in the wiki nav) **but I did not read its body** — the
  source code above is stronger evidence and I stopped there.

## Search boundary

Date **2026-08-26**. Charter §7 permits one widen; this is it, recorded in full.

**Primary source, read locally, exhaustive.** Downfall pinned at
`lamali292/Downfall@32e61132052ae58e32cd33342d24136ffe18be12` (depth-1 clone,
5,209 tracked files, read-only, outside the repo). Greps run over all tracked
C#/JSON: filenames matching `event`; `NEvent|EventPage|EventOption|EventData|
RoomEvent|Events\.(Register|Add)|EventRegistry`; every
`using MegaCrit.Sts2.Core.*Events`; `EventModel|EventRoom|EventOption|
NEventRoom|AncientEventModel|EventPool|EventRegistry`;
`MapPointType|RoomType\.|MapModel|ActModel|NodeType|IsValidForAct`;
`CustomEventModel`; `class X : EventModel|AncientModel|CustomAncientModel`;
`COLORFUL_PHILOSOPHERS`. The event surface is five files and I read all five in
full, plus all ten `localization/eng/events.json`.

**Widen — 3 web searches.** Queries: *"Slay the Spire 2 mod custom event
EventModel GitHub C# BaseLib"*; *"github 'Slay the Spire 2' mod
'CustomEventModel' OR 'EventOption' OR 'NEventRoom'"*; *"'CustomEventModel'
BaseLib Slay the Spire 2 mod github event pages options"*.

**Sources opened and used as evidence:**
`github.com/Alchyr/BaseLib-StS2` — repo root; `/Abstracts` at master and at tag
`v3.3.7`; `/Patches/Content`; raw `Abstracts/CustomEventModel.cs` at
`22757933ba10adc4322a628519a233a567507d87`; raw `LICENSE.txt` (**MIT**);
releases API (v3.4.5 published 2026-08-14, target master — i.e. tag v3.4.5 is
commit `2275793`); commits API. And
`github.com/fresh-milkshake/Modding-Tutorial@dea5accba9df27f3cfe39b181c28fcbe568863a0`
via its published site, chapter 13 only.

**Opened but not used as evidence:** `alchyr.github.io/BaseLib-Wiki` —
navigation list only.

**Seen in results and deliberately NOT opened** (summaries, mirrors, or
out-of-scope): `visist16/BaseLib-StS2`, `Alchyr/ModTemplate-StS2`,
`jiegec/STS2FirstMod`, `freude916/sts2-quickRestart`, the LobeHub MCP page, the
Nexus Mods pages, the Steam Workshop pages, `daviscook477/BaseMod` (StS1), and
GitHub topic listing pages.

**Boundary limit that matters:** GitHub **code search is behind an auth wall**
for this runner, so I could not enumerate repositories that *consume*
`CustomEventModel`. "No released consumer mod found" is therefore a limit of
the search, **not** a proof of absence.

**Evidence-quality note.** Downfall citations are `path:line` from the local
clone. The two BaseLib files were fetched over the web: `CustomEventModel.cs`
came back as a verbatim code block (member-level citations, **line numbers
uncaptured**), and `ContentPatches.cs` came back as quoted excerpts through a
fetch summarizer — treat its exact wording as quoted-not-verbatim while the
substance (patch targets, routing rule) is directly quoted code.

## What this does NOT establish

- **Not that we should build events.** Nothing here is a recommendation, a
  scope, a count, or a design. No id is minted.
- **Not that `CustomEventModel` works at our pinned BaseLib.** Only the
  filename is confirmed at v3.3.7; the body I read is v3.4.5.
- **Not that any of this is reachable in our game version.** Downfall targets
  V107, BaseLib v3.4.5's notes mention beta compat, the tutorial targets
  v0.103.3. The skew is unresolved here.
- **Not the runtime shape of `EventModel` itself.** Everything above is
  inferred from *callers* and from one library's subclass. The authoritative
  type inventory and the entry-to-exit trace for a world event are S13's, from
  the base decompile.
- **Not that Downfall "could not" make events.** It pins a BaseLib that
  provides the mechanism and chose not to use it. Why is not evidenced here,
  and I am not guessing.
- **Not a claim about the tutorial's correctness.** It is documentation whose
  code I did not compile or run; I cite it only as independent corroboration
  of the registration shape.
