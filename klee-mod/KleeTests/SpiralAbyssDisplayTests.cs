using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using BaseLib.Abstracts;
using KleeMod.Abyss;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.RelicPools;
using MegaCrit.Sts2.Core.Multiplayer.Serialization;
using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.Saves.Runs;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// THE SPIRAL ABYSS'S IN-RUN DISPLAY (2026-10-12): the Blessing relics, the
/// Abyss Shadows relic and the Shadow badges on enemies.
///
/// On the suite's usual terms (README.md, the headless boundary): the PLANNERS
/// that decide what to grant and what to show run for real against real
/// seats; the save runs through the game's own <c>SavedProperties</c>; the
/// "display only" claim is pinned by reflection over every override the
/// display types make; and the three call sites (the pick, combat start, a
/// summon) and the quiet attach are STRUCTURAL pins on the call set, because
/// <c>RelicCmd.Obtain</c> and a live enemy need a run and a combat the harness
/// cannot build. What only the game can show -- where the icons sit, the
/// tooltips, co-op -- is the PR's live-check list.
/// </summary>
public class SpiralAbyssDisplayTests
{
    // ---- Taking a Blessing: exactly one relic per player ---------------------

    [Fact]
    public void Each_Blessing_has_its_own_relic_with_the_Blessings_text()
    {
        var types = AbyssDraft.AllBlessings.Select(AbyssDisplay.RelicTypeFor).ToList();
        Assert.Equal(14, types.Distinct().Count());
        foreach (var b in AbyssDraft.AllBlessings)
        {
            var relic = (AbyssBlessingRelic)Uninit(AbyssDisplay.RelicTypeFor(b));
            Assert.Equal(b, relic.Blessing);
            var loc = relic.Localization!.ToDictionary(r => r.Item1, r => r.Item2);
            Assert.Equal(AbyssText.Name(b), loc["title"]);
            Assert.Equal(AbyssText.Text(b), loc["description"]);
        }
        Assert.Equal(types.Append(typeof(AbyssShadowsRelic)).ToHashSet(),
                     AbyssDisplay.RelicTypes.ToHashSet());
    }

    [Fact]
    public void Taking_a_Blessing_plans_exactly_one_relic_for_every_player()
    {
        var record = new AbyssRecord();
        record.Record(0, AbyssBlessing.LeyLine, AbyssShadow.Rally);
        var seats = new[] { Seat.Klee(), Seat.Kokomi() };

        foreach (var seat in seats)
        {
            var player = seat.Player;
            Assert.Equal(new[] { AbyssBlessing.LeyLine },
                         AbyssDisplay.BlessingsToGrant(record.Blessings, player.Relics));
            Assert.True(AbyssDisplay.NeedsShadowsRelic(record.Shadows, player.Relics));
            Grant(player, record);
        }

        foreach (var seat in seats)
        {
            var relics = seat.Player.Relics;
            Assert.Single(relics.OfType<AbyssLeyLineRelic>());
            Assert.Single(relics.OfType<AbyssShadowsRelic>());
            Assert.Equal(2, relics.Count);
            // The other copy of the shared event runs the option again: nothing more.
            Assert.Empty(AbyssDisplay.BlessingsToGrant(record.Blessings, relics));
            Assert.False(AbyssDisplay.NeedsShadowsRelic(record.Shadows, relics));
        }

        // The next act's pick adds that act's Blessing and no second Shadows relic.
        record.Record(1, AbyssBlessing.FatefulFortune, AbyssShadow.Clock);
        foreach (var seat in seats)
        {
            Assert.Equal(new[] { AbyssBlessing.FatefulFortune },
                         AbyssDisplay.BlessingsToGrant(record.Blessings, seat.Player.Relics));
            Assert.False(AbyssDisplay.NeedsShadowsRelic(record.Shadows, seat.Player.Relics));
        }
    }

    [Fact]
    public void No_Shadow_yet_means_no_Shadows_relic()
    {
        var seat = Seat.Klee();
        Assert.False(AbyssDisplay.NeedsShadowsRelic(Array.Empty<AbyssShadow>(), seat.Player.Relics));
        Assert.False(AbyssDisplay.NeedsShadowsRelic(new[] { AbyssShadow.None }, seat.Player.Relics));
        Assert.Empty(AbyssDisplay.BlessingsToGrant(new[] { AbyssBlessing.None }, seat.Player.Relics));
    }

