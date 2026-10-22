using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using BaseLib.Abstracts;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE INAZUMA COMPANION OVERHAUL -- on the arm's existing flag (sim twin
/// <c>tier0/tests/test_inazuma_companion_overhaul.py</c>). Gorou's three are
/// Kokomi's own cards; the Universals are the Inazuma pool rework's
/// thirty-four (2026-10-18, <c>review/active/inazuma-companions-2026-10-18.md</c>).
///
/// WHAT IS REAL HERE AND WHAT IS STRUCTURAL, on the terms
/// <c>CompanionOverhaulHookTests</c> sets: a PURE reader can be called
/// headlessly against a <see cref="Seat"/> holding real powers and is asserted
/// for real; RESOLUTION cannot (<c>PowerCmd</c>, <c>ElementalHit</c> and a live
/// <c>CombatState</c> are outside the headless boundary), so the firing ORDER
/// and the mutating halves are pinned off the compiled method and labelled
/// STRUCTURAL. The arithmetic those hooks perform is asserted for real in the
/// sim twin, against the same constants.
/// </summary>
public class InazumaCompanionOverhaulTests
{
    private const BindingFlags All = HeadlessGame.All;

    private static ValueProp Attack => ValueProp.Move;   // IsPoweredAttack()

    /// <summary>Gorou's three (Kokomi's own since the re-founding) and the
    /// thirty-four Universals of the Inazuma pool rework (2026-10-18), in
    /// the roster's order.</summary>
    private static readonly Type[] Rows =
    {
        typeof(ProtoMiGorouInuzaka),
        typeof(ProtoMiGorouWarBanner),
        typeof(ProtoMiGorouJuuga),
        typeof(ProtoMiSayuFuuinDash),
        typeof(ProtoMiSayuDaruma),
        typeof(ProtoMiSayuNaptime),
        typeof(ProtoMiShinobuSanctifyingRing),
        typeof(ProtoMiShinobuGrassRing),
        typeof(ProtoMiShinobuThundergrust),
        typeof(ProtoMiThomaBlazingBarrier),
        typeof(ProtoMiThomaCrimsonOoyoroi),
        typeof(ProtoMiSaraCrowfeatherCover),
        typeof(ProtoMiSaraTenguStormcall),
        typeof(ProtoMiKazuhaSlash),
        typeof(ProtoMiYaeSesshouSakura),
        typeof(ProtoMiAyakaSoumetsu),
        typeof(ProtoMiAyakaHyouka),
        typeof(ProtoMiAyatoKyouka),
        typeof(ProtoMiHeizouHeartstopper),
        typeof(ProtoMiHeizouWindmusterKick),
        typeof(ProtoMiKiraraSurpriseDispatch),
        typeof(ProtoMiMizukiAnraku),
        typeof(ProtoMiMizukiAisaUtamakura),
        typeof(ProtoMiChioriHasode),
        typeof(ProtoMiIttoUshi),
        typeof(ProtoMiRaidenEuthymia),
        typeof(ProtoMiRaidenMusouNoHitotachi),
        typeof(ProtoMiIttoRoyalDescent),
        typeof(ProtoMiYoimiyaNiwabi),
        typeof(ProtoMiKazuhaChihayaburu),
        typeof(ProtoMiWandererHanega),
        typeof(ProtoMiAyatoKyoukaFuushi),
        typeof(ProtoMiKiraraMeowteorKick),
        typeof(ProtoMiYoimiyaRyuukinSaxifrage),
        typeof(ProtoMiWandererKyougen),
        typeof(ProtoMiChioriTwinBlades),
        typeof(ProtoMiYaeSacredSakurasFavor),
    };

    /// <summary>The powers the arm adds, by class, since the Inazuma pool
    /// rework (2026-10-18).</summary>
    private static readonly Type[] NewPowers =
    {
        typeof(JuugaPower),
        typeof(SanctifyingRingPower), typeof(BlazingBarrierPower),
        typeof(CrimsonOoyoroiPower), typeof(CrowfeatherCoverPower),
        typeof(NextAttackElectroPower), typeof(SesshouSakuraPower),
        typeof(SoumetsuPower), typeof(SurpriseDispatchPower),
        typeof(PlaneOfEuthymiaPower), typeof(RoyalDescentPower),
        typeof(NiwabiFireDancePower), typeof(ChihayaburuPower),
        typeof(HanegaPower),
        typeof(TwinBladesPower), typeof(SacredSakurasFavorPower),
    };

    /// <summary>The ones whose stack is a marker rather than a number.</summary>
    private static readonly Type[] SinglePowers =
    {
        typeof(NextAttackElectroPower), typeof(PlaneOfEuthymiaPower),
        typeof(NiwabiFireDancePower), typeof(SacredSakurasFavorPower),
    };

    // ---- THE ROWS -------------------------------------------------------

    [Fact]
    public void The_rows_are_offerable_inazuma_companions()
    {
        Assert.Equal(37, Rows.Length);
        foreach (var type in Rows)
        {
            var card = (CardModel)Activator.CreateInstance(type)!;
            var comp = Assert.IsAssignableFrom<ICompanionCard>(card);
            Assert.Equal("inazuma", comp.Nation);
            Assert.Null(comp.PersonalPool);     // no Personal, no stand-in
            Assert.True(comp.Star == 4 || comp.Star == 5,
                $"{type.Name}: star {comp.Star}");
            Assert.NotEqual(CardRarity.Basic, card.Rarity);
        }
    }

    [Fact]
    public void The_rarity_split_is_the_reworks()
    {
        // The Inazuma pool rework (2026-10-18), grown to two cards a
        // character: 8 Common, 16 Uncommon, 10 Rare Universals, plus Gorou's
        // two Commons and one Uncommon. 8 / 15 / 11 since Baleful Omen
        // (Uncommon) gave way to Musou no Hitotachi (Rare), 2026-10-19.
        var byRarity = Rows
            .Select(t => ((CardModel)Activator.CreateInstance(t)!).Rarity)
            .GroupBy(r => r)
            .ToDictionary(g => g.Key, g => g.Count());
        Assert.Equal(8 + 2, byRarity[CardRarity.Common]);
        Assert.Equal(15 + 1, byRarity[CardRarity.Uncommon]);
        Assert.Equal(11, byRarity[CardRarity.Rare]);
    }

