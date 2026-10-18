using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using HarmonyLib;
using KleeMod.Abyss;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Factories;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Multiplayer.Serialization;
using MegaCrit.Sts2.Core.Saves.Runs;
using MegaCrit.Sts2.Core.ValueProps;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// THE SPIRAL ABYSS, ROUND TWO (<c>review/ruled/abyss-pools-2-2026-10-12.md</c>,
/// ruled 2026-10-12: pick 1 (a), pick 2 (a) with Moonlit Spring at 8, Frenzy
/// as 2 Strength, and no retunes).
///
/// On <see cref="SpiralAbyssTests"/>' terms: the durations, the expiry, the
/// save, the page mix and each new entry's decision run for real on the real
/// types; the hooks that need a live combat (a power applied, Block gained, a
/// reaction's splash, a reward rolled) are STRUCTURAL pins on the call set.
/// What only the game can show is the PR's live-check list.
/// </summary>
public class AbyssPoolsTwoTests
{
    private static SpiralAbyss NewModifier(int act)
    {
        var abyss = (SpiralAbyss)RuntimeHelpers.GetUninitializedObject(typeof(SpiralAbyss));
        abyss.ActForTests = act;
        return abyss;
    }

    private static readonly AbyssBlessing[] ThisActBlessings =
    {
        AbyssBlessing.Overflow, AbyssBlessing.VigorOfTheAbyss,
        AbyssBlessing.MoonlitSpring, AbyssBlessing.BattleRhythm,
    };

    private static readonly AbyssShadow[] ThisActShadows =
    {
        AbyssShadow.ThornyGround, AbyssShadow.Bulwark, AbyssShadow.Frenzy, AbyssShadow.Riptide,
    };

    // ---- The durations ----------------------------------------------------------

    [Fact]
    public void Four_Blessings_and_four_Shadows_last_this_act_and_the_rest_the_whole_run()
    {
        foreach (var b in AbyssDraft.AllBlessings)
        {
            Assert.Equal(ThisActBlessings.Contains(b) ? AbyssDuration.ThisAct : AbyssDuration.WholeRun,
                         AbyssDurations.Of(b));
        }
        foreach (var s in AbyssDraft.AllShadows)
        {
            Assert.Equal(ThisActShadows.Contains(s) ? AbyssDuration.ThisAct : AbyssDuration.WholeRun,
                         AbyssDurations.Of(s));
        }
        // Every This act entry says so in its own text, in every act; no
        // Whole run one does.
        for (var act = 0; act < AbyssNumbers.ActRows; act++)
        {
            foreach (var b in AbyssDraft.AllBlessings)
            {
                Assert.Equal(AbyssDurations.Of(b) == AbyssDuration.ThisAct,
                             AbyssText.Text(b, act).StartsWith("This act, ", StringComparison.Ordinal));
            }
            foreach (var s in AbyssDraft.AllShadows)
            {
                Assert.Equal(AbyssDurations.Of(s) == AbyssDuration.ThisAct,
                             AbyssText.Text(s, act).StartsWith("This act, ", StringComparison.Ordinal));
            }
        }
        Assert.Equal("Whole run", AbyssDurations.Tag(AbyssDuration.WholeRun));
        Assert.Equal("This act", AbyssDurations.Tag(AbyssDuration.ThisAct));
    }

    [Fact]
    public void The_save_numbers_of_the_first_sixteen_never_moved()
    {
        Assert.Equal(8, (int)AbyssBlessing.FatefulFortune);
        Assert.Equal(7, (int)AbyssShadow.Riptide);
        Assert.Equal(8, (int)AbyssShadow.FatuiSkirmishers);
        Assert.Equal(new[] { 9, 10, 11, 12, 13, 14 },
            new[] { AbyssBlessing.Overflow, AbyssBlessing.VigorOfTheAbyss, AbyssBlessing.MoonlitSpring,
                    AbyssBlessing.BattleRhythm, AbyssBlessing.WaveringMoon, AbyssBlessing.StarfellDraft }
                .Select(b => (int)b));
        Assert.Equal(new[] { 9, 10, 11, 12 },
            new[] { AbyssShadow.ThornyGround, AbyssShadow.Bulwark, AbyssShadow.Frenzy, AbyssShadow.Withering }
                .Select(s => (int)s));
    }

