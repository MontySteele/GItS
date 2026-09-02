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
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE MONDSTADT COMPANION OVERHAUL'S SECOND WAVE -- the thirteen rows whose
/// printed text needed an engine hook, and the hooks (sim twin
/// <c>tier0/tests/test_companion_overhaul_hooks.py</c>).
///
/// Compiled only under <c>-p:PrototypeCards=true</c>, the same switch that
/// compiles the arm.
///
/// WHAT IS REAL HERE AND WHAT IS STRUCTURAL. More is real than in the first
/// pass's file, because this wave's work is mostly in PURE readers -- a damage
/// modifier, a cost modifier, an element funnel, a ledger -- and a pure reader
/// can be called headlessly against a <see cref="Seat"/> holding real powers.
/// What is still out of reach is RESOLUTION: <c>PowerCmd</c>,
/// <c>ElementalHit</c> and a live <c>CombatState</c> are outside the boundary
/// (KleeTests/README), so the firing ORDER and the mutating halves are pinned
/// off the compiled method and are labelled STRUCTURAL wherever they are. The
/// arithmetic those hooks perform is asserted for real in the sim twin,
/// against the same constants.
/// </summary>
public class CompanionOverhaulHookTests
{
    private const BindingFlags All = HeadlessGame.All;

    private static ValueProp Attack => ValueProp.Move;   // IsPoweredAttack()

    /// <summary>The thirteen rows of the second wave, by class.</summary>
    private static readonly Type[] SecondWave =
    {
        typeof(ProtoMcDionaIcyPaws),
        typeof(ProtoMcNoelleSweepingTime),
        typeof(ProtoMcBarbaraMelodyLoop),
        typeof(ProtoMcBennettPassionOverload),
        typeof(ProtoMcDahliaSacramentalShower),
        typeof(ProtoMcDahliaFavonianFavor),
        typeof(ProtoMcDurinBinaryForm),
        typeof(ProtoMcRazorClawAndThunder),
        typeof(ProtoMcRazorLightningFang),
        typeof(ProtoMcVarkaSturmUndDrang),
        typeof(ProtoMcAmberExplosivePuppet),
        typeof(ProtoMcEulaGlacialIllumination),
        typeof(ProtoMcMikaStarfrostSwirl),
    };

    /// <summary>The thirteen new powers, by class.</summary>
    private static readonly Type[] NewPowers =
    {
        typeof(IcyPawsPower), typeof(MelodyLoopPower),
        typeof(PassionOverloadPower), typeof(SacramentalShowerPower),
        typeof(FavonianFavorPower), typeof(BinaryFormWhitePower),
        typeof(BinaryFormDarkPower), typeof(LightningFangPower),
        typeof(SturmUndDrangPower), typeof(SwirlChargePower),
        typeof(BaronBunnyPower), typeof(LightfallSwordPower),
        typeof(StarfrostDiscountPower),
    };

    // ---- THE ROWS -------------------------------------------------------

    [Fact]
    public void The_thirteen_are_offerable_mondstadt_universals()
    {
        Assert.Equal(13, SecondWave.Length);
        foreach (var type in SecondWave)
        {
            var card = (CardModel)Activator.CreateInstance(type)!;
            var comp = Assert.IsAssignableFrom<ICompanionCard>(card);
            Assert.Equal("mondstadt", comp.Nation);
            Assert.Null(comp.PersonalPool);
            Assert.True(comp.Star == 4 || comp.Star == 5,
                $"{type.Name}: star {comp.Star}");
            Assert.NotEqual(CardRarity.Basic, card.Rarity);
        }
    }

    [Fact]
    public void The_roster_now_carries_the_whole_workshop()
    {
        // Twenty-one plus thirteen. The compiler already holds the roster ->
        // class direction (a deleted row stops the build); this is the count,
        // and it is the acceptance condition for "no row was left out".
        var universals = Il.Method("CompanionOverhaulRoster", "Universals");
        // CallSequence, not Calls: `ModelDb.Card<T>()` renders without its
        // type argument, so all thirty-four are the SAME call name and a set
        // would report one.
        var referenced = Il.CallSequence(universals)
            .Count(c => c.StartsWith("ModelDb.Card"));
        Assert.Equal(34, referenced);
    }

