using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using KleeMod.Abyss;
using KleeMod.Elements;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Multiplayer.Serialization;
using MegaCrit.Sts2.Core.Saves.Runs;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// THE SPIRAL ABYSS MODE's pins (<c>review/active/spiral-abyss-pools-2026-10-12.md</c>).
///
/// THE HEADLESS BOUNDARY (README.md) holds here as everywhere: no live combat,
/// no ModelDb, no event room. So every Blessing and Shadow is pinned through
/// the pure decision it makes (<see cref="AbyssRules"/>), which is the exact
/// function the modifier's hook calls, plus the hooks that can be called
/// headlessly (Resonance's draw). The draft, the record, the stacking, the
/// no-repeat rule, the roll and the save are pinned on the real types.
///
/// What only a live run can show -- the menu button, the page over the
/// Ancient, the co-op vote, each hook firing at its moment -- is listed in the
/// build's PR as the live check it owes.
/// </summary>
public class SpiralAbyssTests
{
    private static SpiralAbyss NewModifier() =>
        (SpiralAbyss)RuntimeHelpers.GetUninitializedObject(typeof(SpiralAbyss));

    // ---- The texts are the paper's -----------------------------------------

    [Fact]
    public void Every_entry_text_is_the_papers_word_for_word()
    {
        var paper = File.ReadAllText(Path.Combine(
            RepoRoot(), "review", "active", "spiral-abyss-pools-2026-10-12.md"));
        foreach (var b in AbyssDraft.AllBlessings)
        {
            Assert.Contains($"**{AbyssText.Name(b)}** | {AbyssText.Text(b)} |", paper);
        }
        foreach (var s in AbyssDraft.AllShadows)
        {
            Assert.Contains($"**{AbyssText.Name(s)}** | {AbyssText.Text(s)} |", paper);
        }
        Assert.Equal(8, AbyssDraft.AllBlessings.Count);
        Assert.Equal(8, AbyssDraft.AllShadows.Count);
    }

    // ---- Each Blessing once ---------------------------------------------------

    [Fact]
    public void LeyLine_applies_to_bare_enemies_and_takes_1_off_an_aura_wearers_hit()
    {
        Assert.True(AbyssRules.LeyLineApplies(isEnemy: true, isAlive: true, hasAura: false));
        Assert.False(AbyssRules.LeyLineApplies(true, true, hasAura: true));
        Assert.False(AbyssRules.LeyLineApplies(true, isAlive: false, false));
        Assert.False(AbyssRules.LeyLineApplies(isEnemy: false, true, false));

        Assert.Equal(-1m, AbyssRules.LeyLineDamageDelta(true, true, true, 12m));
        Assert.Equal(0m, AbyssRules.LeyLineDamageDelta(true, dealerHasAura: false, true, 12m));
        Assert.Equal(0m, AbyssRules.LeyLineDamageDelta(dealerIsEnemy: false, true, true, 12m));
        Assert.Equal(0m, AbyssRules.LeyLineDamageDelta(true, true, isPoweredAttack: false, 12m));
        Assert.Equal(0m, AbyssRules.LeyLineDamageDelta(true, true, true, 0m));
    }

    [Fact]
    public void AbyssalMoon_fires_on_every_third_card_of_a_turn()
    {
        var fired = Enumerable.Range(1, 9).Where(AbyssRules.AbyssalMoonFires).ToArray();
        Assert.Equal(new[] { 3, 6, 9 }, fired);
        Assert.False(AbyssRules.AbyssalMoonFires(0));
        Assert.Equal(4, AbyssNumbers.AbyssalMoonDamage);
    }

    [Fact]
    public void MoonlitRest_heals_4() => Assert.Equal(4, AbyssNumbers.MoonlitRestHeal);

    [Fact]
    public void FirstStrike_adds_one_play_to_the_first_Attack_only()
    {
        Assert.Equal(1, AbyssRules.FirstStrikeExtraPlays(isAttack: true, attackAlreadyPlayedThisCombat: false));
        Assert.Equal(0, AbyssRules.FirstStrikeExtraPlays(true, attackAlreadyPlayedThisCombat: true));
        Assert.Equal(0, AbyssRules.FirstStrikeExtraPlays(isAttack: false, false));
    }

    [Fact]
    public void ElementalBurst_pays_6_once_per_Power_played()
    {
        Assert.True(AbyssRules.ElementalBurstFires(isPower: true, isFirstInSeries: true));
        Assert.False(AbyssRules.ElementalBurstFires(true, isFirstInSeries: false));
        Assert.False(AbyssRules.ElementalBurstFires(isPower: false, true));
        Assert.Equal(6, AbyssNumbers.ElementalBurstDamage);
    }

