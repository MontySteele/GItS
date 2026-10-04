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
/// `EB-513` source pin (its companion carriers were cut 2026-10-03). The
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

    // ==================================================================
    // KOKOMI'S PLAN HALF, the same declaration one card over (`EB-659`).
    // ==================================================================

    [Fact]
    public void A_planned_block_is_not_enchant_modifiable_either()
    {
        // `KokomiPlan.Kind.Block` pays with
        // `GainBlock(kokomi, plan.Amount, ValueProp.Move, null)` -- the same
        // null `CardPlay`, so the same absent card source, so the same face.
        // Read the Field prints a planned Block (Cleansing Wave did, until
        // the Casket pass cut it, 2026-09-28).
        var seat = Seat.Kokomi();
        var card = Held<ProtoKkReadTheField>(seat);
        Enchant<Nimble>(card, NimbleAmount);

        var planned = card.DynamicVars["PlanBlock"];
        Assert.IsType<UnsourcedBlockVar>(planned);
        Assert.Equal(planned.BaseValue, Preview(planned, card));
    }
}
