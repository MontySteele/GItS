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
            var b = Build(new ProtoFsOusiaPledge());           // a Drain card
            var ledger = FurinaStageLedger.For(b.Furina.Creature);
            Seat.Force(b.Furina.Creature, "CurrentHp", ledger.Line + 10);
            // Her HP legibility pass (2026-10-19): a Drain inside the
            // buffer says it returns.
            Assert.Equal(FurinaStageFacePreview.ReturnsTag,
                         FurinaStageFacePreview.DrainLine(b.Card, 4));

            ledger.ModsOverride = new StageMods { Masquerade = 1 };
            Assert.Equal(FurinaStageFacePreview.ReturnsTag
                         + "\n(+4 Block: The Masquerade)",
                         FurinaStageFacePreview.DrainLine(b.Card, 4));

            ledger.ModsOverride = null;
            Assert.NotNull(ledger.Seat(StagePerformer.Freminet));
            Assert.Equal(FurinaStageFacePreview.ReturnsTag
                         + "\n(+4 Block: Freminet)",
                         FurinaStageFacePreview.DrainLine(b.Card, 4));

            // Both, after the line warning when the Drain goes past it.
            ledger.ModsOverride = new StageMods { Masquerade = 1 };
            // 2 HP of Drain buffer left (the Drain buffer, 2026-10-11).
            ledger.NoteDrain(ledger.BufferLeft - 2,
                             (int)b.Furina.Creature.CurrentHp);
            Assert.Equal("\n(2 returns, 2 past your line)"
                         + "\n(+4 Block: The Masquerade)\n(+4 Block: Freminet)",
                         FurinaStageFacePreview.DrainLine(b.Card, 4));

            // A Drain that cannot be paid pays no Block: the refusal only.
            Seat.Force(b.Furina.Creature, "CurrentHp", 4);
            Assert.Equal(FurinaStageFacePreview.NotEnoughHp,
                         FurinaStageFacePreview.DrainLine(b.Card, 4));
        });
    }
}