    [Fact]
    public void The_two_enemy_hosted_rows_aim_at_a_chosen_enemy()
    {
        // "Apply Hydro to TARGET enemy" and "place a Lightfall Sword ON
        // TARGET" are the two rows that put their power on the body they
        // named, which is the whole answer to "a power holds no target". A
        // card that landed one of them on itself would be a different card.
        foreach (var type in new[] { typeof(ProtoMcBarbaraMelodyLoop),
                                     typeof(ProtoMcEulaGlacialIllumination) })
        {
            var card = (CardModel)Activator.CreateInstance(type)!;
            Assert.Equal(TargetType.AnyEnemy, card.TargetType);
        }
    }

    [Fact]
    public void Binary_form_is_the_arms_only_modal_row()
    {
        var card = (CardModel)Activator.CreateInstance(
            typeof(ProtoMcDurinBinaryForm))!;
        var modal = Assert.IsAssignableFrom<IModalCard>(card);
        Assert.Equal(2, modal.ModeLabels.Count);
        Assert.All(modal.ModeAimsAtChosenEnemy, Assert.False);
        // A POWER card that chooses. The two forms are applied by the two
        // branches, and the choice is "for the fight" -- neither power ticks.
        Assert.Equal(CardType.Power, card.Type);
        // STRUCTURAL: the choice goes through the base game's own card-level
        // screen, which is what ModalChoice wraps -- a mode picked any other
        // way would not sync a co-op seat.
        var play = typeof(ProtoMcDurinBinaryForm).GetMethod("OnPlay", All)!;
        var calls = Il.Calls(play);
        Assert.Contains(calls, c => c.Contains("ModalChoice.SelectMode"));
        Assert.Contains(calls, c => c.Contains("ModalChoice.RecordChoice"));
        Assert.Contains(calls, c => c.Contains("PowerCmd.Apply"));
    }

    // ---- THE POWERS -----------------------------------------------------

    [Fact]
    public void Every_new_power_is_a_counter()
    {
        foreach (var type in NewPowers)
        {
            var power = (PowerModel)Activator.CreateInstance(type)!;
            Assert.Equal(PowerStackType.Counter, power.StackType);
        }
    }

    [Fact]
    public void The_blade_is_the_one_debuff_because_it_sits_on_an_enemy()
    {
        // Everything else in the arm buffs its owner; Eula's blade is placed
        // on the target and falls on it, so it reads as what it is.
        Assert.Equal(PowerType.Debuff,
            ((PowerModel)Activator.CreateInstance(
                typeof(LightfallSwordPower))!).Type);
        foreach (var type in NewPowers.Where(t => t != typeof(LightfallSwordPower)
                                              && t != typeof(MelodyLoopPower)))
        {
            Assert.Equal(PowerType.Buff,
                ((PowerModel)Activator.CreateInstance(type)!).Type);
        }
    }

    [Theory]
    [InlineData(typeof(SacramentalShowerPower), CompanionOverhaulLaw.ShowerDamage)]
    [InlineData(typeof(LightningFangPower), CompanionOverhaulLaw.LightningFangDamage)]
    [InlineData(typeof(BaronBunnyPower), CompanionOverhaulLaw.BaronBunnyDamage)]
    [InlineData(typeof(BaronBunnyPower), CompanionOverhaulLaw.BaronBunnyReduction)]
    [InlineData(typeof(LightfallSwordPower), CompanionOverhaulLaw.LightfallBase)]
    [InlineData(typeof(LightfallSwordPower), CompanionOverhaulLaw.LightfallPerAttack)]
    public void Every_power_face_prints_the_number_it_pays(Type type, int number)
    {
        // FACE FROM BODY at the power level, exactly as the first pass pins
        // it: the description interpolates the CompanionOverhaulLaw constant
        // the hook spends, so a retune moves both or neither.
        var power = (ILocalizationProvider)Activator.CreateInstance(type)!;
        var description = power.Localization!
            .Single(entry => entry.Item1 == "description").Item2;
        Assert.Contains(number.ToString(), description);
    }

    // ---- THE PURE READERS, FOR REAL -------------------------------------

    [Fact]
    public void The_three_riders_all_pay_and_they_stack()
    {
        // The sim's `flat_attack_bonus` sums all three; so does the engine,
        // by folding every ModifyDamageAdditive. Same answer, and the pin is
        // that no rider excludes another.
        var seat = Seat.Klee()
            .WithPower<PassionOverloadPower>(4)
            .WithPower<LightningFangPower>(2)
            .WithPower<SwirlChargePower>(6);
        var card = new ProtoMcRazorClawAndThunder();
        var target = Seat.Klee().Creature;      // any body that is not us
        var total = seat.Creature.Powers
            .Sum(p => p.ModifyDamageAdditive(
                target, 10m, Attack, seat.Creature, card, null));
        Assert.Equal(4 + CompanionOverhaulLaw.LightningFangDamage + 6, total);
    }

