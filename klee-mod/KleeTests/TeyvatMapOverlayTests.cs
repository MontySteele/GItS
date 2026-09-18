using System;
using System.Linq;
using System.Reflection;
using KleeMod.Teyvat;
using KleeMod.Teyvat.Patches;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// THE MAP OVERLAY, AND THE MAP GROUND IT GAVE BACK (2026-09-17).
///
/// [USER], on the shipped frame: *"the map is harder to read than the normal
/// Slay the Spire 2 map; I like the basic idea but perhaps we went off the
/// rails replacing the map background with Genshin images and we should instead
/// try to come up with a Genshin-themed map overlay that keeps the basic idea
/// of the map intact."* Two things came out of that and both are pinned here.
///
/// WHAT A HEADLESS SUITE CAN SAY ABOUT A GODOT NODE: nothing, and the design
/// is shaped so that it does not have to. `KleeTests` may not CALL GodotSharp
/// (`README.md`, the headless boundary), so `MapOverlay.Attach` cannot be run
/// at all. Everything it DECIDES before it touches the tree is therefore a
/// pure function over strings and tables -- `ShouldAttach`, `Tints`,
/// `WordmarkPath`, `VignettePath`, `ActMapBgPath.BaseZonePath` -- and those are
/// exercised directly, with the arm moved both ways in one build.
///
/// The one thing left that a value cannot answer -- "a missing node adds
/// nothing and throws nothing" -- is pinned STRUCTURALLY through
/// <see cref="Il"/>, by reading which node accessor the resolver calls. That is
/// labelled as a structural pin wherever it is used and it cannot see a
/// reordering inside a method; what it CAN see is `GetNode` where
/// `GetNodeOrNull` belongs, which is the whole failure mode, because the names
/// this overlay looks for are a guess about a tree nobody has decompiled.
/// </summary>
public class TeyvatMapOverlayTests : IDisposable
{
    private readonly bool _enabled = TeyvatFrame.Enabled;

    public void Dispose() => TeyvatFrame.Enabled = _enabled;

    // ----------------------------------------------------------------------
    // the gate
    // ----------------------------------------------------------------------

    [Fact]
    public void ArmOffAddsNothingOnAnyFace()
    {
        TeyvatFrame.Enabled = false;
        foreach (var entry in TeyvatFrame.AssetAlias.Keys)
        {
            Assert.False(MapOverlay.ShouldAttach(entry), entry);
        }
    }

    [Fact]
    public void ArmOnDressesEveryFace()
    {
        TeyvatFrame.Enabled = true;
        foreach (var entry in TeyvatFrame.AssetAlias.Keys)
        {
            Assert.True(MapOverlay.ShouldAttach(entry), entry);
        }
    }

    /// <summary>
    /// A BASE ZONE REACHED WITH THE ARM ON DRESSES NOTHING. The act list is
    /// rolled per run and a run can stand in Overgrowth with the flag up; an
    /// overlay there would put Mondstadt's emblem over the base game's map.
    /// </summary>
    [Theory]
    [InlineData("OVERGROWTH")]
    [InlineData("UNDERDOCKS")]
    [InlineData("HIVE")]
    [InlineData("GLORY")]
    [InlineData("")]
    public void ArmOnLeavesABaseZoneAlone(string entry)
    {
        TeyvatFrame.Enabled = true;
        Assert.False(MapOverlay.ShouldAttach(entry));
    }

    [Fact]
    public void NoActIsNotAFace()
    {
        TeyvatFrame.Enabled = true;
        Assert.False(MapOverlay.ShouldAttach(null));
    }

    // ----------------------------------------------------------------------
    // the tint table
    // ----------------------------------------------------------------------

    /// <summary>
    /// THE TABLE IS THE DRESSING REGISTRY, exactly. A seventh face added to
    /// `TeyvatFrame.AssetAlias` without a tint would draw an overlay with no
    /// colour grade -- or, worse, throw out of the `Tints[entry]` lookup inside
    /// a Harmony postfix on the map screen. `ShouldAttach` asks THIS table for
    /// that reason, so the two cannot be one row apart.
    /// </summary>
    [Fact]
    public void EveryFaceHasATintAndNoOneElseDoes()
    {
        Assert.Equal(
            TeyvatFrame.AssetAlias.Keys.OrderBy(k => k, StringComparer.Ordinal),
            MapOverlay.Tints.Keys.OrderBy(k => k, StringComparer.Ordinal));
    }

    /// <summary>
    /// Six digits of hex and nothing else. `Godot.Color`'s string constructor
    /// is lenient enough to accept a name or a `#`, and a typo that parses is
    /// a tint nobody picked.
    /// </summary>
    [Fact]
    public void EveryTintIsASixDigitHex()
    {
        foreach (var (entry, hex) in MapOverlay.Tints)
        {
            Assert.Equal(6, hex.Length);
            Assert.True(hex.All(Uri.IsHexDigit), $"{entry}: {hex}");
            Assert.DoesNotContain("#", hex, StringComparison.Ordinal);
        }
    }

    /// <summary>
    /// Six DISTINCT hues: the grade is the only thing on the screen that says
    /// which nation this is once the ground stopped saying it, and two faces
    /// sharing a colour would make the two faces of one act indistinguishable
    /// (Natlan and Inazuma stand on the same zone, Fontaine and Sumeru on the
    /// same zone -- so they share the map ground exactly).
    /// </summary>
    [Fact]
    public void NoTwoFacesShareATint()
    {
        Assert.Equal(MapOverlay.Tints.Count,
                     MapOverlay.Tints.Values.Distinct(StringComparer.OrdinalIgnoreCase).Count());
    }

