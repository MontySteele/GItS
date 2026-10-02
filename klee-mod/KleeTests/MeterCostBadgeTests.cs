using System.Linq;
using System.Reflection;
using KleeMod.Cards;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// THE METER COST BADGE, pinned (EB-220).
///
/// [USER], 2026-08-30: "Yes, I think Encore and Charge need badges." The badge
/// itself cannot be exercised here -- painting needs Godot nodes, which are
/// process death in this host (README, the headless boundary) -- but everything
/// the badge is FOR is a plain read off a card, and those are pinned for real:
/// what each meter charges, whether the bank can pay it, and the one structural
/// fact that keeps the display honest, namely that the badge asks the same
/// function the gate asks.
///
/// THIS FILE IS NOT UNDER `Prototype/`, unlike the Spark badge's pin was. That
/// is the change: the badge used to be quarantined because every priced face it
/// drew was a prototype row, and Encore's priced faces are shipped Furina cards.
/// </summary>
public class MeterCostBadgeTests
{
    private const BindingFlags All = HeadlessGame.All;

    /// <summary>A card in a seat's hand: mutable, owned, and therefore askable.
    /// `IsMutable` first -- Owner's setter calls AssertMutable, which is EB-94's
    /// throw met from the other side.</summary>
    private static T Held<T>(Seat seat) where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        Seat.Set(card, "Owner", seat.Player);
        return card;
    }

    // --- the badge reads the gate's own number ----------------------------

    [Fact]
    public void The_badge_renders_the_price_and_the_affordability_it_is_told()
    {
        // STRUCTURAL PIN, and the property it pins is the badge's whole reason
        // to exist: it asks MeterCost for the price and for affordability
        // rather than carrying either rule itself. A badge with its own copy of
        // a price -- the display-versus-gate drift this repairs -- would show up
        // here as the absence of these calls.
        var calls = Il.Calls(Il.Method("MeterCostBadge", "Paint"));

        Assert.Contains(calls, c => c.EndsWith("MeterCost.Priced"));
        Assert.Contains(calls, c => c.EndsWith("MeterCost.Affordable"));
    }

    [Fact]
    public void Every_meter_bank_is_the_paying_call_s_own_read()
    {
        // STRUCTURAL PIN. The bank read is the accessor the payment gates on:
        // SparkPower.CanSpend reads SparksAtPlay. (Encore and Charge went with
        // the shipped kits, legacy cleanup stage 5.)
        var calls = Il.Calls(Il.Method("MeterCost", "BankOf"));

        Assert.Contains(calls, c => c.EndsWith("SparkPower.SparksAtPlay"));
    }

    // --- EB-222: the badge holds no texture across scenes ------------------

    [Fact]
    public void The_badge_caches_no_engine_owned_object_in_a_static_field()
    {
        // THE REGRESSION, made impossible. EB-220 kept its glyphs in a
        // `static readonly Dictionary<Meter, Texture2D?>`: one load for the
        // process, held forever. The game frees a room's assets WITH the room
        // ("Preloading 'Combat Room' assets" in, `Asset not cached:
        // res://klee/powers/bomb.png` out), so by the first card drawn in
        // combat #2 that field held a disposed `CompressedTexture2D`, and
        // handing it to `TextureRect.SetTexture` threw
        // `ObjectDisposedException` out of the TURN LOOP -- the combat stuck,
        // the run over, every `understudy.soak` run.
        //
        // A resource whose lifetime the engine owns therefore may not be
        // reachable from a static of ours, not directly and not inside a
        // collection. This reads FIELD TYPES ONLY -- no Godot object is
        // touched, which is itself the headless boundary (README).
        var badge = Il.Method("MeterCostBadge", "Paint").DeclaringType!;
        var offenders = badge
            .GetFields(BindingFlags.Static | BindingFlags.Public
                       | BindingFlags.NonPublic)
            .Where(f => IsEngineOwned(f.FieldType))
            .Select(f => f.Name)
            .ToList();

        Assert.Empty(offenders);
    }

    /// <summary>A type that is, or contains, something the ENGINE allocates and
    /// frees. Names only: comparing a type's name does not touch a Godot
    /// object, which is the headless boundary this pin has to respect.</summary>
    private static bool IsEngineOwned(System.Type type)
        => (type.FullName ?? string.Empty)
               .StartsWith("Godot.", System.StringComparison.Ordinal)
           || type.GetGenericArguments().Any(IsEngineOwned)
           || (type.IsArray && IsEngineOwned(type.GetElementType()!));

    [Fact]
    public void The_glyph_is_resolved_from_the_loader_on_every_paint()
    {
        // STRUCTURAL PIN (painting needs Godot nodes -- README's boundary).
        // Two halves of EB-222's fix, both in the one method the badge asks for
        // a texture through: it goes to `ResourceLoader` each time (so the
        // engine's own cache, which knows what it has freed, is the source),
        // and it asks `IsInstanceValid` before answering (so a wrapper for an
        // object that is already gone is never handed on). Re-introduce a
        // dictionary in front of the load and the pin above fails; drop the
        // validity check and this one does.
        var calls = Il.Calls(Il.Method("MeterCostBadge", "Glyph"));

        Assert.Contains(calls, c => c.EndsWith("ResourceLoader.Load"));
        Assert.Contains(calls, c => c.EndsWith("GodotObject.IsInstanceValid"));
    }

    [Fact]
    public void A_freed_glyph_degrades_to_no_glyph_and_still_paints_the_number()
    {
        // STRUCTURAL PIN, and the shape is EB-221's: warn once, draw less, never
        // throw at the caller. `Paint` runs inside `CardPileCmd.Draw`, i.e.
        // inside the turn loop, so the ONE thing it may never do is propagate.
        //
        // Three facts, in the order they matter: the write to the icon goes
        // through the guarded setter rather than straight at the node; that
        // setter catches `ObjectDisposedException` (the exact exception the
        // shipped stack carries) instead of letting it out; and the number is
        // painted AFTER the glyph, so the degraded path still leaves a price on
        // the card. The last one is a sequence read: `SetGlyph` precedes
        // `SetTextAutoSize` in `Paint`'s call order.
        var paint = Il.CallSequence(Il.Method("MeterCostBadge", "Paint"))
            .Select(c => c.Split('<')[0])
            .ToList();

        Assert.Contains("MeterCostBadge.SetGlyph", paint);
        Assert.True(
            paint.IndexOf("MeterCostBadge.SetGlyph")
                < paint.FindIndex(c => c.EndsWith("SetTextAutoSize")),
            "the number must be painted after the glyph, so a freed glyph still "
            + "leaves the price on the card");

        var handled = Il.Method("MeterCostBadge", "SetGlyph")
            .GetMethodBody()!.ExceptionHandlingClauses
            .Where(c => c.Flags == ExceptionHandlingClauseOptions.Clause)
            .Select(c => c.CatchType?.Name)
            .ToList();

        Assert.Contains("ObjectDisposedException", handled);
        Assert.Contains(
            Il.Calls(Il.Method("MeterCostBadge", "WarnFreedGlyph")),
            c => c.EndsWith("Log.Warn"));
    }

    // --- R225 item 5: every meter wears a glyph ---------------------------

    // --- Sparks, unchanged by the generalisation --------------------------

    // --- Encore: the top-level cost line ----------------------------------

    // --- Encore: a MODE's cost line ---------------------------------------

    // --- affordability, per meter -----------------------------------------

    // --- what is NOT badged, and each is a decision -----------------------

}
