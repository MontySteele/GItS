#nullable enable

using System;
using STS2_MCP;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// EB-748. THE SENTENCE A REFUSAL PUTS ON THE PAGE, PINNED HEADLESSLY.
///
/// A card refused by a power reached the blind page as the bare enum
/// `BlockedByHook`, which `understudy/qa_packet.UNPLAYABLE_REASONS` renders as
/// "something else on the board is stopping you right now"; two seats flagged
/// it and one GUESSED the cause off `Smoggy 1` in the status list. The bridge
/// now reads `CardModel.CanPlay`'s SECOND out parameter -- what refused -- and
/// `vendor/STS2_MCP/gits/GitsRefusalSource.cs` turns that object into the
/// sentence. That file is deliberately free of Godot, Harmony and game types,
/// so this assembly compiles THAT source (not a fork of it), exactly as
/// `GitsPortPrecedenceTests` and `GitsSkipActTests` do for their own decisions.
///
/// WHAT THESE PINS ARE FOR. The reader is REFLECTION over an object whose
/// static type the bridge does not name, so the two failure directions are
/// both silent in a live game: a preventer whose name it cannot read would
/// print nothing (and look like the old defect), and a slot holding something
/// that is not a preventer at all would print "True is stopping you right
/// now". Neither shows up in a compile and neither is cheap to reach with a
/// run up. They are decided here instead.
/// </summary>
public class GitsRefusalSourceTests
{
    // Stand-ins for the game's own models. Only their SHAPE matters: the
    // reader asks by property name and falls back to the type name.
    private sealed class SmoggyPower
    {
        public string Title => "Smoggy";
    }

    private sealed class NamelessPower
    {
    }

    private sealed class TheBoundHeartModel
    {
    }

    private sealed class DisplayNamedPower
    {
        public string DisplayName => "The Stage";
    }

    private sealed class PlainlyNamedPower
    {
        public string Name => "Confused";
    }

    private sealed class BlankTitlePower
    {
        public string Title => "   ";
    }

    private sealed class ThrowingTitlePower
    {
        public string Title => throw new InvalidOperationException("no");
    }

    private sealed class IndexedPower
    {
        public string this[int i] => "not a name";

        public string Name => "Indexed";
    }

    private enum SomeEnum
    {
        BlockedByHook
    }

    // ------------------------------------------------------ nothing to say

    [Fact]
    public void NoPreventerSaysNothing()
    {
        Assert.Null(McpMod.GitsRefusalSource(null));
    }

    [Theory]
    [InlineData(true)]
    [InlineData(3)]
    [InlineData("BlockedByHook")]
    public void APrimitiveInTheSlotSaysNothing(object value)
    {
        // The second out parameter is not what this file hopes it is. Saying
        // nothing keeps the wire key absent and the page exactly as it was;
        // the alternative is "True is stopping you right now".
        Assert.Null(McpMod.GitsRefusalSource(value));
    }

    [Fact]
    public void AnEnumInTheSlotSaysNothing()
    {
        Assert.Null(McpMod.GitsRefusalSource(SomeEnum.BlockedByHook));
    }

    // --------------------------------------------------- the printed names

    [Fact]
    public void ATitleIsTheNamePrinted()
    {
        Assert.Equal("Smoggy is stopping you right now",
                     McpMod.GitsRefusalSource(new SmoggyPower()));
    }

    [Fact]
    public void ADisplayNameIsReadWhereThereIsNoTitle()
    {
        Assert.Equal("The Stage is stopping you right now",
                     McpMod.GitsRefusalSource(new DisplayNamedPower()));
    }

    [Fact]
    public void APlainNameIsReadWhereThereIsNeither()
    {
        Assert.Equal("Confused is stopping you right now",
                     McpMod.GitsRefusalSource(new PlainlyNamedPower()));
    }

    // ------------------------------------------- the type-name fallback

    [Fact]
    public void AModelWithNoNameFallsBackToItsTypeNameWithoutTheSuffix()
    {
        Assert.Equal("Nameless is stopping you right now",
                     McpMod.GitsRefusalSource(new NamelessPower()));
    }

    [Fact]
    public void ATypeNameIsSeparatedIntoWords()
    {
        Assert.Equal("The Bound Heart is stopping you right now",
                     McpMod.GitsRefusalSource(new TheBoundHeartModel()));
    }

    [Fact]
    public void ABlankTitleIsNotAName()
    {
        Assert.Equal("Blank Title is stopping you right now",
                     McpMod.GitsRefusalSource(new BlankTitlePower()));
    }

    [Fact]
    public void APropertyThatThrowsOnReadIsNotAName()
    {
        // A state read must never throw. The type name is what is left.
        Assert.Equal("Throwing Title is stopping you right now",
                     McpMod.GitsRefusalSource(new ThrowingTitlePower()));
    }

    [Fact]
    public void AnIndexerIsNotAName()
    {
        Assert.Equal("Indexed is stopping you right now",
                     McpMod.GitsRefusalSource(new IndexedPower()));
    }
}