    /// <summary>
    /// FAINT IS THE SPEC. The whole point of the overlay over the plates is
    /// that the map stays readable, and a grade above ~15% starts taking the
    /// contrast back off the node icons -- which is the defect, not the fix.
    /// </summary>
    [Fact]
    public void TheGradeStaysInTheFaintBand()
    {
        Assert.InRange(MapOverlay.TintAlpha, 0.10f, 0.15f);
    }

    // ----------------------------------------------------------------------
    // the paths
    // ----------------------------------------------------------------------

    [Fact]
    public void EachFaceNamesItsOwnTwoPictures()
    {
        foreach (var entry in TeyvatFrame.AssetAlias.Keys)
        {
            var id = entry.ToLowerInvariant();
            Assert.Equal($"res://teyvat/map/{id}_wordmark.png", MapOverlay.WordmarkPath(entry));
            Assert.Equal($"res://teyvat/map/{id}_vignette.png", MapOverlay.VignettePath(entry));
        }
    }

    // ----------------------------------------------------------------------
    // a missing node adds nothing (structural pin)
    // ----------------------------------------------------------------------

    /// <summary>
    /// STRUCTURAL PIN. `MapOverlay.ParentCandidates` is a GUESS about a tree
    /// this repo has no decompile of, so every one of those names may be
    /// absent. `GetNode` throws on a miss and this code runs inside a Harmony
    /// postfix on the map screen's own open, where a throw takes the map screen
    /// -- and the run -- with it. `GetNodeOrNull` is the only accessor allowed
    /// in here, and that is what this reads.
    /// </summary>
    [Fact]
    public void TheParentResolverNeverThrowsOnAMissingNode()
    {
        var resolve = typeof(MapOverlay).GetMethod(
            "ResolveParent", BindingFlags.NonPublic | BindingFlags.Static);
        Assert.NotNull(resolve);

        var calls = Il.Calls(resolve!);
        Assert.Contains(calls, c => c.EndsWith(".GetNodeOrNull", StringComparison.Ordinal));
        Assert.DoesNotContain(calls, c => c.EndsWith(".GetNode", StringComparison.Ordinal));
    }

    /// <summary>
    /// STRUCTURAL PIN, the other half: the entry point asks the gate. An
    /// `Attach` that built the overlay first and checked the flag afterwards
    /// would pass every value test above and still put a node on the base
    /// game's map screen.
    /// </summary>
    [Fact]
    public void AttachAsksTheGate()
    {
        var attach = typeof(MapOverlay).GetMethod(
            nameof(MapOverlay.Attach), BindingFlags.Public | BindingFlags.Static);
        Assert.NotNull(attach);

        var calls = Il.Calls(attach!);
        Assert.Contains(calls, c => c.EndsWith(".ShouldAttach", StringComparison.Ordinal));
    }

    // ----------------------------------------------------------------------
    // the map ground goes back to the base zone
    // ----------------------------------------------------------------------

    /// <summary>
    /// THE REVERT, as the one string operation it is. Every face's ground path
    /// carries its own id twice -- once as the directory, once in the file name
    /// -- and replacing the id with the base zone's produces the base zone's
    /// path whatever the prefix and extension around it are.
    /// </summary>
    [Fact]
    public void EveryFaceSGroundIsSentToItsBaseZone()
    {
        TeyvatFrame.Enabled = true;
        foreach (var (entry, zone) in TeyvatFrame.AssetAlias)
        {
            var id = entry.ToLowerInvariant();
            var dressed = $"res://images/packed/map/map_bgs/{id}/map_top_{id}.png";
            Assert.Equal(
                $"res://images/packed/map/map_bgs/{zone}/map_top_{zone}.png",
                ActMapBgPath.BaseZonePath(entry, dressed));
        }
    }

    [Fact]
    public void ArmOffLeavesTheGroundPathAlone()
    {
        TeyvatFrame.Enabled = false;
        Assert.Null(ActMapBgPath.BaseZonePath(
            TeyvatFrame.Mondstadt,
            "res://images/packed/map/map_bgs/mondstadt/map_top_mondstadt.png"));
    }

    [Fact]
    public void ABaseZoneSGroundPathIsNotRewritten()
    {
        TeyvatFrame.Enabled = true;
        Assert.Null(ActMapBgPath.BaseZonePath(
            "OVERGROWTH",
            "res://images/packed/map/map_bgs/overgrowth/map_top_overgrowth.png"));
    }

    /// <summary>
    /// A PATH THAT DOES NOT CARRY THE ID IS LEFT ALONE, never guessed at. That
    /// is the shape a game patch moving the path format arrives in, and the
    /// right answer to it is the base game's own behaviour rather than a
    /// fabricated path that resolves to nothing.
    /// </summary>
    [Fact]
    public void AnUnrecognisedPathIsLeftAlone()
    {
        TeyvatFrame.Enabled = true;
        Assert.Null(ActMapBgPath.BaseZonePath(
            TeyvatFrame.Mondstadt, "res://images/packed/map/somewhere_else.png"));
        Assert.Null(ActMapBgPath.BaseZonePath(TeyvatFrame.Mondstadt, null));
    }
}
