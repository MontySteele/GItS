using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// EB-140 — the two upgrade delta keys that move a number in a BRANCH.
///
/// `hold_the_line` (`{conditional_block: +3}`) and `take_it_from_the_top`
/// (`{conditional_damage: +4}`) were ratified at W3 (R211) and shipped with an
/// EMPTY `OnUpgrade`: tier0 applied both deltas and the live game applied
/// neither, so the campfire choice existed in the sim and not in the game.
/// EB-140 taught `gen_klee_cards.EXPRESSIBLE_DELTAS` both keys. What this file
/// pins is the SHIPPED RESULT, on the real game types.
///
/// THE DELTA HAS TWO HALVES AND THEY ARE SAID IN TWO GRAMMARS, so they are
/// pinned two ways:
///
///   * the TOP-LEVEL half rides the op's own <c>DynamicVar</c>, so it is fully
///     reachable — the game's own <c>CardModel.UpgradeInternal</c> runs
///     headlessly and the var's base value moves for real;
///   * the BRANCH half is a literal inside <c>OnPlay</c>, which needs a live
///     <c>CombatState</c> and is outside the headless boundary (README, "The
///     headless boundary"). Its FACE is reachable and is asserted directly —
///     `{IfUpgraded:show:up|base}` is the string the player reads — and the
///     claim that the body reads the same flag is a labelled STRUCTURAL pin.
///
/// The exact emitted C# for both branches is pinned on the other side of the
/// generator, against the shipped `.cs` files, in
/// `tier0/tests/test_roster_codegen.py`.
/// </summary>
public class ConditionalUpgradePinTests
{
    /// <summary>Upgrade a card the way the game's campfire does.
    ///
    /// `UpgradeInternal` is the real path: it raises the level, calls the
    /// card's own `OnUpgrade`, and finalizes every DynamicVar's preview into
    /// its base. `IsMutable` is set first for the reason the other suites set
    /// it (ParityAuthorityPinTests): a freshly constructed CardModel is the
    /// canonical prototype and mutating one asserts mutability, which the
    /// game's own `ToMutable` would have granted through a ModelDb the
    /// headless host has no boot for.</summary>
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

    // --- hold_the_line: conditional_block raises BOTH halves ---------------

    // --- take_it_from_the_top: conditional_damage moves the branch only ----

}