    [Fact]
    public void The_roster_replaces_two_nations_and_carries_both_workshops()
    {
        // The compiler already holds the roster -> class direction (a deleted
        // row stops the build); this is the count, and the acceptance
        // condition for "no row was left out".
        var inazuma = Il.Method("CompanionOverhaulRoster", "InazumaUniversals");
        var referenced = Il.CallSequence(inazuma)
            .Count(c => c.StartsWith("ModelDb.Card"));
        // 21 since the Kokomi re-founding (2026-10-12): Gorou's three are her
        // own cards. 34 since the Inazuma pool rework (2026-10-18).
        Assert.Equal(34, referenced);

        var mondstadt = Il.Method("CompanionOverhaulRoster", "Universals");
        // 35 since the AoE trim (2026-10-03) split Durin in two; 39 since the
        // Klee-only companions (2026-10-03) added four shared rows.
        Assert.Equal(39, Il.CallSequence(mondstadt)
            .Count(c => c.StartsWith("ModelDb.Card")));
    }

    [Fact]
    public void The_plan_lines_are_the_three_reworked_cards()
    {
        // The Inazuma pool rework (2026-10-18): Naptime, Daruma and Kirara
        // print a Plan line, on the Universal rows the off-character sweep
        // lets any seat plan.
        var naptime = Assert.IsAssignableFrom<IPlannedCard>(new ProtoMiSayuNaptime());
        Assert.Equal(new[] { KokomiPlan.Kind.Block, KokomiPlan.Kind.Draw },
                     naptime.PlanClauses.Select(c => c.Kind));
        var daruma = Assert.IsAssignableFrom<IPlannedCard>(new ProtoMiSayuDaruma());
        Assert.Equal(new[] { KokomiPlan.Kind.Energy, KokomiPlan.Kind.Block },
                     daruma.PlanClauses.Select(c => c.Kind));
        var kirara = Assert.IsAssignableFrom<IPlannedCard>(new ProtoMiKiraraSurpriseDispatch());
        var clause = Assert.Single(kirara.PlanClauses);
        Assert.Equal(KokomiPlan.Kind.Block, clause.Kind);
        Assert.Equal(14, clause.Amount);
        // Kyouka Fuushi, the rework's Plan Rare: 7 three times, plus the
        // earlier Plans.
        var fuushi = Assert.IsAssignableFrom<IPlannedCard>(new ProtoMiAyatoKyoukaFuushi());
        var hit = Assert.Single(fuushi.PlanClauses);
        Assert.Equal(KokomiPlan.Kind.DamageTimesPlusEarlierPlans, hit.Kind);
        Assert.Equal((7, 3, KokomiPlan.Aim.FrontEnemy), (hit.Amount, hit.Times, hit.Aim));
    }

    [Fact]
    public void Kiraras_two_rows_are_the_ones_that_declare_no_element()
    {
        // She is Dendro; this engine has six elements and no Dendro aura, and
        // her card names no element at all. Element.None is the honest
        // rendering -- inventing one of the six would be a design decision
        // wearing a schema default.
        var kirara = (ICompanionCard)Activator.CreateInstance(
            typeof(ProtoMiKiraraSurpriseDispatch))!;
        Assert.Equal(Element.None, kirara.CompanionElement);
        Assert.Equal(Element.None, ((ICompanionCard)new ProtoMiKiraraMeowteorKick()).CompanionElement);
        foreach (var type in Rows.Where(
                     t => t != typeof(ProtoMiKiraraSurpriseDispatch)
                          && t != typeof(ProtoMiKiraraMeowteorKick)))
        {
            var comp = (ICompanionCard)Activator.CreateInstance(type)!;
            Assert.NotEqual(Element.None, comp.CompanionElement);
        }
    }

    [Fact]
    public void The_war_banner_gains_block_and_plans_permanent_strength()
    {
        // The Kokomi level pass (2026-10-12): "Gain 7 [10] Block. Or plan:
        // Gain 1 [2] Strength." Its Dexterity clock (`WarBannerPower`) left
        // with the old face. The Kokomi balance audit (ruled 2026-10-21):
        // the upgrade adds Block only, so the Plan is 1 Strength upgraded too.
        var play = typeof(ProtoMiGorouWarBanner).GetMethod("PlayNowLine", All)!;
        var calls = Il.CallSequence(play);
        Assert.DoesNotContain(calls, c => c.StartsWith("PowerCmd.Apply"));
        Assert.Contains(calls, c => c.Contains("GainBlock"));
        Assert.Null(typeof(KokomiPlan).Assembly.GetTypes()
            .FirstOrDefault(t => t.Name == "WarBannerPower"));
        var clause = Assert.Single(new ProtoMiGorouWarBanner().PlanClauses);
        Assert.Equal(KokomiPlan.Kind.GainStrength, clause.Kind);
        Assert.Equal(1, clause.Amount);
        var up = new ProtoMiGorouWarBanner();
        Seat.Set(up, "IsMutable", true);
        typeof(MegaCrit.Sts2.Core.Models.CardModel)
            .GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(up, Array.Empty<object?>());
        Assert.Equal(1, Assert.Single(up.PlanClauses).Amount);
    }

    [Fact]
    public void Shinobus_ring_is_paid_in_plain_hp_and_not_in_exert()
    {
        // "Lose 3 HP" is plain HP loss. This engine spells that
        // Unblockable|Unpowered self-damage -- the shipped Hot Hands line --
        // and NOT `exert`, which is Kokomi's rule and is eaten by Block.
        var play = typeof(ProtoMiShinobuSanctifyingRing).GetMethod("OnPlay", All)!;
        var calls = Il.Calls(play);
        Assert.Contains(calls, c => c.Contains("CreatureCmd.Damage"));
        Assert.DoesNotContain(calls, c => c.Contains("KokomiRules.Exert"));
    }

