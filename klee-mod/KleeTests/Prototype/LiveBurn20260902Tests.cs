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

        // EVERY smart row, whatever the grid's shape: `EB-343` widened the
        // modifier axis, and the claim here is about all of them at once, so
        // the rows are read off the power rather than listed.
        var smart = pile.Localization!
            .Where(r => r.Item1.StartsWith("smartDescription")).ToList();
        Assert.True(smart.Count >= 4);
        foreach (var (_, face) in smart)
        {
            // `EB-450` swapped `{Count}` for `{Charges}`. Both are read off
            // `_charges` in `SyncDisplay` and neither is the stack, which is
            // the whole of this claim; the list also carries the order.
            Assert.Contains("{Charges}", face);
            Assert.DoesNotContain("{Amount}", face);
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
    public void The_mine_tip_says_its_number_is_not_the_printed_one()
    {
        // The r4 Opus seat left a Gremlin Merc at 3 HP under a "Mine 3" as a
        // free kill; the Mine dealt 2 and the enemy survived and hit him. The
        // Bomb badge had learned to name Weak at `EB-287`; the Mine, which
        // fires on the ENEMY's turn with no badge in front of the player, had
        // not.
        //
        // `EB-343` (R248) changed WHICH modifier that sentence names, not that
        // it names one: Klee's Weak no longer reaches a Bomb, so the tip names
        // what does -- and still sends the reader to the badge for the live
        // number, which is the half the seat actually needed.
        //
        // `EB-373` NARROWED IT TO WHAT THE CODE FOLDS. A Mine is a Bomb, and
        // `FoldedMods` reads the target's Vulnerable and its damage cap and
        // nothing else, so "the enemy's debuffs move it" was promising a Slow
        // or a Flutter would. Same words as the Bomb tip, so a reader cannot
        // hold the two against each other.
        var body = string.Concat(Il.Strings(
            typeof(ArmKeywordTips)
                .GetMethod("ForMine", HeadlessGame.All)!));

        // `EB-436` spent "Read the badge:" on the hit clause; the terms it
        // introduced are still named, which is what R248 asked for.
        Assert.Contains("Only their ", body);
        Assert.Contains("[gold]Vulnerable[/gold] and a cap move it.", body);
        Assert.DoesNotContain("[gold]Weak[/gold]", body);

        // AND IT IS MEASURED NOW. The sentence used to carry a semicolon, and
        // `tools/lint_text_conventions.py` reads these bodies out of the
        // source with a regex that stopped at one -- so this whole tip sat
        // outside the census in both of its wordings and was never held to the
        // tip ceiling. The regex is fixed in the same change; the assertion
        // here is the prose half of it.
        Assert.DoesNotContain(";", body);
    }

    [Fact]
    public void The_bomb_tip_says_whose_burden_a_bomb_is()
    {
        // `EB-343`'s card-side half. The badge shows the NUMBER; only the
        // keyword tip can say whose number it is, and this is the one rule in
        // the deck that runs opposite to every other damage source she has --
        // so it is printed where the word is met rather than inferred from a
        // total that did not move.
        //
        // AND IT FITS THE CEILING ([USER], PR #340): the clause is one half of
        // one sentence, and the three sentences together are 135 of the 135
        // that the base game's longest mechanic tip measures. The rewrite is
        // why this word takes no named exception in
        // `tools/lint_text_conventions.py` while the badge's modified faces do.
        //
        // "Its hit takes" BECAME "It takes" AT `EB-361`, which is the spelling
        // the static badge face already used ("It takes the enemy's debuffs,
        // not your Strength or Weak") -- five of the characters rule 3's
        // sentence needed, taken from a word the rule does not need.
        var body = string.Concat(Il.Strings(
            typeof(ArmKeywordTips)
                .GetMethod("ForBomb", HeadlessGame.All)!));

        // `EB-373`: the same clause, narrowed to the two terms the fold reads.
        Assert.Contains("Not an Attack: only [gold]Vulnerable[/gold] and a cap "
                      + "move it.", body);
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
        // THE WORDING WAS COMPRESSED BY `EB-334` and the anchor moved with it:
        // the fifth clause (who deals a Plan's damage) had to fit under the
        // same 135-character tip ceiling, so "Play this on the Bake-Kurage:"
        // became "On the Bake-Kurage,". What this pin is about is unchanged --
        // the tip still says WHERE a Plan card goes, which is the whole of
        // `EB-293`.
        Assert.Contains("On the [gold]Bake-Kurage[/gold]", body);
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
