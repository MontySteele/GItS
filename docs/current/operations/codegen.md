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

Hand-written: the mirrors under `Teyvat/Events/Mirrors/`. A base event with no
mirror is REPORTED, not generated — the generator names it and moves on. That
list is the engineering queue for this surface.

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
disagrees with the frozen harvest's, or a face names a base event the game
does not have. It SKIPS with a note an event the harvest marks
`<<NO OPTIONS SECTION ON PAGE>>` (The Merchant___). Faces map to dressing act
ids in `FACES` at the top of the generator; acts 2 and 3 are listed there and
inactive, because their sibling acts do not exist yet.
