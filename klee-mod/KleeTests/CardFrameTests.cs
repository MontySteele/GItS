using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using BaseLib.Abstracts;
using BaseLib.Utils.Attributes;
using KleeMod.Cards;
using KleeMod.Vfx;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// CARD FRAMES STAGE 1, pinned (2026-10-19). [USER]: "we need a quick way of
/// distinguishing the character cards".
///
/// Painting is not reachable here (Godot nodes are process death in this
/// host); what is reachable is everything the paint reads: each kit pool's
/// tint, that the pools are the BaseLib type the HSV material patch serves,
/// that their ids and members did not move, and which nation each companion
/// face declares.
/// </summary>
public class CardFrameTests
{
    // Allocated, not constructed (the CompanionCardPoolTests idiom).
    private static CardPoolModel Pool(Type t) =>
        (CardPoolModel)System.Runtime.CompilerServices.RuntimeHelpers
            .GetUninitializedObject(t);

    public static IEnumerable<object[]> Kits() => new[]
    {
        new object[] { typeof(KleeCardPool), "klee" },
        new object[] { typeof(FurinaCardPool), "furina" },
        new object[] { typeof(KokomiCardPool), "kokomi" },
        new object[] { typeof(VarkaCardPool), "varka" },
        new object[] { typeof(YaeCardPool), "yae" },
    };

    [Theory]
    [MemberData(nameof(Kits))]
    public void Each_kit_pool_reports_its_own_tint(Type type, string kit)
    {
        var pool = (KitCardPool)Pool(type);
        var row = CardFrameColors.All.Single(t => t.Kit == kit);
        Assert.Equal(row, pool.Tint);
        Assert.Equal(row.H, pool.H);
        Assert.Equal(row.S, pool.S);
        Assert.Equal(row.V, pool.V);
        Assert.Equal(row.DeckEntry, pool.DeckEntryCardColor);
        Assert.Equal(row.EnergyOutline, pool.EnergyOutlineColor);
        // BaseLib's CustomCardPoolMaterialPatch builds the HSV material only
        // for its own pool type and only on this path; any other path hands
        // back the base material untinted.
        Assert.IsAssignableFrom<CustomCardPoolModel>(pool);
        Assert.Equal("card_frame_red", pool.CardFrameMaterialPath);
        Assert.False(((CustomCardPoolModel)pool).IsShared);
        Assert.False(pool.IsColorless);
    }

    /// <summary>The base game's own frame materials (SlayTheSpire2.pck,
    /// materials/cards/frames/*_mat.tres, read 2026-10-19).</summary>
    private static readonly (string Name, float H, float S, float V)[] BaseFrames =
    {
        ("ironclad", 0.025f, 0.85f, 1.0f),
        ("regent", 0.12f, 1.5f, 1.2f),
        ("silent", 0.32f, 0.45f, 1.2f),
        ("defect", 0.55f, 0.9f, 1.0f),
        ("necrobinder", 0.965f, 0.55f, 1.2f),
        ("colorless", 1.0f, 0.0f, 1.2f),
    };

    /// <summary>The point of the change: no kit wears a base character's
    /// frame or another kit's. Two frames read apart when their hue rotations
    /// differ by 0.03 of a turn or their saturations by 0.3 (Kokomi's pearl
    /// sits on the Ironclad's hue at less than half its saturation).</summary>
    [Fact]
    public void No_two_frames_share_a_look()
    {
        var all = BaseFrames
            .Concat(CardFrameColors.All.Select(t => (Name: t.Kit, t.H, t.S, t.V)))
            .ToArray();
        Assert.Equal(5, CardFrameColors.All.Length);
        for (var i = 0; i < all.Length; i++)
        {
            for (var j = i + 1; j < all.Length; j++)
            {
                var a = all[i];
                var b = all[j];
                var dh = Math.Abs(a.H - b.H) % 1f;
                dh = Math.Min(dh, 1f - dh);
                var ds = Math.Abs(a.S - b.S);
                Assert.True(dh >= 0.03f || ds >= 0.3f,
                    $"{a.Name} and {b.Name} frames are too close (dh {dh}, ds {ds})");
            }
        }
    }