    // --- Grass Ring of Sanctification: "since your last turn" (2026-09-23) --

    [Fact]
    public void The_grass_ring_reads_hp_lost_since_your_last_turn()
    {
        // [USER] 2026-09-23: "agreed on a)". "If you lost HP this turn" read a
        // window that opened at the top of the player's turn, so the enemy
        // turn was wiped before any card could ask and the clause never paid
        // on the player's own turn. The face and the read both moved.
        var card = new ProtoMiShinobuGrassRing();
        var face = card.Localization!.First(r => r.Item1 == "description").Item2;
        Assert.Contains("If you lost HP since your last turn", face);
        Assert.DoesNotContain("this turn", face);

        var calls = Il.Calls(typeof(ProtoMiShinobuGrassRing).GetMethod("OnPlay", All)!);
        Assert.Contains(calls, c => c.EndsWith("HpLossWindow.LostSinceLastTurn",
                                               StringComparison.Ordinal));
        Assert.DoesNotContain(calls, c => c.Contains("HpLostThisTurn"));
    }

    [Fact]
    public void The_window_counts_the_enemy_turn_and_opens_when_your_turn_ends()
    {
        // REAL: the window on a real Klee seat, through the listener's own
        // hook (any character, not only Furina, whose funnel fed the old
        // read). The hook touches no instance state, so an uninitialised
        // instance is the canonical one for this purpose.
        var hooks = (KleeElementalHooks)System.Runtime.CompilerServices
            .RuntimeHelpers.GetUninitializedObject(typeof(KleeElementalHooks));
        var klee = Seat.Klee().Creature;
        HpLossWindow.ResetAtTurnEnd(klee);                 // her turn ended
        Assert.False(HpLossWindow.LostSinceLastTurn(klee));

        // The enemy turn hits her for 5: a negative HP delta.
        hooks.AfterCurrentHpChanged(klee, -5m).GetAwaiter().GetResult();
        Assert.True(HpLossWindow.LostSinceLastTurn(klee));
        Assert.Equal(5, HpLossWindow.LostAmount(klee));

        // Healing is not loss.
        hooks.AfterCurrentHpChanged(klee, 3m).GetAwaiter().GetResult();
        Assert.Equal(5, HpLossWindow.LostAmount(klee));

        // Her next turn ends: the next window opens empty.
        HpLossWindow.ResetAtTurnEnd(klee);
        Assert.False(HpLossWindow.LostSinceLastTurn(klee));
    }

    [Fact]
    public void The_window_resets_at_the_players_turn_end_and_at_combat_start()
    {
        // STRUCTURAL: the lifecycle broadcasts need a live combat. Reset at
        // AfterSideTurnEnd (after every end-of-turn effect), cleared at
        // BeforeCombatStart so turn one counts from the start of combat, and
        // fed from AfterCurrentHpChanged. Sim twin: the end of
        // `combat._player_turn`, and `resources.note_player_hp_loss`.
        Assert.Contains(Il.Calls(Il.Method("KleeElementalHooks", "AfterSideTurnEnd")),
                        c => c.EndsWith("HpLossWindow.ResetAtTurnEnd",
                                        StringComparison.Ordinal));
        Assert.Contains(Il.Calls(Il.Method("KleeElementalHooks", "BeforeCombatStart")),
                        c => c.EndsWith("HpLossWindow.ClearAll",
                                        StringComparison.Ordinal));
        Assert.Contains(Il.Calls(Il.Method("KleeElementalHooks", "AfterCurrentHpChanged")),
                        c => c.EndsWith("HpLossWindow.Note",
                                        StringComparison.Ordinal));
    }

    [Fact]
    public void Mizukis_snack_hits_and_mends_whatever_the_hp()
    {
        // The 2026-10-11 Companion pass: "Swirl ALL enemies. Deal 14 damage
        // to ALL enemies and Mend 6." Both halves, no 70% branch.
        var calls = Il.Calls(typeof(ProtoMiMizukiAnraku).GetMethod("OnPlay", All)!);
        Assert.Contains(calls, c => c.Contains("DamageCmd.Attack"));
        Assert.Contains(calls, c => c.Contains("KokomiRules.Mend"));
        Assert.DoesNotContain(calls, c => c.Contains("get_CurrentHp"));
        var card = new ProtoMiMizukiAnraku();
        var face = ((BaseLib.Abstracts.ILocalizationProvider)card).Localization!
            .Single(r => r.Item1 == "description").Item2;
        Assert.Equal("[gold]Swirl[/gold] ALL enemies. Deal "
                   + "{CalculatedDamage:diff()} damage to ALL enemies and "
                   + "[gold]Mend[/gold] 6{InCombat: ({MendLands} will "
                   + "land)|}.", face);
        Assert.Equal(2, card.EnergyCost.Canonical);
    }

    [Fact]
    public void Mizukis_snack_is_the_one_row_that_mends()
    {
        // And it goes through KokomiRules.Mend -- the ONE place "never above
        // the HP you entered the fight with" is written. A second Mend for the
        // companion pool is exactly what this asserts did not happen.
        var play = typeof(ProtoMiMizukiAnraku).GetMethod("OnPlay", All)!;
        Assert.Contains(Il.Calls(play), c => c.Contains("KokomiRules.Mend"));

        foreach (var type in Rows.Where(t => t != typeof(ProtoMiMizukiAnraku)))
        {
            var other = type.GetMethod("OnPlay", All);
            if (other == null) continue;
            Assert.DoesNotContain(Il.Calls(other),
                c => c.Contains("KokomiRules.Mend"));
        }
    }

    [Fact]
    public void Mend_asks_whether_either_arm_is_live_for_this_creature()
    {
        // THE ONE LINE THAT MOVED for the companion arm. The rule below it is
        // unchanged and unduplicated; what widened is the gate, because
        // Mizuki's row is a UNIVERSAL and Klee or Furina can draft it.
        // Through `MendWouldLand` since the Kokomi review r6 (2026-10-14).
        var mend = Il.Method("KokomiRules", "MendWouldLand");
        Assert.Contains(Il.Calls(mend), c => c.Contains("MendIsLive"));

        var live = Il.Method("KokomiRules", "MendIsLive");
        var calls = Il.Calls(live);
        Assert.Contains(calls, c => c.Contains("KokomiOverhaul.LiveFor"));
    }

