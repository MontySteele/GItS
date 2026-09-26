using System;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards.Generated;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// Two Smith fixes before [USER]'s solo Klee run (2026-09-26).
///
/// PRUNE'S UPGRADE UNDER THE ARM. Off the arm, Prune -- Little Witch's Hunt
/// upgrades to +1 Spark from Klee's kit (`kit_spark`). Under the arm a Companion
/// play pays no Spark, so that upgrade bought nothing; there the upgrade is the
/// face's Block, 5 to 8 (`arm_block` on the upgrades sheet), through the
/// `{Block:diff()}` var so the Smith shows it green.
///
/// THE SPARK PRICE ON THE SMITH'S PREVIEW. Four rows' upgrades cut their Spark
/// price and nothing else. The badge already printed the new number on the
/// preview copy; it now paints it green the way <c>NCard</c> paints an energy
/// or star cost the upgrade moved (<see cref="SparkCost.PriceJustUpgraded"/>).
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KleeUpgradePreviewTests
{
    private static void Upgrade(CardModel card)
    {
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, Array.Empty<object?>());
    }

    private static string Description(CustomCardModel card) =>
        card.Localization!.Single(row => row.Item1 == "description").Item2;

    // ---- Prune: the arm's upgrade is the Block ---------------------------

    [Fact]
    public void Prunes_face_prints_its_block_through_the_diff_var()
    {
        var prune = new PruneWitchHunt();
        Assert.Contains("gain {Block:diff()} [gold]Block[/gold]",
                        Description(prune));
        Assert.Equal(5m, prune.DynamicVars.Block.BaseValue);
    }

    [Fact]
    public void Under_the_arm_prunes_upgrade_is_block_five_to_eight()
    {
        var was = KleeOverhaul.Enabled;
        try
        {
            KleeOverhaul.Enabled = true;
            var prune = new PruneWitchHunt();
            Upgrade(prune);
            Assert.Equal(8m, prune.DynamicVars.Block.BaseValue);
            // The Smith's green: the var the face prints was moved by the
            // upgrade, which is what `:diff()` highlights.
            Assert.True(prune.DynamicVars.Block.WasJustUpgraded);
        }
        finally
        {
            KleeOverhaul.Enabled = was;
        }
    }

    [Fact]
    public void Off_the_arm_prunes_upgrade_leaves_the_block_at_five()
    {
        var was = KleeOverhaul.Enabled;
        try
        {
            KleeOverhaul.Enabled = false;
            var prune = new PruneWitchHunt();
            Upgrade(prune);
            Assert.True(prune.IsUpgraded);
            Assert.Equal(5m, prune.DynamicVars.Block.BaseValue);
            Assert.False(prune.DynamicVars.Block.WasJustUpgraded);
        }
        finally
        {
            KleeOverhaul.Enabled = was;
        }
    }

    // ---- the Spark price on the Smith's preview ---------------------------

    /// <summary>What `CardModel.AfterCloned` does in the game, off the ModelDb
    /// the headless host has no boot for: the copy remembers its canonical.
    /// </summary>
    private static void SetCanonical(CardModel copy, CardModel canonical) =>
        typeof(CardModel).GetField("_canonicalInstance", HeadlessGame.All)!
            .SetValue(copy, canonical);

    /// <summary>The Smith's preview copy, as the game builds it: a mutable
    /// clone of the canonical card, upgraded, marked as a Deck preview.</summary>
    private static CardModel Preview<T>(T canonical) where T : CardModel, new()
    {
        var copy = new T();
        Seat.Set(copy, "IsMutable", true);
        SetCanonical(copy, canonical);
        Upgrade(copy);
        copy.UpgradePreviewType = CardUpgradePreviewType.Deck;
        return copy;
    }

    private static void AssertPreviewGreensThePrice<T>(int from, int to)
        where T : CardModel, new()
    {
        var canonical = new T();
        Assert.Equal(from, SparkCost.PrintedPriceOf(canonical));
        Assert.False(SparkCost.PriceJustUpgraded(canonical));

        var preview = Preview(canonical);
        Assert.Equal(to, SparkCost.PrintedPriceOf(preview));
        Assert.True(SparkCost.PriceJustUpgraded(preview));
    }

    [Fact]
    public void Sparkling_bursts_preview_greens_its_price_two_to_one() =>
        AssertPreviewGreensThePrice<ProtoKoSparklingBurst>(2, 1);

    [Fact]
    public void Once_mores_preview_greens_its_price_two_to_one() =>
        AssertPreviewGreensThePrice<ProtoKoOnceMore>(2, 1);

    [Fact]
    public void Boom_badges_preview_greens_its_price_two_to_one() =>
        AssertPreviewGreensThePrice<ProtoKoBoomBadge>(2, 1);

    [Fact]
    public void Blazing_delights_preview_greens_its_price_three_to_two() =>
        AssertPreviewGreensThePrice<ProtoKoBlazingDelight>(3, 2);

    [Fact]
    public void An_upgrade_that_is_not_a_preview_is_not_green()
    {
        // The real upgrade in a deck: upgraded, but not the Smith's copy.
        var canonical = new ProtoKoSparklingBurst();
        var copy = new ProtoKoSparklingBurst();
        Seat.Set(copy, "IsMutable", true);
        SetCanonical(copy, canonical);
        Upgrade(copy);
        Assert.False(SparkCost.PriceJustUpgraded(copy));
    }
}
