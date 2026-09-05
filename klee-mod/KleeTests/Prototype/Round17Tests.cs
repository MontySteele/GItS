using System;
using System.Linq;
using System.Reflection;
using BaseLib.Abstracts;
using KleeMod.Cards.Furina;
using KleeMod.Cards.Generated;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// ROUND 17, the Furina reframe's half: two readings a seat could not
/// reconcile from the screen, and in both cases the ENGINE was right and the
/// line the page printed was not.
/// </summary>
public class Round17Tests
{
    private const BindingFlags All =
        BindingFlags.Public | BindingFlags.NonPublic
        | BindingFlags.Instance | BindingFlags.Static;

    // ==================================================================
    // `EB-511` -- the amplifier that "went missing" the moment a second
    //             multiplier was on the board
    // ==================================================================
    //
    // WHAT THE SEAT SAW (Furina r11, natural lane, (c) 1). Fight 3 turn 2:
    // Chevreuse -- Interdiction Fire printed 7 under a Weak stack with a
    // `Reaction preview: Vaporize 1.5x` under it, and the fight's HP said it
    // had dealt 8. "7 x 1.5 = 10 or 11, not 8. 8 is exactly what you get if
    // the Vaporize multiplier never applied." Fight 4 turn 6 read the same
    // way one member over: Crabaletta's line said "hit Seapunk for 4 Hydro,
    // and left no aura on it" -- the glossary's own signature for a reaction
    // consuming the aura -- at a number with no 1.5 in it.
    //
    // NOTHING WAS DROPPED. The card's base is 7, Guest Cast rewrites the
    // PRINTED number to 10 (`SpotlightSystem.PrintedDamageDelta`, folded into
    // the card's own `CalculatedDamageVar` rather than into a damage hook),
    // and the engine then folds Weak and the amplifier multiplicatively over
    // that: 10 x 0.75 x 1.5 = 11.25, and 11 landed. The seat's arithmetic
    // reached 8 because the two numbers it SUBTRACTED were wrong.
    //
    // THE LIAR WAS THE SALON BLOCK. `PerformMember` filed the performance at
    // `TickValue` -- what the tick was worth BEFORE the pipeline -- so under
    // Weak a Crabaletta reported at 6 had landed for 4, and the Vaporizing one
    // reported at 4 had landed for 6. `ElementalHit.Deal` has RETURNED the
    // truncated landed amount since `EB-270` for exactly this reason, and now
    // that is what the row carries.

    /// <summary>The seat's card, so the base is the sheet's and not a
    /// literal retyped here.</summary>
    private static decimal ChevreuseBase() =>
        new ChevreuseInterdictionFire().DynamicVars.CalculationBase.BaseValue;

    [Fact]
    public void The_spotlight_rewrites_the_printed_number_and_the_rest_multiply_it()
    {
        // Guest Cast is a multiplier on the PRINTED base and truncates there:
        // 7 -> 10, which is the number the seat read on turn 3 with Weak
        // gone.
        var printed = Math.Truncate(
            ChevreuseBase() * SpotlightSystem.GuestCastBaseMultiplier);

        Assert.Equal(7m, ChevreuseBase());
        Assert.Equal(10m, printed);
    }

    [Fact]
    public void Weak_and_vaporize_compose_over_the_spotlit_base()
    {
        // `SimDamagePipeline.Resolve` IS `ElementalHit.Deal`'s three steps in
        // Deal's own order, and `KleeOverhaulRoundOneFixTests` pins the two
        // spellings against each other -- so this is the elemental path's
        // answer and the Bomb's alike.
        var weak = Seat.Furina().WithPower<WeakPower>(1);
        var target = Seat.Klee(400);

        var landed = SimDamagePipeline.Resolve(
            weak.Creature, target.Creature, 10m,
            ReactionConstants.VaporizeMult);

        Assert.Equal(11, landed);
        // ...and it is not 8, which is the number the seat's arithmetic
        // produced and the reason the row was filed.
        Assert.NotEqual(8, landed);
    }