    // ---- Expiry: a This act entry ends with its act ------------------------------

    [Fact]
    public void A_this_act_entry_is_in_force_in_its_act_and_gone_after_it()
    {
        var record = new AbyssRecord();
        record.Record(0, AbyssBlessing.Overflow, AbyssShadow.Riptide);
        record.Record(1, AbyssBlessing.WaveringMoon, AbyssShadow.Withering);

        Assert.True(record.HasInForce(AbyssBlessing.Overflow, 0));
        Assert.True(record.HasInForce(AbyssShadow.Riptide, 0));
        Assert.False(record.HasInForce(AbyssBlessing.Overflow, 1));
        Assert.False(record.HasInForce(AbyssShadow.Riptide, 1));
        Assert.False(record.HasInForce(AbyssBlessing.Overflow, 2));

        // Whole run entries stay from the act they were taken in.
        Assert.True(record.HasInForce(AbyssBlessing.WaveringMoon, 1));
        Assert.True(record.HasInForce(AbyssBlessing.WaveringMoon, 2));
        Assert.True(record.HasInForce(AbyssShadow.Withering, 2));

        Assert.Equal(new[] { AbyssBlessing.Overflow }, record.BlessingsInForce(0));
        Assert.Equal(new[] { AbyssBlessing.WaveringMoon }, record.BlessingsInForce(1));
        Assert.Equal(new[] { AbyssShadow.Riptide }, record.ShadowsInForce(0));
        Assert.Equal(new[] { AbyssShadow.Withering }, record.ShadowsInForce(2));

        // "Taken" is still taken: an expired entry is never offered again.
        Assert.True(record.Has(AbyssBlessing.Overflow));
        Assert.True(record.Has(AbyssShadow.Riptide));
    }

    [Fact]
    public void The_modifier_reads_the_act_for_this_act_entries_only()
    {
        var abyss = NewModifier(act: 0);
        abyss.Record.Record(0, AbyssBlessing.MoonlitSpring, AbyssShadow.Frenzy);
        abyss.Record.Record(1, AbyssBlessing.Crystallize, AbyssShadow.Clock);

        Assert.True(abyss.Has(AbyssBlessing.MoonlitSpring));
        Assert.True(abyss.Has(AbyssShadow.Frenzy));
        Assert.Equal(new[] { AbyssShadow.Frenzy }, abyss.ShadowsNow);   // the Clock comes in act 2

        abyss.ActForTests = 1;
        Assert.False(abyss.Has(AbyssBlessing.MoonlitSpring));
        Assert.False(abyss.Has(AbyssShadow.Frenzy));
        Assert.True(abyss.Has(AbyssBlessing.Crystallize));
        Assert.True(abyss.Has(AbyssShadow.Clock));
        Assert.Equal(new[] { AbyssShadow.Clock }, abyss.ShadowsNow);
    }

