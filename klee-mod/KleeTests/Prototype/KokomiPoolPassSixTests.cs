using System;
using System.Linq;
using System.Reflection;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// KOKOMI POOL PASS SIX -- the Plan-less hand (`EB-703`, 2026-09-08,
/// review/active/kokomi-plan-less-hand-2026-09-08.md).
///
/// THE FINDING, repeated by rounds 26 to 30 without a row of its own: a hand
/// with no Plan card in it has no decision in it. The starter held two Plan
/// cards in ten, so roughly one opening hand in five posed the kit nothing --
/// round 30 lane 1 counted three of its eleven opening turns, including the
/// first turn of the run, and round 27 lane 2 opened fight 1 on "three Strikes
/// and two Defends, the unmodified basic deck" while the jellyfish panel
/// printed "No Plan card in hand: the jellyfish waits."
///
/// WHAT CHANGES: Kokomi's basic Strike becomes HER card. "Deal 6 damage. Plan:
/// Deal 8 damage", upgrading 9 and 11 -- Ambush's shape at a basic's premium,
/// two more damage for a turn's delay. Every hand now holds the kit's
/// question. Defend stays the base game's: Block a turn late is the dead half
/// every seat rejected, and one card in the hand that cannot be written keeps
/// the question a question.
///
/// WHAT IS REAL HERE AND WHAT IS STRUCTURAL, on
/// <see cref="KokomiPoolPassFiveTests"/>' split. The card shape is REAL -- the
/// row is constructed and its face, cost, type, rarity, tag, element, plan
/// clause and smith's move are read off the shipped class. The WIRING is not:
/// a starting deck needs a live run, so the four seams are pinned off the
/// compiled methods. The end-to-end arithmetic is the sim twin's:
/// <c>tier0/tests/test_kokomi_plan.py</c> and
/// <c>tier0/tests/test_kokomi_overhaul.py</c>.
///
/// THE NUMBERS ARE PROTOTYPE NUMBERS (D by the ladder). Nothing here is
/// quotable (R215 B).
///
/// THE COLLECTION IS LOAD-BEARING, <see cref="BaseBasicsTests"/>' reason: the
/// element case flips `KokomiOverhaul.Enabled`, which is one static for the
/// whole process.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiPoolPassSixTests
{
    private const BindingFlags All = HeadlessGame.All;

    // ======================================================================
    // 1. THE CARD -- a basic that asks the kit's question
    // ======================================================================

    [Fact]
    public void The_strike_prints_a_now_line_and_a_plan_line()
    {
        var card = new ProtoKkStrike();

        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.Equal(CardType.Attack, card.Type);
        Assert.Equal(CardRarity.Basic, card.Rarity);
        Assert.Equal(6m, card.DynamicVars.Damage.BaseValue);
        Assert.Equal(
            "Deal {Damage:diff()} damage. [gold]Plan[/gold]: Deal "
            + "{PlanDamage:diff()} damage.",
            Face(card));

        // THE WRITTEN HALF IS AMBUSH'S SHAPE AT A BASIC'S PREMIUM: two more
        // damage for a turn's delay, aimed the way every damage Plan is --
        // at whatever body is in front when the jellyfish carries it out,
        // never at the one that was there when it was written.
        Assert.Single(card.PlanClauses);
        Assert.Equal(KokomiPlan.Kind.Damage, card.PlanClauses[0].Kind);
        Assert.Equal(8, card.PlanClauses[0].Amount);
        Assert.Equal(KokomiPlan.Aim.FrontEnemy, card.PlanClauses[0].Aim);
    }

    [Fact]
    public void The_smith_moves_both_halves_by_the_base_strikes_three()
    {
        var card = new ProtoKkStrike();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", All)!
            .Invoke(card, Array.Empty<object?>());

        Assert.Equal(9m, card.DynamicVars.Damage.BaseValue);
        Assert.Equal(11m, card.PlanClauses[0].Amount);
    }

    [Fact]
    public void The_face_up_hit_applies_nothing_and_the_written_one_is_hydro()
    {
        // A BASIC IS SUPPOSED TO BE BAD ([USER] 2026-09-02, LAW's cadence
        // line), and the exemption reaches HER OWN basic: four Hydro appliers
        // in the opening deck is a power change the design note did not ask
        // for. WRITING the Strike is what earns the aura, and that is a reason
        // to write it -- a carry-out is the jellyfish's hit, which
        // `KokomiPlan.ResolveAll` deals as `Element.Hydro` whatever the card.
        //
        // DECLARED, NOT OMITTED, and the distinction is
        // `CatalystCadence.PrintedElement`'s own: a card that says NOTHING is
        // asked of the CHARACTER, so the row carries `IElementalCard`
        // returning `Element.None` -- Kirara's shape, which that header names.
        var klee = KleeOverhaul.Enabled;
        var kokomi = KokomiOverhaul.Enabled;
        try
        {
            KleeOverhaul.Enabled = true;
            KokomiOverhaul.Enabled = true;

            Assert.Equal(Element.None, new ProtoKkStrike().Element);
            Assert.Equal(Element.None, CatalystCadence.PrintedElement(
                new ProtoKkStrike(), Seat.Kokomi().Creature));
            // The cadence itself is untouched: her other Attacks still apply.
            Assert.Equal(Element.Hydro, CatalystCadence.PrintedElement(
                new ProtoKkRiptide(), Seat.Kokomi().Creature));
        }
        finally
        {
            KleeOverhaul.Enabled = klee;
            KokomiOverhaul.Enabled = kokomi;
        }

        // THE CARRY-OUT IS STILL A HYDRO HIT, read off the resolver rather
        // than off a live drain: every damaging Plan clause goes through
        // `ElementalHit.Deal(..., Element.Hydro, ...)`. The sim's twin runs
        // the arithmetic end to end
        // (`test_her_strike_is_six_face_up_and_eight_written`).
        Assert.Contains("Element.Hydro", Source("KokomiPlan", power: true));

        // AND THE FACE SAYS SO. The keyword still declares Hydro -- the gem
        // and the reaction rule -- and `ForPlanElement` is the sentence that
        // says WHEN: "Its own hit applies no aura; the Bake-Kurage carries out
        // the Plan as a Hydro hit, which does." What is GONE is the face-up
        // Hydro rider (`KleeCardTooltips.ForCard(..., Element.Hydro, ...)`),
        // which would have promised a reaction the play cannot make.
        Assert.Contains(KleeKeywords.AppliesHydro,
                        new ProtoKkStrike().CanonicalKeywords);
        var generated = Source("ProtoKkStrike");
        Assert.Contains("ArmKeywordTips.ForPlanElement", generated);
        Assert.DoesNotContain("KleeCardTooltips.ForCard", generated);
    }

    // ======================================================================
    // 2. THE TAG -- "one of your Strikes" still has exactly one answer
    // ======================================================================

    [Fact]
    public void Her_strike_wears_the_strike_tag_and_her_other_basics_do_not()
    {
        // `EB-543` REACHED THE OTHER WAY. That row removed the tag from every
        // prototype basic, because the arm dealt base Strikes and a kit card
        // wearing the tag was a SECOND answer to a question with one right
        // one. Her Strike is now her own card, so the tag has to travel with
        // it -- otherwise Neow's Talisman's "Upgrade 1 of your Strikes",
        // Strike Dummy and Miniature Cannon find NOTHING in her deck, which
        // is the same relic half broken from the other end.
        Assert.Contains(CardTag.Strike, new ProtoKkStrike().Tags);
        Assert.DoesNotContain(CardTag.Defend, new ProtoKkStrike().Tags);

        // EXCLUSIVITY, which is what `EB-543` was actually about: the other
        // two basics she opens with wear neither tag, so the scan has one hit
        // per copy of one card.
        foreach (var other in new CardModel[]
                 { new ProtoKkSlackWater(), new ProtoKkKuragesOath() })
        {
            Assert.Equal(CardRarity.Basic, other.Rarity);
            Assert.DoesNotContain(CardTag.Strike, other.Tags);
            Assert.DoesNotContain(CardTag.Defend, other.Tags);
        }
    }

    [Fact]
    public void The_tag_is_declared_on_the_sheet_and_not_re_derived()
    {
        // DERIVATION IS WHAT OVER-TAGGED SLACK WATER (`EB-409`, `EB-543`):
        // "basic attack that deals damage" describes three of her rows. The
        // sheet names the ONE row that IS the Strike (`basic_tag: strike`)
        // and the codegen emits the tag from that alone.
        var generated = Source("ProtoKkStrike");
        Assert.Contains(
            "protected override HashSet<CardTag> CanonicalTags => "
            + "new() { CardTag.Strike };",
            generated);
        Assert.DoesNotContain("CanonicalTags", Source("ProtoKkSlackWater"));
    }

    // ======================================================================
    // 3. THE WIRING -- both starter seams, and the offer screen it stays off
    // ======================================================================

    [Fact]
    public void The_starter_deals_four_of_hers_and_no_shipped_strike()
    {
        var deck = Cards("KokomiOverhaulRoster", "StartingDeck");

        Assert.Equal(10, deck.Count);
        Assert.Equal(4, deck.Count(c => c == "ModelDb.Card<ProtoKkStrike>"));
        Assert.DoesNotContain(deck, c => c.Contains("StrikeSilent"));
        Assert.DoesNotContain(deck, c => c.Contains("StrikeIronclad"));
        // The Defend half is untouched, and that is the design and not an
        // omission.
        Assert.Equal(4, deck.Count(c => c == "ModelDb.Card<DefendSilent>"));
    }

    [Fact]
    public void The_fourth_seam_hands_out_the_same_card_the_deck_deals()
    {
        // `EB-351`'s seam, which is exactly why it exists: Large Capsule's
        // "an additional Strike and Defend" asks the CHARACTER, and until
        // this pass both arms answered with a base card. Answering with
        // `StrikeSilent` now would drop a shipped basic into a deck whose
        // Strikes all print a Plan line -- `EB-351`'s original defect, one
        // arm over.
        Assert.Equal(new[] { "ModelDb.Card<ProtoKkStrike>" },
                     Cards("KokomiOverhaulRoster", "StarterStrike"));
        Assert.Equal(new[] { "ModelDb.Card<DefendSilent>" },
                     Cards("KokomiOverhaulRoster", "StarterDefend"));
    }

    [Fact]
    public void The_basic_is_in_the_pool_for_lookup_and_out_of_every_offer()
    {
        // BOTH HALVES ARE LOAD-BEARING, and they are the quarantine's own
        // (`PrototypeRoster`'s header): IN `AllCards`, because a poolless
        // card throws "You monster!" the moment it is drawn and this one is
        // drawn every turn; OUT of `Slice()`, which IS `FilterThroughEpochs`
        // and therefore every reward roll, shop shelf and card transform.
        // `tools/lint_arm_pool_parity.py` is the gate on the second half --
        // `basic` is the starter's mark and the only exemption it allows.
        var roster = Il.CallSequence(
            Il.Method("PrototypeRoster", "BuildKokomi"))
            .Aggregate(string.Empty, (a, c) => a + c);
        Assert.Contains("ProtoKkStrike", roster);

        var slice = Il.CallSequence(Il.Method("KokomiOverhaulRoster", "Slice"))
            .Aggregate(string.Empty, (a, c) => a + c);
        Assert.DoesNotContain("ProtoKkStrike", slice);
    }

    // ======================================================================
    // helpers -- KokomiPoolPassFiveTests' own, for its reasons
    // ======================================================================

    private static System.Collections.Generic.IReadOnlyList<string> Cards(
        string type, string method) =>
        Il.CallSequence(Il.Method(type, method))
            .Where(c => c.StartsWith("ModelDb.Card")).ToList();

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    /// <summary>One class's own source, read off disk. A SOURCE READ and not
    /// an IL one, and only for the facts IL cannot carry: a `CanonicalTags`
    /// override is a property initialiser whose absence leaves no call at
    /// all, and a literal enum argument leaves no call either.</summary>
    private static string Source(string type, bool power = false)
    {
        var root = System.AppContext.BaseDirectory;
        var repo = new System.IO.DirectoryInfo(root);
        while (repo != null && !System.IO.Directory.Exists(
                   System.IO.Path.Combine(repo.FullName, "klee-mod")))
        {
            repo = repo.Parent;
        }
        Assert.NotNull(repo);
        var dir = power
            ? System.IO.Path.Combine(repo!.FullName, "klee-mod", "KleeCode",
                                     "Powers", "Prototype")
            : System.IO.Path.Combine(repo!.FullName, "klee-mod", "KleeCode",
                                     "Cards", "Prototype", "Generated");
        return System.IO.File.ReadAllText(
            System.IO.Path.Combine(dir, type + ".cs"));
    }
}