    [Fact]
    public void The_pick_grants_through_the_planner_for_the_events_owner()
    {
        // STRUCTURAL: RelicCmd.Obtain needs a live run.
        Assert.Contains("AbyssDisplay.GrantTo", Il.Calls(Il.Method("AbyssChoicePage", "OnChosen")));
        var grant = Il.Calls(typeof(AbyssDisplay).GetMethod(nameof(AbyssDisplay.GrantTo))!);
        Assert.Contains("AbyssDisplay.BlessingsToGrant", grant);
        Assert.Contains("AbyssDisplay.NeedsShadowsRelic", grant);
        Assert.Contains("RelicCmd.Obtain", grant);
    }

    // ---- Reload: restored, never doubled -------------------------------------

    [Fact]
    public void The_Shadows_relic_list_survives_the_games_own_SavedProperties()
    {
        var initialized = typeof(ModelIdSerializationCache)
            .GetField("_initialized", BindingFlags.Static | BindingFlags.NonPublic);
        Assert.NotNull(initialized);
        var was = (bool)initialized!.GetValue(null)!;
        try
        {
            ModelIdSerializationCache.CacheSavedPropertiesForTypeDebug(typeof(AbyssShadowsRelic));
            initialized.SetValue(null, true);

            var relic = (AbyssShadowsRelic)Uninit(typeof(AbyssShadowsRelic));
            relic.SetShadows(new[] { AbyssShadow.Clock, AbyssShadow.Riptide });

            var props = SavedProperties.FromInternal(relic, null);
            Assert.NotNull(props);
            var loaded = (AbyssShadowsRelic)Uninit(typeof(AbyssShadowsRelic));
            props!.FillInternal(loaded);

            Assert.Equal(new[] { AbyssShadow.Clock, AbyssShadow.Riptide }, loaded.Shadows);
        }
        finally
        {
            initialized.SetValue(null, was);
        }
    }

    [Fact]
    public void A_reload_restores_the_relics_and_a_later_grant_adds_no_duplicate()
    {
        var abyss = (SpiralAbyss)Uninit(typeof(SpiralAbyss));
        abyss.Record.Record(0, AbyssBlessing.Crystallize, AbyssShadow.Herald);
        abyss.Record.Record(1, AbyssBlessing.Resonance, AbyssShadow.SheerCold);
        var seat = Seat.Klee();
        Grant(seat.Player, abyss.Record);

        // The save: the modifier's three int[] and the player's relics (the
        // game re-creates each relic from its id and refills its saved
        // properties). Rebuilt here the same way, on a fresh seat.
        var reloadedAbyss = (SpiralAbyss)Uninit(typeof(SpiralAbyss));
        reloadedAbyss.SpiralAbyssActs = abyss.SpiralAbyssActs;
        reloadedAbyss.SpiralAbyssBlessings = abyss.SpiralAbyssBlessings;
        reloadedAbyss.SpiralAbyssShadows = abyss.SpiralAbyssShadows;
        var reloaded = Seat.Klee();
        foreach (var relic in seat.Player.Relics)
        {
            var copy = (RelicModel)Uninit(relic.GetType());
            if (relic is AbyssShadowsRelic shown)
            {
                ((AbyssShadowsRelic)copy).SpiralAbyssShadowsShown = shown.SpiralAbyssShadowsShown;
            }
            Relics(reloaded.Player).Add(copy);
        }

        Assert.Empty(AbyssDisplay.BlessingsToGrant(reloadedAbyss.Record.Blessings, reloaded.Player.Relics));
        Assert.False(AbyssDisplay.NeedsShadowsRelic(reloadedAbyss.Record.Shadows, reloaded.Player.Relics));
        Assert.Equal(3, reloaded.Player.Relics.Count);
        Assert.Equal(new[] { AbyssShadow.Herald, AbyssShadow.SheerCold },
                     reloaded.Player.Relics.OfType<AbyssShadowsRelic>().Single().Shadows);
    }

