## Codegen — roster cards

One character-aware generator emits the C# card classes from the canonical
YAML sheets. Klee is the compatibility baseline; Furina and Kokomi are the
other profiles.

```sh
.venv/bin/python tools/gen_roster_cards.py           # generate all profiles
.venv/bin/python tools/gen_roster_cards.py --check    # verify committed output, no write
```

The generator rejects unknown card-level fields as well as unknown effects
(load-bearing: `encore_cost` changes playability without being an effect).
Partial upgrades are forbidden — a card gets its complete ruled upgrade or lists
under `upgrades.no_upgrade_path`. Depth: `docs/current/atlas/klee-mod-cards.md`.

- **Cost lines are DERIVED from the printed spend, at TWO levels** (`EB-182`).
  A top-level `spend_spark` / `spend_charge` is the CARD's price and makes it
  unplayable below the bank (`combat.spark_cost` / `charge_cost` →
  `card_playable`; C# an `IsPlayable` override). A spend at the HEAD of a
  `choose_one` MODE is that MODE's price: the mode is not offered when the
  bank is short (`effects.mode_price` → `offered_modes` → `_chosen_mode`, the
  one seam the pilot, the falsifier and a replay all pass through; C#
  `ModalChoice.ModePrice` omits it from the choose-a-card screen, which the
  0.111.0 decompile gives no per-option disabled state to grey). The card
  stays playable while ANY mode is affordable; one with none is refused with a
  reason naming the price and the bank (`combat.modal_refusal`). A spend
  further down a mode body is a consequence, not a price, and is refused where
  it resolves as it always was.

## Codegen — Teyvat dressed events

```sh
.venv/Scripts/python.exe tools/gen_teyvat_events.py            # generate the active faces
.venv/Scripts/python.exe tools/gen_teyvat_events.py --check    # verify committed output, no write
.venv/Scripts/python.exe tools/gen_teyvat_events.py --refresh  # rebuild tools/data/sts2_base_events.json
```

### THE C# SHAPE, and why it is not what the spike did

The spike (`review/records/teyvat-spike-build-2026-09-15.md` item 2) MIRRORED
`RoomFullOfCheese` clause for clause into `SpringvaleCheeseCellar`. That does
not scale: thirty-eight (base event, face) pairs in act 1 alone would be
thirty-eight hand-copied bodies, each one a place for a mechanic to drift.

**A dressed event cannot subclass its base event.** Two structural blocks, both
read off the 0.111.0 decompile:

1. **Every base event class is `sealed`.** Sixty of the sixty-eight classes in
   `MegaCrit.Sts2.Core.Models.Events` are `public sealed class X : EventModel`
   — `RoomFullOfCheese` included; the only unsealed eight are the Ancient
   events (`Neow`, `Darv`, `Pael`, `Orobas`, `Tanx`, `Tezcatara`, `Vakuu`,
   `Nonupeipe`), which no dressing touches. `class SpringvaleCheeseCellar :
   RoomFullOfCheese` does not compile.
2. **The loc keys are string literals, not derived.** Even unsealed, each base
   event hardcodes its own keys —
   `new EventOption(this, Gorge, "ROOM_FULL_OF_CHEESE.pages.INITIAL.options.GORGE")`
   — rather than calling `EventModel.InitialOptionKey`, which IS derived
   (`OptionKey` is `$"{StringHelper.Slugify(GetType().Name)}.pages.{page}.options.{name}"`).
   A subclass would therefore inherit the BASE's keys and the dressed text
   would have to overwrite a global row. And the handlers (`Gorge`, `Search`)
   are `private`, so an override could not re-key them without re-implementing
   them anyway.

**So the shape is: one hand-written abstract MIRROR per base event, and a
generated one-line dressed subclass per (base event, face).**

```csharp
// Teyvat/Events/Mirrors/RoomFullOfCheeseMirror.cs   -- hand-written, once
public abstract class RoomFullOfCheeseMirror : TeyvatEventMirror { /* the base event's clauses */ }

// Teyvat/Events/Mondstadt/SpringvaleCheeseCellar.cs -- GENERATED, zero bodies
public sealed class SpringvaleCheeseCellar : RoomFullOfCheeseMirror { }
```

Everything the dressing needs derives from the subclass's NAME, and the
decompile says so:

- `ModelDb.GetEntry(type)` is `StringHelper.Slugify(type.Name)`, so
  `Id.Entry` is `SPRINGVALE_CHEESE_CELLAR` with no table anywhere.
- `ModelDb.GetCategoryType` walks `type.BaseType` until it reaches
  `AbstractModel`'s direct child, so an extra level of inheritance still
  resolves the category to `event`. Depth does not matter.
- `EventModel.Title` and `InitialDescription` are `Id.Entry + ".title"` and
  `Id.Entry + ".pages.INITIAL.description"`.
- `OptionKey` slugifies `GetType().Name`, which for the subclass is the
  dressed name — so a mirror that builds its keys through `InitialOptionKey`
  and the `PageKey` helper on `TeyvatEventMirror` re-keys itself for free,
  per face, with no generated code at all.
- `ReflectionHelper.GetSubtypesFromList` filters `!type.IsAbstract`, so the
  mirrors are NOT registered in `ModelDb` and the dressed subclasses are. One
  registration per dressed event, which is what the `PullNextEvent`
  substitution table needs to resolve `ModelDb.Event<T>()`.

The mirror is where the base game's clauses are re-implemented, and it is
written ONCE however many nations dress it. `RoomFullOfCheese` is in both act-1
faces; one mirror serves both.

### WHAT IS GENERATED AND WHAT IS NOT

Generated (never edit by hand): the dressed subclasses under
`Teyvat/Events/<Face>/`, and `Teyvat/TeyvatEventsGenerated.cs` — the loc rows
(a `TeyvatLoc` partial), the `PullNextEvent` substitution table, and the shape
table the headless pins read.

**The placeholder rule (EB-770).** A base loc row spells a runtime value with
a SmartFormat var — `[red]{RandomCard}[/red] is removed from your
[gold]Deck[/gold].` A dressed row may spell that value out in WORDS instead;
that is what a dressing is for. What it may not do is put a BRACKETED GLOSS in
its place: the engine reads `[...]` as a rich-text tag, finds no tag by that
name and deletes the group, so `[Specific card] is removed from your deck.`
reached the player as ` is removed from your deck.` The generator refuses that
shape, and refuses a var the base event does not declare. The var names it
reads the rows against are in the index as `key_vars` — identifiers, like
every other value there, so `--check` needs neither the game nor a decompile.
Rebuild them on a machine with the game installed:

```sh
python tools/gen_teyvat_events.py --refresh-vars   # reads localization/eng/events.json
                                                   # out of SlayTheSpire2.pck
```

A `Loss:` line is refused the same way when the base event has no lethal
option: the `.loss` row is written only for a base that `can_kill`, so the
line would be prose no run can reach.

Hand-written: the mirrors under `Teyvat/Events/Mirrors/`. A base event with no
mirror is REPORTED, not generated — the generator names it and moves on. That
list is the engineering queue for this surface.

A mirror's row in `MIRRORS` is a `MirrorSpec`, not just a class name, because
the index's key scrape is a regex over string literals and no scrape can say
how a face's lines pair with an event's keys. Seven shapes defeat it, and the
spec has a field for each:

| Shape | Field | What it says |
| --- | --- | --- |
| a `_LOCKED` twin, or a later-page option with no line | `extra_options` | the key, and the paired option it borrows its text from |
| source order, not list order | `options` | the face-paired keys in LIST order |
| a key built by concatenation | `pages` | the page keys a run can actually reach |
| a page two options share | `page_source` | which line supplies it |
| a later-page option that HAS a line | `options`, spelled as a full suffix | it pairs by position and is written where it sits |
| the face's lines are a TABLE, not options | `table_option` / `dish_table` | how the table folds into the key or keys that exist |
| the face line names its OWN key | `keyed` | the keys the face's `@` lines must fill |

The two table shapes un-parked act 1's final four.

**`keyed` — the line that carries its own key.** Position runs out at an event
whose reachable keys outnumber a wiki-shaped face's bullets, and borrowing a
neighbour's line there prints another branch's consequences on the button. So a
face may write a line that names the key it fills:

```
@pages.REJECT.options.DOUBLE_DOWN | Walk Out of the Opera — … This ends the run.
@pages.MERCHANT.description — The defendant is a Fleuve Cendre smuggler …
```

The first form is an OPTION and supplies `<entry>.<key>.title` and
`.description`; the second is a PAGE and supplies `<entry>.<key>`. The key is
the full suffix under the entry, spelled as the base event's own literals off
the decompile; the separator is an em dash and a plain ` - ` is accepted. A
keyed line is NEVER an option, so adding one cannot move what a face's
positional lines pair with. The mirror declares `keyed=KeyedLines((…))` and the
check is by NAME both ways: a declared key with no line on a face is a refusal
naming the key, and a line whose key no mirror declares is a refusal too.
`KeyedLines.optional` is for a key that already has a derivation (The Future of
Potions' `DONE`) — a face that writes a line wins, one that does not keeps
deriving; `positional=False` says the face's bullets are a reader's
restatement and the keyed list is the whole pairing (Tinker Time, Colossal
Flower). A mirror that declares `keyed` never falls back to the index's scrape
for its option or page lists. This is what un-parked acts 2 and 3's last three.

**A full-suffix key in `options`** — `pages.ALL.options.LINGER`,
`pages.DECIPHER.options.GIVE_UP` — is an option a LATER PAGE offers that the
face already writes a line for, because the wiki lists it beside the INITIAL
ones and the curation followed the wiki. It pairs by position exactly like a
bare name; the only difference is where its two rows are written. In the
generated `EventShape` it lands in `ExtraOptionKeys`, which is the full-suffix
list, because `OptionKeys` is the list the pins prefix with
`pages.INITIAL.options.`.

**`table_option`** is for an event with ONE option key and a face full of
lines. The Future of Potions builds up to three options, all under
`…options.POTION`, with the per-potion words supplied at runtime as `LocString`
vars; the face's five lines are the five rarities that one option can wear. The
title row becomes a SmartFormat `choose` over the rarity, whose arms are the
face's own five labels in the face's order plus the first again as the default
arm — `ChooseFormatter` is one of the extensions `LocManager.InitSmartFormat`
registers, and the shipped GERMAN row for this very key already uses it. The
description row is the FIRST line's outcome with declared literal-for-literal
`slots` swapped for the vars the engine fills (`a specified Common potion` →
`{Potion}`, and so on); a literal the face does not contain is a refusal, not a
silent no-op. Page text comes off the RAW line, because a page is looked up
through `L10NLookup`, which adds only the event's own `DynamicVars` — a page
row carrying `{Potion}` would be a format call on a var nobody supplies.

**`dish_table`** is for Endless Conveyor, whose grab option's key IS the rolled
dish (`…pages.ALL.options.<id>`, eight of them) and each of whose dishes also
needs a `DISHES.<id>.title` row that `CalculateVars` reads into
`CurrentDishTitle`. The face writes the belt as one line with the eight dishes
inside it; the hook splits its `<Name> (<effect>)` pairs and gives each dish its
name and its effect. Positional against the ids the spec lists in the face's
order, because a nation may rename every dish and a name match would then
quietly find nothing; a count that disagrees is a refusal. The grab LINE pairs
with `pages.ALL.options.LOCKED`, the one key on that branch that is not a dish
and the same option greyed out.

**The harvest count is a NOTE, not a refusal, once a mirror declares
`options`.** The count exists to stop a face's lines pairing with the wrong
keys, and the wiki writes a multi-page event's later options as it pleases —
Abyssal Baths lists Linger and Exit Baths beside the two INITIAL ones, Endless
Conveyor writes Leave as a bullet under the grab option rather than as an
option at all. A declared `options` list is read off the DECOMPILE, and the
pairing check compares the face against THAT. A mirror that declares no list
still pairs off the scrape, and there the harvest count is the only guard
there is.

The mirror's doc comment says which of its own keys are which, and the pins
read the generated `EventShape` rather than either.

**No face has a parked event.** All six faces generate every (base event,
face) pair they name; the only skip left is The Merchant___, whose wiki page
has no options section for a face to disagree with.

`tools/data/sts2_base_events.json` is the structural index the generator and
the pins both read: per base event the class name, the `Id.Entry`, the option
key names in order, the other page keys, whether an option can kill, and the
harvest's option count. **Identifiers only** — no method bodies and no
base-game prose, so the repo's decompile rule (`.gitignore:28`,
`csharp-build-spec.md` §0.3) is not bent. `--refresh` rebuilds it from a local
decompile; `--check` and CI never need one.

### THE ARM, AND WHY THE GENERATED FILES ARE NOT `#if`-ed OUT

`Teyvat/**` compiles in BOTH directions and is inert at runtime behind
`TeyvatFrame.Enabled` — `KleeCode.csproj`'s TEYVAT_FRAME block says why: the
arm's acceptance condition is a statement about what the act list and the
event pool CONTAIN with the flag off as well as on, and a pin compiled on only
one side of the switch could not say the first half. Generated events follow
the same rule the hand-written `SpringvaleCheeseCellar` already followed: the
class compiles always, the substitution table is read only when
`TeyvatFrame.Enabled`, and `gates.py`'s plain `dotnet test` therefore covers
every pin in this surface.

### THE REFUSALS

The generator exits nonzero, naming the event, when a face's option count
cannot be paired with the mirror's keys, when a face's option count disagrees
with the frozen harvest's AND the mirror declares no `options` list of its own,
when a `table_option`'s slot literal is not in the face, when a `dish_table`
parses a different number of dishes than the mirror names, when a keyed key the
mirror declares has no line on a face or a face writes one the mirror does not
declare, or when a face names a base event the game does not have. It SKIPS with a note an event the harvest
marks
`<<NO OPTIONS SECTION ON PAGE>>` (The Merchant___). Faces map to dressing act
ids in `FACES` at the top of the generator; acts 2 and 3 are listed there and
inactive — their acts exist since R273, so what they wait on now is their own
mirrors, not their sibling acts.

## Codegen — Teyvat dressed Ancients

```sh
.venv/Scripts/python.exe tools/gen_teyvat_ancients.py            # generate
.venv/Scripts/python.exe tools/gen_teyvat_ancients.py --check    # verify, no write
.venv/Scripts/python.exe tools/gen_teyvat_ancients.py --refresh  # rebuild
                                       # tools/data/sts2_base_ancients.json
```

R275 (2026-09-17): one body per Ancient per face, Darv is Alice on every face,
first pass is name / image / flavour and never a boon, art second.

### THE C# SHAPE, and why it is NOT the events pipeline's

The dressed EVENTS surface next door needs a hand-written abstract MIRROR per
base event, for two reasons that both fail here:

1. **The Ancients are the unsealed eight.** Sixty of the sixty-eight classes in
   `MegaCrit.Sts2.Core.Models.Events` are `sealed`; the exceptions are exactly
   `Neow`, `Darv`, `Pael`, `Orobas`, `Tanx`, `Tezcatara`, `Vakuu` and
   `Nonupeipe`. `class DvalinMondstadt : Neow` compiles.
2. **An Ancient's keys are DERIVED, not literals.** `AncientEventModel`
   overrides `LocTable => "ancients"`, and every string it shows hangs off
   `Id.Entry`, which `ModelDb.GetEntry` takes from
   `StringHelper.Slugify(type.Name)`:

   | what | member | key |
   | --- | --- | --- |
   | name | `EventModel.Title` | `<ENTRY>.title` |
   | epithet | `AncientEventModel.Epithet` | `<ENTRY>.epithet` |
   | dialogue | `AncientEventModel.DialogueSet` → `AncientDialogueSet.PopulateLocKeys(Id.Entry)` | `<ENTRY>.talk.<CHAR>.<X>-<Y>[r].ancient` / `.char`, plus `.next` |
   | the DONE page | `AncientEventModel.Done` | `<ENTRY>.pages.DONE.description` |

   None of the four is `virtual`, so there is nothing to override and nothing
   to re-implement: the subclass re-keys its whole text surface by existing.

**So the shape is one generated one-line subclass per (Ancient, face) and no
mirror at all** — `public sealed class DvalinMondstadt : Neow { }`.
`DefineDialogues()` and `AllPossibleOptions` are inherited untouched, so not one
mechanic is restated. `ModelDb.GetCategoryType` walks `BaseType` to
`AbstractModel`'s direct child, so the extra level still resolves to `event`,
and `ReflectionHelper.GetSubtypesInMods` registers the non-abstract dressings
the way it registers the dressed events.

### THE DIALOGUE, and who reads it

`AncientDialogueSet` is uniform across all eight: one `FirstVisitEverDialogue`,
five `CharacterDialogues` keyed by
`CharKey<Ironclad/Silent/Defect/Necrobinder/Regent>()` at `VisitIndex` 0 / 1 / 4,
and an `AgnosticDialogues` list (two for most, three for Vakuu, five for Neow).
A dialogue's LENGTH is `new AncientDialogue(params string[] sfxPaths)` in
compiled C# and no loc row can change it, which is what the index records and
the generator checks.

**Our roster reads the AGNOSTIC lines and nothing else.**
`GetValidDialogues` tries `CharacterDialogues.TryGetValue(characterId.Entry)`;
Klee, Kokomi and Furina are not keys there, so the lookup misses and the call
falls to the agnostic list (and, from visit two on, the repeating pool). A
`firstVisitEver` line is shown once per Ancient regardless of character. One
dialogue is shown per visit; its lines are paged with a Next button whose text
is the derived `<stem>.next`.

`IsRepeating` is derived from an `r` suffix on the line-0 key, and that is a
fact about the shipped loc PACK, not about any C# this repo reads — so a
dressed line is carried as COORDINATES (`TeyvatGeneratedAncients.AncientLine`)
and the stem is resolved against the live table at merge time.

### THE PICTURE

`EventModel.BackgroundScenePath` is `private`,
`SceneHelper.GetScenePath("events/background_scenes/" + Id.Entry.ToLowerInvariant())`,
and `NAncientEventLayout` instantiates it into `%AncientBgContainer`.
`EventModel.GetAssetPaths` also PRELOADS it for every `EventLayoutType.Ancient`,
so the getter is the patch target and `CreateBackgroundScene` is not — the same
argument `EventPortraitPatch` makes. Four more derived paths ride along:
`AncientEventModel.MapIconPath` / `MapIconOutlinePath`
(`packed/map/ancients/ancient_node_<entry>[_outline].png`),
`RunHistoryIconOutlinePath`, and
`ImageHelper.GetRoomIconPath(MapPointType.Ancient, RoomType.Event, Id)`, whose
suffix is `GetRoomIconSuffix`'s `modelId.Entry.ToLowerInvariant()`.

`Patches/AncientPicturePatch` postfixes all five and borrows the BASE Ancient's
file, but only when the dressed path does not exist (`ResourceLoader.Exists`) —
so the art bill R275 defers lands on that seam and the patch stands down per
entry, with no code change.

### THE POOLS, AND DARV

A face act answers `AllAncients` and `GetUnlockedAncients` by handing the BASE
act's own answer through `TeyvatGeneratedAncients.Dress`, a `Select`. Equal
length and equal order by construction, every epoch filter preserved (the Hive
removes Orobas behind `OrobasEpoch`), and the identity with the arm off.

Darv is not in any act. `ModelDb.AllSharedAncients` holds him alone,
`UnlockState.SharedAncients` gates him on `DarvEpoch`, and
`RunManager.GenerateRooms` shuffles the survivors on `Rng.UpFront` and deals
slices to `State.Acts.Skip(1)` through `ActModel.SetSharedAncientSubset`.
`Patches/AncientSharedPoolPatch` prefixes that hand-off — the one call that
knows both which Ancients were dealt and which act they were dealt to — and
swaps each for that face's dressing. Every rng draw is spent before the patch is
reached, so the deal is bit-identical to an undressed run's. Act 1 is never
dealt one (`Skip(1)`), so the two act-1 faces have no Darv body.

### THE LOC, AND WHY AN EMPTY FIELD IS AN ALIAS

`TeyvatAncients.RowsFor(LocTable)` builds the merge in two passes.

**Pass one is the ALIAS.** Every live row under `<BASE>.` is copied to
`<DRESSED>.` with the same suffix, through `GetLocStringsWithPrefix` (which
unions the table's own keys with its English fallback's) and `GetRawText`. That
is how an empty faces-file cell keeps the game's own line, in every language,
with no base-game prose in the repo.

**And it is why the BOONS stay the game's.** An Ancient's options are
`RelicOption<T>()`, and `EventOption.FromRelic` is
`eventModel.GetOptionTitle(textKey) ?? relic.Title` — `LocString.GetIfExists`,
so an absent row falls through to the RELIC's own rows. The generator has no
path that writes an option row, and a pin asserts it both ways.

**Pass two is the face's rows**, laid over the alias: the flat rows, then the
dialogue lines by coordinate. When a face moves a line from one speaker to the
other, the alias's copy of the OTHER suffix is dropped — leaving both would let
`AncientDialogue.PopulateLines` read the stale one, since it picks `.ancient`
over `.char` by existence.

### THE FACES FILE

`docs/current/dossiers/content/ancient-faces.tsv`, one row per (Ancient, face),
columns `ancient face name epithet first_visit dialogue_1 dialogue_2 dialogue_3
agnostic_1 agnostic_2 extra`. **A TSV and not one `.md` per face**, because an
Ancient's face is a short fixed list of fields rather than the events pipeline's
per-event prose sections — eighteen rows of fielded data, where the events
grammar's positional-bullet pairing would have nothing to pair against.

`name` is required; every other column may be empty and today every one is.
A dialogue cell's lines are `|`-separated and each carries a speaker prefix
(`A: ` the Ancient, `C: ` the character); `dialogue_1/2/3` take a per-character
form `IRONCLAD= ... ;; SILENT= ...` because the five characters' line counts
differ; `agnostic_2` carries every agnostic dialogue after the first,
`;;`-separated; `extra` is `key= text ;; key= text` over the suffixes the
index's `extra_keys` declares — `results.prefix` (Neow), `loss` (Vakuu),
`pages.INITIAL.options.OPTION_POOL_3_LOCKED.title` (Orobas).

`tools/data/sts2_base_ancients.json` is the structural index: per Ancient the
class name, the entry, that it is not sealed, the dialogue line counts and the
loc-key suffixes it spells. **Identifiers and counts only** — `--check` and CI
need neither the game nor a decompile.

### THE REFUSALS

The generator exits nonzero, naming the body, when the faces file is missing a
(Ancient, face) R275 owes, when a row names a face R273 did not rule or an
Ancient the game does not have, when a row has no name, when two rows claim one
body, when a dressed entry collides with another dressing's or with a BASE
Ancient's (which would make the merge rewrite the shipped game's own text), when
a dialogue cell's line count disagrees with the compiled base, when a dialogue
line has no speaker prefix, when a bare per-character cell is written for a
dialogue whose five characters have different lengths, and when an `extra` key
is not one the base entry has.

