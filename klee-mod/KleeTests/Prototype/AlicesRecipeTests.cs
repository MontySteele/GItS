using System;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// ALICE'S RECIPE, reworked 2026-10-11. [USER]: "Every bomb you place makes
/// every other bomb grow by 2 - an exponential ramp - upgrade raises the
/// effect to 3", then "let's make it affect both" (Bombs and Mines). Sim twin:
/// the <c>test_alices_recipe_*</c> tests in
/// <c>tier0/tests/test_klee_overhaul_rules.py</c>.
///
/// The growth is a real call on real piles (<see cref="ProtoBombs"/>); a
/// placement itself needs <c>PowerCmd</c>, so where the growth sits inside
/// <c>ProtoBombPower.Place</c> is a labelled structural pin.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class AlicesRecipeTests
{
    private static int[] Sizes(ProtoBombPower pile) =>
        pile.Charges.Select(c => c.Size).ToArray();

    [Fact]
    public void The_card_is_a_three_cost_rare_power_two_upgrading_to_three()
    {
        var card = new ProtoKoAlicesRecipe();
        Assert.Equal((CardType.Power, 3, CardRarity.Rare),
                     (card.Type, card.EnergyCost.Canonical, card.Rarity));
        Assert.Equal(2m, card.DynamicVars["PowerAmount"].BaseValue);
        Assert.Equal("Whenever you place a [gold]Bomb[/gold] or [gold]Mine[/gold], "
                   + "your other [gold]Bombs[/gold] and [gold]Mines[/gold] grow by "
                   + "{PowerAmount:diff()}.",
                     ((CustomCardModel)card).Localization!
                         .First(r => r.Item1 == "description").Item2);

        var plus = new ProtoKoAlicesRecipe();
        Seat.Set(plus, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(plus, Array.Empty<object>());
        Assert.Equal(3m, plus.DynamicVars["PowerAmount"].BaseValue);
        Assert.Equal(3, plus.EnergyCost.Canonical);
    }

    [Fact]
    public void A_placement_grows_every_other_charge_on_any_enemy_mines_included()
    {
        var klee = Seat.Klee().WithPower<AlicesRecipePower>(2);
        var a = Seat.Klee(200).Creature;
        var b = Seat.Klee(200).Creature;
        ProtoBombs.Board(klee.Creature, a, b);
        var pileA = ProtoBombs.Place(a, klee.Creature,
            new ProtoBombs.Charge(5), new ProtoBombs.Charge(4, IsMine: true));
        var pileB = ProtoBombs.Place(b, klee.Creature, new ProtoBombs.Charge(3));

        AlicesRecipePower.GrowBeforePlacement(klee.Creature);

        Assert.Equal(new[] { 7, 6 }, Sizes(pileA));
        Assert.True(pileA.Charges[1].IsMine);
        Assert.Equal(new[] { 5 }, Sizes(pileB));
    }

    [Fact]
    public void A_placement_on_all_counts_once_per_charge()
    {
        // PlaceOnAll reaches Place once per enemy, so a Bomb on each of two
        // enemies is two growths; the first new charge grows when the second
        // lands. Replayed here with the same order Place takes: grow, land.
        var klee = Seat.Klee().WithPower<AlicesRecipePower>(2);
        var a = Seat.Klee(200).Creature;
        var b = Seat.Klee(200).Creature;
        ProtoBombs.Board(klee.Creature, a, b);
        var old = ProtoBombs.Place(a, klee.Creature, new ProtoBombs.Charge(5));

        AlicesRecipePower.GrowBeforePlacement(klee.Creature);
        var newA = ProtoBombs.Place(a, klee.Creature, new ProtoBombs.Charge(6, IsMine: true));
        AlicesRecipePower.GrowBeforePlacement(klee.Creature);
        var newB = ProtoBombs.Place(b, klee.Creature, new ProtoBombs.Charge(6, IsMine: true));

        Assert.Equal(new[] { 9 }, Sizes(old));
        Assert.Equal(new[] { 8 }, Sizes(newA));
        Assert.Equal(new[] { 6 }, Sizes(newB));

        // STRUCTURAL: PlaceOnAll is a loop over Place, not a second path.
        Assert.Contains("ProtoBombPower.Place",
                        Il.Calls(Il.Method("ProtoBombPower", "PlaceOnAll")));
    }

    [Fact]
    public void The_upgraded_amount_and_two_copies_add()
    {
        var klee = Seat.Klee().WithPower<AlicesRecipePower>(3);
        Assert.Equal(3, AlicesRecipePower.GrowthFor(klee.Creature));
        var a = Seat.Klee(200).Creature;
        ProtoBombs.Board(klee.Creature, a);
        var pile = ProtoBombs.Place(a, klee.Creature, new ProtoBombs.Charge(5));
        AlicesRecipePower.GrowBeforePlacement(klee.Creature);
        Assert.Equal(new[] { 8 }, Sizes(pile));

        // A Counter power: a second copy's 2 lands on the same stack.
        var power = (AlicesRecipePower)System.Runtime.CompilerServices.RuntimeHelpers
            .GetUninitializedObject(typeof(AlicesRecipePower));
        Assert.Equal(PowerStackType.Counter, power.StackType);
    }

    [Fact]
    public void Without_the_power_nothing_grows_and_other_klees_piles_are_left_alone()
    {
        var klee = Seat.Klee();
        var partner = Seat.Klee().WithPower<AlicesRecipePower>(2);
        var a = Seat.Klee(200).Creature;
        ProtoBombs.Board(klee.Creature, a);
        partner.Creature.CombatState = klee.Creature.CombatState;
        var mine = ProtoBombs.Place(a, klee.Creature, new ProtoBombs.Charge(5));
        AlicesRecipePower.GrowBeforePlacement(klee.Creature);
        Assert.Equal(new[] { 5 }, Sizes(mine));
        // The partner's Recipe grows the partner's Bombs, not Klee's.
        AlicesRecipePower.GrowBeforePlacement(partner.Creature);
        Assert.Equal(new[] { 5 }, Sizes(mine));
    }

    [Fact]
    public void Place_grows_before_the_charge_lands_and_moves_do_not_pay()
    {
        // STRUCTURAL: the growth runs before the pile is applied, so the new
        // charge is never among "your other Bombs".
        var place = Il.CallSequence(Il.Method("ProtoBombPower", "Place")).ToList();
        var grow = place.IndexOf("AlicesRecipePower.GrowBeforePlacement");
        Assert.True(grow >= 0);
        Assert.True(grow < place.IndexOf("ProtoBombPower.AddCharge"));
        // A move is `relocated`, which skips the growth: the jump and
        // Exquisite Compound pass it (pinned with the Dodoco Charm's flag in
        // ArmRelicsPotionsTests), and the growth never places a charge.
        Assert.DoesNotContain(
            Il.Calls(Il.Method("AlicesRecipePower", "GrowBeforePlacement")),
            c => c.StartsWith("ProtoBombPower.Place", StringComparison.Ordinal));
    }
}