    [Fact]
    public void Gorou_opens_the_play_total_before_he_banks_half_of_it()
    {
        // The ledger has to start at zero when the play does, or the card
        // banks the last card's damage. Emitted only for a row that asks --
        // the same arrangement Kokomi's `BeginPlay` has.
        // Her own two-line card since the re-founding (2026-10-12): the
        // printed effect is the now-line.
        var play = typeof(ProtoMiGorouInuzaka).GetMethod("PlayNowLine", All)!;
        var sequence = Il.CallSequence(play).ToList();
        var open = sequence.FindIndex(c => c.Contains("BeginPlay"));
        var bank = sequence.FindIndex(c => c.Contains("BlockHalfDamage"));
        Assert.True(open >= 0, "the play total is never opened");
        Assert.True(bank > open, "the half is banked before the play opens");

        foreach (var type in Rows.Where(t => t != typeof(ProtoMiGorouInuzaka)))
        {
            var other = type.GetMethod("OnPlay", All);
            if (other == null) continue;
            Assert.DoesNotContain(Il.Calls(other),
                c => c.Contains("CompanionOverhaulLedger") && c.Contains("BeginPlay"));
        }
    }

    [Fact]
    public void Chiori_is_the_one_card_attack_that_ignores_block()
    {
        // STRUCTURAL: "This ignores Block." is `IgnoringBlock()` on the
        // card's own attack (`ValueProp.Unblockable`), and no other row asks.
        var play = typeof(ProtoMiChioriHasode).GetMethod("OnPlay", All)!;
        Assert.Contains(Il.Calls(play), c => c.Contains("IgnoringBlock"));
        foreach (var type in Rows.Where(t => t != typeof(ProtoMiChioriHasode)))
        {
            var other = type.GetMethod("OnPlay", All);
            if (other == null) continue;
            Assert.DoesNotContain(Il.Calls(other), c => c.Contains("IgnoringBlock"));
        }
    }

    [Fact]
    public void Ignoring_block_sets_unblockable_and_keeps_the_attack_powered()
    {
        var command = MegaCrit.Sts2.Core.Commands.DamageCmd.Attack(5m).IgnoringBlock();
        Assert.True(command.DamageProps.HasFlag(ValueProp.Unblockable));
        Assert.True(command.DamageProps.HasFlag(ValueProp.Move));
        Assert.False(command.DamageProps.HasFlag(ValueProp.Unpowered));
    }

    // ---- THE POWERS -----------------------------------------------------

    [Fact]
    public void Every_new_power_is_a_counter_but_the_markers()
    {
        foreach (var type in NewPowers)
        {
            var power = (PowerModel)Activator.CreateInstance(type)!;
            Assert.Equal(SinglePowers.Contains(type)
                             ? PowerStackType.Single : PowerStackType.Counter,
                         power.StackType);
        }
    }

    [Fact]
    public void Every_new_power_is_a_buff()
    {
        foreach (var type in NewPowers)
        {
            Assert.Equal(PowerType.Buff,
                ((PowerModel)Activator.CreateInstance(type)!).Type);
        }
    }

    [Theory]
    // (`EB-415` took the War Banner's row off this list; its power left with
    // the Kokomi level pass, 2026-10-12.)
    [InlineData(typeof(JuugaPower), CompanionOverhaulLaw.JuugaDamage)]
    [InlineData(typeof(SanctifyingRingPower), CompanionOverhaulLaw.SanctifyingRingDamage)]
    [InlineData(typeof(BlazingBarrierPower), CompanionOverhaulLaw.BlazingBarrierBlock)]
    [InlineData(typeof(SesshouSakuraPower), CompanionOverhaulLaw.SakuraDamage)]
    // The 2026-09-25 text pass prints the later Sakura's whole hit (base
    // plus bonus, which is what `FireVolley` deals) rather than the bonus.
    [InlineData(typeof(SesshouSakuraPower),
                CompanionOverhaulLaw.SakuraDamage + CompanionOverhaulLaw.SakuraBonus)]
    [InlineData(typeof(SoumetsuPower), CompanionOverhaulLaw.SoumetsuDamage)]
    [InlineData(typeof(SoumetsuPower), CompanionOverhaulLaw.SoumetsuFinale)]
    [InlineData(typeof(SurpriseDispatchPower), CompanionOverhaulLaw.SurpriseDispatchDamage)]
    [InlineData(typeof(HanegaPower), CompanionOverhaulLaw.HanegaBlockLoss)]
    // `EB-463` / `EB-565` TOOK TWO ROWS OFF THIS LIST, and neither number
    // moved: `TamotoPower` (retired 2026-10-18) and `BaronBunnyPower` print `{Damage}`, a var
    // seeded from the same `CompanionOverhaulLaw` constant and rewritten at
    // PLAY with the card's Guest Cast fold on it. The face and the hit still
    // read one number -- `SummonDamageTests` is where that is pinned, because
    // the number a `Localization` row prints is now a hole rather than a
    // literal.
    public void Every_power_face_prints_the_number_it_pays(Type type, int number)
    {
        // FACE FROM BODY at the power level: the description interpolates the
        // CompanionOverhaulLaw constant the hook spends, so a retune moves
        // both or neither.
        var power = (ILocalizationProvider)Activator.CreateInstance(type)!;
        var description = power.Localization!
            .Single(entry => entry.Item1 == "description").Item2;
        Assert.Contains(number.ToString(), description);
    }

    // ---- THE PURE READERS, FOR REAL -------------------------------------

    [Fact]
    public void Crowfeather_pays_and_stacks_with_mondstadts_riders()
    {
        var seat = Seat.Klee()
            .WithPower<PassionOverloadPower>(4)
            .WithPower<LightningFangPower>(2)
            .WithPower<CrowfeatherCoverPower>(4)
            .WithPower<NextAttackElectroPower>(1);
        var card = new ProtoMiShinobuThundergrust();
        var target = Seat.Klee().Creature;      // any body that is not us
        var total = seat.Creature.Powers
            .Sum(p => p.ModifyDamageAdditive(
                target, 10m, Attack, seat.Creature, card, null));
        // The Electro rider adds no damage.
        Assert.Equal(4 + CompanionOverhaulLaw.LightningFangDamage + 4, total);
    }

