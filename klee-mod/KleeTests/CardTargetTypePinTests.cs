using KleeMod.Cards.Furina.Generated;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// EB-142 -- the live defect an attended playtest of package 0.2-1028 found,
/// pinned on the ONE value that was wrong.
///
/// `take_it_from_the_top` prints Block 5 and then, behind a
/// `spotlight_moved_this_turn` conditional, 10 damage (14 upgraded). The
/// generator derived a card's <see cref="TargetType"/> from its TOP-LEVEL ops
/// only, so the branch-nested damage was invisible to the derivation and the
/// constructor emitted <c>TargetType.Self</c> -- while the branch it emitted
/// opens with <c>ArgumentNullException.ThrowIfNull(cardPlay.Target)</c>.
///
/// The game fills `cardPlay.Target` in only for a card the player AIMS, so
/// with `TargetType.Self` the guard threw on every play with the Spotlight
/// moved. `OnPlay` is async and `TaskHelper.LogTaskExceptions` swallows the
/// throw, so the failure was SILENT at the table: Block landed, enemy HP did
/// not move, and only godot.log said why --
///   `GameAction PlayCardAction card: CARD.KLEEMOD-TAKE_IT_FROM_THE_TOP ...
///    completed with exception: System.ArgumentNullException: Value cannot be
///    null. (Parameter 'cardPlay.Target')`
/// Reproduced twice with KLEEMOD_SPOTLIGHT_MOVED = 1. Both faces were
/// affected; TargetType is not an upgradeable value, so one pin covers both.
///
/// The generated file is regenerated on every codegen run, so this pin is the
/// thing that survives a regression in the derivation.
/// `tools/lint_generated_structure` law L4 is the class-wide gate beside it:
/// no emitted card may declare `TargetType.Self` and still REQUIRE
/// `cardPlay.Target`.
/// </summary>
public class CardTargetTypePinTests
{
    [Fact]
    public void Take_it_from_the_top_aims_at_an_enemy()
    {
        var card = new TakeItFromTheTop();

        Assert.Equal(TargetType.AnyEnemy, card.TargetType);
        Assert.NotEqual(TargetType.Self, card.TargetType);
    }

    [Fact]
    public void Take_it_from_the_top_is_still_the_skill_the_sheet_prints()
    {
        // Guard on the pin above: an aiming TargetType is only the right
        // answer for THIS card while its body is still Block-plus-branched-
        // damage. If the row is ever rewritten to a pure self card, this fails
        // beside it rather than leaving a stale assertion standing.
        var card = new TakeItFromTheTop();

        Assert.Equal(CardType.Skill, card.Type);
        Assert.Equal(CardRarity.Uncommon, card.Rarity);
    }
}