    [Fact]
    public void The_Shadows_relic_lists_each_Shadow_by_name_and_text()
    {
        var text = AbyssDisplay.ShadowsText(new[] { AbyssShadow.Clock, AbyssShadow.Rally });
        Assert.Contains($"[gold]{AbyssText.Name(AbyssShadow.Clock)}[/gold]: {AbyssText.Text(AbyssShadow.Clock)}", text);
        Assert.Contains($"[gold]{AbyssText.Name(AbyssShadow.Rally)}[/gold]: {AbyssText.Text(AbyssShadow.Rally)}", text);
        Assert.Equal("None yet.", AbyssDisplay.ShadowsText(Array.Empty<AbyssShadow>()));

        var relic = (AbyssShadowsRelic)Uninit(typeof(AbyssShadowsRelic));
        var loc = relic.Localization!.ToDictionary(r => r.Item1, r => r.Item2);
        Assert.Equal("Abyss Shadows", loc["title"]);
        Assert.Contains("{" + AbyssShadowsRelic.ShadowsVar + "}", loc["description"]);
    }

    // ---- Display only: no hook that could change a fight ---------------------

    /// <summary>Every member a display type may override: names, icons, text,
    /// rarity and the never-offered flags. A combat or run hook here would be
    /// a second copy of an effect the modifier already applies.</summary>
    private static readonly HashSet<string> DisplayOnly = new(StringComparer.Ordinal)
    {
        "get_Rarity", "get_HasUponPickupEffect", "get_IsAllowedInShops", "IsAllowed",
        "get_ShouldFlashOnPlayer", "get_IconBaseName", "get_PackedIconPath",
        "get_BigIconPath", "get_Localization", "get_CanonicalVars",
        "get_Type", "get_StackType",
    };

    [Fact]
    public void The_display_relics_and_badges_override_nothing_but_display()
    {
        var framework = new[] { typeof(AbstractModel), typeof(RelicModel), typeof(PowerModel), typeof(CustomRelicModel) };
        foreach (var type in AbyssDisplay.RelicTypes.Concat(AbyssDisplay.PowerTypes))
        {
            for (var t = type; t != null && !framework.Contains(t); t = t.BaseType)
            {
                foreach (var m in t.GetMethods(BindingFlags.Instance | BindingFlags.Public
                                               | BindingFlags.NonPublic | BindingFlags.DeclaredOnly))
                {
                    if (!m.IsVirtual) continue;
                    var root = m.GetBaseDefinition().DeclaringType!;
                    if (!framework.Contains(root)) continue;   // our own abstract members
                    Assert.True(DisplayOnly.Contains(m.Name),
                        $"{type.Name} overrides {root.Name}.{m.Name}, which is not display-only");
                }
            }

            // No mod listener interface either (a Bomb or reaction listener
            // would be a hook by another door).
            var listeners = type.GetInterfaces()
                .Where(i => i.Namespace?.StartsWith("KleeMod", StringComparison.Ordinal) == true)
                .Select(i => i.Name).ToList();
            Assert.Empty(listeners);
        }
    }

    [Fact]
    public void A_badge_is_hidden_count_single_and_attached_without_a_hook()
    {
        foreach (var type in AbyssDisplay.PowerTypes)
        {
            var power = (AbyssShadowPower)Uninit(type);
            Assert.Equal(PowerStackType.Single, power.StackType);
            Assert.Equal(type, AbyssDisplay.PowerTypeFor(power.Shadow));
            var loc = power.Localization!.ToDictionary(r => r.Item1, r => r.Item2);
            Assert.Equal(AbyssText.Name(power.Shadow), loc["title"]);
            Assert.Equal(AbyssText.Text(power.Shadow), loc["description"]);
        }
        Assert.Equal(12, AbyssDisplay.PowerTypes.Distinct().Count());

        // STRUCTURAL: the quiet attach, never PowerCmd.Apply (whose hooks a
        // power-applied listener would hear).
        var show = Il.Calls(typeof(AbyssDisplay).GetMethod(nameof(AbyssDisplay.ShowShadows))!);
        Assert.Contains("PowerModel.ApplyInternal", show);
        Assert.Contains("AbyssDisplay.ShadowsToShow", show);
        Assert.DoesNotContain("PowerCmd.Apply", show);
    }

    // ---- The badges: on every enemy, at the start and when summoned ---------

