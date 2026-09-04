using System;
using System.Reflection;
using System.Threading.Tasks;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE FURINA REFRAME'S STARTER SEAM -- R254, round 4 pick 1, 2026-09-04.
///
/// [USER], ruling <c>review/ruled/furina-reframe-round-4-2026-09-04.md</c>
/// sec.6: "maybe a reader in the starter deck? I still want to leave it at
/// just 2 'good' cards, but they can be stronger." Her two kit starters stay
/// two and ONE of them reads Fanfare -- <i>Aria of Recompense</i>, under the
/// arm only: "Gain 5 Encore. If you have at least 6 Fanfare, gain 5 more."
/// Both numbers are lifted rather than picked (the 5 is Aria's own printed
/// Encore, the 6 the bar the four rider copies already carry), so no number
/// here was decided on this side of the wire.
///
/// TWO FACTS, the same two the sim pins
/// (<c>tier0/tests/test_furina_reframe_starter.py</c>): the arm deals the copy
/// and a flag-off run deals the shipped card, and the copy pays 5 below the
/// bar and 10 at it.
///
/// THE FIRST IS STRUCTURAL AND THE SECOND IS REAL, and the split is forced
/// rather than chosen. <c>Furina.StartingDeck</c> resolves every slot through
/// <c>ModelDb.Card&lt;T&gt;</c>, which throws until the game boots, so what
/// the deck HOLDS can only be read off the emitted calls -- the same seam
/// <c>KurageMemoryPinTests.The_starter_swap_happens_at_exactly_one_seam</c>
/// reads one character over. What the card DOES needs no model table at all,
/// so it is played.
///
/// NOTHING MEASURED HERE IS QUOTABLE (R215 B): a prototype row's arithmetic,
/// not a number about a game.
/// </summary>
public class FurinaReframeStarterTests
{
    private sealed class Arm : IDisposable
    {
        private readonly bool _enabled = FurinaReframe.Enabled;

        internal Arm(bool master) { FurinaReframe.Enabled = master; }

        public void Dispose() { FurinaReframe.Enabled = _enabled; }
    }

    // ==================================================================
    // 1. WHICH CARD THE RUN IS DEALT -- one seam, both sides of the flag.
    // ==================================================================

    [Fact]
    public void The_starter_swap_happens_at_exactly_one_seam()
    {
        // ONE SEAM, so the mod and the sim cannot disagree about what she opens
        // with -- `loader._starter_ids` is the sim's, and this is its twin. The
        // authored deck reaching the seam at all is what makes there be only
        // one: if a second site ever swapped a starter card, the getter would
        // still be the only place this list is built.
        var getter = Il.CallSequence(Il.Method("Furina", "get_StartingDeck"));

        Assert.Contains("FurinaReframeRoster.StarterAria", getter);
        // And the slot is no longer filled unconditionally: a getter that still
        // named the shipped card directly would deal it under the arm too.
        Assert.DoesNotContain("ModelDb.Card<AriaOfRecompense>", getter);
    }

    [Fact]
    public void The_seam_names_the_copy_and_the_shipped_card()
    {
        // BOTH BRANCHES, read off the seam itself. With the arm off it is the
        // shipped card byte for byte -- the acceptance condition on the flag --
        // and with it on it is the copy. A seam that named only one of them
        // would be a swap that cannot be turned off, or one that never happens.
        var calls = Il.CallSequence(Il.Method("FurinaReframeRoster",
                                              "StarterAria"));

        Assert.Contains("ModelDb.Card<ProtoFrAriaOfRecompense>", calls);
        Assert.Contains("ModelDb.Card<AriaOfRecompense>", calls);
        Assert.Contains("FurinaReframe.get_Enabled", calls);
    }