    [Fact]
    public void Resonance_draws_one_more_on_turn_1_through_the_real_hook()
    {
        var abyss = NewModifier();
        var seat = Seat.Klee().WithCombatState();

        // Not taken: the hook leaves the draw alone.
        Assert.Equal(5m, abyss.ModifyHandDraw(seat.Player, 5m));

        abyss.Record.Record(0, AbyssBlessing.Resonance, AbyssShadow.Clock);
        SetTurn(seat.Player, 1);
        Assert.Equal(6m, abyss.ModifyHandDraw(seat.Player, 5m));
        SetTurn(seat.Player, 2);
        Assert.Equal(5m, abyss.ModifyHandDraw(seat.Player, 5m));

        Assert.True(AbyssRules.ResonanceApplies(1));
        Assert.False(AbyssRules.ResonanceApplies(2));
        Assert.Equal(1, AbyssNumbers.ResonanceEnergy);
    }

    [Fact]
    public void Crystallize_gives_8_Block() => Assert.Equal(8, AbyssNumbers.CrystallizeBlock);

    [Fact]
    public void FatefulFortune_gives_12_Max_HP() => Assert.Equal(12, AbyssNumbers.FatefulFortuneMaxHp);

    // ---- Each Shadow once ------------------------------------------------------

    [Fact]
    public void Clock_starts_on_round_5()
    {
        Assert.False(AbyssRules.ClockApplies(4));
        Assert.True(AbyssRules.ClockApplies(5));
        Assert.True(AbyssRules.ClockApplies(9));
        Assert.Equal(2, AbyssNumbers.ClockStrength);
    }

    [Fact]
    public void MageShield_is_8_hits_a_reaction_takes_3_and_the_counter_breaks_it()
    {
        Assert.Equal(8, AbyssNumbers.MageShieldHits);
        Assert.Equal(7, AbyssRules.ShieldAfterHit(8, Element.None, Element.Hydro));
        Assert.Equal(7, AbyssRules.ShieldAfterHit(8, Element.Pyro, Element.Hydro));
        Assert.Equal(0, AbyssRules.ShieldAfterHit(8, Element.Cryo, Element.Hydro));
        Assert.Equal(0, AbyssRules.ShieldAfterHit(1, Element.None, Element.Hydro));
        Assert.Equal(5, AbyssRules.ShieldAfterReaction(8));
        Assert.Equal(0, AbyssRules.ShieldAfterReaction(2));
        Assert.True(AbyssRules.MageShieldRoom(isElite: true));
        Assert.False(AbyssRules.MageShieldRoom(isElite: false));
    }

    [Fact]
    public void SheerCold_bites_only_a_living_player_with_no_Block()
    {
        Assert.True(AbyssRules.SheerColdApplies(isPlayer: true, isAlive: true, block: 0));
        Assert.False(AbyssRules.SheerColdApplies(true, true, block: 1));
        Assert.False(AbyssRules.SheerColdApplies(isPlayer: false, true, 0));
        Assert.False(AbyssRules.SheerColdApplies(true, isAlive: false, 0));
        Assert.Equal(3, AbyssNumbers.SheerColdHpLoss);
    }

    [Fact]
    public void ElementalMark_and_Riptide_trigger_on_an_enemy_attack_that_got_through()
    {
        Assert.True(AbyssRules.EnemyAttackLanded(true, true, true, unblockedDamage: 1));
        Assert.False(AbyssRules.EnemyAttackLanded(true, true, true, unblockedDamage: 0));
        Assert.False(AbyssRules.EnemyAttackLanded(true, true, isPoweredAttack: false, 5));
        Assert.False(AbyssRules.EnemyAttackLanded(true, dealerIsEnemy: false, true, 5));
        Assert.False(AbyssRules.EnemyAttackLanded(targetIsPlayer: false, true, true, 5));
        Assert.Equal(1, AbyssNumbers.RiptideStrength);
    }

    [Fact]
    public void Herald_adds_15_percent_max_HP()
    {
        Assert.Equal(15, AbyssRules.HeraldBonus(100));
        Assert.Equal(8, AbyssRules.HeraldBonus(50));   // 7.5 rounds away from zero
        Assert.Equal(0, AbyssRules.HeraldBonus(0));
    }

    [Fact]
    public void Rally_gives_the_others_2_Strength() => Assert.Equal(2, AbyssNumbers.RallyStrength);

