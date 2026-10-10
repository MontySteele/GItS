using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;
using static KleeMod.Tests.Prototype.FurinaSpendAllPreviewWeakTests;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// The Spend rounds review (<c>review/records/furina-spend-rounds-review-2026-10-10.md</c>,
/// "What changes (Claude ships)"): High Stakes every 4 [3] (change 1) and the
/// Drain face naming who pays its Block (change 3). Change 2, High Stakes in
/// the card preview, is <see cref="FurinaHighStakesPreviewTests"/>. Sim twin
/// of change 1: <c>tier0/tests/test_furina_spend_round_fixes.py</c>.
/// </summary>
[Collection(CombatInProgressSwitch.Name)]
public class FurinaSpendReviewFixesTests
{
    // ---- 1. High Stakes: every 4 [3] ----------------------------------------

    [Fact]
    public void High_stakes_is_every_four_and_three_upgraded()
    {
        Assert.Equal(4, FurinaStageLaw.HighStakesEvery);
        Assert.Equal(3, FurinaStageLaw.HighStakesEveryUpgraded);
        Assert.Equal(4, new ProtoFsHighStakes().DynamicVars["PowerAmount"].IntValue);
        var up = new ProtoFsHighStakes();
        Seat.Set(up, "IsMutable", true);
        typeof(MegaCrit.Sts2.Core.Models.CardModel)
            .GetMethod("UpgradeInternal", HeadlessGame.All)!.Invoke(up, null);
        Assert.Equal(3, up.DynamicVars["PowerAmount"].IntValue);
        // 12 HP drained: +3 a hit, +4 upgraded.
        Assert.Equal(3, FurinaStageLaw.HighStakesBonus(12, FurinaStageLaw.HighStakesEvery));
        Assert.Equal(4, FurinaStageLaw.HighStakesBonus(12, FurinaStageLaw.HighStakesEveryUpgraded));
    }

    // ---- 3. The Drain face names its Block source ---------------------------

    [Fact]
    public void The_block_words_name_the_masquerade_and_freminet()
    {
        Assert.Equal("\n(+3 Block: The Masquerade)",
                     FurinaStageFacePreview.DrainBlock(3, 1, false));
        Assert.Equal("\n(+6 Block: The Masquerade)",
                     FurinaStageFacePreview.DrainBlock(3, 2, false));
        Assert.Equal("\n(+3 Block: Freminet)",
                     FurinaStageFacePreview.DrainBlock(3, 0, true));
        Assert.Equal("\n(+4 Block: The Masquerade)\n(+4 Block: Freminet)",
                     FurinaStageFacePreview.DrainBlock(4, 1, true));
        Assert.Equal("", FurinaStageFacePreview.DrainBlock(4, 0, false));
        Assert.Equal("", FurinaStageFacePreview.DrainBlock(0, 1, true));
    }

    [Fact]
    public void A_drain_face_names_who_pays_its_block_on_the_board()
    {
        InCombat(() =>
        {
            var b = Build(new ProtoFsOverdraft());             // Drain 4
            var ledger = FurinaStageLedger.For(b.Furina.Creature);
            Seat.Force(b.Furina.Creature, "CurrentHp", ledger.Line + 10);
            Assert.Equal("", FurinaStageFacePreview.DrainLine(b.Card, 4));

            ledger.ModsOverride = new StageMods { Masquerade = 1 };
            Assert.Equal("\n(+4 Block: The Masquerade)",
                         FurinaStageFacePreview.DrainLine(b.Card, 4));

            ledger.ModsOverride = null;
            Assert.NotNull(ledger.Seat(StagePerformer.Freminet));
            Assert.Equal("\n(+4 Block: Freminet)",
                         FurinaStageFacePreview.DrainLine(b.Card, 4));

            // Both, after the line warning when the Drain goes past it.
            ledger.ModsOverride = new StageMods { Masquerade = 1 };
            Seat.Force(b.Furina.Creature, "CurrentHp", ledger.Line + 2);
            Assert.Equal(FurinaStageFacePreview.PastLine(ledger.Line)
                         + "\n(+4 Block: The Masquerade)\n(+4 Block: Freminet)",
                         FurinaStageFacePreview.DrainLine(b.Card, 4));

            // A Drain that cannot be paid pays no Block: the refusal only.
            Seat.Force(b.Furina.Creature, "CurrentHp", 4);
            Assert.Equal(FurinaStageFacePreview.NotEnoughHp,
                         FurinaStageFacePreview.DrainLine(b.Card, 4));
        });
    }
}
