using System;
using System.Collections.Generic;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE KLEE STATUS PACKAGE (2026-10-01, ruled). Paper
/// <c>review/active/klee-status-package-2026-10-01.md</c>: "1) I think a) is
/// fine - we can keep tho the game's conventions 2) and 3) agreed on your
/// defaults". Eight pool cards in (Dazed on the fair loaders, Confiscated on
/// the busted ones, and the payoffs), eight out, and Albedo's Klee stand-in
/// is Dust of Purification. A status is Status type or Status rarity. What
/// awaits a command is pinned off the compiled methods. Sim twin:
/// <c>tier0/tests/test_klee_status_package.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KleeStatusPackageTests
{
    private static T Upgraded<T>() where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, Array.Empty<object>());
        return card;
    }

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    private static List<string> Seq(string type, string method) =>
        Il.CallSequence(Il.Method(type, method)).ToList();

    private static readonly string[] Package =
    {
        "ProtoKoForbiddenFun", "ProtoKoItWasntMe", "ProtoKoLisasTreats",
        "ProtoKoRedKnight", "ProtoKoFindersKeepers", "ProtoKoKleeCanExplain",
        "ProtoKoDamageReport", "ProtoKoSolitaryConfinement",
        // Defence in the status pile (2026-10-01, the paper's sec.5).
        "ProtoKoUpInSmoke", "ProtoKoBehindJeansDesk", "ProtoKoKitchenAlchemy",
    };

    [Fact]
    public void The_offer_is_seventy_eight_with_the_package_last_and_the_cuts_gone()
    {
        var slice = Seq("KleeOverhaulRoster", "Slice")
            .Where(c => c.StartsWith("ModelDb.Card", StringComparison.Ordinal))
            .Select(c => c.Substring(c.IndexOf('<') + 1).TrimEnd('>'))
            .ToList();
        Assert.Equal(78, slice.Count);
        Assert.Equal(Package, slice.Skip(67).ToArray());
        foreach (var gone in new[] { "PocketFireworks", "RapidFire",
                                     "FlameDance", "DodocoCover", "CarefulNow",
                                     "SplitCharge", "FishFry",
                                     "FriendshipBracelet",
                                     // Defence in the status pile.
                                     "FishFlavoredBait", "BigBounce",
                                     "SpinningSparkler" })
        {
            Assert.DoesNotContain(slice, c => c == "ProtoKo" + gone);
            Assert.Null(typeof(ProtoKoPop).Assembly.GetType(
                "KleeMod.Cards.Prototype.Generated.ProtoKo" + gone));
        }
        Assert.Null(typeof(ProtoKoPop).Assembly.GetType(
            "KleeMod.Cards.Prototype.Generated.ProtoMcAlbedoTectonicTide"));
    }

    [Fact]
    public void The_eight_rows_have_the_papers_types_costs_and_rarities()
    {
        var shapes = new (CardModel Card, CardType Type, int Cost, CardRarity Rarity)[]
        {
            (new ProtoKoForbiddenFun(), CardType.Attack, 0, CardRarity.Common),
            (new ProtoKoItWasntMe(), CardType.Skill, 0, CardRarity.Common),
            (new ProtoKoLisasTreats(), CardType.Skill, 0, CardRarity.Uncommon),
            (new ProtoKoRedKnight(), CardType.Attack, 2, CardRarity.Rare),
            (new ProtoKoFindersKeepers(), CardType.Power, 1, CardRarity.Uncommon),
            (new ProtoKoKleeCanExplain(), CardType.Skill, 1, CardRarity.Uncommon),
            (new ProtoKoDamageReport(), CardType.Power, 1, CardRarity.Rare),
            (new ProtoKoSolitaryConfinement(), CardType.Power, 1, CardRarity.Rare),
            (new ProtoMcAlbedoDustOfPurification(), CardType.Skill, 1, CardRarity.Rare),
            (new ProtoKoUpInSmoke(), CardType.Skill, 0, CardRarity.Common),
            (new ProtoKoBehindJeansDesk(), CardType.Skill, 1, CardRarity.Uncommon),
            (new ProtoKoKitchenAlchemy(), CardType.Skill, 1, CardRarity.Uncommon),
        };
        foreach (var (card, type, cost, rarity) in shapes)
        {
            Assert.Equal(type, card.Type);
            Assert.Equal(cost, card.EnergyCost.Canonical);
            Assert.Equal(rarity, card.Rarity);
        }
    }

    [Fact]
    public void The_papers_numbers_and_their_upgrades()
    {
        Assert.Equal((10m, 14m), (new ProtoKoForbiddenFun().DynamicVars.Damage.BaseValue,
                                  Upgraded<ProtoKoForbiddenFun>().DynamicVars.Damage.BaseValue));
        Assert.Equal((6m, 9m), (new ProtoKoItWasntMe().DynamicVars.Block.BaseValue,
                                Upgraded<ProtoKoItWasntMe>().DynamicVars.Block.BaseValue));
        Assert.Equal((2m, 3m), (new ProtoKoLisasTreats().DynamicVars["Energy"].BaseValue,
                                Upgraded<ProtoKoLisasTreats>().DynamicVars["Energy"].BaseValue));
        Assert.Equal((22m, 28m), (new ProtoKoRedKnight().DynamicVars.Damage.BaseValue,
                                  Upgraded<ProtoKoRedKnight>().DynamicVars.Damage.BaseValue));
        Assert.Equal((5m, 7m), (new ProtoKoFindersKeepers().DynamicVars["PowerAmount"].BaseValue,
                                Upgraded<ProtoKoFindersKeepers>().DynamicVars["PowerAmount"].BaseValue));
        Assert.Equal((6m, 8m), (new ProtoKoKleeCanExplain().DynamicVars.Block.BaseValue,
                                Upgraded<ProtoKoKleeCanExplain>().DynamicVars.Block.BaseValue));
        Assert.Equal((5m, 7m), (new ProtoKoDamageReport().DynamicVars["PowerAmount"].BaseValue,
                                Upgraded<ProtoKoDamageReport>().DynamicVars["PowerAmount"].BaseValue));
        Assert.Equal((6m, 8m), (new ProtoMcAlbedoDustOfPurification().DynamicVars["Grow"].BaseValue,
                                Upgraded<ProtoMcAlbedoDustOfPurification>().DynamicVars["Grow"].BaseValue));
        Assert.DoesNotContain(CardKeyword.Innate,
                              new ProtoKoSolitaryConfinement().Keywords);
        Assert.Contains(CardKeyword.Innate,
                        Upgraded<ProtoKoSolitaryConfinement>().Keywords);
    }

    [Fact]
    public void The_loaders_add_dazed_or_confiscated_into_the_discard_pile()
    {
        foreach (var dazed in new[] { "ProtoKoForbiddenFun", "ProtoKoItWasntMe" })
        {
            Assert.Contains(Seq(dazed, "OnPlay"), c => c.Contains("Dazed"));
            Assert.Contains("Add a [gold]Dazed[/gold] into your [gold]Discard Pile[/gold].",
                            Face((CardModel)Activator.CreateInstance(
                                typeof(ProtoKoPop).Assembly.GetType(
                                    "KleeMod.Cards.Prototype.Generated." + dazed)!)!));
        }
        foreach (var confiscated in new[] { "ProtoKoLisasTreats", "ProtoKoRedKnight" })
        {
            var play = Seq(confiscated, "OnPlay");
            Assert.Contains(play, c => c.Contains("Confiscated"));
            Assert.Contains(play, c => c.Contains("CardPileCmd.AddGeneratedCardToCombat"));
        }
    }

    [Fact]
    public void A_status_is_status_type_or_status_rarity()
    {
        Assert.True(KleeStatusPackage.IsStatus(
            new MegaCrit.Sts2.Core.Models.Cards.Dazed()));
        Assert.True(KleeStatusPackage.IsStatus(new Confiscated()));
        Assert.True(KleeStatusPackage.IsConfiscated(new Confiscated()));
        Assert.False(KleeStatusPackage.IsStatus(new ProtoKoPop()));
        Assert.False(KleeStatusPackage.IsStatus(null));
    }

    [Fact]
    public void The_payoffs_call_their_bodies()
    {
        Assert.Contains(Seq("ProtoKoKleeCanExplain", "OnPlay"),
                        c => c.Contains("KleeStatusPackage.TransformStatusesInto"));
        var transform = Seq("KleeStatusPackage", "TransformStatusesInto");
        Assert.Contains(transform, c => c.Contains("CardCmd.Transform"));
        Assert.Contains(Seq("ProtoMcAlbedoDustOfPurification", "OnPlay"),
                        c => c.Contains("KleeStatusPackage.ExhaustStatusesGrowLargest"));
        var dust = Seq("KleeStatusPackage", "ExhaustStatusesGrowLargest");
        Assert.Contains(dust, c => c.Contains("KleeStatusPackage.ExhaustStatuses"));
        Assert.Contains(Seq("KleeStatusPackage", "ExhaustStatuses"),
                        c => c.Contains("CardCmd.Exhaust"));
        Assert.Contains(dust, c => c.Contains("ProtoBombPower.GrowLargest"));
        Assert.Contains(Seq("FindersKeepersPower", "AfterCardPlayed"),
                        c => c.Contains("ProtoBombPower.PlaceOnRandom"));
        Assert.Contains(Seq("DamageReportPower", "AfterCardDrawn"),
                        c => c.Contains("ElementalHit.DealUnelemented"));
    }

    [Fact]
    public void Solitary_confinement_frees_confiscated_and_nothing_else()
    {
        var power = new SolitaryConfinementPower();
        Assert.False(power.TryModifyEnergyCostInCombat(
            new ProtoKoPop(), 1m, out var other));
        Assert.Equal(1m, other);
    }

    [Fact]
    public void Makers_of_dazed_and_confiscated_carry_their_tips()
    {
        Assert.Contains(Il.Strings(Il.Method("KleeCardTooltips", "ForCard"))
                            .Concat(Seq("KleeCardTooltips", "ForCard")),
                        c => c.Contains("Dazed"));
        Assert.Contains("Pop!", Face(new ProtoKoKleeCanExplain()));
        Assert.Contains("[gold]Confiscated[/gold]", Face(new ProtoKoSolitaryConfinement()));
    }

    // ---- defence in the status pile (2026-10-01, the paper's sec.5) ------
    //
    // [USER]: "Ok Klee - I'd say we go for option 1 and add the defensive
    // utility into her status pile, which gives some incentive for players to
    // engage with it. We can give a mix of weak, high-block cards (already
    // present) and perhaps an alchemy-flavored Strength reduction?"

    private static string Source(string type)
    {
        var repo = new System.IO.DirectoryInfo(AppContext.BaseDirectory);
        while (repo != null && !System.IO.Directory.Exists(
                   System.IO.Path.Combine(repo.FullName, "klee-mod")))
        {
            repo = repo.Parent;
        }
        Assert.NotNull(repo);
        return System.IO.File.ReadAllText(System.IO.Path.Combine(
            repo!.FullName, "klee-mod", "KleeCode", "Cards", "Prototype",
            "Generated", type + ".cs"));
    }

    private static bool Playable(CardModel card) =>
        (bool)typeof(CardModel)
            .GetProperty("IsPlayable", HeadlessGame.All)!
            .GetValue(card)!;

    private static List<CardModel> Hand(Seat seat) =>
        (List<CardModel>)typeof(CardPile)
            .GetField("_cards", HeadlessGame.All)!
            .GetValue(PileType.Hand.GetPile(seat.Player)!)!;

    [Fact]
    public void The_defence_rows_numbers_and_their_upgrades()
    {
        Assert.Equal((2m, 3m), (new ProtoKoUpInSmoke().DynamicVars["PowerAmount"].BaseValue,
                                Upgraded<ProtoKoUpInSmoke>().DynamicVars["PowerAmount"].BaseValue));
        Assert.Equal((11m, 14m), (new ProtoKoBehindJeansDesk().DynamicVars.Block.BaseValue,
                                  Upgraded<ProtoKoBehindJeansDesk>().DynamicVars.Block.BaseValue));
        Assert.Equal((1m, 1m), (new ProtoKoKitchenAlchemy().DynamicVars["StrengthLoss"].BaseValue,
                                Upgraded<ProtoKoKitchenAlchemy>().DynamicVars["StrengthLoss"].BaseValue));
        Assert.Contains(CardKeyword.Exhaust, new ProtoKoKitchenAlchemy().Keywords);
        Assert.DoesNotContain(CardKeyword.Retain, new ProtoKoKitchenAlchemy().Keywords);
        Assert.Contains(CardKeyword.Retain, Upgraded<ProtoKoKitchenAlchemy>().Keywords);
        Assert.Equal(TargetType.AllEnemies, new ProtoKoUpInSmoke().TargetType);
        Assert.Equal(TargetType.AllEnemies, new ProtoKoKitchenAlchemy().TargetType);
        Assert.Equal("Apply {PowerAmount:diff()} [gold]Weak[/gold] to ALL enemies. "
                     + "Add a [gold]Dazed[/gold] into your [gold]Discard Pile[/gold].",
                     Face(new ProtoKoUpInSmoke()));
        Assert.Equal("Gain {Block:diff()} [gold]Block[/gold]. "
                     + "Add a [gold]Confiscated[/gold] into your [gold]Discard Pile[/gold].",
                     Face(new ProtoKoBehindJeansDesk()));
        Assert.Equal("ALL enemies lose 1 [gold]Strength[/gold]. "
                     + "Exhaust every status in your hand; they lose 1 more for each.",
                     Face(new ProtoKoKitchenAlchemy()));
    }

    [Fact]
    public void Up_in_smoke_weakens_all_and_discards_a_dazed()
    {
        var play = Seq("ProtoKoUpInSmoke", "OnPlay");
        Assert.Contains(play, c => c.Contains("PowerCmd.Apply<WeakPower>"));
        Assert.Contains(play, c => c.Contains("Dazed"));
        Assert.Contains(play, c => c.Contains("CardPileCmd.AddGeneratedCardToCombat"));
        Assert.DoesNotContain(play, c => c.Contains("Confiscated"));
        var source = Source("ProtoKoUpInSmoke");
        Assert.Contains("CombatState!.HittableEnemies", source);
        Assert.Contains("PileType.Discard, Owner);", source);
    }

    [Fact]
    public void Behind_jeans_desk_blocks_and_adds_a_confiscated()
    {
        var play = Seq("ProtoKoBehindJeansDesk", "OnPlay");
        Assert.Contains(play, c => c.Contains("CreatureCmd.GainBlock"));
        Assert.Contains(play, c => c.Contains("Confiscated"));
        Assert.Contains(play, c => c.Contains("CardPileCmd.AddGeneratedCardToCombat"));
        Assert.DoesNotContain(play, c => c.Contains("Dazed"));
        Assert.Contains("PileType.Discard, Owner);", Source("ProtoKoBehindJeansDesk"));
    }

    // Kitchen Alchemy, reworked 2026-10-02 after the forced-deck seat (0 plays
    // in 7 hands: a status is rarely in hand): "ALL enemies lose 1
    // Strength. Exhaust every status in your hand; they lose 1 more for each."
    // Upgrade: Retain (tuned 2026-10-02 after three forced-deck seats; it was
    // +1 loss, and upgraded it took 3 to 5 permanent Strength off one enemy).

    [Fact]
    public void Kitchen_alchemy_exhausts_every_status_then_takes_one_total_from_all()
    {
        // STRUCTURAL: the play needs a live combat. Every status exhausted
        // first, then Malaise's own call -- StrengthPower at MINUS one total
        // (the base plus 1 per status), a permanent loss -- on every
        // hittable enemy.
        var play = Seq("ProtoKoKitchenAlchemy", "OnPlay");
        var exhaust = play.FindIndex(c => c.Contains("KleeStatusPackage.ExhaustStatuses"));
        var total = play.FindIndex(c => c.Contains("KleeStatusPackage.LossWithStatuses"));
        var loss = play.FindIndex(c => c.Contains("PowerCmd.Apply<StrengthPower>"));
        Assert.True(exhaust >= 0 && total > exhaust && loss > total);
        Assert.DoesNotContain(play, c => c.Contains("TemporaryStrength"));
        Assert.DoesNotContain(play, c => c.Contains("CardSelectCmd"));
        var source = Source("ProtoKoKitchenAlchemy");
        Assert.Contains("LossWithStatuses(DynamicVars[\"StrengthLoss\"].IntValue, 1, exhausted)", source);
        Assert.Contains("foreach (var weakened in CombatState!.HittableEnemies.ToList())", source);
        Assert.Contains("weakened, -loss,", source);

        var body = Seq("KleeStatusPackage", "ExhaustStatuses");
        Assert.Contains(body, c => c.Contains("CardCmd.Exhaust"));
    }

    [Fact]
    public void Kitchen_alchemy_loss_is_the_base_plus_one_per_status()
    {
        var printed = new ProtoKoKitchenAlchemy().DynamicVars["StrengthLoss"].IntValue;
        var upgraded = Upgraded<ProtoKoKitchenAlchemy>().DynamicVars["StrengthLoss"].IntValue;
        Assert.Equal(1, KleeStatusPackage.LossWithStatuses(printed, 1, 0));   // no status
        Assert.Equal(3, KleeStatusPackage.LossWithStatuses(printed, 1, 2));   // two statuses
        Assert.Equal(1, KleeStatusPackage.LossWithStatuses(upgraded, 1, 0));  // upgrade is Retain
        Assert.Equal(3, KleeStatusPackage.LossWithStatuses(upgraded, 1, 2));
    }

    [Fact]
    public void Kitchen_alchemy_is_always_playable_and_counts_statuses_not_curses()
    {
        var seat = Seat.Klee().WithCombatState();
        var card = new ProtoKoKitchenAlchemy();
        Seat.Set(card, "IsMutable", true);
        Seat.Force(card, "Owner", seat.Player);
        var hand = Hand(seat);

        Assert.False(card is IUnplayableReasonCard);
        Assert.Equal(0, KleeStatusPackage.StatusesInHand(seat.Creature));
        Assert.True(Playable(card));

        hand.Add(new ProtoKoPop());                     // not a status
        hand.Add(new MegaCrit.Sts2.Core.Models.Cards.Regret());   // a curse
        Assert.Equal(0, KleeStatusPackage.StatusesInHand(seat.Creature));

        hand.Add(new MegaCrit.Sts2.Core.Models.Cards.Dazed());
        hand.Add(new Confiscated());                    // Status rarity counts
        Assert.Equal(2, KleeStatusPackage.StatusesInHand(seat.Creature));
        Assert.True(Playable(card));

        // None of the three defence rows carries a gate.
        Assert.False(new ProtoKoUpInSmoke() is IUnplayableReasonCard);
        Assert.False(new ProtoKoBehindJeansDesk() is IUnplayableReasonCard);
    }
}