    [Fact]
    public void A_new_rider_pays_nothing_on_a_skill_or_someone_elses_hit()
    {
        var seat = Seat.Klee().WithPower<CrowfeatherCoverPower>(4);
        var power = seat.Creature.Powers.OfType<CrowfeatherCoverPower>().Single();
        var other = Seat.Klee().Creature;
        var skill = new ProtoMiThomaBlazingBarrier();        // a Skill
        Assert.Equal(0m, power.ModifyDamageAdditive(
            other, 10m, Attack, seat.Creature, skill, null));
        var attack = new ProtoMiShinobuThundergrust();
        Assert.Equal(0m, power.ModifyDamageAdditive(
            other, 10m, Attack, other, attack, null));       // not our hit
        Assert.Equal(0m, power.ModifyDamageAdditive(
            other, 10m, ValueProp.Unpowered, seat.Creature, attack, null));
    }

    [Fact]
    public void The_electro_rider_claims_the_element_of_the_next_attack()
    {
        // Tengu Stormcall's and Baleful Omen's rider (2026-10-18), at
        // Crowfeather's one-shot tier: it wins over a blanket.
        var card = new ProtoMiAyakaHyouka();                  // prints Cryo
        var plain = Seat.Klee();
        Assert.Equal(Element.Cryo,
            CompanionOverhaulRiders.ElementFor(card, plain.Creature));
        var rider = Seat.Klee().WithPower<NextAttackElectroPower>(1);
        Assert.Equal(Element.Electro,
            CompanionOverhaulRiders.ElementFor(card, rider.Creature));
        var fang = Seat.Klee()
            .WithPower<LightningFangPower>(2)
            .WithPower<PassionOverloadPower>(4);
        Assert.Equal(Element.Pyro,
            CompanionOverhaulRiders.ElementFor(card, fang.Creature));
        var both = Seat.Klee()
            .WithPower<PassionOverloadPower>(4)
            .WithPower<NextAttackElectroPower>(1);
        Assert.Equal(Element.Electro,
            CompanionOverhaulRiders.ElementFor(card, both.Creature));
    }

    // ---- THE REWORK'S RARE POWERS (2026-10-18), the pure readers ---------