    [Fact]
    public void A_rider_pays_nothing_on_a_skill_or_someone_elses_hit()
    {
        var seat = Seat.Klee().WithPower<PassionOverloadPower>(4);
        var power = seat.Creature.Powers.OfType<PassionOverloadPower>().Single();
        var other = Seat.Klee().Creature;
        var skill = new ProtoMcDionaIcyPaws();               // a Skill
        Assert.Equal(0m, power.ModifyDamageAdditive(
            other, 10m, Attack, seat.Creature, skill, null));
        var attack = new ProtoMcRazorClawAndThunder();
        Assert.Equal(0m, power.ModifyDamageAdditive(
            other, 10m, Attack, other, attack, null));       // not our hit
        Assert.Equal(0m, power.ModifyDamageAdditive(
            other, 10m, ValueProp.Unpowered, seat.Creature, attack, null));
    }

    [Fact]
    public void The_element_override_is_last_wins_over_the_blanket_one()
    {
        var card = new ProtoMcRazorClawAndThunder();          // prints Electro
        var skill = new ProtoMcDionaIcyPaws();                // a Skill

        // Nothing standing: the card's own element, character for character
        // what the two shipped read sites used to compute inline.
        var bare = Seat.Klee();
        Assert.Equal(Element.Electro,
            CompanionOverhaulRiders.ElementFor(card, bare.Creature));

        // The blanket rider alone.
        var fang = Seat.Klee().WithPower<LightningFangPower>(2);
        Assert.Equal(Element.Electro,
            CompanionOverhaulRiders.ElementFor(card, fang.Creature));

        // A one-shot beats the blanket.
        var both = Seat.Klee()
            .WithPower<LightningFangPower>(2)
            .WithPower<PassionOverloadPower>(4);
        Assert.Equal(Element.Pyro,
            CompanionOverhaulRiders.ElementFor(card, both.Creature));

        // Varka's charge is last of all, and only once it has an element --
        // an unbanked charge names none and must not blank the card.
        var swirl = Seat.Klee()
            .WithPower<PassionOverloadPower>(4)
            .WithPower<SwirlChargePower>(6);
        Assert.Equal(Element.Pyro,
            CompanionOverhaulRiders.ElementFor(card, swirl.Creature));
        swirl.Creature.Powers.OfType<SwirlChargePower>().Single()
            .Remember(Element.Cryo);
        Assert.Equal(Element.Cryo,
            CompanionOverhaulRiders.ElementFor(card, swirl.Creature));

        // A SKILL is never overridden: the riders speak about Attacks, and
        // this one declares no IElementalCard at all -- so the funnel gives
        // back exactly what the card gives back, which is nothing.
        Assert.Equal(Element.None,
            CompanionOverhaulRiders.ElementFor(skill, both.Creature));
    }

    [Fact]
    public void The_override_reaches_a_card_that_would_apply_nothing()
    {
        // "Your next Attack applies Pyro" is a statement about the Attack, not
        // a modifier to one it was already making. The sim takes the same
        // reading and says so in `_element_for`.
        var seat = Seat.Klee().WithPower<PassionOverloadPower>(4);
        var plain = new ProtoSparkBlast();                   // no IElementalCard
        Assert.Equal(Element.Pyro,
            CompanionOverhaulRiders.ElementFor(plain, seat.Creature));
    }

    [Fact]
    public void Baron_bunny_reduces_the_hit_and_never_heals()
    {
        var seat = Seat.Klee().WithPower<BaronBunnyPower>(1);
        var bunny = seat.Creature.Powers.OfType<BaronBunnyPower>().Single();
        var enemy = Seat.Klee().Creature;    // any dealer whose Player is set
        // A player-side dealer is refused: the decoy answers an ENEMY.
        Assert.Equal(0m, bunny.ModifyDamageAdditive(
            seat.Creature, 12m, Attack, enemy, null, null));
    }

