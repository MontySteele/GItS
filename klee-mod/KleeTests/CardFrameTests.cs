using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using BaseLib.Abstracts;
using BaseLib.Utils.Attributes;
using Godot;
using HarmonyLib;
using KleeMod.Cards;
using KleeMod.Vfx;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.CardPools;
using MegaCrit.Sts2.Core.Models.Cards;
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
    /// frame or another kit's, and (stage 2) no companion nation's tint side
    /// wears either of those or another nation's. Two frames read apart when
    /// their hue rotations differ by 0.03 of a turn or their saturations by
    /// 0.3 (Kokomi's pearl sits on the Ironclad's hue at less than half its
    /// saturation; Fontaine's steel blue sits in Furina's hue family at a third
    /// of her chroma). The 1e-4 slack is float spelling, not tolerance: 0.66f
    /// minus 0.63f is 0.0299999 in single precision.</summary>
    [Fact]
    public void No_two_frames_share_a_look()
    {
        var all = BaseFrames
            .Concat(CardFrameColors.All.Select(t => (Name: t.Kit, t.H, t.S, t.V)))
            .Concat(CardFrameColors.Nations.Select(n => (Name: n.Nation, n.H, n.S, n.V)))
            .ToArray();
        Assert.Equal(5, CardFrameColors.All.Length);
        Assert.Equal(3, CardFrameColors.Nations.Length);
        for (var i = 0; i < all.Length; i++)
        {
            for (var j = i + 1; j < all.Length; j++)
            {
                var a = all[i];
                var b = all[j];
                var dh = Math.Abs(a.H - b.H) % 1f;
                dh = Math.Min(dh, 1f - dh);
                var ds = Math.Abs(a.S - b.S);
                Assert.True(dh >= 0.03f - 1e-4f || ds >= 0.3f - 1e-4f,
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

    // ---- borrowed basics wear the kit's frame (2026-10-20) -----------------
    // [USER]: "All of the Strikes and Defends in Kokomi's deck still have the
    // Silent's green border."

    /// <summary>The patch target resolves on the real CardModel, the base
    /// getter the frame, tiny card and orb read, and the patch class names it.</summary>
    [Fact]
    public void The_kit_basics_patch_targets_the_base_VisualCardPool_getter()
    {
        var getter = AccessTools.PropertyGetter(typeof(CardModel), "VisualCardPool");
        Assert.NotNull(getter);
        Assert.Equal(typeof(CardModel), getter!.DeclaringType);
        Assert.Equal(typeof(CardPoolModel), getter.ReturnType);
        Assert.True(getter.IsVirtual);

        var patch = typeof(KitCardPool).Assembly.GetType(
            "KleeMod.CardModel_VisualCardPool_KitBasics_Patch");
        Assert.NotNull(patch);
        var info = patch!.GetCustomAttribute<HarmonyPatch>()!.info;
        Assert.Equal(typeof(CardModel), info.declaringType);
        Assert.Equal("get_VisualCardPool", info.methodName);
        Assert.NotNull(patch.GetMethod("Postfix",
            BindingFlags.Static | BindingFlags.NonPublic));
    }

    /// <summary>The base Strike and Defend the kits start on do not override
    /// VisualCardPool, so the patched base body is the one they run.</summary>
    [Theory]
    [InlineData(typeof(StrikeSilent))]
    [InlineData(typeof(DefendSilent))]
    [InlineData(typeof(StrikeIronclad))]
    [InlineData(typeof(DefendIronclad))]
    [InlineData(typeof(StrikeDefect))]
    [InlineData(typeof(DefendDefect))]
    public void The_borrowed_starters_run_the_base_getter(Type card)
    {
        var getter = card.GetProperty("VisualCardPool")!.GetGetMethod()!;
        Assert.Equal(typeof(CardModel), getter.GetBaseDefinition().DeclaringType);
        Assert.Equal(typeof(CardModel), getter.DeclaringType);
    }

    [Theory]
    [MemberData(nameof(Kits))]
    public void A_borrowed_basic_takes_its_owners_kit_pool(Type type, string kit)
    {
        _ = kit;
        var basePool = Pool(typeof(SilentCardPool));
        var kitPool = Pool(type);
        Assert.Same(kitPool, BorrowedBasicFrame.PoolFor(CardRarity.Basic, basePool, kitPool));
    }

    [Fact]
    public void Everything_else_keeps_its_own_frame()
    {
        var silent = Pool(typeof(SilentCardPool));
        var ironclad = Pool(typeof(IroncladCardPool));
        var kokomi = Pool(typeof(KokomiCardPool));
        var klee = Pool(typeof(KleeCardPool));

        // Not Basic: a drafted base card keeps its colour.
        foreach (var rarity in Enum.GetValues<CardRarity>().Where(r => r != CardRarity.Basic))
        {
            Assert.Same(silent, BorrowedBasicFrame.PoolFor(rarity, silent, kokomi));
        }
        // No owner (library, compendium): base colour.
        Assert.Same(silent, BorrowedBasicFrame.PoolFor(CardRarity.Basic, silent, null));
        // Owner plays a base character: base colour (a Silent's own Strike).
        Assert.Same(silent, BorrowedBasicFrame.PoolFor(CardRarity.Basic, silent, silent));
        Assert.Same(silent, BorrowedBasicFrame.PoolFor(CardRarity.Basic, silent, ironclad));
        // A kit's own Basic already wears its kit pool, even in another kit's deck.
        Assert.Same(klee, BorrowedBasicFrame.PoolFor(CardRarity.Basic, klee, kokomi));
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

    // ---- stage 2 (2026-10-20): split companion frames, kit orbs -----------
    // [USER]: "Agreed on all of the card / orb / energy mockup picks,
    // including Kokomi's (b)".

    [Theory]
    [InlineData("mondstadt", 0.52f, 0.45f, 1.45f)]
    [InlineData("inazuma", 0.77f, 1.0f, 1.15f)]
    [InlineData("fontaine", 0.66f, 0.40f, 1.45f)]
    public void Each_companion_nation_has_its_ruled_tint(string nation, float h, float s, float v)
    {
        var tint = CardFrameColors.NationFor(nation);
        Assert.NotNull(tint);
        Assert.Equal((h, s, v), (tint!.Value.H, tint.Value.S, tint.Value.V));
    }

    [Fact]
    public void Every_shared_companion_nation_splits_and_no_other_does()
    {
        // Every nation a companion declares has a pip; the three with shared
        // companions also have a split tint. Liyue (no companion yet) and
        // unknown nations keep plain Colorless.
        foreach (var n in new[] { "mondstadt", "inazuma", "fontaine" })
        {
            Assert.NotNull(CardFrameColors.NationFor(n));
        }
        Assert.Null(CardFrameColors.NationFor("liyue"));
        Assert.Null(CardFrameColors.NationFor(null));
        Assert.Equal((1.0f, 0.0f, 1.2f),
            (CardFrameColors.ColorlessH, CardFrameColors.ColorlessS, CardFrameColors.ColorlessV));
        Assert.Equal((0.40f, 0.20f), (CardFrameColors.SplitStart, CardFrameColors.SplitWidth));
    }

    [Fact]
    public void Only_a_companion_drawn_in_the_companion_pool_splits()
    {
        var amber = (CardModel)System.Runtime.CompilerServices.RuntimeHelpers
            .GetUninitializedObject(typeof(ICompanionCard).Assembly.GetTypes()
                .Single(t => t.Name == "ProtoMcAmberFieryRain"));
        var companion = Pool(typeof(CompanionCardPool));
        var klee = Pool(typeof(KleeCardPool));
        Assert.Equal(CardFrameColors.Mondstadt, CompanionSplitFrame.TintFor(amber, companion));
        // Kit-own companions wear their kit's frame.
        Assert.Null(CompanionSplitFrame.TintFor(amber, klee));
        // A non-companion in the companion pool (none today) would not split.
        Assert.Null(CompanionSplitFrame.TintFor(new StrikeSilent(), companion));
        Assert.Null(CompanionSplitFrame.TintFor(null, companion));
    }

    /// <summary>The frame is an atlas region: the attack frame is
    /// Rect2(1320, 83, 598, 844) of ui_atlas_0 (read from the pck), so the
    /// shader's x has to be re-based on that span, not on 0..1.</summary>
    [Fact]
    public void The_split_is_measured_across_the_frames_atlas_region()
    {
        var uv = CompanionSplitFrame.UvRect(new Rect2(1320, 83, 598, 844), new Vector2(4096, 4096));
        Assert.Equal(1320f / 4096f, uv.X, 6);
        Assert.Equal(83f / 4096f, uv.Y, 6);
        Assert.Equal(598f / 4096f, uv.Z, 6);
        Assert.Equal(844f / 4096f, uv.W, 6);
        // A plain texture (the tiny card's back) is the whole rect, and a
        // degenerate atlas falls back to it rather than dividing by zero.
        Assert.Equal(CompanionSplitFrame.Whole, CompanionSplitFrame.UvRectOf(null));
        Assert.Equal(CompanionSplitFrame.Whole,
            CompanionSplitFrame.UvRect(new Rect2(0, 0, 10, 10), Vector2.Zero));
    }

    [Fact]
    public void The_split_patches_target_the_base_getters()
    {
        var getter = AccessTools.PropertyGetter(typeof(CardModel), "FrameMaterial");
        Assert.NotNull(getter);
        Assert.False(getter!.IsVirtual);
        var patch = typeof(KitCardPool).Assembly.GetType(
            "KleeMod.Vfx.CardModel_FrameMaterial_CompanionSplit_Patch");
        Assert.NotNull(patch);
        var info = patch!.GetCustomAttribute<HarmonyPatch>()!.info;
        Assert.Equal(typeof(CardModel), info.declaringType);
        Assert.Equal("get_FrameMaterial", info.methodName);
        Assert.NotNull(AccessTools.Field(typeof(MegaCrit.Sts2.Core.Nodes.Cards.NTinyCard), "_cardBack"));
        Assert.NotNull(AccessTools.Method(typeof(MegaCrit.Sts2.Core.Nodes.Cards.NTinyCard), "SetCard"));
        Assert.NotNull(AccessTools.Method(typeof(MegaCrit.Sts2.Core.Nodes.Cards.NTinyCard), "Set",
            new[] { typeof(CardPoolModel), typeof(CardType), typeof(CardRarity) }));
        // Harmony resolves every patch the way it will at boot.
        foreach (var t in new[] { "KleeMod.Vfx.NTinyCard_CompanionSplit_Patch",
                                  "KleeMod.NCard_EnergyOutline_VisualPool_Patch",
                                  "KleeMod.Vfx.CardModel_FrameMaterial_CompanionSplit_Patch" })
        {
            var patchType = typeof(KitCardPool).Assembly.GetType(t)!;
            var classInfo = patchType.GetCustomAttributes<HarmonyPatch>().Select(h => h.info).FirstOrDefault();
            var patchMethods = patchType.GetMethods(BindingFlags.Static | BindingFlags.NonPublic)
                .Where(m => m.Name is "Postfix" || m.GetCustomAttributes<HarmonyPatch>().Any())
                .ToArray();
            Assert.NotEmpty(patchMethods);
            foreach (var m in patchMethods)
            {
                var own = m.GetCustomAttributes<HarmonyPatch>().Select(h => h.info).FirstOrDefault();
                var declaring = own?.declaringType ?? classInfo!.declaringType;
                var name = own?.methodName ?? classInfo!.methodName;
                var args = own?.argumentTypes ?? classInfo?.argumentTypes;
                // AccessTools.Method throws on an ambiguous name, as Harmony
                // does at boot (NTinyCard.Set vs GodotObject.Set).
                Assert.NotNull(AccessTools.Method(declaring, name, args));
            }
        }
    }

    [Theory]
    [MemberData(nameof(Kits))]
    public void Each_kit_pool_serves_its_own_orbs_through_the_BaseLib_hook(Type type, string kit)
    {
        // No kit pool re-declares the energy name: a base name ("ironclad")
        // would bypass BaseLib's ICustomEnergyIconPool lookup entirely.
        var name = type.GetProperty(nameof(CardPoolModel.EnergyColorName))!.GetGetMethod()!;
        Assert.Equal(typeof(KitCardPool), name.DeclaringType);
        Assert.True(name.IsFinal);
        Assert.IsAssignableFrom<ICustomEnergyIconPool>(Pool(type));

        var tint = CardFrameColors.All.Single(t => t.Kit == kit);
        Assert.Equal($"{kit}/ui/energy_cost.png", tint.CostOrbPath);
        Assert.Equal($"{kit}/ui/energy_text_icon.png", tint.TextIconPath);
        Assert.Equal($"{kit}/ui/energy_counter.tscn", tint.EnergyCounterPath);
        Assert.Equal($"res://images/atlases/ui_atlas.sprites/card/energy_{tint.BorrowedEnergy}.tres",
            KitEnergyIcon.BaseCostOrb(tint.BorrowedEnergy));
        Assert.Equal($"res://images/packed/sprite_fonts/{tint.BorrowedEnergy}_energy_icon.png",
            KitEnergyIcon.BaseTextIcon(tint.BorrowedEnergy));
    }

    [Fact]
    public void The_cost_outline_follows_the_drawn_pool_only_when_it_is_the_default()
    {
        var silent = new Godot.Color("1A6625");
        var kokomi = CardFrameColors.Kokomi.EnergyOutline;
        var green = new Godot.Color("00FF00");
        var outlineFor = typeof(KitCardPool).Assembly
            .GetType("KleeMod.NCard_EnergyOutline_VisualPool_Patch")!
            .GetMethod("OutlineFor", BindingFlags.Static | BindingFlags.NonPublic)!;
        Godot.Color? Call(Godot.Color cur, Godot.Color own, Godot.Color vis) =>
            (Godot.Color?)outlineFor.Invoke(null, new object[] { cur, own, vis });
        Assert.Equal(kokomi, Call(silent, silent, kokomi));
        Assert.Null(Call(green, silent, kokomi));      // an upgrade or a cost change
        Assert.Null(Call(silent, silent, silent));     // pools agree
    }
}