## Codegen — Teyvat creature scenes and motion

```sh
.venv/Scripts/python.exe tools/gen_teyvat_creature_scenes.py            # generate
.venv/Scripts/python.exe tools/gen_teyvat_creature_scenes.py --check    # verify, no write
.venv/Scripts/python.exe tools/gen_teyvat_creature_scenes.py --list     # the res:// scenes
.venv/Scripts/python.exe tools/gen_teyvat_creature_scenes.py --motions  # body -> motion
```

One table, `docs/current/dossiers/content/enemy-dressings.tsv`, columns `body
face base_entry display_name size_class motion notes`. One run writes three
things: the committed `.tscn` per scene under
`klee-mod/pck-src/teyvat/creature_visuals/`, the five motion libraries under
`klee-mod/pck-src/teyvat/motion/`, and the two C# tables in
`klee-mod/KleeCode/Teyvat/TeyvatCreaturesGenerated.cs`, plus the six bespoke
libraries under `motion/bespoke/`. `--check` fails on any drift and
`tier0/tests/test_teyvat_creature_scenes.py` rides it. Never hand-edit a file
in either directory.

### The scene shape, and the one node a clip may move

    root (Node2D)
      %Visuals (Node2D)        <- ENGINE-OWNED scale; nothing we author touches it
        Rig (Node2D)           <- the ONLY node an animation keys
          Body (Sprite2D)      <- carries the SIZE CLASS: position and scale
      %Bounds / %IntentPos / %CenterPos
      %AnimationPlayer         <- libraries = { "": the motion .tres }
      %AnimationTree           <- the four-state machine the router travels

