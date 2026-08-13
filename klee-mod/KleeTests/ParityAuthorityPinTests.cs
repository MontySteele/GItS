using System.Linq;
using KleeMod.Cards;
using KleeMod.Cards.Furina.Generated;
using KleeMod.Powers;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// The C#-parity findings of the 2026-08-13 correctness audit, PINNED AS THE
/// AUTHORITY RECORD. Nothing here is a fix and nothing here should be "made
/// to pass" by editing the mod.
///
/// All three findings (H3, M1, M2) are divergences between the shipped mod and
/// tier0, and in all three the audit places the repair on the SIM side
/// (BACKLOG EB-97, EB-100, EB-101 -- the window-2 batch, EB-104). A window-2
/// agent needs to know precisely what the mod does today, from a running
/// binary rather than from a reading of the source; that is what these are.
///
/// If a window-2 change moves any assertion below, the mod's behaviour moved,
/// and that is a finding in its own right.
///
/// H3's value pins live in <see cref="DerivationPinTests"/> (they need the same
/// Creature fixture as the rest of the cap arithmetic).
/// </summary>
public class ParityAuthorityPinTests
{
    // ---------------------------------------------------------------
    // M1 -- Supporting Cast's first-play draw resolves AFTER the card in the
    // mod and BEFORE it in tier0.
    //
    // Structural pin (see Harness/Il.cs for what that means and what it
    // cannot see). Reproducing the hand contents end to end needs a live
    // combat, which is outside the headless boundary; the divergence itself
    // is that the RECORD and the RESOLVE sit in two different hooks, and that
    // is readable from the two hooks' call sets.
    //
    // Both refuters noted the mod's leg is not movable anyway --
    // BeforeCardPlayed is not async and carries no PlayerChoiceContext, so it
    // could not await a draw even if it wanted to. That is pinned too: the
    // return type.
    // ---------------------------------------------------------------

    [Fact]
    public void M1_authority_the_spotlight_draw_is_RECORDED_before_the_card_resolves()
    {
        var before = Il.Method("FurinaResourceHooks", "BeforeCardPlayed");

        Assert.Contains("SpotlightSystem.NotePlay", Il.Calls(before));
        Assert.DoesNotContain("SpotlightSystem.ResolvePendingDraw", Il.Calls(before));
    }

    [Fact]
    public void M1_authority_the_spotlight_draw_is_RESOLVED_after_the_card_resolves()
    {
        var after = Il.Method("FurinaResourceHooks", "AfterCardPlayed");

        Assert.Contains("SpotlightSystem.ResolvePendingDraw", Il.Calls(after));
        Assert.DoesNotContain("SpotlightSystem.NotePlay", Il.Calls(after));
    }

    [Fact]
    public void M1_authority_note_play_is_synchronous_and_cannot_draw()
    {
        // A draw is `await CardPileCmd.Draw(...)`. NotePlay returns void and
        // takes no PlayerChoiceContext, so the deferral is structural rather
        // than a choice the mod could reverse in place.
        var notePlay = typeof(SpotlightSystem)
            .GetMethod(nameof(SpotlightSystem.NotePlay), HeadlessGame.All)!;
        Assert.Equal(typeof(void), notePlay.ReturnType);

        var resolve = typeof(SpotlightSystem)
            .GetMethod(nameof(SpotlightSystem.ResolvePendingDraw), HeadlessGame.All)!;
        Assert.Equal(typeof(System.Threading.Tasks.Task), resolve.ReturnType);
        Assert.Contains(resolve.GetParameters(),
            p => p.ParameterType.Name == "PlayerChoiceContext");
    }

    // ---------------------------------------------------------------
    // M2 -- Encore Performance is dead text in tier0 under the upgraded
    // starter, and live in the mod.
    //
    // The whole divergence is one predicate: tier0's copy op early-returns on
    // a raw designation pointer that R2's both-modes relic never sets, while
    // the C# card asks SpotlightSystem.IsSpotlighted, which honours
    // BothModes. This runs the real card model and the real predicate.
    // ---------------------------------------------------------------

    [Fact]
    public void M2_authority_a_furina_card_is_spotlighted_under_the_both_modes_relic()
    {
        var seat = Seat.Furina().WithRelic<CurtainNeverFalls>();
        var card = PlayableCopyOfEncorePerformance(seat);

        Assert.IsAssignableFrom<ICharacterCard>(card);
        Assert.True(SpotlightSystem.BothModes(seat.Creature));
        Assert.True(SpotlightSystem.IsSpotlighted(card));
    }

    [Fact]
    public void M2_authority_without_the_relic_and_without_a_mode_it_is_not()
    {
        // The base-mode leg, so the test above is not passing for a reason
        // unrelated to the relic.
        var seat = Seat.Furina().WithCombatState();
        var card = PlayableCopyOfEncorePerformance(seat);

        Assert.False(SpotlightSystem.BothModes(seat.Creature));
        Assert.False(SpotlightSystem.IsSpotlighted(card));
    }

    /// <summary>
    /// A working copy of the card, owned by one seat.
    ///
    /// A freshly constructed CardModel is CANONICAL -- the shared prototype --
    /// and both its Owner getter and its Owner setter call AssertMutable, so
    /// the prototype cannot answer an ownership question. The game's own escape
    /// hatch, ToMutable(), resolves through ModelDb, a registry only the game's
    /// boot populates (outside the headless boundary). So the same flag
    /// ToMutable sets is set directly: IsMutable, through its own setter. From
    /// there the real Owner setter runs, and every predicate under test reads
    /// the real fields.
    /// </summary>
    private static EncorePerformance PlayableCopyOfEncorePerformance(Seat seat)
    {
        var card = new EncorePerformance();
        Seat.Set(card, "IsMutable", true);
        Seat.Set(card, "Owner", seat.Player);
        return card;
    }

    [Fact]
    public void M2_authority_encore_performance_reads_the_hand_during_its_own_resolution()
    {
        // The other half of why M1 and M2 meet on this card: its OnPlay reads
        // the hand pile and filters it through IsSpotlighted. Structural pin
        // -- it is what makes the M1 ordering observable at all.
        var onPlay = typeof(EncorePerformance)
            .GetMethod("OnPlay", HeadlessGame.All)!;
        var calls = Il.Calls(onPlay);

        Assert.Contains("CardPile.Get", calls);
        Assert.Contains("SpotlightSystem.IsSpotlighted", calls);
    }
}
