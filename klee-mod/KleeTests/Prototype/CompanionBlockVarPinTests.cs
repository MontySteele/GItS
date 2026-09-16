using System.IO;
using System.Linq;
using System.Runtime.CompilerServices;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// `EB-742`, ANSWERED BY MEASUREMENT RATHER THAN BY THE FIX IT ASKED FOR.
///
/// THE ROW'S CLAIM. "<i>Front Row Seat</i>, <i>Shaken, Not Purred</i> and
/// <i>I Got Your Back</i> declare <c>BlockVar(PowerAmount)</c> WITH NO BLOCK
/// OP, so BaseLib's <c>GainsBlock</c> auto-detect reads them as Block cards
/// and offers them Nimble." The remedy it asked for was a plain var at the
/// generator and <c>GainsBlock == false</c> pinned on the three.
///
/// THE HALF OF THE CLAIM THAT IS FALSE, and it is the load-bearing half: all
/// three DO have a block op. Each row in <c>docs/prototype-surface.yaml</c>
/// opens with <c>{op: block, amount: 6}</c> (Barbara 5), each generated face
/// prints "Gain {CalculatedBlock:diff()} Block", and each <c>OnPlay</c> opens
/// with <c>CreatureCmd.GainBlock</c>. So <c>GainsBlock</c> is true for the
/// reason the game means it -- the card gains Block when you play it -- and
/// Nimble is offered correctly. <c>GainsBlock == false</c> is not reachable
/// from the generator change the row proposed: the <c>CalculatedBlockVar</c>
/// beside the <c>PowerAmount</c> var would still answer true, and the only way
/// to make the three answer false is to take away Block they print.
///
/// AND THE VAR THE ROW WANTED REMOVED IS `EB-513`. The second clause ("If a
/// Bomb goes off this turn, gain 5 Block") is the CARD's printed Block that
/// reaches the player through a Power only because its trigger looks forward,
/// so it takes the card's Frail fold on the face and on the payout. A plain
/// <c>DynamicVar</c> reaches no hook: the r18 seat watched Frail rewrite
/// Defend 5 to 3 while Diona printed and delivered 4 + 5. The generator's
/// <c>BLOCK_PAYING_POWERS</c> names these three powers and nothing else, and
/// that set is the fix, not the defect.
///
/// SO THIS FILE PINS WHAT IS TRUE, which is the only thing a pin can do, and
/// it exists because the next reader of `EB-742` would otherwise make the
/// change the row asks for and lose `EB-513` silently -- the sim and the mod
/// would still agree, every Nimble test would still pass, and only Frail on a
/// companion's second clause would go wrong.
/// </summary>
public class CompanionBlockVarPinTests
{
    private static T Held<T>(Seat seat) where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        Seat.Set(card, "Owner", seat.Player);
        return card;
    }

    /// <summary>A generated card's own source, found by walking up from this
    /// test's source path -- <c>FurinaStageRoundTwoTests</c>'s idiom.</summary>
    private static string Generated(string type,
                                    [CallerFilePath] string here = "")
    {
        var relative = Path.Combine("klee-mod", "KleeCode", "Cards",
                                    "Prototype", "Generated", type + ".cs");
        var dir = Path.GetDirectoryName(here);
        while (dir != null)
        {
            var candidate = Path.Combine(dir, relative);
            if (File.Exists(candidate)) return File.ReadAllText(candidate);
            dir = Path.GetDirectoryName(dir);
        }
        throw new FileNotFoundException(relative);
    }

    /// <summary>
    /// THE THREE ARE BLOCK CARDS, and the game's own property says so. This is
    /// the assertion `EB-742` expected to be false; it is true, and the two
    /// facts below are why.
    /// </summary>
    [Fact]
    public void The_three_companion_stand_ins_do_gain_block()
    {
        var seat = Seat.Klee();

        Assert.True(Held<ProtoMcBarbaraFrontRowSeat>(seat).GainsBlock);
        Assert.True(Held<ProtoMcDionaShakenNotPurred>(seat).GainsBlock);
        Assert.True(Held<ProtoMcNoelleIGotYourBack>(seat).GainsBlock);
    }

    /// <summary>
    /// THE CONTROL, both ways. A real Block card on the same shelf answers
    /// true, and a card that grants no Block at all answers false -- so the
    /// assertion above is reading the detector and not a constant.
    /// </summary>
    [Fact]
    public void A_real_block_card_and_a_blockless_one_bracket_it()
    {
        var seat = Seat.Klee();

        // `Dodoco Cover` is a plain Block skill on Klee's own prototype shelf.
        Assert.True(Held<ProtoKoDodocoCover>(seat).GainsBlock);
        // `Pocket Match` is a Bomb placer: no Block anywhere on its face.
        Assert.False(Held<ProtoKoPocketMatch>(seat).GainsBlock);
    }

    /// <summary>
    /// SOURCE PIN, the `EB-513` half. The bonus clause keeps its block var
    /// under <c>ValueProp.Move</c>, which is what routes it through
    /// <c>Hook.ModifyBlock</c> on the face and through the same fold at the
    /// power's payout. A regression to <c>DynamicVar("PowerAmount")</c>
    /// is invisible to every behavioural assertion in this repo's headless
    /// suite -- the preview hook needs a live combat -- so it is caught here.
    ///
    /// `EB-787`: THE CLASS IS <c>UnsourcedBlockVar</c>, the mod's subclass of
    /// the game's own. It exists because the game's <c>BlockVar</c> folds the
    /// card's ENCHANTMENT into the preview as well, and the payout cannot --
    /// <c>Pay</c> hands <c>GainBlock</c> a null <c>CardPlay</c>, so
    /// <c>Hook.ModifyBlock</c> has no card source to read one off. A Nimble
    /// moved Barbara's rider 3 to 5 on the face and paid 3 (live-looks-8c,
    /// #575). Everything the paragraph above says is unchanged: it IS a
    /// <c>BlockVar</c>, its preview IS <c>Hook.ModifyBlock</c>, and
    /// <c>GainsBlock</c> still answers true for the reason this file's first
    /// assertion gives. <c>EnchantedRiderTests</c> measures the enchant half.
    /// </summary>
    [Fact]
    public void The_bonus_clause_is_still_a_block_var()
    {
        foreach (var type in new[]
                 {
                     "ProtoMcBarbaraFrontRowSeat",
                     "ProtoMcDionaShakenNotPurred",
                     "ProtoMcNoelleIGotYourBack",
                 })
        {
            var source = Generated(type);
            Assert.Contains("new UnsourcedBlockVar(\"PowerAmount\", ", source);
            // And the card's OWN Block is still there, which is the fact that
            // makes `GainsBlock` true for the right reason.
            Assert.Contains("new CalculatedBlockVar(", source);
            Assert.Contains("CreatureCmd.GainBlock(", source);
        }
    }
}