    [Fact]
    public void Fatui_covers_elites_and_bosses_with_3_Plated_Armor()
    {
        Assert.True(AbyssRules.FatuiRoom(isElite: true, isBoss: false));
        Assert.True(AbyssRules.FatuiRoom(false, isBoss: true));
        Assert.False(AbyssRules.FatuiRoom(false, false));
        Assert.Equal(3, AbyssNumbers.FatuiPlating);
    }

    [Fact]
    public void Act_elements_and_counters()
    {
        Assert.Equal(Element.Hydro, AbyssElements.ForAct(0));
        Assert.Equal(Element.Pyro, AbyssElements.ForAct(1));
        Assert.Equal(Element.Electro, AbyssElements.ForAct(2));
        Assert.Equal(Element.Electro, AbyssElements.ForAct(5));
        foreach (var e in AbyssElements.Table)
        {
            Assert.True(e.LeavesAura());
            Assert.NotEqual(Element.None, AbyssElements.CounterOf(e));
            Assert.NotEqual(e, AbyssElements.CounterOf(e));
        }
    }

    // ---- The draft: stacking, no repeats, the roll ----------------------------

    [Fact]
    public void Three_acts_stack_three_Blessings_and_three_Shadows()
    {
        var abyss = NewModifier();
        const ulong seed = 123456789UL;
        for (var act = 0; act < 3; act++)
        {
            var offer = AbyssDraft.Offer(seed, act, abyss.Record);
            Assert.Equal(3, offer.Options.Count);
            var pick = act % 3;
            Assert.True(abyss.Record.Record(act, offer.Options[pick].Blessing, offer.ShadowIfChosen(pick)));
        }

        Assert.Equal(new[] { 0, 1, 2 }, abyss.Record.Acts);
        Assert.Equal(3, abyss.Record.Blessings.Distinct().Count());
        Assert.Equal(3, abyss.Record.Shadows.Distinct().Count());
        foreach (var b in abyss.Record.Blessings) Assert.True(abyss.Record.Has(b));
        foreach (var s in abyss.Record.Shadows) Assert.True(abyss.Record.Has(s));
    }

    [Fact]
    public void An_act_records_once_however_many_players_resolve_the_shared_option()
    {
        var record = new AbyssRecord();
        Assert.True(record.Record(0, AbyssBlessing.LeyLine, AbyssShadow.Rally));
        Assert.False(record.Record(0, AbyssBlessing.LeyLine, AbyssShadow.Rally));
        Assert.Single(record.Blessings);
    }

    [Fact]
    public void No_entry_repeats_in_a_run_across_many_seeds_and_picks()
    {
        for (ulong seed = 1; seed <= 300; seed++)
        {
            var record = new AbyssRecord();
            for (var act = 0; act < 3; act++)
            {
                var offer = AbyssDraft.Offer(seed * 7919UL, act, record);
                Assert.Equal(3, offer.Options.Count);
                Assert.Equal(3, offer.Options.Select(o => o.Blessing).Distinct().Count());
                Assert.Equal(3, offer.Options.Select(o => o.Shadow).Distinct().Count());
                Assert.DoesNotContain(offer.Options, o => record.Has(o.Blessing));
                Assert.DoesNotContain(offer.Options, o => record.Has(o.Shadow));

                var pick = (int)((seed + (ulong)act) % 3);
                var shadow = offer.ShadowIfChosen(pick);
                Assert.NotEqual(offer.Options[pick].Shadow, shadow);
                Assert.Contains(offer.Options.Where((_, i) => i != pick), o => o.Shadow == shadow);
                record.Record(act, offer.Options[pick].Blessing, shadow);
            }
            Assert.Equal(3, record.Blessings.Distinct().Count());
            Assert.Equal(3, record.Shadows.Distinct().Count());
        }
    }

    [Fact]
    public void The_page_and_the_roll_are_reload_stable()
    {
        const ulong seed = 987654321UL;
        var record = new AbyssRecord();
        record.Record(0, AbyssBlessing.Crystallize, AbyssShadow.Herald);

        var first = AbyssDraft.Offer(seed, 1, record);

        // The save round trip: three int[] out, three int[] in.
        var reloaded = new AbyssRecord();
        reloaded.LoadActs(record.ActsArray());
        reloaded.LoadBlessings(record.BlessingsArray());
        reloaded.LoadShadows(record.ShadowsArray());
        var second = AbyssDraft.Offer(seed, 1, reloaded);

        Assert.Equal(first.Options, second.Options);
        Assert.Equal(first.ShadowRoll, second.ShadowRoll);
        for (var i = 0; i < 3; i++) Assert.Equal(first.ShadowIfChosen(i), second.ShadowIfChosen(i));

        // Another act or another seed draws another page.
        Assert.False(AbyssDraft.Offer(seed, 2, record).Options.SequenceEqual(first.Options)
                     && AbyssDraft.Offer(seed + 1, 1, record).Options.SequenceEqual(first.Options));
    }