    [Fact]
    public void A_run_continued_mid_act_keeps_the_acts_entries_and_one_continued_after_has_lost_them()
    {
        var initialized = typeof(ModelIdSerializationCache)
            .GetField("_initialized", BindingFlags.Static | BindingFlags.NonPublic);
        Assert.NotNull(initialized);
        var was = (bool)initialized!.GetValue(null)!;
        try
        {
            ModelIdSerializationCache.CacheSavedPropertiesForTypeDebug(typeof(SpiralAbyss));
            initialized.SetValue(null, true);

            var abyss = NewModifier(act: 1);
            abyss.Record.Record(0, AbyssBlessing.Resonance, AbyssShadow.Bulwark);
            abyss.Record.Record(1, AbyssBlessing.BattleRhythm, AbyssShadow.ThornyGround);

            var props = SavedProperties.FromInternal(abyss, null);
            Assert.NotNull(props);

            // Continued in act 2 (index 1), the act of the second pick.
            var midAct = NewModifier(act: 1);
            props!.FillInternal(midAct);
            Assert.True(midAct.Has(AbyssBlessing.BattleRhythm));
            Assert.True(midAct.Has(AbyssShadow.ThornyGround));
            Assert.False(midAct.Has(AbyssShadow.Bulwark));      // act 1's, ended
            Assert.True(midAct.Has(AbyssBlessing.Resonance));   // whole run

            // Continued once act 3 has begun: the act-2 entries are gone.
            var later = NewModifier(act: 2);
            props.FillInternal(later);
            Assert.False(later.Has(AbyssBlessing.BattleRhythm));
            Assert.False(later.Has(AbyssShadow.ThornyGround));
            Assert.True(later.Has(AbyssBlessing.Resonance));
        }
        finally
        {
            initialized.SetValue(null, was);
        }
    }

    // ---- The page: both durations on every page ------------------------------------

    [Fact]
    public void Every_page_shows_a_whole_run_and_a_this_act_Blessing_while_both_remain()
    {
        var passedReturned = false;
        for (ulong seed = 1; seed <= 400; seed++)
        {
            var record = new AbyssRecord();
            for (var act = 0; act < 3; act++)
            {
                var offer = AbyssDraft.Offer(seed * 104729UL, act, record);
                Assert.Equal(3, offer.Options.Count);
                var left = AbyssDraft.AllBlessings.Except(record.Blessings).ToList();
                var durations = offer.Options.Select(o => AbyssDurations.Of(o.Blessing)).ToList();
                if (left.Any(b => AbyssDurations.Of(b) == AbyssDuration.ThisAct))
                {
                    Assert.Contains(AbyssDuration.ThisAct, durations);
                }
                if (left.Any(b => AbyssDurations.Of(b) == AbyssDuration.WholeRun))
                {
                    Assert.Contains(AbyssDuration.WholeRun, durations);
                }
                Assert.DoesNotContain(offer.Options, o => record.Has(o.Blessing));

                // Pick a Whole run one, so the This act ones are passed.
                var pick = offer.Options.ToList().FindIndex(o =>
                    AbyssDurations.Of(o.Blessing) == AbyssDuration.WholeRun);
                if (pick < 0) pick = 0;
                if (act > 0)
                {
                    var earlier = AbyssDraft.Offer(seed * 104729UL, act - 1, PrefixOf(record, act - 1));
                    passedReturned |= offer.Options.Any(o =>
                        AbyssDurations.Of(o.Blessing) == AbyssDuration.ThisAct
                        && earlier.Options.Any(e => e.Blessing == o.Blessing));
                }
                record.Record(act, offer.Options[pick].Blessing, offer.ShadowIfChosen(pick));
            }
        }
        // "A passed This act entry may return in a later act."
        Assert.True(passedReturned);
    }

    [Fact]
    public void The_mix_keeps_shuffled_order_and_falls_back_when_one_duration_is_gone()
    {
        var shuffled = new[]
        {
            AbyssBlessing.LeyLine, AbyssBlessing.AbyssalMoon, AbyssBlessing.FirstStrike,
            AbyssBlessing.Overflow, AbyssBlessing.Resonance,
        };
        Assert.Equal(new[] { AbyssBlessing.LeyLine, AbyssBlessing.AbyssalMoon, AbyssBlessing.Overflow },
                     AbyssDraft.MixedPage(shuffled, 3));

        var thisActFirst = new[]
        {
            AbyssBlessing.Overflow, AbyssBlessing.BattleRhythm, AbyssBlessing.MoonlitSpring,
            AbyssBlessing.LeyLine,
        };
        Assert.Equal(new[] { AbyssBlessing.Overflow, AbyssBlessing.BattleRhythm, AbyssBlessing.LeyLine },
                     AbyssDraft.MixedPage(thisActFirst, 3));

        var allWhole = new[] { AbyssBlessing.LeyLine, AbyssBlessing.Resonance, AbyssBlessing.FirstStrike };
        Assert.Equal(allWhole, AbyssDraft.MixedPage(allWhole, 3));
        Assert.Empty(AbyssDraft.MixedPage(allWhole, 0));
    }