    [Fact]
    public void The_discount_reads_attacks_only_and_floors_at_zero()
    {
        var seat = Seat.Klee().WithPower<StarfrostDiscountPower>(1);
        var power = seat.Creature.Powers.OfType<StarfrostDiscountPower>().Single();

        var attack = new ProtoMcRazorClawAndThunder();        // 1 energy Attack
        Force(attack, seat);
        Assert.True(power.TryModifyEnergyCostInCombat(attack, 2m, out var cost));
        Assert.Equal(1m, cost);

        var skill = new ProtoMcDionaIcyPaws();
        Force(skill, seat);
        Assert.False(power.TryModifyEnergyCostInCombat(skill, 2m, out _));

        // A zero-cost Attack is already free: nothing to claim.
        Assert.False(power.TryModifyEnergyCostInCombat(attack, 0m, out _));
    }

    [Fact]
    public void The_white_multiplier_adds_per_copy()
    {
        Assert.Equal(1m, CompanionOverhaulReactions.DamageMultiplier(null));
        Assert.Equal(1m, CompanionOverhaulReactions.DamageMultiplier(
            Seat.Klee().Creature));
        Assert.Equal(CompanionOverhaulLaw.BinaryWhiteReactionMult,
            CompanionOverhaulReactions.DamageMultiplier(
                Seat.Klee().WithPower<BinaryFormWhitePower>(1).Creature));
        Assert.Equal(2m, CompanionOverhaulReactions.DamageMultiplier(
            Seat.Klee().WithPower<BinaryFormWhitePower>(2).Creature));
    }

    [Fact]
    public void The_ledger_counts_per_turn_and_rolls_on_the_round()
    {
        var ledger = new CompanionOverhaulLedger();
        ledger.RollTo(1);
        ledger.NoteAttack();
        ledger.NoteAttack();
        Assert.Equal(2, ledger.AttacksPlayedThisTurn);
        ledger.RollTo(1);                       // same round: no reset
        Assert.Equal(2, ledger.AttacksPlayedThisTurn);
        ledger.RollTo(2);
        Assert.Equal(0, ledger.AttacksPlayedThisTurn);
        // A skipped round is still a reset -- the roll is self-correcting.
        ledger.NoteAttack();
        ledger.RollTo(9);
        Assert.Equal(0, ledger.AttacksPlayedThisTurn);
    }

    [Fact]
    public void The_generated_branch_asks_the_ledger_plus_one()
    {
        // The `+ 1` is the card asking the question: both engines count an
        // Attack AFTER it resolves, so the third Attack sees two. A
        // divergence here is a card that fires on the wrong swing.
        var play = typeof(ProtoMcRazorClawAndThunder).GetMethod("OnPlay", All)!;
        Assert.Contains("CompanionOverhaulLedger.For", Il.Calls(play));
        Assert.Contains("CompanionOverhaulLedger.get_AttacksPlayedThisTurn",
            Il.Calls(play));
    }

    [Fact]
    public void The_blade_counts_and_pays_off_its_own_tally()
    {
        var blade = (LightfallSwordPower)Activator.CreateInstance(
            typeof(LightfallSwordPower))!;
        Assert.Equal(0, blade.Counted);
        blade.Note();
        blade.Note();
        Assert.Equal(2, blade.Counted);
    }

    // ---- THE ORDER LAWS AND THE FUNNELS, STRUCTURALLY -------------------

    [Fact]
    public void One_listener_drives_the_three_incoming_readers_in_order()
    {
        // STRUCTURAL. Two of the three put an element on the board and can
        // kill the attacker, so listener iteration order would decide which
        // reactions fire -- EB-19/races-c, answered the way the end-of-turn
        // six answer it. The sim asserts the same order against this file.
        var hook = typeof(CompanionOverhaulIncomingHit)
            .GetMethod("BeforeDamageReceived", All)!;
        var calls = Il.CallSequence(hook)
            .Where(c => c.Contains("SacramentalShowerPower")
                     || c.Contains("BaronBunnyPower")
                     || c.Contains("IcyPawsPower"))
            .ToList();
        Assert.NotEmpty(calls);
        var first = calls.FindIndex(c => c.Contains("SacramentalShowerPower"));
        var second = calls.FindIndex(c => c.Contains("BaronBunnyPower"));
        var third = calls.FindIndex(c => c.Contains("IcyPawsPower"));
        Assert.True(first < second && second < third,
            string.Join(", ", calls));
    }

