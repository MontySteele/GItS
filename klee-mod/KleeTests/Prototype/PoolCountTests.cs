using System.Collections.Generic;
using System.Linq;
using KleeMod.Cards;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE POOL-COUNT PIN (legacy cleanup stage 4, 2026-10-01). Each character's
/// pool IS its prototype roster now -- the roster's pool is what
/// <c>FilterThroughEpochs</c> offers -- so its size and rarity split are
/// pinned here, read off the compiled roster methods (<see cref="ArmPools"/>:
/// <c>ModelDb</c> throws in a test host, so the type arguments are read off
/// the IL and the cards built with <c>new</c>).
///
/// Every kit's target is 78 standard cards, plus two Ancients and five
/// multiplayer cards where it has them (STATE.md). A row added or cut moves a
/// number here on purpose; <c>tools/lint_arm_pool_parity.py</c> holds the same
/// rosters to the sheet and the sim.
/// </summary>
public class PoolCountTests
{
    private const string Powers = "KleeMod.Powers.";

    private static (int Common, int Uncommon, int Rare) Split(
        IReadOnlyList<CardModel> cards) =>
        (cards.Count(c => c.Rarity == CardRarity.Common),
         cards.Count(c => c.Rarity == CardRarity.Uncommon),
         cards.Count(c => c.Rarity == CardRarity.Rare));

    private static void AssertPool(string roster, string method,
                                   int common, int uncommon, int rare,
                                   int size = 78)
    {
        var pool = ArmPools.Named(Powers + roster, method);
        Assert.Equal(size, pool.Count);
        Assert.Equal(pool.Count, pool.Select(c => c.GetType()).Distinct().Count());
        Assert.Equal((common, uncommon, rare), Split(pool));
        Assert.All(pool, c => Assert.Equal("KleeMod.Cards.Prototype.Generated",
                                           c.GetType().Namespace));
    }

    private static void AssertTier(string roster, string method)
    {
        var tier = ArmPools.Named(Powers + roster, method);
        Assert.Equal(5, tier.Count);
        Assert.All(tier, c => Assert.Equal(CardMultiplayerConstraint.MultiplayerOnly,
                                           c.MultiplayerConstraint));
    }

    private static void AssertAncients(string character)
    {
        var ancients = ArmPools.NamedByGetter("KleeMod.RosterAncientCards", character);
        Assert.Equal(2, ancients.Count);
        Assert.All(ancients, c => Assert.Equal(CardRarity.Ancient, c.Rarity));
    }

    [Fact]
    public void Klee_is_78_and_24_33_21_with_two_ancients_and_five_coop()
    {
        AssertPool("KleeOverhaulRoster", "Slice", 24, 33, 21);
        AssertAncients("Klee");
        AssertTier("KleeOverhaulRoster", "MultiplayerSlice");
    }

    [Fact]
    public void Kokomi_is_78_and_21_36_21_with_two_ancients_and_five_coop()
    {
        AssertPool("KokomiOverhaulRoster", "Slice", 21, 36, 21);
        AssertAncients("Kokomi");
        AssertTier("KokomiOverhaulRoster", "MultiplayerSlice");
    }

    [Fact]
    public void Furina_is_34_rows_and_10_17_7_with_two_ancients_and_no_coop()
    {
        // THE SALON'S TAB (2026-10-05, proposal sec.16): the slice's 24 rows
        // (12 Common, 8 Uncommon, 4 Rare), and the pool to 39
        // (review/active/furina-pool-40-2026-10-05.md sec.3, ruled): seven
        // Uncommons and three Rares more. The paper's 29 -> 39 counts the
        // two Basics and the three Neuvillette companion rows besides. The
        // 2026-10-09 playtest trim moved Interval Bell and Tidal Flourish to
        // Uncommon: 12 / 15 / 7 -> 10 / 17 / 7.
        AssertPool("FurinaStageRoster", "Pool", 10, 17, 7, size: 34);
        AssertAncients("Furina");
        Assert.Null(System.Type.GetType(
            "KleeMod.Powers.FurinaStageRoster, klee")?.GetMethod("MultiplayerRows"));
    }

    [Fact]
    public void Varka_is_78_and_20_35_23()
    {
        // No Ancient and no co-op tier yet.
        AssertPool("VarkaRoster", "Pool", 20, 35, 23);
    }

    [Fact]
    public void The_companion_roster_is_prototype_rows_only()
    {
        // Mondstadt's 34 and Inazuma's 24 rewritten Universals and Fontaine's
        // 16 ported as they are (pick 4); no shipped companion comes through.
        var universals = new[] { "Universals", "InazumaUniversals", "FontaineUniversals" }
            .SelectMany(m => ArmPools.Named(Powers + "CompanionOverhaulRoster", m))
            .ToList();
        // Mondstadt 35 since the AoE trim (2026-10-03) split Durin in two; 39
        // since the Klee-only companions (2026-10-03) added Sinful Hex, Mollis
        // Favonius, Ladder of Divine Ascent and Qiqi's Herald of Frost (Liyue).
        Assert.Equal(39 + 24 + 16, universals.Count);
        var byNation = universals.GroupBy(c => ((ICompanionCard)c).Nation)
            .ToDictionary(g => g.Key!, g => g.Count());
        Assert.Equal(38, byNation["mondstadt"]);
        Assert.Equal(1, byNation["liyue"]);
        Assert.Equal(24, byNation["inazuma"]);
        Assert.Equal(16, byNation["fontaine"]);
        Assert.All(universals, c => Assert.Null(((ICompanionCard)c).PersonalPool));
        Assert.All(universals, c => Assert.Equal("KleeMod.Cards.Prototype.Generated",
                                                 c.GetType().Namespace));
        Assert.DoesNotContain("CompanionRoster",
            string.Join(" ", Harness.Il.Calls(Harness.Il.Method("CompanionOverhaulRoster", "Roster"))));
    }
}
