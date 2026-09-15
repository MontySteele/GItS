using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// THE BASE OF EVERY DRESSED EVENT'S MECHANICS, and the one reason there is a
/// class here at all rather than a subclass of the base event itself.
///
/// A DRESSED EVENT CANNOT SUBCLASS ITS BASE EVENT. Two structural blocks, both
/// read off the 0.111.0 decompile and both written up in
/// `docs/current/operations/codegen.md`:
///
///   1. Sixty of the sixty-eight classes in
///      `MegaCrit.Sts2.Core.Models.Events` are `public sealed class X :
///      EventModel` -- `RoomFullOfCheese` included. The only unsealed eight
///      are the Ancient events, which no dressing touches. The subclass does
///      not compile.
///   2. Even unsealed, a base event hardcodes its loc keys as STRING LITERALS
///      -- `new EventOption(this, Gorge,
///      "ROOM_FULL_OF_CHEESE.pages.INITIAL.options.GORGE")` -- rather than
///      calling `EventModel.InitialOptionKey`, which is the derived one. A
///      subclass would inherit the BASE's keys and the dressed text would have
///      to overwrite a global row. Its handlers (`Gorge`, `Search`) are
///      `private` besides, so an override could not re-key them without
///      re-implementing them.
///
/// SO THE MIRROR IS THE SUBCLASSABLE THING. Each concrete mirror below
/// re-implements ONE base event's clauses, once, and every nation that dresses
/// that event is a generated one-line subclass of it with no body at all.
///
/// AND THE MIRROR'S KEYS ARE DERIVED, which is what makes that possible.
/// `EventModel.OptionKey` is
/// `$"{StringHelper.Slugify(GetType().Name)}.pages.{page}.options.{name}"` and
/// `ModelDb.GetEntry` is `StringHelper.Slugify(type.Name)`, so for a dressed
/// subclass BOTH resolve to the dressed name. A mirror that builds every key
/// through <see cref="EventModel.InitialOptionKey"/> and <see cref="PageKey"/>
/// re-keys itself per face for free.
///
/// ABSTRACT ON PURPOSE. `ReflectionHelper.GetSubtypesFromList` filters
/// `!type.IsAbstract` before `ModelDb.Init` calls `Activator.CreateInstance`
/// on each, so a mirror is never constructed, never holds a `ModelId` and
/// never appears in `ModelDb` -- only the concrete dressed subclasses do, which
/// is exactly what `ModelDb.Event&lt;T&gt;()` in the substitution table needs.
///
/// NOT GATED BY `#if TEYVAT_FRAME`, on `KleeCode.csproj`'s own argument for
/// this arm: `Teyvat/**` compiles both ways so one build can pin what the act
/// list and the event pool contain with the flag off AS WELL AS on. Nothing
/// here is reachable with the flag off, because `PullNextEventPatch` returns
/// on its first line.
/// </summary>
public abstract class TeyvatEventMirror : EventModel
{
    /// <summary>
    /// A non-INITIAL page key for THIS dressing --
    /// `SPRINGVALE_CHEESE_CELLAR.pages.GORGE.description` and the like.
    ///
    /// `EventModel` derives the INITIAL option keys (`OptionKey`) and the two
    /// top-level ones (`Title`, `InitialDescription`) from the type, but gives
    /// no helper for the page a chosen option lands on -- the base events
    /// write those out as literals. This is that helper, and it reads
    /// `Id.Entry` for the same reason: so the mirror never names a dressing.
    /// </summary>
    /// <param name="suffix">
    /// The part after `<c>&lt;entry&gt;.pages.</c>`, e.g.
    /// <c>GORGE.description</c> or <c>GORGE.selectionScreenPrompt</c>.
    /// </param>
    protected string PageKey(string suffix) => Id.Entry + ".pages." + suffix;
}
