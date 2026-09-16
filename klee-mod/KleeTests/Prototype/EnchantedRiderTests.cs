using System;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Enchantments;
using MegaCrit.Sts2.Core.ValueProps;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// `EB-787`. AN ENCHANT MOVES THE PRINTED BLOCK AND NEVER THE RIDER.
///
/// THE FIND (live-looks-8c, #575). A <c>Nimble</c> on <i>Barbara - Front Row
/// Seat</i> moved BOTH of the card's numbers: "Gain 5 Block" became 7, which
/// is what Nimble is for, and "whenever a Bomb goes off this turn, gain 3
/// Block" became 5, which is a number the card never gains -- the power is
/// applied <c>DynamicVars["PowerAmount"].IntValue</c>, which is
/// <c>(int)BaseValue</c>, and it pays out through a <c>GainBlock</c> whose
/// <c>CardPlay</c> is null, so <c>Hook.ModifyBlock</c> has no card source to
/// read an enchantment off. The face was the only liar.
///
/// WHAT THE FIX IS, in one line: the rider's declaration moved from the game's
/// <c>BlockVar</c> to <see cref="UnsourcedBlockVar"/>, whose preview runs the
/// PAYOUT's own <c>Hook.ModifyBlock</c> call -- same props, same target, null
/// card source -- so Frail and Dexterity still fold the face exactly as they
/// fold the gain (`EB-513`, which is why the rider is a Block var at all) and
/// the enchantment reaches neither.
///
/// THE HEADLESS BOUNDARY, and what it costs this file (README). The hook half
/// needs a live <c>CombatState</c>, so FRAIL cannot be measured here; it is
/// pinned structurally, as the call the preview makes, beside the existing
/// `EB-513` source pin in <see cref="CompanionBlockVarPinTests"/>. The
/// ENCHANT half needs nothing but a card and an <c>EnchantmentModel</c>, so it
/// is measured: <c>runGlobalHooks: false</c> is the branch where the game's
/// own <c>BlockVar</c> folds the enchantment and nothing else, which is
/// exactly the number under test.
/// </summary>
public class EnchantedRiderTests
{
    /// <summary>Nimble's rider, without the enchantment: this is the card's
    /// printed Block and it must still move.</summary>
    private const int PrintedBlock = 5;

    /// <summary>Barbara's rider, which must not.</summary>
    private const int Rider = 3;

    private const int NimbleAmount = 2;