    // ---- Each new Blessing --------------------------------------------------------

    [Fact]
    public void Overflow_doubles_a_players_reaction_damage_at_the_one_reaction_damage_seam()
    {
        Assert.Equal(2m, AbyssRules.OverflowFactor(dealerIsPlayer: true));
        Assert.Equal(1m, AbyssRules.OverflowFactor(dealerIsPlayer: false));
        Assert.Equal(1m, SpiralAbyss.OverflowFactor(null));

        // STRUCTURAL: the multiplier every reaction's own damage passes reads it.
        var seam = Il.Calls(typeof(global::KleeMod.Powers.CompanionOverhaulReactions)
            .GetMethod("DamageMultiplier", HeadlessGame.All)!);
        Assert.Contains("SpiralAbyss.OverflowFactor", seam);
    }

    [Fact]
    public void Vigor_adds_3_to_a_players_attacks_only_above_half_HP()
    {
        Assert.Equal(3m, AbyssRules.VigorDamageDelta(true, true, 41, 80, actTaken: 0));
        Assert.Equal(0m, AbyssRules.VigorDamageDelta(true, true, 40, 80, 0));   // exactly half
        Assert.Equal(0m, AbyssRules.VigorDamageDelta(true, false, 80, 80, 0));  // not an attack
        Assert.Equal(0m, AbyssRules.VigorDamageDelta(false, true, 80, 80, 0));  // an enemy
        // 3 / 4 / 5 by the act it was taken in (2026-10-18).
        Assert.Equal(4m, AbyssRules.VigorDamageDelta(true, true, 41, 80, actTaken: 1));
        Assert.Equal(5m, AbyssRules.VigorDamageDelta(true, true, 41, 80, actTaken: 2));

        // Through the real hook.
        var abyss = NewModifier(act: 0);
        var seat = Seat.Klee(maxHp: 80);
        Assert.Equal(0m, abyss.ModifyDamageAdditive(null, 6m, ValueProp.Move, seat.Creature, null, null));
        abyss.Record.Record(0, AbyssBlessing.VigorOfTheAbyss, AbyssShadow.Clock);
        Assert.Equal(3m, abyss.ModifyDamageAdditive(null, 6m, ValueProp.Move, seat.Creature, null, null));
        Assert.Equal(0m, abyss.ModifyDamageAdditive(null, 6m, ValueProp.Move | ValueProp.Unpowered, seat.Creature, null, null));
        Seat.Force(seat.Creature, "CurrentHp", 40);
        Assert.Equal(0m, abyss.ModifyDamageAdditive(null, 6m, ValueProp.Move, seat.Creature, null, null));
        Seat.Force(seat.Creature, "CurrentHp", 70);
        abyss.ActForTests = 1;   // the act ended
        Assert.Equal(0m, abyss.ModifyDamageAdditive(null, 6m, ValueProp.Move, seat.Creature, null, null));
    }

