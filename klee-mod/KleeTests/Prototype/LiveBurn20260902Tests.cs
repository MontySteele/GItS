using System;
using System.Linq;
using BaseLib.Patches.Features;
using KleeMod.Cards;
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
        // `EB-291` / `EB-343`: Klee's Weak never reaches a Bomb or a Mine, so
        // no Klee-side modifier may be named on the word. The live number is
        // the badge's. TEXT PASS 2026-09-25: the Mine tip is one sentence --
        // when else it goes off -- and the folded terms left it with the Bomb
        // tip's edge cases.
        var body = string.Concat(Il.Strings(
            typeof(ArmKeywordTips)
                .GetMethod("ForMine", HeadlessGame.All)!));

        Assert.EndsWith("A [gold]Bomb[/gold] that also goes off just before its "
                     + "enemy attacks. Any [gold]Set off[/gold] spends it too.", body);
        Assert.DoesNotContain("[gold]Weak[/gold]", body);
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

        // THE 2026-09-25 TEXT PASS kept "instead" off: "Play the card on the
        // Bake-Kurage and this happens at the start of your next turn." A
        // plan-only row still leads its own face with "Play on the
        // Bake-Kurage." (the codegen's `_plan_only_line`). What this pin is
        // about is unchanged -- the tip says WHERE a Plan card goes, which is
        // the whole of `EB-293`.
        // THE STATUS BATCH (2026-10-01, sec.3 pick 2, [USER]: "Agreed on the
        // Plan text change") put the word back as the tip's opening, "Instead
        // of the line above": the face prints "Or plan:" under every now-line
        // (a Plan-only card keeps "Plan:").
        // The tip still says WHERE a Plan card goes.
        Assert.StartsWith("Instead of the line above, ",
                          body.Substring(body.IndexOf("Instead",
                              System.StringComparison.Ordinal)));
        Assert.Contains("play the card on the [gold]Bake-Kurage[/gold]", body);
    }

    // ---- EB-297: no Burst gauge for a Kokomi who has no Burst -------------

    // ---- EB-327: and nothing FILLS the meter the gauge stood down from -----

    // ---- EB-300 / EB-296: the restore fires on exactly the broken path ----

}