    [Fact]
    public void Both_passed_Shadows_can_be_rolled()
    {
        var rolls = Enumerable.Range(1, 200)
            .Select(s => AbyssDraft.Offer((ulong)s, 0, new AbyssRecord()).ShadowRoll)
            .Distinct().OrderBy(r => r).ToArray();
        Assert.Equal(new[] { 0, 1 }, rolls);
    }

    // ---- The save ---------------------------------------------------------------

    [Fact]
    public void The_modifier_state_survives_a_save_and_reload_mid_run()
    {
        var abyss = NewModifier();
        abyss.Record.Record(0, AbyssBlessing.LeyLine, AbyssShadow.MageShield);
        abyss.Record.Record(1, AbyssBlessing.FirstStrike, AbyssShadow.Riptide);

        var saved = typeof(SpiralAbyss)
            .GetProperties(BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic)
            .Where(p => p.GetCustomAttribute<SavedPropertyAttribute>() != null)
            .ToList();
        Assert.Equal(3, saved.Count);
        Assert.All(saved, p => Assert.Equal(typeof(int[]), p.PropertyType));

        // What SavedProperties.FillInternal does: read every saved property off
        // the old instance and set it on a fresh one.
        var loaded = NewModifier();
        foreach (var p in saved) p.SetValue(loaded, p.GetValue(abyss));

        Assert.Equal(abyss.Record.Acts, loaded.Record.Acts);
        Assert.Equal(abyss.Record.Blessings, loaded.Record.Blessings);
        Assert.Equal(abyss.Record.Shadows, loaded.Record.Shadows);
        Assert.True(loaded.Record.HasPicked(1));
        Assert.False(loaded.Record.HasPicked(2));

        // And the next page drawn after the reload is the page drawn before it.
        Assert.Equal(AbyssDraft.Offer(42, 2, abyss.Record).Options,
                     AbyssDraft.Offer(42, 2, loaded.Record).Options);
    }

    [Fact]
    public void The_modifier_state_survives_the_games_own_SavedProperties()
    {
        var initialized = typeof(ModelIdSerializationCache)
            .GetField("_initialized", BindingFlags.Static | BindingFlags.NonPublic);
        Assert.NotNull(initialized);
        var was = (bool)initialized!.GetValue(null)!;
        try
        {
            ModelIdSerializationCache.CacheSavedPropertiesForTypeDebug(typeof(SpiralAbyss));
            initialized.SetValue(null, true);

            var abyss = NewModifier();
            abyss.Record.Record(0, AbyssBlessing.Resonance, AbyssShadow.Clock);
            abyss.Record.Record(1, AbyssBlessing.MoonlitRest, AbyssShadow.SheerCold);
            abyss.Record.Record(2, AbyssBlessing.AbyssalMoon, AbyssShadow.Rally);

            var props = SavedProperties.FromInternal(abyss, null);
            Assert.NotNull(props);
            var loaded = NewModifier();
            props!.FillInternal(loaded);

            Assert.Equal(abyss.Record.Acts, loaded.Record.Acts);
            Assert.Equal(abyss.Record.Blessings, loaded.Record.Blessings);
            Assert.Equal(abyss.Record.Shadows, loaded.Record.Shadows);
        }
        finally
        {
            initialized.SetValue(null, was);
        }
    }

    [Fact]
    public void A_new_run_starts_with_nothing_taken()
    {
        var abyss = NewModifier();
        abyss.Record.Record(0, AbyssBlessing.LeyLine, AbyssShadow.Clock);
        typeof(SpiralAbyss).GetMethod("AfterRunCreated", BindingFlags.Instance | BindingFlags.NonPublic)!
            .Invoke(abyss, new object[] { null });
        Assert.Empty(abyss.Record.Acts);
    }

    [Fact]
    public void A_run_without_the_modifier_has_no_Abyss()
    {
        Assert.Null(SpiralAbyss.In(null));
    }

    // ---- Helpers ----------------------------------------------------------------

    private static void SetTurn(Player player, int turn) =>
        Seat.Force(player.PlayerCombatState, "TurnNumber", turn);

    private static string RepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir != null && !Directory.Exists(Path.Combine(dir.FullName, "klee-mod", "KleeCode")))
        {
            dir = dir.Parent;
        }
        Assert.NotNull(dir);
        return dir!.FullName;
    }
}
