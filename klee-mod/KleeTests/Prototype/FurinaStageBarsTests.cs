using System;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.Rooms;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA, THE STAGE -- THE BARS AND THE LINE (2026-09-26 smoke, 0.2.3839).
///
/// THE FIND. Two Ushers on the stage, cues drawn over both, and NO Fanfare
/// bar under either; the lone Usher of the first frame stood on Furina's
/// legs. Both are the base game's pet layout, read off the 0.111.0
/// decompile: <c>NCombatRoom.AddCreature</c> hides every non-Osty pet's bar
/// (<c>ToggleIsInteractable(false)</c> writes <c>_stateDisplay.Visible</c>),
/// and starts its line at <c>owner.X - 20</c>, inside the owner's box.
///
/// Pinned headlessly where the answer is a value (the model's bar flag, the
/// line's arithmetic) and structurally where it needs a scene tree (the
/// postfix, the write to the bar). No combat room exists in `dotnet test`.
/// </summary>
public class FurinaStageBarsTests
{
    private static StagePerformerMonster Model(StagePerformer who)
    {
        var type = (Type)typeof(FurinaStagePets)
            .GetMethod("ModelFor", HeadlessGame.All)!
            .Invoke(null, new object[] { who })!;
        return (StagePerformerMonster)Activator.CreateInstance(type,
                                                               nonPublic: true)!;
    }

    // ---- no bar (the re-founding, 2026-10-04) ------------------------------

    [Fact]
    public void No_performer_model_shows_a_bar()
    {
        // Rule 1: "performers with no bars". Every member of the cast and
        // every guest is a pet with its bar hidden, the Bake-Kurage's shape,
        // and the postfix that put the bars back is gone.
        foreach (var who in Enum.GetValues<StagePerformer>())
        {
            var model = Model(who);
            Assert.False(model.IsHealthBarVisible, $"{who} shows a bar");
            Assert.Equal(who, model.Performer);
        }
        Assert.DoesNotContain(typeof(FurinaStagePlacement).Assembly.GetTypes(),
            t => t.Name == "NCombatRoom_AddCreature_StageBars_Patch");
    }

    // ---- the line: clear of her ---------------------------------------------

    /// <summary>Furina's own box, `furina/model/combat.tscn`'s Bounds: 240.
    /// </summary>
    private const float FurinaHalf = 120f;

    [Theory]
    [InlineData(new float[] { 121f })]                    // the lone Usher
    [InlineData(new float[] { 121f, 121f })]              // two Ushers
    [InlineData(new float[] { 121f, 129f, 120f })]        // the trio
    [InlineData(new float[] { 96f, 84f, 80f })]           // three guests
    public void No_performer_stands_on_her(float[] widths)
    {
        const float ownerX = -550f;
        var centres = FurinaStagePlacement.LineCentres(ownerX, FurinaHalf, widths);

        Assert.Equal(widths.Length, centres.Length);
        var herEdge = ownerX + FurinaHalf;
        // The back body's left edge is a floor gap clear of her box.
        Assert.Equal(herEdge + FurinaStagePlacement.Gap,
                     centres[0] - widths[0] * 0.5f, 3);
        for (var i = 1; i < widths.Length; i++)
        {
            var leftEdge = centres[i] - widths[i] * 0.5f;
            var priorRight = centres[i - 1] + widths[i - 1] * 0.5f;
            // No two bodies overlap, and the front is the right-most.
            Assert.Equal(priorRight + FurinaStagePlacement.Gap, leftEdge, 3);
            Assert.True(centres[i] > centres[i - 1]);
        }
    }

    [Fact]
    public void The_smoke_frame_no_longer_overlaps()
    {
        // The engine's old slot 0 for a lone Usher: owner.X - 20 + 60.5, a
        // centre 40.5 right of hers and a left edge 20 LEFT of it -- inside
        // her 240 box. The new line puts that left edge past her right one.
        var centre = FurinaStagePlacement.LineCentres(0f, FurinaHalf,
                                                      new[] { 121f })[0];
        Assert.True(centre - 60.5f >= FurinaHalf, $"left edge {centre - 60.5f}");
    }
}
