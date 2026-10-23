using System.IO;
using System.Linq;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE SPEND OUTLET PAPER (<c>review/ruled/furina-spend-outlet-2026-10-12.md</c>
/// sec.2, ruled 2026-10-12, all defaults): Rising Applause+ gains Retain and
/// the base card is unchanged; her starter spend-all carries a one-line rider
/// saying when to play it. The caps are pinned in
/// <see cref="FurinaSpendUpToTests"/> and Packed House in
/// <see cref="FurinaDiversityPassTests"/>. Sim twin:
/// <c>tier0/tests/test_furina_spend_outlet_2026_10_12.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class FurinaSpendOutletTests
{
    private static CardModel Upgraded(CardModel card)
    {
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, null);
        return card;
    }

    private static string Generated(string type) => File.ReadAllText(
        Path.Combine(Round17Tests.Repo(), "klee-mod", "KleeCode", "Cards",
                     "Prototype", "Generated", type + ".cs"));

    [Fact]
    public void Rising_applause_gains_retain_only_on_the_upgrade()
    {
        var card = new ProtoFsStandingOvation();
        Assert.Equal(CardRarity.Basic, card.Rarity);
        Assert.DoesNotContain(CardKeyword.Retain, card.Keywords);
        Assert.Equal(5m, card.DynamicVars.Block.BaseValue);

        var upgraded = Upgraded(new ProtoFsStandingOvation());
        Assert.Contains(CardKeyword.Retain, upgraded.Keywords);
        Assert.Equal(7m, upgraded.DynamicVars.Block.BaseValue);
    }

    [Fact]
    public void Rising_applause_carries_the_bank_damage_rider_and_no_other_card_does()
    {
        Assert.Contains("ArmKeywordTips.ForBankDamage(",
                        Generated("ProtoFsStandingOvation"));
        var dir = Path.Combine(Round17Tests.Repo(), "klee-mod", "KleeCode",
                               "Cards", "Prototype", "Generated");
        var carriers = Directory.GetFiles(dir, "*.cs")
            .Where(f => File.ReadAllText(f).Contains("ForBankDamage("))
            .Select(Path.GetFileNameWithoutExtension)
            .ToArray();
        Assert.Equal(new[] { "ProtoFsStandingOvation" }, carriers);

        var tips = File.ReadAllText(Path.Combine(
            Round17Tests.Repo(), "klee-mod", "KleeCode", "Cards", "Prototype",
            "PlayerTips.cs"));
        // The Furina wave (2026-10-13): it opens with where Fanfare comes
        // from (`FurinaWaveTests`).
        Assert.Contains("\"Whenever you lose HP, gain that much "
                        + "[gold]Fanfare[/gold]. Its \"", tips);
        Assert.Contains("\"damage is the [gold]Fanfare[/gold] you hold: play "
                        + "it when \"", tips);
        Assert.Contains("\"the bank is worth it.\"", tips);
        var mod = File.ReadAllText(Path.Combine(
            Round17Tests.Repo(), "klee-mod", "KleeCode", "KleeMod.cs"));
        Assert.Contains("ArmKeywordTips.BankDamageKey + \".title\"", mod);
    }
}
