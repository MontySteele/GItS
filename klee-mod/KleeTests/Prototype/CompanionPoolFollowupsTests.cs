using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Patches;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Factories;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.Screens.CardLibrary;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// The two follow-ups to the shared companions' own pool
/// (<see cref="CompanionCardPool"/>): a transform offers only companions the
/// player could be offered, and the card library's Colorless tab shows them.
/// </summary>
public class CompanionPoolFollowupsTests
{
    private static readonly BindingFlags All = HeadlessGame.All;

    // ==================================================================
    // A transform of a companion never offers Yae her hidden Sakura
    // ==================================================================

    [Fact]
    public void A_transform_never_offers_Yae_her_hidden_sakura()
    {
        var sakura = new ProtoMiYaeSesshouSakura();
        var ayaka = new ProtoMiAyakaHyouka();
        var strike = new ProtoYmSlyStrike();
        var options = new CardModel[] { sakura, ayaka, strike };

        var yae = CompanionTransformFilter.Filter(options, Seat.Yae().Player).ToList();
        Assert.DoesNotContain(sakura, yae);
        Assert.Contains(ayaka, yae);
        // A non-companion option is never touched.
        Assert.Contains(strike, yae);

        // Everyone else keeps the base answer, the same object.
        Assert.Same(options, CompanionTransformFilter.Filter(options, Seat.Klee().Player));
        Assert.Same(options, CompanionTransformFilter.Filter(options, Seat.Furina().Player));
    }

    [Fact]
    public void A_filter_that_would_leave_nothing_keeps_the_base_answer()
    {
        // The base method throws on an empty set; an empty set is not a
        // reachable roster, so the filter stands aside rather than crash.
        var options = new CardModel[] { new ProtoMiYaeSesshouSakura() };
        Assert.Same(options, CompanionTransformFilter.Filter(options, Seat.Yae().Player));
    }

    [Fact]
    public void The_transform_filter_is_a_postfix_on_the_base_options()
    {
        // STRUCTURAL. Harmony binds a postfix's arguments by NAME.
        var method = AccessTools.DeclaredMethod(
            typeof(CardFactory), "GetDefaultTransformationOptions");
        Assert.NotNull(method);
        Assert.Contains("original",
                        method!.GetParameters().Select(p => p.Name));

        var patch = typeof(CompanionTransformFilter).Assembly.GetTypes()
            .Single(t => t.Name == "CardFactory_CompanionTransformFilter_Patch");
        Assert.Contains(patch.GetCustomAttributes(inherit: true)
                            .OfType<HarmonyPatch>().Select(a => a.info),
                        i => i.declaringType == typeof(CardFactory)
                             && i.methodName == "GetDefaultTransformationOptions");
        var postfix = patch.GetMethod("Postfix", All)!;
        Assert.NotNull(postfix.GetCustomAttribute<HarmonyPostfix>());
        Assert.Equal(new[] { "original", "__result" },
                     postfix.GetParameters().Select(p => p.Name));
        Assert.Contains("CompanionTransformFilter.Filter", Il.Calls(postfix));
        Assert.Contains("CompanionPool.IsOfferable",
                        Il.Calls(typeof(CompanionTransformFilter).GetMethod("Filter")!)
                            .Concat(LambdaCalls(typeof(CompanionTransformFilter))));
    }

    // ==================================================================
    // The card library's Colorless tab shows the shared companions
    // ==================================================================

    [Fact]
    public void The_colorless_tab_is_widened_by_the_companion_pool_alone()
    {
        var shared = new ProtoMiAyakaHyouka();
        var other = new ProtoYmSlyStrike();
        Func<CardModel, bool> baseTab = _ => false;
        Func<CardModel, bool> companion = c => ReferenceEquals(c, shared);

        var widened = CompanionLibraryFilter.Widen(baseTab, companion);
        Assert.True(widened(shared));
        Assert.False(widened(other));
        // The base predicate still answers for its own cards.
        Assert.True(CompanionLibraryFilter.Widen(_ => true, companion)(other));

        // The membership test is the base tab's own shape: a pool type test.
        Assert.Contains("CardModel.get_Pool",
                        Il.Calls(typeof(CompanionLibraryFilter)
                            .GetMethod(nameof(CompanionLibraryFilter.InCompanionPool))!));
    }

    [Fact]
    public void The_library_patch_reads_the_fields_the_base_game_declares()
    {
        // STRUCTURAL. Harmony's ____field injection binds by field NAME; a
        // Steam move that renames either field fails here, not in the menu.
        var pools = typeof(NCardLibrary).GetField("_poolFilters", All);
        Assert.NotNull(pools);
        Assert.Equal(typeof(Dictionary<NCardPoolFilter, Func<CardModel, bool>>),
                     pools!.FieldType);
        var colorless = typeof(NCardLibrary).GetField("_colorlessFilter", All);
        Assert.NotNull(colorless);
        Assert.Equal(typeof(NCardPoolFilter), colorless!.FieldType);
        Assert.NotNull(typeof(NCardLibrary).GetMethod("_Ready", All));

        var patch = typeof(CompanionLibraryFilter).Assembly.GetTypes()
            .Single(t => t.Name == "NCardLibrary_CompanionLibraryFilter_Patch");
        Assert.Contains(patch.GetCustomAttributes(inherit: true)
                            .OfType<HarmonyPatch>().Select(a => a.info),
                        i => i.declaringType == typeof(NCardLibrary)
                             && i.methodName == "_Ready");
        var postfix = patch.GetMethod("Postfix", All)!;
        Assert.NotNull(postfix.GetCustomAttribute<HarmonyPostfix>());
        Assert.Equal(new[] { "____poolFilters", "____colorlessFilter" },
                     postfix.GetParameters().Select(p => p.Name));
        Assert.Contains("CompanionLibraryFilter.Widen", Il.Calls(postfix));
    }

    private static IEnumerable<string> LambdaCalls(Type type) =>
        type.GetNestedTypes(All)
            .SelectMany(t => t.GetMethods(All))
            .SelectMany(m => Il.Calls(m));
}
