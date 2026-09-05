using System;
using System.Collections.Generic;
using System.Linq;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
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

    // ---- `EB-555`: the cap is defined where it is used -------------------

    [Fact]
    public void The_bomb_tip_defines_the_cap_it_names()
    {
        // "The Bomb keyword says twice that only Vulnerable and a cap move it,
        // and no screen I saw ever explained what a cap is. I verified the
        // Vulnerable half; the other half is a term with no definition
        // anywhere in the text I was shown" (Klee r20 lane 1, (c) 2).
        //
        // A DEFINING PHRASE AND NOT A SENTENCE, and it names whose HP it is:
        // a cap limits the HP the ENEMY can lose, which is what `FoldedMods`
        // reads off the target, and saying so also rules out the reading that
        // a cap might be something of Klee's.
        var bomb = Printed("ForBomb");
        Assert.Contains("and a cap on the ", bomb);
        Assert.Contains("enemy's HP loss move it.", bomb);
    }

    [Fact]
    public void The_mine_tip_keeps_its_own_clause_unchanged()
    {
        // ONE DEFINITION PER PAGE, not one per clause. The Mine tip is at 133
        // of its 135-character ceiling and prints directly under the Bomb tip;
        // a Mine IS a Bomb, so the term is defined on the screen either way.
        Assert.Contains("Vulnerable[/gold] and a cap move it.", Printed("ForMine"));
    }

    // ---- `EB-536` (widened): the pile's numbers are sizes -----------------

    [Fact]
    public void The_badge_labels_its_list_as_sizes_and_not_as_a_count()
    {
        // "Bombs here: 3, including 1 Mine reads as a count and is a VALUE. I
        // misread it for a fight and a half until Bomb 21 ... Bombs here: 9 /
        // 12 disambiguated it. When there is one Bomb the field is genuinely
        // ambiguous" (Klee r20 lane 2, (c) 1). `EB-450` replaced the count
        // with the list; the label was the half it left behind.
        var faces = Faces(new ProtoBombPower()).Select(r => r.Body).ToList();
        Assert.NotEmpty(faces);
        foreach (var face in faces)
        {
            Assert.DoesNotContain("Bombs here:", face);
        }
        Assert.Contains(faces,
            f => f.Contains("Bomb sizes here: [blue]{Charges}[/blue]"));
    }

    [Fact]
    public void A_single_charge_block_still_prints_no_hit_clause()
    {
        // `EB-514`'s clause, cut off the one-charge faces by `EB-536` and
        // pinned here beside the label it shares a row with: on a pile of one
        // the total IS the hit, so "in 1 hit for 1 Spark" spends a sentence
        // restating a number the reader already has. The axis is in the KEY --
        // `SmartKey` writes "One" into it for the single-charge faces -- so
        // this reads the pair rather than guessing from the body.
        var rows = Faces(new ProtoBombPower());
        Assert.NotEmpty(rows);
        foreach (var (key, body) in rows)
        {
            if (!key.StartsWith("smartDescription", StringComparison.Ordinal))
            {
                continue;
            }
            var single = key.StartsWith("smartDescriptionOne",
                                        StringComparison.Ordinal);
            Assert.Equal(!single, body.Contains("hits for"));
        }
    }

    /// <summary>Every localised body the Bomb badge registers, static face and
    /// smart faces alike, with the key it is filed under.</summary>
    private static List<(string Key, string Body)> Faces(ProtoBombPower power) =>
        (power.Localization ?? new List<(string, string)>())
        .Where(row => row.Item1.StartsWith("description",
                                           StringComparison.Ordinal)
                   || row.Item1.StartsWith("smartDescription",
                                           StringComparison.Ordinal))
        .Select(row => (row.Item1, row.Item2))
        .ToList();
}