    [Fact]
    public void The_traps_use_the_hook_the_mine_uses()
    {
        // Reuse, not a parallel hook. Klee's Mine answers an enemy attack
        // from BeforeDamageReceived on the ENEMY; these three read the same
        // broadcast from the player's side. If this ever stops being true the
        // two would answer at different moments in the same hit.
        Assert.NotNull(typeof(ProtoBombPower).GetMethod("BeforeDamageReceived", All));
        Assert.NotNull(typeof(CompanionOverhaulIncomingHit)
            .GetMethod("BeforeDamageReceived", All));
    }

    [Fact]
    public void Both_element_read_sites_go_through_the_one_funnel()
    {
        // The application listener and the reaction reader must not be able to
        // disagree about a card's element: one would apply an aura the other
        // would react against. This is the pin that keeps them on one answer.
        foreach (var method in new MethodBase[]
                 {
                     typeof(KleeElementalHooks)
                         .GetMethod("BeforeDamageReceived", All)!,
                     typeof(AuraPower).GetMethod("ElementOf", All)!,
                 })
        {
            Assert.Contains("AuraCmd.ElementOfPlay", Il.Calls(method));
        }
        Assert.Contains("CompanionOverhaulRiders.ElementFor",
            Il.Calls(typeof(AuraCmd).GetMethod("ElementOfPlay", All)!));
    }

    [Fact]
    public void The_reaction_event_is_raised_from_the_one_resolution_site()
    {
        // The mod counts reactions in exactly one place and broadcast none;
        // this is the broadcast, and it stays at that one place.
        var resolve = Il.Method("ReactionEffects", "Resolve");
        Assert.Contains(Il.Calls(resolve),
            c => c.Contains("CompanionOverhaulReactions.Note"));
    }

    [Fact]
    public void Both_reaction_damage_sites_take_the_white_multiplier()
    {
        // "Enemies take 50% more damage from reactions" reaches exactly two
        // places in this engine -- the amplifier and the Overload splash --
        // and the sim reaches the same two. Everything else a reaction does
        // deals no damage of its own.
        var amp = typeof(ReactionTable).GetMethods(All)
            .Single(m => m.Name == "AmplifierMultiplier"
                      && m.GetParameters().Length == 2);
        Assert.Contains(Il.Calls(amp),
            c => c.Contains("CompanionOverhaulReactions.DamageMultiplier"));
        var resolve = Il.Method("ReactionEffects", "Resolve");
        Assert.Contains(Il.Calls(resolve),
            c => c.Contains("CompanionOverhaulReactions.DamageMultiplier"));
    }

    [Fact]
    public void The_blade_joins_the_end_of_turn_walk_and_the_others_do_not()
    {
        // Eula's blade deals damage and is hosted on an enemy, so its position
        // in the sequence matters and the one listener drives it. The wave's
        // other three end-of-turn items are a tick and two removals, which
        // cannot change an outcome by running in a different order, so they
        // keep their own broadcast -- the shipped AttackUpThisTurnPower's
        // shape. The sim asserts the same split against this file.
        var walk = typeof(CompanionOverhaulTurnEnd)
            .GetMethod("AfterSideTurnEnd", All)!;
        var calls = Il.Calls(walk);
        Assert.Contains(calls, c => c.Contains("LightfallSwordPower"));
        Assert.DoesNotContain(calls, c => c.Contains("FavonianFavorPower"));
        Assert.DoesNotContain(calls, c => c.Contains("PassionOverloadPower"));
        Assert.DoesNotContain(calls, c => c.Contains("LightningFangPower"));

        foreach (var type in new[] { typeof(FavonianFavorPower),
                                     typeof(PassionOverloadPower),
                                     typeof(LightningFangPower) })
        {
            Assert.NotNull(type.GetMethod("AfterSideTurnEnd", All));
        }
    }

    [Fact]
    public void The_two_permanent_powers_never_tick_down()
    {
        // The workshop's sec.1 rule: "A Power has no turn limit." Durin's two
        // forms are chosen "for the fight" and Varka's reads every Swirl, so
        // none of the three may carry a clock.
        foreach (var type in new[] { typeof(BinaryFormWhitePower),
                                     typeof(BinaryFormDarkPower),
                                     typeof(SturmUndDrangPower) })
        {
            var calls = type.GetMethods(All)
                .Where(m => m.DeclaringType == type)
                .SelectMany(Il.Calls)
                .ToList();
            Assert.DoesNotContain("PowerCmd.TickDownDuration", calls);
        }
    }