    [Fact]
    public void The_swap_is_one_card_for_one_card()
    {
        // What keeps this a substitution rather than a starter rework: the deck
        // the getter builds is still TEN slots -- nine `ModelDb.Card<T>` sites
        // plus the one seam. Counted off the ORDERED read, which keeps the
        // three Soloist copies distinct; the set-valued `Calls` would fold them
        // and could not see a slot go missing.
        var getter = Il.CallSequence(Il.Method("Furina", "get_StartingDeck"));
        var slots = 0;
        foreach (var call in getter)
        {
            if (call.StartsWith("ModelDb.Card<", StringComparison.Ordinal)
                || call == "FurinaReframeRoster.StarterAria")
            {
                slots++;
            }
        }

        Assert.Equal(10, slots);
        Assert.Contains("ModelDb.Card<SalonDebut>", getter);
    }

    // ==================================================================
    // 2. WHAT THE COPY PAYS. The bar is 6; 5 is one under it.
    // ==================================================================

    [Theory]
    [InlineData(5, 5)]     // one under the bar: the shipped line alone
    [InlineData(6, 10)]    // at the bar: the shipped line and the reader
    public void The_copy_pays_the_reader_only_at_the_bar(int fanfare, int paid)
    {
        // REAL: the row's own `OnPlay`, on a seat whose meter is set to the
        // amount under test. `ReadableFanfare` is what the generated body
        // asks, and it is the clamped read -- so a seat with a debt gets the
        // base line and nothing more, which is the behaviour every other
        // Fanfare reader in this kit already has.
        using var _ = new Arm(master: true);
        var seat = Seat.Furina().WithCombatState();
        FurinaResources.GainFanfare(seat.Creature, fanfare);
        Assert.Equal(fanfare, FurinaResources.Fanfare(seat.Creature));

        Play(Held<ProtoFrAriaOfRecompense>(seat));

        Assert.Equal(paid, FurinaResources.Encore(seat.Creature));
    }

    [Fact]
    public void The_shipped_card_never_reads_the_meter()
    {
        // The R130 veto stands where it was ruled ([USER], 2026-08-07: the
        // starter gets no payoff). R254 moves a PROTOTYPE arm rather than
        // reversing it, so the shipped row still gains 5 off a full meter --
        // and its body does not ask the meter at all.
        var calls = Il.Calls(Il.Method("AriaOfRecompense", "OnPlay"));

        Assert.Contains("FurinaResources.GainEncore", calls);
        Assert.DoesNotContain("FurinaResources.ReadableFanfare", calls);
    }

    [Fact]
    public void The_copy_reads_the_meter_through_the_clamped_reader()
    {
        // ONE READER FOR THE WHOLE KIT. `ReadableFanfare` clamps at zero, so a
        // seat carrying a Fanfare debt (Track C.2 leaves one on purpose) gets
        // the base line and nothing worse -- the same door every other Fanfare
        // gate in this mod goes through. A row that read the raw field would
        // be a second rule about the same meter.
        var calls = Il.Calls(Il.Method("ProtoFrAriaOfRecompense", "OnPlay"));

        Assert.Contains("FurinaResources.ReadableFanfare", calls);
        Assert.Contains("FurinaResources.GainEncore", calls);
    }

    // ==================================================================
    // Fixtures.
    // ==================================================================

    /// <summary>A card in a seat's hand: mutable, owned, and therefore
    /// playable. `IsMutable` first -- Owner's setter calls AssertMutable.
    /// Lifted from <c>FurinaReframeSliceTwoTests.Held</c>.</summary>
    private static T Held<T>(Seat seat) where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        Seat.Set(card, "Owner", seat.Player);
        return card;
    }

    /// <summary>The row's own `OnPlay`, awaited.
    ///
    /// Reflective because the method is `protected`: a generated card's play
    /// body is not public API, and the alternative -- restating the two
    /// `GainEncore` calls here -- would assert this file's arithmetic rather
    /// than the card's. Neither parameter is touched by this row, so both are
    /// passed as their defaults.</summary>
    private static void Play(CardModel card)
    {
        var play = card.GetType()
            .GetMethod("OnPlay", HeadlessGame.All)!;
        var task = (Task)play.Invoke(card, new object?[] { null, null })!;
        task.GetAwaiter().GetResult();
    }
}