    private static T Held<T>(Seat seat) where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        Seat.Set(card, "Owner", seat.Player);
        return card;
    }

    /// <summary>
    /// Put a real <c>Nimble</c> on a card, at an amount.
    ///
    /// The real path is <c>CardModel.EnchantInternal</c>, which calls
    /// <c>EnchantmentModel.ApplyInternal</c> and reaches the model registry
    /// and the card's display events -- outside the boundary. So the
    /// enchantment is allocated uninitialised (its constructor registers with
    /// the game's model tables, which a test has no business mutating), its
    /// amount is seeded, and it is hung on the card's own property. What is
    /// bypassed is the APPLY; what is exercised is the READ, which is
    /// <c>card.Enchantment</c> and is the whole of what a Block var does with
    /// one.
    /// </summary>
    private static void Enchant<T>(CardModel card, int amount)
        where T : EnchantmentModel
    {
        var enchantment = (T)RuntimeHelpers.GetUninitializedObject(typeof(T));
        typeof(EnchantmentModel)
            .GetField("_amount", HeadlessGame.All)!
            .SetValue(enchantment, amount);
        Seat.Set(card, "Enchantment", enchantment);
    }

    private static decimal Preview(DynamicVar var, CardModel card)
    {
        var.UpdateCardPreview(card, CardPreviewMode.Normal, null,
                              runGlobalHooks: false);
        return var.PreviewValue;
    }

    // ==================================================================
    // THE ROW'S ACCEPTANCE SENTENCE, both halves, on one enchanted card.
    // ==================================================================

    [Fact]
    public void A_nimble_barbara_prints_block_seven_and_a_rider_of_three()
    {
        var seat = Seat.Klee();
        var card = Held<ProtoMcBarbaraFrontRowSeat>(seat);
        Enchant<Nimble>(card, NimbleAmount);

        // THE PRINTED BLOCK STILL MOVES. Barbara's own Block is a
        // `CalculatedBlockVar` whose `Calculate` reaches `CombatManager`, so
        // the number is read off the game's plain `BlockVar` under the same
        // enchantment -- the identical `EnchantBlockAdditive` call, and the
        // declaration every other Block card on the shelf carries.
        var printed = new BlockVar("Block", PrintedBlock, ValueProp.Move);
        Assert.Equal(PrintedBlock + NimbleAmount, Preview(printed, card));

        // AND THE RIDER DOES NOT.
        var rider = card.DynamicVars["PowerAmount"];
        Assert.IsType<UnsourcedBlockVar>(rider);
        Assert.Equal(Rider, Preview(rider, card));
        // The highlight reads off this one, so a rider the enchantment never
        // moved must not be coloured as though it had.
        Assert.Equal(Rider, rider.EnchantedValue);
        // And the number the power is actually applied is untouched either
        // way -- it always was, which is why the defect was a face and not a
        // rule.
        Assert.Equal(Rider, rider.IntValue);
    }

    [Fact]
    public void The_games_own_block_var_is_what_used_to_move_it()
    {
        // THE CONTROL, and the defect reproduced. Same card, same
        // enchantment, same base value -- only the declaration differs. If
        // this ever stops printing 5 the assertion above has stopped reading
        // the enchantment at all and is passing for the wrong reason.
        var seat = Seat.Klee();
        var card = Held<ProtoMcBarbaraFrontRowSeat>(seat);
        Enchant<Nimble>(card, NimbleAmount);

        var wasDeclaredThisWay =
            new BlockVar("PowerAmount", Rider, ValueProp.Move);
        Assert.Equal(Rider + NimbleAmount, Preview(wasDeclaredThisWay, card));

        // And with no enchantment on the card at all, the two agree -- so the
        // subclass changes exactly one thing.
        var plain = Held<ProtoMcBarbaraFrontRowSeat>(seat);
        Assert.Equal(Rider, Preview(
            new BlockVar("PowerAmount", Rider, ValueProp.Move), plain));
        Assert.Equal(Rider, Preview(plain.DynamicVars["PowerAmount"], plain));
    }

    [Fact]
    public void Nimble_is_still_offered_to_all_three_companions()
    {
        // ELIGIBILITY DID NOT MOVE, in either direction. `UnsourcedBlockVar`
        // subclasses `BlockVar` on purpose: BaseLib's `GainsBlock`
        // auto-detect counts one, `Nimble.CanEnchant` gates on `GainsBlock`,
        // and each of the three prints real Block of its own besides the
        // rider (`CompanionBlockVarPinTests`, `EB-742`). This row moved a
        // printed number and no rule.
        var seat = Seat.Klee();

        Assert.True(Held<ProtoMcBarbaraFrontRowSeat>(seat).GainsBlock);
        Assert.True(Held<ProtoMcDionaShakenNotPurred>(seat).GainsBlock);
        Assert.True(Held<ProtoMcNoelleIGotYourBack>(seat).GainsBlock);
    }

    // ==================================================================
    // THE FRAIL HALF, structurally: `EB-513` is not paid for by this fix.
    // ==================================================================

    [Fact]
    public void The_riders_preview_still_runs_the_games_block_hooks()
    {
        // STRUCTURAL PIN (README, "the headless boundary"): `Hook.ModifyBlock`
        // needs a live combat. What it is handed is the fact under test, and
        // the IL says it: the preview calls the hook -- which is where Frail,
        // Dexterity and No Block live -- and never the enchantment's own
        // methods, which is the leak the row reported.
        var calls = Il.Calls(typeof(UnsourcedBlockVar)
            .GetMethod("UpdateCardPreview", HeadlessGame.All)!);

        Assert.Contains("Hook.ModifyBlock", calls);
        Assert.DoesNotContain(calls,
            c => c.Contains("EnchantBlock", StringComparison.Ordinal));
        // Nor by delegating to the base class, which would fold it before
        // this method ever wrote a value.
        Assert.DoesNotContain("BlockVar.UpdateCardPreview", calls);
    }

    [Fact]
    public void The_rider_is_still_a_powered_move_so_frail_still_bites_it()
    {
        // `ValueProp.Move` without `Unpowered` is the whole of
        // `IsPoweredCardOrMonsterMoveBlock`, which is what `FrailPower` and
        // `FastenPower` gate on -- and it is the prop the payout passes
        // (`FrontRowSeatPower.Pay`). Face and payout share it or `EB-513`
        // comes back.
        var seat = Seat.Klee();
        foreach (var rider in new[]
                 {
                     Held<ProtoMcBarbaraFrontRowSeat>(seat).DynamicVars["PowerAmount"],
                     Held<ProtoMcDionaShakenNotPurred>(seat).DynamicVars["PowerAmount"],
                     Held<ProtoMcNoelleIGotYourBack>(seat).DynamicVars["PowerAmount"],
                 })
        {
            var block = Assert.IsType<UnsourcedBlockVar>(rider);
            Assert.Equal(ValueProp.Move, block.Props);
        }
    }

    // ==================================================================
    // KOKOMI'S PLAN HALF, the same declaration one card over (`EB-659`).
    // ==================================================================

    [Fact]
    public void A_planned_block_is_not_enchant_modifiable_either()
    {
        // `KokomiPlan.Kind.Block` pays with
        // `GainBlock(kokomi, plan.Amount, ValueProp.Move, null)` -- the same
        // null `CardPlay`, so the same absent card source, so the same face.
        // Cleansing Wave prints its own Block AND a planned one, which is the
        // shape that makes the two conventions visible on one screen.
        var seat = Seat.Kokomi();
        var card = Held<ProtoKkCleansingWave>(seat);
        Enchant<Nimble>(card, NimbleAmount);

        var planned = card.DynamicVars["PlanBlock"];
        Assert.IsType<UnsourcedBlockVar>(planned);
        Assert.Equal(planned.BaseValue, Preview(planned, card));
    }
}