`%Visuals.Scale` is `NCreature`'s (`ScaleTo`, `SetDefaultScaleTo`,
`OstyScaleToSize` write it, `UpdateBounds` reads it back), and `Body`'s
transform is what makes an elite bigger than a regular — so a clip that keyed
either would fight the engine or flatten every body to one size. `Rig` exists
to give the clips somewhere legal to write, and it is the same intermediate
Furina's rig already has (`pck-src/furina/model/combat.tscn`). The four legal
track paths are `Visuals/Rig:position`, `:scale`, `:rotation` and
`Visuals/Rig/Body:modulate`, pinned in the test file and in `ALLOWED_TRACKS`.

The state machine is Furina's, verbatim: Start auto-advances to idle; idle
reaches attack, hurt and death on a `Travel`; attack and hurt return to idle at
the end of the clip; death goes only to End and never returns.
`Vfx/CreatureAnimationRouter` drives it with no per-creature code.

### The motion column

Five shared sets — `stand`, `bounce`, `hover`, `loom`, `mech` — each an
`AnimationLibrary` `.tres` of five clips (`RESET`/`idle`/`attack`/`hurt`/
`death`). The library is EXTERNAL because 123 scenes would otherwise carry the
same ~200 lines of keyframes 25 times over; `build_pck.ps1` overlays
`klee-mod/pck-src` verbatim (`:1092-1098`) and the pck contract is derived from
that work directory after the copy, so a `.tres` packs and contracts exactly as
a `.tscn` does with no change to either.

