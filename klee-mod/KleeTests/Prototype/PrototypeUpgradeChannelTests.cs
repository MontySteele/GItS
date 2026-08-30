using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// EB-213 — THE PROTOTYPE SURFACE'S UPGRADE CHANNEL.
///
/// The surface had none. Shipped upgrades live in
/// <c>docs/&lt;character&gt;-upgrades.yaml</c> keyed by shipped card id, and a
/// <c>proto_</c> key there would give R213 B's deletion rule a second file to
/// remember, so no prototype row had ever declared one and
/// <c>tools/gen_prototype_cards.py</c> had no path for one. The cost was
/// specific: under <c>C.KURAGE_MEMORY</c> the staged Kurage's Oath SUBSTITUTES
/// for the shipped row in Kokomi's offerable pool, so the only Oath a flagged
/// run can hold was the one that could not be smithed — and [USER]'s ruled
/// "3 block per memory played, upgrade to 5" existed as a row note rather than
/// as a card.
///
/// A row now carries <c>upgrade: {kurage_ward: +2}</c> itself and the generator
/// registers it into the merged delta index before emitting. EVERYTHING AFTER
/// THAT IS THE SHIPPED PATH, UNFORKED, and that is what this file pins: the
/// same <c>DynamicVar</c>, the same <c>OnUpgrade</c>, the same
/// <c>UpgradeInternal</c> the campfire calls, the same
/// <c>{PowerAmount:diff()}</c> face. If the emitted upgrade were a second
/// grammar, the arm would be proving a prototype can be printed rather than
/// that it can SHIP, which is the whole objection R213 B's "same emitter" rule
/// exists to answer.
///
/// Compiled only under <c>-p:PrototypeCards=true</c>, like everything in this
/// directory: the class it pins does not exist in a release build, so a pin
/// against it must not either. The sim twin is
/// <c>tier0/tests/test_kurage_base_kit.py</c>'s EB-213 block (the campfire
/// reaching the ruled 5) and <c>tier0/tests/test_prototype_surface.py</c>'s
/// (b2) block (the channel itself).
///
/// NO NUMBER HERE IS QUOTABLE (R213 B / R215 B). 3 and 5 are [USER]'s
/// placeholder with no measurement attached; every assertion is about whether
/// the campfire reaches them.
/// </summary>
public class PrototypeUpgradeChannelTests
{
    /// <summary>Upgrade a card the way the game's campfire does — the same
    /// helper shape <c>ConditionalUpgradePinTests</c> uses, and for the same
    /// reason: <c>UpgradeInternal</c> raises the level, calls the card's own
    /// <c>OnUpgrade</c> and finalizes each DynamicVar's preview into its
    /// base.</summary>
    private static T Upgraded<T>() where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel)
            .GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, null);
        return card;
    }

    private static string Description(CustomCardModel card) =>
        card.Localization!.Single(row => row.Item1 == "description").Item2;

    [Fact]
    public void The_substituted_oath_reports_an_upgraded_form()
    {
        // EB-213's acceptance, in one line: before the channel this card had
        // an empty OnUpgrade carrying the generator's "NO upgrade path"
        // comment, so a campfire raised its level and moved nothing.
        var upgraded = Upgraded<ProtoKuragesOathMemory>();

        Assert.True(upgraded.IsUpgraded);
    }

    [Fact]
    public void The_upgrade_moves_the_ward_to_the_ruled_five()
    {
        var card = new ProtoKuragesOathMemory();
        Assert.Equal(3m, card.DynamicVars["PowerAmount"].BaseValue);

        var upgraded = Upgraded<ProtoKuragesOathMemory>();

        Assert.Equal(5m, upgraded.DynamicVars["PowerAmount"].BaseValue);
    }

    [Fact]
    public void The_face_says_both_numbers_before_the_campfire_is_reached()
    {
        // The delta is emitted through the op's OWN var, which is what makes
        // the printed amount a token rather than a literal — a card whose face
        // hard-codes 3 is a face that cannot tell the player what the campfire
        // buys. `diff()` is the shipped renderer, not a prototype one.
        Assert.Contains("{PowerAmount:diff()}",
                        Description(new ProtoKuragesOathMemory()));
    }

    [Fact]
    public void The_applied_power_reads_the_var_rather_than_a_literal()
    {
        // STRUCTURAL, and labelled: applying the power needs a live
        // PlayerChoiceContext (README, "The headless boundary"). What is
        // checkable is that OnPlay asks the var at all — an upgraded var that
        // OnPlay never reads is the same defect one step in, and it is the
        // shape the pre-EB-213 class had by construction.
        var calls = Il.Calls(Il.Method("ProtoKuragesOathMemory", "OnPlay"));

        Assert.Contains("DynamicVarSet.get_Item", calls);
    }
}