    [Fact]
    public void Moonlit_Spring_heals_5_and_stacks_with_Moonlit_Rest()
    {
        // Spring is 5 in every act (2026-10-18, round 3: 8 healed 70 to 80
        // HP in one act); Rest is 4 / 6 / 8 by the act it was taken in.
        Assert.Equal(new[] { 5, 5, 5 }, AbyssNumbers.MoonlitSpringHealByAct);
        Assert.Equal(5, AbyssRules.CombatEndHeal(moonlitRestAct: null, moonlitSpringAct: 0));
        Assert.Equal(9, AbyssRules.CombatEndHeal(0, 0));
        Assert.Equal(4, AbyssRules.CombatEndHeal(0, null));
        Assert.Equal(0, AbyssRules.CombatEndHeal(null, null));
        // Rest taken in act 1, Spring in act 3: 4 + 5.
        Assert.Equal(9, AbyssRules.CombatEndHeal(0, 2));
        Assert.Equal(13, AbyssRules.CombatEndHeal(2, 2));
        Assert.Contains("AbyssRules.CombatEndHeal",
            Il.Calls(typeof(SpiralAbyss).GetMethod(nameof(SpiralAbyss.AfterCombatVictory))!));
    }

    [Fact]
    public void No_retunes_the_first_eights_act_1_numbers_stand()
    {
        // 2026-10-18 moved no act 1 number.
        Assert.Equal(4, AbyssNumbers.AbyssalMoonDamage(0));
        Assert.Equal(8, AbyssNumbers.CrystallizeBlock(0));
        Assert.Equal(4, AbyssNumbers.MoonlitRestHeal(0));
    }

    [Fact]
    public void Battle_Rhythm_gives_1_Strength_and_1_Dexterity_at_combat_start()
    {
        Assert.Equal(new[] { 1, 2, 2 }, AbyssNumbers.BattleRhythmStrengthByAct);
        Assert.Equal(new[] { 1, 2, 2 }, AbyssNumbers.BattleRhythmDexterityByAct);
        var start = Il.CallSequence(typeof(SpiralAbyss).GetMethod(nameof(SpiralAbyss.AfterRoomEntered))!);
        Assert.Contains("PowerCmd.Apply<StrengthPower>", start);
        Assert.Contains("PowerCmd.Apply<DexterityPower>", start);
    }

    [Fact]
    public void Wavering_Moon_answers_a_players_reaction_from_the_one_reaction_site()
    {
        Assert.True(AbyssRules.WaveringMoonFires(dealerIsPlayer: true));
        Assert.False(AbyssRules.WaveringMoonFires(dealerIsPlayer: false));
        Assert.Equal(new[] { 3, 4, 5 }, AbyssNumbers.WaveringMoonDamageByAct);
        Assert.Contains("SpiralAbyss.NoteReaction",
            Il.Calls(Il.Method("ReactionEffects", "Resolve")));
        Assert.Contains("CreatureCmd.Damage",
            Il.Calls(typeof(SpiralAbyss).GetMethod("NoteReaction", HeadlessGame.All)!));
    }

    [Fact]
    public void Starfell_Draft_adds_a_card_to_card_rewards_only_ahead_of_the_clamp()
    {
        Assert.Equal(4, AbyssRules.StarfellDraftCount(3, isCardReward: true));
        Assert.Equal(3, AbyssRules.StarfellDraftCount(3, isCardReward: false));
        Assert.Equal(0, AbyssRules.StarfellDraftCount(0, isCardReward: true));

        var patch = typeof(SpiralAbyss).Assembly.GetType("KleeMod.Abyss.CardFactory_CreateForReward_StarfellDraft_Patch")!;
        var clamp = typeof(SpiralAbyss).Assembly.GetType("KleeMod.CardFactory_CreateForReward_Clamp_Patch")!;
        var target = patch.GetCustomAttribute<HarmonyPatch>()!.info;
        Assert.Equal(typeof(CardFactory), target.declaringType);
        Assert.Equal(nameof(CardFactory.CreateForReward), target.methodName);
        // Ahead of the reward clamp (default priority), so the clamp sees the
        // larger draw.
        Assert.True(patch.GetCustomAttribute<HarmonyPriority>()!.info.priority > Priority.Normal);
        Assert.Null(clamp.GetCustomAttribute<HarmonyPriority>());
        Assert.Contains("AbyssRules.StarfellDraftCount", Il.Calls(patch.GetMethod("Prefix", HeadlessGame.All)!));
    }

