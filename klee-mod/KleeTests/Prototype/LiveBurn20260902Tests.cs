using System;
using System.Linq;
using BaseLib.Patches.Features;
using KleeMod.Cards;
using KleeMod.Cards.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE 2026-09-02 LIVE BURN. Six defects found by playing rather than by
/// testing -- two blind seats (`EB-289`, `EB-291`, `EB-293`) and [USER]'s own
/// session on the deployed arm (`EB-296`, `EB-297`, `EB-300`). Each is pinned
/// here at the one decision it turned on, and where the decision is a printed
/// sentence the pin reads the sentence rather than a proxy for it.
///
/// WHAT IS NOT HERE, and it is named rather than implied. Three of the six can
/// only be finished by playing:
///   * `EB-296` / `EB-300` -- the controller walk itself. What is reachable
///     headlessly is the CONDITION the restore fires on; whether the hand comes
///     back is a live check.
///   * `EB-297` -- whether the gauge draws. Godot is outside the boundary
///     (KleeTests README), so what is pinned is the predicate the bridge
///     selects on.
///   * `EB-292` -- the source of the non-finite trail position, which is a
///     hypothesis and stays open with it.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class LiveBurn20260902Tests
{
    private static string Row(ProtoBombPower pile, string key) =>
        pile.Localization!.First(r => r.Item1 == key).Item2;

    // ---- EB-289: the count on the badge is the LIVE count -----------------

    [Fact]
    public void A_pile_that_lost_a_charge_prints_the_charges_it_still_has()
    {
        // THE DEFECT, in the r4 Opus seat's own reading: "Bomb 8 ... Bombs
        // here: 2", a Set off that dealt 8 and paid ONE Spark, and "its Mine
        // had already self-popped on the previous enemy turn, so only one bomb
        // should have remained". The Spark was right -- rule 4 pays one per
        // explosion -- and the printed COUNT was the lie.
        var klee = Seat.Klee();
        var enemy = Seat.Klee(30).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature,
            new ProtoBombs.Charge(4, IsMine: true));
        // Placed through the power's own door, so the display syncs the way it
        // does in a fight (the harness seeds fields directly and does not).
        pile.AddCharge(new ProtoBombPower.ProtoCharge(8, false, 0));

        Assert.Equal(2m, pile.DynamicVars["Count"].BaseValue);

        // Rule 6: the enemy's attack pops the Mines and leaves plain Bombs.
        var mines = pile.TakeMines();

        Assert.Single(mines!);
        Assert.Single(pile.Charges);
        Assert.Equal(1m, pile.DynamicVars["Count"].BaseValue);

        // THE MUTATION GUARD, and the whole reason the var exists: the stack
        // amount did NOT move, because the take is pure by design -- it runs
        // inside a damage hook where no command may. A face reading `{Amount}`
        // is therefore reading a stack the takes cannot lower.
        Assert.Equal(1, pile.Amount);
        Assert.NotEqual(pile.Charges.Count, 0);
    }

    [Fact]
    public void The_printed_count_is_the_charge_list_and_not_the_stack()
    {
        // The row itself, so the var and the sentence cannot be fixed apart.
        var klee = Seat.Klee();
        var enemy = Seat.Klee(30).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature,
            new ProtoBombs.Charge(5));

        foreach (var key in new[] { "smartDescription", "smartDescriptionWeak",
                                    "smartDescriptionMines",
                                    "smartDescriptionMinesWeak" })
        {
            Assert.Contains("{Count}", Row(pile, key));
            Assert.DoesNotContain("{Amount}", Row(pile, key));
        }
    }

    [Fact]
    public void Every_bomb_in_a_pile_is_its_own_explosion()
    {
        // The rule the seat priced the Spark against, stated where it is
        // decided: `SetOff` takes the whole pile and walks it one charge at a
        // time, and `Explode` -- one charge, one Pyro hit, one bus ring -- is
        // what `PoundingSurprise.OnBombExploded` hangs a Spark on. Two Bombs
        // are two explosions and therefore two Sparks; the seat's fight-1 and
        // fight-3 readings agree, and fight 2 disagreed only because one of
        // the two was already gone.
        var setOff = typeof(ProtoBombPower)
            .GetMethod("SetOff", HeadlessGame.All)!;
        var calls = Il.Calls(setOff).ToList();
        Assert.Contains(calls, c => c.EndsWith("ProtoBombPower.Explode",
                                               StringComparison.Ordinal));

        var explode = typeof(ProtoBombPower)
            .GetMethod("Explode", HeadlessGame.All)!;
        Assert.Contains(Il.Calls(explode),
            c => c.EndsWith("ProtoBombPower.NotifyExplosionListeners",
                            StringComparison.Ordinal));
    }

    // ---- EB-291: the Mine's number is not a fixed number ------------------

    [Fact]
    public void The_mine_tip_says_that_weak_shrinks_it()
    {
        // The r4 Opus seat left a Gremlin Merc at 3 HP under a "Mine 3" as a
        // free kill; the Mine dealt 2 and the enemy survived and hit him. The
        // Bomb badge had learned to name Weak at `EB-287`; the Mine, which
        // fires on the ENEMY's turn with no badge in front of the player, had
        // not.
        var body = string.Concat(Il.Strings(
            typeof(ArmKeywordTips)
                .GetMethod("ForMine", HeadlessGame.All)!));

        Assert.Contains("[gold]Weak[/gold]", body);
        Assert.Contains("shrinks it like any Bomb", body);
    }

    // ---- EB-293: the Plan keyword covers the plan-only case ---------------

    [Fact]
    public void The_plan_tip_covers_a_card_that_can_only_be_planned()
    {
        // "instead" presumed a normal play to do instead of, and a plan-only
        // row has none. The r2 Opus seat could not tell and would not risk
        // finding out. The word "instead" is gone from the tip; the plan-only
        // instruction itself is printed on the FACE by the codegen
        // (`gen_klee_cards._plan_only_line`, pinned by
        // `tier0/tests/test_prototype_surface.py`), and the tip says what
        // every Plan card shares: where it goes and when it happens.
        var body = string.Concat(Il.Strings(
            typeof(ArmKeywordTips)
                .GetMethod("ForPlan", HeadlessGame.All)!));

        Assert.DoesNotContain("instead", body);
        Assert.Contains("Play this on the [gold]Bake-Kurage[/gold]", body);
    }

    // ---- EB-297: no Burst gauge for a Kokomi who has no Burst -------------

    [Fact]
    public void The_burst_gauge_stands_down_under_her_own_arm()
    {
        // [USER], live on the deployed arm: the overhead meter still read
        // 0/20. `EB-281`'s fact, one character over -- the arm turns the Burst
        // gate off, so a spec that still applied drew a bar for a resource she
        // does not have.
        var kokomi = Seat.Kokomi().Creature;
        var was = KokomiOverhaul.Enabled;
        try
        {
            KokomiOverhaul.Enabled = false;
            Assert.True(KokomiResources.BurstGaugeApplies(kokomi));

            KokomiOverhaul.Enabled = true;
            Assert.False(KokomiResources.BurstGaugeApplies(kokomi));
        }
        finally
        {
            KokomiOverhaul.Enabled = was;
        }

        // And never for anybody else, on either arm -- the co-op clause every
        // prototype display carries (`EB-194`, `EB-221`).
        Assert.False(KokomiResources.BurstGaugeApplies(Seat.Klee().Creature));
        Assert.False(KokomiResources.BurstGaugeApplies(Seat.Furina().Creature));
    }

    // ---- EB-327: and nothing FILLS the meter the gauge stood down from -----

    [Fact]
    public void A_reaction_pays_no_burst_under_her_own_arm()
    {
        // The feed half of `EB-297`'s sentence, and the half that was still
        // live: the blind seat read `Kokomi Burst: 5/20` off the status line
        // in round 4 and watched it climb 5 -> 10 -> 15, one reaction at a
        // time, with no card, relic or keyword in the slice naming the meter.
        // Three of her four income sites were already off at their own seams;
        // the reaction funnel (`ReactionEffects.Resolve`) was not.
        //
        // Pinned at `GainBurst` because that is where the guard went -- the
        // funnel every source lands in, as Klee's `EB-266` guard sits in
        // `BurstResource.Find`. The reaction call site itself is a live path
        // (it needs a dealer, a target and a consumed aura) and is outside the
        // headless boundary; what is reachable here is the decision it makes.
        var kokomi = Seat.Kokomi().WithCombatState().Creature;
        var was = KokomiOverhaul.Enabled;
        try
        {
            KokomiOverhaul.Enabled = false;
            KokomiResources.GainBurst(kokomi, KokomiConstants.BurstPerReaction);
            Assert.Equal(KokomiConstants.BurstPerReaction,
                         KokomiResources.GetBurst(kokomi));

            KokomiOverhaul.Enabled = true;
            KokomiResources.GainBurst(kokomi, KokomiConstants.BurstPerReaction);
            Assert.Equal(KokomiConstants.BurstPerReaction,
                         KokomiResources.GetBurst(kokomi));  // unmoved
        }
        finally
        {
            KokomiOverhaul.Enabled = was;
        }

        // The co-op clause: the guard is HERS, so a Klee or a Furina dealing
        // the reaction is untouched by it (they have no Kokomi meter to move
        // either way, which is what `FindBurst` already answers).
        Assert.Equal(0, KokomiResources.GetBurst(Seat.Klee().Creature));
    }

    // ---- EB-300 / EB-296: the restore fires on exactly the broken path ----

    [Fact]
    public void The_navigation_restore_fires_only_after_a_custom_target_play()
    {
        // The library's controller path omits the game's own
        // `EnableControllerNavigation()`, so the hand is left unfocusable and
        // the creature ring unlinked. The postfix that puts the line back must
        // fire on exactly that path and nowhere else -- in a release build no
        // card declares a custom target type, and this is what makes it inert
        // there.
        var predicate = Type.GetType(
            "KleeMod.Patches.NCardPlay_TryPlayCard_RestoreControllerNavigation"
            + "_Patch, klee")!
            .GetMethod("ShouldRestore", HeadlessGame.All)!;
        bool Restore(object? card) =>
            (bool)predicate.Invoke(null, new[] { card })!;

        Assert.False(Restore(null));

        // A card aimed the ordinary way is not on the broken path.
        var plain = new Kaboom();
        Assert.False(Restore(plain));

        // A card that DOES declare one, on the process-wide registry the game
        // populates at `ModelDb.Init` -- which no headless run reaches, so the
        // registration is this test's own and is taken back out again.
        var probe = (TargetType)0x5EB300;
        var table = (System.Collections.IDictionary)typeof(CustomTargetType)
            .GetField("SingleTargeting", HeadlessGame.All)!
            .GetValue(null)!;
        CustomTargetType.RegisterSingleTargetType(probe, (_, _) => true);
        try
        {
            Assert.True(CustomTargetType.IsCustomSingleTargetType(probe));
            var custom = new Kaboom();
            Seat.Force(custom, "TargetType", probe);
            Assert.True(Restore(custom));
        }
        finally
        {
            table.Remove(probe);
        }
    }
}
