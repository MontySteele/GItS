#nullable enable

using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using BaseLib.Abstracts;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using KleeMod.Vfx;
using MegaCrit.Sts2.Core.Context;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE ICON DECLUTTER (2026-10-19, [USER]: "can we do a search over all of
/// the things in each kit that still print a status icon and see if they're
/// 'really' needed? I've noticed that our characters tend to make a lot of
/// icons."). Pinned here: which badges leave the owner's own status strip
/// (and that a co-op partner still sees them), that one power now carries a
/// card and its upgrade with the two old powers' combined behaviour, and that
/// no two different powers share a title.
/// </summary>
public class IconDeclutterTests
{
    public IconDeclutterTests() => HeadlessGame.Arm();

    private static void AsLocalSeat(ulong me, Action body)
    {
        var was = LocalContext.NetId;
        try
        {
            LocalContext.NetId = me;
            body();
        }
        finally
        {
            LocalContext.NetId = was;
        }
    }

    private static Seat WithNetId(Seat seat, ulong netId)
    {
        Seat.Set(seat.Player, "NetId", netId);
        return seat;
    }

    private static Creature PetOf(Seat owner, Type monster)
    {
        var ctor = typeof(Creature).GetConstructors(HeadlessGame.All)
            .First(c => c.GetParameters().Length == 3
                        && c.GetParameters()[0].ParameterType == typeof(Player));
        var pet = (Creature)ctor.Invoke(new object?[] { null, 10, 10 });
        Seat.Force(pet, "Monster", RuntimeHelpers.GetUninitializedObject(monster));
        pet.PetOwner = owner.Player;
        if (owner.Player.PlayerCombatState is { } state)
        {
            ((List<Creature>)typeof(PlayerCombatState)
                .GetField("_pets", HeadlessGame.All)!
                .GetValue(state)!).Add(pet);
        }
        return pet;
    }

    // ---- 1. badges a surface already draws ----------------------------------

    [Fact]
    public void Yaes_sakura_badges_hide_on_her_screen_and_show_to_a_partner()
    {
        var yae = WithNetId(Seat.Yae(), 1UL)
            .WithPower<SakuraFirstPower>(1).WithPower<SakuraNinthPower>(1);
        foreach (var badge in yae.Creature.Powers.OfType<SakuraBadgePower>())
        {
            AsLocalSeat(1UL, () => Assert.True(YaeSakuraDisplay.HidesBadge(badge)));
            AsLocalSeat(2UL, () => Assert.False(YaeSakuraDisplay.HidesBadge(badge)));
        }
        // Another of her powers keeps its badge; a canonical model must not
        // throw.
        var other = WithNetId(Seat.Yae(), 1UL).WithPower<FanfarePower>(1);
        AsLocalSeat(1UL, () => Assert.False(YaeSakuraDisplay.HidesBadge(
            other.Creature.Powers.OfType<FanfarePower>().Single())));
        Assert.False(YaeSakuraDisplay.HidesBadge(new SakuraFirstPower()));
    }

    [Fact]
    public void Kokomis_plan_count_hides_on_her_screen_where_the_strip_draws_it()
    {
        var kokomi = WithNetId(Seat.Kokomi().WithCombatState(), 1UL)
            .WithPower<PendingPlansPower>(2);
        var badge = kokomi.Creature.Powers.OfType<PendingPlansPower>().Single();
        AsLocalSeat(1UL, () => Assert.True(KokomiBadges.HidesBadge(badge)));
        AsLocalSeat(2UL, () => Assert.False(KokomiBadges.HidesBadge(badge)));
        Assert.False(KokomiBadges.HidesBadge(new PendingPlansPower()));
    }

    [Fact]
    public void The_bake_kurage_marker_hides_once_the_jellyfish_carries_its_sentence()
    {
        var kokomi = WithNetId(Seat.Kokomi().WithCombatState(), 1UL)
            .WithPower<ProtoBakeKuragePower>(1);
        var marker = kokomi.Creature.Powers.OfType<ProtoBakeKuragePower>().Single();
        // No jellyfish on the field yet: the badge is the only home.
        AsLocalSeat(1UL, () => Assert.False(KokomiBadges.HidesBadge(marker)));

        var pet = PetOf(kokomi, typeof(BakeKurageMonster));
        AsLocalSeat(1UL, () => Assert.True(KokomiBadges.HidesBadge(marker)));
        AsLocalSeat(2UL, () => Assert.False(KokomiBadges.HidesBadge(marker)));
        // The jellyfish's own hover carries the marker's tips; nobody else's.
        Assert.Same(marker, KokomiBadges.PetMarker(pet));
        Assert.Null(KokomiBadges.PetMarker(kokomi.Creature));
        Assert.Null(KokomiBadges.PetMarker(null));
        var hook = Il.Calls(Il.Method("Creature_HoverTips_BakeKurage_Patch",
                                      "Postfix"));
        Assert.Contains(hook, c => c.Contains("KokomiBadges.PetTips"));
    }

    [Fact]
    public void Varkas_left_flag_hides_on_his_screen_and_joins_the_dial_hover()
    {
        var varka = WithNetId(Seat.Varka(), 1UL).WithPower<HydroOathLeftPower>(1);
        var left = varka.Creature.Powers.OfType<HydroOathLeftPower>().Single();
        AsLocalSeat(1UL, () => Assert.True(VarkaOathDial.HidesBadge(left)));
        AsLocalSeat(2UL, () => Assert.False(VarkaOathDial.HidesBadge(left)));
        // The hover adds the left flag's tips after the Oath badge's.
        var hover = Il.Calls(Il.Method("VarkaOathDial", "ShowHover"));
        Assert.Contains("PowerModel.get_HoverTips", hover);
        Assert.Contains(hover, c => c.Contains("AddRange"));
    }

    [Fact]
    public void Every_hide_is_at_the_container_never_through_visibility()
    {
        // The seat bridge's power list skips an invisible power, and the
        // seat page reads every one of these.
        foreach (var type in new[]
                 {
                     typeof(SakuraBadgePower), typeof(PendingPlansPower),
                     typeof(ProtoBakeKuragePower), typeof(OathLeftPower),
                 })
        {
            Assert.Null(type.GetProperty("IsVisibleInternal",
                HeadlessGame.All | System.Reflection.BindingFlags.DeclaredOnly));
        }
    }

    // ---- 2. one badge for a card and its upgrade ----------------------------

    private static T Twin<T>(Seat seat, int amount, int upgraded, bool upgradedFirst)
        where T : UpgradeTwinPower
    {
        seat.WithPower<T>(amount);
        var power = seat.Creature.Powers.OfType<T>().Single();
        // What the plays noted: the first decides the order.
        power.NoteCopies(0, upgradedFirst, fresh: true);
        power.NoteCopies(upgraded, upgraded: true, fresh: false);
        return power;
    }

    [Fact]
    public void A_twin_counts_plain_and_upgraded_copies_and_keeps_their_order()
    {
        var both = Twin<KurageCanopyPower>(Seat.Kokomi(), 3, 1, upgradedFirst: false);
        Assert.Equal(2, both.PlainCopies);
        Assert.Equal(1, both.UpgradedCopies);
        Assert.Equal(new[] { (2, false), (1, true) }, both.Batches());

        var plusFirst = Twin<KurageCanopyPower>(Seat.Kokomi(), 2, 1, upgradedFirst: true);
        Assert.Equal(new[] { (1, true), (1, false) }, plusFirst.Batches());

        Assert.Equal(new[] { (2, false) }, UpgradeTwinPower.Batches(2, 0, false));
        Assert.Equal(new[] { (2, true) }, UpgradeTwinPower.Batches(0, 2, false));
        Assert.Empty(UpgradeTwinPower.Batches(0, 0, true));

        // A fresh instance starts its count over.
        both.NoteCopies(1, upgraded: false, fresh: true);
        Assert.Equal(0, both.UpgradedCopies);
        // Never more upgraded copies than copies.
        both.NoteCopies(9, upgraded: true, fresh: false);
        Assert.Equal((int)both.Amount, both.UpgradedCopies);
    }

    [Fact]
    public void Prima_donna_reads_every_copy_as_energy_and_upgraded_ones_as_cards()
    {
        // Before: PrimaDonna = plain + plus, PrimaDonnaDraw = plus.
        var furina = Seat.Furina();
        Twin<PrimaDonnaPower>(furina, 3, 2, upgradedFirst: false);
        var mods = FurinaStage.ModsOf(furina.Creature);
        Assert.Equal(3, mods.PrimaDonna);
        Assert.Equal(2, mods.PrimaDonnaDraw);

        var plain = Seat.Furina().WithPower<PrimaDonnaPower>(1);
        Assert.Equal(0, FurinaStage.ModsOf(plain.Creature).PrimaDonnaDraw);
    }

    [Fact]
    public void Canopy_and_detonator_add_each_batch_through_their_old_doors()
    {
        var canopy = Il.Calls(Il.Method("KurageCanopyPower", "OnPlanResolved"));
        Assert.Contains(canopy, c => c.Contains("UpgradeTwinPower.Batches"));
        Assert.Contains(canopy, c => c.Contains("KokomiCards.AddJellyfish"));
        var mines = Il.Calls(Il.Method("AlicesDetonatorPower", "BeforeHandDraw"));
        Assert.Contains(mines, c => c.Contains("UpgradeTwinPower.Batches"));
        Assert.Contains("CardModel.UpgradeInternal", mines);
        foreach (var gone in new[]
                 {
                     "AlicesDetonatorPlusPower", "PrimaDonnaPlusPower",
                     "KurageCanopyPlusPower",
                 })
        {
            Assert.Null(typeof(UpgradeTwinPower).Assembly
                .GetType("KleeMod.Powers." + gone));
        }
    }

    // ---- 3. no two powers share a title -------------------------------------

    /// <summary>Furina's guests: an upgraded guest is the same character on
    /// the stage, so it keeps the guest's name (its sentence says what the
    /// upgrade does). A curated list, not a pattern: a new pair is a line
    /// here, added deliberately.</summary>
    private static readonly HashSet<string> GuestPairs = new()
    {
        "Charlotte", "Chevreuse", "Clorinde", "Escoffier", "Freminet",
        "Lynette", "Lyney", "Navia", "Neuvillette", "Sigewinne", "Wriothesley",
    };

    [Fact]
    public void No_two_different_powers_share_a_title()
    {
        var titles = new Dictionary<string, List<string>>();
        foreach (var type in typeof(UpgradeTwinPower).Assembly.GetTypes()
                     .Where(t => !t.IsAbstract
                                 && typeof(PowerModel).IsAssignableFrom(t)
                                 && typeof(ILocalizationProvider).IsAssignableFrom(t)))
        {
            string? title;
            try
            {
                var model = (ILocalizationProvider)RuntimeHelpers
                    .GetUninitializedObject(type);
                title = model.Localization?
                    .FirstOrDefault(r => r.Item1 == "title").Item2;
            }
            catch (Exception)
            {
                continue;
            }
            if (string.IsNullOrEmpty(title)) continue;
            if (!titles.TryGetValue(title, out var list))
            {
                titles[title] = list = new List<string>();
            }
            list.Add(type.Name);
        }
        var shared = titles.Where(kv => kv.Value.Count > 1
                                        && !(GuestPairs.Contains(kv.Key)
                                             && kv.Value.Count == 2
                                             && kv.Value.All(n => n.StartsWith(kv.Key)
                                                                  && n.EndsWith("BadgePower"))))
            .Select(kv => $"{kv.Key}: {string.Join(", ", kv.Value.OrderBy(n => n))}")
            .OrderBy(s => s)
            .ToList();
        Assert.True(shared.Count == 0,
                    "powers sharing a title:\n" + string.Join("\n", shared));
    }
}