    // ---- Each new Shadow --------------------------------------------------------------

    [Fact]
    public void Frenzy_and_Thorny_Ground_put_powers_on_the_enemies_at_combat_start()
    {
        Assert.Equal(new[] { 2, 3, 4 }, AbyssNumbers.FrenzyStrengthByAct);
        Assert.Equal(new[] { 2, 2, 3 }, AbyssNumbers.ThornyGroundThornsByAct);
        Assert.Equal("This act, enemies start each combat with 2 Strength.", AbyssText.Text(AbyssShadow.Frenzy, 0));
        var start = Il.CallSequence(typeof(SpiralAbyss).GetMethod(nameof(SpiralAbyss.AfterRoomEntered))!);
        Assert.Contains("PowerCmd.Apply<ThornsPower>", start);
        Assert.Equal(2, start.Count(c => c == "PowerCmd.Apply<StrengthPower>"));   // Frenzy, Battle Rhythm
    }

    [Fact]
    public void Bulwark_gives_each_enemy_4_Block_at_the_start_of_every_player_turn()
    {
        // 2026-10-17: per turn, not once at combat start (the user: "Bulwark
        // looks pretty weak"; "4 is fine for now").
        Assert.Equal(new[] { 4, 6, 8 }, AbyssNumbers.BulwarkBlockByAct);
        var turn = Il.Calls(typeof(SpiralAbyss).GetMethod(nameof(SpiralAbyss.AfterSideTurnStart))!);
        Assert.Contains("CreatureCmd.GainBlock", turn);
        Assert.Equal("This act, at the start of your turn, each enemy gains 4 Block.",
                     AbyssText.Text(AbyssShadow.Bulwark, 0));
    }

    [Fact]
    public void Withering_weakens_the_players_at_combat_start()
    {
        Assert.Equal(1, AbyssNumbers.WitheringWeak);
        Assert.Equal(AbyssDuration.WholeRun, AbyssDurations.Of(AbyssShadow.Withering));
        var start = Il.CallSequence(typeof(SpiralAbyss).GetMethod(nameof(SpiralAbyss.AfterRoomEntered))!);
        Assert.Contains("PowerCmd.Apply<WeakPower>", start);
    }

    // ---- The display at act end -----------------------------------------------------

    [Fact]
    public void At_act_end_an_expired_Blessings_relic_goes_and_the_badges_drop_the_Shadow()
    {
        var record = new AbyssRecord();
        record.Record(0, AbyssBlessing.BattleRhythm, AbyssShadow.Riptide);
        record.Record(1, AbyssBlessing.StarfellDraft, AbyssShadow.Withering);

        var held = new List<RelicModel>
        {
            (RelicModel)RuntimeHelpers.GetUninitializedObject(typeof(AbyssBattleRhythmRelic)),
            (RelicModel)RuntimeHelpers.GetUninitializedObject(typeof(AbyssShadowsRelic)),
        };
        var remove = AbyssDisplay.BlessingRelicsToRemove(record.BlessingsInForce(1), held);
        Assert.Single(remove);
        Assert.IsType<AbyssBattleRhythmRelic>(remove[0]);
        Assert.Empty(AbyssDisplay.BlessingRelicsToRemove(record.BlessingsInForce(0), held));
        Assert.Equal(new[] { AbyssBlessing.StarfellDraft },
                     AbyssDisplay.BlessingsToGrant(record.BlessingsInForce(1), held));

        // The badges are drawn from the Shadows in force (Withering acts on
        // the player, so it badges the player).
        Assert.Equal(new[] { AbyssShadow.Withering },
                     AbyssDisplay.ShadowsToShow(false, true, record.ShadowsInForce(1), Array.Empty<PowerModel>()));

        // STRUCTURAL: the act-change hook brings every player's relics into line.
        Assert.Contains("AbyssDisplay.GrantTo",
            Il.Calls(typeof(SpiralAbyss).GetMethod(nameof(SpiralAbyss.AfterActEntered))!));
        Assert.Contains("RelicCmd.Remove", Il.Calls(typeof(AbyssDisplay).GetMethod(nameof(AbyssDisplay.GrantTo))!));
        Assert.Contains("AbyssDisplay.BlessingRelicsToRemove",
            Il.Calls(typeof(AbyssDisplay).GetMethod(nameof(AbyssDisplay.GrantTo))!));
    }