    private static T Owned<T>(Seat seat) where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        Seat.Set(card, "Owner", seat.Player);
        return card;
    }

    [Fact]
    public void Euthymia_refuses_the_flush_for_its_owner_only()
    {
        var seat = Seat.Klee().WithPower<PlaneOfEuthymiaPower>(1);
        var power = seat.Creature.Powers.OfType<PlaneOfEuthymiaPower>().Single();
        Assert.False(power.ShouldFlush(seat.Creature.Player!));
        Assert.True(power.ShouldFlush(Seat.Klee().Creature.Player!));
    }

    [Fact]
    public void Royal_descent_pays_on_an_attack_that_dealt_no_damage()
    {
        Assert.True(RoyalDescentPower.DealtNoDamage(new[] { 0 }));
        Assert.True(RoyalDescentPower.DealtNoDamage(new[] { 0, 0, 0 }));
        Assert.False(RoyalDescentPower.DealtNoDamage(new[] { 0, 3, 0 }));
        Assert.False(RoyalDescentPower.DealtNoDamage(System.Array.Empty<int>()));
    }

    [Fact]
    public void Hanega_takes_three_off_card_block_and_nothing_else()
    {
        var seat = Seat.Klee().WithPower<HanegaPower>(2);
        var power = seat.Creature.Powers.OfType<HanegaPower>().Single();
        // Owned by this seat, so the card is "a card that gives you Block".
        var defend = Owned<ProtoMiThomaBlazingBarrier>(seat);
        // Two copies: 3 less each (the review, 2026-10-18).
        Assert.Equal(-2 * CompanionOverhaulLaw.HanegaBlockLoss,
            power.ModifyBlockAdditive(seat.Creature, 6m, ValueProp.Move, defend, null));
        Assert.Equal(6, HanegaPower.BlockLoss(2));
        // Power and relic Block (no card source, or unpowered) are untouched.
        Assert.Equal(0m, power.ModifyBlockAdditive(
            seat.Creature, 6m, ValueProp.Move, null, null));
        Assert.Equal(0m, power.ModifyBlockAdditive(
            seat.Creature, 6m, ValueProp.Unpowered, defend, null));
    }

    [Fact]
    public void Ooyoroi_prevents_the_block_clear_for_its_owner_only()
    {
        var seat = Seat.Klee().WithPower<CrimsonOoyoroiPower>(6);
        var power = seat.Creature.Powers.OfType<CrimsonOoyoroiPower>().Single();
        Assert.False(power.ShouldClearBlock(seat.Creature));
        Assert.True(power.ShouldClearBlock(Seat.Klee().Creature));
    }

    [Fact]
    public void Niwabi_doubles_an_attack_only_while_none_was_played_this_turn()
    {
        var seat = Seat.Klee().WithCombatState().WithPower<NiwabiFireDancePower>(1);
        var power = seat.Creature.Powers.OfType<NiwabiFireDancePower>().Single();
        var attack = Owned<ProtoMiShinobuThundergrust>(seat);
        var skill = Owned<ProtoMiThomaBlazingBarrier>(seat);
        Assert.Equal(2, power.ModifyCardPlayCount(attack, null, 1));
        Assert.Equal(1, power.ModifyCardPlayCount(skill, null, 1));
        CompanionOverhaulLedger.For(seat.Creature).NoteAttack();
        Assert.Equal(1, power.ModifyCardPlayCount(attack, null, 1));
        CompanionOverhaulLedger.ResetAll();
    }

    [Fact]
    public void Chihayaburu_draws_at_the_one_swirl_site()
    {
        var note = Il.Method("CompanionOverhaulReactions", "Note");
        var sequence = Il.CallSequence(note).ToList();
        var swirl = sequence.FindIndex(c => c.Contains("NoteSwirl"));
        var draw = sequence.FindIndex(c => c.Contains("ChihayaburuPower.OnSwirl"));
        Assert.True(swirl >= 0 && draw > swirl,
            "Chihayaburu reads the Swirl the ledger has just counted");
    }

    [Fact]
    public void The_ledger_counts_swirls_and_a_plays_damage_and_rolls_both()
    {
        var seat = Seat.Klee().WithCombatState();
        var ledger = CompanionOverhaulLedger.For(seat.Creature);
        ledger.BeginPlay();
        ledger.NoteDamage(7);
        ledger.NoteDamage(0);                 // a blocked hit banks nothing
        ledger.NoteDamage(5);
        Assert.Equal(12, ledger.DamageDealtThisPlay);
        ledger.BeginPlay();
        Assert.Equal(0, ledger.DamageDealtThisPlay);

        ledger.NoteSwirl();
        ledger.NoteSwirl();
        Assert.Equal(2, ledger.SwirlsThisTurn);
        ledger.NoteDamage(9);
        ledger.RollTo(ledger.GetHashCode());  // any round that is not this one
        Assert.Equal(0, ledger.SwirlsThisTurn);
        Assert.Equal(0, ledger.DamageDealtThisPlay);
        CompanionOverhaulLedger.ResetAll();
    }

    [Fact]
    public void The_swirl_count_is_taken_at_the_one_reaction_site()
    {
        // Beside Varka's latch, off the same event, so "a Swirl happened" has
        // one definition in this engine and the two readers cannot disagree.
        var note = Il.Method("CompanionOverhaulReactions", "Note");
        Assert.Contains(Il.Calls(note), c => c.Contains("NoteSwirl"));
    }

    // ---- THE ORDER IS LAW ------------------------------------------------

    [Fact]
    public void The_end_of_turn_walk_runs_the_inazuma_block_before_the_latch()
    {
        // Shinobu's ring GRANTS Block and Nicole's latch asks whether the
        // player ended the turn holding any, so the whole Inazuma block has to
        // sit before it. The sim twin asserts the same sequence off its own
        // source; this is the mod's half.
        var walk = Il.Method("CompanionOverhaulTurnEnd", "AfterSideTurnEnd");
        var seen = Il.CallSequence(walk)
            .Where(c => c.Contains("OfType"))
            .ToList();
        var mondstadt = seen.FindIndex(c => c.Contains("SolarIsotomaBloomPower"));
        var first = seen.FindIndex(c => c.Contains("JuugaPower"));
        var ring = seen.FindIndex(c => c.Contains("SanctifyingRingPower"));
        var latch = seen.FindIndex(c => c.Contains("RevelationPower"));
        Assert.True(mondstadt >= 0 && first > mondstadt,
            "the Inazuma block runs after the Mondstadt six");
        Assert.True(ring > first,
            "the sequence is the workshop's own sec.3 character order");
        Assert.True(latch > ring, "Nicole's latch must stay last of all");
    }

    [Fact]
    public void The_incoming_hit_walk_puts_the_barrier_last()
    {
        // Thoma's Blazing Barrier is Diona's paws with a Block payout, and it
        // goes after them for the reason they go after the two traps: it reads
        // the absorption everything above it has already re-priced.
        var walk = Il.Method("CompanionOverhaulIncomingHit", "BeforeDamageReceived");
        var text = string.Join("\n", Il.CallSequence(walk));
        Assert.True(
            text.IndexOf("BlazingBarrierPower", StringComparison.Ordinal)
            > text.IndexOf("IcyPawsPower", StringComparison.Ordinal),
            "the barrier must read the absorption the paws have already priced");
    }

    [Fact]
    public void The_play_watcher_totals_only_card_sourced_damage_it_dealt()
    {
        // STRUCTURAL, and it is what keeps the two engines counting the same
        // thing: the sim adds `hp_dmg` for source in ("card", "attack"), and
        // this arm's power-sourced hits pass neither a dealer nor a card
        // source, so neither engine counts them.
        var hook = Il.Method("CompanionOverhaulPlayWatcher", "AfterDamageReceived");
        Assert.Contains(Il.Calls(hook), c => c.Contains("NoteDamage"));
    }

    // ==================================================================
    // Heizou's Heartstopper Strike (rebuilt 2026-10-18): Finisher's shape
    // ==================================================================

    [Fact]
    public void Heizous_face_prints_the_live_total_and_the_attack_count()
    {
        // The Inazuma pool rework: "Deal 4 Anemo damage, plus 4 for each other
        // Attack you played this turn." The count is the arm's ledger, read
        // during the play, before this Attack is noted (`EB-696`'s live
        // total stays on the face in combat).
        var face = ((CustomCardModel)(CardModel)new ProtoMiHeizouHeartstopper())
            .Localization!.First(r => r.Item1 == "description").Item2;
        Assert.Contains("for each other Attack you played this turn.", face);
        Assert.Contains("{CalculatedDamage:diff()}", face);
        Assert.DoesNotContain("Swirl", face);
    }
    // ==================================================================
    // Kyouka Fuushi and growing the pool to 34 (2026-10-18)
    // ==================================================================

    [Fact]
    public void Kyouka_fuushi_counts_every_plan_before_it_and_not_itself()
    {
        KokomiOverhaulLedger.ResetAll();
        try
        {
            var seat = Seat.Kokomi().WithCombatState();
            var clause = Assert.Single(new ProtoMiAyatoKyoukaFuushi().PlanClauses);
            var ledger = KokomiOverhaulLedger.For(seat.Creature);
            ledger.NotePlanCarryingOut();                    // itself
            Assert.Equal(3, KokomiPlan.EarlierPlanHits(seat.Creature, clause));
            // The count-all ruling (2026-10-22): a Sting or Ward counts.
            ledger.NotePlanCarryingOut(jellyfish: true);     // a Sting
            Assert.Equal(4, KokomiPlan.EarlierPlanHits(seat.Creature, clause));
            ledger.NotePlanCarryingOut(jellyfish: true);     // a Ward
            ledger.NotePlanCarryingOut();
            Assert.Equal(6, KokomiPlan.EarlierPlanHits(seat.Creature, clause));
            Assert.Contains(Il.Calls(Il.Method("KokomiPlan", "EarlierPlanHits")),
                            c => c.Contains("get_PlansCarriedOutThisTurn"));
            // The carry-out hands Hit the grown count.
            var resolve = string.Join(" ", Il.CallSequence(
                Il.Method("KokomiPlan", "ResolveOne")));
            Assert.Contains("KokomiPlan.EarlierPlanHits", resolve);
        }
        finally
        {
            KokomiOverhaulLedger.ResetAll();
        }
    }

    [Fact]
    public void The_new_rows_print_the_papers_faces()
    {
        string Face(CardModel card) => ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;
        Assert.Contains("plus once for each earlier [gold]Plan[/gold].",
                        Face(new ProtoMiAyatoKyoukaFuushi()));
        Assert.Contains("If you have [gold]Block[/gold], deal {BranchDamage:diff()} additional damage.",
                        Face(new ProtoMiKiraraMeowteorKick()));
        Assert.Contains("If you have no [gold]Block[/gold], deal {BranchDamage:diff()} additional damage.",
                        Face(new ProtoMiWandererKyougen()));
        Assert.Contains("damage 3 times.", Face(new ProtoMiYoimiyaRyuukinSaxifrage()));
        Assert.Equal("Your Attacks that hit more than once hit one additional time.",
                     Face(new ProtoMiChioriTwinBlades()));
        Assert.Equal("Damage you deal at the end of your turn is increased by 50%.",
                     Face(new ProtoMiYaeSacredSakurasFavor()));
        Assert.Equal(CardRarity.Uncommon, new ProtoMiAyakaHyouka().Rarity);
    }

    [Fact]
    public void Twin_blades_adds_a_hit_to_a_multi_hit_attack_only()
    {
        var seat = Seat.Klee().WithCombatState().WithPower<TwinBladesPower>(1);
        var power = seat.Creature.Powers.OfType<TwinBladesPower>().Single();
        var ryuukin = Owned<ProtoMiYoimiyaRyuukinSaxifrage>(seat);
        var three = new MegaCrit.Sts2.Core.Commands.Builders.AttackCommand(4m)
            .WithHitCount(3).FromCard(ryuukin, null);
        Assert.Equal(3, TwinBladesPower.PrintedHits(three));
        Assert.Equal(4, power.ModifyAttackHitCount(three, 3));
        // The printed count decides, not the running one: Niwabi's replay
        // or another modifier does not make a single hit multi-hit.
        var kick = Owned<ProtoMiKiraraMeowteorKick>(seat);
        var one = new MegaCrit.Sts2.Core.Commands.Builders.AttackCommand(9m)
            .FromCard(kick, null);
        Assert.Equal(2, power.ModifyAttackHitCount(one, 2));
        // Someone else's Attack: nothing.
        var other = Seat.Klee().WithCombatState();
        var theirs = new MegaCrit.Sts2.Core.Commands.Builders.AttackCommand(4m)
            .WithHitCount(3).FromCard(Owned<ProtoMiYoimiyaRyuukinSaxifrage>(other), null);
        Assert.Equal(3, power.ModifyAttackHitCount(theirs, 3));
        // A Plan line: an Attack's multi-hit gains one, a single hit or a
        // Skill does not.
        Assert.Equal(1, TwinBladesPower.PlanExtraHits(seat.Creature, ryuukin, 3));
        Assert.Equal(0, TwinBladesPower.PlanExtraHits(seat.Creature, ryuukin, 1));
        Assert.Equal(0, TwinBladesPower.PlanExtraHits(
            seat.Creature, new ProtoMiSayuNaptime(), 2));
        Assert.Contains("TwinBladesPower.PlanExtraHits",
            Il.Calls(Il.Method("KokomiPlan", "Hit")));
        // Upgraded, the card is Innate and still costs 1.
        var card = new ProtoMiChioriTwinBlades();
        Assert.Contains("AddKeyword", string.Join(" ", Il.Calls(
            typeof(ProtoMiChioriTwinBlades).GetMethod("OnUpgrade", All)!)));
        Assert.Equal(1, card.EnergyCost.Canonical);
    }

    private static Creature EnemyBody()
    {
        var body = Seat.Klee(40).Creature;
        Seat.Force(body, "Side", CombatSide.Enemy);
        return body;
    }

    [Fact]
    public void Sacred_sakuras_favor_multiplies_only_in_the_end_of_turn_phase()
    {
        var seat = Seat.Klee().WithCombatState().WithPower<SacredSakurasFavorPower>(1);
        var power = seat.Creature.Powers.OfType<SacredSakurasFavorPower>().Single();
        var enemy = EnemyBody();
        var state = seat.Player.PlayerCombatState!;
        foreach (var phase in new[] { PlayerTurnPhase.Start, PlayerTurnPhase.Play,
                                      PlayerTurnPhase.AutoPostPlay })
        {
            Seat.Force(state, "Phase", phase);
            Assert.Equal(1m, power.ModifyDamageMultiplicative(
                enemy, 10m, ValueProp.Unpowered, seat.Creature, null, null));
        }
        Seat.Force(state, "Phase", PlayerTurnPhase.End);
        var combat = ProtoBombs.Board(seat.Creature, enemy);
        seat.Creature.CombatState = combat;
        // The enemy side's turn (after the switch) is not hers.
        combat.CurrentSide = CombatSide.Enemy;
        Assert.False(SacredSakurasFavorPower.InEndOfTurn(seat.Creature));
        combat.CurrentSide = CombatSide.Player;
        Assert.True(SacredSakurasFavorPower.InEndOfTurn(seat.Creature));
        // Her own hit on an enemy: x1.5.
        Assert.Equal(CompanionOverhaulLaw.SacredSakuraMult,
            power.ModifyDamageMultiplicative(
                enemy, 10m, ValueProp.Unpowered, seat.Creature, null, null));
        // A dealer-less door names her seat through its credit scope.
        Assert.Equal(1m, power.ModifyDamageMultiplicative(
            enemy, 10m, ValueProp.Unpowered, null, null, null));
        using (Diagnostics.DamageCredit.Open(seat.Creature,
                   Diagnostics.DamageCredit.Power))
        {
            Assert.Equal(CompanionOverhaulLaw.SacredSakuraMult,
                power.ModifyDamageMultiplicative(
                    enemy, 10m, ValueProp.Unpowered, null, null, null));
        }
        // Another player's hit, or a hit on a player, is not hers.
        var partner = Seat.Klee().WithCombatState();
        Assert.Equal(1m, power.ModifyDamageMultiplicative(
            enemy, 10m, ValueProp.Unpowered, partner.Creature, null, null));
        Assert.Equal(1m, power.ModifyDamageMultiplicative(
            seat.Creature, 10m, ValueProp.Unpowered, enemy, null, null));
        // STRUCTURAL: no actor list is involved. Lisa's start-of-turn
        // Lightning Rose fires in the Start phase, which is not End.
        Assert.DoesNotContain("SacredSakurasFavorPower", string.Join(" ",
            Il.Calls(Il.Method("CompanionOverhaulTurnEnd", "Act"))));
    }

    [Fact]
    public void Sacred_sakuras_favor_is_offered_to_yae()
    {
        Assert.False(CompanionPool.IsHiddenFrom(new ProtoMiYaeSacredSakurasFavor(), "yae"));
        Assert.True(CompanionPool.IsHiddenFrom(new ProtoMiYaeSesshouSakura(), "yae"));
    }

    // ---- RAIDEN, 2026-10-19 ------------------------------------------------
    // [USER]: "On Musou - what about something closer to Defect's
    // hyperbeam?" / "Im seeing this as a 3 cost card like hyperbeam."

    private static List<CardModel> Hand(Seat seat) =>
        (List<CardModel>)typeof(CardPile)
            .GetField("_cards", All)!
            .GetValue(PileType.Hand.GetPile(seat.Player)!)!;

    private static T UpgradedCard<T>() where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", All)!
            .Invoke(card, Array.Empty<object?>());
        return card;
    }

    [Fact]
    public void Musou_is_a_three_cost_rare_hyperbeam()
    {
        var card = new ProtoMiRaidenMusouNoHitotachi();
        Assert.Equal(CardRarity.Rare, card.Rarity);
        Assert.Equal(CardType.Attack, card.Type);
        Assert.Equal(TargetType.AllEnemies, card.TargetType);
        Assert.Equal(3, (int)card.EnergyCost.Canonical);
        Assert.Equal(Element.Electro, ((ICompanionCard)card).CompanionElement);
        Assert.Equal(16, (int)card.DynamicVars.CalculationBase.BaseValue);
        Assert.Equal(2, (int)card.DynamicVars.ExtraDamage.BaseValue);
        Assert.Equal(3, (int)card.DynamicVars["StrengthLoss"].BaseValue);
        var up = UpgradedCard<ProtoMiRaidenMusouNoHitotachi>();
        Assert.Equal(22, (int)up.DynamicVars.CalculationBase.BaseValue);
        Assert.Equal(2, (int)up.DynamicVars.ExtraDamage.BaseValue);
        Assert.Equal(3, (int)up.DynamicVars["StrengthLoss"].BaseValue);
        Assert.Equal(3, (int)up.EnergyCost.Canonical);
    }

    [Fact]
    public void Musou_counts_the_hand_without_itself()
    {
        var seat = Seat.Klee().WithCombatState();
        var musou = Owned<ProtoMiRaidenMusouNoHitotachi>(seat);
        var hand = Hand(seat);
        Assert.Equal(0, InazumaHand.OtherCardsInHand(musou));
        hand.Add(musou);
        Assert.Equal(0, InazumaHand.OtherCardsInHand(musou));
        for (var i = 0; i < 4; i++) hand.Add(new ProtoMiIttoUshi());
        Assert.Equal(4, InazumaHand.OtherCardsInHand(musou));
        // The face's multiplier: 16 + 2 x 4.
        Assert.Equal(24, 16 + 2 * InazumaHand.OtherCardsInHand(musou));
    }

    [Fact]
    public void Musou_hits_then_takes_three_strength_from_everyone_this_turn()
    {
        var calls = Il.CallSequence(typeof(ProtoMiRaidenMusouNoHitotachi)
            .GetMethod("OnPlay", All)!).ToList();
        var hit = calls.FindIndex(c => c.Contains("DamageCmd.Attack"));
        var losses = calls.Select((c, i) => (c, i))
            .Where(x => x.c.Contains("PowerCmd.Apply")).Select(x => x.i).ToList();
        Assert.True(hit >= 0);
        Assert.Equal(2, losses.Count);              // ALL enemies, then you
        Assert.All(losses, i => Assert.True(i > hit));
        Assert.Contains(calls, c => c.Contains("HittableEnemies"));
        // Piercing Wail's this-turn shape: a TemporaryStrengthPower that takes.
        Assert.True(typeof(TemporaryStrengthPower)
            .IsAssignableFrom(typeof(ProtoMiRaidenMusouNoHitotachiPower)));
        var isPositive = typeof(ProtoMiRaidenMusouNoHitotachiPower)
            .GetProperty("IsPositive", All)!;
        Assert.False((bool)isPositive.GetValue(new ProtoMiRaidenMusouNoHitotachiPower())!);
    }

    [Fact]
    public void Euthymia_costs_two_and_its_upgrade_is_innate()
    {
        var card = new ProtoMiRaidenEuthymia();
        Assert.Equal(2, (int)card.EnergyCost.Canonical);
        var up = UpgradedCard<ProtoMiRaidenEuthymia>();
        Assert.Equal(2, (int)up.EnergyCost.Canonical);
        Assert.Contains(CardKeyword.Innate, up.Keywords);
        Assert.DoesNotContain(CardKeyword.Innate, card.Keywords);
    }
}
