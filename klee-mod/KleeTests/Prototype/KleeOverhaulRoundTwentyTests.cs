using System.Linq;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// KLEE OVERHAUL, ROUND TWENTY: the two seats' blind act-one runs
/// (`review/qa/klee-round-20-2026-09-05/`), plus R261's off-list ruling out of
/// round seventeen.
///
///   * `EB-557` (R261) -- Jumpy Dumpty gains Innate and Ka-pow! does not, so
///     turn one always holds the placer and the detonator still has to be
///     drawn.
///
/// WHAT IS REAL HERE. The keywords are the models' own `CanonicalKeywords` and
/// the tip sentences are read off the compiled method's string constants, the
/// way <see cref="ArmKeywordTipTests"/> reads them -- enumerating a tip end to
/// end formats a `LocString` through a null `LocManager` (README, "The
/// headless boundary").
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KleeOverhaulRoundTwentyTests
{
    /// <summary>The literal text one `ArmKeywordTips` attach method prints.
    /// Adjacent string constants are folded by the compiler, so each sentence
    /// is a single `ldstr` and reading them needs no ordering.</summary>
    private static string Printed(string method) => string.Concat(
        Il.Strings(typeof(ArmKeywordTips).GetMethod(
            method, HeadlessGame.All)!));

    // ---- `EB-557` (R261): the placer is Innate, the detonator is not ------

    [Fact]
    public void The_placer_is_innate_and_the_detonator_is_not()
    {
        // R261, [USER]'s own narrowing of the round-17 options: Pop! in the
        // starter was declined and a relic-planted Bomb was passed over, so
        // "Jumpy Dumpty gains Innate; Ka-pow! does not." Turn one always holds
        // the placer; the detonator still has to be drawn; the other draws
        // still have to carry the Block.
        //
        // THE KEYWORD RAIL AND NOT A BODY. `CanonicalKeywords` is the rail the
        // game's own auto-keyword pipeline renders the banner from, which is
        // what keeps the word out of the description string -- the same rail
        // Ka-pow!'s Retain rides.
        var placer = new ProtoKoJumpyDumpty();
        Assert.Contains(CardKeyword.Innate, placer.CanonicalKeywords);

        var detonator = new ProtoKoKapow();
        Assert.DoesNotContain(CardKeyword.Innate, detonator.CanonicalKeywords);
        // And the ruling did not take Retain off it on the way past (round 5
        // pick 1).
        Assert.Contains(CardKeyword.Retain, detonator.CanonicalKeywords);
    }

    [Fact]
    public void The_upgraded_placer_keeps_the_opening_it_was_ruled_for()
    {
        // `innate:` is a FIELD on the row rather than an upgrade delta, so
        // both faces carry it: an upgrade is a different card, and a player
        // who smiths the placer must not lose the opening R261 gave it.
        var upgraded = new ProtoKoJumpyDumpty();
        Seat.Set(upgraded, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(upgraded, new object?[] { });
        Assert.Contains(CardKeyword.Innate, upgraded.CanonicalKeywords);
    }

    [Fact]
    public void The_bomb_tip_says_the_deck_opens_with_a_placer()
    {
        // The rail states Innate about ONE CARD, on the card, to a player
        // already holding it. What a reader who meets the WORD needs is the
        // fact about the DECK: the first thing you can always do is plant.
        Assert.Contains("Your deck opens with a placer.", Printed("ForBomb"));
    }
}