    // ---- The screen ---------------------------------------------------------------------

    [Fact]
    public void Cards_carry_their_duration_tags_and_the_strip_shows_only_what_is_in_force()
    {
        var offer = new AbyssOffer(1, new[]
        {
            new AbyssOption(AbyssBlessing.Overflow, AbyssShadow.Bulwark),
            new AbyssOption(AbyssBlessing.LeyLine, AbyssShadow.Withering),
            new AbyssOption(AbyssBlessing.StarfellDraft, AbyssShadow.Clock),
        }, 0);
        var record = new AbyssRecord();
        record.Record(0, AbyssBlessing.MoonlitSpring, AbyssShadow.Frenzy);   // act 1, This act both
        record.Record(1, AbyssBlessing.Resonance, AbyssShadow.Riptide);      // act 2: Riptide is This act

        var content = AbyssOverlayContent.For(offer, record);
        Assert.Equal(new[] { "This act", "Whole run", "Whole run" }, content.Cards.Select(c => c.BlessingTag));
        Assert.Equal(new[] { "This act", "Whole run", "Whole run" }, content.Cards.Select(c => c.ShadowTag));

        // Act 1's This act pair has dropped off; act 2's Riptide is shown.
        Assert.Equal(new[] { "Resonance" }, content.BlessingsTaken.Select(e => e.Name));
        Assert.Equal(new[] { "Riptide" }, content.ShadowsInForce.Select(e => e.Name));
        Assert.True(content.ShadowsInForce[0].ThisAct);
        Assert.EndsWith("[gold]This act[/gold]", content.ShadowsInForce[0].HoverText);
        Assert.EndsWith("[gold]Whole run[/gold]", content.BlessingsTaken[0].HoverText);

        var flow = new AbyssOverlayFlow();
        flow.Open();
        var json = AbyssOverlay.PageJson(content, flow);
        Assert.Contains("\"blessing_duration\":\"This act\"", json);
        Assert.Contains("\"shadow_duration\":\"Whole run\"", json);
    }

    [Fact]
    public void Every_new_entry_has_its_relic_badge_icon_and_strip_title()
    {
        var rows = AbyssChoicePage.LocRows();
        foreach (var b in AbyssDraft.AllBlessings)
        {
            var relic = (AbyssBlessingRelic)RuntimeHelpers.GetUninitializedObject(AbyssDisplay.RelicTypeFor(b));
            Assert.Equal(b, relic.Blessing);
            Assert.StartsWith("abyss/relics/", AbyssOverlayContent.BlessingIconFile(b));
            Assert.Equal(AbyssText.Name(b), rows[AbyssChoicePage.StripTitleKey(AbyssText.Name(b))]);
        }
        foreach (var s in AbyssDraft.AllShadows)
        {
            var badge = (AbyssShadowPower)RuntimeHelpers.GetUninitializedObject(AbyssDisplay.PowerTypeFor(s));
            Assert.Equal(s, badge.Shadow);
            Assert.StartsWith("abyss/powers/", badge.IconFile);
        }
    }

    // ---- Co-op ----------------------------------------------------------------------------