    [Fact]
    public void Every_enemy_gets_one_badge_per_Shadow_and_never_a_second()
    {
        var applied = new[] { AbyssShadow.Clock, AbyssShadow.MageShield, AbyssShadow.Riptide };
        Assert.Equal(applied, AbyssDisplay.ShadowsToShow(isEnemy: true, applied, Array.Empty<PowerModel>()));

        var worn = new List<PowerModel> { (PowerModel)Uninit(typeof(AbyssClockShadowPower)) };
        Assert.Equal(new[] { AbyssShadow.MageShield, AbyssShadow.Riptide },
                     AbyssDisplay.ShadowsToShow(true, applied, worn));
        worn.Add((PowerModel)Uninit(typeof(AbyssMageShieldShadowPower)));
        worn.Add((PowerModel)Uninit(typeof(AbyssRiptideShadowPower)));
        Assert.Empty(AbyssDisplay.ShadowsToShow(true, applied, worn));

        // Players never wear them; no Shadow, no badge.
        Assert.Empty(AbyssDisplay.ShadowsToShow(isEnemy: false, applied, Array.Empty<PowerModel>()));
        Assert.Empty(AbyssDisplay.ShadowsToShow(true, Array.Empty<AbyssShadow>(), Array.Empty<PowerModel>()));
    }

    [Fact]
    public void A_room_filtered_Shadow_wears_its_badge_only_where_it_acts()
    {
        // Co-op Abyss run, 2026-10-14: Fatui Skirmishers' badge sat on every
        // hallway enemy and both seats read it as 3 Plated Armor on every
        // enemy. The paper (review/active/spiral-abyss-pools-2026-10-12.md):
        // "Elites and bosses enter combat with 3 Plated Armor." The effect
        // already followed it; the badge now does too.
        Assert.Equal("Elites and bosses enter combat with 3 Plated Armor.",
                     AbyssText.Text(AbyssShadow.FatuiSkirmishers));
        var inForce = new[] { AbyssShadow.Bulwark, AbyssShadow.FatuiSkirmishers, AbyssShadow.MageShield };
        Assert.Equal(new[] { AbyssShadow.Bulwark },
                     AbyssRules.BadgesFor(inForce, isElite: false, isBoss: false));
        Assert.Equal(inForce, AbyssRules.BadgesFor(inForce, isElite: true, isBoss: false));
        Assert.Equal(new[] { AbyssShadow.Bulwark, AbyssShadow.FatuiSkirmishers },
                     AbyssRules.BadgesFor(inForce, isElite: false, isBoss: true));

        // STRUCTURAL: both badge moments go through the filter.
        var start = Il.Calls(typeof(SpiralAbyss).GetMethod(nameof(SpiralAbyss.AfterRoomEntered))!);
        Assert.Contains("AbyssRules.BadgesFor", start);
        var summon = Il.Calls(typeof(SpiralAbyss).GetMethod(nameof(SpiralAbyss.AfterCreatureAddedToCombat))!);
        Assert.Contains("AbyssRules.BadgesFor", summon);
    }

    [Fact]
    public void Badges_go_on_at_combat_start_and_on_every_later_summon()
    {
        // STRUCTURAL: both moments need a live combat.
        var start = Il.Calls(typeof(SpiralAbyss).GetMethod(nameof(SpiralAbyss.AfterRoomEntered))!);
        Assert.Contains("AbyssDisplay.ShowShadows", start);
        var summon = Il.Calls(typeof(SpiralAbyss).GetMethod(nameof(SpiralAbyss.AfterCreatureAddedToCombat))!);
        Assert.Contains("AbyssDisplay.ShowShadows", summon);
    }

    // ---- Never offered -------------------------------------------------------

    [Fact]
    public void The_display_relics_roll_nowhere_trade_nowhere_and_sell_nowhere()
    {
        var rolled = (IEnumerable<RelicRarity>)typeof(RelicGrabBag)
            .GetField("_rarities", BindingFlags.Static | BindingFlags.NonPublic)!.GetValue(null)!;
        foreach (var type in AbyssDisplay.RelicTypes)
        {
            var relic = (RelicModel)Uninit(type);
            Assert.Equal(RelicRarity.None, relic.Rarity);
            Assert.DoesNotContain(relic.Rarity, rolled);
            Assert.False(relic.IsTradable);
            Assert.False(relic.IsAllowedInShops);
            Assert.False(relic.IsAllowed(null!));
        }
    }