`motion` is a property of the ROW, like `size_class`, and splits a body's
scenes the same way when two rows disagree: the suffix names only the axis that
varies, so `<body>_<class>`, `<body>_<motion>` or `<body>_<class>_<motion>`
(`_assign_scene_ids`). Today only `golden_wolflord` splits, and on class alone.

`default_motion()` is the rule that FILLED the column and is what gives a row
added tomorrow a motion; it is a suggestion and never a gate, so vetoing one
row is a one-cell edit.

### Bespoke rigs — the sixth motion value

`motion = bespoke` is the sixth legal value and the one that is not shared.
Six bosses carry it: `azhdaha`, `all_devouring_narwhal`, `rhodeia_of_loch`,
`emperor_of_fire_and_iron`, `golden_wolflord`,
`everlasting_lord_of_arcane_wisdom`. Such a row draws not one plate but the
LAYERS that plate was cut into, and its library is its own:

    Rig (Node2D)                 <- still the node the whole-body clips key
      <layer> (Sprite2D) x2-3    <- one per cut layer, named for the layer
    %AnimationPlayer             <- res://teyvat/motion/bespoke/<body>.tres

Three artefacts make a bespoke body, and `--check` refuses the row by name if
any is missing:

| what | where | committed? |
|---|---|---|
| the fence | `tools/combat_layer_fences/teyvat/<body>.yaml` | yes |
| the cut manifest | `tools/combat_layer_fences/teyvat/<body>.layers.json` | yes |
| the layer PNGs | `ImageGen/images/teyvat/creature_visuals/<body>/layers/` | no (Tier F) |