    [Fact]
    public void Coop_one_Blessing_one_rolled_Shadow_and_the_duration_follows_the_entry()
    {
        // Each player's copy of the shared event resolves the same option; the
        // record takes it once, and its durations are the entries' own.
        var abyss = NewModifier(act: 0);
        var offer = AbyssDraft.Offer(777UL, 0, abyss.Record);
        var pick = offer.Options.ToList().FindIndex(o => AbyssDurations.Of(o.Blessing) == AbyssDuration.ThisAct);
        Assert.True(pick >= 0);
        var shadow = offer.ShadowIfChosen(pick);
        Assert.True(abyss.Record.Record(0, offer.Options[pick].Blessing, shadow));
        Assert.False(abyss.Record.Record(0, offer.Options[pick].Blessing, shadow));
        Assert.Single(abyss.Record.Blessings);
        Assert.True(abyss.Has(offer.Options[pick].Blessing));
        abyss.ActForTests = 1;
        Assert.False(abyss.Has(offer.Options[pick].Blessing));
    }

    // ---- Helpers -----------------------------------------------------------------------------

    private static AbyssRecord PrefixOf(AbyssRecord record, int beforeAct)
    {
        var copy = new AbyssRecord();
        for (var i = 0; i < record.Acts.Count; i++)
        {
            if (record.Acts[i] < beforeAct) copy.Record(record.Acts[i], record.Blessings[i], record.Shadows[i]);
        }
        return copy;
    }
    // ---- Reaction Blessings: only with an elemental player (2026-10-18) -----

    [Fact]
    public void Reaction_Blessings_are_offered_only_when_a_player_can_react()
    {
        Assert.Equal(new[] { AbyssBlessing.Overflow, AbyssBlessing.WaveringMoon }, AbyssDraft.ReactionBlessings);

        // The mod's five characters can trigger a reaction; base-game classes cannot.
        foreach (var t in new[] { typeof(Klee), typeof(Kokomi), typeof(Furina), typeof(Varka), typeof(Yae) })
        {
            Assert.True(AbyssDraft.CanReact(RuntimeHelpers.GetUninitializedObject(t)), t.Name);
        }
        Assert.False(AbyssDraft.CanReact(new MegaCrit.Sts2.Core.Models.Characters.Ironclad()));
        Assert.False(AbyssDraft.CanReact(null));

        var sawReaction = false;
        for (ulong seed = 1; seed <= 300; seed++)
        {
            var filtered = new AbyssRecord();
            var open = new AbyssRecord();
            for (var act = 0; act < 3; act++)
            {
                var page = AbyssDraft.Offer(seed * 7919UL, act, filtered, anyElementalPlayer: false);
                // Drawn from the rest of the pool: still a full, mixed page.
                Assert.Equal(3, page.Options.Count);
                Assert.DoesNotContain(page.Options, o => AbyssDraft.ReactionBlessings.Contains(o.Blessing));
                // Deterministic from the seed.
                Assert.Equal(page.Options, AbyssDraft.Offer(seed * 7919UL, act, filtered, false).Options);
                Assert.Equal(page.ShadowRoll, AbyssDraft.Offer(seed * 7919UL, act, filtered, false).ShadowRoll);

                // With an elemental player nothing is filtered: the page is the
                // unfiltered draw, so an elemental run's saved page is unchanged.
                var elemental = AbyssDraft.Offer(seed * 7919UL, act, open, anyElementalPlayer: true);
                var legacy = AbyssDraft.Offer(seed * 7919UL, act, open.Blessings, open.Shadows);
                Assert.Equal(legacy.Options, elemental.Options);
                Assert.Equal(legacy.ShadowRoll, elemental.ShadowRoll);
                sawReaction |= elemental.Options.Any(o => AbyssDraft.ReactionBlessings.Contains(o.Blessing));

                filtered.Record(act, page.Options[0].Blessing, page.ShadowIfChosen(0));
                open.Record(act, elemental.Options[0].Blessing, elemental.ShadowIfChosen(0));
            }
        }
        Assert.True(sawReaction);

        // STRUCTURAL: the choice page asks the run's players.
        var install = Il.Calls(typeof(AbyssChoicePage).GetMethod("Install", HeadlessGame.All)!);
        Assert.Contains("AbyssDraft.Offer", install);
    }
}