    [Fact]
    public void The_two_powers_the_game_folds_are_each_still_their_own_factor()
    {
        // THE POWERED-ATTACK PATH, run for real. `Hook.ModifyDamageInternal`
        // walks every listener doing `num *= num3` (the fold
        // `BombPower.IsSuppressionArbiter` is written against), so what a test
        // can check headless is that each listener still answers its own
        // multiplier when the other one is standing.
        var attacker = Seat.Furina().WithPower<WeakPower>(1);
        var wearer = Seat.Klee(400).WithPower<HydroAuraPower>(2);
        var card = new ChevreuseInterdictionFire();
        var props = ValueProp.Move;
        Assert.True(props.IsPoweredAttack());
        Assert.Equal(Element.Pyro, card.Element);

        var weak = attacker.Creature.Powers.OfType<WeakPower>().Single();
        var aura = wearer.Creature.Powers.OfType<HydroAuraPower>().Single();

        var weakMult = weak.ModifyDamageMultiplicative(
            wearer.Creature, 10m, props, attacker.Creature, card, null);
        var auraMult = aura.ModifyDamageMultiplicative(
            wearer.Creature, 10m, props, attacker.Creature, card, null);

        Assert.Equal(0.75m, weakMult);
        Assert.Equal(ReactionConstants.VaporizeMult, auraMult);
        Assert.Equal(11, (int)(10m * weakMult * auraMult));
    }

    [Fact]
    public void A_performance_is_filed_at_the_number_that_landed()
    {
        // THE FIX ITSELF, read off the call site: `PerformMember` cannot be
        // run headless (a hit needs a live `CombatState`), so what a test CAN
        // read is which value the ledger row is built from. `amount` there is
        // the pre-pipeline tick and is the defect.
        var source = System.IO.File.ReadAllText(
            System.IO.Path.Combine(Repo(), "klee-mod", "KleeCode", "Powers",
                                   "SalonPowers.cs"));

        Assert.Contains("landed = await ElementalHit.Deal(", source);
        Assert.Contains("landed, paid, Evoked: false));", source);
        Assert.DoesNotContain("amount, paid, Evoked: false));", source);
    }

    [Fact]
    public void Deal_still_hands_back_what_it_dealt()
    {
        // The return the fix above depends on, stated as a fact about the
        // signature rather than trusted: `EB-270` built it and nothing may
        // quietly make it void again.
        var deal = Il.Method("ElementalHit", "Deal");

        Assert.Equal(typeof(System.Threading.Tasks.Task<int>),
                     ((MethodInfo)deal).ReturnType);
    }

    // ==================================================================
    // `EB-508` -- a Deploy performs the member it FIELDS
    // ==================================================================
    //
    // WHAT THE SEAT SAW (Furina r11, natural lane, (c) 2). Fight 4 turn 6: it
    // played Salon Début -- "Deploy Mademoiselle Crabaletta" -- and the Salon
    // block's FIRST line was the Usher performing and taking the last Encore,
    // with Crabaletta performing dry underneath. "Something performed the
    // front member off a Deploy, and no printed line says it should."
    //
    // THE DEPLOY WAS NOT THE CAUSE. That turn held four performances from four
    // causes -- a Companion card's front trigger, this deploy, a second
    // Companion card, and a second deploy -- and only the deploy's own is
    // about the member the card names. `Deploy` passes `entering`, the member
    // that just took the stage, and it always has. What no line said was WHICH
    // CARD each row came from, which is `EB-505`/`EB-506`'s question and not
    // this one's.
    //
    // THE BEHAVIOURAL PIN IS THE SIM'S, because a deploy needs a live
    // `CombatState`: `tier0/tests/test_eb508_deploy_performs_the_fielded_
    // member.py` stages the seat's own full stage and reads who performed.
    // What is checkable here is the call site and its order.

    [Fact]
    public void The_deploy_performs_after_the_member_has_entered()
    {
        var sequence = Il.CallSequence(
            Il.Method("SalonMemberPower", "Deploy"));
        var add = IndexOf(sequence, c => c.EndsWith(".Add", StringComparison.Ordinal));
        var perform = IndexOf(sequence, c => c.Contains("PerformMember"));

        Assert.True(add >= 0, string.Join(", ", sequence));
        Assert.True(perform > add, string.Join(", ", sequence));
    }

    [Fact]
    public void The_deploy_performs_the_entering_member_and_not_the_front()
    {
        var source = System.IO.File.ReadAllText(
            System.IO.Path.Combine(Repo(), "klee-mod", "KleeCode", "Powers",
                                   "SalonPowers.cs"));

        Assert.Contains(
            "await PerformMember(choiceContext, owner, entering);", source);
        Assert.DoesNotContain(
            "await PerformMember(choiceContext, owner, company[0]);", source);
    }