The manifest is committed on purpose: the pixels are gitignored and a worktree
never has them, so a manifest living beside them would make `--check`
unrunnable anywhere but the art checkout. It is produced by the cutter
(`operations/art.md`), holds one `{file, w, h, offset_x, offset_y}` per layer
in BACK-TO-FRONT order, and that order is the scene's node order.

**The size class rides `scale`, the placement rides `offset`.** A layer sprite
sits at `position = (0, 0)` with `scale = (s, s)` — the same `s` `Body` carries
— and its place on the plate is a `Sprite2D.offset` of `(offset_x, offset_y −
140)`, applied inside the node transform. The drawn result is identical to a
`position`, and the reason for the swap is the Golden Wolflord: it is a boss on
one face and a regular on another over ONE library, so a rest pose that
depended on the class could not be keyed. With `position` at zero every clip
key is a pure delta and the pivot is the rig origin — the creature's feet,
which is what "a claw raises about its base" wants and why every rotation here
is small. `%Bounds`, `%IntentPos` and `%CenterPos` are byte-identical to the
shared-set row's, pinned that way.

Legal track paths widen by exactly one step: `Visuals/Rig:position|scale|
rotation` as before, plus `Visuals/Rig/<layer>:position|rotation|scale|
modulate` for a layer the body actually has (`legal_track`). `Visuals/Rig/Body`
is that rule read on a shared-set body, so one predicate covers both passes.

Adding a seventh boss: cut it, commit the fence and the manifest, add a builder
to `BESPOKE_CLIPS`, flip the row's `motion` cell, regenerate, and add the layer
rows to the contract fixture.

### Death timing

`Vfx/ModdedPlayerDeathSeam` gained a second arm. The base's `StartDeathAnim`
puts its clip measurement behind `if (_spineAnimator != null)`, so a spine-less
body reports a death animation zero seconds long and `Hook.AfterDeath` tears it
out of the arena before a frame draws. The new arm reports the real clip length
for a DRESSED body only — gated on `TeyvatFrame.Enabled` and on the creature's
registered visuals scene living under `res://teyvat/creature_visuals/` — plays
no sound (the death sting is the player's), and hands back the base's own
answer when there is no clip to measure. With the arm off nothing changes.