    [Fact]
    public void The_display_relics_join_only_the_never_rolled_Deprecated_pool()
    {
        Assert.Equal(typeof(DeprecatedRelicPool), AbyssDisplay.PoolType);
        Assert.Contains("AbyssDisplay.RegisterPool", Il.Calls(typeof(global::KleeMod.KleeMod).GetMethod(nameof(global::KleeMod.KleeMod.Initialize))!));
        Assert.Contains("ModHelper.AddModelToPool",
                        Il.Calls(typeof(AbyssDisplay).GetMethod("RegisterPool", HeadlessGame.All)!));

        // No pool or offer in this mod names one: every ModelDb.Relic<T> of a
        // display relic is in AbyssDisplay, and no relic pool's member list
        // reads AbyssDisplay's type list.
        var names = AbyssDisplay.RelicTypes.Select(t => $"ModelDb.Relic<{t.Name}>").ToHashSet();
        // The control: the sweep's spelling is the one the grant really uses.
        Assert.Contains("ModelDb.Relic<AbyssLeyLineRelic>",
                        Il.CallSequence(typeof(AbyssDisplay).GetMethod("BlessingRelic", HeadlessGame.All)!));
        foreach (var type in typeof(global::KleeMod.KleeMod).Assembly.GetTypes())
        {
            if (type == typeof(AbyssDisplay) || type.DeclaringType == typeof(AbyssDisplay)) continue;
            foreach (var m in type.GetMethods(HeadlessGame.All | BindingFlags.DeclaredOnly))
            {
                if (m.IsAbstract || m.GetMethodBody() == null) continue;
                var calls = Il.CallSequence(m);
                Assert.False(calls.Any(names.Contains), $"{type.Name}.{m.Name} names a display relic");
            }
            if (typeof(RelicPoolModel).IsAssignableFrom(type) && !type.IsAbstract)
            {
                var gen = type.GetMethod("GenerateAllRelics", HeadlessGame.All);
                if (gen != null) Assert.DoesNotContain("AbyssDisplay.get_RelicTypes", Il.Calls(gen));
            }
        }
    }

    // ---- The shields' own icons ------------------------------------------------

    [Fact]
    public void Each_Abyss_Mage_Shield_has_its_own_icon()
    {
        var shields = new[]
        {
            typeof(HydroAbyssShieldPower), typeof(PyroAbyssShieldPower),
            typeof(ElectroAbyssShieldPower), typeof(CryoAbyssShieldPower),
        };
        var files = shields.Select(t => ((AbyssShieldPower)Uninit(t)).IconFile).ToList();
        Assert.Equal(4, files.Distinct().Count());
        Assert.All(files, f => Assert.StartsWith("abyss/powers/shield_", f));
        Assert.DoesNotContain(files, f => f.Contains("vigil_of_the_deep"));
    }

    // ---- Helpers ------------------------------------------------------------------

    private static object Uninit(Type type) => RuntimeHelpers.GetUninitializedObject(type);

    private static List<RelicModel> Relics(Player player) =>
        (List<RelicModel>)typeof(Player).GetField("_relics", HeadlessGame.All)!.GetValue(player)!;

    /// <summary>What <see cref="AbyssDisplay.GrantTo"/> does, with the relic
    /// added straight to the list: <c>RelicCmd.Obtain</c> is outside the
    /// boundary, and the decisions are the planners'.</summary>
    private static void Grant(Player player, AbyssRecord record)
    {
        foreach (var b in AbyssDisplay.BlessingsToGrant(record.Blessings, player.Relics))
        {
            Relics(player).Add((RelicModel)Uninit(AbyssDisplay.RelicTypeFor(b)));
        }
        if (AbyssDisplay.NeedsShadowsRelic(record.Shadows, player.Relics))
        {
            Relics(player).Add((RelicModel)Uninit(typeof(AbyssShadowsRelic)));
        }
        foreach (var shown in player.Relics.OfType<AbyssShadowsRelic>()) shown.SetShadows(record.Shadows);
    }
}