    /// <summary>A CustomCardPoolModel is an ICustomModel, which BaseLib's
    /// PrefixIdPatch would re-key with a namespace prefix. Each pool pins the
    /// entry the game gave it as a plain CardPoolModel
    /// (<c>ModelDb.GetEntry</c> = <c>StringHelper.Slugify(type.Name)</c>).</summary>
    [Theory]
    [MemberData(nameof(Kits))]
    public void Each_kit_pool_keeps_its_model_id(Type type, string kit)
    {
        _ = kit;
        var id = type.GetCustomAttribute<CustomIDAttribute>(inherit: false);
        Assert.NotNull(id);
        Assert.Equal(StringHelper.Slugify(type.Name), id!.ID);
        Assert.Equal(ModelDb.GetEntry(type), id.ID);
    }

    /// <summary>Membership and offer did not move. CustomCardPoolModel's own
    /// GenerateAllCards returns an EMPTY array, so a pool that inherited it
    /// instead of declaring its own would lose every card (and every card in
    /// it would throw "You monster!" on draw). Each pool still declares both
    /// doors itself; the bodies are unchanged in this commit, and the members
    /// themselves are `tools/lint_pool_membership.py`'s (ModelDb, which they
    /// resolve through, is not populated in this host).</summary>
    [Theory]
    [MemberData(nameof(Kits))]
    public void Each_kit_pool_still_declares_its_own_members_and_offer(Type type, string kit)
    {
        _ = kit;
        const BindingFlags own = BindingFlags.Instance | BindingFlags.NonPublic
            | BindingFlags.DeclaredOnly;
        Assert.NotNull(type.GetMethod("GenerateAllCards", own));
        Assert.NotNull(type.GetMethod("FilterThroughEpochs", own));
        Assert.Equal(typeof(KitCardPool), type.BaseType);
    }

    // ---- the nation pip ---------------------------------------------------

    [Fact]
    public void Every_declared_nation_has_a_pip()
    {
        var nations = typeof(ICompanionCard).Assembly.GetTypes()
            .Where(t => typeof(ICompanionCard).IsAssignableFrom(t)
                        && typeof(CardModel).IsAssignableFrom(t)
                        && !t.IsAbstract)
            .Select(t => NationEmblem.NationOf(
                (CardModel)System.Runtime.CompilerServices.RuntimeHelpers
                    .GetUninitializedObject(t)))
            .Where(n => n != null)
            .Distinct()
            .ToArray();
        Assert.NotEmpty(nations);
        foreach (var nation in nations)
        {
            Assert.NotNull(NationEmblem.StyleFor(nation));
        }
    }

    [Theory]
    [InlineData("mondstadt", "M")]
    [InlineData("liyue", "L")]
    [InlineData("inazuma", "I")]
    [InlineData("fontaine", "F")]
    public void Each_nation_has_its_initial_and_its_own_colour(string nation, string initial)
    {
        var style = NationEmblem.StyleFor(nation);
        Assert.NotNull(style);
        Assert.Equal(initial, style!.Value.Initial);
        var others = new[] { "mondstadt", "liyue", "inazuma", "fontaine" }
            .Where(n => n != nation)
            .Select(n => NationEmblem.StyleFor(n)!.Value.Fill);
        Assert.DoesNotContain(style.Value.Fill, others);
    }

    [Fact]
    public void A_card_with_no_nation_draws_no_pip()
    {
        Assert.Null(NationEmblem.StyleFor(null));
        Assert.Null(NationEmblem.StyleFor("snezhnaya"));
        Assert.Null(NationEmblem.NationOf(null));
    }

    [Theory]
    [InlineData("ProtoMcAmberFieryRain", "mondstadt")]
    [InlineData("ProtoMiAyakaHyouka", "inazuma")]
    [InlineData("ProtoMfCharlotteEnduringFrosthelm", "fontaine")]
    public void The_pip_reads_the_companion_sheet_nation(string typeName, string nation)
    {
        var type = typeof(ICompanionCard).Assembly.GetTypes()
            .Single(t => t.Name == typeName);
        var card = (CardModel)System.Runtime.CompilerServices.RuntimeHelpers
            .GetUninitializedObject(type);
        Assert.Equal(nation, NationEmblem.NationOf(card));
    }
}
