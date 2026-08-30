#nullable enable

using System.Collections.Generic;
using STS2_MCP;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// EB-184: A TARGET DEMANDED OF A MODE THAT ATTACKS NOTHING.
///
/// Kokomi slice 1 round 4, `t02`. The seat took the *Gain 3 Block* half of an
/// Attack-typed modal and wrote no target, correctly from the printed face;
/// the bridge answered *"Card requires a target"* and the line never resolved.
/// The refusal came from ONE test -- `card.TargetType == TargetType.AnyEnemy`
/// -- and the card's TargetType is not the question. The game aims a card
/// BEFORE its mode is chosen, so a modal with one aiming mode MUST declare
/// `AnyEnemy`; what has to be asked is the chosen MODE.
///
/// This file exercises the reader that answers it, headlessly, on the pattern
/// `GitsPortPrecedenceTests` set: the vendored source is COMPILED into this
/// assembly, not forked, and the cards below are fakes with the two members
/// the real generated cards carry (`KleeMod.Cards.IModalCard`). That the
/// generated cards actually carry them is pinned from the Python side, in
/// `tier0/tests/test_eb184_mode_targeting.py`.
///
/// BOTH DIRECTIONS ARE HERE. The repair is that a targetless mode stops owing
/// a target; the half that must not move is that an AIMING mode still does,
/// and so does a card that named no mode at all.
/// </summary>
public class GitsModalTargetingTests
{
    /// <summary>`proto_thoma_crimson_ooyoroi_either` -- the round-4 card, as
    /// codegen emits it: mode 1 aims, mode 2 is the Block the seat took.</summary>
    private sealed class ThomaLike
    {
        public IReadOnlyList<string> ModeLabels =>
            new[] { "Deal 8 damage, applying its element",
                    "Gain 3 Block, applying no element" };

        public IReadOnlyList<bool> ModeAimsAtChosenEnemy => new[] { true, false };
    }

    private sealed class NotModal
    {
        public string Title => "Strike";
    }

    private sealed class HalfRead
    {
        public IReadOnlyList<string> ModeLabels => new[] { "A", "B" };

        public IReadOnlyList<bool> ModeAimsAtChosenEnemy => new[] { true };
    }

    private sealed class TwoBlocks
    {
        public IReadOnlyList<string> ModeLabels =>
            new[] { "Gain 3 Block", "Gain 3 Block and draw a card" };

        public IReadOnlyList<bool> ModeAimsAtChosenEnemy => new[] { false, false };
    }

    [Fact]
    public void TheBlockModeThatWasRefusedAimsAtNobody()
    {
        var modes = GitsModalTargeting.Modes(new ThomaLike());
        Assert.NotNull(modes);
        Assert.Equal(2, modes!.Count);
        int index = GitsModalTargeting.Match(modes, "Gain 3 Block, applying no element");
        Assert.Equal(1, index);
        Assert.False(modes[index].Aims);
    }

    [Fact]
    public void TheDamageModeOfTheSameCardStillAims()
    {
        var modes = GitsModalTargeting.Modes(new ThomaLike())!;
        int index = GitsModalTargeting.Match(modes, "Deal 8 damage, applying its element");
        Assert.Equal(0, index);
        Assert.True(modes[index].Aims);
    }

    [Fact]
    public void AFormMayNameTheModeShortOfItsWholePrintedLabel()
    {
        var modes = GitsModalTargeting.Modes(new ThomaLike())!;
        Assert.Equal(1, GitsModalTargeting.Match(modes, "Gain 3 Block"));
        Assert.Equal(0, GitsModalTargeting.Match(modes, "deal 8 damage"));
    }

    [Fact]
    public void AnAmbiguousNameIsReportedAndNeverGuessedAt()
    {
        var modes = GitsModalTargeting.Modes(new TwoBlocks())!;
        Assert.Equal(GitsModalTargeting.Ambiguous,
                     GitsModalTargeting.Match(modes, "Gain 3"));
        // An EXACT label still wins over being a substring of its neighbour:
        // a form that wrote the whole printed line named one mode, and the
        // longer sibling does not make that ambiguous.
        Assert.Equal(0, GitsModalTargeting.Match(modes, "Gain 3 Block"));
        Assert.Equal(GitsModalTargeting.NoMode,
                     GitsModalTargeting.Match(modes, "Deal 8 damage"));
        Assert.Equal(GitsModalTargeting.NoMode,
                     GitsModalTargeting.Match(modes, "   "));
    }

    [Fact]
    public void ACardThatIsNotModalAnswersNothingAndKeepsTheOldRule()
    {
        Assert.Null(GitsModalTargeting.Modes(new NotModal()));
        Assert.Null(GitsModalTargeting.Modes(null));
    }

    [Fact]
    public void ACardWhoseTwoRowsDisagreeIsNotHalfRead()
    {
        // A half-read card is not a licence to skip a refusal: no modes means
        // the card-type rule stands, which is the strict direction.
        Assert.Null(GitsModalTargeting.Modes(new HalfRead()));
    }

    [Fact]
    public void TheLabelsAreListedForARefusalToPrint()
    {
        var modes = GitsModalTargeting.Modes(new ThomaLike())!;
        Assert.Equal("'Deal 8 damage, applying its element' | "
                   + "'Gain 3 Block, applying no element'",
                     GitsModalTargeting.Labels(modes));
    }
}