    [Fact]
    public void Every_speculative_reader_is_pure()
    {
        // THE RULE THIS FILE EXISTS TO KEEP. ModifyDamageAdditive and
        // TryModifyEnergyCostInCombat are called for previews and tooltips, and
        // a mutation inside one desynced co-op on 2026-07-27 (the Vigil's own
        // note). Every reader below is a pure read; every mutation this arm
        // makes is in BeforeCardPlayed, AfterCardPlayed or BeforeDamageReceived.
        var forbidden = new[] { "PowerCmd.", "CreatureCmd.", "CardCmd.",
                                "ElementalHit.", "Rng." };
        var readers = new List<MethodBase>();
        foreach (var type in NewPowers)
        {
            foreach (var name in new[] { "ModifyDamageAdditive",
                                         "ModifyDamageMultiplicative",
                                         "TryModifyEnergyCostInCombat" })
            {
                var m = type.GetMethod(name, All);
                if (m != null && m.DeclaringType == type) readers.Add(m);
            }
        }
        readers.Add(typeof(CompanionOverhaulRiders).GetMethod("ElementFor", All)!);
        readers.Add(typeof(CompanionOverhaulReactions)
            .GetMethod("DamageMultiplier", All)!);
        Assert.NotEmpty(readers);
        foreach (var reader in readers)
        {
            foreach (var call in Il.Calls(reader))
            {
                Assert.DoesNotContain(forbidden, f => call.StartsWith(f));
            }
        }
    }

    [Fact]
    public void The_rider_latch_is_taken_before_the_play_and_spent_after()
    {
        // Mika's card IS an Attack that applies its own rider, which the
        // shipped NextAttackUpPower never had to face -- "remove myself after
        // any Attack" would eat the discount the card just printed. The latch
        // is the answer, and it is the CardPlay-identity idiom
        // SparkAttackCostPower documents.
        var before = typeof(NextAttackRiderPower)
            .GetMethod("BeforeCardPlayed", All)!;
        var after = typeof(NextAttackRiderPower)
            .GetMethod("AfterCardPlayed", All)!;
        Assert.NotNull(typeof(NextAttackRiderPower)
            .GetField("_spendingOn", All));
        Assert.NotNull(typeof(NextAttackRiderPower)
            .GetField("_spending", All));
        Assert.Contains(Il.Calls(after), c => c.Contains("PowerCmd.Remove")
                                           || c.Contains("PowerCmd.ModifyAmount"));
        // The latch is TAKEN before the play and never spends anything there:
        // a removal in BeforeCardPlayed would take the rider off the very
        // Attack it was bought for.
        Assert.DoesNotContain(Il.Calls(before), c => c.StartsWith("PowerCmd."));

        foreach (var type in new[] { typeof(PassionOverloadPower),
                                     typeof(SwirlChargePower),
                                     typeof(StarfrostDiscountPower) })
        {
            Assert.True(typeof(NextAttackRiderPower).IsAssignableFrom(type),
                type.Name);
        }
    }

    [Fact]
    public void The_arm_does_not_edit_the_shipped_next_attack_powers()
    {
        // A flag-off build has to keep meaning what it printed. Bennett's
        // shipped Passion Overload carries no element clause, so the rewrite
        // is a SECOND class rather than a retune -- the standing rule of this
        // arm, met a second time.
        var shipped = new[] { typeof(NextAttackUpPower),
                              typeof(AttackUpThisTurnPower) }
            .SelectMany(t => t.GetMethods(All).Where(m => m.DeclaringType == t))
            .SelectMany(Il.Calls)
            .ToList();
        Assert.DoesNotContain(shipped, c => c.StartsWith("CompanionOverhaul"));
        Assert.DoesNotContain(shipped, c => c.Contains("PassionOverloadPower"));
    }

    /// <summary>Give a canonical card an owner, which the cost reader asks
    /// for. Through the harness's own writer, which knows both field shapes
    /// the game uses and says why the setter is bypassed.</summary>
    ///
    /// IsMutable is set too, and it is not ceremony: the reader goes through
    /// `SparkCost.OwnerCreatureOf`, which returns null for a canonical model
    /// on purpose (EB-94 -- `CardModel.Owner`'s getter THROWS on one). A card
    /// somebody is holding is mutable, and this is what makes the fake one
    /// that.
    private static void Force(CardModel card, Seat seat)
    {
        Seat.Set(card, "IsMutable", true);
        Seat.Force(card, "Owner", seat.Player);
    }
}