    // ==================================================================
    // `EB-509` -- the relic that went on dealing a card the card refuses
    // ==================================================================
    //
    // WHAT THE SEAT SAW (Furina r11, natural lane). The starting relic adds an
    // Ethereal Spotlight to hand every turn. Under the reframe Center Stage is
    // retired, so Guest Cast is the only target and the second copy is refused
    // by the card's own `IsPlayable` -- "the Spotlight is already on your
    // Companion cards". That is five to seven dead draws a fight.
    //
    // THE RELIC'S ARM FACE ALREADY SAID SO -- "It does nothing once your
    // Companion cards are lit for this combat" -- and the sentence was true
    // about the CARD and false about the relic.
    //
    // ONE PREDICATE, TWO CALLERS, which is the whole fix:
    // `SpotlightSystem.DesignateOneModeIsRedundant` is what the card's refusal
    // reads, and the grant now asks it one broadcast earlier.

    [Fact]
    public void The_grant_asks_the_cards_own_refusal_before_it_deals()
    {
        var calls = Il.Calls(Il.Method("EtherealSpotlightRelic",
                                       "BeforeSideTurnStart"));

        Assert.Contains(
            calls, c => c.Contains("DesignateOneModeIsRedundant"));
    }

    [Fact]
    public void The_card_refuses_on_the_very_predicate_the_grant_asks()
    {
        var refusal = Il.Calls(Il.Method("EtherealSpotlight", "get_IsPlayable"));

        Assert.Contains(
            refusal, c => c.Contains("DesignateOneModeIsRedundant"));
    }

    [Fact]
    public void The_price_is_not_what_stops_the_grant()
    {
        // A seat short of Encore this turn may have it next turn, so the
        // refusal on price is temporary and the card belongs in hand. The
        // card asks both questions; the relic asks only the lasting one.
        var grant = Il.Calls(Il.Method("EtherealSpotlightRelic",
                                       "BeforeSideTurnStart"));
        var refusal = Il.Calls(Il.Method("EtherealSpotlight", "get_IsPlayable"));

        Assert.DoesNotContain(
            grant, c => c.Contains("DesignateOneModeIsUnpayable"));
        Assert.Contains(
            refusal, c => c.Contains("DesignateOneModeIsUnpayable"));
    }

    [Fact]
    public void A_lit_spotlight_is_what_redundant_means()
    {
        // The predicate itself, run for real on both sides of the arm.
        using var arm = new FurinaReframeArm();
        var seat = Seat.Furina().WithCombatState();

        Assert.False(SpotlightSystem.DesignateOneModeIsRedundant(
            seat.Creature));

        CustomResources<SpotlightModeResource>
            .Get(seat.Player.PlayerCombatState).Amount =
                (int)SpotlightMode.GuestCast;

        Assert.True(SpotlightSystem.DesignateOneModeIsRedundant(
            seat.Creature));

        arm.Off();
        Assert.False(SpotlightSystem.DesignateOneModeIsRedundant(
            seat.Creature));
    }

    private sealed class FurinaReframeArm : IDisposable
    {
        private readonly bool _enabled = FurinaReframe.Enabled;
        private readonly bool _spotlight = FurinaReframe.SpotlightEnabled;

        internal FurinaReframeArm()
        {
            FurinaReframe.Enabled = true;
            FurinaReframe.SpotlightEnabled = true;
        }

        internal void Off()
        {
            FurinaReframe.Enabled = false;
            FurinaReframe.SpotlightEnabled = false;
        }

        public void Dispose()
        {
            FurinaReframe.Enabled = _enabled;
            FurinaReframe.SpotlightEnabled = _spotlight;
        }
    }

    private static int IndexOf(
        System.Collections.Generic.IReadOnlyList<string> calls,
        Func<string, bool> match)
    {
        for (var i = 0; i < calls.Count; i++)
        {
            if (match(calls[i])) return i;
        }
        return -1;
    }

    /// <summary>The repo root, from the test assembly's own location.</summary>
    internal static string Repo()
    {
        var dir = new System.IO.DirectoryInfo(AppContext.BaseDirectory);
        while (dir != null && !System.IO.Directory.Exists(
                   System.IO.Path.Combine(dir.FullName, "klee-mod")))
        {
            dir = dir.Parent;
        }
        return dir?.FullName
            ?? throw new InvalidOperationException("no repo root above " +
                                                   AppContext.BaseDirectory);
    }
}
